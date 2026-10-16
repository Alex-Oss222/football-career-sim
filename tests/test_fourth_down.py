"""Kernel 2014.6 batch B9F: fourth-down decisions (go, field goal or punt).

Stone's standing instruction ("Fourth downs remain my call. I want the
decision prepared before third down whenever possible. Skalaski gives me
distance, field position, score, timeouts, clock and the kicking
information; Tice gives me the best prepared conversion call") and the
one-resolution rule, under PROFILE_2014_6 and the frozen rules of
library/2014_6_fourth_down_specification.md (its disclosed amendment F1
included). Every number is read from the fourth-down artifact
(library/data/2010_2014w4_fourth_down_decisions.json). Synthetic seeds and
synthetic clubs only; the private service is never contacted (the
pause/continue path through scripts/close_week.py is in
tests/test_close_week_pause.py).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ast
import copy
import inspect
import json
import random as random_module
import unittest
from dataclasses import replace
from unittest import mock

from runtime import bands, game_runner, kernel
from runtime import fourth_down as fd
from runtime import scoring_decisions as sd
from runtime.calibration_base import BASE_2010_2014W4
from runtime.game_runner import build_game_packet
from runtime.kernel import decision_block_errors, resolve_game, validate_result
from runtime.play_detail import check_ledger
from runtime.profiles import B9F_FLAGS, PROFILE_2014_5, PROFILE_2014_6, Profile
from runtime.statbook import make_receipt
from synthetic_games import SEED, sample_teams
from test_profiles import strip_2014_6_fields

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "research"))
import fourth_down_specification  # noqa: E402
import pre_build_specification  # noqa: E402

MODEL = BASE_2010_2014W4.fourth_down()
ART = MODEL.data
A, B = sample_teams()
DELEGATION = {"otherwise": "league"}
U6 = {"try_policy": DELEGATION, "kickoff_policy": DELEGATION}
# The B9 level of kernel 2014.6: every mechanism but live fourth downs.
PROFILE_B9 = Profile("2014.6", base=PROFILE_2014_6.base, cell_rules=PROFILE_2014_6.cell_rules,
                     strength=PROFILE_2014_6.strength, flags=PROFILE_2014_6.flags - B9F_FLAGS, record_base=True)
CONVERTED = ("converted", "touchdown")
# What a pause may never show: a probability, a chart value, a cell, a basis.
FORBIDDEN = ("prob", "p_convert", "cell", "chart", "basis", "odds", "share", "pair", "make")


def play(name, home=A, away=B, profile=PROFILE_2014_6, **kw):
    return resolve_game(home, away, seed=SEED + b"-" + name.encode(), event_id=name, _test_profile=profile, **kw)


def receipt(result, detail="compact_stats"):
    return make_receipt(result, week=5, matchup="B at A", detail=detail)


def clean(result):
    """The result and both receipt details validate and audit clean."""
    return (validate_result(result) + check_ledger(result) + check_ledger(receipt(result, "full"))
            + check_ledger(receipt(result)))


def records(result, team=None):
    """(possession, record) for every fourth-down decision of a result."""
    return [(p, d) for p in result["possessions"] for d in p.get("fourth_downs") or ()
            if team is None or p["team"] == team]


def label(edge):
    lo, hi = edge
    return str(lo) if lo == hi else "%d-%d" % (lo, hi)


def all_states():
    states = ART["rules"]["states"]
    out = ["neutral", "h1_le%d" % states["h1_seconds"]]
    out += ["q4|%s|%s" % (b, n) for b in states["late_time_buckets"] for n in states["needs"]]
    return out + ["ot|%s" % m for m in states["ot_margins"]]


def game_seconds(state):
    """The regulation countdown of a record's state (period and clock text)."""
    minutes, seconds = (int(x) for x in state["clock"].split(":"))
    return (4 - int(state["period"])) * 900 + minutes * 60 + seconds


def live(home, away, controlled, answer, *, name, profile=PROFILE_2014_6, limit=60, **kw):
    """Resolve a user-controlled game, answering each fourth-down pause with
    ``answer(pause)`` (the choices) and every other pause with its first
    eligible answer. Returns (final result, the fourth-down pauses, whether a
    substitution pause occurred)."""
    decisions, pauses, substituted = [], [], False
    for _ in range(limit):
        r = play(name, home, away, profile=profile, management_mode="user_controlled", controlled_team=controlled,
                 continuation={"decisions": decisions} if decisions else None, **kw)
        if r.get("terminated"):
            return r, pauses, substituted
        pause = r["pauses"][-1]
        if pause["trigger"] == "fourth_down":
            pauses.append(pause)
            choices = answer(pause)
        else:
            substituted = substituted or pause["trigger"] == "consequential_substitution"
            choices = {d["slot"]: (d.get("default") or d["eligible"][0]) for d in pause["decisions"]}
        decisions.append({"token": pause["continuation_token"], "choices": choices})
    raise AssertionError("no end after %d pauses" % limit)


def neutral_labels(result):
    """A result without what only names a decision's source (the basis, the
    state shown at a pause, the pauses and the published decision source),
    so the same decisions from either source compare equal."""
    out = copy.deepcopy(result)
    out.pop("pauses", None)
    for p in out["possessions"]:
        for d in p.get("fourth_downs") or ():
            d.pop("basis", None)
            d.pop("shown", None)
        if isinstance(p.get("fourth_down"), dict):
            p["fourth_down"].pop("decision_source", None)
    for row in out["play_ledger"]:
        if isinstance(row.get("fourth_down_decision"), dict):
            row["fourth_down_decision"].pop("basis", None)
    return out


# ---- the artifact ---------------------------------------------------------------------------------------

class ArtifactTests(unittest.TestCase):
    def test_specifications_are_pinned(self):
        self.assertEqual(fourth_down_specification.check(), [])
        self.assertEqual(ART["specification_sha256"], fourth_down_specification.FROZEN_SHA256)
        self.assertEqual(ART["pre_build_specification_sha256"], pre_build_specification.FROZEN_SHA256)
        rules = fourth_down_specification.frozen_rules()
        self.assertEqual(ART["rules"]["distance_bins"], rules["distance_bins"])
        self.assertEqual(ART["rules"]["zones"], rules["zones"])
        self.assertEqual(ART["rules"]["frozen_collapse_ladder"], rules["collapse_ladder"])
        self.assertEqual([a["id"] for a in ART["amendments"]], ["F1", "F2"])
        self.assertEqual(ART["rules"]["collapse_ladder"], ART["amendments"][1]["rungs"])
        self.assertEqual([m["state"] for m in ART["rules"]["masks"]], ["ot|trail"])
        self.assertEqual(fd.FOURTH_TAG, rules["substream"])
        self.assertEqual(fd.SOCKETS, rules["sockets"])
        self.assertEqual(list(fd.ACTIONS), rules["actions"])
        self.assertEqual(list(fd.TIMINGS), rules["timing"])
        self.assertEqual(sorted(fd.RUN_KINDS), sorted(rules["call_families"]["run"]))
        self.assertEqual(sorted(fd.PASS_KINDS), sorted(rules["call_families"]["pass"]))

    def test_every_reachable_key_reads_a_cell_of_at_least_min_cell(self):
        keys = 0
        for dbin in ART["rules"]["distance_bins"]:
            for zone in ART["rules"]["zones"]:
                if dbin[0] > zone[1]:
                    continue  # a distance beyond the goal line is unreachable
                for state in all_states():
                    keys += 1
                    key = "%s|%s|%s" % (label(dbin), label(zone), state)
                    cell = MODEL.cell_map[key]
                    self.assertGreaterEqual(sum(MODEL.counts(cell)), ART["rules"]["min_cell"], key)
        self.assertEqual(keys, len(MODEL.cell_map))
        self.assertEqual(sum(ART["chart"]["rungs"].values()), keys)

    def test_conversion_pairs_and_centres_add_up(self):
        pairs = ART["conversion"]["pairs"]
        for dbin in ART["rules"]["distance_bins"]:
            lab = label(dbin)
            self.assertEqual([pairs[lab + "|goal"][i] + pairs[lab + "|field"][i] for i in (0, 1)], pairs[lab + "|any"])
            for split in ("goal", "field"):
                target = ART["conversion"]["map"]["%s|%s" % (lab, split)]
                self.assertGreaterEqual(pairs[target][1], ART["rules"]["min_cell"])
        seasons = ART["per_season"].values()
        decisions = [sum(v["decisions"][i] for v in seasons) for i in range(3)]
        c = ART["centres"]
        self.assertEqual([c["go_share"][0], c["field_goal_share"][0], c["punt_share"][0]], decisions)
        self.assertEqual(c["go_share"][1], sum(decisions))
        self.assertEqual(c["conversion_rate"], [sum(v["conversion"][i] for v in seasons) for i in (0, 1)])
        self.assertEqual(c["attempts_per_team_game"], [decisions[0], sum(ART["team_games"].values())])
        self.assertEqual(sum(sum(row) for row in ART["state_totals"].values()), sum(decisions))
        offsets = ART["field_goal_offset"]["counts"]
        self.assertEqual(MODEL.fg_offset, int(max(offsets, key=lambda k: offsets[k])))

    def test_the_r14_mask_moves_a_trailing_overtime_punt_to_go(self):
        for distance, los in ((4, 75), (10, 45), (1, 30)):
            cell = MODEL.cell(distance, los, "ot|trail")
            g, f, p = MODEL.counts(cell)
            self.assertEqual(MODEL.chart_counts(cell, "ot|trail"), (g + p, f, 0))
            tied = MODEL.cell(distance, los, "ot|tied")
            self.assertEqual(MODEL.chart_counts(tied, "ot|tied"), MODEL.counts(tied))

    def test_the_last_two_minutes_keep_their_own_state(self):
        # Amendment F2: a thin last-two-minutes key widens its zone within its
        # own state (a W cell of that state) before its time bucket is merged;
        # its disclosure example reads its own state.
        own = merged = 0
        for key, cell in MODEL.cell_map.items():
            state = key.split("|", 2)[2]
            if not state.startswith("q4|le120|"):
                continue
            if cell.endswith("/" + state):
                own += 1
            else:
                merged += 1
                self.assertTrue(cell.endswith("/q4|le600|" + state.split("|")[2]) or cell.endswith("/neutral"), key)
        self.assertGreater(own, merged)
        self.assertTrue(any(c.split("/")[1].startswith("W") for c in MODEL.chart))
        example = ART["amendments"][1]["f1_ladder_for_the_record"]["example"]
        self.assertTrue(example["adopted_cell"].endswith("/" + example["key"].split("|", 2)[2]))
        self.assertEqual(MODEL.cell_map[example["key"]], example["adopted_cell"])

    def test_game_state_boundaries(self):
        st = MODEL.state
        self.assertEqual(st(overtime=False, game_seconds_left=601, diff=-3), "neutral")
        self.assertEqual(st(overtime=False, game_seconds_left=600, diff=-3), "q4|301-600|trail1_3")
        self.assertEqual(st(overtime=False, game_seconds_left=300, diff=-5), "q4|121-300|trail4_8")
        self.assertEqual(st(overtime=False, game_seconds_left=120, diff=0), "q4|le120|tied")
        self.assertEqual(st(overtime=False, game_seconds_left=1800 + 120, diff=7), "h1_le120")
        self.assertEqual(st(overtime=False, game_seconds_left=1800 + 121, diff=7), "neutral")
        self.assertEqual(st(overtime=False, game_seconds_left=1800, diff=7), "neutral")
        self.assertEqual(st(overtime=True, game_seconds_left=400, diff=0), "ot|tied")
        self.assertEqual(st(overtime=True, game_seconds_left=400, diff=-3), "ot|trail")
        self.assertEqual(st(overtime=True, game_seconds_left=400, diff=3), "ot|lead")

    def test_attempt_records_are_feasible_and_keep_their_family(self):
        rng = random_module.Random(7)
        for _ in range(400):
            d = rng.randint(1, 20)
            line = rng.randint(d, 99)
            for converted in (True, False):
                for family in (None, "run", "pass"):
                    for r in MODEL.attempt_records(d, line, converted, family):
                        self.assertEqual(bool(r["converted"]), converted)
                        self.assertEqual(label(MODEL.distance_bins[[b[0] <= d <= b[1] for b in
                                                                    MODEL.distance_bins].index(True)]),
                                         label(next(b for b in MODEL.distance_bins if b[0] <= r["distance"] <= b[1])))
                        if family == "run":
                            self.assertIn(r["kind"], fd.RUN_KINDS)
                        elif family == "pass":
                            self.assertIn(r["kind"], fd.PASS_KINDS)
                        if converted:
                            self.assertGreaterEqual(r["yards"], d)
                        else:
                            turnover = r["kind"] == "interception" or r["kind"].startswith("fumble_")
                            self.assertTrue(turnover or r["yards"] < d)
                            self.assertTrue(1 <= line - r["yards"] <= 99)


class PurityTests(unittest.TestCase):
    def test_no_club_identity_is_read(self):
        self.assertEqual(list(inspect.signature(fd.decide).parameters),
                         ["policy", "state", "u", "counts", "live_default"])
        tree = ast.parse(Path(fd.__file__).read_text(encoding="utf-8"))
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        names |= {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        names |= {n.arg for n in ast.walk(tree) if isinstance(n, ast.arg)}
        self.assertFalse({"team_id", "controlled_team"} & names)
        strings = {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
        self.assertFalse({"team_id", "controlled_team"} & strings)
        self.assertTrue(fd.FOURTH_TAG.endswith("-v1"))


# ---- blocks ----------------------------------------------------------------------------------------------

SHEET_RUN = A.offensive_call_sheet[0]["name"]       # 12 Ace Right, Power R (run)
SHEET_PASS = A.offensive_call_sheet[1]["name"]      # 12 Trey Right, Stick, H Chip-Release (pass)
SHORT_GO = {"id": "short-go", "source": "fixture", "otherwise": "league",
            "rules": [{"when": {"ydstogo": {"min": 1, "max": 2}, "los": {"min": 1, "max": 60}}, "decision": "go",
                       "call": SHEET_RUN},
                      {"when": {"period": [4], "margin": {"min": -16, "max": -1}, "game_seconds_max": 300},
                       "decision": "go", "call": SHEET_PASS}]}


class PolicyTests(unittest.TestCase):
    def test_frequencies_unknown_keys_and_malformed_rules_are_refused(self):
        names = fd.sheet_call_names(A.offensive_call_sheet)
        self.assertEqual(fd.policy_errors(SHORT_GO, names), [])
        bad = [
            {},
            {"rules": []},
            {"otherwise": "maybe"},
            {"otherwise": "league", "go_rate": 0.5},
            {"otherwise": "league", "mystery": 1},
            {"otherwise": "league", "rules": [{"when": {"ydstogo": [1]}, "decision": "go", "probability": 0.7}]},
            {"otherwise": "league", "rules": [{"when": {"chance": [1]}, "decision": "go"}]},
            {"otherwise": "league", "rules": [{"when": {"ydstogo": [1]}, "decision": "kick"}]},
            {"otherwise": "league", "rules": [{"when": {"ydstogo": [1]}, "decision": "punt", "call": SHEET_RUN}]},
            {"otherwise": "league", "rules": [{"when": {"ydstogo": [1]}, "decision": "go", "call": "Nowhere"}]},
            {"otherwise": "league", "rules": [{"when": {}, "decision": "go"}]},
            {"otherwise": "league", "rules": [{"when": {"period": [5]}, "decision": "go"}]},
            {"otherwise": "league", "rules": [{"when": {"los": 30}, "decision": "go"}]},
            {"otherwise": "league", "prepared_calls": {"third-and-short": "Nowhere"}},
            {"otherwise": "league", "prepared_calls": {"odds": SHEET_RUN}},
            # Review fix (October 16, 2026): a menu no fourth down matches, and
            # two spellings of one menu.
            {"otherwise": "league", "prepared_calls": {"fourth and short": SHEET_RUN}},
            {"otherwise": "league", "prepared_calls": {"second-and-long": SHEET_RUN}},
            {"otherwise": "league", "prepared_calls": {"third and short": SHEET_RUN, "3rd-and-short": SHEET_PASS}},
        ]
        for block in bad:
            self.assertTrue(fd.policy_errors(block, names), block)

    def test_prepared_call_menus_are_keyed_as_the_kernel_reads_them(self):
        names = fd.sheet_call_names(A.offensive_call_sheet)
        block = {"otherwise": "ask", "prepared_calls": {"third and short": SHEET_RUN, "Normal Down": SHEET_PASS,
                                                         "high red zone": SHEET_RUN, "goal line": SHEET_PASS}}
        self.assertEqual(fd.policy_errors(block, names), [])
        self.assertEqual(fd.canonical_policy(block)["prepared_calls"],
                         {"goal-line": SHEET_PASS, "high-red-zone": SHEET_RUN, "normal-down": SHEET_PASS,
                          "third-and-short": SHEET_RUN})

    def test_call_sheet_decisions_and_week_inputs(self):
        names = fd.sheet_call_names(A.offensive_call_sheet)
        decisions = {"two_point": DELEGATION, "kickoff": DELEGATION, "fourth_down": SHORT_GO}
        self.assertEqual(sd.sheet_errors(decisions, names), [])
        self.assertTrue(sd.sheet_errors({"fourth_down": {"otherwise": "league", "rate": 1}}))
        self.assertTrue(sd.sheet_errors({"fourth_down": SHORT_GO}, ["Other"]))
        self.assertTrue(sd.sheet_errors({"fifth_down": DELEGATION}))
        kinds = sd.decision_kinds(PROFILE_2014_6)
        self.assertEqual(kinds, ("two_point", "kickoff", "fourth_down"))
        self.assertEqual(sd.profile_kinds(PROFILE_2014_6), ("two_point", "kickoff"))
        self.assertEqual(sd.kernel_kinds("2014.6"), kinds)
        self.assertEqual(sd.kernel_kinds("2014.5"), ())
        # Optional: never required (Stone decides live without one); passed through when present.
        self.assertEqual(sd.input_policies({"two_point": DELEGATION, "kickoff": DELEGATION}, kinds),
                         {"try_policy": DELEGATION, "kickoff_policy": DELEGATION})
        self.assertEqual(sd.input_policies(decisions, kinds, names)["fourth_down_policy"], SHORT_GO)
        with self.assertRaisesRegex(ValueError, "does not decide"):
            sd.input_policies(decisions, sd.profile_kinds(PROFILE_2014_6), names)
        with self.assertRaisesRegex(ValueError, "U6"):
            sd.input_policies({"fourth_down": SHORT_GO}, kinds, names)

    def test_rewording_a_call_name_or_its_text_leaves_the_packet_identical(self):
        a = replace(A, fourth_down_policy=SHORT_GO)
        renamed = {"Power, renamed for the press": SHEET_RUN, "Stick, renamed": SHEET_PASS}
        back = {v: k for k, v in renamed.items()}
        sheet = tuple(dict(c, name=back.get(c["name"], c["name"])) for c in A.offensive_call_sheet)
        block = copy.deepcopy(SHORT_GO)
        block.update(id="another id", source="reworded")
        for rule in block["rules"]:
            rule["call"] = back[rule["call"]]
        b = replace(A, offensive_call_sheet=sheet, fourth_down_policy=block)
        # Both packet builders (the production packet and the kernel's).
        self.assertEqual(game_runner._team_packet(a), game_runner._team_packet(b))
        self.assertEqual(kernel._outcome_team(a)["fourth_down_policy"], kernel._outcome_team(b)["fourth_down_policy"])
        self.assertEqual(kernel._outcome_team(a)["fourth_down_policy"]["rules"][0]["call"]["type"], "run")
        moved = replace(A, fourth_down_policy=dict(SHORT_GO, otherwise="punt"))
        self.assertNotEqual(game_runner._team_packet(a), game_runner._team_packet(moved))

    def test_blocks_fail_closed_before_any_draw(self):
        class NoDraw(random_module.Random):
            def random(self):
                raise AssertionError("a draw was taken before the block was refused")

        ask = {"otherwise": "ask"}
        a_ask = replace(A, fourth_down_policy=ask, **U6)
        self.assertEqual(decision_block_errors(a_ask, B, profile=PROFILE_2014_6, game_type="regular",
                                               management_mode="user_controlled", controlled_team="A"), [])
        refused = [
            (dict(home=replace(A, fourth_down_policy=SHORT_GO)), PROFILE_2014_5, "regular", "does not resolve"),
            (dict(home=replace(A, fourth_down_policy=SHORT_GO)), PROFILE_2014_6, "preseason", "preseason"),
            (dict(home=replace(A, fourth_down_policy=SHORT_GO)), PROFILE_2014_6, "pro_bowl", "pro_bowl"),
            (dict(home=replace(A, fourth_down_policy=ask)), PROFILE_2014_6, "regular", "asks for a live"),
            (dict(home=replace(A, **U6), away=replace(B, fourth_down_policy=ask), management_mode="user_controlled",
                  controlled_team="A"), PROFILE_2014_6, "regular", "asks for a live"),
            (dict(home=replace(A, fourth_down_policy={"otherwise": "league", "rules": [
                {"when": {"ydstogo": [1]}, "decision": "go", "call": "Nowhere"}]})), PROFILE_2014_6, "regular",
             "not a call"),
        ]
        with mock.patch.object(kernel, "_rng", lambda seed, packet: NoDraw(0)):
            for kw, profile, game_type, message in refused:
                with self.assertRaisesRegex(ValueError, message):
                    play("b9f-refused", profile=profile, game_type=game_type, **kw)
        with self.assertRaisesRegex(ValueError, "preseason"):
            build_game_packet("pkt", "snapshot", replace(A, fourth_down_policy=SHORT_GO), B, game_type="preseason")


class DecideTests(unittest.TestCase):
    STATE = {"period": 2, "diff": 3, "seconds": 2400, "ydstogo": 1, "los": 45, "goal_to_go": False}

    def test_rules_otherwise_delegation_and_the_chart(self):
        policy = fd.canonical_policy(SHORT_GO)
        self.assertNotIn("id", policy)
        self.assertEqual(fd.decide(policy, self.STATE, 0.99, (1, 1, 1)), ("go", "policy:0", SHEET_RUN))
        late = dict(self.STATE, period=4, diff=-4, seconds=200, ydstogo=9, los=70)
        self.assertEqual(fd.decide(policy, late, 0.99, (1, 1, 1)), ("go", "policy:1", SHEET_PASS))
        far = dict(self.STATE, ydstogo=9, los=70)
        self.assertEqual(fd.decide(policy, far, 0.99, (1, 1, 1)), ("punt", "delegated:league", None))
        self.assertEqual(fd.decide(policy, far, 0.1, (1, 1, 1)), ("go", "delegated:league", None))
        self.assertEqual(fd.decide({"otherwise": "punt", "rules": []}, far, 0.0, (1, 1, 1)), ("punt", "policy:0", None))
        self.assertEqual(fd.decide(dict(policy, otherwise="field_goal"), far, 0.0, (1, 1, 1)),
                         ("field_goal", "policy:2", None))
        self.assertEqual(fd.decide(dict(policy, otherwise="ask"), far, 0.0, (1, 1, 1)), (None, "live", None))
        self.assertEqual(fd.decide(None, far, 0.0, (1, 1, 1), live_default=True), (None, "live", None))
        self.assertEqual(fd.decide(None, far, 0.3, (1, 1, 2)), ("field_goal", "league", None))

    def test_the_chart_draw(self):
        self.assertEqual([fd.choose(u, (1, 1, 2)) for u in (0.0, 0.249, 0.25, 0.499, 0.5, 0.999)],
                         ["go", "go", "field_goal", "field_goal", "punt", "punt"])
        self.assertEqual(fd.chart_probabilities((1, 1, 2)), [0.25, 0.25, 0.5])
        self.assertEqual(fd.decision_source("league"), "league_model")
        self.assertEqual(fd.decision_source("delegated:league"), "league_model")
        self.assertEqual(fd.decision_source("live"), "head_coach")
        self.assertEqual(fd.decision_source("policy:3"), "head_coach")


class NoBonusTests(unittest.TestCase):
    def test_the_conversion_socket_is_inert_at_slope_zero(self):
        self.assertTrue(all(v == 0.0 for v in fd.SOCKETS.values()))
        for distance in (1, 2, 4, 6, 9, 15):
            for goal in (True, False):
                k, n = MODEL.conversion_pair(distance, goal)
                for edge in (-3.0, 0.0, 0.7, 5.0):
                    self.assertEqual(MODEL.p_convert((k, n), edge), k / n)

    def test_the_socket_moves_the_declared_way_when_patched(self):
        pair = MODEL.conversion_pair(4, False)
        with mock.patch.dict(fd.SOCKETS, {"conversion_edge": 0.01}):
            self.assertGreater(MODEL.p_convert(pair, 1.0), pair[0] / pair[1])
            self.assertLess(MODEL.p_convert(pair, -1.0), pair[0] / pair[1])


# ---- the kernel ------------------------------------------------------------------------------------------

class KernelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.games = [play("b9f-k-%d" % i) for i in range(10)]

    def test_every_possession_records_its_decisions_and_audits_clean(self):
        decided = 0
        for r in self.games:
            self.assertEqual(clean(r), [])
            self.assertTrue(all(isinstance(p.get("fourth_downs"), list) for p in r["possessions"]))
            for p, d in records(r):
                decided += 1
                self.assertEqual(d["basis"], "league")
                state = d["state"]
                seconds = state["clock"] if p["half"] == "OT" else game_seconds(state)
                chart_state = MODEL.state(overtime=p["half"] == "OT",
                                          game_seconds_left=0 if p["half"] == "OT" else seconds,
                                          diff=state["score_diff"])
                self.assertEqual(d["cell"], MODEL.cell(state["ydstogo"], state["los"], chart_state))
                self.assertEqual(d["chart"], list(MODEL.chart_counts(d["cell"], chart_state)))
                if chart_state == "ot|trail":
                    self.assertEqual(d["chart"][2], 0)  # R14 (amendment F2)
                if d["decision"] == "go":
                    pair = MODEL.conversion_pair(state["ydstogo"], state["goal_to_go"])
                    self.assertEqual((d["conversion"], d["p_convert"]), (list(pair), pair[0] / pair[1]))
        self.assertGreater(decided, 100)

    def test_timing_names_the_third_down_snap(self):
        seen = set()
        for r in self.games:
            for p, d in records(r):
                rows = [x for x in r["play_ledger"] if x["drive"] == p["number"] and x["play_type"] in ("pass", "run")]
                before = rows[d["index"] - 1]
                self.assertEqual(before["down"], 3)
                scrimmage = not (before.get("kneel") or before.get("spike"))
                self.assertEqual(d["timing"], "before_third_down" if scrimmage else "at_fourth_down")
                seen.add(d["timing"])
        self.assertIn("before_third_down", seen)

    def test_the_decided_row_carries_the_decision(self):
        for r in self.games:
            for p, d in records(r):
                rows = [x for x in r["play_ledger"] if x["drive"] == p["number"]]
                marked = [x for x in rows if x.get("fourth_down_decision")]
                self.assertTrue(any(x["fourth_down_decision"] == {"decision": d["decision"], "basis": d["basis"],
                                                                  "timing": d["timing"], "call": d["call"]}
                                    for x in marked))
            for p in r["possessions"]:
                fourth = p.get("fourth_down") or {}
                if fourth.get("decision_source") is not None:
                    self.assertEqual(fourth["decision_source"], "league_model")

    def test_extreme_blocks_resolve_from_anywhere(self):
        # A standing go, field goal or punt from every fourth down (a live
        # answer may choose any of them anywhere): every result audits clean,
        # a decided field goal is kicked from the line plus the sourced offset
        # and every outcome kind of a go appears.
        outcomes = set()
        for action in fd.ACTIONS:
            block = {"otherwise": action}
            for i in range(6):
                r = play("b9f-x-%s-%d" % (action, i), home=replace(A, fourth_down_policy=block),
                         away=replace(B, fourth_down_policy=block))
                self.assertEqual(clean(r), [], (action, i))
                for p, d in records(r):
                    self.assertEqual((d["decision"], d["basis"]), (action, "policy:0"))
                    if action == "go":
                        outcomes.add(d["outcome"])
                    if action == "field_goal" and d["resolution"] == "model":
                        self.assertEqual(p["category"], "field_goal_attempt")
                        self.assertEqual(p["fg_distance"], d["state"]["los"] + MODEL.fg_offset)
                    if action == "punt" and d["resolution"] == "model":
                        self.assertEqual(p["category"], "punt")
        self.assertTrue({"converted", "failed", "touchdown"} <= outcomes, outcomes)

    def test_a_conversion_continues_the_possession(self):
        continued = 0
        for i in range(8):
            r = play("b9f-c-%d" % i, home=replace(A, fourth_down_policy={"otherwise": "go"}))
            for p in r["possessions"]:
                segs = p.get("segments") or []
                if not any(s["end"] == "continued" for s in segs):
                    continue
                continued += 1
                self.assertEqual(segs[0]["start"], p["start_spot"])
                for a, b in zip(segs, segs[1:]):
                    self.assertEqual(a["end"], "continued")
                    self.assertEqual(b["start"], a["start"] - a["net"])
                    self.assertLess(b["clock"], a["clock"])
                self.assertEqual(sum(s["plays"] for s in segs), p["scrimmage_plays"])
                self.assertEqual(sum(s["own_seconds"] for s in segs), p["own_seconds"])
                self.assertEqual(sum(s["net"] for s in segs), p["net_yards"])
            self.assertEqual(clean(r), [])
        self.assertGreater(continued, 3)

    def test_a_named_call_fixes_the_family_and_labels_the_snap(self):
        a = replace(A, fourth_down_policy={"otherwise": "league", "rules": [
            {"when": {"ydstogo": {"min": 1, "max": 3}}, "decision": "go", "call": SHEET_RUN},
            {"when": {"ydstogo": {"min": 4}}, "decision": "go", "call": SHEET_PASS}]})
        labelled = 0
        for i in range(6):
            r = play("b9f-call-%d" % i, home=a)
            self.assertEqual(clean(r), [])
            for p, d in records(r, "A"):
                self.assertEqual(d["decision"], "go")
                family = fd.RUN_KINDS if d["call"] == SHEET_RUN else fd.PASS_KINDS
                self.assertIn(d["kind"], family)
                pair = MODEL.conversion_pair(d["state"]["ydstogo"], d["state"]["goal_to_go"])
                self.assertEqual(d["p_convert"], pair[0] / pair[1])  # the call never moves it
                rows = [x for x in r["play_ledger"] if x["drive"] == p["number"] and x["play_type"] in ("pass", "run")]
                row = rows[d["index"]]
                self.assertEqual(row["fourth_down_decision"]["call"], d["call"])
                if row.get("label_source") == "sheet:fourth-down-call":
                    labelled += 1
                    self.assertEqual(row["concept"], d["call"])
        self.assertGreater(labelled, 0)

    def test_overtime_and_postseason_resolve(self):
        for i in range(4):
            r = play("b9f-post-%d" % i, game_type="postseason")
            self.assertEqual(clean(r), [])


class IsolationTests(unittest.TestCase):
    """Live fourth downs draw their decision and outcome uniforms on the keyed
    fourth-down-v1 substream: every possession before the first one a
    decision changed equals its B9-level run (without the flag) apart from
    the append-only records, and a game no decision changed equals it
    whole."""

    def test_unchanged_possessions_equal_the_branch_off_run(self):
        whole = prefixes = 0
        # Batch B11: a decision-free game is rarer than one in 24 on these
        # labels (b9f-iso-34 is the first), so the scan covers 35.
        for i in range(35):
            name = "b9f-iso-%d" % i
            on, off = play(name), play(name, profile=PROFILE_B9)
            x, y = strip_2014_6_fields(on), strip_2014_6_fields(off)
            first = next((k for k, p in enumerate(on["possessions"]) if p.get("segments")), None)
            if first is None:
                whole += 1
                self.assertEqual(x, y, name)
                continue
            prefixes += 1
            self.assertEqual(x["possessions"][:first], y["possessions"][:first], name)
            drives = {p["number"] for p in on["possessions"][:first]}
            self.assertEqual([r for r in x["play_ledger"] if r["drive"] in drives],
                             [r for r in y["play_ledger"] if r["drive"] in drives], name)
        self.assertGreater(prefixes, 5)
        self.assertGreater(whole, 0)


# ---- the live decision -----------------------------------------------------------------------------------

def chart_answers(reference, team, otherwise=None):
    """An answer function giving, at each pause, the decision the chart made
    at the same point of ``reference`` (the same drive and segment); a point
    the reference lacks takes ``otherwise`` (None: an error)."""
    made = {(p["number"], d["segment"]): d["decision"] for p, d in records(reference, team)}

    def answer(pause):
        key = (pause["drive"], pause["segment"])
        if otherwise is not None:
            return {"fourth_down": made.get(key, otherwise)}
        return {"fourth_down": made[key]}
    return answer


class LiveTests(unittest.TestCase):
    def test_the_pause_shows_only_what_the_staff_supply(self):
        a = replace(A, **U6)
        kw = dict(seed=SEED + b"-b9f-show", event_id="b9f-show", _test_profile=PROFILE_2014_6,
                  management_mode="user_controlled", controlled_team="A")
        r = resolve_game(a, B, **kw)
        decisions = []
        while r["pauses"][-1]["trigger"] != "fourth_down":
            pause = r["pauses"][-1]
            decisions.append({"token": pause["continuation_token"],
                              "choices": {d["slot"]: d["eligible"][0] for d in pause["decisions"]}})
            r = resolve_game(a, B, continuation={"decisions": decisions}, **kw)
        pause = r["pauses"][-1]
        self.assertFalse(r["terminated"])
        self.assertNotIn("final_score", r)
        self.assertEqual(set(pause), {"trigger", "team", "drive", "segment", "timing", "period", "clock", "score",
                                      "timeouts", "timeouts_as_of", "situation", "kicking", "conversion_call",
                                      "drive_so_far", "decisions", "continuation_token"})
        self.assertEqual(pause["team"], "A")
        self.assertIn(pause["timing"], fd.TIMINGS)
        self.assertEqual(pause["situation"]["down"], 3 if pause["timing"] == "before_third_down" else 4)
        self.assertEqual(pause["kicking"]["field_goal_distance"],
                         pause["situation"]["yardline_100"] + MODEL.fg_offset)
        self.assertEqual(set(pause["kicking"]), {"field_goal_distance", "from", "kicker", "punter", "venue", "home",
                                                 "weather"})
        self.assertEqual(pause["decisions"][0], {"slot": "fourth_down", "eligible": list(fd.ACTIONS)})
        # The sample sheet declares no menus: every call of it is Tice's menu.
        names = fd.sheet_call_names(A.offensive_call_sheet)
        self.assertEqual(pause["decisions"][1], {"slot": "call", "eligible": list(dict.fromkeys(names)),
                                                 "with": "go"})
        self.assertEqual(pause["conversion_call"]["prepared"], None)  # the sheet names none: none is invented
        shown = copy.deepcopy(pause)
        shown["conversion_call"].pop("calls")  # call names are the sheet's own words
        shown["decisions"][1].pop("eligible")
        text = json.dumps(shown).lower()
        for word in FORBIDDEN:
            self.assertNotIn(word, text)
        # The drive so far is walked states only: no player and no later snap.
        snaps = pause["drive_so_far"]["snaps"]
        self.assertTrue(all(set(s) == {"down", "ydstogo", "yardline_100", "play", "yards", "first_down"}
                            for s in snaps))
        # Answers are checked against the pause.
        token = pause["continuation_token"]
        for choices in ({"fourth_down": "go"}, {"fourth_down": "go", "call": "Nowhere"},
                        {"fourth_down": "punt", "call": names[0]}, {"fourth_down": "kneel"}, {"call": names[0]}):
            with self.assertRaises(ValueError, msg=choices):
                resolve_game(a, B, continuation={"decisions": decisions + [{"token": token, "choices": choices}]},
                             **kw)
        with self.assertRaises(ValueError):
            resolve_game(a, B, continuation={"decisions": decisions + [{"token": "0" * 64,
                                                                         "choices": {"fourth_down": "punt"}}]}, **kw)

    def test_tices_prepared_call_reaches_the_pause_and_a_policy_go(self):
        # Review fix (October 16, 2026): menus spelled as the sheets spell
        # them reach the kernel's lookup, at a live pause and on a block's go.
        menus = ["third and short", "third and medium", "third and long", "normal down"]
        sheet = tuple(dict(c, menus=menus) for c in A.offensive_call_sheet)
        prepared = {"third and short": SHEET_RUN, "3rd-and-medium": SHEET_PASS, "Third and Long": SHEET_PASS}
        by_menu = {"third-and-short": SHEET_RUN, "third-and-medium": SHEET_PASS, "third-and-long": SHEET_PASS}

        def menu_of(ydstogo):
            return "third-and-short" if ydstogo <= 2 else "third-and-medium" if ydstogo <= 5 else "third-and-long"
        a = replace(A, offensive_call_sheet=sheet, fourth_down_policy={"otherwise": "ask", "prepared_calls": prepared},
                    **U6)
        r, pauses, _ = live(a, B, "A", lambda pause: {"fourth_down": "punt"}, name="b9f-prepared")
        self.assertTrue(pauses)
        for pause in pauses:
            call = pause["conversion_call"]
            self.assertEqual(call["menu"], menu_of(pause["situation"]["ydstogo"]))
            self.assertEqual(call["prepared"], by_menu[call["menu"]])
        a = replace(a, fourth_down_policy={"otherwise": "go", "prepared_calls": prepared})
        r = play("b9f-prepared-go", a, B, management_mode="user_controlled", controlled_team="A")
        self.assertTrue(r["terminated"])
        self.assertEqual(clean(r), [])
        gos = [d for _, d in records(r, "A") if d["decision"] == "go"]
        self.assertTrue(gos)
        for d in gos:
            self.assertEqual(d["call"], by_menu[menu_of(d["state"]["ydstogo"])], d["state"])

    def test_the_drive_so_far_reconciles_with_its_penalty_records(self):
        # Review fix (October 16, 2026): the drive summary lists the replayed
        # records already enforced, so its scrimmage and penalty yards add to
        # the start less the spot shown.
        from scripts.close_week import _fourth_down_lines
        a = replace(A, offensive_call_sheet=(), **U6)
        with_records = 0
        for i in range(6):
            r, pauses, _ = live(a, B, "A", lambda pause: {"fourth_down": "punt"}, name="b9f-sofar-%d" % i)
            self.assertEqual(clean(r), [])
            for pause in pauses:
                so_far = pause["drive_so_far"]
                self.assertEqual(set(so_far), {"start_yardline_100", "snaps", "penalties", "penalty_yards"})
                scrimmage = sum(snap["yards"] for snap in so_far["snaps"])
                self.assertEqual(so_far["start_yardline_100"] - scrimmage - so_far["penalty_yards"],
                                 pause["situation"]["yardline_100"], pause["drive"])
                self.assertEqual(so_far["penalty_yards"], sum(e["yards"] for e in so_far["penalties"]))
                for entry in so_far["penalties"]:
                    self.assertEqual(set(entry), {"type", "fouled_by", "status", "yards", "first_down",
                                                  "after_snaps"})
                    self.assertLessEqual(entry["after_snaps"], len(so_far["snaps"]))
                if so_far["penalties"]:
                    with_records += 1
                    text = "\n".join(_fourth_down_lines(pause))
                    self.assertIn("%d penalty yards" % so_far["penalty_yards"], text)
        self.assertGreater(with_records, 0)

    def test_live_answers_decide_and_the_other_club_takes_the_chart(self):
        a = replace(A, offensive_call_sheet=(), **U6)
        cycle = ["go", "punt", "field_goal"]
        answers = []

        def answer(pause):
            answers.append(cycle[len(answers) % 3])
            return {"fourth_down": answers[-1]}
        r, pauses, _ = live(a, B, "A", answer, name="b9f-live")
        self.assertEqual(clean(r), [])
        self.assertTrue(pauses)
        mine = [d for _, d in records(r, "A")]
        self.assertEqual([d["decision"] for d in mine], answers)
        self.assertTrue(all(d["basis"] == "live" for d in mine))
        self.assertTrue(all(d["basis"] == "league" for _, d in records(r, "B")))
        self.assertEqual([d["timing"] for d in mine], [p["timing"] for p in pauses])
        for p in r["possessions"]:
            fourth = p.get("fourth_down") or {}
            if p["team"] == "A" and fourth.get("decision_source") and p.get("fourth_downs"):
                if p["fourth_downs"][-1].get("terminal"):
                    self.assertEqual(fourth["decision_source"], "head_coach")

    def test_the_same_decision_sequence_from_either_side_gives_the_same_result(self):
        # The label swap: the chart's decisions supplied as the controlling
        # coach's live answers, by either club, reproduce the autonomous game
        # exactly (apart from what names the source): the decision source is
        # an input, never a probability shift. Sheets without calls (a call
        # would fix a go's family) and both clubs on U6 delegations.
        a, b = replace(A, offensive_call_sheet=(), **U6), replace(B, offensive_call_sheet=(), **U6)
        compared = 0
        for i in range(8):
            name = "b9f-swap-%d" % i
            auto = play(name, a, b)
            same = [auto]
            for club in ("A", "B"):
                r, pauses, substituted = live(a, b, club, chart_answers(auto, club), name=name)
                if substituted:
                    break  # a substitution pause is a coach's choice of its own
                self.assertEqual(len(pauses), len(records(auto, club)))
                self.assertTrue(all(d["basis"] == "live" for _, d in records(r, club)))
                same.append(r)
            else:
                compared += 1
                self.assertEqual(neutral_labels(same[1]), neutral_labels(auto), name)
                self.assertEqual(neutral_labels(same[2]), neutral_labels(auto), name)
        self.assertGreater(compared, 2)

    def test_a_different_answer_changes_only_what_follows(self):
        a = replace(A, offensive_call_sheet=(), **U6)
        auto = play("b9f-diff", a, B)
        chart = chart_answers(auto, "A", otherwise="punt")
        first = []

        def flip_first(pause):
            choice = chart(pause)
            if not first:
                first.append(pause)
                choice = {"fourth_down": "punt" if choice["fourth_down"] != "punt" else "go"}
            return choice
        r, pauses, substituted = live(a, B, "A", flip_first, name="b9f-diff")
        self.assertFalse(substituted)
        drive = first[0]["drive"]
        before = lambda res: [p for p in neutral_labels(res)["possessions"] if p["number"] < drive]
        self.assertEqual(before(r), before(auto))
        self.assertNotEqual(neutral_labels(r), neutral_labels(auto))
        self.assertEqual(clean(r), [])

    def test_a_block_with_otherwise_ask_asks_only_where_no_rule_decides(self):
        block = {"otherwise": "ask", "rules": [{"when": {"ydstogo": {"min": 5}}, "decision": "punt"}]}
        a = replace(A, offensive_call_sheet=(), fourth_down_policy=block, **U6)
        r, pauses, _ = live(a, B, "A", lambda pause: {"fourth_down": "go"}, name="b9f-ask")
        self.assertEqual(clean(r), [])
        mine = [d for _, d in records(r, "A")]
        self.assertTrue(pauses)
        for d in mine:
            if d["state"]["ydstogo"] >= 5:
                self.assertEqual((d["decision"], d["basis"]), ("punt", "policy:0"))
            else:
                self.assertEqual((d["decision"], d["basis"]), ("go", "live"))
        self.assertEqual(len(pauses), sum(d["basis"] == "live" for d in mine))

    def test_preseason_and_autonomous_games_take_the_chart(self):
        for kw in (dict(game_type="preseason", management_mode="user_controlled", controlled_team="A"),
                   dict()):
            r = play("b9f-chart", **kw)
            self.assertTrue(r["terminated"])
            self.assertTrue(all(d["basis"] == "league" for _, d in records(r)))


class AuditTests(unittest.TestCase):
    def test_band_rows_read_the_artifact_and_grade_only_the_chart(self):
        games = [play("b9f-band-%d" % i) for i in range(10)]
        team_games, rows = bands.audit_fourth_down([receipt(g) for g in games], cohort="2014.6")
        self.assertEqual(team_games, 20)
        by = {m: (o, c, t, s) for m, o, c, t, s in rows}
        c = ART["centres"]
        self.assertEqual(by["fourth-down go share of chart decisions"][1], c["go_share"][0] / c["go_share"][1])
        self.assertEqual(by["fourth-down conversion rate"][1], c["conversion_rate"][0] / c["conversion_rate"][1])
        self.assertEqual(by["fourth-down attempts per team-game (team-games decided by the chart)"][1],
                         c["attempts_per_team_game"][0] / c["attempts_per_team_game"][1])
        total = sum(len(p.get("fourth_downs") or ()) for g in games for p in g["possessions"])
        self.assertEqual(by["fourth-down decisions per team-game (informational)"][0], total / 20)
        self.assertEqual(bands.audit_fourth_down([receipt(g) for g in games], cohort="2014.5"), (0, []))
        # A club's block is counted apart and never moves a graded row.
        blocked = [play("b9f-band-%d" % i, home=replace(A, fourth_down_policy={"otherwise": "go"}))
                   for i in range(10)]
        _, rows = bands.audit_fourth_down([receipt(g) for g in blocked], cohort="2014.6")
        by = {m: (o, c_, t, s) for m, o, c_, t, s in rows}
        chart = [d for g in blocked for _, d in records(g, "B")]
        self.assertEqual(by["fourth-down go share of chart decisions"][0],
                         sum(d["decision"] == "go" for d in chart) / len(chart))
        apart = [m for m in by if m.startswith("fourth downs decided by a club's block")][0]
        self.assertEqual(by[apart][0], sum(len(records(g, "A")) for g in blocked))


class ViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        a = replace(A, fourth_down_policy={"otherwise": "league", "rules": [
            {"when": {"ydstogo": {"min": 1, "max": 3}}, "decision": "go", "call": SHEET_RUN}]})
        cls.result = play("b9f-views", home=a)
        assert clean(cls.result) == []

    def test_rendered_markdown_never_shows_a_basis_cell_or_probability(self):
        import importlib
        from runtime import gamebook
        from runtime.statbook import aggregate_receipts
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
        forbidden = ("basis", "policy:", "delegated", "league chart", "p_convert", "probab", "odds", "before_third_down",
                     "at_fourth_down", "fourth_down_decision", "fourth-down-call", "conversion pair")
        for text in texts:
            for word in forbidden:
                self.assertNotIn(word, text)
        # The gamebook's fourth-down efficiency counts the decided go snaps.
        view = gamebook.GameView(rc, "A")
        made, tried = view.fourth_down("A")
        gos = [d for _, d in records(self.result, "A") if d["decision"] == "go"]
        self.assertEqual(tried, len(gos))
        self.assertEqual(made, sum(d["outcome"] in CONVERTED for d in gos))

    def test_the_calibration_audit_carries_the_fourth_down_rows(self):
        import importlib
        render_stats = importlib.import_module("scripts.render_season_stats")
        receipts = [receipt(play("b9f-cal-%d" % i)) for i in range(8)]
        for rc in receipts:
            rc["season"] = 2014
        text = "\n".join(render_stats._base_cohort_lines("2014.6", receipts, "none"))
        self.assertIn("### Fourth-down rows", text)
        self.assertIn("fourth-down go share of chart decisions", text)


if __name__ == "__main__":
    unittest.main()
