import unittest

from runtime.statbook import aggregate_receipts, leaders, make_receipt
from runtime.stat_tables import passer_rating
from scripts.render_season_stats import (
    all_players_markdown, coverage_line, leaders_markdown, league_markdown,
)


class StatbookTests(unittest.TestCase):
    def result(self, event_id="g1"):
        empty = {
            "position": "QB", "pass_attempts": 0, "passing_yards": 0,
            "rushing_attempts": 0, "rushing_yards": 0, "receptions": 0,
            "receiving_yards": 0, "sacks_allowed": 0, "sacks": 0,
            "pressures": 0, "interceptions": 0, "fumbles": 0,
            "field_goals_made": 0, "punts": 0, "return_yards": 0,
            "tackles": 0,
        }
        a = dict(empty)
        a.update(pass_attempts=30, passing_yards=250, interceptions=1, targets=7)
        b = dict(empty)
        b.update(position="RB", rushing_attempts=20, rushing_yards=100)
        bench = dict(empty)
        bench.update(position="WR")
        base = {
            "points": 20, "touchdowns": 2, "field_goals": 2, "punts": 4,
            "turnovers": 1, "sacks_allowed": 2, "penalties": 6,
            "penalty_yards": 45, "passing_yards": 250, "rushing_yards": 100,
            "first_downs": 20, "third_down_attempts": 12,
            "third_down_conversions": 5, "time_of_possession": 1800,
            "kick_returns": 2, "punt_returns": 1,
        }
        return {
            "terminated": True,
            "kernel_version": "test",
            "event_id": event_id,
            "final_score": {"A": 20, "B": 17},
            "team_stats": {
                "A": {**base, "players": {"qb-a": a, "rb-a": b, "bench-a": bench}},
                "B": {**base, "points": 17, "players": {"qb-b": a, "rb-b": b, "bench-b": bench}},
            },
            "play_ledger": [
                {"sequence":1,"offense":"A","play_type":"pass","concept":"Mesh"},
                {"sequence":2,"offense":"B","play_type":"run","concept":"Power"},
            ],
            "play_call_stats": {
                "A":{"Mesh":{"family":"Mesh","snaps":1,"dropbacks":1,"pass_attempts":1,"completions":1,"yards":12,"runs":0,"touchdowns":0,"turnovers":0,"sacks":0}},
                "B":{"Power":{"family":"Power","snaps":1,"runs":1,"dropbacks":0,"pass_attempts":0,"completions":0,"yards":5,"touchdowns":0,"turnovers":0,"sacks":0}},
            },
        }

    def test_receipt_and_aggregation(self):
        r1 = make_receipt(self.result("g1"), week=1, matchup="B at A")
        r2 = make_receipt(self.result("g2"), week=2, matchup="A at B")
        book = aggregate_receipts([r1, r2])
        self.assertEqual(book["through_week"], 2)
        self.assertEqual(book["teams"]["A"]["games"], 2)
        self.assertEqual(book["teams"]["A"]["team_stats"]["passing_yards"], 500)
        self.assertEqual(book["teams"]["A"]["players"]["qb-a"]["pass_attempts"], 60)
        self.assertEqual(book["plays_recorded"], 4)
        self.assertEqual(book["play_calls"]["A"]["Mesh"]["snaps"], 2)
        self.assertEqual(book["play_calls"]["A"]["Mesh"]["yards"], 24)
        self.assertIn("bench-a", book["teams"]["A"]["players"])
        self.assertIn("bench-a", book["players"])
        self.assertEqual(book["players"]["bench-a"]["receiving_yards"], 0)
        self.assertIn("targets", book["player_stat_fields"])
        self.assertEqual(book["players"]["qb-a"]["targets"], 14)
        self.assertEqual(leaders(book, "targets")[0]["value"], 14)
        self.assertEqual(leaders(book, "passing_yards")[0]["value"], 500)
        self.assertTrue(book["coverage_complete"])

    def test_compact_receipt_preserves_stats_without_snap_bloat(self):
        receipt = make_receipt(
            self.result("compact"), week=1, matchup="B at A",
            detail="compact_stats",
        )
        self.assertEqual(receipt["detail"], "compact_stats")
        self.assertNotIn("play_ledger", receipt)
        self.assertNotIn("play_call_stats", receipt)
        self.assertEqual(receipt["home"], "A")
        self.assertEqual(receipt["away"], "B")
        self.assertEqual(
            receipt["team_stats"]["A"]["players"]["bench-a"],
            {"position": "WR", "games": 1},
        )
        self.assertEqual(
            receipt["team_stats"]["A"]["players"]["qb-a"],
            {"position": "QB", "pass_attempts": 30,
             "passing_yards": 250, "interceptions": 1, "targets": 7, "games": 1},
        )
        book = aggregate_receipts([receipt])
        self.assertEqual(book["teams"]["A"]["team_stats"]["passing_yards"], 250)
        self.assertEqual(book["players"]["qb-a"]["passing_yards"], 250)
        self.assertEqual(book["players"]["bench-a"]["games"], 1)
        self.assertEqual(book["teams"]["A"]["opponent_stats"]["points"], 17)
        self.assertEqual(book["plays_recorded"], 0)
        self.assertTrue(book["coverage_complete"])

    def test_matchup_must_name_the_receipt_clubs(self):
        with self.assertRaises(ValueError):
            make_receipt(self.result("bad-matchup"), week=1, matchup="A vs B")

    def test_same_player_id_on_both_clubs_fails_closed(self):
        result = self.result("shared-id")
        players_b = result["team_stats"]["B"]["players"]
        players_b["qb-a"] = players_b.pop("qb-b")
        receipt = make_receipt(result, week=1, matchup="B at A", detail="compact_stats")
        with self.assertRaises(ValueError):
            aggregate_receipts([receipt])

    def test_unknown_receipt_detail_fails_closed(self):
        with self.assertRaises(ValueError):
            make_receipt(
                self.result("bad-detail"), week=1, matchup="B at A",
                detail="giant",
            )

    def test_player_attribution_completeness_is_team_scoped(self):
        receipt = make_receipt(
            self.result("attrib"), week=1, matchup="B at A",
            player_attribution_incomplete_teams=("B",),
        )
        book = aggregate_receipts([receipt])
        self.assertTrue(book["coverage_complete"])
        self.assertFalse(book["player_attribution_complete"])
        self.assertTrue(book["team_player_attribution_complete"]["A"])
        self.assertFalse(book["team_player_attribution_complete"]["B"])

    def test_partial_player_attribution_withholds_leaders_but_not_team_coverage(self):
        receipt=make_receipt(
            self.result("attrib-render"),week=1,matchup="B at A",
            player_attribution_incomplete_teams=("B",),
        )
        book=aggregate_receipts([receipt])
        self.assertIn("complete for this club's",coverage_line(book,"A"))
        self.assertIn("player attribution PARTIAL",coverage_line(book))
        rendered=leaders_markdown(2013,book)
        self.assertIn("rankings are withheld",rendered)
        self.assertNotIn("| Rank |",rendered)

    def test_partial_coverage_propagates(self):
        receipt = make_receipt(
            self.result("legacy"), week=1, matchup="B at A",
            coverage="legacy_partial",
        )
        self.assertFalse(aggregate_receipts([receipt])["coverage_complete"])

    def test_duplicate_receipts_fail_closed(self):
        receipt = make_receipt(self.result("same"), week=1, matchup="B at A")
        with self.assertRaises(ValueError):
            aggregate_receipts([receipt, receipt])

    def test_stat_views_are_position_first(self):
        players = {
            "QB One": {"position": "QB", "teams": ["AAA"], "games": 1, "completions": 20,
                       "pass_attempts": 30, "passing_yards": 250,
                       "passing_touchdowns": 2, "interceptions_thrown": 1},
            "CB One": {"position": "CB", "teams": ["BBB"], "games": 1, "tackles": 5,
                       "solo_tackles": 5, "defensive_interceptions": 1},
            "WR One": {"position": "WR", "teams": ["AAA"], "games": 1, "receptions": 3,
                       "targets": 4, "receiving_yards": 40, "tackles": 1},
        }
        teams = {
            "AAA": {"games": 1, "players": {k: players[k] for k in ("QB One", "WR One")}},
            "BBB": {"games": 1, "players": {"CB One": players["CB One"]}},
        }
        book = {"through_week": 1, "receipt_count": 1, "coverage_complete": True,
                "player_attribution_complete": True, "players": players, "teams": teams}

        league = league_markdown(2013, book)
        qb = league.split("## Quarterbacks")[1].split("## ")[0]
        db = league.split("## Defensive backs")[1].split("## ")[0]
        self.assertIn("| QB One | AAA | 1 | 20 | 30 | 66.7 | 250 |", qb)
        self.assertNotIn("CB One", qb)
        self.assertIn("| CB One | BBB | 1 | 5 | 5 |", db)
        self.assertLess(league.index("## Quarterbacks"), league.index("## Wide receivers"))
        self.assertIn("| WR One | AAA | WR | TOT 1 |", league)

        ledger = all_players_markdown(2013, book)
        aaa = ledger.split("## AAA")[1].split("## BBB")[0]
        self.assertIn("### Quarterbacks", aaa)
        self.assertIn("### Wide receivers", aaa)
        self.assertNotIn("CB One", aaa)
        self.assertNotIn("Nonzero stored statistics", ledger)

        leaders_text = leaders_markdown(2013, book)
        qb_leaders = leaders_text.split("## Quarterbacks")[1].split("## Running backs")[0]
        self.assertIn("| 1 | QB One | AAA | 250 |", qb_leaders)
        self.assertNotIn("CB One", qb_leaders)

    def test_weeks_one_to_three_receipts_still_aggregate_and_render(self):
        import json
        from pathlib import Path
        from runtime.statbook import STATBOOK_SCHEMA_VERSION
        from scripts.render_season_stats import render_views
        self.assertEqual(STATBOOK_SCHEMA_VERSION, 3)
        root = Path(__file__).resolve().parents[1] / "career/2013/stats/game_receipts"
        receipts = [json.loads(p.read_text()) for p in sorted(root.glob("*.json"))]
        legacy = [r for r in receipts if r.get("kernel_version") in ("2013.4", "2013.5")]
        self.assertTrue(legacy)
        self.assertTrue(all("drives" not in r for r in legacy))
        previous = [r for r in receipts if r.get("kernel_version") == "2013.6"]
        self.assertTrue(previous)
        self.assertTrue(all(len(row) == 14 for r in previous for row in r["drives"]))
        book = aggregate_receipts(legacy)
        team = next(iter(book["teams"].values()))
        self.assertNotIn("field_goal_attempts", team["team_stats"])
        views = render_views(2013, "Jacksonville Jaguars", receipts)
        self.assertIn("Legacy cohort", views["calibration_audit.md"])

    def test_new_receipts_carry_the_drives_summary(self):
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from synthetic_games import sample
        result = sample()[0]
        for detail in ("full", "compact_stats"):
            receipt = make_receipt(result, week=4, matchup="B at A", detail=detail)
            self.assertEqual(len(receipt["drives"]), len(result["possessions"]))
            self.assertEqual(receipt["schema_version"], 3)
            # Kernel 2013.7: 14 kernel 2013.6 fields plus 11 field-position
            # fields; kernel 2014.1 appends the timeout state and ladder level,
            # kernel 2014.4 the drive's own seconds, clock-expiry leg, passer and
            # the chain model; its phase 2 the adjusted punt transition, the
            # layout resample record and the field-goal probability.
            self.assertTrue(all(len(row) == 34 for row in receipt["drives"]))
        with self.assertRaises(ValueError):
            aggregate_receipts([{**make_receipt(result, week=4, matchup="B at A"), "schema_version": 4}])
        book = aggregate_receipts([make_receipt(result, week=4, matchup="B at A", detail="compact_stats")])
        self.assertEqual(book["teams"]["A"]["team_stats"]["drives"],
                         sum(1 for p in result["possessions"] if p["team"] == "A"))
        self.assertEqual(book["teams"]["A"]["drive_model_games"], 1)

    def test_kernel_2014_6_field_group_scaffold(self):
        # Kernel 2014.6 plumbing (B1): the field group and the per-club count
        # of 2014.6 games appear only once a 2014.6 receipt exists, so every
        # closed book and view is unchanged; the recorded base is copied.
        from runtime.statbook import KERNEL_2014_6_FROM, KERNEL_2014_6_TEAM_STAT_FIELDS
        from scripts.render_season_stats import compact_book_for_storage
        self.assertEqual(KERNEL_2014_6_FROM, (2014, 6))
        self.assertEqual(KERNEL_2014_6_TEAM_STAT_FIELDS, ())
        old = make_receipt(dict(self.result("old"), kernel_version="2014.5"), week=1, matchup="B at A")
        self.assertNotIn("calibration_base", old)
        book = aggregate_receipts([old])
        self.assertNotIn("kernel_2014_6_games", book["teams"]["A"])
        self.assertNotIn("kernel_2014_6_games", compact_book_for_storage(book)["teams"]["A"])
        recorded = {"name": "2010_2014w4", "manifest_sha256": "0" * 64, "cell_rules": "2014.6"}
        new = make_receipt(dict(self.result("new"), kernel_version="2014.6", calibration_base=recorded),
                           week=2, matchup="B at A")
        self.assertEqual(new["calibration_base"], recorded)
        book = aggregate_receipts([old, new])
        self.assertEqual(book["teams"]["A"]["kernel_2014_6_games"], 1)
        self.assertEqual(book["teams"]["A"]["games"], 2)
        self.assertEqual(compact_book_for_storage(book)["teams"]["B"]["kernel_2014_6_games"], 1)

    def test_passer_rating_matches_nfl_formula(self):
        line = {"completions": 20, "pass_attempts": 30, "passing_yards": 250,
                "passing_touchdowns": 2, "interceptions_thrown": 1}
        self.assertEqual(passer_rating(line), "100.7")
        perfect = {"completions": 10, "pass_attempts": 10, "passing_yards": 200,
                   "passing_touchdowns": 2, "interceptions_thrown": 0}
        self.assertEqual(passer_rating(perfect), "158.3")
        self.assertEqual(passer_rating({}), "—")


if __name__ == "__main__":
    unittest.main()
