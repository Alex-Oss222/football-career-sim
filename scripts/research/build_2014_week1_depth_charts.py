#!/usr/bin/env python3
"""Build the 2014 Week 1 depth-chart library for the 31 background clubs.

Research tool only; the runtime never downloads anything. Fetch the inputs
into SOURCE_DIR first (a transient workspace, never committed):

  nflverse week-by-week 2014 depth charts (primary):
    https://github.com/nflverse/nflverse-data/releases/download/depth_charts/depth_charts_2014.csv
  nflverse 2014 weekly rosters (club-membership cross-check only):
    https://github.com/nflverse/nflverse-data/releases/download/weekly_rosters/roster_weekly_2014.csv
  nflverse 2014 injury reports (the Week 1 pre-game report):
    https://github.com/nflverse/nflverse-data/releases/download/injuries/injuries_2014.csv
  the user's Week 1 file (optional; same club membership as the nflverse
  chart, adds birth_date, headshot_url and page_url per player):
    user_nfl_2014_week1.json

Usage:
  python scripts/research/build_2014_week1_depth_charts.py SOURCE_DIR > library/data/2014_week1_depth_charts.json

Read only: the Week 1 depth chart, the Week 1 injury report (dated
September 3 to 6, 2014), branch control from the 2014 roster, the branch
draft pairing, the branch trades and the 2013 branch placements carried in
the league database. No score, statistic, game participation, later
transaction or later roster status is read. Later weeks' injury reports and
depth charts are consulted only to project the return of a player already
out before Week 1 (the 2013 builder's rule). The weekly-roster feed's status
column is ignored because it stamps later-season moves onto Week 1.

Differences from the 2013 builder, all documented in
library/2014_week1_depth_charts.md: no prior-season usage file is read
(the branch's 2013 differs from the real one), so co-listed players are
ordered by depth string, then line slot, then jersey number, then name;
branch trades, draft pairings and the 2013 branch placements are applied
from the 2014 records instead of one hard-coded trade.
"""
from __future__ import annotations

import collections
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from runtime.usage import MINIMUM_GAME_DAY, group  # noqa: E402

SEASON = 2014
WEEK = 1
CLUBS = {
    "ARI": "Arizona Cardinals", "ATL": "Atlanta Falcons", "BAL": "Baltimore Ravens",
    "BUF": "Buffalo Bills", "CAR": "Carolina Panthers", "CHI": "Chicago Bears",
    "CIN": "Cincinnati Bengals", "CLE": "Cleveland Browns", "DAL": "Dallas Cowboys",
    "DEN": "Denver Broncos", "DET": "Detroit Lions", "GB": "Green Bay Packers",
    "HOU": "Houston Texans", "IND": "Indianapolis Colts", "KC": "Kansas City Chiefs",
    "MIA": "Miami Dolphins", "MIN": "Minnesota Vikings", "NE": "New England Patriots",
    "NO": "New Orleans Saints", "NYG": "New York Giants", "NYJ": "New York Jets",
    "OAK": "Oakland Raiders", "PHI": "Philadelphia Eagles", "PIT": "Pittsburgh Steelers",
    "SD": "San Diego Chargers", "SEA": "Seattle Seahawks", "SF": "San Francisco 49ers",
    "STL": "St. Louis Rams", "TB": "Tampa Bay Buccaneers", "TEN": "Tennessee Titans",
    "WAS": "Washington Redskins",
}
# The weekly-roster feed uses legacy codes for five clubs.
ROSTER_CODE = {"ARI": "ARZ", "BAL": "BLT", "CLE": "CLV", "HOU": "HST", "STL": "SL"}
PROTAGONIST_CODE = "JAX"

ROSTER_MD = ROOT / "career/2014/team/roster/roster.md"
BIRTH_DATES = ROOT / "library/data/player_birth_dates.json"
LEAGUE_PLAYERS = ROOT / "career/2014/league/personnel/league_players.json"

# Draft pairing (career/2014/league/personnel/draft_pairing.md, method
# section 6): the real Jaguars' k-th selection goes to the club that really
# drafted Jacksonville's k-th branch selection and takes the depth slot he
# held on the real Jaguars' Week 1 chart. Mode "slot": his real slot string
# is kept and ties with an incumbent at the same string are broken by the
# ordinary tiebreak (the 2013 convention, which never displaces a listed
# player by fiat).
PAIRINGS = {
    "Blake Bortles": ("STL", "Draft pairing k=1: real Jaguars' #3 pick; Jacksonville took Aaron Donald at #13 (St. Louis's real pick)"),
    "Marqise Lee": ("CLE", "Draft pairing k=2: real Jaguars' #39 pick; Jacksonville took Joel Bitonio at #26 (Cleveland's real #35 pick)"),
    "Allen Robinson": ("GB", "Draft pairing k=3: real Jaguars' #61 pick; Jacksonville took Davante Adams at #38 (Green Bay's real #53 pick)"),
    "Brandon Linder": ("CAR", "Draft pairing k=4: real Jaguars' #93 pick; Jacksonville took Trai Turner at #90 (Carolina's real #92 pick)"),
    "Chris Smith": ("CHI", "Draft pairing k=7: real Jaguars' #159 pick; Jacksonville took Charles Leno Jr. at #168 (Chicago's real #246 pick)"),
    "Luke Bowanko": ("NE", "Draft pairing k=8: real Jaguars' #205 pick; Jacksonville took Jemea Thomas at #205 (New England's real #206 pick)"),
    "Storm Johnson": ("NE", "Draft pairing k=9: real Jaguars' #222 pick; Jacksonville took Malcolm Butler at #241 (New England's real undrafted signing)"),
}
# Real Jaguars' selections with no partner club (draft_pairing.md).
PAIRINGS_UNPLACED = {
    "Aaron Colvin": "Draft pairing k=5: real Jaguars' #114 pick; Jacksonville's partner club would be Jacksonville itself (Telvin Smith, real #144), so the selection is unplaced",
}
# 2013 branch placements carried into 2014 (league_players.json,
# assignment existing_branch_placement; library/2013_week1_depth_charts.md).
# Each stays under the club that received him in the branch, at the slot
# string he holds on his real 2014 Week 1 chart. Blaine Gabbert is not
# listed: the real San Francisco trade rides the rails (see the record).
CARRIED_2013_PLACEMENTS = {
    "Luke Joeckel": ("PHI", "2013 draft swap (#2, Lane Johnson); a Philadelphia player in the branch since 2013"),
    "Dwayne Gratz": ("PHI", "2013 draft swap (#64, Jordan Poyer); a Philadelphia player in the branch since 2013"),
    "Demetrius McCray": ("PHI", "2013 draft swap (#210 stayed with Philadelphia); a Philadelphia player in the branch since 2013"),
    "Ace Sanders": ("PHI", "2013 draft swap (#101 stayed with Philadelphia); a Philadelphia player in the branch since 2013"),
    "Matt Barkley": ("OAK", "2013 draft swap (#98, Sio Moore); an Oakland player in the branch since 2013"),
    "Johnathan Cyprien": ("KC", "2013 draft swap (#33, Travis Kelce); a Kansas City player in the branch since 2013"),
    "Jeremy Harris": ("KC", "2013 draft swap (#208, Tyler Bray), unplaced in 2013 for want of a Week 1 chart; the league database carries him as Kansas City's, and he has a 2014 chart slot"),
    "Denard Robinson": ("TEN", "2013 draft swap (#135, Lavar Edwards); a Tennessee player in the branch since 2013"),
    "Josh Evans": ("WAS", "2013 draft swap (#169, Bacarri Rambo); a Washington player in the branch since 2013"),
}
# Branch trades (career/2014/trades/completed_trades/trades.md). Mode
# "bottom": added below every listed player of his group, the 2013 Gabbert
# convention, because the branch has no depth evidence for him on his new
# club and the real Jaguars' slot describes a different club.
TRADES = {
    "Uche Nwaneri": ("ARI", "G", "Branch trade to Arizona, March 20, 2014 (2013 ledger Entry 99)"),
    "Jason Babin": ("MIA", "DE", "Branch trade to Miami, March 24, 2014 (ledger Entry 102)"),
    "Tyson Alualu": ("HOU", "DT", "Branch trade to Houston, March 24, 2014 (ledger Entry 102)"),
    "Cecil Shorts": ("IND", "WR", "Branch trade to Indianapolis, March 31, 2014 (ledger Entry 104)"),
    "Justin Blackmon": ("IND", "WR", "Branch trade to Indianapolis, March 31, 2014 (ledger Entry 104); no real suspension is imported (rails rule 2), so he is available"),
    "Will Rackley": ("SEA", "G", "Branch trade to Seattle, May 12, 2014 (ledger Entry 110)"),
}
# Former Jacksonville players with no branch club and no 2014 chart row.
UNPLACED_NO_CHART = {
    "Russell Allen": "LB; retired April 22, 2014 (retirements.md; traded to Arizona April 7, applied at Arizona)",
    "Stephen Morris": "QB; declined Jacksonville's undrafted offer; his real club was the real Jaguars, so he is an unplaced free agent (rails rule 4)",
    "Austen Lane": "DE; claimed on waivers August 31, 2013 by a club the branch never named; on no 2014 Week 1 chart",
    "Isaiah Stanback": "WR; claimed on waivers August 31, 2013 by a club the branch never named; on no 2014 Week 1 chart",
    "Kevin Rutland": "CB; not tendered March 11, 2014; on no 2014 Week 1 chart",
    "Allen Reisner": "TE; not tendered March 11, 2014; on no 2014 Week 1 chart",
    "Brandon King": "DB; 2013 practice squad, not offered a contract; on no 2014 Week 1 chart",
}
# Injury-report designations under which the report projected a player not
# to play: Out (will not play) and Doubtful (at least 75 percent likely not
# to play). Same convention as 2013.
UNAVAILABLE_REPORT = {"Out", "Doubtful"}
OL_SLOT_ORDER = ("LT", "LG", "C", "RG", "RT")
SIDE = {"QB": "O", "RB": "O", "FB": "O", "WR": "O", "TE": "O", "OL": "O",
        "DL": "F", "LB": "F", "DB": "B", "K": "S", "P": "S", "LS": "S"}
BIO_FIELDS = ("birth_date", "headshot_url", "page_url")


def norm(name):
    return re.sub(r"[^a-z]", "", name.lower())


def read(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def jersey_key(jersey):
    return int(jersey) if str(jersey or "").isdigit() else 999


def control_reason(status):
    """Why a player belongs to Jacksonville, from the roster Status cell."""
    m = re.search(r"\(Rookie, drafted (No\. \d+), ([A-Z][a-z]+ \d+, \d{4})", status)
    if m:
        return "drafted by Jacksonville, %s, %s" % (m.group(1), m.group(2))
    m = re.search(r"\(Rookie, undrafted; signed ([A-Z][a-z]+ \d+, \d{4})", status)
    if m:
        return "undrafted signing by Jacksonville, %s" % m.group(1)
    m = re.search(r"\((re-)?signed ([A-Z][a-z]+ \d+, \d{4})", status)
    if m:
        return "%ssigned by Jacksonville %s" % ("re-" if m.group(1) else "", m.group(2))
    if "reserve/future" in status:
        return "Jacksonville reserve/future contract effective March 11, 2014"
    if "tender" in status:
        return "Jacksonville tender; under Jacksonville control"
    return "under Jacksonville control in the branch (2013 roster carried)"


def branch_control(roster_md):
    """Jacksonville-controlled players: name -> (position, reason)."""
    text = roster_md.read_text(encoding="utf-8")
    body = text.split("## Current controlled players", 1)[1]
    body = re.split(r"^## ", body, maxsplit=1, flags=re.M)[0]
    control = {}
    for line in body.splitlines():
        m = re.match(r"^\| ([^|]+?) \| ([A-Z]+) \| \d{4}-\d{2}-\d{2} \| \d+ \| ([^|]+?) \|", line)
        if m:
            control[m.group(1).strip()] = (m.group(2), control_reason(m.group(3)))
    return control


def identity():
    """name -> gsis id from the identity registry and the league database."""
    ids = {}
    for name, row in json.load(open(BIRTH_DATES, encoding="utf-8"))["players"].items():
        if row.get("gsis_id"):
            ids.setdefault(name, row["gsis_id"])
    for row in json.load(open(LEAGUE_PLAYERS, encoding="utf-8"))["players"]:
        if row.get("player_id"):
            ids.setdefault(row["name"], row["player_id"])
    return ids


def real_jaguars_reason(row, league_db):
    """Why a real Jaguars Week 1 player has no branch club (rails rule 4)."""
    entry = league_db.get(row["gsis_id"])
    if entry is None:
        return "2014 rookie the real Jaguars drafted or signed; not a branch player"
    if entry["assignment"] == "real_jaguars_only":
        return "real 2013 Jaguars player the branch never controlled (unplaced since 2013)"
    club = entry.get("source_club") or "another club"
    return "real Jaguars 2014 acquisition the branch never made (real 2013 club %s)" % club


def pre_existing_return(reports, charted):
    """First week a player already out before Week 1 is expected to play.

    He did not play in the real Week 1, so his later pre-game reports still
    describe that pre-existing injury. He returns the first week he is
    reported Questionable or Probable, or is off the report while listed on
    his club's depth chart. After that week nothing more is read: any later
    report could describe an injury from a real game. None means no return
    during the regular season.
    """
    for week in range(2, 18):
        status = reports.get(week)
        if status in {"Questionable", "Probable"} or (status is None and charted(week)):
            return week
    return None


def compact(player):
    """Stored fields only; group and unit are derived from position on load."""
    out = {"player_id": player["player_id"], "position": player["position"], "depth": player["depth"]}
    if player["name"] != player["player_id"]:
        out["name"] = player["name"]
    if player["listed_position"] != player["position"]:
        out["listed_position"] = player["listed_position"]
    if not player["available"]:
        out["available"] = False
    if player["injury_report"]:
        out["injury_report"] = player["injury_report"]
    if player["return_week"]:
        out["return_week"] = player["return_week"]
    if player["roles"]:
        out["roles"] = player["roles"]
    for key in ("slots", "jersey", "gsis_id") + BIO_FIELDS:
        if player.get(key):
            out[key] = player[key]
    return out


def load_user_file(source):
    """gsis id -> the user's row (bio fields, slots and jersey), if the file exists."""
    path = source / "user_nfl_2014_week1.json"
    if not path.is_file():
        return {}
    data = json.load(open(path, encoding="utf-8"))
    rows = {}
    for club in data["clubs"].values():
        for player in club["players"]:
            if player.get("gsis_id"):
                rows[player["gsis_id"]] = player
    return rows


def build(source):
    source = Path(source)
    all_depth = read(source / "depth_charts_2014.csv")
    depth = [r for r in all_depth if r["week"] == "1" and r["game_type"] == "REG"]
    roster_feed = {(r["team"], r["gsis_id"]) for r in read(source / "roster_weekly_2014.csv")
                   if r["week"] == "1" and r["game_type"] == "REG"}
    all_injuries = read(source / "injuries_2014.csv")
    injuries = {(r["team"], r["gsis_id"]): r for r in all_injuries
                if r["week"] == "1" and r["game_type"] == "REG"}
    later_reports = collections.defaultdict(dict)
    for r in all_injuries:
        if r["game_type"] == "REG" and r["week"] != "1" and r["report_status"]:
            later_reports[(r["team"], r["gsis_id"])][int(r["week"])] = r["report_status"]
    later_charts = {(r["club_code"], r["gsis_id"], int(r["week"]))
                    for r in all_depth if r["game_type"] == "REG" and r["week"] not in ("", "1")}
    user_rows = load_user_file(source)
    league_db = {row["player_id"]: row for row in json.load(open(LEAGUE_PLAYERS, encoding="utf-8"))["players"]}

    control = branch_control(ROSTER_MD)
    ids = identity()
    control_by_gsis, control_by_norm, unmatched = {}, {}, []
    for name, (position, reason) in control.items():
        gsis = ids.get(name)
        if gsis:
            control_by_gsis[gsis] = (name, position, reason)
        else:
            unmatched.append(name)
        control_by_norm[norm(name)] = (name, position, reason)

    name_to_rows = collections.defaultdict(list)
    for row in depth:
        name_to_rows[row["full_name"].strip()].append(row)

    def real_row(name, code=None):
        rows = [r for r in name_to_rows.get(name, ()) if code is None or r["club_code"] == code]
        return rows[0] if rows else None

    # gsis -> (from club, to club, basis, mode)
    moves, synthetic = {}, collections.defaultdict(list)
    for name, (to_code, basis) in PAIRINGS.items():
        row = real_row(name, PROTAGONIST_CODE)
        if row is None:
            raise SystemExit("pairing player %s is not on the real Jaguars' Week 1 chart" % name)
        moves[row["gsis_id"]] = (PROTAGONIST_CODE, to_code, basis, "slot")
    for name, (to_code, basis) in CARRIED_2013_PLACEMENTS.items():
        row = real_row(name)
        if row is not None:
            moves[row["gsis_id"]] = (row["club_code"], to_code, basis, "slot")
        else:
            gsis = ids.get(name)
            synthetic[to_code].append((name, league_db.get(gsis, {}).get("position", "WR"), gsis,
                                       basis + "; on no 2014 Week 1 chart (his real 2014 absence is a suspension, which never rides the rails)"))
    for name, (to_code, position, basis) in TRADES.items():
        row = real_row(name)
        if row is not None:
            moves[row["gsis_id"]] = (row["club_code"], to_code, basis, "bottom")
        else:
            synthetic[to_code].append((name, position, ids.get(name), basis + "; on no 2014 Week 1 chart"))

    # Every listed player once per club, keeping every depth slot. A move
    # re-files the player under his branch club.
    listed = collections.OrderedDict()
    for row in depth:
        club = row["club_code"]
        move = moves.get(row["gsis_id"])
        if move and club == move[0]:
            club = move[1]
        key = (club, row["gsis_id"])
        entry = listed.setdefault(key, {"row": row, "slots": [], "move": move if club != row["club_code"] else None})
        slot = row["depth_position"].strip()
        entry["slots"].append((row["formation"], slot, int(row["depth_team"])))

    name_clubs = collections.defaultdict(set)
    for (code, _), entry in listed.items():
        name_clubs[norm(entry["row"]["full_name"])].add(code)

    clubs, removed, cross_check = {}, collections.defaultdict(list), collections.Counter()
    real_jaguars = []
    for code, team in CLUBS.items():
        players, changes, notes = [], [], []
        for (club, gsis), entry in listed.items():
            if club != code:
                continue
            row = entry["row"]
            name, listed_position = row["full_name"].strip(), row["position"].strip()
            football = [s for s in entry["slots"] if s[0] in {"Offense", "Defense"} and s[1]]
            if not football:
                football = [(f, "", rank + 3) for f, name_, rank in entry["slots"] if f in {"Offense", "Defense"}]
            best_slot = min(football, key=lambda s: s[2])[1] if football else ""
            position = best_slot if group(best_slot) else listed_position
            if entry["move"] and entry["move"][3] == "bottom":
                # A traded player is filed at the position the branch trade
                # record names, not at the slot of a club he never joined.
                position = TRADES[name][1]
            grp = group(position)
            if grp is None:
                raise SystemExit("unmapped position %r for %s" % (position, name))
            controlled = control_by_gsis.get(gsis)
            if controlled is None:
                # Name fallback only for a controlled player with no gsis id;
                # a namesake of a matched player (Baltimore's C.J. Mosley,
                # Minnesota's Mike Harris) stays with his club.
                candidate = control_by_norm.get(norm(name))
                if candidate and candidate[0] in unmatched and SIDE.get(group(candidate[1])) == SIDE.get(grp):
                    controlled = candidate
            if controlled:
                changes.append("Removed %s (%s): %s" % (name, position, controlled[2]))
                removed[team].append((name, controlled[2]))
                continue
            player_id = name
            if len(name_clubs[norm(name)]) > 1 or norm(name) in control_by_norm:
                player_id = "%s (%s)" % (name, code)
            real_code = row["club_code"]
            if entry["move"]:
                changes.append("Added %s (%s): %s%s" % (
                    name, position, entry["move"][2],
                    "; keeps his real slot string" if entry["move"][3] == "slot" else "; placed below every listed %s" % grp))
            cross_check["listed" if (ROSTER_CODE.get(real_code, real_code), gsis) in roster_feed else "not_in_roster_feed"] += 1
            report = injuries.get((real_code, gsis), {}).get("report_status", "") or None
            return_week = None
            if report in UNAVAILABLE_REPORT:
                return_week = pre_existing_return(later_reports.get((real_code, gsis), {}),
                                                  lambda week: (real_code, gsis, week) in later_charts)
            tier = min((s[2] for s in football), default=min(s[2] for s in entry["slots"]) + 3)
            if entry["move"] and entry["move"][3] == "bottom":
                tier = 9
            roles = []
            for formation, slot, rank in entry["slots"]:
                if slot in {"KR", "KOR"} and rank == 1:
                    roles.append("kick_return")
                if slot == "PR" and rank == 1:
                    roles.append("punt_return")
            if grp == "K":
                roles.append("placekicker")
            if grp == "P":
                roles.append("punt")
            ol_slot = next((OL_SLOT_ORDER.index(s[1]) for s in football if s[1] in OL_SLOT_ORDER), 9)
            slots = ",".join("%s%d" % (s[1] or s[0][:3].upper(), s[2]) for s in entry["slots"])
            user = user_rows.get(gsis, {})
            jersey = row["jersey_number"]
            if user:
                mine = {s for s in slots.split(",") if not s.startswith(("OFF", "DEF", "SPE"))}
                theirs = {s for s in (user.get("slots") or "").split(",") if s}
                cross_check["user_slots_agree" if mine == theirs else "user_slots_differ"] += 1
                # The user's jersey equals the Week 1 weekly-roster jersey for
                # every player; the depth-chart feed's jersey is stale for
                # about half, so the user's number is used when present.
                if user.get("jersey"):
                    cross_check["jersey_from_user_file"] += 1
                    if user["jersey"] != jersey:
                        cross_check["depth_chart_jersey_differs"] += 1
                    jersey = user["jersey"]
            player = {
                "player_id": player_id, "name": name, "position": position,
                "listed_position": listed_position, "group": grp,
                "available": report not in UNAVAILABLE_REPORT,
                "injury_report": report, "return_week": return_week, "roles": sorted(set(roles)),
                "gsis_id": gsis, "jersey": jersey, "slots": slots,
                "_order": (tier, ol_slot, jersey_key(jersey), name),
            }
            for field in BIO_FIELDS:
                if user.get(field):
                    player[field] = user[field]
                    cross_check["bio_" + field] += 1
            players.append(player)
        for name, position, gsis, basis in synthetic.get(code, ()):
            grp = group(position)
            bio = user_rows.get(gsis, {})
            player = {
                "player_id": name, "name": name, "position": position, "listed_position": position,
                "group": grp, "available": True, "injury_report": None, "return_week": None,
                "roles": [], "gsis_id": gsis, "jersey": None, "slots": "",
                "_order": (9, 9, 999, name),
            }
            for field in BIO_FIELDS:
                if bio.get(field):
                    player[field] = bio[field]
            players.append(player)
            changes.append("Added %s (%s): %s; placed below every listed %s" % (name, position, basis, grp))

        by_group = collections.defaultdict(list)
        for player in players:
            by_group[player["group"]].append(player)
        for members in by_group.values():
            for rank, player in enumerate(sorted(members, key=lambda p: p["_order"]), 1):
                player["depth"] = rank
        for player in players:
            del player["_order"]
        players.sort(key=lambda p: (list(SIDE).index(p["group"]) if p["group"] in SIDE else 99, p["depth"]))
        counts = collections.Counter(p["group"] for p in players if p["available"])
        short = {g: need for g, need in MINIMUM_GAME_DAY.items() if counts.get(g, 0) < need}
        if short:
            notes.append("Below the game-day minimum: %s" % ", ".join(
                "%s %d of %d" % (g, counts.get(g, 0), n) for g, n in short.items()))
        clubs[team] = {"code": code, "players": [compact(p) for p in players], "branch_changes": changes, "notes": notes}

    # The real Jaguars' Week 1 chart: recorded for the pairing, never a club.
    unplaced = []
    jaguars_rows = collections.OrderedDict()
    for row in depth:
        if row["club_code"] == PROTAGONIST_CODE:
            jaguars_rows.setdefault(row["gsis_id"], []).append(row)
    for gsis, rows in jaguars_rows.items():
        row = rows[0]
        name = row["full_name"].strip()
        slots = ",".join("%s%d" % (r["depth_position"].strip() or r["formation"][:3].upper(), int(r["depth_team"])) for r in rows)
        if gsis in control_by_gsis:
            disposition = "Jacksonville-controlled in the branch"
        elif gsis in moves:
            disposition = "moved to %s: %s" % (CLUBS[moves[gsis][1]], moves[gsis][2])
        elif name in PAIRINGS_UNPLACED:
            disposition = "unplaced: " + PAIRINGS_UNPLACED[name]
        elif name == "Alan Ball":
            disposition = "unplaced: left Jacksonville as a free agent March 11, 2014; his real next move was a re-signing with the real Jaguars, a real Jaguars move the branch never made (rails rule 4)"
        elif name == "Will Ta'ufo'ou":
            disposition = "unplaced: 2013 practice squad, not offered a contract; his real next move was a re-signing with the real Jaguars (rails rule 4)"
        else:
            disposition = "unplaced: " + real_jaguars_reason(row, league_db)
        if disposition.startswith("unplaced"):
            unplaced.append("%s (%s): %s" % (name, row["position"], disposition[len("unplaced: "):]))
        real_jaguars.append({"player_id": name, "position": row["position"], "slots": slots,
                             "injury_report": injuries.get((PROTAGONIST_CODE, gsis), {}).get("report_status", "") or None,
                             "gsis_id": gsis, "disposition": disposition})
    for name, reason in sorted(UNPLACED_NO_CHART.items()):
        unplaced.append("%s (%s): %s" % (name, reason.split(";")[0], reason.split("; ", 1)[1]))

    # Exclusivity gate, replicated: no controlled player on any club and no
    # player on two clubs.
    seen = {}
    for team, club in clubs.items():
        for player in club["players"]:
            if player.get("gsis_id") in control_by_gsis or norm(player["player_id"].split(" (")[0]) in control_by_norm and player.get("gsis_id") is None:
                raise SystemExit("controlled player %s left on %s" % (player["player_id"], team))
            for key in (player.get("gsis_id"), player["player_id"]):
                if key and key in seen and seen[key] != team:
                    raise SystemExit("%s appears on %s and %s" % (key, seen[key], team))
                if key:
                    seen[key] = team

    return {
        "schema_version": 1,
        "season": SEASON,
        "week": WEEK,
        "gate": "Prepared research. Usable as background TeamInput only when the master clock reaches Week 1 (September 7, 2014); the real charts were public September 2 to 5, 2014.",
        "branch_basis": "career/2014/team/roster/roster.md, July 29, 2014 (78 Jacksonville-controlled players: 74 under contract and four unsigned tenders)",
        "branch_controlled_players": sorted(control),
        "branch_control_unmatched": unmatched,
        "unplaced_branch_players": unplaced,
        "draft_swaps_without_week1_chart": ["%s: %s" % (n, b) for n, b in sorted(PAIRINGS_UNPLACED.items())],
        "real_jaguars_week1_chart": real_jaguars,
        "sources": {
            "depth_chart": "nflverse depth_charts_2014.csv, week 1, regular season",
            "availability": "nflverse injuries_2014.csv, week 1 report (September 3 to 6, 2014); Out and Doubtful are unavailable",
            "pre_existing_returns": "for Week 1 Out/Doubtful players only: first later week reported Questionable/Probable, or off the report and on the club depth chart",
            "co_listed_order": "depth string, then line slot LT-LG-C-RG-RT, then jersey number, then name; no prior-season usage is read because the branch's 2013 is not the real 2013",
            "membership_cross_check": "nflverse roster_weekly_2014.csv, week 1 club membership only; status ignored",
            "bio_fields": "user_nfl_2014_week1.json (same club membership as the nflverse chart): birth_date, headshot_url and page_url per gsis id, carried as data only",
            "branch_control": "career/2014/team/roster/roster.md matched by gsis id through library/data/player_birth_dates.json and career/2014/league/personnel/league_players.json",
            "draft_pairing": "career/2014/league/personnel/draft_pairing.md",
            "trades": "career/2014/trades/completed_trades/trades.md",
            "retirements": "career/2014/league/personnel/retirements.md",
        },
        "cross_check": dict(sorted(cross_check.items())),
        "removed_by_club": {team: [n for n, _ in names] for team, names in sorted(removed.items())},
        "clubs": clubs,
    }


def dumps(library):
    """Stable JSON with one player per line, so a rebuild diffs cleanly."""
    lines = ["{"]
    head = {k: v for k, v in library.items() if k != "clubs"}
    for key, value in head.items():
        lines.append("  %s: %s," % (json.dumps(key), json.dumps(value)))
    lines.append('  "clubs": {')
    teams = list(library["clubs"])
    for t_index, team in enumerate(teams):
        club = library["clubs"][team]
        lines.append("    %s: {" % json.dumps(team))
        lines.append('      "code": %s,' % json.dumps(club["code"]))
        lines.append('      "branch_changes": %s,' % json.dumps(club["branch_changes"]))
        lines.append('      "notes": %s,' % json.dumps(club["notes"]))
        lines.append('      "players": [')
        for p_index, player in enumerate(club["players"]):
            comma = "," if p_index < len(club["players"]) - 1 else ""
            lines.append("        %s%s" % (json.dumps(player), comma))
        lines.append("      ]")
        lines.append("    }" + ("," if t_index < len(teams) - 1 else ""))
    lines += ["  }", "}"]
    return "\n".join(lines) + "\n"


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.stdout.write(dumps(build(sys.argv[1])))


if __name__ == "__main__":
    main()
