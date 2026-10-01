import json
from pathlib import Path
import tempfile
import unittest

from runtime.events import closures, event_refs, load_events, preserve_event_comments, render_record, resolve_path


class EventRecordTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.mapping = {'event_record_sources': ['career/**/*.md', 'runtime/**/*.md'],
                        'legacy_event_aliases': {}}

    def write_event(self, owner='career/2014/trades/trade.md', **changes):
        event = {'id': '2014-04-07-allen-trade', 'date': '2014-04-07',
                 'summary': 'Russell Allen was traded to Arizona.', 'status': 'closed'}
        event.update(changes)
        path = self.root / owner
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('a') as file:
            file.write('<!-- event-record: ' + json.dumps(event) + ' -->\n')
        return event

    def test_record_uses_actual_dates_and_excludes_technical_closures(self):
        self.write_event()
        self.write_event('career/2014/free_agency/signing.md', id='2014-04-04-henne-signing',
                         date='2014-04-04', summary='Chad Henne re-signed.')
        self.write_event('runtime/README.md', id='2014-04-17-release', date='2014-04-17', kind='technical',
                         closure={'checkpoint': 'Release accepted', 'through': '2014-04-17', 'sequence': 106})
        events = load_events(self.root, self.mapping)
        text = render_record(2014, events, self.root)
        self.assertLess(text.index('April 4, 2014'), text.index('April 7, 2014'))
        self.assertNotIn('April 17', text)
        self.assertIn('[Full record](trades/trade.md)', text)
        self.assertEqual(len([line for line in text.splitlines() if line.startswith('- ')]), 2)

    def test_mixed_legacy_batch_resolves_to_multiple_owners(self):
        one = self.write_event()
        two = self.write_event('career/2014/free_agency/signing.md', id='2014-04-04-henne-signing')
        self.mapping['legacy_event_aliases']['106'] = [one['id'], two['id']]
        self.assertEqual(len(load_events(self.root, self.mapping)), 2)
        self.assertEqual(event_refs({'event_entry': 106}, self.mapping), [one['id'], two['id']])
        self.assertEqual(event_refs({'event_ref': one['id']}, self.mapping), [one['id']])

    def test_imprecise_date_is_not_rendered_as_an_exact_day(self):
        self.write_event(date='2014-04-01', date_end='2014-04-30',
                         date_label='April 2014 (exact date unrecorded)')
        text = render_record(2014, load_events(self.root, self.mapping), self.root)
        self.assertIn('April 2014 (exact date unrecorded)', text)
        self.assertNotIn('April 1, 2014', text)

    def test_missing_owner_alias_is_rejected(self):
        self.mapping['legacy_event_aliases']['106'] = ['missing-event']
        with self.assertRaisesRegex(ValueError, 'missing owner'):
            load_events(self.root, self.mapping)

    def test_duplicate_event_owner_is_rejected(self):
        self.write_event()
        self.write_event('career/2014/duplicate.md')
        with self.assertRaisesRegex(ValueError, 'Duplicate event owner'):
            load_events(self.root, self.mapping)

    def test_closure_order_is_independent_of_event_date(self):
        self.write_event(closure={'checkpoint': 'Earlier closure', 'through': '2014-04-07', 'sequence': 1})
        self.write_event(id='2014-04-04-retrospective', date='2014-04-04',
                         closure={'checkpoint': 'Latest closure', 'through': '2014-04-07', 'sequence': 2})
        self.assertEqual(closures(load_events(self.root, self.mapping))[-1][2]['checkpoint'], 'Latest closure')

    def test_same_day_closed_transactions_keep_their_recorded_order(self):
        self.write_event(id='2014-04-07-z-acquire-picks', summary='Jacksonville acquired picks.',
                         closure={'checkpoint': 'Picks acquired', 'through': '2014-04-07', 'sequence': 104})
        self.write_event(id='2014-04-07-a-send-picks', summary='Jacksonville traded those picks.',
                         closure={'checkpoint': 'Picks traded', 'through': '2014-04-07', 'sequence': 105})
        text = render_record(2014, load_events(self.root, self.mapping), self.root)
        self.assertLess(text.index('acquired picks'), text.index('traded those picks'))

    def test_duplicate_closure_sequence_is_rejected(self):
        self.write_event(closure={'checkpoint': 'One', 'through': '2014-04-07', 'sequence': 1})
        self.write_event(id='2014-04-08-two', closure={'checkpoint': 'Two', 'through': '2014-04-08', 'sequence': 1})
        with self.assertRaisesRegex(ValueError, 'Duplicate event closure'):
            load_events(self.root, self.mapping)

    def test_invalid_or_incomplete_event_is_rejected(self):
        self.write_event(date_end='2014-04-06')
        with self.assertRaisesRegex(ValueError, 'ends before'):
            load_events(self.root, self.mapping)

    def test_future_playbooks_are_never_read(self):
        path = self.root / 'career/playbook/2050_future.md'
        path.parent.mkdir(parents=True)
        path.write_bytes(b'\xff')
        self.write_event()
        self.assertEqual(len(load_events(self.root, self.mapping)), 1)

    def test_frozen_source_path_resolves_without_changing_receipt(self):
        self.write_event()
        receipt = {'source': 'career/2014/old_trade.md', 'source_sha256': 'unchanged'}
        original = json.dumps(receipt)
        self.mapping['path_aliases'] = {receipt['source']: 'career/2014/trades/trade.md'}
        self.assertTrue(resolve_path(self.root, receipt['source'], self.mapping).is_file())
        self.assertEqual(json.dumps(receipt), original)

    def test_path_alias_escape_and_cycle_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'leaves repository'):
            resolve_path(self.root, '../outside', self.mapping)
        self.mapping['path_aliases'] = {'one': 'two', 'two': 'one'}
        with self.assertRaisesRegex(ValueError, 'Cyclic'):
            resolve_path(self.root, 'one', self.mapping)

    def test_regeneration_keeps_owner_metadata_but_replaces_stale_prose(self):
        event = self.write_event()
        marker = '<!-- event-record: ' + json.dumps(event) + ' -->'
        existing = '# Stale result\n\nWrong score.\n\n' + marker + '\n'
        generated = '# Receipt result\n\nRecorded score.\n'
        result = preserve_event_comments(generated, existing)
        self.assertIn(marker, result)
        self.assertNotIn('Wrong score', result)
        self.assertEqual(result, preserve_event_comments(generated, result))
        self.assertEqual(result, preserve_event_comments(result, existing))


if __name__ == '__main__':
    unittest.main()
