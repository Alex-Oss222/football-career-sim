#!/usr/bin/env python3
"""Super Bowl XLVIII MVP from the closed Super Bowl receipt.

  python scripts/super_bowl_mvp.py            # dry run: the shortlist
  python scripts/super_bowl_mvp.py --close    # draw and record

Method: career/2013/awards/super_bowl_mvp_method.json, fixed before the draw.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.packets import canonical
from scripts.league_awards import method as weekly_method, pick, score

AWARDS = ROOT / "career/2013/awards"
METHOD = AWARDS / "super_bowl_mvp_method.json"
RESULT = AWARDS / "super_bowl_mvp.json"
RECEIPT = ROOT / "career/2013/stats/postseason_receipts/week_21_minnesota_vikings_at_buffalo_bills.json"


def shortlist(m):
    weekly = weekly_method()
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    score_of = receipt["final_score"]
    winner = max(score_of, key=score_of.get)
    rows = []
    for name, player in receipt["team_stats"][winner]["players"].items():
        total = sum(score(category, player, weekly) for category in ("offense", "defense", "special_teams"))
        rows.append({"player": name, "team": winner, "position": player.get("position"), "score": round(total, 2)})
    rows.sort(key=lambda r: (-r["score"], r["player"]))
    return receipt, rows[:m["shortlist_size"]]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--close", action="store_true")
    parser.add_argument("--entry", default="")
    args = parser.parse_args()
    m = json.loads(METHOD.read_text(encoding="utf-8"))
    receipt, rows = shortlist(m)
    for r in rows:
        print("%s (%s, %s) %s" % (r["player"], r["team"], r["position"], r["score"]))
    if not args.close:
        return 0
    if RESULT.exists():
        print("SUPER BOWL MVP: already drawn")
        return 1
    from runtime.private_client import Client
    client = Client()
    snapshot = client.current_snapshot()
    pkt = {"procedure": m["procedure"], "event_id": "2013-honours-super-bowl-mvp-%s" % m["procedure_tag"],
           "snapshot": snapshot, "award": "Super Bowl XLVIII MVP", "game": receipt["event_id"],
           "shortlist": rows, "panel_weights": m["panel_weights"][:len(rows)],
           "method_sha256": hashlib.sha256(METHOD.read_bytes()).hexdigest(),
           "receipt_sha256": hashlib.sha256(RECEIPT.read_bytes()).hexdigest()}
    ref = client.close_event(pkt)
    result = {"procedure": m["procedure"], "ledger_entry": args.entry, "snapshot": snapshot,
              "event_id": pkt["event_id"], "packet_sha256": hashlib.sha256(canonical(pkt)).hexdigest(),
              "result_ref": ref, "method_sha256": pkt["method_sha256"], "receipt_sha256": pkt["receipt_sha256"],
              "shortlist": rows, "winner_index": pick(ref, pkt)}
    RESULT.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    winner = rows[result["winner_index"]]
    print("MVP: %s (%s)" % (winner["player"], winner["team"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
