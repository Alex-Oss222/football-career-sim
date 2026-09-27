#!/usr/bin/env python3
"""Build the 2013 regular-season schedule rails from nflverse games.csv.

Research tool only. Fetch the input first:
  https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv

Usage:
  python scripts/research/build_2013_schedule.py games.csv > library/data/2013_schedule.json

Only schedule columns are read (week, date, weekday, kickoff, clubs, site,
stadium). Scores, results, betting lines, quarterbacks, coaches, officials
and weather are never read.
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.research.build_2013_week1_depth_charts import CLUBS  # noqa: E402

CLUBS = {**CLUBS, "JAX": "Jacksonville Jaguars"}
SCHEDULE_COLUMNS = ("week", "gameday", "weekday", "gametime", "away_team", "home_team", "location", "stadium")


def build(path):
    games = []
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["season"] != "2013" or row["game_type"] != "REG":
                continue
            r = {k: row[k] for k in SCHEDULE_COLUMNS}
            games.append({
                "week": int(r["week"]), "date": r["gameday"], "weekday": r["weekday"],
                "kickoff_et": r["gametime"], "away": CLUBS[r["away_team"]], "home": CLUBS[r["home_team"]],
                "site": "neutral" if r["location"] == "Neutral" else "home", "stadium": r["stadium"],
            })
    games.sort(key=lambda g: (g["week"], g["date"], g["kickoff_et"], g["away"]))
    return games


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    games = build(sys.argv[1])
    lines = ["{", '  "season": 2013,', '  "source": "nflverse games.csv, schedule columns only",', '  "games": [']
    lines += ["    %s%s" % (json.dumps(g), "," if i < len(games) - 1 else "") for i, g in enumerate(games)]
    lines += ["  ]", "}"]
    sys.stdout.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
