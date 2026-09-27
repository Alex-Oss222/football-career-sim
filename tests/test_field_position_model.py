import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

from runtime import field_position
from runtime.calibration import load_drive_model

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / ".sim_cache" / "sources"
BUILDER = ROOT / "scripts" / "research" / "build_2012_field_position_model.py"


class FieldPositionModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = json.loads(field_position.DATA.read_text())

    def test_artifact_validates_and_reconciles(self):
        self.assertEqual(field_position.validate(), [])
        m = self.model
        self.assertEqual(m["reconciliation"]["partition"],
                         {"neutral": 4632, "h1_final": 256, "late": 1035, "ot": 61})
        self.assertEqual([sum(row) for row in m["neutral_counts"]],
                         [436, 757, 1176, 921, 572, 316, 165, 102, 89, 98])
        counts = {c: 0 for c in m["categories"]}
        for row in m["neutral_counts"]:
            for c, n in zip(m["categories"], row):
                counts[c] += n
        for group in ("h1_final_counts", "late_counts"):
            for cells in m[group].values():
                for c, n in cells.items():
                    counts[c] += n
        for c, n in m["ot_counts"].items():
            counts[c] += n
        self.assertEqual(counts, load_drive_model()["category_counts"])
        self.assertEqual(m["reconciliation"]["chains"]["observed"], [9241, 919, 6814, 2600])
        self.assertEqual([len(m[k]) for k in ("kickoff_pool", "free_kick_pool", "punt_pool",
                                               "interception_pool", "fumble_pool")],
                         [2444, 13, 2405, 386, 251])
        self.assertEqual(sum(r[0] for r in m["kickoff_pool"]), 1128)
        self.assertEqual(m["band_centres"]["sacks_per_dropback"], [1169, 18957])
        self.assertEqual(m["rates"]["scramble"], [681, 1223])

    def test_cell_map_matches_preregistration(self):
        m = self.model
        self.assertEqual(m["cell_map"]["301-600|trail1_3"], "301-600+121-300|trail1_3")
        self.assertEqual(m["cell_map"]["le120|trail1_3"], "le120|trail1_3")
        self.assertEqual({m["cell_map"]["%s|tied" % t] for t in ("301-600", "121-300", "le120")},
                         {"301-600+121-300+le120|tied"})
        sizes = {cell: sum(v.values()) for cell, v in m["late_counts"].items()}
        self.assertEqual(sizes["301-600+121-300|trail1_3"], 49)
        self.assertEqual(sizes["le120|trail1_3"], 30)
        self.assertEqual(sizes["301-600+121-300+le120|tied"], 54)
        self.assertTrue(all(n >= 30 for n in sizes.values()))
        self.assertEqual({k: sum(v.values()) for k, v in m["h1_final_counts"].items()},
                         {"0-30": 113, "31-60": 77, "61-120": 66})
        self.assertEqual(sum(m["ot_counts"].values()), 61)

    def test_fg_offsets_and_touchdown_identity(self):
        T = field_position.T
        for t in field_position._all_tuples(self.model, "field_goal_attempt"):
            self.assertIn(t[T["fg_distance"]] - t[T["end"]], (17, 18, 19))
        for t in field_position._all_tuples(self.model, "touchdown"):
            self.assertEqual(t[T["net0"]], t[T["start"]])
        for record in self.model["punt_pool"]:
            if not record[6]:
                self.assertEqual(record[5], 100 - record[0] + record[2] - record[3] + record[4])

    def test_tampering_is_detected(self):
        for mutate in (
            lambda m: m["neutral_counts"][0].__setitem__(0, m["neutral_counts"][0][0] + 1),
            lambda m: m["cell_map"].__setitem__("le120|trail1_3", "le120|trail4_8x"),
            lambda m: next(r for r in m["punt_pool"] if not r[6]).__setitem__(5, 1),
            lambda m: m["preregistration"].__setitem__("k_transition", 25),
            lambda m: m["reconciliation"].__setitem__("result", "fail"),
        ):
            altered = copy.deepcopy(self.model)
            mutate(altered)
            self.assertTrue(field_position.validate(altered))

    def test_artifact_reproducible(self):
        missing = [name for name in ("play_by_play_2012.csv.gz", "reg_pbp_2012.csv", "roster_2012.csv")
                   if not (SOURCES / name).exists()]
        if missing:
            self.skipTest("2012 sources absent (%s); byte-for-byte rebuild not checked" % ", ".join(missing))
        done = subprocess.run([sys.executable, str(BUILDER), "--check"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)


if __name__ == "__main__":
    unittest.main()
