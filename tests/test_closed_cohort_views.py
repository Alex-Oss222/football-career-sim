"""Kernel 2014.6 plumbing (batch B1): closed cohorts stay exactly as audited.

Every committed 2013 and 2014 (Weeks 1-4 and preseason) view generated from
closed receipts regenerates byte-identically: the season stat views
(including each calibration audit), standings, box scores, preseason views,
the award shortlists and the 2014 award pages; and check_ledger, dispatched
by each receipt's own kernel version, returns the recorded output with the
recorded measurable classes for every committed receipt
(tests/data/closed_cohort_ledger.json, recorded before B1). Closed games are
never rerun and closed receipts are never edited."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashlib
import json
import unittest

from runtime.calibration_base import BASE_2012, base_for_result
from runtime.play_detail import check_ledger, measurable_classes
from runtime.seasons import SeasonPaths

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TEAM = "Jacksonville Jaguars"
LEDGER = Path(__file__).parent / "data/closed_cohort_ledger.json"


def receipts_in(folder):
    return [json.loads(p.read_text()) for p in sorted(Path(folder).glob("*.json"))]


class ClosedSeasonViewTests(unittest.TestCase):
    def check_views(self, year, receipts, folder):
        from scripts.render_season_stats import render_views
        views = render_views(year, TEAM, receipts)
        self.assertIn("calibration_audit.md", views)
        for name, text in views.items():
            with self.subTest(year=year, view=name):
                self.assertEqual((folder / name).read_text(encoding="utf-8"), text)

    def test_2013_season_views_and_standings(self):
        from scripts.render_standings import render
        paths = SeasonPaths(2013, ROOT)
        receipts = receipts_in(paths.receipts)
        self.assertEqual(len(receipts), 256)
        self.check_views(2013, receipts, paths.stats)
        self.assertEqual((ROOT / "career/2013/standings.md").read_text(), render(2013, receipts))

    def test_2014_season_views_and_standings(self):
        from scripts.render_standings import render
        paths = SeasonPaths(2014, ROOT)
        receipts = receipts_in(paths.receipts)
        self.assertEqual(len(receipts), 61)
        self.assertEqual({int(r["week"]) for r in receipts}, {1, 2, 3, 4})
        self.check_views(2014, receipts, paths.stats)
        self.assertEqual(paths.record("standings.md").read_text(), render(2014, receipts))

    def test_box_scores(self):
        from scripts.render_box_score import stale_blocks
        outputs = sorted((ROOT / "career/2013/regular_season").glob("*/output.md"))
        outputs += sorted((ROOT / "career/2013/postseason").glob("*/output.md"))
        self.assertTrue(outputs)
        for output in outputs:
            with self.subTest(output=output.relative_to(ROOT).as_posix()):
                self.assertEqual(stale_blocks(output, ROOT / "career/2013/stats/game_receipts"), [])
        paths = SeasonPaths(2014, ROOT)
        outputs = sorted(paths.regular_season.glob("*/output.md")) + sorted(paths.postseason.glob("*/output.md"))
        self.assertTrue(outputs)
        for output in outputs:
            with self.subTest(output=output.relative_to(ROOT).as_posix()):
                self.assertEqual(stale_blocks(output, paths.receipts, season=2014), [])
        games = sorted(p for pattern in ("Game_*/output.md", "game_*/output.md")
                       for p in paths.preseason_games_dir.glob(pattern))
        self.assertTrue(games)
        for output in games:
            with self.subTest(output=output.relative_to(ROOT).as_posix()):
                self.assertEqual(stale_blocks(output, paths.preseason_receipts, season=2014), [])

    def test_2014_preseason_views(self):
        from scripts.render_preseason_stats import stale_views
        paths = SeasonPaths(2014, ROOT)
        self.assertEqual(len(receipts_in(paths.preseason_receipts)), 4)
        self.assertEqual(stale_views(paths), [])


class ClosedAwardViewTests(unittest.TestCase):
    def test_shortlists_recompute_from_the_receipts(self):
        from scripts.league_awards import load_results, method, shortlists
        for year in (2013, 2014):
            m, results = method(year), load_results(year)
            self.assertTrue(results, year)
            for period, entry in results.items():
                lists = shortlists(entry["kind"], entry["key"], m, year)
                for award, record in entry["awards"].items():
                    with self.subTest(year=year, period=period, award=award):
                        self.assertEqual(record["shortlist"], lists[award])

    def test_2014_award_pages(self):
        from runtime.events import preserve_event_comments
        from scripts.render_award_pages import render_pages
        folder = SeasonPaths(2014, ROOT).awards
        results = json.loads((folder / "results.json").read_text())
        method = json.loads((folder / "methodology.json").read_text())
        pages = render_pages(2014, results, method)
        self.assertTrue(pages)
        for relative, text in pages.items():
            with self.subTest(page=relative):
                previous = (folder / relative).read_text()
                self.assertEqual(previous, preserve_event_comments(text, previous))


class ClosedLedgerTests(unittest.TestCase):
    def test_every_committed_receipt_audits_as_recorded(self):
        fixture = json.loads(LEDGER.read_text())
        rows = {}
        for year in (2013, 2014):
            paths = SeasonPaths(year, ROOT)
            for folder in (paths.receipts, paths.postseason_receipts, paths.preseason_receipts):
                for path in sorted(Path(folder).glob("*.json")):
                    receipt = json.loads(path.read_text())
                    self.assertIs(base_for_result(receipt), BASE_2012)
                    rows[path.relative_to(ROOT).as_posix()] = {"errors": check_ledger(receipt),
                                                              "measurable": sorted(measurable_classes(receipt))}
        self.assertEqual(len(rows), fixture["receipts"])
        self.assertEqual({k: [len(v["measurable"]), v["errors"]] for k, v in rows.items()}, fixture["rows"])
        blob = json.dumps(rows, sort_keys=True, separators=(",", ":"))
        self.assertEqual(hashlib.sha256(blob.encode()).hexdigest(), fixture["digest"])


if __name__ == "__main__":
    unittest.main()
