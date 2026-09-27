import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

from runtime import drive_model
from runtime.calibration import load, load_drive_model, validate

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / ".sim_cache" / "sources"
BUILDER = ROOT / "scripts" / "research" / "build_2012_drive_model.py"


class DriveModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = load_drive_model()
        cls.baseline = load()

    def tuples(self):
        pools = self.model["pools"]
        for category, rows in pools["interior"].items():
            for row in rows:
                yield category, row
        for bucket in pools["half_final"].values():
            for category, rows in bucket.items():
                for row in rows:
                    yield category, row

    def test_drive_totals_reconcile(self):
        interior = sum(self.model["interior_counts"].values())
        half_final = sum(sum(v.values()) for v in self.model["half_final_counts"].values())
        self.assertEqual(interior + half_final, 5984)
        totals = self.baseline["period_totals"]
        counts = self.model["category_counts"]
        self.assertEqual(counts["field_goal_attempt"], totals["field_goal_attempts"])
        fg = [row for c, row in self.tuples() if c == "field_goal_attempt"]
        self.assertEqual(len(fg), 1016)
        self.assertEqual(sum(row[4] for row in fg), totals["field_goals_made"])
        self.assertEqual(counts["interception"], totals["interceptions"])
        self.assertEqual(self.model["rates"]["extra_point"], [1229, 1237])

    def test_plays_and_net_yards_reproduce_the_baseline(self):
        rows = [row for _, row in self.tuples()]
        self.assertLessEqual(abs(sum(r[0] for r in rows) / 512 - 64.2), 0.1)
        self.assertLessEqual(abs(sum(r[1] for r in rows) / 512 - 347.2), 1.0)

    def test_every_tuple_inside_its_category_range(self):
        for category, row in self.tuples():
            low, high = self.model["net_range"][category]
            self.assertTrue(low <= row[1] <= high)

    def test_bucket_edges_are_preregistered(self):
        self.assertEqual(self.model["bucket_edges"],
                         [[0, 30], [31, 60], [61, 120], [121, 240], [241, 1800]])
        self.assertEqual(drive_model.PREREGISTERED_BUCKET_EDGES, self.model["bucket_edges"])

    def test_calibration_validates_and_detects_tampering(self):
        self.assertEqual(validate(), [])
        self.assertEqual(drive_model.validate(), [])
        altered = copy.deepcopy(self.model)
        altered["rates"]["field_goal"][0] += 1
        self.assertTrue(validate(drive=altered))
        altered = copy.deepcopy(self.model)
        altered["interior_counts"]["punt"] += 1
        self.assertTrue(validate(drive=altered))

    def test_artifact_reproducible(self):
        missing = [name for name in ("play_by_play_2012.csv.gz", "reg_pbp_2012.csv")
                   if not (SOURCES / name).exists()]
        if missing:
            self.skipTest("2012 play-by-play sources absent (%s); byte-for-byte rebuild not checked"
                          % ", ".join(missing))
        done = subprocess.run([sys.executable, str(BUILDER), "--check"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)


if __name__ == "__main__":
    unittest.main()
