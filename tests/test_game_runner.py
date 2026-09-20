import inspect
import tempfile
import threading
import unittest
from pathlib import Path
from http.server import ThreadingHTTPServer
from unittest.mock import patch

from runtime.game_runner import (architecture_errors, build_game_packet,
                                 resolve_background_game,
                                 resolve_protagonist_game, run_game)
from runtime.kernel import TeamInput
from runtime.player_evidence import PlayerInput
from runtime.private_client import Client, PrivateRuntimeUnavailable
from runtime.private_service import Store, handler


class ProductionGameRunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/"state.sqlite3"
        self.store=Store(self.db); self.store.initialize("snapshot")
        self.token="test-only-token"
        self.server=ThreadingHTTPServer(("127.0.0.1",0),handler(self.store,self.token,"snapshot"))
        threading.Thread(target=self.server.serve_forever,daemon=True).start()
        self.addCleanup(self.server.server_close); self.addCleanup(self.server.shutdown)
        self.client=Client(f"http://127.0.0.1:{self.server.server_port}",token=self.token,snapshot="snapshot")
        roster=(PlayerInput("qb","QB",roles=("passer",),rotation_status="competition"),
                PlayerInput("rb","RB",roles=("rusher",),rotation_status="bubble"),
                PlayerInput("wr","WR",roles=("receiver",)),
                PlayerInput("ot","OT",roles=("pass_protection",)),
                PlayerInput("lb","LB",unit="defense",roles=("punt_coverage",)),
                PlayerInput("out","WR",available=False))
        self.home=TeamInput("A",tuple(p.player_id for p in roster if p.available),roster=roster)
        self.away=TeamInput("B",tuple(p.player_id for p in roster if p.available),roster=roster)

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

    def test_labels_paths_participation_and_evidence(self):
        self.assertIs(resolve_background_game,run_game)
        self.assertIs(resolve_protagonist_game,run_game)
        first=run_game(self.home,self.away,event_id="labels",snapshot="snapshot",client=self.client)
        # Protagonist is intentionally absent from the packet schema and API.
        packet=build_game_packet("labels-2","snapshot",self.home,self.away)
        self.assertNotIn("protagonist",str(packet).lower())
        self.assertNotIn("out",first["team_stats"]["A"]["players"])
        self.assertTrue(any(x["unit"]=="special teams" for x in first["player_evidence"]))
        effort=[x for x in first["player_evidence"] if "observable_effort" in x]
        self.assertTrue(effort)
        self.assertTrue(all("assignment_execution" in x or x["unit"]=="special teams" for x in effort))


if __name__=="__main__": unittest.main()
