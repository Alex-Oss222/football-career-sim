#!/usr/bin/env python3
"""Build birth-date evidence only, never current ages or later career outcomes.

Usage: python scripts/research/build_player_birth_dates.py SOURCE_DIR --checked-on YYYY-MM-DD
SOURCE_DIR contains nflverse players.csv and roster_2013.csv. Output is JSON
on stdout. Downloaded current status, last season and team are never imported.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.research.build_2013_week1_depth_charts import branch_control

# Reviewed identities, not fuzzy-name guesses. The DT is not the 2014 LB;
# the DE is not either namesake DB; King is Purdue's 2010 entrant, not Auburn's.
IDENTITIES = {
    "Mike Brown": "00-0029155", "Mike Brewster": "00-0029052",
    "C.J. Wilson": "00-0027822", "C.J. Mosley": "00-0023624",
    "Daryl Smith": "00-0022839", "Brandon King": "00-0027468",
    "Antwon Blake": "00-0029050",
}


def norm(name):
    return re.sub(r"[^a-z]", "", name.lower())


def build(source, checked_on):
    source = Path(source)
    with (source / "players.csv").open() as f:
        players = list(csv.DictReader(f))
    with (source / "roster_2013.csv").open() as f:
        roster = list(csv.DictReader(f))
    by_id = {p["gsis_id"]: p for p in players}
    library = json.loads((ROOT / "library/data/2013_week1_depth_charts.json").read_text())
    targets = {p["player_id"]: p for c in library["clubs"].values() for p in c["players"]}
    targets.update({n: {"position": p} for n, p in branch_control(ROOT / "career/2013/roster.md").items()})
    result = {}
    corrections = json.loads((ROOT / "library/data/player_birth_date_corrections.json").read_text())["players"]
    for name, target in sorted(targets.items()):
        identity = target.get("gsis_id") or IDENTITIES.get(name)
        if identity is None:
            matches = [p for p in players if norm(name) == norm(p["display_name"])]
            if len(matches) != 1:
                raise ValueError("Identity needs manual review: " + name)
            identity = matches[0]["gsis_id"]
        player = by_id[identity]
        dob = player["birth_date"] or None
        comparison = {p["birth_date"] for p in roster if p["gsis_id"] == identity and p["birth_date"]}
        if comparison and comparison != {dob}:
            raise ValueError("Birth-date disagreement: %s %s vs %s" % (name, dob, comparison))
        verification = json.loads((source / "espn_birth_dates" / (identity + ".json")).read_text())
        if verification.get("player") != name or not verification.get("birth_date"):
            raise ValueError("Independent verification missing: " + name)
        sources = ["nflverse_players"] + (["nflverse_roster_2013"] if comparison else [])
        sources.append("espn")
        row = {"gsis_id": identity, "birth_date": dob, "espn_id": verification["espn_id"],
               "evidence": "corroborated", "sources": sources}
        if verification["birth_date"] != dob:
            correction = corrections.get(name)
            if correction is None or correction["nflverse_birth_date"] != dob or correction["espn_birth_date"] != verification["birth_date"]:
                raise ValueError("Unreviewed independent birth-date disagreement: " + name)
            row["birth_date"] = correction["birth_date"]
            row["evidence"] = "reviewed_source_conflict"
            row["sources"].append("conflict_review")
        result[name] = row
    return {"schema_version": 1, "scope": "2013 branch roster and background depth library",
            "checked_on": checked_on,
            "sources": {
                "nflverse_players": {"url": "https://github.com/nflverse/nflverse-data/releases/download/players/players.csv",
                                     "sha256": hashlib.sha256((source / "players.csv").read_bytes()).hexdigest()},
                "nflverse_roster_2013": {"url": "https://github.com/nflverse/nflverse-data/releases/download/rosters/roster_2013.csv",
                                         "sha256": hashlib.sha256((source / "roster_2013.csv").read_bytes()).hexdigest()},
                "espn": {"url_template": "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/athletes/{espn_id}?lang=en&region=us",
                         "fields_used": ["id", "displayName", "dateOfBirth"]},
                "conflict_review": {"path": "library/data/player_birth_date_corrections.json"}},
            "players": result}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_dir")
    parser.add_argument("--checked-on", required=True)
    args = parser.parse_args()
    from datetime import date
    date.fromisoformat(args.checked_on)
    data = build(args.source_dir, args.checked_on)
    # One person per line keeps the evidence registry reviewable.
    head = {k: v for k, v in data.items() if k != "players"}
    print(json.dumps(head, indent=2)[:-2] + ',\n  "players": {')
    print(",\n".join("    %s: %s" % (json.dumps(n), json.dumps(p)) for n, p in data["players"].items()))
    print("  }\n}")
