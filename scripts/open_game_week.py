#!/usr/bin/env python3
"""Open a game week's decisions for Stone (rebuild step 4).

  python scripts/open_game_week.py [--week N] [--check] [--root PATH]

When a Jacksonville game week opens (after the previous game closes, before
the week's first Game Week Briefing), the decision queue (state/
decision_queue.json) gains the week's two items that are Stone's, from the
schedule and his standing instructions:

- the week's game plan (class ``weekly_game_plan``), which holds the week's
  inputs until he sets his Game Plan;
- the week's inactives (class ``game_day_inactives``), waiting on every
  exam the medical entries name before the game (``medical_waits``: a
  reassessment or a projected return), so a list set before them is
  confirmed after them. When a standing
  instruction covers the inactives (his healthy-inactive rule), the item says
  why it is still his (``standing_not_applied``): the rule covers the healthy
  inactives only, and who is out for the game is known only as the week goes
  on; his Game Plan may answer it with "Standing rule";
- the week's practice schedule (class ``practice_plan``, rebuild step 5, C1),
  only when no standing practice instruction covers the week (none is in
  force, the instruction does not set a week like it, as a Thursday game, or
  its schedule for the week does not pass the padded-practice and rest
  limits: scripts/record_practice_week.cover). It is owned by Stone, due
  before the first day of the practice week, holds nothing, and its record is
  a blank block under the reserved heading "Practice week" on the week's My
  Responses page, appended with the item (runtime/responses.append_block); an
  instruction in force that does not cover the week is named on the item with
  why. The regular season only: the postseason's practice rule (one padded
  practice a week) is not built.

The week is the next Jacksonville game not yet closed, unless --week names
another; after the regular season it is the next playoff game the bracket has
set (runtime/game_weeks.py), named for its round ("Wild Card game plan for
Pittsburgh"); while a bye is the open period its one item is Stone's My
Adjustments (class ``bye_adjustments``, holding only the bye's own close, its
due time not set; rebuild step 5, C3), opened with the blank page it asks for,
and the next game's items open only after the bye closes; nothing is opened
twice (an item of the class for the week, open or settled, stays as it is). Each item is raised by
the workflow on the master date, citing the last game's event when its
result page carries one. Nothing is opened while a game is paused. Writing
the briefing (scripts/render_game_week.py) runs this first, so the briefing
lists the items; ``--check`` writes nothing and exits 1 when the open week's
items are missing. Opening an item moves no time and creates no event.
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

from runtime import current_job, decision_queue  # noqa: E402
from runtime.decisions import week_pages  # noqa: E402

QUEUE = decision_queue.QUEUE
JAX = "Jacksonville Jaguars"
PLAN, INACTIVES = "weekly_game_plan", "game_day_inactives"
NOT_APPLIED = ("the rule covers the healthy inactives only; who is out for the game is known only as the week goes "
               "on, so the list is set on the Game Plan")


def _day(value):
    return "%s %d" % (value.strftime("%B"), value.day)


def _held(item, season, week):
    return any(b.get("kind") == "week_inputs" and b.get("season") == season and b.get("week") == week
               for b in item.get("blocks") or ())


def last_game_event(root, wk):
    """(event id, result page) of Jacksonville's last closed game, from its result page's event line."""
    from runtime.events import load_events
    from runtime import game_weeks
    games = wk.club_games(JAX) + wk.post_receipts      # a playoff game is the last game after the season
    if not games:
        return None, None
    last = max(games, key=lambda r: int(r["week"]))
    postseason = game_weeks.is_postseason(wk.paths, last["week"])
    page = wk.paths.game_report(int(last["week"]), postseason)
    if not page.is_file():
        return None, None
    rel = page.relative_to(wk.root).as_posix()
    played = next((g["date"] for g in game_weeks.club_games(wk.paths, JAX) if g["week"] == int(last["week"])),
                  None)
    owned = [e for e in load_events(wk.root).values() if e.owner == rel and e.data.get("kind", "football") == "football"]
    found = [e for e in owned if e.data["date"] == played] or owned
    return (found[-1].id if found else None), rel


def medical_waits(wk):
    """What the week's inactives wait on: each exam the roster record's medical entries name between
    today and the game day (runtime/season_summary.medical_entry: a reassessment or a projected
    return, on or after today and before the game date), one wait per player and date, oldest first.
    A projected return alone under an independent hold has no club owner (the independent process
    releases it). A note not in the medical format is left to the check, which names it."""
    from runtime import roster as roster_record, season_summary as summary
    game_day = date.fromisoformat(wk.game["date"])
    out = []
    for row in summary.held(roster_record.load(wk.paths.roster)):
        try:
            entry = summary.medical_entry(row, wk.master)
        except ValueError:
            continue
        if entry is None:
            continue
        on = {}
        for d in entry["reviews"]:
            if wk.master <= d < game_day:
                on.setdefault(d, []).append("reassessment")
        if entry["projected"] and wk.master <= entry["projected"] < game_day:
            on.setdefault(entry["projected"], []).append("projected return")
        independent = entry["instruction"] == summary.KINDS["Independent medical hold"]
        for d, what in on.items():
            owner = None if independent and what == ["projected return"] else "medical_staff"
            out.append({"what": "%s's %s" % (row["name"], " and ".join(what)), "owner": owner, "date": d.isoformat()})
    return sorted(out, key=lambda w: (w["date"], w["what"]))


def items_for(root, wk):
    """The week's two items for Stone, as they open."""
    season, week, game = wk.season, wk.game["week"], wk.game
    holder = wk.job.get("holder")
    block = decision_queue.event("week_inputs", season, week)
    place = wk.place(wk.opponent)
    when = date.fromisoformat(game["date"])
    kick = wk.views.kickoff(game["kickoff_et"])
    event, source = last_game_event(root, wk)
    raised = {"date": wk.master.isoformat(), "by": "workflow", **({"event": event} if event else {})}
    sources = [{"path": source}] if source else []
    pages = week_pages(season, week, wk.root, postseason=wk.postseason)
    name = wk.label()       # "Week 6", or a playoff game's round ("Wild Card")
    plan = {"id": "%d-w%02d-game-plan" % (season, week), "title": "%s game plan for %s" % (name, place),
            "class": PLAN, "owner": holder, "authority_rows": list(decision_queue.CLASSES[PLAN].rows),
            "question": "Stone's %s plan for %s, from which the call sheet is frozen before the game."
                        % (name, place),
            "raised": raised, "status": "OPEN", "waits_on": [],
            "deadline": {"date": game["date"], "label": "before the %s call sheet is frozen and the %s "
                         "inputs are built; kickoff %s, %s" % (name, name, _day(when), kick), "before": block},
            "blocks": [block], "fallback": None, "can_continue": None,
            "record": {"path": pages.readme.relative_to(wk.root).as_posix()}, "sources": sources,
            "resolution": None}
    inactives = {"id": "%d-w%02d-inactives" % (season, week), "title": "%s inactives" % name,
                 "class": INACTIVES, "owner": holder, "authority_rows": list(decision_queue.CLASSES[INACTIVES].rows),
                 "question": "Stone's %s inactives for %s." % (name, place),
                 "raised": dict(raised), "status": "OPEN", "waits_on": medical_waits(wk),
                 "deadline": {"date": game["date"], "label": "before the %s inputs are built" % name,
                              "before": dict(block)},
                 "blocks": [dict(block)]}
    covering = [i for i in current_job.instructions(wk.job) if INACTIVES in (i.get("closes") or ())]
    if covering:
        inactives["standing_not_applied"] = [{"instruction": i["id"], "reason": NOT_APPLIED} for i in covering]
    inactives.update({"fallback": None, "can_continue": None,
                      "record": {"path": wk.paths.record("depth_chart.md").relative_to(wk.root).as_posix()},
                      "sources": [dict(s) for s in sources], "resolution": None})
    practice = practice_item_for(root, wk)
    return [plan, inactives] + ([practice] if practice else [])


PRACTICE = "practice_plan"


def practice_item_for(root, wk):
    """The week's practice ask, when no standing practice instruction covers it (rebuild step 5, C1),
    or None. The regular season only."""
    from runtime import open_events, practices
    from runtime.decision_queue import PRACTICE_ANCHOR
    from runtime import season_summary as summary
    from scripts import record_practice_week
    if wk.postseason:
        return None
    season, week = wk.season, int(wk.game["week"])
    schedule, why = record_practice_week.cover(root, season, week)
    if schedule is not None:
        return None
    holder = wk.job.get("holder")
    first, _ = practices.week_span(season, week, wk.root)
    listed = summary.first_practice(wk.cv.scheduled, week, wk.master)
    start = listed or first
    name = wk.label()
    pages = week_pages(season, week, wk.root, postseason=wk.postseason)
    item = {"id": "%d-w%02d-practice-week" % (season, week), "title": "%s practice week" % name,
            "class": PRACTICE, "subject": "practice_schedule", "owner": holder,
            "authority_rows": list(decision_queue.CLASSES[PRACTICE].rows),
            "question": "Stone's %s practice schedule: each day's work, what the players wear and who attends, and "
                        "the players' days off, checked against the padded-practice and rest limits before any session"
                        % name,
            "raised": {"date": wk.master.isoformat(), "by": "workflow"}, "status": "OPEN", "waits_on": [],
            "deadline": {"date": start.isoformat(), "at": open_events.iso(open_events.et(start)),
                         "label": "before the %s practice week, which may begin %s, %s"
                                  % (name, start.strftime("%A"), _day(start))},
            "blocks": [], "fallback": None, "can_continue": None,
            "record": {"path": pages.responses.relative_to(wk.root).as_posix(), "anchor": PRACTICE_ANCHOR},
            "sources": [{"path": wk.paths.record("calendar.md").relative_to(wk.root).as_posix()}],
            "resolution": None}
    in_force = current_job.practice_instruction(wk.job, season)
    if in_force is not None:
        item["standing_not_applied"] = [{"instruction": in_force["id"], "reason": why}]
    return item


BYE = "bye_adjustments"


def bye_item_for(root, wk):
    """The open bye's one item (rebuild step 5, C3): Stone's My Adjustments, holding only the bye's own
    close, its due time not set (the bye's work dates are his own choice on the page it asks for)."""
    from runtime import bye_week
    from runtime.decisions import bye_pages
    week = int(wk.period["bye"])
    pages = bye_pages(wk.season, week, wk.root)
    first, last = bye_week.dates(wk.season, week, wk.root)
    before, _ = bye_week.around(wk.season, week, wk.root)
    raised = {"date": wk.master.isoformat(), "by": "workflow"}
    sources = []
    if before is not None:
        report = wk.paths.game_report(int(before["week"]))
        if report.is_file():
            sources.append({"path": report.relative_to(wk.root).as_posix()})
    return {"id": bye_week.bye_item_id(wk.season, week), "title": "Week %d bye adjustments" % week, "class": BYE,
            "owner": wk.job.get("holder"), "authority_rows": list(decision_queue.CLASSES[BYE].rows),
            "question": "Stone's Week %d bye adjustments, %s %d to %s%d: what to keep, correct, test, remove or "
                        "defer on offense, defense and special teams, the eligible role and depth decisions, and the "
                        "bye's work and the players' four consecutive days off" % (
                            week, first.strftime("%B"), first.day,
                            "" if last.month == first.month else last.strftime("%B") + " ", last.day),
            "raised": raised, "status": "OPEN", "waits_on": [], "deadline": None,
            "blocks": [decision_queue.event("bye_close", wk.season, week)], "fallback": None, "can_continue": None,
            "record": {"path": pages.adjustments.relative_to(wk.root).as_posix()}, "sources": sources,
            "resolution": None}


def missing(root=ROOT, week=None):
    """The open week's items not yet in the queue (none for a closed week or a paused game). While the
    bye is the open period it is the bye's one adjustments item, and the next game's items wait for
    the bye's close; a bye opens no game plan, inactives or practice item."""
    from scripts.render_career_views import paused_games
    from scripts.render_game_week import Week
    root = Path(root).resolve()
    if paused_games(root):
        return [], None
    wk = Week(root, week)
    if wk.game is None and (wk.period or {}).get("bye") is not None:
        from runtime import bye_week
        queue = decision_queue.load(root)
        if bye_week.bye_item(queue, wk.season, int(wk.period["bye"])) is not None:
            return [], wk
        return [bye_item_for(root, wk)], wk
    if wk.game is None or wk.closed:
        return [], wk
    queue = decision_queue.load(root)
    have = {i.get("class") for i in queue["items"] if _held(i, wk.season, wk.game["week"])}
    ids = {i.get("id") for i in queue["items"]}
    return [i for i in items_for(root, wk) if i["class"] not in have and i["id"] not in ids], wk


def open_items(root=ROOT, week=None):
    """Open the week's missing items; returns their ids. A practice ask's blank "Practice week" block
    is appended to the week's My Responses page with it (runtime/responses.append_block)."""
    from scripts.apply_game_plan import write_like
    root = Path(root).resolve()
    new, wk = missing(root, week)
    if not new:
        return []
    path = root / QUEUE
    queue = json.loads(path.read_text(encoding="utf-8"))
    for item in new:
        if item["class"] == BYE:
            # The page the item asks for exists with it: a blank My Adjustments (scripts/render_bye_week.py).
            from scripts import render_bye_week
            bye = render_bye_week.Bye(root, int(wk.period["bye"]))
            if not bye.pages.adjustments.is_file():
                bye.pages.folder.mkdir(parents=True, exist_ok=True)
                bye.pages.adjustments.write_text(render_bye_week.adjustments_page(bye), encoding="utf-8")
        if item["class"] == PRACTICE:
            from runtime import responses
            from runtime.decisions import PRACTICE_WEEK
            responses.append_block({"week": int(wk.game["week"])}, PRACTICE_WEEK, item, root, wk.season)
    queue["items"] += new
    write_like(path, queue)
    return [i["id"] for i in new]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--week", type=int)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    if args.check:
        new, _ = missing(args.root, args.week)
        print("\n".join("Decision not yet opened: %s" % i["title"] for i in new) or "GAME WEEK DECISIONS OPEN")
        return 1 if new else 0
    opened = open_items(args.root, args.week)
    print("\n".join("opened %s" % i for i in opened) or "game week decisions: nothing to open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
