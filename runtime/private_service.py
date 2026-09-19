"""Access-isolated Railway service for private Engine State.

The public /health endpoint exposes no seed, ratings, packets or journal data.
All mutation/resolution/self-test endpoints require a bearer token.
"""
import base64
import hashlib
import json
import os
import secrets
from flask import Flask, jsonify, request
import psycopg
from psycopg.rows import dict_row

from runtime.packets import Packet, PacketConflict, resolve

SCHEMA_VERSION = "1"
PROCEDURE_VERSION = "2013-drive-kernel-v1"
SNAPSHOT = os.environ.get("CAREER_SNAPSHOT", "JAX-2013-AUG08-WALKTHROUGH-STATE-7")
DATABASE_URL = os.environ["DATABASE_URL"]
API_TOKEN = os.environ["ENGINE_API_TOKEN"]

app = Flask(__name__)

def db():
    return psycopg.connect(DATABASE_URL, autocommit=False, row_factory=dict_row)

def initialize():
    with db() as conn:
        with conn.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS engine_meta (
                key TEXT PRIMARY KEY, value BYTEA NOT NULL
            )""")
            cur.execute("""CREATE TABLE IF NOT EXISTS engine_packets (
                event_id TEXT PRIMARY KEY, payload BYTEA NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )""")
            cur.execute("""CREATE TABLE IF NOT EXISTS engine_results (
                event_id TEXT PRIMARY KEY REFERENCES engine_packets(event_id),
                packet_digest TEXT NOT NULL, outcome TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )""")
            cur.execute("SELECT value FROM engine_meta WHERE key='career_seed'")
            if cur.fetchone() is None:
                cur.execute("INSERT INTO engine_meta(key,value) VALUES('career_seed',%s)",
                            (secrets.token_bytes(32),))
            cur.execute("INSERT INTO engine_meta(key,value) VALUES('snapshot',%s) ON CONFLICT (key) DO UPDATE SET value=EXCLUDED.value",
                        (SNAPSHOT.encode(),))
        conn.commit()

class PostgresJournal:
    def freeze_once(self, event_id, payload):
        with db() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO engine_packets(event_id,payload) VALUES(%s,%s) ON CONFLICT DO NOTHING",
                            (event_id, payload))
                cur.execute("SELECT payload FROM engine_packets WHERE event_id=%s", (event_id,))
                stored = bytes(cur.fetchone()["payload"])
            conn.commit()
        return stored

    def close_result(self, event_id, packet_digest, outcome):
        with db() as conn:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO engine_results(event_id,packet_digest,outcome)
                               VALUES(%s,%s,%s) ON CONFLICT DO NOTHING""",
                            (event_id, packet_digest, outcome))
                cur.execute("SELECT packet_digest,outcome FROM engine_results WHERE event_id=%s", (event_id,))
                row = cur.fetchone()
                if row["packet_digest"] != packet_digest:
                    raise PacketConflict("result packet digest conflict")
                stored = row["outcome"]
            conn.commit()
        return stored

def seed():
    with db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT value FROM engine_meta WHERE key='career_seed'")
            row = cur.fetchone()
            if not row:
                raise RuntimeError("career seed not initialized")
            return bytes(row["value"])

def seed_fingerprint():
    return hashlib.sha256(seed()).hexdigest()[:16]

def authorized():
    header = request.headers.get("Authorization", "")
    return header.startswith("Bearer ") and secrets.compare_digest(header[7:], API_TOKEN)

@app.get("/health")
def health():
    try:
        initialize()
        with db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
                cur.execute("SELECT COUNT(*) AS n FROM engine_meta WHERE key='career_seed'")
                seeded = cur.fetchone()["n"] == 1
        return jsonify({
            "ready": bool(seeded),
            "schema_version": SCHEMA_VERSION,
            "procedure_version": PROCEDURE_VERSION,
            "snapshot": SNAPSHOT,
            "backend": "postgres",
        }), 200 if seeded else 503
    except Exception:
        return jsonify({"ready": False, "schema_version": SCHEMA_VERSION}), 503

@app.get("/v1/probe")
def probe():
    if not authorized():
        return jsonify({"error": "unauthorized"}), 401
    try:
        initialize()
        journal = PostgresJournal()
        # Probe uses a reserved administrative event outside the career ledger.
        packet = Packet.freeze(
            "runtime-probe-v1", PROCEDURE_VERSION,
            snapshot=SNAPSHOT,
            inputs={"kind": "readiness-probe"},
            modifiers={},
            weights={"ok": 1},
        )
        first = resolve(packet, seed(), journal)
        second = resolve(packet, seed(), journal)
        return jsonify({
            "ready": first == second == "ok",
            "schema_version": SCHEMA_VERSION,
            "procedure_version": PROCEDURE_VERSION,
            "snapshot": SNAPSHOT,
            "seed_fingerprint": seed_fingerprint(),
            "journal_idempotent": first == second,
        })
    except Exception:
        return jsonify({"ready": False, "schema_version": SCHEMA_VERSION}), 503

@app.post("/v1/resolve")
def resolve_event():
    if not authorized():
        return jsonify({"error": "unauthorized"}), 401
    body = request.get_json(force=True)
    try:
        raw = base64.b64decode(body["packet_b64"], validate=True)
        parsed = json.loads(raw)
        packet = Packet.freeze(
            parsed["event_id"], parsed["procedure_version"],
            snapshot=parsed["snapshot"], inputs=parsed["inputs"],
            modifiers=parsed["modifiers"], weights=parsed["weights"],
        )
        if packet.payload != raw:
            return jsonify({"error": "noncanonical packet"}), 409
        outcome = resolve(packet, seed(), PostgresJournal())
        return jsonify({"event_id": packet.event_id, "outcome": outcome})
    except PacketConflict as exc:
        return jsonify({"error": str(exc)}), 409
    except Exception:
        return jsonify({"error": "invalid request"}), 400

initialize()
