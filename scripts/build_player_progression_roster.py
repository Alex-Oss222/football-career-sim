#!/usr/bin/env python3
"""Derive the offseason player-progression cohort from the live roster.

The current roster is the source of truth for who is eligible. A frozen
2013 exit index is used only to distinguish Jacksonville continuity from 2014
newcomers. Run this again after any signing, release, trade, tender resolution,
or draft-related roster addition before resolving offseason progression.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROSTER = ROOT / "career/2014/roster.md"
DEFAULT_EXIT_INDEX = (
    ROOT / "career/2014/offseason/player_development/2013_exit_player_index.json"
)
DEFAULT_OUTPUT = (
    ROOT / "career/2014/offseason/player_development/progression_roster.json"
)


@dataclass(frozen=True)
class RosterPlayer:
    player: str
    pos: str
    status: str


COUNT_RE = re.compile(r"Canonical controlled-player count:\*\*\s*\*\*(\d+)\*\*")
AS_OF_RE = re.compile(r"^\*\*As of:\*\*\s*(.+?)(?:\s*\(|$)")


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_current_roster(path: Path) -> tuple[str, int, list[RosterPlayer]]:
    """Read only the canonical `Current controlled players` section."""

    text = path.read_text(encoding="utf-8")
    match = COUNT_RE.search(text)
    if not match:
        raise ValueError("roster is missing canonical controlled-player count")
    canonical_count = int(match.group(1))

    as_of = None
    in_current = False
    player_col = pos_col = status_col = None
    players: list[RosterPlayer] = []
    seen: set[str] = set()

    for line in text.splitlines():
        if as_of is None:
            date_match = AS_OF_RE.match(line)
            if date_match:
                as_of = date_match.group(1).strip()
        if line.strip() == "## Current controlled players":
            in_current = True
            continue
        if in_current and line.startswith("## "):
            break
        if not in_current:
            continue
        if not line.startswith("|"):
            player_col = pos_col = status_col = None
            continue
        cells = _cells(line)
        if "Player" in cells:
            player_col = cells.index("Player")
            pos_col = cells.index("Pos") if "Pos" in cells else None
            status_col = next(
                (i for i, value in enumerate(cells) if value == "Status"), None
            )
            continue
        if player_col is None or pos_col is None or status_col is None:
            continue
        if cells and set(cells[0]) <= {"-", ":"}:
            continue
        if max(player_col, pos_col, status_col) >= len(cells):
            raise ValueError("malformed roster row: " + line)
        player = cells[player_col]
        if player in seen:
            raise ValueError("duplicate player in current roster: " + player)
        seen.add(player)
        players.append(RosterPlayer(player, cells[pos_col], cells[status_col]))

    if as_of is None:
        raise ValueError("roster is missing an As of date")
    if len(players) != canonical_count:
        raise ValueError(
            f"parsed {len(players)} current controlled players; "
            f"roster declares {canonical_count}"
        )
    return as_of, canonical_count, players


def load_exit_index(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("season") != 2013:
        raise ValueError("exit index must identify the 2013 season")
    result: dict[str, str] = {}
    for row in data.get("players", []):
        player = row.get("player")
        pos = row.get("pos")
        if not isinstance(player, str) or not player.strip() or not isinstance(pos, str):
            raise ValueError("invalid player row in exit index")
        if player in result:
            raise ValueError("duplicate player in exit index: " + player)
        result[player] = pos
    if data.get("count") != len(result):
        raise ValueError("exit index count does not match player rows")
    return result


def continuity_kind(player: RosterPlayer, exit_index: dict[str, str]) -> str:
    if player.player not in exit_index:
        return "new_2014_acquisition"
    if "reserve/future" in player.status.lower():
        return "practice_squad_to_reserve_future"
    return "returning_2013_jaguar"


def build_manifest(roster_path: Path, exit_index_path: Path) -> dict:
    as_of, controlled_count, roster = parse_current_roster(roster_path)
    exit_index = load_exit_index(exit_index_path)
    rows = []
    counts = {
        "controlled_players": controlled_count,
        "jacksonville_2013_continuity": 0,
        "returning_2013_jaguar": 0,
        "practice_squad_to_reserve_future": 0,
        "new_2014_acquisition": 0,
    }
    for player in roster:
        kind = continuity_kind(player, exit_index)
        if kind != "new_2014_acquisition":
            counts["jacksonville_2013_continuity"] += 1
        counts[kind] += 1
        rows.append(
            {
                "player": player.player,
                "pos": player.pos,
                "continuity": kind,
            }
        )

    roster_source = (
        str(roster_path.relative_to(ROOT))
        if roster_path.is_relative_to(ROOT)
        else str(roster_path)
    )
    exit_source = (
        str(exit_index_path.relative_to(ROOT))
        if exit_index_path.is_relative_to(ROOT)
        else str(exit_index_path)
    )
    return {
        "schema_version": 1,
        "season": 2014,
        "as_of": as_of,
        "roster_source": roster_source,
        "continuity_source": exit_source,
        "policy": (
            "Roster controls eligibility. The exit index identifies Jacksonville "
            "2013 continuity only. Regenerate after any transaction or draft addition "
            "before progression is resolved."
        ),
        "counts": counts,
        "players": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--roster", type=Path, default=DEFAULT_ROSTER)
    parser.add_argument("--exit-index", type=Path, default=DEFAULT_EXIT_INDEX)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare generated data to the existing output",
    )
    args = parser.parse_args()

    try:
        manifest = build_manifest(args.roster.resolve(), args.exit_index.resolve())
        rendered = json.dumps(manifest, indent=2) + "\n"
        if args.check:
            if not args.output.is_file():
                raise ValueError("progression roster output is missing")
            if args.output.read_text(encoding="utf-8") != rendered:
                raise ValueError(
                    "progression roster is stale; regenerate it from the live roster"
                )
            print(
                "PLAYER_PROGRESSION_ROSTER: CURRENT "
                f"({manifest['counts']['controlled_players']} controlled, "
                f"{manifest['counts']['jacksonville_2013_continuity']} "
                "with 2013 Jacksonville continuity)"
            )
            return 0
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(
            "PLAYER_PROGRESSION_ROSTER: WROTE "
            f"{args.output} ({manifest['counts']['controlled_players']} controlled, "
            f"{manifest['counts']['jacksonville_2013_continuity']} "
            "with 2013 Jacksonville continuity)"
        )
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("PLAYER_PROGRESSION_ROSTER: BLOCKED")
        print("- " + str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
