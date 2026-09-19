"""Fail-closed adapter for the access-isolated Engine State deployment.

Only readiness metadata crosses this boundary.  In particular, the API never
returns the career seed, frozen packets, ratings, or journal rows.
"""
import hashlib, json, os
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from . import KERNEL_VERSION, SCHEMA_VERSION
from .packets import canonical

DEFAULT_URL="http://127.0.0.1:8765"
DEFAULT_TOKEN_FILE="/run/secrets/football-career-sim-engine-token"
READINESS_CLOSE_CANARY_CONTRACT="event-close-canary-v2"

class PrivateRuntimeUnavailable(RuntimeError): pass

def _readiness_close_packet(snapshot,kernel):
    """Build a versioned administrative closure canary.

    The event identity is derived from the canonical canary payload itself, so a
    future canary schema/contract change cannot collide with an older frozen
    administrative event in the persistent journal.
    """
    body={"administrative":True,
          "contract":READINESS_CLOSE_CANARY_CONTRACT,
          "kernel":kernel,
          "snapshot":snapshot,
          "type":"readiness-close-probe"}
    event_id="__readiness_close_probe__:"+hashlib.sha256(canonical(body)).hexdigest()
    return {"event_id":event_id,**body}

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
        except HTTPError as e:
            detail=None
            try:
                payload=json.loads(e.read().decode("utf-8"))
                if isinstance(payload,dict) and isinstance(payload.get("error"),str):
                    detail=payload["error"].strip()
            except (OSError,UnicodeDecodeError,json.JSONDecodeError):
                pass
            suffix=f": {detail}" if detail else ""
            raise PrivateRuntimeUnavailable(
                f"private runtime {path} failed closed (HTTP {e.code}{suffix})"
            ) from e
        except (OSError,URLError,json.JSONDecodeError) as e:
            raise PrivateRuntimeUnavailable(f"private runtime {path} failed closed") from e
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
        # Exercise the same authenticated transport and immutable event journal
        # used by a real game. The reserved identity is derived from the whole
        # versioned canary payload, so older frozen canaries cannot conflict.
        packet=_readiness_close_packet(data["snapshot"],data["kernel"])
        close_first=self.close_event(packet)
        close_second=self.close_event(packet)
        if not (isinstance(close_first,str) and close_first and close_first==close_second):
            raise PrivateRuntimeUnavailable("private runtime event closure probe is not idempotent")
        return {"authenticated":True,"ready":True,"schema":data["schema"],
                "kernel":data["kernel"],"snapshot":data["snapshot"],
                "recovery":data["recovery"],"journal_persistent":True,
                "administrative_probe_idempotent":True,
                "event_closure_probe_idempotent":True}
    def close_event(self,packet):
        if not isinstance(packet,dict):
            raise ValueError("packet must be a JSON object")
        event_id=packet.get("event_id")
        if not isinstance(event_id,str) or not event_id.strip():
            raise ValueError("packet event_id must be a nonempty string")
        data=self._request("/events/close",{"packet":packet})
        result_ref=data.get("result_ref")
        if not isinstance(result_ref,str) or not result_ref:
            raise PrivateRuntimeUnavailable("private runtime returned invalid event reference")
        return result_ref
    def current_snapshot(self):
        data=self._request("/ready")
        snapshot=data.get("snapshot")
        if not isinstance(snapshot,str) or not snapshot:
            raise PrivateRuntimeUnavailable("private runtime returned invalid snapshot")
        return snapshot
    def advance_snapshot(self,previous_snapshot,next_snapshot,checkpoint):
        for name,value in (("previous_snapshot",previous_snapshot),
                           ("next_snapshot",next_snapshot),("checkpoint",checkpoint)):
            if not isinstance(value,str) or not value.strip():
                raise ValueError(f"{name} must be a nonempty string")
        data=self._request("/admin/snapshot/advance",{
            "previous_snapshot":previous_snapshot,"next_snapshot":next_snapshot,
            "checkpoint":checkpoint})
        return data["snapshot"]
