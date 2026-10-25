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
SECTIONS = ("## 1. The game and what is at stake", "## 2. Our last game and the self-scout",
            "## 3. Medical and game-day availability", "## 4. Opponent scouting: when they have the ball",
            "## 5. Opponent scouting: when we have the ball", "## 6. Special teams and game operations",
            "## 7. Staff proposals, alternatives and costs", "## 8. What is owed by the head coach")


def copy_repo(test):
    tmp = tempfile.TemporaryDirectory(dir=ROOT.parent)
    test.addCleanup(tmp.cleanup)
    root = Path(tmp.name) / "repo"
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(*IGNORED), symlinks=True)
    return root


class RegistryTests(unittest.TestCase):
    def tables(self):
        """{subheading: rows} of the plan's "The decisions in a year" section."""
        text = (ROOT / "docs/rebuild_plan.md").read_text(encoding="utf-8")
        section = text.split("## The decisions in a year", 1)[1].split("\n## ", 1)[0]
        out = {}
        for part in section.split("\n### ")[1:]:
            title, body = part.split("\n", 1)
            out[title.split(":")[0].strip()] = [[c.strip() for c in line.strip().strip("|").split("|")]
                                                for line in body.splitlines()
                                                if line.startswith("| ") and not line.startswith("| When")]
        return out

    def test_every_decision_of_the_plan_is_named(self):
        rows = self.tables()["Phase decisions"]
        named = [(d.when, d.brief, d.page, d.result) for d in decisions.REGISTRY]
        for row in rows:
            brief = re.sub(r"\s*\(.*\)$", "", row[1])
            self.assertIn((row[0], brief, row[2], row[3]), named)
        self.assertEqual(len(rows), len(decisions.REGISTRY))
        self.assertEqual([d.kind for d in decisions.REGISTRY if d.implemented], ["game_week", "bye_week"])
        # Step 5 built the injury replacement, trade talks (short of executing a trade) and the news of
        # another club's head-coach change; the step 6 events wait.
        self.assertEqual([e.kind for e in decisions.EVENTS + decisions.NEWS if e.implemented],
                         ["injury_replacement", "trade_talks", "head_coach_change"])
        # The season's own page, apart from any week's My Responses page.
        self.assertEqual(decisions.BY_KIND["season_end"].page, "My Season Response")
        self.assertNotIn(decisions.RESPONSES, [d.page for d in decisions.REGISTRY])

    def test_every_event_of_the_plan_is_named(self):
        # The events inside a week or phase are inserts, not decisions of three pages.
        rows = self.tables()["Events inside a week or phase"]
        self.assertEqual([(r[0], r[1], r[2], int(r[4])) for r in rows],
                         [(e.when, e.brings, e.result, e.step) for e in decisions.EVENTS])
        for row, event in zip(rows, decisions.EVENTS):
            folder = decisions.event_folder(event, 2014, ROOT)
            self.assertTrue(folder.is_dir(), (event.kind, folder))
            self.assertTrue(folder.relative_to(ROOT).as_posix().endswith(row[3]), (event.kind, folder, row[3]))
        self.assertEqual({e.step for e in decisions.EVENTS if e.kind in ("injury_replacement", "trade_talks")}, {5})
        self.assertEqual({e.step for e in decisions.EVENTS if e.kind not in ("injury_replacement", "trade_talks")}, {6})
        self.assertFalse(set(decisions.EVENT_KIND) & set(decisions.BY_KIND))
        # News (an event decided outside Jacksonville) is a kind of its own, built in step 5.
        self.assertFalse(set(decisions.NEWS_KIND) & (set(decisions.EVENT_KIND) | set(decisions.BY_KIND)))
        self.assertEqual({e.step for e in decisions.NEWS}, {5})
        # Every owner folder resolves through the folder map; one that an event uses, or that exists,
        # is a folder the plan names (a news owner's folder comes with its first page).
        text = (ROOT / "docs/rebuild_plan.md").read_text(encoding="utf-8")
        used = {e.owner for e in decisions.EVENTS}
        self.assertTrue({e.owner for e in decisions.NEWS} <= set(decisions.OWNERS))
        for owner in decisions.OWNERS:
            folder = decisions.event_folder(decisions.Event("x", "x", "x", owner, "x", 5), 2014, ROOT)
            self.assertTrue(folder.is_relative_to(ROOT / "career/2014"), (owner, folder))
            if owner in used or folder.exists():
                self.assertTrue(folder.is_dir(), (owner, folder))
                self.assertIn(folder.relative_to(ROOT / "career/2014").as_posix(), text)
        self.assertEqual(decisions.week_pages(2014, 6, ROOT).responses.name, "My_Responses.md")

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
        # The template's sections, in its order and words (foundation/templates/game_week).
        template = (ROOT / "foundation/templates/game_week/game_week_briefing_template.md").read_text(encoding="utf-8")
        self.assertEqual([l for l in template.splitlines() if l.startswith("## ")], list(SECTIONS))
        from runtime.player_pages import club_short
        self.assertIn(club_short(self.wk.opponent), text)
        self.assertIsNotNone(render_game_week.issued_on(self.wk))
        self.assertEqual(render_game_week.validation_errors(self.root), [])
        self.assertEqual(render_game_week.check(self.root), [])

    def test_missing_staff_texts_are_to_come(self):
        # Whatever the week's stored state, a briefing without the staff's texts says they are to come.
        self.wk.pages.staff_texts.unlink(missing_ok=True)
        with contextlib.redirect_stdout(io.StringIO()):
            render_game_week.write(self.root)
        text = self.wk.pages.briefing.read_text(encoding="utf-8")
        for label in ("Staff's central football question", "Two things to carry forward"):
            self.assertIn("**%s:** To come." % label, text)
        self.assertEqual(len(re.findall(r"\*\*\w+'s recommendation:\*\* To come\.", text)), 2)
        self.assertIn("'s report:** To come.", text)
        proposals = text.split(SECTIONS[6], 1)[1].split("\n## ", 1)[0]
        self.assertIn("| To come | To come | To come |", proposals)
        # The optional parts are left out until they are stored.
        for label in ("What the game book does not settle", "Not established", "Possible operational question"):
            self.assertNotIn("**%s:**" % label, text)

    def test_stored_texts_are_shown_and_may_cite_only_the_page(self):
        record = self.wk.record("Jacksonville Jaguars")
        when = self.wk.master.isoformat()
        texts = {"texts": {
            "central_question": {"author": "Mike Tice", "date": when, "text": "Can we stay %s on the road?" % record},
            "carry_forward": {"author": "Mike Tice", "date": when,
                              "items": [{"point": "Ball security", "text": "Film first."},
                                        {"point": "Fourth downs", "text": "Decide at the spot."}]},
            "defense_questions": {"author": "Romeo Crennel", "date": when, "rows": {"Jake Locker": "Contain him."}}}}
        path = self.wk.pages.staff_texts
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(texts), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            render_game_week.write(self.root)
        text = self.wk.pages.briefing.read_text(encoding="utf-8")
        self.assertIn("**Staff's central football question:** Can we stay %s on the road? (Mike Tice, " % record, text)
        self.assertIn("- **Fourth downs.** Decide at the spot.", text)
        self.assertEqual(render_game_week.validation_errors(self.root), [])
        if "| Jake Locker, QB |" in text:
            self.assertIn("Contain him.", text)
        texts["texts"]["central_question"]["text"] = "We are 9,876 yards better."
        path.write_text(json.dumps(texts), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            render_game_week.write(self.root)
        self.assertTrue(any("9,876 is not a figure the briefing shows" in e
                            for e in render_game_week.validation_errors(self.root)))
        # A text with no author, or a part the briefing has no place for, is refused.
        del texts["texts"]["central_question"]["author"]
        path.write_text(json.dumps(texts), encoding="utf-8")
        self.assertTrue(any("needs its author and date" in e for e in render_game_week.validation_errors(self.root)))
        texts["texts"] = {"staff_mood": {"author": "x", "date": when, "text": "y"}}
        path.write_text(json.dumps(texts), encoding="utf-8")
        self.assertTrue(any("is not a part of the briefing" in e for e in render_game_week.validation_errors(self.root)))

    def test_the_medical_table_shows_only_whom_a_decision_turns_on(self):
        text = self.wk.pages.briefing.read_text(encoding="utf-8")
        section = text.split(SECTIONS[2], 1)[1].split("\n## ", 1)[0]
        data = json.loads(self.wk.paths.roster.read_text(encoding="utf-8"))
        for p in data["players"]:
            if p["list"] == "reserve" and "designated for return" not in p["status"]:
                self.assertNotIn(p["name"], section)
        self.assertIn("**Game-day numbers:**", section)
        self.assertIn("**Medical authority:**", section)

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
        kept = [p for p, _ in render_game_week.earlier_briefings(render_game_week.Week(self.root))]
        with contextlib.redirect_stdout(io.StringIO()):
            written = render_game_week.write(self.root)
        earlier = [path for path, _ in render_game_week.earlier_briefings(render_game_week.Week(self.root))]
        self.assertEqual(earlier[:-1], kept)
        earlier = earlier[-1:]
        self.assertEqual(earlier[0].read_text(encoding="utf-8"), old)
        self.assertIn(earlier[0], written)
        section = self.wk.pages.briefing.read_text(encoding="utf-8").split(SECTIONS[2], 1)[1].split("\n## ", 1)[0]
        # His row is gone (or there): read the player column, since another held player's contingency
        # may name him as the next in the chart's order.
        from runtime.game_plan import cells
        rows = [cells(line) for line in section.splitlines() if line.startswith("| ")][1:]
        players = {re.sub(r"^\[([^\]]*)\]\(.*\)$", r"\1", r[0].rpartition(", ")[0]) for r in rows}
        self.assertEqual(changed["name"] in players, not under)
        self.assertIn(earlier[0].name, self.wk.pages.readme.read_text(encoding="utf-8"))
        # Both issues are in the week's issue record, the earlier one under its kept name.
        record = render_game_week.issues(render_game_week.Week(self.root))
        self.assertEqual([e["file"] for e in record], [p.name for p in kept] + [earlier[0].name,
                                                                                 self.wk.pages.briefing.name])
        self.assertIn("**Status:** Revised: it replaces the briefing of", self.wk.pages.briefing.read_text(encoding="utf-8"))
        # Issuing a page moves no time and settles nothing.
        self.assertEqual((self.root / "state/05_Current_Season_State.md").read_bytes(), state)
        self.assertEqual((self.root / "state/decision_queue.json").read_bytes(), queue)
        self.assertEqual(render_game_week.validation_errors(self.root), [])

    def test_the_briefing_lists_only_the_games_standing_instructions(self):
        # The career answers (current_job.CAREER_SUBJECTS) are never game directions: the briefing
        # lists the game's (current_job.SUBJECTS), the desk lists every one.
        from runtime import current_job
        from scripts import render_career_views
        text = self.wk.pages.briefing.read_text(encoding="utf-8")
        block = text.split("**Standing directions:**", 1)[1].split("**What the club, not Stone, decides:**", 1)[0]
        every = current_job.instructions(self.wk.job)
        career = [i for i in every if i.get("subject") in current_job.CAREER_SUBJECTS]
        game = [i for i in every if i.get("subject") in current_job.SUBJECTS]
        # The standing practice instruction is not a game direction either.
        practice = [i for i in every if i.get("subject") in current_job.PRACTICE_SUBJECTS]
        self.assertTrue(career and game and practice)
        for item in career:
            self.assertNotIn("**%s" % render_career_views.SUBJECT_LABEL[item["subject"]], block)
        self.assertNotIn("**Practice schedule", block)
        for item in game:
            self.assertIn("**%s" % render_career_views.SUBJECT_LABEL[item["subject"]], block)
        render_career_views.write(self.root)
        desk = self.wk.paths.desk.read_text(encoding="utf-8")
        for item in career:
            self.assertIn("**%s" % render_career_views.SUBJECT_LABEL[item["subject"]], desk)
        self.assertIn("**Practice schedule:**", desk)
        # A career answer alone never makes the briefing out of date.
        self.assertFalse(any("a new briefing is due" in e for e in render_game_week.check(self.root)))

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
        kept = render_game_week.earlier_briefings(render_game_week.Week(self.root))
        edited = issued.replace("| Records entering the week | Jacksonville %s;" % mine,
                                "| Records entering the week | Jacksonville 9-0;", 1)
        self.assertNotEqual(edited, issued)
        page.write_text(edited, encoding="utf-8")
        self.assertTrue(any("differs from the briefing issued" in e for e in render_game_week.validation_errors(self.root)))
        with self.assertRaises(ValueError):
            render_game_week.write(self.root)
        self.assertEqual(render_game_week.earlier_briefings(render_game_week.Week(self.root)), kept)
        self.assertEqual(sorted(self.wk.pages.folder.glob(page.stem + "_*.md")), sorted(p for p, _ in kept))
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
        # Its revision is the record's too: the n-th issue of its day, named from the second on.
        current = render_game_week.current_issue(self.wk)
        entries = render_game_week.issues(self.wk)
        self.assertEqual([e["revision"] for e in entries], render_game_week.revisions(entries))
        label = render_game_week.label_of(current)
        self.assertIn("**Issued:** %s" % label, page.read_text(encoding="utf-8"))
        self.assertIn("Issued %s" % label, self.wk.pages.readme.read_text(encoding="utf-8"))
        self.assertEqual(label.endswith(", revision %d" % current[1]), current[1] > 1)

    def test_a_misnumbered_revision_fails(self):
        path = render_game_week.issues_path(self.wk)
        data = json.loads(path.read_text(encoding="utf-8"))
        data["issued"][-1]["revision"] += 1
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assertTrue(any("is recorded as revision" in e for e in render_game_week.validation_errors(self.root)))
        del data["issued"][-1]["revision"]
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assertTrue(any("is malformed" in e for e in render_game_week.validation_errors(self.root)))


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
        # Only the comparable count, the way every game is counted now, with the weeks it covers; the
        # earlier count is neither shown beside it nor added to it, and the page carries no accounting note.
        self.assertEqual(penalties, {"Penalties since Week 5": ["10 for 63 yards", "7 for 69 yards"]})
        self.assertIsNone(note)
        self.assertNotIn("18 for 121 yards", str(rows))
        self.assertNotIn("8 for 58 yards", str(rows))
        # One method alone is one row, and the other figures are the statistics owner's totals.
        rows, note = render_game_week.team_rows(games[1:], "A")
        self.assertIsNone(note)
        self.assertIn(["Penalties", "10 for 63 yards", "7 for 69 yards"], rows)
        self.assertIn(["Points", "30", "30"], render_game_week.team_rows(games, "A")[0])

    def test_the_contingency_is_who_takes_his_place_not_the_next_name(self):
        # Week 6 review: the next name in the group's list can be another starter (the center after
        # the left guard) or a safety after the nickel; the default names who the game's own rules put
        # in his slot or seat, with the chart and its last game-day list as they stand.
        chart = {"depth": {"OL": ["LT1", "LG1", "C1", "RG1", "RT1", "T2", "G2", "C2"],
                           "DB": ["CB1", "CB2", "S1", "S2", "NB", "S3", "OR", "CB3"],
                           "WR": ["X", "Z"]},
                 "positions": {"LT1": "OT", "LG1": "OT", "C1": "C", "RG1": "G", "RT1": "OT", "T2": "OT",
                               "G2": "G", "C2": "C", "CB1": "CB", "CB2": "CB", "S1": "S", "S2": "S",
                               "NB": "CB", "S3": "S", "OR": "CB", "CB3": "CB", "X": "WR", "Z": "WR"},
                 "roles": {"NB": ["nickel"], "OR": ["outside_reserve"]}}
        replace = render_game_week.chart_replacement
        self.assertEqual(replace(chart, "LG1", set()), ("G2", "left guard"))
        self.assertEqual(replace(chart, "C1", set()), ("C2", "center"))
        self.assertEqual(replace(chart, "NB", {"CB3"}), ("OR", "nickel"))
        self.assertEqual(replace(chart, "NB", set()), ("CB3", "nickel"))
        self.assertEqual(replace(chart, "CB1", set()), ("OR", "outside corner"))
        self.assertEqual(replace(chart, "S1", set()), ("S3", "safety"))
        # A reserve holds no slot or seat, and another group keeps the next name in its order.
        self.assertIsNone(replace(chart, "T2", set()))
        self.assertIsNone(replace(chart, "X", set()))

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

    def test_a_player_leading_more_than_one_category_has_one_row(self):
        from types import SimpleNamespace
        games = [receipt("e1", 1, "B", "A", {"A": 10, "B": 7},
                         {"A": {"players": {"Brown": player("ILB", sacks=2, tackles=34),
                                            "Woodyard": player("ILB", sacks=0, tackles=34),
                                            "Pollard": player("SS", sacks=2, tackles=20, defensive_interceptions=2)}},
                          "B": {"players": {}}})]
        rows = render_game_week.threat_rows(SimpleNamespace(opponent="A"), games, ("Tackles", "Sacks", "Interceptions"),
                                            lambda name: "To come")
        names = [r[0].split(",")[0] for r in rows]
        self.assertEqual(sorted(names), ["Brown", "Pollard", "Woodyard"])
        self.assertEqual(len(names), len(set(names)))
        brown = next(r for r in rows if r[0].startswith("Brown"))
        self.assertEqual(brown[1], "Tackles leader, tied: 34; Sacks leader, tied: 2")
        pollard = next(r for r in rows if r[0].startswith("Pollard"))
        self.assertEqual(pollard[1], "Sacks leader, tied: 2; Interceptions leader: 2")

    def test_an_ask_whose_date_has_passed_is_left_out(self):
        from datetime import date
        ask = ("the menu, including whether the Flea Flicker and TE Delay stay, and who takes Trawick's practice work "
               "after his October 7 exam.")
        self.assertEqual(render_game_week.current_ask(ask, date(2014, 10, 5)), ask)
        self.assertEqual(render_game_week.current_ask(ask, date(2014, 10, 7)), ask)
        self.assertEqual(render_game_week.current_ask(ask, date(2014, 10, 12)),
                         "the menu, including whether the Flea Flicker and TE Delay stay.")
        self.assertEqual(render_game_week.current_ask("who does not dress: 7 of the 53; none out", date(2014, 10, 12)),
                         "who does not dress: 7 of the 53; none out")

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
