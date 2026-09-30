"""Acceptance checks for the prepared April 23, 2014 historical fixture release."""
from collections import Counter
from datetime import date, datetime
import json
import re
import unittest
from zoneinfo import ZoneInfo

from runtime import week_inputs
from runtime.league import DIVISION_OF, TEAMS
from runtime.seasons import SeasonPaths
from runtime.schedule_2014 import FOLDER, ROOT

JAX = 'Jacksonville Jaguars'
FIELDS = {'game_id', 'week', 'date', 'weekday', 'kickoff_et', 'away', 'home', 'site', 'stadium'}
OPTIONAL = {'city', 'note'}


class Fixtures2014Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / FOLDER / 'fixtures.json').read_text())
        cls.games = cls.data['games']
        cls.opponents = json.loads((ROOT / FOLDER / 'league_opponents.json').read_text())

    def test_release_identity_and_runtime_loading(self):
        self.assertEqual((self.data['season'], self.data['status']), (2014, 'RELEASED'))
        self.assertEqual(self.data['usable_from'], '2014-04-23T20:00:00-04:00')
        self.assertEqual(SeasonPaths(2014, ROOT).regular_games(), self.games)
        self.assertEqual(len(week_inputs.schedule(1, 2014)), 16)

    def test_schedule_facts_only(self):
        for g in self.games:
            self.assertTrue(FIELDS <= set(g) <= FIELDS | OPTIONAL, g)
        self.assertEqual(set(self.data), {'schema_version', 'season', 'status', 'released', 'usable_from',
                                          'source', 'source_sha256', 'policy', 'games', 'amendments'})

    def test_unique_season_qualified_ids_match_runtime_event_ids(self):
        ids = [g['game_id'] for g in self.games]
        self.assertEqual(len(ids), 256)
        self.assertEqual(len(set(ids)), 256)
        for g in self.games:
            self.assertEqual(g['game_id'], week_inputs.event_id(g, 1, 2014))

    def test_club_balance_weeks_and_byes(self):
        self.assertEqual({t for g in self.games for t in (g['home'], g['away'])}, set(TEAMS))
        self.assertEqual({g['week'] for g in self.games}, set(range(1, 18)))
        slots = Counter((g['week'], t) for g in self.games for t in (g['home'], g['away']))
        self.assertEqual(max(slots.values()), 1)
        for team in TEAMS:
            self.assertEqual(sum(g['home'] == team for g in self.games), 8, team)
            self.assertEqual(sum(g['away'] == team for g in self.games), 8, team)
            byes = [w for w in range(1, 18) if (w, team) not in slots]
            self.assertEqual(len(byes), 1, team)
        self.assertEqual([w for w in range(1, 18) if (w, JAX) not in slots], [11])

    def test_matches_historical_opponent_inventory(self):
        self.assertEqual({(g['home'], g['away']) for g in self.games},
                         {(g['home'], g['away']) for g in self.opponents['games']})
        for g in self.games:
            self.assertNotEqual(g['home'], g['away'])
            self.assertIn(g['home'], DIVISION_OF)

    def test_dates_weekdays_and_kickoff_format(self):
        for g in self.games:
            day = date.fromisoformat(g['date'])
            self.assertEqual(day.strftime('%A'), g['weekday'])
            self.assertTrue(date(2014, 9, 4) <= day <= date(2014, 12, 28))
            self.assertRegex(g['kickoff_et'], r'^([01]\d|2[0-3]):[0-5]\d$')
        opener = [g for g in self.games if g['week'] == 1 and g['weekday'] == 'Thursday']
        self.assertEqual([(g['away'], g['home'], g['date']) for g in opener],
                         [('Green Bay Packers', 'Seattle Seahawks', '2014-09-04')])
        thanksgiving = {(g['away'], g['home'], g['kickoff_et'])
                        for g in self.games if g['date'] == '2014-11-27'}
        self.assertEqual(thanksgiving, {('Chicago Bears', 'Detroit Lions', '12:30'),
                                        ('Philadelphia Eagles', 'Dallas Cowboys', '16:30'),
                                        ('Seattle Seahawks', 'San Francisco 49ers', '20:30')})

    def test_london_neutral_sites_and_local_kickoffs(self):
        neutral = [g for g in self.games if g['site'] == 'neutral']
        self.assertEqual({(g['week'], g['date'], g['home'], g['away']) for g in neutral},
                         {(g['week'], g['date'], g['home'], g['away']) for g in self.opponents['fixed_games']})
        local = {}
        for g in neutral:
            self.assertEqual((g['stadium'], g.get('city')), ('Wembley Stadium', 'London'))
            et = datetime.fromisoformat(g['date'] + 'T' + g['kickoff_et']).replace(tzinfo=ZoneInfo('America/New_York'))
            local[g['week']] = et.astimezone(ZoneInfo('Europe/London')).strftime('%H:%M')
        self.assertEqual(local, {4: '18:00', 8: '13:30', 10: '18:00'})

    def test_each_home_club_uses_one_home_stadium(self):
        stadiums = {}
        for g in self.games:
            if g['site'] == 'home':
                stadiums.setdefault(g['home'], set()).add(g['stadium'])
        self.assertTrue(all(len(s) == 1 for s in stadiums.values()), stadiums)
        self.assertEqual(stadiums['New York Giants'], stadiums['New York Jets'])
        self.assertEqual(stadiums['Buffalo Bills'], {'Ralph Wilson Stadium'})

    def test_jacksonville_calendar(self):
        jax = {g['week']: g for g in self.games if JAX in (g['home'], g['away'])}
        self.assertEqual(len(jax), 16)
        thursday = jax[16]
        self.assertEqual((thursday['date'], thursday['weekday'], thursday['home'], thursday['away']),
                         ('2014-12-18', 'Thursday', JAX, 'Tennessee Titans'))
        self.assertEqual((jax[10]['site'], jax[10]['home'], jax[10]['away']), ('neutral', JAX, 'Dallas Cowboys'))
        self.assertEqual(sum(g['home'] == JAX and g['site'] == 'home' for g in jax.values()), 7)

    def test_amendments_are_listed_not_applied(self):
        by_id = {g['game_id']: g for g in self.games}
        for amendment in self.data['amendments']:
            game = by_id[amendment['game_id']]
            self.assertTrue(any(game[k] != v for k, v in amendment['change'].items()), amendment)
            self.assertTrue(amendment.get('effective') or amendment.get('not_before')
                            or amendment['kind'].endswith('unresolved'))

    def test_readable_view_matches_byes(self):
        text = (ROOT / FOLDER / 'fixtures.md').read_text()
        codes = {v: k for k, v in json.loads((ROOT / FOLDER / 'rotation_2014.json').read_text())['club_codes'].items()}
        for week in range(1, 18):
            row = re.search(r'^\| %d \| [^|]+ \| (\d+) \| ([^|]+) \|' % week, text, re.M)
            playing = {t for g in self.games if g['week'] == week for t in (g['home'], g['away'])}
            byes = sorted(codes[t] for t in TEAMS if t not in playing)
            self.assertEqual(int(row[1]), sum(g['week'] == week for g in self.games))
            self.assertEqual(row[2].strip(), ', '.join(byes) or '—')


if __name__ == '__main__':
    unittest.main()
