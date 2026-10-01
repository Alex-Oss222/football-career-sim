"""A 2014 preseason game through the same runner and kernel as a regular week.

Synthetic rosters, a temporary season root and the local private service
(pinned seed per test); scripts/close_preseason_game.py's closure, pause and
continuation, receipt location, box score, stat views, duplicate refusal,
the dated extra-point rule and the untouched regular-season tree. No real
2014 game runs and the repository's receipts are never read or written.
"""
import contextlib
import dataclasses
import hashlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import drive_model, game_runner, kernel, preseason, seasons
from runtime.kernel import TeamInput, resolve_game, validate_result
from runtime.rules import PRESEASON, active_limit, extra_point_rule
from runtime.seasons import SeasonPaths
from scripts import close_preseason_game, close_week, render_preseason_stats
from scripts.check_week_input_exclusivity import check_inputs
from local_private_service import local_service
from support_rosters import game_day_roster

JAX = close_week.PROTAGONIST
TB = "Tampa Bay Buccaneers"
EVENT = "2014-preseason-01-tampa-bay-buccaneers-at-jacksonville-jaguars"
FIXTURES = ROOT / "career/2014/04_Training_Camp_and_Preseason/Preseason_Games/fixtures.json"
CALLS = ({"name": "12 Ace Right, Power R", "family": "Power", "type": "run", "personnel": "12", "formation": "12 Ace Right"},
         {"name": "11 Doubles, Zip, Smoke", "family": "Smoke/Now", "type": "pass", "personnel": "11", "formation": "11 Doubles"})


def club(team_id, prefix, third_quarterback=False, plan=()):
    roster = tuple(p for p in game_day_roster(prefix) if p.player_id != prefix + "-WR5")
    if third_quarterback:
        roster += (replace(roster[1], player_id=prefix + "-QB3", depth=3),)
    return TeamInput(team_id, tuple(p.player_id for p in roster), roster=roster, offensive_call_sheet=CALLS,
                     rotation_plan=tuple(plan))


def rotation_plan(prefix):
    """Stone's shape: two first-unit possessions under a snap ceiling with a
    receiver and a guard swapped between them, the second unit, then reserves."""
    return (
        {"side": "offense", "unit": "first offense, series 1", "until": {"possessions": 1},
         "players": {"QB": [prefix + "-QB1"], "WR": [prefix + "-WR1", prefix + "-WR2", prefix + "-WR3"],
                     "LT": prefix + "-OT1", "LG": prefix + "-OG1", "C": prefix + "-C1", "RG": prefix + "-OG2",
                     "RT": prefix + "-OT2"}},
        {"side": "offense", "unit": "first offense, series 2", "until": {"possessions": 1, "snaps": 12},
         "players": {"QB": [prefix + "-QB1"], "WR": [prefix + "-WR3", prefix + "-WR2", prefix + "-WR4"],
                     "OL": [prefix + "-OT1", prefix + "-OG3", prefix + "-C1", prefix + "-OG2", prefix + "-OT2"]}},
        {"side": "offense", "unit": "second offense", "until": {"quarter": 3},
         "players": {"QB": [prefix + "-QB2"], "OL": [prefix + "-OT3", prefix + "-OG1", prefix + "-C2"]}},
        {"side": "offense", "unit": "reserves", "players": {"QB": [prefix + "-QB3"]}},
        {"side": "defense", "unit": "first defense", "until": {"quarter": 1, "possessions_after": 1},
         "players": {"DL": [prefix + "-DE1", prefix + "-DT1", prefix + "-DE2", prefix + "-DT2"]}},
        {"side": "defense", "unit": "second defense", "players": {"DL": [prefix + "-DE3", prefix + "-DT3"]}},
    )


class SeasonPathTests(unittest.TestCase):
    def test_fixtures_and_folders(self):
        paths = SeasonPaths(2014, ROOT)
        games = paths.preseason_games()
        self.assertEqual([g["game"] for g in games], [1, 2, 3, 4])
        self.assertEqual(games[0]["game_id"], EVENT)
        self.assertEqual(games[0]["date"], "2014-08-08")
        self.assertIsNone(games[3]["kickoff_et"])  # game 4 kickoff pending a dated notice
        self.assertEqual(paths.preseason_game(2)["home"], "Chicago Bears")
        base = paths.career / "04_Training_Camp_and_Preseason/Preseason_Games"
        self.assertEqual(paths.preseason_folder(1), base / "Game_01")
        self.assertEqual(paths.preseason_receipts, base / "statistics/records/game_receipts")
        self.assertEqual(paths.paused_game(1, preseason=True), base / "Game_01/paused_game.json")
        self.assertEqual(paths.paused_game(1), paths.regular_season / "Week_01" / "paused_game.json")
        self.assertEqual(paths.preseason_cache(1, "inputs"), ROOT / ".sim_cache/2014/preseason_01_inputs.json")
        with self.assertRaises(ValueError):
            paths.preseason_folder(0)
        with self.assertRaises(ValueError):
            paths.paused_game(1, postseason=True, preseason=True)
        # Preseason games 1 (August 8, 2014) and 2 (August 14, 2014) are closed: their receipts are
        # the only ones in the directory, and it stays apart from the regular-season and postseason sets.
        receipts = sorted(p.name for p in paths.preseason_receipts.glob('*.json'))
        self.assertEqual(receipts, ['preseason_01_tampa_bay_buccaneers_at_jacksonville_jaguars.json',
                                    'preseason_02_jacksonville_jaguars_at_chicago_bears.json'])
        self.assertNotEqual(paths.preseason_receipts, paths.receipts)


class ExtraPointRuleTests(unittest.TestCase):
    def teams(self):
        return club("A", "A"), club("B", "B")

    def test_rule_is_dated_and_preseason_only(self):
        self.assertEqual(extra_point_rule(PRESEASON, "2014-08-08")["distance"], 33)
        self.assertEqual(extra_point_rule(PRESEASON, "2014-08-14")["distance"], 33)
        self.assertEqual(extra_point_rule(PRESEASON, "2014-08-17")["distance"], 33)
        self.assertIsNone(extra_point_rule(PRESEASON, "2014-08-22")["distance"])
        self.assertIsNone(extra_point_rule(PRESEASON, "2015-08-08")["distance"])
        self.assertIsNone(extra_point_rule("regular", "2014-08-08"))
        self.assertIsNone(extra_point_rule("postseason", "2014-08-08"))
        self.assertEqual(active_limit(PRESEASON), 90)
        self.assertEqual(active_limit("regular"), 46)

    def test_kernel_applies_the_distance_on_august_8_and_not_on_august_22(self):
        a, b = self.teams()
        seed = hashlib.sha256(b"preseason-xp").digest()
        with patch.object(drive_model, "fg_make_prob_at", return_value=0.0):
            early = resolve_game(a, b, seed=seed, event_id="pre-1", game_type=PRESEASON, game_date="2014-08-08")
            late = resolve_game(a, b, seed=seed, event_id="pre-3", game_type=PRESEASON, game_date="2014-08-22")
        for result in (early, late):
            self.assertEqual(validate_result(result), [])
        self.assertEqual(early["extra_point_rule"]["snap_yard_line"], 15)
        self.assertEqual(early["game_date"], "2014-08-08")
        attempts = sum(s["extra_point_attempts"] for s in early["team_stats"].values())
        self.assertGreater(attempts, 0)
        self.assertEqual(sum(s["extra_points_made"] for s in early["team_stats"].values()), 0)
        self.assertEqual(late["extra_point_rule"]["snap_yard_line"], 2)
        self.assertGreater(sum(s["extra_points_made"] for s in late["team_stats"].values()), 0)
        regular = resolve_game(a, b, seed=seed, event_id="reg", game_type="regular")
        self.assertNotIn("extra_point_rule", regular)
        self.assertNotIn("game_date", regular)
        with self.assertRaises(ValueError):
            resolve_game(a, b, seed=seed, event_id="x", game_type="scrimmage")

    def test_packet_carries_the_date_only_for_a_dated_game(self):
        a, b = self.teams()
        plain = game_runner.build_game_packet("e", "snapshot!", a, b, game_type="regular")
        self.assertNotIn("game_date", plain)
        dated = game_runner.build_game_packet("e", "snapshot!", a, b, game_type=PRESEASON, game_date="2014-08-08")
        self.assertEqual(dated["game_date"], "2014-08-08")
        with self.assertRaises(ValueError):
            game_runner.build_game_packet("e", "snapshot!", a, b, game_type="scrimmage")


class PreseasonClosureTests(unittest.TestCase):
    """End to end against a temporary root: the real fixtures, synthetic clubs."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.paths = SeasonPaths(2014, root)
        folder = self.paths.preseason_folder(1)
        folder.mkdir(parents=True)
        shutil.copy(FIXTURES, self.paths.preseason_fixtures)
        (folder / "output.md").write_text("# Preseason game 1\n\nReport.\n", encoding="utf-8")
        self.paths.roster.parent.mkdir(parents=True)
        self.paths.roster.write_text("| Player | Pos | Status |\n| --- | --- | --- |\n"
                                     + "".join("| %s | %s | Offseason roster |\n" % (p.player_id, p.position)
                                               for p in game_day_roster("A")), encoding="utf-8")
        self.client = local_service(self, root / "private", self._testMethodName)[1]
        self.home = club(JAX, "A", third_quarterback=True)
        self.away = club(TB, "B")
        game = {"event_id": EVENT, "receipt": preseason.receipt_name(self.paths.preseason_game(1)), "week": 1,
                "preseason_game": 1, "date": "2014-08-08", "away": TB, "home": JAX, "venue": "home",
                "game_type": PRESEASON, "away_input": dataclasses.asdict(self.away),
                "home_input": dataclasses.asdict(self.home)}
        self.package = {"season": 2014, "preseason_game": 1, "week": 1, "game_type": PRESEASON, "games": [game]}
        self.results_path = self.paths.preseason_cache(1, "results")
        # The release gate reads the repository; the synthetic closure is isolated from it.
        patcher = patch.object(seasons, "require_game_release")
        patcher.start(); self.addCleanup(patcher.stop)

    def force_pause(self):
        packet = game_runner.build_game_packet(EVENT, "snapshot", self.home, self.away, game_type=PRESEASON,
                                               game_date="2014-08-08", management_mode="user_controlled")
        entropy = game_runner._entropy_from_ref(self.client.close_event(packet))
        base = kernel.resolve_game(self.home, self.away, seed=entropy, event_id=EVENT, game_type=PRESEASON,
                                   game_date="2014-08-08")
        drive = next(p["number"] for p in base["possessions"] if p["team"] == JAX)
        onsets = {(drive, "A-QB1"): {"injury_class": "lower_extremity", "severity": "multi_week", "removed": True}}

        def forced(home, away, **kwargs):
            return kernel.resolve_game(home, away, **kwargs, _test_onsets=dict(onsets))
        patcher = patch.object(game_runner, "resolve_game", forced)
        patcher.start(); self.addCleanup(patcher.stop)
        return drive

    def close(self, answer=None):
        with contextlib.redirect_stdout(io.StringIO()):
            return close_preseason_game.close_game(self.package, self.paths, "snapshot", self.client,
                                                   self.results_path, answer)

    def test_pause_continue_receipt_box_score_views_and_duplicate_refusal(self):
        drive = self.force_pause()
        result, paused = self.close()
        self.assertIsNone(result)
        record_path = self.paths.paused_game(1, preseason=True)
        self.assertEqual(record_path, self.paths.preseason_folder(1) / "paused_game.json")
        record = json.loads(record_path.read_text())
        self.assertEqual((record["status"], record["event_id"], record["pause"]["drive"]), ("paused", EVENT, drive))
        self.assertNotIn("final_score", json.dumps(record))
        self.assertFalse(self.results_path.exists())
        self.assertFalse(self.paths.preseason_receipts.exists())
        text = close_preseason_game.describe_pause(record, record_path, 1, 2014)
        self.assertIn("PRESEASON GAME 1 PAUSED", text)
        self.assertIn("close_preseason_game.py 1 --season 2014 --close --continue", text)
        # Stone answers; the same packet closes through the same event reference.
        choices = {d["slot"]: d["default"] for d in record["pause"]["decisions"]}
        result, still = self.close({"choices": choices})
        while still is not None:
            result, still = self.close({"choices": {d["slot"]: d["default"] for d in still["pause"]["decisions"]}})
        self.assertTrue(result["terminated"])
        self.assertEqual(result["game_type"], PRESEASON)
        self.assertEqual(result["extra_point_rule"]["distance"], 33)
        self.assertEqual(result["pauses"][0]["continuation_token"], record["pause"]["continuation_token"])
        self.assertEqual(json.loads(record_path.read_text())["status"], "closed")
        # A second close of the same event is refused, before any draw.
        with self.assertRaisesRegex(ValueError, "already closed"):
            self.close()

        receipt_path, output, views = close_preseason_game.finish(self.package, self.paths, result)
        self.assertEqual(receipt_path.parent, self.paths.preseason_receipts)
        self.assertEqual(receipt_path.name, "preseason_01_tampa_bay_buccaneers_at_jacksonville_jaguars.json")
        receipt = json.loads(receipt_path.read_text())
        self.assertEqual((receipt["detail"], receipt["season"], receipt["game_type"], receipt["preseason_game"]),
                         ("full", 2014, PRESEASON, 1))
        self.assertEqual(receipt["extra_point_rule"]["snap_yard_line"], 15)
        self.assertIn("play_ledger", receipt)
        self.assertEqual(receipt["final_score"], result["final_score"])
        # The box score is the 2014 gamebook, inside the marked block of Game_01/output.md.
        body = output.read_text()
        self.assertIn("<!-- box-score event=%s team=%s -->" % (EVENT, JAX), body)
        self.assertIn("Scoring summary", body)
        self.assertIn(JAX, body)
        from scripts.render_box_score import stale_blocks
        self.assertEqual(stale_blocks(output, self.paths.preseason_receipts, season=2014), [])
        # Preseason stat views, from the preseason receipts only, clearly labelled.
        self.assertEqual(set(views), set(render_preseason_stats.VIEW_FILES))
        stats_dir = self.paths.preseason_games_dir / "statistics"
        self.assertIn("PRESEASON ONLY", (stats_dir / "preseason_stats.md").read_text())
        self.assertIn("33-yard kick", (stats_dir / "preseason_stats.md").read_text())
        self.assertEqual(json.loads((stats_dir / "preseason_totals.json").read_text())["scope"], "preseason_only")
        self.assertEqual(render_preseason_stats.stale_views(self.paths), [])
        # Nothing regular-season exists: no receipts, no standings, no weekly folder.
        self.assertFalse(self.paths.receipts.exists())
        self.assertFalse(self.paths.postseason_receipts.exists())
        self.assertFalse(self.paths.regular_season.exists())
        self.assertFalse(self.paths.record("standings.md").exists())
        self.assertFalse(self.paths.stats.exists())
        # A receipt cannot be written twice either.
        with self.assertRaisesRegex(ValueError, "already exists"):
            close_preseason_game.write_receipt(self.package, self.paths, result)

    def test_rotation_plan_closes_through_the_service_and_the_receipt_records_it(self):
        self.home = club(JAX, "A", third_quarterback=True, plan=rotation_plan("A"))
        self.package["games"][0]["home_input"] = dataclasses.asdict(self.home)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(close_preseason_game.gate_errors(self.package, self.paths, 1), [])
        result, paused = self.close()
        self.assertIsNone(paused)
        self.assertTrue(result["terminated"])
        rotation = result["rotation"]
        self.assertEqual(rotation[JAX]["basis"], {"offense": "plan", "defense": "plan", "special_teams": "depth_order"})
        self.assertEqual(rotation[TB]["basis"]["offense"], "default")
        offense = rotation[JAX]["applied"]["offense"]
        self.assertEqual([e["unit"] for e in offense[:2]], ["first offense, series 1", "first offense, series 2"])
        self.assertEqual(offense[0]["lineup"]["OL"], ["A-OT1", "A-OG1", "A-C1", "A-OG2", "A-OT2"])
        self.assertEqual(offense[1]["lineup"]["OL"], ["A-OT1", "A-OG3", "A-C1", "A-OG2", "A-OT2"])
        self.assertEqual(offense[1]["lineup"]["WR"][:3], ["A-WR3", "A-WR2", "A-WR4"])
        self.assertEqual(offense[-1]["lineup"]["QB"], ["A-QB3"])
        lines = result["team_stats"][JAX]["players"]
        unit = sum(1 for r in result["play_ledger"] if r.get("offense") == JAX and r.get("play_type") in ("pass", "run"))
        self.assertGreater(lines["A-QB1"]["offensive_snaps"], 0)
        self.assertLess(lines["A-QB1"]["offensive_snaps"], unit)
        self.assertGreater(lines["A-QB2"]["offensive_snaps"], 0)
        receipt_path, output, views = close_preseason_game.finish(self.package, self.paths, result)
        receipt = json.loads(receipt_path.read_text())
        self.assertEqual(receipt["rotation"], rotation)
        self.assertEqual(receipt["rotation"][JAX]["blocks"]["offense"][1]["until"], {"possessions": 1, "snaps": 12})
        # The gamebook's snap counts show the starters' partial shares.
        body = output.read_text()
        counts = body[body.index("#### Snap counts"):]
        share = next(line for line in counts.splitlines() if line.startswith("| A-QB1 "))
        self.assertRegex(share.split("|")[3], r"\d+ \((\d|[1-9]\d)%\)")   # a partial offensive share
        self.assertIn("A-QB2", counts)
        from runtime.statbook import make_receipt
        regular_like = {k: v for k, v in result.items() if k != "rotation"}
        self.assertNotIn("rotation", make_receipt(regular_like, week=1, matchup="%s at %s" % (TB, JAX)))

    def test_gate_rejects_a_shared_player_and_accepts_a_full_preseason_roster(self):
        base = game_day_roster("A")
        big = tuple(base) + tuple(replace(p, player_id=p.player_id + "x", depth=p.depth + 10) for p in base[:43])
        home = TeamInput(JAX, tuple(p.player_id for p in big), roster=big, offensive_call_sheet=CALLS)
        self.package["games"][0]["home_input"] = dataclasses.asdict(home)
        self.assertEqual(len(home.active_players), 90)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(close_preseason_game.gate_errors(self.package, self.paths, 1), [])
        self.assertTrue(any("limit 46" in e for e in check_inputs(self.package, set(), JAX, expected_games=1)))
        self.assertTrue(any("package is for preseason game" in e
                            for e in close_preseason_game.gate_errors(self.package, self.paths, 2)))
        errors = check_inputs(self.package, {"B-QB1"}, JAX, expected_games=1, active_limit=90)
        self.assertTrue(any("Jacksonville-controlled player appears on" in e for e in errors))


class PreseasonBuilderTests(unittest.TestCase):
    """Jacksonville from the roster, a frozen depth chart and call sheet; the
    opponent from opponent_roster.json through the depth-library reader."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.paths = SeasonPaths(2014, root)
        folder = self.paths.preseason_folder(1)
        folder.mkdir(parents=True)
        shutil.copy(FIXTURES, self.paths.preseason_fixtures)
        jax = game_day_roster("A")
        self.paths.roster.parent.mkdir(parents=True)
        rows = ["| Player | Pos | DOB | Age | Status | Availability | Role |", "| --- | --- | --- | ---: | --- | --- | --- |"]
        for p in jax:
            status = "Offseason roster (signed 2014)" if p.depth > 1 else "Offseason roster"
            avail = "Out, projected return August 20, 2014" if p.player_id == "A-WR2" else "No communicated restriction"
            rows.append("| %s | %s | 1990-01-01 | 24 | %s | %s | Role not set |" % (p.player_id, p.position, status, avail))
        rows.append("| A-PS1 | WR | 1990-01-01 | 24 | Practice squad | No communicated restriction | — |")
        self.paths.roster.write_text("# Roster\n\n" + "\n".join(rows) + "\n", encoding="utf-8")
        depth = {}
        for p in jax:
            depth.setdefault(p.position, []).append(p.player_id)
        (folder / "depth_chart.json").write_text(json.dumps({
            "depth": depth, "positions": {p.player_id: p.position for p in jax},
            "roles": {"A-QB1": ["passer"]}, "game_day_inactives": {"players": ["A-S4"]}}))
        (folder / "call_sheet.json").write_text(json.dumps({"offensive_call_sheet": list(CALLS)}))
        opponent = {"code": "TB", "branch_changes": [], "notes": [], "players": [
            {"player_id": p.player_id, "position": p.position, "depth": p.depth} for p in game_day_roster("B")]}
        opponent["players"][0]["available"] = False  # out at the start of camp
        (folder / "opponent_roster.json").write_text(json.dumps(opponent))

    def test_package_from_the_frozen_files(self):
        with patch.object(preseason.strength, "team_strength", return_value=(None, {"players": {}})):
            package = preseason.build_package(self.paths, 1, [], with_ages=False)
        game = package["games"][0]
        self.assertEqual((game["event_id"], game["date"], game["game_type"]), (EVENT, "2014-08-08", PRESEASON))
        home, away = game["home_input"], game["away_input"]
        self.assertEqual(home["team_id"], JAX)
        self.assertNotIn("A-PS1", [p["player_id"] for p in home["roster"]])
        self.assertNotIn("A-S4", home["active_players"])      # Stone's inactive
        self.assertNotIn("A-WR2", home["active_players"])     # roster hold with a dated return
        self.assertIn("A-QB2", home["active_players"])
        self.assertEqual(home["offensive_call_sheet"], list(CALLS))
        self.assertEqual(away["team_id"], TB)
        self.assertNotIn("B-QB1", away["active_players"])
        self.assertIn("B-QB2", away["active_players"])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(close_preseason_game.gate_errors(package, self.paths, 1), [])
        # A player injured in an earlier closed preseason receipt stays out until his return.
        receipt = {"event_id": EVENT, "season": 2014, "week": 1, "game_type": PRESEASON,
                   "injuries": [{"player": "A-RB1", "restriction": "out", "injury_class": "lower_extremity", "return_days": 30},
                                {"player": "B-WR1", "restriction": "out", "injury_class": "upper_extremity", "return_days": 3}]}
        second = self.paths.preseason_folder(2)
        second.mkdir()
        for name in ("depth_chart.json", "call_sheet.json", "opponent_roster.json"):
            shutil.copy(self.paths.preseason_folder(1) / name, second / name)
        with patch.object(preseason.strength, "team_strength", return_value=(None, {"players": {}})):
            later = preseason.build_package(self.paths, 2, [receipt], with_ages=False)
        jacksonville, chicago = later["games"][0]["away_input"], later["games"][0]["home_input"]
        self.assertEqual((jacksonville["team_id"], chicago["team_id"]), (JAX, "Chicago Bears"))
        self.assertNotIn("A-RB1", jacksonville["active_players"])
        self.assertIn("B-WR1", chicago["active_players"])  # back by August 14
        self.assertEqual(later["games"][0]["event_id"], "2014-preseason-02-jacksonville-jaguars-at-chicago-bears")

    def test_rotation_files_enter_the_package_and_fail_closed(self):
        folder = self.paths.preseason_folder(1)
        # A-WR2 is held by his roster note and there is no A-QB3 on this roster: a dressed plan.
        plan = {"rotation_plan": [
            {"side": "offense", "unit": "first offense", "until": {"possessions": 2, "snaps": 12},
             "players": {"QB": ["A-QB1"], "WR": ["A-WR1", "A-WR3", "A-WR4"]}},
            {"side": "offense", "unit": "second offense", "players": {"QB": ["A-QB2"]}},
            {"side": "defense", "unit": "first defense", "until": {"quarter": 1, "possessions_after": 1},
             "players": {"DL": ["A-DE1", "A-DT1", "A-DE2", "A-DT2"]}},
            {"side": "defense", "unit": "second defense", "players": {"DL": ["A-DE3", "A-DT3"]}}]}
        (folder / "rotation.json").write_text(json.dumps(plan))
        opponent = json.loads((folder / "opponent_roster.json").read_text())
        opponent["rotation"] = [
            {"side": "offense", "unit": "first", "until": {"possessions": 2}, "players": {"QB": ["B-QB2"]}},
            {"side": "offense", "unit": "rest", "players": {"QB": ["B-QB2"]}}]
        (folder / "opponent_roster.json").write_text(json.dumps(opponent))
        with patch.object(preseason.strength, "team_strength", return_value=(None, {"players": {}})):
            package = preseason.build_package(self.paths, 1, [], with_ages=False)
        game = package["games"][0]
        self.assertEqual(game["rotation_basis"], {JAX: "plan", TB: "plan"})
        self.assertEqual(game["home_input"]["rotation_plan"], plan["rotation_plan"])
        self.assertEqual(game["away_input"]["rotation_plan"], opponent["rotation"])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(close_preseason_game.gate_errors(package, self.paths, 1), [])
        home = close_week.team_input(game["home_input"])
        self.assertEqual(len(home.rotation_plan), 4)
        # A plan naming a player off the game-day unit (B-QB1 is out) or an unknown group fails closed.
        opponent["rotation"][0]["players"]["QB"] = ["B-QB1"]
        (folder / "opponent_roster.json").write_text(json.dumps(opponent))
        with patch.object(preseason.strength, "team_strength", return_value=(None, {"players": {}})):
            with self.assertRaisesRegex(ValueError, "B-QB1 is not on the game-day unit"):
                preseason.build_package(self.paths, 1, [], with_ages=False)
        opponent["rotation"][0]["players"] = {"QB": ["B-QB2"], "NB": ["B-CB3"]}
        (folder / "opponent_roster.json").write_text(json.dumps(opponent))
        with patch.object(preseason.strength, "team_strength", return_value=(None, {"players": {}})):
            with self.assertRaisesRegex(ValueError, "unknown group 'NB'"):
                preseason.build_package(self.paths, 1, [], with_ages=False)
        (folder / "opponent_roster.json").write_text(json.dumps({k: v for k, v in opponent.items() if k != "rotation"}))
        plan["rotation_plan"][0]["players"]["WR"] = ["A-WR1", "A-WR3", "A-S4"]  # Stone's inactive
        (folder / "rotation.json").write_text(json.dumps(plan))
        with patch.object(preseason.strength, "team_strength", return_value=(None, {"players": {}})):
            with self.assertRaisesRegex(ValueError, "rotation.json.*A-S4 is not on the game-day unit"):
                preseason.build_package(self.paths, 1, [], with_ages=False)
        (folder / "rotation.json").write_text(json.dumps({"blocks": []}))
        with patch.object(preseason.strength, "team_strength", return_value=(None, {"players": {}})):
            with self.assertRaisesRegex(ValueError, "rotation_plan"):
                preseason.build_package(self.paths, 1, [], with_ages=False)
        (folder / "rotation.json").unlink()
        with patch.object(preseason.strength, "team_strength", return_value=(None, {"players": {}})):
            package = preseason.build_package(self.paths, 1, [], with_ages=False)
        self.assertEqual(package["games"][0]["rotation_basis"], {JAX: "default", TB: "default"})
        self.assertNotIn("rotation_plan", package["games"][0]["home_input"])

    def test_missing_inputs_fail_closed(self):
        folder = self.paths.preseason_folder(2)
        folder.mkdir()
        with self.assertRaisesRegex(ValueError, "No Jacksonville call sheet for preseason game 2"):
            preseason.build_package(self.paths, 2, [], with_ages=False)
        (folder / "call_sheet.json").write_text(json.dumps({"offensive_call_sheet": list(CALLS)}))
        with self.assertRaisesRegex(ValueError, "No depth chart for preseason game 2"):
            preseason.build_package(self.paths, 2, [], with_ages=False)


if __name__ == "__main__":
    unittest.main()
