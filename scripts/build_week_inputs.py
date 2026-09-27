#!/usr/bin/env python3
"""Build, freeze and gate one week's TeamInput package.

  python scripts/build_week_inputs.py WEEK

Reads the week's Jacksonville call sheet from
career/2013/regular_season/week_NN_*/call_sheet.json, every closed receipt
for availability, and writes .sim_cache/week_NN_inputs.json. It then runs the
weekly exclusivity and game-day gate with the scheduled game count. Nothing
is drawn and no event is closed.
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

from runtime.week_inputs import build_package, schedule
from scripts.check_week_input_exclusivity import check_inputs, controlled_players_from_roster
from scripts.render_season_stats import load_receipts

# Document 7 section 2.2: without contemporaneous regular-season evidence
# every club carries the Average anchor, flagged low-confidence.
AVERAGE_ANCHORS = {"offense_anchor": 2.0, "defense_anchor": 2.0, "special_teams_anchor": 2.0}


def call_sheet_path(week):
    matches = sorted((ROOT / "career/2013/regular_season").glob("week_%02d_*/call_sheet.json" % week))
    return matches[0] if matches else None


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("week", type=int)
    args = parser.parse_args()

    sheet_path = call_sheet_path(args.week)
    if sheet_path is None:
        print("WEEK_INPUTS: BLOCKED")
        print("- No Jacksonville call sheet for Week %d: Stone's weekly plan must be frozen as "
              "career/2013/regular_season/week_%02d_<away>_at_<home>/call_sheet.json before the draw."
              % (args.week, args.week))
        return 1
    call_sheet = json.loads(sheet_path.read_text(encoding="utf-8"))["offensive_call_sheet"]
    receipts = [r for r in load_receipts(ROOT / "career/2013/stats/game_receipts") if int(r["week"]) < args.week]
    package = build_package(args.week, receipts, call_sheet, AVERAGE_ANCHORS)

    out = ROOT / ".sim_cache" / ("week_%02d_inputs.json" % args.week)
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(package, indent=1), encoding="utf-8")
    errors = check_inputs(package, controlled_players_from_roster(ROOT / "career/2013/roster.md"),
                          "Jacksonville Jaguars", expected_games=len(schedule(args.week)))
    if errors:
        print("WEEK_INPUTS: BLOCKED")
        for error in errors:
            print("- " + error)
        return 1
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    unavailable = sum(1 for g in package["games"] for side in ("away_input", "home_input")
                      for p in g[side]["roster"] if not p["available"])
    print("WEEK_INPUTS: READY  week %d, %d games, %d players unavailable, sha256 %s"
          % (args.week, len(package["games"]), unavailable, digest))
    print("Frozen package: %s" % out.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
