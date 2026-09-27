import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import copy
import math
import re
import unittest
from unittest import mock

from runtime import drive_model, field_position, play_detail
from runtime.kernel import TeamInput, resolve_game, validate_result, ot_status
from runtime.play_detail import COHERENCE_CLASSES, _period_clock, check_ledger
from synthetic_games import EVENT_PREFIX, SEED, sample, sample_teams, team

ROOT = Path(__file__).resolve().parents[1]
SCRIMMAGE = {"pass", "run"}
KICKS = {"kickoff", "free_kick"}


def drive_rows(result, number):
    return [r for r in result["play_ledger"] if r["drive"] == number and r["play_type"] not in KICKS]


class KernelCoherenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.games = sample()

    def test_check_ledger_zero_violations(self):
        self.assertEqual(len(COHERENCE_CLASSES), 32)
        errors = [e for r in self.games for e in check_ledger(r)]
        self.assertEqual(errors, [])
        self.assertTrue(all(validate_result(r) == [] for r in self.games))
        self.assertTrue(all(play_detail.measurable_classes(r) == set(COHERENCE_CLASSES) for r in self.games))
        failures = sum(r["diagnostics"].get("prefix_order_failed", 0) for r in self.games)
        zero = sum(r["diagnostics"].get("fallback_zero_tuple", 0) for r in self.games)
        self.assertEqual((failures, zero), (0, 0))

    def test_terminal_snap_last(self):
        for r in self.games:
            for p in r["possessions"]:
                if p["category"] not in {"touchdown", "interception", "fumble_lost"}:
                    continue
                scrim = [x for x in drive_rows(r, p["number"]) if x["play_type"] in SCRIMMAGE]
                marked = [x for x in scrim if x["touchdown"] or x["turnover"]]
                self.assertEqual(len(marked), 1)
                self.assertEqual(marked[0]["snap_in_drive"], max(x["snap_in_drive"] for x in scrim))
                if p["category"] == "touchdown":
                    self.assertFalse(marked[0]["sack"])
                    self.assertGreater(marked[0]["result_yards"], 0)

    def test_every_possession_one_terminal_marker(self):
        seen = set()
        for r in self.games:
            for p in r["possessions"]:
                rows = drive_rows(r, p["number"])
                markers = [x for x in rows if x["play_type"] in {"field_goal", "punt", "safety", "possession_end"}
                           or (x["play_type"] in SCRIMMAGE and (x["touchdown"] or x["turnover"]))]
                self.assertEqual(len(markers), 1, (r["event_id"], p["number"]))
                marker = markers[0]
                expected = play_detail.MARKER_FOR[p["category"]]
                actual = marker["play_type"]
                if actual in SCRIMMAGE:
                    actual = "touchdown" if marker["touchdown"] else marker["turnover_type"]
                self.assertEqual(actual, expected)
                if actual == "possession_end":
                    self.assertEqual(marker["reason"], p["category"])
                tries = [x for x in rows if x["play_type"] == "extra_point"]
                self.assertEqual(len(tries), 1 if p["xp_made"] is not None else 0)
                seen.add(p["category"])
        for category in ("touchdown", "field_goal_attempt", "punt", "interception", "fumble_lost",
                         "downs", "safety", "end_of_half", "end_of_game"):
            self.assertIn(category, seen)

    def test_halves_bounded_and_second_half_receiver(self):
        for r in self.games:
            regulation = [p for p in r["possessions"] if p["half"] in (1, 2)]
            self.assertFalse([p for p in regulation if p["start_clock"] > 1800 > p["end_clock"]])
            first_h2 = next(p for p in regulation if p["half"] == 2)
            self.assertNotEqual(first_h2["team"], r["opening_receiver"])
            self.assertEqual(regulation[0]["team"], r["opening_receiver"])
            ledger = r["play_ledger"]
            self.assertEqual((ledger[0]["play_type"], ledger[0]["period"], ledger[0]["game_clock"]),
                             ("kickoff", 1, "15:00"))
            q3 = [x for x in ledger if x["play_type"] == "kickoff" and (x["period"], x["game_clock"]) == (3, "15:00")
                  and x["drive"] == first_h2["number"]]
            self.assertEqual(len(q3), 1)
            self.assertEqual(q3[0]["defense"], first_h2["team"])
            for half in (1, 2):
                self.assertEqual(sum(p["seconds"] for p in regulation if p["half"] == half), 1800)

    def test_half_final_possession_ends_its_window(self):
        for r in self.games:
            for half, boundary in ((1, 1800), (2, 0)):
                rows = [p for p in r["possessions"] if p["half"] == half]
                finals = [p for p in rows if p["half_final"]]
                self.assertLessEqual(len(finals), 1)
                if finals:
                    self.assertIs(finals[0], rows[-1])
                    self.assertEqual(finals[0]["end_clock"], boundary)
                    self.assertIsNone(finals[0]["kickoff_after"])

    def test_no_kickoff_after_expired_clock_or_walkoff(self):
        for r in self.games:
            poss = r["possessions"]
            ot = any(p["half"] == "OT" for p in poss)
            left = sum(1 for p in poss if p["kickoff_after"])
            kick_rows = [x for x in r["play_ledger"] if x["play_type"] in KICKS]
            self.assertEqual(len(kick_rows), 2 + ot + left)
            self.assertEqual(len(r["kickoffs"]), len(kick_rows))
            returns = sum(s["kick_returns"] for s in r["team_stats"].values())
            touchbacks = sum(1 for x in kick_rows if x["touchback"])
            self.assertEqual(len(kick_rows), returns + touchbacks)
            for p in poss:
                if p["kickoff_after"]:
                    self.assertNotIn(p["end_clock"], (1800, 0) if p["half"] in (1, 2) else (0,))
                    self.assertIsNot(p, poss[-1])
            self.assertIsNone(poss[-1]["kickoff_after"])

    def test_drive_net_consistent_with_category(self):
        long_punts = 0
        for r in self.games:
            for p in r["possessions"]:
                key = "clock" if p["category"].startswith("end_of_") else p["category"]
                envelope = field_position.load()["envelopes"][key][field_position.start_bin(p["start_spot"])]
                self.assertIsNotNone(envelope)
                if key != "touchdown":
                    self.assertTrue(envelope[0] <= p["net_yards"] <= envelope[1])
                scrim = [x for x in drive_rows(r, p["number"]) if x["play_type"] in SCRIMMAGE]
                self.assertEqual(sum(x["result_yards"] for x in scrim), p["net_yards"])
                long_punts += p["category"] == "punt" and p["net_yards"] > 37
        # Reported, not asserted: punt drives netting over the 2012 p95 (37).
        print("\n[2013.7 sample] punt drives netting over 37 yards: %d" % long_punts)

    def test_fg_and_xp_misses_and_score_identity(self):
        fga = fgm = 0
        bins = {}
        missed_fg_rows = missed_xp_rows = 0
        for r in self.games:
            for team_id, s in r["team_stats"].items():
                self.assertEqual(r["final_score"][team_id],
                                 6 * s["touchdowns"] + s["extra_points_made"] + 3 * s["field_goals"] + 2 * s["safeties"])
                fga += s["field_goal_attempts"]
                fgm += s["field_goals"]
                kicker_misses = sum(line["field_goals_attempted"] - line["field_goals_made"]
                                    for line in s["players"].values())
                rows = [x for x in r["play_ledger"] if x["play_type"] == "field_goal"
                        and x["offense"] == team_id and not x["made"]]
                self.assertEqual(kicker_misses, len(rows))
            missed_fg_rows += sum(1 for x in r["play_ledger"] if x["play_type"] == "field_goal" and not x["made"])
            missed_xp_rows += sum(1 for x in r["play_ledger"] if x["play_type"] == "extra_point" and not x["made"])
            for p in r["possessions"]:
                if p["category"] == "field_goal_attempt":
                    label = next(lab for lab, _, high in drive_model.load()["rates"]["fg_bin_edges"]
                                 if p["fg_distance"] <= high)
                    cell = bins.setdefault(label, [0, 0])
                    cell[0] += p["fg_made"]
                    cell[1] += 1
        self.assertGreater(missed_fg_rows, 0)
        self.assertGreater(missed_xp_rows, 0)
        centre = 852 / 1016
        self.assertLessEqual(abs(fgm / fga - centre), 3 * math.sqrt(centre * (1 - centre) / fga))
        rates = drive_model.load()["rates"]["fg_by_distance"]
        for label, (made, attempts) in bins.items():
            if attempts >= 30:
                p = rates[label][0] / rates[label][1]
                self.assertLessEqual(abs(made / attempts - p), 3 * math.sqrt(p * (1 - p) / attempts), label)

    def test_score_identity_legacy_fallback(self):
        legacy = copy.deepcopy(self.games[0])
        legacy["kernel_version"] = "2013.5"
        for s in legacy["team_stats"].values():
            for field in ("field_goal_attempts", "extra_point_attempts", "extra_points_made", "safeties",
                          "turnovers_on_downs", "clock_expired_drives", "kickoffs", "drives"):
                del s[field]
        for team_id, s in legacy["team_stats"].items():
            s["points"] = 7 * s["touchdowns"] + 3 * s["field_goals"]
            legacy["final_score"][team_id] = s["points"]
        self.assertNotIn("score ledger mismatch", validate_result(legacy))
        doctored = copy.deepcopy(legacy)
        first = next(iter(doctored["final_score"]))
        doctored["final_score"][first] += 1
        self.assertIn("score ledger mismatch", validate_result(doctored))
        current = copy.deepcopy(self.games[0])
        current["final_score"][first] += 1
        self.assertIn("score ledger mismatch", validate_result(current))

    def test_ot_status_table(self):
        A, B = "A", "B"
        cases = [
            ([(A, "touchdown")], "regular", False, "end"),
            ([(A, "field_goal")], "regular", False, "continue"),
            ([(A, "field_goal"), (B, "touchdown")], "regular", False, "end"),
            ([(A, "field_goal"), (B, "field_goal")], "regular", False, "continue"),
            ([(A, "field_goal"), (B, "field_goal"), (A, None)], "regular", False, "continue"),
            ([(A, "field_goal"), (B, "field_goal"), (A, None), (B, "field_goal")], "regular", False, "end"),
            ([(A, "field_goal"), (B, None)], "regular", False, "end"),
            ([(A, "safety")], "regular", False, "end"),
            ([(A, None), (B, "safety")], "regular", False, "end"),
            ([(A, None)], "regular", False, "continue"),
            ([(A, None), (B, "field_goal")], "regular", False, "end"),
            ([(A, None), (B, None)], "regular", True, "end"),
            ([(A, None), (B, None)], "postseason", True, "continue"),
            ([(A, "field_goal")], "postseason", True, "continue"),
        ]
        for history, game_type, expired, expected in cases:
            entries = [{"team": t, "score": s} for t, s in history]
            self.assertEqual(ot_status(entries, game_type, expired=expired), expected, history)

    def test_overtime_integration(self):
        ot_games = [r for r in self.games if any(p["half"] == "OT" for p in r["possessions"])]
        self.assertTrue(ot_games)
        due_next = []
        for r in ot_games:
            self.assertEqual(validate_result(r), [])
            self.assertLessEqual(sum(p["seconds"] for p in r["possessions"]), 4500)
            regulation = [p for p in r["possessions"] if p["half"] in (1, 2)]
            ot = [p for p in r["possessions"] if p["half"] == "OT"]
            due = next(t for t in r["final_score"] if t != regulation[-1]["team"])
            due_next.append(ot[0]["team"] == due)
            self.assertFalse(any(p["xp_made"] is not None for p in ot if p["category"] == "touchdown"))
        self.assertEqual(set(due_next), {True, False})

    def test_postseason_games_validate_and_never_tie(self):
        a, b = team("A"), team("B")
        for i in range(40):
            r = resolve_game(a, b, seed=SEED + b"-ps%05d" % i, event_id=f"post-{i}", game_type="postseason")
            self.assertEqual(validate_result(r), [])
            self.assertEqual(len(set(r["final_score"].values())), 2)

    def test_period_clock_boundaries(self):
        self.assertEqual(_period_clock(1800, closing=True), (2, "0:00"))
        self.assertEqual(_period_clock(1800), (3, "15:00"))
        self.assertEqual(_period_clock(2700, closing=True), (1, "0:00"))
        self.assertEqual(_period_clock(0, closing=True), (4, "0:00"))
        self.assertEqual(_period_clock(3600), (1, "15:00"))
        self.assertEqual(_period_clock(0, closing=True, overtime="OT2"), ("OT2", "0:00"))

    def test_stream_separation(self):
        calls = ({"name": "Mesh", "family": "Mesh", "type": "pass"}, {"name": "Power", "family": "Power", "type": "run"})
        renamed = ({"name": "Mesh Base", "family": "Mesh", "type": "pass"},
                   {"name": "Power Base", "family": "Power", "type": "run"})

        def build(sheet):
            a, b = team("A"), team("B")
            a = TeamInput("A", a.active_players, roster=a.roster, offensive_call_sheet=sheet)
            return a, b

        def team_level(result):
            return {t: {k: v for k, v in s.items() if k != "players"} for t, s in result["team_stats"].items()}

        for i in range(6):
            first = resolve_game(*build(calls), seed=SEED + b"-%05d" % i, event_id=f"streams-{i}")
            with mock.patch.object(play_detail, "SNAP_DETAIL_TAG", "public-snap-detail-test"), \
                    mock.patch.object(play_detail, "KICKOFF_DETAIL_TAG", "public-kickoff-detail-test"), \
                    mock.patch.object(play_detail, "LABEL_TAG", "public-call-label-test"):
                second = resolve_game(*build(renamed), seed=SEED + b"-%05d" % i, event_id=f"streams-{i}")
            self.assertEqual(first["final_score"], second["final_score"])
            self.assertEqual(first["possessions"], second["possessions"])
            self.assertEqual(first["kickoffs"], second["kickoffs"])
            self.assertEqual(team_level(first), team_level(second))
            self.assertNotEqual(first["play_ledger"], second["play_ledger"])
            self.assertEqual(validate_result(second), [])

    def test_determinism(self):
        a, b = sample_teams()
        one = resolve_game(a, b, seed=SEED + b"-00003", event_id=f"{EVENT_PREFIX}-3")
        self.assertEqual(one, self.games[3])
        from runtime.statbook import make_receipt
        self.assertEqual(make_receipt(one, week=4, matchup="B at A", detail="compact_stats")["drives"],
                         make_receipt(self.games[3], week=4, matchup="B at A", detail="compact_stats")["drives"])

    def test_protagonist_blind(self):
        for name in ("kernel.py", "drive_model.py", "field_position.py", "play_detail.py", "call_families.py"):
            text = (ROOT / "runtime" / name).read_text()
            self.assertNotRegex(text, r"team_id\s*[!=]=\s*['\"]")
            self.assertNotRegex(text, r"(?i)jacksonville|jaguars|\bJAX\b|protagonist\s*==")
        # Swapped labels under identical anchors: the same football up to the
        # home edge, measured on the home side's mean points.
        x, y = team("A"), team("B")
        home_first = [resolve_game(x, y, seed=SEED + b"-%05d" % i, event_id=f"blind-{i}")["final_score"]["A"]
                      for i in range(100)]
        home_second = [resolve_game(y, x, seed=SEED + b"-%05d" % i, event_id=f"blind-{i}")["final_score"]["B"]
                       for i in range(100)]
        mean = lambda v: sum(v) / len(v)
        spread = math.sqrt(sum((v - mean(home_first)) ** 2 for v in home_first) / 99)
        self.assertLess(abs(mean(home_first) - mean(home_second)), 4 * spread * math.sqrt(2 / 100))


if __name__ == "__main__":
    unittest.main()
