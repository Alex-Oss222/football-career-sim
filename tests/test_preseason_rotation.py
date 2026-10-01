"""Preseason unit rotation (runtime/rotation.py) through the kernel.

Synthetic rosters and seeds only. Blocks apply in order, a snap ceiling ends
a block at the next possession boundary, a removed starter's slot promotes
within the block, the E2 pause still fires for a removed quarterback inside
a block, the documented default rotates a club with no plan, swapping the
controlled club changes nothing, a plan fails closed, and no regular-season
or postseason result reads the module (tests/data/result_identity.json pins
the digests in tests/test_attribution.py).
"""
import hashlib
import json
import sys
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import game_runner, rotation
from runtime.kernel import TeamInput, resolve_game, validate_result
from runtime.rules import PRESEASON
from support_rosters import game_day_roster
from synthetic_games import TEAM_A_SHEET

SEED = hashlib.sha256(b"preseason-rotation-synthetic").digest()
DATE = "2014-08-08"


def club(prefix, plan=(), third_quarterback=True):
    roster = tuple(game_day_roster(prefix))
    if third_quarterback:
        roster += (replace(roster[1], player_id=prefix + "-QB3", depth=3),)
    return TeamInput(prefix, tuple(p.player_id for p in roster), roster=roster,
                     offensive_call_sheet=TEAM_A_SHEET if prefix == "A" else (), rotation_plan=tuple(plan))


def block(side, unit, until=None, **players):
    return {"side": side, "unit": unit, "until": until, "players": players}


PLAN = (
    block("offense", "first offense", {"possessions": 2},
          QB=["A-QB1"], WR=["A-WR2", "A-WR1", "A-WR3"], OL=["A-OT1", "A-OG1", "A-C1", "A-OG2", "A-OT2"]),
    block("offense", "second offense", {"possessions": 2}, QB=["A-QB2"], WR=["A-WR4", "A-WR5"]),
    block("offense", "reserves", None, QB=["A-QB3"]),
    block("defense", "first defense", {"possessions": 2}, DL=["A-DE2", "A-DT1", "A-DE1", "A-DT2"]),
    block("defense", "second defense", None, DL=["A-DE3", "A-DT3", "A-DE4"]),
)


def play(a, b, event="pre-rotation", **kwargs):
    return resolve_game(a, b, seed=SEED, event_id=event, game_type=PRESEASON, game_date=DATE, **kwargs)


def applied(result, team, side="offense"):
    return result["rotation"][team]["applied"][side]


def snaps_by_drive(result, team):
    out = {}
    for row in result["play_ledger"]:
        if row.get("offense") == team and row.get("play_type") in ("pass", "run"):
            out[row["drive"]] = out.get(row["drive"], 0) + 1
    return out


class BlockOrderTests(unittest.TestCase):
    def test_blocks_apply_in_order_and_name_the_passer(self):
        a, b = club("A", PLAN), club("B")
        result = play(a, b)
        self.assertEqual(validate_result(result), [])
        offense = applied(result, "A")
        self.assertEqual([e["block"] for e in offense[:4]], [0, 0, 1, 1])
        self.assertTrue(all(e["block"] == 2 for e in offense[4:]))
        self.assertEqual(offense[0]["unit"], "first offense")
        self.assertEqual(offense[0]["lineup"]["WR"], ["A-WR2", "A-WR1", "A-WR3"])
        self.assertEqual(offense[0]["lineup"]["OL"], ["A-OT1", "A-OG1", "A-C1", "A-OG2", "A-OT2"])
        self.assertEqual(offense[2]["lineup"]["WR"][:2], ["A-WR4", "A-WR5"])  # the rest follow by depth
        self.assertEqual(offense[2]["lineup"]["WR"][2], "A-WR1")
        self.assertEqual(offense[4]["lineup"]["QB"], ["A-QB3"])
        passer = {p["number"]: p["passer"] for p in result["possessions"] if p["team"] == "A"}
        for entry in offense:
            self.assertEqual(passer[entry["possession"]], entry["lineup"]["QB"][0])
        defense = applied(result, "A", "defense")
        self.assertEqual([e["block"] for e in defense[:3]], [0, 0, 1])
        self.assertEqual(defense[0]["lineup"]["DL"], ["A-DE2", "A-DT1", "A-DE1", "A-DT2"])
        self.assertEqual(defense[2]["lineup"]["DL"][:3], ["A-DE3", "A-DT3", "A-DE4"])
        # Snap counts follow the rotation: every quarterback threw, none took every snap.
        lines = result["team_stats"]["A"]["players"]
        total = sum(e["snaps"] for e in [{"snaps": n} for n in snaps_by_drive(result, "A").values()])
        for qb in ("A-QB1", "A-QB2", "A-QB3"):
            self.assertGreater(lines[qb]["offensive_snaps"], 0)
            self.assertLess(lines[qb]["offensive_snaps"], total)
        self.assertEqual(result["rotation"]["A"]["basis"], {"offense": "plan", "defense": "plan",
                                                            "special_teams": "depth_order"})
        self.assertEqual(result["rotation"]["B"]["basis"]["offense"], "default")

    def test_snap_ceiling_ends_the_block_at_the_next_boundary(self):
        plan = (block("offense", "first", {"snaps": 9, "possessions": 6}, QB=["A-QB1"]),
                block("offense", "rest", None, QB=["A-QB2"]))
        result = play(club("A", plan), club("B"))
        self.assertEqual(validate_result(result), [])
        offense = applied(result, "A")
        snaps = snaps_by_drive(result, "A")
        first = [e["possession"] for e in offense if e["block"] == 0]
        self.assertTrue(first)
        self.assertLess(len(first), 6)
        before_last = sum(snaps.get(n, 0) for n in first[:-1])
        self.assertLess(before_last, 9)                      # the ceiling had not been reached
        self.assertGreaterEqual(sum(snaps.get(n, 0) for n in first), 9)  # it was reached in the last one
        self.assertTrue(all(e["block"] == 1 for e in offense[len(first):]))
        self.assertEqual(result["rotation"]["A"]["blocks"]["offense"][0]["until"], {"snaps": 9, "possessions": 6})

    def test_special_teams_block_names_the_kicking_unit(self):
        plan = (block("special_teams", "first kick unit", {"possessions": 2}, K=["A-K1"], LS=["A-LS1"]),
                block("special_teams", "second kick unit", None, LB=["A-OLB3", "A-ILB3"]))
        result = play(club("A", plan), club("B"))
        self.assertEqual(validate_result(result), [])
        kicks = applied(result, "A", "special_teams")
        self.assertTrue(kicks)
        self.assertEqual(kicks[0]["unit"], "first kick unit")
        self.assertIn("kick", kicks[0])
        self.assertEqual(result["rotation"]["A"]["basis"]["special_teams"], "plan")


class RemovalTests(unittest.TestCase):
    def test_injured_starter_promotes_within_the_block(self):
        plan = (block("offense", "first", {"possessions": 5}, WR=["A-WR1", "A-WR2", "A-WR3"]),
                block("offense", "rest", None, WR=["A-WR4"]))
        a, b = club("A", plan), club("B")
        base = play(a, b)
        first = applied(base, "A")[0]["possession"]
        onsets = {(first, "A-WR2"): {"injury_class": "lower_extremity", "severity": "multi_week", "removed": True}}
        result = play(a, b, _test_onsets=onsets)
        self.assertEqual(validate_result(result), [])
        offense = applied(result, "A")
        self.assertEqual(offense[0]["lineup"]["WR"], ["A-WR1", "A-WR2", "A-WR3"])
        later = [e for e in offense if e["block"] == 0 and e["possession"] > first]
        self.assertTrue(later)
        for entry in later:
            self.assertEqual(entry["lineup"]["WR"][:3], ["A-WR1", "A-WR3", "A-WR4"])
        self.assertTrue(any(i["player"] == "A-WR2" and i["removed"] for i in result["injuries"]))
        sub = next(s for s in result["substitutions"] if s["removed"] == "A-WR2")
        self.assertEqual(sub["basis"], "depth_order")

    def test_pause_fires_for_a_removed_quarterback_inside_a_block(self):
        plan = (block("offense", "first", {"possessions": 3}, QB=["A-QB1"]),
                block("offense", "second", None, QB=["A-QB2"]))
        a, b = club("A", plan), club("B")
        base = play(a, b)
        first = applied(base, "A")[0]["possession"]
        onsets = {(first, "A-QB1"): {"injury_class": "lower_extremity", "severity": "multi_week", "removed": True}}
        partial = play(a, b, management_mode="user_controlled", controlled_team="A", _test_onsets=dict(onsets))
        self.assertFalse(partial["terminated"])
        pause = partial["pauses"][-1]
        decision = next(d for d in pause["decisions"] if d["slot"] == "A-QB1")
        self.assertEqual(decision["reason"], "quarterback")
        self.assertEqual(decision["eligible"], ["A-QB2", "A-QB3"])
        self.assertNotIn("rotation", partial)
        # Stone sends the third quarterback: his choice leads the block, then the plan resumes.
        result = play(a, b, management_mode="user_controlled", controlled_team="A", _test_onsets=dict(onsets),
                      continuation={"decisions": [{"token": pause["continuation_token"], "choices": {"A-QB1": "A-QB3"}}]})
        self.assertTrue(result["terminated"])
        self.assertEqual(validate_result(result), [])
        offense = applied(result, "A")
        self.assertEqual(offense[0]["lineup"]["QB"][0], "A-QB1")
        in_block = [e for e in offense if e["block"] == 0 and e["possession"] > first]
        self.assertTrue(in_block)
        for entry in in_block:
            self.assertEqual(entry["lineup"]["QB"][0], "A-QB3")
        second = [e for e in offense if e["block"] == 1]
        self.assertTrue(second)
        self.assertEqual(second[0]["lineup"]["QB"][0], "A-QB2")
        passer = {p["number"]: p["passer"] for p in result["possessions"] if p["team"] == "A"}
        self.assertEqual(passer[in_block[0]["possession"]], "A-QB3")
        self.assertEqual(passer[second[0]["possession"]], "A-QB2")
        self.assertEqual(result["team_stats"]["A"]["players"]["A-QB1"]["offensive_snaps"],
                         snaps_by_drive(result, "A")[first])


class DefaultAndLabelSwapTests(unittest.TestCase):
    def test_default_rotation_by_quarter(self):
        a, b = club("A"), club("B")
        result = play(a, b)
        self.assertEqual(validate_result(result), [])
        for team in ("A", "B"):
            self.assertEqual(result["rotation"][team]["basis"],
                             {"offense": "default", "defense": "default", "special_teams": "depth_order"})
            blocks = result["rotation"][team]["blocks"]["offense"]
            self.assertEqual([b["unit"] for b in blocks], ["first unit", "second unit", "reserves"])
            self.assertEqual(blocks[0]["until"], {"quarter": 1, "possessions_after": 1})
            self.assertEqual(blocks[1]["until"], {"quarter": 3})
            self.assertIsNone(blocks[2]["until"])
            self.assertEqual(blocks[0]["players"]["QB"], [team + "-QB1"])
            self.assertEqual(blocks[1]["players"]["QB"], [team + "-QB2"])
            self.assertEqual(blocks[2]["players"]["QB"], [team + "-QB3"])
            self.assertEqual(blocks[0]["players"]["WR"], [team + "-WR1", team + "-WR2", team + "-WR3"])
            self.assertEqual(blocks[1]["players"]["WR"], [team + "-WR4", team + "-WR5", team + "-WR3"])
            for side in ("offense", "defense"):
                entries = applied(result, team, side)
                first = [e for e in entries if e["block"] == 0]
                self.assertTrue(all(e["quarter"] <= 2 for e in first))
                self.assertLessEqual(sum(e["quarter"] == 2 for e in first), 1)
                self.assertTrue(all(e["quarter"] in (2, 3) for e in entries if e["block"] == 1))
                self.assertTrue(all(e["quarter"] >= 4 for e in entries if e["block"] == 2))
                self.assertEqual([e["block"] for e in entries], sorted(e["block"] for e in entries))
            lines = result["team_stats"][team]["players"]
            unit = sum(snaps_by_drive(result, team).values())
            self.assertLess(lines[team + "-QB1"]["offensive_snaps"], unit)
            self.assertGreater(lines[team + "-QB1"]["offensive_snaps"], 0)
            self.assertGreater(lines[team + "-QB2"]["offensive_snaps"], 0)

    def test_default_pads_a_short_slice_with_the_deepest_players(self):
        players = game_day_roster("A")
        blocks = rotation.default_blocks(players)
        self.assertEqual(blocks["offense"][1]["players"]["QB"], ["A-QB2"])
        self.assertEqual(blocks["offense"][2]["players"]["QB"], ["A-QB2"])
        self.assertEqual(blocks["offense"][2]["players"]["WR"], ["A-WR5", "A-WR4", "A-WR3"])
        self.assertEqual(blocks["defense"][0]["players"]["DB"], ["A-CB1", "A-S1", "A-CB2", "A-S2", "A-CB3"])
        self.assertEqual(blocks["special_teams"], [])

    def test_label_swap_changes_neither_rotation_nor_result(self):
        a, b = club("A", PLAN), club("B")
        as_home = play(a, b, management_mode="user_controlled", controlled_team="A")
        as_away = play(a, b, management_mode="user_controlled", controlled_team="B")
        plain = play(a, b)
        self.assertEqual(json.dumps(as_home, sort_keys=True, default=str), json.dumps(as_away, sort_keys=True, default=str))
        self.assertEqual(json.dumps(as_home, sort_keys=True, default=str), json.dumps(plain, sort_keys=True, default=str))
        self.assertEqual(as_home["rotation"], as_away["rotation"])
        no_plan_home = play(club("A"), club("B"), management_mode="user_controlled", controlled_team="A")
        no_plan_away = play(club("A"), club("B"), management_mode="user_controlled", controlled_team="B")
        self.assertEqual(no_plan_home["rotation"], no_plan_away["rotation"])
        self.assertEqual(no_plan_home["final_score"], no_plan_away["final_score"])


class FailClosedTests(unittest.TestCase):
    def errors(self, plan, team="A"):
        return rotation.plan_errors(club(team, plan), club(team, plan).roster, PRESEASON)

    def test_unknown_player_group_side_and_missing_until(self):
        self.assertTrue(any("not on the game-day unit" in e
                            for e in self.errors((block("offense", "x", None, QB=["A-QB9"]),))))
        self.assertTrue(any("is not a WR" in e for e in self.errors((block("offense", "x", None, WR=["A-QB1"]),))))
        self.assertTrue(any("unknown group" in e for e in self.errors((block("offense", "x", None, DL=["A-DE1"]),))))
        self.assertTrue(any("unknown group" in e for e in self.errors((block("offense", "x", None, QBS=["A-QB1"]),))))
        self.assertTrue(any("unknown side" in e for e in self.errors((block("kicking", "x", None),))))
        self.assertTrue(any("needs an until rule" in e
                            for e in self.errors((block("offense", "x", None, QB=["A-QB1"]),
                                                  block("offense", "y", None, QB=["A-QB2"])))))
        self.assertTrue(any("five line slots" in e
                            for e in self.errors((block("offense", "x", None, LT="A-OT1", RT="A-OT2"),))))
        self.assertTrue(any("until must use" in e
                            for e in self.errors((block("offense", "x", {"drives": 2}, QB=["A-QB1"]),
                                                  block("offense", "y", None)))))
        self.assertTrue(any("names a player twice" in e
                            for e in self.errors((block("offense", "x", None, WR=["A-WR1", "A-WR1"]),))))
        self.assertEqual(self.errors(PLAN), [])
        slots = (block("offense", "x", None, LT="A-OT1", LG="A-OG1", C="A-C1", RG="A-OG2", RT="A-OT2"),)
        self.assertEqual(self.errors(slots), [])
        self.assertEqual(rotation.parse(club("A", slots))[0]["offense"][0]["players"]["OL"],
                         ["A-OT1", "A-OG1", "A-C1", "A-OG2", "A-OT2"])

    def test_kernel_and_runner_refuse_a_bad_plan_before_any_draw(self):
        bad = club("A", (block("offense", "x", None, QB=["A-QB9"]),))
        with self.assertRaisesRegex(ValueError, "rotation plan"):
            play(bad, club("B"))
        with self.assertRaisesRegex(ValueError, "rotation plan"):
            game_runner.build_game_packet("e", "snapshot!", bad, club("B"), game_type=PRESEASON, game_date=DATE)

    def test_featured_entries_still_pass_and_are_not_blocks(self):
        plan = ({"player_id": "A-WR1", "featured": True},) + PLAN
        self.assertEqual(self.errors(plan), [])
        result = play(club("A", plan), club("B"))
        self.assertEqual(validate_result(result), [])


class RegularSeasonUnchangedTests(unittest.TestCase):
    def test_no_rotation_outside_preseason_and_a_block_is_refused(self):
        a, b = club("A"), club("B")
        for game_type in ("regular", "postseason"):
            result = resolve_game(a, b, seed=SEED, event_id="unchanged-" + game_type, game_type=game_type)
            self.assertNotIn("rotation", result)
            passers = {p["passer"] for p in result["possessions"] if p["team"] == "A"}
            self.assertEqual(passers, {"A-QB1"})
            planned = club("A", PLAN)
            with self.assertRaisesRegex(ValueError, "preseason games only"):
                resolve_game(planned, b, seed=SEED, event_id="refused", game_type=game_type)
            # The runner's regular-season unit (46 actives) is refused for the same reason.
            spares = {"A-QB3", "A-WR5"}
            legal = TeamInput("A", tuple(p.player_id for p in planned.roster if p.player_id not in spares),
                              roster=planned.roster, offensive_call_sheet=TEAM_A_SHEET, rotation_plan=planned.rotation_plan)
            with self.assertRaisesRegex(ValueError, "preseason games only"):
                game_runner.build_game_packet("e", "snapshot!", legal, b, game_type=game_type)
        featured = club("A", ({"player_id": "A-WR1", "featured": True},))
        self.assertEqual(rotation.plan_errors(featured, featured.roster, "regular"), [])

    def test_quarter_helpers(self):
        self.assertEqual([rotation.quarter_of(1, 1800), rotation.quarter_of(1, 900), rotation.quarter_of(1, 901),
                          rotation.quarter_of(2, 1000), rotation.quarter_of(2, 10), rotation.quarter_of("OT", 900),
                          rotation.quarter_of(1, 100, quarter=3)], [1, 2, 1, 3, 4, 5, 3])
        self.assertEqual([rotation.quarter_of_remaining(r) for r in (3600, 2700, 2000, 1800, 1000, 900, 1)],
                         [1, 2, 2, 3, 3, 4, 4])
        self.assertEqual(rotation.quarter_of_remaining(900, overtime=True), 5)


if __name__ == "__main__":
    unittest.main()
