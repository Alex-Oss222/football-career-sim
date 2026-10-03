"""Kernel 2014.6 batch B6, W5a: the public clock detail (records only).

Snap stamps from the base's gap table on the public-clock-detail-v1
substream, kicks at start - own + kick length, timeout rows seated after
clock-running snaps and two-minute-warning rows, under the profile flag
clock_detail_v1. A/B invariance with a stamper switch, Pro Bowl and overtime
warnings, no timeout after a terminal snap, and render checks. Synthetic
seeds only; no career state.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import play_detail as pd
from runtime.calibration_base import BASE_2010_2014W4
from runtime.gamebook import render as render_gamebook
from runtime.kernel import resolve_game, validate_result
from runtime.profiles import PROFILE_2014_5, PROFILE_2014_6, Profile
from runtime.statbook import KERNEL_2014_6_LEDGER_ROWS, aggregate_receipts, make_receipt
from synthetic_games import SEED, sample_teams
from test_profiles import strip_2014_6_fields

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

MODEL = BASE_2010_2014W4.field_position()
W5A = MODEL.clock_detail
# The stamper switch: the same kernel without the two records-only flags.
RECORDS_OFF = Profile("2014.6", base="2010_2014w4", cell_rules="2014.6", strength=PROFILE_2014_6.strength,
                      flags=PROFILE_2014_6.flags - {"clock_detail_v1", "substitution_record"}, record_base=True)
NEW_ROWS = set(KERNEL_2014_6_LEDGER_ROWS)
INVARIANCE_GAMES = 600


def play(i, profile, tag="w5a", **kw):
    a, b = sample_teams()
    return resolve_game(a, b, seed=SEED + b"-b6-%s-%03d" % (tag.encode(), i), event_id="b6-%s-%d" % (tag, i),
                        _test_profile=profile, **kw)


def seconds_of(row, overtime=False):
    return pd._row_seconds(row, overtime)


def outcome(result):
    """Everything but the records the two flags add: the final score, the
    possessions (less the fourth-down decision marker), kicks, injuries,
    team and player counters, and the scrimmage rows' players and yards."""
    out = strip_2014_6_fields(result)
    out.pop("substitutions", None)
    out.pop("diagnostics", None)
    out.pop("play_call_stats", None)
    for row in out["play_ledger"]:
        # Stamps and situation labels move with the stamper; the football does not.
        for key in ("period", "game_clock", "situation", "concept", "family", "personnel", "formation", "motion",
                    "protection", "tags", "label_source", "label_type", "label_groups", "script_position",
                    "scramble", "carrier_group", "target_group", "sequence", "snap_in_drive"):
            row.pop(key, None)
    return out


class InvarianceTests(unittest.TestCase):
    """The stamper and the substitution record change no outcome, credit or
    exposure: 600 games under the full profile and under the switch agree on
    everything but the records (W5a and W2a, plan B6 gate)."""

    @classmethod
    def setUpClass(cls):
        cls.pairs = [(play(i, PROFILE_2014_6, "inv"), play(i, RECORDS_OFF, "inv")) for i in range(INVARIANCE_GAMES)]

    def test_outcome_credit_and_exposure_invariant(self):
        for on, off in self.pairs:
            self.assertEqual(validate_result(on), [])
            self.assertEqual(outcome(on), outcome(off))
            # Exposure: the injury draws read the slot model's hazard, so an
            # identical injury list over 600 games means an identical hazard.
            self.assertEqual(on["injuries"], off["injuries"])
            self.assertEqual({t: {p: (l["offensive_snaps"], l["defensive_snaps"], l["special_teams_snaps"])
                                  for p, l in s["players"].items()} for t, s in on["team_stats"].items()},
                             {t: {p: (l["offensive_snaps"], l["defensive_snaps"], l["special_teams_snaps"])
                                  for p, l in s["players"].items()} for t, s in off["team_stats"].items()})

    def test_switch_removes_exactly_the_records(self):
        on, off = self.pairs[0]
        self.assertTrue(any(r["play_type"] in NEW_ROWS for r in on["play_ledger"]))
        self.assertFalse(any(r["play_type"] in NEW_ROWS for r in off["play_ledger"]))
        self.assertTrue(all("decision_source" in p["fourth_down"] for p in on["possessions"] if p["fourth_down"]))
        self.assertFalse(any("decision_source" in p["fourth_down"] for p in off["possessions"] if p["fourth_down"]))
        self.assertTrue(all("entrant" in s for s in on["substitutions"]))
        self.assertFalse(any("entrant" in s for s in off["substitutions"]))

    def test_2014_5_carries_no_record(self):
        r = play(0, PROFILE_2014_5, "inv")
        self.assertFalse(any(r["play_type"] in NEW_ROWS for r in r["play_ledger"]))
        self.assertFalse(any("decision_source" in (p["fourth_down"] or {}) for p in r["possessions"]))
        for p in r["possessions"]:
            rows = [x for x in r["play_ledger"] if x["drive"] == p["number"] and x["play_type"] in ("pass", "run")]
            own = p["own_seconds"]
            for i, row in enumerate(rows, 1):
                self.assertEqual(pd._row_seconds(row, p["half"] == "OT"), p["start_clock"] - round(own * i / len(rows)))


class StampTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.games = [play(i, PROFILE_2014_6) for i in range(40)]

    def rows(self, result, number):
        return [r for r in result["play_ledger"] if r["drive"] == number]

    def test_stamps_allocate_the_drive_s_own_seconds(self):
        for r in self.games:
            self.assertEqual(validate_result(r), [])
            for p in r["possessions"]:
                rows = self.rows(r, p["number"])
                ot = p["half"] == "OT"
                scrim = [x for x in rows if x["play_type"] in ("pass", "run")]
                if not scrim:
                    continue
                stamps = [seconds_of(x, ot) for x in scrim]
                self.assertEqual(stamps[0], p["start_clock"])
                self.assertEqual(stamps, sorted(stamps, reverse=True))
                own_end = p["start_clock"] - p["own_seconds"]
                self.assertGreaterEqual(stamps[-1], own_end)
                kicks = [x for x in rows if x["play_type"] in ("punt", "field_goal")]
                if kicks:
                    kick = seconds_of(kicks[0], ot)
                    length = MODEL.kick_length(p["category"])
                    expected = min(length, p["own_seconds"])
                    if p["own_seconds"] - expected < len(scrim):
                        expected = max(0, p["own_seconds"] - len(scrim))
                    self.assertEqual(kick, own_end + expected)
                    self.assertGreaterEqual(stamps[-1], kick)
                if p["own_seconds"] >= len(scrim):
                    # Every gap at least 1 s: distinct, decreasing stamps.
                    self.assertEqual(len(set(stamps)), len(stamps))
                    if kicks:
                        self.assertGreater(stamps[-1], seconds_of(kicks[0], ot))

    def test_new_rows_carry_their_fields(self):
        seen = set()
        for r in self.games:
            for row in r["play_ledger"]:
                if row["play_type"] in NEW_ROWS:
                    seen.add(row["play_type"])
                    for key in ("drive", "sequence", "period", "game_clock", "offense", "defense", "decision_source"):
                        self.assertIn(key, row)
                    self.assertEqual(row["decision_source"], pd.LEAGUE_MODEL)
                    if row["play_type"] == pd.TIMEOUT_ROW:
                        self.assertIn(row["team"], (row["offense"], row["defense"]))
                    else:
                        self.assertEqual(row["game_clock"], "2:00")
            for p in r["possessions"]:
                if p["fourth_down"]:
                    self.assertEqual(p["fourth_down"]["decision_source"], pd.LEAGUE_MODEL)
        self.assertEqual(seen, NEW_ROWS)

    def test_timeout_rows_match_charged_timeouts_and_never_follow_a_terminal_snap(self):
        total = fallbacks = 0
        for r in self.games:
            for p in r["possessions"]:
                rows = self.rows(r, p["number"])
                timeouts = [x for x in rows if x["play_type"] == pd.TIMEOUT_ROW]
                total += len(timeouts)
                self.assertEqual(sum(x["team"] == p["team"] for x in timeouts), p["timeouts"][2])
                self.assertEqual(sum(x["team"] != p["team"] for x in timeouts), p["timeouts"][3])
                for index, row in enumerate(rows):
                    if row["play_type"] != pd.TIMEOUT_ROW:
                        continue
                    before = next((rows[j] for j in range(index - 1, -1, -1)
                                   if rows[j]["play_type"] not in (pd.TIMEOUT_ROW, pd.TWO_MINUTE_WARNING_ROW)), None)
                    if before is None or before["play_type"] in ("kickoff", "free_kick"):
                        # The counted fallback: no clock-running snap to follow, so
                        # the timeout sits before the drive's first snap.
                        fallbacks += 1
                        self.assertEqual(row["snap_in_drive"], 0)
                    else:
                        self.assertIn(before["play_type"], ("pass", "run"))
                        self.assertFalse(before.get("touchdown") or before.get("turnover"), (p["number"], index))
                        self.assertTrue(before["play_type"] == "run" or before.get("completion") or before.get("sack"))
                    # Stamped with the clock of the next snap or the kick (the clock is stopped).
                    after = next((rows[j] for j in range(index + 1, len(rows))
                                  if rows[j]["play_type"] in ("pass", "run", "punt", "field_goal")), None)
                    if after is not None:
                        self.assertEqual((row["period"], row["game_clock"]), (after["period"], after["game_clock"]))
            self.assertEqual([e for e in pd.audit_only_errors(r) if e.startswith("timeout_rows_mismatch")], [])
        self.assertGreater(total, 100)
        self.assertEqual(fallbacks, sum(r["diagnostics"].get("timeout_seat_fallback", 0) for r in self.games))
        self.assertLess(fallbacks, total / 10)

    def test_two_minute_warnings_once_per_crossed_period(self):
        for r in self.games:
            warnings = [x for x in r["play_ledger"] if x["play_type"] == pd.TWO_MINUTE_WARNING_ROW]
            periods = [x["period"] for x in warnings]
            self.assertEqual(periods[:2], [2, 4])
            self.assertEqual(len(set(periods)), len(periods))
            overtime = [p for p in r["possessions"] if p["half"] == "OT"]
            crossed = any(p["start_clock"] > 120 >= p["end_clock"] for p in overtime)
            self.assertEqual("OT" in periods, crossed)
            self.assertEqual([e for e in pd.audit_only_errors(r) if e.startswith("two_minute_warning_missing")], [])
            # Seated where the stamps cross 2:00: the rows before are later than 2:00.
            for w in warnings:
                index = r["play_ledger"].index(w)
                ot = isinstance(w["period"], str)
                mark = seconds_of(w, ot)
                earlier = [x for x in r["play_ledger"][:index] if x["drive"] == w["drive"]]
                later = [x for x in r["play_ledger"][index + 1:] if x["drive"] == w["drive"]
                         and x["play_type"] in ("pass", "run", "punt", "field_goal")]
                self.assertTrue(all(seconds_of(x, ot) > mark for x in earlier))
                self.assertTrue(all(seconds_of(x, ot) <= mark for x in later))

    def test_pro_bowl_warnings_in_all_four_quarters(self):
        a, b = sample_teams()
        r = resolve_game(a, b, seed=SEED + b"-b6-probowl", event_id="b6-probowl", venue="neutral",
                         game_type="pro_bowl", _test_profile=PROFILE_2014_6)
        self.assertEqual(validate_result(r), [])
        warnings = [x["period"] for x in r["play_ledger"] if x["play_type"] == pd.TWO_MINUTE_WARNING_ROW]
        self.assertEqual(warnings[:4], [1, 2, 3, 4])
        self.assertEqual(pd.two_minute_marks(False, True), [2820, 1920, 1020, 120])
        self.assertEqual(pd.clock_context(2800, False, True), "inside_2_min")
        self.assertEqual(pd.clock_context(2800, False, False), "normal")

    def test_postseason_overtime_marks(self):
        from runtime.rules import RULES
        bound, length = RULES.postseason_ot_period_bound, RULES.postseason_ot_seconds
        marks = pd.two_minute_marks(("OT", bound, length), False)
        self.assertEqual(len(marks), bound)
        self.assertEqual(marks[0], (bound - 1) * length + 120)
        self.assertEqual([pd._period_clock(m, overtime=("OT", bound, length)) for m in marks[:2]],
                         [("OT", "2:00"), ("OT2", "2:00")])
        found = None
        for i in range(60):
            r = play(i, PROFILE_2014_6, "post", game_type="postseason")
            if any(p["half"] == "OT" for p in r["possessions"]):
                found = r
                break
        if found is None:
            self.skipTest("no postseason overtime in 60 synthetic games")
        self.assertEqual(validate_result(found), [])
        self.assertEqual([e for e in pd.audit_only_errors(found) if e.startswith("two_minute_warning_missing")], [])

    def test_no_scrimmage_snap_at_zero(self):
        for r in self.games:
            self.assertEqual([e for e in pd.audit_only_errors(r) if e.startswith("snap_at_zero")], [])

    def test_sack_gap_is_keyed_by_kernel_version(self):
        self.assertIn("sack_2014w4|normal", W5A["gap_seconds"])
        normal_2014 = pd.gap_seconds(W5A, "sack", "normal", "sack_2014w4")
        normal_2013 = pd.gap_seconds(W5A, "sack", "normal", "sack_2010_2013")
        self.assertNotEqual(normal_2014, normal_2013)
        table = W5A["gap_seconds"]
        self.assertAlmostEqual(normal_2014, table["sack_2014w4|normal"][0] / table["sack_2014w4|normal"][1])
        pooled_run = (table["run|normal"][0] + table["run_oob|normal"][0]) / (
            table["run|normal"][1] + table["run_oob|normal"][1])
        self.assertAlmostEqual(pd.gap_seconds(W5A, "run", "normal", "sack_2014w4"), pooled_run)
        # A missing cell falls back to the kind's pooled mean.
        self.assertNotIn("spike|normal", table)
        self.assertGreater(pd.gap_seconds(W5A, "spike", "normal", "sack_2014w4"), 0)

    def test_gap_allocation_and_exemption(self):
        self.assertEqual(sum(pd._allocate_gaps([3.0, 1.0, 1.0], 10, None)), 10)
        self.assertEqual(pd._allocate_gaps([30.0, 1.0, 1.0], 3, None), [1, 1, 1])
        diagnostics = {}
        self.assertEqual(sum(pd._allocate_gaps([2.0, 2.0, 2.0], 2, diagnostics)), 2)
        self.assertEqual(diagnostics["clock_gap_exempt"], 1)
        stamps, kick = pd.clock_stamps(W5A, [], [], start_clock=1000, own=0, kick_length=18)
        self.assertEqual((stamps, kick), ([], 1000))
        stamps, kick = pd.clock_stamps(W5A, ["run"], [False], start_clock=1000, own=11, kick_length=18)
        self.assertEqual((stamps, kick), ([1000], 1000 - 11 + 10))


class RenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = play(3, PROFILE_2014_6, "render")
        cls.receipt = make_receipt(cls.result, week=5, matchup="B at A", detail="full")
        cls.compact = make_receipt(cls.result, week=5, matchup="B at A", detail="compact_stats")

    def test_full_receipt_carries_records_and_compact_does_not(self):
        self.assertTrue(any(r["play_type"] in NEW_ROWS for r in self.receipt["play_ledger"]))
        self.assertEqual(self.receipt["substitutions"], self.result["substitutions"])
        self.assertNotIn("substitutions", self.compact)
        self.assertNotIn("play_ledger", self.compact)

    def test_gamebook_and_box_score_render(self):
        text = render_gamebook(self.receipt, "A")
        self.assertIn("#### Scoring summary", text)
        self.assertIn("#### Snap counts", text)
        import render_box_score
        self.assertTrue(render_box_score.render(self.receipt, "A", 2014).startswith("####"))
        self.assertIn("#### Team comparison", render_box_score.render(self.receipt, "A", 2013))
        self.assertTrue(render_box_score.render(self.compact, "A", 2014))

    def test_statbook_counts_scrimmage_rows_only(self):
        book = aggregate_receipts([self.receipt])
        scrimmage = sum(1 for r in self.receipt["play_ledger"] if r["play_type"] in ("pass", "run"))
        self.assertEqual(book["plays_recorded"], scrimmage)
        self.assertEqual(book["teams"]["A"]["kernel_2014_6_games"], 1)
        self.assertEqual(sum(p["scrimmage_plays"] for p in self.result["possessions"]), scrimmage)

    def test_check_ledger_and_coherence_accept_the_rows(self):
        from runtime import bands
        self.assertEqual(pd.check_ledger(self.receipt), [])
        checked, counts = bands.coherence([self.receipt], cohort="2014.6")
        self.assertEqual(checked, 1)
        self.assertEqual([c for c, n, _ in counts if n], [])
        self.assertNotIn("kick_clock_shared", [c for c, _, _ in counts])
        checked, audit = bands.audit_only_coherence([self.receipt], cohort="2014.6")
        self.assertEqual([c for c, _, _ in audit], list(pd.B6_CLASSES))
        self.assertTrue(all(m == 1 for _, _, m in audit))
        # Rendered coherence tables of the closed cohorts never list them.
        self.assertNotIn("kick_clock_shared", pd.classes_for_cohort("2014.5"))

    def test_spike_row_is_informational(self):
        from runtime import bands
        team_games, rows = bands.audit_field_position([self.receipt] * 15, cohort="2014.6")
        row = next(r for r in rows if r[0].startswith("spikes stamped with more than"))
        self.assertIn(row[4], ("INFORMATIONAL", "INSUFFICIENT SAMPLE"))
        self.assertIsNone(row[3])


if __name__ == "__main__":
    unittest.main()
