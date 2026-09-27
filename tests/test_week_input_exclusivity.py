import sys
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from support_rosters import game_day_roster

from runtime.week_inputs import game_day_actives
from scripts.check_week_input_exclusivity import (
    check_inputs,
    controlled_players_from_roster,
)


class WeekInputExclusivityTests(unittest.TestCase):
    def test_roster_parser_includes_active_and_practice_squad(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"roster.md"
            path.write_text(
                "| Player | Pos | Status | Availability | Role |\n"
                "|---|---|---|---|---|\n"
                "| Kirk Cousins | QB | Active 53 | No communicated restriction | QB1 |\n"
                "| Brent Grimes | CB | Active 53 | No communicated restriction | — |\n"
                "\n"
                "| Player | Pos | Status |\n"
                "|---|---|---|\n"
                "| Tyler Bray | QB | Practice squad |\n"
                "| Brandon King | DB | Practice squad |\n"
                "\n"
                "| Player | Current branch status |\n"
                "|---|---|\n"
                "| Austen Lane | Claimed on waivers |\n",
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


    def test_expected_game_count_rejects_partial_slate(self):
        data={
            "games":[{
                "away":"Oakland Raiders","home":"Jacksonville Jaguars",
                "away_input":{"active_players":["QB:Oakland QB"],"roster":[]},
                "home_input":{"active_players":["QB:Kirk Cousins"],"roster":[]},
            }]
        }
        errors=check_inputs(
            data,{"Kirk Cousins"},"Jacksonville Jaguars",expected_games=16
        )
        self.assertTrue(any("expected 16" in error for error in errors))

    def test_same_team_in_two_weekly_games_fails(self):
        data={
            "games":[
                {
                    "away":"A","home":"B",
                    "away_input":{"active_players":["QB:A QB"],"roster":[]},
                    "home_input":{"active_players":["QB:B QB"],"roster":[]},
                },
                {
                    "away":"A","home":"C",
                    "away_input":{"active_players":["QB:A QB"],"roster":[]},
                    "home_input":{"active_players":["QB:C QB"],"roster":[]},
                },
            ]
        }
        errors=check_inputs(data,set(),"Jacksonville Jaguars")
        self.assertTrue(any("appears in multiple weekly games" in error for error in errors))

    @staticmethod
    def full_input(prefix, qb_name):
        roster=[asdict(p) for p in game_day_roster(prefix)]
        roster[0]["player_id"]=qb_name
        return {"active_players":game_day_actives(roster),"roster":roster}

    def test_clean_slate_passes(self):
        data={
            "games":[{
                "away":"Oakland Raiders",
                "home":"Jacksonville Jaguars",
                "away_input":self.full_input("OAK","Oakland QB"),
                "home_input":self.full_input("JAX","Kirk Cousins"),
            }]
        }
        self.assertEqual(
            check_inputs(data,{"Kirk Cousins"},"Jacksonville Jaguars"),[]
        )

    def test_thin_or_depthless_input_fails(self):
        thin=self.full_input("HOU","Houston QB")
        thin["roster"]=[r for r in thin["roster"] if r["position"] not in {"RB","OLB","ILB"}]
        thin["active_players"]=[r["player_id"] for r in thin["roster"]]
        depthless=self.full_input("JAX","Kirk Cousins")
        for row in depthless["roster"]:
            row["depth"]=None
        data={"games":[{"away":"Houston Texans","home":"Jacksonville Jaguars",
                        "away_input":thin,"home_input":depthless}]}
        errors=check_inputs(data,{"Kirk Cousins"},"Jacksonville Jaguars")
        self.assertTrue(any("Houston Texans: game-day unit incomplete: RB" in e for e in errors))
        self.assertTrue(any("Houston Texans: game-day unit incomplete: LB" in e for e in errors))
        self.assertTrue(any("Jacksonville Jaguars: QB group has no explicit depth order" in e for e in errors))


if __name__=="__main__":
    unittest.main()
