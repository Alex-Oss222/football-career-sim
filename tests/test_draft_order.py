"""2014 draft order from the closed 2013 branch receipts (runtime.draft_order)."""
import unittest

from runtime import draft_order, postseason


class DraftOrderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.regular = draft_order._load(postseason.REGULAR_RECEIPTS)
        cls.post = draft_order._load(postseason.POSTSEASON_RECEIPTS)
        cls.rows = draft_order.order(cls.regular, cls.post)
        cls.by_club = {r["club"]: r for r in cls.rows}

    def test_every_club_once_in_32_slots(self):
        self.assertEqual([r["slot"] for r in self.rows], list(range(1, 33)))
        self.assertEqual(len(self.by_club), 32)

    def test_playoff_groups_follow_elimination(self):
        groups = [r["group"] for r in self.rows]
        self.assertEqual(groups[:20], ["non-playoff"] * 20)
        self.assertEqual(groups[20:], ["wild_card"] * 4 + ["divisional"] * 4 + ["conference"] * 2
                         + ["super_bowl_loser", "champion"])
        self.assertEqual(self.rows[-1]["club"], postseason.winner(
            next(r for r in self.post if int(r["week"]) == 21)))

    def test_non_playoff_order_is_by_percentage_then_sos(self):
        head = self.rows[:20]
        for a, b in zip(head, head[1:]):
            self.assertLessEqual((a["pct"], round(a["sos"], 6)), (b["pct"], round(b["sos"], 6)))

    def test_jacksonville_lost_divisional(self):
        self.assertEqual(self.by_club["Jacksonville Jaguars"]["group"], "divisional")
        self.assertIn(self.by_club["Jacksonville Jaguars"]["slot"], range(25, 29))

    def test_cross_conference_tie_is_never_resolved_by_invention(self):
        for r in self.rows:
            if r["tie"] and r["tie"].startswith("coin flip pending"):
                self.assertTrue(any(o["tie"] and r["club"] in o["tie"] for o in self.rows))

    def test_order_requires_a_closed_super_bowl(self):
        with self.assertRaises(ValueError):
            draft_order.order(self.regular, [r for r in self.post if int(r["week"]) != 21])


if __name__ == "__main__":
    unittest.main()
