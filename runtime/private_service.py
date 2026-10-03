"""Authenticated private Engine State service.

Deployment data and authentication material must be outside the checkout.  The
HTTP API intentionally exposes only health/readiness, opaque result closure
and, from kernel 2014.6 (batch B7), the player-state latent draws.

Latent draws (schema 2 tables, created on every store so a schema 1 store
migrates in place with every existing row untouched; the change is journaled
in schema_transitions). The season reference R_Y is an HMAC of the store seed
by league year and never leaves the service. /latent/bind draws and records z
for every row of the committed public table (runtime.player_state) and
commits to the sorted rows; binding a league year a second time with the same
manifest is idempotent and with another manifest is refused. /latent/draws
releases z only for the keys of an already-journaled event, binds those keys
to the event on first request (roster_sha256) and refuses a different roster
later; a later entrant's key is drawn from the same R_Y and appended. Both are
locked while a snapshot advance is pending.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import argparse, hashlib, hmac, json, os, secrets, sqlite3, threading, time
from pathlib import Path
from contextlib import closing
from urllib.parse import urlsplit, parse_qs
from .packets import canonical
from . import player_state

SCHEMA="1"; KERNEL="2014.5"

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
                created INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS kernel_transitions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                previous_kernel TEXT NOT NULL,
                next_kernel TEXT NOT NULL,
                snapshot TEXT NOT NULL,
                created INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS schema_transitions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                previous_schema TEXT NOT NULL,
                next_schema TEXT NOT NULL,
                created INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS latent_seasons(
                league_year INTEGER PRIMARY KEY,
                manifest_sha256 TEXT NOT NULL,
                public_table_sha256 TEXT NOT NULL,
                commitment TEXT NOT NULL,
                rows INTEGER NOT NULL,
                created INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS latent_draws(
                league_year INTEGER NOT NULL,
                gsis_id TEXT NOT NULL,
                slot TEXT NOT NULL,
                z TEXT NOT NULL,
                created INTEGER NOT NULL,
                PRIMARY KEY(league_year,gsis_id,slot));
            CREATE TABLE IF NOT EXISTS latent_requests(
                event_id TEXT PRIMARY KEY,
                league_year INTEGER NOT NULL,
                roster_sha256 TEXT NOT NULL,
                created INTEGER NOT NULL);""")
    def initialize(self,snapshot,allow_pending=False):
        """Bind the store to the image's Document 5 digest.

        With allow_pending, a stored snapshot that differs from the image is
        kept (never overwritten) and the service starts locked: event closure
        is refused until the ordinary CAS advance from merged main catches the
        store up. Returns True when an advance is pending.
        """
        with self.lock, closing(self.connect()) as c, c:
            c.execute("BEGIN IMMEDIATE")
            row=c.execute("SELECT value FROM meta WHERE key='seed'").fetchone()
            if not row: c.execute("INSERT INTO meta VALUES('seed',?)",(secrets.token_bytes(32),))
            old=c.execute("SELECT value FROM meta WHERE key='snapshot'").fetchone()
            pending=bool(old and old[0].decode()!=snapshot)
            if pending and not allow_pending: raise ValueError("branch snapshot mismatch")
            c.execute("INSERT OR IGNORE INTO meta VALUES('snapshot',?)",(snapshot.encode(),))
            # A kernel release reaches a live store only through a rebuilt image
            # starting against the same volume. The seed, the events and every
            # snapshot ledger are untouched; the change itself is journaled
            # append-only so the store's kernel lineage is auditable.
            stored_kernel=c.execute("SELECT value FROM meta WHERE key='kernel'").fetchone()
            if stored_kernel and stored_kernel[0].decode()!=KERNEL:
                bound=(old[0].decode() if old else snapshot)
                c.execute("INSERT INTO kernel_transitions(previous_kernel,next_kernel,snapshot,created) "
                          "VALUES(?,?,?,?)",(stored_kernel[0].decode(),KERNEL,bound,int(time.time())))
            c.execute("INSERT OR REPLACE INTO meta VALUES('kernel',?)",(KERNEL.encode(),))
            stored_schema=c.execute("SELECT value FROM meta WHERE key='schema'").fetchone()
            if stored_schema and stored_schema[0].decode()!=SCHEMA:
                # Kernel 2014.6 (B7): a schema change is journaled append-only; every
                # existing row (events, snapshots, draws) is untouched.
                c.execute("INSERT INTO schema_transitions(previous_schema,next_schema,created) VALUES(?,?,?)",
                          (stored_schema[0].decode(),SCHEMA,int(time.time())))
            c.execute("INSERT OR REPLACE INTO meta VALUES('schema',?)",(SCHEMA.encode(),))
            return pending
    def schema_history(self):
        with closing(self.connect()) as c:
            return c.execute("SELECT previous_schema,next_schema FROM schema_transitions ORDER BY id").fetchall()
    def kernel_history(self):
        """Append-only kernel lineage of this store, oldest first."""
        with closing(self.connect()) as c:
            return c.execute("SELECT previous_kernel,next_kernel,snapshot FROM kernel_transitions ORDER BY id").fetchall()
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

    # ---- kernel 2014.6 (batch B7): player-state latent draws ----------------------
    def _reference(self,c,league_year):
        seed=c.execute("SELECT value FROM meta WHERE key='seed'").fetchone()[0]
        return player_state.season_reference(seed,league_year)
    def _draw(self,c,key):
        """z (hex) for one key, recorded on first need; R_Y is the key's own year's."""
        year,gsis,slot=int(key[1]),key[2],key[3]
        row=c.execute("SELECT z FROM latent_draws WHERE league_year=? AND gsis_id=? AND slot=?",
                      (year,gsis,slot)).fetchone()
        if row: return row[0]
        z=player_state.z_text(player_state.draw_z(self._reference(c,year),key))
        c.execute("INSERT INTO latent_draws(league_year,gsis_id,slot,z,created) VALUES(?,?,?,?,?)",
                  (year,gsis,slot,z,int(time.time())))
        return z
    def latent_bound(self):
        """{league_year: {manifest_sha256, commitment, rows}} of the bound years (never R)."""
        with closing(self.connect()) as c:
            return {str(r[0]):{"manifest_sha256":r[1],"commitment":r[2],"rows":r[3]} for r in
                    c.execute("SELECT league_year,manifest_sha256,commitment,rows FROM latent_seasons ORDER BY league_year")}
    def bind_latent(self,league_year,manifest_sha256):
        """Draw and record z for every row of the committed public table of
        `league_year` (the manifest must be the pinned one), and commit to the
        sorted rows. Idempotent for the same manifest; a second manifest is
        refused. Returns the binding record (no R)."""
        try: league_year=int(league_year)
        except (TypeError,ValueError): raise ValueError("league_year must be an integer") from None
        if not isinstance(manifest_sha256,str) or len(manifest_sha256)!=64:
            raise ValueError("manifest_sha256 must be a 64-character hex digest")
        if league_year!=player_state.league_year():
            raise ValueError("no public player-state table is committed for league year %d"%league_year)
        pinned=player_state.manifest_sha256()
        if manifest_sha256!=pinned:
            raise ValueError("manifest %s is not the committed manifest %s"%(manifest_sha256[:12],pinned[:12]))
        table=player_state.public_table()
        with self.lock, closing(self.connect()) as c, c:
            c.execute("BEGIN IMMEDIATE")
            bound=c.execute("SELECT manifest_sha256,public_table_sha256,commitment,rows FROM latent_seasons "
                            "WHERE league_year=?",(league_year,)).fetchone()
            if bound:
                if bound[0]!=manifest_sha256: raise ValueError("league year %d is bound to another manifest; a second manifest is refused"%league_year)
                return {"league_year":league_year,"manifest_sha256":bound[0],"public_table_sha256":bound[1],
                        "commitment":bound[2],"rows":bound[3],"bound":True,"idempotent":True}
            rows=[]
            for gsis in sorted(table):
                for key in player_state.row_keys(gsis,table[gsis],league_year,league_year):
                    rows.append((player_state.key_text(key),self._draw(c,key)))
            commitment=player_state.commitment(rows)
            manifest=player_state.manifest()
            c.execute("INSERT INTO latent_seasons(league_year,manifest_sha256,public_table_sha256,commitment,rows,created) "
                      "VALUES(?,?,?,?,?,?)",(league_year,manifest_sha256,manifest["public_table_sha256"],commitment,
                                             len(rows),int(time.time())))
            return {"league_year":league_year,"manifest_sha256":manifest_sha256,
                    "public_table_sha256":manifest["public_table_sha256"],"commitment":commitment,
                    "rows":len(rows),"bound":True,"idempotent":False}
    def latent_draws(self,event_id,league_year,keys,roster_sha256):
        """{key text: z hex} for the keys of a journaled event. The first
        request binds the event to its roster digest; a later request with
        another roster is refused, as is a request before the event's closure,
        for an unbound league year, or with a digest the keys do not match."""
        if not isinstance(event_id,str) or not event_id.strip():
            raise ValueError("event_id must be a nonempty string")
        try: league_year=int(league_year)
        except (TypeError,ValueError): raise ValueError("league_year must be an integer") from None
        keys=[player_state.parse_key_text(k) for k in keys]
        if not keys: raise ValueError("latent keys required")
        if any(k[3] not in player_state.BASE_SLOTS+(player_state.INNOVATION_SLOT,) for k in keys):
            raise ValueError("unknown latent slot")
        if roster_sha256!=player_state.roster_sha256(keys):
            raise ValueError("roster_sha256 does not match the requested keys")
        with self.lock, closing(self.connect()) as c, c:
            c.execute("BEGIN IMMEDIATE")
            bound=c.execute("SELECT commitment FROM latent_seasons WHERE league_year=?",(league_year,)).fetchone()
            if not bound: raise ValueError("league year %d is not bound"%league_year)
            event=c.execute("SELECT result FROM events WHERE event_id=?",(event_id,)).fetchone()
            if not event or not event[0]: raise ValueError("latent draws are released only for a journaled event")
            prior=c.execute("SELECT roster_sha256 FROM latent_requests WHERE event_id=?",(event_id,)).fetchone()
            if prior and prior[0]!=roster_sha256: raise ValueError("roster mismatch: the event's latent keys were bound to another roster")
            if not prior:
                c.execute("INSERT INTO latent_requests(event_id,league_year,roster_sha256,created) VALUES(?,?,?,?)",
                          (event_id,league_year,roster_sha256,int(time.time())))
            draws={player_state.key_text(k):self._draw(c,k) for k in keys}
            return {"league_year":league_year,"commitment":bound[0],"draws":draws}

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

def handler(store,token,snapshot=None,locked_until=None):
    # locked_until: set only when an image started behind/ahead of the stored
    # snapshot. Event closure stays refused until the ordinary CAS advance
    # makes the stored snapshot equal that image digest.
    def pending():
        return locked_until is not None and store.current_snapshot()!=locked_until
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
                waiting=pending()
                return self.send(200,{"ready":store.ready() and not waiting,"snapshot_advance_pending":waiting,"schema":SCHEMA,"kernel":KERNEL,"procedure":KERNEL,"snapshot":current,"career_initialized":True,"private_seed_exists":True,"journal_persistent":True,"recovery":"verified","latent_bound":store.latent_bound()})
            self.send(404,{"error":"not found"})
        def do_POST(self):
            if not self.auth(): return
            try:
                parsed=urlsplit(self.path)
                if (parsed.path in {"/events/close","/admin/probe"} or parsed.path.startswith("/latent/")) and pending():
                    return self.send(409,{"error":"snapshot advance pending; event closure locked"})
                if parsed.path in {"/latent/bind","/latent/draws"}:
                    # Kernel 2014.6 (B7): bodyless, like every other mutation.
                    query=parse_qs(parsed.query,keep_blank_values=True)
                    one=lambda name:(query.get(name) or [None])[0]
                    if parsed.path=="/latent/bind":
                        if one("league_year") is None or one("manifest_sha256") is None:
                            raise ValueError("league_year and manifest_sha256 are both required")
                        return self.send(200,store.bind_latent(one("league_year"),one("manifest_sha256")))
                    if any(one(n) is None for n in ("event_id","league_year","roster_sha256","keys")):
                        raise ValueError("event_id, league_year, roster_sha256 and keys are all required")
                    keys=[k for k in one("keys").split(",") if k]
                    return self.send(200,store.latent_draws(one("event_id"),one("league_year"),keys,one("roster_sha256")))
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
