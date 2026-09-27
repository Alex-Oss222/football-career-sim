#!/usr/bin/env python3
"""Container entry point; deployment secrets and persistent storage stay external."""
import hashlib, os, secrets, sys
from pathlib import Path
from http.server import ThreadingHTTPServer
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from runtime.private_service import Store, handler

state_file=ROOT/"state/05_Current_Season_State.md"
snapshot=os.getenv("ENGINE_SNAPSHOT") or hashlib.sha256(state_file.read_bytes()).hexdigest()
token=os.environ["ENGINE_API_TOKEN"]
path=Path(os.getenv("ENGINE_DATABASE_PATH","/data/engine.sqlite3"))
store=Store(path)
locked_until=None
if os.getenv("ENGINE_RECOVER_TO_CHECKED_IN_SNAPSHOT")=="1":
    try:
        store.initialize(snapshot)
    except ValueError as exc:
        if str(exc)!="branch snapshot mismatch":
            raise
        reason=os.getenv("ENGINE_RECOVERY_REASON","").strip()
        if not reason:
            raise RuntimeError("ENGINE_RECOVERY_REASON required for snapshot recovery") from exc
        store.recover_snapshot(snapshot,reason)
        store.initialize(snapshot)
else:
    # A newer merged image may start before the ordinary CAS advance. It
    # starts locked (no event closure) instead of crashing, so the advance
    # can still reach it; readiness stays BLOCKED until the digests agree.
    if store.initialize(snapshot,allow_pending=True):
        locked_until=snapshot
        print("engine started LOCKED: stored snapshot differs from image; run advance_private_snapshot.py from merged main",flush=True)
server=ThreadingHTTPServer((os.getenv("ENGINE_BIND_HOST","0.0.0.0"),int(os.getenv("PORT","8765"))),handler(store,token,snapshot,locked_until))
server.serve_forever()
