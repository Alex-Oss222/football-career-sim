import unittest

from scripts.build_annual_player_sheets import (
    POSITION_SHEET_TRAITS,
    ROOT,
    load_season_players,
    render_player_sheet,
    slugify,
    target_path,
)

class AnnualPlayerSheetTests(unittest.TestCase):
    def test_slugify_handles_initials_and_apostrophes(self):
        self.assertEqual(slugify("C.J. Anderson"),"c_j_anderson")
        self.assertEqual(slugify("Sen'Derrick Marks"),"sen_derrick_marks")

    def test_2013_completed_season_has_one_final_sheet_each(self):
        _,players=load_season_players(2013)
        self.assertEqual(len(players),61)
        missing=[str(target_path(2013,p.player).relative_to(ROOT)) for p in players if not target_path(2013,p.player).exists()]
        self.assertEqual(missing,[])

    def test_2014_sheet_is_blocked_before_2014_season_close(self):
        with self.assertRaisesRegex(ValueError,"final-season records"):
            load_season_players(2014)

    def test_qb_sheet_is_position_specific(self):
        checkpoint,players=load_season_players(2013)
        cousins=next(p for p in players if p.player=="Kirk Cousins")
        sheet=render_player_sheet(cousins,2013,checkpoint)
        for trait in POSITION_SHEET_TRAITS["QB"]:
            self.assertIn(f"| {trait} |",sheet)
        self.assertNotIn("## Year-over-year change",sheet)
        self.assertNotIn("Previous annual profile",sheet)

    def test_generator_does_not_invent_grade(self):
        checkpoint,players=load_season_players(2013)
        sheet=render_player_sheet(players[0],2013,checkpoint)
        self.assertIn("| Overall at position | — /10 | Unassessed | Unassessed |",sheet)

if __name__=="__main__":
    unittest.main()
