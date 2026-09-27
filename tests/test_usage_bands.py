import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import unittest

from runtime import usage
from runtime.bands import audit
from runtime.kernel import TeamInput, resolve_game, validate_result
from runtime.statbook import make_receipt
from support_rosters import game_day_roster


def team(prefix):
    roster = game_day_roster(prefix)
    return TeamInput(prefix, tuple(p.player_id for p in roster), roster=roster)


class UsageBandTests(unittest.TestCase):
    seed = b"synthetic-calibration-seed-not-career-state"

    @classmethod
    def setUpClass(cls):
        a, b = team("A"), team("B")
        cls.results = [
            resolve_game(a, b, seed=cls.seed, event_id=f"band-{i}") for i in range(160)
        ]
        cls.receipts = [
            make_receipt(r, week=1, matchup="B at A", detail="compact_stats")
            for r in cls.results
        ]

    def test_baseline_artifact_validates(self):
        self.assertEqual(usage.validate(), [])
        self.assertEqual(usage.load()["season"], 2012)

    def test_results_reconcile(self):
        self.assertTrue(all(validate_result(r) == [] for r in self.results))

    def test_synthetic_league_sits_inside_every_2012_band(self):
        team_games, rows = audit(self.receipts)
        self.assertEqual(team_games, 320)
        outside = [row for row in rows if row[4] != "WITHIN"]
        self.assertEqual(outside, [])

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
