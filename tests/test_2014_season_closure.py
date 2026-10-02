"""Isolated 2014 end-to-end closure acceptance (season release gate `season_closure`).

One complete synthetic Week 1 slate, the sixteen real 2014 fixtures with
synthetic depth-ordered rosters, closes through scripts/close_week.py's own
functions (Jacksonville first under user control, the rest as a batch) against
a copy of the repository in a temporary root and a local private service with
a pinned store seed. Every dependent view is then generated the way the weekly
workflow generates it (receipts, statbook, standings, gamebook box score,
award pages, team tracker, player cards) and the repository validator runs on
that temporary root. The real career tree, cache and live service are never
touched; the real repository's own release gates are not consulted for the
draw, the temporary root's are. No 2014 career game runs.
"""
import contextlib
import dataclasses
import hashlib
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import KERNEL_VERSION, seasons
from runtime.kernel import TeamInput, validate_result
from runtime.seasons import SeasonPaths, game_release_errors
from runtime.week_inputs import event_id, receipt_name
from scripts import (close_week, league_awards, render_box_score, render_season_stats,
                     render_standings, render_team_tracker, update_player_cards)
from scripts.validate_repository import validate
from local_private_service import local_service
from support_rosters import game_day_roster

JAX = close_week.PROTAGONIST
SEASON, WEEK = 2014, 1
IGNORED = (".git", ".sim_cache", "__pycache__", ".pytest_cache")


def club(team_id, prefix):
    """A legal 46-player game-day unit (support_rosters has 47; drop the fifth receiver)."""
    roster = tuple(p for p in game_day_roster(prefix) if p.player_id != prefix + "-WR5")
    return TeamInput(team_id, tuple(p.player_id for p in roster), roster=roster)


def weekly_package(paths):
    games = []
    fixtures = [g for g in paths.regular_games() if g["week"] == WEEK]
    for index, fixture in enumerate(fixtures, 1):
        away = club(fixture["away"], "A%02d" % index)
        home = club(fixture["home"], "H%02d" % index)
        games.append({"event_id": event_id(fixture, generation=1, season=SEASON),
                      "receipt": receipt_name(fixture), "week": WEEK,
                      "away": away.team_id, "home": home.team_id, "venue": "home",
                      "game_type": "regular",
                      "away_input": dataclasses.asdict(away), "home_input": dataclasses.asdict(home)})
    return {"season": SEASON, "week": WEEK, "games": games}


def accept_release(root):
    """The temporary root's own release record: every gate VERIFIED on existing
    evidence, the installed kernel accepted, and a synthetic game depth chart."""
    path = root / "runtime/season_readiness.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    release = data["seasons"][str(SEASON)]
    release["accepted_kernel"] = KERNEL_VERSION
    for gate in release["gates"]:
        gate["status"] = "VERIFIED"
        gate["remaining"] = "Synthetic acceptance fixture (tests/test_2014_season_closure.py)"
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    depth = SeasonPaths(SEASON, root).depth_chart
    depth.parent.mkdir(parents=True, exist_ok=True)
    # A synthetic game depth chart in the working chart's shape (depth order
    # keyed by group); the synthetic slate draws its own rosters, so no
    # branch player is placed here.
    depth.write_text(json.dumps({"team": JAX, "season": SEASON, "status": "synthetic acceptance fixture",
                                 "effective": "tests/test_2014_season_closure.py", "depth": {},
                                 "game_day_inactives": []}), encoding="utf-8")


class SeasonClosure2014Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT.parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(*IGNORED), symlinks=True)
        accept_release(self.root)
        self.paths = SeasonPaths(SEASON, self.root)
        # The copied root carries whatever the real season has already closed
        # and drawn. The synthetic slate is a Week 1 of its own: it overwrites
        # the real Week 1 receipts and redraws the Week 1 awards from scratch,
        # while every later real week (receipts, outputs and awards) stays in
        # the copy exactly as the real season closed it.
        results = self.paths.awards / "results.json"
        if results.exists():
            drawn = json.loads(results.read_text(encoding="utf-8"))
            drawn.pop("week-%d" % WEEK, None)
            if drawn:
                results.write_text(json.dumps(drawn, indent=2) + "\n", encoding="utf-8")
            else:
                results.unlink()
        shutil.rmtree(self.paths.awards / ("week_%02d" % WEEK), ignore_errors=True)
        self.real = SeasonPaths(SEASON, ROOT)
        self.real_files = sorted(p for p in (ROOT / "career" / str(SEASON)).rglob("*.json"))
        real_cache = self.real.cache(WEEK, "results")
        self.real_cache_before = real_cache.read_bytes() if real_cache.exists() else None

    def close_slate(self, package, snapshot, client):
        results_path = self.paths.cache(WEEK, "results")
        with contextlib.redirect_stdout(io.StringIO()):
            results, paused = close_week.close_slate(package, self.paths, snapshot, client, results_path)
            while paused is not None:  # consequential Jacksonville removals: the depth default
                defaults = {d["slot"]: d["default"] for d in paused["pause"]["decisions"]}
                results, paused = close_week.close_slate(package, self.paths, snapshot, client,
                                                         results_path, {"choices": defaults})
        return results

    def test_full_week_closes_and_validates_on_the_isolated_root(self):
        root, paths = self.root, self.paths
        self.assertEqual(game_release_errors(SEASON, root), [])
        package = weekly_package(paths)
        self.assertEqual(len(package["games"]), 16)
        self.assertEqual(sum(JAX in (g["away"], g["home"]) for g in package["games"]), 1)
        snapshot = hashlib.sha256((root / "state/05_Current_Season_State.md").read_bytes()).hexdigest()
        _, client = local_service(self, root / "private", "season-closure-2014", snapshot=snapshot)

        # The production runner checks the season release of the root it runs
        # in: here the temporary root's accepted record, never the real one.
        original = seasons.require_game_release
        with patch.object(seasons, "require_game_release", lambda season, r=root, **kw: original(season, r, **kw)):
            results = self.close_slate(package, snapshot, client)

        self.assertEqual(set(results), {g["event_id"] for g in package["games"]})
        for event, result in results.items():
            self.assertTrue(result["terminated"], event)
            self.assertEqual(validate_result(result), [], event)
            self.assertTrue(event.startswith("2014-week01-"), event)
        self.assertTrue(paths.cache(WEEK, "results").is_relative_to(root))

        # Receipts: full for Jacksonville, compact for the other fifteen games.
        receipts_dir = close_week.write_receipts(package, paths, results, SEASON)
        self.assertEqual(receipts_dir, paths.receipts)
        self.assertEqual(receipts_dir, root / "career/2014/05_Regular_Season/Statistics/records/game_receipts")
        written = sorted(p.name for p in receipts_dir.glob("week_%02d_*.json" % WEEK))
        self.assertEqual(written, sorted(g["receipt"] for g in package["games"]))
        own = json.loads((receipts_dir / "week_01_jacksonville_jaguars_at_philadelphia_eagles.json").read_text())
        self.assertEqual((own["season"], own["week"]), (SEASON, WEEK))
        self.assertIn("play_ledger", own)
        other = json.loads((receipts_dir / "week_01_green_bay_packers_at_seattle_seahawks.json").read_text())
        self.assertEqual(other["season"], SEASON)
        self.assertNotIn("play_ledger", other)

        # Every generated view, as the weekly workflow generates it.
        regular = render_season_stats.load_receipts(paths.receipts)
        views = render_season_stats.render_views(SEASON, JAX, regular)
        paths.stats.mkdir(parents=True, exist_ok=True)
        for name, text in views.items():
            (paths.stats / name).write_text(text, encoding="utf-8")
        self.assertTrue((root / "career/2014/05_Regular_Season/Statistics/records/season_totals.json").is_file())
        standings = paths.record("standings.md")
        standings.write_text(render_standings.render(SEASON, regular), encoding="utf-8")
        self.assertEqual(standings, root / "career/2014/05_Regular_Season/standings.md")
        self.assertRegex(standings.read_text(encoding="utf-8"), r"\*\*Through:\*\* Week \d+\.")

        week_dir = paths.week_folder(WEEK)
        self.assertEqual(week_dir, root / "career/2014/05_Regular_Season/Games/Week_01")
        output = week_dir / "output.md"
        markers = "<!-- box-score event=%s team=%s -->\n<!-- /box-score -->\n" % (own["event_id"], JAX)
        if output.is_file():
            # The real week file carries either the template's placeholder
            # markers (preparation closed, game unplayed) or, once the real
            # week has closed, the filled block; either way the box score
            # fills the markers and the file's own history stays intact.
            shell = output.read_text(encoding="utf-8")
            placeholder = "<!-- box-score event=[event id] team=%s -->\n\n<!-- /box-score -->\n" % JAX
            filled = re.compile(r"<!-- box-score event=\S+ team=%s -->\n.*?<!-- /box-score -->\n" % re.escape(JAX), re.S)
            if placeholder in shell:
                shell = shell.replace(placeholder, markers)
            else:
                self.assertRegex(shell, filled)
                shell = filled.sub(lambda _: markers, shell, count=1)
        else:
            shell = "# Week 1 synthetic closure output\n\nFull stats for the game.\n\n" + markers
        output.write_text(render_box_score.fill(shell, paths.receipts, SEASON), encoding="utf-8")
        self.assertEqual(render_box_score.stale_blocks(output, paths.receipts, season=SEASON), [])
        self.assertIn("Scoring", output.read_text(encoding="utf-8"))

        # The week's awards, drawn through the same local service from the
        # frozen 2014 methodology (the root's own copy), then rendered.
        with patch.object(league_awards, "ROOT", root), \
                patch("runtime.private_client.Client", return_value=client), \
                patch.object(sys, "argv", ["league_awards", "week", str(WEEK), "--season", str(SEASON), "--close"]), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(league_awards.main(), 0)
        drawn = json.loads((paths.awards / "results.json").read_text(encoding="utf-8"))
        self.assertIn("week-1", drawn)  # later real weeks' draws stay in the copy
        self.assertEqual(len(drawn["week-1"]["awards"]), 6)
        self.assertTrue(all(a["event_id"].startswith("2014-award-week01-") for a in drawn["week-1"]["awards"].values()))
        self.assertEqual(paths.awards, root / "career/2014/05_Regular_Season/Awards")
        self.assertTrue((paths.awards / "week_01/README.md").is_file())
        real_results = self.real.awards / "results.json"
        if real_results.exists():  # the real season's draws are untouched
            self.assertNotEqual(json.loads(real_results.read_text(encoding="utf-8")), drawn)

        tracker = render_team_tracker.tracker_dir(root, SEASON)
        for rel, text in render_team_tracker.render(root, SEASON, JAX).items():
            (tracker / rel).parent.mkdir(parents=True, exist_ok=True)
            (tracker / rel).write_text(text, encoding="utf-8")
        self.assertEqual(update_player_cards.refresh_cards(SEASON, root), [])

        # The repository validator accepts the closed, regenerated temporary
        # root. A checkout mid-edit may already carry continuity errors of its
        # own (an unreceipted phase summary, say); those are the baseline, and
        # the closure must add none and none may concern the season records.
        baseline = set(validate(ROOT))
        errors = validate(root)
        self.assertEqual(sorted(set(errors) - baseline), [])

        # Isolation: nothing reached the real season tree, cache or receipts.
        self.assertEqual(sorted(p for p in (ROOT / "career" / str(SEASON)).rglob("*.json")), self.real_files)
        self.assertEqual(sorted(self.real.receipts.glob("*.json")), [p for p in self.real_files if p.parent == self.real.receipts])
        real_cache = self.real.cache(WEEK, "results")  # the real workspace is untouched
        self.assertEqual(real_cache.read_bytes() if real_cache.exists() else None, self.real_cache_before)


if __name__ == "__main__":
    unittest.main()
