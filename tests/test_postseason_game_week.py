"""A playoff game through the three game-week pages, end to end in a temporary copy
(game week version 2, Phase C; docs/game_week_v2.md, section 7).

The copy's regular season is cut short so that its closed games set a playoff field: the released
fixtures keep only the first weeks, the closed games after them are removed, and a postseason
slots file is written beside the real 2013 one, in its layout, with fixture dates the week after the
copy's clock (the 2014 file is not yet researched; nothing here is a real 2014 date or result).
With three weeks Jacksonville is the AFC's first seed: it has a Wild Card bye, and no Divisional
page is issued while the Wild Card games are unplayed. With two weeks it is the third seed and
hosts Pittsburgh in the Wild Card round. Then, the way the weekly workflow runs a game week:

- briefing: render_game_week.py opens the week's two decision items and issues the Game Week
  Briefing (with the playoff game's own facts), the blank Game Plan and the index in the round's
  folder under the postseason folder, through the folder map;
- check and apply: a complete version 2 Game Plan (Baseline: Carry Week 5, the standing two-point
  and kickoff rules, fourth downs left to the live call, the inactives named) checks and,
  once the exams the items wait on are held, applies: the call sheet is frozen in the postseason
  folder's data twin, where the weekly build looks for it, and the items are settled;
- close and report: the copy's Week 5 game record becomes the Wild Card game (Pittsburgh at
  Jacksonville, the same clubs), the playoff acceptance fixture is written as its Game Report, the
  rebuild's box-score step names its markers and fills the game book last, and every Game Report
  check passes;
- after the loss: no later game is opened and no page is issued.

No game is played, the private service is never contacted and the real repository is never touched.
"""
import contextlib
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import clean_pages, game_plan, game_report, game_weeks  # noqa: E402
from runtime.decisions import week_pages  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402
from runtime.week_inputs import receipt_name  # noqa: E402

JAX, PIT = "Jacksonville Jaguars", "Pittsburgh Steelers"
SEASON, WILD_CARD, DIVISIONAL = 2014, 18, 19
IGNORED = (".git", ".sim_cache", "__pycache__", ".pytest_cache")
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "game_reports" / "playoff_game.md"
# The receipt fields tied to the week a game was played under (tests/test_week_close_pages.py).
WEEK_BOUND = ("defensive_calls", "defensive_call_stats", "decision_policies")
# Fixture slot dates (the copy's clock is October 5, 2014): the rounds on the weekends after it.
SLOT_DATES = {"2014-01-04": "2014-10-11", "2014-01-05": "2014-10-12", "2014-01-11": "2014-10-18",
              "2014-01-12": "2014-10-19", "2014-01-19": "2014-10-26", "2014-02-02": "2014-11-09"}


def quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


class PostseasonGameWeekTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT.parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(*IGNORED), symlinks=True)
        self.paths = SeasonPaths(SEASON, self.root)
        self.week5 = json.loads((self.paths.receipts / "week_05_pittsburgh_steelers_at_jacksonville_jaguars.json")
                                .read_text(encoding="utf-8"))
        self.real = sorted(p.name for p in SeasonPaths(SEASON, ROOT).receipts.glob("*.json"))

    # ---------------------------------------------------------------- the copy's season
    def write_slots(self):
        slots = json.loads((ROOT / "library/data/2013_postseason_slots.json").read_text(encoding="utf-8"))
        text = json.dumps(dict(slots, season=SEASON, note="Test fixture slots: not real 2014 dates."))
        for old, new in SLOT_DATES.items():
            text = text.replace(old, new)
        self.paths.postseason_slots.write_text(text, encoding="utf-8")

    def end_season_after(self, last):
        """The copy's regular season as its first ``last`` weeks: the later fixtures and closed games go
        (their pages stay, as other pages link to them)."""
        path = self.paths.schedule
        data = json.loads(path.read_text(encoding="utf-8"))
        keep = [g for g in data["games"] if g["week"] <= last]
        ids = {g["game_id"] for g in keep}
        data.update(games=keep, amendments=[a for a in data.get("amendments") or () if a.get("game_id") in ids])
        path.write_text(json.dumps(data, indent=1), encoding="utf-8")
        for receipt in self.paths.receipts.glob("week_*.json"):
            if int(receipt.name[5:7]) > last:
                receipt.unlink()

    def inactives(self, plan):
        """A legal list from the stored facts: every player out for the game, then the deepest reserve
        of the largest groups (tests/test_game_plan.needed_inactives, for a playoff game's date)."""
        outs, problems = plan.outs()
        self.assertEqual(problems, [])
        active = plan.active()
        out = [p for p in active if p in outs]
        groups = sorted(plan.chart["depth"].items(), key=lambda kv: -len(kv[1]))
        depth = 1
        while len(out) < plan.needed():
            for _, players in groups:
                if len(out) < plan.needed() and len(players) > depth + 2:
                    name = players[-depth]
                    if name in active and name not in out:
                        out.append(name)
            depth += 1
        return out

    def exams_held(self):
        """The exams the week's items wait on, held: each dated wait moved to the day before today (the
        clock stays), and the briefing re-issued for the changed situation (tests/test_game_plan.py)."""
        from runtime.player_bios import master_date
        from scripts import render_game_week
        path = self.root / "state/decision_queue.json"
        queue = json.loads(path.read_text(encoding="utf-8"))
        before = (master_date(self.root) - timedelta(days=1)).isoformat()
        for item in queue["items"]:
            if any(b.get("week") == WILD_CARD for b in item.get("blocks") or ()):
                for wait in item.get("waits_on") or ():
                    if wait.get("date"):
                        wait["date"] = before
        path.write_text(json.dumps(queue, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        quiet(render_game_week.write, self.root)

    def close_wild_card(self, game):
        """The copy's Week 5 game record, as the Wild Card game: the same clubs, sides and play."""
        receipt = {k: v for k, v in self.week5.items() if k not in WEEK_BOUND}
        receipt.update(week=WILD_CARD, game_type="postseason", event_id=game["game_id"])
        folder = self.paths.postseason_receipts
        folder.mkdir(parents=True, exist_ok=True)
        (folder / receipt_name(game)).write_text(json.dumps(receipt, indent=1), encoding="utf-8")
        state = self.root / "state/05_Current_Season_State.md"
        text, n = re.subn(r"(\| Master date/time \| )[A-Za-z]+ \d{1,2}, \d{4}[^|]*\|",
                          r"\g<1>October 12, 2014, after the Wild Card game against Pittsburgh |",
                          state.read_text(encoding="utf-8"), count=1)
        self.assertEqual(n, 1)
        state.write_text(text, encoding="utf-8")
        return receipt

    # ---------------------------------------------------------------- the test
    def test_a_playoff_game_runs_through_the_three_pages(self):
        from scripts import apply_game_plan, check_game_plan, open_game_week, render_box_score
        from scripts import render_coach_record, render_game_week
        root, paths = self.root, self.paths
        post_folder = paths.postseason

        # Mid-season, no playoff game exists: no opponent is named before the bracket sets it.
        with self.assertRaises(game_weeks.NotSet):
            game_weeks.club_game(paths, WILD_CARD, JAX)
        with self.assertRaises(ValueError):
            render_game_week.Week(root, WILD_CARD)
        self.write_slots()

        # A first-round bye: no Wild Card pages, and the Divisional game waits for the Wild Card results.
        self.end_season_after(3)
        self.assertEqual(game_weeks.seed_of(game_weeks.regular_receipts(paths), JAX), ("AFC", 1))
        wk = render_game_week.Week(root)
        self.assertIsNone(wk.game)
        self.assertIn("Divisional", wk.waiting)
        self.assertEqual(quiet(render_game_week.write, root), [])
        self.assertFalse(any(post_folder.glob("Week_*")))
        problems, _, _ = check_game_plan.check(root, SEASON, DIVISIONAL)
        self.assertTrue(problems[0].startswith("Divisional: Jacksonville's game is not set yet"), problems)

        # The third seed hosts the sixth: Pittsburgh at Jacksonville in the Wild Card round.
        self.end_season_after(2)
        wk = render_game_week.Week(root)
        game = wk.game
        self.assertEqual((game["week"], game["away"], game["home"], game["round_name"]), (WILD_CARD, PIT, JAX, "Wild Card"))
        self.assertEqual((game["home_seed"], game["away_seed"], game["stadium"]), (3, 6, "EverBank Field"))
        self.assertTrue(wk.postseason and not wk.closed)

        # Briefing: the round's folder under the postseason folder, through the folder map.
        written = quiet(render_game_week.write, root)
        pages = week_pages(SEASON, WILD_CARD, root)
        self.assertEqual(pages.folder, paths.week_folder(WILD_CARD, postseason=True))
        self.assertTrue(pages.folder.is_relative_to(post_folder) and pages.data.is_relative_to(paths.data))
        for page in (pages.briefing, pages.plan, pages.readme):
            self.assertIn(page, written)
        self.assertFalse(paths.week_folder(WILD_CARD).exists())
        briefing = pages.briefing.read_text(encoding="utf-8")
        self.assertTrue(briefing.startswith("# Wild Card Game Week Briefing: Pittsburgh\n"))
        # The playoff game's own facts are section 1's rows, in place of the regular season's standings.
        section = briefing.split("## 1. The game and what is at stake", 1)[1].split("\n## 2.", 1)[0]
        for text in ("| Game type | Wild Card, AFC |", "| Seeds | Jacksonville No. 3, Pittsburgh No. 6 |",
                     "| Venue and kickoff | EverBank Field, ", "Jacksonville: ", "since its Week 2 game, at home",
                     "| If we lose | The season is over. |", "| If we win | We play in the Divisional round",
                     "| Earlier meeting |", "A playoff game cannot end tied", "first possession",
                     "| Game-day roster | 46 dress"):
            self.assertIn(text, section)
        self.assertNotIn("| Stakes |", section)
        self.assertEqual(clean_pages.page_errors(pages.briefing.relative_to(root).as_posix(), briefing, root=root), [])
        self.assertTrue(pages.plan.read_text(encoding="utf-8").startswith("# Wild Card Game Plan: Pittsburgh\n"))
        self.assertTrue(pages.readme.read_text(encoding="utf-8").startswith("# Wild Card: Pittsburgh\n"))
        queue = json.loads((root / "state/decision_queue.json").read_text(encoding="utf-8"))
        items = [i for i in queue["items"] if any(b.get("week") == WILD_CARD for b in i["blocks"])]
        self.assertEqual(sorted(i["title"] for i in items), ["Wild Card game plan for Pittsburgh", "Wild Card inactives"])
        self.assertEqual(open_game_week.missing(root)[0], [])
        self.assertEqual(render_game_week.check(root), [])

        # Check and apply: the page's choices into the call sheet in the postseason folder's data twin.
        plan = check_game_plan.Plan(root, SEASON, WILD_CARD)
        players = self.inactives(plan)
        answers = {
            "baseline": "Carry Week 5", "attack": "Their linebackers in space against our tight ends.",
            "protect": "A cutback behind an overrun.", "change_course": "A safety rotating late to the second tight end.",
            "inactives": ", ".join(players), "depth": "No change", "contingency": "None",
            "coverage_units": "No change", "offense_caller": "No change", "base_personnel": "Twelve personnel leads.",
            "learn": "Who travels with the second tight end.", "opening_approach": "As in Week 5.",
            "opening": "Carry Week 5 opening", "third_down": "No change", "backed_up": "No change",
            "red_zone": "No change", "two_minute": "No change", "four_minute": "No change",
            "sudden_change": "No change", "special_plays": "No change", "not_available": "None",
            "defense_caller": "No change", "front": "Force and cutback first.", "coverage": "Quarters and 6.",
            "rush": game_plan.RUSH_CHOICE, "discover": "Their protection against the replaced rusher.",
            "matchups": "No change", "kicking_caller": "No change", "kicking": "No change",
            "fourth_down": "None", "two_point": "Standing rule", "kickoff": "Standing rule",
            "endgame": "No change", "participation": "None", "tradeoff": "None", "staff": "None",
            "public": "No new statement", "open_decisions": "None", "ready": "None",
            "practice": [["Third down", "Tice with the offense", "Third and medium", "The Saturday walkthrough"]]}
        facts = render_game_week.plan_facts(render_game_week.Week(root, WILD_CARD))
        pages.plan.write_text(game_plan.render("Wild Card Game Plan: Pittsburgh", facts, answers), encoding="utf-8")
        problems, _, _ = check_game_plan.check(root, SEASON, WILD_CARD)
        self.assertEqual(problems, [])
        self.exams_held()
        # He answers the briefing re-issued after the exams: the same choices, its issue on Briefing used.
        facts = render_game_week.plan_facts(render_game_week.Week(root, WILD_CARD))
        pages.plan.write_text(game_plan.render("Wild Card Game Plan: Pittsburgh", facts, answers), encoding="utf-8")
        problems, written = quiet(apply_game_plan.apply, root, SEASON, WILD_CARD, rebuild_pages=False)
        self.assertEqual(problems, [])
        sheet_path = paths.call_sheet(WILD_CARD, postseason=True)
        self.assertIn(sheet_path, written)
        # The weekly build finds exactly this sheet (scripts/build_week_inputs.py looks in both folders).
        self.assertEqual([p for p in (paths.call_sheet(WILD_CARD), sheet_path) if p.exists()], [sheet_path])
        sheet = json.loads(sheet_path.read_text(encoding="utf-8"))
        week5 = json.loads(paths.call_sheet(5).read_text(encoding="utf-8"))
        self.assertEqual(sheet["event"], "2014 postseason Wild Card, Pittsburgh at Jacksonville, October 12, 2014")
        # Week 5's calls carried as set; its "what I am looking at" text is author intent, not the sheet's.
        strip = lambda calls: [{k: v for k, v in c.items() if k != "what_stone_is_looking_at"} for c in calls]
        self.assertEqual(sheet["offensive_call_sheet"], strip(week5["offensive_call_sheet"]))
        self.assertEqual(sheet["defensive_call_sheet"]["rows"], week5["defensive_call_sheet"]["rows"])
        self.assertNotIn("fourth_down", sheet["decisions"])
        chart = json.loads(paths.depth_chart.read_text(encoding="utf-8"))
        self.assertEqual(chart["game_day_inactives"]["week"], WILD_CARD)
        self.assertEqual(chart["game_day_inactives"]["players"], players)
        queue = json.loads((root / "state/decision_queue.json").read_text(encoding="utf-8"))
        settled = [i for i in queue["items"] if any(b.get("week") == WILD_CARD for b in i["blocks"])]
        self.assertTrue(settled and all(i["status"] == "RESOLVED" and i["resolution"]["by"] == "user" for i in settled))
        self.assertEqual(apply_game_plan.validation_errors(root), [])
        quiet(render_game_week.write_index, root, WILD_CARD)
        self.assertIn("Set for the game", pages.readme.read_text(encoding="utf-8"))
        self.assertEqual(render_game_week.check(root, WILD_CARD), [])

        # Game day: the Game Report opened with its preparation and pregame media, frozen before kickoff.
        from scripts import freeze_pregame
        report = FIXTURE.read_text(encoding="utf-8")
        head, *sections = report.split("\n## ")
        head = re.sub(r"^\*\*Final: .*\n", "", head + "\n", flags=re.M).rstrip("\n")
        pregame = "\n## ".join([head] + [part for part in sections if part.startswith(("1. ", "2. "))]) + "\n"
        pages.report.write_text(pregame, encoding="utf-8")
        self.assertEqual(freeze_pregame.freeze(root, SEASON, WILD_CARD), pages.pregame)
        frozen = json.loads(pages.pregame.read_text(encoding="utf-8"))
        self.assertEqual(sorted(frozen["sections"]), sorted(game_report.PREGAME))
        self.assertEqual(game_report.validation_errors(root), [])

        # Close and report: the Game Report in the round's folder, its box score named and filled last.
        receipt = self.close_wild_card(game)
        self.assertEqual(check_game_plan.check(root, SEASON, WILD_CARD)[0], ["Wild Card has been played; its plan stays "
                                                                             "as it was set"])
        with self.assertRaises(ValueError):
            freeze_pregame.freeze(root, SEASON, WILD_CARD)      # after the game, nothing is frozen
        coach_record = render_coach_record.render(SEASON, PIT, root)
        self.assertIn("## Coach record\n\n%s\n" % coach_record, report)     # the table the coach record prints
        self.assertEqual(pages.report, paths.game_report(WILD_CARD, postseason=True))
        pages.report.write_text(report, encoding="utf-8")
        # The rebuild's box-score step for this page (scripts/rebuild_pages.box_scores; the copy's cut
        # weeks keep result pages whose games it no longer holds, so the step is run on this page).
        named = render_box_score.named(pages.report, SEASON, root)
        pages.report.write_text(render_box_score.fill(named, paths.receipts, SEASON, report=True), encoding="utf-8")
        text = pages.report.read_text(encoding="utf-8")
        self.assertNotIn(game_report.EVENT_PLACEHOLDER, text)
        self.assertEqual(game_report.report_errors(text, receipt, game, root=root), [])
        self.assertEqual(game_report.validation_errors(root), [])
        # The pregame media rewritten once the result is known is refused.
        changed = text.replace("No pregame media session was recorded.",
                               "No pregame media session was recorded; the staff expected a long afternoon.", 1)
        self.assertNotEqual(changed, text)
        pages.report.write_text(changed, encoding="utf-8")
        self.assertTrue(any("differs from the section frozen before kickoff" in e
                            for e in game_report.validation_errors(root)), game_report.validation_errors(root))
        pages.report.write_text(text, encoding="utf-8")
        self.assertEqual(render_box_score.stale_blocks(pages.report, paths.receipts, season=SEASON), [])
        self.assertEqual(clean_pages.page_errors(pages.report.relative_to(root).as_posix(), text, root=root), [])
        block = game_report.BLOCK.search(text)
        self.assertEqual(block.group("event"), game["game_id"])
        self.assertEqual(text[block.end():].strip(), "")
        for target in re.findall(r"\]\(([^)#]+)", text.split("\n## Full game statistics", 1)[0]):
            self.assertTrue((pages.folder / target).resolve().is_file(), target)
        quiet(render_game_week.write_index, root, WILD_CARD)
        self.assertIn("| Written |", pages.readme.read_text(encoding="utf-8"))
        self.assertEqual(render_game_week.check(root, WILD_CARD), [])

        # After the loss: no later game, no page and no item.
        wk = render_game_week.Week(root)
        self.assertIsNone(wk.game)
        self.assertIn("beaten in the Wild Card round", wk.waiting)
        self.assertEqual(quiet(render_game_week.write, root), [])
        self.assertEqual(open_game_week.missing(root)[0], [])
        self.assertEqual(sorted(p.name for p in post_folder.glob("Week_*")), ["Week_18"])
        self.assertEqual(render_game_week.validation_errors(root), [])

        # Isolation: nothing reached the real season.
        self.assertFalse(SeasonPaths(SEASON, ROOT).postseason_slots.exists())
        self.assertEqual(sorted(p.name for p in SeasonPaths(SEASON, ROOT).receipts.glob("*.json")), self.real)


    # ---------------------------------------------------------------- the later rounds
    def receipt_of(self, week):
        """A closed regular-season game record of the copy, before the season is cut short."""
        folder = self.paths.receipts
        return {p.name: json.loads(p.read_text(encoding="utf-8")) for p in folder.glob("week_%02d_*.json" % week)}

    def close_round(self, week, templates):
        """Every game of postseason ``week`` closed in the copy: Jacksonville's from a Jacksonville win on
        the same side (``templates``: its home and away win records), every other game a home win, each
        a closed record relabelled onto the bracket's clubs (tests/test_week_close_pages.relabel)."""
        from test_week_close_pages import relabel
        folder = self.paths.postseason_receipts
        folder.mkdir(parents=True, exist_ok=True)
        ours = None
        for game in game_weeks.bracket(self.paths, week):
            side = "home" if game["home"] == JAX else "away" if game["away"] == JAX else None
            template = templates[side] if side else templates["other"]
            other_side = "away" if side == "home" else "home"
            if side:
                names = {template[other_side]: game[other_side]}
            else:
                names = {template["away"]: game["away"], template["home"]: game["home"]}
            receipt = relabel({k: v for k, v in template.items() if k not in WEEK_BOUND}, names)
            receipt.update(week=week, game_type="postseason", event_id=game["game_id"],
                           matchup="%s at %s" % (game["away"], game["home"]))
            self.assertEqual((receipt["away"], receipt["home"]), (game["away"], game["home"]))
            (folder / receipt_name(game)).write_text(json.dumps(receipt, indent=1), encoding="utf-8")
            if side:
                ours = (game, receipt)
        from runtime import postseason
        self.assertEqual(postseason.winner(ours[1]), JAX)
        return ours

    def set_master(self, text):
        state = self.root / "state/05_Current_Season_State.md"
        new, n = re.subn(r"(\| Master date/time \| )[A-Za-z]+ \d{1,2}, \d{4}[^|]*\|", r"\g<1>%s |" % text,
                         state.read_text(encoding="utf-8"), count=1)
        self.assertEqual(n, 1)
        state.write_text(new, encoding="utf-8")

    def plan_round(self, week, carry):
        """The round's briefing issued, a version 2 Game Plan carrying ``carry`` checked and applied, and
        its call sheet frozen in the postseason folder's data twin; returns (briefing, sheet)."""
        from scripts import apply_game_plan, check_game_plan, render_game_week
        root = self.root
        quiet(render_game_week.write, root)
        pages = week_pages(SEASON, week, root)
        self.assertEqual(pages.folder, self.paths.week_folder(week, postseason=True))
        plan = check_game_plan.Plan(root, SEASON, week)
        answers = {
            "baseline": "Carry Week %d" % carry, "attack": "Their linebackers in space against our tight ends.",
            "protect": "A cutback behind an overrun.", "change_course": "A safety rotating late.",
            "inactives": ", ".join(self.inactives(plan)), "depth": "No change", "contingency": "None",
            "coverage_units": "No change", "offense_caller": "No change", "base_personnel": "Twelve personnel leads.",
            "learn": "Who travels with the second tight end.", "opening_approach": "As before.",
            "opening": "Carry Week %d opening" % carry, "third_down": "Carry Week %d" % carry, "backed_up": "No change",
            "red_zone": "No change", "two_minute": "No change", "four_minute": "No change",
            "sudden_change": "No change", "special_plays": "No change", "not_available": "None",
            "defense_caller": "No change", "front": "Force and cutback first.", "coverage": "Quarters and 6.",
            "rush": game_plan.RUSH_CHOICE, "discover": "Their protection.", "matchups": "No change",
            "kicking_caller": "No change", "kicking": "No change", "fourth_down": "None",
            "two_point": "Standing rule", "kickoff": "Standing rule", "endgame": "No change", "participation": "None",
            "tradeoff": "None", "staff": "None", "public": "No new statement", "open_decisions": "None",
            "ready": "All decisions settled",
            "practice": [["Third down", "Tice with the offense", "Third and medium", "The Saturday walkthrough"]]}
        facts = render_game_week.plan_facts(render_game_week.Week(root, week))
        title = pages.plan.read_text(encoding="utf-8").splitlines()[0][2:]
        pages.plan.write_text(game_plan.render(title, facts, answers), encoding="utf-8")
        self.assertEqual(check_game_plan.check(root, SEASON, week)[0], [])
        problems, written = quiet(apply_game_plan.apply, root, SEASON, week, rebuild_pages=False)
        self.assertEqual(problems, [])
        sheet_path = self.paths.call_sheet(week, postseason=True)
        self.assertIn(sheet_path, written)
        self.assertFalse(self.paths.call_sheet(week).exists())
        self.assertEqual(apply_game_plan.validation_errors(root), [])
        quiet(render_game_week.write_index, root, week)
        briefing = pages.briefing.read_text(encoding="utf-8")
        self.assertEqual(clean_pages.page_errors(pages.briefing.relative_to(root).as_posix(), briefing, root=root), [])
        return briefing.split("## 1. The game and what is at stake", 1)[1].split("\n## 2.", 1)[0], \
            json.loads(sheet_path.read_text(encoding="utf-8"))

    def test_the_later_rounds_run_through_the_same_pages(self):
        """Divisional, Conference Championship and Super Bowl games through the same briefing, Game Plan,
        check and apply, each on the matchup the round before it set: a later round carries an earlier
        round's plan, and the Super Bowl is at a neutral site."""
        wins = {"home": self.receipt_of(3)["week_03_indianapolis_colts_at_jacksonville_jaguars.json"],
                "away": self.receipt_of(2)["week_02_jacksonville_jaguars_at_washington_redskins.json"]}
        other = next(r for r in self.receipt_of(1).values() if JAX not in (r["away"], r["home"])
                     and r["final_score"][r["home"]] > r["final_score"][r["away"]])
        wins["other"] = other
        self.write_slots()
        self.end_season_after(2)
        root, paths = self.root, self.paths
        week5 = json.loads(paths.call_sheet(5).read_text(encoding="utf-8"))
        # The game path dates a closed playoff game from the bracket of its own repository
        # (runtime/week_inputs._game_dates through runtime/postseason.schedule); here that is the copy.
        from unittest.mock import patch
        from runtime import postseason, week_inputs
        for module in (postseason, week_inputs):
            patcher = patch.object(module, "ROOT", root)
            patcher.start()
            self.addCleanup(patcher.stop)

        # The Wild Card round, closed: Jacksonville beats Pittsburgh at home; every other host wins.
        game, _ = self.close_round(WILD_CARD, wins)
        self.assertEqual((game["away"], game["home"]), (PIT, JAX))
        self.set_master("October 12, 2014, after the Wild Card game against Pittsburgh")

        # Divisional: set only now, Jacksonville at the second seed, which had the first-round bye.
        game = game_weeks.club_game(paths, DIVISIONAL, JAX)
        self.assertEqual((game["round_name"], game["away"], game["away_seed"], game["home_seed"]),
                         ("Divisional", JAX, 3, 2))
        host = game["home"]
        section, sheet = self.plan_round(DIVISIONAL, 5)
        for text in ("| Game type | Divisional, AFC |", "| Seeds | Jacksonville No. 3, %s No. 2 |" % host.rsplit(" ", 1)[0],
                     "Jacksonville: 6 days since its Wild Card game, on the road",
                     "since its Week 2 game after its bye, at home",
                     "| If we win | We play in the Conference Championship", "| If we lose | The season is over. |",
                     "A playoff game cannot end tied", "| Game-day roster | 46 dress"):
            self.assertIn(text, section)
        strip = lambda calls: [{k: v for k, v in c.items() if k != "what_stone_is_looking_at"} for c in calls]
        self.assertEqual(sheet["offensive_call_sheet"], strip(week5["offensive_call_sheet"]))
        self.assertTrue(sheet["event"].startswith("2014 postseason Divisional, Jacksonville at "))
        self.close_round(DIVISIONAL, wins)
        self.set_master("October 19, 2014, after the Divisional game at %s" % host.rsplit(" ", 1)[0])

        # Conference Championship: carrying the Divisional round's plan as set.
        game = game_weeks.club_game(paths, 20, JAX)
        self.assertEqual((game["round_name"], game["away"], game["home_seed"]), ("Conference Championship", JAX, 1))
        section, conference = self.plan_round(20, DIVISIONAL)
        self.assertIn("| Game type | Conference Championship, AFC |", section)
        self.assertIn("| If we win | We play in the Super Bowl", section)
        days = (date.fromisoformat(game["date"]) - date.fromisoformat(
            game_weeks.club_game(paths, DIVISIONAL, JAX)["date"])).days
        self.assertIn("Jacksonville: %d days since its Divisional game, on the road" % days, section)
        self.assertEqual(conference["offensive_call_sheet"], sheet["offensive_call_sheet"])
        self.assertEqual(conference["defensive_call_sheet"]["rows"], sheet["defensive_call_sheet"]["rows"])
        self.close_round(20, wins)
        self.set_master("October 26, 2014, after the Conference Championship game at %s"
                        % game["home"].rsplit(" ", 1)[0])

        # The Super Bowl: the two champions at a neutral site, Jacksonville the designated home club.
        game = game_weeks.club_game(paths, 21, JAX)
        self.assertEqual((game["round_name"], game["home"], game["site"], game["stadium"]),
                         ("Super Bowl", JAX, "neutral", "MetLife Stadium"))
        section, final = self.plan_round(21, 20)
        for text in ("| Game type | Super Bowl |", "| Venue and kickoff | MetLife Stadium, ",
                     "Jacksonville: 14 days since its Conference Championship game, at a neutral site",
                     "since its Conference Championship game, at a neutral site",
                     "| If we win | We are the league champions. |", "| Earlier meeting | None this season. |"):
            self.assertIn(text, section)
        self.assertNotIn("at home", section.split("| Rest and travel |", 1)[1].split("\n", 1)[0])
        self.assertEqual(final["event"], "2014 postseason Super Bowl, %s at Jacksonville, November 9, 2014"
                         % game["away"].rsplit(" ", 1)[0])
        self.assertEqual(final["offensive_call_sheet"], sheet["offensive_call_sheet"])
        from scripts import render_game_week
        self.assertEqual(render_game_week.validation_errors(root), [])
        self.assertEqual(sorted(p.name for p in paths.postseason.glob("Week_*")), ["Week_19", "Week_20", "Week_21"])
        # Isolation: nothing reached the real season.
        self.assertFalse(SeasonPaths(SEASON, ROOT).postseason_slots.exists())


if __name__ == "__main__":
    unittest.main()
