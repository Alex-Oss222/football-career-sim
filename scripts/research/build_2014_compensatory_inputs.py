#!/usr/bin/env python3
"""Build the 2013 qualifying-free-agent inputs for the branch 2014 compensatory awards.

  python scripts/research/build_2014_compensatory_inputs.py

Sources (both public before March 24, 2014 for the fields used):
- nflverse roster_2012.csv: each player's final 2012 club and accrued seasons.
- nflverse historical_contracts.csv.gz (Over The Cap data): the 2013 contract
  a player signed with his new club (APY) and his prior contract's term.
The branch 2013 club comes from library/data/2013_week1_depth_charts.json, which
already removes Jacksonville-controlled players and never places the real
Jaguars' signings that the branch did not make. Jacksonville's own 2013 gains
come from its branch contracts (career/2013/offseason/free_agency/signings.md).
No 2014 compensatory award list is read. Downloads are cached in .sim_cache/.
"""
import bisect
import csv
import collections
import gzip
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / ".sim_cache" / "compensatory_2014"
OUT = ROOT / "career" / "2014" / "04_draft" / "compensatory" / "inputs.json"
ROSTER_URL = "https://github.com/nflverse/nflverse-data/releases/download/rosters/roster_2012.csv"
CONTRACTS_URL = "https://github.com/nflverse/nflverse-data/releases/download/contracts/historical_contracts.csv.gz"
NICK = {"49ers": "SF", "Bears": "CHI", "Bengals": "CIN", "Bills": "BUF", "Broncos": "DEN", "Browns": "CLE",
        "Buccaneers": "TB", "Cardinals": "ARI", "Chargers": "SD", "Chiefs": "KC", "Colts": "IND",
        "Commanders": "WAS", "Redskins": "WAS", "Cowboys": "DAL", "Dolphins": "MIA", "Eagles": "PHI",
        "Falcons": "ATL", "Giants": "NYG", "Jaguars": "JAX", "Jets": "NYJ", "Lions": "DET", "Packers": "GB",
        "Panthers": "CAR", "Patriots": "NE", "Raiders": "OAK", "Rams": "STL", "Ravens": "BAL", "Saints": "NO",
        "Seahawks": "SEA", "Steelers": "PIT", "Texans": "HOU", "Titans": "TEN", "Vikings": "MIN"}
ALIAS = {"LAC": "SD", "LV": "OAK", "LAR": "STL", "LA": "STL", "ARZ": "ARI", "BLT": "BAL", "CLV": "CLE",
         "HST": "HOU", "SL": "STL"}
# Branch 2013 contracts (signings.md section 2): APY is total value over term.
JACKSONVILLE_GAINS = [
    ("Brent Grimes", "CB", "ATL", 5_500_000, 1, 5_500_000),
    ("Roy Miller", "DT", "TB", 2_500_000, 2, 5_000_000),
    ("Sen'Derrick Marks", "DT", "TEN", 1_500_000, 1, 1_500_000),
    ("Alan Ball", "CB", "HOU", 1_000_000, 1, 1_000_000),
]


def fetch(url, name):
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / name
    if not path.exists():
        urllib.request.urlretrieve(url, path)
    return path


def codes(team):
    return {NICK[team]} if team in NICK else {ALIAS.get(p, p) for p in team.split("/")}


def norm(name):
    name = name.split(" (")[0].lower()
    for suffix in (" jr.", " sr.", " iii", " ii"):
        name = name.replace(suffix, "")
    return re.sub(r"[^a-z]", "", name)


def main():
    week1 = json.loads((ROOT / "library/data/2013_week1_depth_charts.json").read_text())
    with open(fetch(ROSTER_URL, "roster_2012.csv"), newline="") as f:
        last = {r["gsis_id"]: (ALIAS.get(r["team"], r["team"]), int(r["years_exp"] or 0)) for r in csv.DictReader(f)}
    with gzip.open(fetch(CONTRACTS_URL, "historical_contracts.csv.gz"), "rt", newline="") as f:
        by_name = collections.defaultdict(list)
        in_force = {}
        for r in csv.DictReader(f):
            by_name[norm(r["player"])].append(r)
            if r["year_signed"].isdigit() and r["years"].isdigit() and r["apy"] not in ("", "NA"):
                start, term = int(r["year_signed"]), int(r["years"])
                key = r["otc_id"] or r["player"]
                if start <= 2013 <= start + term - 1 and (key not in in_force or start > in_force[key][0]):
                    in_force[key] = (start, float(r["apy"]))
    market = sorted(apy for _, apy in in_force.values())

    def percentile(apy):
        below = bisect.bisect_left(market, apy)
        ties = bisect.bisect_right(market, apy) - below
        return round(100 * (below + ties / 2) / len(market), 2)
    candidates, excluded = [], []
    for club in week1["clubs"].values():
        for p in club["players"]:
            pid, new = p["player_id"], club["code"]
            if p.get("gsis_id") not in last:
                continue
            old, exp = last[p["gsis_id"]]
            if old == new:
                continue
            row = {"player": pid, "position": p["position"], "old_club": old, "new_club": new,
                   "accrued_seasons_after_2012": exp + 1}
            contracts = by_name.get(norm(pid), [])
            signed = [c for c in contracts if c["year_signed"] == "2013" and new in codes(c["team"])]
            prior = [c for c in contracts if c["year_signed"].isdigit() and 2000 < int(c["year_signed"]) <= 2012]
            if exp + 1 < 4:
                excluded.append({**row, "reason": "fewer than four accrued seasons: not an unrestricted free agent"})
                continue
            if not prior:
                excluded.append({**row, "reason": "no prior contract in the source; expiry cannot be shown"})
                continue
            p_row = max(prior, key=lambda c: int(c["year_signed"]))
            end = int(p_row["year_signed"]) + int(p_row["years"]) - 1
            if end > 2012:
                excluded.append({**row, "reason": f"prior contract ran through {end}: released or traded, not expired"})
                continue
            if new in codes(p_row["team"]):
                excluded.append({**row, "reason": "re-signed with the club holding his expiring contract"})
                continue
            if old not in codes(p_row["team"]):
                excluded.append({**row, "reason": "prior contract was not with his final 2012 club"})
                continue
            if not signed:
                excluded.append({**row, "reason": "unvalued: no 2013 contract with the new club in the source"})
                continue
            s_row = max(signed, key=lambda c: float(c["apy"] or 0))
            candidates.append({**row, "apy": int(float(s_row["apy"])), "years": int(s_row["years"]),
                               "value": int(float(s_row["value"])), "basis": "Over The Cap via nflverse",
                               "prior_contract": f'{p_row["team"]} {p_row["year_signed"]}, {p_row["years"]} years'})
    for name, pos, old, apy, years, value in JACKSONVILLE_GAINS:
        candidates.append({"player": name, "position": pos, "old_club": old, "new_club": "JAX",
                           "accrued_seasons_after_2012": None, "apy": apy, "years": years, "value": value,
                           "basis": "Branch contract, career/2013/offseason/free_agency/signings.md",
                           "prior_contract": "Expired 2012 contract (unrestricted free agent)"})
    for c in candidates:
        c["salary_percentile"] = percentile(c["apy"])
    candidates.sort(key=lambda r: (-r["apy"], r["player"]))
    excluded.sort(key=lambda r: (r["reason"], r["player"]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "schema_version": 1, "qualifying_free_agency_year": 2013,
        "sources": {"roster_2012": ROSTER_URL, "contracts": CONTRACTS_URL,
                    "branch_2013_clubs": "library/data/2013_week1_depth_charts.json",
                    "jacksonville_gains": "career/2013/offseason/free_agency/signings.md"},
        "salary_market": {"basis": "APY of each player's latest source contract in force in the 2013 league year",
                          "contracts": len(market), "median_apy": int(market[len(market) // 2])},
        "candidates": candidates, "excluded_movers": excluded}, indent=1) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(candidates)} valued, {len(excluded)} excluded")


if __name__ == "__main__":
    main()
