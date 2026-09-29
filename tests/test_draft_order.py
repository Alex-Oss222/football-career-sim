"""2014 draft order from the closed 2013 branch receipts (runtime.draft_order)."""
import unittest
import copy
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock

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


class SevenRoundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.first = draft_order.order()
        cls.register = draft_order.load_ownership()
        cls.rows = draft_order.seven_rounds(cls.first, cls.register)

    def asset(self, rnd, club):
        return next(r for r in self.rows if r["round"] == rnd and r["club"] == club)

    def test_all_224_assets_once_and_each_round_has_32_original_clubs(self):
        self.assertEqual(len(self.rows), 224)
        self.assertEqual(len({(r["round"], r["club"]) for r in self.rows}), 224)
        for rnd in range(1, 8):
            rows = [r for r in self.rows if r["round"] == rnd]
            self.assertEqual({r["club"] for r in rows}, set(draft_order.TEAMS))
            self.assertEqual({slot for r in rows for slot in r["slot_options"]}, set(range(1, 33)))
            self.assertEqual(len([r for r in rows if r["coin_flip_pending"]]), 2)

    def test_two_club_rotation_changes_seattle_second_to_36(self):
        self.assertEqual(self.asset(1, "Seattle Seahawks")["slot_options"], [5])
        self.assertEqual(self.asset(2, "Seattle Seahawks")["base_overall_options"], [36])
        self.assertEqual(self.asset(2, "Houston Texans")["base_overall_options"], [37])
        self.assertEqual(self.asset(3, "Seattle Seahawks")["slot_options"], [5])

    def test_larger_segment_rotates_even_when_sos_is_different(self):
        first = ["Denver Broncos", "Cleveland Browns", "Detroit Lions", "Chicago Bears", "Oakland Raiders", "Miami Dolphins"]
        for rnd in range(1, 8):
            offset = (rnd - 1) % len(first)
            expected = first[offset:] + first[:offset]
            actual = [r["club"] for r in self.rows if r["round"] == rnd and r["slot_options"][0] in range(7, 13)]
            self.assertEqual(actual, expected)

    def test_playoff_priority_groups_never_rotate_together(self):
        # Buffalo, KC, Pittsburgh and Tampa Bay all finished 9-7. The champion
        # remains 32; only the three Wild Card losers rotate among 21-23.
        for rnd in range(1, 8):
            self.assertEqual(self.asset(rnd, "Buffalo Bills")["slot_options"], [32])
            slots = [self.asset(rnd, c)["slot_options"][0] for c in
                     ("Kansas City Chiefs", "Pittsburgh Steelers", "Tampa Bay Buccaneers")]
            self.assertEqual(set(slots), {21, 22, 23})
            self.assertEqual(self.asset(rnd, "Dallas Cowboys")["slot_options"], [25])
            self.assertEqual(self.asset(rnd, "Philadelphia Eagles")["slot_options"], [29])

    def test_coin_uncertainty_matches_both_possible_realizations_every_round(self):
        # Independently enumerate the two permitted first-round arrangements.
        scenarios = []
        for reverse in (False, True):
            first = copy.deepcopy(self.first)
            if reverse:
                first[13], first[14] = first[14], first[13]
                first[13]["slot"], first[14]["slot"] = 14, 15
            for row in first:
                if row["tie"] and row["tie"].startswith("coin flip pending"):
                    row["tie"] = "test-only recorded coin result"
            scenarios.append(draft_order.seven_rounds(first, self.register))
        for row in self.rows:
            possibilities = set()
            for scenario in scenarios:
                actual = next(r for r in scenario if (r["round"], r["club"]) == (row["round"], row["club"]))
                possibilities.update(actual["slot_options"])
            self.assertEqual(set(row["slot_options"]), possibilities)
        self.assertEqual(self.asset(2, "Green Bay Packers")["slot_options"], [14, 19])

    def test_no_alphabetical_coin_result_for_same_conference(self):
        season = Mock(recording=False, notes=[])
        def fallback(*args):
            season.notes.append({"step": None})
            return "Miami Dolphins"
        season.best_of.side_effect = fallback
        rows = draft_order._break(season, ["Miami Dolphins", "New York Jets"], {})
        self.assertTrue(all(note.startswith("coin flip pending") for _, note in rows))
        self.assertFalse(season.recording)
        self.assertEqual(season.notes, [])

    def test_corrected_cousins_deal_has_one_owner_for_each_asset(self):
        washington = self.asset(1, "Washington Redskins")
        self.assertEqual(washington["owner"], "Jacksonville Jaguars")
        self.assertEqual(washington["base_overall_options"], [13])
        self.assertEqual(self.asset(1, "Jacksonville Jaguars")["base_overall_options"], [26])
        second = self.asset(2, "Jacksonville Jaguars")
        self.assertEqual((second["owner"], second["base_overall_options"]), ("Washington Redskins", [58]))
        owned = [r for r in self.rows if r["owner"] == "Jacksonville Jaguars"]
        self.assertEqual(len(owned), 7)
        self.assertEqual([r["round"] for r in owned], [1, 1, 3, 4, 5, 6, 7])
        self.assertEqual(draft_order.ownership_for(2015, 2, "Jacksonville Jaguars", self.register)[0], "Washington Redskins")
        self.assertEqual(self.asset(1, "St. Louis Rams")["owner"], "St. Louis Rams")

    def test_traded_pick_follows_original_club_rotation_not_current_owner(self):
        carolina = self.asset(7, "Carolina Panthers")
        self.assertEqual(carolina["owner"], "San Francisco 49ers")
        self.assertEqual(carolina["slot_options"], [19])
        self.assertEqual(self.asset(7, "San Francisco 49ers")["slot_options"], [1])

    def test_compensatory_unknowns_are_retained_and_start_after_round_three(self):
        self.assertIsNone(self.register["compensatory"]["round_counts"])
        self.assertEqual(self.register["compensatory"]["qualifying_free_agency_year"], 2013)
        for rnd in range(1, 8):
            row = self.asset(rnd, "Jacksonville Jaguars")
            self.assertEqual(row["compensatory_after_rounds"], list(range(3, rnd)))
        self.assertEqual(self.asset(3, "Jacksonville Jaguars")["base_overall_options"], [90])
        from scripts.render_draft_order import overall
        self.assertEqual(overall(self.asset(4, "Jacksonville Jaguars")), "122 + C3")
        self.assertEqual(overall(self.asset(7, "Jacksonville Jaguars")), "218 + C3 + C4 + C5 + C6")

    def test_ownership_register_rejects_double_ownership_and_invalid_assets(self):
        bad = []
        duplicate = copy.deepcopy(self.register)
        extra = copy.deepcopy(duplicate["transfers"][0])
        extra["owner"] = "St. Louis Rams"
        duplicate["transfers"].append(extra)
        bad.append(duplicate)
        for field, value in (("round", 8), ("owner", "Unknown Team"), ("draft_year", 2013)):
            record = copy.deepcopy(self.register)
            record["transfers"][0][field] = value
            bad.append(record)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "picks.json"
            for record in bad:
                with self.subTest(record=record["transfers"][-1]):
                    path.write_text(json.dumps(record))
                    with self.assertRaises(ValueError):
                        draft_order.load_ownership(path)

    def test_default_other_club_allocation_is_not_claimed_verified(self):
        row = self.asset(2, "Kansas City Chiefs")
        self.assertEqual(row["ownership_status"], "provisional")


if __name__ == "__main__":
    unittest.main()
