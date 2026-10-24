"""The trade offer log split into one page per call, and its built index (rebuild step 5, part B2).

The log written before 2014 Week 6 (``targets_and_offers/trade_offers.md``) is history: it was
split into its eight calls under the split rule (tests/test_clean_pages.py audits the bytes), and
the page at its path is now the index scripts/render_trade_pages.py builds. Every event here is
test data in one throwaway copy of the checkout (support_events); the real repository is never
written. Weeks and dates come from the fixtures and the receipts, never from today's date.
"""
from datetime import timedelta
import os
from pathlib import Path
import re
import sys
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
from release_staging import copied_root  # noqa: E402
import support_events as se  # noqa: E402
from runtime import clean_pages, decision_queue, decisions, deadlines, open_events  # noqa: E402
from runtime.events import EVENT_META  # noqa: E402
from scripts import render_trade_pages as trades  # noqa: E402

LOG_SEASON = 2014          # the season whose offer log, written before Week 6, was split
INDEX = trades.index_path(ROOT, LOG_SEASON)
INDEX_REL = INDEX.relative_to(ROOT).as_posix()
# The eight calls, named as the completed records are: players, club, date of the first call.
CALLS = {"nwaneri_to_arizona_2014-03-11.md", "nwaneri_to_san_francisco_2014-03-11.md",
         "babin_to_miami_2014-03-11.md", "alualu_to_houston_2014-03-24.md", "allen_to_arizona_2014-03-24.md",
         "rackley_to_seattle_2014-05-11.md", "shorts_blackmon_to_indianapolis_2014-03-31.md",
         "colts_picks_to_washington_2014-03-31.md"}
LINK = re.compile(r"\]\(([^()\s]+)\)")


def links(text):
    return LINK.findall(text)


class CallPageTests(unittest.TestCase):
    def setUp(self):
        self.entry = clean_pages.splits(ROOT)[INDEX_REL]

    def test_the_log_is_eight_call_pages(self):
        parts = {Path(p["path"]).name: p for p in self.entry["parts"]}
        self.assertEqual(set(parts), CALLS)
        for name, part in parts.items():
            with self.subTest(call=name):
                path = ROOT / part["path"]
                self.assertEqual(path.parent, INDEX.parent)  # its relative links still resolve
                self.assertTrue(part["title"].startswith("# Trade call: "))
                # No call written before Week 6 gains an event line.
                self.assertIsNone(EVENT_META.search(path.read_text(encoding="utf-8")))
                for dest in links(path.read_text(encoding="utf-8")):
                    self.assertTrue((path.parent / dest.split("#")[0]).exists(), dest)

    def test_the_opening_stays_at_the_log_and_adding_an_entry_moves_to_the_workflow(self):
        moved = {m["to"]: m for m in self.entry["moved"]}
        self.assertEqual(set(moved), {INDEX_REL, "docs/update_workflow.md"})
        self.assertTrue(moved[INDEX_REL]["text"].startswith("# Jacksonville 2014 trade offer log\n\n"))
        self.assertTrue(moved["docs/update_workflow.md"]["text"].startswith("## Adding an entry\n"))
        self.assertEqual(moved["docs/update_workflow.md"]["range"][1], self.entry["length"])

    def test_a_shared_introduction_goes_with_each_call_it_introduces(self):
        rebuilt = clean_pages.rebuilt_original(INDEX_REL, ROOT)
        intro = rebuilt.index(b"## March 24, 2014:")
        holding = {Path(p["path"]).name for p in self.entry["parts"] if any(s <= intro < e for s, e in p["ranges"])}
        self.assertEqual(holding, {"babin_to_miami_2014-03-11.md", "alualu_to_houston_2014-03-24.md",
                                   "allen_to_arizona_2014-03-24.md", "rackley_to_seattle_2014-05-11.md"})


class TradeIndexTests(unittest.TestCase):
    def test_the_index_is_built_clean_and_current(self):
        pages = trades.render_index(ROOT, LOG_SEASON)
        self.assertEqual(list(pages), [INDEX])
        text = pages[INDEX]
        self.assertEqual(text, INDEX.read_text(encoding="utf-8"))
        self.assertEqual(trades.check(ROOT, LOG_SEASON), [])
        self.assertEqual(clean_pages.page_errors(INDEX_REL, text, root=ROOT), [])
        self.assertEqual(clean_pages.text_errors(INDEX_REL, text, ROOT), [])
        opening = next(m["text"] for m in clean_pages.splits(ROOT)[INDEX_REL]["moved"] if m["to"] == INDEX_REL)
        self.assertTrue(text.startswith(opening))
        for dest in links(text):
            self.assertTrue((INDEX.parent / dest.split("#")[0]).is_file(), dest)

    def test_the_index_lists_the_eight_calls_with_their_records(self):
        text = INDEX.read_text(encoding="utf-8")
        rows = [line for line in text.split("## Open trade calls")[0].splitlines() if line.startswith("| ")
                and "](" in line]
        self.assertEqual(len(rows), 8)
        self.assertEqual({links(row)[0] for row in rows}, CALLS)
        completed = [row for row in rows if "[Completed " in row]
        self.assertEqual(len(completed), 7)
        for row in completed:  # each completed call links the completed record of the same players and club
            call, record = links(row)
            self.assertTrue(record.startswith("../completed_trades/"), row)
            self.assertEqual(re.sub(r"_\d{4}-\d{2}-\d{2}\.md$", "", Path(record).name),
                             re.sub(r"_\d{4}-\d{2}-\d{2}\.md$", "", call))
        (withdrawn,) = [row for row in rows if "[Completed " not in row]
        self.assertIn("nwaneri_to_san_francisco_2014-03-11.md", withdrawn)
        self.assertIn("No trade; the call page is its record", withdrawn)
        # In the order of the first call, as the log gave them on a shared date.
        firsts = [re.search(r"_(\d{4}-\d{2}-\d{2})\.md", row)[1] for row in rows]
        self.assertEqual(firsts, sorted(firsts))
        self.assertIn("No trade call is open.", text)

    def test_the_folder_navigation_keeps_its_bytes(self):
        (path, text), = trades.render(ROOT, LOG_SEASON).items()
        self.assertEqual(text, path.read_text(encoding="utf-8"))
        rel = path.relative_to(ROOT).as_posix()
        self.assertEqual(clean_pages.digest(path.read_bytes()), clean_pages.history(ROOT)[rel])
        self.assertEqual(set(trades.pages(ROOT, LOG_SEASON)), {path, INDEX})


class TradeEventIndexTests(unittest.TestCase):
    """Trade calls recorded as events from Week 6, in a copy at a mid-week clock."""

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
        cls.index = trades.index_path(cls.root, se.SEASON)

    def setUp(self):
        for rel in (str(decision_queue.QUEUE), se.STATE):
            path = self.root / rel
            before = path.read_bytes()
            self.addCleanup(path.write_bytes, before)
        for folder in open_events.stores(se.SEASON, self.root):
            self.addCleanup(self._clear, folder)
        folder = decisions.event_folder("trade_talks", se.SEASON, self.root)
        before = set(folder.glob("*.md"))
        self.addCleanup(lambda: [p.unlink() for p in folder.glob("*.md") if p not in before])
        se.midweek(self.root, self.tuesday, 10, 30, self.week)

    @staticmethod
    def _clear(folder):
        for path in folder.glob("*.json") if folder.is_dir() else ():
            path.unlink()

    def index_text(self):
        text = trades.render_index(self.root, se.SEASON)[self.index]
        rel = self.index.relative_to(self.root.resolve()).as_posix()
        self.assertEqual(clean_pages.page_errors(rel, text, root=self.root), [])
        for dest in links(text):
            self.assertTrue((self.index.parent / dest.split("#")[0]).is_file(), dest)
        return text

    def test_an_open_call_and_then_its_trade_result_appear(self):
        raised = open_events.et(self.tuesday, 9)
        due = open_events.et(self.tuesday + timedelta(days=1), 16)
        open_events.raise_event(se.trade_call(self.root, "test-index-call", raised, due), self.root)
        record = open_events.get(se.SEASON, "%s-test-index-call" % self.tuesday.isoformat(), self.root)
        source = os.path.relpath(self.root / record["raised"]["source"]["path"], self.index.parent)
        text = self.index_text()
        opened = text.split("## Open trade calls")[1]
        self.assertIn("| %s | [Trade call from Test Club](%s) | Open | %s |" % (
            open_events.at_text(raised), source, open_events.at_text(due)), opened)
        self.assertNotIn("No trade call is open.", text)
        # Caldwell's criteria, Stone's answer, the decision and its result page: the call moves to
        # the list of calls with its Trade Result, as the result writer leaves it.
        open_events.add_process(se.SEASON, record["id"], {
            "at": open_events.iso(open_events.et(self.tuesday, 9, 30)), "kind": "criteria", "by": "caldwell",
            "what": "The need, the legal options and the terms on the date.", "source": record["raised"]["source"]},
            self.root)
        se.settle(self.root, record["queue_item"], "RESOLVED", {
            "date": self.tuesday.isoformat(), "by": "user", "record": {"path": record["raised"]["source"]["path"]},
            "summary": "A test answer."})
        name = decisions.result_file("trade_talks", self.tuesday.isoformat(), "Test Club", self.root).name
        page = se.result_page(self.root, record, name, self.tuesday)
        open_events.resolve(se.SEASON, record["id"], {
            "at": open_events.iso(open_events.et(self.tuesday, 10)), "outcome": "declined", "by": "caldwell",
            "decision": {"text": "Declined the test call.", "author": "David Caldwell",
                         "date": self.tuesday.isoformat(), "criteria": 0}, "result_page": page}, self.root)
        self.assertEqual(open_events.validation_errors(self.root), [])
        text = self.index_text()
        calls, opened = text.split("## Open trade calls")
        result = os.path.relpath(self.root / page, self.index.parent)
        self.assertIn("| %s | [Trade call from Test Club](%s) | [Declined %s](%s) |" % (
            se.long_date(self.tuesday), source, se.long_date(self.tuesday), result), calls)
        self.assertIn("No trade call is open.", opened)
        self.assertEqual(len([line for line in calls.splitlines() if line.startswith("| ") and "](" in line]), 9)
        # The page on disk is now stale until rebuilt, and the check says so.
        self.assertEqual(trades.check(self.root, se.SEASON),
                         ["Trade index stale: %s" % self.index.relative_to(self.root.resolve())])

    def test_a_call_raised_after_the_clock_cannot_reach_the_index(self):
        late = open_events.et(self.tuesday, 11)
        with self.assertRaises(open_events.Refused):
            open_events.raise_event(se.trade_call(self.root, "test-index-late", late), self.root)
        self.assertIn("No trade call is open.", self.index_text())

    def test_the_trade_deadline_shows_only_while_the_briefs_show_it(self):
        at = open_events.et(self.tuesday + timedelta(days=21), 16)
        window = {"key": "%d-%s" % (se.SEASON, trades.DEADLINE_KEY), "title": "Trade deadline",
                  "at": open_events.iso(at), "why": "A test window.", "state": "No proposal is on record",
                  "action": "No answer is required", "source": {"path": INDEX_REL}}
        other = dict(window, key="test-eligibility-window", title="A player's return window")
        with mock.patch.object(deadlines, "coming_up", return_value=[other, window]):
            text = self.index_text()
        self.assertIn("## Trade deadline\n\n| Deadline | When | Where it stands |\n|---|---|---|\n"
                      "| Trade deadline | %s | No proposal is on record |\n" % open_events.at_text(at), text)
        self.assertNotIn("return window", text)
        with mock.patch.object(deadlines, "coming_up", return_value=[other]):
            self.assertNotIn("Trade deadline", self.index_text())


if __name__ == "__main__":
    unittest.main()
