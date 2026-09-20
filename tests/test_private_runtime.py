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
        self.store.close('event-2',b'x')
        self.store.correct('event-2','source correction')
        self.store.correct('event-2','source correction')
        with self.store.connect() as c:
            self.assertEqual(c.execute('select count(*) from corrections').fetchone()[0],1)
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

    def post_empty(self,path,token=None):
        request=Request(self.url+path,data=b'',
                        headers={'Authorization':f'Bearer {token or self.token}'},
                        method='POST')
        with urlopen(request) as response: return json.load(response)

    def test_digest_close_contract_idempotence_and_altered_refusal(self):
        packet={'event_id':'digest-source','fact':'same'}
        digest=hashlib.sha256(canonical(packet)).hexdigest()
        query='?event_id=digest-source&packet_sha256='+digest
        first=self.post_empty('/events/close'+query)
        second=self.post_empty('/events/close'+query)
        self.assertEqual(first,second)
        self.assertTrue(first['result_ref'])
        changed=hashlib.sha256(canonical({'event_id':'digest-source','fact':'changed'})).hexdigest()
        with self.assertRaises(HTTPError) as error:
            self.post_empty('/events/close?event_id=digest-source&packet_sha256='+changed)
        self.assertEqual(error.exception.code,409)
        for bad_query in (
            '?event_id=digest-source',
            '?packet_sha256='+digest,
            '?event_id=digest-source&packet_sha256=bad',
        ):
            with self.assertRaises(HTTPError):
                self.post_empty('/events/close'+bad_query)

    def test_digest_close_url_encodes_event_identity(self):
        client=Client(self.url,token=self.token,snapshot='snapshot')
        packet={'event_id':'preseason:1 / home','fact':'same'}
        first=client.close_event(packet)
        second=client.close_event(packet)
        self.assertEqual(first,second)
        self.assertTrue(first)

    def test_legacy_body_contract_remains_compatible(self):
        packet={'event_id':'legacy-source','fact':'same'}
        flat=self.post('/events/close',packet)
        wrapped=self.post('/events/close',{'packet':packet})
        wrapped_string=self.post('/events/close',{'event_id':'legacy-source',
                                                  'packet':json.dumps(packet)})
        self.assertEqual(flat,wrapped)
        self.assertEqual(flat,wrapped_string)
        with self.assertRaises(HTTPError) as error:
            self.post('/events/close',{'event_id':'other','packet':packet})
        self.assertEqual(error.exception.code,409)

    def test_client_validates_packet_and_sends_digest_query_without_body(self):
        client=Client(self.url,token=self.token,snapshot='snapshot')
        with self.assertRaises(ValueError): client.close_event([])
        with self.assertRaises(ValueError): client.close_event({})
        calls=[]
        client._request=lambda path,body=None,method=None: calls.append((path,body,method)) or {'result_ref':'opaque'}
        packet={'event_id':'one','fact':'same'}
        expected=hashlib.sha256(canonical(packet)).hexdigest()
        self.assertEqual(client.close_event(packet),'opaque')
        self.assertEqual(len(calls),1)
        path,body,method=calls[0]
        self.assertEqual(body,None)
        self.assertEqual(method,'POST')
        self.assertIn('/events/close?',path)
        self.assertIn('event_id=one',path)
        self.assertIn('packet_sha256='+expected,path)
        self.assertEqual(list(inspect.signature(Client.close_event).parameters),['self','packet'])

    def test_readiness_fails_when_real_close_transport_is_broken(self):
        client=Client(self.url,token=self.token,snapshot='snapshot')
        real=client._request
        def request(path,body=None,method=None):
            if path.startswith('/events/close?'):
                raise PrivateRuntimeUnavailable('broken closure')
            return real(path,body,method)
        client._request=request
        with self.assertRaises(PrivateRuntimeUnavailable): client.readiness()

    def test_audited_snapshot_recovery_restores_checked_in_binding(self):
        client=Client(self.url,token=self.token,snapshot='next')
        self.assertEqual(client.advance_snapshot('snapshot','next','uncommitted-branch'),'next')
        self.assertEqual(self.store.current_snapshot(),'next')
        self.assertEqual(
            self.store.recover_snapshot('snapshot','uncommitted public transaction failed'),
            'snapshot')
        self.store.initialize('snapshot')
        with self.store.connect() as connection:
            rows=connection.execute(
                'select from_snapshot,to_snapshot,reason from snapshot_recoveries'
            ).fetchall()
        self.assertEqual(
            rows,
            [('next','snapshot','uncommitted public transaction failed')])
        restarted=Store(Path(self.tmp.name)/'state.sqlite3')
        restarted.initialize('snapshot')
        self.assertEqual(restarted.current_snapshot(),'snapshot')

    def test_snapshot_recovery_requires_explicit_reason(self):
        with self.assertRaises(ValueError):
            self.store.recover_snapshot('other','')

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

    def test_bodyless_administrative_probe_is_idempotent(self):
        first=self.post_empty('/admin/probe')
        second=self.post_empty('/admin/probe')
        self.assertTrue(first['idempotent'])
        self.assertTrue(first['journal_fingerprint'])
        self.assertEqual(first,second)

    def test_snapshot_and_correction_clients_send_bodyless_queries(self):
        client=Client(self.url,token=self.token,snapshot='snapshot')
        calls=[]
        client._request=lambda path,body=None,method=None: (
            calls.append((path,body,method)) or
            ({'snapshot':'next value'} if path.startswith('/admin/snapshot/advance?')
             else {'recorded':True})
        )
        self.assertEqual(
            client.advance_snapshot('old value','next value','checkpoint: one / two'),
            'next value')
        self.assertTrue(client.record_correction('event: 1 / home','reason with spaces & punctuation'))
        self.assertEqual(len(calls),2)
        for path,body,method in calls:
            self.assertIsNone(body)
            self.assertEqual(method,'POST')
            self.assertIn('?',path)
        self.assertIn('previous_snapshot=old+value',calls[0][0])
        self.assertIn('next_snapshot=next+value',calls[0][0])
        self.assertIn('checkpoint=checkpoint%3A+one+%2F+two',calls[0][0])
        self.assertIn('event_id=event%3A+1+%2F+home',calls[1][0])
        self.assertIn('reason=reason+with+spaces+%26+punctuation',calls[1][0])

    def test_bodyless_correction_records_known_event(self):
        self.store.close('correction-target',b'original')
        client=Client(self.url,token=self.token,snapshot='snapshot')
        self.assertTrue(client.record_correction('correction-target','bounded source correction'))
        with self.store.connect() as connection:
            row=connection.execute(
                'select event_id,reason from corrections order by id desc limit 1'
            ).fetchone()
        self.assertEqual(row,('correction-target','bounded source correction'))

    def test_legacy_snapshot_and_correction_bodies_remain_compatible(self):
        self.store.close('legacy-correction',b'original')
        correction=self.post('/corrections',{
            'event_id':'legacy-correction','reason':'legacy reason'})
        self.assertTrue(correction['recorded'])
        advanced=self.post('/admin/snapshot/advance',{
            'previous_snapshot':'snapshot',
            'next_snapshot':'legacy-next',
            'checkpoint':'legacy checkpoint'})
        self.assertEqual(advanced['snapshot'],'legacy-next')
        self.assertEqual(self.store.current_snapshot(),'legacy-next')

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
        if (root/'.git').exists():
            names=subprocess.check_output(['git','ls-files'],cwd=root,text=True).splitlines()
        else:
            names=[path.relative_to(root).as_posix() for path in root.rglob('*')
                   if path.is_file() and '__pycache__' not in path.parts]
        for name in names:
            data=(root/name).read_bytes()
            self.assertNotIn(b'PRIVATE_' + b'JOURNAL_CONTENT',data)
            self.assertNotIn(name, {'engine.sqlite3','engine.backup.sqlite3','engine-token'})
        self.assertFalse((root/'engine.sqlite3').exists())

if __name__=='__main__': unittest.main()
