"""Shared deterministic 2013 football kernel.

Protagonist and background games call this same drive resolver. The API accepts
football facts, not protagonist labels or desired results. Outcome draws are
closed against the private Engine State through the supplied resolver.
"""
from dataclasses import dataclass, field
from .calibration import DRIVE_WEIGHTS, PENALTY_WEIGHTS, TIER_ANCHORS
from .injury import SEVERITY_WEIGHTS, occurrence_weights, football_status
from .packets import Packet

PROCEDURE_VERSION = "2013-drive-kernel-v2"

@dataclass(frozen=True)
class PlayerInput:
    player_id: str
    position: str
    exposure: float
    available: bool = True

@dataclass
class TeamInput:
    team_id: str
    offense: str = "average"
    defense: str = "average"
    special_teams: str = "average"
    players: tuple = ()

@dataclass
class TeamStats:
    score: int = 0
    drives: int = 0
    yards: int = 0
    passing: int = 0
    rushing: int = 0
    turnovers: int = 0
    punts: int = 0
    field_goals: int = 0
    touchdowns: int = 0
    penalties: int = 0
    penalty_yards: int = 0
    third_down_made: int = 0
    third_down_att: int = 0
    possession_seconds: int = 0

@dataclass
class GameResult:
    home: TeamStats = field(default_factory=TeamStats)
    away: TeamStats = field(default_factory=TeamStats)
    drive_log: list = field(default_factory=list)
    injuries: list = field(default_factory=list)
    overtime_periods: int = 0

def _anchor(tier):
    key = str(tier).strip().lower()
    if key not in TIER_ANCHORS:
        raise ValueError(f"unknown qualitative tier: {tier}")
    return TIER_ANCHORS[key]

def _weights(offense, defense, special_teams):
    delta = max(-4, min(4, _anchor(offense) - _anchor(defense)))
    st = max(-2, min(2, _anchor(special_teams)))
    w = dict(DRIVE_WEIGHTS)
    shift = delta * 10
    w["td_methodical"] = max(20, w["td_methodical"] + shift)
    w["td_explosive"] = max(10, w["td_explosive"] + shift // 2)
    w["field_goal"] = max(20, w["field_goal"] + delta * 4 + st * 2)
    w["punt_short"] = max(20, w["punt_short"] - shift // 2)
    w["punt_fieldflip"] = max(20, w["punt_fieldflip"] - shift // 2)
    w["turnover_short"] = max(10, w["turnover_short"] - delta * 4)
    w["turnover_deep"] = max(10, w["turnover_deep"] - delta * 3)
    return w

def _shape(outcome):
    return {
        "td_methodical": (65, 205, 7, 2, 0, 0),
        "td_explosive": (55, 92, 7, 1, 0, 0),
        "field_goal": (40, 178, 3, 2, 0, 0),
        "punt_short": (12, 106, 0, 1, 0, 1),
        "punt_fieldflip": (24, 151, 0, 1, 0, 1),
        "turnover_short": (10, 77, 0, 0, 1, 0),
        "turnover_deep": (35, 166, 0, 1, 1, 0),
        "turnover_on_downs": (30, 174, 0, 2, 0, 0),
        "missed_field_goal": (35, 166, 0, 2, 0, 0),
        "end_period": (18, 84, 0, 0, 0, 0),
        "safety": (-5, 48, -2, 0, 0, 0),
    }[outcome]

def _packet(event_id, snapshot, suffix, inputs, weights):
    return Packet.freeze(
        f"{event_id}:{suffix}", PROCEDURE_VERSION,
        snapshot=snapshot, inputs=inputs, modifiers={}, weights=weights,
    )

def _run_drive(result, event_id, snapshot, index, offense, defense,
               offense_stats, defense_stats, resolve_packet, seconds_left):
    outcome = resolve_packet(_packet(
        event_id, snapshot, f"drive:{index}",
        {"offense": offense.team_id, "defense": defense.team_id},
        _weights(offense.offense, defense.defense, offense.special_teams),
    ))
    yards, seconds, points, third_att, turnover, punt = _shape(outcome)
    seconds = min(seconds, max(0, seconds_left))
    offense_stats.drives += 1
    offense_stats.yards += yards
    pass_yards = max(0, round(max(0, yards) * 0.667))
    offense_stats.passing += pass_yards
    offense_stats.rushing += yards - pass_yards
    offense_stats.possession_seconds += seconds
    offense_stats.third_down_att += third_att
    offense_stats.third_down_made += min(third_att, 1 if outcome in {"td_methodical","field_goal","punt_fieldflip","turnover_deep"} else 0)
    offense_stats.turnovers += turnover
    offense_stats.punts += punt

    penalty = resolve_packet(_packet(
        event_id, snapshot, f"penalty:{index}",
        {"offense": offense.team_id, "defense": defense.team_id},
        PENALTY_WEIGHTS,
    ))
    if penalty == "offense":
        offense_stats.penalties += 1
        offense_stats.penalty_yards += 8
    elif penalty == "defense":
        defense_stats.penalties += 1
        defense_stats.penalty_yards += 8

    if points == 7:
        offense_stats.touchdowns += 1
        offense_stats.score += 7
    elif points == 3:
        offense_stats.field_goals += 1
        offense_stats.score += 3
    elif points == -2:
        defense_stats.score += 2

    result.drive_log.append({
        "drive": index, "offense": offense.team_id, "outcome": outcome,
        "yards": yards, "seconds": seconds, "penalty": penalty,
    })
    return outcome, seconds

def _resolve_injuries(result, event_id, snapshot, team, resolve_packet):
    for player in team.players:
        if not isinstance(player, PlayerInput) or not player.available or player.exposure <= 0:
            continue
        occurred = resolve_packet(_packet(
            event_id, snapshot, f"injury:{team.team_id}:{player.player_id}",
            {"team": team.team_id, "player": player.player_id, "position": player.position},
            occurrence_weights(player.position, player.exposure),
        ))
        if occurred == "injury":
            severity = resolve_packet(_packet(
                event_id, snapshot, f"injury-severity:{team.team_id}:{player.player_id}",
                {"team": team.team_id, "player": player.player_id, "position": player.position},
                SEVERITY_WEIGHTS,
            ))
            result.injuries.append({
                "team": team.team_id,
                "player_id": player.player_id,
                "football_status": football_status(severity),
            })

def simulate_game(event_id, snapshot, home, away, resolve_packet,
                  possessions_each=11, postseason=False):
    if home.team_id == away.team_id:
        raise ValueError("teams must be distinct")
    if possessions_each < 1:
        raise ValueError("possessions_each must be positive")
    result = GameResult()
    sides = [(home, result.home), (away, result.away)]
    elapsed = 0
    drive_index = 0

    for index in range(possessions_each * 2):
        side_index = index % 2
        offense, offense_stats = sides[side_index]
        defense, defense_stats = sides[1 - side_index]
        drive_index += 1
        _, seconds = _run_drive(
            result, event_id, snapshot, drive_index, offense, defense,
            offense_stats, defense_stats, resolve_packet, 3600 - elapsed,
        )
        elapsed += seconds
        if elapsed >= 3600:
            break

    # 2013 modified sudden death. One 15-minute OT in preseason/regular season;
    # postseason continues in additional 15-minute periods until a winner.
    if result.home.score == result.away.score:
        toss = resolve_packet(_packet(
            event_id, snapshot, "ot-coin",
            {"home": home.team_id, "away": away.team_id},
            {"home_receive": 1, "away_receive": 1},
        ))
        receive_index = 0 if toss == "home_receive" else 1
        periods = 0
        while result.home.score == result.away.score and (postseason or periods == 0):
            periods += 1
            result.overtime_periods = periods
            ot_elapsed = 0
            first_possession = True
            both_opportunities = False
            possession_index = receive_index
            while ot_elapsed < 900:
                offense, offense_stats = sides[possession_index]
                defense, defense_stats = sides[1 - possession_index]
                before_off = offense_stats.score
                before_def = defense_stats.score
                drive_index += 1
                outcome, seconds = _run_drive(
                    result, event_id, snapshot, drive_index, offense, defense,
                    offense_stats, defense_stats, resolve_packet, 900 - ot_elapsed,
                )
                ot_elapsed += seconds
                off_scored = offense_stats.score > before_off
                def_scored = defense_stats.score > before_def
                if first_possession and (outcome in {"td_methodical","td_explosive","safety"}):
                    break
                if not first_possession:
                    both_opportunities = True
                if both_opportunities and (off_scored or def_scored):
                    break
                first_possession = False
                possession_index = 1 - possession_index
                if result.home.score != result.away.score and both_opportunities:
                    break
            if not postseason:
                break
            receive_index = 1 - receive_index

    _resolve_injuries(result, event_id, snapshot, home, resolve_packet)
    _resolve_injuries(result, event_id, snapshot, away, resolve_packet)
    return result
