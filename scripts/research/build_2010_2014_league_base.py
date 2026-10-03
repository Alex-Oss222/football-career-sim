#!/usr/bin/env python3
"""Build the kernel 2014.6 league base: field-position model v3, drive model v2 and
aggregate baseline v3 (plan batch B3a, core; B3b, annotations). Data only: no runtime
module reads these files until batch B5.

  python scripts/research/build_2010_2014_league_base.py [--seasons 2010-2014w4|2012]
        [--sources DIR] [--stage core|annotations|all] [--check]

Sources come only through scripts/research/sources_2010_2014.py (the batch B2 gate and
manifest): nflverse play-by-play 2010-2013 and 2014 Weeks 1-4 (primary), nflscrapR
reg_pbp for the same seasons (second pass), the seasonal rosters 2010-2013 and the cut
2014 weekly roster (position groups), and the NFL.com offensive passing and rushing team
tables 2010-2013 (reconciliation). DIR defaults to $SOURCES_2010_2014_DIR.

Rules: library/2014_6_pre_build_specification.md (its sha256 is in every header). The
seasons are pooled with equal weight per event; per-season integer counts are stored.
The drive grouping, classifier, start kinds and transition records are the committed
2012 builders' (scripts/research/league_base_2010_2014.py). Per season, a 2012 run of the
committed build functions on that same extraction must reproduce the committed 2012
artifacts on every key but reconciliation and second_pass, or the build fails.

--check rebuilds in memory and compares with the committed files: --stage core compares
the core fields only (each record's prefix before the annotation fields), --stage
annotations or all compares the whole files byte-for-byte. Without sources present the
check exits 2 (raw data stays out of the repository).

Post-divergence caveat: 2013 and 2014 Weeks 1-4 are an anonymous post-divergence league
population. They enter pooled fits only; no artifact holds a club, game, player or date
field.
"""
from __future__ import annotations

import argparse
import collections
import copy
import csv
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import build_2012_drive_model as dm  # noqa: E402
import build_2012_field_position_model as fp  # noqa: E402
import league_base_2010_2014 as lb  # noqa: E402
import pre_build_specification  # noqa: E402
import sources_2010_2014 as sources  # noqa: E402

ROOT = HERE.parents[1]
DATA = ROOT / "library" / "data"
COMMITTED_2012 = {
    "field_position": DATA / "2012_nfl_field_position_model.json",
    "drive_model": DATA / "2012_nfl_drive_model.json",
    "aggregate": DATA / "2012_nfl_aggregate_baseline.json",
    "usage": DATA / "2012_nfl_position_usage_baseline.json",
}
MODES = {
    "2010-2014w4": {"seasons": (2010, 2011, 2012, 2013, 2014), "stem": "2010_2014w4"},
    "2012": {"seasons": (2012,), "stem": "2012", "suffix": "_v3"},
}

RULES = lb.RULES
EOH = RULES["end_of_half"]
THRESHOLDS = RULES["thresholds"]
FILTERS = RULES["structural_filters"]
MIN_CELL = THRESHOLDS["MIN_CELL"]
K_TRANSITION = THRESHOLDS["K_TRANSITION"]
CATEGORIES = fp.CATEGORIES
START_BINS = fp.START_BINS
NEEDS = tuple((label, low, high) for label, (low, high) in sorted(EOH["NEEDS"].items(), key=lambda kv: kv[1][0]))
LATE_TIME = (("301-600", 301, 600), ("121-300", 121, 300), ("le120", 0, 120))   # game order (committed)
H1_LATE_EDGES = tuple(tuple(e) for e in EOH["H1_LATE_EDGES"])
NEUTRAL_OVER = EOH["NEUTRAL_OVER_SECONDS"]
R17A_LOW, R17A_HIGH = EOH["R17A_TOP_ACCEPT_SECONDS"]
OT_FROM = FILTERS["overtime_from_season"]
KICKOFF_FROM = FILTERS["kickoffs_from_season"]

FP_SCHEMA = "2010-2014w4-nfl-field-position-model-v3"
DM_SCHEMA = "2010-2014w4-nfl-drive-model-v2"
AGG_SCHEMA = "2010-2014w4-nfl-aggregate-baseline-v3"

# Core tuple fields: the v2 fields, then the 2014.6 core additions. Annotation fields follow.
V2_TUPLE_FIELDS = tuple(fp.TUPLE_FIELDS)
CORE_TUPLE_FIELDS = V2_TUPLE_FIELDS + ("season", "seconds_basis", "last_spike_to_end")
ANNOTATION_TUPLE_FIELDS = (
    "rush_yards", "pass_yards", "completions", "sack_losses", "other_yards", "run_values", "completion_values",
    "term_snap", "spike_positions", "pen", "fumbles", "emph", "exposure", "placement",
)
TUPLE_FIELDS = CORE_TUPLE_FIELDS + ANNOTATION_TUPLE_FIELDS
CORE_KICK_FIELDS = tuple(fp.KICK_FIELDS) + ("season",)
KICK_FIELDS = CORE_KICK_FIELDS + ("pen", "spot_adjust", "fumble", "possession", "muffer_role")
CORE_PUNT_FIELDS = tuple(fp.PUNT_FIELDS) + ("season",)
PUNT_FIELDS = CORE_PUNT_FIELDS + ("pen", "spot_adjust", "fumble", "possession", "muffer_role")
TURNOVER_FIELDS = tuple(fp.TURNOVER_FIELDS) + ("season",)
PEN_FIELDS = ("order", "type_code", "side", "signed_yards", "status", "enforce", "first_down", "host",
              "half_distance", "nominal_yards")
FUMBLE_FIELDS = ("snap_order", "kind", "host", "outcome", "forced", "forcer_group", "recoverer_group",
                 "recoverer_is_forcer", "recoverer_is_fumbler")
KICK_PEN_FIELDS = ("type_code", "side", "signed_yards", "status")
SECONDS_BASIS = ("top", "corrected", "imputed")

COUNT_TOLERANCE = 0.01
SHARE_TOLERANCE = 0.01
MEAN_TOLERANCE = 0.6
FG_BINS = dm.FG_BINS


# ============================================================================ extraction

def extract_all(seasons, dest, sources_list=lb.SOURCES, log=None):
    out = {}
    for source in sources_list:
        for s in seasons:
            if log:
                log("extract %s %s" % (source, lb.TAG[s]))
            out[(source, s)] = lb.season(s, source, dest)
    return out


def regression_2012(dest, extracted):
    """The committed 2012 build functions on the 2012 extraction reproduce the committed
    artifacts on every key except reconciliation and second_pass (per-season extraction
    uses the committed functions)."""
    errors = []
    committed_fp = json.loads(COMMITTED_2012["field_position"].read_text())
    committed_dm = json.loads(COMMITTED_2012["drive_model"].read_text())
    usage = json.loads(COMMITTED_2012["usage"].read_text())
    baseline = json.loads(COMMITTED_2012["aggregate"].read_text())
    # Drive model: the committed extractor on the gated, digest-verified file.
    path = sources.source_path(lb.pbp_name(2012, "nflverse"), dest)
    primary_dm = dm.extract(path, "nflverse")
    model_dm, dm_errors = dm.build_model(primary_dm, baseline)
    errors += ["2012 drive model: " + e for e in dm_errors]
    for key in sorted(set(model_dm) | set(committed_dm)):
        if key in ("reconciliation", "second_pass"):
            continue
        if model_dm.get(key) != committed_dm.get(key):
            errors.append("2012 drive model key %s differs from the committed artifact" % key)
    # Field position: fp.extract on the gated rows (the same extraction this build uses).
    rows = lb.load_rows(2012, "nflverse", dest)
    with lb._committed_load(rows):
        primary = fp.extract(path, "nflverse", lb.positions(2012, dest))
    model_fp, fp_errors = fp.build_model(primary, committed_dm, usage)
    errors += ["2012 field position: " + e for e in fp_errors]
    for key in sorted(set(model_fp) | set(committed_fp)):
        if key in ("reconciliation", "second_pass"):
            continue
        if model_fp.get(key) != committed_fp.get(key):
            errors.append("2012 field-position key %s differs from the committed artifact" % key)
    mine = extracted.get(("nflverse", 2012))
    if mine is not None and len(mine["drives"]) != len(primary["drives"]):
        errors.append("2012 drive count differs between the extraction and the committed build")
    return errors


# ============================================================================ R17a seconds

def apply_r17a(drives_by_season):
    """Corrected drive seconds (specification section 4, R17a). Returns the corrections block."""
    diffs = collections.defaultdict(list)
    for drives in drives_by_season.values():
        for c in drives:
            top, e = c["top_first"], c["elapsed"]
            if top is not None and e is not None and R17A_LOW <= top - e <= R17A_HIGH:
                diffs[c["r17a_group"]].append(top - e)
    medians = {g: lb.median_low(sorted(v)) for g, v in sorted(diffs.items())}
    counts = collections.Counter()
    by_season = collections.defaultdict(collections.Counter)
    pace = {}
    for drives in drives_by_season.values():
        for c in drives:
            top, e = c["top_first"], c["elapsed"]
            if top is not None and e is not None and R17A_LOW <= top - e <= R17A_HIGH:
                c["seconds"], c["seconds_basis"] = top, "top"
            elif e is not None and medians.get(c["r17a_group"]) is not None:
                c["seconds"], c["seconds_basis"] = max(0, e + medians[c["r17a_group"]]), "corrected"
            else:
                c["seconds"], c["seconds_basis"] = None, "imputed"
    # A drive with no usable clock keeps the committed pace rule (plays x category pace).
    for category in CATEGORIES:
        timed = [c for drives in drives_by_season.values() for c in drives
                 if c["category"] == category and c["seconds"] is not None]
        pace[category] = (sum(c["seconds"] for c in timed), sum(c["plays"] for c in timed))
    for s, drives in drives_by_season.items():
        for c in drives:
            if c["seconds"] is None:
                total, plays = pace[c["category"]]
                c["seconds"] = int(round(c["plays"] * total / plays)) if plays else 0
            counts[(c["r17a_group"], c["seconds_basis"])] += 1
            by_season[s][c["seconds_basis"]] += 1
            if c["seconds_v2"] != c["seconds"]:
                by_season[s]["changed_from_committed_rule"] += 1
            if c["last_row_top_blank"]:
                by_season[s]["committed_rule_imputed"] += 1
            # Seconds from the last spike to the drive's end, in the drive's own seconds frame.
            if c["last_spike_clock"] is not None and c["first_clock"] is not None:
                c["last_spike_to_end"] = max(0, int(round(c["seconds"] - (c["first_clock"] - c["last_spike_clock"]))))
            else:
                c["last_spike_to_end"] = None
    return {
        "rule": "Drive seconds are the drive time of possession on the first row of the drive group carrying one, "
                "accepted when 0 <= TOP - e <= 45 with e the game-clock seconds from the first snap to the terminal "
                "snap; otherwise e plus the median of TOP - e over the accepted drives of the drive's group "
                "(interior; first-half clock expiry; end-of-game clock). A drive with no usable clock keeps the "
                "committed plays x category-pace rule.",
        "group_medians": medians,
        "accepted_counts": {g: len(v) for g, v in sorted(diffs.items())},
        "by_group_basis": {"%s|%s" % k: v for k, v in sorted(counts.items())},
        "by_season": {lb.TAG[s]: dict(sorted(v.items())) for s, v in sorted(by_season.items())},
    }


def r17a_grouping_reconciliation(dest, seasons, medians):
    """The corrected-drive counts under the nflverse `fixed_drive` grouping (the build) and
    under its `drive` grouping (the review's measurement), counts only: drives whose R17a
    seconds are not their first time of possession (not accepted), and drives whose committed
    value (the last row's time of possession, or the category pace when that is blank) is not
    the R17a value (changed)."""
    out = {}
    for s in seasons:
        rows = lb.load_rows(s, "nflverse", dest)
        result = {}
        for key in ("fixed_drive", "drive"):
            if key == "drive":
                rows = [dict(r, drive_key=r.get("drive") or "") for r in rows]
            fp.annotate_scores(rows)
            drives = fp.build_drives(rows)
            corrected = changed = 0
            for d in drives:
                for r in d["rows"]:
                    if fp.clock_seconds(r.get("drive_time_of_possession", "")) is not None:
                        top = fp.clock_seconds(r["drive_time_of_possession"])
                        break
                else:
                    top = None
                last = fp.clock_seconds(d["rows"][-1].get("drive_time_of_possession", ""))
                first = next((r for r in d["rows"] if r["posteam"] == d["posteam"]
                              and (fp.is_off(r) or r["play_type"] == "no_play") and not fp.is_kick_row(r)),
                             d["offs"][0])
                a, b = lb.clock_of(first), lb.clock_of(d["offs"][-1])
                e = None if a is None or b is None else int(round(a - b))
                accepted = top is not None and e is not None and R17A_LOW <= top - e <= R17A_HIGH
                corrected += not accepted
                group = lb.r17a_group(d)
                new = top if accepted else (None if e is None else max(0, e + medians[group]))
                changed += last is None or new is None or last != new
            result[key] = {"drives": len(drives), "not_accepted": corrected, "changed_from_committed_rule": changed}
        out[lb.TAG[s]] = result
    return out


# ============================================================================ partition

def regime(c):
    if c["half"] == "Overtime":
        if c["season"] < OT_FROM:
            return "ot_excluded"
        if c["ot_index"] == 0:
            return "ot_first"
        return "ot_sudden" if c["score_diff"] == 0 else "ot_untied"
    if c["t0"] > NEUTRAL_OVER:
        return "neutral"
    return "h1_late" if c["half"] == "Half1" else "late"


def need_of(diff):
    return next(label for label, low, high in NEEDS if low <= diff <= high)


def time_label(seconds):
    return next(label for label, low, high in LATE_TIME if low <= seconds <= high)


def h1_bucket(seconds):
    return next(i for i, (low, high) in enumerate(H1_LATE_EDGES) if seconds <= high)


def collapse_late(counts):
    """The committed late collapse (fp.collapse_late) on the eight needs: a thin cell merges
    into the adjacent later time bucket; a thin le120 bucket into the adjacent earlier one;
    repeated. Need is never merged. Raw counts."""
    cell_map = {}
    labels = [label for label, _, _ in LATE_TIME]
    for need, _, _ in NEEDS:
        groups = [[label] for label in labels]

        def size(group):
            return sum(counts.get((label, need), 0) for label in group)
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
    """The committed first-half bucket collapse (fp.h1_keymap) on the h1_late edges: a bucket
    under MIN_CELL merges into the next larger surviving bucket; a thin largest bucket into
    the nearest smaller surviving one."""
    counts = [0] * len(H1_LATE_EDGES)
    for c in drives:
        counts[h1_bucket(c["t0"])] += 1
    bucket_map = list(range(len(H1_LATE_EDGES)))

    def alive(j):
        return bucket_map[j] == j
    for i in range(len(H1_LATE_EDGES)):
        target = bucket_map[i]
        if counts[target] >= MIN_CELL:
            continue
        larger = [j for j in range(target + 1, len(H1_LATE_EDGES)) if alive(j)]
        smaller = [j for j in range(target - 1, -1, -1) if alive(j)]
        if not larger and not smaller:
            continue
        nxt = larger[0] if larger else smaller[0]
        counts[nxt] += counts[target]
        counts[target] = 0
        for j, mapped in enumerate(bucket_map):
            if mapped == target:
                bucket_map[j] = nxt
    keys = ["%d-%d" % edge for edge in H1_LATE_EDGES]
    return {keys[i]: keys[bucket_map[i]] for i in range(len(H1_LATE_EDGES))}


# ============================================================================ records

class Codes:
    """Penalty-type codes: an index into the artifact's penalty_types list."""

    def __init__(self, names):
        self.names = sorted(names)
        self.index = {n: i for i, n in enumerate(self.names)}

    def __call__(self, name):
        return self.index[name]


def nominal_yards(drives_by_season, pools_by_season):
    """Per penalty type: the most common accepted yardage outside half-distance enforcement."""
    seen = collections.defaultdict(collections.Counter)
    for drives in drives_by_season.values():
        for c in drives:
            for p in c["pen"]:
                if p[4] == "A" and p[3] is not None and not p[8]:
                    seen[p[1]][abs(p[3])] += 1
    for pools in pools_by_season.values():
        for name in ("kickoff_pool", "free_kick_pool", "punt_pool"):
            for record in pools[name]:
                for kind, side, signed, status in record[-5]:
                    if status == "A" and signed is not None:
                        seen[kind][abs(signed)] += 1
    out = {}
    for kind, c in seen.items():
        yards, n = max(sorted(c.items()), key=lambda kv: kv[1])
        # A type with no dominant yardage (a spot foul) has no nominal yards.
        out[kind] = yards if n * 2 > sum(c.values()) else None
    return out


def tuple_of(c, codes, nominal, stage):
    fg = c["fg"] or [None, None, None]
    safety = c["safety_term"] or [None, None]
    row = [
        c["plays"], c["net0"], c["seconds"], c["start"], c["end"], c["t0"], c["score_diff"],
        int(c["final"]), c["term_bucket"], c["term_down"], c["term_ydstogo"], c["chains"],
        c["kneel_yards"], c["spikes"], fg[0], fg[1], fg[2], safety[0], safety[1],
        c["runs"], c["attempts"], c["sacks"], c["td_kind"],
        c["off_timeouts"], c["def_timeouts"], c["off_timeouts_used"], c["def_timeouts_used"],
        c["season"], SECONDS_BASIS.index(c["seconds_basis"]), c["last_spike_to_end"],
    ]
    if stage == "core":
        return row
    pen = [[p[0], codes(p[1]), p[2], p[3], p[4], p[5], p[6], p[7], p[8], nominal.get(p[1])] for p in c["pen"]]
    row += [c["rush_yards"], c["pass_yards"], c["completions"], c["sack_losses"], c["other_yards"],
            c["run_values"], c["completion_values"], c["term_snap"], c["spike_positions"], pen,
            c["fumbles"], c["emph"], c["exposure"], c["placement"]]
    return row


def kick_record(record, codes, stage, width):
    core = record[:width]
    if stage == "core":
        return core
    pen = [[codes(kind), side, signed, status] for kind, side, signed, status in record[width]]
    return core + [pen] + list(record[width + 1:])


# ============================================================================ the build

def pair(k, n):
    return [int(k), int(n)]


def by_season_pairs(seasons, fn):
    """{"pooled": [k, n], "by_season": {tag: [k, n]}, "drift": test} for a share."""
    per = {lb.TAG[s]: fn(s) for s in seasons}
    pooled = [sum(v[0] for v in per.values()), sum(v[1] for v in per.values())]
    return {"pooled": pooled, "by_season": per, "drift": lb.share_drift(list(per.values()))}


def by_season_rate(seasons, fn):
    """A per-unit count rate (events per team-game): [events, units] per season, Poisson drift."""
    per = {lb.TAG[s]: fn(s) for s in seasons}
    pooled = [sum(v[0] for v in per.values()), sum(v[1] for v in per.values())]
    return {"pooled": pooled, "by_season": per, "drift": lb.rate_drift(list(per.values()))}


def by_season_mean(seasons, fn):
    """Integer moments [n, sum, sum of squares] per season, ANOVA drift."""
    per = {lb.TAG[s]: lb.moments(fn(s)) for s in seasons}
    pooled = [sum(v[i] for v in per.values()) for i in range(3)]
    return {"pooled": pooled, "by_season": per, "drift": lb.mean_drift(list(per.values()))}


def build(extracted, seasons, stage="all"):
    """The three artifacts from the extraction. Returns (fp, dm, agg, errors)."""
    errors = []
    primary = {s: extracted[("nflverse", s)] for s in seasons}
    drives_by_season = {s: primary[s]["drives"] for s in seasons}
    corrections_r17a = apply_r17a(drives_by_season)
    for s in seasons:
        for c in drives_by_season[s]:
            c["regime"] = regime(c)
    drives = [c for s in seasons for c in drives_by_season[s]]
    team_games = {s: primary[s]["team_games"] for s in seasons}
    total_team_games = sum(team_games.values())
    games = {s: primary[s]["games"] for s in seasons}
    excluded_ot = [c for c in drives if c["regime"] == "ot_excluded"]
    if seasons == (2010, 2011, 2012, 2013, 2014) and len(excluded_ot) != FILTERS["excluded_2010_2011_overtime_drives"]:
        errors.append("2010-2011 overtime drives %d, specification %d"
                      % (len(excluded_ot), FILTERS["excluded_2010_2011_overtime_drives"]))
    based = [c for c in drives if c["regime"] != "ot_excluded"]

    # -- penalty codes, nominal yards, placement (annotation stage) ---------------------------------
    pools_by_season = {s: primary[s]["pools"] for s in seasons}
    retained_by_season = {s: primary[s]["retained"] for s in seasons}
    kinds = set()
    for c in drives:
        kinds.update(p[1] for p in c["pen"])
    for s in seasons:
        for name in ("kickoff_pool", "free_kick_pool", "punt_pool"):
            for record in pools_by_season[s][name]:
                kinds.update(p[0] for p in record[-5])
        for name, records in retained_by_season[s].items():
            for record in records:
                kinds.update(p[0] for p in record[-5])
    codes = Codes(kinds)
    nominal = nominal_yards(drives_by_season, pools_by_season)

    parts = collections.defaultdict(list)
    for c in based:
        parts[c["regime"]].append(c)

    def T(c):
        return tuple_of(c, codes, nominal, stage)

    # -- neutral pools by start bin ---------------------------------------------------------------
    neutral_counts = [[0] * len(CATEGORIES) for _ in START_BINS]
    neutral_pools = [[[] for _ in CATEGORIES] for _ in START_BINS]
    for c in parts["neutral"]:
        b, k = fp.bin_index(c["start"]), CATEGORIES.index(c["category"])
        neutral_counts[b][k] += 1
        if c["renderable"]:
            neutral_pools[b][k].append(T(c))
    ladder = [[[] for _ in CATEGORIES] for _ in START_BINS]
    for b in range(len(START_BINS)):
        for k in range(len(CATEGORIES)):
            if not neutral_counts[b][k]:
                continue
            chosen, n = [b], len(neutral_pools[b][k])
            for j in sorted((j for j in range(len(START_BINS)) if j != b), key=lambda j: (abs(j - b), j)):
                if n >= MIN_CELL:
                    break
                chosen.append(j)
                n += len(neutral_pools[j][k])
            ladder[b][k] = sorted(chosen)

    # -- h1_late ------------------------------------------------------------------------------------------
    keymap = h1_keymap(parts["h1_late"])
    h1_pools, h1_counts = {}, {}
    for c in parts["h1_late"]:
        key = keymap["%d-%d" % H1_LATE_EDGES[h1_bucket(c["t0"])]]
        h1_counts.setdefault(key, {k: 0 for k in CATEGORIES})[c["category"]] += 1
        if c["renderable"]:
            h1_pools.setdefault(key, {k: [] for k in CATEGORIES})[c["category"]].append(T(c))
    for key in set(keymap.values()):
        h1_pools.setdefault(key, {k: [] for k in CATEGORIES})
    for key, cells in h1_counts.items():
        if sum(cells.values()) < MIN_CELL:
            errors.append("h1_late bucket %s holds %d drives, under MIN_CELL" % (key, sum(cells.values())))

    # -- late cells ---------------------------------------------------------------------------------------
    raw = collections.Counter((time_label(c["t0"]), need_of(c["score_diff"])) for c in parts["late"])
    cell_map = collapse_late(raw)
    late_pools, late_counts = {}, {}
    for c in parts["late"]:
        cell = cell_map["%s|%s" % (time_label(c["t0"]), need_of(c["score_diff"]))]
        late_counts.setdefault(cell, {k: 0 for k in CATEGORIES})[c["category"]] += 1
        if c["renderable"]:
            late_pools.setdefault(cell, {k: [] for k in CATEGORIES})[c["category"]].append(T(c))
    for cell in set(cell_map.values()):
        late_pools.setdefault(cell, {k: [] for k in CATEGORIES})
        late_counts.setdefault(cell, {k: 0 for k in CATEGORIES})
    for cell, cells in late_counts.items():
        if sum(cells.values()) < MIN_CELL:
            errors.append("late cell %s holds %d drives, under MIN_CELL" % (cell, sum(cells.values())))

    # -- overtime ----------------------------------------------------------------------------------------
    ot_counts, ot_pools = {}, {}
    for name in ("ot_first", "ot_sudden", "ot_untied"):
        ot_counts[name] = {k: 0 for k in CATEGORIES}
        ot_pools[name] = {k: [] for k in CATEGORIES}
        for c in parts[name]:
            ot_counts[name][c["category"]] += 1
            if c["renderable"]:
                ot_pools[name][c["category"]].append(T(c))
    for name in ("ot_first", "ot_sudden"):
        if seasons == (2010, 2011, 2012, 2013, 2014) and sum(ot_counts[name].values()) < MIN_CELL:
            errors.append("%s holds %d drives, under MIN_CELL" % (name, sum(ot_counts[name].values())))

    every_pool = [p for row in neutral_pools for p in row]
    for group in list(h1_pools.values()) + list(late_pools.values()) + list(ot_pools.values()):
        every_pool += list(group.values())
    for pool in every_pool:
        pool.sort(key=lambda t: json.dumps(t))

    # -- envelopes ------------------------------------------------------------------------------------------
    envelopes = {k: [None] * len(START_BINS) for k in CATEGORIES}
    for c in based:
        b = fp.bin_index(c["start"])
        cell = envelopes[c["category"]][b]
        envelopes[c["category"]][b] = [c["net0"], c["net0"]] if cell is None else [
            min(cell[0], c["net0"]), max(cell[1], c["net0"])]

    # -- transition pools ------------------------------------------------------------------------------------
    kick_w, punt_w = len(fp.KICK_FIELDS) + 1, len(fp.PUNT_FIELDS) + 1
    kickoff_pool, free_kick_pool, punt_pool, int_pool, fum_pool = [], [], [], [], []
    retained = {"kickoff": [], "free_kick": [], "punt": []}
    for s in seasons:
        pools = pools_by_season[s]
        if s >= KICKOFF_FROM:
            kickoff_pool += [kick_record(r, codes, stage, kick_w) for r in pools["kickoff_pool"]]
            retained["kickoff"] += [kick_record(r, codes, stage, kick_w) for r in retained_by_season[s]["kickoff"]]
        free_kick_pool += [kick_record(r, codes, stage, kick_w) for r in pools["free_kick_pool"]]
        retained["free_kick"] += [kick_record(r, codes, stage, kick_w) for r in retained_by_season[s]["free_kick"]]
        punt_pool += [kick_record(r, codes, stage, punt_w) for r in pools["punt_pool"]]
        retained["punt"] += [kick_record(r, codes, stage, punt_w) for r in retained_by_season[s]["punt"]]
        int_pool += pools["interception_pool"]
        fum_pool += pools["fumble_pool"]
    if stage != "core":
        # Retained records join their kick pools in the kicking frame (possession "kicking",
        # outcome "retained"), so a draw meets them at their real frequency.
        kickoff_pool += retained["kickoff"]
        free_kick_pool += retained["free_kick"]
        punt_pool += retained["punt"]
    for pool in (punt_pool, int_pool, fum_pool, retained["punt"]):
        pool.sort(key=lambda r: r[0])     # stable: same-spot records keep season and file order
    if any(r[6] < KICKOFF_FROM for r in kickoff_pool):
        errors.append("a kickoff record from before 2011 entered the kickoff pool")
    for name, records, frame in (("kickoff", retained["kickoff"], "kickoff"),
                                 ("free_kick", retained["free_kick"], "kickoff"),
                                 ("punt", retained["punt"], "punt")):
        for r in records:
            nxt, e = (r[1], r[4]) if frame == "kickoff" else (r[5], r[4])
            landing = (35 if name == "kickoff" else 20) + r[2] - r[3] if frame == "kickoff" else 100 - r[0] + r[2] - r[3]
            if nxt != 100 - landing + e or not 1 <= nxt <= 99:
                errors.append("retained %s record fails the kicking-frame identity" % name)
                break

    # -- seconds and clock scale -------------------------------------------------------------------------------
    total_seconds = {s: sum(c["seconds"] for c in drives_by_season[s]) for s in seasons}
    clock_scale = [3600 * sum(games.values()), sum(total_seconds.values())]
    clock_scale_by_season = {lb.TAG[s]: [3600 * games[s], total_seconds[s]] for s in seasons}

    # -- constants measured (spike window, early field goal, W5a tables) ----------------------------------
    constants, const_errors = measured_constants(extracted, seasons)
    errors += const_errors

    centres = band_centres(seasons, drives_by_season, primary, team_games, pools_by_season, keymap)

    fp_model = {
        "schema": FP_SCHEMA,
        "seasons": [lb.TAG[s] for s in seasons],
        "season_type": "regular",
        "information_boundary": information_boundary(seasons),
        "provenance": provenance(seasons),
        "builder": "scripts/research/build_2010_2014_league_base.py",
        "specification_sha256": pre_build_specification.digest(),
        "sources": source_header(seasons),
        "stage": stage,
        "categories": list(CATEGORIES),
        "tuple_fields": list(CORE_TUPLE_FIELDS if stage == "core" else TUPLE_FIELDS),
        "core_tuple_fields": list(CORE_TUPLE_FIELDS),
        "chain_fields": list(fp.CHAIN_FIELDS),
        "kick_fields": list(CORE_KICK_FIELDS if stage == "core" else KICK_FIELDS),
        "punt_fields": list(CORE_PUNT_FIELDS if stage == "core" else PUNT_FIELDS),
        "turnover_fields": list(TURNOVER_FIELDS),
        "seconds_basis_codes": list(SECONDS_BASIS),
        "preregistration": preregistration(),
        "cell_map": cell_map,
        "h1_late_keymap": keymap,
        "neutral_counts": neutral_counts,
        "neutral_ladder": ladder,
        "h1_late_counts": dict(sorted(h1_counts.items())),
        "late_counts": dict(sorted(late_counts.items())),
        "ot_first_counts": ot_counts["ot_first"],
        "ot_sudden_counts": ot_counts["ot_sudden"],
        "ot_untied_counts": ot_counts["ot_untied"],
        "pools": {"neutral": neutral_pools, "h1_late": dict(sorted(h1_pools.items())),
                  "late": dict(sorted(late_pools.items())), "ot_first": ot_pools["ot_first"],
                  "ot_sudden": ot_pools["ot_sudden"]},
        "envelopes": envelopes,
        "kickoff_pool": kickoff_pool,
        "free_kick_pool": free_kick_pool,
        "punt_pool": punt_pool,
        "interception_pool": int_pool,
        "fumble_pool": fum_pool,
        "rates": {"scramble": [sum(primary[s]["scramble"][0] for s in seasons),
                               sum(primary[s]["scramble"][1] for s in seasons)],
                  "scramble_by_season": {lb.TAG[s]: primary[s]["scramble"] for s in seasons}},
        "clock_scale": clock_scale,
        "clock_scale_by_season": clock_scale_by_season,
        "constants": constants,
        "band_centres": centres,
        "corrections": corrections_block(seasons, drives_by_season, primary, corrections_r17a),
        "start_kinds": {lb.TAG[s]: primary[s]["start_kinds"] for s in seasons},
        "partition": {
            "rule": "neutral: regulation drives starting with more than 600 s left in the half; h1_late: first half "
                    "at or under 600 s; late: second half at or under 600 s; ot_first: the opening overtime "
                    "possession (2012 onward); ot_sudden: a later overtime possession starting tied; ot_untied: a "
                    "later overtime possession not tied (counted, not pooled: a trailing overtime offense draws "
                    "from the late trail1_3 cell); ot_excluded: the 2010-2011 overtime drives (pure sudden death), "
                    "counted, excluded from every pool and from the overtime and late drive-share centres.",
            "counts": {name: len(parts[name]) for name in
                       ("neutral", "h1_late", "late", "ot_first", "ot_sudden", "ot_untied")},
            "ot_excluded": len(excluded_ot),
            "drives": len(drives),
            "by_season": {lb.TAG[s]: dict(sorted(collections.Counter(c["regime"] for c in drives_by_season[s]).items()))
                          for s in seasons},
        },
        "EXPLAINED": dict(sorted(EXPLAINED.items())),
    }
    if stage != "core":
        fp_model["retained_kick_pools"] = retained
        fp_model["penalty_types"] = codes.names
        fp_model["penalty_nominal_yards"] = {k: nominal[k] for k in sorted(nominal)}
        fp_model["pen_fields"] = list(PEN_FIELDS)
        fp_model["kick_pen_fields"] = list(KICK_PEN_FIELDS)
        fp_model["fumble_fields"] = list(FUMBLE_FIELDS)
        annotations, ann_errors = annotation_blocks(extracted, seasons, drives_by_season, pools_by_season,
                                                    retained_by_season, parts, team_games)
        fp_model.update(annotations)
        errors += ann_errors

    dm_model, dm_errors = build_drive_model(extracted, seasons, drives_by_season, primary, team_games,
                                            clock_scale, clock_scale_by_season, fp_model)
    errors += dm_errors
    agg, agg_errors = build_aggregate(extracted, seasons, drives_by_season, primary, team_games, dm_model)
    errors += agg_errors
    return fp_model, dm_model, agg, errors


def information_boundary(seasons):
    if len(seasons) == 1:
        return "2012 regular-season play-by-play only; no 2013 or later data; no club, game, player or date field."
    return ("NFL regular seasons 2010-2013 and 2014 Weeks 1-4 (games through September 29, 2014; 61 games), cut at "
            "fetch by scripts/research/sources_2010_2014.py; no later row; no club, game, player or date field. "
            "Usable in the branch from September 30, 2014; frozen at the first 2014 Week 5 event for the rest of the "
            "2014 season.")


def provenance(seasons):
    return {
        "seasons": [lb.TAG[s] for s in seasons],
        "cut_2014": RULES["data_window"]["cut_2014"] if 2014 in seasons else None,
        "weighting": RULES["weighting"]["rule"],
        "post_divergence": ("2013 and 2014 Weeks 1-4 are an anonymous post-divergence league population: pooled "
                            "fits only, never a club's or player's own value.") if 2013 in seasons else None,
        "branch_records": "no branch receipt, audit reading or result entered any value",
    }


def source_header(seasons):
    manifest = sources.load_manifest()
    names = []
    for s in seasons:
        names += [lb.pbp_name(s, "nflverse"), lb.pbp_name(s, "nflscrapr"), lb.roster_name(s)]
        if s < 2014:
            names += ["nflcom_offense_passing_%d.csv" % s, "nflcom_offense_rushing_%d.csv" % s]
    out = {}
    for name in names:
        record = manifest["assets"][name]
        out[name] = {"sha256": record["sha256"], "fetched_sha256": record["fetched_sha256"], "url": record["url"],
                     "publisher": record["publisher"]}
    out["manifest"] = {"file": "library/data/2010_2014_sources_manifest.json",
                       "sha256": sources.sha256_file(sources.MANIFEST)}
    return out


def preregistration():
    return {
        "specification": "library/2014_6_pre_build_specification.md",
        "start_bins": [list(b) for b in START_BINS],
        "zones": {label: [low, high] for label, low, high in fp.ZONES},
        "neutral_over_seconds": NEUTRAL_OVER,
        "h1_late_edges": [list(e) for e in H1_LATE_EDGES],
        "late_time_buckets": {label: [low, high] for label, low, high in LATE_TIME},
        "needs": {label: [low, high] for label, low, high in NEEDS},
        "min_cell": MIN_CELL,
        "k_transition": K_TRANSITION,
        "fg_offsets": list(fp.FG_OFFSETS),
        "decision_zones": EOH["DECISION_ZONES"],
        "term_buckets": list(fp.TERM_BUCKETS),
        "late_collapse_rule": "A thin late cell merges into the adjacent later time bucket; a thin le120 bucket merges "
                              "into the adjacent earlier one; repeated. Need is never merged. Raw counts.",
        "h1_late_collapse_rule": "A bucket under MIN_CELL merges into the next larger surviving bucket; a thin largest "
                                 "bucket into the nearest smaller surviving one. Raw counts.",
        "tuple_ladder": "A neutral (bin, category) tuple list under MIN_CELL adds the nearest bins, ties to the lower "
                        "index (the committed rule).",
        "structural_filters": FILTERS,
        "keep_end": ["field_goal_attempt", "punt", "downs", "interception", "fumble_lost"],
        "keep_net": ["clock"],
        "fixed": {"touchdown": "net = start, end = 0", "safety": "net = start - 100, end = 100"},
    }


EXPLAINED = {
    "2010_12_CAR_CLE": "Play 3904 of 2010_12_CAR_CLE splits one drive in the nflverse fixed_drive key; the source "
                       "drive key repairs it (counted, never repaired by hand).",
    "2011_13_DET_NO": "The nflverse rows around play 1335 are out of file order; the punt at 9:01 of the second "
                      "quarter falls inside a later fixed_drive group and ends no drive (counted in the scoring "
                      "artifact's punt unit only; found by the B3c denominator check).",
    "2013_05_SD_OAK": "Two field-goal attempts on one drive (a penalty re-kick); counted in the field-goal rates "
                      "only, the drive carries its last attempt.",
}


# ============================================================================ constants

def measured_constants(extracted, seasons):
    """SPIKE_WINDOW and EARLY_FG_SECONDS reproduced from the data, and the W5a gap and
    kick-length tables (pass 1 nflverse, pass 2 nflscrapR)."""
    errors = []
    out = {}
    pre = [s for s in seasons if s <= 2012]
    spikes = [(clock, c["season"]) for s in seasons for c in extracted[("nflverse", s)]["drives"]
              if c["half"] != "Overtime" for clock in c["spike_clocks"] if clock is not None]
    if spikes:
        pre_max = max((clock for clock, s in spikes if s <= 2012), default=None)
        out["spike_window"] = {"pre_divergence_max_seconds": pre_max, "specification": EOH["SPIKE_WINDOW"],
                               "all_seasons_max_seconds": max(clock for clock, _ in spikes),
                               "count_at_max": sum(1 for clock, s in spikes if s <= 2012 and clock == pre_max),
                               "definition": "the regulation half clock at a spike, 2010-2012"}
        if set(pre) == {2010, 2011, 2012} and pre_max != EOH["SPIKE_WINDOW"]:
            errors.append("spike window: 2010-2012 maximum %s, specification %s" % (pre_max, EOH["SPIKE_WINDOW"]))
    fgs = [(c["fg_snap_clock"], c["season"]) for s in seasons for c in extracted[("nflverse", s)]["drives"]
           if c["fg_snap_clock"] is not None and c["fg_snap_down"] is not None and c["fg_snap_down"] < 4
           and c["half"] != "Overtime"]
    if fgs:
        all_max = max(clock for clock, _ in fgs)
        out["early_field_goal"] = {
            "max_seconds": all_max, "specification": EOH["EARLY_FG_SECONDS"],
            "next_largest": sorted({clock for clock, _ in fgs}, reverse=True)[1:3],
            "definition": "the half clock at the kick snap of a regulation field-goal attempt on first, second or "
                          "third down"}
        if seasons == (2010, 2011, 2012, 2013, 2014) and all_max != EOH["EARLY_FG_SECONDS"]:
            errors.append("early field goal: maximum %s, specification %s" % (all_max, EOH["EARLY_FG_SECONDS"]))
    tables = {}
    for source in lb.SOURCES:
        tables[source] = w5a_tables(extracted, seasons, source)
    out["w5a"] = tables["nflverse"]
    comparison, cmp_errors = compare_w5a(tables["nflverse"], tables["nflscrapr"])
    out["w5a_second_pass"] = comparison
    errors += cmp_errors
    return out, errors


def clock_context(qtr, quarter_clock, half_clock):
    if half_clock is not None and half_clock <= 120 and (qtr in (2, 4) or (qtr or 0) >= 5):
        return "inside_2_min"
    if qtr == 4 and quarter_clock is not None and 120 < quarter_clock <= 300:
        return "q4_2_to_5_min"
    return "normal"


def w5a_tables(extracted, seasons, source):
    """Gap table: seconds between consecutive snaps of a drive by the previous snap's kind and
    clock context; the sack gap split 2010-2013 / 2014 Weeks 1-4. Kick-length table: seconds
    from the last scrimmage snap to the kick snap, by kick and the last snap's kind.
    Timeout seats: counts of the snap kind before each timeout row."""
    gaps = collections.defaultdict(lambda: [0, 0])
    kicks = collections.defaultdict(lambda: [0, 0])
    seats = collections.Counter()
    for s in seasons:
        for c in extracted[(source, s)]["drives"]:
            seq = c["clock_sequence"]
            for prev, cur in zip(seq, seq[1:]):
                if prev[1] is None or cur[1] is None:
                    continue
                gap = int(round(prev[1] - cur[1]))
                if gap < 0:
                    continue
                if cur[0] == "timeout":
                    seats[prev[0]] += 1
                    continue
                if prev[0] == "timeout":
                    continue
                if cur[0] in ("punt", "field_goal"):
                    cell = kicks["%s|%s" % (cur[0], prev[0])]
                    cell[0] += gap
                    cell[1] += 1
                    continue
                context = clock_context(prev[2], prev[3], prev[1])
                kind = prev[0]
                if kind == "sack":
                    kind = "sack_2014w4" if s == 2014 else "sack_2010_2013"
                cell = gaps["%s|%s" % (kind, context)]
                cell[0] += gap
                cell[1] += 1
    return {"gap_seconds": {k: v for k, v in sorted(gaps.items())},
            "kick_length_seconds": {k: v for k, v in sorted(kicks.items())},
            "timeout_seats": dict(sorted(seats.items())),
            "fields": "[sum of seconds, snaps] per cell; the mean is sum / snaps",
            "kinds": EOH["W5A_GAP_KINDS"], "contexts": EOH["W5A_CLOCK_CONTEXTS"], "kicks": EOH["W5A_KICKS"]}


def compare_w5a(a, b):
    rows, errors = [], []
    for table in ("gap_seconds", "kick_length_seconds"):
        for key in sorted(set(a[table]) | set(b[table])):
            x, y = a[table].get(key, [0, 0]), b[table].get(key, [0, 0])
            if x[1] < 30 or y[1] < 30:
                status = "informational (under 30 snaps)"
            else:
                diff = abs(x[0] / x[1] - y[0] / y[1])
                status = "within 1 s" if diff <= 1.0 else "UNEXPLAINED"
                if status == "UNEXPLAINED":
                    errors.append("W5a %s %s: nflverse %.2f, nflscrapR %.2f" % (table, key, x[0] / x[1], y[0] / y[1]))
            rows.append({"table": table, "cell": key, "nflverse": x, "nflscrapr": y, "status": status})
    return {"rule": "cell means within 1 s for cells of at least 30 snaps in both passes", "comparison": rows,
            "result": "pass" if not errors else "fail"}, errors


# ============================================================================ band centres

def band_centres(seasons, drives_by_season, primary, team_games, pools_by_season, keymap):
    """Unweighted centres with per-season integer counts (specification section 5)."""
    tg = lambda s: team_games[s]  # noqa: E731

    def base(s):
        """Every real drive (team-game, overall-share and play centres)."""
        return drives_by_season[s]

    def base_ex(s):
        """Without the 2010-2011 overtime drives (overtime and late centres)."""
        return [c for c in drives_by_season[s] if c["regime"] != "ot_excluded"]

    out = {"team_games": {lb.TAG[s]: team_games[s] for s in seasons}}
    for category in CATEGORIES:
        out["drive_share:" + category] = by_season_pairs(
            seasons, lambda s, k=category: pair(sum(c["category"] == k for c in base(s)), len(base(s))))
    out["drives_per_team_game"] = by_season_rate(seasons, lambda s: pair(len(base(s)), tg(s)))
    out["fga_per_team_game"] = by_season_rate(
        seasons, lambda s: pair(primary[s]["play"]["counts"].get("fg_attempts", 0), tg(s)))
    out["fgm_per_team_game"] = by_season_rate(
        seasons, lambda s: pair(primary[s]["play"]["counts"].get("fg_made", 0), tg(s)))
    out["drive_ending_punts_per_team_game"] = by_season_rate(
        seasons, lambda s: pair(sum(c["category"] == "punt" for c in base(s)), tg(s)))
    out["clock_expired_drives_per_team_game"] = by_season_rate(
        seasons, lambda s: pair(sum(c["category"] == "clock" for c in base(s)), tg(s)))
    out["offensive_drive_turnovers_per_team_game"] = by_season_rate(
        seasons, lambda s: pair(sum(c["category"] in ("interception", "fumble_lost") for c in base(s)), tg(s)))
    out["interception_share_of_turnovers"] = by_season_pairs(
        seasons, lambda s: pair(sum(c["category"] == "interception" for c in base(s)),
                                sum(c["category"] in ("interception", "fumble_lost") for c in base(s))))
    for label, low, high in FG_BINS:
        out["fg_accuracy:" + label] = by_season_pairs(
            seasons, lambda s, lo=low, hi=high: pair(
                sum(m for d, m in primary[s]["play"]["fg_rows"] if lo <= d <= hi),
                sum(1 for d, _ in primary[s]["play"]["fg_rows"] if lo <= d <= hi)))
    out["fg_accuracy"] = by_season_pairs(
        seasons, lambda s: pair(primary[s]["play"]["counts"].get("fg_made", 0),
                                primary[s]["play"]["counts"].get("fg_attempts", 0)))
    kick_seasons = tuple(s for s in seasons if s >= KICKOFF_FROM)
    out["kickoff_touchback_share"] = by_season_pairs(
        kick_seasons, lambda s: pair(sum(r[0] for r in pools_by_season[s]["kickoff_pool"]),
                                     len(pools_by_season[s]["kickoff_pool"])))
    out["kickoff_nontouchback_start"] = by_season_mean(
        kick_seasons, lambda s: [r[1] for r in pools_by_season[s]["kickoff_pool"] if not r[0]])
    for label, low, high in fp.PUNT_NET_BINS:
        out["punt_net:" + label] = by_season_mean(
            seasons, lambda s, lo=low, hi=high: [r[0] - (100 - r[5]) for r in pools_by_season[s]["punt_pool"]
                                                 if lo <= r[0] <= hi])
    out["kick_return_yards"] = by_season_mean(
        kick_seasons, lambda s: [r[3] for r in pools_by_season[s]["kickoff_pool"] if r[5] == "returned"])
    out["punt_return_yards"] = by_season_mean(
        seasons, lambda s: [r[3] for r in pools_by_season[s]["punt_pool"] if r[1] == "returned"])
    out["sacks_per_dropback"] = by_season_pairs(
        seasons, lambda s: pair(sum(c["sacks"] for c in base(s)),
                                sum(c["sacks"] + c["attempts"] + c["spikes"] for c in base(s))))
    # First half (the h1_late regime and the half-final drives).
    h1_finals = lambda s: [c for c in base(s) if c["half"] == "Half1" and c["final"]]  # noqa: E731
    out["h1_final_fg_share"] = by_season_pairs(
        seasons, lambda s: pair(sum(c["category"] == "field_goal_attempt" for c in h1_finals(s)), len(h1_finals(s))))
    out["h1_final_clock_share"] = by_season_pairs(
        seasons, lambda s: pair(sum(c["category"] == "clock" for c in h1_finals(s)), len(h1_finals(s))))
    for low, high in ((61, 120), (121, 240)):
        out["h1_p_final:%d-%d" % (low, high)] = by_season_pairs(
            seasons, lambda s, lo=low, hi=high: pair(
                sum(c["final"] for c in base(s) if c["half"] == "Half1" and lo <= c["t0"] <= hi),
                sum(1 for c in base(s) if c["half"] == "Half1" and lo <= c["t0"] <= hi)))
    for low, high in H1_LATE_EDGES + ((601, 1800),):
        out["h1_final_start_window:%d-%d" % (low, high)] = by_season_pairs(
            seasons, lambda s, lo=low, hi=high: pair(sum(lo <= c["t0"] <= hi for c in h1_finals(s)),
                                                     len(h1_finals(s))))
    out["h1_clock_expired_inside_30"] = by_season_pairs(
        seasons, lambda s: pair(sum(c["category"] == "clock" and c["end"] <= 30 for c in h1_finals(s)),
                                sum(c["category"] == "clock" for c in h1_finals(s))))
    # Late game.
    for low, high, tag in ((-999, -12, "trail12p"), (-11, -9, "trail9_11")):
        out["q4_inside_2_min_fga_per_team_game:" + tag] = by_season_rate(
            seasons, lambda s, lo=low, hi=high: pair(sum(
                1 for c in base(s) if c["fg_snap_clock"] is not None and c["term_qtr"] == 4
                and c["fg_snap_clock"] <= 120 and c["term_sd"] is not None and lo <= c["term_sd"] <= hi), tg(s)))
    out["def_timeouts_per_h2_possession_over_600"] = by_season_rate(
        seasons, lambda s: pair(sum(c["def_timeouts_used"] for c in base(s) if c["half"] == "Half2" and c["t0"] > 600),
                                sum(1 for c in base(s) if c["half"] == "Half2" and c["t0"] > 600)))
    out["timeouts_per_team_game"] = by_season_rate(
        seasons, lambda s: pair(sum(c["off_timeouts_used"] + c["def_timeouts_used"] for c in base(s)), tg(s)))
    out["late_punt_share_last5_trail1_8"] = by_season_pairs(
        seasons, lambda s: pair(sum(c["category"] == "punt" for c in base_ex(s) if _late_trailing(c, 300)),
                                sum(1 for c in base_ex(s) if _late_trailing(c, 300))))
    out["late_punt_share_le120_trail1_8"] = by_season_pairs(
        seasons, lambda s: pair(sum(c["category"] == "punt" for c in base_ex(s) if _late_trailing(c, 120)),
                                sum(1 for c in base_ex(s) if _late_trailing(c, 120))))
    ot = lambda s: [c for c in base_ex(s) if c["half"] == "Overtime"]  # noqa: E731
    ot_seasons = tuple(s for s in seasons if s >= OT_FROM)
    out["ot_spikes_over_spike_window"] = by_season_rate(
        ot_seasons, lambda s: pair(sum(1 for c in ot(s) for clock in c["spike_clocks"]
                                       if clock is not None and clock > EOH["SPIKE_WINDOW"]), len(ot(s))))
    out["ot_trailing_punts"] = by_season_pairs(
        ot_seasons, lambda s: pair(sum(c["category"] == "punt" for c in ot(s) if c["score_diff"] < 0),
                                   sum(1 for c in ot(s) if c["score_diff"] < 0)))
    out["extra_point"] = by_season_pairs(
        seasons, lambda s: pair(primary[s]["play"]["counts"].get("xp_made", 0),
                                primary[s]["play"]["counts"].get("xp_attempts", 0)))
    out["third_down_attempts_per_punt_drive"] = by_season_mean(
        seasons, lambda s: [c["chains"][2] for c in base(s) if c["category"] == "punt"])
    out["points_per_drive_by_start_bin"] = {
        "%d-%d" % (low, high): by_season_rate(
            seasons, lambda s, lo=low, hi=high: pair(sum(c["points"] for c in base(s) if lo <= c["start"] <= hi),
                                                     sum(1 for c in base(s) if lo <= c["start"] <= hi)))
        for low, high in fp.POINTS_BINS}
    out["start_bin_counts"] = {lb.TAG[s]: [sum(1 for c in base(s) if low <= c["start"] <= high)
                                           for low, high in START_BINS] for s in seasons}
    out["start_all"] = by_season_mean(seasons, lambda s: [c["start"] for c in base(s)])
    out["scramble_share_of_qb_rushes"] = by_season_pairs(seasons, lambda s: pair(*primary[s]["scramble"]))
    out["fourth_down_per_team_game"] = by_season_rate(seasons, lambda s: pair(sum(c["chains"][4] for c in base(s)), tg(s)))
    out["fourth_down_conversion"] = by_season_pairs(
        seasons, lambda s: pair(sum(c["chains"][5] for c in base(s)), sum(c["chains"][4] for c in base(s))))
    out["kneels_per_team_game"] = by_season_rate(seasons, lambda s: pair(sum(len(c["kneel_yards"]) for c in base(s)), tg(s)))
    out["rule"] = ("Unweighted centres: [events, denominator] or [n, sum, sum of squares] per season and pooled; "
                   "drift is the per-season homogeneity test (chi-square, Poisson chi-square or ANOVA F). The "
                   "2010-2011 overtime drives are excluded from every drive centre; kickoff centres start in 2011.")
    return out


def _late_trailing(c, seconds):
    qtr = c["term_qtr"] or 0
    late = qtr >= 5 or (qtr == 4 and c["term_qsr"] is not None and c["term_qsr"] <= seconds)
    return late and c["score_diff"] is not None and -8 <= c["score_diff"] <= -1


def corrections_block(seasons, drives_by_season, primary, r17a):
    drives = [c for s in seasons for c in drives_by_season[s]]
    return {
        "r17a_seconds": r17a,
        "start_fp_corrected_drives": {lb.TAG[s]: sum(1 for c in drives_by_season[s] if c["corrected_start"])
                                      for s in seasons},
        "fg_offset": {lb.TAG[s]: [c["fg_offset_corrected"] for c in drives_by_season[s] if c["fg_offset_corrected"]]
                      for s in seasons},
        "fg_offset_rule": "A field-goal attempt whose kick distance minus line of scrimmage is outside {17, 18, 19} "
                          "keeps its real distance; its end is set to distance - 18 (committed rule).",
        "non_renderable": {
            "safety": sum(1 for c in drives if c["category"] == "safety" and not c["renderable"]
                          and c["regime"] != "ot_excluded"),
            "touchdown": sum(1 for c in drives if c["category"] == "touchdown" and not c["renderable"]
                             and c["regime"] != "ot_excluded"),
            "zero_play_terminal": sum(1 for c in drives if c["category"] in ("touchdown", "interception",
                                                                             "fumble_lost", "downs")
                                      and c["plays"] == 0 and c["regime"] != "ot_excluded"),
            "rule": "Penalty safeties, aborted-snap fumbles out of the end zone, touchdowns not scored from "
                    "scrimmage and zero-play terminal drives count in the category mix but are never drawn as a "
                    "render tuple (committed rule).",
        },
        "turnover_touchbacks": {lb.TAG[s]: primary[s]["turnover_touchbacks"] for s in seasons},
        "imputed_tries": {lb.TAG[s]: primary[s]["imputed_tries"] for s in seasons},
        "extraction_corrections": {lb.TAG[s]: primary[s]["corrections"] for s in seasons},
    }


# ============================================================================ annotations

def annotation_blocks(extracted, seasons, drives_by_season, pools_by_season, retained_by_season, parts, team_games):
    errors = []
    drives = [c for s in seasons for c in drives_by_season[s] if c["regime"] != "ot_excluded"]
    # Automatic first downs, per defensive type: accepted no-play fouls short of the line to gain.
    auto = collections.defaultdict(lambda: [0, 0])
    for c in drives:
        for p in c["pen"]:
            if p[4] == "A" and p[2] == "D":
                cell = auto[p[1]]
                cell[1] += 1
                cell[0] += p[6]
    emphasis = {}
    for i, (side, kind) in enumerate(lb.EMPHASIS):
        exposure = lb.EMPHASIS_EXPOSURE[i]
        idx = 0 if exposure == "dropbacks" else 1
        emphasis["%s|%s" % (side, kind)] = {
            "exposure": exposure,
            "by_season": {lb.TAG[s]: [sum(c["emph"][i] for c in drives_by_season[s] if c["regime"] != "ot_excluded"),
                                      sum(c["exposure"][idx] for c in drives_by_season[s] if c["regime"] != "ot_excluded")]
                          for s in seasons}}
    feasibility = relocation_feasibility(parts)
    fumble_summary = collections.Counter()
    for c in drives:
        for f in c["fumbles"]:
            fumble_summary["%s|%s" % (f[1], f[3])] += 1
    lost_kind = collections.Counter()
    for c in drives:
        if c["category"] == "fumble_lost":
            lost = [f for f in c["fumbles"] if f[3] == "lost"]
            lost_kind[lost[-1][1] if lost else "no_lost_fumble_record"] += 1
    second, pass_errors = annotation_second_pass(extracted, seasons)
    errors += pass_errors
    unparsed = {lb.TAG[s]: sum(c["pen_unparsed"] for c in drives_by_season[s]) for s in seasons}
    return {
        "auto_first_down": {k: auto[k] for k in sorted(auto)},
        "emphasis_counts": emphasis,
        "relocation_feasibility": feasibility,
        "fumble_summary": dict(sorted(fumble_summary.items())),
        "fumble_lost_terminal_kind": dict(sorted(lost_kind.items())),
        "kick_mappings": {lb.TAG[s]: extracted[("nflverse", s)]["kick_mappings"] for s in seasons},
        "penalty_unparsed_clauses": unparsed,
        "annotation_rules": ANNOTATION_RULES,
        "annotation_second_pass": second,
    }, errors


ANNOTATION_RULES = {
    "yardage": "rush_yards, pass_yards (completions only), completions, sack_losses (snap order), run_values and "
               "completion_values (snap order, the terminal value included), term_snap [kind, yards] of the "
               "terminal scrimmage snap, spike_positions (scrimmage-snap indices), other_yards = net0 minus "
               "rushing, passing, sack and kneel yards (penalty and other yardage).",
    "pen": "Penalty clauses on the drive's own rows (scrimmage snaps, no-play rows, the punt or field-goal row; "
           "kick and try rows excluded), parsed from the counted description (text after the last REVERSED.). "
           "order = the hosting row's index among those rows; side O/D relative to the drive's offense; signed "
           "accepted yards positive for the offense; status A accepted, D declined, X offsetting; enforce N on a "
           "no-play row, S after a counted scrimmage snap, K on the drive's kick snap; first_down = an accepted "
           "defensive foul on a row flagged first_down_penalty; host = the row's kind; half_distance from the "
           "description; nominal_yards = the type's most common accepted yardage outside half-distance when it "
           "holds more than half of them, otherwise null (a spot foul).",
    "emph": "Accepted fouls of the five 2014 emphasis type-sides on the drive's rows: " + ", ".join(
        "%s %s" % pair_ for pair_ in lb.EMPHASIS) + ".",
    "exposure": "[dropbacks including no-play dropbacks, snaps (scrimmage and no-play rows)].",
    "fumbles": "Fumbles (fumble = 1; a nullified play carries 0) on the drive's rows: kind run, reception, sack, "
               "aborted or kick (the drive's own punt or field-goal snap); outcome kept, oob or lost; forced; forcer and recoverer position groups from that "
               "season's roster; whether the recoverer is the forcer or the fumbler. The single source of the "
               "lost-fumble terminal kind.",
    "placement": "The legal start range [lo, hi]: shifting the drive by the change of start keeps every pre-snap "
                 "spot of its rows inside 1-99 (lo = start + 1 - the smallest spot, hi = start + 99 - the largest).",
    "kick_records": "pen (clauses on the kick row, signed positive when they help the receiving club), spot_adjust "
                    "= enforcement minus the accepted penalty yards' effect on it (minus their sum in the receiving "
                    "frame, plus it in the kicking frame); enforcement stays the total, so the committed identities "
                    "hold; fumble [muff or fumble, outcome, muffer role], possession receiving or kicking, "
                    "muffer_role returner (the play's returner muffed) or other.",
    "retained": "Kicking-club recoveries (excluding touchdowns and onside kicks; kickoffs from 2011) join their kick "
                "pools in the kicking frame (outcome retained, possession kicking): next start = 100 - (spot + kick - "
                "return) + enforcement, asserted per record; retained_kick_pools lists them apart as well.",
}


def relocation_feasibility(parts):
    out = {}
    for name in ("neutral", "h1_late", "late", "ot_first", "ot_sudden"):
        records = [c for c in parts[name] if c["renderable"]]
        over = sum(1 for c in records if sum(p[3] for p in c["pen"] if p[4] == "A" and p[2] == "D"
                                             and p[3] is not None and p[3] > 0) > c["start"] - 1)
        outside = sum(1 for c in records if not c["placement"][0] <= c["start"] <= c["placement"][1])
        out[name] = {"tuples": len(records), "defensive_penalty_yards_over_start_minus_1": over,
                     "start_outside_placement": outside}
    return out


def annotation_second_pass(extracted, seasons):
    """nflscrapR accepted penalty counts and yards per season within 1% (pass 2)."""
    rows, errors = [], []
    for s in seasons:
        a = extracted[("nflverse", s)]["play"]
        b = extracted[("nflscrapr", s)]["play"]
        for key in ("penalties_accepted", "penalty_yards_accepted"):
            x, y = a[key], b[key]
            rel = abs(x - y) / x if x else 0.0
            status = "match" if x == y else ("within 1%" if rel <= COUNT_TOLERANCE else "UNEXPLAINED")
            if status == "UNEXPLAINED":
                errors.append("annotation second pass %s %s: nflverse %s, nflscrapR %s" % (lb.TAG[s], key, x, y))
            rows.append({"season": lb.TAG[s], "metric": key, "nflverse": x, "nflscrapr": y, "status": status})
        for key, fn in (("scrimmage_fumbles", lambda ex: sum(len(c["fumbles"]) for c in ex["drives"])),
                        ("lost_fumbles", lambda ex: sum(f[3] == "lost" for c in ex["drives"] for f in c["fumbles"]))):
            x, y = fn(extracted[("nflverse", s)]), fn(extracted[("nflscrapr", s)])
            rel = abs(x - y) / x if x else 0.0
            explained = ANNOTATION_EXPLAINED.get((lb.TAG[s], key))
            status = "match" if x == y else ("within 1%" if rel <= COUNT_TOLERANCE else
                                             ("explained" if explained else "UNEXPLAINED"))
            if status == "UNEXPLAINED":
                errors.append("annotation second pass %s %s: nflverse %s, nflscrapR %s" % (lb.TAG[s], key, x, y))
            row = {"season": lb.TAG[s], "metric": key, "nflverse": x, "nflscrapr": y, "status": status}
            if explained and status == "explained":
                row["explanation"] = explained
            rows.append(row)
        rows.append({"season": lb.TAG[s], "metric": "rows_with_two_accepted_clauses",
                     "nflverse": a["rows_with_two_accepted"], "nflscrapr": b["rows_with_two_accepted"],
                     "status": "listed"})
    # The automatic-first-down table, both passes: per defensive type with at least 30 accepted
    # drive clauses in both, the first-down shares within two percentage points.
    tables = {}
    for source in lb.SOURCES:
        auto = collections.defaultdict(lambda: [0, 0])
        for s in seasons:
            for c in extracted[(source, s)]["drives"]:
                for p in c["pen"]:
                    if p[4] == "A" and p[2] == "D":
                        auto[p[1]][1] += 1
                        auto[p[1]][0] += p[6]
        tables[source] = auto
    auto_rows = []
    family_of = {kind: family for family, kinds in AUTO_FAMILIES.items() for kind in kinds}
    for kind in sorted(set(tables["nflverse"]) | set(tables["nflscrapr"])):
        x, y = tables["nflverse"].get(kind, [0, 0]), tables["nflscrapr"].get(kind, [0, 0])
        row = {"type": kind, "nflverse": list(x), "nflscrapr": list(y)}
        if x[1] < 30 or y[1] < 30:
            row["status"] = "informational (under 30)"
        elif share_close(x, y):
            row["status"] = "within tolerance"
        elif kind in family_of:
            row["status"] = "explained"
            row["explanation"] = "label revision: compared as the %s family" % family_of[kind]
        else:
            row["status"] = "UNEXPLAINED"
            errors.append("auto first down %s: nflverse %s, nflscrapR %s" % (kind, x, y))
        auto_rows.append(row)
    for family, kinds in sorted(AUTO_FAMILIES.items()):
        x = [sum(tables["nflverse"].get(k, [0, 0])[i] for k in kinds) for i in (0, 1)]
        y = [sum(tables["nflscrapr"].get(k, [0, 0])[i] for k in kinds) for i in (0, 1)]
        ok = x[1] >= 30 and y[1] >= 30 and share_close(x, y) \
            and abs(x[1] - y[1]) <= max(0.05 * x[1], 2 * math.sqrt(max(x[1], y[1])))
        if not ok:
            errors.append("auto first down family %s: nflverse %s, nflscrapR %s" % (family, x, y))
        auto_rows.append({"family": family, "types": list(kinds), "nflverse": x, "nflscrapr": y,
                          "status": "within tolerance" if ok else "UNEXPLAINED"})
    return {"rule": "accepted clause counts and yards per season within 1%; fumble counts within 1% unless "
                    "explained; multi-clause rows listed (counts); automatic-first-down shares within the larger of 2 "
                    "percentage points and 2 standard errors of the difference for types with 30 or more accepted "
                    "drive clauses in both passes; a type the description revisions relabel is compared as its "
                    "family (family totals within the larger of 5% and 2 Poisson standard errors, shares as above)",
            "comparison": rows, "auto_first_down": auto_rows,
            "result": "pass" if not errors else "fail"}, errors


def share_close(x, y):
    """Two shares agree within two percentage points or two standard errors of their difference."""
    p1, p2 = x[0] / x[1], y[0] / y[1]
    pooled = (x[0] + y[0]) / (x[1] + y[1])
    se = math.sqrt(max(pooled * (1 - pooled), 1e-12) * (1 / x[1] + 1 / y[1]))
    return abs(p1 - p2) <= max(0.02, 2 * se)


# The description revisions behind the two files relabel some fouls between these names
# (counted on the 2010-2014 Weeks 1-4 drive clauses: the family totals agree, the names do not).
AUTO_FAMILIES = {
    "personal foul": ("Personal Foul", "Unnecessary Roughness", "Unsportsmanlike Conduct", "Taunting"),
    "twelve men": ("Defensive 12 On-field", "Illegal Substitution"),
}

ANNOTATION_EXPLAINED = {
    ("2011", "scrimmage_fumbles"): "nflscrapR leaves its fumble flag unset on seven 2011 fumbles (614 against 607): six "
                                   "the offense kept or that went out of bounds and one lost (288 against 287).",
    ("2014w4", "scrimmage_fumbles"): "nflscrapR leaves its fumble flag unset on eight 2014 Weeks 1-4 fumbles the "
                                     "offense kept (133 against 125); the lost fumbles agree (64).",
}


# ============================================================================ drive model

def fg_logistic(rows):
    """Newton fit of logit P(made) = a + b x distance; returns (a, b, se_b)."""
    a, b = 4.0, -0.08
    for _ in range(100):
        g0 = g1 = h00 = h01 = h11 = 0.0
        for d, made in rows:
            p = 1 / (1 + math.exp(-(a + b * d)))
            g0 += made - p
            g1 += (made - p) * d
            w = p * (1 - p)
            h00 += w
            h01 += w * d
            h11 += w * d * d
        det = h00 * h11 - h01 * h01
        step_a = (h11 * g0 - h01 * g1) / det
        step_b = (h00 * g1 - h01 * g0) / det
        a, b = a + step_a, b + step_b
        if abs(step_a) < 1e-12 and abs(step_b) < 1e-14:
            break
    w_sum = [0.0, 0.0, 0.0]
    for d, _ in rows:
        p = 1 / (1 + math.exp(-(a + b * d)))
        w = p * (1 - p)
        w_sum[0] += w
        w_sum[1] += w * d
        w_sum[2] += w * d * d
    det = w_sum[0] * w_sum[2] - w_sum[1] ** 2
    return a, b, math.sqrt(w_sum[0] / det)


def anchor(b, rate, distances):
    lo, hi = -20.0, 20.0
    for _ in range(200):
        mid = (lo + hi) / 2
        mean_p = sum(1 / (1 + math.exp(-(mid + b * d))) for d in distances) / len(distances)
        if mean_p < rate:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def build_drive_model(extracted, seasons, drives_by_season, primary, team_games, clock_scale,
                      clock_scale_by_season, fp_model):
    errors = []
    counts = lambda s: primary[s]["play"]["counts"]  # noqa: E731
    base = lambda s: drives_by_season[s]  # noqa: E731  (every real drive)
    fg_by_distance = {}
    fg_by_distance_season = {}
    for label, low, high in FG_BINS:
        per = {lb.TAG[s]: pair(sum(m for d, m in primary[s]["play"]["fg_rows"] if low <= d <= high),
                               sum(1 for d, _ in primary[s]["play"]["fg_rows"] if low <= d <= high))
               for s in seasons}
        fg_by_distance_season[label] = {"by_season": per, "drift": lb.share_drift(list(per.values()))}
        fg_by_distance[label] = [sum(v[0] for v in per.values()), sum(v[1] for v in per.values())]

    def pooled(fn):
        per = {lb.TAG[s]: fn(s) for s in seasons}
        return [sum(v[0] for v in per.values()), sum(v[1] for v in per.values())], per

    field_goal, fg_season = pooled(lambda s: pair(counts(s).get("fg_made", 0), counts(s).get("fg_attempts", 0)))
    extra_point, xp_season = pooled(lambda s: pair(counts(s).get("xp_made", 0), counts(s).get("xp_attempts", 0)))
    two_a, two_a_season = pooled(lambda s: pair(*primary[s]["play"]["two_point"]["drive_model"]))
    two_b, two_b_season = pooled(lambda s: pair(*primary[s]["play"]["two_point"]["scrimmage"]))
    td_pass, td_season = pooled(lambda s: pair(counts(s).get("pass_td", 0),
                                                counts(s).get("pass_td", 0) + counts(s).get("rush_td", 0)))
    turnover, to_season = pooled(lambda s: pair(sum(c["category"] == "interception" for c in base(s)),
                                                sum(c["category"] in ("interception", "fumble_lost") for c in base(s))))
    safeties = sum(counts(s).get("safeties", 0) for s in seasons)
    # FG logistic, both passes, events weighting.
    rows_a = [r for s in seasons for r in primary[s]["play"]["fg_rows"]]
    rows_b = [r for s in seasons for r in extracted[("nflscrapr", s)]["play"]["fg_rows"]]
    a1, b1, se1 = fg_logistic(rows_a)
    a2, b2, se2 = fg_logistic(rows_b)
    tuple_distances = _pool_fg_distances(fp_model)
    bands = {}
    for label, low, high in FG_BINS:
        made, att = fg_by_distance[label]
        dist = [d for d in tuple_distances if low <= d <= high]
        if not dist or not att:
            errors.append("field-goal band %s has no tuple distances or attempts" % label)
            continue
        bands[label] = {"low": low, "high": high, "intercept": anchor(b1, made / att, dist), "rate": made / att,
                        "made": made, "attempts": att, "pool_tuple_distances": len(dist)}
    if abs(b1 - b2) > 2 * se1:
        errors.append("FG logistic slope: pass 1 %.5f, pass 2 %.5f differ by more than 2 SE" % (b1, b2))
    rates = {
        "fg_by_distance": fg_by_distance,
        "fg_bin_edges": [[label, low, high] for label, low, high in FG_BINS],
        "field_goal": field_goal,
        "extra_point": extra_point,
        "two_point": two_a,
        "td_type_pass": td_pass,
        "turnover_type_interception": turnover,
        "safeties": safeties,
    }
    rates_by_season = {
        "fg_by_distance": fg_by_distance_season,
        "field_goal": {"by_season": fg_season, "drift": lb.share_drift(list(fg_season.values()))},
        "extra_point": {"by_season": xp_season, "drift": lb.share_drift(list(xp_season.values()))},
        "two_point": {"by_season": two_a_season, "drift": lb.share_drift(list(two_a_season.values()))},
        "td_type_pass": {"by_season": td_season, "drift": lb.share_drift(list(td_season.values()))},
        "turnover_type_interception": {"by_season": to_season, "drift": lb.share_drift(list(to_season.values()))},
        "safeties": {lb.TAG[s]: counts(s).get("safeties", 0) for s in seasons},
    }
    category_counts = {k: sum(c["category"] == k for s in seasons for c in base(s)) for k in CATEGORIES}
    model = {
        "schema": DM_SCHEMA,
        "seasons": [lb.TAG[s] for s in seasons],
        "season_type": "regular",
        "information_boundary": information_boundary(seasons),
        "provenance": provenance(seasons),
        "builder": "scripts/research/build_2010_2014_league_base.py",
        "specification_sha256": pre_build_specification.digest(),
        "sources": source_header(seasons),
        "categories": list(CATEGORIES),
        "category_counts": category_counts,
        "category_counts_by_season": {lb.TAG[s]: {k: sum(c["category"] == k for c in base(s)) for k in CATEGORIES}
                                      for s in seasons},
        "rates": rates,
        "rates_by_season": rates_by_season,
        "two_point_definitions": {
            "drive_model": {"pooled": two_a, "by_season": two_a_season,
                            "definition": "every row with a two-point conversion result (the committed definition)"},
            "scrimmage_not_nullified": {
                "pooled": two_b, "by_season": two_b_season,
                "definition": "two-point attempts from scrimmage: a two-point result row whose description does "
                              "not say No Play (amendment A2) and is not from kick formation (a fake or an aborted "
                              "kick is a kick decision, specification section 4); defensive returns excluded"},
            "reconciliation": "The definitions differ by the kick-formation tries (fakes and aborted kicks) the "
                              "scrimmage definition drops; 2012 reads 29/56 against 28/52 (four kick-formation tries, "
                              "one converted). The scoring artifact (B3c) asserts its try records against the "
                              "scrimmage definition."},
        "field_goal_distance": {
            "rule": "One logistic slope per yard of kick distance on every regular-season field-goal attempt of the "
                    "base, equal weight per event; per drive-model band a separate intercept solved by bisection so "
                    "that the mean fitted probability over the base pool's own field-goal tuple distances in that "
                    "band equals the band's pooled make rate.",
            "attempts": len(rows_a), "made": sum(m for _, m in rows_a),
            "pooled_intercept": a1, "slope_per_yard": b1, "slope_se": se1,
            "second_pass": {"source": "nflscrapR", "attempts": len(rows_b), "slope_per_yard": b2, "slope_se": se2,
                            "pooled_intercept": a2},
            "bands": bands,
        },
        "clock_scale": clock_scale,
        "clock_scale_by_season": clock_scale_by_season,
        "team_games": {lb.TAG[s]: team_games[s] for s in seasons},
        "games": {lb.TAG[s]: primary[s]["games"] for s in seasons},
        "punt_terminal_by_category": {lb.TAG[s]: dict(sorted(collections.Counter(
            c["category"] for c in base(s) if c["term_play_type"] == "punt").items())) for s in seasons},
        "dropped": "The 2013.6 interior and half-final pools are not carried (the 2012 drive model keeps them).",
    }
    second, pass_errors = drive_model_second_pass(extracted, seasons)
    model["second_pass"] = second
    errors += pass_errors
    model["reconciliation"] = {"result": "pass"}
    return model, errors


def _pool_fg_distances(fp_model):
    idx = fp_model["core_tuple_fields"].index("fg_distance")
    out = []
    pools = fp_model["pools"]
    k = CATEGORIES.index("field_goal_attempt")
    for row in pools["neutral"]:
        out += [t[idx] for t in row[k]]
    for name in ("h1_late", "late"):
        for cells in pools[name].values():
            out += [t[idx] for t in cells["field_goal_attempt"]]
    for name in ("ot_first", "ot_sudden"):
        out += [t[idx] for t in pools[name]["field_goal_attempt"]]
    return [d for d in out if d is not None]


DM_EXPLAINED = dict(dm.EXPLAINED)


def drive_model_second_pass(extracted, seasons):
    """Per season, nflverse against nflscrapR: drive counts by category and play-level kick
    counts within 1% (committed rule), unless explained."""
    rows, errors = [], []
    for s in seasons:
        a, b = extracted[("nflverse", s)], extracted[("nflscrapr", s)]
        metrics = {}
        for name, ex in (("a", a), ("b", b)):
            cnt = collections.Counter("category:" + c["category"] for c in ex["drives"])
            cnt["drives"] = len(ex["drives"])
            pc = ex["play"]["counts"]
            for key in ("fg_attempts", "fg_made", "xp_attempts", "xp_made", "safeties"):
                cnt[key] = pc.get(key, 0)
            metrics[name] = cnt
        for key in sorted(set(metrics["a"]) | set(metrics["b"])):
            x, y = metrics["a"].get(key, 0), metrics["b"].get(key, 0)
            rel = abs(x - y) / x if x else (0.0 if y == 0 else float("inf"))
            explained = SECOND_PASS_EXPLAINED.get((lb.TAG[s], key)) or SECOND_PASS_EXPLAINED.get(("*", key))
            status = "match" if x == y else ("within 1%" if rel <= COUNT_TOLERANCE else
                                             ("explained" if explained else "UNEXPLAINED"))
            if status == "UNEXPLAINED":
                errors.append("drive-model second pass %s %s: nflverse %s, nflscrapR %s" % (lb.TAG[s], key, x, y))
            row = {"season": lb.TAG[s], "metric": key, "nflverse": x, "nflscrapr": y, "status": status}
            if status == "explained":
                row["explanation"] = explained
            rows.append(row)
    return {"source": "nflscrapR reg_pbp, identical classifier, drive key 'drive'",
            "independence": "Both files derive from the NFL GSIS feed; the second pass checks the parse and the "
                            "classifier, not an independent observation.",
            "rules": "Counts within 1% unless explained.",
            "comparison": rows, "result": "pass" if not errors else "fail"}, errors


# Second-pass deviations explained by coding differences in the nflscrapR files.
SECOND_PASS_EXPLAINED = {
    ("2010", "safeties"): "nflscrapR sets its safety flag on five 2010 plays whose descriptions record no safety (three "
                          "kickoffs, an interception and a run to the 1); the thirteen described safeties agree.",
    ("2010", "category:safety"): "One of the five spurious nflscrapR safety flags (a run to the 1) ends a drive, so "
                                 "nflscrapR shows 14 safety drives against nflverse's 13 (see safeties).",
    ("*", "xp_attempts"): "nflscrapR is missing extra-point rows (the committed 2012 explanation found 115 in 2012); "
                          "the other seasons' shortfalls are of the same kind and were not matched row by row.",
    ("*", "xp_made"): "nflscrapR is missing extra-point rows (as xp_attempts).",
    ("*", "category:other"): "nflscrapR carries fewer terminal pass, punt and field-goal rows and more no_play rows, "
                             "so some drives lose their terminal offensive play (the committed 2012 explanation).",
}


# ============================================================================ aggregate baseline

def nflcom_totals(season, dest):
    out = {}
    for table in ("passing", "rushing"):
        name = "nflcom_offense_%s_%d.csv" % (table, season)
        path = sources.source_path(name, dest)
        with open(path, newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        totals = collections.Counter()
        for r in rows:
            for k, v in r.items():
                if k in ("season", "Team"):
                    continue
                try:
                    totals[k] += int(float(v.replace(",", "")))
                except (ValueError, AttributeError):
                    pass
        out[table] = dict(totals)
    return out


def build_aggregate(extracted, seasons, drives_by_season, primary, team_games, dm_model, dest=None):
    errors = []
    counts = lambda s: primary[s]["play"]["counts"]  # noqa: E731
    base = lambda s: drives_by_season[s]  # noqa: E731  (every real drive, overtime included)
    tg = lambda s: team_games[s]  # noqa: E731

    def p(fn):
        return by_season_pairs(seasons, fn)

    def r(fn):
        return by_season_rate(seasons, fn)
    derived = {
        "gross_yards_per_pass_attempt": r(lambda s: pair(counts(s)["pass_yards"],
                                                         counts(s)["pass_attempts"] + counts(s).get("spikes", 0))),
        "yards_per_carry": r(lambda s: pair(counts(s)["rush_yards"] + counts(s).get("kneel_yards", 0),
                                            counts(s)["rush_attempts"] + counts(s).get("kneels", 0))),
        "completion_rate": p(lambda s: pair(counts(s)["completions"],
                                            counts(s)["pass_attempts"] + counts(s).get("spikes", 0))),
        "sack_rate": p(lambda s: pair(counts(s)["sacks"], counts(s)["sacks"] + counts(s)["pass_attempts"]
                                      + counts(s).get("spikes", 0))),
        "interception_rate": p(lambda s: pair(counts(s)["interceptions"],
                                              counts(s)["pass_attempts"] + counts(s).get("spikes", 0))),
        "accepted_penalties_per_team_game": r(lambda s: pair(primary[s]["play"]["penalties_accepted"], tg(s))),
        "accepted_penalty_yards_per_team_game": r(lambda s: pair(primary[s]["play"]["penalty_yards_accepted"], tg(s))),
        "penalty_first_downs_per_team_game": r(lambda s: pair(counts(s).get("penalty_first_downs", 0), tg(s))),
        "drive_penalty_per_play": r(lambda s: pair(
            sum(1 for c in base(s) for q in c["pen"] if q[4] == "A"), sum(c["exposure"][1] for c in base(s)))),
    }
    volume = {
        "points_per_team_game": r(lambda s: pair(team_points(extracted[("nflverse", s)]), tg(s))),
        "plays_per_team_game": r(lambda s: pair(sum(c["plays"] for c in base(s)), tg(s))),
        "net_yards_per_team_game": r(lambda s: pair(sum(c["net0"] for c in base(s)), tg(s))),
        "first_downs_per_team_game": r(lambda s: pair(sum(c["chains"][0] + c["chains"][1] for c in base(s)), tg(s))),
        "third_down_attempts_per_team_game": r(lambda s: pair(sum(c["chains"][2] for c in base(s)), tg(s))),
        "third_down_rate": p(lambda s: pair(sum(c["chains"][3] for c in base(s)), sum(c["chains"][2] for c in base(s)))),
        "drives_per_team_game": r(lambda s: pair(len(base(s)), tg(s))),
    }
    period = {lb.TAG[s]: dict(sorted(counts(s).items()), team_games=tg(s), games=primary[s]["games"],
                              penalties_accepted=primary[s]["play"]["penalties_accepted"],
                              penalty_yards_accepted=primary[s]["play"]["penalty_yards_accepted"])
              for s in seasons}
    pooled_totals = collections.Counter()
    for values in period.values():
        pooled_totals.update(values)
    q = lambda name: derived[name]["pooled"][0] / derived[name]["pooled"][1]  # noqa: E731
    v = lambda name: volume[name]["pooled"][0] / volume[name]["pooled"][1]  # noqa: E731
    outcomes = {k: dm_model["category_counts"][k] for k in CATEGORIES}
    n_drives = sum(outcomes.values())
    model = {
        "drives_per_team_game": v("drives_per_team_game"),
        "plays_per_team_game": v("plays_per_team_game"),
        "yards_per_team_game": v("net_yards_per_team_game"),
        "points_per_team_game": v("points_per_team_game"),
        "third_down_rate": v("third_down_rate"),
        "penalty_per_play": q("drive_penalty_per_play"),
        "field_goal_accuracy": dm_model["rates"]["field_goal"][0] / dm_model["rates"]["field_goal"][1],
        "drive_outcomes": {
            "touchdown": outcomes["touchdown"] / n_drives,
            "field_goal": outcomes["field_goal_attempt"] / n_drives,
            "punt": outcomes["punt"] / n_drives,
            "turnover": (outcomes["interception"] + outcomes["fumble_lost"]) / n_drives,
            "other": (outcomes["downs"] + outcomes["safety"] + outcomes["clock"]) / n_drives},
        "definitions": "Pooled, equal weight per event, from the integer pairs in derived and volume.",
    }
    agg = {
        "schema": AGG_SCHEMA,
        "seasons": [lb.TAG[s] for s in seasons],
        "season_type": "regular",
        "information_boundary": information_boundary(seasons),
        "provenance": provenance(seasons),
        "builder": "scripts/research/build_2010_2014_league_base.py",
        "specification_sha256": pre_build_specification.digest(),
        "sources": source_header(seasons),
        "derived": derived,
        "volume": volume,
        "period_totals_by_season": period,
        "period_totals": {
            "team_games": sum(tg(s) for s in seasons), "games": sum(primary[s]["games"] for s in seasons),
            "field_goal_attempts": dm_model["rates"]["field_goal"][1],
            "field_goals_made": dm_model["rates"]["field_goal"][0],
            "extra_point_attempts": dm_model["rates"]["extra_point"][1],
            "extra_points_made": dm_model["rates"]["extra_point"][0],
            "two_point_attempts": dm_model["rates"]["two_point"][1],
            "two_point_made": dm_model["rates"]["two_point"][0],
            "safeties": dm_model["rates"]["safeties"],
            "interceptions": dm_model["category_counts"]["interception"],
        },
        "model": model,
        "injury_model": {"severity": {}, "note": "Injury parameters live in the 2010-2014w4 injury calibration."},
        "definitions": {
            "gross_yards_per_pass_attempt": "Gross passing yards (completions) per pass attempt including spikes; "
                                            "sacks excluded (the NFL.com Att and Pass Yds definitions).",
            "yards_per_carry": "Rushing yards per rush attempt, kneels included (NFL.com definition).",
            "completion_rate": "Completions per pass attempt including spikes.",
            "accepted_penalties_per_team_game": "Accepted penalty clauses parsed from every play description "
                                                "(offsetting and declined excluded), per team-game: the published "
                                                "count of penalties accepted against a club.",
            "drive_penalty_per_play": "Accepted clauses on drive rows per drive snap (scrimmage and no-play rows): the "
                                      "per-play factor kept for the R11 fallback.",
            "points_per_team_game": "All points scored (touchdowns, tries, field goals, safeties) per team-game, "
                                    "from the rebuilt running score.",
        },
    }
    if 2012 in seasons:
        # The 2012 replacement-officials games (Weeks 1-3) stay in; the sensitivity is reported.
        weeks = primary[2012]["play"]["penalties_by_week"]
        out_pen = sum(v[0] for w, v in weeks.items() if w in ("1", "2", "3"))
        out_games = sum(v[1] for w, v in weeks.items() if w in ("1", "2", "3"))
        k, n = derived["accepted_penalties_per_team_game"]["pooled"]
        agg["replacement_officials_sensitivity"] = {
            "games_2012_weeks_1_3": out_games,
            "accepted_penalties_per_team_game_with": k / n,
            "accepted_penalties_per_team_game_without": (k - out_pen) / (n - 2 * out_games),
            "difference": k / n - (k - out_pen) / (n - 2 * out_games),
            "rule": "kept in the base (specification section 2); the without-value drops the 2012 Weeks 1-3 games"}
    rec, rec_errors = reconcile_nflcom(seasons, primary, extracted)
    agg["reconciliation"] = rec
    errors += rec_errors
    return agg, errors


def team_points(season_extract):
    return season_extract["play"]["points"]


NFLCOM_KEYS = {"pass_attempts_incl_spikes": ("passing", "Att"), "completions": ("passing", "Cmp"),
               "pass_yards": ("passing", "Pass Yds"), "pass_td": ("passing", "TD"), "interceptions": ("passing", "INT"),
               "sacks": ("passing", "Sck"), "rush_attempts_incl_kneels": ("rushing", "Att"),
               "rush_yards_incl_kneels": ("rushing", "Rush Yds"), "rush_td": ("rushing", "TD")}


def reconcile_nflcom(seasons, primary, extracted):
    """Play-by-play totals against the NFL.com offensive team tables, 2010-2013 (within 1%)."""
    rows, errors = [], []
    dest = extracted.get("_dest")
    for s in seasons:
        if s >= 2014 or dest is None:
            continue
        nfl = nflcom_totals(s, dest)
        c = primary[s]["play"]["counts"]
        mine = {"pass_attempts_incl_spikes": c["pass_attempts"] + c.get("spikes", 0), "completions": c["completions"],
                "pass_yards": c["pass_yards"], "pass_td": c.get("pass_td", 0), "interceptions": c["interceptions"],
                "sacks": c["sacks"], "rush_attempts_incl_kneels": c["rush_attempts"] + c.get("kneels", 0),
                "rush_yards_incl_kneels": c["rush_yards"] + c.get("kneel_yards", 0), "rush_td": c.get("rush_td", 0)}
        for key, (table, column) in NFLCOM_KEYS.items():
            x, y = mine[key], nfl[table].get(column)
            if y is None:
                rows.append({"season": lb.TAG[s], "metric": key, "pbp": x, "nflcom": None, "status": "column missing"})
                continue
            rel = abs(x - y) / y if y else 0.0
            status = "match" if x == y else ("within 1%" if rel <= COUNT_TOLERANCE else "UNEXPLAINED")
            if status == "UNEXPLAINED":
                errors.append("NFL.com %s %s: play-by-play %s, NFL.com %s" % (lb.TAG[s], key, x, y))
            rows.append({"season": lb.TAG[s], "metric": key, "pbp": x, "nflcom": y, "status": status})
    return {"rule": "play-by-play totals within 1% of the NFL.com offensive team tables (2010-2013); 2014 Weeks 1-4 "
                    "is single publisher (nflverse; no table compiled before the gate is fetched)",
            "penalties": "unreconciled: the B2 source set holds no NFL.com penalty table; the accepted-penalty "
                         "parse is checked against nflscrapR only (annotation second pass)",
            "comparison": rows, "result": "pass" if not errors else "fail"}, errors


# ============================================================================ validate

FORBIDDEN_KEYS = {"game_id", "posteam", "defteam", "team", "club", "player", "player_id", "gsis_id", "date",
                  "game_date", "week", "play_id", "home_team", "away_team", "stadium", "stadium_id", "name"}


def forbidden(key):
    low = key.lower()
    return low in FORBIDDEN_KEYS or low.endswith("_id") or low.endswith("_player") or low.endswith("_team")


def _keys(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.add(k)
            _keys(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _keys(v, out)
    return out


def validate(fp_model, dm_model, agg):
    """Structural checks on the three artifacts (no sources needed)."""
    errors = []
    if fp_model.get("schema") != FP_SCHEMA or dm_model.get("schema") != DM_SCHEMA or agg.get("schema") != AGG_SCHEMA:
        errors.append("schema differs")
    if fp_model.get("clock_scale") != dm_model.get("clock_scale"):
        errors.append("clock_scale differs between the field-position and drive models")
    spec = pre_build_specification.digest()
    for name, art in (("field_position", fp_model), ("drive_model", dm_model), ("aggregate", agg)):
        if art.get("specification_sha256") != spec:
            errors.append("%s header specification digest differs" % name)
        if "no club, game, player or date field" not in art.get("information_boundary", ""):
            errors.append("%s lacks the information boundary" % name)
        for key in _keys({k: v for k, v in art.items() if k not in ("sources", "EXPLAINED", "provenance")}, set()):
            if forbidden(key):
                errors.append("%s holds a forbidden key %r" % (name, key))
    fields = fp_model.get("tuple_fields", [])
    if fields[:len(V2_TUPLE_FIELDS)] != list(V2_TUPLE_FIELDS):
        errors.append("tuple fields do not extend the v2 list")
    width = len(fields)
    total = sum(sum(row) for row in fp_model["neutral_counts"])
    total += sum(sum(v.values()) for v in fp_model["h1_late_counts"].values())
    total += sum(sum(v.values()) for v in fp_model["late_counts"].values())
    for name in ("ot_first", "ot_sudden", "ot_untied"):
        total += sum(fp_model[name + "_counts"].values())
    partition = fp_model["partition"]
    if total != sum(partition["counts"].values()) or total + partition["ot_excluded"] != partition["drives"]:
        errors.append("partition counts do not sum to the drives")
    groups = []
    pools = fp_model["pools"]
    for b, row in enumerate(fp_model["neutral_counts"]):
        groups += [(n, pools["neutral"][b][k]) for k, n in enumerate(row)]
    for name in ("h1_late", "late"):
        for key, cells in fp_model[name + "_counts"].items():
            groups += [(cells[k], pools[name].get(key, {}).get(k, [])) for k in CATEGORIES]
    for name in ("ot_first", "ot_sudden"):
        groups += [(fp_model[name + "_counts"][k], pools[name][k]) for k in CATEGORIES]
    missing = 0
    for n, pool in groups:
        if n < len(pool):
            errors.append("a pool holds more tuples than its count")
            break
        missing += n - len(pool)
        if any(len(t) != width for t in pool):
            errors.append("a tuple has the wrong number of fields")
            break
    documented = fp_model["corrections"]["non_renderable"]
    # The excluded-overtime-free count of non-renderable drives must equal the pools' gap
    # (ot_untied drives are counted but never pooled).
    untied = sum(fp_model["ot_untied_counts"].values())
    if missing + 0 < 0 or missing > documented["safety"] + documented["touchdown"] + documented["zero_play_terminal"] + untied:
        errors.append("non-renderable drives exceed the documented corrections")
    for label in fp_model["preregistration"]["late_time_buckets"]:
        for need in fp_model["preregistration"]["needs"]:
            cell = fp_model["cell_map"].get("%s|%s" % (label, need))
            if cell is None or cell not in fp_model["late_counts"]:
                errors.append("late cell map incomplete for %s|%s" % (label, need))
    for cell, cells in fp_model["late_counts"].items():
        if sum(cells.values()) < MIN_CELL:
            errors.append("late cell %s under MIN_CELL" % cell)
    for key, cells in fp_model["h1_late_counts"].items():
        if sum(cells.values()) < MIN_CELL:
            errors.append("h1_late bucket %s under MIN_CELL" % key)
    for name, width_ in (("kickoff_pool", len(fp_model["kick_fields"])), ("free_kick_pool", len(fp_model["kick_fields"])),
                         ("punt_pool", len(fp_model["punt_fields"])),
                         ("interception_pool", len(fp_model["turnover_fields"])),
                         ("fumble_pool", len(fp_model["turnover_fields"]))):
        if any(len(r) != width_ for r in fp_model[name]):
            errors.append("%s records have the wrong width" % name)
    season_index = fp_model["kick_fields"].index("season")
    if any(r[season_index] < KICKOFF_FROM for r in fp_model["kickoff_pool"]):
        errors.append("a 2010 kickoff record is in the kickoff pool")
    t_season = fields.index("season")
    for name in ("ot_first", "ot_sudden"):
        for pool in pools[name].values():
            if any(t[t_season] < OT_FROM for t in pool):
                errors.append("a 2010-2011 overtime tuple is in %s" % name)
    # Rate denominators above 0 (a zero denominator would crash a draw path).
    for key, value in fp_model["rates"].items():
        if isinstance(value, list) and len(value) == 2 and value[1] <= 0:
            errors.append("field-position rate %s has a zero denominator" % key)
    for key, value in dm_model["rates"].items():
        if isinstance(value, list) and len(value) == 2 and value[1] <= 0:
            errors.append("drive-model rate %s has a zero denominator" % key)
    for label, value in dm_model["rates"]["fg_by_distance"].items():
        if value[1] <= 0:
            errors.append("field-goal band %s has no attempts" % label)
    for block in (agg["derived"], agg["volume"]):
        for key, value in block.items():
            if value["pooled"][1] <= 0:
                errors.append("aggregate %s has a zero denominator" % key)
    # The header against the contents.
    if fp_model["seasons"] != dm_model["seasons"] or dm_model["seasons"] != agg["seasons"]:
        errors.append("the three artifacts name different seasons")
    if sorted(fp_model["clock_scale_by_season"]) != sorted(fp_model["seasons"]):
        errors.append("clock_scale_by_season does not cover the header seasons")
    if fp_model["clock_scale"] != [sum(v[0] for v in fp_model["clock_scale_by_season"].values()),
                                   sum(v[1] for v in fp_model["clock_scale_by_season"].values())]:
        errors.append("the pooled clock scale is not the sum of the seasons'")
    return errors


# ============================================================================ the library record

RECORD = ROOT / "library" / "2010_2014_calibration_base.md"
BEGIN, END = "<!-- generated:begin -->", "<!-- generated:end -->"


def _share(block):
    k, n = block["pooled"]
    p = block["drift"]["p"] if block.get("drift") else None
    return "%d/%d = %.4f%s" % (k, n, k / n if n else float("nan"), "" if p is None else " (drift p %.4f)" % p)


def _rate(block):
    k, n = block["pooled"]
    p = block["drift"]["p"] if block.get("drift") else None
    return "%.4f per unit (%d / %d)%s" % (k / n, k, n, "" if p is None else ", drift p %.4f" % p)


def _mean(block):
    n, total, _ = block["pooled"]
    p = block["drift"]["p"] if block.get("drift") and block["drift"].get("p") is not None else None
    return "%.3f (n %d)%s" % (total / n if n else float("nan"), n, "" if p is None else ", drift p %.4f" % p)


def tables_md(fp_model, dm_model, agg):
    out = ["Generated by `scripts/research/build_2010_2014_league_base.py` from the three artifacts; do not edit.", ""]
    part = fp_model["partition"]
    out.append("**Partition** (drives): " + ", ".join("%s %d" % kv for kv in part["counts"].items())
               + "; 2010-2011 overtime excluded %d; total %d." % (part["ot_excluded"], part["drives"]))
    out.append("")
    out.append("| Season | Games | Drives | " + " | ".join(part["counts"]) + " | Clock scale |")
    out.append("|---|---|---|" + "---|" * len(part["counts"]) + "---|")
    for season in fp_model["seasons"]:
        by = part["by_season"][season]
        out.append("| %s | %d | %d | %s | %d / %d |" % (
            season, dm_model["games"][season], sum(by.values()),
            " | ".join(str(by.get(k, 0)) for k in part["counts"]), *fp_model["clock_scale_by_season"][season]))
    out.append("")
    out.append("Pooled clock scale: %d / %d." % tuple(fp_model["clock_scale"]))
    r = fp_model["corrections"]["r17a_seconds"]
    out.append("")
    out.append("**R17a drive seconds**: group medians of TOP - e " + ", ".join(
        "%s %s s" % kv for kv in r["group_medians"].items()) + "; drives by group and basis " + ", ".join(
        "%s %d" % kv for kv in r["by_group_basis"].items()) + ".")
    g = fp_model["corrections"]["r17a_grouping"]
    out.append("By grouping (not accepted; changed from the committed rule): " + "; ".join(
        "%s fixed_drive %d and %d of %d, drive %d and %d of %d" % (
            s, v["fixed_drive"]["not_accepted"], v["fixed_drive"]["changed_from_committed_rule"],
            v["fixed_drive"]["drives"], v["drive"]["not_accepted"], v["drive"]["changed_from_committed_rule"],
            v["drive"]["drives"]) for s, v in g.items()) + "; totals fixed_drive %d, drive %d changed." % (
        sum(v["fixed_drive"]["changed_from_committed_rule"] for v in g.values()),
        sum(v["drive"]["changed_from_committed_rule"] for v in g.values())))
    c = fp_model["constants"]
    out.append("")
    out.append("**Constants reproduced**: spike window %s s (2010-2012 maximum, %d spikes at it); early field goal %s s "
               "(next %s)." % (c["spike_window"]["pre_divergence_max_seconds"], c["spike_window"]["count_at_max"],
                               c["early_field_goal"]["max_seconds"], ", ".join(str(v) for v in c["early_field_goal"]["next_largest"])))
    out.append("")
    out.append("**Cells**: late " + ", ".join("%s %d" % (k, sum(v.values())) for k, v in sorted(fp_model["late_counts"].items()))
               + "; h1_late " + ", ".join("%s %d" % (k, sum(v.values())) for k, v in sorted(fp_model["h1_late_counts"].items()))
               + "; ot_first %d, ot_sudden %d, ot_untied %d." % tuple(
                   sum(fp_model[n + "_counts"].values()) for n in ("ot_first", "ot_sudden", "ot_untied")))
    out.append("")
    out.append("**Transition pools**: " + ", ".join("%s %d" % (k, len(fp_model[k])) for k in
                                                     ("kickoff_pool", "free_kick_pool", "punt_pool", "interception_pool",
                                                      "fumble_pool"))
               + "; retained " + ", ".join("%s %d" % (k, len(v)) for k, v in fp_model.get("retained_kick_pools", {}).items())
               + ".")
    rates = dm_model["rates"]
    out.append("")
    out.append("| Drive-model rate | Pooled | Drift p |")
    out.append("|---|---|---|")
    for label in ("<30", "30-39", "40-49", "50+"):
        k, n = rates["fg_by_distance"][label]
        p = dm_model["rates_by_season"]["fg_by_distance"][label]["drift"]["p"]
        out.append("| FG %s | %d/%d = %.4f | %.4f |" % (label, k, n, k / n, p))
    for name in ("field_goal", "extra_point", "two_point", "td_type_pass", "turnover_type_interception"):
        k, n = rates[name]
        out.append("| %s | %d/%d = %.4f | %.4f |" % (name, k, n, k / n, dm_model["rates_by_season"][name]["drift"]["p"]))
    two = dm_model["two_point_definitions"]["scrimmage_not_nullified"]["pooled"]
    out.append("| two_point, scrimmage definition | %d/%d = %.4f | |" % (two[0], two[1], two[0] / two[1]))
    out.append("")
    out.append("| Season | FG | XP | Two-point | Completion | Gross YPA | YPC | Penalties per team-game | Points per team-game |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    rb, d, v = dm_model["rates_by_season"], agg["derived"], agg["volume"]
    for season in fp_model["seasons"]:
        def ratio(pair_):
            return pair_[0] / pair_[1] if pair_[1] else float("nan")
        out.append("| %s | %.4f | %.4f | %d/%d | %.4f | %.3f | %.3f | %.3f | %.3f |" % (
            season, ratio(rb["field_goal"]["by_season"][season]), ratio(rb["extra_point"]["by_season"][season]),
            *rb["two_point"]["by_season"][season], ratio(d["completion_rate"]["by_season"][season]),
            ratio(d["gross_yards_per_pass_attempt"]["by_season"][season]), ratio(d["yards_per_carry"]["by_season"][season]),
            ratio(d["accepted_penalties_per_team_game"]["by_season"][season]),
            ratio(v["points_per_team_game"]["by_season"][season])))
    fgd = dm_model["field_goal_distance"]
    out.append("")
    out.append("**FG distance logistic** (events): slope %.5f per yard (SE %.4f); pass 2 %.5f (SE %.4f); band intercepts "
               % (fgd["slope_per_yard"], fgd["slope_se"], fgd["second_pass"]["slope_per_yard"], fgd["second_pass"]["slope_se"])
               + ", ".join("%s %.4f" % (k, v["intercept"]) for k, v in fgd["bands"].items()) + ".")
    out.append("")
    out.append("| Aggregate | Pooled (equal weight per event) |")
    out.append("|---|---|")
    for name, block in agg["derived"].items():
        out.append("| %s | %s |" % (name, _rate(block) if block["drift"] and block["drift"]["test"].startswith("poisson")
                                     else _share(block)))
    for name, block in agg["volume"].items():
        out.append("| %s | %s |" % (name, _rate(block) if block["drift"] and block["drift"]["test"].startswith("poisson")
                                     else _share(block)))
    ro = agg.get("replacement_officials_sensitivity")
    if ro:
        out.append("")
        out.append("**Replacement officials** (2012 Weeks 1-3, %d games, kept): accepted penalties per team-game %.4f with, "
                   "%.4f without (difference %+.4f)." % (ro["games_2012_weeks_1_3"], ro["accepted_penalties_per_team_game_with"],
                                                        ro["accepted_penalties_per_team_game_without"], ro["difference"]))
    rec = agg["reconciliation"]
    statuses = collections.Counter(row["status"] for row in rec["comparison"])
    out.append("")
    out.append("**NFL.com reconciliation** (2010-2013): " + ", ".join("%s %d" % kv for kv in sorted(statuses.items()))
               + " of %d comparisons; result %s. Penalties: %s." % (len(rec["comparison"]), rec["result"], rec["penalties"]))
    for name, block in (("field position", fp_model["second_pass"]), ("drive model", dm_model["second_pass"])):
        statuses = collections.Counter(row["status"] for row in block["comparison"])
        out.append("")
        out.append("**Second pass, %s**: " % name + ", ".join("%s %d" % kv for kv in sorted(statuses.items()))
                   + "; result %s." % block["result"])
        for row in block["comparison"]:
            if row["status"] == "explained":
                out.append("- %s %s: nflverse %s, nflscrapR %s. %s" % (row["season"], row["metric"], row["nflverse"],
                                                                       row["nflscrapr"], row["explanation"]))
    if "annotation_second_pass" in fp_model:
        block = fp_model["annotation_second_pass"]
        statuses = collections.Counter(row["status"] for row in block["comparison"])
        out.append("")
        out.append("**Second pass, annotations**: " + ", ".join("%s %d" % kv for kv in sorted(statuses.items()))
                   + "; result %s." % block["result"])
        for row in block["comparison"]:
            if row["status"] == "explained":
                out.append("- %s %s: nflverse %s, nflscrapR %s. %s" % (row["season"], row["metric"], row["nflverse"],
                                                                       row["nflscrapr"], row["explanation"]))
        out.append("")
        out.append("**Relocation feasibility**: " + "; ".join(
            "%s %d tuples, %d with defensive penalty yards over start - 1, %d outside placement" % (
                k, v["tuples"], v["defensive_penalty_yards_over_start_minus_1"], v["start_outside_placement"])
            for k, v in fp_model["relocation_feasibility"].items()) + ".")
        out.append("")
        out.append("**Emphasis counts** (accepted, per exposure): " + "; ".join(
            "%s %s" % (k, ", ".join("%s %d/%d" % (s, *v) for s, v in block_["by_season"].items()))
            for k, block_ in fp_model["emphasis_counts"].items()) + ".")
        out.append("")
        out.append("**Lost-fumble terminal kind**: " + ", ".join(
            "%s %d" % kv for kv in fp_model["fumble_lost_terminal_kind"].items()) + ".")
    return "\n".join(out) + "\n"


def render_record(fp_model, dm_model, agg):
    text = RECORD.read_text()
    head, rest = text.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    return head + BEGIN + "\n" + tables_md(fp_model, dm_model, agg) + END + tail


# ============================================================================ main

def render(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n"


def outputs(mode):
    spec = MODES[mode]
    stem, suffix = spec["stem"], spec.get("suffix", "")
    return {
        "field_position": DATA / ("%s_nfl_field_position_model%s.json" % (stem, suffix)),
        "drive_model": DATA / ("%s_nfl_drive_model%s.json" % (stem, suffix)),
        "aggregate": DATA / ("%s_nfl_aggregate_baseline%s.json" % (stem, suffix)),
    }


def core_projection(fp_model):
    """The field-position artifact projected onto its core fields (annotation keys and every
    record's annotation suffix dropped)."""
    core = copy.deepcopy(fp_model)
    tw, kw, pw = len(CORE_TUPLE_FIELDS), len(CORE_KICK_FIELDS), len(CORE_PUNT_FIELDS)
    for key in ("retained_kick_pools", "penalty_types", "penalty_nominal_yards", "pen_fields", "kick_pen_fields",
                "fumble_fields", "auto_first_down", "emphasis_counts", "relocation_feasibility", "fumble_summary",
                "fumble_lost_terminal_kind", "kick_mappings", "penalty_unparsed_clauses", "annotation_rules",
                "annotation_second_pass"):
        core.pop(key, None)
    core["stage"] = "core"
    core["tuple_fields"] = list(CORE_TUPLE_FIELDS)
    core["kick_fields"] = list(CORE_KICK_FIELDS)
    core["punt_fields"] = list(CORE_PUNT_FIELDS)
    pools = core["pools"]
    pools["neutral"] = [[[t[:tw] for t in p] for p in row] for row in pools["neutral"]]
    for name in ("h1_late", "late"):
        pools[name] = {key: {k: [t[:tw] for t in v] for k, v in cells.items()} for key, cells in pools[name].items()}
    for name in ("ot_first", "ot_sudden"):
        pools[name] = {k: [t[:tw] for t in v] for k, v in pools[name].items()}
    for pool in pools["neutral"]:
        for p in pool:
            p.sort(key=lambda t: json.dumps(t))
    for name in ("h1_late", "late"):
        for cells in pools[name].values():
            for v in cells.values():
                v.sort(key=lambda t: json.dumps(t))
    for name in ("ot_first", "ot_sudden"):
        for v in pools[name].values():
            v.sort(key=lambda t: json.dumps(t))
    core["kickoff_pool"] = [r[:kw] for r in core["kickoff_pool"] if r[5] != "retained"]
    core["free_kick_pool"] = [r[:kw] for r in core["free_kick_pool"] if r[5] != "retained"]
    core["punt_pool"] = [r[:pw] for r in core["punt_pool"] if r[1] != "retained"]
    return core


def run(mode, dest, stage="all", log=print):
    seasons = MODES[mode]["seasons"]
    extracted = extract_all(seasons, dest, log=log)
    extracted["_dest"] = dest
    errors = []
    if 2012 in seasons:
        errors += regression_2012(dest, extracted)
    fp_model, dm_model, agg, build_errors = build(extracted, seasons, stage="all")
    errors += build_errors
    fp_model["corrections"]["r17a_grouping"] = r17a_grouping_reconciliation(
        dest, seasons, fp_model["corrections"]["r17a_seconds"]["group_medians"])
    second, sp_errors = field_position_second_pass(extracted, seasons)
    fp_model["second_pass"] = second
    errors += sp_errors
    errors += validate(fp_model, dm_model, agg)
    result = "pass" if not errors else "fail"
    fp_model["reconciliation"] = {"result": result}
    dm_model["reconciliation"]["result"] = result
    return fp_model, dm_model, agg, errors


def summary(ex):
    """Counts compared between the passes (committed summary, on compact drives)."""
    drives = ex["drives"]
    out = collections.Counter()
    out["drives"] = len(drives)
    for c in drives:
        out["category:" + c["category"]] += 1
    out["kneels"] = sum(len(c["kneel_yards"]) for c in drives)
    out["spikes"] = sum(c["spikes"] for c in drives)
    out["sacks"] = sum(c["sacks"] for c in drives)
    for i, name in enumerate(fp.CHAIN_FIELDS):
        out["chains:" + name] = sum(c["chains"][i] for c in drives)
    for name in ("kickoff_pool", "free_kick_pool", "punt_pool", "interception_pool", "fumble_pool"):
        out[name] = len(ex["pools"][name])
    return out


FP_SECOND_PASS_EXPLAINED_BY_SEASON = {
    ("2010", "category:safety"): SECOND_PASS_EXPLAINED[("2010", "category:safety")],
    ("2014w4", "kneels"): "nflscrapR codes six 2014 Weeks 1-4 kickoff touchbacks whose description says the returner "
                          "knelt as quarterback kneels and lacks one real kneel (94 against 99 in 61 games); nflverse "
                          "is used.",
    ("2014w4", "sacks"): "nflscrapR codes five 2014 Weeks 1-4 plays as sacks that nflverse codes as runs or no-plays "
                         "(two of them aborted-snap fumbles), and nflverse two that nflscrapR codes as runs: 240 "
                         "against 243 in 61 games; nflverse is used.",
}
FP_SECOND_PASS_EXPLAINED = {
    ("2010", "safeties"): "nflscrapR sets its safety flag on five 2010 plays whose descriptions record no safety (three "
                          "kickoffs, an interception and a run to the 1); the thirteen described safeties agree.",
    ("2010", "category:safety"): "One of the five spurious nflscrapR safety flags (a run to the 1) ends a drive, so "
                                 "nflscrapR shows 14 safety drives against nflverse's 13 (see safeties).",
    "punt_pool": "nflscrapR has fewer punt rows than nflverse (the committed 2012 explanation).",
    "category:punt": "nflscrapR has fewer punt rows (as punt_pool).",
    "category:other": "nflscrapR drops terminal offensive rows (committed 2012 explanation).",
    "spikes": "nflscrapR codes some spikes as ordinary incomplete passes (the committed 2012 explanation; the other "
              "seasons' one- or two-spike gaps were not matched row by row).",
}


def field_position_second_pass(extracted, seasons):
    rows, errors = [], []
    pooled = {"a": collections.Counter(), "b": collections.Counter()}
    for s in seasons:
        a, b = summary(extracted[("nflverse", s)]), summary(extracted[("nflscrapr", s)])
        pooled["a"].update(a)
        pooled["b"].update(b)
        for key in sorted(set(a) | set(b)):
            x, y = a.get(key, 0), b.get(key, 0)
            rel = abs(x - y) / x if x else (0.0 if y == 0 else float("inf"))
            explained = FP_SECOND_PASS_EXPLAINED_BY_SEASON.get((lb.TAG[s], key)) or FP_SECOND_PASS_EXPLAINED.get(key)
            status = "match" if x == y else ("within 1%" if rel <= COUNT_TOLERANCE else
                                             ("explained" if explained else "UNEXPLAINED"))
            if status == "UNEXPLAINED":
                errors.append("field-position second pass %s %s: nflverse %s, nflscrapR %s" % (lb.TAG[s], key, x, y))
            row = {"season": lb.TAG[s], "metric": key, "nflverse": x, "nflscrapr": y, "status": status}
            if status == "explained":
                row["explanation"] = explained
            rows.append(row)
    return {"source": "nflscrapR reg_pbp, identical code, drive key 'drive'",
            "rules": "Counts within 1% per season unless explained.",
            "comparison": rows, "result": "pass" if not errors else "fail"}, errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seasons", choices=sorted(MODES), default="2010-2014w4")
    parser.add_argument("--sources", type=Path, default=sources.default_dest())
    parser.add_argument("--stage", choices=("core", "annotations", "all"), default="all")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.sources is None or not Path(args.sources).is_dir():
        print("sources not present (set $SOURCES_2010_2014_DIR or --sources); nothing built", file=sys.stderr)
        return 2
    fp_model, dm_model, agg, errors = run(args.seasons, args.sources, args.stage, log=lambda m: print(m, file=sys.stderr))
    if errors:
        for error in errors:
            print("BUILD FAILURE: " + error, file=sys.stderr)
        return 1
    paths = outputs(args.seasons)
    texts = {"field_position": render(fp_model), "drive_model": render(dm_model), "aggregate": render(agg)}
    record = render_record(fp_model, dm_model, agg) if args.seasons == "2010-2014w4" else None
    if args.check:
        failed = False
        if record is not None:
            ok = RECORD.read_text() == record
            print("%s %s (generated tables)" % ("reproduced" if ok else "DIFFERS", RECORD.relative_to(ROOT)))
            failed |= not ok
        for role, path in paths.items():
            current = path.read_text() if path.exists() else ""
            if role == "field_position" and args.stage == "core":
                ok = current and render(core_projection(json.loads(current))) == render(core_projection(fp_model))
            else:
                ok = current == texts[role]
            print("%s %s" % ("reproduced" if ok else "DIFFERS", path.relative_to(ROOT)))
            failed |= not ok
        return 1 if failed else 0
    for role, path in paths.items():
        path.write_text(texts[role])
        print("wrote %s (%d bytes)" % (path.relative_to(ROOT), len(texts[role])))
    if record is not None:
        RECORD.write_text(record)
        print("wrote the tables of %s" % RECORD.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
