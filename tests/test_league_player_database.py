"""Research database safety: identity, uncertainty, gates and non-destructive rebuilds."""
import copy
import gzip
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.research import build_league_player_database as db


class LeaguePlayerDatabaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot=json.loads(gzip.decompress((db.ROOT/db.REL/'source_snapshot.json.gz').read_bytes()))
        cls.built=db.build(cls.snapshot,db.ROOT)
        cls.players={p['player_id']:p for p in cls.built['players']}

    def test_control_covers_reserve_retired_and_practice_squad(self):
        control=[p for p in self.players.values() if p['assignment']=='jacksonville_control']
        self.assertEqual(len(control),61)
        self.assertEqual(sum(p['branch_status']=='Practice squad' for p in control),8)
        meester=next(p for p in control if p['name']=='Brad Meester')
        self.assertEqual(meester['branch_status'],'Reserve/Retired')
        self.assertTrue(all(p['inventory_club']=='JAX' and not p['free_agency']['candidate'] for p in control))

    def test_same_name_players_and_existing_swaps_stay_separate(self):
        self.assertEqual(self.players['00-0024334']['inventory_club'],'CHI')
        self.assertIsNone(self.players['00-0029620']['inventory_club'])
        self.assertEqual(self.players['00-0029620']['assignment'],'unplaced_branch_claim')
        harris=next(p for p in self.players.values() if p['name']=='Jeremy Harris')
        self.assertEqual((harris['inventory_club'],harris['assignment']),('KC','existing_branch_placement'))
        gabbert=next(p for p in self.players.values() if p['name']=='Blaine Gabbert')
        self.assertEqual(gabbert['inventory_club'],'GB')

    def test_real_jaguars_only_players_never_gain_branch_membership(self):
        rows=[p for p in self.players.values() if p['assignment']=='real_jaguars_only']
        self.assertTrue(rows)
        self.assertTrue(all(p['inventory_club'] is None and not p['free_agency']['candidate'] for p in rows))

    def test_every_roster_identity_is_retained_and_invalid_row_quarantined(self):
        self.assertTrue({r['gsis_id'] for r in self.snapshot['rosters']} <= self.players.keys())
        self.assertNotIn('',self.players)
        self.assertNotIn('Dick Conn',{p['name'] for p in self.players.values()})
        self.assertTrue(any(r['name']=='Dick Conn' for r in self.snapshot['quarantine']))
        self.assertTrue(any(p['last_observed_week'] is None for p in self.players.values()))

    def test_manual_targets_override_heuristics(self):
        targets=[p for p in self.players.values() if p['free_agency']['evidence']=='verified_two_pass']
        self.assertEqual(len(targets),9)
        self.assertEqual(next(p for p in targets if p['name']=='Andrew Hawkins')['free_agency']['category'],'RFA')
        self.assertTrue(any(p['name']=='Golden Tate' and p['source_club']=='SEA' for p in targets))
        self.assertFalse(any(p['name']=='Ben Tate' for p in targets))

    def test_future_contract_and_draft_inputs_fail_closed(self):
        for table,field in [('contracts','year_signed'),('draft_picks','season')]:
            snapshot=copy.deepcopy(self.snapshot)
            snapshot[table][0][field]='2014'
            with self.subTest(table=table),self.assertRaises(ValueError):db.build(snapshot,db.ROOT)
        snapshot=copy.deepcopy(self.snapshot);snapshot['as_of']='2014-03-11'
        with self.assertRaises(ValueError):db.build(snapshot,db.ROOT)

    def test_invalid_contract_year_and_duplicate_identity_fail_closed(self):
        snapshot=copy.deepcopy(self.snapshot);snapshot['contracts'][0]['year_signed']='0'
        with self.assertRaises(ValueError):db.build(snapshot,db.ROOT)
        snapshot=copy.deepcopy(self.snapshot);snapshot['players'].append(snapshot['players'][0])
        with self.assertRaises(ValueError):db.build(snapshot,db.ROOT)

    def test_contracts_do_not_fall_back_to_other_clubs_or_names(self):
        p={'otc_id':'1'}
        contract={'otc_id':'1','team':'Titans','year_signed':'2013','years':'2','player_page':'https://example.test/1'}
        self.assertEqual(db.contract_for(p,'NE',[contract])['evidence'],'no_matching_club_contract')
        self.assertEqual(db.contract_for({'otc_id':'2'},'TEN',[contract])['evidence'],'no_pre_2014_contract')
        other={**contract,'years':'1'}
        self.assertEqual(db.contract_for(p,'TEN',[contract,other])['evidence'],'ambiguous_same_year_terms')
        stale={**contract,'year_signed':'2010','years':'2'}
        self.assertEqual(db.contract_for(p,'TEN',[stale])['evidence'],'stale_contract')
        self.assertIsNone(db.contract_for(p,None,[contract])['end'])
        self.assertEqual(db.contract_clubs('TB/NE'),{'TB','NE'})

    def test_sourced_extensions_remove_false_expiry_candidates(self):
        for name,end in [('Ben Roethlisberger',2015),('Rob Gronkowski',2019)]:
            p=next(p for p in self.players.values() if p['name']==name)
            self.assertEqual(p['contract']['end'],end)
            self.assertEqual(p['contract']['evidence'],'sourced_correction')
            self.assertFalse(p['free_agency']['candidate'])

    def test_correction_dates_and_control_are_enforced(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/db.REL).mkdir(parents=True)
            shutil.copy(db.ROOT/db.REL/'free_agent_pool.md',root/db.REL/'free_agent_pool.md')
            data=json.loads((db.ROOT/db.REL/'league_corrections.json').read_text())
            patch=copy.deepcopy(next(iter(data['players'].values())))
            patch['sources'][0]['published']='2014-03-11'
            data['players']={'00-0000001':patch}
            target=root/db.REL/'league_corrections.json';target.write_text(json.dumps(data))
            with self.assertRaises(ValueError):db.corrections(root)
            patch['sources'][0]['published']='2013-01-01'
            pid=next(iter(self.snapshot['branch']['control']))
            data['players']={pid:patch};target.write_text(json.dumps(data))
            with self.assertRaises(ValueError):db.build(self.snapshot,root)

    def test_ambiguous_latest_team_is_not_decided_by_row_order(self):
        snapshot=copy.deepcopy(self.snapshot)
        pid=next(p['player_id'] for p in self.players.values() if p['assignment']=='historical_observation_only' and p['source_club']=='ATL' and p['last_observed_week']==17)
        obs=next(r for r in snapshot['rosters'] if r['gsis_id']==pid and r['week']==17)
        snapshot['rosters'].append({**obs,'team':'BUF'})
        player=next(p for p in db.build(snapshot,db.ROOT)['players'] if p['player_id']==pid)
        self.assertIsNone(player['inventory_club'])
        self.assertIn('ambiguous_latest_club',player['issues'])

    def test_snapshot_has_no_future_outcomes_or_current_player_status(self):
        for p in self.snapshot['players']:
            self.assertFalse({'last_season','latest_team','status','years_of_experience'} & p.keys())
        for p in self.snapshot['draft_picks']:
            self.assertLessEqual(int(p['season']),2013)
            self.assertFalse({'hof','games','car_av','probowls','allpro'} & p.keys())
        for p in self.snapshot['contracts']:
            self.assertFalse({'is_active','season_history','value','apy'} & p.keys())
        gronk=next(p for p in self.snapshot['players'] if p['display_name']=='Rob Gronkowski')
        self.assertTrue(all('TB' not in db.contract_clubs(c['team']) for c in self.snapshot['contracts'] if c['otc_id']==gronk['otc_id']))

    def test_estimated_service_never_becomes_verified_accrued_seasons(self):
        self.assertEqual([db.estimated_category(x) for x in [None,0,1,2,3,10]], [None,'ERFA','ERFA','RFA','UFA','UFA'])
        self.assertTrue(all(p['accrued_seasons_verified'] is None for p in self.players.values()))
        for p in self.players.values():
            if p['free_agency']['evidence']=='experience_estimate':
                self.assertEqual(p['contract']['end'],2013)
                self.assertNotEqual(p['inventory_club'],'JAX')

    def test_regeneration_matches_committed_outputs(self):
        for path,text in db.render(self.built,self.snapshot,db.ROOT).items():
            self.assertEqual((db.ROOT/path).read_text(),text,str(path))

    def test_manual_source_and_rails_notes_survive_rebuild(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);shutil.copytree(db.ROOT/db.REL,root/db.REL)
            club=root/db.REL/'clubs/PHI.md';original=club.read_text()
            club.write_text('Owner note before the generated block.\n'+original+'\nDated source note after the rails table.\n')
            pool=root/db.REL/'free_agent_pool.md';old_pool=pool.read_text()
            pool.write_text(old_pool+'\nManual source follow-up.\n')
            outputs=db.render(self.built,self.snapshot,root)
            self.assertTrue(outputs[db.REL/'clubs/PHI.md'].startswith('Owner note'))
            self.assertTrue(outputs[db.REL/'clubs/PHI.md'].endswith('Dated source note after the rails table.\n'))
            self.assertTrue(outputs[db.REL/'free_agent_pool.md'].endswith('Manual source follow-up.\n'))
            self.assertEqual(db.manual_pool(outputs[db.REL/'free_agent_pool.md']),db.manual_pool(old_pool))
            self.assertNotIn(db.REL/'retirements.md',outputs)
            self.assertFalse(any(str(p).startswith(('state/','foundation/')) for p in outputs))


if __name__=='__main__':unittest.main()
