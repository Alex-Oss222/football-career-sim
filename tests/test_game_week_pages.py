"""The decision registry (runtime/decisions.py) and the game week's pages
(scripts/render_game_week.py): the Game Week Briefing, the blank Game Plan and
the week index. The week is worked out from the stored facts (the next
Jacksonville game not yet closed), never from a date.
"""
import contextlib
import io
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime import decisions  # noqa: E402
from runtime.clean_pages import page_errors  # noqa: E402
from scripts import render_game_week  # noqa: E402

IGNORED = (".git", ".sim_cache", "__pycache__", ".pytest_cache")
SECTIONS = ("## The game", "## Medical update", "## How we played", "## Pro scouting report", "## What we need from you",
            "## Your standing instructions", "## Who else decides", "## Staff read")


def copy_repo(test):
    tmp = tempfile.TemporaryDirectory(dir=ROOT.parent)
    test.addCleanup(tmp.cleanup)
    root = Path(tmp.name) / "repo"
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(*IGNORED), symlinks=True)
    return root


class RegistryTests(unittest.TestCase):
    def test_every_decision_of_the_plan_is_named(self):
        text = (ROOT / "docs/rebuild_plan.md").read_text(encoding="utf-8")
        table = text.split("## The decisions in a year", 1)[1].split("\n## ", 1)[0]
        rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in table.splitlines()
                if line.startswith("| ") and not line.startswith("| When")]
        named = [(d.brief, d.page, d.result) for d in decisions.REGISTRY]
        for row in rows:
            brief = re.sub(r"\s*\(.*\)$", "", row[1])
            self.assertIn((brief, row[2], row[3]), named)
        self.assertEqual(len(rows), len(decisions.REGISTRY))
        self.assertEqual([d.kind for d in decisions.REGISTRY if d.implemented], ["game_week"])

    def test_every_folder_resolves_through_the_map(self):
        for d in decisions.REGISTRY:
            folder = decisions.folder(d, 2014, ROOT, week=1)
            self.assertTrue(folder.is_relative_to(ROOT), d.kind)
            if d.place != "week":
                self.assertTrue(folder.is_dir(), (d.kind, folder))

    def test_page_names(self):
        pages = decisions.week_pages(2014, 1, ROOT)
        self.assertEqual((pages.briefing.name, pages.plan.name, pages.report.name),
                         ("Game_Week_Briefing.md", "Game_Plan.md", "Game_Report.md"))


class BriefingTests(unittest.TestCase):
    def setUp(self):
        self.root = copy_repo(self)
        self.wk = render_game_week.Week(self.root)
        if self.wk.game is None:
            self.skipTest("no Jacksonville game is open")
        with contextlib.redirect_stdout(io.StringIO()):
            render_game_week.write(self.root)
        self.wk = render_game_week.Week(self.root)

    def test_the_briefing_is_clean_and_in_order(self):
        text = self.wk.pages.briefing.read_text(encoding="utf-8")
        self.assertEqual(page_errors(self.wk.rel(self.wk.pages.briefing), text, root=self.root), [])
        places = [text.index(s) for s in SECTIONS]
        self.assertEqual(places, sorted(places))
        self.assertIn(self.wk.opponent, text)
        self.assertIsNotNone(render_game_week.issued_on(text))
        self.assertEqual(render_game_week.validation_errors(self.root), [])
        self.assertEqual(render_game_week.check(self.root), [])

    def test_a_missing_staff_read_is_to_come(self):
        # Whatever the week's stored state, a briefing without a read says it is to come.
        self.wk.pages.staff_read.unlink(missing_ok=True)
        with contextlib.redirect_stdout(io.StringIO()):
            render_game_week.write(self.root)
        self.assertIn("## Staff read\n\nStaff read to come.\n", self.wk.pages.briefing.read_text(encoding="utf-8"))

    def test_a_stored_read_is_shown_and_may_cite_only_the_page(self):
        record = self.wk.record("Jacksonville Jaguars")
        read = {"author": "Mike Tice", "date": self.wk.master.isoformat(), "text": "We are %s." % record}
        self.wk.pages.staff_read.parent.mkdir(parents=True, exist_ok=True)
        self.wk.pages.staff_read.write_text(json.dumps(read), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            render_game_week.write(self.root)
        text = self.wk.pages.briefing.read_text(encoding="utf-8")
        self.assertIn("**Mike Tice, ", text)
        self.assertIn(read["text"], text)
        self.assertEqual(render_game_week.validation_errors(self.root), [])
        read["text"] = "We are 9,876 yards better."
        self.wk.pages.staff_read.write_text(json.dumps(read), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            render_game_week.write(self.root)
        self.assertTrue(any("9,876 is not a figure the briefing shows" in e
                            for e in render_game_week.validation_errors(self.root)))

    def test_a_changed_situation_issues_a_new_briefing_and_keeps_the_old(self):
        old = self.wk.pages.briefing.read_text(encoding="utf-8")
        path = self.wk.paths.roster
        data = json.loads(path.read_text(encoding="utf-8"))
        # Clear a player under a medical instruction, or put one under it when none is.
        under = [p for p in data["players"] if p["list"] == "active"
                 and not p["availability"].startswith("No communicated")]
        changed = under[0] if under else next(p for p in data["players"] if p["list"] == "active")
        changed["availability"] = ("No communicated restriction" if under else
                                   "Out, short: lower extremity; projected return December 31, %d" % self.wk.season)
        path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        self.assertTrue(any("a new briefing is due" in e for e in render_game_week.check(self.root)))
        state = (self.root / "state/05_Current_Season_State.md").read_bytes()
        queue = (self.root / "state/decision_queue.json").read_bytes()
        with contextlib.redirect_stdout(io.StringIO()):
            written = render_game_week.write(self.root)
        earlier = render_game_week.earlier_briefings(render_game_week.Week(self.root))
        self.assertEqual(len(earlier), 1)
        self.assertEqual(earlier[0].read_text(encoding="utf-8"), old)
        self.assertIn(earlier[0], written)
        shown = changed["name"] + " |" in self.wk.pages.briefing.read_text(encoding="utf-8")
        self.assertEqual(shown, not under)
        self.assertIn(earlier[0].name, self.wk.pages.readme.read_text(encoding="utf-8"))
        # Issuing a page moves no time and settles nothing.
        self.assertEqual((self.root / "state/05_Current_Season_State.md").read_bytes(), state)
        self.assertEqual((self.root / "state/decision_queue.json").read_bytes(), queue)
        self.assertEqual(render_game_week.validation_errors(self.root), [])

    def test_the_game_plan_is_never_rewritten(self):
        self.wk.pages.plan.write_text(self.wk.pages.plan.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        mine = self.wk.pages.plan.read_bytes()
        with contextlib.redirect_stdout(io.StringIO()):
            render_game_week.write(self.root)
        self.assertEqual(self.wk.pages.plan.read_bytes(), mine)

    def test_the_desk_links_the_briefing_and_the_plan(self):
        from scripts import render_career_views
        render_career_views.write(self.root)
        desk = self.wk.paths.desk.read_text(encoding="utf-8")
        waiting = desk.split("## Waiting on you", 1)[1].split("\n## ", 1)[0]
        week = self.wk.game["week"]
        if "Week %d" % week in waiting:
            self.assertIn("[Game Week Briefing](%s)" % self.wk.rel(self.wk.pages.briefing).split("/", 2)[2], waiting)
            self.assertIn("[Game Plan](%s)" % self.wk.rel(self.wk.pages.plan).split("/", 2)[2], waiting)


if __name__ == "__main__":
    unittest.main()
