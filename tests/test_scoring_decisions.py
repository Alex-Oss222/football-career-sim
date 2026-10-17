"""Kernel 2014.6 batch B9: scoring decisions.

R8 two-point tries (the league try chart, the pooled two-point rate, an
optional club decision block), R15 defensive and return touchdowns
(interception, fumble, punt return, blocked punt, blocked field goal and
kickoff returns at their sourced line-of-scrimmage shares) and R9 onside
kicks (the league onside chart, the expected and surprise recovery rates,
real onside spot records and library rule R4 in overtime), under
PROFILE_2014_6. Every number is read from the scoring artifact
(library/data/2010_2014w4_scoring_decisions.json). Forced branches use the
test-only _test_scoring hook the production runner cannot pass. Synthetic
seeds only; the private service is never contacted.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ast
import inspect
import json
import unittest
from dataclasses import replace
from unittest import mock

from runtime import gamebook, participation, play_detail, standings, usage
from runtime import scoring_decisions as sd
from runtime.calibration_base import BASE_2010_2014W4
from runtime.game_runner import build_game_packet
from runtime.kernel import resolve_game, validate_result
from runtime.play_detail import check_ledger, scoring_events
from runtime.profiles import B9_FLAGS, B9F_FLAGS, B10_FLAGS, B11_FLAGS, B13_FLAGS, PROFILE_2014_5, PROFILE_2014_6, Profile
from runtime.rules import extra_point_rule, ot_history, ot_status, try_rule
from runtime.statbook import (KERNEL_2014_6_PLAYER_FIELDS, KERNEL_2014_6_TEAM_STAT_FIELDS, aggregate_receipts,
                              make_receipt)
from synthetic_games import SEED, sample_teams
from test_profiles import strip_2014_6_fields

ROOT = Path(__file__).resolve().parents[1]
MODEL = BASE_2010_2014W4.scoring()
ART = MODEL.data
A, B = sample_teams()
PROFILE_B8 = Profile("2014.6", base=PROFILE_2014_6.base, cell_rules=PROFILE_2014_6.cell_rules,
                     strength=PROFILE_2014_6.strength, flags=PROFILE_2014_6.flags - B9_FLAGS, record_base=True)
DELEGATION = {"otherwise": "league", "source": "fixture: follow the league chart", "id": "delegation"}
# Batch B9F: a user-controlled club without a fourth-down block decides its
# fourth downs live (Stone's standing instruction). The scoring tests that
# answer only scoring pauses delegate the controlled club's fourth downs to
# the league chart, so every fourth down is decided as in the autonomous run.
FOURTH = {"fourth_down_policy": {"otherwise": "league"}}
# The B9 level of kernel 2014.6 (without the B9F live fourth downs, the B10
# ball security, the B11 penalty records and the B13 yard split): the
# seed-pinned reproductions below were found under it, and B9F changes every
# later fourth-down possession (B10 every later lost-fumble layout and
# retained kick, B11 every later drive draw and layout, B13 every later
# layout's values), so they keep reproducing at this level.
PROFILE_B9_LEVEL = Profile("2014.6", base=PROFILE_2014_6.base, cell_rules=PROFILE_2014_6.cell_rules,
                           strength=PROFILE_2014_6.strength,
                           flags=PROFILE_2014_6.flags - B9F_FLAGS - B10_FLAGS - B11_FLAGS - B13_FLAGS,
                           record_base=True)
WEEK4_SHEET = ROOT / "career/2014/05_Regular_Season/Games/Week_04/call_sheet.json"
SCORING_SOURCES = set(sd.SOURCES)


def play(name, forced=None, home=A, away=B, profile=PROFILE_2014_6, **kw):
    return resolve_game(home, away, seed=SEED + b"-" + name.encode(), event_id=name, _test_profile=profile,
                        _test_scoring=forced, **kw)


def receipt(result, detail="compact_stats"):
    return make_receipt(result, week=5, matchup="%s at %s" % (sorted(result["final_score"])[1],
                                                               sorted(result["final_score"])[0]), detail=detail)


def clean(result):
    """The result and both receipt details validate and audit clean."""
    return (validate_result(result) + check_ledger(result) + check_ledger(receipt(result, "full"))
            + check_ledger(receipt(result)))


def other(team_id):
    return "B" if team_id == "A" else "A"


def all_tries(result):
    """(scorer, try record, state) for every try of a result."""
    out = []
    for p in result["possessions"]:
        if p.get("try"):
            out.append((p["team"], p["try"]))
        non_offensive = p.get("non_offensive_score") or {}
        if non_offensive.get("try"):
            out.append((non_offensive["team"], non_offensive["try"]))
    out += [(k["receiving"], k["try"]) for k in result["kickoffs"] if k.get("try")]
    return out


def first(seq, pred, what):
    for item in seq:
        if pred(item):
            return item
    raise AssertionError("no synthetic game with %s" % what)


def with_team(name, decisions=None, sheet=None):
    """A synthetic club with decision blocks (and a call sheet)."""
    base = A if name == "A" else B
    fields = {}
    if decisions:
        fields.update(decisions)
    if sheet is not None:
        fields["offensive_call_sheet"] = tuple(sheet)
    return replace(base, **fields)


# ---- the artifact and the state map --------------------------------------------------------------------

class ChartTests(unittest.TestCase):
    def test_every_chart_cell_reproduces_its_counts(self):
        t = ART["try"]
        sums = {}
        for raw, cell in t["decision_cell_map"].items():
            k, n = t["raw_cells"].get(raw, [0, 0])
            acc = sums.setdefault(cell, [0, 0])
            acc[0] += k
            acc[1] += n
        for cell, entry in t["decision_chart"].items():
            self.assertEqual(sums[cell], [entry["go"], entry["tries"]], cell)
            self.assertEqual(MODEL.p_go(cell), (entry["go"], entry["tries"]))
        self.assertEqual(sum(n for _, n in t["tries_by_season"].values()), sum(e["tries"] for e in t["decision_chart"].values()))
        for cell, pair in ART["onside"]["decision_chart"].items():
            self.assertEqual(MODEL.p_onside(cell), tuple(pair))
        self.assertEqual(MODEL.two_point, tuple(ART["two_point_success"]["pooled"]))
        self.assertEqual({k: len(v) for k, v in MODEL.spot_records.items()},
                         {k: len(v) for k, v in ART["onside"]["spot_records_from_35"].items()})
        self.assertEqual(MODEL.kick_chain_cap, 8)

    def test_every_binned_unit_partitions_its_pooled_units(self):
        # The lost-fumble bins are keyed by the fumbled snap's line of
        # scrimmage (the specification's return_td_los_bins), so every unit
        # is binned; a key that drops units (the fumble spot, off the field
        # on an end-zone strip-sack) is refused by the model.
        n = ART["non_offensive"]
        for unit in ("interception", "fumble_lost", "punt"):
            bins = n[unit]["los_bins"]
            self.assertTrue(n[unit]["bins_adopted"], unit)
            self.assertEqual([sum(v[0] for v in bins.values()), sum(v[1] for v in bins.values())],
                             list(n[unit]["pooled"]), unit)
        self.assertEqual(n["fumble_lost"]["los_bins"], {"1-20": [4, 151], "21-40": [13, 189], "41-60": [13, 307],
                                                        "61-80": [35, 396], "81-99": [28, 123]})
        broken = json.loads(json.dumps(ART))
        broken["non_offensive"]["fumble_lost"]["los_bins"]["81-99"] = [23, 147]
        with self.assertRaisesRegex(sd.ScoringModelError, "fumble_lost line-of-scrimmage bins"):
            sd.model_from(broken)

    def test_every_feasible_pick_six_record_stays_on_the_field(self):
        # Review round 2: a record is feasible from a line of scrimmage only
        # when its interception spot (LOS - air yards) lies between the
        # passer's 1 and the back line, so every drawn return covers 1 to 109
        # yards. Before the near-side bound, LOS 91-99 kept 1 to 6 records of
        # the 81-99 bin whose return was 0 or negative (-7 at LOS 98).
        low, high = sd.RETURN_TD_YARDS
        for los in range(1, 100):
            records = MODEL.interception_records(los)
            self.assertTrue(records, los)
            for r in records:
                self.assertTrue(low <= 100 - (los - r["air_yards"]) <= high, (los, r))
        self.assertEqual(len(MODEL.interception_records(98)), 44)
        # An artifact with a line that has no feasible record is refused at
        # load (here the 81-99 bin without its air yards of 0 or more).
        broken = json.loads(json.dumps(ART))
        recs = broken["non_offensive"]["records"]
        fields = recs["fields"]["interception_return_td"]
        at_bin, at_air = fields.index("los_bin"), fields.index("air_yards")
        recs["interception_return_td"] = [r for r in recs["interception_return_td"]
                                          if not (r[at_bin] == "81-99" and r[at_air] >= 0)]
        with self.assertRaisesRegex(sd.ScoringModelError, "feasible from line of scrimmage 99"):
            sd.model_from(broken)

    def test_try_state_boundaries(self):
        cmap = ART["try"]["decision_cell_map"]
        for seconds, label in ((10 ** 4, "Q1-Q3"), (901, "Q1-Q3"), (900, "Q4 900-601"), (601, "Q4 900-601"),
                               (600, "Q4 600-301"), (301, "Q4 600-301"), (300, "Q4 300-121"),
                               (121, "Q4 300-121"), (120, "Q4 120-0"), (0, "Q4 120-0")):
            for diff, key in ((-2, "-2"), (15, "+15"), (16, ">=16"), (40, ">=16"), (-15, "-15"), (-16, "<=-16"),
                              (0, "+0")):
                self.assertEqual(MODEL.try_cell(seconds, diff), cmap["%s|%s" % (label, key)], (seconds, diff))
        self.assertEqual(sd.try_seconds(4, "0:00"), 0)
        self.assertEqual(sd.try_seconds(1, "15:00"), 3600)
        self.assertEqual(sd.try_seconds(3, "2:05"), 1025)

    def test_onside_state_boundaries(self):
        cell = MODEL.onside_cell
        self.assertEqual(cell(seconds_left=901, period=3, overtime=False, opening=False, diff=0), "Q1-Q3|tied")
        self.assertEqual(cell(seconds_left=900, period=4, overtime=False, opening=False, diff=-1), "Q4 900-301|trail 1-3")
        self.assertEqual(cell(seconds_left=301, period=4, overtime=False, opening=False, diff=-4), "Q4 900-301|trail 4-8")
        self.assertEqual(cell(seconds_left=300, period=4, overtime=False, opening=False, diff=-8), "Q4 300-121|trail 4-8")
        self.assertEqual(cell(seconds_left=120, period=4, overtime=False, opening=False, diff=-9), "Q4 120-0|trail 9-16")
        self.assertEqual(cell(seconds_left=121, period=4, overtime=False, opening=False, diff=-17), "Q4 300-121|trail 17+")
        self.assertEqual(cell(seconds_left=1800, period=3, overtime=False, opening=True, diff=3), "opening|lead 1+")
        # The overtime opener uses the opening cell (default 1B.8); a later
        # overtime kick the overtime cell.
        self.assertEqual(cell(seconds_left=600, period=None, overtime=True, opening=True, diff=0), "opening|tied")
        self.assertEqual(cell(seconds_left=400, period=None, overtime=True, opening=False, diff=3), "OT|lead 1+")

    def test_recovery_classes(self):
        rc = MODEL.recovery_class
        self.assertEqual(rc(seconds_left=300, period=4, overtime=False, diff=-1), "expected")
        self.assertEqual(rc(seconds_left=301, period=4, overtime=False, diff=-1), "surprise")
        self.assertEqual(rc(seconds_left=100, period=4, overtime=False, diff=0), "surprise")
        self.assertEqual(rc(seconds_left=100, period=3, overtime=False, diff=-5), "surprise")
        self.assertEqual(rc(seconds_left=100, period=None, overtime=True, diff=-3), "surprise")
        self.assertEqual(MODEL.p_recover("expected"), 18 / 163)
        self.assertEqual(MODEL.p_recover("surprise"), ART["onside"]["recovery"]["surprise"][0]
                         / ART["onside"]["recovery"]["surprise"][1])


class PurityTests(unittest.TestCase):
    def test_no_club_identity_is_read(self):
        self.assertEqual(list(inspect.signature(sd.decide).parameters), ["policy", "kind", "state", "u", "chart_pair"])
        tree = ast.parse(Path(sd.__file__).read_text(encoding="utf-8"))
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        names |= {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        names |= {n.arg for n in ast.walk(tree) if isinstance(n, ast.arg)}
        self.assertFalse({"team_id", "controlled_team"} & names)
        strings = {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
        self.assertFalse({"team_id", "controlled_team"} & strings)
        for tag in (sd.TRY_TAG, sd.KICK_TAG, sd.RETURN_TAG, sd.TRY_DETAIL_TAG):
            self.assertTrue(tag.endswith("-v1"))


# ---- policies ----------------------------------------------------------------------------------------------

GO_LATE = {"id": "go-late", "source": "fixture", "otherwise": "kick",
           "rules": [{"when": {"period": [4], "diff_after_td": [-2, -5, -10]}, "decision": "go"},
                     {"when": {"period": [1, 2, 3], "diff_after_td": {"min": 16}}, "decision": "go"}]}
ONSIDE_LATE = {"otherwise": "deep",
               "rules": [{"when": {"period": [4], "diff_after_score": {"min": -16, "max": -1},
                                   "game_seconds_max": 300}, "decision": "onside"}]}


class PolicyValidationTests(unittest.TestCase):
    def test_frequency_unknown_and_missing_keys_are_rejected(self):
        bad = [
            ({"otherwise": "league", "go_rate": 0.5}, "two_point"),
            ({"otherwise": "league", "rules": [{"when": {"period": [4]}, "decision": "go", "share": 1}]}, "two_point"),
            ({"otherwise": "league", "rules": [{"when": {"period": [4], "probability": 1}, "decision": "go"}]},
             "two_point"),
            ({"otherwise": "league", "rules": [{"when": {"quarter": [4]}, "decision": "go"}]}, "two_point"),
            ({"otherwise": "league", "colour": "teal"}, "two_point"),
            ({"rules": []}, "two_point"),
            ({}, "two_point"),
            ({"otherwise": "maybe"}, "two_point"),
            ({"otherwise": "league", "rules": [{"when": {"period": ["OT"]}, "decision": "go"}]}, "two_point"),
            ({"otherwise": "league", "rules": [{"when": {"period": [4]}, "decision": "onside"}]}, "two_point"),
            ({"otherwise": "league", "rules": [{"when": {}, "decision": "go"}]}, "two_point"),
            ({"otherwise": "league", "rules": [{"when": {"opening_kick": 1}, "decision": "deep"}]}, "kickoff"),
            ({"otherwise": "go"}, "kickoff"),
        ]
        for block, kind in bad:
            self.assertTrue(sd.policy_errors(block, kind), block)
        for block, kind in ((GO_LATE, "two_point"), (ONSIDE_LATE, "kickoff"), (DELEGATION, "two_point"),
                            ({"otherwise": "ask"}, "kickoff"),
                            ({"otherwise": "deep", "rules": [{"when": {"period": ["OT"], "opening_kick": True},
                                                              "decision": "onside"}]}, "kickoff")):
            self.assertEqual(sd.policy_errors(block, kind), [], block)
        self.assertTrue(sd.sheet_errors({"three_point": DELEGATION}))
        self.assertTrue(sd.sheet_errors({}))
        self.assertEqual(sd.sheet_errors(None), [])

    def test_rewording_text_leaves_the_packet_identical(self):
        def legal(t):  # the synthetic clubs dress 47; the packet builder admits 46
            return replace(t, active_players=tuple(pid for pid in t.active_players if not pid.endswith("-CB5")))
        a1 = with_team("A", {"try_policy": GO_LATE})
        a2 = with_team("A", {"try_policy": dict(GO_LATE, id="renamed", source="another wording")})
        a3 = with_team("A", {"try_policy": dict(GO_LATE, rules=[dict(GO_LATE["rules"][0],
                                                                     when={"period": [4], "diff_after_td": [-2]})])})
        p1 = build_game_packet("pk", "snapshot", legal(a1), legal(B))
        self.assertEqual(p1, build_game_packet("pk", "snapshot", legal(a2), legal(B)))
        self.assertNotEqual(p1, build_game_packet("pk", "snapshot", legal(a3), legal(B)))
        self.assertNotIn("source", json.dumps(p1["home"]["try_policy"]))
        self.assertNotIn("try_policy", build_game_packet("pk", "snapshot", legal(A), legal(B))["home"])
        # The kernel's own packet strips through the same function.
        r1, r2 = play("pk-word", home=a1), play("pk-word", home=a2)
        r1.pop("decision_policies"), r2.pop("decision_policies")
        self.assertEqual(r1, r2)

    def test_blocks_fail_closed(self):
        def legal(t):
            return replace(t, active_players=tuple(pid for pid in t.active_players if not pid.endswith("-CB5")))
        with self.assertRaisesRegex(ValueError, "decision block"):
            build_game_packet("pk", "snapshot", legal(with_team("A", {"try_policy": {"otherwise": "league",
                                                                                     "rate": 1}})), legal(B))
        with self.assertRaisesRegex(ValueError, "decision block"):
            build_game_packet("pk", "snapshot", legal(with_team("A", {"try_policy": DELEGATION})), legal(B),
                              game_type="preseason", game_date="2014-08-09")
        with self.assertRaises(ValueError):
            play("pk-pre", home=with_team("A", {"try_policy": DELEGATION}), game_type="preseason",
                 game_date="2014-08-09")
        with self.assertRaises(ValueError):
            play("pk-pb", home=with_team("A", {"kickoff_policy": DELEGATION}), game_type="pro_bowl")
        with self.assertRaises(ValueError):
            play("pk-b8", home=with_team("A", {"try_policy": DELEGATION}), profile=PROFILE_B8)
        with self.assertRaises(ValueError):
            play("pk-empty", home=with_team("A", {"try_policy": {}}))

    def test_u6_fails_closed_for_the_controlled_club(self):
        with self.assertRaisesRegex(ValueError, "U6"):
            play("u6-none", management_mode="user_controlled", controlled_team="A")
        with self.assertRaisesRegex(ValueError, "U6"):
            play("u6-half", home=with_team("A", {"try_policy": DELEGATION}), management_mode="user_controlled",
                 controlled_team="A")
        # The other club needs none; 2014.5 decides none.
        a = with_team("A", {"try_policy": DELEGATION, "kickoff_policy": DELEGATION, **FOURTH})
        r = play("u6-ok", home=a, management_mode="user_controlled", controlled_team="A")
        self.assertTrue(r["terminated"])
        self.assertTrue(all(t["basis"] == "delegated:league" for club, t in all_tries(r) if club == "A"))
        self.assertTrue(all(t["basis"] == "league" for club, t in all_tries(r) if club == "B"))
        resolve_game(A, B, seed=SEED + b"-u6-old", event_id="u6-old", management_mode="user_controlled",
                     controlled_team="A", _test_profile=PROFILE_2014_5)

    def test_week_inputs_fail_closed_without_a_block(self):
        kinds = sd.profile_kinds(PROFILE_2014_6)
        self.assertEqual(kinds, ("two_point", "kickoff"))
        self.assertEqual(sd.profile_kinds(PROFILE_2014_5), ())
        self.assertEqual(sd.kernel_kinds("2014.5"), ())
        self.assertEqual(sd.kernel_kinds("2013.4"), ())
        with self.assertRaisesRegex(ValueError, "U6"):
            sd.input_policies(None, kinds)
        with self.assertRaisesRegex(ValueError, "U6"):
            sd.input_policies({"two_point": DELEGATION}, kinds)
        with self.assertRaises(ValueError):
            sd.input_policies({"two_point": DELEGATION}, ())
        with self.assertRaises(ValueError):
            sd.input_policies({"two_point": {"otherwise": "league", "odds": 2}, "kickoff": DELEGATION}, kinds)
        self.assertEqual(sd.input_policies({"two_point": GO_LATE, "kickoff": ONSIDE_LATE}, kinds),
                         {"try_policy": GO_LATE, "kickoff_policy": ONSIDE_LATE})
        self.assertEqual(sd.input_policies(None, ()), {})

    def test_build_week_inputs_blocks_jacksonville_without_a_block(self):
        from datetime import date
        from runtime import week_inputs
        sheet = json.loads(WEEK4_SHEET.read_text(encoding="utf-8"))
        kinds = sd.profile_kinds(PROFILE_2014_6)
        with self.assertRaisesRegex(ValueError, "U6"):
            week_inputs.jacksonville_input([], date(2014, 9, 28), {}, sheet["offensive_call_sheet"], 2014,
                                           decision_kinds=kinds)
        with mock.patch.object(week_inputs, "controlled_active", return_value=[]), \
                mock.patch.object(week_inputs, "injured_out", return_value=set()):
            data = week_inputs.jacksonville_input([], date(2014, 9, 28), {}, sheet["offensive_call_sheet"], 2014,
                                                  decisions={"two_point": GO_LATE, "kickoff": DELEGATION},
                                                  decision_kinds=kinds)
        self.assertEqual((data["try_policy"], data["kickoff_policy"]), (GO_LATE, DELEGATION))


class DecideTests(unittest.TestCase):
    def test_rules_delegation_and_the_chart(self):
        pair = (1, 4)
        state = {"period": 4, "diff": -2, "seconds": 100}
        self.assertEqual(sd.decide(GO_LATE, "two_point", state, 0.99, pair), ("go", "policy:0"))
        self.assertEqual(sd.decide(GO_LATE, "two_point", dict(state, diff=-3), 0.0, pair), ("kick", "policy:2"))
        self.assertEqual(sd.decide(GO_LATE, "two_point", dict(state, period=2, diff=20), 0.99, pair),
                         ("go", "policy:1"))
        self.assertEqual(sd.decide(DELEGATION, "two_point", state, 0.2, pair), ("go", "delegated:league"))
        self.assertEqual(sd.decide(DELEGATION, "two_point", state, 0.25, pair), ("kick", "delegated:league"))
        self.assertEqual(sd.decide(None, "two_point", state, 0.2, pair), ("go", "league"))
        self.assertEqual(sd.decide({"otherwise": "ask"}, "kickoff", state, 0.0, pair), (None, "live"))
        kick_state = {"period": 4, "diff": -4, "seconds": 250, "opening": False}
        self.assertEqual(sd.decide(ONSIDE_LATE, "kickoff", kick_state, 0.99, (0, 9)), ("onside", "policy:0"))
        self.assertEqual(sd.decide(ONSIDE_LATE, "kickoff", dict(kick_state, seconds=400), 0.0, (9, 9)),
                         ("deep", "policy:1"))
        opening = {"otherwise": "deep", "rules": [{"when": {"period": ["OT"], "opening_kick": True},
                                                   "decision": "onside"}]}
        self.assertEqual(sd.decide(opening, "kickoff", {"period": "OT", "diff": 0, "seconds": 600, "opening": True},
                                   0.99, (0, 1)), ("onside", "policy:0"))


class NoBonusTests(unittest.TestCase):
    def test_sockets_are_inert_at_slope_zero(self):
        self.assertTrue(all(v == 0.0 for v in sd.SOCKETS.values()))
        self.assertEqual(MODEL.two_point_success(), 115 / 232)
        for edge in (-3.0, 0.0, 0.7, 5.0):
            self.assertEqual(MODEL.two_point_success(edge), 115 / 232)
        pair = MODEL.return_rate("interception", 70)
        self.assertEqual(MODEL.p_return(pair, returner=4.0, coverage=-2.0), pair[0] / pair[1])
        self.assertEqual(MODEL.p_blocked(MODEL.missed_fg, protection=3.0, rush=3.0), 5 / 678)
        for label in ("expected", "surprise"):
            k, n = MODEL.recovery[label]
            self.assertEqual(MODEL.p_recover(label, kicking_unit=2.0, hands_unit=-2.0), k / n)

    def test_each_socket_moves_the_declared_way_when_patched(self):
        pair = MODEL.return_rate("punt", 70)
        base = pair[0] / pair[1]
        with mock.patch.dict(sd.SOCKETS, {"two_point_edge": 0.05}):
            self.assertGreater(MODEL.two_point_success(1.0), 115 / 232)
            self.assertLess(MODEL.two_point_success(-1.0), 115 / 232)
        with mock.patch.dict(sd.SOCKETS, {"returner": 0.001, "coverage": 0.001}):
            self.assertGreater(MODEL.p_return(pair, returner=1.0), base)
            self.assertLess(MODEL.p_return(pair, coverage=1.0), base)
        k, n = MODEL.recovery["surprise"]
        with mock.patch.dict(sd.SOCKETS, {"onside_kicking_unit": 0.01, "onside_hands_unit": 0.01}):
            self.assertGreater(MODEL.p_recover("surprise", kicking_unit=1.0), k / n)
            self.assertLess(MODEL.p_recover("surprise", hands_unit=1.0), k / n)
        with mock.patch.dict(sd.SOCKETS, {"blocked_kick_protection": 0.001, "blocked_kick_rush": 0.001}):
            self.assertLess(MODEL.p_blocked(MODEL.missed_fg, protection=1.0), 5 / 678)
            self.assertGreater(MODEL.p_blocked(MODEL.missed_fg, rush=1.0), 5 / 678)


# ---- the kernel ---------------------------------------------------------------------------------------------

class KernelExactTests(unittest.TestCase):
    def test_controlled_club_and_mode_change_nothing(self):
        a = with_team("A", {"try_policy": DELEGATION, "kickoff_policy": DELEGATION, **FOURTH})
        b = with_team("B", {"try_policy": DELEGATION, "kickoff_policy": DELEGATION, **FOURTH})
        compared = 0
        for i in range(8):
            name = "exact-%d" % i
            auto = play(name, home=a, away=b)
            home = play(name, home=a, away=b, management_mode="user_controlled", controlled_team="A")
            away = play(name, home=a, away=b, management_mode="user_controlled", controlled_team="B")
            if not (home.get("terminated") and away.get("terminated")):
                continue  # an E2 substitution pause (a consequential removal), not a scoring decision
            self.assertEqual(auto, home)
            self.assertEqual(auto, away)
            compared += 1
        self.assertGreater(compared, 2)

    def test_policy_compliance_and_symmetry(self):
        a = with_team("A", {"try_policy": GO_LATE, "kickoff_policy": ONSIDE_LATE})
        b = with_team("B", {"try_policy": GO_LATE, "kickoff_policy": ONSIDE_LATE})
        seen = {"A": 0, "B": 0}
        for i in range(12):
            r = play("comply-%d" % i, home=a, away=b)
            self.assertEqual(clean(r), [])
            for club, t in all_tries(r):
                seen[club] += 1
                self.assertTrue(t["basis"].startswith("policy:"), t)
                self.assertEqual(t["decision"], "go" if t["basis"] in ("policy:0", "policy:1") else "kick")
            for k in r["kickoffs"]:
                if k.get("onside") is not None:
                    self.assertTrue(k["basis"].startswith("policy:"))
                    self.assertEqual(k["onside"], k["basis"] == "policy:0")
                    if k["onside"]:
                        self.assertEqual((k["half"], k["remaining"] <= 300), (2, True))
        self.assertTrue(seen["A"] and seen["B"])

    def test_policy_never_shifts_a_draw_of_its_game(self):
        # Delegating to the chart decides exactly as the chart: the same
        # packet minus the block is a different packet (another stream), but
        # the decision function is the same, so the try decisions of a
        # delegated club reproduce the chart's from the same uniforms.
        for i in range(6):
            r = play("deleg-%d" % i, home=with_team("A", {"try_policy": DELEGATION}))
            for club, t in all_tries(r):
                self.assertEqual(t["basis"], "delegated:league" if club == "A" else "league")
                self.assertEqual(t["p_go"], list(MODEL.p_go(t["cell"])))


class ForcedCaseTests(unittest.TestCase):
    """Every forced R15/R9/R8 case, clean on the result and on both receipts."""

    @classmethod
    def setUpClass(cls):
        cls.name = "b9-forced-1"
        cls.base = play(cls.name)

    def force(self, forced, **kw):
        r = play(self.name, forced, **kw)
        self.assertEqual(clean(r), [])
        self.assertEqual(scoring_events(receipt(r)), r["scoring_events"])
        self.assertEqual(sum(e["points"] for e in r["scoring_events"]), sum(r["final_score"].values()))
        return r

    def drives(self, *categories, result=None):
        result = result or self.base
        return [p for p in result["possessions"] if p["category"] in categories and p is not result["possessions"][-1]
                and p["half"] in (1, 2)]

    def test_pick_six_mid_half(self):
        p = first(self.drives("interception"), lambda p: not p["half_final"], "a mid-half interception")
        r = self.force({"drives": {p["number"]: "defensive_touchdown"}})
        q = r["possessions"][p["number"] - 1]
        score = q["non_offensive_score"]
        defense = other(q["team"])
        self.assertEqual((score["team"], score["source"]), (defense, "interception"))
        self.assertIn(score["points"], (6, 7, 8))
        self.assertEqual(score["try"]["points"], score["points"] - 6)
        kick = next(k for k in r["kickoffs"] if k["after_drive"] == q["number"])
        self.assertEqual((kick["kicking"], kick["receiving"]), (defense, q["team"]))
        # The touchdown publishes no start of its own: continuity is the
        # scorer's kickoff (kickoff_after), and the original offense receives.
        self.assertEqual((q["next_start"], q["kickoff_after"]["next_start"]), (kick["next_start"], kick["next_start"]))
        self.assertEqual(r["possessions"][q["number"]]["team"], q["team"])
        row = [x for x in r["play_ledger"] if x["drive"] == q["number"] and x["play_type"] in ("pass", "run")][-1]
        self.assertTrue(row["touchdown"] and row["turnover"])
        self.assertEqual((row["scoring_team"], row["return_yards"]), (defense, score["return_yards"]))
        line = r["team_stats"][defense]["players"][row["tackler"]]
        self.assertEqual(line["interception_return_touchdowns"], 1)
        self.assertEqual(line["interception_return_yards"], score["return_yards"])
        self.assertEqual(r["team_stats"][defense]["defensive_touchdowns"], 1)
        # The turnover row's touchdown is the defense's: it is never the
        # offense's call touchdown (the counter reads the row before the
        # kernel marks it) nor a touchdown marker of the drive.
        offense = q["team"]
        call_tds = sum(c["touchdowns"] for c in r["play_call_stats"][offense].values())
        own_tds = sum(1 for x in r["play_ledger"] if x["offense"] == offense and x["play_type"] in ("pass", "run")
                      and x.get("touchdown") and not x.get("turnover"))
        self.assertEqual(call_tds, own_tds)

    def test_pick_six_from_inside_the_passers_ten_covers_the_field(self):
        # Review round 2 reproduction: p6-1509, drive 20 is an interception
        # thrown from the passer's own 2 (LOS 98). Before the near-side bound
        # its forced pick-six drew a record returned -7 yards; now the return
        # is a feasible 1 to 109 yards, credited to the interceptor.
        r = resolve_game(A, B, seed=SEED + b"p6-1509", event_id="p6-1509", _test_profile=PROFILE_B9_LEVEL,
                         _test_scoring={"drives": {20: "defensive_touchdown"}})
        self.assertEqual(clean(r), [])
        q = r["possessions"][19]
        self.assertEqual((q["category"], q["end_spot"], q["non_offensive_score"]["source"]),
                         ("interception", 98, "interception"))
        low, high = sd.RETURN_TD_YARDS
        self.assertTrue(low <= q["non_offensive_score"]["return_yards"] <= high)
        row = [x for x in r["play_ledger"] if x["drive"] == 20 and x["play_type"] in ("pass", "run")][-1]
        line = r["team_stats"][other(q["team"])]["players"][row["tackler"]]
        self.assertEqual(line["interception_return_yards"], q["non_offensive_score"]["return_yards"])

    def test_a_return_touchdown_off_the_field_is_refused(self):
        # validate_result and check_ledger (result, full and compact
        # receipts) refuse a return touchdown that covers under 1 yard, the
        # defense's and a kick's alike.
        p = first(self.drives("interception"), lambda p: not p["half_final"], "a mid-half interception")
        r = self.force({"drives": {p["number"]: "defensive_touchdown"}})
        r["possessions"][p["number"] - 1]["non_offensive_score"]["return_yards"] = -7
        self.assertIn("return touchdown distance outside 1-109 yards", validate_result(r))
        for audited in (r, receipt(r, "full"), receipt(r)):
            self.assertTrue(any(e.startswith("score_identity_violations") and "covers -7 yards" in e
                                for e in check_ledger(audited)))
        row = [x for x in r["play_ledger"] if x["drive"] == p["number"] and x["play_type"] in ("pass", "run")][-1]
        r["possessions"][p["number"] - 1]["non_offensive_score"]["return_yards"] = 50
        row["return_yards"] = 0
        self.assertIn("return touchdown distance outside 1-109 yards", validate_result(r))
        self.assertTrue(any("touchdown row covers 0 yards" in e for e in check_ledger(r)))
        k = first(self.base["kickoffs"], lambda k: not k["free_kick"] and k.get("onside") is False, "a deep kickoff")
        kicked = self.force({"kicks": {k["kick_no"]: "touchdown"}})
        kick = kicked["kickoffs"][k["kick_no"] - 1]
        self.assertEqual(kick["outcome"], "returned_touchdown")
        kick["return_yards"] = 0
        self.assertIn("return touchdown distance outside 1-109 yards", validate_result(kicked))
        self.assertTrue(any("kick %d return touchdown covers 0 yards" % k["kick_no"] in e
                            for e in check_ledger(kicked)))

    def test_fumble_return_keyed_by_the_fumbled_snap(self):
        # b9-seek-0, drive 7: a lost fumble (found by search; fails loudly if
        # not; re-searched for batch B11, which moves every later drive).
        base = play("b9-seek-0")
        p = base["possessions"][6]
        self.assertEqual(p["category"], "fumble_lost")
        r = play("b9-seek-0", {"drives": {p["number"]: "defensive_touchdown"}})
        self.assertEqual(clean(r), [])
        q = r["possessions"][p["number"] - 1]
        self.assertEqual(q["non_offensive_score"]["source"], "fumble")
        self.assertEqual(q["non_offensive_score"]["return_yards"], 100 - q["end_spot"])
        row = [x for x in r["play_ledger"] if x["drive"] == q["number"] and x["play_type"] in ("pass", "run")][-1]
        self.assertEqual(row["yardline"], q["end_spot"] + row["result_yards"])
        # Batch B10: the return touchdown is the recoverer's (the fumble
        # record's), a credit separate from the forcer's tackle.
        scorer = row["fumble"]["recovered_by"]
        self.assertEqual(row["fumble"]["recovering_team"], other(q["team"]))
        self.assertEqual(r["team_stats"][other(q["team"])]["players"][scorer]["fumble_return_touchdowns"], 1)

    def test_fumble_rate_reads_the_bin_of_the_fumbled_snaps_line(self):
        # b9-seek-14, drive 7: a lost fumble snapped from the 84 (bin 81-99)
        # whose spot is the 78 (bin 61-80), found by search. Every lost
        # fumble's rate lookup takes the fumbled row's own line of scrimmage,
        # and the 81-99 lookup reads the artifact's 81-99 counts (bins keyed
        # by that line since the round-1 review; never the fumble spot).
        calls = []
        original = sd.ScoringModel.return_rate

        def spy(model, unit, los):
            pair = original(model, unit, los)
            calls.append((unit, int(los), pair))
            return pair

        with mock.patch.object(sd.ScoringModel, "return_rate", spy):
            r = play("b9-seek-14", profile=PROFILE_B9_LEVEL)
        fumbled = []
        for p in r["possessions"]:
            if p["category"] == "fumble_lost":
                row = [x for x in r["play_ledger"] if x["drive"] == p["number"] and x["play_type"] in ("pass", "run")][-1]
                fumbled.append((row["yardline"], p["end_spot"]))
        self.assertIn((84, 78), fumbled)
        self.assertEqual([los for unit, los, _ in calls if unit == "fumble_lost"], [los for los, _ in fumbled])
        bins = ART["non_offensive"]["fumble_lost"]["los_bins"]
        self.assertIn(("fumble_lost", 84, tuple(bins["81-99"])), calls)
        self.assertNotEqual(bins["81-99"], bins["61-80"])

    def test_punt_return_and_blocked_punt(self):
        p = first(self.drives("punt"), lambda p: True, "a punt")
        r = self.force({"drives": {p["number"]: "punt_return_td"}})
        q = r["possessions"][p["number"] - 1]
        row = next(x for x in r["play_ledger"] if x["drive"] == q["number"] and x["play_type"] == "punt")
        self.assertEqual(row["outcome"], play_detail.PUNT_RETURN_TD)
        # The return covers the punt to the goal line: 100 - LOS + gross.
        self.assertEqual(row["return_yards"], 100 - q["end_spot"] + row["gross"])
        defense = other(q["team"])
        self.assertEqual(r["team_stats"][defense]["players"][row["returner"]]["punt_return_touchdowns"], 1)
        self.assertGreaterEqual(r["team_stats"][q["team"]]["players"][row["punter"]]["punts"], 1)
        self.assertIsNone(row["cover_player"])
        r = self.force({"drives": {p["number"]: "blocked_punt_td"}})
        q = r["possessions"][p["number"] - 1]
        row = next(x for x in r["play_ledger"] if x["drive"] == q["number"] and x["play_type"] == "punt")
        self.assertEqual((row["outcome"], row["gross"], row["blocked"], row["attribution"]),
                         (play_detail.PUNT_BLOCKED_TD, 0, True, sd.GROUP_DRAW))
        self.assertEqual(row["return_yards"], 100 - q["end_spot"])
        self.assertEqual(r["team_stats"][other(q["team"])]["players"][row["scorer"]]["blocked_kick_touchdowns"], 1)

    def test_blocked_field_goal(self):
        for i in range(40):
            name = "b9-fg-%d" % i
            g = play(name)
            miss = [p for p in g["possessions"] if p["category"] == "field_goal_attempt" and not p["fg_made"]
                    and p is not g["possessions"][-1]]
            if miss:
                break
        else:
            self.fail("no missed field goal")
        r = play(name, {"drives": {miss[0]["number"]: "blocked_fg_td"}})
        self.assertEqual(clean(r), [])
        q = r["possessions"][miss[0]["number"] - 1]
        kick = next(k for k in r["kickoffs"] if k["after_drive"] == q["number"])
        self.assertEqual(q["non_offensive_score"]["source"], "blocked_field_goal")
        # No missed-field-goal start: the blocking club kicks off.
        self.assertEqual((q["next_start"], kick["kicking"]), (kick["next_start"], other(q["team"])))
        row = next(x for x in r["play_ledger"] if x["drive"] == q["number"] and x["play_type"] == "field_goal")
        self.assertTrue(row["touchdown"] and row["blocked"] and not row["made"])

    def test_kick_return_touchdowns_on_both_openers_and_twice(self):
        h2 = next(k["kick_no"] for k in self.base["kickoffs"] if k["half"] == 2 and k["after_drive"] is None)
        for forced in ({1: "touchdown"}, {h2: "touchdown"}, {1: "touchdown", 2: "touchdown"}):
            r = self.force({"kicks": forced})
            for kick_no in forced:
                k = r["kickoffs"][kick_no - 1]
                self.assertEqual((k["outcome"], k["next_start"]), ("returned_touchdown", None))
                row = next(x for x in r["play_ledger"] if x["play_type"] == "kickoff" and x["drive"] == k["drive"]
                           and x["touchdown"] and x["scoring_team"] == k["receiving"])
                self.assertEqual(row["return_yards"], 35 + k["kick_yards"])
                self.assertGreaterEqual(r["team_stats"][k["receiving"]]["players"][row["returner"]]
                                        ["kick_return_touchdowns"], 1)
                self.assertEqual(r["kickoffs"][kick_no]["kicking"], k["receiving"])
            h2_kick = next(k for k in r["kickoffs"] if k["half"] == 2 and k["after_drive"] is None)
            self.assertEqual(h2_kick["kicking"], r["opening_receiver"])

    def test_onside_recoveries_on_both_openers(self):
        h2 = next(k["kick_no"] for k in self.base["kickoffs"] if k["half"] == 2 and k["after_drive"] is None)
        pools = {side: {int(x["next_start"]) for x in MODEL.spot_records[side]} for side in ("kicking", "receiving")}
        for kick_no in (1, h2):
            for branch, side in (("onside_recovered", "kicking"), ("onside_lost", "receiving")):
                r = self.force({"kicks": {kick_no: branch}})
                k = r["kickoffs"][kick_no - 1]
                self.assertTrue(k["onside"])
                self.assertEqual(k["outcome"], branch)
                self.assertIn(k["next_start"], pools[side])
                nxt = next(p for p in r["possessions"] if p["number"] == k["drive"])
                self.assertEqual(nxt["team"], k["kicking"] if side == "kicking" else k["receiving"])
                self.assertEqual(nxt["start_kind"], "onside_recovery" if side == "kicking" else "onside_lost")
                row = next(x for x in r["play_ledger"] if x["play_type"] == "kickoff" and x["drive"] == k["drive"]
                           and x.get("onside"))
                self.assertFalse(row["touchback"])
                self.assertIsNone(row["returner"])
                self.assertEqual(row["attribution"], sd.GROUP_DRAW)
                recovering = k["kicking"] if side == "kicking" else k["receiving"]
                self.assertIn(row["recovered_by"], r["team_stats"][recovering]["players"])
                self.assertEqual(r["team_stats"][k["kicking"]]["onside_recoveries"],
                                 sum(1 for j in r["kickoffs"] if j["kicking"] == k["kicking"]
                                     and j["outcome"] == "onside_recovered"))
                if kick_no == h2 and side == "kicking":
                    self.assertEqual(k["kicking"], r["opening_receiver"])

    def test_two_point_good_and_no_good(self):
        td = first(self.drives("touchdown"), lambda p: True, "a touchdown")
        for made in (True, False):
            r = self.force({"tries": {"drive:%d" % td["number"]: {"decision": "go", "made": made}}})
            q = r["possessions"][td["number"] - 1]
            self.assertEqual((q["try"]["decision"], q["try"]["made"], q["xp_made"]), ("go", made, None))
            self.assertEqual(q["points"], 8 if made else 6)
            rows = [x for x in r["play_ledger"] if x["drive"] == q["number"] and x["play_type"] in play_detail.TRY_ROWS]
            self.assertEqual([x["play_type"] for x in rows], ["two_point"])
            row = rows[0]
            self.assertEqual((row["anchor"], row["scoring_team"], row["made"]), ({"drive": q["number"]}, q["team"], made))
            players = r["team_stats"][q["team"]]["players"]
            credited = sum(players[pid].get(f, 0) for pid in players for f in sd.TWO_POINT_FIELDS)
            self.assertEqual(credited, (2 if row["try_type"] == "pass" else 1) if made else 0)
            if row["try_type"] == "pass":
                self.assertEqual((row["passer"], row["runner"]), (q["passer"], None))
            self.assertEqual(r["team_stats"][q["team"]]["two_point_attempts"],
                             sum(1 for c, t in all_tries(r) if c == q["team"] and t["decision"] == "go"))

    def test_try_after_a_non_offensive_touchdown(self):
        p = first(self.drives("interception", "fumble_lost"), lambda p: True, "a turnover")
        r = self.force({"drives": {p["number"]: "defensive_touchdown"},
                        "tries": {"drive:%d" % p["number"]: {"decision": "go", "made": True}}})
        q = r["possessions"][p["number"] - 1]
        row = next(x for x in r["play_ledger"] if x["play_type"] == "two_point" and x["anchor"] == {"drive": q["number"]})
        self.assertEqual((row["offense"], row["scoring_team"]), (other(q["team"]), other(q["team"])))
        self.assertEqual(q["non_offensive_score"]["points"], 8)
        r = self.force({"kicks": {1: "touchdown"}, "tries": {"kick:1": {"decision": "go", "made": False}}})
        self.assertEqual((r["kickoffs"][0]["points"], r["kickoffs"][0]["try"]["decision"]), (6, "go"))

    def test_pick_six_on_a_half_final_possession(self):
        for i in range(80):
            name = "b9-hf-%d" % i
            g = play(name)
            hf = [p for p in g["possessions"] if p["half_final"] and p["half"] == 1
                  and p["category"] in ("interception", "fumble_lost")]
            if hf:
                break
        else:
            self.skipTest("no half-final turnover in 80 synthetic games")
        r = play(name, {"drives": {hf[0]["number"]: "defensive_touchdown"}})
        self.assertEqual(clean(r), [])
        q = r["possessions"][hf[0]["number"] - 1]
        self.assertIsNotNone(q["non_offensive_score"].get("try"))
        self.assertFalse(any(k["after_drive"] == q["number"] for k in r["kickoffs"]))
        self.assertEqual(r["possessions"][q["number"]]["half"], 2)


class OvertimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.games = []
        for i in range(120):
            name = "b9ot-%d" % i
            r = play(name)
            if any(p["half"] == "OT" for p in r["possessions"]):
                cls.games.append((name, r))
            if len(cls.games) >= 5:
                break
        if len(cls.games) < 3:
            raise AssertionError("too few synthetic overtime games; pick other seeds")

    def opener(self, r):
        return next(k["kick_no"] for k in r["kickoffs"] if k["half"] == "OT")

    def test_ot_status_units(self):
        self.assertEqual(ot_status([{"team": "A", "score": "touchdown", "scoring_team": "B"}]), "end")
        self.assertEqual(ot_status([{"team": "A", "score": "field_goal"}, {"team": "B", "score": "touchdown",
                                                                           "scoring_team": "A"}]), "end")
        self.assertEqual(ot_status([{"team": "B", "score": None, "opportunity": "R4"},
                                    {"team": "A", "score": "field_goal"}]), "end")
        self.assertEqual(ot_status([{"team": "A", "score": "field_goal"}]), "continue")

    def test_opening_kick_return_touchdown_ends_it_without_a_try(self):
        name, base = self.games[0]
        r = play(name, {"kicks": {self.opener(base): "touchdown"}})
        self.assertEqual(clean(r), [])
        self.assertFalse([p for p in r["possessions"] if p["half"] == "OT"])
        last = r["kickoffs"][-1]
        self.assertEqual((last["points"], last.get("try")), (6, None))
        self.assertFalse([x for x in r["play_ledger"] if x["play_type"] in play_detail.TRY_ROWS and x["period"] == "OT"])

    def test_defensive_touchdown_ends_it_without_a_try(self):
        for name, base in self.games:
            ot = [p for p in base["possessions"] if p["half"] == "OT"]
            if ot[0]["category"] in ("interception", "fumble_lost", "punt"):
                break
        else:
            self.skipTest("no overtime opening possession that can be returned")
        branch = "punt_return_td" if ot[0]["category"] == "punt" else "defensive_touchdown"
        r = play(name, {"drives": {ot[0]["number"]: branch}})
        self.assertEqual(clean(r), [])
        q = r["possessions"][-1]
        self.assertEqual((q["number"], q["half"]), (ot[0]["number"], "OT"))
        self.assertEqual((q["non_offensive_score"]["points"], q["non_offensive_score"].get("try")), (6, None))
        self.assertGreater(r["final_score"][other(q["team"])], r["final_score"][q["team"]])

    def test_offensive_walk_off_has_no_try(self):
        for name, r in self.games:
            last = r["possessions"][-1]
            if last["half"] == "OT" and last["category"] == "touchdown":
                self.assertIsNone(last.get("try"))
                self.assertIsNone(last["xp_made"])
                return
        self.skipTest("no overtime walk-off touchdown among the synthetic games")

    def test_rule_r4_after_an_opening_field_goal(self):
        for name, base in self.games:
            ot = [p for p in base["possessions"] if p["half"] == "OT"]
            if ot[0]["category"] == "field_goal_attempt" and ot[0]["fg_made"]:
                break
        else:
            self.skipTest("no overtime opening field goal")
        kick = next(k["kick_no"] for k in base["kickoffs"] if k["half"] == "OT" and k["after_drive"] == ot[0]["number"])
        r = play(name, {"kicks": {kick: "onside_recovered"}})
        self.assertEqual(clean(r), [])
        self.assertEqual([p["number"] for p in r["possessions"] if p["half"] == "OT"], [ot[0]["number"]])
        self.assertGreater(r["final_score"][ot[0]["team"]], r["final_score"][other(ot[0]["team"])])

    def test_opening_recovery_gives_the_receiver_its_opportunity(self):
        name, base = self.games[0]
        r = play(name, {"kicks": {self.opener(base): "onside_recovered"}})
        self.assertEqual(clean(r), [])
        k = r["kickoffs"][self.opener(base) - 1]
        ot = [p for p in r["possessions"] if p["half"] == "OT"]
        history = ot_history(ot, [j for j in r["kickoffs"] if j["half"] == "OT"])
        self.assertEqual(history[0]["team"], k["receiving"])
        self.assertEqual(history[0]["opportunity"], "kicking-club recovery (R4)")
        self.assertEqual(ot[0]["team"], k["kicking"])
        self.assertEqual(ot_status(history), "end")

    def test_the_chart_path_reaches_rule_r4(self):
        # The chart's opening cell (not only a policy) can make the overtime
        # opener onside: with that cell and the surprise recovery patched to
        # certainty, the league basis decides it.
        name, base = self.games[0]
        cell, recovery_class = MODEL.onside_cell, MODEL.recovery_class

        def ot_cell(**kw):
            return "OT opener (test)" if kw["overtime"] and kw["opening"] else cell(**kw)

        def ot_class(**kw):
            return "certain (test)" if kw["overtime"] else recovery_class(**kw)

        # Only the overtime opener's cell and recovery are patched, so
        # regulation (and so the overtime itself) is unchanged.
        with mock.patch.object(MODEL, "onside_cell", ot_cell), mock.patch.object(MODEL, "recovery_class", ot_class), \
                mock.patch.dict(MODEL.onside_chart, {"OT opener (test)": (1, 1)}), \
                mock.patch.dict(MODEL.recovery, {"certain (test)": (1, 1)}):
            r = play(name)
        k = next(j for j in r["kickoffs"] if j["half"] == "OT")
        self.assertEqual((k["onside"], k["basis"], k["outcome"]), (True, "league", "onside_recovered"))
        self.assertEqual(clean(r), [])
        history = ot_history([p for p in r["possessions"] if p["half"] == "OT"],
                             [j for j in r["kickoffs"] if j["half"] == "OT"])
        self.assertEqual(history[0]["team"], k["receiving"])


class ProBowlTests(unittest.TestCase):
    def test_pro_bowl_pick_six(self):
        for i in range(40):
            name = "b9pb-%d" % i
            g = play(name, game_type="pro_bowl")
            picks = [p for p in g["possessions"] if p["category"] == "interception" and p is not g["possessions"][-1]]
            if picks:
                break
        else:
            self.fail("no Pro Bowl interception")
        r = play(name, {"drives": {picks[0]["number"]: "defensive_touchdown"}}, game_type="pro_bowl")
        self.assertEqual(clean(r), [])
        p, q = r["possessions"][picks[0]["number"] - 1], r["possessions"][picks[0]["number"]]
        self.assertEqual(r["kickoffs"], [])
        self.assertNotIn("try", p["non_offensive_score"])
        if p.get("quarter") == q.get("quarter"):
            self.assertEqual((q["team"], q["start_kind"], q["start_spot"]), (p["team"], "placement", 75))
        self.assertFalse([x for x in r["play_ledger"] if x["play_type"] == "two_point"])
        self.assertTrue(all(s["two_point_attempts"] == 0 for s in r["team_stats"].values()))
        self.assertFalse(any(p.get("try") for p in r["possessions"]))


class RulesTests(unittest.TestCase):
    def test_try_rule_seam(self):
        self.assertEqual(try_rule(), {"extra_point": extra_point_rule(), "two_point_snap_yard_line": 2,
                                      "defense_may_score": False})
        self.assertEqual(try_rule("preseason", "2014-08-09")["extra_point"]["distance"], 33)

    def test_every_regulation_touchdown_is_tried(self):
        for i in range(10):
            r = play("b9-try-%d" % i)
            for p in r["possessions"]:
                if p["category"] == "touchdown" and p["half"] in (1, 2):
                    self.assertIsNotNone(p.get("try"), p["number"])
        # b9-seek-41, drive 25: a touchdown with 0:00 left in the fourth
        # quarter (found by search) is still tried, though it cannot win.
        r = play("b9-seek-41", profile=PROFILE_B9_LEVEL)
        p = r["possessions"][24]
        self.assertEqual((p["category"], p["half"], p["end_clock"]), ("touchdown", 2, 0))
        self.assertIsNotNone(p["try"])
        rows = [x for x in r["play_ledger"] if x["drive"] == 25 and x["play_type"] in play_detail.TRY_ROWS]
        self.assertEqual(len(rows), 1)

    def test_preseason_window_kick_is_the_33_yard_field_goal(self):
        dm = BASE_2010_2014W4.drive_model()
        with mock.patch.object(type(dm), "fg_make_prob_at", lambda self, distance: 0.0):
            window = play("b9-pre-w", game_type="preseason", game_date="2014-08-09")
            later = play("b9-pre-w", game_type="preseason", game_date="2014-08-28")
        kicks = [t for _, t in all_tries(window) if t["decision"] == "kick"]
        self.assertTrue(kicks and not any(t["made"] for t in kicks))
        later_kicks = [t for _, t in all_tries(later) if t["decision"] == "kick"]
        self.assertTrue(any(t["made"] for t in later_kicks))


class ParticipationTests(unittest.TestCase):
    def test_try_snap_credits_one_snap_per_side(self):
        off, dfn = list(A.roster), list(B.roster)
        passer = usage.game_passer(off)
        receiver = usage.depth_order(off, "WR")[0].player_id
        row = {"passer": passer.player_id, "target": receiver, "runner": None}
        hazard = {}
        snaps = participation.try_snap({}, "A", "B", off, dfn, passer, usage.protection_front(off), row,
                                       hazard_out=hazard)
        self.assertEqual(snaps["A"][passer.player_id], 1)
        self.assertEqual(snaps["A"][receiver], 1)
        self.assertTrue(all(v <= 1 for side in snaps.values() for v in side.values()))
        self.assertTrue(snaps["B"])
        self.assertEqual(set(hazard), {"A", "B"})
        self.assertNotIn("two_point", participation.SCRIMMAGE_TYPES)

    def test_a_two_point_row_is_never_route_evidence(self):
        # The try names a target but is not a scrimmage snap: player evidence
        # reads the drive's own routes only.
        from runtime.kernel import _append_evidence
        receiver = next(p for p in A.roster if p.position == "WR")
        evidence = []
        _append_evidence(evidence, [{"play_type": "run", "runner": "A-RB1"},
                                    {"play_type": "two_point", "target": receiver.player_id}],
                         list(A.roster), list(B.roster), "touchdown")
        self.assertFalse([e for e in evidence if e["player"] == receiver.player_id])
        _append_evidence(evidence, [{"play_type": "pass", "target": receiver.player_id}], list(A.roster),
                         list(B.roster), "touchdown")
        self.assertTrue([e for e in evidence if e["player"] == receiver.player_id])

    def test_kernel_credits_the_try_snap(self):
        r = play("b9-part", home=with_team("A", {"try_policy": {"otherwise": "go"}}))
        rows = [x for x in r["play_ledger"] if x["play_type"] == "two_point" and x["offense"] == "A"]
        self.assertTrue(rows)
        players = r["team_stats"]["A"]["players"]
        for x in rows:
            for field in ("passer", "target", "runner"):
                if x.get(field):
                    self.assertGreaterEqual(players[x[field]]["offensive_snaps"], 1)
        self.assertEqual(validate_result(r), [])


class E2PauseTests(unittest.TestCase):
    def test_pause_across_a_non_offensive_touchdown(self):
        a = with_team("A", {"try_policy": DELEGATION, "kickoff_policy": DELEGATION, **FOURTH})
        # b9-e2-0: a B turnover (re-searched for batch B11; "b9-e2" no longer has one).
        base = play("b9-e2-0", home=a)
        p = first([p for p in base["possessions"][:-1] if p["team"] == "B" and p["half"] in (1, 2)
                   and p["category"] in ("interception", "fumble_lost")], lambda p: True, "a B turnover")
        # A scores on B's turnover and kicks the try: its kicker is exposed on
        # that possession (the try's unit), and removing the only kicker is a
        # consequential package change, so the pause follows the score.
        forced = {"drives": {p["number"]: "defensive_touchdown"},
                  "tries": {"drive:%d" % p["number"]: {"decision": "kick"}}}
        kicker = usage.kicking_specialist(list(a.roster), "K", "placekicker").player_id
        onsets = {(p["number"], kicker): {"injury_class": "lower_extremity", "severity": "short", "removed": True}}
        kw = dict(seed=SEED + b"-b9-e2-0", event_id="b9-e2-0", _test_profile=PROFILE_2014_6, _test_scoring=forced,
                  _test_onsets=onsets, management_mode="user_controlled", controlled_team="A")
        decisions, ours = [], None
        for _ in range(12):
            r = resolve_game(a, B, continuation={"decisions": decisions} if decisions else None, **kw)
            if r.get("terminated"):
                break
            pause = r["pauses"][-1]
            self.assertNotIn("final_score", r)
            if pause.get("drive") == p["number"] and kicker in {d["slot"] for d in pause["decisions"]}:
                # The pause follows the non-offensive score: the partial
                # result already holds it (completed events only).
                ours = r
                q = r["possessions"][p["number"] - 1]
                self.assertEqual(q["non_offensive_score"]["team"], "A")
            decisions.append({"token": pause["continuation_token"],
                              "choices": {d["slot"]: d["eligible"][0] for d in pause["decisions"]}})
        self.assertIsNotNone(ours, "the removal at the non-offensive score did not pause")
        self.assertTrue(r["terminated"])
        # The prefix reproduces; the paused possession's kick after the score
        # (kickoff_after, next_start) is filled in once the kick is made.
        n = len(ours["possessions"])
        self.assertEqual(r["possessions"][:n - 1], ours["possessions"][:n - 1])
        trim = lambda q: {k: v for k, v in q.items() if k not in ("kickoff_after", "next_start")}
        self.assertEqual(trim(r["possessions"][n - 1]), trim(ours["possessions"][n - 1]))
        self.assertEqual(clean(r), [])

    def test_live_try_decision_through_the_pause(self):
        a = with_team("A", {"try_policy": {"otherwise": "ask"}, "kickoff_policy": DELEGATION, **FOURTH})
        kw = dict(seed=SEED + b"-b9-live", event_id="b9-live", _test_profile=PROFILE_2014_6,
                  management_mode="user_controlled", controlled_team="A")
        decisions, answers = [], []
        for _ in range(16):
            r = resolve_game(a, B, continuation={"decisions": decisions} if decisions else None, **kw)
            if r.get("terminated"):
                break
            pause = r["pauses"][-1]
            if pause["trigger"] == "consequential_substitution":
                decisions.append({"token": pause["continuation_token"],
                                  "choices": {d["slot"]: d["eligible"][0] for d in pause["decisions"]}})
                continue
            self.assertEqual((pause["trigger"], pause["team"]), ("two_point", "A"))
            self.assertEqual(pause["decisions"][0]["eligible"], ["go", "kick"])
            text = json.dumps(pause)
            for word in ("p_go", "basis", "cell", "prob"):
                self.assertNotIn(word, text)
            answer = "go" if len(answers) % 2 == 0 else "kick"
            answers.append(answer)
            decisions.append({"token": pause["continuation_token"], "choices": {"try": answer}})
        self.assertTrue(r["terminated"] and answers)
        live = [t for club, t in all_tries(r) if club == "A"]
        self.assertEqual([t["decision"] for t in live], answers)
        self.assertTrue(all(t["basis"] == "live" for t in live))
        self.assertEqual(clean(r), [])
        stale = [{"token": "0" * 64, "choices": {"try": "go"}}]
        with self.assertRaises(ValueError):
            resolve_game(a, B, continuation={"decisions": stale}, **kw)

    def test_only_the_controlling_coach_answers_live(self):
        # Refused from the inputs alone, before any draw, on every seed (also
        # where the asking club never scores): never by how the game goes.
        import random as random_module
        from runtime import kernel

        class NoDraw(random_module.Random):
            def random(self):
                raise AssertionError("a draw was taken before the ask was refused")

        ask = {"otherwise": "ask"}
        cases = [dict(home=with_team("A", {"try_policy": ask})),
                 dict(home=with_team("A", {"kickoff_policy": ask})),
                 dict(home=with_team("A", {"try_policy": DELEGATION, "kickoff_policy": DELEGATION}),
                      away=with_team("B", {"try_policy": ask}), management_mode="user_controlled",
                      controlled_team="A")]
        with mock.patch.object(kernel, "_rng", lambda seed, packet: NoDraw(0)):
            for kw in cases:
                for i in range(6):
                    with self.assertRaisesRegex(ValueError, "asks for a live"):
                        play("b9-ask-%d" % i, **kw)
        for i in range(30):
            with self.assertRaisesRegex(ValueError, "asks for a live"):
                play("b9-ask-auto-%d" % i, home=with_team("A", {"try_policy": ask}))


class LabelTests(unittest.TestCase):
    def test_try_rows_take_two_point_menu_calls(self):
        sheet = json.loads(WEEK4_SHEET.read_text(encoding="utf-8"))["offensive_call_sheet"]
        names = {c["name"]: c for c in sheet}
        a = with_team("A", {"try_policy": {"otherwise": "go"}}, sheet=sheet)
        concepts = set()
        for i in range(12):
            r = play("b9-label-%d" % i, home=a)
            for x in r["play_ledger"]:
                if x["play_type"] == "two_point" and x["offense"] == "A":
                    self.assertEqual(x["situation"], "two-point")
                    self.assertEqual(x["label_type"], x["try_type"])
                    if x["label_source"] == "sheet":
                        self.assertIn("two-point", names[x["concept"]]["menus"])
                    concepts.add(x["concept"])
        self.assertIn("11 Bunch, Snag", concepts)

    def test_outcomes_do_not_change_with_menus_stripped(self):
        sheet = json.loads(WEEK4_SHEET.read_text(encoding="utf-8"))["offensive_call_sheet"]
        uniform = [{k: v for k, v in c.items() if k not in ("menus", "opener", "opener_returns")} for c in sheet]
        policy = {"try_policy": {"otherwise": "go"}}
        situational, plain = with_team("A", policy, sheet=sheet), with_team("A", policy, sheet=uniform)
        labels = {"concept", "family", "personnel", "formation", "motion", "protection", "tags", "scramble",
                  "label_groups", "label_source", "label_type", "situation", "script_position"}
        for i in range(6):
            x = play("b9-uniform-%d" % i, home=situational)
            y = play("b9-uniform-%d" % i, home=plain)
            for key in ("final_score", "possessions", "kickoffs", "team_stats", "injuries"):
                self.assertEqual(x[key], y[key], key)
            self.assertEqual([{k: v for k, v in r.items() if k not in labels} for r in x["play_ledger"]],
                             [{k: v for k, v in r.items() if k not in labels} for r in y["play_ledger"]])


# Re-searched for batch B13, whose replayed yard split moves every later
# layout and the decisions read from it: "b9-views" no longer holds a
# regulation touchdown after its blocked punt; "b9-views-0" is the first label
# of the pattern b9-views-N whose chain below resolves.
VIEWS_NAME = "b9-views-0"


class StatbookAndViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Each branch is forced on a drive found after the earlier ones are
        # applied (a forced branch changes everything after it).
        forced = {"kicks": {1: "touchdown"}, "drives": {}, "tries": {}}
        g = play(VIEWS_NAME, forced)
        p = next(p for p in g["possessions"][:-1] if p["category"] in ("interception", "fumble_lost")
                 and p["half"] in (1, 2))
        forced["drives"][p["number"]] = "defensive_touchdown"
        forced["tries"]["drive:%d" % p["number"]] = {"decision": "go", "made": False}
        g = play(VIEWS_NAME, forced)
        punt = next(q for q in g["possessions"][:-1] if q["category"] == "punt" and q["number"] > p["number"])
        forced["drives"][punt["number"]] = "blocked_punt_td"
        g = play(VIEWS_NAME, forced)
        td = next(q for q in g["possessions"][:-1] if q["category"] == "touchdown" and q["number"] > punt["number"]
                  and q["half"] in (1, 2))
        forced["tries"]["drive:%d" % td["number"]] = {"decision": "go", "made": True}
        cls.result = play(VIEWS_NAME, forced)
        assert validate_result(cls.result) == []
        cls.old = resolve_game(A, B, seed=SEED + b"-b9-old", event_id="b9-old", _test_profile=PROFILE_2014_5)

    def test_mixed_2014_5_and_2014_6_statbook(self):
        new = receipt(self.result)
        old = receipt(self.old)
        book = aggregate_receipts([old, new])
        for team_id in ("A", "B"):
            t = book["teams"][team_id]
            self.assertEqual(t["kernel_2014_6_games"], 1)
            for field in KERNEL_2014_6_TEAM_STAT_FIELDS:
                self.assertEqual(t["team_stats"][field], self.result["team_stats"][team_id][field])
        only_old = aggregate_receipts([old])
        self.assertNotIn("kernel_2014_6_games", only_old["teams"]["A"])
        self.assertFalse(set(KERNEL_2014_6_TEAM_STAT_FIELDS) & set(only_old["teams"]["A"]["team_stats"]))
        self.assertFalse(set(KERNEL_2014_6_PLAYER_FIELDS) & set(only_old["player_stat_fields"]))
        self.assertTrue(set(KERNEL_2014_6_PLAYER_FIELDS) & set(book["player_stat_fields"]))
        credited = sum(line.get(f, 0) for line in book["players"].values() for f in set(sd.PLAYER_TD_FIELD.values()))
        self.assertEqual(credited, sum(self.result["team_stats"][t]["defensive_touchdowns"]
                                       + self.result["team_stats"][t]["special_teams_touchdowns"] for t in "AB"))

    def test_standings_net_touchdowns_include_returns(self):
        rc = json.loads(json.dumps(receipt(self.result)).replace('"A"', '"Jacksonville Jaguars"')
                        .replace('"B"', '"Houston Texans"'))
        rc["matchup"] = "Houston Texans at Jacksonville Jaguars"
        rc["home"], rc["away"] = "Jacksonville Jaguars", "Houston Texans"
        game = standings.games_from_receipts([rc])[0]
        for club, tid in (("Jacksonville Jaguars", "A"), ("Houston Texans", "B")):
            s = self.result["team_stats"][tid]
            offensive = sum(1 for p in self.result["possessions"] if p["team"] == tid and p["category"] == "touchdown")
            self.assertEqual(game.touchdowns(club), offensive + s["defensive_touchdowns"] + s["special_teams_touchdowns"])
        self.assertGreater(self.result["team_stats"]["A"]["defensive_touchdowns"]
                           + self.result["team_stats"]["B"]["defensive_touchdowns"], 0)

    def test_gamebook_reads_tries_and_returns(self):
        rc = receipt(self.result, "full")
        text = gamebook.render(rc, "A")
        self.assertIn("kickoff return", text)
        self.assertIn("blocked punt return", text)
        self.assertTrue(" pass from " in text or " run)" in text)
        self.assertTrue("(pass failed)" in text or "(run failed)" in text)
        self.assertIn("Two-point conversions, made-attempts", text)
        view = gamebook.GameView(rc, "A")
        self.assertEqual({c: sum(e["points"] for e in view.events if e["club"] == c) for c in view.clubs},
                         rc["final_score"])
        # A turnover row returned for the defense's touchdown is never the
        # offense's fourth-down conversion.
        row = {"play_type": "pass", "offense": "A", "down": 4, "touchdown": True, "turnover": True}
        view.scrim["A"] = [row]
        self.assertEqual(view.fourth_down("A"), (0, 1))

    def test_rendered_markdown_never_shows_a_basis_or_probability(self):
        import importlib
        rc = receipt(self.result, "full")
        texts = [gamebook.render(rc, club) for club in ("A", "B")]
        render_stats = importlib.import_module("scripts.render_season_stats")
        book = aggregate_receipts([receipt(self.result)])
        texts.append(render_stats.team_stats_markdown(2014, book, [receipt(self.result)]))
        tracker = importlib.import_module("scripts.render_team_tracker")
        game = {"kind": "regular", "week": 5, "opponent": "B", "home": True, "points": self.result["final_score"]["A"],
                "opp_points": self.result["final_score"]["B"], "team": rc["team_stats"]["A"],
                "opp": rc["team_stats"]["B"], "event_id": rc["event_id"]}
        texts.append(tracker.game_page("A", 2014, game, []))
        forbidden = ("basis", "policy:", "delegated", "league chart", "p_go", "p_onside", "p_recover",
                     "recovery_class", "Q1-Q3", "Q4 120-0", "Q4 900", "trail 1-3", "lead 1+", "surprise",
                     "expected recovery", "group_draw", "attribution", "probab", "odds")
        for text in texts:
            for word in forbidden:
                self.assertNotIn(word, text)
        self.assertIn("Two-point conversions and return touchdowns", texts[-1])


class AuditTests(unittest.TestCase):
    def test_scoring_rows_read_the_artifact(self):
        from runtime import bands
        receipts = []
        for i in range(10):
            r = play("b9-audit-%d" % i)
            rc = receipt(r)
            receipts.append(rc)
        team_games, rows = bands.audit_scoring(receipts, cohort="2014.6")
        self.assertEqual(team_games, 20)
        centres = {m: c for m, _, c, _, _ in rows}
        self.assertAlmostEqual(centres["two-point conversion rate"], 115 / 232)
        self.assertAlmostEqual(centres["extra-point rate"], 5192 / 5228)
        self.assertAlmostEqual(centres["fourth-quarter go share of tries down 2 after the touchdown"], 32 / 34)
        self.assertAlmostEqual(centres["onside share of kicks trailing by 1-8 inside 2:00"], 66 / 70)
        self.assertAlmostEqual(centres["expected onside recovery rate"], 18 / 163)
        self.assertAlmostEqual(centres["interception-return touchdown share of interceptions"], 254 / 2088)
        self.assertAlmostEqual(centres["fumble-return touchdown share of lost fumbles"], 93 / 1166)
        self.assertAlmostEqual(centres["punt return or blocked-punt touchdown share of punts"], 93 / 10475)
        self.assertAlmostEqual(centres["kickoff-return touchdown share of deep kickoffs"], 31 / 8049)
        self.assertAlmostEqual(centres["onside kicks per team-game"], 233 / 2170)
        statuses = {m: s for m, _, _, _, s in rows}
        self.assertEqual(statuses["points per team-game (measured; no forecast)"], "MEASURED")
        self.assertEqual(bands.audit_scoring(receipts, cohort="2014.5")[1], [])

    def test_calibration_audit_sentence_is_scoped(self):
        import importlib
        render_stats = importlib.import_module("scripts.render_season_stats")
        self.assertIn("not modelled", render_stats.POINTS_NOTE)
        self.assertNotIn("not modelled", render_stats.POINTS_NOTE_2014_6)
        receipts = [receipt(play("b9-cal-%d" % i)) for i in range(8)]
        for rc in receipts:
            rc["season"] = 2014
        text = "\n".join(render_stats._base_cohort_lines("2014.6", receipts, "none"))
        self.assertIn("### Scoring-decision rows", text)
        self.assertIn(render_stats.POINTS_NOTE_2014_6, text)
        self.assertNotIn(render_stats.POINTS_NOTE, text)

    CHART_ROWS = ("two-point attempt share of tries", "fourth-quarter go share of tries down 2 after the touchdown",
                  "onside kicks per team-game", "onside share of kicks trailing by 1-8 inside 2:00")
    APART = ("tries and kickoffs decided by a club's block or a live answer (informational; counted apart, "
             "never graded against the chart)")

    def test_a_block_never_moves_a_chart_row(self):
        # Round-2 review: the rows centred on the league charts grade only
        # the chart's decisions (league, delegated:league). Club A carries a
        # block for both kinds (every decision policy:i); club B delegates to
        # the chart. Moving A's block (every one of its decisions flipped,
        # all else held) leaves each chart row and the counted-apart row
        # unchanged, though the unfiltered go share moves.
        import copy
        from runtime import bands
        a = with_team("A", {"try_policy": GO_LATE, "kickoff_policy": ONSIDE_LATE})
        b = with_team("B", {"try_policy": DELEGATION, "kickoff_policy": DELEGATION})
        receipts = [receipt(play("b9-basis-%d" % i, home=a, away=b)) for i in range(12)]
        on = play_detail.KICK_SUMMARY_FIELDS.index("onside")
        basis = play_detail.KICK_SUMMARY_FIELDS.index("basis")
        kicking = play_detail.KICK_SUMMARY_FIELDS.index("kicking")
        moved = copy.deepcopy(receipts)
        flipped = 0
        for rc in moved:
            line = rc["team_stats"]["A"]  # every policy:i decision is A's; its counters move with it
            for t in bands._tries(rc):
                if t["basis"].startswith("policy:"):
                    go = t["decision"] == "kick"
                    t["decision"] = "go" if go else "kick"
                    step = 1 if go else -1
                    line["two_point_attempts"] += step
                    line["extra_point_attempts"] -= step
                    if t["made"]:
                        line["two_point_conversions"] += step
                        line["extra_points_made"] -= step
                    flipped += 1
            rows = [list(row) for row in rc["kicks"]]
            for row in rows:
                if row[on] is not None and row[basis].startswith("policy:"):
                    self.assertEqual(row[kicking], "A")
                    row[on] = not row[on]
                    line["onside_kicks"] += 1 if row[on] else -1
                    flipped += 1
            rc["kicks"] = rows
        self.assertGreater(flipped, 0)
        graded = {}
        for name, rcs in (("block", receipts), ("moved", moved)):
            graded[name] = {m: (o, c, t, s) for m, o, c, t, s in bands.audit_scoring(rcs, cohort="2014.6")[1]
                            if m in self.CHART_ROWS + (self.APART,)}
        self.assertEqual(set(graded["block"]), set(self.CHART_ROWS + (self.APART,)))
        self.assertEqual(graded["block"], graded["moved"])

        def go_share(rcs):
            tries = [t for rc in rcs for t in bands._tries(rc)]
            return sum(t["decision"] == "go" for t in tries) / len(tries)
        self.assertNotEqual(go_share(receipts), go_share(moved))
        # The graded rows are B's delegated decisions exactly; A's are apart.
        tries = [t for rc in receipts for t in bands._tries(rc)]
        kicks = [k for rc in receipts for k in play_detail.kicks_of(rc) if k.get("onside") is not None]
        chart = [t for t in tries if t["basis"] == "delegated:league"]
        self.assertTrue(chart and len(chart) < len(tries))
        self.assertAlmostEqual(graded["block"][self.CHART_ROWS[0]][0],
                               sum(t["decision"] == "go" for t in chart) / len(chart))
        b_onside = sum(bool(k["onside"]) for k in kicks if k["kicking"] == "B")
        self.assertAlmostEqual(graded["block"][self.CHART_ROWS[2]][0], b_onside / len(receipts))
        self.assertEqual(graded["block"][self.APART][0],
                         sum(1 for d in tries + kicks if d["basis"].startswith("policy:")))
        self.assertEqual(graded["block"][self.APART][3], "MEASURED")


class IsolationTests(unittest.TestCase):
    """A game in which no B9 branch fires equals its B8-level run apart from
    the append-only records; the extra point is the same draw against the
    same rate, so no extra point flips (both profiles read 5,192/5,228)."""

    def test_no_branch_game_equals_its_branch_off_run(self):
        compared = flips = 0
        for i in range(30):
            name = "b9-iso-%d" % i
            on, off = play(name), play(name, profile=PROFILE_B8)
            fired = (any(x["play_type"] == "two_point" for x in on["play_ledger"])
                     or any(p.get("non_offensive_score") for p in on["possessions"])
                     or any(k.get("onside") or k.get("touchdown") for k in on["kickoffs"]))
            if fired:
                continue
            compared += 1
            x, y = strip_2014_6_fields(on), strip_2014_6_fields(off)
            flips += sum(1 for p, q in zip(on["possessions"], off["possessions"]) if p["xp_made"] != q["xp_made"])
            self.assertEqual(x, y, name)
        self.assertGreater(compared, 5)
        self.assertEqual(flips, 0)


class LateFeasibilityTests(unittest.TestCase):
    def test_onside_starts_never_need_a_zero_tuple(self):
        both = {"kickoff_policy": {"otherwise": "onside"}}
        zero = 0
        for i in range(10):
            r = play("b9-late-%d" % i, home=with_team("A", both), away=with_team("B", both))
            self.assertEqual(clean(r), [])
            zero += r["diagnostics"]["fallback_zero_tuple"]
            for k in r["kickoffs"]:
                self.assertEqual(bool(k.get("onside")), not k["free_kick"])
        self.assertEqual(zero, 0)

    def test_the_committed_late_onside_block(self):
        # scripts/research/acceptance_2014_6.py --block late-onside (600 games
        # at acceptance; three here).
        sys.path.insert(0, str(ROOT / "scripts" / "research"))
        import acceptance_2014_6 as acc
        out = acc.late_onside_block(count=3)
        self.assertTrue(out["pass"], out)
        self.assertEqual(out["games"], 3)
        self.assertGreater(out["onside_kicks"], 0)


class RealInputLabelSwapTests(unittest.TestCase):
    """The Week 4 Jacksonville and San Diego inputs (acceptance slate clubs,
    synthetic latent draws): the same policy carried by either club is the
    same function of state; the other club takes the league chart."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / "scripts" / "research"))
        import acceptance_2014_6 as acc
        clubs = acc.slate_clubs("2014.6")
        cls.jax, cls.sd = clubs["Jacksonville Jaguars"], clubs["San Diego Chargers"]

    def run_side(self, carrier):
        jax = replace(self.jax, try_policy=GO_LATE, kickoff_policy=ONSIDE_LATE) if carrier == "jax" else self.jax
        sdc = replace(self.sd, try_policy=GO_LATE, kickoff_policy=ONSIDE_LATE) if carrier == "sd" else self.sd
        holder = (jax if carrier == "jax" else sdc).team_id
        tries = 0
        for i in range(4):
            r = resolve_game(sdc, jax, seed=SEED + b"-b9-swap-%d" % i, event_id="b9-swap-%d" % i, venue="neutral",
                             _test_profile=PROFILE_2014_6)
            self.assertEqual(validate_result(r), [])
            for club, t in all_tries(r):
                tries += 1
                if club == holder:
                    self.assertTrue(t["basis"].startswith("policy:"))
                    self.assertEqual(t["decision"], "go" if t["basis"] in ("policy:0", "policy:1") else "kick")
                else:
                    self.assertEqual(t["basis"], "league")
        return tries

    def test_policy_moved_between_the_clubs(self):
        self.assertGreater(self.run_side("jax") + self.run_side("sd"), 0)

    def test_the_committed_swap_block(self):
        # scripts/research/acceptance_2014_6.py --block swap (120 games per arm
        # at acceptance; two here): every holder's try and kick follows its
        # block and the other club takes the league chart. A relabelled club
        # is another packet (another stream), so the Jacksonville and Denver
        # arms agree in distribution (the block's z readings), not game by game.
        import acceptance_2014_6 as acc
        out = acc.swap_block(count=2)
        arms = out["arms"]
        for arm in acc.SWAP_ARMS:
            a = arms[arm]
            self.assertEqual((a["refused"], a["errors"]), ([], 0), arm)
            self.assertEqual((a["compliant"], a["kicks_compliant"], a["other_league"]),
                             (a["tries"], a["kicks"], a["other_tries"]), arm)
        self.assertTrue(all(arms[arm]["tries"] for arm in acc.SWAP_ARMS))
        self.assertIn("z_points_jax_vs_den", out)


class SocketWiringTests(unittest.TestCase):
    """The E1 sockets reach the kernel's call sites (real Week 4 inputs with
    synthetic latent draws): each return or blocked-kick probability is drawn
    with its unit's input (the returner's tier value, the defence's coverage
    composite, the kicking club's protection and the defence's rush, each
    composite less its strength term's centre); at slope 0 nothing moves,
    and a patched slope moves the drawn probability the declared way."""

    SEEDS = 3

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / "scripts" / "research"))
        import acceptance_2014_6 as acc
        from runtime import strength
        clubs = acc.slate_clubs("2014.6")
        cls.jax, cls.sd = clubs["Jacksonville Jaguars"], clubs["San Diego Chargers"]
        cls.terms = strength.parameters(PROFILE_2014_6.strength).terms
        cls.base_games, cls.calls, cls.receipts = cls.games()

    @classmethod
    def games(cls, sockets=None):
        calls, receipts, games = [], [], []
        p_return, p_blocked = sd.ScoringModel.p_return, sd.ScoringModel.p_blocked

        def spy_return(pair, returner=0.0, coverage=0.0):
            p = p_return(pair, returner, coverage)
            calls.append(("return", tuple(pair), {"returner": returner, "coverage": coverage}, p))
            return p

        def spy_blocked(pair, protection=0.0, rush=0.0):
            p = p_blocked(pair, protection, rush)
            calls.append(("blocked", tuple(pair), {"protection": protection, "rush": rush}, p))
            return p

        with mock.patch.object(sd.ScoringModel, "p_return", staticmethod(spy_return)), \
                mock.patch.object(sd.ScoringModel, "p_blocked", staticmethod(spy_blocked)), \
                mock.patch.dict(sd.SOCKETS, sockets or {}):
            for i in range(cls.SEEDS):
                games.append(resolve_game(cls.sd, cls.jax, seed=SEED + b"-b9-sock-%d" % i, event_id="b9-sock-%d" % i,
                                          venue="neutral", _test_profile=PROFILE_2014_6,
                                          _test_strength_receipt=receipts))
        return games, calls, receipts

    def deviations(self, side, unit):
        centre = next(t["centre"] for t in self.terms if t["side"] == side and t["unit"] == unit)
        return {r["units"][side][unit]["composite"] - centre for r in self.receipts if side in r["units"]}

    def test_each_call_site_passes_its_unit_input(self):
        coverage = self.deviations("defense", "coverage")
        protection, rush = self.deviations("offense", "protection"), self.deviations("defense", "rush")
        returns = [c for c in self.calls if c[0] == "return"]
        blocked = [c for c in self.calls if c[0] == "blocked"]
        turnover_pairs = {tuple(v) for unit in ("interception", "fumble_lost")
                          for v in ART["non_offensive"][unit]["los_bins"].values()}
        turnovers = [c for c in returns if c[1] in turnover_pairs and c[2]["returner"] == 0.0]
        self.assertTrue(turnovers and blocked)
        self.assertTrue(all(c[2]["coverage"] in coverage for c in turnovers))
        self.assertTrue(any(c[2]["coverage"] != 0.0 for c in turnovers))
        self.assertTrue(any(c[2]["returner"] != 0.0 for c in returns))
        self.assertTrue(all(c[2]["protection"] in protection and c[2]["rush"] in rush for c in blocked))
        self.assertTrue(all(c[3] == c[1][0] / c[1][1] for c in self.calls))  # slope 0: the base rate exactly

    def test_a_patched_slope_moves_the_drawn_probability(self):
        slopes = {"returner": 0.001, "coverage": 0.001, "blocked_kick_protection": 0.001, "blocked_kick_rush": 0.001}
        _, calls, _ = self.games(slopes)
        moved = 0
        for kind, pair, inputs, p in calls:
            base = pair[0] / pair[1]
            if kind == "return":
                expected = base + 0.001 * inputs["returner"] - 0.001 * inputs["coverage"]
            else:
                expected = base - 0.001 * inputs["protection"] + 0.001 * inputs["rush"]
            self.assertAlmostEqual(p, min(1.0, max(0.0, expected)), places=12)
            moved += p != base
        self.assertGreater(moved, 0)
        # A slope large enough to decide the draw changes the game itself: one
        # sign drives every return probability with a nonzero coverage input
        # to 0 and the other to 1, so at least one of them changes a game.
        # (Review fix, October 16, 2026: the single sign held only for the
        # draws before the rebuilt player-state manifest re-keyed these games.)
        base = [g["final_score"] for g in self.base_games]
        changed = []
        for slope in (-1.0, 1.0):
            games, _, _ = self.games({"coverage": slope})
            changed.append([g["final_score"] for g in games] != base)
        self.assertTrue(any(changed), changed)


if __name__ == "__main__":
    unittest.main()
