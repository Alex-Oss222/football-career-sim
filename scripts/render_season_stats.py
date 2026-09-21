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


def coverage_line(book, team_id=None):
    if not book["coverage_complete"]:
        return (
            "**Coverage:** PARTIAL. One or more legacy games lack a complete "
            "stat receipt. Tables show only preserved statistics and must not "
            "be treated as complete league rankings until the gap is backfilled."
        )
    if team_id is not None:
        if not book.get("team_player_attribution_complete", {}).get(team_id, True):
            return (
                "**Coverage:** team totals complete; player attribution PARTIAL "
                "for this club because a branch-roster correction left exact "
                "replacement attribution unknowable."
            )
        return "**Coverage:** complete for this team's stored game receipts."
    if not book.get("player_attribution_complete", True):
        return (
            "**Coverage:** team totals complete; league player attribution PARTIAL "
            "for one or more clubs after branch-roster corrections. Known player "
            "lines are preserved, but formal league rankings are withheld."
        )
    return "**Coverage:** complete for every stored game receipt."


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
        "**Version:** `%s-W%02d-TEAM-STATS-2`" % (year, book["through_week"]),
        "**Through:** Week %d." % book["through_week"],
        coverage_line(book, team_id),
        "",
    ]
    if not team:
        lines += ["No stored receipt currently matches this team identifier.", ""]
        return "\n".join(lines)

    players = team["players"]
    lines += [
        "## Passing", "",
        "| Player | CMP/ATT | YDS | AVG | TD | INT | SACK |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for player, line in player_rows(
        players,
        ("pass_attempts", "passing_yards", "passing_touchdowns", "interceptions"),
        "passing_yards",
    ):
        attempts = line.get("pass_attempts", 0)
        completions = line.get("completions", 0)
        lines.append("| %s | %s/%s | %s | %s | %s | %s | %s |" % (
            player, completions, attempts, line.get("passing_yards", 0),
            avg(line.get("passing_yards", 0), attempts),
            line.get("passing_touchdowns", 0), line.get("interceptions_thrown", line.get("interceptions", 0)),
            line.get("sacks_taken", 0),
        ))

    lines += [
        "", "## Rushing", "",
        "| Player | CAR | YDS | AVG | TD | LNG | FUM |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for player, line in player_rows(
        players,
        ("rushing_attempts", "rushing_yards", "rushing_touchdowns"),
        "rushing_yards",
    ):
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            player, line.get("rushing_attempts", 0), line.get("rushing_yards", 0),
            avg(line.get("rushing_yards", 0), line.get("rushing_attempts", 0)),
            line.get("rushing_touchdowns", 0), line.get("long_rush", 0),
            line.get("fumbles", 0),
        ))

    lines += [
        "", "## Receiving", "",
        "| Player | REC | TGTS | YDS | AVG | TD | LNG |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for player, line in player_rows(
        players,
        ("targets", "receptions", "receiving_yards", "receiving_touchdowns"),
        "receiving_yards",
    ):
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            player, line.get("receptions", 0), line.get("targets", 0),
            line.get("receiving_yards", 0),
            avg(line.get("receiving_yards", 0), line.get("receptions", 0)),
            line.get("receiving_touchdowns", 0), line.get("long_reception", 0),
        ))

    lines += [
        "", "## Defense", "",
        "| Player | SOLO | AST | TOT | SACK | TFL | PD | INT | INT YDS | FF | FR |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for player, line in player_rows(
        players,
        (
            "tackles", "sacks", "tackles_for_loss", "passes_defended",
            "defensive_interceptions", "forced_fumbles", "fumble_recoveries",
        ),
        "tackles",
    ):
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            player, line.get("solo_tackles", 0), line.get("assisted_tackles", 0),
            line.get("tackles", 0), line.get("sacks", 0),
            line.get("tackles_for_loss", 0), line.get("passes_defended", 0),
            line.get("defensive_interceptions", 0),
            line.get("interception_return_yards", 0),
            line.get("forced_fumbles", 0), line.get("fumble_recoveries", 0),
        ))

    lines += [
        "", "## Kicking", "",
        "| Player | FGM/FGA | XPM/XPA | PTS |",
        "|---|---:|---:|---:|",
    ]
    for player, line in player_rows(
        players,
        ("field_goals_attempted", "field_goals_made", "extra_points_attempted", "extra_points_made"),
        "field_goals_made",
    ):
        points = line.get("field_goals_made", 0) * 3 + line.get("extra_points_made", 0)
        lines.append("| %s | %s/%s | %s/%s | %s |" % (
            player, line.get("field_goals_made", 0), line.get("field_goals_attempted", 0),
            line.get("extra_points_made", 0), line.get("extra_points_attempted", 0), points,
        ))

    lines += [
        "", "## Punting", "",
        "| Player | NO | YDS | AVG | LNG | IN20 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for player, line in player_rows(players, ("punts", "punt_yards"), "punt_yards"):
        lines.append("| %s | %s | %s | %s | %s | %s |" % (
            player, line.get("punts", 0), line.get("punt_yards", 0),
            avg(line.get("punt_yards", 0), line.get("punts", 0)),
            line.get("long_punt", 0), line.get("punts_inside_20", 0),
        ))

    lines += [
        "", "## Returns", "",
        "| Player | KR | KR YDS | KR AVG | PR | PR YDS | PR AVG |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for player, line in player_rows(
        players,
        ("kick_returns", "kick_return_yards", "punt_returns", "punt_return_yards"),
        "return_yards",
    ):
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            player, line.get("kick_returns", 0), line.get("kick_return_yards", 0),
            avg(line.get("kick_return_yards", 0), line.get("kick_returns", 0)),
            line.get("punt_returns", 0), line.get("punt_return_yards", 0),
            avg(line.get("punt_return_yards", 0), line.get("punt_returns", 0)),
        ))

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



def all_players_markdown(year, book):
    fields = list(book.get("player_stat_fields", ()))
    preferred_order = [
        "dropbacks", "pass_attempts", "completions", "passing_yards",
        "passing_touchdowns", "interceptions_thrown", "sacks_taken", "sack_yards",
        "rushing_attempts", "rushing_yards", "rushing_touchdowns", "long_rush",
        "targets", "receptions", "receiving_yards", "receiving_touchdowns", "long_reception",
        "fumbles", "fumbles_lost", "sacks_allowed", "sacks", "pressures",
        "solo_tackles", "assisted_tackles", "tackles", "tackles_for_loss",
        "passes_defended", "defensive_interceptions", "interception_return_yards",
        "forced_fumbles", "fumble_recoveries", "field_goals_attempted",
        "field_goals_made", "extra_points_attempted", "extra_points_made",
        "punts", "punt_yards", "long_punt", "punts_inside_20",
        "kick_returns", "kick_return_yards", "punt_returns", "punt_return_yards",
        "return_yards",
    ]
    ordered = [field for field in preferred_order if field in fields]
    ordered += sorted(field for field in fields if field not in ordered)
    labels = {
        "dropbacks":"DB", "pass_attempts":"PassAtt", "completions":"Cmp",
        "passing_yards":"PassYds", "passing_touchdowns":"PassTD",
        "interceptions_thrown":"INT", "sacks_taken":"SackTaken",
        "rushing_attempts":"RushAtt", "rushing_yards":"RushYds",
        "rushing_touchdowns":"RushTD", "targets":"Tgt", "receptions":"Rec",
        "receiving_yards":"RecYds", "receiving_touchdowns":"RecTD",
        "sacks_allowed":"SackAllowed", "sacks":"Sack", "pressures":"Press",
        "tackles":"Tkl", "tackles_for_loss":"TFL", "passes_defended":"PD",
        "defensive_interceptions":"DefINT", "forced_fumbles":"FF",
        "fumble_recoveries":"FR", "field_goals_made":"FGM",
        "field_goals_attempted":"FGA", "extra_points_made":"XPM",
        "extra_points_attempted":"XPA", "punts":"Punt", "punt_yards":"PuntYds",
        "kick_returns":"KR", "kick_return_yards":"KRYds", "punt_returns":"PR",
        "punt_return_yards":"PRYds", "return_yards":"RetYds",
    }
    lines = [
        "# %s NFL all-player stat ledger" % year, "",
        "**Version:** `%s-W%02d-ALL-PLAYER-STATS-2`" % (year, book["through_week"]),
        "**Through:** Week %d." % book["through_week"],
        coverage_line(book), "",
        "Compact comprehensive ledger of every nonzero supported player counter "
        "preserved by the closed-game receipts. Zero-only rows are omitted from "
        "this readable view; absence does not prove non-participation.", "",
        "| Player | Team(s) | Pos | Nonzero stored statistics |",
        "|---|---|---|---|",
    ]
    rows=[]
    for player_id,line in book.get("players",{}).items():
        if str(player_id).startswith("__"):
            continue
        nonzero=[
            (field,line.get(field,0)) for field in ordered
            if isinstance(line.get(field,0),(int,float))
            and not isinstance(line.get(field,0),bool)
            and line.get(field,0)!=0
        ]
        if nonzero:
            rows.append((player_id,line,nonzero))
    rows.sort(key=lambda item:(
        ", ".join(item[1].get("teams",())),
        item[1].get("position",""), item[0]))
    for player,line,nonzero in rows:
        stats="; ".join(
            "%s=%s" % (labels.get(field,field),value)
            for field,value in nonzero)
        lines.append("| %s | %s | %s | %s |" % (
            player, ", ".join(line.get("teams",())),
            line.get("position",""), stats))
    lines.append("")
    return "\n".join(lines)


def compact_book_for_storage(book):
    """Remove mechanically implied zero fields from the generated JSON cache."""
    compact = {
        key: value for key,value in book.items()
        if key not in {"teams","players"}
    }
    compact["teams"]={}
    for team_id,team in book.get("teams",{}).items():
        row={"games":team.get("games",0),"team_stats":dict(team.get("team_stats",{})),"players":{}}
        for player_id,line in team.get("players",{}).items():
            kept={"position":line.get("position","")}
            kept.update({
                key:value for key,value in line.items()
                if key!="position" and isinstance(value,(int,float))
                and not isinstance(value,bool) and value!=0
            })
            if len(kept)>1 or str(player_id).startswith("__"):
                row["players"][player_id]=kept
        compact["teams"][team_id]=row
    compact["players"]={}
    for player_id,line in book.get("players",{}).items():
        kept={"position":line.get("position",""),"teams":list(line.get("teams",()))}
        kept.update({
            key:value for key,value in line.items()
            if key not in {"position","teams"} and isinstance(value,(int,float))
            and not isinstance(value,bool) and value!=0
        })
        if len(kept)>2:
            compact["players"][player_id]=kept
    return compact


def leaders_markdown(year, book):
    lines = [
        "# %s NFL statistical leaders" % year,
        "",
        "**Version:** `%s-W%02d-LEADERS-1`" % (year, book["through_week"]),
        "**Through:** Week %d." % book["through_week"],
        coverage_line(book),
        "",
    ]
    if not book["coverage_complete"] or not book.get("player_attribution_complete", True):
        lines += [
            "League rankings are withheld while player attribution is incomplete. "
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



def play_calls_markdown(year, team_id, book):
    calls = book.get("play_calls", {}).get(team_id, {})
    lines = [
        "# %s %s offensive play-call statistics" % (year, team_id),
        "",
        "**Version:** `%s-W%02d-PLAY-CALL-STATS-1`" % (year, book["through_week"]),
        "**Through:** Week %d." % book["through_week"],
        coverage_line(book, team_id),
        "",
        "These are generated game-use totals for the named calls supplied in the weekly offensive call sheet. Generic calls appear only when a game packet did not provide a named call menu.",
        "",
        "| Call | Family | Snaps | Runs | Dropbacks | CMP/ATT | Yards | YPP | TD | TO | Sacks |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    rows = sorted(calls.items(), key=lambda item: (-item[1].get("snaps", 0), item[0]))
    for name, line in rows:
        snaps = line.get("snaps", 0)
        lines.append("| %s | %s | %s | %s | %s | %s/%s | %s | %s | %s | %s | %s |" % (
            name, line.get("family", name), snaps, line.get("runs", 0),
            line.get("dropbacks", 0), line.get("completions", 0),
            line.get("pass_attempts", 0), line.get("yards", 0),
            avg(line.get("yards", 0), snaps), line.get("touchdowns", 0),
            line.get("turnovers", 0), line.get("sacks", 0),
        ))
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
        json.dumps(compact_book_for_storage(book), sort_keys=True, separators=(",",":")) + "\n", encoding="utf-8"
    )
    (stats_dir / "team_player_stats.md").write_text(
        team_markdown(args.year, args.team, book), encoding="utf-8"
    )
    (stats_dir / "league_player_stats.md").write_text(
        league_markdown(args.year, book), encoding="utf-8"
    )
    (stats_dir / "all_player_stats.md").write_text(
        all_players_markdown(args.year, book), encoding="utf-8"
    )
    (stats_dir / "league_leaders.md").write_text(
        leaders_markdown(args.year, book), encoding="utf-8"
    )
    (stats_dir / "play_call_stats.md").write_text(
        play_calls_markdown(args.year, args.team, book), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
