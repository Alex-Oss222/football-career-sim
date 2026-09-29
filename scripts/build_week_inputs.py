#!/usr/bin/env python3
"""Build, freeze and gate one week's TeamInput package.

  python scripts/build_week_inputs.py WEEK [--season YEAR]

Reads the week's Jacksonville call sheet from
career/YEAR/{regular_season,postseason,preseason}/week_NN_*/call_sheet.json
and every closed receipt of that season for availability, builds the package
and runs the weekly exclusivity and game-day gate with the scheduled game
count. The package is written to the season's cache
(.sim_cache/week_NN_inputs.json for 2013, .sim_cache/YEAR/week_NN_inputs.json
otherwise) only when the gate passes; any other exit leaves no package at
that path. Nothing is drawn and no event is closed.

Every input is the requested season's own (runtime.season). A season whose
schedule, depth library, roster or depth chart does not exist is BLOCKED
with the missing prerequisite named; nothing falls back to 2013. Receipts of
an earlier season are not read, so injuries open at that season's end do
not carry over: that carry-over is a separate policy decision.
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

from runtime.season import DEFAULT_SEASON, season_paths
from runtime.week_inputs import build_package, schedule
from scripts.check_week_input_exclusivity import check_inputs, controlled_players_from_roster
from scripts.render_season_stats import load_receipts

# Document 7 section 2.2: without contemporaneous regular-season evidence
# every club carries the Average anchor, flagged low-confidence.
AVERAGE_ANCHORS = {"offense_anchor": 2.0, "defense_anchor": 2.0, "special_teams_anchor": 2.0}


def call_sheet_path(week, season=DEFAULT_SEASON, root=None):
    paths = season_paths(season, root)
    matches = []
    for game_type in ("regular", "postseason", "preseason"):
        matches += sorted(paths.phase_dir(game_type).glob("week_%02d_*/call_sheet.json" % week))
    return matches[0] if matches else None


def build(week, season=DEFAULT_SEASON, root=None):
    paths = season_paths(season, root)
    out = paths.inputs_cache(week)
    # Only a package that passed the gate may sit at the frozen path.
    out.unlink(missing_ok=True)
    try:
        games = schedule(week, season, root)
    except ValueError as exc:
        print("WEEK_INPUTS: BLOCKED")
        print("- %s" % exc)
        return 1
    jacksonville_plays = any("Jacksonville Jaguars" in (g["away"], g["home"]) for g in games)
    sheet_path = call_sheet_path(week, season, root)
    if sheet_path is None and not jacksonville_plays:
        call_sheet = []  # bye week: no Jacksonville game, so no call sheet
    elif sheet_path is None:
        print("WEEK_INPUTS: BLOCKED")
        print("- No Jacksonville call sheet for Week %d: Stone's weekly plan must be frozen as "
              "career/%d/regular_season/week_%02d_<away>_at_<home>/call_sheet.json before the draw."
              % (week, season, week))
        return 1
    else:
        call_sheet = json.loads(sheet_path.read_text(encoding="utf-8"))["offensive_call_sheet"]
    receipts = [r for r in load_receipts(paths.receipts_dir("regular")) if int(r["week"]) < week]
    # Postseason rounds also carry injuries from the earlier playoff rounds.
    receipts += [r for r in load_receipts(paths.receipts_dir("postseason")) if int(r["week"]) < week]
    try:
        package = build_package(week, receipts, call_sheet, AVERAGE_ANCHORS, season, root)
        controlled = controlled_players_from_roster(paths.require("roster"))
    except ValueError as exc:
        print("WEEK_INPUTS: BLOCKED")
        print("- %s" % exc)
        return 1

    out.parent.mkdir(parents=True, exist_ok=True)
    errors = check_inputs(package, controlled, "Jacksonville Jaguars", expected_games=len(games))
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
          % (week, len(package["games"]), unavailable, digest))
    print("Frozen package: %s" % out.relative_to(paths.root))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("week", type=int)
    parser.add_argument("--season", type=int, default=DEFAULT_SEASON, help="season to build (default 2013)")
    args = parser.parse_args()
    return build(args.week, args.season)


if __name__ == "__main__":
    sys.exit(main())
