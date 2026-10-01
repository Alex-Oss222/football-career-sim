"""Actual filesystem staging: preserve prior evidence and refuse unsafe rollover."""
import json
import os
from pathlib import Path
import tempfile
import unittest

from runtime.seasons import SeasonPaths
from scripts.season_handoff import (
    TEAM_GATES, HISTORY_GATES, check, digest, stage, refresh_reference_inventory,
    opening_errors, opening_gate_sources, review_opening, repository_opening_errors,
)
from tests.test_annual_assessment_completion import authored_card, empty_period


class HandoffTests(unittest.TestCase):
    def baseline(self, root, year):
        return self.assessment_baseline(root, year)

    def bare_baseline(self, root, year):
        folder = root / 'career' / str(year)
        folder.mkdir(parents=True,exist_ok=True)
        evidence = folder/'closed.md'
        evidence.write_text('Synthetic closed interviews and administrative evidence')
        files = {'roster':'roster.md','staff':'coaching_staff.md','depth_chart':'depth.json',
                 'player_contracts':'contracts.md','contract_status':'status.md','cap':'cap.md',
                 'development':'development.md','decisions':'decisions.md',
                 'calendar':'calendar_source.md','record':'record_source.md','player_ages':'ages.md',
                 'player_finances':'finance.json','organization_finances':'organization.md',
                 'draft_assets':'draft_assets.json','medical_and_roles':'medical.md','checkpoint':'checkpoint.md'}
        sources={}
        for key,name in files.items():
            path=folder/name
            path.write_text('{}' if name.endswith('.json') else '[Evidence](closed.md)\nUnresolved medical hold; contract persists.\n')
            sources[key]=path.relative_to(root).as_posix()
        target=root/'career'/str(year+1)
        target.mkdir(parents=True,exist_ok=True)
        SeasonPaths(year+1, root).calendar.write_text('Synthetic historical-calendar test fixture')
        data = {'season':year,'next_season':year+1,'calendar_policy':'historical','status':'TEAM_CLOSED',
                'carry_forward':sources, 'source_sha256':{k:digest(root/v) for k,v in sources.items()},
                'gates':{k:{'status':'COMPLETE','evidence':[{'path':evidence.relative_to(root).as_posix(),'sha256':digest(evidence)}]}
                         for k in TEAM_GATES} | {k:{'status':'OPEN','evidence':[]} for k in HISTORY_GATES}}
        refresh_reference_inventory(root, data)
        for item in data['reference_inventory'].values():
            item.update(status='COMPLETE', evidence=[{'path': evidence.relative_to(root).as_posix(),
                                                     'sha256': digest(evidence)}])
        return data

    def assessment_baseline(self, root, year=2014):
        from scripts.build_annual_player_sheets import review_final_assessments
        data = self.bare_baseline(root, year)
        paths = SeasonPaths(year, root)
        paths.roster.parent.mkdir(parents=True, exist_ok=True)
        evidence_link = os.path.relpath(root/'career'/str(year)/'closed.md', paths.roster.parent)
        paths.roster.write_text('**As of:** Season close\n\n**Canonical controlled-player count:** **1**\n\n## Current controlled players\n\n| Player | Pos | Status |\n|---|---|---|\n| Sample | LS | Signed |\n\n[Evidence]('+evidence_link+')\nUnresolved medical hold; contract persists.\n')
        data['carry_forward']['roster'] = paths.roster.relative_to(root).as_posix()
        data['source_sha256']['roster'] = digest(paths.roster)
        for gate, filename in [('team_season_closed', 'season_closeout.md'),
                               ('exit_interviews', 'exit_interviews.md')]:
            path = paths.record('closeouts/'+filename)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('Completed synthetic season review and actual exit evidence.\n')
            data['gates'][gate] = {'status': 'COMPLETE', 'evidence': [
                {'path': path.relative_to(root).as_posix(), 'sha256': digest(path)}]}
        for slug, name in [('sample', 'Sample'), ('departed', 'Departed')]:
            for final in (False, True):
                path = paths.record('closeouts/player_assessments' if final else 'player_profiles')/(slug+'.md')
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(authored_card(root, year, name, path, final=final))
        for key, folder in [('player_cards', 'player_profiles'), ('final_assessments', 'closeouts/player_assessments')]:
            source = paths.record(folder)
            data['carry_forward'][key] = source.relative_to(root).as_posix()
            data['source_sha256'][key] = digest(source)
        manifest = paths.record('closeouts/season_handoff.json')
        manifest.write_text(json.dumps(data))
        review_final_assessments(year, root)
        return json.loads(manifest.read_text())

    def completed_opening(self, root):
        from scripts.update_player_cards import START, stats_block
        data = self.assessment_baseline(root)
        stage(root, data)
        path = root/'career/2015/opening_handoff.json'
        opening = json.loads(path.read_text())
        for name, sources in opening_gate_sources(root, 2015).items():
            evidence = []
            for relative in sources:
                source = root/relative
                if not source.exists():
                    source.parent.mkdir(parents=True, exist_ok=True)
                    source.write_text('{}' if source.suffix == '.json' else 'Reviewed continuing medical instruction.\n')
                evidence.append({'path': relative, 'sha256': digest(source)})
            opening['opening_review']['reconciliations'][name] = {'status': 'COMPLETE', 'evidence': evidence}
        opening['opening_review']['status'] = 'COMPLETE'
        row = opening['opening_assessments'][0]
        card = root/row['target'];card.parent.mkdir(parents=True, exist_ok=True)
        text = authored_card(root, 2015, 'Sample', card)
        final = root/row['final_assessment']
        exit_review = SeasonPaths(2015, root).record('closeouts/exit_interviews.md')
        text = text.replace(os.path.relpath(exit_review, card.parent), os.path.relpath(final, card.parent))
        previous = (root/row['previous_opening']).read_text()
        periods = {False: empty_period(), True: empty_period()}
        text = text.split(START)[0]+stats_block(2015, 'Sample', 'LS', periods, previous, root)+'\n'
        card.write_text(text)
        row.update(status='COMPLETE', reviewed_sha256=digest(card))
        path.write_text(json.dumps(opening))
        return opening

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
            SeasonPaths(2015, root).calendar.unlink()
            with self.assertRaisesRegex(ValueError,'historical successor calendar'):stage(root,data)
            data['gates']['exit_interviews']['evidence']=[]
            self.assertIn('Completed gate lacks evidence: exit_interviews',check(root,data))
            data['carry_forward']['roster']='../../outside.md'
            with self.assertRaisesRegex(ValueError,'leaves repository'):check(root,data)

    def test_final_assessment_sources_carry_without_relabelling_opening_grades(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); data = self.assessment_baseline(root)
            cards = SeasonPaths(2014, root).record('player_profiles')
            before = {p: p.read_bytes() for p in cards.glob('*.md')}
            stage(root, data)
            staged = json.loads((root/'career/2015/opening_handoff.json').read_text())
            self.assertEqual(len(staged['opening_assessments']), 1)
            planned = staged['opening_assessments'][0]
            self.assertTrue(planned['final_assessment'].endswith('Player_Assessments/sample.md'))
            self.assertEqual(planned['status'], 'REVIEW_REQUIRED')
            self.assertEqual(before, {p: p.read_bytes() for p in before})
            self.assertFalse(SeasonPaths(2015, root).record('player_profiles/sample.md').exists())
            self.assertFalse(SeasonPaths(2015, root).record('player_profiles/departed.md').exists())
            self.assertFalse(SeasonPaths(2015, root).awards.exists())
            (cards/'sample.md').write_text((cards/'sample.md').read_text()+'Changed assessment\n')
            with self.assertRaisesRegex(ValueError, 'not frozen/reviewed: player_cards'):
                stage(root, data)

    def test_old_event_markers_stay_with_their_original_owner(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);data=self.baseline(root,2014)
            roster=root/data['carry_forward']['roster']
            event='<!-- event-record: {"id":"2014-example","date":"2014-12-28","status":"closed","summary":"A recorded event"} -->'
            roster.write_text(roster.read_text()+event+'\n')
            data['source_sha256']['roster']=digest(roster)
            stage(root,data)
            self.assertIn(event,roster.read_text())
            self.assertNotIn('event-record:',SeasonPaths(2015,root).roster.read_text())

    def test_opening_cards_without_finals_block_all_staging_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);data=self.baseline(root,2014)
            cards=SeasonPaths(2014,root).record('player_profiles')
            data['carry_forward'].pop('final_assessments')
            with self.assertRaisesRegex(ValueError,'Season-end player assessments'):
                stage(root,data)
            self.assertFalse(SeasonPaths(2015,root).roster.exists())

    def test_inventory_tracks_real_owners_and_reopens_changed_membership(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);data=self.baseline(root,2014)
            plan=SeasonPaths(2014,root).record('offseason/player_development/sample.md')
            plan.parent.mkdir(parents=True);plan.write_text('Undelivered teaching work remains due.\n')
            with self.assertRaisesRegex(ValueError,'inventory changed'):
                stage(root,data)
            refresh_reference_inventory(root,data)
            review=data['reference_inventory']['individual_development']
            self.assertEqual(review['sources'],[plan.relative_to(root).as_posix()])
            self.assertEqual(review['status'],'OPEN')
            review.update(status='COMPLETE',evidence=[{'path':review['sources'][0],'sha256':digest(plan)}])
            stage(root,data)
            self.assertFalse(SeasonPaths(2015,root).record('offseason/player_development/sample.md').exists())
            self.assertEqual(plan.read_text(),'Undelivered teaching work remains due.\n')
            later = {'season': 2015}
            refresh_reference_inventory(root, later)
            self.assertIn(plan.relative_to(root).as_posix(),
                          later['reference_inventory']['individual_development']['sources'])
            plan.write_text('New delivery evidence requires review.\n')
            self.assertTrue(any('changed review evidence' in e for e in check(root,data)))

    def test_opening_requires_complete_cards_and_all_reconciliations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);data=self.assessment_baseline(root);stage(root,data)
            opening=json.loads((root/'career/2015/opening_handoff.json').read_text())
            errors=opening_errors(root,opening)
            self.assertTrue(any('Missing opening assessment' in e for e in errors))
            self.assertTrue(any('reconciliation remains open: medical' in e for e in errors))
            self.assertTrue(repository_opening_errors(root,2015))
            (root/'career/2015/opening_handoff.json').unlink()
            self.assertTrue(repository_opening_errors(root,2015))

    def test_completed_opening_is_reviewed_without_activating_or_freezing_future_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);opening=self.completed_opening(root)
            self.assertEqual(opening_errors(root,opening),[])
            source=root/opening['opening_assessments'][0]['final_assessment'];before=source.read_bytes()
            review_opening(root,opening)
            self.assertEqual(repository_opening_errors(root,2015),[])
            self.assertEqual(source.read_bytes(),before)
            # Normal later coaching notes do not erase the dated opening approval.
            card=root/opening['opening_assessments'][0]['target']
            card.write_text(card.read_text()+'\nLater permitted coaching update.\n')
            self.assertEqual(repository_opening_errors(root,2015),[])
            self.assertTrue(any('changed opening assessment review' in e for e in opening_errors(root,opening)))
            manifest=root/'career/2015/opening_handoff.json'
            changed=json.loads(manifest.read_text());changed['opening_review']['status']='OPEN'
            manifest.write_text(json.dumps(changed))
            self.assertTrue(repository_opening_errors(root,2015))

    def test_opening_rejects_stale_reviews_and_dropped_career_statistics(self):
        for kind in ('card','medical','prior_statistics','final'):
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);opening=self.completed_opening(root)
                row=opening['opening_assessments'][0]
                if kind=='medical':
                    source=SeasonPaths(2015,root).record('medical/current_injury_report.md')
                elif kind=='final':
                    source=root/row['final_assessment']
                else:
                    source=root/row['target']
                text=source.read_text()
                if kind=='prior_statistics':
                    text='\n'.join(line for line in text.splitlines() if not line.startswith('| 2013 |'))+'\n'
                else:
                    text+='\nChanged source.\n'
                source.write_text(text)
                if kind=='prior_statistics':row['reviewed_sha256']=digest(source)
                self.assertTrue(opening_errors(root,opening))
                with self.assertRaises(ValueError):review_opening(root,opening)

    def test_existing_successor_receipts_are_not_silently_treated_as_reset(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);data=self.baseline(root,2014)
            receipt=SeasonPaths(2015,root).receipts/'unexpected.json'
            receipt.parent.mkdir(parents=True);receipt.write_text('{}')
            with self.assertRaisesRegex(ValueError,'already contains game receipts'):
                stage(root,data)
            self.assertEqual(receipt.read_text(),'{}')
            self.assertFalse(SeasonPaths(2015,root).roster.exists())

    def test_required_owners_cannot_be_omitted_to_skip_final_readiness(self):
        for omitted in (('roster',), ('player_cards',), ('player_cards','final_assessments')):
            with self.subTest(omitted=omitted),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);data=self.assessment_baseline(root)
                for name in omitted:data['carry_forward'].pop(name)
                for path in SeasonPaths(2014,root).record('closeouts/player_assessments').glob('*.md'):
                    path.unlink()
                errors=check(root,data,staging=True)
                for name in omitted:
                    self.assertIn('Missing required carry-forward owner: '+name,errors)
                self.assertTrue(any('missing final annual assessment' in e for e in errors))
                with self.assertRaises(ValueError):stage(root,data)
                self.assertFalse(SeasonPaths(2015,root).roster.exists())

    def test_current_prior_team_review_and_source_snapshot_must_still_match(self):
        for changed in ('team_gate','source_snapshot','team_evidence'):
            with self.subTest(changed=changed),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);opening=self.completed_opening(root)
                path=SeasonPaths(2014,root).record('closeouts/season_handoff.json')
                prior=json.loads(path.read_text())
                if changed=='team_gate':
                    prior['gates']['roster_and_medical']['status']='OPEN'
                elif changed=='source_snapshot':
                    prior['source_sha256']['staff']='changed-review'
                else:
                    source=root/prior['carry_forward']['staff']
                    prior['gates']['staff_contracts']['evidence']=[{
                        'path':source.relative_to(root).as_posix(),'sha256':digest(source)}]
                path.write_text(json.dumps(prior))
                self.assertTrue(any('Prior-season' in e for e in opening_errors(root,opening)))
                with self.assertRaises(ValueError):review_opening(root,opening)

    def test_later_league_history_closure_does_not_reopen_team_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);opening=self.completed_opening(root)
            path=SeasonPaths(2014,root).record('closeouts/season_handoff.json')
            prior=json.loads(path.read_text())
            source=root/'career/2014/league_history_closed.md';source.write_text('Reviewed league history closure.\n')
            for name in HISTORY_GATES:
                prior['gates'][name]={'status':'COMPLETE','evidence':[{
                    'path':source.relative_to(root).as_posix(),'sha256':digest(source)}]}
            path.write_text(json.dumps(prior))
            self.assertEqual(opening_errors(root,opening),[])
            review_opening(root,opening)
            after=json.loads(path.read_text())
            self.assertTrue(all(after['gates'][name]['status']=='COMPLETE' for name in HISTORY_GATES))

    def test_duplicate_or_additional_historical_stat_rows_fail_opening(self):
        for duplicate in (True,False):
            with self.subTest(duplicate=duplicate),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);opening=self.completed_opening(root)
                row=opening['opening_assessments'][0];card=root/row['target']
                text=card.read_text()
                previous=next(line for line in text.splitlines() if line.startswith('| 2014 |'))
                added=previous if duplicate else previous.replace('| 2014 |','| 2012 |',1)
                card.write_text(text.replace(previous,previous+'\n'+added,1))
                row['reviewed_sha256']=digest(card)
                self.assertTrue(any('changed prior regular-season statistics' in e
                                    for e in opening_errors(root,opening)))

    def test_only_explicit_unresolved_opening_decisions_block_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);opening=self.completed_opening(root)
            opening['pending_decisions']=[{'id':'summer-role','status':'OPEN',
                                           'requires_user':True,'date':'2015-07-30'}]
            self.assertEqual(opening_errors(root,opening),[])
            opening['pending_decisions'].append({'id':'opening-contract','status':'OPEN','blocks_opening':True})
            self.assertTrue(any('Unresolved decision blocks opening' in e for e in opening_errors(root,opening)))
            opening['pending_decisions'][-1]['status']='RESOLVED'
            self.assertEqual(opening_errors(root,opening),[])
            prior_path=SeasonPaths(2014,root).record('closeouts/season_handoff.json')
            prior=json.loads(prior_path.read_text())
            prior['pending_decisions']=[{'id':'new-opening-hold','blocks_opening':True,'status':'OPEN'}]
            prior_path.write_text(json.dumps(prior))
            self.assertTrue(any('prior handoff / new-opening-hold' in e for e in opening_errors(root,opening)))


if __name__=='__main__':unittest.main()
