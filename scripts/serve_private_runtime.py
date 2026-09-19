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
store=Store(path); store.initialize(snapshot)
server=ThreadingHTTPServer((os.getenv("ENGINE_BIND_HOST","0.0.0.0"),int(os.getenv("PORT","8765"))),handler(store,token,snapshot))
server.serve_forever()
