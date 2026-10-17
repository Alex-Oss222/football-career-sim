"""Kernel 2014.6 W1a: the defensive call record (records only).

Stone's structured defensive sheet labels each defensive snap of the club
carrying it with the sheet's applicable row, deterministically, after the
game has resolved (runtime/defensive_calls.py). These tests hold the sheet's
vocabulary to the active defensive book (read through the playbook lock),
the validator's encoding rules, the snap situations, the kernel's record and
its coherence classes, the invariance of every outcome, possession and
exposure with and without a sheet (and with the sheet on the other club),
the packets, the week inputs, the closure and resume path, the receipts and
statistics, and the repository check. Synthetic fixture sheet and clubs
only; no week's sheet is read or written and no 2014 game is closed.
"""
import contextlib
import copy
import dataclasses
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from datetime import date
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import call_situations as cs
from runtime import defensive_calls as dc
from runtime import game_runner, kernel
from runtime.kernel import decision_block_errors, resolve_game, validate_result
from runtime.play_detail import audit_only_errors, check_ledger, measurable_classes
from runtime.profiles import PROFILE_2014_5, PROFILE_2014_6
from runtime.statbook import aggregate_receipts, make_receipt
from synthetic_games import SEED, sample_teams

FIXTURE = ROOT / "tests/data/defensive_sheet_fixture.json"
GAMES = 4


def fixture_sheet(team="A"):
    sheet = json.loads(FIXTURE.read_text(encoding="utf-8"))
    sheet["team"] = team
    return sheet


def stripped(result):
    """A result without the W1a record: the labels, the record and the stats."""
    out = json.loads(json.dumps(result, default=str))
    out.pop("defensive_calls", None)
    out.pop("defensive_call_stats", None)
    for row in out["play_ledger"]:
        for field in dc.FIELDS:
            row.pop(field, None)
    return out


def exposure(result):
    return {t: {p: (line.get("offensive_snaps"), line.get("defensive_snaps"), line.get("special_teams_snaps"))
                for p, line in s["players"].items()} for t, s in result["team_stats"].items()}


def play(home, away, i, **kw):
    return resolve_game(home, away, seed=SEED + b"-w1a-%05d" % i, event_id="w1a-%d" % i,
                        _test_profile=kw.pop("profile", PROFILE_2014_6), **kw)


def book_text():
    return (ROOT / dc.active_defensive_book()).read_text(encoding="utf-8")


def section(text, start, end):
    return text[text.index(start):text.index(end, text.index(start))]


def table_column(block):
    rows = [line for line in block.splitlines() if line.startswith("|")]
    return [line.split("|")[1].strip() for line in rows[2:]]


class VocabularyTests(unittest.TestCase):
    """The sheet's words are the active defensive book's, read only through
    the playbook lock (docs/repository_map.json active_playbooks)."""

    def test_the_active_book_is_read_through_the_lock(self):
        mapping = json.loads((ROOT / "docs/repository_map.json").read_text())
        book = dc.active_defensive_book()
        self.assertIn(book, mapping["active_playbooks"])
        self.assertIn("defensive", book)
        head = book_text().split("\n---", 1)[0]
        start, end = dc._effective_seasons(head)
        self.assertTrue(start <= 2014 <= end)

    def test_pressure_families_are_section_8s_six(self):
        families = table_column(section(book_text(), "# 8. RUSH AND PRESSURE SYSTEM", "## 8.1"))
        self.assertEqual(families, list(dc.PRESSURE_FAMILIES.values()))
        self.assertEqual(len(families), 6)

    def test_fronts_coverage_families_strengths_coverages_and_packages(self):
        text = book_text()
        self.assertEqual(table_column(section(text, "# 5. FRONT ARCHITECTURE", "## 5.1")), list(dc.FRONTS))
        self.assertEqual(table_column(section(text, "## 10.1 Coverage Families", "## 10.2")),
                         list(dc.COVERAGE_FAMILIES))
        strength = next(line for line in section(text, "## 2.2 Vocabulary Rules", "## 2.3").splitlines()
                        if line.startswith("| Strength"))
        for word in dc.STRENGTHS:
            self.assertIn(word, strength)
        coverage_text = section(text, "# 10. COVERAGE SYSTEM", "## 10.2") + section(
            text, "# APPENDIX B. CALL QUICK REFERENCE", "# APPENDIX C")
        for word in dc.COVERAGES:
            bare = word.split(" ")[-1] if word[0].isdigit() and " " in word else word
            self.assertRegex(coverage_text, r"(?<![\w])%s(?![\w])" % re.escape(bare), word)
        for name in dc.PACKAGES:
            self.assertIn(name.lower(), text.lower(), name)
        self.assertIn("interior mug", text)


class SheetValidatorTests(unittest.TestCase):
    def test_the_fixture_is_valid(self):
        sheet = fixture_sheet("Jacksonville Jaguars")
        self.assertEqual(dc.sheet_errors(sheet), [])
        self.assertEqual(dc.source_errors(sheet, ROOT, 2014), [])
        self.assertEqual(dc.sheet_sha256(sheet), dc.sheet_sha256(json.loads(json.dumps(sheet))))

    def mutated(self, change):
        sheet = fixture_sheet("Jacksonville Jaguars")
        change(sheet)
        return sheet

    def assertRefused(self, change, words, repository=False):
        sheet = self.mutated(change)
        errors = dc.sheet_errors(sheet) + (dc.source_errors(sheet, ROOT, 2014) if repository else [])
        self.assertTrue(any(words in e for e in errors), errors)

    def row(self, sheet, rid):
        return next(r for r in sheet["rows"] if r["id"] == rid)

    def test_encoding_rules(self):
        self.assertRefused(lambda s: self.row(s, "P1").update(menu="normal-down"), "never labels")
        self.assertRefused(lambda s: self.row(s, "C1").update(menu="second-and-long"), "never labels")
        self.assertRefused(lambda s: self.row(s, "K1").update(menu="third-and-medium"), "never labels")
        self.assertRefused(lambda s: self.row(s, "D1").pop("menu"), "needs a menu key")
        self.assertRefused(lambda s: self.row(s, "D1").update(menu="third-and-6-9"), "needs a menu key")
        self.assertRefused(lambda s: self.row(s, "D2").update(menu="normal-down"), "one labelling row per menu")
        self.assertRefused(lambda s: self.row(s, "D1").pop("call"), "needs its call")
        self.assertRefused(lambda s: s["rows"].append(dict(self.row(s, "D1"))), "duplicate row id")

    def test_nothing_off_the_practiced_menu_or_the_book(self):
        self.assertRefused(lambda s: self.row(s, "D1")["call"].update(coverage=["Tampa"]), "not on the practiced menu")
        self.assertRefused(lambda s: self.row(s, "D1")["call"].update(package="Big Nickel"),
                           "not on the practiced menu")
        self.assertRefused(lambda s: self.row(s, "D1")["call"].update(front="Mint"), "not a word of the active")
        self.assertRefused(lambda s: self.row(s, "D1")["call"].update(pressure="zero-blitz"), "not a word")
        self.assertRefused(lambda s: s["practiced"]["coverages"].append("Cover 9"), "not a word")
        self.assertRefused(lambda s: self.row(s, "D1")["call"].update(personnel="11"), "unknown call field")

    def test_pressure_families_and_the_interior_mug(self):
        self.assertRefused(lambda s: self.row(s, "D5")["call"].update(pressure="base-4", tags=[]),
                           "interior mug is encoded as pressure replace")
        self.assertRefused(lambda s: self.row(s, "D5")["call"].update(tags=[]), "interior mug")
        self.assertRefused(lambda s: self.row(s, "D1")["call"].update(tags=["mug"]), "belongs to the replace family")

    def test_rush_rule_keys_and_records(self):
        self.assertRefused(lambda s: s["rush_rule"].update(rule="five on third down"), "rush_rule.rule")
        self.assertRefused(lambda s: s.update(share=0.4), "unknown sheet field")
        self.assertRefused(lambda s: self.row(s, "D1").update(probability=0.5), "unknown row field")
        self.assertRefused(lambda s: s.update(presentation=["11 2x2"]), "unknown sheet field")
        self.assertRefused(lambda s: self.row(s, "D1")["source"].pop("line"), "packet line")

    def test_repository_checks(self):
        later = "career/playbook/alex_stone_2016_2017_defensive_evolution_ii.md"
        self.assertRefused(lambda s: s.update(book=later), "schema version 1 holds", repository=True)
        sheet = fixture_sheet("Jacksonville Jaguars")
        self.assertEqual(dc.source_errors(sheet, ROOT), [])  # the live week: the active book
        self.assertTrue(any("not the defensive iteration in force" in e
                            for e in dc.source_errors(dict(sheet, book=later), ROOT, 2014)))
        self.assertTrue(any("not the active defensive playbook" in e for e in dc.source_errors(dict(sheet, book=later), ROOT)))
        # The playbook index (never a book) dates each iteration; a 2016 sheet
        # cannot name Iteration II while the active season is 2014.
        self.assertEqual(dc.defensive_iterations(ROOT)[dc.VOCABULARY_BOOK], (2013, 2015))
        self.assertTrue(any("not the defensive iteration in force" in e
                            for e in dc.source_errors(dict(sheet, book=later), ROOT, 2016)))
        self.assertTrue(dc.source_errors(sheet, ROOT, 2016))
        self.assertRefused(lambda s: self.row(s, "D1")["source"].update(text="Normal down | **Under Y, Cover 1**"),
                           "not verbatim", repository=True)
        self.assertRefused(lambda s: self.row(s, "D1")["source"].update(line=999), "outside", repository=True)
        self.assertRefused(lambda s: self.row(s, "D1")["source"].update(path=dc.active_defensive_book()),
                           "not a packet", repository=True)
        self.assertRefused(lambda s: s.update(packet="career/2014/no_such_packet.md"), "not a file", repository=True)
        # Whitespace runs compare as one space (packet tables pad their cells).
        sheet = self.mutated(lambda s: self.row(s, "D1")["source"].update(
            text="Normal down |   **Under Y, Quarters**   | Base four"))
        self.assertEqual(dc.source_errors(sheet, ROOT, 2014), [])

    def test_committed_sheet_check(self):
        data = {"team": "Jacksonville Jaguars", dc.SHEET_KEY: fixture_sheet("Jacksonville Jaguars")}
        self.assertEqual(dc.committed_sheet_errors(data, ROOT, 2014), [])
        self.assertTrue(dc.committed_sheet_errors(dict(data, team="Pittsburgh Steelers"), ROOT, 2014))
        self.assertEqual(dc.committed_sheet_errors({"team": "Jacksonville Jaguars"}, ROOT, 2014), [])


class SnapMenuTests(unittest.TestCase):
    def snap(self, **kw):
        row = {"play_type": "pass", "down": 1, "ydstogo": 10, "yardline": 60, "period": 2, "game_clock": "8:00"}
        row.update(kw)
        return row

    def test_down_distance_zone_and_clock(self):
        self.assertEqual(dc.snap_menus(self.snap(), 0), [cs.NORMAL])
        self.assertEqual(dc.snap_menus(self.snap(down=2, ydstogo=8), 0), [cs.SECOND_LONG, cs.NORMAL])
        self.assertEqual(dc.snap_menus(self.snap(down=3, ydstogo=2), 0), [cs.THIRD_SHORT])
        self.assertEqual(dc.snap_menus(self.snap(down=4, ydstogo=4), 0), [cs.THIRD_MEDIUM])
        self.assertEqual(dc.snap_menus(self.snap(down=3, ydstogo=9, yardline=15), 0),
                         [cs.THIRD_LONG, cs.HIGH_RED, dc.RED_ZONE])
        self.assertEqual(dc.snap_menus(self.snap(yardline=3), 0),
                         [cs.GOAL_LINE, cs.LOW_RED, cs.HIGH_RED, dc.RED_ZONE, cs.NORMAL])
        self.assertEqual(dc.snap_menus(self.snap(yardline=95), 0), [cs.BACKED_UP, cs.NORMAL])
        self.assertEqual(dc.snap_menus({"play_type": "two_point"}, 0),
                         [cs.TWO_POINT, cs.GOAL_LINE, cs.LOW_RED, cs.HIGH_RED, dc.RED_ZONE])

    def test_lead_late_convention_and_the_clock_menus(self):
        # The defense leads (the offense trails) in the second half's last 2:00.
        self.assertEqual(dc.snap_menus(self.snap(period=4, game_clock="1:59"), -3),
                         [dc.LEAD_LATE, cs.TWO_MINUTE, cs.NORMAL])
        # Inside 4:00 but outside 2:00 it is not lead-late (the other candidate window).
        self.assertEqual(dc.snap_menus(self.snap(period=4, game_clock="3:30"), -3), [cs.NORMAL])
        self.assertEqual(dc.snap_menus(self.snap(period=4, game_clock="3:30"), 3), [cs.FOUR_MINUTE, cs.NORMAL])
        self.assertEqual(dc.snap_menus(self.snap(period=2, game_clock="1:30"), 7), [cs.TWO_MINUTE, cs.NORMAL])
        self.assertEqual(dc.snap_menus(self.snap(period=4, game_clock="1:30"), 0), [cs.TWO_MINUTE, cs.NORMAL])
        self.assertEqual(dc.snap_menus(self.snap(period=1, game_clock="1:30"), 0), [cs.NORMAL])
        windows = dc.LEAD_LATE_CONVENTION["candidate_windows"]
        self.assertEqual(set(windows), {"two-minute", "four-minute"})
        self.assertEqual(dc.LEAD_LATE_CONVENTION["applied_window"], "two-minute")
        self.assertEqual(windows["two-minute"]["seconds_left_at_most"], cs.TWO_MINUTE_SECONDS)
        self.assertEqual(windows["four-minute"]["seconds_left_at_most"], cs.FOUR_MINUTE_SECONDS)

    def test_the_applicable_row_and_kneels(self):
        rows = {menu: row["id"] for menu, row in dc.labelling_rows(fixture_sheet()).items()}
        self.assertEqual(dc.expected_label(self.snap(down=3, ydstogo=9, yardline=15), 0, rows)["def_row"], "D5")
        self.assertEqual(dc.expected_label(self.snap(yardline=8), 0, rows)["def_label_source"], "sheet:red-zone")
        kneel = dc.expected_label(self.snap(kneel=True), 0, rows)
        self.assertEqual((kneel["def_row"], kneel["def_label_source"]), (None, "kneel"))
        self.assertEqual(dc.expected_label(self.snap(down=3, ydstogo=1), 0, {})["def_label_source"], "none")
        self.assertEqual(dc.expected_label(self.snap(), 0, rows)["def_rush_rule"], dc.RUSH_RULE)


class KernelRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a, cls.b = sample_teams()
        cls.sa = replace(cls.a, defensive_call_sheet=fixture_sheet("A"))
        cls.sb = replace(cls.b, defensive_call_sheet=fixture_sheet("B"))
        cls.plain = [play(cls.a, cls.b, i) for i in range(GAMES)]
        cls.on_a = [play(cls.sa, cls.b, i) for i in range(GAMES)]
        cls.on_b = [play(cls.a, cls.sb, i) for i in range(GAMES)]

    def test_outcomes_possessions_and_exposure_are_unchanged(self):
        for plain, on_a, on_b in zip(self.plain, self.on_a, self.on_b):
            self.assertNotIn("defensive_calls", plain)
            self.assertFalse(any(f in row for row in plain["play_ledger"] for f in dc.FIELDS))
            for labelled in (on_a, on_b):
                self.assertEqual(stripped(labelled), json.loads(json.dumps(plain, default=str)))
                self.assertEqual(labelled["possessions"], plain["possessions"])
                self.assertEqual(exposure(labelled), exposure(plain))
                self.assertEqual(labelled["injuries"], plain["injuries"])

    def test_labels_are_on_the_sheet_clubs_defense_only(self):
        for result, club in ((self.on_a[0], "A"), (self.on_b[0], "B")):
            for row in result["play_ledger"]:
                snap = row.get("play_type") in dc.SNAP_TYPES and row.get("defense") == club
                self.assertEqual(all(f in row for f in dc.FIELDS), snap, row)
                self.assertEqual(any(f in row for f in dc.FIELDS), snap, row)
            self.assertEqual(set(result["defensive_calls"]["teams"]), {club})

    def test_the_record_validates_and_reconciles(self):
        sheet = fixture_sheet("A")
        for result in self.on_a:
            self.assertEqual(validate_result(result), [])
            self.assertEqual(check_ledger(result), [])
            self.assertIn("def_label_menu_mismatch", measurable_classes(result))
            entry = result["defensive_calls"]["teams"]["A"]
            self.assertEqual(entry["sheet_sha256"], dc.sheet_sha256(sheet))
            self.assertEqual(entry["offensive_menus_sha256"], dc.offensive_menus_sha256(self.a.offensive_call_sheet))
            self.assertEqual(entry["rush_rule"], dc.RUSH_RULE)
            self.assertEqual(set(entry["rows"]), {r["id"] for r in sheet["rows"] if r["kind"] == dc.SITUATION})
            self.assertEqual(result["defensive_calls"]["lead_late"], dc.LEAD_LATE_CONVENTION)
            stats = result["defensive_call_stats"]["A"]
            labelled = [r for r in result["play_ledger"] if r.get("defense") == "A" and "def_row" in r]
            self.assertEqual(sum(v["snaps"] for v in stats["rows"].values()) + stats["unlabelled_snaps"], len(labelled))
            for line in stats["rows"].values():
                self.assertEqual(set(line), {"snaps"})  # no outcome columns
            # The reported class: every snap of a Dime row (six backs; the convention seats at most five).
            dime = {rid for rid, row in entry["rows"].items() if row["package_conflict"]}
            self.assertEqual(dime, {"D2", "D5", "D8"})
            conflicts = [e for e in audit_only_errors(result) if e.startswith("def_package_participation_conflict")]
            self.assertEqual(len(conflicts), sum(1 for r in labelled if r["def_row"] in dime))

    def test_deterministic(self):
        again = play(self.sa, self.b, 0)
        self.assertEqual(json.dumps(again, sort_keys=True, default=str),
                         json.dumps(self.on_a[0], sort_keys=True, default=str))

    def test_coherence_classes_catch_a_wrong_label(self):
        result = copy.deepcopy(self.on_a[0])
        row = next(r for r in result["play_ledger"] if r.get("def_row") == "D1")
        row["def_row"] = "D5"
        self.assertTrue(any(e.startswith("def_label_menu_mismatch") for e in check_ledger(result)))
        result = copy.deepcopy(self.on_a[0])
        row = next(r for r in result["play_ledger"] if r.get("offense") == "A" and r.get("play_type") == "run")
        row.update({f: None for f in dc.FIELDS})
        self.assertTrue(any(e.startswith("def_label_wrong_club") for e in check_ledger(result)))
        result = copy.deepcopy(self.on_a[0])
        row = next(r for r in result["play_ledger"] if "def_row" in r)
        del row["def_situation"]
        self.assertTrue(any(e.startswith("def_label_wrong_club") for e in check_ledger(result)))
        result = copy.deepcopy(self.on_a[0])
        result["defensive_call_stats"]["A"]["rows"]["D1"]["snaps"] += 1
        self.assertTrue(any(e.startswith("def_label_menu_mismatch") for e in check_ledger(result)))
        result = copy.deepcopy(self.on_a[0])
        result["defensive_calls"]["teams"]["Z"] = result["defensive_calls"]["teams"].pop("A")
        self.assertTrue(any(e.startswith("def_label_wrong_club") for e in check_ledger(result)))

    def test_receipts_and_statistics(self):
        full = make_receipt(self.on_a[0], week=5, matchup="B at A")
        compact = make_receipt(self.on_a[0], week=5, matchup="B at A", detail="compact_stats")
        self.assertEqual(full["defensive_calls"], self.on_a[0]["defensive_calls"])
        self.assertEqual(full["defensive_call_stats"], self.on_a[0]["defensive_call_stats"])
        self.assertEqual(check_ledger(full), [])
        self.assertNotIn("defensive_calls", compact)
        plain = make_receipt(self.plain[0], week=5, matchup="B at A")
        self.assertNotIn("defensive_calls", plain)
        from scripts.render_season_stats import play_calls_markdown
        book = aggregate_receipts([full])
        self.assertEqual(book["defensive_calls"]["A"][0]["rows"]["D1"]["snaps"],
                         self.on_a[0]["defensive_call_stats"]["A"]["rows"]["D1"]["snaps"])
        text = play_calls_markdown(2014, "A", book)
        self.assertIn("## Defensive call record", text)
        self.assertIn("| 5 | D1 | normal-down |", text)
        self.assertNotIn("defensive_calls", aggregate_receipts([plain]))
        self.assertNotIn("Defensive call record", play_calls_markdown(2014, "A", aggregate_receipts([plain])))

    def test_the_sheet_stays_out_of_both_packets(self):
        self.assertEqual(game_runner._team_packet(self.sa), game_runner._team_packet(self.a))
        self.assertEqual(kernel._outcome_team(self.sa), kernel._outcome_team(self.a))
        from support_rosters import single_quarterback_teams
        home, away = single_quarterback_teams()  # legal 46-man units
        with_sheet = replace(home, defensive_call_sheet=fixture_sheet(home.team_id))
        self.assertEqual(game_runner.build_game_packet("w1a", "snapshot", with_sheet, away),
                         game_runner.build_game_packet("w1a", "snapshot", home, away))

    def test_refusals_before_any_draw(self):
        def faults(home, profile=PROFILE_2014_6, game_type="regular"):
            return decision_block_errors(home, self.b, profile=profile, game_type=game_type)
        self.assertEqual(faults(self.sa), [])
        self.assertTrue(any("does not record defensive calls" in e for e in faults(self.sa, PROFILE_2014_5)))
        self.assertTrue(any("out of scope" in e for e in faults(self.sa, game_type="preseason")))
        self.assertTrue(any("out of scope" in e for e in faults(self.sa, game_type="pro_bowl")))
        bad = fixture_sheet("A"); bad["rows"][2]["menu"] = "third-and-6-9"
        self.assertTrue(any("defensive call sheet" in e for e in faults(replace(self.a, defensive_call_sheet=bad))))
        self.assertTrue(any("carries the defensive call sheet of B" in e
                            for e in faults(replace(self.a, defensive_call_sheet=fixture_sheet("B")))))
        with self.assertRaisesRegex(ValueError, "does not record defensive calls"):
            play(self.sa, self.b, 0, profile=PROFILE_2014_5)

        class NoJournal:
            snapshot = "snapshot"
            def close_event(self, packet):
                raise AssertionError("journaled a refused game")
        with self.assertRaisesRegex(ValueError, "defensive call sheet"):
            game_runner.run_game(replace(self.a, defensive_call_sheet=bad), self.b, event_id="w1a-refused",
                                 snapshot="snapshot", client=NoJournal())


class InputsTests(unittest.TestCase):
    """The week build and the closure carry the sheet as a dict, or nothing."""

    @classmethod
    def setUpClass(cls):
        from runtime import week_inputs
        from runtime.seasons import SeasonPaths
        from scripts.render_season_stats import load_receipts
        cls.week_inputs = week_inputs
        cls.receipts = [r for r in load_receipts(SeasonPaths(2014).receipts) if int(r["week"]) <= 4]
        sheet = json.loads((ROOT / "career/2014/05_Regular_Season/Games/Week_04/call_sheet.json").read_text())
        cls.call_sheet = sheet["offensive_call_sheet"]
        cls.anchors = {"offense_anchor": 2.0, "defense_anchor": 2.0, "special_teams_anchor": 2.0}

    def build(self, **kw):
        return self.week_inputs.jacksonville_input(self.receipts, date(2014, 10, 5), self.anchors, self.call_sheet,
                                                   2014, **kw)

    def test_jacksonville_input(self):
        plain = self.build()
        self.assertNotIn("defensive_call_sheet", plain)
        sheet = fixture_sheet("Jacksonville Jaguars")
        data = self.build(defensive_sheet=sheet)
        self.assertEqual(data["defensive_call_sheet"], sheet)
        self.assertEqual({k: v for k, v in data.items() if k != "defensive_call_sheet"}, plain)
        bad = copy.deepcopy(sheet); bad["rows"][0]["menu"] = "normal-down"
        with self.assertRaisesRegex(ValueError, "W1a defensive call sheet"):
            self.build(defensive_sheet=bad)
        with self.assertRaisesRegex(ValueError, "not Jacksonville Jaguars's"):
            self.build(defensive_sheet=fixture_sheet("Pittsburgh Steelers"))
        with patch.object(self.week_inputs, "live_defensive_record", return_value=False):
            with self.assertRaisesRegex(ValueError, "does not record defensive calls"):
                self.build(defensive_sheet=sheet)

    def test_close_week_team_input(self):
        from scripts import close_week
        a, _ = sample_teams()
        data = json.loads(json.dumps(dataclasses.asdict(replace(a, defensive_call_sheet=fixture_sheet("A")))))
        self.assertEqual(close_week.team_input(data).defensive_call_sheet, fixture_sheet("A"))
        data.pop("defensive_call_sheet")
        self.assertIsNone(close_week.team_input(data).defensive_call_sheet)


class ClosureAndResumeTests(unittest.TestCase):
    """The sheet never touches a pause trigger, and a resume reads the
    frozen package: the paused prefix and the closed game equal the same
    closure without the sheet, the closed game labelled."""

    def setUp(self):
        from test_close_week_pause import BACKGROUND, DELEGATED, EVENT, JAX, club, game
        from local_private_service import local_service
        from runtime.seasons import SeasonPaths
        from scripts import close_week
        self.close_week, self.EVENT, self.BACKGROUND = close_week, EVENT, BACKGROUND
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        runs = {}
        for arm in ("plain", "sheet"):
            root = Path(self.tmp.name) / arm
            (root / "career/2014").mkdir(parents=True)
            paths = SeasonPaths(2014, root)
            client = local_service(self, root / "private", "w1a-closure")[1]
            home = replace(club(JAX, "A", featured=("A-QB1",), third_quarterback=True), **DELEGATED)
            if arm == "sheet":
                home = replace(home, defensive_call_sheet=fixture_sheet(JAX))
            away = club("B", "B")
            package = {"season": 2014, "week": 1, "games": [
                game(BACKGROUND, "week_01_d_at_c.json", club("D", "D"), club("C", "C")),
                game(EVENT, "week_01_b_at_jacksonville.json", away, home)]}
            runs[arm] = (paths, client, package)
        self.runs = runs

    def close(self, arm, answer=None):
        paths, client, package = self.runs[arm]
        packet = game_runner.build_game_packet(self.EVENT, "snapshot", self.close_week.team_input(
            package["games"][1]["home_input"]), self.close_week.team_input(package["games"][1]["away_input"]),
            management_mode="user_controlled")
        entropy = game_runner._entropy_from_ref(client.close_event(packet))
        base = kernel.resolve_game(self.close_week.team_input(package["games"][1]["home_input"]),
                                   self.close_week.team_input(package["games"][1]["away_input"]),
                                   seed=entropy, event_id=self.EVENT)
        drive = next(p["number"] for p in base["possessions"] if p["team"] == "Jacksonville Jaguars")
        onsets = {(drive, "A-QB1"): {"injury_class": "lower_extremity", "severity": "multi_week", "removed": True}}

        def forced(home, away, **kwargs):
            extra = {"_test_onsets": dict(onsets)} if kwargs.get("event_id") == self.EVENT else {}
            return kernel.resolve_game(home, away, **kwargs, **extra)
        with patch.object(game_runner, "resolve_game", forced), contextlib.redirect_stdout(io.StringIO()):
            results, paused = self.close_week.close_slate(package, paths, "snapshot", client,
                                                         paths.cache(1, "results"), answer)
            while answer is not None and paused is not None:
                defaults = {d["slot"]: d["default"] for d in paused["pause"]["decisions"]}
                results, paused = self.close_week.close_slate(package, paths, "snapshot", client,
                                                             paths.cache(1, "results"), {"choices": defaults})
        return results, paused

    def test_pause_and_resume_with_the_sheet(self):
        out = {}
        for arm in ("plain", "sheet"):
            _, paused = self.close(arm)
            self.assertIsNotNone(paused, arm)
            pause = paused["pause"]
            defaults = {d["slot"]: d["default"] for d in pause["decisions"]}
            results, still = self.close(arm, {"choices": defaults})
            self.assertIsNone(still)
            out[arm] = (paused, results)
        (p_plain, r_plain), (p_sheet, r_sheet) = out["plain"], out["sheet"]
        self.assertEqual(p_sheet["pause"], p_plain["pause"])
        self.assertEqual(p_sheet["partial"], p_plain["partial"])
        self.assertNotIn("def_row", json.dumps(p_sheet))
        final = r_sheet[self.EVENT]
        self.assertEqual(validate_result(final), [])
        self.assertIn("Jacksonville Jaguars", final["defensive_calls"]["teams"])
        self.assertEqual(stripped(final), stripped(r_plain[self.EVENT]))
        self.assertEqual(r_sheet[self.BACKGROUND], r_plain[self.BACKGROUND])


@unittest.skipIf(shutil.which("git") is None, "git is not installed (the engine image)")
class FreezeOrderTests(unittest.TestCase):
    """scripts/validate_repository.py: the record names the committed sheet,
    and the sheet's freeze commit precedes the receipt's closure commit."""

    def setUp(self):
        from scripts import validate_repository
        self.vr = validate_repository
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "test")
        self.sheet = "career/2014/Week_05/call_sheet.json"
        self.receipt = "career/2014/receipts/week_05.json"

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def commit(self, *rels):
        self.git("add", *rels)
        self.git("commit", "-q", "-m", "c")

    def test_freeze_precedes_closure(self):
        self.write(self.sheet, "{}")
        self.assertTrue(self.vr.freeze_order_errors(self.root, self.sheet, self.receipt))  # not committed
        self.commit(self.sheet)
        self.write(self.receipt, "{}")
        self.assertEqual(self.vr.freeze_order_errors(self.root, self.sheet, self.receipt), [])  # closure pending
        self.commit(self.receipt)
        self.assertEqual(self.vr.freeze_order_errors(self.root, self.sheet, self.receipt), [])
        self.write(self.sheet, '{"changed": 1}')
        self.assertTrue(any("changed after its freeze" in e
                            for e in self.vr.freeze_order_errors(self.root, self.sheet, self.receipt)))

    def test_same_commit_is_refused(self):
        self.write(self.sheet, "{}")
        self.write(self.receipt, "{}")
        self.commit(self.sheet, self.receipt)
        self.assertTrue(any("does not follow" in e
                            for e in self.vr.freeze_order_errors(self.root, self.sheet, self.receipt)))

    def test_receipt_record_against_the_committed_sheet(self):
        a, b = sample_teams()
        result = play(replace(a, team_id="Jacksonville Jaguars",
                              defensive_call_sheet=fixture_sheet("Jacksonville Jaguars")), b, 1)
        receipt = make_receipt(result, week=5, matchup="B at Jacksonville Jaguars")
        call_sheet = {"team": "Jacksonville Jaguars", "offensive_call_sheet": list(a.offensive_call_sheet),
                      dc.SHEET_KEY: fixture_sheet("Jacksonville Jaguars")}
        self.assertEqual(dc.receipt_record_errors(receipt, call_sheet), [])
        other = copy.deepcopy(call_sheet); other[dc.SHEET_KEY]["rows"][2]["id"] = "D1x"
        self.assertTrue(any("sheet sha256" in e for e in dc.receipt_record_errors(receipt, other)))
        other = dict(call_sheet, offensive_call_sheet=list(a.offensive_call_sheet)[1:])
        self.assertTrue(any("offensive menus" in e for e in dc.receipt_record_errors(receipt, other)))
        self.assertTrue(dc.receipt_record_errors(receipt, None))
        self.assertTrue(dc.receipt_record_errors(receipt, dict(call_sheet, team="Pittsburgh Steelers")))


if __name__ == "__main__":
    unittest.main()
