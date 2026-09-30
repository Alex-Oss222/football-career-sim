"""February 2014: the deferred carousel and retained-club coordinator openings
(career/2014/early_offseason/staff_changes/carousel_deferred_method.json)."""
from datetime import date
import random
import unittest

from scripts import coaching_carousel as cc
from scripts import coaching_carousel_deferred as d


class DeferredCarouselTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m, cls.m75 = cc.load(d.METHOD), cc.load(cc.METHOD)
        cls.clubs = cc.inputs()
        cls.runs = [d.resolve(random.Random(i), cls.m, cls.clubs, cls.m75) for i in range(2000)]

    def test_deterministic(self):
        a = d.resolve(random.Random(7), self.m, self.clubs, self.m75)
        b = d.resolve(random.Random(7), self.m, self.clubs, self.m75)
        self.assertEqual(a, b)

    def test_window_and_candidates(self):
        for changes, openings, events, departed, pending in self.runs:
            self.assertEqual([c["club"] for c in changes], list(d.DEFERRED))
            for e in events:
                when = date.fromisoformat(e["date"])
                self.assertGreaterEqual(when, d.FIRST_REQUEST)
                self.assertLessEqual(when, d.END)
                self.assertNotIn(e["coach"], d.GONE)
                if e["job"] == "head coach":
                    self.assertGreaterEqual(when, d.OPENS_D1)
            for o in openings:
                self.assertNotIn(o["club"], d.CHANGED_ENTRY_75)
                self.assertNotEqual(o["club"], cc.JAX)

    def test_permissions_and_one_hire_per_job(self):
        for _, _, events, departed, _ in self.runs:
            hires = [(e["club"], e["job"]) for e in events if e["event"] == "hired"]
            self.assertEqual(len(hires), len(set(hires)))
            self.assertEqual(len(hires), len(departed))
            for e in events:
                if e["event"] == "hired" and e["job"] != "head coach":
                    self.assertFalse(cc.STAFF[e["coach"]].get("coordinator"), e)


if __name__ == "__main__":
    unittest.main()
