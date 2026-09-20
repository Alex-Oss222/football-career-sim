"""Public season-stat aggregation for closed game results.

This module is deliberately downstream of the game kernel. It never affects
resolution, ratings, probability, seeding, or game state. It only aggregates
coach-facing statistics that already exist in a closed result.
"""
from copy import deepcopy

from .player_evidence import STAT_FIELDS

STATBOOK_SCHEMA_VERSION = 2

TEAM_STAT_FIELDS = (
    "points", "touchdowns", "field_goals", "punts", "turnovers",
    "sacks_allowed", "penalties", "penalty_yards", "passing_yards",
    "rushing_yards", "first_downs", "third_down_attempts",
    "third_down_conversions", "time_of_possession", "kick_returns",
    "punt_returns",
)


def _compact_team_stats(team_stats):
    """Preserve every nonzero public statistic while removing diff-heavy zero rows."""
    compact = {}
    for team_id, game in team_stats.items():
        row = {key: deepcopy(value) for key, value in game.items() if key != "players"}
        players = {}
        for player_id, line in game.get("players", {}).items():
            position = line.get("position", "")
            numeric = {
                key: value for key, value in line.items()
                if key != "position"
                and isinstance(value, (int, float))
                and not isinstance(value, bool)
                and value != 0
            }
            if numeric:
                players[player_id] = {"position": position, **numeric}
        row["players"] = players
        compact[team_id] = row
    return compact


def make_receipt(result, *, week, matchup, coverage="complete", detail="full"):
    """Return a public receipt for one already-closed game.

    full keeps the snap ledger and all player counters. compact_stats keeps
    every nonzero generated player/team statistic but omits snap rows,
    named-call data, zero-only player rows, and zero-valued player fields.
    """
    if not result.get("terminated"):
        raise ValueError("only terminated games may enter the statbook")
    event_id = result.get("event_id")
    if not isinstance(event_id, str) or not event_id:
        raise ValueError("closed game requires event_id")
    if not isinstance(week, int) or week < 1:
        raise ValueError("week must be a positive integer")
    if coverage not in {"complete", "legacy_partial"}:
        raise ValueError("unknown stat coverage state")
    if detail not in {"full", "compact_stats"}:
        raise ValueError("unknown receipt detail")
    team_stats = result.get("team_stats")
    if not isinstance(team_stats, dict) or len(team_stats) != 2:
        raise ValueError("two-team statistics required")
    receipt = {
        "schema_version": STATBOOK_SCHEMA_VERSION,
        "event_id": event_id,
        "week": week,
        "matchup": matchup,
        "coverage": coverage,
        "detail": detail,
        "kernel_version": result.get("kernel_version"),
        "final_score": deepcopy(result["final_score"]),
        "team_stats": (
            deepcopy(team_stats)
            if detail == "full"
            else _compact_team_stats(team_stats)
        ),
    }
    if detail == "full":
        receipt["play_ledger"] = deepcopy(result.get("play_ledger", []))
        receipt["play_call_stats"] = deepcopy(result.get("play_call_stats", {}))
    return receipt


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
    play_calls = {}
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

        for team_id, calls in receipt.get("play_call_stats", {}).items():
            team_calls = play_calls.setdefault(team_id, {})
            for name, line in calls.items():
                row = team_calls.setdefault(name, {"family": line.get("family", name)})
                for field, value in line.items():
                    if field == "family":
                        continue
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        row[field] = row.get(field, 0) + value

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
        "plays_recorded": sum(len(receipt.get("play_ledger", [])) for receipt in receipts),
        "player_stat_fields": sorted(player_stat_fields),
        "teams": teams,
        "players": league_players,
        "play_calls": play_calls,
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
