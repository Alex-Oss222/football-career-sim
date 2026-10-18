#!/usr/bin/env python3
"""Close one week's games from its frozen package and generate every view.

  python scripts/close_week.py WEEK --season YEAR --close
  python scripts/close_week.py WEEK --season YEAR --close --continue ANSWER.json

Requires .sim_cache/YEAR/week_NN_inputs.json from build_week_inputs.py and a READY
check_game_readiness.py. Each game closes once through the production runner
(runtime.game_runner.run_game); a rerun of this command only replays events
already closed, which the private service returns unchanged. Results are
kept in .sim_cache/YEAR/week_NN_results.json. Then it writes the public receipts
(full for Jacksonville, compact for everyone else) and regenerates the
statbook and standings. It never writes the weekly prose or advances the
private snapshot.

Kernel 2014.4 (E2): Jacksonville's game runs first, user controlled. When the
kernel stops at a consequential Jacksonville removal, the completed events
are written to the week folder's paused_game.json (no final totals), the
pause is printed, and the command exits with status 2 before any other game
of the slate or any receipt closes. Stone answers with a JSON file
{"choices": {"<removed player>": "<replacement>"}} and reruns the command
with --continue ANSWER.json: the same packet closes through the same private
event reference, so the prefix and the frozen injury reproduce, and the
whole slate then closes as one batch. Background games stay autonomous.

Kernel 2014.6 (batch B9F): the same pause carries Stone's live decisions
(the pause's trigger): a Jacksonville fourth down ("fourth_down", prepared
before the third-down snap whenever possible; answer {"choices":
{"fourth_down": "go"|"field_goal"|"punt", "call": "<a call of the matching
menu, with go>"}}), and, when the frozen sheet's block says otherwise: ask, a
two-point try ("two_point", {"choices": {"try": "go"|"kick"}}) or an onside
kick ("onside", {"choices": {"kickoff": "onside"|"deep"}}). The paused record
shows only what the staff supply, never a probability.

Kernel 2014.6 W1a: the structured defensive sheet (records only) stays out of
the journaled packet, so the paused record (and the closed record after it)
binds each sheet's sha256 ("defensive_sheets"); a resume or a re-closure
whose frozen package carries another sheet, or a sheet the pause did not, is
refused before any draw (overnight review fix, October 17, 2026).

Decision queue (state/decision_queue.json): an open item that holds this
week, or a part of its committed call sheet or of Jacksonville's frozen
inputs, refuses --close and --close --continue with exit status 1 before the
readiness check, the private snapshot or any draw; the dry run reports it
(runtime.decision_queue). While the game is paused, or once part of the
slate has closed, the only instruction is to revert the edit that opened it.
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
PAUSED = 2  # exit status: the protagonist game waits for Stone's answer
PARTIAL_FIELDS = ("score", "possessions", "kickoffs", "play_ledger", "injuries",
                  "substitutions", "pauses")


def team_input(data):
    from runtime.kernel import TeamInput
    # Kernel 2014.6 W1a: the frozen package's structured defensive sheet
    # (records only) passes through as a dict, or None without one; a resume
    # reads the same frozen package, whose sheets the paused record binds.
    sheet = data.get("defensive_call_sheet")
    return TeamInput(**{**data, "active_players": tuple(data["active_players"]),
                        "roster": tuple(data["roster"]),
                        "offensive_call_sheet": tuple(data.get("offensive_call_sheet", ())),
                        "defensive_call_sheet": dict(sheet) if sheet is not None else None})


def encode(value):
    if dataclasses.is_dataclass(value):
        return dataclasses.asdict(value)
    raise TypeError(type(value))


def as_json(value):
    return json.loads(json.dumps(value, default=encode))


def protagonist_game(package):
    games = [g for g in package["games"] if PROTAGONIST in (g["away"], g["home"])]
    if len(games) > 1:
        raise ValueError("more than one protagonist game in the weekly package")
    return games[0] if games else None


def controlled_team_id(game):
    side = "home_input" if game["home"] == PROTAGONIST else "away_input"
    return game[side]["team_id"]


def load_answer(path):
    """Stone's answer: {"choices": {slot: answer}, "token"?: str}: a removed
    player's replacement, or (kernel 2014.6) a fourth-down, two-point or
    onside decision by its slot; the kernel validates it against the pause."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("choices"), dict) or not data["choices"]:
        raise ValueError("answer file must hold a nonempty 'choices' object {slot: answer} (a removed player's "
                         "replacement, or fourth_down, call, try or kickoff)")
    if "token" in data and not isinstance(data["token"], str):
        raise ValueError("answer token must be a string")
    return data


def read_paused(record_path, event_id, kernel_version=None):
    """The week's paused record for this event, or None. Kernel 2014.6
    plumbing (batch B1): a pause is continued only by the kernel that made
    it. A waiting pause recorded under another kernel version is refused
    (with or without --continue): resuming would replay its prefix with
    different draws, so the recorded state could not reproduce."""
    if not record_path.exists():
        return None
    record = json.loads(record_path.read_text(encoding="utf-8"))
    if record.get("event_id") != event_id:
        raise ValueError("paused record %s belongs to event %s, not %s"
                         % (record_path, record.get("event_id"), event_id))
    if kernel_version is None:
        from runtime import KERNEL_VERSION as kernel_version
    if record.get("status") == "paused" and record.get("kernel_version") != kernel_version:
        raise ValueError("paused record %s was made by kernel %s; the live kernel is %s, so --continue "
                         "cannot resume it" % (record_path, record.get("kernel_version"), kernel_version))
    return record


def continuation_decisions(record, answer):
    """The decisions already made plus Stone's new answer, bound to the pending token."""
    decisions = list((record or {}).get("decisions", []))
    if answer is None:
        return decisions
    if record is None or record.get("status") != "paused":
        raise ValueError("--continue given but no paused protagonist game is waiting")
    token = record["pause"]["continuation_token"]
    if answer.get("token", token) != token:
        raise ValueError("answer token does not match the pending pause")
    decisions.append({"token": token, "choices": dict(answer["choices"])})
    return decisions


def defensive_sheet_hashes(game):
    """Kernel 2014.6 W1a (overnight review fix, October 17, 2026): {club:
    sha256} of the frozen package's structured defensive sheets for this
    game ({} without one). The sheet stays out of the journaled packet, so
    the paused record binds it instead: a resume or a re-closure of the same
    event refuses a package whose sheet changed (check_sheet_binding)."""
    from runtime.defensive_calls import sheet_sha256
    return {inp["team_id"]: sheet_sha256(inp["defensive_call_sheet"])
            for inp in (game["home_input"], game["away_input"]) if inp.get("defensive_call_sheet") is not None}


def check_sheet_binding(record, record_path, game):
    """Refuse, before any draw, a paused or closed record whose bound
    defensive sheets differ from the frozen package's (a record without the
    binding bound none)."""
    bound, now = record.get("defensive_sheets") or {}, defensive_sheet_hashes(game)
    if bound != now:
        raise ValueError("the frozen package's defensive call sheet changed since the pause: %s binds %s, the "
                         "package carries %s" % (record_path, json.dumps(bound, sort_keys=True),
                                                 json.dumps(now, sort_keys=True)))


def write_paused(record_path, package, game, partial, decisions):
    """E2 step 4: completed events only. Never final totals."""
    if partial.get("terminated") or "final_score" in partial or "team_stats" in partial:
        raise RuntimeError("refusing to record a finished game as paused")
    record = {"status": "paused", "season": package["season"], "week": package["week"],
              "event_id": game["event_id"], "matchup": "%s at %s" % (game["away"], game["home"]),
              "kernel_version": partial.get("kernel_version"),
              "pause": partial["pauses"][-1], "decisions": decisions,
              "partial": {k: partial[k] for k in PARTIAL_FIELDS if k in partial}}
    sheets = defensive_sheet_hashes(game)
    if sheets:
        record["defensive_sheets"] = sheets
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_text(json.dumps(record, sort_keys=True, indent=1) + "\n", encoding="utf-8")
    return record


TRIGGER_TEXT = {"consequential_substitution": "consequential substitution", "fourth_down": "fourth down",
                "two_point": "try after touchdown", "onside": "kickoff"}
ANSWER_EXAMPLE = {"fourth_down": '{"choices": {"fourth_down": "go" | "field_goal" | "punt", "call": "<call>"}}',
                  "two_point": '{"choices": {"try": "go" | "kick"}}',
                  "onside": '{"choices": {"kickoff": "onside" | "deep"}}'}
ORDINAL = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th"}


def _fourth_down_lines(pause):
    """Skalaski's and Tice's information as the pause carries it."""
    sit, kick, conv = pause["situation"], pause["kicking"], pause["conversion_call"]
    distance = "goal" if sit.get("goal_to_go") else sit.get("ydstogo")
    timing = ("prepared before the third-down snap" if pause.get("timing") == "before_third_down"
              else "at the fourth-down snap")
    lines = ["- %s: %s and %s at the %s (%s yards to the goal line)" % (
                 timing, ORDINAL.get(sit.get("down"), sit.get("down")), distance, sit.get("field_position"),
                 sit.get("yardline_100")),
             "- Skalaski: score %s, clock %s %s, timeouts %s (held at %s)" % (
                 json.dumps(pause.get("score"), sort_keys=True), pause.get("period"), pause.get("clock"),
                 json.dumps(pause.get("timeouts"), sort_keys=True), pause.get("timeouts_as_of")),
             "- Skalaski: field goal of %s yards from %s; kicker %s, punter %s; venue %s (home %s), weather %s" % (
                 kick.get("field_goal_distance"), kick.get("from"), kick.get("kicker"), kick.get("punter"),
                 kick.get("venue"), kick.get("home"), kick.get("weather")),
             "- Tice: prepared conversion call %s; matching menu %s: %s" % (
                 conv.get("prepared") or "(none named on the frozen sheet)",
                 conv.get("menu") or "(the sheet declares no menus; every call)",
                 ", ".join(conv.get("calls") or []) or "(no call on the sheet)")]
    so_far = pause.get("drive_so_far") or {}
    snaps = so_far.get("snaps") or []
    scrimmage = sum(s.get("yards", 0) for s in snaps)
    if "penalties" not in so_far:
        lines.append("- the drive so far: from %s yards out, %d snaps, %d yards" % (
            so_far.get("start_yardline_100"), len(snaps), scrimmage))
        return lines
    # Kernel 2014.6 batch B11 review fix (October 16, 2026): scrimmage and
    # penalty yards apart, adding to the start less the spot shown.
    lines.append("- the drive so far: from %s yards out, %d snaps, %d scrimmage yards, %d penalty yards" % (
        so_far.get("start_yardline_100"), len(snaps), scrimmage, so_far.get("penalty_yards", 0)))
    for entry in so_far["penalties"]:
        lines.append("  - after %d snaps: %s on the %s, %s, %+d yards%s" % (
            entry.get("after_snaps", 0), entry.get("type"), entry.get("fouled_by"), entry.get("status"),
            entry.get("yards", 0), ", first down" if entry.get("first_down") else ""))
    return lines


def default_detail(decision):
    """Kernel 2014.6 batch B15 (W2c): what the depth_order default does (the
    entrant and the slot moves of the autonomous rule); empty for a pause
    record without them."""
    if "default_entrant" not in decision:
        return ""
    moves = ", ".join("%s %s to %s" % (m["player"], m["from"], m["to"]) for m in decision.get("default_moves") or ())
    return " (enters: %s; moves: %s)" % (decision.get("default_entrant") or "none", moves or "none")


def describe_pause(record, record_path, week, season):
    pause = record["pause"]
    trigger = pause.get("trigger", "consequential_substitution")
    lines = ["WEEK %d PAUSED (%s): %s, drive %s, %s %s, score %s"
             % (week, TRIGGER_TEXT.get(trigger, trigger), record["matchup"], pause.get("drive"), pause.get("period"),
                pause.get("clock"), json.dumps(pause.get("score"), sort_keys=True))]
    if trigger == "fourth_down":
        lines += _fourth_down_lines(pause)
    elif trigger in ("two_point", "onside"):
        lines.append("- situation %s" % json.dumps(pause.get("situation"), sort_keys=True))
    for injury in pause.get("injuries", []):
        lines.append("- removed: %s (%s; %s, %s, restriction %s)"
                     % (injury.get("player"), injury.get("team"), injury.get("injury_class"),
                        injury.get("severity"), injury.get("restriction")))
    for decision in pause.get("decisions", []):
        if trigger == "consequential_substitution":
            lines.append("- replace %s (%s; %s): eligible %s; depth default %s%s"
                         % (decision["slot"], decision.get("group"), decision.get("reason"),
                            ", ".join(decision["eligible"]), decision.get("default"), default_detail(decision)))
        else:
            lines.append("- %s: one of %s%s" % (decision["slot"], ", ".join(decision["eligible"]),
                                                 " (with %s)" % decision["with"] if decision.get("with") else ""))
    lines.append("- continuation token %s... (paused record: %s)"
                 % (pause["continuation_token"][:16], record_path))
    if trigger in ANSWER_EXAMPLE:
        example = ANSWER_EXAMPLE[trigger]
    else:
        example = '{"choices": {%s}}' % ", ".join('"%s": "<replacement>"' % d["slot"]
                                                  for d in pause.get("decisions", []))
    lines.append("Answer with a JSON file %s and rerun: "
                 "python scripts/close_week.py %d --season %d --close --continue ANSWER.json"
                 % (example, week, season))
    return "\n".join(lines)


def close_slate(package, paths, snapshot, client, results_path, answer=None, run=None):
    """Close the week's events: Jacksonville first under user control, then the rest.

    Returns (results, paused_record). With a paused record no other game of the
    slate has been drawn and nothing else was written.
    """
    if run is None:
        from runtime.game_runner import run_game as run
    week = package["week"]
    results = json.loads(results_path.read_text(encoding="utf-8")) if results_path.exists() else {}
    postseason_week = any(g.get("game_type") == "postseason" for g in package["games"])
    own = protagonist_game(package)
    if own is None and answer is not None:
        raise ValueError("--continue given but Jacksonville does not play this week")
    if own is not None and own["event_id"] not in results:
        record_path = paths.paused_game(week, postseason_week)
        record = read_paused(record_path, own["event_id"])
        if record is not None:
            check_sheet_binding(record, record_path, own)
        decisions = continuation_decisions(record, answer)
        result = run(team_input(own["home_input"]), team_input(own["away_input"]),
                     event_id=own["event_id"], snapshot=snapshot, client=client,
                     venue=own["venue"], game_type=own.get("game_type", "regular"),
                     management_mode="user_controlled", controlled_team=controlled_team_id(own),
                     continuation={"decisions": decisions} if decisions else None)
        result = as_json(result)
        if not result.get("terminated"):
            return results, write_paused(record_path, package, own, result, decisions)
        results[own["event_id"]] = result
        results_path.parent.mkdir(parents=True, exist_ok=True)
        results_path.write_text(json.dumps(results), encoding="utf-8")
        print("closed %s" % own["event_id"])
        if record is not None:
            closed = {k: record[k] for k in ("season", "week", "event_id", "matchup")}
            closed.update({"status": "closed", "decisions": decisions, "pauses": result.get("pauses", [])})
            if record.get("defensive_sheets"):
                closed["defensive_sheets"] = record["defensive_sheets"]
            record_path.write_text(json.dumps(closed, sort_keys=True, indent=1) + "\n", encoding="utf-8")
    for game in package["games"]:
        if game is own or game["event_id"] in results:
            continue
        result = run(team_input(game["home_input"]), team_input(game["away_input"]),
                     event_id=game["event_id"], snapshot=snapshot, client=client,
                     venue=game["venue"], game_type=game.get("game_type", "regular"))
        results[game["event_id"]] = as_json(result)
        results_path.parent.mkdir(parents=True, exist_ok=True)
        results_path.write_text(json.dumps(results), encoding="utf-8")
        print("closed %s" % game["event_id"])
    return results, None


def write_receipts(package, paths, results, season):
    from runtime.statbook import make_receipt
    from runtime.player_bios import unverified_ages
    # Postseason receipts live apart so standings, the regular-season statbook,
    # awards and the band audit stay regular-season only (runtime.postseason).
    postseason_week = any(g.get("game_type") == "postseason" for g in package["games"])
    receipts_dir = paths.postseason_receipts if postseason_week else paths.receipts
    receipts_dir.mkdir(parents=True, exist_ok=True)
    for game in package["games"]:
        detail = "full" if PROTAGONIST in (game["away"], game["home"]) else "compact_stats"
        receipt = make_receipt(results[game["event_id"]], week=package["week"],
                               matchup="%s at %s" % (game["away"], game["home"]), detail=detail)
        if season != 2013:
            receipt["season"] = season
        # Background players who entered with no verified birth date
        # (runtime.player_bios): public metadata, never a resolution input.
        unverified = unverified_ages(game.get("player_ages"))
        if unverified:
            receipt["age_unverified"] = unverified
        (receipts_dir / game["receipt"]).write_text(
            json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return receipts_dir


def rails_package_errors(package, week, season, root=ROOT):
    """The frozen package's in-season rails record must match the committed
    data and the schedule's cutoffs (engineering review S2, S3): a rebuild
    after a technical abort reproduces the same inputs or nothing closes."""
    from runtime import rails
    from runtime.week_inputs import event_id, schedule
    data = rails.load(season, root)
    if data is None or week < data.effective_from_week:
        return ["package carries in-season rails metadata before the rails' effective week"] \
            if package.get("rails") else []
    meta = package.get("rails")
    if not meta:
        return ["package lacks its in-season rails record (rebuild with build_week_inputs.py)"]
    errors = []
    games = schedule(week, season)
    cutoffs = rails.slate_cutoffs(games)
    expected = {event_id(g, season=season): cutoffs[rails.game_key(g)].isoformat() for g in games}
    if meta.get("cutoffs") != expected:
        errors.append("package rails cutoffs differ from the schedule's")
    if meta.get("manifest_sha256") != rails.sha256_file(rails.data_dir(season, root) / "manifest.json"):
        errors.append("in-season rails data changed after the package was frozen")
    db_meta = meta.get("db_slots") or {}
    if db_meta.get("applied"):
        # Review fix (October 16, 2026): the defensive-back family table the
        # package's labels came from (batch B15, W2b).
        from runtime.seasons import SeasonPaths
        table = SeasonPaths(season, root).db_families
        if not table.is_file() or db_meta.get("families_sha256") != rails.sha256_file(table):
            errors.append("the defensive-back family table changed after the package was frozen "
                          "(or the package does not record it); rebuild with build_week_inputs.py")
    coverage = rails.week_cutoff_coverage_error(data, max(cutoffs.values()), week)
    if coverage:
        errors.append(coverage)
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("week", type=int)
    parser.add_argument("--close", action="store_true", help="actually close the events")
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--continue", dest="answer", metavar="ANSWER.json",
                        help="Stone's answer for a paused Jacksonville game (a substitution, or a "
                             "fourth-down, two-point or onside decision)")
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
    errors += rails_package_errors(package, args.week, args.season)
    errors += check_inputs(package, controlled_players_from_roster(paths.roster),
                           PROTAGONIST, expected_games=len(schedule(args.week, args.season)))
    if errors:
        # The frozen package must still pass the weekly gate before any draw.
        print("WEEK_INPUTS: BLOCKED")
        for error in errors:
            print("- " + error)
        return 1
    # The decision queue: never inside close_slate, so no slate is refused
    # partway; imported here so nothing that draws a game loads it.
    from runtime import decision_queue
    sheet = decision_queue.committed_sheet(args.season, args.week, ROOT)
    # The parts the committed sheet freezes and the parts the frozen package
    # would draw: a block dropped from the sheet after the build still holds.
    parts = decision_queue.sheet_parts(sheet) if sheet else []
    parts += [p for p in decision_queue.package_parts(package, PROTAGONIST) if p not in parts]
    checks = [decision_queue.event("week_close", args.season, args.week)]
    checks += [decision_queue.event("call_sheet_part", args.season, args.week, part=p) for p in parts]
    postseason_week = any(g.get("game_type") == "postseason" for g in package["games"])
    record_path = paths.paused_game(args.week, postseason_week)
    paused_now = decision_queue._paused(record_path)
    partial = paths.cache(args.week, "results").exists()
    held = decision_queue.blocking_errors(checks, ROOT, settle=not (paused_now or partial))
    if not args.close:
        for line in held:
            print("Note: " + line + " (a --close would be refused)")
        print("Dry run: %d games in %s; add --close to close them." % (len(package["games"]), package_path.name))
        return 0
    if held:
        print("WEEK_CLOSE: BLOCKED\n- " + "\n- ".join(held))
        if paused_now:
            print("- The paused game record %s is unchanged. Document 5 and the decision queue must not change "
                  "while a game is paused: revert the edit that opened this item, then rerun %s."
                  % (record_path.relative_to(paths.root),
                     "the same --continue" if args.answer else "with --continue and Stone's answer"))
        elif partial:
            print("- Part of this week's slate has already closed (%s). Revert the edit that opened this item and "
                  "rerun: the closed events replay unchanged. Never void or redraw the week for it."
                  % paths.cache(args.week, "results").relative_to(paths.root))
        return 1
    answer = load_answer(args.answer) if args.answer else None
    readiness = subprocess.run([sys.executable, str(ROOT / "scripts/check_game_readiness.py"), "--season", str(args.season)],
                               capture_output=True, text=True)
    if "GAME READINESS: READY" not in readiness.stdout:
        print(readiness.stdout + readiness.stderr)
        return 1

    from runtime.private_client import Client

    snapshot = hashlib.sha256((ROOT / "state/05_Current_Season_State.md").read_bytes()).hexdigest()
    client = Client(snapshot=snapshot)
    results, paused = close_slate(package, paths, snapshot, client, paths.cache(args.week, "results"), answer)
    if paused is not None:
        postseason_week = any(g.get("game_type") == "postseason" for g in package["games"])
        print(describe_pause(paused, paths.paused_game(args.week, postseason_week), args.week, args.season))
        return PAUSED

    write_receipts(package, paths, results, args.season)
    if args.season != 2013:
        # Kernel 2014.6 (B7): the week's participation observables from the
        # frozen package (runtime.observables); records only.
        from runtime import observables
        observables.write(observables.from_package(package, observables.season_identities(args.season, ROOT)), ROOT)
    subprocess.run([sys.executable, str(ROOT / "scripts/render_season_stats.py"), str(args.season),
                    "--team", PROTAGONIST], check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts/render_standings.py"), str(args.season)], check=True)
    print("Week %d closed: %d receipts written. Next: fill the box score with "
          "render_box_score.py --write, write the weekly output and league roundup, close state."
          % (args.week, len(package["games"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
