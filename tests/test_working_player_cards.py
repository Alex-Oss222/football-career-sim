import re
import json
import tempfile
import unittest
from pathlib import Path
from scripts.update_player_cards import (
    ROOT, START, END, columns, clean_labels, refresh_text, stats_block,
    stat_values, profile_errors, period_data,
)


def period(yards=None, week=1):
    line = {} if yards is None else {'games': 1, 'passing_yards': yards}
    return {'players': {'Kirk Cousins': line},
            'fields': {'Kirk Cousins': set(line)}, 'games': int(yards is not None),
            'through': week, 'complete': True}


class WorkingPlayerCardTests(unittest.TestCase):
    def test_receipt_aggregation_keeps_season_periods_separate(self):
        regular = period_data(2013)
        playoffs = period_data(2013, True)
        self.assertEqual(regular['games'], 16)
        self.assertEqual(playoffs['games'], 2)
        self.assertEqual(regular['players']['Kirk Cousins']['passing_yards'], 3981)
        self.assertEqual(playoffs['players']['Kirk Cousins']['passing_yards'], 480)
        _, values = stat_values('Kirk Cousins', 'QB', regular)
        self.assertEqual(values[0], '16')

    def test_wrong_season_and_game_type_receipts_are_rejected(self):
        source = next((ROOT/'career/2013/stats/game_receipts').glob('*.json'))
        receipt = json.loads(source.read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root/'career/2014/stats/game_receipts/game.json'
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(receipt), encoding='utf-8')
            with self.assertRaises(ValueError):
                period_data(2014, root=root)
            path = root/'career/2013/stats/postseason_receipts/game.json'
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(receipt), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Wrong game type'):
                period_data(2013, True, root)

    def test_longest_field_goal_uses_maximum_instead_of_sum(self):
        receipts = [json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'career/2013/stats/game_receipts').glob('*.json')]
        receipts = [r for r in receipts if 'Josh Scobee' in r['team_stats'].get('Jacksonville Jaguars', {}).get('players', {})][:2]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            directory = root/'career/2013/stats/game_receipts'
            directory.mkdir(parents=True)
            for index, receipt in enumerate(receipts):
                receipt['team_stats']['Jacksonville Jaguars']['players']['Josh Scobee']['long_field_goal'] = (47, 52)[index]
                (directory/f'{index}.json').write_text(json.dumps(receipt), encoding='utf-8')
            data = period_data(2013, root=root)
            self.assertEqual(data['players']['Josh Scobee']['long_field_goal'], 52)
            _, values = stat_values('Josh Scobee', 'K', data)
            self.assertEqual(values[[c[0] for c in columns('K')].index('LONG')], '52')

    def test_current_roster_cards_and_stats_are_consistent(self):
        self.assertEqual(profile_errors(2014), [])
        cards = list((ROOT/'career/2014/player_profiles').glob('*.md'))
        self.assertEqual(len(cards), 57)  # 55 players, index and template

    def test_player_facing_year_labels_preserve_proper_name(self):
        self.assertEqual(clean_labels('Andre Branch; Branch evidence; Branch regular season'),
                         'Andre Branch; recorded evidence; 2013 regular season')
        for year in (2013, 2014):
            for path in (ROOT/f'career/{year}/player_profiles').glob('*.md'):
                text = path.read_text(encoding='utf-8').replace('Andre Branch', '')
                self.assertIsNone(re.search(r'\bbranch\b', text, re.I), str(path))

    def test_missing_stat_is_unrecorded_and_real_zero_is_preserved(self):
        status, values = stat_values('Kirk Cousins', 'QB', period(0))
        headers = [c[0] for c in columns('QB')]
        self.assertEqual(status, 'Through Week 1')
        self.assertEqual(values[headers.index('YDS')], '0')
        self.assertEqual(values[headers.index('CMP')], 'Unrecorded')

    def test_absent_closed_receipts_do_not_claim_no_playoff_appearance(self):
        status, _ = stat_values('Kirk Cousins', 'QB', period(), True, True)
        self.assertEqual(status, 'Unrecorded')

    def test_stats_refresh_preserves_evaluation_and_prior_year(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            old = stats_block(2014, 'Kirk Cousins', 'QB', {False: period(250), True: period(80, 19)}, root=root)
            old = old.replace('| 2014 |', '| 2013 |')
            text = '| Overall | 6.0 /10 | Staff judgment |\n'+old+'\n'
            updated = refresh_text(text, 2014, 'Kirk Cousins', 'QB',
                                   {False: period(300), True: period(100, 19)}, root)
            self.assertTrue(updated.startswith('| Overall | 6.0 /10 | Staff judgment |\n'))
            self.assertEqual(updated.count('| 2013 |'), 2)
            self.assertEqual(updated.count('| 2014 |'), 2)
            regular, playoffs = updated.split('## Playoff statistics by year')
            self.assertIn('| 300 |', regular)
            self.assertIn('| 100 |', playoffs)
            self.assertEqual(updated.count(START), 1)
            self.assertTrue(updated.rstrip().endswith(END))

    def test_both_years_show_the_completed_2013_production(self):
        for year in (2013, 2014):
            text = (ROOT/f'career/{year}/player_profiles/kirk_cousins.md').read_text(encoding='utf-8')
            self.assertIn('| Statistic | 2013 regular season | 2013 playoffs |', text)
            self.assertIn('| YDS | 3981 | 480 |', text)


if __name__ == '__main__':
    unittest.main()
