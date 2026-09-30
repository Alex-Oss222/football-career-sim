"""The 2010-2012 production evidence builder and its committed output
(scripts/research/build_2010_2012_production_evidence.py,
library/data/2010_2012_production_evidence.json).

Unit checks on the tiering and shrinkage rules use small synthetic inputs;
file checks read the committed JSON only (no network, no source files).
"""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/research/build_2010_2012_production_evidence.py"
DATA = ROOT / "library/data/2010_2012_production_evidence.json"

spec = importlib.util.spec_from_file_location("build_production", SCRIPT)
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class TierRuleTests(unittest.TestCase):
    def test_fixed_cut_points(self):
        # share_above: < .10 Elite, < .30 Plus, < .70 Average, < .90 Below-Average, else Replacement-Level.
        for share, tier in ((0.0, "Elite"), (0.099, "Elite"), (0.10, "Plus"), (0.299, "Plus"), (0.30, "Average"),
                            (0.699, "Average"), (0.70, "Below-Average"), (0.899, "Below-Average"),
                            (0.90, "Replacement-Level"), (1.0, "Replacement-Level")):
            self.assertEqual(build.tier_of(share), tier, share)

    def test_declared_rule_matches_the_function(self):
        tiers = build.PREREGISTERED["tiers"]
        self.assertEqual(tiers["Elite"], "share_above < 0.10")
        self.assertEqual(tiers["Replacement-Level"], "share_above >= 0.90")
        self.assertIn("not_a_bespoke_number", tiers)

    def test_metric_definitions(self):
        fg = {"0_19": [0, 0], "20_29": [4, 4], "30_39": [3, 4], "40_49": [2, 4], "50_59": [1, 2], "60_": [0, 0]}
        rates = {"0_19": 1.0, "20_29": 0.95, "30_39": 0.85, "40_49": 0.70, "50_59": 0.55, "60_": 0.2}
        row = {"group": "K", "fg_att": 14, "fg_made": 10, "fg_by_band": fg}
        value, n = build.raw_metric(row, rates)
        expected = 4 * 0.95 + 4 * 0.85 + 4 * 0.70 + 2 * 0.55
        self.assertEqual(n, 14)
        self.assertAlmostEqual(value, (10 - expected) / 14)
        row = {"group": "QB", "passing_epa": 30.0, "dropbacks": 300}
        self.assertEqual(build.raw_metric(row, rates), (0.1, 300))
        row = {"group": "WR", "rushing_epa": 2.0, "receiving_epa": 18.0, "opportunities": 80}
        self.assertEqual(build.raw_metric(row, rates), (0.25, 80))
        row = {"group": "DB", "games": 16, "sacks": 1.0, "qb_hits": 2, "tfl": 3, "interceptions": 4, "passes_defended": 10}
        self.assertEqual(build.raw_metric(row, rates), ((1 + 1 + 3 + 4 + 5) / 16, 16))
        row = {"group": "P", "punts": 50, "net_yards": 2000}
        self.assertEqual(build.raw_metric(row, rates), (40.0, 50))
        self.assertEqual(build.raw_metric({"group": "OL"}, rates), (None, None))

    def test_two_point_tries_and_tfl_source_are_declared_amendments(self):
        amendments = build.PREREGISTERED["amendments"]
        self.assertEqual(len(amendments), 2)
        self.assertIn("two-point", amendments[1]["what"])
        self.assertIn("tackle_for_loss", amendments[0]["what"])


class CommittedFileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding="utf-8"))

    def test_public_dates_precede_the_divergence(self):
        for season, block in self.data["seasons"].items():
            self.assertLess(block["public_date"], self.data["divergence"], season)
            self.assertTrue(block["admissible_pre_divergence"])
        self.assertEqual(self.data["seasons"]["2012"]["public_date"], "2012-12-30")
        self.assertEqual(self.data["seasons"]["2011"]["public_date"], "2012-01-01")
        self.assertEqual(self.data["seasons"]["2010"]["public_date"], "2011-01-02")
        self.assertEqual(sorted(self.data["seasons"]), ["2010", "2011", "2012"])

    def test_every_tiered_row_is_a_qualifier_with_a_verification_label(self):
        minimums = {g: m["minimum"] for g, m in self.data["preregistered"]["metrics"].items()}
        labels = {"Confirmed two-pass", "Corrected", "Unverified", "Job evidence"}
        for pid, p in self.data["players"].items():
            for season, s in p["seasons"].items():
                self.assertIn(s["verification"], labels, (pid, season))
                if s["group"] == "OL":
                    self.assertIsNone(s["tier"])
                    self.assertEqual(s["verification"], "Job evidence")
                    continue
                self.assertGreaterEqual(s["n"], minimums[s["group"]], (pid, season))
                self.assertIn(s["tier"], ("Elite", "Plus", "Average", "Below-Average", "Replacement-Level"))
                self.assertIn("shrunk", s)
        summary = self.data["summary"]
        self.assertEqual(summary["verification"]["Unverified"], 0)
        self.assertGreater(summary["verification"]["Confirmed two-pass"], 2000)

    def test_tier_shares_follow_the_cut_points(self):
        for season, block in self.data["seasons"].items():
            for grp, counts in block["counts"].items():
                n = sum(counts.get(t, 0) for t in ("Elite", "Plus", "Average", "Below-Average", "Replacement-Level"))
                self.assertAlmostEqual(counts["Elite"] / n, 0.10, delta=0.05 + 1 / n, msg=(season, grp))  # tied shrunk values share one rank
                self.assertAlmostEqual(counts["Average"] / n, 0.40, delta=0.05 + 1 / n, msg=(season, grp))  # tied shrunk values share one rank
                self.assertAlmostEqual(counts["Replacement-Level"] / n, 0.10, delta=0.05 + 1 / n, msg=(season, grp))  # tied shrunk values share one rank

    def test_shrinkage_moves_toward_the_league_mean(self):
        for season, block in self.data["seasons"].items():
            means = block["league_means"]
            for pid, p in self.data["players"].items():
                s = p["seasons"].get(season)
                if not s or s["group"] == "OL":
                    continue
                mean = means[s["group"]]["mean"]
                self.assertTrue(min(s["raw"], mean) - 1e-9 <= s["shrunk"] <= max(s["raw"], mean) + 1e-9, (pid, season))

    def test_no_post_divergence_season(self):
        self.assertTrue(all(int(y) <= 2012 for p in self.data["players"].values() for y in p["seasons"]))
        self.assertNotIn("2013", json.dumps(self.data["sources"]))


if __name__ == "__main__":
    unittest.main()
