#!/usr/bin/env python3
"""Depth or inactives after the Game Plan is set (rebuild step 5, C2).

  python scripts/change_game_day.py WEEK --season YEAR --needed [--root PATH]
  python scripts/change_game_day.py WEEK --season YEAR [--file PAGE] [--root PATH]
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

Stone answers in the block's "My answer" line, one line each, in the Game
Plan's own forms: "Inactives: ..." (the players by name, or "Standing rule"
with the others he names) and "Depth/role changes: ..." (a role and its
player, or a group's new order, separated by semicolons); a line left out
keeps the inactives as they stand, or the depth unchanged. The default mode
reads each open change's block: an empty block leaves the change open; an
answered one is checked (``block_choices``, then the Game Plan's checks as
``record_change`` runs them) and, once it passes, written by ``record_change``,
its "Date answered" line filled with the master date (the runner's only edit
to his page) and the block frozen by its digest in the week's responses record
(``applied``: its sha256, date and the change it commits to), which validation
holds it to. With --file his page (a .md or .txt file with the same headings)
is placed first, refused with nothing written when it changes an applied block
or carries a reserved heading the week has not asked
(scripts/record_practice_week.place_upload).

--check writes nothing: it exits 1 while a change is open (the runner applies
it before building the inputs), naming whether its block is unanswered, ready
to apply or refused and why, and 0 otherwise.

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
N" on a later Game Plan carries the list as it stood at the game. Nothing here
moves the clock or creates an event.
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


def change_problems(root, season, week, choices, item_id=None):
    """(problems, context): the Game Plan's checks of a change (``choices``) against the chart as
    applied, the inactives as they stand and the frozen sheet, without writing; ``context`` carries
    what the writer needs once they pass."""
    root = Path(root).resolve()
    refused = closed_for_changes(root, season, week)
    if refused:
        return [refused], None
    base = Plan(root, season, week)
    if base.game is None:
        return ["%s: Jacksonville has no game" % base.label()], None
    if base.applied is None:
        return ["%s: the Game Plan is not applied yet; change the Game Plan itself" % base.label()], None
    queue = decision_queue.load(root)
    holder = base.job.get("holder")
    mine = week_items(queue, season, week, holder)
    still = [i for i in mine if i.get("status") == "OPEN" and (item_id is None or i["id"] == item_id)]
    if not still:
        return ["%s: no depth and inactives change is open for the week; it opens when the medical staff or a "
                "roster move makes one needed" % base.label()], None
    before = current_inactives(base)
    plan = Plan(root, season, week, inactives=before, choices=choices)
    listed, moved = inactive_problems(plan), depth_problems(plan)
    problems = listed + moved
    if not listed and not moved:
        problems += role_problems(plan)
    sheet = json.loads(plan.pages.call_sheet.read_text(encoding="utf-8"))
    problems += offense_problems(plan, sheet)
    return problems, {"plan": plan, "item": still[0], "mine": mine, "before": before}


def record_change(root, season, week, choices, item_id=None, block_sha256=None, rebuild=True):
    """Write Stone's change of the week's inactives or depth (``choices``: "inactives" and "depth" in
    the Game Plan's parsed forms; an inactive line left out keeps the list as it stands) after the
    Game Plan's checks pass against the chart as applied; returns (problems, paths written)."""
    root = Path(root).resolve()
    problems, context = change_problems(root, season, week, choices, item_id)
    if problems:
        return problems, []
    plan, item, mine, before = context["plan"], context["item"], context["mine"], context["before"]
    queue_path = root / decision_queue.QUEUE
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    item = next(i for i in queue["items"] if i.get("id") == item["id"])
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


# ------------------------------------------------------------------ his block on My Responses
CHANGE_KIND = "game_day_change"
BLOCK_LINES = {"inactives": ("inactives", "Inactives"), "depth/role changes": ("depth", "Depth/role changes"),
               "depth and role changes": ("depth", "Depth/role changes")}
BLOCK_FORM = ("one line each in the Game Plan's forms: \"Inactives: \" and the players by name (or \"Standing rule\" "
              "with the others you name), and \"Depth/role changes: \" and a role and its player (Kick returner: "
              "name) or a group's new order (Wide receivers order: names), separated by semicolons")


def block_choices(text):
    """(choices, problems): a change's own lines from his block's answer, read by the Game Plan's own
    readers (runtime/game_plan.py): ``inactives`` when he writes an "Inactives:" line, ``depth``
    ("none" when he writes no "Depth/role changes:" line)."""
    choices, problems = {}, []
    lines = [l.strip() for l in (text or "").split("\n")]
    for n, line in enumerate(lines, 1):
        line = re.sub(r"^[-*]\s+", "", line).strip()
        if not line:
            continue
        label, sep, value = line.partition(":")
        found = BLOCK_LINES.get(label.strip().lower()) if sep else None
        if found is None:
            problems.append("%r is not a line the change takes; write %s" % (line[:80], BLOCK_FORM))
            continue
        key, name = found
        if key in choices:
            problems.append("%s: the line appears twice; write it once" % name)
            continue
        if not value.strip():
            problems.append("%s: the line is empty; leave it out to keep it as it stands" % name)
            continue
        field = game_plan.Field(key, n, value.strip(), name)
        read = game_plan.READERS[key if key == "depth" else "inactives"](key, field, problems)
        if key == "inactives" and isinstance(read, dict) and "same_as" in read:
            problems.append("Inactives: Carry Week N belongs on a Game Plan; name the inactives for this game")
            continue
        if read is not None:
            choices[key] = read
    if not choices and not problems:
        problems.append("Write the change, %s" % BLOCK_FORM)
    choices.setdefault("depth", "none")
    return choices, problems


def item_heading(item, mine):
    """The block heading of a game-day change item (its record's anchor)."""
    return next(h for h in [decisions.game_day_change_heading(n) for n in range(1, len(mine) + 2)]
                if anchor(h) == item["record"]["anchor"])


def read_answers(root, season, week):
    """[(item, heading, block, choices, problems)] of the week's open changes, in order: each open
    item's block read and checked (an empty block has no choices and no problems)."""
    from scripts import record_practice_week as rpw
    root = Path(root).resolve()
    plan = Plan(root, season, week)
    queue = decision_queue.load(root)
    mine = week_items(queue, season, week, plan.job.get("holder"))
    out = []
    for item in [i for i in mine if i.get("status") == "OPEN"]:
        heading = item_heading(item, mine)
        block = rpw.read_block(root, season, {"week": week}, heading)
        if block is None:
            out.append((item, heading, None, None, ["%s: the block is missing from the week's My Responses page"
                                                    % heading]))
            continue
        if not block.answer:
            out.append((item, heading, block, None, []))
            continue
        choices, problems = block_choices(block.answer)
        problems = ["%s: %s" % (heading, p) for p in problems]
        problems += [p for p in [rpw.date_problem(block, plan.master)] if p]
        problems += rpw.clean_problems(root, season, {"week": week}, block)
        if not problems:
            checked, _ = change_problems(root, season, week, choices, item["id"])
            problems += ["%s: %s" % (heading, p) for p in checked]
        out.append((item, heading, block, choices, problems))
    return out


def apply_answers(root, season, week, rebuild=True):
    """(problems, notes, written): every answered open change of the week checked and, when all pass,
    written (``record_change``) and its block frozen. With any problem nothing is written."""
    from scripts import record_practice_week as rpw
    from scripts.render_career_views import paused_games
    root = Path(root).resolve()
    if paused_games(root):
        return ["A Jacksonville game is paused; nothing is recorded until it is finished"], [], []
    answers = read_answers(root, season, week)
    problems = [p for *_, found in answers for p in found]
    if problems:
        return problems, [], []
    notes = ["%s: still open; no answer yet" % heading for item, heading, block, choices, _ in answers
             if choices is None]
    written = []
    master = Plan(root, season, week).master
    for item, heading, block, choices, _ in answers:
        if choices is None:
            continue
        expected = hashlib.sha256(rpw.filled(block, master).encode("utf-8")).hexdigest()
        found, paths = record_change(root, season, week, choices, item_id=item["id"], block_sha256=expected,
                                     rebuild=False)
        if found:
            return found, notes, written
        written += paths
        change = changes_record(Plan(root, season, week))["changes"][-1]
        frozen = rpw.freeze_block(root, season, {"week": week}, block,
                                  {"kind": CHANGE_KIND, "inactives": change["inactives"]["after"],
                                   "depth": change["depth"]}, master)
        if frozen.sha256 != expected:
            raise ValueError("%s: the frozen block's digest differs from the one recorded" % heading)
        from runtime import responses
        pages = responses.pages_of(season, {"week": week}, root)
        written += [pages.responses, pages.responses_record]
    if written and rebuild:
        from scripts.apply_game_plan import rebuild as rebuild_pages
        problems = rebuild_pages(root, week)
    return problems, notes, written


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
        from runtime import responses
        bound = {b.get("heading"): b for b in responses.record_of(season, {"week": week}, root).get("blocks") or ()}
        for n, change in enumerate(changes, 1):
            digest = change.get("block_sha256")
            applied = (bound.get(change.get("heading")) or {}).get("applied") or {}
            if digest is not None and applied.get("sha256") != digest:
                errors.append("%s %d: the block it was written from is not the one frozen on My Responses"
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
    parser.add_argument("--file", type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    if args.needed:
        item, message = open_item(args.root, args.season, args.week)
        print(message)
        return 0
    if args.check:
        answers = read_answers(args.root, args.season, args.week)
        for item, heading, block, choices, problems in answers:
            state = ("unanswered" if choices is None and not problems else "refused" if problems
                     else "answered, ready to apply")
            print("- open: %s, due before the Week %d inputs are built; %s" % (item["title"], args.week, state))
            for problem in problems:
                print("  - %s" % problem)
        print("GAME-DAY CHANGE: %s" % ("OPEN" if answers else "NONE OPEN"))
        return 1 if answers else 0
    if args.file is not None:
        from scripts import record_practice_week as rpw
        try:
            rpw.place_upload(args.root, args.season, {"week": args.week}, args.file)
        except (OSError, ValueError) as exc:
            print("GAME-DAY CHANGE: UPLOAD REFUSED")
            print("- %s" % exc)
            return 1
    problems, notes, written = apply_answers(args.root, args.season, args.week)
    for note in notes:
        print("  note: %s" % note)
    if problems:
        print("GAME-DAY CHANGE: NOT RECORDED")
        for problem in problems:
            print("- %s" % problem)
        return 1
    for path in written:
        print("wrote %s" % Path(path).resolve().relative_to(Path(args.root).resolve()).as_posix())
    print("GAME-DAY CHANGE: %s" % ("RECORDED" if written else "NOTHING TO RECORD"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
