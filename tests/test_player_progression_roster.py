import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_player_progression_roster import (
    build_manifest,
    load_exit_index,
    parse_current_roster,
)

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / 'career/2014/00_Team_Operations/Team/Roster/roster.md'
EXIT_INDEX = (
    ROOT
    / 'career/2014/00_Team_Operations/Player_Development/2013_exit_player_index.json'
)
OUTPUT = (
    ROOT
    / 'career/2014/00_Team_Operations/Player_Development/progression_roster.json'
)


class PlayerProgressionRosterTests(unittest.TestCase):
    def test_current_roster_drives_progression_cohort(self):
        manifest = build_manifest(ROSTER, EXIT_INDEX)
        _, controlled_count, roster = parse_current_roster(ROSTER)
        exit_index = load_exit_index(EXIT_INDEX)

        self.assertEqual(manifest["counts"]["controlled_players"], controlled_count)
        self.assertEqual(len(manifest["players"]), controlled_count)
        self.assertEqual(
            manifest["counts"]["jacksonville_2013_continuity"],
            manifest["counts"]["returning_2013_jaguar"]
            + manifest["counts"]["practice_squad_to_reserve_future"],
        )
        self.assertEqual(
            controlled_count,
            manifest["counts"]["jacksonville_2013_continuity"]
            + manifest["counts"]["new_2014_acquisition"],
        )

        by_name = {row["player"]: row for row in manifest["players"]}
        self.assertEqual(set(by_name), {row.player for row in roster})
        for row in roster:
            if row.player not in exit_index:
                self.assertEqual(
                    by_name[row.player]["continuity"], "new_2014_acquisition"
                )
            elif "reserve/future" in row.status.lower():
                self.assertEqual(
                    by_name[row.player]["continuity"],
                    "practice_squad_to_reserve_future",
                )
            else:
                self.assertEqual(
                    by_name[row.player]["continuity"], "returning_2013_jaguar"
                )

        # Cousins is not special-cased by the builder. While the live roster
        # controls him, his 2013 Jacksonville continuity must classify him as
        # a returner. If a later canonical transaction removes him, the roster
        # remains authoritative and this assertion no longer applies.
        if "Kirk Cousins" in by_name:
            self.assertEqual(
                by_name["Kirk Cousins"]["continuity"],
                "returning_2013_jaguar",
            )

    def test_continuity_is_not_inferred_from_draft_or_memory(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            roster = tmp / "roster.md"
            roster.write_text(
                "**As of:** March 1, 2014\n"
                "**Canonical controlled-player count:** **3**\n\n"
                "## Current controlled players\n\n"
                "### Quarterbacks (2)\n"
                "| Player | Pos | Status |\n"
                "|---|---|---|\n"
                "| Kirk Cousins | QB | Offseason roster |\n"
                "| New Quarterback | QB | Offseason roster |\n\n"
                "### Receivers (1)\n"
                "| Player | Pos | Status |\n"
                "|---|---|---|\n"
                "| Practice Player | WR | Offseason roster (reserve/future contract effective March 11) |\n\n"
                "## Departures\n",
                encoding="utf-8",
            )
            exit_index = tmp / "exit.json"
            exit_index.write_text(
                json.dumps(
                    {
                        "season": 2013,
                        "count": 2,
                        "players": [
                            {"player": "Kirk Cousins", "pos": "QB"},
                            {"player": "Practice Player", "pos": "WR"},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            manifest = build_manifest(roster, exit_index)
            by_name = {row["player"]: row for row in manifest["players"]}
            self.assertEqual(
                by_name["Kirk Cousins"]["continuity"],
                "returning_2013_jaguar",
            )
            self.assertEqual(
                by_name["Practice Player"]["continuity"],
                "practice_squad_to_reserve_future",
            )
            self.assertEqual(
                by_name["New Quarterback"]["continuity"],
                "new_2014_acquisition",
            )

    def test_committed_manifest_is_current(self):
        generated = build_manifest(ROSTER, EXIT_INDEX)
        committed = json.loads(OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(committed, generated)


if __name__ == "__main__":
    unittest.main()
