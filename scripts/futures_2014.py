#!/usr/bin/env python3
"""February 2014: Jacksonville's reserve/future contracts.

  python scripts/futures_2014.py            # dry run
  python scripts/futures_2014.py --close    # one private draw; write results

Method: career/2014/01_early_offseason/futures_method.json, committed before the draw.
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

METHOD = ROOT / "career/2014/01_early_offseason/futures_method.json"
RESULTS = ROOT / "career/2014/01_early_offseason/futures_results.json"
UNCONTESTED = ("Tyler Bray", "Richard Murphy", "Antwon Blake", "Jerome Long", "Jerrell Jackson")
LET_GO = ("Brandon King", "Will Ta'ufo'ou")


def chance(m):
    """League rails method section 4."""
    if m < 0.8:
        return 0.0
    if m <= 1.0:
        return 0.5 * (m - 0.8) / 0.2
    if m <= 1.25:
        return 0.5 + 0.4 * (m - 1.0) / 0.25
    return 0.9


def resolve(rng):
    u = rng.random()
    p = chance(1.0)
    signed = [{"player": n, "date": "2014-02-03", "basis": "uncontested"} for n in UNCONTESTED]
    smith = {"player": "D'Anthony Smith", "m": 1.0, "chance": p, "draw": round(u, 4), "jacksonville": u < p}
    if smith["jacksonville"]:
        signed.append({"player": "D'Anthony Smith", "date": "2014-02-05", "basis": "market draw won"})
    return {"signed": signed, "smith": smith, "let_go": list(LET_GO),
            "lost": [] if smith["jacksonville"] else [{"player": "D'Anthony Smith", "club": "Seattle Seahawks",
                                                       "date": "2014-02-05", "move": "reserve/future contract"}]}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--close", action="store_true")
    parser.add_argument("--entry", default="")
    args = parser.parse_args()
    m = json.loads(METHOD.read_text(encoding="utf-8"))
    print("Smith chance %.2f" % chance(1.0))
    if not args.close:
        return 0
    if RESULTS.exists():
        print("FUTURES: already drawn")
        return 1
    from runtime.game_runner import _entropy_from_ref
    from runtime.private_client import Client
    client = Client()
    pkt = {"procedure": m["procedure"], "event_id": m["event_id"], "snapshot": client.current_snapshot(),
           "method_sha256": digest(METHOD), "code_sha256": digest(Path(__file__).resolve())}
    ref = client.close_event(pkt)
    rng = random.Random(int.from_bytes(hashlib.sha256(_entropy_from_ref(ref) + canonical(pkt)).digest(), "big"))
    res = resolve(rng)
    RESULTS.write_text(json.dumps({**pkt, "ledger_entry": args.entry, "result_ref": ref,
                                   "packet_sha256": hashlib.sha256(canonical(pkt)).hexdigest(), **res},
                                  indent=1) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
