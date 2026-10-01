"""The 2014-onward gamebook box score, the unchanged 2013 box score, and the
coach record table, all read from receipts only."""
import datetime as dt
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime.gamebook import GamebookError, line_score_table, render as render_gamebook
from runtime.statbook import make_receipt
from scripts import render_box_score, render_coach_record


def synthetic_receipt(detail="full"):
    from synthetic_games import sample
    return make_receipt(sample()[0], week=1, matchup="B at A", detail=detail)


def table_after(text, title):
    """Rows (list of cells) of the Markdown table that follows a bold or #### title."""
    body = text.split(title, 1)[1]
    rows = []
    for line in body.splitlines()[1:]:
        if line.startswith("|"):
            rows.append([c.strip() for c in line.strip("|").split("|")])
        elif rows:
            break
    return rows[2:]  # drop header and separator


class GamebookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = synthetic_receipt()
        cls.text = render_gamebook(cls.receipt, "A")

    def test_sections_in_template_order_with_lead_club_first(self):
        order = ["#### Scoring summary", "#### Team stats for the game", "#### A stats for the game",
                 "#### B stats for the game", "#### Drive chart", "#### Snap counts"]
        positions = [self.text.index(h) for h in order]
        self.assertEqual(positions, sorted(positions))
        for title in ("**Passing**", "**Rushing**", "**Receiving**", "**Defense**", "**Kicking**", "**Punting**"):
            self.assertIn(title, self.text)

    def test_scoring_summary_adds_to_the_final_score(self):
        rows = table_after(self.text, "#### Scoring summary")
        self.assertTrue(rows)
        final = self.receipt["final_score"]
        self.assertEqual([int(rows[-1][-2]), int(rows[-1][-1])], [final["B"], final["A"]])
        broken = json.loads(json.dumps(self.receipt))
        broken["final_score"]["A"] += 3
        with self.assertRaises(GamebookError):
            render_gamebook(broken, "A")

    def test_player_lines_add_to_team_totals(self):
        stats = self.receipt["team_stats"]
        for club in ("A", "B"):
            section = self.text.split("#### %s stats for the game" % club, 1)[1].split("####", 1)[0]
            rushing = table_after(section, "**Rushing**")
            self.assertEqual(rushing[-1][0], "Team total")
            self.assertEqual(sum(int(r[2]) for r in rushing[:-1]), int(rushing[-1][2]))
            self.assertEqual(int(rushing[-1][2]), stats[club]["rushing_yards"])
            receiving = table_after(section, "**Receiving**")
            self.assertEqual(sum(int(r[3]) for r in receiving[:-1]), stats[club]["passing_yards"])
            defense = table_after(section, "**Defense**")
            self.assertEqual(sum(int(r[1]) for r in defense[:-1]), int(defense[-1][1]))
        team = table_after(self.text, "#### Team stats for the game")
        by_label = {r[1]: r[2:] for r in team}
        self.assertEqual(by_label["Final score"], [str(stats["A"]["points"]), str(stats["B"]["points"])])
        self.assertEqual(by_label["Total first downs"], [str(stats["A"]["first_downs"]), str(stats["B"]["first_downs"])])
        for club, column in (("A", 0), ("B", 1)):
            parts = [int(by_label[k][column]) for k in ("By rushing", "By passing", "By penalty")]
            self.assertEqual(sum(parts), stats[club]["first_downs"])

    def test_unsupported_rows_and_columns_are_left_out(self):
        for absent in ("QB HITS", "OWN REC", "Two-point", "had blocked", "| FC |", "Definitions"):
            self.assertNotIn(absent, self.text)
        for present in ("Success rate", "Explosive plays", "Red zone efficiency", "Net punting average",
                        "Kickoffs, number and touchbacks", "Field goal attempts:"):
            self.assertIn(present, self.text)

    def test_no_unrendered_cells(self):
        self.assertNotIn("None", self.text)
        self.assertNotIn("nan", self.text.lower().split())

    def test_compact_receipt_drops_only_ledger_derived_items(self):
        text = render_gamebook(synthetic_receipt("compact_stats"), "A")
        self.assertIn("#### Team stats for the game", text)
        self.assertIn("Third down efficiency", text)
        for absent in ("Success rate", "Red zone efficiency", "Scoring summary", "| FG% | LNG |", "| LNG | RTG |"):
            self.assertNotIn(absent, text)
        self.assertIn("| Player | CMP/ATT | YDS | AVG | TD | INT | SCK-YDS | RTG |", text)

    def test_drive_chart_and_snap_counts_cover_every_possession_and_participant(self):
        drives = self.receipt["drives"]
        chart = self.text.split("#### Drive chart", 1)[1].split("#### Snap counts", 1)[0]
        self.assertEqual(chart.count("\n| ") - 2, len(drives))  # one header line per club
        snaps = self.text.split("#### Snap counts", 1)[1]
        for club in ("A", "B"):
            played = [p for p, line in self.receipt["team_stats"][club]["players"].items()
                      if any(line.get(f) for f in ("offensive_snaps", "defensive_snaps", "special_teams_snaps"))]
            section = snaps.split("**%s**" % club, 1)[1].split("**", 1)[0]
            self.assertEqual(section.count("(100%)") > 0, True)
            for pid in played:
                self.assertIn("| %s |" % pid, section)

    def test_line_score_matches_the_final(self):
        table = line_score_table(self.receipt)
        rows = [r for r in table.splitlines() if r.startswith("| A") or r.startswith("| B")]
        final = self.receipt["final_score"]
        for row in rows:
            cells = [c.strip() for c in row.strip("|").split("|")]
            self.assertEqual(sum(int(c) for c in cells[1:-1]), int(cells[-1]))
            self.assertEqual(int(cells[-1]), final[cells[0]])

    def test_render_box_score_dispatches_by_season(self):
        self.assertEqual(render_box_score.render(self.receipt, "A", 2014), self.text)
        legacy = render_box_score.render(self.receipt, "A", 2013)
        self.assertIn("#### Team comparison", legacy)
        self.assertNotIn("Scoring summary", legacy)


class LegacyBoxScoreTests(unittest.TestCase):
    """The 2013 outputs keep their filled blocks byte for byte."""

    def test_2013_week_one_block_matches_its_receipt(self):
        output = ROOT / "career/2013/regular_season/week_01_kansas_city_at_jacksonville/output.md"
        receipts = ROOT / "career/2013/stats/game_receipts"
        self.assertEqual(render_box_score.stale_blocks(output, receipts), [])
        match = render_box_score.BLOCK.search(output.read_text(encoding="utf-8"))
        receipt = render_box_score.load_receipt(match.group("event"), receipts)
        self.assertEqual(render_box_score.render(receipt, match.group("team")) + "\n", match.group("body"))
        self.assertTrue(match.group("body").startswith("#### Team comparison"))


class CoachRecordTests(unittest.TestCase):
    def test_2013_record_from_receipts(self):
        rows, show_postseason = render_coach_record.compute(2013, "Tennessee Titans")
        self.assertTrue(show_postseason)
        labels = [label for label, _ in rows]
        self.assertNotIn("This season", labels)  # first season with the team
        self.assertEqual(dict(rows)["With Jaguars"], ["10-6-0 (.625)", "1-1", "11-7-0 (.611)"])
        self.assertEqual(dict(rows)["NFL head coach, career"], ["10-6-0 (.625)", "1-1", "11-7-0 (.611)"])
        self.assertEqual(dict(rows)["Against Tennessee Titans"], ["1-1-0", "0-1", "1-2-0"])
        text = render_coach_record.render(2013)
        self.assertIn("| Record | Regular season | Postseason | Overall |", text)

    def test_2014_adds_this_season_row(self):
        rows, _ = render_coach_record.compute(2014)
        self.assertEqual([label for label, _ in rows][:2], ["This season", "With Jaguars"])

    def test_postseason_column_waits_for_a_postseason_game(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "career/2013/stats/game_receipts"
            folder.mkdir(parents=True)
            receipt = {"event_id": "x", "week": 1, "home": "Jacksonville Jaguars", "away": "Kansas City Chiefs",
                       "final_score": {"Jacksonville Jaguars": 20, "Kansas City Chiefs": 20}}
            (folder / "week_01.json").write_text(json.dumps(receipt), encoding="utf-8")
            text = render_coach_record.render(2013, "Chiefs", root)
            self.assertIn("| Record | Regular season | Overall |", text)
            self.assertNotIn("Postseason", text)
            self.assertIn("| With Jaguars | 0-0-1 (.500) | 0-0-1 (.500) |", text)
            self.assertIn("| Against Chiefs | 0-0-1 | 0-0-1 |", text)

    def test_career_start_is_the_recorded_hire_date(self):
        from runtime.events import load_events
        hire = load_events(ROOT)["2013-01-15-pre-hire-search-closure"]
        self.assertEqual(hire.owner, "career/2013/offseason/hiring_search.md")
        self.assertEqual(dt.date.fromisoformat(hire.data["date"]), render_coach_record.CAREER_START)
        self.assertEqual(render_coach_record.CAREER_START, dt.date(2013, 1, 15))
        self.assertEqual(render_coach_record.days_since_start(dt.date(2013, 1, 15)), 0)
        self.assertEqual(render_coach_record.days_since_start(dt.date(2014, 9, 7)), 600)


if __name__ == "__main__":
    unittest.main()
