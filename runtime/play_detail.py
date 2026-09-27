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


def _rng(seed, *, event_id, drive_no, offense):
    payload = json.dumps(
        ["public-snap-detail-v2", event_id, drive_no, offense],
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


def _period_clock(regulation_seconds_remaining):
    remaining = max(0, int(regulation_seconds_remaining))
    if remaining > 2700:
        period, in_period = 1, remaining - 2700
    elif remaining > 1800:
        period, in_period = 2, remaining - 1800
    elif remaining > 900:
        period, in_period = 3, remaining - 900
    else:
        period, in_period = 4, remaining
    return period, "%d:%02d" % (in_period // 60, in_period % 60)


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
    outcome,
    start_clock,
    end_clock,
    kick_return=False,
    punt_return=False,
    passer=None,
):
    """Allocate one resolved drive into reconciled player/snap public detail."""
    rng = _rng(seed, event_id=event_id, drive_no=drive_no, offense=team.team_id)
    shares = usage.load()["values"]
    completion_rate = load_calibration()["derived"]["completion_rate"]["value"]
    plays = max(1, int(plays))
    pass_plays = max(0, min(int(pass_plays), plays))
    sacks = max(0, min(int(sacks), pass_plays))

    indices = list(range(plays))
    rng.shuffle(indices)
    pass_slots = set(indices[:pass_plays])
    pass_slot_order = sorted(pass_slots)
    sack_slots = set(rng.sample(pass_slot_order, sacks)) if sacks else set()
    attempt_slots = [i for i in pass_slot_order if i not in sack_slots]
    run_slots = [i for i in range(plays) if i not in pass_slots]

    # One passer per club per game: the depth-chart QB1 unless the kernel
    # supplies a different game passer.
    qb = passer or usage.game_passer(available) or choose(rng, available, {"QB"}, "passer")
    qb_line = offense_stats["players"][qb.player_id]

    turnover_slot = None
    turnover_type = None
    if outcome == "turnover":
        interception_can_reconcile = len(attempt_slots) > 1 or not pass_yards
        if attempt_slots and (not run_slots or rng.random() < 0.8) and interception_can_reconcile:
            turnover_slot = rng.choice(attempt_slots)
            turnover_type = "interception"
        elif run_slots:
            turnover_slot = rng.choice(run_slots)
            turnover_type = "fumble"
        elif attempt_slots:
            turnover_slot = rng.choice(attempt_slots)
            turnover_type = "interception"

    completion_slots = []
    eligible_completions = [i for i in attempt_slots if i != turnover_slot]
    for index in eligible_completions:
        if rng.random() < completion_rate:
            completion_slots.append(index)
    if (pass_yards or outcome == "touchdown") and eligible_completions and not completion_slots:
        completion_slots.append(rng.choice(eligible_completions))
    if turnover_type == "interception" and turnover_slot in completion_slots:
        completion_slots.remove(turnover_slot)

    completion_yards = _allocate(pass_yards, len(completion_slots), rng)
    passing_by_slot = dict(zip(completion_slots, completion_yards))
    rushing_yards = _allocate_runs(rush_yards, len(run_slots), rng)
    rushing_by_slot = dict(zip(run_slots, rushing_yards))

    touchdown_slot = None
    touchdown_type = None
    if outcome == "touchdown":
        pass_td_slots = list(completion_slots)
        if pass_td_slots and (not run_slots or rng.random() < 0.58):
            touchdown_slot = pass_td_slots[-1]
            touchdown_type = "pass"
        elif run_slots:
            touchdown_slot = run_slots[-1]
            touchdown_type = "rush"
        elif pass_td_slots:
            touchdown_slot = pass_td_slots[-1]
            touchdown_type = "pass"

    drive_seconds = max(1, int(start_clock) - int(end_clock))
    ledger = []
    call_stats = {}

    for index in range(plays):
        snap_no = index + 1
        remaining = int(start_clock) - round(drive_seconds * snap_no / plays)
        period, game_clock = _period_clock(remaining)
        is_pass = index in pass_slots
        is_sack = index in sack_slots
        play_type = "pass" if is_pass else "run"
        call = _choose_call(rng, team, play_type)
        counter = _call_counter(call_stats, call)
        counter["snaps"] += 1

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

        if is_pass:
            counter["dropbacks"] += 1
            record["passer"] = qb.player_id
            _bump(qb_line, "dropbacks")
            if is_sack:
                loss = rng.randint(3, 10)
                record["sack"] = True
                record["result_yards"] = -loss
                counter["sacks"] += 1
                counter["yards"] -= loss
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
            else:
                receiver = usage.pick(rng, available, shares["target_share"], "target", role="receiver")
                rec_line = offense_stats["players"][receiver.player_id]
                record["target"] = receiver.player_id
                _bump(qb_line, "pass_attempts")
                _bump(rec_line, "targets")
                counter["pass_attempts"] += 1

                if turnover_type == "interception" and index == turnover_slot:
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
                elif index in completion_slots:
                    yards = passing_by_slot.get(index, 0)
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
                    if index == touchdown_slot and touchdown_type == "pass":
                        record["touchdown"] = True
                        _bump(qb_line, "passing_touchdowns")
                        _bump(rec_line, "receiving_touchdowns")
                        counter["touchdowns"] += 1
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
            yards = rushing_by_slot.get(index, 0)
            record["runner"] = runner.player_id
            record["rushing_yards"] = yards
            record["result_yards"] = yards
            _bump(run_line, "rushing_attempts")
            _bump(run_line, "rushing_yards", yards)
            _max(run_line, "long_rush", yards)
            counter["runs"] += 1
            counter["yards"] += yards

            if turnover_type == "fumble" and index == turnover_slot:
                _bump(run_line, "fumbles")
                _bump(run_line, "fumbles_lost")
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
            elif index == touchdown_slot and touchdown_type == "rush":
                record["touchdown"] = True
                _bump(run_line, "rushing_touchdowns")
                counter["touchdowns"] += 1
            else:
                _credit_tackle(rng, defenders, defense_stats, record, negative=yards < 0)

        ledger.append(record)

    terminal_snap = plays + 1
    period, game_clock = _period_clock(end_clock)

    if outcome == "field_goal":
        kicker = usage.kicking_specialist(available, "K", "placekicker") or choose(rng, available, {"K"}, "placekicker")
        line = offense_stats["players"][kicker.player_id]
        _bump(line, "field_goals_attempted")
        _bump(line, "field_goals_made")
        ledger.append({
            "drive": drive_no, "snap_in_drive": terminal_snap, "period": period,
            "game_clock": game_clock, "offense": team.team_id, "defense": defense.team_id,
            "play_type": "field_goal", "kicker": kicker.player_id, "made": True,
            "result_yards": 0, "touchdown": False, "turnover": False,
        })
    elif outcome == "punt":
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
        ledger.append({
            "drive": drive_no, "snap_in_drive": terminal_snap, "period": period,
            "game_clock": game_clock, "offense": team.team_id, "defense": defense.team_id,
            "play_type": "punt", "punter": punter.player_id, "cover_player": cover.player_id,
            "punt_yards": punt_yards, "returner": returner, "return_yards": return_yards,
            "result_yards": 0, "touchdown": False, "turnover": False,
        })

    if outcome == "touchdown":
        kicker = usage.kicking_specialist(available, "K", "placekicker") or choose(rng, available, {"K"}, "placekicker")
        line = offense_stats["players"][kicker.player_id]
        _bump(line, "extra_points_attempted")
        _bump(line, "extra_points_made")
        ledger.append({
            "drive": drive_no, "snap_in_drive": terminal_snap, "period": period,
            "game_clock": game_clock, "offense": team.team_id, "defense": defense.team_id,
            "play_type": "extra_point", "kicker": kicker.player_id, "made": True,
            "result_yards": 0, "touchdown": False, "turnover": False,
        })
        terminal_snap += 1

    if kick_return:
        returner = _returner(rng, defenders, "kick_return")
        return_yards = rng.randint(12, 36)
        rline = defense_stats["players"][returner.player_id]
        _bump(rline, "kick_returns")
        _bump(rline, "kick_return_yards", return_yards)
        _bump(rline, "return_yards", return_yards)
        ledger.append({
            "drive": drive_no, "snap_in_drive": terminal_snap, "period": period,
            "game_clock": game_clock, "offense": team.team_id, "defense": defense.team_id,
            "play_type": "kickoff", "returner": returner.player_id,
            "return_yards": return_yards, "result_yards": return_yards,
            "touchdown": False, "turnover": False,
        })

    return ledger, call_stats
