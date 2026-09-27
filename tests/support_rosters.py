"""Synthetic, depth-ordered game-day rosters for runtime tests only."""
from runtime.player_evidence import PlayerInput

LAYOUT = (
    ("QB", 2, "offense"), ("RB", 3, "offense"), ("FB", 1, "offense"),
    ("WR", 5, "offense"), ("TE", 3, "offense"), ("OT", 3, "offense"),
    ("OG", 3, "offense"), ("C", 2, "offense"), ("DE", 4, "defense"),
    ("DT", 3, "defense"), ("OLB", 3, "defense"), ("ILB", 3, "defense"),
    ("CB", 5, "defense"), ("S", 4, "defense"), ("K", 1, "special_teams"),
    ("P", 1, "special_teams"), ("LS", 1, "special_teams"),
)


def game_day_roster(prefix):
    roster = []
    for position, count, unit in LAYOUT:
        for depth in range(1, count + 1):
            roster.append(PlayerInput(
                f"{prefix}-{position}{depth}", position, unit=unit,
                depth=depth, rotation_status="core" if depth == 1 else "competition",
            ))
    return tuple(roster)
