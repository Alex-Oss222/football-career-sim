"""Physical migration preserves event payloads and refuses partial collisions."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.migrate_season_layout import migrate


class LayoutMigrationTests(unittest.TestCase):
    def write(self, root, name, text):
        path = root/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def baseline(self, root):
        self.write(root, 'docs/repository_map.json', json.dumps({'active_playbooks': []}))
        self.write(root, 'career/2014/offseason_training/otas/staff_plan.md',
                   '# OTAs\n\n[Observed work](training_report.md)\n[Calendar](../../calendar.md)\n')
        self.write(root, 'career/2014/offseason_training/otas/training_report.md', '# Observed work\n')
        self.write(root, 'career/2014/calendar.md', '# Calendar\n')
        self.write(root, 'career/2014/draft/frozen.json', '{"source":"career/2014/calendar.md","event_id":"unchanged"}\n')

    def test_preview_writes_nothing_and_apply_preserves_frozen_payload(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.baseline(root)
            before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            preview = migrate(root, [2014], rewrite_links=True)
            self.assertEqual(len(preview['moves']), 4)
            self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()})
            applied = migrate(root, [2014], write=True, rewrite_links=True)
            self.assertEqual(preview, applied)
            frozen = root/'career/2014/03_Draft/frozen.json'
            self.assertEqual(frozen.read_bytes(), before[Path('career/2014/draft/frozen.json')])
            plan = root/'career/2014/02_Offseason_Training/OTAs/staff_plan.md'
            self.assertIn('[Calendar](../../Calendar.md)', plan.read_text())
            self.assertFalse((root/'career/2014/offseason_training').exists())
            self.assertEqual(migrate(root, [2014], write=True, rewrite_links=True)['moves'], {})

    def test_collision_and_unmigrated_ledger_fail_before_any_move(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.baseline(root)
            target = self.write(root, 'career/2014/Calendar.md', 'Existing calendar')
            with self.assertRaisesRegex(ValueError, 'destination already exists'):
                migrate(root, [2014], write=True)
            self.assertEqual(target.read_text(), 'Existing calendar')
            self.assertTrue((root/'career/2014/draft/frozen.json').is_file())
            target.unlink()
            self.write(root, 'career/2014/ledger.md', '# Still owns evidence')
            with self.assertRaisesRegex(ValueError, 'Migrate ledger facts'):
                migrate(root, [2014], write=True)
            self.assertTrue((root/'career/2014/calendar.md').is_file())

    def test_2013_and_future_playbook_contents_stay_untouched(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.baseline(root)
            old = self.write(root, 'career/2013/roster.md', '# Historical roster\n')
            future = self.write(root, 'career/playbook/future.md', '[Unopened](../2014/calendar.md)')
            migrate(root, [2014], write=True, rewrite_links=True)
            self.assertEqual(old.read_text(), '# Historical roster\n')
            self.assertEqual(future.read_text(), '[Unopened](../2014/calendar.md)')
            with self.assertRaisesRegex(ValueError, '2014 onward'):
                migrate(root, [2013], write=True)


if __name__ == '__main__':
    unittest.main()
