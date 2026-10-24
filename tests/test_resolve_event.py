"""One result page per resolved event (rebuild step 5, A4; docs/event_inserts.md F12 to F15).

The real repository is only read (a week with no results keeps its index bytes); every event here
is test data in a throwaway copy of the checkout (support_events), never the real one. Weeks and
dates come from the fixtures and receipts: the open week is the first Jacksonville game without a
receipt, its mid-week clock its Tuesday, so the tests hold at any later clock.
"""
import contextlib
from datetime import timedelta
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from release_staging import IGNORED  # noqa: E402
import support_events as se  # noqa: E402
from runtime import decision_queue, decisions, event_inserts, game_report, open_events, responses  # noqa: E402
from runtime.clean_pages import page_errors  # noqa: E402
from runtime.events import EVENT_META, annual_record_path  # noqa: E402
from scripts import render_game_week, resolve_event  # noqa: E402

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


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest() if Path(path).is_file() else None


class RealIndexTests(unittest.TestCase):
    def test_a_week_with_no_results_keeps_its_index_bytes(self):
        if open_events.load(SEASON, ROOT):
            self.skipTest("the season has recorded events")
        for week in render_game_week.page_weeks(ROOT):
            wk = render_game_week.Week(ROOT, week)
            self.assertEqual(render_game_week.index_page(wk), wk.pages.readme.read_text(encoding="utf-8"),
                             "Week %d" % week)
            self.assertEqual(event_inserts.other_business(SEASON, wk.period, wk.rel(wk.pages.readme), ROOT), [])
        self.assertEqual(resolve_event.check(ROOT, SEASON), [])


class ReportLinkTests(unittest.TestCase):
    """F15: the week's report links each result and never pastes one (no store is read)."""

    def results(self):
        page = "career/%s/x/Trade_Result_2000-01-04_Test_Club.md"
        out = []
        for n, club in enumerate(("Test Club", "Other Test Club")):
            out.append({"subject": club, "summary": {"text": "A test call from another club about a trade number %d."
                                                     % n},
                        "process": [{"what": "The other club withdrew the call before any answer was given."}],
                        "resolution": {"result_page": page % ("dir%d" % n), "decision": {"text": "Declined."}}})
        return out

    def test_each_result_is_linked_and_none_is_pasted(self):
        results = self.results()
        rel = "career/dir0/report/Game_Report.md"
        linked = "# Report\n\n[one](../x/Trade_Result_2000-01-04_Test_Club.md); " \
                 "[two](../../dir1/x/Trade_Result_2000-01-04_Test_Club.md#outcome).\n"
        self.assertEqual(game_report.result_link_errors(linked, results, rel), [])
        # Without the report's own path a link to a page of the same name counts.
        self.assertEqual(game_report.result_link_errors("[one](a/Trade_Result_2000-01-04_Test_Club.md)", results), [])
        # A link to a page of the same name elsewhere is not the result's.
        wrong = "# Report\n\n[one](../x/Trade_Result_2000-01-04_Test_Club.md); " \
                "[two](../../dir2/x/Trade_Result_2000-01-04_Test_Club.md).\n"
        self.assertEqual(len(game_report.result_link_errors(wrong, results, rel)), 1)
        missing = "# Report\n\n[one](../x/Trade_Result_2000-01-04_Test_Club.md).\n"
        errors = game_report.result_link_errors(missing, results, rel)
        self.assertEqual(len(errors), 1)
        self.assertIn("Other Test Club", errors[0])
        pasted = linked + "\nA test call from another club about a trade number 0.\n"
        self.assertTrue(any("copies the result" in e for e in game_report.result_link_errors(pasted, results, rel)))
        pasted = linked + "\nThe other club withdrew the call before any answer was given.\n"
        self.assertTrue(any("copies the result" in e for e in game_report.result_link_errors(pasted, results, rel)))
        # A short decision text that recurs is not a copy.
        self.assertEqual(game_report.result_link_errors(linked + "\nDeclined.\n", results, rel), [])


class ResolveTests(unittest.TestCase):
    def setUp(self):
        self.root = copy_repo(self)
        self.game = se.open_game(self.root)
        if self.game is None:
            self.skipTest("every regular-season game has closed")
        self.week = int(self.game["week"])
        self.period = {"week": self.week}
        self.tuesday = se.tuesday_before(self.game)
        self.wednesday = self.tuesday + timedelta(days=1)
        se.midweek(self.root, self.tuesday, 10, 30, self.week)
        self.pages = decisions.week_pages(SEASON, self.week, self.root)
        self.source = se.source_page(self.root, "trade_talks")

    # ---------------------------------------------------------------- helpers
    def at(self, day, hour, minute=0):
        return open_events.et(day, hour, minute)

    def call(self, ident, hour=9, due=None, subject="Test Club"):
        record = se.trade_call(self.root, ident, self.at(self.tuesday, hour),
                               due if due is not None else self.at(self.wednesday, 16), subject=subject,
                               source=self.source)
        open_events.raise_event(record, self.root)
        quiet(render_game_week.write, self.root)
        return open_events.get(SEASON, record["id"], self.root)

    def entry(self, event_id, kind, when, what, by="caldwell", state=None):
        open_events.add_process(SEASON, event_id, {"at": open_events.iso(when), "kind": kind, "what": what, "by": by,
                                                   "source": {"path": self.source}}, self.root, state=state)

    def criteria(self, event_id, when):
        self.entry(event_id, "criteria", when, "The need at the position, the legal options on the date, the contract "
                                               "facts and the other club's terms, each on file.")

    def answer(self, record, text):
        heading = event_inserts.answer_heading(open_events.Route(season=SEASON, period=self.period, root=self.root),
                                               record["id"], open_events.title(record))
        page = self.pages.responses
        content = page.read_text(encoding="utf-8")
        block = responses.blocks_of(content)[heading]
        filled = block.text.replace("**My answer:**\n", "**My answer:** %s\n" % text, 1)
        filled = filled.replace("**My football or professional reason:**\n",
                                "**My football or professional reason:** The depth at the position.\n", 1)
        filled = filled.replace("**Conditions or instructions:**\n", "**Conditions or instructions:** None.\n", 1)
        page.write_text(content.replace(block.text, filled, 1), encoding="utf-8")
        self.assertEqual(responses.apply(SEASON, self.period, self.root)[0], [])

    def resolve(self, event_id, outcome, when, by="caldwell", decision="Caldwell declined the call; the roster stays "
                "as it is.", **kwargs):
        return resolve_event.resolve(self.root, SEASON, event_id, outcome, by, open_events.iso(when), decision,
                                     **kwargs)

    def page_of(self, event_id):
        record = open_events.get(SEASON, event_id, self.root)
        return self.root / record["resolution"]["result_page"]

    def assert_valid(self):
        self.assertEqual(open_events.validation_errors(self.root), [])
        self.assertEqual(responses.validation_errors(self.root), [])
        self.assertEqual(resolve_event.check(self.root, SEASON), [])
        self.assertEqual(render_game_week.check(self.root), [])

    # ---------------------------------------------------------------- tests
    def test_f12_f14_a_call_resolved_on_tuesday_is_readable_on_tuesday(self):
        held = decision_queue.blocking_errors([decision_queue.event("week_inputs", SEASON, self.week)], self.root)
        first = self.call("test-call-first")
        self.criteria(first["id"], self.at(self.tuesday, 9, 30))
        self.answer(first, "I oppose the proposal.")
        se.midweek(self.root, self.tuesday, 15, 0, self.week)
        written = self.resolve(first["id"], "declined", self.at(self.tuesday, 14))
        page = self.page_of(first["id"])
        self.assertIn(page, [Path(p) for p in written])
        self.assertEqual(page.parent, decisions.event_folder("trade_talks", SEASON, self.root))
        self.assertEqual(page.name, "Trade_Result_%s_Test_Club.md" % self.tuesday.isoformat())
        text = page.read_text(encoding="utf-8")
        # F12: its fields, the triggering fact, the deciding party, the time and its event line.
        for field in ("# Trade Result: Test Club", "**Event date:** %s" % resolve_event.long_at(self.at(self.tuesday, 9)),
                      "**Resolved on:** %s" % resolve_event.long_at(self.at(self.tuesday, 14)),
                      "**Involving:** Test Club; David Caldwell, who decides; Alex Stone, who recommends.",
                      "**What happened:** A test call from another club about a trade.",
                      "**Stone's answer:** Opposed it (answered", "](../../Regular_Season/",
                      "**Final decision:** David Caldwell, who decides: Caldwell declined the call",
                      "The decision applies the criteria David Caldwell recorded on", "**Outcome:** Declined.",
                      "**Changes effective:** No contract, roster, staff or employment change.",
                      "**Outstanding issue:** None.", "**Source records:** [Test source]"):
            self.assertIn(field, text)
        lines = [json.loads(m) for m in EVENT_META.findall(text)]
        self.assertEqual([line["id"] for line in lines], [first["id"]])
        self.assertEqual(lines[0]["date"], self.tuesday.isoformat())
        self.assertNotIn(first["id"], text.replace(EVENT_META.search(text)[0], ""))
        rel = page.relative_to(self.root).as_posix()
        self.assertEqual(page_errors(rel, text, root=self.root), [])
        # Readable on Tuesday: Record.md lists it and the week's index links it, before the game.
        record_md = annual_record_path(self.root, SEASON).read_text(encoding="utf-8")
        self.assertIn("David Caldwell declined the trade call from Test Club. [Full record](", record_md)
        index = self.pages.readme.read_text(encoding="utf-8")
        self.assertIn(event_inserts.OTHER_BUSINESS, index)
        self.assertIn("(../../../Team_Operations/Trades/%s)" % page.name, index)
        # The item is settled by his answer, the event resolved, and the week's holds are unchanged.
        self.assertEqual(se.item(self.root, first["queue_item"])["status"], "RESOLVED")
        self.assertEqual(decision_queue.blocking_errors([decision_queue.event("week_inputs", SEASON, self.week)],
                                                        self.root), held)
        # F14: a second negotiation still open has its dated process entries and no result.
        second = self.call("test-call-second", hour=11, subject="Other Test Club")
        se.midweek(self.root, self.tuesday, 16, 0, self.week)
        self.entry(second["id"], "counter", self.at(self.tuesday, 15, 30), "The other club changed its terms.",
                   by="other_club", state="countered")
        quiet(render_game_week.write, self.root)
        second = open_events.get(SEASON, second["id"], self.root)
        self.assertEqual((second["state"], second["resolution"], len(second["process"])), ("countered", None, 1))
        folder = decisions.event_folder("trade_talks", SEASON, self.root)
        self.assertEqual(sorted(p.name for p in folder.glob("Trade_Result_*.md")), [page.name])
        index = self.pages.readme.read_text(encoding="utf-8")
        self.assertIn("Trade call from Other Test Club", index)
        self.assertIn("| Open | Due %s |" % open_events.at_text(self.at(self.wednesday, 16)), index)
        self.assert_valid()

    def test_f13_five_events_in_one_week_give_five_pages_and_five_links(self):
        a = self.call("test-call-declined", hour=8)
        b = self.call("test-call-rejected", hour=9, subject="Second Test Club")
        c = self.call("test-call-withdrawn", hour=10, subject="Third Test Club")
        injury = se.injury_replacement(self.root, "test-roster-question", self.at(self.tuesday, 10, 15), self.game,
                                       short=False)
        open_events.raise_event(injury, self.root)
        news_source = se.source_page(self.root, "head_coach_change")
        news = {"schema": open_events.SCHEMA, "id": "%s-test-head-coach-change" % self.tuesday.isoformat(),
                "kind": "head_coach_change", "season": SEASON, "subject": "Test Club",
                "raised": {"at": open_events.iso(self.at(self.tuesday, 10, 20)), "by": "communications_staff",
                           "source": {"path": news_source}},
                "known_to": ["stone", "communications_staff"], "authority": {"rows": ["1"], "decides": "other_club"},
                "stone_part": "none", "summary": {"text": "A test notice of another club's coaching change.",
                                                  "author": "Team communications staff",
                                                  "date": self.tuesday.isoformat()},
                "staff_position": None, "consequence": None, "facts": [], "options": [], "deadline": None,
                "state": "open", "process": [], "queue_item": None, "response": None, "resolution": None}
        open_events.raise_event(news, self.root)
        quiet(render_game_week.write, self.root)
        for record in (a, b):
            self.criteria(record["id"], self.at(self.tuesday, 10, 25))
        self.criteria(injury["id"], self.at(self.tuesday, 10, 25))
        self.answer(a, "I oppose the proposal.")
        self.answer(b, "I support the proposal.")
        se.midweek(self.root, self.wednesday, 12, 0, self.week)
        self.resolve(a["id"], "declined", self.at(self.wednesday, 9))
        self.resolve(b["id"], "rejected", self.at(self.wednesday, 9, 30), decision="Caldwell rejected the terms.")
        self.entry(c["id"], "withdrawn_by_other_side", self.at(self.wednesday, 10), "The other club withdrew its call.",
                   by="other_club")
        self.resolve(c["id"], "withdrawn", self.at(self.wednesday, 10, 5), by="other_club",
                     decision="The club withdrew its call before an answer was given.")
        self.entry(injury["id"], "medical", self.at(self.wednesday, 10, 30),
                   "The medical staff cleared the player for the next game.", by="medical_staff")
        self.resolve(injury["id"], "no_move", self.at(self.wednesday, 11), decision="Caldwell made no roster move.")
        news_page = se.result_page(self.root, news, "Head_Coach_Change_%s_Test_Club.md" % self.wednesday.isoformat(),
                                   self.wednesday, summary="Test Club changed its head coach in a test.")
        self.resolve(news["id"], "executed", self.at(self.wednesday, 11, 30), by="other_club",
                     decision="The club named an interim head coach from its staff.", result=news_page)
        pages = [self.page_of(r["id"]) for r in (a, b, c, injury, news)]
        self.assertEqual(len(set(pages)), 5)
        self.assertTrue(all(p.is_file() for p in pages))
        index = self.pages.readme.read_text(encoding="utf-8")
        table = index.split(event_inserts.OTHER_BUSINESS, 1)[1]
        for page in pages:
            self.assertEqual(table.count(page.name), 1, page.name)
        self.assertEqual(sorted(p.name for p in self.pages.folder.glob("My_Responses*.md")), ["My_Responses.md"])
        record_md = annual_record_path(self.root, SEASON).read_text(encoding="utf-8")
        for page in pages:
            self.assertIn(Path(page).name + ")", record_md)
        # Stone's item for the withdrawn call is withdrawn by the organization, naming the club's act.
        item = se.item(self.root, c["queue_item"])
        self.assertEqual((item["status"], item["resolution"]["by"]), ("WITHDRAWN", "organization"))
        self.assertIn(open_events.OTHER_SIDE_SUMMARY, item["resolution"]["summary"])
        self.assertIn("No answer was given; the question ended before he answered.",
                      self.page_of(c["id"]).read_text(encoding="utf-8"))
        medical = se.item(self.root, open_events.get(SEASON, injury["id"], self.root)["queue_item"])
        self.assertEqual((medical["status"], medical["resolution"]["by"]), ("WITHDRAWN", "medical"))
        self.assert_valid()

    def test_two_results_of_one_kind_date_and_subject_get_two_files(self):
        one = self.call("test-call-one")
        two = self.call("test-call-two", hour=10)
        for record in (one, two):
            self.criteria(record["id"], self.at(self.tuesday, 10, 10))
            self.answer(record, "I oppose the proposal.")
        se.midweek(self.root, self.tuesday, 15, 0, self.week)
        self.resolve(one["id"], "declined", self.at(self.tuesday, 13))
        self.resolve(two["id"], "declined", self.at(self.tuesday, 14))
        stem = "Trade_Result_%s_Test_Club" % self.tuesday.isoformat()
        self.assertEqual((self.page_of(one["id"]).name, self.page_of(two["id"]).name), (stem + ".md", stem + "_2.md"))
        self.assert_valid()

    def test_refusals_write_nothing(self):
        record = self.call("test-call-refused")
        watched = [self.root / decision_queue.QUEUE, open_events.path_of(record, self.root),
                   annual_record_path(self.root, SEASON), self.pages.readme]
        later = self.at(self.tuesday, 10)

        def refused(outcome, when=later, by="caldwell", text="Caldwell declined the call.", **kwargs):
            before = [digest(p) for p in watched]
            with self.assertRaises(resolve_event.Refused) as caught:
                self.resolve(record["id"], outcome, when, by=by, decision=text, **kwargs)
            self.assertEqual([digest(p) for p in watched], before)
            return str(caught.exception)

        # Executing (or accepting) a trade is not built: the plain message.
        self.assertEqual(refused("executed"), resolve_event.TRADE_NOT_BUILT)
        self.assertEqual(refused("accepted"), resolve_event.TRADE_NOT_BUILT)
        # A decision by the general manager without its criteria.
        self.assertIn("decides only from criteria", refused("declined"))
        # His answer is still open, and no other side ended the question: the event waits on it.
        self.criteria(record["id"], self.at(self.tuesday, 9, 30))
        self.assertIn("the event waits on", refused("declined"))
        # Criteria recorded after his answer do not count.
        self.answer(record, "I oppose the proposal.")
        self.entry(record["id"], "criteria", self.at(self.tuesday, 10, 30), "A later look at the same terms.")
        self.assertIn("after Stone's answer", refused("declined", when=self.at(self.tuesday, 10, 30), criteria=2))
        # After the clock, unclean words, lapsing without his permission, and a built outcome with a page.
        self.assertIn("after the master date/time", refused("declined", when=self.at(self.tuesday, 11)))
        self.assertIn("football words", refused("declined", text="The engine says no."))
        self.assertIn("lapses only with", refused("lapsed"))
        self.assertIn("takes no --result", refused("rejected", by="other_club", result=self.source))
        self.assertEqual(list(decisions.event_folder("trade_talks", SEASON, self.root).glob("Trade_Result_*.md")), [])
        # With the criteria before his answer it resolves.
        self.resolve(record["id"], "declined", self.at(self.tuesday, 10, 30), criteria=0)
        self.assertEqual(open_events.get(SEASON, record["id"], self.root)["state"], "resolved")

    def test_an_unanswered_injury_replacement_is_decided_at_its_due_time(self):
        record = se.injury_replacement(self.root, "test-roster-due", self.at(self.tuesday, 9), self.game, short=False)
        open_events.raise_event(record, self.root)
        quiet(render_game_week.write, self.root)
        self.criteria(record["id"], self.at(self.tuesday, 9, 30))
        kickoff = open_events.kickoff(self.game)
        game_day = kickoff.date()
        # Before the due time his open item holds the event.
        with self.assertRaises(resolve_event.Refused):
            self.resolve(record["id"], "no_move", self.at(self.tuesday, 10), decision="Caldwell made no roster move.")
        se.set_clock(self.root, "%s, after the %d p.m. ET record of the Week %d preparation (a test record)"
                     % (se.long_date(game_day), (kickoff.hour + 1) % 12 or 12, self.week))
        self.resolve(record["id"], "no_move", kickoff + timedelta(minutes=30), decision="Caldwell made no roster move.")
        item = se.item(self.root, record["id"])
        self.assertEqual((item["status"], item["resolution"]["by"], item["resolution"]["summary"]),
                         ("WITHDRAWN", "organization", open_events.DUE_TIME_SUMMARY))
        text = self.page_of(record["id"]).read_text(encoding="utf-8")
        self.assertIn("**Stone's answer:** No recommendation was given;", text)
        self.assertEqual(open_events.validation_errors(self.root), [])
        self.assertEqual(resolve_event.check(self.root, SEASON), [])

    def test_a_built_page_is_held_to_its_record(self):
        record = self.call("test-call-checked")
        self.criteria(record["id"], self.at(self.tuesday, 9, 30))
        self.answer(record, "I oppose the proposal.")
        self.resolve(record["id"], "declined", self.at(self.tuesday, 10, 30), closure=True)
        page = self.page_of(record["id"])
        line = json.loads(EVENT_META.findall(page.read_text(encoding="utf-8"))[0])
        self.assertEqual(line["closure"]["through"], self.tuesday.isoformat())
        self.assertTrue(line["closure"]["checkpoint"].startswith("Canonical update - %s - " % se.long_date(self.tuesday)))
        self.assertEqual(resolve_event.check(self.root, SEASON), [])
        original = page.read_text(encoding="utf-8")
        page.write_text(original.replace("Declined.", "Declined, firmly."), encoding="utf-8")
        self.assertTrue(any("differs from its event's record" in e for e in resolve_event.check(self.root, SEASON)))
        # The rebuild writes the page back from its record, its closure kept.
        self.assertEqual(resolve_event.built_pages(self.root, SEASON), [(page, original)])
        page.write_text(original, encoding="utf-8")
        self.assertEqual(resolve_event.check(self.root, SEASON), [])
        # The script's own check of a resolution writes nothing.
        self.assertEqual(quiet(resolve_event.main, ["--season", str(SEASON), "--check", "--root", str(self.root)]), 0)


if __name__ == "__main__":
    unittest.main()
