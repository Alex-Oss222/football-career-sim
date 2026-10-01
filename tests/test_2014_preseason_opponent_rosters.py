"""The prepared 2014 preseason opponent library (Tampa Bay, August 8, 2014).

Prepared research, gated for the August 8, 2014 preseason game and after.
These checks cover the file's shape, its branch reconciliation and the weekly
TeamInput exclusivity gate on a synthetic one-game package; they do not
authorize a game.
"""
import json
import re
import unittest
from collections import Counter
from pathlib import Path

from runtime.usage import MINIMUM_GAME_DAY, group
from runtime.week_inputs import game_day_actives
from scripts.check_week_input_exclusivity import (
    check_inputs, controlled_players_from_roster, game_day_errors,
)

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "library/data/2014_preseason_opponent_rosters.json"
RECORD = ROOT / "library/2014_preseason_opponent_rosters.md"
ROSTER = ROOT / "career/2014/team/roster/roster.md"
TEAM = "Tampa Bay Buccaneers"
UNIT = {"QB": "offense", "RB": "offense", "FB": "offense", "WR": "offense", "TE": "offense",
        "OL": "offense", "DL": "defense", "LB": "defense", "DB": "defense",
        "K": "special teams", "P": "special teams", "LS": "special teams"}


def team_input(team, players):
    roster = [{"player_id": p["player_id"], "position": p["position"],
               "available": p.get("available", True), "unit": UNIT[group(p["position"])],
               "roles": tuple(p.get("roles", ())), "depth": p["depth"]} for p in players]
    return {"team_id": team, "active_players": [p["player_id"] for p in roster if p["available"]],
            "offense_anchor": 2.0, "defense_anchor": 2.0, "special_teams_anchor": 2.0,
            "roster": roster}


def jacksonville_players():
    """A scratch Jacksonville input from the branch roster table (gate check only)."""
    players, counts = [], Counter()
    for line in ROSTER.read_text(encoding="utf-8").split("## Current controlled players", 1)[1].splitlines():
        m = re.match(r"^\| ([^|]+?) \| ([A-Z]+) \| \d{4}-\d{2}-\d{2} \| \d+ \|", line)
        if m and group(m.group(2)):
            grp = group(m.group(2))
            counts[grp] += 1
            players.append({"player_id": m.group(1).strip(), "position": m.group(2), "depth": counts[grp]})
    return players


class PreseasonOpponentLibrary2014Tests(unittest.TestCase):
    library = json.loads(LIBRARY.read_text(encoding="utf-8"))
    club = library["clubs"][TEAM]

    def test_schema_and_gate(self):
        lib = self.library
        self.assertEqual((lib["schema_version"], lib["season"], lib["game"], lib["as_of"]),
                         (1, 2014, "preseason-01", "2014-08-08"))
        for key in ("gate", "branch_basis", "sources", "clubs", "removed_by_club", "cross_check"):
            self.assertIn(key, lib)
        self.assertTrue(lib["gate"].startswith("gated: usable for the August 8, 2014 preseason game and after"))
        self.assertEqual(list(lib["clubs"]), [TEAM])
        self.assertEqual(self.club["code"], "TB")
        for player in self.club["players"]:
            self.assertEqual(set(player) - {"name", "listed_position", "available", "injury_report",
                                            "availability_note", "return_week", "roles", "slots",
                                            "jersey", "gsis_id", "birth_date", "headshot_url",
                                            "headshot_license", "headshot_license_url",
                                            "headshot_credit", "headshot_page", "page_url"},
                             {"player_id", "position", "depth"})
            self.assertIn(group(player["position"]), UNIT)

    def test_camp_roster_size(self):
        self.assertGreaterEqual(len(self.club["players"]), 85)
        self.assertLessEqual(len(self.club["players"]), 90)

    def test_depth_is_a_clean_sequence_with_one_starting_quarterback(self):
        by_group = {}
        for player in self.club["players"]:
            by_group.setdefault(group(player["position"]), []).append(player)
        for grp, members in by_group.items():
            with self.subTest(group=grp):
                self.assertEqual(sorted(p["depth"] for p in members), list(range(1, len(members) + 1)))
        quarterbacks = sorted(by_group["QB"], key=lambda p: p["depth"])
        self.assertEqual([p["player_id"] for p in quarterbacks if p["depth"] == 1], ["Josh McCown"])
        self.assertEqual([p["player_id"] for p in quarterbacks],
                         ["Josh McCown", "Mike Glennon", "Mike Kafka", "Alex Tanney"])

    def test_offensive_line_slots_are_ordered_as_the_chart_listed_them(self):
        line = sorted((p for p in self.club["players"] if group(p["position"]) == "OL"), key=lambda p: p["depth"])
        self.assertEqual([p["slots"].split(",")[0] for p in line[:5]], ["LT1", "LG1", "C1", "RG1", "RT1"])
        self.assertEqual([p["player_id"] for p in line[:5]],
                         ["Anthony Collins", "Oniel Cousins", "Evan Dietrich-Smith", "Jamon Meredith", "Demar Dotson"])
        self.assertEqual([p["slots"].split(",")[0] for p in line[5:10]], ["LT2", "LG2", "C2", "RG2", "RT2"])
        self.assertEqual(len(line), 14)

    def test_starters_as_the_chart_listed_them(self):
        first = {p["player_id"] for p in self.club["players"] if any(s.endswith("1") and not s.endswith("11") for s in p.get("slots", "").split(","))}
        for name in ("Josh McCown", "Doug Martin", "Jorvorskie Lane", "Vincent Jackson", "Chris Owusu",
                     "Brandon Myers", "Adrian Clayborn", "Gerald McCoy", "Clinton McDonald", "Michael Johnson",
                     "Jonathan Casillas", "Mason Foster", "Lavonte David", "Mike Jenkins", "Leonard Johnson",
                     "Mark Barron", "Dashon Goldson", "Connor Barth", "Michael Koenen", "Andrew DePaola", "Eric Page"):
            self.assertIn(name, first)
        self.assertNotIn("Alterraun Verner", first)

    def test_no_jacksonville_controlled_player_and_no_duplicate(self):
        controlled = controlled_players_from_roster(ROSTER)
        self.assertEqual(len(controlled), self.library["branch_controlled_count"])
        registry = json.loads((ROOT / "library/data/player_birth_dates.json").read_text(encoding="utf-8"))["players"]
        controlled_gsis = {registry[n]["gsis_id"] for n in controlled if n in registry and registry[n].get("gsis_id")}
        ids, gsis = Counter(), Counter()
        for player in self.club["players"]:
            ids[player["player_id"]] += 1
            self.assertNotIn(player["player_id"], controlled)
            if player.get("gsis_id"):
                gsis[player["gsis_id"]] += 1
                self.assertNotIn(player["gsis_id"], controlled_gsis, player["player_id"])
        self.assertEqual([i for i, n in ids.items() if n > 1], [])
        self.assertEqual([i for i, n in gsis.items() if n > 1], [])
        self.assertEqual(set(self.library["removed_by_club"][TEAM]),
                         {"Alterraun Verner", "Cameron Brate", "Jeremy Cain"})
        self.assertTrue(any(c.startswith("Removed Alterraun Verner") for c in self.club["branch_changes"]))
        self.assertTrue(any(c.startswith("Removed Cameron Brate") for c in self.club["branch_changes"]))
        self.assertTrue(any(c.startswith("Removed Jeremy Cain") for c in self.club["branch_changes"]))
        self.assertNotIn("Brandon Dixon", ids)      # joined Tampa Bay September 6
        self.assertNotIn("Logan Mankins", ids)      # acquired August 26
        self.assertNotIn("Carl Nicks", ids)         # released July 30

    def test_held_out_players_from_pregame_reports(self):
        out = {p["player_id"]: p for p in self.club["players"] if p.get("available") is False}
        self.assertEqual(set(out), {"Mike Jenkins", "Dashon Goldson"})
        for player in out.values():
            self.assertEqual(player["injury_report"], "Out")
            self.assertIn("August 8", player["availability_note"])

    def test_legal_game_day_unit_and_exclusivity_gate(self):
        tampa = team_input(TEAM, self.club["players"])
        self.assertEqual(game_day_errors(TEAM, tampa), [])
        counts = Counter(group(p["position"]) for p in tampa["roster"] if p["available"])
        for grp, need in MINIMUM_GAME_DAY.items():
            self.assertGreaterEqual(counts[grp], need, grp)
        tampa["active_players"] = game_day_actives(tampa["roster"])
        jacksonville = team_input("Jacksonville Jaguars", jacksonville_players())
        jacksonville["active_players"] = game_day_actives(jacksonville["roster"])
        package = {"games": [{"away": TEAM, "home": "Jacksonville Jaguars",
                              "away_input": tampa, "home_input": jacksonville}]}
        controlled = controlled_players_from_roster(ROSTER)
        self.assertEqual(check_inputs(package, controlled, expected_games=1), [])
        # The gate still rejects a controlled player placed on Tampa Bay.
        bad = json.loads(json.dumps(package))
        bad["games"][0]["away_input"]["roster"].append({"player_id": "Alterraun Verner", "position": "CB",
                                                         "available": True, "unit": "defense", "roles": (), "depth": 17})
        self.assertTrue(any("Alterraun Verner" in e for e in check_inputs(bad, controlled, expected_games=1)))

    def test_record_carries_the_gate_and_the_reconciliations(self):
        text = RECORD.read_text(encoding="utf-8")
        self.assertIn("gated: usable for the August 8, 2014 preseason game and after", text)
        for name in ("Alterraun Verner", "Cameron Brate", "Jeremy Cain", "Mike Jenkins", "Dashon Goldson"):
            self.assertIn(name, text)


if __name__ == "__main__":
    unittest.main()
