#!/usr/bin/env python3
"""Build the 2014 preseason opponent library: Tampa Bay's 90-man camp roster
as it stood for the August 8, 2014 preseason opener at Jacksonville,
reconciled to branch control.

Research tool only; the runtime never downloads anything. The real chart and
roster are not available as a machine feed (nflverse carries no preseason
depth charts, weekly rosters or injury reports for 2014, and the season
roster file lists only players who reached a regular-season roster), so the
club's first unofficial depth chart (released August 5, 2014) and the
July 21 to August 8 transaction log are transcribed below from the dated
public sources named in library/2014_preseason_opponent_rosters.md. The
identity files supply gsis ids, birth dates, jersey numbers and photographs:

  library/data/player_birth_dates.json            (identity registry)
  library/data/2014_week1_depth_charts.json       (Week 1 library: bio fields)
  library/data/player_photos.json                 (open-licensed photographs)
  SOURCE_DIR/players.csv                          (nflverse players, optional)
  SOURCE_DIR/roster_2014.csv                      (nflverse 2014 season rosters, optional:
                                                   jersey numbers of players who reached
                                                   a regular-season roster)

Usage:
  python scripts/research/build_2014_preseason_opponent_rosters.py [SOURCE_DIR] \
      > library/data/2014_preseason_opponent_rosters.json

Read only: the August 5 chart, the transactions through August 8, the
August 8 pregame report, branch control from the 2014 roster and the branch
draft/undrafted pairing. No preseason score, statistic, game participation
or later transaction is an input. The same conventions as the Week 1 builder
(scripts/research/build_2014_week1_depth_charts.py) apply: depth within a
kernel group by chart string, then line slot, then jersey, then name; a
Jacksonville-controlled player is removed and the next man up takes his slot.
"""
import collections
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from runtime.usage import MINIMUM_GAME_DAY, group  # noqa: E402
from scripts.research.build_2014_week1_depth_charts import (  # noqa: E402
    BIO_FIELDS, OL_SLOT_ORDER, SIDE, BIRTH_DATES, ROSTER_MD,
    branch_control, compact, identity, jersey_key, norm,
)

SEASON = 2014
GAME = "preseason-01"
AS_OF = "2014-08-08"
TEAM = "Tampa Bay Buccaneers"
CODE = "TB"
WEEK1_LIBRARY = ROOT / "library/data/2014_week1_depth_charts.json"
PHOTOS = ROOT / "library/data/player_photos.json"
PFR = "https://www.pro-football-reference.com/players/"

# The club's first 2014 unofficial depth chart, released August 5, 2014
# (buccaneers.com "Depth Chart Reflects Ongoing Competition"; SI.com
# August 6 and Bucs Nation August 5 transcriptions; Bleacher Report "2014
# Virtual Program"). Each column is (chart label, kernel-group position of the
# column, [players in listed order]). "Other" entries follow the ranked ones.
# Players under contract on August 8 who do not appear on any available
# transcription are listed under UNLISTED and placed below every listed player
# of their group. Jeremy Grable (SLB4) and Mycal Swaim were on the chart but
# waived/injured August 4, so they are not roster members.
CHART = [
    ("Offense", "QB", "QB", ["Josh McCown", "Mike Glennon", "Mike Kafka", "Alex Tanney"]),
    ("Offense", "RB", "RB", ["Doug Martin", "Bobby Rainey", "Charles Sims", "Mike James", "Jeff Demps"]),
    ("Offense", "FB", "FB", ["Jorvorskie Lane", "Lonnie Pryor", "Ian Thompson"]),
    ("Offense", "WR", "WR", ["Vincent Jackson", "Louis Murphy", "Tommy Streeter", "Robert Herron", "Skye Dawson", "Solomon Patton"]),
    ("Offense", "WR", "WR", ["Chris Owusu", "Mike Evans", "Eric Page", "Lavelle Hawkins", "Russell Shepard"]),
    ("Offense", "TE", "TE", ["Brandon Myers", "Timothy Wright", "Luke Stocker", "Austin Seferian-Jenkins", "Cameron Brate"]),
    ("Offense", "LT", "T", ["Anthony Collins", "Kevin Pamphile", "J.B. Shugarts"]),
    ("Offense", "LG", "G", ["Oniel Cousins", "Kadeem Edwards", "Josh Allen"]),
    ("Offense", "C", "C", ["Evan Dietrich-Smith", "Jace Daniels", "Jason Foster", "Josh Allen", "Andrew Miller"]),
    ("Offense", "RG", "G", ["Jamon Meredith", "Patrick Omameh", "Andrew Miller"]),
    ("Offense", "RT", "T", ["Demar Dotson", "Matt Patchan"]),
    ("Defense", "LDE", "DE", ["Adrian Clayborn", "William Gholston", "Chaz Sutton"]),
    ("Defense", "DT", "DT", ["Gerald McCoy", "Da'Quan Bowers", "Ronald Talley", "Euclid Cummings"]),
    ("Defense", "DT", "DT", ["Clinton McDonald", "Akeem Spence", "Matthew Masifilo", "Jibreel Black"]),
    ("Defense", "RDE", "DE", ["Michael Johnson", "Steven Means", "Scott Solomon"]),
    ("Defense", "SLB", "OLB", ["Jonathan Casillas", "Ka'Lial Glaud", "Nate Askew"]),
    ("Defense", "MLB", "MLB", ["Mason Foster", "Dane Fletcher", "Damaso Munoz"]),
    ("Defense", "WLB", "OLB", ["Lavonte David", "Danny Lansanah", "Brandon Magee"]),
    ("Defense", "LCB", "CB", ["Alterraun Verner", "Rashaan Melvin"]),
    ("Defense", "RCB", "CB", ["Mike Jenkins", "Johnthan Banks", "Deveron Carr", "Keith Lewis", "Anthony Gaitor"]),
    ("Defense", "NB", "CB", ["Leonard Johnson", "Quinton Pointer"]),
    ("Defense", "SS", "SS", ["Mark Barron", "Major Wright", "Bradley McDougald"]),
    ("Defense", "FS", "FS", ["Dashon Goldson", "Keith Tandy", "Kelcie McCray"]),
    ("Special Teams", "PK", "K", ["Connor Barth", "Patrick Murray"]),
    ("Special Teams", "P", "P", ["Michael Koenen"]),
    ("Special Teams", "LS", "LS", ["Andrew DePaola", "Jeremy Cain"]),
    ("Special Teams", "KR", None, ["Eric Page", "Jeff Demps", "Mike James"]),
    ("Special Teams", "PR", None, ["Eric Page", "Bobby Rainey", "Robert Herron", "Skye Dawson"]),
]
# Under contract on August 8, 2014 but on no available transcription of the
# August 5 chart: name -> (position, basis).
UNLISTED = {
    "Ryne Giddins": ("DE", "signed August 4, 2014, after the chart was prepared"),
    "James Ruffin": ("DE", "signed August 4, 2014, after the chart was prepared"),
    "Kip Edwards": ("CB", "signed July 29, 2014; his chart cell was not located in any available transcription"),
    "Danny Gorrer": ("CB", "re-signed March 13, 2014; his chart cell was not located in any available transcription (injured in camp; placed on injured reserve August 25)"),
    "Mark Joyce": ("S", "signed August 3, 2014, after the chart was prepared; waived August 9"),
}
# The chart's long-snapper order was not located; DePaola is listed first
# here only because Cain is removed by branch control (see branch_changes).
LS_ORDER_UNVERIFIED = True

# Rank at which "Other" entries start in a chart column (after the third string).
OTHER_FROM = {"WR": 7, "DT": 4, "RCB": 4}

# Held out of the August 8 game under a pre-game report dated by August 8
# (buccaneers.com "Jacksonville Pregame Report", August 8, 2014; "Camp Notes:
# Verner Easing Back In"; Bucs Nation August 3 and 6 camp notes).
HELD_OUT = {
    "Alterraun Verner": "hamstring; will not play (pregame report, August 8)",
    "Mike Jenkins": "lower-leg (hamstring) injury; will not play (pregame report, August 8)",
    "Dashon Goldson": "held out as planned after offseason foot surgery (pregame report, August 8)",
}

# Transactions July 21 to August 9, 2014 (ESPN and Pro Football Reference
# transaction logs; buccaneers.com and Bucs Nation dated notices). Recorded
# for the reconciliation list; the roster above already reflects them.
TRANSACTIONS = [
    ("2014-07-21", "Signed LB Jeremy Grable (undrafted) and OT J.B. Shugarts"),
    ("2014-07-23", "Claimed LB Brandon Magee off waivers from Cleveland; placed DE Ronald Talley on the active/non-football injury list (activated by August 3)"),
    ("2014-07-27", "Re-signed CB Anthony Gaitor; signed DT Jibreel Black (undrafted); waived WR Quintin Payton and RB Brendan Bigelow"),
    ("2014-07-29", "Signed CB Kip Edwards (ESPN also lists July 31; ProFootballTalk's July 30 notice says the signing was announced with Nicks's release)"),
    ("2014-07-30", "Released G Carl Nicks (mutual parting announced July 25; ESPN lists July 29)"),
    ("2014-08-03", "Signed S Mark Joyce; released WR David Gettis with an injury settlement"),
    ("2014-08-04", "Signed DE Ryne Giddins and DE James Ruffin; waived/injured LB Jeremy Grable and S Mycal Swaim"),
    ("2014-08-09", "Waived S Mark Joyce (after the game; ESPN lists August 12). Not applied: he is a roster member on August 8"),
]


def load_week1_bio():
    """gsis id -> (Week 1 club code, player row); bio fields are club-neutral,
    the jersey is used only when the Week 1 club is Tampa Bay."""
    rows = {}
    for club in json.load(open(WEEK1_LIBRARY, encoding="utf-8"))["clubs"].values():
        for player in club["players"]:
            if player.get("gsis_id"):
                rows[player["gsis_id"]] = (club["code"], player)
    return rows


def load_nflverse(source):
    """gsis id -> (display name, birth date, pfr id) and TB regular-season jerseys."""
    players, jerseys = {}, {}
    if source is None:
        return players, jerseys
    path = Path(source) / "players.csv"
    if path.is_file():
        with open(path, newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                players[row["gsis_id"]] = row
    path = Path(source) / "roster_2014.csv"
    if path.is_file():
        with open(path, newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if row["team"] == CODE and row.get("jersey_number"):
                    jerseys[row["gsis_id"]] = row["jersey_number"]
    return players, jerseys


# Names the registry or nflverse spell differently from the chart.
ALIASES = {"Evan Dietrich-Smith": "Evan Smith", "Timothy Wright": "Tim Wright"}


def build(source=None):
    control = branch_control(ROSTER_MD)
    ids = identity()
    registry = json.load(open(BIRTH_DATES, encoding="utf-8"))["players"]
    week1 = load_week1_bio()
    photos = json.load(open(PHOTOS, encoding="utf-8"))["players"]
    nfl_players, nfl_jerseys = load_nflverse(source)
    nfl_by_name = collections.defaultdict(list)
    for row in nfl_players.values():
        nfl_by_name[norm(row["display_name"])].append(row)

    control_by_gsis, control_by_norm = {}, {}
    for name, (position, reason) in control.items():
        gsis = ids.get(name)
        if gsis:
            control_by_gsis[gsis] = (name, position, reason)
        control_by_norm[norm(name)] = (name, position, reason)

    def lookup(name):
        """gsis id and birth date for a chart name, registry first."""
        for candidate in (name, ALIASES.get(name)):
            if candidate and candidate in registry and registry[candidate].get("gsis_id"):
                return registry[candidate]["gsis_id"], registry[candidate].get("birth_date"), "registry"
        for candidate in (name, ALIASES.get(name)):
            if not candidate:
                continue
            rows = [r for r in nfl_by_name.get(norm(candidate), ())
                    if r.get("rookie_season") and int(r["rookie_season"]) <= SEASON]
            if len(rows) > 1:
                # A namesake who left the league before 2014 (the 2004 Keith
                # Lewis) yields to the one active in 2014.
                rows = [r for r in rows if r.get("last_season") and int(r["last_season"]) >= SEASON]
            if len(rows) == 1:
                return rows[0]["gsis_id"], rows[0].get("birth_date") or None, "nflverse_players"
        return None, None, None

    entries = collections.OrderedDict()
    for column, (formation, label, position, names) in enumerate(CHART):
        for rank, name in enumerate(names, 1):
            entry = entries.setdefault(name, {"name": name, "slots": [], "position": None})
            if position and entry["position"] is None:
                entry["position"] = position
            other = OTHER_FROM.get(label) is not None and rank >= OTHER_FROM[label]
            entry["slots"].append((formation, label, rank, column, other))
    for name, (position, basis) in UNLISTED.items():
        entries[name] = {"name": name, "slots": [], "position": position, "unlisted": basis}

    players, changes, notes, removed, cross = [], [], [], [], collections.Counter()
    for name, entry in entries.items():
        position = entry["position"]
        grp = group(position)
        if grp is None:
            raise SystemExit("unmapped position %r for %s" % (position, name))
        gsis, birth, basis = lookup(name)
        controlled = control_by_gsis.get(gsis) if gsis else None
        if controlled is None and norm(name) in control_by_norm and gsis is None:
            controlled = control_by_norm[norm(name)]
        if controlled:
            changes.append("Removed %s (%s): %s" % (name, position, controlled[2]))
            removed.append(name)
            continue
        football = [s for s in entry["slots"] if s[0] in {"Offense", "Defense"}]
        if football:
            best = min(football, key=lambda s: (s[2], s[3]))
            tier, column = best[2], best[3]
            ol_slot = OL_SLOT_ORDER.index(best[1]) if best[1] in OL_SLOT_ORDER else 9
        elif entry["slots"]:
            best = min(entry["slots"], key=lambda s: (s[2], s[3]))
            tier, ol_slot, column = best[2], 9, best[3]
        else:
            tier, ol_slot, column = 9, 9, 9
            changes.append("Added %s (%s) below every listed %s: %s" % (name, position, grp, entry["unlisted"]))
        roles = []
        for formation, label, rank, _, _ in entry["slots"]:
            if label == "KR" and rank == 1:
                roles.append("kick_return")
            if label == "PR" and rank == 1:
                roles.append("punt_return")
        if grp == "K":
            roles.append("placekicker")
        if grp == "P":
            roles.append("punt")
        slots = ",".join("%s%d" % (s[1], s[2]) for s in entry["slots"])
        week1_code, week1_row = week1.get(gsis, (None, {})) if gsis else (None, {})
        # A Tampa Bay jersey only: the Week 1 number of a player who reached
        # another club (Meredith at Tennessee, McCray at Kansas City) is not
        # his camp number here.
        jersey = nfl_jerseys.get(gsis) or (week1_row.get("jersey") if week1_code == CODE else None) or None
        cross["jersey_nflverse_2014" if nfl_jerseys.get(gsis) else ("jersey_week1_tb" if jersey else "jersey_unknown")] += 1
        cross["gsis_" + (basis or "none")] += 1
        held = HELD_OUT.get(name)
        player = {
            "player_id": name, "name": name, "position": position, "listed_position": position,
            "group": grp, "available": held is None, "injury_report": "Out" if held else None,
            "return_week": None, "roles": sorted(set(roles)), "gsis_id": gsis, "jersey": jersey,
            "slots": slots, "_order": (tier, ol_slot, column, jersey_key(jersey), name),
        }
        if held:
            player["availability_note"] = held
        if birth:
            player["birth_date"] = birth
        for field in BIO_FIELDS:
            if week1_row.get(field) and field != "birth_date":
                player[field] = week1_row[field]
        photo = photos.get(gsis) if gsis else None
        if photo and not player.get("headshot_url"):
            player["headshot_url"] = photo["url"]
            player["headshot_license"] = photo["license"]
            player["headshot_license_url"] = photo["license_url"]
            player["headshot_credit"] = photo["credit"]
            player["headshot_page"] = photo["source_page"]
        if not player.get("page_url") and gsis and nfl_players.get(gsis, {}).get("pfr_id"):
            pfr_id = nfl_players[gsis]["pfr_id"]
            player["page_url"] = "%s%s/%s.htm" % (PFR, pfr_id[0], pfr_id)
        players.append(player)

    by_group = collections.defaultdict(list)
    for player in players:
        by_group[player["group"]].append(player)
    for members in by_group.values():
        for rank, player in enumerate(sorted(members, key=lambda p: p["_order"]), 1):
            player["depth"] = rank
    for player in players:
        del player["_order"]
    players.sort(key=lambda p: (list(SIDE).index(p["group"]), p["depth"]))
    counts = collections.Counter(p["group"] for p in players if p["available"])
    short = {g: need for g, need in MINIMUM_GAME_DAY.items() if counts.get(g, 0) < need}
    if short:
        notes.append("Below the game-day minimum: %s" % ", ".join(
            "%s %d of %d" % (g, counts.get(g, 0), n) for g, n in short.items()))
    notes.append("Next man up after the removals: Rashaan Melvin at LCB (Verner), Andrew DePaola the only long snapper (Cain); Brate's removal leaves four tight ends")
    notes.append("Chart cells not located for Kip Edwards, Danny Gorrer and Mark Joyce; the long-snapper order and the WR column assignments are single-source transcriptions. Jersey numbers are stored only for players who reached a 2014 regular-season roster (Week 1 library or nflverse roster_2014); the camp-only players carry none, so their ties break by name.")
    if LS_ORDER_UNVERIFIED:
        notes.append("Long snapper: the chart order between DePaola and Cain was not located; Cain is removed by branch control, so the order has no effect")

    seen = {}
    for player in players:
        if player.get("gsis_id") in control_by_gsis:
            raise SystemExit("controlled player %s retained" % player["player_id"])
        if player["player_id"] in seen:
            raise SystemExit("duplicate player %s" % player["player_id"])
        seen[player["player_id"]] = True

    def stored(player):
        out = compact(player)
        if player.get("availability_note"):
            out["availability_note"] = player["availability_note"]
        return out

    return {
        "schema_version": 1,
        "season": SEASON,
        "game": GAME,
        "as_of": AS_OF,
        "gate": "gated: usable for the August 8, 2014 preseason game and after. The chart was public August 5, 2014 and the pregame report August 8, 2014; no preseason score, statistic, participation or later transaction is an input.",
        "branch_basis": "career/2014/team/roster/roster.md, August 1, 2014 (78 Jacksonville-controlled players: 74 under contract and four unsigned tenders)",
        "branch_controlled_count": len(control),
        "removed_by_club": {TEAM: removed},
        "transactions_july_21_to_august_9": ["%s: %s" % t for t in TRANSACTIONS],
        "sources": {
            "depth_chart": "Tampa Bay's first 2014 unofficial depth chart, released August 5, 2014: buccaneers.com 'Depth Chart Reflects Ongoing Competition' (August 5), si.com 'Tampa Bay Buccaneers release depth chart: Mike Evans behind Chris Owusu' (August 6), bucsnation.com 'Buccaneers Depth Chart: Observations and Reaction' (August 5), bleacherreport.com 'Buccaneers 2014 Virtual Program' (August 2014); transcribed from search-engine extracts because the pages themselves were not reachable from this session (see the record's limits)",
            "roster_membership": "the chart's listed players plus the dated transaction log (ESPN and Pro Football Reference 2014 transaction pages; buccaneers.com and bucsnation.com notices), with later arrivals (Larry English August 13, Rishaw Johnson August 21, Marc Anthony and Jeremiah Warren August 25, Logan Mankins August 26, Garrett Gilkey August 31, Brandon Dixon September 6) excluded by their dates",
            "availability": "buccaneers.com 'Jacksonville Pregame Report' (August 8, 2014) and 'Camp Notes: Verner Easing Back In'; bucsnation.com camp notes of August 3 and 6, 2014. Only players reported as not playing are unavailable; practice absences alone do not make a player unavailable",
            "co_listed_order": "chart string, then line slot LT-LG-C-RG-RT, then chart column, then jersey number, then name (the Week 1 rule); unlisted players rank below every listed player of their group",
            "identity": "library/data/player_birth_dates.json, then nflverse players.csv (single 2014-active match by name); jersey from the Week 1 library or nflverse roster_2014.csv; photographs from library/data/player_photos.json; page_url from the Week 1 library or the nflverse pfr id",
            "branch_control": "career/2014/team/roster/roster.md matched by gsis id through the identity registry and the league database, as in the Week 1 build",
            "draft_and_undrafted_pairing": "career/2014/league/personnel/draft_pairing.md and career/2014/draft/udfa_signings.md",
            "trades_and_free_agency": "career/2014/trades/completed_trades/trades.md, career/2014/free_agency/signings.md, career/2014/league/personnel/fa_draws.md",
            "retirements": "career/2014/league/personnel/retirements.md (none affecting Tampa Bay by August 8, 2014)",
        },
        "cross_check": dict(sorted(cross.items())),
        "clubs": {TEAM: {"code": CODE, "branch_changes": changes, "notes": notes,
                         "players": [stored(p) for p in players]}},
    }


def dumps(library):
    lines = ["{"]
    for key, value in library.items():
        if key == "clubs":
            continue
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
    if len(sys.argv) > 2:
        sys.exit(__doc__)
    sys.stdout.write(dumps(build(sys.argv[1] if len(sys.argv) == 2 else None)))


if __name__ == "__main__":
    main()
