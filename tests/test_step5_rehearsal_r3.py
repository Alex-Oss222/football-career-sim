"""Rebuild step 5, acceptance test 3: the synthetic week rehearsal, run on the open week as it stands.

Everything happens in a throwaway copy of the checkout, every event in it is test data (its summary
and source page say so), the draws go through tests/local_private_service.py, and the real
repository is only read. The week and every date come from the fixtures, the receipts, the queue and
Document 5: the open week is the first Jacksonville game without a receipt, its Tuesday is five days
before its game, the week before it is the last closed one. The runner's commits are rehearsed in
order, each followed by the page rebuild, repository validation (the clean-page check among it), the
game readiness check and the career-layer isolation test:

1. the head-coach check, run once after the week before the open week closed and before the open
   week's practice week: the retroactive weeks first, every club that played drawn by the adopted
   method (its rate table zeroed in the copy except one cell of the coaches who are not in
   Jacksonville's coach's season, so Jacksonville can never change and the result never depends on
   the draw), a club's draws stopping at its first change, a change for a week behind the club's
   latest closed game effective the day after that game, and a second run refused;
2. the practice week from Stone's standing instruction, checked before any session, a second padded
   day in the week refused;
3. on the Tuesday, a mid-week record: a trade call due Wednesday at 4 p.m. ET reissues the brief
   with ACTION REQUIRED (the old copy kept) and opens a My Responses block; Caldwell's criteria are
   recorded; Stone opposes it; Caldwell declines it; one Trade Result page is readable that day,
   linked from the week index and listed in Record.md; the week's holds never move;
4. a second club calls the same day and withdraws on the Wednesday before Stone answers: his item is
   withdrawn by the organization, one Trade Result records the withdrawal, and its notice shows under
   FOR YOUR INFORMATION in exactly one issue, the first issued after it;
5. Stone's Game Plan written against the latest issue, complete but not set while its exams are
   still to come;
6. the practice-week commit at game day: the exams' medical entries, the practice record (the
   season's padded count moving by the week's one padded practice), the Game Report opened and its
   pregame sections frozen; the brief reissued because the entries changed its own sections, its
   "Briefing used" re-dated, and the Game Plan applied after the exams;
7. the game closed by relabelling the week before it onto it (tests/test_week_close_pages.py) with
   a long-term Jacksonville injury: one injury replacement event with legal options and no grade,
   Caldwell's criteria first; the week's awards and its head-coach check (a second run refused);
   the next week opened;
8. Stone recommends a practice-squad promotion, Caldwell decides it and apply_transaction.py executes
   it: one Transaction page; the roster, contract record, contract inputs, player record, chart and
   its log agree; the rails' control and the exclusivity gate pass and the next week's inputs build;
9. COMING UP: each eligibility window on the roster record shows until its date, the trading
   deadline only under COMING UP and only in the briefs it belongs to, and once it passes nothing
   shows and no hold, page or question exists.

A second test removes the standing practice instruction in another copy: the open week asks its
practice schedule on My Responses (one item holding nothing and a blank block, the brief reissued
for its section 8), two padded days are refused when the answer is checked, one is set.
"""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import unittest
from datetime import date, timedelta
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "scripts"))

from runtime import (clean_pages, current_job, deadlines, decision_queue, decisions, event_inserts,  # noqa: E402
                     game_plan, game_report, game_weeks, league_coaches as lc, open_events, people, player_bios,
                     player_contracts, practices, rails, responses, season_summary, transactions as tx,
                     week_pages as wpages)
from runtime import events as ev_mod  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402
from scripts import (apply_game_plan, apply_responses, apply_transaction, check_game_plan,  # noqa: E402
                     check_responses, coaching_check, freeze_pregame, injury_events, league_awards, raise_event,
                     rebuild_pages, record_practice_week as rpw, render_club_pages, render_contract_pages,
                     render_game_week, resolve_event, season_handoff)
from check_game_readiness import assess  # noqa: E402
import support_events as se  # noqa: E402
import support_roster_moves as srm  # noqa: E402
from local_private_service import local_service  # noqa: E402
from test_game_plan import needed_inactives, role_cover  # noqa: E402
from test_game_report import template_report  # noqa: E402
from test_injury_replacement import GATE  # noqa: E402

SEASON = se.SEASON
CLUB = se.CLUB
TEST = "a test record"
GRADE = re.compile(r"/\s*10\b|\bgrad(?:e|es|ed|ing)\b|\brat(?:ed|ing)\b", re.I)
STATE = "state/05_Current_Season_State.md"
# The real records the rehearsal only reads: each must keep its bytes.
WATCHED = ("state/05_Current_Season_State.md", "state/04_Roster_and_Staff_Register.md", "state/decision_queue.json",
           "state/current_job.json")


def quiet(call, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()) as out:
        result = call(*args, **kwargs)
    return result, out.getvalue()


def tree_digest(root, rels):
    out = {}
    for rel in rels:
        path = Path(root) / rel
        files = sorted(p for p in path.rglob("*") if p.is_file()) if path.is_dir() else [path] if path.is_file() else []
        for p in files:
            out[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def real_watch():
    paths = SeasonPaths(SEASON, ROOT)
    rels = list(WATCHED) + [paths.receipts.relative_to(ROOT).as_posix()]
    rels += [f.relative_to(ROOT).as_posix() for f in open_events.stores(SEASON, ROOT)]
    rels += [lc.data_folder(SEASON, ROOT).relative_to(ROOT).as_posix(), lc.folder(SEASON, ROOT).relative_to(ROOT).as_posix()]
    game = se.open_game(ROOT)
    if game is not None:
        pages = decisions.week_pages(SEASON, int(game["week"]), ROOT)
        rels += [pages.folder.relative_to(ROOT).as_posix(), pages.data.relative_to(ROOT).as_posix()]
    return tree_digest(ROOT, rels)


class Runner(unittest.TestCase):
    """The runner's steps on a copy of the checkout, with the checks of every commit point."""

    def setUp(self):
        self.real = real_watch()
        self.root = srm.copy_repo(self)
        for record in self.root.glob("career/**/paused_game.json"):
            record.unlink()
        self.paths = SeasonPaths(SEASON, self.root)
        self.game = se.open_game(self.root)
        if self.game is None:
            self.skipTest("every regular-season game has closed")
        self.week = int(self.game["week"])
        self.period = {"week": self.week}
        self.pages = decisions.week_pages(SEASON, self.week, self.root)
        self.tuesday = se.tuesday_before(self.game)
        self.wednesday = self.tuesday + timedelta(days=1)
        self.game_day = date.fromisoformat(self.game["date"])
        self.commits = []

    def tearDown(self):
        # Isolation: nothing reached the real repository.
        self.assertEqual(real_watch(), self.real)

    # ------------------------------------------------------------------ the runner's tools
    def at(self, day, hour, minute=0):
        return open_events.et(day, hour, minute)

    def clock(self, day, hour, minute=0):
        """A mid-week record at ``hour``:``minute`` ET, with the head-coach changes the clock reaches."""
        se.midweek(self.root, day, hour, minute, self.open_week())
        code, _ = quiet(coaching_check.main, ["--season", str(SEASON), "--effective"], root=self.root, out=print)
        self.assertEqual(code, 0)

    def open_week(self):
        return int(se.open_game(self.root)["week"])

    def checkpoint(self, value=None):
        """Document 5's checkpoint moved to the latest closed event line (or ``value``)."""
        value = value or ev_mod.closures(ev_mod.load_events(self.root))[-1][2]["checkpoint"]
        path = self.root / STATE
        text, n = re.subn(r"^(\*\*Global package checkpoint:\*\* `)[^`]+(`)", r"\g<1>%s\g<2>" % value,
                          path.read_text(encoding="utf-8"), count=1, flags=re.M)
        self.assertEqual(n, 1)
        path.write_text(text, encoding="utf-8")

    def commit(self, label, check=False):
        """A commit point: every built page rebuilt, then validation (the clean-page check among it),
        the game readiness check (the private service's probe aside: a copy is never bound to it) and
        the career-layer isolation test."""
        _, problems = rebuild_pages.rebuild(self.root, SEASON)
        self.assertEqual(problems, [], label)
        if check:
            self.assertEqual(rebuild_pages.rebuild(self.root, SEASON, check=True), ([], []), label)
        blockers = ["%s: %s" % (b["label"], b["detail"]) for b in assess(self.root, SEASON)["blockers"]
                    if b["id"] != "private_probe"]
        self.assertEqual(blockers, [], label)
        done = subprocess.run([sys.executable, "-m", "unittest", "-q", "test_career_layer_isolation"],
                              cwd=str(ROOT / "tests"), capture_output=True, text=True,
                              env=dict(os.environ, PYTHONPATH=str(ROOT)))
        self.assertEqual(done.returncode, 0, done.stderr[-2000:])
        self.commits.append(label)

    def issues(self, week):
        wk = render_game_week.Week(self.root, week)
        return render_game_week.issues(wk) if wk.pages.data.joinpath("briefings.json").is_file() else []

    def reissue(self, expect):
        """The open week's brief issued again for ``expect`` ("a" or "b"): the old copy kept as issued."""
        wk = render_game_week.Week(self.root)
        reason = render_game_week.reissue_reason(wk)
        self.assertIsNotNone(reason)
        self.assertTrue(reason.startswith(expect + ":"), reason)
        old = wk.pages.briefing.read_bytes()
        before = render_game_week.issues(wk)
        quiet(render_game_week.write, self.root)
        wk = render_game_week.Week(self.root)
        after = render_game_week.issues(wk)
        self.assertEqual(len(after), len(before) + 1)
        self.assertEqual((wk.pages.folder / after[-2]["file"]).read_bytes(), old)
        self.assertEqual(after[-1]["reason"], reason)
        return wk.pages.briefing.read_text(encoding="utf-8"), after[-1]

    def holds(self, week):
        return decision_queue.blocking_errors([decision_queue.event("week_inputs", SEASON, week),
                                               decision_queue.event("week_close", SEASON, week)], self.root)

    def answer(self, event_id, period, words, reason="The depth at the position.", conditions="None."):
        """Stone's answer written in his block on My Responses (test data)."""
        record = responses.record_of(SEASON, period, self.root)
        heading = next(b["heading"] for b in record["blocks"] if b.get("event") == event_id)
        page = responses.pages_of(SEASON, period, self.root).responses
        text = page.read_text(encoding="utf-8")
        block = responses.blocks_of(text)[heading]
        filled = block.text.replace("**My answer:**\n", "**My answer:** %s\n" % words, 1)
        filled = filled.replace("**My football or professional reason:**\n",
                                "**My football or professional reason:** %s\n" % reason, 1)
        filled = filled.replace("**Conditions or instructions:**\n", "**Conditions or instructions:** %s\n" % conditions, 1)
        page.write_text(text.replace(block.text, filled, 1), encoding="utf-8")
        week = str(period["week"])
        self.assertEqual(quiet(check_responses.main, [week, "--season", str(SEASON), "--root", str(self.root)])[0], 0)
        self.assertEqual(quiet(apply_responses.main, [week, "--season", str(SEASON), "--root", str(self.root)])[0], 0)
        return heading

    def resolve(self, event_id, outcome, by, when, decision):
        code, out = quiet(resolve_event.main, [event_id, "--season", str(SEASON), "--outcome", outcome, "--by", by,
                                               "--at", open_events.iso(when), "--decision", decision, "--closure",
                                               "--root", str(self.root)])
        self.assertEqual(code, 0, out)
        self.checkpoint()
        return open_events.get(SEASON, event_id, self.root)

    def raise_call(self, ident, subject, raised, due):
        record = se.trade_call(self.root, ident, raised, due, subject=subject, source=self.call_source)
        record["summary"]["text"] = "A test call from another club about a trade (%s)." % TEST
        path = self.root.parent / ("%s.json" % ident)
        path.write_text(json.dumps(record), encoding="utf-8")
        code, out = quiet(raise_event.main, ["--season", str(SEASON), "--file", str(path), "--root", str(self.root)])
        self.assertEqual(code, 0, out)
        open_events.add_process(SEASON, record["id"], {
            "at": open_events.iso(raised + timedelta(minutes=5)), "kind": "criteria", "by": "caldwell",
            "what": "A test record of the need at the position, the legal options on the date, the contract facts "
                    "and the other club's terms, each on file.", "source": {"path": self.call_source}}, self.root)
        return open_events.get(SEASON, record["id"], self.root)

    def fyi_issues(self, event_id, weeks):
        """[(week, n)]: the issues showing ``event_id`` under FOR YOUR INFORMATION."""
        return [(w, n) for w in weeks for n, e in enumerate(self.issues(w), 1)
                if any(i.get("event") == event_id and i["section"] == "fyi" for i in e.get("inserts") or ())]

    def successor(self, stamp, weeks):
        """The issue after a stamp's issue, in the season's issue order."""
        order = [(w, n) for w in weeks for n in range(1, len(self.issues(w)) + 1)]
        week = stamp["period"]["week"]
        n = next(n for n, e in enumerate(self.issues(week), 1)
                 if e["date"] == stamp["date"] and int(e["revision"]) == stamp["revision"])
        return order[order.index((week, n)) + 1]


class RehearsalTests(Runner):
    def test_the_open_week_rehearsed_from_its_first_record_to_the_next_weeks_roster_move(self):
        self.coaching_check_before_the_practice_week()
        self.practice_schedule_from_the_standing_instruction()
        self.tuesday_trade_calls()
        self.wednesday_withdrawal()
        self.game_plan_against_the_latest_issue()
        self.practice_week_commit()
        self.game_plan_applied_after_the_exams()
        self.close_with_a_long_term_injury()
        self.injury_replacement_by_promotion()
        self.coming_up_windows_and_the_trading_deadline()
        # Every page checked as written, none re-recorded as history.
        self.assertEqual(clean_pages.history(self.root), clean_pages.history(ROOT))
        self.assertEqual(rebuild_pages.rebuild(self.root, SEASON, check=True), ([], []))

    # ------------------------------------------------------------------ 1. the head-coach check
    def coaching_check_before_the_practice_week(self):
        root = self.root
        method = lc.load_method(SEASON, root)
        self.assertTrue(lc.adopted(method))
        previous = max(lc.closed_weeks(SEASON, root))
        self.assertEqual(previous, max(w for w in practices.club_games(SEASON, root) if w < self.week))
        due = lc.due_weeks(SEASON, root, previous)
        if not due:
            return              # the checks through the closed week are on record already
        # Test data: the copy's rate table zeroed but for one cell of the coaches in their other season
        # with the club than Jacksonville's coach, so no draw depends on chance and Jacksonville cannot
        # change; the cell is the one holding the most clubs in the first week due.
        tenures = lc.tenures(method, root)
        mine = tenures[CLUB]
        games = lc.closed_games(SEASON, root)
        first = lc.week_inputs(SEASON, due[0], root, method, lc.checks(SEASON, root), games)
        cells = [lc.cell(r) for r in first["clubs"] if r["tenure"] != mine]
        self.assertTrue(cells, "every club in the first week due is in Jacksonville's coach's season")
        cell = max(sorted(set(cells)), key=cells.count)
        table_file = root / method["table"]["file"]
        table = json.loads(table_file.read_text(encoding="utf-8"))
        for key, row in table["rates"].items():
            row["rate"] = 1.0 if key == cell else 0.0
        table_file.write_text(json.dumps(table, indent=1) + "\n", encoding="utf-8")
        method["table"]["sha256"] = hashlib.sha256(table_file.read_bytes()).hexdigest()
        lc.method_path(SEASON, root).write_text(json.dumps(method, indent=1) + "\n", encoding="utf-8")
        snapshot = hashlib.sha256((root / STATE).read_bytes()).hexdigest()
        store, client = local_service(self, root / "private", "rehearsal-r3-check", snapshot=snapshot)
        lines = []
        self.assertEqual(coaching_check.close(SEASON, previous, root, client, lines.append), 0, lines)
        records = lc.checks(SEASON, root)
        self.assertEqual(sorted(w for w in records if w in due), due)
        # In week order, one private event each, the retroactive weeks first and flagged.
        self.assertEqual([records[w]["order"] for w in due], list(range(records[due[0]]["order"],
                                                                         records[due[0]]["order"] + len(due))))
        retro = [w for w in method["retroactive"]["weeks"] if w in due]
        self.assertEqual([w for w in due if records[w]["retroactive"]], retro)
        with store.connect() as c:
            drawn = [r[0] for r in c.execute("SELECT event_id FROM events ORDER BY rowid")]
        self.assertEqual(drawn, [lc.event_id(SEASON, w) for w in due])
        # Every club that played is drawn or named as not drawn; a club on its bye has no line.
        fixtures = self.paths.regular_games()
        for w in due:
            played = {g[side] for g in fixtures if g["week"] == w for side in ("away", "home")}
            lines_ = [r["club"] for r in records[w]["clubs"]] + [r["club"] for r in records[w]["not_drawn"]]
            self.assertEqual(sorted(lines_), sorted(played), "Week %d" % w)
        self.assertEqual(len({g[s] for g in fixtures for s in ("away", "home")}), 32)
        # A club's draws stop at its first change, which takes effect the day after its latest closed
        # game, the week it was drawn for being behind that game; Jacksonville never changes.
        changes = [(w, r) for w in due for r in records[w]["clubs"] if r["changed"]]
        self.assertTrue(changes)
        self.assertTrue(any(w in retro for w, _ in changes) or not retro)
        for w, row in changes:
            self.assertNotEqual(row["club"], CLUB)
            last = lc.record_after(games[row["club"]], previous)[4]
            self.assertEqual(row["effective"], (date.fromisoformat(last) + timedelta(days=1)).isoformat())
            for later in (x for x in due if x > w and any(g.week == x for g in games[row["club"]])):
                self.assertIn({"club": row["club"], "reason": "changed earlier this season"}, records[later]["not_drawn"])
                self.assertNotIn(row["club"], [r["club"] for r in records[later]["clubs"]])
        self.assertTrue(any(max(g.week for g in games[r["club"]] if g.week <= previous) > w for w, r in changes))
        self.assertIsNone(lc.career_hold(SEASON, root))
        # A second run is refused and draws nothing.
        with self.assertRaises(coaching_check.Refused):
            coaching_check.close(SEASON, previous, root, client, lines.append)
        with store.connect() as c:
            self.assertEqual(c.execute("SELECT COUNT(*) FROM events").fetchone()[0], len(due))
        self.changes = changes
        self.commit("head-coach check")

    # ------------------------------------------------------------------ 2. the practice schedule
    def practice_schedule_from_the_standing_instruction(self):
        root, week = self.root, self.week
        self.assertIsNotNone(current_job.practice_instruction(current_job.load(root), SEASON))
        before = practices.padded_status(SEASON, week - 1, root)["first"]
        status, problems, lines, written = rpw.schedule_command(root, SEASON, week, check=True)
        self.assertEqual((status, problems, written), ("SET", [], []))
        self.assertIn("Padded practices before this week: %d used, %d left of the 11" % (before["used"], before["left"]),
                      lines)
        schedule, why = rpw.cover(root, SEASON, week)
        self.assertIsNotNone(schedule, why)
        self.padded = sum(1 for s in schedule["sessions"] if s["equipment"] == practices.PADDED)
        self.assertLessEqual(self.padded, 1)
        # No practice item opens for a week the standing instruction covers.
        self.assertIsNone(rpw.practice_item(root, SEASON, week))
        # A second padded day in the week is refused when the schedule is checked.
        drills = [s for s in schedule["sessions"] if s["type"] == "practice"][:2]
        doubled = [dict(s, equipment=practices.PADDED) if s in drills else s for s in schedule["sessions"]]
        refused = practices.check_schedule(SEASON, week, doubled, schedule["days_off"], root)
        self.assertTrue(any("second padded practice" in p for p in refused), refused)

    # ------------------------------------------------------------------ 3. the Tuesday calls
    def tuesday_trade_calls(self):
        root, week = self.root, self.week
        held = self.holds(week)
        self.call_source = se.source_page(root, "trade_talks", name="test_trade_call_source.md",
                                          text="# Test trade call\n\nA test record of a trade call from another club, for "
                                               "the rehearsal only.\n")
        # 10 a.m.: the first call, due Wednesday at 4 p.m. ET.
        self.clock(self.tuesday, 10)
        first = self.raise_call("test-trade-call-test-club", "Test Club", self.at(self.tuesday, 9),
                                self.at(self.wednesday, 16))
        page, entry = self.reissue("a")
        self.assertIn("## ACTION REQUIRED\n\n**One decision needs your answer.**", page)
        self.assertIn("**Response due: Wednesday, %s %d, 4 p.m. ET**" % (self.wednesday.strftime("%B"),
                                                                     self.wednesday.day), page)
        self.assertIn("**Why it needs you:** Your football recommendation to David Caldwell; he decides.", page)
        self.assertIn(event_inserts.ONE_RULE, page)
        self.assertNotIn(first["id"], page)
        self.assertIn(("action", first["id"]), [(i["section"], i.get("event")) for i in entry["inserts"]])
        self.assertIn("## %s" % open_events.title(first), self.pages.responses.read_text(encoding="utf-8"))
        # Each head-coach change the clock has reached is news under FOR YOUR INFORMATION here.
        news = [e["id"] for e in lc.stored_news(SEASON, root).values()]
        self.assertEqual(sorted(i["event"] for i in entry["inserts"] if i["section"] == "fyi"), sorted(news))
        item = se.item(root, first["queue_item"])
        self.assertEqual((item["status"], item["blocks"]),
                         ("OPEN", [decision_queue.event("event_resolution", SEASON, event=first["id"])]))
        self.assertEqual(self.holds(week), held)
        self.commit("first trade call")
        # 11 a.m.: a second club calls the same day.
        self.clock(self.tuesday, 11)
        second = self.raise_call("test-trade-call-second-test-club", "Second Test Club", self.at(self.tuesday, 10, 45),
                                 self.at(self.wednesday + timedelta(days=1), 16))
        page, entry = self.reissue("a")
        self.assertIn("**Two decisions need your answer.**", page)
        self.assertEqual([i.get("event") for i in entry["inserts"] if i["section"] == "action"], [first["id"], second["id"]])
        self.assertEqual(self.holds(week), held)
        self.commit("second trade call")
        # 2 p.m.: Stone opposes the first call; his answer is not a change of situation.
        self.clock(self.tuesday, 14)
        self.answer(first["id"], self.period, "I oppose the proposal.")
        first = open_events.get(SEASON, first["id"], root)
        self.assertEqual((first["state"], first["response"]["substance"]), ("answered", {"kind": "oppose"}))
        self.assertEqual((se.item(root, first["queue_item"])["status"],
                          se.item(root, first["queue_item"])["resolution"]["by"]), ("RESOLVED", "user"))
        self.assertIsNone(render_game_week.reissue_reason(render_game_week.Week(root)))
        self.commit("Stone's answer")
        # 3 p.m.: Caldwell declines it from his criteria: one Trade Result, readable that day.
        self.clock(self.tuesday, 15)
        first = self.resolve(first["id"], "declined", "caldwell", self.at(self.tuesday, 15),
                             "Caldwell declined the call; the roster stays as it is.")
        self.assertEqual(first["resolution"]["decision"]["criteria"], 0)
        result = root / first["resolution"]["result_page"]
        self.assertEqual(result.parent, decisions.event_folder("trade_talks", SEASON, root))
        self.assertEqual(result.name, "Trade_Result_%s_Test_Club.md" % self.tuesday.isoformat())
        text = result.read_text(encoding="utf-8")
        self.assertEqual(clean_pages.page_errors(result.relative_to(root).as_posix(), text, root=root), [])
        self.assertEqual([json.loads(m)["id"] for m in ev_mod.EVENT_META.findall(text)], [first["id"]])
        self.assertIn("**Stone's answer:** Opposed it", text)
        self.assertIn("**Outcome:** Declined.", text)
        record_md = ev_mod.annual_record_path(root, SEASON).read_text(encoding="utf-8")
        self.assertIn("- %s: David Caldwell declined the trade call from Test Club. [Full record](%s)." % (
            se.long_date(self.tuesday), result.relative_to(self.paths.annual_record.parent).as_posix()), record_md)
        index = self.pages.readme.read_text(encoding="utf-8")
        self.assertIn(event_inserts.OTHER_BUSINESS, index)
        self.assertIn(os.path.relpath(result, self.pages.folder), index)
        self.assertEqual(self.holds(week), held)
        self.first, self.second = first, open_events.get(SEASON, second["id"], root)
        self.commit("first trade call declined")

    # ------------------------------------------------------------------ 4. the withdrawal
    def wednesday_withdrawal(self):
        root = self.root
        self.clock(self.wednesday, 11)
        second = self.second
        open_events.add_process(SEASON, second["id"], {
            "at": open_events.iso(self.at(self.wednesday, 10, 30)), "kind": "withdrawn_by_other_side", "by": "other_club",
            "what": "A test record: the other club withdrew its call before any answer was given.",
            "source": {"path": self.call_source}}, root)
        second = self.resolve(second["id"], "withdrawn", "other_club", self.at(self.wednesday, 10, 45),
                              "The club withdrew its call before an answer was given.")
        item = se.item(root, second["queue_item"])
        self.assertEqual((item["status"], item["resolution"]["by"]), ("WITHDRAWN", "organization"))
        self.assertIn(open_events.OTHER_SIDE_SUMMARY, item["resolution"]["summary"])
        page = root / second["resolution"]["result_page"]
        self.assertEqual(page.name, "Trade_Result_%s_Second_Test_Club.md" % self.wednesday.isoformat())
        self.assertIn("**Stone's answer:** No answer was given; the question ended before he answered.",
                      page.read_text(encoding="utf-8"))
        # News for the next issue: it does not reissue this one.
        self.assertIsNone(render_game_week.reissue_reason(render_game_week.Week(root)))
        self.assertEqual(second["resolution"]["after_issue"]["period"], self.period)
        self.second = second
        self.assertEqual(sorted(p.name for p in decisions.event_folder("trade_talks", SEASON, root).glob("Trade_Result_*")),
                         sorted([Path(self.first["resolution"]["result_page"]).name, page.name]))
        self.commit("second trade call withdrawn")

    # ------------------------------------------------------------------ 5. the Game Plan
    def game_plan_against_the_latest_issue(self):
        root, week = self.root, self.week
        wk = render_game_week.Week(root)
        previous = max(w for w in range(1, week) if self.paths.call_sheet(w).is_file())
        inactive = needed_inactives(root, week)
        self.plan_answers = answers_for(previous, inactive, role_cover(root, inactive))
        text = game_plan.render("Week %d Game Plan" % week, render_game_week.plan_facts(wk), self.plan_answers)
        self.assertIn("**Briefing used:** %s" % render_game_week.label_of(render_game_week.current_issue(wk)), text)
        wk.pages.plan.write_text(text, encoding="utf-8")
        (problems, notes, _), _ = quiet(check_game_plan.check, root, SEASON, week)
        self.assertEqual(problems, [])
        # Complete, but not set while an exam its items wait on is still to come.
        self.waits = [w for i in decision_queue.load(root)["items"] if i["status"] == "OPEN"
                      and any(b.get("week") == week for b in i.get("blocks") or ())
                      for w in i.get("waits_on") or () if w.get("date")]
        (problems, written), _ = quiet(apply_game_plan.apply, root, SEASON, week)
        if any(date.fromisoformat(w["date"]) >= self.wednesday for w in self.waits):
            self.assertEqual(written, [])
            self.assertFalse(self.pages.call_sheet.exists())
        self.commit("Game Plan written")

    # ------------------------------------------------------------------ 6. the practice-week commit
    def practice_week_commit(self):
        root, week = self.root, self.week
        saturday, monday = self.game_day - timedelta(days=1), self.tuesday - timedelta(days=1)
        wk = render_game_week.Week(root)
        se.set_clock(root, "%s, after the game-day clock advance for Week %d %s" % (se.long_date(self.game_day), week,
                                                                                    wk.where()))
        # The exams of the week, each recorded on its date (test data: no change).
        data = json.loads(self.paths.roster.read_text(encoding="utf-8"))
        names = []
        for wait in self.waits:
            name = wait["what"].split("'s reassessment")[0]
            if name in names:
                continue
            names.append(name)
            row = next(p for p in data["players"] if p["name"] == name)
            day = date.fromisoformat(wait["date"])
            new = re.sub(r"; reassessment [A-Z][a-z]+ \d{1,2}", "; reassessed %s %d with no change (%s)" % (
                day.strftime("%B"), day.day, TEST), row["availability"], count=1)
            self.assertNotEqual(new, row["availability"])
            row["availability"] = new
        self.paths.roster.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        history = wpages.medical_path(wpages.Season(root, SEASON), "medical_history.md")
        recorded = history.read_bytes()
        heading = "%s to %s: test reassessments" % (se.long_date(monday).rsplit(",", 1)[0], (
            "%d" % saturday.day if saturday.month == monday.month else se.long_date(saturday).rsplit(",", 1)[0]))
        line = {"date": monday.isoformat(), "date_end": saturday.isoformat(), "status": "closed",
                "id": "%s-to-%s-test-reassessments" % (monday.isoformat(), saturday.strftime("%m-%d")),
                "summary": "A test record of the week's reassessments, with no change; the practice week produced no "
                           "injury or new restriction."}
        history.write_text(recorded.decode("utf-8") + "\n<!-- event-record: %s -->\n\n## %s\n\nA test record for the "
                           "rehearsal: %s reassessed on the dates the instructions named, with no change.\n" % (
                               json.dumps(line, sort_keys=True), heading, " and ".join(names) or "no player was"),
                           encoding="utf-8")
        anchor = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        # What was held, against the schedule the standing instruction set.
        schedule, why = rpw.applied_schedule(root, SEASON, week)
        self.assertIsNotNone(schedule, why)
        source = {"page": self.pages.readme.relative_to(root).as_posix()}
        sessions = [dict(s, participation_recorded=False, participation=[
            {"player": n, "status": "did_not_participate", "basis": "medical_instruction",
             "medical": {"page": history.relative_to(root).as_posix(), "anchor": anchor}, "source": source}
            for n in names] if s["type"] == "practice" else []) for s in schedule["sessions"]]
        held = root.parent / "held.json"
        held.write_text(json.dumps({"source": source, "sessions": sessions, "days_off": schedule["days_off"],
                                    "gaps": ["Participation was not recorded session by session (%s)" % TEST]}),
                        encoding="utf-8")
        used = practices.padded_status(SEASON, week - 1, root)["first"]["used"]
        problems, _, written = rpw.record(root, SEASON, week, held)
        self.assertEqual(problems, [])
        self.assertTrue(written.is_file())
        self.assertEqual(practices.padded_status(SEASON, week, root)["first"]["used"], used + self.padded)
        # The Game Report opened with its preparation and pregame media, frozen, and its two event lines.
        sequence = max(item["sequence"] for _, _, item in ev_mod.closures(ev_mod.load_events(root))) + 1
        prep = {"closure": {"checkpoint": "Canonical update - %s - Week %d preparation closed (%s)" % (
                    se.long_date(saturday), week, TEST), "sequence": sequence, "through": saturday.isoformat()},
                "date": monday.isoformat(), "date_end": saturday.isoformat(), "status": "closed",
                "id": "%s-week-%d-preparation-closed" % (saturday.isoformat(), week),
                "summary": "A test record: the Week %d preparation closed under Stone's standing practice instruction."
                           % week}
        day = {"closure": {"checkpoint": "Canonical update - %s - Week %d game day (%s)" % (
                   se.long_date(self.game_day), week, TEST), "sequence": sequence + 1, "through": self.game_day.isoformat()},
               "date": self.game_day.isoformat(), "id": "%s-week-%d-game-day" % (self.game_day.isoformat(), week),
               "kind": "technical", "status": "closed",
               "summary": "A test record: game day of Week %d; the clock reached the game." % week}
        self.pages.report.write_text(opened_report(root, self.game, week, [prep, day], names), encoding="utf-8")
        self.assertEqual(quiet(freeze_pregame.main, [str(week), "--season", str(SEASON), "--root", str(root)])[0], 0)
        self.checkpoint(day["closure"]["checkpoint"])
        quiet(coaching_check.main, ["--season", str(SEASON), "--effective"], root=root, out=print)
        if names:
            # The entries changed the brief's own sections while the week's items are open: reissued.
            _, entry = self.reissue("b")
            self.game_day_issue = entry
            (problems, _, _), _ = quiet(check_game_plan.check, root, SEASON, week)
            self.assertTrue(any(p.startswith("Briefing used:") for p in problems), problems)
            # "Briefing used" re-dated on his page (the runner's one edit; his answers stand).
            wk = render_game_week.Week(root)
            label = render_game_week.label_of(render_game_week.current_issue(wk))
            page = wk.pages.plan.read_text(encoding="utf-8")
            wk.pages.plan.write_text(re.sub(r"^(\*\*Briefing used:\*\* ).*$", lambda m: m.group(1) + label + "  ", page,
                                            count=1, flags=re.M), encoding="utf-8")
        (problems, _, _), _ = quiet(check_game_plan.check, root, SEASON, week)
        self.assertEqual(problems, [])
        self.commit("practice-week commit", check=True)

    # ------------------------------------------------------------------ the apply
    def game_plan_applied_after_the_exams(self):
        root, week = self.root, self.week
        (problems, written), _ = quiet(apply_game_plan.apply, root, SEASON, week)
        self.assertEqual(problems, [])
        self.assertIn(self.pages.call_sheet, written)
        items = [i for i in decision_queue.load(root)["items"] if i["class"] in ("weekly_game_plan", "game_day_inactives")
                 and any(b.get("week") == week for b in i["blocks"])]
        self.assertTrue(items and all((i["status"], i["resolution"]["by"]) == ("RESOLVED", "user") for i in items))
        self.assertEqual(decision_queue.blocking_errors([decision_queue.event("week_inputs", SEASON, week)], root), [])
        self.commit("Game Plan applied")

    # ------------------------------------------------------------------ 7. the close
    def close_with_a_long_term_injury(self):
        root, week = self.root, self.week
        inactive = set(json.loads(self.pages.inactives.read_text(encoding="utf-8"))["players"])
        chart = json.loads(self.paths.depth_chart.read_text(encoding="utf-8"))
        roles = set(chart.get("roles") or {})
        data = tx.roster(SEASON, root)
        self.injured = next(r["name"] for r in data["players"] if r["list"] == "active" and r["position"] == "CB"
                            and r["name"] not in inactive and r["name"] not in roles)
        opened = self.pages.report.read_text(encoding="utf-8")
        closed_week, game, receipt = srm.close_open_week(root, SEASON, [(self.injured, "long_term", 70)])
        self.assertEqual(closed_week, week)
        played = date.fromisoformat(game["date"])
        # The Game Report: its frozen pregame sections as they were, each result of the week linked.
        results, still = open_events.period_events(SEASON, self.period, root)
        self.assertEqual(still, [])
        ours = [r for r in game_weeks.regular_receipts(self.paths) if CLUB in (r["away"], r["home"])]
        record = sorted(game_report.record_forms(ours, CLUB), key=len)[0]
        page = template_report(receipt, game_weeks.club_game(self.paths, week, CLUB), record, root)
        for heading in game_report.PREGAME:
            page = page.replace(section(page, heading), section(opened, heading), 1)
        links = ["[%s](%s)" % (open_events.title(r), os.path.relpath(root / r["resolution"]["result_page"],
                                                                     self.pages.folder)) for r in results]
        page = page.replace("## 7. ", "The week's other business: %s.\n\n## 7. " % "; ".join(links), 1)
        sequence = max(item["sequence"] for _, _, item in ev_mod.closures(ev_mod.load_events(root))) + 1
        checkpoint = "Canonical update - %s - Week %d closed" % (wpages.long_date(played), week)
        event = {"date": played.isoformat(), "id": "%s-week-%d-game" % (played.isoformat(), week), "status": "closed",
                 "summary": "%s in the Week %d game (a test close)." % (wpages.score_line(receipt), week),
                 "closure": {"checkpoint": checkpoint, "through": played.isoformat(), "sequence": sequence}}
        title, rest = page.split("\n", 1)
        earlier = [line for line in opened.splitlines() if line.startswith("<!-- event-record: ")]
        text = "\n".join([title, ""] + earlier + ["<!-- event-record: %s -->" % json.dumps(event, sort_keys=True), rest])
        self.pages.report.write_text(text, encoding="utf-8")
        self.assertEqual(game_report.pregame_errors(text, json.loads(self.pages.pregame.read_text(encoding="utf-8")),
                                                    True), [])
        self.assertEqual(game_report.result_link_errors(text, results, self.pages.report.relative_to(root).as_posix()), [])
        self.checkpoint(checkpoint)
        snapshot = hashlib.sha256((root / STATE).read_bytes()).hexdigest()
        _, client = local_service(self, root / "private-close", "rehearsal-r3-close", snapshot=snapshot)
        with patch.object(league_awards, "ROOT", root), patch("runtime.private_client.Client", return_value=client), \
                patch.object(sys, "argv", ["league_awards", "week", str(week), "--season", str(SEASON), "--close"]), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(league_awards.main(), 0)
        # The roster question the game leaves: one event, legal options only, Caldwell's criteria first.
        lines = []
        self.assertEqual(injury_events.main([str(week), "--season", str(SEASON)], root=root, out=lines.append), 0, lines)
        events = [e for e in open_events.load(SEASON, root) if e["kind"] == tx.KIND]
        self.assertEqual([e["subject"] for e in events], [self.injured])
        event = events[0]
        self.next_week = self.open_week()
        self.assertEqual((event["period"], event["authority"], event["stone_part"]),
                         ({"week": self.next_week}, {"rows": ["3", "5", "7"], "decides": "caldwell"}, "recommends"))
        self.assertEqual(event["process"][0]["kind"], "criteria")
        for text_ in [f["value"] for f in event["facts"]] + [o["basis"] for o in event["options"]]:
            self.assertIsNone(GRADE.search(text_), text_)
        squad = {r["name"] for r in data["players"] if r["list"] == "practice_squad"}
        self.assertTrue(squad <= {o["name"] for o in event["options"]})
        self.assertFalse(open_events.cannot_dress(event))
        self.assertFalse(any(decision_queue.holds(i, decision_queue.event("week_inputs", SEASON, self.next_week))
                             for i in decision_queue.load(root)["items"] if i.get("event") == event["id"]))
        self.event = event
        # The week's head-coach check, once; a second run is refused.
        lines = []
        self.assertEqual(coaching_check.close(SEASON, week, root, client, lines.append), 0, lines)
        with self.assertRaises(coaching_check.Refused):
            coaching_check.close(SEASON, week, root, client, lines.append)
        changed = {r["club"] for w, r in getattr(self, "changes", ())}
        self.assertFalse(changed & {r["club"] for r in lc.checks(SEASON, root)[week]["clubs"]})
        # The new incident record enters the season's carry-forward inventory.
        season_handoff.prepare(root, SEASON)
        self.commit("week closed", check=True)
        # The next week opened: its first issue asks the roster question; My Responses has its block.
        first = self.issues(self.next_week)[0]
        self.assertIn(("action", event["id"]), [(i["section"], i.get("event")) for i in first["inserts"]])
        nxt = decisions.week_pages(SEASON, self.next_week, root)
        self.assertIn("## %s" % open_events.title(event), nxt.responses.read_text(encoding="utf-8"))
        # Each trade result shows under FOR YOUR INFORMATION in exactly one issue: the first after it.
        weeks = [week, self.next_week]
        for record in (self.first, self.second):
            record = open_events.get(SEASON, record["id"], root)
            shown = self.fyi_issues(record["id"], weeks)
            self.assertEqual(shown, [self.successor(record["resolution"]["after_issue"], weeks)], record["id"])
        if getattr(self, "game_day_issue", None) is not None:
            # The practice-week commit issued the week again after the withdrawal: the notice is in that
            # issue, so the next week's first issue does not repeat it.
            self.assertEqual(self.fyi_issues(self.second["id"], weeks), [(week, len(self.issues(week)))])
        for news in lc.stored_news(SEASON, root).values():
            self.assertLessEqual(len(self.fyi_issues(news["id"], weeks)), 1)

    # ------------------------------------------------------------------ 8. the roster move
    def injury_replacement_by_promotion(self):
        root, week = self.root, self.next_week
        event = self.event
        played = date.fromisoformat(next(g for g in open_events.club_fixtures(SEASON, root)
                                         if int(g["week"]) == self.week)["date"])
        monday = played + timedelta(days=1)
        options = [o for o in event["options"] if "Practice squad" in o["basis"]]
        squad = next((o["name"] for o in options if o["position"] in ("DB", "CB", "S")), options[0]["name"])
        frozen = week_digests(root, week)
        log_before = len(json.loads(self.paths.record("team/depth_chart/update_log.json").read_text())["entries"])
        # 10 a.m.: Stone recommends the promotion; a recommendation executes nothing.
        self.clock(monday, 10)
        self.answer(event["id"], {"week": week}, "I recommend %s for the place." % squad,
                    reason="He knows the coverage calls.")
        answered = open_events.get(SEASON, event["id"], root)
        self.assertEqual((answered["state"], answered["response"]["substance"]),
                         ("answered", {"kind": "recommend", "option": squad}))
        self.assertIsNone(answered["resolution"])
        self.assertIn(squad, {r["name"] for r in tx.roster(SEASON, root)["players"] if r["list"] == "practice_squad"})
        # The brief is not issued again for his answer, nor for a game dated after its issue.
        self.assertIsNone(render_game_week.reissue_reason(render_game_week.Week(root)))
        self.commit("Stone's recommendation")
        # 11 a.m.: Caldwell decides from his criteria; the runner records and applies it.
        self.clock(monday, 11)
        source = answered["raised"]["source"]
        decision = {"schema": tx.SCHEMA, "id": "%s-decision-1" % event["id"], "season": SEASON, "event": event["id"],
                    "date": monday.isoformat(), "at": open_events.iso(self.at(monday, 11)),
                    "decided_by": answered["authority"]["decides"], "criteria": 0,
                    "recommendation": tx.recommendation_of(answered),
                    "basis": {"text": "A test decision: the club keeps its numbers at the position for the next game.",
                              "source": source},
                    "moves": [{"player": self.injured, "kind": "reserve", "from_list": "active", "to_list": "reserve",
                               "designation": "ordinary"},
                              {"player": squad, "kind": "promoted", "from_list": "practice_squad", "to_list": "active",
                               "availability": {"text": "No communicated restriction (a test medical communication "
                                                        "for %s)" % squad, "source": source["path"]}}],
                    "source": source, "status": "decided"}
        path = root.parent / "decision.json"
        path.write_text(json.dumps(decision), encoding="utf-8")
        lines = []
        self.assertEqual(apply_transaction.main(["--file", str(path), "--season", str(SEASON)], root=root,
                                                out=lines.append), 0, lines)
        lines = []
        self.assertEqual(apply_transaction.main([decision["id"], "--season", str(SEASON)], root=root,
                                                out=lines.append), 0, lines)
        documents_after_moves(self, root, decision["moves"], monday)
        # One Transaction page, the event's one result, readable at once.
        resolved = open_events.get(SEASON, event["id"], root)
        self.assertEqual(resolved["state"], "resolved")
        page = root / resolved["resolution"]["result_page"]
        self.assertEqual(page.name, "Transaction_%s_%s.md" % (monday.isoformat(), self.injured.replace(" ", "_")))
        roster_folder = decisions.event_folder(tx.KIND, SEASON, root)
        self.assertEqual([p.name for p in roster_folder.glob("Transaction_%s_*.md" % monday.isoformat())], [page.name])
        text = page.read_text(encoding="utf-8")
        self.assertEqual(clean_pages.page_errors(page.relative_to(root).as_posix(), text, root=root), [])
        self.assertEqual([json.loads(m)["id"] for m in ev_mod.EVENT_META.findall(text)], [event["id"]])
        self.assertIn(page.name, ev_mod.annual_record_path(root, SEASON).read_text(encoding="utf-8"))
        self.assertIn(page.name, decisions.week_pages(SEASON, week, root).readme.read_text(encoding="utf-8"))
        # The roster record, the contract record and inputs, the player record, the chart and its log agree.
        rows = {r["name"]: r for r in tx.roster(SEASON, root)["players"]}
        self.assertEqual((rows[self.injured]["list"], rows[squad]["list"]), ("reserve", "active"))
        self.assertEqual(sum(r["list"] == "active" for r in rows.values()), 53)
        self.assertEqual(player_contracts.errors(root), [])
        self.assertEqual(render_contract_pages.check(root, SEASON), [])
        current = player_contracts.contract_on(player_contracts.load(people.slugify(squad), root))
        self.assertEqual(current["start"]["method"]["name"], "promotion")
        self.assertEqual(people.load_all(root)[people.slugify(squad)]["transactions"][-1]["kind"], "promoted")
        chart = json.loads(self.paths.depth_chart.read_text(encoding="utf-8"))
        self.assertNotIn(self.injured, sum(chart["depth"].values(), []))
        self.assertIn(squad, sum(chart["depth"].values(), []))
        log = json.loads(self.paths.record("team/depth_chart/update_log.json").read_text())["entries"]
        self.assertEqual(len(log), log_before + 1)
        self.assertEqual(tx.validation_errors(root), [])
        self.assertEqual(render_club_pages.check(root), [])
        # The rails' control, the exclusivity gate on the next week's inputs, built in the copy by the game
        # path's own builder (the latest frozen sheet standing in for the week's), and the week's own pages
        # untouched.
        registry = player_bios.load(root)
        control = rails.jacksonville_control(SEASON, root)
        for name in (squad, self.injured):
            self.assertTrue(control.controlled(registry[name]["gsis_id"], monday), name)
        gate = subprocess.run([sys.executable, "-c", GATE, str(root), str(week)], cwd=str(root), capture_output=True,
                              text=True, env={"PYTHONPATH": str(root), "PATH": "/usr/bin:/bin"})
        self.assertEqual(gate.stdout.strip().splitlines()[-1:], ["[]"], gate.stderr[-2000:])
        self.assertEqual(week_digests(root, week), frozen)
        # Applied once.
        with self.assertRaises(tx.Refused):
            apply_transaction.apply(root, SEASON, decision["id"], rebuild=False, out=lambda *_: None)
        self.squad = squad
        self.commit("roster move applied", check=True)

    # ------------------------------------------------------------------ 9. COMING UP
    def coming_up_windows_and_the_trading_deadline(self):
        root = self.root
        weeks = [self.week, self.next_week]
        shown = {(w, n): {i["window"]: i["section"] for i in e.get("inserts") or () if "window" in i}
                 for w in weeks for n, e in enumerate(self.issues(w), 1)}
        at = {(w, n): open_events.issued_at(e) for w in weeks for n, e in enumerate(self.issues(w), 1)}
        # Each eligibility window on the roster record shows in every brief issued before its date.
        data = tx.roster(SEASON, root)
        windows = [("%s-%s-%s" % (deadlines._name_key(r["name"]), what, season_summary.date_on(
                       when, date(SEASON, 9, 1)).isoformat()), season_summary.date_on(when, date(SEASON, 9, 1)))
                   for r in data["players"] for what, when in deadlines.LIMIT.findall(r.get("availability") or "")]
        for key, day in windows:
            for issue, found in shown.items():
                if self.issues(issue[0])[issue[1] - 1].get("inserts") is None:
                    continue        # an issue written before step 5 recorded no window
                self.assertEqual(key in found, at[issue] < open_events.et(day), (key, issue))
        # The trading deadline: only under COMING UP, only in the briefs of the last game before it.
        deadline = deadlines.trading_deadline(SEASON, root)
        if deadline is None:
            return
        key = deadlines.league_date(SEASON, "trading_deadline", root)["key"]
        last = max((g for g in open_events.club_fixtures(SEASON, root) if open_events.kickoff(g) < deadline),
                   key=open_events.kickoff)
        for issue, found in shown.items():
            if key in found:
                self.assertEqual(found[key], "coming_up")
                self.assertTrue(issue[0] == int(last["week"]) or at[issue] >= open_events.kickoff(last), issue)
                self.assertLess(at[issue], deadline)
        if self.next_week == int(last["week"]):
            self.assertTrue(all(key in found for (w, _), found in shown.items() if w == self.next_week))
        after_game = open_events.kickoff(last) + timedelta(hours=4)
        later = int(last["week"]) + 1
        if after_game < deadline:
            route = open_events.route(SEASON, after_game, {"week": later}, root, issue=1)
            window = next(n.window for n in route.coming_up if n.key == key)
            self.assertEqual((window["state"], window["action"]), (deadlines.NO_PROPOSAL, deadlines.NO_ANSWER))
        # Afterward nothing shows, and no hold, page or question exists.
        past = deadline + timedelta(minutes=1)
        self.assertNotIn(key, [w["key"] for w in deadlines.coming_up(SEASON, past, root)])
        route = open_events.route(SEASON, past, {"week": later}, root, issue=1)
        self.assertFalse(any(n.key == key for n in route.coming_up))
        self.assertFalse(any(key in json.dumps(i) for i in decision_queue.load(root)["items"]))
        self.assertFalse(any(key in json.dumps(e) for e in open_events.load(SEASON, root)))
        results = sorted(p.name for p in decisions.event_folder("trade_talks", SEASON, root).glob("Trade_Result_*.md"))
        self.assertEqual(results, sorted(Path(r["resolution"]["result_page"]).name for r in (self.first, self.second)))


class NoInstructionTests(Runner):
    def test_without_a_standing_instruction_the_week_asks_its_practice_schedule(self):
        root, week = self.root, self.week
        job_path = root / current_job.JOB
        job = json.loads(job_path.read_text(encoding="utf-8"))
        rule = next(i for i in current_job.instructions(job) if i["subject"] == "practice_schedule")
        rule["status"] = "WITHDRAWN"
        job_path.write_text(json.dumps(job, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        held = self.holds(week)
        before = self.issues(week)
        quiet(render_game_week.write, root)
        # One practice item owned by Stone, holding nothing, and a blank "Practice week" block.
        item = rpw.practice_item(root, SEASON, week)
        self.assertEqual((item["class"], item["owner"], item["status"], item["blocks"]),
                         ("practice_plan", "stone", "OPEN", []))
        block = rpw.read_block(root, SEASON, self.period, decisions.PRACTICE_WEEK)
        self.assertEqual(block.answer, "")
        self.assertEqual(self.holds(week), held)
        # The brief issued again: its section 8 asks the practice week while the week's items are open.
        after = self.issues(week)
        self.assertEqual(len(after), len(before) + 1)
        self.assertTrue(after[-1]["reason"].startswith("b:"), after[-1]["reason"])
        brief = self.pages.briefing.read_text(encoding="utf-8")
        self.assertIn("Week %d practice week" % week, brief)
        self.assertIn("Answer the practice week under its heading on [My Responses]", brief)
        # The runner cannot record a schedule nobody gave.
        held_file = root.parent / "held.json"
        held_file.write_text(json.dumps({"source": {"page": "x"}, "sessions": [], "days_off": []}), encoding="utf-8")
        problems, _, written = rpw.record(root, SEASON, week, held_file)
        self.assertTrue(problems and "the runner cannot record a schedule nobody gave" in problems[0], problems)
        self.assertIsNone(written)
        self.commit("practice week asked")
        # His answer, checked before any session: a second padded day refused, nothing written.
        self.clock(self.tuesday, 9)
        from test_practices import answer_text
        two = answer_text(week, ("Wednesday", "Thursday")).replace("\n", "; ")

        def answer_with(text):
            current = self.pages.responses.read_text(encoding="utf-8")
            old = rpw.read_block(root, SEASON, self.period, decisions.PRACTICE_WEEK)
            self.pages.responses.write_text(current.replace(old.text, old.text.replace(
                "**My answer:**\n", "**My answer:** %s\n" % text, 1), 1), encoding="utf-8")
        answer_with(two)
        watched = [self.pages.responses, self.pages.responses_record, root / decision_queue.QUEUE]
        bytes_ = [p.read_bytes() for p in watched]
        status, problems, _, written = rpw.answer(root, SEASON, week)
        self.assertEqual((status, written), ("REFUSED", []))
        self.assertTrue(any("second padded practice" in p for p in problems), problems)
        self.assertEqual([p.read_bytes() for p in watched], bytes_)
        # One padded day, the day off and the walkthrough: set, and the item resolved by him.
        text = self.pages.responses.read_text(encoding="utf-8")
        self.pages.responses.write_text(text.replace(two, answer_text(week).replace("\n", "; ")), encoding="utf-8")
        used = practices.padded_status(SEASON, week - 1, root)["first"]
        status, problems, lines, _ = rpw.answer(root, SEASON, week)
        self.assertEqual((status, problems), ("SET", []))
        settled = rpw.practice_item(root, SEASON, week)
        self.assertEqual((settled["status"], settled["resolution"]["by"]), ("RESOLVED", "user"))
        schedule, why = rpw.applied_schedule(root, SEASON, week)
        self.assertEqual(schedule["source"]["heading"], decisions.PRACTICE_WEEK)
        self.assertEqual(sum(s["equipment"] == practices.PADDED for s in schedule["sessions"]), 1)
        self.assertEqual(practices.padded_status(SEASON, week - 1, root)["first"], used)
        # His first session, not the first day of the week's span, is the week's first practice: the
        # head-coach checks still due before it fail nothing yet.
        self.assertEqual(lc.first_practice_day(SEASON, week, root),
                         min(date.fromisoformat(s["date"]) for s in schedule["sessions"]))
        self.assertEqual(lc.coverage_errors(root, SEASON), [])
        self.commit("practice week set")


# ---------------------------------------------------------------------- helpers
def answers_for(previous, inactive, cover):
    """A complete Game Plan for the open week (test data, the choices tests/test_game_plan.py writes):
    the previous week carried, the standing rules, the inactives named from the stored facts, and each
    game role whose holder does not dress given to the next player of his group who does."""
    answers = {
        "baseline": "Carry Week %d" % previous, "attack": "Their linebackers in space against our tight ends.",
        "protect": "A cutback behind an overrun.", "change_course": "A safety rotating late to the second tight end.",
        "inactives": ", ".join(inactive), "depth": "; ".join(cover) if cover else "No change",
        "contingency": "Reissue after the examinations.", "coverage_units": "No change",
        "offense_caller": "No change", "base_personnel": "Twelve personnel leads.",
        "learn": "Who travels with the second tight end.", "opening_approach": "As last week, with changes below.",
        "opening": "Carry Week %d opening" % previous, "third_down": "Carry Week %d" % previous,
        "backed_up": "No change", "red_zone": "No change", "two_minute": "No change", "four_minute": "No change",
        "sudden_change": "No change", "special_plays": "No change", "not_available": "None",
        "defense_caller": "No change", "front": "Force and cutback first.", "coverage": "Quarters and 6.",
        "rush": game_plan.RUSH_CHOICE, "discover": "Their protection against the replaced rusher.",
        "matchups": "No change", "kicking_caller": "No change", "kicking": "No change",
        "fourth_down": "Standing rule", "two_point": "Standing rule", "kickoff": "Standing rule",
        "endgame": "No change", "participation": "Reissue after the examination.", "tradeoff": "None",
        "staff": "None", "public": "No new statement", "open_decisions": "None", "ready": "The exams of the week.",
        "practice": [["Third down", "Tice with the offense", "Third and medium", "The Saturday walkthrough"]]}
    return answers


def section(text, heading):
    """A ``##`` section of a page, its heading line to the next ``##`` heading."""
    start = text.index("## %s" % heading)
    end = text.index("\n## ", start + 3)
    return text[start:end + 1]


def opened_report(root, game, week, lines, names):
    """The Game Report as the practice-week commit opens it: the header, the week's two event lines,
    its preparation (test data) and the pregame media section, no session having been recorded; the
    other sections stay the template's prompts until the game is played."""
    template = (Path(root) / game_report.TEMPLATE).read_text(encoding="utf-8")
    _, rest = template.split("\n## Coach record", 1)
    when = date.fromisoformat(game["date"])
    header = ["# %s at %s" % (game["away"], game["home"]), "", "**Regular-season Week %d**  " % week,
              "%s, %s %d, %d | %s | %s  " % (game["weekday"], when.strftime("%B"), when.day, when.year,
                                            game["kickoff_et"], game.get("stadium")),
              "**Final: [Winner] [score], [Loser] [score]**", ""]
    for line in lines:
        header += ["<!-- event-record: %s -->" % json.dumps(line, sort_keys=True), ""]
    first = ("## 1. Preparation and final game-day decisions\n\nA test record of the preparation for the rehearsal: "
             "the week as Stone's standing practice instruction set it. %s\n\n**Plan in force:** Stone's [Week %d Game "
             "Plan](Game_Plan.md).  \n**Game-day availability:** As the Game Plan sets it.\n\n") % (
        ("%s did not practice under their medical instructions." % " and ".join(names)) if names else
        "No player was under a medical instruction.", week)
    second = "## 2. Pregame media\n\nNo pregame media session was recorded.\n\n"
    after = rest.split("\n## 3. The game", 1)[1]
    return "\n".join(header) + "\n## Coach record" + rest.split("\n## 1.", 1)[0] + "\n" + first + second + \
        "## 3. The game" + after


def week_digests(root, week):
    pages = decisions.week_pages(SEASON, week, root)
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
            for p in (pages.plan, pages.call_sheet, pages.applied)}


def documents_after_moves(test, root, moves, day):
    """Documents 4 and 5 after the moves, as the runner writes them in the transaction's commit (test
    data): a player placed on reserve keeps his index row with its status changed, a practice-squad
    promotion moves his row from the practice-squad table into the index, and both controlled counts
    move by the promotions."""
    register = Path(root) / "state/04_Roster_and_Staff_Register.md"
    text = register.read_text(encoding="utf-8")
    head, rest = text.split("### Current player index", 1)
    index, after = rest.split("### Players no longer", 1)
    when = se.long_date(day)
    added = 0
    for move in moves:
        if move["to_list"] == "reserve":
            row = next(l for l in index.splitlines() if l.startswith("| %s | JAX-" % move["player"]))
            cells = row.split(" | ")
            cells[5] = "Reserve/Injured (placed %s; %s)" % (when, TEST)
            index = index.replace(row, " | ".join(cells), 1)
        elif (move["from_list"], move["to_list"]) == ("practice_squad", "active"):
            row = next(l for l in after.splitlines() if l.startswith("| %s | JAX-" % move["player"]))
            after = after.replace(row + "\n", "", 1)
            cells = row.split(" | ")
            cells[5] = "Active 53 (promoted from the practice squad %s; %s)" % (when, TEST)
            last = [l for l in index.splitlines() if re.match(r"^\| [^|]+? \| JAX-", l)][-1]
            index = index.replace(last, last + "\n" + " | ".join(cells), 1)
            added += 1
    text = head + "### Current player index" + index + "### Players no longer" + after
    count = int(re.search(r"\| Current controlled players \| \*\*(\d+)\*\*", text)[1])
    text = text.replace("| Current controlled players | **%d**" % count, "| Current controlled players | **%d**"
                        % (count + added), 1)
    register.write_text(text, encoding="utf-8")
    state = Path(root) / STATE
    old = "| **Current Jacksonville controlled roster** | **%d** |" % count
    s = state.read_text(encoding="utf-8")
    test.assertIn(old, s)
    state.write_text(s.replace(old, "| **Current Jacksonville controlled roster** | **%d** |" % (count + added), 1),
                     encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
