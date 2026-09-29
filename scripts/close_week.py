#!/usr/bin/env python3
"""Close one week's games from its frozen package and generate every view.

  python scripts/close_week.py WEEK --season YEAR --close

Requires .sim_cache/YEAR/week_NN_inputs.json from build_week_inputs.py and a READY
check_game_readiness.py. Each game closes once through the production runner
(runtime.game_runner.run_game); a rerun of this command only replays events
already closed, which the private service returns unchanged. Results are
kept in .sim_cache/YEAR/week_NN_results.json. Then it writes the public receipts
(full for Jacksonville, compact for everyone else) and regenerates the
statbook and standings. It never writes the weekly prose or advances the
private snapshot.
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

from runtime.seasons import SeasonPaths, require_game_release, require_receipt_season

PROTAGONIST = "Jacksonville Jaguars"


def team_input(data):
    from runtime.kernel import TeamInput
    return TeamInput(**{**data, "active_players": tuple(data["active_players"]),
                        "roster": tuple(data["roster"]),
                        "offensive_call_sheet": tuple(data.get("offensive_call_sheet", ()))})


def encode(value):
    if dataclasses.is_dataclass(value):
        return dataclasses.asdict(value)
    raise TypeError(type(value))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("week", type=int)
    parser.add_argument("--close", action="store_true", help="actually close the events")
    parser.add_argument("--season", type=int, required=True)
    args = parser.parse_args()
    paths = SeasonPaths(args.season, ROOT)
    try:
        require_game_release(args.season, ROOT)
    except ValueError as exc:
        print("WEEK_INPUTS: BLOCKED\n- " + str(exc))
        return 1

    package_path = paths.cache(args.week, "inputs")
    package = json.loads(package_path.read_text(encoding="utf-8"))
    if package.get("season") != args.season:
        raise ValueError("Frozen package belongs to a different season")
    require_receipt_season(package["games"], args.season)
    from runtime.week_inputs import schedule
    from scripts.check_week_input_exclusivity import check_inputs, controlled_players_from_roster
    errors = [] if package.get("week") == args.week else ["package is for week %s" % package.get("week")]
    errors += check_inputs(package, controlled_players_from_roster(paths.roster),
                           PROTAGONIST, expected_games=len(schedule(args.week, args.season)))
    if errors:
        # The frozen package must still pass the weekly gate before any draw.
        print("WEEK_INPUTS: BLOCKED")
        for error in errors:
            print("- " + error)
        return 1
    if not args.close:
        print("Dry run: %d games in %s; add --close to close them." % (len(package["games"]), package_path.name))
        return 0
    readiness = subprocess.run([sys.executable, str(ROOT / "scripts/check_game_readiness.py"), "--season", str(args.season)],
                               capture_output=True, text=True)
    if "GAME READINESS: READY" not in readiness.stdout:
        print(readiness.stdout + readiness.stderr)
        return 1

    from runtime.game_runner import run_game
    from runtime.private_client import Client
    from runtime.statbook import make_receipt

    snapshot = hashlib.sha256((ROOT / "state/05_Current_Season_State.md").read_bytes()).hexdigest()
    client = Client(snapshot=snapshot)
    results_path = paths.cache(args.week, "results")
    results = json.loads(results_path.read_text(encoding="utf-8")) if results_path.exists() else {}
    for game in package["games"]:
        if game["event_id"] not in results:
            result = run_game(team_input(game["home_input"]), team_input(game["away_input"]),
                              event_id=game["event_id"], snapshot=snapshot, client=client,
                              venue=game["venue"], game_type=game.get("game_type", "regular"))
            results[game["event_id"]] = json.loads(json.dumps(result, default=encode))
            results_path.write_text(json.dumps(results), encoding="utf-8")
            print("closed %s" % game["event_id"])

    # Postseason receipts live apart so standings, the regular-season statbook,
    # awards and the band audit stay regular-season only (runtime.postseason).
    postseason_week = any(g.get("game_type") == "postseason" for g in package["games"])
    receipts_dir = paths.postseason_receipts if postseason_week else paths.receipts
    receipts_dir.mkdir(parents=True, exist_ok=True)
    for game in package["games"]:
        detail = "full" if PROTAGONIST in (game["away"], game["home"]) else "compact_stats"
        receipt = make_receipt(results[game["event_id"]], week=args.week,
                               matchup="%s at %s" % (game["away"], game["home"]), detail=detail)
        if args.season != 2013:
            receipt["season"] = args.season
        (receipts_dir / game["receipt"]).write_text(
            json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "scripts/render_season_stats.py"), str(args.season),
                    "--team", PROTAGONIST], check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts/render_standings.py"), str(args.season)], check=True)
    print("Week %d closed: %d receipts written. Next: fill the box score with "
          "render_box_score.py --write, write the weekly output and league roundup, close state."
          % (args.week, len(package["games"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
