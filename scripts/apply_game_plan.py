#!/usr/bin/env python3
"""Apply Stone's checked Game Plan (rebuild step 4).

  python scripts/apply_game_plan.py WEEK --season YEAR [--file PATH] [--root PATH]

Runs scripts/check_game_plan.py first and refuses (exit 1) until the page is
complete. Then it converts the page into exactly the records the game path
already reads, and the record of the apply:

- the frozen call sheet, ``SeasonPaths(YEAR).call_sheet(WEEK)``, written as
  every frozen sheet is (indent 1, a final newline), valid under the existing
  validators; build_week_inputs.py reads it unchanged;
- the game depth chart's ``game_day_inactives`` and any order or role change,
  in both copies (the game chart and the working chart), with one dated entry
  in the depth chart's update log naming the page as its source. A starter,
  kicker or punter named in the role table heads his group. Where an order
  change moves a player whose receiver or defensive-back label (Stone's dated
  role decisions on the working chart) no longer holds, a dated entry clears
  that label rather than leave it on the wrong player;
- the decision-queue items the plan settles (the week's game plan and
  inactives, Stone's), marked RESOLVED by the user with the page as their
  record. Nothing is applied while either item still waits on an exam dated
  that day or later (its ``waits_on``): the page is complete, and it is set
  once the exams are held, when the check reads their results (``waiting``);
- the week's inactives record beside the call sheet (``inactives.json``,
  runtime/decisions.WeekPages.inactives), the permanent owner of the list
  ("Same as Week N" reads it; the chart holds only the latest list);
- the applied plan record (``applied_plan.json``, WeekPages.applied): the day
  it was applied, the digest of the page and of the call sheet as frozen, its
  depth changes and the chart before them, and the event of the apply, whose
  event line the week index carries (the annual record lists it).

Applying again (a revised page, before the game is built) first undoes the
earlier apply's depth changes, replaces its update-log entry and its record,
so the log and the record always describe the plan against the chart as it
stood before it. Stone's page stays as the record of his decision and is
never written. Every built page is rebuilt afterwards (scripts/
rebuild_pages.py), so no view that reads the chart is left stale. The Game
Week Briefing is not reissued for the plan's own settlement. Nothing is
drawn, and the clock does not move.

Repository validation runs ``validation_errors``: every applied week's page
and call sheet as the record froze them, the open week's game-plan item
present once its briefing is issued.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import game_plan  # noqa: E402
from scripts.check_game_plan import (JAX, ROLE_WORDS, Plan, changed_chart, check, page_digest,  # noqa: E402
                                     place_upload)

PLAN_CLASSES = ("weekly_game_plan", "game_day_inactives")
LOG_EVENT = "Week %d: Stone's Game Plan"


def long_date(value):
    return "%s %d, %d" % (value.strftime("%B"), value.day, value.year)


def write_like(path, data):
    """Write ``data`` to a JSON record in the layout the record already has (its indent and
    whether it escapes non-ASCII), so a change shows only what changed."""
    raw = path.read_text(encoding="utf-8") if path.is_file() else ""
    try:
        old = json.loads(raw)
    except ValueError:
        old = None
    layout = next(((i, a) for i in (1, 2) for a in (False, True)
                   if old is not None and json.dumps(old, indent=i, ensure_ascii=a) + "\n" == raw), (1, False))
    path.write_text(json.dumps(data, indent=layout[0], ensure_ascii=layout[1]) + "\n", encoding="utf-8")


def opponent_words(plan):
    g = plan.game
    return ("at %s" if g["away"] == JAX else "against %s") % (
        g["home"] if g["away"] == JAX else g["away"]).rsplit(" ", 1)[0]


def inactive_note(plan, players):
    value = plan.choices.get("inactives") or {}
    reasons = value.get("reasons") or {} if isinstance(value, dict) else {}
    listed = "; ".join("%s (%s)" % (p, reasons[p]) if p in reasons else p for p in players)
    named = len(value.get("players") or ()) if isinstance(value, dict) else 0
    how = (" by his standing rule" + (", with %d he named" % named if named else "")
           if isinstance(value, dict) and value.get("standing") else
           " as in Week %d" % value["same_as"] if isinstance(value, dict) and "same_as" in value else "")
    return ("%d of the %d are inactive for Week %d %s (%d dress), set by Stone on %s on his Week %d Game Plan%s: %s."
            % (len(players), len(plan.active()), plan.week, opponent_words(plan), len(plan.active()) - len(players),
               long_date(plan.master), plan.week, how, listed))


def _restore(chart, earlier):
    """Undo an earlier apply's depth changes on ``chart`` (in place): each group order and role it
    changed goes back to what it was, where the chart still holds what that apply set."""
    for group, order in ((earlier.get("before") or {}).get("orders") or {}).items():
        if chart.get("depth", {}).get(group) == (earlier.get("set") or {}).get("orders", {}).get(group):
            chart["depth"][group] = list(order)
    roles = chart.setdefault("roles", {})
    for role, holders in ((earlier.get("before") or {}).get("roles") or {}).items():
        now = [p for p, r in roles.items() if role in (r or ())]
        if now != [(earlier.get("set") or {}).get("roles", {}).get(role)]:
            continue
        for p in now:
            roles[p] = [r for r in roles[p] if r != role]
            if not roles[p]:
                del roles[p]
        for p in holders:
            roles.setdefault(p, []).append(role)


def _before(chart, after):
    """What the apply changed, as it stood before: {orders, roles} for the groups and roles that differ."""
    orders = {g: list(chart["depth"][g]) for g, o in (after.get("depth") or {}).items()
              if chart.get("depth", {}).get(g) != o}
    roles = {}
    for player, held in (after.get("roles") or {}).items():
        for role in held:
            was = [p for p, r in (chart.get("roles") or {}).items() if role in (r or ())]
            if was != [player]:
                roles[role] = was
    return {"orders": orders, "roles": roles}


def _set(chart, before):
    return {"orders": {g: list(chart["depth"][g]) for g in before["orders"]},
            "roles": {role: next(p for p, r in chart.get("roles", {}).items() if role in (r or ()))
                      for role in before["roles"]}}


def cleared_labels(plan, base, after):
    """The players of a reordered group whose place changed and who hold one of Stone's dated
    receiver or defensive-back labels (the working chart's role decisions): the label no longer
    describes the order, so the apply clears it."""
    working = plan.paths.record("offseason/depth_chart_working.json")
    if not working.is_file():
        return []
    labels = {}
    for decision in json.loads(working.read_text(encoding="utf-8")).get("stone_role_decisions", ()):
        if decision.get("game_plan_week") == plan.week:
            continue        # this week's own earlier apply, replaced below
        for row in decision.get("decisions", ()):
            labels[row["player"]] = row.get("role")
    out = []
    for group, order in (after.get("depth") or {}).items():
        old = (base.get("depth") or {}).get(group) or []
        for player in order:
            if labels.get(player) and player in old and old.index(player) != order.index(player):
                out.append(player)
    return out


def event_for(plan, sheet, players, changes):
    """The apply's event: Stone set the week's Game Plan, in football words for the annual record."""
    decisions = sheet.get("decisions") or {}
    parts = []
    for kind, words in (("fourth_down", "fourth downs"), ("two_point", "two-point tries"), ("kickoff", "kickoffs")):
        entry = plan.choices.get(kind)
        if kind not in decisions:
            how = "his live call" if kind == "fourth_down" else None
        elif isinstance(entry, dict) and entry.get("standing"):
            how = "his standing rule"
        elif isinstance(entry, dict) and "same_as" in entry:
            how = "as in Week %d" % entry["same_as"]
        else:
            how = "his own rules"
        if how:
            parts.append("%s %s" % (words, how))
    defense = sheet.get("defensive_call_sheet")
    summary = ("Stone set his Week %d Game Plan %s: the call sheet frozen with %d offensive calls%s, %s; the %d "
               "inactives %s; %s." % (
                   plan.week, opponent_words(plan), len(sheet.get("offensive_call_sheet") or ()),
                   " and %d defensive calls" % len(defense["rows"]) if defense else "", ", ".join(parts),
                   len(players), ", ".join(players), "; ".join(changes) if changes else "no depth chart change"))
    event = {"id": "%s-week-%d-game-plan-set" % (plan.master.isoformat(), plan.week), "date": plan.master.isoformat(),
             "season": plan.season, "status": "closed", "summary": summary}
    # Set after the day's last closure (the last game, the evening it closed): the record lists it after.
    from runtime.events import closures, load_events
    closed = closures(load_events(plan.root))
    if closed and closed[-1][2]["through"] == event["date"]:
        event["follows"] = closed[-1][1].id
    return event


def apply_records(plan, sheet, players, resolve_queue=True):
    """Write the call sheet, the chart's inactives and depth changes with their log entry, the applied
    plan record, and settle the queue items; returns the paths written."""
    written = []
    path = plan.paths.call_sheet(plan.week)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(game_plan.sheet_bytes(sheet))
    written.append(path)
    page = plan.rel(plan.pages.plan)
    earlier = plan.applied or {}
    depth = plan.choices.get("depth") if isinstance(plan.choices.get("depth"), dict) else {}
    working_path = plan.paths.record("offseason/depth_chart_working.json")
    game = json.loads(plan.paths.depth_chart.read_text(encoding="utf-8"))
    _restore(game, earlier)
    after, changes = changed_chart(game, depth)
    before = _before(game, after)
    cleared = cleared_labels(plan, game, after)
    for chart_path in [plan.paths.depth_chart] + ([working_path] if working_path.is_file() else []):
        chart = json.loads(chart_path.read_text(encoding="utf-8"))
        _restore(chart, earlier)
        chart, _ = changed_chart(chart, depth)
        if players is not None:
            chart["game_day_inactives"] = {"week": plan.week, "players": list(players),
                                           "note": inactive_note(plan, players)}
        if chart_path == working_path:
            decisions = [d for d in chart.get("stone_role_decisions", ())
                         if d.get("game_plan_week") != plan.week]
            if cleared:
                decisions.append({"date": long_date(plan.master), "game_plan_week": plan.week,
                                  "rule": "Stone's Week %d Game Plan changed the order; these players' earlier labels "
                                          "no longer describe their places." % plan.week,
                                  "decisions": [{"player": p, "role": None, "note": "place changed on the Week %d "
                                                 "Game Plan" % plan.week} for p in cleared]})
            if decisions or "stone_role_decisions" in chart:
                chart["stone_role_decisions"] = decisions
        write_like(chart_path, chart)
        written.append(chart_path)
    log_path = plan.paths.record("team/depth_chart/update_log.json")
    log = json.loads(log_path.read_text(encoding="utf-8"))
    change = "Week %d inactives: %s." % (plan.week, ", ".join(players)) if players is not None else ""
    shown = changes + ["the earlier label of %s cleared" % p for p in cleared]
    change += (" " + "; ".join(shown) + ".") if shown else " No order or role change."
    log["entries"] = [e for e in log["entries"] if not (e.get("event") == LOG_EVENT % plan.week and any(
        (s or {}).get("page") == page for s in e.get("sources") or ()))]
    log["entries"].append({"date": long_date(plan.master), "recorded": plan.master.isoformat(),
                           "event": LOG_EVENT % plan.week, "change": change.strip(),
                           "sources": [{"label": "Week %d Game Plan" % plan.week, "page": page}]})
    write_like(log_path, log)
    written.append(log_path)
    if players is not None:
        plan.pages.inactives.write_text(json.dumps({
            "season": plan.season, "week": plan.week, "set": plan.master.isoformat(), "players": list(players),
            "note": inactive_note(plan, players), "page": page}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(plan.pages.inactives)
    record = {"season": plan.season, "week": plan.week, "applied": plan.master.isoformat(), "page": page,
              "page_sha256": page_digest(plan.text), "call_sheet_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
              "before": before, "set": _set(after, before), "labels_cleared": cleared,
              "event": event_for(plan, sheet, players or [], changes)}
    write_like(plan.pages.applied, record)
    written.append(plan.pages.applied)
    if resolve_queue:
        written += settle_queue(plan, page)
    return written


def plan_items(plan, queue):
    """The week's open items Stone's Game Plan answers (his game plan and inactives)."""
    holder = plan.job.get("holder")
    return [i for i in queue["items"] if i.get("status") == "OPEN" and i.get("owner") == holder
            and i.get("class") in PLAN_CLASSES and any(
                b.get("kind") == "week_inputs" and b.get("season") == plan.season and b.get("week") == plan.week
                for b in i.get("blocks") or ())]


def settle_queue(plan, page):
    from runtime import decision_queue
    queue_path = plan.root / decision_queue.QUEUE
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    settled = 0
    for item in plan_items(plan, queue):
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


def rebuild(root, week=None):
    """Every built page, from the records the plan changed (scripts/rebuild_pages.py); returns its
    problems."""
    from scripts import rebuild_pages
    _, problems = rebuild_pages.rebuild(root)
    return problems


def waiting(plan):
    """One line per item the page answers that still waits on an exam dated today or later: until
    they are held, nothing is set from the page (the clock waits for his answer after them; the
    check then reads their results). [] when nothing waits."""
    from runtime import decision_queue
    from runtime.decisions import exams_ahead
    out = []
    for item in plan_items(plan, decision_queue.load(plan.root)):
        ahead = exams_ahead(item, plan.master)
        if ahead:
            out.append("%s waits on %s; the page is complete and is set once %s held" % (
                item["title"], "; ".join("%s (%s)" % (w["what"].split(";")[0],
                                                      long_date(date.fromisoformat(w["date"]))) for w in ahead),
                "it is" if len(ahead) == 1 else "they are"))
    return out


def apply(root, season, week, rebuild_pages=True, report=None):
    """Check the week's page and apply it; ``report`` (a dict) is told when nothing is set because
    an item still waits on an exam (``waiting``)."""
    problems, notes, plan = check(root, season, week)
    if problems:
        return problems, []
    held = waiting(plan)
    if held:
        if report is not None:
            report["waiting"] = True
        return held, []
    sheet = plan.sheet()
    written = apply_records(plan, sheet, plan.inactives())
    if rebuild_pages:
        problems = rebuild(plan.root, week)
    return problems, written


def validation_errors(root=ROOT):
    """Every applied Game Plan as its record froze it, and the open week's decisions opened:

    - an applied week's page is the page applied (its digest) and its call sheet the one frozen;
    - while the chart's game-day list is a week's, it is that week's inactives record;
    - a week with a Game Plan and a call sheet has an applied record (the sheet came from the page);
    - once the open week's Game Week Briefing is issued, the decision queue holds the week's game-plan
      item (scripts/open_game_week.py opens it)."""
    from runtime import decision_queue
    from runtime.decisions import week_pages
    from runtime.seasons import SeasonPaths, active_season
    root = Path(root).resolve()
    season = active_season(root)
    paths = SeasonPaths(season, root)
    errors = []
    chart = json.loads(paths.depth_chart.read_text(encoding="utf-8")) if paths.depth_chart.is_file() else {}
    for game in paths.regular_games():
        if JAX not in (game["away"], game["home"]):
            continue
        week = game["week"]
        pages = week_pages(season, week, root)
        record = game_plan.applied_record(pages.applied)
        label = "Week %d Game Plan" % week
        inactives = game_plan.applied_record(pages.inactives)
        listed = chart.get("game_day_inactives") or {}
        if inactives is not None and listed.get("week") == week and \
                list(listed.get("players") or []) != list(inactives.get("players") or []):
            errors.append("Week %d: the depth chart's inactives are not the week's inactives as set" % week)
        if record is None:
            if pages.plan.is_file() and pages.call_sheet.is_file():
                errors.append("%s: the call sheet was not frozen from the page; apply it (python "
                              "scripts/apply_game_plan.py %d --season %d)" % (label, week, season))
            continue
        if not pages.plan.is_file() or page_digest(pages.plan.read_text(encoding="utf-8")) != record.get("page_sha256"):
            errors.append("%s: the page has changed since it was applied on %s; apply it again (python "
                          "scripts/apply_game_plan.py %d --season %d), or restore it as applied"
                          % (label, record.get("applied"), week, season))
        if not pages.call_sheet.is_file() or \
                hashlib.sha256(pages.call_sheet.read_bytes()).hexdigest() != record.get("call_sheet_sha256"):
            errors.append("%s: the call sheet is not the one the page froze" % label)
    try:
        from scripts.render_game_week import Week
        wk = Week(root)
    except (OSError, ValueError, KeyError):
        return errors
    if wk.game is not None and not wk.closed and wk.pages.briefing.is_file():
        queue = decision_queue.load(root)
        week = wk.game["week"]
        if not any(i.get("class") == "weekly_game_plan" and any(
                b.get("season") == season and b.get("week") == week for b in i.get("blocks") or ())
                for i in queue["items"]):
            errors.append("Week %d: the Game Week Briefing is issued, but the decision queue holds no game-plan item "
                          "for the week (python scripts/open_game_week.py opens it)" % week)
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("week", type=int)
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--file", type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        if args.file is not None:
            place_upload(args.root, args.season, args.week, args.file)
        report = {}
        problems, written = apply(args.root, args.season, args.week, report=report)
    except (OSError, ValueError) as exc:
        print("GAME PLAN: NOT APPLIED\n- %s" % exc)
        return 1
    root = Path(args.root).resolve()
    if not written:
        print("GAME PLAN: COMPLETE, NOT YET SET" if report.get("waiting") else "GAME PLAN: NOT APPLIED")
        for problem in problems:
            print("- " + problem)
        return 1
    print("GAME PLAN: APPLIED  Week %d, %d" % (args.week, args.season))
    for path in written:
        print("wrote %s" % Path(path).relative_to(root).as_posix())
    for problem in problems:
        print("page not rebuilt: %s" % problem)
    print("Commit the applied plan (the page, the call sheet, the charts, the log, the queue and the record) on "
          "its own before the week's inputs are built: validation requires the call sheet's freeze commit to "
          "come before the commit that closes the game.")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
