"""The decision queue: what an item holds, the fail-closed gate and validation.

Mutations run on one throwaway copy of the checkout per class; each test
restores the files it changed. Weeks come from the fixtures and receipts
(the first unplayed Jacksonville week, the first bye), and dates from the
master date, so the tests hold at any later clock.
"""
from datetime import timedelta
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from release_staging import copied_root
from runtime import current_job, decision_queue
from runtime.decision_queue import event
from runtime.events import load_events, repository_map
from runtime.player_bios import master_date
from runtime.seasons import SeasonPaths

SEASON = 2014
CLUB = "Jacksonville Jaguars"
W5_SHEET = "career/2014/05_Regular_Season/Games/Week_05/call_sheet.json"


def club_weeks():
    return sorted({g["week"] for g in SeasonPaths(SEASON, ROOT).regular_games() if CLUB in (g["away"], g["home"])})


def first_unplayed_week():
    """The first week with a Jacksonville fixture and no receipt."""
    receipts = SeasonPaths(SEASON, ROOT).receipts
    return next(w for w in club_weeks() if not any(receipts.glob("week_%02d_*.json" % w)))


class DecisionQueueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping = repository_map(ROOT)
        cls.events = load_events(ROOT, cls.mapping)
        cls.master = master_date(ROOT)
        cls.root = copied_root(SimpleNamespace(addCleanup=cls.addClassCleanup))
        cls.week = first_unplayed_week()

    def setUp(self):
        self.job = current_job.load(self.root)
        self.queue = decision_queue.load(self.root)

    def write(self, relative, text):
        path = self.root / relative
        before = path.read_bytes() if path.exists() else None
        self.addCleanup(lambda: path.write_bytes(before) if before is not None else path.unlink(missing_ok=True))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def plan_item(self, **changes):
        """A valid OPEN weekly plan item for the first unplayed week."""
        item = {"id": "test-plan", "title": "Test plan", "class": "weekly_game_plan", "owner": "stone",
                "authority_rows": ["9"], "question": "A test question.",
                "raised": {"date": self.master.isoformat(), "by": "workflow"}, "status": "OPEN",
                "waits_on": [], "deadline": None,
                "blocks": [event("week_inputs", SEASON, self.week)], "fallback": None, "can_continue": None,
                "record": {"path": "career/2014/README.md"}, "sources": [], "resolution": None}
        item.update(changes)
        return item

    def errors_with(self, *items, job=None, keep=True):
        queue = json.loads(json.dumps(self.queue))
        queue["items"] = (queue["items"] if keep else []) + list(items)
        self.write(str(decision_queue.QUEUE), json.dumps(queue, indent=1))
        return decision_queue.validation_errors(self.root, self.mapping, self.events, self.master, job or self.job)

    def assertError(self, text, errors):
        self.assertTrue(any(text in e for e in errors), "%r not in %r" % (text, errors))

    def test_repository_queue_is_valid(self):
        job = current_job.load(ROOT)
        self.assertEqual(decision_queue.validation_errors(ROOT, self.mapping, self.events, self.master, job), [])

    def test_holds(self):
        week = {"status": "OPEN", "blocks": [event("week_inputs", 2014, 6)]}
        self.assertTrue(decision_queue.holds(week, event("week_inputs", 2014, 6)))
        self.assertTrue(decision_queue.holds(week, event("week_close", 2014, 6)))
        self.assertFalse(decision_queue.holds(week, event("week_inputs", 2014, 7)))
        self.assertFalse(decision_queue.holds(week, event("week_close", 2015, 6)))
        part = {"status": "OPEN", "blocks": [event("call_sheet_part", 2014, 6, part="decisions.fourth_down")]}
        self.assertTrue(decision_queue.holds(part, event("call_sheet_part", 2014, 6, part="decisions.fourth_down")))
        self.assertFalse(decision_queue.holds(part, event("call_sheet_part", 2014, 6, part="decisions.two_point")))
        self.assertFalse(decision_queue.holds(part, event("week_inputs", 2014, 6)))
        self.assertFalse(decision_queue.holds(part, event("week_close", 2014, 6)))
        stage = {"status": "OPEN", "blocks": [event("season_stage", 2015)]}
        self.assertTrue(decision_queue.holds(stage, event("season_opening", 2015)))
        self.assertFalse(decision_queue.holds(stage, event("season_opening", 2016)))
        for status in ("RESOLVED", "WITHDRAWN"):
            self.assertFalse(decision_queue.holds(dict(week, status=status), event("week_inputs", 2014, 6)))
        with self.assertRaises(ValueError):
            event("call_sheet_part", 2014, 6)

    def test_load_and_gate_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                decision_queue.load(root)
            lines = decision_queue.blocking_errors([event("week_inputs", 2014, 6)], root)
            self.assertEqual(len(lines), 1)
            self.assertTrue(lines[0].startswith("Decision queue unreadable (state/decision_queue.json: "))
            with self.assertRaisesRegex(ValueError, "Decision queue unreadable"):
                decision_queue.refuse_if_blocked([event("season_stage", 2015)], root)
            (root / "state").mkdir()
            for text in ("{not json", '{"schema_version": 2, "items": []}', '{"schema_version": 1, "items": {}}'):
                (root / "state/decision_queue.json").write_text(text)
                with self.assertRaises(ValueError):
                    decision_queue.load(root)
            (root / "state/decision_queue.json").write_text(
                '{"schema_version": 1, "enforced_from": {"season": 2014, "week": 6}, "items": []}')
            self.assertEqual(decision_queue.blocking_errors([event("week_inputs", 2014, 6)], root), [])

    def test_refusal_names_the_owner_and_the_held_event(self):
        item = self.plan_item()
        self.write(str(decision_queue.QUEUE), json.dumps(dict(self.queue, items=[item])))
        lines = decision_queue.blocking_errors([event("week_close", SEASON, self.week)], self.root)
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].startswith("Decision open: test-plan, Test plan. It holds the Week %d game. "
                                            "Owner: Alex Stone (the user): present it to the user" % self.week))
        self.assertEqual(decision_queue.blocking_errors([event("week_close", SEASON, self.week + 1)], self.root), [])
        self.assertEqual(decision_queue.describe(event("week_close", 2014, 18)), "the Wild Card game")
        self.assertEqual(decision_queue.describe(event("week_inputs", 2014, 21)),
                         "the Super Bowl game: nothing for it is frozen until this is settled")
        self.assertEqual(decision_queue.describe(event("call_sheet_part", 2014, 6, part="decisions.fourth_down")),
                         "freezing a fourth-down rule in the Week 6 call sheet")

    def test_sheet_parts(self):
        sheet = json.loads((ROOT / W5_SHEET).read_text(encoding="utf-8"))
        self.assertCountEqual(decision_queue.sheet_parts(sheet), ["offensive_call_sheet", "decisions.two_point",
                                                                  "decisions.kickoff", "defensive_call_sheet"])

    def test_class_may_not_block_that_kind(self):
        item = self.plan_item(**{"class": "personnel_transaction", "owner": "caldwell"})
        self.assertError("test-plan is a personnel_transaction item, which may not block week_inputs",
                         self.errors_with(item))

    def test_owner_differs_from_class_default(self):
        self.assertError("test-plan is owned by caldwell, not the class default stone",
                         self.errors_with(self.plan_item(owner="caldwell")))
        self.assertFalse(any("class default" in e for e in self.errors_with(
            self.plan_item(owner="caldwell", owner_note="A test note"))))

    def resolved(self, **resolution):
        base = {"date": self.master.isoformat(), "by": "user", "record": {"path": "career/2014/README.md"},
                "summary": "A test summary."}
        base.update(resolution)
        return self.plan_item(status="RESOLVED", resolution=base)

    def test_holder_item_settled_by_staff(self):
        self.assertError("test-plan is Alex Stone's decision and may be settled only by the user or a "
                         "standing instruction, not by staff", self.errors_with(self.resolved(by="staff")))

    def test_resolved_without_record(self):
        item = self.resolved()
        del item["resolution"]["record"]
        self.assertError("test-plan is RESOLVED without a resolution date, by, record and summary",
                         self.errors_with(item))

    def test_resolution_after_master_date(self):
        later = (self.master + timedelta(days=1)).isoformat()
        self.assertError("resolution.date %s is not an ISO date on or before the master date" % later,
                         self.errors_with(self.resolved(date=later)))

    def test_open_item_on_closed_week(self):
        item = self.plan_item(blocks=[event("week_inputs", 2014, 5)])
        self.assertError("test-plan is open, but Week 5 of 2014 has closed", self.errors_with(item))

    def test_open_item_during_a_pause(self):
        paused = SeasonPaths(SEASON, self.root).paused_game(self.week).relative_to(self.root).as_posix()
        self.write(paused, json.dumps({"status": "paused"}))
        self.assertError("test-plan holds Week %d of 2014 while that game is paused" % self.week,
                         self.errors_with(self.plan_item()))

    def test_calling_items_are_raised_only_by_the_user(self):
        item = self.plan_item(**{"class": "play_calling_delegation", "blocks": [], "deadline": None})
        self.assertError("test-plan is a play_calling_delegation item, which only the user raises",
                         self.errors_with(item))

    def test_standing_instruction_covers_an_open_item(self):
        job = json.loads(json.dumps(self.job))
        current_job.appointment(job)["standing_instructions"].append(
            {"id": "test-inactive-rule", "subject": "inactives", "status": "IN_FORCE",
             "closes": ["game_day_inactives"], "record": {"path": "career/2014/README.md"}})
        item = self.plan_item(**{"class": "game_day_inactives", "authority_rows": ["8"]})
        self.assertError("test-plan is covered by the standing instruction test-inactive-rule; settle it as "
                         "covered (resolution.by standing_instruction) or record why the instruction does not "
                         "apply", self.errors_with(item, job=job))
        item["standing_not_applied"] = [{"instruction": "test-inactive-rule", "reason": "A test reason."},
                                        {"instruction": "stone-healthy-inactive-rule", "reason": "A test reason."}]
        self.assertFalse(any("test-plan is covered" in e for e in self.errors_with(item, job=job)))

    def test_holder_needs_a_part_in_the_class(self):
        item = self.plan_item(**{"class": "medical_status", "owner": "stone", "owner_note": "A test note",
                                 "blocks": [], "deadline": None})
        self.assertError("test-plan puts medical_status to Alex Stone, but his appointment gives him no decision "
                         "or recommendation on rows 15, 16, 17", self.errors_with(item))

    def test_call_sheet_without_a_resolved_plan(self):
        sheet = json.loads((ROOT / W5_SHEET).read_text(encoding="utf-8"))
        folder = SeasonPaths(SEASON, self.root).week_folder(self.week)
        self.write((folder / "call_sheet.json").relative_to(self.root).as_posix(), json.dumps(sheet))
        others = [i for i in self.queue["items"] if not (
            i["class"] == "weekly_game_plan" and i["status"] == "RESOLVED"
            and event("week_inputs", SEASON, self.week) in i["blocks"])]
        errors = self.errors_with(*others, keep=False)
        self.assertError("call sheet for Week %d exists without Stone's resolved weekly plan item" % self.week, errors)
        self.assertFalse(any("call sheet for Week" in e for e in self.errors_with(*others, self.resolved(), keep=False)))

    def test_block_on_a_bye_week(self):
        bye = next(w for w in range(1, 18) if w not in club_weeks())
        item = self.plan_item(blocks=[event("week_inputs", SEASON, bye)])
        self.assertError("test-plan holds Week %d of 2014, in which Jacksonville Jaguars does not play" % bye,
                         self.errors_with(item))

    def test_open_season_opening_for_the_active_season(self):
        active = int(self.mapping["active_season"])
        item = self.plan_item(**{"class": "staff_appointment", "blocks": [event("season_opening", active)]})
        self.assertError("test-plan holds opening the %d season, which is already active" % active,
                         self.errors_with(item))

    def test_further_open_item_for_the_next_week_is_valid(self):
        self.assertEqual(self.errors_with(self.plan_item()), [])
        self.assertEqual(current_job.validation_errors(self.root, self.mapping, self.events, self.master), [])


if __name__ == "__main__":
    unittest.main()
