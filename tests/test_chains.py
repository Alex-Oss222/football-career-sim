"""Kernel 2014.4, defect register Tier 1 item 3: down, distance and the
chains walked from each drive's own snap ledger (runtime/chains.py)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import copy
import unittest
from unittest import mock

from runtime import chains, field_position as fp, play_detail
from runtime.chains import chain_feasible, drive_layout, fourth_down_state, walk
from runtime.kernel import resolve_game, validate_result
from runtime.play_detail import CHAIN_CLASSES, check_ledger, measurable_classes
from synthetic_games import SEED, sample, sample_teams

SCRIMMAGE = ("pass", "run")
SEED_BYTES = b"chain-walk-fixture-seed-not-career-state-0000"


def states(w):
    return [(r["down"], r["ydstogo"], r["los"], r["goal_to_go"], r["first_down"]) for r in w["rows"]]


def scrimmage(result, number):
    return [r for r in result["play_ledger"] if r["drive"] == number and r["play_type"] in SCRIMMAGE]


class WalkTests(unittest.TestCase):
    def test_first_down_exactly_at_the_line(self):
        w = walk(75, [4, 6, 3])
        self.assertEqual(states(w), [(1, 10, 75, False, False), (2, 6, 71, False, True),
                                     (1, 10, 65, False, False)])
        self.assertEqual(w["chains"], [1, 0, 0, 0, 0])
        self.assertEqual(w["state"], {"down": 2, "ydstogo": 7, "goal_to_go": False, "los": 62})

    def test_one_yard_short_is_not_a_first_down(self):
        w = walk(75, [4, 5])
        self.assertEqual(w["rows"][1]["first_down"], False)
        self.assertEqual(w["state"], {"down": 3, "ydstogo": 1, "goal_to_go": False, "los": 66})

    def test_sack_behind_the_line_lengthens_the_distance(self):
        # A first down at the 38, then a sack back past that marker: the next
        # line stays at the 28 and the distance grows; a sack never converts.
        w = walk(50, [12, -8, 20])
        self.assertEqual(states(w)[:2], [(1, 10, 50, False, True), (1, 10, 38, False, False)])
        self.assertEqual(states(w)[2], (2, 18, 46, False, True))
        self.assertEqual(w["chains"][0], 2)

    def test_goal_to_go(self):
        w = walk(8, [3, 2])
        self.assertEqual(states(w), [(1, 8, 8, True, False), (2, 5, 5, True, False)])
        self.assertEqual(w["state"], {"down": 3, "ydstogo": 3, "goal_to_go": True, "los": 3})
        # From the 15 the line to gain is the 5; reaching it starts 1st & goal.
        w = walk(15, [6, 4, 1])
        self.assertEqual(states(w), [(1, 10, 15, False, False), (2, 4, 9, False, True),
                                     (1, 5, 5, True, False)])

    def test_touchdown_is_a_first_down(self):
        w = walk(30, [5, 25])
        self.assertEqual(w["rows"][1]["first_down"], True)
        self.assertEqual(w["chains"], [1, 0, 0, 0, 0])

    def test_kneels_count_as_downs(self):
        w = walk(40, [-1, -1, -1])
        self.assertEqual([r["down"] for r in w["rows"]], [1, 2, 3])
        self.assertEqual(w["chains"], [0, 1, 0, 0, 0])
        self.assertEqual(w["state"], {"down": 4, "ydstogo": 13, "goal_to_go": False, "los": 43})

    def test_spike_uses_a_down(self):
        w = walk(60, [9, 0, 0])
        self.assertEqual([r["down"] for r in w["rows"]], [1, 2, 3])
        self.assertEqual(w["state"]["down"], 4)

    def test_punt_on_fourth_down(self):
        self.assertEqual(fourth_down_state("punt", 80, [2, 3, 1]),
                         {"down": 4, "ydstogo": 4, "goal_to_go": False, "los": 74})

    def test_downs_state_is_the_line_before_the_failed_snap(self):
        w = walk(40, [3, 2, 1, 2])
        self.assertEqual(w["failed"], 3)
        self.assertEqual(w["chains"], [0, 1, 0, 1, 0])
        # Ends at the 32; the published line of scrimmage is the 34.
        self.assertEqual(fourth_down_state("downs", 40, [3, 2, 1, 2]),
                         {"down": 4, "ydstogo": 4, "goal_to_go": False, "los": 34})
        self.assertIsNone(fourth_down_state("downs", 40, [3, 2, 1]))

    def test_snap_after_a_failed_fourth_down_is_a_break(self):
        w = walk(40, [0, 0, 0, 0, 5])
        self.assertEqual((w["failed"], w["breaks"]), (3, [4]))

    def test_field_goal_on_third_down(self):
        self.assertEqual(fourth_down_state("field_goal_attempt", 30, [12, 3, 2]),
                         {"down": 3, "ydstogo": 5, "goal_to_go": False, "los": 13})
        self.assertEqual(fourth_down_state("field_goal_attempt", 25, []),
                         {"down": 1, "ydstogo": 10, "goal_to_go": False, "los": 25})

    def test_turnover_snap_credits_no_first_down(self):
        w = walk(70, [3, 15], turnover_last=True)
        self.assertEqual(w["chains"], [0, 0, 0, 0, 0])
        self.assertIsNone(w["failed"])


class FeasibilityTests(unittest.TestCase):
    def test_punt_needs_three_snaps_after_its_last_first_down(self):
        self.assertTrue(chain_feasible("punt", plays=3, net=9, spot=80))
        self.assertFalse(chain_feasible("punt", plays=3, net=10, spot=80))
        self.assertFalse(chain_feasible("punt", plays=2, net=3, spot=80))
        self.assertTrue(chain_feasible("punt", plays=4, net=12, spot=80))
        self.assertFalse(chain_feasible("punt", plays=8, net=12, spot=80))  # two first downs need 20
        self.assertFalse(chain_feasible("punt", plays=4, net=6, spot=8))  # goal to go cannot convert

    def test_downs_needs_four_snaps(self):
        self.assertFalse(chain_feasible("downs", plays=3, net=2, spot=50))
        self.assertTrue(chain_feasible("downs", plays=4, net=2, spot=50))

    def test_field_goal_and_touchdown(self):
        self.assertTrue(chain_feasible("field_goal_attempt", plays=0, net=0, spot=20))
        self.assertTrue(chain_feasible("field_goal_attempt", plays=2, net=5, spot=20))
        self.assertFalse(chain_feasible("field_goal_attempt", plays=5, net=4, spot=20))
        self.assertTrue(chain_feasible("touchdown", plays=1, net=75, spot=75))
        self.assertFalse(chain_feasible("touchdown", plays=9, net=8, spot=8))

    def test_real_2012_drives_at_their_own_start(self):
        # Every real 2012 drive is feasible at its own start except the ones
        # whose reset or distance came from a penalty (no penalty rows).
        data, T = fp.load(), fp.T
        infeasible = total = 0
        for category in fp.CATEGORIES:
            for t in fp._all_tuples(data, category):
                total += 1
                net, _ = fp.adapt(category, t, t[T["start"]])
                terminal = fp.fixed_yardage(category, t)[2]
                if not chain_feasible(category, plays=t[T["plays"]], net=net, spot=t[T["start"]],
                                      kneel_yards=t[T["kneel_yards"]], sacks=t[T["sacks"]],
                                      runs=t[T["runs"]], terminal_value=terminal):
                    infeasible += 1
        self.assertEqual(total, 5979)
        self.assertLess(infeasible, 0.02 * total)

    def test_static_feasible_applies_the_chain_gate(self):
        t = next(t for t in fp._all_tuples(fp.load(), "punt") if t[fp.T["plays"]] == 3)
        end = t[fp.T["end"]]
        # Replayed so that three snaps must net ten or more: never selectable.
        spot = end + 12
        if 1 <= spot <= 99:
            self.assertFalse(fp.static_feasible("punt", t, spot))


class LayoutTests(unittest.TestCase):
    def layout(self, **kw):
        base = dict(seed=SEED_BYTES, event_id="chain-fixture", drive_no=1, offense="X", td_type=None,
                    kneel_yards=[], spikes=0, losses=[], safety_terminal=None, completion_rate=0.6)
        base.update(kw)
        return drive_layout(**base)

    def test_punt_layout_ends_on_fourth_down(self):
        out = self.layout(category="punt", runs=3, attempts=4, sacks=0, pass_yards=14, rush_free=7,
                          net=21, spot=80, targets=[1, 0, 2, 1, 0, 0], term_down=4)
        self.assertTrue(out["ok"])
        self.assertEqual(sum(out["values"]), 21)
        self.assertEqual(out["walk"]["state"]["down"], 4)
        self.assertEqual(out["walk"]["chains"][3:], [0, 0])  # no fourth-down attempt before the punt

    def test_downs_layout_fails_on_its_last_snap(self):
        out = self.layout(category="downs", runs=2, attempts=3, sacks=0, pass_yards=9, rush_free=3,
                          net=12, spot=45, targets=[1, 0, 1, 0, 1, 0], term_down=4)
        self.assertTrue(out["ok"])
        self.assertEqual(out["walk"]["failed"], 4)

    def test_infeasible_split_is_repaired_with_the_same_net(self):
        # Four snaps before a punt need one ten-yard snap; the kernel's split
        # (9 passing over two attempts, 3 rushing) has none.
        diagnostics = {}
        out = self.layout(category="punt", runs=2, attempts=2, sacks=0, pass_yards=9, rush_free=3,
                          net=12, spot=80, targets=[0, 1, 1, 0, 0, 0], term_down=4, diagnostics=diagnostics)
        self.assertTrue(out["ok"])
        self.assertEqual(out["pass_yards"] + out["rush_free"], 12)
        self.assertEqual(out["walk"]["state"]["down"], 4)
        self.assertNotIn("chain_layout_failed", diagnostics)

    def test_layout_is_deterministic_and_on_its_own_stream(self):
        kw = dict(category="field_goal_attempt", runs=4, attempts=5, sacks=1, pass_yards=30, rush_free=15,
                  losses=[6], net=39, spot=62, targets=[2, 0, 1, 1, 0, 0], term_down=4)
        one = self.layout(**kw)
        with mock.patch.object(play_detail, "SNAP_DETAIL_TAG", "public-snap-detail-test"):
            two = self.layout(**kw)
        self.assertEqual(one, two)


class SampleChainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.games = sample()

    def test_every_drive_reconciles_with_its_ledger(self):
        for r in self.games:
            self.assertTrue(set(CHAIN_CLASSES) <= measurable_classes(r))
            for p in r["possessions"]:
                rows = scrimmage(r, p["number"])
                yards = [x["result_yards"] for x in rows]
                w = walk(p["start_spot"], yards, p["category"] in chains.TURNOVER_TERMINALS)
                self.assertEqual([(x["down"], x["ydstogo"], x["yardline"], x["goal_to_go"], x["first_down"])
                                  for x in rows], states(w))
                self.assertEqual([p["chains"][0]] + p["chains"][2:], w["chains"])
                self.assertEqual(p["chain_model"], chains.CHAIN_MODEL)
                if p["category"] == "punt":
                    self.assertEqual(p["fourth_down"]["down"], 4)
                if p["category"] == "downs":
                    self.assertEqual(w["failed"], len(yards) - 1)
                    self.assertEqual(p["fourth_down"]["los"], p["end_spot"] + yards[-1])
                if p["fourth_down"]:
                    self.assertEqual({k: p["fourth_down"][k] for k in chains.STATE_FIELDS},
                                     fourth_down_state(p["category"], p["start_spot"], yards))
            for team, s in r["team_stats"].items():
                mine = [p for p in r["possessions"] if p["team"] == team]
                flags = sum(x["first_down"] for p in mine for x in scrimmage(r, p["number"]))
                self.assertEqual(s["first_downs"], flags + sum(p["chains"][1] for p in mine))
        failed = sum(r["diagnostics"].get("chain_layout_failed", 0) for r in self.games)
        self.assertEqual(failed, 0)

    def test_defect_register_audit(self):
        # The register's two measurements (item 3). A drive with no first down
        # that punts or kicks from outside the 10 is 4th & (10 - net) exactly.
        nofd = equal = exact_scope = exact = big = big_nofd = 0
        for r in self.games:
            for p in r["possessions"]:
                fd, ch = p["fourth_down"], p["chains"]
                if fd and ch[0] + ch[1] == 0:
                    nofd += 1
                    equal += fd["ydstogo"] == 10 - p["net_yards"]
                if fd and ch[0] == 0 and p["category"] != "downs" and p["start_spot"] > 10:
                    exact_scope += 1
                    exact += fd["ydstogo"] == 10 - p["net_yards"]
                if p["category"] != "touchdown" and p["net_yards"] >= 10:
                    big += 1
                    if ch[0] + ch[1] == 0:
                        big_nofd += 1
                        # Only a lost fumble can carry ten yards without a
                        # first down (2012: all 23 such drives).
                        self.assertEqual(p["category"], "fumble_lost")
        self.assertEqual(exact, exact_scope)
        self.assertGreater(equal / nofd, 0.97)       # 2012 pool 1,491 of 1,517; kernel 2014.3 about a third
        self.assertLess(big_nofd / big, 0.02)        # 2012 pool 23 of 2,632; kernel 2014.3 7.4%

    def test_chain_classes_detect_and_gate(self):
        r = copy.deepcopy(self.games[0])
        self.assertEqual(check_ledger(r), [])
        punt = next(p for p in r["possessions"] if p["category"] == "punt")
        rows = scrimmage(r, punt["number"])
        rows[0]["ydstogo"] += 1
        rows[1]["goal_to_go"] = not rows[1]["goal_to_go"]
        punt["fourth_down"]["ydstogo"] += 1
        punt["chains"][0] += 1
        found = {e.split(":")[0] for e in check_ledger(r)}
        self.assertTrue({"down_distance_chain_break", "fourth_down_distance_mismatch",
                         "first_downs_ne_ledger", "goal_to_go_mismatch"} <= found)
        flipped = copy.deepcopy(self.games[0])
        row = next(x for x in flipped["play_ledger"] if x["play_type"] in SCRIMMAGE and not x["first_down"])
        row["first_down"] = True
        self.assertIn("chain counters differ from the snap ledger", validate_result(flipped))
        # Without the walked model (closed 2013 receipts) nothing is measured.
        legacy = copy.deepcopy(self.games[0])
        for p in legacy["possessions"]:
            del p["chain_model"]
        self.assertFalse(set(CHAIN_CLASSES) & measurable_classes(legacy))
        compact = {k: v for k, v in self.games[0].items() if k != "play_ledger"}
        self.assertFalse(set(CHAIN_CLASSES) & measurable_classes(compact))

    def test_chain_fields_do_not_depend_on_the_snap_detail_stream(self):
        a, b = sample_teams()

        def chain_rows(result):
            return [(x["drive"], x["down"], x["ydstogo"], x["yardline"], x["result_yards"], x["first_down"])
                    for x in result["play_ledger"] if x["play_type"] in SCRIMMAGE]

        for i in range(3):
            first = resolve_game(a, b, seed=SEED + b"-chain-%02d" % i, event_id="chain-stream-%d" % i)
            with mock.patch.object(play_detail, "SNAP_DETAIL_TAG", "public-snap-detail-test"):
                second = resolve_game(a, b, seed=SEED + b"-chain-%02d" % i, event_id="chain-stream-%d" % i)
            self.assertEqual(chain_rows(first), chain_rows(second))
            self.assertEqual(first["possessions"], second["possessions"])


if __name__ == "__main__":
    unittest.main()
