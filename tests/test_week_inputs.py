import json
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from runtime import week_inputs
from runtime.league import TEAMS
from scripts.build_week_inputs import AVERAGE_ANCHORS
from scripts.check_week_input_exclusivity import check_inputs, controlled_players_from_roster
from scripts.render_season_stats import load_receipts

ROOT = Path(__file__).resolve().parents[1]
WEEK1_SHEET = ROOT / "career/2013/regular_season/week_01_kansas_city_at_jacksonville/call_sheet.json"


def injury_receipt(player, days, restriction="out"):
    return {"week": 1, "away": "Kansas City Chiefs", "home": "Jacksonville Jaguars",
            "injuries": [{"team": "Kansas City Chiefs", "player": player, "injury_class": "lower_extremity",
                          "restriction": restriction, "return_days": days}]}


class ScheduleTests(unittest.TestCase):
    def test_every_club_plays_once_in_week_two(self):
        games = week_inputs.schedule(2)
        clubs = [team for g in games for team in (g["away"], g["home"])]
        self.assertEqual(len(games), 16)
        self.assertEqual(sorted(clubs), sorted(TEAMS))

    def test_bye_weeks_shrink_the_slate(self):
        self.assertLess(len(week_inputs.schedule(4)), 16)

    def test_identifiers_are_stable(self):
        game = next(g for g in week_inputs.schedule(2) if g["home"] == "Oakland Raiders")
        self.assertEqual(week_inputs.event_id(game), "2013-week02-jacksonville-jaguars-at-oakland-raiders")
        self.assertEqual(week_inputs.receipt_name(game), "week_02_jacksonville_jaguars_at_oakland_raiders.json")


class AvailabilityTests(unittest.TestCase):
    def test_injury_holds_until_projected_return(self):
        receipts = [injury_receipt("Eric Kush", 12)]
        self.assertIn("Eric Kush", week_inputs.injured_out(receipts, date(2013, 9, 15)))
        self.assertNotIn("Eric Kush", week_inputs.injured_out(receipts, date(2013, 9, 20)))

    def test_roster_note_with_projected_return_clears_on_that_date(self):
        note = "Out, upper extremity (Week 2); projected return September 27"
        self.assertFalse(week_inputs.roster_available(note, date(2013, 9, 22)))
        self.assertTrue(week_inputs.roster_available(note, date(2013, 9, 29)))
        self.assertTrue(week_inputs.roster_available(
            "Out, trunk (Week 2); projected return January 30, 2014", date(2014, 2, 1)))
        self.assertFalse(week_inputs.roster_available("Independent medical hold", date(2013, 12, 1)))
        self.assertTrue(week_inputs.roster_available(
            "Limited, no projected absence (upper extremity, Week 5)", date(2013, 10, 13)))

    def test_limited_without_days_does_not_sit_a_player(self):
        receipts = [injury_receipt("Matt Kalil", 0, restriction="limited")]
        self.assertEqual(week_inputs.injured_out(receipts, date(2013, 9, 15)), {})


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sheet = json.loads(WEEK1_SHEET.read_text())["offensive_call_sheet"]
        receipts = [r for r in load_receipts(ROOT / "career/2013/stats/game_receipts") if int(r["week"]) < 2]
        cls.sheet, cls.receipts = sheet, receipts
        # Week 2 rebuilt with today's roster notes: players hurt later (for
        # example Kelce, Week 13) are dated out, so the 46-man gate is relaxed
        # for this structural rebuild and tested on its own below.
        with mock.patch.object(week_inputs, "GAME_DAY_ACTIVES", 0):
            cls.package = week_inputs.build_package(2, receipts, sheet, AVERAGE_ANCHORS)

    def test_short_unit_with_healthy_inactives_fails_the_build(self):
        chart = json.loads(week_inputs.DEPTH_CHART.read_text())
        inactives = set(chart["game_day_inactives"]["players"])
        rows = list(week_inputs.controlled_active())
        # Hold one dressed, available player without adding him to Stone's list.
        index = next(i for i, (player, note) in enumerate(rows)
                     if player not in inactives and note == week_inputs.AVAILABLE_TEXT)
        held = rows[index][0]
        rows[index] = (held, "Out, medical hold")
        with mock.patch.object(week_inputs, "controlled_active", return_value=rows), \
                mock.patch.object(week_inputs, "injured_out", return_value={}):
            with self.assertRaisesRegex(ValueError, "not 46.*%s" % held):
                week_inputs.jacksonville_input([], date(2013, 12, 15), AVERAGE_ANCHORS, self.sheet)

    def test_unlabelled_call_fails_the_build(self):
        with self.assertRaisesRegex(ValueError, "Mystery"):
            week_inputs.jacksonville_input([], date(2013, 10, 13), AVERAGE_ANCHORS,
                                           [{"name": "Mystery", "family": "Mystery", "type": "pass"}])

    def test_week_two_package_passes_the_weekly_gate(self):
        controlled = controlled_players_from_roster(ROOT / "career/2013/roster.md")
        self.assertEqual(check_inputs(self.package, controlled, "Jacksonville Jaguars", expected_games=16), [])

    def test_jacksonville_dresses_its_game_day_unit(self):
        game = next(g for g in self.package["games"] if g["away"] == "Jacksonville Jaguars")
        jax = game["away_input"]
        chart = json.loads((ROOT / "career/2013/depth_chart.json").read_text())
        inactives = set(chart["game_day_inactives"]["players"])
        available = {p["player_id"] for p in jax["roster"] if p["available"]}
        self.assertEqual(set(jax["active_players"]), available - inactives)
        self.assertLessEqual(len(jax["active_players"]), 46)
        unavailable = {p["player_id"] for p in jax["roster"] if not p["available"]}
        self.assertFalse(unavailable & set(jax["active_players"]))

    def test_background_clubs_dress_at_most_forty_six(self):
        for game in self.package["games"]:
            for side in ("away", "home"):
                if game[side] != "Jacksonville Jaguars":
                    self.assertLessEqual(len(game[side + "_input"]["active_players"]), 46)

    def test_deepest_player_is_made_inactive_first(self):
        roster = [{"player_id": "QB%d" % i, "position": "QB", "depth": i, "available": True} for i in (1, 2, 3)]
        roster += [{"player_id": "OL%d" % i, "position": "OL", "depth": i, "available": True} for i in range(1, 11)]
        roster += [{"player_id": "%s%d" % (pos, i), "position": pos, "depth": i, "available": True}
                   for pos, n in (("RB", 4), ("WR", 7), ("TE", 4), ("DL", 10), ("LB", 7), ("DB", 10))
                   for i in range(1, n + 1)]
        roster += [{"player_id": pos, "position": pos, "depth": 1, "available": True} for pos in ("K", "P", "LS")]
        active = week_inputs.game_day_actives(roster)
        self.assertEqual(len(active), 46)
        self.assertNotIn("OL10", active)
        self.assertNotIn("DB10", active)
        self.assertIn("QB3", active)

    def test_branch_injuries_carry_into_the_next_week(self):
        game = next(g for g in self.package["games"] if "Carolina Panthers" in (g["away"], g["home"]))
        side = game["away_input"] if game["away"] == "Carolina Panthers" else game["home_input"]
        newton = next(p for p in side["roster"] if p["player_id"] == "Cam Newton")
        self.assertFalse(newton["available"])

    def test_unplaced_jacksonville_player_fails_closed(self):
        with mock.patch.object(week_inputs, "controlled_active",
                               return_value=[("Unplaced Player", week_inputs.AVAILABLE_TEXT)]):
            with self.assertRaises(ValueError):
                week_inputs.jacksonville_input([], date(2013, 9, 15), AVERAGE_ANCHORS, [])


if __name__ == "__main__":
    unittest.main()


class AvailabilityNoteTests(unittest.TestCase):
    """Entry 57: the Week 14 generation-1 void."""

    def test_explained_clear_note_is_available(self):
        from datetime import date
        from runtime.week_inputs import roster_available
        day = date(2013, 12, 5)
        self.assertTrue(roster_available("No communicated restriction (Week 11 injury cleared November 26)", day))
        self.assertFalse(roster_available("Out, head/neck, independent medical hold (Week 13); projected return April 5, 2014", day))
        self.assertFalse(roster_available("Out, medical hold", day))

    def test_unrecognized_note_fails_the_build(self):
        from datetime import date
        from runtime.week_inputs import roster_available
        with self.assertRaises(ValueError):
            roster_available("Questionable", date(2013, 12, 5))

    def test_generation_suffix(self):
        from runtime.week_inputs import event_id
        game = {"week": 14, "away": "Houston Texans", "home": "Jacksonville Jaguars"}
        self.assertEqual(event_id(game, 1), "2013-week14-houston-texans-at-jacksonville-jaguars")
        self.assertEqual(event_id(game, 2), "2013-week14-houston-texans-at-jacksonville-jaguars-g2")
        self.assertEqual(event_id(game), event_id(game, 2))
