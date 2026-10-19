"""The result-side week pages and the Game Report's generated block (rebuild step 4, builder B).

Fast checks on the real repository, read only: the built week pages are
current and clean; the Game Report's box score is the weekly output's gamebook
with only its sacks header changed, and it passes the clean-page check; the
box-score markers are the only markup the check lets through beside the
event-record line; the annual record refuses an unclean new line; and the
Game Report's path comes from the folder map. The synthetic Week 6 close is
tests/test_week_close_pages.py. Also here: the Game Report template's own
headings render clean, every injury severity reads in football words, the
shared summary words (runtime/season_summary.py), and every built page is
current by the one rebuild command (scripts/rebuild_pages.py --check).
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

    def test_week_page_renders_the_stored_highlights_and_never_drops_one(self):
        # F6: the highlights and reactive events are stored text in the page's twin in the data
        # area, never parsed back from the page; an entry that names no other game of the week stops
        # the build instead of being dropped.
        import shutil
        import tempfile
        season = week_pages.Season(ROOT, SEASON)
        weeks = season.closed_weeks()
        if not weeks:
            self.skipTest("no closed week")
        week = weeks[-1]
        tmp = tempfile.TemporaryDirectory(dir=ROOT.parent)
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        for part in ("career", "data", "docs", "state", "library/data", "runtime/season_readiness.json"):
            source, target = ROOT / part, root / part
            target.parent.mkdir(parents=True, exist_ok=True)
            (shutil.copytree if source.is_dir() else shutil.copy2)(source, target)
        season = week_pages.Season(root, SEASON)
        _, blank = week_pages.week_page(season, week)
        self.assertNotIn("A written highlight.", blank)
        other = next(g for g in week_pages.ordered_games(season, week) if JAX not in (g["away"], g["home"]))
        ours = season.jacksonville(week)
        event = season.receipt(other)["event_id"]
        path = week_pages.highlights_path(season, week)
        self.assertTrue(path.relative_to(root).as_posix().startswith("data/"))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"games": {event: "A written highlight."}, "reactive_events": "A dust-up."}),
                        encoding="utf-8")
        _, page = week_pages.week_page(season, week)
        heading = "## " + week_pages.score_line(season.receipt(other))
        self.assertIn(heading, page)
        self.assertIn("A written highlight.", page.split(heading, 1)[1].split("\n## ", 1)[0])
        self.assertIn("## %s\n\nA dust-up.\n" % week_pages.REACTIVE, page)
        for bad in ({"games": {event + "x": "Lost."}}, {"games": {event: 3}}, {"games": {}, "notes": "x"},
                    {"games": {season.receipt(ours)["event_id"]: "Ours."}} if ours else {"games": {"x": "y"}}):
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaises(ValueError, msg=bad):
                week_pages.week_page(season, week)

    def test_injury_report_lists_every_instruction_on_the_record(self):
        season = week_pages.Season(ROOT, SEASON)
        _, text = week_pages.injury_report(season)
        for player in season.roster["players"]:
            note = player.get("availability") or week_pages.NO_RESTRICTION
            listed = "| %s |" % player["name"] in text or "| [%s](" % player["name"] in text
            held = player["list"] == "reserve" or not note.startswith(week_pages.NO_RESTRICTION)
            self.assertEqual(listed, held and player["list"] != "practice_squad", player["name"])

    def test_every_injury_severity_reads_in_football_words(self):
        """A multi-week or long-term injury (the game records them as multi_week and long_term)
        writes the medical history entry and the incident record clean, never stopping the week."""
        season = week_pages.Season(ROOT, SEASON)
        game = next(g for g in season.fixtures if g["week"] == FIRST and JAX in (g["away"], g["home"]))
        other = game["home"] if game["away"] == JAX else game["away"]
        players = [p["name"] for p in season.roster["players"] if p["list"] == "active"][:4]
        injuries = [{"team": JAX, "player": name, "injury_class": cls, "severity": severity, "restriction": "out",
                     "return_days": days, "reassessment_days": 2, "removed": True, "period": 2, "clock": "4:10"}
                    for name, cls, severity, days in zip(players, ("lower_extremity", "upper_extremity", "trunk",
                                                                   "head_neck"),
                                                         ("multi_week", "long_term", "short", "minor"), (24, 70, 9, 2))]
        receipt = {"week": FIRST, "away": game["away"], "home": game["home"], "injuries": injuries,
                   "final_score": {JAX: 20, other: 17}, "drives": []}
        entry = week_pages.history_entry(season, receipt)
        history = season.rel(week_pages.medical_path(season, "medical_history.md"))
        self.assertEqual(clean_pages.text_errors(history, "# History\n\n" + entry), [])
        self.assertIn("lower extremity, multi-week", entry)
        self.assertIn("upper extremity, long term", entry)
        for injury in injuries:
            rel, text = week_pages.incident_page(season, receipt, injury)
            self.assertEqual(clean_pages.page_errors(rel, text), [], rel)
            self.assertNotIn("_", text.split("## Current medical information")[1].split("## Dated updates")[0])
        self.assertEqual(week_pages.severity_words({"severity": "multi_week"}), "multi-week")
        self.assertEqual(week_pages.severity_words({"severity": "long_term"}), "long term")
        self.assertEqual(week_pages.severity_words({"severity": "season_ending"}), "season ending")

    def test_rebased_links_reach_the_same_file(self):
        out = week_pages.rebase("([record](../../Medical/incidents/x.md#a))",
                                "career/2014/Team_Operations/Team/Roster/roster.md",
                                "career/2014/Team_Operations/Medical/current_injury_report.md")
        self.assertEqual(out, "([record](incidents/x.md#a))")


TEMPLATE = ROOT / "foundation/templates/regular_season_output_template.md"
# Template guidance headings, never written on a Game Report.
GUIDANCE = ("Rules for every turn", "Prose standard", "Runner mechanics", "Header", "Preparation evidence",
            "Game evidence", "Section layout")


def template_skeleton(week=FIRST):
    """A Game Report holding the Game Report template's own headings and fixed labels, in its order,
    placeholders filled with their own words (tests/test_week_close_pages.py writes its report so)."""
    text = TEMPLATE.read_text(encoding="utf-8")
    lines = []
    for line in text.split("\n## Coach info\n", 1)[1].splitlines():
        heading = re.match(r"^(#{2,4}) (.+)$", line)
        label = re.match(r"^\*\*([^*\\]+)\*\*", line)
        if heading and heading.group(2) not in GUIDANCE:
            lines += [heading.group(1) + " " + heading.group(2), ""]
        elif label and not heading:
            lines += ["**%s**" % label.group(1), ""]
    page = "\n".join(["# Week %d Game Report" % week, "", "## Coach info", ""] + lines)
    return re.sub(r"(?:&#91;|\\\[)([^\]\\]*)\\?\]", r"\1", page)


class GameReportTemplateTests(unittest.TestCase):
    def test_the_template_headings_render_clean(self):
        rel = SeasonPaths(SEASON, ROOT).game_report(FIRST).relative_to(ROOT).as_posix()
        page = template_skeleton()
        for heading in ("## Coach info", "## 3. Game", "### Game review", "## 6. Weekly personnel and availability",
                        "## 7. Week closure"):
            self.assertIn(heading + "\n", page)
        self.assertEqual(clean_pages.page_errors(rel, page), [])
        # The check is live on this page: the heading the earlier reports carry would fail it.
        self.assertTrue(clean_pages.page_errors(rel, page.replace(
            "## 6. Weekly personnel and availability\n", "## 6. Weekly personnel and availability snapshot\n")))


class SharedSummaryTests(unittest.TestCase):
    """runtime/season_summary.py: the words the desk, the statistics index, the injury report and the
    depth chart share."""

    def test_next_medical_dates_leave_out_a_passed_date(self):
        from datetime import date
        from runtime import season_summary as summary
        row = {"availability": "Out, long term: lower extremity, removed; projected return December 8, 2014; "
                               "reassessment September 14 ([medical record](x.md))"}
        self.assertEqual(summary.medical_status(row), "Out · lower extremity (long term)")
        self.assertEqual(summary.next_dates(row, date(2014, 10, 5)), "Projected return December 8, 2014")
        self.assertEqual(summary.next_dates(row, date(2014, 9, 10)),
                         "Review September 14, 2014; projected return December 8, 2014")
        self.assertEqual(summary.next_dates(row, date(2014, 12, 9)), "None communicated")
        self.assertEqual(summary.next_dates({"availability": "Out, minor: trunk; reassessment January 2"},
                                            date(2014, 12, 29)), "Review January 2, 2015")
        held = {"availability": "Independent medical hold, short: head/neck, logged at 5:19"}
        self.assertEqual(summary.medical_status(held), "Independent hold · head/neck (short)")
        self.assertEqual(summary.medical_status({"availability": "Limited, minor: upper extremity, logged"}),
                         "Limited · upper extremity (minor)")

    def test_an_availability_entry_from_the_game_record_reads_back_whole(self):
        # W6-9: the roster's medical communication has one format, written from the game's record
        # and read by every page; an entry outside it is a validation error.
        from datetime import timedelta
        from runtime import season_summary as summary
        season = week_pages.Season(ROOT, SEASON)
        games = [r for r in season.receipts.values() if week_pages.ours_injured(r)]
        if not games:
            self.skipTest("no Jacksonville injury on record")
        receipt = max(games, key=lambda r: int(r["week"]))
        injury = dict(week_pages.ours_injured(receipt)[0], return_days=24, reassessment_days=6, severity="multi_week")
        text, source = week_pages.availability_entry(season, receipt, injury)
        played = week_pages.injury_date(season, receipt)
        entry = summary.medical_entry({"availability": text}, played)
        self.assertEqual(entry["severity"], "multi-week")
        self.assertNotIn("projected", entry["injury"])
        self.assertEqual(entry["projected"], played + timedelta(days=24))
        self.assertEqual(entry["reviews"], [played + timedelta(days=6)])
        self.assertTrue((ROOT / source).name.startswith(week_pages.people.slugify(injury["player"])))
        self.assertEqual(summary.format_errors({"players": [{"name": "X", "availability": text}]}, played), [])
        self.assertTrue(summary.format_errors({"players": [{"name": "X", "availability": "Sore"}]}, played))
        self.assertTrue(summary.format_errors({"players": [{"name": "X", "availability":
                                                            "Out, minor: trunk; projected return May 2"}]}, played))

    def test_leaders_count_sacks_in_words(self):
        from runtime import season_summary as summary
        team = {"players": {"A": {"tackles": 40, "sacks": 1}, "B": {"tackles": 41, "sacks": 1.5}}}
        self.assertEqual(summary.leaders(team), [("Tackling", "B", "41 tackles · 1.5 sacks")])
        team["players"]["B"]["sacks"] = 1
        self.assertEqual(summary.leaders(team)[0][2], "41 tackles · 1 sack")


class RebuildPagesTests(unittest.TestCase):
    def test_every_built_page_is_current(self):
        from scripts import rebuild_pages
        self.assertEqual(rebuild_pages.rebuild(ROOT, SEASON, check=True), ([], []))
        with self.assertRaises(ValueError):
            rebuild_pages.rebuild(ROOT, SEASON - 1, check=True)


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
