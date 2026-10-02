"""Kernel 2014.3 credit rules: the on-field line, coverage tackles, long snaps.

Credit only: these rules read the club's own depth order and roles and never
touch the possession stream. ResultIdentityTests pins that: synthetic games
must reproduce the result digests recorded under kernel 2014.2
(tests/data/result_identity.json); the 1,090-game replay is in runtime/README.md.
"""
import copy
import hashlib
import json
from pathlib import Path
import unittest

from runtime.kernel import resolve_game, validate_result

from runtime import usage
from runtime.player_evidence import PlayerInput
from support_rosters import game_day_roster
from synthetic_games import sample, sample_teams


def player(pid, position, depth, **kw):
    return PlayerInput(pid, position, depth=depth, **kw)


class ProtectionFrontTests(unittest.TestCase):
    def test_front_is_five_by_position_and_depth(self):
        front = usage.protection_front(game_day_roster("A"))
        self.assertEqual({s: p.player_id for s, p in front.items()}, {
            "LT": "A-OT1", "LG": "A-OG1", "C": "A-C1", "RG": "A-OG2", "RT": "A-OT2"})

    def test_unit_wide_depth_order_like_the_library(self):
        line = [player("lt", "T", 1), player("lg", "G", 2), player("c", "C", 3), player("rg", "G", 4),
                player("rt", "T", 5), player("t6", "T", 6), player("g7", "G", 7)]
        front = usage.protection_front(line)
        self.assertEqual([front[s].player_id for s in usage.LINE_SLOTS], ["lt", "lg", "c", "rg", "rt"])

    def test_missing_center_takes_next_lineman_by_depth(self):
        line = [player("lt", "T", 1), player("lg", "G", 2), player("rg", "G", 4),
                player("rt", "T", 5), player("g6", "G", 6), player("t7", "T", 7)]
        front = usage.protection_front(line)
        self.assertEqual(front["C"].player_id, "g6")
        self.assertEqual(len(front), 5)

    def seats(self, line):
        return [usage.protection_front(line)[s].player_id for s in usage.LINE_SLOTS]

    def test_unit_wide_chart_seats_by_depth_whatever_the_label(self):
        # Chicago's shape: a guard-labelled left tackle; Denver's: a guard at RT.
        chicago = [player("lt", "G", 1), player("lg", "G", 2), player("c", "C", 3), player("rg", "G", 4),
                   player("rt", "T", 5), player("t6", "T", 6)]
        self.assertEqual(self.seats(chicago), ["lt", "lg", "c", "rg", "rt"])
        denver = [player("lt", "T", 1), player("lg", "G", 2), player("c", "C", 3), player("rg", "G", 4),
                  player("rt", "G", 5), player("t6", "T", 6)]
        self.assertEqual(self.seats(denver), ["lt", "lg", "c", "rg", "rt"])
        # Washington's shape: a center-labelled left guard.
        washington = [player("lt", "T", 1), player("lg", "C", 2), player("c", "C", 3), player("rg", "G", 4),
                      player("rt", "T", 5), player("g7", "G", 7)]
        self.assertEqual(self.seats(washington), ["lt", "lg", "c", "rg", "rt"])

    def test_vacant_slot_prefers_a_fitting_label(self):
        # Depth 3 (the center) is inactive: a later center fills C before an earlier tackle.
        line = [player("lt", "T", 1), player("lg", "G", 2), player("rg", "G", 4), player("rt", "T", 5),
                player("t6", "T", 6), player("c7", "C", 7)]
        self.assertEqual(self.seats(line), ["lt", "lg", "c7", "rg", "rt"])

    def test_edge_and_interior_rushers(self):
        front = usage.protection_front(game_day_roster("A"))
        self.assertEqual(usage.beaten_slots(player("x", "DE", 1), front), ["LT", "RT"])
        self.assertEqual(usage.beaten_slots(player("x", "OLB", 1), front), ["LT", "RT"])
        self.assertEqual(usage.beaten_slots(player("x", "CB", 1), front), ["LT", "RT"])
        self.assertEqual(usage.beaten_slots(player("x", "DT", 1), front), ["LG", "C", "RG"])
        self.assertEqual(usage.beaten_slots(player("x", "ILB", 1), front), ["LG", "C", "RG"])
        self.assertEqual(usage.beaten_slots(player("x", "LB", 1), front), list(usage.LINE_SLOTS))


class KickingGameRuleTests(unittest.TestCase):
    def test_coverage_unit_skips_base_starters(self):
        roster = game_day_roster("A")
        unit = usage.coverage_unit(roster, "kickoff_coverage")
        ids = {p.player_id for p in unit}
        self.assertEqual(len(unit), 10)
        for starter in ("A-ILB1", "A-OLB1", "A-ILB2", "A-OLB2", "A-CB1", "A-S1", "A-WR1", "A-WR3",
                        "A-TE1", "A-RB1"):
            self.assertNotIn(starter, ids)
        self.assertNotIn(usage.club_returner(roster, "kick_return").player_id, ids)
        self.assertEqual(len(usage.coverage_unit(roster, "punt_coverage")), 9)

    def test_designated_coverage_players_come_first_then_the_rule_fills(self):
        roster = list(game_day_roster("A"))
        roster[0] = PlayerInput("A-QB1", "QB", depth=1, roles=("punt_coverage",))
        unit = [p.player_id for p in usage.coverage_unit(roster, "punt_coverage")]
        self.assertEqual(unit[0], "A-QB1")
        self.assertEqual(len(unit), 9)

    def test_club_returner_is_one_player(self):
        roster = game_day_roster("A")
        self.assertEqual(usage.club_returner(roster, "kick_return").player_id, "A-WR4")
        roster = list(roster) + [PlayerInput("A-KR", "CB", depth=9, roles=("kick_return",))]
        self.assertEqual(usage.club_returner(roster, "kick_return").player_id, "A-KR")

    def test_long_snapper_falls_back_to_center(self):
        line = [player("lt", "T", 1), player("lg", "G", 2), player("c", "C", 3),
                player("rg", "G", 4), player("rt", "T", 5)]
        front = usage.protection_front(line)
        self.assertEqual(usage.long_snapper(line, front).player_id, "c")
        self.assertEqual(usage.long_snapper(line + [player("ls", "LS", 1)], front).player_id, "ls")


class SampleCreditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.games = sample()

    def test_sacks_charged_to_the_front_facing_the_rusher(self):
        checked = 0
        for game in self.games:
            by_team = game["team_stats"]
            for row in game["play_ledger"]:
                if not row.get("sack"):
                    continue
                offense, defense = row["offense"], row["defense"]
                blocker = by_team[offense]["players"][row["blocker"]]
                # Kernel 2014.4: a game starter, or a lineman who entered after
                # a removal; either way he was on the field for that drive.
                self.assertTrue(blocker["line_starts"] == 1 or blocker["offensive_snaps"] > 0)
                self.assertGreater(blocker["offensive_snaps"], 0)
                rusher = by_team[defense]["players"][row["tackler"]]["position"]
                edge = rusher in usage.EDGE_RUSHERS
                self.assertIn(row["blocker_slot"], usage.EDGE_SLOTS if edge else usage.INTERIOR_SLOTS)
                checked += 1
        self.assertGreater(checked, 500)

    def test_coverage_tackles_only_on_returns(self):
        checked = 0
        for game in self.games:
            for row in game["play_ledger"]:
                if row.get("play_type") in ("kickoff", "free_kick", "punt"):
                    self.assertEqual(bool(row.get("cover_player")), row.get("outcome") == "returned")
                    if row.get("cover_player"):
                        checked += 1
                        self.assertNotIn(row["cover_player"], (row.get("kicker"), row.get("punter")))
                        line = game["team_stats"][row["offense"]]["players"][row["cover_player"]]
                        self.assertGreaterEqual(line["special_teams_tackles"], 1)
        self.assertGreater(checked, 500)

    def test_one_returner_per_club_per_game(self):
        # Kernel 2014.4: one club returner at a time. He changes only after a
        # removal from his club since the previous return: the returner
        # himself, or a starter whose place the returner then took (the
        # returner rule skips base starters).
        for game in self.games:
            removals = [(i["team"], i["drive"]) for i in game["injuries"] if i["removed"]]
            for kind in ("kickoff", "punt"):
                last = {}
                for row in game["play_ledger"]:
                    if not row.get("returner") or (row["play_type"] == "punt") != (kind == "punt"):
                        continue
                    team = row["defense"]
                    previous = last.get(team)
                    if previous is not None and previous[0] != row["returner"]:
                        self.assertTrue(any(t == team and previous[1] <= d < row["drive"] for t, d in removals))
                    last[team] = (row["returner"], row["drive"])

    def test_line_starts_and_long_snaps(self):
        for game in self.games:
            for team, stats in game["team_stats"].items():
                players = stats["players"]
                self.assertEqual(sum(p["line_starts"] for p in players.values()), 5)
                snaps = stats["punts"] + stats["field_goal_attempts"] + stats["extra_point_attempts"]
                self.assertEqual(players[f"{team}-LS1"]["long_snaps"], snaps)



class NegativeCheckTests(unittest.TestCase):
    """Each kernel 2014.3 credit check fires on a doctored result."""

    @classmethod
    def setUpClass(cls):
        cls.game = next(g for g in sample() if any(r.get("sack") for r in g["play_ledger"]))

    def doctored(self, change):
        game = copy.deepcopy(self.game)
        change(game)
        return validate_result(game)

    def test_line_starts(self):
        def change(game):
            players = game["team_stats"]["A"]["players"]
            players["A-OT3"]["line_starts"] += 1
        self.assertIn("line start count mismatch", self.doctored(change))

    def test_sack_off_the_field(self):
        def change(game):
            row = next(r for r in game["play_ledger"] if r.get("sack"))
            players = game["team_stats"][row["offense"]]["players"]
            players[row["blocker"]]["sacks_allowed"] -= 1
            players[row["offense"] + "-OT3"]["sacks_allowed"] += 1
        self.assertIn("sack charged to a lineman off the field", self.doctored(change))

    def test_coverage_tackles(self):
        def change(game):
            game["team_stats"]["A"]["players"]["A-WR1"]["special_teams_tackles"] += 1
        self.assertIn("coverage tackle count mismatch", self.doctored(change))

        def untackled(game):
            row = next(r for r in game["play_ledger"] if r.get("cover_player"))
            game["team_stats"][row["offense"]]["players"][row["cover_player"]]["special_teams_tackles"] -= 1
            row["cover_player"] = None
        self.assertIn("returned kick without a coverage tackler", self.doctored(untackled))

        def moved(game):
            row = next(r for r in game["play_ledger"] if r.get("cover_player"))
            players = game["team_stats"][row["offense"]]["players"]
            players[row["cover_player"]]["special_teams_tackles"] -= 1
            spare = next(p for p in players if p != row["cover_player"] and p.endswith("S4"))
            players[spare]["special_teams_tackles"] += 1
        self.assertIn("coverage tackle credit differs from the ledger", self.doctored(moved))

    def test_long_snaps(self):
        def change(game):
            game["team_stats"]["A"]["players"]["A-LS1"]["long_snaps"] += 1
        self.assertIn("long snap count mismatch", self.doctored(change))


class ViewTests(unittest.TestCase):
    """The 2014.3 counters render where present (2013 views stay unchanged:
    validate_repository.py checks them byte for byte)."""

    def test_season_view_and_box_score(self):
        from runtime.stat_tables import position_sections
        from scripts.render_box_score import team_box
        game = sample()[0]
        players = {p: dict(line, teams=["A"]) for p, line in game["team_stats"]["A"]["players"].items()}
        text = "\n".join(position_sections(players, with_team=True))
        self.assertIn("STARTS", text)
        self.assertIn("LONG SNAPS", text)
        if any(line["special_teams_tackles"] for line in players.values()):
            self.assertIn("Kick and punt coverage", text)
        box = "\n".join(team_box("A", game["team_stats"]["A"]["players"]))
        self.assertIn("##### Offensive line", box)
        self.assertIn("##### Long snapping", box)


class ResultIdentityTests(unittest.TestCase):
    """A credit-only or display-only change must not move a result: the
    digests recorded in tests/data/result_identity.json reproduce. The file
    was re-recorded for the kernel 2014.4 candidate (synthetic legacy-path
    fixtures; items 2, 4 and 5 and the E1 home term change results by
    design), as its note says. Closed 2013 receipts are never rerun.

    Kernel 2014.6 build (batch B1): the games resolve explicitly under
    PROFILE_2014_5, so these digests stay the isolation proof of every 2014.6
    mechanism until and after the release flips KERNEL_VERSION."""

    def test_results_match_the_recorded_digests(self):
        from runtime.profiles import PROFILE_2014_5
        fixture = json.loads((Path(__file__).parent / "data/result_identity.json").read_text())
        a, b = sample_teams()
        for row in fixture["games"]:
            game_type, i = row["game_type"], row["index"]
            seed = hashlib.sha256(("identity-%s-%d" % (game_type, i)).encode()).digest()
            r = resolve_game(a, b, seed=seed, event_id="identity-%s-%d" % (game_type, i),
                             venue="neutral" if i % 5 == 0 else "home", game_type=game_type,
                             _test_profile=PROFILE_2014_5)
            out = {k: r[k] for k in ("final_score", "possessions", "kickoffs", "injuries", "opening_receiver")}
            out["team"] = {t: {k: v for k, v in s.items() if k != "players"} for t, s in r["team_stats"].items()}
            digest = hashlib.sha256(json.dumps(out, sort_keys=True, default=str).encode()).hexdigest()
            self.assertEqual(digest, row["digest"], "%s game %d" % (game_type, i))


if __name__ == "__main__":
    unittest.main()
