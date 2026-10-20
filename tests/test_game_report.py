"""The Game Report of game week version 2 (docs/game_week_v2.md, section 6; runtime/game_report.py).

The template's layout (Coach record, sections 1 to 7, then Full game statistics with the two
box-score markers last) and its checks: the sections in order, the box score last and filled from
the closed game, and the header's final score, the line score, overtime and the record agreeing
with the game book. The editorial acceptance fixtures (tests/fixtures/game_reports/) are filled
Game Reports: a quiet game (2014 Week 4 at San Diego: no Jacksonville turnover, no player removed,
no role change) and a turnover-heavy game (2014 Week 2 at Washington: six turnovers), each told in
the new layout from that week's closed game and its recorded preparation and media, read only;
the playoff fixture is checked end to end in tests/test_postseason_game_week.py. They are tests,
not the career's record of those games, which stays in each week's output.md as written.
"""
import json
import re
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime import clean_pages, game_report, game_weeks, gamebook  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402
from scripts import render_box_score  # noqa: E402

JAX = "Jacksonville Jaguars"
SEASON = 2014
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "game_reports"
SECTIONS = ["Coach record", "1. Preparation and final game-day decisions", "2. Pregame media", "3. The game",
            "4. Postgame media", "5. Football review and next week's work", "6. After-action report",
            "7. Final record and next game", "Full game statistics"]
UNNAMED = "<!-- box-score event={{EVENT_ID}} team={{TEAM_NAME}} -->"


def closed(week, root=ROOT):
    """(game, closed record) of Jacksonville's regular-season game in ``week``."""
    paths = SeasonPaths(SEASON, root)
    game = game_weeks.club_game(paths, week, JAX)
    return game, game_weeks.closed_receipt(game_weeks.regular_receipts(paths), game)


def record_text(receipts):
    return sorted(game_report.record_forms(receipts, JAX), key=len)[0]


def template_report(receipt, game, record, root=ROOT):
    """The Game Report template filled for ``receipt`` with its prompts' own words: the header, the
    line score and the record reconciled with the game, the Overtime section kept only when it was
    played, the markers left unnamed for the box-score step. A structural page, not a football one."""
    text = (Path(root) / game_report.TEMPLATE).read_text(encoding="utf-8")
    away, home = receipt["away"], receipt["home"]
    score = receipt["final_score"]
    win, lose = (away, home) if score[away] >= score[home] else (home, away)
    when = date.fromisoformat(game["date"])
    round_line = ("**%s, %s**  " % (game["round_name"], game["conference"]) if game.get("game_type") == "postseason"
                  else "**Regular-season Week %d**  " % int(game["week"]))
    out, skip, seen_table = [], False, False
    for line in text.splitlines():
        if line.startswith("# [Away team]"):
            line = "# %s at %s" % (away, home)
        elif line.startswith("**[Regular-season Week N"):
            line = round_line
        elif line.startswith("[Day, Date]"):
            line = "%s, %s %d, %d | %s | %s  " % (game["weekday"], when.strftime("%B"), when.day, when.year,
                                                    game["kickoff_et"], game.get("stadium"))
        elif line.startswith("**Final: [Winner]"):
            line = "**Final: %s %d, %s %d**" % (win, score[win], lose, score[lose])
        elif line.startswith("<!-- event-record:"):
            continue
        elif line.startswith("**Record after game:**"):
            line = "**Record after game:** %s.  " % record
        elif line.startswith("### Overtime"):
            skip = not game_report.overtime_played(receipt)
            if skip:
                continue
        elif line.startswith("### Final score by quarter"):
            out += [line, "", gamebook.line_score_table(receipt)]
            skip = "table"          # the template's own table is replaced by the game book's
            continue
        elif line.startswith("#"):
            skip = False
        if skip == "table":
            if line.startswith("|"):
                seen_table = True
                continue
            if not seen_table:
                continue        # the blank line before the template's table
            skip = False        # the blank line after it is kept
        if skip is True:
            continue
        out.append(re.sub(r"\[([^\]]*)\]", r"\1", line))
    return "\n".join(out).rstrip("\n") + "\n"


def filled(text, receipt, root=ROOT):
    """``text`` with its unnamed markers naming the game and the box score filled from the game book."""
    named = game_report.place_markers(text, receipt["event_id"])
    return render_box_score.fill(named, SeasonPaths(SEASON, root).receipts, SEASON, report=True)


class TemplateTests(unittest.TestCase):
    def test_the_sections_are_the_designs(self):
        self.assertEqual(game_report.sections(ROOT), SECTIONS)

    def test_the_template_carries_no_writer_note_and_ends_with_the_markers(self):
        text = (ROOT / game_report.TEMPLATE).read_text(encoding="utf-8")
        for note in ("AUTHORING", "BUILD NOTE", "not printed", "remove from issued"):
            self.assertNotIn(note, text)
        self.assertTrue(text.rstrip().endswith(UNNAMED + "\n<!-- /box-score -->"))
        events = [l for l in text.splitlines() if l.startswith("<!-- event-record:")]
        self.assertEqual(len(events), 1)
        self.assertTrue(clean_pages.event_marker(events[0]))

    def test_the_template_with_its_prompts_filled_is_a_clean_page(self):
        game, receipt = closed(4)
        page = template_report(receipt, game, "3-1")
        rel = SeasonPaths(SEASON, ROOT).game_report(6).relative_to(ROOT).as_posix()
        self.assertEqual(clean_pages.page_errors(rel, page), [])
        self.assertIn(UNNAMED, page)       # the unnamed markers pass until the game is named
        self.assertTrue(clean_pages.page_errors(rel, page.replace("## 6. After-action report\n",
                                                                  "## 6. After-action snapshot\n")))

    def test_the_old_template_is_for_weeks_1_to_5(self):
        text = (ROOT / "foundation/templates/regular_season_output_template.md").read_text(encoding="utf-8")
        head = text.split("\n## ", 1)[0]
        self.assertIn("2014 Weeks 1 to 5 only", head)
        self.assertIn("game_week/game_report_template.md", head)


class LayoutTests(unittest.TestCase):
    def setUp(self):
        self.game, self.receipt = closed(4)
        self.page = filled(template_report(self.receipt, self.game, "3-1"), self.receipt)

    def errors(self, text, receipt="closed"):
        return game_report.report_errors(text, self.receipt if receipt == "closed" else receipt, self.game)

    def test_a_filled_report_passes(self):
        self.assertEqual(self.errors(self.page), [])
        self.assertTrue(self.page.rstrip().endswith("<!-- /box-score -->"))

    def test_the_box_score_is_last(self):
        block = game_report.BLOCK.search(self.page).group(0)
        moved = self.page.replace(block, "").replace("## 4. Postgame media", block + "\n\n## 4. Postgame media")
        self.assertTrue(any("outside '## Full game statistics'" in e for e in self.errors(moved)), self.errors(moved))
        after = self.page + "\nA closing note.\n"
        self.assertTrue(any("is not last" in e for e in self.errors(after)))
        twice = self.page + "\n" + block + "\n"
        self.assertTrue(any("exactly one box score" in e for e in self.errors(twice)))

    def test_unnamed_markers_after_the_game_are_named_first(self):
        unnamed = template_report(self.receipt, self.game, "3-1")
        self.assertTrue(any("does not name the game yet" in e for e in self.errors(unnamed)))

    def parts(self):
        head, *sections = self.page.split("\n## ")
        return head, sections

    def test_no_result_before_the_game(self):
        self.assertTrue(any("before the game has been played" in e for e in self.errors(self.page, None)))
        # The report as the practice week's close opens it: the header without a result, sections 1 and 2.
        head, sections = self.parts()
        head = re.sub(r"^\*\*Final: .*\n", "", head + "\n", flags=re.M).rstrip("\n")
        pregame = "\n## ".join([head] + [s for s in sections if s.startswith(("1. ", "2. "))]) + "\n"
        self.assertEqual(self.errors(pregame, None), [])

    def test_sections_in_order_and_only_the_templates(self):
        head, sections = self.parts()
        four = next(i for i, s in enumerate(sections) if s.startswith("4. "))
        sections[four], sections[four + 1] = sections[four + 1], sections[four]
        swapped = "\n## ".join([head] + sections)
        self.assertTrue(any("not in the template's order" in e for e in self.errors(swapped)))
        self.assertTrue(any("is not a section" in e for e in self.errors(self.page.replace("## 6. After-action report",
                                                                                            "## 6. Weekly personnel"))))
        missing = self.page.replace("## 5. Football review and next week's work\n", "")
        self.assertTrue(any("is missing" in e for e in self.errors(missing)))

    def test_the_result_reconciles_with_the_game_book(self):
        wrong = self.page.replace("**Final: San Diego Chargers 21, Jacksonville Jaguars 20**",
                                  "**Final: San Diego Chargers 24, Jacksonville Jaguars 20**")
        self.assertTrue(any("the game ended" in e for e in self.errors(wrong)))
        order = self.page.replace("**Final: San Diego Chargers 21, Jacksonville Jaguars 20**",
                                  "**Final: Jacksonville Jaguars 20, San Diego Chargers 21**")
        self.assertTrue(any("winner first" in e for e in self.errors(order)))
        line = self.page.replace("| Jaguars | 3 | 7 | 3 | 7 | 20 |", "| Jaguars | 3 | 7 | 7 | 3 | 20 |")
        self.assertTrue(any("line score differs" in e for e in self.errors(line)))
        record = self.page.replace("**Record after game:** 3-1.", "**Record after game:** 4-0.")
        self.assertTrue(any("record after the game is 3-1" in e for e in self.errors(record)))
        round_line = self.page.replace("**Regular-season Week 4**", "**Regular-season Week 5**")
        self.assertTrue(any("round line" in e for e in self.errors(round_line)))
        overtime = self.page.replace("### Final score by quarter", "### Overtime\n\nNone.\n\n### Final score by quarter")
        self.assertTrue(any("ended in regulation" in e for e in self.errors(overtime)))

    def test_an_overtime_game_needs_its_overtime(self):
        game, receipt = closed(1)
        self.assertTrue(game_report.overtime_played(receipt))
        page = filled(template_report(receipt, game, "1-0"), receipt)
        self.assertIn("### Overtime", page)
        self.assertIn("| OT |", page)
        self.assertEqual(game_report.report_errors(page, receipt, game), [])
        without = re.sub(r"### Overtime\n\n.*?\n\n", "", page, flags=re.S)
        self.assertTrue(any("went to overtime" in e for e in game_report.report_errors(without, receipt, game)))


class StoryTests(unittest.TestCase):
    """The story's figures against the game book, one table of figures (the statistics), and the
    pregame sections frozen before kickoff (acceptance tests 7 to 9)."""

    def setUp(self):
        self.game, self.receipt = closed(4)        # San Diego 21, Jacksonville 20
        self.page = filled((FIXTURES / "quiet_game.md").read_text(encoding="utf-8"), self.receipt)
        self.assertEqual(self.errors(self.page), [])

    def errors(self, text):
        return game_report.report_errors(text, self.receipt, self.game)

    def told(self, sentence, section="## 3. The game\n"):
        return self.page.replace(section, section + "\n" + sentence + "\n", 1)

    def test_a_score_the_game_never_stood_at_is_refused(self):
        errors = self.errors(self.told("Jacksonville led 14-6 early in the third quarter and won 31-27."))
        self.assertIn("Game Report: the game story gives 14-6, a score the game never stood at (the scoring summary "
                      "runs from 0-0 to Jacksonville Jaguars 20, San Diego Chargers 21)", errors)
        self.assertTrue(any("gives 31-27" in e for e in errors))
        self.assertTrue(any("'Jacksonville led 14-6 early in the third quarter and won 31-27.' does not match the game "
                            "book" in e for e in errors), errors)
        # Every score it stood at stands, either way round, and the record.
        stood = game_report.scores_stood(self.receipt)
        self.assertIn((0, 0), stood)
        self.assertIn((20, 21), stood)
        self.assertEqual(self.errors(self.told("San Diego led 21-13, and Jacksonville, now 3-1, cut it to 21-20.")), [])
        self.assertTrue(any("gives 20-14" in e for e in self.errors(self.told("Jacksonville led 20-14."))))

    def test_won_and_lost_name_the_right_club(self):
        self.assertTrue(self.errors(self.told("Jacksonville beat San Diego 21-20.")))
        self.assertTrue(self.errors(self.told("San Diego lost 21-20.")))
        self.assertEqual(self.errors(self.told("San Diego beat Jacksonville 21-20, and the Jaguars fell 21-20.")), [])
        # Anywhere in the prose, not only the story; a result of another club's game is not this game's.
        review = "## 5. Football review and next week's work\n"
        self.assertTrue(self.errors(self.told("The Jaguars won 20-21 on the road.", review)))
        self.assertEqual(self.errors(self.told("Houston beat Tennessee 30-17 the same day.", review)), [])

    def test_a_statistics_table_in_the_story_is_refused(self):
        table = "| Player | CMP | ATT | YDS |\n|---|---|---|---|\n| Cousins | 20 | 30 | 250 |\n"
        for section in ("### Players who stood out\n", "## 5. Football review and next week's work\n",
                        "## 3. The game\n"):
            text = self.page.replace(section, section + "\n" + table, 1)
            self.assertTrue(any("the only tables before the full game statistics are the coach record, the line score "
                                "and the after-action injuries" in e for e in self.errors(text)), section)
        # The after-action injuries table in the template's columns stands.
        injuries = ("| Player | What was reported | Effect now | Next medical decision |\n|---|---|---|---|\n"
                    "| A player | Out | No practice | Not communicated |\n")
        text = self.page.replace("### Injuries and availability changes\n",
                                 "### Injuries and availability changes\n\n" + injuries, 1)
        self.assertEqual(game_report.table_errors(text), [])

    def test_the_pregame_sections_are_frozen_before_kickoff(self):
        from datetime import date
        record = game_report.pregame_record(self.page, date(2014, 9, 28))
        self.assertEqual(sorted(record["sections"]), sorted(game_report.PREGAME))
        self.assertEqual(game_report.pregame_errors(self.page, record, closed=True), [])
        rewritten = self.page.replace("## 2. Pregame media\n", "## 2. Pregame media\n\nA note written after the game.\n", 1)
        self.assertTrue(any("'## 2. Pregame media' differs from the section frozen before kickoff" in e
                            for e in game_report.pregame_errors(rewritten, record, closed=True)))
        # The story may be written after the game; only sections 1 and 2 are frozen.
        later = self.page.replace("## 3. The game\n", "## 3. The game\n\nA line added after the game.\n", 1)
        self.assertEqual(game_report.pregame_errors(later, record, closed=True), [])
        # Once the game is played, a report with no freeze record fails; before it, nothing is owed.
        self.assertTrue(game_report.pregame_errors(self.page, None, closed=True))
        self.assertEqual(game_report.pregame_errors(self.page, None, closed=False), [])


class EditorialFixtureTests(unittest.TestCase):
    """Each fixture is a filled Game Report that passes every Game Report check, with the box score
    last and identical to the game book."""

    def check_fixture(self, name, week):
        game, receipt = closed(week)
        text = (FIXTURES / name).read_text(encoding="utf-8")
        page = filled(text, receipt)
        paths = SeasonPaths(SEASON, ROOT)
        rel = (paths.week_folder(week) / "Game_Report.md").relative_to(ROOT).as_posix()
        self.assertEqual(game_report.report_errors(page, receipt, game), [])
        self.assertEqual(clean_pages.page_errors(rel, page), [])
        block = game_report.BLOCK.search(page)
        self.assertEqual(block.group("body"), render_box_score.render(receipt, JAX, SEASON, report=True) + "\n")
        self.assertEqual(page[block.end():].strip(), "")
        # The prose carries no statistics table of its own: the only tables before the game book are
        # the coach record, the line score and the after-action injuries, and section 6 holds no
        # roster inventory.
        story = page.split("\n## Full game statistics", 1)[0]
        self.assertLessEqual(len(re.findall(r"^\|\s*:?-{3,}", story, re.M)), 3)
        after_action = story.split("\n## 6. After-action report", 1)[1].split("\n## 7.", 1)[0]
        self.assertLessEqual(len(re.findall(r"^\|\s*:?-{3,}", after_action, re.M)), 1)
        self.assertEqual(re.findall(r"^### (.+)$", after_action, re.M),
                         ["Injuries and availability changes", "Players who stood out",
                          "Role or transaction consequences"])
        # Every link resolves from the week's folder.
        for target in re.findall(r"\]\(([^)#]+)", story):
            resolved = (paths.week_folder(week) / target.replace("%20", " ")).resolve()
            self.assertTrue(resolved.is_file(), target)
        return page

    def test_the_quiet_game(self):
        page = self.check_fixture("quiet_game.md", 4)
        self.assertIn("No changes.", page)
        self.assertIn("No one was removed from the game.", page)

    def test_the_turnover_heavy_game(self):
        page = self.check_fixture("turnover_game.md", 2)
        receipt = closed(2)[1]
        self.assertEqual(sum(receipt["team_stats"][c]["turnovers"] for c in (receipt["away"], receipt["home"])), 6)
        self.assertIn("three interceptions", page)

    def test_the_fixtures_media_is_the_recorded_media(self):
        """The fixtures' dialogue is the recorded sessions' own words, never written for the fixture."""
        for name, week in (("quiet_game.md", 4), ("turnover_game.md", 2)):
            recorded = SeasonPaths(SEASON, ROOT).game_report(week).read_text(encoding="utf-8")
            text = (FIXTURES / name).read_text(encoding="utf-8")
            for section in ("## 2. Pregame media", "## 4. Postgame media"):
                body = text.split(section, 1)[1].split("\n## ", 1)[0]
                for line in body.strip().splitlines():
                    if line.startswith(("**Reporter:**", "**Stone:**")):
                        self.assertIn(line, recorded, (name, line[:60]))


if __name__ == "__main__":
    unittest.main()
