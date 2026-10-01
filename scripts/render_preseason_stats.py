#!/usr/bin/env python3
"""Render the preseason stat views from the preseason receipts only.

  python scripts/render_preseason_stats.py --season YEAR

Reads career/YEAR/04_Training_Camp_and_Preseason/Preseason_Games/statistics/records/game_receipts/ and
writes `preseason_totals.json` and `preseason_stats.md` beside it under
04_Training_Camp_and_Preseason/Preseason_Games/statistics/. Preseason statistics are aggregated with the
same runtime.statbook code as the regular season but never join the
regular-season statbook, standings, awards or draft order, and no league
ranking is drawn from them. Nothing is typed by hand: every number comes
from a closed-game receipt.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.rules import PRESEASON
from runtime.seasons import SeasonPaths, require_receipt_season
from runtime.stat_tables import pct, position_sections, time_text
from runtime.statbook import aggregate_receipts

PROTAGONIST = "Jacksonville Jaguars"
VIEW_FILES = ("preseason_totals.json", "preseason_stats.md")


def load_receipts(directory):
    receipts = []
    if directory.exists():
        for path in sorted(directory.glob("*.json")):
            receipts.append(json.loads(path.read_text(encoding="utf-8")))
    return receipts


def require_preseason(receipts, year):
    require_receipt_season(receipts, year)
    for receipt in receipts:
        if receipt.get("game_type") != PRESEASON or "-preseason-" not in str(receipt.get("event_id")):
            raise ValueError("not a preseason receipt: %s" % receipt.get("event_id"))


def games_table(receipts):
    lines = ["## Games", "", "| Game | Date | Matchup | Final | Try rule |", "|---:|---|---|---|---|"]
    for r in sorted(receipts, key=lambda r: int(r.get("preseason_game", r["week"]))):
        score = r["final_score"]
        final = "%s %d, %s %d" % (r["away"], score[r["away"]], r["home"], score[r["home"]])
        rule = r.get("extra_point_rule") or {}
        try_text = ("snapped from the %d (%d-yard kick)" % (rule["snap_yard_line"], rule["distance"])
                    if rule.get("distance") else "ordinary try")
        lines.append("| %d | %s | %s | %s | %s |" % (int(r.get("preseason_game", r["week"])), r.get("date", "—"),
                                                     r["matchup"], final, try_text))
    return lines + [""]


def team_table(book):
    lines = ["## Team totals", "", "Per club across its closed preseason games; opponents' totals are the games against Jacksonville only.", "",
             "| Club | G | Pts | Pts allowed | Pass yds | Rush yds | 1st downs | 3rd down | TO | Sacks allowed | Pen-yds | TOP |",
             "|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|---|"]
    order = sorted(book["teams"], key=lambda t: (t != PROTAGONIST, t))
    for team in order:
        data = book["teams"][team]
        t, o = data["team_stats"], data["opponent_stats"]
        lines.append("| %s | %d | %d | %d | %d | %d | %d | %d/%d (%s%%) | %d | %d | %d-%d | %s |" % (
            team, data["games"], t.get("points", 0), o.get("points", 0), t.get("passing_yards", 0),
            t.get("rushing_yards", 0), t.get("first_downs", 0), t.get("third_down_conversions", 0),
            t.get("third_down_attempts", 0), pct(t.get("third_down_conversions", 0), t.get("third_down_attempts", 0)),
            t.get("turnovers", 0), t.get("sacks_allowed", 0), t.get("penalties", 0), t.get("penalty_yards", 0),
            time_text(t.get("time_of_possession", 0))))
    return lines + [""]


def stats_markdown(year, receipts, book):
    lines = ["# %d preseason statistics" % year, "",
             "**Scope:** PRESEASON ONLY. Generated from the %d preseason receipts under "
             "`statistics/records/game_receipts/`; these totals never enter the regular-season "
             "statbook, standings, awards or draft order, and no league ranking is drawn from them." % year,
             "**Through:** %s." % ("no preseason game has closed" if not receipts
                                   else "preseason game %d" % book["through_week"]), ""]
    if not receipts:
        return "\n".join(lines + ["No preseason game has closed.", ""])
    lines += games_table(receipts) + team_table(book)
    jax = book["teams"].get(PROTAGONIST)
    if jax:
        lines += ["## Jacksonville players (preseason)", "",
                  "By position, then player. G counts preseason games on the game-day unit.", ""]
        lines += position_sections(jax["players"], with_team=False, level="###")
    others = {p: line for p, line in book.get("players", {}).items() if PROTAGONIST not in line.get("teams", [])}
    if others:
        lines += ["## Opponent players (preseason, games against Jacksonville only)", ""]
        lines += position_sections(others, with_team=True, level="###")
    return "\n".join(lines).rstrip("\n") + "\n"


def render_views(year, receipts):
    require_preseason(receipts, year)
    book = aggregate_receipts(receipts)
    totals = {"scope": "preseason_only", "season": year, "through_game": book["through_week"],
              "receipt_count": book["receipt_count"],
              "teams": {t: {k: d[k] for k in ("games", "plays", "opponent_plays", "team_stats", "opponent_stats")}
                        for t, d in sorted(book["teams"].items())}}
    return {"preseason_totals.json": json.dumps(totals, sort_keys=True, separators=(",", ":")) + "\n",
            "preseason_stats.md": stats_markdown(year, receipts, book)}


def write_views(paths):
    receipts = load_receipts(paths.preseason_receipts)
    views = render_views(paths.year, receipts)
    folder = paths.preseason_games_dir / "statistics"
    folder.mkdir(parents=True, exist_ok=True)
    for name, text in views.items():
        (folder / name).write_text(text, encoding="utf-8")
    return views


def stale_views(paths):
    """Names of preseason views missing or differing from the receipts (empty when no receipt exists)."""
    receipts = load_receipts(paths.preseason_receipts)
    if not receipts:
        return []
    folder = paths.preseason_games_dir / "statistics"
    return [name for name, text in render_views(paths.year, receipts).items()
            if not (folder / name).is_file() or (folder / name).read_text(encoding="utf-8") != text]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--season", type=int, required=True)
    args = parser.parse_args()
    paths = SeasonPaths(args.season, ROOT)
    views = write_views(paths)
    print("rendered %d preseason stat views from %d receipts" % (len(views), len(load_receipts(paths.preseason_receipts))))


if __name__ == "__main__":
    main()
