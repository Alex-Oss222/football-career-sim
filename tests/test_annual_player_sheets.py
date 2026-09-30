import unittest

from scripts.build_annual_player_sheets import (
    ROOT, load_season_players, render_player_sheet, slugify, target_path,
)

class AnnualPlayerSheetTests(unittest.TestCase):
    def test_slugify_handles_initials_and_apostrophes(self):
        self.assertEqual(slugify("C.J. Anderson"), "c_j_anderson")
        self.assertEqual(slugify("Sen'Derrick Marks"), "sen_derrick_marks")
        self.assertEqual(slugify("Daniel Te'o-Nesheim"), "daniel_te_o_nesheim")

    def test_2013_exit_universe_has_one_profile_each(self):
        _, players = load_season_players(2013)
        self.assertEqual(len(players), 61)
        missing=[str(target_path(2013,p.player).relative_to(ROOT)) for p in players if not target_path(2013,p.player).exists()]
        self.assertEqual(missing, [])

    def test_current_2014_roster_has_one_profile_each(self):
        _, players = load_season_players(2014)
        roster=(ROOT/"career/2014/roster.md").read_text(encoding="utf-8")
        self.assertIn(f"**Canonical controlled-player count:** **{len(players)}**", roster)
        missing=[str(target_path(2014,p.player).relative_to(ROOT)) for p in players if not target_path(2014,p.player).exists()]
        self.assertEqual(missing, [])

    def test_cousins_2014_sheet_inherits_2013_profile(self):
        checkpoint, players = load_season_players(2014)
        cousins=next(p for p in players if p.player=="Kirk Cousins")
        sheet=render_player_sheet(cousins,2014,checkpoint)
        self.assertIn("[2013 Jacksonville profile](../../2013/player_profiles/kirk_cousins.md)",sheet)
        self.assertIn("Carries forward the supported 2013 player",sheet)
        self.assertIn("## Established player state",sheet)
        self.assertIn("## Year-over-year change",sheet)

    def test_numeric_grades_are_not_fabricated_by_generator(self):
        checkpoint, players=load_season_players(2014)
        sheet=render_player_sheet(players[0],2014,checkpoint)
        self.assertIn("| Overall | — /10 | Unassessed |",sheet)
        self.assertNotIn("| Overall | 5",sheet)

if __name__=="__main__":
    unittest.main()
