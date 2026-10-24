"""A synthetic closed week with Jacksonville injuries, in a throwaway copy of the checkout only
(rebuild step 5, D1).

The copy's open week (the first Jacksonville game without a receipt) is closed by relabelling the
previous week's closed games onto its fixtures, game for game, as tests/test_week_close_pages.py
does; the Jacksonville injuries are set to the severities a test names, the master date moves to
after the game and each injured player's medical communication is recorded on the roster record in
the close's one format (runtime/week_pages.availability_entry), with its incident record written.
Weeks and dates come from the fixtures, never from today's date. Nothing is played and the real
repository is never touched.
"""
from datetime import date, timedelta
import json
from pathlib import Path
import re
import shutil
import tempfile

from runtime import open_events, week_pages
from runtime.seasons import SeasonPaths
from runtime.week_inputs import event_id, receipt_name

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


def open_week(root, season):
    paths = SeasonPaths(season, root)
    game = next(g for g in open_events.club_fixtures(season, root) if not (paths.receipts / receipt_name(g)).is_file())
    return int(game["week"]), game


def close_open_week(root, season, injuries):
    """Close the copy's open week from the previous week's games; ``injuries`` is
    [(player name, severity, days to return)] given to Jacksonville's injuries in order (each a
    player on the active roster). Returns (week, game, Jacksonville's receipt)."""
    paths = SeasonPaths(season, root)
    week, game = open_week(root, season)
    fixtures = paths.regular_games()
    new = ours_first(g for g in fixtures if g["week"] == week)
    previous = max(g["week"] for g in fixtures if g["week"] < week and any(
        JAX in (x["away"], x["home"]) for x in fixtures if x["week"] == g["week"]))
    old = ours_first(g for g in fixtures if g["week"] == previous)
    ours = None
    for before, after in zip(old, new):
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
            ours = receipt
            template = [i for i in receipt["injuries"] if i.get("team") == JAX]
            others = [i for i in receipt["injuries"] if i.get("team") != JAX]
            made = []
            for n, (player, severity, days) in enumerate(injuries):
                injury = dict(template[n % len(template)])
                injury.update({"player": player, "severity": severity, "return_days": days, "reassessment_days": 6,
                               "restriction": "out", "removed": True})
                made.append(injury)
            receipt["injuries"] = others + made
        (paths.receipts / receipt_name(after)).write_text(json.dumps(receipt, indent=1), encoding="utf-8")
    for extra in (g for g in new[len(old):]):
        raise AssertionError("the open week has more games than the week before it: %s" % extra)
    played = date.fromisoformat(game["date"])
    set_clock(root, "%s, after the Week %d game" % (week_pages.long_date(played), week))
    roster = paths.roster
    data = json.loads(roster.read_text(encoding="utf-8"))
    data["as_of"] = {"date": played.isoformat(), "event": "after the Week %d game" % week}
    season_pages = week_pages.Season(root, season)
    closed = next(r for r in season_pages.receipts.values() if int(r["week"]) == week and JAX in (r["away"], r["home"]))
    for injury in (i for i in closed["injuries"] if i.get("team") == JAX):
        row = next(p for p in data["players"] if p["name"] == injury["player"])
        row["availability"], source = week_pages.availability_entry(season_pages, closed, injury)
        row.setdefault("sources", {})["availability"] = source
    roster.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    season_pages = week_pages.Season(root, season)
    for rel, text in week_pages.incidents(season_pages).items():
        path = root / rel
        if not path.is_file():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    return week, game, ours


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
