"""Authenticated private Engine State service.

Deployment data and authentication material must be outside the checkout.  The
HTTP API intentionally exposes only health/readiness and opaque result closure.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import argparse, hashlib, hmac, json, os, secrets, sqlite3, threading, time
from pathlib import Path
from contextlib import closing

SCHEMA="1"; KERNEL="2013.1"

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
            CREATE TABLE IF NOT EXISTS backups(id INTEGER PRIMARY KEY AUTOINCREMENT,digest TEXT NOT NULL,created INTEGER NOT NULL);""")
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
    def ready(self,expected_snapshot):
        with closing(self.connect()) as c, c:
            m=dict(c.execute("SELECT key,value FROM meta"))
            seed=m.get('seed'); snapshot=m.get('snapshot',b'').decode()
            backup_path=self.path.with_name('engine.backup.sqlite3')
            with closing(sqlite3.connect(backup_path)) as backup:
                c.backup(backup)
            with closing(sqlite3.connect(f'file:{backup_path}?mode=ro',uri=True)) as recovered:
                if recovered.execute('PRAGMA integrity_check').fetchone()[0] != 'ok': return False
                if recovered.execute("SELECT value FROM meta WHERE key='snapshot'").fetchone()[0].decode()!=expected_snapshot: return False
            digest=hashlib.sha256(backup_path.read_bytes()).hexdigest()
            c.execute("INSERT INTO backups(digest,created) VALUES(?,?)",(digest,int(time.time())))
            return bool(seed and len(seed)>=32 and snapshot==expected_snapshot and m.get('kernel',b'').decode()==KERNEL and m.get('schema',b'').decode()==SCHEMA)
    def close(self,event_id,packet):
        packet_hash=hashlib.sha256(packet).hexdigest()
        with self.lock, closing(self.connect()) as c, c:
            c.execute("BEGIN IMMEDIATE")
            row=c.execute("SELECT packet_hash,result FROM events WHERE event_id=?",(event_id,)).fetchone()
            if row:
                if row[0]!=packet_hash: raise ValueError("altered packet refused")
                return row[1]
            # Journal packet identity before deriving/drawing the result.
            c.execute("INSERT INTO events VALUES(?,?,NULL,?,NULL)",(event_id,packet_hash,int(time.time())))
            seed=c.execute("SELECT value FROM meta WHERE key='seed'").fetchone()[0]
            result=hashlib.sha256(hmac.new(seed,packet,hashlib.sha256).digest()).hexdigest()
            c.execute("UPDATE events SET result=?,closed=? WHERE event_id=?",(result,int(time.time()),event_id))
            return result
    def correct(self,event_id,reason):
        if not reason.strip(): raise ValueError("correction reason required")
        with closing(self.connect()) as c, c:
            if not c.execute("SELECT 1 FROM events WHERE event_id=?",(event_id,)).fetchone(): raise ValueError("unknown event")
            c.execute("INSERT INTO corrections(event_id,reason,created) VALUES(?,?,?)",(event_id,reason,int(time.time())))

def handler(store,token,snapshot):
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
            if self.path=="/ready": return self.send(200,{"ready":store.ready(snapshot),"schema":SCHEMA,"kernel":KERNEL,"career_initialized":True,"snapshot_initialized":True,"recovery":"verified"})
            self.send(404,{"error":"not found"})
        def do_POST(self):
            if not self.auth(): return
            n=int(self.headers.get("Content-Length","0")); body=json.loads(self.rfile.read(n) or b"{}")
            try:
                if self.path=="/events/close": return self.send(200,{"result_ref":store.close(body["event_id"],json.dumps(body["packet"],sort_keys=True,separators=(",",":")).encode())})
                if self.path=="/corrections": store.correct(body["event_id"],body["reason"]); return self.send(201,{"recorded":True})
                self.send(404,{"error":"not found"})
            except (KeyError,ValueError) as e: self.send(409,{"error":str(e)})
    return Handler

def main():
    p=argparse.ArgumentParser(); p.add_argument("--db",required=True); p.add_argument("--token-file",required=True); p.add_argument("--snapshot",required=True); p.add_argument("--port",type=int,default=8765); a=p.parse_args()
    token=Path(a.token_file).read_text().strip(); store=Store(a.db); store.initialize(a.snapshot)
    ThreadingHTTPServer(("127.0.0.1",a.port),handler(store,token,a.snapshot)).serve_forever()
if __name__=="__main__": main()
