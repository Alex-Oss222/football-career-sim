import json
import tempfile
import unittest
from pathlib import Path

from runtime.player_evidence import STAT_FIELDS
from runtime.statbook import make_receipt
from scripts.render_box_score import fill, render, stale_blocks


def line(position, **counters):
    return {"position": position, **{field: 0 for field in STAT_FIELDS}, **counters}


def club(prefix, points):
    return {
        "points": points, "touchdowns": 2, "field_goals": 1, "punts": 3, "turnovers": 1,
        "sacks_allowed": 2, "penalties": 5, "penalty_yards": 40, "passing_yards": 230,
        "rushing_yards": 101, "first_downs": 19, "third_down_attempts": 13,
        "third_down_conversions": 5, "time_of_possession": 1830, "kick_returns": 2, "punt_returns": 1,
        "players": {
            prefix + " QB": line("QB", dropbacks=34, pass_attempts=32, completions=21, passing_yards=230,
                                 passing_touchdowns=2, interceptions_thrown=1, interceptions=1,
                                 sacks_taken=2, sack_yards=11, rushing_attempts=2, rushing_yards=6),
            prefix + " RB": line("RB", rushing_attempts=22, rushing_yards=95, rushing_touchdowns=1, long_rush=18),
            prefix + " LB": line("LB", tackles=9, solo_tackles=6, assisted_tackles=3),
            prefix + " OT": line("OT"),
        },
    }


def receipt():
    home, away = "Jacksonville Jaguars", "Kansas City Chiefs"
    result = {"terminated": True, "kernel_version": "t", "event_id": "box-test",
              "final_score": {home: 24, away: 17},
              "team_stats": {home: club("JAX", 24), away: club("KC", 17)}}
    return make_receipt(result, week=1, matchup="%s at %s" % (away, home), detail="compact_stats")


class BoxScoreTests(unittest.TestCase):
    def test_lead_team_first_with_category_tables_and_totals(self):
        text = render(receipt(), "Jacksonville Jaguars")
        self.assertIn("| Statistic | Jacksonville Jaguars | Kansas City Chiefs |", text)
        self.assertIn("| Third down | 5/13 (38.5%) | 5/13 (38.5%) |", text)
        self.assertIn("| Time of possession | 30:30 | 30:30 |", text)
        self.assertLess(text.index("#### Jacksonville Jaguars"), text.index("#### Kansas City Chiefs"))
        self.assertIn("| JAX QB | 21/32 | 230 | 7.2 | 2 | 1 | 2-11 | 94.5 |", text)
        self.assertIn("| **Team total** | 24 | 101 | 4.2 | 1 | 18 |", text)
        self.assertNotIn("Red zone", text)
        self.assertNotIn("JAX OT", text)

    def test_marked_block_is_filled_and_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "box-test.json").write_text(json.dumps(receipt()), encoding="utf-8")
            output = directory / "output.md"
            marker = "<!-- box-score event=box-test team=Jacksonville Jaguars -->\n<!-- /box-score -->"
            output.write_text("### Box score\n\n" + marker + "\n", encoding="utf-8")
            self.assertEqual(stale_blocks(output, directory), ["box-test"])
            output.write_text(fill(output.read_text(encoding="utf-8"), directory), encoding="utf-8")
            self.assertEqual(stale_blocks(output, directory), [])
            self.assertIn("##### Passing", output.read_text(encoding="utf-8"))
            output.write_text(output.read_text(encoding="utf-8").replace("| 230 |", "| 231 |", 1), encoding="utf-8")
            self.assertEqual(stale_blocks(output, directory), ["box-test"])

    def test_kernel_2013_7_receipt_adds_a_drive_chart(self):
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from synthetic_games import sample
        result = sample()[1]
        text = render(make_receipt(result, week=6, matchup="B at A", detail="full"), "A")
        chart = text.split("#### Drive chart", 1)[1]
        self.assertEqual(chart.count("\n| ") - 1, len(result["possessions"]))
        punts = [p for p in result["possessions"] if p["category"] == "punt"]
        if punts:
            fd = punts[0]["fourth_down"]
            self.assertIn("(4th & %d at " % fd["ydstogo"] if fd["down"] == 4 else "& %d at " % fd["ydstogo"], chart)
        self.assertNotIn("Drive chart", render(receipt(), "Jacksonville Jaguars"))


if __name__ == "__main__":
    unittest.main()
