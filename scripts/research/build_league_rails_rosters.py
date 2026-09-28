#!/usr/bin/env python3
"""Draft the 2014 league-rails club rosters from committed and downloaded data.

  python scripts/research/build_league_rails_rosters.py CONTRACTS_CSV_GZ

Inputs: library/data/2013_week1_depth_charts.json (the branch's 31 background
clubs, already reconciled to Jacksonville control and the 2013 draft swaps)
and nflverse historical_contracts.csv.gz (Over The Cap). Only contracts signed
in 2013 or earlier are read, so no 2014 signing, destination or term leaks in.
The contract end year is a draft: Over The Cap rows for extensions can list
only the added years, so every row is labelled for the user to confirm.
Output: career/2014/offseason/league_rails/clubs/*.md and free_agent_pool.md.
"""
import csv, gzip, json, re, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "career/2014/offseason/league_rails"
NICK = {"Washington Redskins": ("Redskins", "Commanders", "Football Team"), "Oakland Raiders": ("Raiders",),
        "San Diego Chargers": ("Chargers",), "St. Louis Rams": ("Rams",)}


def norm(name):
    return re.sub(r"[^a-z]", "", name.lower().replace(" jr", "").replace(" sr", "").replace(" iii", "").replace(" ii", ""))


def main(path):
    lib = json.loads((ROOT / "library/data/2013_week1_depth_charts.json").read_text())
    clubs = lib["clubs"]
    contracts = defaultdict(list)
    for r in csv.DictReader(gzip.open(path, "rt")):
        try:
            ys, yrs = int(r["year_signed"]), int(r["years"] or 0)
        except ValueError:
            continue
        if ys <= 2013 and yrs > 0:
            contracts[norm(r["player"])].append((ys, yrs, r))
    (OUT / "clubs").mkdir(parents=True, exist_ok=True)
    pool = []
    for club in sorted(clubs):
        c = clubs[club]
        nicks = NICK.get(club, (club.split()[-1],))
        rows = []
        for p in c["players"]:
            name = p["player_id"]
            cands = contracts.get(norm(name), [])
            same = [x for x in cands if any(n in x[2]["team"] for n in nicks)] or cands
            if same:
                ys, yrs, r = max(same, key=lambda x: (x[0], x[1]))
                end = ys + yrs - 1
                apy = int(float(r["apy"] or 0))
                status = "Pending free agent (draft)" if end <= 2013 else "Under contract (draft)"
                ctext = "%d-%d, %s a year" % (ys, end, "${:,}".format(apy) if apy else "APY not listed")
            else:
                end, status, ctext = None, "Unknown: confirm", "not in the contract data"
            rows.append((p.get("slots") or p["position"], name, p["position"], ctext, status))
            if end is not None and end <= 2013:
                pool.append((club, name, p["position"], ctext))
        lines = ["# %s: 2014 rails roster (draft)" % club, "",
                 "**Status:** DRAFT for the user to complete. Starting point: the branch's 2013 Week 1 unit (`library/2013_week1_depth_charts.md`), with contract years from Over The Cap data signed in 2013 or earlier. The contract end year is unverified: extensions can list only the added years. No 2014 signing, release, trade or destination is recorded here; those enter only on their real dates (AGENTS.md, Historical league rails).",
                 "", "| 2013 slot | Player | Pos | Contract in the data (signed-to-end, average per year) | 2014 status | User notes |",
                 "|---|---|---|---|---|---|"]
        for slot, name, pos, ctext, status in rows:
            lines.append("| %s | %s | %s | %s | %s | |" % (slot, name, pos, ctext, status))
        lines += ["", "## Changes on the rails (fill by real date)", "",
                  "| Real date | Move | Player | Detail | Source | Gate passed in branch? |", "|---|---|---|---|---|---|", ""]
        (OUT / "clubs" / ("%s.md" % c["code"])).write_text("\n".join(lines))
    lines = ["# 2014 free-agent pool (draft)", "",
             "**Status:** DRAFT. Players on the 31 other clubs whose latest contract in the Over The Cap data signed in 2013 or earlier ends with the 2013 season. It is unverified and incomplete: unrestricted, restricted and exclusive-rights status is not separated, extensions may be missing, and players off the Week 1 charts are not included. Jacksonville's own pending free agents are in `career/2014/offseason/contract_status_register.md`. Where each player really went is not recorded until his real signing date.",
             "", "| Club (2013) | Player | Pos | Contract in the data |", "|---|---|---|---|"]
    lines += ["| %s | %s | %s | %s |" % x for x in pool]
    (OUT / "free_agent_pool.md").write_text("\n".join(lines) + "\n")
    print(len(clubs), "clubs;", len(pool), "pending free agents")


if __name__ == "__main__":
    main(sys.argv[1])
