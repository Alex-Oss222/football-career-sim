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


# Readable stat views follow the standard NFL statbook layout: every player
# is filed under his roster position group, and each group shows only the
# columns that position is measured by (NFL.com / Pro-Football-Reference
# categories). Derived columns (Cmp%, Y/A, passer rating, FG%) are computed
# from stored counters only; nothing is estimated.

def g(line, field):
    return line.get(field, 0) or 0


def pct(made, attempts):
    return "%.1f" % (100.0 * made / attempts) if attempts else "—"


def thrown(line):
    return line.get("interceptions_thrown", g(line, "interceptions"))


def passer_rating(line):
    """Official NFL passer rating from completions, attempts, yards, TD, INT."""
    att = g(line, "pass_attempts")
    if not att:
        return "—"
    clamp = lambda v: max(0.0, min(2.375, v))
    a = clamp((g(line, "completions") / att - 0.3) * 5)
    b = clamp((g(line, "passing_yards") / att - 3) * 0.25)
    c = clamp(g(line, "passing_touchdowns") / att * 20)
    d = clamp(2.375 - thrown(line) / att * 25)
    return "%.1f" % ((a + b + c + d) / 6 * 100)


def col(header, field):
    return (header, lambda l: g(l, field), (field,))


PASSING_COLS = (
    col("Cmp", "completions"), col("Att", "pass_attempts"),
    ("Cmp%", lambda l: pct(g(l, "completions"), g(l, "pass_attempts")), ()),
    col("Yds", "passing_yards"),
    ("Y/A", lambda l: avg(g(l, "passing_yards"), g(l, "pass_attempts")), ()),
    col("TD", "passing_touchdowns"),
    ("Int", thrown, ("interceptions_thrown", "interceptions")),
    ("Rate", passer_rating, ()),
    col("Sk", "sacks_taken"), col("SkYds", "sack_yards"),
)
RUSHING_COLS = (
    col("Car", "rushing_attempts"), col("Yds", "rushing_yards"),
    ("Y/C", lambda l: avg(g(l, "rushing_yards"), g(l, "rushing_attempts")), ()),
    col("TD", "rushing_touchdowns"), col("Lng", "long_rush"),
)
RECEIVING_COLS = (
    col("Tgt", "targets"), col("Rec", "receptions"), col("Yds", "receiving_yards"),
    ("Y/R", lambda l: avg(g(l, "receiving_yards"), g(l, "receptions")), ()),
    col("TD", "receiving_touchdowns"), col("Lng", "long_reception"),
)
FUMBLE_COLS = (col("Fmb", "fumbles"), col("FL", "fumbles_lost"))
QB_COLS = PASSING_COLS + (
    col("Rush", "rushing_attempts"), col("RushYds", "rushing_yards"),
    col("RushTD", "rushing_touchdowns"),
) + FUMBLE_COLS
RB_COLS = RUSHING_COLS + (
    col("Tgt", "targets"), col("Rec", "receptions"), col("RecYds", "receiving_yards"),
    col("RecTD", "receiving_touchdowns"),
) + FUMBLE_COLS
REC_COLS = RECEIVING_COLS + (
    col("Car", "rushing_attempts"), col("RushYds", "rushing_yards"),
    col("RushTD", "rushing_touchdowns"),
) + FUMBLE_COLS
OL_COLS = (col("Sacks allowed", "sacks_allowed"),)
FRONT_COLS = (
    col("Tkl", "tackles"), col("Solo", "solo_tackles"), col("Ast", "assisted_tackles"),
    col("TFL", "tackles_for_loss"), col("Sack", "sacks"), col("Press", "pressures"),
    col("PD", "passes_defended"), col("Int", "defensive_interceptions"),
    col("FF", "forced_fumbles"), col("FR", "fumble_recoveries"),
)
DB_COLS = (
    col("Tkl", "tackles"), col("Solo", "solo_tackles"), col("Ast", "assisted_tackles"),
    col("TFL", "tackles_for_loss"), col("Int", "defensive_interceptions"),
    col("IntYds", "interception_return_yards"), col("PD", "passes_defended"),
    col("Sack", "sacks"), col("Press", "pressures"),
    col("FF", "forced_fumbles"), col("FR", "fumble_recoveries"),
)
KICKING_COLS = (
    col("FGM", "field_goals_made"), col("FGA", "field_goals_attempted"),
    ("FG%", lambda l: pct(g(l, "field_goals_made"), g(l, "field_goals_attempted")), ()),
    col("XPM", "extra_points_made"), col("XPA", "extra_points_attempted"),
    ("Pts", lambda l: 3 * g(l, "field_goals_made") + g(l, "extra_points_made"), ()),
)
PUNTING_COLS = (
    col("Punts", "punts"), col("Yds", "punt_yards"),
    ("Avg", lambda l: avg(g(l, "punt_yards"), g(l, "punts")), ()),
    col("Lng", "long_punt"), col("In20", "punts_inside_20"), col("TB", "punt_touchbacks"),
)
RETURN_COLS = (
    col("KR", "kick_returns"), col("KRYds", "kick_return_yards"),
    ("KR Avg", lambda l: avg(g(l, "kick_return_yards"), g(l, "kick_returns")), ()),
    col("PR", "punt_returns"), col("PRYds", "punt_return_yards"),
    ("PR Avg", lambda l: avg(g(l, "punt_return_yards"), g(l, "punt_returns")), ()),
)
RETURN_FIELDS = {"kick_returns", "kick_return_yards", "punt_returns", "punt_return_yards", "return_yards"}
# Mechanically implied by columns already shown (dropbacks = attempts + sacks).
IMPLIED_FIELDS = {"dropbacks", "return_yards"}

POSITION_GROUPS = (
    ("Quarterbacks", {"QB"}, QB_COLS, "passing_yards"),
    ("Running backs", {"RB", "HB", "FB"}, RB_COLS, "rushing_yards"),
    ("Wide receivers", {"WR"}, REC_COLS, "receiving_yards"),
    ("Tight ends", {"TE"}, REC_COLS, "receiving_yards"),
    ("Offensive line", {"OT", "OG", "C", "T", "G", "OL", "LT", "LG", "RG", "RT"}, OL_COLS, "sacks_allowed"),
    ("Defensive line", {"DE", "DT", "NT", "DL"}, FRONT_COLS, "tackles"),
    ("Linebackers", {"OLB", "ILB", "MLB", "LB"}, FRONT_COLS, "tackles"),
    ("Defensive backs", {"CB", "S", "FS", "SS", "DB"}, DB_COLS, "tackles"),
    ("Kickers", {"K", "PK"}, KICKING_COLS, "field_goals_made"),
    ("Punters", {"P"}, PUNTING_COLS, "punt_yards"),
)

LABELS = {
    "dropbacks": "DB", "pass_attempts": "PassAtt", "completions": "Cmp",
    "passing_yards": "PassYds", "passing_touchdowns": "PassTD",
    "interceptions_thrown": "IntThrown", "interceptions": "IntThrown",
    "sacks_taken": "SkTaken", "sack_yards": "SkYds",
    "rushing_attempts": "Car", "rushing_yards": "RushYds",
    "rushing_touchdowns": "RushTD", "long_rush": "RushLng", "targets": "Tgt",
    "receptions": "Rec", "receiving_yards": "RecYds",
    "receiving_touchdowns": "RecTD", "long_reception": "RecLng",
    "fumbles": "Fmb", "fumbles_lost": "FL", "sacks_allowed": "SkAllowed",
    "tackles": "Tkl", "solo_tackles": "Solo", "assisted_tackles": "Ast",
    "tackles_for_loss": "TFL", "sacks": "Sack", "pressures": "Press",
    "passes_defended": "PD", "defensive_interceptions": "Int",
    "interception_return_yards": "IntYds", "forced_fumbles": "FF",
    "fumble_recoveries": "FR", "field_goals_made": "FGM",
    "field_goals_attempted": "FGA", "extra_points_made": "XPM",
    "extra_points_attempted": "XPA", "punts": "Punts", "punt_yards": "PuntYds",
    "long_punt": "PuntLng", "punts_inside_20": "In20", "punt_touchbacks": "TB",
}


def numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def position_group(position):
    for index, (_, positions, _, _) in enumerate(POSITION_GROUPS):
        if position in positions:
            return index
    return None


def covered(columns):
    return {field for _, _, fields in columns for field in fields}


def player_rows(players, fields, sort_field):
    rows = []
    for player_id, line in players.items():
        if str(player_id).startswith("__"):
            continue
        if not any(g(line, field) for field in fields):
            continue
        rows.append((player_id, line))
    rows.sort(key=lambda item: (-g(item[1], sort_field), ", ".join(item[1].get("teams", ())), item[0]))
    return rows


def table(title, rows, columns, *, with_team, with_pos=False):
    lead = ["Player"] + (["Team"] if with_team else []) + (["Pos"] if with_pos else [])
    headers = lead + [header for header, _, _ in columns]
    lines = ["## " + title, "",
             "| " + " | ".join(headers) + " |",
             "|" + "---|" * len(lead) + "---:|" * len(columns)]
    for player_id, line in rows:
        cells = [player_id]
        if with_team:
            cells.append(", ".join(line.get("teams", ())))
        if with_pos:
            cells.append(line.get("position", ""))
        cells += [str(fn(line)) for _, fn, _ in columns]
        lines.append("| " + " | ".join(cells) + " |")
    if not rows:
        lines.append("| — |" + " |" * (len(headers) - 1))
    lines.append("")
    return lines


def position_sections(players, *, with_team):
    """Position-group tables, a returns table, and a residual table for any
    stored counter that falls outside the player's position columns, so the
    readable view never silently drops a generated statistic."""
    grouped = {index: [] for index in range(len(POSITION_GROUPS))}
    other = []
    residuals = []
    for player_id, line in players.items():
        if str(player_id).startswith("__"):
            continue
        nonzero = {f for f, v in line.items() if f not in {"position", "teams"} and numeric(v) and v}
        if not nonzero:
            continue
        index = position_group(line.get("position", ""))
        shown = RETURN_FIELDS | IMPLIED_FIELDS
        if index is not None:
            shown |= covered(POSITION_GROUPS[index][2])
            if nonzero - RETURN_FIELDS - IMPLIED_FIELDS:
                grouped[index].append((player_id, line))
        extra = sorted(nonzero - shown, key=lambda f: list(LABELS).index(f) if f in LABELS else 999)
        if extra:
            (other if index is None else residuals).append((player_id, line, extra))

    lines = []
    for index, (title, _, columns, sort_field) in enumerate(POSITION_GROUPS):
        rows = grouped[index]
        rows.sort(key=lambda item: (-g(item[1], sort_field), ", ".join(item[1].get("teams", ())), item[0]))
        lines += table(title, rows, columns, with_team=with_team)

    lines += table("Kick and punt returns", player_rows(
        players, ("kick_returns", "punt_returns"), "return_yards"),
        RETURN_COLS, with_team=with_team, with_pos=True)

    extra_rows = sorted(other + residuals, key=lambda item: (
        ", ".join(item[1].get("teams", ())), item[1].get("position", ""), item[0]))
    lines += ["## Other statistics outside the player's position table", "",
              "Special-teams tackles, trick plays and players at positions without "
              "a dedicated table. Listed so no stored counter is omitted.", "",
              "| Player | " + ("Team | " if with_team else "") + "Pos | Statistics |",
              "|---|" + ("---|" if with_team else "") + "---|---|"]
    for player_id, line, extra in extra_rows:
        stats = ", ".join("%s %s" % (LABELS.get(f, f), g(line, f)) for f in extra)
        lines.append("| %s | %s%s | %s |" % (
            player_id, (", ".join(line.get("teams", ())) + " | ") if with_team else "",
            line.get("position", ""), stats))
    if not extra_rows:
        lines.append("| — |" + (" |" if with_team else "") + " | |")
    lines.append("")
    return lines


def team_markdown(year, team_id, book):
    team = book["teams"].get(team_id)
    lines = [
        "# %s %s player statistics" % (year, team_id),
        "",
        "**Version:** `%s-W%02d-TEAM-STATS-3`" % (year, book["through_week"]),
        through_line(book),
        coverage_line(book, team_id),
        "",
        "Organized by position group. Each table shows the standard statistics "
        "for that position; returns and cross-position counters follow.",
        "",
    ]
    if not team:
        lines += ["No stored receipt currently matches this team identifier.", ""]
        return "\n".join(lines)
    return "\n".join(lines + position_sections(team["players"], with_team=False))


LEAGUE_CATEGORIES = (
    ("Passing", ("pass_attempts",), "passing_yards", PASSING_COLS),
    ("Rushing", ("rushing_attempts",), "rushing_yards", RUSHING_COLS + FUMBLE_COLS),
    ("Receiving", ("targets", "receptions"), "receiving_yards", RECEIVING_COLS),
    ("Defense", ("tackles", "sacks", "defensive_interceptions", "passes_defended",
                 "forced_fumbles", "fumble_recoveries"), "tackles", DB_COLS),
    ("Kicking", ("field_goals_attempted", "extra_points_attempted"), "field_goals_made", KICKING_COLS),
    ("Punting", ("punts",), "punt_yards", PUNTING_COLS),
    ("Kick and punt returns", ("kick_returns", "punt_returns"), "return_yards", RETURN_COLS),
)


def league_markdown(year, book):
    lines = [
        "# %s NFL player statistics" % year,
        "",
        "**Version:** `%s-W%02d-LEAGUE-PLAYER-STATS-4`" % (year, book["through_week"]),
        through_line(book),
        coverage_line(book),
        "",
        "League-wide statistical categories in the NFL.com order. Each table "
        "lists every player with an opportunity in that category, with position.",
        "",
    ]
    for title, fields, sort_field, columns in LEAGUE_CATEGORIES:
        lines += table(title, player_rows(book["players"], fields, sort_field),
                       columns, with_team=True, with_pos=True)
    return "\n".join(lines)


def all_players_markdown(year, book):
    lines = [
        "# %s NFL all-player stat ledger" % year, "",
        "**Version:** `%s-W%02d-ALL-PLAYER-STATS-3`" % (year, book["through_week"]),
        through_line(book),
        coverage_line(book), "",
        "Every player with a nonzero stored statistic, filed by position group. "
        "Each position table carries the standard columns for that position "
        "(quarterbacks: passing plus rushing; backs: rushing plus receiving; "
        "receivers and tight ends: receiving plus rushing; defenders: tackles, "
        "sacks, takeaways; specialists: kicking or punting). Returns and any "
        "counter outside a player's position table are listed after. Zero-only "
        "players are omitted; absence does not prove non-participation.", "",
    ]
    return "\n".join(lines + position_sections(book.get("players", {}), with_team=True))

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
        "**Version:** `%s-W%02d-LEADERS-4`" % (year, book["through_week"]),
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
        lines += ["## " + title, "", "| Rank | Player | Team | Pos | Total |", "|---:|---|---|---|---:|"]
        for rank, row in enumerate(leaders(book, field), 1):
            lines.append("| %d | %s | %s | %s | %s |" % (
                rank, row["player_id"], ", ".join(row["teams"]), row["position"], row["value"]))
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
