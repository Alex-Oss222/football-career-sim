"""The desk's season summary and the season calendar (scripts/render_career_views.py builds both).

The desk's "Season at a glance", "Player production" and "Medical and
availability" sections come from the closed games and the roster record through
runtime/season_summary.py, the same words the statistics index (built by
scripts/render_season_stats.py) and the injury report (scripts/render_week_pages.py)
show. The calendar puts the current month and the next games first, above the
season's full-year dates. These functions format stored football facts; they
neither decide anything nor alter season state.
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
from runtime import people, roster as roster_record, season_summary as summary
from scripts.render_season_stats import load_receipts

CLUB = "Jacksonville Jaguars"


def _link(page, target, text):
    page, target = Path(page), Path(target)
    destination = os.path.relpath(target, page.parent).replace(os.sep, "/")
    return "[%s](%s)" % (text, destination)


def _player_link(ctx, page, name):
    target = ctx.paths.record("player_profiles") / (people.slugify(name) + ".md")
    return _link(page, target, name) if target.is_file() else name


def _facts(ctx):
    if hasattr(ctx, "_season_hub_facts"):
        return ctx._season_hub_facts
    source = load_receipts(ctx.paths.receipts) if ctx.paths.receipts.is_dir() else []
    # Only complete NFL game results belong in the current summary.
    receipts = [r for r in source if r.get("home") in DIVISION_OF and r.get("away") in DIVISION_OF
                and isinstance(r.get("final_score"), dict) and isinstance(r.get("team_stats"), dict)]
    book = aggregate_receipts(receipts)
    team = book.get("teams", {}).get(CLUB, {})
    games = summary.club_games(receipts, CLUB)
    records = compute(receipts)
    roster = roster_record.load(ctx.paths.roster)
    ctx._season_hub_facts = book, team, games, records, roster
    return ctx._season_hub_facts


def _medical_table(ctx, page, rows):
    result = ["| Player | Status | Next medical date |", "|---|---|---|"]
    for r in rows:
        source = (r.get("sources") or {}).get("availability")
        status = summary.medical_status(r)
        if source:
            status = _link(page, ctx.root / source, status)
        result.append("| %s | %s | %s |" % (_player_link(ctx, page, r["name"]), status,
                                            summary.next_dates(r, ctx.master)))
    return result


def dashboard_sections(ctx):
    page = ctx.paths.desk
    _, team, games, standings, roster = _facts(ctx)
    first, points, efficiency = summary.glance(team, games, standings, CLUB)
    stats = ctx.paths.record("statbook.md")
    medical = ctx.paths.record("medical/current_injury_report.md")
    standing = ctx.paths.record("standings.md")
    lines = ["## Season at a glance", "", "**%s.** %s. %s." % (first, points, efficiency),
             "", _link(page, stats, "Season statistics") + " · " + _link(page, standing, "Division standings"),
             "", "## Player production", "",
             "| Category | Player | Through the last game |", "|---|---|---|"]
    production = summary.leaders(team)
    for label, name, value in production:
        lines.append("| %s | %s | %s |" % (label, _player_link(ctx, page, name), value))
    if not production:
        lines.append("| — | No games played | — |")
    lines += ["", "## Medical and availability", ""]
    injured = summary.held(roster)
    lines += _medical_table(ctx, page, injured) if injured else ["No active-roster medical instructions."]
    lines += ["", "Projected dates require medical clearance. " + _link(page, medical, "Full injury report"), "", ""]
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
    fixture_page = ctx.paths.record("schedule/fixtures.md")
    fixture_link = _link(page, fixture_page, "released fixtures")
    remainder = re.sub(r"\[historical fixtures\]\([^)]+\.json\)", lambda _: fixture_link, remainder)
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
    # The game on the master date stays upcoming until the clock says it was played
    # (render_career_views.last_and_next reads the clock the same way).
    after = re.search(r"after the Week (\d+) game", ctx.clock)
    next_games = [g for g in ctx.games if date.fromisoformat(g["date"]) > ctx.master
                  or (date.fromisoformat(g["date"]) == ctx.master
                      and not (after and int(after[1]) == g["week"]))][:5]
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
