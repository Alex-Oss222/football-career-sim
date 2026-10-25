"""The Game Report of game week version 2 (docs/game_week_v2.md, section 6; runtime/game_report.py).

The layout is chosen per game. From 2014 Week 7, every postseason game included, it is the
template's (Coach record, sections 1 to 5, then Full game statistics with the two box-score markers
last: no media sections and a short football review, the user's decision of October 24, 2026);
2014 Week 6's report keeps the layout it was written in (sections 1 to 7, the pregame media in
section 2 and the postgame media in section 4), and still validates, its frozen pregame record
included. The checks: the sections in order, the box score last and filled from the closed game,
and the header's final score, the line score, overtime and the record agreeing with the game book.
Every closed game on file is before Week 7, so the template's checks are run on a closed earlier
game with the template's first week moved back for the test (``TemplateLayout``).

The editorial acceptance fixtures (tests/fixtures/game_reports/) are filled Game Reports: a quiet
game (2014 Week 4 at San Diego: no Jacksonville turnover, no player removed, no role change) and a
turnover-heavy game (2014 Week 2 at Washington: six turnovers), each told in the layout of its time
(Week 6's, as both games are before Week 7) from that week's closed game and its recorded
preparation and media, read only; and a playoff game in the template's layout, checked end to end
in tests/test_postseason_game_week.py. They are tests, not the career's record of those games, which
stays in each week's output.md as written.
"""
import json
import re
import sys
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime import clean_pages, game_report, game_weeks, gamebook  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402
from scripts import render_box_score  # noqa: E402

JAX = "Jacksonville Jaguars"
SEASON = 2014
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "game_reports"
SECTIONS = ["Coach record", "1. Preparation and final game-day decisions", "2. The game",
            "3. Football review and next week's work", "4. After-action report", "5. Final record and next game",
            "Full game statistics"]
WEEK_6_SECTIONS = ["Coach record", "1. Preparation and final game-day decisions", "2. Pregame media", "3. The game",
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


class TemplateLayout(unittest.TestCase):
    """Every closed game on file is before 2014 Week 7: these tests hold a closed earlier game to the
    template's layout by moving its first week back to the season's first week."""

    def setUp(self):
        patcher = patch.object(game_report, "TEMPLATE_FROM", (SEASON, 1))
        patcher.start()
        self.addCleanup(patcher.stop)


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
        self.assertTrue(clean_pages.page_errors(rel, page.replace("## 4. After-action report\n",
                                                                  "## 4. After-action snapshot\n")))

    def test_the_old_template_is_for_weeks_1_to_5(self):
        text = (ROOT / "foundation/templates/regular_season_output_template.md").read_text(encoding="utf-8")
        head = text.split("\n## ", 1)[0]
        self.assertIn("2014 Weeks 1 to 5 only", head)
        self.assertIn("game_week/game_report_template.md", head)


class LayoutTests(TemplateLayout):
    def setUp(self):
        super().setUp()
        self.game, self.receipt = closed(4)
        self.page = filled(template_report(self.receipt, self.game, "3-1"), self.receipt)

    def errors(self, text, receipt="closed"):
        return game_report.report_errors(text, self.receipt if receipt == "closed" else receipt, self.game)

    def test_a_filled_report_passes(self):
        self.assertEqual(self.errors(self.page), [])
        self.assertTrue(self.page.rstrip().endswith("<!-- /box-score -->"))

    def test_the_box_score_is_last(self):
        block = game_report.BLOCK.search(self.page).group(0)
        review = "## 3. Football review and next week's work"
        moved = self.page.replace(block, "").replace(review, block + "\n\n" + review)
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
        # The report as the practice week's close opens it: the header without a result, section 1.
        head, sections = self.parts()
        head = re.sub(r"^\*\*Final: .*\n", "", head + "\n", flags=re.M).rstrip("\n")
        pregame = "\n## ".join([head] + [s for s in sections if s.startswith("1. ")]) + "\n"
        self.assertEqual(self.errors(pregame, None), [])

    def test_sections_in_order_and_only_the_templates(self):
        head, sections = self.parts()
        four = next(i for i, s in enumerate(sections) if s.startswith("4. "))
        sections[four], sections[four + 1] = sections[four + 1], sections[four]
        swapped = "\n## ".join([head] + sections)
        self.assertTrue(any("not in the template's order" in e for e in self.errors(swapped)))
        self.assertTrue(any("is not a section" in e for e in self.errors(self.page.replace("## 4. After-action report",
                                                                                            "## 4. Weekly personnel"))))
        missing = self.page.replace("## 3. Football review and next week's work\n", "")
        self.assertTrue(any("is missing" in e for e in self.errors(missing)))
        record = self.page.replace("**Record after game:**", "**Record:**")
        self.assertIn("Game Report: '## 5. Final record and next game' needs its '**Record after game:**' line",
                      self.errors(record))

    def test_no_media_sections(self):
        for media, before in (("## 2. Pregame media\n\nNo pregame media session was recorded.\n\n", "## 2. The game"),
                              ("## Postgame media\n\nNo postgame media session was recorded.\n\n",
                               "## 3. Football review")):
            errors = self.errors(self.page.replace(before, media + before, 1))
            self.assertTrue(any("is not a section of the Game Report" in e and "has no media sections" in e
                                for e in errors), errors)

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
    pregame sections frozen before kickoff (acceptance tests 7 to 9), on the quiet game's fixture in
    Week 6's layout (its game is before Week 7)."""

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
        record = game_report.pregame_record(self.page, date(2014, 9, 28), self.game)
        self.assertEqual(list(record["sections"]), WEEK_6_SECTIONS[1:3])
        self.assertEqual(game_report.pregame_errors(self.page, record, closed=True, game=self.game), [])
        rewritten = self.page.replace("## 2. Pregame media\n", "## 2. Pregame media\n\nA note written after the game.\n", 1)
        self.assertTrue(any("'## 2. Pregame media' differs from the section frozen before kickoff" in e
                            for e in game_report.pregame_errors(rewritten, record, closed=True, game=self.game)))
        # The story may be written after the game; only sections 1 and 2 are frozen.
        later = self.page.replace("## 3. The game\n", "## 3. The game\n\nA line added after the game.\n", 1)
        self.assertEqual(game_report.pregame_errors(later, record, closed=True, game=self.game), [])
        # Once the game is played, a report with no freeze record fails; before it, nothing is owed.
        self.assertTrue(game_report.pregame_errors(self.page, None, closed=True, game=self.game))
        self.assertEqual(game_report.pregame_errors(self.page, None, closed=False, game=self.game), [])


class PerGameLayoutTests(unittest.TestCase):
    """The layout chosen per game: Week 6's as written, the template's from Week 7 and in the postseason."""

    def setUp(self):
        self.week6, self.receipt6 = closed(6)
        self.week7 = game_weeks.club_game(SeasonPaths(SEASON, ROOT), 7, JAX)
        self.template = (ROOT / game_report.TEMPLATE).read_text(encoding="utf-8")

    def test_each_game_has_its_layout(self):
        week6 = game_report.layout(self.week6)
        self.assertEqual(list(week6.sections), WEEK_6_SECTIONS)
        self.assertEqual((week6.story, week6.pregame), ("3. The game", tuple(WEEK_6_SECTIONS[1:3])))
        self.assertEqual(week6.final_record, "7. Final record and next game")
        playoff = dict(self.week7, week=18, game_type="postseason", round_name="Wild Card")
        later = dict(self.week7, game_id=self.week7["game_id"].replace("2014-", "2015-", 1), week=1)
        for game in (self.week7, playoff, later, None):
            template = game_report.layout(game)
            self.assertEqual(list(template.sections), SECTIONS)
            self.assertEqual((template.story, template.pregame), ("2. The game", (SECTIONS[1],)))
            self.assertEqual(template.final_record, "5. Final record and next game")
        self.assertEqual(game_report.layout(dict(self.week6, week=5)), week6)

    def test_week_6s_report_and_its_frozen_record_still_validate(self):
        paths = SeasonPaths(SEASON, ROOT)
        text = paths.game_report(6).read_text(encoding="utf-8")
        self.assertEqual(game_report.report_errors(text, self.receipt6, self.week6), [])
        from runtime.decisions import week_pages
        record = json.loads(week_pages(SEASON, 6, ROOT).pregame.read_text(encoding="utf-8"))
        self.assertEqual(list(record["sections"]), WEEK_6_SECTIONS[1:3])
        self.assertEqual(game_report.pregame_errors(text, record, True, game=self.week6), [])
        rewritten = text.replace("## 2. Pregame media\n", "## 2. Pregame media\n\nA line written after the game.\n", 1)
        self.assertTrue(game_report.pregame_errors(rewritten, record, True, game=self.week6))
        # Held to the template's layout, it is refused: Week 6 keeps the layout it was written in.
        later = dict(self.week6, game_id=self.week6["game_id"].replace("week06", "week07"), week=7)
        self.assertTrue(any("is not a section" in e for e in game_report.report_errors(text, None, later)))

    def test_a_week_7_report_with_a_media_section_is_refused(self):
        # The template as the practice week's close opens it, with nothing written yet, passes before the game.
        self.assertEqual(game_report.report_errors(self.template, None, self.week7), [])
        media = "## 2. Pregame media\n\nNo pregame media session was recorded.\n\n"
        opened = self.template.replace("## 2. The game\n", media + "## 2. The game\n", 1)
        errors = game_report.report_errors(opened, None, self.week7)
        self.assertIn("2014 Week 7 the Game Report has no media sections", " ".join(errors))
        postgame = self.template.replace("## 3. Football review", "## 4. Postgame media\n\nNone.\n\n## 3. Football review")
        self.assertTrue(any("'## 4. Postgame media' is not a section" in e
                            for e in game_report.report_errors(postgame, None, self.week7)))
        # Its freeze holds section 1 only; a record of sections 1 and 2, as Week 6's, is refused.
        record = game_report.pregame_record(self.template, date(2014, 10, 19), self.week7)
        self.assertEqual(list(record["sections"]), [SECTIONS[1]])
        self.assertEqual(game_report.pregame_errors(self.template, record, False, game=self.week7), [])
        both = dict(record, sections=dict(record["sections"], **{"2. Pregame media": "0" * 64}))
        self.assertTrue(any("this game's pregame sections are '## 1. Preparation and final game-day decisions'" in e
                            for e in game_report.pregame_errors(opened, both, False, game=self.week7)))


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
        order = game_report.layout(game).sections
        after = next(h for h in order if h.endswith(". After-action report"))
        after_action = story.split("\n## %s" % after, 1)[1].split("\n## %s" % order[order.index(after) + 1], 1)[0]
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

    def test_the_playoff_fixture_is_in_the_templates_layout(self):
        """The playoff fixture (tests/test_postseason_game_week.py) is told in the template's layout: no
        media, the four review lines short, and up to three players who stood out, one line each."""
        text = (FIXTURES / "playoff_game.md").read_text(encoding="utf-8")
        self.assertEqual([h.strip() for h in game_report.H2.findall(text)], SECTIONS)
        review = text.split("\n## 3. Football review and next week's work\n", 1)[1].split("\n## ", 1)[0]
        lines = [l for l in review.splitlines() if l.strip()]
        self.assertEqual([l.split(":**", 1)[0] for l in lines], ["**Offense", "**Defense",
                                                                "**Special teams and game management",
                                                                "**What changes for the next game"])
        self.assertLessEqual(len(review.split()), 180)
        players = text.split("\n### Players who stood out\n", 1)[1].split("\n### ", 1)[0]
        self.assertLessEqual(len([l for l in players.splitlines() if l.strip()]), 3)

    def test_the_fixtures_media_is_the_recorded_media(self):
        """The fixtures' dialogue (Week 6's layout) is the recorded sessions' own words, never written for
        the fixture."""
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
