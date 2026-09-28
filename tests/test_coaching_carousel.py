"""The January 2014 coaching carousel follows the sourced 2013-14 rules
(library/2014_coaching_hiring_and_anti_tampering_rules.md section 8)."""
from datetime import date
import random
import unittest

from scripts import coaching_carousel as cc


class CarouselRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.method = cc.load(cc.METHOD)
        cls.clubs = cc.inputs()
        cls.runs = [cc.resolve(random.Random(i), cls.method, cls.clubs) for i in range(3000)]

    def test_inputs(self):
        self.assertEqual(len(self.clubs), 32)
        self.assertIsNone(self.clubs[cc.JAX]["p_change"])
        self.assertEqual(self.clubs["New Orleans Saints"]["tenure"], 7)
        for team, c in self.clubs.items():
            if team != cc.JAX:
                self.assertTrue(0 < c["p_change"] < 1, team)

    def test_windows_and_hire_dates(self):
        for changes, events, departed, pending in self.runs:
            for e in events:
                when = date.fromisoformat(e["date"])
                self.assertLessEqual(when, cc.BRANCH_DATE)
                if e["job"] == "head coach":
                    self.assertGreaterEqual(when, cc.HC_WINDOW_OPENS)
                else:
                    self.assertGreater(when, cc.ELIMINATED_JAX)
                if e["event"] == "hired":
                    self.assertGreater(when, cc.ELIMINATED_JAX)

    def test_permissions(self):
        for _, events, _, _ in self.runs:
            for e in events:
                if e["event"].startswith("permission"):
                    if e["job"] == "head coach":
                        self.assertEqual(e["event"], "permission granted")
                    elif cc.STAFF[e["coach"]].get("coordinator") or e["job"] == cc.STAFF[e["coach"]]["job"]:
                        self.assertEqual(e["event"], "permission refused")
                    else:
                        self.assertEqual(e["event"], "permission granted")

    def test_stages_are_logged_in_order_and_departures_are_final(self):
        for _, events, departed, _ in self.runs:
            for name, d in departed.items():
                later = [e for e in events if e["coach"] == name and e["date"] > d["date"]]
                self.assertEqual(later, [], name)
                self.assertTrue(any(e["event"] == "interview" and e["coach"] == name for e in events))
            hires = [e for e in events if e["event"] == "hired"]
            self.assertEqual(len(hires), len(departed))

    def test_super_bowl_clubs_are_deferred(self):
        for changes, _, _, _ in self.runs:
            for c in changes:
                if c["club"] in ("Buffalo Bills", "Minnesota Vikings"):
                    self.assertEqual(c.get("deferred"), self.method["deferred_procedure"]["event_id"])
                    self.assertIsNone(c["changed"])
                else:
                    self.assertIn(c["changed"], (True, False))

    def test_one_hire_per_club_job(self):
        for _, events, departed, _ in self.runs:
            jobs = [(d["club"], d["job"]) for d in departed.values()]
            self.assertEqual(len(jobs), len(set(jobs)))
            offers = [(e["club"], e["job"]) for e in events if e["event"] == "hired"]
            self.assertEqual(len(offers), len(set(offers)))

    def test_head_coach_hire_date_follows_jacksonville_hire(self):
        seen = 0
        for changes, _, departed, _ in self.runs:
            by_club = {c["club"]: c for c in changes}
            for name, d in departed.items():
                row = by_club[d["club"]]
                if d["job"] == "head coach":
                    seen += 1
                    self.assertEqual(row["hire_day"], d["date"])
                    self.assertIn(name, row["hired_from"])
                    self.assertGreater(date.fromisoformat(d["date"]), cc.ELIMINATED_JAX)
            for c in changes:
                if c["changed"] and c["hired_from"] == "external":
                    self.assertNotIn((c["club"], "head coach"), [(d["club"], d["job"]) for d in departed.values()])
        self.assertGreater(seen, 0)

    def test_pending_is_recorded_not_resolved(self):
        seen = 0
        for _, events, departed, pending in self.runs:
            for p in pending:
                seen += 1
                self.assertNotIn(p["coach"], departed)
                self.assertTrue(any(e["event"] == "interview" and e["coach"] == p["coach"] and e["club"] == p["club"]
                                    for e in events))
                self.assertFalse(any(e["event"] in ("offer", "hired") and e["coach"] == p["coach"] and e["club"] == p["club"]
                                     for e in events))
        self.assertGreater(seen, 0)

    def test_in_window_head_coach_detail_names_w11(self):
        for _, events, _, _ in self.runs:
            for e in events:
                if e["event"] == "permission granted" and e["job"] == "head coach":
                    if date.fromisoformat(e["date"]) <= cc.ELIMINATED_JAX:
                        self.assertIn("W11", e["detail"])
                    else:
                        self.assertIn("T2", e["detail"])

    def test_determinism(self):
        a = cc.resolve(random.Random(7), self.method, self.clubs)
        b = cc.resolve(random.Random(7), self.method, self.clubs)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
