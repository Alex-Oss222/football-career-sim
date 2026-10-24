#!/usr/bin/env python3
"""Check a week's practice schedule and record what was held (rebuild step 5, C1).

  python scripts/record_practice_week.py WEEK --season YEAR --schedule [--root PATH]
  python scripts/record_practice_week.py WEEK --season YEAR [--file INPUT.json] [--check] [--root PATH]

Each week's practice schedule (each session's day, type, equipment and required
attendance, and the players' days off) is Stone's decision (Document 3 row 11).
While his standing practice instruction is in force (the job record, subject
``practice_schedule``; the user's answer of October 23, 2026, "Spread the
pads"), the week's schedule is built from it (runtime/practices.
schedule_from_instruction): the six days before a game on its game day, pads on
the days it names, its unpadded equipment otherwise, and the days off it adds.
Nothing defaults: a week the instruction does not set (the bye, whose work and
break are set on My Adjustments; a game on another day, the Thursday game of
2014 Week 16) has no schedule here.

--schedule shows the week's schedule and checks it, before any session, against
the padded-practice and rest limits (runtime/practices.check_schedule: the
eleven of the first eleven weeks and the three of the last six as the closed
records leave them, two in one week only once, no required player work on a
day off beyond an injured player's treatment and quarterback meetings, and the
bye's break). It writes nothing, and exits 1 when the week is not set by the
instruction or the schedule is refused.

With --file it records what was held in the practice-week commit, against the
week's applied schedule (docs/run_week.md, step 5), as the week's practice and
rest record (``practices.json`` in the week's data folder, runtime/practices.py).
The file holds the page the week's preparation is recorded on (``source``:
{page, anchor}), each session held, changed or cancelled (date, type,
equipment and participation_recorded required; required true, attendees the
team, held, no pad exception and no participation entry otherwise), the days
off, and the gaps: what the medical staff and the staff did not record. It
refuses a date after the master date or outside the week; a session the
schedule does not name unless it is a change with its basis and source, and a
scheduled session left out; a padded practice beyond the budget or a second
one in a week once the double week is used (a cancelled padded practice is
counted unless it was cancelled within its first hour for a reason beyond the
club's control, a rule on one source, which the page says); a participation
status that contradicts a medical instruction (a player out recorded full, or
not listed in a session whose participation is recorded); a player not on the
roster. With no schedule given it writes the week's not-set record (no
sessions, a gaps line, its padded count unknown): the runner never records a
schedule nobody gave. --check writes nothing. A closed record or a played week
is never rewritten.

Practice produces facts, never invented performance: no adjective, quote or
practice result goes into the record, and no practice injury is generated.
Nothing here moves the clock or creates an event.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import practices  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402

JAX = "Jacksonville Jaguars"
SESSION_DEFAULTS = {"required": True, "attendees": "team", "status": "held", "pad_exceptions": [], "participation": []}
SESSION_NEEDED = ("date", "type", "equipment", "participation_recorded")


def applied_schedule(root, season, week):
    """(schedule or None, why not): the week's schedule as Stone's standing practice instruction sets
    it. Stone's "Practice week" answer on My Responses, while no instruction is in force, is read by
    rebuild step 5's second wave (builder C, after My Responses is merged)."""
    from runtime import current_job
    instruction = current_job.practice_instruction(current_job.load(root), season)
    if instruction is None:
        return None, ("No standing practice instruction is in force for %d; the week's schedule is Stone's answer "
                      "under Practice week on its My Responses page" % season)
    try:
        return practices.schedule_from_instruction(instruction, season, week, root), None
    except practices.NotCovered as exc:
        return None, str(exc)


def roster_names(paths):
    roster = json.loads(paths.roster.read_text(encoding="utf-8"))
    return [p["name"] for p in roster.get("players") or ()] + [d["name"] for d in roster.get("departures") or ()]


def out_on_reader(paths, season):
    """out_on(player, day): "out" or "limited" from an active-roster player's medical instruction on
    the roster record as it stands (a projected return reached clears him, as the game reads it), or
    None. An instruction the staff cannot read is not guessed: None, and the plan check names it."""
    from runtime.week_inputs import roster_available
    roster = json.loads(paths.roster.read_text(encoding="utf-8"))
    notes = {p["name"]: p.get("availability") or "" for p in roster.get("players") or () if p.get("list") == "active"}

    def out_on(player, day):
        note = notes.get(player)
        if not note or note.startswith("No communicated restriction"):
            return None
        if note.startswith("Limited"):
            return "limited"
        try:
            return None if roster_available(note, day, season) else "out"
        except ValueError:
            return None
    return out_on


def played(paths, week):
    folder = paths.receipts
    return folder.is_dir() and any(JAX in json.loads(p.read_text(encoding="utf-8")).get("matchup", "")
                                   for p in folder.glob("week_%02d_*.json" % week))


def held_record(season, week, data, schedule, root):
    """The recorded week from the runner's input file."""
    sessions = []
    for raw in data.get("sessions") or ():
        missing = [k for k in SESSION_NEEDED if k not in raw]
        if missing:
            raise ValueError("a session needs %s (%r)" % (", ".join(missing), raw))
        session = dict(SESSION_DEFAULTS, **{k: v for k, v in raw.items() if k != "change"})
        session = {k: session[k] for k in practices.SESSION_KEYS}
        if "change" in raw:
            session["change"] = raw["change"]
        sessions.append(session)
    days_off = [dict({"players": "all", "exceptions": []}, **d) for d in data.get("days_off") or ()]
    return {"schema": practices.SCHEMA, "season": season, "week": week,
            "kind": "bye" if practices.is_bye(season, week, root) else "game", "basis": "recorded",
            "schedule": {"source": schedule["source"], "sha256": schedule["sha256"]},
            "source": data.get("source"), "sessions": sorted(sessions, key=lambda s: s["date"]),
            "days_off": sorted(days_off, key=lambda d: d["date"]), "gaps": list(data.get("gaps") or [])}


def default_source(paths, week, root):
    """The not-set week's source: the week's Game Report once opened, else its index."""
    for page in (paths.game_report(week), paths.week_folder(week) / "README.md"):
        if page.is_file():
            return {"page": page.relative_to(root).as_posix()}
    raise ValueError("Week %d has no page to cite" % week)


def record(root, season, week, file=None, check=False):
    """(problems, notes, written path or None)."""
    from runtime.player_bios import master_date
    root = Path(root).resolve()
    paths = SeasonPaths(season, root)
    existing = practices.load(season, week, root)
    if existing is not None and existing.get("basis") == "closed_record":
        return ["Week %d's practice is a closed record and stays as written" % week], [], None
    if played(paths, week):
        return ["Week %d has been played; its practice record stays as it was recorded" % week], [], None
    schedule, why = applied_schedule(root, season, week)
    if schedule is None and file is not None:
        return ["No practice schedule was set for Week %d (%s); the runner cannot record a schedule nobody gave. "
                "Record the week as not set (run without --file), or record Stone's schedule first" % (week, why)], [], None
    if schedule is None:
        new = practices.not_set_record(season, week, default_source(paths, week, root), root)
    elif file is None:
        return ["Week %d's schedule is set; name what was held with --file" % week], [], None
    else:
        try:
            new = held_record(season, week, json.loads(Path(file).read_text(encoding="utf-8")), schedule, root)
        except (OSError, ValueError) as exc:
            return ["Week %d's practice file: %s" % (week, exc)], [], None
    found = {w: r for w, r in practices.records(season, root).items() if w != week}
    problems = practices.record_errors(new, root, players=roster_names(paths), master=master_date(root),
                                       out_on=out_on_reader(paths, season), schedule=schedule, records_=found)
    if problems:
        return problems, [], None
    found[week] = new
    notes = practices.days_off(season, root, found)["warnings"]
    if check:
        return [], notes, None
    return [], notes, practices.write(new, root)


def show_schedule(root, season, week):
    """(problems, lines): the week's schedule from the standing instruction and its check."""
    root = Path(root).resolve()
    schedule, why = applied_schedule(root, season, week)
    if schedule is None:
        return [why], []
    dated = [(off["date"], "%s: the players' day off" % practices.long_day(off["date"]))
             for off in schedule["days_off"]]
    dated += [(s["date"], "%s: %s, %s" % (practices.long_day(s["date"]), practices.TYPE_WORDS[s["type"]].lower(),
                                          practices.EQUIPMENT_WORDS[s["equipment"]].lower()))
              for s in schedule["sessions"]]
    lines = [text for _, text in sorted(dated)]
    found = {w: r for w, r in practices.records(season, root).items() if w < week}
    problems = practices.check_schedule(season, week, schedule["sessions"], schedule["days_off"], root, found)
    status = practices.padded_status(season, week - 1, root, found)
    period = status["first" if week <= practices.FIRST_WEEKS else "last"]
    lines.append("Padded practices before this week: %s used, %s left of the %d" % (
        "unknown" if period["used"] is None else period["used"], "unknown" if period["left"] is None else period["left"],
        period["limit"]))
    return problems, lines


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("week", type=int)
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--schedule", action="store_true")
    parser.add_argument("--file", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    if args.schedule:
        problems, lines = show_schedule(args.root, args.season, args.week)
        print("PRACTICE SCHEDULE: %s  Week %d, %d" % ("REFUSED" if problems and lines else
                                                      "NOT SET" if problems else "SET", args.week, args.season))
        for line in lines:
            print("  " + line)
        for problem in problems:
            print("- " + problem)
        return 1 if problems else 0
    problems, notes, written = record(args.root, args.season, args.week, args.file, args.check)
    if problems:
        print("PRACTICE WEEK: NOT RECORDED")
        for problem in problems:
            print("- " + problem)
        return 1
    print("PRACTICE WEEK: %s  Week %d, %d" % ("CHECKED" if args.check else "RECORDED", args.week, args.season))
    if written is not None:
        print("wrote %s" % written.relative_to(Path(args.root).resolve()).as_posix())
    for note in notes:
        print("  note: " + note)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
