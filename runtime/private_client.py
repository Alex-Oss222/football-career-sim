"""Fail-closed adapter for the access-isolated Engine State deployment."""
import json, os
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from . import KERNEL_VERSION, SCHEMA_VERSION

DEFAULT_URL="http://127.0.0.1:8765"
DEFAULT_TOKEN_FILE="/run/secrets/football-career-sim-engine-token"

class PrivateRuntimeUnavailable(RuntimeError): pass

class Client:
    def __init__(self,url=None,token_file=None):
        self.url=(url or os.getenv("FCS_ENGINE_URL") or DEFAULT_URL).rstrip("/")
        self.token_file=Path(token_file or os.getenv("FCS_ENGINE_TOKEN_FILE") or DEFAULT_TOKEN_FILE)
    def _request(self,path,body=None):
        try: token=self.token_file.read_text().strip()
        except OSError as e: raise PrivateRuntimeUnavailable("private credentials unavailable") from e
        headers={"Authorization":f"Bearer {token}"}
        data=None
        if body is not None: data=json.dumps(body,separators=(",",":")).encode(); headers["Content-Type"]="application/json"
        try:
            with urlopen(Request(self.url+path,data=data,headers=headers),timeout=3) as r: return json.load(r)
        except (OSError,HTTPError,URLError,json.JSONDecodeError) as e: raise PrivateRuntimeUnavailable("private runtime probe failed closed") from e
    def readiness(self):
        data=self._request("/ready")
        required=(data.get("ready") and data.get("schema")==SCHEMA_VERSION and data.get("kernel")==KERNEL_VERSION and data.get("career_initialized") and data.get("snapshot_initialized") and data.get("recovery")=="verified")
        if not required: raise PrivateRuntimeUnavailable("private runtime identity or recovery mismatch")
        return {"authenticated":True,"ready":True,"schema":data["schema"],"kernel":data["kernel"],"recovery":data["recovery"]}
    def close_event(self,event_id,packet): return self._request("/events/close",{"event_id":event_id,"packet":packet})["result_ref"]
