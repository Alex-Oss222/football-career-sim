import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from validate_repository import validate
from check_game_readiness import assess, check


class ContinuityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='continuity-test-', dir=ROOT.parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        mapping = json.loads((ROOT/'docs/repository_map.json').read_text())
        allowed_books = set(mapping['active_playbooks']) | {'career/playbook/README.md'}
        # Do not read archived or future playbook contents, even for fixtures.
        for source in ROOT.rglob('*'):
            path = source.relative_to(ROOT)
            if not source.is_file() or any(p in {'.git', '__pycache__'} for p in path.parts):
                continue
            destination = self.root/path
            destination.parent.mkdir(parents=True, exist_ok=True)
            if path.parts[0] == 'archive' or (path.as_posix().startswith('career/playbook/') and path.as_posix() not in allowed_books):
                destination.touch()
            else:
                shutil.copyfile(source, destination)

    def change(self, path, old, new):
        file = self.root/path
        text = file.read_text()
        self.assertIn(old, text)
        file.write_text(text.replace(old, new, 1))

    def test_closed_current_records_and_future_phase_stubs_pass(self):
        self.assertEqual(validate(self.root), [])
        # An unchanged May 5 cap worksheet is valid at the May 23 clock.
        self.assertIn('May 5', (self.root/'career/2013/offseason/current_cap_worksheet.md').read_text())

    def test_changed_output_requires_summary_review(self):
        output = self.root/'career/2013/offseason/otas/output.md'
        output.write_text(output.read_text()+'\nSynthetic changed observation.\n')
        self.assertTrue(any('output changed' in error for error in validate(self.root)))

    def test_original_unstarted_summary_is_rejected(self):
        (self.root/'career/2013/offseason/otas/standouts.md').write_text('# OTA standouts\n\nNOT STARTED\n')
        self.assertTrue(any('otas: invalid/missing phase evidence' in error for error in validate(self.root)))

    def test_missing_phase_record_is_rejected(self):
        (self.root/'career/2013/offseason/training_camp/roster_decisions.md').unlink()
        self.assertTrue(any('Missing required file' in error for error in validate(self.root)))

    def test_checkpoint_divergence_is_rejected(self):
        self.change('state/05_Current_Season_State.md', '**Global package checkpoint:** `Canonical',
                    '**Global package checkpoint:** `Unclosed Canonical')
        self.assertTrue(any('checkpoint differs' in error for error in validate(self.root)))

    def test_foundation_change_requires_new_source_version(self):
        file = self.root/'foundation/03_Head_Coach_Organization_and_Authority_Canon.md'
        file.write_text(file.read_text()+'\nSynthetic amendment.\n')
        self.assertTrue(any('stale source-version hash' in error for error in validate(self.root)))

    def test_membership_mismatch_is_rejected_even_when_count_matches(self):
        self.change('career/2013/roster.md', '| Kirk Cousins |', '| Synthetic replacement |')
        self.assertTrue(any('membership differs' in error for error in validate(self.root)))

    def test_broken_markdown_anchor_is_rejected(self):
        file = self.root/'README.md'
        file.write_text(file.read_text()+'\n[Bad anchor](career/2013/README.md#nonexistent-heading)\n')
        self.assertTrue(any('missing heading' in error for error in validate(self.root)))

    def test_unknown_readiness_gate_cannot_replace_required_gate(self):
        manifest = self.root/'runtime/readiness.json'
        data = json.loads(manifest.read_text())
        data['requirements'][0]['id'] = 'pretend'
        manifest.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            check(self.root)

    def test_status_flags_cannot_enable_missing_execution_runtime(self):
        manifest = self.root/'runtime/readiness.json'
        data = json.loads(manifest.read_text())
        for item in data['requirements']:
            item['status'] = 'VERIFIED'
        manifest.write_text(json.dumps(data))
        self.assertTrue(any('Execution integration' in blocker for blocker in check(self.root)))

    def test_structured_readiness_assessment_is_fail_closed(self):
        result = assess(self.root)
        self.assertFalse(result['ready'])
        ids = {blocker['id'] for blocker in result['blockers']}
        self.assertEqual(
            ids,
            {'calibration', 'playing_rules', 'injury_model', 'football_kernel',
             'private_runtime', 'execution_integration'},
        )
        self.assertNotIn('seed', json.dumps(result).lower())

    def test_missing_remaining_work_statement_is_invalid(self):
        manifest = self.root/'runtime/readiness.json'
        data = json.loads(manifest.read_text())
        data['requirements'][0]['remaining'] = ''
        manifest.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            assess(self.root)


if __name__ == '__main__':
    unittest.main()
