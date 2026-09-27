#!/usr/bin/env python3
"""Audited redraw of an injury projection that was generated but never recorded.

  python scripts/recover_injury_projection.py            # dry run: packets and digests
  python scripts/recover_injury_projection.py --close    # draw through the private service

Pasztor's and Mosley's preseason injuries (Entries 22 and 25) were logged with
class and restriction only; the preseason packets were never preserved, so the
original projection cannot be replayed (Entry 46). Each missing projection is
redrawn once from the same injury model every club uses (runtime/injuries.py),
conditioned only on the recorded class and restriction. The packet is fixed in
career/2013/migrations/injury_projection_recovery.json and committed before the
draw; the private service commits its digest and supplies the entropy, as for
any game. The draw mirrors maybe_injury: one uniform picks the severity band,
then randint picks the days, repeated until the recorded restriction holds.
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta
import hashlib
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.game_runner import _entropy_from_ref
from runtime.injuries import SEVERITY
from runtime.packets import canonical

MANIFEST = ROOT / "career/2013/migrations/injury_projection_recovery.json"
PROCEDURE = "injury-projection-recovery-v1"


def model_digest():
    return hashlib.sha256((ROOT / "runtime/injuries.py").read_bytes()).hexdigest()


def build_packet(manifest, entry):
    return {
        "procedure": PROCEDURE, "event_id": entry["event_id"], "snapshot": manifest["snapshot"],
        "source_event": entry["source_event"], "player": entry["player"],
        "injury_date": entry["injury_date"], "injury_class": entry["injury_class"],
        "restriction": entry["restriction"], "min_return_days": entry["min_return_days"],
        "model": {"file": "runtime/injuries.py", "sha256": manifest["model_sha256"],
                  "severity": [list(band) for band in SEVERITY]},
    }


def packet_digest(packet):
    return hashlib.sha256(canonical(packet)).hexdigest()


def draw(entropy, packet):
    """Severity and return days for one packet; no discretion anywhere."""
    rng = random.Random(int.from_bytes(hashlib.sha256(entropy + canonical(packet)).digest(), "big"))
    while True:
        u = rng.random()
        for ceiling, name, low, high in SEVERITY:
            if u < ceiling:
                days = rng.randint(low, high)
                break
        if days >= packet["min_return_days"]:
            return name, days


def resolve(result_ref, packet):
    severity, days = draw(_entropy_from_ref(result_ref), packet)
    back = date.fromisoformat(packet["injury_date"]) + timedelta(days=days)
    return {"result_ref": result_ref, "severity": severity, "return_days": days,
            "reassessment_days": min(max(days // 3, 1), 7), "projected_return": back.isoformat()}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--close", action="store_true", help="draw through the private service")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["model_sha256"] != model_digest():
        print("RECOVERY: BLOCKED\n- runtime/injuries.py differs from the registered model")
        return 1
    packets = [build_packet(manifest, e) for e in manifest["recoveries"]]
    for packet in packets:
        digest = packet_digest(packet)
        registered = manifest["packet_sha256"].get(packet["event_id"])
        print("%s  %s  registered=%s" % (packet["event_id"], digest, registered == digest))
        if args.close and registered != digest:
            print("RECOVERY: BLOCKED\n- packet digest differs from the registered one")
            return 1
    if not args.close:
        return 0
    if manifest.get("results"):
        print("RECOVERY: already drawn; results are in the manifest")
        return 1

    from runtime.private_client import Client
    client = Client(snapshot=manifest["snapshot"])
    if client.current_snapshot() != manifest["snapshot"]:
        print("RECOVERY: BLOCKED\n- private snapshot differs from the registered one")
        return 1
    results = {}
    for packet in packets:
        results[packet["event_id"]] = resolve(client.close_event(packet), packet)
        print(packet["event_id"], json.dumps(results[packet["event_id"]]))
    manifest["results"] = results
    MANIFEST.write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
