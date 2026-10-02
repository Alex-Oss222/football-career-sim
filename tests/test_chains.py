"""Kernel 2014.4, defect register Tier 1 item 3: down, distance and the
chains walked from each drive's own snap ledger (runtime/chains.py)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import copy
import hashlib
import unittest
from unittest import mock

from runtime import chains, field_position as fp, play_detail
from runtime.calibration_base import BASE_2012
from runtime.chains import chain_feasible, drive_layout, fourth_down_state, walk
from runtime.kernel import resolve_game, validate_result
from runtime.play_detail import CHAIN_CLASSES, check_ledger, measurable_classes
from runtime.game_runner import ENTROPY_DOMAIN
from support_rosters import game_day_roster, single_quarterback_teams
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


class PenaltyFirstDownTests(unittest.TestCase):
    """Item 3 open issue 1: a walked scrimmage first down beyond the 2012
    tuple's scrimmage count absorbs one of its penalty first downs."""

    def test_formula(self):
        pen = chains.penalty_first_downs
        self.assertEqual(pen(2, 1, 2), 1)   # walk matches the real scrimmage count
        self.assertEqual(pen(2, 1, 1), 1)   # walk below it: the flag's first down stays
        self.assertEqual(pen(2, 1, 3), 0)   # one excess walked first down absorbs it
        self.assertEqual(pen(2, 2, 3), 1)
        self.assertEqual(pen(0, 1, 4), 0)   # never negative
        self.assertEqual(pen(3, 0, 5), 0)

    def test_total_never_double_counts(self):
        pen = chains.penalty_first_downs
        for c0 in range(6):
            for c1 in range(4):
                for walked in range(9):
                    total = walked + pen(c0, c1, walked)
                    self.assertGreaterEqual(total, walked)
                    self.assertLessEqual(total, max(walked, c0 + c1))

    def test_kernel_publishes_the_absorbed_count(self):
        # Every drive's published penalty count is the formula applied to its
        # own real tuple and walk, in drive order.
        a, b = sample_teams()
        calls = []
        real = chains.penalty_first_downs

        def spy(c0, c1, walked):
            out = real(c0, c1, walked)
            calls.append((int(c0), int(c1), int(walked), out))
            return out

        absorbed = 0
        with mock.patch.object(chains, "penalty_first_downs", side_effect=spy):
            for i in range(20):
                calls.clear()
                r = resolve_game(a, b, seed=SEED + b"-pen-%02d" % i, event_id="pen-fd-%d" % i)
                drives = [p for p in r["possessions"] if p.get("chain_model") == chains.CHAIN_MODEL]
                self.assertEqual(len(calls), len(drives))
                for p, (c0, c1, walked, out) in zip(drives, calls):
                    self.assertEqual((p["chains"][0], p["chains"][1]), (walked, out))
                    absorbed += c1 - out
        self.assertGreater(absorbed, 0)


class FeasibilityTests(unittest.TestCase):
    def test_punt_needs_three_snaps_after_its_last_first_down(self):
        self.assertTrue(chain_feasible("punt", plays=3, net=9, spot=80))
        self.assertFalse(chain_feasible("punt", plays=3, net=10, spot=80))
        self.assertFalse(chain_feasible("punt", plays=2, net=3, spot=80))
        self.assertTrue(chain_feasible("punt", plays=4, net=12, spot=80))
        self.assertFalse(chain_feasible("punt", plays=8, net=12, spot=80))  # two first downs need 20
        self.assertFalse(chain_feasible("punt", plays=4, net=6, spot=8))  # goal to go cannot convert

    def test_kneels_are_fixed_losses_after_the_free_snaps(self):
        # A real 2012 drive (run, kneel -2, kneel -1, punt on 4th) replayed
        # from the 94 with net 8: its one free snap must gain 11, a first
        # down, so the punt would come on third down. Store seed 398 of
        # tests/test_injuries_in_game.py drew it before this gate counted the
        # kneel yards (October 2026). Net 6 (a 9-yard run) stays feasible.
        self.assertFalse(chain_feasible("punt", plays=3, net=8, spot=94, kneel_yards=[-2, -1]))
        self.assertFalse(chain_feasible("punt", plays=3, net=9, spot=69, kneel_yards=[-2]))
        self.assertTrue(chain_feasible("punt", plays=3, net=6, spot=94, kneel_yards=[-2, -1]))
        self.assertTrue(chain_feasible("punt", plays=3, net=8, spot=94))
        # Kneels after a first down: the free snaps before them still need
        # the ten (6 snaps, two kneels, net 7: the four free snaps gain 10).
        self.assertTrue(chain_feasible("punt", plays=7, net=7, spot=50, kneel_yards=[-2, -1]))
        self.assertFalse(chain_feasible("punt", plays=7, net=6, spot=50, kneel_yards=[-2, -1]))

    def test_fumbled_sack_is_counted_once(self):
        # A real 2012 fumble (six snaps, five attempts and one sack, net 30
        # from the 53 with three first downs) replayed from the 18 with its
        # end kept nets -5. Six snaps need a first down, so ten yards gained,
        # and the lone sack can give back ten at most: the passes gain five
        # at most, so no order reaches the line to gain. The gate counted
        # that sack twice (a fumbled-snap allowance and a last-series sack)
        # until October 1, 2026 (kernel seeds pz-2103, samp-1482, sw2-2762).
        self.assertFalse(chain_feasible("fumble_lost", plays=6, net=-5, spot=18, sacks=1, runs=0))
        self.assertFalse(chain_feasible("fumble_lost", plays=6, net=-8, spot=15, sacks=1, runs=0))
        self.assertTrue(chain_feasible("fumble_lost", plays=6, net=30, spot=53, sacks=1, runs=0))
        # Two sacks, or a fumbled run beside the sack, can give back twenty.
        self.assertTrue(chain_feasible("fumble_lost", plays=6, net=-5, spot=18, sacks=2, runs=0))
        self.assertTrue(chain_feasible("fumble_lost", plays=6, net=-5, spot=18, sacks=1, runs=1))

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

    def test_last_rung_enumerates_the_plan(self):
        # The three drives that kept an unconstrained order at the candidate
        # acceptance (806 games): a five-snap touchdown from the 12 whose
        # passes must reach the line to gain exactly (pass 9 / rush 3 admits
        # no first down before the scoring run), and a four-snap clock drive
        # netting 0 whose only legal order needs the sack to give back exactly
        # the ten yards the passes gained. With the random redraws disabled
        # the enumeration finds both.
        from runtime import chains
        with mock.patch.object(chains, "DRAWS", 1), mock.patch.object(chains, "ALT_DRAWS", 0), \
                mock.patch.object(chains, "REPAIR_STEPS", 0):
            diagnostics = {}
            out = self.layout(category="touchdown", td_type="rush", runs=1, attempts=4, sacks=0, pass_yards=9,
                              rush_free=3, net=12, spot=12, targets=[2, 0, 1, 1, 0, 0], diagnostics=diagnostics)
            self.assertTrue(out["ok"])
            self.assertIn("chain_plan_enumerated", diagnostics)
            self.assertNotIn("chain_layout_failed", diagnostics)
            self.assertEqual(out["pass_yards"] + out["rush_free"], 12)
            self.assertIsNone(out["walk"]["failed"])
            self.assertEqual(out["walk"]["breaks"], [])
            diagnostics = {}
            out = self.layout(category="clock", runs=0, attempts=3, sacks=1, pass_yards=8, rush_free=0,
                              losses=[8], net=0, spot=80, targets=[1, 0, 1, 1, 0, 0], diagnostics=diagnostics)
            self.assertTrue(out["ok"])
            self.assertIn("chain_plan_enumerated", diagnostics)
            self.assertEqual(out["losses"], [10])
            self.assertEqual(out["walk"]["chains"][0], 1)
            self.assertIsNone(out["walk"]["failed"])

    def test_concentrated_rung_puts_the_ground_on_one_snap(self):
        # A real four-snap punt netting 19 behind a penalty first down,
        # replayed from the 99 with its end kept: net 53. The three snaps
        # after the last first down gain nine at most, so one snap carries
        # 44 or more, which no spread allocation of 19 passing and 34 rushing
        # and no bounded shift produces; the same-rung resample had no
        # substitute and the game failed validation (kernel seeds pz-25,
        # samp-835, pz-1345, sw2-749; October 1, 2026).
        diagnostics = {}
        out = self.layout(category="punt", runs=3, attempts=1, sacks=0, pass_yards=19, rush_free=34,
                          net=53, spot=99, targets=[0, 1, 1, 0, 0, 0], term_down=4, diagnostics=diagnostics)
        self.assertTrue(out["ok"])
        self.assertIn("chain_plan_concentrated", diagnostics)
        self.assertNotIn("chain_layout_failed", diagnostics)
        self.assertEqual(sum(out["values"]), 53)
        self.assertEqual(out["pass_yards"] + out["rush_free"], 53)
        self.assertGreaterEqual(max(out["values"]), 44)
        self.assertEqual(out["walk"]["state"]["down"], 4)
        self.assertEqual(out["walk"]["chains"][0], 1)

    def test_concentration_gathers_the_ground_before_a_fumbled_snap(self):
        # A real five-run fumble netting 10 from the 80 (one first down): the
        # fumbled snap credits no first down, so the ten yards must sit on a
        # snap before it. Repair 3 fed the largest value, the terminal snap
        # (store seed 44 of tests/test_game_runner.py, October 1, 2026); the
        # concentrated rung gathers onto the largest movable snap first.
        from runtime.chains import _concentrate
        kinds, completed = ["run"] * 5, [False] * 5
        steps = list(_concentrate(kinds, completed, [0, 2, 0, 3, 5], 4, "fumble_lost", "run", movable_only=True))
        self.assertEqual(steps[-1], [0, 0, 0, 10, 0])
        self.assertTrue(all(sum(v) == 10 for v in steps))
        w = walk(80, steps[-1], turnover_last=True)
        self.assertEqual((w["chains"][0], w["failed"], w["breaks"]), (1, None, []))
        anywhere = list(_concentrate(kinds, completed, [0, 2, 0, 3, 5], 4, "fumble_lost", "run"))
        self.assertEqual(anywhere[-1], [0, 0, 0, 0, 10])
        self.assertIsNotNone(walk(80, anywhere[-1], turnover_last=True)["failed"])

    def test_layout_is_deterministic_and_on_its_own_stream(self):
        kw = dict(category="field_goal_attempt", runs=4, attempts=5, sacks=1, pass_yards=30, rush_free=15,
                  losses=[6], net=39, spot=62, targets=[2, 0, 1, 1, 0, 0], term_down=4)
        one = self.layout(**kw)
        with mock.patch.object(play_detail, "SNAP_DETAIL_TAG", "public-snap-detail-test"):
            two = self.layout(**kw)
        self.assertEqual(one, two)


def sweep_entropy(label):
    """Kernel entropy as the production runner derives it from an opaque
    event reference, here from the label (the October 2026 seed sweep)."""
    return hashlib.sha256(ENTROPY_DOMAIN + hashlib.sha256(label.encode()).digest()).digest()


def pause_teams():
    """The pause-path fixture of the October 1, 2026 seed sweep (token
    "pause" of library/2014_6_pre_build_specification.md, A6 sweep)."""
    a = tuple(p for p in game_day_roster("A") if p.player_id != "A-WR5")
    b = tuple(p for p in game_day_roster("B") if p.player_id != "B-WR5")
    from runtime.kernel import TeamInput
    return TeamInput("A", tuple(p.player_id for p in a), roster=a), TeamInput("B", tuple(p.player_id for p in b), roster=b)


class SeedSweepRegressionTests(unittest.TestCase):
    """October 1, 2026: a 12,000-game autonomous seed sweep over three
    synthetic fixtures (scripts/research/seed_sweep.py --block october-1)
    found three causes of a refused game. Kernel 2014.6 batch B1 (October 2,
    2026) pins each cause to the real 2012 drive, located in the committed
    2012 base, or to the forced removals that produced it, instead of to a
    kernel seed: a later kernel that draws differently cannot make these
    fixtures hollow."""

    LAYOUT_SEED = b"forced-regression-fixture-not-career-state-00"

    @classmethod
    def setUpClass(cls):
        cls.model = BASE_2012.field_position()
        cls.completion_rate = BASE_2012.aggregate()["derived"]["completion_rate"]["value"]
        cls.usage_values = BASE_2012.usage()["values"]

    def located(self, category, locator, **fields):
        t = self.model.locate_tuple(category, locator)
        self.assertIsNotNone(t, locator)
        for name, value in fields.items():
            self.assertEqual(t[self.model.T[name]], value, (locator, name))
        return t

    def layout(self, category, t, spot, pass_yards, rush_free, label):
        T = self.model.T
        net, _ = self.model.adapt(category, t, spot)
        diagnostics = {}
        out = drive_layout(seed=self.LAYOUT_SEED, event_id=label, drive_no=1, offense="X", category=category,
                           td_type=None, runs=t[T["runs"]], attempts=t[T["attempts"]], sacks=t[T["sacks"]],
                           kneel_yards=list(t[T["kneel_yards"]]), spikes=t[T["spikes"]], pass_yards=pass_yards,
                           rush_free=rush_free, losses=[], safety_terminal=None, net=net, spot=spot,
                           completion_rate=self.completion_rate, targets=list(t[T["chains"]]),
                           term_down=t[T["term_down"]], diagnostics=diagnostics, usage_values=self.usage_values)
        return out, diagnostics, net

    def gated(self, category, t, spot):
        """True when only the chain-feasibility gate keeps tuple t out at the spot."""
        T = self.model.T
        net, _ = self.model.adapt(category, t, spot)
        terminal = self.model.fixed_yardage(category, t)[2]
        with mock.patch.object(chains, "chain_feasible", return_value=True):
            admitted_without_gate = self.model.static_feasible(category, t, spot)
        return (admitted_without_gate and not self.model.static_feasible(category, t, spot)
                and not chain_feasible(category, plays=t[T["plays"]], net=net, spot=spot,
                                       kneel_yards=t[T["kneel_yards"]], sacks=t[T["sacks"]], runs=t[T["runs"]],
                                       terminal_value=terminal))

    def test_relocated_punt_is_concentrated_onto_one_snap(self):
        # Cause 1 (kernel seeds pz-25, samp-835, pz-1345, sw2-749): the real
        # four-snap punt netting 19 behind a penalty first down, replayed
        # from the 97-99 with its end kept (net 51-53). The three snaps after
        # the first down gain nine at most, so one snap carries the rest;
        # every split of the free yards and every layout stream lays it out
        # as a fourth-down punt (drive_layout's concentrated rung).
        t = self.located("punt", ["late", "121-300|lead9", 32], plays=4, net0=19, end=46, runs=3, attempts=1,
                         sacks=0, chains=[0, 1, 1, 0, 0, 0], term_down=4)
        concentrated = 0
        for spot in (97, 98, 99):
            self.assertTrue(self.model.static_feasible("punt", t, spot))
            for pass_yards in (0, 10, 19, 26, 53):
                for k in range(4):
                    net = self.model.adapt("punt", t, spot)[0]
                    pass_yards = min(pass_yards, net)
                    with self.subTest(spot=spot, pass_yards=pass_yards, stream=k):
                        out, diagnostics, net = self.layout("punt", t, spot, pass_yards, net - pass_yards,
                                                            "punt-%d-%d-%d" % (spot, pass_yards, k))
                        self.assertTrue(out["ok"])
                        self.assertNotIn("chain_layout_failed", diagnostics)
                        self.assertEqual(sum(out["values"]), net)
                        self.assertEqual(out["walk"]["state"]["down"], 4)
                        self.assertEqual(out["walk"]["chains"][0], 1)
                        self.assertGreaterEqual(max(out["values"]), net - 9)
                        concentrated += "chain_plan_concentrated" in diagnostics
        self.assertGreater(concentrated, 0)

    def test_five_run_fumble_gains_its_first_down_before_the_fumbled_snap(self):
        # Cause 1b (store seed 44 of tests/test_game_runner.py): the real
        # five-run fumble netting 10 at its own start, the 80. Its first down
        # must come before the fumbled snap, on every layout stream.
        t = self.located("fumble_lost", ["late", "121-300|lead1_8", 1], plays=5, runs=5, attempts=0, sacks=0,
                         start=80, end=70)
        for k in range(8):
            with self.subTest(stream=k):
                out, diagnostics, net = self.layout("fumble_lost", t, 80, 0, 10, "fumble-%d" % k)
                self.assertEqual(net, 10)
                self.assertTrue(out["ok"])
                self.assertNotIn("chain_layout_failed", diagnostics)
                w = walk(80, out["values"], turnover_last=True)
                self.assertEqual((w["chains"][0], w["failed"], w["breaks"]), (1, None, []))
                self.assertFalse(w["rows"][-1]["first_down"])

    def test_fumbled_sack_gate_keeps_the_tuple_out(self):
        # Cause 2 (kernel seeds pz-2103, samp-1482, sw2-2762): the real
        # six-snap, one-sack fumble replayed from the 18 nets -5; six snaps
        # need a first down that no order reaches, so the chain gate (alone)
        # keeps it out of every rung there. At its own start it is feasible.
        t = self.located("fumble_lost", ["late", "121-300|trail9", 4], plays=6, sacks=1, runs=0, attempts=5,
                         start=53, end=23)
        self.assertEqual(self.model.adapt("fumble_lost", t, 18), (-5, 23))
        self.assertTrue(self.gated("fumble_lost", t, 18))
        self.assertTrue(self.model.static_feasible("fumble_lost", t, 53))
        for pool_id in (("late", "121-300|trail9"), ("late_union", "trail9"), ("neutral", self.model.start_bin(18))):
            for rung in self.model._rungs(pool_id, "fumble_lost", 18):
                self.assertFalse(any(x is t for x in rung), pool_id)

    def test_kneel_then_punt_gate_keeps_the_tuple_out(self):
        # Store seed 398 of tests/test_injuries_in_game.py: the real
        # three-snap punt (run, kneel -2, kneel -1, punt) replayed from the
        # 94 nets 8, so its run had to gain 11, a first down, and the punt
        # fell on third down. The gate counts the kneel yards.
        t = self.located("punt", ["late", "121-300|lead9", 10], plays=3, runs=1, attempts=0, kneel_yards=[-2, -1],
                         start=86, end=86)
        self.assertEqual(self.model.adapt("punt", t, 94), (8, 86))
        self.assertTrue(self.gated("punt", t, 94))
        self.assertTrue(self.model.static_feasible("punt", t, 86))

    def test_emergency_passer_keeps_the_job(self):
        # Cause 3 (kernel seeds sweep-706, sweep-1278, sweep-1872; store seed
        # 67): the lone quarterback removed, a running back passing in his
        # place, then the removal of the running back ranked above the
        # filler, which reorders the group. Forced removals reproduce it on
        # any stream; the filler keeps the job (participation.emergency_view).
        a, b = single_quarterback_teams()
        seed = hashlib.sha256(b"forced-emergency-passer").digest()
        event = "forced-emergency-passer"
        base = resolve_game(a, b, seed=seed, event_id=event)
        first = [p["number"] for p in base["possessions"] if p["team"] == "A"][1]
        removal = {"injury_class": "lower_extremity", "severity": "multi_week", "removed": True}
        forced = {(first, "qb"): removal}
        r = resolve_game(a, b, seed=seed, event_id=event, _test_onsets=dict(forced))
        self.assertEqual(validate_result(r), [])
        after = [p for p in r["possessions"] if p["team"] == "A" and p["number"] > first]
        filler = after[0]["passer"]
        self.assertNotEqual(filler, "qb")
        from runtime import usage
        live = [p for p in a.roster if p.available and p.player_id != "qb"]
        ahead = [p.player_id for p in usage.depth_order(live, "RB")]
        self.assertIn(filler, ahead)
        ahead = ahead[:ahead.index(filler)]
        self.assertTrue(ahead, "the filler must have a running back ranked above him")
        second = None
        for p in after[1:]:
            trial = dict(forced)
            trial[(p["number"], ahead[0])] = removal
            try:
                second = resolve_game(a, b, seed=seed, event_id=event, _test_onsets=trial)
            except ValueError:
                continue  # no exposure for him in that interval: try a later drive
            break
        self.assertIsNotNone(second, "no later drive in which the running back could be removed")
        self.assertEqual(validate_result(second), [])
        removed = {i["player"]: i["drive"] for i in second["injuries"] if i["removed"] and i["team"] == "A"}
        self.assertEqual(removed["qb"], first)
        # Until the filler himself is removed (a natural onset may follow
        # the forced ones), he passes on every drive, including those after
        # the reordering removal.
        cutoff = removed.get(filler, float("inf"))
        self.assertLess(removed[ahead[0]], cutoff)
        later = [p for p in second["possessions"] if p["team"] == "A" and first < p["number"] <= cutoff]
        self.assertTrue([p for p in later if p["number"] > removed[ahead[0]]])
        self.assertEqual({p["passer"] for p in later}, {filler})
        for p in later:
            self.assertIn({"group": "QB", "available": 0, "required": 1, "filled_by": filler, "from": "RB"},
                          p["emergency"])


class SeedSweepScriptTests(unittest.TestCase):
    """scripts/research/seed_sweep.py: the frozen A6 block and the October 1
    block, the production entropy derivation and the three fixtures."""

    @classmethod
    def setUpClass(cls):
        import importlib.util
        root = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location("seed_sweep", root / "scripts/research/seed_sweep.py")
        cls.sweep = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.sweep)
        sys.path.insert(0, str(root / "scripts" / "research"))
        import pre_build_specification
        cls.frozen = pre_build_specification.frozen_rules()["seeds"]["sweep"]

    def test_blocks_match_the_frozen_specification(self):
        a6 = self.sweep.labels("a6")
        self.assertEqual(len(a6), self.frozen["games"])
        self.assertEqual(sorted({name for _, name in a6}), sorted(self.frozen["fixture_tokens"]))
        for name in self.frozen["fixture_tokens"]:
            mine = [label for label, fixture in a6 if fixture == name]
            self.assertEqual(len(mine), self.frozen["per_fixture"])
            self.assertEqual(mine[0], self.frozen["pattern"].replace("<fixture>", name).replace("<i>", "0"))
            self.assertEqual(mine[-1], "sweep-2014.6-%s-%d" % (name, self.frozen["per_fixture"] - 1))
        october = dict(self.sweep.labels("october-1"))
        self.assertEqual(len(october), 12000)
        for label in ("pz-25", "samp-835", "sw2-749", "pz-2103", "sweep-706"):
            self.assertIn(label, october)
        self.assertEqual(self.sweep.BLOCKS["a6"][2], "2014.6")

    def test_entropy_and_fixtures_are_the_sweeps(self):
        self.assertEqual(self.sweep.entropy("pz-25"), sweep_entropy("pz-25"))
        for name, source in self.frozen["fixture_tokens"].items():
            module, function = source.split()
            home, away = self.sweep.fixture(name)
            expected = {"single": single_quarterback_teams, "pause": pause_teams, "sample": sample_teams}[name]()
            self.assertEqual((home, away), expected, name)
        row = self.sweep.play(("pz-0", "pause", "2014.5"))
        self.assertEqual((row["label"], row["refused"]), ("pz-0", []))


class FixedSeedSweepTests(unittest.TestCase):
    """A small fixed slice of the October 1, 2026 sweep (its full form is
    scripts/research/seed_sweep.py): the kernel invariants hold."""

    TEAMS = {"sweep": single_quarterback_teams, "pz": pause_teams, "samp": sample_teams}

    def test_fixed_seed_sweep_has_no_invariant_failure(self):
        labels = ["sweep-%d" % i for i in range(16)] + ["pz-%d" % i for i in range(8)] + ["samp-%d" % i for i in range(8)]
        for label in labels:
            with self.subTest(seed=label):
                a, b = self.TEAMS[label.split("-")[0]]()
                r = resolve_game(a, b, seed=sweep_entropy(label), event_id=label)
                self.assertEqual(validate_result(r), [], label)
                self.assertEqual(r["diagnostics"].get("chain_layout_failed", 0), 0)


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


class LayoutResampleTests(unittest.TestCase):
    """Kernel 2014.4 phase 2: when no plan legalises a drawn drive's snaps,
    another real drive of the same category and rung stands in, on the
    drive's own resample stream, recorded in the receipt; the game closes."""

    def failing_layout(self, drive_no):
        real = chains.drive_layout
        calls = {"n": 0}

        def wrapper(**kw):
            if kw["drive_no"] == drive_no:
                calls["n"] += 1
                if calls["n"] == 1:
                    out = real(**kw)
                    out["ok"] = False
                    kw["diagnostics"]["chain_layout_failed"] = kw["diagnostics"].get("chain_layout_failed", 0) + 1
                    return out
            return real(**kw)
        return wrapper, calls

    def test_resample_stands_in_and_the_game_closes(self):
        from runtime import kernel
        a, b = sample_teams()
        seed = SEED + b"-resample-01"
        base = resolve_game(a, b, seed=seed, event_id="resample-1")
        wrapper, calls = self.failing_layout(4)
        with mock.patch.object(kernel.chain_walk, "drive_layout", wrapper):
            first = resolve_game(a, b, seed=seed, event_id="resample-1")
        with mock.patch.object(kernel.chain_walk, "drive_layout", self.failing_layout(4)[0]):
            second = resolve_game(a, b, seed=seed, event_id="resample-1")
        self.assertEqual(validate_result(first), [])
        self.assertEqual(check_ledger(first), [])
        self.assertEqual(first["diagnostics"]["chain_layout_resampled"], 1)
        self.assertEqual(first["diagnostics"]["chain_layout_resample_exhausted"], 0)
        self.assertEqual(first["diagnostics"].get("chain_layout_failed", 0), 0)
        drive = first["possessions"][3]
        rec = drive["layout_resample"]
        self.assertEqual(rec["resamples"], 1)
        self.assertNotEqual(rec["original"]["locator"], rec["final"]["locator"])
        self.assertIsNotNone(rec["original"]["locator"])
        self.assertIsNotNone(rec["final"]["locator"])
        original = base["possessions"][3]
        # The original tuple is the base game's drive (its plays and own seconds).
        self.assertEqual(rec["original"]["tuple"][0], original["scrimmage_plays"])
        self.assertEqual(fp.scaled_seconds(rec["original"]["tuple"]), original["own_seconds"])
        self.assertEqual(drive["category"], original["category"])
        self.assertEqual(drive["start_spot"], original["start_spot"])
        self.assertEqual(drive["chain_model"], chains.CHAIN_MODEL)
        self.assertNotIn("layout_resample", first["possessions"][2])
        # The three drives before it are the base game's; the possession
        # stream is not consumed by the resample.
        self.assertEqual([p["category"] for p in first["possessions"][:3]], [p["category"] for p in base["possessions"][:3]])
        # Determinism: same seed, same resample, same game.
        self.assertEqual(first["possessions"], second["possessions"])
        self.assertEqual(first["final_score"], second["final_score"])
        self.assertEqual(first["play_ledger"], second["play_ledger"])
        # The class is measurable on the result and on a compact receipt, and
        # detects a doctored record.
        from runtime.play_detail import RESAMPLE_CLASSES
        self.assertTrue(set(RESAMPLE_CLASSES) <= measurable_classes(first))
        compact = {k: v for k, v in first.items() if k != "play_ledger"}
        self.assertTrue(set(RESAMPLE_CLASSES) <= measurable_classes(compact))
        doctored = copy.deepcopy(first)
        doctored["possessions"][3]["layout_resample"]["final"] = copy.deepcopy(rec["original"])
        self.assertTrue(any(e.startswith("layout_resample_incoherent") for e in check_ledger(doctored)))
        doctored = copy.deepcopy(first)
        doctored["possessions"][3]["layout_resample"]["original"]["tuple"][0] += 1
        self.assertTrue(any(e.startswith("layout_resample_incoherent") for e in check_ledger(doctored)))
        legacy = copy.deepcopy(first)
        for p in legacy["possessions"]:
            del p["chain_model"]
        self.assertFalse(set(RESAMPLE_CLASSES) & measurable_classes(legacy))

    def test_resample_draws_from_the_same_rung(self):
        pool_id = ("neutral", fp.start_bin(75))
        options = fp.eligible(pool_id, "punt", 75, "h2_neutral", 900)
        drawn = fp.Drive("punt", options[0], fp.scaled_seconds(options[0]), False, "neutral", "h2_neutral",
                         pool_id=pool_id, clock_regime="h2_neutral")
        import random
        alt = fp.resample_drive(random.Random(3), drawn, 75, 900)
        self.assertIsNotNone(alt)
        self.assertEqual(alt.category, "punt")
        self.assertIsNot(alt.tuple, options[0])
        self.assertIn(alt.tuple, options)
        self.assertFalse(alt.consumes_window)
        self.assertEqual(fp.resample_drive(random.Random(3), drawn, 75, 900).tuple, alt.tuple)
        # A drive drawn without a pool (the zero-play expiry) cannot be resampled.
        zero = fp.Drive("clock", fp.ZERO_TUPLE, 0, True, "neutral", "h1_final")
        self.assertIsNone(fp.resample_drive(random.Random(3), zero, 75, 30))
        # Window-ending resamples keep their status and stay time feasible.
        h1 = ("h1_final", fp.h1_key(90))
        finals = fp.eligible(h1, "field_goal_attempt", 40, "h1_final", 90)
        if finals:
            ending = fp.ending_drive("field_goal_attempt", finals[0], 90, "neutral", "h1_final", pool_id=h1,
                                     clock_regime="h1_final")
            alt = fp.resample_drive(random.Random(5), ending, 40, 90)
            if alt is not None:
                self.assertTrue(alt.consumes_window)
                self.assertTrue(fp.time_feasible(alt.tuple, 90))


if __name__ == "__main__":
    unittest.main()
