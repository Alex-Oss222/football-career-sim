import json
import re
from datetime import date, timedelta
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from runtime import player_bios, week_inputs
from scripts import render_player_ages
from runtime.seasons import current_record

ROOT = Path(__file__).resolve().parents[1]


class PlayerBiographyTests(unittest.TestCase):
    def test_completed_birthdays_and_calendar_rollover(self):
        self.assertEqual(player_bios.age_on("1989-01-05", "2013-12-29"), 24)
        self.assertEqual(player_bios.age_on("1989-01-05", "2014-01-04"), 24)
        self.assertEqual(player_bios.age_on("1989-01-05", "2014-01-05"), 25)
        self.assertEqual(player_bios.age_on("1991-12-27", "2013-12-26"), 21)
        self.assertEqual(player_bios.age_on("1991-12-27", "2013-12-29"), 22)

    def test_leap_day_and_invalid_dates(self):
        self.assertEqual(player_bios.age_on("1988-02-29", date(2013, 2, 28)), 24)
        self.assertEqual(player_bios.age_on("1988-02-29", date(2013, 3, 1)), 25)
        self.assertEqual(player_bios.age_on("1988-02-29", date(2012, 2, 29)), 24)
        with self.assertRaises(ValueError):
            player_bios.age_on("1988-02-30", "2013-12-29")
        with self.assertRaises(ValueError):
            player_bios.age_on("1988-02-29", "1987-12-29")

    def test_namesakes_are_reviewed_identities(self):
        bios = player_bios.biographies(["C.J. Mosley", "C.J. Wilson", "Brandon King", "Mike Brown"], "2013-12-29")
        self.assertEqual(bios["C.J. Mosley"]["gsis_id"], "00-0023624")
        self.assertEqual(bios["C.J. Mosley"]["age"], 30)
        self.assertEqual(bios["C.J. Wilson"]["birth_date"], "1987-03-30")
        self.assertEqual(bios["Brandon King"]["birth_date"], "1987-01-28")
        self.assertEqual(bios["Mike Brown"]["birth_date"], "1989-02-09")

    def test_missing_or_unsourced_birthday_fails_preparation(self):
        with self.assertRaisesRegex(ValueError, "Verify birth date"):
            player_bios.biographies(["New signing"], "2014-01-01", {})
        with self.assertRaisesRegex(ValueError, "Verify birth date"):
            player_bios.biographies(["New signing"], "2014-01-01", {"New signing": {"birth_date": None}})

    def test_current_views_and_practice_squad_are_complete(self):
        self.assertEqual(render_player_ages.check(), [])
        roster = current_record('roster').read_text()
        names = [n for n, _, _ in render_player_ages.controlled_rows(roster)]
        # 78 controlled at May 12, 2014 (Entry 108: 53 plus nine draftees and
        # 17 undrafted rookies; Entry 110: Rackley traded); the six
        # reserve/future players also appear in the section 4 history table.
        self.assertEqual(len(set(names)), 78)
        self.assertIn("| Tyler Bray | QB | 1991-12-27 | 22 | Offseason roster (reserve/future contract effective March 11) |", roster)

    def test_regeneration_replaces_stale_age_and_is_idempotent(self):
        text = "<!-- player-ages-as-of: 2013-12-29 -->\n\n| Player | Pos | DOB | Age | Status |\n|---|---|---|---:|---|\n| Mike Harris | CB | 1900-01-01 | 99 | Active 53 |\n"
        result = render_player_ages.table_ages(text, date(2014, 1, 5), player_bios.load())
        self.assertIn("| Mike Harris | CB | 1989-01-05 | 25 | Active 53 |", result)
        self.assertIn("player-ages-as-of: 2014-01-05", result)
        self.assertEqual(render_player_ages.table_ages(result, date(2014, 1, 5), player_bios.load()), result)

    def test_stale_views_are_rejected_even_without_a_birthday(self):
        with tempfile.TemporaryDirectory(dir=ROOT.parent) as d:
            root = Path(d)
            current = [current_record(name).relative_to(ROOT) for name in ('roster','player_ages','background_depth')]
            for path in (player_bios.REGISTRY, "docs/repository_map.json", "state/05_Current_Season_State.md",
                         "state/04_Roster_and_Staff_Register.md", *current):
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((ROOT / path).read_bytes())
            p = root / "state/05_Current_Season_State.md"
            next_day = player_bios.master_date(root) + timedelta(days=1)
            label = f"{next_day:%B} {next_day.day}, {next_day.year}"
            p.write_text(re.sub(r"(\| Master date/time \| )[A-Za-z]+ \d{1,2}, \d{4}",
                                lambda m: m[1] + label, p.read_text()))
            self.assertEqual(len(render_player_ages.check(root)), 3)

    def test_game_date_metadata_does_not_change_team_input(self):
        # Meester remains rostered in January; a historical retirement date is
        # never a branch transaction. Public ages stay outside the seed packet.
        game = {"week": 18, "date": "2014-01-04", "away": "Jacksonville Jaguars",
                "home": "Kansas City Chiefs", "site": "home", "game_type": "postseason"}
        jax = {"roster": [{"player_id": "Brad Meester"}, {"player_id": "Mike Harris"}]}
        kc = {"roster": [{"player_id": "Alex Smith (KC)"}]}
        with mock.patch.object(week_inputs, "schedule", return_value=[game]), \
                mock.patch.object(week_inputs, "jacksonville_input", return_value=jax), \
                mock.patch.object(week_inputs, "background_input", return_value=kc):
            built = week_inputs.build_package(18, [], [], {})["games"][0]
        self.assertEqual(built["away_input"], jax)
        self.assertEqual(built["home_input"], kc)
        self.assertEqual(built["player_ages"]["Brad Meester"]["age"], 36)
        self.assertEqual(built["player_ages"]["Mike Harris"]["age"], 24)
        self.assertNotIn("retirement", json.dumps(built))

    def test_unverified_age_is_allowed_only_for_named_background_players(self):
        players = {"Known": {"gsis_id": "00-0000001", "birth_date": "1990-08-09", "sources": ["x"]},
                   "Dated-less": {"gsis_id": "00-0000002", "birth_date": None, "sources": ["x"]}}
        with self.assertRaisesRegex(ValueError, "Verify birth date before preparing player: No Record"):
            player_bios.biographies(["Known", "No Record"], "2014-08-08", players)
        with self.assertRaisesRegex(ValueError, "Dated-less"):
            player_bios.biographies(["Dated-less"], "2014-08-08", players, allow_unverified=["No Record"])
        ages = player_bios.biographies(["Known", "No Record", "Dated-less"], "2014-08-08", players,
                                       allow_unverified=["No Record", "Dated-less"])
        self.assertEqual(ages["Known"], {"gsis_id": "00-0000001", "birth_date": "1990-08-09", "age": 23})
        self.assertEqual(ages["No Record"], {"gsis_id": None, "birth_date": None, "age": None, "age_unverified": True})
        self.assertEqual(ages["Dated-less"]["gsis_id"], "00-0000002")
        self.assertEqual(player_bios.unverified_ages(ages), ["Dated-less", "No Record"])
        self.assertEqual(player_bios.unverified_ages(None), [])

    def test_weekly_package_flags_only_background_unverified_ages(self):
        game = {"week": 1, "date": "2014-09-07", "away": "Jacksonville Jaguars", "home": "Philadelphia Eagles",
                "site": "home"}
        jax = {"team_id": "Jacksonville Jaguars", "roster": [{"player_id": "Brad Meester", "available": True}]}
        phi = {"team_id": "Philadelphia Eagles",
               "roster": [{"player_id": "Mike Harris", "available": True}, {"player_id": "Nobody Listed", "available": True}]}
        patches = (mock.patch.object(week_inputs, "schedule", return_value=[game]),
                   mock.patch.object(week_inputs, "jacksonville_input", return_value=jax),
                   mock.patch.object(week_inputs, "background_input", return_value=phi),
                   mock.patch.object(week_inputs.strength, "team_strength", return_value=(None, {})))
        with patches[0], patches[1], patches[2], patches[3]:
            row = week_inputs.build_package(1, [], [], {}, season=2014)["games"][0]
        self.assertEqual(row["player_ages"]["Nobody Listed"],
                         {"gsis_id": None, "birth_date": None, "age": None, "age_unverified": True})
        self.assertEqual(row["player_ages"]["Brad Meester"]["age"], 37)
        self.assertEqual(player_bios.unverified_ages(row["player_ages"]), ["Nobody Listed"])
        # The same name on Jacksonville's side still fails closed.
        jax["roster"].append(phi["roster"].pop())
        with patches[0], patches[1], patches[2], patches[3], \
                self.assertRaisesRegex(ValueError, "Verify birth date before preparing player: Nobody Listed"):
            week_inputs.build_package(1, [], [], {}, season=2014)

    def test_week1_library_birth_dates_are_registered_or_named_unverified(self):
        library = json.loads((ROOT / "library/data/2014_week1_depth_charts.json").read_text())
        registry = player_bios.load()
        unverified = [p["player_id"] for club in library["clubs"].values() for p in club["players"]
                      if p["player_id"] not in registry]
        # Phil Bates carries no birth date in the library; he enters a weekly
        # package only as a background player flagged age_unverified.
        self.assertEqual(unverified, ["Phil Bates"])
        self.assertEqual(registry["Logan Thomas"]["evidence"], "library_week1_source")
        self.assertEqual(registry["Jay Ratliff"]["alias_of"], "Jeremiah Ratliff")
        self.assertEqual(registry["Jay Ratliff"]["gsis_id"], registry["Jeremiah Ratliff"]["gsis_id"])

    def test_preseason_package_flags_only_opponent_unverified_ages(self):
        from runtime import preseason
        game = {"game": 1, "game_id": "2014-preseason-01-tampa-bay-buccaneers-at-jacksonville-jaguars",
                "date": "2014-08-08", "away": "Tampa Bay Buccaneers", "home": "Jacksonville Jaguars"}
        jax = {"team_id": "JAX", "roster": [{"player_id": "Brad Meester"}]}
        tb = {"team_id": "TB", "roster": [{"player_id": "Mike Harris"}, {"player_id": "Nobody Listed"}]}
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "call_sheet.json").write_text(json.dumps({"offensive_call_sheet": []}))
            paths = mock.Mock(year=2014)
            paths.preseason_game.return_value = game
            paths.preseason_folder.return_value = Path(tmp)
            patches = (mock.patch.object(preseason, "opponent_input", return_value=tb),
                       mock.patch.object(preseason.strength, "team_strength", return_value=(None, {})))
            with patches[0], patches[1], mock.patch.object(preseason, "jacksonville_input", return_value=jax):
                row = preseason.build_package(paths, 1, [])["games"][0]
            self.assertEqual(row["player_ages"]["Nobody Listed"],
                             {"gsis_id": None, "birth_date": None, "age": None, "age_unverified": True})
            self.assertEqual(row["player_ages"]["Brad Meester"]["age"], 37)
            self.assertEqual(player_bios.unverified_ages(row["player_ages"]), ["Nobody Listed"])
            # The same name on Jacksonville's side still fails closed.
            jax["roster"].append(tb["roster"].pop())
            with patches[0], patches[1], mock.patch.object(preseason, "jacksonville_input", return_value=jax), \
                    self.assertRaisesRegex(ValueError, "Verify birth date before preparing player: Nobody Listed"):
                preseason.build_package(paths, 1, [])

if __name__ == "__main__":
    unittest.main()
