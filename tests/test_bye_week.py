"""The bye week (rebuild step 5, C3; docs/bye_week.md, sections 3 to 7).

In a temporary copy, the club's games up to the bye are closed by relabelling
earlier closed Jacksonville games onto them, game for game (the same scores and
statistics, a fake result for the copy only), with recorded practice weeks as the
standing instruction sets them, and the clock moved to the evening of the game
before the bye. The bye then opens: the Bye Week Review is issued from stored
facts and the next game's briefing is not; Stone's My Adjustments is checked in
the design's messages and applied; the bye's practice and rest record is written
against it; a test result resolved in the bye appears on the bye's index and its
review only; the league's other games of the week close with the bye's answers
open (the hold is the bye's own close alone); the staff's Bye Week Report is held
to the records; and the bye closes on its Sunday with the club's record
unchanged and no Jacksonville game recorded, after which the next game week
opens.

docs/bye_week.md section 7, tests 1 to 12: (1) the bye is recognized from the
fixtures, the games around it anchored to them and its review built from the
closed games only (OpenTests); (2) the three pages exist in the bye week's folder
and the earlier season's bye pages are untouched (FlowTests); (3) opening a page
moves no time and plays no game, and the open answer holds only the bye's close
(OpenTests); (4) no Jacksonville game, score or box score, and no game plan,
inactives or practice item for the bye (OpenTests, FlowTests); (5) "No change"
answers an area (OpenTests); (6) the break and the padded budget are checked and
the week's sessions recorded as held (OpenTests, FlowTests); (7) no medical
clearance, role from an out player or transaction is taken from the page
(OpenTests); (8) the same decisions in other words compile to the same bytes
(OpenTests); (9) a game elsewhere in the week does not change the issued review
(OpenTests); (10) the report is held to the records and never repeats the roster
(FlowTests); (11) the next game's briefing reads the unchanged record (FlowTests);
(12) no earlier page is rewritten (FlowTests). A Thursday game after a bye gives
the Wednesday-to-Saturday break (ThursdayTests; runtime/practices.py's own tests
hold the rest of the break rules).

Weeks and dates come from the fixtures and the closed records, never from
today's date. Nothing is written to the real repository.
"""
import contextlib
import datetime as dt
import hashlib
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
sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import bye_week, current_job, decision_queue, open_events, practices  # noqa: E402
from runtime.clean_pages import page_errors  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402
from runtime.week_inputs import event_id, receipt_name  # noqa: E402
import support_events as se  # noqa: E402

JAX = "Jacksonville Jaguars"
SEASON = se.SEASON
IGNORED = (".git", ".sim_cache", "__pycache__", ".pytest_cache")
WEEK_BOUND = ("defensive_calls", "defensive_call_stats", "decision_policies")
BYE = bye_week.byes(SEASON, ROOT)[0]


def quiet(call, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()) as out:
        result = call(*args, **kwargs)
    return result, out.getvalue()


def relabel(value, names):
    if isinstance(value, dict):
        return {relabel(k, names): relabel(v, names) for k, v in value.items()}
    if isinstance(value, list):
        return [relabel(v, names) for v in value]
    if isinstance(value, str):
        return names.get(value, value)
    return value


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def move(receipt, before, after):
    """A closed game's receipt relabelled onto another fixture: the clubs renamed, the week and the
    event its new fixture's (a fake result, for the copy only)."""
    if JAX in (before["away"], before["home"]):
        other = before["home"] if before["away"] == JAX else before["away"]
        names = {other: after["home"] if after["away"] == JAX else after["away"]}
    else:
        names = {before["away"]: after["away"], before["home"]: after["home"]}
    receipt = relabel(receipt, names)
    for key in WEEK_BOUND:
        receipt.pop(key, None)
    receipt.update({"week": int(after["week"]), "away": after["away"], "home": after["home"],
                    "matchup": "%s at %s" % (after["away"], after["home"]), "event_id": event_id(after, season=SEASON)})
    return receipt


class ByeCopy(unittest.TestCase):
    """A temporary copy at the evening of the club's game before the bye."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT.parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(*IGNORED), symlinks=True)
        self.paths = SeasonPaths(SEASON, self.root)
        self.ours = {int(g["week"]): g for g in open_events.club_fixtures(SEASON, self.root)}
        self.before, self.after = bye_week.around(SEASON, BYE, self.root)
        self.first, self.last = bye_week.dates(SEASON, BYE, self.root)
        closed = [w for w in sorted(self.ours) if (self.paths.receipts / receipt_name(self.ours[w])).is_file()]
        self.closed = closed
        # Close every Jacksonville game before the bye from the closed ones, in turn.
        for n, week in enumerate(w for w in sorted(self.ours) if w < BYE and w not in closed):
            source = self.ours[closed[n % len(closed)]]
            receipt = json.loads((self.paths.receipts / receipt_name(source)).read_text(encoding="utf-8"))
            moved = move(receipt, source, self.ours[week])
            (self.paths.receipts / receipt_name(self.ours[week])).write_text(json.dumps(moved, indent=1),
                                                                            encoding="utf-8")
            self.record_week(week)
        last = self.before
        played = dt.date.fromisoformat(last["date"])
        se.set_clock(self.root, "%s, after the Week %d game against %s (a test record)" % (
            se.long_date(played), int(last["week"]), last["away"].rsplit(" ", 1)[0]))

    def record_week(self, week):
        """The week's practice record as the standing instruction sets it (a recorded week, test data)."""
        rule = current_job.practice_instruction(current_job.load(self.root), SEASON)
        try:
            schedule = practices.schedule_from_instruction(rule, SEASON, week, self.root)
        except practices.NotCovered:
            return
        sessions = [dict(s, status="held", pad_exceptions=[], participation_recorded=False, participation=[])
                    for s in schedule["sessions"]]
        record = {"schema": practices.SCHEMA, "season": SEASON, "week": week, "kind": "game", "basis": "recorded",
                  "schedule": {"source": schedule["source"], "sha256": schedule["sha256"]},
                  "source": {"page": self.paths.week_folder(week).joinpath("README.md").relative_to(self.root)
                             .as_posix()},
                  "sessions": sessions, "days_off": schedule["days_off"], "gaps": ["A test week"]}
        practices.write(record, self.root)

    def bye(self):
        from scripts import render_bye_week
        return render_bye_week.Bye(self.root, BYE)

    def write_pages(self):
        from scripts import render_bye_week
        return quiet(render_bye_week.write, self.root)[0]

    def adjustments(self, **over):
        """My Adjustments, answered: the given lines replacing the defaults (by label)."""
        bye = self.bye()
        from scripts import render_bye_week
        entries = render_bye_week.issues(bye)
        latest = render_bye_week.label_of(render_bye_week.issue_of(entries[-1]))
        answers = {
            "Briefing answered": latest,
            "Current approach": "Carry current approved instructions, with the explicit changes below",
            "Keep": "Current system unchanged", "Highest-priority correction": "No specific change",
            "What I will not add": "No additional restriction", "How I will know if a change is ready": "No new evaluation",
            "offense Direction": "No change", "defense Direction": "No change",
            "Why": "Nothing on the closed games calls for it.", "Who owns the work": "No new owner",
            "What must be shown before it is used more": "No new requirement", "Fallback": "Carry current menu",
            "What must be checked": "No new evaluation", "Direction to Westhoff": "No change",
            "Reason": "None", "Evaluation": "No new evaluation", "Actual eligible role/depth decisions": "No change",
            "If the medical staff does not clear a player": "Bring me a new briefing",
            "Any recommendation to Caldwell": "No recommendation", "Development/evaluation opportunities": "None",
            "Mandatory consecutive player days off": "%s to %s" % (bye_week.long_day(self.window()[0]),
                                                                    bye_week.long_day(self.window()[1])),
            "Staff self-scout work": "Every closed game through the last one, the coordinators",
            "Permitted player work before/after rest": "No on-field player work during the bye",
            "What we will actually test": "No new test", "What work is removed to make room": "None",
            "Medical limits": "Follow every current staff instruction",
            "Durable coaching changes I am making now": "None",
            "Ideas for the next opponent, not yet a frozen game plan": "No change",
            "Instructions that stay in force": "Every standing instruction", "Open issues that still require my answer": "None",
            "I have finished the bye-week decisions": "Yes"}
        answers.update(over)
        page = render_bye_week.adjustments_page(bye)
        out, section = [], None
        for line in page.split("\n"):
            if line.startswith("## "):
                section = line[3:].split(". ", 1)[-1].lower()
            m = re.match(r"^\*\*([^*]+):\*\*\s*$", line.rstrip())
            if m:
                key = "%s %s" % (section, m[1]) if m[1] == "Direction" else m[1]
                if key in answers:
                    line = "**%s:** %s%s" % (m[1], answers[key], "  " if line.endswith("  ") else "")
            out.append(line)
        text = "\n".join(out)
        bye.pages.adjustments.write_text(text, encoding="utf-8")
        return text

    def window(self):
        return practices.bye_break_windows(SEASON, BYE, self.root)[0]

    def check(self):
        from scripts import check_bye_adjustments
        return check_bye_adjustments.check(self.root, SEASON, BYE)

    def holds(self, kind):
        return decision_queue.blocking_errors([decision_queue.event(kind, SEASON, BYE)], self.root)


class OpenTests(ByeCopy):
    def test_the_bye_opens_with_its_review_and_the_next_week_waits(self):
        from scripts import open_game_week, render_bye_week, render_game_week
        state = (self.root / se.STATE).read_bytes()
        self.assertEqual(bye_week.active_bye(self.paths, self.root), BYE)
        written = self.write_pages()
        bye = self.bye()
        for page in (bye.pages.review, bye.pages.adjustments, bye.pages.readme, bye.pages.briefings):
            self.assertIn(page, [Path(p) for p in written])
        # Opening a page moves no time and plays no game.
        self.assertEqual((self.root / se.STATE).read_bytes(), state)
        self.assertFalse(any(JAX in json.loads(p.read_text(encoding="utf-8")).get("matchup", "")
                             for p in self.paths.receipts.glob("week_%02d_*.json" % BYE)))
        # The next game's briefing and items wait for the bye's close.
        wk = render_game_week.Week(self.root)
        self.assertEqual((wk.game, wk.period), (None, {"bye": BYE}))
        self.assertEqual(quiet(render_game_week.write, self.root)[0], [])
        nxt = render_game_week.decisions.week_pages(SEASON, int(self.after["week"]), self.root)
        self.assertFalse(nxt.briefing.exists())
        self.assertEqual(open_game_week.missing(self.root)[0], [])
        queue = decision_queue.load(self.root)
        mine = [i for i in queue["items"] if any(b.get("week") in (BYE, int(self.after["week"]))
                                                 for b in i.get("blocks") or ())]
        self.assertEqual([(i["class"], i["status"], i["blocks"]) for i in mine],
                         [("bye_adjustments", "OPEN", [decision_queue.event("bye_close", SEASON, BYE)])])
        self.assertIsNone(mine[0]["deadline"])
        # The bye's answer holds only the bye's own close: the week's slate builds and closes meanwhile.
        self.assertEqual(self.holds("week_inputs"), [])
        self.assertEqual(self.holds("week_close"), [])
        self.assertTrue(any(mine[0]["id"] in line for line in self.holds("bye_close")))
        # The review: the template's sections, from stored facts as of its issue; the staff's parts to come.
        page = bye.pages.review.read_text(encoding="utf-8")
        self.assertEqual(page_errors(bye.rel(bye.pages.review), page, root=self.root), [])
        for heading in ("## The club entering the bye", "## Offensive self-scout", "## Defensive self-scout",
                        "## Special-teams self-scout", "## Players and medical instructions",
                        "## Calendar and available coaching work", "## Coaching decisions recommended to Stone",
                        "## Staff assessment"):
            self.assertIn(heading, page)
        record = bye_week.record_words(SEASON, BYE, self.root)
        self.assertIn("| Current record, division position | %s." % record, page)
        self.assertIn(bye.game_words(self.after), page)
        self.assertIn("%s to %s" % (bye_week.long_day(self.window()[0]), bye_week.long_day(self.window()[1])), page)
        self.assertIn("To come.", page)
        self.assertNotIn("## ACTION REQUIRED", page)
        # Its issue record, and the pages' check.
        entries = render_bye_week.issues(bye)
        self.assertEqual([(e["file"], e["reason"]) for e in entries], [(bye.pages.review.name, None)])
        self.assertEqual(render_bye_week.check(self.root), [])
        self.assertEqual(quiet(render_bye_week.write, self.root)[0], [])
        # A Week of the league elsewhere cannot change the issued review: it is rebuilt as of its issue.
        thursday = next(g for g in self.paths.regular_games() if int(g["week"]) == BYE)
        source = next(g for g in self.paths.regular_games() if int(g["week"]) == self.closed[0]
                      and JAX not in (g["away"], g["home"]))
        receipt = json.loads((self.paths.receipts / receipt_name(source)).read_text(encoding="utf-8"))
        (self.paths.receipts / receipt_name(thursday)).write_text(json.dumps(move(receipt, source, thursday)),
                                                                  encoding="utf-8")
        day = dt.date.fromisoformat(thursday["date"]) + dt.timedelta(days=1)
        se.set_clock(self.root, "%s, after the 9 a.m. ET record of the Week %d bye (a test record)" % (
            se.long_date(day), BYE))
        self.assertIsNone(render_bye_week.reissue_reason(self.bye()))

    def test_my_adjustments_is_checked_in_the_designs_messages(self):
        self.write_pages()
        self.adjustments()
        problems, notes, compiled = self.check()
        self.assertEqual(problems, [])
        # No change is a full answer; the same decisions in other words compile to the same bytes.
        self.adjustments(**{"offense Direction": "Keep \"Doubles Stick\"; test \"Trips\"",
                            "Highest-priority correction": "No specific change."})
        one = bye_week.compiled_bytes(self.check()[2])
        self.adjustments(**{"offense Direction": "We test \"Trips\"; we will keep \"Doubles Stick\".",
                            "Highest-priority correction": "no specific change"})
        two = bye_week.compiled_bytes(self.check()[2])
        self.assertEqual(one, two)
        parts = json.loads(one)["areas"]["offense"]["parts"]
        self.assertEqual([(p["kind"], p["calls"]) for p in parts], [("keep", ["Doubles Stick"]), ("test", ["Trips"])])
        self.assertTrue(json.loads(one)["areas"]["defense"]["no_change"])
        # Required player film inside the break, on its Saturday, fails with the design's message.
        saturday = self.window()[1] - dt.timedelta(days=1)
        self.adjustments(**{"Permitted player work before/after rest": "%s: film" % saturday.strftime("%A")})
        problems = self.check()[0]
        self.assertIn("You scheduled required player film work on %s, inside the four-day player break. Move it before "
                      "the break or make it staff-only." % practices.long_day(saturday), problems)
        # Pads with none left of the first eleven weeks' eleven, and with the count unknown, fail.
        monday = self.first
        self.adjustments(**{"Permitted player work before/after rest":
                            "%s: practice in helmets and shoulder pads" % monday.strftime("%A")})
        status = practices.padded_status(SEASON, BYE - 1, self.root)
        self.assertEqual(status["first"]["left"], 0)
        problems = self.check()[0]
        self.assertIn("This practice requests pads but the earlier recorded practices have used the season's available "
                      "first-eleven-week allocation. Choose helmets-only work or no field period.", problems)
        unknown = max(w for w in practices.records(SEASON, self.root) if w < BYE)
        practices.path(SEASON, unknown, self.root).unlink()
        problems = self.check()[0]
        self.assertTrue(any("not all on record" in p for p in problems), problems)
        self.record_week(unknown)
        # A medical clearance assumed, a transaction ordered, an install claimed, a name off the roster,
        # a call outside the active books, an unanswered line and an unfinished page are each refused.
        cases = [({"Medical limits": "Lowery is now cleared for full work"}, "no medical clearance is assumed"),
                 ({"Any recommendation to Caldwell": "Sign a linebacker today"}, "this page orders none"),
                 ({"defense Direction": "Keep the installed Cover 9 rotation"}, "'installed'"),
                 ({"Staff self-scout work": "Joe Nobody reviews the film"}, "Joe Nobody is not on the roster"),
                 ({"offense Direction": "Test \"Zebra Rocket\""}, "is not a call or term of the active playbooks"),
                 ({"Fallback": ""}, "unanswered"),
                 ({"I have finished the bye-week decisions": "No"}, "applied once every decision is explicit")]
        for over, words in cases:
            with self.subTest(words=words):
                self.adjustments(**over)
                problems = self.check()[0]
                self.assertTrue(any(words in p for p in problems), problems)
        # A recommendation is recorded as his and noted, never ordered.
        self.adjustments(**{"Any recommendation to Caldwell": "Recommend a review of the linebacker depth"})
        problems, notes, compiled = self.check()
        self.assertEqual(problems, [])
        self.assertTrue(any("recorded as your recommendation" in n for n in notes))


class FlowTests(ByeCopy):
    def test_the_bye_runs_from_its_review_to_its_close(self):
        from scripts import (apply_bye_adjustments, close_bye_week, open_game_week, record_practice_week,
                             render_bye_week, render_game_week)
        self.write_pages()
        bye = self.bye()
        record_before = bye_week.record_words(SEASON, BYE, self.root)
        earlier_byes = {p: digest(p) for p in SeasonPaths(SEASON - 1, ROOT).week_folder(1).parent.glob("*bye*/*.md")}
        # A test result resolved in the bye, then a dated medical entry that changes the review's own
        # sections while the bye's answer is open: the review is issued again, with the result under FOR
        # YOUR INFORMATION, the earlier issue kept as he saw it.
        se.set_clock(self.root, "%s, after the 10 a.m. ET record of the Week %d bye (a test record)" % (
            se.long_date(self.first), BYE))
        source = se.source_page(self.root, "head_coach_change")
        when = open_events.et(self.first, 9)
        news = {"schema": open_events.SCHEMA, "id": "%s-test-coach-change" % self.first.isoformat(),
                "kind": "head_coach_change", "season": SEASON, "subject": "Test Club",
                "raised": {"at": open_events.iso(when), "by": "communications_staff", "source": {"path": source}},
                "known_to": ["stone"], "authority": {"rows": ["1"], "decides": open_events.OTHER_CLUB},
                "stone_part": "none", "summary": {"text": "A test change of head coach at another club.",
                                                  "author": "Team communications staff",
                                                  "date": self.first.isoformat()},
                "facts": [], "options": [], "deadline": None, "state": "open", "process": []}
        open_events.raise_event(news, self.root)
        result = se.result_page(self.root, news, "Head_Coach_Change_test.md", self.first)
        open_events.resolve(SEASON, news["id"], {
            "at": open_events.iso(when), "outcome": "executed", "by": open_events.OTHER_CLUB,
            "decision": {"text": "The club named an interim head coach from its staff.",
                         "author": "Team communications staff", "date": self.first.isoformat(), "criteria": None},
            "result_page": result}, self.root)
        self.assertEqual(open_events.get(SEASON, news["id"], self.root)["resolution"]["period"], {"bye": BYE})
        self.assertIsNone(render_bye_week.reissue_reason(self.bye()))     # news alone waits for the next issue
        self.assertTrue(any("closes on its Sunday" in r for r in close_bye_week.refusals(self.root, SEASON, BYE)))
        roster = json.loads(self.paths.roster.read_text(encoding="utf-8"))
        cleared = next(r for r in roster["players"] if r.get("list") == "active"
                       and not (r.get("availability") or "").startswith("No communicated restriction"))
        cleared["availability"] = "No communicated restriction"
        self.paths.roster.write_text(json.dumps(roster, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        self.assertTrue(render_bye_week.reissue_reason(self.bye()).startswith("b:"))
        self.write_pages()
        entries = render_bye_week.issues(self.bye())
        self.assertEqual(len(entries), 2)
        self.assertTrue((bye.pages.folder / entries[0]["file"]).is_file())
        review = bye.pages.review.read_text(encoding="utf-8")
        self.assertIn("## FOR YOUR INFORMATION", review)
        self.assertIn("Test Club changes its head coach", review)
        self.assertIn("Head_Coach_Change_test.md", bye.pages.readme.read_text(encoding="utf-8"))
        # His adjustments: no change on offense and special teams, a correction on defense, an immediate
        # depth change, the work before the break and the break.
        chart = json.loads(self.paths.depth_chart.read_text(encoding="utf-8"))
        order = list(reversed(chart["depth"]["LB"]))
        start, end = self.window()
        work = "; ".join("%s: practice in helmets" % (self.first + dt.timedelta(days=n)).strftime("%A")
                         for n in range((start - self.first).days))
        self.adjustments(**{"defense Direction": "Correct the run fits against twelve personnel",
                            "Actual eligible role/depth decisions": "Linebackers order: %s" % ", ".join(order),
                            "Permitted player work before/after rest": work or "No on-field player work during the bye"})
        self.assertEqual(self.check()[0], [])
        # Not yet applied: the bye cannot close, and no session of the bye can be recorded.
        self.assertTrue(close_bye_week.refusals(self.root, SEASON, BYE))
        held = self.root / "held.json"
        held.write_text(json.dumps({"source": {"page": bye.rel(bye.pages.readme)}, "sessions": [], "days_off": []}),
                        encoding="utf-8")
        problems, _, _ = record_practice_week.record(self.root, SEASON, BYE, held)
        self.assertTrue(problems and "not applied yet" in problems[0], problems)
        # Applied: the record, the item settled by him, the depth change through the chart writers.
        problems, notes, written = apply_bye_adjustments.apply(self.root, SEASON, BYE)
        self.assertEqual(problems, [])
        applied = bye_week.applied_record(SEASON, BYE, self.root)
        self.assertEqual(applied["page_sha256"], bye_week.page_sha256(bye.pages.adjustments.read_text(encoding="utf-8")))
        item = bye_week.bye_item(decision_queue.load(self.root), SEASON, BYE)
        self.assertEqual((item["status"], item["resolution"]["by"]), ("RESOLVED", "user"))
        self.assertEqual(self.holds("bye_close"), [])
        self.assertEqual(json.loads(self.paths.depth_chart.read_text(encoding="utf-8"))["depth"]["LB"], order)
        log = json.loads(self.paths.record("team/depth_chart/update_log.json").read_text(encoding="utf-8"))
        self.assertIn("My Adjustments", log["entries"][-1]["sources"][0]["label"])
        self.assertEqual(apply_bye_adjustments.apply(self.root, SEASON, BYE)[2], [])
        self.assertEqual(bye_week.validation_errors(self.root), [])
        # The bye's practice and rest record, against the applied schedule, with its legal break.
        schedule, _ = record_practice_week.applied_schedule(self.root, SEASON, BYE)
        se.set_clock(self.root, "%s, after the 9 a.m. ET record of the Week %d bye (a test record)" % (
            se.long_date(self.last), BYE))
        held.write_text(json.dumps({"source": {"page": bye.rel(bye.pages.readme)},
                                    "sessions": [dict(s, participation_recorded=False) for s in schedule["sessions"]],
                                    "days_off": schedule["days_off"],
                                    "gaps": ["Participation was not recorded session by session"]}), encoding="utf-8")
        problems, _, path = record_practice_week.record(self.root, SEASON, BYE, held)
        self.assertEqual(problems, [])
        log_record = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual((log_record["kind"], log_record["schedule"]["sha256"]), ("bye", schedule["sha256"]))
        # The league's other games of the week close while nothing of the bye holds them.
        self.assertEqual(self.holds("week_close"), [])
        problems = close_bye_week.refusals(self.root, SEASON, BYE)
        self.assertTrue(any("slate has not closed" in p for p in problems), problems)
        donors = [g for g in self.paths.regular_games() if int(g["week"]) == self.closed[0]
                  and JAX not in (g["away"], g["home"])]
        for donor, game in zip(donors, [g for g in self.paths.regular_games() if int(g["week"]) == BYE]):
            receipt = json.loads((self.paths.receipts / receipt_name(donor)).read_text(encoding="utf-8"))
            (self.paths.receipts / receipt_name(game)).write_text(json.dumps(move(receipt, donor, game)),
                                                                  encoding="utf-8")
        # The staff's report, held to the records: a box score, a wrong record or a pasted result is refused.
        problems = close_bye_week.refusals(self.root, SEASON, BYE)
        self.assertTrue(any("the report is not written" in p for p in problems), problems)
        frame = render_bye_week.report_frame(self.bye())
        report = frame.replace("To come.", "No additional adjustment was adopted.")
        report = report.replace("| No additional adjustment was adopted. | No additional adjustment was adopted. |",
                                "| Not yet performed | The next game week's film |")
        report = report.replace("## 5. League context and the next opponent\n\nNo additional adjustment was adopted.",
                                "## 5. League context and the next opponent\n\n**Jacksonville:** No game this week; "
                                "record unchanged. The other business of the week: [the change at Test Club](%s)."
                                % "../../../League/Coaching_Changes/Head_Coach_Change_test.md")
        bye.pages.report.write_text(report, encoding="utf-8")
        self.assertEqual(bye_week.report_errors(SEASON, BYE, self.root), [])
        for bad, words in ((report + "\n## Box score\n", "no box score"),
                           (frame, "is not written yet"),
                           (report.replace("%s through" % record_before, "7-4 through"), "the record line"),
                           (report.replace("[the change at Test Club]", "the change at Test Club ["), "not linked")):
            with self.subTest(words=words):
                bye.pages.report.write_text(bad, encoding="utf-8")
                self.assertTrue(any(words in e for e in bye_week.report_errors(SEASON, BYE, self.root)),
                                bye_week.report_errors(SEASON, BYE, self.root))
        bye.pages.report.write_text(report, encoding="utf-8")
        # It closes on its Sunday: the close line written, the record unchanged, no Jacksonville game.
        self.assertEqual(close_bye_week.refusals(self.root, SEASON, BYE), [])
        problems, written = close_bye_week.close(self.root, SEASON, BYE)
        self.assertEqual(problems, [])
        self.assertTrue(bye_week.bye_closed(self.paths, self.root, BYE))
        self.assertIsNone(bye_week.active_bye(self.paths, self.root))
        from runtime.events import annual_record_path
        record = annual_record_path(self.root, SEASON).read_text(encoding="utf-8")
        self.assertIn("Week %d bye" % BYE, record)
        self.assertEqual(bye_week.record_words(SEASON, BYE, self.root), record_before)
        self.assertFalse(any(JAX in json.loads(p.read_text(encoding="utf-8")).get("matchup", "")
                             for p in self.paths.receipts.glob("week_%02d_*.json" % BYE)))
        self.assertEqual(close_bye_week.refusals(self.root, SEASON, BYE)[0][:22], "The Week %d bye has cl" % BYE)
        self.assertEqual(bye_week.validation_errors(self.root), [])
        self.assertEqual(render_bye_week.check(self.root), [])
        # The next game week opens, its first notices counted from the bye's last review: the bye's result
        # is on neither its index nor its first briefing.
        wk = render_game_week.Week(self.root)
        self.assertEqual(int(wk.game["week"]), int(self.after["week"]))
        self.assertTrue(open_game_week.missing(self.root)[0])
        quiet(render_game_week.write, self.root)
        nxt = render_game_week.decisions.week_pages(SEASON, int(self.after["week"]), self.root)
        self.assertTrue(nxt.briefing.is_file())
        self.assertNotIn("Test Club", nxt.readme.read_text(encoding="utf-8"))
        brief = nxt.briefing.read_text(encoding="utf-8")
        self.assertNotIn("Test Club", brief)
        self.assertIn("Jacksonville %s" % record_before, brief)         # the record the bye left unchanged
        # The earlier season's bye pages are untouched.
        self.assertEqual({p: digest(p) for p in earlier_byes}, earlier_byes)


class ResponsesIndexTests(ByeCopy):
    def test_the_index_says_whether_my_responses_waits_on_him(self):
        """The bye's My Responses row is waiting on him while a question of an event raised in the bye
        is open, and no longer once it is settled (rehearsal r5: it said "Open" for good)."""
        from scripts import raise_event, render_bye_week
        self.write_pages()
        se.set_clock(self.root, "%s, after the 10 a.m. ET record of the Week %d bye (a test record)" % (
            se.long_date(self.first), BYE))
        record = se.injury_replacement(self.root, "test-roster-question", open_events.et(self.first, 9), self.after,
                                       short=False)
        upload = self.root.parent / "test_roster_question.json"
        upload.write_text(json.dumps(record), encoding="utf-8")
        self.assertEqual(quiet(raise_event.main, ["--season", str(SEASON), "--file", str(upload),
                                                  "--root", str(self.root)])[0], 0)
        self.write_pages()
        bye = self.bye()
        self.assertTrue(bye.pages.responses.is_file())
        row = lambda: next(l for l in bye.pages.readme.read_text(encoding="utf-8").splitlines()
                           if l.startswith("| [My Responses]"))
        self.assertTrue(row().endswith("| Waiting on you |"), row())
        item = open_events.get(SEASON, record["id"], self.root)["queue_item"]
        se.settle(self.root, item, "RESOLVED", {"date": self.first.isoformat(), "by": "user",
                                                "summary": "Answered on My Responses (test data)."})
        render_bye_week.write_index(self.root)
        self.assertTrue(row().endswith("| No answer waiting |"), row())
        self.assertEqual(render_bye_week.check(self.root), [])


class OpeningTests(ByeCopy):
    def test_the_week_6_to_10_openings_are_unchanged_apart_from_the_practice_item(self):
        import unittest.mock
        from scripts import open_game_week
        from scripts.render_game_week import Week
        weeks = [w for w in sorted(self.ours) if w < BYE and w >= practices.log_start(SEASON, ROOT)]
        for week in weeks:
            with self.subTest(week=week):
                wk = Week(self.root, week)
                self.assertEqual([i["class"] for i in open_game_week.items_for(self.root, wk)],
                                 [open_game_week.PLAN, open_game_week.INACTIVES])
                with unittest.mock.patch.object(current_job, "practice_instruction", return_value=None):
                    self.assertEqual([i["class"] for i in open_game_week.items_for(self.root, wk)],
                                     [open_game_week.PLAN, open_game_week.INACTIVES, open_game_week.PRACTICE])


class ThursdayTests(unittest.TestCase):
    def test_a_thursday_game_after_the_bye_gives_wednesday_to_saturday(self):
        games = [dict(g) for g in practices.fixtures(SEASON, ROOT)]
        _, after = bye_week.around(SEASON, BYE, ROOT)
        game = next(g for g in games if g["game_id"] == after["game_id"])
        thursday = dt.date.fromisoformat(game["date"]) - dt.timedelta(days=3)
        game.update(date=thursday.isoformat(), weekday="Thursday")
        (start, end), = practices.bye_break_windows(SEASON, BYE, ROOT, games)
        self.assertEqual((start.strftime("%A"), end.strftime("%A")), ("Wednesday", "Saturday"))


if __name__ == "__main__":
    unittest.main()
