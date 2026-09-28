#!/usr/bin/env python3
"""Build the eligibility and line-start evidence for the 2013 season honours.

  python scripts/research/build_2013_honours_evidence.py SOURCE_DIR PACKAGE...

SOURCE_DIR holds the pinned public files named in SOURCES below. PACKAGE is
each frozen weekly TeamInput package for Weeks 1-17 (.sim_cache, transient);
each must match its closed receipts' game-day actives exactly or the build
stops. The output, career/2013/awards/season_honours_evidence.json, records
every source digest, so the draw reads only committed data.

Nothing here reads a 2013 result, award, statistic or later transaction. The
public files supply only facts fixed before the 2013 season: each player's
experience, his 2012 regular-season games, each club's 2012 record and its
opening-day head coach.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.research.build_2013_week1_depth_charts import CLUBS
from scripts.render_season_stats import load_receipts

OUT = ROOT / "career/2013/awards/season_honours_evidence.json"
SOURCES = {
    "roster_weekly_2013.csv": "https://github.com/nflverse/nflverse-data/releases/download/weekly_rosters/roster_weekly_2013.csv",
    "player_stats_2012.csv": "https://github.com/nflverse/nflverse-data/releases/download/player_stats/player_stats_2012.csv",
    "player_stats_def_2012.csv": "https://github.com/nflverse/nflverse-data/releases/download/player_stats/player_stats_def_2012.csv",
    "player_stats_2011.csv": "https://github.com/nflverse/nflverse-data/releases/download/player_stats/player_stats_2011.csv",
    "player_stats_def_2011.csv": "https://github.com/nflverse/nflverse-data/releases/download/player_stats/player_stats_def_2011.csv",
    "roster_2012.csv": "https://github.com/nflverse/nflverse-data/releases/download/rosters/roster_2012.csv",
    "games.csv": "https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv",
}
OL = {"T", "G", "C", "OT", "OG", "OL"}
# Branch facts from state/04_Roster_and_Staff_Register.md for Jacksonville
# players the public 2013 roster feed does not list.
BRANCH_EXPERIENCE = {
    "Adam Thielen": {"first_season": 2013, "basis": "state/04 register: three-year UDFA minimum contract (2013 undrafted rookie)"},
}
BRANCH_HEAD_COACHES = {"JAX": {"coach": "Alex Stone", "basis": "branch hire (career/2013/offseason/hiring_search.md)"}}
COMEBACK_MAX_2012_GAMES = 6
COMEBACK_MIN_EXPERIENCE = 2
COMEBACK_MIN_2011_GAMES = 8


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def season_players():
    team_of, positions = {}, {}
    for receipt in load_receipts(ROOT / "career/2013/stats/game_receipts"):
        if int(receipt["week"]) > 17:
            continue
        for team, stats in receipt["team_stats"].items():
            for name, row in stats["players"].items():
                team_of[name] = team
                positions.setdefault(name, {}).setdefault(row.get("position"), 0)
                positions[name][row.get("position")] += 1
    return team_of, positions


def main():
    source, packages = Path(sys.argv[1]), [Path(p) for p in sys.argv[2:]]
    team_of, positions = season_players()
    ids = json.loads((ROOT / "library/data/player_birth_dates.json").read_text(encoding="utf-8"))["players"]
    gsis = {name: ids[name]["gsis_id"] for name in team_of if name in ids}

    experience = {}
    for row in read(source / "roster_weekly_2013.csv"):
        if row["game_type"] == "REG" and row["years_exp"] != "":
            current = experience.get(row["gsis_id"])
            if current is None or int(row["week"]) < current[1]:
                experience[row["gsis_id"]] = (int(row["years_exp"]), int(row["week"]))
    # A player the 2013 feed omits takes his 2012 experience plus one.
    for row in read(source / "roster_2012.csv"):
        if row["years_exp"] != "" and row["gsis_id"] not in experience:
            experience[row["gsis_id"]] = (int(row["years_exp"]) + 1, 0)

    def games(season):
        weeks = {}
        for name in ("player_stats_%d.csv" % season, "player_stats_def_%d.csv" % season):
            for row in read(source / name):
                if row["season"] == str(season) and row["season_type"] == "REG":
                    weeks.setdefault(row["player_id"], set()).add(int(row["week"]))
        return weeks
    games_2011, games_2012 = games(2011), games(2012)

    rookies, comeback, unresolved = {}, {}, []
    for name in sorted(team_of):
        if name in BRANCH_EXPERIENCE:
            if BRANCH_EXPERIENCE[name]["first_season"] == 2013:
                rookies[name] = {"team": team_of[name], "basis": BRANCH_EXPERIENCE[name]["basis"]}
            continue
        known = experience.get(gsis.get(name))
        if known is None:
            unresolved.append(name)
            continue
        years = known[0]
        if years == 0:
            rookies[name] = {"team": team_of[name], "basis": "roster_weekly_2013 years_exp 0"}
        played_2011 = len(games_2011.get(gsis[name], ()))
        played_2012 = len(games_2012.get(gsis[name], ()))
        if (years >= COMEBACK_MIN_EXPERIENCE and played_2011 >= COMEBACK_MIN_2011_GAMES
                and played_2012 <= COMEBACK_MAX_2012_GAMES):
            comeback[name] = {"team": team_of[name], "years_exp": years,
                              "games_2011": played_2011, "games_2012": played_2012}

    receipts = {}
    for receipt in load_receipts(ROOT / "career/2013/stats/game_receipts"):
        if int(receipt["week"]) <= 17:
            receipts[(int(receipt["week"]), receipt["away"], receipt["home"])] = receipt
    starts, package_digests = {}, {}
    for path in packages:
        package = json.loads(path.read_text(encoding="utf-8"))
        # The Week 1 generation-3 package predates the "week" header.
        week = int(package.get("week", 1))
        package_digests[str(week)] = sha(path)
        for game in package["games"]:
            receipt = receipts[(week, game["away"], game["home"])]
            for side in ("away_input", "home_input"):
                team_input = game[side]
                team = team_input["team_id"]
                active = set(team_input["active_players"])
                if active != set(receipt["team_stats"][team]["players"]):
                    raise SystemExit("package week %d %s does not match its receipt" % (week, team))
                line = sorted((p for p in team_input["roster"]
                               if p["position"] in OL and p["player_id"] in active and p.get("available", True)),
                              key=lambda p: p["depth"])[:5]
                for player in line:
                    row = starts.setdefault(player["player_id"], {"team": team, "position": player["position"], "weeks": []})
                    row["weeks"].append(week)
    if sorted(int(w) for w in package_digests) != list(range(1, 18)):
        raise SystemExit("need one package for each of Weeks 1-17")

    coaches, records = {}, {}
    for row in read(source / "games.csv"):
        if row["game_type"] != "REG":
            continue
        if row["season"] == "2013" and row["week"] == "1":
            coaches[row["away_team"]] = row["away_coach"]
            coaches[row["home_team"]] = row["home_coach"]
        if row["season"] == "2012":
            away, home = int(row["away_score"]), int(row["home_score"])
            for club, us, them in ((row["away_team"], away, home), (row["home_team"], home, away)):
                wlt = records.setdefault(club, [0, 0, 0])
                wlt[0 if us > them else 1 if us < them else 2] += 1
    head_coaches = {}
    clubs = {**CLUBS, "JAX": "Jacksonville Jaguars"}
    for code, team in sorted(clubs.items(), key=lambda item: item[1]):
        branch = BRANCH_HEAD_COACHES.get(code)
        wins, losses, ties = records[code]
        head_coaches[team] = {
            "coach": branch["coach"] if branch else coaches[code],
            "basis": branch["basis"] if branch else "opening-day head coach (nfldata games.csv, 2013 Week 1 row); no branch change on record",
            "record_2012": {"wins": wins, "losses": losses, "ties": ties}}

    out = {
        "schema_version": "season-honours-evidence-v1",
        "sources": {name: {"url": url, "sha256": sha(source / name)} for name, url in SOURCES.items()},
        "name_to_gsis": "library/data/player_birth_dates.json",
        "packages_sha256": package_digests,
        "rules": {
            "rookie": "First NFL season is 2013: years_exp 0 in the earliest 2013 regular-season roster_weekly row, or a branch rookie contract on the register.",
            "comeback": "Not a rookie, years_exp >= %d in 2013, at least %d 2011 regular-season games and at most %d 2012 regular-season games with a recorded statistic (nflverse player_stats and player_stats_def, REG): an established player who lost most of 2012." % (COMEBACK_MIN_EXPERIENCE, COMEBACK_MIN_2011_GAMES, COMEBACK_MAX_2012_GAMES),
            "line_start": "The five available game-day active offensive linemen with the lowest depth in the frozen TeamInput start that game.",
            "head_coach": "Opening-day head coach; the branch records no in-season change.",
        },
        "unresolved_experience": unresolved,
        "rookies": rookies,
        "comeback_eligible": comeback,
        "line_starts": {name: starts[name] for name in sorted(starts)},
        "head_coaches": head_coaches,
    }
    OUT.write_text(json.dumps(out, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    print("rookies %d, comeback-eligible %d, linemen %d, unresolved %s" % (
        len(rookies), len(comeback), len(starts), unresolved))
    return 0


if __name__ == "__main__":
    sys.exit(main())
