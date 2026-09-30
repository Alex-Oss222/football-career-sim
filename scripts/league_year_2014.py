#!/usr/bin/env python3
"""March 11, 2014: the league-year market draws and Arizona's package I answer.

  python scripts/league_year_2014.py            # dry run: index and chance per draw
  python scripts/league_year_2014.py --close    # one private packet; write results

Method: career/2014/early_offseason/league_year_method.json, committed before the draw.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.packets import canonical

METHOD = ROOT / "career/2014/early_offseason/league_year_method.json"
RESULTS = ROOT / "career/2014/early_offseason/league_year_results.json"


def chance(m):
    """League rails method section 4."""
    if m < 0.8:
        return 0.0
    if m <= 1.0:
        return 0.5 * (m - 0.8) / 0.2
    if m <= 1.25:
        return 0.5 + 0.4 * (m - 1.0) / 0.25
    return 0.9


def index(d):
    if d.get("uncontested"):
        return None
    if d.get("trade"):
        return d["sent_points"] / d["asked_points"]
    apy = d["jax_apy"] / d["real_apy"]
    if not d.get("real_gtd"):
        return apy
    return 0.5 * apy + 0.5 * d["jax_gtd"] / d["real_gtd"]


def probability(d):
    m = index(d)
    return (0.9 if m is None else chance(m)), m


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--close", action="store_true")
    parser.add_argument("--entry", default="")
    args = parser.parse_args()
    method = json.loads(METHOD.read_text(encoding="utf-8"))
    for d in method["draws"]:
        p, m = probability(d)
        print("%-12s m=%s chance=%.4f" % (d["key"], "uncontested" if m is None else "%.4f" % m, p))
    if not args.close:
        return 0
    if RESULTS.exists():
        print("LEAGUE YEAR: already drawn")
        return 1
    from runtime.game_runner import _entropy_from_ref
    from runtime.private_client import Client
    client = Client()
    pkt = {"procedure": method["procedure"], "event_id": method["event_id"], "snapshot": client.current_snapshot(),
           "method_sha256": digest(METHOD), "code_sha256": digest(Path(__file__).resolve())}
    ref = client.close_event(pkt)
    entropy = _entropy_from_ref(ref) + canonical(pkt)
    out = []
    for d in method["draws"]:
        p, m = probability(d)
        rng = random.Random(int.from_bytes(hashlib.sha256(entropy + d["key"].encode()).digest(), "big"))
        u = rng.random()
        out.append({"key": d["key"], "player": d["player"], "date": d["date"],
                    "m": None if m is None else round(m, 4), "chance": round(p, 4),
                    "draw": round(u, 4), "jacksonville": u < p})
    RESULTS.write_text(json.dumps({**pkt, "ledger_entry": args.entry, "result_ref": ref,
                                   "packet_sha256": hashlib.sha256(canonical(pkt)).hexdigest(),
                                   "results": out}, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
