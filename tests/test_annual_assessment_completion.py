"""Authored final assessments must be complete, sourced and explicitly reviewed."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from runtime.seasons import SeasonPaths
from scripts.build_annual_player_sheets import (
    GENERAL_TRAITS, assessment_card_errors, final_assessment_errors,
    load_season_players, review_final_assessments, target_path,
)
from scripts.update_player_cards import profile_errors, stats_block


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def empty_period():
    return {'players': {}, 'fields': {}, 'games': 0, 'through': 0, 'complete': True}


def authored_card(root, year, name, path, *, final=False):
    """Fixture prose represents authored judgments, never production generation."""
    paths = SeasonPaths(year, root)
    opening = paths.record('player_profiles') / path.name
    exit_review = paths.record('closeouts/exit_interviews.md')
    traits = [*GENERAL_TRAITS, 'Snap accuracy', 'Snap velocity', 'Protection transition']
    text = f'''# {name} — {year} NFL Player Sheet

**Team:** Jacksonville Jaguars
**Season:** {year}
**Position:** LS
**Age:** Unverified
**Profile status:** {'Final annual assessment' if final else 'Working player card'}
**Assessment stage:** {'Final' if final else 'Opening'} annual assessment
**Evaluation policy:** Authored personnel judgment; evidence limits remain explicit.
**Checkpoint:** {'Completed season and exit review' if final else 'Entry assessment'}
**NFL standing:** Reserve specialist
**Player identity:** Controlled short snap; protection work needs further evidence.
**Previous annual profile:** None; first recorded Jacksonville assessment.

## Player grades

| Category | Grade | NFL standing |
| --- | --- | --- |
'''
    text += ''.join(f'| {trait} | 5.0 /10 | Staff judgment |\n' for trait in traits)
    text += '\n## League comparison\n\n| Trait | vs. Average | vs. Best | vs. Worst |\n| --- | --- | --- | --- |\n'
    text += ''.join(f'| {trait} | Comparable | Less consistent | More reliable |\n' for trait in traits[1:])
    for heading in ('Established player state', 'What supports this assessment',
                    'Historical comparison', 'Play style', 'Best traits', 'Main weaknesses'):
        text += f'\n## {heading}\n\nRetained assessment from the cited work; no unrecorded improvement is asserted.\n'
    text += '''
## Year-over-year change

| Area | Prior profile | Current checkpoint | Change | Evidence / football reason |
| --- | --- | --- | --- | --- |
| Identity | No earlier card | Recorded work | First assessment | Cited review |

## Evidence and uncertainty

Limited observed protection work; personnel judgment is distinct from measurement.
'''
    text += f'\n[Exit review]({os.path.relpath(exit_review, path.parent)})\n'
    if final:
        text += f'\n[Opening assessment and dated updates]({os.path.relpath(opening, path.parent)})\n'
        text += '\n## Change from the opening assessment\n\nRetained the opening view. The exit review records no observed change in protection reliability.\n'
    text += '\n**One-line description:** Reserve snapper with an evidence gap in protection.\n\n'
    periods = {False: empty_period(), True: empty_period()}
    # Preserve a genuinely separate prior-year row while adding the current one.
    old = stats_block(year-1, name, 'LS', periods, root=root)
    return text + stats_block(year, name, 'LS', periods, old, root) + '\n'


class AnnualAssessmentCompletionTests(unittest.TestCase):
    def fixture(self, year=2015, *, departed=True):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        paths = SeasonPaths(year, root)
        paths.roster.parent.mkdir(parents=True, exist_ok=True)
        paths.roster.write_text('''**As of:** Season close
**Canonical controlled-player count:** **1**

## Current controlled players

| Player | Pos | Status |
| --- | --- | --- |
| Sam Snap | LS | Under contract |
''')
        gates = {}
        for gate, filename in [('team_season_closed', 'season_closeout.md'),
                               ('exit_interviews', 'exit_interviews.md')]:
            source = paths.record('closeouts/'+filename)
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text('Authored completed-season review with the available evidence.\n')
            gates[gate] = {'status': 'COMPLETE', 'evidence': [
                {'path': source.relative_to(root).as_posix(), 'sha256': sha(source)}]}
        manifest = paths.record('closeouts/season_handoff.json')
        manifest.write_text(json.dumps({'season': year, 'gates': gates, 'pending_decisions': ['preserve me']}))
        names = ['Sam Snap'] + (['Dale Former'] if departed else [])
        for name in names:
            final = target_path(year, name, root)
            opening = paths.record('player_profiles')/final.name
            opening.parent.mkdir(parents=True, exist_ok=True)
            opening.write_text(authored_card(root, year, name, opening))
            final.parent.mkdir(parents=True, exist_ok=True)
            final.write_text(authored_card(root, year, name, final, final=True))
        return root, paths, manifest

    def test_authored_completion_works_in_2014_and_later_without_rewriting_cards(self):
        for year in (2014, 2015):
            with self.subTest(year=year):
                root, paths, manifest = self.fixture(year)
                before = {p: p.read_bytes() for folder in ('player_profiles', 'closeouts/player_assessments')
                          for p in paths.record(folder).glob('*.md')}
                self.assertEqual(final_assessment_errors(year, root, require_complete=True), [])
                self.assertTrue(any('review is missing' in e for e in final_assessment_errors(year, root, require_reviewed=True)))
                self.assertEqual(review_final_assessments(year, root), 2)
                self.assertEqual(final_assessment_errors(year, root, require_complete=True, require_reviewed=True), [])
                self.assertEqual(before, {p: p.read_bytes() for p in before})
                data = json.loads(manifest.read_text())
                self.assertEqual(data['pending_decisions'], ['preserve me'])
                _, players = load_season_players(year, root)
                self.assertEqual({p.player for p in players}, {'Sam Snap', 'Dale Former'})

    def test_missing_departed_player_final_is_not_hidden_by_current_roster(self):
        root, _, _ = self.fixture()
        target_path(2015, 'Dale Former', root).unlink()
        errors = final_assessment_errors(2015, root, require_complete=True)
        self.assertTrue(any('dale_former' in e and 'missing final' in e for e in errors))
        with self.assertRaises(ValueError):
            review_final_assessments(2015, root)

    def test_zero_cards_and_missing_roster_member_fail_readiness(self):
        root, paths, _ = self.fixture()
        for path in paths.record('player_profiles').glob('*.md'):
            path.unlink()
        self.assertEqual(profile_errors(2015, root, require_complete=False), [])
        self.assertTrue(any('no opening annual assessments' in e for e in profile_errors(2015, root)))
        self.assertTrue(final_assessment_errors(2015, root, require_complete=True))

    def test_future_empty_finals_are_optional_until_readiness_check(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.assertEqual(final_assessment_errors(2022, root), [])
            self.assertTrue(final_assessment_errors(2022, root, require_complete=True))
            self.assertEqual(profile_errors(2022, root, require_complete=False), [])
            self.assertTrue(profile_errors(2022, root))
            self.assertEqual(profile_errors(2013, root), [])

    def test_header_only_card_cannot_claim_completion(self):
        root, paths, _ = self.fixture()
        final = target_path(2015, 'Sam Snap', root)
        final.write_text('**Assessment stage:** Final annual assessment\n')
        errors = final_assessment_errors(2015, root, require_complete=True)
        self.assertTrue(any('authored grade' in e or 'grade traits' in e for e in errors))
        opening = paths.record('player_profiles/sam_snap.md')
        opening.write_text('# Sam Snap — 2015 Player Profile\n')
        self.assertTrue(profile_errors(2015, root, require_complete=False))

    def test_review_invalidates_on_final_or_source_change(self):
        for which in ('final', 'opening', 'exit'):
            with self.subTest(which=which):
                root, paths, _ = self.fixture()
                review_final_assessments(2015, root)
                path = (target_path(2015, 'Sam Snap', root) if which == 'final' else
                        paths.record('player_profiles/sam_snap.md') if which == 'opening' else
                        paths.record('closeouts/exit_interviews.md'))
                text = path.read_text()
                path.write_text(text.replace('5.0 /10', '5.5 /10', 1) if which != 'exit' else text+'New review evidence.\n')
                self.assertTrue(final_assessment_errors(2015, root, require_reviewed=True))

    def test_default_validation_preserves_reviewed_final_history(self):
        root, _, _ = self.fixture()
        review_final_assessments(2015, root)
        final = target_path(2015, 'Sam Snap', root)
        final.write_text(final.read_text().replace('5.0 /10', '5.5 /10', 1))
        self.assertTrue(any('stale' in error for error in final_assessment_errors(2015, root)))
        # An explicit new review may accept changed authored content.
        self.assertEqual(review_final_assessments(2015, root), 2)
        for path in final.parent.glob('*.md'):
            path.unlink()
        self.assertTrue(any('missing final' in error for error in final_assessment_errors(2015, root)))

    def test_final_requires_same_year_opening_and_reviewed_exit_evidence(self):
        root, _, _ = self.fixture()
        final = target_path(2015, 'Sam Snap', root)
        text = final.read_text()
        import re
        final.write_text(re.sub(r'^\[(?:Opening assessment and dated updates|Exit review)\].*\n', '', text, flags=re.M))
        errors = final_assessment_errors(2015, root, require_complete=True)
        self.assertTrue(any('same-year opening' in e for e in errors))
        self.assertTrue(any('exit-interview evidence' in e for e in errors))

    def test_changed_current_or_prior_statistics_are_rejected(self):
        for old_year in (2014, 2015):
            with self.subTest(old_year=old_year):
                root, _, _ = self.fixture()
                final = target_path(2015, 'Sam Snap', root)
                text = final.read_text()
                final.write_text(text.replace(f'| {old_year} | Jacksonville |', f'| {old_year} | Invented team |', 1))
                self.assertTrue(any('statistics' in e for e in final_assessment_errors(2015, root, require_complete=True)))

    def test_closeout_filename_does_not_replace_reviewed_gate(self):
        root, _, manifest = self.fixture()
        data = json.loads(manifest.read_text())
        data['gates']['exit_interviews']['status'] = 'OPEN'
        manifest.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'reviewed exit_interviews'):
            review_final_assessments(2015, root)

    def test_adopted_season_review_owner_needs_no_duplicate_closeout_file(self):
        root, paths, manifest = self.fixture()
        old = paths.record('closeouts/season_closeout.md')
        report = paths.record('closeouts/season_review.md')
        old.rename(report)
        data = json.loads(manifest.read_text())
        data['gates']['team_season_closed']['evidence'] = [
            {'path': report.relative_to(root).as_posix(), 'sha256': sha(report)}]
        manifest.write_text(json.dumps(data))
        self.assertEqual(review_final_assessments(2015, root), 2)
        self.assertFalse(old.exists())
        self.assertEqual(final_assessment_errors(2015, root, require_reviewed=True), [])

    def test_recorded_participant_without_retained_card_is_rejected(self):
        root, _, _ = self.fixture()
        period = {**empty_period(), 'players': {'Absent Former Player': {}}}
        with patch('scripts.update_player_cards.period_data', return_value=period):
            with self.assertRaisesRegex(ValueError, 'recorded participants lack retained opening cards'):
                load_season_players(2015, root)

    def test_grade_placeholder_and_wrong_season_fail_semantic_validation(self):
        root, paths, _ = self.fixture()
        opening = paths.record('player_profiles/sam_snap.md')
        text = opening.read_text().replace('5.0 /10', '— /10', 1).replace('**Season:** 2015', '**Season:** 2016')
        opening.write_text(text)
        errors = assessment_card_errors(opening, 2015, 'Sam Snap', 'LS', root=root)
        self.assertTrue(any('wrong season' in e for e in errors))
        self.assertTrue(any('invalid authored grade' in e for e in errors))

    def test_exact_decimal_grades_are_accepted_only_within_one_to_ten(self):
        root, paths, _ = self.fixture()
        opening = paths.record('player_profiles/sam_snap.md')
        text = opening.read_text()
        for grade, valid in [('6.7', True), ('1.01', True), ('9.999', True),
                             ('10.00', True), ('0.9', False), ('10.1', False),
                             ('-1', False), ('NaN', False)]:
            with self.subTest(grade=grade):
                opening.write_text(text.replace('5.0 /10', grade+' /10', 1))
                errors = assessment_card_errors(opening, 2015, 'Sam Snap', 'LS', root=root)
                self.assertEqual(not errors, valid, errors)


if __name__ == '__main__':
    unittest.main()
