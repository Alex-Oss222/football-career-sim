#!/usr/bin/env python3
"""Apply Stone's checked Game Plan (game week version 2).

  python scripts/apply_game_plan.py WEEK --season YEAR [--file PATH] [--root PATH]

Runs scripts/check_game_plan.py first and refuses (exit 1) until the page is
complete. Then it compiles the page (runtime/game_plan.compile_sheet) into
exactly the records the game path already reads, and the record of the apply:

- the frozen call sheet, ``SeasonPaths(YEAR).call_sheet(WEEK)`` (a playoff
  round's in the postseason folder's data twin, ``postseason=True``), written as
  every frozen sheet is (indent 1, a final newline), valid under the existing
  validators; build_week_inputs.py reads it unchanged;
- the game depth chart's ``game_day_inactives`` and any order or role change,
  in both copies (the game chart and the working chart), with one dated entry
  in the depth chart's update log naming the page as its source. A starter,
  kicker or punter named in the role table heads his group. Where an order
  change moves a player whose receiver or defensive-back label (Stone's dated
  role decisions on the working chart) no longer holds, or the plan takes from
  a player the game role his label names (the nickel, the outside reserve
  corner, the returns: runtime/assignments.LABEL_ROLES), a dated entry clears
  that label rather than leave it on the wrong player (record_cleared, which
  a game-day change and the bye adjustments use too);
- the decision-queue items the plan settles (the week's game plan and
  inactives, Stone's), marked RESOLVED by the user with the page as their
  record. Nothing is applied while either item still waits on an exam dated
  that day or later (its ``waits_on``): the page is complete, and it is set
  once the exams are held, when the check reads their results (``waiting``).
  Nothing waits on practice: any call of the active book may be named,
  whether or not the week's practice covered it;
- the week's inactives record beside the call sheet (``inactives.json``,
  runtime/decisions.WeekPages.inactives), the permanent owner of the list
  ("Carry Week N" reads it; the chart holds only the latest list);
- the applied plan record (``applied_plan.json``, WeekPages.applied): the day
  it was applied, the digest of the page and of the call sheet as frozen, its
  depth changes and the chart before them, the source map from every emitted
  call, defensive row and decision to the page line or the carried frozen
  item it came from, his reasons and other author intent with their page
  lines and the day they were known (intent never reaches the call sheet),
  and the event of the apply, whose event line the week index carries (the
  annual record lists it).

Applying again (a revised page, before the game is built) first undoes the
earlier apply's depth changes, replaces its update-log entry and its record,
so the log and the record always describe the plan against the chart as it
stood before it. Once Stone has changed the depth or inactives on My Responses
after the apply (scripts/change_game_day.py) the page is not applied again:
the change was made against the plan as applied. The chart writers
(``chart_paths``, ``write_charts``, ``log_change``) are the one way the two
chart copies and the update log are written, here, by a game-day change, a bye
adjustment and a roster transaction. Stone's page stays as the record of his decision and is
never written. Every built page is rebuilt afterwards (scripts/
rebuild_pages.py), so no view that reads the chart is left stale. The Game
Week Briefing is not reissued for the plan's own settlement. Nothing is
drawn, and the clock does not move.

Repository validation runs ``validation_errors``: every applied week's page
and call sheet as the record froze them, and the open week's game-plan item
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

from runtime import assignments, game_plan  # noqa: E402
from scripts.check_game_plan import (JAX, ROLE_WORDS, Plan, changed_chart, check, page_digest,  # noqa: E402
                                     place_upload)

PLAN_CLASSES = ("weekly_game_plan", "game_day_inactives")
LOG_EVENT = "Week %d: Stone's Game Plan"


def log_event(plan):
    """The update-log event of the week's apply: "Week 6: Stone's Game Plan", or the playoff round's."""
    return "%s: Stone's Game Plan" % plan.label() if plan.postseason else LOG_EVENT % plan.week


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
    game = "the %s game" % plan.label() if plan.postseason else plan.label()
    return ("%d of the %d are inactive for %s %s (%d dress), set by Stone on %s on his %s Game Plan%s: %s."
            % (len(players), len(plan.active()), game, opponent_words(plan), len(plan.active()) - len(players),
               long_date(plan.master), plan.label(), how, listed))


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


def label_decisions(paths, skip=None):
    """{player: label}: Stone's dated receiver and defensive-back labels on the working chart (its
    role decisions, the latest per player; a cleared label is None), leaving out the decisions
    ``skip`` (a function of a decision) matches."""
    working = paths.record("offseason/depth_chart_working.json")
    if not working.is_file():
        return {}
    labels = {}
    for decision in json.loads(working.read_text(encoding="utf-8")).get("stone_role_decisions", ()):
        if skip is not None and skip(decision):
            continue
        for row in decision.get("decisions", ()):
            labels[row["player"]] = row.get("role")
    return labels


def cleared_labels(labels, base, after):
    """[(player, why)]: the players holding one of Stone's labels (``labels``, label_decisions) that no
    longer describes the chart: "place" when his place in a reordered group changed, "role" when the
    chart took from him the game role his label names (assignments.LABEL_ROLES); a label naming no
    role is not touched by a role change. The change clears each one."""
    out = []
    for group, order in (after.get("depth") or {}).items():
        old = (base.get("depth") or {}).get(group) or []
        for player in order:
            if labels.get(player) and player in old and old.index(player) != order.index(player):
                out.append((player, "place"))
    now, placed = after.get("roles") or {}, {p for p, _ in out}
    for player in role_changed(base, after):
        named = assignments.LABEL_ROLES.get(labels.get(player))
        if named and not named <= set(now.get(player) or ()) and player not in placed:
            out.append((player, "role"))
    return out


def record_cleared(chart, cleared, when, what, drop=None, **key):
    """The working chart ``chart`` with its role decisions: those ``drop`` (a function of a decision)
    does not match, and, when ``cleared`` (cleared_labels) holds a player, one entry dated ``when``
    clearing those labels, keyed by ``key``; ``what`` names Stone's decision that changed the chart
    ("Week 7 Game Plan")."""
    decisions = [d for d in chart.get("stone_role_decisions", ()) if drop is None or not drop(d)]
    if cleared:
        decisions.append(dict({"date": when}, **key,
                              rule="Stone's %s changed the order or the roles; these players' earlier labels "
                                   "no longer describe their places." % what,
                              decisions=[{"player": p, "role": None, "note": "%s changed on the %s" % (why, what)}
                                         for p, why in cleared]))
    if decisions or "stone_role_decisions" in chart:
        chart["stone_role_decisions"] = decisions
    return chart


def cleared_words(cleared):
    return ["the earlier label of %s cleared" % p for p, _ in cleared]


def role_changed(base, after):
    """The players whose game roles (nickel, outside reserve, returners) differ after the apply."""
    was, now = base.get("roles") or {}, after.get("roles") or {}
    return [p for p in sorted(set(was) | set(now)) if sorted(was.get(p) or ()) != sorted(now.get(p) or ())]


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
        elif isinstance(entry, dict) and entry.get("no_change"):
            how = "unchanged"
        else:
            how = "his own rules"
        if how:
            parts.append("%s %s" % (words, how))
    defense = sheet.get("defensive_call_sheet")
    summary = ("Stone set his %s Game Plan %s: the call sheet frozen with %d offensive calls%s, %s; the %d "
               "inactives %s; %s." % (
                   plan.label(), opponent_words(plan), len(sheet.get("offensive_call_sheet") or ()),
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


def chart_paths(paths):
    """The depth chart's two copies (the chart writers' interface): the game chart the build reads and,
    when the season keeps one, the working chart beside it."""
    working = paths.record("offseason/depth_chart_working.json")
    return [paths.depth_chart] + ([working] if working.is_file() else [])


def write_charts(paths, change):
    """Write one change to both copies of the depth chart, each in the layout it already has: ``change``
    takes a copy of a chart and whether it is the working copy, and returns the chart to write. The one
    writer of the charts for the Game Plan's apply, a game-day change (scripts/change_game_day.py), a
    bye adjustment and a roster transaction; returns the paths written."""
    written = []
    for chart_path in chart_paths(paths):
        chart = change(json.loads(chart_path.read_text(encoding="utf-8")), chart_path != paths.depth_chart)
        write_like(chart_path, chart)
        written.append(chart_path)
    return written


def log_change(paths, entry, replaces=None):
    """Append one dated entry to the depth chart's update log (the one dated log of chart changes),
    first dropping the entries ``replaces`` (a function of an entry) matches; returns its path."""
    log_path = paths.record("team/depth_chart/update_log.json")
    log = json.loads(log_path.read_text(encoding="utf-8"))
    if replaces is not None:
        log["entries"] = [e for e in log["entries"] if not replaces(e)]
    log["entries"].append(entry)
    write_like(log_path, log)
    return log_path


def apply_records(plan, sheet, players, resolve_queue=True):
    """Write the call sheet, the chart's inactives and depth changes with their log entry, the applied
    plan record, and settle the queue items; returns the paths written."""
    written = []
    path = plan.pages.call_sheet        # a playoff game's in the postseason folder's data twin
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(game_plan.sheet_bytes(sheet))
    written.append(path)
    page = plan.rel(plan.pages.plan)
    earlier = plan.applied or {}
    depth = plan.choices.get("depth") if isinstance(plan.choices.get("depth"), dict) else {}
    game = json.loads(plan.paths.depth_chart.read_text(encoding="utf-8"))
    _restore(game, earlier)
    after, changes = changed_chart(game, depth)
    before = _before(game, after)
    this_week = lambda d: d.get("game_plan_week") == plan.week      # noqa: E731  (a re-apply replaces it)
    cleared = cleared_labels(label_decisions(plan.paths, skip=this_week), game, after)

    def change(chart, working):
        _restore(chart, earlier)
        chart, _ = changed_chart(chart, depth)
        if players is not None:
            chart["game_day_inactives"] = {"week": plan.week, "players": list(players),
                                           "note": inactive_note(plan, players)}
        if working:
            record_cleared(chart, cleared, long_date(plan.master), "%s Game Plan" % plan.label(), drop=this_week,
                           game_plan_week=plan.week)
        return chart
    written += write_charts(plan.paths, change)
    change = "%s inactives: %s." % (plan.label(), ", ".join(players)) if players is not None else ""
    shown = changes + cleared_words(cleared)
    change += (" " + "; ".join(shown) + ".") if shown else " No order or role change."
    written.append(log_change(plan.paths, {
        "date": long_date(plan.master), "recorded": plan.master.isoformat(), "event": log_event(plan),
        "change": change.strip(), "sources": [{"label": "%s Game Plan" % plan.label(), "page": page}]},
        replaces=lambda e: e.get("event") == log_event(plan) and any(
            (s or {}).get("page") == page for s in e.get("sources") or ())))
    if players is not None:
        plan.pages.inactives.write_text(json.dumps({
            "season": plan.season, "week": plan.week, "set": plan.master.isoformat(), "players": list(players),
            "note": inactive_note(plan, players), "page": page}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(plan.pages.inactives)
    _, source, _ = plan.compiled()
    record = {"season": plan.season, "week": plan.week, "applied": plan.master.isoformat(), "page": page,
              "page_sha256": page_digest(plan.text), "call_sheet_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
              "before": before, "set": _set(after, before), "labels_cleared": [p for p, _ in cleared],
              # Where every emitted call, defensive row and decision came from (a page line or a carried
              # frozen item), and his reasons, kept as author intent: they never reach the call sheet.
              "source_map": source, "intent": dict(game_plan.intent(plan.choices), known=plan.master.isoformat()),
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
                              "summary": "Stone set %s on his %s Game Plan, checked and applied %s"
                                         % (what, plan.label(), long_date(plan.master))}
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


def changed_on_game_day(root, season, week):
    """The depth or inactives changes Stone made on My Responses after the week's Game Plan was applied
    (scripts/change_game_day.py, the week's ``game_day_changes.json``); [] when none."""
    from runtime import game_weeks
    from runtime.decisions import week_pages
    from runtime.seasons import SeasonPaths
    postseason = game_weeks.is_postseason(SeasonPaths(season, Path(root).resolve()), week)
    path = week_pages(season, week, Path(root).resolve(), postseason=postseason).game_day_changes
    if not path.is_file():
        return []
    return list(json.loads(path.read_text(encoding="utf-8")).get("changes") or [])


def apply(root, season, week, rebuild_pages=True, report=None):
    """Check the week's page and apply it; ``report`` (a dict) is told when nothing is set because
    an item still waits on an exam (``waiting``). A week with a game-day change recorded is not
    applied again: the change was made against the plan as applied."""
    changed = changed_on_game_day(root, season, week)
    if changed:
        from runtime import game_weeks
        from runtime.seasons import SeasonPaths
        name = (game_weeks.round_name(week) if game_weeks.is_postseason(SeasonPaths(season, Path(root).resolve()), week)
                else "Week %d" % week)
        when = sorted({c["date"] for c in changed})
        return ["%s: Stone changed the depth or inactives on My Responses after the Game Plan was applied (%s); the "
                "plan stays as it was set, and a further change is made there"
                % (name, ", ".join(long_date(date.fromisoformat(d)) for d in when))], []
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
    from runtime import game_weeks
    for game in game_weeks.club_games(paths, JAX):     # the season's games, its playoff games set so far
        week = game["week"]
        pages = week_pages(season, week, root, postseason=game.get("game_type") == "postseason")
        record = game_plan.applied_record(pages.applied)
        label = "%s Game Plan" % game_weeks.label(game)
        inactives = game_plan.applied_record(pages.inactives)
        listed = chart.get("game_day_inactives") or {}
        if inactives is not None and listed.get("week") == week and \
                list(listed.get("players") or []) != list(inactives.get("players") or []):
            errors.append("%s: the depth chart's inactives are not the week's inactives as set" % game_weeks.label(game))
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
            errors.append("%s: the Game Week Briefing is issued, but the decision queue holds no game-plan item "
                          "for the week (python scripts/open_game_week.py opens it)" % wk.label())
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
    from runtime import game_weeks
    from runtime.seasons import SeasonPaths
    name = (game_weeks.round_name(args.week) if game_weeks.is_postseason(SeasonPaths(args.season, root), args.week)
            else "Week %d" % args.week)
    print("GAME PLAN: APPLIED  %s, %d" % (name, args.season))
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
