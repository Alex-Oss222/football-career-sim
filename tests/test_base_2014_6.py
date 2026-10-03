"""Kernel 2014.6 batch B5: the 2010-2014 calibration base and its schema-3
readers (per-base model tests).

The base pins its artifacts and the pre-build specification; the readers
(DriveModelV2, FieldPositionModelV3, the schema-3 aggregate and injury
validators) fail closed on a changed artifact; the kernel's numbers come
from the base (the per-play penalty counter stays the 2012 factor until
R11); the 2014.6 band cohort is graded on this base with its own rows, and
the closed 2012-base cohorts keep theirs. Synthetic seeds only.
"""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import bands, calibration, drive_model, field_position as fp, injury_model
from runtime.calibration_base import BASE_2010_2014W4, BASE_2012
from runtime.kernel import resolve_game
from runtime.profiles import PROFILE_2014_5, PROFILE_2014_6
from runtime.statbook import make_receipt
from synthetic_games import SEED, sample_teams

BASE = BASE_2010_2014W4


class ReaderTests(unittest.TestCase):
    def test_models_by_schema(self):
        self.assertIsInstance(BASE.field_position(), fp.FieldPositionModelV3)
        self.assertIsInstance(BASE.drive_model(), drive_model.DriveModelV2)
        self.assertIs(type(BASE_2012.field_position()), fp.FieldPositionModel)
        self.assertIs(type(BASE_2012.drive_model()), drive_model.DriveModel)
        with self.assertRaises(ValueError):
            fp.model_class("no-such-schema")
        with self.assertRaises(ValueError):
            drive_model.model_class("no-such-schema")

    def test_numbers_come_from_the_base(self):
        dm = BASE.drive_model()
        rates = BASE.drive_model().load()["rates"]
        self.assertEqual(dm.rate("extra_point"), rates["extra_point"][0] / rates["extra_point"][1])
        self.assertEqual(dm.data["clock_scale"], BASE.field_position().data["clock_scale"])
        fgd = dm.load()["field_goal_distance"]
        self.assertEqual(dm.fg_distance_model()["slope"], fgd["slope_per_yard"])
        made, n = BASE.field_position().data["band_centres"]["sacks_per_dropback"]["pooled"]
        self.assertEqual(BASE.field_position().sack_rate_base(), made / n)
        k = calibration.kernel_rates(BASE.aggregate(), BASE_2012.aggregate())
        derived = BASE.aggregate()["derived"]
        self.assertEqual(k["completion_rate"], derived["completion_rate"]["pooled"][0] / derived["completion_rate"]["pooled"][1])
        # R11 owns the penalty counter (batch B11): the 2012 factor stays.
        self.assertEqual(k["penalty_per_play"], BASE_2012.aggregate()["model"]["penalty_per_play"])
        with self.assertRaises(ValueError):
            calibration.kernel_rates(BASE.aggregate())
        for name in ("interior_probs", "half_final_probs", "net_range", "clock_tuple"):
            with self.assertRaises(NotImplementedError):
                getattr(dm, name)("x")

    def test_validators_fail_closed(self):
        fpm = BASE.field_position()
        rules = BASE.specification_rules()["end_of_half"]
        good = BASE.fresh("field_position")
        expected = dict(BASE.partitions)["field_position.drives"]
        spec = BASE.pin("specification").sha256
        self.assertEqual(fp.validate_v3(good, BASE.drive_model().data, expected, spec, rules), [])
        for mutate in (lambda d: d.update(specification_sha256="0" * 64),
                       lambda d: d["preregistration"].update(needs={}),
                       lambda d: d["constants"]["spike_window"].update(specification=999),
                       lambda d: d.update(clock_scale=[1, 1]),
                       lambda d: d["kickoff_pool"].pop(0),
                       lambda d: d["pools"]["late"]["le120|tied"]["clock"].append(d["pools"]["late"]["le120|tied"]["clock"][0])):
            bad = copy.deepcopy(good)
            mutate(bad)
            self.assertTrue(fp.validate_v3(bad, BASE.drive_model().data, expected, spec, rules))
        dm = BASE.fresh("drive_model")
        self.assertEqual(drive_model.validate_v2(dm), [])
        dm["rates"]["fg_by_distance"]["<30"][0] += 1
        self.assertTrue(drive_model.validate_v2(dm))
        inj = BASE.fresh("injury")
        self.assertEqual(injury_model.validate(inj), [])
        inj["recommended"]["position_relative_risk_per_snap"]["slot_mix"]["QB"] = 2.0
        self.assertIn("declared slot mix differs from participation.SCRIMMAGE_SLOT_MIX", injury_model.validate(inj))
        agg = BASE.fresh("aggregate")
        self.assertEqual(calibration.validate(agg, base=BASE), [])
        del agg["volume"]["plays_per_team_game"]
        self.assertTrue(calibration.validate(agg, base=BASE))
        self.assertIs(fpm, BASE.field_position())

    def test_retained_kicks_are_not_drawn(self):
        fpm = BASE.field_position()
        K, P = fpm.KICK, fpm.PUNT
        self.assertEqual(len(fpm.data["kickoff_pool"]) - len(fpm._kick_pools["kickoff_pool"]),
                         len(fpm.data["retained_kick_pools"]["kickoff"]))
        self.assertTrue(all(r[K["possession"]] == "receiving" for r in fpm._kick_pools["kickoff_pool"]))
        self.assertTrue(all(r[P["possession"]] == "receiving" for r in fpm._punt_pool))
        self.assertEqual(len(fpm._kick_pools["kickoff_pool"]),
                         fpm.data["band_centres"]["kickoff_touchback_share"]["pooled"][1])

    def test_locators_round_trip_every_pool_kind(self):
        fpm = BASE.field_position()
        data = fpm.data
        samples = [("neutral", data["pools"]["neutral"][3][2][5], "punt"),
                   ("h1_late", data["pools"]["h1_late"]["0-30"]["clock"][3], "clock"),
                   ("late", data["pools"]["late"]["le120|trail1_3"]["touchdown"][1], "touchdown"),
                   ("ot_first", data["pools"]["ot_first"]["punt"][0], "punt"),
                   ("ot_sudden", data["pools"]["ot_sudden"]["field_goal_attempt"][0], "field_goal_attempt")]
        for kind, t, category in samples:
            locator = fpm.tuple_locator(category, t)
            self.assertEqual(locator[0], kind)
            self.assertIs(fpm.locate_tuple(category, locator), t)
            self.assertTrue(fpm._counts(tuple(locator[:2])))
        self.assertIsNone(fpm.locate_tuple("punt", ["h1_final", "0-30", 0]))

    def test_snap_ranges_cover_every_pool(self):
        ranges = BASE.field_position().snap_seconds_range()
        self.assertEqual(ranges[0][0], 0)
        self.assertGreater(max(ranges), 15)


class InjuryAndUsageSwitchTests(unittest.TestCase):
    def test_flags_choose_the_blocks(self):
        self.assertIs(PROFILE_2014_6.injury_base(BASE), BASE)
        self.assertIs(PROFILE_2014_6.usage_base(BASE), BASE)
        self.assertIs(PROFILE_2014_5.injury_base(BASE_2012), BASE_2012)
        from runtime.profiles import Profile
        bare = Profile("2014.6", base="2010_2014w4", cell_rules="2014.6", strength="honours-production-v3",
                       flags=frozenset({"base_2014_6", "regimes_v3"}))
        self.assertIs(bare.injury_base(BASE), BASE_2012)
        self.assertIs(bare.usage_base(BASE), BASE_2012)

    def test_usage_is_credit_only(self):
        # The usage shares change who is credited, never the possession record.
        from runtime.profiles import Profile
        no_usage = Profile("2014.6", base="2010_2014w4", cell_rules="2014.6", strength="honours-production-v3",
                           flags=frozenset({"base_2014_6", "regimes_v3", "injury_2014_6"}), record_base=True)
        a, b = sample_teams()
        for i in range(3):
            seed = SEED + b"-b5-usage-%d" % i
            with_usage = resolve_game(a, b, seed=seed, event_id="b5-usage-%d" % i, _test_profile=PROFILE_2014_6)
            without = resolve_game(a, b, seed=seed, event_id="b5-usage-%d" % i, _test_profile=no_usage)
            for key in ("final_score", "kickoffs"):
                self.assertEqual(with_usage[key], without[key])
            strip = lambda ps: [{k: v for k, v in p.items() if k not in ("passer",)} for p in ps]  # noqa: E731
            self.assertEqual(strip(with_usage["possessions"]), strip(without["possessions"]))


class CohortBandTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        a, b = sample_teams()
        cls.receipts = []
        for i in range(10):
            r = resolve_game(a, b, seed=SEED + b"-b5-band-%02d" % i, event_id="b5-band-%d" % i,
                             _test_profile=PROFILE_2014_6)
            receipt = make_receipt(r, week=5, matchup="B at A", detail="compact_stats")
            receipt["possessions"] = r["possessions"]
            cls.receipts.append(receipt)

    def test_2014_6_rows_are_graded_on_their_own_base(self):
        _, drive_rows = bands.audit_drive_model(self.receipts, cohort="2014.6")
        metrics = [m for m, *_ in drive_rows]
        self.assertNotIn("kick returns per team game", metrics)
        centres = BASE.field_position().data["band_centres"]
        share = dict((m, c) for m, _, c, _, _ in drive_rows)
        made, n = centres["drive_share:touchdown"]["pooled"]
        self.assertAlmostEqual(share["drive share: touchdown"], made / n)
        _, fp_rows = bands.audit_field_position(self.receipts, cohort="2014.6")
        names = [m for m, *_ in fp_rows]
        for metric in ("timeouts per team-game", "trailing overtime punts (zero tolerance)",
                       "first-half final possessions: field-goal-attempt share",
                       "overtime spikes with more than 148 s left (zero tolerance)",
                       "P(final | first-half possession starting with 61-120 s left)"):
            self.assertIn(metric, names)
        _, injury_rows = bands.audit_injuries(self.receipts, cohort="2014.6")
        self.assertEqual(len(injury_rows), len(bands.INJURY_ROWS))
        _, usage_rows = bands.audit(self.receipts, cohort="2014.6")
        volume = BASE.aggregate()["volume"]["points_per_team_game"]["pooled"]
        self.assertAlmostEqual(dict((m, c) for m, _, c, _, _ in usage_rows)["points per team game"],
                               volume[0] / volume[1])
        checked, counts = bands.coherence(self.receipts, cohort="2014.6")
        self.assertEqual(checked, len(self.receipts))
        self.assertEqual({cls: n for cls, n, _ in counts if n}, {})

    def test_the_2012_cohorts_have_no_new_rows(self):
        from test_calibration_base import committed_receipts
        closed = [r for r in committed_receipts() if r.get("kernel_version") == "2014.5"]
        self.assertTrue(closed)
        _, fp_rows = bands.audit_field_position(closed, cohort="2014.5")
        names = [m for m, *_ in fp_rows]
        self.assertNotIn("timeouts per team-game", names)
        self.assertEqual(bands.audit_injuries(closed, cohort="2014.5"), (0, []))
        _, drive_rows = bands.audit_drive_model(closed, cohort="2014.5")
        self.assertIn("kick returns per team game", [m for m, *_ in drive_rows])

if __name__ == "__main__":
    unittest.main()
