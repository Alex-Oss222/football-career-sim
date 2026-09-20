"""One protagonist-blind possession kernel for interactive and background games."""
from dataclasses import dataclass, asdict
import hashlib, json, random

from . import KERNEL_VERSION
from .calibration import load, validate
from .injuries import maybe_injury
from .rules import RULES
from .player_evidence import empty_player_stats, normalize_players, observation
from .play_detail import apply_drive_detail


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
                    )
                )


def _drive_team_stats(rng, cal, team, defense, plays, pass_plays, sacks):
    pass_attempt_opportunities = max(0, pass_plays - sacks)
    if pass_attempt_opportunities:
        pass_yards = max(
            -5,
            round(
                rng.gauss(
                    pass_attempt_opportunities * 6.55,
                    max(6, pass_attempt_opportunities * 3),
                )
            ),
        )
    else:
        pass_yards = 0

    rush_plays = plays - pass_plays
    if rush_plays:
        rush_yards = max(
            -5,
            round(rng.gauss(rush_plays * 4.26, max(4, rush_plays * 2))),
        )
    else:
        rush_yards = 0

    return pass_yards, rush_yards


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

    packet = {
        "event_id": event_id,
        "home": asdict(home),
        "away": asdict(away),
        "venue": venue,
        "weather": weather,
        "game_type": game_type,
    }
    rng = _rng(seed, packet)
    cal = load()
    assert not validate(cal)
    probs = cal["model"]["drive_outcomes"]

    possessions = []
    play_ledger = []
    teams = {home.team_id: home, away.team_id: away}
    rosters = {home.team_id: home_players, away.team_id: away_players}
    stats = {
        t.team_id: {
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
            "players": empty_player_stats(rosters[t.team_id]),
        }
        for t in (home, away)
    }
    play_call_stats = {home.team_id: {}, away.team_id: {}}
    evidence = []

    clock = RULES.quarter_seconds * 4
    offense = away.team_id if rng.random() < 0.5 else home.team_id
    drive_no = 0

    while clock > 0:
        team = teams[offense]
        defense = away if offense == home.team_id else home
        drive_no += 1
        start_clock = clock
        seconds = min(clock, rng.randint(95, 205))
        clock -= seconds

        edge = max(
            -0.06,
            min(
                0.06,
                (team.offense_anchor - defense.defense_anchor) * 0.025
                + (0.008 if team is home else 0),
            ),
        )
        adjusted = dict(probs)
        adjusted["touchdown"] += edge
        adjusted["punt"] -= edge * 0.65
        adjusted["turnover"] -= edge * 0.35

        draw = rng.random()
        cumulative = 0
        for outcome, chance in adjusted.items():
            cumulative += chance
            if draw <= cumulative:
                break

        plays = rng.randint(3, 10)
        pass_plays = sum(
            rng.random() < cal["model"]["pass_play_share"] for _ in range(plays)
        )
        sacks = sum(
            rng.random() < cal["derived"]["sack_rate"]["value"]
            for _ in range(pass_plays)
        )
        if outcome in {"turnover", "touchdown"} and pass_plays and sacks == pass_plays:
            sacks -= 1

        pass_yards, rush_yards = _drive_team_stats(
            rng, cal, team, defense, plays, pass_plays, sacks
        )
        if (
            outcome == "turnover"
            and pass_plays - sacks == 1
            and plays - pass_plays == 0
        ):
            pass_yards = 0

        s = stats[offense]
        d = stats[defense.team_id]
        s["passing_yards"] += pass_yards
        s["rushing_yards"] += rush_yards
        s["sacks_allowed"] += sacks
        s["first_downs"] += max(0, round((pass_yards + rush_yards) / 15))

        third = max(0, plays // 3)
        s["third_down_attempts"] += third
        s["third_down_conversions"] += sum(
            rng.random() < cal["model"]["third_down_rate"] for _ in range(third)
        )
        pens = sum(
            rng.random() < cal["model"]["penalty_per_play"] for _ in range(plays)
        )
        s["penalties"] += pens
        s["penalty_yards"] += pens * rng.randint(5, 10) if pens else 0

        points = 0
        if outcome == "touchdown":
            points = 7
            s["touchdowns"] += 1
        elif outcome == "field_goal":
            points = 3
            s["field_goals"] += 1
        elif outcome == "punt":
            s["punts"] += 1
        elif outcome == "turnover":
            s["turnovers"] += 1

        s["points"] += points
        s["time_of_possession"] += seconds

        punt_return = False
        if outcome == "punt":
            punt_return = rng.random() < 0.52
            d["punt_returns"] += int(punt_return)

        kick_return = False
        if points and rng.random() > cal["model"]["kickoff_touchback_rate"]:
            kick_return = True
            d["kick_returns"] += 1

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
            outcome=outcome,
            start_clock=start_clock,
            end_clock=clock,
            kick_return=kick_return,
            punt_return=punt_return,
        )
        for play in drive_ledger:
            play["sequence"] = len(play_ledger) + 1
            play_ledger.append(play)
        _merge_call_stats(play_call_stats[offense], drive_calls)
        _append_evidence(
            evidence,
            drive_ledger,
            rosters[offense],
            rosters[defense.team_id],
            outcome,
        )

        possessions.append(
            {
                "number": drive_no,
                "team": offense,
                "start_clock": start_clock,
                "end_clock": clock,
                "seconds": seconds,
                "scrimmage_plays": plays,
                "outcome": outcome,
                "points": points,
            }
        )
        offense = defense.team_id

    total = RULES.quarter_seconds * 4
    overtime_seconds = 0

    if stats[home.team_id]["points"] == stats[away.team_id]["points"]:
        ot_limit = (
            RULES.postseason_ot_seconds
            if game_type == "postseason"
            else RULES.regular_ot_seconds
        )
        ot_offense = offense
        possessions_in_ot = 0

        while True:
            start_ot_clock = ot_limit - overtime_seconds
            seconds = min(start_ot_clock, rng.randint(75, 190))
            if seconds <= 0:
                if game_type == "postseason":
                    ot_limit += RULES.postseason_ot_seconds
                    continue
                break

            overtime_seconds += seconds
            possessions_in_ot += 1
            drive_no += 1
            team = teams[ot_offense]
            defense = away if ot_offense == home.team_id else home

            draw = rng.random()
            cumulative = 0
            for outcome, chance in probs.items():
                cumulative += chance
                if draw <= cumulative:
                    break

            plays = rng.randint(3, 9)
            pass_plays = sum(
                rng.random() < cal["model"]["pass_play_share"] for _ in range(plays)
            )
            sacks = sum(
                rng.random() < cal["derived"]["sack_rate"]["value"]
                for _ in range(pass_plays)
            )
            if outcome in {"turnover", "touchdown"} and pass_plays and sacks == pass_plays:
                sacks -= 1

            pass_yards, rush_yards = _drive_team_stats(
                rng, cal, team, defense, plays, pass_plays, sacks
            )
            if (
                outcome == "turnover"
                and pass_plays - sacks == 1
                and plays - pass_plays == 0
            ):
                pass_yards = 0

            s = stats[ot_offense]
            d = stats[defense.team_id]
            s["passing_yards"] += pass_yards
            s["rushing_yards"] += rush_yards
            s["sacks_allowed"] += sacks
            s["first_downs"] += max(0, round((pass_yards + rush_yards) / 15))

            third = max(0, plays // 3)
            s["third_down_attempts"] += third
            s["third_down_conversions"] += sum(
                rng.random() < cal["model"]["third_down_rate"] for _ in range(third)
            )
            pens = sum(
                rng.random() < cal["model"]["penalty_per_play"] for _ in range(plays)
            )
            s["penalties"] += pens
            s["penalty_yards"] += pens * rng.randint(5, 10) if pens else 0

            points = 7 if outcome == "touchdown" else 3 if outcome == "field_goal" else 0
            if outcome == "touchdown":
                s["touchdowns"] += 1
            elif outcome == "field_goal":
                s["field_goals"] += 1
            elif outcome == "punt":
                s["punts"] += 1
            elif outcome == "turnover":
                s["turnovers"] += 1

            s["points"] += points
            s["time_of_possession"] += seconds

            punt_return = False
            if outcome == "punt":
                punt_return = rng.random() < 0.52
                d["punt_returns"] += int(punt_return)

            kick_return = False
            if points and rng.random() > cal["model"]["kickoff_touchback_rate"]:
                kick_return = True
                d["kick_returns"] += 1

            end_ot_clock = max(0, start_ot_clock - seconds)
            drive_ledger, drive_calls = apply_drive_detail(
                seed=seed,
                event_id=event_id,
                drive_no=drive_no,
                team=team,
                defense=defense,
                available=rosters[ot_offense],
                defenders=rosters[defense.team_id],
                offense_stats=s,
                defense_stats=d,
                plays=plays,
                pass_plays=pass_plays,
                sacks=sacks,
                pass_yards=pass_yards,
                rush_yards=rush_yards,
                outcome=outcome,
                start_clock=start_ot_clock,
                end_clock=end_ot_clock,
                kick_return=kick_return,
                punt_return=punt_return,
            )
            for play in drive_ledger:
                play["period"] = "OT"
                play["sequence"] = len(play_ledger) + 1
                play_ledger.append(play)
            _merge_call_stats(play_call_stats[ot_offense], drive_calls)
            _append_evidence(
                evidence,
                drive_ledger,
                rosters[ot_offense],
                rosters[defense.team_id],
                outcome,
            )

            possessions.append(
                {
                    "number": drive_no,
                    "team": ot_offense,
                    "period": "OT",
                    "start_clock": start_ot_clock,
                    "end_clock": end_ot_clock,
                    "seconds": seconds,
                    "scrimmage_plays": plays,
                    "outcome": outcome,
                    "points": points,
                }
            )

            lead = stats[home.team_id]["points"] != stats[away.team_id]["points"]
            if lead and (points == 7 or possessions_in_ot >= 2):
                break
            ot_offense = defense.team_id
            if overtime_seconds >= ot_limit and game_type != "postseason":
                break

        total += overtime_seconds

    used = sum(v["time_of_possession"] for v in stats.values())
    stats[offense]["time_of_possession"] += total - used

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
        "final_score": {k: v["points"] for k, v in stats.items()},
        "possessions": possessions,
        "play_ledger": play_ledger,
        "play_call_stats": play_call_stats,
        "team_stats": stats,
        "player_evidence": evidence,
        "injuries": injuries,
        "pauses": pauses,
        "terminated": True,
    }


def validate_result(result):
    errors = []

    for team, score in result["final_score"].items():
        s = result["team_stats"][team]
        players = s["players"]

        if score != s["touchdowns"] * 7 + s["field_goals"] * 3:
            errors.append("score ledger mismatch")
        if sum(p["passing_yards"] for p in players.values()) != s["passing_yards"]:
            errors.append("passing yardage mismatch")
        if sum(p["rushing_yards"] for p in players.values()) != s["rushing_yards"]:
            errors.append("rushing yardage mismatch")
        if sum(p["receiving_yards"] for p in players.values()) != s["passing_yards"]:
            errors.append("receiving yardage mismatch")
        if sum(p["sacks_allowed"] for p in players.values()) != s["sacks_allowed"]:
            errors.append("sack attribution mismatch")
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

    elapsed = sum(p["seconds"] for p in result["possessions"])
    if sum(s["time_of_possession"] for s in result["team_stats"].values()) != elapsed:
        errors.append("clock mismatch")
    if any(
        p["end_clock"] < 0 or p["start_clock"] < p["end_clock"]
        for p in result["possessions"]
    ):
        errors.append("invalid clock")

    scrimmage_expected = sum(p.get("scrimmage_plays", 0) for p in result["possessions"])
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

    return errors
