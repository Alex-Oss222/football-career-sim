"""Kernel 2014.1: charged timeouts, kneel start zones and goal-to-go distances."""
import sys
import unittest
from pathlib import Path

from runtime import field_position as fp
from runtime.play_detail import check_ledger, has_timeouts
from runtime.rules import RULES

sys.path.insert(0, str(Path(__file__).resolve().parent))
from synthetic_games import sample  # noqa: E402

T = fp.T


def _with(t, **fields):
    t = list(t)
    for name, value in fields.items():
        t[T[name]] = value
    return tuple(t)


class LadderTests(unittest.TestCase):
    def setUp(self):
        base = next(t for cells in fp.load()["pools"]["late"].values() for pool in cells.values() for t in pool)
        self.t = _with(base, off_timeouts=2, def_timeouts=0)

    def test_levels(self):
        match = fp.timeout_match
        self.assertTrue(match(0, self.t, (2, 0), "def"))
        self.assertFalse(match(0, self.t, (3, 0), "def"))
        self.assertTrue(match(1, self.t, (3, 0), "def"))   # defence (clock-stopping side) exact
        self.assertFalse(match(1, self.t, (2, 1), "def"))
        self.assertTrue(match(1, self.t, (2, 3), "off"))   # trailing offence exact
        self.assertTrue(match(2, self.t, (1, 3), "off"))   # offence band 1-2
        self.assertFalse(match(2, self.t, (3, 0), "off"))
        self.assertTrue(match(3, self.t, (0, 3), "off"))

    def test_tuples_without_counts_match_only_unconditioned(self):
        t = _with(self.t, off_timeouts=None)
        self.assertFalse(any(fp.timeout_match(level, t, (2, 0), "def") for level in range(3)))
        self.assertTrue(fp.timeout_match(3, t, (2, 0), "def"))

    def test_every_2012_tuple_carries_counts(self):
        data = fp.load()
        tuples = [t for b in data["pools"]["neutral"] for c in b for t in c]
        tuples += [t for cells in data["pools"]["late"].values() for pool in cells.values() for t in pool]
        self.assertTrue(all(t[T["off_timeouts"]] in (0, 1, 2, 3) and t[T["def_timeouts"]] in (0, 1, 2, 3)
                            for t in tuples))
        self.assertTrue(all(0 <= t[T["off_timeouts_used"]] <= 3 and 0 <= t[T["def_timeouts_used"]] <= 3
                            for t in tuples))


class KneelZoneTests(unittest.TestCase):
    def test_kneel_drive_replays_only_in_its_start_zone(self):
        data = fp.load()
        kneel = next(t for cells in data["pools"]["h1_final"].values() for t in cells["clock"]
                     if t[T["kneel_yards"]] and fp.zone(t[T["start"]]) == "A")
        spot = kneel[T["start"]]
        self.assertTrue(fp.static_feasible("clock", kneel, spot))
        self.assertFalse(fp.static_feasible("clock", kneel, 5))   # the opponent's 5: zone C
        self.assertEqual(fp._clock_fallback.__name__, "_clock_fallback")


class KernelTimeoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = sample()

    def test_every_possession_carries_a_coherent_timeout_state(self):
        for result in self.results:
            self.assertTrue(has_timeouts(result))
            errors = [e for e in check_ledger(result) if e.startswith(("timeout_state_invalid", "fourth_down_beyond_goal"))]
            self.assertEqual(errors, [], result["event_id"])

    def test_halves_open_with_three_and_timeouts_are_used(self):
        used = 0
        for result in self.results:
            for half in (1, 2):
                first = next(p for p in result["possessions"] if p["half"] == half)
                self.assertEqual(first["timeouts"][:2], [RULES.timeouts_per_half] * 2)
            used += sum(p["timeouts"][2] + p["timeouts"][3] for p in result["possessions"])
        self.assertGreater(used, 0)

    def test_regular_overtime_opens_with_two(self):
        seen = 0
        for result in self.results:
            ot = [p for p in result["possessions"] if p["half"] == "OT"]
            if ot:
                seen += 1
                self.assertEqual(ot[0]["timeouts"][:2], [RULES.regular_ot_timeouts] * 2)
        self.assertGreater(seen, 0)

    def test_fourth_down_distance_never_passes_the_goal_line(self):
        for result in self.results:
            for p in result["possessions"]:
                fourth = p.get("fourth_down")
                if fourth and fourth["ydstogo"] is not None:
                    self.assertLessEqual(fourth["ydstogo"], fourth["los"])
                    self.assertIn("goal_to_go", fourth)

    def test_late_draws_use_the_ladder(self):
        levels = {p["timeout_level"] for r in self.results for p in r["possessions"]
                  if p["half"] == 2 and p["cell"] != "neutral"}
        self.assertTrue(levels & {0, 1, 2})


if __name__ == "__main__":
    unittest.main()
