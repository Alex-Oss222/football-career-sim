import unittest
from runtime.injury import relative_position_weight, football_status

class InjuryTests(unittest.TestCase):
    def test_position_risk_ordering_matches_source_model(self):
        self.assertGreater(relative_position_weight("WR"), relative_position_weight("QB"))
        self.assertGreater(relative_position_weight("TE"), relative_position_weight("OL"))
        self.assertGreater(relative_position_weight("DB"), relative_position_weight("DL"))
    def test_statuses_are_bounded(self):
        for s in ("practice_limited","short_absence","multi_week","long_term"):
            self.assertTrue(football_status(s))

if __name__ == "__main__":
    unittest.main()
