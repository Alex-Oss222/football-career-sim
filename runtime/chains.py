"""Kernel 2014.4 (defect register Tier 1 item 3): down, distance and the chains
derived from the drive's own ordered snaps.

Before 2014.4 a replayed 2012 drive kept its real chain counts and its real
fourth-down down and distance even when a new start spot changed its net
yardage, so a no-first-down drive's fourth-down distance and its first-down
count could contradict the snaps it published. Here the published state is
walked from the snap ledger itself:

* a drive opens 1st & min(10, distance to the goal line) (goal to go when the
  line to gain is at or past the goal line);
* each scrimmage snap moves the spot by its own yards (a sack is negative, an
  incompletion and a spike gain nothing, a kneel is a down with its own
  yards); a snap that reaches the line to gain is a first down (a touchdown
  always is), otherwise the down advances and the distance shrinks by the
  gain;
* a snap that loses possession (interception, lost fumble, the safety snap)
  credits no first down, whatever yards it carries (2012: all 23 non-scoring
  drives of 10+ yards without a first down end in a lost fumble);
* a fourth-down snap that falls short turns the ball over on downs and must
  be the drive's last snap.

The drive's first downs and third- and fourth-down attempts and conversions
are counted from that walk. Penalties have no ledger rows (they are team
counters only; defect register item 11), so a 2012 drive's penalty first
downs stay a documented counter (chains[1]) and are the only chain value not
reconciled to the ledger.

Penalty first downs are not double counted (item 3 open issue 1). The real
drive's penalty yards moved the ball but have no snap, so the replayed snaps
carry that ground themselves and the walk can credit a scrimmage first down
where the real drive got its line to gain from a flag. When the walk finds
more scrimmage first downs than the 2012 tuple's scrimmage count c0, each
excess walked first down absorbs one of the tuple's penalty first downs c1:

    penalty = max(0, c1 - max(0, walked - c0))

(`penalty_first_downs`). A walk at or below c0 keeps all c1; the published
total never exceeds max(walked, c0 + c1) and never falls below walked.

The layout that fixes each snap's kind, completion and yards and their order
therefore feeds team counters. It runs on its own keyed stream
(CHAIN_LAYOUT_TAG, per event, drive and offence) that neither consumes the
possession stream nor depends on the public snap-detail stream, which still
names the players (runtime.play_detail).

Nothing here reads a club identity or which side is the protagonist.
"""
from __future__ import annotations

import hashlib
import json
import math
import random

CHAIN_LAYOUT_TAG = "chain-layout-v1"
# Published on every possession (append-only) so receipts with and without a
# snap ledger can tell a derived chain state from a copied 2012 one.
CHAIN_MODEL = "ledger-walk-v1"
TURNOVER_TERMINALS = ("interception", "fumble_lost", "safety")
# Pre-registered search limits (fixed before any sample was inspected; they
# bound work, not outcomes): value draws per tier, randomized restarts per
# draw, depth-first nodes per restart, one-yard equalization steps.
DRAWS = 4
ALT_DRAWS = 2
ALT_PLANS = 8
SPLIT_SHIFTS = (3, 6, 10, 15, 20)
RESTARTS = 4
NODE_BUDGET = 3000
EXACT_BUDGET = 600
REPAIR_STEPS = 120
# Last rung (added at the candidate acceptance, September 30, 2026, after
# three drives in 806 games kept an unconstrained order): when every plan
# above fails, the plan is enumerated in a fixed order instead of drawn: each
# sack-loss combination in the kernel's own 3-10 range (at most
# LOSS_RUNG_LIMIT; sampled from the drive's stream beyond it) crossed with a
# passing-against-rushing shift of 0, 1 or 2 yards either way. The drive's
# net, snap counts and terminal never move. The first legal order wins.
LOSS_RUNG_LIMIT = 64


def penalty_first_downs(scrimmage_real, penalty_real, walked):
    """The drive's published penalty first downs: the 2012 tuple's penalty
    count less any walked scrimmage first downs beyond the tuple's own
    scrimmage count (those walked first downs already carry the flag's
    ground; module docstring)."""
    c0, c1, walked = int(scrimmage_real), int(penalty_real), int(walked)
    return max(0, c1 - max(0, walked - c0))


def line_to_gain(spot):
    """The line to gain (yards from the goal line) for a series from `spot`;
    0 means goal to go."""
    return max(0, int(spot) - 10)


def walk(start_spot, values, turnover_last=False):
    """Walk one drive's ordered scrimmage snaps (their yards) from its start.

    Returns per-snap states before each snap (down, ydstogo, goal_to_go, los)
    with the snap's first_down flag, the drive's [first downs, 3rd att, 3rd
    conv, 4th att, 4th conv], the state after the last snap (None when the
    drive failed on downs), the index of a failed fourth-down snap and any
    snaps that follow it (breaks)."""
    down, spot = 1, int(start_spot)
    ltg = line_to_gain(spot)
    rows, failed, breaks = [], None, []
    fd = a3 = c3 = a4 = c4 = 0
    n = len(values)
    for i, value in enumerate(values):
        if failed is not None:
            breaks.append(i)
        before = {"down": down, "ydstogo": spot - ltg, "goal_to_go": ltg == 0, "los": spot}
        new = spot - int(value)
        lost = turnover_last and i == n - 1
        gained = not lost and new <= ltg
        if down == 3:
            a3 += 1
            c3 += gained
        elif down == 4:
            a4 += 1
            c4 += gained
        if gained:
            fd += 1
            down = 1
            ltg = line_to_gain(new)
        else:
            if down >= 4 and not lost and failed is None:
                failed = i
            down += 1
        spot = new
        rows.append(dict(before, first_down=gained))
    state = None
    if failed is None and down <= 4:
        state = {"down": down, "ydstogo": spot - ltg, "goal_to_go": ltg == 0, "los": spot}
    return {"rows": rows, "chains": [fd, a3, c3, a4, c4], "state": state,
            "failed": failed, "breaks": breaks}


STATE_FIELDS = ("down", "ydstogo", "goal_to_go", "los")


# ---- Kernel 2014.6 batch B11 (R11): ledger-walk-v2 -----------------------------------------
#
# Under the profile flag penalty_records a drive's walk takes an event list: its
# scrimmage snaps, each with the clauses enforced after it (runtime.penalties
# AFTER_SNAP), and its no-play and pre-kick penalty rows. A step is
# ("s", yards, pen) or ("p", pen), pen = (accepted signed yards, automatic
# first down, the credited record) or None (runtime.penalties.compiled).
#
# * A snap moves the spot by its own yards and is a scrimmage first down when it
#   reaches the line to gain, as in walk(); its third- or fourth-down attempt
#   is the snap's.
# * Its clauses are then enforced from the spot it reached: a defensive foul is
#   a first down by penalty when it is automatic for its type or its yards
#   reach the line to gain, and the series restarts from the new spot; an
#   offensive foul moves the ball back and keeps the down and the line to
#   gain. On a snap that made its own first down an automatic foul is still a
#   first down by penalty, as the source flags it (482 of the 1,136 drive
#   plays flagged first_down_penalty also carry the rushing or passing flag,
#   library/data/2010_2014w4_penalties.json first_down_convention); a foul
#   that only reaches the new line is not.
#   The snap's third- or fourth-down conversion is its own gain (the source's
#   third_down_converted). A fourth-down snap short of the line is a turnover
#   on downs unless its own clause gave the first down.
# * A no-play row keeps the down: a defensive foul is a first down by penalty by
#   the same rule, an offensive foul lengthens the distance; it is never a
#   third- or fourth-down attempt.
# * The drive's penalty first downs (chains[1]) are the walked count of rows that
#   gave one (one record per row carries the flag).
CHAIN_MODEL_V2 = "ledger-walk-v2"
CHAIN_LAYOUT_TAG_V2 = "chain-layout-v2"


def _enforce(spot, down, ltg, pen, gained):
    """(new spot, down, line to gain, first down by penalty) after one row's clauses."""
    y, auto, _ = pen
    new = spot - int(y)
    first = False
    if auto or (y > 0 and new <= ltg):
        first = bool(auto) or not gained
        down, ltg = 1, line_to_gain(new)
    return new, down, ltg, first


def walk_steps(start_spot, steps, turnover_last=False):
    """The v2 walk of one drive's steps (above). Returns the walk() fields over
    the scrimmage snaps ("rows": the state before each snap and its scrimmage
    first down; "chains" [first downs, 3rd att, 3rd conv, 4th att, 4th conv];
    "state"; "failed" and "breaks" as snap indices) plus "steps" (the state
    before every step, its scrimmage first down and its first down by penalty),
    "penalty_first_downs" and "pre_tail_state" (the state after the last snap,
    before any trailing penalty row; None when there is none to keep)."""
    down, spot = 1, int(start_spot)
    ltg = line_to_gain(spot)
    rows, out_steps, breaks = [], [], []
    failed = None
    fd = a3 = c3 = a4 = c4 = pfd = 0
    snaps = sum(1 for step in steps if step[0] == "s")
    seen = 0
    pre_tail = None
    for step in steps:
        if failed is not None and step[0] == "s":
            breaks.append(seen)
        before = {"down": down, "ydstogo": spot - ltg, "goal_to_go": ltg == 0, "los": spot}
        first = False
        if step[0] == "s":
            value, pen = int(step[1]), step[2]
            new = spot - value
            seen += 1
            lost = turnover_last and seen == snaps
            gained = not lost and new <= ltg
            was = down
            if down == 3:
                a3 += 1
                c3 += gained
            elif down == 4:
                a4 += 1
                c4 += gained
            if gained:
                fd += 1
                down, ltg = 1, line_to_gain(new)
            else:
                down += 1
            spot = new
            if pen is not None and not lost:
                spot, down, ltg, first = _enforce(spot, down, ltg, pen, gained)
            if was >= 4 and not gained and not first and not lost and failed is None:
                failed = seen - 1
            rows.append(dict(before, first_down=gained))
            out_steps.append(dict(before, first_down=gained, penalty_first_down=first))
            if seen == snaps:
                pre_tail = (None if failed is not None or down > 4 else
                            {"down": down, "ydstogo": spot - ltg, "goal_to_go": ltg == 0, "los": spot})
        else:
            spot, down, ltg, first = _enforce(spot, down, ltg, step[1], False)
            out_steps.append(dict(before, first_down=False, penalty_first_down=first))
        pfd += first
    state = None
    if failed is None and down <= 4:
        state = {"down": down, "ydstogo": spot - ltg, "goal_to_go": ltg == 0, "los": spot}
    if not snaps:
        pre_tail = {"down": 1, "ydstogo": int(start_spot) - line_to_gain(start_spot),
                    "goal_to_go": line_to_gain(start_spot) == 0, "los": int(start_spot)}
    return {"rows": rows, "chains": [fd, a3, c3, a4, c4], "state": state, "failed": failed, "breaks": breaks,
            "steps": out_steps, "penalty_first_downs": pfd, "pre_tail_state": pre_tail}


def fourth_down_state_steps(category, start_spot, steps):
    """fourth_down_state over v2 steps: the state at the kick (after every row,
    a pre-kick row included) or, on downs, before the failed fourth-down snap."""
    w = walk_steps(start_spot, steps)
    snaps = sum(1 for step in steps if step[0] == "s")
    if category == "downs":
        if w["failed"] is None or w["failed"] != snaps - 1:
            return None
        return {k: w["rows"][w["failed"]][k] for k in STATE_FIELDS}
    if not steps:
        spot = int(start_spot)
        return {"down": 1, "ydstogo": spot - line_to_gain(spot), "goal_to_go": line_to_gain(spot) == 0, "los": spot}
    return w["state"]


def terminal_state_steps(category, start_spot, steps):
    """terminal_state over v2 steps (the same fallback to the last step's state)."""
    state = fourth_down_state_steps(category, start_spot, steps)
    if state is not None:
        return state
    w = walk_steps(start_spot, steps)
    if w["steps"]:
        return {k: w["steps"][-1][k] for k in STATE_FIELDS}
    spot = int(start_spot)
    return {"down": 1, "ydstogo": spot - line_to_gain(spot), "goal_to_go": line_to_gain(spot) == 0, "los": spot}


def layout_steps(layout):
    """The v2 steps of a laid-out drive: its sequence of snaps (each with the
    clauses riding on it) and penalty rows; a layout without a sequence (no
    penalty records) is its snaps alone."""
    from .penalties import compiled
    sequence = layout.get("sequence")
    values = layout["values"]
    if sequence is None:
        return [("s", int(v), None) for v in values]
    events = layout.get("events") or ()
    attached = layout.get("attached") or {}
    out = []
    for tag, ref in sequence:
        if tag == "s":
            groups = attached.get(ref)
            records = tuple(r for g in groups for r in g.records) if groups else ()
            out.append(("s", int(values[ref]), compiled(records) if records else None))
        else:
            out.append(("p", compiled(events[ref].records)))
    return out


def layout_penalty_yards(layout):
    """The accepted yards of a laid-out drive's replayed records."""
    if layout.get("sequence") is None:
        return 0
    events = layout.get("events") or ()
    total = sum(r.yards for groups in (layout.get("attached") or {}).values() for g in groups for r in g.records)
    total += sum(r.yards for tag, ref in layout["sequence"] if tag == "p" for r in events[ref].records)
    return total


def ledger_steps(rows):
    """The v2 steps of one drive's ledger rows (its scrimmage rows with their
    clause lists, its penalty rows), in ledger order, from the published
    records: each accepted record's signed yards, its automatic first down
    and the record holding the row's first-down flag."""
    from .penalties import PENALTY_ROW
    out = []
    for row in rows:
        kind = row.get("play_type")
        if kind in ("pass", "run"):
            out.append(("s", row.get("result_yards", 0), _ledger_pen(row.get("penalties"))))
        elif kind == PENALTY_ROW:
            out.append(("p", _ledger_pen(row.get("penalties")) or (0, False, None)))
    return out


def _ledger_pen(entries):
    if not entries:
        return None
    yards = sum(int(e.get("penalty_yards") or 0) for e in entries if e.get("status") == "accepted")
    auto = any(e.get("status") == "accepted" and e.get("penalty_side") == "defense" and e.get("auto_first_down")
               for e in entries)
    pick = next((i for i, e in enumerate(entries) if e.get("first_down")), None)
    return (yards, auto, pick)


def fourth_down_state(category, start_spot, values):
    """(down, ydstogo, goal_to_go, los) before a punt, field-goal or downs
    terminal: the state after the last scrimmage snap, or for downs the state
    before the failed fourth-down snap. None when the walk has no such state
    (a downs drive that never failed, a kick after a failed fourth down)."""
    w = walk(start_spot, values)
    if category == "downs":
        if w["failed"] is None or w["failed"] != len(values) - 1:
            return None
        return {k: w["rows"][w["failed"]][k] for k in STATE_FIELDS}
    if not values:
        spot = int(start_spot)
        return {"down": 1, "ydstogo": spot - line_to_gain(spot), "goal_to_go": line_to_gain(spot) == 0, "los": spot}
    return w["state"]


def terminal_state(category, start_spot, values):
    """The published fourth-down state (kernel). Equal to fourth_down_state;
    only when no legal layout existed (chain_layout_failed, counted and
    reported by the coherence classes) it falls back to the last snap's own
    state so the possession still carries one."""
    state = fourth_down_state(category, start_spot, values)
    if state is not None:
        return state
    w = walk(start_spot, values)
    if w["rows"]:
        return {k: w["rows"][-1][k] for k in STATE_FIELDS}
    spot = int(start_spot)
    return {"down": 1, "ydstogo": spot - line_to_gain(spot), "goal_to_go": line_to_gain(spot) == 0, "los": spot}


def annotate(rows, walked, fourth_down=None):
    """Write the walk onto one drive's ledger rows (append-only fields): each
    scrimmage snap gets its down, ydstogo, goal_to_go and first_down; a
    punt, field-goal or downs row also gets goal_to_go from the published
    fourth-down state (it already carries down, ydstogo and los)."""
    scrimmage = [r for r in rows if r.get("play_type") in ("pass", "run")]
    for row, state in zip(scrimmage, walked["rows"]):
        row["down"] = state["down"]
        row["ydstogo"] = state["ydstogo"]
        row["goal_to_go"] = state["goal_to_go"]
        row["first_down"] = state["first_down"]
    if fourth_down is not None:
        for row in rows:
            if row.get("play_type") in ("punt", "field_goal") or (
                    row.get("play_type") == "possession_end" and row.get("reason") == "downs"):
                row["goal_to_go"] = fourth_down["goal_to_go"]


# ---- static feasibility (tuple selection) ------------------------------------

def last_series_lengths(category, kneels):
    """Snaps allowed after the drive's last first down, terminal snap included."""
    if category == "punt":
        lengths = (3,)
    elif category == "downs":
        lengths = (4,)
    elif category in ("field_goal_attempt", "clock"):
        lengths = (0, 1, 2, 3)
    else:
        lengths = (1, 2, 3, 4)
    floor = kneels + (1 if category not in ("punt", "downs", "field_goal_attempt", "clock") else 0)
    return tuple(n for n in lengths if n >= floor)


def chain_feasible(category, *, plays, net, spot, kneel_yards=(), sacks=0, runs=0, terminal_value=0,
                   last_lengths=None, penalty=None):
    """Can a drive of `plays` scrimmage snaps netting `net` from `spot` be
    ordered into a legal chain walk that ends in its category's terminal
    state? A necessary counting and yardage condition, evaluated before the
    snap values exist. `last_lengths` overrides the category's allowed
    last-series lengths (kernel 2014.6 W3: a field goal held to fourth down
    allows exactly three snaps after the last first down, fourth_down_fg_feasible):

    * the snaps after the last first down fit the category (punt: 3, so the
      punt comes on 4th down; downs: 4, the last one short; field goal and
      clock: 0-3; a touchdown or turnover: its terminal snap on downs 1-4);
    * every other snap belongs to a series that ends in a first down, at most
      four snaps each, so f >= ceil(m / 4) first downs; each needs a series
      starting outside the 10 (a goal-to-go series cannot convert without a
      touchdown) and at least ten yards;
    * a drive with no first down gains less than its opening distance before
      any terminal snap; its kneels are fixed losses taken after that
      ground was gained, so the free snaps before them carry the net less
      the kneel yards (a 3-snap punt netting 8 after kneels of -3 ran for
      11, which is a first down and a punt on third down).

    Kernel 2014.6 batch B11 (R11): `penalty` (runtime.penalties
    .static_summary of the replayed records) makes the condition the
    penalty-aware one. A first down may come from a penalty: each automatic
    first down the search may seat lowers the scrimmage first downs needed
    by one; the yards before the last series are bounded by the net less the
    pre-kick rows' yards plus every offensive penalty yard the search may
    seat (a loss after a first down); with no first down at all, the
    scrimmage snaps' own gains (the net less every record's yards) must stay
    short of the opening distance lengthened by the movable offensive
    yards, unless a defensive record could restart the series. Each
    scrimmage first down the drive still needs (beyond the automatic ones)
    takes ten yards from its series' snaps and non-automatic defensive
    records, so the snaps' positive gains, at most the scrimmage net plus
    every loss the value model can draw (ten per sack, the base's largest
    run loss per run, the kneels), plus those records' yards must reach ten
    per first down.
    """
    spot, net, kneels = int(spot), int(net), len(kneel_yards)
    kneel_sum = sum(int(y) for y in kneel_yards)
    dist0 = spot - line_to_gain(spot)
    if category == "touchdown":
        pre = None
    elif category == "fumble_lost":
        # The fumbled snap is one of the drive's own snaps: a fumbled sack
        # is one of its `sacks` and may lose up to ten like any other, a
        # fumbled run may lose up to ten, a fumbled completion's share of a
        # positive passing total is never negative. Its loss is bounded
        # with the last series below (October 1, 2026: a separate allowance
        # here counted a lone fumbled sack twice, so a 6-snap, 1-sack
        # fumble netting -5 from the 18 passed although no snap order can
        # reach the first down its six snaps need).
        pre = net
    elif category == "safety":
        pre = net - terminal_value
    else:
        pre = net
    lengths = last_series_lengths(category, kneels)
    if last_lengths is not None:
        lengths = tuple(n for n in last_lengths if n in lengths)
    auto = penalty["auto_movable"] if penalty else 0
    for length in lengths:
        if length > plays:
            continue
        m = plays - length
        if m == 0:
            if pre is None or category == "fumble_lost":
                return True
            if penalty is None:
                if pre - kneel_sum < dist0:
                    return True
                continue
            # No series boundary before the last series: the snaps' own gains
            # plus every defensive record's yards stay short of the opening
            # distance lengthened by the movable offensive yards, or one
            # defensive record before the first snap is itself a first down
            # (automatic, or as long as the opening distance) and the rest
            # stay short of a fresh ten.
            gains = pre - penalty["yards"] - kneel_sum + penalty["def_movable"] + penalty["def_tail"]
            if gains < dist0 + penalty["off_movable"]:
                return True
            if penalty["opener"] is not None and gains - penalty["opener"] < 10 + penalty["off_movable"]:
                return True
            continue
        f = math.ceil(m / 4)
        if spot <= 10 * max(0, f - auto):
            continue
        if pre is not None:
            in_last = max(0, length - kneels - (0 if category in ("punt", "downs", "field_goal_attempt", "clock") else 1))
            lowest_last = kneel_sum - 10 * min(sacks, in_last)
            if category == "fumble_lost":
                # The terminal snap joins the series' losses: a fumbled sack
                # is one of `sacks` (min(sacks, in_last + 1)); a fumbled run
                # adds its own ten to the non-terminal sacks.
                lowest_last = kneel_sum - 10 * max(min(sacks, in_last + 1), (1 if runs else 0) + min(sacks, in_last))
            before_last = pre if penalty is None else pre - penalty["tail_yards"] + penalty["off_movable"]
            if before_last - min(0, lowest_last) < 10 * max(0, f - auto):
                continue
            if penalty is not None:
                room = max(0, pre - penalty["yards"] + 10 * sacks + int(penalty.get("run_loss", 10)) * runs
                           - kneel_sum)
                if room + penalty["def_nonauto"] < 10 * max(0, f - auto):
                    continue
        return True
    return False


# Kernel 2014.6 batch B6 (W3): a field goal kicked on fourth down has exactly
# three scrimmage snaps after its last first down (downs 1, 2, 3, then the kick).
FG_FOURTH_DOWN_LAST_SERIES = (3,)


def fourth_down_fg_feasible(*, plays, net, spot, kneel_yards=(), sacks=0, runs=0, penalty=None):
    """Kernel 2014.6 (W3): can a field-goal drive of `plays` snaps netting
    `net` from `spot` be laid out with the kick on fourth down? The same
    counting and yardage condition as chain_feasible with the last series
    held to three snaps (a drive with fewer than three snaps cannot kick on
    fourth down)."""
    return chain_feasible("field_goal_attempt", plays=plays, net=net, spot=spot, kneel_yards=kneel_yards,
                          sacks=sacks, runs=runs, last_lengths=FG_FOURTH_DOWN_LAST_SERIES, penalty=penalty)


# ---- layout ------------------------------------------------------------------

def _stream(seed, *parts, tag=CHAIN_LAYOUT_TAG):
    payload = json.dumps([tag, *parts], separators=(",", ":")).encode()
    return random.Random(int.from_bytes(hashlib.sha256(seed + payload).digest(), "big"))


def resample_stream(seed, event_id, drive_no, offense, segment=None, tag=CHAIN_LAYOUT_TAG):
    """Kernel 2014.4 phase 2: the stream a drive's layout resample draws
    on (its replacement tuple, sack losses and yard split), keyed like the
    layout stream with its own tag so neither consumes the other. Kernel
    2014.6 batch B9F: a continuation segment n of a possession (after a
    fourth-down conversion) has its own, keyed by the segment as well; the
    drive's first segment (None) keeps the unchanged key. Kernel 2014.6
    batch B11: under penalty_records every layout stream carries
    CHAIN_LAYOUT_TAG_V2."""
    if segment is None:
        return _stream(seed, event_id, drive_no, offense, "layout-resample", tag=tag)
    return _stream(seed, event_id, drive_no, offense, "layout-resample", "segment", int(segment), tag=tag)


def _runs_clock(kind, completed, penalized=False):
    """A run, a sack or a completed pass leaves the clock running. Kernel 2014.6
    batch B11: the one clock rule for spikes and penalty rows (shared with
    runtime.play_detail._seat_spikes): an accepted foul stops it, so a spike
    never follows a penalty row or a snap with an accepted clause."""
    if penalized:
        return False
    return kind in ("run", "sack") or (kind in ("att", "catch") and completed)


# ---- Kernel 2014.6 batch B11 (R11): penalty items of the layout search ----------------------

def _penalized(records):
    return any(r.status == "A" for r in records)


def _resetter(pen):
    """A row that can give a first down without a snap (a defensive accepted
    clause with yards or an automatic first down)."""
    return pen is not None and (pen[0] > 0 or pen[1])


def _attach(rng, kinds, completed, terminal, groups, diagnostics):
    """{snap index: [Attach]}: each clause group of a counted snap rides on a
    laid-out snap of its host kind (a completion on a completed attempt, an
    incompletion on an incomplete one), drawn evenly on the layout stream
    among the snaps holding none yet; a group with no snap of its kind takes
    one of the same base kind, else any (counted penalty_host_fallback). The
    terminal snap of a touchdown or turnover drive holds none (its clauses
    are enforced after the possession and never reach here)."""
    from .penalties import HOST_KINDS
    last = len(kinds) - 1
    eligible = [i for i in range(len(kinds)) if not (terminal is not None and i == last)]
    taken = set()
    out = {}
    for group in groups:
        wanted = HOST_KINDS.get(group.host)

        def fits(i, strict=True):
            kind = kinds[i]
            if wanted is None:
                return True
            if kind not in wanted:
                return False
            if strict and group.host == "complete":
                return bool(completed[i])
            if strict and group.host == "incomplete":
                return not completed[i]
            return True

        pool = [i for i in eligible if i not in taken and fits(i)]
        if not pool:
            pool = [i for i in eligible if i not in taken and fits(i, strict=False)]
            if not pool:
                pool = [i for i in eligible if i not in taken] or list(eligible)
            if pool:
                diagnostics["penalty_host_fallback"] = diagnostics.get("penalty_host_fallback", 0) + 1
        if not pool:
            diagnostics["penalty_host_missing"] = diagnostics.get("penalty_host_missing", 0) + 1
            continue
        index = pool[rng.randrange(len(pool))]
        taken.add(index)
        out.setdefault(index, []).append(group)
    return out


def _snap_item(kinds, completed, values, i, attached):
    from .penalties import compiled
    groups = attached.get(i)
    if not groups:
        return ("s", kinds[i], bool(completed[i]), int(values[i]), None, ())
    records = tuple(r for g in groups for r in g.records)
    return ("s", kinds[i], bool(completed[i]), int(values[i]), compiled(records), records)


def _event_item(event):
    from .penalties import compiled
    return ("p", None, False, 0, compiled(event.records), tuple(event.records))


def _steps_of(items):
    return [("s", it[3], it[4]) if it[0] == "s" else ("p", it[4]) for it in items]


class _EventSearch:
    """Kernel 2014.6 batch B11: _Search over the movable snaps and the
    movable penalty rows of one drive (`items`; each a hashable tuple (tag,
    kind, completed, yards, compiled clauses, records)), followed by its
    fixed tail (`tail`: kneels, pre-kick rows, the terminal snap), with
    walk_steps as its state. The hard constraints are _Search's, plus: every
    record is enforced only where it is legal (runtime.penalties.legal) and
    leaves the ball in the field; the final-down pruning holds only while no
    row that can give a first down remains. Counts are [first downs, 3rd
    att, 3rd conv, 4th att, 4th conv, non-terminal 4th conv, first downs by
    penalty]; the caps and `exact` read the first six and five."""

    def __init__(self, rng, items, tail, start, *, final_down, downs, turnover_last, caps=None, exact=None,
                 spike_rule=True):
        self.rng, self.items, self.tail, self.start = rng, list(items), list(tail), start
        self.final_down, self.downs, self.turnover_last = final_down, downs, turnover_last
        self.caps = tuple(caps) if caps else (None,) * 6
        self.exact, self.spike_rule = tuple(exact) if exact else None, spike_rule
        self.tail_snaps = [sum(1 for it in self.tail[p + 1:] if it[0] == "s") for p in range(len(self.tail))]
        self.tail_resetters = [sum(1 for it in self.tail[p + 1:] if _resetter(it[4])) for p in range(len(self.tail))]
        self.n_tail_snaps = sum(1 for it in self.tail if it[0] == "s")
        self.n_tail_resetters = sum(1 for it in self.tail if _resetter(it[4]))

    def _down_ok(self, next_down, snaps_after, resetters_after):
        target = self.final_down
        if isinstance(target, int) and not resetters_after:
            if snaps_after != target - next_down and snaps_after < target:
                return False
        return True

    def _step(self, state, item, snaps_after, resetters_after):
        from .penalties import legal
        spot, down, ltg, running, counts = state
        tag, kind, completed, value, pen, records = item
        fd, a3, c3, a4, c4, mid4, pfd = counts
        if tag == "p":
            if records and not legal(records, spot):
                return None
            y, auto, _ = pen
            new = spot - y
            if not 1 <= new <= 99:
                return None
            if auto or (y > 0 and new <= ltg):
                down, ltg = 1, line_to_gain(new)
                pfd += 1
            if not self._down_ok(down, snaps_after, resetters_after):
                return None
            return (new, down, ltg, False, (fd, a3, c3, a4, c4, mid4, pfd))
        new = spot - value
        last_snap = snaps_after == 0
        lost = self.turnover_last and last_snap
        if not lost and not (last_snap and new == 0 and self.final_down == "td"):
            if not 1 <= new <= 99:
                return None
        if kind == "spike" and self.spike_rule and not running:
            return None
        gained = not lost and new <= ltg
        if gained and new <= 0 and not last_snap:
            return None
        was = down
        if down == 3:
            a3 += 1
            c3 += gained
        elif down == 4:
            a4 += 1
            c4 += gained
            mid4 += gained and not last_snap
        if gained:
            fd += 1
            down, ltg = 1, line_to_gain(new)
        else:
            down += 1
        first = False
        after = new
        if pen is not None and not lost:
            if not legal(records, new):
                return None
            y, auto, _ = pen
            after = new - y
            if not 1 <= after <= 99:
                return None
            if auto or (y > 0 and after <= ltg):
                first = not gained
                pfd += first
                down, ltg = 1, line_to_gain(after)
        if was == 4 and not gained and not first and not lost:
            if not (self.downs and last_snap):
                return None
        counts = (fd, a3, c3, a4, c4, mid4, pfd)
        for value_now, cap in zip(counts, self.caps):
            if cap is not None and value_now > cap:
                return None
        if not self._down_ok(down, snaps_after, resetters_after):
            return None
        return (after, down, ltg, _runs_clock(kind, completed, _penalized(records)), counts)

    def _finish(self, state):
        for position, item in enumerate(self.tail):
            state = self._step(state, item, self.tail_snaps[position], self.tail_resetters[position])
            if state is None:
                return False
        if isinstance(self.final_down, int) and state[1] != self.final_down:
            return False
        if self.exact is not None and state[4][:5] != self.exact:
            return False
        return True

    def run(self, budget=NODE_BUDGET):
        """One randomized search: an order of the movable item indices, or
        None, and whether the space was exhausted (_Search.run)."""
        nodes = [0]
        dead = set()
        start_state = (self.start, 1, line_to_gain(self.start), False, (0,) * 7)
        exhausted = [True]
        distinct = []
        for item in self.items:
            if item not in distinct:
                distinct.append(item)
        counts0 = tuple(sum(1 for item in self.items if item == d) for d in distinct)
        is_snap = [d[0] == "s" for d in distinct]
        is_reset = [_resetter(d[4]) for d in distinct]
        snaps0 = sum(n for n, s in zip(counts0, is_snap) if s)
        resets0 = sum(n for n, r in zip(counts0, is_reset) if r)

        def dfs(state, left, n_left, snaps_left, resets_left, path):
            nodes[0] += 1
            if nodes[0] > budget:
                exhausted[0] = False
                return None
            if not n_left:
                return path if self._finish(state) else None
            key = (state, left)
            if key in dead:
                return None
            order = [k for k, n in enumerate(left) if n]
            self.rng.shuffle(order)
            for k in order:
                snaps_after = snaps_left - is_snap[k] + self.n_tail_snaps
                resets_after = resets_left - is_reset[k] + self.n_tail_resetters
                nxt = self._step(state, distinct[k], snaps_after, resets_after)
                if nxt is None:
                    continue
                found = dfs(nxt, left[:k] + (left[k] - 1,) + left[k + 1:], n_left - 1, snaps_left - is_snap[k],
                            resets_left - is_reset[k], path + [k])
                if found is not None:
                    return found
                if nodes[0] > budget:
                    return None
            dead.add(key)
            return None

        picked = dfs(start_state, counts0, len(self.items), snaps0, resets0, [])
        found = None
        if picked is not None:
            pools = {i: [j for j, item in enumerate(self.items) if item == d] for i, d in enumerate(distinct)}
            found = [pools[k].pop(0) for k in picked]
        return found, exhausted[0]


def _score_steps(w, targets):
    """_score with the drive's first downs by penalty against the real drive's
    own count (c1)."""
    score = _score(w["chains"], targets)
    if targets:
        score += abs(w["penalty_first_downs"] - int(targets[1]))
    return score


class _Search:
    """Depth-first order search over the movable snaps with the chain walk as
    its state. Hard constraints: the running spot stays in the field, no
    fourth-down snap falls short except a downs drive's last snap, a spike
    follows a snap that left the clock running (kernel 2013.9) and the drive
    ends in its category's terminal down. Optional caps bound the walk's
    counts [first downs, 3rd att, 3rd conv, 4th att, 4th conv, non-terminal
    4th conv] from above; `exact` requires the first five to equal the real
    drive's own counts."""

    def __init__(self, rng, sig, n_mov, start, *, final_down, downs, turnover_last, caps=None, exact=None,
                 spike_rule=True):
        self.rng, self.sig, self.n_mov, self.start = rng, sig, n_mov, start
        self.final_down, self.downs, self.turnover_last = final_down, downs, turnover_last
        self.caps = tuple(caps) if caps else (None,) * 6
        self.exact, self.spike_rule = tuple(exact) if exact else None, spike_rule
        self.tail = list(range(n_mov, len(sig)))

    def _step(self, state, snap, remaining_after):
        total, down, ltg, running, counts = state
        kind, completed, value = snap
        spot = self.start - total
        new = spot - value
        last_snap = remaining_after == 0
        lost = self.turnover_last and last_snap
        if not lost and not (last_snap and new == 0 and self.final_down == "td"):
            if not 1 <= new <= 99:
                return None
        if kind == "spike" and self.spike_rule and not running:
            return None
        gained = not lost and new <= ltg
        if gained and new <= 0 and not last_snap:
            return None
        if down == 4 and not gained and not lost:
            if not (self.downs and last_snap):
                return None
        fd, a3, c3, a4, c4, mid4 = counts
        fd += gained
        if down == 3:
            a3 += 1
            c3 += gained
        elif down == 4:
            a4 += 1
            c4 += gained
            mid4 += gained and not last_snap
        counts = (fd, a3, c3, a4, c4, mid4)
        for value_now, cap in zip(counts, self.caps):
            if cap is not None and value_now > cap:
                return None
        next_down = 1 if gained else down + 1
        target = self.final_down
        if isinstance(target, int):
            if remaining_after != target - next_down and remaining_after < target:
                return None
        return (total + value, next_down, line_to_gain(new) if gained else ltg,
                _runs_clock(kind, completed), counts)

    def _finish(self, state):
        for position, index in enumerate(self.tail):
            state = self._step(state, self.sig[index], len(self.tail) - position - 1)
            if state is None:
                return False
        if isinstance(self.final_down, int) and state[1] != self.final_down:
            return False
        if self.exact is not None and state[4][:5] != self.exact:
            return False
        return True

    def run(self, budget=NODE_BUDGET):
        """One randomized search: an order of the movable indices, or None.
        Also reports whether the search space was exhausted (proof of no
        order) rather than stopped by the node budget."""
        nodes = [0]
        dead = set()
        start_state = (0, 1, line_to_gain(self.start), False, (0,) * 6)
        exhausted = [True]
        # The movable snaps as a multiset of distinct (kind, completed, yards).
        distinct = []
        for i in range(self.n_mov):
            if self.sig[i] not in distinct:
                distinct.append(self.sig[i])
        counts0 = tuple(sum(1 for i in range(self.n_mov) if self.sig[i] == d) for d in distinct)
        tail = len(self.tail)

        def dfs(state, left, n_left, path):
            nodes[0] += 1
            if nodes[0] > budget:
                exhausted[0] = False
                return None
            if not n_left:
                return path if self._finish(state) else None
            key = (state, left)
            if key in dead:
                return None
            order = [k for k, n in enumerate(left) if n]
            self.rng.shuffle(order)
            for k in order:
                nxt = self._step(state, distinct[k], n_left - 1 + tail)
                if nxt is None:
                    continue
                found = dfs(nxt, left[:k] + (left[k] - 1,) + left[k + 1:], n_left - 1, path + [k])
                if found is not None:
                    return found
                if nodes[0] > budget:
                    return None
            dead.add(key)
            return None

        picked = dfs(start_state, counts0, self.n_mov, [])
        found = None
        if picked is not None:
            pools = {d: [i for i in range(self.n_mov) if self.sig[i] == d] for d in distinct}
            found = [pools[distinct[k]].pop(0) for k in picked]
        return found, exhausted[0]


def _draw(rng, pd, category, terminal, runs, attempts, sacks, kneel_yards, spikes, pass_yards, rush_free,
          losses, safety_terminal, completion_rate, usage_values=None, real=None, replay_values=False):
    """Kinds, completions and per-snap values, as runtime.play_detail._layout
    draws them (the movable snaps first, then kneels and the terminal snap).
    `usage_values` is the calibration base's usage table (the negative-run
    rate and loss distribution; the 2012 base's when None).

    Kernel 2014.6 batch B13 (runtime.yard_split): with `real` (R16a) exactly
    the real completions are completed, the terminal catch counting as one,
    chosen among the non-terminal attempts on this stream (rng.sample; an
    interception is never completed); with `replay_values` too (R16b) each
    kind's values are the real drive's own (yard_split.assign), the uniform
    allocation the fallback when the slots do not match them (noted on the
    returned draw's ``notes``)."""
    counts = {"run": runs, "att": attempts, "sack": sacks}
    if terminal:
        counts[pd.BASE_KIND[terminal]] -= 1
    movable = ["run"] * counts["run"] + ["sack"] * counts["sack"] + ["att"] * counts["att"] + ["spike"] * spikes
    rng.shuffle(movable)
    kinds = movable + ["kneel"] * len(kneel_yards) + ([terminal] if terminal else [])
    plays = len(kinds)
    last = plays - 1
    notes = []
    if real is None:
        completed = [k == "catch" or (k == "att" and rng.random() < completion_rate) for k in kinds]
    else:
        want = max(0, real.completions - (1 if terminal == "catch" else 0))
        attempts_at = [i for i, k in enumerate(kinds) if k == "att"]
        if want > len(attempts_at):
            notes.append("real_completions_clamped")
        chosen = set(rng.sample(attempts_at, min(want, len(attempts_at)))) if want and attempts_at else set()
        completed = [k == "catch" or (k == "att" and i in chosen) for i, k in enumerate(kinds)]
    eligible = [i for i, k in enumerate(kinds) if k in ("att", "catch")]
    if pass_yards and eligible and not any(completed):
        completed[rng.choice(eligible)] = True
    completion_slots = [i for i, done in enumerate(completed) if done]
    safety_run = category == "safety" and terminal == "run"
    run_slots = [i for i, k in enumerate(kinds) if k == "run" and not (safety_run and i == last)]
    sack_slots = [i for i, k in enumerate(kinds) if k == "sack" and not (category == "safety" and i == last)]
    kneel_slots = [i for i, k in enumerate(kinds) if k == "kneel"]
    values = [0] * plays
    replayed = None
    if real is not None and replay_values:
        from . import yard_split
        terminal_at = last if terminal in ("catch", "run") and plays else None
        replayed = []
        for slots, real_values, total, kind, fallback in (
                (completion_slots, real.completion_values, pass_yards, "catch", "real_values_fallback_completions"),
                (run_slots, real.run_values, rush_free, "run", "real_values_fallback_runs")):
            assigned = yard_split.assign(rng, slots, real_values, total,
                                         terminal_slot=terminal_at if terminal == kind else None,
                                         terminal_matches=real.term_kind == kind)
            if assigned is None:
                notes.append(fallback)
            replayed.append(assigned)
    if replayed is not None and replayed[0] is not None:
        for index, value in replayed[0].items():
            values[index] = value
    else:
        for index, value in zip(completion_slots, pd._allocate(pass_yards, len(completion_slots), rng)):
            values[index] = value
    if replayed is not None and replayed[1] is not None:
        for index, value in replayed[1].items():
            values[index] = value
    else:
        for index, value in zip(run_slots, pd._allocate_runs(rush_free, len(run_slots), rng, usage_values)):
            values[index] = value
    for index, loss in zip(sack_slots, losses):
        values[index] = -loss
    for index, value in zip(kneel_slots, kneel_yards):
        values[index] = value
    if category == "safety" and plays:
        values[last] = safety_terminal[1]
    if category == "touchdown" and plays and values[last] < 1:
        same = completion_slots if kinds[last] == "catch" else run_slots
        candidates = [i for i in same if i != last and 1 <= values[i] <= 99] or [
            i for i in same if i != last and values[i] >= 1]
        if candidates:
            swap = rng.choice(candidates)
            values[last], values[swap] = values[swap], values[last]
    return _Drawn((kinds, completed, values, len(movable)), notes)


class _Drawn(tuple):
    """A _draw result (kinds, completed, values, movable count) with the
    batch B13 notes of that draw (the fallbacks the adopted draw counts)."""

    def __new__(cls, items, notes=()):
        out = super().__new__(cls, items)
        out.notes = tuple(notes)
        return out


def _score(chains, targets):
    """Distance from the real drive's own chain counts (scrimmage first downs,
    3rd att/conv, 4th att/conv): a preference among legal orders only."""
    if not targets:
        return 0
    want = (targets[0], targets[2], targets[3], targets[4], targets[5])
    return sum(abs(a - b) for a, b in zip(chains, want))


def _alt_plans(rng, pass_yards, rush_free, losses, *, usable, free_runs, td_type, losses_random, count=ALT_PLANS,
               pass_fixed=False):
    """Alternative (passing, free rushing, sack losses) plans for a drive the
    kernel's split cannot order legally. The drive's net never moves: a
    redrawn sack loss (3-10 yards, as the kernel draws it; only when the
    losses were drawn rather than fitted to the net) changes the free
    passing-plus-rushing total by the same amount, and passing yards shift
    against rushing yards. The scoring kind keeps at least one yard. Kernel
    2014.6 batch B13: `pass_fixed` (a replayed drive with no completion)
    keeps the passing yards where they are (fixed completions bind every
    rung)."""
    plans, seen = [], {(pass_yards, rush_free, tuple(losses))}
    shifts = list(SPLIT_SHIFTS)
    for k in range(count * 3):
        if len(plans) >= count:
            break
        new_losses = list(losses)
        if losses_random and losses and k % 2 == 1:
            new_losses = [rng.randint(3, 10) for _ in losses]
        free_total = pass_yards + rush_free + sum(new_losses) - sum(losses)
        shift = shifts[k % len(shifts)] * rng.choice((1, -1))
        if not usable:
            p = 0
        elif not free_runs:
            p = free_total
        elif pass_fixed:
            p = pass_yards
        else:
            p = pass_yards + shift
        r = free_total - p
        if (td_type == "pass" and p < 1) or (td_type == "rush" and r < 1):
            continue
        if usable and free_runs and p < min(0, pass_yards):
            continue
        key = (p, r, tuple(new_losses))
        if key in seen:
            continue
        seen.add(key)
        plans.append((p, r, new_losses))
    return plans


def _concentrate(kinds, completed, values, n_mov, category, terminal, movable_only=False):
    """Repair 3 as a sequence: one yard at a time from the smallest positive
    value to the largest within the completions and within the free runs (a
    scoring or fumbled snap joins its kind; a scoring snap keeps a yard),
    yielding the values after each step until no yard can move
    (REPAIR_STEPS at most). The kind totals never change. With
    `movable_only` the yards gather on the largest movable snap (a fumbled
    terminal snap credits no first down, so the ground a first down needs
    must sit before it)."""
    last = len(kinds) - 1
    with_terminal = terminal in ("catch", "run") and category in ("touchdown", "fumble_lost")
    movable = range(n_mov)
    groups = [[i for i in movable if completed[i] and kinds[i] in ("att", "catch")]
              + ([last] if with_terminal and terminal == "catch" else []),
              [i for i in movable if kinds[i] == "run"] + ([last] if with_terminal and terminal == "run" else [])]
    for _ in range(REPAIR_STEPS):
        moved = False
        for group in groups:
            if len(group) < 2:
                continue
            targets = [i for i in group if i < n_mov] if movable_only else group
            if not targets:
                continue
            big = max(targets, key=lambda i: (values[i], -i))
            donors = [i for i in group if i != big and values[i] > 0
                      and not (i == last and category == "touchdown" and values[i] <= 1)]
            if not donors:
                continue
            donor = min(donors, key=lambda i: (values[i], i))
            values[donor] -= 1
            values[big] += 1
            moved = True
        if not moved:
            return
        yield list(values)


FG_FOURTH_DOWN_RELAXED = "fg_fourth_down_relaxed"


def drive_layout(*, seed, event_id, drive_no, offense, category, td_type, runs, attempts, sacks,
                 kneel_yards, spikes, pass_yards, rush_free, losses, safety_terminal, net, spot,
                 completion_rate, targets=None, term_down=None, diagnostics=None, usage_values=None,
                 fg_down=None, segment=None, lost_kind=None, penalty=None, real_split=None, replay_values=False):
    """The ordered snaps of one resolved drive with a legal chain walk.

    `category` is the kernel category (punt, field_goal_attempt, downs,
    touchdown, interception, fumble_lost, safety, or clock for any
    window-ending drive). The snap counts, the net and the terminal come from
    the kernel and never move. Chosen here: the order, the completion draws
    and the split of each kind's yards across its snaps, and (only when the
    kernel's own split admits no legal order) an alternative passing/rushing
    split or sack-loss draw (_alt_plans), which the kernel then publishes.

    Search order, most faithful first:
    * tier 0: the real drive's terminal down for a field goal, and no more
      fourth-down snaps (and non-terminal fourth-down conversions) than the
      real drive had; tier 1 drops both; tier 2 also drops the kernel 2013.9
      spike seat;
    * within a tier: the kernel's split (DRAWS value draws), then each
      alternative plan (ALT_DRAWS draws);
    * each draw keeps the order closest to the real drive's chain counts over
      RESTARTS randomized searches.
    Then the kernel split's values are equalized within kind one yard at a
    time (Repair 2 of runtime.play_detail._layout), then the plan is
    enumerated: sack losses over their range crossed with one- and two-yard
    passing shifts (LOSS_RUNG_LIMIT, chain_plan_enumerated), and last the
    plan is concentrated: the kernel's, the extreme and the alternative
    splits with their yards gathered onto one snap of each kind, movable
    snaps first (chain_plan_concentrated). If nothing is legal the drive
    keeps an unconstrained order and chain_layout_failed is counted; the
    coherence classes report the resulting break.

    Kernel 2014.6 (batch B6, W3): `fg_down` holds a field-goal drive's kick to
    that down in every tier (the kernel passes 4 when the kick is not early
    by runtime.field_position.FieldPositionModelV3.early_fg_ok). When no
    plan admits it, the closable last fallback admits the real down
    (`term_down`), counted FG_FOURTH_DOWN_RELAXED; the first pass's
    diagnostics are discarded, so the counters describe the adopted layout.
    None (every kernel up to 2014.5) is the unchanged search.

    Kernel 2014.6 (batch B9F): `segment` n lays out a possession's
    continuation segment after a fourth-down conversion on its own keyed
    layout stream (the drive's, keyed by the segment as well); None, the
    drive's first segment, keeps the unchanged stream.

    Kernel 2014.6 (batch B10, R12 layer B; profile flag fumble_terminal_kind):
    `lost_kind` (run, catch or sack: runtime.ball_security.terminal_kind of
    the tuple's own lost entry) is a fumble_lost drive's terminal kind, taken
    without the snap-count draw when the drive has a snap of that kind; the
    existing option ladder stays the fallback when that kind cannot be
    ordered. Every adopted terminal other than `lost_kind` is counted
    fumble_terminal_fallback. None (every kernel up to 2014.5, and 2014.6
    without the flag) is the unchanged draw.

    Kernel 2014.6 (batch B11, R11; profile flag penalty_records): `penalty` is
    the replayed drive's runtime.penalties.DrivePlan. The layout stream
    carries CHAIN_LAYOUT_TAG_V2; each drawn split's clause groups ride on host
    snaps of their kind (_attach), the movable penalty rows join the snaps in
    _EventSearch and the pre-kick rows its tail; the chain walk is walk_steps
    (ledger-walk-v2) and every rung's search carries the records. The kernel
    has already taken the records' yards out of the scrimmage split, so the
    snaps plus the records still net the drive. The layout gains "sequence"
    (["s", snap index] and ["p", event id] in order), "attached" ({snap
    index: [Attach]}), "events" and "chain_model". None is the unchanged path.

    Kernel 2014.6 (batch B13, R16a and R16b; profile flags yard_split and
    snap_values): `real_split` is the drive's runtime.yard_split.RealSplit. Its
    completions are fixed in every rung (exactly the real count; pass yards
    stay 0 for a drive with none), its sack losses are never redrawn
    (losses_random is False), and with `replay_values` each kind's values are
    the real drive's own (_draw). The fallbacks of the adopted draw are
    counted (real_completions_clamped, real_values_fallback_completions,
    real_values_fallback_runs). None is the unchanged path.
    """
    args = dict(seed=seed, event_id=event_id, drive_no=drive_no, offense=offense, category=category,
                td_type=td_type, runs=runs, attempts=attempts, sacks=sacks, kneel_yards=kneel_yards, spikes=spikes,
                pass_yards=pass_yards, rush_free=rush_free, losses=losses, safety_terminal=safety_terminal, net=net,
                spot=spot, completion_rate=completion_rate, targets=targets, usage_values=usage_values,
                segment=segment, lost_kind=lost_kind, penalty=penalty, real_split=real_split,
                replay_values=replay_values)
    if fg_down is not None and category == "field_goal_attempt":
        scratch = {}
        held = _drive_layout(term_down=fg_down, diagnostics=scratch, every_tier=True, **args)
        if held["ok"]:
            if diagnostics is not None:
                for name, count in scratch.items():
                    diagnostics[name] = diagnostics.get(name, 0) + count
            return held
        if diagnostics is not None:
            diagnostics[FG_FOURTH_DOWN_RELAXED] = diagnostics.get(FG_FOURTH_DOWN_RELAXED, 0) + 1
    return _drive_layout(term_down=term_down, diagnostics=diagnostics, **args)


def _drive_layout(*, seed, event_id, drive_no, offense, category, td_type, runs, attempts, sacks,
                  kneel_yards, spikes, pass_yards, rush_free, losses, safety_terminal, net, spot,
                  completion_rate, targets=None, term_down=None, diagnostics=None, usage_values=None,
                  every_tier=False, segment=None, lost_kind=None, penalty=None, real_split=None,
                  replay_values=False):
    """drive_layout's search (docstring there). `every_tier` keeps the
    field-goal terminal down in tiers 2 and 3 as well (W3)."""
    from . import play_detail as pd

    diagnostics = diagnostics if diagnostics is not None else {}
    tag = CHAIN_LAYOUT_TAG_V2 if penalty is not None else CHAIN_LAYOUT_TAG
    rng = (_stream(seed, event_id, drive_no, offense, tag=tag) if segment is None
           else _stream(seed, event_id, drive_no, offense, "segment", int(segment), tag=tag))
    kneel_yards = [int(y) for y in kneel_yards]
    losses = [int(x) for x in losses]
    spot, net = int(spot), int(net)
    available = {"run": runs, "catch": attempts, "sack": sacks}
    if category == "safety":
        terminal = safety_terminal[0]
    elif category == "fumble_lost" and lost_kind is not None and available.get(lost_kind, 0) > 0:
        # Batch B10 (R12 layer B): the tuple's own lost-fumble kind, no draw.
        terminal = lost_kind
    else:
        terminal = pd._terminal_kind(rng, category, td_type, runs, attempts, sacks)
    options = [terminal]
    if category == "fumble_lost":
        options += [k for k, n in (("run", runs), ("catch", attempts), ("sack", sacks)) if n and k != terminal]
    turnover_last = category in TURNOVER_TERMINALS
    base_final = {"punt": 4, "downs": 5, "touchdown": "td"}.get(category)
    fg_final = term_down if category == "field_goal_attempt" and term_down in (1, 2, 3, 4) else None
    real = tuple(int(targets[i]) for i in (0, 2, 3, 4, 5)) if targets else None
    tiers = (
        # Exact: the real drive's own scrimmage first downs, third- and
        # fourth-down attempts and conversions (kernel split only).
        {"final": fg_final or base_final, "caps": real + (real[4],) if real else None, "exact": real,
         "spike": True, "alternatives": False},
        {"final": fg_final or base_final,
         "caps": (None, None, None, real[3], None, real[4]) if real else None, "exact": None,
         "spike": True, "alternatives": True},
        {"final": (fg_final or base_final) if every_tier else base_final, "caps": None, "exact": None,
         "spike": True, "alternatives": True},
        {"final": (fg_final or base_final) if every_tier else base_final, "caps": None, "exact": None,
         "spike": False, "alternatives": True},
    )
    usable = attempts - (1 if category == "interception" else 0)
    free_runs = runs - (1 if category == "safety" and safety_terminal and safety_terminal[0] == "run" else 0)
    losses_random = usable + free_runs > 0 and real_split is None
    # Batch B13 (R16a): a replayed drive with no completion keeps its passing
    # yards fixed in every rung.
    pass_fixed = real_split is not None and real_split.completions <= 0
    draw_options = {"real": real_split, "replay_values": bool(replay_values and real_split is not None)}

    def attempt(kinds, completed, values, n_mov, tier):
        if penalty is not None:
            return attempt_events(kinds, completed, values, n_mov, tier)
        sig = [(kinds[i], completed[i], values[i]) for i in range(len(kinds))]
        search = _Search(rng, sig, n_mov, spot, final_down=tier["final"], downs=category == "downs",
                         turnover_last=turnover_last, caps=tier["caps"], exact=tier["exact"],
                         spike_rule=tier["spike"])
        best = None
        for _ in range(1 if tier["exact"] else RESTARTS):
            order, exhausted = search.run(EXACT_BUDGET if tier["exact"] else NODE_BUDGET)
            if order is None:
                if exhausted:
                    break
                continue
            full = order + list(range(n_mov, len(kinds)))
            w = walk(spot, [values[i] for i in full], turnover_last)
            score = _score(w["chains"], targets)
            if best is None or score < best[0]:
                best = (score, full, w)
            if score == 0:
                break
        return best

    movable_events = [e for e in penalty.events if not e.tail] if penalty is not None else []
    tail_events = [e for e in penalty.events if e.tail] if penalty is not None else []

    def arrangement(kinds, completed, values, n_mov, attached):
        """(movable items, their refs, tail items, their refs) of one draw."""
        has_terminal = len(kinds) > n_mov + len(kneel_yards)
        items = [_snap_item(kinds, completed, values, i, attached) for i in range(n_mov)]
        refs = [("s", i) for i in range(n_mov)]
        items += [_event_item(e) for e in movable_events]
        refs += [("p", e.eid) for e in movable_events]
        tail_idx = list(range(n_mov, n_mov + len(kneel_yards)))
        tail = [_snap_item(kinds, completed, values, i, attached) for i in tail_idx]
        tail_refs = [("s", i) for i in tail_idx]
        tail += [_event_item(e) for e in tail_events]
        tail_refs += [("p", e.eid) for e in tail_events]
        if has_terminal:
            tail.append(_snap_item(kinds, completed, values, len(kinds) - 1, attached))
            tail_refs.append(("s", len(kinds) - 1))
        return items, refs, tail, tail_refs

    def attempt_events(kinds, completed, values, n_mov, tier):
        attached = _attach(rng, kinds, completed, terminal if len(kinds) > n_mov + len(kneel_yards) else None,
                           penalty.attached, diagnostics)
        items, refs, tail, tail_refs = arrangement(kinds, completed, values, n_mov, attached)
        search = _EventSearch(rng, items, tail, spot, final_down=tier["final"], downs=category == "downs",
                              turnover_last=turnover_last, caps=tier["caps"], exact=tier["exact"],
                              spike_rule=tier["spike"])
        best = None
        for _ in range(1 if tier["exact"] else RESTARTS):
            order, exhausted = search.run(EXACT_BUDGET if tier["exact"] else NODE_BUDGET)
            if order is None:
                if exhausted:
                    break
                continue
            sequence = [refs[j] for j in order] + tail_refs
            w = walk_steps(spot, _steps_of([items[j] for j in order] + tail), turnover_last)
            score = _score_steps(w, targets)
            if best is None or score < best[0]:
                best = (score, sequence, w, attached)
            if score == 0:
                break
        return best

    def ordered(kinds, completed, values, sequence, attached, w):
        """The layout fields of a v2 arrangement: the snaps in sequence order,
        the sequence and attachments re-indexed to that order."""
        snap_order = [ref for tag, ref in sequence if tag == "s"]
        position = {old: new for new, old in enumerate(snap_order)}
        return {"kinds": [kinds[i] for i in snap_order], "completed": [completed[i] for i in snap_order],
                "values": [values[i] for i in snap_order], "walk": w,
                "sequence": [["s", position[ref]] if tag == "s" else ["p", ref] for tag, ref in sequence],
                "attached": {position[i]: list(groups) for i, groups in attached.items() if i in position},
                "events": list(penalty.events), "chain_model": CHAIN_MODEL_V2}

    def bump(name):
        diagnostics[name] = diagnostics.get(name, 0) + 1

    def finish(kinds, completed, values, best, plan, how, notes=()):
        for name in how:
            bump(name)
        for name in notes:
            bump(name)
        if category == "fumble_lost" and lost_kind is not None and terminal != lost_kind:
            bump("fumble_terminal_fallback")
        if "chain_layout_repaired" in how:
            bump("prefix_order_repaired")
        if penalty is not None:
            _, sequence, w, attached = best
            out = {"ok": True, "terminal": terminal, "pass_yards": plan[0], "rush_free": plan[1],
                   "losses": list(plan[2])}
            out.update(ordered(kinds, completed, values, sequence, attached, w))
            return out
        _, full, w = best
        return {"ok": True, "terminal": terminal, "kinds": [kinds[i] for i in full],
                "completed": [completed[i] for i in full], "values": [values[i] for i in full],
                "walk": w, "pass_yards": plan[0], "rush_free": plan[1], "losses": list(plan[2])}

    kernel_plan = (pass_yards, rush_free, losses)
    last_draw = None
    for option_no, terminal in enumerate(options):
        alternatives = None
        for tier_no, tier in enumerate(tiers):
            if alternatives is None or not tier["alternatives"]:
                plans = [kernel_plan]
            else:
                plans = [kernel_plan] + alternatives
            plan_no = 0
            while plan_no < len(plans):
                plan = plans[plan_no]
                for draw_no in range(DRAWS if plan_no == 0 else ALT_DRAWS):
                    drawn = _draw(rng, pd, category, terminal, runs, attempts, sacks, kneel_yards, spikes,
                                  plan[0], plan[1], plan[2], safety_terminal, completion_rate, usage_values,
                                  **draw_options)
                    if plan_no == 0:
                        last_draw = drawn
                    best = attempt(*drawn, tier)
                    if best is not None:
                        how = []
                        if tier_no:
                            how.append("chain_layout_inexact")
                        if tier_no > 1:
                            how.append("chain_layout_relaxed")
                        if draw_no:
                            how.append("chain_layout_redrawn")
                        if plan_no:
                            how.append("chain_split_repaired")
                        if option_no:
                            how.append("chain_layout_repaired")
                        return finish(*drawn[:3], best, plan, how, notes=drawn.notes)
                if plan_no == 0 and tier["alternatives"]:
                    if alternatives is None:
                        alternatives = _alt_plans(rng, pass_yards, rush_free, losses, usable=usable,
                                                  free_runs=free_runs, td_type=td_type,
                                                  losses_random=losses_random, pass_fixed=pass_fixed)
                    plans = [kernel_plan] + alternatives
                plan_no += 1
        # Value repair within kind on the kernel split's last draw (kind
        # totals unchanged): move one yard at a time from the largest to the
        # smallest value of the completions and of the free runs (a scoring
        # or fumbled snap joins its kind; a scoring snap keeps a yard).
        kinds, completed, values, n_mov = last_draw
        values = list(values)
        last = len(kinds) - 1
        with_terminal = terminal in ("catch", "run") and category in ("touchdown", "fumble_lost")
        movable = range(n_mov)
        groups = [[i for i in movable if completed[i] and kinds[i] in ("att", "catch")]
                  + ([last] if with_terminal and terminal == "catch" else []),
                  [i for i in movable if kinds[i] == "run"] + ([last] if with_terminal and terminal == "run" else [])]
        for concentrate in (False, True):
            values = list(last_draw[2])
            for _ in range(REPAIR_STEPS):
                moved = False
                for group in groups:
                    if len(group) < 2:
                        continue
                    big = max(group, key=lambda i: (values[i], -i))
                    small = min(group, key=lambda i: (values[i], i))
                    if concentrate:
                        # Repair 3: move a yard from the smallest positive
                        # value to the largest, so one snap can reach a line
                        # to gain the others fall short of.
                        donors = [i for i in group if i != big and values[i] > 0
                                  and not (i == last and category == "touchdown" and values[i] <= 1)]
                        if not donors:
                            continue
                        donor = min(donors, key=lambda i: (values[i], i))
                        values[donor] -= 1
                        values[big] += 1
                        moved = True
                        continue
                    if big == last and category == "touchdown" and values[big] <= 1:
                        continue
                    if values[big] - values[small] >= 2:
                        values[big] -= 1
                        values[small] += 1
                        moved = True
                if not moved:
                    break
                best = attempt(kinds, completed, values, n_mov, tiers[3])
                if best is not None:
                    return finish(kinds, completed, values, best, kernel_plan,
                                  ["chain_layout_inexact", "chain_layout_relaxed", "chain_layout_repaired"],
                                  notes=last_draw.notes)
    # Last rung: the plan enumerated rather than drawn. Every sack-loss
    # combination in the kernel's range when the losses were drawn (the
    # kernel's own losses otherwise), crossed with a one- or two-yard shift
    # of passing against free rushing yards. A drive whose net is reachable
    # only with a particular loss (a real drive whose first down a long sack
    # gave back) or a particular split (a goal-line drive whose passes must
    # reach the line to gain exactly) is otherwise missed by the random
    # redraws and the coarse SPLIT_SHIFTS above.
    import itertools
    if losses_random and losses:
        combos = list(itertools.product(range(3, 11), repeat=len(losses)))
        if len(combos) > LOSS_RUNG_LIMIT:
            combos = [tuple(rng.randint(3, 10) for _ in losses) for _ in range(LOSS_RUNG_LIMIT)]
    else:
        combos = [tuple(losses)]
    shifts = (0, 1, -1, 2, -2) if usable and free_runs and not pass_fixed else (0,)
    for shift, new_losses in itertools.product(shifts, combos):
        delta = sum(new_losses) - sum(losses)
        if not delta and not shift:
            continue
        if usable:
            p, r = pass_yards + delta + shift, rush_free - shift
        else:
            p, r = pass_yards, rush_free + delta
        if (td_type == "pass" and p < 1) or (td_type == "rush" and r < 1):
            continue
        plan = (p, r, list(new_losses))
        drawn = _draw(rng, pd, category, options[0], runs, attempts, sacks, kneel_yards, spikes,
                      plan[0], plan[1], plan[2], safety_terminal, completion_rate, usage_values, **draw_options)
        best = attempt(*drawn, tiers[3])
        if best is not None:
            terminal = options[0]
            return finish(*drawn[:3], best, plan, ["chain_layout_inexact", "chain_layout_relaxed",
                                                   "chain_split_repaired", "chain_plan_enumerated"],
                          notes=drawn.notes)
    # Final rung (October 1, 2026, defect register item 3): the plan
    # concentrated. A relocated drive whose net far exceeds what its snap
    # count spreads (a real 4-snap punt netting 19 behind a penalty first
    # down, replayed from the 99 with its end kept: net 53) is legal only
    # when one snap carries most of the ground (a 44-yard snap, then three
    # short ones and the punt on fourth down). A random allocation and the
    # bounded shifts above never produce that, so the kernel's plan, each
    # extreme split (all free yards passing, all rushing) and each
    # alternative plan is drawn once and its values moved one yard at a time
    # onto the largest value of each kind (Repair 3), first onto a movable
    # snap (a five-run fumble netting 10 needs its first down before the
    # fumbled snap, which Repair 3 fed instead), then onto any; the search
    # runs after every step. Nothing before this rung changes: it runs only
    # after every plan above failed.
    free_total = pass_yards + rush_free
    concentrated = [kernel_plan]
    if usable and free_runs and not pass_fixed:
        concentrated += [(free_total, 0, losses), (0, free_total, losses)]
    concentrated += _alt_plans(rng, pass_yards, rush_free, losses, usable=usable, free_runs=free_runs,
                               td_type=td_type, losses_random=losses_random, pass_fixed=pass_fixed)
    for plan in concentrated:
        if (td_type == "pass" and plan[0] < 1) or (td_type == "rush" and plan[1] < 1):
            continue
        drawn = _draw(rng, pd, category, options[0], runs, attempts, sacks, kneel_yards, spikes,
                      plan[0], plan[1], plan[2], safety_terminal, completion_rate, usage_values, **draw_options)
        kinds, completed, values, n_mov = drawn
        for movable_only in (True, False):
            for values in _concentrate(kinds, completed, list(drawn[2]), n_mov, category, options[0],
                                       movable_only=movable_only):
                best = attempt(kinds, completed, values, n_mov, tiers[3])
                if best is not None:
                    terminal = options[0]
                    how = ["chain_layout_inexact", "chain_layout_relaxed", "chain_plan_concentrated"]
                    if plan is not kernel_plan:
                        how.append("chain_split_repaired")
                    return finish(kinds, completed, values, best, plan, how, notes=drawn.notes)
    bump("chain_layout_failed")
    bump("prefix_order_failed")
    kinds, completed, values, n_mov = last_draw
    if penalty is not None:
        # No legal arrangement: the snaps in their drawn order, each movable
        # penalty row before the snap of its real order (the coherence
        # classes report the break, as before).
        attached = _attach(rng, kinds, completed, terminal if len(kinds) > n_mov + len(kneel_yards) else None,
                           penalty.attached, diagnostics)
        items, refs, tail, tail_refs = arrangement(kinds, completed, values, n_mov, attached)
        snaps = [j for j, ref in enumerate(refs) if ref[0] == "s"]
        events = sorted((j for j, ref in enumerate(refs) if ref[0] == "p"),
                        key=lambda j: (penalty.events[refs[j][1]].before, j))
        order, placed = [], 0
        for j in snaps:
            while events and penalty.events[refs[events[0]][1]].before <= placed:
                order.append(events.pop(0))
            order.append(j)
            placed += 1
        order += events
        sequence = [refs[j] for j in order] + tail_refs
        w = walk_steps(spot, _steps_of([items[j] for j in order] + tail), turnover_last)
        out = {"ok": False, "terminal": terminal, "pass_yards": pass_yards, "rush_free": rush_free,
               "losses": list(losses)}
        out.update(ordered(kinds, completed, values, sequence, attached, w))
        return out
    return {"ok": False, "terminal": terminal, "kinds": kinds, "completed": completed, "values": values,
            "walk": walk(spot, values, turnover_last), "pass_yards": pass_yards, "rush_free": rush_free,
            "losses": list(losses)}
