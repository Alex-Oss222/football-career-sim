#!/usr/bin/env python3
"""Check a week's practice schedule and record what was held (rebuild step 5, C1).

  python scripts/record_practice_week.py WEEK --season YEAR --schedule [--upload PAGE] [--check] [--root PATH]
  python scripts/record_practice_week.py WEEK --season YEAR [--file INPUT.json] [--check] [--root PATH]

Each week's practice schedule (each session's day, type, equipment and required
attendance, and the players' days off) is Stone's decision (Document 3 row 11).
While his standing practice instruction is in force (the job record, subject
``practice_schedule``; the user's answer of October 23, 2026, "Spread the
pads"), the week's schedule is built from it (runtime/practices.
schedule_from_instruction): the six days before a game on its game day, pads on
the days it names, its unpadded equipment otherwise, and the days off it adds;
and it covers the week only when that schedule passes the padded-practice and
rest limits (``cover``: runtime/practices.check_schedule, against the records
of the weeks before it). A week the instruction does not cover (a game on
another day, as the Thursday game of 2014 Week 16; a week whose padded count is
unknown or spent; any week while no instruction is in force) is asked on the
week's My Responses page: the week's opening (scripts/open_game_week.py) opens
a ``practice_plan`` item owned by Stone, due before the first day of the
practice week and holding nothing, with a blank block under the reserved
heading "Practice week", and he answers it there in the form
runtime/practices.compile_answer reads ("Tuesday: day off", "Wednesday:
practice in helmets and shoulder pads", "Saturday: walkthrough in helmets").
Nothing defaults: the runner never writes a schedule. The bye's work and break
are set on My Adjustments (rebuild step 5, C3), not here.

--schedule, for a week the instruction covers, shows the schedule and its
check and writes nothing. For a week asked on My Responses it reads his block,
compiles it and checks it before any session against the same limits (the
eleven of the first eleven weeks and the three of the last six as the earlier
records leave them, two in one week only once, no required player work on a
day off beyond an injured player's treatment and quarterback meetings, every
day inside the week and none already past), in the messages of docs/bye_week.md
section 6; once it passes it fills the block's empty "Date answered" line with
the master date (the runner's only edit to his page), freezes the block by its
digest in the week's responses record (``applied``: its sha256, date and the
compiled schedule) and resolves the item by the user with the block as its
record. With --check it writes nothing. An empty block leaves the question
open; exit 1 while the week has no schedule or the answer is refused. With
--upload his page (a .md or .txt file with the same headings) is placed first
(``place_upload``), and nothing is written when it is refused.

With --file it records what was held in the practice-week commit, against the
week's applied schedule (his applied answer, else the instruction where it
covers the week; docs/run_week.md, step 5), as the week's practice and rest
record (``practices.json`` in the week's data folder, runtime/practices.py).
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

The reserved blocks of My Responses (``reserved_*``, ``freeze_block``,
``place_upload``) are shared with scripts/change_game_day.py: an applied block
stays as written, and an upload that changes one, or that carries a reserved
heading the week has not asked, is refused with nothing written.

Practice produces facts, never invented performance: no adjective, quote or
practice result goes into the record, and no practice injury is generated.
Nothing here moves the clock or creates an event.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import decisions, practices  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402

JAX = "Jacksonville Jaguars"
SESSION_DEFAULTS = {"required": True, "attendees": "team", "status": "held", "pad_exceptions": [], "participation": []}
SESSION_NEEDED = ("date", "type", "equipment", "participation_recorded")


def instruction_schedule(root, season, week):
    """(schedule or None, why not): the week's schedule as Stone's standing practice instruction
    builds it, before it is checked."""
    from runtime import current_job
    instruction = current_job.practice_instruction(current_job.load(root), season)
    if instruction is None:
        return None, ("No standing practice instruction is in force for %d; the week's schedule is Stone's answer "
                      "under Practice week on its My Responses page" % season)
    try:
        return practices.schedule_from_instruction(instruction, season, week, root), None
    except practices.NotCovered as exc:
        return None, str(exc)


def cover(root, season, week, records_=None):
    """(schedule or None, why not): the week's schedule when the standing practice instruction
    covers it: it builds the week and its schedule passes the padded-practice and rest limits
    against the records of the weeks before it. Otherwise the week is asked on My Responses."""
    root = Path(root).resolve()
    schedule, why = instruction_schedule(root, season, week)
    if schedule is None:
        return None, why
    found = practices.records(season, root) if records_ is None else records_
    problems = practices.check_schedule(season, week, schedule["sessions"], schedule["days_off"], root,
                                        {w: r for w, r in found.items() if w < week})
    if problems:
        return None, ("The standing practice instruction's Week %d schedule does not pass the practice limits: %s"
                      % (week, " ".join(p.rstrip(".") + "." for p in problems)))
    return schedule, None


def answered_schedule(root, season, week):
    """The week's schedule as Stone's applied "Practice week" answer sets it, or None."""
    root = Path(root).resolve()
    entry = reserved_binding(root, season, {"week": week}, PRACTICE_WEEK)
    applied = (entry or {}).get("applied") or {}
    substance = applied.get("substance") or {}
    if substance.get("kind") != PRACTICE_KIND:
        return None
    page = decisions.week_pages(season, week, root).responses.relative_to(root).as_posix()
    return practices.schedule_from_answer(substance, page, PRACTICE_WEEK)


def applied_schedule(root, season, week):
    """(schedule or None, why not): the week's schedule, as his applied answer sets it, else as the
    standing practice instruction covers it. The bye's is his applied My Adjustments (its work and
    the players' days off, runtime/bye_week.applied_schedule): until it is applied no player session
    of the bye can be recorded as required work."""
    root = Path(root).resolve()
    if practices.is_bye(season, week, root):
        from runtime import bye_week
        schedule = bye_week.applied_schedule(season, week, root)
        if schedule is None:
            return None, "the bye's work and break are set on My Adjustments, which is not applied yet"
        return schedule, None
    answered = answered_schedule(root, season, week)
    if answered is not None:
        return answered, None
    return cover(root, season, week)


# ------------------------------------------------------------------ his reserved blocks on My Responses
PRACTICE_WEEK = decisions.PRACTICE_WEEK
PRACTICE_KIND = "practice_schedule"
DATE_LINE = re.compile(r"^\*\*Date answered:\*\*[ \t]*$", re.M)


def responses_rel(root, season, period):
    from runtime import responses
    return responses.pages_of(season, period, root).responses.relative_to(root).as_posix()


def reserved_binding(root, season, period, heading):
    """The responses record's binding of a reserved heading of the period, or None."""
    from runtime import responses
    record = responses.record_of(season, period, root)
    return next((b for b in record.get("blocks") or () if b.get("heading") == heading), None)


def read_block(root, season, period, heading):
    """The block under ``heading`` on the period's My Responses page, or None."""
    from runtime import responses
    page = responses.pages_of(season, period, root).responses
    if not page.is_file():
        return None
    return responses.blocks_of(page.read_text(encoding="utf-8")).get(heading)


def date_problem(block, master):
    """His block may leave "Date answered" empty (the staff fills it) or name the master date."""
    from runtime.responses import FIELDS
    written = block.fields.get(FIELDS[3], "").strip()
    if written and written != "%s %d, %d" % (master.strftime("%B"), master.day, master.year):
        return "%s: Date answered is filled in by the staff when the answer is recorded; leave it empty" % block.heading
    return None


def clean_problems(root, season, period, block):
    """His block's own words held to the clean-page check (the page is one, his to keep clean)."""
    from runtime.clean_pages import page_errors
    return ["%s: %s" % (block.heading, e.split(": ", 1)[-1])
            for e in page_errors(responses_rel(root, season, period), block.text, root=root)]


def filled(block, master):
    """The block's bytes with an empty "Date answered" line filled with the master date."""
    on = "%s %d, %d" % (master.strftime("%B"), master.day, master.year)
    return DATE_LINE.sub("**Date answered:** %s" % on, block.text, count=1)


def freeze_block(root, season, period, block, substance, master):
    """Fill the block's empty "Date answered" line (the runner's only edit to his page), then freeze
    it: its binding's ``applied`` holds the filled block's sha256, the date and what it commits to
    (``substance``), so responses validation holds it to its digest. Returns the frozen block."""
    from runtime import responses
    pages = responses.pages_of(season, period, root)
    text = pages.responses.read_text(encoding="utf-8")
    new = filled(block, master)
    if new != block.text:
        if text.count(block.text) != 1:
            raise ValueError("%s: the block is not once on the page" % block.heading)
        text = text.replace(block.text, new, 1)
        pages.responses.write_text(text, encoding="utf-8")
    frozen = responses.blocks_of(text)[block.heading]
    record = responses.record_of(season, period, root)
    entry = next(b for b in record["blocks"] if b.get("heading") == block.heading)
    entry["applied"] = {"sha256": frozen.sha256, "date": master.isoformat(), "substance": substance}
    responses._save_record(season, period, root, record)
    return frozen


def reserved_upload_problems(root, season, period, text):
    """Why an uploaded My Responses page may not replace the period's: a reserved heading the period
    has not asked (no binding), or an applied reserved block changed or removed. [] when it may."""
    from runtime import responses
    record = responses.record_of(season, period, root)
    bound = {b["heading"]: b for b in record.get("blocks") or () if decisions.reserved_heading(b.get("heading"))}
    blocks = responses.blocks_of(text)
    problems = []
    for heading in blocks:
        if decisions.reserved_heading(heading) and heading not in bound:
            problems.append("%s: this answer has not been asked for %s; the staff opens it when it is needed"
                            % (heading, open_label(period)))
    for heading, entry in bound.items():
        applied = entry.get("applied")
        if not applied:
            continue
        if heading not in blocks:
            problems.append("%s: a recorded answer cannot be removed" % heading)
        elif blocks[heading].sha256 != applied.get("sha256"):
            problems.append("%s: this answer was recorded on %s and stays as written" % (heading, applied.get("date")))
    return problems


def open_label(period):
    (kind, week), = period.items()
    return "Week %d" % week if kind == "week" else "the Week %d bye" % week


def place_upload(root, season, period, source):
    """An uploaded .md or .txt My Responses page, checked first for his reserved blocks
    (``reserved_upload_problems``), then placed through runtime/responses.place_upload, which writes
    only the period's My Responses page. ValueError, with nothing written, when refused."""
    from runtime import responses
    source = Path(source)
    if source.suffix.lower() not in (".md", ".txt"):
        raise ValueError("an uploaded My Responses page is a .md or .txt file")
    text = source.read_text(encoding="utf-8")
    problems = reserved_upload_problems(Path(root).resolve(), season, period, text if text.endswith("\n")
                                        else text + "\n")
    if problems:
        raise ValueError("; ".join(problems))
    return responses.place_upload(root, season, period, source)


def practice_item(root, season, week, queue=None):
    """The week's practice ask (decision_queue.practice_item, its record the week's My Responses
    page), open or settled, or None."""
    from runtime import current_job, decision_queue
    root = Path(root).resolve()
    queue = decision_queue.load(root) if queue is None else queue
    holder = current_job.load(root).get("holder")
    rel = decisions.week_pages(season, week, root).responses.relative_to(root).as_posix()
    return next((i for i in queue["items"] if decision_queue.practice_item(i, holder)
                 and (i.get("record") or {}).get("path") == rel), None)


def answer(root, season, week, check=False):
    """(status, problems, lines, written): Stone's "Practice week" answer read, compiled and checked
    before any session; once it passes (and not ``check``) the block is frozen and the item resolved
    by the user. Status: SET (answered and applied, or applied now), CHECKED, WAITING (no answer
    yet), REFUSED or NOT ASKED."""
    from runtime import decision_queue
    from runtime.player_bios import master_date
    from scripts.render_career_views import paused_games
    root = Path(root).resolve()
    period = {"week": week}
    item = practice_item(root, season, week)
    if item is None:
        return "NOT ASKED", ["Week %d's practice week has not been asked on My Responses (the week's opening asks it "
                             "when no standing practice instruction covers the week)" % week], [], []
    answered = answered_schedule(root, season, week)
    if item.get("status") != "OPEN" or answered is not None:
        if answered is None:
            return "REFUSED", ["Week %d's practice question was settled without a recorded answer" % week], [], []
        return "SET", [], practices.schedule_lines(answered), []
    block = read_block(root, season, period, PRACTICE_WEEK)
    if block is None:
        return "REFUSED", ["The %s block is missing from the Week %d My Responses page" % (PRACTICE_WEEK, week)], [], []
    if not block.answer:
        return "WAITING", ["%s: still open; no answer yet. Nothing is set and no session is scheduled until you "
                           "answer, %s" % (PRACTICE_WEEK, practices.ANSWER_FORM)], [], []
    master = master_date(root)
    compiled, problems = practices.compile_answer(block.answer, season, week, root)
    lines = practices.schedule_lines(compiled) if not problems else []
    problems += [p for p in [date_problem(block, master)] if p]
    problems += clean_problems(root, season, period, block)
    if not problems:
        past = [s["date"] for s in compiled["sessions"] + compiled["days_off"] if s["date"] < master.isoformat()]
        if past:
            problems.append("%s has passed; the schedule sets the days still to come" % practices.long_day(min(past)))
    if not problems:
        earlier = {w: r for w, r in practices.records(season, root).items() if w < week}
        problems += practices.check_schedule(season, week, compiled["sessions"], compiled["days_off"], root, earlier)
    if problems:
        return "REFUSED", problems, lines, []
    if check:
        return "CHECKED", [], lines, []
    if paused_games(root):
        return "REFUSED", ["A Jacksonville game is paused; nothing is recorded until it is finished"], lines, []
    substance = {"kind": PRACTICE_KIND, "sessions": compiled["sessions"], "days_off": compiled["days_off"]}
    freeze_block(root, season, period, block, substance, master)
    queue = decision_queue.load(root)
    padded = sum(1 for s in compiled["sessions"] if practices.session_padded(s))
    rel = responses_rel(root, season, period)
    for entry in queue["items"]:
        if entry.get("id") == item["id"]:
            entry["status"] = "RESOLVED"
            entry["resolution"] = {
                "date": master.isoformat(), "by": "user",
                "record": {"path": rel, "anchor": decision_queue.PRACTICE_ANCHOR},
                "summary": "Stone set the Week %d practice week on My Responses, %s: %d session%s, %s, and %d day%s off"
                           % (week, "%s %d" % (master.strftime("%B"), master.day), len(compiled["sessions"]),
                              "" if len(compiled["sessions"]) == 1 else "s",
                              "no padded practice" if not padded else "%d padded" % padded,
                              len(compiled["days_off"]), "" if len(compiled["days_off"]) == 1 else "s")}
    path = decision_queue.save(root, queue)
    from runtime import responses
    pages = responses.pages_of(season, period, root)
    return "SET", [], lines, [pages.responses, pages.responses_record, path]


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
    schedule, why = instruction_schedule(root, season, week)
    if schedule is None:
        return [why], []
    lines = practices.schedule_lines(schedule)
    found = {w: r for w, r in practices.records(season, root).items() if w < week}
    problems = practices.check_schedule(season, week, schedule["sessions"], schedule["days_off"], root, found)
    status = practices.padded_status(season, week - 1, root, found)
    period = status["first" if week <= practices.FIRST_WEEKS else "last"]
    lines.append("Padded practices before this week: %s used, %s left of the %d" % (
        "unknown" if period["used"] is None else period["used"], "unknown" if period["left"] is None else period["left"],
        period["limit"]))
    return problems, lines


def schedule_command(root, season, week, check=False):
    """(status, problems, lines, written) of --schedule: his applied answer, else the instruction where
    it covers the week (shown and checked, nothing written), else his answer on My Responses."""
    root = Path(root).resolve()
    if answered_schedule(root, season, week) is None and practice_item(root, season, week) is None:
        problems, lines = show_schedule(root, season, week)
        return ("REFUSED" if problems and lines else "NOT SET" if problems else "SET"), problems, lines, []
    return answer(root, season, week, check)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("week", type=int)
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--schedule", action="store_true")
    parser.add_argument("--file", type=Path)
    parser.add_argument("--upload", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    if args.upload is not None:
        if not args.schedule or args.check:
            print("PRACTICE SCHEDULE: an upload is placed with --schedule (and without --check)")
            return 2
        try:
            place_upload(args.root, args.season, {"week": args.week}, args.upload)
        except (OSError, ValueError) as exc:
            print("PRACTICE SCHEDULE: UPLOAD REFUSED  Week %d, %d" % (args.week, args.season))
            print("- %s" % exc)
            return 1
    if args.schedule:
        status, problems, lines, written = schedule_command(args.root, args.season, args.week, args.check)
        print("PRACTICE SCHEDULE: %s  Week %d, %d" % (status, args.week, args.season))
        for line in lines:
            print("  " + line)
        for problem in problems:
            print("- " + problem)
        for path in written:
            print("wrote %s" % Path(path).resolve().relative_to(Path(args.root).resolve()).as_posix())
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
