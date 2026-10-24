#!/usr/bin/env python3
"""Apply Stone's My Adjustments for the bye (rebuild step 5, C3; docs/bye_week.md, section 5, item 4).

  python scripts/apply_bye_adjustments.py WEEK --season YEAR [--root PATH]

Once the page passes its check (scripts/check_bye_adjustments.py, with "I have
finished the bye-week decisions: Yes"), this records it, in one run:

- the applied record (``applied_adjustments.json`` in the bye week's data
  folder): the page's digest and date and the choices compiled from it,
  among them the bye's work and the players' days off, which are the bye's
  schedule (runtime/bye_week.applied_schedule), so a player session of the
  bye is recorded as required work only once the adjustments that name it
  are applied (scripts/record_practice_week.py);
- the bye's adjustments item resolved by the user, with the page as its
  record;
- only the immediate authorized role or depth changes, through the game-day
  change's chart writers (scripts/apply_game_plan.write_charts and
  log_change), with one update-log entry citing My Adjustments.

His tests, his ideas for the next opponent and his durable coaching changes
stay on the applied record as his words: the next game's Game Plan chooses
what goes onto its sheet. A recommendation to the general manager is recorded
as his recommendation, never executed; it reaches the general manager as an
event only through scripts/raise_event.py, the one way to record one. The
applied page stays as written. Refused while a game is paused, when the bye
is not open, while the check finds a problem, or once applied (a second run
changes nothing). Nothing here moves the clock or creates an event.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import bye_week, decision_queue  # noqa: E402


def summary(compiled, applied_on, week):
    """The item's resolution in football words."""
    def area(name, value):
        if value["no_change"]:
            return "%s no change" % name
        kinds = []
        for part in value["parts"]:
            if part["kind"] not in kinds:
                kinds.append(part["kind"])
        return "%s %s" % (name, " and ".join(kinds))
    days = [d["date"] for d in compiled["schedule"]["days_off"]]
    from scripts.render_bye_week import day
    off = ("the players off %s to %s" % (day(days[0], False), day(days[-1], False))) if days else "no day off named"
    return ("Stone's Week %d bye adjustments applied on My Adjustments, %s: %s; %s; %s; %s; %s" % (
        week, day(applied_on, False), area("offense", compiled["areas"]["offense"]),
        area("defense", compiled["areas"]["defense"]), area("special teams", compiled["areas"]["special_teams"]),
        "no role or depth change" if compiled["roles"] == "none" else "a role or depth change", off))


def apply(root, season, week):
    """(problems, notes, written)."""
    from scripts import check_bye_adjustments, render_bye_week
    from scripts.render_career_views import paused_games
    root = Path(root).resolve()
    if paused_games(root):
        return ["A Jacksonville game is paused; nothing is recorded until it is finished"], [], []
    if bye_week.applied_record(season, week, root) is not None:
        return [], ["My Adjustments is already applied; nothing changes"], []
    problems, notes, compiled = check_bye_adjustments.check(root, season, week)
    if problems:
        return problems, notes, []
    bye = render_bye_week.Bye(root, week)
    queue = decision_queue.load(root)
    item = bye_week.bye_item(queue, season, week)
    if item is None or item.get("status") != "OPEN":
        return ["The Week %d bye's adjustments item is not open" % week], notes, []
    pages = bye.pages
    rel = pages.adjustments.relative_to(root).as_posix()
    text = pages.adjustments.read_text(encoding="utf-8")
    written = []
    changes = []
    if compiled["roles"] != "none":
        from scripts.apply_game_plan import log_change, long_date, write_charts
        from scripts.check_game_plan import changed_chart
        depth = compiled["roles"]
        _, changes = changed_chart(json.loads(bye.paths.depth_chart.read_text(encoding="utf-8")), depth)
        written += write_charts(bye.paths, lambda chart, working: changed_chart(chart, depth)[0])
        written.append(log_change(bye.paths, {
            "date": long_date(bye.master), "recorded": bye.master.isoformat(),
            "event": "Week %d bye: Stone's role and depth decisions" % week,
            "change": "Week %d bye adjustments, applied immediately: %s." % (week, "; ".join(changes)),
            "sources": [{"label": "Week %d My Adjustments" % week,
                         "page": "%s#5-personnel-and-medical-contingencies" % rel}]}))
    record = {"schema": bye_week.APPLIED_SCHEMA, "about": bye_week.APPLIED_ABOUT, "season": season, "week": week,
              "date": bye.master.isoformat(), "page": rel, "page_sha256": bye_week.page_sha256(text),
              "choices": compiled, "chart_changes": changes}
    pages.applied.parent.mkdir(parents=True, exist_ok=True)
    pages.applied.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    written.append(pages.applied)
    for entry in queue["items"]:
        if entry.get("id") == item["id"]:
            entry["status"] = "RESOLVED"
            entry["resolution"] = {"date": bye.master.isoformat(), "by": "user", "record": {"path": rel},
                                   "summary": summary(compiled, bye.master, week)}
    written.append(decision_queue.save(root, queue))
    written += render_bye_week.write_index(root)
    if compiled.get("recommendation") is not None:
        notes.append("the recommendation to the general manager is recorded as Stone's; record it as the general "
                     "manager's question with scripts/raise_event.py, citing My Adjustments section 5")
    return [], notes, written


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("week", type=int)
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    problems, notes, written = apply(args.root, args.season, args.week)
    if problems:
        print("BYE ADJUSTMENTS: NOT APPLIED  Week %d, %d" % (args.week, args.season))
        for problem in problems:
            print("- " + problem)
        return 1
    print("BYE ADJUSTMENTS: %s  Week %d, %d" % ("APPLIED" if written else "UNCHANGED", args.week, args.season))
    for path in written:
        print("wrote %s" % Path(path).resolve().relative_to(Path(args.root).resolve()).as_posix())
    for note in notes:
        print("  note: " + note)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
