"""Kernel 2014.6 build, batch B5X: provisional detections carried to B17.

Batch B5 read seven graded 2014.6 rows OUTSIDE and stopped on U8; the build
carries each as a PROVISIONAL detection (runtime.bands.PROVISIONAL_DETECTIONS)
with its attribution and the batch expected to resolve it. These tests pin the
contract: the registry of every released cohort is unchanged, the 2014.6
permanent registry is still exactly the carried 2014.5 one, every provisional
row names its attribution and resolving batch, audits label the rows and do not
bound them, and the B17 view (provisional=False) grades them as unregistered.
No centre, tolerance, pool or result is touched here.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import unittest

from runtime import KERNEL_VERSION, bands
from runtime.bands import (KNOWN_DETECTION_BOUND, KNOWN_DETECTIONS, PROVISIONAL_DETECTIONS,
                           PROVISIONAL_REGRADE_BATCH, known_detections, known_status, provisional_detections)
from runtime.calibration_base import BASE_2010_2014W4

EXPECTED = {
    "first-half final possessions starting with 0-30 s left (share)",
    "first-half final possessions starting with 31-60 s left (share)",
    "timeouts per team-game",
    "drive share: touchdown",
    "drive share: punt",
    "drive share: safety",
    "top receiver share of team targets (team-game)",
    "punt share of possessions ending in Q4's last 2:00 or OT, offense trailing 1-8",
    "sacks per dropback",
    "third-down attempts per punt drive",
}


class ProvisionalRegistryTests(unittest.TestCase):
    def test_only_the_2014_6_cohort_has_provisional_rows(self):
        self.assertEqual(set(PROVISIONAL_DETECTIONS), {"2014.6"})
        self.assertEqual(set(provisional_detections("2014.6")), EXPECTED)
        for cohort in ("2013.6", "2013.7", "2014.1", "2014.2", "2014.5", KERNEL_VERSION, "legacy"):
            self.assertEqual(provisional_detections(cohort), {})

    def test_released_registries_are_unchanged(self):
        self.assertEqual(set(known_detections("2014.5")), {
            "punts per team game (drive-ending)", "FGM per team game", "drive share: clock",
            "clock-expired drives per team game", "FGA per team game",
            "punt share of possessions ending in Q4's last 5:00 or OT, offense trailing 1-8"})
        for note in known_detections("2014.5").values():
            self.assertNotIn("PROVISIONAL", note)
        self.assertEqual(known_detections("2014.5", provisional=False), known_detections("2014.5"))

    def test_2014_6_permanent_registry_is_the_carried_2014_5_registry(self):
        self.assertEqual(known_detections("2014.6", provisional=False), known_detections("2014.5"))
        self.assertEqual(set(known_detections("2014.6")) - set(known_detections("2014.5")), EXPECTED)
        self.assertFalse(EXPECTED & set(known_detections("2014.5")))

    def test_every_provisional_row_carries_attribution_and_resolving_batch(self):
        for metric, entry in provisional_detections("2014.6").items():
            self.assertEqual(set(entry), {"observed", "attribution", "resolves"}, metric)
            for key in entry:
                self.assertTrue(entry[key].strip(), (metric, key))
            note = KNOWN_DETECTIONS["2014.6"][metric]
            self.assertTrue(note.startswith("PROVISIONAL"), metric)
            self.assertIn(PROVISIONAL_REGRADE_BATCH, note)
            self.assertIn("never auto-registered permanently", note)
            self.assertIn(entry["attribution"], note)
            self.assertIn(entry["resolves"], note)
        resolves = {m: e["resolves"] for m, e in provisional_detections("2014.6").items()}
        for metric in ("drive share: touchdown", "drive share: punt", "drive share: safety", "sacks per dropback"):
            self.assertTrue(resolves[metric].startswith("B7"), metric)
        self.assertTrue(resolves["top receiver share of team targets (team-game)"].startswith("B13/B16"))
        for metric in ("punt share of possessions ending in Q4's last 2:00 or OT, offense trailing 1-8",
                       "third-down attempts per punt drive"):
            self.assertIn("re-grade at B17", resolves[metric])
        for metric in ("first-half final possessions starting with 0-30 s left (share)",
                       "first-half final possessions starting with 31-60 s left (share)",
                       "timeouts per team-game"):
            self.assertIn("residual", resolves[metric])

    def test_provisional_metric_strings_are_2014_6_rows_with_artifact_centres(self):
        centres = BASE_2010_2014W4.field_position().load()["band_centres"]
        for key in ("h1_final_start_window:0-30", "h1_final_start_window:31-60", "timeouts_per_team_game",
                    "late_punt_share_le120_trail1_8", "sacks_per_dropback", "third_down_attempts_per_punt_drive"):
            self.assertIn(key, centres)
        self.assertIn("top_receiver_target_share", bands.expected(BASE_2010_2014W4))
        for label in ("touchdown", "punt", "safety"):
            self.assertIn("drive_share:%s" % label, centres)

    def test_status_labels_and_does_not_bound_a_provisional_row(self):
        far = ("timeouts per team-game", 3.0, 3.70, 0.08, "OUTSIDE")
        self.assertEqual(known_status(far, "2014.6"),
                         "OUTSIDE (provisional detection, re-graded at %s)" % PROVISIONAL_REGRADE_BATCH)
        self.assertNotIn("beyond", known_status(far, "2014.6"))
        within = ("timeouts per team-game", 3.69, 3.70, 0.08, "WITHIN")
        self.assertEqual(known_status(within, "2014.6"),
                         "WITHIN (provisional detection, re-graded at %s)" % PROVISIONAL_REGRADE_BATCH)
        self.assertEqual(known_status(far, "2014.5"), "OUTSIDE")
        self.assertEqual(known_status(("timeouts per team-game", 3.0, 3.70, 0.08, "INSUFFICIENT SAMPLE"),
                                      "2014.6"), "INSUFFICIENT SAMPLE")

    def test_b17_view_grades_provisional_rows_as_unregistered(self):
        far = ("timeouts per team-game", 3.0, 3.70, 0.08, "OUTSIDE")
        self.assertEqual(known_status(far, "2014.6", provisional=False), "OUTSIDE")
        within = ("timeouts per team-game", 3.69, 3.70, 0.08, "WITHIN")
        self.assertEqual(known_status(within, "2014.6", provisional=False), "WITHIN")
        # A carried 2014.5 detection keeps its bounded status in both views.
        carried = ("punts per team game (drive-ending)", 4.66, 4.82, 0.15, "OUTSIDE")
        for view in (True, False):
            self.assertEqual(known_status(carried, "2014.6", provisional=view),
                             "OUTSIDE (known detection, within %dx tolerance)" % KNOWN_DETECTION_BOUND)

    def test_renderer_block_names_the_provisional_rule(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
        from render_season_stats import _known_detection_lines
        lines = _known_detection_lines("2014.6")
        self.assertIn("PROVISIONAL", lines[0])
        self.assertIn("B17", lines[0])
        self.assertEqual(sum(1 for line in lines if "PROVISIONAL (batch B5X" in line), len(EXPECTED))
        self.assertNotIn("PROVISIONAL", "".join(_known_detection_lines("2014.5")))

    def test_acceptance_harness_separates_provisional_rows(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))
        import acceptance_2014_6 as acc
        rows = [{"label": "x", "refused": None, "digest": "d",
                 "receipt": {"kernel_version": "2014.6", "team_stats": {}}}]
        out = acc.summary(rows, "2014.6")
        self.assertIn("outside_provisional", out)
        self.assertIn("outside_ungated", out)
        self.assertFalse(out["provisional_regrade"])
        self.assertTrue(acc.summary(rows, "2014.6", provisional=False)["provisional_regrade"])


if __name__ == "__main__":
    unittest.main()
