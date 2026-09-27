#!/usr/bin/env python3
"""Close one week's games from its frozen package and generate every view.

  python scripts/close_week.py WEEK --close

Requires .sim_cache/week_NN_inputs.json from build_week_inputs.py and a READY
check_game_readiness.py. Each game closes once through the production runner
(runtime.game_runner.run_game); a rerun of this command only replays events
already closed, which the private service returns unchanged. Results are
kept in .sim_cache/week_NN_results.json. Then it writes the public receipts
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
    args = parser.parse_args()

    package_path = ROOT / ".sim_cache" / ("week_%02d_inputs.json" % args.week)
    package = json.loads(package_path.read_text(encoding="utf-8"))
    from runtime.week_inputs import schedule
    from scripts.check_week_input_exclusivity import check_inputs, controlled_players_from_roster
    errors = [] if package.get("week") == args.week else ["package is for week %s" % package.get("week")]
    errors += check_inputs(package, controlled_players_from_roster(ROOT / "career/2013/roster.md"),
                           PROTAGONIST, expected_games=len(schedule(args.week)))
    if errors:
        # The frozen package must still pass the weekly gate before any draw.
        print("WEEK_INPUTS: BLOCKED")
        for error in errors:
            print("- " + error)
        return 1
    if not args.close:
        print("Dry run: %d games in %s; add --close to close them." % (len(package["games"]), package_path.name))
        return 0
    readiness = subprocess.run([sys.executable, str(ROOT / "scripts/check_game_readiness.py")],
                               capture_output=True, text=True)
    if "GAME READINESS: READY" not in readiness.stdout:
        print(readiness.stdout + readiness.stderr)
        return 1

    from runtime.game_runner import run_game
    from runtime.private_client import Client
    from runtime.statbook import make_receipt

    snapshot = hashlib.sha256((ROOT / "state/05_Current_Season_State.md").read_bytes()).hexdigest()
    client = Client(snapshot=snapshot)
    results_path = ROOT / ".sim_cache" / ("week_%02d_results.json" % args.week)
    results = json.loads(results_path.read_text(encoding="utf-8")) if results_path.exists() else {}
    for game in package["games"]:
        if game["event_id"] not in results:
            result = run_game(team_input(game["home_input"]), team_input(game["away_input"]),
                              event_id=game["event_id"], snapshot=snapshot, client=client,
                              venue=game["venue"])
            results[game["event_id"]] = json.loads(json.dumps(result, default=encode))
            results_path.write_text(json.dumps(results), encoding="utf-8")
            print("closed %s" % game["event_id"])

    receipts_dir = ROOT / "career/2013/stats/game_receipts"
    for game in package["games"]:
        detail = "full" if PROTAGONIST in (game["away"], game["home"]) else "compact_stats"
        receipt = make_receipt(results[game["event_id"]], week=args.week,
                               matchup="%s at %s" % (game["away"], game["home"]), detail=detail)
        (receipts_dir / game["receipt"]).write_text(
            json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "scripts/render_season_stats.py"), "2013",
                    "--team", PROTAGONIST], check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts/render_standings.py"), "2013"], check=True)
    print("Week %d closed: %d receipts written. Next: fill the box score with "
          "render_box_score.py --write, write the weekly output and league roundup, close state."
          % (args.week, len(package["games"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
