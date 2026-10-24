"""The open-event store, the clock inside a week, the queue links and the hold (rebuild step 5, A1).

Every event here is test data in one throwaway copy of the checkout (support_events); the real
repository is never written. Weeks and dates come from the fixtures and the receipts: the open week
is the first Jacksonville game without a receipt, the mid-week clock its Tuesday, so the tests hold
at any later clock. The queue and Document 5 are restored after each test.
"""
from datetime import date, timedelta
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from release_staging import copied_root  # noqa: E402
import support_events as se  # noqa: E402
from runtime import current_job, decision_queue, open_events  # noqa: E402
from runtime.decision_queue import event  # noqa: E402
from runtime.events import load_events, repository_map  # noqa: E402
from runtime.player_bios import master_date  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402

SEASON = se.SEASON


def reference_holds(item, ev):
    """The hold before step 5: an OPEN item holds an event one of its blocks, or an event a block
    implies, equals."""
    implied = {"week_inputs": ("week_close",), "season_stage": ("season_opening",)}
    if item.get("status") != "OPEN":
        return False
    for block in item.get("blocks") or ():
        if ev == block or any(ev == dict(block, kind=k) for k in implied.get(block.get("kind"), ())):
            return True
    return False


class OpenEventTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.game = se.open_game(ROOT)
        if cls.game is None:
            raise unittest.SkipTest("every regular-season game has closed")
        cls.week = int(cls.game["week"])
        cls.root = copied_root(SimpleNamespace(addCleanup=cls.addClassCleanup))
        for record in cls.root.glob("career/**/paused_game.json"):
            record.unlink()
        cls.tuesday = se.tuesday_before(cls.game)
        cls.kickoff = open_events.kickoff(cls.game)
        cls.mapping = repository_map(cls.root)

    def setUp(self):
        for rel in (str(decision_queue.QUEUE), se.STATE):
            path = self.root / rel
            before = path.read_bytes()
            self.addCleanup(path.write_bytes, before)
        for folder in open_events.stores(SEASON, self.root):
            self.addCleanup(self._clear, folder)
        se.midweek(self.root, self.tuesday, 10, 30, self.week)

    @staticmethod
    def _clear(folder):
        for path in folder.glob("*.json") if folder.is_dir() else ():
            path.unlink()

    def queue_errors(self):
        job = current_job.load(self.root)
        return decision_queue.validation_errors(self.root, self.mapping, load_events(self.root, self.mapping),
                                                master_date(self.root), job)

    def assertError(self, text, errors):
        self.assertTrue(any(text in e for e in errors), "%r not in %r" % (text, errors))

    def raise_(self, record):
        open_events.raise_event(record, self.root)
        return open_events.get(SEASON, record["id"], self.root)

    def holds_any_week(self, item):
        evs = [event(k, SEASON, w) for w in range(1, 22) for k in ("week_inputs", "week_close")]
        evs += [event("call_sheet_part", SEASON, w, part=p) for w in range(1, 22) for p in decision_queue.SHEET_PARTS]
        return [ev for ev in evs if decision_queue.holds(item, ev)]

    # ---- the clock
    def test_master_at_reads_the_three_forms(self):
        game_day = date.fromisoformat(self.game["date"])
        se.set_clock(self.root, "%s, after the game-day clock advance for Week %d" % (se.long_date(game_day), self.week))
        clock = open_events.master_clock(self.root)
        self.assertEqual((clock.at, clock.timed), (open_events.et(game_day), False))
        se.set_clock(self.root, "%s, after the Week %d game (a test score)" % (se.long_date(game_day), self.week))
        self.assertEqual(open_events.master_at(self.root), self.kickoff)
        se.midweek(self.root, self.tuesday, 10, 30, self.week)
        clock = open_events.master_clock(self.root)
        self.assertEqual((clock.at, clock.timed), (open_events.et(self.tuesday, 10, 30), True))
        se.set_clock(self.root, "%s, a line with no time" % se.long_date(self.tuesday))
        self.assertEqual(open_events.master_at(self.root), open_events.et(self.tuesday))
        # The offset is ET's on the date: daylight time ends on the first Sunday of November.
        first_sunday = next(date(SEASON, 11, d) for d in range(1, 8) if date(SEASON, 11, d).weekday() == 6)
        self.assertEqual(open_events.et(first_sunday - timedelta(days=1)).utcoffset(), timedelta(hours=-4))
        self.assertEqual(open_events.et(first_sunday).utcoffset(), timedelta(hours=-5))
        with self.assertRaises(ValueError):
            open_events.parse_at("%sT16:00:00" % self.tuesday.isoformat())
        with self.assertRaises(ValueError):
            open_events.parse_at("%sT16:00:00-05:00" % self.tuesday.isoformat())

    def test_the_new_form_reads_as_its_date_everywhere(self):
        from scripts import render_career_views as views
        from scripts.validate_repository import validate
        self.assertEqual(master_date(self.root), self.tuesday)
        ctx = views.context(self.root)
        self.assertEqual(ctx.master, self.tuesday)
        last, upcoming = views.last_and_next(ctx)
        self.assertEqual(upcoming["week"], self.week)
        self.assertLess(date.fromisoformat(last["date"]), self.tuesday)
        errors = validate(self.root)
        self.assertFalse(any("Cannot parse master date/time" in e for e in errors))
        # The mid-week record moves the clock without a closed event line (an event raised or answered),
        # so the latest closure is behind it; the validator allows that in this form only (rehearsal r4).
        from scripts.validate_repository import MASTER_CLOSURE
        self.assertNotIn(MASTER_CLOSURE, errors)

    def test_only_the_mid_week_form_runs_ahead_of_the_latest_closure(self):
        from scripts.validate_repository import MASTER_CLOSURE, master_closure_error as error
        midweek = "%s, after the 10:30 a.m. ET record of the Week %d preparation (a test record)" % (
            se.long_date(self.tuesday), self.week)
        game_day = "%s, after the game-day clock advance for Week %d" % (se.long_date(self.tuesday), self.week)
        earlier = self.tuesday - timedelta(days=2)
        self.assertIsNone(error(midweek, self.tuesday, earlier))
        self.assertIsNone(error(midweek, self.tuesday, self.tuesday))
        self.assertEqual(error(midweek, self.tuesday, self.tuesday + timedelta(days=1)), MASTER_CLOSURE)
        self.assertIsNone(error(game_day, self.tuesday, self.tuesday))
        self.assertEqual(error(game_day, self.tuesday, earlier), MASTER_CLOSURE)
        self.assertEqual(error(None, self.tuesday, earlier), MASTER_CLOSURE)

    def test_an_event_raised_after_the_clock_fails(self):
        late = open_events.et(self.tuesday, 11)
        with self.assertRaisesRegex(open_events.Refused, "after the master date/time"):
            open_events.raise_event(se.trade_call(self.root, "test-late-call", late), self.root)
        # A line with no time is read by its date: any time that day is on the clock.
        se.set_clock(self.root, "%s, a line with no time" % se.long_date(self.tuesday))
        self.raise_(se.trade_call(self.root, "test-same-day-call", late))
        with self.assertRaisesRegex(open_events.Refused, "after the master date/time"):
            open_events.raise_event(se.trade_call(self.root, "test-next-day-call", late + timedelta(days=1)),
                                    self.root)

    # ---- F17, as ruled: the hold follows the event
    def test_a_trade_answer_holds_only_its_event_whatever_its_due_time(self):
        raised = open_events.et(self.tuesday, 9)
        after_game = open_events.et(date.fromisoformat(self.game["date"]) + timedelta(days=2), 16)
        before_kickoff = open_events.et(date.fromisoformat(self.game["date"]) - timedelta(days=1), 12)
        before = {k: decision_queue.blocking_errors([event(k, SEASON, self.week)], self.root)
                  for k in ("week_inputs", "week_close")}
        for ident, due in (("test-call-due-tuesday", after_game), ("test-call-due-saturday", before_kickoff)):
            record = self.raise_(se.trade_call(self.root, ident, raised, due))
            item = se.item(self.root, record["queue_item"])
            self.assertEqual(item["blocks"], [event("event_resolution", SEASON, event=record["id"])])
            self.assertEqual(item["deadline"]["at"], open_events.iso(due))
            self.assertTrue(decision_queue.holds(item, event("event_resolution", SEASON, event=record["id"])))
            self.assertEqual(self.holds_any_week(item), [])
        # The week's inputs and close are held by exactly what held them before.
        for kind, lines in before.items():
            self.assertEqual(decision_queue.blocking_errors([event(kind, SEASON, self.week)], self.root), lines)
        self.assertEqual(self.queue_errors(), [])
        self.assertEqual(open_events.validation_errors(self.root), [])

    def test_a_legal_team_vacancy_holds_the_game_until_settled(self):
        raised = open_events.et(self.tuesday, 9)
        record = self.raise_(se.injury_replacement(self.root, "test-injury-short", raised, self.game))
        mine, his = se.item(self.root, record["queue_item"]), se.item(self.root, record["id"] + "-transaction")
        held = event("week_inputs", SEASON, self.week)
        for item in (mine, his):
            self.assertEqual(item["deadline"]["before"], held)
            self.assertTrue(decision_queue.holds(item, held))
            self.assertTrue(decision_queue.holds(item, event("week_close", SEASON, self.week)))
        self.assertEqual((mine["owner"], his["owner"]), ("stone", "caldwell"))
        lines = decision_queue.blocking_errors([held], self.root)
        self.assertTrue(any(record["id"] + "-transaction" in line for line in lines))
        self.assertEqual(self.queue_errors(), [])
        self.assertEqual(open_events.validation_errors(self.root), [])
        # Without the recorded shortfall an injury replacement holds only its event.
        other = self.raise_(se.injury_replacement(self.root, "test-injury-not-short", raised, self.game, short=False))
        self.assertEqual(self.holds_any_week(se.item(self.root, other["queue_item"])), [])
        self.assertFalse(any(i["id"] == other["id"] + "-transaction" for i in decision_queue.load(self.root)["items"]))

    def bye_week(self):
        weeks = {int(g["week"]) for g in open_events.club_fixtures(SEASON, self.root)}
        return next(w for w in range(1, 18) if w not in weeks)

    def bye_item(self, week, **changes):
        item = {"id": "test-bye-adjustments", "title": "Test bye adjustments", "class": "bye_adjustments",
                "owner": "stone", "authority_rows": ["9"], "question": "A test question.",
                "raised": {"date": self.tuesday.isoformat(), "by": "workflow"}, "status": "OPEN", "waits_on": [],
                "deadline": None, "blocks": [event("bye_close", SEASON, week)], "fallback": None,
                "can_continue": None, "record": {"path": "career/%d/README.md" % SEASON}, "sources": [],
                "resolution": None}
        item.update(changes)
        return item

    def test_a_bye_close_item_does_not_hold_the_bye_weeks_close(self):
        bye = self.bye_week()
        item = self.bye_item(bye)
        self.assertTrue(decision_queue.holds(item, event("bye_close", SEASON, bye)))
        self.assertFalse(decision_queue.holds(item, event("week_close", SEASON, bye)))
        self.assertFalse(decision_queue.holds(item, event("week_inputs", SEASON, bye)))
        queue = decision_queue.load(self.root)
        se.save_queue(self.root, dict(queue, items=queue["items"] + [item]))
        self.assertEqual(self.queue_errors(), [])
        self.assertEqual(decision_queue.describe(event("bye_close", SEASON, bye)), "closing the Week %d bye" % bye)

    def test_a_bye_close_block_on_a_playing_week_fails(self):
        queue = decision_queue.load(self.root)
        se.save_queue(self.root, dict(queue, items=queue["items"] + [self.bye_item(self.week)]))
        self.assertError("holds the close of Week %d of %d as a bye, but Jacksonville Jaguars plays that week"
                         % (self.week, SEASON), self.queue_errors())
        # Only the bye's adjustments item may hold the bye's close.
        se.save_queue(self.root, dict(queue, items=queue["items"] + [self.bye_item(
            self.bye_week(), **{"class": "practice_plan", "authority_rows": ["11"]})]))
        self.assertError("is a practice_plan item, which may not block bye_close", self.queue_errors())

    def test_a_week_block_on_a_trade_item_fails(self):
        record = self.raise_(se.trade_call(self.root, "test-call-blocking", open_events.et(self.tuesday, 9),
                                           self.kickoff))
        queue = decision_queue.load(self.root)
        held = event("week_inputs", SEASON, self.week)
        for entry in queue["items"]:
            if entry["id"] == record["queue_item"]:
                entry["blocks"].append(held)
                entry["deadline"]["before"] = held
        se.save_queue(self.root, queue)
        self.assertError("a trade call never holds the game", self.queue_errors())

    def test_an_overdue_trade_item_holds_nothing_but_its_event(self):
        due = open_events.et(self.tuesday, 9, 30)
        record = self.raise_(se.trade_call(self.root, "test-call-overdue", open_events.et(self.tuesday, 9), due))
        queue = decision_queue.load(self.root)
        overdue = decision_queue.overdue_items(queue, open_events.master_at(self.root))
        self.assertEqual([i["id"] for i in overdue], [record["queue_item"]])
        self.assertEqual(self.holds_any_week(overdue[0]), [])
        self.assertEqual(self.queue_errors(), [])
        self.assertEqual(open_events.validation_errors(self.root), [])
        self.assertEqual(se.item(self.root, record["queue_item"])["status"], "OPEN")

    # ---- the two-way link and the store's rules
    def test_the_event_and_its_item_point_at_each_other(self):
        record = self.raise_(se.trade_call(self.root, "test-call-linked", open_events.et(self.tuesday, 9)))
        self.assertEqual(se.item(self.root, record["queue_item"])["event"], record["id"])
        path = open_events.path_of(record, self.root)
        path.write_text(json.dumps(dict(record, queue_item="2014-w06-game-plan")), encoding="utf-8")
        self.assertError("which does not name this event back", open_events.validation_errors(self.root))
        path.write_text(json.dumps(dict(record, queue_item=None)), encoding="utf-8")
        errors = open_events.validation_errors(self.root)
        self.assertError("is named by queue item %s, which the event does not name" % record["id"], errors)
        self.assertError("needs his answer but names no queue item", errors)
        path.unlink()
        self.assertError("names event %s, which no event record holds" % record["id"],
                         open_events.validation_errors(self.root))

    def test_an_fyi_or_standing_answered_event_with_his_item_fails(self):
        record = self.raise_(se.trade_call(self.root, "test-call-standing", open_events.et(self.tuesday, 9)))
        path = open_events.path_of(record, self.root)
        for part in ("none", "standing:stone-not-open-to-job-offers"):
            path.write_text(json.dumps(dict(record, stone_part=part)), encoding="utf-8")
            self.assertError("needs no answer from Alex Stone (%s), but an OPEN item of his carries it" % part,
                             open_events.validation_errors(self.root))
        with self.assertRaisesRegex(open_events.Refused, "unknown standing instruction"):
            open_events.raise_event(se.trade_call(self.root, "test-call-unknown-rule", open_events.et(self.tuesday, 9),
                                                  stone_part="standing:no-such-rule"), self.root)

    def test_a_figure_without_a_source_fails(self):
        record = se.trade_call(self.root, "test-call-unsourced", open_events.et(self.tuesday, 9),
                               facts=[{"label": "Pick offered", "value": "A fourth-round pick in 2015", "source": None}])
        with self.assertRaisesRegex(open_events.Refused, "facts 1 carries a figure or date without a source"):
            open_events.raise_event(record, self.root)
        record["facts"][0]["value"] = "A later-round pick"
        self.raise_(record)

    def test_an_event_needs_a_source_page_and_a_fresh_id(self):
        record = se.trade_call(self.root, "test-call-no-source", open_events.et(self.tuesday, 9))
        record["raised"]["source"] = None
        with self.assertRaisesRegex(open_events.Refused, "only from a source page"):
            open_events.raise_event(record, self.root)
        record = self.raise_(se.trade_call(self.root, "test-call-once", open_events.et(self.tuesday, 9)))
        with self.assertRaisesRegex(open_events.Refused, "already recorded"):
            open_events.raise_event(se.trade_call(self.root, "test-call-once", open_events.et(self.tuesday, 9)),
                                    self.root)
        self.assertEqual(record["period"], {"week": self.week})
        self.assertEqual(record["raised"]["after_issue"], open_events.latest_issue(SEASON, {"week": self.week}, self.root))

    # ---- deciding: the criteria before the case
    def test_a_decision_without_its_preceding_criteria_fails(self):
        record = self.raise_(se.trade_call(self.root, "test-call-criteria", open_events.et(self.tuesday, 9)))
        se.settle(self.root, record["queue_item"], "RESOLVED", {
            "date": self.tuesday.isoformat(), "by": "user", "record": {"path": record["raised"]["source"]["path"]},
            "summary": "A test answer."})
        page = se.result_page(self.root, record, "Trade_Result_test_criteria.md", self.tuesday)
        decision = {"at": open_events.iso(open_events.et(self.tuesday, 10)), "outcome": "declined", "by": "caldwell",
                    "decision": {"text": "Declined the test call.", "author": "David Caldwell",
                                 "date": self.tuesday.isoformat(), "criteria": None}, "result_page": page}
        with self.assertRaisesRegex(open_events.Refused, "without a criteria entry recorded before"):
            open_events.resolve(SEASON, record["id"], decision, self.root)
        open_events.add_process(SEASON, record["id"], {
            "at": open_events.iso(open_events.et(self.tuesday, 9, 30)), "kind": "criteria", "by": "caldwell",
            "what": "The need, the legal options and the terms on the date.", "source": record["raised"]["source"]},
            self.root)
        decision["decision"]["criteria"] = 0
        open_events.resolve(SEASON, record["id"], decision, self.root)
        self.assertEqual(open_events.get(SEASON, record["id"], self.root)["state"], "resolved")
        self.assertEqual(open_events.validation_errors(self.root), [])
        self.assertEqual(self.queue_errors(), [])

    def test_executing_a_trade_is_refused(self):
        record = self.raise_(se.trade_call(self.root, "test-call-executed", open_events.et(self.tuesday, 9)))
        open_events.add_process(SEASON, record["id"], {
            "at": open_events.iso(open_events.et(self.tuesday, 9, 30)), "kind": "criteria", "by": "caldwell",
            "what": "The need and the terms.", "source": record["raised"]["source"]}, self.root)
        se.settle(self.root, record["queue_item"], "RESOLVED", {
            "date": self.tuesday.isoformat(), "by": "user", "record": {"path": record["raised"]["source"]["path"]},
            "summary": "A test answer."})
        page = se.result_page(self.root, record, "Trade_Result_test_executed.md", self.tuesday)
        with self.assertRaisesRegex(open_events.Refused, "a trade is not executed here"):
            open_events.resolve(SEASON, record["id"], {
                "at": open_events.iso(open_events.et(self.tuesday, 10)), "outcome": "executed", "by": "caldwell",
                "decision": {"text": "Agreed.", "author": "David Caldwell", "date": self.tuesday.isoformat(),
                             "criteria": 0}, "result_page": page}, self.root)

    # ---- another side's act
    def withdrawn(self, ident):
        record = self.raise_(se.trade_call(self.root, ident, open_events.et(self.tuesday, 9)))
        open_events.add_process(SEASON, record["id"], {
            "at": open_events.iso(open_events.et(self.tuesday, 10)), "kind": "withdrawn_by_other_side",
            "by": open_events.OTHER_CLUB, "what": "The other club withdrew the proposal.",
            "source": record["raised"]["source"]}, self.root)
        return open_events.get(SEASON, record["id"], self.root)

    def test_a_counterpartys_withdrawal_closes_the_event(self):
        record = self.withdrawn("test-call-withdrawn")
        rel = open_events.path_of(record, self.root).relative_to(self.root.resolve()).as_posix()
        se.settle(self.root, record["queue_item"], "WITHDRAWN", {
            "date": self.tuesday.isoformat(), "by": "organization", "record": {"path": rel, "pointer": "/process/0"},
            "summary": "%s: the other club withdrew its proposal." % open_events.OTHER_SIDE_SUMMARY})
        self.assertEqual(self.queue_errors(), [])
        page = se.result_page(self.root, record, "Trade_Result_test_withdrawn.md", self.tuesday)
        open_events.resolve(SEASON, record["id"], {
            "at": open_events.iso(open_events.et(self.tuesday, 10, 15)), "outcome": "withdrawn",
            "by": open_events.OTHER_CLUB, "decision": {"text": "The other club withdrew its proposal.",
                                                       "author": "David Caldwell", "date": self.tuesday.isoformat(),
                                                       "criteria": None}, "result_page": page}, self.root)
        self.assertEqual(open_events.validation_errors(self.root), [])

    def test_a_withdrawal_without_a_sourced_entry_fails(self):
        record = self.raise_(se.trade_call(self.root, "test-call-unsourced-withdrawal", open_events.et(self.tuesday, 9)))
        rel = open_events.path_of(record, self.root).relative_to(self.root.resolve()).as_posix()
        se.settle(self.root, record["queue_item"], "WITHDRAWN", {
            "date": self.tuesday.isoformat(), "by": "organization", "record": {"path": rel},
            "summary": "%s." % open_events.OTHER_SIDE_SUMMARY})
        self.assertError("is Alex Stone's decision and may be settled only by the user or a standing instruction, "
                         "not by organization (the other side's act is a process entry", self.queue_errors())
        # A process entry the store holds is always sourced: one without a source is refused.
        with self.assertRaisesRegex(open_events.Refused, "process 1 source"):
            open_events.add_process(SEASON, record["id"], {
                "at": open_events.iso(open_events.et(self.tuesday, 10)), "kind": "withdrawn_by_other_side",
                "by": open_events.OTHER_CLUB, "what": "Withdrawn.", "source": None}, self.root)

    def test_nothing_is_written_while_a_game_is_paused(self):
        paused = SeasonPaths(SEASON, self.root).paused_game(self.week)
        paused.parent.mkdir(parents=True, exist_ok=True)
        paused.write_text(json.dumps({"status": "paused"}), encoding="utf-8")
        self.addCleanup(paused.unlink)
        with self.assertRaisesRegex(open_events.Refused, "paused"):
            open_events.raise_event(se.trade_call(self.root, "test-call-paused", open_events.et(self.tuesday, 9)),
                                    self.root)

    # ---- rule 5: nothing that holds the game changed
    def test_the_holds_of_every_existing_item_and_week_are_unchanged(self):
        queue = decision_queue.load(ROOT)
        events = []
        for week in range(1, 22):
            events += [event("week_inputs", SEASON, week), event("week_close", SEASON, week)]
            events += [event("call_sheet_part", SEASON, week, part=p) for p in decision_queue.SHEET_PARTS]
        events += [event(k, s) for k in ("season_stage", "season_opening") for s in (SEASON, SEASON + 1)]
        for item in queue["items"]:
            for ev in events:
                self.assertEqual(decision_queue.holds(item, ev), reference_holds(item, ev), (item["id"], ev))
        # Every existing kind keeps its words.
        self.assertEqual(decision_queue.describe(event("week_inputs", 2014, 6)),
                         "the Week 6 game: nothing for it is frozen until this is settled")
        self.assertEqual(decision_queue.describe(event("season_opening", 2015)), "opening the 2015 season")
        with self.assertRaises(ValueError):
            decision_queue.describe({"kind": "no_such_kind", "season": 2014})


if __name__ == "__main__":
    unittest.main()
