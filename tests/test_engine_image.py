"""The engine image carries every file the private service reads.

Kernel 2014.6 release review (October 17, 2026). The other service tests run
the service from the full checkout, so a file that the final stage of
Dockerfile.engine leaves out goes unnoticed until the deployed 2014 bind
(release step 6) fails. These tests rebuild the final stage's file set from
its COPY lines in a temporary directory, start its CMD from there in an
isolated interpreter and bind the 2014 player states over HTTP, as
scripts/bind_latent_season.py does against the deployed service. Synthetic
token and store only; nothing here reaches the live runtime.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.request import urlopen

from runtime import KERNEL_VERSION, player_state as ps
from runtime.private_client import Client, PrivateRuntimeUnavailable
from runtime.private_service import KERNEL, SCHEMA

ROOT = Path(__file__).resolve().parents[1]
TOKEN = "test-only-image-token"


def final_stage():
    """(copies, cmd, workdir) of the last stage of Dockerfile.engine."""
    lines = (ROOT / "Dockerfile.engine").read_text().splitlines()
    start = max(i for i, line in enumerate(lines) if line.startswith("FROM "))
    copies, cmd, workdir = [], None, None
    for line in lines[start + 1:]:
        words = line.split()
        if not words or words[0].startswith("#"):
            continue
        if words[0] == "WORKDIR":
            workdir = words[1]
        elif words[0] == "COPY":
            if len(words) != 4 or words[1] != "--from=verify" or not words[2].startswith("/app/"):
                raise AssertionError("unexpected final-stage COPY: " + line)
            copies.append((words[2][len("/app/"):], words[3]))
        elif words[0] == "CMD":
            cmd = json.loads(line[len("CMD"):].strip())
    return copies, cmd, workdir


def build_image_layout(app):
    """Copy the checkout's files into `app` exactly as the final stage does."""
    copies, _, _ = final_stage()
    for source, destination in copies:
        src, dst = ROOT / source, app / destination
        if src.is_dir():
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
    return app


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class EngineImageTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.app = build_image_layout(self.tmp / "app")

    def serve(self):
        """Start the image's CMD from the layout; returns a client bound to its snapshot."""
        copies, cmd, workdir = final_stage()
        self.assertEqual(workdir, "/app")
        self.assertEqual(cmd[0], "python")
        port = free_port()
        env = {k: v for k, v in os.environ.items() if not k.startswith(("PYTHON", "ENGINE_"))}
        env.update(ENGINE_API_TOKEN=TOKEN, ENGINE_DATABASE_PATH=str(self.tmp / "engine.sqlite3"),
                   ENGINE_BIND_HOST="127.0.0.1", PORT=str(port),
                   PYTHONDONTWRITEBYTECODE="1", PYTHONUNBUFFERED="1")
        # -I: the checkout (PYTHONPATH, the current directory) is never on the path.
        process = subprocess.Popen([sys.executable, "-I", *cmd[1:]], cwd=self.app, env=env,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.addCleanup(lambda: process.communicate())
        self.addCleanup(process.kill)
        url = "http://127.0.0.1:%d" % port
        deadline = time.time() + 30
        while True:
            try:
                with urlopen(url + "/health", timeout=1) as r:
                    health = json.load(r)
                break
            except OSError:
                if process.poll() is not None or time.time() > deadline:
                    self.fail("image service did not start: " + (process.communicate()[0] or ""))
                time.sleep(0.1)
        self.assertEqual((health["schema"], health["kernel"]), (SCHEMA, KERNEL))
        snapshot = hashlib.sha256((self.app / "state/05_Current_Season_State.md").read_bytes()).hexdigest()
        return Client(url, token=TOKEN, snapshot=snapshot), process

    def test_final_stage_binds_the_2014_player_states(self):
        self.assertEqual(KERNEL, KERNEL_VERSION)
        for path in (ps.MODEL_PATH, ps.PUBLIC_PATH, ps.MANIFEST_PATH):
            image_copy = self.app / path.relative_to(ROOT)
            self.assertTrue(image_copy.is_file(), path.relative_to(ROOT).as_posix())
            self.assertEqual(image_copy.read_bytes(), path.read_bytes())
        client, _ = self.serve()
        # Release steps 4-5 (health, ready, canaries), then step 6 (the bind).
        self.assertTrue(client.readiness()["ready"])
        bound = client.bind_latent(2014, ps.manifest_sha256())
        table = ps.public_table()
        self.assertEqual(bound["manifest_sha256"], ps.manifest_sha256())
        self.assertEqual(bound["public_table_sha256"], ps.manifest()["public_table_sha256"])
        self.assertEqual(bound["rows"], sum(len(ps.row_keys(g, r, 2014, 2014)) for g, r in table.items()))
        self.assertFalse(bound["idempotent"])

    def test_a_missing_data_file_answers_instead_of_dropping_the_request(self):
        (self.app / ps.MANIFEST_PATH.relative_to(ROOT)).unlink()
        client, process = self.serve()
        with self.assertRaisesRegex(PrivateRuntimeUnavailable, r"/latent/bind failed closed \(HTTP 500: "
                                    r"private runtime data unavailable: .*2014_player_state_manifest\.json"):
            client.bind_latent(2014, ps.manifest_sha256())
        self.assertIsNone(process.poll())
        self.assertTrue(client.readiness()["ready"])


if __name__ == "__main__":
    unittest.main()
