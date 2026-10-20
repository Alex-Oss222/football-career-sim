"""A club's game in a season week, regular season or postseason (game week version 2, Phase C).

The game-week pages (scripts/render_game_week.py, check_game_plan.py,
apply_game_plan.py and open_game_week.py) find Jacksonville's game here, so a
playoff game goes through the same three pages as a season game
(docs/game_week_v2.md, section 7).

- A regular-season week reads the released fixtures (SeasonPaths.regular_games).
- A postseason week (a round of runtime.postseason.ROUNDS after the season's
  last regular-season week) reads the bracket runtime.postseason.schedule
  builds from the closed games only, seated on the season's postseason slots
  file (SeasonPaths.postseason_slots: the real dates, kickoff times and sites,
  researched in two passes like every calendar). The Wild Card round is set
  once every regular-season fixture has closed; each later round once every
  game of the round before it has closed. Until then the round raises
  ``NotSet``: no opponent is named before the bracket sets it.
- A club seeded for a first-round bye has no Wild Card game; a club outside
  the field, or beaten in a round, has no later game (``next_postseason_game``
  says why). A postseason game never ends tied (runtime/rules.py).

A postseason game is returned in the shape of a regular-season fixture (its
week, date, weekday, kickoff, clubs and stadium; a home club's site is its
latest regular-season home stadium unless the slot names a venue) with the
round, the conference and both seeds beside it. Nothing here writes, moves the
clock or creates an event.
"""
from __future__ import annotations

import json
from datetime import date

from . import postseason
from .seasons import SeasonPaths

ROUND_NAMES = {"wild_card": "Wild Card", "divisional": "Divisional", "conference": "Conference Championship",
               "super_bowl": "Super Bowl"}
NEXT_ROUND = {"wild_card": "divisional", "divisional": "conference", "conference": "super_bowl"}
FIRST_ROUND = min(postseason.ROUNDS)
# Seeds with a first-round bye (library/2013_postseason_format_and_schedule.md, F3; unchanged in 2014).
BYE_SEEDS = (1, 2)


class NotSet(ValueError):
    """A postseason round the bracket cannot set yet, in football words."""


def _paths(paths_or_year, root=None):
    if isinstance(paths_or_year, SeasonPaths):
        return paths_or_year
    return SeasonPaths(paths_or_year) if root is None else SeasonPaths(paths_or_year, root)


def last_regular_week(paths):
    return max(int(g["week"]) for g in paths.regular_games())


def is_postseason(paths, week):
    """Whether ``week`` is a postseason round of the season (after its last regular-season week)."""
    week = int(week)
    if week not in postseason.ROUNDS:
        return False
    try:
        return week > last_regular_week(paths)
    except (OSError, ValueError, KeyError):
        return True


def round_name(week):
    return ROUND_NAMES[postseason.ROUNDS[int(week)]]


def label(game):
    """The game's name in football words: "Week 6", or the round ("Wild Card")."""
    if game.get("game_type") == "postseason":
        return game["round_name"]
    return "Week %d" % int(game["week"])


def _load(folder):
    if not folder.is_dir():
        return []
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(folder.glob("*.json"))]


def regular_receipts(paths):
    """The closed regular-season games: each closed-game record that matches a released fixture."""
    fixtures = {(int(g["week"]), g["away"], g["home"]) for g in paths.regular_games()}
    return [r for r in _load(paths.receipts) if (int(r["week"]), r["away"], r["home"]) in fixtures]


def postseason_receipts(paths):
    return [r for r in _load(paths.postseason_receipts) if postseason.is_postseason(r["week"])]


def closed_receipt(receipts, game):
    """The closed record of ``game`` among ``receipts``, or None."""
    return next((r for r in receipts if int(r["week"]) == int(game["week"]) and r["away"] == game["away"]
                 and r["home"] == game["home"]), None)


def home_stadium(paths, club):
    """The club's latest regular-season home stadium on the released fixtures: the season's, or, for a
    club with no home game in them, the season before's."""
    for year in (paths.year, paths.year - 1):
        try:
            games = SeasonPaths(year, paths.root).regular_games()
        except (OSError, ValueError, KeyError):
            continue
        rows = sorted((g for g in games if g["home"] == club and g.get("site", "home") == "home"
                       and g.get("stadium")), key=lambda g: g["date"])
        if rows:
            return rows[-1]["stadium"]
    return None


def fixture(paths, game):
    """A bracket game (runtime.postseason) in the shape of a regular-season fixture."""
    from .week_inputs import event_id
    when = date.fromisoformat(game["date"])
    site = game.get("site", "home")
    return {"game_id": event_id(game, season=paths.year), "week": int(game["week"]), "date": game["date"],
            "weekday": when.strftime("%A"), "kickoff_et": game.get("kickoff_et"), "away": game["away"],
            "home": game["home"], "site": site,
            "stadium": game.get("venue") or (home_stadium(paths, game["home"]) if site == "home" else None),
            "game_type": "postseason", "round": game["round"], "round_name": ROUND_NAMES[game["round"]],
            "conference": game["conference"], "away_seed": game.get("away_seed"),
            "home_seed": game.get("home_seed"), "network": game.get("network")}


def bracket(paths, week, regular=None, post=None):
    """The games of postseason round ``week``, as fixtures, in slot order. ``NotSet`` (in football
    words) when the round cannot be set yet: the regular season unfinished, the season's postseason
    dates not on file, or a game of the round before it still to be played."""
    week = int(week)
    if not is_postseason(paths, week):
        raise ValueError("Week %d is not a postseason round of the %d season" % (week, paths.year))
    name = round_name(week)
    regular = regular_receipts(paths) if regular is None else regular
    closed = {(int(r["week"]), r["away"], r["home"]) for r in regular}
    if any((int(g["week"]), g["away"], g["home"]) not in closed for g in paths.regular_games()):
        raise NotSet("the %s games are set once the regular season has finished" % name)
    if not paths.postseason_slots.is_file():
        raise NotSet("the %d postseason dates are not on file yet; the %s games are seated on them"
                     % (paths.year, name))
    slots = json.loads(paths.postseason_slots.read_text(encoding="utf-8"))
    post = postseason_receipts(paths) if post is None else post
    try:
        games = postseason.schedule(week, regular, post, slots, season=paths.year)
    except ValueError as exc:
        if "closed games" not in str(exc):
            raise
        raise NotSet("the %s games are set once every game of the round before it has been played" % name) from exc
    return [fixture(paths, g) for g in games]


def seed_of(regular, club):
    """(conference, seed) of ``club`` in the playoff field the regular season set, or None."""
    field = postseason.seeds(regular)
    for conference, clubs in field.items():
        if club in clubs:
            return conference, clubs.index(club) + 1
    return None


def club_game(paths_or_year, week, club, root=None):
    """The club's game in ``week``, as a fixture, or None when it has none that week (a bye, a club
    outside the field). A postseason round the bracket cannot set yet raises ``NotSet``."""
    paths = _paths(paths_or_year, root)
    week = int(week)
    if is_postseason(paths, week):
        return next((g for g in bracket(paths, week) if club in (g["away"], g["home"])), None)
    return next((g for g in paths.regular_games() if int(g["week"]) == week and club in (g["away"], g["home"])),
                None)


def next_postseason_game(paths_or_year, club, root=None):
    """(game, why): the club's next postseason game not yet played, or (None, the football reason
    there is none: the field not set, the club outside it or beaten, a round still awaiting the
    results before it). A first-round bye passes to the round after it."""
    paths = _paths(paths_or_year, root)
    regular = regular_receipts(paths)
    post = postseason_receipts(paths)
    for week in sorted(postseason.ROUNDS):
        if not is_postseason(paths, week):
            continue
        try:
            games = bracket(paths, week, regular, post)
        except NotSet as exc:
            return None, str(exc)
        ours = next((g for g in games if club in (g["away"], g["home"])), None)
        if ours is None:
            seeded = seed_of(regular, club)
            if week == FIRST_ROUND and seeded and seeded[1] in BYE_SEEDS:
                continue
            return None, ("not in the playoff field" if week == FIRST_ROUND and not seeded
                          else "the season is over")
        played = closed_receipt(post, ours)
        if played is None:
            return ours, None
        if postseason.winner(played) != club:
            return None, "beaten in the %s round; the season is over" % ours["round_name"]
    return None, "the season is over"


def club_games(paths_or_year, club, root=None):
    """Every game of the club the stored facts set, regular season then postseason, by date: its
    released fixtures and each postseason game the bracket has set (a round not yet set ends the
    list)."""
    paths = _paths(paths_or_year, root)
    games = [g for g in paths.regular_games() if club in (g["away"], g["home"])]
    regular = None
    for week in sorted(postseason.ROUNDS):
        if not is_postseason(paths, week):
            continue
        if regular is None:
            regular = regular_receipts(paths)
        try:
            ours = next((g for g in bracket(paths, week, regular) if club in (g["away"], g["home"])), None)
        except NotSet:
            break
        if ours is not None:
            games.append(ours)
    return sorted(games, key=lambda g: (g["date"], int(g["week"])))
