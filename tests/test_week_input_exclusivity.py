import contextlib
import io
import json
import sys
import tempfile
import unittest
from unittest import mock
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

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

    def test_dated_status_parentheticals_still_mark_control(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"roster.md"
            path.write_text(
                "| Player | Pos | Status | Availability | Role |\n"
                "|---|---|---|---|---|\n"
                "| Kirk Cousins | QB | Active 53 (signed August 31, 2014) | No communicated restriction | QB1 |\n"
                "| Tyler Bray | QB | Practice squad (signed September 1, 2014) | No communicated restriction | — |\n"
                "| Cameron Brate | TE | Injured reserve (September 2, 2014) | Out | — |\n"
                "| Jerrell Jackson | WR | Reserve/Injured (September 2, 2014) | Out | — |\n"
                "| Austen Lane | DE | Claimed on waivers (August 31, 2013) | — | — |\n",
                encoding="utf-8",
            )
            self.assertEqual(controlled_players_from_roster(path),
                             {"Kirk Cousins","Tyler Bray","Cameron Brate","Jerrell Jackson"})

    def test_cli_roster_defaults_to_the_season_roster(self):
        from scripts import check_week_input_exclusivity as cli
        data={"games":[{
            "away":"Jacksonville Jaguars","home":"Philadelphia Eagles",
            "away_input":{"active_players":["QB:Somebody Else"],"roster":[]},
            "home_input":{"active_players":["QB:Kirk Cousins"],"roster":[]},
        }]}
        with tempfile.TemporaryDirectory() as tmp:
            package=Path(tmp)/"week_01_inputs.json"
            package.write_text(json.dumps(data),encoding="utf-8")
            out=io.StringIO()
            with mock.patch.object(sys,"argv",["x",str(package),"--season","2014"]), \
                    contextlib.redirect_stdout(out):
                code=cli.main()
        # Cousins is Jacksonville-controlled on the 2014 roster, so the 2014
        # default roster (not career/2013/roster.md) must flag him.
        self.assertEqual(code,1)
        self.assertIn("Kirk Cousins: Jacksonville-controlled player appears on Philadelphia Eagles",out.getvalue())

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



class PackageSeasonTests(unittest.TestCase):
    """The CLI reads control from the package's own season's roster when no
    --season is given, refuses a --season that differs from the package's,
    and keeps the 2013 default for a package without a season key."""

    ROSTERS={2013:"| Player | Pos | Status |\n|---|---|---|\n| Old Player | QB | Active 53 |\n",
             2014:"| Player | Pos | Status |\n|---|---|---|\n| New Player | QB | Active 53 |\n"}

    def run_cli(self, package, *argv):
        from scripts import check_week_input_exclusivity as cli
        requested=[]
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp)
            for season,text in self.ROSTERS.items():
                (tmp/("roster_%d.md" % season)).write_text(text,encoding="utf-8")

            def paths(season, root):
                requested.append(season)
                return SimpleNamespace(roster=tmp/("roster_%d.md" % season))
            path=tmp/"week_05_inputs.json"
            path.write_text(json.dumps(package),encoding="utf-8")
            out=io.StringIO()
            with mock.patch.object(cli,"SeasonPaths",paths), \
                    mock.patch.object(sys,"argv",["x",str(path)]+list(argv)), \
                    contextlib.redirect_stdout(out):
                code=cli.main()
        return code,out.getvalue(),requested

    @staticmethod
    def package(season=None):
        away=WeekInputExclusivityTests.full_input("NYG","Old Player")
        away["roster"][1]["player_id"]="New Player"
        away["active_players"]=game_day_actives(away["roster"])
        data={"games":[{"away":"New York Giants","home":"Jacksonville Jaguars","away_input":away,
                        "home_input":WeekInputExclusivityTests.full_input("JAX","Jacksonville QB")}]}
        if season is not None:
            data["season"]=season
        return data

    def test_a_2014_package_without_season_uses_the_2014_roster(self):
        code,out,requested=self.run_cli(self.package(2014),"--expected-games","1")
        self.assertEqual((code,requested),(1,[2014]))
        self.assertIn("New Player: Jacksonville-controlled player appears on New York Giants",out)
        self.assertNotIn("Old Player",out)
        code,out,requested=self.run_cli(self.package(2014),"--season","2014")
        self.assertEqual((code,requested),(1,[2014]))
        self.assertIn("New Player: Jacksonville-controlled",out)

    def test_a_season_that_differs_from_the_package_is_blocked(self):
        code,out,requested=self.run_cli(self.package(2014),"--season","2013")
        self.assertEqual(code,1)
        self.assertIn("WEEK_INPUT_EXCLUSIVITY: BLOCKED",out)
        self.assertIn("the package is for season 2014, not --season 2013",out)
        self.assertEqual(requested,[])  # refused before any roster is read
        code,out,_=self.run_cli(self.package("twenty"))
        self.assertEqual(code,1)
        self.assertIn("is not a season year",out)

    def test_a_package_without_a_season_key_keeps_the_2013_default(self):
        code,out,requested=self.run_cli(self.package())
        self.assertEqual((code,requested),(1,[2013]))
        self.assertIn("Old Player: Jacksonville-controlled player appears on New York Giants",out)
        self.assertNotIn("New Player",out)
        code,out,requested=self.run_cli(self.package(),"--season","2014")
        self.assertEqual((code,requested),(1,[2014]))
        self.assertIn("New Player: Jacksonville-controlled",out)
        # A list is not a package: no season, the 2013 default, and blocked.
        code,out,requested=self.run_cli([])
        self.assertEqual((code,requested),(1,[2013]))
        self.assertIn("requires a nonempty games list",out)

    def test_a_clean_package_of_its_own_season_is_ready(self):
        data=self.package(2014)
        for row in data["games"][0]["away_input"]["roster"]:
            if row["player_id"] in {"Old Player","New Player"}:
                row["player_id"]="Giants "+row["player_id"]
        data["games"][0]["away_input"]["active_players"]=game_day_actives(data["games"][0]["away_input"]["roster"])
        code,out,requested=self.run_cli(data,"--expected-games","1")
        self.assertEqual((code,requested),(0,[2014]),out)
        self.assertIn("WEEK_INPUT_EXCLUSIVITY: READY",out)


if __name__=="__main__":
    unittest.main()
