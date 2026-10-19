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
        from runtime.seasons import GAME_REPORT_FROM, SeasonPaths
        year, first = GAME_REPORT_FROM
        pages = decisions.week_pages(year, first, ROOT)
        self.assertEqual((pages.briefing.name, pages.plan.name, pages.report.name),
                         ("Game_Week_Briefing.md", "Game_Plan.md", "Game_Report.md"))
        # The result page is the folder map's (SeasonPaths.game_report): before the first Game Report
        # week it is the week's output as written.
        for week in (first - 1, first, first + 1):
            self.assertEqual(decisions.week_pages(year, week, ROOT).report, SeasonPaths(year, ROOT).game_report(week))


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
        self.assertIsNotNone(render_game_week.issued_on(self.wk))
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
        earlier = [path for path, _ in render_game_week.earlier_briefings(render_game_week.Week(self.root))]
        self.assertEqual(len(earlier), 1)
        self.assertEqual(earlier[0].read_text(encoding="utf-8"), old)
        self.assertIn(earlier[0], written)
        shown = changed["name"] + " |" in self.wk.pages.briefing.read_text(encoding="utf-8")
        self.assertEqual(shown, not under)
        self.assertIn(earlier[0].name, self.wk.pages.readme.read_text(encoding="utf-8"))
        # Both issues are in the week's issue record, the earlier one under its kept name.
        record = render_game_week.issues(render_game_week.Week(self.root))
        self.assertEqual([e["file"] for e in record], [earlier[0].name, self.wk.pages.briefing.name])
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


class IssueRecordTests(unittest.TestCase):
    """F3: each issued briefing is held to its recorded issue; a hand edit fails validation and is
    never kept as what he saw; the issue date is the record's, never read from the page."""

    def setUp(self):
        self.root = copy_repo(self)
        wk = render_game_week.Week(self.root)
        if wk.game is None:
            self.skipTest("no Jacksonville game is open")
        with contextlib.redirect_stdout(io.StringIO()):
            render_game_week.write(self.root)
        self.wk = render_game_week.Week(self.root)

    def test_a_hand_edited_briefing_fails_and_is_never_kept(self):
        page = self.wk.pages.briefing
        issued = page.read_text(encoding="utf-8")
        self.assertEqual(render_game_week.validation_errors(self.root), [])
        record = render_game_week.issues(self.wk)
        self.assertEqual(record[-1]["sha256"], render_game_week.sha256(page))
        mine = self.wk.record("Jacksonville Jaguars")
        edited = issued.replace("| Jacksonville | %s |" % mine, "| Jacksonville | 9-0 |", 1)
        self.assertNotEqual(edited, issued)
        page.write_text(edited, encoding="utf-8")
        self.assertTrue(any("differs from the briefing issued" in e for e in render_game_week.validation_errors(self.root)))
        with self.assertRaises(ValueError):
            render_game_week.write(self.root)
        self.assertEqual(render_game_week.earlier_briefings(render_game_week.Week(self.root)), [])
        self.assertFalse(list(self.wk.pages.folder.glob(page.stem + "_*.md")))
        page.write_text(issued, encoding="utf-8")
        self.assertEqual(render_game_week.validation_errors(self.root), [])

    def test_a_briefing_no_issue_produced_fails(self):
        stray = self.wk.pages.earlier_briefing("October 1")
        stray.write_text(self.wk.pages.briefing.read_text(encoding="utf-8"), encoding="utf-8")
        self.assertTrue(any("not a briefing the issue record holds" in e
                            for e in render_game_week.validation_errors(self.root)))
        stray.unlink()
        render_game_week.issues_path(self.wk).unlink()
        self.assertTrue(any("has no issue record" in e for e in render_game_week.validation_errors(self.root)))

    def test_the_issue_date_is_the_records(self):
        page = self.wk.pages.briefing
        when = render_game_week.issued_on(self.wk)
        self.assertEqual(when.isoformat(), render_game_week.issues(self.wk)[-1]["date"])
        self.assertIn("From the coaching staff, %s:" % render_game_week.day(when), page.read_text(encoding="utf-8"))
        self.assertIn("Issued %s" % render_game_week.day(when), self.wk.pages.readme.read_text(encoding="utf-8"))


def receipt(event, week, away, home, scores, stats, records=False):
    """A minimal closed-game record for the statistics owner (runtime/statbook.aggregate_receipts)."""
    from runtime.statbook import STATBOOK_SCHEMA_VERSION
    out = {"event_id": event, "schema_version": STATBOOK_SCHEMA_VERSION, "week": week, "coverage": "complete",
           "away": away, "home": home, "final_score": scores,
           "team_stats": {club: dict(stats[club], points=scores[club]) for club in (away, home)}}
    if records:
        out["penalties"] = {}      # the game carries the penalty records (each foul charged to its club)
    return out


def player(position, **fields):
    return dict(fields, position=position)


class BriefingFactsTests(unittest.TestCase):
    """The briefing's figures are the statistics owner's (R2, F5), a tie is a tie (R4), the medical
    table names the roster status and reads exams across the new year (R11, F10, W6-9), and the
    plan's practice work is due before the week's first practice (R7)."""

    def test_penalties_under_two_methods_are_never_added(self):
        games = [receipt("e1", 4, "B", "A", {"A": 10, "B": 7},
                         {"A": {"penalties": 8, "penalty_yards": 58, "players": {}},
                          "B": {"penalties": 2, "penalty_yards": 18, "players": {}}}),
                 receipt("e2", 5, "A", "C", {"A": 20, "C": 23},
                         {"A": {"penalties": 10, "penalty_yards": 63, "players": {}},
                          "C": {"penalties": 7, "penalty_yards": 69, "players": {}}}, records=True)]
        rows, note = render_game_week.team_rows(games, "A")
        penalties = {r[0]: r[1:] for r in rows if r[0].startswith("Penalties")}
        self.assertEqual(penalties, {"Penalties, through Week 4": ["8 for 58 yards", "2 for 18 yards"],
                                     "Penalties, from Week 5": ["10 for 63 yards", "7 for 69 yards"]})
        self.assertIn("never added", note)
        self.assertNotIn("18 for 121 yards", str(rows))
        # One method alone is one row, and the other figures are the statistics owner's totals.
        rows, note = render_game_week.team_rows(games[1:], "A")
        self.assertIsNone(note)
        self.assertIn(["Penalties", "10 for 63 yards", "7 for 69 yards"], rows)
        self.assertIn(["Points", "30", "30"], render_game_week.team_rows(games, "A")[0])

    def test_players_tied_for_a_lead_each_have_a_row(self):
        games = [receipt("e1", 1, "B", "A", {"A": 10, "B": 7},
                         {"A": {"players": {"Mincey": player("DE", sacks=2, tackles=5),
                                            "Stanford": player("LB", sacks=2, tackles=7),
                                            "Posluszny": player("LB", sacks=1, tackles=7)}},
                          "B": {"players": {}}})]
        rows = render_game_week.leaders(games, "A")
        self.assertEqual([r[:2] for r in rows if r[0].startswith("Sacks")],
                         [["Sacks, tied", "Mincey"], ["Sacks, tied", "Stanford"]])
        self.assertEqual([r[:2] for r in rows if r[0].startswith("Tackles")],
                         [["Tackles, tied", "Posluszny"], ["Tackles, tied", "Stanford"]])
        from runtime import season_summary as summary
        team = {"players": {"X": {"tackles": 40}, "Y": {"tackles": 40}, "Z": {"tackles": 12}}}
        self.assertEqual([(c, n) for c, n, _ in summary.leaders(team)], [("Tackling, tied", "X"), ("Tackling, tied", "Y")])

    def stand_in(self, root, master):
        """A week read for the medical table: the copy's roster record as of ``master``."""
        from types import SimpleNamespace
        from runtime.seasons import SeasonPaths
        paths = SeasonPaths(2014, root)
        return SimpleNamespace(paths=paths, master=master, rel=lambda p: Path(p).relative_to(root).as_posix())

    def edited_roster(self, root, changes):
        from runtime.seasons import SeasonPaths
        path = SeasonPaths(2014, root).roster
        data = json.loads(path.read_text(encoding="utf-8"))
        for row in data["players"]:
            if row["name"] in changes:
                row.update(changes[row["name"]])
        path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        return data

    def test_the_medical_table_names_the_reserve_list_and_the_year_of_each_exam(self):
        from datetime import date
        root = copy_repo(self)
        data = json.loads(render_game_week.Week(root).paths.roster.read_text(encoding="utf-8"))
        active = next(p for p in data["players"] if p["list"] == "active")
        season = next(p for p in data["players"] if p["list"] == "reserve")
        self.edited_roster(root, {
            active["name"]: {"availability": "Out, minor: trunk, logged in the Week 16 game; projected return "
                                             "January 5, 2015; reassessment January 2 ([medical record](x.md))"},
            season["name"]: {"status": "Reserve/Injured (placed August 31, 2014)",
                             "availability": "Out, long term: lower extremity; projected return October 9, 2014"}})
        rows = {r[0]: r for r in render_game_week.availability_rows(self.stand_in(root, date(2014, 12, 28)), "x.md")}
        # A reassessment written without its year is the nearer one: across the new year it keeps 2015.
        self.assertEqual(rows[active["name"]][3:7], ["Out", "trunk (minor)", "January 5, 2015", "January 2, 2015"])
        # A player on reserve/injured, not designated for return, is out for the season.
        self.assertEqual(rows[season["name"]][2], "Reserve/injured")
        self.assertEqual(rows[season["name"]][5], "Out for the season")
        rows = {r[0]: r for r in render_game_week.availability_rows(self.stand_in(root, date(2015, 1, 3)), "x.md")}
        self.assertEqual(rows[active["name"]][6], "None communicated")  # January 2, 2015 has passed
        self.edited_roster(root, {season["name"]: {"status": "Reserve/Injured, designated for return (placed "
                                                             "September 8, 2014)"}})
        rows = {r[0]: r for r in render_game_week.availability_rows(self.stand_in(root, date(2014, 10, 5)), "x.md")}
        self.assertEqual(rows[season["name"]][2], "Reserve/injured, designated for return")
        self.assertEqual(rows[season["name"]][5], "October 9, 2014")

    def test_an_entry_in_another_layout_is_read_whole_or_refused(self):
        from datetime import date
        root = copy_repo(self)
        data = json.loads(render_game_week.Week(root).paths.roster.read_text(encoding="utf-8"))
        name = next(p for p in data["players"] if p["list"] == "active")["name"]
        self.edited_roster(root, {name: {"availability": "Out, short: lower extremity; projected return October 30, "
                                                         "2014; reassessment October 18 ([medical record](x.md))"}})
        row = next(r for r in render_game_week.availability_rows(self.stand_in(root, date(2014, 10, 12)), "x.md")
                   if r[0] == name)
        self.assertEqual(row[4:7], ["lower extremity (short)", "October 30, 2014", "October 18"])
        self.edited_roster(root, {name: {"availability": "Sore after practice"}})
        with self.assertRaises(ValueError):
            render_game_week.availability_rows(self.stand_in(root, date(2014, 10, 12)), "x.md")

    def test_the_practice_work_is_due_before_the_first_practice(self):
        from datetime import date
        from runtime import season_summary as summary
        events = [("October 6", "Pittsburgh review"), ("October 7 to 11", "Week 6 practice week; an exam October 7")]
        self.assertEqual(summary.first_practice(events, 6, date(2014, 10, 5)), date(2014, 10, 7))
        self.assertIsNone(summary.first_practice(events, 6, date(2014, 10, 8)))
        self.assertIsNone(summary.first_practice(events, 7, date(2014, 10, 5)))
        root = copy_repo(self)
        wk = render_game_week.Week(root)
        if wk.game is None:
            self.skipTest("no Jacksonville game is open")
        text = "\n".join(render_game_week.asks_section(wk, wk.rel(wk.pages.briefing)))
        practice = render_game_week.first_practice(wk)
        plan_rows = [line for line in text.splitlines() if line.startswith("| ") and "game plan" in line.lower()]
        for line in plan_rows:
            self.assertEqual("Practice work before the first practice" in line, practice is not None)


if __name__ == "__main__":
    unittest.main()
