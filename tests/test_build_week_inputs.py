"""scripts/build_week_inputs.py: the information gate and its messages."""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime import week_inputs
from scripts import build_week_inputs


class InformationGateTests(unittest.TestCase):
    def test_build_refuses_before_the_jacksonville_game_day(self):
        # 2014 Week 1: Jacksonville at Philadelphia, September 7, 2014.
        with mock.patch.object(build_week_inputs, "master_date", return_value=date(2014, 8, 28)):
            error = build_week_inputs.information_gate_error(1, 2014)
        self.assertIn("master clock is 2014-08-28", error)
        self.assertIn("2014-09-07", error)
        with mock.patch.object(build_week_inputs, "master_date", return_value=date(2014, 9, 7)):
            self.assertIsNone(build_week_inputs.information_gate_error(1, 2014))

    def test_bye_week_gates_on_the_slate_first_date(self):
        # 2014 Week 11 is Jacksonville's bye; the slate opens Thursday November 13.
        games = week_inputs.schedule(11, 2014)
        self.assertFalse(any("Jacksonville Jaguars" in (g["away"], g["home"]) for g in games))
        with mock.patch.object(build_week_inputs, "master_date", return_value=date(2014, 11, 12)):
            self.assertIn("week's first game day of 2014-11-13", build_week_inputs.information_gate_error(11, 2014))
        with mock.patch.object(build_week_inputs, "master_date", return_value=date(2014, 11, 13)):
            self.assertIsNone(build_week_inputs.information_gate_error(11, 2014))

    def test_closed_2013_weeks_are_past_the_gate(self):
        self.assertIsNone(build_week_inputs.information_gate_error(1, 2013))

    def test_cli_blocks_before_game_day(self):
        out = io.StringIO()
        with mock.patch.object(build_week_inputs, "require_game_release"), \
                mock.patch.object(build_week_inputs, "master_date", return_value=date(2014, 9, 6)), \
                mock.patch.object(sys, "argv", ["x", "1", "--season", "2014"]), \
                contextlib.redirect_stdout(out):
            code = build_week_inputs.main()
        self.assertEqual(code, 1)
        self.assertIn("WEEK_INPUTS: BLOCKED\n- Information gate", out.getvalue())


class CallSheetMessageTests(unittest.TestCase):
    def test_missing_call_sheet_message_names_the_expected_path(self):
        out = io.StringIO()
        with mock.patch.object(build_week_inputs, "require_game_release"), \
                mock.patch.object(build_week_inputs, "information_gate_error", return_value=None), \
                mock.patch.object(build_week_inputs, "call_sheet_path", return_value=None), \
                mock.patch.object(sys, "argv", ["x", "1", "--season", "2014"]), \
                contextlib.redirect_stdout(out):
            code = build_week_inputs.main()
        self.assertEqual(code, 1)
        self.assertIn("No Jacksonville call sheet for Week 1: Stone's weekly plan must be frozen as "
                      "career/2014/05_Regular_Season/Games/Week_01/call_sheet.json", out.getvalue())


class ActiveStatusTests(unittest.TestCase):
    def test_active_53_matches_with_a_dated_parenthetical(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "roster.md"
            path.write_text(
                "| Player | Pos | Status | Availability | Role |\n"
                "|---|---|---|---|---|\n"
                "| Kirk Cousins | QB | Active 53 (signed August 31, 2014) | No communicated restriction | QB1 |\n"
                "| Chad Henne | QB | Active 53 | No communicated restriction | QB2 |\n"
                "| Tyler Bray | QB | Practice squad (signed September 1, 2014) | No communicated restriction | — |\n"
                "| Active 53 Man | WR | Active 53rd rower | No communicated restriction | — |\n",
                encoding="utf-8")
            rows = week_inputs.controlled_active(2014, roster_path=path)
        self.assertEqual([name for name, _ in rows], ["Kirk Cousins", "Chad Henne"])


if __name__ == "__main__":
    unittest.main()
