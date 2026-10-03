"""Deterministic public snap-detail allocation for an already-resolved drive.

The possession kernel owns score/outcome generation. This module uses
separate deterministic RNG streams to allocate that already-resolved drive
into public snap records and player statistics (snap-detail stream), to name
the kicker and returner of a kick (kickoff-detail stream) and to attach a
descriptive call label to each snap after its ball carrier or target is fixed
(label stream). Because none of them consumes the possession RNG, requesting
more detail cannot alter the game result.
"""
from __future__ import annotations

import hashlib
import json
import random

from . import call_families
from . import call_situations
from . import chains as chain_walk
from . import usage
from .player_evidence import choose

OFFENSIVE_LINE = {"OT", "OG", "C", "T", "G", "OL"}
# Kernel 2014.3: v5/v3 name the on-field blocker, coverage tackler and long
# snapper (credit only; the possession stream is untouched).
SNAP_DETAIL_TAG = "public-snap-detail-v5"
KICKOFF_DETAIL_TAG = "public-kickoff-detail-v3"
# Kernel 2014.5: the label stream reads the sheet's situational menus and
# opening sequence (runtime.call_situations); the tag is unchanged because
# the stream still never touches the possession draw.
LABEL_TAG = "public-call-label-v1"
KNEEL_LABEL = "Victory (kneel)"
SPIKE_LABEL = "Clock (spike)"
SCRAMBLE_LABEL = "QB Scramble"
GENERIC_RUN = "Generic Run"
GENERIC_PASS = "Generic Pass"


def _stream(tag, seed, *parts):
    payload = json.dumps([tag, *parts], separators=(",", ":")).encode()
    return random.Random(int.from_bytes(hashlib.sha256(seed + payload).digest(), "big"))


def _rng(seed, *, event_id, drive_no, offense):
    return _stream(SNAP_DETAIL_TAG, seed, event_id, drive_no, offense)


def _label_rng(seed, *, event_id, drive_no, offense):
    return _stream(LABEL_TAG, seed, event_id, drive_no, offense)


def _allocate(total, count, rng):
    """Allocate an integer total over count records while reconciling exactly."""
    if count <= 0:
        return []
    if count == 1:
        return [int(total)]
    sign = -1 if total < 0 else 1
    remaining = abs(int(total))
    weights = [max(0.05, rng.random()) for _ in range(count)]
    denom = sum(weights)
    values = [int(remaining * weight / denom) for weight in weights]
    residue = remaining - sum(values)
    order = list(range(count))
    rng.shuffle(order)
    for index in order[:residue]:
        values[index] += 1
    return [sign * value for value in values]


def _allocate_runs(total, count, rng, usage_values=None):
    """Allocate drive rushing yards so some carries lose yardage.

    The sourced 2012 negative-run rate marks losing carries; their losses come
    from the sourced loss distribution and the remaining carries absorb the
    difference, so the drive total still reconciles exactly. `usage_values`
    is the calibration base's usage table (the 2012 base's when None).
    """
    if count <= 1 or total < 0:
        return _allocate(total, count, rng)
    values = usage_values if usage_values is not None else usage.load()["values"]
    rate = values["negative_run_rate"]
    losing = [i for i in range(count) if rng.random() < rate]
    if len(losing) == count:
        losing = losing[:-1]
    losses = {i: usage.draw_loss(rng, values["negative_run_loss_distribution"]) for i in losing}
    gaining = [i for i in range(count) if i not in losses]
    shares = _allocate(int(total) + sum(losses.values()), len(gaining), rng)
    values = [0] * count
    for index, value in zip(gaining, shares):
        values[index] = value
    for index, loss in losses.items():
        values[index] = -loss
    return values


def _credit_tackle(rng, defenders, defense_stats, record, *, negative=False, usage_values=None):
    """Credit a solo or assisted tackle using the sourced group shapes (the
    calibration base's usage table; the 2012 base's when None)."""
    values = usage_values if usage_values is not None else usage.load()["values"]
    shares = values["tfl_share"] if negative else values["tackle_share"]
    first = usage.pick(rng, defenders, shares, "defense", role="tackle", rank_shapes=values["rank_shares"])
    second = None
    if rng.random() < values["assisted_tackle_play_rate"]:
        try:
            second = usage.pick(
                rng, defenders, values["tackle_share"], "defense",
                role="tackle", exclude=(first,), rank_shapes=values["rank_shares"],
            )
        except ValueError:
            second = None
    credited = [first] + ([second] if second is not None else [])
    for player in credited:
        line = defense_stats["players"][player.player_id]
        _bump(line, "tackles")
        _bump(line, "assisted_tackles" if second is not None else "solo_tackles")
        if negative:
            _bump(line, "tackles_for_loss")
    record["tackler"] = first.player_id
    if second is not None:
        record["assist_tackler"] = second.player_id
    return first


def _returner(rng, players, role):
    """The coach-designated returner, else the club returner by the
    kernel 2014.3 depth rule (runtime.usage.club_returner): one per game."""
    return usage.club_returner(players, role) or choose(rng, players, {"WR", "RB", "CB", "S"}, role)


def _coverage_tackle(rng, players, stats_players, role, exclude):
    """Kernel 2014.3: credit the returned kick's tackle to one player of the
    kicking club's coverage unit, evenly (no sourced within-unit share)."""
    unit = usage.coverage_unit(players, role, exclude=exclude)
    if not unit:
        return None
    tackler = rng.choice(unit)
    _bump(stats_players[tackler.player_id], "special_teams_tackles")
    return tackler


def _declarations(raw, name, family, kind):
    """(carrier, target) for label use; an unusable entry is 'unspecified'."""
    entry = dict(raw) if isinstance(raw, dict) else {}
    entry.update({"name": name, "family": family, "type": kind})
    try:
        return call_families.resolve(entry)
    except ValueError:
        return (call_families.UNSPECIFIED if kind in ("run", "any", "mixed") else None,
                call_families.UNSPECIFIED if kind in ("pass", "any", "mixed") else None)


def _normalize_call(raw, default_type):
    if isinstance(raw, str):
        carrier, target = _declarations(None, raw, raw, default_type)
        return {
            "name": raw,
            "family": raw,
            "type": default_type,
            "personnel": None,
            "formation": None,
            "motion": None,
            "protection": None,
            "tags": (),
            "carrier": carrier,
            "target": target,
            "menus": (),
            "opener": None,
            "opener_returns": (),
        }
    if isinstance(raw, dict):
        name = str(raw.get("name") or raw.get("concept") or raw.get("family") or default_type.title())
        family = str(raw.get("family") or raw.get("concept") or name)
        kind = str(raw.get("type") or default_type).lower()
        carrier, target = _declarations(raw, name, family, kind)
        return {
            "name": name,
            "family": family,
            "type": kind,
            "personnel": raw.get("personnel"),
            "formation": raw.get("formation"),
            "motion": raw.get("motion"),
            "protection": raw.get("protection"),
            "tags": tuple(raw.get("tags") or ()),
            "carrier": carrier,
            "target": target,
            # Kernel 2014.5 (label stream only; excluded from the outcome packet).
            "menus": call_situations.menu_keys(raw.get("menus")),
            "opener": _opener(raw.get("opener")),
            "opener_returns": tuple(r for r in (_opener(x) for x in (raw.get("opener_returns") or ())) if r),
        }
    return _normalize_call(default_type.title(), default_type)


def _opener(value):
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def canonical_call_sheet(team):
    """Return football-substance-only call metadata for outcome commitment.

    Display names, list order and the descriptive carrier/target declarations
    are intentionally excluded, so rewording a call name or changing who a
    label may describe cannot change the outcome draw. The current possession
    kernel does not use call-level matchup effects, but it still freezes the
    structural weekly menu for audit/replay purposes.
    """
    raw = tuple(getattr(team, "offensive_call_sheet", ()) or ())
    rows = []
    for item in raw:
        normalized = _normalize_call(item, "any")
        rows.append({
            "family": normalized["family"],
            "type": normalized["type"],
            "personnel": normalized["personnel"],
            "formation": normalized["formation"],
            "motion": normalized["motion"],
            "protection": normalized["protection"],
            "tags": list(normalized["tags"]),
        })
    # Sorted and deduplicated: reordering the sheet or listing the same
    # football call twice under different names cannot move the outcome draw.
    unique = {json.dumps(row, sort_keys=True, separators=(",", ":")): row for row in rows}
    return [unique[key] for key in sorted(unique)]


def _call_sheet(team, play_type):
    raw = tuple(getattr(team, "offensive_call_sheet", ()) or ())
    normalized = [_normalize_call(item, play_type) for item in raw]
    return [item for item in normalized if item["type"] in {play_type, "any", "mixed"}]


def _canonical(call):
    return json.dumps({k: (list(v) if isinstance(v, tuple) else v) for k, v in call.items()},
                      sort_keys=True, separators=(",", ":"))


def _candidates(team, play_type, fits):
    """Compatible calls, deduplicated and sorted by name then canonical JSON."""
    seen = {}
    for call in _call_sheet(team, play_type):
        if fits(call):
            seen.setdefault(_canonical(call), call)
    return [seen[key] for key in sorted(seen, key=lambda key: (seen[key]["name"], key))]


def _engine_label(name, kind):
    return {"name": name, "family": name, "type": kind, "personnel": None, "formation": None,
            "motion": None, "protection": None, "tags": (), "carrier": None, "target": None,
            "menus": (), "opener": None, "opener_returns": ()}


def _groups(value):
    if value is None:
        return None
    return value if isinstance(value, str) else list(value)


def _personnel_slots(personnel):
    """{group: slots} for a two-digit personnel code (backs, tight ends,
    receivers the rest of five); None when the code names no skill layout
    (for example 6OL), in which case no personnel limit applies."""
    code = str(personnel or "")
    if len(code) != 2 or not code.isdigit():
        return None
    backs, ends = int(code[0]), int(code[1])
    if backs + ends > 5:
        return None
    return {"RB": backs, "FB": backs, "TE": ends, "WR": 5 - backs - ends}


def _personnel_fits(call, grp, rank):
    """Kernel 2013.10: whether the player who made the snap could be on the
    field in the call's personnel. His group needs a slot, and his depth rank
    in that group may be at most one past the slots (one rotation spot, as in
    "Thielen / Blackmon" or "MJD / Grimes"). A fullback needs two backs. A
    quarterback, an unranked player or a personnel code with no skill layout
    always fits."""
    slots = _personnel_slots(call.get("personnel"))
    if slots is None or grp in (None, "QB") or rank is None:
        return True
    if grp == "FB":
        return slots["FB"] >= 2 and rank <= slots["FB"] - 1
    count = slots.get(grp)
    if count is None:
        return True
    return count >= 1 and rank <= count + 1


def _group_rank(players, player):
    """1-based depth rank of a player within his position group."""
    grp = usage.group(player.position)
    ordered = usage.depth_order(tuple(players), grp)
    for rank, member in enumerate(ordered, 1):
        if member.player_id == player.player_id:
            return rank
    return None


def _menu_select(lrng, team, play_type, fits, situation, script):
    """(call, label_source, script_position) for a snap on the sheet.

    Kernel 2014.5, label stream only. In order: the opening sequence on a
    normal down (the lowest unsent opener position whose call can describe
    the snap, ``sheet:opening-sequence``); the snap's applicable menus from
    the most specific to ``normal down`` (``sheet:<menu>``, uniform within
    the menu); the uniform rule over the sheet's unrestricted calls
    (``sheet:fallback``; a call declaring menus without ``normal down`` can
    never fall through); then None for a generic label. A sheet declaring no
    menus at all takes the uniform rule under its 2014.4 name ``sheet``.
    """
    pool_all = _candidates(team, play_type, fits)
    if not pool_all:
        return None, None, None
    menus = situation["menus"] if situation else [call_situations.NORMAL]
    if script is not None and menus[0] == call_situations.NORMAL:
        keys = {_canonical(call): call for call in pool_all}
        slot, call = call_situations.next_script_call(
            script["positions"], script["sent"], lambda c: _canonical(c) in keys)
        if call is not None:
            return keys[_canonical(call)], "sheet:" + call_situations.OPENING, slot
    declared = any(call["menus"] for call in _call_sheet(team, play_type)) or (
        script is not None and script["positions"])
    if not declared:
        return pool_all[lrng.randrange(len(pool_all))], "sheet", None
    for menu in menus:
        pool = [call for call in pool_all if menu in call["menus"]]
        if pool:
            return pool[lrng.randrange(len(pool))], "sheet:" + menu, None
    pool = [call for call in pool_all if not call_situations.restricted(call)]
    if pool:
        return pool[lrng.randrange(len(pool))], "sheet:fallback", None
    return None, None, None


def _choose_label(lrng, team, record, runner_group, target_group, runner_rank=None, target_rank=None,
                  situation=None, script=None, scramble_rate=None):
    """(call, label_source, label_groups, scramble, script_position) for one
    resolved snap. `scramble_rate` is the calibration base's (the 2012
    base's when None)."""
    if record.get("kneel"):
        return _engine_label(KNEEL_LABEL, "run"), "kneel", None, False, None
    if record.get("spike"):
        return _engine_label(SPIKE_LABEL, "pass"), "spike", None, False, None
    if record["play_type"] == "run":
        if runner_group == "QB":
            scramble = lrng.random() < (_scramble_rate() if scramble_rate is None else scramble_rate)
            if scramble:
                call, source, slot = _menu_select(lrng, team, "pass", lambda call: True, situation, script)
                if call is None:
                    return _engine_label(SCRAMBLE_LABEL, "pass"), "generic", None, True, None
                return call, source, _groups(call["target"]), True, slot
        call, source, slot = _menu_select(
            lrng, team, "run", lambda call: isinstance(call["carrier"], tuple)
            and runner_group in call["carrier"]
            and _personnel_fits(call, runner_group, runner_rank), situation, script)
        if call is None:
            return _engine_label(GENERIC_RUN, "run"), "generic", None, False, None
        return call, source, _groups(call["carrier"]), False, slot
    if record.get("sack"):
        fits = lambda call: True
    else:
        fits = lambda call: (call["target"] == call_families.ANY or (
            isinstance(call["target"], tuple) and target_group in call["target"]))\
            and _personnel_fits(call, target_group, target_rank)
    call, source, slot = _menu_select(lrng, team, "pass", fits, situation, script)
    if call is None:
        return _engine_label(GENERIC_PASS, "pass"), "generic", None, False, None
    return call, source, _groups(call["target"]), False, slot


def _scramble_rate(base=None):
    """The base's QB scramble share of QB carries (the 2012 base's when None)."""
    from .calibration_base import BASE_2012
    scrambles, qb_rushes = (base or BASE_2012).field_position().load()["rates"]["scramble"]
    return scrambles / qb_rushes


def _bump(line, field, amount=1):
    line[field] = line.get(field, 0) + amount


def _max(line, field, value):
    line[field] = max(line.get(field, 0), value)


def _call_counter(call_stats, call):
    key = call["name"]
    return call_stats.setdefault(
        key,
        {
            "family": call["family"],
            "snaps": 0,
            "runs": 0,
            "dropbacks": 0,
            "pass_attempts": 0,
            "completions": 0,
            "yards": 0,
            "touchdowns": 0,
            "turnovers": 0,
            "sacks": 0,
        },
    )


PERIOD_BOUNDARIES = {2700: 1, 1800: 2, 900: 3, 0: 4}


def _period_clock(remaining, closing=False, overtime=False):
    """(period, clock text) for seconds remaining in regulation (or the OT
    period). At an exact quarter boundary a closing row is labelled with the
    earlier period at 0:00 and an opening row with the later period at 15:00."""
    remaining = max(0, int(remaining))
    if isinstance(overtime, tuple):
        # Kernel 2013.8 postseason overtime: ("OT", periods, length) lays the
        # periods on one continuous countdown of periods * length seconds, so
        # a possession continues across a period break. Periods are "OT",
        # "OT2", "OT3"; an exact boundary closes the earlier period at 0:00
        # and opens the later one at the full period length.
        _, periods, length = overtime
        elapsed = periods * length - remaining
        number, in_period = divmod(elapsed, length)
        if closing and in_period == 0 and number > 0:
            number, left = number, 0
        else:
            number, left = number + 1, length - in_period
        label = "OT" if number == 1 else "OT%d" % number
        return label, "%d:%02d" % (left // 60, left % 60)
    if overtime:
        label = overtime if isinstance(overtime, str) else "OT"
        return label, "%d:%02d" % (remaining // 60, remaining % 60)
    if closing and remaining in PERIOD_BOUNDARIES:
        return PERIOD_BOUNDARIES[remaining], "0:00"
    if remaining > 2700:
        period, in_period = 1, remaining - 2700
    elif remaining > 1800:
        period, in_period = 2, remaining - 1800
    elif remaining > 900:
        period, in_period = 3, remaining - 900
    else:
        period, in_period = 4, remaining
    return period, "%d:%02d" % (in_period // 60, in_period % 60)


def _order_ok(values, order, low, high):
    total = 0
    for index in order:
        total += values[index]
        if not low <= total <= high:
            return False
    return True


def _prefix_order(values, rng, low, high, budget=4000):
    """Order snap values so every running total stays inside [low, high].

    Keeps the snap-rng order when it already qualifies, otherwise takes the
    first qualifying snap at each step, then a bounded depth-first search.
    Returns None when no order is found; the caller then repairs the values
    within their kind (totals unchanged) or counts a failure."""
    order = list(range(len(values)))
    if _order_ok(values, order, low, high):
        return order
    remaining = list(order)
    total = 0
    out = []
    while remaining:
        pick = next((pos for pos, i in enumerate(remaining) if low <= total + values[i] <= high), None)
        if pick is None:
            break
        index = remaining.pop(pick)
        total += values[index]
        out.append(index)
    if not remaining:
        return out
    fallback = [i for i in order if values[i] < 0] + sorted(
        (i for i in order if values[i] >= 0), key=lambda i: values[i])
    if _order_ok(values, fallback, low, high):
        return fallback
    # Bounded depth-first search, values tried nearest the band's middle first.
    middle = (low + high) / 2
    nodes = [0]
    seen = set()

    def search(total, left, path):
        nodes[0] += 1
        if nodes[0] > budget:
            return None
        if not left:
            return path
        key = (total, tuple(sorted(values[i] for i in left)))
        if key in seen:
            return None
        seen.add(key)
        tried = set()
        for i in sorted(left, key=lambda i: (abs(total + values[i] - middle), i)):
            if values[i] in tried or not low <= total + values[i] <= high:
                continue
            tried.add(values[i])
            found = search(total + values[i], [j for j in left if j != i], path + [i])
            if found is not None:
                return found
        return None

    return search(0, order, [])


def _terminal_kind(rng, category, td_type, runs, attempts, sacks):
    if category == "touchdown":
        return "catch" if td_type == "pass" else "run"
    if category == "interception":
        return "int"
    if category == "fumble_lost":
        options = [(k, n) for k, n in (("run", runs), ("catch", attempts), ("sack", sacks)) if n]
        if options:
            return rng.choices([k for k, _ in options], weights=[n for _, n in options], k=1)[0]
    return None


BASE_KIND = {"catch": "att", "int": "att", "att": "att", "run": "run", "sack": "sack"}
SAME_KIND = {"catch": ("att", "catch"), "att": ("att", "catch"), "run": ("run",), "sack": ("sack",)}


def _layout(rng, category, terminal, runs, attempts, sacks, kneel_yards, spikes, pass_yards, rush_free,
            losses, safety_terminal, net, spot, completion_rate, repair=True, usage_values=None):
    """Kinds, completions and per-snap values of one drive, ordered so the
    running spot stays in the field before the terminal snap. Totals by kind
    are fixed by the kernel; only the order and the split within a kind move."""
    counts = {"run": runs, "att": attempts, "sack": sacks}
    if terminal:
        counts[BASE_KIND[terminal]] -= 1
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
    for index, value in zip(completion_slots, _allocate(pass_yards, len(completion_slots), rng)):
        values[index] = value
    for index, value in zip(run_slots, _allocate_runs(rush_free, len(run_slots), rng, usage_values)):
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

    # Running spot bounds: before the terminal snap the ball stays in the
    # field (spot S - total in [1, 99]).
    low, high = spot - 99, spot - 1
    free_index = list(range(len(movable)))
    tail = list(range(len(movable), plays))

    def ordered():
        return _prefix_order([values[i] for i in free_index], rng, low, high)

    def tail_ok():
        total = sum(values[i] for i in free_index)
        for position, index in enumerate(tail):
            total += values[index]
            final = position == len(tail) - 1 and terminal is not None
            if final and category == "touchdown":
                if total != net:
                    return False
            elif final and category == "safety":
                if total != spot - 100:
                    return False
            elif not low <= total <= high:
                return False
        return True

    order = ordered()
    repaired = False
    if order is None or not tail_ok():
        order = None
        if repair:
            repaired = True
            # Repair 1: exchange the terminal value with a same-kind snap.
            if terminal and category != "safety":
                for candidate in [i for i in free_index if kinds[i] in SAME_KIND.get(kinds[last], ())
                                  and (kinds[last] != "catch" or completed[i])]:
                    if category == "touchdown" and values[candidate] < 1:
                        continue
                    values[last], values[candidate] = values[candidate], values[last]
                    trial = ordered()
                    if trial is not None and tail_ok():
                        order = trial
                        break
                    values[last], values[candidate] = values[candidate], values[last]
            # Repair 2: move one yard at a time from the largest to the
            # smallest value of the same kind (kind totals unchanged).
            if order is None:
                # A touchdown's scoring snap (or a fumbled run or catch) joins
                # its kind; the scoring snap keeps at least one yard.
                with_terminal = terminal in ("catch", "run") and category in ("touchdown", "fumble_lost")
                groups = [[i for i in free_index if completed[i]] + ([last] if with_terminal and terminal == "catch" else []),
                          [i for i in free_index if kinds[i] == "run"] + ([last] if with_terminal and terminal == "run" else [])]
                for _ in range(400):
                    moved = False
                    for group in groups:
                        if len(group) < 2:
                            continue
                        big = max(group, key=lambda i: (values[i], -i))
                        small = min(group, key=lambda i: (values[i], i))
                        if big == last and category == "touchdown" and values[big] <= 1:
                            continue
                        if values[big] - values[small] >= 2:
                            values[big] -= 1
                            values[small] += 1
                            moved = True
                    trial = ordered()
                    if trial is not None and tail_ok():
                        order = trial
                        break
                    if not moved:
                        break
    ok = order is not None
    if order is None:
        order = list(range(len(free_index)))
    permutation = [free_index[i] for i in order] + tail
    rows = _seat_spikes([(kinds[i], completed[i], values[i]) for i in permutation], len(free_index))
    return {"ok": ok, "repaired": repaired and ok,
            "kinds": [row[0] for row in rows],
            "completed": [row[1] for row in rows],
            "values": [row[2] for row in rows]}


def _clock_runs_after(row):
    """True when the game clock keeps running after this snap: a run, a sack
    or a completed pass. An incompletion or a spike stops it."""
    kind, completed, _ = row
    return kind in ("run", "sack") or (kind in ("att", "catch") and completed)


def _seat_spikes(rows, movable):
    """Kernel 2013.9: a spike only stops a running clock. Every possession
    starts on a stopped clock (a change of possession is an administrative
    stoppage, library/2013_nfl_playing_rules_for_simulation.md R14), and an
    incompletion or a spike stops it again, so a spike may not be a drive's
    first snap or follow one of those. Each misplaced spike (value 0) moves,
    within the free prefix, to just after the nearest snap that leaves the
    clock running, earlier first. Prefix sums are unchanged because a spike
    gains nothing; no randomness is consumed. A drive with no such snap keeps
    its spike after the first snap (never first)."""
    rows = list(rows)
    for _ in range(movable):
        bad = next((p for p in range(movable) if rows[p][0] == "spike" and not (
            p > 0 and _clock_runs_after(rows[p - 1]))), None)
        if bad is None:
            break
        spike = rows.pop(bad)
        prefix = movable - 1
        slots = [q for q in range(1, prefix + 1) if _clock_runs_after(rows[q - 1])
                 and not (q < prefix and rows[q][0] == "spike")]
        if slots:
            target = min(slots, key=lambda q: (abs(q - bad), q > bad))
        else:
            target = min(1, prefix)
        rows.insert(target, spike)
        if not slots:
            break
    return rows


def apply_drive_detail(
    *,
    seed,
    event_id,
    drive_no,
    team,
    defense,
    available,
    defenders,
    offense_stats,
    defense_stats,
    runs,
    attempts,
    sacks,
    pass_yards,
    rush_free,
    category,
    start_clock,
    end_clock,
    start_spot,
    kneel_yards=(),
    spikes=0,
    td_type=None,
    turnover_type=None,
    sack_losses=(),
    safety_terminal=None,
    fg_made=None,
    fg_distance=None,
    xp_made=None,
    net_yards=0,
    overtime=False,
    punt_record=None,
    turnover_record=None,
    fourth_down=None,
    passer=None,
    diagnostics=None,
    own_seconds=None,
    layout=None,
    score_diff=0,
    start_kind=None,
    game_ledger=(),
    calibration_base=None,
    usage_base=None,
):
    """Allocate one resolved drive into reconciled player/snap public detail.

    Every number that changes the score, possession, clock, ball spot or a
    team counter arrives from the kernel: the real snap counts (runs,
    attempts, sacks, kneels, spikes), the passing and free rushing totals,
    the sack losses, the terminal kind and the transition records. This
    stream only decides who, in what order and how the already-fixed yardage
    splits across snaps, keeping the running ball spot inside the field
    before the terminal snap. The terminal snap (touchdown, turnover, safety)
    is always the drive's last scrimmage snap; kneels come immediately before
    any punt, field-goal or downs row.

    Kernel 2014.4: the kernel passes `layout` (runtime.chains.drive_layout,
    its own chain-layout stream), which fixes the snap kinds, completions,
    yards and order because the chain walk over them feeds team counters.
    This stream then only names the players. Without a layout (direct
    callers and tests) the legacy layout below runs on this stream.

    Kernel 2014.5: `score_diff` (offense minus defense at the drive's start),
    `start_kind` and `game_ledger` (the game's rows so far) feed only the
    label stream: each snap's call label is chosen from the sheet's menu for
    its down, distance, zone and clock, or from the opening sequence in
    script order (runtime.call_situations). None of them reaches a draw.

    Kernel 2014.6 plumbing (batch B1): `calibration_base` is the kernel's
    bound base (runtime.calibration_base); its usage table, completion rate,
    tilt factors and scramble rate are used here. None is the 2012 base.
    Kernel 2014.6 (batch B5): `usage_base` is the base whose usage table
    credits the drive (runtime.profiles.Profile.usage_base); None is
    `calibration_base`. The completion rate is the bound base's
    (runtime.calibration.kernel_rates).
    """
    from .calibration_base import BASE_2012
    from .calibration import kernel_rates
    cbase = calibration_base if calibration_base is not None else BASE_2012
    ubase = usage_base if usage_base is not None else cbase
    rng = _rng(seed, event_id=event_id, drive_no=drive_no, offense=team.team_id)
    shares = ubase.usage()["values"]
    rank_shapes = shares["rank_shares"]
    completion_rate = kernel_rates(cbase.aggregate(), None if cbase.legacy_2012() else BASE_2012.aggregate())[
        "completion_rate"]
    tilt_factors = ubase.tilt_factors()
    scramble_rate = _scramble_rate(cbase)
    diagnostics = diagnostics if diagnostics is not None else {}
    kneel_yards = list(kneel_yards)
    losses = list(sack_losses)
    spot = int(start_spot)
    net = int(net_yards)

    if layout is not None:
        terminal = layout["terminal"]
    else:
        if category == "safety":
            terminal = safety_terminal[0]
        else:
            terminal = _terminal_kind(rng, category, td_type, runs, attempts, sacks)
        # A lost fumble's terminal kind is descriptive (which snap was fumbled):
        # when the drawn kind cannot be ordered inside the field, the others are
        # tried in a fixed order before any value repair.
        options = [terminal]
        if category == "fumble_lost":
            options += [k for k, n in (("run", runs), ("catch", attempts), ("sack", sacks)) if n and k != terminal]
        for attempt, terminal in enumerate(options):
            layout = _layout(rng, category, terminal, runs, attempts, sacks, kneel_yards, spikes, pass_yards,
                             rush_free, losses, safety_terminal, net, spot, completion_rate,
                             repair=attempt == len(options) - 1, usage_values=shares)
            if layout["ok"] or attempt == len(options) - 1:
                break
        if layout["repaired"] or attempt:
            diagnostics["prefix_order_repaired"] = diagnostics.get("prefix_order_repaired", 0) + 1
        if not layout["ok"]:
            diagnostics["prefix_order_failed"] = diagnostics.get("prefix_order_failed", 0) + 1
    kinds, completed, values = layout["kinds"], layout["completed"], layout["values"]
    plays = len(kinds)
    last = plays - 1

    # The kernel supplies this drive's passer (kernel 2014.4: chosen per
    # drive from the players still available); else the depth-chart QB1.
    qb = passer or usage.game_passer(available) or choose(rng, available, {"QB"}, "passer")
    qb_line = offense_stats["players"][qb.player_id]
    # Kernel 2014.3: the five linemen on the field (same for every drive).
    front = usage.protection_front(available)
    # Kernel 2014.4 (defect register item 19): tier-weighted credit from each
    # club's strength record; empty without one (runtime/usage.tilt_map).
    target_tilt = usage.tilt_map(getattr(team, "strength", None), available, "target", tilt_factors)
    rush_tilt = usage.tilt_map(getattr(team, "strength", None), available, "rush", tilt_factors)
    sack_tilt = usage.tilt_map(getattr(defense, "strength", None), defenders, "sack", tilt_factors)

    drive_seconds = max(0, int(start_clock) - int(end_clock))
    # Kernel 2014.4: scrimmage snaps are stamped inside the drive's own
    # seconds. A window-ending drive's clock-expiry leg (drive_seconds -
    # own) runs after its last snap and belongs to the terminal
    # possession-end row at end_clock; no snap is stamped inside it.
    own = drive_seconds if own_seconds is None else max(0, min(int(own_seconds), drive_seconds))
    own_end = int(start_clock) - own
    ledger = []
    groups_for = {}
    remaining_at = []

    def clock_at(remaining):
        return _period_clock(remaining, closing=remaining <= int(end_clock), overtime=overtime)

    def fumble(line, record):
        _bump(line, "fumbles")
        _bump(line, "fumbles_lost")
        defender = usage.pick(rng, defenders, shares["tackle_share"], "defense", role="tackle",
                              rank_shapes=rank_shapes)
        def_line = defense_stats["players"][defender.player_id]
        _bump(def_line, "forced_fumbles")
        _bump(def_line, "fumble_recoveries")
        _bump(def_line, "tackles")
        _bump(def_line, "solo_tackles")
        record["turnover"] = True
        record["turnover_type"] = "fumble"
        record["tackler"] = defender.player_id

    running = 0
    for index in range(plays):
        snap_no = index + 1
        remaining = int(start_clock) - round(own * snap_no / plays)
        remaining_at.append(remaining)
        period, game_clock = clock_at(remaining)
        kind = kinds[index]
        is_terminal = terminal is not None and index == last
        is_pass = kind in ("att", "catch", "int", "sack", "spike")
        yards = values[index]

        record = {
            "drive": drive_no,
            "snap_in_drive": snap_no,
            "period": period,
            "game_clock": game_clock,
            "offense": team.team_id,
            "defense": defense.team_id,
            "play_type": "pass" if is_pass else "run",
            "yardline": spot - running,
            "passer": None,
            "runner": None,
            "target": None,
            "blocker": None,
            "tackler": None,
            "assist_tackler": None,
            "result_yards": 0,
            "passing_yards": 0,
            "rushing_yards": 0,
            "completion": False,
            "sack": False,
            "turnover": False,
            "turnover_type": None,
            "touchdown": False,
            "kneel": kind == "kneel",
            "spike": kind == "spike",
        }
        running += yards

        if kind == "sack":
            loss = -yards
            record["passer"] = qb.player_id
            _bump(qb_line, "dropbacks")
            record["sack"] = True
            record["result_yards"] = yards
            _bump(qb_line, "sacks_taken")
            _bump(qb_line, "sack_yards", loss)
            # Kernel 2014.3: the rusher first, then the on-field lineman
            # facing him (edge rushers beat a tackle, interior rushers a
            # guard or the center).
            rusher = usage.pick(rng, defenders, shares["sack_share"], "defense", role="pass_rush",
                                tilt=sack_tilt, rank_shapes=rank_shapes)
            if front:
                slots = usage.beaten_slots(rusher, front)
                slot = slots[0] if len(slots) == 1 else rng.choice(slots)
                blocker = front[slot]
            else:
                slot, blocker = None, choose(rng, available, OFFENSIVE_LINE, "pass_protection")
            _bump(offense_stats["players"][blocker.player_id], "sacks_allowed")
            record["blocker"] = blocker.player_id
            record["blocker_slot"] = slot
            _bump(defense_stats["players"][rusher.player_id], "sacks")
            _bump(defense_stats["players"][rusher.player_id], "pressures")
            _bump(defense_stats["players"][rusher.player_id], "tackles")
            _bump(defense_stats["players"][rusher.player_id], "solo_tackles")
            record["tackler"] = rusher.player_id
            if is_terminal and category == "fumble_lost":
                _bump(qb_line, "fumbles")
                _bump(qb_line, "fumbles_lost")
                _bump(defense_stats["players"][rusher.player_id], "forced_fumbles")
                _bump(defense_stats["players"][rusher.player_id], "fumble_recoveries")
                record["turnover"] = True
                record["turnover_type"] = "fumble"
        elif kind == "spike":
            record["passer"] = qb.player_id
            _bump(qb_line, "dropbacks")
            _bump(qb_line, "pass_attempts")
        elif is_pass:
            record["passer"] = qb.player_id
            _bump(qb_line, "dropbacks")
            receiver = usage.pick(rng, available, shares["target_share"], "target", role="receiver",
                                  tilt=target_tilt, rank_shapes=rank_shapes)
            rec_line = offense_stats["players"][receiver.player_id]
            record["target"] = receiver.player_id
            groups_for[index] = (None, usage.group(receiver.position), None, _group_rank(available, receiver))
            _bump(qb_line, "pass_attempts")
            _bump(rec_line, "targets")

            if kind == "int":
                _bump(qb_line, "interceptions")
                _bump(qb_line, "interceptions_thrown")
                defender = usage.pick(rng, defenders, shares["interception_share"], "defense", role="coverage",
                                      rank_shapes=rank_shapes)
                def_line = defense_stats["players"][defender.player_id]
                _bump(def_line, "defensive_interceptions")
                return_yards = int(turnover_record["return_yards"]) if turnover_record else 0
                _bump(def_line, "interception_return_yards", return_yards)
                _bump(def_line, "passes_defended")
                record["turnover"] = True
                record["turnover_type"] = "interception"
                record["tackler"] = defender.player_id
                record["return_yards"] = return_yards
            elif completed[index]:
                record["completion"] = True
                record["passing_yards"] = yards
                record["result_yards"] = yards
                _bump(qb_line, "completions")
                _bump(qb_line, "passing_yards", yards)
                _bump(rec_line, "receptions")
                _bump(rec_line, "receiving_yards", yards)
                _max(rec_line, "long_reception", yards)
                if is_terminal and category == "touchdown":
                    record["touchdown"] = True
                    _bump(qb_line, "passing_touchdowns")
                    _bump(rec_line, "receiving_touchdowns")
                elif is_terminal and category == "fumble_lost":
                    record["runner"] = None
                    fumble(rec_line, record)
                else:
                    _credit_tackle(rng, defenders, defense_stats, record, usage_values=shares)
            else:
                if rng.random() < 0.35:
                    cover = usage.pick(rng, defenders, shares["pass_defensed_share"], "defense", role="coverage",
                                       rank_shapes=rank_shapes)
                    _bump(defense_stats["players"][cover.player_id], "passes_defended")
                    record["tackler"] = cover.player_id
                if rng.random() < 0.20:
                    pressure = usage.pick(rng, defenders, shares["sack_share"], "defense", role="pass_rush",
                                          tilt=sack_tilt, rank_shapes=rank_shapes)
                    _bump(defense_stats["players"][pressure.player_id], "pressures")
        elif kind == "kneel":
            run_line = qb_line
            record["runner"] = qb.player_id
            record["rushing_yards"] = yards
            record["result_yards"] = yards
            groups_for[index] = (usage.group(qb.position), None, 1, None)
            _bump(run_line, "rushing_attempts")
            _bump(run_line, "rushing_yards", yards)
        else:
            runner = usage.pick(
                rng, available, shares["rush_share"], "rush", role="rusher",
                only=lambda p: usage.group(p.position) != "QB" or p.player_id == qb.player_id,
                tilt=rush_tilt, rank_shapes=rank_shapes,
            )
            run_line = offense_stats["players"][runner.player_id]
            record["runner"] = runner.player_id
            record["rushing_yards"] = yards
            record["result_yards"] = yards
            groups_for[index] = (usage.group(runner.position), None, _group_rank(available, runner), None)
            _bump(run_line, "rushing_attempts")
            _bump(run_line, "rushing_yards", yards)
            _max(run_line, "long_rush", yards)
            if is_terminal and category == "fumble_lost":
                fumble(run_line, record)
            elif is_terminal and category == "touchdown":
                record["touchdown"] = True
                _bump(run_line, "rushing_touchdowns")
            else:
                _credit_tackle(rng, defenders, defense_stats, record, negative=yards < 0, usage_values=shares)

        ledger.append(record)

    terminal_snap = plays + 1
    period, game_clock = _period_clock(end_clock, closing=True, overtime=overtime)
    base = {
        "drive": drive_no, "period": period, "game_clock": game_clock,
        "offense": team.team_id, "defense": defense.team_id,
        "result_yards": 0, "touchdown": False, "turnover": False,
    }
    fourth = {}
    if fourth_down is not None:
        fourth = {"down": fourth_down["down"], "ydstogo": fourth_down["ydstogo"], "los": fourth_down["los"]}

    def kicker_line():
        kicker = usage.kicking_specialist(available, "K", "placekicker") or choose(rng, available, {"K"}, "placekicker")
        return kicker, offense_stats["players"][kicker.player_id]

    def snap():
        """Kernel 2014.3: the long snapper on every punt, field goal and try."""
        snapper = usage.long_snapper(available, front)
        if snapper is None:
            return None
        _bump(offense_stats["players"][snapper.player_id], "long_snaps")
        return snapper.player_id

    if category == "field_goal_attempt":
        kicker, line = kicker_line()
        _bump(line, "field_goals_attempted")
        if fg_made:
            _bump(line, "field_goals_made")
        ledger.append({**base, "snap_in_drive": terminal_snap, "play_type": "field_goal",
                       "kicker": kicker.player_id, "made": bool(fg_made), "distance": fg_distance,
                       "long_snapper": snap(), **fourth})
    elif category == "punt":
        punter = usage.kicking_specialist(available, "P", "punt") or choose(rng, available, {"P"}, "punt")
        line = offense_stats["players"][punter.player_id]
        los, gross = punt_record["los"], punt_record["gross"]
        ret, touchback = punt_record["return_yards"], punt_record["touchback"]
        _bump(line, "punts")
        _bump(line, "punt_yards", gross)
        _max(line, "long_punt", gross)
        if touchback:
            _bump(line, "punt_touchbacks")
        elif 100 - los + gross - ret >= 81:
            _bump(line, "punts_inside_20")
        snapper = snap()
        returner = cover = None
        if punt_record["outcome"] == "returned":
            returner = _returner(rng, defenders, "punt_return")
            rline = defense_stats["players"][returner.player_id]
            _bump(rline, "punt_returns")
            _bump(rline, "punt_return_yards", ret)
            _bump(rline, "return_yards", ret)
            returner = returner.player_id
            tackler = _coverage_tackle(rng, available, offense_stats["players"], "punt_coverage", (punter,))
            cover = tackler.player_id if tackler else None
        ledger.append({**base, "snap_in_drive": terminal_snap, "play_type": "punt",
                       "punter": punter.player_id, "cover_player": cover, "long_snapper": snapper,
                       "punt_yards": gross, "returner": returner, "return_yards": ret,
                       "gross": gross, "enforcement": punt_record["enforcement"],
                       "outcome": punt_record["outcome"], "touchback": touchback,
                       "next_start": punt_record["next_start"], **fourth})
    elif category == "touchdown" and xp_made is not None:
        kicker, line = kicker_line()
        _bump(line, "extra_points_attempted")
        if xp_made:
            _bump(line, "extra_points_made")
        # Kernel 2014.4: the untimed try (and a safety below) sits with its
        # scoring snap at the drive's own end, not after the expiry leg.
        period, game_clock = clock_at(own_end)
        ledger.append({**base, "period": period, "game_clock": game_clock,
                       "snap_in_drive": terminal_snap, "play_type": "extra_point",
                       "kicker": kicker.player_id, "made": bool(xp_made), "long_snapper": snap()})
    elif category == "safety":
        period, game_clock = clock_at(own_end)
        ledger.append({**base, "period": period, "game_clock": game_clock,
                       "snap_in_drive": terminal_snap, "play_type": "safety",
                       "scoring_team": defense.team_id})
    elif category in POSSESSION_END_REASONS:
        ledger.append({**base, "snap_in_drive": terminal_snap, "play_type": "possession_end",
                       "reason": category, **(fourth if category == "downs" else {})})

    # Descriptive call labels on their own stream, after every player is named.
    lrng = _label_rng(seed, event_id=event_id, drive_no=drive_no, offense=team.team_id)
    call_stats = {}
    # Kernel 2014.5: the situation of each snap (its walked down and distance,
    # zone, half clock and score) and the offense's opening sequence so far.
    walk = layout.get("walk") if isinstance(layout, dict) else None
    if walk is None:
        walk = chain_walk.walk(spot, values, category in chain_walk.TURNOVER_TERMINALS)
    states = walk["rows"]
    sheet = [_normalize_call(item, "any") for item in (getattr(team, "offensive_call_sheet", ()) or ())]
    positions = call_situations.script_positions(sheet)
    snaps_before, sent = call_situations.script_state(game_ledger, team.team_id)
    script_snaps = snaps_before
    for index, record in enumerate(ledger[:plays]):
        runner_group, target_group, runner_rank, target_rank = groups_for.get(index, (None, None, None, None))
        state = states[index] if index < len(states) else None
        half, left = call_situations.half_clock(start_clock, remaining_at[index], overtime)
        menus = call_situations.classify(
            down=state["down"] if state else 1,
            ydstogo=state["ydstogo"] if state else None,
            yardline=state["los"] if state else record["yardline"],
            goal_to_go=state["goal_to_go"] if state else False,
            half=half, half_remaining=left, score_diff=int(score_diff or 0),
            start_kind=start_kind, snap_index=index)
        situation = {"menus": menus}
        script = None
        scrimmage = not (record.get("kneel") or record.get("spike"))
        if positions and scrimmage and script_snaps < len(positions):
            script = {"positions": positions, "sent": sent}
        call, source, label_groups, scramble, slot = _choose_label(
            lrng, team, record, runner_group, target_group, runner_rank, target_rank, situation, script,
            scramble_rate)
        if scrimmage:
            script_snaps += 1
        if slot is not None:
            sent.add(slot)
        record.update({
            "concept": call["name"], "family": call["family"], "personnel": call["personnel"],
            "formation": call["formation"], "motion": call["motion"], "protection": call["protection"],
            "tags": list(call["tags"]), "scramble": scramble, "carrier_group": runner_group,
            "target_group": target_group, "label_groups": label_groups, "label_source": source,
            "label_type": call["type"], "situation": menus[0], "script_position": slot,
        })
        counter = _call_counter(call_stats, call)
        counter["snaps"] += 1
        counter["yards"] += record["result_yards"]
        if record["play_type"] == "run":
            counter["runs"] += 1
        else:
            counter["dropbacks"] += 1
            if record["sack"]:
                counter["sacks"] += 1
            else:
                counter["pass_attempts"] += 1
                counter["completions"] += int(record["completion"])
        counter["touchdowns"] += int(record["touchdown"])
        counter["turnovers"] += int(record["turnover"])

    return ledger, call_stats


POSSESSION_END_REASONS = ("downs", "end_of_half", "end_of_game", "end_of_overtime", "end_of_quarter")


def apply_kickoff_detail(*, seed, event_id, kick_no, kicking, receiving, rosters, stats,
                         returned, remaining, drive, free_kick=False, overtime=False, record=None):
    """Public row for one kickoff or post-safety free kick.

    The kernel has already drawn the real 2012 kick record (touchback, kick
    yards, return yards, enforcement, outcome and the next start); this
    separate stream only names the kicker and returner, so it cannot change
    any score, clock, spot or team counter."""
    rng = _stream(KICKOFF_DETAIL_TAG, seed, event_id, kick_no)
    record = record or {}
    kicking_players = rosters[kicking.team_id]
    kicker = usage.kicking_specialist(kicking_players, "K", "placekicker") or choose(
        rng, kicking_players, {"K"}, "placekicker")
    period, game_clock = _period_clock(remaining, overtime=overtime)
    row = {
        "drive": drive, "snap_in_drive": 0, "period": period, "game_clock": game_clock,
        "offense": kicking.team_id, "defense": receiving.team_id,
        "play_type": "free_kick" if free_kick else "kickoff",
        "kicker": kicker.player_id, "touchback": not returned,
        "returner": None, "return_yards": 0, "result_yards": 0, "cover_player": None,
        "touchdown": False, "turnover": False,
        "kick_yards": record.get("kick_yards"), "enforcement": record.get("enforcement"),
        "outcome": record.get("outcome"), "next_start": record.get("next_start"),
    }
    if returned:
        returner = _returner(rng, rosters[receiving.team_id], "kick_return")
        return_yards = int(record.get("return_yards") or 0)
        line = stats[receiving.team_id]["players"][returner.player_id]
        _bump(line, "kick_returns")
        _bump(line, "kick_return_yards", return_yards)
        _bump(line, "return_yards", return_yards)
        row["returner"] = returner.player_id
        row["return_yards"] = return_yards
        row["result_yards"] = return_yards
        if record.get("outcome", "returned") == "returned":
            tackler = _coverage_tackle(rng, kicking_players, stats[kicking.team_id]["players"],
                                       "kickoff_coverage", (kicker,))
            row["cover_player"] = tackler.player_id if tackler else None
    return [row]


# ---- ledger coherence ------------------------------------------------------

class CoherenceClass:
    """One zero-tolerance ledger-coherence class (kernel 2014.6 plumbing, B1).

    `group` names the receipts it applies to; `measurable(result)` is its
    measurable predicate (evaluated only on a result or receipt with
    possessions); `listed_from` is None for a class every cohort's audit
    table lists (each of the 42 classes through kernel 2014.5), or the first
    kernel cohort whose table lists it. A class added for kernel 2014.6 is
    gated by the kernel marker in its predicate (from_kernel) and listed only
    from that cohort, so closed cohorts' tables never change."""

    __slots__ = ("name", "group", "measurable", "listed_from")

    def __init__(self, name, group, measurable, listed_from=None):
        self.name, self.group, self.measurable, self.listed_from = name, group, measurable, listed_from

    def __repr__(self):
        return "CoherenceClass(%r, %r)" % (self.name, self.group)


def from_kernel(version):
    """A measurable-predicate marker: True for a result or receipt of that
    kernel version or later (runtime.statbook.kernel_at_least)."""
    from .statbook import kernel_at_least
    minimum = tuple(int(v) for v in str(version).split("."))
    return lambda result: kernel_at_least(result.get("kernel_version"), minimum)


def _ledger(result):
    return bool(result.get("play_ledger"))


# The measurable predicate of each group (see measurable_classes).
_GROUP_PREDICATES = {
    # The 15 original classes: every result or receipt with possessions.
    "legacy": lambda r: True,
    # Kernel 2013.7 onward: evaluated only when every possession carries a
    # start spot. The ledger-free ones read the drives summary; the kick-row
    # and label classes need the full snap ledger.
    "spot": lambda r: has_spots(r),
    "spot_ledger": lambda r: has_spots(r) and _ledger(r),
    # Kernel 2014.1 onward: evaluated only when every possession carries the
    # timeout state.
    "timeout": lambda r: has_spots(r) and has_timeouts(r),
    # Kernel 2014.4 onward: evaluated only when every possession carries its
    # own seconds and clock-expiry leg (has_clock_legs); snap_after_expiry
    # needs the full snap ledger.
    "clock_leg": lambda r: has_clock_legs(r),
    "clock_leg_ledger": lambda r: has_clock_legs(r) and _ledger(r),
    # Kernel 2014.4 onward (defect register item 3): evaluated only when the
    # snap ledger carries the walked down and distance (has_chain_ledger).
    "chain": lambda r: has_chain_ledger(r),
    # Kernel 2014.4 phase 2: evaluated when every possession carries the
    # walked chain model (has_chain_model); a drive that published a layout
    # resample must name a real pool, a real original tuple and a final
    # tuple of the same category feasible at its start spot.
    "resample": lambda r: has_chain_model(r),
}


def _registry(rows):
    return tuple(CoherenceClass(name, group, _GROUP_PREDICATES[group]) for group, names in rows for name in names)


COHERENCE_REGISTRY = _registry((
    ("legacy", ("snaps_after_terminal", "drives_missing_terminal", "duplicate_terminal",
                "drives_spanning_half", "wrong_second_half_receiver", "missing_half_kickoff",
                "kickoff_after_expired_clock", "xp_after_ot_walkoff", "td_snap_sack_or_nonpositive",
                "drive_net_outside_2012_range", "snap_sum_ne_drive_net", "prefix_out_of_bounds",
                "clock_regression", "score_identity_violations", "ot_end_inconsistent")),
    ("spot", ("start_spot_out_of_field", "td_net_ne_start", "safety_not_at_goal_line",
              "safety_start_infeasible", "end_spot_identity", "spot_chain_break")),
    ("spot_ledger", ("kick_spot_mismatch",)),
    ("spot", ("fg_distance_offset", "category_impossible_at_start",
              "late_terminal_state_mismatch", "fourth_down_state_missing", "chain_counter_mismatch")),
    ("spot_ledger", ("label_type_mismatch", "label_carrier_mismatch", "label_target_mismatch",
                     "scramble_with_designed_label", "kneel_spike_mislabelled")),
    ("timeout", ("timeout_state_invalid", "fourth_down_beyond_goal")),
    ("clock_leg", ("seconds_per_snap_outside",)),
    ("clock_leg_ledger", ("snap_after_expiry",)),
    ("clock_leg", ("expiry_leg_exceeds_allowance",)),
    ("chain", ("down_distance_chain_break", "fourth_down_distance_mismatch", "first_downs_ne_ledger",
               "goal_to_go_mismatch")),
    ("resample", ("layout_resample_incoherent",)),
))


def _names(*groups):
    return tuple(c.name for c in COHERENCE_REGISTRY if c.group in groups)


COHERENCE_CLASSES = tuple(c.name for c in COHERENCE_REGISTRY)
RESAMPLE_CLASSES = _names("resample")
TIMEOUT_CLASSES = _names("timeout")
CLOCK_LEG_CLASSES = _names("clock_leg", "clock_leg_ledger")
CLOCK_LEG_LEDGER_CLASSES = _names("clock_leg_ledger")
CHAIN_CLASSES = _names("chain")
# Frozen by group, never by slicing: a class added later (gated by its
# kernel marker) joins neither the 15 original classes nor the spot classes.
LEGACY_CLASSES = _names("legacy")
SPOT_CLASSES = _names("spot", "spot_ledger")
SPOT_LEDGER_CLASSES = _names("spot_ledger")


def classes_for_cohort(version=None):
    """The classes a cohort's audit table lists: every class with no
    listed_from, plus those listed from that kernel cohort or earlier."""
    from .statbook import kernel_at_least
    out = []
    for c in COHERENCE_REGISTRY:
        if c.listed_from is None or (version is not None and kernel_at_least(
                version, tuple(int(v) for v in c.listed_from.split(".")))):
            out.append(c.name)
    return tuple(out)
KICK_TYPES = ("kickoff", "free_kick")
FOURTH_DOWN_ACTION = {"punt": "punt", "field_goal_attempt": "field_goal", "downs": "go"}
MARKER_FOR = {
    "touchdown": "touchdown", "field_goal_attempt": "field_goal", "punt": "punt",
    "interception": "interception", "fumble_lost": "fumble", "safety": "safety",
    "downs": "possession_end", "end_of_half": "possession_end",
    "end_of_game": "possession_end", "end_of_overtime": "possession_end",
    "end_of_quarter": "possession_end",
}
DRIVE_SUMMARY_FIELDS = (
    "number", "team", "half", "category", "points", "scrimmage_plays", "start_clock",
    "end_clock", "net_yards", "fg_distance", "fg_made", "xp_made", "kickoff_after",
    "half_final",
    # Kernel 2013.7 onward (append-only; 2013.6 rows zip shorter).
    "start_spot", "start_kind", "end_spot", "next_start", "score_diff", "cell",
    "tuple_terminal_bucket", "chains", "fourth_down", "kneels", "spikes",
    # Kernel 2014.1 onward (append-only).
    "timeouts", "timeout_level",
    # Kernel 2014.4 onward (append-only): own seconds, clock-expiry leg, the drive's passer, chain model.
    "own_seconds", "expiry_seconds", "passer", "chain_model",
    # Kernel 2014.4 phase 2 (append-only): the punt transition as adjusted,
    # the layout resample record, the field-goal probability drawn against.
    "punt", "layout_resample", "fg_prob",
)
LABEL_TYPES = {KNEEL_LABEL: "run", GENERIC_RUN: "run", SPIKE_LABEL: "pass",
               GENERIC_PASS: "pass", SCRAMBLE_LABEL: "pass"}


def drive_summary(possessions):
    """Compact per-possession list for receipts (ledger-free coherence audit)."""
    return [[p.get(field) for field in DRIVE_SUMMARY_FIELDS] for p in possessions]


def _possessions(result):
    if result.get("possessions") and "category" in result["possessions"][0]:
        return result["possessions"]
    return [dict(zip(DRIVE_SUMMARY_FIELDS, row)) for row in result.get("drives", ())]


def has_spots(result):
    """True for a 2013.7-or-later result or receipt (every drive has a start spot)."""
    possessions = _possessions(result)
    return bool(possessions) and all(p.get("start_spot") is not None for p in possessions)


def measurable_classes(result):
    """The coherence classes this result or receipt can be checked for: each
    registered class whose measurable predicate holds (COHERENCE_REGISTRY)."""
    if not _possessions(result):
        return set()
    return {c.name for c in COHERENCE_REGISTRY if c.measurable(result)}


def has_chain_model(result):
    """True for a kernel 2014.4-or-later result or receipt: every possession
    carries its chains and fourth-down state walked from its own snaps."""
    possessions = _possessions(result)
    return bool(possessions) and all(p.get("chain_model") for p in possessions)


def has_chain_ledger(result):
    """Kernel 2014.4: the chain classes need the walked model and a snap
    ledger whose every scrimmage row carries its down and distance (closed
    2013 receipts and compact receipts are not measured)."""
    ledger = result.get("play_ledger")
    if not ledger or not has_spots(result) or not has_chain_model(result):
        return False
    return all("down" in r and "ydstogo" in r for r in ledger if r.get("play_type") in ("pass", "run"))


def _check_chain_ledger(possessions, rows_by_drive, err):
    """Kernel 2014.4 (defect register item 3): each drive's published down,
    distance, first downs and fourth-down state are re-walked from its own
    scrimmage rows (runtime.chains.walk) and must agree with them."""
    from . import chains
    from .field_position import FOURTH_DOWN_CATEGORIES
    for p in possessions:
        number, category = p["number"], p["category"]
        rows = rows_by_drive.get(number, [])
        scrim = [r for r in rows if r.get("play_type") in ("pass", "run")]
        yards = [r.get("result_yards", 0) for r in scrim]
        start = p["start_spot"]
        w = chains.walk(start, yards, category in chains.TURNOVER_TERMINALS)
        where = "drive %s" % number
        for index, (row, state) in enumerate(zip(scrim, w["rows"])):
            if (row.get("down"), row.get("ydstogo"), row.get("yardline"), bool(row.get("first_down"))) != (
                    state["down"], state["ydstogo"], state["los"], state["first_down"]):
                err("down_distance_chain_break", "%s snap %s: %s & %s at %s" % (
                    where, index + 1, row.get("down"), row.get("ydstogo"), row.get("yardline")))
                break
        failed = w["failed"]
        if w["breaks"] or (failed is not None and not (category == "downs" and failed == len(yards) - 1)):
            err("down_distance_chain_break", "%s snap after a failed fourth down" % where)
        elif category == "downs" and failed is None:
            err("down_distance_chain_break", "%s turned over on downs without failing on fourth" % where)
        elif category == "punt" and (w["state"] is None or w["state"]["down"] != 4) and yards:
            err("down_distance_chain_break", "%s punts before fourth down" % where)
        for index, (row, state) in enumerate(zip(scrim, w["rows"])):
            if bool(row.get("goal_to_go")) != state["goal_to_go"] or (
                    bool(row.get("goal_to_go")) != (row.get("ydstogo") == row.get("yardline"))):
                err("goal_to_go_mismatch", "%s snap %s" % (where, index + 1))
                break
        if category in FOURTH_DOWN_CATEGORIES:
            fd = p.get("fourth_down") or {}
            expected = chains.fourth_down_state(category, start, yards)
            if expected is None or any(fd.get(k) != expected[k] for k in chains.STATE_FIELDS):
                err("fourth_down_distance_mismatch", "%s published %s" % (
                    where, [fd.get(k) for k in chains.STATE_FIELDS]))
            for row in rows:
                if row.get("play_type") in ("punt", "field_goal") or (
                        row.get("play_type") == "possession_end" and row.get("reason") == "downs"):
                    if any(row.get(k) != fd.get(k) for k in chains.STATE_FIELDS):
                        err("fourth_down_distance_mismatch", "%s %s row" % (where, row.get("play_type")))
            if fd and bool(fd.get("goal_to_go")) != (fd.get("ydstogo") == fd.get("los")):
                err("goal_to_go_mismatch", "%s fourth-down state" % where)
        chain = list(p.get("chains") or [])
        flags = sum(bool(r.get("first_down")) for r in scrim)
        if len(chain) != 6 or [chain[0]] + chain[2:6] != w["chains"] or chain[0] != flags:
            err("first_downs_ne_ledger", "%s chains %s walk %s" % (where, chain, w["chains"]))


def has_clock_legs(result):
    """True for a kernel 2014.4-or-later result or receipt (every possession
    carries its own seconds and clock-expiry leg)."""
    possessions = _possessions(result)
    return bool(possessions) and all(p.get("own_seconds") is not None and p.get("expiry_seconds") is not None
                                     for p in possessions)


def _row_remaining(row, game_type):
    """Kernel 2014.4: a ledger row's clock as seconds left on the possession
    countdown (regulation 3600..0; regular overtime 900..0; postseason
    overtime on the kernel's continuous period-bound countdown)."""
    from .rules import RULES
    minutes, seconds = (int(v) for v in row["game_clock"].split(":"))
    left = minutes * 60 + seconds
    period = row["period"]
    if isinstance(period, str) and period.startswith("OT"):
        if game_type != "postseason":
            return left
        number = int(period[2:] or 1)
        return (RULES.postseason_ot_period_bound - number) * RULES.postseason_ot_seconds + left
    return 3600 - ((int(period) - 1) * 900 + 900 - left)


def _check_clock_legs(result, possessions, rows_by_drive, err, fpm):
    """Kernel 2014.4: a drive's own seconds lie in the 2012 range for its snap
    count; its clock-expiry leg is 0..CLOCK_EXPIRY_ALLOWANCE, only on a
    window-ending drive, and own + expiry is the possession's clock; with the
    full ledger, no scrimmage snap is stamped after the drive's own end.
    `fpm` is the field-position model of the result's own base."""
    from . import field_position as fp
    game_type = result.get("game_type", "regular")
    ranges = fpm.snap_seconds_range()
    for p in possessions:
        number, own, expiry = p["number"], p["own_seconds"], p["expiry_seconds"]
        elapsed = p["start_clock"] - p["end_clock"]
        if (expiry < 0 or expiry > fp.CLOCK_EXPIRY_ALLOWANCE or own + expiry != elapsed
                or (expiry and not p.get("half_final"))):
            err("expiry_leg_exceeds_allowance", "drive %s own %s expiry %s over %s" % (number, own, expiry, elapsed))
        span = ranges.get(p.get("scrimmage_plays"))
        if span is None or not span[0] <= own <= span[1]:
            err("seconds_per_snap_outside", "drive %s: %s snaps in %s s" % (number, p.get("scrimmage_plays"), own))
        if rows_by_drive is None:
            continue
        own_end = p["end_clock"] + expiry
        for row in rows_by_drive.get(number, ()):
            if row.get("play_type") in ("pass", "run") and _row_remaining(row, game_type) < own_end:
                err("snap_after_expiry", "drive %s snap %s at %s %s" % (
                    number, row.get("snap_in_drive"), row["period"], row["game_clock"]))


def has_timeouts(result):
    """True for a kernel 2014.1-or-later result or receipt."""
    possessions = _possessions(result)
    return bool(possessions) and all(p.get("timeouts") is not None for p in possessions)


def _check_timeouts(possessions, game_type, other, err):
    """Kernel 2014.1: each club's charged timeouts stay within the allowance
    and carry exactly from possession to possession inside a half (a reset at
    each half, at overtime, and every two postseason overtime periods)."""
    from .rules import RULES
    held, segment = {}, None
    for p in possessions:
        off_before, def_before, off_used, def_used = p["timeouts"]
        if p["half"] == "OT":
            if game_type == "postseason":
                allowance = RULES.postseason_ot_timeouts_per_half
                elapsed = RULES.postseason_ot_period_bound * RULES.postseason_ot_seconds - p["start_clock"]
                key = ("OT", int(elapsed // (2 * RULES.postseason_ot_seconds)))
            else:
                allowance, key = RULES.regular_ot_timeouts, ("OT", 0)
        else:
            allowance, key = RULES.timeouts_per_half, p["half"]
        if key != segment:
            segment, held = key, {}
        team, rival = p["team"], other.get(p["team"])
        if not all(0 <= value <= allowance and 0 <= used <= value
                   for value, used in ((off_before, off_used), (def_before, def_used))):
            err("timeout_state_invalid", "drive %s timeouts %s" % (p["number"], p["timeouts"]))
        if team in held and held[team] != off_before:
            err("timeout_state_invalid", "drive %s offence count does not carry" % p["number"])
        if rival in held and held[rival] != def_before:
            err("timeout_state_invalid", "drive %s defence count does not carry" % p["number"])
        held[team], held[rival] = off_before - off_used, def_before - def_used
        fourth = p.get("fourth_down")
        if fourth and fourth.get("ydstogo") is not None and fourth.get("los") is not None \
                and fourth["ydstogo"] > fourth["los"]:
            err("fourth_down_beyond_goal", "drive %s: %s to go at %s" % (p["number"], fourth["ydstogo"], fourth["los"]))


def _score_kind(p):
    category = p["category"]
    if category == "touchdown":
        return "touchdown"
    if category == "field_goal_attempt" and p.get("fg_made"):
        return "field_goal"
    if category == "safety":
        return "safety"
    return None


def _elapsed(row):
    minutes, seconds = (int(v) for v in row["game_clock"].split(":"))
    left = minutes * 60 + seconds
    period = row["period"]
    if isinstance(period, str) and period.startswith("OT"):
        number = int(period[2:] or 1)
        return 3600 + 900 * number - left
    return (int(period) - 1) * 900 + 900 - left


def _clock_base(half):
    return 1800 if half == 1 else 0


PRO_BOWL = "pro_bowl"
PRO_BOWL_SPOT = 75
QUARTER_STARTS = (2700, 1800, 900)


def _frame(p, game_type):
    """(draw half, clock base) of a possession: the half and its base, or for
    a Pro Bowl possession its quarter window (kernel 2014.3)."""
    if game_type == PRO_BOWL and p["half"] in (1, 2):
        # A receipt's drive summary omits the quarter; no Pro Bowl possession
        # crosses one, so its start clock fixes it.
        quarter = p.get("quarter") or 4 - (int(p["start_clock"]) - 1) // 900
        return (2 if quarter == 4 else 1), (4 - quarter) * 900
    return p["half"], _clock_base(p["half"])


def _zero_play_expiry(p):
    """Kernel 2014.4: a zero-play possession whose whole window (at most the
    clock-expiry allowance) is its clock-expiry leg. It replays no 2012
    drive: its net is 0 by definition, not a sample from the start bin's
    2012 clock envelope."""
    return (p.get("scrimmage_plays") == 0 and p["category"].startswith("end_of_") and p["net_yards"] == 0
            and p.get("own_seconds") == 0 and p.get("expiry_seconds") == p["start_clock"] - p["end_clock"])


def _check_spots(result, possessions, err, fp):
    """Ledger-free kernel 2013.7 classes on the possession list or drives summary.

    `fp` is the field-position model of the result's own calibration base: its
    cell, need, zone and clock-bucket rules are the frozen rules of that
    base (the 2013.7 rules of the 2012 base for every kernel up to 2014.5),
    selected by the receipt's kernel version, never a later base's."""
    game_type = result.get("game_type", "regular")

    def key(p):
        return "clock" if p["category"].startswith("end_of_") else p["category"]

    for p in possessions:
        number, start, net, end = p["number"], p["start_spot"], p["net_yards"], p.get("end_spot")
        category = key(p)
        if not isinstance(start, int) or not 1 <= start <= 99:
            err("start_spot_out_of_field", "drive %s start %s" % (number, start))
            continue
        envelope = fp.load()["envelopes"][category][fp.start_bin(start)]
        if envelope is None and not _zero_play_expiry(p):
            err("category_impossible_at_start", "drive %s %s from %s" % (number, category, start))
        if category == "touchdown" and (net != start or end != 0):
            err("td_net_ne_start", "drive %s net %s start %s end %s" % (number, net, start, end))
        if category == "safety":
            if start - net != 100 or end != 100:
                err("safety_not_at_goal_line", "drive %s start %s net %s" % (number, start, net))
            if envelope is None:
                err("safety_start_infeasible", "drive %s safety from %s" % (number, start))
        if end != start - net or (category not in ("touchdown", "safety") and not (
                isinstance(end, int) and 1 <= end <= 99)):
            err("end_spot_identity", "drive %s start %s net %s end %s" % (number, start, net, end))
        if category == "field_goal_attempt" and (p.get("fg_distance") or 0) - (end or 0) not in (17, 18, 19):
            err("fg_distance_offset", "drive %s distance %s end %s" % (number, p.get("fg_distance"), end))
        # Transition rules published with the possession.
        nxt = p.get("next_start")
        kick = p.get("kickoff_after")
        if category == "downs" and nxt != 100 - end:
            err("spot_chain_break", "drive %s downs next %s end %s" % (number, nxt, end))
        if category == "field_goal_attempt" and not p.get("fg_made") and nxt != min(80, 110 - p["fg_distance"]):
            err("spot_chain_break", "drive %s missed FG next %s" % (number, nxt))
        if kick and (kick.get("next_start") != nxt or (
                kick.get("touchback") and nxt != 80 + (kick.get("enforcement") or 0))):
            err("spot_chain_break", "drive %s kick next %s" % (number, nxt))
        # Fourth-down decision state on punt, field-goal and downs terminals.
        if category in fp.FOURTH_DOWN_CATEGORIES:
            fd = p.get("fourth_down")
            draw_half, base = _frame(p, game_type)
            window = p["start_clock"] - base
            clock_s = p["end_clock"] - base
            expected = None
            if isinstance(fd, dict) and isinstance(p.get("score_diff"), int):
                # Kernel 2014.4: a downs drive publishes the line of scrimmage
                # of its failed fourth-down snap, short of the line to gain by
                # more than that snap gained (end = los - gain, gain < ydstogo).
                walked_downs = category == "downs" and p.get("chain_model")
                if walked_downs and not (isinstance(fd.get("los"), int) and isinstance(fd.get("ydstogo"), int)
                                         and 1 <= fd["los"] <= 99 and fd["los"] - end < fd["ydstogo"]):
                    err("fourth_down_state_missing", "drive %s downs state" % number)
                expected = {
                    "los": fd.get("los") if walked_downs else end,
                    "clock_s": clock_s, "half": draw_half, "score_diff": p["score_diff"],
                    "need": fp.need(p["score_diff"]), "decision_zone": fp.decision_zone(end),
                    "cell": fp.cell_for(draw_half, window, p["score_diff"]),
                    "clock_bucket": fp.terminal_bucket(clock_s) if draw_half == 2 else None,
                    "action": FOURTH_DOWN_ACTION[category],
                }
            if expected is None or any(fd.get(k) != v for k, v in expected.items()):
                err("fourth_down_state_missing", "drive %s" % number)
            elif draw_half == 2 and fd["cell"] != "neutral" and (
                    fd["clock_bucket"] != fd.get("tuple_terminal_bucket")
                    or fp.cell_need(fd["cell"]) != fd["need"]):
                err("late_terminal_state_mismatch", "drive %s bucket %s tuple %s" % (
                    number, fd["clock_bucket"], fd.get("tuple_terminal_bucket")))
    for a, b in zip(possessions, possessions[1:]):
        if game_type == PRO_BOWL and b["half"] in (1, 2) and b["start_clock"] in QUARTER_STARTS:
            # A new Pro Bowl quarter starts at the 25 whatever ended the last.
            if b["start_spot"] != PRO_BOWL_SPOT:
                err("spot_chain_break", "drive %s opens a quarter at %s" % (b["number"], b["start_spot"]))
            continue
        if a["half"] == b["half"] and a.get("next_start") is not None and b["start_spot"] != a["next_start"]:
            err("spot_chain_break", "drive %s start %s after next %s" % (b["number"], b["start_spot"], a["next_start"]))
        if a["half"] == b["half"] and a.get("next_start") is None:
            err("spot_chain_break", "drive %s follows drive %s without a next start" % (b["number"], a["number"]))
    for team, s in result.get("team_stats", {}).items():
        mine = [p for p in possessions if p["team"] == team]
        chains = [sum((p.get("chains") or [0] * 6)[i] for p in mine) for i in range(4)]
        if (s.get("first_downs") != chains[0] + chains[1] or s.get("third_down_attempts") != chains[2]
                or s.get("third_down_conversions") != chains[3]):
            err("chain_counter_mismatch", "%s counters differ from the drive chains" % team)


def _check_spot_ledger(result, possessions, rows_by_drive, kicks, err):
    """Kick-row and label classes (full snap ledger, kernel 2013.7 onward)."""
    by_number = {p["number"]: p for p in possessions}
    for k in kicks:
        p = by_number.get(k["drive"])
        nxt = k.get("next_start")
        if p is None or nxt != p["start_spot"]:
            err("kick_spot_mismatch", "kick before drive %s next %s" % (k["drive"], nxt))
            continue
        spot = 20 if k["play_type"] == "free_kick" else 35
        e = k.get("enforcement") or 0
        if k.get("touchback"):
            if nxt != 80 + e:
                err("kick_spot_mismatch", "touchback before drive %s" % k["drive"])
        elif nxt != spot + (k.get("kick_yards") or 0) - (k.get("return_yards") or 0) + e:
            err("kick_spot_mismatch", "kick identity before drive %s" % k["drive"])
    for index, p in enumerate(possessions):
        punts = [r for r in rows_by_drive.get(p["number"], []) if r.get("play_type") == "punt"]
        if not punts:
            continue
        row = punts[0]
        los, nxt = row.get("los"), row.get("next_start")
        if los != p.get("end_spot") or nxt != p.get("next_start"):
            err("kick_spot_mismatch", "punt on drive %s los %s next %s" % (p["number"], los, nxt))
            continue
        after = possessions[index + 1] if index + 1 < len(possessions) else None
        if after is not None and result.get("game_type") == PRO_BOWL and after["half"] in (1, 2) \
                and after["start_clock"] in QUARTER_STARTS:
            after = None  # the next Pro Bowl quarter starts at the 25
        if after is not None and after["half"] == p["half"] and after["start_spot"] != nxt:
            err("kick_spot_mismatch", "punt on drive %s next %s start %s" % (p["number"], nxt, after["start_spot"]))
        e = row.get("enforcement") or 0
        if row.get("touchback"):
            if nxt != 80 + e:
                err("kick_spot_mismatch", "punt touchback on drive %s" % p["number"])
        elif (row.get("gross") or 0) - (row.get("return_yards") or 0) + e != los - (100 - nxt):
            err("kick_spot_mismatch", "punt identity on drive %s" % p["number"])
    passers = {}
    for rows in rows_by_drive.values():
        for r in rows:
            if r.get("play_type") == "pass" and r.get("passer"):
                passers.setdefault(r["offense"], r["passer"])
    # Kernel 2014.4: the passer is chosen per drive (a backup can take over
    # after a removal), so a kneel belongs to that drive's passer.
    drive_passers = {p["number"]: p["passer"] for p in possessions if p.get("passer")}
    for number, rows in rows_by_drive.items():
        for r in rows:
            if r.get("play_type") not in ("pass", "run"):
                continue
            concept = r.get("concept")
            source = r.get("label_source")
            label_type = r.get("label_type") or LABEL_TYPES.get(concept)
            groups = r.get("label_groups")
            where = "drive %s snap %s" % (number, r.get("snap_in_drive"))
            if r.get("kneel"):
                passer = drive_passers.get(number, passers.get(r["offense"]))
                if concept != KNEEL_LABEL or (passer is not None and r.get("runner") != passer):
                    err("kneel_spike_mislabelled", where)
                continue
            if r.get("spike"):
                if concept != SPIKE_LABEL or r.get("target"):
                    err("kneel_spike_mislabelled", where)
                continue
            if concept in (KNEEL_LABEL, SPIKE_LABEL):
                err("kneel_spike_mislabelled", where)
                continue
            if r.get("scramble"):
                if label_type == "run" or not (source == "generic" or str(source).startswith("sheet")):
                    err("scramble_with_designed_label", where)
                continue
            if label_type not in (r["play_type"], "any", "mixed"):
                err("label_type_mismatch", where)
                continue
            if not str(source).startswith("sheet"):
                continue
            if r["play_type"] == "run":
                if not isinstance(groups, list) or r.get("carrier_group") not in groups:
                    err("label_carrier_mismatch", where)
            elif r.get("target") and groups != "any" and (
                    not isinstance(groups, list) or r.get("target_group") not in groups):
                err("label_target_mismatch", where)


def check_ledger(result, base=None):
    """Coherence errors for one closed game, as 'class: detail' strings.

    Runs the ledger-free checks on the possession list (or a receipt's compact
    'drives' summary) and, when a full snap ledger is present, the snap-level
    checks as well. Receipts without start spots (kernels before 2013.7) get
    exactly their 2013.6 checks. An empty list means no violation was found.

    Kernel 2014.6 plumbing (batch B1): every audit uses the calibration base
    and cell rules of the result's own kernel_version
    (runtime.calibration_base.base_for_result; an unknown version raises).
    `base` overrides that only for synthetic tests of a test base."""
    from .rules import ot_status
    from .calibration_base import base_for_result

    base = base if base is not None else base_for_result(result)
    errors = []

    def err(cls, detail):
        errors.append("%s: %s" % (cls, detail))

    possessions = _possessions(result)
    if not possessions:
        return errors
    spots = has_spots(result)
    game_type = result.get("game_type", "regular")
    teams = list(result.get("final_score", {}))
    other = {t: next((u for u in teams if u != t), None) for t in teams}
    regulation = [p for p in possessions if p["half"] in (1, 2)]
    overtime = [p for p in possessions if p["half"] == "OT"]
    last = possessions[-1]
    if spots and has_timeouts(result):
        _check_timeouts(possessions, game_type, other, err)

    for p in regulation:
        if p["start_clock"] > 1800 > p["end_clock"]:
            err("drives_spanning_half", "drive %s" % p["number"])
    first_h2 = next((p for p in regulation if p["half"] == 2), None)
    pro_bowl = game_type == PRO_BOWL
    if pro_bowl:
        # Kernel 2014.3 Pro Bowl: possession alternates at the start of each
        # quarter, every quarter opens at the 25 and no possession crosses one.
        openers = [next((p for p in regulation if p["start_clock"] == top), None) for top in (3600,) + QUARTER_STARTS]
        teams_open = [p["team"] if p else None for p in openers]
        if None in teams_open or not (teams_open[0] == teams_open[2] != teams_open[1] == teams_open[3]):
            err("wrong_second_half_receiver", "Pro Bowl quarter possession does not alternate")
        for p in openers:
            if p is not None and p["start_spot"] != PRO_BOWL_SPOT:
                err("spot_chain_break", "drive %s opens a quarter at %s" % (p["number"], p["start_spot"]))
        for p in regulation:
            if any(p["start_clock"] > b > p["end_clock"] for b in (2700, 900)):
                err("drives_spanning_half", "drive %s spans a quarter" % p["number"])
    elif regulation and (first_h2 is None or first_h2["team"] == regulation[0]["team"]):
        err("wrong_second_half_receiver", "second half opened by the opening receiver")
    for half, top, bottom in ((1, 3600, 1800), (2, 1800, 0)):
        rows = [p for p in regulation if p["half"] == half]
        clock = top
        for p in rows:
            if p["start_clock"] != clock or p["end_clock"] > p["start_clock"] or (
                    p["end_clock"] == p["start_clock"]):
                err("clock_regression", "drive %s possession clock" % p["number"])
            clock = p["end_clock"]
        if rows and clock != bottom:
            err("clock_regression", "half %s does not end at %d" % (half, bottom))
    for a, b in zip(possessions, possessions[1:]):
        if pro_bowl and b["half"] in (1, 2) and b["start_clock"] in QUARTER_STARTS:
            continue  # a Pro Bowl quarter's opener is set by the alternation
        if a["half"] == b["half"] and a["team"] == b["team"]:
            err("clock_regression", "drive %s repeats the offense" % b["number"])

    fpm = base.field_position() if spots else None
    for p in possessions:
        category = p["category"]
        range_key = "clock" if category.startswith("end_of_") else category
        if _zero_play_expiry(p):
            pass  # kernel 2014.4: no 2012 drive is replayed, so no 2012 net range applies
        elif spots:
            envelope = fpm.load()["envelopes"][range_key][fpm.start_bin(p["start_spot"])] if (
                isinstance(p["start_spot"], int) and 1 <= p["start_spot"] <= 99) else None
            if envelope is None or (range_key != "touchdown" and not envelope[0] <= p["net_yards"] <= envelope[1]):
                err("drive_net_outside_2012_range", "drive %s net %s" % (p["number"], p["net_yards"]))
        else:
            low, high = base.drive_model().net_range(range_key)
            if not low <= p["net_yards"] <= high:
                err("drive_net_outside_2012_range", "drive %s net %s" % (p["number"], p["net_yards"]))
        if p.get("kickoff_after"):
            expired = p["end_clock"] in ((1800, 0) if p["half"] in (1, 2) else (0,))
            if expired or p is last:
                err("kickoff_after_expired_clock", "drive %s" % p["number"])
        if p.get("half_final"):
            boundary = 1800 if p["half"] == 1 else 0
            nxt = possessions[possessions.index(p) + 1] if p is not last else None
            if pro_bowl and p["half"] in (1, 2):
                boundary = _frame(p, game_type)[1]
                nxt = None
            if p["end_clock"] != boundary or (nxt is not None and nxt["half"] == p["half"]
                                              and p["half"] in (1, 2)):
                err("clock_regression", "half-final drive %s does not end its window" % p["number"])
            if p.get("kickoff_after"):
                err("kickoff_after_expired_clock", "kick after half-final drive %s" % p["number"])
        if p["half"] == "OT" and category == "touchdown" and p.get("xp_made") is not None:
            err("xp_after_ot_walkoff", "drive %s" % p["number"])

    points = {t: 0 for t in teams}
    for p in possessions:
        kind = _score_kind(p)
        if kind == "touchdown":
            points[p["team"]] += 6 + (1 if p.get("xp_made") else 0)
        elif kind == "field_goal":
            points[p["team"]] += 3
        elif kind == "safety" and other.get(p["team"]):
            points[other[p["team"]]] += 2
    if teams and points != dict(result["final_score"]):
        err("score_identity_violations", "drive points %s vs final %s" % (points, result["final_score"]))
    for team, s in result.get("team_stats", {}).items():
        if "extra_points_made" in s:
            identity = 6 * s["touchdowns"] + s["extra_points_made"] + 3 * s["field_goals"] + 2 * s["safeties"]
            if identity != result["final_score"].get(team):
                err("score_identity_violations", "%s team counters" % team)

    regulation_points = {t: 0 for t in teams}
    for p in regulation:
        kind = _score_kind(p)
        if kind == "touchdown":
            regulation_points[p["team"]] += 6 + (1 if p.get("xp_made") else 0)
        elif kind == "field_goal":
            regulation_points[p["team"]] += 3
        elif kind == "safety" and other.get(p["team"]):
            regulation_points[other[p["team"]]] += 2
    tied = len(set(regulation_points.values())) == 1
    if overtime and not tied:
        err("ot_end_inconsistent", "overtime played after a decided regulation")
    if tied and teams and not overtime:
        err("ot_end_inconsistent", "tied regulation without overtime")
    history = []
    for index, p in enumerate(overtime):
        history.append({"team": p["team"], "score": _score_kind(p)})
        status = ot_status(history, game_type)
        final = index == len(overtime) - 1
        if status == "end" and not final:
            err("ot_end_inconsistent", "play continued after drive %s ended overtime" % p["number"])
        if final and status != "end" and not (
                p["end_clock"] == 0 and ot_status(history, game_type, expired=True) == "end"):
            err("ot_end_inconsistent", "overtime stopped before it ended at drive %s" % p["number"])

    if spots:
        _check_spots(result, possessions, err, fpm)

    ledger = result.get("play_ledger")
    clock_legs = has_clock_legs(result)
    if not ledger:
        if clock_legs:
            _check_clock_legs(result, possessions, None, err, base.field_position())
        return errors

    previous = None
    for row in ledger:
        period = row["period"]
        order = 4 + int(period[2:] or 1) if isinstance(period, str) else int(period)
        stamp = (order, _elapsed(row))
        if previous and (stamp[0] < previous[0] or stamp[1] < previous[1]):
            err("clock_regression", "sequence %s" % row.get("sequence"))
        previous = stamp

    kicks = [row for row in ledger if row.get("play_type") in KICK_TYPES]
    by_number = {p["number"]: p for p in possessions}
    if pro_bowl:
        if kicks:
            err("kickoff_after_expired_clock", "a kick row in a game without kickoffs")
    elif not ledger or ledger[0].get("play_type") != "kickoff" or (
            ledger[0]["period"], ledger[0]["game_clock"]) != (1, "15:00"):
        err("missing_half_kickoff", "no opening kickoff at Q1 15:00")
    openers = {regulation[0]["number"]} if regulation and not pro_bowl else set()
    if first_h2 and not pro_bowl:
        openers.add(first_h2["number"])
        second = [k for k in kicks if k["drive"] == first_h2["number"]
                  and (k["period"], k["game_clock"]) == (3, "15:00")]
        if not second or second[0]["defense"] != first_h2["team"]:
            err("missing_half_kickoff", "no second-half kickoff at Q3 15:00 to %s" % first_h2["team"])
    if overtime and not pro_bowl:
        openers.add(overtime[0]["number"])
    kicked_drives = set()
    for k in kicks:
        drive = k["drive"]
        if drive in kicked_drives:
            err("kickoff_after_expired_clock", "second kick before drive %s" % drive)
        kicked_drives.add(drive)
        if drive in openers:
            continue
        before = by_number.get(drive - 1)
        if drive not in by_number or before is None or not before.get("kickoff_after"):
            err("kickoff_after_expired_clock", "kick row before drive %s" % drive)
    for number in openers:
        if number not in kicked_drives:
            err("missing_half_kickoff", "drive %s has no opening kick" % number)

    rows_by_drive = {}
    for row in ledger:
        if row.get("play_type") in KICK_TYPES:
            continue
        rows_by_drive.setdefault(row["drive"], []).append(row)
    for number in rows_by_drive:
        if number not in by_number:
            err("snaps_after_terminal", "rows for unknown drive %s" % number)
    for p in possessions:
        rows = rows_by_drive.get(p["number"], [])
        category = p["category"]
        markers = []
        for index, row in enumerate(rows):
            kind = row.get("play_type")
            if kind in ("pass", "run"):
                if row.get("touchdown"):
                    markers.append((index, "touchdown"))
                if row.get("turnover"):
                    markers.append((index, row.get("turnover_type")))
            elif kind in ("field_goal", "punt", "safety", "possession_end"):
                markers.append((index, kind))
        if not markers:
            err("drives_missing_terminal", "drive %s" % p["number"])
            continue
        if len(markers) > 1:
            err("duplicate_terminal", "drive %s" % p["number"])
        index, marker = markers[0]
        if marker != MARKER_FOR.get(category):
            err("drives_missing_terminal", "drive %s marker %s for %s" % (p["number"], marker, category))
        if marker == "possession_end" and rows[index].get("reason") != category:
            err("drives_missing_terminal", "drive %s reason mismatch" % p["number"])
        if any(r.get("play_type") in ("pass", "run") for r in rows[index + 1:]):
            err("snaps_after_terminal", "drive %s" % p["number"])
        tries = [r for r in rows if r.get("play_type") == "extra_point"]
        if category == "touchdown":
            if p.get("xp_made") is None and tries:
                err("xp_after_ot_walkoff" if p["half"] == "OT" else "duplicate_terminal",
                    "drive %s try without an attempt" % p["number"])
            if p.get("xp_made") is not None and (len(tries) != 1 or tries[0].get("made") != p["xp_made"]):
                err("score_identity_violations", "drive %s try row" % p["number"])
        elif tries:
            err("duplicate_terminal", "drive %s try without a touchdown" % p["number"])
        if category == "field_goal_attempt":
            kicks_fg = [r for r in rows if r.get("play_type") == "field_goal"]
            if kicks_fg and bool(kicks_fg[0].get("made")) != bool(p.get("fg_made")):
                err("score_identity_violations", "drive %s field-goal row" % p["number"])
        scrimmage = [r for r in rows if r.get("play_type") in ("pass", "run")]
        yards = [r.get("result_yards", 0) for r in scrimmage]
        if sum(yards) != p["net_yards"]:
            err("snap_sum_ne_drive_net", "drive %s: %s vs %s" % (p["number"], sum(yards), p["net_yards"]))
        if category == "touchdown":
            final = scrimmage[-1] if scrimmage else None
            if final is None or final.get("sack") or not final.get("touchdown") or final.get("result_yards", 0) <= 0:
                err("td_snap_sack_or_nonpositive", "drive %s" % p["number"])
        if spots:
            start = p["start_spot"]
            running = 0
            for position, value in enumerate(yards):
                running += value
                spot = start - running
                is_last = position == len(yards) - 1
                if is_last and category == "touchdown":
                    if spot != 0:
                        err("prefix_out_of_bounds", "drive %s touchdown ends at %s" % (p["number"], spot))
                elif is_last and category == "safety":
                    if spot != 100:
                        err("prefix_out_of_bounds", "drive %s safety ends at %s" % (p["number"], spot))
                        err("safety_not_at_goal_line", "drive %s terminal snap ends at %s" % (p["number"], spot))
                elif not 1 <= spot <= 99:
                    err("prefix_out_of_bounds", "drive %s snap %s spot %s" % (p["number"], position + 1, spot))
                    break
            continue
        running = 0
        for position, value in enumerate(yards):
            running += value
            if abs(value) > 99 or not -99 <= running <= 99:
                err("prefix_out_of_bounds", "drive %s snap %s" % (p["number"], position + 1))
                break
            if category == "touchdown" and position < len(yards) - 1 and running >= p["net_yards"]:
                err("prefix_out_of_bounds", "drive %s reached the end zone before the touchdown" % p["number"])
                break
    if spots:
        _check_spot_ledger(result, possessions, rows_by_drive, kicks, err)
    if has_chain_ledger(result):
        _check_chain_ledger(possessions, rows_by_drive, err)
    if has_chain_model(result):
        _check_layout_resamples(possessions, err, base.field_position())
    if clock_legs:
        _check_clock_legs(result, possessions, rows_by_drive, err, base.field_position())
    return errors


def _check_layout_resamples(possessions, err, fp):
    """Kernel 2014.4 phase 2: a published layout resample names its pool, the
    original tuple's index and leading fields, and a final tuple of the same
    category at that index in the same pool, feasible at the drive's start
    spot; the resample count is a positive integer. `fp` is the
    field-position model of the result's own base."""
    for p in possessions:
        rec = p.get("layout_resample")
        if not rec:
            continue
        where = "drive %s" % p["number"]
        category = "clock" if str(p["category"]).startswith("end_of_") else p["category"]
        try:
            pool_id = tuple(rec["pool"])
            count = rec["resamples"]
            original, final = rec["original"], rec["final"]
            if not isinstance(count, int) or count < 1:
                raise ValueError("resample count")
            if not fp._counts(pool_id):
                raise ValueError("unknown pool")
            tuples = {}
            for label, item in (("original", original), ("final", final)):
                t = fp.locate_tuple(category, item["locator"])
                if t is None or list(t[:5]) != list(item["tuple"]):
                    raise ValueError("%s tuple does not match the artifact" % label)
                tuples[label] = t
            if original["locator"] == final["locator"]:
                raise ValueError("final tuple is the original")
            final_tuple = tuples["final"]
            if p.get("start_spot") is not None and not fp.static_feasible(category, final_tuple, p["start_spot"]):
                raise ValueError("final tuple infeasible at the start spot")
            if int(final_tuple[fp.T["plays"]]) != int(p.get("scrimmage_plays", final_tuple[fp.T["plays"]])):
                raise ValueError("published plays differ from the final tuple")
        except (KeyError, TypeError, ValueError, IndexError) as exc:
            err("layout_resample_incoherent", "%s: %s" % (where, exc))


def coherence_counts(errors):
    counts = {cls: 0 for cls in COHERENCE_CLASSES}
    for error in errors:
        cls = error.split(":", 1)[0]
        counts[cls] = counts.get(cls, 0) + 1
    return counts
