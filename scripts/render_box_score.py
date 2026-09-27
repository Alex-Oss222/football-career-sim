#!/usr/bin/env python3
"""Render a game's box score from its closed-game stat receipt.

A weekly output.md marks where the box score belongs:

    <!-- box-score event=EVENT_ID team=Jacksonville Jaguars -->
    <!-- /box-score -->

`--write OUTPUT_MD` fills every marked block in that file from the named
receipts; validation fails if a block no longer matches its receipt.
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
    BOX_DEFENSE, FUMBLES, KICKING, PUNTING, RECEIVING, RETURNS, RUSHING, avg,
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
)


def load_receipt(event_id, directory=RECEIPTS):
    path = Path(directory) / (event_id + ".json")
    return json.loads(path.read_text(encoding="utf-8"))


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


def render(receipt, lead_team):
    clubs = team_order(receipt, lead_team)
    lines = comparison(receipt, clubs)
    for club in clubs:
        lines += team_box(club, receipt["team_stats"][club].get("players", {}))
    return "\n".join(lines)


def fill(text, directory=RECEIPTS):
    """Return text with every marked box-score block regenerated."""
    def replace(match):
        body = render(load_receipt(match.group("event"), directory), match.group("team"))
        return match.group(1) + body + "\n" + match.group(5)
    return BLOCK.sub(replace, text)


def stale_blocks(path, directory=RECEIPTS):
    """Event ids whose marked box score no longer matches its receipt."""
    text = Path(path).read_text(encoding="utf-8")
    stale = []
    for match in BLOCK.finditer(text):
        expected = render(load_receipt(match.group("event"), directory), match.group("team")) + "\n"
        if match.group("body") != expected:
            stale.append(match.group("event"))
    return stale


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("event_id", nargs="?", help="Receipt event id to print")
    parser.add_argument("--team", help="Club listed first (defaults to the home club)")
    parser.add_argument("--write", metavar="OUTPUT_MD", help="Fill the marked box-score blocks in this file")
    args = parser.parse_args()
    if args.write:
        path = Path(args.write)
        path.write_text(fill(path.read_text(encoding="utf-8")), encoding="utf-8")
        print("filled box scores in %s" % path)
        return
    if not args.event_id:
        parser.error("give an event id or --write OUTPUT_MD")
    receipt = load_receipt(args.event_id)
    print(render(receipt, args.team or receipt["home"]))


if __name__ == "__main__":
    main()
