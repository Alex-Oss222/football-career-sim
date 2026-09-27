#!/usr/bin/env python3
"""Rebuild public season-stat views from closed game stat receipts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.bands import audit
from runtime.statbook import aggregate_receipts, leaders


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


def coverage_line(book, team_id=None):
    if not book.get("receipt_count"):
        return "**Coverage:** no closed-game receipts yet; every table is empty."
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
        through_line(book),
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
        "**Version:** `%s-W%02d-LEAGUE-PLAYER-STATS-3`" % (year, book["through_week"]),
        through_line(book),
        coverage_line(book),
        "",
    ]
    categories = (
        ("Passing", ("pass_attempts", "passing_yards"), "passing_yards",
         "| Player | Team(s) | CMP/ATT | YDS | AVG | TD | INT | SACK |",
         "|---|---|---:|---:|---:|---:|---:|---:|",
         lambda l: ("%s/%s" % (l["completions"], l["pass_attempts"]), l["passing_yards"],
                    avg(l["passing_yards"], l["pass_attempts"]), l["passing_touchdowns"],
                    l.get("interceptions_thrown", l["interceptions"]), l["sacks_taken"])),
        ("Rushing", ("rushing_attempts", "rushing_yards"), "rushing_yards",
         "| Player | Team(s) | CAR | YDS | AVG | TD | LNG | FUM |",
         "|---|---|---:|---:|---:|---:|---:|---:|",
         lambda l: (l["rushing_attempts"], l["rushing_yards"],
                    avg(l["rushing_yards"], l["rushing_attempts"]), l["rushing_touchdowns"],
                    l["long_rush"], l["fumbles"])),
        ("Receiving", ("targets", "receptions", "receiving_yards"), "receiving_yards",
         "| Player | Team(s) | REC | TGT | YDS | AVG | TD | LNG |",
         "|---|---|---:|---:|---:|---:|---:|---:|",
         lambda l: (l["receptions"], l["targets"], l["receiving_yards"],
                    avg(l["receiving_yards"], l["receptions"]), l["receiving_touchdowns"],
                    l["long_reception"])),
        ("Defense", ("tackles", "sacks", "defensive_interceptions", "passes_defended"), "tackles",
         "| Player | Team(s) | TKL | SOLO | AST | TFL | SACK | INT | PD | FF |",
         "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
         lambda l: (l["tackles"], l["solo_tackles"], l["assisted_tackles"], l["tackles_for_loss"],
                    l["sacks"], l["defensive_interceptions"], l["passes_defended"],
                    l["forced_fumbles"])),
    )
    for title, fields, sort_field, header, separator, cells in categories:
        lines += ["## " + title, "", header, separator]
        for player, line in player_rows(players, fields, sort_field):
            row = (player, ", ".join(line.get("teams", ()))) + tuple(cells(line))
            lines.append("| " + " | ".join(str(value) for value in row) + " |")
        lines.append("")
    return "\n".join(lines)


def team_stats_markdown(year, book):
    lines = [
        "# %s NFL team statistics" % year,
        "",
        "**Version:** `%s-W%02d-TEAM-TOTALS-1`" % (year, book["through_week"]),
        through_line(book),
        "**Coverage:** team totals are complete for every stored receipt; records and tiebreaks live in `../standings.md`.",
        "",
        "Per-game averages from closed-game receipts. Plays are rushing attempts plus dropbacks.",
        "",
        "| Team | G | PTS/G | YDS/G | PASS/G | RUSH/G | PLAYS/G | 1D/G | 3RD | TO | SACKS ALLOWED | PEN/G | TOP/G |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    rows = []
    for team_id, team in book.get("teams", {}).items():
        games = team.get("games", 0)
        if not games:
            continue
        t = team["team_stats"]
        plays = sum(
            line.get("rushing_attempts", 0) + line.get("dropbacks", 0)
            for line in team.get("players", {}).values()
        )
        per = lambda value: "%.1f" % (value / games)
        top = t["time_of_possession"] / games
        rows.append((t["points"] / games, (
            team_id, games, per(t["points"]), per(t["passing_yards"] + t["rushing_yards"]),
            per(t["passing_yards"]), per(t["rushing_yards"]), per(plays), per(t["first_downs"]),
            "%s/%s" % (t["third_down_conversions"], t["third_down_attempts"]),
            t["turnovers"], t["sacks_allowed"], per(t["penalties"]),
            "%d:%02d" % (top // 60, top % 60),
        )))
    rows.sort(key=lambda item: (-item[0], item[1][0]))
    for _, row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    lines.append("")
    return "\n".join(lines)


def calibration_audit_markdown(year, receipts, book):
    team_games, rows = audit(receipts)
    lines = [
        "# %s statistical band audit" % year,
        "",
        "**Version:** `%s-W%02d-BAND-AUDIT-1`" % (year, book["through_week"]),
        through_line(book),
        "**Team-games audited:** %d (grading starts at 16)." % team_games,
        "",
        "League-wide receipts compared with the sourced 2012 shapes in "
        "`library/data/2012_nfl_aggregate_baseline.json` and "
        "`library/data/2012_nfl_position_usage_baseline.json`. This is a defect "
        "detector for engine code and TeamInputs. An OUTSIDE row is investigated; "
        "it never reruns, selects or edits a closed game.",
        "",
        "| Metric | Observed | 2012 band centre | Tolerance | Status |",
        "|---|---:|---:|---:|---|",
    ]
    fmt = lambda v: "—" if v is None else ("%.3f" % v if abs(v) < 2 else "%.1f" % v)
    for metric, observed, band, tolerance, status in rows:
        lines.append("| %s | %s | %s | ±%s | %s |" % (
            metric, fmt(observed), fmt(band), fmt(tolerance), status))
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
        through_line(book),
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
        "**Version:** `%s-W%02d-LEADERS-3`" % (year, book["through_week"]),
        through_line(book),
        coverage_line(book),
        "",
    ]
    if not book.get("receipt_count"):
        lines += ["No regular-season game has closed, so no leader exists yet.", ""]
        return "\n".join(lines)
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
        ("Passing touchdowns", "passing_touchdowns"),
        ("Rushing yards", "rushing_yards"),
        ("Rushing touchdowns", "rushing_touchdowns"),
        ("Receptions", "receptions"),
        ("Receiving yards", "receiving_yards"),
        ("Receiving touchdowns", "receiving_touchdowns"),
        ("Tackles", "tackles"),
        ("Tackles for loss", "tackles_for_loss"),
        ("Sacks", "sacks"),
        ("Interceptions", "defensive_interceptions"),
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
        through_line(book),
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

def render_views(year, team, receipts):
    """Every generated stat file, keyed by file name, from one receipt set."""
    book = aggregate_receipts(receipts)
    return {
        "season_totals.json": json.dumps(
            compact_book_for_storage(book), sort_keys=True, separators=(",", ":")
        ) + "\n",
        "team_player_stats.md": team_markdown(year, team, book),
        "league_player_stats.md": league_markdown(year, book),
        "all_player_stats.md": all_players_markdown(year, book),
        "league_leaders.md": leaders_markdown(year, book),
        "play_call_stats.md": play_calls_markdown(year, team, book),
        "team_stats.md": team_stats_markdown(year, book),
        "calibration_audit.md": calibration_audit_markdown(year, receipts, book),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("year", type=int)
    parser.add_argument("--team", required=True, help="Exact team_id used by game receipts")
    args = parser.parse_args()

    stats_dir = ROOT / "career" / str(args.year) / "stats"
    receipts = load_receipts(stats_dir / "game_receipts")
    stats_dir.mkdir(parents=True, exist_ok=True)
    for name, text in render_views(args.year, args.team, receipts).items():
        (stats_dir / name).write_text(text, encoding="utf-8")
    print("rendered %d stat views from %d receipts" % (8, len(receipts)))


if __name__ == "__main__":
    main()
