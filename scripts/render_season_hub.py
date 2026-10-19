"""Readable season summaries built from game, roster, medical and calendar records.

These functions format existing football facts. They neither resolve decisions
nor alter season state. See the owning records for event detail.
"""
from __future__ import annotations

import calendar as month_calendar
from datetime import date
import os
from pathlib import Path
import re

from runtime.league import DIVISION_OF
from runtime.standings import compute
from runtime.statbook import aggregate_receipts
from runtime import people, roster as roster_record
from scripts.render_season_stats import load_receipts

CLUB = "Jacksonville Jaguars"


def _link(page, target, text):
    page, target = Path(page), Path(target)
    destination = os.path.relpath(target, page.parent).replace(os.sep, "/")
    return "[%s](%s)" % (text, destination)


def _player_link(ctx, page, name):
    target = ctx.paths.career / "Team_Operations/Team/Player_Cards" / (people.slugify(name) + ".md")
    return _link(page, target, name) if target.is_file() else name


def _facts(ctx):
    source = load_receipts(ctx.paths.receipts) if ctx.paths.receipts.is_dir() else []
    # Only complete NFL game results belong in the current summary.
    receipts = [r for r in source if r.get("home") in DIVISION_OF and r.get("away") in DIVISION_OF
                and isinstance(r.get("final_score"), dict) and isinstance(r.get("team_stats"), dict)]
    book = aggregate_receipts(receipts)
    team = book.get("teams", {}).get(CLUB, {})
    games = sorted((r for r in receipts if CLUB in (r["home"], r["away"])), key=lambda r: int(r["week"]))
    records = compute(receipts)
    roster = roster_record.load(ctx.paths.roster)
    return book, team, games, records, roster


def _record(games):
    wins = losses = ties = 0
    for r in games:
        score = r["final_score"]
        opponent = r["away"] if r["home"] == CLUB else r["home"]
        if score[CLUB] > score[opponent]:
            wins += 1
        elif score[CLUB] < score[opponent]:
            losses += 1
        else:
            ties += 1
    return "%d-%d" % (wins, losses) + ("-%d" % ties if ties else "")


def _summary(team, games, standings):
    own, against = team.get("team_stats") or {}, team.get("opponent_stats") or {}
    played = len(games)
    if not played:
        return ("No games played", "Not established", "Not established")
    division = standings["division_ranks"][DIVISION_OF[CLUB]]
    position = division.index(CLUB) + 1
    conf = standings["conferences"]["AFC"]
    afc_order = conf["division_winners"] + conf["others"]
    afc_seed = afc_order.index(CLUB) + 1
    record = _record(games)
    first = "%s · %d%s AFC South · AFC position %d" % (
        record, position, "st" if position == 1 else "nd" if position == 2 else "rd" if position == 3 else "th", afc_seed)
    points = "%d scored · %d allowed · %+d differential" % (
        own.get("points", 0), against.get("points", 0), own.get("points", 0) - against.get("points", 0))
    conversions = own.get("third_down_conversions", 0)
    tries = own.get("third_down_attempts", 0)
    allowed = against.get("third_down_conversions", 0)
    chances = against.get("third_down_attempts", 0)
    performance = "%0.1f points per game · %0.1f%% on third down · %0.1f%% allowed" % (
        own.get("points", 0) / played, 100 * conversions / tries if tries else 0,
        100 * allowed / chances if chances else 0)
    return first, points, performance


def _highlights(team):
    stats = team.get("players") or {}
    categories = (
        ("Passing", "passing_yards", "passing_yards", "passing_touchdowns", "interceptions_thrown"),
        ("Rushing", "rushing_yards", "rushing_yards", "rushing_touchdowns", None),
        ("Receiving", "receiving_yards", "receiving_yards", "receptions", "receiving_touchdowns"),
        ("Tackling", "tackles", "tackles", "sacks", None),
    )
    results = []
    for label, field, shown, other, extra in categories:
        ranked = [(n, stats[n]) for n in stats if stats[n].get(field, 0)]
        if not ranked:
            continue
        name, row = max(ranked, key=lambda pair: (pair[1].get(field, 0), pair[0]))
        value = "%s %s" % (format(row.get(shown, 0), ","), {
            "passing_yards": "pass yds", "rushing_yards": "rush yds",
            "receiving_yards": "rec yds", "tackles": "tackles"}[shown])
        extra_parts = []
        if other in ("passing_touchdowns", "rushing_touchdowns", "receiving_touchdowns"):
            extra_parts.append("%d TD" % row.get(other, 0))
        elif other == "receptions":
            extra_parts.append("%d catches" % row.get(other, 0))
        elif other == "sacks" and row.get("sacks"):
            extra_parts.append("%s sacks" % row["sacks"])
        if extra == "interceptions_thrown":
            extra_parts.append("%d INT" % row.get(extra, 0))
        elif extra == "receiving_touchdowns":
            extra_parts.append("%d TD" % row.get(extra, 0))
        if extra_parts:
            value += " · " + ", ".join(extra_parts)
        results.append((label, name, value))
    return results


def _active_medical(roster):
    return [p for p in roster.get("players") or ()
            if p.get("list") == "active" and
            (p.get("availability", "").startswith("Out,") or
             p.get("availability", "").startswith("Independent medical hold"))]


def _reserve_medical(roster):
    return [p for p in roster.get("players") or () if p.get("list") == "reserve"]


def _medical_status(row):
    text = row.get("availability", "")
    if text.startswith("Independent medical hold"):
        match = re.search(r"^Independent medical hold,\s*([^:]+):\s*([^,;]+)", text)
        return "Independent hold · %s" % match.group(2).strip() if match else "Independent medical hold"
    match = re.match(r"Out,\s*([^:]+):\s*([^,;]+)", text)
    return "Out · %s (%s)" % (match.group(2).strip(), match.group(1).strip()) if match else "Under medical instruction"


def _medical_dates(row):
    text = row.get("availability", "")
    projected = re.search(r"projected return\s+([A-Z][a-z]+\s+\d{1,2}(?:,\s+\d{4})?)", text, re.I)
    reassess = re.search(r"reassessment\s+([A-Z][a-z]+\s+\d{1,2}(?:,\s+\d{4})?)", text, re.I)
    result = []
    if reassess:
        result.append("Review " + reassess.group(1))
    if projected:
        result.append("Projected " + projected.group(1))
    return "; ".join(result) or "No new date communicated"


def _medical_table(ctx, page, roster, rows):
    result = ["| Player | Status | Next medical date |", "|---|---|---|"]
    for r in rows:
        name = _player_link(ctx, page, r["name"])
        source = (r.get("sources") or {}).get("availability")
        if source:
            status = _link(page, ctx.root / source, _medical_status(r))
        else:
            status = _medical_status(r)
        result.append("| %s | %s | %s |" % (name, status, _medical_dates(r)))
    return result


def medical_page(ctx):
    page = ctx.paths.career / "Team_Operations/Medical/current_injury_report.md"
    _, _, _, _, roster = _facts(ctx)
    active, reserve = _active_medical(roster), _reserve_medical(roster)
    lines = ["# Medical and availability", "", "As of %s. Medical staff control participation and return clearance." %
             ctx.master.strftime("%B %d, %Y").replace(" 0", " "), "",
             "## Players on the active roster", ""]
    lines += _medical_table(ctx, page, roster, active) if active else ["No current medical limitations reported."]
    lines += ["", "A projected return is not clearance to participate.", "",
              "## Players on reserve/injured", ""]
    lines += _medical_table(ctx, page, roster, reserve) if reserve else ["None."]
    lines += ["", _link(page, page.parent / "medical_history.md", "Medical history") +
              " · " + _link(page, ctx.paths.record("depth_chart.md"), "Depth chart") +
              " · " + _link(page, ctx.paths.desk, "Head coach's desk"), ""]
    return "\n".join(lines)


def statistics_page(ctx):
    page = ctx.paths.career / "Regular_Season/Statistics/README.md"
    book, team, games, standings, _ = _facts(ctx)
    first, points, performance = _summary(team, games, standings)
    lines = ["# %d regular-season statistics" % ctx.season, "",
             "Jacksonville Jaguars · Through Week %d." % book.get("through_week", 0), "",
             "## Team at a glance", "", "| Season | Scoring | Efficiency |", "|---|---|---|",
             "| %s | %s | %s |" % (first, points, performance), "",
             "## Games played", "", "| Week | Opponent | Result |", "|---:|---|---:|"]
    for r in games:
        week = int(r["week"])
        opponent = r["away"] if r["home"] == CLUB else r["home"]
        score = r["final_score"]
        result = "W" if score[CLUB] > score[opponent] else "L" if score[CLUB] < score[opponent] else "T"
        label = ("vs " if r["home"] == CLUB else "at ") + opponent
        game = ctx.paths.week_folder(week) / "output.md"
        lines.append("| %d | %s | %s %d-%d |" % (
            week, _link(page, game, label) if game.is_file() else label, result,
            score[CLUB], score[opponent]))
    if not games:
        lines.append("| — | No completed games | — |")
    lines += ["", "## Player leaders", "", "| Category | Player | Season total |", "|---|---|---:|"]
    for label, name, total in _highlights(team):
        lines.append("| %s | %s | %s |" % (label, _player_link(ctx, page, name), total))
    lines += ["", "## Full statistics", ""]
    dests = (("Jacksonville player statistics", "records/team_player_stats.md"),
             ("Team comparisons", "records/team_stats.md"),
             ("League leaders", "records/league_leaders.md"),
             ("League player statistics", "records/league_player_stats.md"),
             ("Play-call statistics", "records/play_call_stats.md"))
    lines += [" · ".join(_link(page, page.parent / p, label) for label, p in dests), "",
              _link(page, ctx.paths.career / "Regular_Season/standings.md", "Standings") +
              " · " + _link(page, ctx.paths.desk, "Head coach's desk"), ""]
    return "\n".join(lines)


def dashboard_sections(ctx):
    page = ctx.paths.desk
    _, team, games, standings, roster = _facts(ctx)
    first, points, efficiency = _summary(team, games, standings)
    stats = ctx.paths.career / "Regular_Season/Statistics/README.md"
    medical = ctx.paths.career / "Team_Operations/Medical/current_injury_report.md"
    standing = ctx.paths.career / "Regular_Season/standings.md"
    lines = ["## Season at a glance", "", "**%s.** %s. %s." % (first, points, efficiency),
             "", _link(page, stats, "Season statistics") + " · " + _link(page, standing, "Division standings"),
             "", "## Player production", "",
             "| Category | Player | Through the last game |", "|---|---|---|"]
    for label, name, value in _highlights(team):
        lines.append("| %s | %s | %s |" % (label, _player_link(ctx, page, name), value))
    if len(lines) and not _highlights(team):
        lines.append("| — | No games played | — |")
    lines += ["", "## Medical and availability", ""]
    injured = _active_medical(roster)
    lines += _medical_table(ctx, page, roster, injured) if injured else ["No active-roster medical instructions."]
    lines += ["", "Projected dates require medical clearance. " + _link(page, medical, "Full medical report"), ""]
    return "\n".join(lines)


def insert_dashboard(ctx, desk):
    marker = "## Coming up\n"
    if marker not in desk:
        raise ValueError("Head coach's desk is missing its Coming up section")
    return desk.replace(marker, dashboard_sections(ctx) + marker, 1)


def calendar_page(ctx):
    page = ctx.paths.calendar
    current = page.read_text(encoding="utf-8")
    section = "## Early offseason\n"
    if section not in current:
        raise ValueError("The season calendar has no full-year date inventory")
    remainder = section + current.split(section, 1)[1]
    remainder = remainder.replace("branch camp report", "camp report")
    remainder = remainder.replace(
        "[historical fixtures](../../data/2014/Regular_Season/Schedule/fixtures.json)",
        "[released fixtures](Regular_Season/Schedule/fixtures.md)")
    month = ctx.master.month
    weeks = month_calendar.monthcalendar(ctx.master.year, month)
    games = {date.fromisoformat(g["date"]): g for g in ctx.games}
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    lines = ["# Jacksonville %d calendar" % ctx.season, "",
             "Dates and appointments for the football year. Times are Eastern. Scheduled work is not a completed result.",
             "", "## %s %d" % (ctx.master.strftime("%B"), ctx.master.year), "",
             "| " + " | ".join(days) + " |",
             "| " + " | ".join("---" for _ in days) + " |"]
    for week in weeks:
        cells = []
        for d in week:
            if not d:
                cells.append(" ")
                continue
            when = date(ctx.master.year, month, d)
            game = games.get(when)
            label = str(d)
            if game:
                away, home = game["away"], game["home"]
                other = away if home == CLUB else home
                place = "vs" if home == CLUB else "at"
                label += " " + _link(page, ctx.paths.week_folder(game["week"]) / "README.md", "%s %s" % (place, other))
            if when == ctx.master:
                label = "**%s**" % label
            cells.append(label)
        lines.append("| " + " | ".join(cells) + " |")
    lines += ["", "## Upcoming dates", "", "| Date | Event |", "|---|---|"]
    next_games = [g for g in ctx.games if date.fromisoformat(g["date"]) > ctx.master][:5]
    for g in next_games:
        when = date.fromisoformat(g["date"])
        other = g["away"] if g["home"] == CLUB else g["home"]
        place = "vs" if g["home"] == CLUB else "at"
        lines.append("| %s | %s |" % (
            when.strftime("%b %d").replace(" 0", " "),
            _link(page, ctx.paths.week_folder(g["week"]) / "README.md",
                  "Week %d %s %s" % (g["week"], place, other))))
    lines += ["", "## Full-year dates", "", remainder]
    return "\n".join(lines).rstrip() + "\n"
