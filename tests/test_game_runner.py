import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import inspect
import tempfile
import unittest
from unittest.mock import patch

from runtime.game_runner import (architecture_errors, build_game_packet,
                                 resolve_background_game,
                                 resolve_protagonist_game, run_game)
from runtime.kernel import TeamInput, _append_evidence
from runtime.player_evidence import PlayerInput
from runtime.private_client import Client, PrivateRuntimeUnavailable
from runtime.private_service import Store
from local_private_service import TOKEN, local_service
from support_rosters import single_quarterback_teams


class ProductionGameRunnerTests(unittest.TestCase):
    """The local private store's seed is pinned (local_private_service) so
    every game here reproduces; before October 1, 2026 the store drew a
    fresh seed per run and this module's ordinary autonomous games were
    refused by the kernel invariants under some seeds (the October 1 seed
    sweep, scripts/research/seed_sweep.py).

    The store seeds 44 (a real five-run fumble whose first down must come
    before the fumbled snap) and 67 (an emergency passer replaced without a
    removal) were pinned here until kernel 2014.6 batch B1 (October 2,
    2026); they are now forced fixtures that no later kernel can make
    hollow: tests/test_chains.py SeedSweepRegressionTests."""

    STORE_SEED = "runner"
    SWEEP_SEEDS = ("runner-0", "runner-1", "runner-2")

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/"state.sqlite3"
        self.token=TOKEN
        self.store,self.client=local_service(self,self.tmp.name,self.STORE_SEED)
        # One quarterback, one unavailable receiver and a complete legal
        # 46-man game-day unit on both clubs (support_rosters).
        self.home,self.away=single_quarterback_teams()

    def test_more_than_46_actives_fails_closed(self):
        roster=tuple(self.home.roster)
        self.assertEqual(len([p for p in roster if p.available]),46)
        extra=roster+(PlayerInput("extra","WR",roles=("receiver",)),)
        big=TeamInput("A",tuple(p.player_id for p in extra if p.available),roster=extra)
        with self.assertRaisesRegex(ValueError,"46"):
            build_game_packet("actives","snapshot",big,self.away)
        self.assertTrue(build_game_packet("actives","snapshot",self.home,self.away))

    def test_architecture_and_freeze_precedes_kernel(self):
        self.assertEqual(architecture_errors(),[])
        self.assertNotIn("seed",inspect.signature(run_game).parameters)
        order=[]
        class JournalClient:
            snapshot="snapshot"
            def close_event(self,packet): order.append("closed"); return "ab"*32
        fake={"value":None}
        def kernel(*args,**kwargs):
            order.append("kernel"); return fake
        with patch("runtime.game_runner.resolve_game",kernel), patch("runtime.game_runner.validate_result",lambda result:[]):
            self.assertIs(run_game(self.home,self.away,event_id="order",snapshot="snapshot",client=JournalClient()),fake)
        self.assertEqual(order,["closed","kernel"])


    def test_production_runner_refuses_test_hooks(self):
        # Kernel 2014.6 plumbing (B1): production resolves only with the
        # profile of KERNEL_VERSION; the kernel's _test_* hooks stay private.
        import runtime.game_runner as runner
        from runtime.kernel import resolve_game
        self.assertFalse([n for n in inspect.signature(run_game).parameters if n.startswith("_test")])
        self.assertIn("_test_profile", inspect.signature(resolve_game).parameters)
        self.assertIn("_test_onsets", inspect.signature(resolve_game).parameters)

        def hooked(home, away, *, event_id, snapshot, client=None, _test_profile=None):
            client.close_event(None)
            return runner.resolve_game(home, away, seed=b"", event_id=event_id)

        def forwarding(home, away, *, event_id, snapshot, client=None):
            client.close_event(None)
            return runner.resolve_game(home, away, seed=b"", event_id=event_id, _test_profile=None)
        with patch.object(runner, "run_game", hooked):
            self.assertIn("production runner accepts a test hook (_test_profile)", runner.architecture_errors())
        with patch.object(runner, "run_game", forwarding):
            self.assertIn("production runner passes a test hook to the kernel", runner.architecture_errors())
        self.assertEqual(runner.architecture_errors(), [])

    def test_call_sheet_packet_uses_football_substance_not_display_alias(self):
        calls=({'name':'Mesh Base','family':'Mesh','type':'pass','personnel':'11','formation':'Bunch'},)
        renamed=({'name':'MESH!!!','family':'Mesh','type':'pass','personnel':'11','formation':'Bunch'},)
        one=TeamInput("C",self.home.active_players,roster=self.home.roster,offensive_call_sheet=calls)
        two=TeamInput("C",self.home.active_players,roster=self.home.roster,offensive_call_sheet=renamed)
        p1=build_game_packet("calls","snapshot",one,self.away)
        p2=build_game_packet("calls","snapshot",two,self.away)
        self.assertEqual(p1,p2)
        self.assertNotIn("Mesh Base",str(p1))
        self.assertIn("Mesh",str(p1))

    def test_unlabelled_call_sheet_fails_closed_before_closure(self):
        calls=({'name':'Mystery','family':'Mystery Concept','type':'run'},)
        bad=TeamInput("C",self.home.active_players,roster=self.home.roster,offensive_call_sheet=calls)
        with self.assertRaisesRegex(ValueError,"Mystery"):
            build_game_packet("calls","snapshot",bad,self.away)
        declared=({'name':'Mystery','family':'Mystery Concept','type':'run','carrier':['RB']},)
        ok=TeamInput("C",self.home.active_players,roster=self.home.roster,offensive_call_sheet=declared)
        self.assertTrue(build_game_packet("calls","snapshot",ok,self.away))

    def test_private_replay_restart_conflict_and_no_seed_exposure(self):
        first=run_game(self.home,self.away,event_id="game-1",snapshot="snapshot",client=self.client)
        self.assertEqual(first,run_game(self.home,self.away,event_id="game-1",snapshot="snapshot",client=self.client))
        restarted=Store(self.db); self.assertTrue(restarted.ready())
        replay_client=Client(self.client.url,token=self.token,snapshot="snapshot")
        self.assertEqual(first,run_game(self.home,self.away,event_id="game-1",snapshot="snapshot",client=replay_client))
        changed=TeamInput("A",self.home.active_players,scheme="spread",roster=self.home.roster)
        with self.assertRaises(PrivateRuntimeUnavailable):
            run_game(changed,self.away,event_id="game-1",snapshot="snapshot",client=self.client)
        self.assertNotIn("seed",inspect.signature(run_game).parameters)
        self.assertFalse(any("seed" in key for key in first))

    def test_incomplete_game_day_unit_fails_closed_before_event_closure(self):
        thin=TeamInput("T",("qb","rb"),roster=(PlayerInput("qb","QB"),PlayerInput("rb","RB")))
        with self.assertRaisesRegex(ValueError,"legal game-day unit"):
            build_game_packet("thin","snapshot",thin,self.away)

    def test_one_passer_and_depth_ordered_usage(self):
        result=run_game(self.home,self.away,event_id="depth",snapshot="snapshot",client=self.client)
        players=result["team_stats"]["A"]["players"]
        # Kernel 2014.4: the depth-chart QB passes until he is removed; any
        # later passer is a drive passer that followed his removal.
        throwers=[p for p,v in players.items() if v["pass_attempts"]]
        self.assertEqual(throwers[0] if "qb" in throwers else "qb","qb")
        passers=[p["passer"] for p in result["possessions"] if p["team"]=="A"]
        self.assertEqual(passers[0],"qb")
        if set(throwers)!={"qb"}:
            self.assertTrue(any(i["player"]=="qb" and i["removed"] for i in result["injuries"]))
        self.assertTrue(all(v["tackles"]==v["solo_tackles"]+v["assisted_tackles"] for v in players.values()))

    def test_store_seed_sweep_keeps_the_invariants(self):
        # A small fixed set of store seeds, several ordinary autonomous
        # games each, through the production runner: the kernel invariants
        # (validated inside run_game) hold for every one.
        for label in self.SWEEP_SEEDS:
            root=Path(self.tmp.name)/label; root.mkdir()
            client=local_service(self,root,label)[1]
            for k in range(3):
                with self.subTest(seed=label,game=k):
                    result=run_game(self.home,self.away,event_id="sweep-%d"%k,snapshot="snapshot",client=client)
                    self.assertTrue(result["terminated"])
                    self.assertEqual(result["diagnostics"].get("chain_layout_failed",0),0)

    def test_labels_paths_participation_and_evidence(self):
        self.assertIs(resolve_background_game,run_game)
        self.assertIs(resolve_protagonist_game,run_game)
        first=run_game(self.home,self.away,event_id="labels",snapshot="snapshot",client=self.client)
        # Protagonist is intentionally absent from the packet schema and API.
        packet=build_game_packet("labels-2","snapshot",self.home,self.away)
        self.assertNotIn("protagonist",str(packet).lower())
        self.assertNotIn("out",first["team_stats"]["A"]["players"])
        # A private random game need not include a returned punt. Evidence must
        # follow the observed coverage tackles, rather than inventing one to
        # satisfy a fixture expectation.
        covers=[x["cover_player"] for x in first["play_ledger"]
                if x.get("play_type")=="punt" and x.get("cover_player")]
        observed=[x["player"] for x in first["player_evidence"] if x["unit"]=="special teams"]
        self.assertEqual(sorted(observed),sorted(covers))
        effort=[x for x in first["player_evidence"] if "observable_effort" in x]
        self.assertTrue(all("assignment_execution" in x or x["unit"]=="special teams" for x in effort))


class SparsePlayerEvidenceTests(unittest.TestCase):
    def test_returned_punt_records_only_the_named_coverage_tackle(self):
        cover=PlayerInput("cover","LB",unit="defense",roles=("punt_coverage",))
        evidence=[]
        _append_evidence(evidence,[{"play_type":"punt","cover_player":"cover"}],(cover,),(),"punt")
        self.assertEqual(len(evidence),1)
        self.assertEqual(evidence[0]["unit"],"special teams")
        self.assertEqual(evidence[0]["player"],"cover")
        self.assertEqual(evidence[0]["special_teams_responsibility"],"tackle made on the return")
        self.assertNotIn("observable_effort",evidence[0])
        missing=[]
        _append_evidence(missing,[{"play_type":"punt"}],(cover,),(),"punt")
        self.assertEqual(missing,[])

    def test_route_effort_requires_an_observed_nonturnover_route(self):
        receiver=PlayerInput("receiver","WR")
        evidence=[]
        _append_evidence(evidence,[{"target":"receiver"}],(receiver,),(),"touchdown")
        self.assertEqual(evidence[0]["assignment_execution"],"assignment held")
        self.assertIn("observable_effort",evidence[0])
        missing=[]
        _append_evidence(missing,[],(receiver,),(),"punt")
        _append_evidence(missing,[{"target":"receiver"}],(receiver,),(),"turnover")
        self.assertEqual(missing,[])


if __name__=="__main__": unittest.main()
