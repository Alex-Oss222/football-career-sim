"""Kernel 2014.6 batch B8: possession sequencing.

The five alternation sites take the next possessor from the event that ended
the last possession; a kickoff is one link of a kick chain; the overtime
history is rules.ot_history over possessions and kicks; results and receipts
carry the kick summary and scoring_events, which the audit rebuilds and
compares. No branch fires in production until batches B9 and B10, so the
test-only _test_scoring hook forces each branch here. Synthetic seeds only;
the private service is never contacted.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import copy
import dataclasses
import unittest

from runtime import field_position as fp
from runtime import game_runner, play_detail
from runtime.calibration_base import BASE_2010_2014W4
from runtime.kernel import _start_kind, resolve_game, validate_result
from runtime.play_detail import (KICK_SUMMARY_FIELDS, check_ledger, expected_start_kind, kicks_of,
                                 measurable_classes, scoring_events)
from runtime.profiles import PROFILE_2014_5, PROFILE_2014_6, Profile
from runtime.rules import (KICK_CHAIN_BOUND, RETAINED_START_KINDS, kick_score, kicking_club, ot_history,
                           ot_status, possession_score)
from runtime.statbook import make_receipt
from synthetic_games import SEED, sample_teams
from test_profiles import strip_2014_6_fields

A, B = sample_teams()
# A synthetic seed whose regulation ends level under PROFILE_2014_6 (found by
# search; the test fails loudly if it no longer does).
OT_NAME = "b8-ot-30"
NO_SEQUENCING = Profile("2014.6", base=PROFILE_2014_6.base, cell_rules=PROFILE_2014_6.cell_rules,
                        strength=PROFILE_2014_6.strength,
                        flags=PROFILE_2014_6.flags - {"possession_sequencing"}, record_base=True)


def play(name, forced=None, profile=PROFILE_2014_6, **kw):
    return resolve_game(A, B, seed=SEED + b"-" + name.encode(), event_id=name, _test_profile=profile,
                        _test_scoring=forced, **kw)


def receipt(result, detail="compact_stats"):
    return make_receipt(result, week=5, matchup="B at A", detail=detail)


def clean(result):
    """Result and compact receipt both validate and audit clean."""
    errors = validate_result(result) + check_ledger(result) + check_ledger(receipt(result))
    return errors


def other(team):
    return "B" if team == "A" else "A"


class RulesTests(unittest.TestCase):
    def test_possession_score(self):
        self.assertEqual(possession_score({"category": "touchdown", "team": "A", "xp_made": True}), ("touchdown", "A", 7))
        self.assertEqual(possession_score({"category": "touchdown", "team": "A", "xp_made": None}), ("touchdown", "A", 6))
        self.assertEqual(possession_score({"category": "field_goal_attempt", "team": "A", "fg_made": True}),
                         ("field_goal", "A", 3))
        self.assertIsNone(possession_score({"category": "field_goal_attempt", "team": "A", "fg_made": False}))
        self.assertEqual(possession_score({"category": "safety", "team": "A"}, "B"), ("safety", "B", 2))
        self.assertIsNone(possession_score({"category": "punt", "team": "A"}))
        # A defensive touchdown recorded on the possession is the defense's score.
        p = {"category": "interception", "team": "A",
             "non_offensive_score": {"kind": "touchdown", "team": "B", "points": 7}}
        self.assertEqual(possession_score(p), ("touchdown", "B", 7))
        self.assertEqual(kick_score({"outcome": "returned_touchdown", "receiving": "A", "points": 6}), ("touchdown", "A", 6))
        self.assertEqual(kick_score({"touchdown": True, "scoring_team": "A", "xp_made": True}), ("touchdown", "A", 7))
        self.assertIsNone(kick_score({"outcome": "returned", "receiving": "A"}))
        self.assertEqual(kicking_club("touchdown", "A", "B"), "A")
        self.assertEqual(kicking_club("field_goal", "A", "B"), "A")
        self.assertEqual(kicking_club("safety", "A", "B"), "B")

    def test_ot_history_plain_possessions(self):
        possessions = [{"number": 20, "half": "OT", "team": "A", "category": "punt"},
                       {"number": 21, "half": "OT", "team": "B", "category": "field_goal_attempt", "fg_made": True}]
        self.assertEqual(ot_history(possessions), [{"team": "A", "score": None}, {"team": "B", "score": "field_goal"}])
        self.assertEqual(ot_history(possessions + [{"number": 5, "half": 2, "team": "A", "category": "touchdown"}]),
                         ot_history(possessions))
        self.assertEqual(ot_status(ot_history(possessions)), "end")

    def test_ot_history_defensive_touchdown(self):
        possessions = [{"number": 20, "half": "OT", "team": "A", "category": "interception",
                        "non_offensive_score": {"kind": "touchdown", "team": "B", "points": 6}}]
        history = ot_history(possessions)
        self.assertEqual(history, [{"team": "A", "score": "touchdown", "scoring_team": "B"}])
        self.assertEqual(ot_status(history), "end")

    def test_ot_history_kick_entries(self):
        kicks = [{"kick_no": 9, "half": "OT", "drive": 20, "kicking": "A", "receiving": "B", "outcome": "retained"}]
        possessions = [{"number": 20, "half": "OT", "team": "A", "category": "field_goal_attempt", "fg_made": True}]
        history = ot_history(possessions, kicks)
        # The receiving club is considered to have had its opportunity (R4):
        # its scoreless entry comes first, and the kicker's field goal wins.
        self.assertEqual([(e["team"], e["score"]) for e in history], [("B", None), ("A", "field_goal")])
        self.assertEqual(ot_status(history), "end")
        # A later retained kick, once the receiving club has possessed, adds nothing.
        later = [{"kick_no": 10, "half": "OT", "drive": 22, "kicking": "A", "receiving": "B", "outcome": "retained"}]
        possessions = [{"number": 20, "half": "OT", "team": "B", "category": "punt"},
                       {"number": 21, "half": "OT", "team": "A", "category": "touchdown", "xp_made": None}]
        self.assertEqual(len(ot_history(possessions, later)), 2)
        # An opening kickoff returned for a touchdown: zero possessions, a complete history.
        kicks = [{"kick_no": 9, "half": "OT", "drive": 20, "kicking": "A", "receiving": "B",
                  "outcome": "returned_touchdown", "points": 6}]
        history = ot_history([], kicks)
        self.assertEqual(history, [{"team": "B", "score": "touchdown", "kick": 9}])
        self.assertEqual(ot_status(history), "end")
        # Kicks sort before the possession whose number they carry, by kick number.
        kicks = [{"kick_no": 11, "half": "OT", "drive": 21, "kicking": "B", "receiving": "A", "outcome": "returned_touchdown",
                  "points": 7},
                 {"kick_no": 10, "half": "OT", "drive": 21, "kicking": "A", "receiving": "B", "outcome": "returned_touchdown",
                  "points": 7}]
        possessions = [{"number": 20, "half": "OT", "team": "A", "category": "field_goal_attempt", "fg_made": True}]
        history = ot_history(possessions, kicks)
        self.assertEqual([e.get("kick") for e in history], [None, 10, 11])
        self.assertEqual(ot_history([], []), [])


class HookTests(unittest.TestCase):
    def test_hook_requires_the_sequencing_flag(self):
        with self.assertRaises(ValueError):
            play("b8-hook-2014-5", {"kicks": {1: "retained"}}, profile=PROFILE_2014_5)
        with self.assertRaises(ValueError):
            play("b8-hook-off", {"kicks": {1: "retained"}}, profile=NO_SEQUENCING)
        with self.assertRaises(ValueError):
            play("b8-hook-shape", {"onside": {1: "x"}})
        with self.assertRaises(ValueError):
            play("b8-hook-branch", {"kicks": {1: "fumble"}})
        with self.assertRaises(ValueError):
            play("b8-hook-drive", {"drives": {1: "safety"}})

    def test_production_runner_cannot_pass_the_hook(self):
        self.assertEqual(game_runner.architecture_errors(), [])


class ForcedKickBranchTests(unittest.TestCase):
    def test_retained_opening_kickoff(self):
        r = play("b8-retained-open", {"kicks": {1: "retained"}})
        self.assertEqual(clean(r), [])
        k = r["kickoffs"][0]
        self.assertEqual((k["outcome"], k["chain"], k["after_drive"], k["drive"], k["basis"]), ("retained", 1, None, 1, "league"))
        self.assertFalse(k["returned"])
        first = r["possessions"][0]
        # The kicking club keeps the ball, in its own frame.
        self.assertEqual(first["team"], k["kicking"])
        self.assertNotEqual(first["team"], r["opening_receiver"])
        self.assertEqual(first["start_kind"], "kickoff_retained")
        self.assertEqual(first["start_spot"], 100 - (35 + k["kick_yards"] - k["return_yards"]) + k["enforcement"])
        self.assertEqual(_start_kind(k), "kickoff_retained")
        # The second half is still kicked off by the opening receiver.
        second = next(j for j in r["kickoffs"] if j["half"] == 2 and j["after_drive"] is None)
        self.assertEqual(second["kicking"], r["opening_receiver"])
        self.assertIn("possession_sequence_break", measurable_classes(r))
        row = next(x for x in r["play_ledger"] if x["play_type"] == "kickoff")
        self.assertTrue(row["turnover"])
        self.assertEqual(row["outcome"], "retained")
        self.assertFalse(sum(s["kick_returns"] for s in r["team_stats"].values()) > len(r["kickoffs"]) - 1)

    def test_retained_free_kick_fails_closed_without_a_record(self):
        # The base holds no retained safety free kick (0 of 65); the forced
        # branch cannot invent one. Find a safety drive to force it on.
        base = play("b8-safety-11")
        safety = next(p for p in base["possessions"] if p["category"] == "safety" and p.get("kickoff_after"))
        kick = next(k for k in base["kickoffs"] if k["after_drive"] == safety["number"])
        # The club scored upon free-kicks to the scorer, who possesses next.
        self.assertTrue(kick["free_kick"])
        self.assertEqual(kick["kicking"], safety["team"])
        self.assertEqual(base["possessions"][safety["number"]]["team"], other(safety["team"]))
        self.assertEqual(base["possessions"][safety["number"]]["start_kind"], "free_kick")
        with self.assertRaises(ValueError):
            play("b8-safety-11", {"kicks": {kick["kick_no"]: "retained"}})

    def test_opening_kick_returned_for_a_touchdown(self):
        r = play("b8-td-open", {"kicks": {1: "touchdown"}})
        self.assertEqual(clean(r), [])
        first, second = r["kickoffs"][:2]
        receiver = r["opening_receiver"]
        self.assertEqual((first["outcome"], first["touchdown"], first["scoring_team"], first["next_start"]),
                         ("returned_touchdown", True, receiver, None))
        self.assertIn(first["points"], (6, 7))
        self.assertEqual(first["xp_made"], first["points"] == 7)
        # The scorer kicks off next on the same chain; the original kicker possesses first.
        self.assertEqual((second["chain"], second["after_drive"], second["drive"], second["kicking"]), (2, None, 1, receiver))
        self.assertEqual(r["possessions"][0]["team"], other(receiver))
        self.assertEqual(r["scoring_events"][0], {"kind": "touchdown", "team": receiver, "points": first["points"],
                                                  "half": 1, "source": "kick", "kick_no": 1})
        self.assertEqual(r["scoring_events"], scoring_events(r))
        # The try row is anchored to the kick and credited to the scorer's kicker.
        tries = [x for x in r["play_ledger"] if x["play_type"] == "extra_point" and x.get("anchor")]
        self.assertEqual(len(tries), 1)
        self.assertEqual((tries[0]["anchor"], tries[0]["offense"], tries[0]["made"]), ({"kick": 1}, receiver, first["xp_made"]))
        self.assertEqual(r["team_stats"][receiver]["extra_point_attempts"],
                         sum(1 for p in r["possessions"] if p["team"] == receiver and p["xp_made"] is not None) + 1)
        kick_row = next(x for x in r["play_ledger"] if x["play_type"] == "kickoff")
        self.assertTrue(kick_row["touchdown"])
        self.assertEqual(kick_row["scoring_team"], receiver)
        # The second-half kicker is still the opening receiver.
        h2 = next(j for j in r["kickoffs"] if j["half"] == 2 and j["after_drive"] is None)
        self.assertEqual(h2["kicking"], receiver)

    def test_two_return_touchdowns_in_a_row(self):
        r = play("b8-td-twice", {"kicks": {1: "touchdown", 2: "touchdown"}})
        self.assertEqual(clean(r), [])
        chain = [k for k in r["kickoffs"] if k["drive"] == 1]
        self.assertEqual([k["chain"] for k in chain], [1, 2, 3])
        self.assertEqual([k["touchdown"] for k in chain], [True, True, False])
        self.assertEqual(chain[1]["kicking"], chain[0]["receiving"])
        self.assertEqual(chain[2]["kicking"], chain[1]["receiving"])
        self.assertEqual(r["possessions"][0]["team"], chain[2]["receiving"])
        self.assertEqual([e["source"] for e in r["scoring_events"][:2]], ["kick", "kick"])
        points = {t: sum(e["points"] for e in r["scoring_events"] if e["team"] == t) for t in r["final_score"]}
        self.assertEqual(points, r["final_score"])

    def test_kick_chain_bound_fails_closed(self):
        with self.assertRaises(RuntimeError):
            play("b8-td-bound", {"kicks": {i: "touchdown" for i in range(1, KICK_CHAIN_BOUND + 1)}})

    def test_return_touchdown_after_a_score(self):
        base = play("b8-td-mid")
        scoring = next(p for p in base["possessions"] if p.get("kickoff_after") and p["category"] == "touchdown")
        kick_no = next(k["kick_no"] for k in base["kickoffs"] if k["after_drive"] == scoring["number"])
        r = play("b8-td-mid", {"kicks": {kick_no: "touchdown"}})
        self.assertEqual(clean(r), [])
        k, nxt = r["kickoffs"][kick_no - 1], r["kickoffs"][kick_no]
        self.assertEqual((k["touchdown"], k["after_drive"], nxt["after_drive"], nxt["chain"]),
                         (True, scoring["number"], scoring["number"], 2))
        # The scoring possession's kickoff_after describes the chain's last kick.
        p = r["possessions"][scoring["number"] - 1]
        self.assertEqual(p["kickoff_after"]["next_start"], nxt["next_start"])
        self.assertEqual(p["next_start"], nxt["next_start"])
        self.assertEqual(r["possessions"][scoring["number"]]["team"], nxt["receiving"])


class ForcedDriveBranchTests(unittest.TestCase):
    def turnover(self, name, game_type="regular"):
        base = play(name, game_type=game_type)
        p = next((p for p in base["possessions"] if p["category"] in ("interception", "fumble_lost")
                  and p is not base["possessions"][-1]), None)
        if p is None:
            self.skipTest("no turnover in the synthetic game")
        return p["number"]

    def test_defensive_touchdown_regulation(self):
        n = self.turnover("b8-dtd")
        r = play("b8-dtd", {"drives": {n: "defensive_touchdown"}})
        self.assertEqual(clean(r), [])
        p, q = r["possessions"][n - 1], r["possessions"][n]
        defense = other(p["team"])
        self.assertEqual(p["non_offensive_score"]["team"], defense)
        self.assertEqual(p["non_offensive_score"]["kind"], "touchdown")
        self.assertIn(p["category"], ("interception", "fumble_lost"))
        self.assertEqual(possession_score(p), ("touchdown", defense, p["non_offensive_score"]["points"]))
        # The defense kicks off to the same offense: the possessor repeats.
        if p["half"] == q["half"]:
            self.assertEqual(q["team"], p["team"])
            self.assertIn(q["start_kind"], ("kickoff", "kickoff_touchback"))
            kick = next(k for k in r["kickoffs"] if k["after_drive"] == n)
            self.assertEqual((kick["kicking"], kick["receiving"]), (defense, p["team"]))
            self.assertEqual(p["next_start"], kick["next_start"])
        event = next(e for e in r["scoring_events"] if e.get("drive") == n)
        self.assertEqual(event["team"], defense)
        tries = [x for x in r["play_ledger"] if x["play_type"] == "extra_point" and x.get("anchor") == {"drive": n}]
        self.assertEqual(len(tries), 1 if p["non_offensive_score"]["xp_made"] is not None else 0)
        if tries:
            self.assertEqual(tries[0]["offense"], defense)
        # The compact receipt carries the score through the drives summary.
        rc = receipt(r)
        drives = [dict(zip(play_detail.DRIVE_SUMMARY_FIELDS, row)) for row in rc["drives"]]
        self.assertEqual(drives[n - 1]["non_offensive_score"], p["non_offensive_score"])
        self.assertEqual(scoring_events(rc), r["scoring_events"])

    def test_pro_bowl_defensive_touchdown_places_the_scored_upon_club(self):
        n = self.turnover("b8-pb-dtd", game_type="pro_bowl")
        r = play("b8-pb-dtd", {"drives": {n: "defensive_touchdown"}}, game_type="pro_bowl")
        self.assertEqual(clean(r), [])
        p, q = r["possessions"][n - 1], r["possessions"][n]
        self.assertEqual(r["kickoffs"], [])
        if p.get("quarter") == q.get("quarter"):
            self.assertEqual((q["team"], q["start_kind"], q["start_spot"]), (p["team"], "placement", 75))
        self.assertEqual(p["next_start"], 75)


class OvertimeSequencingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = play(OT_NAME)
        if not any(p["half"] == "OT" for p in cls.base["possessions"]):
            raise AssertionError("%s no longer reaches overtime; pick another seed" % OT_NAME)
        cls.opener = next(k["kick_no"] for k in cls.base["kickoffs"] if k["half"] == "OT")

    def test_opening_kick_returned_for_a_touchdown_ends_overtime(self):
        r = play(OT_NAME, {"kicks": {self.opener: "touchdown"}})
        self.assertEqual(clean(r), [])
        ot = [p for p in r["possessions"] if p["half"] == "OT"]
        self.assertEqual(ot, [])
        last = r["kickoffs"][-1]
        self.assertEqual((last["half"], last["touchdown"], last["xp_made"], last["points"]), ("OT", True, None, 6))
        self.assertEqual(r["scoring_events"][-1]["source"], "kick")
        winner = last["scoring_team"]
        self.assertGreater(r["final_score"][winner], r["final_score"][other(winner)])
        history = ot_history(ot, [k for k in r["kickoffs"] if k["half"] == "OT"])
        self.assertEqual(history, [{"team": winner, "score": "touchdown", "kick": last["kick_no"]}])
        self.assertEqual(ot_status(history), "end")
        # No try after a walk-off, no extra kick after the game ended.
        self.assertFalse([x for x in r["play_ledger"] if x["play_type"] == "extra_point" and x.get("anchor")])
        self.assertEqual(len([k for k in r["kickoffs"] if k["half"] == "OT"]), 1)

    def test_retained_opening_kick_gives_the_receiving_club_its_opportunity(self):
        r = play(OT_NAME, {"kicks": {self.opener: "retained"}})
        self.assertEqual(clean(r), [])
        ot = [p for p in r["possessions"] if p["half"] == "OT"]
        kick = r["kickoffs"][self.opener - 1]
        self.assertEqual(kick["outcome"], "retained")
        self.assertEqual(ot[0]["team"], kick["kicking"])
        self.assertEqual(ot[0]["start_kind"], "kickoff_retained")
        history = ot_history(ot, [k for k in r["kickoffs"] if k["half"] == "OT"])
        self.assertEqual(history[0], {"team": kick["receiving"], "score": None, "kick": self.opener,
                                      "opportunity": "kicking-club recovery (R4)"})
        self.assertEqual(history[1]["team"], kick["kicking"])
        # The game ended exactly where the rule ends it.
        self.assertEqual(ot_status(history), "end")
        self.assertNotEqual(ot_status(history[:-1]), "end")


class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = play("b8-td-twice", {"kicks": {1: "touchdown", 2: "touchdown"}})
        cls.receipt = receipt(cls.result)

    def test_receipts_carry_the_kicks_summary_and_events(self):
        rc = self.receipt
        self.assertEqual(len(rc["kicks"]), len(self.result["kickoffs"]))
        self.assertEqual(len(rc["kicks"][0]), len(KICK_SUMMARY_FIELDS))
        rows = kicks_of(rc)
        self.assertEqual([k["kick_no"] for k in rows], [k["kick_no"] for k in self.result["kickoffs"]])
        self.assertEqual(rows[0]["points"], self.result["kickoffs"][0]["points"])
        self.assertEqual(rc["scoring_events"], self.result["scoring_events"])
        self.assertEqual(scoring_events(rc), self.result["scoring_events"])
        self.assertIn("kick_chain_incoherent", measurable_classes(rc))
        full = receipt(self.result, "full")
        self.assertEqual(full["kicks"], rc["kicks"])
        self.assertEqual(check_ledger(full), [])
        # A 2014.5 receipt measures neither class and carries neither field.
        old = receipt(play("b8-old", profile=PROFILE_2014_5))
        self.assertNotIn("kicks", old)
        self.assertFalse(set(play_detail.B8_CLASSES) & measurable_classes(old))

    def test_stored_events_are_compared_not_trusted(self):
        rc = copy.deepcopy(self.receipt)
        rc["scoring_events"][0]["points"] = 99
        self.assertTrue(any(e.startswith("score_identity_violations: stored scoring_events") for e in check_ledger(rc)))
        rc = copy.deepcopy(self.result)
        rc["scoring_events"] = []
        self.assertTrue(any(e.startswith("score_identity_violations: stored scoring_events") for e in check_ledger(rc)))

    def test_kick_chain_incoherent(self):
        rc = copy.deepcopy(self.receipt)
        index = KICK_SUMMARY_FIELDS.index
        # The second link kicked by the wrong club.
        rc["kicks"][1][index("kicking")], rc["kicks"][1][index("receiving")] = (
            rc["kicks"][1][index("receiving")], rc["kicks"][1][index("kicking")])
        self.assertTrue(any(e.startswith("kick_chain_incoherent") for e in check_ledger(rc)))
        # A hand-over to the wrong spot.
        rc = copy.deepcopy(self.receipt)
        rc["kicks"][2][index("next_start")] += 1
        self.assertTrue(any("next start" in e for e in check_ledger(rc) if e.startswith("kick_chain_incoherent")))
        # A kick after a non-scoring drive.
        rc = copy.deepcopy(self.receipt)
        drives = [dict(zip(play_detail.DRIVE_SUMMARY_FIELDS, row)) for row in rc["drives"]]
        kick = next(k for k in kicks_of(rc) if k["after_drive"] is not None)
        scoring = drives[kick["after_drive"] - 1]
        if scoring["category"] == "touchdown":
            rc["drives"][kick["after_drive"] - 1][play_detail.DRIVE_SUMMARY_FIELDS.index("category")] = "punt"
            self.assertTrue(any(e.startswith("kick_chain_incoherent") for e in check_ledger(rc)))

    def test_possession_sequence_break(self):
        rc = copy.deepcopy(self.receipt)
        team = play_detail.DRIVE_SUMMARY_FIELDS.index("team")
        half = play_detail.DRIVE_SUMMARY_FIELDS.index("half")
        # Swap the possessor of a mid-half possession that followed a non-scoring drive.
        drives = [dict(zip(play_detail.DRIVE_SUMMARY_FIELDS, row)) for row in rc["drives"]]
        for i in range(1, len(drives)):
            if drives[i]["half"] == drives[i - 1]["half"] and possession_score(drives[i - 1]) is None:
                rc["drives"][i][team] = other(rc["drives"][i][team])
                break
        errors = check_ledger(rc)
        self.assertTrue(any(e.startswith("possession_sequence_break") for e in errors), errors)
        # The old alternation class is not used for this cohort.
        self.assertFalse(any("repeats the offense" in e for e in errors))
        del half

    def test_last_possession_kick_only_when_the_chain_ended_the_game(self):
        r = copy.deepcopy(self.result)
        last = r["possessions"][-1]
        last["kickoff_after"] = {"returned": True, "free_kick": False, "next_start": 70, "touchback": False,
                                 "enforcement": 0}
        self.assertTrue(any(e.startswith("kickoff_after_expired_clock") for e in check_ledger(r)))


class InvarianceTests(unittest.TestCase):
    """A game in which no branch fires equals its run without the flag apart
    from the append-only records, and kernel 2014.5 carries none of them."""

    def test_flag_adds_only_the_records(self):
        for i in range(6):
            name = "b8-inv-%d" % i
            on, off = play(name), play(name, profile=NO_SEQUENCING)
            self.assertEqual(validate_result(on) + check_ledger(on), [])
            self.assertIn("scoring_events", on)
            self.assertNotIn("scoring_events", off)
            self.assertTrue(all("chain" in k for k in on["kickoffs"]))
            self.assertFalse(any("chain" in k for k in off["kickoffs"]))
            self.assertEqual(strip_2014_6_fields(on), strip_2014_6_fields(off))
            self.assertEqual(scoring_events(on), scoring_events(off))
            self.assertFalse(set(play_detail.B8_CLASSES) & measurable_classes(off))

    def test_2014_5_carries_no_record(self):
        r = play("b8-inv-0", profile=PROFILE_2014_5)
        self.assertNotIn("scoring_events", r)
        self.assertFalse(any("chain" in k for k in r["kickoffs"]))
        self.assertFalse(any("non_offensive_score" in p for p in r["possessions"]))
        self.assertEqual(len(measurable_classes(r)), 42)

    def test_scoring_events_match_the_drives(self):
        r = play("b8-inv-1")
        events = r["scoring_events"]
        self.assertTrue(all(e["source"] == "drive" for e in events))
        scored = [p for p in r["possessions"] if possession_score(p) is not None]
        self.assertEqual([e["drive"] for e in events], [p["number"] for p in scored])
        self.assertEqual({t: sum(e["points"] for e in events if e["team"] == t) for t in r["final_score"]}, r["final_score"])


class FieldPositionTests(unittest.TestCase):
    def test_adjust_punt_skips_retained_records(self):
        record = {"los": 40, "outcome": "retained", "gross": 27, "return_yards": 0, "enforcement": -8,
                  "next_start": 5, "touchback": False}
        out = fp.adjust_punt(record, 6)
        self.assertEqual(out["next_start"], 5)
        self.assertEqual(out["gross"], 27)
        returned = dict(record, outcome="returned", next_start=100 - 40 + 27 - 0 - 8)
        self.assertNotEqual(fp.adjust_punt(returned, 6)["next_start"], returned["next_start"])

    def test_punt_feasibility_in_the_right_frame(self):
        model = BASE_2010_2014W4.field_position()
        P = model.PUNT
        pool = model.data["punt_pool"]
        retained = [r for r in pool if r[P["possession"]] == "kicking"]
        self.assertEqual(len(retained), 105)
        for r in retained:
            self.assertEqual(r[P["outcome"]], "retained")
            self.assertEqual(model.punt_start(r, r[P["los"]]), r[P["next_start"]])
        for r in pool:
            if not r[P["touchback"]]:
                self.assertEqual(model.punt_start(r, r[P["los"]]), r[P["next_start"]])
                self.assertTrue(model.punt_feasible(r, r[P["los"]]))
        # From the own 2, a retained record that gives a start beyond the goal line is infeasible.
        r = retained[0]
        far = 2
        self.assertEqual(model.punt_feasible(r, far), 1 <= model.punt_start(r, far) <= 99)
        # The live punt draw still meets no retained record (R12 layer C, batch B10).
        self.assertFalse(any(r[P["possession"]] == "kicking" for r in model._punt_pool))

    def test_start_kinds(self):
        self.assertEqual(_start_kind({"free_kick": False, "touchback": False, "outcome": "retained"}), "kickoff_retained")
        self.assertEqual(_start_kind({"free_kick": True, "touchback": False, "outcome": "retained"}), "free_kick_retained")
        self.assertEqual(_start_kind({"free_kick": False, "touchback": True, "outcome": "touchback"}), "kickoff_touchback")
        self.assertEqual(_start_kind({"free_kick": False, "touchback": False, "outcome": "returned"}), "kickoff")
        self.assertEqual(expected_start_kind({"free_kick": False, "outcome": "touchback"}), "kickoff_touchback")
        self.assertEqual(expected_start_kind({"free_kick": True, "outcome": "retained"}), "free_kick_retained")
        self.assertIn("punt_retained", RETAINED_START_KINDS)


if __name__ == "__main__":
    unittest.main()
