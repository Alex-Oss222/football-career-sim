"""Weekly TeamInput package for any regular-season week.

- Slate: `library/data/2013_schedule.json` (schedule rails only).
- Background clubs: the sourced Week 1 units (`runtime.depth_library`),
  carried forward. Later real depth charts are not read: they reflect real
  games' injuries and results, which the branch never had. A player already
  out before Week 1 returns at the library's `return_week`.
- Availability: every injury in a closed receipt keeps its player out until
  the injury date plus its projected return days; Jacksonville's own medical
  holds come from `career/2013/roster.md`.
- Jacksonville: the controlled active roster, `career/2013/depth_chart.json`
  (order, roles, inactives) and the week's structured call sheet.

Unit anchors are passed in explicitly (Document 7 section 2.2).
"""
import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path

from . import call_families, depth_library, player_bios
from .usage import group, lineup_errors
from .seasons import SeasonPaths, require_receipt_season

ROOT = Path(__file__).resolve().parents[1]
SCHEDULE = ROOT / "library" / "data" / "2013_schedule.json"
ROSTER = ROOT / "career" / "2013" / "roster.md"
DEPTH_CHART = ROOT / "career" / "2013" / "depth_chart.json"
PROTAGONIST = "Jacksonville Jaguars"
AVAILABLE_TEXT = "No communicated restriction"
GAME_DAY_ACTIVES = 46
LIMITED_TEXT = "Limited, no projected absence"
UNIT = depth_library.UNIT


def slug(team, sep):
    return re.sub(r"[^a-z0-9]+", sep, team.lower()).strip(sep)


def schedule(week, season=2013):
    from . import postseason
    if postseason.is_postseason(week):
        # Weeks 18-21: the bracket built from closed receipts (runtime.postseason).
        return postseason.schedule(week, season=season)
    games = [g for g in SeasonPaths(season, ROOT).regular_games() if g["week"] == week]
    if not games:
        raise ValueError("no %d schedule for week %s" % (season, week))
    return games


GENERATIONS = ROOT / "career/2013/migrations/event_generations.json"


def event_generation(week, season=2013):
    """The current event generation for a week: 1 unless a user-authorized
    void in career/2013/migrations/event_generations.json replaced it."""
    generations = SeasonPaths(season, ROOT).generations
    if not generations.exists():
        return 1
    weeks = json.loads(generations.read_text(encoding="utf-8")).get("weeks", {})
    return int(weeks.get(str(int(week)), {}).get("current_generation", 1))


def event_id(game, generation=None, season=2013):
    generation = event_generation(game["week"], season) if generation is None else generation
    base = "%d-week%02d-%s-at-%s" % (season, game["week"], slug(game["away"], "-"), slug(game["home"], "-"))
    return base if generation == 1 else "%s-g%d" % (base, generation)


def receipt_name(game):
    return "week_%02d_%s_at_%s.json" % (game["week"], slug(game["away"], "_"), slug(game["home"], "_"))


def _game_dates(season=2013):
    from . import postseason
    games = SeasonPaths(season, ROOT).regular_games()
    dates = {(g["week"], g["away"], g["home"]): date.fromisoformat(g["date"]) for g in games}
    # Closed postseason rounds: their games can always be rebuilt from receipts.
    for week in sorted(postseason.ROUNDS):
        try:
            rows = postseason.schedule(week, season=season)
        except (ValueError, FileNotFoundError, KeyError):
            break
        dates.update({(g["week"], g["away"], g["home"]): date.fromisoformat(g["date"]) for g in rows})
    return dates


def injured_out(receipts, game_day, season=2013):
    """{player_id: reason} for players still inside their projected return window."""
    require_receipt_season(receipts, season)
    dates = _game_dates(season)
    out = {}
    for receipt in receipts:
        played = dates[(int(receipt["week"]), receipt["away"], receipt["home"])]
        for injury in receipt.get("injuries", ()):
            days = injury.get("return_days") or 0
            if injury.get("restriction") == "limited" and not days:
                continue
            back = played + timedelta(days=days)
            if game_day < back:
                out[injury["player"]] = "%s (%s), projected return %s" % (
                    injury.get("restriction"), injury.get("injury_class"), back.isoformat())
    return out


def background_input(team, week, receipts, game_day, anchors, season=2013):
    team_input = depth_library.team_input(team, week=week, season=season, **anchors)
    out = injured_out(receipts, game_day, season)
    for player in team_input["roster"]:
        if player["player_id"] in out:
            player["available"] = False
    team_input["active_players"] = game_day_actives(team_input["roster"])
    return team_input


GAME_DAY_ACTIVE_LIMIT = 46


def game_day_actives(roster):
    """A background club's 46 game-day actives, chosen mechanically from depth.

    No club's real inactive list is imported. While more than 46 players are
    available, the deepest-ranked player in the club's depth order is made
    inactive (the larger position group first on a tie), never below a legal
    game-day unit. Jacksonville's inactives are Stone's decision instead.
    """
    rows = [p for p in roster if p["available"]]
    sizes = {}
    for p in rows:
        sizes[group(p["position"])] = sizes.get(group(p["position"]), 0) + 1
    def deepest_first(item):
        index, p = item
        depth = p.get("depth") if isinstance(p.get("depth"), int) else 99
        return (-depth, -sizes.get(group(p["position"]), 0), -index)
    order = [p for _, p in sorted(enumerate(rows), key=deepest_first)]
    active = list(rows)
    for candidate in order:
        if len(active) <= GAME_DAY_ACTIVE_LIMIT:
            break
        trial = [p for p in active if p is not candidate]
        if not lineup_errors([_Row(p) for p in trial]):
            active = trial
    return [p["player_id"] for p in active]


class _Row:
    def __init__(self, row):
        self.position = row["position"]


def controlled_active(season=2013, roster_path=None):
    """(player, availability text) for every Jacksonville active-53 player."""
    rows = []
    status_col = avail_col = None
    path = roster_path or SeasonPaths(season, ROOT).roster
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            status_col = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if "Player" in cells:
            status_col = cells.index("Status") if "Status" in cells else None
            avail_col = cells.index("Availability") if "Availability" in cells else None
            continue
        if status_col is None or set(cells[0]) <= {"-", ":"}:
            continue
        if cells[status_col] == "Active 53":
            rows.append((cells[0], cells[avail_col] if avail_col is not None else AVAILABLE_TEXT))
    return rows


HOLD_NOTE = re.compile(r"\b(Out|hold|Suspended|Reserve|Non-football|Exempt)\b", re.IGNORECASE)
PROJECTED_RETURN = re.compile(r"projected return ([A-Z][a-z]+ \d{1,2}(?:, \d{4})?)")


def roster_available(availability, game_day, season=2013):
    """Whether a roster availability note clears a player for `game_day`.

    A game injury recorded with a projected return clears on that date, the
    rule every background club gets; a hold without a date (a medical hold,
    a suspension) clears only when the roster entry is changed. A player
    listed as limited with no projected absence plays, as for every club.
    """
    if availability.startswith(AVAILABLE_TEXT) or availability.startswith(LIMITED_TEXT):
        return True
    match = PROJECTED_RETURN.search(availability)
    if not match:
        if not HOLD_NOTE.search(availability):
            # A note that is neither clear, limited, dated nor an explicit
            # hold is a data defect, not a hold: fail the build (Entry 57).
            raise ValueError("unrecognized availability note: %r" % availability)
        return False
    text = match.group(1)
    if season != 2013 and "," not in text:
        raise ValueError('New-season projected returns require an explicit year')
    back = datetime.strptime(text if "," in text else text + ", 2013", "%B %d, %Y").date()
    return game_day >= back


def jacksonville_input(receipts, game_day, anchors, call_sheet, season=2013):
    undeclared = call_families.sheet_errors(call_sheet)
    if undeclared:
        # Kernel 2013.7 fails closed on a call no label rule covers.
        raise ValueError("call sheet cannot be labelled: " + "; ".join(undeclared))
    chart = json.loads(SeasonPaths(season, ROOT).depth_chart.read_text(encoding="utf-8"))
    depth = {player: rank for players in chart["depth"].values() for rank, player in enumerate(players, 1)}
    injured = injured_out(receipts, game_day, season)
    inactives = set(chart["game_day_inactives"]["players"])
    roster, missing = [], []
    for player, availability in controlled_active(season):
        if player not in depth:
            missing.append(player)
            continue
        position = chart["positions"][player]
        cleared = roster_available(availability, game_day, season)
        roster.append({
            "player_id": player, "position": position,
            "available": cleared and player not in injured,
            "unit": UNIT[group(position)], "roles": chart["roles"].get(player, []),
            "depth": depth[player],
            "medical_limitation": None if cleared else availability,
        })
    if missing:
        raise ValueError("depth_chart.json does not place: " + ", ".join(missing))
    active = [p["player_id"] for p in roster if p["available"] and p["player_id"] not in inactives]
    healthy_inactive = [p["player_id"] for p in roster if p["available"] and p["player_id"] in inactives]
    if len(active) < GAME_DAY_ACTIVES and healthy_inactive:
        # 2013 clubs dress 46 while healthy players remain: an unavailable
        # player missing from Stone's inactive list is a plan gap to resolve
        # before the draw, never a silent 45-man unit (Entry 57).
        unlisted = [p["player_id"] for p in roster if not p["available"] and p["player_id"] not in inactives]
        raise ValueError("Jacksonville would dress %d, not %d: unavailable but not listed inactive: %s; "
                         "healthy inactives: %s" % (len(active), GAME_DAY_ACTIVES, ", ".join(unlisted) or "none",
                                                     ", ".join(healthy_inactive)))
    return {
        "team_id": PROTAGONIST,
        "active_players": active,
        **anchors, "roster": roster, "offensive_call_sheet": list(call_sheet),
    }


def build_package(week, receipts, call_sheet, anchors, season=2013):
    games = []
    birth_dates = player_bios.load()
    for game in schedule(week, season):
        game_day = date.fromisoformat(game["date"])

        def unit(team):
            if team == PROTAGONIST:
                return jacksonville_input(receipts, game_day, anchors, call_sheet, season)
            return background_input(team, week, receipts, game_day, anchors, season)

        games.append({
            "event_id": event_id(game, season=season), "receipt": receipt_name(game), "week": week,
            "date": game["date"], "away": game["away"], "home": game["home"],
            "venue": "neutral" if game["site"] == "neutral" else "home",
            "game_type": game.get("game_type", "regular"),
            **{key: game[key] for key in ("round", "conference", "matchup", "kickoff_et", "network",
                                          "away_seed", "home_seed") if key in game},
            "away_input": unit(game["away"]), "home_input": unit(game["home"]),
        })
        # Public preparation metadata, deliberately outside TeamInput and the
        # outcome packet. Birthdays cannot reroll already-frozen football.
        games[-1]["player_ages"] = player_bios.biographies(
            [p["player_id"] for side in ("away_input", "home_input")
             for p in games[-1][side]["roster"]], game_day, birth_dates)
    return {"season": season, "week": week, "games": games}
