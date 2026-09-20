"""Public season-stat aggregation for closed game results.

This module is deliberately downstream of the game kernel. It never affects
resolution, ratings, probability, seeding, or game state. It only aggregates
coach-facing statistics that already exist in a closed result.
"""
from copy import deepcopy

from .player_evidence import STAT_FIELDS

STATBOOK_SCHEMA_VERSION = 1

TEAM_STAT_FIELDS = (
    "points", "touchdowns", "field_goals", "punts", "turnovers",
    "sacks_allowed", "penalties", "penalty_yards", "passing_yards",
    "rushing_yards", "first_downs", "third_down_attempts",
    "third_down_conversions", "time_of_possession", "kick_returns",
    "punt_returns",
)


def make_receipt(result, *, week, matchup, coverage="complete"):
    """Return the public stat-only receipt for one already-closed game."""
    if not result.get("terminated"):
        raise ValueError("only terminated games may enter the statbook")
    event_id = result.get("event_id")
    if not isinstance(event_id, str) or not event_id:
        raise ValueError("closed game requires event_id")
    if not isinstance(week, int) or week < 1:
        raise ValueError("week must be a positive integer")
    if coverage not in {"complete", "legacy_partial"}:
        raise ValueError("unknown stat coverage state")
    team_stats = result.get("team_stats")
    if not isinstance(team_stats, dict) or len(team_stats) != 2:
        raise ValueError("two-team statistics required")
    return {
        "schema_version": STATBOOK_SCHEMA_VERSION,
        "event_id": event_id,
        "week": week,
        "matchup": matchup,
        "coverage": coverage,
        "final_score": deepcopy(result["final_score"]),
        "team_stats": deepcopy(team_stats),
    }


def _blank_team():
    return {
        "games": 0,
        "team_stats": {field: 0 for field in TEAM_STAT_FIELDS},
        "players": {},
    }


def _blank_player(position):
    return {
        "position": position,
        **{field: 0 for field in STAT_FIELDS},
    }


def _numeric_player_fields(line):
    return {
        key for key, value in line.items()
        if key != "position"
        and isinstance(value, (int, float))
        and not isinstance(value, bool)
    }


def aggregate_receipts(receipts):
    """Aggregate game receipts without inferring any missing statistic."""
    receipts = list(receipts)
    seen = set()
    teams = {}
    league_players = {}
    through_week = 0
    complete = True
    player_stat_fields = set(STAT_FIELDS)

    for receipt in receipts:
        event_id = receipt.get("event_id")
        if event_id in seen:
            raise ValueError(f"duplicate stat receipt: {event_id}")
        seen.add(event_id)
        if receipt.get("schema_version") != STATBOOK_SCHEMA_VERSION:
            raise ValueError("unsupported statbook schema")
        through_week = max(through_week, int(receipt.get("week", 0)))
        complete = complete and receipt.get("coverage") == "complete"

        for team_id, game in receipt.get("team_stats", {}).items():
            team = teams.setdefault(team_id, _blank_team())
            team["games"] += 1
            for field in TEAM_STAT_FIELDS:
                value = game.get(field)
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    team["team_stats"][field] += value

            for player_id, line in game.get("players", {}).items():
                position = line.get("position", "")
                numeric_fields = _numeric_player_fields(line)
                player_stat_fields.update(numeric_fields)
                player = team["players"].setdefault(player_id, _blank_player(position))
                if not player.get("position") and position:
                    player["position"] = position
                for field in numeric_fields:
                    value = line[field]
                    player[field] = player.get(field, 0) + value

                # League totals follow the player across teams. Pseudo-player
                # ids beginning "__" preserve unattributed legacy totals but
                # never enter player leaderboards.
                if not str(player_id).startswith("__"):
                    league = league_players.setdefault(
                        player_id,
                        {"teams": set(), **_blank_player(position)},
                    )
                    league["teams"].add(team_id)
                    if not league.get("position") and position:
                        league["position"] = position
                    for field in numeric_fields:
                        value = line[field]
                        league[field] = league.get(field, 0) + value

    for line in league_players.values():
        line["teams"] = sorted(line["teams"])

    return {
        "schema_version": STATBOOK_SCHEMA_VERSION,
        "through_week": through_week,
        "coverage_complete": complete,
        "receipt_count": len(receipts),
        "player_stat_fields": sorted(player_stat_fields),
        "teams": teams,
        "players": league_players,
    }


def leaders(book, field, *, limit=10):
    """Return league leaders for one additive player field."""
    if field not in set(book.get("player_stat_fields", STAT_FIELDS)):
        raise ValueError(f"unknown player stat: {field}")
    rows = []
    for player_id, line in book.get("players", {}).items():
        value = line.get(field, 0)
        if value:
            rows.append({
                "player_id": player_id,
                "teams": tuple(line.get("teams", ())),
                "position": line.get("position", ""),
                "value": value,
            })
    rows.sort(key=lambda row: (-row["value"], row["player_id"]))
    return rows[:limit]
