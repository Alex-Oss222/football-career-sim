"""Deterministic public snap-detail allocation for an already-resolved drive.

The possession kernel owns score/outcome generation. This module uses a
separate deterministic RNG stream to allocate that already-resolved drive into
public snap records, player statistics and named play-call usage. Because it
never consumes the possession RNG, requesting more detail cannot alter the
game result.
"""
from __future__ import annotations

import hashlib
import json
import random

from . import usage
from .calibration import load as load_calibration
from .player_evidence import choose

OFFENSIVE_LINE = {"OT", "OG", "C", "T", "G", "OL"}
SNAP_DETAIL_TAG = "public-snap-detail-v3"
KICKOFF_DETAIL_TAG = "public-kickoff-detail-v1"


def _rng(seed, *, event_id, drive_no, offense):
    payload = json.dumps(
        [SNAP_DETAIL_TAG, event_id, drive_no, offense],
        separators=(",", ":"),
    ).encode()
    digest = hashlib.sha256(seed + payload).digest()
    return random.Random(int.from_bytes(digest, "big"))


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


def _allocate_runs(total, count, rng):
    """Allocate drive rushing yards so some carries lose yardage.

    The sourced 2012 negative-run rate marks losing carries; their losses come
    from the sourced loss distribution and the remaining carries absorb the
    difference, so the drive total still reconciles exactly.
    """
    if count <= 1 or total < 0:
        return _allocate(total, count, rng)
    rate = usage.load()["values"]["negative_run_rate"]
    losing = [i for i in range(count) if rng.random() < rate]
    if len(losing) == count:
        losing = losing[:-1]
    losses = {i: usage.draw_loss(rng) for i in losing}
    gaining = [i for i in range(count) if i not in losses]
    shares = _allocate(int(total) + sum(losses.values()), len(gaining), rng)
    values = [0] * count
    for index, value in zip(gaining, shares):
        values[index] = value
    for index, loss in losses.items():
        values[index] = -loss
    return values


def _credit_tackle(rng, defenders, defense_stats, record, *, negative=False):
    """Credit a solo or assisted tackle using the sourced group shapes."""
    values = usage.load()["values"]
    shares = values["tfl_share"] if negative else values["tackle_share"]
    first = usage.pick(rng, defenders, shares, "defense", role="tackle")
    second = None
    if rng.random() < values["assisted_tackle_play_rate"]:
        try:
            second = usage.pick(
                rng, defenders, values["tackle_share"], "defense",
                role="tackle", exclude=(first,),
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
    """The coach-designated returner handles the return when one is listed."""
    designated = [p for p in players if role in p.roles or role in p.responsibilities]
    if designated:
        return min(
            enumerate(designated),
            key=lambda item: (item[1].depth if isinstance(item[1].depth, int) else 99, item[0]),
        )[1]
    return choose(rng, players, {"WR", "RB", "CB", "S"}, role)


def _normalize_call(raw, default_type):
    if isinstance(raw, str):
        return {
            "name": raw,
            "family": raw,
            "type": default_type,
            "personnel": None,
            "formation": None,
            "motion": None,
            "protection": None,
            "tags": (),
        }
    if isinstance(raw, dict):
        name = str(raw.get("name") or raw.get("concept") or raw.get("family") or default_type.title())
        return {
            "name": name,
            "family": str(raw.get("family") or raw.get("concept") or name),
            "type": str(raw.get("type") or default_type).lower(),
            "personnel": raw.get("personnel"),
            "formation": raw.get("formation"),
            "motion": raw.get("motion"),
            "protection": raw.get("protection"),
            "tags": tuple(raw.get("tags") or ()),
        }
    return _normalize_call(default_type.title(), default_type)


def canonical_call_sheet(team):
    """Return football-substance-only call metadata for outcome commitment.

    Display aliases and list order are intentionally excluded so rewording a
    call name cannot change the outcome draw. The current possession kernel does
    not yet use call-level matchup effects, but it still freezes the structural
    weekly menu for audit/replay purposes.
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
    rows.sort(key=lambda row: json.dumps(row, sort_keys=True, separators=(",", ":")))
    return rows


def _call_sheet(team, play_type):
    raw = tuple(getattr(team, "offensive_call_sheet", ()) or ())
    normalized = [_normalize_call(item, play_type) for item in raw]
    exact = [item for item in normalized if item["type"] in {play_type, "any", "mixed"}]
    return exact


def _choose_call(rng, team, play_type):
    calls = _call_sheet(team, play_type)
    if not calls:
        return _normalize_call("Generic Pass" if play_type == "pass" else "Generic Run", play_type)
    return rng.choice(calls)


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
    if overtime:
        # A postseason game can need more than one overtime period: "OT",
        # then "OT2", "OT3".
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


def _prefix_order(values, rng, low, high):
    """Order snap values so every running total stays inside [low, high].

    Keeps the snap-rng order when it already qualifies, otherwise takes the
    first qualifying snap at each step; falls back to losses first then gains
    ascending. Returns None when no order is found (a hard failure that
    check_ledger reports, never patched silently)."""
    order = list(range(len(values)))

    def ok(seq):
        total = 0
        for index in seq:
            total += values[index]
            if not low <= total <= high:
                return False
        return True

    if ok(order):
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
    if ok(fallback):
        return fallback
    return None


def _terminal_kind(rng, category, td_type, rushes, attempts, sacks):
    if category == "touchdown":
        return "catch" if td_type == "pass" else "run"
    if category == "interception":
        return "int"
    options = []
    if category == "fumble_lost":
        options = [(k, n) for k, n in (("run", rushes), ("catch", attempts), ("sack", sacks)) if n]
    elif category == "safety":
        options = [(k, n) for k, n in (("run", rushes), ("sack", sacks)) if n]
        if not options and attempts:
            options = [("att", attempts)]
    if not options:
        return None
    return rng.choices([k for k, _ in options], weights=[n for _, n in options], k=1)[0]


BASE_KIND = {"catch": "att", "int": "att", "att": "att", "run": "run", "sack": "sack"}


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
    plays,
    pass_plays,
    sacks,
    pass_yards,
    rush_yards,
    category,
    start_clock,
    end_clock,
    td_type=None,
    turnover_type=None,
    sack_losses=(),
    fg_made=None,
    fg_distance=None,
    xp_made=None,
    net_yards=0,
    overtime=False,
    punt_return=False,
    passer=None,
):
    """Allocate one resolved drive into reconciled player/snap public detail.

    Every number that changes the score, possession, clock or a team counter
    arrives from the kernel. This stream only decides who, in what order and
    how the already-fixed yardage splits across snaps. The terminal snap (the
    touchdown, the turnover, the fumble) is always the drive's last snap.
    """
    rng = _rng(seed, event_id=event_id, drive_no=drive_no, offense=team.team_id)
    shares = usage.load()["values"]
    completion_rate = load_calibration()["derived"]["completion_rate"]["value"]
    plays = max(0, int(plays))
    pass_plays = max(0, min(int(pass_plays), plays))
    sacks = max(0, min(int(sacks), pass_plays))
    losses = list(sack_losses)[:sacks]
    losses += [0] * (sacks - len(losses))
    rushes = plays - pass_plays
    attempts = pass_plays - sacks

    terminal = _terminal_kind(rng, category, td_type, rushes, attempts, sacks) if plays else None
    kinds = ["run"] * rushes + ["sack"] * sacks + ["att"] * attempts
    if terminal:
        kinds.remove(BASE_KIND[terminal])
    rng.shuffle(kinds)
    if terminal:
        kinds.append(terminal)

    completed = [k == "catch" or (k == "att" and rng.random() < completion_rate) for k in kinds]
    eligible = [i for i, k in enumerate(kinds) if k in ("att", "catch")]
    if pass_yards and eligible and not any(completed):
        completed[rng.choice(eligible)] = True
    completion_slots = [i for i, done in enumerate(completed) if done]
    run_slots = [i for i, k in enumerate(kinds) if k == "run"]
    sack_slots = [i for i, k in enumerate(kinds) if k == "sack"]

    values = [0] * plays
    for index, value in zip(completion_slots, _allocate(pass_yards, len(completion_slots), rng)):
        values[index] = value
    for index, value in zip(run_slots, _allocate_runs(rush_yards, len(run_slots), rng)):
        values[index] = value
    for index, loss in zip(sack_slots, losses):
        values[index] = -loss

    last = plays - 1
    net = int(net_yards)
    if category == "touchdown" and plays and values[last] < 1:
        same = completion_slots if kinds[last] == "catch" else run_slots
        candidates = [i for i in same if i != last and 1 <= values[i] <= 99] or [
            i for i in same if i != last and values[i] >= 1]
        if candidates:
            swap = rng.choice(candidates)
            values[last], values[swap] = values[swap], values[last]

    movable = list(range(last)) if terminal else list(range(plays))
    if category == "touchdown":
        low, high = max(-99, net - 99), net - 1
    else:
        low, high = -99, 99
    order = _prefix_order([values[i] for i in movable], rng, low, high)
    if order is not None:
        permutation = [movable[i] for i in order] + ([last] if terminal else [])
        kinds = [kinds[i] for i in permutation]
        completed = [completed[i] for i in permutation]
        values = [values[i] for i in permutation]

    # One passer per club per game: the depth-chart QB1 unless the kernel
    # supplies a different game passer.
    qb = passer or usage.game_passer(available) or choose(rng, available, {"QB"}, "passer")
    qb_line = offense_stats["players"][qb.player_id]

    drive_seconds = max(0, int(start_clock) - int(end_clock))
    ledger = []
    call_stats = {}

    def clock_at(remaining):
        return _period_clock(remaining, closing=remaining <= int(end_clock), overtime=overtime)

    def fumble(line, record, counter):
        _bump(line, "fumbles")
        _bump(line, "fumbles_lost")
        defender = usage.pick(rng, defenders, shares["tackle_share"], "defense", role="tackle")
        def_line = defense_stats["players"][defender.player_id]
        _bump(def_line, "forced_fumbles")
        _bump(def_line, "fumble_recoveries")
        _bump(def_line, "tackles")
        _bump(def_line, "solo_tackles")
        record["turnover"] = True
        record["turnover_type"] = "fumble"
        record["tackler"] = defender.player_id
        counter["turnovers"] += 1

    for index in range(plays):
        snap_no = index + 1
        remaining = int(start_clock) - round(drive_seconds * snap_no / plays)
        period, game_clock = clock_at(remaining)
        kind = kinds[index]
        is_terminal = terminal is not None and index == last
        is_pass = kind != "run"
        play_type = "pass" if is_pass else "run"
        call = _choose_call(rng, team, play_type)
        counter = _call_counter(call_stats, call)
        counter["snaps"] += 1
        yards = values[index]

        record = {
            "drive": drive_no,
            "snap_in_drive": snap_no,
            "period": period,
            "game_clock": game_clock,
            "offense": team.team_id,
            "defense": defense.team_id,
            "play_type": play_type,
            "concept": call["name"],
            "family": call["family"],
            "personnel": call["personnel"],
            "formation": call["formation"],
            "motion": call["motion"],
            "protection": call["protection"],
            "tags": list(call["tags"]),
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
        }

        if kind == "sack":
            loss = -yards
            counter["dropbacks"] += 1
            record["passer"] = qb.player_id
            _bump(qb_line, "dropbacks")
            record["sack"] = True
            record["result_yards"] = yards
            counter["sacks"] += 1
            counter["yards"] += yards
            _bump(qb_line, "sacks_taken")
            _bump(qb_line, "sack_yards", loss)
            blocker = choose(rng, available, OFFENSIVE_LINE, "pass_protection")
            rusher = usage.pick(rng, defenders, shares["sack_share"], "defense", role="pass_rush")
            _bump(offense_stats["players"][blocker.player_id], "sacks_allowed")
            record["blocker"] = blocker.player_id
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
                counter["turnovers"] += 1
        elif is_pass:
            counter["dropbacks"] += 1
            record["passer"] = qb.player_id
            _bump(qb_line, "dropbacks")
            receiver = usage.pick(rng, available, shares["target_share"], "target", role="receiver")
            rec_line = offense_stats["players"][receiver.player_id]
            record["target"] = receiver.player_id
            _bump(qb_line, "pass_attempts")
            _bump(rec_line, "targets")
            counter["pass_attempts"] += 1

            if kind == "int":
                _bump(qb_line, "interceptions")
                _bump(qb_line, "interceptions_thrown")
                defender = usage.pick(rng, defenders, shares["interception_share"], "defense", role="coverage")
                def_line = defense_stats["players"][defender.player_id]
                _bump(def_line, "defensive_interceptions")
                return_yards = rng.randint(0, 35)
                _bump(def_line, "interception_return_yards", return_yards)
                _bump(def_line, "passes_defended")
                record["turnover"] = True
                record["turnover_type"] = "interception"
                record["tackler"] = defender.player_id
                counter["turnovers"] += 1
            elif completed[index]:
                record["completion"] = True
                record["passing_yards"] = yards
                record["result_yards"] = yards
                _bump(qb_line, "completions")
                _bump(qb_line, "passing_yards", yards)
                _bump(rec_line, "receptions")
                _bump(rec_line, "receiving_yards", yards)
                _max(rec_line, "long_reception", yards)
                counter["completions"] += 1
                counter["yards"] += yards
                if is_terminal and category == "touchdown":
                    record["touchdown"] = True
                    _bump(qb_line, "passing_touchdowns")
                    _bump(rec_line, "receiving_touchdowns")
                    counter["touchdowns"] += 1
                elif is_terminal and category == "fumble_lost":
                    record["runner"] = None
                    fumble(rec_line, record, counter)
                else:
                    _credit_tackle(rng, defenders, defense_stats, record)
            else:
                if rng.random() < 0.35:
                    cover = usage.pick(rng, defenders, shares["pass_defensed_share"], "defense", role="coverage")
                    _bump(defense_stats["players"][cover.player_id], "passes_defended")
                    record["tackler"] = cover.player_id
                if rng.random() < 0.20:
                    pressure = usage.pick(rng, defenders, shares["sack_share"], "defense", role="pass_rush")
                    _bump(defense_stats["players"][pressure.player_id], "pressures")
        else:
            runner = usage.pick(
                rng, available, shares["rush_share"], "rush", role="rusher",
                only=lambda p: usage.group(p.position) != "QB" or p.player_id == qb.player_id,
            )
            run_line = offense_stats["players"][runner.player_id]
            record["runner"] = runner.player_id
            record["rushing_yards"] = yards
            record["result_yards"] = yards
            _bump(run_line, "rushing_attempts")
            _bump(run_line, "rushing_yards", yards)
            _max(run_line, "long_rush", yards)
            counter["runs"] += 1
            counter["yards"] += yards
            if is_terminal and category == "fumble_lost":
                fumble(run_line, record, counter)
            elif is_terminal and category == "touchdown":
                record["touchdown"] = True
                _bump(run_line, "rushing_touchdowns")
                counter["touchdowns"] += 1
            else:
                _credit_tackle(rng, defenders, defense_stats, record, negative=yards < 0)

        ledger.append(record)

    terminal_snap = plays + 1
    period, game_clock = _period_clock(end_clock, closing=True, overtime=overtime)
    base = {
        "drive": drive_no, "period": period, "game_clock": game_clock,
        "offense": team.team_id, "defense": defense.team_id,
        "result_yards": 0, "touchdown": False, "turnover": False,
    }

    def kicker_line():
        kicker = usage.kicking_specialist(available, "K", "placekicker") or choose(rng, available, {"K"}, "placekicker")
        return kicker, offense_stats["players"][kicker.player_id]

    if category == "field_goal_attempt":
        kicker, line = kicker_line()
        _bump(line, "field_goals_attempted")
        if fg_made:
            _bump(line, "field_goals_made")
        ledger.append({**base, "snap_in_drive": terminal_snap, "play_type": "field_goal",
                       "kicker": kicker.player_id, "made": bool(fg_made), "distance": fg_distance})
    elif category == "punt":
        punter = usage.kicking_specialist(available, "P", "punt") or choose(rng, available, {"P"}, "punt")
        line = offense_stats["players"][punter.player_id]
        punt_yards = rng.randint(32, 58)
        _bump(line, "punts")
        _bump(line, "punt_yards", punt_yards)
        _max(line, "long_punt", punt_yards)
        if rng.random() < 0.35:
            _bump(line, "punts_inside_20")
        cover = choose(rng, available, {"LB", "CB", "S", "WR", "RB", "TE"}, "punt_coverage")
        returner = None
        return_yards = 0
        if punt_return:
            returner = _returner(rng, defenders, "punt_return")
            return_yards = rng.randint(0, 22)
            rline = defense_stats["players"][returner.player_id]
            _bump(rline, "punt_returns")
            _bump(rline, "punt_return_yards", return_yards)
            _bump(rline, "return_yards", return_yards)
            returner = returner.player_id
        ledger.append({**base, "snap_in_drive": terminal_snap, "play_type": "punt",
                       "punter": punter.player_id, "cover_player": cover.player_id,
                       "punt_yards": punt_yards, "returner": returner, "return_yards": return_yards})
    elif category == "touchdown" and xp_made is not None:
        kicker, line = kicker_line()
        _bump(line, "extra_points_attempted")
        if xp_made:
            _bump(line, "extra_points_made")
        ledger.append({**base, "snap_in_drive": terminal_snap, "play_type": "extra_point",
                       "kicker": kicker.player_id, "made": bool(xp_made)})
    elif category == "safety":
        ledger.append({**base, "snap_in_drive": terminal_snap, "play_type": "safety",
                       "scoring_team": defense.team_id})
    elif category in POSSESSION_END_REASONS:
        ledger.append({**base, "snap_in_drive": terminal_snap, "play_type": "possession_end",
                       "reason": category})

    return ledger, call_stats


POSSESSION_END_REASONS = ("downs", "end_of_half", "end_of_game", "end_of_overtime")


def apply_kickoff_detail(*, seed, event_id, kick_no, kicking, receiving, rosters, stats,
                         returned, remaining, drive, free_kick=False, overtime=False):
    """Public row for one kickoff or post-safety free kick.

    The kernel has already drawn whether the kick was returned; this separate
    stream only names the kicker and returner and the descriptive return
    yardage, so it cannot change any score, clock or team counter."""
    payload = json.dumps([KICKOFF_DETAIL_TAG, event_id, kick_no], separators=(",", ":")).encode()
    rng = random.Random(int.from_bytes(hashlib.sha256(seed + payload).digest(), "big"))
    kicking_players = rosters[kicking.team_id]
    kicker = usage.kicking_specialist(kicking_players, "K", "placekicker") or choose(
        rng, kicking_players, {"K"}, "placekicker")
    period, game_clock = _period_clock(remaining, overtime=overtime)
    row = {
        "drive": drive, "snap_in_drive": 0, "period": period, "game_clock": game_clock,
        "offense": kicking.team_id, "defense": receiving.team_id,
        "play_type": "free_kick" if free_kick else "kickoff",
        "kicker": kicker.player_id, "touchback": not returned,
        "returner": None, "return_yards": 0, "result_yards": 0,
        "touchdown": False, "turnover": False,
    }
    if returned:
        returner = _returner(rng, rosters[receiving.team_id], "kick_return")
        return_yards = rng.randint(12, 36)
        line = stats[receiving.team_id]["players"][returner.player_id]
        _bump(line, "kick_returns")
        _bump(line, "kick_return_yards", return_yards)
        _bump(line, "return_yards", return_yards)
        row["returner"] = returner.player_id
        row["return_yards"] = return_yards
        row["result_yards"] = return_yards
    return [row]


# ---- ledger coherence ------------------------------------------------------

COHERENCE_CLASSES = (
    "snaps_after_terminal", "drives_missing_terminal", "duplicate_terminal",
    "drives_spanning_half", "wrong_second_half_receiver", "missing_half_kickoff",
    "kickoff_after_expired_clock", "xp_after_ot_walkoff", "td_snap_sack_or_nonpositive",
    "drive_net_outside_2012_range", "snap_sum_ne_drive_net", "prefix_out_of_bounds",
    "clock_regression", "score_identity_violations", "ot_end_inconsistent",
)
KICK_TYPES = ("kickoff", "free_kick")
MARKER_FOR = {
    "touchdown": "touchdown", "field_goal_attempt": "field_goal", "punt": "punt",
    "interception": "interception", "fumble_lost": "fumble", "safety": "safety",
    "downs": "possession_end", "end_of_half": "possession_end",
    "end_of_game": "possession_end", "end_of_overtime": "possession_end",
}
DRIVE_SUMMARY_FIELDS = (
    "number", "team", "half", "category", "points", "scrimmage_plays", "start_clock",
    "end_clock", "net_yards", "fg_distance", "fg_made", "xp_made", "kickoff_after",
    "half_final",
)


def drive_summary(possessions):
    """Compact per-possession list for receipts (ledger-free coherence audit)."""
    return [[p.get(field) for field in DRIVE_SUMMARY_FIELDS] for p in possessions]


def _possessions(result):
    if result.get("possessions") and "category" in result["possessions"][0]:
        return result["possessions"]
    return [dict(zip(DRIVE_SUMMARY_FIELDS, row)) for row in result.get("drives", ())]


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


def check_ledger(result):
    """Coherence errors for one closed 2013.6 game, as 'class: detail' strings.

    Runs the ledger-free checks on the possession list (or a receipt's compact
    'drives' summary) and, when a full snap ledger is present, the snap-level
    checks as well. An empty list means no violation was found."""
    from .rules import ot_status
    from . import drive_model

    errors = []

    def err(cls, detail):
        errors.append("%s: %s" % (cls, detail))

    possessions = _possessions(result)
    if not possessions:
        return errors
    game_type = result.get("game_type", "regular")
    teams = list(result.get("final_score", {}))
    other = {t: next((u for u in teams if u != t), None) for t in teams}
    regulation = [p for p in possessions if p["half"] in (1, 2)]
    overtime = [p for p in possessions if p["half"] == "OT"]
    last = possessions[-1]

    for p in regulation:
        if p["start_clock"] > 1800 > p["end_clock"]:
            err("drives_spanning_half", "drive %s" % p["number"])
    first_h2 = next((p for p in regulation if p["half"] == 2), None)
    if regulation and (first_h2 is None or first_h2["team"] == regulation[0]["team"]):
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
        if a["half"] == b["half"] and a["team"] == b["team"]:
            err("clock_regression", "drive %s repeats the offense" % b["number"])

    for p in possessions:
        category = p["category"]
        range_key = "clock" if category.startswith("end_of_") else category
        low, high = drive_model.net_range(range_key)
        if not low <= p["net_yards"] <= high:
            err("drive_net_outside_2012_range", "drive %s net %s" % (p["number"], p["net_yards"]))
        if p.get("kickoff_after"):
            expired = p["end_clock"] in ((1800, 0) if p["half"] in (1, 2) else (0,))
            if expired or p is last:
                err("kickoff_after_expired_clock", "drive %s" % p["number"])
        if p.get("half_final"):
            boundary = 1800 if p["half"] == 1 else 0
            nxt = possessions[possessions.index(p) + 1] if p is not last else None
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

    ledger = result.get("play_ledger")
    if not ledger:
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
    if not ledger or ledger[0].get("play_type") != "kickoff" or (
            ledger[0]["period"], ledger[0]["game_clock"]) != (1, "15:00"):
        err("missing_half_kickoff", "no opening kickoff at Q1 15:00")
    by_number = {p["number"]: p for p in possessions}
    openers = {regulation[0]["number"]} if regulation else set()
    if first_h2:
        openers.add(first_h2["number"])
        second = [k for k in kicks if k["drive"] == first_h2["number"]
                  and (k["period"], k["game_clock"]) == (3, "15:00")]
        if not second or second[0]["defense"] != first_h2["team"]:
            err("missing_half_kickoff", "no second-half kickoff at Q3 15:00 to %s" % first_h2["team"])
    if overtime:
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
        running = 0
        for position, value in enumerate(yards):
            running += value
            if abs(value) > 99 or not -99 <= running <= 99:
                err("prefix_out_of_bounds", "drive %s snap %s" % (p["number"], position + 1))
                break
            if category == "touchdown" and position < len(yards) - 1 and running >= p["net_yards"]:
                err("prefix_out_of_bounds", "drive %s reached the end zone before the touchdown" % p["number"])
                break
    return errors


def coherence_counts(errors):
    counts = {cls: 0 for cls in COHERENCE_CLASSES}
    for error in errors:
        cls = error.split(":", 1)[0]
        counts[cls] = counts.get(cls, 0) + 1
    return counts
