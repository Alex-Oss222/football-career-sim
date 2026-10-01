import unittest
import json
import shutil
import tempfile
from pathlib import Path

from scripts.build_annual_player_sheets import (
    POSITION_SHEET_TRAITS,
    ROOT,
    EXIT_INDEX,
    BIRTH_DATES,
    load_season_players,
    render_player_sheet,
    slugify,
    target_path,
    check_profiles,
    repository_profile_errors,
    final_assessment_errors,
)
from runtime.seasons import SeasonPaths

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

    def test_final_review_has_a_separate_destination_and_requires_season_close(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            opening = SeasonPaths(2014, root).record('player_profiles/kirk_cousins.md')
            final = target_path(2014, 'Kirk Cousins', root)
            self.assertNotEqual(final, opening)
            final.parent.mkdir(parents=True)
            final.write_text('**Assessment stage:** Final annual assessment\n')
            self.assertEqual(final_assessment_errors(2014, root),
                             ['2014 final player assessments exist before season close'])
            closeout = SeasonPaths(2014, root).record('closeouts/season_closeout.md')
            closeout.parent.mkdir(parents=True, exist_ok=True)
            closeout.write_text('Season closed\n')
            self.assertEqual(final_assessment_errors(2014, root), [])

    def test_qb_sheet_is_position_specific(self):
        checkpoint,players=load_season_players(2013)
        cousins=next(p for p in players if p.player=="Kirk Cousins")
        sheet=render_player_sheet(cousins,2013,checkpoint)
        for trait in POSITION_SHEET_TRAITS["QB"]:
            self.assertIn(f"| {trait} |",sheet)
        self.assertNotIn("## Year-over-year change",sheet)
        self.assertNotIn("Previous annual profile",sheet)

    def test_every_2013_position_can_render(self):
        checkpoint,players=load_season_players(2013)
        for player in players:
            sheet=render_player_sheet(player,2013,checkpoint)
            self.assertIn(f"**Position:** {player.pos}",sheet)

    def test_generator_does_not_invent_grade(self):
        checkpoint,players=load_season_players(2013)
        sheet=render_player_sheet(players[0],2013,checkpoint)
        self.assertIn("| Overall at position | — /10 | Unassessed | Unassessed |",sheet)

    def fixture(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root=Path(temp.name)
        for source in (EXIT_INDEX, BIRTH_DATES):
            destination=root/source.relative_to(ROOT)
            destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,destination)
        checkpoint,players=load_season_players(2013,root)
        for player in players:
            path=target_path(2013,player.player,root)
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(render_player_sheet(player,2013,checkpoint),encoding='utf-8')
            evidence=root/player.evidence
            evidence.parent.mkdir(parents=True,exist_ok=True)
            evidence.touch()
        return root,players

    def test_all_checked_in_sheets_pass_full_validation(self):
        self.assertEqual(repository_profile_errors(),[])

    def test_missing_or_wrong_position_trait_is_rejected(self):
        root,players=self.fixture()
        path=target_path(2013,'Lane Johnson',root)
        text=path.read_text(encoding='utf-8')
        path.write_text(text.replace('| Anchor vs power |','| Hands |'),encoding='utf-8')
        errors=check_profiles(2013,players,root)
        self.assertTrue(any('grade traits differ from OT' in error for error in errors))
        self.assertTrue(any('position benchmarks' in error for error in errors))

    def test_invalid_grade_and_duplicate_benchmark_are_rejected(self):
        root,players=self.fixture()
        path=target_path(2013,'Lane Johnson',root)
        text=path.read_text(encoding='utf-8').replace('— /10','10.5 /10',1)
        row='| Anchor vs power | Unassessed | Unassessed | Unassessed | Unassessed | Pending historical benchmark |'
        path.write_text(text.replace(row,row+'\n'+row),encoding='utf-8')
        errors=check_profiles(2013,players,root)
        self.assertTrue(any('invalid position grade' in error for error in errors))
        self.assertTrue(any('position benchmarks' in error for error in errors))

    def test_unclosed_season_and_extra_player_are_rejected(self):
        root,players=self.fixture()
        path=target_path(2014,'Kirk Cousins',root)
        path.parent.mkdir(parents=True)
        path.write_text('# Premature final sheet',encoding='utf-8')
        target_path(2013,'Unexpected Player',root).write_text('# Extra',encoding='utf-8')
        errors=repository_profile_errors(root)
        self.assertTrue(any('2014 final player assessments exist before season close' in error for error in errors))
        self.assertTrue(any('unexpected annual profile' in error for error in errors))

    def test_frozen_syntheses_do_not_read_living_offseason_profiles(self):
        root,players=self.fixture()
        living=SeasonPaths(2014,root).record('offseason/player_development/roster_profiles.md')
        living.write_text('| **Kirk Cousins (QB)** | Later-season observation |',encoding='utf-8')
        checkpoint,reloaded=load_season_players(2013,root)
        self.assertEqual(players,reloaded)
        self.assertIn('January 14, 2014',checkpoint)

    def test_duplicate_exit_index_paths_are_rejected(self):
        root,_=self.fixture()
        path=root/EXIT_INDEX.relative_to(ROOT)
        data=json.loads(path.read_text(encoding='utf-8'))
        data['players'][1]=data['players'][0]
        path.write_text(json.dumps(data),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'duplicate player paths'):
            load_season_players(2013,root)

if __name__=="__main__":
    unittest.main()
