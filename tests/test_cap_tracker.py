import copy
import json
import unittest

from scripts.render_jaguars_cap_tracker import (
    INPUT, ROOT, exact_amount, md_rows, team_accounting, totals, validate,
)


class CapTrackerTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / INPUT).read_text())

    def player(self, name):
        return next(p for p in self.data['players'] if p['name'] == name)

    def test_future_charges_follow_executed_contracts_not_waived_bray_deal(self):
        draft = md_rows((ROOT / 'career/2013/offseason/draft/draftees.md').read_text())
        surviving = [row for row in draft if len(row) == 9 and row[0].startswith('#') and row[1] != 'Tyler Bray']
        expected_2015 = sum(exact_amount(row[6]) for row in surviving) + 4 * 585000
        expected_2016 = sum(exact_amount(row[7]) for row in surviving)
        names={row[1] for row in surviving} | {'A.J. Bouye','Adam Thielen','Brynden Trawick','C.J. Anderson'}
        rookies=[p for p in self.data['players'] if p['name'] in names]
        self.assertEqual(totals(rookies, ['2015', '2016']), [expected_2015, expected_2016])
        self.assertEqual(self.player('Tyler Bray')['years']['2015']['status'], 'term_unknown')
        self.assertIsNone(self.player('Tyler Bray')['years']['2015']['cap'])

    def test_tender_and_options_are_not_double_counted_as_signed_contracts(self):
        before=totals(self.data['players'], ['2014'])
        self.player('Eugene Monroe')['years']['2014']['cap']+=1
        self.assertEqual(totals(self.data['players'], ['2014']), before)
        self.player('Eugene Monroe')['years']['2014']['cap']-=1
        self.assertEqual(totals(self.data['players'], ['2014'], status='tender'), [11654000])
        self.assertEqual(self.player('Justin Blackmon')['years']['2016']['status'], 'option_unexercised')
        self.assertEqual(self.player('Lane Johnson')['years']['2017']['status'], 'option_unexercised')
        self.assertEqual(totals(self.data['players'], ['2017']), [0])

    def test_unknown_cannot_be_replaced_with_zero(self):
        self.player('John Parker Wilson')['years']['2014']['cap'] = 0
        with self.assertRaisesRegex(ValueError, 'must not be numeric'):
            validate(self.data)

    def test_duplicate_player_cannot_double_count(self):
        self.data['players'].append(copy.deepcopy(self.data['players'][0]))
        with self.assertRaisesRegex(ValueError, 'Duplicate player'):
            validate(self.data)

    def test_former_player_history_is_retained_outside_current_roster(self):
        # A synthetic former-player row tests preservation, not a branch move.
        former = copy.deepcopy(self.player('Roy Miller'))
        former.update(name='Synthetic former player', former_player=True,
                      departure_date=self.data['as_of'],
                      departure_source=self.data['current_contract_table'])
        before = totals(self.data['players'], ['2014'])[0]
        self.data['players'].append(former)
        validate(self.data)
        self.assertEqual(totals(self.data['players'], ['2014'])[0],
                         before + former['years']['2014']['cap'])
        former['departure_date'] = '2014-03-01'
        with self.assertRaisesRegex(ValueError, 'future departure'):
            validate(self.data)

    def test_cap_room_is_withheld_until_accounting_is_complete(self):
        book = self.data['team_years']['2014']
        book.update(carryover=0, net_adjustments=0, counted_team_salary=120000000,
                    sources=['synthetic test input, not repository accounting'])
        self.assertIsNone(team_accounting(self.data, '2014')['room'])
        book['accounting_reconciled'] = True
        with self.assertRaisesRegex(ValueError, 'unresolved player obligations'):
            validate(self.data)

    def test_signed_adjustment_is_applied_once(self):
        # Synthetic arithmetic only, not a Jacksonville cap-space assertion.
        book = self.data['team_years']['2014']
        book.update(carryover=2000000, net_adjustments=-500000,
                    counted_team_salary=120000000, rookie_incremental_reserve=1000000,
                    accounting_reconciled=True)
        self.assertEqual(team_accounting(self.data, '2014'), {
            'adjusted': 134500000, 'room': 14500000, 'after_rookies': 13500000,
        })

    def test_present_dataset_matches_roster_and_current_contract_table(self):
        self.assertEqual(validate(self.data), [str(y) for y in range(2014, 2024)])

    def test_original_contracts_survive_without_later_real_restructures(self):
        self.assertEqual(self.player('Kirk Cousins')['years']['2014']['cap'], 570000)
        self.assertEqual(self.player('Kirk Cousins')['years']['2015']['proration'], 0)
        self.assertEqual(self.player('Marcedes Lewis')['years']['2015']['base'], 6650000)
        pos=self.player('Paul Posluszny')['years']
        self.assertEqual([pos[y]['proration'] for y in ['2014','2015','2016']], [2000000,2000000,0])
        self.assertEqual(pos['2016']['cap'], 7500000)

    def test_deferred_blackmon_cash_is_not_charged_twice_to_cap(self):
        row=self.player('Justin Blackmon')['years']['2014']
        self.assertEqual(row['cash']-row['base'], 1700000)
        self.assertEqual(row['approximate_cap'], row['base']+row['proration'])
        self.assertEqual(row['status'], 'approximate')

    def test_every_signed_2014_deal_is_priced_and_estimates_stay_separate(self):
        current=[p for p in self.data['players'] if p['control'] in {'signed','future'}]
        self.assertEqual(len(current),42)
        self.assertTrue(all(p['years']['2014']['status'] in {'known','approximate'} for p in current))
        before=totals(current,['2014'])
        row=self.player('Montell Owens')['years']['2014']
        row['approximate_cap']+=1000
        self.assertEqual(totals(current,['2014']),before)
        with self.assertRaisesRegex(ValueError,'Estimated cap components disagree'):
            validate(self.data)

    def test_credited_service_uses_branch_practice_squad_history(self):
        expected={'Richard Murphy':495000, 'Jerrell Jackson':420000, 'Jerome Long':420000,
                  "D'Anthony Smith":495000, 'Antwon Blake':495000}
        for name,salary in expected.items():
            self.assertEqual(self.player(name)['years']['2014']['cap'],salary)
        self.assertEqual(totals(self.data['players'],['2014'],field='planning_allowance',status='term_unknown'),[1300000])

    def test_estimated_current_charge_must_match_the_owner_table(self):
        row=self.player('Uche Nwaneri')['years']['2014']
        row['base']+=1000
        row['approximate_cap']+=1000
        with self.assertRaisesRegex(ValueError,'Current estimate differs'):
            validate(self.data)


if __name__ == '__main__':
    unittest.main()
