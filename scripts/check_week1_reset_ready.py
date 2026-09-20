#!/usr/bin/env python3
"""Fail closed until every 2013 Week 1 replacement team input is canonical."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "career/2013/migrations/week_01_full_fidelity_reset.json"

REQUIRED_TEAM_FIELDS = {
    "team_id",
    "active_players",
    "offense_anchor",
    "defense_anchor",
    "special_teams_anchor",
    "roster",
}


def team_errors(label, value):
    if not isinstance(value, dict):
        return [f"{label}: missing TeamInput object"]
    errors = []
    missing = sorted(REQUIRED_TEAM_FIELDS - set(value))
    if missing:
        errors.append(f"{label}: missing fields {', '.join(missing)}")
    if not value.get("team_id"):
        errors.append(f"{label}: empty team_id")
    if not value.get("active_players"):
        errors.append(f"{label}: no active_players")
    if not value.get("roster"):
        errors.append(f"{label}: no roster")
    return errors


def check(data):
    errors = []
    if data.get("migration") != "2013-week-01-full-fidelity-reset":
        errors.append("wrong migration manifest")
    if data.get("user_authorized") is not True:
        errors.append("reset is not user-authorized")
    games = data.get("games")
    if not isinstance(games, list) or len(games) != 16:
        errors.append("manifest must contain exactly 16 Week 1 games")
        return errors
    event_ids = set()
    team_names = set()
    for game in games:
        event_id = game.get("event_id")
        if not event_id or event_id in event_ids:
            errors.append("missing or duplicate replacement event_id")
        event_ids.add(event_id)
        team_names.update([game.get("away"), game.get("home")])
        errors.extend(team_errors(f"{game.get('away')} away_input", game.get("away_input")))
        errors.extend(team_errors(f"{game.get('home')} home_input", game.get("home_input")))
    if len(team_names) != 32:
        errors.append(f"Week 1 manifest must cover 32 unique teams, found {len(team_names)}")
    return errors


def main():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors = check(data)
    if errors:
        print("WEEK1_RESET_BLOCKED")
        for error in errors:
            print("- " + error)
        return 1
    print("WEEK1_RESET_READY")
    return 0


if __name__ == "__main__":
    sys.exit(main())
