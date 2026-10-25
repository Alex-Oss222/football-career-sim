import copy
from datetime import date, timedelta
import json
import re
import tempfile
import unittest

from scripts.render_jaguars_cap_tracker import (
    INPUT, ROOT, cap_cell, dollars, exact_amount, md_rows, organization_staff, reader_words, render,
    release_exposure, render_main, team_accounting, totals, validate, working_charge, working_total,
)

# The contract records after the September 8, 2014 transactions (tests/test_player_contracts.py
# CONVERTED_ON). The dated figures and named contracts below are read as they stood that day, so a
# later signing, release, promotion, trade or reserve move never changes them.
PINNED = date(2014, 9, 8)


def amount(page, label):
    """The dollar figure of a two-column ``| label | $n |`` row (negative when shown -$n)."""
    found = re.search(r'^\| ' + re.escape(label) + r' \| (-?)\$([\d,]+) \|', page, re.M)
    return int(found.group(2).replace(',', '')) * (-1 if found.group(1) else 1)


class CapTrackerTests(unittest.TestCase):
    def setUp(self):
        # The club-level contract inputs with the player rows and their date from the contract
        # records, as the inputs held them before the records became their one owner (render reads
        # the records itself, so it is given the inputs alone).
        from runtime import player_contracts
        self.data = json.loads((ROOT / INPUT).read_text())
        self.data['players'] = player_contracts.rows(ROOT)
        self.data['as_of'] = player_contracts.as_of(ROOT)
        # The same inputs with the rows and date of PINNED. validate() compares the rows with the
        # live roster record last, so it runs on these only where it must fail before that check.
        self.dated = copy.deepcopy(self.data)
        self.dated['players'] = player_contracts.rows(ROOT, on=PINNED)
        self.dated['as_of'] = player_contracts.as_of(ROOT, on=PINNED)

    def player(self, name, data=None):
        return next(p for p in (data or self.data)['players'] if p['name'] == name)

    def dated_main(self):
        # The cap table as the records stood on PINNED. render() is not given the day: its validate()
        # compares the dated rows with the live roster record, which every later move changes.
        from runtime import player_contracts
        dated = player_contracts.tracker_inputs(self.data, ROOT, PINNED)
        return reader_words(render_main(dated, player_contracts.horizon(dated)))

    def test_future_charges_follow_executed_contracts_not_waived_bray_deal(self):
        draft = md_rows((ROOT / 'career/2013/offseason/draft/draftees.md').read_text())
        surviving = [row for row in draft if len(row) == 9 and row[0].startswith('#') and row[1] not in ('Tyler Bray', 'Lavar Edwards')]  # both waived at the August 30, 2014 reduction
        expected_2015 = sum(exact_amount(row[6]) for row in surviving) + 4 * 585000
        expected_2016 = sum(exact_amount(row[7]) for row in surviving)
        names={row[1] for row in surviving} | {'A.J. Bouye','Adam Thielen','Brynden Trawick','C.J. Anderson'}
        # The contracts as they stood on PINNED: a later release of one of these players ends his charges.
        rookies=[p for p in self.dated['players'] if p['name'] in names]
        self.assertEqual(totals(rookies, ['2015', '2016']), [expected_2015, expected_2016])
        # Bray's reserve/future deal ended with the August 30, 2014 waiver; his
        # practice-squad contract (August 31) is weekly and ends with 2014.
        bray=self.player('Tyler Bray',self.dated)
        self.assertEqual(working_charge(bray['years']['2014']), 107100)
        self.assertEqual(bray['contract_ends'], 2014)
        self.assertIsNone(working_charge(bray['years']['2015']))
        self.assertIsNone(working_charge(bray['years']['2016']))

    def test_tender_and_options_are_not_double_counted_as_signed_contracts(self):
        # The four qualifying offers were withdrawn August 30, 2014; a withdrawn
        # tender is a former-player row with no charge, counted nowhere.
        self.assertEqual(totals(self.data['players'], ['2014'], status='tender'), [0])
        # The rows as they stood on PINNED: a later signing, release or option decision never moves these.
        bradfield = self.player('Cameron Bradfield', self.dated)
        self.assertTrue(bradfield.get('former_player'))
        self.assertTrue(all(r['status'] == 'not_committed' for r in bradfield['years'].values()))
        self.assertEqual(self.player('Justin Blackmon', self.dated)['years']['2016']['status'], 'option_unexercised')
        self.assertEqual(self.player('Lane Johnson', self.dated)['years']['2017']['status'], 'option_unexercised')
        self.assertEqual(totals(self.dated['players'], ['2017']), [47836771])  # replay contracts plus the 2014 rookie contracts, less Jemea Thomas (waived August 30, 2014)

    def test_model_cannot_be_silently_reclassified_as_historical(self):
        # His row as it stood on PINNED (waived August 30, 2014), so a later re-signing never changes it.
        self.player('John Parker Wilson', self.dated)['years']['2014']['cap'] = 0
        with self.assertRaisesRegex(ValueError, 'must not be numeric'):
            validate(self.dated)

    def test_duplicate_player_cannot_double_count(self):
        self.data['players'].append(copy.deepcopy(self.data['players'][0]))
        with self.assertRaisesRegex(ValueError, 'Duplicate player'):
            validate(self.data)

    def test_former_player_history_is_retained_outside_current_roster(self):
        # A synthetic former-player row tests preservation, not a branch move. It copies Roy Miller's
        # contract as it stood on PINNED, which a later move of his never changes.
        former = copy.deepcopy(self.player('Roy Miller', self.dated))
        former.update(name='Synthetic former player', former_player=True,
                      departure_date=self.data['as_of'],
                      departure_source=self.data['current_contract_table'])
        before = totals(self.data['players'], ['2014'])[0]
        self.data['players'].append(former)
        validate(self.data)
        self.assertEqual(totals(self.data['players'], ['2014'])[0],
                         before + former['years']['2014']['cap'])
        # A day after the records' latest entry is a future departure whatever that date is.
        former['departure_date'] = (date.fromisoformat(self.data['as_of']) + timedelta(days=1)).isoformat()
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
        main = next(value for path, value in outputs.items() if path.name == 'cap_tracker.md')
        self.assertIn('Unused prior-year room carried in | $5,330,000 to $6,000,000', main)
        self.assertIn('Adjusted team cap | Unresolved', main)
        estimate = self.data['team_years']['2014']['carryover_working_estimate']
        # The live dashboard keeps the rollover apart: the before-rollover difference plus each end of the range.
        before = amount(main, 'Difference below league cap, before club adjustments and reserves')
        self.assertIn('Difference including the rollover estimate | %s to %s'
                      % (dollars(before + estimate['low']), dollars(before + estimate['high'])), main)
        self.assertIn('Difference including the rollover estimate | $15,876,308 to $16,546,308', self.dated_main())  # the generator's standing Top-51 dashboard on PINNED; the full count applies from September 3 (cap worksheet)
        estimate['low'], estimate['high'] = estimate['high'], estimate['low']
        with self.assertRaisesRegex(ValueError, 'Carryover working estimate'):
            validate(self.data)

    def test_present_dataset_matches_roster(self):
        self.assertEqual(validate(self.data), [str(y) for y in range(2014, 2026)])

    def test_readable_horizon_and_separate_organization_payroll(self):
        outputs=render(self.data)
        main=next(value for path,value in outputs.items() if path.name=='cap_tracker.md')
        organization=next(value for path,value in outputs.items() if path.name=='coaching_payroll.md')
        self.assertIn('**Nine-year view**',main)
        self.assertIn('**Additional three years**',main)
        dated=self.dated_main()
        self.assertIn('| Working counted total | $122,453,692 |',dated)  # the generator's Top-51 dashboard after the September 8 transactions
        self.assertIn('| Difference below league cap, before club adjustments and reserves | $10,546,308 |',dated)
        # The live dashboard's counted total and its difference make up the league cap.
        self.assertEqual(amount(main,'Working counted total')
                         +amount(main,'Difference below league cap, before club adjustments and reserves'),
                         self.data['league_caps']['2014'])
        self.assertIn('Certified cap space | Unresolved',main)
        self.assertNotRegex(main,r'^##+ \d+\.',)
        self.assertNotIn('Release comparisons',main)
        # The assistants' payroll in the coach records as they stood on PINNED (a copy without the later
        # entries, so a later hire, departure or amendment never moves it); the live page shows the
        # assistants' payroll of the live records.
        from runtime import coaches
        from runtime.player_bios import master_date
        years=[str(y) for y in range(self.data['start_year'],self.data['end_year']+1)]
        assistants=lambda root,on: [sum(s.get(y,0) for _,t,s in organization_staff(root,years,on) if t.get('job')!='Head coach')
                                    for y in ('2014','2015')]
        with tempfile.TemporaryDirectory() as tmp:
            coaches.folder(tmp).mkdir(parents=True)
            for slug,record in coaches.load_all(ROOT).items():
                record['entries']=[e for e in record['entries'] if coaches.day(coaches.when(e))<=PINNED]
                (coaches.folder(tmp)/('%s.json' % slug)).write_text(coaches.dump(record),encoding='utf-8')
            self.assertEqual(assistants(tmp,PINNED),[7700000,3650000])
        self.assertIn('| Assistant coaches | %s | %s |' % tuple(dollars(v) if v else '' for v in assistants(ROOT,master_date(ROOT))),
                      organization)
        # Every coach's salary comes from his permanent record; the head coach's is the reconstructed term.
        stone=coaches.current_contract(coaches.load('alex_stone',ROOT))
        self.assertIn('Alex Stone | Head coach | $%s' % format(stone['salary']['2014'],','),organization)
        self.assertNotIn('Unspecified',organization)
        self.assertNotIn('Alex Stone',main)

    def test_render_uses_current_sources_without_changing_frozen_financial_inputs(self):
        original = copy.deepcopy(self.data)
        outputs = render(self.data)
        self.assertEqual(self.data, original)
        for path, text in outputs.items():
            self.assertNotRegex(text, r'\bEntr(?:y|ies) \d+')
            self.assertNotIn('ledger.md', text)
            self.assertNotIn('Update the event ledger', text)
            for target in re.findall(r'\]\(([^)]+)\)', text):
                if target.startswith(('https:', 'http:', '#')):
                    continue
                self.assertTrue((ROOT / path.parent / target.split('#')[0]).is_file(),
                                (path, target))
        details = outputs[next(path for path in outputs if path.name == 'contract_details.md')]
        self.assertIn('departure March 31, 2014', details)
        self.assertIn('Trades/completed_trades/trades.md', details)
        self.assertIn('[adopted contract reconstruction]', details)
        self.assertIn('$2,072,910', details)
        self.assertIn('without an additional bonus-recovery credit', details)

    def test_signed_draft_class_and_traded_players_are_not_shown_as_pending(self):
        outputs=render(self.data)
        main=next(value for path,value in outputs.items() if path.name=='cap_tracker.md')
        details=next(value for path,value in outputs.items() if path.name=='contract_details.md')
        self.assertIn('| Aaron Donald, DT, Pittsburgh | May 8, 2014 | Signed May 11, 2014 |',main)
        self.assertNotIn('These are selection rights',main)
        self.assertNotIn('Review the exercise decision in the 2015 option window',details)
        self.assertIn('Aaron Donald and Joel Bitonio | 2018 fifth-year options remain unexercised',main)
        for name in ['Uche Nwaneri','Jason Babin','Justin Blackmon']:
            self.assertNotIn(name, main.split('## Decision calendar')[1].split('## Expiring')[0])

    def test_original_contracts_survive_without_later_real_restructures(self):
        # Each contract as it stood on PINNED, and as the records stand now while that contract continues
        # (a later amendment keeps the contract and would show here; a trade or release ends it).
        from runtime import player_contracts
        records={r['name']:r for r in player_contracts.load_all(ROOT).values()}
        def views(name):
            then,now=(player_contracts.contract_on(records[name],on) for on in (PINNED,None))
            return [self.player(name,self.dated)]+([self.player(name)] if now and now['contract']==then['contract'] else [])
        for cousins in views('Kirk Cousins'):
            self.assertEqual(cousins['years']['2014']['cap'], 570000)
            self.assertEqual(cousins['years']['2015']['proration'], 0)
        for lewis in views('Marcedes Lewis'):
            self.assertEqual(lewis['years']['2015']['base'], 6650000)
        for posluszny in views('Paul Posluszny'):
            pos=posluszny['years']
            self.assertEqual([pos[y]['proration'] for y in ['2014','2015','2016']], [2000000,2000000,0])
            self.assertEqual(pos['2016']['cap'], 7500000)

    def test_traded_blackmon_leaves_only_accelerated_bonus_as_dead_money(self):
        # Traded to Indianapolis March 31, 2014 (Entry 104): the deferred cash left with
        # the contract; only the 2014 and 2015 bonus allocations stay, once, as dead money.
        p=self.player('Justin Blackmon')
        self.assertTrue(p.get('former_player'))
        self.assertEqual([p['years'][y]['status'] for y in ['2014','2015']], ['not_committed','not_committed'])
        from runtime import player_contracts
        dead=[d['amount'] for d in player_contracts.dead_money(ROOT) if d['player']=='Justin Blackmon']
        self.assertEqual(dead, [2*2975818])
        # The charge lives on his contract record's trade ending, not in the inputs' club-level rows.
        self.assertNotIn('Justin Blackmon', [d['player'] for d in self.data['dead_money']])

    def test_every_signed_2014_deal_is_priced_and_estimates_stay_separate(self):
        from runtime import roster as roster_record
        from scripts.render_jaguars_cap_tracker import source_path
        current=[p for p in self.data['players'] if p['control'] in {'signed','future'}]
        # Exactly the players the roster record lists (the active roster, the reserve lists and the practice
        # squad), less any unsigned tender, hold a signed contract: the two records change in one commit.
        listed={r['name'] for r in roster_record.load(source_path(self.data['current_roster'],ROOT))['players']}
        tendered={p['name'] for p in self.data['players'] if p['control']=='tender' and not p.get('former_player')}
        self.assertEqual({p['name'] for p in current},listed-tendered)
        self.assertTrue(all(p['years']['2014']['status'] in {'known','approximate'} for p in current))
        # On PINNED, with Montell Owens's estimate as it stood then (validate fails before its roster check).
        dated=[p for p in self.dated['players'] if p['control'] in {'signed','future'}]
        self.assertEqual(len(dated),64)  # the active 53 and the four on reserve/injured after the September 8, 2014 transactions, plus the seven practice-squad contracts remaining from August 31
        self.assertTrue(all(p['years']['2014']['status'] in {'known','approximate'} for p in dated))
        before=totals(dated,['2014'])
        row=self.player('Montell Owens',self.dated)['years']['2014']
        row['approximate_cap']+=1000
        self.assertEqual(totals(dated,['2014']),before)
        with self.assertRaisesRegex(ValueError,'Estimated cap components disagree'):
            validate(self.dated)

    def test_credited_service_uses_branch_practice_squad_history(self):
        # Jackson's reserve/future minimum continues on reserve/injured; the
        # other five futures ended with the August 30, 2014 waivers (Murphy and
        # Long returned on weekly practice-squad contracts, a 17-week estimate). The contracts as they
        # stood on PINNED: a later promotion, release or signing never changes these.
        expected={'Jerrell Jackson':420000}
        for name,salary in expected.items():
            self.assertEqual(self.player(name,self.dated)['years']['2014']['cap'],salary)
        for name in ('Richard Murphy','Jerome Long'):
            self.assertEqual(working_charge(self.player(name,self.dated)['years']['2014']),107100)
        for name in ("D'Anthony Smith",'Antwon Blake','John Parker Wilson'):
            self.assertTrue(self.player(name,self.dated).get('former_player'))
            self.assertIsNone(working_charge(self.player(name,self.dated)['years']['2014']))
        self.assertEqual(working_charge(self.player('Jonathan Grimes',self.dated)['years']['2014']),570000)
        self.assertTrue(all(r['status']!='term_unknown' for p in self.data['players'] for r in p['years'].values()))

    def test_the_views_are_built_from_the_contract_records_not_a_copy(self):
        # The contract records own the player rows (rebuild step 5); an edit to a copy of the rows
        # changes no cap view. The edited row is any estimated charge but the first row's, compared
        # below (Jeremy Mincey's while he is under contract).
        before=render(copy.deepcopy(self.data))
        row=next(p['years']['2014'] for p in self.data['players'][1:] if p['years']['2014']['status']=='approximate')
        row['base']+=1000
        row['approximate_cap']+=1000
        self.assertEqual(render(self.data), before)
        from runtime import player_contracts
        self.assertEqual(self.data['players'][0], player_contracts.rows(ROOT)[0])
        self.assertNotEqual(self.data['players'], player_contracts.rows(ROOT))

    def test_covered_years_cannot_revert_to_placeholders(self):
        # His contract as it stood on PINNED (validate fails before its roster check).
        self.player('Kirk Cousins',self.dated)['years']['2015'] = {
            'status':'unknown_amount','cap':None,'base':None,'proration':None,'cash':None,
        }
        with self.assertRaisesRegex(ValueError,'Missing covered-year charge'):
            validate(self.dated)

    def test_charges_cannot_extend_a_deal_without_changing_its_term(self):
        # His contract as it stood on PINNED (validate fails before its roster check).
        p=self.player('Jonathan Grimes',self.dated)
        p['years']['2015']=copy.deepcopy(p['years']['2014'])
        with self.assertRaisesRegex(ValueError,'Charge exceeds recorded term'):
            validate(self.dated)

    def test_blank_future_cells_currency_and_totals(self):
        from runtime import player_contracts
        outputs=render(self.data)
        main=outputs[next(path for path in outputs if path.name=='cap_tracker.md')]
        self.assertNotIn('Unknown',main)
        self.assertNotIn('Term unknown',main)
        self.assertNotIn('Not committed',main)
        # The live table shows each deal's covered years in currency and its other years blank, and
        # counts each player contract and each dead-money charge once.
        cousins=self.player('Kirk Cousins')['years']
        self.assertIn(' | '.join(cap_cell(cousins[str(y)]) for y in range(2014,2018))+' |',main)
        dead=sum(x['amount'] for x in player_contracts.dead_money(ROOT) if str(x['year'])=='2014')
        self.assertIn('| Recorded cap obligations | %s |' % dollars(working_total(self.data['players'],'2014')+dead),main)
        # The table and charges as the records stood on PINNED, after the September 8, 2014 transactions.
        dated=self.dated_main()
        self.assertIn('$570,000 | $660,000 |  |  |',dated)
        self.assertEqual(cap_cell(self.player('Lane Johnson',self.dated)['years']['2017']), '')
        self.assertEqual(cap_cell(self.player('Brent Grimes',self.dated)['years']['2014']), '')
        self.assertEqual(working_charge(self.player('Alan Ball',self.dated)['years']['2014']), 804706)  # signed September 8, 2014: the $855,000 rate for sixteen of seventeen pay weeks
        self.assertEqual([working_total(self.dated['players'],str(y)) for y in [2014,2015,2016,2017]],
                         [114607730,115430972,79764658,47836771])  # after the September 8, 2014 transactions (Ball signed, Phillips promoted on a three-year contract)
        self.assertIn('$125,194,686',dated)  # Old Bray bonus and the August 30 dead money are included once.

    def test_slot_guarantees_and_release_exposure_reconcile(self):
        # The rookie-slot contracts as they stood on PINNED (validate fails before its roster check).
        lane=self.player('Lane Johnson',self.dated);kelce=self.player('Travis Kelce',self.dated)
        self.assertEqual(lane['remaining_guarantees'],6997254)
        self.assertEqual(kelce['remaining_guarantees'],1153596)
        self.assertEqual(release_exposure(kelce,'2014'),2921742)
        kelce['remaining_guarantees']+=1
        with self.assertRaisesRegex(ValueError,'Remaining guarantees disagree'):
            validate(self.dated)


if __name__ == '__main__':
    unittest.main()
