"""Background-club TeamInputs from the sourced 2013 Week 1 depth-chart library.

`library/data/2013_week1_depth_charts.json` holds the 31 non-Jacksonville
clubs' Week 1 game-day units, already reconciled to branch control (see
`library/2013_week1_depth_charts.md`). Jacksonville's input always comes from
the branch roster and Stone's staff, never from this library.

Unit anchors are not stored here: they are resolution inputs under Document 7
section 2.2 and are passed in explicitly by the caller.

The library is season-specific (`library/data/{season}_week1_depth_charts.json`,
resolved by `runtime.season`). A season without its own library fails
closed; the 2013 units never stand in for another season's clubs.
"""
import json
from functools import lru_cache
from pathlib import Path

from .season import DEFAULT_SEASON, season_paths
from .usage import group

LIBRARY = Path(__file__).resolve().parents[1] / "library" / "data" / "2013_week1_depth_charts.json"
UNIT = {"QB": "offense", "RB": "offense", "FB": "offense", "WR": "offense", "TE": "offense",
        "OL": "offense", "DL": "defense", "LB": "defense", "DB": "defense",
        "K": "special teams", "P": "special teams", "LS": "special teams"}


@lru_cache(maxsize=4)
def load(path=LIBRARY):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def season_library(season=DEFAULT_SEASON, root=None):
    """The parsed library for one season; SeasonDataMissing when it does not exist."""
    paths = season_paths(season, root)
    data = load(paths.require("depth_library"))
    if data.get("season") != season:
        raise ValueError("%s declares season %r, not %d" % (paths.depth_library.name, data.get("season"), season))
    return data


def clubs(season=DEFAULT_SEASON, root=None):
    return tuple(season_library(season, root)["clubs"])


def available(player, week):
    """Week 1 report availability; a pre-existing injury ends at its return week."""
    if player.get("available", True):
        return True
    return bool(player.get("return_week")) and week >= player["return_week"]


def team_input(team, *, offense_anchor, defense_anchor, special_teams_anchor, week=1,
               season=DEFAULT_SEASON, root=None):
    """A kernel TeamInput dict for one background club's game-day unit in `week`."""
    club = season_library(season, root)["clubs"][team]
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
