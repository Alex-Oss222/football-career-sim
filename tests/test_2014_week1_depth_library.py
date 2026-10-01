"""The prepared 2014 Week 1 background depth-chart library.

Prepared research, gated until the master clock reaches Week 1 (September 7,
2014). These checks cover the file's shape and branch reconciliation, not
its authorization as game input.
"""
import json
import re
import unittest
from collections import Counter
from pathlib import Path

from runtime import depth_library
from runtime.league import TEAMS
from runtime.usage import MINIMUM_GAME_DAY, group
from scripts.check_week_input_exclusivity import controlled_players_from_roster, game_day_errors

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "library/data/2014_week1_depth_charts.json"
ROSTER = ROOT / 'career/2014/00_Team_Operations/Team/Roster/roster.md'
GROUPS = {"QB", "RB", "FB", "WR", "TE", "OL", "DL", "LB", "DB", "K", "P", "LS"}
DEPTH_REQUIRED = ("QB", "RB", "WR", "TE")


def unit(team):
    return depth_library.team_input(team, season=2014, offense_anchor=2.0,
                                    defense_anchor=2.0, special_teams_anchor=2.0)


class Week1DepthLibrary2014Tests(unittest.TestCase):
    library = json.loads(LIBRARY.read_text(encoding="utf-8"))

    def test_schema_and_gate(self):
        lib = self.library
        self.assertEqual((lib["schema_version"], lib["season"], lib["week"]), (1, 2014, 1))
        for key in ("branch_basis", "branch_controlled_players", "unplaced_branch_players",
                    "draft_swaps_without_week1_chart", "sources", "cross_check", "clubs", "gate"):
            self.assertIn(key, lib)
        self.assertIn("September 7, 2014", lib["gate"])
        self.assertEqual(lib["branch_control_unmatched"], [])
        for club in lib["clubs"].values():
            for key in ("code", "branch_changes", "notes", "players"):
                self.assertIn(key, club)
            for player in club["players"]:
                self.assertEqual(set(player) - {"name", "listed_position", "available", "injury_report",
                                                "return_week", "roles", "slots", "jersey", "gsis_id",
                                                "birth_date", "headshot_url", "headshot_license",
                                                "headshot_license_url", "headshot_credit",
                                                "headshot_page", "page_url"},
                                 {"player_id", "position", "depth"})

    def test_covers_every_background_club_and_not_jacksonville(self):
        self.assertEqual(set(self.library["clubs"]), set(TEAMS) - {"Jacksonville Jaguars"})
        self.assertNotIn("Jacksonville Jaguars", self.library["clubs"])
        self.assertEqual(len(self.library["clubs"]), 31)

    def test_every_position_maps_to_a_kernel_group(self):
        for team, club in self.library["clubs"].items():
            for player in club["players"]:
                with self.subTest(team=team, player=player["player_id"]):
                    self.assertIn(group(player["position"]), GROUPS)

    def test_depth_is_a_clean_sequence_within_each_group(self):
        for team, club in self.library["clubs"].items():
            by_group = {}
            for player in club["players"]:
                by_group.setdefault(group(player["position"]), []).append(player["depth"])
            for grp in DEPTH_REQUIRED:
                self.assertIn(grp, by_group, "%s has no %s" % (team, grp))
            for grp, depths in by_group.items():
                with self.subTest(team=team, group=grp):
                    self.assertEqual(sorted(depths), list(range(1, len(depths) + 1)))

    def test_every_club_is_a_legal_depth_ordered_game_day_unit(self):
        for team in self.library["clubs"]:
            with self.subTest(team=team):
                self.assertEqual(game_day_errors(team, unit(team)), [])
                counts = Counter(group(p["position"]) for p in unit(team)["roster"] if p["available"])
                for grp, need in MINIMUM_GAME_DAY.items():
                    self.assertGreaterEqual(counts[grp], need, "%s %s" % (team, grp))

    def test_no_branch_controlled_player_and_no_shared_player(self):
        controlled = controlled_players_from_roster(ROSTER)
        self.assertEqual(len(controlled), 78)
        self.assertEqual(set(self.library["branch_controlled_players"]), controlled)
        ids, gsis, club_of = Counter(), Counter(), {}
        for team, club in self.library["clubs"].items():
            for player in club["players"]:
                ids[player["player_id"]] += 1
                # A namesake of a controlled player (Minnesota's Mike Harris)
                # carries his club code in player_id and a different gsis id.
                self.assertNotIn(player["player_id"], controlled, "%s still on %s" % (player["player_id"], team))
                if player.get("name") in controlled:
                    self.assertRegex(player["player_id"], r" \([A-Z]{2,3}\)$")
                if player.get("gsis_id"):
                    gsis[player["gsis_id"]] += 1
                    club_of.setdefault(player["gsis_id"], team)
        self.assertEqual([i for i, n in ids.items() if n > 1], [])
        self.assertEqual([i for i, n in gsis.items() if n > 1], [])
        self.assertFalse(set(ids) & controlled)

    def test_branch_transactions_pairings_and_placements_are_applied(self):
        def ids(team):
            return {p.get("name", p["player_id"]) for p in self.library["clubs"][team]["players"]}
        # Draft pairing (career/2014/league/personnel/draft_pairing.md).
        self.assertIn("Blake Bortles", ids("St. Louis Rams"))
        self.assertNotIn("Aaron Donald", ids("St. Louis Rams"))
        self.assertIn("Marqise Lee", ids("Cleveland Browns"))
        self.assertNotIn("Joel Bitonio", ids("Cleveland Browns"))
        self.assertIn("Allen Robinson", ids("Green Bay Packers"))
        self.assertNotIn("Davante Adams", ids("Green Bay Packers"))
        self.assertIn("Brandon Linder", ids("Carolina Panthers"))
        self.assertNotIn("Trai Turner", ids("Carolina Panthers"))
        self.assertIn("Chris Smith", ids("Chicago Bears"))
        self.assertIn("Luke Bowanko", ids("New England Patriots"))
        self.assertIn("Storm Johnson", ids("New England Patriots"))
        self.assertNotIn("Malcolm Butler", ids("New England Patriots"))
        self.assertTrue(any("Aaron Colvin" in s for s in self.library["draft_swaps_without_week1_chart"]))
        # Branch trades.
        self.assertIn("Uche Nwaneri", ids("Arizona Cardinals"))
        self.assertIn("Jason Babin", ids("Miami Dolphins"))
        self.assertNotIn("Jason Babin", ids("New York Jets"))
        self.assertIn("Tyson Alualu", ids("Houston Texans"))
        self.assertIn("Cecil Shorts", ids("Indianapolis Colts"))
        self.assertIn("Justin Blackmon", ids("Indianapolis Colts"))
        self.assertIn("Will Rackley", ids("Seattle Seahawks"))
        blackmon = next(p for p in self.library["clubs"]["Indianapolis Colts"]["players"]
                        if p["player_id"] == "Justin Blackmon")
        self.assertTrue(blackmon.get("available", True))
        # Free agents Jacksonville won and lost; the carried 2013 placements.
        self.assertNotIn("Kirk Cousins", ids("Washington Redskins"))
        self.assertNotIn("Aqib Talib", ids("Denver Broncos"))
        self.assertNotIn("Alterraun Verner", ids("Tampa Bay Buccaneers"))
        self.assertIn("Golden Tate", ids("Detroit Lions"))
        self.assertIn("Julian Edelman", ids("New England Patriots"))
        self.assertIn("Brent Grimes", ids("Miami Dolphins"))
        self.assertIn("Luke Joeckel", ids("Philadelphia Eagles"))
        self.assertNotIn("Lane Johnson", ids("Philadelphia Eagles"))
        self.assertIn("Matt Barkley", ids("Oakland Raiders"))
        self.assertNotIn("Matt Barkley", ids("Philadelphia Eagles"))
        self.assertIn("Johnathan Cyprien", ids("Kansas City Chiefs"))
        self.assertIn("Denard Robinson", ids("Tennessee Titans"))
        self.assertIn("Josh Evans", ids("Washington Redskins"))
        # Retired and unplaced players are on no club.
        everyone = set().union(*(ids(t) for t in self.library["clubs"]))
        for name in ("Russell Allen", "Alan Ball", "Toby Gerhart", "Aaron Colvin", "Zane Beadles"):
            self.assertNotIn(name, everyone)
        self.assertTrue(any(s.startswith("Alan Ball") for s in self.library["unplaced_branch_players"]))

    def test_counts_and_availability(self):
        total = sum(len(c["players"]) for c in self.library["clubs"].values())
        self.assertEqual(total, 1588)
        for team, club in self.library["clubs"].items():
            self.assertGreaterEqual(len(club["players"]), 45, team)
        team_input = unit("New England Patriots")
        unavailable = {p["player_id"] for p in team_input["roster"] if not p["available"]}
        self.assertIn("Storm Johnson", unavailable)
        self.assertFalse(unavailable & set(team_input["active_players"]))
        self.assertLessEqual(len(team_input["active_players"]), 53)
        for team, club in self.library["clubs"].items():
            for player in club["players"]:
                if player.get("available") is False:
                    self.assertIn(player.get("injury_report"), {"Out", "Doubtful"})
                for field in ("birth_date",):
                    if field in player:
                        self.assertRegex(player[field], r"^\d{4}-\d{2}-\d{2}$")

    def test_record_carries_the_gate(self):
        record = (ROOT / "library/2014_week1_depth_charts.md").read_text(encoding="utf-8")
        self.assertRegex(record, re.compile(r"usable .*only when the master clock reaches Week 1", re.I | re.S))
        self.assertIn("September 7, 2014", record)


if __name__ == "__main__":
    unittest.main()
