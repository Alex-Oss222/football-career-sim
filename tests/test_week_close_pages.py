"""A synthetic Week 6 close in a temporary copy (rebuild step 4, builder B).

The pages a game week's close rewrites on the result side are built from their
stored owners and pass the clean-page rule: the Game Report's generated box
score, the annual record, the Games and league-results indexes and week page,
the injury report, the medical history's game entry and the incident records
it opens (scripts/render_week_pages.py, scripts/render_annual_record.py,
scripts/render_box_score.py).

The fake result: the copy's first post-history week (the first Game Report
week) is closed by relabelling the copy's previous week's closed games onto
that week's fixtures, game for game, Jacksonville's on Jacksonville's: the
same scores and statistics, the same injuries, now in the new week. The
master date and the roster record move to the new game day, as the week's
close moves them, with each newly injured player's medical instruction. The
statistics, standings, award and club views the close also rewrites are
rebuilt by their own builders; the pages those other builders own are kept as
history in the copy (support_page_history), because cleaning them is another
builder's work. Then repository validation adds no error and the clean-page
check passes. No game is played and the real repository is never touched.
"""
import contextlib
import hashlib
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import clean_pages, events, player_pages, week_pages  # noqa: E402
from runtime.roster import load as load_roster  # noqa: E402
from runtime.season_layout import PAGE_HISTORY  # noqa: E402
from runtime.seasons import GAME_REPORT, GAME_REPORT_FROM, SeasonPaths  # noqa: E402
from runtime.week_inputs import event_id, receipt_name  # noqa: E402
from scripts import (league_awards, render_box_score, render_season_stats, render_standings,  # noqa: E402
                     render_team_tracker, render_week_pages)
from scripts.validate_repository import validate  # noqa: E402
from local_private_service import local_service  # noqa: E402
from support_page_history import keep_as_history, pinned_copy  # noqa: E402

JAX = "Jacksonville Jaguars"
SEASON, WEEK = GAME_REPORT_FROM
IGNORED = (".git", ".sim_cache", "__pycache__", ".pytest_cache")
# The receipt fields tied to the week a game was played under: the defensive call record names that
# week's committed sheet, and the decision policies its standing rules.
WEEK_BOUND = ("defensive_calls", "defensive_call_stats", "decision_policies")


def relabel(value, names):
    """``value`` with every string equal to a key of ``names`` (a club) replaced, at any depth."""
    if isinstance(value, dict):
        return {relabel(k, names): relabel(v, names) for k, v in value.items()}
    if isinstance(value, list):
        return [relabel(v, names) for v in value]
    if isinstance(value, str):
        return names.get(value, value)
    return value


def ours_first(games):
    return sorted(games, key=lambda g: (JAX not in (g["away"], g["home"]), g["away"]))


class WeekClosePagesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT.parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(*IGNORED), symlinks=True)
        self.paths = SeasonPaths(SEASON, self.root)
        self.real = sorted(p.name for p in SeasonPaths(SEASON, ROOT).receipts.glob("*.json"))

    def fake_week(self):
        """Close the week in the copy from the previous week's games; returns Jacksonville's receipt."""
        paths = self.paths
        fixtures = paths.regular_games()
        new = ours_first(g for g in fixtures if g["week"] == WEEK)
        old = ours_first(g for g in fixtures if g["week"] == WEEK - 1)
        self.assertEqual(len(new), len(old))
        self.assertFalse(list(paths.receipts.glob("week_%02d_*.json" % WEEK)), "the week is already closed")
        ours = None
        for before, after in zip(old, new):
            receipt = json.loads((paths.receipts / receipt_name(before)).read_text(encoding="utf-8"))
            # The previous week's away club becomes the new away club, its home club the new home club.
            names = {before["away"]: after["away"], before["home"]: after["home"]}
            if JAX in (before["away"], before["home"]):  # Jacksonville stays Jacksonville
                other = before["home"] if before["away"] == JAX else before["away"]
                names = {other: after["home"] if after["away"] == JAX else after["away"]}
            receipt = relabel(receipt, names)
            for key in WEEK_BOUND:
                receipt.pop(key, None)
            receipt.update({"week": WEEK, "away": after["away"], "home": after["home"],
                            "matchup": "%s at %s" % (after["away"], after["home"]),
                            "event_id": event_id(after, season=SEASON)})
            if JAX in (after["away"], after["home"]):
                # Swapping the sides: the score and statistics stay with their clubs.
                ours = receipt
            (paths.receipts / receipt_name(after)).write_text(json.dumps(receipt, indent=1), encoding="utf-8")
        return ours

    def move_clock(self, receipt):
        """The master date and the roster record to the game day, each new injury's instruction on it."""
        played = date.fromisoformat(next(g for g in self.paths.regular_games()
                                         if g["week"] == WEEK and JAX in (g["away"], g["home"]))["date"])
        state = self.root / "state/05_Current_Season_State.md"
        text = state.read_text(encoding="utf-8")
        text, n = re.subn(r"(\| Master date/time \| )[A-Za-z]+ \d{1,2}, \d{4}[^|]*\|",
                          r"\g<1>%s, after the Week %d game |" % (week_pages.long_date(played), WEEK), text, count=1)
        self.assertEqual(n, 1)
        state.write_text(text, encoding="utf-8")
        roster = self.paths.roster
        data = json.loads(roster.read_text(encoding="utf-8"))
        data["as_of"] = {"date": played.isoformat(), "event": "after the Week %d game" % WEEK}
        page = self.paths.roster_page.relative_to(self.root).as_posix()
        injured = [i for i in receipt["injuries"] if i.get("team") == JAX]
        self.assertTrue(injured, "the fake week carries no Jacksonville injury")
        for injury in injured:
            row = next(p for p in data["players"] if p["name"] == injury["player"])
            incident = self.paths.record("medical/incidents/%s_%s.md" % (
                week_pages.people.slugify(injury["player"]), played.isoformat())).relative_to(self.root).as_posix()
            row["availability"] = "%s, %s: %s; projected return %s ([medical record](%s))" % (
                injury["restriction"].capitalize(), injury["severity"], week_pages.injury_words(injury).split(",")[0],
                week_pages.long_date(played + timedelta(days=injury["return_days"])),
                week_pages.relative(page, incident))
        roster.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        return played

    def write_report(self, receipt):
        """The week's Game Report: a clean shell, its event line and the generated box score."""
        report = self.paths.game_report(WEEK)
        self.assertEqual(report.name, GAME_REPORT)
        checkpoint = "Canonical update - %s - Week %d closed" % (week_pages.long_date(self.played), WEEK)
        sequence = max(item["sequence"] for _, _, item in events.closures(events.load_events(self.root))) + 1
        event = {"date": self.played.isoformat(), "id": "%s-week-%d-game" % (self.played.isoformat(), WEEK),
                 "status": "closed", "summary": "%s in the Week %d game." % (week_pages.score_line(receipt), WEEK),
                 "closure": {"checkpoint": checkpoint, "through": self.played.isoformat(), "sequence": sequence}}
        state = self.root / "state/05_Current_Season_State.md"
        text, n = re.subn(r"^(\*\*Global package checkpoint:\*\* `)[^`]+(`)", r"\g<1>%s\g<2>" % checkpoint,
                          state.read_text(encoding="utf-8"), count=1, flags=re.M)
        self.assertEqual(n, 1)
        state.write_text(text, encoding="utf-8")
        shell = "\n".join([
            "# Week %d Game Report" % WEEK, "",
            "<!-- event-record: %s -->" % json.dumps(event, sort_keys=True), "",
            "## 3. Game", "", "### Full stats for the game", "",
            "<!-- box-score event=%s team=%s -->" % (receipt["event_id"], JAX), "<!-- /box-score -->", ""])
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(render_box_score.fill(shell, self.paths.receipts, SEASON, report=True), encoding="utf-8")
        return report

    def settle_week(self, report):
        """The week's open decisions, settled in the copy as Stone's Game Plan settles them."""
        path = self.root / "state/decision_queue.json"
        queue = json.loads(path.read_text(encoding="utf-8"))
        for item in queue["items"]:
            if item["status"] == "OPEN" and any(b.get("kind") == "week_inputs" and b.get("week") == WEEK
                                                for b in item.get("blocks", ())):
                item["status"] = "RESOLVED"
                item["resolution"] = {"date": self.played.isoformat(), "by": "user",
                                      "record": {"path": report.relative_to(self.root).as_posix()},
                                      "summary": "Settled for the synthetic close."}
        path.write_text(json.dumps(queue, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    def rebuild_other_views(self, client):
        """The views the close rewrites that other builders own, as the weekly workflow rebuilds them."""
        root, paths = self.root, self.paths
        from scripts import render_player_ages
        for rel, text in render_player_ages.render_views(root).items():
            (root / rel).write_text(text, encoding="utf-8")
        regular = render_season_stats.load_receipts(paths.receipts)
        for name, text in render_season_stats.render_views(SEASON, JAX, regular).items():
            paths.file_in(paths.stats, name).parent.mkdir(parents=True, exist_ok=True)
            paths.file_in(paths.stats, name).write_text(text, encoding="utf-8")
        paths.record("standings.md").write_text(render_standings.render(SEASON, regular), encoding="utf-8")
        with patch.object(league_awards, "ROOT", root), \
                patch("runtime.private_client.Client", return_value=client), \
                patch.object(sys, "argv", ["league_awards", "week", str(WEEK), "--season", str(SEASON), "--close"]), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(league_awards.main(), 0)
        tracker = render_team_tracker.tracker_dir(root, SEASON)
        for rel, text in render_team_tracker.render(root, SEASON, JAX).items():
            (tracker / rel).parent.mkdir(parents=True, exist_ok=True)
            (tracker / rel).write_text(text, encoding="utf-8")
        player_pages.write(root)
        from scripts import render_career_views, render_club_pages, render_coach_pages, render_inseason_rails
        render_club_pages.write(root)
        render_coach_pages.write(root)
        render_career_views.write(root)
        closed = render_season_stats.load_receipts(paths.receipts)
        page = render_inseason_rails.page_path(SEASON, WEEK, root)
        page.write_text(render_inseason_rails.render(SEASON, WEEK, root, [r for r in closed if int(r["week"]) < WEEK]),
                        encoding="utf-8")

    def owned(self):
        """The pages this step's result-side builders write."""
        season = week_pages.Season(self.root, SEASON)
        owned = set(week_pages.built(season)) | set(week_pages.incidents(season))
        return owned | {season.rel(week_pages.medical_path(season, "medical_history.md")),
                        season.rel(events.annual_record_path(self.root, SEASON)),
                        season.rel(self.paths.game_report(WEEK))}

    def hold_as_history(self, rels):
        """New pages other builders wrote in the copy (their own step cleans them), recorded in the
        copy's page history only, so the check here reads this builder's pages."""
        path = self.root / PAGE_HISTORY
        data = json.loads(path.read_text(encoding="utf-8"))
        for rel in rels:
            body = (self.root / rel).read_bytes()
            data["pages"][rel] = clean_pages.digest(body)
            data["lengths"][rel] = len(body)
        path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")

    def test_week_close_rebuilds_clean_pages_and_validates(self):
        root, paths = self.root, self.paths
        receipt = self.fake_week()
        self.played = self.move_clock(receipt)
        report = self.write_report(receipt)
        self.settle_week(report)
        snapshot = hashlib.sha256((root / "state/05_Current_Season_State.md").read_bytes()).hexdigest()
        _, client = local_service(self, root / "private", "week-close-pages", snapshot=snapshot)
        self.rebuild_other_views(client)

        # This builder's pages: the week pages, the medical entry and incidents, then the record.
        history = week_pages.medical_path(week_pages.Season(root, SEASON), "medical_history.md")
        before = history.read_bytes()
        written, problems = render_week_pages.write(root, SEASON)
        self.assertEqual(problems, [])
        self.assertGreater(written, 0)
        self.assertTrue(history.read_bytes().startswith(before), "the medical history only gains entries")
        appended = history.read_bytes()[len(before):].decode("utf-8")
        self.assertEqual(appended.count("<!-- event-record:"), 1)
        self.assertIn("Week %d injuries" % WEEK, appended)
        self.assertEqual(render_week_pages.write(root, SEASON), (0, []))  # a second run changes nothing
        record = events.annual_record_path(root, SEASON)
        record_before = record.read_bytes()
        record.write_text(events.render_record(SEASON, events.load_events(root), root), encoding="utf-8")
        self.assertTrue(record.read_bytes().startswith(record_before))
        self.assertEqual(render_week_pages.check(root, SEASON), [])

        season = week_pages.Season(root, SEASON)
        results = week_pages.week_page_path(season, WEEK)
        self.assertTrue(results.is_file())
        self.assertIn(week_pages.TO_COME, results.read_text(encoding="utf-8"))
        self.assertIn("SCK/YDS", report.read_text(encoding="utf-8"))
        self.assertNotIn("SCK-YDS", report.read_text(encoding="utf-8"))
        self.assertEqual(render_box_score.stale_blocks(report, paths.receipts, season=SEASON), [])
        for rel in week_pages.incidents(season):
            self.assertTrue((root / rel).is_file(), rel)

        # Pages other builders own that the close rewrote stay history in the copy; every page this
        # builder writes is checked as a page written from Week 6 on.
        old = clean_pages.history(root)
        owned = self.owned()
        others = [rel for rel in old if rel not in owned and (root / rel).is_file()
                  and clean_pages.digest((root / rel).read_bytes()) != old[rel]]
        keep_as_history(root, others)
        added = [rel for rel, _, _ in clean_pages.checked_parts(root) if rel not in owned and rel not in old]
        self.hold_as_history(added)
        with pinned_copy(root):
            unclean = clean_pages.clean_errors(root)
            errors = validate(root)
        self.assertEqual(unclean, [])
        baseline = set(validate(ROOT))
        self.assertEqual(sorted(set(errors) - baseline), [])
        for rel in [r for r in old if r in owned]:
            data = (root / rel).read_bytes()
            self.assertNotEqual(clean_pages.unchecked_prefix(data, old[rel], clean_pages.history_lengths(root).get(rel)),
                                len(data), "%s was rewritten or gained entries and is checked" % rel)

        # Isolation: nothing reached the real season.
        self.assertEqual(sorted(p.name for p in SeasonPaths(SEASON, ROOT).receipts.glob("*.json")), self.real)


if __name__ == "__main__":
    unittest.main()
