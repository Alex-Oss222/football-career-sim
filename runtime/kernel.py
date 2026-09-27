"""One protagonist-blind possession kernel for interactive and background games."""
from dataclasses import dataclass, asdict
import hashlib, json, math, random

from . import KERNEL_VERSION
from .calibration import load, validate
from .injuries import maybe_injury
from .rules import RULES, ot_status
from . import drive_model
from . import usage
from .player_evidence import empty_player_stats, normalize_players, observation
from .play_detail import (
    apply_drive_detail, apply_kickoff_detail, canonical_call_sheet, check_ledger,
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
            blocker = offense_by_id.get(play["blocker"])
            if blocker:
                evidence.append(
                    observation(
                        blocker,
                        unit="offense",
                        role="pass protection",
                        responsibility="protect assigned gap/edge",
                        situation="generated passing down",
                        assignment="assignment identified",
                        technique="leverage lost",
                        physical_execution="pressure reached quarterback",
                    )
                )
        if play.get("play_type") == "punt" and play.get("cover_player"):
            cover = offense_by_id.get(play["cover_player"])
            if cover:
                evidence.append(
                    observation(
                        cover,
                        unit="special teams",
                        role="punt coverage",
                        responsibility="maintain coverage lane and leverage",
                        situation="punt",
                        assignment="coverage lane held",
                        communication="substitution responsibility confirmed",
                        observable_effort="coverage pursuit continued to the finish",
                        special_teams_responsibility="coverage lane, leverage and tackle finish",
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


def _chains(rng, cal, values, plays, yards, penalties):
    """Third-down attempts/conversions and first downs for one drive."""
    per_game_plays = cal["model"]["plays_per_team_game"]
    third_rate = values["third_down_attempts_per_team_game"] / per_game_plays
    attempts = sum(rng.random() < third_rate for _ in range(plays))
    conversions = sum(rng.random() < cal["model"]["third_down_rate"] for _ in range(attempts))
    yards_per_first_down = (
        cal["model"]["yards_per_team_game"] / values["scrimmage_first_downs_per_team_game"]
    )
    first_downs = 0
    if yards > 0:
        whole, part = divmod(yards / yards_per_first_down, 1)
        first_downs = int(whole) + (rng.random() < part)
    per_penalty = (
        values["penalty_first_downs_per_team_game"]
        / (cal["model"]["penalty_per_play"] * per_game_plays)
    )
    first_downs += sum(rng.random() < per_penalty for _ in range(penalties))
    return attempts, conversions, first_downs


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


def _edge(team, defense, home):
    return max(
        -0.06,
        min(
            0.06,
            (team.offense_anchor - defense.defense_anchor) * 0.025
            + (0.008 if team is home else 0),
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
    usage_values = usage.load()["values"]
    model = cal["model"]
    gross_per_attempt = cal["derived"]["gross_yards_per_pass_attempt"]
    yards_per_attempt = gross_per_attempt["numerator"] / gross_per_attempt["denominator"]
    carry = cal["derived"]["yards_per_carry"]
    yards_per_carry = carry["numerator"] / carry["denominator"]
    xp_rate = drive_model.rate("extra_point")
    td_pass_rate = drive_model.rate("td_type_pass")
    punt_return_rate = model["punt_return_rate"]
    touchback_rate = model["kickoff_touchback_rate"]
    interior = drive_model.interior_probs()

    teams = {home.team_id: home, away.team_id: away}
    rosters = {home.team_id: home_players, away.team_id: away_players}
    stats = {t.team_id: _blank_team_stats(rosters[t.team_id]) for t in (home, away)}
    play_call_stats = {home.team_id: {}, away.team_id: {}}
    evidence = []
    possessions = []
    play_ledger = []
    kickoffs = []
    diagnostics = {"yard_split_count_fallback": 0, "net_without_snaps_dropped": 0, "td_split_fitted": 0,
                   "interior_clock_redirected": 0}
    # Legacy synthetic inputs without a QB keep one deterministic passer.
    passers = {tid: usage.game_passer(players) or players[0] for tid, players in rosters.items()}

    def other(team_id):
        return away.team_id if team_id == home.team_id else home.team_id

    def append_rows(rows):
        for row in rows:
            row["sequence"] = len(play_ledger) + 1
            play_ledger.append(row)

    def kick(kicking, receiving, *, free_kick, half, remaining, ot_label="OT"):
        kick_no = len(kickoffs) + 1
        if free_kick:
            returned = rng.random() < drive_model.safety_free_kick_return_rate()
        else:
            returned = not rng.random() < touchback_rate
        stats[kicking]["kickoffs"] += 1
        if returned:
            stats[receiving]["kick_returns"] += 1
        record = {
            "kick_no": kick_no, "kicking": kicking, "receiving": receiving,
            "returned": returned, "free_kick": free_kick, "half": half,
            "drive": len(possessions) + 1,
        }
        kickoffs.append(record)
        append_rows(apply_kickoff_detail(
            seed=seed, event_id=event_id, kick_no=kick_no,
            kicking=teams[kicking], receiving=teams[receiving], rosters=rosters,
            stats=stats, returned=returned, free_kick=free_kick,
            remaining=remaining, overtime=ot_label if half == "OT" else False, drive=record["drive"],
        ))
        return record

    def possess(offense, window, half, ot_history=None, ot_label="OT"):
        team = teams[offense]
        defense = teams[other(offense)]
        edge = _edge(team, defense, home)
        drive_no = len(possessions) + 1

        # 1-3. Category and a real 2012 drive of that category.
        category = drive_model.draw_category(rng, drive_model.apply_edge(interior, edge))
        row = drive_model.sample_tuple(rng, drive_model.pool("interior", category))
        seconds = drive_model.scaled_seconds(row)
        half_final = False
        if category == "clock":
            diagnostics["interior_clock_redirected"] += 1
        if category == "clock" or seconds >= window:
            half_final = True
            key = drive_model.bucket(window)
            category = drive_model.draw_category(
                rng, drive_model.apply_edge(drive_model.half_final_probs(key), edge))
            row = None
            if category != "clock":
                row = drive_model.sample_tuple(
                    rng, drive_model.pool("half_final", category, key), max_seconds=window)
            if category == "clock" or row is None:
                category = "clock"
                row = drive_model.clock_tuple(rng, key)
            # The half-final pool holds THE last offensive possession of a
            # half, so this possession runs out the window: no further
            # possession and no kickoff follow it in this half (or OT period).
            # Correction of the double-final defect found by the 2013.6
            # acceptance audit, where leftover time started another,
            # almost always clock-expired, possession.
            seconds = window
        plays, net = int(row[0]), int(row[1])
        if plays == 0 and category in {"touchdown", "interception", "fumble_lost", "downs"}:
            plays = 1

        # 4. Pass/run shape of the drive.
        pass_plays = sum(rng.random() < model["pass_play_share"] for _ in range(plays))
        sacks = sum(rng.random() < cal["derived"]["sack_rate"]["value"] for _ in range(pass_plays))
        if category == "interception" and pass_plays == 0:
            pass_plays = 1
        if category in {"touchdown", "interception"} and pass_plays and sacks == pass_plays:
            sacks -= 1
        rushes = plays - pass_plays
        usable = pass_plays - sacks - (1 if category == "interception" else 0)
        if usable + rushes == 0 and sacks:
            sacks -= 1
            usable += 1

        # 5. Touchdown type and turnover type.
        td_type = None
        if category == "touchdown":
            wants_pass = rng.random() < td_pass_rate
            feasible = [t for t, ok in (("pass", usable > 0), ("rush", rushes > 0)) if ok]
            td_type = ("pass" if wants_pass else "rush") if len(feasible) == 2 else feasible[0]
        turnover_type = category if category in drive_model.TURNOVER_CATEGORIES else None

        # 6. Sack losses (possession stream).
        sack_losses = [rng.randint(3, 10) for _ in range(sacks)]

        # 7. Gross passing/rushing yardage reconciled to the tuple's net.
        if usable + rushes == 0 and net:
            diagnostics["net_without_snaps_dropped"] += 1
            net = 0
        total = net + sum(sack_losses)
        weight_pass = max(0.0, rng.gauss(usable * yards_per_attempt, max(6, usable * 3))) if usable else 0.0
        weight_rush = max(0.0, rng.gauss(rushes * yards_per_carry, max(4, rushes * 2))) if rushes else 0.0
        if usable + rushes == 0:
            pass_yards = rush_yards = 0
        elif not usable:
            pass_yards, rush_yards = 0, total
        elif not rushes:
            pass_yards, rush_yards = total, 0
        else:
            if weight_pass + weight_rush <= 0:
                diagnostics["yard_split_count_fallback"] += 1
                weight_pass, weight_rush = usable, rushes
            pass_yards, rush_yards = _split_yards(total, weight_pass, weight_rush)
        if td_type == "pass" and pass_yards < 1:
            rush_yards -= 1 - pass_yards
            pass_yards = 1
        elif td_type == "rush" and rush_yards < 1:
            pass_yards -= 1 - rush_yards
            rush_yards = 1
        if td_type and usable and rushes:
            # Feasibility, not calibration: the non-touchdown type's yards
            # must fit before the scoring snap without reaching the end zone
            # (<= net - 1) or backing into the own end zone after the sacks
            # (>= net - 99 + losses). Any excess moves to the touchdown type,
            # whose total then lies in [losses + 1, 99].
            before = rush_yards if td_type == "pass" else pass_yards
            fitted = min(max(before, net - 99 + sum(sack_losses)), net - 1)
            if fitted != before:
                diagnostics["td_split_fitted"] += 1
                if td_type == "pass":
                    rush_yards, pass_yards = fitted, pass_yards + before - fitted
                else:
                    pass_yards, rush_yards = fitted, rush_yards + before - fitted

        s = stats[offense]
        d = stats[defense.team_id]
        s["passing_yards"] += pass_yards
        s["rushing_yards"] += rush_yards
        s["sacks_allowed"] += sacks

        # 8. Penalties and chains (unchanged mechanism).
        pens = sum(rng.random() < model["penalty_per_play"] for _ in range(plays))
        s["penalties"] += pens
        s["penalty_yards"] += pens * rng.randint(5, 10) if pens else 0
        third, converted, firsts = _chains(
            rng, cal, usage_values, plays, pass_yards + rush_yards, pens
        )
        s["first_downs"] += firsts
        s["third_down_attempts"] += third
        s["third_down_conversions"] += converted

        # 9. Terminal scoring.
        points = 0
        score_kind = None
        xp_made = None
        fg_made = None
        fg_distance = None
        punt_return = False
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
            fg_distance = int(row[3])
            fg_made = rng.random() < drive_model.fg_make_prob(fg_distance)
            if fg_made:
                points = 3
                s["field_goals"] += 1
                score_kind = "field_goal"
        elif category == "punt":
            s["punts"] += 1
            punt_return = rng.random() < punt_return_rate
            d["punt_returns"] += int(punt_return)
        elif category in drive_model.TURNOVER_CATEGORIES:
            s["turnovers"] += 1
        elif category == "downs":
            s["turnovers_on_downs"] += 1
        elif category == "safety":
            d["points"] += 2
            d["safeties"] += 1
            score_kind = "safety"
        elif category == "clock":
            s["clock_expired_drives"] += 1
        s["drives"] += 1
        s["points"] += points
        s["time_of_possession"] += seconds

        terminal = CLOCK_REASON[half] if category == "clock" else category
        if half == "OT":
            start_clock, end_clock = window, window - seconds
        else:
            base = 1800 if half == 1 else 0
            start_clock, end_clock = base + window, base + window - seconds

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
            plays=plays,
            pass_plays=pass_plays,
            sacks=sacks,
            pass_yards=pass_yards,
            rush_yards=rush_yards,
            category=terminal,
            td_type=td_type,
            turnover_type=turnover_type,
            sack_losses=sack_losses,
            fg_made=fg_made,
            fg_distance=fg_distance,
            xp_made=xp_made,
            net_yards=net,
            start_clock=start_clock,
            end_clock=end_clock,
            overtime=ot_label if half == "OT" else False,
            punt_return=punt_return,
            passer=passers[offense],
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
            "sack_loss_total": sum(sack_losses),
            "fg_distance": fg_distance,
            "fg_made": fg_made,
            "xp_made": xp_made,
            "half_final": half_final,
            "kickoff_after": None,
        }
        if half == "OT":
            record["period"] = "OT"
        possessions.append(record)
        return record, score_kind

    # Regulation: two clock-bounded halves; a possession never crosses one.
    opening_receiver = away.team_id if rng.random() < 0.5 else home.team_id
    for half in (1, 2):
        offense = opening_receiver if half == 1 else other(opening_receiver)
        window = RULES.quarter_seconds * 2
        kick(other(offense), offense, free_kick=False, half=half,
             remaining=window + (1800 if half == 1 else 0))
        while window > 0:
            record, score_kind = possess(offense, window, half)
            window -= record["seconds"]
            if score_kind and window > 0:
                kicked = kick(offense, other(offense), free_kick=score_kind == "safety",
                              half=half, remaining=window + (1800 if half == 1 else 0))
                record["kickoff_after"] = {"returned": kicked["returned"],
                                           "free_kick": kicked["free_kick"]}
            offense = other(offense)

    total = RULES.quarter_seconds * 4
    overtime_seconds = 0
    if stats[home.team_id]["points"] == stats[away.team_id]["points"]:
        # A new coin toss decides the overtime receiver.
        offense = home.team_id if rng.random() < 0.5 else away.team_id
        period_length = (
            RULES.postseason_ot_seconds if game_type == "postseason" else RULES.regular_ot_seconds
        )
        window = period_length
        history = []
        ot_period = 1
        kick(other(offense), offense, free_kick=False, half="OT", remaining=window)
        while True:
            if window <= 0:
                if ot_status(history, game_type, expired=True) == "end":
                    break
                window = period_length
                ot_period += 1
            label = "OT" if ot_period == 1 else "OT%d" % ot_period
            record, score_kind = possess(offense, window, "OT", history, label)
            window -= record["seconds"]
            overtime_seconds += record["seconds"]
            history.append({"team": offense, "score": score_kind})
            if ot_status(history, game_type) == "end":
                break
            if score_kind and window > 0:
                kicked = kick(offense, other(offense), free_kick=score_kind == "safety",
                              half="OT", remaining=window, ot_label=label)
                record["kickoff_after"] = {"returned": kicked["returned"],
                                           "free_kick": kicked["free_kick"]}
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
    if second is None or second["team"] == opening:
        errors.append("second half opened by the opening receiver")
    kicks = result.get("kickoffs", [])
    expected_kicks = 2 + (1 if overtime else 0) + sum(1 for p in possessions if p.get("kickoff_after"))
    if len(kicks) != expected_kicks:
        errors.append("kickoff count mismatch")
    for team, s in result["team_stats"].items():
        if s["kickoffs"] != sum(1 for k in kicks if k["kicking"] == team):
            errors.append("kickoff counter mismatch")
        if s["kick_returns"] != sum(1 for k in kicks if k["receiving"] == team and k["returned"]):
            errors.append("kick return counter mismatch")
        if s["drives"] != sum(1 for p in possessions if p["team"] == team):
            errors.append("drive counter mismatch")
    if any(p.get("half_final") and p["end_clock"] != (1800 if p["half"] == 1 else 0) for p in possessions):
        errors.append("half-final possession does not end its window")
    for half in (1, 2):
        finals = [p for p in regulation if p["half"] == half and p.get("half_final")]
        rows = [p for p in regulation if p["half"] == half]
        if len(finals) > 1 or (finals and finals[0] is not rows[-1]):
            errors.append(f"half {half} continues after its half-final possession")
    errors.extend(check_ledger(result))
    return errors
