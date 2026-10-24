#!/usr/bin/env python3
"""Pass 2 for the in-season head-coach change rates: separate code, same pinned file.

  python scripts/research/verify_hc_inseason_hazard.py GAMES_CSV

Written apart from scripts/research/build_hc_inseason_hazard.py and sharing no
code with it: it reads the CSV by column position, orders each club's games
by date rather than by week number, and finds a change from the last game the
season's opening coach coached. It then

1. lists every counted change by club, season and game, with the coaches and
   the record after the game, and compares the list with the table's;
2. checks each against the January table: the club-season must be a
   "changed" one there (a different coach opened the club's next season, read
   from that next season's first game, which for every change here is a 2012
   or earlier row) and must sit in a January cell, and its split cell, whose
   changed count covers it (library/data/2012_hc_change_base_rates.json);
3. recomputes every cell's at-risk club-games and changes, the overall rate,
   the smoothed rates, and the January table conditional on no in-season
   change, and compares each with the committed table
   (library/data/2012_hc_inseason_hazard.json);
4. lists every club-season with more than one coach in its rows, so each
   stand-in and each change is seen by eye.

It prints every difference and exits 1 if there is one. It writes nothing.
"""
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
TABLE = ROOT / "library/data/2012_hc_inseason_hazard.json"
JANUARY = ROOT / "library/data/2012_hc_change_base_rates.json"
SAME_CLUB = {"STL": "LA", "SD": "LAC", "OAK": "LV", "JAC": "JAX"}


def rows_by_club(path):
    """{club: {season: [(date, type, coach, us, them)]}} for 1999-2012, read by column position."""
    out = {}
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        col = {name: i for i, name in enumerate(header)}
        for row in reader:
            year = row[col["season"]]
            if not year.isdigit() or not 1999 <= int(year) <= 2012:
                continue
            for us, them in (("home", "away"), ("away", "home")):
                club = SAME_CLUB.get(row[col[us + "_team"]], row[col[us + "_team"]])
                out.setdefault(club, {}).setdefault(int(year), []).append(
                    (row[col["gameday"]], row[col["game_type"]], row[col[us + "_coach"]],
                     int(row[col[us + "_score"]]), int(row[col[them + "_score"]])))
    for seasons in out.values():
        for games in seasons.values():
            games.sort()
    return out


def opener(seasons, year):
    reg = [g for g in seasons.get(year, []) if g[1] == "REG"]
    return reg[0][2] if reg else None


def run_of(seasons, year):
    """How many seasons in a row, ending with ``year``, the same coach opened."""
    coach, n = opener(seasons, year), 0
    while opener(seasons, year - n) == coach and coach is not None:
        n += 1
    return n


def margin_band(m):
    if m <= 0:
        return "0 or fewer"
    if m <= 2:
        return "1 to 2"
    if m <= 4:
        return "3 to 4"
    return "5 or more"


def january_keys(seasons, year):
    reg = [g for g in seasons[year] if g[1] == "REG"]
    won = sum(g[3] > g[4] for g in reg) + sum(g[3] == g[4] for g in reg) / 2
    run = run_of(seasons, year)
    tb = {1: "1st season", 2: "2nd-3rd", 3: "2nd-3rd"}.get(run, "4th+")
    post = lambda y: any(g[1] != "REG" for g in seasons.get(y, []))
    if post(year):
        return ["playoffs|" + tb]
    for top, label in ((4.5, "0-4"), (6.5, "5-6"), (8.5, "7-8"), (10.5, "9-10")):
        if won <= top:
            wb = label
            break
    else:
        wb = "11+"
    if run == 1:
        return [wb + "|" + tb]
    recent = "recent playoffs" if post(year - 1) or post(year - 2) else "no recent playoffs"
    return [wb + "|" + tb, wb + "|" + tb + "|" + recent]


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    path = Path(argv[1])
    table = json.loads(TABLE.read_text(encoding="utf-8"))
    january = json.loads(JANUARY.read_text(encoding="utf-8"))
    differences = []
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != table["source"]["sha256"] or digest != january["source"]["sha256"]:
        differences.append("input digest %s differs from the tables' recorded digests" % digest)
    data = rows_by_club(path)

    # Club-seasons with more than one coach in their regular-season rows.
    print("Club-seasons with more than one coach, 2002-2012:")
    for club in sorted(data):
        for year in sorted(data[club]):
            reg = [g for g in data[club][year] if g[1] == "REG"]
            if year >= 2002 and len({g[2] for g in reg}) > 1:
                runs = []
                for i, g in enumerate(reg, 1):
                    if not runs or runs[-1][0] != g[2]:
                        runs.append([g[2], i, i])
                    runs[-1][2] = i
                print("  %s %d: %s" % (club, year, "; ".join("%s games %d-%d" % tuple(r) for r in runs)))

    # Recompute the risk set and the changes.
    at_risk, events, found, counted = {}, {}, [], 0
    for club in sorted(data):
        for year in sorted(data[club]):
            if not 2002 <= year <= 2012 or (club, year) == ("NO", 2012):
                continue
            reg = [g for g in data[club][year] if g[1] == "REG"]
            if not reg:
                continue
            counted += 1
            first = reg[0][2]
            tenure = "first season" if run_of(data[club], year) == 1 else "later season"
            final = max(i for i in range(len(reg)) if reg[i][2] == first)   # index of his last game
            won = lost = tied = 0
            for i in range(len(reg) - 1):
                won, lost, tied = won + (reg[i][3] > reg[i][4]), lost + (reg[i][3] < reg[i][4]), tied + (reg[i][3] == reg[i][4])
                key = margin_band(lost - won) + "|" + tenure
                at_risk[key] = at_risk.get(key, 0) + 1
                if i == final:
                    events[key] = events.get(key, 0) + 1
                    found.append((club, year, i + 1, first, reg[i + 1][2], won, lost, tied))
                    break
    print("\nCounted changes (club, season, game, coach, successor, record after the game):")
    for c in found:
        print("  %s %d game %d: %s, then %s; %d-%d%s" % (c[0], c[1], c[2], c[3], c[4], c[5], c[6],
                                                         "-%d" % c[7] if c[7] else ""))
    theirs = [(c["club"], c["season"], c["game"], c["coach"], c["successor"], c["wins"], c["losses"], c["ties"])
              for c in table["changes"]]
    if found != theirs:
        differences.append("the change list differs from the table's: %s" % sorted(set(found) ^ set(theirs)))
    if counted != table["club_seasons"]:
        differences.append("club-seasons %d, the table says %d" % (counted, table["club_seasons"]))
    lengths = {len([g for g in data[club][year] if g[1] == "REG"]) for club in data for year in data[club]
               if 2002 <= year <= 2012 and (club, year) != ("NO", 2012)}
    if lengths != {16} or table["games_at_risk"] != {"first": 1, "last": 15}:
        differences.append("season lengths %s against the table's games at risk %s" % (sorted(lengths),
                                                                                       table["games_at_risk"]))

    # The January table: each change is a "changed" club-season there, inside a cell that covers it.
    print("\nAgainst the January table:")
    removed = {}
    for club, year, game, coach, successor, *_ in found:
        nxt = opener(data[club], year + 1)
        changed = nxt is not None and nxt != coach
        keys = january_keys(data[club], year)
        for key in keys:
            removed[key] = removed.get(key, 0) + 1
        print("  %s %d: next season opened by %s (%s); January cell %s" % (
            club, year, nxt, "changed" if changed else "NOT CHANGED", " and ".join(keys)))
        if not changed:
            differences.append("%s %d is not a changed club-season in the January table" % (club, year))
    for key, n in sorted(removed.items()):
        cell = january["cells"].get(key)
        if cell is None or cell["changed"] < n:
            differences.append("January cell %s cannot hold %d in-season changes: %s" % (key, n, cell))

    # The rates.
    total_events, total_risk = sum(events.values()), sum(at_risk.values())
    overall = total_events / total_risk
    w = table["prior_weight"]
    if (total_events, total_risk, round(overall, 6)) != (table["overall"]["changes"], table["overall"]["club_games"],
                                                          table["overall"]["rate"]):
        differences.append("overall %d of %d differs from the table's %s" % (total_events, total_risk, table["overall"]))
    print("\nCells (changes of club-games, smoothed rate):")
    for key in sorted(set(at_risk) | set(table["rates"])):
        mine = {"changes": events.get(key, 0), "club_games": at_risk.get(key, 0),
                "raw_rate": round(events.get(key, 0) / at_risk[key], 6) if at_risk.get(key) else None,
                "rate": round((events.get(key, 0) + w * overall) / (at_risk.get(key, 0) + w), 6)}
        print("  %-28s %d of %d, %.6f" % (key, mine["changes"], mine["club_games"], mine["rate"]))
        if table["rates"].get(key) != mine:
            differences.append("cell %s: %s, the table says %s" % (key, mine, table["rates"].get(key)))

    # The January table conditional on no in-season change.
    cond = table["january_conditional"]
    base = {k: v for k, v in january["cells"].items() if "smoothed_toward" not in v}
    n_all = sum(v["seasons"] for v in base.values()) - len(found)
    c_all = sum(v["changed"] for v in base.values()) - len(found)
    rate_all = c_all / n_all
    mine = {}
    for key, v in base.items():
        n, c = v["seasons"] - removed.get(key, 0), v["changed"] - removed.get(key, 0)
        mine[key] = round((c + 5 * rate_all) / (n + 5), 4)
    for key, v in january["cells"].items():
        if "smoothed_toward" in v:
            n, c = v["seasons"] - removed.get(key, 0), v["changed"] - removed.get(key, 0)
            mine[key] = round((c + 5 * mine[key.rsplit("|", 1)[0]]) / (n + 5), 4)
    if (n_all, c_all, round(rate_all, 4)) != (cond["club_seasons"], cond["changed"], cond["overall_rate"]):
        differences.append("conditional totals %d, %d, %.4f differ from the table's" % (n_all, c_all, rate_all))
    for key in sorted(set(mine) | set(cond["cells"])):
        if cond["cells"].get(key, {}).get("rate") != mine.get(key):
            differences.append("conditional cell %s: %s, the table says %s" % (key, mine.get(key), cond["cells"].get(key)))
    print("\nConditional January table: %d club-seasons, %d changed, overall %.4f" % (n_all, c_all, rate_all))

    print("\nDifferences: %d" % len(differences))
    for d in differences:
        print("  " + d)
    return 1 if differences else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
