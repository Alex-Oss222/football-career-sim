"""The inserts at the top of the active brief and the one reissue rule (rebuild step 5, A2).

F1 reads the real repository only; every other test writes test events into a throwaway copy
(support_events), never the real one. Weeks and dates come from the fixtures and receipts: the open
week is the first Jacksonville game without a receipt, its mid-week clock its Tuesday.
"""
import contextlib
from datetime import date, timedelta
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from release_staging import IGNORED  # noqa: E402
import support_events as se  # noqa: E402
from runtime import deadlines, decision_queue, event_inserts, open_events  # noqa: E402
from runtime.clean_pages import page_errors  # noqa: E402
from scripts import render_game_week  # noqa: E402

SEASON = se.SEASON


def copy_repo(test):
    tmp = tempfile.TemporaryDirectory(dir=ROOT.parent)
    test.addCleanup(tmp.cleanup)
    root = Path(tmp.name) / "repo"
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(*IGNORED), symlinks=True)
    for record in root.glob("career/**/paused_game.json"):
        record.unlink()
    return root


def quiet(call, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return call(*args, **kwargs)


class RealWeekTests(unittest.TestCase):
    """F1: the open week opens without events; its issued pages are unchanged and no reissue is due."""

    def test_f1_the_issued_briefing_and_index_rebuild_byte_for_byte(self):
        wk = render_game_week.Week(ROOT)
        if wk.game is None or not wk.pages.briefing.is_file():
            self.skipTest("no issued briefing for an open week")
        self.assertEqual(open_events.load(SEASON, ROOT), [])
        when, revision = render_game_week.current_issue(wk)
        page = wk.pages.briefing.read_text(encoding="utf-8")
        rebuilt = render_game_week.briefing(wk, when, previous=render_game_week.previous_issue(wk), revision=revision)
        self.assertEqual(rebuilt, page)
        # Section 8 keeps its "If facts change" sentence, and no insert section is added.
        self.assertIn("**If facts change:** The staff issues a new briefing", page)
        for heading in event_inserts.HEADINGS:
            self.assertNotIn(heading, page)
        self.assertIsNone(render_game_week.reissue_reason(wk))
        self.assertFalse(render_game_week.overtaken(wk))
        self.assertEqual(render_game_week.index_page(wk), wk.pages.readme.read_text(encoding="utf-8"))
        # Every earlier issue keeps its recorded bytes.
        self.assertEqual(render_game_week.issue_errors(wk), [])


class InsertTests(unittest.TestCase):
    def setUp(self):
        self.root = copy_repo(self)
        self.game = se.open_game(self.root)
        if self.game is None:
            self.skipTest("every regular-season game has closed")
        self.week = int(self.game["week"])
        self.tuesday = se.tuesday_before(self.game)
        self.wednesday = self.tuesday + timedelta(days=1)
        se.midweek(self.root, self.tuesday, 10, 30, self.week)

    def wk(self):
        return render_game_week.Week(self.root)

    def raise_(self, record):
        open_events.raise_event(record, self.root)
        return open_events.get(SEASON, record["id"], self.root)

    def issue(self):
        return quiet(render_game_week.write, self.root)

    def no_issue(self):
        """A write that issues no briefing: at most the week's index changes (its other business, A4)."""
        wk = self.wk()
        written = self.issue()
        self.assertEqual([p for p in written if p != wk.pages.readme], [])
        return written

    def page(self):
        return self.wk().pages.briefing.read_text(encoding="utf-8")

    def call(self, ident, hour=9, due=None, **changes):
        return self.raise_(se.trade_call(self.root, ident, open_events.et(self.tuesday, hour), due, **changes))

    # F2
    def test_f2_a_call_after_the_issue_gives_a_new_dated_issue(self):
        wk = self.wk()
        before = render_game_week.issues(wk)
        old = wk.pages.briefing.read_text(encoding="utf-8")
        due = open_events.et(self.wednesday, 16)
        record = self.call("test-call-tennessee", due=due)
        self.assertEqual(render_game_week.reissue_reason(self.wk())[:2], "a:")
        written = self.issue()
        entries = render_game_week.issues(self.wk())
        self.assertEqual(len(entries), len(before) + 1)
        kept = self.wk().pages.folder / entries[-2]["file"]
        self.assertIn(kept, written)
        self.assertEqual(kept.read_text(encoding="utf-8"), old)
        latest = entries[-1]
        self.assertEqual(latest["date"], self.tuesday.isoformat())
        self.assertEqual(latest["at"], open_events.iso(open_events.et(self.tuesday, 10, 30)))
        self.assertTrue(latest["reason"].startswith("a:"))
        self.assertEqual([(i.get("event"), i["section"], i["due"]) for i in latest["inserts"] if i["section"] == "action"],
                         [(record["id"], "action", open_events.iso(due))])
        # Any window recorded is one the windows give for the issue (A5), never an answer.
        self.assertEqual([i["window"] for i in latest["inserts"] if i["section"] == "coming_up"],
                         [w["key"] for w in deadlines.coming_up(SEASON, open_events.et(self.tuesday, 10, 30), self.root)])
        page = self.page()
        self.assertIn("## ACTION REQUIRED\n\n**One decision needs your answer.**", page)
        self.assertIn("**Response due: Wednesday, %s %d, 4 p.m. ET**" % (self.wednesday.strftime("%B"),
                                                                     self.wednesday.day), page)
        self.assertIn("**Why it needs you:** Your football recommendation to David Caldwell; he decides.", page)
        self.assertIn("**Staff position:** Not yet supplied.", page)
        self.assertIn("**If no agreement is reached:** The other club's deadline passes at 4 p.m. ET on Wednesday",
                      page)
        self.assertIn("**Individual event result:** Pending", page)
        self.assertIn(event_inserts.ONE_RULE, page)
        # The inserts sit under the header lines, before section 1; the rest is the briefing as it
        # would be without them.
        self.assertLess(page.index("## ACTION REQUIRED"), page.index("## 1. "))
        wk = self.wk()
        bare = render_game_week.briefing(wk, self.tuesday, previous=render_game_week.previous_issue(wk), revision=1,
                                         route=open_events.Route())
        self.assertTrue(event_inserts.strip_inserts(page) == bare)
        # Nothing is accepted or invented: the event and its item stay open, with no result.
        now = open_events.get(SEASON, record["id"], self.root)
        self.assertEqual((now["state"], now["process"], now["resolution"]), ("open", [], None))
        self.assertEqual(se.item(self.root, record["queue_item"])["status"], "OPEN")
        # No event id, data path or system word is on the page.
        self.assertNotIn(record["id"], page)
        self.assertEqual(page_errors(self.wk().rel(self.wk().pages.briefing), page, root=self.root), [])
        self.assertEqual(render_game_week.validation_errors(self.root), [])
        self.assertIsNone(render_game_week.reissue_reason(self.wk()))
        self.assertEqual(self.issue(), [])

    def news(self, ident, hour):
        """A test head-coach change at another club, decided by that club and resolved at once."""
        source = se.source_page(self.root, "head_coach_change")
        raised = open_events.et(self.tuesday, hour)
        record = {"schema": open_events.SCHEMA, "id": "%s-%s" % (self.tuesday.isoformat(), ident),
                  "kind": "head_coach_change", "season": SEASON, "subject": "Test Club",
                  "raised": {"at": open_events.iso(raised), "by": "communications_staff", "source": {"path": source}},
                  "known_to": ["stone"], "authority": {"rows": ["1"], "decides": open_events.OTHER_CLUB},
                  "stone_part": "none",
                  "summary": {"text": "A test change of head coach at another club.",
                              "author": "Team communications staff", "date": self.tuesday.isoformat()},
                  "facts": [], "options": [], "deadline": None, "state": "open", "process": []}
        self.raise_(record)
        page = se.result_page(self.root, record, "Head_Coach_Change_test.md", self.tuesday)
        open_events.resolve(SEASON, record["id"], {
            "at": open_events.iso(raised), "outcome": "executed", "by": open_events.OTHER_CLUB,
            "decision": {"text": "The club named an interim head coach from its staff.",
                         "author": "Team communications staff", "date": self.tuesday.isoformat(), "criteria": None},
            "result_page": page}, self.root)
        return open_events.get(SEASON, record["id"], self.root)

    def test_an_fyi_only_change_gives_no_reissue(self):
        record = self.news("test-coach-change", 9)
        self.assertEqual(open_events.validation_errors(self.root), [])
        self.assertIsNone(render_game_week.reissue_reason(self.wk()))
        self.no_issue()
        # The notice waits for the next scheduled issue.
        nxt = open_events.route(SEASON, open_events.et(self.tuesday, 11), {"week": self.week + 1}, self.root, issue=1)
        self.assertEqual([n.key for n in nxt.fyi], [record["id"]])

    def test_a_result_settled_after_the_last_issue_shows_once_in_the_next_weeks_first_issue(self):
        record = self.call("test-call-withdrawn")
        self.issue()                                   # the reissue that carries it under ACTION REQUIRED
        se.midweek(self.root, self.wednesday, 11, 0, self.week)
        open_events.add_process(SEASON, record["id"], {
            "at": open_events.iso(open_events.et(self.wednesday, 10)), "kind": "withdrawn_by_other_side",
            "by": open_events.OTHER_CLUB, "what": "The other club withdrew its proposal.",
            "source": record["raised"]["source"]}, self.root)
        rel = open_events.path_of(record, self.root).relative_to(self.root.resolve()).as_posix()
        se.settle(self.root, record["queue_item"], "WITHDRAWN", {
            "date": self.wednesday.isoformat(), "by": "organization", "record": {"path": rel, "pointer": "/process/0"},
            "summary": "%s: the other club withdrew." % open_events.OTHER_SIDE_SUMMARY})
        page = se.result_page(self.root, record, "Trade_Result_test.md", self.wednesday)
        open_events.resolve(SEASON, record["id"], {
            "at": open_events.iso(open_events.et(self.wednesday, 10, 30)), "outcome": "withdrawn",
            "by": open_events.OTHER_CLUB, "decision": {"text": "The other club withdrew its proposal.",
                                                       "author": "David Caldwell", "date": self.wednesday.isoformat(),
                                                       "criteria": None}, "result_page": page}, self.root)
        # An ended question is news: no reissue of this week's briefing, which keeps what it showed.
        self.assertIsNone(render_game_week.reissue_reason(self.wk()))
        self.no_issue()
        at = open_events.et(self.wednesday, 11)
        first = open_events.route(SEASON, at, {"week": self.week + 1}, self.root, issue=1)
        second = open_events.route(SEASON, at, {"week": self.week + 1}, self.root, issue=2)
        self.assertEqual([n.key for n in first.fyi], [record["id"]])
        self.assertEqual([n.key for n in second.fyi], [])
        lines = event_inserts.render(first, "career/README.md", at)
        self.assertIn("## FOR YOUR INFORMATION", lines)
        self.assertNotIn("## ACTION REQUIRED", lines)
        self.assertNotIn(event_inserts.ONE_RULE, lines)
        self.assertTrue(any("Trade call from Test Club: withdrawn" in l for l in lines))
        self.assertTrue(any("**Football consequence:** To come." in l for l in lines))

    def test_a_counteroffer_on_a_pending_event_reissues(self):
        record = self.call("test-call-countered")
        self.issue()
        self.assertIsNone(render_game_week.reissue_reason(self.wk()))
        se.midweek(self.root, self.tuesday, 15, 0, self.week)
        open_events.add_process(SEASON, record["id"], {
            "at": open_events.iso(open_events.et(self.tuesday, 14)), "kind": "counter", "by": open_events.OTHER_CLUB,
            "what": "The other club changed its terms.", "source": record["raised"]["source"]}, self.root,
            state="countered")
        self.assertTrue(render_game_week.reissue_reason(self.wk()).startswith("b: counter"))
        # Stone's own criteria-free reading is not a change: a criteria entry alone does not reissue.
        other = self.call("test-call-criteria-only")
        self.issue()
        open_events.add_process(SEASON, other["id"], {
            "at": open_events.iso(open_events.et(self.tuesday, 14, 30)), "kind": "criteria", "by": "caldwell",
            "what": "The need and the terms on the date.", "source": other["raised"]["source"]}, self.root)
        self.assertIsNone(render_game_week.reissue_reason(self.wk()))

    def test_an_exam_date_passing_is_not_a_finding_but_a_medical_entry_is(self):
        wk = self.wk()
        game_day = date.fromisoformat(self.game["date"])
        se.midweek(self.root, game_day - timedelta(days=2), 9, 0, self.week)
        self.assertIsNone(render_game_week.reissue_reason(self.wk()))
        path = wk.paths.roster
        data = json.loads(path.read_text(encoding="utf-8"))
        player = next(p for p in data["players"] if p["list"] == "active"
                      and p["availability"].startswith("No communicated"))
        back = game_day + timedelta(days=30)
        player["availability"] = "Out, short: lower extremity; projected return %s %d, %d" % (
            back.strftime("%B"), back.day, back.year)
        path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        self.assertTrue(render_game_week.reissue_reason(self.wk()).startswith("b: the briefing's own sections"))

    def test_the_insert_order(self):
        kickoff = open_events.kickoff(self.game)
        late = self.call("test-call-due-late", hour=8, due=kickoff - timedelta(hours=2))
        undated = self.call("test-call-undated", hour=9)
        early = self.call("test-call-due-early", hour=10, due=open_events.et(self.wednesday, 16))
        self.news("test-coach-change-before", 7)
        self.issue()
        page = self.page()
        self.assertIn("**Three decisions need your answer.**", page)
        # The due answers first, earliest first; then the answer with no due time.
        places = [page.index(open_events.at_text(open_events.parse_at(r["raised"]["at"]))) for r in (early, late, undated)]
        self.assertEqual(places, sorted(places))
        self.assertIn("**Response due: not set**", page)
        self.assertIn("No deadline is set; no answer is never a yes or a no.", page)
        sections = [page.index(h) for h in event_inserts.HEADINGS if h in page]
        self.assertEqual(sections, sorted(sections))
        # ACTION REQUIRED and FOR YOUR INFORMATION, and COMING UP after them when a window is due (A5).
        windows = deadlines.coming_up(SEASON, open_events.parse_at(render_game_week.issues(self.wk())[-1]["at"]),
                                      self.root)
        self.assertEqual(len(sections), 2 + bool(windows))
        entries = render_game_week.issues(self.wk())[-1]["inserts"]
        self.assertEqual([i.get("event") for i in entries if i["section"] == "action"],
                         [early["id"], late["id"], undated["id"]])
        # The news resolved since the issue before this one is shown under FOR YOUR INFORMATION, after
        # the answers; the reissue rule closes the block.
        self.assertTrue(page.index("## ACTION REQUIRED") < page.index("## FOR YOUR INFORMATION")
                        < page.index(event_inserts.ONE_RULE) < page.index("## 1. "))
        self.assertTrue("Test Club changes its head coach: completed" in page)
        for record in (late, undated, early):
            self.assertFalse(record["id"] in page)
        self.assertEqual(page_errors(self.wk().rel(self.wk().pages.briefing), page, root=self.root), [])

    def test_an_issued_brief_is_rebuilt_as_of_its_own_issue(self):
        first = self.call("test-call-first")
        self.issue()
        page = self.page()
        se.midweek(self.root, self.tuesday, 12, 0, self.week)
        self.call("test-call-second", hour=11)
        wk = self.wk()
        when, revision = render_game_week.current_issue(wk)
        rebuilt = render_game_week.briefing(wk, when, previous=render_game_week.previous_issue(wk), revision=revision)
        self.assertEqual(rebuilt, page)
        # The new call is on the week's index at once (its other business); the briefing stays as issued.
        quiet(render_game_week.write_index, self.root)
        self.assertEqual(render_game_week.validation_errors(self.root), [])
        self.assertEqual(render_game_week.reissue_reason(wk)[:2], "a:")
        self.assertIn(first["id"], [i.get("event") for i in render_game_week.issues(wk)[-1]["inserts"]])

    def test_during_the_bye_no_game_week_is_open(self):
        bye = next(w for w in range(1, 18) if w not in {int(g["week"]) for g in open_events.club_fixtures(SEASON, self.root)})
        (self.root / se.STATE).write_bytes((ROOT / se.STATE).read_bytes())    # the clock as recorded
        before = sorted(p.relative_to(self.root).as_posix() for p in (self.root / "career").rglob("*.md"))
        with mock.patch.object(open_events, "active_bye", return_value=bye):
            wk = self.wk()
            self.assertIsNone(wk.game)
            self.assertEqual(wk.period, {"bye": bye})
            self.assertEqual(open_events.open_period(SEASON, self.root), {"bye": bye})
            self.assertEqual(render_game_week.check(self.root), [])
            self.assertEqual(self.issue(), [])
            from scripts import apply_game_plan, open_game_week
            self.assertEqual(open_game_week.missing(self.root)[0], [])
            self.assertEqual(apply_game_plan.validation_errors(self.root), [])
            from scripts import rebuild_pages
            _, problems = rebuild_pages.rebuild(self.root, check=True)
            self.assertEqual(problems, [])
        after = sorted(p.relative_to(self.root).as_posix() for p in (self.root / "career").rglob("*.md"))
        self.assertEqual(after, before)


class PlanCurrencyTests(unittest.TestCase):
    """F11: an insert-only reissue never unsets an applied plan or an unapplied plan's check."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / "tests"))
        import test_game_plan
        cls.base = test_game_plan

    def setUp(self):
        self.case = self.base.OpenWeek("check")
        self.case.setUp()
        self.addCleanup(self.case.doCleanups)
        self.root = self.case.root
        self.game = se.open_game(self.root)

    def reissue_with_a_call(self, ident):
        clock = open_events.master_clock(self.root)
        raised = clock.at if clock.timed else open_events.et(clock.date, 23)
        open_events.raise_event(se.trade_call(self.root, ident, raised), self.root)
        quiet(render_game_week.write, self.root)

    def plan_problems(self):
        """The plan check with builder C2's wiring of plan_issue_problems into briefing_problems."""
        from scripts import check_game_plan

        def wired(plan):
            when = plan.choices.get("briefing")
            wk = render_game_week.Week(plan.root, plan.week)
            return event_inserts.plan_issue_problems(wk, when)[0]
        with mock.patch.object(check_game_plan, "briefing_problems", wired):
            return self.case.check()

    def test_an_unapplied_plan_stays_checkable_after_an_insert_only_reissue(self):
        self.case.write(self.case.answers())
        answered = render_game_week.current_issue(render_game_week.Week(self.root))
        before = self.plan_problems()[0]
        self.assertFalse(any(p.startswith("Briefing used") for p in before))
        plan = self.case.pages.plan.read_bytes()
        self.reissue_with_a_call("test-call-plan")
        wk = render_game_week.Week(self.root)
        self.assertNotEqual(render_game_week.current_issue(wk), answered)
        problems, notes = event_inserts.plan_issue_problems(wk, {"date": answered[0], "revision": answered[1]})
        self.assertEqual((problems, notes), ([], [event_inserts.NOTE[:1].upper() + event_inserts.NOTE[1:]]))
        self.assertEqual(self.plan_problems()[0], before)
        self.assertEqual(self.case.pages.plan.read_bytes(), plan)
        # A reissue whose own sections changed still needs "Briefing used" brought up to date.
        data = json.loads(wk.paths.roster.read_text(encoding="utf-8"))
        player = next(p for p in data["players"] if p["list"] == "active" and p["availability"].startswith("No communicated"))
        player["availability"] = self.case.out_note()
        wk.paths.roster.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        quiet(render_game_week.write, self.root)
        problems, _ = event_inserts.plan_issue_problems(render_game_week.Week(self.root),
                                                        {"date": answered[0], "revision": answered[1]})
        self.assertTrue(problems and problems[0].startswith("Briefing used: your page answers the briefing of"))

    def test_an_applied_plan_stays_valid_after_an_insert_only_reissue(self):
        from scripts import apply_game_plan
        self.case.exams_held()
        self.case.write(self.case.answers())
        self.case.apply()
        pages = self.case.pages
        frozen = (pages.plan.read_bytes(), pages.call_sheet.read_bytes(), pages.applied.read_bytes())
        self.assertEqual(apply_game_plan.validation_errors(self.root), [])
        self.reissue_with_a_call("test-call-applied")
        self.assertEqual((pages.plan.read_bytes(), pages.call_sheet.read_bytes(), pages.applied.read_bytes()), frozen)
        self.assertEqual(apply_game_plan.validation_errors(self.root), [])
        self.assertIn("## ACTION REQUIRED", pages.briefing.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
