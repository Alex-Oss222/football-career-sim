"""Public season-stat aggregation for closed game results.

This module is deliberately downstream of the game kernel. It never affects
resolution, ratings, probability, seeding, or game state. It only aggregates
coach-facing statistics that already exist in a closed result.
"""
from copy import deepcopy

from .player_evidence import STAT_FIELDS

# Kernel 2014.4 participation counters enter a season book only from receipts
# that carry them, so books built from earlier receipts are unchanged.
PARTICIPATION_FIELDS = ("offensive_snaps", "defensive_snaps", "special_teams_snaps")
BOOK_FIELDS = tuple(f for f in STAT_FIELDS if f not in PARTICIPATION_FIELDS)

STATBOOK_SCHEMA_VERSION = 3

# Longest-play counters combine by maximum, never by sum.
LONG_FIELDS = frozenset({"long_rush", "long_reception", "long_punt"})

TEAM_STAT_FIELDS = (
    "points", "touchdowns", "field_goals", "punts", "turnovers",
    "sacks_allowed", "penalties", "penalty_yards", "passing_yards",
    "rushing_yards", "first_downs", "third_down_attempts",
    "third_down_conversions", "time_of_possession", "kick_returns",
    "punt_returns",
    # Kernel 2013.6 onward (kernel 2013.7 keeps them unchanged). Older
    # receipts do not carry these fields; they aggregate as absent (never as
    # zero) and are labelled by the renderers.
    "field_goal_attempts", "extra_point_attempts", "extra_points_made",
    "safeties", "turnovers_on_downs", "clock_expired_drives", "kickoffs",
    "drives",
)
LEGACY_TEAM_STAT_FIELDS = TEAM_STAT_FIELDS[:16]
DRIVE_MODEL_TEAM_STAT_FIELDS = TEAM_STAT_FIELDS[16:]
DRIVE_MODEL_FROM_KERNEL = (2013, 6)
# Kernel 2013.7 onward the drives summary also carries start and end spots,
# the next start, the real drive chains and the fourth-down state (see
# runtime.play_detail.DRIVE_SUMMARY_FIELDS); no team stat field is added.
FIELD_POSITION_FROM_KERNEL = (2013, 7)
# Kernel 2014.6 field group (batch B1 scaffold). The team and player
# counters that only kernel 2014.6-or-later receipts carry are appended here,
# in a fixed order, by the batch that adds each one. Older receipts aggregate
# them as absent, never as zero, and a book counts its kernel 2014.6 games
# per club (kernel_2014_6_games) only when such a receipt exists, so every
# closed 2013 and 2014 Weeks 1-4 view is unchanged.
KERNEL_2014_6_FROM = (2014, 6)
KERNEL_2014_6_TEAM_STAT_FIELDS = ()
KERNEL_2014_6_PLAYER_FIELDS = ()
# Every key the 2014.6 group adds, by where it lives in a result or receipt
# (tests/test_profiles.py strip_2014_6_fields removes exactly these).
# DRIVE_SUMMARY_FIELDS additions are possession keys; snap-ledger row keys
# are "ledger".
KERNEL_2014_6_FIELD_GROUP = {
    # Batch B6 (W2a): the full receipt's substitution record. Batch B8: the
    # compact kicks summary and the game's scoring events.
    "result": ("calibration_base", "substitutions", "kicks", "scoring_events"),
    # Batch B5: the window seconds left at a drive's last spike (R14). Batch
    # B8: a non-offensive score made during the possession (R15, B9).
    "possession": ("last_spike_seconds_left", "non_offensive_score"),
    # Batch B8: the kick record's chain and scoring fields.
    "kickoff": ("remaining", "chain", "after_drive", "basis", "touchdown", "scoring_team", "xp_made", "points"),
    # Batch B6 (W5a): a league-model decision marker on new rows and on the
    # fourth-down state (nested under "fourth_down", see FOURTH_DOWN_FIELDS).
    "ledger": ("decision_source",),
    "fourth_down": ("decision_source",),
    "team": KERNEL_2014_6_TEAM_STAT_FIELDS,
    "player": KERNEL_2014_6_PLAYER_FIELDS,
}
# Batch B6 (W5a): the snap-ledger row kinds only kernel 2014.6-or-later
# results carry (timeout and two-minute-warning rows). plays_recorded counts
# scrimmage rows only for such receipts (_plays_recorded); older receipts
# keep their row count so closed views regenerate unchanged.
KERNEL_2014_6_LEDGER_ROWS = ("timeout", "two_minute_warning")
SCRIMMAGE_ROWS = ("pass", "run")


def kernel_at_least(version, minimum=DRIVE_MODEL_FROM_KERNEL):
    """True when a kernel version string is at or after ``minimum``."""
    try:
        parts = tuple(int(v) for v in str(version).split("."))
    except ValueError:
        return False
    return parts >= minimum


def _numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _receipt_team_stats(team_stats, *, compact):
    """Stamp one game-active appearance on every game-day player row.

    Every player in a closed result's player dictionary was on that club's
    game-day active list, so each row carries games=1. compact_stats then
    drops zero-valued counters but keeps the row, which is what lets games
    active be counted for every player, not only those who recorded a stat.
    """
    stamped = {}
    for team_id, game in team_stats.items():
        row = {key: deepcopy(value) for key, value in game.items() if key != "players"}
        players = {}
        for player_id, line in game.get("players", {}).items():
            counters = {
                key: value for key, value in line.items()
                if key != "position" and _numeric(value) and (value != 0 or not compact)
            }
            if not str(player_id).startswith("__"):
                counters["games"] = 1
            players[player_id] = {"position": line.get("position", ""), **counters}
        row["players"] = players
        stamped[team_id] = row
    return stamped


INJURY_FIELDS = ("team", "player", "injury_class", "severity", "restriction",
                 "return_days", "reassessment_days")


# Kernel 2014.4 onset fields, carried only when the result has them (closed
# 2013 receipts are unchanged).
INJURY_ONSET_FIELDS = ("onset", "drive", "period", "clock", "removed")


def public_injury(injury):
    """The game's public injury report entry: who, what class, what restriction."""
    entry = {field: injury.get(field) for field in INJURY_FIELDS}
    entry.update({field: injury[field] for field in INJURY_ONSET_FIELDS if field in injury})
    return entry


def _home_and_away(matchup, team_stats):
    away, separator, home = matchup.partition(" at ")
    if not separator or {away, home} != set(team_stats):
        raise ValueError("matchup must read 'Away Club at Home Club' using the receipt's clubs")
    return home, away


def make_receipt(result, *, week, matchup, coverage="complete", detail="full",
                 player_attribution_incomplete_teams=()):
    """Return a public receipt for one already-closed game.

    Both details carry the game's public injury report. full keeps the snap
    ledger and all player counters. compact_stats keeps
    every nonzero generated player/team statistic and every game-day player
    row, but omits snap rows, named-call data and zero-valued player fields.
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
    if not isinstance(player_attribution_incomplete_teams, (tuple, list, set)):
        raise ValueError("player attribution teams must be a collection")
    team_stats = result.get("team_stats")
    if not isinstance(team_stats, dict) or len(team_stats) != 2:
        raise ValueError("two-team statistics required")
    home, away = _home_and_away(matchup, team_stats)
    receipt = {
        "schema_version": STATBOOK_SCHEMA_VERSION,
        "event_id": event_id,
        "week": week,
        "matchup": matchup,
        "home": home,
        "away": away,
        "coverage": coverage,
        "detail": detail,
        "kernel_version": result.get("kernel_version"),
        "final_score": deepcopy(result["final_score"]),
        "team_stats": _receipt_team_stats(team_stats, compact=detail == "compact_stats"),
    }
    incomplete=sorted(set(player_attribution_incomplete_teams))
    if any(team not in team_stats for team in incomplete):
        raise ValueError("player attribution team not present in receipt")
    if incomplete:
        receipt["player_attribution_incomplete_teams"]=incomplete
    receipt["injuries"] = [public_injury(i) for i in result.get("injuries", ())]
    if kernel_at_least(result.get("kernel_version")) and result.get("possessions"):
        # Compact per-possession summary so coherence can be audited on
        # every game, including compact_stats background receipts.
        from .play_detail import drive_summary
        receipt["game_type"] = result.get("game_type", "regular")
        receipt["drives"] = drive_summary(result["possessions"])
    if result.get("extra_point_rule") is not None:
        # Preseason only: the dated try rule the kernel applied (runtime.rules).
        receipt["game_date"] = result.get("game_date")
        receipt["extra_point_rule"] = deepcopy(result["extra_point_rule"])
    if result.get("rotation") is not None:
        # Preseason only: the unit rotation as applied (runtime/rotation.py).
        receipt["rotation"] = deepcopy(result["rotation"])
    if result.get("calibration_base") is not None:
        # Kernel 2014.6 onward (append-only): the calibration base, its
        # manifest digest and cell rules the game was resolved with
        # (runtime.calibration_base.base_for_result checks them on audit).
        receipt["calibration_base"] = deepcopy(result["calibration_base"])
    if kernel_at_least(result.get("kernel_version"), KERNEL_2014_6_FROM) and result.get("scoring_events") is not None:
        # Kernel 2014.6 onward (batch B8, append-only): the compact kicks
        # summary and the scoring events, on both details; check_ledger
        # rebuilds the events from the drives and kicks and compares.
        from .play_detail import kick_summary
        receipt["kicks"] = kick_summary(result.get("kickoffs", ()))
        receipt["scoring_events"] = deepcopy(result["scoring_events"])
    if detail == "full":
        receipt["play_ledger"] = deepcopy(result.get("play_ledger", []))
        receipt["play_call_stats"] = deepcopy(result.get("play_call_stats", {}))
        if kernel_at_least(result.get("kernel_version"), KERNEL_2014_6_FROM):
            # Kernel 2014.6 onward (batch B6, W2a): the substitution record
            # (entrant, slots, moves, fills, specialists, returners) rides
            # with the full receipt; compact receipts are unchanged.
            receipt["substitutions"] = deepcopy(result.get("substitutions", []))
    return receipt


def _blank_team():
    return {
        "games": 0,
        "team_stats": {field: 0 for field in LEGACY_TEAM_STAT_FIELDS},
        "opponent_stats": {field: 0 for field in LEGACY_TEAM_STAT_FIELDS},
        "plays": 0,
        "opponent_plays": 0,
        "players": {},
    }


def _blank_player(position):
    return {
        "position": position,
        **{field: 0 for field in BOOK_FIELDS},
    }


def _scrimmage_plays(game):
    """Rushing attempts plus dropbacks, the offensive snap count."""
    return sum(
        line.get("rushing_attempts", 0) + line.get("dropbacks", 0)
        for line in game.get("players", {}).values()
    )


def _accumulate(total, line, fields):
    for field in fields:
        value = line[field]
        if field in LONG_FIELDS:
            total[field] = max(total.get(field, 0), value)
        else:
            total[field] = total.get(field, 0) + value


def _numeric_player_fields(line):
    return {key for key, value in line.items() if key != "position" and _numeric(value)}


def aggregate_receipts(receipts):
    """Aggregate game receipts without inferring any missing statistic."""
    receipts = list(receipts)
    seen = set()
    teams = {}
    league_players = {}
    play_calls = {}
    through_week = 0
    complete = True
    player_attribution_complete = True
    team_player_attribution_complete = {}
    player_stat_fields = set(BOOK_FIELDS)

    for receipt in receipts:
        event_id = receipt.get("event_id")
        if event_id in seen:
            raise ValueError(f"duplicate stat receipt: {event_id}")
        seen.add(event_id)
        if receipt.get("schema_version") != STATBOOK_SCHEMA_VERSION:
            raise ValueError("unsupported statbook schema")
        through_week = max(through_week, int(receipt.get("week", 0)))
        complete = complete and receipt.get("coverage") == "complete"
        incomplete_teams=set(receipt.get("player_attribution_incomplete_teams", ()))
        if incomplete_teams:
            player_attribution_complete=False

        for team_id, calls in receipt.get("play_call_stats", {}).items():
            team_calls = play_calls.setdefault(team_id, {})
            for name, line in calls.items():
                row = team_calls.setdefault(name, {"family": line.get("family", name)})
                for field, value in line.items():
                    if field == "family":
                        continue
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        row[field] = row.get(field, 0) + value

        # Explosive (20+ yards) and negative plays per named call come from
        # the full snap ledger; compact receipts carry no ledger.
        for play in receipt.get("play_ledger", ()):
            if play.get("play_type") not in {"run", "pass"} or not play.get("concept"):
                continue
            calls_for = play_calls.setdefault(play["offense"], {})
            row = calls_for.setdefault(play["concept"], {"family": play.get("family", play["concept"])})
            gain = play.get("result_yards", 0)
            row["explosive_plays"] = row.get("explosive_plays", 0) + (1 if gain >= 20 else 0)
            row["negative_plays"] = row.get("negative_plays", 0) + (1 if gain < 0 else 0)

        clubs = receipt.get("team_stats", {})
        listed = [set(game.get("players", {})) for game in clubs.values()]
        if len(listed) == 2:
            shared = sorted(p for p in listed[0] & listed[1] if not str(p).startswith("__"))
            if shared:
                raise ValueError(
                    "%s: player id on both clubs (%s); give same-named players distinct ids"
                    % (event_id, ", ".join(shared)))

        for team_id, game in clubs.items():
            team_player_attribution_complete.setdefault(team_id, True)
            if team_id in incomplete_teams:
                team_player_attribution_complete[team_id]=False
            team = teams.setdefault(team_id, _blank_team())
            team["games"] += 1
            opponent = next((g for t, g in clubs.items() if t != team_id), {})
            team["plays"] += _scrimmage_plays(game)
            team["opponent_plays"] += _scrimmage_plays(opponent)
            for field in TEAM_STAT_FIELDS + KERNEL_2014_6_TEAM_STAT_FIELDS:
                if _numeric(game.get(field)):
                    team["team_stats"][field] = team["team_stats"].get(field, 0) + game[field]
                if _numeric(opponent.get(field)):
                    team["opponent_stats"][field] = team["opponent_stats"].get(field, 0) + opponent[field]
            if _numeric(game.get("drives")):
                team["drive_model_games"] = team.get("drive_model_games", 0) + 1
            if kernel_at_least(receipt.get("kernel_version"), KERNEL_2014_6_FROM):
                team["kernel_2014_6_games"] = team.get("kernel_2014_6_games", 0) + 1

            for player_id, line in game.get("players", {}).items():
                position = line.get("position", "")
                numeric_fields = _numeric_player_fields(line)
                player_stat_fields.update(numeric_fields)
                player = team["players"].setdefault(player_id, _blank_player(position))
                if not player.get("position") and position:
                    player["position"] = position
                _accumulate(player, line, numeric_fields)

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
                    _accumulate(league, line, numeric_fields)

    for line in league_players.values():
        line["teams"] = sorted(line["teams"])

    return {
        "schema_version": STATBOOK_SCHEMA_VERSION,
        "through_week": through_week,
        "coverage_complete": complete,
        "player_attribution_complete": player_attribution_complete,
        "team_player_attribution_complete": team_player_attribution_complete,
        "receipt_count": len(receipts),
        "plays_recorded": sum(_plays_recorded(receipt) for receipt in receipts),
        "player_stat_fields": sorted(player_stat_fields),
        "teams": teams,
        "players": league_players,
        "play_calls": play_calls,
    }


def _plays_recorded(receipt):
    """A receipt's recorded plays: for kernel 2014.6-or-later receipts the
    scrimmage rows only (batch B6, W5a: timeout and two-minute-warning rows
    are records, not plays); earlier receipts keep their row count, so every
    closed 2013 and 2014 Weeks 1-4 view regenerates unchanged."""
    ledger = receipt.get("play_ledger", [])
    if kernel_at_least(receipt.get("kernel_version"), KERNEL_2014_6_FROM):
        return sum(1 for play in ledger if play.get("play_type") in SCRIMMAGE_ROWS)
    return len(ledger)


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
