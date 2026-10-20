"""A playoff game through the three game-week pages, end to end in a temporary copy
(game week version 2, Phase C; docs/game_week_v2.md, section 7).

The copy's regular season is cut short so that its closed games set a playoff field: the released
fixtures keep only the first weeks, the closed games after them are removed, and a postseason
slots file is written beside the real 2013 one, in its layout, with fixture dates the week after the
copy's clock (the 2014 file is not yet researched; nothing here is a real 2014 date or result).
With three weeks Jacksonville is the AFC's first seed: it has a Wild Card bye, and no Divisional
page is issued while the Wild Card games are unplayed. With two weeks it is the third seed and
hosts Pittsburgh in the Wild Card round. Then, the way the weekly workflow runs a game week:

- briefing: render_game_week.py opens the week's two decision items and issues the Game Week
  Briefing (with the playoff game's own facts), the blank Game Plan and the index in the round's
  folder under the postseason folder, through the folder map;
- check and apply: a complete version 2 Game Plan (Baseline: Carry Week 5, the standing two-point
  and kickoff rules, fourth downs left to the live call, the inactives named) checks and,
  once the exams the items wait on are held, applies: the call sheet is frozen in the postseason
  folder's data twin, where the weekly build looks for it, and the items are settled;
- close and report: the copy's Week 5 game record becomes the Wild Card game (Pittsburgh at
  Jacksonville, the same clubs), the playoff acceptance fixture is written as its Game Report, the
  rebuild's box-score step names its markers and fills the game book last, and every Game Report
  check passes;
- after the loss: no later game is opened and no page is issued.

No game is played, the private service is never contacted and the real repository is never touched.
"""
import contextlib
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import clean_pages, game_plan, game_report, game_weeks  # noqa: E402
from runtime.decisions import week_pages  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402
from runtime.week_inputs import receipt_name  # noqa: E402

JAX, PIT = "Jacksonville Jaguars", "Pittsburgh Steelers"
SEASON, WILD_CARD, DIVISIONAL = 2014, 18, 19
IGNORED = (".git", ".sim_cache", "__pycache__", ".pytest_cache")
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "game_reports" / "playoff_game.md"
# The receipt fields tied to the week a game was played under (tests/test_week_close_pages.py).
WEEK_BOUND = ("defensive_calls", "defensive_call_stats", "decision_policies")
# Fixture slot dates (the copy's clock is October 5, 2014): the rounds on the weekends after it.
SLOT_DATES = {"2014-01-04": "2014-10-11", "2014-01-05": "2014-10-12", "2014-01-11": "2014-10-18",
              "2014-01-12": "2014-10-19", "2014-01-19": "2014-10-26", "2014-02-02": "2014-11-09"}


def quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


class PostseasonGameWeekTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT.parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(*IGNORED), symlinks=True)
        self.paths = SeasonPaths(SEASON, self.root)
        self.week5 = json.loads((self.paths.receipts / "week_05_pittsburgh_steelers_at_jacksonville_jaguars.json")
                                .read_text(encoding="utf-8"))
        self.real = sorted(p.name for p in SeasonPaths(SEASON, ROOT).receipts.glob("*.json"))

    # ---------------------------------------------------------------- the copy's season
    def write_slots(self):
        slots = json.loads((ROOT / "library/data/2013_postseason_slots.json").read_text(encoding="utf-8"))
        text = json.dumps(dict(slots, season=SEASON, note="Test fixture slots: not real 2014 dates."))
        for old, new in SLOT_DATES.items():
            text = text.replace(old, new)
        self.paths.postseason_slots.write_text(text, encoding="utf-8")

    def end_season_after(self, last):
        """The copy's regular season as its first ``last`` weeks: the later fixtures and closed games go
        (their pages stay, as other pages link to them)."""
        path = self.paths.schedule
        data = json.loads(path.read_text(encoding="utf-8"))
        keep = [g for g in data["games"] if g["week"] <= last]
        ids = {g["game_id"] for g in keep}
        data.update(games=keep, amendments=[a for a in data.get("amendments") or () if a.get("game_id") in ids])
        path.write_text(json.dumps(data, indent=1), encoding="utf-8")
        for receipt in self.paths.receipts.glob("week_*.json"):
            if int(receipt.name[5:7]) > last:
                receipt.unlink()

    def inactives(self, plan):
        """A legal list from the stored facts: every player out for the game, then the deepest reserve
        of the largest groups (tests/test_game_plan.needed_inactives, for a playoff game's date)."""
        outs, problems = plan.outs()
        self.assertEqual(problems, [])
        active = plan.active()
        out = [p for p in active if p in outs]
        groups = sorted(plan.chart["depth"].items(), key=lambda kv: -len(kv[1]))
        depth = 1
        while len(out) < plan.needed():
            for _, players in groups:
                if len(out) < plan.needed() and len(players) > depth + 2:
                    name = players[-depth]
                    if name in active and name not in out:
                        out.append(name)
            depth += 1
        return out

    def exams_held(self):
        """The exams the week's items wait on, held: each dated wait moved to the day before today (the
        clock stays), and the briefing re-issued for the changed situation (tests/test_game_plan.py)."""
        from runtime.player_bios import master_date
        from scripts import render_game_week
        path = self.root / "state/decision_queue.json"
        queue = json.loads(path.read_text(encoding="utf-8"))
        before = (master_date(self.root) - timedelta(days=1)).isoformat()
        for item in queue["items"]:
            if any(b.get("week") == WILD_CARD for b in item.get("blocks") or ()):
                for wait in item.get("waits_on") or ():
                    if wait.get("date"):
                        wait["date"] = before
        path.write_text(json.dumps(queue, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        quiet(render_game_week.write, self.root)

    def close_wild_card(self, game):
        """The copy's Week 5 game record, as the Wild Card game: the same clubs, sides and play."""
        receipt = {k: v for k, v in self.week5.items() if k not in WEEK_BOUND}
        receipt.update(week=WILD_CARD, game_type="postseason", event_id=game["game_id"])
        folder = self.paths.postseason_receipts
        folder.mkdir(parents=True, exist_ok=True)
        (folder / receipt_name(game)).write_text(json.dumps(receipt, indent=1), encoding="utf-8")
        state = self.root / "state/05_Current_Season_State.md"
        text, n = re.subn(r"(\| Master date/time \| )[A-Za-z]+ \d{1,2}, \d{4}[^|]*\|",
                          r"\g<1>October 12, 2014, after the Wild Card game against Pittsburgh |",
                          state.read_text(encoding="utf-8"), count=1)
        self.assertEqual(n, 1)
        state.write_text(text, encoding="utf-8")
        return receipt

    # ---------------------------------------------------------------- the test
    def test_a_playoff_game_runs_through_the_three_pages(self):
        from scripts import apply_game_plan, check_game_plan, open_game_week, render_box_score
        from scripts import render_coach_record, render_game_week
        root, paths = self.root, self.paths
        post_folder = paths.postseason

        # Mid-season, no playoff game exists: no opponent is named before the bracket sets it.
        with self.assertRaises(game_weeks.NotSet):
            game_weeks.club_game(paths, WILD_CARD, JAX)
        with self.assertRaises(ValueError):
            render_game_week.Week(root, WILD_CARD)
        self.write_slots()

        # A first-round bye: no Wild Card pages, and the Divisional game waits for the Wild Card results.
        self.end_season_after(3)
        self.assertEqual(game_weeks.seed_of(game_weeks.regular_receipts(paths), JAX), ("AFC", 1))
        wk = render_game_week.Week(root)
        self.assertIsNone(wk.game)
        self.assertIn("Divisional", wk.waiting)
        self.assertEqual(quiet(render_game_week.write, root), [])
        self.assertFalse(any(post_folder.glob("Week_*")))
        problems, _, _ = check_game_plan.check(root, SEASON, DIVISIONAL)
        self.assertTrue(problems[0].startswith("Divisional: Jacksonville's game is not set yet"), problems)

        # The third seed hosts the sixth: Pittsburgh at Jacksonville in the Wild Card round.
        self.end_season_after(2)
        wk = render_game_week.Week(root)
        game = wk.game
        self.assertEqual((game["week"], game["away"], game["home"], game["round_name"]), (WILD_CARD, PIT, JAX, "Wild Card"))
        self.assertEqual((game["home_seed"], game["away_seed"], game["stadium"]), (3, 6, "EverBank Field"))
        self.assertTrue(wk.postseason and not wk.closed)

        # Briefing: the round's folder under the postseason folder, through the folder map.
        written = quiet(render_game_week.write, root)
        pages = week_pages(SEASON, WILD_CARD, root)
        self.assertEqual(pages.folder, paths.week_folder(WILD_CARD, postseason=True))
        self.assertTrue(pages.folder.is_relative_to(post_folder) and pages.data.is_relative_to(paths.data))
        for page in (pages.briefing, pages.plan, pages.readme):
            self.assertIn(page, written)
        self.assertFalse(paths.week_folder(WILD_CARD).exists())
        briefing = pages.briefing.read_text(encoding="utf-8")
        self.assertTrue(briefing.startswith("# Wild Card Game Week Briefing: Pittsburgh\n"))
        # The playoff game's own facts are section 1's rows, in place of the regular season's standings.
        section = briefing.split("## 1. The game and what is at stake", 1)[1].split("\n## 2.", 1)[0]
        for text in ("| Game type | Wild Card, AFC |", "| Seeds | Jacksonville No. 3, Pittsburgh No. 6 |",
                     "| Venue and kickoff | EverBank Field, ", "Jacksonville: ", "since its Week 2 game, at home",
                     "| If we lose | The season is over. |", "| If we win | We play in the Divisional round",
                     "| Earlier meeting |", "A playoff game cannot end tied", "first possession",
                     "| Game-day roster | 46 dress"):
            self.assertIn(text, section)
        self.assertNotIn("| Stakes |", section)
        self.assertEqual(clean_pages.page_errors(pages.briefing.relative_to(root).as_posix(), briefing, root=root), [])
        self.assertTrue(pages.plan.read_text(encoding="utf-8").startswith("# Wild Card Game Plan: Pittsburgh\n"))
        self.assertTrue(pages.readme.read_text(encoding="utf-8").startswith("# Wild Card: Pittsburgh\n"))
        queue = json.loads((root / "state/decision_queue.json").read_text(encoding="utf-8"))
        items = [i for i in queue["items"] if any(b.get("week") == WILD_CARD for b in i["blocks"])]
        self.assertEqual(sorted(i["title"] for i in items), ["Wild Card game plan for Pittsburgh", "Wild Card inactives"])
        self.assertEqual(open_game_week.missing(root)[0], [])
        self.assertEqual(render_game_week.check(root), [])

        # Check and apply: the page's choices into the call sheet in the postseason folder's data twin.
        plan = check_game_plan.Plan(root, SEASON, WILD_CARD)
        players = self.inactives(plan)
        answers = {
            "baseline": "Carry Week 5", "attack": "Their linebackers in space against our tight ends.",
            "protect": "A cutback behind an overrun.", "change_course": "A safety rotating late to the second tight end.",
            "inactives": ", ".join(players), "depth": "No change", "contingency": "None",
            "coverage_units": "No change", "offense_caller": "No change", "base_personnel": "Twelve personnel leads.",
            "learn": "Who travels with the second tight end.", "opening_approach": "As in Week 5.",
            "opening": "Carry Week 5 opening", "third_down": "No change", "backed_up": "No change",
            "red_zone": "No change", "two_minute": "No change", "four_minute": "No change",
            "sudden_change": "No change", "special_plays": "No change", "not_available": "None",
            "defense_caller": "No change", "front": "Force and cutback first.", "coverage": "Quarters and 6.",
            "rush": game_plan.RUSH_CHOICE, "discover": "Their protection against the replaced rusher.",
            "matchups": "No change", "kicking_caller": "No change", "kicking": "No change",
            "fourth_down": "None", "two_point": "Standing rule", "kickoff": "Standing rule",
            "endgame": "No change", "participation": "None", "tradeoff": "None", "staff": "None",
            "public": "No new statement", "open_decisions": "None", "ready": "None",
            "practice": [["Third down", "Tice with the offense", "Third and medium", "The Saturday walkthrough"]]}
        facts = render_game_week.plan_facts(render_game_week.Week(root, WILD_CARD))
        pages.plan.write_text(game_plan.render("Wild Card Game Plan: Pittsburgh", facts, answers), encoding="utf-8")
        problems, _, _ = check_game_plan.check(root, SEASON, WILD_CARD)
        self.assertEqual(problems, [])
        self.exams_held()
        problems, written = quiet(apply_game_plan.apply, root, SEASON, WILD_CARD, rebuild_pages=False)
        self.assertEqual(problems, [])
        sheet_path = paths.call_sheet(WILD_CARD, postseason=True)
        self.assertIn(sheet_path, written)
        # The weekly build finds exactly this sheet (scripts/build_week_inputs.py looks in both folders).
        self.assertEqual([p for p in (paths.call_sheet(WILD_CARD), sheet_path) if p.exists()], [sheet_path])
        sheet = json.loads(sheet_path.read_text(encoding="utf-8"))
        week5 = json.loads(paths.call_sheet(5).read_text(encoding="utf-8"))
        self.assertEqual(sheet["event"], "2014 postseason Wild Card, Pittsburgh at Jacksonville, October 12, 2014")
        # Week 5's calls carried as set; its "what I am looking at" text is author intent, not the sheet's.
        strip = lambda calls: [{k: v for k, v in c.items() if k != "what_stone_is_looking_at"} for c in calls]
        self.assertEqual(sheet["offensive_call_sheet"], strip(week5["offensive_call_sheet"]))
        self.assertEqual(sheet["defensive_call_sheet"]["rows"], week5["defensive_call_sheet"]["rows"])
        self.assertNotIn("fourth_down", sheet["decisions"])
        chart = json.loads(paths.depth_chart.read_text(encoding="utf-8"))
        self.assertEqual(chart["game_day_inactives"]["week"], WILD_CARD)
        self.assertEqual(chart["game_day_inactives"]["players"], players)
        queue = json.loads((root / "state/decision_queue.json").read_text(encoding="utf-8"))
        settled = [i for i in queue["items"] if any(b.get("week") == WILD_CARD for b in i["blocks"])]
        self.assertTrue(settled and all(i["status"] == "RESOLVED" and i["resolution"]["by"] == "user" for i in settled))
        self.assertEqual(apply_game_plan.validation_errors(root), [])
        quiet(render_game_week.write_index, root, WILD_CARD)
        self.assertIn("Set for the game", pages.readme.read_text(encoding="utf-8"))
        self.assertEqual(render_game_week.check(root, WILD_CARD), [])

        # Close and report: the Game Report in the round's folder, its box score named and filled last.
        receipt = self.close_wild_card(game)
        self.assertEqual(check_game_plan.check(root, SEASON, WILD_CARD)[0], ["Wild Card has been played; its plan stays "
                                                                             "as it was set"])
        report = FIXTURE.read_text(encoding="utf-8")
        coach_record = render_coach_record.render(SEASON, PIT, root)
        self.assertIn("## Coach record\n\n%s\n" % coach_record, report)     # the table the coach record prints
        self.assertEqual(pages.report, paths.game_report(WILD_CARD, postseason=True))
        pages.report.write_text(report, encoding="utf-8")
        # The rebuild's box-score step for this page (scripts/rebuild_pages.box_scores; the copy's cut
        # weeks keep result pages whose games it no longer holds, so the step is run on this page).
        named = render_box_score.named(pages.report, SEASON, root)
        pages.report.write_text(render_box_score.fill(named, paths.receipts, SEASON, report=True), encoding="utf-8")
        text = pages.report.read_text(encoding="utf-8")
        self.assertNotIn(game_report.EVENT_PLACEHOLDER, text)
        self.assertEqual(game_report.report_errors(text, receipt, game, root=root), [])
        self.assertEqual(game_report.validation_errors(root), [])
        self.assertEqual(render_box_score.stale_blocks(pages.report, paths.receipts, season=SEASON), [])
        self.assertEqual(clean_pages.page_errors(pages.report.relative_to(root).as_posix(), text, root=root), [])
        block = game_report.BLOCK.search(text)
        self.assertEqual(block.group("event"), game["game_id"])
        self.assertEqual(text[block.end():].strip(), "")
        for target in re.findall(r"\]\(([^)#]+)", text.split("\n## Full game statistics", 1)[0]):
            self.assertTrue((pages.folder / target).resolve().is_file(), target)
        quiet(render_game_week.write_index, root, WILD_CARD)
        self.assertIn("| Written |", pages.readme.read_text(encoding="utf-8"))
        self.assertEqual(render_game_week.check(root, WILD_CARD), [])

        # After the loss: no later game, no page and no item.
        wk = render_game_week.Week(root)
        self.assertIsNone(wk.game)
        self.assertIn("beaten in the Wild Card round", wk.waiting)
        self.assertEqual(quiet(render_game_week.write, root), [])
        self.assertEqual(open_game_week.missing(root)[0], [])
        self.assertEqual(sorted(p.name for p in post_folder.glob("Week_*")), ["Week_18"])
        self.assertEqual(render_game_week.validation_errors(root), [])

        # Isolation: nothing reached the real season.
        self.assertFalse(SeasonPaths(SEASON, ROOT).postseason_slots.exists())
        self.assertEqual(sorted(p.name for p in SeasonPaths(SEASON, ROOT).receipts.glob("*.json")), self.real)


if __name__ == "__main__":
    unittest.main()
