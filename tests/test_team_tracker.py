import json
import unittest
from pathlib import Path

from scripts.render_team_tracker import check, load_games, totals

ROOT = Path(__file__).resolve().parents[1]


class TeamTrackerTests(unittest.TestCase):
    def test_totals_match_the_season_statbook(self):
        games = load_games(ROOT, 2013, "Jacksonville Jaguars")
        mine = totals([g for g in games if g["kind"] == "regular"])
        book = json.loads((ROOT / "career/2013/stats/season_totals.json").read_text())
        for name, line in book["players"].items():
            if line.get("teams") != ["Jacksonville Jaguars"]:
                continue
            for field, value in line.items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    self.assertEqual(mine[name].get(field, 0), value, (name, field))

    def test_one_page_per_game_and_current(self):
        games = load_games(ROOT, 2013, "Jacksonville Jaguars")
        self.assertEqual(sum(g["kind"] == "regular" for g in games), 16)
        self.assertEqual(sum(g["kind"] == "postseason" for g in games), 2)
        self.assertEqual(check(ROOT, 2013), [])
        self.assertEqual(check(ROOT, 2014), [])


if __name__ == "__main__":
    unittest.main()
