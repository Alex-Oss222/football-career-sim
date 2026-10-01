#!/usr/bin/env python3
"""Close one Jacksonville preseason game through the production runner.

  python scripts/close_preseason_game.py N --season YEAR            (dry run: build and gate)
  python scripts/close_preseason_game.py N --season YEAR --close
  python scripts/close_preseason_game.py N --season YEAR --close --continue ANSWER.json

Mirrors scripts/close_week.py for one dated preseason fixture
(career/YEAR/04_Training_Camp_and_Preseason/Preseason_Games/fixtures.json). Jacksonville's TeamInput is
built from the current roster, the game's frozen depth chart and
Game_0N/call_sheet.json; the opponent's from Game_0N/opponent_roster.json
(runtime/preseason.py documents both files). The two-club package is frozen
to .sim_cache/YEAR/preseason_0N_inputs.json, gated by the TeamInput
exclusivity check, and closed exactly once through the private Engine State
service with the fixture's own event id, Jacksonville user controlled (kernel
2014.4 E2). A consequential Jacksonville removal writes
Game_0N/paused_game.json and exits 2; Stone answers {"choices": {...}} and
reruns with --continue ANSWER.json, which reuses the frozen package so the
same packet closes through the same event reference.

After closure the full receipt is preserved under the preseason receipt
directory, the box-score block in Game_0N/output.md is filled (season
gamebook) and the preseason stat views are rendered. It never writes under
regular_season/ or the standings, never advances the private snapshot, and
refuses to close an event whose receipt already exists.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.rules import PRESEASON, active_limit
from runtime.seasons import SeasonPaths, require_game_release, require_receipt_season
from scripts.close_week import (PROTAGONIST, as_json, continuation_decisions, load_answer, read_paused,
                                team_input, write_paused)

PAUSED = 2
MARKER = "<!-- box-score event=%s team=%s -->\n<!-- /box-score -->\n"


def controlled_team_id(game):
    side = "home_input" if game["home"] == PROTAGONIST else "away_input"
    return game[side]["team_id"]


def the_game(package):
    games = package.get("games") or []
    if len(games) != 1 or games[0].get("game_type") != PRESEASON or PROTAGONIST not in (games[0]["away"], games[0]["home"]):
        raise ValueError("a preseason package holds exactly one Jacksonville preseason game")
    return games[0]


def gate_errors(package, paths, number):
    from scripts.check_week_input_exclusivity import check_inputs, controlled_players_from_roster
    errors = []
    if package.get("season") != paths.year:
        errors.append("frozen package belongs to season %s" % package.get("season"))
    if package.get("preseason_game") != number:
        errors.append("frozen package is for preseason game %s" % package.get("preseason_game"))
    try:
        game = the_game(package)
        require_receipt_season([game], paths.year)
        if game["event_id"] != paths.preseason_game(number)["game_id"]:
            errors.append("package event id differs from the fixture")
    except (ValueError, KeyError) as exc:
        return errors + [str(exc)]
    errors += check_inputs(package, controlled_players_from_roster(paths.roster), PROTAGONIST,
                           expected_games=1, active_limit=active_limit(PRESEASON))
    return errors


def describe_pause(record, record_path, number, season):
    pause = record["pause"]
    lines = ["PRESEASON GAME %d PAUSED: %s, drive %s, %s %s, score %s"
             % (number, record["matchup"], pause.get("drive"), pause.get("period"), pause.get("clock"),
                json.dumps(pause.get("score"), sort_keys=True))]
    for injury in pause.get("injuries", []):
        lines.append("- removed: %s (%s; %s, %s, restriction %s)"
                     % (injury.get("player"), injury.get("team"), injury.get("injury_class"),
                        injury.get("severity"), injury.get("restriction")))
    for decision in pause.get("decisions", []):
        lines.append("- replace %s (%s; %s): eligible %s; depth default %s"
                     % (decision["slot"], decision.get("group"), decision.get("reason"),
                        ", ".join(decision["eligible"]), decision.get("default")))
    lines.append("- continuation token %s... (paused record: %s)" % (pause["continuation_token"][:16], record_path))
    lines.append("Answer with a JSON file {\"choices\": {%s}} and rerun: "
                 "python scripts/close_preseason_game.py %d --season %d --close --continue ANSWER.json"
                 % (", ".join('"%s": "<replacement>"' % d["slot"] for d in pause.get("decisions", [])), number, season))
    return "\n".join(lines)


def close_game(package, paths, snapshot, client, results_path, answer=None, run=None):
    """Close the one event, Jacksonville user controlled. Returns (result or None, paused record or None)."""
    if run is None:
        from runtime.game_runner import run_game as run
    game = the_game(package)
    number = package["preseason_game"]
    results = json.loads(results_path.read_text(encoding="utf-8")) if results_path.exists() else {}
    if game["event_id"] in results:
        raise ValueError("preseason game %d (%s) is already closed; a preseason event closes once"
                         % (number, game["event_id"]))
    record_path = paths.paused_game(number, preseason=True)
    record = read_paused(record_path, game["event_id"])
    if record is not None and record.get("status") == "closed":
        raise ValueError("preseason game %d (%s) is already closed; a preseason event closes once"
                         % (number, game["event_id"]))
    decisions = continuation_decisions(record, answer)
    result = run(team_input(game["home_input"]), team_input(game["away_input"]),
                 event_id=game["event_id"], snapshot=snapshot, client=client,
                 venue=game["venue"], game_type=PRESEASON, game_date=game["date"],
                 management_mode="user_controlled", controlled_team=controlled_team_id(game),
                 continuation={"decisions": decisions} if decisions else None)
    result = as_json(result)
    if not result.get("terminated"):
        return None, write_paused(record_path, package, game, result, decisions)
    results[game["event_id"]] = result
    results_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.write_text(json.dumps(results), encoding="utf-8")
    if record is not None:
        closed = {k: record[k] for k in ("season", "week", "event_id", "matchup")}
        closed.update({"status": "closed", "decisions": decisions, "pauses": result.get("pauses", [])})
        record_path.write_text(json.dumps(closed, sort_keys=True, indent=1) + "\n", encoding="utf-8")
    print("closed %s" % game["event_id"])
    return result, None


def write_receipt(package, paths, result):
    """The full public receipt, in the preseason receipt directory only."""
    from runtime.statbook import make_receipt
    game = the_game(package)
    receipt = make_receipt(result, week=package["preseason_game"],
                           matchup="%s at %s" % (game["away"], game["home"]), detail="full")
    receipt["season"] = paths.year
    receipt["preseason_game"] = package["preseason_game"]
    receipt["date"] = game["date"]
    receipt["game_type"] = PRESEASON
    # Background players who entered with no verified birth date (runtime.player_bios).
    from runtime.player_bios import unverified_ages
    unverified = unverified_ages(game.get("player_ages"))
    if unverified:
        receipt["age_unverified"] = unverified
    path = paths.preseason_receipts / game["receipt"]
    if path.exists():
        raise ValueError("receipt already exists: %s" % path.relative_to(paths.root))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return path


def fill_output(package, paths):
    """Place the box-score block in Game_0N/output.md when that file exists, and render it."""
    from scripts.render_box_score import fill
    game = the_game(package)
    output = paths.preseason_folder(package["preseason_game"]) / "output.md"
    if not output.exists():
        return None
    text = output.read_text(encoding="utf-8")
    marker = "<!-- box-score event=%s team=%s -->" % (game["event_id"], PROTAGONIST)
    if marker not in text:
        text = text.rstrip("\n") + "\n\n" + MARKER % (game["event_id"], PROTAGONIST)
    output.write_text(fill(text, paths.preseason_receipts, paths.year), encoding="utf-8")
    return output


def render_stats(paths):
    from scripts.render_preseason_stats import write_views
    return write_views(paths)


def finish(package, paths, result):
    """Receipt, box score and preseason stat views; nothing regular-season."""
    receipt_path = write_receipt(package, paths, result)
    output = fill_output(package, paths)
    views = render_stats(paths)
    return receipt_path, output, views


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("game", type=int, help="preseason game number (1-4)")
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--close", action="store_true", help="actually close the event")
    parser.add_argument("--continue", dest="answer", metavar="ANSWER.json",
                        help="Stone's substitution answer for a paused game (reuses the frozen package)")
    args = parser.parse_args()
    paths = SeasonPaths(args.season, ROOT)
    try:
        require_game_release(args.season, ROOT, preseason=args.game)
    except ValueError as exc:
        print("PRESEASON_INPUTS: BLOCKED\n- " + str(exc))
        return 1
    if args.season == 2013:
        print("PRESEASON_INPUTS: BLOCKED\n- the 2013 preseason is closed canon (ledger Entries 20-25)")
        return 1

    package_path = paths.preseason_cache(args.game, "inputs")
    receipt_dir = paths.preseason_receipts
    try:
        fixture = paths.preseason_game(args.game)
        existing = [p for p in receipt_dir.glob("*.json")
                    if json.loads(p.read_text(encoding="utf-8")).get("event_id") == fixture["game_id"]]
        if existing:
            print("PRESEASON GAME %d ALREADY CLOSED: receipt %s" % (args.game, existing[0].relative_to(ROOT)))
            return 1
        if args.answer:
            if not package_path.exists():
                print("PRESEASON_INPUTS: BLOCKED\n- --continue needs the frozen package %s from the paused run"
                      % package_path.relative_to(ROOT))
                return 1
            package = json.loads(package_path.read_text(encoding="utf-8"))
        else:
            from runtime.preseason import build_package
            from scripts.render_season_stats import load_receipts
            package_path.unlink(missing_ok=True)
            package = build_package(paths, args.game, load_receipts(receipt_dir) if receipt_dir.exists() else [])
        errors = gate_errors(package, paths, args.game)
    except (ValueError, KeyError, FileNotFoundError) as exc:
        errors = [str(exc)]
    if errors:
        print("PRESEASON_INPUTS: BLOCKED")
        for error in errors:
            print("- " + error)
        return 1
    if not args.answer:
        package_path.parent.mkdir(parents=True, exist_ok=True)
        package_path.write_text(json.dumps(package, indent=1), encoding="utf-8")
    digest = hashlib.sha256(package_path.read_bytes()).hexdigest()
    game = the_game(package)
    if not args.close:
        print("PRESEASON_INPUTS: READY  game %d, %s at %s, %s; sha256 %s\nDry run: add --close to close it."
              % (args.game, game["away"], game["home"], game["date"], digest))
        return 0
    answer = load_answer(args.answer) if args.answer else None
    readiness = subprocess.run([sys.executable, str(ROOT / "scripts/check_game_readiness.py"), "--season", str(args.season),
                                "--preseason", str(args.game)],
                               capture_output=True, text=True)
    if "GAME READINESS: READY" not in readiness.stdout:
        print(readiness.stdout + readiness.stderr)
        return 1

    from runtime.private_client import Client
    snapshot = hashlib.sha256((ROOT / "state/05_Current_Season_State.md").read_bytes()).hexdigest()
    client = Client(snapshot=snapshot)
    try:
        result, paused = close_game(package, paths, snapshot, client, paths.preseason_cache(args.game, "results"), answer)
    except ValueError as exc:
        print("PRESEASON CLOSE REFUSED: " + str(exc))
        return 1
    if paused is not None:
        print(describe_pause(paused, paths.paused_game(args.game, preseason=True), args.game, args.season))
        return PAUSED
    receipt_path, output, views = finish(package, paths, result)
    print("Preseason game %d closed: receipt %s; box score %s; stat views %s. Next: write the game report "
          "(preseason output template), reconcile injuries/roles/state, close the ledger and calendar. "
          "Standings and the regular-season statbook are untouched."
          % (args.game, receipt_path.relative_to(ROOT), output.relative_to(ROOT) if output else "no output.md yet",
             ", ".join(sorted(views))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
