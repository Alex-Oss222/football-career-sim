#!/usr/bin/env python3
"""Rebuild public season-stat views from closed game stat receipts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.statbook import aggregate_receipts, leaders


def load_receipts(directory):
    receipts = []
    for path in sorted(directory.glob("*.json")):
        with path.open(encoding="utf-8") as handle:
            receipts.append(json.load(handle))
    return receipts


def coverage_line(book):
    if book["coverage_complete"]:
        return "**Coverage:** complete for every stored game receipt."
    return (
        "**Coverage:** PARTIAL. One or more legacy games lack a complete "
        "player-level receipt. Tables show only preserved statistics and must "
        "not be treated as complete league rankings until the gap is backfilled."
    )


def avg(yards, opportunities):
    return "%.1f" % (yards / opportunities) if opportunities else "—"


def player_rows(players, fields, sort_field):
    rows = []
    for player_id, line in players.items():
        if str(player_id).startswith("__"):
            continue
        if not any(line.get(field, 0) for field in fields):
            continue
        rows.append((player_id, line))
    rows.sort(key=lambda item: (-item[1].get(sort_field, 0), item[0]))
    return rows


def team_markdown(year, team_id, book):
    team = book["teams"].get(team_id)
    lines = [
        "# %s %s player statistics" % (year, team_id),
        "",
        "**Version:** `%s-W%02d-TEAM-STATS-1`" % (year, book["through_week"]),
        "**Through:** Week %d." % book["through_week"],
        coverage_line(book),
        "",
    ]
    if not team:
        lines += ["No stored receipt currently matches this team identifier.", ""]
        return "\n".join(lines)

    players = team["players"]
    lines += ["## Passing", "", "| Player | ATT | YDS | INT |", "|---|---:|---:|---:|"]
    for player, line in player_rows(players, ("pass_attempts", "passing_yards", "interceptions"), "passing_yards"):
        lines.append("| %s | %s | %s | %s |" % (
            player, line["pass_attempts"], line["passing_yards"], line["interceptions"]))
    lines += ["", "## Rushing", "", "| Player | CAR | YDS | AVG |", "|---|---:|---:|---:|"]
    for player, line in player_rows(players, ("rushing_attempts", "rushing_yards"), "rushing_yards"):
        lines.append("| %s | %s | %s | %s |" % (
            player, line["rushing_attempts"], line["rushing_yards"],
            avg(line["rushing_yards"], line["rushing_attempts"])))
    lines += ["", "## Receiving", "", "| Player | REC | YDS | AVG |", "|---|---:|---:|---:|"]
    for player, line in player_rows(players, ("receptions", "receiving_yards"), "receiving_yards"):
        lines.append("| %s | %s | %s | %s |" % (
            player, line["receptions"], line["receiving_yards"],
            avg(line["receiving_yards"], line["receptions"])))
    lines += ["", "## Defense", "", "| Player | TKL | SACK |", "|---|---:|---:|"]
    for player, line in player_rows(players, ("tackles", "sacks"), "tackles"):
        lines.append("| %s | %s | %s |" % (
            player, line["tackles"], line["sacks"]))
    lines += ["", "## Special teams", "", "| Player | FGM | PUNTS | RET YDS |", "|---|---:|---:|---:|"]
    for player, line in player_rows(players, ("field_goals_made", "punts", "return_yards"), "return_yards"):
        lines.append("| %s | %s | %s | %s |" % (
            player, line["field_goals_made"], line["punts"], line["return_yards"]))
    lines.append("")
    return "\n".join(lines)


def league_markdown(year, book):
    players = book["players"]
    lines = [
        "# %s NFL player statistics" % year,
        "",
        "**Version:** `%s-W%02d-LEAGUE-PLAYER-STATS-1`" % (year, book["through_week"]),
        "**Through:** Week %d." % book["through_week"],
        coverage_line(book),
        "",
    ]
    categories = (
        ("Passing", ("pass_attempts", "passing_yards", "interceptions"), "passing_yards",
         "| Player | Team(s) | ATT | YDS | INT |", "|---|---|---:|---:|---:|"),
        ("Rushing", ("rushing_attempts", "rushing_yards"), "rushing_yards",
         "| Player | Team(s) | CAR | YDS | AVG |", "|---|---|---:|---:|---:|"),
        ("Receiving", ("receptions", "receiving_yards"), "receiving_yards",
         "| Player | Team(s) | REC | YDS | AVG |", "|---|---|---:|---:|---:|"),
        ("Defense", ("tackles", "sacks"), "tackles",
         "| Player | Team(s) | TKL | SACK |", "|---|---|---:|---:|"),
    )
    for title, fields, sort_field, header, separator in categories:
        lines += ["## " + title, "", header, separator]
        for player, line in player_rows(players, fields, sort_field):
            teams = ", ".join(line.get("teams", ()))
            if title == "Passing":
                row = (player, teams, line["pass_attempts"], line["passing_yards"], line["interceptions"])
            elif title == "Rushing":
                row = (player, teams, line["rushing_attempts"], line["rushing_yards"],
                       avg(line["rushing_yards"], line["rushing_attempts"]))
            elif title == "Receiving":
                row = (player, teams, line["receptions"], line["receiving_yards"],
                       avg(line["receiving_yards"], line["receptions"]))
            else:
                row = (player, teams, line["tackles"], line["sacks"])
            if title == "Defense":
                lines.append("| %s | %s | %s | %s |" % row)
            else:
                lines.append("| %s | %s | %s | %s | %s |" % row)
        lines.append("")
    return "\n".join(lines)


def leaders_markdown(year, book):
    lines = [
        "# %s NFL statistical leaders" % year,
        "",
        "**Version:** `%s-W%02d-LEADERS-1`" % (year, book["through_week"]),
        "**Through:** Week %d." % book["through_week"],
        coverage_line(book),
        "",
    ]
    if not book["coverage_complete"]:
        lines += [
            "League rankings are withheld while coverage is incomplete. "
            "Known lines remain available in `league_player_stats.md`, but "
            "they are not labeled as league leaders.",
            "",
        ]
        return "\n".join(lines)

    for title, field in (
        ("Passing yards", "passing_yards"),
        ("Rushing yards", "rushing_yards"),
        ("Receiving yards", "receiving_yards"),
        ("Sacks", "sacks"),
        ("Tackles", "tackles"),
    ):
        lines += ["## " + title, "", "| Rank | Player | Team(s) | Total |", "|---:|---|---|---:|"]
        for rank, row in enumerate(leaders(book, field), 1):
            lines.append("| %d | %s | %s | %s |" % (
                rank, row["player_id"], ", ".join(row["teams"]), row["value"]))
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("year", type=int)
    parser.add_argument("--team", required=True, help="Exact team_id used by game receipts")
    args = parser.parse_args()

    stats_dir = ROOT / "career" / str(args.year) / "stats"
    receipts_dir = stats_dir / "game_receipts"
    receipts = load_receipts(receipts_dir)
    if not receipts:
        raise SystemExit("no stat receipts found in %s" % receipts_dir)

    book = aggregate_receipts(receipts)
    stats_dir.mkdir(parents=True, exist_ok=True)
    (stats_dir / "season_totals.json").write_text(
        json.dumps(book, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (stats_dir / "team_player_stats.md").write_text(
        team_markdown(args.year, args.team, book), encoding="utf-8"
    )
    (stats_dir / "league_player_stats.md").write_text(
        league_markdown(args.year, book), encoding="utf-8"
    )
    (stats_dir / "league_leaders.md").write_text(
        leaders_markdown(args.year, book), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
