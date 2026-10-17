"""Kernel 2014.6 batch B5, R17 and R7: the first-half late regime of the
schema-3 model (runtime.field_position.FieldPositionModelV3).

Every first-half possession with a window at or under H1_LATE_SECONDS draws
from h1_late tuples whose own start lies within TIME_MATCH_SECONDS of the
window (else the fallback width, counted), then the bucket cell, the union,
a time-feasible clock final and the fit-or-expiry rung; over
H1_LATE_SECONDS the fitting neutral draw is the primary path. Synthetic
seeds only; no career state.
"""
import json
import random
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import chains
from runtime import field_position as fp
from runtime.calibration_base import BASE_2010_2014W4
from runtime.kernel import resolve_game, validate_result
from runtime.profiles import PROFILE_2014_6
from synthetic_games import SEED, sample_teams

MODEL = BASE_2010_2014W4.field_position()
T = MODEL.T


def games(n, tag):
    a, b = sample_teams()
    return [resolve_game(a, b, seed=SEED + b"-b5-%s-%03d" % (tag.encode(), i), event_id="b5-%s-%d" % (tag, i),
                         _test_profile=PROFILE_2014_6) for i in range(n)]


class ConstantsTests(unittest.TestCase):
    def test_constants_are_the_specification_s(self):
        rules = BASE_2010_2014W4.specification_rules()["end_of_half"]
        self.assertEqual(MODEL.H1_LATE_SECONDS, rules["H1_LATE_SECONDS"])
        self.assertEqual(MODEL.TIME_MATCH, (rules["TIME_MATCH_SECONDS"], rules["TIME_MATCH_FALLBACK_SECONDS"]))
        self.assertEqual(MODEL.SPIKE_WINDOW, rules["SPIKE_WINDOW"])
        self.assertEqual(rules["FINAL_FEASIBLE_SLACK_SECONDS"], fp.CLOCK_EXPIRY_ALLOWANCE)
        self.assertEqual([list(e) for e in MODEL.H1_LATE_EDGES], rules["H1_LATE_EDGES"])

    def test_h1_late_cell_label_cannot_parse_as_a_need(self):
        for window in (1, 30, 31, 600):
            cell = MODEL.cell_for(1, window, -3)
            self.assertTrue(cell.startswith("h1_late:"))
            self.assertIsNone(MODEL.cell_need(cell))
        self.assertEqual(MODEL.cell_for(1, 601, -3), "neutral")


class WindowOverSixHundredTests(unittest.TestCase):
    def test_a_window_over_600_never_ends_the_window(self):
        rng = random.Random(5)
        for i in range(400):
            window = rng.randint(601, 1800)
            spot = rng.randint(1, 99)
            drive = MODEL.draw_drive(rng, spot, 1, window, rng.randint(-14, 14), 0.0, {},
                                     timeouts=(rng.randint(0, 3), rng.randint(0, 3)))
            self.assertFalse(drive.consumes_window, (window, spot))
            self.assertLess(drive.seconds, window)
            self.assertFalse(drive.tuple[T["final"]])
            self.assertNotEqual(drive.category, "clock")

    def test_an_empty_neutral_fit_still_draws(self):
        # With w > 600 and the fitting neutral draw empty, the clock and fit
        # rungs answer (a zero-play possession only within the allowance).
        rng = random.Random(9)
        real = MODEL._draw_from
        calls = {"n": 0}

        def no_fit(*args, **kw):
            if kw.get("clock_regime") == "fit_h1" and calls["n"] == 0:
                calls["n"] += 1
                return None
            return real(*args, **kw)
        diagnostics = {}
        with mock.patch.object(MODEL, "_draw_from", no_fit):
            drive = MODEL.draw_drive(rng, 75, 1, 900, 0, 0.0, diagnostics, timeouts=(3, 3))
        self.assertEqual(diagnostics.get("h1_neutral_infeasible"), 1)
        self.assertLess(drive.seconds, 900)
        self.assertNotEqual(drive.fallback, "zero")


class TimeMatchTests(unittest.TestCase):
    def test_membership_is_exactly_the_window(self):
        rng = random.Random(3)
        for _ in range(60):
            window, spot = rng.randint(1, 600), rng.randint(1, 99)
            for category in fp.CATEGORIES:
                got = MODEL.eligible(("h1_late", MODEL.h1_key(window)), category, spot, "h1_late", window, 40)
                self.assertTrue(all(abs(t[T["t0"]] - window) <= 40 for t in got))
                # The ladder's first feasible rung, filtered by the match.
                for rung in MODEL._rungs(("h1_late_union", None), category, spot):
                    expected = MODEL._dynamic(tuple(t for t in rung if abs(t[T["t0"]] - window) <= 40),
                                              category, "h1_late", window)
                    if expected:
                        self.assertEqual(got, expected)
                        break
                else:
                    self.assertEqual(got, ())
            counts = MODEL._window_counts(window, 40)
            for category in fp.CATEGORIES:
                members = MODEL._members(("h1_late_union", None), category)
                self.assertEqual(counts[category], sum(abs(t[T["t0"]] - window) <= 40 for t in members))

    def test_finals_are_time_feasible_and_non_finals_fit(self):
        rng = random.Random(11)
        for _ in range(500):
            window, spot = rng.randint(1, 600), rng.randint(1, 99)
            drive = MODEL.draw_drive(rng, spot, 1, window, rng.randint(-10, 10), 0.0, {},
                                     timeouts=(rng.randint(0, 3), rng.randint(0, 3)))
            if drive.tuple is fp.ZERO_TUPLE:
                self.assertLessEqual(window, fp.CLOCK_EXPIRY_ALLOWANCE)
                continue
            if drive.consumes_window:
                self.assertTrue(drive.tuple[T["final"]])
                self.assertTrue(MODEL.time_feasible(drive.tuple, window))
                self.assertEqual(drive.seconds, window)
            else:
                self.assertLess(drive.seconds, window)
                self.assertFalse(drive.tuple[T["final"]])
            if drive.match_width is not None:
                self.assertLessEqual(abs(drive.tuple[T["t0"]] - window), drive.match_width)
                self.assertEqual(drive.pool_id, ("h1_late", MODEL.h1_key(window)))

    def test_replaying_real_states_reproduces_p_final(self):
        # Each real first-half drive starting with 61-120 or 121-240 s left,
        # replayed once from its own state, ends the half about as often as
        # the real drives did (the band centre, 3 standard errors).
        centres = MODEL.data["band_centres"]
        rng = random.Random(17)
        for low, high in ((61, 120), (121, 240)):
            states = [t for c in fp.CATEGORIES for t in MODEL._members(("h1_late_union", None), c)
                      if low <= t[T["t0"]] <= high]
            finals = 0
            for t in states:
                drive = MODEL.draw_drive(rng, t[T["start"]], 1, t[T["t0"]], t[T["score_diff"]], 0.0, {},
                                         timeouts=(t[T["off_timeouts"]], t[T["def_timeouts"]]))
                finals += drive.consumes_window
            made, n = centres["h1_p_final:%d-%d" % (low, high)]["pooled"]
            p = made / n
            observed = finals / len(states)
            self.assertLessEqual(abs(observed - p), 3 * (p * (1 - p) / len(states)) ** 0.5,
                                 "%d-%d: %.3f against %.3f" % (low, high, observed, p))

    def test_the_rung_cache_stays_bounded(self):
        rng = random.Random(23)
        for _ in range(300):
            MODEL.draw_drive(rng, rng.randint(1, 99), 1, rng.randint(1, 600), 0, 0.0, {}, timeouts=(3, 3))
        kinds = {key[0][0] for key in MODEL._rungs_cache}
        self.assertTrue(kinds <= {"neutral", "h1_late", "h1_late_union", "late", "late_union", "ot_first",
                                  "ot_sudden"}, kinds)
        # Keyed by (pool, category, spot) only: no window in any key.
        pools = {key[0] for key in MODEL._rungs_cache}
        self.assertLessEqual(len(MODEL._rungs_cache), len(pools) * len(fp.CATEGORIES) * 99)


class ClockZoneTests(unittest.TestCase):
    """R7: a clock tuple replays only where its end decision zone is its
    real end zone, in every regime and in the clock fallback."""

    def test_clock_tuples_keep_their_end_zone(self):
        tuples = [t for t in fp._v3_tuples(MODEL.data, "clock")]
        self.assertGreater(len(tuples), 1000)
        for t in tuples[::7]:
            for spot in range(1, 100, 6):
                net, end = MODEL.adapt("clock", t, spot)
                if MODEL.static_feasible("clock", t, spot):
                    self.assertEqual(MODEL.decision_zone(end), MODEL.decision_zone(t[T["end"]]))

    def test_clock_expired_first_halves_end_in_their_real_zone(self):
        for r in games(6, "zone"):
            for p in r["possessions"]:
                if p["half"] == 1 and p.get("half_final") and p["category"] == "end_of_half" and p["scrimmage_plays"]:
                    self.assertIn(MODEL.decision_zone(p["end_spot"]), ("own_half", "opp_49_35", "opp_34_1"))


class ForcedResampleTests(unittest.TestCase):
    """A forced layout resample in each regime closes a game that passes
    validate_result after a JSON round trip."""

    @staticmethod
    def regime(p):
        cell = p["cell"]
        if p["half"] == "OT":
            return "ot"
        if cell.startswith("h1_late:"):
            return "h1_late"
        if cell == "neutral":
            return "h1_neutral" if p["half"] == 1 else "h2_neutral"
        return "late"

    @staticmethod
    def failing(drive_no):
        real = chains.drive_layout
        state = {"n": 0}

        def wrapper(**kw):
            if kw["drive_no"] == drive_no and state["n"] == 0:
                state["n"] += 1
                out = real(**kw)
                out["ok"] = False
                return out
            return real(**kw)
        return wrapper

    def test_forced_resample_in_each_regime(self):
        from runtime import kernel
        a, b = sample_teams()
        seen = {}
        for i in range(12):
            seed, event = SEED + b"-b5-resample-%02d" % i, "b5-resample-%d" % i
            base = resolve_game(a, b, seed=seed, event_id=event, _test_profile=PROFILE_2014_6)
            for p in base["possessions"]:
                regime = self.regime(p)
                if regime in seen or not p["scrimmage_plays"]:
                    continue
                with mock.patch.object(kernel.chain_walk, "drive_layout", self.failing(p["number"])):
                    forced = resolve_game(a, b, seed=seed, event_id=event, _test_profile=PROFILE_2014_6)
                drive = forced["possessions"][p["number"] - 1]
                if "layout_resample" not in drive:
                    continue
                trip = json.loads(json.dumps(forced))
                self.assertEqual(validate_result(trip), [], regime)
                rec = drive["layout_resample"]
                if regime == "h1_late" and rec.get("match_width") is not None:
                    self.assertIn(rec["match_width"], MODEL.TIME_MATCH)
                seen[regime] = p["number"]
            if len(seen) == 5:
                break
        self.assertTrue({"h1_late", "h1_neutral", "h2_neutral", "late"} <= set(seen), seen)


class SampleTests(unittest.TestCase):
    def test_sample_games_validate_and_report_no_zero_tuple(self):
        for r in games(8, "sample"):
            self.assertEqual(validate_result(r), [])
            self.assertEqual(r["diagnostics"].get("fallback_zero_tuple", 0), 0)
            self.assertNotIn("interior_clock_redirected", {k for k, v in r["diagnostics"].items() if v})


if __name__ == "__main__":
    unittest.main()
