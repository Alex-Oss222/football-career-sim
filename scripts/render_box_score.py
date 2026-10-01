#!/usr/bin/env python3
"""Render a game's box score from its closed-game stat receipt.

A weekly output.md marks where the box score belongs:

    <!-- box-score event=EVENT_ID team=Jacksonville Jaguars -->
    <!-- /box-score -->

`--write OUTPUT_MD` fills every marked block in that file from the named
receipts; validation fails if a block no longer matches its receipt.

Two layouts, chosen by `--season`: the 2013 box score below (team comparison,
category tables, drive chart), kept byte-identical for the closed 2013
outputs, and from 2014 the gamebook layout of the weekly game turn template
(scoring summary, team stats, eleven individual tables per club, drive chart,
snap counts) in runtime/gamebook.py, whose docstring lists the rows and
columns each receipt field supports and the ones left out. `--line-score`
prints the template's Section 3 line score for a 2014-onward receipt.
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

from runtime.stat_tables import (
    BOX_DEFENSE, COVERAGE, FUMBLES, KICKING, LINE_STARTS, LONG_SNAPS, OFFENSIVE_LINE, PUNTING,
    RECEIVING, RETURNS, RUSHING, avg,
    combine, derived, col, g, passer_rating, pct, table, thrown, time_text,
)

RECEIPTS = ROOT / "career" / "2013" / "stats" / "game_receipts"
BLOCK = re.compile(
    r"(<!-- box-score event=(?P<event>[^ ]+) team=(?P<team>.+?) -->\n)(?P<body>.*?)(<!-- /box-score -->)",
    re.S,
)
UNATTRIBUTED = "Team / unattributed"

BOX_PASSING = (
    derived("CMP/ATT", lambda l: "%d/%d" % (g(l, "completions"), g(l, "pass_attempts"))),
    col("YDS", "passing_yards"),
    derived("AVG", lambda l: avg(g(l, "passing_yards"), g(l, "pass_attempts"))),
    col("TD", "passing_touchdowns"),
    derived("INT", thrown),
    derived("SCK", lambda l: "%d-%d" % (g(l, "sacks_taken"), g(l, "sack_yards"))),
    derived("RTG", passer_rating),
)

CATEGORIES = (
    # (title, columns, fields that put a player in the table, sort field, team total)
    ("Passing", BOX_PASSING, ("pass_attempts", "sacks_taken"), "passing_yards", True),
    ("Rushing", RUSHING, ("rushing_attempts",), "rushing_yards", True),
    ("Receiving", RECEIVING, ("targets", "receptions"), "receiving_yards", True),
    ("Fumbles", FUMBLES, ("fumbles",), "fumbles", False),
    ("Defense", BOX_DEFENSE, ("tackles", "sacks", "passes_defended", "defensive_interceptions",
                              "forced_fumbles", "fumble_recoveries"), "tackles", True),
    ("Kicking", KICKING, ("field_goals_attempted", "extra_points_attempted"), "field_goals_made", False),
    ("Punting", PUNTING, ("punts",), "punt_yards", False),
    ("Returns", RETURNS, ("kick_returns", "punt_returns"), "return_yards", False),
    # Kernel 2014.3 sections appear only in receipts that carry these fields.
    ("Offensive line", (LINE_STARTS,) + OFFENSIVE_LINE, ("line_starts",), "sacks_allowed", True),
    ("Coverage", COVERAGE, ("special_teams_tackles",), "special_teams_tackles", True),
    ("Long snapping", (LONG_SNAPS,), ("long_snaps",), "long_snaps", False),
)


def load_receipt(event_id, directory=RECEIPTS):
    """The receipt whose event_id matches, whatever its file name. Postseason
    receipts sit in the sibling postseason_receipts directory."""
    base = Path(directory)
    paths = sorted(base.glob("*.json")) + sorted((base.parent / "postseason_receipts").glob("*.json"))
    for path in paths:
        receipt = json.loads(path.read_text(encoding="utf-8"))
        if receipt.get("event_id") == event_id:
            return receipt
    raise FileNotFoundError("no receipt for event %s" % event_id)


def team_order(receipt, lead_team):
    clubs = [receipt["away"], receipt["home"]]
    if lead_team not in clubs:
        raise ValueError("%s did not play in %s" % (lead_team, receipt["event_id"]))
    return [lead_team] + [c for c in clubs if c != lead_team]


def comparison(receipt, clubs):
    stats = {c: receipt["team_stats"][c] for c in clubs}
    players = {c: combine(stats[c].get("players", {}).values()) for c in clubs}

    def row(label, fn):
        return "| %s | %s |" % (label, " | ".join(str(fn(c)) for c in clubs))

    plays = lambda c: g(players[c], "rushing_attempts") + g(players[c], "dropbacks")
    yards = lambda c: stats[c]["passing_yards"] + stats[c]["rushing_yards"]
    lines = [
        "#### Team comparison", "",
        "| Statistic | " + " | ".join(clubs) + " |",
        "|---|" + "---:|" * len(clubs),
        row("Final score", lambda c: receipt["final_score"][c]),
        row("First downs", lambda c: stats[c]["first_downs"]),
        row("Third down", lambda c: "%d/%d (%s%%)" % (
            stats[c]["third_down_conversions"], stats[c]["third_down_attempts"],
            pct(stats[c]["third_down_conversions"], stats[c]["third_down_attempts"]))),
        row("Plays", plays),
        row("Total yards", yards),
        row("Yards per play", lambda c: avg(yards(c), plays(c))),
        row("Passing yards", lambda c: stats[c]["passing_yards"]),
        row("Completions/attempts", lambda c: "%d/%d" % (
            g(players[c], "completions"), g(players[c], "pass_attempts"))),
        row("Sacked-yards lost", lambda c: "%d-%d" % (g(players[c], "sacks_taken"), g(players[c], "sack_yards"))),
        row("Rushing yards", lambda c: stats[c]["rushing_yards"]),
        row("Rushing attempts", lambda c: g(players[c], "rushing_attempts")),
        row("Penalties-yards", lambda c: "%d-%d" % (stats[c]["penalties"], stats[c]["penalty_yards"])),
        row("Turnovers", lambda c: stats[c]["turnovers"]),
        row("Time of possession", lambda c: time_text(stats[c]["time_of_possession"])),
        "",
    ]
    return lines


def team_box(team_id, players):
    lines = ["#### " + team_id, ""]
    for title, columns, fields, sort_field, with_total in CATEGORIES:
        rows = [(UNATTRIBUTED if str(p).startswith("__") else p, line)
                for p, line in players.items() if any(g(line, f) for f in fields)]
        if not rows:
            continue
        rows.sort(key=lambda item: (item[0] == UNATTRIBUTED, -g(item[1], sort_field), item[0]))
        total = combine(line for _, line in rows) if with_total and len(rows) > 1 else None
        lines += ["##### " + title, ""] + table(None, rows, columns, total=total)
    return lines


START_KIND = {
    "kickoff": "kickoff", "kickoff_touchback": "kickoff (touchback)", "free_kick": "free kick",
    "punt": "punt", "interception": "interception", "fumble_lost": "fumble", "downs": "downs",
    "missed_fg": "missed FG", "period_change": "period change", "placement": "placed at the 25",
}
RESULT = {
    "touchdown": "Touchdown", "field_goal_attempt": "FG", "punt": "Punt", "interception": "Interception",
    "fumble_lost": "Fumble lost", "downs": "Downs", "safety": "Safety", "end_of_half": "End of half",
    "end_of_game": "End of game", "end_of_overtime": "End of overtime", "end_of_quarter": "End of quarter",
}


def spot_text(spot):
    """yardline_100 as a field position: 'own 25', 'opp 40' or 'midfield'."""
    if spot is None:
        return "—"
    if spot == 50:
        return "midfield"
    return "own %d" % (100 - spot) if spot > 50 else "opp %d" % spot


def clock_text(half, seconds, game_type="regular"):
    if half == "OT" and game_type == "postseason":
        # Kernel 2013.8 postseason overtime: one continuous countdown of
        # periods (runtime.rules.postseason_ot_period_bound), labelled per period.
        from runtime.play_detail import _period_clock
        from runtime.rules import RULES
        label, text = _period_clock(seconds, overtime=(
            "OT", RULES.postseason_ot_period_bound, RULES.postseason_ot_seconds))
        return "%s %s" % (label, text)
    if half == "OT":
        return "OT %d:%02d" % (seconds // 60, seconds % 60)
    left = seconds - 900 if seconds > 900 else seconds
    quarter = {1: 1 if seconds > 2700 else 2, 2: 3 if seconds > 900 else 4}[half]
    if half == 1:
        left = seconds - 2700 if seconds > 2700 else seconds - 1800
    return "Q%d %d:%02d" % (quarter, left // 60, left % 60)


def drive_chart(receipt):
    """Kernel 2013.7-or-later receipts: every possession's start, end and result."""
    from runtime.play_detail import DRIVE_SUMMARY_FIELDS
    drives = [dict(zip(DRIVE_SUMMARY_FIELDS, row)) for row in receipt.get("drives", ())]
    if not drives or any(d.get("start_spot") is None for d in drives):
        return []
    # Kernel 2014.4 receipts walk the state from the drive's own snaps;
    # earlier receipts keep their original wording.
    walked = all(d.get("chain_model") for d in drives)
    state_text = ("downs result shows the down and distance before the kick, or before the failed "
                  "fourth-down snap, walked from the drive's own snaps." if walked else
                  "downs result shows the real 2012 fourth-down state its drive carried.")
    lines = ["#### Drive chart", "",
             "Start and end are field positions for the offense; a punt, field-goal or " + state_text, "",
             "| # | Team | Start clock | Start | How | Plays | Yds | End | Result |",
             "|---:|---|---|---|---|---:|---:|---|---|"]
    for d in drives:
        result = RESULT.get(d["category"], d["category"])
        if d["category"] == "field_goal_attempt":
            result = "FG %s (%d yd)" % ("good" if d.get("fg_made") else "no good", d["fg_distance"])
        elif d["category"] == "touchdown" and d.get("xp_made") is not None:
            result += ", XP %s" % ("good" if d["xp_made"] else "no good")
        fourth = d.get("fourth_down")
        if fourth and fourth.get("down") and fourth.get("ydstogo") is not None:
            result += " (%s & %d at %s)" % (
                {1: "1st", 2: "2nd", 3: "3rd", 4: "4th"}.get(fourth["down"], fourth["down"]),
                fourth["ydstogo"], spot_text(fourth["los"]))
        end = "end zone" if d["category"] in ("touchdown", "safety") else spot_text(d.get("end_spot"))
        lines.append("| %d | %s | %s | %s | %s | %d | %d | %s | %s |" % (
            d["number"], d["team"], clock_text(d["half"], d["start_clock"], receipt.get("game_type", "regular")), spot_text(d["start_spot"]),
            START_KIND.get(d.get("start_kind"), d.get("start_kind") or "—"), d["scrimmage_plays"],
            d["net_yards"], end, result))
    return lines + [""]


GAMEBOOK_FROM_SEASON = 2014


def render(receipt, lead_team, season=2013):
    """The box score for one club's output: 2013 layout, or the gamebook from 2014."""
    if season >= GAMEBOOK_FROM_SEASON:
        from runtime.gamebook import render as render_gamebook
        return render_gamebook(receipt, lead_team)
    clubs = team_order(receipt, lead_team)
    lines = comparison(receipt, clubs)
    for club in clubs:
        lines += team_box(club, receipt["team_stats"][club].get("players", {}))
    lines += drive_chart(receipt)
    return "\n".join(lines)


def fill(text, directory=RECEIPTS, season=2013):
    """Return text with every marked box-score block regenerated."""
    def replace(match):
        body = render(load_receipt(match.group("event"), directory), match.group("team"), season)
        return match.group(1) + body + "\n" + match.group(5)
    return BLOCK.sub(replace, text)


def stale_blocks(path, directory=RECEIPTS, season=2013):
    """Event ids whose marked box score no longer matches its receipt."""
    text = Path(path).read_text(encoding="utf-8")
    stale = []
    for match in BLOCK.finditer(text):
        expected = render(load_receipt(match.group("event"), directory), match.group("team"), season) + "\n"
        if match.group("body") != expected:
            stale.append(match.group("event"))
    return stale


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("event_id", nargs="?", help="Receipt event id to print")
    parser.add_argument("--team", help="Club listed first (defaults to the home club)")
    parser.add_argument("--write", metavar="OUTPUT_MD", help="Fill the marked box-score blocks in this file")
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--line-score", action="store_true",
                        help="Print the line score (2014 onward) instead of the box score")
    parser.add_argument("--preseason", action="store_true",
                        help="Read the season's preseason receipts (preseason_games/statistics) instead")
    args = parser.parse_args()
    from runtime.seasons import SeasonPaths, require_receipt_season
    paths = SeasonPaths(args.season, ROOT)
    receipts = paths.preseason_receipts if args.preseason else paths.receipts
    if args.write:
        path = Path(args.write).resolve()
        if not path.is_relative_to(paths.career):
            parser.error('--write must belong to the requested career season')
        text = path.read_text(encoding="utf-8")
        for match in BLOCK.finditer(text):
            require_receipt_season([load_receipt(match.group('event'), receipts)], args.season)
        path.write_text(fill(text, receipts, args.season), encoding="utf-8")
        print("filled box scores in %s" % path)
        return
    if not args.event_id:
        parser.error("give an event id or --write OUTPUT_MD")
    receipt = load_receipt(args.event_id, receipts)
    require_receipt_season([receipt], args.season)
    if args.line_score:
        if args.season < GAMEBOOK_FROM_SEASON:
            parser.error("--line-score needs a 2014-or-later season")
        from runtime.gamebook import line_score_table
        print(line_score_table(receipt))
        return
    print(render(receipt, args.team or receipt["home"], args.season))


if __name__ == "__main__":
    main()
