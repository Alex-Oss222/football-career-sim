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

Kernel 2014.6 plumbing (batch B1): the data-dependent functions are methods
of FieldPositionModel, one instance per calibration base
(runtime.calibration_base.CalibrationBase.field_position), which owns the
loaded artifact, its field indexes and every memoised helper (the spot rungs,
the any-start lists, the zone likelihoods, the snap-seconds range). The
tuple, kick, punt and turnover field indexes come from the artifact's own
tuple_fields, kick_fields, punt_fields and turnover_fields, which must extend
the runtime lists below (append-only). The kernel binds its base's model once
per game; the module-level functions are the 2012 base's model, kept for the
research builders, audits and tests that read the 2012 base.
"""
from __future__ import annotations

from dataclasses import dataclass
import bisect

from . import chains
from . import drive_model
from .rules import RULES

from pathlib import Path

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
# The 2012 artifact's own partition total (the 2012 calibration base pins
# the same count as "field_position.drives"; each base pins its own).
EXPECTED_DRIVES = 5984
KICK = {"touchback": 0, "next_start": 1, "kick_yards": 2, "return_yards": 3, "enforcement": 4, "outcome": 5}
PUNT = {"los": 0, "outcome": 1, "gross": 2, "return_yards": 3, "enforcement": 4, "next_start": 5, "touchback": 6}
TURNOVER = {"end": 0, "next_start": 1, "return_yards": 2, "touchback": 3, "delta": 4}
# The runtime field lists each artifact must extend (append-only).
RUNTIME_FIELDS = {
    "tuple_fields": TUPLE_FIELDS,
    "kick_fields": tuple(sorted(KICK, key=KICK.get)),
    "punt_fields": tuple(sorted(PUNT, key=PUNT.get)),
    "turnover_fields": tuple(sorted(TURNOVER, key=TURNOVER.get)),
}


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def field_lists(data):
    """{list name: the artifact's field list} after the append-only prefix
    check: each artifact list must exist and begin with the runtime list (a
    later artifact may append fields, never reorder or drop one). Raises
    ValueError otherwise."""
    out = {}
    for name, runtime in RUNTIME_FIELDS.items():
        fields = data.get(name)
        if not isinstance(fields, list) or tuple(fields[:len(runtime)]) != runtime \
                or len(set(fields)) != len(fields):
            raise ValueError("%s do not extend the runtime field list (append-only)" % name.replace("_", " "))
        out[name] = tuple(fields)
    return out


def _index(fields):
    return {name: index for index, name in enumerate(fields)}


def validate(data=None, drive=None, expected_drives=EXPECTED_DRIVES):
    """Structural checks on the artifact; returns a list of errors.

    `drive` is the drive-model artifact of the same calibration base (its
    clock scale must match); `expected_drives` the base's pinned partition
    total. The defaults are the 2012 base's."""
    data = data if data is not None else _raw()
    drive = drive if drive is not None else drive_model.load()
    errors = []
    if data.get("schema") != SCHEMA:
        errors.append("field-position schema differs")
    if data.get("categories") != list(CATEGORIES):
        errors.append("field-position categories differ from the kernel categories")
    try:
        lists = field_lists(data)
    except ValueError as exc:
        errors.append(str(exc))
        lists = {name: tuple(runtime) for name, runtime in RUNTIME_FIELDS.items()}
    t_index = _index(lists["tuple_fields"])
    punt_index = _index(lists["punt_fields"])
    turnover_index = _index(lists["turnover_fields"])
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
    if total != expected_drives:
        errors.append("partition counts sum to %d, not %s" % (total, format(expected_drives, ",")))
    missing = 0
    groups = [(counts[b][c], pools.get("neutral", [])[b][c]) for b in range(len(counts))
              for c in range(len(CATEGORIES))] if len(pools.get("neutral", [])) == len(counts) else []
    for name in ("h1_final", "late"):
        for key, cells in data.get(name + "_counts", {}).items():
            pool = pools.get(name, {}).get(key, {})
            groups += [(cells.get(c, 0), pool.get(c, [])) for c in CATEGORIES]
    groups += [(data.get("ot_counts", {}).get(c, 0), pools.get("ot", {}).get(c, [])) for c in CATEGORIES]
    width = len(lists["tuple_fields"])
    for n, pool in groups:
        if not _is_int(n) or n < len(pool):
            errors.append("a pool holds more tuples than its count")
            break
        missing += n - len(pool)
        if any(len(t) != width for t in pool):
            errors.append("a tuple has the wrong number of fields")
            break
    documented = data.get("corrections", {}).get("non_renderable", {})
    if missing != documented.get("safety", -1) + documented.get("touchdown", -1) + documented.get("zero_play_terminal", -1):
        errors.append("non-renderable drives differ from the documented corrections")
    cell_map = data.get("cell_map", {})
    for label in pre.get("late_time_buckets", {}):
        for need_label in pre.get("needs", {}):
            cell = cell_map.get("%s|%s" % (label, need_label))
            if cell is None or cell not in data.get("late_counts", {}):
                errors.append("cell map does not cover %s|%s" % (label, need_label))
    for cell, cells in data.get("late_counts", {}).items():
        if sum(cells.values()) < pre.get("min_cell", 30):
            errors.append("late cell %s under MIN_CELL" % cell)
    keymap = data.get("h1_final_keymap", {})
    if sorted(keymap) != sorted("%d-%d" % e for e in H1_BUCKET_EDGES) or any(
            v not in data.get("h1_final_counts", {}) for v in keymap.values()):
        errors.append("first-half final keymap incomplete")
    for pool in _all_tuples(data, "field_goal_attempt"):
        if pool[t_index["fg_distance"]] - pool[t_index["end"]] not in (17, 18, 19):
            errors.append("a field-goal tuple has a distance offset outside {17, 18, 19}")
            break
    for pool in _all_tuples(data, "touchdown"):
        if pool[t_index["net0"]] != pool[t_index["start"]] or pool[t_index["td_kind"]] not in ("pass", "rush"):
            errors.append("a touchdown tuple does not net its start or lacks a scoring kind")
            break
    for pool in _all_tuples(data, "safety"):
        if pool[t_index["safety_term_kind"]] not in ("sack", "run") or not _is_int(pool[t_index["safety_term_los"]]):
            errors.append("a safety tuple lacks its render terminal")
            break
    kick = data.get("kickoff_pool", [])
    if len(kick) != data.get("band_centres", {}).get("kickoff_touchback_share", [0, -1])[1] or not kick:
        errors.append("kickoff pool size differs from its band centre")
    for name in ("kickoff_pool", "free_kick_pool"):
        for record in data.get(name, []):
            if len(record) != len(lists["kick_fields"]):
                errors.append("%s record malformed" % name)
                break
    p = punt_index
    for record in data.get("punt_pool", []):
        if len(record) != len(lists["punt_fields"]) or (not record[p["touchback"]] and record[p["next_start"]] != (
                100 - record[p["los"]] + record[p["gross"]] - record[p["return_yards"]] + record[p["enforcement"]])):
            errors.append("punt record does not satisfy its published identity")
            break
    o = turnover_index
    for name in ("interception_pool", "fumble_pool"):
        for record in data.get(name, []):
            if len(record) != len(lists["turnover_fields"]) or record[o["delta"]] != record[o["next_start"]] - (100 - record[o["end"]]):
                errors.append("%s record does not satisfy its published identity" % name)
                break
    if data.get("clock_scale") != drive["clock_scale"]:
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


# ---- keys that need no artifact -------------------------------------------------------

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
    unset, own_seconds is the tuple's own seconds (on the 2012 base's clock
    scale) capped at `seconds`; every model passes it for a window-ending
    drive (ending_drive)."""
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
    # Kernel 2014.6 (schema 3, R17): the first-half time match width (40 or
    # 80 s) of a window-matched h1_late draw; None for every other draw.
    match_width: int | None = None

    def __post_init__(self):
        if self.own_seconds is None:
            own = min(own_seconds(self.tuple), self.seconds) if self.consumes_window else self.seconds
            object.__setattr__(self, "own_seconds", own)

    @property
    def expiry_seconds(self):
        return self.seconds - self.own_seconds


ZERO_TUPLE = (0, 0, 0, 0, 0, 0, 0, 1, "gt600", None, None, [0, 0, 0, 0, 0, 0], [], 0,
              None, None, None, None, None, 0, 0, 0, None, None, None, 0, 0)


def _band(n):
    return next(i for i, band in enumerate(TIMEOUT_BANDS) if n in band)


def _bump(diagnostics, name):
    diagnostics[name] = diagnostics.get(name, 0) + 1


SACK_PROB_FLOOR, SACK_PROB_CEILING = 0.005, 0.5


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


def downs_start(end):
    return 100 - end


def missed_fg_start(distance):
    return min(80, 110 - distance)


class FieldPositionModel:
    """The field-position draws and keys bound to one calibration base.

    Its keys (start bin, zone, need, late time label, cell, decision zone,
    terminal clock bucket) are the frozen kernel 2013.7 cell and need rules
    read from the base's own preregistration and cell map: every receipt up
    to kernel 2014.5 is audited with the 2012 base's model. A later
    artifact schema brings its own rules in its own model; it never edits
    these."""

    CATEGORIES = CATEGORIES
    FOURTH_DOWN_CATEGORIES = FOURTH_DOWN_CATEGORIES
    CLOCK_EXPIRY_ALLOWANCE = CLOCK_EXPIRY_ALLOWANCE

    def __init__(self, base):
        self.base = base
        self.dm = base.drive_model()
        data = base.raw("field_position")
        expected = dict(base.partitions).get("field_position.drives", EXPECTED_DRIVES)
        errors = validate(data, drive=self.dm.data, expected_drives=expected)
        if errors:
            raise ValueError("invalid field-position model: " + "; ".join(errors))
        self.data = data
        lists = field_lists(data)
        self.fields = lists
        self.T = _index(lists["tuple_fields"])
        self.KICK = _index(lists["kick_fields"])
        self.PUNT = _index(lists["punt_fields"])
        self.TURNOVER = _index(lists["turnover_fields"])
        self._rungs_cache = {}
        self._any_start_cache = {}
        self._zone_cache = {}
        self._snap_range = None

    def load(self):
        """The validated artifact; treat as read-only."""
        return self.data

    def value(self, t, name, default=None):
        """A tuple's field by name, guarded: a field the tuple does not carry
        (ZERO_TUPLE, or a field appended after it was written) reads `default`."""
        index = self.T.get(name)
        if index is None or index >= len(t):
            return default
        return t[index]

    def tuple_weight(self, t):
        """A tuple's draw weight (kernel 2014.6 plumbing): its season's entry
        in the base's season-weight table; 1 for ZERO_TUPLE, for a tuple
        without a season field and for every tuple of a base drawn by events
        (an empty table, the adopted default)."""
        weights = dict(self.base.season_weights)
        if t is ZERO_TUPLE or not weights:
            return 1
        return weights.get(self.value(t, "season"), 1)

    # ---- keys --------------------------------------------------------------------

    def start_bin(self, spot):
        for index, (low, high) in enumerate(self.data["preregistration"]["start_bins"]):
            if low <= spot <= high:
                return index
        raise ValueError("spot %s outside the field" % spot)

    def zone(self, spot):
        for label, (low, high) in self.data["preregistration"]["zones"].items():
            if low <= spot <= high:
                return label
        raise ValueError("spot %s outside the field" % spot)

    def need(self, diff):
        for label, (low, high) in self.data["preregistration"]["needs"].items():
            if low <= diff <= high:
                return label
        raise ValueError("score difference %s outside the need buckets" % diff)

    def time_label(self, seconds):
        for label, (low, high) in self.data["preregistration"]["late_time_buckets"].items():
            if low <= seconds <= high:
                return label
        raise ValueError("%s seconds is not a late window" % seconds)

    def cell_for(self, half, window, diff):
        """'neutral', a late cell id, or 'OT'. OT trailing uses the <=120 trail 1-3
        cell (labelled inference: the trailing team must score)."""
        if half == "OT":
            return self.data["cell_map"]["le120|trail1_3"] if diff < 0 else "OT"
        if half == 2 and window <= self.data["preregistration"]["neutral_h2_seconds"]:
            return self.data["cell_map"]["%s|%s" % (self.time_label(window), self.need(diff))]
        return "neutral"

    cell_need = staticmethod(cell_need)
    terminal_bucket = staticmethod(terminal_bucket)
    h1_bucket_index = staticmethod(h1_bucket_index)

    def h1_key(self, window):
        return self.data["h1_final_keymap"]["%d-%d" % H1_BUCKET_EDGES[h1_bucket_index(window)]]

    def decision_zone(self, los):
        for label, (low, high) in self.data["preregistration"]["decision_zones"].items():
            if low <= los <= high:
                return label
        raise ValueError("line of scrimmage %s outside the field" % los)

    def scaled_seconds(self, t):
        return self.dm.scaled_seconds(t)

    # ---- one tuple replayed from a start spot ------------------------------------------

    def adapt(self, category, t, spot):
        """(net, end) of 2012 tuple t replayed from start spot S."""
        T = self.T
        if category == "touchdown":
            return spot, 0
        if category == "safety":
            return spot - 100, 100
        if category in KEEP_END:
            return spot - t[T["end"]], t[T["end"]]
        net = t[T["net0"]]
        return net, spot - net

    def fixed_yardage(self, category, t):
        """(free snaps, kneel yards, terminal value, non-terminal sacks) of a tuple."""
        T = self.T
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

    def static_feasible(self, category, t, spot):
        """Spot-only feasibility (no clock): field, envelope and snap capacity."""
        T = self.T
        net, end = self.adapt(category, t, spot)
        b = self.start_bin(spot)
        envelope = self.data["envelopes"][category][b]
        if envelope is None:
            return False  # no 2012 drive of this category from this start bin
        if category not in ("touchdown", "safety"):
            if not 1 <= end <= 99 or not envelope[0] <= net <= envelope[1]:
                return False
        if category == "safety" and not envelope[0] <= net <= envelope[1]:
            return False
        if category == "touchdown" and t[T["td_kind"]] not in ("pass", "rush"):
            return False
        free, kneels, terminal, sacks = self.fixed_yardage(category, t)
        if t[T["kneel_yards"]] and not 1 <= end + kneels <= 99:
            return False  # kneels are the drive's last snaps: the spot before them must be in the field
        if t[T["kneel_yards"]] and self.zone(t[T["start"]]) != self.zone(spot):
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

    def _pool(self, pool_id, category):
        pools = self.data["pools"]
        kind, key = pool_id
        if kind == "neutral":
            return pools["neutral"][key][CATEGORIES.index(category)]
        if kind == "ot":
            return pools["ot"][category]
        return pools[kind][key][category]

    def _counts(self, pool_id):
        data = self.data
        kind, key = pool_id
        if kind == "neutral":
            return dict(zip(CATEGORIES, data["neutral_counts"][key]))
        if kind == "ot":
            return data["ot_counts"]
        if kind == "late_union":
            out = {c: 0 for c in CATEGORIES}
            for cell in self._need_cells(key):
                for c, n in data["late_counts"][cell].items():
                    out[c] += n
            return out
        return data[kind + "_counts"][key]

    def _need_cells(self, need_label):
        return sorted({cell for cell in self.data["late_counts"] if cell_need(cell) == need_label})

    def _rungs(self, pool_id, category, spot):
        """Spot-feasible tuples of a pool at spot S, per ladder rung: (same bin,
        same zone). A neutral bin's list is its build-time ladder (thin bins add
        their nearest bins). Memoised per model (its base)."""
        key = (pool_id, category, spot)
        try:
            return self._rungs_cache[key]
        except KeyError:
            pass
        T = self.T
        data = self.data
        b, z = self.start_bin(spot), self.zone(spot)
        kind, pool_key = pool_id
        if kind == "neutral":
            ladder = data["neutral_ladder"][pool_key][CATEGORIES.index(category)]
            same = [t for j in ladder for t in data["pools"]["neutral"][j][CATEGORIES.index(category)]]
            wider = [t for j in range(len(data["neutral_counts"]))
                     if self.zone(data["preregistration"]["start_bins"][j][0]) == z
                     for t in data["pools"]["neutral"][j][CATEGORIES.index(category)]]
        else:
            if kind == "late_union":
                members = [t for cell in self._need_cells(pool_key) for t in data["pools"]["late"][cell][category]]
            else:
                members = list(self._pool(pool_id, category))
            same = [t for t in members if self.start_bin(t[T["start"]]) == b]
            wider = [t for t in members if self.zone(t[T["start"]]) == z]
        out = tuple(tuple(t for t in rung if self.static_feasible(category, t, spot)) for rung in (same, wider))
        self._rungs_cache[key] = out
        return out

    def _static(self, pool_id, category, spot):
        """The first rung with a spot-feasible tuple (no clock filter); () when none."""
        for rung in self._rungs(pool_id, category, spot):
            if rung:
                return rung
        return ()

    def ends_window(self, regime, category, t):
        """True when a tuple replays as the drive that runs out the window.

        In regulation a "final" 2012 drive was the last of its half or game, so it
        ran out the clock. In overtime (kernel 2013.8) a 2012 drive was also
        "final" when its score ended the game (a walk-off touchdown or field
        goal); that is not the period expiring. Under the 2013 overtime rule only
        a clock-expired drive ends the period, so in the "ot" regime every other
        tuple replays with its own scaled seconds and must fit the window."""
        if not t[self.T["final"]]:
            return False
        return regime != "ot" or category == "clock"

    def time_feasible(self, t, window):
        """Kernel 2014.4: can tuple t end a window of `window` seconds? Its own
        scaled seconds must fit (s <= window) and leave no more than the
        clock-expiry allowance to run off after its last snap (window <= s + E)."""
        own = self.own_seconds(t)
        return own <= window <= own + CLOCK_EXPIRY_ALLOWANCE

    def own_seconds(self, t):
        """A tuple's own elapsed seconds (ZERO_TUPLE, a zero-play clock expiry: 0)."""
        return 0 if t is ZERO_TUPLE else self.scaled_seconds(t)

    def snap_seconds_range(self):
        """Kernel 2014.4: {scrimmage snaps: (fewest, most) own scaled seconds}
        over every real drive in the artifact's pools (2012: 5,977 drives with
        a snap; e.g. 1 snap 1-48 s, 7 snaps 48-384 s). A zero-play possession
        may also take 0 s (the zero-play clock expiry). Derived from the
        base's data alone, never from a kernel sample; the coherence class
        seconds_per_snap_outside compares a drive's own seconds with it."""
        if self._snap_range is None:
            T = self.T
            out = {0: (0, 0)}
            for category in CATEGORIES:
                for t in _all_tuples(self.data, category):
                    n, s = t[T["plays"]], self.scaled_seconds(t)
                    low, high = out.get(n, (s, s))
                    out[n] = (min(low, s), max(high, s))
            self._snap_range = out
        return self._snap_range

    def _dynamic(self, tuples, category, regime, window):
        """Clock filters of the regime (see the module docstring and README).

        Kernel 2014.4: a tuple that ends the window (every first-half final; a
        late final; an overtime clock final) must be time feasible
        (time_feasible), replacing the 2013.6 start-bucket match, which let a
        90-second drive stand for a 9:20 window. Any other tuple must finish
        inside the window (s < window)."""
        if regime == "h1_neutral":
            return tuples
        if regime == "h1_final":
            return tuple(t for t in tuples if self.time_feasible(t, window))
        if regime == "h2_neutral":
            return tuple(t for t in tuples if self.scaled_seconds(t) < window)
        T = self.T
        out = []
        for t in tuples:
            if self.ends_window(regime, category, t):
                if not self.time_feasible(t, window):
                    continue
                left = 0
            else:
                seconds = self.scaled_seconds(t)
                if seconds >= window:
                    continue
                left = window - seconds
            if regime == "late" and category in FOURTH_DOWN_CATEGORIES and terminal_bucket(left) != t[T["term_bucket"]]:
                continue
            out.append(t)
        return tuple(out)

    def eligible(self, pool_id, category, spot, regime, window):
        """Tuples feasible at the spot and the clock, by the ladder: the same-bin
        rung if any of its tuples is feasible, else the same-zone rung; () masks
        the category. The ladder steps on full feasibility (spot and clock), so a
        same-bin rung whose tuples all fail the clock filter never masks a
        category that the same zone can still supply."""
        for rung in self._rungs(pool_id, category, spot):
            feasible = self._dynamic(rung, category, regime, window)
            if feasible:
                return feasible
        if NEED_UNION_RUNGS and regime == "late" and pool_id[0] == "late":
            # Kernel 2014.2: a late cell with no feasible drive of the category
            # borrows the same need's other time buckets (same bin, then same
            # zone), under the same clock filters.
            union = ("late_union", cell_need(pool_id[1]))
            for rung in self._rungs(union, category, spot):
                feasible = self._dynamic(rung, category, regime, window)
                if feasible:
                    return feasible
            # Last rung: any real drive of the category and need, whatever its
            # start, that is feasible at this spot (end in the field, net inside
            # the current start bin's 2012 envelope) and at this clock.
            feasible = self._dynamic(self._any_start(union, category, spot), category, regime, window)
            if feasible:
                return feasible
        return ()

    def _any_start(self, pool_id, category, spot):
        key = (pool_id, category, spot)
        try:
            return self._any_start_cache[key]
        except KeyError:
            value = self._any_start_cache[key] = tuple(
                t for t in self._members(pool_id, category) if self.static_feasible(category, t, spot))
            return value

    category_mix = staticmethod(category_mix)

    def draw_options(self, pool_id, regime, spot, window):
        """(counts, eligible tuples by category) for one draw from one pool."""
        counts = self._counts(pool_id)
        options = {c: self.eligible(pool_id, c, spot, regime, window) for c in CATEGORIES if counts.get(c, 0)}
        return counts, options

    def timeout_match(self, level, t, timeouts, key):
        """Kernel 2014.1 ladder: does tuple t match the clubs' charged timeouts?

        Level 0: both clubs' counts equal the tuple's; level 1: the clock-stopping
        side's count (the offense when it trails, otherwise the defense) equals the
        tuple's; level 2: that side's count is in the same band (0, 1-2, 3);
        level 3: unconditioned."""
        if level >= 3:
            return True
        T = self.T
        off, dfn = t[T["off_timeouts"]], t[T["def_timeouts"]]
        if off is None or dfn is None:
            return False
        if level == 0:
            return (off, dfn) == tuple(timeouts)
        mine, now = (off, timeouts[0]) if key == "off" else (dfn, timeouts[1])
        return mine == now if level == 1 else _band(mine) == _band(now)

    def _members(self, pool_id, category):
        """Every tuple of a pool's category, before spot and clock feasibility."""
        kind, key = pool_id
        if kind == "late_union":
            return [t for cell in self._need_cells(key) for t in self.data["pools"]["late"][cell][category]]
        return list(self._pool(pool_id, category))

    def _timeout_options(self, pool_id, counts, options, timeouts, key, diagnostics):
        """(weights, options) conditioned on the charged timeouts by the ladder.

        A level is used when the pool holds at least MIN_TIMEOUT_POOL matching
        tuples and at least one matching tuple is feasible here; the category
        weight is its 2012 cell count times the share of its tuples that match
        (P(category | cell, timeouts) up to a constant)."""
        members = {c: self._members(pool_id, c) for c in counts if counts.get(c, 0)}
        for level in range(3):
            matching = {c: [t for t in m if self.timeout_match(level, t, timeouts, key)] for c, m in members.items()}
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
                narrowed[c] = tuple(t for t in feasible if self.timeout_match(level, t, timeouts, key)) or feasible
                if feasible and narrowed[c] is feasible and diagnostics is not None:
                    diagnostics["timeout_tuple_widened"] = diagnostics.get("timeout_tuple_widened", 0) + 1
            if any(weights.get(c) and narrowed.get(c) for c in weights):
                if diagnostics is not None:
                    diagnostics["timeout_level_%d" % level] = diagnostics.get("timeout_level_%d" % level, 0) + 1
                return weights, narrowed, level
        if diagnostics is not None:
            diagnostics["timeout_level_3"] = diagnostics.get("timeout_level_3", 0) + 1
        return counts, options, 3

    def _reference(self, pool_id):
        """The larger pool whose start zones estimate P(zone | category) for a
        conditioned draw: the need's union of late cells, every first-half final,
        or the overtime pool."""
        kind, key = pool_id
        if kind == "late":
            return ("late_union", cell_need(key))
        if kind == "h1_final":
            return ("h1_final_all", None)
        return pool_id

    def zone_likelihood(self, reference, spot_zone):
        """{category: P(zone | category) / P(zone)} over the reference pool, with
        add-one smoothing over the three zones. Memoised per model."""
        cache_key = (reference, spot_zone)
        try:
            return self._zone_cache[cache_key]
        except KeyError:
            pass
        T = self.T
        data = self.data
        kind, key = reference

        def members(c):
            if kind == "h1_final_all":
                return [t for cells in data["pools"]["h1_final"].values() for t in cells[c]]
            return self._members(reference, c)
        by_cat = {c: members(c) for c in CATEGORIES}
        a = ZONE_SMOOTHING
        total = sum(len(m) for m in by_cat.values())
        in_zone = sum(1 for m in by_cat.values() for t in m if self.zone(t[T["start"]]) == spot_zone)
        base = (in_zone + a) / (total + 3 * a)
        out = {}
        for c, m in by_cat.items():
            n_zone = sum(1 for t in m if self.zone(t[T["start"]]) == spot_zone)
            out[c] = ((n_zone + a) / (len(m) + 3 * a)) / base
        self._zone_cache[cache_key] = out
        return out

    def sack_rate_base(self):
        """The base's sacks per dropback the phase-2 sack shift is measured from."""
        made, n = self.data["band_centres"]["sacks_per_dropback"]
        return made / n

    def tuple_weights(self, pool, sack_shift):
        """Kernel 2014.4 phase 2: each real drive's binomial likelihood ratio
        when the per-dropback sack probability moves from the 2012 base p0 to
        p1 = p0 + shift: (p1/p0)^sacks x ((1-p1)/(1-p0))^attempts (attempts =
        dropbacks - sacks). Identical for every club; a zero shift is never
        routed here."""
        T = self.T
        p0 = self.sack_rate_base()
        p1 = min(SACK_PROB_CEILING, max(SACK_PROB_FLOOR, p0 + sack_shift))
        ratio_sack, ratio_none = p1 / p0, (1 - p1) / (1 - p0)
        return [ratio_sack ** int(t[T["sacks"]] or 0) * ratio_none ** int(t[T["attempts"]] or 0) for t in pool]

    def draw_tuple(self, rng, pool, sack_shift=0.0):
        """One tuple from the pool: uniform (one randrange, as every earlier
        kernel) with no sack shift; otherwise weighted by tuple_weights (one
        random)."""
        if not sack_shift:
            return pool[rng.randrange(len(pool))]
        weights = self.tuple_weights(pool, sack_shift)
        target = rng.random() * sum(weights)
        cumulative = 0.0
        for t, w in zip(pool, weights):
            cumulative += w
            if target < cumulative:
                return t
        return pool[-1]

    def _draw_from(self, rng, pool_id, regime, spot, window, edge, timeouts=None, key="def", diagnostics=None,
                   exclude=(), clock_regime=None, extra=None):
        counts, options = self.draw_options(pool_id, clock_regime or regime, spot, window)
        # Kernel 2014.4: `exclude` masks categories (the fit draws mask clock,
        # which cannot run out a window it does not reach); `clock_regime`
        # applies another regime's clock filters (a late fit drive keeps the
        # late terminal-bucket rule) without its conditioning.
        options = {c: (() if c in exclude else v) for c, v in options.items()}
        if ZONE_CONDITIONING and regime in TIMEOUT_REGIMES:
            ratio = self.zone_likelihood(self._reference(pool_id), self.zone(spot))
            counts = {c: n * ratio[c] for c, n in counts.items()}
        level = None
        if timeouts is not None and regime in TIMEOUT_REGIMES:
            counts, options, level = self._timeout_options(pool_id, counts, options, timeouts, key, diagnostics)
        extra = extra or {}
        probs = category_mix(counts, edge, options, extra.get("int", 0.0))
        if not probs:
            return None
        category = drive_model.draw_category(rng, probs)
        pool = options[category]
        return category, self.draw_tuple(rng, pool, extra.get("sack", 0.0)), level

    def _clock_fallback(self, rng, tuples, spot, window):
        """A final clock tuple feasible at the spot, and (kernel 2014.4) time
        feasible for the window, whose start bucket is nearest the window's
        (2013.6 edges); None when there is none."""
        T = self.T
        bucket = h1_bucket_index(window)
        by_distance = {}
        for t in tuples:
            if t[T["final"]] and self.static_feasible("clock", t, spot) and self.time_feasible(t, window):
                by_distance.setdefault(abs(h1_bucket_index(t[T["t0"]]) - bucket), []).append(t)
        if not by_distance:
            return None
        pool = by_distance[min(by_distance)]
        return pool[rng.randrange(len(pool))]

    def _late_clock_tuples(self, need_label):
        return [t for cell in self._need_cells(need_label) for t in self.data["pools"]["late"][cell]["clock"]]

    def _h1_clock_tuples(self):
        return [t for cells in self.data["pools"]["h1_final"].values() for t in cells["clock"]]

    def ending_drive(self, category, t, window, cell, regime, **kw):
        """Kernel 2014.4: a drive that ends the window. It uses the whole window
        (the kernel's half invariants), keeps its own seconds and publishes the
        rest as its clock-expiry leg."""
        return Drive(category, t, window, True, cell, regime, own_seconds=min(self.own_seconds(t), window), **kw)

    def _fit_or_expire(self, rng, spot, window, edge, cell, regime, diagnostics, fit_regime, fit_counter, extra=None):
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
        drawn = self._draw_from(rng, ("neutral", self.start_bin(spot)), "h2_neutral", spot, window, edge,
                                exclude=("clock",), clock_regime=clock_regime, extra=extra)
        if drawn is not None:
            _bump(diagnostics, fit_counter)
            return Drive(drawn[0], drawn[1], self.scaled_seconds(drawn[1]), False, cell, fit_regime,
                         fallback="h1_fit" if fit_counter == "h1_fit_fallback" else "fit",
                         pool_id=("neutral", self.start_bin(spot)), clock_regime=clock_regime)
        if window <= CLOCK_EXPIRY_ALLOWANCE:
            _bump(diagnostics, "clock_expiry_zero")
            return self.ending_drive("clock", ZERO_TUPLE, window, cell, regime, fallback="expiry")
        _bump(diagnostics, "fallback_zero_tuple")
        return self.ending_drive("clock", ZERO_TUPLE, window, cell, regime, fallback="zero")

    def draw_drive(self, rng, spot, half, window, diff, edge, diagnostics, timeouts=None, extra=None):
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
        cell = self.cell_for(half, window, diff)
        key = "off" if diff < 0 else "def"
        if half == "OT" and diff > 0:
            diagnostics["ot_leading_offense"] = diagnostics.get("ot_leading_offense", 0) + 1
        if half == 1:
            drawn = self._draw_from(rng, ("neutral", self.start_bin(spot)), "h1_neutral", spot, window, edge,
                                    extra=extra)
            if drawn is not None:
                category, t, _ = drawn
                seconds = self.scaled_seconds(t)
                if category != "clock" and seconds < window:
                    return Drive(category, t, seconds, False, cell, "h1_neutral",
                                 pool_id=("neutral", self.start_bin(spot)), clock_regime="h1_neutral")
            diagnostics["interior_clock_redirected"] = diagnostics.get("interior_clock_redirected", 0) + 1
            # Kernel 2014.4: the redirect reaches only time-feasible finals
            # (_dynamic); the draw returns None, consuming nothing, when the
            # window's pool has none (every window over about 160 s).
            drawn = self._draw_from(rng, ("h1_final", self.h1_key(window)), "h1_final", spot, window, edge,
                                    timeouts, key, diagnostics, extra=extra)
            if drawn is not None:
                return self.ending_drive(drawn[0], drawn[1], window, cell, "h1_final", redirected=True,
                                         timeout_level=drawn[2], pool_id=("h1_final", self.h1_key(window)),
                                         clock_regime="h1_final")
            _bump(diagnostics, "h1_final_infeasible")
            # Kernel 2014.1 (every call from 2014.4): before any clock fallback, a
            # real drive from the start bin that fits the time left (the half
            # then continues), then a time-feasible clock final, then expiry.
            drawn = self._draw_from(rng, ("neutral", self.start_bin(spot)), "h2_neutral", spot, window, edge,
                                    exclude=("clock",), extra=extra)
            if drawn is not None:
                _bump(diagnostics, "h1_fit_fallback")
                return Drive(drawn[0], drawn[1], self.scaled_seconds(drawn[1]), False, cell, "h1_neutral",
                             fallback="h1_fit", pool_id=("neutral", self.start_bin(spot)), clock_regime="h2_neutral")
            t = self._clock_fallback(rng, self._h1_clock_tuples(), spot, window)
            if t is not None:
                _bump(diagnostics, "fallback_clock_tuple")
                return self.ending_drive("clock", t, window, cell, "h1_final", fallback="clock_tuple", redirected=True)
            return self._fit_or_expire(rng, spot, window, edge, cell, "h1_final", diagnostics, "h1_neutral",
                                       "h1_fit_fallback", extra=extra)
        if cell == "neutral":
            drawn = self._draw_from(rng, ("neutral", self.start_bin(spot)), "h2_neutral", spot, window, edge,
                                    extra=extra)
            if drawn is not None:
                seconds = self.scaled_seconds(drawn[1])
                if window - seconds <= self.data["preregistration"]["neutral_h2_seconds"]:
                    diagnostics["h2_neutral_into_late"] = diagnostics.get("h2_neutral_into_late", 0) + 1
                return Drive(drawn[0], drawn[1], seconds, False, cell, "h2_neutral",
                             pool_id=("neutral", self.start_bin(spot)), clock_regime="h2_neutral")
            need_label = self.need(diff)
            regime, pool_id = "late", ("late_union", need_label)
        elif cell == "OT":
            regime, pool_id, need_label = "ot", ("ot", None), "tied"
        else:
            regime, pool_id, need_label = ("late" if half == 2 else "ot"), ("late", cell), cell_need(cell)
        drawn = self._draw_from(rng, pool_id, regime, spot, window, edge, timeouts, key, diagnostics, extra=extra)
        fallback = None
        if drawn is None and pool_id[0] != "late_union":
            fallback = "need_union"
            diagnostics["fallback_need_union"] = diagnostics.get("fallback_need_union", 0) + 1
            pool_id = ("late_union", need_label)
            drawn = self._draw_from(rng, pool_id, regime, spot, window, edge, timeouts, key, diagnostics, extra=extra)
        if drawn is None:
            # Kernel 2014.4: a time-feasible clock final, else a drive that fits
            # inside the window, else (window <= E) a zero-play clock expiry.
            t = self._clock_fallback(rng, self._late_clock_tuples(need_label), spot, window)
            if t is not None:
                _bump(diagnostics, "fallback_clock_tuple")
                return self.ending_drive("clock", t, window, cell, regime, fallback="clock_tuple")
            return self._fit_or_expire(rng, spot, window, edge, cell, regime, diagnostics, regime,
                                       "fallback_fit_drive", extra=extra)
        category, t, level = drawn
        if self.ends_window(regime, category, t):
            return self.ending_drive(category, t, window, cell, regime, fallback=fallback, timeout_level=level,
                                     pool_id=pool_id, clock_regime=regime)
        return Drive(category, t, self.scaled_seconds(t), False, cell, regime, fallback=fallback,
                     timeout_level=level, pool_id=pool_id, clock_regime=regime)

    def tuple_locator(self, category, t):
        """A stable identifier of a real drive inside the committed artifact:
        [pool kind, pool key, index in that pool's category list], searched over
        every pool (a neutral rung draws from neighbouring bins, so the drawn
        pool id alone does not place a tuple); None when not found."""
        data = self.data
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

    def locate_tuple(self, category, locator):
        """The tuple a locator names, or None."""
        data = self.data
        try:
            kind, key, i = locator
            if kind == "neutral":
                return data["pools"]["neutral"][key][CATEGORIES.index(category)][i]
            if kind == "ot":
                return data["pools"]["ot"][category][i]
            return data["pools"][kind][key][category][i]
        except (KeyError, IndexError, TypeError, ValueError):
            return None

    def resample_drive(self, rng, drawn, spot, window, exclude=()):
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
        candidates = [t for t in self.eligible(drawn.pool_id, drawn.category, spot, regime, window)
                      if not any(t is x or t == x for x in skip)]
        if drawn.consumes_window:
            candidates = [t for t in candidates if regime == "h1_final" or self.ends_window(regime, drawn.category, t)]
        else:
            candidates = [t for t in candidates if self.scaled_seconds(t) < window
                          and not (regime not in ("h1_neutral", "h2_neutral")
                                   and self.ends_window(regime, drawn.category, t))]
        if not candidates:
            return None
        t = candidates[rng.randrange(len(candidates))]
        fields = dict(fallback=drawn.fallback, redirected=drawn.redirected, timeout_level=drawn.timeout_level,
                      pool_id=drawn.pool_id, clock_regime=drawn.clock_regime)
        if drawn.consumes_window:
            return self.ending_drive(drawn.category, t, window, drawn.cell, drawn.regime, **fields)
        return Drive(drawn.category, t, self.scaled_seconds(t), False, drawn.cell, drawn.regime, **fields)

    # ---- transitions -------------------------------------------------------------------------

    def _kick_record(self, rng, pool, spot):
        record = pool[rng.randrange(len(pool))]
        K = self.KICK
        touchback = record[K["touchback"]]
        return {"touchback": bool(touchback), "next_start": record[K["next_start"]],
                "kick_yards": record[K["kick_yards"]],
                "return_yards": 0 if touchback else record[K["return_yards"]],
                "enforcement": record[K["enforcement"]], "outcome": record[K["outcome"]], "kick_spot": spot}

    def kickoff(self, rng):
        """A real 2012 own-35 kickoff: one randrange over the pool."""
        return self._kick_record(rng, self.data["kickoff_pool"], 35)

    def free_kick(self, rng):
        """A real 2012 safety free kick from the 20: one randrange over 13."""
        return self._kick_record(rng, self.data["free_kick_pool"], 20)

    def _nearest(self, pool, key_index, spot, ok):
        """The K feasible records nearest the spot, with every record tied at the
        K-th distance included (pool sorted by the key; season order within a
        key). Including the tied boundary keeps the draw from favouring a fixed
        subset of records at a crowded line of scrimmage."""
        keys = [record[key_index] for record in pool]
        right = bisect.bisect_left(keys, spot)
        left = right - 1
        out = []
        limit = self.data["preregistration"]["k_transition"]
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

    def punt(self, rng, los):
        """A real 2012 punt drawn from the 20 feasible records nearest the line of
        scrimmage (ties by index). A touchback publishes gross = LOS and a start
        of 80 + enforcement; otherwise start = 100 - LOS + gross - return + e."""
        P = self.PUNT

        def ok(record):
            if record[P["touchback"]]:
                return los <= record[P["los"]]
            start = 100 - los + record[P["gross"]] - record[P["return_yards"]] + record[P["enforcement"]]
            return 1 <= start <= 99
        candidates = self._nearest(self.data["punt_pool"], P["los"], los, ok)
        record = candidates[rng.randrange(len(candidates))]
        touchback = bool(record[P["touchback"]])
        gross = los if touchback else record[P["gross"]]
        ret = 0 if touchback else record[P["return_yards"]]
        enforcement = record[P["enforcement"]]
        start = 80 + enforcement if touchback else 100 - los + gross - ret + enforcement
        return {"los": los, "outcome": record[P["outcome"]], "gross": gross, "return_yards": ret,
                "enforcement": enforcement, "next_start": start, "touchback": touchback,
                "record_los": record[P["los"]]}

    adjust_punt = staticmethod(adjust_punt)
    adjust_return = staticmethod(adjust_return)

    def turnover(self, rng, kind, end):
        """A real 2012 interception or fumble-lost transition from the 20 feasible
        records nearest the turnover spot: start = 100 - end + delta, or 80 + e
        for a touchback."""
        O = self.TURNOVER
        pool = self.data["interception_pool" if kind == "interception" else "fumble_pool"]

        def start_of(record):
            if record[O["touchback"]]:
                return record[O["next_start"]]
            return 100 - end + record[O["delta"]]
        candidates = self._nearest(pool, O["end"], end, lambda r: 1 <= start_of(r) <= 99)
        record = candidates[rng.randrange(len(candidates))]
        touchback = bool(record[O["touchback"]])
        start = start_of(record)
        return {"end": end, "next_start": start, "return_yards": record[O["return_yards"]],
                "touchback": touchback, "enforcement": (start - 80) if touchback else 0,
                "delta": record[O["delta"]], "record_end": record[O["end"]]}

    downs_start = staticmethod(downs_start)
    missed_fg_start = staticmethod(missed_fg_start)


# ---- kernel 2014.6: the schema-3 model (batch B5) ------------------------------------------

SCHEMA_V3 = "2010-2014w4-nfl-field-position-model-v3"
V3_POOLS = ("h1_late", "late")
V3_OT_POOLS = ("ot_first", "ot_sudden")


def _v3_tuples(data, category):
    pools = data.get("pools", {})
    index = CATEGORIES.index(category)
    for row in pools.get("neutral", []):
        yield from row[index] if index < len(row) else []
    for name in V3_POOLS:
        for cell in pools.get(name, {}).values():
            yield from cell.get(category, [])
    for name in V3_OT_POOLS:
        yield from pools.get(name, {}).get(category, [])


def _receiving(records, index):
    """Transition records the receiving club takes over at their published
    start (the retained kicking-team recoveries of B3b wait for R12 layer C,
    batch B10: drawn here they would hand the ball to the wrong club)."""
    return [r for r in records if r[index] != "kicking"]


def validate_v3(data, drive, expected_drives, specification_sha256, rules):
    """Structural checks on a schema-3 artifact (the 2010-2014 base);
    returns a list of errors. `rules` are the pinned specification's frozen
    end-of-half rules, which the artifact's preregistration must equal."""
    errors = []
    if data.get("schema") != SCHEMA_V3:
        errors.append("field-position schema differs")
    if data.get("categories") != list(CATEGORIES):
        errors.append("field-position categories differ from the kernel categories")
    if data.get("specification_sha256") != specification_sha256:
        errors.append("field-position artifact names another pre-build specification")
    try:
        lists = field_lists(data)
    except ValueError as exc:
        errors.append(str(exc))
        return errors
    T_ = _index(lists["tuple_fields"])
    for name in ("season", "last_spike_to_end"):
        if name not in T_:
            errors.append("tuple field %s missing" % name)
    for name in ("possession",):
        if name not in lists["kick_fields"] or name not in lists["punt_fields"]:
            errors.append("transition field %s missing" % name)
    if errors:
        return errors
    pre = data.get("preregistration", {})
    if [tuple(b) for b in pre.get("start_bins", [])] != [(90, 99), (81, 89), (80, 80), (70, 79), (60, 69), (50, 59),
                                                         (40, 49), (30, 39), (20, 29), (1, 19)]:
        errors.append("start bins differ from the pre-registered list")
    if pre.get("min_cell") != 30 or pre.get("k_transition") != 20 or pre.get("fg_offsets") != [17, 18, 19]:
        errors.append("pre-registered constants differ")
    for key, rule in (("needs", "NEEDS"), ("late_time_buckets", "LATE_TIME_BUCKETS"),
                      ("decision_zones", "DECISION_ZONES"), ("h1_late_edges", "H1_LATE_EDGES"),
                      ("neutral_over_seconds", "NEUTRAL_OVER_SECONDS")):
        if pre.get(key) != rules.get(rule):
            errors.append("preregistration %s differs from the specification's %s" % (key, rule))
    if rules.get("H1_LATE_SECONDS") != rules.get("NEUTRAL_OVER_SECONDS") or \
            rules.get("FINAL_FEASIBLE_SLACK_SECONDS") != CLOCK_EXPIRY_ALLOWANCE:
        errors.append("specification end-of-half windows differ from the kernel's clock-expiry allowance")
    if data.get("constants", {}).get("spike_window", {}).get("specification") != rules.get("SPIKE_WINDOW") or \
            data["constants"]["spike_window"].get("pre_divergence_max_seconds") != rules.get("SPIKE_WINDOW"):
        errors.append("spike window differs from the specification")
    counts = data.get("neutral_counts", [])
    pools = data.get("pools", {})
    total = sum(sum(row) for row in counts)
    for name in ("h1_late", "late"):
        total += sum(sum(v.values()) for v in data.get(name + "_counts", {}).values())
    for name in V3_OT_POOLS + ("ot_untied",):
        total += sum(data.get(name + "_counts", {}).values())
    if total != expected_drives:
        errors.append("partition counts sum to %d, not %s" % (total, format(expected_drives, ",")))
    groups = [(counts[b][c], pools.get("neutral", [])[b][c]) for b in range(len(counts))
              for c in range(len(CATEGORIES))] if len(pools.get("neutral", [])) == len(counts) else []
    for name in V3_POOLS:
        for key, cells in data.get(name + "_counts", {}).items():
            pool = pools.get(name, {}).get(key, {})
            groups += [(cells.get(c, 0), pool.get(c, [])) for c in CATEGORIES]
    for name in V3_OT_POOLS:
        groups += [(data.get(name + "_counts", {}).get(c, 0), pools.get(name, {}).get(c, [])) for c in CATEGORIES]
    missing = 0
    width = len(lists["tuple_fields"])
    for n, pool in groups:
        if not _is_int(n) or n < len(pool):
            errors.append("a pool holds more tuples than its count")
            break
        missing += n - len(pool)
        if any(len(t) != width for t in pool):
            errors.append("a tuple has the wrong number of fields")
            break
    documented = data.get("corrections", {}).get("non_renderable", {})
    if missing != documented.get("safety", -1) + documented.get("touchdown", -1) + documented.get("zero_play_terminal", -1):
        errors.append("non-renderable drives differ from the documented corrections")
    cell_map = data.get("cell_map", {})
    for label in pre.get("late_time_buckets", {}):
        for need_label in pre.get("needs", {}):
            cell = cell_map.get("%s|%s" % (label, need_label))
            if cell is None or cell not in data.get("late_counts", {}):
                errors.append("cell map does not cover %s|%s" % (label, need_label))
    for cell, cells in data.get("late_counts", {}).items():
        if sum(cells.values()) < pre.get("min_cell", 30):
            errors.append("late cell %s under MIN_CELL" % cell)
    keymap = data.get("h1_late_keymap", {})
    if sorted(keymap) != sorted("%d-%d" % tuple(e) for e in pre.get("h1_late_edges", [])) or any(
            v not in data.get("h1_late_counts", {}) for v in keymap.values()):
        errors.append("first-half late keymap incomplete")
    for t in _v3_tuples(data, "field_goal_attempt"):
        if t[T_["fg_distance"]] - t[T_["end"]] not in (17, 18, 19):
            errors.append("a field-goal tuple has a distance offset outside {17, 18, 19}")
            break
    for t in _v3_tuples(data, "touchdown"):
        if t[T_["net0"]] != t[T_["start"]] or t[T_["td_kind"]] not in ("pass", "rush"):
            errors.append("a touchdown tuple does not net its start or lacks a scoring kind")
            break
    for t in _v3_tuples(data, "safety"):
        if t[T_["safety_term_kind"]] not in ("sack", "run") or not _is_int(t[T_["safety_term_los"]]):
            errors.append("a safety tuple lacks its render terminal")
            break
    for category in CATEGORIES:
        for t in _v3_tuples(data, category):
            if t[T_["spikes"]] and not _is_int(t[T_["last_spike_to_end"]]):
                errors.append("a tuple with a spike lacks its last-spike seconds")
                break
    K_, P_, O_ = _index(lists["kick_fields"]), _index(lists["punt_fields"]), _index(lists["turnover_fields"])
    kick = _receiving(data.get("kickoff_pool", []), K_["possession"])
    if not kick or len(kick) != data.get("band_centres", {}).get("kickoff_touchback_share", {}).get("pooled", [0, -1])[1]:
        errors.append("kickoff pool size differs from its band centre")
    for name in ("kickoff_pool", "free_kick_pool"):
        for record in data.get(name, []):
            if len(record) != len(lists["kick_fields"]) or (
                    record[K_["possession"]] != "kicking" and not record[K_["touchback"]]
                    and record[K_["next_start"]] != (35 if name == "kickoff_pool" else 20)
                    + record[K_["kick_yards"]] - record[K_["return_yards"]] + record[K_["enforcement"]]):
                errors.append("%s record does not satisfy its published identity" % name)
                break
    for record in data.get("punt_pool", []):
        if len(record) != len(lists["punt_fields"]) or (
                record[P_["possession"]] != "kicking" and not record[P_["touchback"]]
                and record[P_["next_start"]] != (100 - record[P_["los"]] + record[P_["gross"]]
                                                 - record[P_["return_yards"]] + record[P_["enforcement"]])):
            errors.append("punt record does not satisfy its published identity")
            break
    for name in ("interception_pool", "fumble_pool"):
        for record in data.get(name, []):
            if len(record) != len(lists["turnover_fields"]) or \
                    record[O_["delta"]] != record[O_["next_start"]] - (100 - record[O_["end"]]):
                errors.append("%s record does not satisfy its published identity" % name)
                break
    if data.get("clock_scale") != drive["clock_scale"]:
        errors.append("clock scale differs from the drive model's")
    sacks = data.get("band_centres", {}).get("sacks_per_dropback", {}).get("pooled")
    if not (isinstance(sacks, list) and len(sacks) == 2 and 0 < sacks[0] < sacks[1]):
        errors.append("sacks-per-dropback centre invalid")
    if data.get("reconciliation", {}).get("result") != "pass":
        errors.append("field-position reconciliation did not pass")
    if data.get("second_pass", {}).get("result") != "pass":
        errors.append("field-position second pass did not pass")
    return errors


class FieldPositionModelV3(FieldPositionModel):
    """The schema-3 field-position draws of the 2010-2014 base (kernel
    2014.6, batch B5; profile flag regimes_v3). Its keys and constants are
    the pinned pre-build specification's (section 4, end of half and late
    game), read from the base, never typed:

    - R17 (first half): every first-half possession with a window at or
      under H1_LATE_SECONDS draws from h1_late: the tuples whose own start t0
      lies within TIME_MATCH_SECONDS of the window, else within
      TIME_MATCH_FALLBACK_SECONDS (an engineering fallback, counted
      h1_late_match_fallback), then the window's bucket cell, then the
      union of the h1_late cells, a time-feasible clock final and the fit
      or expiry rung. A real final must be time feasible (s <= w <= s + 40);
      a non-final must fit (s < w); fit draws use non-final tuples. Over
      H1_LATE_SECONDS there is no redirect: the fitting neutral draw (no
      clock drive, s < w) is the primary path.
    - R7: a clock tuple is feasible only if its end decision zone equals its
      real end zone, in every regime and in _clock_fallback (ZERO_TUPLE is
      exempt).
    - R10: the late needs are the specification's eight; every late fallback
      (the need union, the late clock fallback, _fit_or_expire) masks each
      category whose count is zero in the time cell actually drawn.
    - R14: ot_first when the overtime history is empty, ot_sudden otherwise;
      a trailing overtime offense draws the late trail1_3 cell at the
      overtime clock's own time label, with the punt masked and its weight
      moved to downs (an inference: 0 punts in 6 real trailing drives), the
      exclusion passed through _fit_or_expire. Spike rule: a tuple with a
      spike is feasible only if w - own + (its last spike's seconds to its
      end) <= SPIKE_WINDOW.
    - W5b: every timeout-conditioned draw prefers, within the drawn
      category, the tuples whose real clubs used no more timeouts than the
      branch clubs hold (inside resample_drive too); no category is masked
      by timeouts, timeout_unavailable_kept counts a drawn category with no
      such tuple, and the kernel's cap stays as a backstop.

    Kick and punt draws use the records the receiving club takes over
    (retained kicking-team recoveries wait for R12 layer C, batch B10)."""

    TIMEOUT_REGIMES = ("h1_late", "late", "ot")
    FIT_REGIMES = {"h1_neutral": "fit_h1", "h1_late": "fit_h1", "late": "fit_late", "ot": "fit_ot"}

    def __init__(self, base):
        self.base = base
        self.dm = base.drive_model()
        data = base.raw("field_position")
        rules = base.specification_rules()["end_of_half"]
        expected = dict(base.partitions).get("field_position.drives")
        errors = validate_v3(data, self.dm.data, expected, base.pin("specification").sha256, rules)
        if errors:
            raise ValueError("invalid field-position model: " + "; ".join(errors))
        self.data = data
        self.rules = rules
        lists = field_lists(data)
        self.fields = lists
        self.T = _index(lists["tuple_fields"])
        self.KICK = _index(lists["kick_fields"])
        self.PUNT = _index(lists["punt_fields"])
        self.TURNOVER = _index(lists["turnover_fields"])
        self.H1_LATE_SECONDS = rules["H1_LATE_SECONDS"]
        self.H1_LATE_EDGES = tuple(tuple(e) for e in rules["H1_LATE_EDGES"])
        self.TIME_MATCH = (rules["TIME_MATCH_SECONDS"], rules["TIME_MATCH_FALLBACK_SECONDS"])
        self.SPIKE_WINDOW = rules["SPIKE_WINDOW"]
        # Kernel 2014.6 batch B6 (W3, W5a): the early-field-goal bound and the
        # clock-detail tables (gap seconds, kick lengths, timeout seats) are
        # the artifact's constants block (specification section 4; W5a
        # table cells are [sum of seconds, snaps]); read, never typed.
        self.EARLY_FG_SECONDS = rules["EARLY_FG_SECONDS"]
        constants = data.get("constants") or {}
        if constants.get("early_field_goal", {}).get("specification") != self.EARLY_FG_SECONDS:
            raise ValueError("early field-goal constant differs between the artifact and the specification")
        self.clock_detail = constants.get("w5a") or {}
        self._kick_length = {}
        for kick in self.clock_detail.get("kicks", ()):
            seconds = snaps = 0
            for key, (total, n) in self.clock_detail["kick_length_seconds"].items():
                if key.split("|", 1)[0] == kick:
                    seconds += total
                    snaps += n
            self._kick_length[kick] = int(round(seconds / snaps)) if snaps else 0
        self._fg4_cache = {}
        self._rungs_cache = {}
        self._any_start_cache = {}
        self._zone_cache = {}
        self._snap_range = None
        self._kick_pools = {name: _receiving(data[name], self.KICK["possession"])
                            for name in ("kickoff_pool", "free_kick_pool")}
        self._punt_pool = _receiving(data["punt_pool"], self.PUNT["possession"])
        # Per category, the h1_late union's starts, sorted, for the time-match counts.
        T = self.T
        self._h1_starts = {c: sorted(t[T["t0"]] for t in self._members(("h1_late_union", None), c))
                           for c in CATEGORIES}

    # ---- keys --------------------------------------------------------------------

    def h1_key(self, window):
        w = max(0, int(window))
        for low, high in self.H1_LATE_EDGES:
            if low <= w <= high:
                return self.data["h1_late_keymap"]["%d-%d" % (low, high)]
        raise ValueError("%s seconds is not a first-half late window" % window)

    def cell_for(self, half, window, diff):
        """'neutral', 'h1_late:<bucket>' (a label that cannot parse as a
        need), a late cell id, or 'OT'. A trailing overtime offense uses the
        late trail1_3 cell at the overtime clock's own time label (labelled
        inference: the trailing team must score)."""
        pre = self.data["preregistration"]
        if half == "OT":
            if diff < 0:
                return self.data["cell_map"]["%s|trail1_3" % self.time_label(min(window, pre["neutral_over_seconds"]))]
            return "OT"
        if half == 1 and window <= self.H1_LATE_SECONDS:
            return "h1_late:" + self.h1_key(window)
        if half == 2 and window <= pre["neutral_over_seconds"]:
            return self.data["cell_map"]["%s|%s" % (self.time_label(window), self.need(diff))]
        return "neutral"

    # ---- feasibility -------------------------------------------------------------

    # The kernel's sack-loss draw floor for a drive with a free snap
    # (kernel.lay_out and runtime.chains draw sack losses from 3 to 10 yards).
    SACK_LOSS_FLOOR = 3

    def sack_order_feasible(self, category, t, spot):
        """Batch B5 (found by the A6 sweep): a drive with no first down and a
        free snap takes each sack for at least SACK_LOSS_FLOOR yards, so
        some k of its s sacks must fit before its gains without leaving the
        field (spot + 3k <= 99) and the rest after them without the gains
        reaching the line to gain (net + 3(s - k) < the opening distance).
        Drives with a first-down series, kneels, no free snap or no sack
        are left to chains.chain_feasible."""
        T = self.T
        sacks, kneels = t[T["sacks"]], t[T["kneel_yards"]]
        if not sacks or kneels or t is ZERO_TUPLE or category in ("touchdown", "safety"):
            return True
        free, _, _, _ = self.fixed_yardage(category, t)
        if free <= 0:
            return True
        lengths = chains.last_series_lengths(category, 0)
        if t[T["plays"]] > max(lengths):
            return True
        net = self.adapt(category, t, spot)[0]
        dist0 = spot - chains.line_to_gain(spot)
        floor = self.SACK_LOSS_FLOOR
        return any(spot + floor * k <= 99 and net + floor * (sacks - k) < dist0 for k in range(sacks + 1))

    def static_feasible(self, category, t, spot):
        if not FieldPositionModel.static_feasible(self, category, t, spot):
            return False
        if not self.sack_order_feasible(category, t, spot):
            return False
        if category == "clock" and t is not ZERO_TUPLE:
            # R7: a clock expiry keeps its real end decision zone.
            end = self.adapt(category, t, spot)[1]
            if self.decision_zone(end) != self.decision_zone(t[self.T["end"]]):
                return False
        return True

    def spike_ok(self, t, left):
        """R14 spike rule: `left` is the window time after the tuple's own
        end (w - own); its last spike came that many seconds plus its own
        last-spike-to-end seconds before the window's end."""
        T = self.T
        if not t[T["spikes"]]:
            return True
        return left + t[T["last_spike_to_end"]] <= self.SPIKE_WINDOW

    # ---- W3: early field goals (kernel 2014.6, batch B6) ------------------------------------

    KICK_CATEGORY = {"field_goal_attempt": "field_goal", "punt": "punt"}

    def kick_length(self, category):
        """Mean seconds from a drive's last scrimmage snap to its kick snap,
        pooled over the last snap's kind, by kick (the artifact's W5a
        kick-length table); 0 for a category that is not a kick."""
        return self._kick_length.get(self.KICK_CATEGORY.get(category), 0)

    def kick_snap_clock(self, category, t, window):
        """The window clock at a kick drive's kick snap: the window less the
        drive's own seconds, plus the kick length (clipped to the drive's own
        seconds, so a short drive's kick is never stamped before its start)."""
        own = self.own_seconds(t)
        return window - own + min(self.kick_length(category), own)

    def early_fg_ok(self, t, window, overtime, ends_window, walk_off=False):
        """W3: may this field-goal tuple kick before fourth down? Yes when the
        drive ends its window; or, in regulation, when its kick-snap clock is
        at most EARLY_FG_SECONDS (43 s, the pre-divergence maximum,
        2012_15_SF_NE); or, in overtime, when a made kick ends the game
        (`walk_off`, the kernel's per-game context)."""
        if ends_window:
            return True
        if overtime:
            return bool(walk_off)
        return self.kick_snap_clock("field_goal_attempt", t, window) <= self.EARLY_FG_SECONDS

    def fourth_down_fg_feasible(self, t, spot):
        """W3: can this field-goal tuple, replayed from `spot`, be laid out
        with the kick on fourth down (runtime.chains.fourth_down_fg_feasible)?
        Memoised per tuple and spot under the base."""
        key = (id(t), spot)
        try:
            return self._fg4_cache[key]
        except KeyError:
            pass
        T = self.T
        net = self.adapt("field_goal_attempt", t, spot)[0]
        ok = chains.fourth_down_fg_feasible(plays=t[T["plays"]], net=net, spot=spot, kneel_yards=t[T["kneel_yards"]],
                                            sacks=t[T["sacks"]], runs=t[T["runs"]])
        self._fg4_cache[key] = ok
        return ok

    OVERTIME_REGIMES = ("ot", "fit_ot")

    def fg_tuple_admitted(self, t, spot, window, regime, ends_window, extra):
        """W3 (profile flag early_fg_v2 in `extra`): a field-goal tuple is
        admitted only when its kick is early by early_fg_ok or a fourth-down
        layout exists at the spot. The specification names tuples whose real
        kick came before fourth down; the same test is applied to a tuple
        that really kicked on fourth down, because relocation keeps its end
        spot and can hand a three-snap drive more than its opening distance
        (a first down, so no fourth-down kick): the sweep found every W3
        fallback in such tuples, and the kernel holds every non-early kick
        to fourth down whatever the real down."""
        if not (extra or {}).get("early_fg_v2"):
            return True
        if t is ZERO_TUPLE or t[self.T["term_down"]] not in (1, 2, 3, 4):
            return True
        if self.early_fg_ok(t, window, regime in self.OVERTIME_REGIMES, ends_window,
                            (extra or {}).get("walk_off_fg", False)):
            return True
        return self.fourth_down_fg_feasible(t, spot)

    def ends_window(self, regime, category, t):
        if str(regime).startswith("fit"):
            return False
        return FieldPositionModel.ends_window(self, regime, category, t)

    def _dynamic(self, tuples, category, regime, window, spot=None, extra=None):
        """Clock filters of a schema-3 regime: a window-ending tuple (a real
        final in h1_late and late; a clock final in overtime) must be time
        feasible; any other tuple must fit (s < w); a fit regime ("fit_h1",
        "fit_late", "fit_ot") takes non-final tuples only; the late terminal
        bucket rule applies in late and fit_late; the spike rule applies in
        every regime. Batch B6 (W3): with `spot` and `extra` holding
        early_fg_v2, a field-goal tuple is admitted by fg_tuple_admitted."""
        T = self.T
        fit = str(regime).startswith("fit")
        late = regime in ("late", "fit_late")
        early_fg = category == "field_goal_attempt" and spot is not None and (extra or {}).get("early_fg_v2")
        out = []
        for t in tuples:
            if fit:
                if t[T["final"]]:
                    continue
                ends = False
            else:
                ends = self.ends_window(regime, category, t)
            if ends:
                if not self.time_feasible(t, window):
                    continue
                bucket_left, left = 0, window - self.own_seconds(t)
            else:
                seconds = self.scaled_seconds(t)
                if seconds >= window:
                    continue
                bucket_left = left = window - seconds
            if late and category in FOURTH_DOWN_CATEGORIES and terminal_bucket(bucket_left) != t[T["term_bucket"]]:
                continue
            if not self.spike_ok(t, left):
                continue
            if early_fg and not self.fg_tuple_admitted(t, spot, window, regime, ends, extra):
                continue
            out.append(t)
        return tuple(out)

    # ---- pools ------------------------------------------------------------------------------

    def _pool(self, pool_id, category):
        pools = self.data["pools"]
        kind, key = pool_id
        if kind == "neutral":
            return pools["neutral"][key][CATEGORIES.index(category)]
        if kind in V3_OT_POOLS:
            return pools[kind][category]
        return pools[kind][key][category]

    def _counts(self, pool_id):
        data = self.data
        kind, key = pool_id
        if kind == "neutral":
            return dict(zip(CATEGORIES, data["neutral_counts"][key]))
        if kind in V3_OT_POOLS:
            return data[kind + "_counts"]
        if kind in ("late_union", "h1_late_union"):
            cells = self._need_cells(key) if kind == "late_union" else sorted(data["h1_late_counts"])
            table = data["late_counts" if kind == "late_union" else "h1_late_counts"]
            out = {c: 0 for c in CATEGORIES}
            for cell in cells:
                for c, n in table[cell].items():
                    out[c] += n
            return out
        return data[kind + "_counts"][key]

    def _members(self, pool_id, category):
        kind, key = pool_id
        if kind == "late_union":
            return [t for cell in self._need_cells(key) for t in self.data["pools"]["late"][cell][category]]
        if kind == "h1_late_union":
            return [t for cell in sorted(self.data["pools"]["h1_late"]) for t in self.data["pools"]["h1_late"][cell][category]]
        return list(self._pool(pool_id, category))

    def _matched(self, tuples, window, width):
        T = self.T
        return tuple(t for t in tuples if abs(t[T["t0"]] - window) <= width)

    def _window_counts(self, window, width):
        """{category: real h1_late drives whose own start lies within `width`
        seconds of the window} (P(category | t0 near w) up to a constant)."""
        out = {}
        for c in CATEGORIES:
            starts = self._h1_starts[c]
            out[c] = bisect.bisect_right(starts, window + width) - bisect.bisect_left(starts, window - width)
        return out

    def _rungs(self, pool_id, category, spot):
        """Spot-feasible tuples per rung (same bin, same zone); memoised per
        (pool, category, spot): bounded, since a time match filters the
        union's rungs at draw time instead of keying the cache by window."""
        key = (pool_id, category, spot)
        try:
            return self._rungs_cache[key]
        except KeyError:
            pass
        T = self.T
        data = self.data
        b, z = self.start_bin(spot), self.zone(spot)
        kind, pool_key = pool_id
        if kind == "neutral":
            index = CATEGORIES.index(category)
            same = [t for j in data["neutral_ladder"][pool_key][index] for t in data["pools"]["neutral"][j][index]]
            wider = [t for j in range(len(data["neutral_counts"]))
                     if self.zone(data["preregistration"]["start_bins"][j][0]) == z
                     for t in data["pools"]["neutral"][j][index]]
        else:
            members = self._members(pool_id, category)
            same = [t for t in members if self.start_bin(t[T["start"]]) == b]
            wider = [t for t in members if self.zone(t[T["start"]]) == z]
        out = tuple(tuple(t for t in rung if self.static_feasible(category, t, spot)) for rung in (same, wider))
        self._rungs_cache[key] = out
        return out

    def eligible(self, pool_id, category, spot, regime, window, match=None, extra=None):
        """Feasible tuples by the ladder (same bin, then same zone). With a
        time match the rungs are the h1_late union's, cached per (category,
        spot) and filtered by |t0 - w| <= match at draw time (bounded
        cache); the late need-union rungs are unchanged. `extra` carries the
        per-game context the clock filters read (W3)."""
        if match is not None:
            for rung in self._rungs(("h1_late_union", None), category, spot):
                feasible = self._dynamic(self._matched(rung, window, match), category, regime, window, spot, extra)
                if feasible:
                    return feasible
            return ()
        # The ladder of FieldPositionModel.eligible, with the W3 context.
        for rung in self._rungs(pool_id, category, spot):
            feasible = self._dynamic(rung, category, regime, window, spot, extra)
            if feasible:
                return feasible
        if NEED_UNION_RUNGS and regime == "late" and pool_id[0] == "late":
            union = ("late_union", cell_need(pool_id[1]))
            for rung in self._rungs(union, category, spot):
                feasible = self._dynamic(rung, category, regime, window, spot, extra)
                if feasible:
                    return feasible
            feasible = self._dynamic(self._any_start(union, category, spot), category, regime, window, spot, extra)
            if feasible:
                return feasible
        return ()

    def draw_options(self, pool_id, regime, spot, window, match=None, extra=None):
        if match is not None:
            counts = self._window_counts(window, match)
        else:
            counts = self._counts(pool_id)
        options = {c: self.eligible(pool_id, c, spot, regime, window, match, extra)
                   for c in CATEGORIES if counts.get(c, 0)}
        return counts, options

    def _reference(self, pool_id):
        kind, key = pool_id
        if kind == "late":
            return ("late_union", cell_need(key))
        if kind in ("h1_late", "h1_late_union"):
            return ("h1_late_union", None)
        return pool_id

    def zone_likelihood(self, reference, spot_zone):
        cache_key = (reference, spot_zone)
        try:
            return self._zone_cache[cache_key]
        except KeyError:
            pass
        T = self.T
        by_cat = {c: self._members(reference, c) for c in CATEGORIES}
        a = ZONE_SMOOTHING
        total = sum(len(m) for m in by_cat.values())
        in_zone = sum(1 for m in by_cat.values() for t in m if self.zone(t[T["start"]]) == spot_zone)
        base = (in_zone + a) / (total + 3 * a)
        out = {c: ((sum(1 for t in m if self.zone(t[T["start"]]) == spot_zone) + a) / (len(m) + 3 * a)) / base
               for c, m in by_cat.items()}
        self._zone_cache[cache_key] = out
        return out

    def _timeout_members(self, pool_id, counts, match, window):
        members = {c: self._members(pool_id if match is None else ("h1_late_union", None), c)
                   for c in counts if counts.get(c, 0)}
        if match is not None:
            members = {c: list(self._matched(m, window, match)) for c, m in members.items()}
        return members

    def _timeout_options(self, pool_id, counts, options, timeouts, key, diagnostics, members=None):
        """The kernel 2014.1 ladder over `members` (the pool's, or a time
        match's, tuples by category)."""
        if members is None:
            members = {c: self._members(pool_id, c) for c in counts if counts.get(c, 0)}
        for level in range(3):
            matching = {c: [t for t in m if self.timeout_match(level, t, timeouts, key)] for c, m in members.items()}
            if sum(len(m) for m in matching.values()) < MIN_TIMEOUT_POOL:
                continue
            weights, narrowed = {}, {}
            for c, m in matching.items():
                if not members[c]:
                    continue
                weights[c] = counts[c] * len(m) / len(members[c])
                feasible = options.get(c, ())
                narrowed[c] = tuple(t for t in feasible if self.timeout_match(level, t, timeouts, key)) or feasible
                if feasible and narrowed[c] is feasible and diagnostics is not None:
                    diagnostics["timeout_tuple_widened"] = diagnostics.get("timeout_tuple_widened", 0) + 1
            if any(weights.get(c) and narrowed.get(c) for c in weights):
                if diagnostics is not None:
                    diagnostics["timeout_level_%d" % level] = diagnostics.get("timeout_level_%d" % level, 0) + 1
                return weights, narrowed, level
        if diagnostics is not None:
            diagnostics["timeout_level_3"] = diagnostics.get("timeout_level_3", 0) + 1
        return counts, options, 3

    def held_preference(self, pool, timeouts):
        """W5b: the tuples whose real clubs used no more timeouts than the
        branch clubs hold (offense, defense); None when there are none."""
        T = self.T
        held_off, held_def = timeouts
        ok = tuple(t for t in pool if (t[T["off_timeouts_used"]] or 0) <= held_off
                   and (t[T["def_timeouts_used"]] or 0) <= held_def)
        return ok or None

    def sack_rate_base(self):
        made, n = self.data["band_centres"]["sacks_per_dropback"]["pooled"]
        return made / n

    def category_mix_v3(self, counts, edge, options, int_edge=0.0, transfer=None):
        """category_mix with the R14 transfer: `transfer` = (from, to) moves
        the first category's probability to the second (after the edge,
        before masking)."""
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
        if transfer is not None:
            source, target = transfer
            probs = dict(probs)
            probs[target] = probs.get(target, 0.0) + probs.get(source, 0.0)
            probs[source] = 0.0
        masked = {c: (p if counts.get(c, 0) > 0 and options.get(c) else 0.0) for c, p in probs.items()}
        mass = sum(masked.values())
        return {c: v / mass for c, v in masked.items()} if mass > 0 else {}

    def _draw_from(self, rng, pool_id, regime, spot, window, edge, timeouts=None, key="def", diagnostics=None,
                   exclude=(), clock_regime=None, extra=None, match=None, transfer=None):
        counts, options = self.draw_options(pool_id, clock_regime or regime, spot, window, match, extra)
        options = {c: (() if c in exclude else v) for c, v in options.items()}
        if ZONE_CONDITIONING and regime in self.TIMEOUT_REGIMES:
            ratio = self.zone_likelihood(self._reference(pool_id), self.zone(spot))
            counts = {c: n * ratio[c] for c, n in counts.items()}
        level = None
        kept = set()
        if timeouts is not None and regime in self.TIMEOUT_REGIMES:
            counts, options, level = self._timeout_options(
                pool_id, counts, options, timeouts, key, diagnostics,
                members=self._timeout_members(pool_id, counts, match, window))
            preferred = {}
            for c, pool in options.items():
                held = self.held_preference(pool, timeouts) if pool else None
                if pool and held is None:
                    kept.add(c)
                preferred[c] = held or pool
            options = preferred
        extra = extra or {}
        probs = self.category_mix_v3(counts, edge, options, extra.get("int", 0.0), transfer)
        if not probs:
            return None
        category = drive_model.draw_category(rng, probs)
        if category in kept and diagnostics is not None:
            _bump(diagnostics, "timeout_unavailable_kept")
        return category, self.draw_tuple(rng, options[category], extra.get("sack", 0.0)), level

    def _clock_fallback(self, rng, tuples, spot, window):
        T = self.T
        bucket = h1_bucket_index(window)
        by_distance = {}
        for t in tuples:
            if t[T["final"]] and self.static_feasible("clock", t, spot) and self.time_feasible(t, window) \
                    and self.spike_ok(t, window - self.own_seconds(t)):
                by_distance.setdefault(abs(h1_bucket_index(t[T["t0"]]) - bucket), []).append(t)
        if not by_distance:
            return None
        pool = by_distance[min(by_distance)]
        return pool[rng.randrange(len(pool))]

    def _h1_late_clock_tuples(self):
        return self._members(("h1_late_union", None), "clock")

    def _h1_clock_tuples(self):
        raise NotImplementedError("schema 3 retires the h1_final pools")

    def zero_cell_categories(self, pool_id):
        """R10: the categories with no real drive in the time cell drawn."""
        counts = self._counts(pool_id)
        return tuple(c for c in CATEGORIES if not counts.get(c, 0))

    def _fit_or_expire(self, rng, spot, window, edge, cell, regime, diagnostics, fit_regime, fit_counter, extra=None,
                       exclude=()):
        """A drive that fits inside the window (non-final, not a clock drive,
        `exclude` masked) under the regime's fit filters, else a zero-play
        expiry (inside the allowance: clock_expiry_zero; beyond it:
        fallback_zero_tuple, which the coherence audit flags)."""
        clock_regime = self.FIT_REGIMES[regime]
        pool_id = ("neutral", self.start_bin(spot))
        drawn = self._draw_from(rng, pool_id, "fit", spot, window, edge, exclude=("clock",) + tuple(exclude),
                                clock_regime=clock_regime, extra=extra)
        if drawn is not None:
            _bump(diagnostics, fit_counter)
            return Drive(drawn[0], drawn[1], self.scaled_seconds(drawn[1]), False, cell, fit_regime,
                         fallback="h1_fit" if fit_counter == "h1_fit_fallback" else "fit",
                         pool_id=pool_id, clock_regime=clock_regime)
        if window <= CLOCK_EXPIRY_ALLOWANCE:
            _bump(diagnostics, "clock_expiry_zero")
            return self.ending_drive("clock", ZERO_TUPLE, window, cell, regime, fallback="expiry")
        _bump(diagnostics, "fallback_zero_tuple")
        return self.ending_drive("clock", ZERO_TUPLE, window, cell, regime, fallback="zero")

    def _finish(self, drawn, window, cell, regime, pool_id, fallback=None, match=None):
        category, t, level = drawn
        if self.ends_window(regime, category, t):
            return self.ending_drive(category, t, window, cell, regime, fallback=fallback, timeout_level=level,
                                     pool_id=pool_id, clock_regime=regime, match_width=match)
        return Drive(category, t, self.scaled_seconds(t), False, cell, regime, fallback=fallback,
                     timeout_level=level, pool_id=pool_id, clock_regime=regime, match_width=match)

    def draw_drive(self, rng, spot, half, window, diff, edge, diagnostics, timeouts=None, extra=None):
        """One possession under the schema-3 regimes (class docstring).

        `extra` carries the matchup shifts ("int", "sack") and the per-game
        context the kernel passes (no module state): "ot_history_empty"
        (required for a tied overtime draw) and "walk_off_fg" (read by a
        later batch)."""
        extra = extra or {}
        cell = self.cell_for(half, window, diff)
        key = "off" if diff < 0 else "def"
        if half == "OT" and diff > 0:
            _bump(diagnostics, "ot_leading_offense")
        if half == 1 and window > self.H1_LATE_SECONDS:
            # R17: no redirect over H1_LATE_SECONDS; the fitting neutral draw.
            pool_id = ("neutral", self.start_bin(spot))
            drawn = self._draw_from(rng, pool_id, "fit", spot, window, edge, exclude=("clock",),
                                    clock_regime="fit_h1", extra=extra)
            if drawn is not None:
                return Drive(drawn[0], drawn[1], self.scaled_seconds(drawn[1]), False, cell, "h1_neutral",
                             pool_id=pool_id, clock_regime="fit_h1")
            _bump(diagnostics, "h1_neutral_infeasible")
            t = self._clock_fallback(rng, self._h1_late_clock_tuples(), spot, window)
            if t is not None:
                _bump(diagnostics, "fallback_clock_tuple")
                return self.ending_drive("clock", t, window, cell, "h1_late", fallback="clock_tuple")
            return self._fit_or_expire(rng, spot, window, edge, cell, "h1_neutral", diagnostics, "h1_neutral",
                                       "h1_fit_fallback", extra=extra)
        if half == 1:
            bucket = ("h1_late", self.h1_key(window))
            narrow, wide = self.TIME_MATCH
            for pool_id, match in ((bucket, narrow), (bucket, wide), (bucket, None), (("h1_late_union", None), None)):
                drawn = self._draw_from(rng, pool_id, "h1_late", spot, window, edge, timeouts, key, diagnostics,
                                        extra=extra, match=match)
                if drawn is not None:
                    if match != narrow:
                        _bump(diagnostics, "h1_late_match_fallback" if match == wide else
                              "h1_late_cell_fallback" if pool_id is bucket else "h1_late_union_fallback")
                    return self._finish(drawn, window, cell, "h1_late", pool_id, match=match)
            _bump(diagnostics, "h1_late_infeasible")
            t = self._clock_fallback(rng, self._h1_late_clock_tuples(), spot, window)
            if t is not None:
                _bump(diagnostics, "fallback_clock_tuple")
                return self.ending_drive("clock", t, window, cell, "h1_late", fallback="clock_tuple")
            return self._fit_or_expire(rng, spot, window, edge, cell, "h1_late", diagnostics, "h1_late",
                                       "h1_fit_fallback", extra=extra)
        transfer, primary_exclude = None, ()
        if cell == "neutral":
            pool_id = ("neutral", self.start_bin(spot))
            drawn = self._draw_from(rng, pool_id, "h2_neutral", spot, window, edge, extra=extra)
            if drawn is not None:
                seconds = self.scaled_seconds(drawn[1])
                if window - seconds <= self.data["preregistration"]["neutral_over_seconds"]:
                    _bump(diagnostics, "h2_neutral_into_late")
                return Drive(drawn[0], drawn[1], seconds, False, cell, "h2_neutral",
                             pool_id=pool_id, clock_regime="h2_neutral")
            need_label = self.need(diff)
            regime, pool_id, masked = "late", ("late_union", need_label), ()
        elif half == "OT" and diff < 0:
            # R14: a trailing overtime offense, the late trail1_3 cell.
            regime, pool_id, need_label = "ot", ("late", cell), cell_need(cell)
            transfer, primary_exclude = ("punt", "downs"), ("punt",)
            masked = self.zero_cell_categories(pool_id)
        elif cell == "OT":
            if "ot_history_empty" not in extra:
                raise ValueError("a tied overtime draw needs the overtime history context")
            regime, need_label = "ot", "tied"
            pool_id = ("ot_first" if extra["ot_history_empty"] else "ot_sudden", None)
            masked = self.zero_cell_categories(pool_id)
        else:
            regime, pool_id, need_label = "late", ("late", cell), cell_need(cell)
            masked = self.zero_cell_categories(pool_id)
        drawn = self._draw_from(rng, pool_id, regime, spot, window, edge, timeouts, key, diagnostics,
                                exclude=primary_exclude, extra=extra, transfer=transfer)
        fallback = None
        if drawn is None and pool_id[0] != "late_union":
            fallback = "need_union"
            _bump(diagnostics, "fallback_need_union")
            pool_id = ("late_union", need_label)
            drawn = self._draw_from(rng, pool_id, regime, spot, window, edge, timeouts, key, diagnostics,
                                    exclude=tuple(masked) + primary_exclude, extra=extra, transfer=transfer)
        if drawn is None:
            if "clock" not in masked:
                t = self._clock_fallback(rng, self._late_clock_tuples(need_label), spot, window)
                if t is not None:
                    _bump(diagnostics, "fallback_clock_tuple")
                    return self.ending_drive("clock", t, window, cell, regime, fallback="clock_tuple")
            return self._fit_or_expire(rng, spot, window, edge, cell, regime, diagnostics, regime,
                                       "fallback_fit_drive", extra=extra, exclude=tuple(masked) + primary_exclude)
        return self._finish(drawn, window, cell, regime, pool_id, fallback=fallback)

    def tuple_locator(self, category, t):
        data = self.data
        c = CATEGORIES.index(category)
        for j, bin_pools in enumerate(data["pools"]["neutral"]):
            for i, m in enumerate(bin_pools[c]):
                if m is t:
                    return ["neutral", j, i]
        for kind in V3_POOLS:
            for key, cells in data["pools"][kind].items():
                for i, m in enumerate(cells[category]):
                    if m is t:
                        return [kind, key, i]
        for kind in V3_OT_POOLS:
            for i, m in enumerate(data["pools"][kind][category]):
                if m is t:
                    return [kind, None, i]
        return None

    def locate_tuple(self, category, locator):
        data = self.data
        try:
            kind, key, i = locator
            if kind == "neutral":
                return data["pools"]["neutral"][key][CATEGORIES.index(category)][i]
            if kind in V3_OT_POOLS:
                return data["pools"][kind][category][i]
            if kind not in V3_POOLS:
                return None
            return data["pools"][kind][key][category][i]
        except (KeyError, IndexError, TypeError, ValueError):
            return None

    def snap_seconds_range(self):
        if self._snap_range is None:
            T = self.T
            out = {0: (0, 0)}
            for category in CATEGORIES:
                for t in _v3_tuples(self.data, category):
                    n, sec = t[T["plays"]], self.scaled_seconds(t)
                    low, high = out.get(n, (sec, sec))
                    out[n] = (min(low, sec), max(high, sec))
            self._snap_range = out
        return self._snap_range

    def _resample_rungs(self, drawn, spot, regime, window, extra=None):
        """(pool id, match width, feasible tuples) in widening order for a
        layout resample: the drawn rung (its time match), then, schema 3
        (batch B5, found by the A6 sweep: a deep start can leave a thin cell
        rung with no other legal drive), the wider pools of the same
        category and regime: the first-half bucket cell and union, the late
        need union and any start of that union, or any start of the drawn
        pool. Category, regime and clock filters never change."""
        pool_id, category, match = drawn.pool_id, drawn.category, drawn.match_width
        yield pool_id, match, self.eligible(pool_id, category, spot, regime, window, match, extra)
        kind = pool_id[0]
        if kind == "h1_late":
            if match is not None:
                yield pool_id, None, self.eligible(pool_id, category, spot, regime, window, extra=extra)
            yield (("h1_late_union", None), None,
                   self.eligible(("h1_late_union", None), category, spot, regime, window, extra=extra))
            union = ("h1_late_union", None)
        elif kind in ("late", "late_union"):
            union = ("late_union", cell_need(pool_id[1]) if kind == "late" else pool_id[1])
            yield union, None, self.eligible(union, category, spot, regime, window, extra=extra)
        else:
            union = pool_id
        yield union, None, self._dynamic(self._any_start(union, category, spot), category, regime, window, spot, extra)

    def resample_drive(self, rng, drawn, spot, window, exclude=(), timeouts=None, extra=None):
        """resample_drive on the drawn rung, time match and regime, widening
        to the same category's wider pools when the rung has no other legal
        drive (_resample_rungs); with `timeouts`, the W5b preference applies
        to the candidates. `extra` is the kernel's per-game context (W3)."""
        if drawn.pool_id is None or drawn.tuple is ZERO_TUPLE:
            return None
        regime = drawn.clock_regime or drawn.regime
        skip = [drawn.tuple] + list(exclude)
        candidates, pool_id, match = [], drawn.pool_id, drawn.match_width
        for pool_id, match, rung in self._resample_rungs(drawn, spot, regime, window, extra):
            candidates = [t for t in rung if not any(t is x or t == x for x in skip)]
            if drawn.consumes_window:
                candidates = [t for t in candidates if self.ends_window(regime, drawn.category, t)]
            else:
                candidates = [t for t in candidates if self.scaled_seconds(t) < window
                              and not self.ends_window(regime, drawn.category, t)]
            if candidates:
                break
        if timeouts is not None and regime in self.TIMEOUT_REGIMES and candidates:
            candidates = list(self.held_preference(candidates, timeouts) or candidates)
        if not candidates:
            return None
        t = candidates[rng.randrange(len(candidates))]
        fields = dict(fallback=drawn.fallback, redirected=drawn.redirected, timeout_level=drawn.timeout_level,
                      pool_id=pool_id, clock_regime=drawn.clock_regime, match_width=match)
        if drawn.consumes_window:
            return self.ending_drive(drawn.category, t, window, drawn.cell, drawn.regime, **fields)
        return Drive(drawn.category, t, self.scaled_seconds(t), False, drawn.cell, drawn.regime, **fields)

    # ---- transitions -------------------------------------------------------------------------

    def kickoff(self, rng):
        """A real own-35 kickoff (2011 onward) the receiving club takes over."""
        return self._kick_record(rng, self._kick_pools["kickoff_pool"], 35)

    def free_kick(self, rng):
        """A real safety free kick from the 20 the receiving club takes over."""
        return self._kick_record(rng, self._kick_pools["free_kick_pool"], 20)

    def punt(self, rng, los):
        P = self.PUNT

        def ok(record):
            if record[P["touchback"]]:
                return los <= record[P["los"]]
            start = 100 - los + record[P["gross"]] - record[P["return_yards"]] + record[P["enforcement"]]
            return 1 <= start <= 99
        candidates = self._nearest(self._punt_pool, P["los"], los, ok)
        record = candidates[rng.randrange(len(candidates))]
        touchback = bool(record[P["touchback"]])
        gross = los if touchback else record[P["gross"]]
        ret = 0 if touchback else record[P["return_yards"]]
        enforcement = record[P["enforcement"]]
        start = 80 + enforcement if touchback else 100 - los + gross - ret + enforcement
        return {"los": los, "outcome": record[P["outcome"]], "gross": gross, "return_yards": ret,
                "enforcement": enforcement, "next_start": start, "touchback": touchback,
                "record_los": record[P["los"]]}


MODEL_CLASSES = {SCHEMA: FieldPositionModel, SCHEMA_V3: FieldPositionModelV3}


def model_class(schema):
    """The field-position reader of an artifact schema; an unknown schema raises."""
    try:
        return MODEL_CLASSES[schema]
    except KeyError:
        raise ValueError("no field-position reader for schema %r" % (schema,)) from None


# ---- the 2012 base's model (module-level API) ---------------------------------------------

def model():
    """The 2012 calibration base's field-position model."""
    from .calibration_base import BASE_2012
    return BASE_2012.field_position()


def _raw():
    from .calibration_base import BASE_2012
    return BASE_2012.raw("field_position")


def load():
    """The validated 2012 artifact; treat as read-only."""
    return model().load()


def start_bin(spot):
    return model().start_bin(spot)


def zone(spot):
    return model().zone(spot)


def need(diff):
    return model().need(diff)


def time_label(seconds):
    return model().time_label(seconds)


def cell_for(half, window, diff):
    return model().cell_for(half, window, diff)


def h1_key(window):
    return model().h1_key(window)


def decision_zone(los):
    return model().decision_zone(los)


def scaled_seconds(t):
    return drive_model.scaled_seconds(t)


def adapt(category, t, spot):
    return model().adapt(category, t, spot)


def fixed_yardage(category, t):
    return model().fixed_yardage(category, t)


def static_feasible(category, t, spot):
    return model().static_feasible(category, t, spot)


def _pool(pool_id, category):
    return model()._pool(pool_id, category)


def _counts(pool_id):
    return model()._counts(pool_id)


def _need_cells(need_label):
    return model()._need_cells(need_label)


def _rungs(pool_id, category, spot):
    return model()._rungs(pool_id, category, spot)


def _static(pool_id, category, spot):
    return model()._static(pool_id, category, spot)


def ends_window(regime, category, t):
    return model().ends_window(regime, category, t)


def time_feasible(t, window):
    return model().time_feasible(t, window)


def own_seconds(t):
    """A tuple's own elapsed seconds on the 2012 base's clock scale."""
    return 0 if t is ZERO_TUPLE else scaled_seconds(t)


def snap_seconds_range():
    return model().snap_seconds_range()


def _dynamic(tuples, category, regime, window):
    return model()._dynamic(tuples, category, regime, window)


def eligible(pool_id, category, spot, regime, window):
    return model().eligible(pool_id, category, spot, regime, window)


def _any_start(pool_id, category, spot):
    return model()._any_start(pool_id, category, spot)


def draw_options(pool_id, regime, spot, window):
    return model().draw_options(pool_id, regime, spot, window)


def timeout_match(level, t, timeouts, key):
    return model().timeout_match(level, t, timeouts, key)


def _members(pool_id, category):
    return model()._members(pool_id, category)


def _timeout_options(pool_id, counts, options, timeouts, key, diagnostics):
    return model()._timeout_options(pool_id, counts, options, timeouts, key, diagnostics)


def _reference(pool_id):
    return model()._reference(pool_id)


def zone_likelihood(reference, spot_zone):
    return model().zone_likelihood(reference, spot_zone)


def sack_rate_base():
    return model().sack_rate_base()


def tuple_weights(pool, sack_shift):
    return model().tuple_weights(pool, sack_shift)


def draw_tuple(rng, pool, sack_shift=0.0):
    return model().draw_tuple(rng, pool, sack_shift)


def _draw_from(rng, pool_id, regime, spot, window, edge, timeouts=None, key="def", diagnostics=None,
               exclude=(), clock_regime=None, extra=None):
    return model()._draw_from(rng, pool_id, regime, spot, window, edge, timeouts, key, diagnostics,
                              exclude, clock_regime, extra)


def _clock_fallback(rng, tuples, spot, window):
    return model()._clock_fallback(rng, tuples, spot, window)


def _late_clock_tuples(need_label):
    return model()._late_clock_tuples(need_label)


def _h1_clock_tuples():
    return model()._h1_clock_tuples()


def ending_drive(category, t, window, cell, regime, **kw):
    return model().ending_drive(category, t, window, cell, regime, **kw)


def _fit_or_expire(rng, spot, window, edge, cell, regime, diagnostics, fit_regime, fit_counter, extra=None):
    return model()._fit_or_expire(rng, spot, window, edge, cell, regime, diagnostics, fit_regime, fit_counter,
                                  extra)


def draw_drive(rng, spot, half, window, diff, edge, diagnostics, timeouts=None, extra=None):
    return model().draw_drive(rng, spot, half, window, diff, edge, diagnostics, timeouts, extra)


def tuple_locator(category, t):
    return model().tuple_locator(category, t)


def locate_tuple(category, locator):
    return model().locate_tuple(category, locator)


def resample_drive(rng, drawn, spot, window, exclude=()):
    return model().resample_drive(rng, drawn, spot, window, exclude)


def _kick_record(rng, pool, spot):
    return model()._kick_record(rng, pool, spot)


def kickoff(rng):
    return model().kickoff(rng)


def free_kick(rng):
    return model().free_kick(rng)


def _nearest(pool, key_index, spot, ok):
    return model()._nearest(pool, key_index, spot, ok)


def punt(rng, los):
    return model().punt(rng, los)


def turnover(rng, kind, end):
    return model().turnover(rng, kind, end)
