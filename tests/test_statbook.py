import unittest

from runtime.statbook import aggregate_receipts, leaders, make_receipt


class StatbookTests(unittest.TestCase):
    def result(self, event_id="g1"):
        empty = {
            "position": "QB", "pass_attempts": 0, "passing_yards": 0,
            "rushing_attempts": 0, "rushing_yards": 0, "receptions": 0,
            "receiving_yards": 0, "sacks_allowed": 0, "sacks": 0,
            "pressures": 0, "interceptions": 0, "fumbles": 0,
            "field_goals_made": 0, "punts": 0, "return_yards": 0,
            "tackles": 0,
        }
        a = dict(empty)
        a.update(pass_attempts=30, passing_yards=250, interceptions=1, targets=7)
        b = dict(empty)
        b.update(position="RB", rushing_attempts=20, rushing_yards=100)
        bench = dict(empty)
        bench.update(position="WR")
        base = {
            "points": 20, "touchdowns": 2, "field_goals": 2, "punts": 4,
            "turnovers": 1, "sacks_allowed": 2, "penalties": 6,
            "penalty_yards": 45, "passing_yards": 250, "rushing_yards": 100,
            "first_downs": 20, "third_down_attempts": 12,
            "third_down_conversions": 5, "time_of_possession": 1800,
            "kick_returns": 2, "punt_returns": 1,
        }
        return {
            "terminated": True,
            "kernel_version": "test",
            "event_id": event_id,
            "final_score": {"A": 20, "B": 17},
            "team_stats": {
                "A": {**base, "players": {"qb-a": a, "rb-a": b, "bench-a": bench}},
                "B": {**base, "points": 17, "players": {"qb-b": a, "rb-b": b, "bench-b": bench}},
            },
            "play_ledger": [
                {"sequence":1,"offense":"A","play_type":"pass","concept":"Mesh"},
                {"sequence":2,"offense":"B","play_type":"run","concept":"Power"},
            ],
            "play_call_stats": {
                "A":{"Mesh":{"family":"Mesh","snaps":1,"dropbacks":1,"pass_attempts":1,"completions":1,"yards":12,"runs":0,"touchdowns":0,"turnovers":0,"sacks":0}},
                "B":{"Power":{"family":"Power","snaps":1,"runs":1,"dropbacks":0,"pass_attempts":0,"completions":0,"yards":5,"touchdowns":0,"turnovers":0,"sacks":0}},
            },
        }

    def test_receipt_and_aggregation(self):
        r1 = make_receipt(self.result("g1"), week=1, matchup="B at A")
        r2 = make_receipt(self.result("g2"), week=2, matchup="A at B")
        book = aggregate_receipts([r1, r2])
        self.assertEqual(book["through_week"], 2)
        self.assertEqual(book["teams"]["A"]["games"], 2)
        self.assertEqual(book["teams"]["A"]["team_stats"]["passing_yards"], 500)
        self.assertEqual(book["teams"]["A"]["players"]["qb-a"]["pass_attempts"], 60)
        self.assertEqual(book["plays_recorded"], 4)
        self.assertEqual(book["play_calls"]["A"]["Mesh"]["snaps"], 2)
        self.assertEqual(book["play_calls"]["A"]["Mesh"]["yards"], 24)
        self.assertIn("bench-a", book["teams"]["A"]["players"])
        self.assertIn("bench-a", book["players"])
        self.assertEqual(book["players"]["bench-a"]["receiving_yards"], 0)
        self.assertIn("targets", book["player_stat_fields"])
        self.assertEqual(book["players"]["qb-a"]["targets"], 14)
        self.assertEqual(leaders(book, "targets")[0]["value"], 14)
        self.assertEqual(leaders(book, "passing_yards")[0]["value"], 500)
        self.assertTrue(book["coverage_complete"])

    def test_partial_coverage_propagates(self):
        receipt = make_receipt(
            self.result("legacy"), week=1, matchup="B at A",
            coverage="legacy_partial",
        )
        self.assertFalse(aggregate_receipts([receipt])["coverage_complete"])

    def test_duplicate_receipts_fail_closed(self):
        receipt = make_receipt(self.result("same"), week=1, matchup="B at A")
        with self.assertRaises(ValueError):
            aggregate_receipts([receipt, receipt])


if __name__ == "__main__":
    unittest.main()
