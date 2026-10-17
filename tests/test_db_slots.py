"""Kernel 2014.6 batch B15: W2b (position-true defensive-back seats), W2c (E2
pause eligibility) and their Week 5 inputs (the background clubs'
contemporaneous DB labels and chart nickel roles, Jacksonville's roles
failing closed).

participation.db_seats seats each club's defensive backs by family: DB1 and
DB2 the outside corners, DB3 and DB4 the safeties, DB5 the nickel, then the
reserves; the designated nickel is settled first, the outside reserve
replaces an outside starter, and without roles the move-up convention holds.
Synthetic seeds, the frozen Week 3 game depth chart (commit 7cf75a5) and the
committed data only; no career state is written and no service is called.
"""
import copy
import json
import sys
import tempfile
import unittest
from dataclasses import replace
from datetime import date
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import depth_library, participation, player_evidence, strength, usage, week_inputs
from runtime.player_evidence import PlayerInput
from runtime.depth_library import UNIT
from runtime.kernel import DEPTH_ORDER, TeamInput, resolve_game, validate_result
from runtime.profiles import PROFILE_2014_5, PROFILE_2014_6, Profile
from runtime.seasons import SeasonPaths
from runtime.usage import group
from support_rosters import game_day_roster
from synthetic_games import SEED, sample_teams
from test_injuries_in_game import force

ROOT = Path(__file__).resolve().parents[1]
CHART = Path(__file__).parent / "data/week_03_jacksonville_game_depth_chart.json"
JAX = "Jacksonville Jaguars"
SEATS_OFF = Profile("2014.6", base="2010_2014w4", cell_rules="2014.6", strength=PROFILE_2014_6.strength,
                    flags=PROFILE_2014_6.flags - {"db_slots", "pause_eligibility"}, record_base=True)
WEEK3_ROLES = {"Jordan Poyer": "nickel", "A.J. Bouye": "outside_reserve"}  # the Week 3 decision record
# A user-controlled club's dated delegations (U6 and its fourth downs), so the
# only pause is the substitution under test.
DELEGATED = {"try_policy": {"otherwise": "league"}, "kickoff_policy": {"otherwise": "league"},
             "fourth_down_policy": {"otherwise": "league"}}


def ids(seats):
    return [p.player_id for _, p in seats]


def with_roles(players, roles):
    return tuple(replace(p, roles=p.roles + (roles[p.player_id],)) if p.player_id in roles else p for p in players)


def jacksonville_week_3(roles=None, featured=(), **fields):
    """Jacksonville's Week 3 game input from the frozen chart (the 46 dressed,
    their chart positions, depth and roles), with ``roles`` added and the
    ``featured`` players in a rotation plan. The roles are inputs, so they
    enter the packet and the game's random stream with it."""
    chart = json.loads(CHART.read_text(encoding="utf-8"))
    inactive = set(chart["game_day_inactives"]["players"])
    roles = roles or {}
    roster = []
    for grp, players in chart["depth"].items():
        for rank, player in enumerate(players, 1):
            position = chart["positions"][player]
            roster.append({"player_id": player, "position": position, "available": True,
                           "unit": UNIT[group(position)],
                           "roles": list(chart["roles"].get(player, [])) + ([roles[player]] if player in roles else []),
                           "depth": rank, "medical_limitation": None})
    active = tuple(p["player_id"] for p in roster if p["player_id"] not in inactive)
    plan = tuple({"player_id": pid, "featured": True} for pid in featured)
    return TeamInput(JAX, active, roster=tuple(roster), rotation_plan=plan, **fields)


class SeatTests(unittest.TestCase):
    def setUp(self):
        self.players = game_day_roster("A")

    def test_base_four_then_nickel_then_family_units(self):
        self.assertEqual(ids(participation.db_seats(self.players)),
                         ["A-CB1", "A-CB2", "A-S1", "A-S2", "A-CB3", "A-CB4", "A-CB5", "A-S3", "A-S4"])
        self.assertEqual([s for s, _ in participation.db_seats(self.players)],
                         ["CB1", "CB2", "S1", "S2", "NB1", "CB3", "CB4", "S3", "S4"])
        seated = participation.seat_defensive_backs(self.players)
        self.assertEqual([p.player_id for p in usage.depth_order(seated, "DB")][:5],
                         ["A-CB1", "A-CB2", "A-S1", "A-S2", "A-CB3"])
        # Only the DB group's depth moves; the tuple keeps its order.
        self.assertEqual([p.player_id for p in seated], [p.player_id for p in self.players])
        for before, after in zip(self.players, seated):
            if group(before.position) != "DB":
                self.assertEqual(before, after)
            else:
                self.assertEqual(replace(before, depth=after.depth), after)
        self.assertEqual(participation.seat_defensive_backs(seated), seated)  # idempotent

    def test_move_up_without_roles(self):
        starters = participation.db_starters(self.players)
        self.assertEqual(starters, ("A-CB1", "A-CB2"))
        left = tuple(p for p in self.players if p.player_id != "A-CB1")
        # The nickel moves outside, the next corner enters at nickel; the
        # safeties keep their seats.
        self.assertEqual(ids(participation.db_seats(left, starters))[:5], ["A-CB2", "A-CB3", "A-S1", "A-S2", "A-CB4"])
        left = tuple(p for p in self.players if p.player_id != "A-S1")
        self.assertEqual(ids(participation.db_seats(left, starters))[:5], ["A-CB1", "A-CB2", "A-S2", "A-S3", "A-CB3"])

    def test_the_nickel_is_settled_first_and_the_outside_reserve_replaces_a_starter(self):
        players = with_roles(self.players, {"A-CB4": "nickel", "A-CB5": "outside_reserve"})
        starters = participation.db_starters(players)
        self.assertEqual(starters, ("A-CB1", "A-CB2"))
        self.assertEqual(ids(participation.db_seats(players, starters))[:5],
                         ["A-CB1", "A-CB2", "A-S1", "A-S2", "A-CB4"])
        left = tuple(p for p in players if p.player_id != "A-CB1")
        self.assertEqual(ids(participation.db_seats(left, starters))[:5], ["A-CB2", "A-CB5", "A-S1", "A-S2", "A-CB4"])
        # The designated nickel gone, the next corner other than the outside
        # reserve takes the nickel.
        left = tuple(p for p in players if p.player_id != "A-CB4")
        self.assertEqual(ids(participation.db_seats(left, starters))[:5], ["A-CB1", "A-CB2", "A-S1", "A-S2", "A-CB3"])
        # A safety can be the designated nickel.
        players = with_roles(self.players, {"A-S3": "nickel"})
        self.assertEqual(ids(participation.db_seats(players))[:5], ["A-CB1", "A-CB2", "A-S1", "A-S2", "A-S3"])

    def test_an_exhausted_family_is_filled_by_the_other(self):
        players = with_roles(self.players, {"A-CB4": "nickel", "A-CB5": "outside_reserve"})
        starters = participation.db_starters(players)
        left = tuple(p for p in players if p.player_id not in ("A-S1", "A-S2", "A-S3"))
        # The safety seat takes the next corner other than the outside reserve.
        self.assertEqual(ids(participation.db_seats(left, starters))[:5], ["A-CB1", "A-CB2", "A-S4", "A-CB3", "A-CB4"])
        # A generic DB label (an emergency filler's) fills a short seat first.
        filler = replace(game_day_roster("A")[0], player_id="A-X", position="DB", depth=101)
        self.assertEqual(ids(participation.db_seats(left + (filler,), starters))[:5],
                         ["A-CB1", "A-CB2", "A-S4", "A-X", "A-CB4"])

    def test_seating_is_not_idempotent_once_a_family_runs_out(self):
        # Review fix (October 16, 2026): a seat filled from the other family
        # renumbers that player ahead of his own family, so a second seating
        # reorders; the kernel seats every view once (KernelSeatTests).
        left = tuple(p for p in self.players if p.player_id not in ("A-CB5", "A-S3", "A-S4", "A-S1"))
        starters = participation.db_starters(left)
        once = participation.seat_defensive_backs(left, starters)
        self.assertEqual([p.player_id for p in usage.depth_order(once, "DB")],
                         ["A-CB1", "A-CB2", "A-S2", "A-CB4", "A-CB3"])
        twice = participation.seat_defensive_backs(once, starters)
        self.assertNotEqual([p.player_id for p in usage.depth_order(twice, "DB")],
                            [p.player_id for p in usage.depth_order(once, "DB")])

    def test_the_outside_reserve_starts_when_a_starter_is_not_dressed(self):
        # Review fix (October 16, 2026): the outside reserve is the first
        # replacement for an outside starter before kickoff too, ahead of a
        # lower-ranked corner. The Week 4 chart's DB order with Stone's
        # recorded roles (Bouye nickel, Ball outside reserve) and Poyer
        # inactive.
        order = (("Aqib Talib", "CB"), ("Alterraun Verner", "CB"), ("Bacarri Rambo", "S"),
                 ("Brynden Trawick", "S"), ("A.J. Bouye", "CB"), ("Chris Prosinski", "S"),
                 ("Adrian Phillips", "S"), ("Alan Ball", "CB"), ("Malcolm Butler", "CB"))
        roles = {"A.J. Bouye": ("nickel",), "Alan Ball": ("outside_reserve",)}
        unit = tuple(PlayerInput(name, pos, unit="defense", depth=i, roles=roles.get(name, ()))
                     for i, (name, pos) in enumerate(order, 1))
        self.assertEqual(participation.db_starters(unit), ("Aqib Talib", "Alterraun Verner"))
        without = lambda name: tuple(p for p in unit if p.player_id != name)  # noqa: E731
        self.assertEqual(participation.db_starters(without("Aqib Talib")), ("Alterraun Verner", "Alan Ball"))
        self.assertEqual(participation.db_starters(without("Alterraun Verner")), ("Aqib Talib", "Alan Ball"))
        self.assertEqual(ids(participation.db_seats(without("Aqib Talib")))[:5],
                         ["Alterraun Verner", "Alan Ball", "Bacarri Rambo", "Brynden Trawick", "A.J. Bouye"])
        # The frozen Week 3 chart with its recorded roles (Poyer nickel, Bouye
        # outside reserve): Talib not dressed, Bouye starts, not Butler.
        players = player_evidence.normalize_players(jacksonville_week_3(WEEK3_ROLES))
        self.assertEqual(participation.db_starters(players), ("Aqib Talib", "Alterraun Verner"))
        self.assertEqual(participation.db_starters(tuple(p for p in players if p.player_id != "Aqib Talib")),
                         ("Alterraun Verner", "A.J. Bouye"))
        # Without roles the depth order decides, as before.
        plain = tuple(replace(p, roles=()) for p in unit)
        self.assertEqual(participation.db_starters(tuple(p for p in plain if p.player_id != "Aqib Talib")),
                         ("Alterraun Verner", "A.J. Bouye"))

    def test_the_seats_read_only_family_depth_and_roles(self):
        # The label swap at the function: the same players under other ids
        # (another club's) take the same seats.
        other = tuple(replace(p, player_id=p.player_id.replace("A-", "Z-")) for p in self.players)
        self.assertEqual([(s, p.player_id.replace("Z-", "A-")) for s, p in participation.db_seats(other)],
                         [(s, p.player_id) for s, p in participation.db_seats(self.players)])

    def test_strength_reads_the_base_four(self):
        units = strength.defense_units(participation.seat_defensive_backs(self.players))
        self.assertEqual([p.player_id for _, p in units["coverage"][:4]], ["A-CB1", "A-CB2", "A-S1", "A-S2"])
        # The box safety is the first labelled SS of the base four, else S or FS.
        self.assertEqual([p.player_id for _, p in units["run_defense"]][-1], "A-S1")


class KernelSeatTests(unittest.TestCase):
    """The Verner case on the frozen Week 3 chart (Talib, Verner, Rambo,
    Trawick, Poyer, Bouye, Butler, Prosinski, Phillips; Ball inactive):
    Poyer's and then Talib's removal, as in the Week 3 record."""

    @classmethod
    def setUpClass(cls):
        cls.b = sample_teams()[1]

    def onsets(self, team, profile, tag):
        """Poyer's removal after the opponent's first possession and Talib's
        after its second, in this input's own game."""
        base = resolve_game(team, self.b, seed=SEED + b"-" + tag.encode(), event_id=tag, _test_profile=profile)
        drives = [p["number"] for p in base["possessions"] if p["team"] == "B"]
        return {**force(drives[0], "Jordan Poyer", injury_class="head_neck"),
                **force(drives[1], "Aqib Talib", injury_class="head_neck")}

    def play(self, team, profile=PROFILE_2014_6, tag="w2b-jax", **kw):
        r = resolve_game(team, self.b, seed=SEED + b"-" + tag.encode(), event_id=tag, _test_profile=profile,
                         _test_onsets=self.onsets(team, profile, tag), **kw)
        self.assertEqual(validate_result(r), [])
        return r

    def test_move_up_convention_keeps_the_safeties_seated(self):
        r = self.play(jacksonville_week_3())
        subs = {s["removed"]: s for s in r["substitutions"]}
        self.assertEqual(subs["Jordan Poyer"]["vacated_slots"], [{"side": "defense", "slot": "DB5"}])
        self.assertEqual(subs["Jordan Poyer"]["entrant"], "A.J. Bouye")
        talib = subs["Aqib Talib"]
        self.assertEqual(talib["entrant"], "Malcolm Butler")
        self.assertEqual(talib["entering_slots"], [{"side": "defense", "slot": "DB5", "player": "Malcolm Butler"}])
        self.assertEqual([(m["player"], m["from"], m["to"]) for m in talib["moves"]],
                         [("Alterraun Verner", "DB2", "DB1"), ("A.J. Bouye", "DB5", "DB2")])
        # Before B15 the safeties moved up a seat and Bouye took DB4 (the
        # depth-order group).
        old = self.play(jacksonville_week_3(), profile=SEATS_OFF)
        moves = {m["player"] for m in {s["removed"]: s for s in old["substitutions"]}["Aqib Talib"]["moves"]}
        self.assertIn("Bacarri Rambo", moves)

    def test_the_recorded_roles_keep_the_nickel_inside(self):
        r = self.play(jacksonville_week_3(WEEK3_ROLES))
        subs = {s["removed"]: s for s in r["substitutions"]}
        # Poyer (the nickel) gone: the next corner other than the outside
        # reserve takes the nickel; Bouye stays the outside reserve.
        self.assertEqual(subs["Jordan Poyer"]["entrant"], "Malcolm Butler")
        talib = subs["Aqib Talib"]
        self.assertEqual(talib["entrant"], "A.J. Bouye")
        self.assertEqual(talib["entering_slots"], [{"side": "defense", "slot": "DB2", "player": "A.J. Bouye"}])
        self.assertEqual([(m["player"], m["from"], m["to"]) for m in talib["moves"]],
                         [("Alterraun Verner", "DB2", "DB1")])
        line = r["team_stats"][JAX]["players"]
        self.assertGreater(line["A.J. Bouye"]["defensive_snaps"], 0)
        self.assertGreater(line["Malcolm Butler"]["defensive_snaps"], 0)

    def test_which_club_is_controlled_changes_nothing(self):
        # No consequential removal, so no pause: the same result whichever
        # club is the controlled one, and autonomously.
        team = jacksonville_week_3(WEEK3_ROLES, **DELEGATED)
        b = self.b
        self.b = replace(b, **DELEGATED)
        try:
            plain = self.play(team, tag="w2b-swap")
            ours = self.play(team, tag="w2b-swap", management_mode="user_controlled", controlled_team=JAX)
            theirs = self.play(team, tag="w2b-swap", management_mode="user_controlled", controlled_team="B")
        finally:
            self.b = b
        for result in (ours, theirs):
            self.assertEqual(json.dumps(result, sort_keys=True, default=str), json.dumps(plain, sort_keys=True, default=str))

    def test_every_consumer_reads_one_db_order_after_a_family_runs_short(self):
        # Review fix (October 16, 2026): each view is seated once from the
        # unseated live list, so the scrimmage lineup, the W2a record, the
        # live rosters (kickoffs, coverage units, returners) and the
        # successor read one DB order for the same available players.
        a, b = sample_teams()
        for gone, dropped, entrant, slot in (("B-S1", ("B-CB5", "B-S3", "B-S4"), "B-CB4", "DB4"),
                                             ("B-CB1", ("B-CB3", "B-CB4", "B-CB5"), "B-S4", "DB5")):
            team = replace(b, active_players=tuple(pid for pid in b.active_players if pid not in dropped))
            tag = "w2b-once-" + gone
            base = resolve_game(a, team, seed=SEED + b"-" + tag.encode(), event_id=tag, _test_profile=PROFILE_2014_6)
            drive = [p["number"] for p in base["possessions"] if p["team"] == "A"][0]
            orders = {}
            real = participation.seat_defensive_backs

            def logged(players, starters=None):
                out = real(players, starters)
                dbs = [p for p in usage.depth_order(out, "DB") if p.player_id.startswith("B-")]
                if dbs:
                    orders.setdefault(frozenset(p.player_id for p in dbs), set()).add(
                        tuple(p.player_id for p in dbs))
                return out
            with mock.patch.object(participation, "seat_defensive_backs", logged):
                r = resolve_game(a, team, seed=SEED + b"-" + tag.encode(), event_id=tag,
                                 _test_profile=PROFILE_2014_6, _test_onsets=force(drive, gone))
            self.assertEqual(validate_result(r), [])
            for members, seen in orders.items():
                self.assertEqual(len(seen), 1, (gone, sorted(seen)))
            sub = next(s for s in r["substitutions"] if s["removed"] == gone)
            self.assertEqual(sub["entrant"], entrant, gone)
            self.assertEqual(sub["entering_slots"], [{"side": "defense", "slot": slot, "player": entrant}], gone)

    def test_the_2014_5_kernel_keeps_the_depth_order(self):
        r = self.play(jacksonville_week_3(WEEK3_ROLES), profile=PROFILE_2014_5)
        self.assertTrue(all("entrant" not in s for s in r["substitutions"]))
        talib = next(s for s in r["substitutions"] if s["removed"] == "Aqib Talib")
        self.assertEqual(talib["replacement"], "Alterraun Verner")


class PauseEligibilityTests(unittest.TestCase):
    """W2c on the Week 3 chart with the recorded roles and Talib featured (a
    consequential removal), Jacksonville user-controlled."""

    @classmethod
    def setUpClass(cls):
        cls.b = sample_teams()[1]
        cls.team = jacksonville_week_3(WEEK3_ROLES, featured=("Aqib Talib", "Alterraun Verner"), **DELEGATED)
        base = resolve_game(cls.team, cls.b, seed=SEED + b"-w2c-jax", event_id="w2c-jax",
                            _test_profile=PROFILE_2014_6)
        cls.drive = [p["number"] for p in base["possessions"] if p["team"] == "B"][1]
        cls.onsets = force(cls.drive, "Aqib Talib")
        cls.partial = cls.play(cls.onsets)

    @classmethod
    def play(cls, onsets, decisions=None, management_mode="user_controlled"):
        kw = dict(management_mode=management_mode, controlled_team=JAX) if management_mode == "user_controlled" else {}
        if decisions is not None:
            kw["continuation"] = {"decisions": decisions}
        return resolve_game(cls.team, cls.b, seed=SEED + b"-w2c-jax", event_id="w2c-jax", _test_profile=PROFILE_2014_6,
                            _test_onsets=onsets, **kw)

    def answer(self, partial, choices):
        return [{"token": partial["pauses"][-1]["continuation_token"], "choices": choices}]

    def test_off_field_family_first_then_the_field_then_the_sentinel(self):
        decision = self.partial["pauses"][-1]["decisions"][0]
        self.assertEqual(decision["slot"], "Aqib Talib")
        self.assertEqual(decision["eligible"],
                         ["A.J. Bouye", "Malcolm Butler", "Chris Prosinski", "Adrian Phillips",
                          "Alterraun Verner", "Bacarri Rambo", "Brynden Trawick", "Jordan Poyer", DEPTH_ORDER])
        self.assertEqual(decision["default"], DEPTH_ORDER)
        self.assertEqual(decision["default_entrant"], "A.J. Bouye")
        self.assertEqual(decision["default_moves"],
                         [{"side": "defense", "player": "Alterraun Verner", "from": "DB2", "to": "DB1"}])

    def test_the_sentinel_reproduces_the_autonomous_rule(self):
        resumed = self.play(self.onsets, self.answer(self.partial, {"Aqib Talib": DEPTH_ORDER}))
        auto = self.play(self.onsets, management_mode="autonomous")
        self.assertTrue(resumed["terminated"])
        self.assertEqual(validate_result(resumed), [])
        for key in ("final_score", "possessions", "play_ledger", "team_stats", "injuries", "substitutions"):
            self.assertEqual(resumed[key], auto[key], key)
        self.assertEqual(resumed["pauses"][0]["choices"], {"Aqib Talib": DEPTH_ORDER})

    def test_an_on_field_choice_is_a_reassignment(self):
        resumed = self.play(self.onsets, self.answer(self.partial, {"Aqib Talib": "Jordan Poyer"}))
        self.assertEqual(validate_result(resumed), [])
        sub = next(s for s in resumed["substitutions"] if s["removed"] == "Aqib Talib")
        self.assertEqual((sub["basis"], sub["replacement"]), ("coach_choice", "Jordan Poyer"))
        # Poyer takes Talib's outside seat and the nickel role passes on: the
        # next corner other than the outside reserve enters at nickel.
        self.assertEqual(sub["entrant"], "Malcolm Butler")
        self.assertEqual([(m["player"], m["from"], m["to"]) for m in sub["moves"]], [("Jordan Poyer", "DB5", "DB1")])

    def test_the_sentinel_is_exempt_from_the_duplicate_check(self):
        onsets = {**self.onsets, **force(self.drive, "Alterraun Verner")}
        partial = self.play(onsets)
        slots = {d["slot"] for d in partial["pauses"][-1]["decisions"]}
        self.assertEqual(slots, {"Aqib Talib", "Alterraun Verner"})
        resumed = self.play(onsets, self.answer(partial, {"Aqib Talib": DEPTH_ORDER, "Alterraun Verner": DEPTH_ORDER}))
        self.assertTrue(resumed["terminated"])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.play(onsets, self.answer(partial, {"Aqib Talib": "A.J. Bouye", "Alterraun Verner": "A.J. Bouye"}))
        with self.assertRaisesRegex(ValueError, "not an eligible"):
            self.play(onsets, self.answer(partial, {"Aqib Talib": "Alan Ball", "Alterraun Verner": DEPTH_ORDER}))

    def test_a_depth_order_answer_beside_a_coach_choice_records_its_own_entrant(self):
        # Review fix (October 16, 2026): the boundary's records are recomputed
        # in removal order after the coach's choice, so Verner's depth-order
        # record names the outside reserve and Talib's names only Butler.
        onsets = {**self.onsets, **force(self.drive, "Alterraun Verner")}
        partial = self.play(onsets)
        resumed = self.play(onsets, self.answer(partial, {"Aqib Talib": "Malcolm Butler",
                                                          "Alterraun Verner": DEPTH_ORDER}))
        self.assertEqual(validate_result(resumed), [])
        subs = {s["removed"]: s for s in resumed["substitutions"] if s["drive"] == self.drive and s["team"] == JAX}
        talib, verner = subs["Aqib Talib"], subs["Alterraun Verner"]
        self.assertEqual((talib["basis"], talib["replacement"], talib["entrant"]),
                         ("coach_choice", "Malcolm Butler", "Malcolm Butler"))
        self.assertEqual(talib["entering_slots"], [{"side": "defense", "slot": "DB1", "player": "Malcolm Butler"}])
        self.assertEqual((verner["basis"], verner["replacement"], verner["entrant"]),
                         ("depth_order", "A.J. Bouye", "A.J. Bouye"))
        self.assertEqual(verner["entering_slots"], [{"side": "defense", "slot": "DB2", "player": "A.J. Bouye"}])
        entering = [e["player"] for s in (talib, verner) for e in s["entering_slots"]]
        self.assertEqual(len(entering), len(set(entering)))

    def test_the_pinned_receiver_list_moves(self):
        # tests/test_injuries_in_game.py pins the 2014.5 list (every receiver
        # by depth); under W2c the off-field receivers come first.
        a, b = sample_teams()
        spare = replace(a.roster[0], player_id="A-WR9", position="WR", depth=9)
        team = TeamInput(a.team_id, tuple(p.player_id for p in a.roster), roster=a.roster + (spare,),
                         offensive_call_sheet=a.offensive_call_sheet,
                         rotation_plan=({"player_id": "A-WR1", "featured": True},), **DELEGATED)
        kw = dict(seed=SEED + b"-injury-00011", event_id="injury-11", _test_profile=PROFILE_2014_6)
        drive = [p["number"] for p in resolve_game(team, b, **kw)["possessions"] if p["team"] == "A"][0]
        partial = resolve_game(team, b, management_mode="user_controlled", controlled_team="A",
                               _test_onsets=force(drive, "A-WR1"), **kw)
        slots = {d["slot"]: d for d in partial["pauses"][-1]["decisions"]}
        self.assertEqual(slots["A-WR1"]["eligible"], ["A-WR4", "A-WR5", "A-WR2", "A-WR3", DEPTH_ORDER])
        self.assertEqual(slots["A-WR1"]["default_entrant"], "A-WR4")


class InputTests(unittest.TestCase):
    def test_the_family_table_follows_the_rule(self):
        data = depth_library.db_families(2014)
        players = data["players"]
        by_name = {rec["player_id"]: rec for rec in players.values()}
        # A chart corner slot settles the family over the depth chart's
        # back-filled position column (the library carried FS).
        self.assertEqual((by_name["DeAngelo Hall"]["position"], by_name["DeAngelo Hall"]["basis"]), ("CB", "chart_slot"))
        self.assertEqual(by_name["Omar Bolden"]["position"], "CB")
        # A deep-safety slot settles nothing: the weekly roster's label does.
        self.assertEqual((by_name["Da'Norris Searcy"]["position"], by_name["Da'Norris Searcy"]["basis"]),
                         ("FS", "weekly_roster"))
        johnson = next(g for g, rec in players.items() if rec["player_id"] == "Leonard Johnson")
        self.assertEqual(data["nickel"], {"TB": [johnson]})  # Tampa Bay's NKL1, the source's one nickel label
        self.assertEqual(data["outside_reserve"], {})
        self.assertEqual(data["verification"]["chart_and_weekly_disagree"], [])
        self.assertTrue(all(rec["family"] in ("corner", "safety") for rec in players.values()))
        self.assertTrue(all(rec["position"] == "CB" for rec in players.values() if rec["family"] == "corner"))
        self.assertEqual(SeasonPaths(2014).db_families, ROOT / "library/data/2014_db_families.json")
        self.assertEqual(SeasonPaths(2014).practice_squads, ROOT / "library/data/2014_inseason_rails/base.json")

    def test_relabel_changes_only_db_labels_and_the_chart_nickel(self):
        data = depth_library.db_families(2014)
        bolden = next(g for g, rec in data["players"].items() if rec["player_id"] == "Omar Bolden")
        nickel = data["nickel"]["TB"][0]
        club = {"code": "TB", "players": [
            {"player_id": "Omar Bolden", "position": "FS", "depth": 8, "gsis_id": bolden},
            {"player_id": "Leonard Johnson", "position": "CB", "depth": 3, "gsis_id": nickel},
            {"player_id": "Somebody", "position": "S", "depth": 9, "gsis_id": "90-0000001"},
            {"player_id": "A Receiver", "position": "WR", "depth": 1, "gsis_id": bolden}]}
        report = {}
        out = depth_library.relabel_defensive_backs(club, 2014, report=report)
        self.assertEqual([p["position"] for p in out["players"]], ["CB", "CB", "S", "WR"])
        self.assertEqual(out["players"][1]["roles"], ["nickel"])
        self.assertNotIn("roles", out["players"][0])
        self.assertEqual(report["unlisted"], ["Somebody"])
        self.assertEqual(report["relabelled"], [{"player_id": "Omar Bolden", "from": "FS", "to": "CB",
                                                 "basis": "chart_slot"}])
        # The nickel is the club's own chart label only.
        other = depth_library.relabel_defensive_backs(dict(club, code="DEN"), 2014)
        self.assertNotIn("roles", other["players"][1])
        self.assertEqual(club["players"][0]["position"], "FS")  # the input is not mutated

    def test_jacksonville_roles_fail_closed(self):
        chart = json.loads(CHART.read_text(encoding="utf-8"))
        errors = week_inputs.db_role_errors(chart)
        self.assertEqual(len(errors), 2)
        self.assertTrue(all("fail closed" in e for e in errors))
        good = copy.deepcopy(chart)
        good["roles"]["A.J. Bouye"] = ["nickel"]
        good["roles"]["Alan Ball"] = ["outside_reserve"]
        self.assertEqual(week_inputs.db_role_errors(good), [])
        bad = copy.deepcopy(good)
        bad["roles"]["Chris Prosinski"] = ["outside_reserve"]
        self.assertTrue(any("2 outside_reserve roles" in e for e in week_inputs.db_role_errors(bad)))
        bad = copy.deepcopy(good)
        del bad["roles"]["Alan Ball"]
        bad["roles"]["Chris Prosinski"] = ["outside_reserve"]
        self.assertTrue(any("not a corner" in e for e in week_inputs.db_role_errors(bad)))
        bad = copy.deepcopy(good)
        del bad["roles"]["A.J. Bouye"]
        bad["roles"]["Alan Ball"] = ["nickel", "outside_reserve"]
        self.assertTrue(any("same player" in e for e in week_inputs.db_role_errors(bad)))
        bad = copy.deepcopy(good)
        bad["roles"]["Kirk Cousins"] = ["passer", "nickel"]
        del bad["roles"]["A.J. Bouye"]
        self.assertTrue(any("defensive-back list" in e for e in week_inputs.db_role_errors(bad)))

    def test_the_family_table_follows_the_rails_manifest(self):
        # Review fix (October 16, 2026): a table built against another
        # in-season rails manifest is refused, with the rebuild named.
        from runtime import rails
        self.assertEqual(depth_library.db_families_errors(2014), [])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            table = SeasonPaths(2014, root).db_families
            table.parent.mkdir(parents=True)
            data = json.loads(SeasonPaths(2014).db_families.read_text(encoding="utf-8"))
            table.write_text(json.dumps(data), encoding="utf-8")
            manifest = rails.data_dir(2014, root) / "manifest.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_bytes((rails.data_dir(2014) / "manifest.json").read_bytes())
            self.assertEqual(depth_library.db_families_errors(2014, root), [])
            manifest.write_bytes(manifest.read_bytes() + b"\n")
            errors = depth_library.db_families_errors(2014, root)
        self.assertEqual(len(errors), 1)
        self.assertIn("build_2014_db_families.py", errors[0])
        self.assertEqual(data["verification"]["status_quo_nickel_seat"]["safety_at_db5_by_library_label"], 14)
        self.assertEqual(data["verification"]["status_quo_nickel_seat"]["safety_at_db5_by_family"], 10)

    def test_receipt_ids_are_never_renamed(self):
        receipts = [{"away": "X", "home": "Y", "team_stats": {"X": {"players": {"Old Name": {}}}, "Y": {"players": {}}}}]
        entries = {("k", "X"): {"players": [{"player_id": "New Name", "gsis_id": "00-0000001"}]}}
        errors = week_inputs.receipt_identity_errors(entries, receipts, {"Old Name": "00-0000001"})
        self.assertEqual(len(errors), 1)
        entries = {("k", "X"): {"players": [{"player_id": "Old Name", "gsis_id": "00-0000001"}]}}
        self.assertEqual(week_inputs.receipt_identity_errors(entries, receipts, {"Old Name": "00-0000001"}), [])


class Week5BuildTests(unittest.TestCase):
    """The Week 5 dry build under db_slots (in memory: no file is written, no
    event is closed): Jacksonville fails closed until its roles are in the
    chart; with Stone's recorded roles (Bouye nickel, Ball outside reserve)
    every club is legal and dresses 46, the background DBs take their labels
    and Weeks 1 to 4 are unchanged.

    Since the kernel 2014.6 release (B18) the build is the installed
    kernel's: the player-state model, under a stand-in for the 2014 binding
    (the bind follows the merge), and Jacksonville's two-point and kickoff
    blocks, here league delegations standing in for Stone's Week 5 rules
    (the Week 4 sheet carries none)."""

    @classmethod
    def setUpClass(cls):
        from scripts.render_season_stats import load_receipts
        paths = SeasonPaths(2014)
        cls.receipts = [r for r in load_receipts(paths.receipts) if int(r["week"]) < 5]
        sheet = json.loads((paths.week_folder(4) / "call_sheet.json").read_text(encoding="utf-8"))
        cls.args = (sheet["offensive_call_sheet"], {"offense_anchor": 2.0, "defense_anchor": 2.0,
                                                    "special_teams_anchor": 2.0}, 2014)
        cls.decisions = dict(sheet.get("decisions") or {}, two_point={"otherwise": "league"},
                             kickoff={"otherwise": "league"})
        from runtime import player_state
        cls.binding = {"schema": player_state.BINDING_SCHEMA, "league_year": 2014,
                       "manifest_sha256": player_state.manifest_sha256(), "commitment": "0" * 64}
        chart = json.loads(paths.depth_chart.read_text(encoding="utf-8"))
        chart["roles"].setdefault("A.J. Bouye", []).append("nickel")
        chart["roles"].setdefault("Alan Ball", []).append("outside_reserve")
        cls.tmp = tempfile.TemporaryDirectory()
        cls.chart = Path(cls.tmp.name) / "chart.json"
        cls.chart.write_text(json.dumps(chart), encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def build(self, week, receipts, db_slots, chart=None, **kernel):
        test = self

        class Paths(SeasonPaths):
            @property
            def depth_chart(self):
                return test.chart if chart and self.year == 2014 else super().depth_chart

        from runtime import player_state
        with mock.patch.object(week_inputs, "SeasonPaths", Paths), \
                mock.patch.object(player_state, "binding", return_value=self.binding):
            return week_inputs.build_package(week, receipts, *self.args, decisions=self.decisions, db_slots=db_slots,
                                             **kernel)

    def test_week_5(self):
        with self.assertRaisesRegex(ValueError, "W2b defensive-back roles"):
            self.build(5, self.receipts, True)
        package = self.build(5, self.receipts, True, chart=True)
        from scripts.check_week_input_exclusivity import check_inputs, controlled_players_from_roster
        self.assertEqual(check_inputs(package, controlled_players_from_roster(SeasonPaths(2014).roster), JAX,
                                      expected_games=len(package["games"])), [])
        teams = {}
        for game in package["games"]:
            for side in ("away_input", "home_input"):
                teams[game[side]["team_id"]] = game[side]
        self.assertTrue(all(len(t["active_players"]) == 46 for t in teams.values()))
        report = package["rails"]["game_day"]
        self.assertTrue(all(r["legal"] and r["dressed"] == 46 for g in report.values() for r in g.values()))
        self.assertEqual(package["rails"]["emergency"], [])
        jax = {p["player_id"]: p for p in teams[JAX]["roster"]}
        self.assertIn("nickel", jax["A.J. Bouye"]["roles"])
        self.assertIn("outside_reserve", jax["Alan Ball"]["roles"])
        tb = {p["player_id"]: p for p in teams["Tampa Bay Buccaneers"]["roster"]}
        self.assertIn("nickel", tb["Leonard Johnson"]["roles"])
        den = {p["player_id"]: p for p in teams["Denver Broncos"]["roster"]}
        self.assertEqual(den["Omar Bolden"]["position"], "CB")
        fallback = package["rails"]["depth_fallback"]
        self.assertEqual(sum(fallback["count"].values()),
                         sum(len(v) for g in fallback["players"].values() for v in g.values()))
        self.assertTrue(package["rails"]["db_slots"]["applied"])
        # Review fix (October 16, 2026): the package records the family table
        # its labels came from, and the weekly close refuses another one.
        from runtime import rails
        from scripts.close_week import rails_package_errors
        table = SeasonPaths(2014).db_families
        self.assertEqual(package["rails"]["db_slots"]["families_sha256"], rails.sha256_file(table))
        family_error = "defensive-back family table changed"
        self.assertFalse(any(family_error in e for e in rails_package_errors(package, 5, 2014)))
        stale = copy.deepcopy(package)
        stale["rails"]["db_slots"]["families_sha256"] = "0" * 64
        self.assertTrue(any(family_error in e for e in rails_package_errors(stale, 5, 2014)))
        # Without db_slots (as under kernel 2014.5) nothing is relabelled.
        plain = self.build(5, self.receipts, False)
        den = {p["player_id"]: p for g in plain["games"] for s in ("away_input", "home_input")
               if g[s]["team_id"] == "Denver Broncos" for p in g[s]["roster"]}
        self.assertEqual(den["Omar Bolden"]["position"], "FS")
        self.assertEqual(plain["rails"]["db_slots"], {"applied": False})

    def test_weeks_1_to_4_are_unchanged(self):
        # Before the rails' first week db_slots reads nothing: the background
        # clubs' inputs are the Week 1 library's either way. Jacksonville's
        # current career files describe Week 5, so its input is stubbed with
        # the frozen Week 3 unit (the stub records whether its roles were
        # required: never before Week 5).
        frozen = jacksonville_week_3()
        asked = []

        def stub(receipts, game_day, anchors, call_sheet, season=2013, decisions=None, decision_kinds=(),
                 db_roles=False):
            asked.append(db_roles)
            return {"team_id": JAX, "active_players": list(frozen.active_players), **anchors,
                    "roster": [dict(p) for p in frozen.roster], "offensive_call_sheet": list(call_sheet)}

        receipts = [r for r in self.receipts if int(r["week"]) < 4]
        # Week 4 is closed under kernel 2014.5: its package is that kernel's
        # build (the honours-production-v3 records, no decision kinds).
        closed = {"strength_model": strength.MODEL, "decision_kinds": ()}
        with mock.patch.object(week_inputs, "jacksonville_input", stub):
            on = self.build(4, receipts, True, **closed)
            off = self.build(4, receipts, False, **closed)
        self.assertEqual(json.dumps(on, sort_keys=True), json.dumps(off, sort_keys=True))
        self.assertEqual(asked, [False, False])
        self.assertNotIn("rails", on)


if __name__ == "__main__":
    unittest.main()
