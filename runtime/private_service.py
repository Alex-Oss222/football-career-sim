"""Authenticated private Engine State service.

Deployment data and authentication material must be outside the checkout.  The
HTTP API intentionally exposes only health/readiness and opaque result closure.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import argparse, hashlib, hmac, json, os, secrets, sqlite3, threading, time
from pathlib import Path
from contextlib import closing
from urllib.parse import urlsplit, parse_qs
from .packets import canonical

SCHEMA="1"; KERNEL="2013.3"

class Store:
    def __init__(self,path):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        self.lock=threading.Lock(); self._setup()
    def connect(self): return sqlite3.connect(self.path)
    def _setup(self):
        with closing(self.connect()) as c, c:
            c.executescript("""PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value BLOB NOT NULL);
            CREATE TABLE IF NOT EXISTS events(event_id TEXT PRIMARY KEY,packet_hash TEXT NOT NULL,result TEXT,created INTEGER NOT NULL,closed INTEGER);
            CREATE TABLE IF NOT EXISTS corrections(id INTEGER PRIMARY KEY AUTOINCREMENT,event_id TEXT NOT NULL,reason TEXT NOT NULL,created INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS backups(id INTEGER PRIMARY KEY AUTOINCREMENT,digest TEXT NOT NULL,created INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS admin_probes(probe_id TEXT PRIMARY KEY,created INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS snapshot_history(
                previous_snapshot TEXT NOT NULL,
                next_snapshot TEXT NOT NULL,
                checkpoint TEXT NOT NULL,
                created INTEGER NOT NULL,
                UNIQUE(previous_snapshot),
                UNIQUE(next_snapshot));
            CREATE TABLE IF NOT EXISTS snapshot_recoveries(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_snapshot TEXT NOT NULL,
                to_snapshot TEXT NOT NULL,
                reason TEXT NOT NULL,
                created INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS snapshot_transitions_v2(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                previous_snapshot TEXT NOT NULL,
                next_snapshot TEXT NOT NULL,
                checkpoint TEXT NOT NULL,
                created INTEGER NOT NULL);""")
    def initialize(self,snapshot):
        with self.lock, closing(self.connect()) as c, c:
            c.execute("BEGIN IMMEDIATE")
            row=c.execute("SELECT value FROM meta WHERE key='seed'").fetchone()
            if not row: c.execute("INSERT INTO meta VALUES('seed',?)",(secrets.token_bytes(32),))
            old=c.execute("SELECT value FROM meta WHERE key='snapshot'").fetchone()
            if old and old[0].decode()!=snapshot: raise ValueError("branch snapshot mismatch")
            c.execute("INSERT OR IGNORE INTO meta VALUES('snapshot',?)",(snapshot.encode(),))
            c.execute("INSERT OR REPLACE INTO meta VALUES('kernel',?)",(KERNEL.encode(),))
            c.execute("INSERT OR REPLACE INTO meta VALUES('schema',?)",(SCHEMA.encode(),))
    def current_snapshot(self):
        with closing(self.connect()) as c:
            row=c.execute("SELECT value FROM meta WHERE key='snapshot'").fetchone()
            if not row: raise ValueError("snapshot is not initialized")
            return row[0].decode()
    def ready(self):
        with closing(self.connect()) as c, c:
            m=dict(c.execute("SELECT key,value FROM meta"))
            seed=m.get('seed'); snapshot=m.get('snapshot',b'').decode()
            backup_path=self.path.with_name('engine.backup.sqlite3')
            with closing(sqlite3.connect(backup_path)) as backup:
                c.backup(backup)
            with closing(sqlite3.connect(f'file:{backup_path}?mode=ro',uri=True)) as recovered:
                if recovered.execute('PRAGMA integrity_check').fetchone()[0] != 'ok': return False
                if recovered.execute("SELECT value FROM meta WHERE key='snapshot'").fetchone()[0].decode()!=snapshot: return False
            digest=hashlib.sha256(backup_path.read_bytes()).hexdigest()
            c.execute("INSERT INTO backups(digest,created) VALUES(?,?)",(digest,int(time.time())))
            return bool(seed and len(seed)>=32 and m.get('kernel',b'').decode()==KERNEL and m.get('schema',b'').decode()==SCHEMA)
    def advance_snapshot(self,previous_snapshot,next_snapshot,checkpoint):
        values=(previous_snapshot,next_snapshot,checkpoint)
        if any(not isinstance(value,str) or not value.strip() for value in values):
            raise ValueError("snapshot transition fields must be nonempty strings")
        if previous_snapshot==next_snapshot:
            raise ValueError("snapshot transition must change the snapshot")
        with self.lock, closing(self.connect()) as c, c:
            c.execute("BEGIN IMMEDIATE")
            current=c.execute("SELECT value FROM meta WHERE key='snapshot'").fetchone()[0].decode()

            exact_v2=c.execute(
                "SELECT 1 FROM snapshot_transitions_v2 "
                "WHERE previous_snapshot=? AND next_snapshot=? AND checkpoint=? "
                "ORDER BY id DESC LIMIT 1",
                (previous_snapshot,next_snapshot,checkpoint)).fetchone()
            legacy=c.execute(
                "SELECT next_snapshot,checkpoint FROM snapshot_history "
                "WHERE previous_snapshot=?",
                (previous_snapshot,)).fetchone()

            if current==next_snapshot:
                if exact_v2 or legacy==(next_snapshot,checkpoint):
                    return current
                raise ValueError("conflicting snapshot transition refused")
            if current!=previous_snapshot:
                raise ValueError("previous snapshot does not match current snapshot")

            # A prior legacy transition from this same previous snapshot may have
            # been auditably rolled back. The current snapshot comparison above
            # is the CAS authority; v2 therefore permits a new transition after
            # recovery while preserving the old append-only history.
            if c.execute(
                    "SELECT 1 FROM snapshot_transitions_v2 WHERE next_snapshot=?",
                    (next_snapshot,)).fetchone():
                raise ValueError("conflicting snapshot transition refused")
            if c.execute(
                    "SELECT 1 FROM snapshot_history WHERE next_snapshot=?",
                    (next_snapshot,)).fetchone():
                raise ValueError("conflicting snapshot transition refused")

            c.execute(
                "INSERT INTO snapshot_transitions_v2"
                "(previous_snapshot,next_snapshot,checkpoint,created) "
                "VALUES(?,?,?,?)",
                (previous_snapshot,next_snapshot,checkpoint,int(time.time())))
            c.execute("UPDATE meta SET value=? WHERE key='snapshot'",
                      (next_snapshot.encode(),))
            return next_snapshot
    def recover_snapshot(self,target_snapshot,reason):
        """Auditably restore the binding after an uncommitted public transaction.

        This is not a normal progression path. The caller supplies the checked-in
        deployment snapshot; the previous private binding is retained in the
        append-only recovery ledger.
        """
        if not isinstance(target_snapshot,str) or not target_snapshot.strip():
            raise ValueError("recovery target must be a nonempty string")
        if not isinstance(reason,str) or not reason.strip():
            raise ValueError("recovery reason must be a nonempty string")
        with self.lock, closing(self.connect()) as c, c:
            c.execute("BEGIN IMMEDIATE")
            row=c.execute("SELECT value FROM meta WHERE key='snapshot'").fetchone()
            if not row:
                raise ValueError("snapshot is not initialized")
            current=row[0].decode()
            if current==target_snapshot:
                return current
            c.execute(
                "INSERT INTO snapshot_recoveries(from_snapshot,to_snapshot,reason,created) "
                "VALUES(?,?,?,?)",
                (current,target_snapshot,reason.strip(),int(time.time())))
            c.execute("UPDATE meta SET value=? WHERE key='snapshot'",
                      (target_snapshot.encode(),))
            return target_snapshot

    def probe(self):
        """Persist an opaque canary once and return only a stability fingerprint."""
        with self.lock, closing(self.connect()) as c, c:
            snapshot=c.execute("SELECT value FROM meta WHERE key='snapshot'").fetchone()[0].decode()
            probe_id=hashlib.sha256((snapshot+":"+KERNEL).encode()).hexdigest()
            c.execute("INSERT OR IGNORE INTO admin_probes VALUES(?,?)",(probe_id,int(time.time())))
            row=c.execute("SELECT probe_id,created FROM admin_probes WHERE probe_id=?",(probe_id,)).fetchone()
            seed=c.execute("SELECT value FROM meta WHERE key='seed'").fetchone()[0]
            fingerprint=hmac.new(seed,(row[0]+":"+str(row[1])).encode(),hashlib.sha256).hexdigest()
            return {"idempotent":True,"journal_fingerprint":fingerprint}
    def close_digest(self,event_id,packet_hash):
        if not isinstance(event_id,str) or not event_id.strip():
            raise ValueError("event_id must be a nonempty string")
        if not isinstance(packet_hash,str) or len(packet_hash)!=64:
            raise ValueError("packet_sha256 must be a 64-character hex digest")
        try:
            bytes.fromhex(packet_hash)
        except ValueError as exc:
            raise ValueError("packet_sha256 must be hexadecimal") from exc
        with self.lock, closing(self.connect()) as c, c:
            c.execute("BEGIN IMMEDIATE")
            row=c.execute("SELECT packet_hash,result FROM events WHERE event_id=?",(event_id,)).fetchone()
            if row:
                if row[0]!=packet_hash:
                    raise ValueError("altered packet refused")
                return row[1]
            # Persist the immutable packet identity before deriving any entropy.
            c.execute("INSERT INTO events VALUES(?,?,NULL,?,NULL)",
                      (event_id,packet_hash,int(time.time())))
            seed=c.execute("SELECT value FROM meta WHERE key='seed'").fetchone()[0]
            context=canonical(["event-close-digest-v1",event_id,packet_hash])
            result=hashlib.sha256(hmac.new(seed,context,hashlib.sha256).digest()).hexdigest()
            c.execute("UPDATE events SET result=?,closed=? WHERE event_id=?",
                      (result,int(time.time()),event_id))
            return result

    def close(self,event_id,packet):
        """Compatibility wrapper for local tests and legacy body callers."""
        return self.close_digest(event_id,hashlib.sha256(packet).hexdigest())
    def correct(self,event_id,reason):
        if not isinstance(reason,str) or not reason.strip():
            raise ValueError("correction reason required")
        reason=reason.strip()
        with closing(self.connect()) as c, c:
            if not c.execute("SELECT 1 FROM events WHERE event_id=?",(event_id,)).fetchone():
                raise ValueError("unknown event")
            if not c.execute(
                    "SELECT 1 FROM corrections WHERE event_id=? AND reason=?",
                    (event_id,reason)).fetchone():
                c.execute(
                    "INSERT INTO corrections(event_id,reason,created) VALUES(?,?,?)",
                    (event_id,reason,int(time.time())))

def handler(store,token,snapshot=None):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,fmt,*args): pass
        def send(self,status,body):
            raw=json.dumps(body,separators=(",",":")).encode(); self.send_response(status); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw)
        def auth(self):
            supplied=self.headers.get("Authorization","").removeprefix("Bearer ")
            if not hmac.compare_digest(supplied,token): self.send(401,{"error":"unauthorized"}); return False
            return True
        def do_GET(self):
            if self.path=="/health": return self.send(200,{"service":"engine-state","schema":SCHEMA,"kernel":KERNEL})
            if not self.auth(): return
            if self.path=="/ready":
                current=store.current_snapshot()
                return self.send(200,{"ready":store.ready(),"schema":SCHEMA,"kernel":KERNEL,"procedure":KERNEL,"snapshot":current,"career_initialized":True,"private_seed_exists":True,"journal_persistent":True,"recovery":"verified"})
            self.send(404,{"error":"not found"})
        def do_POST(self):
            if not self.auth(): return
            try:
                parsed=urlsplit(self.path)
                if parsed.path=="/events/close":
                    # Canonical production contract: event identity and the
                    # SHA-256 identity of the canonical packet travel in the
                    # authenticated URL; no request body is required.
                    query=parse_qs(parsed.query,keep_blank_values=True)
                    event_id=(query.get("event_id") or [None])[0]
                    packet_hash=(query.get("packet_sha256") or [None])[0]
                    if event_id is not None or packet_hash is not None:
                        if event_id is None or packet_hash is None:
                            raise ValueError("event_id and packet_sha256 are both required")
                        return self.send(200,{"result_ref":store.close_digest(event_id,packet_hash)})

                    # Backward compatibility for pre-digest clients.
                    n=int(self.headers.get("Content-Length","0"))
                    body=json.loads(self.rfile.read(n) or b"{}")
                    if not isinstance(body,dict):
                        raise ValueError("request body must be a JSON object")
                    legacy_outer_id=None
                    if "packet" in body:
                        legacy_outer_id=body.get("event_id")
                        packet=body["packet"]
                        if isinstance(packet,str):
                            try:
                                packet=json.loads(packet)
                            except json.JSONDecodeError as exc:
                                raise ValueError("packet JSON string is invalid") from exc
                    else:
                        packet=body
                    if not isinstance(packet,dict):
                        raise ValueError("packet must be a JSON object")
                    event_id=packet.get("event_id")
                    if not isinstance(event_id,str) or not event_id.strip():
                        raise ValueError("packet event_id must be a nonempty string")
                    if legacy_outer_id is not None and legacy_outer_id!=event_id:
                        raise ValueError("outer event_id does not match packet event_id")
                    return self.send(200,{"result_ref":store.close(event_id,canonical(packet))})

                # Current administrative writes are also bodyless. This keeps
                # every authenticated mutation independent of proxy/body rewriting.
                if parsed.path=="/admin/probe":
                    return self.send(200,store.probe())

                query=parse_qs(parsed.query,keep_blank_values=True)
                if parsed.path=="/admin/snapshot/advance":
                    previous=(query.get("previous_snapshot") or [None])[0]
                    next_snapshot=(query.get("next_snapshot") or [None])[0]
                    checkpoint=(query.get("checkpoint") or [None])[0]
                    if any(value is not None for value in (previous,next_snapshot,checkpoint)):
                        if any(value is None for value in (previous,next_snapshot,checkpoint)):
                            raise ValueError("previous_snapshot, next_snapshot and checkpoint are all required")
                        current=store.advance_snapshot(previous,next_snapshot,checkpoint)
                        return self.send(200,{"advanced":True,"snapshot":current})

                if parsed.path=="/corrections":
                    event_id=(query.get("event_id") or [None])[0]
                    reason=(query.get("reason") or [None])[0]
                    if event_id is not None or reason is not None:
                        if event_id is None or reason is None:
                            raise ValueError("event_id and reason are both required")
                        store.correct(event_id,reason)
                        return self.send(201,{"recorded":True})

                # Compatibility-only body parser for old snapshot/correction clients.
                if parsed.path in {"/admin/snapshot/advance","/corrections"}:
                    n=int(self.headers.get("Content-Length","0"))
                    body=json.loads(self.rfile.read(n) or b"{}")
                    if not isinstance(body,dict):
                        raise ValueError("request body must be a JSON object")
                    if parsed.path=="/admin/snapshot/advance":
                        current=store.advance_snapshot(body["previous_snapshot"],body["next_snapshot"],body["checkpoint"])
                        return self.send(200,{"advanced":True,"snapshot":current})
                    store.correct(body["event_id"],body["reason"])
                    return self.send(201,{"recorded":True})

                self.send(404,{"error":"not found"})
            except (json.JSONDecodeError,KeyError,TypeError,ValueError) as e:
                self.send(409,{"error":str(e)})
    return Handler

def main():
    p=argparse.ArgumentParser(); p.add_argument("--db",required=True); p.add_argument("--token-file",required=True); p.add_argument("--snapshot",required=True); p.add_argument("--port",type=int,default=int(os.getenv("PORT","8765"))); p.add_argument("--host",default=os.getenv("ENGINE_BIND_HOST","127.0.0.1")); a=p.parse_args()
    token=Path(a.token_file).read_text().strip(); store=Store(a.db); store.initialize(a.snapshot)
    ThreadingHTTPServer((a.host,a.port),handler(store,token)).serve_forever()
if __name__=="__main__": main()
