"""Kernel 2014.3 Pro Bowl game type and the 2014 Pro Bowl draft."""
import unittest

from runtime.kernel import PRO_BOWL_SPOT, resolve_game, validate_result
from synthetic_games import sample_teams

SEED = b"pro-bowl-test-seed-not-career-state-000000"


class ProBowlGameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        a, b = sample_teams()
        cls.games = [resolve_game(a, b, seed=SEED + b"-%04d" % i, event_id="pb-%d" % i,
                                  venue="neutral", game_type="pro_bowl") for i in range(80)]

    def test_games_validate(self):
        for game in self.games:
            self.assertEqual(validate_result(game), [])

    def test_no_kickoffs_and_quarter_rules(self):
        for game in self.games:
            self.assertEqual(game["kickoffs"], [])
            self.assertFalse(any(r.get("play_type") in ("kickoff", "free_kick") for r in game["play_ledger"]))
            regulation = [p for p in game["possessions"] if p["half"] in (1, 2)]
            openers = [next(p for p in regulation if p["quarter"] == q) for q in (1, 2, 3, 4)]
            self.assertEqual([p["start_spot"] for p in openers], [PRO_BOWL_SPOT] * 4)
            self.assertEqual(openers[0]["team"], openers[2]["team"])
            self.assertEqual(openers[1]["team"], openers[3]["team"])
            self.assertNotEqual(openers[0]["team"], openers[1]["team"])
            for p in regulation:
                top = (5 - p["quarter"]) * 900
                self.assertTrue(top - 900 <= p["end_clock"] < p["start_clock"] <= top)

    def test_receipt_audits_clean(self):
        from runtime.play_detail import check_ledger
        from runtime.statbook import make_receipt
        for game in self.games[:20]:
            for detail in ("full", "compact_stats"):
                receipt = make_receipt(game, week=20, matchup="B at A", detail=detail)
                self.assertEqual(check_ledger(receipt), [])

    def test_score_is_followed_by_a_placement(self):
        seen = 0
        for game in self.games:
            possessions = game["possessions"]
            for a, b in zip(possessions, possessions[1:]):
                scored = a["category"] == "touchdown" or a["category"] == "safety" or a.get("fg_made")
                if scored and b["half"] == a["half"] and b.get("quarter") == a.get("quarter"):
                    self.assertEqual(b["start_spot"], PRO_BOWL_SPOT)
                    self.assertEqual(b["start_kind"], "placement")
                    self.assertNotEqual(a["team"], b["team"])
                    seen += 1
        self.assertGreater(seen, 100)


class ProBowlDraftTests(unittest.TestCase):
    def test_quotas_and_captains(self):
        from scripts import pro_bowl
        method, honours = pro_bowl.load(pro_bowl.METHOD), pro_bowl.load(pro_bowl.HONOURS)
        for first in (0, 1):
            rosters, log = pro_bowl.run_draft(method, honours, first)
            names = [r["player"] for team in pro_bowl.TEAMS for r in rosters[team]]
            self.assertEqual(len(names), len(set(names)))
            self.assertEqual(sorted(len(rosters[t]) for t in pro_bowl.TEAMS), [42, 42])
            self.assertEqual(sum(r["how"] == "captain" for t in pro_bowl.TEAMS for r in rosters[t]), 4)
            first_picks = [e for e in log if e["how"] == "pick"]
            self.assertEqual(first_picks[0]["team"], pro_bowl.TEAMS[first])

    def test_first_pick_only_swaps_the_alternation(self):
        from scripts import pro_bowl
        method, honours = pro_bowl.load(pro_bowl.METHOD), pro_bowl.load(pro_bowl.HONOURS)
        one, _ = pro_bowl.run_draft(method, honours, 0)
        two, _ = pro_bowl.run_draft(method, honours, 1)
        self.assertNotEqual({r["player"] for r in one["Team One"]}, {r["player"] for r in two["Team One"]})


if __name__ == "__main__":
    unittest.main()
