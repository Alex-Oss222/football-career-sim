import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from validate_repository import receipt_coverage_errors, validate
from check_game_readiness import assess, check
from runtime.seasons import current_record
from runtime.events import EVENT_META, closures, load_events


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

    def test_closed_current_records_pass(self):
        self.assertEqual(validate(self.root), [])

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

    def test_latest_closure_cannot_be_removed_from_its_owner(self):
        latest = closures(load_events(self.root))[-1][1]
        file = self.root/latest.owner
        def remove_closure(match):
            data = json.loads(match[1])
            if data['id'] == latest.id:
                data.pop('closure')
            return '<!-- event-record: ' + json.dumps(data) + ' -->'
        file.write_text(EVENT_META.sub(remove_closure, file.read_text()))
        self.assertTrue(any('checkpoint differs' in error for error in validate(self.root)))

    def test_completed_phase_cannot_point_to_an_unrelated_event(self):
        mapping = json.loads((self.root/'docs/repository_map.json').read_text())
        phase = mapping['phases']['2014_otas']
        file = self.root/phase['output']
        from validate_repository import META
        def change_ref(match):
            data = json.loads(match[1])
            data['event_ref'] = 'unrelated-event'
            data.pop('event_entry', None)
            return '<!-- sim-meta: ' + json.dumps(data) + ' -->'
        file.write_text(META.sub(change_ref, file.read_text()))
        self.assertTrue(any('unknown event owner' in error for error in validate(self.root)))

    def test_annual_record_cannot_replace_its_owner(self):
        record = current_record('record', self.root)
        record.write_text(record.read_text()+'\n- Synthetic event without an owner.\n')
        self.assertTrue(any('record is missing or stale' in error for error in validate(self.root)))

    def test_foundation_change_requires_new_source_version(self):
        file = self.root/'foundation/03_Head_Coach_Organization_and_Authority_Canon.md'
        file.write_text(file.read_text()+'\nSynthetic amendment.\n')
        self.assertTrue(any('stale source-version hash' in error for error in validate(self.root)))

    def test_membership_mismatch_is_rejected_even_when_count_matches(self):
        self.change(current_record('roster', self.root).relative_to(self.root),
                    '| Kirk Cousins |', '| Synthetic replacement |')
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

    def test_status_flags_cannot_enable_noncanonical_private_runtime(self):
        manifest = self.root/'runtime/readiness.json'
        data = json.loads(manifest.read_text())
        for item in data['requirements']:
            item['status'] = 'VERIFIED'
        manifest.write_text(json.dumps(data))
        self.assertTrue(any('Private runtime probe' in blocker for blocker in check(self.root)))

    def test_structured_readiness_assessment_is_fail_closed(self):
        # Legacy evidence remains testable separately from the 2014 release.
        result = assess(self.root, season=2013)
        self.assertFalse(result['ready'])
        ids = {blocker['id'] for blocker in result['blockers']}
        self.assertEqual(ids, {'private_probe'})
        self.assertNotIn('seed', json.dumps(result).lower())

    def test_missing_remaining_work_statement_is_invalid(self):
        manifest = self.root/'runtime/readiness.json'
        data = json.loads(manifest.read_text())
        data['requirements'][0]['remaining'] = ''
        manifest.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            assess(self.root)


    def test_stale_stat_cache_is_rejected(self):
        cache = self.root/'career/2013/stats/season_totals.json'
        data = json.loads(cache.read_text())
        data['receipt_count'] = 999
        cache.write_text(json.dumps(data, sort_keys=True, separators=(',', ':'))+'\n')
        self.assertTrue(any('season_totals.json is stale' in error for error in validate(self.root)))

    def test_stale_generated_stat_view_is_rejected(self):
        view = self.root/'career/2013/stats/league_leaders.md'
        view.write_text(view.read_text()+'\nSynthetic stale line.\n')
        self.assertTrue(any('stale generated stat view' in error for error in validate(self.root)))

    def test_receipt_score_mismatch_is_rejected(self):
        receipt = self.root/'career/2013/stats/game_receipts/synthetic-score-check.json'
        data = {
            'schema_version': 3, 'event_id': 'synthetic-score-check', 'week': 1,
            'matchup': 'B at A', 'home': 'A', 'away': 'B',
            'coverage': 'complete', 'detail': 'compact_stats',
            'final_score': {'A': 8, 'B': 0},
            'team_stats': {'A': {'points': 7, 'players': {}}, 'B': {'points': 0, 'players': {}}},
        }
        receipt.write_text(json.dumps(data, sort_keys=True, separators=(',', ':'))+'\n')
        self.assertTrue(any('receipt points differ from final score' in error for error in validate(self.root)))

    def test_missing_week_receipt_is_rejected(self):
        receipts = sorted((self.root/'career/2013/stats/game_receipts').glob('week_05_*.json'))
        self.assertTrue(receipts)
        receipts[-1].unlink()
        self.assertTrue(any('Week 5:' in error and 'scheduled games' in error
                            for error in validate(self.root)))


class ReceiptCoverageTests(unittest.TestCase):
    @staticmethod
    def receipts(week, count):
        return [{'event_id': f'w{week}-{n}', 'week': week} for n in range(count)]

    @staticmethod
    def schedule(week):
        if week not in (1, 2):
            raise ValueError('no 2013 schedule for week %s' % week)
        return [{}] * (3 if week == 1 else 2)

    def test_full_weeks_pass_and_unreceipted_weeks_are_not_required(self):
        receipts = self.receipts(1, 3) + self.receipts(2, 2)
        self.assertEqual(receipt_coverage_errors(receipts, self.schedule), [])
        self.assertEqual(receipt_coverage_errors(self.receipts(1, 3), self.schedule), [])

    def test_short_or_extra_week_is_rejected(self):
        short = receipt_coverage_errors(self.receipts(1, 2), self.schedule)
        self.assertEqual(len(short), 1)
        self.assertIn('Week 1: 2 game receipt(s) for 3 scheduled games', short[0])
        extra = receipt_coverage_errors(self.receipts(2, 3), self.schedule)
        self.assertIn('Week 2: 3 game receipt(s) for 2 scheduled games', extra[0])

    def test_week_outside_the_regular_season_schedule_is_skipped(self):
        self.assertEqual(receipt_coverage_errors(self.receipts(19, 1), self.schedule), [])

    def test_repository_schedule_is_the_default(self):
        # Week 5 of 2013 has fourteen scheduled games (four byes).
        self.assertEqual(receipt_coverage_errors(self.receipts(5, 14)), [])
        self.assertTrue(receipt_coverage_errors(self.receipts(5, 13)))


if __name__ == '__main__':
    unittest.main()
