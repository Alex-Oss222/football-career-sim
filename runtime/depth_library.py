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
    """A kernel TeamInput dict for one background club's game-day unit in `week`.

    Before the season's in-season rails effective week the unit is the
    club's Week 1 library entry. From that week there is one source of a
    background unit: the weekly slate replay (`runtime.week_inputs.rails_slate`,
    with its branch reserve placements, emergency promotions and slate
    deferral), so this function refuses rather than return a second,
    inconsistent roster (engineering review S2)."""
    from . import rails
    data = rails.load(season)
    if data is not None and int(week) >= data.effective_from_week:
        raise ValueError("Week %d of %d uses the in-season rails: build background units from the weekly "
                         "slate (runtime.week_inputs.rails_slate), not depth_library.team_input" % (week, season))
    club = load(SeasonPaths(season).background_depth)["clubs"][team]
    return club_input(team, club, offense_anchor=offense_anchor, defense_anchor=defense_anchor,
                      special_teams_anchor=special_teams_anchor, week=week)


@lru_cache(maxsize=4)
def _db_families(path):
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def db_families(season):
    """The season's defensive-back families (kernel 2014.6 batch B15, W2b;
    library/data/YEAR_db_families.json, scripts/research/build_2014_db_families.py),
    or None when the season has none."""
    return _db_families(str(SeasonPaths(season).db_families))


def db_families_errors(season, root=None):
    """Review fix (October 16, 2026): the season's defensive-back family table
    must be built against the in-season rails manifest now committed (the
    rails grow with each week's backlog, and a newcomer the table does not
    hold would keep his rails position unnoticed). [] when it matches or the
    season has no table."""
    from . import rails
    paths = SeasonPaths(season, root) if root is not None else SeasonPaths(season)
    if not paths.db_families.is_file():
        return []
    data = json.loads(paths.db_families.read_text(encoding="utf-8"))
    pinned = (data.get("sources", {}).get("inseason_rails_manifest") or {}).get("sha256")
    manifest = rails.data_dir(season, paths.root) / "manifest.json"
    if not manifest.is_file():
        return []
    if pinned != rails.sha256_file(manifest):
        return ["%s was built against another in-season rails manifest (%s); rebuild it with "
                "python scripts/research/build_2014_db_families.py before building the week's inputs"
                % (paths.db_families.relative_to(paths.root).as_posix(), (pinned or "none")[:12])]
    return []


def relabel_defensive_backs(club, season, report=None):
    """One background club entry (the rails schema, players with gsis ids)
    with its defensive backs' contemporaneous labels (W2b): each player of
    the DB group whose gsis id the season's family table holds takes its
    label (CB for a corner; a safety keeps his SS, FS or S), and a player the
    club's own Week 1 chart lists at nickel takes the ``nickel`` role. A
    player the table does not hold keeps the rails' stated position (counted
    in ``report``). Nothing else changes; read only from the in-season rails'
    first week under a kernel that seats defensive backs by family
    (runtime.week_inputs.build_package), so the Week 1 library, Weeks 1 to 4
    and every earlier package are unchanged."""
    data = db_families(season)
    if data is None:
        raise ValueError("no %d defensive-back family table (library/data/%d_db_families.json); "
                         "the DB seats cannot be read" % (season, season))
    stale = db_families_errors(season)
    if stale:
        raise ValueError(stale[0])
    players = data["players"]
    nickels = set(data.get("nickel", {}).get(club.get("code"), ()))
    out = []
    for p in club["players"]:
        row = dict(p)
        if group(p["position"]) == "DB":
            rec = players.get(p.get("gsis_id"))
            if rec is not None:
                if report is not None and rec["position"] != p["position"]:
                    report.setdefault("relabelled", []).append(
                        {"player_id": p["player_id"], "from": p["position"], "to": rec["position"],
                         "basis": rec["basis"]})
                row["position"] = rec["position"]
            elif report is not None:
                report.setdefault("unlisted", []).append(p["player_id"])
            if p.get("gsis_id") in nickels and "nickel" not in (p.get("roles") or ()):
                row["roles"] = list(p.get("roles") or ()) + ["nickel"]
        out.append(row)
    return dict(club, players=out)


def club_input(team, club, *, offense_anchor, defense_anchor, special_teams_anchor, week=1):
    """The same TeamInput from one club entry (the library's schema), wherever
    it is stored: the Week 1 library or a preseason opponent roster file."""
    if not isinstance(club, dict) or not isinstance(club.get("players"), list) or not club["players"]:
        raise ValueError("club entry for %s requires a nonempty players list" % team)
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
