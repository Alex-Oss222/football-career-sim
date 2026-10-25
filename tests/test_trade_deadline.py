"""The trading deadline and the eligibility windows as COMING UP (rebuild step 5, A5; F3).

The real repository is only read; every write happens in a throwaway copy of the checkout. Weeks and
dates come from the season's records (its league dates, fixtures and roster record), never from
today's date: the deadline's brief is the last Jacksonville game before the recorded deadline, and a
synthetic deadline in a copy is placed after the open week's game.
"""
import contextlib
from datetime import date, timedelta
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from release_staging import IGNORED  # noqa: E402
import support_events as se  # noqa: E402
from runtime import deadlines, decision_queue, event_inserts, open_events  # noqa: E402
from runtime import roster as roster_record, season_summary  # noqa: E402
from runtime.clean_pages import page_errors  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402
from scripts import render_game_week  # noqa: E402

SEASON = se.SEASON
MINUTE = timedelta(minutes=1)


def copy_repo(test):
    tmp = tempfile.TemporaryDirectory(dir=ROOT.parent)
    test.addCleanup(tmp.cleanup)
    root = Path(tmp.name) / "repo"
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(*IGNORED), symlinks=True)
    for record in root.glob("career/**/paused_game.json"):
        record.unlink()
    # The copy keeps the season's events as they stand (a resolved one is on a closed week's index,
    # which would go stale without it); a test counts only the events it raises (raised_here).
    test.before = {r["id"] for r in open_events.load(SEASON, root)}
    return root


def raised_here(test, root):
    """The events raised in the copy since copy_repo made it."""
    return [r for r in open_events.load(SEASON, root) if r["id"] not in test.before]


def quiet(call, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return call(*args, **kwargs)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest() if Path(path).is_file() else None


def deadline_games(root=ROOT):
    """(the deadline, the last Jacksonville game before it, the game before that one)."""
    deadline = deadlines.trading_deadline(SEASON, root)
    games = sorted((g for g in open_events.club_fixtures(SEASON, root) if open_events.kickoff(g) < deadline),
                   key=open_events.kickoff)
    return deadline, games[-1], games[-2]


def keys(windows):
    return [w["key"] for w in windows]


class RecordTests(unittest.TestCase):
    def test_the_record_holds_the_calendar_deadline_and_the_waivers(self):
        entry = deadlines.league_date(SEASON, "trading_deadline", ROOT)
        if entry is None:
            self.skipTest("the season records no league dates")
        self.assertEqual(deadlines.validation_errors(ROOT), [])
        # The deadline is the calendar's row and the rules library's, at 4 p.m. ET.
        calendar = SeasonPaths(SEASON, ROOT).calendar.read_text(encoding="utf-8")
        row = re.search(r"^\| ([A-Z][a-z]+ \d{1,2}), 4 p\.m\. \| Trading deadline \|$", calendar, re.M)
        self.assertIsNotNone(row)
        at = deadlines.trading_deadline(SEASON, ROOT)
        self.assertEqual((at.strftime("%B"), at.day, at.hour, at.minute), (row[1].split()[0], int(row[1].split()[1]), 16, 0))
        rules = (ROOT / "library/2014_playing_and_roster_rules.md").read_text(encoding="utf-8")
        self.assertIn("Trade deadline: %s, %s %d, %d, 4:00 p.m. ET" % (at.strftime("%A"), at.strftime("%B"), at.day,
                                                                       at.year), rules)
        self.assertEqual(entry["brought_by"], "caldwell")
        waivers = deadlines.waivers_from(SEASON, ROOT)
        self.assertEqual(waivers, at.date() + timedelta(days=1))
        self.assertIsNone(deadlines.league_date(SEASON, "veteran_waivers", ROOT)["coming_up"])
        # Another season with no record shows no deadline: October's date is never reused.
        self.assertIsNone(deadlines.trading_deadline(SEASON + 1, ROOT))
        later = open_events.et(at.date().replace(year=at.year + 1), 9)
        self.assertEqual([w for w in deadlines.coming_up(SEASON + 1, later, ROOT) if w["key"].endswith("deadline")], [])

    def test_a_malformed_record_fails_validation(self):
        root = copy_repo(self)
        target = deadlines.path(SEASON, root)
        data = json.loads(target.read_text(encoding="utf-8"))
        data["dates"][0]["sources"][0]["anchor"] = "no-such-heading"
        data["dates"][1]["coming_up"] = "last_game_before"
        target.write_text(json.dumps(data), encoding="utf-8")
        errors = deadlines.validation_errors(root)
        self.assertTrue(any("missing heading" in e for e in errors))
        self.assertTrue(any("only the trading deadline" in e for e in errors))


class WindowTests(unittest.TestCase):
    def test_f3_the_deadline_shows_in_its_briefs_and_passes_with_no_call(self):
        if deadlines.trading_deadline(SEASON, ROOT) is None:
            self.skipTest("the season records no trading deadline")
        root = copy_repo(self)
        deadline, game, before = deadline_games(root)
        start = open_events.kickoff(before)
        watched = [root / decision_queue.QUEUE] + [p for f in open_events.stores(SEASON, root) for p in f.glob("*")]
        snapshot = [digest(p) for p in watched]
        for at, shown in ((start - MINUTE, False), (start, True), (open_events.kickoff(game) + MINUTE, True),
                          (deadline - MINUTE, True), (deadline, False), (deadline + timedelta(days=3), False)):
            found = [w for w in deadlines.coming_up(SEASON, at, root) if w["key"].endswith("trading-deadline")]
            self.assertEqual(bool(found), shown, at)
        # The first brief of the deadline's game shows it under COMING UP only, with nothing to answer.
        route = open_events.route(SEASON, start, {"week": int(game["week"])}, root, issue=1)
        self.assertEqual((route.action, route.fyi), ([], []))
        window = next(n.window for n in route.coming_up if n.key.endswith("trading-deadline"))
        self.assertEqual((window["state"], window["action"]), (deadlines.NO_PROPOSAL, deadlines.NO_ANSWER))
        page_rel = decisions_page(root, game)
        lines = event_inserts.render(route, page_rel, start)
        self.assertEqual([h for h in event_inserts.HEADINGS if h in lines], ["## COMING UP"])
        self.assertNotIn(event_inserts.ONE_RULE, lines)
        text = "\n".join(lines)
        self.assertIn("**Trading deadline** | %s" % open_events.at_text(deadline), text)
        self.assertIn("**Current state:** No proposal is on record.", text)
        self.assertIn("**Action now:** No answer is required.", text)
        self.assertEqual(page_errors(page_rel, text, root=root), [])
        # Afterward nothing shows, and no hold, page, question or event exists.
        after = open_events.route(SEASON, deadline + MINUTE, {"week": int(game["week"]) + 1}, root, issue=1)
        self.assertFalse(any(n.key.endswith("trading-deadline") for n in after.coming_up))
        self.assertEqual([digest(p) for p in watched], snapshot)
        self.assertEqual(raised_here(self, root), [])
        self.assertFalse(any(i.get("event") and i["event"] not in self.before
                             for i in decision_queue.load(root)["items"]))

    def test_each_eligibility_window_shows_until_its_date(self):
        data = roster_record.load(SeasonPaths(SEASON, ROOT).roster)
        limits = [(row["name"], what, when) for row in data.get("players") or ()
                  for what, when in deadlines.LIMIT.findall(row.get("availability") or "")]
        if not limits:
            self.skipTest("no player carries an eligibility window")
        for name, what, when in limits:
            day = season_summary.date_on(when, date(SEASON, 9, 1))
            key = "%s-%s-%s" % (deadlines._name_key(name), what, day.isoformat())
            before = deadlines.coming_up(SEASON, open_events.et(day) - MINUTE, ROOT)
            self.assertIn(key, keys(before))
            window = next(w for w in before if w["key"] == key)
            self.assertEqual((window["at"], window["date"], window["action"]), (None, day.isoformat(), deadlines.NO_ANSWER))
            self.assertIn("no %s before %s %d" % (what, day.strftime("%B"), day.day), window["why"])
            self.assertNotIn(key, keys(deadlines.coming_up(SEASON, open_events.et(day), ROOT)))
            # A window is shown by its day, never as a time.
            notice = open_events.Notice("coming_up", key, window=window)
            shown = "\n".join(event_inserts.coming_up_lines(notice, None, "career/README.md", {}))
            self.assertIn("| %s, %s %d" % (day.strftime("%A"), day.strftime("%B"), day.day), shown)
            self.assertNotIn("12 a.m.", shown)


def decisions_page(root, game):
    from runtime import decisions
    return decisions.week_pages(SEASON, int(game["week"]), root).briefing.relative_to(root).as_posix()


class SyntheticDeadlineTests(unittest.TestCase):
    """A test deadline placed after the open week's game, in a copy: a recorded call reaches ACTION
    REQUIRED, the window names it, nothing is accepted and the game is never held."""

    def setUp(self):
        self.root = copy_repo(self)
        self.game = se.open_game(self.root)
        if self.game is None:
            self.skipTest("every regular-season game has closed")
        self.week = int(self.game["week"])
        self.tuesday = se.tuesday_before(self.game)
        game_day = date.fromisoformat(self.game["date"])
        self.deadline = open_events.et(game_day + timedelta(days=2), 16)
        target = deadlines.path(SEASON, self.root)
        data = json.loads(target.read_text(encoding="utf-8"))
        data["dates"][0]["at"] = open_events.iso(self.deadline)
        target.write_text(json.dumps(data, indent=1), encoding="utf-8")
        se.midweek(self.root, self.tuesday, 10, 30, self.week)

    def test_a_call_reaches_action_required_and_never_holds_the_game(self):
        held = decision_queue.blocking_errors([decision_queue.event("week_inputs", SEASON, self.week),
                                               decision_queue.event("week_close", SEASON, self.week)], self.root)
        at = open_events.et(self.tuesday, 10, 30)
        self.assertIn("trading-deadline", " ".join(keys(deadlines.coming_up(SEASON, at, self.root))))
        for n, due in enumerate((self.deadline, open_events.kickoff(self.game) - timedelta(hours=3))):
            record = se.trade_call(self.root, "test-call-deadline-%d" % n, open_events.et(self.tuesday, 9 + n), due)
            open_events.raise_event(record, self.root)
        written = quiet(render_game_week.write, self.root)
        wk = render_game_week.Week(self.root)
        self.assertIn(wk.pages.briefing, written)
        entry = render_game_week.issues(wk)[-1]
        self.assertTrue(entry["reason"].startswith("a:"))
        page = wk.pages.briefing.read_text(encoding="utf-8")
        self.assertTrue(page.index("## ACTION REQUIRED") < page.index("## COMING UP") < page.index("## 1. "))
        self.assertIn("**Current state:** Open: the trade call from Test Club, due", page)
        self.assertIn("**Action now:** No answer is required.", page)
        self.assertIn(deadlines.league_date(SEASON, "trading_deadline", self.root)["key"],
                      [i.get("window") for i in entry["inserts"]])
        # Nothing is accepted, and neither call holds the game, whatever its due time.
        for record in raised_here(self, self.root):
            self.assertEqual((record["state"], record["resolution"]), ("open", None))
            self.assertEqual(se.item(self.root, record["queue_item"])["status"], "OPEN")
        self.assertEqual(decision_queue.blocking_errors([decision_queue.event("week_inputs", SEASON, self.week),
                                                         decision_queue.event("week_close", SEASON, self.week)],
                                                        self.root), held)
        self.assertEqual(open_events.validation_errors(self.root), [])
        self.assertEqual(render_game_week.check(self.root), [])

    def test_an_issued_brief_keeps_the_windows_it_recorded(self):
        # A brief issued while the season had no deadline on record, rebuilt as of its issue once the
        # record is back, still shows only the windows it recorded: a window is never added to an issue.
        target = deadlines.path(SEASON, self.root)
        original = target.read_text(encoding="utf-8")
        key = deadlines.league_date(SEASON, "trading_deadline", self.root)["key"]
        target.unlink()
        record = se.trade_call(self.root, "test-call-window", open_events.et(self.tuesday, 9))
        open_events.raise_event(record, self.root)
        quiet(render_game_week.write, self.root)
        wk = render_game_week.Week(self.root)
        entry = render_game_week.issues(wk)[-1]
        self.assertTrue(entry["reason"].startswith("a:"))
        self.assertNotIn(key, [i.get("window") for i in entry["inserts"]])
        target.write_text(original, encoding="utf-8")
        self.assertIn(key, keys(deadlines.coming_up(SEASON, open_events.parse_at(entry["at"]), self.root)))
        when, revision = render_game_week.current_issue(wk)
        rebuilt = render_game_week.briefing(wk, when, previous=render_game_week.previous_issue(wk), revision=revision)
        self.assertEqual(rebuilt, wk.pages.briefing.read_text(encoding="utf-8"))
        # A COMING UP change waits for the next scheduled issue.
        self.assertIsNone(render_game_week.reissue_reason(wk))

if __name__ == "__main__":
    unittest.main()
