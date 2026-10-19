"""The result-side week pages and the Game Report's generated block (rebuild step 4, builder B).

Fast checks on the real repository, read only: the built week pages are
current and clean; the Game Report's box score is the weekly output's gamebook
with only its sacks header changed, and it passes the clean-page check; the
box-score markers are the only markup the check lets through beside the
event-record line; the annual record refuses an unclean new line; and the
Game Report's path comes from the folder map. The synthetic Week 6 close is
tests/test_week_close_pages.py.
"""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime import clean_pages, gamebook, week_pages  # noqa: E402
from runtime.seasons import GAME_OUTPUT, GAME_REPORT, GAME_REPORT_FROM, SeasonPaths  # noqa: E402
from scripts import render_annual_record, render_box_score, render_week_pages  # noqa: E402

JAX = "Jacksonville Jaguars"
SEASON, FIRST = GAME_REPORT_FROM


def last_jacksonville_receipt():
    paths = SeasonPaths(SEASON, ROOT)
    ours = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(paths.receipts.glob("*.json"))
            if "jacksonville_jaguars" in p.name]
    return max(ours, key=lambda r: int(r["week"])) if ours else None


class GameReportTests(unittest.TestCase):
    def test_report_path_through_the_folder_map(self):
        paths = SeasonPaths(SEASON, ROOT)
        self.assertEqual(paths.game_report(FIRST).name, GAME_REPORT)
        self.assertEqual(paths.game_report(FIRST - 1).name, GAME_OUTPUT)
        self.assertEqual(paths.game_report(FIRST + 1).parent, paths.week_folder(FIRST + 1))
        self.assertEqual(paths.game_report(1, postseason=True).name, GAME_REPORT)
        self.assertEqual(SeasonPaths(SEASON - 1, ROOT).game_report(FIRST + 1).name, GAME_OUTPUT)
        self.assertEqual(SeasonPaths(SEASON + 1, ROOT).game_report(1).name, GAME_REPORT)

    def test_report_block_is_the_gamebook_with_the_clean_sacks_header(self):
        receipt = last_jacksonville_receipt()
        if receipt is None:
            self.skipTest("no closed Jacksonville game")
        weekly = render_box_score.render(receipt, JAX, SEASON)
        report = render_box_score.render(receipt, JAX, SEASON, report=True)
        self.assertEqual(weekly, gamebook.render(receipt, JAX))  # the weekly output is unchanged
        self.assertEqual(report, weekly.replace(gamebook.SACK_YARDS, gamebook.REPORT_SACK_YARDS))
        self.assertIn(gamebook.REPORT_SACK_YARDS, report)
        rel = SeasonPaths(SEASON, ROOT).game_report(FIRST).relative_to(ROOT).as_posix()
        page = "\n".join(["# Game Report", "",
                          "<!-- box-score event=%s team=%s -->" % (receipt["event_id"], JAX), report,
                          "<!-- /box-score -->", ""])
        self.assertEqual(clean_pages.page_errors(rel, page), [])
        self.assertTrue(render_box_score.is_report(rel))
        self.assertEqual(render_box_score.fill(page, SeasonPaths(SEASON, ROOT).receipts, SEASON, report=True), page)

    def test_box_score_markers_alone_on_their_line(self):
        rel = "career/x/Game_Report.md"
        self.assertEqual(clean_pages.page_errors(rel, "<!-- box-score event=2014-week06-a-at-b team=Tennessee Titans -->\n"
                                                      "<!-- /box-score -->\n"), [])
        self.assertTrue(clean_pages.page_errors(rel, "Text <!-- /box-score -->\n"))
        self.assertTrue(clean_pages.page_errors(rel, "<!-- box-score event=x team=Y --> and more\n"))
        self.assertTrue(clean_pages.page_errors(rel, "<!-- note -->\n"))


class WeekPagesTests(unittest.TestCase):
    def test_built_pages_are_current_and_clean(self):
        self.assertEqual(render_week_pages.check(ROOT, SEASON), [])
        season = week_pages.Season(ROOT, SEASON)
        for rel, text in week_pages.built(season).items():
            self.assertEqual(clean_pages.page_errors(rel, text), [], rel)

    def test_games_index_reads_the_closed_games(self):
        season = week_pages.Season(ROOT, SEASON)
        _, text = week_pages.games_index(season)
        ours = [g for g in season.fixtures if JAX in (g["away"], g["home"])]
        closed = [g for g in ours if season.receipt(g)]
        self.assertIn("**%s" % season.record(), text)
        self.assertEqual(len(re.findall(r"\| (?:\[)?(?:Won|Lost|Tied) \d+-\d+", text)), len(closed))
        upcoming = season.next_game()
        if upcoming:
            self.assertIn("| Next |", text)

    def test_league_results_pages_from_the_first_report_week_only(self):
        season = week_pages.Season(ROOT, SEASON)
        self.assertTrue(all(w >= FIRST for w in week_pages.built_weeks(season)))
        built = week_pages.built(season)
        for week in range(1, FIRST):
            self.assertNotIn(season.rel(week_pages.week_page_path(season, week)), built)

    def test_week_page_keeps_hand_written_highlights(self):
        season = week_pages.Season(ROOT, SEASON)
        weeks = season.closed_weeks()
        if not weeks:
            self.skipTest("no closed week")
        week = weeks[-1]
        _, blank = week_pages.week_page(season, week)
        heading = next(line for line in blank.splitlines() if line.startswith("## ") and week_pages.REACTIVE not in line)
        filled = blank.replace(heading + "\n\n" + week_pages.TO_COME, heading + "\n\nA written highlight.", 1)
        _, again = week_pages.week_page(season, week, filled)
        self.assertEqual(again, filled)

    def test_injury_report_lists_every_instruction_on_the_record(self):
        season = week_pages.Season(ROOT, SEASON)
        _, text = week_pages.injury_report(season)
        for player in season.roster["players"]:
            note = player.get("availability") or week_pages.NO_RESTRICTION
            listed = "| %s |" % player["name"] in text
            held = player["list"] == "reserve" or not note.startswith(week_pages.NO_RESTRICTION)
            self.assertEqual(listed, held and player["list"] != "practice_squad", player["name"])

    def test_rebased_links_reach_the_same_file(self):
        out = week_pages.rebase("([record](../../Medical/incidents/x.md#a))",
                                "career/2014/Team_Operations/Team/Roster/roster.md",
                                "career/2014/Team_Operations/Medical/current_injury_report.md")
        self.assertEqual(out, "([record](incidents/x.md#a))")


class AnnualRecordTests(unittest.TestCase):
    def test_record_refuses_an_unclean_new_line(self):
        path = render_annual_record.annual_record_path(ROOT, SEASON)
        text = path.read_text(encoding="utf-8")
        self.assertEqual(render_annual_record.problems(ROOT, SEASON, text), [])
        bad = text + "- A day: closed under kernel 2014.6 [Full record](../../data/x.json).\n"
        found = render_annual_record.problems(ROOT, SEASON, bad)
        self.assertTrue(any("system word" in p for p in found), found)
        self.assertTrue(any("link to a system file" in p for p in found), found)
        good = text + "- A day: Jacksonville 20, Tennessee 17. [Full record](Team_Operations/Medical/medical_history.md).\n"
        self.assertEqual(render_annual_record.problems(ROOT, SEASON, good), [])


if __name__ == "__main__":
    unittest.main()
