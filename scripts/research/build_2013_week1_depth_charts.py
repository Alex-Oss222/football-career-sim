#!/usr/bin/env python3
"""Build the 2013 Week 1 depth-chart library for the 31 background clubs.

Research tool only; the runtime never downloads anything. Fetch the inputs
into SOURCE_DIR first:

  nflverse Week-by-week 2013 depth charts (primary):
    https://github.com/nflverse/nflverse-data/releases/download/depth_charts/depth_charts_2013.csv
  nflverse 2013 weekly rosters (club-membership cross-check only):
    https://github.com/nflverse/nflverse-data/releases/download/weekly_rosters/roster_weekly_2013.csv
  nflverse 2013 injury reports (Week 1 pre-game report):
    https://github.com/nflverse/nflverse-data/releases/download/injuries/injuries_2013.csv
  nflverse 2012 regular-season player stats (co-starter tiebreak):
    https://github.com/nflverse/nflverse-data/releases/download/stats_player/stats_player_reg_2012.csv
  nflverse draft picks (the real 2013 selection at each Jacksonville slot):
    https://github.com/nflverse/nflverse-data/releases/download/draft_picks/draft_picks.csv

Usage:
  python scripts/research/build_2013_week1_depth_charts.py SOURCE_DIR > library/data/2013_week1_depth_charts.json

Read only: the Week 1 depth chart, the Friday September 6, 2013 injury
report, 2012 usage and branch control from career/2013/roster.md. No Week 1
score, statistic, game participation or later roster status is read; the
weekly-roster feed's status column is ignored because it carries later-season
moves (for example injured-reserve placements made in October).
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

# Branch transactions that place a former Jacksonville player on another
# club (ledger Entry 5): Gabbert was traded to Green Bay for C.J. Wilson.
BRANCH_PLACEMENTS = {
    "Green Bay Packers": [{"name": "Blaine Gabbert", "position": "QB",
                           "basis": "Branch trade with Jacksonville (ledger Entry 5)"}],
}
# Draft swaps (user rule, September 27, 2026): at every slot Jacksonville
# used in the branch, the player the real Jaguars took at that slot goes to
# the club that historically had Jacksonville's branch pick, in the depth
# slot he held on his real Week 1 depth chart.
#
# One real draft-day trade did not happen in the branch: on April 27, 2013
# the Jaguars sent #98 to Philadelphia for #101 and #210 (NFL.com, "Matt
# Barkley taken by Philadelphia Eagles after trade"; nflverse draft_picks).
# Jacksonville kept #98 in the branch, so Philadelphia kept #101 and #210 and
# the players the real Jaguars took there go to Philadelphia.
UNTRADED_PICKS = {101: "PHI", 210: "PHI"}

# Waived by Jacksonville on August 31 and claimed by clubs the branch never
# named; they cannot be placed on any club without inventing the claimant.
UNPLACED_CLAIMS = ("Austen Lane", "Brandon Marshall", "Isaiah Stanback")

# Injury-report designations under which the 2013 report projected a
# player not to play: Out (will not play) and Doubtful (at least 75 percent
# likely not to play).
UNAVAILABLE_REPORT = {"Out", "Doubtful"}

USAGE_FIELDS = {
    "QB": ("attempts",), "RB": ("carries",), "FB": ("carries",),
    "WR": ("targets",), "TE": ("targets",),
    "DL": ("def_tackles_solo", "def_tackle_assists"),
    "LB": ("def_tackles_solo", "def_tackle_assists"),
    "DB": ("def_tackles_solo", "def_tackle_assists"),
}
OL_SLOT_ORDER = ("LT", "LG", "C", "RG", "RT")
SIDE = {"QB": "O", "RB": "O", "FB": "O", "WR": "O", "TE": "O", "OL": "O",
        "DL": "F", "LB": "F", "DB": "B", "K": "S", "P": "S", "LS": "S"}


def norm(name):
    return re.sub(r"[^a-z]", "", name.lower())


def read(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def branch_control(roster_md):
    """Jacksonville-controlled players (active 53 and practice squad) with position."""
    control = {}
    player_col = pos_col = status_col = None
    for line in roster_md.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            player_col = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if "Player" in cells and "Pos" in cells:
            player_col, pos_col = cells.index("Player"), cells.index("Pos")
            status_col = next((i for i, c in enumerate(cells) if "status" in c.lower()), None)
            continue
        if player_col is None or set(cells[0]) <= {"-", ":"}:
            continue
        if status_col is not None and cells[status_col] in {"Active 53", "Practice squad"}:
            control[cells[player_col]] = cells[pos_col]
    return control


def branch_picks(draftees_md):
    """(overall slot, player) for every Jacksonville branch selection."""
    text = draftees_md.read_text(encoding="utf-8")
    return [(int(slot), name.strip()) for slot, name in
            re.findall(r"^\| April \d+ \| #(\d+) \| ([^|]+?) \|", text, re.M)]


def draft_moves(source, depth, control):
    """[(player gsis id, from club code, to club code, basis)] under the swap rule."""
    real = {int(r["pick"]): r for r in read(source / "draft_picks.csv") if r["season"] == "2013"}
    week1_club = {}
    for row in depth:
        week1_club.setdefault(norm(row["full_name"]), row["club_code"])
    moves = []
    for slot, player in branch_picks(ROOT / "career/2013/offseason/draft/draftees.md"):
        pick = real[slot]
        historical_club = week1_club.get(norm(player))
        if not historical_club or pick["pfr_player_name"] in control:
            continue
        from_club = PROTAGONIST_CODE if pick["team"] == PROTAGONIST_CODE else pick["team"]
        moves.append((pick["gsis_id"], from_club, historical_club,
                      "Draft swap: real #%d pick; Jacksonville took %s there in the branch" % (slot, player)))
    for slot, club in UNTRADED_PICKS.items():
        pick = real[slot]
        moves.append((pick["gsis_id"], PROTAGONIST_CODE, club,
                      "Draft swap: #%d stayed with %s because the branch had no #98 trade" % (slot, club)))
    return moves


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
    if player["roles"]:
        out["roles"] = player["roles"]
    for key in ("slots", "jersey", "gsis_id"):
        if player[key]:
            out[key] = player[key]
    return out


def build(source):
    source = Path(source)
    depth = [r for r in read(source / "depth_charts_2013.csv") if r["week"] == "1" and r["game_type"] == "REG"]
    roster_feed = {(r["team"], r["gsis_id"]) for r in read(source / "roster_weekly_2013.csv")
                   if r["week"] == "1" and r["game_type"] == "REG"}
    injuries = {(r["team"], r["gsis_id"]): r for r in read(source / "injuries_2013.csv")
                if r["week"] == "1" and r["game_type"] == "REG"}
    usage = {r["player_id"]: r for r in read(source / "stats_player_reg_2012.csv")}
    control = branch_control(ROOT / "career/2013/roster.md")
    control_by_norm = {norm(n): (n, p) for n, p in control.items()}

    moves = {gsis: (src, dst, basis) for gsis, src, dst, basis in draft_moves(source, depth, control)}
    moved_found = set()

    # Every listed player once per club, keeping every depth slot. A draft
    # swap re-files the player under his branch club with his real slots.
    listed = collections.OrderedDict()
    for row in depth:
        club = row["club_code"]
        move = moves.get(row["gsis_id"])
        if move and club == move[0]:
            club = move[1]
            moved_found.add(row["gsis_id"])
        if club == PROTAGONIST_CODE:
            continue
        key = (club, row["gsis_id"])
        entry = listed.setdefault(key, {"row": row, "slots": [], "moved": move[2] if move and key[0] == move[1] else None})
        slot = row["depth_position"].strip()
        entry["slots"].append((row["formation"], slot, int(row["depth_team"])))

    name_clubs = collections.defaultdict(set)
    for (code, _), entry in listed.items():
        name_clubs[norm(entry["row"]["full_name"])].add(code)

    clubs, removed_total, cross_check = {}, [], collections.Counter()
    for code, team in CLUBS.items():
        players, changes, notes = [], [], []
        for (club, gsis), entry in listed.items():
            if club != code:
                continue
            row = entry["row"]
            name, listed_position = row["full_name"].strip(), row["position"].strip()
            # Some rows carry a blank slot name. A blank slot counts only when
            # the player has no named slot, and then ranks behind every named one.
            football = [s for s in entry["slots"] if s[0] in {"Offense", "Defense"} and s[1]]
            if not football:
                football = [(f, "", rank + 3) for f, name_, rank in entry["slots"] if f in {"Offense", "Defense"}]
            # A player is filed by the position of his best depth-chart slot
            # when that slot names one (Terrelle Pryor: listed WR, QB1 slot);
            # otherwise by his roster position.
            best_slot = min(football, key=lambda s: s[2])[1] if football else ""
            position = best_slot if group(best_slot) else listed_position
            grp = group(position)
            controlled = control_by_norm.get(norm(name))
            if controlled and SIDE.get(group(controlled[1])) == SIDE.get(grp):
                changes.append("Removed %s (%s): under Jacksonville control in the branch" % (name, position))
                removed_total.append((team, name))
                continue
            player_id = name
            if len(name_clubs[norm(name)]) > 1 or controlled:
                player_id = "%s (%s)" % (name, code)
            real_code = row["club_code"]
            if entry["moved"]:
                changes.append("Added %s (%s): %s" % (name, position, entry["moved"]))
            cross_check["listed" if (ROSTER_CODE.get(real_code, real_code), gsis) in roster_feed else "not_in_roster_feed"] += 1
            report = injuries.get((real_code, gsis), {}).get("report_status", "") or None
            tier = min((s[2] for s in football), default=min(s[2] for s in entry["slots"]) + 3)
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
            stats = usage.get(gsis, {})
            prior = sum(float(stats.get(f) or 0) for f in USAGE_FIELDS.get(grp, ()))
            ol_slot = next((OL_SLOT_ORDER.index(s[1]) for s in football if s[1] in OL_SLOT_ORDER), 9)
            players.append({
                "player_id": player_id, "name": name, "position": position,
                "listed_position": listed_position, "group": grp,
                "available": report not in UNAVAILABLE_REPORT,
                "injury_report": report, "roles": sorted(set(roles)),
                "gsis_id": gsis,
                "jersey": row["jersey_number"],
                "slots": ",".join("%s%d" % (s[1] or s[0][:3].upper(), s[2]) for s in entry["slots"]),
                "_order": (tier, ol_slot, -prior, name),
            })
        for placement in BRANCH_PLACEMENTS.get(team, ()):
            players.append({
                "player_id": placement["name"], "name": placement["name"],
                "position": placement["position"], "listed_position": placement["position"],
                "group": group(placement["position"]),
                "available": True, "injury_report": None, "roles": [],
                "gsis_id": None, "jersey": None, "slots": "",
                "_order": (9, 9, 0, placement["name"]),
            })
            changes.append("Added %s (%s): %s; placed below every listed %s" % (
                placement["name"], placement["position"], placement["basis"], placement["position"]))

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

    unplaced_draft = sorted(basis for gsis, (_, _, basis) in moves.items() if gsis not in moved_found)
    return {
        "schema_version": 1,
        "season": 2013,
        "week": 1,
        "branch_basis": "career/2013/roster.md, September 4, 2013 (Jacksonville active 53 and practice squad)",
        "branch_controlled_players": sorted(control),
        "unplaced_branch_players": list(UNPLACED_CLAIMS),
        "draft_swaps_without_week1_chart": unplaced_draft,
        "sources": {
            "depth_chart": "nflverse depth_charts_2013.csv, week 1, regular season",
            "availability": "nflverse injuries_2013.csv, week 1 report (Friday, September 6, 2013); Out and Doubtful are unavailable",
            "co_starter_order": "nflverse stats_player_reg_2012.csv (2012 regular-season usage)",
            "membership_cross_check": "nflverse roster_weekly_2013.csv, week 1 club membership only; status ignored",
        },
        "cross_check": dict(cross_check),
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
