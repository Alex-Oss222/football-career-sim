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

Kernel 2014.6 plumbing (batch B1): the data-dependent functions are methods
of DriveModel, one instance per calibration base
(runtime.calibration_base.CalibrationBase.drive_model), which owns the
loaded artifact and its memoised helpers. The kernel binds its base's model
once per game; the module-level functions below are the 2012 base's model,
kept for the research builders, audits and tests that read the 2012 base.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "library/data/2012_nfl_drive_model.json"

CATEGORIES = (
    "touchdown", "field_goal_attempt", "punt", "interception",
    "fumble_lost", "downs", "safety", "clock",
)
TURNOVER_CATEGORIES = ("interception", "fumble_lost")
PREREGISTERED_BUCKET_EDGES = [[0, 30], [31, 60], [61, 120], [121, 240], [241, 1800]]


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


def _ratio(counts):
    total = sum(counts.values())
    return {c: counts.get(c, 0) / total for c in CATEGORIES}


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


# Kernel 2014.4 phase 2 (defect register item 18): one logistic slope per
# yard of distance fitted on every 2010-2012 regular-season attempt, with a
# separate intercept per drive-model band anchored so that the mean fitted
# probability over the band's own 2012 attempts equals the band's 2012 make
# rate (library/data/2014_strength_calibration_v3.json, field_goal_distance;
# built by scripts/research/build_2014_strength_calibration_v3.py). The
# band rows of runtime/bands.py keep their centres by construction. Each
# calibration base pins the file holding its distance model (role
# "fg_distance"); the 2012 base pins this one.
FG_DISTANCE = ROOT / "library/data/2014_strength_calibration_v3.json"


class DriveModel:
    """The drive-model helpers bound to one calibration base."""

    def __init__(self, base):
        self.base = base
        data = base.raw("drive_model")
        errors = validate(data)
        if errors:
            raise ValueError("invalid drive model: " + "; ".join(errors))
        self.data = data
        self._fg_distance = None

    def load(self):
        """The validated artifact; treat as read-only."""
        return self.data

    def interior_probs(self):
        return _ratio(self.data["interior_counts"])

    def bucket(self, remaining_seconds):
        """The half-final pool key for the seconds left in the window."""
        data = self.data
        remaining = max(0, int(remaining_seconds))
        for low, high in data["bucket_edges"]:
            if remaining <= high:
                return data["bucket_pool"]["%d-%d" % (low, high)]
        low, high = data["bucket_edges"][-1]
        return data["bucket_pool"]["%d-%d" % (low, high)]

    def half_final_probs(self, pool_key):
        return _ratio(self.data["half_final_counts"][pool_key])

    def scaled_seconds(self, tuple_row):
        num, den = self.data["clock_scale"]
        return max(1, round(tuple_row[2] * num / den))

    def pool(self, kind, category, pool_key=None):
        pools = self.data["pools"]
        if kind == "interior":
            return pools["interior"].get(category, [])
        return pools["half_final"].get(pool_key, {}).get(category, [])

    def sample_tuple(self, rng, tuples, max_seconds=None):
        """Uniform draw from a category's tuples; None when the filter empties it."""
        if max_seconds is not None:
            tuples = [t for t in tuples if self.scaled_seconds(t) <= max_seconds]
        if not tuples:
            return None
        return tuples[rng.randrange(len(tuples))]

    def clock_tuple(self, rng, pool_key):
        """A clock tuple for an expiring window: that bucket's, else the nearest
        bucket that has one."""
        keys = list(self.data["half_final_counts"])
        order = [pool_key] + sorted((k for k in keys if k != pool_key),
                                    key=lambda k: abs(int(k.split("-")[0]) - int(pool_key.split("-")[0])))
        for key in order:
            tuples = self.pool("half_final", "clock", key)
            if tuples:
                return tuples[rng.randrange(len(tuples))]
        return [0, 0, 0]

    def fg_make_prob(self, distance):
        rates = self.data["rates"]
        for label, low, high in rates["fg_bin_edges"]:
            if distance <= high:
                made, attempts = rates["fg_by_distance"][label]
                return made / attempts
        made, attempts = rates["fg_by_distance"][rates["fg_bin_edges"][-1][0]]
        return made / attempts

    def fg_distance_model(self):
        if self._fg_distance is None:
            data = self.base.raw("fg_distance")["field_goal_distance"]
            bands = []
            for label, low, high in self.data["rates"]["fg_bin_edges"]:
                band = data["bands"][label]
                bands.append((label, low, high, band["intercept"]))
            self._fg_distance = {"slope": data["slope_per_yard"], "bands": bands}
        return self._fg_distance

    def fg_make_prob_at(self, distance):
        """The make probability at one distance under the distance model: the
        band's anchored intercept plus the pooled slope times the distance."""
        model = self.fg_distance_model()
        intercept = model["bands"][-1][3]
        for label, low, high, a in model["bands"]:
            if distance <= high:
                intercept = a
                break
        return 1.0 / (1.0 + math.exp(-(intercept + model["slope"] * distance)))

    def rate(self, name):
        made, attempts = self.data["rates"][name]
        return made / attempts

    def safety_free_kick_return_rate(self):
        returned, not_returned = self.data["rates"]["safety_free_kick_returned"]
        return returned / (returned + not_returned)

    def net_range(self, category):
        return tuple(self.data["net_range"][category])


# ---- the 2012 base's model (module-level API) -------------------------------------

def model():
    """The 2012 calibration base's drive model."""
    from .calibration_base import BASE_2012
    return BASE_2012.drive_model()


def _raw():
    from .calibration_base import BASE_2012
    return BASE_2012.raw("drive_model")


def load():
    """The validated 2012 artifact; treat as read-only."""
    return model().load()


def interior_probs():
    return model().interior_probs()


def bucket(remaining_seconds):
    return model().bucket(remaining_seconds)


def half_final_probs(pool_key):
    return model().half_final_probs(pool_key)


def scaled_seconds(tuple_row):
    return model().scaled_seconds(tuple_row)


def pool(kind, category, pool_key=None):
    return model().pool(kind, category, pool_key)


def sample_tuple(rng, tuples, max_seconds=None):
    return model().sample_tuple(rng, tuples, max_seconds)


def clock_tuple(rng, pool_key):
    return model().clock_tuple(rng, pool_key)


def fg_make_prob(distance):
    return model().fg_make_prob(distance)


def fg_distance_model():
    return model().fg_distance_model()


def fg_make_prob_at(distance):
    return model().fg_make_prob_at(distance)


def rate(name):
    return model().rate(name)


def safety_free_kick_return_rate():
    return model().safety_free_kick_return_rate()


def net_range(category):
    return model().net_range(category)
