"""Public client for the private Engine State service."""
import base64
import json
import os
from urllib.request import Request, urlopen

from .packets import Packet

class RemoteResolver:
    def __init__(self, base_url=None, token=None, timeout=10):
        self.base_url = (base_url or os.environ["ENGINE_RUNTIME_URL"]).rstrip("/")
        self.token = token or os.environ["ENGINE_API_TOKEN"]
        self.timeout = timeout

    def __call__(self, packet: Packet):
        body = json.dumps({"packet_b64": base64.b64encode(packet.payload).decode()}).encode()
        req = Request(
            self.base_url + "/v1/resolve", data=body,
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + self.token},
            method="POST",
        )
        with urlopen(req, timeout=self.timeout) as response:
            payload = json.load(response)
        return payload["outcome"]
