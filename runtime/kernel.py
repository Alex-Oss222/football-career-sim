"""Shared deterministic football kernel.

Every protagonist and background game uses this same drive resolver. The caller
supplies a resolver that closes each Packet against the private Engine State.
No protagonist label is accepted by this API.
"""
from dataclasses import dataclass, field
from .calibration import DRIVE_WEIGHTS, TIER_ANCHORS
from .packets import Packet

PROCEDURE_VERSION = "2013-drive-kernel-v1"

@dataclass
class TeamInput:
    team_id: str
    offense: str = "average"
    defense: str = "average"
    special_teams: str = "average"

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
    third_down_made: int = 0
    third_down_att: int = 0
    possession_seconds: int = 0

@dataclass
class GameResult:
    home: TeamStats = field(default_factory=TeamStats)
    away: TeamStats = field(default_factory=TeamStats)
    drive_log: list = field(default_factory=list)

def _anchor(tier):
    key = str(tier).strip().lower()
    if key not in TIER_ANCHORS:
        raise ValueError(f"unknown qualitative tier: {tier}")
    return TIER_ANCHORS[key]

def _weights(offense, defense, special_teams):
    delta = max(-4, min(4, _anchor(offense) - _anchor(defense)))
    st = max(-2, min(2, _anchor(special_teams)))
    w = dict(DRIVE_WEIGHTS)
    # Each step is deliberately small. Better offense shifts probability from
    # punts/turnovers toward scores; defense does the inverse.
    shift = delta * 12
    w["td_methodical"] = max(20, w["td_methodical"] + shift)
    w["td_explosive"] = max(10, w["td_explosive"] + shift // 2)
    w["field_goal"] = max(20, w["field_goal"] + delta * 5 + st * 2)
    w["punt_short"] = max(20, w["punt_short"] - shift // 2)
    w["punt_fieldflip"] = max(20, w["punt_fieldflip"] - shift // 2)
    w["turnover_short"] = max(10, w["turnover_short"] - delta * 5)
    w["turnover_deep"] = max(10, w["turnover_deep"] - delta * 4)
    return w

def _shape(outcome):
    # Yardage/time are coherent drive-shape anchors, not hidden player ratings.
    return {
        "td_methodical": (74, 205, 7, 1, 0, 0),
        "td_explosive": (61, 92, 7, 0, 0, 0),
        "field_goal": (48, 178, 3, 1, 0, 0),
        "punt_short": (16, 106, 0, 0, 0, 1),
        "punt_fieldflip": (31, 151, 0, 1, 0, 1),
        "turnover_short": (13, 77, 0, 0, 1, 0),
        "turnover_deep": (44, 166, 0, 1, 1, 0),
        "turnover_on_downs": (38, 174, 0, 1, 0, 0),
        "missed_field_goal": (43, 166, 0, 1, 0, 0),
        "end_period": (24, 84, 0, 0, 0, 0),
        "safety": (-5, 48, -2, 0, 0, 0),
    }[outcome]

def simulate_game(event_id, snapshot, home, away, resolve_packet, possessions_each=11):
    if home.team_id == away.team_id:
        raise ValueError("teams must be distinct")
    result = GameResult()
    sides = [(home, result.home), (away, result.away)]
    elapsed = 0
    for index in range(possessions_each * 2):
        team, stats = sides[index % 2]
        opponent = sides[(index + 1) % 2][0]
        packet = Packet.freeze(
            f"{event_id}:drive:{index+1}", PROCEDURE_VERSION,
            snapshot=snapshot,
            inputs={"offense": team.team_id, "defense": opponent.team_id},
            modifiers={},
            weights=_weights(team.offense, opponent.defense, team.special_teams),
        )
        outcome = resolve_packet(packet)
        yards, seconds, points, third, turnover, punt = _shape(outcome)
        seconds = min(seconds, max(0, 3600 - elapsed))
        elapsed += seconds
        stats.drives += 1
        stats.yards += yards
        # A stable era-neutral split for topline accounting; player allocation is
        # a separate roster-aware layer.
        pass_yards = max(0, round(max(0, yards) * 0.66))
        rush_yards = yards - pass_yards
        stats.passing += pass_yards
        stats.rushing += rush_yards
        stats.possession_seconds += seconds
        stats.third_down_att += 1
        stats.third_down_made += third
        stats.turnovers += turnover
        stats.punts += punt
        if points == 7:
            stats.touchdowns += 1
            stats.score += 7
        elif points == 3:
            stats.field_goals += 1
            stats.score += 3
        elif points == -2:
            other_stats = sides[(index + 1) % 2][1]
            other_stats.score += 2
        result.drive_log.append({
            "drive": index + 1, "offense": team.team_id, "outcome": outcome,
            "yards": yards, "seconds": seconds,
        })
        if elapsed >= 3600:
            break
    return result
