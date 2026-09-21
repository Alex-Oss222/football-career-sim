import tempfile
import unittest
from pathlib import Path

from scripts.check_week_input_exclusivity import (
    check_inputs,
    controlled_players_from_roster,
)


class WeekInputExclusivityTests(unittest.TestCase):
    def test_roster_parser_includes_active_and_practice_squad(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"roster.md"
            path.write_text(
                "| Player | Current status |\n"
                "|---|---|\n"
                "| Kirk Cousins | Active 53 |\n"
                "| Brent Grimes | Active 53 |\n"
                "\n"
                "**Jacksonville practice squad (not active 53):** "
                "Tyler Bray, Brandon King.\n",
                encoding="utf-8",
            )
            self.assertEqual(
                controlled_players_from_roster(path),
                {"Kirk Cousins","Brent Grimes","Tyler Bray","Brandon King"},
            )

    def test_current_branch_roster_parser_sees_active_and_practice_squad(self):
        root=Path(__file__).resolve().parents[1]
        controlled=controlled_players_from_roster(root/"career/2013/roster.md")
        self.assertIn("Kirk Cousins",controlled)
        self.assertIn("Tyler Bray",controlled)
        self.assertIn("Jordan Poyer",controlled)
        self.assertIn("C.J. Anderson",controlled)

    def test_branch_controlled_player_on_background_team_fails(self):
        data={
            "games":[{
                "away":"Kansas City Chiefs",
                "home":"Jacksonville Jaguars",
                "away_input":{
                    "active_players":["QB:Tyler Bray"],
                    "roster":[{"player_id":"Tyler Bray","position":"QB"}],
                },
                "home_input":{
                    "active_players":["QB:Kirk Cousins"],
                    "roster":[{"player_id":"Kirk Cousins","position":"QB"}],
                },
            }]
        }
        errors=check_inputs(
            data,{"Kirk Cousins","Tyler Bray"},"Jacksonville Jaguars")
        self.assertTrue(any("Tyler Bray" in error for error in errors))

    def test_same_player_on_two_nonprotagonist_teams_fails(self):
        data={
            "games":[
                {
                    "away":"A","home":"B",
                    "away_input":{"active_players":["WR:Shared Player"],"roster":[]},
                    "home_input":{"active_players":["QB:B QB"],"roster":[]},
                },
                {
                    "away":"C","home":"D",
                    "away_input":{"active_players":["WR:Shared Player"],"roster":[]},
                    "home_input":{"active_players":["QB:D QB"],"roster":[]},
                },
            ]
        }
        errors=check_inputs(data,set(),"Jacksonville Jaguars")
        self.assertTrue(any("multiple weekly TeamInputs" in error for error in errors))

    def test_clean_slate_passes(self):
        data={
            "games":[{
                "away":"Oakland Raiders",
                "home":"Jacksonville Jaguars",
                "away_input":{
                    "active_players":["QB:Oakland QB"],
                    "roster":[{"player_id":"Oakland QB","position":"QB"}],
                },
                "home_input":{
                    "active_players":["QB:Kirk Cousins"],
                    "roster":[{"player_id":"Kirk Cousins","position":"QB"}],
                },
            }]
        }
        self.assertEqual(
            check_inputs(data,{"Kirk Cousins"},"Jacksonville Jaguars"),[]
        )


if __name__=="__main__":
    unittest.main()
