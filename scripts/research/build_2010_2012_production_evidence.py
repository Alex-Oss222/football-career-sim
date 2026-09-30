#!/usr/bin/env python3
"""Build the 2010-2012 pre-divergence production evidence (E1 second stream).

  python scripts/research/build_2010_2012_production_evidence.py SOURCE_DIR

SOURCE_DIR holds the pinned nflverse files named in SOURCES: the official
regular-season player statistics (stats_player_reg_{2010,2011,2012}.csv), the
play-by-play files used for the separate verification pass
(play_by_play_{season}.csv.gz) and the weekly depth charts used for
offensive-line starts (depth_charts_{season}.csv).

Outputs library/data/2010_2012_production_evidence.json. The prose report is
library/2010_2012_production_evidence.md.

Two passes, kept apart in the output:

* Research pass: every metric below from the stats_player file (nflverse's
  redistribution of the official NFL gamebook totals, with its EPA sums).
* Verification pass: the same counts and EPA sums recomputed from scratch from
  the play-by-play file, play by play, by gsis id. A season row is
  "Confirmed two-pass" when both computations agree inside the declared
  tolerance, "Corrected" when the play-by-play recomputation is adopted over
  the stats file, and "Unverified" when the second computation could not be
  made. The 20-player spot check against public search summaries is recorded
  in the Markdown report, not here.

Everything in PREREGISTERED was written before the first run and is not
changed after results are seen: the metrics, the qualifying minimums, the
league-mean shrinkage, and the fixed percentile cut-points that turn a
metric into the five-tier scale. No post-divergence (2013 or later) real
season is read; no branch record is read; no club is treated differently.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "library/data/2010_2012_production_evidence.json"
SEASONS = (2010, 2011, 2012)
DIVERGENCE = "2013-01-15"
BASE = "https://github.com/nflverse/nflverse-data/releases/download/"
SOURCES = {
    **{f"stats_player_reg_{s}.csv": BASE + f"stats_player/stats_player_reg_{s}.csv" for s in SEASONS},
    **{f"play_by_play_{s}.csv.gz": BASE + f"pbp/play_by_play_{s}.csv.gz" for s in SEASONS},
    **{f"depth_charts_{s}.csv": BASE + f"depth_charts/depth_charts_{s}.csv" for s in SEASONS},
}

PREREGISTERED = {
    "written_before_first_run": "2026-09-30",
    "scope": "NFL regular seasons 2010, 2011 and 2012 only; every player with a qualifying season; "
             "keyed by nflverse gsis id",
    "public_date_rule": "a season's final regular-season statistics are public on the date of its last "
                        "regular-season game (recorded per season from the play-by-play game dates); every "
                        "such date precedes the divergence 2013-01-15, so the whole file is admissible pre-divergence "
                        "evidence. nflverse's EPA is a later-computed function of those same contemporaneous plays "
                        "(a derivative, not new information), recorded as a contamination note.",
    "groups": {
        "QB": ["QB"], "RB": ["RB", "HB", "FB"], "WR": ["WR"], "TE": ["TE"],
        "OL": ["T", "G", "C", "OT", "OG", "OL", "LT", "LG", "RG", "RT"],
        "DL": ["DE", "DT", "NT", "DL"], "LB": ["LB", "OLB", "ILB", "MLB"],
        "DB": ["CB", "S", "SS", "FS", "DB", "SAF"], "K": ["K", "PK"], "P": ["P"],
    },
    "metrics": {
        "QB": {"name": "epa_per_dropback", "numerator": "passing_epa", "denominator": "attempts + sacks_suffered",
               "minimum": 200, "shrink_k": 100},
        "RB": {"name": "epa_per_opportunity", "numerator": "rushing_epa + receiving_epa",
               "denominator": "carries + targets", "minimum": 100, "shrink_k": 50},
        "WR": {"name": "epa_per_opportunity", "numerator": "rushing_epa + receiving_epa",
               "denominator": "carries + targets", "minimum": 60, "shrink_k": 50},
        "TE": {"name": "epa_per_opportunity", "numerator": "rushing_epa + receiving_epa",
               "denominator": "carries + targets", "minimum": 40, "shrink_k": 50},
        "OL": {"name": "job_evidence_only", "numerator": "starts (weeks on the club's weekly depth chart, "
               "depth_team 1, formation Offense, regular season) and games played",
               "denominator": None, "minimum": 1, "shrink_k": None,
               "note": "no production line and no tier: starts and games are job evidence"},
        "DL": {"name": "disruption_per_game",
               "numerator": "def_sacks + 0.5 * def_qb_hits + def_tackles_for_loss + def_interceptions + 0.5 * def_pass_defended",
               "denominator": "games", "minimum": 8, "shrink_k": 4},
        "LB": {"name": "disruption_per_game",
               "numerator": "def_sacks + 0.5 * def_qb_hits + def_tackles_for_loss + def_interceptions + 0.5 * def_pass_defended",
               "denominator": "games", "minimum": 8, "shrink_k": 4},
        "DB": {"name": "disruption_per_game",
               "numerator": "def_sacks + 0.5 * def_qb_hits + def_tackles_for_loss + def_interceptions + 0.5 * def_pass_defended",
               "denominator": "games", "minimum": 8, "shrink_k": 4},
        "K": {"name": "fg_made_over_expected_per_attempt",
              "numerator": "fg_made - sum over distance bands of (attempts in band x league make rate in band)",
              "denominator": "fg_att", "minimum": 15, "shrink_k": 10,
              "bands": ["0_19", "20_29", "30_39", "40_49", "50_59", "60_"]},
        "P": {"name": "net_yards_per_punt", "numerator": "pt_net_yards", "denominator": "pt_att",
              "minimum": 30, "shrink_k": 10},
    },
    # Returner block (added September 30, 2026 for the kernel 2014.4 candidate's
    # special-teams work; amendment 3 below). A player is tiered as a kick
    # returner and as a punt returner separately from his position group, so
    # the block lives beside `players`, never inside a position row.
    "returner_metrics": {
        "KR": {"name": "kickoff_return_yards_per_return", "numerator": "kickoff_return_yards",
               "denominator": "kickoff_returns", "minimum": 10, "shrink_k": 10},
        "PR": {"name": "punt_return_yards_per_return", "numerator": "punt_return_yards",
               "denominator": "punt_returns (fair catches excluded)", "minimum": 10, "shrink_k": 10},
    },
    "shrinkage": "shrunk = (n x raw + k x league_mean) / (n + k), league_mean = the denominator-weighted mean over "
                 "that season's qualifiers in the group; tiers are cut on the shrunk value",
    "tiers": {
        "rule": "fixed percentile cut-points among that season's qualifiers in the same position group: "
                "share_above = (qualifiers with a strictly higher shrunk value) / qualifiers",
        "Elite": "share_above < 0.10", "Plus": "0.10 <= share_above < 0.30", "Average": "0.30 <= share_above < 0.70",
        "Below-Average": "0.70 <= share_above < 0.90", "Replacement-Level": "share_above >= 0.90",
        "not_a_bespoke_number": "no tier is assigned by judgement; a non-qualifier has no production tier",
    },
    "window": "a player's production tier is the best tier over the two most recent completed pre-divergence "
              "seasons before the season being played (2014 branch: 2011 and 2012; 2012 study target: 2010 and 2011); "
              "for the 2014 branch, 2010 counts only when neither window season qualifies and is discounted one tier "
              "(Elite -> Plus, ..., Replacement-Level stays); the study target has no earlier season built, so no fallback",
    "verification": {
        "method": "recompute every count and EPA sum from the play-by-play file by gsis id",
        "tolerance": {"counts": "exact", "epa_sums": "abs difference <= 1.0 EPA or <= 2% of the larger magnitude",
                      "denominators": "exact for dropbacks, opportunities, punts and field-goal attempts; games +/- 0"},
        "labels": ["Confirmed two-pass", "Corrected", "Unverified"],
        "adoption": "when the two computations disagree beyond tolerance the play-by-play recomputation is adopted "
                    "(Corrected) because it is the more primitive record; when it cannot be made the stats value stands (Unverified)",
    },
    "amendments": [
        {"date": "2026-09-30", "when": "after the first build, before any calibration fit or tier was read",
         "what": "the tackles-for-loss term of disruption_per_game is taken from the play-by-play recomputation in every season "
                 "(tackle_for_loss_1/2_player_id), not from the stats file",
         "why": "the first build found def_tackles_for_loss unpopulated (all zero) in the 2010 and 2011 stats files; "
                "the 2012 column is kept beside the play-by-play count for comparison only"},
        {"date": "2026-09-30", "when": "same first build",
         "what": "the play-by-play recomputation excludes two-point tries from attempts, carries and targets",
         "why": "the official totals in the stats file exclude them; the first build's off-by-one to off-by-three "
                "count differences were all two-point tries"},
        {"date": "2026-09-30", "when": "after the second-pass calibration was accepted, before any phase-2 "
                 "(sub-composite and special-teams) fit was run",
         "what": "a `returners` block (kick and punt return yards per return, minimum 10 returns, shrinkage k 10, the "
                 "same percentile tiers, the same two-pass verification against the play-by-play returner ids) is added "
                 "beside `players`; the `players` block and every existing tier are unchanged",
         "why": "the special-teams strength needs a returner tier and the file carried none; the block is separate "
                "because a returner also holds a position-group row in the same season"},
    ],
    "contamination": [
        "production mixes the player with his teammates, his quarterback or receivers, his blocking and his scheme",
        "EPA is a model quantity computed later from contemporaneous plays; the plays themselves were public on the game date",
        "defensive counting statistics are opportunity-driven and scorer-dependent (assists, QB hits, passes defended)",
        "a percentile tier compares a player only with that season's qualifiers in his group",
    ],
}
TIER_ORDER = ["Elite", "Plus", "Average", "Below-Average", "Replacement-Level"]
GROUP_OF = {label: grp for grp, labels in PREREGISTERED["groups"].items() for label in labels}
OL_LABELS = set(PREREGISTERED["groups"]["OL"])
FG_BANDS = PREREGISTERED["metrics"]["K"]["bands"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def group_of(position):
    return GROUP_OF.get(str(position or "").strip().upper())


# ------------------------------------------------------------- research pass
def research_rows(stats_rows, starts):
    """{gsis: row} of the research-pass metric inputs for one season."""
    out = {}
    for r in stats_rows:
        if r["season_type"] != "REG":
            continue
        grp = group_of(r["position"])
        if grp is None:
            continue
        pid = r["player_id"]
        games = int(num(r["games"]))
        row = {"player_id": pid, "name": r["player_display_name"], "position": r["position"].strip().upper(),
               "group": grp, "club": r["recent_team"], "games": games}
        if grp == "QB":
            row.update(dropbacks=int(num(r["attempts"]) + num(r["sacks_suffered"])), passing_epa=num(r["passing_epa"]),
                       attempts=int(num(r["attempts"])), sacks_suffered=int(num(r["sacks_suffered"])),
                       passing_yards=int(num(r["passing_yards"])), passing_tds=int(num(r["passing_tds"])),
                       interceptions=int(num(r["passing_interceptions"])))
        elif grp in ("RB", "WR", "TE"):
            row.update(opportunities=int(num(r["carries"]) + num(r["targets"])), carries=int(num(r["carries"])),
                       targets=int(num(r["targets"])), rushing_epa=num(r["rushing_epa"]), receiving_epa=num(r["receiving_epa"]),
                       rushing_yards=int(num(r["rushing_yards"])), receiving_yards=int(num(r["receiving_yards"])),
                       receptions=int(num(r["receptions"])))
        elif grp == "OL":
            row.update(starts=starts.get(pid, 0))
        elif grp in ("DL", "LB", "DB"):
            row.update(sacks=num(r["def_sacks"]), qb_hits=int(num(r["def_qb_hits"])), tfl_stats_file=int(num(r["def_tackles_for_loss"])),
                       interceptions=int(num(r["def_interceptions"])), passes_defended=int(num(r["def_pass_defended"])),
                       tackles=int(num(r["def_tackles_solo"]) + num(r["def_tackles_with_assist"])))
        elif grp == "K":
            row.update(fg_att=int(num(r["fg_att"])), fg_made=int(num(r["fg_made"])),
                       fg_by_band={b: [int(num(r["fg_made_" + b])), int(num(r["fg_made_" + b]) + num(r["fg_missed_" + b]))]
                                   for b in FG_BANDS})
        elif grp == "P":
            row.update(punts=int(num(r["pt_att"])), net_yards=int(num(r["pt_net_yards"])), gross_yards=int(num(r["pt_yards"])))
        out[pid] = row
    return out


RETURNER_GROUPS = ("KR", "PR")


def returner_rows(stats_rows):
    """{gsis: {KR: row, PR: row}} research-pass return lines for one season."""
    out = {}
    for r in stats_rows:
        if r["season_type"] != "REG":
            continue
        pid = r["player_id"]
        base = {"player_id": pid, "name": r["player_display_name"], "position": r["position"].strip().upper(),
                "club": r["recent_team"], "games": int(num(r["games"]))}
        kr = int(num(r["kickoff_returns"]))
        pr = int(num(r["punt_returns"]))
        if kr:
            out.setdefault(pid, {})["KR"] = dict(base, group="KR", returns=kr,
                                                 return_yards=int(num(r["kickoff_return_yards"])))
        if pr:
            out.setdefault(pid, {})["PR"] = dict(base, group="PR", returns=pr,
                                                 return_yards=int(num(r["punt_return_yards"])))
    return out


def ol_starts(depth_rows):
    weeks = defaultdict(set)
    for r in depth_rows:
        if r["game_type"] != "REG" or r["depth_team"].strip() != "1" or r["formation"] != "Offense":
            continue
        if r["position"].strip().upper() in OL_LABELS:
            weeks[r["gsis_id"]].add(int(r["week"]))
    return {pid: len(w) for pid, w in weeks.items()}


# --------------------------------------------------------- verification pass
def pbp_recompute(pbp_rows):
    """Independent per-player totals from the play-by-play file."""
    acc = defaultdict(lambda: defaultdict(float))
    dates = set()
    fg_band_totals = {b: [0, 0] for b in FG_BANDS}
    for r in pbp_rows:
        if r["season_type"] != "REG":
            continue
        dates.add(r["game_date"])
        ptype = r["play_type"]
        epa, qb_epa = num(r["epa"]), num(r["qb_epa"])
        passer, rusher, receiver = r["passer_player_id"], r["rusher_player_id"], r["receiver_player_id"]
        # A two-point try is not an attempt, target or carry in the official totals.
        two_point = r["two_point_attempt"] == "1"
        if ptype == "pass" and passer and not two_point:
            acc[passer]["dropbacks"] += 1
            acc[passer]["passing_epa"] += qb_epa
            if r["sack"] == "1":
                acc[passer]["sacks_suffered"] += 1
            else:
                acc[passer]["attempts"] += 1
            if receiver:
                acc[receiver]["targets"] += 1
                acc[receiver]["receiving_epa"] += epa
        elif ptype in ("run", "qb_kneel") and rusher and not two_point:
            acc[rusher]["carries"] += 1
            acc[rusher]["rushing_epa"] += epa
        elif ptype == "qb_spike" and passer:
            # nflverse counts a spike as an attempt and dropback with no EPA on the passer line.
            acc[passer]["dropbacks"] += 1
            acc[passer]["attempts"] += 1
            acc[passer]["passing_epa"] += qb_epa
        for key, field, weight in (("sacks", "sack_player_id", 1.0), ("sacks", "half_sack_1_player_id", 0.5),
                                   ("sacks", "half_sack_2_player_id", 0.5), ("interceptions", "interception_player_id", 1.0),
                                   ("passes_defended", "pass_defense_1_player_id", 1.0), ("passes_defended", "pass_defense_2_player_id", 1.0),
                                   ("qb_hits", "qb_hit_1_player_id", 1.0), ("qb_hits", "qb_hit_2_player_id", 1.0),
                                   ("tfl", "tackle_for_loss_1_player_id", 1.0), ("tfl", "tackle_for_loss_2_player_id", 1.0)):
            if r[field]:
                acc[r[field]][key] += weight
        if ptype == "field_goal" and r["kicker_player_id"]:
            dist = num(r["kick_distance"])
            band = next((b for b, hi in zip(FG_BANDS, (19, 29, 39, 49, 59, 999)) if dist <= hi), FG_BANDS[-1])
            made = r["field_goal_result"] == "made"
            acc[r["kicker_player_id"]]["fg_att"] += 1
            acc[r["kicker_player_id"]]["fg_made"] += made
            acc[r["kicker_player_id"]]["fg_att_" + band] += 1
            acc[r["kicker_player_id"]]["fg_made_" + band] += made
            fg_band_totals[band][0] += made
            fg_band_totals[band][1] += 1
        if ptype == "punt" and r["punter_player_id"] and r["punt_blocked"] != "1":
            acc[r["punter_player_id"]]["punts"] += 1
        # Returns (amendment 3): a kickoff or punt with a named returner and
        # no fair catch; the yards are the row's return_yards.
        if ptype == "kickoff" and r["kickoff_returner_player_id"] and r["kickoff_fair_catch"] != "1":
            acc[r["kickoff_returner_player_id"]]["kr_returns"] += 1
            acc[r["kickoff_returner_player_id"]]["kr_yards"] += num(r["return_yards"])
        if ptype == "punt" and r["punt_returner_player_id"] and r["punt_fair_catch"] != "1":
            acc[r["punt_returner_player_id"]]["pr_returns"] += 1
            acc[r["punt_returner_player_id"]]["pr_yards"] += num(r["return_yards"])
    return acc, max(dates), fg_band_totals


def compare_return(row, check):
    """(label, detail) for one returner line: returns and yards exact."""
    if check is None:
        return "Unverified", {"reason": "player absent from the play-by-play recomputation"}
    key = "kr" if row["group"] == "KR" else "pr"
    detail = {"returns": [row["returns"], check.get(key + "_returns", 0.0)],
              "return_yards": [row["return_yards"], check.get(key + "_yards", 0.0)]}
    ok = all(abs(a - b) < 1e-9 for a, b in detail.values())
    return ("Confirmed two-pass" if ok else "Corrected"), detail


def adopt_return(row, check, label):
    if label != "Corrected":
        return row
    key = "kr" if row["group"] == "KR" else "pr"
    return dict(row, returns=int(check.get(key + "_returns", 0)), return_yards=int(check.get(key + "_yards", 0)))


def build_returners(season, stats, check):
    """The season's returner block: qualifiers, shrinkage and tiers per returner group."""
    rows = returner_rows(stats)
    labelled = defaultdict(dict)
    counts = defaultdict(lambda: defaultdict(int))
    by_group = defaultdict(list)
    for pid, groups in rows.items():
        for grp, row in groups.items():
            label, detail = compare_return(row, check.get(pid))
            used = adopt_return(row, check.get(pid), label)
            used["verification"], used["verification_detail"] = label, detail
            spec = PREREGISTERED["returner_metrics"][grp]
            used["raw"] = used["return_yards"] / used["returns"] if used["returns"] else None
            used["n"] = used["returns"]
            used["qualifies"] = used["raw"] is not None and used["n"] >= spec["minimum"]
            labelled[pid][grp] = used
            if used["qualifies"]:
                by_group[grp].append(used)
    league_means = {}
    for grp, members in by_group.items():
        k = PREREGISTERED["returner_metrics"][grp]["shrink_k"]
        total_n = sum(m["n"] for m in members)
        mean = sum(m["raw"] * m["n"] for m in members) / total_n
        league_means[grp] = {"mean": mean, "qualifiers": len(members), "total_n": total_n, "shrink_k": k}
        for m in members:
            m["shrunk"] = (m["n"] * m["raw"] + k * mean) / (m["n"] + k)
        values = sorted((m["shrunk"] for m in members), reverse=True)
        for m in members:
            above = sum(1 for v in values if v > m["shrunk"])
            m["share_above"] = above / len(members)
            m["tier"] = tier_of(m["share_above"])
            counts[grp][m["tier"]] += 1
            counts[grp][m["verification"]] += 1
    out = {}
    for pid, groups in labelled.items():
        kept = {grp: {k: v for k, v in row.items() if k != "qualifies"} for grp, row in groups.items() if row["qualifies"]}
        if kept:
            out[pid] = kept
    return {"league_means": league_means, "counts": {g: dict(c) for g, c in counts.items()}, "rows": out}


def compare(row, check):
    """(label, detail) for one season row against the play-by-play recomputation."""
    grp = row["group"]
    if grp == "OL":
        return "Job evidence", {}
    if check is None and grp in ("DL", "LB", "DB"):
        # A defender named on no play-by-play event has zero of every count
        # there; the stats file's zeros are compared against that.
        check = {}
    if check is None:
        return "Unverified", {"reason": "player absent from the play-by-play recomputation"}
    detail = {}
    exact_ok = True
    epa_ok = True

    def count(key, mine):
        nonlocal exact_ok
        theirs = check.get(key, 0.0)
        detail[key] = [mine, theirs]
        if abs(mine - theirs) > 1e-9:
            exact_ok = False

    def epa(key, mine):
        nonlocal epa_ok
        theirs = check.get(key, 0.0)
        detail[key] = [round(mine, 3), round(theirs, 3)]
        if abs(mine - theirs) > max(1.0, 0.02 * max(abs(mine), abs(theirs))):
            epa_ok = False

    if grp == "QB":
        count("dropbacks", row["dropbacks"])
        epa("passing_epa", row["passing_epa"])
    elif grp in ("RB", "WR", "TE"):
        count("carries", row["carries"])
        count("targets", row["targets"])
        epa("rushing_epa", row["rushing_epa"])
        epa("receiving_epa", row["receiving_epa"])
    elif grp in ("DL", "LB", "DB"):
        for key in ("sacks", "qb_hits", "interceptions", "passes_defended"):
            count(key, row[key])
        # Amendment 1 (see PREREGISTERED["amendments"]): the TFL term is the
        # play-by-play count in every season; the stats file's column is
        # recorded beside it for the 2012 comparison only.
        detail["tfl_stats_file_vs_pbp"] = [row["tfl_stats_file"], check.get("tfl", 0.0)]
    elif grp == "K":
        count("fg_att", row["fg_att"])
        count("fg_made", row["fg_made"])
    elif grp == "P":
        count("punts", row["punts"])
    if exact_ok and epa_ok:
        return "Confirmed two-pass", detail
    return "Corrected", detail


def adopt(row, check, label):
    """The values used for the metric: the play-by-play recomputation when Corrected."""
    if label != "Corrected":
        return row
    fixed = dict(row)
    grp = row["group"]
    if grp == "QB":
        fixed["dropbacks"] = int(check.get("dropbacks", 0))
        fixed["passing_epa"] = check.get("passing_epa", 0.0)
    elif grp in ("RB", "WR", "TE"):
        fixed["carries"], fixed["targets"] = int(check.get("carries", 0)), int(check.get("targets", 0))
        fixed["opportunities"] = fixed["carries"] + fixed["targets"]
        fixed["rushing_epa"], fixed["receiving_epa"] = check.get("rushing_epa", 0.0), check.get("receiving_epa", 0.0)
    elif grp in ("DL", "LB", "DB"):
        for key in ("sacks", "qb_hits", "interceptions", "passes_defended"):
            fixed[key] = check.get(key, 0.0)
    elif grp == "K":
        fixed["fg_att"], fixed["fg_made"] = int(check.get("fg_att", 0)), int(check.get("fg_made", 0))
        fixed["fg_by_band"] = {b: [int(check.get("fg_made_" + b, 0)), int(check.get("fg_att_" + b, 0))] for b in FG_BANDS}
    elif grp == "P":
        fixed["punts"] = int(check.get("punts", 0))
    return fixed


# ------------------------------------------------------------------ metrics
def raw_metric(row, league_fg_rates):
    grp = row["group"]
    if grp == "QB":
        return (row["passing_epa"] / row["dropbacks"] if row["dropbacks"] else None), row["dropbacks"]
    if grp in ("RB", "WR", "TE"):
        n = row["opportunities"]
        return ((row["rushing_epa"] + row["receiving_epa"]) / n if n else None), n
    if grp in ("DL", "LB", "DB"):
        n = row["games"]
        value = row["sacks"] + 0.5 * row["qb_hits"] + row["tfl"] + row["interceptions"] + 0.5 * row["passes_defended"]
        return (value / n if n else None), n
    if grp == "K":
        n = row["fg_att"]
        expected = sum(att * league_fg_rates[b] for b, (made, att) in row["fg_by_band"].items())
        return ((row["fg_made"] - expected) / n if n else None), n
    if grp == "P":
        n = row["punts"]
        return (row["net_yards"] / n if n else None), n
    return None, None


def tier_of(share_above):
    if share_above < 0.10:
        return "Elite"
    if share_above < 0.30:
        return "Plus"
    if share_above < 0.70:
        return "Average"
    if share_above < 0.90:
        return "Below-Average"
    return "Replacement-Level"


def build_season(season, source):
    stats = read(source / f"stats_player_reg_{season}.csv")
    depth = read(source / f"depth_charts_{season}.csv")
    pbp = read(source / f"play_by_play_{season}.csv.gz")
    starts = ol_starts(depth)
    rows = research_rows(stats, starts)
    check, last_game, fg_band_totals = pbp_recompute(pbp)
    league_fg_rates = {b: (made / att if att else 0.0) for b, (made, att) in fg_band_totals.items()}
    labelled = {}
    counts = defaultdict(lambda: defaultdict(int))
    for pid, row in rows.items():
        label, detail = compare(row, check.get(pid))
        used = adopt(row, check.get(pid), label)
        if row["group"] in ("DL", "LB", "DB"):
            used["tfl"] = (check.get(pid) or {}).get("tfl", 0.0)
            used["tfl_source"] = "play_by_play"
        used["verification"] = label
        used["verification_detail"] = detail
        labelled[pid] = used
    # qualifiers, shrinkage and tiers per group
    by_group = defaultdict(list)
    for pid, row in labelled.items():
        spec = PREREGISTERED["metrics"][row["group"]]
        if row["group"] == "OL":
            row["qualifies"] = row["starts"] >= 1 or row["games"] >= 1
            continue
        value, n = raw_metric(row, league_fg_rates)
        row["raw"], row["n"] = value, n
        row["qualifies"] = value is not None and n >= spec["minimum"]
        if row["qualifies"]:
            by_group[row["group"]].append(row)
    league_means = {}
    for grp, members in by_group.items():
        k = PREREGISTERED["metrics"][grp]["shrink_k"]
        total_n = sum(m["n"] for m in members)
        mean = sum(m["raw"] * m["n"] for m in members) / total_n
        league_means[grp] = {"mean": mean, "qualifiers": len(members), "total_n": total_n, "shrink_k": k}
        for m in members:
            m["shrunk"] = (m["n"] * m["raw"] + k * mean) / (m["n"] + k)
        values = sorted((m["shrunk"] for m in members), reverse=True)
        for m in members:
            above = sum(1 for v in values if v > m["shrunk"])
            m["share_above"] = above / len(members)
            m["tier"] = tier_of(m["share_above"])
            counts[grp][m["tier"]] += 1
            counts[grp][m["verification"]] += 1
    out = {}
    for pid, row in labelled.items():
        if not row.get("qualifies"):
            continue
        entry = {k: v for k, v in row.items() if k not in ("qualifies",)}
        entry.setdefault("tier", None)
        out[pid] = entry
    return {"season": season, "public_date": last_game, "admissible_pre_divergence": last_game < DIVERGENCE,
            "league_fg_make_rate_by_band": league_fg_rates, "league_means": league_means,
            "counts": {g: dict(c) for g, c in counts.items()}, "rows": out,
            "returners": build_returners(season, stats, check)}


def main():
    source = Path(sys.argv[1])
    seasons = {}
    for season in SEASONS:
        seasons[season] = build_season(season, source)
        print(season, "public", seasons[season]["public_date"], json.dumps(seasons[season]["counts"], sort_keys=True))
        print(season, "returners", json.dumps(seasons[season]["returners"]["counts"], sort_keys=True))
    returners = {}
    for season, block in seasons.items():
        for pid, groups in block["returners"]["rows"].items():
            slot = returners.setdefault(pid, {"name": next(iter(groups.values()))["name"], "seasons": {}})
            slot["seasons"][str(season)] = {grp: {k: v for k, v in row.items() if k not in ("player_id", "name")}
                                            for grp, row in groups.items()}
    players = {}
    for season, block in seasons.items():
        for pid, row in block["rows"].items():
            slot = players.setdefault(pid, {"name": row["name"], "seasons": {}})
            slot["name"] = row["name"]
            slot["seasons"][str(season)] = {k: v for k, v in row.items() if k not in ("player_id", "name")}
    summary = {"players": len(players),
               "player_seasons": sum(len(p["seasons"]) for p in players.values()),
               "verification": {}}
    for label in ("Confirmed two-pass", "Corrected", "Unverified", "Job evidence"):
        summary["verification"][label] = sum(1 for p in players.values() for s in p["seasons"].values()
                                             if s["verification"] == label)
    summary["returners"] = {"players": len(returners),
                            "player_seasons": sum(len(p["seasons"]) for p in returners.values()),
                            "verification": {}}
    for label in ("Confirmed two-pass", "Corrected", "Unverified"):
        summary["returners"]["verification"][label] = sum(
            1 for p in returners.values() for season in p["seasons"].values() for row in season.values()
            if row["verification"] == label)
    output = {
        "schema_version": 1,
        "built_by": "scripts/research/build_2010_2012_production_evidence.py",
        "policy": "runtime/2014_engine_decisions.md E1 (dated public evidence before the divergence); "
                  "runtime/defect_register.md item 1; second evidence stream beside library/data/2010_2012_honours_evidence.json",
        "divergence": DIVERGENCE,
        "preregistered": PREREGISTERED,
        "sources": {name: {"url": url, "sha256": sha(source / name)} for name, url in SOURCES.items()},
        "seasons": {str(s): {k: (v if k != "returners" else {kk: vv for kk, vv in v.items() if kk != "rows"})
                             for k, v in block.items() if k != "rows"} for s, block in seasons.items()},
        "summary": summary,
        "players": players,
        "returners": returners,
    }
    OUT.write_text(json.dumps(output, indent=0, sort_keys=True, default=float) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
