#!/usr/bin/env python3
"""Rebuild the data-derived part of the 2012 NFL injury calibration.

Research tool only; the runtime never downloads anything. Fetch the inputs
first (they are not committed):

  nflverse official injury reports (primary):
    https://github.com/nflverse/nflverse-data/releases/download/injuries/injuries_2012.csv
  nflverse play-by-play (in-game injury notes, participation footprint, play counts):
    https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2012.csv.gz
  nflverse weekly rosters (jersey -> player -> position map only):
    https://github.com/nflverse/nflverse-data/releases/download/weekly_rosters/roster_weekly_2012.csv

Usage (offline once the files are present):
  python scripts/research/build_2012_injury_calibration.py SOURCE_DIR > out.json

Only 2012 regular-season rows (weeks 1-17) are read. Nothing from 2013 or later
enters the output. The output is the "data" block of
library/data/2012_nfl_injury_calibration.json; the literature block and the
recommended parameters are written by hand in that file and cite this output.

Definitions (also in library/2012_nfl_injury_calibration.md):
  * Report episode: a (player, normalized body part) listed as the primary
    injury on consecutive team reports. Illness, "Not Injury Related" and blank
    rows are excluded.
  * Report onset: the episode's first report is the club's 2nd or later
    regular-season report, and that part was not listed (primary or secondary)
    for the player on the club's previous report. It is attributed to the one
    game between the two reports; denominator = consecutive report pairs (480).
    Week-1 listings are camp/preseason carryovers and are excluded.
  * In-game stoppage: a play-by-play note "TEAM-##-Name was injured during the
    play" (the official gamebook records an injury stoppage). The player is the
    last team-prefixed token before the note, matched to the roster by club,
    week and jersey with a surname check. Denominator = 512 team-games.
  * Exposure plays: run, pass, kickoff, punt, extra point, field goal, kneel,
    spike and snapped no_play rows (timeouts and pre-snap fouls excluded);
    player-plays per team-game = 11 x exposure plays / games.
  * Games missed (severity proxy, footprint players only): the number of the
    club's later regular-season games before the player next appears in any
    play-by-play player-id column for that club. A footprint player appeared in
    at least 75% (and at least 3) of his club's games before the onset.
    Offensive linemen have no reliable footprint and are excluded from this
    proxy. A player not seen again is long_term if 9+ club games remained and
    censored otherwise.
  * The weekly-roster status field (ACT/RES) is not used: for 2012 it is a
    back-filled status (players show RES from Week 1 and only 8 RES remain in
    Week 17), so reserve-list timing cannot be read from it.
"""
from __future__ import annotations

import collections
import csv
import gzip
import json
import re
import sys
from pathlib import Path

GROUPS = {
    "QB": "QB", "RB": "RB", "HB": "RB", "FB": "RB", "WR": "WR", "TE": "TE",
    "T": "OL", "G": "OL", "C": "OL", "OT": "OL", "OG": "OL", "OL": "OL",
    "DE": "DL", "DT": "DL", "NT": "DL", "DL": "DL",
    "LB": "LB", "ILB": "LB", "OLB": "LB", "MLB": "LB",
    "CB": "DB", "DB": "DB", "S": "DB", "SS": "DB", "FS": "DB", "SAF": "DB",
    "K": "K/P/LS", "P": "K/P/LS", "LS": "K/P/LS",
}
GROUP_ORDER = ["QB", "RB", "WR", "TE", "OL", "DL", "LB", "DB", "K/P/LS"]
TEAM = {"ARZ": "ARI", "BLT": "BAL", "CLV": "CLE", "HST": "HOU", "SL": "STL",
        "LA": "STL", "LAC": "SD", "LV": "OAK", "JAC": "JAX"}

HEAD_NECK = {"concussion", "head", "neck", "eye", "ear", "facial lacerations",
             "teeth", "face", "jaw", "stinger"}
UPPER = {"shoulder", "elbow", "hand", "wrist", "thumb", "finger", "forearm",
         "biceps", "triceps", "collarbone", "arm"}
LOWER = {"knee", "knees", "ankle", "hamstring", "foot", "groin", "calf", "hip",
         "thigh", "toe", "quadricep", "achilles", "heel", "shin", "tibia",
         "leg", "glute"}
TRUNK = {"back", "ribs", "rib", "chest", "abdomen", "abdominal", "oblique",
         "pectoral", "tailbone", "pelvis", "throat", "lung contusion",
         "cardiac", "arrhythmia", "other"}
EXCLUDED = {"", "illness", "not injury related"}
CLASSES = ["lower_extremity", "upper_extremity", "trunk_other", "head_neck"]
SEVERITY = ["minor", "short", "multi_week", "long_term"]  # runtime/injuries.py names
NOTE = re.compile(r"was injured during the play\.?"
                  r"(?:\s*(His return is (\w+)|He is (Out)))?")
# The injured player is the LAST "TEAM-##-Name" token before the note. A lazy
# match from the first token misattributes notes whose play text also names a
# team-prefixed player (e.g. "downed by IND-55-J.Hickman. CHI-33-C.Tillman was
# injured"), so the prefix is matched greedily up to the final token.
NOTE_PLAYER = re.compile(r".*\b([A-Z]{2,3})-(\d+)-(\S.*?)\s*$", re.S)


# A no_play row is a snapped (penalty-nullified) play only when the text before
# the penalty describes action. Timeouts and pre-snap fouls (false start, delay
# of game, neutral zone infraction, encroachment...) are not exposure.
SNAPPED = re.compile(r"\b(pass|punts|kicks|sacked|scrambles|left end|right end|"
                     r"left tackle|right tackle|left guard|right guard|up the middle|"
                     r"kneels|spiked|field goal|extra point|FUMBLES|Aborted|onside)\b", re.I)
EXPOSURE_TYPES = ("run", "pass", "kickoff", "punt", "extra_point", "field_goal",
                  "qb_kneel", "qb_spike")


def team(code: str) -> str:
    return TEAM.get(code, code)


def part_of(raw: str) -> str:
    text = (raw or "").strip().lower()
    for side in ("left ", "right "):
        if text.startswith(side):
            text = text[len(side):]
    return text.split("/")[0].strip()


def class_of(part: str) -> str | None:
    if part in EXCLUDED:
        return None
    for name, members in (("head_neck", HEAD_NECK), ("upper_extremity", UPPER),
                          ("lower_extremity", LOWER), ("trunk_other", TRUNK)):
        if part in members:
            return name
    raise SystemExit(f"unmapped body part: {part!r}")


def severity_of(missed: int) -> str:
    return "minor" if missed == 0 else "short" if missed <= 2 else \
        "multi_week" if missed <= 8 else "long_term"


def shares(counter, keys):
    total = sum(counter.get(k, 0) for k in keys)
    return {k: round(counter.get(k, 0) / total, 4) if total else None for k in keys}, total


def main(source: Path) -> dict:
    # ---- inputs ---------------------------------------------------------
    rows = [r for r in csv.DictReader(open(source / "injuries_2012.csv", newline=""))
            if r["season"] == "2012" and r["game_type"] == "REG"]
    roster = [r for r in csv.DictReader(open(source / "roster_weekly_2012.csv", newline=""))
              if r["season"] == "2012" and r["game_type"] == "REG"]
    plays = [r for r in csv.DictReader(gzip.open(source / "play_by_play_2012.csv.gz", "rt"))
             if r["season_type"] == "REG"]
    id_cols = [c for c in plays[0] if c.endswith("player_id") and c != "fantasy_player_id"]

    group_of, jersey = {}, {}
    full_name = {r["gsis_id"]: r["full_name"].lower() for r in roster}
    for r in roster:
        g = GROUPS.get(r["position"]) or GROUPS.get(r["depth_chart_position"])
        if g:
            group_of.setdefault(r["gsis_id"], g)
        if r["jersey_number"]:
            jersey.setdefault((team(r["team"]), int(r["week"]), r["jersey_number"]), []).append(r)
    for r in rows:
        if GROUPS.get(r["position"]):
            group_of.setdefault(r["gsis_id"], GROUPS[r["position"]])

    def jersey_player(club, week, number, name):
        """Roster player for a gamebook token; a club-week can list a number
        twice (e.g. a reserve and an active player), so prefer the surname."""
        cands = jersey.get((club, week, number), [])
        surname = name.split(".", 1)[-1].strip().lower()
        for r in cands:
            if surname and surname in r["full_name"].lower():
                return r["gsis_id"]
        active = [r for r in cands if r["status"] == "ACT"]
        return (active or cands or [{"gsis_id": None}])[-1]["gsis_id"]

    # ---- play-by-play: club schedule, footprint, play counts, notes ------
    games = {}                                  # game_id -> (week, home, away)
    seen = collections.defaultdict(set)         # (club, gsis) -> weeks with a footprint
    play_types = collections.Counter()
    order = collections.defaultdict(list)       # game_id -> [(index, ids)]
    notes = []
    for i, p in enumerate(plays):
        gid, week = p["game_id"], int(p["week"])
        games[gid] = (week, team(p["home_team"]), team(p["away_team"]))
        play_types[p["play_type"] or "(none)"] += 1
        if p["play_type"] == "no_play" and SNAPPED.search(p["desc"].split("PENALTY")[0]):
            play_types["no_play_snapped"] += 1
        ids = {p[c] for c in id_cols if p[c]}
        order[gid].append((i, ids))
        for pid in ids:
            # A footprint is credited to the club listed for that player that week.
            for club in (team(p["home_team"]), team(p["away_team"])):
                seen[(club, pid)].add(week)
        start = 0
        for m in NOTE.finditer(p["desc"]):
            who = NOTE_PLAYER.match(p["desc"][start:m.start()])
            start = m.end()
            club = team(who.group(1))
            pid = jersey_player(club, week, who.group(2), who.group(3))
            disp = m.group(2) or m.group(3) or "(none)"
            surname = who.group(3).split(".", 1)[-1].strip().lower()
            notes.append({"game": gid, "week": week, "club": club, "pid": pid,
                          "name_ok": bool(pid) and surname in full_name.get(pid, ""),
                          "index": i, "play_type": p["play_type"] or "(none)",
                          "side": "possession" if club == team(p["posteam"]) else "other",
                          "disposition": disp})
    team_games = 2 * len(games)
    club_weeks = collections.defaultdict(list)
    for week, home, away in games.values():
        club_weeks[home].append(week)
        club_weeks[away].append(week)
    club_weeks = {c: sorted(ws) for c, ws in club_weeks.items()}

    # footprint: restrict "seen" to weeks the player is on that club's roster
    on_club = collections.defaultdict(set)
    for r in roster:
        on_club[(team(r["team"]), r["gsis_id"])].add(int(r["week"]))
    seen = {k: v & on_club.get(k, set()) for k, v in seen.items()}

    def footprint_player(club, pid, before_week):
        prior = [w for w in club_weeks[club] if w < before_week]
        if len(prior) < 3 or group_of.get(pid) == "OL":
            return False
        hits = len(seen.get((club, pid), set()) & set(prior))
        return hits >= 0.75 * len(prior)

    def games_missed(club, pid, onset_game_week):
        later = [w for w in club_weeks[club] if w > onset_game_week]
        for n, w in enumerate(later):
            if w in seen.get((club, pid), set()):
                return n, False
        return len(later), True

    def severity_record(club, pid, onset_game_week):
        if not footprint_player(club, pid, onset_game_week + 1):
            return None
        missed, never = games_missed(club, pid, onset_game_week)
        if never and missed < 9:
            return "censored"
        return severity_of(missed)

    # ---- official injury report onsets ----------------------------------
    report = collections.defaultdict(dict)
    report_weeks = collections.defaultdict(set)
    for r in rows:
        report_weeks[r["team"]].add(int(r["week"]))
        report[(r["team"], int(r["week"]))][r["gsis_id"]] = r
    report_weeks = {t: sorted(ws) for t, ws in report_weeks.items()}

    def parts(row):
        return {part_of(row["report_primary_injury"]),
                part_of(row["report_secondary_injury"])} - {""}

    onsets, pairs = [], 0
    for club, weeks in report_weeks.items():
        pairs += len(weeks) - 1
        for i in range(1, len(weeks)):
            prev = weeks[i - 1]
            for pid, row in report[(club, weeks[i])].items():
                part = part_of(row["report_primary_injury"])
                klass = class_of(part)
                if klass is None:
                    continue
                prev_row = report[(club, prev)].get(pid)
                if prev_row and part in parts(prev_row):
                    continue
                listed = []
                for w2 in weeks[i:]:
                    r2 = report[(club, w2)].get(pid)
                    if not r2 or part not in parts(r2):
                        break
                    listed.append(r2["report_status"])
                onsets.append({"club": club, "week": weeks[i], "prev": prev, "pid": pid,
                               "group": group_of.get(pid), "class": klass, "part": part,
                               "first_status": listed[0] or "(none)",
                               "listed_out_or_doubtful": sum(s in ("Out", "Doubtful") for s in listed),
                               "severity": severity_record(club, pid, prev)})
    strict, strict_pairs = 0, 0
    for club, weeks in report_weeks.items():
        strict_pairs += max(0, len(weeks) - 2)
        for i in range(2, len(weeks)):
            for pid, row in report[(club, weeks[i])].items():
                part = part_of(row["report_primary_injury"])
                if class_of(part) is None:
                    continue
                if any(report[(club, weeks[j])].get(pid) and
                       part in parts(report[(club, weeks[j])][pid]) for j in (i - 1, i - 2)):
                    continue
                strict += 1

    # ---- in-game stoppage notes -----------------------------------------
    for n in notes:
        n["group"] = group_of.get(n["pid"])
        later = [ids for idx, ids in order[n["game"]] if idx > n["index"]]
        n["returned_same_game"] = any(n["pid"] in ids for ids in later) if n["pid"] else None
        n["footprint"] = bool(n["pid"]) and footprint_player(n["club"], n["pid"], n["week"])
        n["severity"] = severity_record(n["club"], n["pid"], n["week"]) if n["pid"] else None
        nxt = [w for w in report_weeks.get(n["club"], []) if w > n["week"]]
        row = report[(n["club"], nxt[0])].get(n["pid"]) if nxt and n["pid"] else None
        n["next_report_part"] = part_of(row["report_primary_injury"]) if row else None

    # ---- footprint players who vanish without a report listing ---------------
    # A footprint player last seen in club game g, still on the club's weekly
    # roster the next week, with 3+ club games left, never seen again and never
    # listed on a later club report. Candidates for severe injuries placed on
    # reserve before the Wednesday report (upper bound: also benchings).
    listed_after = collections.defaultdict(set)
    for (club, w), players in report.items():
        for pid in players:
            listed_after[(club, pid)].add(w)
    vanish = collections.Counter()
    vanish_group = collections.Counter()
    for (club, pid), weeks_seen in seen.items():
        if not weeks_seen or club not in club_weeks:
            continue
        last = max(weeks_seen)
        later = [w for w in club_weeks[club] if w > last]
        if len(later) < 3 or not footprint_player(club, pid, last + 1):
            continue
        if any(w > last for w in listed_after.get((club, pid), ())):
            continue
        if later[0] not in on_club.get((club, pid), set()):
            continue
        band = "long_term" if len(later) >= 9 else "multi_week_or_longer"
        vanish[band] += 1
        vanish_group[group_of.get(pid)] += 1

    # ---- aggregation -----------------------------------------------------
    n_on = len(onsets)
    by_group = collections.Counter(o["group"] for o in onsets)
    note_group = collections.Counter(n["group"] or "(unmatched)" for n in notes)
    by_class = collections.Counter(o["class"] for o in onsets)
    by_part = collections.Counter(o["part"] for o in onsets)
    class_sh, class_total = shares(by_class, CLASSES)
    sev = collections.Counter(o["severity"] for o in onsets if o["severity"])
    sev_sh, sev_n = shares(sev, SEVERITY)
    sev_by_class = {k: shares(collections.Counter(o["severity"] for o in onsets
                                                  if o["class"] == k and o["severity"]),
                              SEVERITY)[0] for k in CLASSES}
    note_sev = collections.Counter(n["severity"] for n in notes if n["severity"])
    note_sev_sh, note_sev_n = shares(note_sev, SEVERITY)
    footprint_notes = [n for n in notes if n["footprint"]]
    note_parts = collections.Counter(class_of(n["next_report_part"]) or "(excluded)"
                                     for n in notes if n["next_report_part"] is not None)
    note_class_sh, note_class_n = shares(note_parts, CLASSES)
    scrimmage = play_types["run"] + play_types["pass"]
    exposure_plays = sum(play_types[t] for t in EXPOSURE_TYPES) + play_types["no_play_snapped"]
    groups = {}
    for g in GROUP_ORDER:
        groups[g] = {
            "report_onsets": by_group[g],
            "report_onsets_per_team_game": round(by_group[g] / pairs, 4),
            "report_share": round(by_group[g] / n_on, 4),
            "ingame_stoppages": note_group[g],
            "ingame_stoppages_per_team_game": round(note_group[g] / team_games, 4),
            "ingame_share": round(note_group[g] / len(notes), 4),
        }
    return {
        "season": 2012,
        "season_type": "REG weeks 1-17",
        "denominators": {
            "team_games": team_games,
            "report_pairs": pairs,
            "scrimmage_plays_run_pass": scrimmage,
            "play_types": dict(play_types.most_common()),
            "exposure_plays": exposure_plays,
            "player_plays_per_team_game": round(11 * exposure_plays / len(games), 1),
        },
        "report_onsets": {
            "count": n_on,
            "per_team_game": round(n_on / pairs, 4),
            "per_team_game_strict_two_report_rule": round(strict / strict_pairs, 4),
            "first_listed_status": dict(collections.Counter(o["first_status"] for o in onsets)),
            "unmatched_position": by_group[None],
        },
        "ingame_stoppages": {
            "count": len(notes),
            "per_team_game": round(len(notes) / team_games, 4),
            "per_1000_scrimmage_plays_run_pass": round(
                1000 * sum(n["play_type"] in ("run", "pass") for n in notes) / scrimmage, 3),
            "per_1000_kickoffs": round(
                1000 * sum(n["play_type"] == "kickoff" for n in notes) / play_types["kickoff"], 3),
            "per_1000_punts": round(
                1000 * sum(n["play_type"] == "punt" for n in notes) / play_types["punt"], 3),
            "by_play_type": dict(collections.Counter(n["play_type"] for n in notes)),
            "by_side": dict(collections.Counter(n["side"] for n in notes)),
            "announced_disposition": dict(collections.Counter(n["disposition"] for n in notes)),
            "player_matched": sum(bool(n["pid"]) for n in notes),
            "player_matched_surname_agrees": sum(n["name_ok"] for n in notes),
            "footprint_players": len(footprint_notes),
            "footprint_returned_same_game": sum(bool(n["returned_same_game"]) for n in footprint_notes),
            "footprint_return_by_disposition": {
                d: [sum(bool(n["returned_same_game"]) for n in footprint_notes if n["disposition"] == d),
                    sum(1 for n in footprint_notes if n["disposition"] == d)]
                for d in ("Probable", "Questionable", "Doubtful", "Out", "(none)")},
            "on_next_report": sum(1 for n in notes if n["next_report_part"] is not None),
            "next_report_class_shares": note_class_sh,
            "next_report_class_n": note_class_n,
            "severity_shares_footprint": note_sev_sh,
            "severity_n_footprint": note_sev_n,
            "severity_censored": note_sev["censored"],
        },
        "unreported_vanish_upper_bound": {
            "count": sum(vanish.values()),
            "per_team_game": round(sum(vanish.values()) / team_games, 4),
            "by_band": dict(vanish),
            "by_group": {g: vanish_group[g] for g in GROUP_ORDER},
        },
        "by_group": groups,
        "class_shares_report_onsets": class_sh,
        "class_counts_report_onsets": {k: by_class[k] for k in CLASSES},
        "concussion_report_onsets": by_part["concussion"],
        "concussion_share_report_onsets": round(by_part["concussion"] / class_total, 4),
        "top_parts_report_onsets": dict(by_part.most_common(15)),
        "severity_report_onsets_footprint": {
            "shares": sev_sh, "n": sev_n, "censored": sev["censored"],
            "counts": {k: sev[k] for k in SEVERITY},
            "by_class": sev_by_class,
            "definition": "minor 0 games missed; short 1-2; multi_week 3-8; long_term 9+ (incl. not seen again with 9+ club games left)",
        },
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    json.dump(main(Path(sys.argv[1])), sys.stdout, indent=2)
    print()
