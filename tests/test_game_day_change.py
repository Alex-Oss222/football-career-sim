"""Depth or inactives after the Game Plan is set (rebuild step 5, C2; scripts/change_game_day.py).

In a temporary copy, the open week's Game Plan is checked and applied once the
exams its items wait on are held (the week then waits on nothing). A later
medical entry puts a player the plan dresses out for the game: the change is
needed, one item owned by Stone opens with a blank block on My Responses, and
the week's build holds on that named item. Stone's change moves the inactives
through the Game Plan's own checks against the chart as applied, while the
call sheet, the applied plan record and the Game Plan keep their bytes; the
chart's inactives equal the week's inactives record, the build no longer
holds, and the Game Plan is not applied again. A change that dresses a player
out for the game, or sits a player a frozen variation names, is refused, as is
any change once the week's inputs are built, a game is paused or the week is
played. The Game Plan's own checks give the same answers through the
refactored ``Plan`` as before.

The week is the open week the stored facts give (the next Jacksonville game
not yet closed), never a date. Nothing is written to the real repository.
"""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import decision_queue  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402
from test_game_plan import SEASON, OpenWeek, needed_inactives, quiet  # noqa: E402


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class GameDayChangeTests(OpenWeek):
    def applied_week(self):
        """The open week's plan written, its exams held and the plan applied: the week waits on nothing."""
        self.write(self.answers())
        self.exams_held()
        self.apply()

    def dressed_player(self):
        """A player the applied plan dresses who holds no game role and is named in no variation: the
        last of the chart's largest defensive group who dresses."""
        chart = self.chart()
        inactive = set(json.loads(self.pages.inactives.read_text(encoding="utf-8"))["players"])
        roles = set(chart.get("roles") or {})
        for group in ("LB", "DL", "OL"):
            for name in reversed(chart["depth"].get(group) or ()):
                if name not in inactive and name not in roles:
                    return name
        self.fail("no dressed player without a role")

    def holds(self):
        return decision_queue.blocking_errors([decision_queue.event("week_inputs", SEASON, self.week)], self.root)

    def test_a_later_medical_entry_opens_the_change_and_the_answer_moves_the_inactives(self):
        from scripts import change_game_day as cgd
        from scripts.apply_game_plan import apply
        self.applied_week()
        self.assertEqual(self.holds(), [])
        # Before anything changes, no change is needed.
        item, message = cgd.open_item(self.root, SEASON, self.week)
        self.assertIsNone(item)
        self.assertIn("no change is needed", message)
        frozen = {p: digest(p) for p in (self.pages.call_sheet, self.pages.applied, self.pages.plan)}
        player = self.dressed_player()
        self.set_availability([player], self.out_note())
        item, message = cgd.open_item(self.root, SEASON, self.week)
        self.assertIsNotNone(item, message)
        self.assertEqual((item["class"], item["owner"], item["status"]), ("depth_and_roles", "stone", "OPEN"))
        self.assertEqual(item["deadline"]["before"], decision_queue.event("week_inputs", SEASON, self.week))
        self.assertIn(player, item["question"])
        page = self.root / item["record"]["path"]
        block = page.read_text(encoding="utf-8").split("## Depth and inactives change\n", 1)[1]
        self.assertEqual([line for line in block.splitlines() if line.strip()],
                         ["**My answer:**", "**My football or professional reason:**", "**Conditions or instructions:**",
                          "**Date answered:**"])
        # The build holds on the named item; a second call opens nothing more.
        self.assertTrue(any(item["id"] in line for line in self.holds()))
        again, message = cgd.open_item(self.root, SEASON, self.week)
        self.assertEqual(again["id"], item["id"])
        self.assertIn("already open", message)
        self.assertEqual(quiet(cgd.main, [str(self.week), "--season", str(SEASON), "--check", "--root",
                                          str(self.root)])[0], 1)
        before = json.loads(self.pages.inactives.read_text(encoding="utf-8"))["players"]
        # A change that dresses the player who is out is refused, and so is one that sits a player a frozen
        # variation names; nothing is written.
        queue_bytes = (self.root / decision_queue.QUEUE).read_bytes()
        problems, written = cgd.record_change(self.root, SEASON, self.week, {"inactives": {"players": before}},
                                              rebuild=False)
        self.assertTrue(any("%s is out" % player in p and "must be among them" in p for p in problems), problems)
        self.assertEqual(written, [])
        named = self.variation_player()
        if named is not None:
            swap = [named if p == before[-1] else p for p in before]
            problems, _ = cgd.record_change(self.root, SEASON, self.week, {"inactives": {"players": swap}},
                                            rebuild=False)
            self.assertTrue(any("needs %s, who does not dress" % named in p for p in problems), problems)
        self.assertEqual((self.root / decision_queue.QUEUE).read_bytes(), queue_bytes)
        # His change: the player who is out sits in place of the last healthy inactive.
        after = [player if p == before[-1] else p for p in before]
        problems, written = cgd.record_change(self.root, SEASON, self.week, {"inactives": {"players": after}},
                                              rebuild=False)
        self.assertEqual(problems, [])
        self.assertEqual({p: digest(p) for p in frozen}, frozen)
        chart = self.chart()
        record = json.loads(self.pages.inactives.read_text(encoding="utf-8"))
        self.assertEqual(chart["game_day_inactives"]["players"], record["players"])
        self.assertEqual((chart["game_day_inactives"]["week"], record["players"]), (self.week, after))
        self.assertEqual(record["as_set"]["players"], before)
        self.assertEqual(record["changes"][-1]["players_before"], before)
        changes = json.loads(self.pages.game_day_changes.read_text(encoding="utf-8"))
        self.assertEqual([(c["heading"], c["item"]) for c in changes["changes"]],
                         [("Depth and inactives change", item["id"])])
        log = json.loads(SeasonPaths(SEASON, self.root).record("team/depth_chart/update_log.json")
                         .read_text(encoding="utf-8"))
        self.assertTrue(log["entries"][-1]["sources"][0]["page"].startswith(item["record"]["path"] + "#"))
        queue = json.loads((self.root / decision_queue.QUEUE).read_text(encoding="utf-8"))
        settled = next(i for i in queue["items"] if i["id"] == item["id"])
        self.assertEqual((settled["status"], settled["resolution"]["by"]), ("RESOLVED", "user"))
        self.assertEqual(self.holds(), [])
        self.assertEqual(quiet(cgd.main, [str(self.week), "--season", str(SEASON), "--check", "--root",
                                          str(self.root)])[0], 0)
        # The plan is not applied again once a change is recorded.
        (problems, written), _ = quiet(apply, self.root, SEASON, self.week)
        self.assertEqual(written, [])
        self.assertTrue(problems and "after the Game Plan was applied" in problems[0], problems)
        # Repository validation of the copy holds the chart to the week's inactives record.
        from scripts.apply_game_plan import validation_errors
        self.assertEqual(validation_errors(self.root), [])
        self.assertEqual(cgd.validation_errors(self.root), [])
        # The week's inputs build from the changed chart (the game's own check of the dressed 46).
        self.assertEqual(self.build_errors(), "")

    def variation_player(self):
        """A dressed player a frozen call's variation names by his surname alone, or None."""
        sheet = json.loads(self.pages.call_sheet.read_text(encoding="utf-8"))
        roster = self.roster()
        inactive = set(json.loads(self.pages.inactives.read_text(encoding="utf-8"))["players"])
        surnames = {}
        for p in roster["players"]:
            surnames.setdefault(p["name"].split()[-1].lower(), []).append(p["name"])
        for call in sheet["offensive_call_sheet"]:
            for tag in call.get("tags") or ():
                for word in tag.split():
                    found = surnames.get(word.lower()) or []
                    if len(found) == 1 and found[0] not in inactive:
                        return found[0]
        return None

    def build_errors(self):
        """'' when the week's package builds in the copy, else the error."""
        import subprocess
        code = ("import json, sys\n"
                "sys.path.insert(0, '.')\n"
                "from runtime.seasons import SeasonPaths\n"
                "from runtime.week_inputs import build_package\n"
                "from scripts.build_week_inputs import AVERAGE_ANCHORS\n"
                "from scripts.render_season_stats import load_receipts\n"
                "week, season = %d, %d\n"
                "paths = SeasonPaths(season)\n"
                "sheet = json.loads(paths.call_sheet(week).read_text())\n"
                "receipts = [r for r in load_receipts(paths.receipts) if int(r['week']) < week]\n"
                "build_package(week, receipts, sheet['offensive_call_sheet'], AVERAGE_ANCHORS, season,\n"
                "    decisions=sheet.get('decisions'), defensive_sheet=sheet.get('defensive_call_sheet'))\n"
                % (self.week, SEASON))
        done = subprocess.run([sys.executable, "-c", code], cwd=self.root, capture_output=True, text=True)
        return "" if done.returncode == 0 else done.stderr.strip().splitlines()[-1]

    def answer(self, heading, text):
        """His answer written on the week's My Responses page, in the block under ``heading``."""
        from scripts import record_practice_week as rpw
        page = self.pages.responses
        block = rpw.read_block(self.root, SEASON, {"week": self.week}, heading)
        lines = block.text.split("\n")
        start = lines.index("**My answer:**" if "**My answer:**" in lines else
                            next(l for l in lines if l.startswith("**My answer:**")))
        end = next(n for n in range(start + 1, len(lines)) if lines[n].startswith("**My football"))
        new = "\n".join(lines[:start] + ["**My answer:**"] + text.split("\n") + [""] + lines[end:])
        page.write_text(page.read_text(encoding="utf-8").replace(block.text, new, 1), encoding="utf-8")

    def test_his_block_on_my_responses_moves_the_inactives_and_is_frozen(self):
        from runtime import responses
        from scripts import change_game_day as cgd, record_practice_week as rpw
        self.applied_week()
        player = self.dressed_player()
        self.set_availability([player], self.out_note())
        item, _ = cgd.open_item(self.root, SEASON, self.week)
        heading = "Depth and inactives change"
        frozen = {p: digest(p) for p in (self.pages.call_sheet, self.pages.applied, self.pages.plan)}
        args = [str(self.week), "--season", str(SEASON), "--root", str(self.root)]
        # Unanswered: the change stays open, --check says so and the apply writes nothing.
        code, out = quiet(cgd.main, args + ["--check"])
        self.assertEqual(code, 1)
        self.assertIn("unanswered", out)
        problems, notes, written = cgd.apply_answers(self.root, SEASON, self.week, rebuild=False)
        self.assertEqual((problems, written), ([], []))
        self.assertTrue(notes and "still open" in notes[0], notes)
        before = json.loads(self.pages.inactives.read_text(encoding="utf-8"))["players"]
        # An answer that dresses the player who is out, or a line the change does not take, is refused.
        for text, words in (("Inactives: %s" % ", ".join(before), "%s is out" % player),
                            ("Bring up a linebacker", "is not a line the change takes")):
            with self.subTest(words=words):
                self.answer(heading, text)
                page = self.pages.responses.read_bytes()
                problems, _, written = cgd.apply_answers(self.root, SEASON, self.week, rebuild=False)
                self.assertTrue(any(words in p for p in problems), problems)
                self.assertEqual((written, self.pages.responses.read_bytes()), ([], page))
        # His change, in the Game Plan's own line form: the player who is out sits in place of the last
        # healthy inactive.
        after = [player if p == before[-1] else p for p in before]
        self.answer(heading, "Inactives: %s\nDepth/role changes: No change" % ", ".join(after))
        code, out = quiet(cgd.main, args + ["--check"])
        self.assertEqual(code, 1)
        self.assertIn("ready to apply", out)
        problems, notes, written = cgd.apply_answers(self.root, SEASON, self.week, rebuild=False)
        self.assertEqual(problems, [])
        self.assertEqual(json.loads(self.pages.inactives.read_text(encoding="utf-8"))["players"], after)
        self.assertEqual({p: digest(p) for p in frozen}, frozen)
        block = rpw.read_block(self.root, SEASON, {"week": self.week}, heading)
        from runtime.player_bios import master_date
        on = master_date(self.root)
        self.assertEqual(block.fields["Date answered"], "%s %d, %d" % (on.strftime("%B"), on.day, on.year))
        binding = rpw.reserved_binding(self.root, SEASON, {"week": self.week}, heading)
        change = json.loads(self.pages.game_day_changes.read_text(encoding="utf-8"))["changes"][-1]
        self.assertEqual(binding["applied"]["sha256"], block.sha256)
        self.assertEqual(change["block_sha256"], block.sha256)
        self.assertEqual((binding["applied"]["substance"]["kind"], binding["applied"]["substance"]["inactives"]),
                         (cgd.CHANGE_KIND, after))
        self.assertEqual(responses.validation_errors(self.root), [])
        self.assertEqual(cgd.validation_errors(self.root), [])
        self.assertEqual(quiet(cgd.main, args + ["--check"])[0], 0)
        self.assertEqual(cgd.apply_answers(self.root, SEASON, self.week, rebuild=False)[2], [])
        # An upload that changes the frozen block is refused, and nothing is written.
        upload = self.root / "upload.md"
        upload.write_text(self.pages.responses.read_text(encoding="utf-8").replace(after[-1], before[-1]),
                          encoding="utf-8")
        page = self.pages.responses.read_bytes()
        code, out = quiet(cgd.main, args + ["--file", str(upload)])
        self.assertEqual(code, 1)
        self.assertIn("stays as written", out)
        self.assertEqual(self.pages.responses.read_bytes(), page)
        # The week's inputs build from the changed chart.
        self.assertEqual(self.build_errors(), "")

    def test_a_change_is_refused_once_built_paused_or_played(self):
        from scripts import change_game_day as cgd
        self.applied_week()
        self.set_availability([self.dressed_player()], self.out_note())
        item, _ = cgd.open_item(self.root, SEASON, self.week)
        self.assertIsNotNone(item)
        before = json.loads(self.pages.inactives.read_text(encoding="utf-8"))["players"]
        paths = SeasonPaths(SEASON, self.root)
        cases = []
        built = paths.cache(self.week, "inputs")
        cases.append((built, "{}", "has been built from the applied plan"))
        cases.append((paths.paused_game(self.week), json.dumps({"status": "paused"}), "A game is paused"))
        receipt = paths.receipts / ("week_%02d_test.json" % self.week)
        cases.append((receipt, json.dumps({"matchup": "Jacksonville Jaguars at X"}), "has been played"))
        for path, text, words in cases:
            with self.subTest(words=words):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
                try:
                    problems, written = cgd.record_change(self.root, SEASON, self.week,
                                                          {"inactives": {"players": before}}, rebuild=False)
                    self.assertEqual(written, [])
                    self.assertTrue(problems and words in problems[0], problems)
                    opened, message = cgd.open_item(self.root, SEASON, self.week)
                    self.assertIn(words, message)
                finally:
                    path.unlink()

    def test_nothing_opens_before_the_plan_is_applied(self):
        from scripts import change_game_day as cgd
        self.set_availability([needed_inactives(self.root, self.week)[-1]], self.out_note())
        item, message = cgd.open_item(self.root, SEASON, self.week)
        self.assertIsNone(item)
        self.assertIn("not applied yet", message)
        problems, written = cgd.record_change(self.root, SEASON, self.week, {"inactives": {"players": []}},
                                              rebuild=False)
        self.assertEqual(written, [])
        self.assertIn("not applied yet", problems[0])

    def test_the_plans_own_checks_give_the_same_answers_through_the_layered_plan(self):
        from scripts import check_game_plan as cgp
        self.write(self.answers(depth="Linebackers order: %s" % ", ".join(reversed(self.chart()["depth"]["LB"]))))
        default = cgp.Plan(self.root, SEASON, self.week)
        layered = cgp.Plan(self.root, SEASON, self.week, chart=self.chart(), choices=default.choices)
        for check in (cgp.inactive_problems, cgp.depth_problems, cgp.role_problems):
            self.assertEqual(check(layered), check(default), check.__name__)
        self.assertEqual(layered.inactives(), default.inactives())
        problems, _, _ = cgp.check(self.root, SEASON, self.week)
        self.assertEqual(problems, cgp.check(self.root, SEASON, self.week)[0])
        # An inactive list given to the plan is read when its choices name none.
        listed = needed_inactives(self.root, self.week)
        given = cgp.Plan(self.root, SEASON, self.week, inactives=listed, choices={"depth": "none"})
        self.assertEqual(given.inactives(), listed)


if __name__ == "__main__":
    unittest.main()
