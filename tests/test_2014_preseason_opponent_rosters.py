"""The prepared 2014 preseason opponent library (Tampa Bay, August 8, 2014;
Chicago, August 14, 2014; Detroit, August 22, 2014).

Prepared research, gated per club for its preseason game and after. These
checks cover the file's shape, each club's branch reconciliation and the
weekly TeamInput exclusivity gate on a synthetic one-game package; they do not
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
ROSTER = ROOT / "career/2014/00_Team_Operations/Team/Roster/roster.md"
REGISTRY = ROOT / "library/data/player_birth_dates.json"
TAMPA = "Tampa Bay Buccaneers"
CHICAGO = "Chicago Bears"
DETROIT = "Detroit Lions"
JACKSONVILLE = "Jacksonville Jaguars"
UNIT = {"QB": "offense", "RB": "offense", "FB": "offense", "WR": "offense", "TE": "offense",
        "OL": "offense", "DL": "defense", "LB": "defense", "DB": "defense",
        "K": "special teams", "P": "special teams", "LS": "special teams"}
PLAYER_FIELDS = {"player_id", "position", "depth"}
OPTIONAL_FIELDS = {"name", "listed_position", "available", "injury_report", "availability_note",
                   "return_week", "roles", "slots", "jersey", "gsis_id", "birth_date", "headshot_url",
                   "headshot_license", "headshot_license_url", "headshot_credit", "headshot_page",
                   "page_url"}
CLUB_FIELDS = {"code", "game", "as_of", "gate", "sources", "cross_check", "branch_changes", "notes", "players"}


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


def first_string(club):
    return {p["player_id"] for p in club["players"]
            if any(re.fullmatch(r"[A-Z]+1", s) for s in p.get("slots", "").split(","))}


class PreseasonOpponentLibrary2014Tests(unittest.TestCase):
    library = json.loads(LIBRARY.read_text(encoding="utf-8"))
    tampa = library["clubs"][TAMPA]
    chicago = library["clubs"][CHICAGO]
    detroit = library["clubs"][DETROIT]
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))["players"]

    # Shape ----------------------------------------------------------------

    def test_schema_and_gates(self):
        lib = self.library
        self.assertEqual((lib["schema_version"], lib["season"]), (2, 2014))
        for key in ("games", "branch_basis", "branch_controlled_count", "clubs", "removed_by_club"):
            self.assertIn(key, lib)
        self.assertEqual(list(lib["clubs"]), [TAMPA, CHICAGO, DETROIT])
        self.assertEqual(lib["games"], {"preseason-01": TAMPA, "preseason-02": CHICAGO, "preseason-03": DETROIT})
        self.assertEqual((self.tampa["code"], self.tampa["game"], self.tampa["as_of"]), ("TB", "preseason-01", "2014-08-08"))
        self.assertEqual((self.chicago["code"], self.chicago["game"], self.chicago["as_of"]), ("CHI", "preseason-02", "2014-08-14"))
        self.assertTrue(self.tampa["gate"].startswith("gated: usable for the August 8, 2014 preseason game and after"))
        self.assertTrue(self.chicago["gate"].startswith("gated: usable for the August 14, 2014 preseason game and after"))
        self.assertEqual((self.detroit["code"], self.detroit["game"], self.detroit["as_of"]), ("DET", "preseason-03", "2014-08-22"))
        self.assertTrue(self.detroit["gate"].startswith("gated: usable for the August 22, 2014 preseason game and after"))
        self.assertIn("transactions_july_24_to_august_25", self.detroit)
        self.assertIn("transactions_july_21_to_august_9", self.tampa)
        self.assertIn("transactions_july_25_to_august_18", self.chicago)
        for club in (self.tampa, self.chicago, self.detroit):
            self.assertTrue(CLUB_FIELDS <= set(club))
            for player in club["players"]:
                self.assertEqual(set(player) - OPTIONAL_FIELDS, PLAYER_FIELDS)
                self.assertIn(group(player["position"]), UNIT)

    def test_camp_roster_sizes(self):
        self.assertEqual(len(self.tampa["players"]), 87)
        self.assertEqual(len(self.chicago["players"]), 89)
        self.assertEqual(len(self.detroit["players"]), 85)

    def test_depth_is_a_clean_sequence_in_every_group(self):
        for team, club in ((TAMPA, self.tampa), (CHICAGO, self.chicago), (DETROIT, self.detroit)):
            by_group = {}
            for player in club["players"]:
                by_group.setdefault(group(player["position"]), []).append(player)
            for grp, members in by_group.items():
                with self.subTest(club=team, group=grp):
                    self.assertEqual(sorted(p["depth"] for p in members), list(range(1, len(members) + 1)))

    def test_every_player_id_resolves_in_the_birth_date_registry_or_is_named_unverified(self):
        unverified = {TAMPA: {"Euclid Cummings", "Jibreel Black", "Ryne Giddins", "Damaso Munoz", "Mark Joyce"},
                      CHICAGO: {"Jordan Lynch", "Lee Pegues", "Derricus Purdy", "Marcus Trice", "Brandon Hartson", "Chad Rempel"},
                      DETROIT: {"James Franklin", "Chad Abram", "Alex Bullard", "A.J. Dalton", "Greg Hickman", "Kris Redding", "Shamari Benton"}}
        for team, club in ((TAMPA, self.tampa), (CHICAGO, self.chicago), (DETROIT, self.detroit)):
            for player in club["players"]:
                with self.subTest(club=team, player=player["player_id"]):
                    row = self.registry.get(player["player_id"])
                    if player["player_id"] in unverified[team]:
                        self.assertIsNone(row)
                        self.assertNotIn("birth_date", player)
                    else:
                        self.assertIsNotNone(row)
                        self.assertEqual(row["gsis_id"], player["gsis_id"])
                        self.assertEqual(row["birth_date"], player["birth_date"])

    # Tampa Bay, August 8 ----------------------------------------------------

    def test_tampa_quarterbacks_as_the_chart_listed_them(self):
        quarterbacks = sorted((p for p in self.tampa["players"] if p["position"] == "QB"), key=lambda p: p["depth"])
        self.assertEqual([p["player_id"] for p in quarterbacks],
                         ["Josh McCown", "Mike Glennon", "Mike Kafka", "Alex Tanney"])

    def test_tampa_offensive_line_slots_are_ordered_as_the_chart_listed_them(self):
        line = sorted((p for p in self.tampa["players"] if group(p["position"]) == "OL"), key=lambda p: p["depth"])
        self.assertEqual([p["slots"].split(",")[0] for p in line[:5]], ["LT1", "LG1", "C1", "RG1", "RT1"])
        self.assertEqual([p["player_id"] for p in line[:5]],
                         ["Anthony Collins", "Oniel Cousins", "Evan Dietrich-Smith", "Jamon Meredith", "Demar Dotson"])
        self.assertEqual([p["slots"].split(",")[0] for p in line[5:10]], ["LT2", "LG2", "C2", "RG2", "RT2"])
        self.assertEqual(len(line), 14)

    def test_tampa_starters_as_the_chart_listed_them(self):
        first = first_string(self.tampa)
        for name in ("Josh McCown", "Doug Martin", "Jorvorskie Lane", "Vincent Jackson", "Chris Owusu",
                     "Brandon Myers", "Adrian Clayborn", "Gerald McCoy", "Clinton McDonald", "Michael Johnson",
                     "Jonathan Casillas", "Mason Foster", "Lavonte David", "Mike Jenkins", "Leonard Johnson",
                     "Mark Barron", "Dashon Goldson", "Connor Barth", "Michael Koenen", "Andrew DePaola", "Eric Page"):
            self.assertIn(name, first)
        self.assertNotIn("Alterraun Verner", first)

    def test_tampa_branch_reconciliation(self):
        ids = {p["player_id"] for p in self.tampa["players"]}
        self.assertEqual(set(self.library["removed_by_club"][TAMPA]),
                         {"Alterraun Verner", "Cameron Brate", "Jeremy Cain"})
        for name in ("Alterraun Verner", "Cameron Brate", "Jeremy Cain"):
            self.assertTrue(any(c.startswith("Removed " + name) for c in self.tampa["branch_changes"]))
        self.assertNotIn("Brandon Dixon", ids)      # joined Tampa Bay September 6
        self.assertNotIn("Logan Mankins", ids)      # acquired August 26
        self.assertNotIn("Carl Nicks", ids)         # released July 30

    def test_tampa_held_out_players_from_pregame_reports(self):
        out = {p["player_id"]: p for p in self.tampa["players"] if p.get("available") is False}
        self.assertEqual(set(out), {"Mike Jenkins", "Dashon Goldson"})
        for player in out.values():
            self.assertEqual(player["injury_report"], "Out")
            self.assertIn("August 8", player["availability_note"])

    # Chicago, August 14 -------------------------------------------------------

    def test_chicago_quarterbacks_as_the_chart_listed_them(self):
        quarterbacks = sorted((p for p in self.chicago["players"] if p["position"] == "QB"), key=lambda p: p["depth"])
        self.assertEqual([p["player_id"] for p in quarterbacks],
                         ["Jay Cutler", "Jordan Palmer", "Jimmy Clausen", "David Fales"])

    def test_chicago_offensive_line_slots_with_leno_removed(self):
        line = sorted((p for p in self.chicago["players"] if group(p["position"]) == "OL"), key=lambda p: p["depth"])
        self.assertEqual([p["slots"].split(",")[0] for p in line[:5]], ["LT1", "LG1", "C1", "RG1", "RT1"])
        self.assertEqual([p["player_id"] for p in line[:5]],
                         ["Jermon Bushrod", "Matt Slauson", "Roberto Garza", "Kyle Long", "Jordan Mills"])
        # Leno (LT2) is Jacksonville's; the second string is the four remaining
        # cells and Dennis Roland is the next man up at left tackle.
        self.assertEqual([p["slots"].split(",")[0] for p in line[5:9]], ["LG2", "C2", "RG2", "RT2"])
        self.assertEqual(line[9]["player_id"], "Dennis Roland")
        self.assertEqual(line[9]["slots"], "LT3")
        self.assertEqual(line[-1]["player_id"], "Rob Turner")   # signed August 10, no chart cell
        self.assertNotIn("slots", line[-1])
        self.assertEqual(len(line), 15)

    def test_chicago_starters_as_the_chart_listed_them(self):
        first = first_string(self.chicago)
        for name in ("Jay Cutler", "Matt Forte", "Tony Fiammetta", "Brandon Marshall", "Alshon Jeffery",
                     "Martellus Bennett", "Lamarr Houston", "Jeremiah Ratliff", "Stephen Paea", "Jared Allen",
                     "Shea McClellin", "D.J. Williams", "Lance Briggs", "Tim Jennings", "Charles Tillman",
                     "Ryan Mundy", "Brock Vereen", "Robbie Gould", "Pat O'Donnell", "Brandon Hartson", "Eric Weems"):
            self.assertIn(name, first)
        self.assertNotIn("Jon Bostic", first)          # co-listed second at MLB
        self.assertNotIn("Charles Leno Jr.", first)

    def test_chicago_branch_reconciliation_including_the_chris_smith_pairing(self):
        ids = {p["player_id"]: p for p in self.chicago["players"]}
        self.assertEqual(set(self.library["removed_by_club"][CHICAGO]), {"Charles Leno Jr.", "Christian Jones"})
        self.assertTrue(any(c.startswith("Removed Charles Leno Jr. (T): drafted by Jacksonville, No. 168") for c in self.chicago["branch_changes"]))
        self.assertTrue(any(c.startswith("Removed Christian Jones (OLB): undrafted signing by Jacksonville") for c in self.chicago["branch_changes"]))
        self.assertTrue(any(c.startswith("Added Chris Smith (DE) below every listed DL: branch draft pairing") for c in self.chicago["branch_changes"]))
        smith = ids["Chris Smith"]
        self.assertEqual((smith["position"], smith["gsis_id"]), ("DE", "00-0031264"))
        self.assertNotIn("slots", smith)
        self.assertNotIn("jersey", smith)
        line = [p for p in self.chicago["players"] if group(p["position"]) == "DL"]
        self.assertEqual(smith["depth"], len(line))
        senn = ids["Jordan Senn"]
        self.assertEqual(senn["slots"], "SLB3")
        self.assertEqual([p["player_id"] for p in sorted((p for p in self.chicago["players"] if group(p["position"]) == "LB"), key=lambda p: p["depth"])][:5],
                         ["Shea McClellin", "D.J. Williams", "Lance Briggs", "Jon Bostic", "Khaseem Greene"])
        for name in ("Jeremy Cain", "Kofi Hughes", "Santonio Holmes", "Darius Reynaud", "Peyton Thompson",
                     "Conor O'Neill", "Graham Pocic", "Terrance Mitchell", "Roy Philon", "Patrick Mannelly",
                     "Domenik Hixon", "Israel Idonije", "Terrence Toliver"):
            self.assertNotIn(name, ids)
        for name in ("Eric Weems", "Zach Miller (CHI)", "Chad Rempel", "Tress Way", "Greg Herd", "Rob Turner"):
            self.assertIn(name, ids)

    def test_chicago_namesakes_carry_reviewed_identities(self):
        ids = {p["player_id"]: p for p in self.chicago["players"]}
        self.assertEqual(ids["Chris Williams (CHI)"]["gsis_id"], "00-0026691")
        self.assertEqual(ids["C.J. Wilson (CHI)"]["gsis_id"], "00-0030141")
        self.assertEqual(ids["Zach Miller (CHI)"]["gsis_id"], "00-0027125")
        self.assertEqual(ids["Jeremiah Ratliff"]["gsis_id"], "00-0023656")
        self.assertEqual(ids["Brandon Marshall"]["gsis_id"], "00-0024334")
        self.assertEqual(ids["D.J. Williams"]["gsis_id"], "00-0022780")
        self.assertNotIn("Chris Williams", ids)
        self.assertNotIn("Zach Miller", ids)

    def test_chicago_held_out_players_from_the_game_day_list(self):
        out = {p["player_id"]: p for p in self.chicago["players"] if p.get("available") is False}
        self.assertEqual(set(out), {"Marquess Wilson", "Craig Steltz", "Isaiah Frey", "Chris Conte", "Eben Britton",
                                    "Brian de la Puente", "Jordan Mills", "Chris Williams (CHI)", "Dante Rosario",
                                    "Willie Young"})
        for player in out.values():
            self.assertEqual(player["injury_report"], "Out")
            self.assertIn("August 14", player["availability_note"])
        available = {p["player_id"] for p in self.chicago["players"] if p.get("available", True)}
        for name in ("Martellus Bennett", "Jared Allen", "Kyle Long", "Tim Jennings", "Kyle Fuller", "Charles Tillman"):
            self.assertIn(name, available)

    def test_chicago_returner_roles(self):
        weems = next(p for p in self.chicago["players"] if p["player_id"] == "Eric Weems")
        self.assertEqual(weems["roles"], ["kick_return", "punt_return"])
        self.assertEqual([p["player_id"] for p in self.chicago["players"] if "placekicker" in p.get("roles", ())], ["Robbie Gould"])
        self.assertEqual({p["player_id"] for p in self.chicago["players"] if "punt" in p.get("roles", ())}, {"Pat O'Donnell", "Tress Way"})

    # Detroit, August 22 -------------------------------------------------------

    def test_detroit_quarterbacks_as_the_chart_listed_them(self):
        quarterbacks = sorted((p for p in self.detroit["players"] if p["position"] == "QB"), key=lambda p: p["depth"])
        self.assertEqual([p["player_id"] for p in quarterbacks],
                         ["Matthew Stafford", "Dan Orlovsky", "Kellen Moore", "James Franklin"])

    def test_detroit_offensive_line_slots_with_lucas_removed(self):
        line = sorted((p for p in self.detroit["players"] if group(p["position"]) == "OL"), key=lambda p: p["depth"])
        self.assertEqual([p["slots"].split(",")[0] for p in line[:5]], ["LT1", "LG1", "C1", "RG1", "RT1"])
        self.assertEqual([p["player_id"] for p in line[:5]],
                         ["Riley Reiff", "Rob Sims", "Dominic Raiola", "Larry Warford", "LaAdrian Waddle"])
        # Lucas (LT2) is Jacksonville's; the second string is the four remaining
        # cells and Michael Williams is the next man up at left tackle.
        self.assertEqual([p["slots"].split(",")[0] for p in line[5:9]], ["LG2", "C2", "RG2", "RT2"])
        self.assertEqual((line[9]["player_id"], line[9]["slots"], line[9]["gsis_id"]), ("Michael Williams", "LT3", "00-0030110"))
        self.assertEqual(len(line), 14)

    def test_detroit_starters_as_the_chart_listed_them(self):
        first = first_string(self.detroit)
        for name in ("Matthew Stafford", "Reggie Bush", "Calvin Johnson", "Golden Tate", "Brandon Pettigrew",
                     "Ezekiel Ansah", "Nick Fairley", "Ndamukong Suh", "Jason Jones", "Ashlee Palmer",
                     "Stephen Tulloch", "DeAndre Levy", "Rashean Mathis", "Darius Slay", "James Ihedigbo",
                     "Glover Quin", "Nate Freese", "Sam Martin", "Don Muhlbach", "Jeremy Ross"):
            self.assertIn(name, first)
        self.assertNotIn("Montell Owens", first)       # FB1 is Jacksonville's
        fullbacks = sorted((p for p in self.detroit["players"] if p["position"] == "FB"), key=lambda p: p["depth"])
        self.assertEqual([(p["player_id"], p["slots"]) for p in fullbacks], [("Jed Collins", "FB2"), ("Chad Abram", "FB3")])

    def test_detroit_branch_reconciliation(self):
        ids = {p["player_id"]: p for p in self.detroit["players"]}
        self.assertEqual(set(self.library["removed_by_club"][DETROIT]),
                         {"Cornelius Lucas", "Montell Owens", "C.J. Mosley", "Julian Stanford"})
        self.assertTrue(any(c.startswith("Removed Cornelius Lucas (T): undrafted signing by Jacksonville") for c in self.detroit["branch_changes"]))
        for name in ("Montell Owens (FB)", "C.J. Mosley (DT)", "Julian Stanford (OLB)"):
            self.assertTrue(any(c.startswith("Removed %s: under Jacksonville control in the branch" % name) for c in self.detroit["branch_changes"]))
        tackles = [p for p in sorted(self.detroit["players"], key=lambda p: p["depth"]) if p["position"] == "DT"]
        self.assertEqual([(p["player_id"], p["slots"]) for p in tackles][:4],
                         [("Nick Fairley", "DT1"), ("Ndamukong Suh", "DT1"), ("Andre Fluellen", "DT2"), ("Caraun Reid", "DT3")])
        self.assertEqual(ids["Jimmy Saddler-McQueen"]["slots"], "DT3")
        for name in ("Golden Tate", "Nate Ness", "Conner Vernon", "Shamari Benton", "Steven Miller", "Kris Redding",
                     "T.J. Jones", "Drew Butler", "Giorgio Tavecchio", "DeJon Gomes", "Jimmy Saddler-McQueen"):
            self.assertIn(name, ids)
        for name in ("Quintin Payton", "Cory Greenwood", "Justin Jackson", "Drayton Florence", "Jon Baldwin",
                     "Reese Wiggins", "Kalonji Kashama", "Josh Bynes", "Michael Egnew", "Emil Igwenagu",
                     "Alex Henery", "Matt Prater", "John Wendling", "Shaun Hill"):
            self.assertNotIn(name, ids)
        for name in ("Nate Ness", "Conner Vernon", "Shamari Benton"):
            self.assertNotIn("slots", ids[name])
        linebackers = [p for p in self.detroit["players"] if group(p["position"]) == "LB"]
        self.assertEqual(ids["Shamari Benton"]["depth"], len(linebackers))

    def test_detroit_namesakes_carry_reviewed_identities(self):
        ids = {p["player_id"]: p for p in self.detroit["players"]}
        self.assertEqual(ids["Larry Webster"]["gsis_id"], "00-0031065")
        self.assertEqual(ids["Corey Fuller"]["gsis_id"], "00-0030095")
        self.assertEqual(ids["Giorgio Tavecchio"]["gsis_id"], "00-0028907")
        self.assertEqual(ids["Dwight Bentley"]["gsis_id"], "00-0029265")
        self.assertEqual(ids["Ezekiel Ansah"]["gsis_id"], "00-0030059")
        self.assertEqual(ids["Jason Jones"]["gsis_id"], "00-0026194")
        self.assertNotIn("Bill Bentley", ids)
        self.assertNotIn("Ziggy Ansah", ids)

    def test_detroit_held_out_players_from_the_game_day_list_and_dated_reports(self):
        out = {p["player_id"]: p for p in self.detroit["players"] if p.get("available") is False}
        self.assertEqual(set(out), {"James Ihedigbo", "Kyle Van Noy", "T.J. Jones", "DeJon Gomes"})
        for player in out.values():
            self.assertEqual(player["injury_report"], "Out")
        for name in ("James Ihedigbo", "Kyle Van Noy", "T.J. Jones"):
            self.assertIn("August 22", out[name]["availability_note"])
        self.assertIn("August 21", out["DeJon Gomes"]["availability_note"])
        available = {p["player_id"] for p in self.detroit["players"] if p.get("available", True)}
        for name in ("Calvin Johnson", "Ezekiel Ansah", "Matthew Stafford", "Reggie Bush", "Ndamukong Suh"):
            self.assertIn(name, available)

    def test_detroit_returner_roles(self):
        ross = next(p for p in self.detroit["players"] if p["player_id"] == "Jeremy Ross")
        self.assertEqual(ross["roles"], ["kick_return", "punt_return"])
        self.assertEqual({p["player_id"] for p in self.detroit["players"] if "placekicker" in p.get("roles", ())}, {"Nate Freese", "Giorgio Tavecchio"})
        self.assertEqual({p["player_id"] for p in self.detroit["players"] if "punt" in p.get("roles", ())}, {"Sam Martin", "Drew Butler"})

    # Gates --------------------------------------------------------------------

    def test_no_jacksonville_controlled_player_and_no_duplicate(self):
        controlled = controlled_players_from_roster(ROSTER)
        self.assertEqual(len(controlled), self.library["branch_controlled_count"])
        controlled_gsis = {self.registry[n]["gsis_id"] for n in controlled if n in self.registry and self.registry[n].get("gsis_id")}
        for team, club in ((TAMPA, self.tampa), (CHICAGO, self.chicago), (DETROIT, self.detroit)):
            ids, gsis = Counter(), Counter()
            for player in club["players"]:
                ids[player["player_id"]] += 1
                self.assertNotIn(player["player_id"], controlled, team)
                if player.get("gsis_id"):
                    gsis[player["gsis_id"]] += 1
                    self.assertNotIn(player["gsis_id"], controlled_gsis, player["player_id"])
            self.assertEqual([i for i, n in ids.items() if n > 1], [])
            self.assertEqual([i for i, n in gsis.items() if n > 1], [])

    def test_legal_game_day_units_and_exclusivity_gates(self):
        controlled = controlled_players_from_roster(ROSTER)
        jacksonville = team_input(JACKSONVILLE, jacksonville_players())
        jacksonville["active_players"] = game_day_actives(jacksonville["roster"])
        for team, club, home in ((TAMPA, self.tampa, False), (CHICAGO, self.chicago, True), (DETROIT, self.detroit, True)):
            with self.subTest(club=team):
                opponent = team_input(team, club["players"])
                self.assertEqual(game_day_errors(team, opponent), [])
                counts = Counter(group(p["position"]) for p in opponent["roster"] if p["available"])
                for grp, need in MINIMUM_GAME_DAY.items():
                    self.assertGreaterEqual(counts[grp], need, grp)
                opponent["active_players"] = game_day_actives(opponent["roster"])
                game = ({"away": JACKSONVILLE, "home": team, "away_input": jacksonville, "home_input": opponent} if home
                        else {"away": team, "home": JACKSONVILLE, "away_input": opponent, "home_input": jacksonville})
                package = {"games": [game]}
                self.assertEqual(check_inputs(package, controlled, expected_games=1), [])
                # The gate still rejects a controlled player placed on the opponent.
                bad = json.loads(json.dumps(package))
                side = "home_input" if home else "away_input"
                bad["games"][0][side]["roster"].append({"player_id": "Charles Leno Jr.", "position": "OT",
                                                        "available": True, "unit": "offense", "roles": (), "depth": 16})
                self.assertTrue(any("Charles Leno Jr." in e for e in check_inputs(bad, controlled, expected_games=1)))

    def test_record_carries_the_gates_and_the_reconciliations(self):
        text = RECORD.read_text(encoding="utf-8")
        self.assertIn("gated: usable for the August 8, 2014 preseason game and after", text)
        self.assertIn("gated: usable for the August 14, 2014 preseason game and after", text)
        self.assertIn("gated: usable for the August 22, 2014 preseason game and after", text)
        for name in ("Alterraun Verner", "Cameron Brate", "Jeremy Cain", "Mike Jenkins", "Dashon Goldson",
                     "Charles Leno Jr.", "Christian Jones", "Chris Smith", "Willie Young", "Marquess Wilson",
                     "Jordan Lynch", "Lee Pegues", "Derricus Purdy", "Marcus Trice", "Brandon Hartson", "Chad Rempel",
                     "Cornelius Lucas", "Montell Owens", "C.J. Mosley", "Julian Stanford", "James Ihedigbo", "Kyle Van Noy",
                     "T.J. Jones", "DeJon Gomes", "James Franklin", "Chad Abram", "Alex Bullard", "A.J. Dalton",
                     "Greg Hickman", "Kris Redding", "Shamari Benton"):
            self.assertIn(name, text)


if __name__ == "__main__":
    unittest.main()
