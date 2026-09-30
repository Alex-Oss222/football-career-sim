"""Actual filesystem staging: preserve prior evidence and refuse unsafe rollover."""
import json
from pathlib import Path
import tempfile
import unittest

from runtime.seasons import SeasonPaths
from scripts.season_handoff import TEAM_GATES, HISTORY_GATES, check, digest, stage


class HandoffTests(unittest.TestCase):
    def baseline(self, root, year):
        folder = root / 'career' / str(year)
        folder.mkdir(parents=True,exist_ok=True)
        evidence = folder/'closed.md'
        evidence.write_text('Synthetic closed interviews and administrative evidence')
        files = {'roster':'roster.md','staff':'coaching_staff.md','depth_chart':'depth.json',
                 'player_contracts':'contracts.md','contract_status':'status.md','cap':'cap.md',
                 'development':'development.md','decisions':'decisions.md'}
        sources={}
        for key,name in files.items():
            path=folder/name
            path.write_text('{}' if name.endswith('.json') else '[Evidence](closed.md)\nUnresolved medical hold; contract persists.\n')
            sources[key]=path.relative_to(root).as_posix()
        target=root/'career'/str(year+1)
        target.mkdir(parents=True,exist_ok=True)
        (target/'calendar.md').write_text('Synthetic historical-calendar test fixture')
        return {'season':year,'next_season':year+1,'calendar_policy':'historical','status':'TEAM_CLOSED',
                'carry_forward':sources, 'source_sha256':{k:digest(root/v) for k,v in sources.items()},
                'gates':{k:{'status':'COMPLETE','evidence':[{'path':evidence.relative_to(root).as_posix(),'sha256':digest(evidence)}]}
                         for k in TEAM_GATES} | {k:{'status':'OPEN','evidence':[]} for k in HISTORY_GATES}}

    def test_2015_and_2016_stage_without_copying_stats_or_mutating_prior_canon(self):
        for year in (2014,2015):
            with self.subTest(year=year), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);data=self.baseline(root,year)
                prior=root/'career'/str(year)/'stats/game_receipts/old.json'
                prior.parent.mkdir(parents=True);prior.write_text('{"points": 17}')
                before={p:p.read_bytes() for p in root.rglob('*') if p.is_file()}
                first=stage(root,data)
                self.assertEqual(first,stage(root,data))
                for p,blob in before.items():self.assertEqual(p.read_bytes(),blob)
                nxt=root/'career'/str(year+1)
                self.assertEqual(list(SeasonPaths(year+1, root).receipts.glob('*.json')),[])
                self.assertIn(f'/{year}/closed.md',SeasonPaths(year+1, root).roster.read_text())
                self.assertIn('Unresolved medical hold',SeasonPaths(year+1, root).roster.read_text())
                self.assertFalse(SeasonPaths(year+1, root).depth_chart.exists())
                self.assertEqual(json.loads((nxt/'opening_handoff.json').read_text())['status'],'STAGED')

    def test_open_interviews_or_changed_contracts_block_all_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);data=self.baseline(root,2014)
            data['gates']['exit_interviews']['status']='OPEN'
            with self.assertRaisesRegex(ValueError,'exit_interviews'):stage(root,data)
            data['gates']['exit_interviews']['status']='COMPLETE'
            (root/data['carry_forward']['player_contracts']).write_text('Changed contract')
            with self.assertRaisesRegex(ValueError,'not frozen/reviewed'):stage(root,data)
            self.assertFalse(SeasonPaths(2015, root).roster.exists())

    def test_existing_successor_file_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);data=self.baseline(root,2014)
            target=SeasonPaths(2015, root).roster;target.parent.mkdir(parents=True);target.write_text('User work')
            with self.assertRaisesRegex(ValueError,'Existing successor file differs'):stage(root,data)
            self.assertEqual(target.read_text(),'User work')
            self.assertFalse((target.parent/'coaching_staff.md').exists())

    def test_missing_calendar_unreviewed_evidence_and_path_escape_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);data=self.baseline(root,2014)
            (root/'career/2015/calendar.md').unlink()
            with self.assertRaisesRegex(ValueError,'historical successor calendar'):stage(root,data)
            data['gates']['exit_interviews']['evidence']=[]
            self.assertIn('Completed gate lacks evidence: exit_interviews',check(root,data))
            data['carry_forward']['roster']='../../outside.md'
            with self.assertRaisesRegex(ValueError,'leaves repository'):check(root,data)

    def test_player_career_rows_survive_and_changed_cards_block_rollover(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);data=self.baseline(root,2014)
            cards=SeasonPaths(2014,root).record('player_profiles')
            cards.mkdir(parents=True)
            (cards/'README.md').write_text('# Player cards\n')
            card=cards/'sample.md'
            from scripts.update_player_cards import stats_block, refresh_cards
            empty={'players':{},'fields':{},'games':0,'through':0,'complete':True}
            block=stats_block(2013,'Sample','QB',{False:empty,True:empty},root=root)
            block=stats_block(2014,'Sample','QB',{False:empty,True:empty},old=block,root=root)
            rows=[line for line in block.splitlines() if line.startswith(('| 2013 |','| 2014 |'))]
            card.write_text('# Sample — 2014 Player Profile\n\n**Season:** 2014\n**Position:** QB\n\n'+block)
            data['carry_forward']['player_cards']=cards.relative_to(root).as_posix()
            data['source_sha256']['player_cards']=digest(cards)
            before=card.read_bytes()
            stage(root,data)
            carried=SeasonPaths(2015,root).record('player_profiles/sample.md').read_text()
            for row in rows:self.assertIn(row,carried)
            self.assertIn('**Season:** 2015',carried)
            self.assertEqual(carried.count('| 2015 |'),2)
            self.assertEqual(refresh_cards(2015,root,check=True),[])
            self.assertEqual(card.read_bytes(),before)
            self.assertFalse(list(SeasonPaths(2015,root).receipts.glob('*.json')))
            self.assertTrue((root/'career/2015/finances/README.md').exists())
            card.write_text(card.read_text()+'Changed assessment\n')
            with self.assertRaisesRegex(ValueError,'not frozen/reviewed: player_cards'):
                stage(root,data)


if __name__=='__main__':unittest.main()
