import json
import unittest
from pathlib import Path

from scripts.build_player_progression_roster import build_manifest

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "career/2014/roster.md"
EXIT_INDEX = (
    ROOT
    / "career/2014/offseason/player_development/2013_exit_player_index.json"
)
OUTPUT = (
    ROOT
    / "career/2014/offseason/player_development/progression_roster.json"
)


class PlayerProgressionRosterTests(unittest.TestCase):
    def test_current_roster_drives_progression_cohort(self):
        manifest = build_manifest(ROSTER, EXIT_INDEX)
        self.assertEqual(manifest["counts"]["controlled_players"], 53)
        self.assertEqual(
            manifest["counts"]["jacksonville_2013_continuity"], 48
        )
        self.assertEqual(manifest["counts"]["returning_2013_jaguar"], 42)
        self.assertEqual(
            manifest["counts"]["practice_squad_to_reserve_future"], 6
        )
        self.assertEqual(manifest["counts"]["new_2014_acquisition"], 5)

        by_name = {row["player"]: row for row in manifest["players"]}
        self.assertEqual(
            by_name["Kirk Cousins"]["continuity"],
            "returning_2013_jaguar",
        )
        self.assertEqual(
            by_name["Tyler Bray"]["continuity"],
            "practice_squad_to_reserve_future",
        )
        self.assertEqual(
            by_name["Hakeem Nicks"]["continuity"],
            "new_2014_acquisition",
        )
        self.assertNotIn("Uche Nwaneri", by_name)
        self.assertNotIn("Jason Babin", by_name)
        self.assertNotIn("Tyson Alualu", by_name)

    def test_newcomers_are_not_given_jacksonville_continuity(self):
        manifest = build_manifest(ROSTER, EXIT_INDEX)
        newcomers = {
            row["player"]
            for row in manifest["players"]
            if row["continuity"] == "new_2014_acquisition"
        }
        self.assertEqual(
            newcomers,
            {
                "Hakeem Nicks",
                "Andrew Hawkins",
                "Daniel Te'o-Nesheim",
                "Alterraun Verner",
                "Aqib Talib",
            },
        )

    def test_committed_manifest_is_current(self):
        generated = build_manifest(ROSTER, EXIT_INDEX)
        committed = json.loads(OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(committed, generated)


if __name__ == "__main__":
    unittest.main()
