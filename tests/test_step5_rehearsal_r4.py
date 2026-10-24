"""Rebuild step 5, acceptance test 4: a synthetic game-day change, in a temporary copy.

First, as before any week's practice week opens, every closed week's head-coach check still due is
drawn through the local test service (tests/test_week_close_pages.check_head_coaches, its rate
table zeroed in the copy, so no change is drawn). The open week (the first Jacksonville game without
a receipt, from the fixtures and receipts, never a date) is then taken, in a throwaway copy of the
checkout, as a week whose items wait on nothing: its Game Plan page blank and unapplied
(tests/test_game_plan.OpenWeek), and the exams its game-plan and inactives items waited on taken as
held before the week's first mid-week record. Then, at mid-week clock records (docs/run_week.md,
step 4a, the third master-date form), counted back from the game's own date:

1. On the Wednesday (four days before a Sunday game) Stone's Game Plan, written against the latest
   issue of the briefing, is checked and applied; the week then holds nothing.
2. On the Thursday a test trade call from a test club is recorded (scripts/raise_event.py), due the
   Friday at 4 p.m.: the briefing is issued again for the new answer only (rule (a)), the earlier
   copy kept, its own sections 1 to 8 unchanged but for the rows his Game Plan settled, which now
   say so; the applied plan stays valid and checkable as it was set (F11), with the reissue's note;
   My Responses gains the call's block; nothing is accepted, and the call holds only its own event,
   never the game.
3. On the Friday a test medical entry puts a player the applied plan dresses out for the game: the
   runner's ``change_game_day.py --needed`` opens the week's depth and inactives change, the
   briefing is issued again for it (rule (a)), My Responses gains its blank block, and the week's
   inputs are held on that named item.
4. On game day, before kickoff (a record of the morning), with the practice week recorded as the
   standing practice instruction set it: the build (scripts/build_week_inputs.py, run in the copy) is
   refused, naming the change; the trade call, past its due time and still open, is overdue and
   holds nothing.
5. Stone answers the change on My Responses in the Game Plan's own line form; ``change_game_day.py``
   moves the inactives (the chart's list equals the week's inactives record, the list as set kept),
   while the call sheet, the applied plan record and the Game Plan keep their bytes; the Game Plan is
   not applied again; the build then runs to READY with the exclusivity and game-day gate passed.

Repository validation of the copy adds nothing to the real checkout's at the Wednesday, Friday and
game-day commit points, and every page is clean. Every event is test data (its source a test page
the copy alone holds, its summary saying so). No game is drawn, the only service contacted is the
local test service, and nothing is written to the real repository; the engine is not touched. The
practice-week commit's Game Report opening and its event lines (docs/run_week.md, step 5) are
acceptance test 3's subject; here the clock reaches game day by a mid-week record. The in-season
rails coverage gate of the build (the other clubs' moves through the slate's cutoff, a separate data
commit researched in two passes when the clock reaches it) is the one gate the copy's build passes
by when the open week's rails are not yet committed; every other gate of the build runs as written.
"""
from datetime import date, datetime, timedelta
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import decision_queue, event_inserts, open_events, responses  # noqa: E402
from runtime.player_bios import master_date  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402
import support_events as se  # noqa: E402
from test_game_plan import SEASON, OpenWeek, quiet  # noqa: E402
from local_private_service import local_service  # noqa: E402
from test_week_close_pages import check_head_coaches, record_practice  # noqa: E402

CHANGE = "Depth and inactives change"
EXAM = re.compile(r"\breassessment (January|February|March|April|May|June|July|August|September|October|November|"
                  r"December) (\d{1,2})\b")
RAILS_GATE = "In-season rails: the moves are committed through"
BUILD = """
import sys
sys.path.insert(0, '.')
from scripts import build_week_inputs as b
gate = b.rails_coverage_error(%(week)d, %(season)d)
if gate is not None:
    assert gate.startswith(%(rails)r), gate
    b.rails_coverage_error = lambda *args: None
sys.argv = ['build_week_inputs.py', '%(week)d', '--season', '%(season)d']
sys.exit(b.main())
"""


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class GameDayChangeRehearsal(OpenWeek):
    """Acceptance test 4 of rebuild step 5, end to end in one temporary copy."""

    # ------------------------------------------------------------------ the runner's steps, in the copy
    def clock(self, day, hour, minute=0):
        """A mid-week record at ``hour``:``minute`` ET on ``day`` (the clock only moves forward)."""
        at = open_events.et(day, hour, minute)
        self.assertGreaterEqual(at, open_events.master_at(self.root), "the clock never moves back")
        se.midweek(self.root, day, hour, minute, self.week)
        return at

    def rebuild(self):
        """Every built page, as the runner's commit rebuilds them; the problems must be none."""
        from scripts import rebuild_pages
        written, problems = rebuild_pages.rebuild(self.root, SEASON)
        self.assertEqual(problems, [])
        return written

    def wk(self):
        from scripts import render_game_week
        return render_game_week.Week(self.root)

    def issues(self):
        from scripts import render_game_week
        return render_game_week.issues(self.wk())

    def holds(self):
        return decision_queue.blocking_errors([decision_queue.event("week_inputs", SEASON, self.week)], self.root)

    def build(self):
        """(exit code, output) of scripts/build_week_inputs.py run in the copy, no engine variable set."""
        import os
        env = {k: v for k, v in os.environ.items() if k not in ("ENGINE_RUNTIME_URL", "ENGINE_API_TOKEN")}
        code = BUILD % {"week": self.week, "season": SEASON, "rails": RAILS_GATE}
        done = subprocess.run([sys.executable, "-c", code], cwd=self.root, env=env, capture_output=True, text=True,
                              timeout=900)
        return done.returncode, done.stdout + done.stderr

    def wait_on_nothing(self, held, game_day):
        """A week whose items wait on nothing (test data): every exam the week's game-plan and
        inactives items waited on, and every reassessment a roster note names from the clock to the
        game, taken as held on ``held``, before the week's first mid-week record, with the medical
        staff's instruction otherwise as it stands; the items then wait on nothing."""
        queue = decision_queue.load(self.root)
        _, items = self.week_items(queue)
        self.assertTrue(items, "the open week has no game-plan or inactives item")
        for item in items:
            item["waits_on"] = []
        decision_queue.save(self.root, queue)
        path = SeasonPaths(SEASON, self.root).roster
        data = json.loads(path.read_text(encoding="utf-8"))
        clock = master_date(self.root)

        def moved(match):
            on = datetime.strptime("%s %s %d" % (match[1], match[2], game_day.year), "%B %d %Y").date()
            if clock <= on <= game_day:
                return "reassessment %s %d" % (held.strftime("%B"), held.day)
            return match[0]
        for row in data["players"]:
            if row.get("list") == "active" and row.get("availability"):
                row["availability"] = EXAM.sub(moved, row["availability"])
        path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    def dressed_player(self):
        """A player the applied plan dresses who holds no game role: the last of the chart's largest
        front or line group who dresses."""
        chart = self.chart()
        inactive = set(json.loads(self.pages.inactives.read_text(encoding="utf-8"))["players"])
        roles = set(chart.get("roles") or {})
        for group in ("LB", "DL", "OL"):
            for name in reversed(chart["depth"].get(group) or ()):
                if name not in inactive and name not in roles:
                    return name
        self.fail("no dressed player without a role")

    def answer(self, heading, text):
        """His answer written in place on the week's My Responses page, in the block under ``heading``."""
        block = responses.blocks_of(self.pages.responses.read_text(encoding="utf-8"))[heading]
        lines = block.text.split("\n")
        start = next(n for n, line in enumerate(lines) if line.startswith("**My answer:**"))
        end = next(n for n in range(start + 1, len(lines)) if lines[n].startswith("**My football"))
        new = "\n".join(lines[:start] + ["**My answer:**"] + text.split("\n") + [""] + lines[end:])
        page = self.pages.responses.read_text(encoding="utf-8")
        self.pages.responses.write_text(page.replace(block.text, new, 1), encoding="utf-8")

    def assert_validates(self):
        """Repository validation of the copy at a commit point adds nothing to the real checkout's."""
        from scripts.validate_repository import validate
        if not hasattr(type(self), "baseline"):
            type(self).baseline = set(validate(ROOT))
        self.maxDiff = None
        self.assertEqual(sorted(set(validate(self.root)) - self.baseline), [])

    def assert_only_notices_added(self, old, new, applied):
        """The reissue added notices at the top; its own sections are the earlier issue's, but for the
        rows of section 8 his Game Plan settled, which now say so (his answer, not a change of the
        situation)."""
        mine, theirs = event_inserts.own_sections(old).split("\n"), event_inserts.own_sections(new).split("\n")
        self.assertEqual(len(mine), len(theirs))
        settled = "| Set on your Game Plan, %s %d; nothing still to come |" % (applied.strftime("%B"), applied.day)
        for was, now in zip(mine, theirs):
            if was != now:
                self.assertTrue(now.endswith(settled) and was.split("|")[1] == now.split("|")[1], (was, now))

    def assert_plan_stands(self, frozen, note=False):
        """F11: the applied plan as it was set (its page, call sheet and record), valid, and checkable
        against the current briefing; ``note`` when a reissue added only notices at the top."""
        from scripts import apply_game_plan
        self.assertEqual({p: digest(p) for p in frozen}, frozen)
        self.assertEqual(apply_game_plan.validation_errors(self.root), [])
        problems, notes, _ = self.check()
        self.assertEqual([p for p in problems if p.startswith("Briefing used")], [])
        if note:
            self.assertIn(event_inserts.NOTE[:1].upper() + event_inserts.NOTE[1:], notes)

    # ------------------------------------------------------------------ the rehearsal
    def test_a_game_day_change_after_the_plan_is_applied(self):
        from scripts import apply_game_plan, change_game_day as cgd, raise_event
        real = {p: digest(ROOT / p) for p in (se.STATE, decision_queue.QUEUE)}
        real_receipts = sorted(p.name for p in SeasonPaths(SEASON, ROOT).receipts.glob("*.json"))
        game = se.open_game(self.root)
        self.assertEqual(int(game["week"]), self.week)
        game_day = date.fromisoformat(game["date"])
        wednesday, thursday, friday = (game_day - timedelta(days=n) for n in (4, 3, 2))
        if master_date(self.root) > wednesday:
            self.skipTest("the open week's clock is already past the fourth day before its game")

        # 0. Before the week's practice week opens, every closed week's head-coach check is drawn, the
        #    retroactive weeks first, through the local test service (tests/test_week_close_pages.py:
        #    the copy's rate table zeroed, so no change is drawn and nothing here depends on a draw).
        closed = max(int(p.name[5:7]) for p in SeasonPaths(SEASON, self.root).receipts.glob("week_*.json"))
        from runtime import league_coaches
        if league_coaches.due_weeks(SEASON, self.root, closed):
            snapshot = hashlib.sha256((self.root / se.STATE).read_bytes()).hexdigest()
            _, client = local_service(self, self.root / "private", "step5-rehearsal-r4", snapshot=snapshot)
            check_head_coaches(self, self.root, closed, client)

        # 1. The Wednesday: a week whose items wait on nothing; the Game Plan, written against the
        #    latest issue, checked and applied. Applying it reissues nothing and holds nothing.
        self.wait_on_nothing(wednesday - timedelta(days=1), game_day)
        self.clock(wednesday, 9)
        self.rebuild()
        self.assertIsNone(self.reissue_reason())
        self.write(self.answers())
        self.assertEqual(self.check()[0], [])
        self.assertEqual(apply_game_plan.waiting(self.check()[2]), [])
        issued = len(self.issues())
        self.apply()
        self.assertEqual(len(self.issues()), issued, "applying the plan is his answer, not a reissue")
        frozen = {p: digest(p) for p in (self.pages.plan, self.pages.call_sheet, self.pages.applied)}
        applied = json.loads(self.pages.applied.read_text(encoding="utf-8"))
        self.assertEqual(applied["applied"], wednesday.isoformat())
        self.assertEqual(self.holds(), [])
        self.assert_plan_stands(frozen)
        as_set = json.loads(self.pages.inactives.read_text(encoding="utf-8"))["players"]
        self.assertEqual(self.chart()["game_day_inactives"]["players"], as_set)
        self.assert_validates()

        # 2. The Thursday: a test trade call, due Friday 4 p.m., recorded through the one recorder.
        self.clock(thursday, 10, 30)
        due = open_events.et(friday, 16)
        record = se.trade_call(self.root, "test-call-game-day-rehearsal", open_events.et(thursday, 10), due)
        upload = self.root / "test_trade_call.json"
        upload.write_text(json.dumps(record, indent=1), encoding="utf-8")
        code, out = quiet(raise_event.main, ["--season", str(SEASON), "--file", str(upload), "--root", str(self.root)])
        self.assertEqual(code, 0, out)
        upload.unlink()
        call = open_events.get(SEASON, record["id"], self.root)
        self.assertEqual(call["period"], {"week": self.week})
        before = self.issues()
        old = self.pages.briefing.read_text(encoding="utf-8")
        self.assertTrue(self.reissue_reason().startswith("a:"))
        self.rebuild()
        after = self.issues()
        self.assertEqual(len(after), len(before) + 1)
        self.assertTrue(after[-1]["reason"].startswith("a:"), after[-1])
        self.assertEqual(after[-1]["at"], open_events.iso(open_events.et(thursday, 10, 30)))
        kept = self.pages.folder / after[-2]["file"]
        self.assertEqual(kept.read_text(encoding="utf-8"), old, "the earlier issue is kept as it went out")
        new = self.pages.briefing.read_text(encoding="utf-8")
        self.assertIn("## ACTION REQUIRED", new)
        self.assertNotIn(record["id"], new)
        self.assert_only_notices_added(old, new, wednesday)
        self.assertEqual([i.get("event") for i in after[-1]["inserts"] if i["section"] == "action"], [record["id"]])
        self.assertIsNone(self.reissue_reason())
        # F11: the plan as set stands, valid and checkable, with the reissue's note.
        self.assert_plan_stands(frozen, note=True)
        # His answer to the call is asked on My Responses; nothing is accepted or invented.
        self.assertIn("## " + open_events.title(call), self.pages.responses.read_text(encoding="utf-8"))
        call = open_events.get(SEASON, record["id"], self.root)
        self.assertEqual((call["state"], call["process"], call["resolution"]), ("open", [], None))
        self.assertEqual(se.item(self.root, call["queue_item"])["status"], "OPEN")
        # The call holds its own event only, never the game.
        self.assertTrue(decision_queue.blocking_errors(
            [decision_queue.event("event_resolution", SEASON, event=record["id"])], self.root))
        self.assertEqual(self.holds(), [])
        self.assertEqual(decision_queue.blocking_errors(
            [decision_queue.event("week_close", SEASON, self.week)], self.root), [])

        # 3. The Friday: a test medical entry puts a dressed player out for the game.
        self.clock(friday, 11)
        player = self.dressed_player()
        self.set_availability([player], self.out_note(), reissue=False)
        code, out = quiet(cgd.main, [str(self.week), "--season", str(SEASON), "--needed", "--root", str(self.root)])
        self.assertEqual(code, 0, out)
        self.assertIn("opened", out)
        opened = cgd.open_changes(self.root, SEASON, self.week)
        self.assertEqual(len(opened), 1)
        item = opened[0]
        self.assertIn(player, item["question"])
        self.assertEqual(item["deadline"]["at"], open_events.iso(open_events.kickoff(game)))
        self.assertTrue(any(item["id"] in line for line in self.holds()), self.holds())
        self.assertTrue(self.reissue_reason().startswith("a:"))
        friday_issue = len(self.issues()) + 1
        self.rebuild()
        entries = self.issues()
        self.assertEqual(len(entries), friday_issue)
        self.assertTrue(entries[-1]["reason"].startswith("a:"), entries[-1])
        self.assertEqual([i.get("item") for i in entries[-1]["inserts"] if i["section"] == "action" and "item" in i],
                         [item["id"]])
        brief = self.pages.briefing.read_text(encoding="utf-8")
        self.assertIn("**Two decisions need your answer.**", brief)
        self.assertIn("](My_Responses.md#%s)" % event_inserts.slug(CHANGE), brief)
        page = self.pages.responses.read_text(encoding="utf-8")
        self.assertEqual(page.count("## %s\n" % CHANGE), 1)
        block = responses.blocks_of(page)[CHANGE]
        self.assertEqual(block.answer, "")
        self.assertEqual(quiet(cgd.main, [str(self.week), "--season", str(SEASON), "--check", "--root",
                                          str(self.root)])[0], 1)
        # Nothing he set moved: the plan still stands as it was applied.
        self.assertEqual({p: digest(p) for p in frozen}, frozen)
        self.assertEqual(json.loads(self.pages.inactives.read_text(encoding="utf-8"))["players"], as_set)
        self.assert_validates()

        # 4. Game day, before kickoff: the clock reaches the game's day by a record of the morning, the
        #    practice week recorded as the standing instruction set it. The build is refused on the
        #    named change; the trade call, past its due time and still open, holds nothing.
        self.clock(game_day, 9)
        self.assertEqual(master_date(self.root), game_day)
        record_practice(self, self.root, self.week)
        self.rebuild()
        code, out = self.build()
        self.assertEqual(code, 1, out)
        self.assertIn("WEEK_INPUTS: BLOCKED", out)
        self.assertIn(item["title"], out)
        self.assertNotIn(se.item(self.root, call["queue_item"])["title"], out)
        self.assertIn(call["queue_item"], [i["id"] for i in decision_queue.overdue_items(
            decision_queue.load(self.root), open_events.master_at(self.root))])
        self.assertFalse((SeasonPaths(SEASON, self.root).cache(self.week, "inputs")).exists())

        # 5. His change on My Responses, in the Game Plan's line form: the player who is out sits in
        #    place of the last healthy inactive as set.
        changed = [player if p == as_set[-1] else p for p in as_set]
        self.answer(CHANGE, "Inactives: %s\nDepth/role changes: No change" % ", ".join(changed))
        code, out = quiet(cgd.main, [str(self.week), "--season", str(SEASON), "--root", str(self.root)])
        self.assertEqual(code, 0, out)
        self.assertIn("GAME-DAY CHANGE: RECORDED", out)
        self.assertEqual({p: digest(p) for p in frozen}, frozen, "the plan as set keeps its bytes")
        record = json.loads(self.pages.inactives.read_text(encoding="utf-8"))
        self.assertEqual(record["players"], changed)
        self.assertEqual(record["as_set"]["players"], as_set)
        self.assertEqual(self.chart()["game_day_inactives"]["players"], changed)
        settled = se.item(self.root, item["id"])
        self.assertEqual((settled["status"], settled["resolution"]["by"]), ("RESOLVED", "user"))
        self.assertEqual(self.holds(), [])
        self.assertEqual(quiet(cgd.main, [str(self.week), "--season", str(SEASON), "--check", "--root",
                                          str(self.root)])[0], 0)
        (problems, written), _ = quiet(apply_game_plan.apply, self.root, SEASON, self.week)
        self.assertEqual(written, [])
        self.assertTrue(problems and "after the Game Plan was applied" in problems[0], problems)
        self.assertEqual(apply_game_plan.validation_errors(self.root), [])
        self.assertEqual(cgd.validation_errors(self.root), [])
        self.assertEqual(responses.validation_errors(self.root), [])
        self.rebuild()
        self.assertIsNone(self.reissue_reason(), "his answer is not a change of situation")
        from scripts import render_game_week
        self.assertEqual(render_game_week.issue_errors(self.wk()), [])

        # The inputs build: every gate of the build passes on the changed chart.
        code, out = self.build()
        self.assertEqual(code, 0, out)
        self.assertIn("WEEK_INPUTS: READY", out)
        package = json.loads(SeasonPaths(SEASON, self.root).cache(self.week, "inputs").read_text(encoding="utf-8"))
        ours = next(g for g in package["games"] if se.CLUB in (g["away"], g["home"]))
        side = ours["away_input"] if ours["away"] == se.CLUB else ours["home_input"]
        self.assertEqual(len(side["active_players"]), len(set(side["active_players"])))
        self.assertNotIn(player, side["active_players"])
        self.assertIn(as_set[-1], side["active_players"])
        self.assertFalse(set(changed) & set(side["active_players"]))
        self.assertEqual({p: digest(p) for p in frozen}, frozen)
        # Once built, the week takes no further change.
        self.assertIn("has been built", cgd.open_item(self.root, SEASON, self.week)[1])

        # Every page clean, nothing re-recorded as history, and validation of the copy adds nothing to
        # the real checkout's; the real repository is untouched.
        from runtime import clean_pages
        self.assertEqual(clean_pages.clean_errors(self.root), [])
        self.assertEqual(clean_pages.history(self.root), clean_pages.history(ROOT))
        from scripts import rebuild_pages
        self.assertEqual(rebuild_pages.rebuild(self.root, SEASON, check=True), ([], []))
        self.assert_validates()
        self.assertEqual({p: digest(ROOT / p) for p in real}, real)
        self.assertEqual(sorted(p.name for p in SeasonPaths(SEASON, ROOT).receipts.glob("*.json")), real_receipts)

    def reissue_reason(self):
        from scripts import render_game_week
        return render_game_week.reissue_reason(self.wk())


if __name__ == "__main__":
    unittest.main()
