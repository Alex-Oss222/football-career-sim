from runtime.seasons import SeasonPaths
import re
import json
import tempfile
import unittest
from pathlib import Path
from runtime import player_cards
from scripts.update_player_cards import (
    ROOT, START, END, LEAD, columns, clean_labels, refresh_text, stats_block,
    stat_values, profile_errors, period_data, season_rows, lead_cells,
)

CARDS = SeasonPaths(2014, ROOT).record('player_profiles')
_ROWS = None


def rows_2014():
    """season_rows for every committed 2014 card, computed once."""
    global _ROWS
    if _ROWS is None:
        names = [re.search(r'^# (.+?) — ', p.read_text(encoding='utf-8'), re.M)[1]
                 for p in sorted(CARDS.glob('*.md')) if p.name not in ('README.md', 'TEMPLATE.md')]
        _ROWS = season_rows(2014, names)
    return _ROWS


def table_rows(text, heading):
    """{season: {column: cell}} for one statistics table of a card or a league page."""
    body = text.split(heading, 1)[1]
    lines = [l for l in body.splitlines() if l.startswith('|')]
    lines = lines[:next((i for i, l in enumerate(lines[1:], 1) if l.startswith('| Season |')), len(lines))]
    head = [c.strip() for c in lines[0].strip('|').split('|')]
    return {cells[0]: dict(zip(head, cells)) for cells in
            ([c.strip() for c in l.strip('|').split('|')] for l in lines[2:])}


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
            path = SeasonPaths(2014, root).record('stats/game_receipts/game.json')
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
        cards = list(SeasonPaths(2014, ROOT).record('player_profiles').glob('*.md'))
        self.assertEqual(len(cards), 85)  # 78 current players and Alan Ball's September 8 entry card, 4 former players, index and template

    def test_player_facing_year_labels_preserve_proper_name(self):
        self.assertEqual(clean_labels('Andre Branch; Branch evidence; Branch regular season'),
                         'Andre Branch; recorded evidence; 2013 regular season')
        for year in (2013, 2014):
            for path in SeasonPaths(year, ROOT).record('player_profiles').glob('*.md'):
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
            opening = '| Overall | 6.0 /10 | Staff judgment |\n'
            update = '\n## Dated coaching updates\n\n### August 1, 2014\n\nProtection check held; game rush remains untested.\n\n'
            text = opening+update+old+'\n'
            updated = refresh_text(text, 2014, 'Kirk Cousins', 'QB',
                                   {False: period(300), True: period(100, 19)}, root)
            self.assertTrue(updated.startswith(opening+update))
            self.assertEqual(updated.count('| 2013 |'), 2)
            self.assertEqual(updated.count('| 2014 |'), 2)
            regular, playoffs = updated.split('## Playoff statistics by year')
            self.assertIn('| 300 |', regular)
            self.assertIn('| 100 |', playoffs)
            self.assertEqual(updated.count(START), 1)
            self.assertTrue(updated.rstrip().endswith(END))

    def test_season_rows_lead_with_season_team_age_and_number(self):
        text = (CARDS/'kirk_cousins.md').read_text(encoding='utf-8')
        for heading in ('## Regular-season statistics by year', '## Playoff statistics by year'):
            header = next(l for l in text.split(heading, 1)[1].splitlines() if l.startswith('| Season |'))
            self.assertTrue(header.startswith('| Season | Team | Age | # | Coverage | G |'), header)
            row = table_rows(text, heading)['2014']
            team, age, number = rows_2014()['Kirk Cousins']
            self.assertEqual((row['Team'], row['Age'], row['#']), (team, str(age), str(number)))
            self.assertEqual(team, 'Jacksonville Jaguars')
        self.assertEqual(lead_cells(2014), ['2014', 'Jacksonville Jaguars', 'N/A', 'N/A'])
        self.assertEqual(lead_cells(2014, ('Jacksonville Jaguars', 26, 8)), ['2014', 'Jacksonville Jaguars', '26', '8'])
        with tempfile.TemporaryDirectory() as folder:
            block = stats_block(2014, 'Kirk Cousins', 'QB', {False: period(250), True: period()},
                                root=Path(folder), row=('Jacksonville Jaguars', 26, None))
        self.assertIn('| '+' | '.join(LEAD)+' | G |', block)
        self.assertIn('| 2014 | Jacksonville Jaguars | 26 | N/A | Through Week 1 |', block)
        separator = next(l for l in block.splitlines() if l.startswith('| --- '))
        self.assertEqual(separator.count('---'), len(LEAD)+len(columns('QB')))

    def test_card_and_league_page_agree_on_team_age_and_number(self):
        """Every card that links to his league page shows that page's 2014 age and number."""
        compared = 0
        for path in sorted(CARDS.glob('*.md')):
            text = path.read_text(encoding='utf-8')
            link = re.search(r'\[Career statistics\]\(([^)]+)\)', text)
            if not link:
                continue
            league = (path.parent/link[1]).resolve().read_text(encoding='utf-8')
            mine = table_rows(text, '## Regular-season statistics by year')['2014']
            theirs = table_rows(league, '### Regular season').get('2014')
            if theirs is None:
                continue
            compared += 1
            self.assertEqual((mine['Age'], mine['#']), (theirs['Age'], theirs['#']), path.name)
            self.assertIn(mine['Team'], theirs['Team'].split(', '), path.name)
        self.assertGreaterEqual(compared, 50)

    def test_rows_use_the_league_cards_birth_dates_and_season_number(self):
        data = player_cards.card_data(ROOT)
        rows = rows_2014()
        # A current Jaguar: his league card's age on the 2014 opening game and his card's number.
        cousins = next(p for p in data['players'] if p['name'] == 'Kirk Cousins' and p['current_jaguar'])
        self.assertEqual(rows['Kirk Cousins'][1], player_cards.age_on(cousins['birth_date'], '2014-09-04'))
        self.assertEqual(rows['Kirk Cousins'][2], cousins['number'])
        # A former Jaguar now with another club: his age, but no Jacksonville number (none recorded),
        # though his league page lists one with his new club.
        cain = next(p for p in data['players'] if p['name'] == 'Jeremy Cain')
        self.assertNotEqual(cain['team'], player_cards.JAX)
        self.assertIsNotNone(cain['number'])
        self.assertEqual(rows['Jeremy Cain'], (player_cards.JAX, player_cards.age_on(cain['birth_date'], '2014-09-04'), None))
        # No game on record: no league player; the same birth-date sources give his age, no number.
        self.assertFalse(any('Cameron Brate' in p['record_names'] for p in data['players']))
        ident = player_cards.Identity(ROOT)
        dob = ident.birth_date({'Cameron Brate'}, None, ident.week1_row(None, 'Cameron Brate'), 'Cameron Brate')
        self.assertIsNotNone(dob)
        self.assertEqual(rows['Cameron Brate'], (player_cards.JAX, player_cards.age_on(dob, '2014-09-04'), None))
        card = table_rows((CARDS/'cameron_brate.md').read_text(encoding='utf-8'), '## Regular-season statistics by year')
        self.assertEqual(card['2014']['#'], 'N/A')

    def test_a_root_without_league_records_reads_na(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(season_rows(2014, ['Kirk Cousins'], Path(folder)), {})

    def test_both_years_show_the_completed_2013_production(self):
        for year in (2013, 2014):
            text = SeasonPaths(year, ROOT).record('player_profiles/kirk_cousins.md').read_text(encoding='utf-8')
            self.assertIn('| Statistic | 2013 regular season | 2013 playoffs |', text)
            self.assertIn('| YDS | 3981 | 480 |', text)


if __name__ == '__main__':
    unittest.main()
