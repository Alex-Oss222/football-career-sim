"""The sourced 2012 field-position drive model used by kernels 2013.7-2013.8.

The artifact (library/data/2012_nfl_field_position_model.json) is built by
scripts/research/build_2012_field_position_model.py from 2012 regular-season
play-by-play. It holds real drive tuples partitioned by game state (neutral
by start bin, first-half finals, late fourth-quarter cells by clock and
score, overtime), the per-(category, start bin) net-yard envelopes, and the
real transition records that turn one possession's end into the next one's
start (kickoffs, safety free kicks, punts, interceptions, fumbles lost).

Stateless: every draw takes the caller's possession RNG, so it stays on the
possession stream. Every rule is keyed only on the ball spot, the clock, the
score and (kernel 2014.1) the two clubs' charged timeouts. Nothing here reads
a club identity; every club uses this code.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path

from . import chains
from . import drive_model
from .rules import RULES

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "library/data/2012_nfl_field_position_model.json"
SCHEMA = "2012-nfl-field-position-model-v2"
CATEGORIES = drive_model.CATEGORIES

TUPLE_FIELDS = (
    "plays", "net0", "seconds", "start", "end", "t0", "score_diff", "final",
    "term_bucket", "term_down", "term_ydstogo", "chains", "kneel_yards", "spikes",
    "fg_distance", "fg_made", "fg_blocked", "safety_term_kind", "safety_term_los",
    "runs", "attempts", "sacks", "td_kind",
    "off_timeouts", "def_timeouts", "off_timeouts_used", "def_timeouts_used",
)
T = {name: index for index, name in enumerate(TUPLE_FIELDS)}
FOURTH_DOWN_CATEGORIES = ("punt", "field_goal_attempt", "downs")
KEEP_END = ("field_goal_attempt", "punt", "downs", "interception", "fumble_lost")
H1_BUCKET_EDGES = ((0, 30), (31, 60), (61, 120), (121, 240), (241, 1800))
# Kernel 2014.1: late, first-half-final and overtime draws are conditioned on
# the clubs' charged timeouts. A ladder level is used when its matching tuples
# in the pool number at least MIN_TIMEOUT_POOL (the pre-registered min_cell).
TIMEOUT_REGIMES = ("h1_final", "late", "ot")
MIN_TIMEOUT_POOL = 30
TIMEOUT_BANDS = ((0,), (1, 2), (3,))
# Kernel 2014.2 late-game recalibration (switches kept for the documented
# before/after comparison; both are on in the kernel):
# - ZONE_CONDITIONING: a conditioned draw's category weights are multiplied by
#   P(start zone | category) / P(start zone), estimated with add-one smoothing
#   over the need's union of late cells (every first-half final; the
#   overtime pool), so the mix reflects where the drive starts;
# - NEED_UNION_RUNGS: a late cell with no feasible drive of a category takes
#   one from the need's other time buckets (same bin, same zone, then any
#   start feasible at the spot), under the same clock filters, instead of
#   masking the category.
ZONE_CONDITIONING = True
NEED_UNION_RUNGS = True
ZONE_SMOOTHING = 1.0
# Kernel 2014.4: the pre-registered clock-expiry allowance E (seconds). A
# 2012 drive may end a half, game or overtime window only when it is time
# feasible there: its own scaled seconds s satisfy s <= window <= s + E, so
# the window's last E seconds or fewer can run off after its final snap.
# E is the 2013 play clock (RULES.play_clock_seconds, 40 s; sourced in
# library/2013_nfl_playing_rules_for_simulation.md): once the last play is
# over, a running clock can bleed at most one play clock before the offence
# must snap again. It was fixed from the rule before any sample was run and
# is not a tuning parameter. A drive is never stretched over more time.
CLOCK_EXPIRY_ALLOWANCE = RULES.play_clock_seconds
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
    if t[T["kneel_yards"]] and zone(t[T["start"]]) != zone(spot):
        return False  # kernel 2014.1: a kneel drive replays only from its own start zone
    if free <= 0:
        # Only sacks can carry the yardage: their losses are fitted to the
        # net, so the required loss must be non-negative (exactly zero
        # without a sack). A touchdown always has its scoring snap.
        required = kneels + terminal - net
        if required < 0 or (sacks <= 0 and required != 0) or category == "touchdown":
            return False
    # Kernel 2014.4 (defect register item 3): the relocated snaps must admit a
    # legal chain walk ending in the category's terminal state (a punt on 4th
    # down, a downs failure on 4th, ...); see runtime.chains.chain_feasible.
    if t is not ZERO_TUPLE and not chains.chain_feasible(
            category, plays=t[T["plays"]], net=net, spot=spot, kneel_yards=t[T["kneel_yards"]],
            sacks=t[T["sacks"]], runs=t[T["runs"]], terminal_value=terminal):
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


def ends_window(regime, category, t):
    """True when a tuple replays as the drive that runs out the window.

    In regulation a "final" 2012 drive was the last of its half or game, so it
    ran out the clock. In overtime (kernel 2013.8) a 2012 drive was also
    "final" when its score ended the game (a walk-off touchdown or field
    goal); that is not the period expiring. Under the 2013 overtime rule only
    a clock-expired drive ends the period, so in the "ot" regime every other
    tuple replays with its own scaled seconds and must fit the window."""
    if not t[T["final"]]:
        return False
    return regime != "ot" or category == "clock"


def time_feasible(t, window):
    """Kernel 2014.4: can tuple t end a window of `window` seconds? Its own
    scaled seconds must fit (s <= window) and leave no more than the
    clock-expiry allowance to run off after its last snap (window <= s + E)."""
    own = own_seconds(t)
    return own <= window <= own + CLOCK_EXPIRY_ALLOWANCE


def own_seconds(t):
    """A tuple's own elapsed seconds (ZERO_TUPLE, a zero-play clock expiry: 0)."""
    return 0 if t is ZERO_TUPLE else scaled_seconds(t)


@lru_cache(maxsize=1)
def snap_seconds_range():
    """Kernel 2014.4: {scrimmage snaps: (fewest, most) own scaled seconds}
    over every real 2012 drive in the artifact's pools (5,977 drives with a
    snap; e.g. 1 snap 1-48 s, 7 snaps 48-384 s). A zero-play possession may
    also take 0 s (the zero-play clock expiry). Derived from the 2012 data
    alone, never from a kernel sample; the coherence class
    seconds_per_snap_outside compares a drive's own seconds with it."""
    out = {0: (0, 0)}
    for category in CATEGORIES:
        for t in _all_tuples(load(), category):
            n, s = t[T["plays"]], scaled_seconds(t)
            low, high = out.get(n, (s, s))
            out[n] = (min(low, s), max(high, s))
    return out


def _dynamic(tuples, category, regime, window):
    """Clock filters of the regime (see the module docstring and README).

    Kernel 2014.4: a tuple that ends the window (every first-half final; a
    late final; an overtime clock final) must be time feasible
    (time_feasible), replacing the 2013.6 start-bucket match, which let a
    90-second drive stand for a 9:20 window. Any other tuple must finish
    inside the window (s < window)."""
    if regime == "h1_neutral":
        return tuples
    if regime == "h1_final":
        return tuple(t for t in tuples if time_feasible(t, window))
    if regime == "h2_neutral":
        return tuple(t for t in tuples if scaled_seconds(t) < window)
    out = []
    for t in tuples:
        if ends_window(regime, category, t):
            if not time_feasible(t, window):
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
    if NEED_UNION_RUNGS and regime == "late" and pool_id[0] == "late":
        # Kernel 2014.2: a late cell with no feasible drive of the category
        # borrows the same need's other time buckets (same bin, then same
        # zone), under the same clock filters.
        union = ("late_union", cell_need(pool_id[1]))
        for rung in _rungs(union, category, spot):
            feasible = _dynamic(rung, category, regime, window)
            if feasible:
                return feasible
        # Last rung: any real drive of the category and need, whatever its
        # start, that is feasible at this spot (end in the field, net inside
        # the current start bin's 2012 envelope) and at this clock.
        feasible = _dynamic(_any_start(union, category, spot), category, regime, window)
        if feasible:
            return feasible
    return ()


@lru_cache(maxsize=None)
def _any_start(pool_id, category, spot):
    return tuple(t for t in _members(pool_id, category) if static_feasible(category, t, spot))


def category_mix(counts, edge, eligible_by_category, int_edge=0.0):
    """The raw 2012 cell mix after the unchanged apply_edge, then masked: a
    category with no 2012 drive in the cell, or no feasible tuple, is removed
    and the rest renormalised (apply_edge would otherwise put +/-edge mass on
    zero-count touchdown or punt categories).

    Kernel 2014.4 phase 2: `int_edge` (the interception-share shift from the
    coverage-against-passing terms) moves that mass from the punt category
    to the interception category before masking; zero leaves the mix exactly
    as apply_edge returned it."""
    total = sum(counts.values())
    if not total:
        return {}
    probs = drive_model.apply_edge({c: counts.get(c, 0) / total for c in CATEGORIES}, edge)
    if int_edge:
        probs = dict(probs)
        probs["interception"] = max(0.0, probs.get("interception", 0.0) + int_edge)
        probs["punt"] = max(0.0, probs.get("punt", 0.0) - int_edge)
        mass = sum(probs.values())
        probs = {c: v / mass for c, v in probs.items()}
    masked = {c: (p if counts.get(c, 0) > 0 and eligible_by_category.get(c) else 0.0) for c, p in probs.items()}
    mass = sum(masked.values())
    return {c: v / mass for c, v in masked.items()} if mass > 0 else {}


@dataclass(frozen=True)
class Drive:
    """One drawn possession. `seconds` is the window time it uses: its own
    scaled seconds, or for a window-ending drive the whole remaining window.
    Kernel 2014.4: `own_seconds` is the tuple's own scaled seconds (0 for a
    zero-play clock expiry) and `expiry_seconds` = seconds - own_seconds is
    the clock-running-out leg after its last snap (0 unless it ends the
    window; at most CLOCK_EXPIRY_ALLOWANCE for a time-feasible drive). Left
    unset, own_seconds is the tuple's own seconds capped at `seconds`."""
    category: str
    tuple: tuple
    seconds: int
    consumes_window: bool
    cell: str
    regime: str
    fallback: str | None = None
    redirected: bool = False
    timeout_level: int | None = None
    own_seconds: int | None = None
    # Kernel 2014.4 phase 2: the pool and clock regime the tuple was drawn
    # from, so a drive whose snaps admit no legal chain layout can be
    # resampled from the same category and start-spot rung (resample_drive).
    pool_id: tuple | None = None
    clock_regime: str | None = None

    def __post_init__(self):
        if self.own_seconds is None:
            own = min(own_seconds(self.tuple), self.seconds) if self.consumes_window else self.seconds
            object.__setattr__(self, "own_seconds", own)

    @property
    def expiry_seconds(self):
        return self.seconds - self.own_seconds


ZERO_TUPLE = (0, 0, 0, 0, 0, 0, 0, 1, "gt600", None, None, [0, 0, 0, 0, 0, 0], [], 0,
              None, None, None, None, None, 0, 0, 0, None, None, None, 0, 0)


def draw_options(pool_id, regime, spot, window):
    """(counts, eligible tuples by category) for one draw from one pool."""
    counts = _counts(pool_id)
    options = {c: eligible(pool_id, c, spot, regime, window) for c in CATEGORIES if counts.get(c, 0)}
    return counts, options


def _band(n):
    return next(i for i, band in enumerate(TIMEOUT_BANDS) if n in band)


def timeout_match(level, t, timeouts, key):
    """Kernel 2014.1 ladder: does tuple t match the clubs' charged timeouts?

    Level 0: both clubs' counts equal the tuple's; level 1: the clock-stopping
    side's count (the offense when it trails, otherwise the defense) equals the
    tuple's; level 2: that side's count is in the same band (0, 1-2, 3);
    level 3: unconditioned."""
    if level >= 3:
        return True
    off, dfn = t[T["off_timeouts"]], t[T["def_timeouts"]]
    if off is None or dfn is None:
        return False
    if level == 0:
        return (off, dfn) == tuple(timeouts)
    mine, now = (off, timeouts[0]) if key == "off" else (dfn, timeouts[1])
    return mine == now if level == 1 else _band(mine) == _band(now)


def _members(pool_id, category):
    """Every tuple of a pool's category, before spot and clock feasibility."""
    kind, key = pool_id
    if kind == "late_union":
        return [t for cell in _need_cells(key) for t in load()["pools"]["late"][cell][category]]
    return list(_pool(pool_id, category))


def _timeout_options(pool_id, counts, options, timeouts, key, diagnostics):
    """(weights, options) conditioned on the charged timeouts by the ladder.

    A level is used when the pool holds at least MIN_TIMEOUT_POOL matching
    tuples and at least one matching tuple is feasible here; the category
    weight is its 2012 cell count times the share of its tuples that match
    (P(category | cell, timeouts) up to a constant)."""
    members = {c: _members(pool_id, c) for c in counts if counts.get(c, 0)}
    for level in range(3):
        matching = {c: [t for t in m if timeout_match(level, t, timeouts, key)] for c, m in members.items()}
        if sum(len(m) for m in matching.values()) < MIN_TIMEOUT_POOL:
            continue
        weights, narrowed = {}, {}
        for c, m in matching.items():
            if not members[c]:
                continue
            weights[c] = counts[c] * len(m) / len(members[c])
            feasible = options.get(c, ())
            # Within a category, prefer the matching feasible tuples; when the
            # spot and clock leave none, keep the category's feasible set so
            # the timeout filter never masks a category (masking is spot and
            # clock feasibility only, as in 2013.x).
            narrowed[c] = tuple(t for t in feasible if timeout_match(level, t, timeouts, key)) or feasible
            if feasible and narrowed[c] is feasible and diagnostics is not None:
                diagnostics["timeout_tuple_widened"] = diagnostics.get("timeout_tuple_widened", 0) + 1
        if any(weights.get(c) and narrowed.get(c) for c in weights):
            if diagnostics is not None:
                diagnostics["timeout_level_%d" % level] = diagnostics.get("timeout_level_%d" % level, 0) + 1
            return weights, narrowed, level
    if diagnostics is not None:
        diagnostics["timeout_level_3"] = diagnostics.get("timeout_level_3", 0) + 1
    return counts, options, 3


def _reference(pool_id):
    """The larger pool whose start zones estimate P(zone | category) for a
    conditioned draw: the need's union of late cells, every first-half final,
    or the overtime pool."""
    kind, key = pool_id
    if kind == "late":
        return ("late_union", cell_need(key))
    if kind == "h1_final":
        return ("h1_final_all", None)
    return pool_id


@lru_cache(maxsize=None)
def zone_likelihood(reference, spot_zone):
    """{category: P(zone | category) / P(zone)} over the reference pool, with
    add-one smoothing over the three zones."""
    data = load()
    kind, key = reference
    def members(c):
        if kind == "h1_final_all":
            return [t for cells in data["pools"]["h1_final"].values() for t in cells[c]]
        return _members(reference, c)
    by_cat = {c: members(c) for c in CATEGORIES}
    a = ZONE_SMOOTHING
    total = sum(len(m) for m in by_cat.values())
    in_zone = sum(1 for m in by_cat.values() for t in m if zone(t[T["start"]]) == spot_zone)
    base = (in_zone + a) / (total + 3 * a)
    out = {}
    for c, m in by_cat.items():
        n_zone = sum(1 for t in m if zone(t[T["start"]]) == spot_zone)
        out[c] = ((n_zone + a) / (len(m) + 3 * a)) / base
    return out


def sack_rate_base():
    """The 2012 sacks per dropback the phase-2 sack shift is measured from."""
    made, n = load()["band_centres"]["sacks_per_dropback"]
    return made / n


SACK_PROB_FLOOR, SACK_PROB_CEILING = 0.005, 0.5


def tuple_weights(pool, sack_shift):
    """Kernel 2014.4 phase 2: each real drive's binomial likelihood ratio
    when the per-dropback sack probability moves from the 2012 base p0 to
    p1 = p0 + shift: (p1/p0)^sacks x ((1-p1)/(1-p0))^attempts (attempts =
    dropbacks - sacks). Identical for every club; a zero shift is never
    routed here."""
    p0 = sack_rate_base()
    p1 = min(SACK_PROB_CEILING, max(SACK_PROB_FLOOR, p0 + sack_shift))
    ratio_sack, ratio_none = p1 / p0, (1 - p1) / (1 - p0)
    return [ratio_sack ** int(t[T["sacks"]] or 0) * ratio_none ** int(t[T["attempts"]] or 0) for t in pool]


def draw_tuple(rng, pool, sack_shift=0.0):
    """One tuple from the pool: uniform (one randrange, as every earlier
    kernel) with no sack shift; otherwise weighted by tuple_weights (one
    random)."""
    if not sack_shift:
        return pool[rng.randrange(len(pool))]
    weights = tuple_weights(pool, sack_shift)
    target = rng.random() * sum(weights)
    cumulative = 0.0
    for t, w in zip(pool, weights):
        cumulative += w
        if target < cumulative:
            return t
    return pool[-1]


def _draw_from(rng, pool_id, regime, spot, window, edge, timeouts=None, key="def", diagnostics=None,
               exclude=(), clock_regime=None, extra=None):
    counts, options = draw_options(pool_id, clock_regime or regime, spot, window)
    # Kernel 2014.4: `exclude` masks categories (the fit draws mask clock,
    # which cannot run out a window it does not reach); `clock_regime`
    # applies another regime's clock filters (a late fit drive keeps the
    # late terminal-bucket rule) without its conditioning.
    options = {c: (() if c in exclude else v) for c, v in options.items()}
    if ZONE_CONDITIONING and regime in TIMEOUT_REGIMES:
        ratio = zone_likelihood(_reference(pool_id), zone(spot))
        counts = {c: n * ratio[c] for c, n in counts.items()}
    level = None
    if timeouts is not None and regime in TIMEOUT_REGIMES:
        counts, options, level = _timeout_options(pool_id, counts, options, timeouts, key, diagnostics)
    extra = extra or {}
    probs = category_mix(counts, edge, options, extra.get("int", 0.0))
    if not probs:
        return None
    category = drive_model.draw_category(rng, probs)
    pool = options[category]
    return category, draw_tuple(rng, pool, extra.get("sack", 0.0)), level


def _clock_fallback(rng, tuples, spot, window):
    """A final clock tuple feasible at the spot, and (kernel 2014.4) time
    feasible for the window, whose start bucket is nearest the window's
    (2013.6 edges); None when there is none."""
    bucket = h1_bucket_index(window)
    by_distance = {}
    for t in tuples:
        if t[T["final"]] and static_feasible("clock", t, spot) and time_feasible(t, window):
            by_distance.setdefault(abs(h1_bucket_index(t[T["t0"]]) - bucket), []).append(t)
    if not by_distance:
        return None
    pool = by_distance[min(by_distance)]
    return pool[rng.randrange(len(pool))]


def _late_clock_tuples(need_label):
    return [t for cell in _need_cells(need_label) for t in load()["pools"]["late"][cell]["clock"]]


def _h1_clock_tuples():
    return [t for cells in load()["pools"]["h1_final"].values() for t in cells["clock"]]


def _bump(diagnostics, name):
    diagnostics[name] = diagnostics.get(name, 0) + 1


def ending_drive(category, t, window, cell, regime, **kw):
    """Kernel 2014.4: a drive that ends the window. It uses the whole window
    (the kernel's half invariants), keeps its own seconds and publishes the
    rest as its clock-expiry leg."""
    return Drive(category, t, window, True, cell, regime, own_seconds=min(own_seconds(t), window), **kw)


def _fit_or_expire(rng, spot, window, edge, cell, regime, diagnostics, fit_regime, fit_counter, extra=None):
    """Kernel 2014.4: nothing time feasible can end the window. Draw a real
    drive from the start bin that fits inside it (not a clock drive; the
    window then continues with the next possession) under the regime's own
    clock filters (in a late cell a fourth-down drive must also end in its
    2012 terminal clock bucket; no non-clock drive ends an overtime period
    or a first-half fit). Only when no such drive
    exists and the window is within the clock-expiry allowance does a
    zero-play clock expiry end it. The last rung, a zero-play possession over
    a longer window, would stretch the clock: it is counted
    (fallback_zero_tuple) and publishes an expiry leg beyond the allowance,
    which the coherence audit flags."""
    clock_regime = "h2_neutral" if regime == "h1_final" else regime
    drawn = _draw_from(rng, ("neutral", start_bin(spot)), "h2_neutral", spot, window, edge, exclude=("clock",),
                       clock_regime=clock_regime, extra=extra)
    if drawn is not None:
        _bump(diagnostics, fit_counter)
        return Drive(drawn[0], drawn[1], scaled_seconds(drawn[1]), False, cell, fit_regime,
                     fallback="h1_fit" if fit_counter == "h1_fit_fallback" else "fit",
                     pool_id=("neutral", start_bin(spot)), clock_regime=clock_regime)
    if window <= CLOCK_EXPIRY_ALLOWANCE:
        _bump(diagnostics, "clock_expiry_zero")
        return ending_drive("clock", ZERO_TUPLE, window, cell, regime, fallback="expiry")
    _bump(diagnostics, "fallback_zero_tuple")
    return ending_drive("clock", ZERO_TUPLE, window, cell, regime, fallback="zero")


def draw_drive(rng, spot, half, window, diff, edge, diagnostics, timeouts=None, extra=None):
    """One possession: a category from the state's 2012 mix, then a real drive
    of that category feasible from the start spot. Draws: one random for the
    category and one randrange for the tuple (again for an H1 redirect).

    Kernel 2014.1: `timeouts` is (offense, defense) charged timeouts left.
    First-half-final, late and overtime draws are conditioned on them
    (timeout_match); None leaves them unconditioned.

    Kernel 2014.4: a window-ending drive is always time feasible
    (time_feasible); when none is, a drive that fits inside the window is
    drawn instead (_fit_or_expire) and the window continues.

    Kernel 2014.4 phase 2: `extra` carries the interception-share shift
    ("int") and the sack-probability shift ("sack") of the matchup; None or
    zeros reproduce the earlier draw exactly."""
    cell = cell_for(half, window, diff)
    key = "off" if diff < 0 else "def"
    if half == "OT" and diff > 0:
        diagnostics["ot_leading_offense"] = diagnostics.get("ot_leading_offense", 0) + 1
    if half == 1:
        drawn = _draw_from(rng, ("neutral", start_bin(spot)), "h1_neutral", spot, window, edge, extra=extra)
        if drawn is not None:
            category, t, _ = drawn
            seconds = scaled_seconds(t)
            if category != "clock" and seconds < window:
                return Drive(category, t, seconds, False, cell, "h1_neutral",
                             pool_id=("neutral", start_bin(spot)), clock_regime="h1_neutral")
        diagnostics["interior_clock_redirected"] = diagnostics.get("interior_clock_redirected", 0) + 1
        # Kernel 2014.4: the redirect reaches only time-feasible finals
        # (_dynamic); the draw returns None, consuming nothing, when the
        # window's pool has none (every window over about 160 s).
        drawn = _draw_from(rng, ("h1_final", h1_key(window)), "h1_final", spot, window, edge,
                           timeouts, key, diagnostics, extra=extra)
        if drawn is not None:
            return ending_drive(drawn[0], drawn[1], window, cell, "h1_final", redirected=True,
                                timeout_level=drawn[2], pool_id=("h1_final", h1_key(window)),
                                clock_regime="h1_final")
        _bump(diagnostics, "h1_final_infeasible")
        # Kernel 2014.1 (every call from 2014.4): before any clock fallback, a
        # real drive from the start bin that fits the time left (the half
        # then continues), then a time-feasible clock final, then expiry.
        drawn = _draw_from(rng, ("neutral", start_bin(spot)), "h2_neutral", spot, window, edge,
                           exclude=("clock",), extra=extra)
        if drawn is not None:
            _bump(diagnostics, "h1_fit_fallback")
            return Drive(drawn[0], drawn[1], scaled_seconds(drawn[1]), False, cell, "h1_neutral",
                         fallback="h1_fit", pool_id=("neutral", start_bin(spot)), clock_regime="h2_neutral")
        t = _clock_fallback(rng, _h1_clock_tuples(), spot, window)
        if t is not None:
            _bump(diagnostics, "fallback_clock_tuple")
            return ending_drive("clock", t, window, cell, "h1_final", fallback="clock_tuple", redirected=True)
        return _fit_or_expire(rng, spot, window, edge, cell, "h1_final", diagnostics, "h1_neutral",
                              "h1_fit_fallback", extra=extra)
    if cell == "neutral":
        drawn = _draw_from(rng, ("neutral", start_bin(spot)), "h2_neutral", spot, window, edge, extra=extra)
        if drawn is not None:
            seconds = scaled_seconds(drawn[1])
            if window - seconds <= load()["preregistration"]["neutral_h2_seconds"]:
                diagnostics["h2_neutral_into_late"] = diagnostics.get("h2_neutral_into_late", 0) + 1
            return Drive(drawn[0], drawn[1], seconds, False, cell, "h2_neutral",
                         pool_id=("neutral", start_bin(spot)), clock_regime="h2_neutral")
        need_label = need(diff)
        regime, pool_id = "late", ("late_union", need_label)
    elif cell == "OT":
        regime, pool_id, need_label = "ot", ("ot", None), "tied"
    else:
        regime, pool_id, need_label = ("late" if half == 2 else "ot"), ("late", cell), cell_need(cell)
    drawn = _draw_from(rng, pool_id, regime, spot, window, edge, timeouts, key, diagnostics, extra=extra)
    fallback = None
    if drawn is None and pool_id[0] != "late_union":
        fallback = "need_union"
        diagnostics["fallback_need_union"] = diagnostics.get("fallback_need_union", 0) + 1
        pool_id = ("late_union", need_label)
        drawn = _draw_from(rng, pool_id, regime, spot, window, edge, timeouts, key, diagnostics, extra=extra)
    if drawn is None:
        # Kernel 2014.4: a time-feasible clock final, else a drive that fits
        # inside the window, else (window <= E) a zero-play clock expiry.
        t = _clock_fallback(rng, _late_clock_tuples(need_label), spot, window)
        if t is not None:
            _bump(diagnostics, "fallback_clock_tuple")
            return ending_drive("clock", t, window, cell, regime, fallback="clock_tuple")
        return _fit_or_expire(rng, spot, window, edge, cell, regime, diagnostics, regime, "fallback_fit_drive",
                              extra=extra)
    category, t, level = drawn
    if ends_window(regime, category, t):
        return ending_drive(category, t, window, cell, regime, fallback=fallback, timeout_level=level,
                            pool_id=pool_id, clock_regime=regime)
    return Drive(category, t, scaled_seconds(t), False, cell, regime, fallback=fallback, timeout_level=level,
                 pool_id=pool_id, clock_regime=regime)


def tuple_locator(category, t):
    """A stable identifier of a real drive inside the committed artifact:
    [pool kind, pool key, index in that pool's category list], searched over
    every pool (a neutral rung draws from neighbouring bins, so the drawn
    pool id alone does not place a tuple); None when not found."""
    data = load()
    c = CATEGORIES.index(category)
    for j, bin_pools in enumerate(data["pools"]["neutral"]):
        for i, m in enumerate(bin_pools[c]):
            if m is t:
                return ["neutral", j, i]
    for kind in ("late", "h1_final"):
        for key, cells in data["pools"][kind].items():
            for i, m in enumerate(cells[category]):
                if m is t:
                    return [kind, key, i]
    for i, m in enumerate(data["pools"]["ot"][category]):
        if m is t:
            return ["ot", None, i]
    return None


def locate_tuple(category, locator):
    """The tuple a locator names, or None."""
    data = load()
    try:
        kind, key, i = locator
        if kind == "neutral":
            return data["pools"]["neutral"][key][CATEGORIES.index(category)][i]
        if kind == "ot":
            return data["pools"]["ot"][category][i]
        return data["pools"][kind][key][category][i]
    except (KeyError, IndexError, TypeError, ValueError):
        return None


def resample_drive(rng, drawn, spot, window, exclude=()):
    """Kernel 2014.4 phase 2 (register item 3, last fallback): another real
    2012 drive of the same category from the same pool rung (category and
    start-spot bucket) and the same clock regime, feasible at the spot and
    the clock, with the same window-ending status as the drive it replaces;
    None when the rung has no other such tuple. One randrange on `rng`, the
    caller's layout-resample stream, never the possession stream."""
    if drawn.pool_id is None or drawn.tuple is ZERO_TUPLE:
        return None
    regime = drawn.clock_regime or drawn.regime
    skip = [drawn.tuple] + list(exclude)
    candidates = [t for t in eligible(drawn.pool_id, drawn.category, spot, regime, window)
                  if not any(t is x or t == x for x in skip)]
    if drawn.consumes_window:
        candidates = [t for t in candidates if regime == "h1_final" or ends_window(regime, drawn.category, t)]
    else:
        candidates = [t for t in candidates if scaled_seconds(t) < window
                      and not (regime not in ("h1_neutral", "h2_neutral") and ends_window(regime, drawn.category, t))]
    if not candidates:
        return None
    t = candidates[rng.randrange(len(candidates))]
    fields = dict(fallback=drawn.fallback, redirected=drawn.redirected, timeout_level=drawn.timeout_level,
                  pool_id=drawn.pool_id, clock_regime=drawn.clock_regime)
    if drawn.consumes_window:
        return ending_drive(drawn.category, t, window, drawn.cell, drawn.regime, **fields)
    return Drive(drawn.category, t, scaled_seconds(t), False, drawn.cell, drawn.regime, **fields)


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


def adjust_punt(record, shift):
    """Kernel 2014.4 phase 2: the punter's term as a change of `shift` yards
    of gross on a non-touchback punt, the start recomputed by the same
    identity; a punt that would now reach the goal line becomes a touchback
    (gross = LOS, start 80 + enforcement). No draw. Zero returns the record
    with adjust 0."""
    out = dict(record, adjust=int(shift))
    if not shift or record["touchback"]:
        return out
    los, ret, enforcement = record["los"], record["return_yards"], record["enforcement"]
    gross = max(0, record["gross"] + int(shift))
    if los - gross <= 0:
        out.update(outcome="touchback", touchback=True, gross=los, return_yards=0, next_start=80 + enforcement)
        return out
    start = 100 - los + gross - ret + enforcement
    # The start must stay inside the field by the same identity the audit
    # checks (kick_spot_mismatch): when the return and enforcement would carry
    # it past a goal line, the applied shift is reduced, never the identity.
    if start > 99:
        gross, start = gross - (start - 99), 99
    elif start < 1:
        gross, start = gross + (1 - start), 1
    out.update(gross=gross, next_start=start, adjust=gross - record["gross"])
    return out


def adjust_return(record, shift):
    """Kernel 2014.4 phase 2: the returner's term as a change of `shift`
    return yards on a returned kick or punt record, the start moved the
    same way and kept inside the field. No draw. Zero returns the record
    with return_adjust 0."""
    out = dict(record, return_adjust=int(shift))
    if not shift or record.get("touchback") or record.get("outcome") != "returned":
        return out
    ret = max(0, record["return_yards"] + int(shift))
    applied = ret - record["return_yards"]
    start = record["next_start"] - applied
    # Inside the field by the kick identity: the applied shift is reduced
    # when the start would leave the field, never the identity.
    if start > 99:
        applied, start = applied + (start - 99), 99
    elif start < 1:
        applied, start = applied - (1 - start), 1
    out.update(return_yards=record["return_yards"] + applied, next_start=start, return_adjust=applied)
    return out


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
