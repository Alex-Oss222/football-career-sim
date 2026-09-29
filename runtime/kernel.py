"""One protagonist-blind possession kernel for interactive and background games."""
from dataclasses import dataclass, asdict
import hashlib, json, math, random

from . import KERNEL_VERSION
from .calibration import load, validate
from .injuries import maybe_injury
from .rules import RULES, ot_status
from . import drive_model
from . import field_position
from . import usage
from .player_evidence import empty_player_stats, normalize_players, observation
from .play_detail import (
    apply_drive_detail, apply_kickoff_detail, canonical_call_sheet, check_ledger,
    _period_clock,
)


@dataclass(frozen=True)
class TeamInput:
    team_id: str
    active_players: tuple
    offense_anchor: float = 2.0
    defense_anchor: float = 2.0
    special_teams_anchor: float = 2.0
    scheme: str = "balanced"
    plan: str = "balanced"
    roster: tuple = ()
    personnel_packages: tuple = ()
    rotation_plan: tuple = ()
    # Public, week-specific offensive calls. Entries may be strings or dicts
    # with name/family/type/personnel/formation/motion/protection/tags.
    offensive_call_sheet: tuple = ()


def _rng(seed, packet):
    digest = hashlib.sha256(
        seed + json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()
    ).digest()
    return random.Random(int.from_bytes(digest, "big"))


def _merge_call_stats(target, source):
    for name, line in source.items():
        row = target.setdefault(
            name,
            {
                "family": line.get("family", name),
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
        for field in (
            "snaps", "runs", "dropbacks", "pass_attempts", "completions",
            "yards", "touchdowns", "turnovers", "sacks",
        ):
            row[field] += line.get(field, 0)


def _append_evidence(evidence, drive_ledger, offense_players, defense_players, outcome):
    offense_by_id = {p.player_id: p for p in offense_players}
    defense_by_id = {p.player_id: p for p in defense_players}

    for play in drive_ledger:
        if play.get("sack") and play.get("blocker"):
            # Kernel 2014.3: the lineman facing the rusher is named; which one
            # is an even draw, so no technique finding is asserted.
            blocker = offense_by_id.get(play["blocker"])
            if blocker:
                evidence.append(
                    observation(
                        blocker,
                        unit="offense",
                        role="pass protection",
                        responsibility="protect assigned gap/edge",
                        situation="generated passing down",
                        physical_execution="sacked from his side of the line",
                    )
                )
        if play.get("play_type") == "punt" and play.get("cover_player"):
            # Kernel 2014.3: named only when he made the tackle on a return.
            cover = offense_by_id.get(play["cover_player"])
            if cover:
                evidence.append(
                    observation(
                        cover,
                        unit="special teams",
                        role="punt coverage",
                        responsibility="maintain coverage lane and leverage",
                        situation="returned punt",
                        special_teams_responsibility="tackle made on the return",
                    )
                )
        if play.get("turnover"):
            if play.get("turnover_type") == "interception" and play.get("passer"):
                passer = offense_by_id.get(play["passer"])
                if passer:
                    evidence.append(
                        observation(
                            passer,
                            unit="offense",
                            role="passer",
                            responsibility="protect the football",
                            situation="turnover play",
                            processing="decision resulted in an interception",
                        )
                    )
            elif play.get("runner"):
                runner = offense_by_id.get(play["runner"])
                if runner:
                    evidence.append(
                        observation(
                            runner,
                            unit="offense",
                            role="ball carrier",
                            responsibility="secure the football",
                            situation="turnover play",
                            physical_execution="fumble lost",
                        )
                    )

    if outcome != "turnover":
        route = next((p for p in drive_ledger if p.get("target")), None)
        if route:
            receiver = offense_by_id.get(route["target"])
            if receiver:
                evidence.append(
                    observation(
                        receiver,
                        unit="offense",
                        role="route participant",
                        responsibility="execute assigned route",
                        situation=f"{outcome} drive",
                        assignment="assignment held",
                        observable_effort="sustained route responsibility through the rep",
                    )
                )


def _split_yards(total, weight_pass, weight_rush):
    """Split an integer total by weight with largest-remainder rounding."""
    denom = weight_pass + weight_rush
    exact_pass = total * weight_pass / denom
    exact_rush = total - exact_pass
    passing, rushing = math.floor(exact_pass), math.floor(exact_rush)
    leftover = total - passing - rushing
    if leftover:
        if exact_pass - passing >= exact_rush - rushing:
            passing += leftover
        else:
            rushing += leftover
    return passing, rushing


def _start_kind(kick_record):
    """How a possession began after a kick: free_kick, kickoff or kickoff_touchback."""
    if kick_record["free_kick"]:
        return "free_kick"
    return "kickoff_touchback" if kick_record["touchback"] else "kickoff"


def _edge(team, defense, home, venue="home"):
    # Kernel 2013.11: the designated home team gets the home term only at a
    # home venue; at a neutral site neither team does.
    return max(
        -0.06,
        min(
            0.06,
            (team.offense_anchor - defense.defense_anchor) * 0.025
            + (0.008 if team is home and venue != "neutral" else 0),
        ),
    )


def _blank_team_stats(players):
    return {
        "points": 0,
        "touchdowns": 0,
        "field_goals": 0,
        "punts": 0,
        "turnovers": 0,
        "sacks_allowed": 0,
        "penalties": 0,
        "penalty_yards": 0,
        "passing_yards": 0,
        "rushing_yards": 0,
        "first_downs": 0,
        "third_down_attempts": 0,
        "third_down_conversions": 0,
        "time_of_possession": 0,
        "kick_returns": 0,
        "punt_returns": 0,
        "field_goal_attempts": 0,
        "extra_point_attempts": 0,
        "extra_points_made": 0,
        "safeties": 0,
        "turnovers_on_downs": 0,
        "clock_expired_drives": 0,
        "kickoffs": 0,
        "drives": 0,
        "players": empty_player_stats(players),
    }


CLOCK_REASON = {1: "end_of_half", 2: "end_of_game", "OT": "end_of_overtime"}
# Kernel 2014.3 Pro Bowl (library/2013_super_bowl_mvp_and_pro_bowl_procedure.md
# section 3; branch readings in career/2013/pro_bowl/method.json): no kickoffs,
# the ball at the 25 to start every quarter and after every score, and a
# possession that ends when any quarter ends.
PRO_BOWL = "pro_bowl"
PRO_BOWL_SPOT = 75
QUARTER_REASON = {1: "end_of_quarter", 2: "end_of_half", 3: "end_of_quarter", 4: "end_of_game"}
SCORE_KIND = {"touchdown": "touchdown", "field_goal_attempt": "field_goal", "safety": "safety"}
LEGACY_OUTCOME = {
    "touchdown": "touchdown", "field_goal_attempt": "field_goal", "punt": "punt",
    "interception": "turnover", "fumble_lost": "turnover", "downs": "downs",
    "safety": "safety",
}


def resolve_game(
    home,
    away,
    *,
    seed,
    event_id,
    venue="home",
    weather="normal",
    game_type="regular",
    management_mode="autonomous",
    resume=None,
):
    if not isinstance(seed, bytes) or len(seed) < 32:
        raise ValueError("private seed required")

    home_players, away_players = normalize_players(home), normalize_players(away)
    if not home_players or not away_players:
        raise ValueError("active participants required")

    home_outcome = asdict(home)
    away_outcome = asdict(away)
    home_outcome["offensive_call_sheet"] = canonical_call_sheet(home)
    away_outcome["offensive_call_sheet"] = canonical_call_sheet(away)
    packet = {
        "event_id": event_id,
        "home": home_outcome,
        "away": away_outcome,
        "venue": venue,
        "weather": weather,
        "game_type": game_type,
    }
    rng = _rng(seed, packet)
    cal = load()
    assert not validate(cal)
    assert not usage.validate()
    drive_model.load()
    field_position.load()
    model = cal["model"]
    gross_per_attempt = cal["derived"]["gross_yards_per_pass_attempt"]
    yards_per_attempt = gross_per_attempt["numerator"] / gross_per_attempt["denominator"]
    carry = cal["derived"]["yards_per_carry"]
    yards_per_carry = carry["numerator"] / carry["denominator"]
    xp_rate = drive_model.rate("extra_point")
    T = field_position.T

    teams = {home.team_id: home, away.team_id: away}
    rosters = {home.team_id: home_players, away.team_id: away_players}
    stats = {t.team_id: _blank_team_stats(rosters[t.team_id]) for t in (home, away)}
    # Kernel 2014.3: the five linemen on the field start the game (credit only).
    for team_id, players in rosters.items():
        for lineman in usage.protection_front(players).values():
            stats[team_id]["players"][lineman.player_id]["line_starts"] += 1
    play_call_stats = {home.team_id: {}, away.team_id: {}}
    evidence = []
    possessions = []
    play_ledger = []
    kickoffs = []
    diagnostics = {"yard_split_count_fallback": 0, "td_split_fitted": 0, "interior_clock_redirected": 0,
                   "sack_losses_fitted": 0, "fallback_need_union": 0, "fallback_clock_tuple": 0,
                   "fallback_zero_tuple": 0, "h2_neutral_into_late": 0, "ot_leading_offense": 0,
                   "prefix_order_repaired": 0, "prefix_order_failed": 0,
                   # Kernel 2014.1: timeout-ladder levels and the end-of-half fit fallback.
                   "timeout_level_0": 0, "timeout_level_1": 0, "timeout_level_2": 0,
                   "timeout_level_3": 0, "h1_fit_fallback": 0, "timeout_tuple_widened": 0,
                   # Kernel 2014.4: no time-feasible first-half final for the
                   # window, a late/overtime fit drive, a zero-play clock
                   # expiry inside the allowance.
                   "h1_final_infeasible": 0, "fallback_fit_drive": 0, "clock_expiry_zero": 0}
    # Kernel 2014.1: charged timeouts left, per club; reset at each half and
    # at the start of overtime (and every two postseason overtime periods).
    timeouts = {home.team_id: RULES.timeouts_per_half, away.team_id: RULES.timeouts_per_half}
    # Legacy synthetic inputs without a QB keep one deterministic passer.
    passers = {tid: usage.game_passer(players) or players[0] for tid, players in rosters.items()}

    def other(team_id):
        return away.team_id if team_id == home.team_id else home.team_id

    ot_half = [0]

    def _reset_postseason_ot_timeouts(window):
        """Postseason overtime: periods 1-2, 3-4, ... are halves; each club
        gets three timeouts at the start of each such half (labelled
        inference, library/2013_nfl_playing_rules_for_simulation.md R6)."""
        total = RULES.postseason_ot_period_bound * RULES.postseason_ot_seconds
        elapsed = total - window
        half_index = int(elapsed // (2 * RULES.postseason_ot_seconds))
        if half_index != ot_half[0]:
            ot_half[0] = half_index
            for team_id in timeouts:
                timeouts[team_id] = RULES.postseason_ot_timeouts_per_half

    def append_rows(rows):
        for row in rows:
            row["sequence"] = len(play_ledger) + 1
            play_ledger.append(row)

    def kick(kicking, receiving, *, free_kick, half, remaining, ot_label="OT"):
        """One real 2012 kickoff (or safety free kick) record: one randrange."""
        kick_no = len(kickoffs) + 1
        drawn = field_position.free_kick(rng) if free_kick else field_position.kickoff(rng)
        returned = not drawn["touchback"]
        stats[kicking]["kickoffs"] += 1
        if returned:
            stats[receiving]["kick_returns"] += 1
        record = {
            "kick_no": kick_no, "kicking": kicking, "receiving": receiving,
            "returned": returned, "free_kick": free_kick, "half": half,
            "drive": len(possessions) + 1,
            "next_start": drawn["next_start"], "touchback": drawn["touchback"],
            "kick_yards": drawn["kick_yards"], "return_yards": drawn["return_yards"],
            "enforcement": drawn["enforcement"], "outcome": drawn["outcome"],
        }
        kickoffs.append(record)
        append_rows(apply_kickoff_detail(
            seed=seed, event_id=event_id, kick_no=kick_no,
            kicking=teams[kicking], receiving=teams[receiving], rosters=rosters,
            stats=stats, returned=returned, free_kick=free_kick,
            remaining=remaining, overtime=ot_label if half == "OT" else False, drive=record["drive"],
            record=record,
        ))
        return record

    def possess(offense, window, half, spot, start_kind, ot_history=None, ot_label="OT", quarter=None):
        team = teams[offense]
        # Pro Bowl quarters are their own windows: the first three draw as a
        # first-half window ending the possession, the fourth as the second
        # half's last fifteen minutes (runtime/README.md, kernel 2014.3).
        draw_half = half if quarter is None else (2 if quarter == 4 else 1)
        defense = teams[other(offense)]
        edge = _edge(team, defense, home, venue)
        drive_no = len(possessions) + 1
        score_diff = stats[offense]["points"] - stats[other(offense)]["points"]

        # 1-3. Game-state cell, category and a real 2012 drive feasible from
        # the start spot (runtime/field_position.py, possession stream).
        if half == "OT" and game_type == "postseason":
            _reset_postseason_ot_timeouts(window)
        timeouts_before = (timeouts[offense], timeouts[other(offense)])
        drawn = field_position.draw_drive(rng, spot, draw_half, window, score_diff, edge, diagnostics, timeouts_before)
        category, row, seconds = drawn.category, drawn.tuple, drawn.seconds
        # The real drive's charged timeouts, capped at what each club holds.
        timeouts_used = (min(timeouts_before[0], row[T["off_timeouts_used"]] or 0),
                         min(timeouts_before[1], row[T["def_timeouts_used"]] or 0))
        timeouts[offense] -= timeouts_used[0]
        timeouts[other(offense)] -= timeouts_used[1]
        half_final = drawn.consumes_window
        net, end_spot = field_position.adapt(category, row, spot)
        plays = int(row[T["plays"]])
        runs, attempts, sacks = int(row[T["runs"]]), int(row[T["attempts"]]), int(row[T["sacks"]])
        kneel_yards = list(row[T["kneel_yards"]])
        spikes = int(row[T["spikes"]])
        chains = list(row[T["chains"]])

        # 4. Real per-drive snap counts: the drive's own runs, attempts,
        # sacks, kneels and spikes, and its own scoring kind. No Bernoulli
        # decides a pass or a sack, so no sack is converted to an attempt.
        td_type = row[T["td_kind"]] if category == "touchdown" else None
        turnover_type = category if category in drive_model.TURNOVER_CATEGORIES else None
        free, kneel_sum, terminal_value, open_sacks = field_position.fixed_yardage(category, row)
        safety_terminal = None
        if category == "safety":
            safety_terminal = (row[T["safety_term_kind"]], terminal_value)

        # 5. Sack losses (possession stream). With no free snap, the sacks
        # carry the drive's yardage: their losses are fitted to the net.
        if free > 0:
            sack_losses = [rng.randint(3, 10) for _ in range(open_sacks)]
            if category == "touchdown" and free == 1 and sum(sack_losses) > 99 - spot:
                # Only fixed snaps precede the scoring snap: their losses must
                # keep the ball out of the own end zone.
                while sum(sack_losses) > 99 - spot:
                    big = max(range(len(sack_losses)), key=lambda i: (sack_losses[i], -i))
                    sack_losses[big] -= 1
                diagnostics["sack_losses_fitted"] += 1
        else:
            required = kneel_sum + terminal_value - net
            base, extra = divmod(required, open_sacks) if open_sacks else (0, 0)
            sack_losses = [base + (1 if i < extra else 0) for i in range(open_sacks)]
            if open_sacks:
                diagnostics["sack_losses_fitted"] += 1
        fixed_sum = kneel_sum - sum(sack_losses) + terminal_value
        free_total = net - fixed_sum

        # 6. Gross passing/rushing yardage over the free snaps.
        usable = attempts - (1 if category == "interception" else 0)
        free_runs = runs - (1 if safety_terminal and safety_terminal[0] == "run" else 0)
        weight_pass = max(0.0, rng.gauss(usable * yards_per_attempt, max(6, usable * 3))) if usable else 0.0
        weight_rush = max(0.0, rng.gauss(free_runs * yards_per_carry, max(4, free_runs * 2))) if free_runs else 0.0
        if usable + free_runs == 0:
            pass_yards = rush_free = 0
        elif not usable:
            pass_yards, rush_free = 0, free_total
        elif not free_runs:
            pass_yards, rush_free = free_total, 0
        else:
            if weight_pass + weight_rush <= 0:
                diagnostics["yard_split_count_fallback"] += 1
                weight_pass, weight_rush = usable, free_runs
            pass_yards, rush_free = _split_yards(free_total, weight_pass, weight_rush)
        if td_type == "pass" and pass_yards < 1 and free_runs:
            rush_free -= 1 - pass_yards
            pass_yards = 1
        elif td_type == "rush" and rush_free < 1 and usable:
            pass_yards -= 1 - rush_free
            rush_free = 1
        if td_type and usable and free_runs:
            # Feasibility, not calibration: the non-scoring kind's yards plus
            # the fixed snaps keep the ball in the field before the scoring
            # snap (running spot in [1, 99]); any excess moves to the scoring
            # kind, whose total then lies in [1, 99].
            before = rush_free if td_type == "pass" else pass_yards
            fitted = min(max(before, spot - 99 - fixed_sum), spot - 1 - fixed_sum)
            if fitted != before:
                diagnostics["td_split_fitted"] += 1
                if td_type == "pass":
                    rush_free, pass_yards = fitted, pass_yards + before - fitted
                else:
                    pass_yards, rush_free = fitted, rush_free + before - fitted
        rush_yards = rush_free + kneel_sum + (terminal_value if safety_terminal and safety_terminal[0] == "run" else 0)
        sack_total = sum(sack_losses) + (-terminal_value if safety_terminal and safety_terminal[0] == "sack" else 0)

        s = stats[offense]
        d = stats[defense.team_id]
        s["passing_yards"] += pass_yards
        s["rushing_yards"] += rush_yards
        s["sacks_allowed"] += sacks

        # 7. Penalties (counters only) and the drive's real chains.
        pens = sum(rng.random() < model["penalty_per_play"] for _ in range(plays))
        s["penalties"] += pens
        s["penalty_yards"] += pens * rng.randint(5, 10) if pens else 0
        s["first_downs"] += chains[0] + chains[1]
        s["third_down_attempts"] += chains[2]
        s["third_down_conversions"] += chains[3]

        # 8. Terminal scoring, then the transition to the next possession.
        points = 0
        score_kind = None
        xp_made = None
        fg_made = None
        fg_distance = None
        next_start = None
        next_kind = None
        punt_record = None
        turnover_record = None
        if category == "touchdown":
            points = 6
            s["touchdowns"] += 1
            score_kind = "touchdown"
            walk_off = ot_history is not None and ot_status(
                ot_history + [{"team": offense, "score": "touchdown"}], game_type) == "end"
            if not walk_off:
                s["extra_point_attempts"] += 1
                xp_made = rng.random() < xp_rate
                if xp_made:
                    points += 1
                    s["extra_points_made"] += 1
        elif category == "field_goal_attempt":
            s["field_goal_attempts"] += 1
            fg_distance = int(row[T["fg_distance"]])
            fg_made = rng.random() < drive_model.fg_make_prob(fg_distance)
            if fg_made:
                points = 3
                s["field_goals"] += 1
                score_kind = "field_goal"
            else:
                next_start, next_kind = field_position.missed_fg_start(fg_distance), "missed_fg"
        elif category == "punt":
            s["punts"] += 1
            punt_record = field_position.punt(rng, end_spot)
            d["punt_returns"] += int(punt_record["outcome"] == "returned")
            next_start, next_kind = punt_record["next_start"], "punt"
        elif category in drive_model.TURNOVER_CATEGORIES:
            s["turnovers"] += 1
            turnover_record = field_position.turnover(rng, category, end_spot)
            next_start, next_kind = turnover_record["next_start"], category
        elif category == "downs":
            s["turnovers_on_downs"] += 1
            next_start, next_kind = field_position.downs_start(end_spot), "downs"
        elif category == "safety":
            d["points"] += 2
            d["safeties"] += 1
            score_kind = "safety"
        elif category == "clock":
            s["clock_expired_drives"] += 1
        s["drives"] += 1
        s["points"] += points
        s["time_of_possession"] += seconds

        terminal = category
        if category == "clock":
            terminal = QUARTER_REASON[quarter] if quarter else CLOCK_REASON[half]
        if half == "OT":
            start_clock, end_clock = window, window - seconds
        else:
            base = (4 - quarter) * RULES.quarter_seconds if quarter else (1800 if half == 1 else 0)
            start_clock, end_clock = base + window, base + window - seconds

        fourth_down = None
        if category in field_position.FOURTH_DOWN_CATEGORIES:
            clock_s = window - seconds
            ydstogo = row[T["term_ydstogo"]]
            fourth_down = {
                # Kernel 2014.1: goal to go when the real distance is at least the
                # distance to the goal line at the replayed spot.
                "down": row[T["term_down"]],
                "ydstogo": min(ydstogo, end_spot) if ydstogo is not None else None,
                "goal_to_go": ydstogo is not None and ydstogo >= end_spot,
                "los": end_spot,
                "clock_s": clock_s, "clock_bucket": field_position.terminal_bucket(clock_s) if draw_half == 2 else None,
                "half": draw_half, "score_diff": score_diff, "need": field_position.need(score_diff),
                "decision_zone": field_position.decision_zone(end_spot), "cell": drawn.cell,
                "tuple_terminal_bucket": row[T["term_bucket"]],
                "action": {"punt": "punt", "field_goal_attempt": "field_goal", "downs": "go"}[category],
            }

        drive_ledger, drive_calls = apply_drive_detail(
            seed=seed,
            event_id=event_id,
            drive_no=drive_no,
            team=team,
            defense=defense,
            available=rosters[offense],
            defenders=rosters[defense.team_id],
            offense_stats=s,
            defense_stats=d,
            runs=runs,
            attempts=attempts,
            sacks=sacks,
            kneel_yards=kneel_yards,
            spikes=spikes,
            pass_yards=pass_yards,
            rush_free=rush_free,
            category=terminal,
            td_type=td_type,
            turnover_type=turnover_type,
            sack_losses=sack_losses,
            safety_terminal=safety_terminal,
            fg_made=fg_made,
            fg_distance=fg_distance,
            xp_made=xp_made,
            net_yards=net,
            start_spot=spot,
            start_clock=start_clock,
            end_clock=end_clock,
            own_seconds=drawn.own_seconds,
            overtime=ot_label if half == "OT" else False,
            punt_record=punt_record,
            turnover_record=turnover_record,
            fourth_down=fourth_down,
            passer=passers[offense],
            diagnostics=diagnostics,
        )
        append_rows(drive_ledger)
        _merge_call_stats(play_call_stats[offense], drive_calls)
        _append_evidence(
            evidence,
            drive_ledger,
            rosters[offense],
            rosters[defense.team_id],
            "turnover" if turnover_type else LEGACY_OUTCOME.get(category, "other"),
        )

        record = {
            "number": drive_no,
            "team": offense,
            "half": half,
            "start_clock": start_clock,
            "end_clock": end_clock,
            "seconds": seconds,
            "scrimmage_plays": plays,
            "outcome": LEGACY_OUTCOME.get(category, terminal),
            "category": terminal,
            "points": points,
            "td_type": td_type,
            "turnover_type": turnover_type,
            "net_yards": net,
            "sack_loss_total": sack_total,
            "fg_distance": fg_distance,
            "fg_made": fg_made,
            "xp_made": xp_made,
            "half_final": half_final,
            "kickoff_after": None,
            # Kernel 2013.7 field position (append-only).
            "start_spot": spot,
            "start_kind": start_kind,
            "end_spot": end_spot,
            "next_start": next_start,
            "score_diff": score_diff,
            "cell": drawn.cell,
            "tuple_terminal_bucket": row[T["term_bucket"]],
            "chains": chains,
            "fourth_down": fourth_down,
            "kneels": len(kneel_yards),
            "spikes": spikes,
            # Kernel 2014.1 (append-only): [offense before, defence before,
            # offense used, defence used] and the timeout-ladder level.
            "timeouts": [timeouts_before[0], timeouts_before[1], timeouts_used[0], timeouts_used[1]],
            "timeout_level": drawn.timeout_level,
            # Kernel 2014.4 (append-only): the drive's own scaled seconds and
            # the clock-expiry leg after its last snap (seconds = own +
            # expiry; expiry is 0 unless the drive ends its window).
            "own_seconds": drawn.own_seconds,
            "expiry_seconds": drawn.expiry_seconds,
        }
        if half == "OT":
            record["period"] = _period_clock(start_clock, overtime=ot_label)[0]
        if quarter:
            record["quarter"] = quarter
        possessions.append(record)
        return record, score_kind, next_kind

    def kicked_after(record, score_kind, window, half, ot_label="OT"):
        remaining = window + (1800 if half == 1 else 0)
        kicked = kick(record["team"], other(record["team"]), free_kick=score_kind == "safety",
                      half=half, remaining=remaining, ot_label=ot_label)
        record["kickoff_after"] = {"returned": kicked["returned"], "free_kick": kicked["free_kick"],
                                   "next_start": kicked["next_start"], "touchback": kicked["touchback"],
                                   "enforcement": kicked["enforcement"]}
        record["next_start"] = kicked["next_start"]
        return kicked["next_start"], _start_kind(kicked)

    def placed(record):
        """Pro Bowl: the next possession starts at the 25 (no kickoff)."""
        record["next_start"] = PRO_BOWL_SPOT
        return PRO_BOWL_SPOT, "placement"

    # Regulation: two clock-bounded halves; a possession never crosses one.
    opening_receiver = away.team_id if rng.random() < 0.5 else home.team_id
    pro_bowl = game_type == PRO_BOWL
    for quarter in ((1, 2, 3, 4) if pro_bowl else ()):
        # Possession alternates at the start of each quarter from the
        # opening coin toss; timeouts reset at each half.
        half = 1 if quarter <= 2 else 2
        offense = opening_receiver if quarter in (1, 3) else other(opening_receiver)
        window = RULES.quarter_seconds
        if quarter in (1, 3):
            for team_id in timeouts:
                timeouts[team_id] = RULES.timeouts_per_half
        spot, start_kind = PRO_BOWL_SPOT, "placement"
        while window > 0:
            record, score_kind, next_kind = possess(offense, window, half, spot, start_kind, quarter=quarter)
            window -= record["seconds"]
            if score_kind and window > 0:
                spot, start_kind = placed(record)
            else:
                spot, start_kind = record["next_start"], next_kind
            offense = other(offense)
    for half in (() if pro_bowl else (1, 2)):
        offense = opening_receiver if half == 1 else other(opening_receiver)
        window = RULES.quarter_seconds * 2
        for team_id in timeouts:
            timeouts[team_id] = RULES.timeouts_per_half
        opened = kick(other(offense), offense, free_kick=False, half=half,
                      remaining=window + (1800 if half == 1 else 0))
        spot, start_kind = opened["next_start"], _start_kind(opened)
        while window > 0:
            record, score_kind, next_kind = possess(offense, window, half, spot, start_kind)
            window -= record["seconds"]
            if score_kind and window > 0:
                spot, start_kind = kicked_after(record, score_kind, window, half)
            else:
                spot, start_kind = record["next_start"], next_kind
            offense = other(offense)

    total = RULES.quarter_seconds * 4
    overtime_seconds = 0
    if stats[home.team_id]["points"] == stats[away.team_id]["points"]:
        # Kernel 2013.8 overtime (library/2013_nfl_playing_rules_for_simulation.md).
        # A new coin toss decides the receiver; possessions alternate on a
        # real clock, each drive using its own seconds; modified sudden death
        # (runtime.rules.ot_status) decides when a score ends the game.
        # Regular season and preseason: one 15-minute period; when it expires
        # the game ends, tied if still level. Postseason: 15-minute periods
        # laid on one continuous countdown, so a possession carries across a
        # period break and the game never ends tied.
        offense = home.team_id if rng.random() < 0.5 else away.team_id
        postseason = game_type == "postseason"
        if postseason:
            periods = RULES.postseason_ot_period_bound
            ot_label = ("OT", periods, RULES.postseason_ot_seconds)
            window = periods * RULES.postseason_ot_seconds
        else:
            ot_label = "OT"
            window = RULES.regular_ot_seconds
        history = []
        for team_id in timeouts:
            timeouts[team_id] = (RULES.postseason_ot_timeouts_per_half if postseason
                                 else RULES.regular_ot_timeouts)
        ot_half[0] = 0
        if pro_bowl:
            spot, start_kind = PRO_BOWL_SPOT, "placement"
        else:
            opened = kick(other(offense), offense, free_kick=False, half="OT", remaining=window, ot_label=ot_label)
            spot, start_kind = opened["next_start"], _start_kind(opened)
        while True:
            record, score_kind, next_kind = possess(offense, window, "OT", spot, start_kind, history, ot_label)
            window -= record["seconds"]
            overtime_seconds += record["seconds"]
            history.append({"team": offense, "score": score_kind})
            if ot_status(history, game_type) == "end":
                break
            if window <= 0:
                if ot_status(history, game_type, expired=True) == "end":
                    break
                raise RuntimeError("postseason overtime exceeded the engine's %d-period bound"
                                   % RULES.postseason_ot_period_bound)
            if score_kind:
                spot, start_kind = (placed(record) if pro_bowl
                                    else kicked_after(record, score_kind, window, "OT", ot_label))
            else:
                spot, start_kind = record["next_start"], next_kind
            offense = other(offense)
        total += overtime_seconds

    injuries = []
    for team in (home, away):
        for p in rosters[team.team_id]:
            injury = maybe_injury(rng, p.position, 20, "game")
            if injury:
                injuries.append({"team": team.team_id, "player": p.player_id, **asdict(injury)})

    pauses = []
    if management_mode == "user_controlled" and not resume:
        pauses.append(
            {
                "trigger": "material_hc_decision",
                "continuation_token": hashlib.sha256((event_id + ":pause").encode()).hexdigest(),
            }
        )

    return {
        "kernel_version": KERNEL_VERSION,
        "event_id": event_id,
        "game_type": game_type,
        "opening_receiver": opening_receiver,
        "final_score": {k: v["points"] for k, v in stats.items()},
        "possessions": possessions,
        "kickoffs": kickoffs,
        "play_ledger": play_ledger,
        "play_call_stats": play_call_stats,
        "team_stats": stats,
        "player_evidence": evidence,
        "injuries": injuries,
        "pauses": pauses,
        "diagnostics": diagnostics,
        "terminated": True,
    }


def validate_result(result):
    errors = []
    first_team = next(iter(result["team_stats"].values()), {})
    current = "extra_points_made" in first_team

    for team, score in result["final_score"].items():
        s = result["team_stats"][team]
        players = s["players"]

        if current:
            expected = (
                6 * s["touchdowns"] + s["extra_points_made"]
                + 3 * s["field_goals"] + 2 * s["safeties"]
            )
        else:
            # Legacy 2013.4/2013.5 results: every touchdown carried seven.
            expected = s["touchdowns"] * 7 + s["field_goals"] * 3
        if score != expected or s["points"] != score:
            errors.append("score ledger mismatch")
        if sum(p["passing_yards"] for p in players.values()) != s["passing_yards"]:
            errors.append("passing yardage mismatch")
        if sum(p["rushing_yards"] for p in players.values()) != s["rushing_yards"]:
            errors.append("rushing yardage mismatch")
        if sum(p["receiving_yards"] for p in players.values()) != s["passing_yards"]:
            errors.append("receiving yardage mismatch")
        if sum(p["sacks_allowed"] for p in players.values()) != s["sacks_allowed"]:
            errors.append("sack attribution mismatch")
        if sum(p["receptions"] for p in players.values()) != sum(p["completions"] for p in players.values()):
            errors.append("reception/completion mismatch")
        if sum(p["pass_attempts"] > 0 for p in players.values()) > 1:
            errors.append("more than one passer without a game-passer change")
        if any(p["tackles"] != p["solo_tackles"] + p["assisted_tackles"] for p in players.values()):
            errors.append("tackle credit mismatch")
        opponent = next(t for t in result["team_stats"] if t != team)
        if sum(p["sacks"] for p in result["team_stats"][opponent]["players"].values()) != s["sacks_allowed"]:
            errors.append("defensive sack credit mismatch")
        if current and all("line_starts" in p for p in players.values()):
            # Kernel 2014.3 credit checks (legacy inputs without linemen or a
            # long snapper keep the old fallbacks).
            linemen = sum(usage.group(p["position"]) == "OL" for p in players.values())
            snapper = linemen or any(p["position"] == "LS" for p in players.values())
            if sum(p["line_starts"] for p in players.values()) != min(5, linemen):
                errors.append("line start count mismatch")
            if linemen and any(p["sacks_allowed"] and not p["line_starts"] for p in players.values()):
                errors.append("sack charged to a lineman off the field")
            kicks = [row for row in result.get("play_ledger", [])
                     if row.get("offense") == team and row.get("play_type") in ("kickoff", "free_kick", "punt")]
            if sum(p["special_teams_tackles"] for p in players.values()) != sum(
                    1 for row in kicks if row.get("cover_player")):
                errors.append("coverage tackle count mismatch")
            if any(row.get("outcome") == "returned" and not row.get("cover_player") for row in kicks):
                errors.append("returned kick without a coverage tackler")
            if any(row.get("cover_player") and row.get("outcome") != "returned" for row in kicks):
                errors.append("coverage tackle on a kick that was not returned")
            for pid, line in players.items():
                if line["special_teams_tackles"] != sum(1 for row in kicks if row.get("cover_player") == pid):
                    errors.append("coverage tackle credit differs from the ledger")
                    break
            snaps = s["punts"] + s["field_goal_attempts"] + s["extra_point_attempts"]
            if snapper and sum(p["long_snaps"] for p in players.values()) != snaps:
                errors.append("long snap count mismatch")
        if (
            sum(p["interceptions_thrown"] + p["fumbles_lost"] for p in players.values())
            != s["turnovers"]
        ):
            errors.append("turnover attribution mismatch")
        if (
            sum(p["passing_touchdowns"] + p["rushing_touchdowns"] for p in players.values())
            != s["touchdowns"]
        ):
            errors.append("touchdown attribution mismatch")
        if current:
            if s["field_goals"] > s["field_goal_attempts"]:
                errors.append("field goals made exceed attempts")
            if not s["extra_points_made"] <= s["extra_point_attempts"] <= s["touchdowns"]:
                errors.append("extra-point counts inconsistent")
            if sum(p["field_goals_made"] for p in players.values()) != s["field_goals"]:
                errors.append("field-goal made attribution mismatch")
            if sum(p["field_goals_attempted"] for p in players.values()) != s["field_goal_attempts"]:
                errors.append("field-goal attempt attribution mismatch")
            if sum(p["extra_points_made"] for p in players.values()) != s["extra_points_made"]:
                errors.append("extra-point made attribution mismatch")
            if sum(p["extra_points_attempted"] for p in players.values()) != s["extra_point_attempts"]:
                errors.append("extra-point attempt attribution mismatch")

    possessions = result["possessions"]
    elapsed = sum(p["seconds"] for p in possessions)
    if sum(s["time_of_possession"] for s in result["team_stats"].values()) != elapsed:
        errors.append("clock mismatch")
    if any(
        p["end_clock"] < 0 or p["start_clock"] < p["end_clock"]
        for p in possessions
    ):
        errors.append("invalid clock")

    scrimmage_expected = sum(p.get("scrimmage_plays", 0) for p in possessions)
    scrimmage_actual = sum(
        play.get("play_type") in {"pass", "run"} for play in result.get("play_ledger", [])
    )
    if scrimmage_actual != scrimmage_expected:
        errors.append("snap ledger mismatch")

    if any(
        play.get("sequence") != index
        for index, play in enumerate(result.get("play_ledger", []), 1)
    ):
        errors.append("play sequence mismatch")

    if not current:
        return errors

    regulation = [p for p in possessions if p.get("half") in (1, 2)]
    overtime = [p for p in possessions if p.get("half") == "OT"]
    for half in (1, 2):
        if sum(p["seconds"] for p in regulation if p["half"] == half) != RULES.quarter_seconds * 2:
            errors.append(f"half {half} possession seconds do not total 1800")
    period = (
        RULES.postseason_ot_seconds if result.get("game_type") == "postseason" else RULES.regular_ot_seconds
    )
    if result.get("game_type") != "postseason" and sum(p["seconds"] for p in overtime) > period:
        errors.append("overtime elapsed exceeds the period")
    if any(p["start_clock"] > 1800 > p["end_clock"] for p in regulation):
        errors.append("possession spans halftime")
    opening = regulation[0]["team"] if regulation else None
    second = next((p for p in regulation if p["half"] == 2), None)
    pro_bowl = result.get("game_type") == PRO_BOWL
    if pro_bowl:
        openers = [next((p for p in regulation if p.get("quarter") == q), None) for q in (1, 2, 3, 4)]
        if any(p is None or p["start_spot"] != PRO_BOWL_SPOT for p in openers) or not (
                openers[0]["team"] == openers[2]["team"] != openers[1]["team"] == openers[3]["team"]):
            errors.append("pro bowl quarter possession mismatch")
        if any(p["start_clock"] > b > p["end_clock"] for p in regulation for b in (2700, 900)):
            errors.append("possession spans a quarter")
    elif second is None or second["team"] == opening:
        errors.append("second half opened by the opening receiver")
    kicks = result.get("kickoffs", [])
    expected_kicks = 0 if pro_bowl else 2 + (1 if overtime else 0) + sum(1 for p in possessions if p.get("kickoff_after"))
    if len(kicks) != expected_kicks:
        errors.append("kickoff count mismatch")
    for team, s in result["team_stats"].items():
        if s["kickoffs"] != sum(1 for k in kicks if k["kicking"] == team):
            errors.append("kickoff counter mismatch")
        if s["kick_returns"] != sum(1 for k in kicks if k["receiving"] == team and k["returned"]):
            errors.append("kick return counter mismatch")
        if s["drives"] != sum(1 for p in possessions if p["team"] == team):
            errors.append("drive counter mismatch")
    if possessions and all(p.get("start_spot") is not None for p in possessions):
        # Kernel 2013.7: the chain counters are the real drives' own counts.
        for team, s in result["team_stats"].items():
            mine = [p["chains"] for p in possessions if p["team"] == team]
            if (s["first_downs"] != sum(c[0] + c[1] for c in mine)
                    or s["third_down_attempts"] != sum(c[2] for c in mine)
                    or s["third_down_conversions"] != sum(c[3] for c in mine)):
                errors.append("chain counters differ from the drive chains")
    # A window's final possession ends it: each half, or each Pro Bowl quarter.
    windows = ((("quarter", q), (4 - q) * RULES.quarter_seconds) for q in (1, 2, 3, 4)) if pro_bowl else (
        (("half", h), 1800 if h == 1 else 0) for h in (1, 2))
    for (kind, number), boundary in windows:
        rows = [p for p in regulation if p.get(kind) == number]
        finals = [p for p in rows if p.get("half_final")]
        if any(p["end_clock"] != boundary for p in finals):
            errors.append("half-final possession does not end its window")
        if len(finals) > 1 or (finals and finals[0] is not rows[-1]):
            errors.append(f"{kind} {number} continues after its half-final possession")
    if any(p.get("half_final") and p["end_clock"] != 0 for p in overtime):
        errors.append("half-final possession does not end its window")
    errors.extend(check_ledger(result))
    return errors
