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

from . import ball_security
from . import call_families
from . import call_situations
from . import chains as chain_walk
from . import participation
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
# Kernel 2014.6 batch B6 (W5a): the clock-detail stream seats a drive's
# charged timeouts (its only draw); the snap stamps themselves are an
# allocation of the drive's own seconds by the base's gap table. Display and
# records only: no outcome draw reads this stream or the stamps.
CLOCK_DETAIL_TAG = "public-clock-detail-v1"
TIMEOUT_ROW = "timeout"
TWO_MINUTE_WARNING_ROW = "two_minute_warning"
LEAGUE_MODEL = "league_model"
# Gap kinds whose out-of-bounds split the kernel cannot see are pooled.
GAP_POOL = {"run": ("run", "run_oob"), "complete": ("complete", "complete_oob")}
SACK_GAP_FROM_KERNEL = (2014, 6)
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


def _clock_rng(seed, *, event_id, drive_no, offense):
    return _stream(CLOCK_DETAIL_TAG, seed, event_id, drive_no, offense)


# ---- W5a clock detail (kernel 2014.6, batch B6) ------------------------------

def gap_kind(kind, completed):
    """The W5a gap kind of a laid-out snap: run, complete, incomplete (an
    interception stops the clock like an incompletion), sack, spike, kneel."""
    if kind == "run":
        return "run"
    if kind == "sack":
        return "sack"
    if kind == "spike":
        return "spike"
    if kind == "kneel":
        return "kneel"
    if kind in ("att", "catch") and completed:
        return "complete"
    return "incomplete"


def clock_context(remaining, overtime=False, pro_bowl=False):
    """The W5a clock context of a snap at `remaining` seconds of the
    possession countdown: inside_2_min (the last 2:00 of a half, of an
    overtime period, or of any Pro Bowl quarter), q4_2_to_5_min (the fourth
    quarter from 5:00 to 2:00), else normal."""
    period, text = _period_clock(remaining, overtime=overtime)
    minutes, seconds = (int(v) for v in text.split(":"))
    left = minutes * 60 + seconds
    if isinstance(period, str):
        return "inside_2_min" if left <= 120 else "normal"
    if left <= 120 and (pro_bowl or period in (2, 4)):
        return "inside_2_min"
    if period == 4 and left <= 300:
        return "q4_2_to_5_min"
    return "normal"


def _table_mean(table, keys, context):
    """Mean seconds of a W5a cell (sum / snaps), pooling the given keys; a
    context with no snaps falls back to the keys' pooled mean over every
    context; None when the table has none."""
    for contexts in ((context,), None):
        total = snaps = 0
        for cell, (sum_s, n) in table.items():
            kind, ctx = cell.split("|", 1)
            if kind in keys and (contexts is None or ctx in contexts):
                total += sum_s
                snaps += n
        if snaps:
            return total / snaps
    return None


def gap_seconds(constants, kind, context, sack_key):
    """Mean W5a gap after a snap of `kind` in `context` (pooled over the
    out-of-bounds split the kernel cannot see; the sack gap by `sack_key`,
    the 2014 running-clock value for kernel 2014.6 and later)."""
    table = constants["gap_seconds"]
    keys = (sack_key,) if kind == "sack" else GAP_POOL.get(kind, (kind,))
    mean = _table_mean(table, keys, context)
    if mean is None and kind == "sack":
        mean = _table_mean(table, ("sack_2010_2013", "sack_2014w4"), context)
    return mean if mean is not None else 1.0


def _allocate_gaps(weights, available, diagnostics):
    """Integer gaps proportional to `weights` summing to `available`, each at
    least 1 s when `available` allows (the exemption, when the drive's own
    seconds are fewer than its gaps, is counted clock_gap_exempt)."""
    n = len(weights)
    if n == 0:
        return []
    available = max(0, int(available))
    total = sum(weights)
    exact = [available * w / total if total > 0 else available / n for w in weights]
    gaps = [int(x) for x in exact]
    residue = available - sum(gaps)
    order = sorted(range(n), key=lambda i: (-(exact[i] - gaps[i]), i))
    for i in order[:residue]:
        gaps[i] += 1
    if available >= n:
        while any(g < 1 for g in gaps):
            short = next(i for i, g in enumerate(gaps) if g < 1)
            big = max(range(n), key=lambda i: (gaps[i], -i))
            gaps[big] -= 1
            gaps[short] += 1
    elif diagnostics is not None:
        diagnostics["clock_gap_exempt"] = diagnostics.get("clock_gap_exempt", 0) + 1
    return gaps


def clock_stamps(constants, kinds, completed, *, start_clock, own, kick_length=0, sack_key="sack_2010_2013",
                 overtime=False, pro_bowl=False, diagnostics=None):
    """W5a: (snap stamps, kick stamp) as seconds of the possession countdown.

    The first snap is stamped at the drive's start; each later snap follows
    the previous one by that snap's gap (the base's mean seconds between
    consecutive snaps by the previous play's kind and clock context), the
    gaps scaled to the drive's own seconds less the kick length. A kick is
    stamped at start - own + kick length (a zero-play kick at its start). The
    context is read from the stamps themselves (two passes). An allocation
    of the real drive's own seconds, never a play-by-play clock simulation.
    """
    plays = len(kinds)
    start, own = int(start_clock), max(0, int(own))
    kick = None
    kick_len = 0
    if kick_length:
        # The kick length is clipped so every snap keeps its 1 s gap when the
        # drive's own seconds allow (a 1-snap, 11 s field-goal drive kicks 10 s
        # after its snap, not on the snap's clock).
        kick_len = min(int(kick_length), own)
        if plays and own - kick_len < plays:
            kick_len = max(0, own - plays)
        kick = start - own + kick_len
    if plays == 0:
        return [], (start if kick is not None else None)
    available = own - kick_len
    gap_kinds = [gap_kind(k, c) for k, c in zip(kinds, completed)]
    stamps = [start] * plays
    for _ in range(2):
        weights = [gap_seconds(constants, gap_kinds[i], clock_context(stamps[i], overtime, pro_bowl), sack_key)
                   for i in range(plays)]
        gaps = _allocate_gaps(weights, available, None)
        stamps = [start]
        for g in gaps[:-1]:
            stamps.append(stamps[-1] - g)
    _allocate_gaps(weights, available, diagnostics)
    return stamps, kick


def timeout_seats(rng, constants, kinds, completed, terminal, has_kick, count, diagnostics=None):
    """W5a: the seat (index of the snap it follows; -1 before the first snap)
    of each of `count` charged timeouts, drawn on the clock-detail stream
    with the base's seat weights by the preceding snap's kind. A timeout sits
    after a snap that left the clock running and never after a terminal
    snap or the last snap of a drive with no kick; without such a snap it
    sits before the first (counted timeout_seat_fallback)."""
    seats = constants["timeout_seats"]
    plays = len(kinds)
    last = plays - 1
    eligible, weights = [], []
    for i in range(plays):
        gk = gap_kind(kinds[i], completed[i])
        if gk not in ("run", "complete", "sack"):
            continue
        if terminal is not None and i == last:
            continue
        if i == last and not has_kick:
            continue
        weight = sum(seats.get(k, 0) for k in GAP_POOL.get(gk, (gk,)))
        if weight <= 0:
            continue
        eligible.append(i)
        weights.append(int(weight))
    out = []
    for _ in range(count):
        if not eligible:
            out.append(-1)
            if diagnostics is not None:
                diagnostics["timeout_seat_fallback"] = diagnostics.get("timeout_seat_fallback", 0) + 1
            continue
        total = sum(weights)
        pick = rng.randrange(total)
        running = 0
        for i, w in zip(eligible, weights):
            running += w
            if pick < running:
                out.append(i)
                break
    return out


def two_minute_marks(overtime=False, pro_bowl=False):
    """The possession-countdown seconds at which a two-minute warning falls:
    2:00 of periods 2 and 4 (every quarter in the Pro Bowl), of the overtime
    period, and of each postseason overtime period on its countdown."""
    if isinstance(overtime, tuple):
        _, periods, length = overtime
        return [(periods - n) * length + 120 for n in range(1, periods + 1)]
    if overtime:
        return [120]
    return [2820, 1920, 1020, 120] if pro_bowl else [1920, 120]


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


FOURTH_DOWN_CALL = "fourth-down-call"


def _call_only(call, field, available, base=None):
    """Kernel 2014.6 batch B9F: the pick filter of a named call's declared
    carrier or target groups (with `base`, both must hold), or None when the
    call declares none or no available player of those groups qualifies."""
    if call is None:
        return None
    groups = call.get(field)
    if not isinstance(groups, tuple) or not groups:
        return None
    keep = (lambda p: usage.group(p.position) in groups and (base is None or base(p)))
    return keep if any(keep(p) for p in available) else None


def _call_fits(call, record, runner_group, target_group, runner_rank, target_rank):
    """Whether a named call can describe the resolved snap (the label rules
    of _choose_label: a run call a run by a carrier it declares, a pass call
    a dropback; a sack fits any pass call)."""
    kind = call.get("type")
    if record["play_type"] == "run":
        return kind in ("run", "any", "mixed") and isinstance(call["carrier"], tuple) and \
            runner_group in call["carrier"] and _personnel_fits(call, runner_group, runner_rank)
    if kind not in ("pass", "any", "mixed"):
        return False
    if record.get("sack"):
        return True
    return (call["target"] == call_families.ANY or (isinstance(call["target"], tuple)
                                                     and target_group in call["target"])) \
        and _personnel_fits(call, target_group, target_rank)


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


# ---- Kernel 2014.6 batch B10: ball security (W4; R12 layer A) -------------------------------

FUMBLE_COUNTERS = ("muffs", "fumbles_recovered_own")
BALL_SECURITY_TEAM_FIELDS = ("fumbles", "fumbles_lost", "muffs", "kicking_team_recoveries")


def _unique_players(players):
    seen, out = set(), []
    for p in players:
        if p is not None and p.player_id not in seen:
            seen.add(p.player_id)
            out.append(p)
    return out


def _team_bump(team_line, field):
    if field in team_line:
        team_line[field] += 1


def _group_pick(rng, players, group, exclude=()):
    """(player, attribution): evenly from the on-field players of the
    record's position group (group_draw), else evenly from every on-field
    player of the side (group_fallback); None when nobody is left."""
    blocked = {getattr(p, "player_id", p) for p in exclude if p is not None}
    pool = [p for p in players if p.player_id not in blocked]
    members = [p for p in pool if usage.group(p.position) == group] if group else []
    if members:
        return ball_security.even(rng, members), ball_security.GROUP_DRAW
    if pool:
        return ball_security.even(rng, pool), ball_security.GROUP_FALLBACK
    return None, None


def _move_tackle(row, forcer, defense_stats, diagnostics):
    """A forced fumble's tackle is the forcer's (the existing convention): on a
    run or completion the snap's tackle credit moves to him as a solo tackle
    (the assist, if any, is withdrawn); counted forced_fumble_tackle_moved."""
    if row.get("play_type") == "run" and not row.get("kneel"):
        negative = row.get("result_yards", 0) < 0
    elif row.get("play_type") == "pass" and row.get("completion"):
        negative = False
    else:
        return
    if row.get("tackler") == forcer.player_id and not row.get("assist_tackler"):
        return
    assisted = row.get("assist_tackler") is not None
    for pid in (row.get("tackler"), row.get("assist_tackler")):
        if pid is None or pid not in defense_stats["players"]:
            continue
        line = defense_stats["players"][pid]
        line["tackles"] -= 1
        line["assisted_tackles" if assisted else "solo_tackles"] -= 1
        if negative:
            line["tackles_for_loss"] -= 1
    line = defense_stats["players"][forcer.player_id]
    _bump(line, "tackles")
    _bump(line, "solo_tackles")
    if negative:
        _bump(line, "tackles_for_loss")
    row["tackler"] = forcer.player_id
    row["assist_tackler"] = None
    diagnostics["forced_fumble_tackle_moved"] = diagnostics.get("forced_fumble_tackle_moved", 0) + 1


def _credit_scrimmage_fumbles(ledger, plays, kinds, completed, terminal, category, plan, lost, rng, qb, front,
                              available, defenders, offense_stats, defense_stats, offense_id, defense_id,
                              diagnostics):
    """Batch B10 (R12 layer A): name and credit every fumble of one drive's
    scrimmage snaps (apply_drive_detail docstring); credit only."""
    model = plan["model"]
    lineup = participation.slot_lineup(available, defenders, qb, front)
    offense = _unique_players(s["player"] for s in lineup["offense"])
    defense = _unique_players(s["player"] for s in lineup["defense"])
    by_id = {p.player_id: p for p in tuple(available) + tuple(offense)}
    def_by_id = {p.player_id: p for p in tuple(defenders) + tuple(defense)}
    last = plays - 1
    terminal_index = last if terminal is not None and plays else None

    def name(row, entry, kind_of_snap):
        kind = entry["kind"]
        if kind == "aborted" and kind_of_snap != "sack":
            # A kept aborted snap: the quarterback's or the centre's at the
            # sourced share (the seated snap's own carrier record is unchanged).
            centre = front.get("C") if front else None
            u = rng.random()
            pick = centre if (centre is not None and u < model.p_centre_aborted) else qb
            return pick, ball_security.SOURCED_SHARE
        if kind_of_snap == "sack" or row.get("sack"):
            return by_id.get(row.get("passer")) or qb, ball_security.CARRIER
        pid = row.get("runner") if row.get("play_type") == "run" else row.get("target")
        return (by_id.get(pid) or qb), ball_security.CARRIER

    def credit(row, entry, fumbler, fumbler_basis, outcome):
        forced = bool(entry.get("forced"))
        forcer = forcer_basis = None
        if forced:
            if row.get("sack") and row.get("tackler") in def_by_id:
                forcer, forcer_basis = def_by_id[row["tackler"]], ball_security.RUSHER
            else:
                forcer, forcer_basis = _group_pick(rng, defense, entry.get("forcer_group"))
            if forcer is None:
                forced = False
        recoverer = recoverer_basis = None
        recovering = None
        if outcome == "lost":
            recovering = defense_id
            if entry.get("recoverer_is_forcer") and forcer is not None:
                recoverer, recoverer_basis = forcer, ball_security.FORCER
            else:
                recoverer, recoverer_basis = _group_pick(rng, defense, entry.get("recoverer_group"), exclude=(forcer,))
        elif outcome == "kept":
            recovering = offense_id
            if entry.get("recoverer_is_fumbler"):
                recoverer, recoverer_basis = fumbler, ball_security.FUMBLER
            else:
                recoverer, recoverer_basis = _group_pick(rng, offense, entry.get("recoverer_group"),
                                                         exclude=(fumbler,))
        line = offense_stats["players"][fumbler.player_id]
        _bump(line, "fumbles")
        _team_bump(offense_stats, "fumbles")
        if outcome == "lost":
            _bump(line, "fumbles_lost")
            _team_bump(offense_stats, "fumbles_lost")
        if forced:
            _bump(defense_stats["players"][forcer.player_id], "forced_fumbles")
            if row.get("sack"):
                pass  # the rusher already holds the sack's tackle
            elif outcome == "lost":
                # The lost fumble's terminal snap drew no tackle: the forcer's.
                fline = defense_stats["players"][forcer.player_id]
                _bump(fline, "tackles")
                _bump(fline, "solo_tackles")
                row["tackler"] = forcer.player_id
            else:
                _move_tackle(row, forcer, defense_stats, diagnostics)
        elif outcome == "lost" and not row.get("sack"):
            row["tackler"] = None
        if recoverer is not None:
            if outcome == "lost":
                _bump(defense_stats["players"][recoverer.player_id], "fumble_recoveries")
            else:
                rline = offense_stats["players"][recoverer.player_id]
                rline["fumbles_recovered_own"] = rline.get("fumbles_recovered_own", 0) + 1
        attribution = {"fumbled_by": fumbler_basis}
        if forced:
            attribution["forced_by"] = forcer_basis
        if recoverer is not None:
            attribution["recovered_by"] = recoverer_basis
        row["fumble"] = {"kind": entry["kind"], "outcome": outcome, "fumbled_by": fumbler.player_id,
                         "forced": forced, "forced_by": forcer.player_id if forced else None,
                         "recovered_by": recoverer.player_id if recoverer is not None else None,
                         "recovering_team": recovering, "attribution": attribution}
        if entry.get("synthetic"):
            row["fumble"]["entry"] = "synthetic"

    # A lost entry the drive does not end on (a fumble lost and won back by
    # the offence before the drive ended otherwise, or one cut at a
    # fourth-down decision) is not modelled: counted.
    lost_seen = sum(1 for source in plan["sources"] for e in ball_security.entries(source[2])
                    if e["outcome"] == "lost")
    terminal_entry = plan.get("terminal")
    used = int(category == "fumble_lost" and isinstance(terminal_entry, dict) and "kind" in terminal_entry)
    if lost_seen > used:
        diagnostics["lost_fumble_entry_unused"] = diagnostics.get("lost_fumble_entry_unused", 0) + lost_seen - used
    for entry, index in ball_security.seat_kept(plan["sources"], kinds, completed, terminal_index, diagnostics):
        row = ledger[index]
        fumbler, basis = name(row, entry, kinds[index])
        credit(row, entry, fumbler, basis, entry["outcome"])
    if category == "fumble_lost" and plays:
        row = ledger[last]
        entry = lost
        if entry is None:
            # No lost entry describes the snap: one is drawn from the sourced
            # shares of the laid-out kind (counted).
            kind = {"run": "run", "catch": "reception", "sack": "sack"}.get(kinds[last], "run")
            entry = model.synthetic_entry(kind, rng)
            diagnostics["lost_fumble_entry_synthesized"] = diagnostics.get("lost_fumble_entry_synthesized", 0) + 1
        if entry["kind"] == "aborted" and kinds[last] == "run" and plan.get("terminal_kind"):
            # Layer B: the terminal run's carrier is the quarterback or the
            # centre drawn at the sourced share (apply_drive_detail).
            fumbler, basis = by_id.get(row.get("runner")) or qb, ball_security.SOURCED_SHARE
        elif kinds[last] == "sack":
            fumbler, basis = by_id.get(row.get("passer")) or qb, ball_security.CARRIER
        else:
            pid = row.get("runner") if row.get("play_type") == "run" else row.get("target")
            fumbler, basis = by_id.get(pid) or qb, ball_security.CARRIER
        credit(row, entry, fumbler, basis, "lost")


def credit_kick_fumble(row, fumble, *, retained, kicking, receiving, units, stats, rng, model, diagnostics=None):
    """Batch B10 (W4, R12 layers A and C): name and credit a kick play's muff
    or return fumble from the record's fumble [kind muff|fumble, outcome,
    muffer role] on the kick's ball-security stream; every name from the
    play's own units (runtime.participation.kick), so exposure is unchanged.

    The muffer or fumbler is the club's returner for a recorded returner role
    (the row's returner, else the first of the return unit: the deterministic
    depth rule, no choose()), a group draw from the return unit for "other",
    and the returner by convention when the feed recorded none. A muff counts
    as a fumble only when the feed recorded its muffer (its fumble flag; a
    kickoff muff the receiving club never possessed is a muff only) or when
    the kicking club recovered it. Forced at the kind's sourced share, by the
    play's coverage tackler or else a coverage player drawn evenly; a kept
    ball recovered by the fumbler at the sourced share, else by a return-unit
    player drawn evenly; a retained ball (the kicking club's recovery) by the
    forcer at the sourced share, else by a coverage player drawn evenly.
    Returns the compact record the kick or punt summary carries."""
    diagnostics = diagnostics if diagnostics is not None else {}
    if fumble:
        kind_raw, outcome, role = fumble[0], fumble[1], fumble[2]
    else:
        # A kicking-club recovery with no fumble in the feed: the receiving
        # club lost the ball untouched by a recorded muffer (convention).
        kind_raw, outcome, role = "muff", "lost", None
        diagnostics["retained_kick_without_fumble"] = diagnostics.get("retained_kick_without_fumble", 0) + 1
    if retained:
        outcome = "lost"
    kind = "muff" if kind_raw == "muff" else "return"
    rec_unit = list(units.get(receiving) or ())
    kick_unit = list(units.get(kicking) or ())
    specialists = {row.get("kicker"), row.get("punter"), row.get("long_snapper")} - {None}
    coverage = [pid for pid in kick_unit if pid not in specialists] or kick_unit
    returner = row.get("returner") or (rec_unit[0] if rec_unit else None)
    if role == "other":
        others = [pid for pid in rec_unit if pid != returner]
        fumbler, fumbler_basis = (ball_security.even(rng, others), ball_security.GROUP_DRAW) if others else (
            returner, ball_security.GROUP_FALLBACK)
    elif role == "returner":
        fumbler, fumbler_basis = returner, ball_security.RETURNER
    else:
        fumbler, fumbler_basis = returner, ball_security.CONVENTION
    u_forced, u_recover = rng.random(), rng.random()
    forced = u_forced < model.p_kick(kind, "forced") and bool(coverage)
    forcer = forcer_basis = None
    if forced:
        if row.get("cover_player") in coverage:
            forcer, forcer_basis = row["cover_player"], ball_security.COVERAGE
        else:
            forcer, forcer_basis = ball_security.even(rng, coverage), ball_security.GROUP_DRAW
    recoverer = recoverer_basis = None
    recovering = None
    if outcome == "kept":
        recovering = receiving
        if u_recover < model.p_kick(kind, "kept_self") or len(rec_unit) < 2:
            recoverer, recoverer_basis = fumbler, ball_security.FUMBLER
        else:
            pool = [pid for pid in rec_unit if pid != fumbler]
            recoverer, recoverer_basis = ball_security.even(rng, pool), ball_security.GROUP_DRAW
    elif outcome == "lost":
        recovering = kicking
        if forced and u_recover < model.p_kick(kind, "lost_forcer_recovers"):
            recoverer, recoverer_basis = forcer, ball_security.FORCER
        else:
            pool = [pid for pid in coverage if pid != forcer] or coverage
            recoverer, recoverer_basis = ball_security.even(rng, pool), ball_security.GROUP_DRAW
    counts_as_fumble = kind == "return" or role is not None or outcome == "lost"
    receiving_line, kicking_line = stats[receiving], stats[kicking]
    if fumbler is not None:
        line = receiving_line["players"][fumbler]
        if kind == "muff":
            line["muffs"] = line.get("muffs", 0) + 1
            _team_bump(receiving_line, "muffs")
        if counts_as_fumble:
            _bump(line, "fumbles")
            _team_bump(receiving_line, "fumbles")
            if outcome == "lost":
                _bump(line, "fumbles_lost")
                _team_bump(receiving_line, "fumbles_lost")
    if forced:
        _bump(kicking_line["players"][forcer], "forced_fumbles")
    if recoverer is not None:
        if outcome == "lost":
            _bump(kicking_line["players"][recoverer], "fumble_recoveries")
            _team_bump(kicking_line, "kicking_team_recoveries")
        else:
            rline = receiving_line["players"][recoverer]
            rline["fumbles_recovered_own"] = rline.get("fumbles_recovered_own", 0) + 1
    attribution = {"fumbled_by": fumbler_basis}
    if forced:
        attribution["forced_by"] = forcer_basis
    if recoverer is not None:
        attribution["recovered_by"] = recoverer_basis
    if kind == "muff":
        row["muffed_by"] = fumbler
    row["fumble"] = {"kind": kind_raw, "outcome": outcome, "role": role, "fumbled_by": fumbler, "forced": forced,
                     "forced_by": forcer, "recovered_by": recoverer, "recovering_team": recovering,
                     "counted": counts_as_fumble, "attribution": attribution}
    if kind == "muff" and outcome == "kept" and row.get("play_type") == "punt" and row.get("return_yards"):
        # W4: the muffing club's own yards after recovering, never a punt return.
        row["own_recovery_yards"] = int(row["return_yards"])
    return {"kind": kind_raw, "outcome": outcome, "role": role, "forced": forced, "counted": counts_as_fumble}


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
    clock_detail=False,
    timeouts_used=(0, 0),
    game_type="regular",
    kernel_version=None,
    clock_plan=None,
    snap_calls=None,
    fumble_plan=None,
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

    Kernel 2014.6 (batch B6, W5a; profile flag clock_detail_v1): with
    `clock_detail`, snaps are stamped by clock_stamps from the base's W5a
    constants, the kick row at start - own + kick length, the drive's
    charged timeouts (`timeouts_used`, offense then defense) become timeout
    rows seated on the clock-detail stream, and a two-minute warning row is
    seated where the drive's stamps cross 2:00 of a period that has one
    (`game_type` names the Pro Bowl; `game_ledger` says whether the period's
    warning already exists). The sack gap is the 2014 value for
    `kernel_version` 2014.6 and later. Records only: no outcome changes.

    Kernel 2014.6 (batch B9F): a possession joined from segments (a drawn
    drive cut at a fourth-down decision, the resolved snap or kick, and a
    continuation drawn after a conversion) passes `clock_plan`
    {"stamps": [one per snap], "kick": kick stamp or None}, its stamps
    computed segment by segment from the same W5a constants; the plan
    replaces the single allocation. `snap_calls` {snap index: normalized
    sheet call} names the call of a resolved go snap: its carrier or target
    is drawn from the call's declared groups when they hold an available
    player, and its label is that call (``sheet:fourth-down-call``) when it
    can describe the snap. Neither changes a draw of the outcome.

    Kernel 2014.6 (batch B10, W4 and R12 layer A; profile flag
    ball_security_credit): `fumble_plan` {"model": the base's
    BallSecurityModel, "sources": [(offset, kept snaps, the replayed tuple's
    fumble list, its penalty records)], "terminal": the lost entry of a
    fumble_lost drive (or {"synthetic": kind} for a fumble the replayed
    drive does not describe), "terminal_kind": whether layer B
    (fumble_terminal_kind) is on} names every fumble of the drive on the
    public-ball-security-v1 stream ("scrim", drive): kept and out-of-bounds
    fumbles are seated on their laid-out snaps (runtime.ball_security
    .seat_kept), the fumbler is the snap's carrier (a kept aborted snap the
    quarterback's or the centre's at the sourced share; with layer B a lost
    aborted snap's terminal run is carried by one of them, drawn at the same
    share), the forcer and recoverer come from the
    side-aware on-field sets (runtime.participation.slot_lineup), a forced
    fumble's tackle is the forcer's, and a punt's muff or return fumble is
    credited from the punt play's units (credit_kick_fumble, stream
    ("punt", drive)). The snap-detail stream is untouched on a drive without
    a fumble; on a lost fumble's terminal snap it draws no defender.
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
    # Kernel 2014.6 batch B10: the drive's ball-security stream and its lost
    # fumble's entry (credit only; no other stream is read or advanced).
    bs_rng = ball_security.stream(seed, event_id, "scrim", drive_no) if fumble_plan is not None else None
    lost = None
    aborted_carrier = None
    if fumble_plan is not None and category == "fumble_lost":
        lost = fumble_plan.get("terminal")
        if isinstance(lost, dict) and lost.get("synthetic"):
            lost = fumble_plan["model"].synthetic_entry(lost["synthetic"], bs_rng)
        if lost is not None and lost["kind"] == "aborted" and terminal == "run" and fumble_plan.get("terminal_kind"):
            # Layer B (fumble_terminal_kind): an aborted snap is carried by the
            # quarterback or the centre (the sourced share; one uniform drawn).
            centre = front.get("C") if front else None
            u = bs_rng.random()
            aborted_carrier = centre if (centre is not None and u < fumble_plan["model"].p_centre_aborted) else qb
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
    pro_bowl = game_type == PRO_BOWL
    stamps = kick_stamp = None
    if clock_detail:
        from .statbook import kernel_at_least
        fp_model = cbase.field_position()
        w5a = getattr(fp_model, "clock_detail", None)
        if not w5a:
            raise ValueError("clock detail needs a calibration base with the W5a constants")
        sack_key = ("sack_2014w4" if kernel_at_least(kernel_version, SACK_GAP_FROM_KERNEL) else "sack_2010_2013")
        if clock_plan is not None:
            stamps, kick_stamp = [int(v) for v in clock_plan["stamps"]], clock_plan.get("kick")
            if len(stamps) != plays:
                raise ValueError("clock plan stamps %d snaps; the drive has %d" % (len(stamps), plays))
        else:
            stamps, kick_stamp = clock_stamps(
                w5a, kinds, completed, start_clock=start_clock, own=own,
                kick_length=fp_model.kick_length(category) if category in ("field_goal_attempt", "punt") else 0,
                sack_key=sack_key, overtime=overtime, pro_bowl=pro_bowl, diagnostics=diagnostics)
    elif clock_plan is not None:
        raise ValueError("a clock plan needs the clock detail (W5a) constants")
    snap_calls = dict(snap_calls or {})

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
        remaining = stamps[index] if stamps is not None else int(start_clock) - round(own * snap_no / plays)
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
                if fumble_plan is None:
                    _bump(qb_line, "fumbles")
                    _bump(qb_line, "fumbles_lost")
                    _bump(defense_stats["players"][rusher.player_id], "forced_fumbles")
                    _bump(defense_stats["players"][rusher.player_id], "fumble_recoveries")
                # Batch B10: the fumble itself is credited after the snaps
                # (_credit_scrimmage_fumbles), on its own stream.
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
                                  tilt=target_tilt, rank_shapes=rank_shapes,
                                  only=_call_only(snap_calls.get(index), "target", available))
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
                    if fumble_plan is None:
                        fumble(rec_line, record)
                    else:
                        record["turnover"] = True
                        record["turnover_type"] = "fumble"
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
            if is_terminal and aborted_carrier is not None:
                # Batch B10 (layer B): the aborted snap's carrier, no draw.
                runner = aborted_carrier
            else:
                called = _call_only(snap_calls.get(index), "carrier", available,
                                    lambda p: usage.group(p.position) != "QB" or p.player_id == qb.player_id)
                runner = usage.pick(
                    rng, available, shares["rush_share"], "rush", role="rusher",
                    only=called or (lambda p: usage.group(p.position) != "QB" or p.player_id == qb.player_id),
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
                if fumble_plan is None:
                    fumble(run_line, record)
                else:
                    record["turnover"] = True
                    record["turnover_type"] = "fumble"
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
    if kick_stamp is not None:
        # W5a: the kick row at start - own + kick length.
        kick_period, kick_clock = clock_at(kick_stamp)
        base_kick = {**base, "period": kick_period, "game_clock": kick_clock}
    else:
        base_kick = base
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
        ledger.append({**base_kick, "snap_in_drive": terminal_snap, "play_type": "field_goal",
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
        if punt_record["outcome"] in ("returned", PUNT_RETURN_TD):
            returner = _returner(rng, defenders, "punt_return")
            rline = defense_stats["players"][returner.player_id]
            _bump(rline, "punt_returns")
            _bump(rline, "punt_return_yards", ret)
            _bump(rline, "return_yards", ret)
            returner = returner.player_id
            if punt_record["outcome"] == "returned":
                # Kernel 2014.6 batch B9 (R15): a punt returned for a
                # touchdown has no coverage tackle.
                tackler = _coverage_tackle(rng, available, offense_stats["players"], "punt_coverage", (punter,))
                cover = tackler.player_id if tackler else None
        ledger.append({**base_kick, "snap_in_drive": terminal_snap, "play_type": "punt",
                       "punter": punter.player_id, "cover_player": cover, "long_snapper": snapper,
                       "punt_yards": gross, "returner": returner, "return_yards": ret,
                       "gross": gross, "enforcement": punt_record["enforcement"],
                       "outcome": punt_record["outcome"], "touchback": touchback,
                       "next_start": punt_record["next_start"], **fourth})
        retained = punt_record.get("possession") == "kicking"
        if fumble_plan is not None and (punt_record.get("fumble") or retained) \
                and punt_record["outcome"] not in PUNT_TD_OUTCOMES:
            # Batch B10 (W4, layer A): the punt's muff or return fumble, named
            # from the punt play's units on the ("punt", drive) stream.
            row = ledger[-1]
            units = participation.kick(row, team.team_id, defense.team_id, available, defenders)
            credit_kick_fumble(row, punt_record.get("fumble"), retained=retained, kicking=team.team_id,
                               receiving=defense.team_id, units=units,
                               stats={team.team_id: offense_stats, defense.team_id: defense_stats},
                               rng=ball_security.stream(seed, event_id, "punt", drive_no),
                               model=fumble_plan["model"], diagnostics=diagnostics)
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

    if fumble_plan is not None:
        _credit_scrimmage_fumbles(ledger, plays, kinds, completed, terminal, category, fumble_plan, lost, bs_rng,
                                  qb, front, available, defenders, offense_stats, defense_stats, team.team_id,
                                  defense.team_id, diagnostics)

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
        named = snap_calls.get(index)
        if named is not None and _call_fits(named, record, runner_group, target_group, runner_rank, target_rank):
            # Kernel 2014.6 batch B9F: the go snap's named call (Stone's live
            # answer or a block's), carrier-true by construction.
            call, source, scramble, slot = named, "sheet:" + FOURTH_DOWN_CALL, False, None
            label_groups = _groups(named["carrier"] if record["play_type"] == "run" else named["target"])
        else:
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

    if clock_detail:
        ledger = _seat_clock_rows(ledger, plays, team.team_id, defense.team_id, drive_no, w5a, kinds, completed,
                                  terminal, category, remaining_at, kick_stamp, stamps, timeouts_used,
                                  _clock_rng(seed, event_id=event_id, drive_no=drive_no, offense=team.team_id),
                                  start_clock, end_clock, overtime, pro_bowl, game_ledger, diagnostics)
    return ledger, call_stats


def _row_seconds(row, overtime):
    """A ledger row's stamp as seconds of the possession countdown."""
    minutes, seconds = (int(v) for v in row["game_clock"].split(":"))
    left = minutes * 60 + seconds
    period = row["period"]
    if isinstance(overtime, tuple):
        _, periods, length = overtime
        number = int(str(period)[2:] or 1) if isinstance(period, str) else 1
        return (periods - number) * length + left
    if overtime:
        return left
    return (4 - int(period)) * 900 + left


def _seat_clock_rows(ledger, plays, offense, defense, drive_no, w5a, kinds, completed, terminal, category,
                     remaining_at, kick_stamp, stamps, timeouts_used, crng, start_clock, end_clock, overtime,
                     pro_bowl, game_ledger, diagnostics):
    """W5a: the drive's rows with its timeout rows and two-minute warning
    seated. A timeout row is stamped with the clock of the snap that follows
    its seat (the clock is stopped), the kick's clock after the last snap, or
    the first snap's clock when seated before it. The warning is stamped
    2:00 and seated before the first row at or under 2:00 of its period."""
    has_kick = category in ("field_goal_attempt", "punt")
    snap_rows = ledger[:plays]
    after = ledger[plays:]
    insert = {i: [] for i in range(-1, plays)}
    off_used, def_used = (int(timeouts_used[0] or 0), int(timeouts_used[1] or 0))
    callers = [offense] * off_used + [defense] * def_used
    seats = timeout_seats(crng, w5a, kinds, completed, terminal, has_kick, len(callers), diagnostics)
    for caller, seat in zip(callers, seats):
        if seat + 1 < plays:
            remaining = remaining_at[seat + 1]
        elif kick_stamp is not None:
            remaining = kick_stamp
        else:
            remaining = remaining_at[0] if remaining_at else int(start_clock)
        if seat == -1:
            remaining = remaining_at[0] if remaining_at else int(start_clock)
        period, game_clock = _period_clock(remaining, closing=remaining <= int(end_clock), overtime=overtime)
        insert[seat].append({"drive": drive_no, "snap_in_drive": seat + 1, "period": period,
                             "game_clock": game_clock, "offense": offense, "defense": defense,
                             "play_type": TIMEOUT_ROW, "team": caller, "result_yards": 0, "touchdown": False,
                             "turnover": False, "decision_source": LEAGUE_MODEL})
    rows = list(insert[-1])
    for index, row in enumerate(snap_rows):
        rows.append(row)
        rows += insert[index]
    rows += after
    # Two-minute warnings this drive's span crosses, once per period.
    done = {r.get("period") for r in game_ledger if r.get("play_type") == TWO_MINUTE_WARNING_ROW}
    for mark in two_minute_marks(overtime, pro_bowl):
        if not (int(start_clock) > mark >= int(end_clock)):
            continue
        period, game_clock = _period_clock(mark, overtime=overtime)
        if period in done:
            continue
        warning = {"drive": drive_no, "snap_in_drive": None, "period": period, "game_clock": game_clock,
                   "offense": offense, "defense": defense, "play_type": TWO_MINUTE_WARNING_ROW,
                   "result_yards": 0, "touchdown": False, "turnover": False, "decision_source": LEAGUE_MODEL}
        at = next((i for i, r in enumerate(rows) if _row_seconds(r, overtime) <= mark), len(rows))
        warning["snap_in_drive"] = sum(1 for r in rows[:at] if r.get("play_type") in ("pass", "run"))
        rows.insert(at, warning)
        done.add(period)
    return rows


# Kernel 2014.6 batch B9 (R15): a punt returned or blocked for a touchdown.
PUNT_RETURN_TD = "return_td"
PUNT_BLOCKED_TD = "blocked_td"
PUNT_TD_OUTCOMES = (PUNT_RETURN_TD, PUNT_BLOCKED_TD)
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


def _try_key(anchor):
    return "kick-%s" % anchor["kick"] if "kick" in anchor else "drive-%s" % anchor["drive"]


def try_row(at, *, scoring, opponent, available, stats, made, seed, event_id, anchor, decision=None):
    """Kernel 2014.6 batch B8: the try row after a non-offensive touchdown (a
    kick return's or the defense's; R15, the try itself R8's). ``at`` gives
    the row's drive, period and game_clock. It is anchored to its score
    (``anchor`` = {"kick": kick_no} or {"drive": number}) and names
    ``scoring_team``, so the audit reads it against that kick or that
    possession's non_offensive_score, never as a possession's own try. The
    kicker and long snapper are named on a keyed detail stream; the kicker's
    try counters are credited here (the club's by the kernel).

    Kernel 2014.6 batch B9 (R8): ``decision`` (the try record's decision,
    basis, cell, chart p and points) is copied onto the row."""
    key = _try_key(anchor)
    rng = _stream(KICKOFF_DETAIL_TAG, seed, event_id, key, "try")
    kicker = usage.kicking_specialist(available, "K", "placekicker") or choose(rng, available, {"K"}, "placekicker")
    line = stats[scoring.team_id]["players"][kicker.player_id]
    _bump(line, "extra_points_attempted")
    if made:
        _bump(line, "extra_points_made")
    snapper = usage.long_snapper(available, usage.protection_front(available))
    if snapper is not None:
        _bump(stats[scoring.team_id]["players"][snapper.player_id], "long_snaps")
    row = {"drive": at["drive"], "snap_in_drive": at.get("snap_in_drive", 0), "period": at["period"],
           "game_clock": at["game_clock"], "offense": scoring.team_id, "defense": opponent,
           "play_type": "extra_point", "kicker": kicker.player_id, "made": bool(made),
           "long_snapper": snapper.player_id if snapper is not None else None,
           "result_yards": 0, "touchdown": False, "turnover": False,
           "anchor": dict(anchor), "scoring_team": scoring.team_id}
    if decision is not None:
        row.update(try_fields(decision))
    return row


# Kernel 2014.6 batch B9 (R8): the try record fields every try row carries
# (decision, basis, chart cell, the chart's go/tries pair and the points).
TRY_ROW_FIELDS = ("decision", "basis", "cell", "p_go", "points")
TRY_DETAIL_TAG = "public-try-detail-v1"
TWO_POINT_ROW = "two_point"
TRY_ROWS = ("extra_point", TWO_POINT_ROW)


def seat_try(rows, row, overtime=False):
    """Kernel 2014.6 batch B9 (R8): the index at which a drive's own
    two-point row is seated in its rows: where the extra-point row would
    stand. That is after the scoring snap, after any timeout row seated after
    the last snap, and after a two-minute-warning row whose mark is at or
    above the try's stamp (the warning is seated before the first row at or
    under 2:00, _seat_clock_rows)."""
    at = next(i for i, r in enumerate(rows) if r.get("play_type") in ("pass", "run") and r.get("touchdown")) + 1
    seconds = _row_seconds(row, overtime)
    while at < len(rows) and (rows[at].get("play_type") == TIMEOUT_ROW or (
            rows[at].get("play_type") == TWO_MINUTE_WARNING_ROW and _row_seconds(rows[at], overtime) >= seconds)):
        at += 1
    return at


def try_fields(decision):
    return {k: (list(decision[k]) if isinstance(decision.get(k), tuple) else decision.get(k)) for k in TRY_ROW_FIELDS}


def two_point_row(at, *, scoring, opponent, available, stats, made, seed, event_id, anchor, passer, decision,
                  pass_share, usage_base, scramble_rate=None):
    """Kernel 2014.6 batch B9 (R8): the row of one two-point try from the 2.

    Credit only, on its own keyed stream (public-try-detail-v1, by event and
    anchor; no team id): the play type is a pass with the league's
    pass share of two-point attempts (``pass_share``, the artifact's type
    counts; success does not depend on it under the adopted pooled rate),
    the passer is the drive's (or the scoring club's game passer after a
    non-offensive touchdown), the receiver by the usage target shares and
    the runner by the rush shares. A success credits
    passing_/receiving_ or rushing_two_point_conversions; no pass attempt,
    carry or yard is counted (the NFL convention). The descriptive call
    label comes from the sheet's two-point menu on its own label stream."""
    key = _try_key(anchor)
    rng = _stream(TRY_DETAIL_TAG, seed, event_id, key)
    shares = usage_base.usage()["values"]
    rank_shapes = shares["rank_shares"]
    factors = usage_base.tilt_factors()
    lines = stats[scoring.team_id]["players"]
    k, n = pass_share
    kind = "pass" if rng.random() < k / n else "run"
    qb = passer or usage.game_passer(available) or available[0]
    row = {"drive": at["drive"], "snap_in_drive": at.get("snap_in_drive", 0), "period": at["period"],
           "game_clock": at["game_clock"], "offense": scoring.team_id, "defense": opponent,
           "play_type": TWO_POINT_ROW, "try_type": kind, "passer": None, "runner": None, "target": None,
           "made": bool(made), "result_yards": 0, "touchdown": False, "turnover": False,
           "anchor": dict(anchor), "scoring_team": scoring.team_id, **try_fields(decision)}
    runner_group = target_group = runner_rank = target_rank = None
    if kind == "pass":
        tilt = usage.tilt_map(getattr(scoring, "strength", None), available, "target", factors)
        receiver = usage.pick(rng, available, shares["target_share"], "target", role="receiver", tilt=tilt,
                              rank_shapes=rank_shapes)
        row["passer"], row["target"] = qb.player_id, receiver.player_id
        target_group, target_rank = usage.group(receiver.position), _group_rank(available, receiver)
        if made:
            _bump(lines[qb.player_id], "passing_two_point_conversions")
            _bump(lines[receiver.player_id], "receiving_two_point_conversions")
    else:
        tilt = usage.tilt_map(getattr(scoring, "strength", None), available, "rush", factors)
        runner = usage.pick(rng, available, shares["rush_share"], "rush", role="rusher",
                            only=lambda p: usage.group(p.position) != "QB" or p.player_id == qb.player_id,
                            tilt=tilt, rank_shapes=rank_shapes)
        row["runner"] = runner.player_id
        runner_group, runner_rank = usage.group(runner.position), _group_rank(available, runner)
        if made:
            _bump(lines[runner.player_id], "rushing_two_point_conversions")
    lrng = _stream(LABEL_TAG, seed, event_id, key, "try")
    situation = {"menus": list(call_situations.classify_try())}
    call, source, label_groups, scramble, _slot = _choose_label(
        lrng, scoring, {"play_type": kind, "sack": False}, runner_group, target_group, runner_rank, target_rank,
        situation, None, scramble_rate)
    row.update({"concept": call["name"], "family": call["family"], "personnel": call["personnel"],
                "formation": call["formation"], "motion": call["motion"], "protection": call["protection"],
                "tags": list(call["tags"]), "label_source": source, "label_type": call["type"],
                "label_groups": label_groups, "situation": situation["menus"][0], "scramble": scramble})
    return row


# ---- possession sequencing (kernel 2014.6, batch B8) -----------------------

# The compact kicks summary a receipt carries (one row per kick, in kick
# order): the kick's number, kicking and receiving club, half, the game
# seconds remaining when it was kicked, its position on its chain, the
# possession it followed (None for a half's opener) and the possession it
# precedes, whether it was a safety free kick, its outcome, its decision
# basis, the start it gave and the points it scored (a return touchdown with
# its try; None otherwise). Append-only, like DRIVE_SUMMARY_FIELDS.
KICK_SUMMARY_FIELDS = ("kick_no", "kicking", "receiving", "half", "remaining", "chain", "after_drive",
                       "drive", "free_kick", "outcome", "basis", "next_start", "points",
                       # Kernel 2014.6 batch B9 (append-only): R9's onside
                       # decision, its chart cell and recovery class, a
                       # return touchdown's try record (R8) and the kick's
                       # return yards (the band rows leave a return
                       # touchdown's out of the drawn pool's mean).
                       "onside", "cell", "recovery_class", "try", "return_yards",
                       # Kernel 2014.6 batch B10 (append-only): the kick's
                       # credited muff or return fumble (kind, outcome, the
                       # record's muffer role, forced, counted as a fumble).
                       "fumble")
RETAINED_OUTCOME = "retained"
RETURN_TOUCHDOWN_OUTCOME = "returned_touchdown"


def has_kick_sequence(result):
    """True when every kick record carries the batch B8 chain fields."""
    kicks = result.get("kickoffs")
    if kicks is None:
        return "kicks" in result
    return all("chain" in k for k in kicks)


def kick_summary(kickoffs):
    """Compact per-kick rows for receipts (KICK_SUMMARY_FIELDS)."""
    return [[k.get(field) for field in KICK_SUMMARY_FIELDS] for k in kickoffs]


def kicks_of(result):
    """The kicks of a result (its kick records) or a receipt (its kicks
    summary rows as mappings), in kick order; [] when neither is present."""
    if result.get("kickoffs") is not None:
        kicks = list(result["kickoffs"])
    else:
        kicks = [dict(zip(KICK_SUMMARY_FIELDS, row)) for row in result.get("kicks", ())]
    return sorted(kicks, key=lambda k: k.get("kick_no", 0))


def is_touchback(kick):
    """A kick record's touchback flag, or on a summary row its outcome (the
    flag and the outcome agree on every record of both bases)."""
    return bool(kick["touchback"]) if "touchback" in kick else kick.get("outcome") == "touchback"


ONSIDE_START_KINDS = {"onside_recovered": "onside_recovery", "onside_lost": "onside_lost"}
KEPT_OUTCOMES = (RETAINED_OUTCOME, "onside_recovered")


def expected_start_kind(kick):
    """The start kind of the possession a kick hands over (kernel._start_kind)."""
    if kick.get("outcome") in ONSIDE_START_KINDS:
        return ONSIDE_START_KINDS[kick["outcome"]]
    retained = kick.get("outcome") == RETAINED_OUTCOME
    if kick.get("free_kick"):
        return "free_kick_retained" if retained else "free_kick"
    if retained:
        return "kickoff_retained"
    return "kickoff_touchback" if is_touchback(kick) else "kickoff"


def scoring_events(result):
    """Every score of a game in game order, rebuilt from the possessions (or
    a receipt's drives) and the kicks: {"kind", "team", "points", "half",
    "source": "drive" | "kick", and "drive" or "kick_no"}. A kick's event
    precedes the possession whose number it carries. Never read from the
    stored list: the audit compares the rebuild to it. Kernel 2014.6 batch
    B9 (R8): a touchdown's event also carries its try record ("try") when the
    kernel decided one (absent for a walk-off and for earlier records)."""
    from .rules import kick_score, possession_score
    teams = list(result.get("final_score") or result.get("score") or {})
    other = {t: next((u for u in teams if u != t), None) for t in teams}
    possessions = _possessions(result)
    kicks = kicks_of(result)
    by_drive = {}
    for kick in kicks:
        by_drive.setdefault(kick.get("drive"), []).append(kick)
    events = []

    def kick_events(group):
        for kick in group:
            score = kick_score(kick)
            if score is not None:
                events.append({"kind": score[0], "team": score[1], "points": score[2], "half": kick.get("half"),
                               "source": "kick", "kick_no": kick.get("kick_no")})
                if kick.get("try") is not None:
                    events[-1]["try"] = kick["try"]

    for p in possessions:
        kick_events(by_drive.pop(p["number"], ()))
        score = possession_score(p, other.get(p.get("team")))
        if score is not None:
            events.append({"kind": score[0], "team": score[1], "points": score[2], "half": p.get("half"),
                           "source": "drive", "drive": p["number"]})
            non_offensive = p.get("non_offensive_score") or {}
            decided = non_offensive.get("try") if non_offensive.get("kind") else p.get("try")
            if decided is not None:
                events[-1]["try"] = decided
    for number in sorted(k for k in by_drive if k is not None):
        kick_events(by_drive[number])
    return events


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

    __slots__ = ("name", "group", "measurable", "listed_from", "audit_only")

    def __init__(self, name, group, measurable, listed_from=None, audit_only=False):
        self.name, self.group, self.measurable, self.listed_from = name, group, measurable, listed_from
        # Kernel 2014.6 batch B6: an audit-only class is measured and
        # reported (bands.audit_only_coherence) but is not a violation:
        # check_ledger leaves it out, so validate_result never refuses a game
        # on it, until the acceptance sweep reads 0 and it becomes zero
        # tolerance (plan B6; a later batch flips the attribute).
        self.audit_only = audit_only

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
    # Kernel 2014.6 batch B6 (W3, W5a): evaluated on a 2014.6-or-later
    # result or receipt with the full snap ledger and the timeout state.
    "b6_ledger": lambda r: from_kernel("2014.6")(r) and has_spots(r) and has_timeouts(r) and _ledger(r),
    # Kernel 2014.6 batch B8 (possession sequencing): evaluated on a
    # 2014.6-or-later result or receipt whose kicks carry the chain fields
    # (has_kick_sequence); zero tolerance from the start, since no branch
    # fires until B9 and B10 and every game must already sequence cleanly.
    "b8_sequence": lambda r: from_kernel("2014.6")(r) and has_spots(r) and has_kick_sequence(r),
    # Kernel 2014.6 batch B9F (live fourth downs): evaluated on a
    # 2014.6-or-later result or receipt whose every possession carries its
    # fourth-down decision records (has_fourth_downs); zero tolerance.
    "b9f_fourth": lambda r: from_kernel("2014.6")(r) and has_spots(r) and has_fourth_downs(r),
    # Kernel 2014.6 batch B10 (ball security): evaluated on a 2014.6-or-later
    # result or receipt carrying the ball-security marker (has_ball_security);
    # the ledger-free reconciliation reads the drives and kicks summaries,
    # the row checks the full snap ledger; zero tolerance.
    "b10_ball": lambda r: from_kernel("2014.6")(r) and has_spots(r) and has_ball_security(r),
}
_LISTED_FROM = {"b6_ledger": "2014.6", "b8_sequence": "2014.6", "b9f_fourth": "2014.6", "b10_ball": "2014.6"}


def _registry(rows):
    out = []
    for group, names in rows:
        for name in names:
            out.append(CoherenceClass(name, group, _GROUP_PREDICATES[group], listed_from=_LISTED_FROM.get(group),
                                      audit_only=group == "b6_ledger"))
    return tuple(out)


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
    # Kernel 2014.6 batch B6 (listed from the 2014.6 cohort; audit-only
    # until the acceptance sweep reads 0): W3's field goal before fourth down
    # and W5a's clock-detail records.
    ("b6_ledger", ("field_goal_before_fourth_down", "kick_clock_shared", "snap_at_zero", "timeout_rows_mismatch",
                   "two_minute_warning_missing")),
    # Kernel 2014.6 batch B8 (listed from the 2014.6 cohort): the next
    # possessor follows from the event that ended the last possession, and
    # every kick sits coherently on its chain (side-aware, touchdown rows
    # exempt from the hand-over checks).
    ("b8_sequence", ("possession_sequence_break", "kick_chain_incoherent")),
    # Kernel 2014.6 batch B9F (listed from the 2014.6 cohort): every fourth
    # down was decided, each decision record agrees with the walked snaps,
    # the ledger and the possession's category, and a joined possession's
    # segments join.
    ("b9f_fourth", ("fourth_down_decision_incoherent",)),
    # Kernel 2014.6 batch B10 (listed from the 2014.6 cohort): every fumble's
    # credit reconciles with its records and counters, and every muffed kick
    # names its muffer.
    ("b10_ball", ("fumble_credit_incoherent", "muff_without_muffer")),
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
B6_CLASSES = _names("b6_ledger")
B8_CLASSES = _names("b8_sequence")
B9F_CLASSES = _names("b9f_fourth")
B10_CLASSES = _names("b10_ball")
AUDIT_ONLY_CLASSES = tuple(c.name for c in COHERENCE_REGISTRY if c.audit_only)


def classes_for_cohort(version=None, include_audit_only=False):
    """The classes a cohort's audit table lists: every class with no
    listed_from, plus those listed from that kernel cohort or earlier.
    Audit-only classes (kernel 2014.6 batch B6) are listed only on request."""
    from .statbook import kernel_at_least
    out = []
    for c in COHERENCE_REGISTRY:
        if c.audit_only and not include_audit_only:
            continue
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
    # Kernel 2014.6 batch B8 (append-only; the slot R15, batch B9, fills):
    # a non-offensive score made during the possession
    # (runtime.rules.possession_score reads it first).
    "non_offensive_score",
    # Kernel 2014.6 batch B9 (R8, append-only): an offensive touchdown's try
    # record (decision, basis, chart cell and pair, made, points, type), so a
    # compact receipt audits the try and its scoring event like the result.
    "try",
    # Kernel 2014.6 batch B9F (append-only): the possession's fourth-down
    # decision records and, for a possession a decision changed, its
    # segments, so a compact receipt audits them like the result.
    "fourth_downs", "segments",
    # Kernel 2014.6 batch B10 (append-only): the possession's credited
    # scrimmage fumbles (kind, outcome, forced, the seated snap), so a
    # compact receipt grades and audits them like the result.
    "fumbles",
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


def has_fourth_downs(result):
    """Kernel 2014.6 batch B9F: every possession carries its fourth-down
    decision records (a list, empty when it had no decision point)."""
    possessions = _possessions(result)
    return bool(possessions) and all(isinstance(p.get("fourth_downs"), list) for p in possessions)


def _segment_key(seg):
    """The envelope key of a joined possession's replayed segment."""
    terminal = str(seg.get("terminal") or seg.get("category"))
    return "clock" if terminal.startswith("end_of_") else terminal


def _model_terminal(p):
    """Kernel 2014.6 batch B9F: the possession's terminal is a fourth-down
    decision's outcome, not a drawn tuple's own (its last segment was cut)."""
    segments = p.get("segments")
    return bool(segments) and segments[-1].get("end") != "replayed"


FOURTH_DOWN_ACTIONS = ("go", "field_goal", "punt")
FOURTH_DOWN_TIMINGS = ("before_third_down", "at_fourth_down")
FOURTH_DOWN_OUTCOME_CATEGORY = {"touchdown": "touchdown", "failed": "downs", "interception": "interception",
                                "fumble_lost": "fumble_lost", "field_goal": "field_goal_attempt",
                                "punt": "punt"}


def _check_fourth_downs(possessions, rows_by_drive, err):
    """Kernel 2014.6 batch B9F: fourth_down_decision_incoherent.

    Every decision record is well formed (an action, a basis, a timing, a
    fourth-down state inside the field), only the last one ends the
    possession, a replayed decision is the drawn drive's own kick, a model
    outcome agrees with the possession's category, and a joined possession's
    segments join (the first starts at the possession's start, each
    continued one hands its end to the next, their snaps and own seconds add
    up). With the full snap ledger: every fourth-down scrimmage snap that is
    not a kneel or spike and every kick at fourth down carries its decision
    mark, and each record's row has its state and outcome."""
    bases = ("league", "delegated:league", "live")
    for p in possessions:
        number, category = p["number"], p["category"]
        category = "clock" if str(category).startswith("end_of_") else category
        records = p.get("fourth_downs") or []
        where = "drive %s" % number
        for k, rec in enumerate(records):
            state = rec.get("state") or {}
            basis = str(rec.get("basis"))
            last = k == len(records) - 1
            problem = None
            if rec.get("decision") not in FOURTH_DOWN_ACTIONS or rec.get("timing") not in FOURTH_DOWN_TIMINGS:
                problem = "decision or timing"
            elif basis not in bases and not (basis.startswith("policy:") and basis[7:].isdigit()):
                problem = "basis %s" % basis
            elif not (state.get("down") == 4 and isinstance(state.get("los"), int) and 1 <= state["los"] <= 99
                      and isinstance(state.get("ydstogo"), int) and 1 <= state["ydstogo"] <= state["los"]
                      and bool(state.get("goal_to_go")) == (state["ydstogo"] == state["los"])):
                problem = "state %s" % state
            elif rec.get("terminal") and not last:
                problem = "only the last decision ends the possession"
            elif rec.get("resolution") == "replayed":
                if rec["decision"] == "go" or rec.get("replay") != rec["decision"] or \
                        FOURTH_DOWN_OUTCOME_CATEGORY[rec["decision"]] != category:
                    problem = "replayed decision is not the drive's own kick"
            elif rec.get("resolution") != "model":
                problem = "resolution %s" % rec.get("resolution")
            elif rec["decision"] == "go":
                outcome = rec.get("outcome")
                if not rec.get("conversion") or outcome not in ("converted", "touchdown", "failed", "interception",
                                                                 "fumble_lost"):
                    problem = "go outcome %s" % outcome
                elif rec.get("terminal") and outcome == "converted" and category != "clock":
                    problem = "a conversion ended the possession without the clock"
                elif rec.get("terminal") and outcome != "converted" and \
                        FOURTH_DOWN_OUTCOME_CATEGORY[outcome] != category:
                    problem = "go outcome %s against category %s" % (outcome, category)
                elif not rec.get("terminal") and outcome != "converted":
                    problem = "a failed go did not end the possession"
            elif FOURTH_DOWN_OUTCOME_CATEGORY[rec["decision"]] != category or not rec.get("terminal"):
                problem = "kick decision against category %s" % category
            if problem:
                err("fourth_down_decision_incoherent", "%s decision %d: %s" % (where, k, problem))
        segments = p.get("segments")
        if segments:
            modelled = [r for r in records if r.get("resolution") == "model"]
            continued = [seg for seg in segments if seg.get("end") == "continued"]
            problem = None
            if not modelled:
                problem = "segments without a model decision"
            elif records and not records[-1].get("terminal") and segments[-1].get("end") != "replayed":
                problem = "the possession ended after a conversion without a replayed segment"
            elif segments[0].get("start") != p.get("start_spot"):
                problem = "first segment starts at %s" % segments[0].get("start")
            elif len(continued) != len(segments) - 1 or segments[-1].get("end") == "continued":
                problem = "segment ends %s" % [seg.get("end") for seg in segments]
            elif len(continued) != sum(1 for r in records if r.get("outcome") == "converted" and not r.get("terminal")):
                problem = "continued segments do not match the conversions"
            elif any(b.get("start") != a.get("start") - a.get("net", 0) for a, b in zip(segments, segments[1:])):
                problem = "a continuation does not start where the conversion ended"
            elif sum(seg.get("plays", 0) for seg in segments) != p.get("scrimmage_plays"):
                problem = "segment snaps do not add up"
            elif p.get("own_seconds") is not None and sum(seg.get("own_seconds", 0) for seg in segments) != \
                    p["own_seconds"]:
                problem = "segment seconds do not add up"
            if problem:
                err("fourth_down_decision_incoherent", "%s: %s" % (where, problem))
        elif any(r.get("resolution") == "model" for r in records) or len(records) > 1:
            err("fourth_down_decision_incoherent", "%s: a model decision without segments" % where)
        if rows_by_drive is None:
            continue
        rows = rows_by_drive.get(number, [])
        scrim = [r for r in rows if r.get("play_type") in ("pass", "run")]
        kicks = [r for r in rows if r.get("play_type") in ("punt", "field_goal")]
        marked = 0
        for r in scrim:
            if r.get("down") == 4 and not (r.get("kneel") or r.get("spike")):
                marked += 1
                if not r.get("fourth_down_decision"):
                    err("fourth_down_decision_incoherent", "%s snap %s: an undecided fourth down"
                        % (where, r.get("snap_in_drive")))
        for r in kicks:
            if r.get("down") == 4:
                marked += 1
                if not r.get("fourth_down_decision"):
                    err("fourth_down_decision_incoherent", "%s %s: an undecided fourth-down kick"
                        % (where, r["play_type"]))
        if marked != len(records):
            err("fourth_down_decision_incoherent", "%s: %d fourth downs, %d decisions" % (where, marked,
                                                                                        len(records)))
            continue
        for k, rec in enumerate(records):
            state = rec.get("state") or {}
            if rec.get("decision") == "go":
                index = rec.get("index")
                row = scrim[index] if isinstance(index, int) and 0 <= index < len(scrim) else None
                ok = row is not None and (row.get("down"), row.get("ydstogo"), row.get("yardline")) == (
                    4, state.get("ydstogo"), state.get("los")) and \
                    (row.get("fourth_down_decision") or {}).get("basis") == rec.get("basis")
                if ok and rec.get("outcome") in ("converted", "touchdown"):
                    ok = bool(row.get("first_down")) or bool(row.get("touchdown"))
                elif ok:
                    ok = row is scrim[-1] and not row.get("first_down")
            else:
                row = kicks[0] if kicks else None
                ok = row is not None and (row.get("down"), row.get("ydstogo"), row.get("los")) == (
                    4, state.get("ydstogo"), state.get("los")) and \
                    (row.get("fourth_down_decision") or {}).get("decision") == rec.get("decision")
            if not ok:
                err("fourth_down_decision_incoherent", "%s decision %d: the ledger row disagrees" % (where, k))


def has_ball_security(result):
    """Kernel 2014.6 batch B10: the result or receipt was resolved with the
    ball-security credit (its marker)."""
    marker = result.get("ball_security")
    return isinstance(marker, dict) and bool(marker.get("credit"))


def _kick_fumbles(result, possessions, kick_list):
    """(receiving club, kicking club, compact fumble) of every kick play's
    credited muff or return fumble: kickoffs and free kicks (their records or
    the kicks summary) and punts (the drive's punt summary)."""
    out = []
    for k in kick_list:
        if isinstance(k.get("fumble"), dict):
            out.append((k.get("receiving"), k.get("kicking"), k["fumble"]))
    teams = list(result.get("final_score", {}))
    for p in possessions:
        punt = p.get("punt") or {}
        if isinstance(punt.get("fumble"), dict):
            other = next((t for t in teams if t != p["team"]), None)
            out.append((other, p["team"], punt["fumble"]))
    return out


def _check_ball_security(result, possessions, kick_list, ledger, err):
    """Kernel 2014.6 batch B10 classes (zero tolerance).

    fumble_credit_incoherent: each club's fumbles, lost fumbles and muffs
    (team counters) equal its players' sums and its records' (the drives'
    credited scrimmage fumbles and the kick plays' counted muffs and return
    fumbles); the forced fumbles, the opponent-ball recoveries and the own
    recoveries the other club's or its own players hold equal the forced,
    lost and kept records; the kicking-team recoveries equal its kept kicks;
    and, with the full snap ledger, every fumble record names its fumbler, a
    forcer exactly when forced, no recoverer out of bounds, the recovering
    club by its outcome, a lost scrimmage fumble on a turnover row and a kept
    one on a row that is not, and every fumble turnover row carries its
    record. muff_without_muffer: every muffed kick row names its muffer (the
    record's fumbler), and a muffed punt credits no return and no coverage
    tackle."""
    teams = result.get("team_stats", {})
    if not teams:
        return
    kick_fumbles = _kick_fumbles(result, possessions, kick_list)
    for team, s in teams.items():
        players = s.get("players", {})
        mine = [f for p in possessions if p["team"] == team for f in (p.get("fumbles") or ())]
        theirs = [f for p in possessions if p["team"] != team for f in (p.get("fumbles") or ())]
        kicks_mine = [f for r, _, f in kick_fumbles if r == team]
        kicks_theirs = [f for r, _, f in kick_fumbles if r != team]
        fumbles = len(mine) + sum(1 for f in kicks_mine if f.get("counted"))
        lost = sum(f["outcome"] == "lost" for f in mine) + sum(f["outcome"] == "lost" for f in kicks_mine)
        muffs = sum(f.get("kind") == "muff" for f in kicks_mine)
        totals = {field: sum(line.get(field, 0) or 0 for line in players.values())
                  for field in ("fumbles", "fumbles_lost", "muffs", "forced_fumbles", "fumble_recoveries",
                                "fumbles_recovered_own")}
        if not (s.get("fumbles") == totals["fumbles"] == fumbles):
            err("fumble_credit_incoherent", "%s fumbles: team %s, players %s, records %s"
                % (team, s.get("fumbles"), totals["fumbles"], fumbles))
        if not (s.get("fumbles_lost") == totals["fumbles_lost"] == lost):
            err("fumble_credit_incoherent", "%s lost fumbles: team %s, players %s, records %s"
                % (team, s.get("fumbles_lost"), totals["fumbles_lost"], lost))
        if not (s.get("muffs") == totals["muffs"] == muffs):
            err("fumble_credit_incoherent", "%s muffs: team %s, players %s, records %s"
                % (team, s.get("muffs"), totals["muffs"], muffs))
        forced = sum(bool(f.get("forced")) for f in theirs) + sum(bool(f.get("forced")) for f in kicks_theirs)
        if totals["forced_fumbles"] != forced:
            err("fumble_credit_incoherent", "%s forced fumbles %s, records %s" % (team, totals["forced_fumbles"], forced))
        recovered = sum(f["outcome"] == "lost" for f in theirs) + sum(f["outcome"] == "lost" for f in kicks_theirs)
        if totals["fumble_recoveries"] != recovered:
            err("fumble_credit_incoherent", "%s recoveries %s, opponent lost fumbles %s"
                % (team, totals["fumble_recoveries"], recovered))
        own = sum(f["outcome"] == "kept" for f in mine) + sum(f["outcome"] == "kept" for f in kicks_mine)
        if totals["fumbles_recovered_own"] != own:
            err("fumble_credit_incoherent", "%s own recoveries %s, kept fumbles %s"
                % (team, totals["fumbles_recovered_own"], own))
        if s.get("kicking_team_recoveries") != sum(f["outcome"] == "lost" for f in kicks_theirs):
            err("fumble_credit_incoherent", "%s kicking-team recoveries %s" % (team, s.get("kicking_team_recoveries")))
    if not ledger:
        return
    by_number = {p["number"]: p for p in possessions}
    seen = {}
    for row in ledger:
        kind = row.get("play_type")
        record = row.get("fumble")
        where = "drive %s sequence %s" % (row.get("drive"), row.get("sequence"))
        kick_row = kind in KICK_TYPES or kind == "punt"
        if kind in ("pass", "run") and row.get("turnover_type") == "fumble" and not isinstance(record, dict):
            err("fumble_credit_incoherent", "%s fumble turnover without its record" % where)
        if kick_row and (row.get("outcome") == "muffed" or (isinstance(record, dict) and record.get("kind") == "muff")):
            if not row.get("muffed_by") or not isinstance(record, dict) or record.get("fumbled_by") != row["muffed_by"]:
                err("muff_without_muffer", where)
            if kind == "punt" and (row.get("returner") or row.get("cover_player")):
                err("muff_without_muffer", "%s muffed punt credits a return or a coverage tackle" % where)
        if not isinstance(record, dict):
            continue
        outcome = record.get("outcome")
        fumbling = row.get("defense") if kick_row else row.get("offense")
        other = row.get("offense") if kick_row else row.get("defense")
        if not record.get("fumbled_by"):
            err("fumble_credit_incoherent", "%s names no fumbler" % where)
        if bool(record.get("forced")) != bool(record.get("forced_by")):
            err("fumble_credit_incoherent", "%s forced %s with forcer %s" % (where, record.get("forced"),
                                                                            record.get("forced_by")))
        if outcome == "oob" and (record.get("recovered_by") or record.get("recovering_team")):
            err("fumble_credit_incoherent", "%s out of bounds with a recoverer" % where)
        if outcome in ("kept", "lost") and record.get("recovering_team") != (fumbling if outcome == "kept" else other):
            err("fumble_credit_incoherent", "%s %s recovered by %s" % (where, outcome, record.get("recovering_team")))
        if not kick_row and bool(row.get("turnover")) != (outcome == "lost"):
            err("fumble_credit_incoherent", "%s %s fumble on a %sturnover row" % (
                where, outcome, "" if row.get("turnover") else "non-"))
        if kick_row and (outcome == "lost") != (row.get("outcome") == RETAINED_OUTCOME):
            err("fumble_credit_incoherent", "%s kick fumble %s on a %s kick" % (where, outcome, row.get("outcome")))
        if not kick_row:
            seen[row.get("drive")] = seen.get(row.get("drive"), 0) + 1
    for number, p in by_number.items():
        if len(p.get("fumbles") or ()) != seen.get(number, 0):
            err("fumble_credit_incoherent", "drive %s records %d fumbles, its rows %d"
                % (number, len(p.get("fumbles") or ()), seen.get(number, 0)))


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
        if p.get("segments"):
            # Kernel 2014.6 batch B9F: each replayed segment's own seconds lie
            # in the range of its own snap count (a segment cut at a decision
            # is a prefix of a real drive's allocation).
            for seg in p["segments"]:
                if seg.get("end") != "replayed":
                    continue
                span = ranges.get(seg.get("plays"))
                if span is None or not span[0] <= seg.get("own_seconds", -1) <= span[1]:
                    err("seconds_per_snap_outside", "drive %s segment: %s snaps in %s s" % (
                        number, seg.get("plays"), seg.get("own_seconds")))
        else:
            span = ranges.get(p.get("scrimmage_plays"))
            if span is None or not span[0] <= own <= span[1]:
                err("seconds_per_snap_outside", "drive %s: %s snaps in %s s" % (number, p.get("scrimmage_plays"),
                                                                                 own))
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
    """The kind of score a possession produced (runtime.rules.possession_score)."""
    from .rules import possession_score
    score = possession_score(p)
    return score[0] if score else None


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
        segments = p.get("segments")
        if segments:
            # Kernel 2014.6 batch B9F: a possession joined from segments. Its
            # replayed segments are real drives, each checked from its own
            # start; a segment cut at a fourth-down decision ends in the
            # decision's outcome, not a replayed category
            # (fourth_down_decision_incoherent audits it).
            envelope = None
            for seg in segments:
                if seg.get("end") != "replayed":
                    continue
                seg_key = _segment_key(seg)
                envelope = fp.load()["envelopes"][seg_key][fp.start_bin(seg["start"])]
                if envelope is None:
                    err("category_impossible_at_start", "drive %s segment %s from %s" % (number, seg_key,
                                                                                          seg["start"]))
            if not segments[-1].get("end") == "replayed":
                envelope = True  # the terminal is a decision's outcome
        elif envelope is None and not _zero_play_expiry(p):
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
        if category == "field_goal_attempt" and not p.get("fg_made") and not p.get("non_offensive_score") \
                and nxt != fp.missed_fg_start(p["fg_distance"]):
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
            elif draw_half == 2 and fd["cell"] != "neutral" and not _model_terminal(p) and (
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


def _check_spot_ledger(result, possessions, rows_by_drive, kicks, err, sequencing=False):
    """Kick-row and label classes (full snap ledger, kernel 2013.7 onward).

    Kernel 2014.6 batch B8: for the sequencing cohort the kick rows' spot
    identity is side-aware and lives in kick_chain_incoherent (a kick the
    kicking club keeps lands in its own frame; a return touchdown has no
    hand-over), so the receiving-frame identity below is not applied."""
    by_number = {p["number"]: p for p in possessions}
    for k in ([] if sequencing else kicks):
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
        if row.get("outcome") in PUNT_TD_OUTCOMES:
            continue  # kernel 2014.6 batch B9 (R15): no hand-over; the scorer kicks off
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
        elif row.get("outcome") == RETAINED_OUTCOME:
            # Kernel 2014.6 batch B10 (R12 layer C): a punt the kicking club
            # kept lands in its own frame (LOS - gross + return + enforcement).
            if nxt != los - (row.get("gross") or 0) + (row.get("return_yards") or 0) + e:
                err("kick_spot_mismatch", "retained punt identity on drive %s" % p["number"])
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


def return_touchdown_distance_errors(result):
    """Kernel 2014.6 batch B9 (R15; review round 2): every return touchdown
    covers runtime.scoring_decisions.RETURN_TD_YARDS (1 to 109 yards). Reads a
    result or a receipt: each possession's sourced non_offensive_score, each
    kickoff from the 35 that took an onside decision and was run back for a
    touchdown (a real return record of R15), and, with the full snap ledger,
    those scores' rows (the row that scored and the kick's row). A test-only
    placeholder touchdown (batch B8 hook, no source and no onside decision) is
    not R15's and is left out. Returns detail strings; [] when clean."""
    from .scoring_decisions import RETURN_TD_YARDS

    low, high = RETURN_TD_YARDS

    def bad(value):
        return isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high

    out = []
    sourced = set()
    for p in _possessions(result):
        score = p.get("non_offensive_score") or {}
        if score.get("source") is not None:
            sourced.add(p["number"])
            if bad(score.get("return_yards")):
                out.append("drive %s %s touchdown covers %r yards" % (p["number"], score["source"],
                                                                     score.get("return_yards")))
    kick_list = kicks_of(result)
    for k in kick_list:
        if k.get("onside") is not None and k.get("outcome") == RETURN_TOUCHDOWN_OUTCOME and bad(k.get("return_yards")):
            out.append("kick %s return touchdown covers %r yards" % (k.get("kick_no"), k.get("return_yards")))
    ledger = result.get("play_ledger") or []
    kick_rows = [r for r in ledger if r.get("play_type") in KICK_TYPES]
    for row, k in zip(kick_rows, kick_list):
        if k.get("onside") is not None and row.get("touchdown") and bad(row.get("return_yards")):
            out.append("kick %s touchdown row covers %r yards" % (k.get("kick_no"), row.get("return_yards")))
    for row in ledger:
        if (row.get("play_type") not in KICK_TYPES and row.get("drive") in sourced and row.get("touchdown")
                and row.get("scoring_team") not in (None, row.get("offense")) and bad(row.get("return_yards"))):
            out.append("drive %s touchdown row covers %r yards" % (row.get("drive"), row.get("return_yards")))
    return out


def check_ledger(result, base=None, audit_only=False):
    """Coherence errors for one closed game, as 'class: detail' strings.

    Runs the ledger-free checks on the possession list (or a receipt's compact
    'drives' summary) and, when a full snap ledger is present, the snap-level
    checks as well. Receipts without start spots (kernels before 2013.7) get
    exactly their 2013.6 checks. An empty list means no violation was found.

    Kernel 2014.6 plumbing (batch B1): every audit uses the calibration base
    and cell rules of the result's own kernel_version
    (runtime.calibration_base.base_for_result; an unknown version raises).
    `base` overrides that only for synthetic tests of a test base.

    Kernel 2014.6 batch B6: the audit-only classes (AUDIT_ONLY_CLASSES) are
    left out unless `audit_only` is true (audit_only_errors), so no game is
    refused on them while they are audit-only."""
    from .rules import kick_score, kick_try_made, ot_history, ot_status, possession_score
    from .calibration_base import base_for_result

    base = base if base is not None else base_for_result(result)
    errors = []
    skipped = set() if audit_only else set(AUDIT_ONLY_CLASSES)

    def err(cls, detail):
        if cls in skipped:
            return
        errors.append("%s: %s" % (cls, detail))

    possessions = _possessions(result)
    if not possessions and not (_GROUP_PREDICATES["b8_sequence"](result) and kicks_of(result)):
        return errors
    spots = has_spots(result)
    game_type = result.get("game_type", "regular")
    teams = list(result.get("final_score", {}))
    other = {t: next((u for u in teams if u != t), None) for t in teams}
    regulation = [p for p in possessions if p["half"] in (1, 2)]
    overtime = [p for p in possessions if p["half"] == "OT"]
    last = possessions[-1] if possessions else None
    # Kernel 2014.6 batch B8: the sequencing cohort reads its kicks (records
    # or the receipt's summary) and audits the hand-over between possessions
    # side-aware; earlier cohorts keep their frozen checks byte for byte.
    sequencing = _GROUP_PREDICATES["b8_sequence"](result)
    kick_list = kicks_of(result) if sequencing else []
    kicks_after = {}
    for k in kick_list:
        kicks_after.setdefault(k.get("after_drive"), []).append(k)
    events = scoring_events(result)
    if spots and has_timeouts(result):
        _check_timeouts(possessions, game_type, other, err)
    if sequencing:
        _check_sequence(possessions, kick_list, kicks_after, game_type, other, err)

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
    elif sequencing:
        # Batch B8: the second-half kicker is the opening receiver, read from
        # the kicks themselves (a return touchdown on an opener changes who
        # possesses first, not who kicked).
        openers_by_half = {h: next((k for k in kick_list if k.get("half") == h and k.get("after_drive") is None
                                    and k.get("chain") == 1), None) for h in (1, 2)}
        if None in openers_by_half.values():
            err("missing_half_kickoff", "a half has no opening kick on the chain")
        elif openers_by_half[2]["kicking"] != openers_by_half[1]["receiving"]:
            err("wrong_second_half_receiver", "second half kicked off by %s, the opening kicker"
                % openers_by_half[2]["kicking"])
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
        if sequencing:
            continue  # batch B8: possession_sequence_break owns the alternation
        if a["half"] == b["half"] and a["team"] == b["team"]:
            err("clock_regression", "drive %s repeats the offense" % b["number"])

    fpm = base.field_position() if spots else None
    for p in possessions:
        category = p["category"]
        range_key = "clock" if category.startswith("end_of_") else category
        if _zero_play_expiry(p):
            pass  # kernel 2014.4: no 2012 drive is replayed, so no 2012 net range applies
        elif spots and p.get("segments"):
            # Kernel 2014.6 batch B9F: the replayed segments of a joined
            # possession, each against its own category and start.
            for seg in p["segments"]:
                if seg.get("end") != "replayed":
                    continue
                seg_key = _segment_key(seg)
                envelope = fpm.load()["envelopes"][seg_key][fpm.start_bin(seg["start"])]
                if envelope is None or (seg_key != "touchdown" and not envelope[0] <= seg["net"] <= envelope[1]):
                    err("drive_net_outside_2012_range", "drive %s segment net %s" % (p["number"], seg["net"]))
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
            # Batch B8: the last possession may be followed by a kick only
            # when that kick chain ended the game, a return touchdown in
            # overtime (rules.ot_history).
            chain_ended = (sequencing and p["half"] == "OT" and kicks_after.get(p["number"])
                           and (kick_score(kicks_after[p["number"]][-1]) is not None
                                or kicks_after[p["number"]][-1].get("outcome") in KEPT_OUTCOMES))
            if expired or (p is last and not chain_ended):
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
        if p["half"] == "OT" and category == "touchdown" and (p.get("xp_made") is not None or p.get("try")):
            err("xp_after_ot_walkoff", "drive %s" % p["number"])

    # Every score, drive and kick, in game order (scoring_events): the
    # identity holds against it, and a stored list is compared, never trusted.
    points = {t: 0 for t in teams}
    for event in events:
        if event["team"] in points:
            points[event["team"]] += event["points"]
    if teams and points != dict(result["final_score"]):
        err("score_identity_violations", "scored points %s vs final %s" % (points, result["final_score"]))
    if result.get("scoring_events") is not None and result["scoring_events"] != events:
        err("score_identity_violations", "stored scoring_events differ from the rebuild")
    for detail in return_touchdown_distance_errors(result):
        # Kernel 2014.6 batch B9 (R15; review round 2): a return touchdown
        # covers 1 to 109 yards.
        err("score_identity_violations", detail)
    for team, s in result.get("team_stats", {}).items():
        if "extra_points_made" in s:
            # Kernel 2014.6 batch B9 (R8): + 2 per two-point conversion (the
            # counter is absent from every earlier receipt, which reads 0).
            identity = (6 * s["touchdowns"] + s["extra_points_made"] + 2 * s.get("two_point_conversions", 0)
                        + 3 * s["field_goals"] + 2 * s["safeties"])
            if identity != result["final_score"].get(team):
                err("score_identity_violations", "%s team counters" % team)

    regulation_points = {t: 0 for t in teams}
    for event in events:
        if event["half"] in (1, 2) and event["team"] in regulation_points:
            regulation_points[event["team"]] += event["points"]
    tied = len(set(regulation_points.values())) == 1
    ot_kicks = [k for k in kick_list if k.get("half") == "OT"]
    overtime_played = bool(overtime or ot_kicks)
    if overtime_played and not tied:
        err("ot_end_inconsistent", "overtime played after a decided regulation")
    if tied and teams and not overtime_played:
        err("ot_end_inconsistent", "tied regulation without overtime")
    # The overtime history (rules.ot_history: possessions and, for the
    # sequencing cohort, kicks) must end exactly where the rule ends it.
    history = ot_history(overtime, ot_kicks)
    ot_expired = bool(overtime) and overtime[-1]["end_clock"] == 0
    for index, entry in enumerate(history):
        status = ot_status(history[:index + 1], game_type)
        final = index == len(history) - 1
        where = ("kick %s" % entry["kick"]) if entry.get("kick") is not None else (
            "drive %s" % overtime[sum(1 for e in history[:index + 1] if e.get("kick") is None) - 1]["number"])
        if status == "end" and not final:
            err("ot_end_inconsistent", "play continued after %s ended overtime" % where)
        if final and status != "end" and not (ot_expired and ot_status(history, game_type, expired=True) == "end"):
            err("ot_end_inconsistent", "overtime stopped before it ended at %s" % where)

    if spots:
        _check_spots(result, possessions, err, fpm)

    ledger = result.get("play_ledger")
    clock_legs = has_clock_legs(result)
    b9f_fourth = _GROUP_PREDICATES["b9f_fourth"](result)
    if _GROUP_PREDICATES["b10_ball"](result):
        # Kernel 2014.6 batch B10: the ball-security reconciliation (ledger
        # rows checked too when the full snap ledger is present).
        _check_ball_security(result, possessions, kicks_of(result), ledger, err)
    if not ledger:
        if clock_legs:
            _check_clock_legs(result, possessions, None, err, base.field_position())
        if b9f_fourth:
            _check_fourth_downs(possessions, None, err)
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
        if sequencing:
            # Batch B8: the second-half opener is kicked by the opening receiver.
            opening_receiver = kicks[0]["defense"] if kicks else None
            if not second or second[0]["offense"] != opening_receiver:
                err("missing_half_kickoff", "no second-half kickoff at Q3 15:00 by %s" % opening_receiver)
        elif not second or second[0]["defense"] != first_h2["team"]:
            err("missing_half_kickoff", "no second-half kickoff at Q3 15:00 to %s" % first_h2["team"])
    if overtime and not pro_bowl:
        openers.add(overtime[0]["number"])
    kicked_drives = set()
    if sequencing:
        # Batch B8: the kick rows are the kick records' rows, one each, in
        # order and agreeing on the hand-over (kick_chain_incoherent owns the
        # chain itself); a chain may put several kicks before one possession.
        if len(kicks) != len(kick_list):
            err("kick_chain_incoherent", "%d kick rows for %d kicks" % (len(kicks), len(kick_list)))
        for row, k in zip(kicks, kick_list):
            if (row["drive"], row["offense"], row["defense"]) != (k["drive"], k["kicking"], k["receiving"]) or (
                    row.get("next_start") != k.get("next_start")):
                err("kick_chain_incoherent", "kick %s row disagrees with its record" % k.get("kick_no"))
            if row.get("play_type") != ("free_kick" if k.get("free_kick") else "kickoff"):
                err("kick_chain_incoherent", "kick %s row kind" % k.get("kick_no"))
        kicked_drives = {k["drive"] for k in kicks}
    for k in ([] if sequencing else kicks):
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
                # Kernel 2014.6 batch B9 (R15): a turnover returned for a
                # touchdown carries touchdown and turnover both; its marker is
                # the turnover (the touchdown is the defense's).
                if row.get("touchdown") and not row.get("turnover"):
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
        tries = [r for r in rows if _own_try(r, p)]
        own_try = p.get("try")
        if category == "touchdown":
            if p.get("xp_made") is None and own_try is None and tries:
                err("xp_after_ot_walkoff" if p["half"] == "OT" else "duplicate_terminal",
                    "drive %s try without an attempt" % p["number"])
            if own_try is not None:
                # Kernel 2014.6 batch B9 (R8): one try row of the decided kind.
                kind = "extra_point" if own_try.get("decision") == "kick" else TWO_POINT_ROW
                if len(tries) != 1 or tries[0].get("play_type") != kind or tries[0].get("made") != own_try.get("made"):
                    err("score_identity_violations", "drive %s try row" % p["number"])
            elif p.get("xp_made") is not None and (len(tries) != 1 or tries[0].get("made") != p["xp_made"]):
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
    if sequencing:
        # Batch B8: a try anchored to a kick (a return touchdown's) reads
        # against that kick's record, never as a possession's try.
        by_kick = {k.get("kick_no"): k for k in kick_list}
        anchored = {}
        for number, rows in rows_by_drive.items():
            for r in rows:
                if r.get("play_type") in TRY_ROWS and r.get("anchor") and not _own_try(r, by_number.get(number)):
                    a = r["anchor"] or {}
                    anchored.setdefault(("kick", a["kick"]) if "kick" in a else ("drive", a.get("drive")), []).append(r)
        for (kind, key), rows in anchored.items():
            decided = None
            if kind == "kick":
                k = by_kick.get(key)
                score, made = (kick_score(k), kick_try_made(k)) if k is not None else (None, None)
                if k is not None and "xp_made" not in k and made is None and len(rows) == 1 and not rows[0].get("made"):
                    made = False  # a summary row reads 6 for a missed try as for no try
                decided = (k or {}).get("try")
            else:
                p = by_number.get(key)
                non_offensive = (p or {}).get("non_offensive_score") or {}
                score = (non_offensive["kind"], non_offensive.get("team")) if non_offensive.get("kind") else None
                made = non_offensive.get("xp_made")
                decided = non_offensive.get("try")
            if decided is not None:
                # Kernel 2014.6 batch B9 (R8): the try record decides the row.
                made = decided.get("made")
                if rows and rows[0].get("play_type") != ("extra_point" if decided.get("decision") == "kick"
                                                         else TWO_POINT_ROW):
                    err("score_identity_violations", "try anchored to %s %s is not its decided kind" % (kind, key))
            if score is None or len(rows) != 1 or rows[0].get("made") != made or rows[0].get("offense") != score[1]:
                err("score_identity_violations", "try anchored to %s %s" % (kind, key))
        for k in kick_list:
            has_try = k.get("try") is not None or kick_try_made(k) is not None
            if kick_score(k) is not None and has_try and len(anchored.get(("kick", k.get("kick_no")), ())) != 1:
                err("score_identity_violations", "kick %s touchdown without its try row" % k.get("kick_no"))
        for p in possessions:
            non_offensive = p.get("non_offensive_score") or {}
            if non_offensive.get("kind") == "touchdown" and (non_offensive.get("xp_made") is not None
                                                             or non_offensive.get("try") is not None) \
                    and len(anchored.get(("drive", p["number"]), ())) != 1:
                err("score_identity_violations", "drive %s defensive touchdown without its try row" % p["number"])
    if spots:
        _check_spot_ledger(result, possessions, rows_by_drive, kicks, err, sequencing)
    if has_chain_ledger(result):
        _check_chain_ledger(possessions, rows_by_drive, err)
    if has_chain_model(result):
        _check_layout_resamples(possessions, err, base.field_position())
    if clock_legs:
        _check_clock_legs(result, possessions, rows_by_drive, err, base.field_position())
    if _GROUP_PREDICATES["b6_ledger"](result) and not skipped >= set(B6_CLASSES):
        _check_b6_ledger(result, possessions, rows_by_drive, err, base.field_position())
    if b9f_fourth:
        _check_fourth_downs(possessions, rows_by_drive, err)
    return errors


def _own_try(row, p):
    """A try row that is a possession's own (an offensive touchdown's): an
    unanchored extra-point row (every kernel before 2014.6), or (batch B9)
    one anchored to that drive and naming its offense as the scorer."""
    if row.get("play_type") not in TRY_ROWS:
        return False
    anchor = row.get("anchor")
    if not anchor:
        return row.get("play_type") == "extra_point"
    return (p is not None and p.get("category") == "touchdown" and anchor.get("drive") == p.get("number")
            and row.get("scoring_team") == p.get("team"))


def _check_sequence(possessions, kicks, kicks_after, game_type, other, err):
    """Kernel 2014.6 batch B8 classes (zero tolerance).

    possession_sequence_break: inside a half, the next possessor follows from
    the event that ended the last possession: after a score, the club the
    kick chain handed the ball to (the receiving club, or the kicking club
    when it kept the ball; with no kick, in the Pro Bowl, the club that
    would have received: the club scored upon, or the scorer after a
    safety); after a kick-less transition, the defense, or the same offense
    after a punt it kept. A half's first possessor is the club its opening
    chain handed the ball to.

    kick_chain_incoherent: every kick sits on its chain: an opener (the
    first kick of its half, following no possession) or the kick after a
    scoring possession, kicked by the scorer (the club scored upon after a
    safety, as a free kick) in the same half and before the next possession;
    a later link follows a kick returned for a touchdown and is kicked by
    that scorer. A kick returned for a touchdown hands over nothing (exempt
    from the hand-over checks); every other kick is the last of its chain
    and hands the ball to the next possession: the receiving club (the
    kicking club when it kept the ball) at the kick's own start, with the
    matching start kind, and when the record carries its yards, by the
    identity of its frame (receiving: spot + kick - return + enforcement;
    touchback: 80 + enforcement; retained: 100 - (spot + kick - return) +
    enforcement)."""
    from .rules import kick_score, kicking_club, possession_score, RETAINED_START_KINDS
    by_number = {p["number"]: p for p in possessions}
    by_kick = {k.get("kick_no"): k for k in kicks}
    pro_bowl = game_type == PRO_BOWL

    def handed_to(kick):
        return kick["kicking"] if kick.get("outcome") in KEPT_OUTCOMES else kick["receiving"]

    # -- the alternation --------------------------------------------------------------------------
    for index, b in enumerate(possessions):
        a = possessions[index - 1] if index else None
        if pro_bowl and b["half"] in (1, 2) and b["start_clock"] in QUARTER_STARTS:
            continue  # the Pro Bowl alternation at each quarter is checked above
        if a is None or a["half"] != b["half"]:
            opener = [k for k in kicks if k.get("half") == b["half"] and k.get("after_drive") is None]
            if opener:
                last_kick = max(opener, key=lambda k: k.get("kick_no", 0))
                if kick_score(last_kick) is not None or b["team"] != handed_to(last_kick):
                    err("possession_sequence_break", "drive %s does not follow its half's opening chain"
                        % b["number"])
            continue
        score = possession_score(a, other.get(a["team"]))
        if score is not None:
            chain = kicks_after.get(a["number"], [])
            if chain:
                last_kick = chain[-1]
                if kick_score(last_kick) is not None:
                    err("possession_sequence_break", "drive %s follows a chain that ended on a touchdown" % b["number"])
                    continue
                expected = handed_to(last_kick)
            else:
                kicker = kicking_club(score[0], score[1], other.get(score[1]))
                expected = other.get(kicker)
            if b["team"] != expected:
                err("possession_sequence_break", "drive %s possessed by %s after %s's %s" % (
                    b["number"], b["team"], score[1], score[0]))
        else:
            if kicks_after.get(a["number"]):
                err("kick_chain_incoherent", "kick after non-scoring drive %s" % a["number"])
            expected = a["team"] if b.get("start_kind") == "punt_retained" else other.get(a["team"])
            if b["team"] != expected:
                err("possession_sequence_break", "drive %s possessed by %s after drive %s (%s)" % (
                    b["number"], b["team"], a["number"], a["category"]))
            if b.get("start_kind") in ("kickoff", "kickoff_touchback", "free_kick", "kickoff_retained",
                                        "free_kick_retained", "onside_recovery", "onside_lost") and not pro_bowl:
                err("possession_sequence_break", "drive %s starts from a kick after a non-scoring drive"
                    % b["number"])

    # -- the kick chains --------------------------------------------------------------------------
    for k in kicks:
        no, chain, n = k.get("kick_no"), k.get("chain"), k.get("drive")
        where = "kick %s" % no
        if chain == 1:
            if k.get("after_drive") is None:
                earlier = [j for j in kicks if j.get("half") == k.get("half") and j.get("kick_no", 0) < no]
                if earlier or k.get("free_kick"):
                    err("kick_chain_incoherent", "%s opens a half that already had a kick" % where)
                if n != (min((p["number"] for p in possessions if p["half"] == k.get("half")), default=n)):
                    err("kick_chain_incoherent", "%s opener precedes drive %s" % (where, n))
            else:
                p = by_number.get(k["after_drive"])
                score = possession_score(p, other.get(p["team"])) if p is not None else None
                if p is None or score is None or not p.get("kickoff_after"):
                    err("kick_chain_incoherent", "%s follows drive %s without a score" % (where, k.get("after_drive")))
                else:
                    kicker = kicking_club(score[0], score[1], other.get(score[1]))
                    if (k["kicking"], k["receiving"]) != (kicker, other.get(kicker)):
                        err("kick_chain_incoherent", "%s kicked by %s after %s's %s" % (
                            where, k["kicking"], score[1], score[0]))
                    if bool(k.get("free_kick")) != (score[0] == "safety"):
                        err("kick_chain_incoherent", "%s kind after a %s" % (where, score[0]))
                    if n != p["number"] + 1 or k.get("half") != p["half"]:
                        err("kick_chain_incoherent", "%s placed before drive %s, after drive %s" % (
                            where, n, p["number"]))
        else:
            prev = by_kick.get((no or 0) - 1)
            prev_score = kick_score(prev) if prev is not None else None
            if prev is None or prev_score is None or prev.get("drive") != n or prev.get("chain") != (chain or 0) - 1 \
                    or k["kicking"] != prev_score[1] or k.get("free_kick") or k.get("after_drive") != prev.get("after_drive"):
                err("kick_chain_incoherent", "%s is not the next link after kick %s" % (where, (no or 0) - 1))
        if kick_score(k) is not None:
            if k.get("next_start") is not None:
                err("kick_chain_incoherent", "%s returned for a touchdown publishes a next start" % where)
            continue
        following = by_kick.get((no or 0) + 1)
        if following is not None and following.get("drive") == n:
            err("kick_chain_incoherent", "%s is followed by another kick before drive %s" % (where, n))
        nxt = by_number.get(n)
        if nxt is None:
            if k.get("half") == "OT" and k.get("outcome") in KEPT_OUTCOMES and following is None:
                continue  # batch B9 (R9, rule R4): a kept overtime kick may end the game
            err("kick_chain_incoherent", "%s hands the ball to no possession" % where)
            continue
        if nxt["team"] != handed_to(k):
            err("kick_chain_incoherent", "%s handed the ball to %s, possessed by %s" % (where, handed_to(k), nxt["team"]))
        if nxt.get("start_spot") != k.get("next_start"):
            err("kick_chain_incoherent", "%s next start %s, drive %s starts at %s" % (
                where, k.get("next_start"), n, nxt.get("start_spot")))
        if nxt.get("start_kind") != expected_start_kind(k):
            err("kick_chain_incoherent", "%s start kind %s for %s" % (where, nxt.get("start_kind"), k.get("outcome")))
        if nxt.get("half") != k.get("half"):
            err("kick_chain_incoherent", "%s kicked in half %s before drive %s" % (where, k.get("half"), n))
        if "kick_yards" in k:
            spot = 20 if k.get("free_kick") else 35
            e = k.get("enforcement") or 0
            kick_yards, ret = k.get("kick_yards") or 0, k.get("return_yards") or 0
            if is_touchback(k):
                expected = 80 + e
            elif k.get("outcome") in KEPT_OUTCOMES:
                expected = 100 - (spot + kick_yards - ret) + e
            else:
                expected = spot + kick_yards - ret + e
            if k.get("next_start") != expected:
                err("kick_chain_incoherent", "%s identity: next %s, expected %s" % (where, k.get("next_start"), expected))


def audit_only_errors(result, base=None):
    """The audit-only class findings of one closed game (kernel 2014.6 batch
    B6), as 'class: detail' strings; empty for a result they do not measure."""
    return [e for e in check_ledger(result, base, audit_only=True) if e.split(":", 1)[0] in AUDIT_ONLY_CLASSES]


def _check_b6_ledger(result, possessions, rows_by_drive, err, fp):
    """Kernel 2014.6 batch B6 classes (audit-only until the sweep reads 0).

    field_goal_before_fourth_down (W3): a field-goal drive whose kick came on
    first, second or third down is coherent only when the drive ended its
    window, or in regulation the kick row's half clock is at most the base's
    EARLY_FG_SECONDS (a Pro Bowl quarter is its own window), or in overtime
    the made kick ended the game.
    kick_clock_shared (W5a): a punt or field-goal row stamped on the clock of
    the drive's last scrimmage snap.
    snap_at_zero (W5a): a scrimmage snap stamped 0:00.
    timeout_rows_mismatch (W5a): a drive's timeout rows per club differ from
    the possession's charged timeouts.
    two_minute_warning_missing (W5a): a period whose 2:00 the game's clock
    crossed has no warning row, or more than one."""
    from .statbook import kernel_at_least
    game_type = result.get("game_type", "regular")
    pro_bowl = game_type == PRO_BOWL
    overtime_spec = (("OT", _ot_bound(), _ot_length()) if game_type == "postseason" else "OT")
    early = getattr(fp, "EARLY_FG_SECONDS", None)
    last = possessions[-1]
    for p in possessions:
        number = p["number"]
        rows = rows_by_drive.get(number, [])
        scrim = [r for r in rows if r.get("play_type") in ("pass", "run")]
        kicks = [r for r in rows if r.get("play_type") in ("punt", "field_goal")]
        half_overtime = p["half"] == "OT"
        ot = overtime_spec if half_overtime else False
        if p["category"] == "field_goal_attempt" and early is not None:
            fd = p.get("fourth_down") or {}
            if fd.get("down") in (1, 2, 3) and not p.get("half_final"):
                ok = False
                if kicks:
                    period, text = kicks[0]["period"], kicks[0]["game_clock"]
                    minutes, seconds = (int(v) for v in text.split(":"))
                    left = minutes * 60 + seconds
                    if half_overtime:
                        ok = bool(p.get("fg_made")) and p is last
                    elif pro_bowl or period in (2, 4):
                        ok = left <= early
                if not ok:
                    err("field_goal_before_fourth_down", "drive %s kicked on down %s" % (number, fd.get("down")))
        for k in kicks:
            if scrim and (k["period"], k["game_clock"]) == (scrim[-1]["period"], scrim[-1]["game_clock"]):
                err("kick_clock_shared", "drive %s %s at %s %s" % (number, k["play_type"], k["period"], k["game_clock"]))
        for r in scrim:
            if r.get("game_clock") == "0:00":
                err("snap_at_zero", "drive %s snap %s" % (number, r.get("snap_in_drive")))
        timeouts = p.get("timeouts") or [0, 0, 0, 0]
        rows_to = [r for r in rows if r.get("play_type") == TIMEOUT_ROW]
        off_rows = sum(1 for r in rows_to if r.get("team") == p["team"])
        def_rows = len(rows_to) - off_rows
        if (off_rows, def_rows) != (timeouts[2], timeouts[3]):
            err("timeout_rows_mismatch", "drive %s rows %s/%s charged %s/%s" % (
                number, off_rows, def_rows, timeouts[2], timeouts[3]))
    # Two-minute warnings: one per crossed mark.
    ledger = result.get("play_ledger") or ()
    warnings = {}
    for r in ledger:
        if r.get("play_type") == TWO_MINUTE_WARNING_ROW:
            warnings[r.get("period")] = warnings.get(r.get("period"), 0) + 1
    crossed = set()
    for half_key, ot in ((1, False), (2, False), ("OT", overtime_spec)):
        mine = [p for p in possessions if p["half"] == half_key]
        if not mine:
            continue
        marks = two_minute_marks(ot, pro_bowl) if half_key == "OT" else [
            m for m in two_minute_marks(False, pro_bowl) if (m > 1800) == (half_key == 1)]
        for mark in marks:
            if any(p["start_clock"] > mark >= p["end_clock"] for p in mine):
                crossed.add(_period_clock(mark, overtime=ot)[0])
    for period in sorted(crossed, key=str):
        if warnings.get(period, 0) != 1:
            err("two_minute_warning_missing", "period %s has %d warning rows" % (period, warnings.get(period, 0)))
    for period in warnings:
        if period not in crossed:
            err("two_minute_warning_missing", "period %s warning without a crossing" % period)


def _ot_bound():
    from .rules import RULES
    return RULES.postseason_ot_period_bound


def _ot_length():
    from .rules import RULES
    return RULES.postseason_ot_seconds


def _check_layout_resamples(possessions, err, fp):
    """Kernel 2014.4 phase 2: a published layout resample names its pool, the
    original tuple's index and leading fields, and a final tuple of the same
    category at that index in the same pool, feasible at the drive's start
    spot; the resample count is a positive integer. `fp` is the
    field-position model of the result's own base."""
    units = []
    for p in possessions:
        if p.get("segments"):
            # Kernel 2014.6 batch B9F: each segment's own resample record,
            # against its drawn category, tuple snaps and start.
            for seg in p["segments"]:
                if seg.get("layout_resample"):
                    units.append(({"number": p["number"], "layout_resample": seg["layout_resample"],
                                   "category": seg["category"], "start_spot": seg["start"],
                                   "scrimmage_plays": seg["tuple_plays"]}))
        elif p.get("layout_resample"):
            units.append(p)
    for p in units:
        rec = p.get("layout_resample")
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
