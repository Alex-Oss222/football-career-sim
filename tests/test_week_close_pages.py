"""A synthetic Week 6 close in a temporary copy (rebuild step 4).

The whole result side of a game week's close, the way the weekly workflow
runs it: the week's games close, the Game Report is written in the Game
Report template's layout with its generated box score, the week's awards are
drawn, and then one command, scripts/rebuild_pages.py, names the report's box
score and fills it last, and rebuilds every built
page in order (the standings, the statistics, the team tracker, the award
pages, the player, club and coach pages, the cap views, the game-week pages,
the Games and league-results pages, the injury report, the medical history's
game entry and the incident records, the in-season roster moves page, the
desk and the calendar, and the annual record). Every page must then pass the
clean-page check and repository validation of the copy must add no error to
the real checkout's; no rewritten page is re-recorded as history.

The fake result: the copy's first Game Report week whose games have not
closed (the first Game Report week until it really closed, then the next one)
is closed by relabelling the copy's previous week's closed games onto that
week's fixtures, game for game, Jacksonville's on Jacksonville's: the same
scores and statistics, now in the new week. Jacksonville's injuries are
recorded as a multi-week and a long-term injury, the severities whose names
the game records with an underscore. The master date and the roster record
move to the new game day, as the week's close moves them, with each newly
injured player's medical instruction. No game is played and the real
repository is never touched.
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

from runtime import clean_pages, events, week_pages  # noqa: E402
from runtime.seasons import GAME_REPORT, GAME_REPORT_FROM, SeasonPaths  # noqa: E402
from runtime.week_inputs import event_id, receipt_name  # noqa: E402
from scripts import league_awards, rebuild_pages, render_box_score, render_week_pages  # noqa: E402
from scripts.validate_repository import validate  # noqa: E402
from local_private_service import local_service  # noqa: E402
from test_game_report import template_report  # noqa: E402

JAX = "Jacksonville Jaguars"
SEASON, FIRST_REPORT_WEEK = GAME_REPORT_FROM


def open_report_week(root=ROOT):
    """The week this test closes in its copy: the first Game Report week whose games have not closed
    in the real checkout."""
    paths = SeasonPaths(SEASON, root)
    weeks = sorted({g["week"] for g in paths.regular_games() if g["week"] >= FIRST_REPORT_WEEK})
    return next(w for w in weeks if not list(paths.receipts.glob("week_%02d_*.json" % w)))


WEEK = open_report_week()
IGNORED = (".git", ".sim_cache", "__pycache__", ".pytest_cache")
# The receipt fields tied to the week a game was played under: the defensive call record names that
# week's committed sheet, and the decision policies its standing rules.
WEEK_BOUND = ("defensive_calls", "defensive_call_stats", "decision_policies")
# Jacksonville's fake injuries, in the game's own severity names, with days to return.
SEVERITIES = (("multi_week", 24), ("long_term", 70))


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


def record_practice(test, root, week):
    """The week's practice and rest record, as the practice-week commit writes it once the master date
    is at game day (docs/run_week.md, step 5): the schedule Stone's standing practice instruction sets
    for the week, held as set, its participation not recorded session by session (test data only)."""
    from runtime import decisions, practices
    from scripts import record_practice_week
    schedule, why = record_practice_week.applied_schedule(root, SEASON, week)
    test.assertIsNotNone(schedule, why)
    page = decisions.week_pages(SEASON, week, root).briefing
    held = {"source": {"page": page.relative_to(root).as_posix()},
            "sessions": [dict(s, participation_recorded=False) for s in schedule["sessions"]],
            "days_off": schedule["days_off"]}
    record = record_practice_week.held_record(SEASON, week, held, schedule, root)
    test.assertEqual(practices.record_errors(record, root, schedule=schedule), [])
    practices.write(record, root)


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
                injured = [i for i in receipt["injuries"] if i.get("team") == JAX]
                self.assertGreaterEqual(len(injured), len(SEVERITIES))
                for injury, (severity, days) in zip(injured, SEVERITIES):
                    injury.update({"severity": severity, "return_days": days, "reassessment_days": 6})
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
        injured = [i for i in receipt["injuries"] if i.get("team") == JAX]
        self.assertTrue(injured, "the fake week carries no Jacksonville injury")
        # Each instruction as the close records it: written from the game's record in the one
        # medical format (runtime/week_pages.availability_entry), as render_week_pages.py
        # --availability prints it.
        season = week_pages.Season(self.root, SEASON)
        game = next(r for r in season.receipts.values() if int(r["week"]) == WEEK and JAX in (r["away"], r["home"]))
        for injury in injured:
            row = next(p for p in data["players"] if p["name"] == injury["player"])
            row["availability"], source = week_pages.availability_entry(season, game, injury)
            row.setdefault("sources", {})["availability"] = source
        roster.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        return played

    def write_report(self, receipt):
        """The week's Game Report in the Game Report template's layout (tests/test_game_report.py
        template_report): its sections, the event line, the header, line score and record of the game,
        and the template's markers last, unnamed: the rebuild names them and fills the box score."""
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
        from runtime import game_report, game_weeks
        game = game_weeks.club_game(self.paths, WEEK, JAX)
        played = [r for r in game_weeks.regular_receipts(self.paths) if JAX in (r["away"], r["home"])]
        record = sorted(game_report.record_forms(played, JAX), key=len)[0]
        page = template_report(receipt, game, record, self.root)
        title, rest = page.split("\n", 1)
        # A report opened before the game (the practice-week commit's preparation and game-day
        # event lines) keeps those lines: the week index and the annual record already cite them.
        opened = report.read_text(encoding="utf-8").splitlines() if report.is_file() else []
        earlier = [line for line in opened if line.startswith("<!-- event-record: ")]
        shell = "\n".join([title, ""] + earlier
                           + ["<!-- event-record: %s -->" % json.dumps(event, sort_keys=True), rest])
        self.assertIn(game_report.EVENT_PLACEHOLDER, shell)
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(shell, encoding="utf-8")
        # Its preparation and pregame media as the game-day commit froze them before kickoff
        # (scripts/freeze_pregame.py; the synthetic close writes the report after the game).
        from runtime import decisions
        frozen = decisions.week_pages(SEASON, WEEK, self.root).pregame
        frozen.parent.mkdir(parents=True, exist_ok=True)
        frozen.write_text(json.dumps(game_report.pregame_record(shell, self.played), indent=1) + "\n", encoding="utf-8")
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

    def draw_awards(self, client):
        """The week's awards, drawn through the local test service as the weekly close draws them."""
        with patch.object(league_awards, "ROOT", self.root), \
                patch("runtime.private_client.Client", return_value=client), \
                patch.object(sys, "argv", ["league_awards", "week", str(WEEK), "--season", str(SEASON), "--close"]), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(league_awards.main(), 0)

    def test_week_close_rebuilds_clean_pages_and_validates(self):
        root, paths = self.root, self.paths
        receipt = self.fake_week()
        self.played = self.move_clock(receipt)
        record_practice(self, self.root, WEEK)
        report = self.write_report(receipt)
        self.settle_week(report)
        snapshot = hashlib.sha256((root / "state/05_Current_Season_State.md").read_bytes()).hexdigest()
        _, client = local_service(self, root / "private", "week-close-pages", snapshot=snapshot)
        self.draw_awards(client)
        self.assertEqual(clean_pages.page_errors(report.relative_to(root).as_posix(),
                                                 report.read_text(encoding="utf-8")), [])

        # One command rebuilds every built page; a second run finds nothing to write.
        history = week_pages.medical_path(week_pages.Season(root, SEASON), "medical_history.md")
        before = history.read_bytes()
        record = events.annual_record_path(root, SEASON)
        record_before = record.read_bytes()
        written, problems = rebuild_pages.rebuild(root, SEASON)
        self.assertEqual(problems, [])
        self.assertTrue(written)
        self.assertEqual(rebuild_pages.rebuild(root, SEASON), ([], []))
        self.assertEqual(rebuild_pages.rebuild(root, SEASON, check=True), ([], []))

        # The history pages only gained entries: the medical history its one game entry, the record
        # its lines.
        self.assertTrue(history.read_bytes().startswith(before), "the medical history only gains entries")
        appended = history.read_bytes()[len(before):].decode("utf-8")
        self.assertEqual(appended.count("<!-- event-record:"), 1)
        self.assertIn("Week %d injuries" % WEEK, appended)
        self.assertIn("multi-week", appended)
        self.assertIn("long term", appended)
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
        injury_report = week_pages.medical_path(season, "current_injury_report.md").read_text(encoding="utf-8")
        self.assertIn("(multi-week)", injury_report)
        self.assertIn("(long term)", injury_report)
        # The next week opens: its briefing, its blank Game Plan and its index are issued.
        from runtime import decisions
        following = decisions.week_pages(SEASON, min(g["week"] for g in paths.regular_games()
                                                     if g["week"] > WEEK and JAX in (g["away"], g["home"])), root)
        self.assertTrue(following.briefing.is_file() and following.plan.is_file())
        self.assertIn("Game Report", decisions.week_pages(SEASON, WEEK, root).readme.read_text(encoding="utf-8"))

        # The briefing of the next week reads each new instruction whole, its exam included.
        from scripts import render_game_week
        briefing = following.briefing.read_text(encoding="utf-8")
        for injury in (i for i in receipt["injuries"] if i.get("team") == JAX and i.get("reassessment_days")):
            exam = week_pages.month_day(self.played + timedelta(days=injury["reassessment_days"]))
            line = next(l for l in briefing.splitlines() if l.startswith("| ") and injury["player"] in l.split("|")[1])
            self.assertIn("| Reassessment, %s |" % exam, line)
            self.assertNotIn("; reassessment", line)      # the note is read whole, not copied as written

        # A played week's index is checked like the open week's (F4): left stale, it fails.
        played_pages = decisions.week_pages(SEASON, WEEK, root)
        built = played_pages.readme.read_text(encoding="utf-8")
        played_pages.readme.write_text(built.replace("[Game Report](Game_Report.md)", "Game Report"), encoding="utf-8")
        self.assertTrue(any("Week %d: the week index is missing or stale" % WEEK in e
                            for e in render_game_week.validation_errors(root)))
        self.assertTrue(render_game_week.check(root, WEEK))
        played_pages.readme.write_text(built, encoding="utf-8")
        self.assertEqual(render_game_week.check(root, WEEK), [])

        # The week's league-results highlights are stored text a rebuild renders (F6).
        game = next(g for g in week_pages.ordered_games(season, WEEK) if JAX not in (g["away"], g["home"]))
        path = week_pages.highlights_path(season, WEEK)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"games": {season.receipt(game)["event_id"]: "A stored highlight."}}),
                        encoding="utf-8")
        self.assertTrue(render_week_pages.check(root, SEASON))
        self.assertEqual(rebuild_pages.rebuild(root, SEASON)[1], [])
        self.assertIn("A stored highlight.", results.read_text(encoding="utf-8"))
        self.assertEqual(render_week_pages.check(root, SEASON), [])

        # Every page is checked as written, none re-recorded as history, and validation of the copy
        # adds nothing to the real checkout's.
        self.assertEqual(clean_pages.clean_errors(root), [])
        self.assertEqual(clean_pages.history(root), clean_pages.history(ROOT))
        baseline = set(validate(ROOT))
        self.assertEqual(sorted(set(validate(root)) - baseline), [])

        # Isolation: nothing reached the real season.
        self.assertEqual(sorted(p.name for p in SeasonPaths(SEASON, ROOT).receipts.glob("*.json")), self.real)


if __name__ == "__main__":
    unittest.main()
