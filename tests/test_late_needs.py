"""Kernel 2014.6 batch B5, R10 and the late-game diagnostics on the schema-3
model: the specification's eight needs; every late fallback (the need
union, the late clock fallback, _fit_or_expire) masks each category whose
count is zero in the time cell actually drawn; the kernel 2014.1 and 2014.2
late-game diagnostics replayed on the 2010-2014 base with the
specification's tolerances (three standard errors); per-game context in
the draw's extras, never module state; slate-order invariance; and a
static scan of every pooled tuple at its own start spot. Synthetic seeds
only; no career state.
"""
import copy
import json
import hashlib
import random
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import field_position as fp
from runtime.calibration_base import BASE_2010_2014W4
from runtime.kernel import resolve_game, validate_result
from runtime.profiles import PROFILE_2014_6
from synthetic_games import SEED, sample_teams

MODEL = BASE_2010_2014W4.field_position()
T = MODEL.T


def digest(result):
    return hashlib.sha256(json.dumps(result, sort_keys=True, default=str).encode()).hexdigest()


class NeedTests(unittest.TestCase):
    def test_eight_needs_with_the_specification_edges(self):
        rules = BASE_2010_2014W4.specification_rules()["end_of_half"]["NEEDS"]
        self.assertEqual(MODEL.data["preregistration"]["needs"], rules)
        for diff, label in ((-1, "trail1_3"), (-4, "trail4_8"), (-9, "trail9_11"), (-11, "trail9_11"),
                            (-12, "trail12_16"), (-16, "trail12_16"), (-17, "trail17p"), (-40, "trail17p"),
                            (0, "tied"), (8, "lead1_8"), (9, "lead9")):
            self.assertEqual(MODEL.need(diff), label)
        self.assertEqual(MODEL.cell_for(2, 100, -13), "le120|trail12_16")

    def test_zero_cell_categories(self):
        self.assertEqual(MODEL.zero_cell_categories(("late", "le120|trail12_16")), ("field_goal_attempt", "punt", "safety"))


class UnionMaskTests(unittest.TestCase):
    """The union path forced: the cell's own draw is empty, so the need
    union, then the clock fallback and the fit rung, answer, and none of
    them yields a category the drawn time cell never saw."""

    def test_union_path_masks_categories_absent_from_the_cell(self):
        cell = "le120|trail12_16"
        masked = set(MODEL.zero_cell_categories(("late", cell)))
        self.assertIn("field_goal_attempt", masked)
        real = MODEL._draw_from
        rng = random.Random(29)
        seen, union = set(), 0

        def no_cell(rng_, pool_id, *args, **kw):
            if pool_id == ("late", cell):
                return None
            return real(rng_, pool_id, *args, **kw)
        with mock.patch.object(MODEL, "_draw_from", no_cell):
            for _ in range(400):
                spot = rng.randint(1, 99)
                diagnostics = {}
                drive = MODEL.draw_drive(rng, spot, 2, rng.randint(1, 120), -13, 0.0, diagnostics,
                                         timeouts=(rng.randint(0, 3), rng.randint(0, 3)))
                union += diagnostics.get("fallback_need_union", 0)
                seen.add(drive.category)
        self.assertEqual(union, 400)
        self.assertFalse(seen & masked, seen)
        # Without the mask the union would offer field goals: its counts hold some.
        union_counts = MODEL._counts(("late_union", "trail12_16"))
        self.assertGreater(union_counts["field_goal_attempt"], 0)

    def test_fit_rung_masks_too(self):
        diagnostics = {}
        rng = random.Random(31)
        with mock.patch.object(MODEL, "_draw_from", lambda *a, **k: None if k.get("clock_regime") != "fit_late"
                               else fp.FieldPositionModelV3._draw_from(MODEL, *a, **k)), \
                mock.patch.object(MODEL, "_clock_fallback", lambda *a, **k: None):
            for _ in range(200):
                drive = MODEL.draw_drive(rng, rng.randint(20, 90), 2, rng.randint(60, 120), -13, 0.0, diagnostics,
                                         timeouts=(3, 3))
                self.assertNotIn(drive.category, ("field_goal_attempt", "punt", "safety"))
        self.assertGreater(diagnostics.get("fallback_fit_drive", 0), 0)


class LateDiagnosticTests(unittest.TestCase):
    """Kernel 2014.1 and 2014.2 late-game diagnostics on the schema-3 model,
    with the specification's criteria."""

    def test_kneel_drives_replay_only_in_their_start_zone(self):
        for t in [t for c in fp.CATEGORIES for t in fp._v3_tuples(MODEL.data, c) if t[T["kneel_yards"]]][::5]:
            category = next(c for c in fp.CATEGORIES if any(x is t for x in fp._v3_tuples(MODEL.data, c)))
            for spot in (5, 30, 55, 70, 85, 95):
                if MODEL.static_feasible(category, t, spot):
                    self.assertEqual(MODEL.zone(spot), MODEL.zone(t[T["start"]]))

    def test_every_pooled_tuple_carries_timeout_counts(self):
        for c in fp.CATEGORIES:
            for t in fp._v3_tuples(MODEL.data, c):
                for name in ("off_timeouts", "def_timeouts", "off_timeouts_used", "def_timeouts_used"):
                    self.assertIsInstance(t[T[name]], int, name)

    def test_replayed_late_states_track_the_real_mix_by_need(self):
        # Every real late drive (Q4, 600 s or less), replayed once from its own
        # state, by need group: the drawn punt and field-goal shares stay
        # within three standard errors of the real shares.
        rng = random.Random(37)
        groups = {"trailing 1-8": ("trail1_3", "trail4_8"), "trailing 9-16": ("trail9_11", "trail12_16"),
                  "leading": ("lead1_8", "lead9")}
        for label, needs in groups.items():
            real = {"punt": 0, "field_goal_attempt": 0}
            drawn = dict(real)
            n = 0
            for cell in MODEL._need_cells(needs[0]) + MODEL._need_cells(needs[1]):
                for category in fp.CATEGORIES:
                    for t in MODEL.data["pools"]["late"][cell][category]:
                        n += 1
                        if category in real:
                            real[category] += 1
                        drive = MODEL.draw_drive(rng, t[T["start"]], 2, t[T["t0"]], t[T["score_diff"]], 0.0, {},
                                                 timeouts=(t[T["off_timeouts"]], t[T["def_timeouts"]]))
                        if drive.category in drawn:
                            drawn[drive.category] += 1
            for category in real:
                p = real[category] / n
                tolerance = 3 * (p * (1 - p) / n) ** 0.5
                self.assertLessEqual(abs(drawn[category] / n - p), max(tolerance, 3 / n),
                                     "%s %s: %.3f against %.3f" % (label, category, drawn[category] / n, p))


class StaticScanTests(unittest.TestCase):
    def test_pooled_tuples_at_their_own_start(self):
        """Every pooled tuple starts at an admitted spot (1-99); nearly all
        replay at their own start; every (pool, category) with a count has a
        tuple feasible at one of its own starts."""
        total = bad = 0
        for kind in ("neutral", "h1_late", "late", "ot_first", "ot_sudden"):
            cells = (enumerate(MODEL.data["pools"]["neutral"]) if kind == "neutral"
                     else MODEL.data["pools"][kind].items() if kind in ("h1_late", "late")
                     else [(None, MODEL.data["pools"][kind])])
            for key, cell in cells:
                for index, category in enumerate(fp.CATEGORIES):
                    pool = cell[index] if kind == "neutral" else cell[category]
                    feasible = 0
                    for t in pool:
                        total += 1
                        self.assertTrue(1 <= t[T["start"]] <= 99)
                        ok = MODEL.static_feasible(category, t, t[T["start"]])
                        feasible += ok
                        bad += not ok
                    if pool:
                        self.assertGreater(feasible, 0, (kind, key, category))
        self.assertEqual(total, dict(BASE_2010_2014W4.partitions)["field_position.pooled_tuples"])
        self.assertLess(bad / total, 0.02, "%d of %d infeasible at their own start" % (bad, total))


class ContextTests(unittest.TestCase):
    """Per-game context (the overtime history, the walk-off flag) travels in
    the draw's extras; no module or model state carries it between games."""

    def test_tied_overtime_draw_requires_its_context(self):
        with self.assertRaises(ValueError):
            MODEL.draw_drive(random.Random(1), 75, "OT", 600, 0, 0.0, {}, timeouts=(2, 2), extra={})
        first = MODEL.draw_drive(random.Random(1), 75, "OT", 600, 0, 0.0, {}, timeouts=(2, 2),
                                 extra={"ot_history_empty": True})
        later = MODEL.draw_drive(random.Random(1), 75, "OT", 600, 0, 0.0, {}, timeouts=(2, 2),
                                 extra={"ot_history_empty": False})
        self.assertEqual(first.pool_id[0], "ot_first")
        self.assertEqual(later.pool_id[0], "ot_sudden")

    def test_walk_off_flag_isolation_and_slate_order(self):
        a, b = sample_teams()
        seeds = [(SEED + b"-b5-ctx-%02d" % i, "b5-ctx-%d" % i) for i in range(4)]
        state = lambda: {k: v for k, v in vars(fp).items()  # noqa: E731
                         if not k.startswith("__") and isinstance(v, (dict, list, set))}
        module_state = state()
        snapshot = copy.deepcopy(module_state)
        forward = [digest(resolve_game(a, b, seed=s, event_id=e, _test_profile=PROFILE_2014_6)) for s, e in seeds]
        backward = [digest(resolve_game(a, b, seed=s, event_id=e, _test_profile=PROFILE_2014_6))
                    for s, e in reversed(seeds)][::-1]
        self.assertEqual(forward, backward)
        self.assertEqual(state(), snapshot)
        # The extras the kernel passes name the context.
        seen = []
        real = MODEL.draw_drive

        def spy(rng, spot, half, window, diff, edge, diagnostics, timeouts=None, extra=None):
            seen.append((half, dict(extra or {})))
            return real(rng, spot, half, window, diff, edge, diagnostics, timeouts, extra)
        with mock.patch.object(MODEL, "draw_drive", spy):
            resolve_game(a, b, seed=seeds[0][0], event_id=seeds[0][1], _test_profile=PROFILE_2014_6)
        self.assertTrue(all({"ot_history_empty", "walk_off_fg"} <= set(x) for _, x in seen))
        self.assertTrue(all(not x["walk_off_fg"] and not x["ot_history_empty"] for h, x in seen if h != "OT"))


if __name__ == "__main__":
    unittest.main()
