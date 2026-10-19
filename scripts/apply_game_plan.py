#!/usr/bin/env python3
"""Apply Stone's checked Game Plan (rebuild step 4).

  python scripts/apply_game_plan.py WEEK --season YEAR [--file PATH] [--root PATH]

Runs scripts/check_game_plan.py first and refuses (exit 1) until the page is
complete. Then it converts the page into exactly the records the game path
already reads, and nothing else:

- the frozen call sheet, ``SeasonPaths(YEAR).call_sheet(WEEK)``, written as
  every frozen sheet is (indent 1, a final newline), valid under the existing
  validators; build_week_inputs.py reads it unchanged;
- the game depth chart's ``game_day_inactives`` and any order or role change,
  in both copies (the game chart and the working chart), with one dated entry
  in the depth chart's update log naming the page as its source;
- the decision-queue items the plan settles (the week's game plan and
  inactives, Stone's), marked RESOLVED by the user with the page as their
  record.

Stone's page stays as the record of his decision; the frozen sheet's
defensive rows cite its lines. The club pages, the career views and the week
index are rebuilt from the records afterwards. The Game Week Briefing is not
touched. Nothing is drawn, and the clock does not move.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import game_plan  # noqa: E402
from scripts.check_game_plan import Plan, check, place_upload  # noqa: E402

PLAN_CLASSES = ("weekly_game_plan", "game_day_inactives")


def long_date(value):
    return "%s %d, %d" % (value.strftime("%B"), value.day, value.year)


def write_like(path, data):
    """Write ``data`` to a JSON record in the layout the record already has (its indent and
    whether it escapes non-ASCII), so a change shows only what changed."""
    raw = path.read_text(encoding="utf-8")
    old = json.loads(raw)
    layout = next(((i, a) for i in (1, 2) for a in (False, True)
                   if json.dumps(old, indent=i, ensure_ascii=a) + "\n" == raw), (1, False))
    path.write_text(json.dumps(data, indent=layout[0], ensure_ascii=layout[1]) + "\n", encoding="utf-8")


def inactive_note(plan, players):
    value = plan.choices.get("inactives") or {}
    reasons = value.get("reasons") or {} if isinstance(value, dict) else {}
    g = plan.game
    where = ("at %s" if g["away"] == "Jacksonville Jaguars" else "against %s") % (
        g["home"] if g["away"] == "Jacksonville Jaguars" else g["away"]).rsplit(" ", 1)[0]
    listed = "; ".join("%s (%s)" % (p, reasons[p]) if p in reasons else p for p in players)
    return ("%d of the %d are inactive for Week %d %s (%d dress), set by Stone on %s on his Week %d Game Plan: %s."
            % (len(players), len(plan.active()), plan.week, where, len(plan.active()) - len(players),
               long_date(plan.master), plan.week, listed))


def apply_records(plan, sheet, players, resolve_queue=True):
    """Write the call sheet, the chart's inactives and order changes with their log entry, and settle
    the queue items; returns the paths written."""
    written = []
    path = plan.paths.call_sheet(plan.week)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(game_plan.sheet_bytes(sheet))
    written.append(path)
    page = plan.rel(plan.pages.plan)
    depth = plan.choices.get("depth") if isinstance(plan.choices.get("depth"), dict) else {}
    changes = []
    working_path = plan.paths.record("offseason/depth_chart_working.json")
    charts = [plan.paths.depth_chart] + ([working_path] if working_path.is_file() else [])
    for chart_path in charts:
        chart = json.loads(chart_path.read_text(encoding="utf-8"))
        for group, order in (depth.get("orders") or {}).items():
            if chart.get("depth", {}).get(group) != order:
                chart["depth"][group] = list(order)
                if chart_path == plan.paths.depth_chart:
                    changes.append("%s order: %s" % (group, ", ".join(order)))
        for role, player in (depth.get("roles") or {}).items():
            roles = chart.setdefault("roles", {})
            holders = [p for p, r in roles.items() if role in (r or ())]
            if holders != [player]:
                for p in holders:
                    roles[p] = [r for r in roles[p] if r != role]
                    if not roles[p]:
                        del roles[p]
                roles.setdefault(player, []).append(role)
                if chart_path == plan.paths.depth_chart:
                    changes.append("%s: %s" % (role.replace("_", " "), player))
        if players is not None:
            chart["game_day_inactives"] = {"week": plan.week, "players": list(players),
                                           "note": inactive_note(plan, players)}
        write_like(chart_path, chart)
        written.append(chart_path)
    log_path = plan.paths.record("team/depth_chart/update_log.json")
    log = json.loads(log_path.read_text(encoding="utf-8"))
    change = "Week %d inactives: %s." % (plan.week, ", ".join(players)) if players is not None else ""
    if changes:
        change += " " + "; ".join(changes) + "."
    else:
        change += " No order or role change."
    log["entries"].append({"date": long_date(plan.master), "recorded": plan.master.isoformat(),
                           "event": "Week %d: Stone's Game Plan" % plan.week, "change": change.strip(),
                           "sources": [{"label": "Week %d Game Plan" % plan.week, "page": page}]})
    write_like(log_path, log)
    written.append(log_path)
    if resolve_queue:
        written += settle_queue(plan, page)
    return written


def settle_queue(plan, page):
    from runtime import decision_queue
    queue_path = plan.root / decision_queue.QUEUE
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    holder = plan.job.get("holder")
    settled = 0
    for item in queue["items"]:
        held = any(b.get("kind") == "week_inputs" and b.get("season") == plan.season and b.get("week") == plan.week
                   for b in item.get("blocks") or ())
        if item.get("status") == "OPEN" and held and item.get("owner") == holder and item.get("class") in PLAN_CLASSES:
            what = "the game plan" if item["class"] == "weekly_game_plan" else "the inactives"
            item["status"] = "RESOLVED"
            item["resolution"] = {"date": plan.master.isoformat(), "by": "user", "record": {"path": page},
                                  "summary": "Stone set %s on his Week %d Game Plan, checked and applied %s"
                                             % (what, plan.week, long_date(plan.master))}
            settled += 1
    if not settled:
        return []
    write_like(queue_path, queue)
    return [queue_path]


def rebuild(root, week):
    """The pages built from the records the plan changed."""
    from scripts import render_career_views, render_club_pages, render_game_week
    render_club_pages.write(root)
    render_career_views.write(root)
    render_game_week.write_index(root, week)


def apply(root, season, week, rebuild_pages=True):
    problems, notes, plan = check(root, season, week)
    if problems:
        return problems, []
    sheet = plan.sheet()
    written = apply_records(plan, sheet, plan.inactives())
    if rebuild_pages:
        rebuild(plan.root, week)
    return [], written


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("week", type=int)
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--file", type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    if args.file is not None:
        place_upload(args.root, args.season, args.week, args.file)
    problems, written = apply(args.root, args.season, args.week)
    if problems:
        print("GAME PLAN: NOT APPLIED")
        for problem in problems:
            print("- " + problem)
        return 1
    root = Path(args.root).resolve()
    print("GAME PLAN: APPLIED  Week %d, %d" % (args.week, args.season))
    for path in written:
        print("wrote %s" % Path(path).relative_to(root).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
