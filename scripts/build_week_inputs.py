#!/usr/bin/env python3
"""Build, freeze and gate one week's TeamInput package.

  python scripts/build_week_inputs.py WEEK --season YEAR

Reads the week's Jacksonville call sheet from
career/YEAR/regular_season/week_NN_*/call_sheet.json and every closed receipt
for availability, builds the package and runs the weekly exclusivity and
game-day gate with the scheduled game count. The package is written to
.sim_cache/YEAR/week_NN_inputs.json only when the gate passes; any other exit
leaves no package at that path. Nothing is drawn and no event is closed.
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
from runtime.seasons import SeasonPaths, require_game_release
from scripts.check_week_input_exclusivity import check_inputs, controlled_players_from_roster
from scripts.render_season_stats import load_receipts

# Document 7 section 2.2: without contemporaneous regular-season evidence
# every club carries the Average anchor, flagged low-confidence.
AVERAGE_ANCHORS = {"offense_anchor": 2.0, "defense_anchor": 2.0, "special_teams_anchor": 2.0}


def call_sheet_path(week, season=2013):
    matches = sorted(SeasonPaths(season, ROOT).regular_season.glob("week_%02d_*/call_sheet.json" % week))
    matches += sorted(SeasonPaths(season, ROOT).postseason.glob("week_%02d_*/call_sheet.json" % week))
    return matches[0] if matches else None


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("week", type=int)
    parser.add_argument("--season", type=int, required=True)
    args = parser.parse_args()
    paths = SeasonPaths(args.season, ROOT)
    try:
        require_game_release(args.season, ROOT)
    except ValueError as exc:
        print("WEEK_INPUTS: BLOCKED\n- " + str(exc))
        return 1

    out = paths.cache(args.week, "inputs")
    # Only a package that passed the gate may sit at the frozen path.
    out.unlink(missing_ok=True)
    jacksonville_plays = any("Jacksonville Jaguars" in (g["away"], g["home"]) for g in schedule(args.week, args.season))
    sheet_path = call_sheet_path(args.week, args.season)
    if sheet_path is None and not jacksonville_plays:
        call_sheet = []  # bye week: no Jacksonville game, so no call sheet
    elif sheet_path is None:
        print("WEEK_INPUTS: BLOCKED")
        print("- No Jacksonville call sheet for Week %d: Stone's weekly plan must be frozen as "
              "career/%d/regular_season/week_%02d_<away>_at_<home>/call_sheet.json before the draw."
              % (args.week, args.season, args.week))
        return 1
    else:
        call_sheet = json.loads(sheet_path.read_text(encoding="utf-8"))["offensive_call_sheet"]
    receipts = [r for r in load_receipts(paths.receipts) if int(r["week"]) < args.week]
    # Postseason rounds also carry injuries from the earlier playoff rounds.
    receipts += [r for r in load_receipts(paths.postseason_receipts) if int(r["week"]) < args.week]
    try:
        package = build_package(args.week, receipts, call_sheet, AVERAGE_ANCHORS, args.season)
    except ValueError as exc:
        print("WEEK_INPUTS: BLOCKED")
        print("- %s" % exc)
        return 1

    out.parent.mkdir(parents=True, exist_ok=True)
    errors = check_inputs(package, controlled_players_from_roster(paths.roster),
                          "Jacksonville Jaguars", expected_games=len(schedule(args.week, args.season)))
    if errors:
        print("WEEK_INPUTS: BLOCKED")
        for error in errors:
            print("- " + error)
        return 1
    out.write_text(json.dumps(package, indent=1), encoding="utf-8")
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    unavailable = sum(1 for g in package["games"] for side in ("away_input", "home_input")
                      for p in g[side]["roster"] if not p["available"])
    print("WEEK_INPUTS: READY  week %d, %d games, %d players unavailable, sha256 %s"
          % (args.week, len(package["games"]), unavailable, digest))
    print("Frozen package: %s" % out.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
