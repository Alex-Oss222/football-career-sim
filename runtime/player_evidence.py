"""Roster-aware attribution and qualitative evidence for generated football.

This module never decides whether a player makes the roster.  It translates
kernel events into the limited observations that the event actually supports.
"""
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class PlayerInput:
    player_id: str
    position: str
    available: bool = True
    unit: str = "offense"
    roles: tuple = ()
    responsibilities: tuple = ()
    rotation_status: str = "competition"
    medical_limitation: str | None = None


STAT_FIELDS = (
    "pass_attempts", "passing_yards", "rushing_attempts", "rushing_yards",
    "receptions", "receiving_yards", "sacks_allowed", "sacks", "pressures",
    "interceptions", "fumbles", "field_goals_made", "punts", "return_yards",
    "tackles",
)


def normalize_players(team):
    """Return available PlayerInput records, preserving legacy test inputs."""
    if team.roster:
        players = tuple(p if isinstance(p, PlayerInput) else PlayerInput(**p) for p in team.roster)
        active = set(team.active_players)
        return tuple(p for p in players if p.available and (not active or p.player_id in active or f"{p.position}:{p.player_id}" in active))
    result = []
    for raw in team.active_players:
        position, player_id = raw.split(":", 1) if ":" in raw else ("WR", raw)
        unit = "special_teams" if position in {"K", "P", "LS", "KR", "PR"} else "defense" if position in {"DL", "DE", "DT", "LB", "CB", "S"} else "offense"
        result.append(PlayerInput(player_id=raw, position=position, unit=unit))
    return tuple(result)


def empty_player_stats(players):
    return {p.player_id: {"position": p.position, **{field: 0 for field in STAT_FIELDS}} for p in players}


def _planned_weight(player, role):
    # Qualitative rotation intentions affect opportunity, never an ability score.
    weight = {"core": 2, "competition": 4, "bubble": 3, "reduced": 1}.get(player.rotation_status, 2)
    if role in player.roles or role in player.responsibilities:
        weight += 4
    return weight


def choose(rng, players, positions, role=""):
    candidates = [p for p in players if p.position in positions]
    if not candidates:
        candidates = list(players)
    if not candidates:
        raise ValueError("available participants required")
    weights = [_planned_weight(p, role) for p in candidates]
    return rng.choices(candidates, weights=weights, k=1)[0]


def observation(player, *, unit, role, responsibility, situation,
                assignment=None, communication=None, processing=None,
                technique=None, physical_execution=None, observable_effort=None,
                correction_retention=None, special_teams_responsibility=None,
                coaching_teaching_issue=None):
    """Create sparse coach-facing evidence; unsupported dimensions stay absent."""
    values = {
        "player": player.player_id, "position": player.position, "unit": unit,
        "personnel_role": role, "football_responsibility": responsibility,
        "situation": situation, "assignment_execution": assignment,
        "communication": communication, "processing": processing,
        "technique": technique, "physical_execution": physical_execution,
        "observable_effort": observable_effort,
        "correction_retention": correction_retention,
        "special_teams_responsibility": special_teams_responsibility,
        "medical_limitation": player.medical_limitation,
        "coaching_teaching_issue": coaching_teaching_issue,
    }
    return {key: value for key, value in values.items() if value is not None}


def serialize_roster(players):
    return [asdict(p) for p in players]
