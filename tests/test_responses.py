"""My Responses, its check and its apply (rebuild step 5, A3).

Every event here is test data in a throwaway copy of the checkout (support_events); the real
repository is never written. Weeks and dates come from the fixtures and receipts: the open week is
the first Jacksonville game without a receipt, its mid-week clock its Tuesday.
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
from runtime import decision_queue, decisions, open_events, responses  # noqa: E402
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


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest() if Path(path).is_file() else None


class ResponsesTests(unittest.TestCase):
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

    def call(self, ident, hour=9, due=None, **changes):
        record = se.trade_call(self.root, ident, open_events.et(self.tuesday, hour),
                               due if due is not None else open_events.et(self.wednesday, 16), **changes)
        open_events.raise_event(record, self.root)
        quiet(render_game_week.write, self.root)
        return open_events.get(SEASON, record["id"], self.root)

    def answer(self, heading, text, reason="None additional.", conditions="None."):
        page = self.pages.responses
        content = page.read_text(encoding="utf-8")
        block = responses.blocks_of(content)[heading]
        filled = block.text.replace("**My answer:**\n", "**My answer:** %s\n" % text, 1)
        filled = filled.replace("**My football or professional reason:**\n",
                                "**My football or professional reason:** %s\n" % reason, 1)
        filled = filled.replace("**Conditions or instructions:**\n", "**Conditions or instructions:** %s\n" % conditions, 1)
        page.write_text(content.replace(block.text, filled, 1), encoding="utf-8")

    def apply(self):
        return responses.apply(SEASON, self.period, self.root)

    def test_the_brief_opens_a_block_bound_to_its_event(self):
        record = self.call("test-call-block")
        page = self.pages.responses.read_text(encoding="utf-8")
        self.assertTrue(page.startswith("# Week %d My Responses\n\n" % self.week))
        heading = open_events.title(record)
        self.assertIn("## %s\n\n**My answer:**\n\n**My football or professional reason:**\n" % heading, page)
        binding = responses.record_of(SEASON, self.period, self.root)["blocks"]
        self.assertEqual([(b["heading"], b["event"], b["item"]) for b in binding],
                         [(heading, record["id"], record["queue_item"])])
        # The briefing's answer link goes to that block, and the page shows no id.
        self.assertIn("[%s](My_Responses.md#%s)" % (heading, responses._anchor(heading)),
                      self.pages.briefing.read_text(encoding="utf-8"))
        self.assertFalse(record["id"] in page)
        self.assertEqual(page_errors(self.pages.responses.relative_to(self.root).as_posix(), page, root=self.root), [])
        # A second event with the same title gets its own numbered block; the first block's bytes stay a prefix.
        before = page
        other = self.call("test-call-block-two", hour=10)
        after = self.pages.responses.read_text(encoding="utf-8")
        self.assertTrue(after.startswith(before))
        self.assertIn("## %s (2)\n" % heading, after)
        self.assertIn("(My_Responses.md#%s-2)" % responses._anchor(heading),
                      self.pages.briefing.read_text(encoding="utf-8"))
        self.assertEqual(responses.validation_errors(self.root), [])
        self.assertEqual(open_events.get(SEASON, other["id"], self.root)["state"], "open")

    def test_a_recommendation_is_recorded_and_never_executed(self):
        record = self.call("test-call-oppose")
        heading = open_events.title(record)
        frozen = [digest(p) for p in (self.pages.plan, self.pages.call_sheet, self.pages.applied)]
        self.answer(heading, "I oppose the proposal.", reason="We need the depth at the position.")
        problems, applied = self.apply()
        self.assertEqual((problems, applied), ([], [heading]))
        event = open_events.get(SEASON, record["id"], self.root)
        self.assertEqual(event["state"], "answered")
        self.assertIsNone(event["resolution"])
        self.assertEqual(event["response"]["substance"], {"kind": "oppose"})
        self.assertEqual(event["process"][-1]["kind"], "response")
        item = se.item(self.root, record["queue_item"])
        self.assertEqual((item["status"], item["resolution"]["by"]), ("RESOLVED", "user"))
        self.assertEqual(item["resolution"]["record"], {"path": self.pages.responses.relative_to(self.root).as_posix(),
                                                       "anchor": responses._anchor(heading)})
        page = self.pages.responses.read_text(encoding="utf-8")
        self.assertIn("**Date answered:** %s" % se.long_date(self.tuesday), page)
        # F11: an answer never changes the call sheet, the applied plan or the Game Plan.
        self.assertEqual([digest(p) for p in (self.pages.plan, self.pages.call_sheet, self.pages.applied)], frozen)
        self.assertEqual(open_events.validation_errors(self.root), [])
        self.assertEqual(responses.validation_errors(self.root), [])
        # Run twice, nothing changes.
        snapshot = [digest(p) for p in (self.pages.responses, self.pages.responses_record,
                                        self.root / decision_queue.QUEUE, open_events.path_of(record, self.root))]
        self.assertEqual(self.apply(), ([], []))
        self.assertEqual([digest(p) for p in (self.pages.responses, self.pages.responses_record,
                                              self.root / decision_queue.QUEUE, open_events.path_of(record, self.root))],
                         snapshot)
        # An applied block is frozen: changing it fails validation and the check.
        self.pages.responses.write_text(page.replace("I oppose the proposal.", "I support the proposal."), encoding="utf-8")
        self.assertTrue(any("an applied block stays as written" in e for e in responses.validation_errors(self.root)))
        self.assertTrue(any("stays as written" in p for p in responses.check(SEASON, self.period, self.root).problems))

    def test_a_blank_block_leaves_the_item_open(self):
        record = self.call("test-call-blank")
        self.assertEqual(self.apply(), ([], []))
        self.assertEqual(se.item(self.root, record["queue_item"])["status"], "OPEN")
        notes = responses.check(SEASON, self.period, self.root).notes
        self.assertTrue(any("still open; no answer yet" in n for n in notes))

    def test_f10_an_unanswered_block_past_its_due_time_is_reported_not_resolved(self):
        record = self.call("test-call-due", due=open_events.et(self.tuesday, 10))
        checked = responses.check(SEASON, self.period, self.root)
        self.assertEqual(checked.problems, [])
        self.assertTrue(any("past its due time" in n for n in checked.notes))
        self.assertEqual(self.apply(), ([], []))
        self.assertEqual(se.item(self.root, record["queue_item"])["status"], "OPEN")
        self.assertEqual(open_events.get(SEASON, record["id"], self.root)["state"], "open")
        self.assertEqual([i["id"] for i in decision_queue.overdue_items(decision_queue.load(self.root),
                                                                      open_events.master_at(self.root))],
                         [record["queue_item"]])

    def test_two_wordings_of_one_answer_compile_to_the_same_substance(self):
        record = self.call("test-call-words")
        for one, two in (("Oppose.", "I am against this trade, and I oppose it."),
                         ("Support it.", "I support the proposal."),
                         ("Let it lapse.", "Let the deadline pass.")):
            self.assertEqual(responses.compile_substance(one, "None.", record),
                             responses.compile_substance(two, "None.", record))
        self.assertEqual(responses.compile_substance("Support it only if we keep a second tight end.", "None.", record),
                         {"kind": "condition", "condition": "we keep a second tight end"})
        self.assertIsNone(responses.compile_substance("Talk to me about it.", "None.", record))
        # A recommendation of a named option.
        option = {"name": "Test Player", "position": "WR", "basis": "On the practice squad",
                  "source": record["raised"]["source"]}
        self.assertEqual(responses.compile_substance("Recommend Test Player.", "", dict(record, options=[option])),
                         {"kind": "recommend", "option": "Test Player"})

    def test_none_needed_for_a_standing_answered_event(self):
        record = self.call("test-call-standing")
        heading = open_events.title(record)
        path = open_events.path_of(record, self.root)
        data = json.loads(path.read_text(encoding="utf-8"))
        path.write_text(json.dumps(dict(data, stone_part="standing:stone-not-open-to-job-offers")), encoding="utf-8")
        self.answer(heading, "Support it.")
        problems = responses.check(SEASON, self.period, self.root).problems
        self.assertTrue(any(p.startswith("%s: None needed: your standing instruction answers it" % heading)
                            and "to change that, write the new rule" in p for p in problems), problems)

    def test_leave_open_until_a_date_before_its_due_time(self):
        record = self.call("test-call-leave")
        heading = open_events.title(record)
        self.answer(heading, "Leave this open until %s %d." % (self.wednesday.strftime("%B"), self.wednesday.day))
        checked = responses.check(SEASON, self.period, self.root)
        self.assertEqual(checked.problems, [])
        self.assertTrue(any("left open until" in n for n in checked.notes))
        self.assertEqual(self.apply(), ([], []))
        self.assertEqual(se.item(self.root, record["queue_item"])["status"], "OPEN")
        later = self.wednesday + timedelta(days=3)
        page = self.pages.responses.read_text(encoding="utf-8")
        self.pages.responses.write_text(page.replace("until %s %d." % (self.wednesday.strftime("%B"), self.wednesday.day),
                                                     "until %s %d." % (later.strftime("%B"), later.day)), encoding="utf-8")
        self.assertTrue(any("cannot be left open past its due time" in p
                            for p in responses.check(SEASON, self.period, self.root).problems))

    def test_names_must_be_on_the_roster_or_the_coach_records(self):
        record = self.call("test-call-names")
        heading = open_events.title(record)
        self.answer(heading, "Support it only if Zebulon Quartermaine stays.")
        self.assertTrue(any("Zebulon Quartermaine is not on the roster or the coach records" in p
                            for p in responses.check(SEASON, self.period, self.root).problems))
        roster = json.loads(open_events.SeasonPaths(SEASON, self.root).roster.read_text(encoding="utf-8"))
        player = next(p["name"] for p in roster["players"] if p["list"] == "active")
        self.answer(heading, "Support it only if %s stays." % player)

    def test_an_answer_for_a_resolved_event_is_refused(self):
        record = self.call("test-call-resolved")
        heading = open_events.title(record)
        open_events.add_process(SEASON, record["id"], {
            "at": open_events.iso(open_events.et(self.tuesday, 10)), "kind": "withdrawn_by_other_side",
            "by": open_events.OTHER_CLUB, "what": "The other club withdrew its proposal.",
            "source": record["raised"]["source"]}, self.root)
        rel = open_events.path_of(record, self.root).relative_to(self.root.resolve()).as_posix()
        se.settle(self.root, record["queue_item"], "WITHDRAWN", {
            "date": self.tuesday.isoformat(), "by": "organization", "record": {"path": rel, "pointer": "/process/0"},
            "summary": "%s: withdrawn." % open_events.OTHER_SIDE_SUMMARY})
        page = se.result_page(self.root, record, "Trade_Result_test.md", self.tuesday)
        open_events.resolve(SEASON, record["id"], {
            "at": open_events.iso(open_events.et(self.tuesday, 10, 15)), "outcome": "withdrawn",
            "by": open_events.OTHER_CLUB, "decision": {"text": "Withdrawn.", "author": "David Caldwell",
                                                       "date": self.tuesday.isoformat(), "criteria": None},
            "result_page": page}, self.root)
        self.answer(heading, "Oppose.")
        self.assertTrue(any("this question is settled" in p for p in responses.check(SEASON, self.period, self.root).problems))
        upload = self.root / "upload.md"
        upload.write_text(self.pages.responses.read_text(encoding="utf-8"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "this question is settled"):
            responses.place_upload(self.root, SEASON, self.period, upload)

    def test_an_upload_is_checked_before_anything_is_written(self):
        record = self.call("test-call-upload")
        heading = open_events.title(record)
        before = {p: digest(p) for p in (self.pages.responses, self.pages.plan, self.pages.responses_record)}
        text = self.pages.responses.read_text(encoding="utf-8")
        upload = self.root / "upload.md"
        upload.write_text(text + "\n## A heading of my own\n\n**My answer:** Yes.\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "not a notice of"):
            responses.place_upload(self.root, SEASON, self.period, upload)
        self.assertEqual({p: digest(p) for p in before}, before)
        with self.assertRaisesRegex(ValueError, "a .md or .txt file"):
            responses.place_upload(self.root, SEASON, self.period, self.root / "upload.json")
        # A good upload writes only My Responses; the Game Plan is never touched.
        upload.write_text(text.replace("**My answer:**\n", "**My answer:** Oppose.\n", 1), encoding="utf-8")
        responses.place_upload(self.root, SEASON, self.period, upload)
        self.assertEqual(digest(self.pages.plan), before[self.pages.plan])
        self.assertEqual(self.apply()[1], [heading])
        # An upload that changes an applied block is refused, and nothing is written.
        upload.write_text(self.pages.responses.read_text(encoding="utf-8").replace("Oppose.", "Support it."),
                          encoding="utf-8")
        applied = digest(self.pages.responses)
        with self.assertRaisesRegex(ValueError, "stays as written"):
            responses.place_upload(self.root, SEASON, self.period, upload)
        self.assertEqual(digest(self.pages.responses), applied)
        # The reserved headings are builder C's, never flagged here.
        responses.append_block(self.period, decisions.PRACTICE_WEEK, None, self.root, SEASON)
        self.assertEqual(responses.check(SEASON, self.period, self.root).problems, [])
        self.assertEqual(open_events.get(SEASON, record["id"], self.root)["response"]["substance"], {"kind": "oppose"})

    def test_a_revision_is_a_new_block(self):
        record = self.call("test-call-revised")
        heading = open_events.title(record)
        self.answer(heading, "Oppose.")
        self.apply()
        item = se.item(self.root, record["queue_item"])
        responses.append_block(self.period, responses.REVISED + heading, item, self.root, SEASON)
        self.answer(responses.REVISED + heading, "Support it.")
        self.assertEqual(self.apply()[1], [responses.REVISED + heading])
        event = open_events.get(SEASON, record["id"], self.root)
        self.assertEqual(event["response"]["substance"], {"kind": "support"})
        self.assertEqual([e["kind"] for e in event["process"]], ["response", "response"])
        self.assertEqual(responses.validation_errors(self.root), [])
        self.assertEqual(open_events.validation_errors(self.root), [])


if __name__ == "__main__":
    unittest.main()
