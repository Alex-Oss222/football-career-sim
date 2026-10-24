#!/usr/bin/env python3
"""Close the bye week (rebuild step 5, C3; docs/bye_week.md, section 5, items 5 and 6).

  python scripts/close_bye_week.py WEEK --season YEAR [--check] [--root PATH]

The bye closes on its own Sunday, after the other clubs' games of the week
have closed and the staff's Bye Week Report is written. This refuses while
Stone's bye adjustments are open or anything holds the bye's close (the
decision queue's ``bye_close``), before the bye's Sunday, before every game of
the week's slate has closed, without the bye's practice and rest record, or
with a report that does not hold to the records (runtime/bye_week.
report_errors). It then writes the bye's close event-record line at the end of
the report (its id the bye's Sunday and the week, its closure the next in the
season's order) and rebuilds the year's Record.md and the bye's index. It
never makes a Jacksonville input, receipt, score or box score: the club's
record is unchanged through the bye. The runner moves Document 5's checkpoint
in the same commit, as after a game; the next game's briefing and items then
open (its first notices counted from the bye's last review). --check writes
nothing.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import bye_week, decision_queue, practices  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402


def close_line(root, season, week):
    """The bye's close event: closed on its Sunday, summarized from the records."""
    from runtime.events import load_events
    from scripts.render_bye_week import day
    root = Path(root).resolve()
    first, last = bye_week.dates(season, week, root)
    applied = bye_week.applied_record(season, week, root)
    record = bye_week.record_words(season, week, root)
    log = practices.load(season, week, root) or {}
    padded = practices.week_padded(log) if log else None
    off = [d["date"] for d in log.get("days_off") or () if d.get("players") == "all"]
    from runtime import open_events
    results, _ = open_events.period_events(season, {"bye": week}, root)
    parts = ["Jacksonville's Week %d bye: no game, the record unchanged at %s" % (week, record)]
    parts.append("Stone's bye adjustments applied %s" % day(applied["date"], False) if applied
                 else "no bye adjustments applied")
    if off:
        a, b = min(off), max(off)
        parts.append("the players off %s to %s" % (day(a, False), day(b, False) if a[:7] != b[:7] else str(int(b[8:]))))
    parts.append("no padded practice" if padded == 0 else "%d padded practice%s" % (padded, "" if padded == 1 else "s")
                 if padded else "the padded count not recorded")
    if results:
        parts.append("%d other matter%s resolved in the bye" % (len(results), "" if len(results) == 1 else "s"))
    parts.append("the league's other Week %d games closed" % week)
    sequence = max([e.data["closure"]["sequence"] for e in load_events(root).values() if "closure" in e.data] or [0])
    return {"closure": {"checkpoint": "Canonical update - %s - Week %d bye closed" % (day(last), week),
                        "sequence": sequence + 1, "through": last.isoformat()},
            "date": first.isoformat(), "date_end": last.isoformat(), "id": bye_week.close_id(season, week, root),
            "season": season, "status": "closed", "summary": "; ".join(parts) + "."}


def refusals(root, season, week):
    """Why the bye cannot close now; [] when it can."""
    from runtime.player_bios import master_date
    from runtime.week_inputs import receipt_name
    from scripts.render_career_views import paused_games
    root = Path(root).resolve()
    paths = SeasonPaths(season, root)
    if week not in bye_week.byes(season, root):
        return ["Week %d of %d is not Jacksonville's bye" % (week, season)]
    if bye_week.bye_closed(paths, root, week):
        return ["The Week %d bye has closed; its report stays as written" % week]
    if paused_games(root):
        return ["A Jacksonville game is paused; nothing is recorded until it is finished"]
    out = []
    item = bye_week.bye_item(decision_queue.load(root), season, week)
    if item is None or item.get("status") == "OPEN":
        out.append("Stone's Week %d bye adjustments are not applied; the bye closes only once he has answered "
                   "My Adjustments" % week)
    held = decision_queue.blocking_errors([decision_queue.event("bye_close", season, week)], root)
    out += held
    _, last = bye_week.dates(season, week, root)
    if master_date(root) < last:
        out.append("The bye closes on its Sunday, %s; the date is %s" % (
            bye_week.long_day(last, True).split(", ", 1)[1], bye_week.long_day(master_date(root), True)))
    missing = [g for g in paths.regular_games() if int(g["week"]) == week
               and not (paths.receipts / receipt_name(g)).is_file()]
    if missing:
        out.append("The league's Week %d slate has not closed (%d game%s still to close)" % (
            week, len(missing), "" if len(missing) == 1 else "s"))
    if practices.load(season, week, root) is None:
        out.append("The bye's practice and rest record is not written (scripts/record_practice_week.py)")
    out += bye_week.report_errors(season, week, root)
    return out


def close(root, season, week, check=False):
    """(problems, written)."""
    root = Path(root).resolve()
    problems = refusals(root, season, week)
    if problems or check:
        return problems, []
    from runtime import decisions
    from runtime.clean_pages import text_errors
    from runtime.events import annual_record_path, load_events, render_record
    report = decisions.bye_pages(season, week, root).report
    line = close_line(root, season, week)
    text = report.read_text(encoding="utf-8")
    text = text.rstrip("\n") + "\n\n<!-- event-record: %s -->\n" % json.dumps(line, sort_keys=True, ensure_ascii=False)
    report.write_text(text, encoding="utf-8")
    events = load_events(root)
    record_path = annual_record_path(root, season)
    expected = render_record(season, events, root)
    unclean = text_errors(record_path.relative_to(root).as_posix(), expected, root)
    if unclean:
        raise ValueError("; ".join(unclean))
    record_path.write_text(expected, encoding="utf-8")
    from scripts import render_bye_week
    written = [report, record_path] + render_bye_week.write_index(root, render_bye_week.Bye(root, week))
    return [], written


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("week", type=int)
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    problems, written = close(args.root, args.season, args.week, args.check)
    if problems:
        print("BYE CLOSE: REFUSED  Week %d, %d" % (args.week, args.season))
        for problem in problems:
            print("- " + problem)
        return 1
    print("BYE CLOSE: %s  Week %d, %d" % ("READY" if args.check else "CLOSED", args.week, args.season))
    for path in written:
        print("wrote %s" % Path(path).resolve().relative_to(Path(args.root).resolve()).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
