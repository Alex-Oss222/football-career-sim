"""Background-club TeamInputs from the sourced 2013 Week 1 depth-chart library.

`library/data/2013_week1_depth_charts.json` holds the 31 non-Jacksonville
clubs' Week 1 game-day units, already reconciled to branch control (see
`library/2013_week1_depth_charts.md`). Jacksonville's input always comes from
the branch roster and Stone's staff, never from this library.

Unit anchors are not stored here: they are resolution inputs under Document 7
section 2.2 and are passed in explicitly by the caller.
"""
import json
from functools import lru_cache
from pathlib import Path

from .usage import group
from .seasons import SeasonPaths

LIBRARY = Path(__file__).resolve().parents[1] / "library" / "data" / "2013_week1_depth_charts.json"
UNIT = {"QB": "offense", "RB": "offense", "FB": "offense", "WR": "offense", "TE": "offense",
        "OL": "offense", "DL": "defense", "LB": "defense", "DB": "defense",
        "K": "special teams", "P": "special teams", "LS": "special teams"}


@lru_cache(maxsize=1)
def load(path=LIBRARY):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def clubs():
    return tuple(load()["clubs"])


def available(player, week):
    """Week 1 report availability; a pre-existing injury ends at its return week."""
    if player.get("available", True):
        return True
    return bool(player.get("return_week")) and week >= player["return_week"]


def team_input(team, *, offense_anchor, defense_anchor, special_teams_anchor, week=1, season=2013):
    """A kernel TeamInput dict for one background club's game-day unit in `week`."""
    club = load(SeasonPaths(season).background_depth)["clubs"][team]
    roster = []
    for player in club["players"]:
        roster.append({
            "player_id": player["player_id"],
            "position": player["position"],
            "available": available(player, week),
            "unit": UNIT.get(group(player["position"]), "offense"),
            "roles": tuple(player.get("roles", ())),
            "depth": player["depth"],
        })
    return {
        "team_id": team,
        "active_players": [p["player_id"] for p in roster if p["available"]],
        "offense_anchor": offense_anchor,
        "defense_anchor": defense_anchor,
        "special_teams_anchor": special_teams_anchor,
        "roster": roster,
    }
