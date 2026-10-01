import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import season_honours as honours


class SeasonHonoursTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m, cls.evidence, cls.receipts, cls.built = honours.build()

    def test_slot_counts(self):
        for team in ("first", "second"):
            for slot, n in self.m["all_pro"]["slots"].items():
                self.assertEqual(len(self.built["all_pro"][team][slot]), n, (team, slot))
        for slot, n in self.m["pro_bowl"]["slots"].items():
            self.assertEqual(len(self.built["pro_bowl"]["selections"][slot]), n, slot)

    def test_one_lineman_per_club_per_position(self):
        for slot in ("T", "G", "C"):
            clubs = [e["team"] for e in self.built["pro_bowl"]["selections"][slot]]
            self.assertEqual(len(clubs), len(set(clubs)), slot)
            first = self.built["all_pro"]["first"][slot] + self.built["all_pro"]["second"][slot]
            self.assertEqual(len(first), len({e["team"] for e in first}), slot)

    def test_super_bowl_players_are_replaced(self):
        sb = set(self.built["pro_bowl"]["super_bowl_clubs"])
        self.assertEqual(len(sb), 2)
        for entries in self.built["pro_bowl"]["selections"].values():
            for e in entries:
                if e["team"] in sb:
                    self.assertEqual(e["reason"], "club in Super Bowl XLVIII")
                if e["replaced_by"]:
                    self.assertNotIn(e["replaced_by"]["team"], sb)

    def test_award_eligibility(self):
        lists = self.built["shortlists"]
        for award, pool in (("OROY", "rookies"), ("DROY", "rookies"), ("CPOY", "comeback_eligible")):
            for row in lists[award]:
                self.assertIn(row["player"], self.evidence[pool], award)
        for award, rows in lists.items():
            self.assertEqual(len(rows), self.m["ap_awards"]["shortlist_size"], award)

    def test_pro_bowl_window_excludes_week_17(self):
        self.assertEqual(self.m["evidence"]["windows"]["pro_bowl"], [1, 16])
        rows16 = honours.season_rows(self.receipts, 1, 16, self.m, self.evidence)
        rows17 = honours.season_rows(self.receipts, 1, 17, self.m, self.evidence)
        self.assertNotEqual(sum(r["offense"] for r in rows16.values()),
                            sum(r["offense"] for r in rows17.values()))

    def test_evidence_uses_no_real_2013_outcome(self):
        text = json.dumps(self.evidence["sources"])
        self.assertNotIn("award", text.lower())

    def test_render_preserves_frozen_awards_and_uses_named_records(self):
        before = honours.RESULTS.read_bytes()
        results = json.loads(before)
        with tempfile.TemporaryDirectory() as folder:
            page = Path(folder) / 'season_honours.md'
            with patch.object(honours, 'PAGE', page):
                honours.render()
            text = page.read_text()
        self.assertEqual(honours.RESULTS.read_bytes(), before)
        self.assertIn('February 2, 2014', text)
        self.assertIn('[Pro Bowl record](../pro_bowl/README.md)', text)
        self.assertNotRegex(text, r'\bEntr(?:y|ies) \d+')
        for award, result in results['ap_awards'].items():
            winner = result['shortlist'][result['winner_index']]
            self.assertIn('| %s | %s | %s | %s |' % (
                self.m['ap_awards']['names'][award], honours.name_of(winner),
                winner['team'], winner['score']), text)


if __name__ == "__main__":
    unittest.main()
