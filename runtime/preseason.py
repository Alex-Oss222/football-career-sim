"""Preseason game package: one dated fixture, two TeamInputs, the same kernel.

A preseason game closes through the production runner exactly as a
regular-season game does (runtime.game_runner.run_game, kernel
``game_type="preseason"``). What differs is only its inputs and storage:

- Fixture: `SeasonPaths.preseason_games()` (schedule facts only).
- Jacksonville: the current branch roster (every player the club controls
  on its offseason/active roster), the game's frozen depth chart
  (`Game_0N/depth_chart.json`, the released season chart's schema; the
  released `depth_chart.json` when no game chart is frozen) and the game's
  frozen call sheet `Game_0N/call_sheet.json` ({"offensive_call_sheet": [...]},
  the regular-season schema). A preseason game may dress the whole roster
  (runtime.rules.active_limit); `game_day_inactives` names who does not.
- Opponent: `Game_0N/opponent_roster.json`, one club entry in the schema of
  `library/data/YEAR_week1_depth_charts.json` (`players` with player_id,
  position, depth, roles, available/return_week), read by the same
  depth-library code as every background club.
- Availability: a player injured in an earlier closed preseason receipt
  stays out until his projected return, by the rule every club gets; a
  Jacksonville roster hold clears by its own note (runtime.week_inputs).
- Rotation (runtime/rotation.py): Jacksonville's unit rotation comes from
  `Game_0N/rotation.json` ({"rotation_plan": [blocks...]}) when Stone froze
  one; the opponent's from a `rotation` key in `opponent_roster.json`. A
  club without a plan gets the kernel's documented default (starters through
  the first quarter and the first possession of the second, the second unit
  through the third quarter, reserves after) from its depth order. A plan
  naming a player off the game-day unit or an unknown group fails closed
  here, before the package is frozen.
- Receipts go to `SeasonPaths.preseason_receipts`, never the regular-season
  receipt set, so standings, the statbook, awards and the draft order never
  read them.
- Ages: the `player_ages` sidecar (outside TeamInput and the packet) needs a
  verified birth date for every Jacksonville player; an opponent camp player
  with no public identity record enters with `age: null` and
  `age_unverified: true`, and the receipt lists those names.
"""
import json
from datetime import date, timedelta

from . import call_families, depth_library, player_bios, rotation, strength
from .player_evidence import normalize_players
from .rules import PRESEASON
from .seasons import SeasonPaths, require_receipt_season
from .usage import group
from .week_inputs import (AVAILABLE_TEXT, PROTAGONIST, UNIT, controlled_active, roster_available, slug)

CONTROLLED_STATUSES = ("Active", "Offseason roster")
AVERAGE_ANCHORS = {"offense_anchor": 2.0, "defense_anchor": 2.0, "special_teams_anchor": 2.0}


def event_id(game, season):
    """The fixture's own id: YEAR-preseason-NN-away-at-home (checked by SeasonPaths)."""
    expected = "%d-preseason-%02d-%s-at-%s" % (season, game["game"], slug(game["away"], "-"), slug(game["home"], "-"))
    if game.get("game_id") != expected:
        raise ValueError("preseason fixture id must be " + expected)
    return expected


def receipt_name(game):
    return "preseason_%02d_%s_at_%s.json" % (game["game"], slug(game["away"], "_"), slug(game["home"], "_"))


def controlled_roster(roster_path):
    """(player, availability text) for every player on Jacksonville's roster
    in camp: the offseason roster, or the active roster after the cuts.
    Reserve lists, the practice squad and reserve/future players are not
    game-day candidates."""
    rows = controlled_active(roster_path=roster_path)
    status_col = avail_col = None
    for line in roster_path.read_text(encoding="utf-8").splitlines():
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
        status = cells[status_col]
        if status != "Active 53" and status.startswith(CONTROLLED_STATUSES):
            rows.append((cells[0], cells[avail_col] if avail_col is not None else AVAILABLE_TEXT))
    names = [name for name, _ in rows]
    if len(set(names)) != len(names):
        raise ValueError("roster lists a player twice: " + ", ".join(sorted({n for n in names if names.count(n) > 1})))
    return rows


def injured_out(receipts, game_day, paths):
    """{player_id: reason} from earlier closed preseason receipts, dated by the fixtures."""
    require_receipt_season(receipts, paths.year)
    dates = {g["game_id"]: date.fromisoformat(g["date"]) for g in paths.preseason_games()}
    out = {}
    for receipt in receipts:
        played = dates[receipt["event_id"]]
        for injury in receipt.get("injuries", ()):
            days = injury.get("return_days") or 0
            if injury.get("restriction") == "limited" and not days:
                continue
            back = played + timedelta(days=days)
            if game_day < back:
                out[injury["player"]] = "%s (%s), projected return %s" % (
                    injury.get("restriction"), injury.get("injury_class"), back.isoformat())
    return out


def rotation_blocks(plan, data, source):
    """Validate a rotation plan against the game-day unit; returns the
    entries to freeze on the TeamInput (every block must name dressed players
    of the named group; an unknown group or side fails closed)."""
    if not isinstance(plan, list) or not all(isinstance(e, dict) for e in plan):
        raise ValueError("%s: rotation_plan must be a list of blocks" % source)
    from .kernel import TeamInput
    team = TeamInput(data["team_id"], tuple(data["active_players"]), roster=tuple(data["roster"]),
                     rotation_plan=tuple(plan))
    errors = rotation.plan_errors(team, normalize_players(team), PRESEASON)
    if errors:
        raise ValueError("%s: " % source + "; ".join(errors))
    if not any(rotation.is_block(e) for e in plan):
        raise ValueError("%s: no rotation block found" % source)
    return list(plan)


def depth_chart_path(paths, game):
    frozen = paths.preseason_folder(game) / "depth_chart.json"
    if frozen.exists():
        return frozen
    if paths.depth_chart.exists():
        return paths.depth_chart
    raise ValueError("No depth chart for preseason game %d: freeze Stone's order as %s "
                     "(the released season chart's schema)" % (game, frozen.relative_to(paths.root)))


def jacksonville_input(paths, game, call_sheet, receipts, anchors=AVERAGE_ANCHORS):
    undeclared = call_families.sheet_errors(call_sheet)
    if undeclared:
        raise ValueError("call sheet cannot be labelled: " + "; ".join(undeclared))
    chart = json.loads(depth_chart_path(paths, game["game"]).read_text(encoding="utf-8"))
    depth = {player: rank for players in chart["depth"].values() for rank, player in enumerate(players, 1)}
    game_day = date.fromisoformat(game["date"])
    injured = injured_out(receipts, game_day, paths)
    inactives = set(((chart.get("game_day_inactives") or {}).get("players")) or ())
    roster, missing = [], []
    for player, availability in controlled_roster(paths.roster):
        if player not in depth:
            missing.append(player)
            continue
        position = chart["positions"][player]
        cleared = roster_available(availability, game_day, paths.year)
        roster.append({
            "player_id": player, "position": position,
            "available": cleared and player not in injured,
            "unit": UNIT[group(position)], "roles": chart["roles"].get(player, []),
            "depth": depth[player],
            "medical_limitation": None if cleared else availability,
        })
    if missing:
        raise ValueError("the depth chart does not place: " + ", ".join(missing))
    unknown = sorted(inactives - {p["player_id"] for p in roster})
    if unknown:
        raise ValueError("game_day_inactives names players not on the roster: " + ", ".join(unknown))
    active = [p["player_id"] for p in roster if p["available"] and p["player_id"] not in inactives]
    data = {"team_id": PROTAGONIST, "active_players": active, **anchors,
            "roster": roster, "offensive_call_sheet": list(call_sheet)}
    plan_path = paths.preseason_folder(game["game"]) / "rotation.json"
    if plan_path.exists():
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        if not isinstance(plan, dict) or "rotation_plan" not in plan:
            raise ValueError("%s must hold {\"rotation_plan\": [...]}" % plan_path.relative_to(paths.root))
        data["rotation_plan"] = rotation_blocks(plan["rotation_plan"], data, plan_path.relative_to(paths.root))
    return data


def opponent_input(paths, game, receipts, anchors=AVERAGE_ANCHORS):
    team = game["away"] if game["home"] == PROTAGONIST else game["home"]
    path = paths.preseason_folder(game["game"]) / "opponent_roster.json"
    if not path.exists():
        raise ValueError("No opponent roster for preseason game %d: %s" % (game["game"], path.relative_to(paths.root)))
    club = json.loads(path.read_text(encoding="utf-8"))
    if club.get("team") not in (None, team):
        raise ValueError("opponent roster names %s, not %s" % (club.get("team"), team))
    data = depth_library.club_input(team, club, week=1, **anchors)
    out = injured_out(receipts, date.fromisoformat(game["date"]), paths)
    for player in data["roster"]:
        if player["player_id"] in out:
            player["available"] = False
    data["active_players"] = [p["player_id"] for p in data["roster"] if p["available"]]
    if "rotation" in club:
        data["rotation_plan"] = rotation_blocks(club["rotation"], data, "%s rotation" % path.relative_to(paths.root))
    return data


def build_package(paths, number, receipts, anchors=AVERAGE_ANCHORS, *, with_ages=True):
    """The one-game package for preseason game `number` (close_preseason_game.py)."""
    game = paths.preseason_game(number)
    if PROTAGONIST not in (game["away"], game["home"]):
        raise ValueError("preseason fixtures are Jacksonville's games")
    sheet_path = paths.preseason_folder(number) / "call_sheet.json"
    if not sheet_path.exists():
        raise ValueError("No Jacksonville call sheet for preseason game %d: freeze Stone's plan as %s"
                         % (number, sheet_path.relative_to(paths.root)))
    call_sheet = json.loads(sheet_path.read_text(encoding="utf-8"))["offensive_call_sheet"]
    prior = [r for r in receipts if int(r["week"]) < number]
    game_day = date.fromisoformat(game["date"])
    coverage = {}

    def unit(team):
        data = (jacksonville_input(paths, game, call_sheet, prior, anchors) if team == PROTAGONIST
                else opponent_input(paths, game, prior, anchors))
        if paths.year != 2013:
            data["strength"], coverage[team] = strength.team_strength(team, data["roster"], paths.year, game_day)
        return data

    row = {
        "event_id": event_id(game, paths.year), "receipt": receipt_name(game), "week": number,
        "rotation_basis": {},
        "preseason_game": number, "date": game["date"], "kickoff_et": game.get("kickoff_et"),
        "away": game["away"], "home": game["home"],
        "venue": "neutral" if game.get("site") == "neutral" else "home", "game_type": PRESEASON,
        "away_input": unit(game["away"]), "home_input": unit(game["home"]),
    }
    for side in ("away_input", "home_input"):
        row["rotation_basis"][row[side]["team_id"]] = "plan" if row[side].get("rotation_plan") else "default"
    if with_ages:
        # A background camp player with no public identity record may enter
        # with age None and the age_unverified flag (carried into the receipt);
        # every Jacksonville player must still carry a verified birth date.
        opponent = "home_input" if game["away"] == PROTAGONIST else "away_input"
        row["player_ages"] = player_bios.biographies(
            [p["player_id"] for side in ("away_input", "home_input") for p in row[side]["roster"]], game_day,
            allow_unverified=[p["player_id"] for p in row[opponent]["roster"]])
    package = {"season": paths.year, "preseason_game": number, "week": number, "game_type": PRESEASON,
               "games": [row]}
    if coverage:
        package["strength_coverage"] = {team: dict(c) for team, c in sorted(coverage.items())}
    return package
