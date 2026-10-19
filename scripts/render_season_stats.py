#!/usr/bin/env python3
"""Rebuild the public season-stat views from closed-game stat receipts.

From 2014 every page is written clean (docs/rebuild_plan.md, rule 4): football
words only, with no file, script, version or system names. The figures, the
orders and the rankings are the same computation as before; only the words
around them change, and 2013 keeps its pages byte for byte. The statistical
band audit is a check for the game code, not a page to read, so from 2014 it is
written to the data area (``view_path``); the season folder's copy as it stood
after 2014 Week 5 stays there as history (rebuild rule 1: the Week 1 to 5 game
reports link to it) and is never rewritten. The statbook index and the records
index are built here too from 2014, so the closed-week count they show is
never kept by hand; the statbook index (the Statistics folder's README, which
only this script writes) leads with the club's season at a glance, its games
and its leaders, in the words the desk uses (runtime/season_summary.py).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.bands import (
    KERNEL_2013_6_LABEL, KNOWN_DETECTION_BOUND, LEGACY_LABEL, audit, audit_drive_model, audit_field_position,
    audit_ball_security, audit_fourth_down, audit_penalties, audit_injuries, audit_scoring, audit_yardage, coherence, cohorts, current_cohorts, known_detections, known_status, provisional_detections,
)
from runtime.calibration_base import cohort_base
from runtime.stat_tables import (
    POSITION_GROUPS, avg, combine, g, pct, position_sections, rating_value,
    time_text,
)
from runtime.seasons import page_link
from runtime.statbook import aggregate_receipts, leaders

# NFL passing qualifier: 14 attempts per team game (Wikipedia, "Passer
# rating"; NFL leaderboard minimum). Rushing and receiving average
# qualifiers are not applied until verified from a dated source.
PASSING_ATTEMPTS_PER_TEAM_GAME = 14
# The first season whose statistics pages are written clean (2013's are history).
CLEAN_FROM = 2014
# From 2014 these views are system files: written to the data area, never a page to read.
SYSTEM_VIEWS = ("season_totals.json", "calibration_audit.md")
# The statbook index (the logical statbook.md: the Statistics folder's README) and the records
# index, built from 2014.
STATBOOK, RECORDS_INDEX = "statbook.md", "README.md"


def clean(year):
    return year >= CLEAN_FROM


def view_path(paths, name):
    """Where a generated statistics view is written: the statbook index at the season's statbook
    page, a system view (``SYSTEM_VIEWS``) in the data area from 2014, every other view in the
    statistics records folder (a system file's twin in the data area, by the folder map)."""
    if name == STATBOOK:
        return paths.record(STATBOOK)
    if clean(paths.year) and name in SYSTEM_VIEWS:
        return paths.data_for(paths.stats) / name
    return paths.file_in(paths.stats, name)


def change_weeks(receipts):
    """The first week whose game records carry each later counting method, by name: "fumbles"
    (a fumble may be kept, the forcer and recoverer are credited apart, muffs count), "penalties"
    (each accepted foul charged to the club that committed it) and "scoring" (two-point tries,
    onside kicks and return touchdowns). A method no game carries is absent."""
    found = {}
    for receipt in receipts:
        week = int(receipt["week"])
        team = next(iter(receipt.get("team_stats", {}).values()), {})
        for name, present in (("fumbles", receipt.get("ball_security") is not None),
                              ("penalties", isinstance(receipt.get("penalties"), dict)),
                              ("scoring", "two_point_attempts" in team)):
            if present:
                found[name] = min(found.get(name, week), week)
    return found


def since(weeks, name):
    """'from Week N on', or 'since the change' when no game carries the method."""
    return ("from Week %d on" % weeks[name]) if name in (weeks or {}) else "since the change"


def load_receipts(directory):
    receipts = []
    for path in sorted(directory.glob("*.json")):
        with path.open(encoding="utf-8") as handle:
            receipts.append(json.load(handle))
    return receipts


def through_line(book):
    if not book.get("receipt_count"):
        return "**Through:** no regular-season game has closed."
    return "**Through:** Week %d." % book["through_week"]


def coverage_line(book, team_id=None, clean_page=False):
    if clean_page:
        return clean_coverage_line(book, team_id)
    if not book.get("receipt_count"):
        return "**Coverage:** no closed-game receipts yet; every table is empty."
    if not book["coverage_complete"]:
        return (
            "**Coverage:** PARTIAL. One or more games lack a complete stat receipt. "
            "Tables show only preserved statistics and are not complete league rankings."
        )
    if team_id is not None:
        if not book.get("team_player_attribution_complete", {}).get(team_id, True):
            return (
                "**Coverage:** team totals complete; player attribution PARTIAL for this "
                "club because a branch-roster correction left exact attribution unknowable."
            )
        return "**Coverage:** complete for this club's closed games."
    if not book.get("player_attribution_complete", True):
        return (
            "**Coverage:** team totals complete; player attribution PARTIAL for one or "
            "more clubs. Known player lines are shown; formal league rankings are withheld."
        )
    return "**Coverage:** complete for every closed game."


def clean_coverage_line(book, team_id=None):
    """The coverage line in football words (the same cases as ``coverage_line``)."""
    if not book.get("receipt_count"):
        return "**Coverage:** no game has closed; every table is empty."
    if not book["coverage_complete"]:
        return ("**Coverage:** PARTIAL. One or more games lack a complete statistics record. Tables show "
                "only the statistics kept and are not complete league rankings.")
    if team_id is not None:
        if not book.get("team_player_attribution_complete", {}).get(team_id, True):
            return ("**Coverage:** team totals complete; player credit PARTIAL for this club because a "
                    "roster correction left the exact credit unknowable.")
        return "**Coverage:** complete for this club's closed games."
    if not book.get("player_attribution_complete", True):
        return ("**Coverage:** team totals complete; player credit PARTIAL for one or more clubs. Known "
                "player lines are shown; league rankings are withheld.")
    return "**Coverage:** complete for every closed game."


def header(title, version, book, team_id=None, intro=None, clean_page=False):
    if clean_page:
        lines = ["# " + title, "", through_line(book), coverage_line(book, team_id, True), ""]
        return lines + ([intro, ""] if intro else [])
    lines = ["# " + title, "", "**Version:** `%s`" % version, through_line(book),
             coverage_line(book, team_id), ""]
    if intro:
        lines += [intro, ""]
    return lines


# Kernel 2014.6 batch B10 review fix (October 16, 2026): the player tables'
# fumble columns combine two definitions in a season that mixes earlier
# receipts with kernel 2014.6 ones; the pages that show them say so (a
# single-definition season's pages are unchanged).
FUMBLE_SPLIT_NOTE = ("FUM, LOST, FF and FR combine two definitions this season: games closed before kernel 2014.6 "
                     "counted every generated fumble as lost and named one defender as its forcer and recoverer; "
                     "from kernel 2014.6 a fumble may be kept, the forcer and recoverer are separate group draws or "
                     "replayed records, and muffs are counted. No fumble rank is published, and who fumbled, forced, "
                     "recovered or muffed is never evidence of a player's ball security.")


def fumble_definitions_mixed(book):
    """True when the season's team-games mix kernel 2014.6 receipts with
    earlier ones (the fumble columns then combine two definitions)."""
    teams = book.get("teams", {}).values()
    total = sum(d.get("games", 0) for d in teams)
    newer = sum(d.get("kernel_2014_6_games", 0) for d in teams)
    return 0 < newer < total


def clean_fumble_note(weeks):
    """FUMBLE_SPLIT_NOTE in football words, with the week the counting changed."""
    first = (weeks or {}).get("fumbles")
    before = ("through Week %d" % (first - 1)) if first else "before the change"
    after = ("from Week %d" % first) if first else "since the change"
    return ("FUM, LOST, FF and FR combine two counting methods this season: %s every fumble counted as "
            "lost, with one defender credited with forcing and recovering it; %s a fumble may be kept, "
            "the players who force and recover it are credited separately and muffs are counted. No "
            "fumble ranking is kept." % (before, after))


def with_fumble_note(intro, book, weeks=None, clean_page=False):
    if not fumble_definitions_mixed(book):
        return intro
    return intro + " " + (clean_fumble_note(weeks) if clean_page else FUMBLE_SPLIT_NOTE)


def no_games(book):
    return [] if book.get("receipt_count") else ["No regular-season game has closed.", ""]


# ---- player views ------------------------------------------------------------

def team_markdown(year, team_id, book, weeks=None):
    lines = header(
        "%s %s player statistics" % (year, team_id),
        "%s-W%02d-TEAM-PLAYER-STATS" % (year, book["through_week"]), book, team_id,
        with_fumble_note("By position, then player. G counts games on the game-day active list.", book,
                         weeks, clean(year)), clean(year),
    ) + no_games(book)
    team = book["teams"].get(team_id)
    if team:
        lines += position_sections(team["players"], with_team=False, clean=clean(year))
    return "\n".join(lines)


def league_markdown(year, book, weeks=None):
    lines = header(
        "%s NFL player statistics by position" % year,
        "%s-W%02d-LEAGUE-PLAYER-STATS" % (year, book["through_week"]), book, None,
        with_fumble_note("Every club's players, one league-wide table per position, each sorted by "
                         "that position's primary production. G counts games on the game-day active list.", book,
                         weeks, clean(year)), clean(year),
    ) + no_games(book)
    return "\n".join(lines + position_sections(book.get("players", {}), with_team=True, clean=clean(year)))


def all_players_markdown(year, book, weeks=None):
    lines = header(
        "%s NFL rosters and player statistics" % year,
        "%s-W%02d-ALL-PLAYER-STATS" % (year, book["through_week"]), book, None,
        with_fumble_note("Club by club, then position, then player: every player who has been on a "
                         "game-day active list, with his position's statistics. G counts games active.", book,
                         weeks, clean(year)), clean(year),
    ) + no_games(book)
    for team_id in sorted(book.get("teams", {})):
        sections = position_sections(book["teams"][team_id].get("players", {}), with_team=False, level="###",
                                     clean=clean(year))
        if sections:
            lines += ["## " + team_id, ""] + sections
    return "\n".join(lines)


# ---- leaders -----------------------------------------------------------------

LEADER_GROUPS = (
    ("Quarterbacks", (("Passing yards", "passing_yards"), ("Passing touchdowns", "passing_touchdowns"),
                      ("Completions", "completions"))),
    ("Running backs", (("Rushing yards", "rushing_yards"), ("Rushing touchdowns", "rushing_touchdowns"),
                       ("Receiving yards", "receiving_yards"))),
    ("Wide receivers", (("Receptions", "receptions"), ("Receiving yards", "receiving_yards"),
                        ("Receiving touchdowns", "receiving_touchdowns"))),
    ("Tight ends", (("Receptions", "receptions"), ("Receiving yards", "receiving_yards"),
                    ("Receiving touchdowns", "receiving_touchdowns"))),
    ("Defensive line", (("Sacks", "sacks"), ("Tackles for loss", "tackles_for_loss"),
                        ("Tackles", "tackles"))),
    ("Linebackers", (("Tackles", "tackles"), ("Sacks", "sacks"),
                     ("Tackles for loss", "tackles_for_loss"))),
    ("Defensive backs", (("Interceptions", "defensive_interceptions"),
                         ("Passes defended", "passes_defended"), ("Tackles", "tackles"))),
    ("Kickers", (("Field goals made", "field_goals_made"), ("Extra points made", "extra_points_made"))),
    ("Punters", (("Punt yards", "punt_yards"), ("Punts inside the 20", "punts_inside_20"))),
)
OVERALL_LEADERS = (
    ("Passing yards", "passing_yards"), ("Rushing yards", "rushing_yards"),
    ("Receiving yards", "receiving_yards"), ("Tackles", "tackles"),
    ("Sacks", "sacks"), ("Interceptions", "defensive_interceptions"),
)


def ranked(rows, value, limit=10):
    """Rank rows (player, line) by value; equal values share a place."""
    rows = sorted(rows, key=lambda item: (-value(item[1]), item[0]))[:limit]
    out, place = [], 0
    for index, (player_id, line) in enumerate(rows, 1):
        if index == 1 or value(line) != value(rows[index - 2][1]):
            place = index
        out.append((place, player_id, line))
    return out


def leader_table(title, rows, fmt, *, with_pos=False, level="###"):
    lines = [level + " " + title, "",
             "| Rank | Player | Team |" + (" Pos |" if with_pos else "") + " Total |",
             "|---:|---|---|" + ("---|" if with_pos else "") + "---:|"]
    for place, player_id, line in rows:
        pos = (" %s |" % line.get("position", "")) if with_pos else ""
        lines.append("| %d | %s | %s |%s %s |" % (
            place, player_id, ", ".join(line.get("teams", ())), pos, fmt(line)))
    lines.append("")
    return lines


def team_games(book, line):
    return max((book["teams"].get(t, {}).get("games", 0) for t in line.get("teams", ())), default=0)


def leaders_markdown(year, book):
    lines = header(
        "%s NFL statistical leaders" % year,
        "%s-W%02d-LEADERS" % (year, book["through_week"]), book, clean_page=clean(year),
    )
    if not book.get("receipt_count"):
        return "\n".join(lines + ["No regular-season game has closed, so no leader exists yet.", ""])
    if not book["coverage_complete"] or not book.get("player_attribution_complete", True):
        if clean(year):
            return "\n".join(lines + [
                "League rankings are withheld while player credit is incomplete. Known lines remain in "
                "the [league player statistics](league_player_stats.md).", ""])
        return "\n".join(lines + [
            "League rankings are withheld while player attribution is incomplete. "
            "Known lines remain in `league_player_stats.md`.", ""])

    players = {p: l for p, l in book.get("players", {}).items() if not str(p).startswith("__")}
    lines += ["By position, then category; each list ranks only players at that position. "
              "Passer-rate leaders and overall leaders follow.", ""]
    for group_title, categories in LEADER_GROUPS:
        positions = next(p for title, p, _, _ in POSITION_GROUPS if title == group_title)
        pool = [(p, l) for p, l in players.items() if l.get("position", "") in positions]
        lines += ["## " + group_title, ""]
        for title, field in categories:
            rows = ranked([(p, l) for p, l in pool if g(l, field)], lambda l, f=field: g(l, f))
            lines += leader_table(title, rows, lambda l, f=field: g(l, f))

    qualified = [(p, l) for p, l in players.items()
                 if g(l, "pass_attempts") and
                 g(l, "pass_attempts") >= PASSING_ATTEMPTS_PER_TEAM_GAME * team_games(book, l)]
    lines += ["## Passer rate leaders", "",
              "Qualified passers: at least %d attempts per team game." % PASSING_ATTEMPTS_PER_TEAM_GAME, ""]
    for title, value, fmt in (
        ("Passer rating", rating_value, lambda l: "%.1f" % rating_value(l)),
        ("Completion percentage", lambda l: g(l, "completions") / g(l, "pass_attempts"),
         lambda l: pct(g(l, "completions"), g(l, "pass_attempts"))),
        ("Yards per attempt", lambda l: g(l, "passing_yards") / g(l, "pass_attempts"),
         lambda l: avg(g(l, "passing_yards"), g(l, "pass_attempts"))),
    ):
        lines += leader_table(title, ranked(qualified, value), fmt)

    lines += ["## All positions", ""]
    for title, field in OVERALL_LEADERS:
        rows = [(r["player_id"], players[r["player_id"]]) for r in leaders(book, field, limit=10)]
        lines += leader_table(title, ranked(rows, lambda l, f=field: g(l, f)), lambda l, f=field: g(l, f),
                              with_pos=True)
    return "\n".join(lines)


# ---- team views --------------------------------------------------------------

def _spot_text(spot):
    """yardline_100 as a field position: 'own 25', 'opp 40' or 'midfield'."""
    if spot is None:
        return "—"
    spot = round(spot)
    if spot == 50:
        return "midfield"
    return "own %d" % (100 - spot) if spot > 50 else "opp %d" % spot


def field_position_rows(receipts):
    """Per-club field position from kernel 2013.7 receipts (drives summary)."""
    from runtime.bands import _drives
    clubs = {}
    for receipt in receipts:
        drives = [d for d in _drives(receipt) if d.get("start_spot") is not None]
        if not drives:
            continue
        teams = list(receipt.get("team_stats", {}))
        for team in teams:
            row = clubs.setdefault(team, {"games": 0, "drives": 0, "start": 0, "opp_drives": 0, "opp_start": 0,
                                          "punts": 0, "punt_net": 0, "tb": 0, "kicks": 0, "fourth": [0, 0]})
            row["games"] += 1
        for d in drives:
            own = clubs[d["team"]]
            own["drives"] += 1
            own["start"] += d["start_spot"]
            for team in teams:
                if team != d["team"]:
                    clubs[team]["opp_drives"] += 1
                    clubs[team]["opp_start"] += d["start_spot"]
            if d["category"] == "punt" and d.get("next_start") is not None:
                own["punts"] += 1
                own["punt_net"] += d["end_spot"] - (100 - d["next_start"])
            if d.get("chains"):
                own["fourth"][0] += d["chains"][4]
                own["fourth"][1] += d["chains"][5]
    return clubs


def penalty_split(receipts):
    """Kernel 2014.6 batch B11: each club's penalty counters split by
    definition. A receipt with the penalty-records marker charges the fouling
    club's accepted replayed records ("records": games, accepted, yards,
    declined, offsetting, first downs by penalty); any other receipt carries
    the earlier counter, one draw per scrimmage play charged to the offense
    ("counter": games, penalties, yards). None when no receipt carries the
    marker (every earlier view is unchanged)."""
    receipts = list(receipts)
    if not any(isinstance(r.get("penalties"), dict) for r in receipts):
        return None
    out = {}
    for receipt in receipts:
        records = isinstance(receipt.get("penalties"), dict)
        for team_id, s in receipt.get("team_stats", {}).items():
            row = out.setdefault(team_id, {"counter": [0, 0, 0], "records": [0, 0, 0, 0, 0, 0]})
            if records:
                values = (1, s.get("penalties", 0), s.get("penalty_yards", 0), s.get("penalties_declined", 0),
                          s.get("penalties_offsetting", 0), s.get("penalty_first_downs", 0))
                row["records"] = [a + b for a, b in zip(row["records"], values)]
            else:
                values = (1, s.get("penalties", 0), s.get("penalty_yards", 0))
                row["counter"] = [a + b for a, b in zip(row["counter"], values)]
    return out


def team_stats_markdown(year, book, receipts=()):
    c = clean(year)
    weeks = change_weeks(receipts)
    lines = header(
        "%s NFL team statistics" % year,
        "%s-W%02d-TEAM-STATS" % (year, book["through_week"]), book, None,
        ("Per-game team statistics from the closed games. Plays are rushing attempts plus dropbacks. "
         "Records and tiebreakers are on the [standings](../standings.md).") if c else
        "Per-game team statistics from closed-game receipts. Plays are rushing "
        "attempts plus dropbacks. Records and tiebreakers live in `../standings.md`.", c,
    ) + no_games(book)
    clubs = [(t, d) for t, d in book.get("teams", {}).items() if d.get("games")]
    if not clubs:
        return "\n".join(lines)

    def per(value, games):
        return "%.1f" % (value / games)

    def third(stats):
        return "%d/%d" % (stats["third_down_conversions"], stats["third_down_attempts"])

    def third_pct(stats):
        return pct(stats["third_down_conversions"], stats["third_down_attempts"])

    split = penalty_split(receipts)
    lines += ["## Offense", ""]
    if split is not None and c:
        first = weeks.get("penalties")
        lines += ["PEN/G and PEN YDS/G count only the games %s, when each game's penalties were charged to "
                  "the offense, per such game; the games %s, with each accepted foul charged to the club that "
                  "committed it, are in the penalty table below. The two counts are never added and no penalty "
                  "ranking is kept." % (("through Week %d" % (first - 1)) if first else "before the change",
                                        ("from Week %d on" % first) if first else "since the change"), ""]
    elif split is not None:
        # Kernel 2014.6 batch B11: the season's penalty counters have two
        # definitions; PEN/G and PEN YDS/G here are the earlier counter's
        # games only, and the records' games have their own table below.
        lines += ["PEN/G and PEN YDS/G count only games closed before the penalty records (one draw per "
                  "scrimmage play, charged to the offense), per such game; games with the penalty records "
                  "are in the penalty table below. No combined penalty figure or rank is published.", ""]
    lines += ["| Team | G | PTS/G | YDS/G | PLAYS/G | Y/P | PASS/G | RUSH/G | %s | 3RD | 3RD%% | GIVE | SCK | PEN/G | PEN YDS/G | TOP/G |" % ("FD/G" if c else "1D/G"),
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    offense = []
    for team_id, data in clubs:
        n, t = data["games"], data["team_stats"]
        yards = t["passing_yards"] + t["rushing_yards"]
        if split is None:
            pen, pen_yards = per(t["penalties"], n), per(t["penalty_yards"], n)
        else:
            games, count, total = split.get(team_id, {"counter": [0, 0, 0]})["counter"]
            pen, pen_yards = (per(count, games), per(total, games)) if games else ("—", "—")
        offense.append((-yards / n, team_id, (
            team_id, n, per(t["points"], n), per(yards, n), per(data["plays"], n),
            avg(yards, data["plays"]), per(t["passing_yards"], n), per(t["rushing_yards"], n),
            per(t["first_downs"], n), third(t), third_pct(t), t["turnovers"], t["sacks_allowed"],
            pen, pen_yards, time_text(t["time_of_possession"] / n))))
    for _, _, row in sorted(offense):
        lines.append("| " + " | ".join(str(v) for v in row) + " |")

    lines += ["", "## Defense", "",
              "Opponent production per game. SCK counts sacks by the defense; TAKE counts takeaways.", "",
              "| Team | G | PTS/G | YDS/G | PLAYS/G | Y/P | PASS/G | RUSH/G | %s | 3RD | 3RD%% | TAKE | SCK | TO +/- |" % ("FD/G" if c else "1D/G"),
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    defense = []
    for team_id, data in clubs:
        n, o, t = data["games"], data["opponent_stats"], data["team_stats"]
        yards = o["passing_yards"] + o["rushing_yards"]
        margin = o["turnovers"] - t["turnovers"]
        defense.append((yards / n, team_id, (
            team_id, n, per(o["points"], n), per(yards, n), per(data["opponent_plays"], n),
            avg(yards, data["opponent_plays"]), per(o["passing_yards"], n), per(o["rushing_yards"], n),
            per(o["first_downs"], n), third(o), third_pct(o), o["turnovers"], o["sacks_allowed"],
            "%+d" % margin if margin else "0")))
    for _, _, row in sorted(defense):
        lines.append("| " + " | ".join(str(v) for v in row) + " |")

    lines += ["", "## Special teams", "",
              "| Team | G | FGM | FGA | FG% | XPM | XPA | PUNTS | PUNT AVG | IN20 | KR | KR AVG | PR | PR AVG |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for team_id, data in sorted(clubs):
        s = combine(data.get("players", {}).values())
        lines.append("| " + " | ".join(str(v) for v in (
            team_id, data["games"], g(s, "field_goals_made"), g(s, "field_goals_attempted"),
            pct(g(s, "field_goals_made"), g(s, "field_goals_attempted")),
            g(s, "extra_points_made"), g(s, "extra_points_attempted"), g(s, "punts"),
            avg(g(s, "punt_yards"), g(s, "punts")), g(s, "punts_inside_20"),
            g(s, "kick_returns"), avg(g(s, "kick_return_yards"), g(s, "kick_returns")),
            g(s, "punt_returns"), avg(g(s, "punt_return_yards"), g(s, "punt_returns")))) + " |")
    lines.append("")

    drive_clubs = [(t, d) for t, d in clubs if d.get("drive_model_games")]
    if drive_clubs and c:
        lines += ["## Drives and kicking", "",
                  "Counted from the games that record drives; G counts those games. SAF counts safeties, "
                  "DOWNS turnovers on downs, CLOCK drives ended by the clock and KO kickoffs.", "",
                  "| Team | G | DRIVES | FGA | XPA | XPM | SAF | DOWNS | CLOCK | KO |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    elif drive_clubs:
        lines += ["## Drives and kicking — Week 4 onward (kernels 2013.6-2013.7)", "",
                  "Counted only from games closed under kernel 2013.6 or later; Weeks 1-3 receipts "
                  "(kernels 2013.4/2013.5) do not carry these counters and are not included. "
                  "G counts those games only. From kernel 2013.7 (after Week 8) a punt return is a "
                  "punt whose 2012 play-by-play record was returned (not a fair catch, "
                  "downed, out-of-bounds or touchback punt).", "",
                  "| Team | G | DRIVES | FGA | XPA | XPM | SAF | DOWNS | CLOCK | KO |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    if drive_clubs:
        for team_id, data in sorted(drive_clubs):
            t = data["team_stats"]
            lines.append("| " + " | ".join(str(v) for v in (
                team_id, data["drive_model_games"], t.get("drives", 0), t.get("field_goal_attempts", 0),
                t.get("extra_point_attempts", 0), t.get("extra_points_made", 0), t.get("safeties", 0),
                t.get("turnovers_on_downs", 0), t.get("clock_expired_drives", 0),
                t.get("kickoffs", 0))) + " |")
        lines.append("")

    scoring_clubs = [(t, d) for t, d in clubs if d.get("kernel_2014_6_games")
                     and "two_point_attempts" in d["team_stats"]]
    if scoring_clubs and c:
        lines += ["## Two-point tries, onside kicks and return touchdowns", "",
                  "Counted %s; G counts those games. DEF TD: interception and fumble return touchdowns; "
                  "ST TD: punt return, blocked-kick and kickoff return touchdowns; ONS REC: the kicking "
                  "club's recoveries of its own onside kicks." % since(weeks, "scoring"), "",
                  "| Team | G | 2PA | 2PM | DEF TD | ST TD | ONSIDE | ONS REC |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|"]
    elif scoring_clubs:
        # Kernel 2014.6 batch B9 (R8, R9, R15): counted only from kernel
        # 2014.6 games; earlier receipts carry none of these counters.
        lines += ["## Two-point tries, onside kicks and return touchdowns — kernel 2014.6 games", "",
                  "Counted only from games closed under kernel 2014.6 or later; G counts those games "
                  "only. DEF TD: interception and fumble return touchdowns; ST TD: punt return, "
                  "blocked-kick and kickoff return touchdowns; ONS REC: the kicking club's recoveries "
                  "of its own onside kicks.", "",
                  "| Team | G | 2PA | 2PM | DEF TD | ST TD | ONSIDE | ONS REC |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|"]
    if scoring_clubs:
        for team_id, data in sorted(scoring_clubs):
            t = data["team_stats"]
            lines.append("| " + " | ".join(str(v) for v in (
                team_id, data["kernel_2014_6_games"], t.get("two_point_attempts", 0),
                t.get("two_point_conversions", 0), t.get("defensive_touchdowns", 0),
                t.get("special_teams_touchdowns", 0), t.get("onside_kicks", 0),
                t.get("onside_recoveries", 0))) + " |")
        lines.append("")

    ball_clubs = [(t, d) for t, d in clubs if d.get("kernel_2014_6_games") and "muffs" in d["team_stats"]]
    if ball_clubs and c:
        lines += ["## Ball security", "",
                  "Counted %s; G counts those games. FUM: the club's fumbles, its muffs counted as fumbles "
                  "included (a kickoff muff the club never possessed is a muff only); LOST: those the club lost; "
                  "MUFFS: its muffed kicks; KICK REC: its recoveries of its own kicks. Earlier games counted every "
                  "fumble as lost, with one defender credited with forcing and recovering it, so the player "
                  "tables' FUM, LOST, FF and FR columns combine two counting methods this season and no fumble "
                  "ranking is kept." % since(weeks, "fumbles"), "",
                  "| Team | G | FUM | LOST | MUFFS | KICK REC |",
                  "|---|---:|---:|---:|---:|---:|"]
    elif ball_clubs:
        # Kernel 2014.6 batch B10 (W4, R12): counted only from kernel 2014.6
        # games; the fumble definition changed with them (split by definition,
        # never combined with the earlier receipts' counters).
        lines += ["## Ball security — kernel 2014.6 games", "",
                  "Counted only from games closed under kernel 2014.6 or later; G counts those games only. "
                  "FUM: the club's fumbles, its muffs the feed counts as fumbles included (a kickoff muff the "
                  "club never possessed is a muff only); LOST: those the club lost; MUFFS: its muffed kicks; "
                  "KICK REC: its recoveries of its own kicks. Earlier receipts counted every generated fumble as "
                  "lost and named one defender as its forcer and recoverer, so the player tables' FUM, LOST, FF "
                  "and FR columns combine two definitions this season and no fumble rank is published. Who "
                  "fumbled, forced, recovered or muffed is a group draw or a replayed record, never evidence of "
                  "a player's ball security.", "",
                  "| Team | G | FUM | LOST | MUFFS | KICK REC |",
                  "|---|---:|---:|---:|---:|---:|"]
    if ball_clubs:
        for team_id, data in sorted(ball_clubs):
            t = data["team_stats"]
            lines.append("| " + " | ".join(str(v) for v in (
                team_id, data["kernel_2014_6_games"], t.get("fumbles", 0), t.get("fumbles_lost", 0),
                t.get("muffs", 0), t.get("kicking_team_recoveries", 0))) + " |")
        lines.append("")

    if split is not None:
        # Kernel 2014.6 batch B11 (R11): counted only from games with the
        # penalty records; split by definition, never combined.
        rows = [(team_id, row["records"]) for team_id, row in sorted(split.items()) if row["records"][0]]
    if split is not None and c:
        lines += ["## Penalties", "",
                  "Counted %s; G counts those games. Each accepted foul is charged to the club that committed it "
                  "(PEN, PEN YDS); DECL and OFFS count its declined and offsetting fouls; FD PEN counts the club's "
                  "own first downs by penalty. Earlier games charged each game's penalties to the offense, so the "
                  "two counts are never added and no penalty ranking is kept." % since(weeks, "penalties"), "",
                  "| Team | G | PEN | PEN YDS | PEN/G | PEN YDS/G | DECL | OFFS | FD PEN |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    elif split is not None:
        lines += ["## Penalties — kernel 2014.6 games with penalty records", "",
                  "Counted only from games closed with the penalty records; G counts those games only. Each "
                  "accepted foul is charged to the fouling club (PEN, PEN YDS); DECL and OFFS count its declined "
                  "and offsetting fouls; 1D PEN counts the club's own first downs by penalty. The fouls are "
                  "the replayed real drives' own records; who fouled is a group draw, never evidence, and an "
                  "accept or decline is the real record's, never a coaching choice. Earlier games charged a "
                  "drawn count to the offense, so the two definitions are never added and no penalty rank is "
                  "published.", "",
                  "| Team | G | PEN | PEN YDS | PEN/G | PEN YDS/G | DECL | OFFS | 1D PEN |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    if split is not None:
        for team_id, (games, count, total, declined, offsetting, first_downs) in rows:
            lines.append("| " + " | ".join(str(v) for v in (
                team_id, games, count, total, per(count, games), per(total, games), declined, offsetting,
                first_downs)) + " |")
        lines.append("")

    spots = field_position_rows(receipts)
    if spots and c:
        lines += ["## Field position", "",
                  "Average drive start for the club and for its opponents, net punting (line of scrimmage to "
                  "the receiving club's start, returns and penalties included) and fourth-down attempts and "
                  "conversions inside drives (a failed attempt ending a drive is a turnover on downs). G counts "
                  "the games that record drive starts.", "",
                  "| Team | G | DRIVES | AVG START | OPP AVG START | PUNTS | NET PUNT | 4TH ATT | 4TH CONV |",
                  "|---|---:|---:|---|---|---:|---:|---:|---:|"]
    elif spots:
        lines += ["## Field position — kernel 2013.7 games (after Week 8)", "",
                  "Kernel 2013.7 games only: average drive start for the club and for its "
                  "opponents, realized punt net (line of scrimmage to the receiving start, "
                  "returns and enforcement included) and fourth-down attempts and conversions "
                  "inside drives (from the real 2012 drive chains; a failed attempt ending a "
                  "drive is a turnover on downs). G counts those games only.", "",
                  "| Team | G | DRIVES | AVG START | OPP AVG START | PUNTS | NET PUNT | 4TH ATT | 4TH CONV |",
                  "|---|---:|---:|---|---|---:|---:|---:|---:|"]
    if spots:
        for team_id, row in sorted(spots.items()):
            lines.append("| " + " | ".join(str(v) for v in (
                team_id, row["games"], row["drives"],
                _spot_text(row["start"] / row["drives"]) if row["drives"] else "—",
                _spot_text(row["opp_start"] / row["opp_drives"]) if row["opp_drives"] else "—",
                row["punts"], avg(row["punt_net"], row["punts"]), row["fourth"][0], row["fourth"][1])) + " |")
        lines.append("")
    return "\n".join(lines)


# The defensive sheet's situations in football words (runtime/defensive_calls.MENUS).
SITUATION_WORDS = {
    "normal-down": "normal downs", "second-and-long": "second and long", "third-and-short": "third and short",
    "third-and-medium": "third and medium", "third-and-long": "third and long", "two-point": "two-point try",
    "goal-line": "goal line", "low-red-zone": "low red zone", "high-red-zone": "high red zone",
    "red-zone": "red zone", "backed-up": "backed up", "two-minute": "two-minute",
    "four-minute": "four-minute", "lead-late": "leading late",
}


def clean_play_calls_markdown(year, team_id, book):
    """The play-call page in football words: each call's snaps and results, then the defensive
    calls by situation. The same rows, orders and figures as ``play_calls_markdown``."""
    lines = header(
        "%s %s play calls" % (year, team_id), None, book, team_id,
        "Every snap in the play-by-play carries a call from that week's call sheet that fits its ball "
        "carrier or target; this table counts the snaps under each call and what they gained. The sheet "
        "sets the calls available in each situation, so a call's totals reflect the situations it was used "
        "in. Generic, kneel, spike and scramble rows are separate; a quarterback scramble counts under the "
        "pass call it carries. Y/P is yards per snap; 20+ counts gains of 20 yards or more; NEG counts snaps "
        "that lost yardage.", True,
    ) + no_games(book)
    calls = book.get("play_calls", {}).get(team_id, {})
    if not calls:
        return "\n".join(lines)
    lines += call_rows(calls)
    games = (book.get("defensive_calls") or {}).get(team_id)
    if games:
        lines += ["## Defensive calls by situation", "",
                  "Each defensive snap is listed under the row of Stone's defensive call sheet for its down and "
                  "distance, field zone or clock, with that row's call as the sheet writes it. A situation's snaps "
                  "are a count of the snaps in that situation. Snaps no row names, kneels and spikes are listed as "
                  "other snaps.", "",
                  "| Week | Situation | Call | SNAPS |", "|---:|---|---|---:|"]
        for game in games:
            for row in game["rows"].values():
                lines.append("| %d | %s | %s | %d |" % (
                    game["week"], SITUATION_WORDS.get(row["menu"], str(row["menu"]).replace("-", " ")),
                    sheet_call(row["text"]), row["snaps"]))
            lines.append("| %d | other snaps | | %d |" % (game["week"], game["unlabelled_snaps"]))
        lines.append("")
    return "\n".join(lines)


def sheet_call(text):
    """A defensive sheet row's call without its numbered heading ("09. SECOND-AND-LONG: "), which
    the situation column already names; the call itself is the sheet's words."""
    text = str(text).replace("|", "/")
    head = re.match(r"^\s*\d+\.\s+[^:]*:\s*", text)
    return text[head.end():] if head and head.end() < len(text) else text


def call_rows(calls):
    lines = ["| Call | Family | SNAPS | RUNS | DB | CMP | ATT | CMP% | YDS | Y/P | 20+ | NEG | TD | TO | SCK |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for name, line in sorted(calls.items(), key=lambda item: (-g(item[1], "snaps"), item[0])):
        lines.append("| " + " | ".join(str(v) for v in (
            name, line.get("family", name), g(line, "snaps"), g(line, "runs"), g(line, "dropbacks"),
            g(line, "completions"), g(line, "pass_attempts"),
            pct(g(line, "completions"), g(line, "pass_attempts")), g(line, "yards"),
            avg(g(line, "yards"), g(line, "snaps")), g(line, "explosive_plays"),
            g(line, "negative_plays"), g(line, "touchdowns"), g(line, "turnovers"),
            g(line, "sacks"))) + " |")
    return lines + [""]


def play_calls_markdown(year, team_id, book):
    if clean(year):
        return clean_play_calls_markdown(year, team_id, book)
    lines = header(
        "%s %s descriptive call labels" % (year, team_id),
        "%s-W%02d-PLAY-CALL-STATS" % (year, book["through_week"]), book, team_id,
        "Descriptive labels on the generated snaps, from the snap ledger. From kernel "
        "2013.7 (after Week 8) each label fits that snap's ball carrier or target: it is drawn "
        "after the carrier or target is fixed, from the weekly sheet's calls whose "
        "declared (or 2013 family-map) groups include him. A label is not Stone's call "
        "selection or frequency, and per-label yardage is not evidence of a concept's "
        "effectiveness. Generic, kneel, spike and scramble labels are separate rows; a "
        "quarterback scramble is counted under the pass label it carries. Kernels "
        "2013.4-2013.6 drew each snap's label at random from the sheet's calls of that "
        "run or pass type, independent of the ball carrier (see the "
        "[October 6, 2013 St. Louis game report]"
        "(" + page_link(2013, "regular_season/week_05_jacksonville_at_st_louis/output.md", 2) + ")), so Weeks "
        "1-8 rows show label assignment only. Y/P is yards per snap; 20+ counts gains "
        "of 20 yards or more; NEG counts snaps that lost yardage.",
    ) + no_games(book)
    calls = book.get("play_calls", {}).get(team_id, {})
    if not calls:
        return "\n".join(lines)
    lines += ["| Call | Family | SNAPS | RUNS | DB | CMP | ATT | CMP% | YDS | Y/P | 20+ | NEG | TD | TO | SCK |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for name, line in sorted(calls.items(), key=lambda item: (-g(item[1], "snaps"), item[0])):
        lines.append("| " + " | ".join(str(v) for v in (
            name, line.get("family", name), g(line, "snaps"), g(line, "runs"), g(line, "dropbacks"),
            g(line, "completions"), g(line, "pass_attempts"),
            pct(g(line, "completions"), g(line, "pass_attempts")), g(line, "yards"),
            avg(g(line, "yards"), g(line, "snaps")), g(line, "explosive_plays"),
            g(line, "negative_plays"), g(line, "touchdowns"), g(line, "turnovers"),
            g(line, "sacks"))) + " |")
    lines.append("")
    lines += defensive_calls_markdown(book, team_id)
    return "\n".join(lines)


def defensive_calls_markdown(book, team_id):
    """Kernel 2014.6 W1a: the club's defensive call record, game by game:
    snaps by the frozen sheet's row (no outcome column). Empty without one,
    so earlier views are unchanged."""
    games = (book.get("defensive_calls") or {}).get(team_id)
    if not games:
        return []
    lines = ["## Defensive call record", "",
             "Each defensive snap carries the row of Stone's frozen structured defensive sheet that its down "
             "and distance, field zone or clock names (the sheet's applicable row, chosen by rule with no random "
             "number, after the play was resolved). A row is the sheet's words, not the call on every such snap, "
             "and the counts are a mix of situations, not Stone's call frequency or evidence that a call worked; "
             "no row changes a result. Snaps no row names, kneels and spikes count as unlabelled.", "",
             "| Week | Row | Situation | Sheet text | SNAPS |", "|---:|---|---|---|---:|"]
    for game in games:
        for rid, row in game["rows"].items():
            lines.append("| %d | %s | %s | %s | %d |" % (game["week"], rid, row["menu"],
                                                       str(row["text"]).replace("|", "/"), row["snaps"]))
        lines.append("| %d | (unlabelled) | | | %d |" % (game["week"], game["unlabelled_snaps"]))
    lines.append("")
    return lines


POINTS_NOTE = (
    "Points: non-offensive touchdowns, their tries and two-point tries are not "
    "modelled by design (about 1.7-2.0 points per team game below the 2012 centre); "
    "the ±5.0 tolerance is deliberately not tightened. Yards per team game are net "
    "of sack yards, as the 2012 centre is (see the correction in the "
    "[December 1, 2013 Cleveland game report]"
    "(" + page_link(2013, "regular_season/week_13_jacksonville_at_cleveland/output.md", 2) + "); earlier audits "
    "compared gross passing yards and read about 14 yards high)."
)
# Kernel 2014.6 batch B9: the "not modelled" sentence above holds for the
# cohorts up to kernel 2014.5 only; from 2014.6 the scoring decisions are
# modelled and graded in their own table.
POINTS_NOTE_2014_6 = (
    "Points: from kernel 2014.6 the two-point tries, onside kicks and the "
    "non-offensive (interception, fumble, punt, blocked-kick and kickoff return) "
    "touchdowns with their tries are modelled from the 2010-2014 scoring artifact "
    "(the scoring-decision rows below); points per team-game are measured, never "
    "forecast. Yards per team game are net of sack yards."
)


def _band_table(rows, cohort=None, centre_label="2012 band centre"):
    """A band table; a cohort's known detections (runtime.bands) are labelled."""
    fmt = lambda v: "—" if v is None else ("%.3f" % v if abs(v) < 2 else "%.1f" % v)
    lines = ["| Metric | Observed | %s | Tolerance | Status |" % centre_label,
             "|---|---:|---:|---:|---|"]
    for row in rows:
        metric, observed, band, tolerance, _ = row
        spread = "—" if tolerance is None else "±" + fmt(tolerance)
        lines.append("| %s | %s | %s | %s | %s |" % (metric, fmt(observed), fmt(band), spread,
                                                     known_status(row, cohort)))
    return lines


def _known_detection_lines(cohort):
    known = known_detections(cohort)
    if not known:
        return []
    lines = ["Known detections (`runtime/bands.py` `KNOWN_DETECTIONS`): graded rows with a "
             "documented design cause, accepted rather than tuned. Each stays graded; OUTSIDE "
             "within %dx its tolerance is the documented detection, and beyond that it is "
             "investigated. No centre, tolerance, coefficient or pool was changed." % KNOWN_DETECTION_BOUND, ""]
    if provisional_detections(cohort):
        lines[0] += (" A row marked PROVISIONAL is a carried diagnosis from the kernel 2014.6 build, not an "
                     "accepted detection: it is not bounded, and batch B17 re-grades it with the provisional "
                     "status removed; a row still OUTSIDE then goes to the user (U8).")
    lines += ["- %s: %s." % (metric, note) for metric, note in known.items()]
    return lines + [""]


def _week_span(receipts, empty):
    weeks = sorted({int(r["week"]) for r in receipts if str(r.get("week", "")).isdigit()})
    if not weeks:
        return empty
    return "Week %d" % weeks[0] if weeks[0] == weeks[-1] else "Weeks %d-%d" % (weeks[0], weeks[-1])


def _coherence_lines(checked, counts):
    lines = ["| Class | Count | Status |", "|---|---:|---|"]
    for cls, count, measurable in counts:
        if not checked or not measurable:
            lines.append("| %s | — | not measurable |" % cls.replace("_", " "))
        else:
            lines.append("| %s | %d | %s |" % (cls.replace("_", " "), count, "OUTSIDE" if count else "WITHIN"))
    return lines


def _base_cohort_lines(version, members, empty):
    """A cohort graded on a later base (kernel 2014.6 onward, batch B5): the
    same tables with that base's centres named, plus its injury rows."""
    base = cohort_base(members, version)
    label = "%s base centre" % base.name
    team_games, rows = audit(members, cohort=version)
    drive_games, drive_rows = audit_drive_model(members, cohort=version)
    fp_games, fp_rows = audit_field_position(members, cohort=version)
    injury_games, injury_rows = audit_injuries(members, cohort=version)
    scoring_games, scoring_rows = audit_scoring(members, cohort=version)
    fourth_games, fourth_rows = audit_fourth_down(members, cohort=version)
    ball_games, ball_rows = audit_ball_security(members, cohort=version)
    penalty_games, penalty_rows = audit_penalties(members, cohort=version)
    yardage_games, yardage_rows = audit_yardage(members, cohort=version)
    checked, counts = coherence(members, cohort=version)
    sources = ", ".join("`%s`" % pin.path for role, pin in base.files if role != "specification")
    scoring = [
        "### Scoring-decision rows", "",
        "Two-point tries, onside kicks and non-offensive touchdowns (kernel 2014.6 batch B9). "
        "Centres from the base's scoring artifact; rates use 3*sqrt(p(1-p)/n) and counts "
        "3*sqrt(c/n), and a rate row reads INSUFFICIENT SAMPLE below 30 events. INFORMATIONAL "
        "rows are not graded and MEASURED rows have no centre.", "",
    ] + _band_table(scoring_rows, centre_label=label) + [""] if scoring_rows else []
    fourth = [
        "### Fourth-down rows", "",
        "Fourth-down decisions and conversions (kernel 2014.6 batch B9F). Centres from the base's "
        "fourth-down artifact; the go share and attempts rows grade only the league chart's decisions, "
        "and the club decisions of a standing rule or a live call are counted apart. Rates use "
        "3*sqrt(p(1-p)/n) and counts 3*sqrt(c/n); a rate row reads INSUFFICIENT SAMPLE below 30 events.", "",
    ] + _band_table(fourth_rows, centre_label=label) + [""] if fourth_rows else []
    ball = [
        "### Ball-security rows", "",
        "Fumbles, muffs and kicking-team recoveries (kernel 2014.6 batch B10). Centres from the base's "
        "ball-security artifact (the fumbles row in the nflverse definition, less the defense's own "
        "fumbles after a turnover); fumbles per team-game use 3*sqrt(phi*c/n) with the artifact's "
        "team-game dispersion, other counts 3*sqrt(c/n) and rates 3*sqrt(p(1-p)/n); a rate row reads "
        "INSUFFICIENT SAMPLE below 30 events. Who fumbled, forced, recovered or muffed is a group draw "
        "or a replayed record, never evidence of a player's ball security.", "",
    ] + _band_table(ball_rows, centre_label=label) + [""] if ball_rows else []
    penalty = [
        "### Penalty rows", "",
        "Replayed penalty records (kernel 2014.6 batch B11). Centres from the base's penalty artifact, in the "
        "engine's scope (the replayed drives' records and the kick plays' records; records enforced after a "
        "possession or on a field-goal row are not replayed). Accepted penalties use 3*sqrt(phi*c/n) with the "
        "artifact's team-game dispersion, penalty yards 3*SD/sqrt(n) and first downs by penalty 3*sqrt(c/n). "
        "Each accepted foul is charged to the fouling club; who fouled is a group draw, never evidence, and an "
        "accept or decline is the real record's. The net-yards row is reported, never tuned.", "",
    ] + _band_table(penalty_rows, centre_label=label) + [""] if penalty_rows else []
    yardage = [
        "### Yardage rows", "",
        "The replayed yard split (kernel 2014.6 batch B13): each replayed drive keeps its own real rushing and "
        "passing yards, completions and sack losses, and its own run and completion values. Centres from the "
        "base's yardage artifact; yards per carry uses 3*SD/(carries*sqrt(n)) with the artifact's team-game "
        "residual SD, the completion rate and run share 3*sqrt(phi*p(1-p)/N) with its team-game dispersion, and "
        "rushing yards 3*SD/sqrt(n). The run-shape rows are graded only on the synthetic all-club acceptance "
        "samples; on a real cohort they are INFORMATIONAL.", "",
    ] + _band_table(yardage_rows, centre_label=label) + [""] if yardage_rows else []
    return [
        "## Kernel %s cohort (%s)" % (version, _week_span(members, empty)), "",
        "**Calibration base:** %s (%s). **Team-games audited:** %d. Carry shares exclude "
        "kneels." % (base.name, sources, team_games), "",
    ] + _band_table(rows, centre_label=label) + ["", POINTS_NOTE_2014_6 if scoring_rows else POINTS_NOTE, "",
        "### Drive model rows", "",
        "Centres from the base's band centres (equal weight per event); tolerance is three "
        "standard errors at the observed sample.", "",
    ] + _band_table(drive_rows, version, label) + [""] + _known_detection_lines(version) + [
        "### Field-position and late-game rows", "",
        "Centres from the base's band centres and its drawn transition pools. Rates use "
        "3*sqrt(p(1-p)/n), counts 3*sqrt(c/n) and means 3*sd/sqrt(n); a row reads "
        "INSUFFICIENT SAMPLE below 30 events. INFORMATIONAL rows are shapes, not grades; the "
        "zero-tolerance rows read OUTSIDE on any event.", "",
    ] + _band_table(fp_rows, centre_label=label) + [
        "",
        "### Injury rows", "",
        "The injury calibration's acceptance bands (kernel 2014.4 method): WITHIN when the "
        "observed value lies inside the band; the centre column is the band midpoint and the "
        "tolerance its half-width.", "",
    ] + _band_table(injury_rows, centre_label="band midpoint") + [""] + scoring + fourth + ball + penalty + yardage + [
        "### Ledger coherence", "",
        "Zero-tolerance counts from `runtime.play_detail.check_ledger`, checked with this "
        "base's rules. Games checked: %d." % checked, "",
    ] + _coherence_lines(checked, counts) + [""]


def _current_cohort_lines(version, members, empty):
    """One field-position-era cohort (kernel 2013.7, 2013.8, ...) of the audit,
    graded against that kernel version's own calibration base."""
    if not cohort_base(members, version).legacy_2012():
        return _base_cohort_lines(version, members, empty)
    team_games, rows = audit(members, cohort=version)
    drive_games, drive_rows = audit_drive_model(members, cohort=version)
    fp_games, fp_rows = audit_field_position(members, cohort=version)
    checked, counts = coherence(members, cohort=version)
    lines = [
        "## Kernel %s cohort (%s)" % (version, _week_span(members, empty)), "",
        "**Team-games audited:** %d. Carry shares exclude kneels, as in the 2012 "
        "baseline." % team_games, "",
    ] + _band_table(rows) + ["", POINTS_NOTE, "",
        "### Drive model rows", "",
        "Centres from the 2012 drive model (nflverse drive definition) and period totals; "
        "tolerance is three standard errors at the observed sample.", "",
    ] + _band_table(drive_rows, version) + [""] + _known_detection_lines(version) + [
        "### Field-position rows", "",
        "Centres from the 2012 field-position model's band_centres. Rates use "
        "3*sqrt(p(1-p)/n) and means 3*sd/sqrt(n) with the 2012 sd; a row reads "
        "INSUFFICIENT SAMPLE below 30 events. INFORMATIONAL rows are shapes, not grades.", "",
    ] + _band_table(fp_rows) + [
        "",
        "### Ledger coherence", "",
        "Zero-tolerance counts from `runtime.play_detail.check_ledger` (15 original and "
        "17 kernel 2013.7 spot and label classes). Games checked: %d. The kick-row and "
        "label classes need the full snap ledger." % checked, "",
    ] + _coherence_lines(checked, counts) + [""]
    return lines


def calibration_audit_markdown(year, receipts, book):
    legacy, kernel_2013_6, current = cohorts(receipts)
    lines = [
        "# %s statistical band audit" % year, "",
        "**Version:** `%s-W%02d-BAND-AUDIT`" % (year, book["through_week"]),
        through_line(book), "",
        "League-wide receipts compared with the sourced 2012 shapes in "
        "`library/data/2012_nfl_aggregate_baseline.json`, "
        "`library/data/2012_nfl_position_usage_baseline.json`, "
        "`library/data/2012_nfl_drive_model.json` and "
        "`library/data/2012_nfl_field_position_model.json`. This is a defect "
        "detector for engine code and TeamInputs. An OUTSIDE row is investigated; "
        "it never reruns, selects or edits a closed game. Receipts are split into "
        "cohorts by kernel version; grading starts at 16 team-games per cohort.", "",
    ]
    team_games, rows = audit(legacy)
    lines += [
        "## Legacy cohort: kernels 2013.4/2013.5",
        "",
        "**Status:** %s." % LEGACY_LABEL,
        "**Team-games audited:** %d." % team_games, "",
    ] + _band_table(rows) + [
        "",
        "Drive-model rows and ledger coherence: not measurable for this cohort "
        "(legacy receipts carry no drives summary or kicking-attempt counters).", "",
    ]
    team_games, rows = audit(kernel_2013_6, cohort="2013.6")
    drive_games, drive_rows = audit_drive_model(kernel_2013_6, cohort="2013.6")
    checked, counts = coherence(kernel_2013_6, cohort="2013.6")
    lines += [
        "## Kernel 2013.6 cohort (%s, detection only)" % _week_span(kernel_2013_6, "Week 4 onward"), "",
        "**Status:** %s." % KERNEL_2013_6_LABEL,
        "**Team-games audited:** %d." % team_games, "",
    ] + _band_table(rows) + ["", POINTS_NOTE, "",
        "### Drive model rows", "",
        "Centres from the 2012 drive model (nflverse drive definition) and period totals; "
        "tolerance is three standard errors at the observed sample.", "",
    ] + _band_table(drive_rows, "2013.6") + [""] + _known_detection_lines("2013.6") + [
        "### Ledger coherence", "",
        "Zero-tolerance counts from `runtime.play_detail.check_ledger` over every "
        "receipt's drives summary plus the full snap ledgers. Games checked: %d. The "
        "kernel 2013.7 spot and label classes are not measurable for this cohort "
        "(its receipts carry no start spots)." % checked, "",
    ] + _coherence_lines(checked, counts) + [""]
    split = dict(current_cohorts(current))
    lines += _current_cohort_lines("2013.7", split.pop("2013.7", []), "after Week 8; no game closed yet")
    for version, members in sorted(split.items(), key=lambda item: tuple(int(v) for v in item[0].split("."))):
        lines += _current_cohort_lines(version, members, "no game closed yet")
    return "\n".join(lines)


# ---- storage -----------------------------------------------------------------

def _nonzero(line, keep):
    kept = {key: line[key] for key in keep if key in line}
    kept.update({key: value for key, value in line.items()
                 if key not in keep and isinstance(value, (int, float))
                 and not isinstance(value, bool) and value != 0})
    return kept


def compact_book_for_storage(book):
    """The aggregated book without mechanically implied zero fields."""
    compact = {key: value for key, value in book.items() if key not in {"teams", "players"}}
    compact["teams"] = {}
    for team_id, team in book.get("teams", {}).items():
        row = {key: team[key] for key in ("games", "plays", "opponent_plays", "team_stats", "opponent_stats")}
        if "kernel_2014_6_games" in team:
            # Kernel 2014.6 onward only (runtime.statbook field group).
            row["kernel_2014_6_games"] = team["kernel_2014_6_games"]
        row["players"] = {}
        for player_id, line in team.get("players", {}).items():
            kept = _nonzero(line, ("position",))
            if len(kept) > 1 or str(player_id).startswith("__"):
                row["players"][player_id] = kept
        compact["teams"][team_id] = row
    compact["players"] = {}
    for player_id, line in book.get("players", {}).items():
        kept = _nonzero({**line, "teams": list(line.get("teams", ()))}, ("position", "teams"))
        if len(kept) > 2:
            compact["players"][player_id] = kept
    return compact


# The statistics pages the indexes list, in order, with what each holds (2014 onward).
INDEXED_VIEWS = (
    ("team_player_stats.md", "%s player statistics", "the club's players by position"),
    ("team_stats.md", "Team statistics", "every club's offense, defense and special teams, per game"),
    ("league_player_stats.md", "League player statistics", "every player by position, league-wide"),
    ("league_leaders.md", "League leaders", "the leaders at each position and overall"),
    ("play_call_stats.md", "%s play calls", "the club's calls by snaps and results, and its defensive calls by situation"),
    ("all_player_stats.md", "Rosters and player statistics", "club by club, every player who has dressed"),
)


def _rel(path, page):
    import os
    return Path(os.path.relpath(path, Path(page).parent)).as_posix()


def _team_name(team):
    return team.split()[-1] if team else team


def glance_sections(paths, team, book, receipts, page):
    """The statbook's club summary (2014 onward): the season at a glance, the games played and the
    club's leaders, in the words the desk uses (runtime/season_summary.py)."""
    from runtime import people, season_summary as summary
    from runtime.standings import compute
    games = summary.club_games(receipts, team)
    club = book.get("teams", {}).get(team, {})
    first, points, efficiency = summary.glance(club, games, compute(receipts), team)
    lines = ["## Team at a glance", "", "| Season | Scoring | Efficiency |", "|---|---|---|",
             "| %s | %s | %s |" % (first, points, efficiency), "",
             "## Games played", "", "| Week | Opponent | Result |", "|---:|---|---:|"]
    for receipt in games:
        week, other = int(receipt["week"]), summary.opponent(receipt, team)
        ours, theirs = receipt["final_score"][team], receipt["final_score"][other]
        label = ("vs " if receipt["home"] == team else "at ") + other
        report = paths.game_report(week)
        if report.is_file():
            label = "[%s](%s)" % (label, _rel(report, page))
        lines.append("| %d | %s | %s %d-%d |" % (week, label, "W" if ours > theirs else "L" if ours < theirs else "T",
                                                ours, theirs))
    if not games:
        lines.append("| | No game played | |")
    lines += ["", "## Player leaders", "", "| Category | Player | Season total |", "|---|---|---:|"]
    cards = paths.record("player_profiles")
    for label, name, value in summary.leaders(club):
        target = cards / (people.slugify(name) + ".md")
        shown = "[%s](%s)" % (name, _rel(target, page)) if target.is_file() else name
        lines.append("| %s | %s | %s |" % (label, shown, value))
    return lines + [""]


def index_pages(year, team, book, root=ROOT, receipts=()):
    """The statbook index (the Statistics folder's README) and the records index, built from the
    same receipts as the views (2014 onward), with links placed by the folder map. The statbook
    leads with the club's season at a glance, its games and its leaders (``glance_sections``)."""
    from runtime.seasons import SeasonPaths
    paths = SeasonPaths(year, root)
    statbook, records = view_path(paths, STATBOOK), view_path(paths, RECORDS_INDEX)
    tracker = paths.stats / "team_tracker" / "README.md"
    standings = paths.record("standings.md")
    if not book.get("receipt_count"):
        status = "No regular-season game has closed; every page is empty until the first game closes."
    elif book["coverage_complete"]:
        status = "**Through Week %d.** Every closed game is counted (%d games)." % (book["through_week"],
                                                                                  book["receipt_count"])
    else:
        status = ("**Through Week %d.** Coverage is PARTIAL: one or more games lack a complete statistics "
                  "record, so the pages show only the statistics kept." % book["through_week"])
    rows = [["[%s](%s)" % (title % _team_name(team) if "%s" in title else title, _rel(records.parent / name, statbook)),
             what] for name, title, what in INDEXED_VIEWS]
    rows.append(["[%s team tracker](%s)" % (_team_name(team), _rel(tracker, statbook)),
                 "the club's season and game-by-game totals"])
    rows.append(["[Standings](%s)" % _rel(standings, statbook), "division, conference and league standings"])
    top = ["[Regular season](%s)" % _rel(paths.record("regular_season/README.md"), statbook)]
    cards = paths.record("player_profiles/README.md")
    if cards.is_file():
        top.append("[Player pages](%s)" % _rel(cards, statbook))
    top.append("[Head coach's desk](%s)" % _rel(paths.desk, statbook))
    lines = ["# %d regular-season statistics" % year, "", " · ".join(top), "", status, ""]
    if book.get("receipt_count"):
        lines += glance_sections(paths, team, book, receipts, statbook)
    lines += ["## Full statistics", "", "| Page | What it holds |", "|---|---|"]
    lines += ["| %s | %s |" % tuple(row) for row in rows] + [""]
    lines += ["Every page is rebuilt from the game records after each closed week. Preseason games never "
              "count here, and postseason games are kept apart.", ""]
    prior = SeasonPaths(year - 1, root).record(STATBOOK) if year - 1 >= 2013 else None
    if prior is not None and prior.is_file():
        lines += ["The %d season: [statistics](%s)." % (year - 1, _rel(prior, statbook)), ""]
    index = ["# %d statistics pages" % year, "", "[Statistics](%s)" % _rel(statbook, records), "", status, ""]
    index += ["- [%s](%s): %s" % (title % _team_name(team) if "%s" in title else title, name, what)
              for name, title, what in INDEXED_VIEWS]
    index += ["- [%s team tracker](%s): the club's season and game-by-game totals" % (
        _team_name(team), _rel(tracker, records)), ""]
    return {STATBOOK: "\n".join(lines), RECORDS_INDEX: "\n".join(index)}


def render_views(year, team, receipts, root=ROOT):
    from runtime.seasons import require_receipt_season
    require_receipt_season(receipts, year)
    """Every generated stat file, keyed by file name, from one receipt set; from 2014 also the
    statbook and records indexes (``index_pages``). ``view_path`` places each one."""
    book = aggregate_receipts(receipts)
    weeks = change_weeks(receipts)
    views = {
        "season_totals.json": json.dumps(compact_book_for_storage(book), sort_keys=True, separators=(",", ":")) + "\n",
        "team_player_stats.md": team_markdown(year, team, book, weeks),
        "league_player_stats.md": league_markdown(year, book, weeks),
        "all_player_stats.md": all_players_markdown(year, book, weeks),
        "league_leaders.md": leaders_markdown(year, book),
        "play_call_stats.md": play_calls_markdown(year, team, book),
        "team_stats.md": team_stats_markdown(year, book, receipts),
        "calibration_audit.md": calibration_audit_markdown(year, receipts, book),
    }
    from runtime.seasons import SeasonPaths
    from runtime.season_layout import rebase_markdown
    from runtime.season_layout import logical_path
    paths = SeasonPaths(year, ROOT)
    out = {name: rebase_markdown(text, logical_path(year, 'stats/' + name), view_path(paths, name).relative_to(ROOT))
           if name.endswith('.md') else text for name, text in views.items()}
    if clean(year):
        out.update(index_pages(year, team, book, root, receipts))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("year", type=int)
    parser.add_argument("--team", required=True, help="Exact team_id used by game receipts")
    parser.add_argument("--check", action="store_true", help="write nothing; exit 1 when a view is stale")
    args = parser.parse_args()

    from runtime.seasons import SeasonPaths
    paths = SeasonPaths(args.year, ROOT)
    receipts = load_receipts(paths.receipts)
    views = render_views(args.year, args.team, receipts)
    if args.check:
        stale = [view_path(paths, name).relative_to(ROOT).as_posix() for name, text in views.items()
                 if not view_path(paths, name).is_file() or view_path(paths, name).read_text(encoding="utf-8") != text]
        print("\n".join("Statistics view stale: " + s for s in stale) if stale else "STATISTICS CURRENT")
        return 1 if stale else 0
    for name, text in views.items():
        target = view_path(paths, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    print("rendered %d stat views from %d receipts" % (len(views), len(receipts)))
    if args.year >= 2014:
        # The player pages read the same game records (rebuild step 3a); run
        # scripts/render_player_pages.py again once the week's awards are drawn.
        from runtime import player_pages
        player_pages.write(ROOT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
