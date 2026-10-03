"""Kernel 2014.6 batch B6, W2a: the substitution record (records only).

participation.slot_lineup is the single on-field source and reproduces the
crediting byte for byte; the kernel's recorder names the entrant, the
vacated and entering slots, slot moves, emergency fills and specialist or
returner changes through the pure path (emergency_view with the kept
fillers, rotation.apply on the current block), never lineup() or select().
Synthetic seeds and the committed Week 3 game depth chart only; no career
state.
"""
import json
import sys
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import participation, usage
from runtime.depth_library import UNIT
from runtime.kernel import TeamInput, resolve_game, validate_result
from runtime.profiles import PROFILE_2014_6, Profile
from runtime.usage import group
from support_rosters import game_day_roster
from synthetic_games import SEED, sample_teams
from test_injuries_in_game import force

ROOT = Path(__file__).resolve().parents[1]
CHART = Path(__file__).parent / "data/week_03_jacksonville_game_depth_chart.json"
RECORD_OFF = Profile("2014.6", base="2010_2014w4", cell_rules="2014.6", strength=PROFILE_2014_6.strength,
                     flags=PROFILE_2014_6.flags - {"substitution_record"}, record_base=True)


def jacksonville_week_3():
    """Jacksonville's Week 3 game input from the frozen chart (commit 7cf75a5:
    the 53 with their chart positions, depth and roles; the seven inactives
    off the game-day unit). No career state is read."""
    chart = json.loads(CHART.read_text(encoding="utf-8"))
    inactive = set(chart["game_day_inactives"]["players"])
    roster = []
    for grp, players in chart["depth"].items():
        for rank, player in enumerate(players, 1):
            position = chart["positions"][player]
            roster.append({"player_id": player, "position": position, "available": True,
                           "unit": UNIT[group(position)], "roles": chart["roles"].get(player, []), "depth": rank,
                           "medical_limitation": None})
    active = tuple(p["player_id"] for p in roster if p["player_id"] not in inactive)
    assert len(active) == 46
    return TeamInput("Jacksonville Jaguars", active, roster=tuple(roster))


class SlotLineupTests(unittest.TestCase):
    def setUp(self):
        self.a, self.b = sample_teams()
        self.off = tuple(game_day_roster("A"))
        self.dfn = tuple(game_day_roster("B"))
        self.passer = usage.game_passer(self.off)
        self.front = usage.protection_front(self.off)

    def test_slot_lineup_reproduces_the_crediting(self):
        # The pre-B6 convention, written out: passer and front every snap,
        # RB1 100/RB2 25, WR 100/100/45, TE 100/30; DL 100/100/100/70, LB
        # 100/100/50, DB 100/100/100/100/80, through the hundredths accumulator.
        rows = [{"play_type": "run"}] * 7
        acc, acc_ref = {}, {}
        got = participation.scrimmage(acc, "A", "B", self.off, self.dfn, self.passer, self.front, rows)
        ref = {"A": {}, "B": {}}
        n = 7
        ref["A"][self.passer.player_id] = n
        for lineman in self.front.values():
            ref["A"][lineman.player_id] = n

        def credit(key, share):
            before = acc_ref.get(key, 0)
            acc_ref[key] = before + share * n
            return acc_ref[key] // 100 - before // 100

        backs = usage.depth_order(self.off, "RB")
        fullbacks = usage.depth_order(self.off, "FB")
        for rank, (player, share) in enumerate(zip(backs[:1] + (fullbacks[:1] or backs[1:2]), (100, 25))):
            c = credit((("A", "O", "RB"), rank), share)
            if c:
                ref["A"][player.player_id] = ref["A"].get(player.player_id, 0) + c
        for grp, shares in (("WR", (100, 100, 45)), ("TE", (100, 30))):
            for rank, (player, share) in enumerate(zip(usage.depth_order(self.off, grp), shares)):
                c = credit((("A", "O", grp), rank), share)
                if c:
                    ref["A"][player.player_id] = ref["A"].get(player.player_id, 0) + c
        for grp, shares in (("DL", (100, 100, 100, 70)), ("LB", (100, 100, 50)), ("DB", (100, 100, 100, 100, 80))):
            for rank, (player, share) in enumerate(zip(usage.depth_order(self.dfn, grp), shares)):
                c = credit((("B", "D", grp), rank), share)
                if c:
                    ref["B"][player.player_id] = ref["B"].get(player.player_id, 0) + c
        self.assertEqual(got, ref)
        self.assertEqual(acc, acc_ref)
        self.assertEqual(list(got["A"]), list(ref["A"]))

    def test_slot_labels_and_shares(self):
        lineup = participation.slot_lineup(self.off, self.dfn, self.passer, self.front)
        labels = [s["slot"] for s in lineup["offense"]]
        self.assertEqual(labels[:6], ["QB", "LT", "LG", "C", "RG", "RT"])
        # The fixture dresses a fullback, so the second back slot is his.
        self.assertEqual(labels[6:], ["RB1", "FB1", "WR1", "WR2", "WR3", "TE1", "TE2"])
        self.assertEqual([s["key"] for s in lineup["offense"][6:8]], [("O", "RB"), ("O", "RB")])
        self.assertEqual([s["share"] for s in lineup["offense"][6:8]], [100, 25])
        self.assertEqual([s["slot"] for s in lineup["defense"]],
                         ["DL1", "DL2", "DL3", "DL4", "LB1", "LB2", "LB3", "DB1", "DB2", "DB3", "DB4", "DB5"])
        self.assertTrue(all(s["share"] > 0 for side in lineup.values() for s in side))
        self.assertEqual([s["key"] for s in lineup["offense"][:6]], [None] * 6)
        self.assertEqual(participation.slot_map(lineup, "offense")[self.passer.player_id], "QB")


class RecorderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a, cls.b = sample_teams()
        base = resolve_game(cls.a, cls.b, seed=SEED + b"-w2a", event_id="w2a", _test_profile=PROFILE_2014_6)
        # An A possession: A's offense and B's defense are exposed on it.
        cls.drive = [p["number"] for p in base["possessions"] if p["team"] == "A"][1]
        cls.receiver = base["opening_receiver"]

    def game(self, onsets, profile=PROFILE_2014_6, **kw):
        return resolve_game(self.a, self.b, seed=SEED + b"-w2a", event_id="w2a", _test_profile=profile,
                            _test_onsets=onsets, **kw)

    def test_entrant_is_the_next_same_side_slot_player(self):
        r = self.game({**force(self.drive, "A-WR1"), **force(self.drive, "B-CB1")})
        self.assertEqual(validate_result(r), [])
        subs = {s["removed"]: s for s in r["substitutions"]}
        wr = subs["A-WR1"]
        self.assertEqual(wr["vacated_slots"], [{"side": "offense", "slot": "WR1"}])
        self.assertEqual(wr["entrant"], "A-WR4")
        self.assertEqual(wr["entering_slots"], [{"side": "offense", "slot": "WR3", "player": "A-WR4"}])
        self.assertEqual([(m["player"], m["from"], m["to"]) for m in wr["moves"]],
                         [("A-WR2", "WR2", "WR1"), ("A-WR3", "WR3", "WR2")])
        self.assertEqual(wr["replacement"], "A-WR2")  # the depth-order successor, unchanged
        self.assertEqual(wr["basis"], "depth_order")
        self.assertEqual(wr["emergency"], [])
        # The entrant took the field: credited snaps after the removal.
        self.assertGreater(r["team_stats"]["A"]["players"]["A-WR4"]["offensive_snaps"], 0)
        cb = subs["B-CB1"]
        self.assertEqual(cb["vacated_slots"], [{"side": "defense", "slot": "DB1"}])
        self.assertEqual(cb["entering_slots"][0]["slot"], "DB5")
        self.assertEqual(len(cb["moves"]), 4)
        self.assertTrue(all(m["side"] == "defense" for m in cb["moves"]))

    def test_specialist_and_returner_changes(self):
        # The opening kickoff exposes the receiving club's returner and the
        # kicking club's kicker: both are removed at the end of drive 1.
        receiving = self.a if self.receiver == "A" else self.b
        kicking = self.b if self.receiver == "A" else self.a
        returner = usage.club_returner(receiving.roster, "kick_return").player_id
        kicker = usage.kicking_specialist(kicking.roster, "K", "placekicker").player_id
        r = self.game({**force(1, returner), **force(1, kicker)})
        self.assertEqual(validate_result(r), [])
        sub = next(s for s in r["substitutions"] if s["removed"] == returner)
        self.assertIn("kick_return", sub["returners"])
        self.assertEqual(sub["returners"]["kick_return"]["from"], returner)
        self.assertNotEqual(sub["returners"]["kick_return"]["to"], returner)
        sub = next(s for s in r["substitutions"] if s["removed"] == kicker)
        self.assertEqual(sub["specialists"]["K"]["from"], kicker)
        self.assertNotEqual(sub["specialists"]["K"]["to"], kicker)

    def test_record_is_the_only_difference(self):
        onsets = {**force(self.drive, "A-WR1"), **force(self.drive, "B-CB1")}
        on, off = self.game(onsets), self.game(onsets, RECORD_OFF)
        self.assertEqual(on["injuries"], off["injuries"])
        self.assertEqual(on["final_score"], off["final_score"])
        self.assertEqual(on["team_stats"], off["team_stats"])
        self.assertEqual([p["emergency"] if "emergency" in p else None for p in on["possessions"]],
                         [p["emergency"] if "emergency" in p else None for p in off["possessions"]])
        for a, b in zip(on["substitutions"], off["substitutions"]):
            self.assertEqual({k: a[k] for k in b}, b)
            self.assertEqual(set(a) - set(b), {"entrant", "vacated_slots", "entering_slots", "moves", "emergency",
                                               "specialists", "returners"})

    def test_sequential_removals_at_one_boundary(self):
        # Two removals on one club at one boundary: the second record is
        # computed against the lineup the first one left.
        r = self.game({**force(self.drive, "A-WR1"), **force(self.drive, "A-WR2")})
        subs = [s for s in r["substitutions"] if s["drive"] == self.drive and s["team"] == "A"]
        self.assertEqual([s["removed"] for s in subs], ["A-WR1", "A-WR2"])
        first, second = subs
        self.assertEqual(first["entrant"], "A-WR4")
        self.assertEqual(second["vacated_slots"], [{"side": "offense", "slot": "WR1"}])
        self.assertEqual(second["entrant"], "A-WR5")
        self.assertEqual(second["entering_slots"], [{"side": "offense", "slot": "WR3", "player": "A-WR5"}])

    def test_coach_choice_recomputes_the_record(self):
        spare = replace(self.a.roster[0], player_id="A-WR9", position="WR", depth=9)
        roster = self.a.roster + (spare,)
        a = TeamInput("A", tuple(p.player_id for p in roster), roster=roster,
                      offensive_call_sheet=self.a.offensive_call_sheet,
                      rotation_plan=({"player_id": "A-WR1", "featured": True},))
        partial = resolve_game(a, self.b, seed=SEED + b"-w2a", event_id="w2a", management_mode="user_controlled",
                               controlled_team="A", _test_onsets=force(self.drive, "A-WR1"),
                               _test_profile=PROFILE_2014_6)
        self.assertTrue(partial.get("paused"))
        pause = partial["pauses"][-1]
        choice = pause["decisions"][0]["eligible"][-1]
        final = resolve_game(a, self.b, seed=SEED + b"-w2a", event_id="w2a", management_mode="user_controlled",
                             controlled_team="A", _test_onsets=force(self.drive, "A-WR1"),
                             continuation={"decisions": [{"token": pause["continuation_token"],
                                                          "choices": {"A-WR1": choice}}]},
                             _test_profile=PROFILE_2014_6)
        self.assertTrue(final["terminated"])
        sub = next(s for s in final["substitutions"] if s["removed"] == "A-WR1")
        self.assertEqual((sub["basis"], sub["replacement"]), ("coach_choice", choice))
        # The chosen player now holds the vacated slot's rank: he is the entrant or a mover.
        on_field = [sub["entrant"]] + [m["player"] for m in sub["moves"]]
        self.assertIn(choice, on_field)
        self.assertEqual(validate_result(final), [])


class PreseasonTests(unittest.TestCase):
    def test_fills_and_rotation_tracker_unchanged(self):
        from test_preseason_rotation import PLAN, club  # the preseason rotation fixture
        a, b = club("A", PLAN), club("B")
        kw = dict(seed=SEED + b"-w2a-pre", event_id="w2a-pre", game_type="preseason", game_date="2014-08-16")
        base = resolve_game(a, b, _test_profile=RECORD_OFF, **kw)
        drive = [p["number"] for p in base["possessions"] if p["team"] == a.team_id][1]
        on = resolve_game(a, b, _test_profile=PROFILE_2014_6, _test_onsets=force(drive, "A-WR2"), **kw)
        off = resolve_game(a, b, _test_profile=RECORD_OFF, _test_onsets=force(drive, "A-WR2"), **kw)
        self.assertEqual(on["rotation"], off["rotation"])
        self.assertEqual(on["team_stats"], off["team_stats"])
        self.assertEqual([p.get("emergency") for p in on["possessions"]], [p.get("emergency") for p in off["possessions"]])
        sub = next(s for s in on["substitutions"] if s["removed"] == "A-WR2")
        self.assertIn("entrant", sub)


class Week3ChartTests(unittest.TestCase):
    """On the frozen Week 3 chart (Talib, Verner, Rambo, Trawick, Poyer,
    Bouye, Butler, ... at defensive back), with Poyer gone as in the Week 3
    record, Talib's removal names Butler entering and Bouye's move."""

    def test_talib_record_names_butler_and_bouye(self):
        jax = jacksonville_week_3()
        _, b = sample_teams()
        base = resolve_game(jax, b, seed=SEED + b"-w2a-jax", event_id="w2a-jax", _test_profile=PROFILE_2014_6)
        self.assertEqual(validate_result(base), [])
        b_drives = [p["number"] for p in base["possessions"] if p["team"] == "B"]
        poyer_drive, talib_drive = b_drives[0], b_drives[1]
        r = resolve_game(jax, b, seed=SEED + b"-w2a-jax", event_id="w2a-jax", _test_profile=PROFILE_2014_6,
                         _test_onsets={**force(poyer_drive, "Jordan Poyer", injury_class="head_neck"),
                                       **force(talib_drive, "Aqib Talib", injury_class="head_neck")})
        self.assertEqual(validate_result(r), [])
        subs = {s["removed"]: s for s in r["substitutions"]}
        poyer = subs["Jordan Poyer"]
        self.assertEqual(poyer["vacated_slots"], [{"side": "defense", "slot": "DB5"}])
        self.assertEqual(poyer["entrant"], "A.J. Bouye")
        talib = subs["Aqib Talib"]
        self.assertEqual(talib["vacated_slots"], [{"side": "defense", "slot": "DB1"}])
        self.assertEqual(talib["entrant"], "Malcolm Butler")
        self.assertEqual(talib["entering_slots"], [{"side": "defense", "slot": "DB5", "player": "Malcolm Butler"}])
        bouye = next(m for m in talib["moves"] if m["player"] == "A.J. Bouye")
        self.assertEqual((bouye["from"], bouye["to"]), ("DB5", "DB4"))
        self.assertEqual([m["player"] for m in talib["moves"]],
                         ["Alterraun Verner", "Bacarri Rambo", "Brynden Trawick", "A.J. Bouye"])
        self.assertEqual(talib["replacement"], "Alterraun Verner")
        self.assertGreater(r["team_stats"]["Jacksonville Jaguars"]["players"]["Malcolm Butler"]["defensive_snaps"], 0)


if __name__ == "__main__":
    unittest.main()
