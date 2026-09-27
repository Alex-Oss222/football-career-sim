import unittest

from runtime.standings import Season, compute, games_from_receipts


def game(week, away, home, away_points, home_points, away_td=0, home_td=0):
    return {
        "event_id": "%s-%s-%d" % (away, home, week), "week": week,
        "home": home, "away": away,
        "final_score": {home: home_points, away: away_points},
        "team_stats": {home: {"touchdowns": home_td}, away: {"touchdowns": away_td}},
    }


class DivisionTiebreakTests(unittest.TestCase):
    def test_head_to_head_separates_two_clubs(self):
        receipts = [
            game(1, "Indianapolis Colts", "Houston Texans", 10, 20),
            game(2, "Tennessee Titans", "Indianapolis Colts", 10, 20),
            game(2, "Houston Texans", "Jacksonville Jaguars", 10, 20),
        ]
        result = compute(receipts)
        self.assertEqual(result["division_ranks"]["AFC South"], [
            "Jacksonville Jaguars", "Houston Texans", "Indianapolis Colts", "Tennessee Titans"])
        note = next(n for n in result["notes"] if n["winner"] == "Houston Texans")
        self.assertEqual(note["step"], "head-to-head")

    def test_three_club_tie_restarts_two_club_procedure(self):
        receipts = [
            game(1, "Miami Dolphins", "Buffalo Bills", 10, 20, 1, 2),
            game(2, "New York Jets", "Miami Dolphins", 10, 20, 1, 2),
            game(3, "Buffalo Bills", "New York Jets", 10, 20, 1, 3),
        ]
        result = compute(receipts)
        self.assertEqual(result["division_ranks"]["AFC East"], [
            "New York Jets", "Buffalo Bills", "Miami Dolphins", "New England Patriots"])
        steps = {n["winner"]: n["step"] for n in result["notes"] if n["context"] == "AFC East"}
        self.assertEqual(steps["New York Jets"], "net touchdowns in all games")
        self.assertEqual(steps["Buffalo Bills"], "head-to-head")

    def test_tie_surviving_every_step_is_reported_not_tossed(self):
        receipts = [
            game(1, "Oakland Raiders", "Denver Broncos", 0, 10, 0, 1),
            game(1, "Kansas City Chiefs", "San Diego Chargers", 0, 10, 0, 1),
        ]
        result = compute(receipts)
        self.assertEqual(result["division_ranks"]["AFC West"][:2], ["Denver Broncos", "San Diego Chargers"])
        note = next(n for n in result["notes"]
                    if n["context"] == "AFC West" and n["winner"] == "Denver Broncos")
        self.assertIsNone(note["step"])


class SeedingTests(unittest.TestCase):
    def test_division_leaders_take_seeds_before_wild_cards(self):
        receipts = [
            game(1, "Oakland Raiders", "Denver Broncos", 0, 10, 0, 1),
            game(1, "Kansas City Chiefs", "San Diego Chargers", 0, 10, 0, 1),
            game(1, "Miami Dolphins", "Buffalo Bills", 3, 30, 0, 4),
        ]
        afc = compute(receipts)["conferences"]["AFC"]
        self.assertEqual(len(afc["division_winners"]), 4)
        self.assertIn("Buffalo Bills", afc["division_winners"][:2])
        self.assertIn("Denver Broncos", afc["division_winners"])
        self.assertEqual(afc["others"][0], "San Diego Chargers")

    def test_no_games_means_no_seeds(self):
        result = compute([])
        self.assertFalse(result["played"])
        self.assertEqual(result["conferences"]["NFC"]["division_winners"], [])


class MeasureTests(unittest.TestCase):
    def test_shared_ranking_places_count_as_held_alone(self):
        season = Season(games_from_receipts([]))
        ranks = season._rank(["A", "B", "C"], {"A": 30, "B": 30, "C": 20}.get, True)
        self.assertEqual(ranks, {"A": 1, "B": 1, "C": 3})

    def test_ties_count_half_and_streaks_follow_results(self):
        receipts = [
            game(1, "Chicago Bears", "Detroit Lions", 17, 17),
            game(2, "Detroit Lions", "Green Bay Packers", 24, 21),
            game(3, "Minnesota Vikings", "Detroit Lions", 10, 13),
        ]
        line = compute(receipts)["lines"]["Detroit Lions"]
        self.assertEqual(line.overall.text(), "2-0-1")
        self.assertAlmostEqual(line.overall.pct, 2.5 / 3)
        self.assertEqual(line.streak, "W2")
        self.assertEqual(line.home.text(), "1-0-1")

    def test_unknown_club_fails_closed(self):
        with self.assertRaises(ValueError):
            compute([game(1, "A", "B", 1, 0)])


if __name__ == "__main__":
    unittest.main()
