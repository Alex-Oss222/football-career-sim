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


if __name__ == "__main__":
    unittest.main()
