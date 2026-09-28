#!/usr/bin/env python3
"""Head-coach change base rates from real 1999-2012 seasons (pre-branch data).

  python scripts/research/build_hc_change_base_rates.py GAMES_CSV

GAMES_CSV is nfldata's games.csv (https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv).
For each club-season from 2002 to 2012 (1999-2001 are read only to count
tenure back, so every tenure and "recent" flag is complete), the coach who
opened the season "changed" if a different head coach opened the club's next
season: a firing during or after the season, a resignation or a retirement
alike. New Orleans 2011-2012 is the one exception: Sean Payton's 2012 league
suspension is not a change (2011 counts as kept, and the 2012 stand-in season
is left out). Rates
are tabulated by the season's wins (ties count half) and the coach's tenure
with the club, with playoff seasons pooled by tenure, and smoothed toward the
overall rate with a Beta prior of weight 5. A non-playoff season of a coach past
his first season is split again by whether the club reached the playoffs in
either of the two prior seasons ("recent"), smoothed toward its parent cell.
No season after 2012 is read.
"""
import collections
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "library/data/2012_hc_change_base_rates.json"
ALIAS = {"STL": "LA", "SD": "LAC", "OAK": "LV", "JAC": "JAX"}
PRIOR_WEIGHT = 5
FIRST_COUNTED = 2002


def wins_bucket(w):
    return "0-4" if w <= 4.5 else "5-6" if w <= 6.5 else "7-8" if w <= 8.5 else "9-10" if w <= 10.5 else "11+"


def tenure_bucket(t):
    return "1st season" if t == 1 else "2nd-3rd" if t <= 3 else "4th+"


def main():
    path = Path(sys.argv[1])
    games = collections.defaultdict(list)
    for r in csv.DictReader(path.open()):
        if not r["season"].isdigit() or not 1999 <= int(r["season"]) <= 2013:
            continue
        s = int(r["season"])
        for side, other in (("home", "away"), ("away", "home")):
            games[(ALIAS.get(r[side + "_team"], r[side + "_team"]), s)].append(
                (r["game_type"], int(r["week"]), r[side + "_coach"], r[side + "_score"], r[other + "_score"]))

    def regular(key):
        return sorted((g for g in games[key] if g[0] == "REG"), key=lambda g: g[1])

    def playoffs(team, s):
        return any(g[0] != "REG" for g in games.get((team, s), ()))

    seasons = []
    for (team, s) in sorted(games):
        if s > 2012:
            continue
        reg = regular((team, s))
        nxt = (team, s + 1)
        if not reg or nxt not in games:
            continue
        if s < FIRST_COUNTED:
            continue
        if (team, s) == ("NO", 2012):
            continue  # the suspension stand-in season (see the docstring)
        start = reg[0][2]
        wins = sum(1 for g in reg if int(g[3]) > int(g[4])) + 0.5 * sum(1 for g in reg if int(g[3]) == int(g[4]))
        tenure, k = 1, s - 1
        while (team, k) in games and regular((team, k))[0][2] == start:
            tenure, k = tenure + 1, k - 1
        changed = regular(nxt)[0][2] != start and (team, s) != ("NO", 2011)
        seasons.append({"team": team, "season": s, "coach": start, "wins": wins, "tenure": tenure,
                        "playoffs": any(g[0] != "REG" for g in games[(team, s)]),
                        "recent": playoffs(team, s - 1) or playoffs(team, s - 2),
                        "changed": changed})
    overall = sum(x["changed"] for x in seasons) / len(seasons)
    cells = collections.defaultdict(lambda: [0, 0])
    splits = collections.defaultdict(lambda: [0, 0])
    for x in seasons:
        key = "playoffs|" + tenure_bucket(x["tenure"]) if x["playoffs"] else wins_bucket(x["wins"]) + "|" + tenure_bucket(x["tenure"])
        cells[key][0] += x["changed"]
        cells[key][1] += 1
        if not x["playoffs"] and x["tenure"] > 1:
            sub = key + "|" + ("recent playoffs" if x["recent"] else "no recent playoffs")
            splits[sub][0] += x["changed"]
            splits[sub][1] += 1
    table = {k: {"changed": c, "seasons": n, "raw_rate": round(c / n, 4),
                 "rate": round((c + PRIOR_WEIGHT * overall) / (n + PRIOR_WEIGHT), 4)} for k, (c, n) in sorted(cells.items())}
    for k, (c, n) in sorted(splits.items()):
        parent = table[k.rsplit("|", 1)[0]]["rate"]
        table[k] = {"changed": c, "seasons": n, "raw_rate": round(c / n, 4),
                    "rate": round((c + PRIOR_WEIGHT * parent) / (n + PRIOR_WEIGHT), 4), "smoothed_toward": "parent cell"}
    # 2013 opening-day head coach and his tenure with the club (2013 counted).
    back = {"LA": "STL", "LAC": "SD", "LV": "OAK"}
    tenure_2013 = {}
    for (team, s) in sorted(games):
        if s != 2013:
            continue
        coach, tenure, k = regular((team, 2013))[0][2], 1, 2012
        while (team, k) in games and regular((team, k))[0][2] == coach:
            tenure, k = tenure + 1, k - 1
        tenure_2013[back.get(team, team)] = {"coach": coach, "tenure": tenure,
                                             "playoffs_2011_or_2012": playoffs(team, 2011) or playoffs(team, 2012)}
    OUT.write_text(json.dumps({
        "schema_version": "hc-change-base-rates-v1",
        "source": {"file": "nfldata games.csv", "url": "https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv",
                   "sha256": hashlib.sha256(path.read_bytes()).hexdigest()},
        "window": "club-seasons 2002-2012 keyed to the coach who opened the season (1999-2001 read only to count tenure back); outcome read from the 2003-2013 opening games; New Orleans 2012 left out and 2011 counted as kept (Payton's suspension)",
        "definition": "changed = a different head coach opened the club's next regular season (a firing during or after the season, a resignation or a retirement alike)",
        "buckets": {"wins": "ties count half; 0-4 (<=4.5), 5-6 (<=6.5), 7-8 (<=8.5), 9-10 (<=10.5), 11+", "tenure": "consecutive seasons the coach opened for the club, this season included, counted back to 1999", "playoffs": "any postseason game that season; pooled by tenure"},
        "smoothing": "rate = (changed + %d * overall) / (seasons + %d)" % (PRIOR_WEIGHT, PRIOR_WEIGHT),
        "overall_rate": round(overall, 4), "club_seasons": len(seasons), "cells": table,
        "tenure_2013": tenure_2013,
        "tenure_note": "2013 opening-day head coach (the 2013 Week 1 row, a pre-season fact) and consecutive seasons he started for the club through 2013; a season the coach missed breaks the count (see the carousel method for overrides)."}, indent=1) + "\n")
    print("club-seasons %d, overall %.3f" % (len(seasons), overall))
    for k, v in table.items():
        print(k, v)


if __name__ == "__main__":
    main()
