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


def chain_feasible(category, *, plays, net, spot, kneel_yards=(), sacks=0, runs=0, terminal_value=0):
    """Can a drive of `plays` scrimmage snaps netting `net` from `spot` be
    ordered into a legal chain walk that ends in its category's terminal
    state? A necessary counting and yardage condition, evaluated before the
    snap values exist:

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
    """
    spot, net, kneels = int(spot), int(net), len(kneel_yards)
    kneel_sum = sum(int(y) for y in kneel_yards)
    dist0 = spot - line_to_gain(spot)
    if category == "touchdown":
        pre = None
    elif category == "fumble_lost":
        # The yards before the fumbled snap: at most the net plus a loss of
        # up to ten on a fumbled run or sack (a completion's share of a
        # positive passing total is never negative).
        pre = net + (10 if runs or sacks else 0)
    elif category == "safety":
        pre = net - terminal_value
    else:
        pre = net
    for length in last_series_lengths(category, kneels):
        if length > plays:
            continue
        m = plays - length
        if m == 0:
            if pre is None or category == "fumble_lost" or pre - kneel_sum < dist0:
                return True
            continue
        f = math.ceil(m / 4)
        if spot <= 10 * f:
            continue
        if pre is not None:
            in_last = max(0, length - kneels - (0 if category in ("punt", "downs", "field_goal_attempt", "clock") else 1))
            lowest_last = kneel_sum - 10 * min(sacks, in_last)
            if pre - min(0, lowest_last) < 10 * f:
                continue
        return True
    return False


# ---- layout ------------------------------------------------------------------

def _stream(seed, *parts):
    payload = json.dumps([CHAIN_LAYOUT_TAG, *parts], separators=(",", ":")).encode()
    return random.Random(int.from_bytes(hashlib.sha256(seed + payload).digest(), "big"))


def resample_stream(seed, event_id, drive_no, offense):
    """Kernel 2014.4 phase 2: the stream a drive's layout resample draws
    on (its replacement tuple, sack losses and yard split), keyed like the
    layout stream with its own tag so neither consumes the other."""
    return _stream(seed, event_id, drive_no, offense, "layout-resample")


def _runs_clock(kind, completed):
    """A run, a sack or a completed pass leaves the clock running."""
    return kind in ("run", "sack") or (kind in ("att", "catch") and completed)


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
          losses, safety_terminal, completion_rate):
    """Kinds, completions and per-snap values, as runtime.play_detail._layout
    draws them (the movable snaps first, then kneels and the terminal snap)."""
    counts = {"run": runs, "att": attempts, "sack": sacks}
    if terminal:
        counts[pd.BASE_KIND[terminal]] -= 1
    movable = ["run"] * counts["run"] + ["sack"] * counts["sack"] + ["att"] * counts["att"] + ["spike"] * spikes
    rng.shuffle(movable)
    kinds = movable + ["kneel"] * len(kneel_yards) + ([terminal] if terminal else [])
    plays = len(kinds)
    last = plays - 1
    completed = [k == "catch" or (k == "att" and rng.random() < completion_rate) for k in kinds]
    eligible = [i for i, k in enumerate(kinds) if k in ("att", "catch")]
    if pass_yards and eligible and not any(completed):
        completed[rng.choice(eligible)] = True
    completion_slots = [i for i, done in enumerate(completed) if done]
    safety_run = category == "safety" and terminal == "run"
    run_slots = [i for i, k in enumerate(kinds) if k == "run" and not (safety_run and i == last)]
    sack_slots = [i for i, k in enumerate(kinds) if k == "sack" and not (category == "safety" and i == last)]
    kneel_slots = [i for i, k in enumerate(kinds) if k == "kneel"]
    values = [0] * plays
    for index, value in zip(completion_slots, pd._allocate(pass_yards, len(completion_slots), rng)):
        values[index] = value
    for index, value in zip(run_slots, pd._allocate_runs(rush_free, len(run_slots), rng)):
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
    return kinds, completed, values, len(movable)


def _score(chains, targets):
    """Distance from the real drive's own chain counts (scrimmage first downs,
    3rd att/conv, 4th att/conv): a preference among legal orders only."""
    if not targets:
        return 0
    want = (targets[0], targets[2], targets[3], targets[4], targets[5])
    return sum(abs(a - b) for a, b in zip(chains, want))


def _alt_plans(rng, pass_yards, rush_free, losses, *, usable, free_runs, td_type, losses_random, count=ALT_PLANS):
    """Alternative (passing, free rushing, sack losses) plans for a drive the
    kernel's split cannot order legally. The drive's net never moves: a
    redrawn sack loss (3-10 yards, as the kernel draws it; only when the
    losses were drawn rather than fitted to the net) changes the free
    passing-plus-rushing total by the same amount, and passing yards shift
    against rushing yards. The scoring kind keeps at least one yard."""
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


def drive_layout(*, seed, event_id, drive_no, offense, category, td_type, runs, attempts, sacks,
                 kneel_yards, spikes, pass_yards, rush_free, losses, safety_terminal, net, spot,
                 completion_rate, targets=None, term_down=None, diagnostics=None):
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
    time (Repair 2 of runtime.play_detail._layout), and last the plan is
    enumerated: sack losses over their range crossed with one- and two-yard
    passing shifts (LOSS_RUNG_LIMIT, chain_plan_enumerated). If nothing is legal the drive keeps an
    unconstrained order and chain_layout_failed is counted; the coherence
    classes report the resulting break."""
    from . import play_detail as pd

    diagnostics = diagnostics if diagnostics is not None else {}
    rng = _stream(seed, event_id, drive_no, offense)
    kneel_yards = [int(y) for y in kneel_yards]
    losses = [int(x) for x in losses]
    spot, net = int(spot), int(net)
    if category == "safety":
        terminal = safety_terminal[0]
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
        {"final": base_final, "caps": None, "exact": None, "spike": True, "alternatives": True},
        {"final": base_final, "caps": None, "exact": None, "spike": False, "alternatives": True},
    )
    usable = attempts - (1 if category == "interception" else 0)
    free_runs = runs - (1 if category == "safety" and safety_terminal and safety_terminal[0] == "run" else 0)
    losses_random = usable + free_runs > 0

    def attempt(kinds, completed, values, n_mov, tier):
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

    def bump(name):
        diagnostics[name] = diagnostics.get(name, 0) + 1

    def finish(kinds, completed, values, best, plan, how):
        _, full, w = best
        for name in how:
            bump(name)
        if "chain_layout_repaired" in how:
            bump("prefix_order_repaired")
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
                                  plan[0], plan[1], plan[2], safety_terminal, completion_rate)
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
                        return finish(*drawn[:3], best, plan, how)
                if plan_no == 0 and tier["alternatives"]:
                    if alternatives is None:
                        alternatives = _alt_plans(rng, pass_yards, rush_free, losses, usable=usable,
                                                  free_runs=free_runs, td_type=td_type,
                                                  losses_random=losses_random)
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
                                  ["chain_layout_inexact", "chain_layout_relaxed", "chain_layout_repaired"])
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
    shifts = (0, 1, -1, 2, -2) if usable and free_runs else (0,)
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
                      plan[0], plan[1], plan[2], safety_terminal, completion_rate)
        best = attempt(*drawn, tiers[3])
        if best is not None:
            terminal = options[0]
            return finish(*drawn[:3], best, plan, ["chain_layout_inexact", "chain_layout_relaxed",
                                                   "chain_split_repaired", "chain_plan_enumerated"])
    bump("chain_layout_failed")
    bump("prefix_order_failed")
    kinds, completed, values, n_mov = last_draw
    return {"ok": False, "terminal": terminal, "kinds": kinds, "completed": completed, "values": values,
            "walk": walk(spot, values, turnover_last), "pass_yards": pass_yards, "rush_free": rush_free,
            "losses": list(losses)}
