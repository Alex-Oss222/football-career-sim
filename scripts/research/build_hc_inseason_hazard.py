#!/usr/bin/env python3
"""In-season head-coach change rates per game from real 2002-2012 regular seasons (pass 1).

  python scripts/research/build_hc_inseason_hazard.py            # fetch the pinned file, write the table
  python scripts/research/build_hc_inseason_hazard.py --file GAMES_CSV
  python scripts/research/build_hc_inseason_hazard.py --check    # rebuild in memory, compare, write nothing

Input: nfldata's ``data/games.csv`` at commit 04a6ffcc (SOURCE), the file the
January 2014 base-rate builder (scripts/research/build_hc_change_base_rates.py)
read: its recorded sha256 is ``c14c7de2...``. That builder took a local file
and recorded nfldata's moving master URL; the commit was found on October 23,
2026 by hashing ``data/games.csv`` at the nfldata commits that changed it before
that builder was committed, newest first. By default the builder fetches the
commit-pinned URL;
with ``--file`` it reads a local copy. Either way it refuses bytes whose sha256
is not the recorded one.

The event (library/2014_inseason_head_coach_changes.md): the coach who coached
a club's game k does not coach game k+1 or any later regular-season game that
season. An interim who finishes the season counts; a stand-in for a coach who
returns does not (the coach who opened the season coached a later game);
Indianapolis 2012 names one coach for every game in this file, so it shows no
stand-in at all. New Orleans 2012 is left out, as in the January data (Sean
Payton's suspension season). Each club-season of 2002 to 2012 is at risk after
each of its games 1 to 15 (game 16 has no later regular-season game), up to and
including its first change: a club is not at risk again that season, as the
weekly check never draws a club again after its change. Seasons 1999 to 2001
are read only to count a coach's seasons with the club back; no row after 2012
is read.

Cells: the club's losses minus wins after game k (ties count neither: 0 or
fewer, 1 to 2, 3 to 4, 5 or more) by the coach's season with the club (his
first season, or a later one: consecutive seasons he opened for the club,
counted as the January builder counts them). Each cell is smoothed toward the
overall per-game rate with a prior weight of 75 club-games (the January
table's prior of five club-seasons at fifteen at-risk games a season). A cell
with fewer at-risk club-games than the prior weight would be merged into the
cell of the next band toward 0 or fewer with the same tenure, with the reason
recorded; none is that small, so none is merged. The cells and the smoothing
are the career's labelled modelling choice, like the January factors.

For step 6's season-end draw only, the builder also writes the January table
conditional on no in-season change: each committed January cell
(library/data/2012_hc_change_base_rates.json, read from the same file, its
digest checked) with the club-seasons that had an in-season change taken out
of its counts (each was a "changed" club-season there; the pass-2 verifier
checks every one), smoothed as the January builder smooths (prior weight 5
toward the overall conditional rate; a split cell toward its parent cell), so
the season-end draw does not count an in-season change twice.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "library/data/2012_hc_inseason_hazard.json"
JANUARY = ROOT / "library/data/2012_hc_change_base_rates.json"
SOURCE = {
    "repository": "nflverse/nfldata",
    "file": "data/games.csv",
    "commit": "04a6ffcccc8a58451f45cd282c0f14766aaa3479",
    "committed": "2026-09-28T19:45:13+00:00",
    "url": "https://raw.githubusercontent.com/nflverse/nfldata/04a6ffcccc8a58451f45cd282c0f14766aaa3479/data/games.csv",
    "sha256": "c14c7de28c9eb7027699b9b316f7276ea03e34a077c8ae65010f15a44a6780d1",
    "january_url": "https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv",
    "found": ("The January 2014 base-rate builder recorded this sha256 and nfldata's moving master URL, with no "
              "copy in the repository. On October 23, 2026 the nfldata commits that changed data/games.csv from "
              "September 21 to 29, 2026 were listed, and the file was hashed at those before the January builder "
              "was committed (September 28, 2026, 20:26:45 UTC), newest first: the second, commit 04a6ffcc "
              "(19:45:13 UTC, current until the next change at 20:15:15 UTC), has the recorded digest, and the "
              "commit-pinned URL returns the same bytes."),
}
ALIAS = {"STL": "LA", "SD": "LAC", "OAK": "LV", "JAC": "JAX"}
FIRST, LAST, TENURE_FROM = 2002, 2012, 1999
LEFT_OUT = {("NO", 2012)}
PRIOR_WEIGHT = 75
JANUARY_PRIOR = 5
BANDS = ("0 or fewer", "1 to 2", "3 to 4", "5 or more")
TENURES = ("first season", "later season")


def band(margin):
    """The losses-minus-wins band of a record."""
    return BANDS[0] if margin <= 0 else BANDS[1] if margin <= 2 else BANDS[2] if margin <= 4 else BANDS[3]


def tenure_band(seasons):
    return TENURES[0] if seasons == 1 else TENURES[1]


def cell_key(margin, seasons):
    return band(margin) + "|" + tenure_band(seasons)


def read_source(path=None):
    """The source bytes, from ``path`` or the commit-pinned URL; refused unless the digest matches."""
    if path is None:
        with urlopen(SOURCE["url"], timeout=120) as response:
            data = response.read()
    else:
        data = Path(path).read_bytes()
    found = hashlib.sha256(data).hexdigest()
    if found != SOURCE["sha256"]:
        raise ValueError("games.csv digest %s is not the recorded %s; refused" % (found, SOURCE["sha256"]))
    return data


def club_games(data):
    """{(club, season): [game rows]} for 1999 to 2012, every game type, each row
    (game_type, week, coach, points for, points against); rows after 2012 are never kept."""
    games = collections.defaultdict(list)
    for r in csv.DictReader(io.StringIO(data.decode("utf-8"))):
        if not r["season"].isdigit():
            continue
        season = int(r["season"])
        if not TENURE_FROM <= season <= LAST:
            continue
        for side, other in (("home", "away"), ("away", "home")):
            club = ALIAS.get(r[side + "_team"], r[side + "_team"])
            games[(club, season)].append((r["game_type"], int(r["week"]), r[side + "_coach"],
                                          int(r[side + "_score"]), int(r[other + "_score"])))
    return games


def regular(games, key):
    return sorted((g for g in games.get(key, ()) if g[0] == "REG"), key=lambda g: g[1])


def seasons_with_club(games, club, season):
    """Consecutive seasons the coach who opened ``season`` opened for the club, this one counted."""
    opener = regular(games, (club, season))[0][2]
    count, back = 1, season - 1
    while (club, back) in games and regular(games, (club, back)) and regular(games, (club, back))[0][2] == opener:
        count, back = count + 1, back - 1
    return count


def hazard(games):
    """(cells {key: [changes, club-games]}, changes [..], club-seasons) over 2002 to 2012."""
    if any(season > LAST for _, season in games):
        raise ValueError("an outcome row after %d was passed to the builder; refused" % LAST)
    cells = {"%s|%s" % (b, t): [0, 0] for b in BANDS for t in TENURES}
    changes, counted = [], 0
    for club, season in sorted(games):
        if season < FIRST or (club, season) in LEFT_OUT:
            continue
        reg = regular(games, (club, season))
        if not reg:
            continue
        counted += 1
        opener = reg[0][2]
        seasons = seasons_with_club(games, club, season)
        last = max(i for i, g in enumerate(reg, 1) if g[2] == opener)
        wins = losses = ties = 0
        for k in range(1, len(reg)):
            g = reg[k - 1]
            wins += g[3] > g[4]
            losses += g[3] < g[4]
            ties += g[3] == g[4]
            key = cell_key(losses - wins, seasons)
            cells[key][1] += 1
            if k == last:
                cells[key][0] += 1
                changes.append({"club": club, "season": season, "game": k, "week": g[1], "coach": opener,
                                "successor": reg[k][2], "wins": wins, "losses": losses, "ties": ties,
                                "seasons_with_club": seasons, "cell": key})
                break
    return cells, changes, counted


def january_cell(games, club, season):
    """The January table's cell key of a club-season (the January builder's definitions)."""
    reg = regular(games, (club, season))
    wins = sum(1 for g in reg if g[3] > g[4]) + 0.5 * sum(1 for g in reg if g[3] == g[4])
    seasons = seasons_with_club(games, club, season)
    tb = "1st season" if seasons == 1 else "2nd-3rd" if seasons <= 3 else "4th+"
    playoffs = lambda s: any(g[0] != "REG" for g in games.get((club, s), ()))
    if playoffs(season):
        return ["playoffs|" + tb]
    wb = "0-4" if wins <= 4.5 else "5-6" if wins <= 6.5 else "7-8" if wins <= 8.5 else "9-10" if wins <= 10.5 else "11+"
    keys = [wb + "|" + tb]
    if seasons > 1:
        keys.append(keys[0] + "|" + ("recent playoffs" if playoffs(season - 1) or playoffs(season - 2)
                                     else "no recent playoffs"))
    return keys


def conditional(games, changes, january):
    """The January cells with the in-season changes taken out (for step 6's season-end draw)."""
    if january["source"]["sha256"] != SOURCE["sha256"]:
        raise ValueError("the January table was not read from the same games.csv")
    removed = collections.Counter()
    for c in changes:
        for key in january_cell(games, c["club"], c["season"]):
            removed[key] += 1
    # The cells without a split partition the club-seasons, so their counts sum to the table's totals.
    base = [row for row in january["cells"].values() if not row.get("smoothed_toward")]
    if sum(row["seasons"] for row in base) != january["club_seasons"]:
        raise ValueError("the January cells do not partition its club-seasons")
    total = january["club_seasons"] - len(changes)
    changed = sum(row["changed"] for row in base) - len(changes)
    overall = changed / total
    cells = {}
    for key, row in january["cells"].items():
        if row.get("smoothed_toward"):
            continue
        n, c = row["seasons"] - removed[key], row["changed"] - removed[key]
        cells[key] = {"changed": c, "seasons": n, "removed": removed[key],
                      "raw_rate": round(c / n, 4) if n else None,
                      "rate": round((c + JANUARY_PRIOR * overall) / (n + JANUARY_PRIOR), 4)}
    for key, row in january["cells"].items():
        if not row.get("smoothed_toward"):
            continue
        parent = cells[key.rsplit("|", 1)[0]]["rate"]
        n, c = row["seasons"] - removed[key], row["changed"] - removed[key]
        cells[key] = {"changed": c, "seasons": n, "removed": removed[key],
                      "raw_rate": round(c / n, 4) if n else None,
                      "rate": round((c + JANUARY_PRIOR * parent) / (n + JANUARY_PRIOR), 4),
                      "smoothed_toward": "parent cell"}
    unknown = set(removed) - set(january["cells"])
    if unknown:
        raise ValueError("in-season changes in cells the January table lacks: %s" % sorted(unknown))
    return {
        "use": ("Step 6's season-end draw only: the chance a club whose head coach was not changed in season "
                "changes him by the next season's opener. The weekly check never reads it."),
        "definition": ("The January table (library/data/2012_hc_change_base_rates.json) with the club-seasons that "
                       "had an in-season change taken out of their cells and of the overall rate, smoothed as the "
                       "January builder smooths: rate = (changed + %d * overall) / (seasons + %d), a split cell "
                       "toward its parent cell." % (JANUARY_PRIOR, JANUARY_PRIOR)),
        "january_sha256": hashlib.sha256(JANUARY.read_bytes()).hexdigest(),
        "club_seasons": total, "changed": changed, "overall_rate": round(overall, 4),
        "cells": dict(sorted(cells.items())),
    }


def build(data, january):
    games = club_games(data)
    cells, changes, counted = hazard(games)
    events = sum(c for c, _ in cells.values())
    at_risk = sum(n for _, n in cells.values())
    overall = events / at_risk
    # Every season of the window has sixteen regular-season games; the last has no later game.
    lengths = {len(regular(games, key)) for key in games if FIRST <= key[1] <= LAST and key not in LEFT_OUT}
    if lengths != {16}:
        raise ValueError("regular seasons of other lengths in the window: %s" % sorted(lengths))
    last_game = max(lengths) - 1
    small = sorted(k for k, (_, n) in cells.items() if n < PRIOR_WEIGHT)
    if small:
        raise ValueError("cells below the prior weight need the merge rule applied by hand: %s" % small)
    rates = {k: {"changes": c, "club_games": n, "raw_rate": round(c / n, 6),
                 "rate": round((c + PRIOR_WEIGHT * overall) / (n + PRIOR_WEIGHT), 6)}
             for k, (c, n) in sorted(cells.items())}
    return {
        "schema_version": "hc-inseason-hazard-v1",
        "source": SOURCE,
        "window": ("regular seasons 2002-2012, each club's games 1 to 15 (game 16 has no later regular-season game) "
                   "up to and including its first change; 1999-2001 read only to count a coach's seasons with the "
                   "club back; no row after 2012 is read"),
        "games_at_risk": {"first": 1, "last": last_game},
        "event": ("the coach who coached the club's game k does not coach game k+1 or any later regular-season game "
                  "that season: an interim who finishes the season counts; a stand-in for a coach who returns does "
                  "not (the season's opening coach coached a later game)"),
        "left_out": ["New Orleans 2012 (the suspension season), as in the January data"],
        "cells": {
            "margin": "the club's losses minus wins after game k, ties counting neither: " + ", ".join(BANDS),
            "tenure": ("the coach's season with the club: his first (he did not open the club's season before) or a "
                       "later one; consecutive seasons he opened for the club, counted back to 1999 as the January "
                       "builder counts them"),
        },
        "smoothing": "rate = (changes + %d * overall) / (club-games + %d)" % (PRIOR_WEIGHT, PRIOR_WEIGHT),
        "prior_weight": PRIOR_WEIGHT,
        "prior_weight_basis": ("the January table's prior of %d club-seasons at fifteen at-risk games a club-season"
                               % JANUARY_PRIOR),
        "merge_rule": ("a cell with fewer at-risk club-games than the prior weight is merged into the cell of the next "
                       "band toward 0 or fewer with the same tenure; none is that small, so none is merged"),
        "merged": [],
        "modelling_choice": ("The cells, the prior weight and the merge rule are the career's labelled modelling "
                             "choice, like the January factors; the user may change them before the first weekly "
                             "draw, never after."),
        "club_seasons": counted,
        "overall": {"changes": events, "club_games": at_risk, "rate": round(overall, 6)},
        "rates": rates,
        "changes": changes,
        "january_conditional": conditional(games, changes, january),
    }


def render(table):
    return json.dumps(table, indent=1) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--file", type=Path, help="a local copy of the pinned games.csv")
    parser.add_argument("--check", action="store_true", help="rebuild in memory and compare; write nothing")
    args = parser.parse_args(argv)
    try:
        data = read_source(args.file)
    except (OSError, ValueError) as exc:
        print("IN-SEASON HAZARD: %s" % exc)
        return 1
    text = render(build(data, json.loads(JANUARY.read_text(encoding="utf-8"))))
    if args.check:
        if not OUT.is_file() or OUT.read_text(encoding="utf-8") != text:
            print("IN-SEASON HAZARD: %s is missing or differs from a rebuild" % OUT.relative_to(ROOT))
            return 1
        print("IN-SEASON HAZARD CURRENT")
        return 0
    OUT.write_text(text, encoding="utf-8")
    table = json.loads(text)
    print("club-seasons %d, changes %d, club-games %d, overall %.6f" % (
        table["club_seasons"], table["overall"]["changes"], table["overall"]["club_games"], table["overall"]["rate"]))
    for key, row in table["rates"].items():
        print(key, row)
    return 0


if __name__ == "__main__":
    sys.exit(main())
