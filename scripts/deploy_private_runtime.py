#!/usr/bin/env python3
"""Install/start the localhost-only private service outside the Git checkout."""
import hashlib, os, secrets, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
STATE=Path("/var/lib/football-career-sim-engine")
TOKEN=Path("/run/secrets/football-career-sim-engine-token")
SNAPSHOT=hashlib.sha256((ROOT/"state/05_Current_Season_State.md").read_bytes()).hexdigest()
STATE.mkdir(parents=True,exist_ok=True); TOKEN.parent.mkdir(parents=True,exist_ok=True)
if not TOKEN.exists(): TOKEN.write_text(secrets.token_urlsafe(48)); os.chmod(TOKEN,0o600)
cmd=[sys.executable,"-m","runtime.private_service","--db",str(STATE/"engine.sqlite3"),"--token-file",str(TOKEN),"--snapshot",SNAPSHOT]
subprocess.Popen(cmd,cwd=ROOT,stdout=open(STATE/"service.log","ab"),stderr=subprocess.STDOUT,start_new_session=True)
time.sleep(.5)
from runtime.private_client import Client
print("private runtime READY" if Client().readiness()["ready"] else "private runtime BLOCKED")
