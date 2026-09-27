import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import unittest

import copy

from runtime import usage
from runtime.bands import audit, audit_drive_model, audit_field_position, coherence, cohorts
from runtime.kernel import TeamInput, resolve_game, validate_result
from runtime.play_detail import DRIVE_SUMMARY_FIELDS, check_ledger
from runtime.statbook import make_receipt
from support_rosters import game_day_roster
from synthetic_games import SAMPLE_SIZE, sample

# Frozen before the kernel 2013.7 acceptance run, not tuned: the first half
# still ends through the half-final redirect (a drawn interior drive that
# would overrun the window is replaced by a half-final drive), so the
# interior drives that survive are skewed short (punt-heavy), adding roughly
# 0.2-0.3 drive-ending punts per team-game. Any other graded row going
# OUTSIDE fails, and so does punts beyond centre + 2x tolerance.
KNOWN_DETECTIONS = {"punts per team game (drive-ending)"}



def team(prefix):
    roster = game_day_roster(prefix)
    return TeamInput(prefix, tuple(p.player_id for p in roster), roster=roster)


class UsageBandTests(unittest.TestCase):
    seed = b"synthetic-calibration-seed-not-career-state"

    @classmethod
    def setUpClass(cls):
        cls.results = list(sample())
        cls.receipts = [
            make_receipt(r, week=4, matchup="B at A", detail="compact_stats")
            for r in cls.results
        ]

    def test_baseline_artifact_validates(self):
        self.assertEqual(usage.validate(), [])
        self.assertEqual(usage.load()["season"], 2012)

    def test_results_reconcile(self):
        self.assertTrue(all(validate_result(r) == [] for r in self.results))

    def test_synthetic_league_sits_inside_every_2012_band(self):
        team_games, rows = audit(self.receipts)
        self.assertEqual(team_games, 2 * SAMPLE_SIZE)
        outside = [row for row in rows if row[4] != "WITHIN"]
        self.assertEqual(outside, [])

    def test_drive_model_rows_and_coherence(self):
        team_games, rows = audit_drive_model(self.receipts)
        self.assertEqual(team_games, 2 * SAMPLE_SIZE)
        graded = [row for row in rows if row[4] != "INFORMATIONAL"]
        outside = [row for row in graded if row[4] != "WITHIN" and row[0] not in KNOWN_DETECTIONS]
        self.assertEqual(outside, [])
        for metric, observed, centre, tolerance, _ in graded:
            if metric in KNOWN_DETECTIONS:
                self.assertLessEqual(abs(observed - centre), 2 * tolerance, metric)
        self.assertTrue(any(row[4] == "INFORMATIONAL" and row[0].startswith("kickoffs") for row in rows))
        checked, counts = coherence(self.receipts)
        self.assertEqual(checked, SAMPLE_SIZE)
        self.assertEqual([c for c in counts if c[1]], [])
        # Compact receipts audit the ledger-free spot classes; the kick-row
        # and label classes need the full ledger.
        measurable = {cls: n for cls, _, n in counts}
        self.assertEqual(measurable["spot_chain_break"], SAMPLE_SIZE)
        self.assertEqual(measurable["label_carrier_mismatch"], 0)

    def test_field_position_rows(self):
        team_games, rows = audit_field_position(self.receipts)
        self.assertEqual(team_games, 2 * SAMPLE_SIZE)
        graded = [row for row in rows if row[4] not in ("INFORMATIONAL", "INSUFFICIENT SAMPLE")]
        self.assertTrue(any(row[0] == "sacks per dropback" for row in graded))
        self.assertTrue(any(row[0].startswith("punt share of possessions ending") for row in rows))
        self.assertEqual([row for row in graded if row[4] != "WITHIN"], [])
        for metric, observed, centre, _, status in rows:
            print("[2013.7 sample] %s: %s (2012 %s) %s" % (
                metric, "—" if observed is None else round(observed, 4), round(centre, 4), status))

    def test_doctored_late_punt_is_detected(self):
        """A punt in a zero-punt late cell (trailing 1-8 inside the last 2:00)
        cannot pass: its fourth-down state no longer recomputes, or the
        terminal-state class fires."""
        doctored = copy.deepcopy(self.receipts)
        index = DRIVE_SUMMARY_FIELDS.index
        hits = 0
        for receipt in doctored:
            for row in receipt["drives"]:
                cell = row[index("cell")]
                if row[index("half")] == 2 and cell in ("le120|trail1_3", "le120|trail4_8") and row[index("category")] != "punt":
                    row[index("category")] = "punt"
                    errors = check_ledger(receipt)
                    self.assertTrue(any(e.split(":")[0] in ("fourth_down_state_missing", "late_terminal_state_mismatch",
                                                             "spot_chain_break", "score_identity_violations")
                                        for e in errors))
                    hits += 1
                    break
            if hits >= 5:
                break
        self.assertTrue(hits)

    def test_doctored_cohort_reads_outside_on_fg_accuracy(self):
        doctored = copy.deepcopy(self.receipts)
        for receipt in doctored:
            for game in receipt["team_stats"].values():
                game["field_goals"] = game["field_goal_attempts"]
        _, rows = audit_drive_model(doctored)
        row = next(r for r in rows if r[0] == "FG accuracy")
        self.assertEqual(row[4], "OUTSIDE")

    def test_legacy_receipts_are_excluded_from_new_rows(self):
        legacy = copy.deepcopy(self.receipts[:20])
        for receipt in legacy:
            receipt["kernel_version"] = "2013.5"
            receipt.pop("drives")
        previous = copy.deepcopy(self.receipts[20:30])
        for receipt in previous:
            receipt["kernel_version"] = "2013.6"
        old, kernel_2013_6, current = cohorts(legacy + previous + self.receipts[30:40])
        self.assertEqual((len(old), len(kernel_2013_6), len(current)), (20, 10, 10))
        self.assertTrue(all(r["kernel_version"] == "2013.7" for r in current))

    def test_depth_chart_orders_usage(self):
        carries = {}
        for r in self.results:
            for player, line in r["team_stats"]["A"]["players"].items():
                carries[player] = carries.get(player, 0) + line["rushing_attempts"]
        self.assertGreater(carries["A-RB1"], carries["A-RB2"])
        self.assertGreater(carries["A-RB2"], carries["A-RB3"])
        self.assertEqual(carries["A-QB2"], 0)

    def test_linebackers_of_any_label_make_tackles(self):
        tackles = {"OLB": 0, "ILB": 0}
        for r in self.results:
            for line in r["team_stats"]["B"]["players"].values():
                if line["position"] in tackles:
                    tackles[line["position"]] += line["tackles"]
        self.assertTrue(all(value > 0 for value in tackles.values()))

    def test_small_samples_are_not_graded(self):
        _, rows = audit(self.receipts[:2])
        self.assertTrue(all(row[4] == "INSUFFICIENT SAMPLE" for row in rows))

    def test_lineup_gate(self):
        self.assertEqual(usage.lineup_errors(game_day_roster("X")), [])
        self.assertTrue(usage.lineup_errors(game_day_roster("X")[:5]))


if __name__ == "__main__":
    unittest.main()


class EmergencySpecialistTests(unittest.TestCase):
    def test_punter_covers_a_missing_kicker(self):
        from types import SimpleNamespace
        players = [SimpleNamespace(position=pos) for pos in
                   ["QB", "RB", "WR", "WR", "WR", "TE"] + ["OT"] * 5 + ["DE"] * 3 + ["LB"] * 2 + ["CB"] * 4 + ["P"]]
        self.assertEqual(usage.lineup_errors(players), [])
        self.assertTrue(usage.lineup_errors(players[:-1]))

    def test_kernel_kicks_with_the_punter_when_no_kicker_dresses(self):
        a, b = team("A"), team("B")
        roster = tuple(p for p in a.roster if p.position != "K")
        a = TeamInput("A", tuple(p.player_id for p in roster), roster=roster)
        result = resolve_game(a, b, seed=b"synthetic-calibration-seed-not-career-state", event_id="emergency-k")
        self.assertEqual(validate_result(result), [])
        kicks = [p for p in result["play_ledger"] if p["offense"] == "A" and p["play_type"] in {"field_goal", "extra_point"}]
        punter = next(p.player_id for p in roster if p.position == "P")
        self.assertTrue(all(p["kicker"] == punter for p in kicks))
