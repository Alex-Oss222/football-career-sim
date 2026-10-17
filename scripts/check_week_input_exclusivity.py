#!/usr/bin/env python3
"""Fail closed when a weekly TeamInput slate violates completeness or player control."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.seasons import SeasonPaths
from runtime.usage import group, lineup_errors
from runtime.week_inputs import GAME_DAY_ACTIVE_LIMIT
# A Status cell is the status alone or the status followed by one dated
# parenthetical, e.g. "Active 53 (signed August 31, 2014)". One definition,
# shared with the in-season rails' Jacksonville control.
from runtime.rails import CONTROLLED_STATUS

# Groups whose usage kernel 2013.4 orders by depth; each needs an explicit order.
DEPTH_REQUIRED = ("QB", "RB", "WR", "TE")


def controlled_players_from_roster(path: Path) -> set[str]:
    """Every player in a roster table whose Status column shows club control."""
    controlled: set[str] = set()
    player_col = status_col = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            player_col = status_col = None
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if "Player" in cells:
            player_col = cells.index("Player")
            status_col = next((i for i, c in enumerate(cells) if "status" in c.lower()), None)
            continue
        if player_col is None or status_col is None or set(cells[0]) <= {"-", ":"}:
            continue
        if status_col < len(cells) and CONTROLLED_STATUS.match(cells[status_col]):
            controlled.add(cells[player_col])
    return controlled


def _player_ids(team_input) -> set[str]:
    if not isinstance(team_input, dict):
        return set()
    ids: set[str] = set()
    for raw in team_input.get("active_players", ()) or ():
        if isinstance(raw, str) and raw.strip():
            ids.add(raw.split(":", 1)[-1].strip())
    for raw in team_input.get("roster", ()) or ():
        if isinstance(raw, dict):
            player_id = raw.get("player_id")
            if isinstance(player_id, str) and player_id.strip():
                ids.add(player_id.strip())
        elif isinstance(raw, str) and raw.strip():
            ids.add(raw.split(":", 1)[-1].strip())
    return ids


def game_day_errors(team, team_input):
    """Game-day unit and depth-order checks for one TeamInput."""
    active = {
        raw.split(":", 1)[-1].strip()
        for raw in team_input.get("active_players", ()) or ()
        if isinstance(raw, str)
    }
    players = []
    for raw in team_input.get("roster", ()) or ():
        if not isinstance(raw, dict) or raw.get("available", True) is False:
            continue
        if active and raw.get("player_id") not in active:
            continue
        players.append(SimpleNamespace(position=raw.get("position"), depth=raw.get("depth")))
    if not players:
        return [f"{team}: TeamInput has no available roster rows"]
    errors = [f"{team}: game-day unit incomplete: {e}" for e in lineup_errors(players)]
    for grp in DEPTH_REQUIRED:
        members = [p for p in players if group(p.position) == grp]
        if members and not any(isinstance(p.depth, int) for p in members):
            errors.append(f"{team}: {grp} group has no explicit depth order")
    return errors


def check_inputs(data, controlled_players, protagonist="Jacksonville Jaguars", expected_games=None,
                 active_limit=GAME_DAY_ACTIVE_LIMIT):
    """``active_limit`` is 46 for a regular-season or postseason slate; a
    preseason game passes runtime.rules.active_limit("preseason")."""
    errors = []
    ownership: dict[str, set[str]] = {}
    team_games: dict[str, int] = {}
    games = data.get("games") if isinstance(data, dict) else None
    if not isinstance(games, list) or not games:
        return ["weekly input package requires a nonempty games list"]
    if expected_games is not None:
        if not isinstance(expected_games, int) or isinstance(expected_games, bool) or expected_games < 1:
            return ["expected_games must be a positive integer"]
        if len(games) != expected_games:
            errors.append(
                f"weekly input package has {len(games)} game(s); expected {expected_games}"
            )

    for game_index, game in enumerate(games, 1):
        if not isinstance(game, dict):
            errors.append("game row must be an object")
            continue
        away = game.get("away")
        home = game.get("home")
        if isinstance(away, str) and isinstance(home, str) and away.strip() and away == home:
            errors.append(f"game {game_index}: away and home team are both {away}")
        for side in ("away", "home"):
            team = game.get(side)
            team_input = game.get(side + "_input")
            if not isinstance(team, str) or not team.strip():
                errors.append(f"{side}: missing team name")
                continue
            prior_game = team_games.get(team)
            if prior_game is not None:
                errors.append(
                    f"{team}: appears in multiple weekly games: {prior_game} and {game_index}"
                )
            else:
                team_games[team] = game_index
            if not isinstance(team_input, dict):
                errors.append(f"{team}: missing TeamInput object")
                continue
            errors.extend(game_day_errors(team, team_input))
            dressed = len(team_input.get("active_players", ()) or ())
            if dressed > active_limit:
                errors.append(f"{team}: {dressed} game-day actives, limit {active_limit}")
            for player in _player_ids(team_input):
                ownership.setdefault(player, set()).add(team)
                if team != protagonist and player in controlled_players:
                    errors.append(
                        f"{player}: Jacksonville-controlled player appears on {team}"
                    )

    for player, teams in sorted(ownership.items()):
        if len(teams) > 1:
            errors.append(
                f"{player}: appears on multiple weekly TeamInputs: "
                + ", ".join(sorted(teams))
            )
    errors.extend(gsis_errors(games))
    return errors


def gsis_errors(games):
    """Kernel 2014.6 (B7): a gsis id in a strength record names one player
    on one club in the weekly slate. Two roster rows of one club or rows of
    two clubs sharing a gsis id, or a player-state record whose latent keys
    name a gsis outside its own players, fail the gate."""
    errors = []
    owners = {}
    for game in games:
        if not isinstance(game, dict):
            continue
        for side in ("away", "home"):
            team = game.get(side)
            record = (game.get(side + "_input") or {}).get("strength") if isinstance(game.get(side + "_input"), dict) else None
            if not isinstance(record, dict):
                continue
            seen = {}
            for pid, row in (record.get("players") or {}).items():
                gsis = (row or {}).get("gsis_id")
                if not gsis:
                    continue
                if gsis in seen and seen[gsis] != pid:
                    errors.append(f"{team}: gsis {gsis} names two roster rows: {seen[gsis]} and {pid}")
                seen[gsis] = pid
                owners.setdefault(gsis, {})[team] = pid
            for key in record.get("latent_keys") or ():
                if isinstance(key, (list, tuple)) and len(key) == 4 and key[2] not in seen:
                    errors.append(f"{team}: latent key names gsis {key[2]}, not one of its players")
    for gsis, teams in sorted(owners.items()):
        if len(teams) > 1:
            errors.append("gsis %s appears on multiple weekly TeamInputs: %s"
                          % (gsis, ", ".join("%s (%s)" % (t, p) for t, p in sorted(teams.items()))))
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", type=Path)
    parser.add_argument("--season", type=int, default=2013,
                        help="Season whose branch roster defines Jacksonville control (default 2013).")
    parser.add_argument(
        "--roster",
        type=Path,
        default=None,
        help="Roster file to read control from; defaults to the season's roster (SeasonPaths).",
    )
    parser.add_argument("--protagonist", default="Jacksonville Jaguars")
    parser.add_argument(
        "--expected-games",
        type=int,
        help="Scheduled game count for this week; use it to reject a partial slate.",
    )
    args = parser.parse_args()

    data = json.loads(args.inputs.read_text(encoding="utf-8"))
    controlled = controlled_players_from_roster(args.roster or SeasonPaths(args.season, ROOT).roster)
    errors = check_inputs(
        data, controlled, args.protagonist, expected_games=args.expected_games
    )
    if errors:
        print("WEEK_INPUT_EXCLUSIVITY: BLOCKED")
        for error in errors:
            print("- " + error)
        return 1
    print("WEEK_INPUT_EXCLUSIVITY: READY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
