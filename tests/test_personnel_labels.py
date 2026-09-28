import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from runtime.play_detail import _personnel_fits, _personnel_slots
from synthetic_games import sample, sample_teams


def call(personnel):
    return {"personnel": personnel}


class PersonnelLabelTests(unittest.TestCase):
    def test_slots(self):
        self.assertEqual(_personnel_slots("22"), {"RB": 2, "FB": 2, "TE": 2, "WR": 1})
        self.assertEqual(_personnel_slots("11"), {"RB": 1, "FB": 1, "TE": 1, "WR": 3})
        self.assertIsNone(_personnel_slots("6OL"))
        self.assertIsNone(_personnel_slots(None))

    def test_fits(self):
        # 22: one receiver plus one rotation spot.
        self.assertTrue(_personnel_fits(call("22"), "WR", 1))
        self.assertTrue(_personnel_fits(call("22"), "WR", 2))
        self.assertFalse(_personnel_fits(call("22"), "WR", 3))
        self.assertFalse(_personnel_fits(call("22"), "WR", 4))
        # 12: WR3 rotates in ("Thielen / Blackmon"); WR4 does not.
        self.assertTrue(_personnel_fits(call("12"), "WR", 3))
        self.assertFalse(_personnel_fits(call("12"), "WR", 4))
        # A fullback needs two backs.
        self.assertTrue(_personnel_fits(call("21"), "FB", 1))
        self.assertFalse(_personnel_fits(call("12"), "FB", 1))
        # No receivers in a 23-type code; quarterbacks and 6OL always fit.
        self.assertFalse(_personnel_fits(call("23"), "WR", 1))
        self.assertTrue(_personnel_fits(call("22"), "QB", 1))
        self.assertTrue(_personnel_fits(call("6OL"), "WR", 5))

    def test_sample_labels_respect_personnel(self):
        a, _ = sample_teams()
        by_id = {p.player_id: p for p in a.roster}
        from runtime import usage
        checked = 0
        for result in sample():
            for row in result.get("play_ledger") or []:
                if row.get("offense") != "A" or row.get("label_source") != "sheet":
                    continue
                player = row.get("target") if row.get("play_type") == "pass" else row.get("runner")
                if not player or player not in by_id or row.get("scramble"):
                    continue
                grp = usage.group(by_id[player].position)
                ordered = usage.depth_order(tuple(p for p in a.roster if p.available), grp)
                rank = next((i for i, p in enumerate(ordered, 1) if p.player_id == player), None)
                checked += 1
                self.assertTrue(_personnel_fits(row, grp, rank), (row.get("concept"), player, rank))
        self.assertGreater(checked, 1000)


if __name__ == "__main__":
    unittest.main()
