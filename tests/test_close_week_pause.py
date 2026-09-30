"""Kernel 2014.4 E2 wired into the weekly closure (scripts/close_week.py).

The protagonist game runs first under user control; a consequential
Jacksonville removal writes a paused record with completed events only and
closes nothing else; --continue resumes the same packet through the same
private event reference and then closes the whole slate as one batch.
Onsets are forced through the kernel's test-only ``_test_onsets`` hook by
patching the runner's kernel binding in the test alone; synthetic rosters,
synthetic ids and a local private service instance. No 2014 game runs.
"""
import contextlib
import dataclasses
import functools
import io
import json
import sys
import tempfile
import threading
import unittest
from dataclasses import replace
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import game_runner, kernel
from runtime.kernel import TeamInput, validate_result
from runtime.private_client import Client
from runtime.private_service import Store, handler
from runtime.seasons import SeasonPaths
from scripts import close_week
from support_rosters import game_day_roster

JAX = close_week.PROTAGONIST
EVENT = "pause-week01-b-at-jacksonville"
BACKGROUND = "pause-week01-d-at-c"


def settled(possessions, pause_drive):
    return [{k: v for k, v in p.items() if p["number"] < pause_drive or k not in ("kickoff_after", "next_start")}
            for p in possessions if p["number"] <= pause_drive]


def club(team_id, prefix, featured=(), third_quarterback=False):
    dropped = {prefix + "-WR5"} | ({prefix + "-S4"} if third_quarterback else set())
    roster = tuple(p for p in game_day_roster(prefix) if p.player_id not in dropped)
    if third_quarterback:  # a real choice for the quarterback slot (S4 gave up his seat)
        roster += (replace(roster[1], player_id=prefix + "-QB3", depth=3),)
    return TeamInput(team_id, tuple(p.player_id for p in roster), roster=roster,
                     rotation_plan=tuple({"player_id": pid, "featured": True} for pid in featured))


def game(event_id, receipt, away, home):
    return {"event_id": event_id, "receipt": receipt, "week": 1, "away": away.team_id, "home": home.team_id,
            "venue": "home", "game_type": "regular",
            "away_input": dataclasses.asdict(away), "home_input": dataclasses.asdict(home)}


class CloseWeekPauseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        (root / "career/2014").mkdir(parents=True)
        self.paths = SeasonPaths(2014, root)
        store = Store(root / "private/state.sqlite3"); store.initialize("snapshot")
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler(store, "test-only-token", "snapshot"))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close); self.addCleanup(server.shutdown)
        self.client = Client(f"http://127.0.0.1:{server.server_port}", token="test-only-token", snapshot="snapshot")
        self.home = club(JAX, "A", featured=("A-QB1", "A-WR1"), third_quarterback=True)
        self.away = club("B", "B")
        # Background game listed first: the closure must still draw Jacksonville first.
        self.package = {"season": 2014, "week": 1, "games": [
            game(BACKGROUND, "week_01_d_at_c.json", club("D", "D"), club("C", "C")),
            game(EVENT, "week_01_b_at_jacksonville.json", self.away, self.home)]}
        self.results_path = self.paths.cache(1, "results")
        # The packet names its management mode, so the user-controlled event
        # reference is the game's only identity. Close it once here, derive the
        # kernel entropy the runner will derive from the same reference, find
        # Jacksonville's first possession, and force QB1's removal at its end.
        packet = game_runner.build_game_packet(EVENT, "snapshot", self.home, self.away,
                                               management_mode="user_controlled")
        self.entropy = game_runner._entropy_from_ref(self.client.close_event(packet))
        base = kernel.resolve_game(self.home, self.away, seed=self.entropy, event_id=EVENT)
        self.drive = next(p["number"] for p in base["possessions"] if p["team"] == JAX)
        self.onsets = onsets = {(self.drive, "A-QB1"): {"injury_class": "lower_extremity",
                                                         "severity": "multi_week", "removed": True}}

        def forced(home, away, **kwargs):
            extra = {"_test_onsets": dict(onsets)} if kwargs.get("event_id") == EVENT else {}
            return kernel.resolve_game(home, away, **kwargs, **extra)
        patcher = patch.object(game_runner, "resolve_game", forced)
        patcher.start(); self.addCleanup(patcher.stop)

    def close(self, answer=None):
        with contextlib.redirect_stdout(io.StringIO()):
            return close_week.close_slate(self.package, self.paths, "snapshot", self.client,
                                          self.results_path, answer)

    def test_pause_writes_partial_only_and_closes_nothing_else(self):
        results, paused = self.close()
        self.assertIsNotNone(paused)
        self.assertEqual(results, {})
        self.assertFalse(self.results_path.exists())
        self.assertFalse(self.paths.receipts.exists())
        record_path = self.paths.paused_game(1)
        self.assertEqual(record_path, self.paths.regular_season / "week_01" / "paused_game.json")
        record = json.loads(record_path.read_text())
        self.assertEqual(record["status"], "paused")
        self.assertEqual(record["event_id"], EVENT)
        self.assertEqual(record["decisions"], [])
        self.assertNotIn("final_score", json.dumps(record))
        self.assertNotIn("team_stats", json.dumps(record))
        pause = record["pause"]
        self.assertEqual(pause["team"], JAX)
        self.assertEqual(pause["drive"], self.drive)
        # The store's seed is random per test, so a natural onset may share the drive.
        self.assertIn("A-QB1", [i["player"] for i in pause["injuries"]])
        quarterback = next(d for d in pause["decisions"] if d["slot"] == "A-QB1")
        self.assertIn("A-QB2", quarterback["eligible"])
        text = close_week.describe_pause(record, record_path, 1, 2014)
        self.assertIn("removed: A-QB1", text)
        self.assertIn("--continue ANSWER.json", text)
        self.assertIn(pause["continuation_token"][:16], text)
        # Rerunning without an answer pauses again at the same token and draws nothing.
        again, paused_again = self.close()
        self.assertEqual(again, {})
        self.assertEqual(paused_again["pause"]["continuation_token"], pause["continuation_token"])

    def test_continue_resumes_the_same_event_and_closes_the_slate(self):
        _, paused = self.close()
        pause = paused["pause"]
        quarterback = next(d for d in pause["decisions"] if d["slot"] == "A-QB1")
        choice = next(p for p in reversed(quarterback["eligible"]) if p != quarterback["default"])
        # Stone's answer names every pending slot: the depth default elsewhere, his choice at quarterback.
        choices = {d["slot"]: d["default"] for d in pause["decisions"]}
        choices["A-QB1"] = choice
        answer_path = Path(self.tmp.name) / "answer.json"
        answer_path.write_text(json.dumps({"choices": choices}))
        results, still_paused = self.close(close_week.load_answer(answer_path))
        while still_paused is not None:  # a later consequential removal: take the depth default
            defaults = {d["slot"]: d["default"] for d in still_paused["pause"]["decisions"]}
            results, still_paused = self.close({"choices": defaults})
        self.assertEqual(set(results), {EVENT, BACKGROUND})
        final = results[EVENT]
        self.assertTrue(final["terminated"])
        self.assertEqual(validate_result(final), [])
        self.assertEqual(final["pauses"][0]["continuation_token"], pause["continuation_token"])
        self.assertEqual(final["pauses"][0]["choices"], choices)
        sub = next(s for s in final["substitutions"] if s["removed"] == "A-QB1")
        self.assertEqual((sub["basis"], sub["replacement"]), ("coach_choice", choice))
        record = json.loads(self.paths.paused_game(1).read_text())
        self.assertEqual(record["status"], "closed")
        self.assertEqual(record["decisions"][0]["choices"], choices)
        self.assertNotIn("partial", record)
        # The background game was drawn autonomously and once.
        self.assertTrue(results[BACKGROUND]["terminated"])
        self.assertEqual(validate_result(results[BACKGROUND]), [])
        receipts_dir = close_week.write_receipts(self.package, self.paths, results, 2014)
        self.assertEqual(sorted(p.name for p in receipts_dir.iterdir()),
                         ["week_01_b_at_jacksonville.json", "week_01_d_at_c.json"])
        own = json.loads((receipts_dir / "week_01_b_at_jacksonville.json").read_text())
        self.assertEqual(own["season"], 2014)
        # Same game run autonomously: identical up to the pause (same event
        # reference, same frozen injury), then the depth default instead of Stone's choice.
        auto = kernel.resolve_game(self.home, self.away, seed=self.entropy, event_id=EVENT,
                                   _test_onsets=dict(self.onsets))
        self.assertEqual(settled(auto["possessions"], self.drive), settled(paused["partial"]["possessions"], self.drive))
        self.assertEqual([r for r in auto["play_ledger"] if r["drive"] <= self.drive], paused["partial"]["play_ledger"])
        self.assertEqual([r for r in final["play_ledger"] if r["drive"] <= self.drive], paused["partial"]["play_ledger"])
        self.assertEqual([i for i in auto["injuries"] if i["drive"] <= self.drive],
                         [i for i in final["injuries"] if i["drive"] <= self.drive])
        auto_sub = next(s for s in auto["substitutions"] if s["removed"] == "A-QB1")
        self.assertEqual(auto_sub["basis"], "depth_order")
        self.assertNotEqual(auto_sub["replacement"], choice)
        after = lambda r: [row.get("passer") for row in r["play_ledger"] if row["drive"] > self.drive and row.get("offense") == JAX]
        self.assertIn(choice, after(final))
        self.assertNotIn(choice, after(auto))

    def test_answers_are_validated_against_the_pending_pause(self):
        _, paused = self.close()
        with self.assertRaisesRegex(ValueError, "token does not match"):
            self.close({"choices": {"A-QB1": "A-QB2"}, "token": "0" * 64})
        with self.assertRaises(ValueError):
            self.close({"choices": {"A-QB1": "A-WR1"}})  # not eligible for the slot
        with self.assertRaises(ValueError):
            close_week.continuation_decisions(None, {"choices": {"A-QB1": "A-QB2"}})
        self.assertEqual(json.loads(self.paths.paused_game(1).read_text())["status"], "paused")
        self.assertEqual(paused["decisions"], [])

    def test_command_line_takes_the_answer_file(self):
        with patch.object(sys, "argv", ["close_week", "1", "--season", "2014", "--close", "--continue", "x.json"]), \
                patch.object(close_week, "require_game_release", side_effect=ValueError("blocked")), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(close_week.main(), 1)
        bad = Path(self.tmp.name) / "bad.json"; bad.write_text(json.dumps({"choices": {}}))
        with self.assertRaises(ValueError):
            close_week.load_answer(bad)


if __name__ == "__main__":
    unittest.main()
