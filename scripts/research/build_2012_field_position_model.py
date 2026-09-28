#!/usr/bin/env python3
"""Rebuild the 2012 NFL field-position drive model used by kernel 2013.7.

Research tool only; the runtime never downloads or parses play-by-play. The
inputs are the same SHA-pinned files as build_2012_drive_model.py (fetch them
into .sim_cache/sources/ first), plus the nflverse 2012 roster for the
quarterback-rush denominator of the scramble share:

  nflverse play-by-play (primary pass):
    https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2012.csv.gz
  nflscrapR play-by-play (second pass):
    https://raw.githubusercontent.com/ryurko/nflscrapR-data/master/play_by_play_data/regular_season/reg_pbp_2012.csv
  nflverse 2012 rosters (position map only):
    https://github.com/nflverse/nflverse-data/releases/download/rosters/roster_2012.csv

Usage:
  python scripts/research/build_2012_field_position_model.py [--sources DIR] [--out PATH] [--check]

--check rebuilds in memory and exits non-zero unless the committed artifact is
reproduced byte-for-byte. Standard library only; deterministic. Only 2012
regular-season plays are read, and the artifact holds no team or game
identifiers.

The drive grouping, offensive-snap test and result classifier are imported
from build_2012_drive_model.py (rows, is_off, classify), so the 5,984 drives
and their categories are the kernel 2013.6 drives; the builder fails unless
the category counts equal the committed 2013.6 artifact's. The drive model
builder and its artifact are not modified.

Both play-by-play files derive from the NFL Game Statistics and Information
System (GSIS) feed, so the second pass verifies the parse and the classifier,
not an independent observation of the season. Any count differing by more
than 1%, any share by more than one percentage point or any mean by more than
0.6 yards fails the build unless it is listed in EXPLAINED.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from build_2012_drive_model import (  # noqa: E402  (same classifier as kernel 2013.6)
    INPUTS, SCRIMMAGE, classify, clock_seconds, is_off, rows, sha256,
)

ROOT = HERE.parents[1]
DEFAULT_SOURCES = ROOT / ".sim_cache" / "sources"
DEFAULT_OUT = ROOT / "library" / "data" / "2012_nfl_field_position_model.json"
DRIVE_MODEL = ROOT / "library" / "data" / "2012_nfl_drive_model.json"
USAGE = ROOT / "library" / "data" / "2012_nfl_position_usage_baseline.json"
ROSTER = {
    "file": "roster_2012.csv",
    "url": "https://github.com/nflverse/nflverse-data/releases/download/rosters/roster_2012.csv",
    "sha256": "90628fcdadd9f2dde083bc77d41139cedc9fefd1fcc09f2ce8675823de23291b",
}

SCHEMA = "2012-nfl-field-position-model-v2"
CATEGORIES = (
    "touchdown", "field_goal_attempt", "punt", "interception",
    "fumble_lost", "downs", "safety", "clock",
)
TEAM_GAMES = 512
EXPECTED_DRIVES = 5984

# ---- pre-registration (fixed before any 2013.7 game was resolved) -----------
START_BINS = ((90, 99), (81, 89), (80, 80), (70, 79), (60, 69), (50, 59),
              (40, 49), (30, 39), (20, 29), (1, 19))
ZONES = (("A", 80, 99), ("B", 50, 79), ("C", 1, 49))
NEUTRAL_H2_SECONDS = 600          # H2 drives starting with more than this are neutral
LATE_TIME = (("301-600", 301, 600), ("121-300", 121, 300), ("le120", 0, 120))
NEEDS = (("trail9", -999, -9), ("trail4_8", -8, -4), ("trail1_3", -3, -1),
         ("tied", 0, 0), ("lead1_8", 1, 8), ("lead9", 9, 999))
MIN_CELL = 30
H1_BUCKET_EDGES = ((0, 30), (31, 60), (61, 120), (121, 240), (241, 1800))  # 2013.6 edges
TERM_BUCKETS = ("le120", "121-300", "301-600", "gt600", "OT")
K_TRANSITION = 20                 # nearest-record draw width for punts and turnovers
DECISION_ZONES = (("own_half", 50, 99), ("opp_49_35", 35, 49), ("opp_34_1", 1, 34))
PUNT_NET_BINS = (("own 1-10", 90, 99), ("own 11-20", 80, 89), ("own 21-30", 70, 79),
                 ("own 31-40", 60, 69), ("own 41-50", 50, 59), ("opp 49-40", 40, 49),
                 ("opp 39-30", 30, 39))
COARSE_STARTS = (("own 1-20", 80, 99), ("own 21-50", 50, 79), ("opp 49-1", 1, 49))
POINTS_BINS = ((90, 99), (80, 89), (70, 79), (60, 69), (50, 59), (40, 49), (30, 39), (20, 29), (1, 19))
FG_OFFSETS = (17, 18, 19)

TUPLE_FIELDS = (
    "plays", "net0", "seconds", "start", "end", "t0", "score_diff", "final",
    "term_bucket", "term_down", "term_ydstogo", "chains", "kneel_yards", "spikes",
    "fg_distance", "fg_made", "fg_blocked", "safety_term_kind", "safety_term_los",
    "runs", "attempts", "sacks", "td_kind",
    # Kernel 2014.1: charged timeouts at the drive's first snap and used during it.
    "off_timeouts", "def_timeouts", "off_timeouts_used", "def_timeouts_used",
)
CHAIN_FIELDS = ("scrimmage_first_downs", "penalty_first_downs", "third_down_attempts",
                "third_down_conversions", "fourth_down_attempts", "fourth_down_conversions")
KICK_FIELDS = ("touchback", "next_start", "kick_yards", "return_yards", "enforcement", "outcome")
PUNT_FIELDS = ("los", "outcome", "gross", "return_yards", "enforcement", "next_start", "touchback")
TURNOVER_FIELDS = ("end", "next_start", "return_yards", "touchback", "delta")

COUNT_TOLERANCE = 0.01
SHARE_TOLERANCE = 0.01
MEAN_TOLERANCE = 0.6

# Second-pass deviations explained by coding differences in the nflscrapR
# file (each confirmed during research or recomputed by this builder).
EXPLAINED = {
    "score_rebuild": "nflscrapR is missing 115 extra-point rows; the running score is rebuilt from each file's own scoring rows with an imputed made try after an offensive or return touchdown that has no try row, so score-state cells can differ by a few drives. nflscrapR's own score_differential column is not used.",
    "punt_rows": "nflscrapR has 11 fewer punt rows than nflverse, so a few punt drives lose their terminal play and the punt pool is smaller.",
    "scramble": "The qb_scramble flag follows the GSIS play description; nflverse (681 of 1,223 quarterback rushes) and nflscrapR (643) carry different description revisions. nflverse is used; the scramble share is informational.",
    "duplicate_td": "nflscrapR repeats one touchdown description (2012112200, plays 2563 and 2658, the second with a penalty appended).",
    "trail1_3_le120": "The trail 1-3 <=120 s late cell holds 30 drives in nflverse and 29 in nflscrapR (score rebuild); the nflverse cell map is used for both passes without re-collapse.",
    "late_punt_share": "Late trailing punt shares use the rebuilt score in both files; nflscrapR's differ through the score rebuild (imputed tries) and its missing punt rows.",
    "spikes": "nflscrapR codes two spikes (2012092304 play 4391, 2012111810 play 2332) as ordinary incomplete passes; nflverse codes them qb_spike. Pass-attempt totals are unaffected.",
    "timeouts": "The timeout counters are GSIS fields coded differently by the two parses. On the 5,940 drives matched across files (club, first play id, clock, start), the starting counts differ on 36 drives for the defence and 32 for the offence, almost always by one timeout with nflverse one lower; nflverse carries 30 more timeout rows (1,878 against 1,848). Both files are equally self-consistent: in each, 5,247 of 5,276 same-half possession changes carry both clubs' counts exactly (start minus timeouts used equals the next drive's start). The gap is under 1% per drive and exceeds the count tolerance only in the small zero-timeout buckets. nflverse is used.",
}
# Metrics whose second-pass deviation each explanation covers.
EXPLAINED_METRICS = {
    "punt_pool": "punt_rows", "category:punt": "punt_rows", "category:other": "punt_rows",
    "scrambles": "scramble", "late:le120|trail1_3": "trail1_3_le120",
    "late_punt_share_last5": "late_punt_share", "late_punt_share_le120": "late_punt_share",
    "late_punt_n_last5": "late_punt_share", "late_punt_n_le120": "late_punt_share",
    "late:le120|trail4_8": "score_rebuild", "late:le120|trail9": "score_rebuild",
    "late:121-300|trail1_3": "score_rebuild", "late:121-300|tied": "score_rebuild",
    "late:301-600|tied": "score_rebuild", "late:le120|tied": "score_rebuild",
    "spikes": "spikes",
    "timeouts:def_start_0": "timeouts", "timeouts:off_start_0": "timeouts",
    "timeouts:def_used": "timeouts", "timeouts:off_used": "timeouts",
    "timeouts:def_start_1": "timeouts", "timeouts:off_start_1": "timeouts",
    "timeouts:def_start_2": "timeouts", "timeouts:off_start_2": "timeouts",
    "timeouts:def_start_3": "timeouts", "timeouts:off_start_3": "timeouts",
}
# A late score-state cell may differ between the passes only through the score
# rebuild: its need-free time-bucket totals (late_time:*) must still agree.
LATE_CELL_EXPLANATION = "score_rebuild"

STR_COLS = (
    "game_id", "posteam", "defteam", "game_half", "play_type", "desc", "field_goal_result",
    "extra_point_result", "two_point_conv_result", "td_team", "kickoff_returner_player_id",
    "kickoff_returner_player_name", "punt_returner_player_id", "rusher_player_id",
    "drive_time_of_possession", "timeout_team",
)
RAW_COLS = (  # kept as source strings: the imported classifier reads them
    "two_point_attempt", "touchdown", "safety", "interception", "fumble_lost",
    "fourth_down_failed",
)
NUM_COLS = ("play_id", "yardline_100", "qtr", "down", "ydstogo", "yards_gained",
            "quarter_seconds_remaining", "half_seconds_remaining", "kick_distance", "return_yards",
            "posteam_timeouts_remaining", "defteam_timeouts_remaining", "timeout")
FLAG_COLS = ("fourth_down_converted", "third_down_converted", "third_down_failed",
             "first_down_rush", "first_down_pass", "first_down_penalty", "sack", "qb_scramble",
             "punt_blocked", "touchback", "kickoff_attempt", "pass_touchdown", "rush_touchdown")

KICK_YDS = re.compile(r"(?:kicks|punts)(?: onside)? (-?\d+) yards?")
FG_YDS = re.compile(r"(\d+) yard field goal")
ALIAS = {"JAC": "JAX", "SD": "LAC", "OAK": "LV", "STL": "LA", "SL": "LA"}


def alias(team):
    return ALIAS.get(team, team)


def _num(value):
    try:
        return float(value) if value != "" else None
    except ValueError:
        return None


def _flag(value):
    try:
        return int(float(value)) if value != "" else 0
    except ValueError:
        return 0


def load(path, source):
    """Projected 2012 REG rows in file order (the imported reader filters REG)."""
    key = INPUTS[source]["drive_key"]
    out = []
    for r in rows(path, source):
        row = {k: r.get(k, "") for k in STR_COLS + RAW_COLS}
        for k in NUM_COLS:
            row[k] = _num(r.get(k, ""))
        for k in FLAG_COLS:
            row[k] = _flag(r.get(k, ""))
        row["drive_key"] = r.get(key, "") or ""
        out.append(row)
    return out


def games(all_rows):
    out = collections.OrderedDict()
    for r in all_rows:
        out.setdefault(r["game_id"], []).append(r)
    for plays in out.values():
        for index, r in enumerate(plays):
            r["gi"] = index
    return out


def flag(r, k):
    value = r.get(k)
    return (value == 1) if isinstance(value, int) else _flag(value or "") == 1


def is_kick_row(r):
    d = r["desc"]
    return r["play_type"] == "kickoff" or r["kickoff_attempt"] == 1 or " kicks " in d or "kicks onside" in d


def kick_yards(r):
    m = KICK_YDS.search(r["desc"])
    return int(m.group(1)) if m else None


def fg_distance(r):
    if r["kick_distance"] is not None:
        return int(r["kick_distance"])
    m = FG_YDS.search(r["desc"])
    return int(m.group(1)) if m else None


def kick_spot_own(r):
    m = re.search(r"from ([A-Z]{2,3}) (-?\d+)", r["desc"])
    if not m:
        return 50 if re.search(r"from (?:MID)?\s*50", r["desc"]) else None
    side, yard = alias(m.group(1)), int(m.group(2))
    if yard == 50:
        return 50
    return yard if side == alias(r["defteam"]) else 100 - yard


def punt_outcome(r):
    d = r["desc"].upper()
    if r["punt_blocked"] == 1 or "BLOCKED" in d:
        return "blocked"
    if flag(r, "touchdown") and r["td_team"] and r["td_team"] != r["posteam"]:
        return "return_td"
    if "MUFF" in d:
        return "muffed"
    if r["touchback"] == 1 or "TOUCHBACK" in d:
        return "touchback"
    if "FAIR CATCH" in d:
        return "fair_catch"
    if r["punt_returner_player_id"]:
        return "returned"
    if "OUT OF BOUNDS" in d:
        return "out_of_bounds"
    if "DOWNED" in d:
        return "downed"
    return "other"


def kickoff_outcome(r):
    d = r["desc"].upper()
    if "ONSIDE" in d:
        return "onside"
    if flag(r, "touchdown"):
        return "return_td"
    if r["touchback"] == 1 or "TOUCHBACK" in d:
        return "touchback"
    if "OUT OF BOUNDS" in d and not (r["kickoff_returner_player_id"] or r["kickoff_returner_player_name"]):
        return "out_of_bounds"
    if "MUFF" in d:
        return "muffed"
    if "FAIR CATCH" in d:
        return "fair_catch"
    if (r["kickoff_returner_player_id"] or r["kickoff_returner_player_name"]
            or re.search(r"for -?\d+ yards?|for no gain", r["desc"])):
        return "returned"
    if "DOWNED" in d:
        return "downed"
    return "other"


def annotate_scores(all_rows):
    """Pre-snap score differential (offense perspective) rebuilt from scoring
    rows, identically in both files: TD +6 to td_team, good XP +1 and two-point
    success +2 to the try team, made FG +3, safety +2 to the defence. A touchdown
    followed by a live snap with no try row gets an imputed made try (nflscrapR
    lacks 115 extra-point rows). Returns the number of imputed tries."""
    imputed = 0
    for plays in games(all_rows).values():
        score = collections.Counter()
        pending = None
        for r in plays:
            is_try = bool(r["extra_point_result"] or r["two_point_conv_result"])
            live = r["play_type"] in ("kickoff", "pass", "run", "punt", "field_goal", "qb_kneel", "qb_spike")
            if pending and live and not is_try:
                score[pending] += 1
                imputed += 1
                pending = None
            pos, dfn = alias(r["posteam"]), alias(r["defteam"])
            r["sd"] = (score[pos] - score[dfn]) if pos and dfn else None
            if is_try:
                pending = None
                score[pos] += (r["extra_point_result"] == "good") + 2 * (r["two_point_conv_result"] == "success")
                continue
            if flag(r, "touchdown") and r["td_team"] and (r["play_type"] != "no_play" or is_off(r)):
                score[alias(r["td_team"])] += 6
                pending = alias(r["td_team"])
            if r["field_goal_result"] == "made":
                score[pos] += 3
            if flag(r, "safety") and dfn:
                score[dfn] += 2
    return imputed


def build_drives(all_rows):
    """Offensive drives per game: the build_2012_drive_model.extract grouping
    and classifier, plus the rows needed for field position and transitions."""
    drives = []
    for gid, plays in games(all_rows).items():
        groups = collections.OrderedDict()
        for r in plays:
            groups.setdefault(r["drive_key"], []).append(r)
        offensive = []
        for grp in groups.values():
            teams = collections.Counter(r["posteam"] for r in grp if is_off(r) and r["posteam"])
            if not teams:
                continue
            pos = teams.most_common(1)[0][0]
            offs = [r for r in grp if is_off(r, pos)]
            if offs:
                offensive.append({"posteam": pos, "plays": grp, "offs": offs, "half": offs[-1]["game_half"]})
        game_drives = []
        for i, d in enumerate(offensive):
            last_in_half = i + 1 == len(offensive) or offensive[i + 1]["half"] != d["half"]
            pos, offs = d["posteam"], d["offs"]
            raw, category, remap = classify(offs, pos, last_in_half)
            snaps = [r for r in d["plays"] if r["posteam"] == pos and (is_off(r) or r["play_type"] == "no_play")]
            first_fp = next((r for r in snaps if not is_kick_row(r)), offs[0])
            game_drives.append({
                "posteam": pos, "raw": raw, "category": category, "remap": remap,
                "half": d["half"], "final": last_in_half, "offs": offs, "rows": d["plays"],
                "own": [r for r in d["plays"] if r["posteam"] == pos],
                "first": first_fp, "terminal": offs[-1], "game_rows": plays,
                "first_gi": first_fp["gi"], "last_off_gi": offs[-1]["gi"],
            })
        for i, drv in enumerate(game_drives):
            drv["prev"] = game_drives[i - 1] if i else None
        drives.extend(game_drives)
    return drives


def start_type(drive):
    """How a drive's possession began (research common.start_type, ported)."""
    prev = drive["prev"]
    lo = prev["last_off_gi"] + 1 if prev else 0
    between = drive["game_rows"][lo:drive["first_gi"]]
    kicks = [r for r in between if is_kick_row(r)]
    boundary = None if prev is None or prev["half"] == drive["half"] else "half_start"
    if prev is None:
        boundary = "game_start"
    if kicks:
        k = ([r for r in kicks if r["play_type"] != "no_play"] or kicks)[-1]
        safety_before = (prev is not None and prev["category"] == "safety") or any(flag(r, "safety") for r in between)
        detail = {"kick_row": k, "boundary": boundary,
                  "recovered_by_kicking_team": drive["posteam"] == k["defteam"] != k["posteam"]}
        if safety_before and boundary is None:
            return "safety_free_kick", detail
        if "ONSIDE" in k["desc"].upper():
            return "onside_kick", detail
        return "kickoff", detail
    if prev is None:
        return "no_kick_game_start", {}
    if boundary:
        return "half_start_no_kick", {}
    if prev["posteam"] == drive["posteam"]:
        return "same_team_continuation", {}
    if prev["raw"] == "opp_touchdown":
        return "after_opp_touchdown_no_kick", {}
    category = prev["category"]
    if category == "punt":
        return "punt", {}
    if category == "field_goal_attempt":
        result = prev["terminal"]["field_goal_result"]
        return {"blocked": "blocked_fg", "made": "made_fg_no_kick"}.get(result, "missed_fg"), {}
    if category in ("interception", "fumble_lost", "downs"):
        return category, {}
    return "other:" + category, {}


def bin_index(y, bins=START_BINS):
    for index, (low, high) in enumerate(bins):
        if low <= y <= high:
            return index
    return None


def zone_of(y):
    return next(label for label, low, high in ZONES if low <= y <= high)


def need_of(diff):
    return next(label for label, low, high in NEEDS if low <= diff <= high)


def time_label(seconds):
    return next(label for label, low, high in LATE_TIME if low <= seconds <= high)


def term_bucket(r):
    qtr = r["qtr"] or 0
    if qtr >= 5:
        return "OT"
    if qtr < 4 or r["quarter_seconds_remaining"] is None:
        return "gt600"
    s = r["quarter_seconds_remaining"]
    return "le120" if s <= 120 else ("121-300" if s <= 300 else ("301-600" if s <= 600 else "gt600"))


def h1_bucket(seconds):
    return next(i for i, (low, high) in enumerate(H1_BUCKET_EDGES) if seconds <= high)


def describe(values):
    n = len(values)
    if not n:
        return {"n": 0, "mean": None, "sd": None}
    mean = sum(values) / n
    sd = math.sqrt(sum((v - mean) ** 2 for v in values) / n)
    return {"n": n, "mean": round(mean, 4), "sd": round(sd, 4)}


def extract(path, source, positions):
    """Per-drive field-position records and transition pools for one file."""
    all_rows = load(path, source)
    imputed = annotate_scores(all_rows)
    drives = build_drives(all_rows)
    corrections = collections.Counter()
    for d in drives:
        t, first = d["terminal"], d["first"]
        category = d["category"]
        d["start"] = int(round(first["yardline_100"]))
        d["corrected_start"] = d["start"] != int(round(
            next((r for r in d["rows"] if r["posteam"] == d["posteam"]
                  and (is_off(r) or r["play_type"] == "no_play")), first)["yardline_100"]))
        if category == "touchdown":
            end = 0
        elif category == "safety":
            end = 100
        elif t["play_type"] in ("punt", "field_goal"):
            end = int(round(t["yardline_100"]))
        else:
            end = int(round((t["yardline_100"] or 0) - (t["yards_gained"] or 0)))
        d["fg"] = None
        if category == "field_goal_attempt":
            distance = fg_distance(t)
            if distance - end not in FG_OFFSETS:
                corrections["fg_offset"] += 1
                d["fg_offset_corrected"] = [distance, distance - end]
                end = distance - 18
            d["fg"] = [distance, int(t["field_goal_result"] == "made"), int(t["field_goal_result"] == "blocked")]
        d["end"] = end
        d["net0"] = d["start"] - end
        d["plays"] = sum(1 for r in d["offs"] if r["play_type"] in SCRIMMAGE)
        d["runs"] = sum(1 for r in d["offs"] if r["play_type"] == "run")
        d["sacks"] = sum(1 for r in d["offs"] if r["play_type"] == "pass" and r["sack"] == 1)
        d["attempts"] = sum(1 for r in d["offs"] if r["play_type"] == "pass" and r["sack"] != 1)
        d["kneel_yards"] = [int(r["yards_gained"] or 0) for r in d["offs"] if r["play_type"] == "qb_kneel"]
        d["spikes"] = sum(1 for r in d["offs"] if r["play_type"] == "qb_spike")
        # Charged timeouts: each club's count at the first snap, and the
        # timeout rows of the drive by the calling club (timeout_team).
        off0, def0 = first.get("posteam_timeouts_remaining"), first.get("defteam_timeouts_remaining")
        d["off_timeouts"] = None if off0 is None else int(off0)
        d["def_timeouts"] = None if def0 is None else int(def0)
        called = [r.get("timeout_team") or "" for r in d["rows"] if r.get("timeout") == 1]
        pos_alias = ALIAS.get(d["posteam"], d["posteam"])
        d["off_timeouts_used"] = sum(1 for team in called if team and ALIAS.get(team, team) == pos_alias)
        d["def_timeouts_used"] = sum(1 for team in called if team and ALIAS.get(team, team) != pos_alias)
        d["seconds"] = clock_seconds(d["rows"][-1].get("drive_time_of_possession", "")) if source == "nflverse" else None
        d["t0"] = int(first["quarter_seconds_remaining"] if (first["qtr"] or 0) >= 5 else first["half_seconds_remaining"])
        d["score_diff"] = first.get("sd")
        d["term_bucket"] = term_bucket(t)
        d["term_down"] = int(t["down"]) if category in ("punt", "field_goal_attempt", "downs") and t["down"] else None
        d["term_ydstogo"] = (int(t["ydstogo"]) if category in ("punt", "field_goal_attempt", "downs")
                             and t["ydstogo"] is not None else None)
        own = d["own"]
        d["chains"] = [
            sum(r["first_down_rush"] + r["first_down_pass"] for r in own),
            sum(r["first_down_penalty"] for r in own),
            sum(r["third_down_converted"] + r["third_down_failed"] for r in own),
            sum(r["third_down_converted"] for r in own),
            sum(r["fourth_down_converted"] + flag(r, "fourth_down_failed") for r in own),
            sum(r["fourth_down_converted"] for r in own),
        ]
        d["td_kind"] = None
        d["renderable"] = True
        if category == "touchdown":
            if t["play_type"] == "pass" and t["sack"] != 1:
                d["td_kind"] = "pass"
            elif t["play_type"] == "run":
                d["td_kind"] = "rush"
            else:
                d["renderable"] = False
                corrections["touchdown_not_scrimmage"] += 1
        d["safety_term"] = None
        if category == "safety":
            kind = "sack" if t["play_type"] == "pass" and t["sack"] == 1 else (
                "run" if t["play_type"] == "run" and (t["yards_gained"] or 0) < 0 else None)
            if kind:
                d["safety_term"] = [kind, int(round(t["yardline_100"]))]
            else:
                d["renderable"] = False
                corrections["safety_not_renderable"] += 1
        if category in ("touchdown", "interception", "fumble_lost", "downs") and d["plays"] == 0:
            d["renderable"] = False
            corrections["zero_play_terminal"] += 1
    # Seconds: nflverse drive time of possession; blank -> plays x category pace
    # (the 2013.6 rule, so the 2013.6 clock_scale applies unchanged).
    if source == "nflverse":
        pace = {}
        for category in CATEGORIES:
            timed = [d for d in drives if d["category"] == category and d["seconds"] is not None]
            pace[category] = (sum(d["seconds"] for d in timed), sum(d["plays"] for d in timed))
        for d in drives:
            if d["seconds"] is None:
                total, plays = pace[d["category"]]
                d["seconds"] = int(round(d["plays"] * total / plays)) if plays else 0
    # Transitions: how each possession began, from the rows between drives.
    kick_pool, free_kicks, punts = [], [], []
    turnovers = {"interception": [], "fumble_lost": []}
    kinds = collections.Counter()
    tb_parse = {"interception": [0, 0], "fumble_lost": [0, 0]}
    for d in drives:
        kind, det = start_type(d)
        d["start_kind"] = kind
        kinds[kind] += 1
        nxt = d["start"]
        if kind in ("kickoff", "safety_free_kick") and not det.get("recovered_by_kicking_team"):
            k = det["kick_row"]
            outcome = kickoff_outcome(k)
            spot = kick_spot_own(k)
            if outcome in ("onside", "return_td") or spot != (35 if kind == "kickoff" else 20):
                continue
            touchback = outcome == "touchback"
            kick = kick_yards(k) or 0
            ret = 0 if touchback else int(k["return_yards"] or 0)
            e = nxt - 80 if touchback else nxt - (spot + kick - ret)
            record = [int(touchback), nxt, kick, ret, e, outcome]
            (kick_pool if kind == "kickoff" else free_kicks).append(record)
        elif kind == "punt":
            t = d["prev"]["terminal"]
            los = int(round(t["yardline_100"]))
            outcome = punt_outcome(t)
            gross = kick_yards(t) or 0
            ret = int(t["return_yards"] or 0)
            touchback = outcome == "touchback"
            e = nxt - 80 if touchback else nxt - (100 - los + gross - ret)
            punts.append([los, outcome, gross, ret, e, nxt, int(touchback)])
        elif kind in turnovers:
            prev = d["prev"]
            t = prev["terminal"]
            end = prev["end"]
            touchback = "TOUCHBACK" in t["desc"].upper()
            tb_parse[kind][0] += touchback
            tb_parse[kind][1] += touchback and nxt == 80
            ret = int(t["return_yards"] or 0)
            turnovers[kind].append([end, nxt, ret, int(touchback), nxt - (100 - end)])
    # Punt and turnover pools are ordered by line of scrimmage (end spot) only;
    # the sort is stable, so records at the same spot keep season order (file
    # order), which is outcome-neutral. The kernel's "20 nearest, ties by
    # index" draw depends on that order; an outcome-sorted order would bias it.
    punts.sort(key=lambda r: r[0])
    for pool in turnovers.values():
        pool.sort(key=lambda r: r[0])
    for kind in turnovers:
        tb_parse[kind].append(sum(1 for d in drives if d["category"] == kind
                                  and "TOUCHBACK" in d["terminal"]["desc"].upper()))
    # Scrambles over quarterback rushes (kneels excluded; rushes with a rusher id).
    qb_rushes = scrambles = 0
    for r in all_rows:
        if r["play_type"] == "run" and r["rusher_player_id"]:
            if positions.get(r["rusher_player_id"]) == "QB":
                qb_rushes += 1
        if r["play_type"] == "run" and r["qb_scramble"] == 1:
            scrambles += 1
    return {
        "source": source, "games": len(games(all_rows)), "drives": drives, "imputed_tries": imputed,
        "kickoff_pool": kick_pool, "free_kick_pool": free_kicks, "punt_pool": punts,
        "interception_pool": turnovers["interception"], "fumble_pool": turnovers["fumble_lost"],
        "start_kinds": dict(sorted(kinds.items())), "turnover_touchbacks": tb_parse,
        "scramble": [scrambles, qb_rushes], "corrections": dict(corrections),
    }


def regime(d):
    """Partition of one 2012 drive (pre-registered)."""
    if d["half"] == "Overtime":
        return "ot"
    if d["half"] == "Half2" and d["t0"] <= NEUTRAL_H2_SECONDS:
        return "late"
    if d["half"] == "Half1" and d["final"]:
        return "h1_final"
    return "neutral"


def collapse_late(counts):
    """cell_map {time|need: cell id}: a thin cell merges into the adjacent
    later time bucket; a thin <=120 bucket merges into the adjacent earlier
    one; repeated until no cell is under MIN_CELL. Need is never merged."""
    cell_map = {}
    labels = [label for label, _, _ in LATE_TIME]
    for need, _, _ in NEEDS:
        groups = [[label] for label in labels]
        size = lambda group: sum(counts.get((label, need), 0) for label in group)
        changed = True
        while changed and len(groups) > 1:
            changed = False
            for index, group in enumerate(groups):
                if size(group) >= MIN_CELL:
                    continue
                target = index + 1 if index + 1 < len(groups) else index - 1
                merged = sorted(group + groups[target], key=labels.index)
                low, high = min(index, target), max(index, target)
                groups = groups[:low] + [merged] + groups[high + 1:]
                changed = True
                break
        for group in groups:
            cell = "%s|%s" % ("+".join(group), need)
            for label in group:
                cell_map["%s|%s" % (label, need)] = cell
    return dict(sorted(cell_map.items()))


def h1_keymap(drives):
    """2013.6 half-final bucket collapse, restricted to first-half finals: a
    bucket under MIN_CELL merges into the next larger surviving bucket; a thin
    largest bucket merges into the nearest smaller surviving one."""
    counts = [0] * len(H1_BUCKET_EDGES)
    for d in drives:
        counts[h1_bucket(d["t0"])] += 1
    bucket_map = list(range(len(H1_BUCKET_EDGES)))
    alive = lambda j: bucket_map[j] == j and counts[j] >= 0
    for i in range(len(H1_BUCKET_EDGES)):
        target = bucket_map[i]
        if counts[target] >= MIN_CELL:
            continue
        larger = [j for j in range(target + 1, len(H1_BUCKET_EDGES)) if alive(j)]
        smaller = [j for j in range(target - 1, -1, -1) if alive(j)]
        if not larger and not smaller:
            continue
        nxt = larger[0] if larger else smaller[0]
        counts[nxt] += counts[target]
        counts[target] = 0
        for j, mapped in enumerate(bucket_map):
            if mapped == target:
                bucket_map[j] = nxt
    keys = ["%d-%d" % edge for edge in H1_BUCKET_EDGES]
    return {keys[i]: keys[bucket_map[i]] for i in range(len(H1_BUCKET_EDGES))}


def tuple_of(d):
    fg = d["fg"] or [None, None, None]
    safety = d["safety_term"] or [None, None]
    return [
        d["plays"], d["net0"], d["seconds"], d["start"], d["end"], d["t0"], d["score_diff"],
        int(d["final"]), d["term_bucket"], d["term_down"], d["term_ydstogo"], d["chains"],
        d["kneel_yards"], d["spikes"], fg[0], fg[1], fg[2], safety[0], safety[1],
        d["runs"], d["attempts"], d["sacks"], d["td_kind"],
        d["off_timeouts"], d["def_timeouts"], d["off_timeouts_used"], d["def_timeouts_used"],
    ]


def late_cell_counts(drives, cell_map):
    out = collections.Counter()
    for d in drives:
        if regime(d) == "late":
            out[cell_map["%s|%s" % (time_label(d["t0"]), need_of(d["score_diff"]))]] += 1
    return out


def summary(extracted, cell_map):
    """Counts, shares and means compared between the two passes."""
    drives = extracted["drives"]
    out = {"drives": len(drives)}
    for category in CATEGORIES + ("other",):
        out["category:" + category] = sum(1 for d in drives if d["category"] == category)
    for name in ("neutral", "h1_final", "late", "ot"):
        out["regime:" + name] = sum(1 for d in drives if regime(d) == name)
    neutral = [d for d in drives if regime(d) == "neutral"]
    for index, (low, high) in enumerate(START_BINS):
        out["neutral_bin:%d-%d" % (low, high)] = sum(1 for d in neutral if low <= d["start"] <= high)
    raw = collections.Counter((time_label(d["t0"]), need_of(d["score_diff"])) for d in drives if regime(d) == "late")
    for (label, need), n in raw.items():
        out["late:%s|%s" % (label, need)] = n
    for label, _, _ in LATE_TIME:
        out["late_time:" + label] = sum(n for (time, _), n in raw.items() if time == label)
    chains = [sum(d["chains"][i] for d in drives) for i in range(6)]
    for name, value in zip(CHAIN_FIELDS, chains):
        out["chains:" + name] = value
    out["kneels"] = sum(len(d["kneel_yards"]) for d in drives)
    out["spikes"] = sum(d["spikes"] for d in drives)
    for side in ("off", "def"):
        for n in range(4):
            out["timeouts:%s_start_%d" % (side, n)] = sum(1 for d in drives if d[side + "_timeouts"] == n)
        out["timeouts:%s_used" % side] = sum(d[side + "_timeouts_used"] for d in drives)
    out["sacks"] = sum(d["sacks"] for d in drives)
    out["dropbacks"] = sum(d["sacks"] + d["attempts"] + d["spikes"] for d in drives)
    out["kickoff_pool"] = len(extracted["kickoff_pool"])
    out["kickoff_touchbacks"] = sum(r[0] for r in extracted["kickoff_pool"])
    out["free_kick_pool"] = len(extracted["free_kick_pool"])
    out["punt_pool"] = len(extracted["punt_pool"])
    out["interception_pool"] = len(extracted["interception_pool"])
    out["fumble_pool"] = len(extracted["fumble_pool"])
    out["scrambles"] = extracted["scramble"][0]
    last5 = [d for d in drives if _late_trailing(d, 300)]
    le120 = [d for d in drives if _late_trailing(d, 120)]
    out["late_punt_n_last5"] = len(last5)
    out["late_punt_n_le120"] = len(le120)
    means = {
        "mean:kickoff_nontb_start": describe([r[1] for r in extracted["kickoff_pool"] if not r[0]])["mean"],
        "mean:td_net": describe([d["net0"] for d in drives if d["category"] == "touchdown"])["mean"],
        "mean:start": describe([d["start"] for d in drives])["mean"],
    }
    for label, low, high in PUNT_NET_BINS:
        nets = [r[0] - (100 - r[5]) for r in extracted["punt_pool"] if low <= r[0] <= high]
        means["mean:punt_net %s" % label] = describe(nets)["mean"]
    shares = {
        "share:late_punt_share_last5": sum(d["category"] == "punt" for d in last5) / len(last5),
        "share:late_punt_share_le120": sum(d["category"] == "punt" for d in le120) / len(le120),
        "share:kickoff_touchback": out["kickoff_touchbacks"] / out["kickoff_pool"],
        "share:sacks_per_dropback": out["sacks"] / out["dropbacks"],
    }
    punt_drives = [d for d in drives if d["category"] == "punt"]
    means["mean:third_attempts_per_punt_drive"] = describe([d["chains"][2] for d in punt_drives])["mean"]
    return out, means, shares


def _late_trailing(d, seconds):
    t = d["terminal"]
    qtr = t["qtr"] or 0
    late = qtr >= 5 or (qtr == 4 and t["quarter_seconds_remaining"] is not None
                        and t["quarter_seconds_remaining"] <= seconds)
    return late and d["score_diff"] is not None and -8 <= d["score_diff"] <= -1


def build_model(primary, drive_model, usage):
    errors = []
    drives = primary["drives"]
    if len(drives) != EXPECTED_DRIVES:
        errors.append("drive count %d, expected %d" % (len(drives), EXPECTED_DRIVES))
    counts = collections.Counter(d["category"] for d in drives)
    if {c: counts.get(c, 0) for c in CATEGORIES} != drive_model["category_counts"] or sum(counts.values()) != sum(
            drive_model["category_counts"].values()):
        errors.append("category counts differ from the 2013.6 drive model: %s" % dict(counts))
    missing_sd = [d for d in drives if d["score_diff"] is None]
    if missing_sd:
        errors.append("%d drives without a rebuilt score" % len(missing_sd))

    parts = collections.defaultdict(list)
    for d in drives:
        parts[regime(d)].append(d)

    # -- neutral pools by start bin ------------------------------------------------
    neutral_counts = [[0] * len(CATEGORIES) for _ in START_BINS]
    neutral_pools = [[[] for _ in CATEGORIES] for _ in START_BINS]
    for d in parts["neutral"]:
        b, c = bin_index(d["start"]), CATEGORIES.index(d["category"])
        neutral_counts[b][c] += 1
        if d["renderable"]:
            neutral_pools[b][c].append(tuple_of(d))
    ladder = [[[] for _ in CATEGORIES] for _ in START_BINS]
    for b in range(len(START_BINS)):
        for c in range(len(CATEGORIES)):
            if not neutral_counts[b][c]:
                continue
            chosen, n = [b], len(neutral_pools[b][c])
            for j in sorted((j for j in range(len(START_BINS)) if j != b), key=lambda j: (abs(j - b), j)):
                if n >= MIN_CELL:
                    break
                chosen.append(j)
                n += len(neutral_pools[j][c])
            ladder[b][c] = sorted(chosen)

    # -- first-half finals ------------------------------------------------------------
    keymap = h1_keymap(parts["h1_final"])
    h1_pools = {}
    h1_counts = {}
    for d in parts["h1_final"]:
        key = keymap["%d-%d" % H1_BUCKET_EDGES[h1_bucket(d["t0"])]]
        h1_counts.setdefault(key, {c: 0 for c in CATEGORIES})[d["category"]] += 1
        if d["renderable"]:
            h1_pools.setdefault(key, {c: [] for c in CATEGORIES})[d["category"]].append(tuple_of(d))

    # -- late cells ---------------------------------------------------------------------
    raw = collections.Counter((time_label(d["t0"]), need_of(d["score_diff"])) for d in parts["late"])
    cell_map = collapse_late(raw)
    late_pools, late_counts = {}, {}
    for d in parts["late"]:
        cell = cell_map["%s|%s" % (time_label(d["t0"]), need_of(d["score_diff"]))]
        late_counts.setdefault(cell, {c: 0 for c in CATEGORIES})[d["category"]] += 1
        if d["renderable"]:
            late_pools.setdefault(cell, {c: [] for c in CATEGORIES})[d["category"]].append(tuple_of(d))
    for cell in set(cell_map.values()):
        late_pools.setdefault(cell, {c: [] for c in CATEGORIES})
    thin = {cell: sum(v.values()) for cell, v in late_counts.items() if sum(v.values()) < MIN_CELL}
    if thin:
        errors.append("late cells under MIN_CELL after collapse: %s" % thin)

    # -- overtime -------------------------------------------------------------------------
    ot_counts = {c: 0 for c in CATEGORIES}
    ot_pool = {c: [] for c in CATEGORIES}
    for d in parts["ot"]:
        ot_counts[d["category"]] += 1
        if d["renderable"]:
            ot_pool[d["category"]].append(tuple_of(d))

    for pools in [p for row in neutral_pools for p in row] + [
            p for cell in list(h1_pools.values()) + list(late_pools.values()) + [ot_pool] for p in cell.values()]:
        pools.sort(key=lambda t: json.dumps(t))

    # -- envelopes: [min, max] real net per (category, start bin), all drives ---------------
    envelopes = {c: [None] * len(START_BINS) for c in CATEGORIES}
    for d in drives:
        b = bin_index(d["start"])
        cell = envelopes[d["category"]][b]
        envelopes[d["category"]][b] = [d["net0"], d["net0"]] if cell is None else [
            min(cell[0], d["net0"]), max(cell[1], d["net0"])]

    # -- band centres -------------------------------------------------------------------------
    kick = primary["kickoff_pool"]
    nontb = describe([r[1] for r in kick if not r[0]])
    punt_net = {}
    for label, low, high in PUNT_NET_BINS:
        nets = [r[0] - (100 - r[5]) for r in primary["punt_pool"] if low <= r[0] <= high]
        punt_net[label] = describe(nets)
    punt_drives = [d for d in drives if d["category"] == "punt"]
    third = describe([d["chains"][2] for d in punt_drives])
    last5 = [d for d in drives if _late_trailing(d, 300)]
    le120 = [d for d in drives if _late_trailing(d, 120)]
    modelled = ("kickoff", "safety_free_kick", "punt", "interception", "fumble_lost", "downs", "missed_fg")
    start_all = describe([d["start"] for d in drives])
    start_modelled = describe([d["start"] for d in drives if d["start_kind"] in modelled])
    bin_shares = [sum(1 for d in drives if low <= d["start"] <= high) for low, high in START_BINS]

    def points(d):
        if d["category"] == "touchdown":
            t = d["terminal"]
            after = d["game_rows"][t["gi"] + 1:t["gi"] + 3]
            tries = [r for r in after if r["extra_point_result"] or r["two_point_conv_result"]]
            bonus = 0
            if tries:
                bonus = (tries[0]["extra_point_result"] == "good") + 2 * (tries[0]["two_point_conv_result"] == "success")
            return 6 + bonus
        if d["category"] == "field_goal_attempt":
            return 3 * d["fg"][1]
        return 0

    by_coarse = {}
    for label, low, high in COARSE_STARTS:
        cell = [d for d in drives if low <= d["start"] <= high]
        by_coarse[label] = {"n": len(cell),
                            "touchdown": [sum(d["category"] == "touchdown" for d in cell), len(cell)],
                            "punt": [sum(d["category"] == "punt" for d in cell), len(cell)]}
    ppd = {}
    for low, high in POINTS_BINS:
        cell = [d for d in drives if low <= d["start"] <= high]
        ppd["%d-%d" % (low, high)] = [sum(points(d) for d in cell), len(cell)]
    sacks = sum(d["sacks"] for d in drives)
    dropbacks = sum(d["sacks"] + d["attempts"] + d["spikes"] for d in drives)
    band_centres = {
        "kickoff_touchback_share": [sum(r[0] for r in kick), len(kick)],
        "kickoff_nontouchback_start": nontb,
        "punt_net_by_los_bin": {label: {**punt_net[label], "low": low, "high": high}
                                for label, low, high in PUNT_NET_BINS},
        "late_punt_share_last5_trail1_8": [sum(d["category"] == "punt" for d in last5), len(last5)],
        "late_punt_share_le120_trail1_8": [sum(d["category"] == "punt" for d in le120), len(le120)],
        "third_down_attempts_per_punt_drive": third,
        "sacks_per_dropback": [sacks, dropbacks],
        "start_all": start_all,
        "start_modelled_transitions": start_modelled,
        "start_bin_counts": bin_shares,
        "outcome_by_coarse_start": by_coarse,
        "points_per_drive_by_start_bin": ppd,
        "scramble_share_of_qb_rushes": primary["scramble"],
        "fourth_down_per_team_game": [sum(d["chains"][4] for d in drives), sum(d["chains"][5] for d in drives), TEAM_GAMES],
        "kneels_per_team_game": [sum(len(d["kneel_yards"]) for d in drives), TEAM_GAMES],
        "ot_punt_share": [ot_counts["punt"], sum(ot_counts.values())],
        "team_games": TEAM_GAMES,
    }

    # -- reconciliation --------------------------------------------------------------------------
    chains = [sum(d["chains"][i] for d in drives) for i in range(6)]
    fga = counts["field_goal_attempt"]
    fgm = sum(d["fg"][1] for d in drives if d["fg"])
    plays_tg = sum(d["plays"] for d in drives) / TEAM_GAMES
    net_tg = sum(d["net0"] for d in drives) / TEAM_GAMES
    zero_third = sum(1 for d in punt_drives if d["chains"][2] == 0)
    runs = sum(d["runs"] for d in drives)
    kneels = sum(len(d["kneel_yards"]) for d in drives)
    attempts = sum(d["attempts"] for d in drives) + sum(d["spikes"] for d in drives)
    reconciliation = {
        "drives": [len(drives), EXPECTED_DRIVES],
        "partition": {name: len(parts[name]) for name in ("neutral", "h1_final", "late", "ot")},
        "field_goal_attempts": [fga, 1016], "field_goals_made": [fgm, 852],
        "interceptions": [counts["interception"], 468],
        "chains": {"observed": chains[:4], "expected": [9241, 919, 6814, 2600]},
        "punt_drives_without_third_down_attempt": [zero_third, len(punt_drives)],
        "plays_per_team_game": [round(plays_tg, 4), 64.2, 0.1],
        "net_per_team_game_start_fp": [round(net_tg, 4), "reported; 2013.6 builder start 347.2 +/- 1.0"],
        "pass_attempts_incl_spikes": [attempts, 17788],
        "sacks": [sacks, 1169],
        "rushes_incl_kneels": [runs + kneels, 13925],
        "start_fp_corrected_drives": sum(1 for d in drives if d["corrected_start"]),
    }
    r = reconciliation
    if r["drives"][0] != EXPECTED_DRIVES or sum(r["partition"].values()) != EXPECTED_DRIVES:
        errors.append("partition does not sum to 5,984: %s" % r["partition"])
    for key in ("field_goal_attempts", "field_goals_made", "interceptions",
                "pass_attempts_incl_spikes", "sacks", "rushes_incl_kneels"):
        if r[key][0] != r[key][1]:
            errors.append("%s does not reconcile: %s" % (key, r[key]))
    if r["chains"]["observed"] != r["chains"]["expected"]:
        errors.append("chain sums do not reconcile: %s" % r["chains"])
    if zero_third:
        errors.append("%d punt drives without a third-down attempt" % zero_third)
    if abs(plays_tg - 64.2) > 0.1:
        errors.append("plays per team-game %.4f outside 64.2 +/- 0.1" % plays_tg)

    corrections = {
        "start_fp": "%d drives whose 2013.6 start was a nullified kickoff row now start at the first non-kick snap." % r["start_fp_corrected_drives"],
        "fg_offset": [d["fg_offset_corrected"] for d in drives if d.get("fg_offset_corrected")],
        "fg_offset_rule": "A field-goal attempt whose kick distance minus line of scrimmage is outside {17, 18, 19} keeps its real distance; its end is set to distance - 18.",
        "non_renderable": {
            "safety": sum(1 for d in drives if d["category"] == "safety" and not d["renderable"]),
            "touchdown": sum(1 for d in drives if d["category"] == "touchdown" and not d["renderable"]),
            "zero_play_terminal": primary["corrections"].get("zero_play_terminal", 0),
            "rule": "Penalty safeties, an aborted-snap fumble out of the end zone and a touchdown scored on a muffed punt recovered by the punting team count in the category mix but are never drawn as a render tuple.",
        },
        "turnover_touchbacks": {
            kind: {"pool_description_touchback": v[0], "pool_description_touchback_and_start_80": v[1],
                   "all_category_drives_description_touchback": v[2]}
            for kind, v in primary["turnover_touchbacks"].items()},
        "turnover_touchback_rule": "A turnover touchback is a pool record (a turnover followed by the other club's drive) whose play description contains 'touchback'; its published next start is 80 + enforcement. The research figure of 32 interception touchbacks is the pool count; 35 counts every interception-category drive, including those not followed by a turnover-started drive (a return touchdown remapped to interception, or the end of a half); 31 of the 32 start exactly at 80.",
    }
    model = {
        "schema": SCHEMA,
        "season": 2012,
        "season_type": "regular",
        "information_boundary": "2012 regular-season play-by-play only; no 2013 or later data; no team or game identifiers.",
        "builder": "scripts/research/build_2012_field_position_model.py",
        "sources": {
            **{name: {"file": spec["file"], "url": spec["url"], "sha256": spec["sha256"],
                      "drive_key": spec["drive_key"]} for name, spec in INPUTS.items()},
            "roster": dict(ROSTER),
        },
        "categories": list(CATEGORIES),
        "tuple_fields": list(TUPLE_FIELDS),
        "chain_fields": list(CHAIN_FIELDS),
        "kick_fields": list(KICK_FIELDS),
        "punt_fields": list(PUNT_FIELDS),
        "turnover_fields": list(TURNOVER_FIELDS),
        "preregistration": {
            "start_bins": [list(b) for b in START_BINS],
            "zones": {label: [low, high] for label, low, high in ZONES},
            "neutral_h2_seconds": NEUTRAL_H2_SECONDS,
            "late_time_buckets": {label: [low, high] for label, low, high in LATE_TIME},
            "needs": {label: [low, high] for label, low, high in NEEDS},
            "min_cell": MIN_CELL,
            "late_collapse_rule": "A thin late cell merges into the adjacent later time bucket; a thin <=120 bucket merges into the adjacent earlier one; repeated. Need is never merged.",
            "h1_bucket_edges": [list(e) for e in H1_BUCKET_EDGES],
            "h1_collapse_rule": "The 2013.6 rule restricted to first-half finals: a bucket under MIN_CELL merges into the next larger bucket (the largest into the next smaller).",
            "tuple_ladder": "A neutral (bin, category) tuple list under MIN_CELL adds the nearest bins, ties to the lower index. At draw time: the bin's list, else same zone, else the category is masked.",
            "k_transition": K_TRANSITION,
            "term_buckets": list(TERM_BUCKETS),
            "decision_zones": {label: [low, high] for label, low, high in DECISION_ZONES},
            "fg_offsets": list(FG_OFFSETS),
            "keep_end": ["field_goal_attempt", "punt", "downs", "interception", "fumble_lost"],
            "keep_net": ["clock"],
            "fixed": {"touchdown": "net = start, end = 0", "safety": "net = start - 100, end = 100"},
            "safety_render_rule": "A safety is drawn only from a start bin with a 2012 safety and with net inside that bin's envelope; its terminal kind (sack or run) and terminal line of scrimmage come from the real render tuple, so the terminal loss is exactly 100 - LOS.",
            "timeouts": "Kernel 2014.1: every tuple carries each club's charged timeouts at the drive's first offensive snap (posteam/defteam_timeouts_remaining) and the timeout rows called during the drive by each club (timeout_team). Late, first-half-final and overtime draws are conditioned on the current counts; see runtime/README.md.",
            "fallbacks": ["union of the need's late cells", "nearest-bucket clock tuple of the same need", "[0, 0, 0] (must never occur)"],
            "ot_mapping": "OT tied -> OT cell; OT trailing -> le120|trail1_3 cell (labelled inference: 2012 OT trailing n=4); OT leading -> OT cell with a diagnostic.",
        },
        "cell_map": cell_map,
        "h1_final_keymap": keymap,
        "neutral_counts": neutral_counts,
        "neutral_ladder": ladder,
        "h1_final_counts": dict(sorted(h1_counts.items())),
        "late_counts": dict(sorted(late_counts.items())),
        "ot_counts": ot_counts,
        "pools": {"neutral": neutral_pools, "h1_final": dict(sorted(h1_pools.items())),
                  "late": dict(sorted(late_pools.items())), "ot": ot_pool},
        "envelopes": envelopes,
        "kickoff_pool": kick,
        "free_kick_pool": primary["free_kick_pool"],
        "punt_pool": primary["punt_pool"],
        "interception_pool": primary["interception_pool"],
        "fumble_pool": primary["fumble_pool"],
        "rates": {"scramble": primary["scramble"]},
        "clock_scale": drive_model["clock_scale"],
        "band_centres": band_centres,
        "corrections": corrections,
        "reconciliation": reconciliation,
        "start_kinds": primary["start_kinds"],
        "EXPLAINED": dict(sorted(EXPLAINED.items())),
        "verification": {
            "category_counts": "identical to the 2013.6 drive model (same classifier and drive key); second pass nflscrapR, same GSIS feed",
            "chains": "two-file; reconciled to 9,241 / 919 / 6,814 / 2,600 in the primary pass",
            "pools": "single-source tuples (nflverse); the second pass compares counts, shares and means",
            "free_kick_pool": "single-source records (nflverse), 13 kicks, small n",
            "seconds": "single-source (nflverse drive time of possession); 2013.6 clock_scale reused",
            "scramble": "UNRESOLVED description-revision conflict (nflverse 681 / nflscrapR 643); informational only",
            "pfr_cross_check": "unresolved: Pro Football Reference drive and punt tables not reachable through the proxy",
        },
    }
    if primary["scramble"][1] <= 0:
        errors.append("no quarterback rushes identified for the scramble share")
    return model, errors


def second_pass(primary, secondary, cell_map):
    a_counts, a_means, a_shares = summary(primary, cell_map)
    b_counts, b_means, b_shares = summary(secondary, cell_map)
    # late cells with the nflverse cell map, no re-collapse
    for name, extracted, target in (("a", primary, a_counts), ("b", secondary, b_counts)):
        for cell, n in late_cell_counts(extracted["drives"], cell_map).items():
            target["late_cell:" + cell] = n
    rows_out, errors = [], []

    time_totals_agree = all(
        a_counts.get(k) == b_counts.get(k) or abs(a_counts[k] - b_counts[k]) <= COUNT_TOLERANCE * a_counts[k]
        for k in a_counts if k.startswith("late_time:"))

    def status_for(key, rel, limit):
        explained = EXPLAINED_METRICS.get(key)
        if explained is None and key.startswith(("late:", "late_cell:")) and time_totals_agree:
            explained = LATE_CELL_EXPLANATION
        if rel <= limit:
            return "within", None
        return ("explained", explained) if explained else ("UNEXPLAINED", None)

    for key in sorted(set(a_counts) | set(b_counts)):
        a, b = a_counts.get(key, 0), b_counts.get(key, 0)
        rel = abs(a - b) / a if a else (0.0 if b == 0 else float("inf"))
        status, why = status_for(key, rel, COUNT_TOLERANCE)
        if a == b:
            status = "match"
        row = {"metric": key, "nflverse": a, "nflscrapr": b, "status": status}
        if why:
            row["explanation"] = why
        if status == "UNEXPLAINED":
            errors.append("second pass %s: nflverse %s, nflscrapR %s" % (key, a, b))
        rows_out.append(row)
    for key in sorted(a_shares):
        a, b = a_shares[key], b_shares[key]
        status, why = status_for(key.split(":", 1)[1], abs(a - b), SHARE_TOLERANCE)
        row = {"metric": key, "nflverse": round(a, 4), "nflscrapr": round(b, 4), "status": status}
        if why:
            row["explanation"] = why
        if status == "UNEXPLAINED":
            errors.append("second pass %s: nflverse %.4f, nflscrapR %.4f" % (key, a, b))
        rows_out.append(row)
    for key in sorted(a_means):
        a, b = a_means[key], b_means[key]
        status = "within" if a is not None and b is not None and abs(a - b) <= MEAN_TOLERANCE else "UNEXPLAINED"
        if status == "UNEXPLAINED":
            errors.append("second pass %s: nflverse %s, nflscrapR %s" % (key, a, b))
        rows_out.append({"metric": key, "nflverse": a, "nflscrapr": b, "status": status})
    block = {
        "source": "nflscrapR reg_pbp_2012.csv, identical code, drive key 'drive', the nflverse cell map (no re-collapse)",
        "independence": "nflverse and nflscrapR both derive from the NFL GSIS feed; the second pass checks the parse and the classifier, not an independent observation.",
        "rules": "Counts within 1%, shares within one percentage point, means within 0.6 yards, unless explained.",
        "imputed_tries": {"nflverse": primary["imputed_tries"], "nflscrapr": secondary["imputed_tries"]},
        "turnover_touchbacks": {"nflverse": primary["turnover_touchbacks"], "nflscrapr": secondary["turnover_touchbacks"]},
        "scramble": {"nflverse": primary["scramble"], "nflscrapr": secondary["scramble"]},
        "comparison": rows_out,
        "result": "pass" if not errors else "fail",
    }
    return block, errors


def positions_map(path):
    counts = collections.defaultdict(collections.Counter)
    with open(path, newline="") as handle:
        for row in csv.DictReader(handle):
            if row["gsis_id"]:
                counts[row["gsis_id"]][row["position"]] += 1
    return {pid: c.most_common(1)[0][0] for pid, c in counts.items()}


def render(model):
    return json.dumps(model, sort_keys=True, separators=(",", ":")) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true", help="compare with the committed artifact instead of writing")
    args = parser.parse_args(argv)

    paths = {}
    for name, spec in list(INPUTS.items()) + [("roster", ROSTER)]:
        path = args.sources / spec["file"]
        if not path.exists():
            print("missing source: %s" % path, file=sys.stderr)
            return 2
        digest = sha256(path)
        if digest != spec["sha256"]:
            print("sha256 mismatch for %s: %s" % (path, digest), file=sys.stderr)
            return 2
        paths[name] = path

    drive_model = json.loads(DRIVE_MODEL.read_text())
    usage = json.loads(USAGE.read_text())
    positions = positions_map(paths["roster"])
    primary = extract(paths["nflverse"], "nflverse", positions)
    errors = []
    if primary["games"] != 256:
        errors.append("nflverse regular season has %d games" % primary["games"])
    model, build_errors = build_model(primary, drive_model, usage)
    errors += build_errors
    secondary = extract(paths["nflscrapr"], "nflscrapr", positions)
    block, pass_errors = second_pass(primary, secondary, model["cell_map"])
    errors += pass_errors
    model["second_pass"] = block
    model["reconciliation"]["result"] = "pass" if not errors else "fail"

    if errors:
        for error in errors:
            print("RECONCILIATION FAILURE: " + error, file=sys.stderr)
        return 1
    text = render(model)
    if args.check:
        current = args.out.read_text() if args.out.exists() else ""
        if current != text:
            print("artifact differs from a fresh build: %s" % args.out, file=sys.stderr)
            return 1
        print("artifact reproduced byte-for-byte: %s" % args.out)
        return 0
    args.out.write_text(text)
    print("wrote %s (%d bytes)" % (args.out, len(text)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
