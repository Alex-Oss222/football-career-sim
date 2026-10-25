"""A synthetic closed week with Jacksonville injuries, in a throwaway copy of the checkout only
(rebuild step 5, D1).

The copy's open week (the first Jacksonville game without a receipt) is closed by relabelling the
previous Jacksonville week's closed games onto its fixtures, game for game, as
tests/test_week_close_pages.py does, Jacksonville's game first; when that week had more clubs on a
bye, the open week's other fixtures take the background games of a closed week with enough of them.
When closing the open week would pass over an open bye, open the bye or leave no Jacksonville game
after it (the season's last game, or every game closed) and the copy's clock has not reached its
game day, the latest closed Jacksonville week is closed again in place from its own receipt instead
(the week before it when no Jacksonville game is left after it or its close opens the bye, the
games after it then unplayed by ``unplay``). Either way the next game's own Game Plan and inactives
questions, which a close's page rebuild opens after the roster question, are left for that rebuild
to open. The Jacksonville injuries are set to the severities a test names (in the form of the game's
own injury records, else any closed game's), the master date moves to after the game and each
injured player's medical communication is recorded on the roster record in the close's one format
(runtime/week_pages.availability_entry), with its incident record written. Weeks and dates come from
the fixtures, never from today's date. Nothing is played and the real repository is never touched.
"""
from datetime import date, timedelta
import json
from pathlib import Path
import re
import shutil
import tempfile

from runtime import bye_week, decision_queue, decisions, game_report, open_events, week_pages
from runtime.seasons import SeasonPaths
from runtime.week_inputs import AVAILABLE_TEXT, event_id, receipt_name

ROOT = Path(__file__).resolve().parents[1]
JAX = "Jacksonville Jaguars"
IGNORED = (".git", ".sim_cache", "__pycache__", ".pytest_cache")
STATE = "state/05_Current_Season_State.md"


def copy_repo(test):
    tmp = tempfile.TemporaryDirectory(dir=ROOT.parent)
    test.addCleanup(tmp.cleanup)
    root = Path(tmp.name) / "repo"
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(*IGNORED), symlinks=True)
    return root.resolve()


def relabel(value, names):
    if isinstance(value, dict):
        return {relabel(k, names): relabel(v, names) for k, v in value.items()}
    if isinstance(value, list):
        return [relabel(v, names) for v in value]
    if isinstance(value, str):
        return names.get(value, value)
    return value


def ours_first(games):
    return sorted(games, key=lambda g: (JAX not in (g["away"], g["home"]), g["away"]))


def closed(paths, game):
    return (paths.receipts / receipt_name(game)).is_file()


def open_week(root, season):
    """(week, fixture) of the copy's first Jacksonville game without a receipt, or (None, None)."""
    paths = SeasonPaths(season, root)
    game = next((g for g in open_events.club_fixtures(season, root) if not closed(paths, g)), None)
    return (int(game["week"]), game) if game else (None, None)


def week_to_close(root, season):
    """The Jacksonville week the copy closes: its open week once the copy's clock has reached its game
    day (a test closing the week it prepared), or while no bye is open, a Jacksonville game is left
    after it and its close does not open the bye; otherwise the latest closed Jacksonville week, closed
    again in place, or the week before it when no Jacksonville game is left after it or its close
    opens the bye."""
    paths = SeasonPaths(season, root)
    games = open_events.club_fixtures(season, root)
    last = max(int(g["week"]) for g in games)
    before_bye = {int(bye_week.around(season, bye, root)[0]["week"]) for bye in bye_week.byes(season, root)}
    week, game = open_week(root, season)
    if game is not None:
        if open_events.master_clock(root).date >= date.fromisoformat(game["date"]):
            return week
        if open_events.active_bye(paths, root) is None and week < last and week not in before_bye:
            return week
    played = sorted(int(g["week"]) for g in games if closed(paths, g))
    return played[-1] if played[-1] < last and played[-1] not in before_bye else played[-2]


def unplay(root, season, week):
    """The copy's games from ``week`` on unplayed again, the postseason's too: their receipts removed,
    and each such Jacksonville game left as not yet prepared, its Game Report's box score naming no
    game, its applied Game Plan records (call sheet, applied plan, inactives, pregame sections)
    removed and its briefings issued after the Jacksonville game before ``week`` withdrawn, the latest
    kept one current; a player whose medical communication rests on an incident after that game is
    back to no communicated restriction, on the medical history, and the depth chart's log keeps the
    entries recorded by that game."""
    paths = SeasonPaths(season, root)
    through = max(((int(g["week"]), g["date"]) for g in open_events.club_fixtures(season, root)
                   if int(g["week"]) < week), default=(0, ""))[1]
    for path in sorted(paths.receipts.glob("*.json")) + sorted(paths.postseason_receipts.glob("*.json")):
        receipt = json.loads(path.read_text(encoding="utf-8"))
        if path.parent == paths.receipts and int(receipt["week"]) < week:
            continue
        path.unlink()
        if JAX not in (receipt["away"], receipt["home"]):
            continue
        pages = decisions.week_pages(season, int(receipt["week"]), root)
        for record in (pages.call_sheet, pages.applied, pages.inactives, pages.pregame):
            record.unlink(missing_ok=True)
        if pages.report.is_file():
            text = pages.report.read_text(encoding="utf-8")
            unnamed = "<!-- box-score event=%s team=%s -->" % (game_report.EVENT_PLACEHOLDER,
                                                               game_report.TEAM_PLACEHOLDER)
            pages.report.write_text(re.sub(r"<!-- box-score event=%s team=.+? -->" % re.escape(receipt["event_id"]),
                                           unnamed, text), encoding="utf-8")
        record = pages.data / "briefings.json"
        if record.is_file():
            data = json.loads(record.read_text(encoding="utf-8"))
            kept = [e for e in data["issued"] if e["date"] <= through]
            for entry in data["issued"][len(kept):]:
                (pages.folder / entry["file"]).unlink(missing_ok=True)
            if kept:
                (pages.folder / kept[-1]["file"]).replace(pages.briefing)
                kept[-1]["file"] = pages.briefing.name
            record.write_text(json.dumps(dict(data, issued=kept), indent=1, ensure_ascii=False) + "\n",
                              encoding="utf-8")
    history = paths.record("medical/medical_history.md").resolve().relative_to(Path(root).resolve()).as_posix()
    data = json.loads(paths.roster.read_text(encoding="utf-8"))
    for row in data["players"]:
        source = (row.get("sources") or {}).get("availability", "")
        incident = re.search(r"/incidents/.+_(\d{4}-\d{2}-\d{2})\.md$", source)
        if incident and incident.group(1) > through:
            row["availability"], row["sources"]["availability"] = AVAILABLE_TEXT, history
    paths.roster.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    log = paths.record("team/depth_chart/update_log.json")
    data = json.loads(log.read_text(encoding="utf-8"))
    data["entries"] = [e for e in data["entries"] if e["recorded"] <= through]
    log.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def unopen(root, season):
    """The copy's next Jacksonville game without the questions its week opened after the roster
    question was raised: its open Game Plan and inactives items (the live close's page rebuild opened
    them when the next game is the live open one), removed from the queue for the copy's own page
    rebuild to open again."""
    week, _ = open_week(root, season)
    if week is None:
        return
    queue = decision_queue.load(root)
    held = decision_queue.event("week_inputs", season, week)
    items = [i for i in queue["items"] if i.get("class") not in ("weekly_game_plan", "game_day_inactives")
             or not decision_queue.holds(i, held)]
    if len(items) < len(queue["items"]):
        decision_queue.save(root, dict(queue, items=items))


def donors(paths, week, count):
    """The closed games relabelled onto ``count`` fixtures of ``week``, Jacksonville's first: the
    previous Jacksonville week's; when that week has fewer (more clubs on a bye), its Jacksonville game
    and the background games of the latest closed week with enough of them, a week its opponent does
    not play in first, so that one club's players stand for one club only."""
    fixtures = paths.regular_games()
    previous = max(g["week"] for g in fixtures if g["week"] < week and JAX in (g["away"], g["home"]))
    out = ours_first(g for g in fixtures if g["week"] == previous)
    if len(out) >= count:
        return out
    background = {w: sorted((g for g in fixtures if g["week"] == w and JAX not in (g["away"], g["home"])
                             and closed(paths, g)), key=lambda g: g["away"]) for w in range(week - 1, 0, -1)}
    enough = [w for w, games in background.items() if len(games) >= count - 1]
    other = {out[0]["away"], out[0]["home"]} - {JAX}
    pick = next((w for w in enough if not any(other & {g["away"], g["home"]} for g in background[w])), enough[0])
    return out[:1] + background[pick]


def injure(receipt, injuries, paths):
    """``receipt`` with Jacksonville's injuries replaced by ``injuries``, each in the form of one of
    the game's own (Jacksonville's, else its opponent's, else any closed game's)."""
    others = [i for i in receipt["injuries"] if i.get("team") != JAX]
    template = [i for i in receipt["injuries"] if i.get("team") == JAX] or [
        dict(i, team=JAX) for i in others or every_injury(paths)]
    made = []
    for n, (player, severity, days) in enumerate(injuries):
        injury = dict(template[n % len(template)])
        injury.update({"player": player, "severity": severity, "return_days": days, "reassessment_days": 6,
                       "restriction": "out", "removed": True})
        made.append(injury)
    receipt["injuries"] = others + made
    return receipt


def close_open_week(root, season, injuries):
    """Close the copy's week (``week_to_close``): an open week from closed games, a closed week again
    from its own receipt, the games after it unplayed first; ``injuries`` is [(player name, severity,
    days to return)] given to Jacksonville's injuries in order (each a player on the active roster).
    Returns (week, game, Jacksonville's receipt)."""
    paths = SeasonPaths(season, root)
    week = week_to_close(root, season)
    game = next(g for g in open_events.club_fixtures(season, root) if int(g["week"]) == week)
    ours = None
    if closed(paths, game):
        unplay(root, season, week + 1)
        ours = injure(json.loads((paths.receipts / receipt_name(game)).read_text(encoding="utf-8")), injuries, paths)
        (paths.receipts / receipt_name(game)).write_text(json.dumps(ours, indent=1), encoding="utf-8")
    else:
        new = ours_first(g for g in paths.regular_games() if g["week"] == week)
        for before, after in zip(donors(paths, week, len(new)), new):
            receipt = json.loads((paths.receipts / receipt_name(before)).read_text(encoding="utf-8"))
            names = {before["away"]: after["away"], before["home"]: after["home"]}
            if JAX in (before["away"], before["home"]):
                other = before["home"] if before["away"] == JAX else before["away"]
                names = {other: after["home"] if after["away"] == JAX else after["away"]}
            receipt = relabel(receipt, names)
            for key in ("defensive_calls", "defensive_call_stats", "decision_policies"):
                receipt.pop(key, None)
            receipt.update({"week": week, "away": after["away"], "home": after["home"],
                            "matchup": "%s at %s" % (after["away"], after["home"]),
                            "event_id": event_id(after, season=season)})
            if JAX in (after["away"], after["home"]):
                ours = injure(receipt, injuries, paths)
            (paths.receipts / receipt_name(after)).write_text(json.dumps(receipt, indent=1), encoding="utf-8")
    unopen(root, season)
    played = date.fromisoformat(game["date"])
    set_clock(root, "%s, after the Week %d game" % (week_pages.long_date(played), week))
    roster = paths.roster
    data = json.loads(roster.read_text(encoding="utf-8"))
    data["as_of"] = {"date": played.isoformat(), "event": "after the Week %d game" % week}
    season_pages = week_pages.Season(root, season)
    result = next(r for r in season_pages.receipts.values() if int(r["week"]) == week and JAX in (r["away"], r["home"]))
    for injury in (i for i in result["injuries"] if i.get("team") == JAX):
        row = next(p for p in data["players"] if p["name"] == injury["player"])
        row["availability"], source = week_pages.availability_entry(season_pages, result, injury)
        row.setdefault("sources", {})["availability"] = source
    roster.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    season_pages = week_pages.Season(root, season)
    for rel, text in week_pages.incidents(season_pages).items():
        path = root / rel
        if not path.is_file():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    return week, game, ours


def every_injury(paths):
    """Every injury the copy's closed games record (a game with none of Jacksonville's or its
    opponent's lends its form from these)."""
    return [i for path in sorted(paths.receipts.glob("*.json"))
            for i in json.loads(path.read_text(encoding="utf-8")).get("injuries") or ()]


def set_clock(root, line):
    path = Path(root) / STATE
    if Path(root).resolve() == ROOT.resolve():
        raise ValueError("the real master date is never moved by a test")
    text = path.read_text(encoding="utf-8")
    path.write_text(re.sub(r"^\| Master date/time \| .+? \|\s*$", "| Master date/time | %s |" % line, text, count=1,
                           flags=re.M), encoding="utf-8")


def midweek(root, day, hour, week, minute=0):
    clock = "%d%s %s" % (hour % 12 or 12, ":%02d" % minute if minute else "", "a.m." if hour < 12 else "p.m.")
    set_clock(root, "%s, after the %s ET record of the Week %d preparation (a test record)" % (
        week_pages.long_date(day), clock, week))
