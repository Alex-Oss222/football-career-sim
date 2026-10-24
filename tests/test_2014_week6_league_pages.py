"""A synthetic first close under the new system (rebuild step 4): the standings, statistics,
award and roster-moves pages after a fake 2014 Week 6, in a copy of the repository.

The real season is never touched. In a temporary copy, each Week 6 fixture gets a fake result:
a closed Week 5 game record of the latest week relabelled to the Week 6 clubs (Jacksonville's
own Week 5 game for Jacksonville's), with no injuries and no defensive call record. The week's
awards are recorded from their formula shortlists (the first finalist named, a fixture draw).
The rest of the week's close that other owners carry is stood in for: the week's open
decisions in the queue are settled as the user's (the Game Plan's apply step settles them in a
real week) and the roster record is dated to the game. The master date is left where it stands:
moving it is the event record's work, not these pages'. Every built page is then rebuilt by the
one command the weekly workflow runs (scripts/rebuild_pages.py). Each page the standings,
statistics, team tracker, award and roster-moves builders own must pass the clean-page check,
validation of the copy must add no error to the real checkout's, and the
figures the pages show come from the same arithmetic (the copy's standings and the statbook
agree on every club's record). Which week is the first new-system week is read from the stored
facts: the next week after the latest closed one.
"""
import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime import clean_pages
from runtime.player_pages import MARKERS
from runtime.seasons import SeasonPaths
from runtime.week_inputs import event_id, receipt_name
from scripts import league_awards, rebuild_pages, render_inseason_rails, render_season_stats, render_team_tracker
from scripts.validate_repository import validate

SEASON, JAX = 2014, "Jacksonville Jaguars"
IGNORED = (".git", ".sim_cache", "__pycache__", ".pytest_cache")


def next_week(paths):
    """The week after the latest closed regular-season week, from the stored game records."""
    closed = {int(r["week"]) for r in render_season_stats.load_receipts(paths.receipts)}
    return max(closed) + 1


def relabel(receipt, mapping):
    """A game record with its clubs renamed (old name -> new name), through placeholders so a
    club that is both renamed and a target is never renamed twice."""
    text = json.dumps(receipt)
    for index, old in enumerate(mapping):
        text = text.replace(json.dumps(old)[1:-1], "@@CLUB%d@@" % index)
    for index, new in enumerate(mapping.values()):
        text = text.replace("@@CLUB%d@@" % index, json.dumps(new)[1:-1])
    return json.loads(text)


def fake_week(paths, week):
    """Fake results for every fixture of ``week``: the latest closed week's game records,
    relabelled; Jacksonville's from its own game. Returns the records written."""
    closed = render_season_stats.load_receipts(paths.receipts)
    latest = max(int(r["week"]) for r in closed)
    sources = [r for r in closed if int(r["week"]) == latest]
    own = next(r for r in sources if JAX in r["team_stats"])
    others = [r for r in sources if r is not own]
    written = []
    for index, fixture in enumerate(sorted((g for g in paths.regular_games() if g["week"] == week),
                                           key=lambda g: g["game_id"])):
        if JAX in (fixture["away"], fixture["home"]):
            source = own
            opponent = next(t for t in own["team_stats"] if t != JAX)
            new_opponent = fixture["home"] if fixture["away"] == JAX else fixture["away"]
            mapping = {opponent: new_opponent}
        else:
            source = others[index % len(others)]
            mapping = {source["away"]: fixture["away"], source["home"]: fixture["home"]}
        receipt = relabel(copy.deepcopy(source), mapping)
        for key in ("defensive_calls", "play_ledger", "play_call_stats", "paused"):
            receipt.pop(key, None)
        receipt.update({"week": week, "event_id": event_id(fixture, season=SEASON), "away": fixture["away"],
                        "home": fixture["home"], "matchup": "%s at %s" % (fixture["away"], fixture["home"]),
                        "injuries": [], "detail": "compact_stats"})
        receipt["final_score"] = {team: receipt["team_stats"][team]["points"] for team in (fixture["away"], fixture["home"])}
        path = paths.receipts / receipt_name(fixture)
        path.write_text(json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        written.append(receipt)
    return written


def fake_awards(root, paths, week):
    """The week's awards from their formula shortlists, the first finalist named (a fixture)."""
    with mock.patch.object(league_awards, "ROOT", root):
        m = league_awards.method(SEASON)
        lists = league_awards.shortlists("week", week, m, SEASON)
    results_path = paths.awards_data / "results.json"
    results = json.loads(results_path.read_text(encoding="utf-8")) if results_path.exists() else {}
    results["week-%d" % week] = {
        "kind": "week", "key": str(week), "label": "Week %d" % week, "order": week, "note": "",
        "awards": {award: {"event_id": league_awards.event_id("week", week, award, m, SEASON),
                           "packet_sha256": "0" * 64, "result_ref": "synthetic", "shortlist": rows,
                           "winner_index": 0} for award, rows in lists.items()}}
    results_path.write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8")


def settle_the_rest(root, paths, week):
    """The parts of the week's close other owners carry, as fixtures: the week's open queue items
    settled as the user's, the roster record dated to Jacksonville's game."""
    from runtime import decision_queue
    queue_path = root / decision_queue.QUEUE
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    raised = None
    for item in queue["items"]:
        if item["status"] == "OPEN" and any(b.get("season") == SEASON and b.get("week") == week
                                            for b in item.get("blocks") or ()):
            raised = item["raised"]["date"]
            item["status"] = "RESOLVED"
            item["resolution"] = {"date": raised, "by": "user", "record": item["record"],
                                  "summary": "Synthetic fixture: settled for the test of the league pages."}
    queue_path.write_text(json.dumps(queue, indent=1) + "\n", encoding="utf-8")
    game = next(g for g in paths.regular_games() if g["week"] == week and JAX in (g["away"], g["home"]))
    roster = json.loads(paths.roster.read_text(encoding="utf-8"))
    roster["as_of"] = {"date": game["date"], "event": "after the synthetic Week %d game" % week}
    paths.roster.write_text(json.dumps(roster, indent=1) + "\n", encoding="utf-8")
    return raised


class Week6LeaguePagesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT.parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(*IGNORED), symlinks=True)
        self.paths = SeasonPaths(SEASON, self.root)
        self.real_receipts = sorted(p.name for p in SeasonPaths(SEASON, ROOT).receipts.glob("*.json"))

    def rebuild(self, week):
        """Every built page, by the one command; returns the pages the five builders own."""
        root, paths = self.root, self.paths
        written, problems = rebuild_pages.rebuild(root, SEASON)
        self.assertEqual(problems, [])
        self.assertEqual(rebuild_pages.rebuild(root, SEASON, check=True), ([], []))
        receipts = render_season_stats.load_receipts(paths.receipts)
        pages = [paths.record("standings.md")]
        pages += [render_season_stats.view_path(paths, name)
                  for name in render_season_stats.render_views(SEASON, JAX, receipts, root)]
        tracker = render_team_tracker.tracker_dir(root, SEASON)
        pages += [tracker / rel for rel in render_team_tracker.render(root, SEASON, JAX)]
        with mock.patch.object(league_awards, "ROOT", root):
            from scripts.render_award_pages import render_pages
            drawn = render_pages(SEASON, league_awards.load_results(SEASON), league_awards.method(SEASON), root=root)
        pages += [paths.awards / rel for rel in sorted(drawn)]
        pages.append(render_inseason_rails.page_path(SEASON, week, root))
        for path in pages:
            self.assertTrue(path.is_file(), path)
        return [p for p in pages if p.suffix == ".md" and p.is_relative_to(root / "career")]

    def test_the_first_new_system_week_closes_with_clean_league_pages(self):
        root, paths = self.root, self.paths
        week = next_week(paths)
        fixtures = [g for g in paths.regular_games() if g["week"] == week]
        self.assertTrue(fixtures)
        written = fake_week(paths, week)
        self.assertEqual(len(written), len(fixtures))
        self.assertEqual(sum(JAX in r["team_stats"] for r in written), 1)
        fake_awards(root, paths, week)
        settle_the_rest(root, paths, week)

        pages = self.rebuild(week)

        # Every page the builders wrote is clean, the weeks before the new system included.
        rels = sorted(p.relative_to(root).as_posix() for p in pages)
        self.assertIn(paths.record("standings.md").relative_to(root).as_posix(), rels)
        self.assertIn(render_inseason_rails.page_path(SEASON, week, root).relative_to(root).as_posix(), rels)
        problems = []
        for path in pages:
            problems += clean_pages.page_errors(path.relative_to(root).as_posix(), path.read_text(encoding="utf-8"),
                                                MARKERS, root)
        self.assertEqual(problems, [])
        checked = {rel for rel, _, _ in clean_pages.checked_parts(root)}
        self.assertTrue(set(rels) <= checked)  # rebuilt pages are checked pages, never exempt history
        self.assertEqual([e for e in clean_pages.clean_errors(root) if e.split(":")[0] in set(rels)], [])

        # The pages show the new week from the same arithmetic.
        standings = paths.record("standings.md").read_text(encoding="utf-8")
        self.assertIn("**Through:** Week %d." % week, standings)
        receipts = render_season_stats.load_receipts(paths.receipts)
        from runtime.standings import compute
        result = compute(receipts)
        line = result["lines"][JAX].overall
        self.assertIn("| **%s** | %d | %d | %d |" % (JAX, line.wins, line.losses, line.ties), standings)
        statbook = render_season_stats.view_path(paths, render_season_stats.STATBOOK).read_text(encoding="utf-8")
        self.assertIn("**Through Week %d.** Every closed game is counted (%d games)." % (week, len(receipts)), statbook)
        tracker = (render_team_tracker.tracker_dir(root, SEASON) / "README.md").read_text(encoding="utf-8")
        self.assertIn("| Regular-season record | %d-%d" % (line.wins, line.losses), tracker)
        week_page = (paths.awards / ("week_%02d" % week) / "README.md").read_text(encoding="utf-8")
        self.assertIn("# Week %d Players of the Week" % week, week_page)
        self.assertTrue(render_season_stats.view_path(paths, "calibration_audit.md").is_relative_to(root / "data"))
        self.assertTrue(render_inseason_rails.meta_path(SEASON, week, root).is_file())
        self.assertEqual(render_inseason_rails.check(SEASON, root), [])
        self.assertEqual(render_team_tracker.check(root, SEASON), [])

        # Validation of the copy adds no error to the real checkout's (the copy has no git
        # history; whatever the checkout already reports is the baseline).
        # The week's Game Report is another owner's work in a real close (written from the game
        # after it, its sections 1 and 2 frozen before it); a report opened before the faked game
        # is left as it stands, so its own checks of a played game are not these pages' errors.
        baseline = set(validate(ROOT))
        report = paths.game_report(week).relative_to(root).as_posix()
        errors = [e for e in validate(root) if not e.startswith(report + ":")]
        self.assertEqual(sorted(set(errors) - baseline), [])

        # Isolation: the real season's game records are untouched.
        self.assertEqual(sorted(p.name for p in SeasonPaths(SEASON, ROOT).receipts.glob("*.json")), self.real_receipts)


if __name__ == "__main__":
    unittest.main()
