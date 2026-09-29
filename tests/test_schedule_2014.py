"""Branch opponent construction, separate from the future dated scheduler."""
from collections import Counter
from copy import deepcopy
import json
import unittest

from runtime import schedule_2014 as schedule
from runtime.league import DIVISIONS, TEAMS


class OpponentMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads((schedule.ROOT / schedule.FOLDER / 'rotation_2014.json').read_text())
        cls.data = schedule.build()
        cls.games = cls.data['games']

    def test_complete_balanced_league_and_reciprocal_division_games(self):
        self.assertEqual(len(self.games), 256)
        pairs = {(g['home'], g['away']) for g in self.games}
        self.assertEqual(len(pairs), 256)
        for team in TEAMS:
            games = [g for g in self.games if team in (g['home'], g['away'])]
            self.assertEqual(sum(g['home'] == team for g in games), 8)
            self.assertEqual(sum(g['away'] == team for g in games), 8)
            self.assertEqual(Counter(g['component'] for g in games),
                             {'division': 6, 'conference_rotation': 4,
                              'interconference_rotation': 4, 'same_place': 2})
        for teams in DIVISIONS.values():
            for home in teams:
                for away in teams:
                    if home != away:
                        self.assertIn((home, away), pairs)

    def test_jacksonville_uses_branch_place_not_historical_place(self):
        jax = 'Jacksonville Jaguars'
        home = {g['away'] for g in self.games if g['home'] == jax}
        away = {g['home'] for g in self.games if g['away'] == jax}
        self.assertEqual(home, {'Tennessee Titans', 'Indianapolis Colts', 'Houston Texans',
                               'Cleveland Browns', 'Pittsburgh Steelers', 'New York Giants',
                               'Dallas Cowboys', 'Buffalo Bills'})
        self.assertEqual(away, {'Tennessee Titans', 'Indianapolis Colts', 'Houston Texans',
                               'Baltimore Ravens', 'Cincinnati Bengals', 'Philadelphia Eagles',
                               'Washington Redskins', 'San Diego Chargers'})
        self.assertEqual(self.data['division_order_2013']['AFC West'][:2],
                         ['Kansas City Chiefs', 'San Diego Chargers'])

    def test_independent_rotation_spot_checks(self):
        # Primary Raiders and Panthers releases dated December 30/31, 2013.
        # Ignore their real standings-dependent games, which do not control here.
        expected = {
            'Oakland Raiders': ({'Buffalo Bills', 'Miami Dolphins', 'Arizona Cardinals', 'San Francisco 49ers'},
                                {'New England Patriots', 'New York Jets', 'St. Louis Rams', 'Seattle Seahawks'}),
            'Carolina Panthers': ({'Chicago Bears', 'Detroit Lions', 'Cleveland Browns', 'Pittsburgh Steelers'},
                                  {'Green Bay Packers', 'Minnesota Vikings', 'Baltimore Ravens', 'Cincinnati Bengals'}),
        }
        for team, (home, away) in expected.items():
            rotation = [g for g in self.games if g['component'].endswith('rotation')]
            self.assertEqual({g['away'] for g in rotation if g['home'] == team}, home)
            self.assertEqual({g['home'] for g in rotation if g['away'] == team}, away)

    def test_changed_standings_move_only_same_place_games(self):
        ranks = deepcopy(self.data['division_order_2013'])
        ranks['AFC South'][0], ranks['AFC South'][1] = ranks['AFC South'][1], ranks['AFC South'][0]
        changed = schedule.build_games(self.config, ranks)
        unaffected = lambda games: [g for g in games if g['component'] != 'same_place']
        self.assertEqual(unaffected(changed), unaffected(self.games))
        jax_same = [g for g in changed if g['component'] == 'same_place'
                    and 'Jacksonville Jaguars' in (g['home'], g['away'])]
        self.assertEqual({(g['home'], g['away']) for g in jax_same}, {
            ('Jacksonville Jaguars', 'New York Jets'),
            ('Kansas City Chiefs', 'Jacksonville Jaguars')})

    def test_dates_are_only_preannounced_london_anchors(self):
        self.assertEqual(self.data['status'], 'OPPONENTS_ONLY')
        self.assertEqual({(g['week'], g['date'], g['home'], g['away'])
                          for g in self.data['fixed_games']}, {
            (4, '2014-09-28', 'Oakland Raiders', 'Miami Dolphins'),
            (8, '2014-10-26', 'Atlanta Falcons', 'Detroit Lions'),
            (10, '2014-11-09', 'Jacksonville Jaguars', 'Dallas Cowboys')})
        self.assertTrue(all(g['neutral_site'] for g in self.data['fixed_games']))
        self.assertTrue(all(set(g) == {'home', 'away', 'component'} for g in self.games))
        self.assertTrue(all(s['published'] <= self.data['as_of'] for s in self.config['sources']))

    def test_incomplete_receipts_and_invalid_division_order_fail(self):
        with self.assertRaisesRegex(ValueError, 'complete 2013 regular season'):
            schedule.branch_ranks([])
        ranks = deepcopy(self.data['division_order_2013'])
        ranks['AFC South'][0] = 'Dallas Cowboys'
        with self.assertRaisesRegex(ValueError, 'permutations'):
            schedule.build_games(self.config, ranks)

    def test_unresolved_division_tie_fails_instead_of_using_name_order(self):
        receipts = []
        for path in sorted((schedule.ROOT / 'career/2013/stats/game_receipts').glob('*.json')):
            r = json.loads(path.read_text())
            r['final_score'] = {r['home']: 0, r['away']: 0}
            r['team_stats'] = {r['home']: {'touchdowns': 0}, r['away']: {'touchdowns': 0}}
            receipts.append(r)
        with self.assertRaisesRegex(ValueError, 'division tie unresolved'):
            schedule.branch_ranks(receipts)

    def test_duplicate_game_and_bad_same_place_pair_fail(self):
        games = deepcopy(self.games)
        games[-1] = games[0]
        with self.assertRaisesRegex(ValueError, '256 unique'):
            schedule.validate_games(games, self.data['division_order_2013'])
        ranks = deepcopy(self.data['division_order_2013'])
        ranks['AFC South'][0], ranks['AFC South'][1] = ranks['AFC South'][1], ranks['AFC South'][0]
        with self.assertRaisesRegex(ValueError, 'same-place pairing'):
            schedule.validate_games(self.games, ranks)

    def test_committed_generated_views_match(self):
        self.assertEqual(schedule.check(), [])


if __name__ == '__main__':
    unittest.main()
