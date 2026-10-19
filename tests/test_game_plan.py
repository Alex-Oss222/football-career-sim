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
# The Week 5 inactives as Stone set them on October 4, 2014 (the game depth chart's game_day_inactives
# for Week 5). The chart holds only the latest list, so the Week 5 list is kept here as the test's record.
WEEK5_INACTIVES = ["Jordan Poyer", "Malcolm Butler", "Jonathan Grimes", "Corey Linsley", "Kasim Edebali",
                   "Taylor Gabriel", "Gator Hoskins"]


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

    def test_the_chart_held_the_week_5_list(self):
        chart = json.loads(SeasonPaths(SEASON, ROOT).depth_chart.read_text(encoding="utf-8"))
        listed = chart["game_day_inactives"]
        if listed["week"] == 5:
            self.assertEqual(listed["players"], WEEK5_INACTIVES)

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


class CheckTests(unittest.TestCase):
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
                    "offense": {"same_as": self.previous}, "fourth_down": {"same_as": self.previous},
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
        chart = json.loads(paths.depth_chart.read_text(encoding="utf-8"))
        self.assertEqual(chart["game_day_inactives"]["week"], self.week)
        self.assertEqual(chart["game_day_inactives"]["players"], players)
        queue = json.loads((self.root / "state/decision_queue.json").read_text(encoding="utf-8"))
        settled = [i for i in queue["items"] if i["class"] in ("weekly_game_plan", "game_day_inactives")
                   and any(b.get("week") == self.week for b in i["blocks"])]
        self.assertTrue(settled)
        self.assertTrue(all(i["status"] == "RESOLVED" and i["resolution"]["by"] == "user" for i in settled))
        self.assertEqual(validate(self.root), [])


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


if __name__ == "__main__":
    unittest.main()
