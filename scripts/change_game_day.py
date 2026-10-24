#!/usr/bin/env python3
"""Depth or inactives after the Game Plan is set (rebuild step 5, C2).

  python scripts/change_game_day.py WEEK --season YEAR --needed [--root PATH]
  python scripts/change_game_day.py WEEK --season YEAR --check [--root PATH]

Once a week's Game Plan is applied its call sheet is frozen, but the week can
still change before the game is built: a dated medical entry puts a player the
plan dresses out for the game, or a roster transaction takes a role holder off
the active roster. The plan stays as it was set; Stone answers the change on the
week's My Responses page, under the reserved heading "Depth and inactives
change" (the second that week "Depth and inactives change 2", and so on),
using the Game Plan's own line forms for the inactives and the depth.

--needed runs after every dated medical entry or roster transaction recorded
after the week's apply (the runner calls it in that commit; a transaction's
apply calls it). When the inactives as set no longer stand (a player who
dresses is out for the game, an inactive has left the active roster, the count
no longer matches the active roster) or a role holder on the chart does not
dress or has left the active roster, it opens one ``depth_and_roles`` item owned
by Stone, due at kickoff, its ``deadline.before`` the week's inputs, holding the
week's inputs and close: the build then holds on a named item, never on an
internal error of the inputs. The item's record is a blank block appended to
My Responses under the next reserved heading (the page is created with only
that block when the week has none). A change already open is not opened twice.
Nothing opens before the plan is applied (the Game Plan itself sets the list),
or once the week's inputs are built, the game is paused or played.

--check exits 1 while a change is open and unanswered (the runner applies it
before building the inputs), and 0 otherwise.

``record_change`` is the writer: from the change's own choices (the inactives
and depth in the Game Plan's forms) it runs the Game Plan's checks
(scripts/check_game_plan.inactive_problems, depth_problems and role_problems,
and the frozen sheet's personnel and named-player variations,
offense_problems) against the chart as applied (``Plan`` with a layered chart
and the inactive list as it stands), refuses a change once the week's inputs
are built, the game is paused or played (``closed_for_changes``), and then
writes both chart copies and one update-log entry citing My Responses
(scripts/apply_game_plan.write_charts and log_change), the week's inactives
record (the current players, the list as set kept, a dated ``changes`` list)
and the week's game-day change record (``game_day_changes.json``), and resolves
the item by the user with the block as its record. It never touches the call
sheet, the applied plan record or the Game Plan; the Game Plan is not applied
again once a change is recorded (scripts/apply_game_plan.apply). "Carry Week
N" on a later Game Plan carries the list as it stood at the game. Reading the
block from My Responses comes with the My Responses page (step 5, builder C,
second wave). Nothing here moves the clock or creates an event.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import decision_queue, decisions, game_plan, responses  # noqa: E402
from runtime import roster as roster_record  # noqa: E402
from runtime.week_pages import kickoff  # noqa: E402
from scripts.apply_game_plan import log_change, long_date, opponent_words, write_charts, write_like  # noqa: E402
from scripts.check_game_plan import (Plan, changed_chart, closed_for_changes, depth_problems,  # noqa: E402
                                     inactive_problems, offense_problems, role_problems)

CLASS = "depth_and_roles"
ET = ZoneInfo("America/New_York")
CHANGES_ABOUT = ("Stone's depth or inactives changes of the week made on My Responses after its Game Plan was "
                 "applied, in order: each change's heading and queue item, its block's digest, the inactives before "
                 "and after, the depth changes and the chart's changes in words. Written only by "
                 "scripts/change_game_day.py; the call sheet, the applied plan record and the Game Plan never change.")


def anchor(heading):
    """The page anchor of a heading (as the repository's link check reads one)."""
    return re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")


def week_items(queue, season, week, holder):
    """The week's game-day change items, open or settled, in order."""
    return [i for i in queue["items"] if decision_queue.game_day_item(i, holder)
            and ((i.get("deadline") or {}).get("before") or {}).get("season") == season
            and ((i.get("deadline") or {}).get("before") or {}).get("week") == week]


def kickoff_at(game):
    """The game's kickoff as an ISO datetime with its ET offset."""
    hour, minute = (int(p) for p in game["kickoff_et"].split(":"))
    day = dt.date.fromisoformat(game["date"])
    return dt.datetime(day.year, day.month, day.day, hour, minute, tzinfo=ET).isoformat()


def append_block(period, heading, item, root, season):
    """A blank block under ``heading`` on the period's My Responses page, bound to ``item``, through
    the one writer of that page (runtime/responses.append_block, builder A3)."""
    return responses.append_block(period, heading, item, root, season)


# ------------------------------------------------------------------ what the week needs
def current_inactives(plan):
    """The week's inactives as they stand (its inactives record, a change included), or None."""
    record = game_plan.applied_record(plan.pages.inactives)
    return None if record is None else list(record.get("players") or [])


def needs(root, season, week):
    """(reasons, sources, why none): what makes a change of the inactives or depth needed for the week,
    in the Game Plan check's words, with the records the reasons rest on. No reason before the week's
    plan is applied or once the week cannot change."""
    root = Path(root).resolve()
    plan = Plan(root, season, week)
    if plan.game is None:
        return [], [], "%s: Jacksonville has no game" % plan.label()
    refused = closed_for_changes(root, season, week)
    if refused:
        return [], [], refused
    if plan.applied is None:
        return [], [], "%s: the Game Plan is not applied yet; it sets the inactives itself" % plan.label()
    players = current_inactives(plan)
    if players is None:
        return [], [], "%s: the week's inactives are not on file" % plan.label()
    plan = Plan(root, season, week, inactives=players, choices={"depth": "none"})
    reasons = inactive_problems(plan)
    if not reasons:
        reasons += role_problems(plan)
    active = set(plan.active())
    rows = {p["name"]: p for p in roster_record.players(plan.roster)}
    for role_label, role in game_plan.ROLES.items():
        for player, held in sorted((plan.chart.get("roles") or {}).items()):
            if role in (held or ()) and player not in active:
                reasons.append("Depth/role changes: %s holds the %s role on the depth chart and is no longer on the "
                               "active roster; give the role to a player who dresses (%s: his name)"
                               % (player, role_label, role_label))
    sources = [{"path": plan.rel(plan.pages.plan)}]
    outs, _ = plan.outs()
    for name in sorted(set(outs) | {p for p in players if p not in active} |
                       {p for p, held in (plan.chart.get("roles") or {}).items() if p not in active}):
        row = rows.get(name) or {}
        path = (row.get("sources") or {}).get("availability" if name in outs else "status")
        if path and {"path": path} not in sources and any(name in r for r in reasons):
            sources.append({"path": path})
    return reasons, sources, None


def open_item(root, season, week):
    """Open the week's game-day change when one is needed and none is open; returns (item or None,
    message)."""
    root = Path(root).resolve()
    reasons, sources, why = needs(root, season, week)
    if why:
        return None, why
    plan = Plan(root, season, week)
    if not reasons:
        return None, "%s: no change is needed; the inactives and depth as set stand" % plan.label()
    queue_path = root / decision_queue.QUEUE
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    holder = plan.job.get("holder")
    mine = week_items(queue, season, week, holder)
    still = [i for i in mine if i.get("status") == "OPEN"]
    if still:
        return still[0], "%s: the change is already open (%s)" % (plan.label(), still[0]["title"])
    n = len(mine) + 1
    heading = decisions.game_day_change_heading(n)
    page = plan.pages.responses
    block = decision_queue.event("week_inputs", season, week)
    when = dt.date.fromisoformat(plan.game["date"])
    item = {"id": "%d-w%02d-game-day-change%s" % (season, week, "" if n == 1 else "-%d" % n),
            "title": "%s depth and inactives change%s" % (plan.label(), "" if n == 1 else " %d" % n),
            "class": CLASS, "owner": holder, "authority_rows": ["8"] + list(decision_queue.CLASSES[CLASS].rows),
            "question": "Stone's change to the %s inactives or depth chart after his Game Plan was applied: %s."
                        % (plan.label(), "; ".join(r.rstrip(".") for r in reasons)),
            "raised": {"date": plan.master.isoformat(), "by": "workflow"}, "status": "OPEN", "waits_on": [],
            "deadline": {"date": plan.game["date"], "at": kickoff_at(plan.game),
                         "label": "before the %s inputs are built; kickoff %s %d, %s ET"
                                  % (plan.label(), when.strftime("%B"), when.day, kickoff(plan.game["kickoff_et"])),
                         "before": block},
            "blocks": [dict(block), decision_queue.event("week_close", season, week)],
            "fallback": None, "can_continue": None,
            "record": {"path": page.relative_to(root).as_posix(), "anchor": anchor(heading)},
            "sources": sources, "resolution": None}
    append_block({"week": week}, heading, item, root, season)
    queue["items"].append(item)
    write_like(queue_path, queue)
    return item, "%s: opened %s" % (plan.label(), item["title"])


# ------------------------------------------------------------------ the writer
def changes_record(plan):
    path = plan.pages.game_day_changes
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"season": plan.season, "week": plan.week, "about": CHANGES_ABOUT, "changes": []}


def change_note(plan, players, page):
    return ("%d of the %d are inactive for %s %s (%d dress), set by Stone on his %s Game Plan and changed by him on "
            "%s on My Responses: %s." % (len(players), len(plan.active()), plan.label(), opponent_words(plan),
                                         len(plan.active()) - len(players), plan.label(), long_date(plan.master),
                                         ", ".join(players)))


def roster_move(chart, leaving=(), joining=None):
    """A copy of a chart with a roster move made (a roster transaction's chart change): each player
    ``leaving`` taken off his group, his position and his roles, and each player ``joining``
    ({name: (group, position)}) placed at the bottom of his group. A role the move leaves empty is
    left for Stone's change; the game-day inactives are his and are not touched."""
    chart = copy.deepcopy(chart)
    for name in leaving:
        for group, order in (chart.get("depth") or {}).items():
            if name in order:
                chart["depth"][group] = [p for p in order if p != name]
        (chart.get("positions") or {}).pop(name, None)
        (chart.get("roles") or {}).pop(name, None)
    for name, (group, position) in (joining or {}).items():
        order = chart.setdefault("depth", {}).setdefault(group, [])
        if name not in order:
            order.append(name)
        chart.setdefault("positions", {})[name] = position
    return chart


def record_change(root, season, week, choices, item_id=None, block_sha256=None, rebuild=True):
    """Write Stone's change of the week's inactives or depth (``choices``: "inactives" and "depth" in
    the Game Plan's parsed forms; an inactive line left out keeps the list as it stands) after the
    Game Plan's checks pass against the chart as applied; returns (problems, paths written)."""
    root = Path(root).resolve()
    refused = closed_for_changes(root, season, week)
    if refused:
        return [refused], []
    base = Plan(root, season, week)
    if base.game is None:
        return ["%s: Jacksonville has no game" % base.label()], []
    if base.applied is None:
        return ["%s: the Game Plan is not applied yet; change the Game Plan itself" % base.label()], []
    queue_path = root / decision_queue.QUEUE
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    holder = base.job.get("holder")
    mine = week_items(queue, season, week, holder)
    still = [i for i in mine if i.get("status") == "OPEN" and (item_id is None or i["id"] == item_id)]
    if not still:
        return ["%s: no depth and inactives change is open for the week; it opens when the medical staff or a "
                "roster move makes one needed" % base.label()], []
    item = still[0]
    before = current_inactives(base)
    plan = Plan(root, season, week, inactives=before, choices=choices)
    listed, moved = inactive_problems(plan), depth_problems(plan)
    problems = listed + moved
    if not listed and not moved:
        problems += role_problems(plan)
    sheet = json.loads(plan.pages.call_sheet.read_text(encoding="utf-8"))
    problems += offense_problems(plan, sheet)
    if problems:
        return problems, []
    players = plan.inactives()
    depth = choices.get("depth") if isinstance(choices.get("depth"), dict) else {}
    _, changes = changed_chart(plan.chart, depth)
    page = item["record"]["path"]
    heading = next(h for h in [decisions.game_day_change_heading(n) for n in range(1, len(mine) + 2)]
                   if anchor(h) == item["record"]["anchor"])
    note = change_note(plan, players, page)

    def change(chart, working):
        chart, _ = changed_chart(chart, depth)
        chart["game_day_inactives"] = {"week": week, "players": list(players), "note": note}
        return chart
    written = write_charts(plan.paths, change)
    added = [p for p in players if p not in before]
    dressed = [p for p in before if p not in players]
    words = ("%s inactives changed on My Responses after the Game Plan: %s inactive%s." % (
        plan.label(), ", ".join(added), "; %s dress%s" % (", ".join(dressed), "es" if len(dressed) == 1 else "")
        if dressed else "") if added or dressed else "%s inactives unchanged." % plan.label())
    words += (" " + "; ".join(changes) + ".") if changes else " No order or role change."
    written.append(log_change(plan.paths, {
        "date": long_date(plan.master), "recorded": plan.master.isoformat(),
        "event": "%s: Stone's depth and inactives change" % plan.label(), "change": words,
        "sources": [{"label": "%s My Responses" % plan.label(), "page": "%s#%s" % (page, item["record"]["anchor"])}]}))
    inactives = json.loads(plan.pages.inactives.read_text(encoding="utf-8"))
    inactives.setdefault("as_set", {k: inactives[k] for k in ("set", "players", "note", "page") if k in inactives})
    inactives["players"], inactives["note"] = list(players), note
    inactives.setdefault("changes", []).append({"date": plan.master.isoformat(), "players_before": before,
                                                "players": list(players), "page": page, "heading": heading})
    plan.pages.inactives.write_text(json.dumps(inactives, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    written.append(plan.pages.inactives)
    record = changes_record(plan)
    record["changes"].append({"n": len(record["changes"]) + 1, "heading": heading, "item": item["id"],
                              "date": plan.master.isoformat(), "page": page, "anchor": item["record"]["anchor"],
                              "block_sha256": block_sha256, "inactives": {"before": before, "after": list(players)},
                              "depth": depth or "none", "chart_changes": changes})
    plan.pages.game_day_changes.parent.mkdir(parents=True, exist_ok=True)
    plan.pages.game_day_changes.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    written.append(plan.pages.game_day_changes)
    item["status"] = "RESOLVED"
    item["resolution"] = {"date": plan.master.isoformat(), "by": "user",
                          "record": {"path": page, "anchor": item["record"]["anchor"]},
                          "summary": "Stone changed the %s %s on My Responses after the Game Plan was applied, %s"
                                     % (plan.label(), "inactives and depth" if changes else "inactives",
                                        long_date(plan.master))}
    write_like(queue_path, queue)
    written.append(queue_path)
    if rebuild:
        from scripts.apply_game_plan import rebuild as rebuild_pages
        problems = rebuild_pages(root, week)
    return problems, written


def validation_errors(root=ROOT):
    """Every recorded game-day change held to its records: each change's queue item a game-day item of
    its week, resolved by the user with the change's block as its record; the week's inactives record
    ending on the change's list, its list as set kept; and the changes in heading order."""
    from runtime import game_weeks
    from runtime.seasons import SeasonPaths, active_season
    root = Path(root).resolve()
    season = active_season(root)
    paths = SeasonPaths(season, root)
    queue = {i.get("id"): i for i in decision_queue.load(root)["items"]}
    errors = []
    for game in game_weeks.club_games(paths, "Jacksonville Jaguars"):
        week = game["week"]
        pages = decisions.week_pages(season, week, root, postseason=game.get("game_type") == "postseason")
        if not pages.game_day_changes.is_file():
            continue
        label = "Week %d game-day change" % week
        record = json.loads(pages.game_day_changes.read_text(encoding="utf-8"))
        changes = record.get("changes") or []
        for n, change in enumerate(changes, 1):
            item = queue.get(change.get("item"))
            if change.get("heading") != decisions.game_day_change_heading(n) or change.get("n") != n:
                errors.append("%s %d: the heading is not %r" % (label, n, decisions.game_day_change_heading(n)))
            if item is None or not decision_queue.game_day_item(item) or item.get("status") != "RESOLVED" or \
                    (item.get("resolution") or {}).get("by") != "user" or \
                    (item.get("resolution") or {}).get("record") != {"path": change.get("page"),
                                                                     "anchor": change.get("anchor")}:
                errors.append("%s %d: its queue item is not the week's change resolved by Stone on its block"
                              % (label, n))
        inactives = game_plan.applied_record(pages.inactives) or {}
        if changes and (inactives.get("players") != changes[-1]["inactives"]["after"]
                        or "as_set" not in inactives
                        or [c.get("players") for c in inactives.get("changes") or ()]
                        != [c["inactives"]["after"] for c in changes]):
            errors.append("%s: the week's inactives record does not end on the last change, keep the list as set "
                          "and list each change" % label)
    return errors


def block_digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def open_changes(root, season, week):
    """The week's game-day changes open and unanswered."""
    root = Path(root).resolve()
    plan = Plan(root, season, week)
    queue = decision_queue.load(root)
    return [i for i in week_items(queue, season, week, plan.job.get("holder")) if i.get("status") == "OPEN"]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("week", type=int)
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--needed", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    if args.needed:
        item, message = open_item(args.root, args.season, args.week)
        print(message)
        return 0
    if args.check:
        still = open_changes(args.root, args.season, args.week)
        for item in still:
            print("- open: %s, due before the Week %d inputs are built" % (item["title"], args.week))
        print("GAME-DAY CHANGE: %s" % ("OPEN" if still else "NONE OPEN"))
        return 1 if still else 0
    print("GAME-DAY CHANGE: the change is read from its My Responses block, which comes with the My Responses page "
          "(rebuild step 5, builder C, second wave); nothing was written")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
