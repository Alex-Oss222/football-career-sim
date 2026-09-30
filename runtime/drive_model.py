"""The sourced 2012 offensive-drive model (kernel 2013.6 artifact).

Kernel 2013.7 draws its drives from runtime/field_position.py but still uses
this module for the category list, the legacy apply_edge shift, category
draws, the clock scale, field-goal accuracy by distance and the kick rates.

The artifact (library/data/2012_nfl_drive_model.json) is built by
scripts/research/build_2012_drive_model.py from 2012 regular-season
play-by-play. It holds category counts, pools of real drive tuples
([plays, net_yards, seconds], field-goal drives adding [kick_distance, made,
blocked]) and integer rate pairs. It carries no team or game identifiers.

This module holds no random state: callers pass the kernel's possession RNG,
so every draw stays on the possession stream. Nothing here knows which club
is the protagonist; every club uses the identical code path.
"""
from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "library/data/2012_nfl_drive_model.json"

CATEGORIES = (
    "touchdown", "field_goal_attempt", "punt", "interception",
    "fumble_lost", "downs", "safety", "clock",
)
TURNOVER_CATEGORIES = ("interception", "fumble_lost")
PREREGISTERED_BUCKET_EDGES = [[0, 30], [31, 60], [61, 120], [121, 240], [241, 1800]]


@lru_cache(maxsize=1)
def _raw():
    return json.loads(DATA.read_text())


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _pair_ok(pair):
    return (
        isinstance(pair, list) and len(pair) == 2 and all(_is_int(v) for v in pair)
        and 0 <= pair[0] <= pair[1] and pair[1] > 0
    )


def validate(data=None):
    """Structural checks on the artifact; returns a list of errors."""
    data = data if data is not None else _raw()
    errors = []
    if data.get("categories") != list(CATEGORIES):
        errors.append("drive model categories differ from the kernel categories")
    if data.get("bucket_edges") != PREREGISTERED_BUCKET_EDGES:
        errors.append("bucket edges differ from the pre-registered list")
    pools = data.get("pools", {})
    interior = pools.get("interior", {})
    counts = data.get("interior_counts", {})
    for category in CATEGORIES:
        n = counts.get(category)
        if not _is_int(n) or n < 0 or n != len(interior.get(category, [])):
            errors.append(f"interior count for {category} is not an integer matching its pool")
    for key, cells in data.get("half_final_counts", {}).items():
        pool = pools.get("half_final", {}).get(key, {})
        for category, n in cells.items():
            if not _is_int(n) or n != len(pool.get(category, [])):
                errors.append(f"half-final count {key}/{category} is not an integer matching its pool")
        if not sum(cells.values()):
            errors.append(f"half-final bucket {key} is empty")
    for key in data.get("bucket_pool", {}).values():
        if key not in data.get("half_final_counts", {}):
            errors.append(f"bucket pool {key} missing")
    for name, pair in data.get("rates", {}).get("fg_by_distance", {}).items():
        if not _pair_ok(pair):
            errors.append(f"fg_by_distance {name} is not a valid integer pair")
    for name in ("field_goal", "extra_point", "two_point", "td_type_pass", "turnover_type_interception"):
        if not _pair_ok(data.get("rates", {}).get(name)):
            errors.append(f"rate {name} is not a valid integer pair")
    kicks = data.get("rates", {}).get("safety_free_kick_returned")
    if not (isinstance(kicks, list) and len(kicks) == 2 and all(_is_int(v) and v >= 0 for v in kicks) and sum(kicks)):
        errors.append("safety free-kick counts invalid")
    scale = data.get("clock_scale")
    if not (isinstance(scale, list) and len(scale) == 2 and all(_is_int(v) and v > 0 for v in scale)):
        errors.append("clock_scale is not a positive integer pair")
    ranges = data.get("net_range", {})
    for category in CATEGORIES:
        low_high = ranges.get(category)
        if not low_high:
            errors.append(f"net range missing for {category}")
            continue
        low, high = low_high
        tuples = list(interior.get(category, []))
        for bucket in pools.get("half_final", {}).values():
            tuples += bucket.get(category, [])
        if any(not low <= t[1] <= high for t in tuples):
            errors.append(f"{category} tuple outside its net range")
        if category == "field_goal_attempt" and any(len(t) != 6 or not _is_int(t[3]) for t in tuples):
            errors.append("field-goal tuples require a kick distance")
    return errors


@lru_cache(maxsize=1)
def load():
    """The validated artifact; treat as read-only."""
    data = _raw()
    errors = validate(data)
    if errors:
        raise ValueError("invalid drive model: " + "; ".join(errors))
    return data


def _ratio(counts):
    total = sum(counts.values())
    return {c: counts.get(c, 0) / total for c in CATEGORIES}


def interior_probs():
    return _ratio(load()["interior_counts"])


def bucket(remaining_seconds):
    """The half-final pool key for the seconds left in the window."""
    data = load()
    remaining = max(0, int(remaining_seconds))
    for low, high in data["bucket_edges"]:
        if remaining <= high:
            return data["bucket_pool"]["%d-%d" % (low, high)]
    low, high = data["bucket_edges"][-1]
    return data["bucket_pool"]["%d-%d" % (low, high)]


def half_final_probs(pool_key):
    return _ratio(load()["half_final_counts"][pool_key])


def apply_edge(probs, edge):
    """Shift a category mix by the matchup/home edge.

    The coefficients are the legacy 2013.5 rule: touchdown += edge, punt -=
    0.65 edge and the turnover categories (pro rata) -= 0.35 edge. Values are
    clamped at zero and renormalised. Identical for every club.
    """
    adjusted = dict(probs)
    adjusted["touchdown"] = adjusted.get("touchdown", 0.0) + edge
    adjusted["punt"] = adjusted.get("punt", 0.0) - 0.65 * edge
    turnover = sum(adjusted.get(c, 0.0) for c in TURNOVER_CATEGORIES)
    if turnover > 0:
        for c in TURNOVER_CATEGORIES:
            adjusted[c] = adjusted.get(c, 0.0) - 0.35 * edge * adjusted.get(c, 0.0) / turnover
    adjusted = {c: max(0.0, adjusted.get(c, 0.0)) for c in CATEGORIES}
    total = sum(adjusted.values())
    return {c: v / total for c, v in adjusted.items()}


def draw_category(rng, probs):
    draw = rng.random()
    cumulative = 0.0
    last = None
    for category in CATEGORIES:
        chance = probs.get(category, 0.0)
        if chance <= 0:
            continue
        cumulative += chance
        last = category
        if draw < cumulative:
            return category
    return last


def scaled_seconds(tuple_row):
    num, den = load()["clock_scale"]
    return max(1, round(tuple_row[2] * num / den))


def pool(kind, category, pool_key=None):
    pools = load()["pools"]
    if kind == "interior":
        return pools["interior"].get(category, [])
    return pools["half_final"].get(pool_key, {}).get(category, [])


def sample_tuple(rng, tuples, max_seconds=None):
    """Uniform draw from a category's tuples; None when the filter empties it."""
    if max_seconds is not None:
        tuples = [t for t in tuples if scaled_seconds(t) <= max_seconds]
    if not tuples:
        return None
    return tuples[rng.randrange(len(tuples))]


def clock_tuple(rng, pool_key):
    """A clock tuple for an expiring window: that bucket's, else the nearest
    bucket that has one."""
    data = load()
    keys = list(data["half_final_counts"])
    order = [pool_key] + sorted((k for k in keys if k != pool_key),
                                key=lambda k: abs(int(k.split("-")[0]) - int(pool_key.split("-")[0])))
    for key in order:
        tuples = pool("half_final", "clock", key)
        if tuples:
            return tuples[rng.randrange(len(tuples))]
    return [0, 0, 0]


def fg_make_prob(distance):
    rates = load()["rates"]
    for label, low, high in rates["fg_bin_edges"]:
        if distance <= high:
            made, attempts = rates["fg_by_distance"][label]
            return made / attempts
    made, attempts = rates["fg_by_distance"][rates["fg_bin_edges"][-1][0]]
    return made / attempts


# Kernel 2014.4 phase 2 (defect register item 18): one logistic slope per
# yard of distance fitted on every 2010-2012 regular-season attempt, with a
# separate intercept per drive-model band anchored so that the mean fitted
# probability over the band's own 2012 attempts equals the band's 2012 make
# rate (library/data/2014_strength_calibration_v3.json, field_goal_distance;
# built by scripts/research/build_2014_strength_calibration_v3.py). The
# band rows of runtime/bands.py keep their centres by construction.
FG_DISTANCE = ROOT / "library/data/2014_strength_calibration_v3.json"


@lru_cache(maxsize=1)
def fg_distance_model():
    data = json.loads(FG_DISTANCE.read_text(encoding="utf-8"))["field_goal_distance"]
    bands = []
    for label, low, high in load()["rates"]["fg_bin_edges"]:
        band = data["bands"][label]
        bands.append((label, low, high, band["intercept"]))
    return {"slope": data["slope_per_yard"], "bands": bands}


def fg_make_prob_at(distance):
    """The make probability at one distance under the distance model: the
    band's anchored intercept plus the pooled slope times the distance."""
    model = fg_distance_model()
    intercept = model["bands"][-1][3]
    for label, low, high, a in model["bands"]:
        if distance <= high:
            intercept = a
            break
    import math
    return 1.0 / (1.0 + math.exp(-(intercept + model["slope"] * distance)))


def rate(name):
    made, attempts = load()["rates"][name]
    return made / attempts


def safety_free_kick_return_rate():
    returned, not_returned = load()["rates"]["safety_free_kick_returned"]
    return returned / (returned + not_returned)


def net_range(category):
    return tuple(load()["net_range"][category])
