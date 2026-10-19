"""The statistics, award and league transactions pages read as football and keep their limits,
and each fact a page shows is read from its stored owner (rebuild step 4 review fixes).

- The snaps-by-label page keeps the evidence limit of its record: a label is matched to a snap
  after the play, so its counts are neither the calls made nor proof that a call worked (R1).
- The league transactions page lists each move's date, club, move, player and status; the
  rails' hold and verification mechanics stay in the data and the detail report (R8).
- The award pages name the winner and the nominees, never a formula score or a selection
  weight; 2013's pages keep their layout (R10).
- The in-season record of a week is read from the data area only; a page written before Week 6
  must carry the same record (F6).
- The first clean season is one fact (runtime/seasons.CLEAN_SEASON) every builder reads (F11).
"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.clean_pages import page_errors  # noqa: E402
from runtime.seasons import CLEAN_SEASON, GAME_REPORT_FROM, SeasonPaths  # noqa: E402

SEASON = GAME_REPORT_FROM[0]
JAX = "Jacksonville Jaguars"


def receipts():
    from scripts.render_season_stats import load_receipts
    return load_receipts(SeasonPaths(SEASON, ROOT).receipts)


class SnapsByLabelTests(unittest.TestCase):
    def test_the_page_keeps_the_label_limit(self):
        from runtime.statbook import aggregate_receipts
        from scripts.render_season_stats import INDEXED_VIEWS, clean_play_calls_markdown
        games = receipts()
        if not games:
            self.skipTest("no closed game")
        text = clean_play_calls_markdown(SEASON, JAX, aggregate_receipts(games))
        self.assertTrue(text.startswith("# %d %s snaps by call-sheet label" % (SEASON, JAX)))
        self.assertIn("matched after the play", text)
        self.assertIn("not which call was made or how well a call worked", text)
        self.assertNotIn("what they gained", text)
        if "## Defensive snaps by situation" in text:
            self.assertIn("| Week | Situation | Sheet wording | SNAPS |", text)
            self.assertIn("not the call on every such snap or evidence that a call worked", text)
        title, what = next((t, w) for name, t, w in INDEXED_VIEWS if name == "play_call_stats.md")
        self.assertEqual(title, "%s snaps by call-sheet label")
        self.assertIn("not the calls made", what)


class LeagueTransactionsTests(unittest.TestCase):
    def latest_week(self):
        from runtime import rails
        data = rails.load(SEASON, ROOT)
        closed = sorted({int(r["week"]) for r in receipts()})
        if data is None or not closed or max(closed) < data.effective_from_week:
            self.skipTest("no closed week with the in-season roster moves")
        return max(closed)

    def test_the_page_is_the_leagues_transactions(self):
        from scripts import render_inseason_rails as builder
        week = self.latest_week()
        for w in (week, week + 1):
            text = builder.render(SEASON, w, ROOT, [r for r in receipts() if int(r["week"]) < w])
            rel = builder.page_path(SEASON, w, ROOT).relative_to(ROOT).as_posix()
            self.assertEqual(page_errors(rel, text, root=ROOT), [])
            self.assertTrue("| Date | Club | Move | Player | Status |" in text or "No roster move took effect." in text)
            for word in ("Real", "real ", "Held", "hold", "ruling", "verified", "administrative", "Cutoff",
                         "Basis", "Applied", "never carried"):
                self.assertNotIn(word, text, (w, word))
            for line in text.splitlines():
                if line.startswith("| ") and not line.startswith("| Date"):
                    self.assertEqual(len(line.strip("|").split("|")), 5, line)
        # The hold mechanics and the moves not applied stay in the staff's detail report.
        detail = builder.detail(SEASON, week, ROOT)
        self.assertIn("## Held additions", detail)
        self.assertIn("## Not applied", detail)

    def test_the_weeks_record_is_read_from_the_data_area_only(self):
        from scripts import render_inseason_rails as builder
        week = self.latest_week()
        tmp = tempfile.TemporaryDirectory(dir=ROOT.parent)
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name) / "repo"
        shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", ".sim_cache", "__pycache__"), symlinks=True)
        self.assertEqual(builder.check(SEASON, root), [])
        meta = builder.meta_path(SEASON, week, root)
        self.assertTrue(meta.relative_to(root).as_posix().startswith("data/"))
        recorded = meta.read_text(encoding="utf-8")
        meta.unlink()
        self.assertTrue(any("record missing" in e for e in builder.check(SEASON, root)))
        page = builder.page_path(SEASON, week, root)
        if builder.EMBEDDED_META.search(page.read_text(encoding="utf-8")):
            # A page written before Week 6 carries its record; the stored one must be the same.
            changed = json.loads(recorded)
            changed["as_of"] = "1999-01-01"
            meta.write_text(json.dumps(changed), encoding="utf-8")
            self.assertTrue(any("differs from the record its page carries" in e for e in builder.check(SEASON, root)))
        meta.write_text(recorded, encoding="utf-8")
        self.assertEqual(builder.check(SEASON, root), [])


class AwardPagesTests(unittest.TestCase):
    def test_the_pages_name_the_nominees_without_scores(self):
        from scripts import league_awards
        from scripts.render_award_pages import award_cards, render_pages
        results = league_awards.load_results(SEASON)
        if not results:
            self.skipTest("no award recorded")
        pages = render_pages(SEASON, results, league_awards.method(SEASON), root=ROOT)
        for rel, text in pages.items():
            lowered = text.lower()
            words = ("score", "formula", "panel", "weigh", "finalist") if rel.endswith(".md") else ("score", "finalist")
            for word in words:
                self.assertNotIn(word, lowered, (rel, word))
        week = next(rel for rel in pages if rel.startswith("week_") and rel.endswith("README.md"))
        self.assertIn("| Photo | Player | Team | Result |", pages[week])
        self.assertIn("| Nominee |", pages[week])
        shortlist = [{"player": "A", "team": "T", "score": 30.0}, {"player": "B", "team": "U", "score": 20.0}]
        self.assertIn("Shortlist score", award_cards("Award", shortlist, 0))           # 2013's cards
        self.assertNotIn("Shortlist score", award_cards("Award", shortlist, 0, scores=False))


class CleanSeasonTests(unittest.TestCase):
    def test_every_builder_reads_the_first_clean_season(self):
        from scripts import rebuild_pages, render_award_pages, render_season_stats, render_standings, render_team_tracker
        self.assertEqual(CLEAN_SEASON, GAME_REPORT_FROM[0])
        for module in (render_season_stats, render_standings, render_team_tracker, render_award_pages):
            self.assertEqual(module.CLEAN_FROM, CLEAN_SEASON, module.__name__)
        self.assertEqual(rebuild_pages.FIRST_SEASON, CLEAN_SEASON)


if __name__ == "__main__":
    unittest.main()
