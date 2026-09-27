import unittest
from collections import Counter

from runtime import depth_library
from runtime.league import TEAMS
from runtime.usage import group
from scripts.check_week_input_exclusivity import game_day_errors


def unit(team):
    return depth_library.team_input(team, offense_anchor=2.0, defense_anchor=2.0, special_teams_anchor=2.0)


class DepthLibraryTests(unittest.TestCase):
    library = depth_library.load()

    def test_covers_every_background_club(self):
        self.assertEqual(set(depth_library.clubs()), set(TEAMS) - {"Jacksonville Jaguars"})

    def test_every_club_is_a_legal_depth_ordered_game_day_unit(self):
        for team in depth_library.clubs():
            with self.subTest(team=team):
                self.assertEqual(game_day_errors(team, unit(team)), [])

    def test_depth_is_a_clean_sequence_within_each_group(self):
        for team, club in self.library["clubs"].items():
            by_group = {}
            for player in club["players"]:
                by_group.setdefault(group(player["position"]), []).append(player["depth"])
            for grp, depths in by_group.items():
                with self.subTest(team=team, group=grp):
                    self.assertEqual(sorted(depths), list(range(1, len(depths) + 1)))

    def test_no_branch_controlled_player_and_no_shared_id(self):
        controlled = set(self.library["branch_controlled_players"])
        ids = Counter(p["player_id"] for club in self.library["clubs"].values() for p in club["players"])
        self.assertFalse(controlled & set(ids))
        self.assertEqual([i for i, n in ids.items() if n > 1], [])

    def test_branch_transactions_and_draft_swaps_are_applied(self):
        def ids(team):
            return {p["player_id"] for p in self.library["clubs"][team]["players"]}
        self.assertIn("Blaine Gabbert", ids("Green Bay Packers"))
        self.assertNotIn("Kirk Cousins", ids("Washington Redskins"))
        self.assertIn("Luke Joeckel", ids("Philadelphia Eagles"))
        self.assertNotIn("Lane Johnson", ids("Philadelphia Eagles"))
        self.assertIn("Matt Barkley", ids("Oakland Raiders"))
        self.assertNotIn("Matt Barkley", ids("Philadelphia Eagles"))

    def test_starting_quarterback_follows_the_depth_slot(self):
        oakland = [p for p in self.library["clubs"]["Oakland Raiders"]["players"]
                   if group(p["position"]) == "QB" and p["depth"] == 1]
        self.assertEqual(oakland[0]["player_id"], "Terrelle Pryor")

    def test_unavailable_players_are_not_active(self):
        team_input = unit("Atlanta Falcons")
        unavailable = {p["player_id"] for p in team_input["roster"] if not p["available"]}
        self.assertFalse(unavailable & set(team_input["active_players"]))


if __name__ == "__main__":
    unittest.main()
