#!/usr/bin/env python3
"""Close one week's games from its frozen package and generate every view.

  python scripts/close_week.py WEEK --close [--season YEAR]

Requires the week's frozen package from build_week_inputs.py (for 2013,
.sim_cache/week_NN_inputs.json; for any later season,
.sim_cache/YEAR/week_NN_inputs.json) and a READY check_game_readiness.py.
Each game closes once through the production runner
(runtime.game_runner.run_game); a rerun of this command only replays events
already closed, which the private service returns unchanged. Results are
kept beside the package in week_NN_results.json. Then it writes the public
receipts (full for Jacksonville, compact for everyone else) under
career/YEAR/stats/ and regenerates that season's statbook and standings. It
never writes the weekly prose or advances the private snapshot.

Season isolation: every path comes from runtime.season. The package, every
event ID and every cached result must belong to the requested season, or
nothing is drawn or written; a result cached for another season is never
reused. The season defaults to 2013, the closed season.
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PROTAGONIST = "Jacksonville Jaguars"
GAME_TYPES = ("regular", "postseason", "preseason")


def team_input(data):
    from runtime.kernel import TeamInput
    return TeamInput(**{**data, "active_players": tuple(data["active_players"]),
                        "roster": tuple(data["roster"]),
                        "offensive_call_sheet": tuple(data.get("offensive_call_sheet", ()))})


def encode(value):
    if dataclasses.is_dataclass(value):
        return dataclasses.asdict(value)
    raise TypeError(type(value))


def package_season_errors(package, week, season):
    """The package, and every event in it, must be this season's week."""
    from runtime.season import DEFAULT_SEASON
    errors = [] if package.get("week") == week else ["package is for week %s" % package.get("week")]
    # A 2013 package predates the season key; every other package carries it.
    declared = package.get("season", DEFAULT_SEASON)
    if declared != season:
        errors.append("package is for season %s, not %d" % (declared, season))
    prefix = "%d-week%02d-" % (season, week)
    for game in package.get("games", ()):
        event_id = str(game.get("event_id"))
        if not event_id.startswith(prefix):
            errors.append("event %s is not a %d Week %d event" % (event_id, season, week))
        if game.get("game_type", "regular") not in GAME_TYPES:
            errors.append("event %s has unknown game type %r" % (event_id, game.get("game_type")))
    types = {g.get("game_type", "regular") for g in package.get("games", ())}
    if len(types) > 1:
        errors.append("package mixes game types: " + ", ".join(sorted(types)))
    return errors


def canonical_readiness(season):
    readiness = subprocess.run([sys.executable, str(ROOT / "scripts/check_game_readiness.py"),
                                "--season", str(season)], capture_output=True, text=True)
    if "GAME READINESS: READY" not in readiness.stdout:
        print(readiness.stdout + readiness.stderr)
        return False
    return True


def close_week(week, *, season=None, root=None, close=False, client=None, readiness=None, runner=None):
    """Gate, close and publish one week of `season` (default 2013).

    `root`, `client`, `readiness` and `runner` exist for the isolated-workspace
    test: a workspace other than this checkout is refused unless a client is
    injected, so it can never bind to the private service.
    """
    from runtime.season import DEFAULT_SEASON, season_of_event, season_paths
    from runtime.week_inputs import schedule
    from scripts.check_week_input_exclusivity import check_inputs, controlled_players_from_roster

    season = DEFAULT_SEASON if season is None else season
    paths = season_paths(season, root)
    if paths.root != ROOT and client is None:
        print("WEEK_CLOSE: BLOCKED")
        print("- %s is not this checkout; only the canonical checkout closes events with the "
              "private service" % paths.root)
        return 1
    package_path = paths.inputs_cache(week)
    if not package_path.is_file():
        print("WEEK_INPUTS: BLOCKED")
        print("- no frozen package at %s; run build_week_inputs.py %d --season %d"
              % (package_path.relative_to(paths.root), week, season))
        return 1
    package = json.loads(package_path.read_text(encoding="utf-8"))
    errors = package_season_errors(package, week, season)
    errors += check_inputs(package, controlled_players_from_roster(paths.require("roster")),
                           PROTAGONIST, expected_games=len(schedule(week, season, root)))
    if errors:
        # The frozen package must still pass the weekly gate before any draw.
        print("WEEK_INPUTS: BLOCKED")
        for error in errors:
            print("- " + error)
        return 1
    if not close:
        print("Dry run: %d games in %s; add --close to close them." % (len(package["games"]), package_path.name))
        return 0
    if not (readiness or canonical_readiness)(season):
        return 1

    from runtime.game_runner import run_game
    from runtime.statbook import make_receipt
    runner = runner or run_game

    snapshot = hashlib.sha256((paths.root / "state/05_Current_Season_State.md").read_bytes()).hexdigest()
    if client is None:
        from runtime.private_client import Client
        client = Client(snapshot=snapshot)
    results_path = paths.results_cache(week)
    results = json.loads(results_path.read_text(encoding="utf-8")) if results_path.exists() else {}
    foreign = sorted(e for e in results if season_of_event(e) != season)
    if foreign:
        # A cached result is reused only for its own season's event.
        print("WEEK_CLOSE: BLOCKED")
        print("- %s holds results from another season: %s" % (results_path.name, ", ".join(foreign)))
        return 1
    results_path.parent.mkdir(parents=True, exist_ok=True)
    for game in package["games"]:
        if game["event_id"] not in results:
            result = runner(team_input(game["home_input"]), team_input(game["away_input"]),
                            event_id=game["event_id"], snapshot=snapshot, client=client,
                            venue=game["venue"], game_type=game.get("game_type", "regular"))
            results[game["event_id"]] = json.loads(json.dumps(result, default=encode))
            results_path.write_text(json.dumps(results), encoding="utf-8")
            print("closed %s" % game["event_id"])

    # Postseason and preseason receipts live apart so standings, the
    # regular-season statbook, awards and the band audit stay regular-season
    # only (runtime.postseason).
    game_type = package["games"][0].get("game_type", "regular")
    receipts_dir = paths.receipts_dir(game_type)
    receipts_dir.mkdir(parents=True, exist_ok=True)
    for game in package["games"]:
        detail = "full" if PROTAGONIST in (game["away"], game["home"]) else "compact_stats"
        receipt = make_receipt(results[game["event_id"]], week=week,
                               matchup="%s at %s" % (game["away"], game["home"]), detail=detail,
                               season=season)
        (receipts_dir / game["receipt"]).write_text(
            json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    if game_type != "preseason":
        subprocess.run([sys.executable, str(ROOT / "scripts/render_season_stats.py"), str(season),
                        "--team", PROTAGONIST, "--root", str(paths.root)], check=True)
        subprocess.run([sys.executable, str(ROOT / "scripts/render_standings.py"), str(season),
                        "--root", str(paths.root)], check=True)
    print("%d Week %d closed: %d receipts written. Next: fill the box score with "
          "render_box_score.py --write, write the weekly output and league roundup, close state."
          % (season, week, len(package["games"])))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("week", type=int)
    parser.add_argument("--close", action="store_true", help="actually close the events")
    parser.add_argument("--season", type=int, default=2013, help="season to close (default 2013)")
    args = parser.parse_args()
    return close_week(args.week, season=args.season, close=args.close)


if __name__ == "__main__":
    sys.exit(main())
