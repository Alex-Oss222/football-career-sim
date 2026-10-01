"""The 2014 awards methodology freeze and scripts/league_awards.py's guarded states."""
import contextlib
import io
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.seasons import SeasonPaths
from scripts import league_awards
from scripts.render_award_pages import render_pages


class Methodology2014Tests(unittest.TestCase):
    def setUp(self):
        self.m2013 = json.loads((ROOT / "career/2013/awards/methodology.json").read_text())
        self.m2014 = league_awards.method(2014)

    def test_freeze_mirrors_2013_method(self):
        for key in ("procedure", "categories", "award_names", "shortlist_size", "panel_weights", "panel_rule", "formulas"):
            self.assertEqual(self.m2014[key], self.m2013[key], key)
        self.assertEqual(self.m2014["procedure_tag"], "v1-2014")
        self.assertEqual(self.m2014["frozen"]["date"], "2014-08-28")
        self.assertEqual(self.m2014["frozen"]["mirrors"], "career/2013/awards/methodology.json")
        self.assertEqual(league_awards.event_id("week", 1, "AFC-offense", self.m2014, 2014),
                         "2014-award-week01-afc-offense-v1-2014")

    def test_months_cover_the_fixture_weeks_by_nfl_week(self):
        weeks = sorted({g["week"] for g in SeasonPaths(2014, ROOT).regular_games()})
        covered = [w for month in self.m2014["months"].values() for w in month["weeks"]]
        self.assertEqual(sorted(covered), weeks)
        self.assertEqual({k: v["weeks"] for k, v in self.m2014["months"].items()},
                         {"September": [1, 2, 3, 4], "October": [5, 6, 7, 8],
                          "November": [9, 10, 11, 12], "December": [13, 14, 15, 16, 17]})
        self.assertIn("by week, not by calendar date", self.m2014["month_rule"])

    def test_readme_carries_the_freeze(self):
        pages = render_pages(2014, {}, self.m2014)
        self.assertIn("## Methodology", pages["README.md"])
        self.assertIn("Frozen August 28, 2014", pages["README.md"])
        self.assertNotIn("Before the first draw, freeze", pages["README.md"])
        # Without a freeze the index keeps its reminder.
        self.assertIn("Before the first draw, freeze", render_pages(2014, {})["README.md"])

    def test_missing_methodology_is_a_clear_error(self):
        with self.assertRaisesRegex(FileNotFoundError, "No 2015 awards methodology: freeze "
                                    "career/2015/05_Regular_Season/Awards/methodology.json"):
            league_awards.method(2015)

    def test_dry_run_reports_missing_receipts_instead_of_crashing(self):
        out = io.StringIO()
        with mock.patch.object(league_awards, "require_game_release"), \
                mock.patch.object(sys, "argv", ["x", "week", "1", "--season", "2014"]), \
                contextlib.redirect_stdout(out):
            code = league_awards.main()
        self.assertEqual(code, 1)
        self.assertIn("AWARDS: BLOCKED\n- no closed 2014 receipt for week 1", out.getvalue())
        out = io.StringIO()
        with mock.patch.object(league_awards, "require_game_release"), \
                mock.patch.object(sys, "argv", ["x", "month", "September", "--season", "2014"]), \
                contextlib.redirect_stdout(out):
            self.assertEqual(league_awards.main(), 1)
        self.assertIn("no closed 2014 receipt for month September", out.getvalue())


if __name__ == "__main__":
    unittest.main()
