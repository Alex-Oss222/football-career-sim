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
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import game_runner, kernel
from runtime.kernel import TeamInput, validate_result
from runtime.play_detail import check_ledger
from runtime.seasons import SeasonPaths
from scripts import close_week
from local_private_service import local_service
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
    """The local private store's seed is pinned per test (the test's own
    name; local_private_service), so every run draws the same games."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.fixture(Path(self.tmp.name), self._testMethodName)

    def fixture(self, root, seed_label):
        (root / "career/2014").mkdir(parents=True)
        self.paths = SeasonPaths(2014, root)
        self.client = local_service(self, root / "private", seed_label)[1]
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
        self.assertEqual(record_path, self.paths.regular_season / "Week_01" / "paused_game.json")
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
        # reference, same frozen injury), then the depth default instead of
        # Stone's choice. Only the pause drive's replacement is compared:
        # after it either run may lose its passer to a natural onset and
        # promote the other quarterback, so the first post-pause passer, not
        # the whole remainder, tells the continued run from the autonomous one.
        auto = kernel.resolve_game(self.home, self.away, seed=self.entropy, event_id=EVENT,
                                   _test_onsets=dict(self.onsets))
        self.assertEqual(settled(auto["possessions"], self.drive), settled(paused["partial"]["possessions"], self.drive))
        self.assertEqual([r for r in auto["play_ledger"] if r["drive"] <= self.drive], paused["partial"]["play_ledger"])
        self.assertEqual([r for r in final["play_ledger"] if r["drive"] <= self.drive], paused["partial"]["play_ledger"])
        self.assertEqual([i for i in auto["injuries"] if i["drive"] <= self.drive],
                         [i for i in final["injuries"] if i["drive"] <= self.drive])
        auto_sub = next(s for s in auto["substitutions"] if s["removed"] == "A-QB1")
        self.assertEqual((auto_sub["basis"], auto_sub["replacement"]), ("depth_order", quarterback["default"]))
        self.assertNotEqual(auto_sub["replacement"], choice)
        first_passer = lambda r: next(p["passer"] for p in r["possessions"] if p["team"] == JAX and p["number"] > self.drive)
        self.assertEqual(first_passer(final), choice)
        self.assertEqual(first_passer(auto), quarterback["default"])
        self.assertTrue(all(p["passer"] == "A-QB1" for p in final["possessions"]
                            if p["team"] == JAX and p["number"] <= self.drive))

    def test_seed_sweep_pauses_continues_and_closes_without_invariant_failures(self):
        # A small set of pinned store seeds through the whole pause/continue
        # closure: every closed result validates (no chain, participation or
        # removal invariant fires on the resumed path).
        for label in ("sweep-0", "sweep-1", "sweep-2"):
            with self.subTest(seed=label):
                self.fixture(Path(self.tmp.name) / label, label)
                _, paused = self.close()
                self.assertIsNotNone(paused)
                pause = paused["pause"]
                quarterback = next(d for d in pause["decisions"] if d["slot"] == "A-QB1")
                choices = {d["slot"]: d["default"] for d in pause["decisions"]}
                choices["A-QB1"] = next(p for p in reversed(quarterback["eligible"]) if p != quarterback["default"])
                results, still_paused = self.close({"choices": choices})
                while still_paused is not None:
                    defaults = {d["slot"]: d["default"] for d in still_paused["pause"]["decisions"]}
                    results, still_paused = self.close({"choices": defaults})
                self.assertEqual(set(results), {EVENT, BACKGROUND})
                for event_id, result in results.items():
                    self.assertTrue(result["terminated"], event_id)
                    self.assertEqual(validate_result(result), [], event_id)
                    self.assertEqual(result["diagnostics"].get("chain_layout_failed", 0), 0, event_id)
                final = results[EVENT]
                self.assertEqual(final["pauses"][0]["choices"], choices)
                self.assertEqual(next(p["passer"] for p in final["possessions"]
                                      if p["team"] == JAX and p["number"] > self.drive), choices["A-QB1"])

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

    def test_a_pause_from_another_kernel_is_refused(self):
        # Kernel 2014.6 plumbing (B1): a pause is continued only by the
        # kernel that made it; resuming under another would replay its
        # prefix with different draws. A closed record stays readable.
        _, paused = self.close()
        self.assertEqual(paused["kernel_version"], kernel.KERNEL_VERSION)
        path = self.paths.paused_game(1)
        record = json.loads(path.read_text())
        self.assertEqual(close_week.read_paused(path, EVENT)["status"], "paused")
        path.write_text(json.dumps(dict(record, kernel_version="2014.4")))
        with self.assertRaisesRegex(ValueError, "made by kernel 2014.4"):
            close_week.read_paused(path, EVENT)
        with self.assertRaisesRegex(ValueError, "made by kernel 2014.4"):
            self.close({"choices": {"A-QB1": "A-QB2"}, "token": record["pause"]["continuation_token"]})
        with self.assertRaisesRegex(ValueError, "made by kernel 2014.4"):
            self.close()
        with self.assertRaisesRegex(ValueError, "the live kernel is 2014.6"):
            close_week.read_paused(path, EVENT, kernel_version="2014.6")
        path.write_text(json.dumps(dict(record, kernel_version="2014.4", status="closed")))
        self.assertEqual(close_week.read_paused(path, EVENT)["status"], "closed")

    def test_command_line_takes_the_answer_file(self):
        with patch.object(sys, "argv", ["close_week", "1", "--season", "2014", "--close", "--continue", "x.json"]), \
                patch.object(close_week, "require_game_release", side_effect=ValueError("blocked")), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(close_week.main(), 1)
        bad = Path(self.tmp.name) / "bad.json"; bad.write_text(json.dumps({"choices": {}}))
        with self.assertRaises(ValueError):
            close_week.load_answer(bad)


class FourthDownPauseTests(unittest.TestCase):
    """Kernel 2014.6 batch B9F through the weekly closure: Jacksonville's
    fourth downs are Stone's live calls (no fourth-down block on the frozen
    sheet), so the user-controlled game pauses at each one with only what
    Skalaski and Tice supply, the answer file resumes it, and the background
    game is decided by the league chart. Its two-point tries are asked live
    as well (otherwise: ask; U6 answered either way). The kernel resolves
    under PROFILE_2014_6 through the runner's binding (test patch only); the
    installed kernel stays 2014.5."""

    SHEET = ({"name": "12 Ace Right, Power R", "family": "Power", "type": "run"},
             {"name": "12 Trey Right, Stick", "family": "Stick", "type": "pass"})

    def setUp(self):
        from runtime.profiles import PROFILE_2014_6
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        (root / "career/2014").mkdir(parents=True)
        self.paths = SeasonPaths(2014, root)
        self.client = local_service(self, root / "private", self._testMethodName)[1]
        delegation = {"otherwise": "league"}
        self.home = replace(club(JAX, "A"), offensive_call_sheet=self.SHEET, try_policy={"otherwise": "ask"},
                            kickoff_policy=delegation)
        self.away = club("B", "B")
        self.package = {"season": 2014, "week": 1, "games": [
            game(BACKGROUND, "week_01_d_at_c.json", club("D", "D"), club("C", "C")),
            game(EVENT, "week_01_b_at_jacksonville.json", self.away, self.home)]}
        self.results_path = self.paths.cache(1, "results")
        resolve = functools.partial(kernel.resolve_game, _test_profile=PROFILE_2014_6)
        for target, name, value in ((game_runner, "resolve_game", resolve),
                                    (game_runner, "installed_profile", lambda: PROFILE_2014_6),
                                    (sys.modules["runtime"], "KERNEL_VERSION", "2014.6")):
            patcher = patch.object(target, name, value)
            patcher.start(); self.addCleanup(patcher.stop)

    def close(self, answer=None):
        with contextlib.redirect_stdout(io.StringIO()):
            return close_week.close_slate(self.package, self.paths, "snapshot", self.client,
                                          self.results_path, answer)

    def test_live_fourth_downs_pause_continue_and_close_the_slate(self):
        results, paused = self.close()
        self.assertEqual(results, {})
        self.assertFalse(self.paths.receipts.exists())
        cycle = ("go", "punt", "field_goal")
        answers, triggers, texts = [], [], []
        for _ in range(80):
            if paused is None:
                break
            pause = paused["pause"]
            triggers.append(pause["trigger"])
            record_path = self.paths.paused_game(1)
            record = json.loads(record_path.read_text())
            self.assertEqual((record["status"], record["kernel_version"]), ("paused", "2014.6"))
            self.assertNotIn("final_score", json.dumps(record))
            if pause["trigger"] == "fourth_down":
                text = close_week.describe_pause(record, record_path, 1, 2014)
                texts.append(text)
                choice = cycle[len(answers) % 3]
                answers.append(choice)
                choices = {"fourth_down": choice}
                if choice == "go":
                    calls = next(d for d in pause["decisions"] if d["slot"] == "call")["eligible"]
                    choices["call"] = calls[-1]
            elif pause["trigger"] == "two_point":
                choices = {"try": "kick"}
                texts.append(close_week.describe_pause(record, record_path, 1, 2014))
            else:
                choices = {d["slot"]: d["default"] for d in pause["decisions"]}
            answer_path = Path(self.tmp.name) / "answer.json"
            answer_path.write_text(json.dumps({"choices": choices}))
            results, paused = self.close(close_week.load_answer(answer_path))
        self.assertIsNone(paused)
        self.assertIn("fourth_down", triggers)
        self.assertEqual(set(results), {EVENT, BACKGROUND})
        final = results[EVENT]
        self.assertTrue(final["terminated"])
        self.assertEqual(validate_result(final) + check_ledger(final), [])
        mine = [d for p in final["possessions"] if p["team"] == JAX for d in p["fourth_downs"]]
        self.assertEqual([d["decision"] for d in mine], answers)
        self.assertTrue(all(d["basis"] == "live" for d in mine))
        self.assertTrue(all(d["call"] in (None, self.SHEET[1]["name"]) for d in mine))
        self.assertTrue(all(d["call"] == self.SHEET[1]["name"] for d in mine if d["decision"] == "go"))
        self.assertTrue(all(d["basis"] == "league" for p in final["possessions"] if p["team"] != JAX
                            for d in p["fourth_downs"]))
        background = results[BACKGROUND]
        self.assertTrue(all(d["basis"] == "league" for p in background["possessions"] for d in p["fourth_downs"]))
        self.assertEqual([h["trigger"] for h in final["pauses"]], triggers)
        record = json.loads(self.paths.paused_game(1).read_text())
        self.assertEqual(record["status"], "closed")
        self.assertEqual(len(record["decisions"]), len(triggers))
        # What the pause printed: Skalaski's and Tice's lines, never a probability.
        fourth = [t for t in texts if "PAUSED (fourth down)" in t]
        self.assertTrue(fourth)
        for text in fourth:
            self.assertIn("Skalaski", text)
            self.assertIn("Tice: prepared conversion call (none named on the frozen sheet)", text)
            self.assertIn('{"choices": {"fourth_down": "go" | "field_goal" | "punt", "call": "<call>"}}', text)
            for word in ("prob", "basis", "cell", "chart", "odds"):
                self.assertNotIn(word, text.lower())
        if "two_point" in triggers:
            self.assertTrue(any("PAUSED (try after touchdown)" in t for t in texts))
        receipts_dir = close_week.write_receipts(self.package, self.paths, results, 2014)
        own = json.loads((receipts_dir / "week_01_b_at_jacksonville.json").read_text())
        self.assertEqual(check_ledger(own), [])

    def test_a_wrong_answer_is_refused_and_the_pause_stands(self):
        _, paused = self.close()
        while paused["pause"]["trigger"] != "fourth_down":
            pause = paused["pause"]
            choices = ({"try": "kick"} if pause["trigger"] == "two_point" else
                       {d["slot"]: d["default"] for d in pause["decisions"]})
            _, paused = self.close({"choices": choices})
        token = paused["pause"]["continuation_token"]
        for choices in ({"fourth_down": "go"}, {"fourth_down": "go", "call": "Nowhere"}, {"fourth_down": "kneel"},
                        {"A-QB1": "A-QB2"}):
            with self.assertRaises(ValueError, msg=choices):
                self.close({"choices": choices})
        record = json.loads(self.paths.paused_game(1).read_text())
        self.assertEqual((record["status"], record["pause"]["continuation_token"]), ("paused", token))
        self.assertFalse(self.results_path.exists())


if __name__ == "__main__":
    unittest.main()
