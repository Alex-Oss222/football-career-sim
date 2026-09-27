"""The sourced 2012 field-position drive model used by kernel 2013.7.

The artifact (library/data/2012_nfl_field_position_model.json) is built by
scripts/research/build_2012_field_position_model.py from 2012 regular-season
play-by-play. It holds real drive tuples partitioned by game state (neutral
by start bin, first-half finals, late fourth-quarter cells by clock and
score, overtime), the per-(category, start bin) net-yard envelopes, and the
real transition records that turn one possession's end into the next one's
start (kickoffs, safety free kicks, punts, interceptions, fumbles lost).

Stateless: every draw takes the caller's possession RNG, so it stays on the
possession stream. Every rule is keyed only on the ball spot, the clock and
the score. Nothing here reads a club identity; every club uses this code.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path

from . import drive_model

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "library/data/2012_nfl_field_position_model.json"
SCHEMA = "2012-nfl-field-position-model-v1"
CATEGORIES = drive_model.CATEGORIES

TUPLE_FIELDS = (
    "plays", "net0", "seconds", "start", "end", "t0", "score_diff", "final",
    "term_bucket", "term_down", "term_ydstogo", "chains", "kneel_yards", "spikes",
    "fg_distance", "fg_made", "fg_blocked", "safety_term_kind", "safety_term_los",
    "runs", "attempts", "sacks", "td_kind",
)
T = {name: index for index, name in enumerate(TUPLE_FIELDS)}
FOURTH_DOWN_CATEGORIES = ("punt", "field_goal_attempt", "downs")
KEEP_END = ("field_goal_attempt", "punt", "downs", "interception", "fumble_lost")
H1_BUCKET_EDGES = ((0, 30), (31, 60), (61, 120), (121, 240), (241, 1800))
EXPECTED_DRIVES = 5984
KICK = {"touchback": 0, "next_start": 1, "kick_yards": 2, "return_yards": 3, "enforcement": 4, "outcome": 5}
PUNT = {"los": 0, "outcome": 1, "gross": 2, "return_yards": 3, "enforcement": 4, "next_start": 5, "touchback": 6}
TURNOVER = {"end": 0, "next_start": 1, "return_yards": 2, "touchback": 3, "delta": 4}


@lru_cache(maxsize=1)
def _raw():
    return json.loads(DATA.read_text())


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def validate(data=None):
    """Structural checks on the artifact; returns a list of errors."""
    data = data if data is not None else _raw()
    errors = []
    if data.get("schema") != SCHEMA:
        errors.append("field-position schema differs")
    if data.get("categories") != list(CATEGORIES):
        errors.append("field-position categories differ from the kernel categories")
    if data.get("tuple_fields") != list(TUPLE_FIELDS):
        errors.append("tuple fields differ from the runtime field list")
    pre = data.get("preregistration", {})
    bins = pre.get("start_bins", [])
    if [tuple(b) for b in bins] != [(90, 99), (81, 89), (80, 80), (70, 79), (60, 69), (50, 59),
                                    (40, 49), (30, 39), (20, 29), (1, 19)]:
        errors.append("start bins differ from the pre-registered list")
    if pre.get("min_cell") != 30 or pre.get("k_transition") != 20 or pre.get("fg_offsets") != [17, 18, 19]:
        errors.append("pre-registered constants differ")
    counts = data.get("neutral_counts", [])
    pools = data.get("pools", {})
    total = sum(sum(row) for row in counts)
    total += sum(sum(v.values()) for v in data.get("h1_final_counts", {}).values())
    total += sum(sum(v.values()) for v in data.get("late_counts", {}).values())
    total += sum(data.get("ot_counts", {}).values())
    if total != EXPECTED_DRIVES:
        errors.append("partition counts sum to %d, not 5,984" % total)
    missing = 0
    groups = [(counts[b][c], pools.get("neutral", [])[b][c]) for b in range(len(counts))
              for c in range(len(CATEGORIES))] if len(pools.get("neutral", [])) == len(counts) else []
    for name in ("h1_final", "late"):
        for key, cells in data.get(name + "_counts", {}).items():
            pool = pools.get(name, {}).get(key, {})
            groups += [(cells.get(c, 0), pool.get(c, [])) for c in CATEGORIES]
    groups += [(data.get("ot_counts", {}).get(c, 0), pools.get("ot", {}).get(c, [])) for c in CATEGORIES]
    for n, pool in groups:
        if not _is_int(n) or n < len(pool):
            errors.append("a pool holds more tuples than its count")
            break
        missing += n - len(pool)
        if any(len(t) != len(TUPLE_FIELDS) for t in pool):
            errors.append("a tuple has the wrong number of fields")
            break
    documented = data.get("corrections", {}).get("non_renderable", {})
    if missing != documented.get("safety", -1) + documented.get("touchdown", -1) + documented.get("zero_play_terminal", -1):
        errors.append("non-renderable drives differ from the documented corrections")
    cell_map = data.get("cell_map", {})
    for label in pre.get("late_time_buckets", {}):
        for need in pre.get("needs", {}):
            cell = cell_map.get("%s|%s" % (label, need))
            if cell is None or cell not in data.get("late_counts", {}):
                errors.append("cell map does not cover %s|%s" % (label, need))
    for cell, cells in data.get("late_counts", {}).items():
        if sum(cells.values()) < pre.get("min_cell", 30):
            errors.append("late cell %s under MIN_CELL" % cell)
    keymap = data.get("h1_final_keymap", {})
    if sorted(keymap) != sorted("%d-%d" % e for e in H1_BUCKET_EDGES) or any(
            v not in data.get("h1_final_counts", {}) for v in keymap.values()):
        errors.append("first-half final keymap incomplete")
    for pool in _all_tuples(data, "field_goal_attempt"):
        if pool[T["fg_distance"]] - pool[T["end"]] not in (17, 18, 19):
            errors.append("a field-goal tuple has a distance offset outside {17, 18, 19}")
            break
    for pool in _all_tuples(data, "touchdown"):
        if pool[T["net0"]] != pool[T["start"]] or pool[T["td_kind"]] not in ("pass", "rush"):
            errors.append("a touchdown tuple does not net its start or lacks a scoring kind")
            break
    for pool in _all_tuples(data, "safety"):
        if pool[T["safety_term_kind"]] not in ("sack", "run") or not _is_int(pool[T["safety_term_los"]]):
            errors.append("a safety tuple lacks its render terminal")
            break
    kick = data.get("kickoff_pool", [])
    if len(kick) != data.get("band_centres", {}).get("kickoff_touchback_share", [0, -1])[1] or not kick:
        errors.append("kickoff pool size differs from its band centre")
    for name in ("kickoff_pool", "free_kick_pool"):
        for record in data.get(name, []):
            if len(record) != len(KICK):
                errors.append("%s record malformed" % name)
                break
    for record in data.get("punt_pool", []):
        if len(record) != len(PUNT) or (not record[6] and record[5] != 100 - record[0] + record[2] - record[3] + record[4]):
            errors.append("punt record does not satisfy its published identity")
            break
    for name in ("interception_pool", "fumble_pool"):
        for record in data.get(name, []):
            if len(record) != len(TURNOVER) or record[4] != record[1] - (100 - record[0]):
                errors.append("%s record does not satisfy its published identity" % name)
                break
    if data.get("clock_scale") != drive_model.load()["clock_scale"]:
        errors.append("clock scale differs from the 2013.6 drive model")
    if data.get("reconciliation", {}).get("result") != "pass":
        errors.append("field-position reconciliation did not pass")
    if data.get("second_pass", {}).get("result") != "pass":
        errors.append("field-position second pass did not pass")
    return errors


def _all_tuples(data, category):
    pools = data.get("pools", {})
    for row in pools.get("neutral", []):
        index = CATEGORIES.index(category)
        yield from row[index] if index < len(row) else []
    for name in ("h1_final", "late"):
        for cell in pools.get(name, {}).values():
            yield from cell.get(category, [])
    yield from pools.get("ot", {}).get(category, [])


@lru_cache(maxsize=1)
def load():
    """The validated artifact; treat as read-only."""
    data = _raw()
    errors = validate(data)
    if errors:
        raise ValueError("invalid field-position model: " + "; ".join(errors))
    return data


# ---- keys ------------------------------------------------------------------------

def start_bin(spot):
    for index, (low, high) in enumerate(load()["preregistration"]["start_bins"]):
        if low <= spot <= high:
            return index
    raise ValueError("spot %s outside the field" % spot)


def zone(spot):
    for label, (low, high) in load()["preregistration"]["zones"].items():
        if low <= spot <= high:
            return label
    raise ValueError("spot %s outside the field" % spot)


def need(diff):
    for label, (low, high) in load()["preregistration"]["needs"].items():
        if low <= diff <= high:
            return label
    raise ValueError("score difference %s outside the need buckets" % diff)


def time_label(seconds):
    for label, (low, high) in load()["preregistration"]["late_time_buckets"].items():
        if low <= seconds <= high:
            return label
    raise ValueError("%s seconds is not a late window" % seconds)


def cell_for(half, window, diff):
    """'neutral', a late cell id, or 'OT'. OT trailing uses the <=120 trail 1-3
    cell (labelled inference: the trailing team must score)."""
    if half == "OT":
        return load()["cell_map"]["le120|trail1_3"] if diff < 0 else "OT"
    if half == 2 and window <= load()["preregistration"]["neutral_h2_seconds"]:
        return load()["cell_map"]["%s|%s" % (time_label(window), need(diff))]
    return "neutral"


def cell_need(cell):
    return cell.split("|", 1)[1] if "|" in cell else None


def terminal_bucket(q4_seconds):
    """Clock bucket of a fourth-quarter terminal snap (seconds left in Q4)."""
    if q4_seconds <= 120:
        return "le120"
    if q4_seconds <= 300:
        return "121-300"
    if q4_seconds <= 600:
        return "301-600"
    return "gt600"


def h1_bucket_index(seconds):
    seconds = max(0, int(seconds))
    return next((i for i, (_, high) in enumerate(H1_BUCKET_EDGES) if seconds <= high), len(H1_BUCKET_EDGES) - 1)


def h1_key(window):
    return load()["h1_final_keymap"]["%d-%d" % H1_BUCKET_EDGES[h1_bucket_index(window)]]


def decision_zone(los):
    for label, (low, high) in load()["preregistration"]["decision_zones"].items():
        if low <= los <= high:
            return label
    raise ValueError("line of scrimmage %s outside the field" % los)


def scaled_seconds(t):
    return drive_model.scaled_seconds(t)


# ---- one tuple replayed from a start spot ------------------------------------------

def adapt(category, t, spot):
    """(net, end) of 2012 tuple t replayed from start spot S."""
    if category == "touchdown":
        return spot, 0
    if category == "safety":
        return spot - 100, 100
    if category in KEEP_END:
        return spot - t[T["end"]], t[T["end"]]
    net = t[T["net0"]]
    return net, spot - net


def fixed_yardage(category, t):
    """(free snaps, kneel yards, terminal value, non-terminal sacks) of a tuple."""
    attempts, runs, sacks = t[T["attempts"]], t[T["runs"]], t[T["sacks"]]
    usable = attempts - (1 if category == "interception" else 0)
    terminal = 0
    if category == "safety":
        terminal = -(100 - t[T["safety_term_los"]])
        if t[T["safety_term_kind"]] == "sack":
            sacks -= 1
        else:
            runs -= 1
    return usable + runs, sum(t[T["kneel_yards"]]), terminal, sacks


def static_feasible(category, t, spot):
    """Spot-only feasibility (no clock): field, envelope and snap capacity."""
    net, end = adapt(category, t, spot)
    b = start_bin(spot)
    envelope = load()["envelopes"][category][b]
    if envelope is None:
        return False  # no 2012 drive of this category from this start bin
    if category not in ("touchdown", "safety"):
        if not 1 <= end <= 99 or not envelope[0] <= net <= envelope[1]:
            return False
    if category == "safety" and not envelope[0] <= net <= envelope[1]:
        return False
    if category == "touchdown" and t[T["td_kind"]] not in ("pass", "rush"):
        return False
    free, kneels, terminal, sacks = fixed_yardage(category, t)
    if t[T["kneel_yards"]] and not 1 <= end + kneels <= 99:
        return False  # kneels are the drive's last snaps: the spot before them must be in the field
    if free <= 0:
        # Only sacks can carry the yardage: their losses are fitted to the
        # net, so the required loss must be non-negative (exactly zero
        # without a sack). A touchdown always has its scoring snap.
        required = kneels + terminal - net
        if required < 0 or (sacks <= 0 and required != 0) or category == "touchdown":
            return False
    return True


# ---- pools ------------------------------------------------------------------------------

def _pool(pool_id, category):
    pools = load()["pools"]
    kind, key = pool_id
    if kind == "neutral":
        return pools["neutral"][key][CATEGORIES.index(category)]
    if kind == "ot":
        return pools["ot"][category]
    return pools[kind][key][category]


def _counts(pool_id):
    data = load()
    kind, key = pool_id
    if kind == "neutral":
        return dict(zip(CATEGORIES, data["neutral_counts"][key]))
    if kind == "ot":
        return data["ot_counts"]
    if kind == "late_union":
        out = {c: 0 for c in CATEGORIES}
        for cell in _need_cells(key):
            for c, n in data["late_counts"][cell].items():
                out[c] += n
        return out
    return data[kind + "_counts"][key]


def _need_cells(need_label):
    return sorted({cell for cell in load()["late_counts"] if cell_need(cell) == need_label})


@lru_cache(maxsize=None)
def _rungs(pool_id, category, spot):
    """Spot-feasible tuples of a pool at spot S, per ladder rung: (same bin,
    same zone). A neutral bin's list is its build-time ladder (thin bins add
    their nearest bins)."""
    data = load()
    b, z = start_bin(spot), zone(spot)
    kind, key = pool_id
    if kind == "neutral":
        ladder = data["neutral_ladder"][key][CATEGORIES.index(category)]
        same = [t for j in ladder for t in data["pools"]["neutral"][j][CATEGORIES.index(category)]]
        wider = [t for j in range(len(data["neutral_counts"])) if zone(data["preregistration"]["start_bins"][j][0]) == z
                 for t in data["pools"]["neutral"][j][CATEGORIES.index(category)]]
    else:
        if kind == "late_union":
            members = [t for cell in _need_cells(key) for t in data["pools"]["late"][cell][category]]
        else:
            members = list(_pool(pool_id, category))
        same = [t for t in members if start_bin(t[T["start"]]) == b]
        wider = [t for t in members if zone(t[T["start"]]) == z]
    return tuple(tuple(t for t in rung if static_feasible(category, t, spot)) for rung in (same, wider))


def _static(pool_id, category, spot):
    """The first rung with a spot-feasible tuple (no clock filter); () when none."""
    for rung in _rungs(pool_id, category, spot):
        if rung:
            return rung
    return ()


def _dynamic(tuples, category, regime, window):
    """Clock filters of the regime (see the module docstring and README)."""
    if regime == "h1_neutral" or regime == "h1_final":
        return tuples
    if regime == "h2_neutral":
        return tuple(t for t in tuples if scaled_seconds(t) < window)
    out = []
    bucket = h1_bucket_index(window)
    for t in tuples:
        if t[T["final"]]:
            if h1_bucket_index(t[T["t0"]]) != bucket:
                continue
            left = 0
        else:
            seconds = scaled_seconds(t)
            if seconds >= window:
                continue
            left = window - seconds
        if regime == "late" and category in FOURTH_DOWN_CATEGORIES and terminal_bucket(left) != t[T["term_bucket"]]:
            continue
        out.append(t)
    return tuple(out)


def eligible(pool_id, category, spot, regime, window):
    """Tuples feasible at the spot and the clock, by the ladder: the same-bin
    rung if any of its tuples is feasible, else the same-zone rung; () masks
    the category. The ladder steps on full feasibility (spot and clock), so a
    same-bin rung whose tuples all fail the clock filter never masks a
    category that the same zone can still supply."""
    for rung in _rungs(pool_id, category, spot):
        feasible = _dynamic(rung, category, regime, window)
        if feasible:
            return feasible
    return ()


def category_mix(counts, edge, eligible_by_category):
    """The raw 2012 cell mix after the unchanged apply_edge, then masked: a
    category with no 2012 drive in the cell, or no feasible tuple, is removed
    and the rest renormalised (apply_edge would otherwise put +/-edge mass on
    zero-count touchdown or punt categories)."""
    total = sum(counts.values())
    if not total:
        return {}
    probs = drive_model.apply_edge({c: counts.get(c, 0) / total for c in CATEGORIES}, edge)
    masked = {c: (p if counts.get(c, 0) > 0 and eligible_by_category.get(c) else 0.0) for c, p in probs.items()}
    mass = sum(masked.values())
    return {c: v / mass for c, v in masked.items()} if mass > 0 else {}


@dataclass(frozen=True)
class Drive:
    category: str
    tuple: tuple
    seconds: int
    consumes_window: bool
    cell: str
    regime: str
    fallback: str | None = None
    redirected: bool = False


ZERO_TUPLE = (0, 0, 0, 0, 0, 0, 0, 1, "gt600", None, None, [0, 0, 0, 0, 0, 0], [], 0,
              None, None, None, None, None, 0, 0, 0, None)


def draw_options(pool_id, regime, spot, window):
    """(counts, eligible tuples by category) for one draw from one pool."""
    counts = _counts(pool_id)
    options = {c: eligible(pool_id, c, spot, regime, window) for c in CATEGORIES if counts.get(c, 0)}
    return counts, options


def _draw_from(rng, pool_id, regime, spot, window, edge):
    counts, options = draw_options(pool_id, regime, spot, window)
    probs = category_mix(counts, edge, options)
    if not probs:
        return None
    category = drive_model.draw_category(rng, probs)
    pool = options[category]
    return category, pool[rng.randrange(len(pool))]


def _clock_fallback(rng, tuples, spot, window):
    """A final clock tuple feasible at the spot whose start bucket is nearest
    the window's (2013.6 edges); None when there is none."""
    bucket = h1_bucket_index(window)
    by_distance = {}
    for t in tuples:
        if t[T["final"]] and static_feasible("clock", t, spot):
            by_distance.setdefault(abs(h1_bucket_index(t[T["t0"]]) - bucket), []).append(t)
    if not by_distance:
        return None
    pool = by_distance[min(by_distance)]
    return pool[rng.randrange(len(pool))]


def _late_clock_tuples(need_label):
    return [t for cell in _need_cells(need_label) for t in load()["pools"]["late"][cell]["clock"]]


def _h1_clock_tuples():
    return [t for cells in load()["pools"]["h1_final"].values() for t in cells["clock"]]


def draw_drive(rng, spot, half, window, diff, edge, diagnostics):
    """One possession: a category from the state's 2012 mix, then a real drive
    of that category feasible from the start spot. Draws: one random for the
    category and one randrange for the tuple (again for an H1 redirect)."""
    cell = cell_for(half, window, diff)
    if half == "OT" and diff > 0:
        diagnostics["ot_leading_offense"] = diagnostics.get("ot_leading_offense", 0) + 1
    if half == 1:
        drawn = _draw_from(rng, ("neutral", start_bin(spot)), "h1_neutral", spot, window, edge)
        if drawn is not None:
            category, t = drawn
            seconds = scaled_seconds(t)
            if category != "clock" and seconds < window:
                return Drive(category, t, seconds, False, cell, "h1_neutral")
        diagnostics["interior_clock_redirected"] = diagnostics.get("interior_clock_redirected", 0) + 1
        drawn = _draw_from(rng, ("h1_final", h1_key(window)), "h1_final", spot, window, edge)
        if drawn is not None:
            return Drive(drawn[0], drawn[1], window, True, cell, "h1_final", redirected=True)
        t = _clock_fallback(rng, _h1_clock_tuples(), spot, window)
        if t is not None:
            diagnostics["fallback_clock_tuple"] = diagnostics.get("fallback_clock_tuple", 0) + 1
            return Drive("clock", t, window, True, cell, "h1_final", fallback="clock_tuple", redirected=True)
        diagnostics["fallback_zero_tuple"] = diagnostics.get("fallback_zero_tuple", 0) + 1
        return Drive("clock", ZERO_TUPLE, window, True, cell, "h1_final", fallback="zero")
    if cell == "neutral":
        drawn = _draw_from(rng, ("neutral", start_bin(spot)), "h2_neutral", spot, window, edge)
        if drawn is not None:
            seconds = scaled_seconds(drawn[1])
            if window - seconds <= load()["preregistration"]["neutral_h2_seconds"]:
                diagnostics["h2_neutral_into_late"] = diagnostics.get("h2_neutral_into_late", 0) + 1
            return Drive(drawn[0], drawn[1], seconds, False, cell, "h2_neutral")
        need_label = need(diff)
        regime, pool_id = "late", ("late_union", need_label)
    elif cell == "OT":
        regime, pool_id, need_label = "ot", ("ot", None), "tied"
    else:
        regime, pool_id, need_label = ("late" if half == 2 else "ot"), ("late", cell), cell_need(cell)
    drawn = _draw_from(rng, pool_id, regime, spot, window, edge)
    fallback = None
    if drawn is None and pool_id[0] != "late_union":
        fallback = "need_union"
        diagnostics["fallback_need_union"] = diagnostics.get("fallback_need_union", 0) + 1
        drawn = _draw_from(rng, ("late_union", need_label), regime, spot, window, edge)
    if drawn is None:
        t = _clock_fallback(rng, _late_clock_tuples(need_label), spot, window)
        if t is not None:
            diagnostics["fallback_clock_tuple"] = diagnostics.get("fallback_clock_tuple", 0) + 1
            return Drive("clock", t, window, True, cell, regime, fallback="clock_tuple")
        diagnostics["fallback_zero_tuple"] = diagnostics.get("fallback_zero_tuple", 0) + 1
        return Drive("clock", ZERO_TUPLE, window, True, cell, regime, fallback="zero")
    category, t = drawn
    if t[T["final"]]:
        return Drive(category, t, window, True, cell, regime, fallback=fallback)
    return Drive(category, t, scaled_seconds(t), False, cell, regime, fallback=fallback)


# ---- transitions -------------------------------------------------------------------------

def _kick_record(rng, pool, spot):
    record = pool[rng.randrange(len(pool))]
    touchback, next_start, kick, ret, enforcement, outcome = record
    return {"touchback": bool(touchback), "next_start": next_start, "kick_yards": kick,
            "return_yards": 0 if touchback else ret, "enforcement": enforcement,
            "outcome": outcome, "kick_spot": spot}


def kickoff(rng):
    """A real 2012 own-35 kickoff: one randrange over the pool."""
    return _kick_record(rng, load()["kickoff_pool"], 35)


def free_kick(rng):
    """A real 2012 safety free kick from the 20: one randrange over 13."""
    return _kick_record(rng, load()["free_kick_pool"], 20)


def _nearest(pool, key_index, spot, ok):
    """The K feasible records nearest the spot, with every record tied at the
    K-th distance included (pool sorted by the key; season order within a
    key). Including the tied boundary keeps the draw from favouring a fixed
    subset of records at a crowded line of scrimmage."""
    import bisect
    keys = [record[key_index] for record in pool]
    right = bisect.bisect_left(keys, spot)
    left = right - 1
    out = []
    limit = load()["preregistration"]["k_transition"]
    cutoff = None
    while left >= 0 or right < len(pool):
        take_left = right >= len(pool) or (left >= 0 and spot - keys[left] <= keys[right] - spot)
        index = left if take_left else right
        distance = abs(keys[index] - spot)
        if cutoff is not None and distance > cutoff:
            break
        if take_left:
            left -= 1
        else:
            right += 1
        if ok(pool[index]):
            out.append((distance, index))
            if len(out) == limit:
                cutoff = distance
    out.sort()
    return [pool[index] for _, index in out]


def punt(rng, los):
    """A real 2012 punt drawn from the 20 feasible records nearest the line of
    scrimmage (ties by index). A touchback publishes gross = LOS and a start
    of 80 + enforcement; otherwise start = 100 - LOS + gross - return + e."""
    def ok(record):
        if record[PUNT["touchback"]]:
            return los <= record[PUNT["los"]]
        start = 100 - los + record[PUNT["gross"]] - record[PUNT["return_yards"]] + record[PUNT["enforcement"]]
        return 1 <= start <= 99
    candidates = _nearest(load()["punt_pool"], PUNT["los"], los, ok)
    record = candidates[rng.randrange(len(candidates))]
    touchback = bool(record[PUNT["touchback"]])
    gross = los if touchback else record[PUNT["gross"]]
    ret = 0 if touchback else record[PUNT["return_yards"]]
    enforcement = record[PUNT["enforcement"]]
    start = 80 + enforcement if touchback else 100 - los + gross - ret + enforcement
    return {"los": los, "outcome": record[PUNT["outcome"]], "gross": gross, "return_yards": ret,
            "enforcement": enforcement, "next_start": start, "touchback": touchback,
            "record_los": record[PUNT["los"]]}


def turnover(rng, kind, end):
    """A real 2012 interception or fumble-lost transition from the 20 feasible
    records nearest the turnover spot: start = 100 - end + delta, or 80 + e
    for a touchback."""
    pool = load()["interception_pool" if kind == "interception" else "fumble_pool"]

    def start_of(record):
        if record[TURNOVER["touchback"]]:
            return record[TURNOVER["next_start"]]
        return 100 - end + record[TURNOVER["delta"]]
    candidates = _nearest(pool, TURNOVER["end"], end, lambda r: 1 <= start_of(r) <= 99)
    record = candidates[rng.randrange(len(candidates))]
    touchback = bool(record[TURNOVER["touchback"]])
    start = start_of(record)
    return {"end": end, "next_start": start, "return_yards": record[TURNOVER["return_yards"]],
            "touchback": touchback, "enforcement": (start - 80) if touchback else 0,
            "delta": record[TURNOVER["delta"]], "record_end": record[TURNOVER["end"]]}


def downs_start(end):
    return 100 - end


def missed_fg_start(distance):
    return min(80, 110 - distance)
