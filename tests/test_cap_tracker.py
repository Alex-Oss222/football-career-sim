import copy
import json
import unittest

from scripts.render_jaguars_cap_tracker import (
    INPUT, ROOT, cap_cell, exact_amount, md_rows, render, release_exposure,
    team_accounting, totals, validate, working_charge, working_total,
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
        self.assertEqual(working_charge(self.player('Tyler Bray')['years']['2015']), 510000)
        self.assertEqual(self.player('Tyler Bray')['contract_ends'], 2015)
        self.assertIsNone(working_charge(self.player('Tyler Bray')['years']['2016']))

    def test_tender_and_options_are_not_double_counted_as_signed_contracts(self):
        before=totals(self.data['players'], ['2014'])
        self.player('Cameron Bradfield')['years']['2014']['cap']+=1
        self.assertEqual(totals(self.data['players'], ['2014']), before)
        self.player('Cameron Bradfield')['years']['2014']['cap']-=1
        self.assertEqual(totals(self.data['players'], ['2014'], status='tender'), [3066000])
        self.assertEqual(self.player('Justin Blackmon')['years']['2016']['status'], 'option_unexercised')
        self.assertEqual(self.player('Lane Johnson')['years']['2017']['status'], 'option_unexercised')
        self.assertEqual(totals(self.data['players'], ['2017']), [48550284])  # replay contracts (Entries 95-97) plus the 2014 rookie contracts (Entry 108)

    def test_model_cannot_be_silently_reclassified_as_historical(self):
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
        former['departure_date'] = '2014-05-12'
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

    def test_rollover_estimate_is_shown_separately_and_needs_a_range_and_source(self):
        outputs = render(self.data)
        main = next(value for path, value in outputs.items() if path.name == 'jaguars_cap.md')
        self.assertIn('Unused prior-year room carried in | $5,330,000 to $6,000,000', main)
        self.assertIn('Difference including the rollover estimate | $12,440,314 to $13,110,314', main)
        self.assertIn('Adjusted team cap | Unresolved', main)
        estimate = self.data['team_years']['2014']['carryover_working_estimate']
        estimate['low'], estimate['high'] = estimate['high'], estimate['low']
        with self.assertRaisesRegex(ValueError, 'Carryover working estimate'):
            validate(self.data)

    def test_present_dataset_matches_roster_and_current_contract_table(self):
        self.assertEqual(validate(self.data), [str(y) for y in range(2014, 2026)])

    def test_readable_horizon_and_separate_organization_payroll(self):
        outputs=render(self.data)
        main=next(value for path,value in outputs.items() if path.name=='jaguars_cap.md')
        organization=next(value for path,value in outputs.items() if path.name=='organization_finances.md')
        self.assertIn('**Nine-year view**',main)
        self.assertIn('**Additional three years**',main)
        self.assertIn('$125,889,686',main)
        self.assertIn('$7,110,314',main)
        self.assertIn('Certified cap space | Unresolved',main)
        self.assertNotRegex(main,r'^##+ \d+\.',)
        self.assertNotIn('Release comparisons',main)
        self.assertIn('$7,700,000',organization)
        self.assertIn('$3,650,000',organization)
        self.assertIn('Alex Stone | Head coach | Unspecified',organization)
        self.assertNotIn('Alex Stone',main)

    def test_signed_draft_class_and_traded_players_are_not_shown_as_pending(self):
        outputs=render(self.data)
        main=next(value for path,value in outputs.items() if path.name=='jaguars_cap.md')
        details=next(value for path,value in outputs.items() if path.name=='jaguars_contract_details.md')
        self.assertIn('| Aaron Donald, DT, Pittsburgh | May 8, 2014 | Signed May 11, 2014 |',main)
        self.assertNotIn('These are selection rights',main)
        self.assertNotIn('Review the exercise decision in the 2015 option window',details)
        self.assertIn('Aaron Donald and Joel Bitonio | 2018 fifth-year options remain unexercised',main)
        for name in ['Uche Nwaneri','Jason Babin','Justin Blackmon']:
            self.assertNotIn(name, main.split('## Decision calendar')[1].split('## Expiring')[0])

    def test_original_contracts_survive_without_later_real_restructures(self):
        self.assertEqual(self.player('Kirk Cousins')['years']['2014']['cap'], 570000)
        self.assertEqual(self.player('Kirk Cousins')['years']['2015']['proration'], 0)
        self.assertEqual(self.player('Marcedes Lewis')['years']['2015']['base'], 6650000)
        pos=self.player('Paul Posluszny')['years']
        self.assertEqual([pos[y]['proration'] for y in ['2014','2015','2016']], [2000000,2000000,0])
        self.assertEqual(pos['2016']['cap'], 7500000)

    def test_traded_blackmon_leaves_only_accelerated_bonus_as_dead_money(self):
        # Traded to Indianapolis March 31, 2014 (Entry 104): the deferred cash left with
        # the contract; only the 2014 and 2015 bonus allocations stay, once, as dead money.
        p=self.player('Justin Blackmon')
        self.assertTrue(p.get('former_player'))
        self.assertEqual([p['years'][y]['status'] for y in ['2014','2015']], ['not_committed','not_committed'])
        dead=[d['amount'] for d in self.data['dead_money'] if d['player']=='Justin Blackmon']
        self.assertEqual(dead, [2*2975818])

    def test_every_signed_2014_deal_is_priced_and_estimates_stay_separate(self):
        current=[p for p in self.data['players'] if p['control'] in {'signed','future'}]
        self.assertEqual(len(current),75)  # 49 after the trades (Entry 104) plus 26 rookie contracts (Entry 108)
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
        self.assertEqual(working_charge(self.player('John Parker Wilson')['years']['2014']),730000)
        self.assertEqual(working_charge(self.player('Jonathan Grimes')['years']['2014']),570000)
        self.assertTrue(all(r['status']!='term_unknown' for p in self.data['players'] for r in p['years'].values()))

    def test_estimated_current_charge_must_match_the_owner_table(self):
        row=self.player('Jeremy Mincey')['years']['2014']
        row['base']+=1000
        row['approximate_cap']+=1000
        with self.assertRaisesRegex(ValueError,'Current charge differs'):
            validate(self.data)

    def test_covered_years_cannot_revert_to_placeholders(self):
        self.player('Kirk Cousins')['years']['2015'] = {
            'status':'unknown_amount','cap':None,'base':None,'proration':None,'cash':None,
        }
        with self.assertRaisesRegex(ValueError,'Missing covered-year charge'):
            validate(self.data)

    def test_charges_cannot_extend_a_deal_without_changing_its_term(self):
        p=self.player('John Parker Wilson')
        p['years']['2015']=copy.deepcopy(p['years']['2014'])
        with self.assertRaisesRegex(ValueError,'Charge exceeds recorded term'):
            validate(self.data)

    def test_blank_future_cells_currency_and_totals(self):
        outputs=render(self.data)
        main=outputs[next(path for path in outputs if path.name=='jaguars_cap.md')]
        self.assertNotIn('Unknown',main)
        self.assertNotIn('Term unknown',main)
        self.assertNotIn('Not committed',main)
        self.assertIn('$570,000 | $660,000 |  |  |',main)
        self.assertEqual(cap_cell(self.player('Lane Johnson')['years']['2017']), '')
        self.assertEqual(cap_cell(self.player('Alan Ball')['years']['2014']), '')
        self.assertEqual([working_total(self.data['players'],str(y)) for y in [2014,2015,2016,2017]],
                         [127183362,123275736,84131574,48550284])  # Entry 108 adds the 26 rookie contracts
        self.assertIn('$137,445,686',main)  # Old Bray bonus is included once.

    def test_slot_guarantees_and_release_exposure_reconcile(self):
        lane=self.player('Lane Johnson');kelce=self.player('Travis Kelce')
        self.assertEqual(lane['remaining_guarantees'],6997254)
        self.assertEqual(kelce['remaining_guarantees'],1153596)
        self.assertEqual(release_exposure(kelce,'2014'),2921742)
        kelce['remaining_guarantees']+=1
        with self.assertRaisesRegex(ValueError,'Remaining guarantees disagree'):
            validate(self.data)


if __name__ == '__main__':
    unittest.main()
