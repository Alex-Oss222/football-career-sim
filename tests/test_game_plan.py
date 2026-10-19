"""Stone's Game Plan page (runtime/game_plan.py), its check and its apply.

The round trip: Week 5's frozen call sheet and inactives, written as a Game
Plan page and applied in a temporary copy, give a byte-identical Week 5
call_sheet.json and the same inactives. The football content travels through
the page; the record's frame (its event, when and from what it was frozen, the
ids of its decision blocks and the packet lines its defensive rows cite) is
read back from the frozen sheet with frame_from_sheet, as the page has no
place for it (a Game Plan written from Week 6 on cites its own lines).

The check and apply tests work out the open week from the stored facts (the
next Jacksonville game not yet closed), never from a date.
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

from runtime import game_plan  # noqa: E402
from runtime import roster as roster_record  # noqa: E402
from runtime.clean_pages import page_errors  # noqa: E402
from runtime.decisions import week_pages  # noqa: E402
from runtime.rules import RULES  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402

SEASON = 2014
IGNORED = (".git", ".sim_cache", "__pycache__", ".pytest_cache")


def week_inactives(week, root=ROOT):
    """A week's inactives as set, from the week's inactives record (the chart holds only the latest)."""
    return json.loads(week_pages(SEASON, week, root).inactives.read_text(encoding="utf-8"))["players"]


WEEK5_INACTIVES = week_inactives(5)


def copy_repo(test):
    tmp = tempfile.TemporaryDirectory(dir=ROOT.parent)
    test.addCleanup(tmp.cleanup)
    root = Path(tmp.name) / "repo"
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(*IGNORED), symlinks=True)
    return root


def week5():
    path = SeasonPaths(SEASON, ROOT).call_sheet(5)
    return path.read_bytes(), json.loads(path.read_text(encoding="utf-8"))


class RoundTripTests(unittest.TestCase):
    def page(self, sheet):
        choices = game_plan.choices_from_sheet(sheet, {"players": WEEK5_INACTIVES})
        return game_plan.render("Week 5 Game Plan: Pittsburgh", "Sunday, October 5, 2014.", choices,
                                game_plan.legal_lines(7, "Mike Westhoff", 4))

    def test_the_week_5_inactives_record_is_the_list_set(self):
        # Stone's Week 5 game page names the seven he set; while the chart's list is Week 5's, it agrees.
        self.assertEqual(len(WEEK5_INACTIVES), 7)
        report = SeasonPaths(SEASON, ROOT).game_report(5).read_text(encoding="utf-8")
        for name in WEEK5_INACTIVES:
            self.assertIn(name.split()[-1], report)
        chart = json.loads(SeasonPaths(SEASON, ROOT).depth_chart.read_text(encoding="utf-8"))
        if chart["game_day_inactives"]["week"] == 5:
            self.assertEqual(chart["game_day_inactives"]["players"], WEEK5_INACTIVES)

    def test_week_5_sheet_survives_the_page(self):
        raw, sheet = week5()
        page = self.page(sheet)
        choices, problems = game_plan.parse(page)
        self.assertEqual(problems, [])
        self.assertEqual(choices["inactives"]["players"], WEEK5_INACTIVES)
        rebuilt = game_plan.build_sheet(choices, game_plan.frame_from_sheet(sheet))
        self.assertEqual(game_plan.sheet_bytes(rebuilt), raw)

    def test_the_frame_holds_no_football_choice(self):
        _, sheet = week5()
        frame = game_plan.frame_from_sheet(sheet)
        self.assertEqual(set(frame["top"]), set(game_plan.TOP_KEYS))
        for block in frame["decisions"].values():
            self.assertEqual(set(block), {"id", "source", "rules"})
            for rule in block["rules"]:
                self.assertEqual(set(rule), {"id", "source"})
        self.assertEqual(set(frame["defense"]), {"head", "rush", "practiced", "rows"})
        for where in [frame["defense"]["rush"]] + frame["defense"]["practiced"] + list(frame["defense"]["rows"].values()):
            self.assertEqual(set(where), {"path", "line"})

    def test_applied_in_a_copy_the_week_5_records_are_identical(self):
        from scripts.apply_game_plan import apply_records
        from scripts.check_game_plan import Plan
        root = copy_repo(self)
        raw, sheet = week5()
        pages = week_pages(SEASON, 5, root)
        pages.plan.write_text(self.page(sheet), encoding="utf-8")
        plan = Plan(root, SEASON, 5)
        self.assertEqual(plan.problems, [])
        rebuilt = game_plan.build_sheet(plan.choices, game_plan.frame_from_sheet(sheet), plan.carried(),
                                        plan.standing())
        apply_records(plan, rebuilt, plan.inactives(), resolve_queue=False)
        self.assertEqual(SeasonPaths(SEASON, root).call_sheet(5).read_bytes(), raw)
        chart = json.loads(SeasonPaths(SEASON, root).depth_chart.read_text(encoding="utf-8"))
        self.assertEqual((chart["game_day_inactives"]["week"], chart["game_day_inactives"]["players"]),
                         (5, WEEK5_INACTIVES))

    def test_same_as_week_5_carries_its_choices_exactly(self):
        _, sheet = week5()
        text = game_plan.render("Week 6 Game Plan", "Intro.", {
            key: {"same_as": 5} for key in ("offense", "fourth_down", "two_point", "kickoff", "defense", "notes")},
            game_plan.legal_lines())
        choices, problems = game_plan.parse(text)
        self.assertEqual(problems, [])
        frame = game_plan.frame_from_sheet(sheet)
        built = game_plan.build_sheet(choices, frame, {5: sheet})
        self.assertEqual({k: v for k, v in built.items() if k not in game_plan.TOP_KEYS},
                         {k: v for k, v in sheet.items() if k not in game_plan.TOP_KEYS})


def open_week(root):
    from scripts.render_game_week import Week
    return Week(root)


def needed_inactives(root, week):
    """A legal inactive list from the stored facts: every player out on game day, then the deepest
    reserve of the largest groups."""
    from runtime.week_inputs import roster_available
    from datetime import date
    paths = SeasonPaths(SEASON, root)
    roster = roster_record.load(paths.roster)
    chart = json.loads(paths.depth_chart.read_text(encoding="utf-8"))
    active = roster_record.players(roster, ("active",))
    game = next(g for g in paths.regular_games() if g["week"] == week and "Jacksonville Jaguars" in (g["away"], g["home"]))
    out = [p["name"] for p in active if not roster_available(p["availability"], date.fromisoformat(game["date"]), SEASON)]
    groups = sorted(chart["depth"].items(), key=lambda kv: -len(kv[1]))
    depth = 1
    while len(out) < len(active) - RULES.active_limit:
        for _, players in groups:
            if len(out) < len(active) - RULES.active_limit and len(players) > depth + 2:
                name = players[-depth]
                if name not in out:
                    out.append(name)
        depth += 1
    return out


class OpenWeek(unittest.TestCase):
    """A temporary copy with the open week's pages issued (no tests of its own)."""

    def setUp(self):
        self.root = copy_repo(self)
        from scripts import render_game_week
        wk = open_week(self.root)
        if wk.game is None:
            self.skipTest("no Jacksonville game is open")
        with contextlib.redirect_stdout(io.StringIO()):
            render_game_week.write(self.root)
        self.week = wk.game["week"]
        self.pages = week_pages(SEASON, self.week, self.root)
        self.previous = max(w for w in range(1, self.week) if SeasonPaths(SEASON, self.root).call_sheet(w).is_file())

    def check(self):
        from scripts.check_game_plan import check
        return check(self.root, SEASON, self.week)

    def write(self, choices):
        legal = game_plan.legal_lines(7, None, self.previous)
        self.pages.plan.write_text(game_plan.render("Week %d Game Plan" % self.week, "Intro.", choices, legal),
                                   encoding="utf-8")


class CheckTests(OpenWeek):
    def test_the_blank_page_names_what_is_missing(self):
        self.pages.plan.unlink()
        with contextlib.redirect_stdout(io.StringIO()):
            from scripts import render_game_week
            render_game_week.write(self.root)
        problems, _, _ = self.check()
        active = roster_record.players(roster_record.load(SeasonPaths(SEASON, self.root).roster), ("active",))
        self.assertIn("Inactives: none named, %d needed" % (len(active) - RULES.active_limit), problems)
        for name in game_plan.SECTIONS[1:]:
            self.assertTrue(any(p.startswith(name + ": nothing written") for p in problems), name)
        self.assertEqual(page_errors(self.pages.plan.relative_to(self.root).as_posix(),
                                     self.pages.plan.read_text(encoding="utf-8"), root=self.root), [])

    def test_invalid_choices_are_named_in_football_words(self):
        roster = roster_record.load(SeasonPaths(SEASON, self.root).roster)
        names = {p["name"] for p in roster_record.players(roster)}
        self.assertNotIn("Ace Sanders", names)
        six = needed_inactives(self.root, self.week)[:5] + ["Ace Sanders"]
        self.write({"inactives": {"players": six}, "depth": "none", "practice": "none",
                    "offense": {"menus": {"red_zone": "Flood Sail at the 15."},
                                "calls": [{"name": "11 Doubles, Flood Sail", "family": "Flood Sail", "type": "pass",
                                           "personnel": "11", "formation": "11 Doubles", "tags": [],
                                           "menus": ["high red zone"]}]},
                    "fourth_down": "none", "two_point": {"standing": True}, "kickoff": {"standing": True},
                    "defense": {"same_as": self.previous}, "special_teams": "none", "notes": ["Kernel note."]})
        problems, _, _ = self.check()
        needed = len(needed_inactives(self.root, self.week))
        self.assertIn("Inactives: 6 named, %d needed" % needed, problems)
        self.assertIn("Inactives: Ace Sanders is not on the roster", problems)
        self.assertIn("Red zone: 'Flood Sail' is not in the active playbook", problems)
        self.assertIn("Notes to the staff: 'Kernel' is not a football word", problems)

    def test_a_complete_page_checks_applies_and_validates(self):
        from scripts.apply_game_plan import apply
        from scripts.validate_repository import validate
        players = needed_inactives(self.root, self.week)
        self.write({"inactives": {"players": players}, "depth": "none", "practice": ["None beyond the plan."],
                    "offense": {"same_as": self.previous}, "fourth_down": {"standing": True},
                    "two_point": {"standing": True}, "kickoff": {"standing": True},
                    "defense": {"same_as": self.previous}, "special_teams": "none", "notes": "none"})
        problems, _, _ = self.check()
        self.assertEqual(problems, [])
        with contextlib.redirect_stdout(io.StringIO()):
            problems, written = apply(self.root, SEASON, self.week)
        self.assertEqual(problems, [])
        paths = SeasonPaths(SEASON, self.root)
        sheet = json.loads(paths.call_sheet(self.week).read_text(encoding="utf-8"))
        before = json.loads(paths.call_sheet(self.previous).read_text(encoding="utf-8"))
        self.assertEqual(sheet["offensive_call_sheet"], before["offensive_call_sheet"])
        self.assertEqual(sheet["defensive_call_sheet"], before["defensive_call_sheet"])
        self.assertEqual(sheet["decisions"]["two_point"], before["decisions"]["two_point"])
        # Standing rule: the stored fourth-down block, with Tice's first call on each matching menu.
        block = sheet["decisions"]["fourth_down"]
        self.assertEqual({k: v for k, v in block.items() if k != "prepared_calls"}, standing_block(self.root))
        self.assertEqual(block["prepared_calls"], game_plan.first_calls(sheet["offensive_call_sheet"]))
        chart = json.loads(paths.depth_chart.read_text(encoding="utf-8"))
        self.assertEqual(chart["game_day_inactives"]["week"], self.week)
        self.assertEqual(chart["game_day_inactives"]["players"], players)
        queue = json.loads((self.root / "state/decision_queue.json").read_text(encoding="utf-8"))
        settled = [i for i in queue["items"] if i["class"] in ("weekly_game_plan", "game_day_inactives")
                   and any(b.get("week") == self.week for b in i["blocks"])]
        self.assertTrue(settled)
        self.assertTrue(all(i["status"] == "RESOLVED" and i["resolution"]["by"] == "user" for i in settled))
        self.assertEqual(validate(self.root), [])


def standing_block(root=ROOT):
    from runtime import current_job
    job = current_job.load(root)
    rule = next(i for i in current_job.instructions(job) if i["id"] == "stone-fourth-down-rule")
    return rule["block"]


class FourthDownRuleTests(unittest.TestCase):
    """Stone's standing fourth-down rule as a decisions.fourth_down block, against its words:
    "fourth-and-2 or less, go, with Tice's first call on the matching menu; fourth-and-3 or 4, go on
    the opponent's side of midfield, otherwise the field goal or the punt by the field-goal line;
    fourth-and-5 or more, a field goal when the kick is 52 yards or less, otherwise a punt". A kick is
    the line of scrimmage (yards to the goal line) plus the bound artifact's field-goal snap offset."""

    # (yards to go, yards to the goal line, goal to go, decision, why)
    CASES = (
        (1, 70, False, "go", "4th-and-1 at the own 30"),
        (2, 99, False, "go", "4th-and-2 at the own 1"),
        (1, 2, True, "go", "4th-and-1 at the 2, as Week 5 read it"),
        (3, 45, False, "go", "4th-and-3 at the opponent's 45"),
        (4, 26, False, "go", "4th-and-4 at the 26, as Week 5 read it"),
        (4, 49, False, "go", "4th-and-4 at the opponent's 49, past midfield"),
        (3, 50, False, "punt", "4th-and-3 at midfield is not past it: a 68-yard kick"),
        (3, 55, False, "punt", "4th-and-3 at the own 45: the field-goal line, a 73-yard kick"),
        (6, 30, False, "field_goal", "4th-and-6 at the opponent's 30: a 48-yard kick"),
        (6, 34, False, "field_goal", "4th-and-6 at the opponent's 34: a 52-yard kick"),
        (6, 35, False, "punt", "4th-and-6 at the opponent's 35: a 53-yard kick"),
        (6, 40, False, "punt", "4th-and-6 at the opponent's 40: a 58-yard kick"),
        (10, 28, False, "field_goal", "4th-and-10 at the 28: Week 5's 46-yard kick"),
        (5, 37, False, "punt", "4th-and-5 at the 37: Week 5's 55-yard kick"),
        (5, 5, True, "field_goal", "4th-and-goal from the 5: a 23-yard kick"),
    )

    def test_the_block_reads_as_the_words(self):
        from runtime import fourth_down
        block = standing_block()
        for ydstogo, los, goal, expected, why in self.CASES:
            state = {"period": 2, "diff": 0, "seconds": 1800, "ydstogo": ydstogo, "los": los, "goal_to_go": goal}
            decision, basis, call = fourth_down.decide(block, state, 0.5, (1, 1, 1))
            self.assertEqual(decision, expected, why)
            self.assertTrue(basis.startswith("policy:"), why)

    def test_the_field_goal_line_is_the_library_offset(self):
        data = json.loads((ROOT / "library/data/2010_2014w4_fourth_down_decisions.json").read_text(encoding="utf-8"))
        offset = int(data["field_goal_offset"]["modal"])
        kick = next(r for r in standing_block()["rules"] if r["decision"] == "field_goal")
        self.assertEqual(kick["when"]["los"]["max"] + offset, 52)

    def test_the_block_is_valid_with_the_weeks_first_calls(self):
        from runtime import fourth_down
        _, sheet = week5()
        block = dict(standing_block(), prepared_calls=game_plan.first_calls(sheet["offensive_call_sheet"]))
        self.assertEqual(block["prepared_calls"]["third-and-short"], "12 Ace, Power Right")
        self.assertEqual(fourth_down.policy_errors(block, fourth_down.sheet_call_names(sheet["offensive_call_sheet"])),
                         [])


class ParseTests(unittest.TestCase):
    def test_rules_read_back_from_their_football_words(self):
        entry = {"rules": [{"when": {"period": [4], "margin": {"min": -8, "max": -1}, "ydstogo": {"max": 2},
                                     "los": {"max": 35}, "goal_to_go": False, "game_seconds_max": 300},
                            "decision": "go", "call": "12 Ace, Power Right"}],
                 "otherwise": "punt", "prepared": {"third and short": "12 Ace, Power Right"}}
        text = game_plan.render("Plan", "Intro.", {"fourth_down": entry}, game_plan.legal_lines())
        choices, problems = game_plan.parse(text)
        self.assertEqual(problems, [])
        self.assertEqual(choices["fourth_down"], entry)

    def test_a_missing_heading_is_named(self):
        text = game_plan.blank("Plan", "Intro.", game_plan.legal_lines()).replace("## Kickoffs", "## Kicking off")
        _, problems = game_plan.parse(text)
        self.assertIn("Kickoffs: the heading is missing", problems)



# ---------------------------------------------------------------- the review fixes (step 4)
def quiet(call, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()) as out:
        result = call(*args, **kwargs)
    return result, out.getvalue()


class PlanFixTests(OpenWeek):
    """The step-4 review findings on the Game Plan, its check and its apply, each in a copy."""

    def complete(self, **over):
        choices = {"inactives": {"players": needed_inactives(self.root, self.week)}, "depth": "none",
                   "practice": "none", "offense": {"same_as": self.previous}, "fourth_down": {"standing": True},
                   "two_point": {"standing": True}, "kickoff": {"standing": True},
                   "defense": {"same_as": self.previous}, "special_teams": "none", "notes": "none"}
        choices.update(over)
        return choices

    def apply(self):
        from scripts.apply_game_plan import apply
        problems, written = quiet(apply, self.root, SEASON, self.week)[0]
        self.assertEqual(problems, [])
        return written

    def roster(self):
        return roster_record.load(SeasonPaths(SEASON, self.root).roster)

    def chart(self):
        return json.loads(SeasonPaths(SEASON, self.root).depth_chart.read_text(encoding="utf-8"))

    def set_availability(self, names, note):
        path = SeasonPaths(SEASON, self.root).roster
        data = json.loads(path.read_text(encoding="utf-8"))
        for p in data["players"]:
            if p["name"] in names:
                p["availability"] = note
        path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        from scripts import render_game_week
        quiet(render_game_week.write, self.root)

    def game_day(self):
        from datetime import date
        game = next(g for g in SeasonPaths(SEASON, self.root).regular_games()
                    if g["week"] == self.week and "Jacksonville Jaguars" in (g["away"], g["home"]))
        return date.fromisoformat(game["date"])

    def out_note(self):
        from datetime import timedelta
        back = self.game_day() + timedelta(days=30)
        return "Out, short: lower extremity; projected return %s %d, %d" % (back.strftime("%B"), back.day, back.year)

    # GP1: the playbook lock covers every word a call carries.
    def test_gp1_every_word_of_a_call_is_held_to_the_active_book(self):
        sheet = json.loads(SeasonPaths(SEASON, self.root).call_sheet(self.previous).read_text(encoding="utf-8"))
        extra = [{"name": "11 Doubles, READ Glance", "family": "Glance", "type": "pass", "personnel": "11",
                  "formation": "11 Doubles", "target": ["WR"], "tags": [], "menus": ["normal down"]},
                 {"name": "20 TWIN, Dart", "family": "Dart", "type": "run", "personnel": "20", "formation": "20 TWIN",
                  "carrier": ["RB"], "tags": [], "menus": ["normal down"]},
                 {"name": "12 FLEX, Power", "family": "Power", "type": "run", "personnel": "12",
                  "formation": "12 FLEX", "tags": [], "menus": ["normal down"]},
                 {"name": "Moonball Wheel", "family": "Four Verticals", "type": "pass", "personnel": "99",
                  "formation": "Bogus", "protection": "FAKEPRO", "tags": [], "menus": ["normal down"]}]
        menus = {k: v for k, v in sheet["menus"].items() if k not in ("fourth_down", "two_point")}
        self.write(self.complete(offense={"menus": menus, "calls": sheet["offensive_call_sheet"] + extra}))
        problems, _, _ = self.check()
        self.assertIn("Normal downs: 'Glance' is not in the active playbook", problems)
        self.assertIn("Normal downs: 'Dart' is not in the active playbook", problems)
        for words in ("'TWIN' is not a formation word", "'12 FLEX' names no formation", "personnel '99'",
                      "'Bogus' is not a formation word", "'FAKEPRO'", "'Moonball', which is not a word"):
            self.assertTrue(any(words in p for p in problems), words)
        # Every call the club has frozen this season passes the same words.
        from runtime import offensive_words
        names = [p["name"] for p in roster_record.players(self.roster())]
        for week in range(1, self.week):
            path = SeasonPaths(SEASON, self.root).call_sheet(week)
            if path.is_file():
                for call in json.loads(path.read_text(encoding="utf-8"))["offensive_call_sheet"]:
                    self.assertEqual(offensive_words.call_errors(call, names), [], (week, call["name"]))

    # GP2: no plan changes while a game is paused or once the week's game is built.
    def test_gp2_a_paused_or_built_week_is_refused(self):
        from scripts.apply_game_plan import apply
        self.write(self.complete())
        paths = SeasonPaths(SEASON, self.root)
        paused = paths.paused_game(self.week)
        paused.parent.mkdir(parents=True, exist_ok=True)
        paused.write_text(json.dumps({"status": "paused"}), encoding="utf-8")
        problems, _, _ = self.check()
        self.assertEqual(problems, ["A game is paused; the plan stays as it was set until the game is finished"])
        paused.unlink()
        built = paths.cache(self.week, "inputs")
        built.parent.mkdir(parents=True, exist_ok=True)
        built.write_text("{}", encoding="utf-8")
        problems, written = apply(self.root, SEASON, self.week)
        self.assertTrue(problems and "has been built from the applied plan" in problems[0], problems)
        self.assertEqual(written, [])
        self.assertFalse(paths.call_sheet(self.week).exists())

    # GP3, F2, W6-7, W6-12: the page is tied to the sheet it froze; the apply leaves the briefing
    # current, records its event and, applied again, replaces its log entry.
    def test_gp3_f2_the_applied_page_is_tied_to_its_sheet(self):
        from scripts import check_game_plan, render_game_week
        from scripts.validate_repository import validate
        self.write(self.complete())
        self.apply()
        self.assertFalse(any("a new briefing is due" in e for e in render_game_week.check(self.root)))
        self.assertEqual(validate(self.root), [])
        index = self.pages.readme.read_text(encoding="utf-8")
        self.assertIn("-week-%d-game-plan-set" % self.week, index)
        record = SeasonPaths(SEASON, self.root).record("record.md").read_text(encoding="utf-8")
        self.assertIn("Stone set his Week %d Game Plan" % self.week, record.rstrip().splitlines()[-1])
        # The page edited after the apply: validation and the check say so until it is applied again.
        self.write(self.complete(notes=["Keep the walkthrough short."]))
        self.assertTrue(any("has changed since it was applied" in e for e in validate(self.root)))
        code, out = quiet(check_game_plan.main, [str(self.week), "--season", str(SEASON), "--root", str(self.root)])
        self.assertEqual(code, 1)
        self.assertIn("NOT YET SET", out)
        self.apply()
        self.assertEqual(validate(self.root), [])
        sheet = json.loads(self.pages.call_sheet.read_text(encoding="utf-8"))
        self.assertEqual(sheet["notes"], ["Keep the walkthrough short."])
        log = json.loads(SeasonPaths(SEASON, self.root).record("team/depth_chart/update_log.json").read_text(
            encoding="utf-8"))
        self.assertEqual(len([e for e in log["entries"] if e["event"] == "Week %d: Stone's Game Plan" % self.week]), 1)

    # GP4, W6-5, W6-8: a game role does what it says; an order change leaves no view stale and no
    # stale label.
    def test_gp4_w6_5_w6_8_roles_and_orders_reach_the_game(self):
        from scripts.validate_repository import validate
        chart = self.chart()
        backup = chart["depth"]["QB"][1]
        receivers = chart["depth"]["WR"]
        swap = list(receivers)
        swap[2], swap[3] = swap[3], swap[2]
        self.write(self.complete(depth={"orders": {"Wide receivers": swap}, "roles": {"Starter": backup}}))
        self.assertEqual(self.check()[0], [])
        self.apply()
        chart = self.chart()
        self.assertEqual(chart["depth"]["QB"][0], backup)
        self.assertIn("passer", chart["roles"][backup])
        self.assertEqual(chart["depth"]["WR"], swap)
        self.assertEqual(validate(self.root), [])
        page = SeasonPaths(SEASON, self.root).record("depth_chart.md").read_text(encoding="utf-8")
        working = json.loads(SeasonPaths(SEASON, self.root).record("offseason/depth_chart_working.json").read_text(
            encoding="utf-8"))
        labels = {}
        for decision in working["stone_role_decisions"]:
            if decision.get("game_plan_week") == self.week:
                continue
            for row in decision["decisions"]:
                labels[row["player"]] = row["role"]
        for player in swap[2:4]:
            if labels.get(player):
                self.assertNotIn("| %s | WR | %s |" % (player, labels[player]), page)

    def test_gp4_gp8_a_role_goes_to_a_player_of_its_group(self):
        chart = self.chart()
        receiver = chart["depth"]["WR"][-1]
        reserve = next(p for p, roles in chart["roles"].items() if "outside_reserve" in roles)
        self.write(self.complete(depth={"orders": {}, "roles": {"Kicker": receiver, "Nickel": receiver}}))
        problems, _, _ = self.check()
        self.assertIn("Depth chart changes: the Kicker role goes to a player of the K group; %s is not one"
                      % receiver, problems)
        self.assertIn("Depth chart changes: the Nickel role goes to a player of the DB group; %s is not one"
                      % receiver, problems)
        self.write(self.complete(depth={"orders": {}, "roles": {"Nickel": reserve}}))
        problems, _, _ = self.check()
        self.assertIn("Depth chart changes: %s cannot take both the Nickel and the Outside reserve corner seats"
                      % reserve, problems)

    # GP5: a subheading where the readers take none is rejected, not dropped.
    def test_gp5_a_subheading_under_a_plain_section_is_rejected(self):
        self.write(self.complete(notes=["Keep the walkthrough short."]))
        text = self.pages.plan.read_text(encoding="utf-8").replace(
            "\n- Keep the walkthrough short.", "\n### For Tice\n\n- Keep the walkthrough short.")
        self.pages.plan.write_text(text, encoding="utf-8")
        problems, _, _ = self.check()
        self.assertIn("Notes to the staff: write under the heading itself, not under a subheading ('For Tice')",
                      problems)

    # GP6, GP7: Same as Week N carries a rule only when that week froze one.
    def test_gp6_gp7_same_as_a_week_without_the_rule(self):
        paths = SeasonPaths(SEASON, self.root)
        sheets = {w: json.loads(paths.call_sheet(w).read_text(encoding="utf-8")) for w in range(1, self.week)
                  if paths.call_sheet(w).is_file()}
        bare = [w for w, sh in sheets.items() if "two_point" not in (sh.get("decisions") or {})]
        no_fourth = [w for w, sh in sheets.items() if "fourth_down" not in (sh.get("decisions") or {})]
        if bare:
            self.write(self.complete(two_point={"same_as": bare[-1]}))
            problems, _, _ = self.check()
            self.assertTrue(any(p.startswith("Two-point tries: Week %d set no two-point rule" % bare[-1])
                                for p in problems), problems)
        if no_fourth:
            self.write(self.complete(fourth_down={"same_as": no_fourth[-1]}))
            problems, _, _ = self.check()
            self.assertTrue(any(p.startswith("Fourth downs: Week %d froze no fourth-down rule" % no_fourth[-1])
                                for p in problems), problems)
        if not bare and not no_fourth:
            self.skipTest("every earlier week froze every rule")

    # GP9: more players out than the inactive places: the list is those players.
    def test_gp9_more_out_than_the_places(self):
        from scripts.check_game_plan import Plan, inactive_problems
        needed = len(roster_record.players(self.roster(), ("active",))) - RULES.active_limit
        chart = self.chart()
        out = [p for p in chart["depth"]["DB"] + chart["depth"]["LB"] if p in
               {q["name"] for q in roster_record.players(self.roster(), ("active",))}][:needed + 1]
        self.set_availability(out, self.out_note())
        self.write(self.complete(inactives={"players": out}))
        self.assertEqual(inactive_problems(Plan(self.root, SEASON, self.week)), [])
        self.write(self.complete(inactives={"players": out[:needed]}))
        problems = inactive_problems(Plan(self.root, SEASON, self.week))
        self.assertTrue(any("are out for the game, more than the %d inactive places" % needed in p for p in problems))

    # GP10: an availability note the staff cannot read fails the check.
    def test_gp10_an_unreadable_note_is_a_problem(self):
        from scripts.check_game_plan import Plan, inactive_problems
        name = self.chart()["depth"]["WR"][0]
        choices = self.complete()
        self.set_availability([name], "Doubtful with an ankle sprain after the Friday practice")
        self.write(choices)
        problems = inactive_problems(Plan(self.root, SEASON, self.week))
        self.assertTrue(any(p.startswith("Inactives: %s's medical status" % name) for p in problems), problems)

    # GP11: an upload for a played week is refused before anything is written; apply never tracebacks.
    def test_gp11_uploads_are_refused_before_writing(self):
        from scripts import apply_game_plan, check_game_plan
        played = self.previous
        page = week_pages(SEASON, played, self.root).plan
        before = page.read_bytes() if page.is_file() else None
        upload = self.root / "upload.md"
        upload.write_text(self.pages.plan.read_text(encoding="utf-8"), encoding="utf-8")
        code, out = quiet(check_game_plan.main, [str(played), "--season", str(SEASON), "--file", str(upload),
                                                 "--root", str(self.root)])
        self.assertEqual(code, 1)
        self.assertIn("has been played", out)
        self.assertEqual(page.read_bytes() if page.is_file() else None, before)
        pdf = self.root / "upload.pdf"
        pdf.write_text("x", encoding="utf-8")
        code, out = quiet(apply_game_plan.main, [str(self.week), "--season", str(SEASON), "--file", str(pdf),
                                                 "--root", str(self.root)])
        self.assertEqual(code, 1)
        self.assertIn("GAME PLAN: NOT APPLIED", out)

    # GP12: clean-page problems are placed in their own subsection and read in football words.
    def test_gp12_problems_name_their_place(self):
        from scripts.check_game_plan import section_of
        self.write(self.complete(notes=["Run THIRD-AND-3 twice."]))
        problems, _, _ = self.check()
        self.assertIn("Notes to the staff: 'THIRD-AND-3' reads as an internal identifier", problems)
        text = "## Offense\n\n### Opening sequence\n\nline\n\n### Red zone\n\nline\n"
        self.assertEqual(section_of(text, 9), "Offense, Red zone")

    # R5: the defense can be filled from what the page shows.
    def test_r5_the_defense_reads_as_the_page_shows_it(self):
        blank = self.pages.plan.read_text(encoding="utf-8")
        defense = blank.split("## Defense", 1)[1].split("\n## ", 1)[0]
        self.assertIn("**Who calls it:**", defense)
        self.assertIn("**Rush rule:**", defense)
        self.assertNotIn("| Row |", defense)
        self.write(self.complete(defense="none"))
        mine = ("\n\n> legal\n\nWho calls it: Alex Stone\n\nRush rule: Four unless I call the five-man counter\n\n"
                "### Practiced this week\n\n| Menu | Words |\n|---|---|\n| Packages | Base |\n| Fronts | Under |\n"
                "| Coverages | 3 Match |\n| Pressures | Base 4 |\n\n### Calls by situation\n\n"
                "| Use | Situation | Package | Front | Strength | Coverage | Pressure |\n|---|---|---|---|---|---|---|\n"
                "| Situation | Normal downs | Base | Under | Field | 3 Match | Base 4 |\n\n")
        text = self.pages.plan.read_text(encoding="utf-8")
        head, rest = text.split("## Defense", 1)
        self.pages.plan.write_text(head + "## Defense" + mine + "## " + rest.split("\n## ", 1)[1], encoding="utf-8")
        problems, _, plan = self.check()
        self.assertEqual(problems, [])
        ds = plan.sheet()["defensive_call_sheet"]
        from runtime.defensive_calls import RUSH_RULE
        self.assertEqual((ds["caller"], ds["rush_rule"]["rule"], ds["rush_rule"]["source"]["text"]),
                         ("Alex Stone", RUSH_RULE, "Four unless I call the five-man counter"))
        self.assertEqual([r["id"] for r in ds["rows"]], ["normal-down"])
        self.assertIn("third and long", game_plan.legal_lines()["Offense"])

    # R6, W6-10: Standing rule under Inactives.
    def test_r6_standing_rule_for_the_inactives(self):
        from scripts.check_game_plan import Plan, standing_inactives
        needed = len(roster_record.players(self.roster(), ("active",))) - RULES.active_limit
        self.write(self.complete(inactives={"standing": True}))
        plan = Plan(self.root, SEASON, self.week)
        self.assertEqual(plan.choices["inactives"], {"standing": True})
        outs, _ = plan.outs()
        players, problems = standing_inactives(plan)
        if needed - len(outs) != 5:
            self.assertIsNone(players)
            self.assertTrue(problems[0].startswith("Inactives: your standing rule sits 5 healthy players"))
        # Two out for the game leaves five healthy places: the rule names them.
        chart = self.chart()
        active = {q["name"] for q in roster_record.players(self.roster(), ("active",))}
        out = [p for p in chart["depth"]["LB"] if p in active][-(needed - 5):]
        self.set_availability(out, self.out_note())
        self.write(self.complete(inactives={"standing": True}))
        plan = Plan(self.root, SEASON, self.week)
        players, problems = standing_inactives(plan)
        if players is None:
            self.assertTrue("not settled" in problems[0] or "short" in problems[0], problems)
            return
        self.assertEqual(players[:len(out)], [p for p in plan.active() if p in out])
        healthy = {g: [p for p in o if p in active and p not in out] for g, o in chart["depth"].items()}
        largest = sorted((g for g in healthy if healthy[g]), key=lambda g: -len(healthy[g]))[:5]
        self.assertEqual(players[len(out):], [healthy[g][-1] for g in largest])
        problems, _, _ = self.check()
        self.assertEqual(problems, [])

    # F8: Same as Week N carries that week's list as set, whatever the chart holds now.
    def test_f8_same_as_reads_the_weeks_record(self):
        from scripts.check_game_plan import Plan
        self.write(self.complete(inactives={"same_as": 5}))
        self.assertEqual(Plan(self.root, SEASON, self.week).inactives(), WEEK5_INACTIVES)
        chart_path = SeasonPaths(SEASON, self.root).depth_chart
        chart = json.loads(chart_path.read_text(encoding="utf-8"))
        chart["game_day_inactives"] = {"week": self.week, "players": [], "note": "x"}
        chart_path.write_text(json.dumps(chart, indent=1), encoding="utf-8")
        self.assertEqual(Plan(self.root, SEASON, self.week).inactives(), WEEK5_INACTIVES)

    # W6-6: the week's decisions are opened by a tool, and an issued briefing needs them.
    def test_w6_6_the_weeks_items_are_opened(self):
        from scripts import open_game_week, render_career_views
        from scripts.validate_repository import validate
        path = self.root / "state/decision_queue.json"
        queue = json.loads(path.read_text(encoding="utf-8"))
        held = lambda i: any(b.get("week") == self.week and b.get("season") == SEASON for b in i.get("blocks") or ())
        queue["items"] = [i for i in queue["items"] if not (held(i) and i["class"] in
                                                            ("weekly_game_plan", "game_day_inactives"))]
        path.write_text(json.dumps(queue, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        render_career_views.write(self.root)
        self.assertTrue(any("holds no game-plan item" in e for e in validate(self.root)))
        opened = open_game_week.open_items(self.root)
        self.assertEqual(sorted(opened), sorted(["%d-w%02d-game-plan" % (SEASON, self.week),
                                                 "%d-w%02d-inactives" % (SEASON, self.week)]))
        self.assertEqual(open_game_week.open_items(self.root), [])
        render_career_views.write(self.root)
        self.assertEqual([e for e in validate(self.root) if "Decision queue" in e or "game-plan item" in e], [])


class OffensiveWordsTests(unittest.TestCase):
    def test_every_word_is_the_active_books(self):
        from runtime import offensive_words
        mapping = json.loads((ROOT / "docs/repository_map.json").read_text(encoding="utf-8"))
        self.assertIn(offensive_words.PLAYBOOK, mapping["active_playbooks"])
        book = (ROOT / offensive_words.PLAYBOOK).read_text(encoding="utf-8")
        for label, words in offensive_words.BOOK_LISTS.items():
            for word in words:
                parts = r"[\s-]+".join(map(re.escape, word.split()))
                self.assertRegex(book, re.compile(r"(?<![0-9A-Za-z])%s(?![0-9A-Za-z])" % parts, re.I), (label, word))


class MasterDateTests(unittest.TestCase):
    """docs/run_week.md's two master-date forms read alike under every reader of the line."""

    def test_the_documented_forms_parse(self):
        from datetime import datetime
        text = (ROOT / "docs/run_week.md").read_text(encoding="utf-8")
        forms = re.findall(r"`(\| Master date/time \| [^`]+\|)`", text)
        self.assertEqual(len(forms), 2)
        for form, played in zip(forms, (False, True)):
            cell = re.search(r"\| Master date/time \| (.*?) \|", form)[1]
            by_bios = datetime.strptime(re.match(r"[A-Za-z]+ \d{1,2}, \d{4}", cell)[0], "%B %d, %Y").date()
            by_validator = datetime.strptime(cell.split(", after")[0], "%B %d, %Y").date()
            self.assertEqual(by_bios, by_validator)
            self.assertEqual(bool(re.search(r"after the Week (\d+) game", cell)), played)


if __name__ == "__main__":
    unittest.main()
