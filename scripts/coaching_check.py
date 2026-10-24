#!/usr/bin/env python3
"""The weekly check for head-coach changes at every club (rebuild step 5, D2).

  python scripts/coaching_check.py WEEK --season YEAR            # dry run: what is due through WEEK, with each chance
  python scripts/coaching_check.py WEEK --season YEAR --close    # draw it: one private event per week, in week order
  python scripts/coaching_check.py --season YEAR --effective     # write each drawn change the clock has reached

Method: the season's method.json in the data twin of the league's head-coach changes folder
(runtime/league_coaches.py), adopted by the user on October 23, 2026 ("One draw for all 32
(Recommended)"), with the sourced in-season rate table it names. Every club that played in the
week is drawn by the same method, Jacksonville included; nothing the draw reads names the
protagonist.

``--close`` runs after the week's slate closes and before the rebuild that opens the next week
(docs/run_week.md step 8), and in any case before the next week's practice week opens; when the
next week's brief and items are already open, as at the first run after step 5's merge, they do
not count. It draws every
closed week still due through WEEK, in order, each as its own private event
(``SEASON-week-NN-head-coach-check``, the January carousel's packet pattern through the private
client's close_event): so the first run after the method's adoption draws the retroactive Weeks 1
to 5 the user authorized ("Yes, check them (Recommended)") before Week 6's check. A week already
recorded is refused, so a second run draws nothing; a failed commit is never redrawn under the same
event id (the service refuses a changed packet for an id it has closed). A club's draws stop at its
first drawn change. A change takes effect the day after the club's latest closed game when the week
is drawn, so a week drawn late rewrites no closed week.

Each change's dated page, with its event-record line, and its head-coach-change news event (FOR
YOUR INFORMATION) are written once the master clock reaches the effective date: at once by
``--close`` when it already has, otherwise by ``--effective`` at the clock's next move (the
practice-week commit, or a mid-week record). A change at the club the job holder coaches is Khan and
Caldwell's decision, written as the Club Decision in step 6; while those pages do not exist the
check records the draw and stops with a plain message (exit 3), and the career holds there.

Refused: while a Jacksonville game is paused; while the method is not adopted; a week not closed;
a week already recorded; inputs that disagree with the closed games; while the career is held.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import league_coaches as lc  # noqa: E402
from runtime.clean_pages import text_errors  # noqa: E402
from runtime.events import EVENT_META, Event, annual_record_path, load_events, render_record, validate_event  # noqa: E402
from runtime.open_events import Refused as EventRefused, prepare as prepare_event  # noqa: E402
from runtime.packets import canonical  # noqa: E402

HELD = 3


class Refused(Exception):
    """A plain refusal; nothing was drawn or written by the refused step."""


def code_digest():
    """The digest of the check's code: this script and runtime/league_coaches.py."""
    h = hashlib.sha256()
    for path in (Path(__file__).resolve(), Path(lc.__file__).resolve()):
        h.update(path.name.encode() + b"\0" + hashlib.sha256(path.read_bytes()).digest())
    return h.hexdigest()


def stream(ref, pkt):
    """The event's random stream: the January carousel's seed from the private reference and the packet."""
    from runtime.game_runner import _entropy_from_ref
    return random.Random(int.from_bytes(hashlib.sha256(_entropy_from_ref(ref) + canonical(pkt)).digest(), "big"))


def refuse_if_paused(root):
    from scripts.render_career_views import paused_games
    paused = paused_games(root)
    if paused:
        raise Refused("A Jacksonville game is paused (%s); nothing is drawn or written until it closes"
                      % paused[0].relative_to(root).as_posix())


def _write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=1) + "\n", encoding="utf-8")


def annual_record(season, root, pages):
    """The season's annual record as it will stand once the new change ``pages`` ({path: text}) are
    written, refused when it would not be clean (a history page keeps its recorded bytes as a prefix,
    so a line may only sort after them)."""
    events = load_events(root)
    for path, text in pages.items():
        rel = path.relative_to(root).as_posix()
        for raw in EVENT_META.findall(text):
            meta = json.loads(raw)
            validate_event(meta, rel)
            if meta["id"] in events:
                raise Refused("the event %s is already recorded" % meta["id"])
            events[meta["id"]] = Event(rel, meta)
    path = annual_record_path(root, season)
    text = render_record(season, events, root)
    problems = text_errors(path.relative_to(root).as_posix(), text, root)
    if problems:
        raise Refused("the annual record would not be clean with the new head-coach change pages, so nothing was "
                      "written: %s" % "; ".join(problems))
    return path, text


def publish(season, root=ROOT, out=print):
    """Write the folder's index, the page of each drawn change the master clock has reached (with its
    event-record line) and its news event, and the annual record. Everything is checked before
    anything is written. Returns the new change pages."""
    root = Path(root).resolve()
    refuse_if_paused(root)
    pages = lc.pages(season, root)
    for path, text in pages.items():
        problems = text_errors(path.relative_to(root).as_posix(), text, root)
        if problems:
            raise Refused("a head-coach page would not be clean: %s" % "; ".join(problems))
    new = [(record, row) for record, row in lc.effective_changes(season, root)
           if not lc.page_path(season, row, root).is_file()]
    record_path, record_text = annual_record(season, root, {lc.page_path(season, row, root): pages[lc.page_path(
        season, row, root)] for _, row in new}) if new else (None, None)
    news = [lc.news_event(season, record, row, root) + (row,) for record, row in new]
    # Each news record names the folder's index as its source page, so the index is written first and
    # put back as it was if any news record is refused; then the news is raised open (its id is not
    # yet on a page), then the change pages are written, then each news event resolves with its page
    # (runtime/open_events: raise_event, then the result page, then resolve).
    index = lc.folder(season, root) / lc.INDEX
    before = index.read_bytes() if index.is_file() else None
    if index in pages and before != pages[index].encode("utf-8"):
        index.parent.mkdir(parents=True, exist_ok=True)
        index.write_text(pages[index], encoding="utf-8")
    try:
        for event, _, _ in news:
            prepare_event(event, root)        # every news record checked before any is raised
    except EventRefused:
        if before is None:
            index.unlink(missing_ok=True)
        else:
            index.write_bytes(before)
        raise
    for event, _, _ in news:
        lc.raise_event(event, root)
    for path, text in pages.items():
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    for event, resolution, row in news:
        lc.resolve_event(season, event["id"], resolution, root)
        out("%s: head-coach change effective %s; page and news written" % (row["club"], row["effective"]))
    if new and (not record_path.is_file() or record_path.read_text(encoding="utf-8") != record_text):
        record_path.write_text(record_text, encoding="utf-8")
    return [lc.page_path(season, row, root) for _, row in new]


def plan(season, through, root=ROOT):
    """The weeks the close would draw and their inputs (a dry run; nothing written)."""
    method = lc.load_method(season, root)
    if not lc.adopted(method):
        return method, []
    records = dict(lc.checks(season, root))
    games = lc.closed_games(season, root)
    out = []
    for week in lc.due_weeks(season, root, through):
        inputs = lc.week_inputs(season, week, root, method, records, games)
        out.append(inputs)
    return method, out


def close(season, through, root=ROOT, client=None, out=print):
    """Draw every due week through ``through``, in order, one private event each; then write what
    the clock has reached. Returns 0, or HELD when a drawn change holds the career."""
    root = Path(root).resolve()
    method = lc.load_method(season, root)
    if not lc.adopted(method):
        raise Refused("The %d head-coach method is not adopted; nothing is drawn" % season)
    problems = lc.method_errors(season, root) + lc.record_errors(season, root)
    if problems:
        raise Refused("; ".join(problems))
    refuse_if_paused(root)
    hold = lc.career_hold(season, root)
    if hold:
        raise Refused(hold)
    if through in lc.checks(season, root):
        raise Refused("Week %d's head-coach check is already recorded; a second run is refused" % through)
    closed = lc.closed_weeks(season, root)
    if through not in closed:
        raise Refused("Week %d has not closed; its head-coach check runs after the week's slate closes" % through)
    due = lc.due_weeks(season, root, through)
    if not due:
        out("Week %d: no club played a game the check covers; nothing is drawn" % through)
        return 0
    if client is None:
        from runtime.private_client import Client
        client = Client()
    snapshot = client.current_snapshot()
    after_week = max(closed)
    games = lc.closed_games(season, root)
    table = lc.load_table(method, root)
    code = code_digest()
    for week in due:
        records = lc.checks(season, root)
        inputs = lc.week_inputs(season, week, root, method, records, games)
        pkt = lc.packet(method, inputs, snapshot, root, code)
        ref = client.close_event(pkt)
        rows = lc.draw(inputs, table, stream(ref, pkt).random)
        record = lc.build_record(method, inputs, pkt, ref, rows, len(records) + 1, root, after_week, games)
        _write_json(lc.week_path(season, week, root), record)
        changed = [r["club"] for r in record["clubs"] if r["changed"]]
        out("Week %d head-coach check%s: %d clubs drawn; %s" % (
            week, " (retroactive)" if record["retroactive"] else "", len(record["clubs"]),
            "changes at " + ", ".join(changed) if changed else "no change"))
        if lc.career_hold(season, root):
            break
    publish(season, root, out)
    hold = lc.career_hold(season, root)
    if hold:
        out(hold)
        return HELD
    return 0


def main(argv=None, client=None, root=ROOT, out=print):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("week", type=int, nargs="?")
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--close", action="store_true")
    parser.add_argument("--effective", action="store_true")
    args = parser.parse_args(argv)
    root = Path(root).resolve()
    try:
        if args.effective:
            if args.close or args.week is not None:
                raise Refused("--effective takes no week and is run on its own")
            hold = lc.career_hold(args.season, root)
            if hold:
                raise Refused(hold)
            written = publish(args.season, root, out)
            out("HEAD-COACH CHANGES CURRENT: %d new page%s" % (len(written), "" if len(written) == 1 else "s"))
            return 0
        if args.week is None:
            raise Refused("name the week: coaching_check.py WEEK --season YEAR [--close]")
        if args.close:
            return close(args.season, args.week, root, client, out)
        method, weeks = plan(args.season, args.week, root)
        if not lc.adopted(method):
            out("The %d head-coach method is not adopted; nothing is drawn" % args.season)
            return 0
        table = lc.load_table(method, root)
        for inputs in weeks:
            expected = sum(table["rates"][lc.cell(r)]["rate"] for r in inputs["clubs"])
            out("Week %d: %d clubs drawn, expected changes %.4f" % (inputs["week"], len(inputs["clubs"]), expected))
            for r in inputs["clubs"]:
                out("  %-24s game %2d  %s  %-26s %.6f" % (r["club"], r["game"], lc.record_text(r["wins"], r["losses"], r["ties"]),
                                                         lc.cell(r), table["rates"][lc.cell(r)]["rate"]))
            for r in inputs["not_drawn"]:
                out("  %-24s not drawn: %s" % (r["club"], r["reason"]))
        if not weeks:
            out("Nothing is due through Week %d" % args.week)
        return 0
    except (Refused, EventRefused) as exc:
        out("HEAD-COACH CHECK REFUSED: %s" % exc)
        return HELD if lc.career_hold(args.season, root) else 1


if __name__ == "__main__":
    sys.exit(main())
