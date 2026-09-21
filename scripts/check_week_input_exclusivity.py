#!/usr/bin/env python3
"""Fail closed when a weekly TeamInput slate violates branch player control."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def controlled_players_from_roster(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    controlled: set[str] = set()
    controlled_status = re.compile(
        r"^(?:Active 53|Practice squad|Injured reserve|IR|Reserve(?:/[^|]+)?|"
        r"PUP|NFI|Suspended|Commissioner(?:/[^|]+)?)$",
        re.IGNORECASE,
    )
    for line in text.splitlines():
        match = re.match(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", line)
        if match and controlled_status.match(match.group(2).strip()):
            controlled.add(match.group(1).strip())
        if line.startswith("**Jacksonville practice squad (not active 53):**"):
            _, names = line.split(":**", 1)
            controlled.update(
                name.strip().rstrip(".")
                for name in names.split(",")
                if name.strip()
            )
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


def check_inputs(data, controlled_players, protagonist="Jacksonville Jaguars"):
    errors = []
    ownership: dict[str, set[str]] = {}
    games = data.get("games") if isinstance(data, dict) else None
    if not isinstance(games, list) or not games:
        return ["weekly input package requires a nonempty games list"]

    for game in games:
        if not isinstance(game, dict):
            errors.append("game row must be an object")
            continue
        for side in ("away", "home"):
            team = game.get(side)
            team_input = game.get(side + "_input")
            if not isinstance(team, str) or not team.strip():
                errors.append(f"{side}: missing team name")
                continue
            if not isinstance(team_input, dict):
                errors.append(f"{team}: missing TeamInput object")
                continue
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
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", type=Path)
    parser.add_argument(
        "--roster",
        type=Path,
        default=ROOT / "career/2013/roster.md",
    )
    parser.add_argument("--protagonist", default="Jacksonville Jaguars")
    args = parser.parse_args()

    data = json.loads(args.inputs.read_text(encoding="utf-8"))
    controlled = controlled_players_from_roster(args.roster)
    errors = check_inputs(data, controlled, args.protagonist)
    if errors:
        print("WEEK_INPUT_EXCLUSIVITY: BLOCKED")
        for error in errors:
            print("- " + error)
        return 1
    print("WEEK_INPUT_EXCLUSIVITY: READY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
