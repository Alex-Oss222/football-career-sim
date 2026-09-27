#!/usr/bin/env python3
"""Rebuild the 2012 NFL offensive-drive model used by kernel 2013.6.

Research tool only; the runtime never downloads or parses play-by-play. Fetch
the two inputs first (they are large and are not committed; the SHA-256 of each
is pinned below and checked before anything is read):

  nflverse play-by-play (primary pass):
    https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2012.csv.gz
  nflscrapR play-by-play (second pass):
    https://raw.githubusercontent.com/ryurko/nflscrapR-data/master/play_by_play_data/regular_season/reg_pbp_2012.csv

Usage:
  python scripts/research/build_2012_drive_model.py [--sources DIR] [--out PATH] [--check]

--check rebuilds in memory and exits non-zero unless the committed artifact is
reproduced byte-for-byte. Only 2012 regular-season plays are read. The
artifact holds no team or game identifiers.

Both passes derive from the NFL Game Statistics and Information System (GSIS)
feed, so the second pass verifies the classifier and the file parse, not an
independent observation of the season. The Pro Football Reference drive table
(5,360 drives, 2,520 punts) could not be reached through the session proxy and
remains an unresolved cross-check.

The builder exits non-zero when any reconciliation fails or when the second
pass shows an unexplained deviation (over 1% in a count, or over 0.6 yards in
a mean net-yards figure).
"""
from __future__ import annotations

import argparse
import collections
import csv
import gzip
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCES = ROOT / ".sim_cache" / "sources"
DEFAULT_OUT = ROOT / "library" / "data" / "2012_nfl_drive_model.json"
BASELINE = ROOT / "library" / "data" / "2012_nfl_aggregate_baseline.json"

INPUTS = {
    "nflverse": {
        "file": "play_by_play_2012.csv.gz",
        "url": "https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2012.csv.gz",
        "sha256": "ff1cda2e26610ef8720324e442d1e5ebc24918e08fd1d2933590b7b91a7068cd",
        "drive_key": "fixed_drive",
    },
    "nflscrapr": {
        "file": "reg_pbp_2012.csv",
        "url": "https://raw.githubusercontent.com/ryurko/nflscrapR-data/master/play_by_play_data/regular_season/reg_pbp_2012.csv",
        "sha256": "9129396fc41597f9f44ab14d4d0fca890a3c56fea686b0b7dc92885aaedd0f98",
        "drive_key": "drive",
    },
}

SCRIMMAGE = {"pass", "run", "qb_kneel", "qb_spike"}
OFFENSIVE = SCRIMMAGE | {"punt", "field_goal"}

CATEGORIES = (
    "touchdown", "field_goal_attempt", "punt", "interception",
    "fumble_lost", "downs", "safety", "clock",
)
# Pre-registered before any 2013.6 measurement; never tuned after results.
BUCKET_EDGES = ((0, 30), (31, 60), (61, 120), (121, 240), (241, 1800))
MIN_BUCKET_DRIVES = 30
FG_BINS = (("<30", 0, 29), ("30-39", 30, 39), ("40-49", 40, 49), ("50+", 50, 99))

EXPECTED_DRIVES = 5984
TEAM_GAMES = 512
GAMES = 256
PLAYS_TOLERANCE = 0.1
YARDS_TOLERANCE = 1.0
COUNT_TOLERANCE = 0.01
MEAN_YARDS_TOLERANCE = 0.6

# Second-pass deviations explained by coding differences in the nflscrapR
# file, each confirmed against the play descriptions during research.
EXPLAINED = {
    "extra_point_attempts": "nflscrapR is missing 115 extra-point rows (1,122 against 1,237); the same 8 non-good kicks appear in both files.",
    "extra_points_made": "nflscrapR is missing 115 extra-point rows.",
    "two_point_attempts": "nflscrapR is missing 6 two-point rows.",
    "two_point_made": "nflscrapR is missing 6 two-point rows (2 successes).",
    "category:other": "nflscrapR has 92 fewer pass, 11 fewer punt and 3 fewer field-goal rows and 64 more no_play rows than nflverse, so some drives lose their terminal offensive play.",
    "category:punt": "nflscrapR has 11 fewer punt rows.",
    "category:field_goal_attempt": "nflscrapR has 3 fewer field-goal rows.",
    "fg_blocked": "Two kicks (2012101407 play 4223, 2012110400 play 3608) are BLOCKED in the nflverse descriptions but No Good in the nflscrapR descriptions. The sources disagree and the blocked/missed split is unresolved; made and attempted totals are identical and the kernel does not distinguish blocked from missed.",
    "fg_missed": "Same two blocked kicks as fg_blocked.",
    "duplicate_td": "nflscrapR repeats one touchdown description (2012112200, plays 2563 and 2658, the second with a penalty appended).",
}


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def rows(path, source):
    handle = gzip.open(path, "rt", newline="") if path.suffix == ".gz" else open(path, newline="")
    with handle:
        for r in csv.DictReader(handle):
            if source == "nflverse" and r.get("season_type") != "REG":
                continue
            yield {k: ("" if v == "NA" else v) for k, v in r.items()}


def num(r, k):
    try:
        return float(r.get(k, ""))
    except ValueError:
        return None


def flag(r, k):
    return num(r, k) == 1.0


def is_off(r, pos=None):
    """Offensive snap of the drive; two-point tries are conversion plays."""
    if r.get("two_point_conv_result") or flag(r, "two_point_attempt"):
        return False
    live_no_play = r.get("play_type") == "no_play" and any(
        flag(r, k) for k in ("interception", "fumble_lost", "touchdown", "safety", "fourth_down_failed"))
    if r.get("play_type") not in OFFENSIVE and not live_no_play:
        return False
    return pos is None or r.get("posteam") == pos


def classify(offs, pos, last_in_half):
    """Result of one offensive drive from its last offensive play.

    Order: TD > safety > FG made/missed > punt > INT > fumble lost > downs >
    clock. Returns (raw_result, category, remap_kind).
    """
    t = offs[-1]
    if flag(t, "touchdown"):
        if t.get("td_team") == pos:
            return "touchdown", "touchdown", None
        # Opponent touchdown: remap to the play that caused it.
        if flag(t, "interception"):
            return "opp_touchdown", "interception", "interception_return"
        if flag(t, "fumble_lost"):
            return "opp_touchdown", "fumble_lost", "fumble_return"
        if t.get("play_type") == "punt":
            return "opp_touchdown", "punt", "punt_return_or_block"
        if t.get("play_type") == "field_goal":
            return "opp_touchdown", "field_goal_attempt", "blocked_field_goal_return"
        if flag(t, "fourth_down_failed"):
            return "opp_touchdown", "downs", "other_by_terminal_play"
        return "opp_touchdown", "unclassified", "other_by_terminal_play"
    if flag(t, "safety"):
        return "safety", "safety", None
    if t.get("play_type") == "field_goal":
        made = t.get("field_goal_result") == "made"
        return ("field_goal_made" if made else "missed_field_goal"), "field_goal_attempt", None
    if t.get("play_type") == "punt":
        return "punt", "punt", None
    if flag(t, "interception"):
        return "interception", "interception", None
    if flag(t, "fumble_lost"):
        return "fumble_lost", "fumble_lost", None
    if flag(t, "fourth_down_failed"):
        return "turnover_on_downs", "downs", None
    if last_in_half:
        half = t.get("game_half")
        return ("end_of_game" if half in ("Half2", "Overtime") else "end_of_half"), "clock", None
    return "other", "other", None


def bucket_index(seconds):
    for index, (low, high) in enumerate(BUCKET_EDGES):
        if seconds <= high:
            return index
    return len(BUCKET_EDGES) - 1


def fg_bin(distance):
    for label, low, high in FG_BINS:
        if distance <= high:
            return label
    return FG_BINS[-1][0]


def clock_seconds(text):
    if text and ":" in text:
        minutes, seconds = text.split(":")[:2]
        return int(minutes) * 60 + int(float(seconds))
    return None


def extract(path, source):
    """Return offensive drives plus play-level kicking counts for one source."""
    drive_key = INPUTS[source]["drive_key"]
    games = collections.OrderedDict()
    kicks = collections.Counter()
    fg_bins = collections.defaultdict(lambda: [0, 0])
    for r in rows(path, source):
        games.setdefault(r["game_id"], []).append(r)
        if r.get("field_goal_result"):
            kicks["fg_attempts"] += 1
            kicks["fg_" + r["field_goal_result"]] += 1
            distance = num(r, "kick_distance")
            if distance is not None:
                cell = fg_bins[fg_bin(distance)]
                cell[1] += 1
                cell[0] += r["field_goal_result"] == "made"
        if r.get("extra_point_result"):
            kicks["extra_point_attempts"] += 1
            kicks["extra_points_made"] += r["extra_point_result"] == "good"
        if r.get("two_point_conv_result"):
            kicks["two_point_attempts"] += 1
            kicks["two_point_made"] += r["two_point_conv_result"] == "success"
        if flag(r, "safety"):
            kicks["safeties"] += 1

    drives = []
    safety_kicks = [0, 0]  # returned, not returned
    for gid, plays in games.items():
        # Free kick after each safety: the next kickoff row of the game.
        for index, r in enumerate(plays):
            if not flag(r, "safety"):
                continue
            for nxt in plays[index + 1:]:
                if nxt.get("play_type") == "kickoff" or flag(nxt, "kickoff_attempt"):
                    returned = bool(nxt.get("kickoff_returner_player_id") or nxt.get("kickoff_returner_player_name"))
                    safety_kicks[0 if returned else 1] += 1
                    break

        groups = collections.OrderedDict()
        for r in plays:
            groups.setdefault(r.get(drive_key, ""), []).append(r)
        offensive = []
        for key, grp in groups.items():
            teams = collections.Counter(r["posteam"] for r in grp if is_off(r) and r.get("posteam"))
            if not teams:
                continue
            pos = teams.most_common(1)[0][0]
            offs = [r for r in grp if is_off(r, pos)]
            if not offs:
                continue
            offensive.append({"posteam": pos, "plays": grp, "offs": offs, "half": offs[-1].get("game_half")})
        for i, d in enumerate(offensive):
            last_in_half = i + 1 == len(offensive) or offensive[i + 1]["half"] != d["half"]
            pos = d["posteam"]
            offs = d["offs"]
            raw, category, remap = classify(offs, pos, last_in_half)
            snaps = [r for r in d["plays"] if r.get("posteam") == pos and (is_off(r) or r.get("play_type") == "no_play")]
            first = snaps[0] if snaps else offs[0]
            start = num(first, "yardline_100")
            t = offs[-1]
            if category == "touchdown":
                end = 0.0
            elif t.get("play_type") in ("punt", "field_goal"):
                end = num(t, "yardline_100")
            else:
                end = (num(t, "yardline_100") or 0) - (num(t, "yards_gained") or 0)
            n_plays = sum(1 for r in offs if r.get("play_type") in SCRIMMAGE)
            fg = None
            if category == "field_goal_attempt":
                distance = num(t, "kick_distance")
                fg = (
                    None if distance is None else int(distance),
                    int(t.get("field_goal_result") == "made"),
                    int(t.get("field_goal_result") == "blocked"),
                )
            half = d["half"]
            drives.append({
                "raw": raw,
                "category": category,
                "remap": remap,
                "plays": n_plays,
                "net": None if start is None or end is None else int(round(start - end)),
                "seconds": clock_seconds(d["plays"][-1].get("drive_time_of_possession", "")),
                "fg": fg,
                "half_final": bool(last_in_half and half in ("Half1", "Half2")),
                "half_seconds": num(first, "half_seconds_remaining"),
                "overtime": half == "Overtime",
                "ident": (gid, str(d["plays"][0].get("play_id", ""))),
            })
    return {"games": len(games), "drives": drives, "kicks": kicks,
            "fg_bins": {k: v for k, v in fg_bins.items()}, "safety_kicks": safety_kicks}


def build_model(primary, baseline):
    drives = primary["drives"]
    errors = []
    unclassified = [d["ident"] for d in drives if d["category"] not in CATEGORIES]
    if unclassified:
        errors.append("unclassified drives: %s" % unclassified[:10])
    missing_net = [d["ident"] for d in drives if d["net"] is None]
    if missing_net:
        errors.append("drives without a derivable net: %s" % missing_net[:10])

    # Mean seconds per play by category (drives with a recorded time only),
    # used to impute a blank drive time as plays x mean.
    pace = {}
    for category in CATEGORIES:
        timed = [d for d in drives if d["category"] == category and d["seconds"] is not None]
        plays = sum(d["plays"] for d in timed)
        pace[category] = (sum(d["seconds"] for d in timed), plays)
    imputed = collections.Counter()
    for d in drives:
        if d["seconds"] is None:
            total, plays = pace[d["category"]]
            d["seconds"] = int(round(d["plays"] * total / plays)) if plays else 0
            imputed[d["category"]] += 1

    def tuple_of(d):
        row = [d["plays"], d["net"], d["seconds"]]
        if d["category"] == "field_goal_attempt":
            distance, made, blocked = d["fg"]
            row += [distance, made, blocked]
        return row

    raw_bucket_counts = collections.Counter(
        bucket_index(d["half_seconds"]) for d in drives if d["half_final"])
    # Collapse rule, fixed in code: a bucket with fewer than 30 drives merges
    # into the next larger bucket (the largest merges into the next smaller).
    bucket_map = list(range(len(BUCKET_EDGES)))
    counts = [raw_bucket_counts.get(i, 0) for i in range(len(BUCKET_EDGES))]
    for i in range(len(BUCKET_EDGES)):
        target = bucket_map[i]
        if counts[target] >= MIN_BUCKET_DRIVES:
            continue
        nxt = target + 1 if target + 1 < len(BUCKET_EDGES) else target - 1
        while bucket_map[nxt] != nxt:
            nxt = bucket_map[nxt]
        counts[nxt] += counts[target]
        counts[target] = 0
        for j, mapped in enumerate(bucket_map):
            if mapped == target:
                bucket_map[j] = nxt
    keys = ["%d-%d" % edge for edge in BUCKET_EDGES]
    pool_keys = [keys[bucket_map[i]] for i in range(len(BUCKET_EDGES))]

    interior = {c: [] for c in CATEGORIES}
    half_final = {}
    for d in drives:
        if d["half_final"]:
            key = pool_keys[bucket_index(d["half_seconds"])]
            half_final.setdefault(key, {c: [] for c in CATEGORIES})[d["category"]].append(tuple_of(d))
        else:
            interior[d["category"]].append(tuple_of(d))
    interior_counts = {c: len(v) for c, v in interior.items()}
    half_final_counts = {k: {c: len(v) for c, v in pools.items()} for k, pools in sorted(half_final.items())}

    all_tuples = [(d["category"], tuple_of(d)) for d in drives]
    net_range = {}
    for category in CATEGORIES:
        nets = [t[1] for c, t in all_tuples if c == category]
        net_range[category] = [min(nets), max(nets)] if nets else None
    total_seconds = sum(t[2] for _, t in all_tuples)
    total_plays = sum(t[0] for _, t in all_tuples)
    total_net = sum(t[1] for _, t in all_tuples)
    fg_tuples = [t for c, t in all_tuples if c == "field_goal_attempt"]
    missing_distance = sum(1 for t in fg_tuples if t[3] is None)
    if missing_distance:
        errors.append("%d field-goal drives without a kick distance" % missing_distance)

    category_counts = collections.Counter(d["category"] for d in drives)
    remap_counts = collections.Counter(d["remap"] for d in drives if d["remap"])
    raw_counts = collections.Counter(d["raw"] for d in drives)
    kicks = primary["kicks"]
    totals = baseline["period_totals"]
    model = baseline["model"]

    plays_per_team_game = total_plays / TEAM_GAMES
    net_per_team_game = total_net / TEAM_GAMES
    reconciliation = {
        "drives": {"observed": len(drives), "expected": EXPECTED_DRIVES,
                   "interior": sum(interior_counts.values()),
                   "half_final": sum(sum(v.values()) for v in half_final_counts.values())},
        "field_goal_attempts": {"observed": category_counts["field_goal_attempt"], "expected": totals["field_goal_attempts"]},
        "field_goals_made": {"observed": sum(t[4] for t in fg_tuples), "expected": totals["field_goals_made"]},
        "interceptions": {"observed": category_counts["interception"], "expected": totals["interceptions"]},
        "plays_per_team_game": {"observed": round(plays_per_team_game, 4), "expected": model["plays_per_team_game"], "tolerance": PLAYS_TOLERANCE},
        "net_yards_per_team_game": {"observed": round(net_per_team_game, 4), "expected": model["yards_per_team_game"], "tolerance": YARDS_TOLERANCE},
    }
    r = reconciliation
    if not (r["drives"]["observed"] == EXPECTED_DRIVES == r["drives"]["interior"] + r["drives"]["half_final"]):
        errors.append("drive total does not reconcile: %s" % r["drives"])
    for key in ("field_goal_attempts", "field_goals_made", "interceptions"):
        if r[key]["observed"] != r[key]["expected"]:
            errors.append("%s does not reconcile: %s" % (key, r[key]))
    if abs(plays_per_team_game - model["plays_per_team_game"]) > PLAYS_TOLERANCE:
        errors.append("plays per team-game %.4f outside tolerance" % plays_per_team_game)
    if abs(net_per_team_game - model["yards_per_team_game"]) > YARDS_TOLERANCE:
        errors.append("net yards per team-game %.4f outside tolerance" % net_per_team_game)
    if kicks["fg_attempts"] != totals["field_goal_attempts"] or kicks["fg_made"] != totals["field_goals_made"]:
        errors.append("play-level FG counts do not match period_totals")

    turnovers = category_counts["interception"] + category_counts["fumble_lost"]
    offensive_tds = baseline["tables"]["passing"]["totals"]["TD"] + baseline["tables"]["rushing"]["totals"]["TD"]
    model_out = {
        "schema": "2012-nfl-drive-model-v1",
        "season": 2012,
        "season_type": "regular",
        "information_boundary": "2012 regular-season play-by-play only; no 2013 or later data; no team or game identifiers.",
        "sources": {name: {"file": spec["file"], "url": spec["url"], "sha256": spec["sha256"], "drive_key": spec["drive_key"]}
                    for name, spec in INPUTS.items()},
        "builder": "scripts/research/build_2012_drive_model.py",
        "definitions": {
            "drive": "Offensive possession grouped by the source drive key with at least one offensive snap (pass, run, kneel, spike, punt or field goal by the team in possession; two-point tries excluded; no_play rows count only with an interception, fumble-lost, touchdown, safety or failed-fourth-down flag).",
            "classifier_order": "touchdown > safety > field goal made/missed > punt > interception > fumble lost > downs > clock",
            "clock": "End of half and end of game merged: the final offensive possession of a half that ended without any other result.",
            "tuple": "[plays, net_yards, seconds]; field_goal_attempt adds [kick_distance, made, blocked]",
            "plays": "Scrimmage snaps (pass, run, kneel, spike) on the drive; the punt or field-goal snap is not counted.",
            "net_yards": "Yard line of the first snap minus the end spot: touchdown end = 0, punt/field-goal end = line of scrimmage, otherwise line of scrimmage minus yards gained on the last snap. Penalty yardage is included.",
            "seconds": "Source drive time of possession; when blank, plays x the category's mean seconds per play.",
            "interior": "Drives that are not the final offensive possession of a regulation half (overtime drives are interior).",
            "half_final": "The final offensive possession of each regulation half, keyed by half_seconds_remaining at its first snap.",
        },
        "categories": list(CATEGORIES),
        "remap": {
            "rule": "Opponent-touchdown drives are remapped to the play that caused them; the defence's score is not modelled.",
            "counts": dict(sorted(remap_counts.items())),
        },
        "raw_result_counts": dict(sorted(raw_counts.items())),
        "category_counts": {c: category_counts.get(c, 0) for c in CATEGORIES},
        "bucket_edges": [list(edge) for edge in BUCKET_EDGES],
        "bucket_collapse_rule": "A bucket with fewer than %d drives merges into the next larger bucket (the largest merges into the next smaller)." % MIN_BUCKET_DRIVES,
        "bucket_raw_counts": {keys[i]: raw_bucket_counts.get(i, 0) for i in range(len(BUCKET_EDGES))},
        "bucket_pool": {keys[i]: pool_keys[i] for i in range(len(BUCKET_EDGES))},
        "interior_counts": interior_counts,
        "half_final_counts": half_final_counts,
        "pools": {"interior": interior, "half_final": dict(sorted(half_final.items()))},
        "rates": {
            "fg_by_distance": {label: primary["fg_bins"].get(label, [0, 0]) for label, _, _ in FG_BINS},
            "fg_bin_edges": [[label, low, high] for label, low, high in FG_BINS],
            "field_goal": [kicks["fg_made"], kicks["fg_attempts"]],
            "extra_point": [kicks["extra_points_made"], kicks["extra_point_attempts"]],
            "two_point": [kicks["two_point_made"], kicks["two_point_attempts"]],
            "td_type_pass": [baseline["tables"]["passing"]["totals"]["TD"], offensive_tds],
            "turnover_type_interception": [category_counts["interception"], turnovers],
            "safeties": kicks["safeties"],
            "safety_free_kick_returned": primary["safety_kicks"],
        },
        "clock_scale": [3600 * GAMES, total_seconds],
        "net_range": net_range,
        "imputed_seconds": {"total": sum(imputed.values()), "by_category": dict(sorted(imputed.items()))},
        "reconciliation": reconciliation,
        "verification": {
            "category_counts": "two-source (same GSIS feed), PFR unverified",
            "fg_by_distance": "two-source (same GSIS feed), PFR unverified",
            "field_goal": "two-source (same GSIS feed) plus stored period_totals",
            "extra_point": "partially verified: nflscrapR shows the same 8 non-good kicks but is missing 115 rows; same GSIS feed; PFR unverified",
            "two_point": "single-source (nflverse); nflscrapR is missing 6 rows",
            "safeties": "two-source (same GSIS feed); reconciles to 11,651 points",
            "safety_free_kick_returned": "single-source (nflverse)",
            "td_type_pass": "stored baseline tables (NFL.com team totals)",
            "turnover_type_interception": "derived from the remapped two-source category counts",
            "pools": "single-source tuples (nflverse); second pass checks counts and mean net yards",
            "clock_scale": "single-source (nflverse drive time of possession)",
            "pfr_cross_check": "unresolved: PFR drives (5,360) and punts (2,520) not reachable through the proxy",
        },
    }
    return model_out, errors


def second_pass(primary, secondary):
    """Per-count comparison nflverse vs nflscrapR; returns (block, errors)."""
    def summary(extracted):
        drives = extracted["drives"]
        counts = collections.Counter("category:" + d["category"] for d in drives)
        counts["drives"] = len(drives)
        for key in ("fg_attempts", "fg_made", "fg_missed", "fg_blocked", "extra_point_attempts",
                    "extra_points_made", "two_point_attempts", "two_point_made", "safeties"):
            counts[key] = extracted["kicks"][key]
        means = {}
        for category in CATEGORIES:
            nets = [d["net"] for d in drives if d["category"] == category and d["net"] is not None]
            plays = [d["plays"] for d in drives if d["category"] == category]
            if nets:
                means["net:" + category] = round(sum(nets) / len(nets), 3)
            if plays:
                means["plays:" + category] = round(sum(plays) / len(plays), 3)
        return counts, means

    a_counts, a_means = summary(primary)
    b_counts, b_means = summary(secondary)
    rows_out, errors = [], []
    for key in sorted(set(a_counts) | set(b_counts)):
        a, b = a_counts.get(key, 0), b_counts.get(key, 0)
        rel = abs(a - b) / a if a else (0.0 if b == 0 else float("inf"))
        explained = EXPLAINED.get(key)
        status = "match" if a == b else ("within 1%" if rel <= COUNT_TOLERANCE else ("explained" if explained else "UNEXPLAINED"))
        if status == "UNEXPLAINED":
            errors.append("second pass %s: nflverse %s, nflscrapR %s" % (key, a, b))
        rows_out.append({"metric": key, "nflverse": a, "nflscrapr": b, "status": status,
                         **({"explanation": explained} if status == "explained" else {})})
    for key in sorted(set(a_means) | set(b_means)):
        a, b = a_means.get(key), b_means.get(key)
        tolerance = MEAN_YARDS_TOLERANCE if key.startswith("net:") else None
        if a is None or b is None:
            status = "UNEXPLAINED"
        elif tolerance is None:
            status = "informational"
        else:
            status = "within 0.6 yd" if abs(a - b) <= tolerance else "UNEXPLAINED"
        if status == "UNEXPLAINED":
            errors.append("second pass %s: nflverse %s, nflscrapR %s" % (key, a, b))
        rows_out.append({"metric": key, "nflverse": a, "nflscrapr": b, "status": status})
    block = {
        "source": "nflscrapR reg_pbp_2012.csv, identical classifier, drive key 'drive'",
        "independence": "nflverse and nflscrapR both derive from the NFL GSIS feed; they are not fully independent sources. The PFR cross-check (drives 5,360, punts 2,520) is blocked by the proxy and remains unresolved.",
        "games": secondary["games"],
        "rules": "Any count differing by more than 1%, or any mean net-yards figure differing by more than 0.6 yards, fails the build unless listed with an explanation.",
        "documented_deviations": dict(sorted(EXPLAINED.items())),
        "comparison": rows_out,
        "result": "pass" if not errors else "fail",
    }
    return block, errors


def render(model):
    return json.dumps(model, sort_keys=True, separators=(",", ":")) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true", help="compare with the committed artifact instead of writing")
    args = parser.parse_args(argv)

    errors = []
    paths = {}
    for name, spec in INPUTS.items():
        path = args.sources / spec["file"]
        if not path.exists():
            print("missing source: %s" % path, file=sys.stderr)
            return 2
        digest = sha256(path)
        if digest != spec["sha256"]:
            print("sha256 mismatch for %s: %s" % (path, digest), file=sys.stderr)
            return 2
        paths[name] = path

    baseline = json.loads(BASELINE.read_text())
    primary = extract(paths["nflverse"], "nflverse")
    if primary["games"] != GAMES:
        errors.append("nflverse regular season has %d games" % primary["games"])
    model, build_errors = build_model(primary, baseline)
    errors += build_errors
    secondary = extract(paths["nflscrapr"], "nflscrapr")
    block, pass_errors = second_pass(primary, secondary)
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
