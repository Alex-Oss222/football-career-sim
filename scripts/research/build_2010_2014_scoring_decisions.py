#!/usr/bin/env python3
"""Build the kernel 2014.6 scoring-decision artifact (plan batch B3c; data only).

  python scripts/research/build_2010_2014_scoring_decisions.py [--seasons 2010-2014w4|2012]
        [--sources DIR] [--check]

Writes library/data/2010_2014w4_scoring_decisions.json and the generated tables of
library/2010_2014_scoring_decisions_calibration.md (between its generated markers).
Sources come only through scripts/research/sources_2010_2014.py (the batch B2 gate);
DIR defaults to $SOURCES_2010_2014_DIR. Rules: library/2014_6_pre_build_specification.md,
section 4, Scoring decisions (its sha256 is in the header).

What it holds, every value counted here:
- the try decision (go or kick per touchdown followed by a try) as a league decision chart by
  the try team's margin and the game seconds left, collapsed by amendment A1; the two-point
  success rate over every two-point attempt from scrimmage, with each preregistered split
  tested and adopted only by the rule; the extra point referenced from the league base's drive
  model (one source);
- the onside decision chart, the expected and surprise recovery classes, and the onside spot
  records from the 35;
- non-offensive touchdown rates per unit (interceptions, lost scrimmage fumbles, punts, missed
  field goals, kickoffs from the 35 and safety free kicks), with line-of-scrimmage bins adopted
  only by the rule, and the feasibility-filtered return-touchdown records;
- try-snap participation from the 2013 snap counts (snaps per two-point try);
- both passes (nflverse primary, nflscrapR second) and their reconciliation.

Each rate's denominator is asserted against the committed league base (B3a): the unit counts
equal that base's drive categories and transition records plus touchdowns. Team and player
identifiers are read only to classify a row; nothing club-, game-, player- or date-keyed is
written.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import build_2012_field_position_model as fp  # noqa: E402
import league_base_2010_2014 as lb  # noqa: E402
import pre_build_specification  # noqa: E402
import sources_2010_2014 as sources  # noqa: E402

ROOT = HERE.parents[1]
DATA = ROOT / "library" / "data"
OUT = DATA / "2010_2014w4_scoring_decisions.json"
RECORD = ROOT / "library" / "2010_2014_scoring_decisions_calibration.md"
BASE = {"field_position": DATA / "2010_2014w4_nfl_field_position_model.json",
        "drive_model": DATA / "2010_2014w4_nfl_drive_model.json"}
SCHEMA = "2010-2014w4-nfl-scoring-decisions-v1"
MODES = {"2010-2014w4": (2010, 2011, 2012, 2013, 2014), "2012": (2012,)}

RULES = lb.RULES["scoring"]
THRESHOLDS = lb.RULES["thresholds"]
MIN_2PT = THRESHOLDS["TWO_POINT_MIN_CELL"]
KEEP = RULES["heterogeneity_keep"]
PRE_DIVERGENCE = (2010, 2011, 2012)
TIME_2PT = (("Q1-Q3", 901, 10 ** 6), ("Q4 900-601", 601, 900), ("Q4 600-301", 301, 600),
            ("Q4 300-121", 121, 300), ("Q4 120-0", 0, 120))
Q4_2PT = [label for label, _, _ in TIME_2PT[1:]]
DIFF_LOW, DIFF_HIGH = RULES["two_point_diff_range"]
TIME_ONS = (("Q1-Q3", 901, 10 ** 6), ("Q4 900-301", 301, 900), ("Q4 300-121", 121, 300), ("Q4 120-0", 0, 120))
DIFF_ONS = (("lead 1+", 1, 999), ("tied", 0, 0), ("trail 1-3", -3, -1), ("trail 4-8", -8, -4),
            ("trail 9-16", -16, -9), ("trail 17+", -999, -17))
LOS_BINS = tuple(tuple(b) for b in RULES["return_td_los_bins"])
SPOT_FROM = {2010: 30}            # onside unit kick spot (own yard line): 2010 from the 30, then the 35
SCRIM = ("pass", "run", "qb_kneel", "qb_spike")


# ============================================================================ helpers

def flag(r, k):
    return fp.flag(r, k)


def is_two_point_row(r):
    return "TWO-POINT CONVERSION" in (r.get("desc") or "").upper() or flag(r, "two_point_attempt") \
        or bool(r.get("two_point_conv_result"))


def kick_formation(r):
    return "kick formation" in (r.get("desc") or "").lower()


def valid(r):
    """A2: a row is nullified only when its description says No Play."""
    text = r.get("desc") or ""
    if r["play_type"] != "no_play":
        return True
    return "No Play" not in text and "NO PLAY" not in text and is_two_point_row(r)


def two_point_result(r):
    v = r.get("two_point_conv_result")
    if v in ("success", "failure"):
        return v
    text = (r.get("desc") or "").upper()
    if "ATTEMPT SUCCEEDS" in text:
        return "success"
    if "ATTEMPT FAILS" in text:
        return "failure"
    return "unknown"


def two_point_type(r):
    if r["play_type"] in ("pass", "run"):
        return r["play_type"]
    text = (r.get("desc") or "").lower()
    if " pass " in text or "pass to" in text or "sacked" in text:
        return "pass"
    return "run"


def secs(r):
    value = r.get("game_seconds_remaining")
    if value is None:
        value = r.get("half_seconds_remaining")
    return value


def tbucket(s, qtr, buckets):
    if (qtr or 0) >= 5:
        return "OT"
    return next((label for label, lo, hi in buckets if lo <= s <= hi), buckets[0][0])


def dbucket_2pt(diff):
    if diff < DIFF_LOW:
        return "<=%d" % (DIFF_LOW - 1)
    if diff > DIFF_HIGH:
        return ">=%d" % (DIFF_HIGH + 1)
    return "%+d" % diff


def dbucket_ons(diff):
    return next(label for label, lo, hi in DIFF_ONS if lo <= diff <= hi)


def los_bin(v):
    if v is None:
        return None
    return next(("%d-%d" % (lo, hi) for lo, hi in LOS_BINS if lo <= v <= hi), None)


def binom_ll(k, n, p):
    if n == 0:
        return 0.0
    if p <= 0 or p >= 1:
        return 0.0 if (k == 0 and p <= 0) or (k == n and p >= 1) else -1e18
    return k * math.log(p) + (n - k) * math.log(1 - p)


def lr_test(groups):
    """Likelihood-ratio test of one rate across groups [(k, n)]: {stat, df, p}."""
    groups = [(k, n) for k, n in groups if n > 0]
    if len(groups) < 2:
        return None
    k_all, n_all = sum(k for k, _ in groups), sum(n for _, n in groups)
    p0 = k_all / n_all
    stat = 2 * (sum(binom_ll(k, n, k / n) for k, n in groups) - sum(binom_ll(k, n, p0) for k, n in groups))
    stat = max(0.0, stat)
    df = len(groups) - 1
    return {"stat": round(stat, 4), "df": df, "p": round(lb.chi2_p(stat, df), 6)}


def stratified_lr(strata):
    """Season homogeneity within strata: the sum of each stratum's LR statistic and df. A stratum
    with no variation (every event 0, or every event 1) carries no information and adds no df."""
    stat = df = 0
    for groups in strata:
        k = sum(g[0] for g in groups)
        n = sum(g[1] for g in groups)
        if k == 0 or k == n:
            continue
        test = lr_test(groups)
        if test:
            stat += test["stat"]
            df += test["df"]
    return {"stat": round(stat, 4), "df": df, "p": round(lb.chi2_p(stat, df), 6) if df else None}


def pair(k, n):
    return [int(k), int(n)]


def tag(s):
    return lb.TAG[s]


# ============================================================================ extraction

def season_records(season, source, dest):
    """Every scoring record of one season and source (anonymous)."""
    rows = lb.load_rows(season, source, dest)
    fp.annotate_scores(rows)
    games = fp.games(rows)
    out = {k: [] for k in ("tries", "two_point", "kicks", "ints", "fumbles", "punts", "fgs")}
    out["no_try_td"] = 0
    out["interceptions_on_no_play_rows"] = 0
    out["ot_tries"] = 0
    out["games"] = len(games)
    for plays in games.values():
        for i, r in enumerate(plays):
            pt = r["play_type"]
            ok = valid(r)
            if pt == "no_play" and flag(r, "interception") and "No Play" not in (r.get("desc") or ""):
                out["interceptions_on_no_play_rows"] += 1
            # -- touchdowns and their first try ------------------------------------------------
            if ok and flag(r, "touchdown") and r["td_team"] and not is_two_point_row(r) \
                    and not r.get("extra_point_result"):
                offensive = fp.alias(r["td_team"]) == fp.alias(r["posteam"]) and pt in ("pass", "run") \
                    and not flag(r, "interception") and not flag(r, "fumble_lost")
                first = None
                for r2 in plays[i + 1:]:
                    if lb.is_try_row(r2):
                        first = r2
                        break
                    if r2["play_type"] in SCRIM + ("punt", "field_goal", "kickoff") or flag(r2, "kickoff_attempt"):
                        break
                if first is None:
                    out["no_try_td"] += 1
                elif (first["qtr"] or 0) >= 5:
                    out["ot_tries"] += 1
                else:
                    decision = "go" if is_two_point_row(first) and not kick_formation(first) else "kick"
                    out["tries"].append({"season": season, "qtr": int(first["qtr"] or 0), "secs": secs(first),
                                         "diff": first.get("sd"), "decision": decision,
                                         "first_nullified": "No Play" in (first.get("desc") or ""),
                                         "offensive_td": offensive})
            # -- two-point attempts (every valid one from scrimmage, re-tries included) -------------
            if ok and is_two_point_row(r) and not kick_formation(r) and r.get("defensive_two_point_attempt") != 1:
                td_row = next((x for x in reversed(plays[:i]) if flag(x, "touchdown") and x["td_team"]
                               and not is_two_point_row(x)), None)
                offensive_td = bool(td_row) and fp.alias(td_row["td_team"]) == fp.alias(td_row["posteam"]) \
                    and td_row["play_type"] in ("pass", "run") and not flag(td_row, "interception") \
                    and not flag(td_row, "fumble_lost")
                out["two_point"].append({"season": season, "result": two_point_result(r), "type": two_point_type(r),
                                         "spot": r.get("yardline_100"), "qtr": int(r["qtr"] or 0), "secs": secs(r),
                                         "home": fp.alias(r["posteam"]) == fp.alias(r.get("home_team") or ""),
                                         "offensive_td": offensive_td, "_club": (season, fp.alias(r["posteam"]))})
            # -- kickoffs (posteam = receiving club; the kicking club is defteam) ----------------
            if pt == "kickoff" or flag(r, "kickoff_attempt"):
                if not ok or not fp.is_kick_row(r):
                    continue
                spot = fp.kick_spot_own(r)
                nxt = next((x for x in plays[i + 1:] if x["play_type"] in SCRIM + ("punt", "field_goal")
                            and not lb.is_try_row(x)), None)
                prev_safety = False
                for x in reversed(plays[:i]):
                    if x["play_type"] in SCRIM + ("punt", "field_goal") or fp.is_kick_row(x):
                        prev_safety = flag(x, "safety")
                        break
                kicking, receiving = fp.alias(r["defteam"]), fp.alias(r["posteam"])
                td = fp.alias(r["td_team"]) if flag(r, "touchdown") and r["td_team"] else None
                found, _ = lb.clauses(r)
                pen_receiving = sum((y or 0) * (1 if lb.same_club(team, kicking) else -1)
                                    for team, _, status, y in found if status == "A")
                out["kicks"].append({
                    "season": season, "spot": spot, "onside": "onside" in (r.get("desc") or "").lower(),
                    "after_safety": prev_safety, "diff_k": None if r.get("sd") is None else -r["sd"],
                    "secs": secs(r), "qtr": int(r["qtr"] or 0), "qsecs": r.get("quarter_seconds_remaining"),
                    "own_recovery": r.get("own_kickoff_recovery") == 1,
                    "next_side": None if nxt is None else ("kicking" if fp.alias(nxt["posteam"]) == kicking else "receiving"),
                    "next_yl": None if nxt is None else nxt.get("yardline_100"),
                    "td_side": None if td is None else ("kicking" if td == kicking else "receiving"),
                    "kick_yards": fp.kick_yards(r), "return_yards": int(r.get("return_yards") or 0),
                    "touchback": r.get("touchback") == 1, "safety": flag(r, "safety"), "pen_receiving": pen_receiving})
                continue
            if not ok:
                continue
            defense_td = flag(r, "touchdown") and r["td_team"] and fp.alias(r["td_team"]) == fp.alias(r["defteam"])
            # -- interceptions on scrimmage downs ---------------------------------------------------
            if flag(r, "interception") and pt == "pass" and not lb.is_try_row(r):
                out["ints"].append({"season": season, "los": r.get("yardline_100"), "air": r.get("air_yards"),
                                    "ret": int(r.get("return_yards") or 0), "td": bool(defense_td)})
            # -- lost scrimmage fumbles without an interception ----------------------------------------
            elif flag(r, "fumble_lost") and pt in SCRIM and not lb.is_try_row(r):
                los = r.get("yardline_100")
                spot = None if los is None else int(round(los - (r.get("yards_gained") or 0)))
                out["fumbles"].append({"season": season, "los": los, "spot": spot, "kind": lb.fumble_kind(r),
                                       "ret": int(r.get("fumble_recovery_1_yards") or r.get("return_yards") or 0),
                                       "td": bool(defense_td)})
            if pt == "punt":
                out["punts"].append({"season": season, "los": r.get("yardline_100"), "blocked": r.get("punt_blocked") == 1,
                                     "gross": fp.kick_yards(r) or 0, "ret": int(r.get("return_yards") or 0),
                                     "td": bool(defense_td),
                                     "own_td": bool(flag(r, "touchdown") and r["td_team"]
                                                    and fp.alias(r["td_team"]) == fp.alias(r["posteam"]))})
            if pt == "field_goal":
                out["fgs"].append({"season": season, "result": r.get("field_goal_result"), "td": bool(defense_td)})
    out["red_zone"] = red_zone_proxy(games)
    return out


def red_zone_proxy(games):
    """Each club-season's red-zone touchdown share (drives with a snap inside the 20 ending in a
    touchdown), in memory only: the two-point team-quality proxy test reads it; nothing is stored."""
    drives = collections.defaultdict(lambda: [0, 0])
    for plays in games.values():
        current = None
        reached = False
        for r in plays:
            key = (r.get("drive_key"), fp.alias(r.get("posteam") or ""))
            if key != current:
                current, reached = key, False
            if r["play_type"] in SCRIM and (r.get("yardline_100") or 100) <= 20 and not reached and r.get("posteam"):
                reached = True
                drives[fp.alias(r["posteam"])][1] += 1
            if reached and flag(r, "touchdown") and r["td_team"] and fp.alias(r["td_team"]) == key[1] \
                    and r["play_type"] in ("pass", "run"):
                drives[key[1]][0] += 1
                reached = False
                current = None
    return {club: (k / n if n else None) for club, (k, n) in drives.items()}


# ============================================================================ analysis

def try_chart(tries):
    raw = collections.defaultdict(lambda: [0, 0])
    for t in tries:
        if t["diff"] is None:
            continue
        cell = (tbucket(t["secs"], t["qtr"], TIME_2PT), dbucket_2pt(t["diff"]))
        raw[cell][0] += t["decision"] == "go"
        raw[cell][1] += 1
    diffs = ["<=%d" % (DIFF_LOW - 1)] + ["%+d" % d for d in range(DIFF_LOW, DIFF_HIGH + 1)] + [">=%d" % (DIFF_HIGH + 1)]
    chart, cell_map = {}, {}
    for d in diffs:
        k, n = raw[("Q1-Q3", d)]
        chart["Q1-Q3|" + d] = {"go": k, "tries": n, "thin": n < MIN_2PT}
        cell_map["Q1-Q3|" + d] = "Q1-Q3|" + d
        groups = [[b] for b in Q4_2PT]

        def size(g):
            return sum(raw[(b, d)][1] for b in g)
        changed = True
        while changed and len(groups) > 1:
            changed = False
            for i in range(len(groups) - 1, -1, -1):
                if size(groups[i]) >= MIN_2PT:
                    continue
                j = i - 1 if i > 0 else i + 1
                lo, hi = min(i, j), max(i, j)
                groups = groups[:lo] + [groups[lo] + groups[hi]] + groups[hi + 1:]
                changed = True
                break
        for g in groups:
            g = sorted(g, key=Q4_2PT.index)
            cid = "+".join(g) + "|" + d
            k = sum(raw[(b, d)][0] for b in g)
            n = sum(raw[(b, d)][1] for b in g)
            chart[cid] = {"go": k, "tries": n, "thin": n < MIN_2PT}
            for b in g:
                cell_map[b + "|" + d] = cid
    return chart, cell_map, {"%s|%s" % c: v for c, v in sorted(raw.items())}


def chart_drift(tries, cell_map, seasons):
    strata = collections.defaultdict(lambda: {s: [0, 0] for s in seasons})
    for t in tries:
        if t["diff"] is None:
            continue
        cell = cell_map["%s|%s" % (tbucket(t["secs"], t["qtr"], TIME_2PT), dbucket_2pt(t["diff"]))]
        strata[cell][t["season"]][0] += t["decision"] == "go"
        strata[cell][t["season"]][1] += 1
    return stratified_lr([list(v.values()) for v in strata.values()])


def split_test(attempts, arm, seasons):
    """A preregistered two-arm split: pooled LR, per-season direction, and the keep rule."""
    groups = {a: [0, 0] for a in (True, False)}
    per = {s: {a: [0, 0] for a in (True, False)} for s in seasons}
    for t in attempts:
        a = arm(t)
        if a is None:
            continue
        success = t["result"] == "success"
        groups[a][0] += success
        groups[a][1] += 1
        per[t["season"]][a][0] += success
        per[t["season"]][a][1] += 1
    test = lr_test([tuple(groups[True]), tuple(groups[False])])
    sign = None
    if groups[True][1] and groups[False][1]:
        sign = (groups[True][0] / groups[True][1] > groups[False][0] / groups[False][1])
    eligible = [s for s in seasons if s in PRE_DIVERGENCE and min(per[s][True][1], per[s][False][1]) >= KEEP["min_attempts_per_arm"]]
    same = bool(eligible) and all(
        (per[s][True][0] / per[s][True][1] > per[s][False][0] / per[s][False][1]) == sign for s in eligible)
    kept = bool(test) and test["p"] < KEEP["p_below"] and same
    return {"arm_true": groups[True], "arm_false": groups[False], "lr": test,
            "by_season": {tag(s): {"arm_true": per[s][True], "arm_false": per[s][False]} for s in seasons},
            "eligible_pre_divergence_seasons": [tag(s) for s in eligible], "same_sign": same, "adopted": kept}


def onside_unit(season, k):
    return k["spot"] == SPOT_FROM.get(season, 35) and not k["after_safety"]


def opening(k):
    return (k["qtr"] in (1, 3) and k["qsecs"] == 900) or (k["qtr"] >= 5 and k["qsecs"] == 900)


def recovered(k):
    if k["td_side"]:
        return k["td_side"] == "kicking"
    return k["own_recovery"] or k["next_side"] == "kicking"


def expected(k):
    return k["qtr"] == 4 and k["secs"] is not None and k["secs"] <= 300 and k["diff_k"] is not None and k["diff_k"] < 0


def analyse(records, seasons):
    """Charts, rates and tests from one pass's records."""
    S = {}
    tries = [t for s in seasons for t in records[s]["tries"]]
    chart, cell_map, raw = try_chart(tries)
    S["try"] = {
        "tries_by_season": {tag(s): pair(sum(t["decision"] == "go" for t in records[s]["tries"]), len(records[s]["tries"]))
                            for s in seasons},
        "touchdowns_without_try": {tag(s): records[s]["no_try_td"] for s in seasons},
        "overtime_tries_excluded": {tag(s): records[s]["ot_tries"] for s in seasons},
        "first_try_nullified": sum(t["first_nullified"] for t in tries),
        "go_rate_season_lr": lr_test([(sum(t["decision"] == "go" for t in records[s]["tries"]), len(records[s]["tries"]))
                                      for s in seasons]),
        "decision_chart": chart, "decision_cell_map": cell_map, "raw_cells": raw,
        "chart_season_drift": chart_drift(tries, cell_map, seasons),
    }
    attempts = [t for s in seasons for t in records[s]["two_point"] if t["result"] in ("success", "failure")]
    per = {tag(s): pair(sum(t["result"] == "success" for t in attempts if t["season"] == s),
                        sum(1 for t in attempts if t["season"] == s)) for s in seasons}
    proxies = {}
    for s in seasons:
        for club, value in records[s]["red_zone"].items():
            proxies[(s, club)] = value
    values = sorted(v for v in (proxies.get(t["_club"]) for t in attempts) if v is not None)
    median = values[len(values) // 2] if values else None
    splits = {
        "type_pass": split_test(attempts, lambda t: t["type"] == "pass", seasons),
        "spot_2": split_test(attempts, lambda t: None if t["spot"] is None else t["spot"] == 2, seasons),
        "offensive_touchdown": split_test(attempts, lambda t: t["offensive_td"], seasons),
        "last_5_minutes": split_test(attempts, lambda t: t["qtr"] == 4 and t["secs"] is not None and t["secs"] <= 300,
                                     seasons),
        "home": split_test(attempts, lambda t: t["home"], seasons),
        "red_zone_proxy_above_median": split_test(
            attempts, lambda t: None if proxies.get(t["_club"]) is None or median is None
            else proxies[t["_club"]] > median, seasons),
    }
    S["two_point_success"] = {
        "pooled": pair(sum(v[0] for v in per.values()), sum(v[1] for v in per.values())),
        "by_season": per, "season_lr": lr_test([tuple(v) for v in per.values()]),
        "unknown_result": sum(1 for s in seasons for t in records[s]["two_point"] if t["result"] == "unknown"),
        "type_counts": dict(sorted(collections.Counter(t["type"] for t in attempts).items())),
        "splits": splits,
        "adopted_splits": sorted(k for k, v in splits.items() if v["adopted"]),
    }
    # Onside.
    kicks = {s: records[s]["kicks"] for s in seasons}
    cells = collections.defaultdict(lambda: [0, 0])
    season_onside = {}
    strata = collections.defaultdict(lambda: {s: [0, 0] for s in seasons})
    for s in seasons:
        unit = [k for k in kicks[s] if onside_unit(s, k)]
        season_onside[tag(s)] = pair(sum(k["onside"] for k in unit), len(unit))
        for k in unit:
            if k["diff_k"] is None:
                continue
            tb = "opening" if opening(k) else tbucket(k["secs"], k["qtr"], TIME_ONS)
            cell = "%s|%s" % (tb, dbucket_ons(k["diff_k"]))
            cells[cell][0] += k["onside"]
            cells[cell][1] += 1
            strata[cell][s][0] += k["onside"]
            strata[cell][s][1] += 1
    recovery = {"expected": [0, 0], "surprise": [0, 0]}
    rec_season = {tag(s): {"expected": [0, 0], "surprise": [0, 0]} for s in seasons}
    spot_records = {"kicking": [], "receiving": []}
    spot_checks = collections.Counter()
    for s in seasons:
        for k in kicks[s]:
            if not k["onside"] or k["after_safety"]:
                continue
            label = "expected" if expected(k) else "surprise"
            got = int(recovered(k))
            recovery[label][0] += got
            recovery[label][1] += 1
            rec_season[tag(s)][label][0] += got
            rec_season[tag(s)][label][1] += 1
            if k["spot"] == 35 and s >= 2011 and k["next_yl"] is not None and k["kick_yards"] is not None \
                    and not k["td_side"]:
                side = "kicking" if got else "receiving"
                landing = 35 + k["kick_yards"]
                nxt = int(round(k["next_yl"]))
                if side == "receiving":
                    e = nxt - (landing - k["return_yards"])
                else:
                    e = nxt - (100 - landing)
                # A penalty that helps the receiver lowers its next start (receiving frame) and
                # raises the kicking club's (kicking frame).
                explained = e == 0 or e == (-k["pen_receiving"] if side == "receiving" else k["pen_receiving"])
                feasible = 1 <= nxt <= 99 and 0 <= k["kick_yards"] <= 65 + 9
                spot_checks["feasible" if feasible else "infeasible"] += 1
                spot_checks["enforcement_explained" if explained else "enforcement_unexplained"] += 1
                if feasible:
                    spot_records[side].append([s, label, k["kick_yards"], k["return_yards"] if side == "receiving" else 0,
                                               e, nxt])
    sens = {label: pair(sum(rec_season[tag(s)][label][0] for s in seasons if s >= 2011),
                        sum(rec_season[tag(s)][label][1] for s in seasons if s >= 2011)) for label in recovery}
    S["onside"] = {
        "decision_chart": {c: pair(*v) for c, v in sorted(cells.items())},
        "onside_share_by_season": season_onside,
        "onside_share_season_lr": lr_test([tuple(v) for v in season_onside.values()]),
        "chart_season_drift": stratified_lr([list(v.values()) for v in strata.values()]),
        "recovery": {label: pair(*v) for label, v in recovery.items()},
        "recovery_lr_expected_vs_surprise": lr_test([tuple(v) for v in recovery.values()]),
        "recovery_by_season": rec_season,
        "recovery_season_lr": {label: lr_test([tuple(rec_season[tag(s)][label]) for s in seasons]) for label in recovery},
        "recovery_2011_2014_sensitivity": sens,
        "safety_free_kicks": pair(sum(k["onside"] for s in seasons for k in kicks[s] if k["after_safety"]),
                                  sum(1 for s in seasons for k in kicks[s] if k["after_safety"])),
        "spot_records_from_35": spot_records,
        "spot_record_checks": dict(sorted(spot_checks.items())),
        "spot_record_fields": ["season", "class", "kick_yards", "return_yards", "enforcement", "next_start"],
    }
    S["non_offensive"] = non_offensive(records, seasons, kicks)
    S["interceptions_on_no_play_rows"] = sum(records[s]["interceptions_on_no_play_rows"] for s in seasons)
    return S


def non_offensive(records, seasons, kicks):
    out = {}

    def unit(name, select, td, los=None, seasons_=seasons):
        per = {tag(s): pair(sum(td(x) for x in select(s)), len(select(s))) for s in seasons_}
        entry = {"pooled": pair(sum(v[0] for v in per.values()), sum(v[1] for v in per.values())),
                 "by_season": per, "season_lr": lr_test([tuple(v) for v in per.values()])}
        if los is not None:
            bins = collections.defaultdict(lambda: [0, 0])
            for s in seasons_:
                for x in select(s):
                    b = los_bin(los(x))
                    if b is None:
                        continue
                    bins[b][0] += td(x)
                    bins[b][1] += 1
            test = lr_test([tuple(v) for v in bins.values()])
            entry["los_bins"] = {b: pair(*bins[b]) for b in sorted(bins, key=lambda b: int(b.split("-")[0]))}
            entry["los_lr"] = test
            entry["bins_adopted"] = bool(test) and test["p"] < RULES["return_td_bins_keep_p_below"]
        out[name] = entry

    unit("interception", lambda s: records[s]["ints"], lambda x: int(x["td"]), lambda x: x["los"])
    unit("fumble_lost", lambda s: records[s]["fumbles"], lambda x: int(x["td"]), lambda x: x["spot"])
    unit("punt", lambda s: records[s]["punts"], lambda x: int(x["td"]), lambda x: x["los"])
    unit("missed_field_goal", lambda s: [f for f in records[s]["fgs"] if f["result"] != "made"], lambda x: int(x["td"]))
    kick_seasons = tuple(s for s in seasons if s >= 2011)
    unit("kickoff", lambda s: [k for k in kicks[s] if k["spot"] == 35 and not k["onside"] and not k["after_safety"]],
         lambda x: int(x["td_side"] == "receiving"), seasons_=kick_seasons)
    unit("safety_free_kick", lambda s: [k for k in kicks[s] if k["after_safety"]],
         lambda x: int(x["td_side"] == "receiving"))
    # Feasibility-filtered records.
    pick, fum, punt, kick = [], [], [], []
    checks = collections.Counter()
    for s in seasons:
        for x in records[s]["ints"]:
            if x["td"]:
                ok = x["los"] is not None and x["air"] is not None and x["air"] <= x["los"] + 9 \
                    and x["ret"] == int(round(100 - x["los"] + x["air"]))
                checks["interception_" + ("feasible" if ok else "dropped")] += 1
                if ok:
                    pick.append([s, los_bin(x["los"]), int(x["air"]), x["ret"]])
        for x in records[s]["fumbles"]:
            if x["td"]:
                ok = x["spot"] is not None and 1 <= x["spot"] <= 99 and 0 <= x["ret"] <= 100
                checks["fumble_" + ("feasible" if ok else "dropped")] += 1
                if ok:
                    fum.append([s, los_bin(x["spot"]), x["spot"], x["ret"]])
        for x in records[s]["punts"]:
            if x["td"]:
                ok = x["los"] is not None and x["gross"] <= x["los"] + 9 and (
                    x["blocked"] or x["ret"] == int(round(100 - x["los"] + x["gross"])))
                checks["punt_" + ("feasible" if ok else "dropped")] += 1
                if ok:
                    punt.append([s, int(x["los"]), int(x["blocked"]), x["gross"], x["ret"]])
        if s >= 2011:
            for k in kicks[s]:
                if k["spot"] == 35 and not k["onside"] and not k["after_safety"] and k["td_side"] == "receiving":
                    ok = k["kick_yards"] is not None and k["return_yards"] == 35 + k["kick_yards"]
                    checks["kickoff_" + ("feasible" if ok else "dropped")] += 1
                    if ok:
                        kick.append([s, k["kick_yards"], k["return_yards"]])
    out["records"] = {"interception_return_td": pick, "fumble_return_td": fum, "punt_return_or_block_td": punt,
                      "kickoff_return_td": kick,
                      "fields": {"interception_return_td": ["season", "los_bin", "air_yards", "return_yards"],
                                 "fumble_return_td": ["season", "spot_bin", "spot", "return_yards"],
                                 "punt_return_or_block_td": ["season", "los", "blocked", "gross", "return_yards"],
                                 "kickoff_return_td": ["season", "kick_yards", "return_yards"]},
                      "checks": dict(sorted(checks.items())),
                      "rule": "gross or air yards at most LOS + 9 and the side-aware spot identity: an interception "
                              "return covers 100 - LOS + air yards; a fumble record needs its fumble spot (the "
                              "fumbled snap's LOS minus its yards) on the field and a return of 0-100 yards (the "
                              "ball is recovered where it rolls, not where it was fumbled); a punt return 100 - LOS + gross (blocked punts "
                              "exempt), a kickoff return 35 + kick yards; a record failing either is dropped, counted",
                      "kick_return_chain_cap": RULES["kick_return_chain_cap"]}
    out["not_modelled"] = {
        "kicking_team_kickoff_touchdowns": sum(1 for s in seasons for k in kicks[s] if k["td_side"] == "kicking"
                                               and not k["onside"]),
        "onside_return_touchdowns": sum(1 for s in seasons for k in kicks[s] if k["onside"] and k["td_side"]),
        "punting_team_touchdowns": sum(1 for s in seasons for p in records[s]["punts"] if p["own_td"]),
        "kick_return_safeties": sum(1 for s in seasons for k in kicks[s] if k["safety"]),
    }
    out["team_games"] = {tag(s): 2 * records[s]["games"] for s in seasons}
    total = {}
    for s in seasons:
        n = sum(x["td"] for x in records[s]["ints"]) + sum(x["td"] for x in records[s]["fumbles"]) \
            + sum(x["td"] for x in records[s]["punts"]) + sum(x["td"] for x in records[s]["fgs"]) \
            + sum(1 for k in kicks[s] if k["td_side"] == "receiving")
        total[tag(s)] = pair(n, 2 * records[s]["games"])
    out["non_offensive_touchdowns_per_team_game"] = {"pooled": pair(sum(v[0] for v in total.values()),
                                                                     sum(v[1] for v in total.values())),
                                                     "by_season": total}
    return out


# ============================================================================ participation

def try_snap_participation(dest):
    """Snaps recorded per two-point try (2013 snap counts): per club-game offensive and
    defensive team snaps regressed on the play-by-play snap counts; nothing club-keyed stored."""
    snaps = {}
    for r in sources.rows("snap_counts_2013.csv", dest):
        if r.get("game_type") != "REG":
            continue
        for side in ("offense", "defense"):
            n, pct = r.get(side + "_snaps"), r.get(side + "_pct")
            try:
                n, pct = float(n), float(pct)
            except (TypeError, ValueError):
                continue
            if pct >= 0.5:
                key = (r["game_id"], fp.alias(r["team"]), side)
                snaps.setdefault(key, []).append(n / pct)
    team_snaps = {k: round(sorted(v)[len(v) // 2]) for k, v in snaps.items()}
    rows = lb.load_rows(2013, "nflverse", dest)
    counts = collections.defaultdict(lambda: [0, 0, 0, 0])   # [scrimmage snaps, no-play rows, two-point tries, punt/fg]
    for r in rows:
        pos = fp.alias(r.get("posteam") or "")
        if not pos:
            continue
        key = r["game_id"]
        if is_two_point_row(r) and valid(r) and not kick_formation(r):
            counts[(key, pos)][2] += 1
        elif r["play_type"] in SCRIM and not lb.is_try_row(r):
            counts[(key, pos)][0] += 1
        elif r["play_type"] in ("punt", "field_goal"):
            counts[(key, pos)][3] += 1
        elif r["play_type"] == "no_play" and not lb.is_try_row(r):
            counts[(key, pos)][1] += 1
    defense = collections.defaultdict(lambda: [0, 0, 0, 0])
    for r in rows:
        dfn = fp.alias(r.get("defteam") or "")
        pos = fp.alias(r.get("posteam") or "")
        if not dfn or not pos:
            continue
        defense[(r["game_id"], dfn)] = counts[(r["game_id"], pos)]
    out = {}
    for side, table in (("offense", counts), ("defense", defense)):
        X, y = [], []
        for (gid, club), c in table.items():
            snap = team_snaps.get((gid, club, side))
            if snap is None:
                continue
            X.append([1.0, c[0], c[1], c[2], c[3]])
            y.append(float(snap))
        beta, se = ols(X, y)
        out[side] = {"club_games": len(y), "per_two_point_try": round(beta[3], 4), "se": round(se[3], 4),
                     "per_scrimmage_snap": round(beta[1], 4), "per_no_play_row": round(beta[2], 4),
                     "per_punt_or_field_goal": round(beta[4], 4), "intercept": round(beta[0], 4)}
    out["rule"] = ("Club-game team snaps (the median of offense or defense snaps / share over players at 50% or more) "
                   "regressed by least squares on the club-game play-by-play counts of scrimmage snaps, no-play rows, "
                   "two-point tries from scrimmage and punt or field-goal snaps (2013 regular season; nflverse snap "
                   "counts begin in 2013). The two-point coefficient is the participation a try snap adds; no "
                   "club-keyed row is stored.")
    return out


def ols(X, y):
    k = len(X[0])
    xtx = [[sum(r[i] * r[j] for r in X) for j in range(k)] for i in range(k)]
    xty = [sum(r[i] * v for r, v in zip(X, y)) for i in range(k)]
    inv = invert(xtx)
    beta = [sum(inv[i][j] * xty[j] for j in range(k)) for i in range(k)]
    resid = [v - sum(b * x for b, x in zip(beta, r)) for r, v in zip(X, y)]
    sigma2 = sum(e * e for e in resid) / (len(y) - k)
    se = [math.sqrt(sigma2 * inv[i][i]) for i in range(k)]
    return beta, se


def invert(m):
    n = len(m)
    a = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(m)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(a[r][c]))
        a[c], a[p] = a[p], a[c]
        pivot = a[c][c]
        a[c] = [v / pivot for v in a[c]]
        for r in range(n):
            if r != c:
                f = a[r][c]
                a[r] = [v - f * w for v, w in zip(a[r], a[c])]
    return [row[n:] for row in a]


# ============================================================================ denominators

def denominator_checks(primary, seasons, base_fp, base_dm):
    """Unit counts against the committed league base (B3a): the drive categories and the
    transition records plus touchdowns."""
    errors, rows = [], []
    cats = base_dm["category_counts_by_season"]
    for s in seasons:
        t = tag(s)
        ints = len(primary[s]["ints"])
        fum = len(primary[s]["fumbles"])
        punts = len(primary[s]["punts"])
        punt_terminal = sum(base_dm["punt_terminal_by_category"][t].values())
        for name, mine, theirs in (("interception", ints, cats[t]["interception"]),
                                   ("fumble_lost", fum, cats[t]["fumble_lost"]), ("punt", punts, punt_terminal)):
            row = {"season": t, "unit": name, "scoring_units": mine, "base_drive_category": theirs}
            if theirs is not None:
                row["status"] = "equal" if mine == theirs else "differs"
            rows.append(row)
    pool = collections.Counter(r[6] for r in base_fp["kickoff_pool"] if r[5] != "retained")
    retained = collections.Counter(r[6] for r in base_fp.get("retained_kick_pools", {}).get("kickoff", []))
    for s in seasons:
        if s < 2011:
            continue
        kicks = [k for k in primary[s]["kicks"] if k["spot"] == 35 and not k["onside"] and not k["after_safety"]]
        tds = sum(1 for k in kicks if k["td_side"] == "receiving")
        rows.append({"season": tag(s), "unit": "kickoff", "scoring_units": len(kicks),
                     "base_kickoff_records": pool.get(s, 0), "base_retained_kickoffs": retained.get(s, 0),
                     "return_touchdowns": tds,
                     "other": len(kicks) - pool.get(s, 0) - retained.get(s, 0) - tds})
    for row in rows:
        why = DENOMINATOR_EXPLAINED.get((row["season"], row["unit"]))
        if row.get("status") == "differs" and why and row["scoring_units"] - row["base_drive_category"] == why[0]:
            row["status"] = "explained"
            row["explanation"] = why[1]
        if row.get("status") == "differs":
            errors.append("scoring unit %s %s: %s, base %s" % (row["season"], row["unit"], row["scoring_units"],
                                                                row["base_drive_category"]))
    return {"rule": "interception units equal the base's interception drives per season, punt units the base's "
                    "punt-terminal drives (any category: a punt can end in a safety or a touchdown), and lost-fumble "
                    "units (scrimmage fumbles lost without an interception) its fumble-lost drives, unless explained; "
                    "kickoff units are the base's kickoff and retained records plus return touchdowns, and the "
                    "remainder is counted: kicks the base holds no record for (the half or game ended before the "
                    "receiving club snapped, or its drive began another way)",
            "comparison": rows}, errors


# Unit-count differences against the base explained by source defects found during the build.
DENOMINATOR_EXPLAINED = {
    ("2012", "fumble_lost"): (-1, "2012_06_KC_TB: one of the base's fumble-lost drives ends on a blocked punt the "
                                  "punter fumbled, which is not a scrimmage fumble"),
    ("2011", "punt"): (1, "2011_13_DET_NO: the nflverse rows around play 1335 are out of file order and the punt at "
                          "9:01 of the second quarter falls inside a later fixed_drive group, so it ends no drive; it "
                          "counts in the punt unit only"),
}


# ============================================================================ build

def build(dest, seasons, log=print):
    records = {"nflverse": {}, "nflscrapr": {}}
    for source in records:
        for s in seasons:
            log("scoring %s %s" % (source, tag(s)))
            records[source][s] = season_records(s, source, dest)
    a = analyse(records["nflverse"], seasons)
    b = analyse(records["nflscrapr"], seasons)
    errors = []
    base_fp = json.loads(BASE["field_position"].read_text()) if seasons == MODES["2010-2014w4"] else None
    base_dm = json.loads(BASE["drive_model"].read_text()) if seasons == MODES["2010-2014w4"] else None
    denominators = None
    if base_fp is not None:
        denominators, d_errors = denominator_checks(records["nflverse"], seasons, base_fp, base_dm)
        errors += d_errors
    participation = try_snap_participation(dest) if 2013 in seasons else None
    for split in a["two_point_success"]["splits"].values():
        split.pop("_", None)
    reconciliation = second_pass_block(a, b, seasons)
    artifact = {
        "schema": SCHEMA,
        "seasons": [tag(s) for s in seasons],
        "season_type": "regular",
        "information_boundary": ("NFL regular seasons 2010-2013 and 2014 Weeks 1-4 (games through September 29, "
                                 "2014), cut at fetch; no club, game, player or date field. 2013 and 2014 Weeks 1-4 "
                                 "are an anonymous post-divergence league population (pooled only)."
                                 if len(seasons) > 1 else "2012 regular season only; no club, game, player or date "
                                                          "field."),
        "builder": "scripts/research/build_2010_2014_scoring_decisions.py",
        "specification_sha256": pre_build_specification.digest(),
        "sources": {name: {"sha256": sources.load_manifest()["assets"][name]["sha256"]}
                    for s in seasons for name in (lb.pbp_name(s, "nflverse"), lb.pbp_name(s, "nflscrapr"))},
        "league_base": {role: {"file": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                        for role, path in BASE.items()} if base_fp is not None else None,
        "team_games": a["non_offensive"]["team_games"],
        "rules": {
            "try_unit": "one decision per touchdown followed by a try: the first try snap after it; go = a two-point "
                        "attempt from scrimmage, kick = an extra-point kick including aborted kicks and fakes from "
                        "kick formation; touchdowns with no try excluded and counted; overtime tries excluded",
            "two_point_chart": "state = the try team's margin after the touchdown and before the try (rebuilt running "
                               "score) and game seconds left; buckets per the specification; collapse amendment A1",
            "two_point_success": "one pooled rate over every two-point attempt from scrimmage not nullified; a split is "
                                 "adopted only with LR p < 0.01 pooled and the same sign in each pre-divergence season "
                                 "with at least 10 attempts per arm",
            "extra_point": "referenced from the league base drive model rates.extra_point (one source, not duplicated)",
            "onside_unit": "every valid kickoff from the kicking club's own 35 (2011-2014) or 30 (2010) whose "
                           "description says onside; safety free kicks apart; expected = the kicking club trails in "
                           "the fourth quarter with 300 s or less left, surprise = every other; recovery = the "
                           "kicking club has the next offensive snap, own_kickoff_recovery, or scores on the kick",
            "non_offensive_units": "valid interceptions on scrimmage downs, lost scrimmage fumbles without an "
                                   "interception, punts, missed field goals (blocked included), non-onside kickoffs "
                                   "from the 35 (2011-2014), safety free kicks; LOS bins adopted only with LR p < 0.01",
            "decision_source": "Jacksonville's two-point and onside decisions come from Stone (U6 unanswered): a "
                               "call-sheet block, a live pause or a dated delegation; every other club and every "
                               "autonomous run uses this league chart. Success odds are the same for every club.",
        },
        "amendments": [
            {"id": "A1", "what": "two-point chart: thin cells collapse within the fourth quarter only; Q1-Q3 is one cell "
                                 "per diff and never merges with Q4",
             "when": "after the preregistered collapse was run and printed, before any kernel use",
             "disclosure": "the preregistered rule merged thin fourth-quarter cells into Q1-Q3, crossing the boundary the "
                           "decision depends on; minimum cell and edges unchanged; no target rate used",
             "preregistered_collapse_for_the_record": "not adopted"},
            {"id": "A2", "what": "a play is nullified only when its description says No Play"},
            {"id": "A3", "what": "the design's independent second pass read the text after REVERSED. as the play that "
                                 "counted; here both passes read the source flags (which carry the final ruling) and the "
                                 "penalty clauses read the counted text"},
        ],
        "try": a["try"],
        "two_point_success": a["two_point_success"],
        "extra_point_reference": {"artifact": "library/data/2010_2014w4_nfl_drive_model.json", "key": "rates.extra_point",
                                  "value": base_dm["rates"]["extra_point"] if base_dm else None},
        "onside": a["onside"],
        "non_offensive": a["non_offensive"],
        "try_snap_participation": participation,
        "denominators": denominators,
        "second_pass": reconciliation,
    }
    _strip_private(artifact)
    return artifact, errors


def _strip_private(obj):
    if isinstance(obj, dict):
        for key in [k for k in obj if k.startswith("_")]:
            del obj[key]
        for v in obj.values():
            _strip_private(v)
    elif isinstance(obj, list):
        for v in obj:
            _strip_private(v)


def second_pass_block(a, b, seasons):
    """Both passes side by side for every rate; the comparison is reported, with the
    drift tests of both passes."""
    def rate(x):
        return None if not x or not x[1] else round(x[0] / x[1], 5)
    rows = []
    for name, x, y in (
            ("tries (go/tries) pooled", [sum(v[0] for v in a["try"]["tries_by_season"].values()),
                                         sum(v[1] for v in a["try"]["tries_by_season"].values())],
             [sum(v[0] for v in b["try"]["tries_by_season"].values()),
              sum(v[1] for v in b["try"]["tries_by_season"].values())]),
            ("two-point success", a["two_point_success"]["pooled"], b["two_point_success"]["pooled"]),
            ("onside expected recovery", a["onside"]["recovery"]["expected"], b["onside"]["recovery"]["expected"]),
            ("onside surprise recovery", a["onside"]["recovery"]["surprise"], b["onside"]["recovery"]["surprise"]),
            ("interception return TD", a["non_offensive"]["interception"]["pooled"],
             b["non_offensive"]["interception"]["pooled"]),
            ("fumble return TD", a["non_offensive"]["fumble_lost"]["pooled"], b["non_offensive"]["fumble_lost"]["pooled"]),
            ("punt return or block TD", a["non_offensive"]["punt"]["pooled"], b["non_offensive"]["punt"]["pooled"]),
            ("kickoff return TD", a["non_offensive"]["kickoff"]["pooled"], b["non_offensive"]["kickoff"]["pooled"]),
            ("missed field goal return TD", a["non_offensive"]["missed_field_goal"]["pooled"],
             b["non_offensive"]["missed_field_goal"]["pooled"])):
        rows.append({"metric": name, "nflverse": x, "nflscrapr": y, "rate_nflverse": rate(x), "rate_nflscrapr": rate(y)})
    q4 = {}
    for key in ("Q4 120-0|-2", "Q4 300-121|-2", "Q4 600-301|-2", "Q4 900-601|-2", "Q1-Q3|-2", "Q4 120-0|-1",
                "Q4 300-121|-1", "Q4 600-301|-1", "Q4 900-601|-1"):
        q4[key] = {"nflverse": a["try"]["raw_cells"].get(key), "nflscrapr": b["try"]["raw_cells"].get(key)}
    return {"source": "nflscrapR reg_pbp, the same extraction code on its own flags and rebuilt running score",
            "interceptions_on_unnullified_no_play_rows": {"nflverse": a["interceptions_on_no_play_rows"],
                                                          "nflscrapr": b["interceptions_on_no_play_rows"],
                                                          "note": "nflscrapR codes some counted interceptions as "
                                                                  "no_play rows (the description does not say No "
                                                                  "Play); the shared extraction skips them, which is "
                                                                  "most of its interception shortfall"},
            "independence": "both files derive from the NFL GSIS feed; nflscrapR lacks extra-point and some two-point "
                            "rows, so its try counts and score states differ by those rows",
            "comparison": rows,
            "chart_season_drift": {"nflverse": a["try"]["chart_season_drift"], "nflscrapr": b["try"]["chart_season_drift"]},
            "onside_chart_season_drift": {"nflverse": a["onside"]["chart_season_drift"],
                                          "nflscrapr": b["onside"]["chart_season_drift"]},
            "onside_share_season_lr": {"nflverse": a["onside"]["onside_share_season_lr"],
                                       "nflscrapr": b["onside"]["onside_share_season_lr"]},
            "raw_cells_down_1_and_2": q4,
            "decision_chart_pass2": b["try"]["decision_chart"],
            "onside_decision_chart_pass2": b["onside"]["decision_chart"],
            "adopted_splits_pass2": b["two_point_success"]["adopted_splits"],
            "non_offensive_bins_adopted_pass2": {k: b["non_offensive"][k].get("bins_adopted")
                                                 for k in ("interception", "fumble_lost", "punt")}}


# ============================================================================ the library record

BEGIN, END = "<!-- generated:begin -->", "<!-- generated:end -->"


def tables(art):
    t = art["try"]
    lines = ["Generated by `scripts/research/build_2010_2014_scoring_decisions.py` from the artifact; do not edit.", ""]
    lines.append("| Season | Go | Tries | Touchdowns without a try |")
    lines.append("|---|---|---|---|")
    for s, (go, n) in t["tries_by_season"].items():
        lines.append("| %s | %d | %d | %d |" % (s, go, n, t["touchdowns_without_try"][s]))
    d = t["chart_season_drift"]
    lines += ["", "Chart season drift (stratified LR, pass 1): stat %.3f on %d df, p %.3f." % (d["stat"], d["df"], d["p"]), ""]
    lines.append("**Fourth-quarter two-point decision cells (go / tries)**")
    lines.append("")
    lines.append("| Cell | Go | Tries | Thin |")
    lines.append("|---|---|---|---|")
    for cell, v in sorted(t["decision_chart"].items()):
        if cell.startswith("Q4") and int(cell.split("|")[1].replace(">=", "").replace("<=", "")) in range(-9, 3):
            lines.append("| %s | %d | %d | %s |" % (cell, v["go"], v["tries"], "yes" if v["thin"] else ""))
    two = art["two_point_success"]
    lines += ["", "**Two-point success**: %d of %d (%s); season LR p %.3f; adopted splits: %s." % (
        two["pooled"][0], two["pooled"][1], "%.4f" % (two["pooled"][0] / two["pooled"][1]), two["season_lr"]["p"],
        ", ".join(two["adopted_splits"]) or "none"), ""]
    lines.append("| Split | Arm true | Arm false | LR p | Same sign | Adopted |")
    lines.append("|---|---|---|---|---|---|")
    for name, v in sorted(two["splits"].items()):
        lines.append("| %s | %d/%d | %d/%d | %s | %s | %s |" % (
            name, v["arm_true"][0], v["arm_true"][1], v["arm_false"][0], v["arm_false"][1],
            "%.4f" % v["lr"]["p"] if v["lr"] else "-", v["same_sign"], v["adopted"]))
    o = art["onside"]
    lines += ["", "**Onside**: onside share by season LR %.3f on %d df, p %.3f; chart season drift p %.3f." % (
        o["onside_share_season_lr"]["stat"], o["onside_share_season_lr"]["df"], o["onside_share_season_lr"]["p"],
        o["chart_season_drift"]["p"]), ""]
    lines.append("| Class | Recovered | Onside kicks | 2011-2014 sensitivity |")
    lines.append("|---|---|---|---|")
    for label, (k, n) in o["recovery"].items():
        sk, sn = o["recovery_2011_2014_sensitivity"][label]
        lines.append("| %s | %d | %d | %d/%d |" % (label, k, n, sk, sn))
    lines += ["", "Onside spot records from the 35: %d kicking-club, %d receiving-club; checks %s." % (
        len(o["spot_records_from_35"]["kicking"]), len(o["spot_records_from_35"]["receiving"]),
        ", ".join("%s %d" % kv for kv in o["spot_record_checks"].items())), ""]
    n = art["non_offensive"]
    lines.append("| Unit | Touchdowns | Units | Season LR p | LOS LR p | Bins adopted |")
    lines.append("|---|---|---|---|---|---|")
    for name in ("interception", "fumble_lost", "punt", "missed_field_goal", "kickoff", "safety_free_kick"):
        v = n[name]
        lines.append("| %s | %d | %d | %s | %s | %s |" % (
            name, v["pooled"][0], v["pooled"][1], "%.3f" % v["season_lr"]["p"] if v["season_lr"] else "-",
            "%.4f" % v["los_lr"]["p"] if v.get("los_lr") else "-", v.get("bins_adopted", "-")))
    lines += ["", "Return-touchdown records kept: %s; checks %s." % (
        ", ".join("%s %d" % (k, len(v)) for k, v in n["records"].items() if isinstance(v, list)),
        ", ".join("%s %d" % kv for kv in n["records"]["checks"].items())), ""]
    p = art.get("try_snap_participation")
    if p:
        lines.append("Try-snap participation (2013 snap counts): %+.2f offensive and %+.2f defensive snaps per two-point "
                     "try (SE %.2f and %.2f; %d and %d club-games)." % (
                         p["offense"]["per_two_point_try"], p["defense"]["per_two_point_try"], p["offense"]["se"],
                         p["defense"]["se"], p["offense"]["club_games"], p["defense"]["club_games"]))
        lines.append("")
    lines.append("**Second pass (nflscrapR)**")
    lines.append("")
    lines.append("| Metric | nflverse | nflscrapR |")
    lines.append("|---|---|---|")
    for row in art["second_pass"]["comparison"]:
        lines.append("| %s | %d/%d | %d/%d |" % (row["metric"], row["nflverse"][0], row["nflverse"][1],
                                                 row["nflscrapr"][0], row["nflscrapr"][1]))
    sp = art["second_pass"]
    lines += ["", "Chart season drift, pass 2: p %.3f; onside chart drift, pass 2: p %.3f; onside share LR, pass 2: "
              "p %.3f." % (sp["chart_season_drift"]["nflscrapr"]["p"], sp["onside_chart_season_drift"]["nflscrapr"]["p"],
                           sp["onside_share_season_lr"]["nflscrapr"]["p"])]
    return "\n".join(lines) + "\n"


def render_record(art, text):
    if BEGIN not in text or END not in text:
        raise ValueError("%s lacks its generated markers" % RECORD)
    head, rest = text.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    return head + BEGIN + "\n" + tables(art) + END + tail


def render(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seasons", choices=sorted(MODES), default="2010-2014w4")
    parser.add_argument("--sources", type=Path, default=sources.default_dest())
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.sources is None or not Path(args.sources).is_dir():
        print("sources not present (set $SOURCES_2010_2014_DIR or --sources); nothing built", file=sys.stderr)
        return 2
    art, errors = build(args.sources, MODES[args.seasons], log=lambda m: print(m, file=sys.stderr))
    if errors:
        for e in errors:
            print("BUILD FAILURE: " + e, file=sys.stderr)
        return 1
    if args.seasons != "2010-2014w4":
        print(render(art)[:2000])
        return 0
    text = render(art)
    record = render_record(art, RECORD.read_text())
    if args.check:
        ok = OUT.exists() and OUT.read_text() == text
        ok_md = RECORD.read_text() == record
        print("%s %s" % ("reproduced" if ok else "DIFFERS", OUT.relative_to(ROOT)))
        print("%s %s (generated tables)" % ("reproduced" if ok_md else "DIFFERS", RECORD.relative_to(ROOT)))
        return 0 if ok and ok_md else 1
    OUT.write_text(text)
    RECORD.write_text(record)
    print("wrote %s (%d bytes) and the tables of %s" % (OUT.relative_to(ROOT), len(text), RECORD.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
