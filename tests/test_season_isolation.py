"""New-season setup must fail closed without touching prior-season canon."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from runtime import game_runner, week_inputs
from runtime.seasons import SeasonPaths, current_record, require_receipt_season
from scripts import close_week, build_week_inputs, render_box_score
import check_game_readiness


class SeasonIsolationTests(unittest.TestCase):
    def test_missing_2014_schedule_never_uses_2013(self):
        with tempfile.TemporaryDirectory(dir=ROOT.parent) as tmp:
            root = Path(tmp)
            old = root / 'library/data/2013_schedule.json'
            old.parent.mkdir(parents=True)
            old.write_text(json.dumps({'games': [{'week': 1, 'date': '2013-09-08'}]}))
            with patch.object(week_inputs, 'ROOT', root):
                self.assertEqual(len(week_inputs.schedule(1, 2013)), 1)
                with self.assertRaises(FileNotFoundError):
                    week_inputs.schedule(1, 2014)

    def test_future_research_cannot_be_used_as_released_fixtures(self):
        with tempfile.TemporaryDirectory(dir=ROOT.parent) as tmp:
            paths = SeasonPaths(2014, Path(tmp))
            paths.schedule.parent.mkdir(parents=True)
            for data in ({'season': 2013, 'status': 'RELEASED', 'games': []},
                         {'season': 2014, 'status': 'PREPARED', 'games': []},
                         {'season': 2014, 'status': 'RELEASED', 'games': [{'date': '2013-09-08'}]}):
                paths.schedule.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    paths.regular_games()

    def test_cache_and_event_identity_are_season_separated(self):
        game = {'week': 1, 'home': 'B', 'away': 'A'}
        self.assertEqual(week_inputs.event_id(game, 1, 2013), '2013-week01-a-at-b')
        self.assertEqual(week_inputs.event_id(game, 1, 2014), '2014-week01-a-at-b')
        self.assertNotEqual(SeasonPaths(2013).cache(1, 'inputs'), SeasonPaths(2014).cache(1, 'inputs'))
        with self.assertRaises(ValueError):
            SeasonPaths(2015)

    def test_foreign_or_unqualified_receipts_are_rejected(self):
        for row in ({'event_id': '2013-week01-a-at-b'}, {'event_id': 'untagged'},
                    {'event_id': '2014-week01-a-at-b', 'season': 2013}):
            with self.assertRaises(ValueError):
                require_receipt_season([row], 2014)
        require_receipt_season([{'event_id': '2013-week01-a-at-b'}], 2013)

    def test_current_owner_changes_only_with_explicit_map(self):
        with tempfile.TemporaryDirectory(dir=ROOT.parent) as tmp:
            root = Path(tmp)
            (root / 'docs').mkdir()
            for year in (2013, 2014):
                file = root / 'career' / str(year) / 'roster.md'
                file.parent.mkdir(parents=True)
                file.write_text(str(year))
            mapping = {'active_season': 2014, 'current_records': {'roster': 'career/2013/roster.md'}}
            (root / 'docs/repository_map.json').write_text(json.dumps(mapping))
            self.assertEqual(current_record('roster', root).read_text(), '2013')
            mapping['current_records']['roster'] = 'career/2014/roster.md'
            (root / 'docs/repository_map.json').write_text(json.dumps(mapping))
            self.assertEqual(current_record('roster', root).read_text(), '2014')

    def test_successful_service_cannot_override_open_2014_release(self):
        with patch.object(check_game_readiness, 'validate', return_value=[]), \
                patch.object(check_game_readiness, 'Client') as client, \
                patch.dict(os.environ, {'ENGINE_RUNTIME_URL': 'http://audit.invalid', 'ENGINE_API_TOKEN': 'synthetic'}):
            client.return_value.readiness.return_value = {'ready': True}
            result = check_game_readiness.assess(season=2014)
            self.assertFalse(result['ready'])
            self.assertIn('season_release', {b['id'] for b in result['blockers']})
            client.assert_not_called()

    def test_direct_2014_game_is_blocked_before_private_closure(self):
        client = Mock()
        with self.assertRaisesRegex(ValueError, 'game execution blocked'):
            game_runner.run_game(None, None, event_id='2014-week01-a-at-b',
                                 snapshot='synthetic-snapshot', client=client)
        client.close_event.assert_not_called()

    def test_week_commands_block_before_reading_or_writing_packages(self):
        for module in (build_week_inputs, close_week):
            with patch.object(sys, 'argv', ['test', '1', '--season', '2014']), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(module.main(), 1)

    def test_box_score_cannot_write_another_season(self):
        with patch.object(sys, 'argv', ['test', '--season', '2014', '--write',
                                      str(ROOT / 'career/2013/README.md')]), \
                contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                render_box_score.main()

    def test_synthetic_closure_routes_only_to_requested_season(self):
        # Storage integration only: no real kernel, service, fixture or game runs.
        with tempfile.TemporaryDirectory(dir=ROOT.parent) as tmp:
            root = Path(tmp)
            paths = SeasonPaths(2014, root)
            sentinel = root / 'career/2013/stats/game_receipts/closed.json'
            sentinel.parent.mkdir(parents=True)
            sentinel.write_bytes(b'prior canon')
            state = root / 'state/05_Current_Season_State.md'
            state.parent.mkdir()
            state.write_text('isolated synthetic checkpoint')
            game = {'event_id': '2014-week01-a-at-b', 'receipt': 'week_01_a_at_b.json',
                    'week': 1, 'home': 'B', 'away': 'A', 'venue': 'home',
                    'home_input': {}, 'away_input': {}}
            package = {'season': 2014, 'week': 1, 'games': [game]}
            paths.cache(1, 'inputs').parent.mkdir(parents=True)
            paths.cache(1, 'inputs').write_text(json.dumps(package))
            receipt = {'event_id': game['event_id'], 'week': 1}
            with patch.object(close_week, 'ROOT', root), \
                    patch.object(close_week, 'require_game_release'), \
                    patch.object(close_week, 'team_input', side_effect=lambda x: x), \
                    patch.object(week_inputs, 'schedule', return_value=[game]), \
                    patch('scripts.check_week_input_exclusivity.controlled_players_from_roster', return_value=[]), \
                    patch('scripts.check_week_input_exclusivity.check_inputs', return_value=[]), \
                    patch('runtime.game_runner.run_game', return_value={'synthetic': True}) as runner, \
                    patch('runtime.private_client.Client'), \
                    patch('runtime.statbook.make_receipt', return_value=receipt), \
                    patch.object(close_week.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, 'GAME READINESS: READY', '')) as commands, \
                    patch.object(sys, 'argv', ['test', '1', '--season', '2014', '--close']), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(close_week.main(), 0)
            self.assertEqual(sentinel.read_bytes(), b'prior canon')
            self.assertEqual(json.loads((paths.receipts / game['receipt']).read_text())['season'], 2014)
            self.assertEqual(len(list((root / 'career/2013').rglob('*json'))), 1)
            self.assertTrue(paths.cache(1, 'results').exists())
            runner.assert_called_once()
            self.assertEqual(commands.call_args_list[-1].args[0][-1], '2014')


if __name__ == '__main__':
    unittest.main()
