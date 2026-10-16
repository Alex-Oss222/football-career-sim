"""Kernel 2014.6 batch B13 (R16a, R16b): the replayed drive's own yard split.

Every earlier kernel split a replayed drive's free yards between its runs and
its passes with two gauss weights centred on constant league means, decided
each attempt's completion with a Bernoulli draw, drew each open sack's loss
as randint(3, 10) and spread each kind's yards over its snaps with uniform
random weights (runtime.play_detail._allocate). The real drive's own split
does not follow those constants: runs were over-credited on the big-net
drives, the yards per carry ran about 4.6 against a real 4.23, and the
per-snap shape (short runs, losing runs) was wrong.

Under the profile flags ``yard_split`` (R16a) and ``snap_values`` (R16b,
needing yard_split) the drive carries its own real record, the B3b
annotations of the schema-3 tuple (library/data/2010_2014w4_nfl_field_position_model.json,
``annotation_rules.yardage``):

- R16a: the real rushing yards R, passing yards P, completions and sack
  losses. The relocation delta d (the change in the drive's free yardage
  when its start spot moves, plus any yardage the replay does not carry) is
  split between the kinds: the runs take round(d x |R| / (|R| + |P|)) (half
  each when both are 0; round half away from zero), all of d when the drive
  has no completion and none when it has no run (library/2014_6_pre_build_specification.md,
  section 5, Yardage). The completions are fixed in every rung: exactly the
  real count is completed (the terminal catch counts as one), pass yards are
  0 when the real drive completed none, and a completion the layout must
  force (a drive with no run and no completion moved from its real spot) is
  counted (relocation_forced_completion). The sack losses are the real ones
  in every rung (no redraw); a drive whose sacks alone carry its yardage
  keeps its real losses moved by the difference the net requires, evenly
  (the installed fit applied to the difference).
- R16b: the real run values and completion values replace the uniform
  allocation. The terminal value stays on the terminal slot; the other
  values are the real drive's own, their order shuffled on the drive's
  chain-layout stream, where the uniform allocation drew (the design
  prototype's rule). Each kind's delta then goes to its non-terminal snaps
  by the gains-proportional rule (gains_proportional).

The terminal snap is never changed by the delta: a kind whose only snap is
the terminal one hands its share to the other kind (counted
real_split_rerouted); a drive with no non-terminal snap of either kind moves
its terminal snap (counted real_split_terminal_moved, as is any later repair
rung that moves it). With R11 (batch B11) shipped, the drive's penalty yards
are its replayed records and never enter the scrimmage values. The
possession stream is unchanged: the placeholder gauss and randint draws are
still taken under their exact earlier conditions (runtime.kernel._yard_split).

No club, player or game identity is read: the split depends only on the
drawn tuple, its start spot and its category, the same for every club.
"""
from __future__ import annotations

from dataclasses import dataclass

MODEL = "real-split-v1"
SCHEMA = "2010-2014w4-yardage-v1"
# The B3b host kinds of a terminal scrimmage snap, as layout kinds.
TERM_KINDS = {"run": "run", "complete": "catch", "sack": "sack"}
# Published-run bins (non-kneel runs by yards): losing, no gain, 1-3, 4-9,
# 10-19, 20 or more (the band rows' shape bins).
RUN_BINS = ("loss", "zero", "1-3", "4-9", "10-19", "20+")
LONG_COMPLETION = 20
# The gains-proportional rule's short-gain threshold (specification).
SHORT_GAIN = 3
FIELDS = ("rush_yards", "pass_yards", "completions", "sack_losses", "run_values", "completion_values", "term_snap")


@dataclass(frozen=True)
class RealSplit:
    """A replayed drive's own yardage, as the split reads it.

    rush and run_values are the free runs (a safety's terminal run left out,
    its value is the spot's); losses are the open sacks' real losses in snap
    order as positive yards lost (a safety's terminal sack left out);
    completion_values are the completions' gross yards in snap order;
    term_kind is the layout kind of the real terminal scrimmage snap (run,
    catch or sack; None for a safety, whose terminal is fixed by the spot,
    and for every other kind) and term_value its yards."""
    rush: int
    passing: int
    completions: int
    losses: tuple
    run_values: tuple
    completion_values: tuple
    term_kind: object
    term_value: object

    def record(self):
        return {"rush": self.rush, "pass": self.passing, "completions": self.completions}


def of_tuple(fpm, category, t):
    """The tuple's RealSplit, or None for a tuple without the schema-3
    yardage annotations (ZERO_TUPLE, an earlier artifact)."""
    if any(fpm.value(t, name) is None for name in FIELDS[:6]):
        return None
    runs = [int(v) for v in fpm.value(t, "run_values")]
    completion_values = [int(v) for v in fpm.value(t, "completion_values")]
    losses = [-int(v) for v in fpm.value(t, "sack_losses")]
    term = fpm.value(t, "term_snap")
    term_kind = TERM_KINDS.get(term[0]) if term else None
    term_value = int(term[1]) if term else None
    if category == "safety":
        kind = fpm.value(t, "safety_term_kind")
        if kind == "run" and runs:
            runs = runs[:-1]
        elif kind == "sack" and losses:
            losses = losses[:-1]
        term_kind = term_value = None
    return RealSplit(rush=sum(runs), passing=sum(completion_values), completions=int(fpm.value(t, "completions")),
                     losses=tuple(losses), run_values=tuple(runs), completion_values=tuple(completion_values),
                     term_kind=term_kind, term_value=term_value)


def round_half_away(x):
    """round(x), halves away from zero (the specification's round)."""
    from math import floor
    return int(floor(x + 0.5)) if x >= 0 else -int(floor(-x + 0.5))


def kind_split(free_total, real, *, usable, free_runs, terminal_kind=None):
    """R16a: (pass_yards, rush_free, rerouted) of a drive's free total.

    `terminal_kind` is the layout terminal of the drive when the kernel knows
    it (catch or run for a touchdown, the lost entry's kind for a lost
    fumble; None otherwise): a kind whose only snap is that terminal hands
    its share of the delta to the other kind, so the terminal snap keeps its
    real value (rerouted True)."""
    if usable + free_runs == 0:
        return 0, 0, False
    if not usable:
        return 0, free_total, False
    if not free_runs:
        # A relocated drive with no run and no completion forces one
        # completion in the layout (counted there).
        return free_total, 0, False
    if real.completions <= 0:
        # Fixed completions: no completion carries pass yards.
        return 0, free_total, False
    rush, passing = real.rush, real.passing
    delta = free_total - (rush + passing)
    scale = abs(rush) + abs(passing)
    d_rush = round_half_away(delta * abs(rush) / scale) if scale else round_half_away(delta / 2)
    d_pass = delta - d_rush
    other_runs = free_runs - (1 if terminal_kind == "run" else 0)
    other_completions = real.completions - (1 if terminal_kind == "catch" else 0)
    rerouted = False
    if d_rush and other_runs <= 0 and other_completions > 0:
        d_rush, d_pass, rerouted = 0, delta, True
    elif d_pass and other_completions <= 0 and other_runs > 0:
        d_rush, d_pass, rerouted = delta, 0, True
    return passing + d_pass, rush + d_rush, rerouted


def _largest_remainder(total, weights, caps=None):
    """Integer shares of a non-negative total proportional to the weights,
    largest-remainder rounding (ties to the earlier snap), never above a cap."""
    weight_sum = sum(weights)
    if total <= 0 or weight_sum <= 0:
        return [0] * len(weights)
    shares = [total * w // weight_sum for w in weights]
    remainders = [total * w % weight_sum for w in weights]
    left = total - sum(shares)
    order = sorted(range(len(weights)), key=lambda i: (-remainders[i], i))
    for i in order:
        if not left:
            break
        if remainders[i] and (caps is None or shares[i] < caps[i]):
            shares[i] += 1
            left -= 1
    return shares


def gains_proportional(values, delta):
    """R16a: a kind's delta over its non-terminal snaps (the specification's
    gains-proportional rule). For delta > 0 each snap weighs
    max(gain - 3, 0) + 1; for delta < 0 each weighs max(gain - 3, 0) and loses
    at most that much; largest-remainder rounding within those caps; what
    cannot be placed moves one yard at a time over the longest snaps.
    Returns the new values (their sum is sum(values) + delta)."""
    values = [int(v) for v in values]
    if not delta or not values:
        return values
    if delta > 0:
        weights = [max(v - SHORT_GAIN, 0) + 1 for v in values]
        return [v + a for v, a in zip(values, _largest_remainder(delta, weights))]
    need = -delta
    weights = [max(v - SHORT_GAIN, 0) for v in values]
    place = min(need, sum(weights))
    take = _largest_remainder(place, weights, caps=weights)
    values = [v - t for v, t in zip(values, take)]
    for _ in range(need - place):
        longest = max(range(len(values)), key=lambda i: (values[i], -i))
        values[longest] -= 1
    return values


def assign(rng, slots, real_values, total, terminal_slot=None, terminal_matches=False):
    """R16b: {slot: value} of one kind (completions or free runs), or None
    when the slots do not match the real values (the caller's fallback).

    `slots` are the kind's value slots in snap order; `terminal_slot` the one
    that is the drive's terminal snap (None when the kind has none);
    `terminal_matches` that the real terminal snap was of this kind, so its
    value (the kind's last real value) stays on the terminal slot. The other
    real values are shuffled over the other slots on `rng` (the layout
    stream); the kind's delta (total less the real values' sum) goes to the
    non-terminal slots by gains_proportional, and onto the terminal slot only
    when the kind has no other slot."""
    slots = list(slots)
    real_values = [int(v) for v in real_values]
    if len(slots) != len(real_values):
        return None
    fixed = {}
    pool = list(real_values)
    others = list(slots)
    if terminal_slot is not None and terminal_matches and terminal_slot in slots:
        fixed[terminal_slot] = pool.pop()
        others = [i for i in slots if i != terminal_slot]
    rng.shuffle(pool)
    out = dict(zip(others, pool))
    out.update(fixed)
    delta = int(total) - sum(real_values)
    if delta:
        targets = [i for i in slots if i != terminal_slot]
        if targets:
            for i, value in zip(targets, gains_proportional([out[i] for i in targets], delta)):
                out[i] = value
        elif slots:
            out[slots[-1]] += delta
    return out


def published(kinds, completed, values):
    """(run bins, completions of LONG_COMPLETION yards or more) of a laid-out
    possession: its non-kneel runs by RUN_BINS and its long completions."""
    bins = [0] * len(RUN_BINS)
    long_completions = 0
    for kind, done, value in zip(kinds, completed, values):
        value = int(value)
        if kind == "run":
            if value < 0:
                bins[0] += 1
            elif value == 0:
                bins[1] += 1
            elif value <= 3:
                bins[2] += 1
            elif value <= 9:
                bins[3] += 1
            elif value <= 19:
                bins[4] += 1
            else:
                bins[5] += 1
        elif kind in ("att", "catch") and done and value >= LONG_COMPLETION:
            long_completions += 1
    return bins, long_completions


def segment_record(real, layout, terminal_value_kinds=("run", "catch")):
    """The replayed split of one laid-out drive as published: the real rush,
    pass and completions, the delta of each kind the adopted plan carries
    ([rush, pass]), the completions the layout forced beyond the real count,
    and whether the terminal snap's value differs from the real one."""
    if real is None or layout is None:
        return None
    kinds, completed, values = layout["kinds"], layout["completed"], layout["values"]
    laid_completions = sum(1 for k, c in zip(kinds, completed) if k in ("att", "catch") and c)
    terminal = layout.get("terminal")
    moved = False
    if terminal in terminal_value_kinds and terminal == real.term_kind and kinds and kinds[-1] == terminal:
        moved = int(values[-1]) != real.term_value
    out = real.record()
    out.update(delta=[int(layout["rush_free"]) - real.rush, int(layout["pass_yards"]) - real.passing],
               forced=max(0, laid_completions - real.completions), terminal_moved=moved)
    return out


class YardageModel:
    """The B13 band centres of a base's yardage artifact
    (library/data/2010_2014w4_yardage.json, built by
    scripts/research/build_2010_2014_yardage.py with its --check)."""

    def __init__(self, data):
        if data.get("schema") != SCHEMA:
            raise ValueError("yardage artifact schema %r is not %s" % (data.get("schema"), SCHEMA))
        self.data = data
        self.centres = data["band_centres"]
