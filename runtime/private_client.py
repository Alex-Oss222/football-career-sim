"""Fail-closed adapter for the access-isolated Engine State deployment.

Only readiness metadata crosses this boundary.  In particular, the API never
returns the career seed, frozen packets, ratings, or journal rows.
"""
import hashlib, json, os
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from . import KERNEL_VERSION, SCHEMA_VERSION

DEFAULT_URL="http://127.0.0.1:8765"
DEFAULT_TOKEN_FILE="/run/secrets/football-career-sim-engine-token"

class PrivateRuntimeUnavailable(RuntimeError): pass

class Client:
    def __init__(self,url=None,token=None,token_file=None,snapshot=None):
        self.url=(url or os.getenv("ENGINE_RUNTIME_URL") or os.getenv("FCS_ENGINE_URL") or DEFAULT_URL).rstrip("/")
        # An explicit test token file must not be shadowed by production env.
        self.token=token if token is not None else (None if token_file is not None else os.getenv("ENGINE_API_TOKEN"))
        self.token_file=Path(token_file or os.getenv("FCS_ENGINE_TOKEN_FILE") or DEFAULT_TOKEN_FILE)
        self.snapshot=snapshot or hashlib.sha256(
            (Path(__file__).resolve().parents[1]/"state/05_Current_Season_State.md").read_bytes()
        ).hexdigest()
    def _request(self,path,body=None):
        token=self.token
        if not token:
            try: token=self.token_file.read_text().strip()
            except OSError as e: raise PrivateRuntimeUnavailable("private credentials unavailable") from e
        if not token: raise PrivateRuntimeUnavailable("private credentials unavailable")
        headers={"Authorization":f"Bearer {token}"}
        data=None
        if body is not None: data=json.dumps(body,separators=(",",":")).encode(); headers["Content-Type"]="application/json"
        try:
            with urlopen(Request(self.url+path,data=data,headers=headers),timeout=3) as r: return json.load(r)
        except (OSError,HTTPError,URLError,json.JSONDecodeError) as e: raise PrivateRuntimeUnavailable("private runtime probe failed closed") from e
    def readiness(self):
        health=self._request("/health")
        if health.get("schema")!=SCHEMA_VERSION or health.get("kernel")!=KERNEL_VERSION:
            raise PrivateRuntimeUnavailable("private runtime health identity mismatch")
        data=self._request("/ready")
        required=(data.get("ready") and data.get("schema")==SCHEMA_VERSION and data.get("kernel")==KERNEL_VERSION and data.get("procedure")==KERNEL_VERSION and data.get("snapshot")==self.snapshot and data.get("career_initialized") and data.get("private_seed_exists") and data.get("journal_persistent") and data.get("recovery")=="verified")
        if not required: raise PrivateRuntimeUnavailable("private runtime identity or recovery mismatch")
        first=self._request("/admin/probe",{})
        second=self._request("/admin/probe",{})
        if not (first.get("idempotent") and second.get("idempotent") and
                first.get("journal_fingerprint") and
                first.get("journal_fingerprint")==second.get("journal_fingerprint")):
            raise PrivateRuntimeUnavailable("private runtime administrative probe is not idempotent")
        return {"authenticated":True,"ready":True,"schema":data["schema"],
                "kernel":data["kernel"],"snapshot":data["snapshot"],
                "recovery":data["recovery"],"journal_persistent":True,
                "administrative_probe_idempotent":True}
    def close_event(self,event_id,packet): return self._request("/events/close",{"event_id":event_id,"packet":packet})["result_ref"]
