"""A local, test-only private Engine State service with a pinned store seed.

The production store draws its seed once with ``secrets.token_bytes`` (never
checked in). Tests that drive the production runner through it would
otherwise run under a different seed on every run; pinning the seed before
``Store.initialize`` (which keeps an existing seed row) makes each test
reproducible and lets a regression pin the exact seed that exposed a defect.
Synthetic snapshots and tokens only; nothing here reaches the live runtime.
"""
import hashlib
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

from runtime.private_client import Client
from runtime.private_service import Store, handler

TOKEN = "test-only-token"


def pinned_seed(label):
    """The 32-byte store seed for a label (``"398"`` reproduces the kernel
    chain-feasibility regression of October 2026)."""
    return hashlib.sha256(b"repro-store-seed-" + str(label).encode()).digest()


def local_service(testcase, root, label, snapshot="snapshot"):
    """Start a private service bound to ``root`` with the pinned seed for
    ``label``; returns (store, client). Shut down with the test case."""
    store = Store(Path(root) / "state.sqlite3")
    with store.connect() as c:
        c.execute("INSERT OR IGNORE INTO meta VALUES('seed',?)", (pinned_seed(label),))
    store.initialize(snapshot)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler(store, TOKEN, snapshot))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    testcase.addCleanup(server.server_close)
    testcase.addCleanup(server.shutdown)
    return store, Client(f"http://127.0.0.1:{server.server_port}", token=TOKEN, snapshot=snapshot)
