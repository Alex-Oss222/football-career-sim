"""Kernel 2014.6 batch B6, W3: a field goal before fourth down.

Under the profile flag early_fg_v2 a field-goal drive kicks on fourth down
unless the kick is early by the frozen rule (the drive ends its window; in
regulation the kick-snap clock is at most EARLY_FG_SECONDS; in overtime the
kick ends the game). A field-goal tuple whose real kick came earlier is
admitted only when a fourth-down layout exists at the spot, and the layout
search is held to fourth down in every tier with a closable, counted
fallback to the real down. Synthetic seeds only; no career state.
"""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import chains
from runtime import field_position as fp
from runtime.calibration_base import BASE_2010_2014W4
from runtime.kernel import resolve_game, validate_result
from runtime.play_detail import audit_only_errors, check_ledger, DRIVE_SUMMARY_FIELDS
from runtime.profiles import PROFILE_2014_6
from synthetic_games import SEED, sample_teams

ROOT = Path(__file__).resolve().parents[1]
WEEK_3 = ROOT / ("career/2014/05_Regular_Season/Statistics/records/game_receipts/"
                 "week_03_indianapolis_colts_at_jacksonville_jaguars.json")
MODEL = BASE_2010_2014W4.field_position()
T = MODEL.T
EARLY = MODEL.EARLY_FG_SECONDS


def games(n, tag="w3"):
    a, b = sample_teams()
    return [resolve_game(a, b, seed=SEED + b"-b6-%s-%03d" % (tag.encode(), i), event_id="b6-%s-%d" % (tag, i),
                         _test_profile=PROFILE_2014_6) for i in range(n)]


def kick_row(result, number):
    return next(r for r in result["play_ledger"] if r["drive"] == number and r["play_type"] == "field_goal")


def half_clock(row, half):
    minutes, seconds = (int(v) for v in row["game_clock"].split(":"))
    left = minutes * 60 + seconds
    if half == "OT":
        return left
    return left + (900 if row["period"] in (1, 3) else 0)


class ConstantsTests(unittest.TestCase):
    def test_constants_come_from_the_base(self):
        rules = BASE_2010_2014W4.specification_rules()["end_of_half"]
        self.assertEqual(EARLY, rules["EARLY_FG_SECONDS"])
        self.assertEqual(EARLY, 43)
        constants = MODEL.load()["constants"]
        self.assertEqual(constants["early_field_goal"]["max_seconds"], 43.0)
        self.assertEqual(constants["early_field_goal"]["next_largest"], [38.0, 36.0])
        # The kick length is the W5a table's field-goal cells pooled over the last snap's kind.
        table = constants["w5a"]["kick_length_seconds"]
        seconds = sum(v[0] for k, v in table.items() if k.startswith("field_goal|"))
        snaps = sum(v[1] for k, v in table.items() if k.startswith("field_goal|"))
        self.assertEqual(MODEL.kick_length("field_goal_attempt"), int(round(seconds / snaps)))
        self.assertEqual(MODEL.kick_length("touchdown"), 0)

    def test_fourth_down_layout_condition(self):
        # The Week 3 drive: five snaps netting 79 from the 80 admit a kick on fourth down.
        self.assertTrue(chains.fourth_down_fg_feasible(plays=5, net=79, spot=80))
        # A one-snap field goal cannot kick on fourth down; a three-snap one can.
        self.assertFalse(chains.fourth_down_fg_feasible(plays=1, net=10, spot=40))
        self.assertTrue(chains.fourth_down_fg_feasible(plays=3, net=5, spot=40))
        self.assertTrue(chains.chain_feasible("field_goal_attempt", plays=1, net=10, spot=40))


class EarlyRuleTests(unittest.TestCase):
    def fg_tuples(self):
        return [t for t in fp._v3_tuples(MODEL.data, "field_goal_attempt") if t[T["term_down"]] in (1, 2, 3)]

    def test_end_of_half_kick_may_come_on_any_down(self):
        # A kick that ends its window (4 s left) is early on any down.
        for t in self.fg_tuples()[:50]:
            self.assertTrue(MODEL.early_fg_ok(t, MODEL.own_seconds(t) + 4, False, True))
            self.assertTrue(MODEL.fg_tuple_admitted(t, 70, MODEL.own_seconds(t) + 4, "h1_late", True,
                                                    {"early_fg_v2": True}))

    def test_regulation_kick_clock_bound(self):
        for t in self.fg_tuples()[:50]:
            own = MODEL.own_seconds(t)
            length = min(MODEL.kick_length("field_goal_attempt"), own)
            at_bound = own - length + EARLY
            self.assertEqual(MODEL.kick_snap_clock("field_goal_attempt", t, at_bound), EARLY)
            self.assertTrue(MODEL.early_fg_ok(t, at_bound, False, False))
            self.assertFalse(MODEL.early_fg_ok(t, at_bound + 1, False, False))

    def test_overtime_cases(self):
        for t in self.fg_tuples()[:50]:
            window = MODEL.own_seconds(t) + 600
            # In overtime the clock bound does not apply: only a walk-off kick is early.
            self.assertTrue(MODEL.early_fg_ok(t, window, True, False, walk_off=True))
            self.assertFalse(MODEL.early_fg_ok(t, window, True, False, walk_off=False))
            self.assertFalse(MODEL.early_fg_ok(t, MODEL.own_seconds(t) + 10, True, False, walk_off=False))
            admitted = MODEL.fg_tuple_admitted(t, 70, window, "ot", False, {"early_fg_v2": True})
            self.assertEqual(admitted, MODEL.fourth_down_fg_feasible(t, 70))
            self.assertTrue(MODEL.fg_tuple_admitted(t, 70, window, "ot", False,
                                                    {"early_fg_v2": True, "walk_off_fg": True}))

    def test_flag_off_admits_every_tuple(self):
        for t in self.fg_tuples()[:50]:
            self.assertTrue(MODEL.fg_tuple_admitted(t, 70, 1200, "h2_neutral", False, {}))
            self.assertTrue(MODEL.fg_tuple_admitted(t, 70, 1200, "h2_neutral", False, None))

    def test_dynamic_filter_excludes_only_infeasible_early_kicks(self):
        tuples = tuple(self.fg_tuples())
        plain = MODEL._dynamic(tuples, "field_goal_attempt", "h2_neutral", 1500, 70, {})
        held = MODEL._dynamic(tuples, "field_goal_attempt", "h2_neutral", 1500, 70, {"early_fg_v2": True})
        held_ids = {id(t) for t in held}
        self.assertTrue(held_ids <= {id(t) for t in plain})
        for t in plain:
            expected = MODEL.early_fg_ok(t, 1500, False, False) or MODEL.fourth_down_fg_feasible(t, 70)
            self.assertEqual(id(t) in held_ids, expected)
        self.assertLess(len(held), len(plain))


class Week3DriveLayoutTests(unittest.TestCase):
    """Vinatieri's 19-yard field goal on first-and-goal from the 1 (Week 3,
    drive 3): five snaps (one completion, four runs) netting 79 from the 80,
    the real kick on first down. Held to fourth down, no layout kicks early;
    with the real down, the installed search kicks early most of the time."""

    @classmethod
    def setUpClass(cls):
        receipt = json.loads(WEEK_3.read_text(encoding="utf-8"))
        drive = dict(zip(DRIVE_SUMMARY_FIELDS, receipt["drives"][2]))
        rows = [r for r in receipt["play_ledger"] if r["drive"] == 3 and r["play_type"] in ("pass", "run")]
        cls.params = dict(
            category="field_goal_attempt", td_type=None,
            runs=sum(1 for r in rows if r["play_type"] == "run"),
            attempts=sum(1 for r in rows if r["play_type"] == "pass" and not r.get("sack")),
            sacks=sum(1 for r in rows if r.get("sack")), kneel_yards=(), spikes=0,
            pass_yards=sum(r["result_yards"] for r in rows if r["play_type"] == "pass" and r.get("completion")),
            rush_free=sum(r["result_yards"] for r in rows if r["play_type"] == "run"), losses=(),
            safety_terminal=None, net=drive["net_yards"], spot=drive["start_spot"], completion_rate=0.6,
            targets=drive["chains"], term_down=drive["fourth_down"]["down"])
        assert (cls.params["runs"], cls.params["attempts"], cls.params["net"], cls.params["spot"]) == (4, 1, 79, 80)
        assert cls.params["term_down"] == 1

    def layouts(self, fg_down):
        early = relaxed = 0
        for i in range(200):
            diagnostics = {}
            layout = chains.drive_layout(seed=SEED + b"-w3-%03d" % i, event_id="w3-%d" % i, drive_no=3,
                                         offense="IND", diagnostics=diagnostics, fg_down=fg_down, **self.params)
            self.assertTrue(layout["ok"])
            final = layout["walk"]["state"]
            early += final["down"] != 4
            relaxed += diagnostics.get(chains.FG_FOURTH_DOWN_RELAXED, 0)
        return early, relaxed

    def test_held_to_fourth_down_no_layout_kicks_early(self):
        early, relaxed = self.layouts(fg_down=4)
        self.assertEqual((early, relaxed), (0, 0))

    def test_installed_search_kicks_early(self):
        early, relaxed = self.layouts(fg_down=None)
        self.assertGreater(early, 0)
        self.assertEqual(relaxed, 0)

    def test_closable_fallback_admits_the_real_down(self):
        # A one-snap field goal cannot kick on fourth down: held to it, the
        # layout falls back to the real down and counts the fallback once.
        diagnostics = {}
        layout = chains.drive_layout(seed=SEED + b"-w3-one", event_id="w3-one", drive_no=1, offense="X",
                                     category="field_goal_attempt", td_type=None, runs=1, attempts=0, sacks=0,
                                     kneel_yards=(), spikes=0, pass_yards=0, rush_free=4, losses=(),
                                     safety_terminal=None, net=4, spot=30, completion_rate=0.6, targets=None,
                                     term_down=2, diagnostics=diagnostics, fg_down=4)
        self.assertTrue(layout["ok"])
        self.assertEqual(layout["walk"]["state"]["down"], 2)
        self.assertEqual(diagnostics.get(chains.FG_FOURTH_DOWN_RELAXED), 1)


class KernelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.games = games(60)

    def test_every_field_goal_is_on_fourth_down_or_early_or_counted(self):
        kicks = early = fourth = 0
        relaxed = sum(r["diagnostics"].get(chains.FG_FOURTH_DOWN_RELAXED, 0) for r in self.games)
        not_early = 0
        for r in self.games:
            self.assertEqual(validate_result(r), [])
            self.assertEqual([e for e in check_ledger(r) if "field_goal_before_fourth_down" in e], [])
            last = r["possessions"][-1]
            for p in r["possessions"]:
                if p["category"] != "field_goal_attempt":
                    continue
                kicks += 1
                down = p["fourth_down"]["down"]
                if down == 4:
                    fourth += 1
                    continue
                row = kick_row(r, p["number"])
                if p["half"] == "OT":
                    ok = p["fg_made"] and p is last
                else:
                    ok = p["half_final"] or (row["period"] in (2, 4) and half_clock(row, p["half"]) <= EARLY)
                if ok:
                    early += 1
                else:
                    not_early += 1
        self.assertGreater(kicks, 60)
        self.assertGreater(fourth, early)
        # A kick before fourth down that is not early is only the counted fallback.
        self.assertLessEqual(not_early, relaxed)
        audit = [e for r in self.games for e in audit_only_errors(r) if "field_goal_before_fourth_down" in e]
        self.assertEqual(len(audit), not_early)

    def test_doctored_receipt_is_flagged_audit_only(self):
        r = next(r for r in self.games
                 if any(p["category"] == "field_goal_attempt" and p["fourth_down"]["down"] == 4
                        and not p["half_final"] and p["half"] != "OT" for p in r["possessions"]))
        p = next(p for p in r["possessions"] if p["category"] == "field_goal_attempt"
                 and p["fourth_down"]["down"] == 4 and not p["half_final"] and p["half"] != "OT")
        doctored = copy.deepcopy(r)
        target = next(q for q in doctored["possessions"] if q["number"] == p["number"])
        target["fourth_down"]["down"] = 1
        row = kick_row(doctored, p["number"])
        row["period"], row["game_clock"] = 1, "10:00"
        flagged = [e for e in audit_only_errors(doctored) if e.startswith("field_goal_before_fourth_down")]
        self.assertEqual(len(flagged), 1)
        self.assertIn("drive %d" % p["number"], flagged[0])
        # Audit-only: the default check and validate_result do not refuse it.
        self.assertEqual([e for e in check_ledger(doctored) if "field_goal_before_fourth_down" in e], [])
        # The same kick inside the bound at the end of a half is coherent.
        row["period"], row["game_clock"] = 2, "0:%02d" % EARLY
        self.assertEqual([e for e in audit_only_errors(doctored) if "field_goal_before_fourth_down" in e], [])
        row["game_clock"] = "0:%02d" % (EARLY + 1)
        self.assertEqual(len([e for e in audit_only_errors(doctored) if "field_goal_before_fourth_down" in e]), 1)


if __name__ == "__main__":
    unittest.main()
