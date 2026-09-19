import json, random, tempfile, unittest
from pathlib import Path
from runtime.anchors import evidence_anchor, initialize_team
from runtime.calibration import load, validate
from runtime.injuries import maybe_injury
from runtime.kernel import TeamInput, resolve_game, validate_result
from runtime.game_runner import resolve_background_game, resolve_protagonist_game
from runtime.rules import RULES, DIVISION_TIEBREAKERS, WILD_CARD_TIEBREAKERS, PLAYOFF_SEEDS, review_authority

class RuntimeTests(unittest.TestCase):
    seed=b'synthetic-calibration-seed-not-career-state'
    def teams(self,edge=0):
        players=tuple(f"WR:p{i}" for i in range(46))
        return TeamInput('A',players,2+edge,2),TeamInput('B',players,2,2)
    def test_calibration_reconciles(self): self.assertEqual(validate(load()),[])
    def test_one_kernel_and_label_blind_anchors(self):
        self.assertIs(resolve_background_game,resolve_protagonist_game)
        one=evidence_anchor({'tier':'Plus','contemporaneous_samples':8,'evidence_id':'same','team':'Jacksonville','protagonist':True})
        two=evidence_anchor({'tier':'Plus','contemporaneous_samples':8,'evidence_id':'same','team':'Miami','protagonist':False})
        self.assertEqual(one,two)
        team=initialize_team('JAX',[{'player_id':'active','position':'WR','medical_status':'available'},
                                    {'player_id':'out','position':'RB','medical_status':'out'}],{})
        self.assertEqual(team.active_players,('WR:active',))
    def test_rules_are_period_specific(self):
        self.assertEqual((RULES.active_limit,RULES.kickoff_yard_line,RULES.kickoff_touchback_yard_line,RULES.pat_snap_yard_line),(46,35,20,2))
        self.assertEqual(review_authority(seconds_left=120),'booth'); self.assertEqual(review_authority(seconds_left=121),'coach')
        self.assertEqual(DIVISION_TIEBREAKERS[0],'head_to_head')
        self.assertEqual(WILD_CARD_TIEBREAKERS[-1],'coin_toss')
        self.assertEqual(PLAYOFF_SEEDS['wild_cards'],(5,6))
    def test_determinism_accounting_and_participation(self):
        a,b=self.teams(); r=resolve_game(a,b,seed=self.seed,event_id='synthetic-1')
        self.assertEqual(r,resolve_game(a,b,seed=self.seed,event_id='synthetic-1')); self.assertEqual(validate_result(r),[])
        self.assertTrue(all(p in a.active_players for p in r['team_stats']['A']['players']))
        self.assertTrue(r['player_evidence'])
        for item in r['player_evidence']:
            self.assertNotIn('grade',item)
            self.assertFalse('observable_effort' in item and item['observable_effort'] in {'bad','lazy','low'})
        for team in ('A','B'):
            player_stats=r['team_stats'][team]['players'].values()
            self.assertEqual(sum(p['passing_yards'] for p in player_stats),r['team_stats'][team]['passing_yards'])
            self.assertEqual(sum(p['rushing_yards'] for p in player_stats),r['team_stats'][team]['rushing_yards'])
    def test_pause_and_continuation(self):
        a,b=self.teams(); paused=resolve_game(a,b,seed=self.seed,event_id='pause',management_mode='user_controlled')
        self.assertEqual(len(paused['pauses']),1)
        continued=resolve_game(a,b,seed=self.seed,event_id='pause',management_mode='user_controlled',resume=paused['pauses'][0]['continuation_token'])
        self.assertFalse(continued['pauses'])
    def test_long_run_period_bands_and_matchup_movement(self):
        points=[]; drives=[]; yards=[]; punts=[]; turnovers=[]; penalties=[]; injuries=[]; sacks=[]; field_goals=[]; returns=[]
        a,b=self.teams()
        for i in range(1200):
            r=resolve_game(a,b,seed=self.seed,event_id=f'batch-{i}')
            for t in ('A','B'):
                s=r['team_stats'][t]; points.append(s['points']); drives.append(sum(x['team']==t for x in r['possessions'])); yards.append(s['passing_yards']+s['rushing_yards']); punts.append(s['punts']); turnovers.append(s['turnovers']); penalties.append(s['penalties']); sacks.append(s['sacks_allowed']); field_goals.append(s['field_goals']); returns.append(s['kick_returns']+s['punt_returns'])
            injuries.append(len(r['injuries']))
        def mean(x): return sum(x)/len(x)
        self.assertTrue(17<mean(points)<29); self.assertTrue(8<mean(drives)<16); self.assertTrue(240<mean(yards)<460)
        self.assertTrue(3<mean(punts)<7); self.assertTrue(.7<mean(turnovers)<2.2); self.assertTrue(4<mean(penalties)<9); self.assertTrue(.2<mean(injuries)<2.5)
        self.assertTrue(1<mean(sacks)<4); self.assertTrue(.8<mean(field_goals)<2.5); self.assertTrue(1<mean(returns)<7)
        strong=[]; neutral=[]
        sa,sb=self.teams(2)
        for i in range(500):
            strong.append(resolve_game(sa,sb,seed=self.seed,event_id=f'strong-{i}')['final_score']['A'])
            neutral.append(resolve_game(a,b,seed=self.seed,event_id=f'neutral-{i}')['final_score']['A'])
        self.assertGreater(mean(strong),mean(neutral))
    def test_overtime_terminates_and_reconciles(self):
        a,b=self.teams()
        found=None
        for i in range(500):
            result=resolve_game(a,b,seed=self.seed,event_id=f'ot-search-{i}')
            if any(p.get('period')=='OT' for p in result['possessions']): found=result; break
        self.assertIsNotNone(found)
        self.assertTrue(found['terminated']); self.assertEqual(validate_result(found),[])
        self.assertLessEqual(sum(p['seconds'] for p in found['possessions']),4500)

    def test_penalties_are_event_generated_not_score_adjustments(self):
        a,b=self.teams(); result=resolve_game(a,b,seed=self.seed,event_id='penalties')
        self.assertTrue(all(s['penalties']>=0 and s['penalty_yards']>=s['penalties']*5
                            for s in result['team_stats'].values()))
    def test_injury_bounds_position_and_replay(self):
        def count(pos):
            rng=random.Random(7); vals=[maybe_injury(rng,pos,40) for _ in range(10000)]; return sum(v is not None for v in vals),vals
        rb,vals=count('RB'); qb,_=count('QB'); self.assertGreater(rb,qb)
        self.assertTrue(all(v is None or v.return_days>=0 for v in vals))
        self.assertLess(sum(v is not None and v.severity=='long_term' for v in vals),rb*.12)
        self.assertEqual(maybe_injury(random.Random(91),'LB',200),maybe_injury(random.Random(91),'LB',200))

if __name__=='__main__': unittest.main()
