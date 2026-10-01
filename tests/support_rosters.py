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


def single_quarterback_teams():
    """The production-runner fixture of tests/test_game_runner.py: one
    quarterback, one unavailable receiver and a 46-man legal unit on both
    clubs, so a removed passer is replaced by an emergency filler."""
    from runtime.kernel import TeamInput
    roster = (PlayerInput("qb", "QB", roles=("passer",), rotation_status="competition"),
              PlayerInput("rb", "RB", roles=("rusher",), rotation_status="bubble"),
              PlayerInput("wr", "WR", roles=("receiver",)),
              PlayerInput("ot", "OT", roles=("pass_protection",)),
              PlayerInput("lb", "LB", unit="defense", roles=("punt_coverage",)),
              PlayerInput("out", "WR", available=False))
    # 2013: at most 46 game-day actives (the deepest fill spares are left off).
    spares = {"fill-WR5", "fill-CB5", "fill-S4", "fill-RB3"}
    roster += tuple(p for p in game_day_roster("fill") if p.position != "QB" and p.player_id not in spares)
    active = tuple(p.player_id for p in roster if p.available)
    return TeamInput("A", active, roster=roster), TeamInput("B", active, roster=roster)
