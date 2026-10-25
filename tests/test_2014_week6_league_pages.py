"""A synthetic first close under the new system (rebuild step 4): the standings, statistics,
award and roster-moves pages after a fake 2014 Week 6, in a copy of the repository.

The real season is never touched. In a temporary copy, each fixture of the week gets a fake
result, game for game: Jacksonville's last closed game relabelled to Jacksonville's fixture (a
bye between them changes nothing), the other fixtures from the latest closed week's other games,
each moved once (then the week's before it, when the latest has fewer), relabelled to the week's
clubs, with no injuries and no defensive call record. In Jacksonville's bye only the other clubs'
games close. The week's awards are recorded from their formula shortlists (the first finalist
named, a fixture draw), with each month's whose weeks all precede the week and that has none
yet, as the close draws them. The rest of the week's close that other owners carry is stood in
for: the week's open decisions holding its games are settled as the user's (the Game Plan's
apply step settles them in a real week; the bye's adjustments hold only the bye's own close and
stay open, as at its slate's close), the roster record is dated to Jacksonville's game when the
week has one, and the week's practice record, when the copy does not hold it yet, is written as
the practice-week commit writes it (a bye's is written at the bye's own close). The master date is left where it stands: moving it is
the event record's work, not these pages'. Every built page is then rebuilt by the
one command the weekly workflow runs (scripts/rebuild_pages.py). Each page the standings,
statistics, team tracker, award and roster-moves builders own must pass the clean-page check,
validation of the copy must add no error to the real checkout's, and the
figures the pages show come from the same arithmetic (the copy's standings and the statbook
agree on every club's record). Which week is closed is read from the stored facts: the next week
after the latest closed one; once the regular season is complete, its last week, closed again
from its own game records with what its close recorded, so the season after it (the postseason
built on the final standings) stands as recorded.
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

from runtime import clean_pages, decision_queue, practices
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


def subject_week(paths):
    """(week, again): the week this test closes in its copy, the next week after the latest closed
    one; once every regular-season week has closed, the last one, closed again (``again``) from its
    own game records."""
    last = max(int(g["week"]) for g in paths.regular_games())
    week = next_week(paths)
    return (week, False) if week <= last else (last, True)


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
    """Fake results for every fixture of ``week``, game for game, relabelled: Jacksonville's from
    its last closed game (a bye between them changes nothing), the others from the latest closed
    week's other games, each moved once, then the week's before it when the latest has fewer.
    Returns the records written."""
    closed = render_season_stats.load_receipts(paths.receipts)
    own = max((r for r in closed if JAX in r["team_stats"]), key=lambda r: int(r["week"]))
    others = iter(sorted((r for r in closed if JAX not in r["team_stats"]), key=lambda r: -int(r["week"])))
    written = []
    for fixture in sorted((g for g in paths.regular_games() if g["week"] == week), key=lambda g: g["game_id"]):
        if JAX in (fixture["away"], fixture["home"]):
            source = own
            opponent = next(t for t in own["team_stats"] if t != JAX)
            new_opponent = fixture["home"] if fixture["away"] == JAX else fixture["away"]
            mapping = {opponent: new_opponent}
        else:
            source = next(others)
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
    """The awards the week's close draws, from their formula shortlists, the first finalist named (a
    fixture), in the entries scripts/league_awards.py writes: the week's, and each month's whose
    weeks all precede it (the rule scripts/validate_repository.award_coverage_errors checks), each
    when it has none yet."""
    results_path = paths.awards_data / "results.json"
    results = json.loads(results_path.read_text(encoding="utf-8")) if results_path.exists() else {}

    def entry(kind, key, m):
        lists = league_awards.shortlists(kind, key, m, SEASON)
        return {"kind": kind, "key": str(key),
                "label": ("Week %d" % key) if kind == "week" else m["months"][key]["label"],
                "order": key if kind == "week" else 100 + m["months"][key]["order"], "note": "",
                "awards": {award: {"event_id": league_awards.event_id(kind, key, award, m, SEASON),
                                   "packet_sha256": "0" * 64, "result_ref": "synthetic", "shortlist": rows,
                                   "winner_index": 0} for award, rows in lists.items()}}

    with mock.patch.object(league_awards, "ROOT", root):
        m = league_awards.method(SEASON)
        if "week-%d" % week not in results:
            results["week-%d" % week] = entry("week", week, m)
        for name, month in (m.get("months") or {}).items():
            if max(month["weeks"]) < week and "month-%s" % name not in results:
                results["month-%s" % name] = entry("month", name, m)
    results_path.write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8")


def settle_the_rest(root, paths, week):
    """The parts of the week's close other owners carry, as fixtures: the week's open queue items
    that hold its games (decision_queue.WEEK_KINDS) settled as the user's, as the Game Plan's apply
    settles them (the bye's adjustments hold only the bye's own close and stay open), and the
    roster record dated to Jacksonville's game when the week has one and the record is dated
    before it."""
    queue_path = root / decision_queue.QUEUE
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    raised = None
    for item in queue["items"]:
        if item["status"] == "OPEN" and any(b.get("kind") in decision_queue.WEEK_KINDS and b.get("season") == SEASON
                                            and b.get("week") == week for b in item.get("blocks") or ()):
            raised = item["raised"]["date"]
            item["status"] = "RESOLVED"
            item["resolution"] = {"date": raised, "by": "user", "record": item["record"],
                                  "summary": "Synthetic fixture: settled for the test of the league pages."}
    queue_path.write_text(json.dumps(queue, indent=1) + "\n", encoding="utf-8")
    game = next((g for g in paths.regular_games() if g["week"] == week and JAX in (g["away"], g["home"])), None)
    roster = json.loads(paths.roster.read_text(encoding="utf-8"))
    if game is not None and roster["as_of"]["date"] < game["date"]:
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
        week, again = subject_week(paths)
        fixtures = [g for g in paths.regular_games() if g["week"] == week]
        self.assertTrue(fixtures)
        if again:
            # The regular season is complete: its last week closes again from its own game records.
            written = [r for r in render_season_stats.load_receipts(paths.receipts) if int(r["week"]) == week]
        else:
            written = fake_week(paths, week)
        self.assertEqual(len(written), len(fixtures))
        # Jacksonville's one game of the week, none in its bye.
        ours = [g for g in fixtures if JAX in (g["away"], g["home"])]
        self.assertEqual(len(ours), 0 if practices.is_bye(SEASON, week, root) else 1)
        self.assertEqual(sum(JAX in r["team_stats"] for r in written), len(ours))
        fake_awards(root, paths, week)
        settle_the_rest(root, paths, week)
        # The week's practice record, as the practice-week commit writes it before the game (a bye's
        # is written at the bye's own close; a week whose record is held keeps it as recorded).
        from test_week_close_pages import check_head_coaches, record_practice
        if ours and practices.load(SEASON, week, root) is None:
            record_practice(self, root, week)
        # The weekly head-coach check, after the slate closes and before the rebuild opens the next week.
        from local_private_service import local_service
        _, client = local_service(self, Path(self.tmp.name) / "private", "week-league-pages")
        check_head_coaches(self, root, week, client)

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
        # after it, its pregame sections frozen before it); a report opened before the faked game
        # is left as it stands, so its own checks of a played game are not these pages' errors.
        baseline = set(validate(ROOT))
        report = paths.game_report(week).relative_to(root).as_posix()
        errors = [e for e in validate(root) if not e.startswith(report + ":")]
        self.assertEqual(sorted(set(errors) - baseline), [])

        # Isolation: the real season's game records are untouched.
        self.assertEqual(sorted(p.name for p in SeasonPaths(SEASON, ROOT).receipts.glob("*.json")), self.real_receipts)


if __name__ == "__main__":
    unittest.main()
