"""Kernel 2014.6 plumbing (batch B1): versioned calibration bases.

The explicit kernel-to-base table, the 2012 base's sha256 and partition
pins (verified at load, failing closed), two bases used in one process in
either order without one's memoised helpers reaching the other, dispatch of
every audit by the receipt's own kernel version, and a mixed-base cohort
that raises."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import copy
import hashlib
import json
import random
import tempfile
import unittest

from runtime import bands, calibration, drive_model, field_position as fp, injury_model, usage
from runtime.calibration_base import (
    BASE_2012, BASES, KERNEL_BASES, PENDING_BASES, CalibrationBase, CalibrationBaseError, Pin,
    base_for_kernel, base_for_result, base_of_kernel, cohort_base, get_base, record,
)
from runtime.kernel import resolve_game, validate_result
from runtime.play_detail import check_ledger
from runtime.profiles import PROFILE_2014_5, Profile
from runtime.seasons import SeasonPaths
from synthetic_games import SEED, sample_teams

ROOT = Path(__file__).resolve().parents[1]
RELEASED = ("2013.4", "2013.5", "2013.6", "2013.7", "2013.8", "2013.9", "2013.10", "2013.11",
            "2014.1", "2014.2", "2014.3", "2014.4", "2014.5")


def committed_receipts():
    out = []
    for year in (2013, 2014):
        paths = SeasonPaths(year, ROOT)
        for folder in (paths.receipts, paths.postseason_receipts, paths.preseason_receipts):
            out += [json.loads(p.read_text()) for p in sorted(Path(folder).glob("*.json"))]
    return out


def synthetic_base(root, name="synthetic", mutate=None, role="field_position", partitions=None):
    """A copy of the 2012 base under `root`, one artifact optionally
    mutated (its pin recomputed): a second base for isolation tests."""
    files = []
    for each, pin in BASE_2012.files:
        target = Path(root) / pin.path
        target.parent.mkdir(parents=True, exist_ok=True)
        data = (ROOT / pin.path).read_bytes()
        if mutate is not None and each == role:
            parsed = json.loads(data)
            mutate(parsed)
            data = json.dumps(parsed).encode()
        target.write_bytes(data)
        files.append((each, Pin(pin.path, hashlib.sha256(data).hexdigest())))
    return CalibrationBase(name=name, cell_rules=BASE_2012.cell_rules, files=tuple(files),
                           partitions=BASE_2012.partitions if partitions is None else partitions, root=Path(root))


def reverse_kickoffs(data):
    data["kickoff_pool"] = list(reversed(data["kickoff_pool"]))


def digest(result):
    return hashlib.sha256(json.dumps(result, sort_keys=True, default=str).encode()).hexdigest()


class MappingTests(unittest.TestCase):
    def test_every_released_kernel_maps_to_the_2012_base(self):
        for version in RELEASED:
            self.assertEqual(base_for_kernel(version), "2012", version)
            self.assertIs(base_of_kernel(version), BASE_2012)
        self.assertEqual(set(KERNEL_BASES), set(RELEASED) | {"2014.6"})

    def test_kernel_2014_6_maps_to_the_u1_base_which_fails_closed(self):
        # U1 = (b): the 2010-2014 (2014 Weeks 1-4) league base; built in B3.
        self.assertEqual(base_for_kernel("2014.6"), "2010_2014w4")
        self.assertIn("2010_2014w4", PENDING_BASES)
        self.assertNotIn("2010_2014w4", BASES)
        with self.assertRaisesRegex(CalibrationBaseError, "not available"):
            get_base("2010_2014w4")
        with self.assertRaises(CalibrationBaseError):
            base_of_kernel("2014.6")

    def test_unknown_versions_raise(self):
        for version in ("2014.7", "2013.3", "2015.1", None, "", "2014.5.1", "x", 2014.5):
            with self.subTest(version=version), self.assertRaises(CalibrationBaseError):
                base_for_kernel(version)
        with self.assertRaises(CalibrationBaseError):
            get_base("1999")

    def test_every_committed_receipt_has_a_base(self):
        receipts = committed_receipts()
        self.assertGreater(len(receipts), 300)
        self.assertEqual({base_for_kernel(r["kernel_version"]) for r in receipts}, {"2012"})


class Pin2012Tests(unittest.TestCase):
    def test_pins_match_the_committed_files(self):
        self.assertEqual(BASE_2012.verify(), [])
        self.assertTrue(BASE_2012.require())
        for role, pin in BASE_2012.files:
            data = (ROOT / pin.path).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), pin.sha256, role)
        self.assertEqual(set(BASE_2012.roles()), {"aggregate", "drive_model", "field_position", "usage", "injury",
                                                  "usage_tilt", "fg_distance"})
        # The modules' own 2012 paths are the pinned files.
        self.assertEqual(BASE_2012.path("aggregate"), calibration.DATA)
        self.assertEqual(BASE_2012.path("drive_model"), calibration.DRIVE_MODEL)
        self.assertEqual(BASE_2012.path("drive_model"), drive_model.DATA)
        self.assertEqual(BASE_2012.path("field_position"), fp.DATA)
        self.assertEqual(BASE_2012.path("usage"), usage.DATA)
        self.assertEqual(BASE_2012.path("injury"), injury_model.DATA)
        self.assertEqual(BASE_2012.path("usage_tilt"), usage.TILT_SOURCE)
        self.assertEqual(BASE_2012.path("fg_distance"), drive_model.FG_DISTANCE)

    def test_partition_counts_are_counted_not_read(self):
        counted = BASE_2012.partition_counts()
        self.assertEqual(counted, dict(BASE_2012.partitions))
        self.assertEqual(counted["field_position.drives"], fp.EXPECTED_DRIVES)
        data = fp.load()
        self.assertEqual(counted["field_position.kickoff_pool"], len(data["kickoff_pool"]))
        self.assertEqual(counted["drive_model.drives"], counted["drive_model.interior"] + counted["drive_model.half_final"])

    def test_a_changed_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = BASE_2012.at(tmp)
            for role, pin in BASE_2012.files:
                target = Path(tmp) / pin.path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / pin.path).read_bytes())
            self.assertEqual(base.verify(), [])
            path = Path(tmp) / BASE_2012.pin("usage").path
            path.write_bytes(path.read_bytes() + b" ")
            errors = base.verify()
            self.assertEqual(len(errors), 1)
            self.assertIn("differs from its pin", errors[0])
            # A base object verifies once, at first load; a new one reading
            # the changed file fails closed.
            with self.assertRaises(CalibrationBaseError):
                BASE_2012.at(tmp).raw("usage")
            with self.assertRaises(CalibrationBaseError):
                BASE_2012.at(tmp).require()
            path.unlink()
            with self.assertRaisesRegex(CalibrationBaseError, "unreadable"):
                BASE_2012.at(tmp).raw("usage")

    def test_a_wrong_partition_pin_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            pinned = tuple((k, v + 1 if k == "field_position.punt_pool" else v) for k, v in BASE_2012.partitions)
            base = synthetic_base(tmp, partitions=pinned)
            errors = base.verify()
            self.assertEqual(len(errors), 1)
            self.assertIn("field_position.punt_pool", errors[0])
            with self.assertRaises(CalibrationBaseError):
                base.require()
            a, b = sample_teams()
            with self.assertRaises(CalibrationBaseError):
                resolve_game(a, b, seed=SEED + b"-b1-pins", event_id="b1-pins",
                             _test_profile=Profile("2014.5", base=base, cell_rules="2013.7",
                                                   strength="honours-production-v3"))

    def test_an_invalid_baseline_raises_instead_of_asserting(self):
        # Formerly `assert not validate(cal)`, skipped under python -O.
        def bad(data):
            data["model"]["drive_outcomes"]["touchdown"] += 0.5
        with tempfile.TemporaryDirectory() as tmp:
            base = synthetic_base(tmp, mutate=bad, role="aggregate")
            self.assertEqual(base.verify(), [])
            a, b = sample_teams()
            with self.assertRaisesRegex(CalibrationBaseError, "aggregate baseline invalid"):
                resolve_game(a, b, seed=SEED + b"-b1-cal", event_id="b1-cal",
                             _test_profile=Profile("2014.5", base=base, cell_rules="2013.7",
                                                   strength="honours-production-v3"))

    def test_manifest_and_record(self):
        manifest = BASE_2012.manifest()
        self.assertEqual([row[0] for row in manifest], sorted(BASE_2012.roles()))
        text = "".join("%s %s %s\n" % row for row in manifest)
        self.assertEqual(BASE_2012.manifest_sha256(), hashlib.sha256(text.encode()).hexdigest())
        self.assertEqual(record(BASE_2012), {"name": "2012", "manifest_sha256": BASE_2012.manifest_sha256(),
                                             "cell_rules": "2013.7"})
        # The season-weight table: empty (equal weight per event) for the
        # 2012 base; a non-empty table is part of the base's identity.
        from dataclasses import replace
        self.assertEqual(BASE_2012.season_weights, ())
        weighted = replace(BASE_2012, season_weights=((2012, 2),))
        self.assertNotEqual(weighted.manifest_sha256(), BASE_2012.manifest_sha256())
        model = weighted.field_position()
        self.assertEqual(model.tuple_weight(fp.ZERO_TUPLE), 1)
        self.assertEqual(model.tuple_weight(fp.load()["pools"]["neutral"][0][0][0]), 1)  # no season field

    def test_fresh_copies_never_touch_the_shared_artifact(self):
        mine = calibration.load()
        mine["model"]["drive_outcomes"]["touchdown"] = 99
        self.assertNotEqual(BASE_2012.raw("aggregate")["model"]["drive_outcomes"]["touchdown"], 99)
        self.assertEqual(calibration.validate(), [])


class ReadinessPinTests(unittest.TestCase):
    def test_readiness_checks_the_live_base_pins(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        from check_game_readiness import calibration_base_blockers
        self.assertEqual(calibration_base_blockers(ROOT), [])
        with tempfile.TemporaryDirectory() as tmp:
            for role, pin in BASE_2012.files:
                target = Path(tmp) / pin.path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / pin.path).read_bytes())
            self.assertEqual(calibration_base_blockers(tmp), [])
            path = Path(tmp) / BASE_2012.pin("fg_distance").path
            path.write_bytes(path.read_bytes().replace(b"slope_per_yard", b"slope_per_yarD"))
            blockers = calibration_base_blockers(tmp)
            self.assertEqual([b["id"] for b in blockers], ["calibration_base"])
            self.assertIn("2014_strength_calibration_v3.json", blockers[0]["detail"])
        # The 2014.6 base is not built yet: readiness for it would block.
        self.assertEqual([b["id"] for b in calibration_base_blockers(ROOT, version="2014.6")], ["calibration_base"])


class TwoBasesTests(unittest.TestCase):
    """Two bases in one process, in both orders: each game reads only its
    own base, and no memoised helper (rungs, zone likelihoods, snap ranges,
    the injury parameters, the drive and field-position models) is shared."""

    GAMES = 3

    def play(self, base, label):
        profile = Profile("2014.5", base=base, cell_rules="2013.7", strength="honours-production-v3")
        a, b = sample_teams()
        out = []
        for i in range(self.GAMES):
            r = resolve_game(a, b, seed=SEED + b"-b1-two-%d" % i, event_id="b1-two-%d" % i, _test_profile=profile)
            self.assertEqual(validate_result(r, base=base), [], label)
            out.append(digest(r))
        return out

    def test_both_orders(self):
        with tempfile.TemporaryDirectory() as tmp_a, tempfile.TemporaryDirectory() as tmp_b:
            # Order one: the 2012 base first, then the synthetic base.
            first_2012 = BASE_2012.at(ROOT)
            first_syn = synthetic_base(tmp_a, mutate=reverse_kickoffs)
            r2012_a = self.play(first_2012, "2012 first")
            rsyn_a = self.play(first_syn, "synthetic second")
            # Order two, with fresh base objects (fresh memos).
            second_syn = synthetic_base(tmp_b, mutate=reverse_kickoffs)
            second_2012 = BASE_2012.at(ROOT)
            rsyn_b = self.play(second_syn, "synthetic first")
            r2012_b = self.play(second_2012, "2012 second")
            self.assertEqual(r2012_a, r2012_b)
            self.assertEqual(rsyn_a, rsyn_b)
            # The synthetic base's own data was used.
            self.assertNotEqual(r2012_a, rsyn_a)
            # The live singleton gives the 2012 results too.
            self.assertEqual(self.play(BASE_2012, "singleton"), r2012_a)
            for one, two in ((first_2012, first_syn), (first_syn, second_syn)):
                self.assertIsNot(one.field_position(), two.field_position())
                self.assertIsNot(one.drive_model(), two.drive_model())
                self.assertIsNot(one.injury_parameters(), two.injury_parameters())
                self.assertIsNot(one.field_position()._rungs_cache, two.field_position()._rungs_cache)
            self.assertEqual(first_2012.field_position().kickoff(random.Random(5)),
                             fp.kickoff(random.Random(5)))
            pool = fp.load()["kickoff_pool"]
            k = random.Random(5).randrange(len(pool))
            self.assertEqual(first_syn.field_position().kickoff(random.Random(5)),
                             fp._kick_record(random.Random(5), [pool[len(pool) - 1 - k]] * len(pool), 35))


class BoundBaseOnlyTests(unittest.TestCase):
    def test_a_game_reads_only_its_bound_base(self):
        # Every default path to the 2012 base raises while a game resolves
        # on another base: the kernel binds its base once and passes it to
        # every draw, label, credit and injury helper.
        from unittest import mock
        from runtime import calibration_base
        original = CalibrationBase.memo

        def guarded(self, key, factory):
            if self is BASE_2012:
                raise AssertionError("the 2012 base was read: %r" % (key,))
            return original(self, key, factory)

        def refuse(*args, **kwargs):
            raise AssertionError("a 2012 default was read")
        with tempfile.TemporaryDirectory() as tmp:
            base = synthetic_base(tmp, mutate=reverse_kickoffs)
            profile = Profile("2014.5", base=base, cell_rules="2013.7", strength="honours-production-v3")
            a, b = sample_teams()
            for game_type in ("regular", "postseason", "preseason"):
                with mock.patch.object(CalibrationBase, "memo", guarded), \
                        mock.patch.object(fp, "model", refuse), mock.patch.object(drive_model, "model", refuse), \
                        mock.patch.object(usage, "load", refuse), mock.patch.object(usage, "tilt_factors", refuse), \
                        mock.patch.object(injury_model, "parameters", refuse), \
                        mock.patch.object(injury_model, "load", refuse), \
                        mock.patch.object(calibration, "load", refuse), \
                        mock.patch.object(calibration, "load_drive_model", refuse):
                    r = resolve_game(a, b, seed=SEED + b"-b1-bound-" + game_type.encode(),
                                     event_id="b1-bound-" + game_type, game_type=game_type,
                                     game_date="2014-08-08" if game_type == "preseason" else None,
                                     _test_profile=profile)
                    self.assertTrue(r["terminated"])
                    self.assertEqual(validate_result(r, base=base), [], game_type)
            # The guard is live: the same game on the 2012 base trips it.
            with mock.patch.object(CalibrationBase, "memo", guarded), self.assertRaises(AssertionError):
                resolve_game(a, b, seed=SEED + b"-b1-bound-live", event_id="b1-bound-live",
                             _test_profile=PROFILE_2014_5)
            self.assertIs(calibration_base.get_base("2012"), BASE_2012)


class DispatchTests(unittest.TestCase):
    @staticmethod
    def receipt_2014_5():
        return next(r for r in committed_receipts() if r.get("kernel_version") == "2014.5" and r.get("play_ledger"))

    @classmethod
    def setUpClass(cls):
        cls.receipt = cls.receipt_2014_5()

    def test_receipts_are_audited_with_their_own_base(self):
        self.assertIs(base_for_result(self.receipt), BASE_2012)
        self.assertEqual(check_ledger(self.receipt), [])
        for version in ("2099.1", None, "2014.6"):
            doctored = dict(self.receipt, kernel_version=version)
            with self.subTest(version=version), self.assertRaises(CalibrationBaseError):
                check_ledger(doctored)

    def test_a_recorded_base_must_match(self):
        good = dict(self.receipt, calibration_base=record(BASE_2012))
        self.assertIs(base_for_result(good), BASE_2012)
        self.assertEqual(check_ledger(good), [])
        for bad in ({"name": "2012", "manifest_sha256": "0" * 64, "cell_rules": "2013.7"},
                    {"name": "2010_2014w4", "manifest_sha256": BASE_2012.manifest_sha256(), "cell_rules": "2013.7"},
                    {"name": "2012", "manifest_sha256": BASE_2012.manifest_sha256(), "cell_rules": "2014.6"},
                    "2012"):
            with self.subTest(bad=bad), self.assertRaises(CalibrationBaseError):
                check_ledger(dict(self.receipt, calibration_base=bad))

    def test_cell_rules_come_from_the_receipts_base(self):
        # The frozen 2013.7 rules (need, cell, decision zone, clock bucket)
        # are the base's own: a base whose decision zones are relabelled
        # grades the same receipt's fourth-down states differently, while
        # dispatch by the receipt's kernel version keeps the 2012 rules.
        def relabel_zones(data):
            zones = data["preregistration"]["decision_zones"]
            labels = list(zones)
            data["preregistration"]["decision_zones"] = {
                labels[(i + 1) % len(labels)]: zones[label] for i, label in enumerate(labels)}
        with tempfile.TemporaryDirectory() as tmp:
            other = synthetic_base(tmp, mutate=relabel_zones)
            self.assertEqual(other.verify(), [])
            self.assertEqual(check_ledger(self.receipt), [])
            self.assertEqual(check_ledger(self.receipt, base=BASE_2012), [])
            errors = check_ledger(self.receipt, base=other)
            self.assertTrue(errors)
            self.assertTrue(all(e.startswith("fourth_down_state_missing") for e in errors), errors[:3])

    def test_mixed_base_cohort_raises(self):
        later = dict(copy.deepcopy(self.receipt), kernel_version="2014.6", event_id="b1-later")
        mixed = [self.receipt, later]
        for audit in (bands.audit, bands.audit_drive_model, bands.audit_field_position, bands.coherence):
            with self.subTest(audit=audit.__name__), self.assertRaisesRegex(CalibrationBaseError, "mixed-base"):
                audit(mixed)
        # A cohort named explicitly must be its receipts' base.
        with self.assertRaises(CalibrationBaseError):
            bands.audit_drive_model([self.receipt], cohort="2014.6")
        self.assertIs(cohort_base([]), BASE_2012)
        self.assertIs(cohort_base([self.receipt], cohort="2014.5"), BASE_2012)
        self.assertIs(cohort_base([self.receipt, dict(self.receipt, kernel_version="2014.4")]), BASE_2012)


class CoherenceRegistryTests(unittest.TestCase):
    def test_every_class_has_a_group_predicate(self):
        from runtime import play_detail as pd
        self.assertEqual(len(pd.COHERENCE_REGISTRY), 42)
        self.assertEqual(pd.COHERENCE_CLASSES, tuple(c.name for c in pd.COHERENCE_REGISTRY))
        self.assertEqual(len(set(pd.COHERENCE_CLASSES)), 42)
        self.assertEqual(pd.LEGACY_CLASSES, pd.COHERENCE_CLASSES[:15])
        self.assertEqual(len(pd.SPOT_CLASSES), 17)
        for c in pd.COHERENCE_REGISTRY:
            self.assertTrue(callable(c.measurable), c.name)
            self.assertIsNone(c.listed_from, c.name)
        self.assertEqual(pd.classes_for_cohort("2013.6"), pd.COHERENCE_CLASSES)
        self.assertEqual(pd.classes_for_cohort("2014.6"), pd.COHERENCE_CLASSES)

    def test_a_2014_6_class_stays_out_of_closed_cohorts(self):
        # A class a later batch adds is gated by its kernel marker and
        # listed only from its cohort: it joins neither the 15 original nor
        # the spot classes, closed receipts never measure it, and closed
        # cohorts' tables do not list it.
        from unittest import mock
        from runtime import play_detail as pd
        marker = pd.from_kernel("2014.6")
        added = pd.CoherenceClass("b1_probe_class", "spot",
                                  lambda r: marker(r) and pd.has_spots(r), listed_from="2014.6")
        receipt = DispatchTests.receipt_2014_5()
        with mock.patch.object(pd, "COHERENCE_REGISTRY", pd.COHERENCE_REGISTRY + (added,)):
            self.assertNotIn("b1_probe_class", pd.LEGACY_CLASSES + pd.SPOT_CLASSES)
            self.assertNotIn("b1_probe_class", pd.measurable_classes(receipt))
            self.assertIn("b1_probe_class", pd.measurable_classes(dict(receipt, kernel_version="2014.6")))
            self.assertNotIn("b1_probe_class", pd.classes_for_cohort("2014.5"))
            self.assertNotIn("b1_probe_class", pd.classes_for_cohort(None))
            self.assertEqual(pd.classes_for_cohort("2014.6")[-1], "b1_probe_class")
            checked, rows = bands.coherence([receipt], cohort="2014.5")
            self.assertNotIn("b1_probe_class", [row[0] for row in rows])
        self.assertTrue(marker({"kernel_version": "2014.6"}))
        self.assertFalse(marker({"kernel_version": "2014.5"}))
        self.assertFalse(marker({}))


class FieldListTests(unittest.TestCase):
    def test_the_2012_lists_are_the_runtime_lists(self):
        lists = fp.field_lists(fp.load())
        self.assertEqual(lists["tuple_fields"], fp.TUPLE_FIELDS)
        model = BASE_2012.field_position()
        self.assertEqual(model.T, fp.T)
        self.assertEqual((model.KICK, model.PUNT, model.TURNOVER), (fp.KICK, fp.PUNT, fp.TURNOVER))

    def test_appended_fields_are_accepted_and_reordering_is_refused(self):
        data = copy.deepcopy(fp.load())
        data["tuple_fields"] = list(fp.TUPLE_FIELDS) + ["season"]
        data["kick_fields"] = list(data["kick_fields"]) + ["season"]
        lists = fp.field_lists(data)
        self.assertEqual(lists["tuple_fields"][-1], "season")
        self.assertEqual(lists["kick_fields"][:6], fp.RUNTIME_FIELDS["kick_fields"])
        for name in ("tuple_fields", "kick_fields", "punt_fields", "turnover_fields"):
            swapped = copy.deepcopy(fp.load())
            swapped[name] = list(reversed(swapped[name]))
            with self.subTest(name=name), self.assertRaises(ValueError):
                fp.field_lists(swapped)
            self.assertTrue(fp.validate(swapped))
            missing = copy.deepcopy(fp.load())
            del missing[name]
            self.assertTrue(fp.validate(missing))

    def test_kick_records_use_index_access(self):
        model = BASE_2012.field_position()
        record = model._kick_record(random.Random(3), [list(r) + ["appended"] for r in fp.load()["kickoff_pool"]], 35)
        self.assertEqual(record, fp.kickoff(random.Random(3)))

    def test_zero_tuple_lookups_are_guarded(self):
        model = BASE_2012.field_position()
        self.assertIsNone(model.value(fp.ZERO_TUPLE, "season"))
        self.assertEqual(model.value(fp.ZERO_TUPLE, "season", 7), 7)
        self.assertEqual(model.value(fp.ZERO_TUPLE, "plays"), 0)
        self.assertEqual(model.tuple_weight(fp.ZERO_TUPLE), 1)
        t = fp.load()["pools"]["neutral"][0][0][0]
        self.assertEqual(model.tuple_weight(t), 1)  # the 2012 base draws by events


if __name__ == "__main__":
    unittest.main()
