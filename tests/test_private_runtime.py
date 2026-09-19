import hashlib, inspect, json, tempfile, threading, unittest
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
from runtime import KERNEL_VERSION
from runtime.packets import canonical
from runtime.private_service import Store, handler
from runtime.private_client import (Client, PrivateRuntimeUnavailable,
                                    _readiness_close_packet)

class PrivateRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.token='synthetic-auth-token'; self.token_file=Path(self.tmp.name)/'token'; self.token_file.write_text(self.token)
        self.store=Store(Path(self.tmp.name)/'state.sqlite3'); self.store.initialize('snapshot')
        self.server=ThreadingHTTPServer(('127.0.0.1',0),handler(self.store,self.token,'snapshot'))
        threading.Thread(target=self.server.serve_forever,daemon=True).start()
        self.addCleanup(self.server.server_close); self.addCleanup(self.server.shutdown)
        self.url=f'http://127.0.0.1:{self.server.server_port}'
    def test_unauthorized_read_denied(self):
        with self.assertRaises(HTTPError) as e: urlopen(self.url+'/ready')
        self.assertEqual(e.exception.code,401)
    def test_restart_persistence_idempotence_and_altered_refusal(self):
        c=Client(self.url,token_file=self.token_file,snapshot='snapshot'); self.assertTrue(c.readiness()['ready'])
        packet={'event_id':'event-1','fact':'original'}
        first=c.close_event(packet); self.assertEqual(first,c.close_event(packet))
        restarted=Store(Path(self.tmp.name)/'state.sqlite3'); self.assertTrue(restarted.ready())
        with self.assertRaisesRegex(PrivateRuntimeUnavailable,'altered packet refused'):
            c.close_event({'event_id':'event-1','fact':'changed'})
        self.assertEqual(restarted.close('event-1',b'{"event_id":"event-1","fact":"original"}'),first)
    def test_seed_once_and_correction_is_explicit(self):
        with self.store.connect() as c: before=c.execute("select value from meta where key='seed'").fetchone()[0]
        self.store.initialize('snapshot')
        with self.store.connect() as c: after=c.execute("select value from meta where key='seed'").fetchone()[0]
        self.assertEqual(before,after)
        self.store.close('event-2',b'x'); self.store.correct('event-2','source correction')
        with self.store.connect() as c: self.assertEqual(c.execute('select count(*) from corrections').fetchone()[0],1)
    def test_missing_credentials_fails_closed(self):
        with self.assertRaises(PrivateRuntimeUnavailable): Client(self.url,token_file=Path(self.tmp.name)/'missing',snapshot='snapshot').readiness()

    def test_wrong_snapshot_fails_closed(self):
        with self.assertRaises(PrivateRuntimeUnavailable):
            Client(self.url,token=self.token,snapshot='wrong').readiness()

    def test_administrative_probe_is_idempotent(self):
        client=Client(self.url,token=self.token,snapshot='snapshot')
        first=client.readiness(); second=client.readiness()
        self.assertTrue(first['administrative_probe_idempotent'])
        self.assertEqual(first,second)
        self.assertTrue(first['event_closure_probe_idempotent'])

    def test_readiness_close_canary_avoids_legacy_frozen_identity(self):
        legacy_id="__readiness_close_probe__:"+hashlib.sha256(
            ("snapshot:"+KERNEL_VERSION).encode()).hexdigest()
        legacy_packet={"administrative":True,"event_id":legacy_id,
                       "kernel":KERNEL_VERSION,"snapshot":"snapshot",
                       "type":"legacy-readiness-close-probe"}
        self.store.close(legacy_id,canonical(legacy_packet))
        current_packet=_readiness_close_packet('snapshot',KERNEL_VERSION)
        self.assertNotEqual(current_packet['event_id'],legacy_id)
        client=Client(self.url,token=self.token,snapshot='snapshot')
        self.assertTrue(client.readiness()['event_closure_probe_idempotent'])

    def post(self,path,body,token=None):
        request=Request(self.url+path,data=json.dumps(body).encode(),
                        headers={'Authorization':f'Bearer {token or self.token}',
                                 'Content-Type':'application/json'})
        with urlopen(request) as response: return json.load(response)

    def post_probe(self, body, token=None):
        return self.post('/admin/probe',body,token)

    def test_single_source_event_id_contract_and_legacy_match(self):
        packet={'event_id':'single-source','fact':'same'}
        self.assertEqual(self.post('/events/close',{'packet':packet}),
                         self.post('/events/close',{'event_id':'single-source','packet':packet}))
        with self.assertRaises(HTTPError) as error:
            self.post('/events/close',{'event_id':'other','packet':packet})
        self.assertEqual(error.exception.code,409)
        for bad in ({'packet':[]},{'packet':{}},{'packet':{'event_id':'  '}}):
            with self.assertRaises(HTTPError): self.post('/events/close',bad)

    def test_client_validates_packet_before_network_io_and_sends_no_outer_id(self):
        client=Client(self.url,token=self.token,snapshot='snapshot')
        with self.assertRaises(ValueError): client.close_event([])
        with self.assertRaises(ValueError): client.close_event({})
        calls=[]
        client._request=lambda path,body: calls.append((path,body)) or {'result_ref':'opaque'}
        self.assertEqual(client.close_event({'event_id':'one'}),'opaque')
        self.assertEqual(calls,[('/events/close',{'packet':{'event_id':'one'}})])
        self.assertEqual(list(inspect.signature(Client.close_event).parameters),['self','packet'])

    def test_readiness_fails_when_real_close_transport_is_broken(self):
        client=Client(self.url,token=self.token,snapshot='snapshot')
        real=client._request
        def request(path,body=None):
            if path=='/events/close': raise PrivateRuntimeUnavailable('broken closure')
            return real(path,body)
        client._request=request
        with self.assertRaises(PrivateRuntimeUnavailable): client.readiness()

    def test_snapshot_advance_cas_idempotence_conflict_and_restart(self):
        client=Client(self.url,token=self.token,snapshot='next')
        self.assertEqual(client.current_snapshot(),'snapshot')
        self.assertEqual(client.advance_snapshot('snapshot','next','checkpoint-1'),'next')
        self.assertEqual(client.advance_snapshot('snapshot','next','checkpoint-1'),'next')
        with self.assertRaises(PrivateRuntimeUnavailable):
            client.advance_snapshot('snapshot','different','checkpoint-2')
        with self.assertRaises(PrivateRuntimeUnavailable):
            client.advance_snapshot('stale','later','checkpoint-3')
        restarted=Store(Path(self.tmp.name)/'state.sqlite3')
        self.assertEqual(restarted.current_snapshot(),'next')
        with restarted.connect() as connection:
            history=connection.execute('select previous_snapshot,next_snapshot,checkpoint from snapshot_history').fetchall()
        self.assertEqual(history,[('snapshot','next','checkpoint-1')])
        self.assertTrue(client.readiness()['ready'])

    def test_two_administrative_probes_are_identical(self):
        first=self.post_probe({})
        second=self.post_probe({})
        self.assertTrue(first['idempotent'])
        self.assertTrue(first['journal_fingerprint'])
        self.assertEqual(first,second)

    def test_administrative_probe_persists_across_store_restart(self):
        first=self.store.probe()
        restarted=Store(Path(self.tmp.name)/'state.sqlite3')
        self.assertEqual(first,restarted.probe())

    def test_unauthorized_administrative_probe_is_rejected(self):
        with self.assertRaises(HTTPError) as error:
            self.post_probe({},token='wrong-token')
        self.assertEqual(error.exception.code,401)

    def test_caller_cannot_select_administrative_probe_identity(self):
        first=self.post_probe({'probe_id':'a'*64})
        second=self.post_probe({'probe_id':'b'*64})
        self.assertEqual(first,second)
        with self.store.connect() as connection:
            identities=connection.execute('select probe_id from admin_probes').fetchall()
        self.assertEqual(len(identities),1)

    def test_bad_auth_snapshot_and_kernel_fail_readiness_closed(self):
        with self.assertRaises(PrivateRuntimeUnavailable):
            Client(self.url,token='wrong-token',snapshot='snapshot').readiness()
        with self.assertRaises(PrivateRuntimeUnavailable):
            Client(self.url,token=self.token,snapshot='wrong').readiness()
        with self.store.connect() as connection:
            connection.execute("update meta set value=? where key='kernel'",(b'wrong-kernel',))
        with self.assertRaises(PrivateRuntimeUnavailable):
            Client(self.url,token=self.token,snapshot='snapshot').readiness()

    def test_no_seed_or_private_journal_in_repository(self):
        root=Path(__file__).resolve().parents[1]
        import subprocess
        for name in subprocess.check_output(['git','ls-files'],cwd=root,text=True).splitlines():
            data=(root/name).read_bytes()
            self.assertNotIn(b'PRIVATE_' + b'JOURNAL_CONTENT',data)
            self.assertNotIn(name, {'engine.sqlite3','engine.backup.sqlite3','engine-token'})
        self.assertFalse((root/'engine.sqlite3').exists())

if __name__=='__main__': unittest.main()
