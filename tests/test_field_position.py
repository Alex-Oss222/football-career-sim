"""Kernel 2013.7 field position: spots, transitions, late-game states, chains.

Each test names the canonical defect it guards (ledger Entries 40-41): the
Week 4 touchback touchdown of seven yards, the Week 5 touchback safety, the
Week 5 one-yard touchdown after a 34-yard unreturned punt, and the Week 5
punt at 1:56 by a club trailing by two. Synthetic seeds only; the shared
250-game sample is reused and the pure draw tests run in milliseconds.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import copy
import json
import random
import unittest

from runtime import field_position as fp
from runtime import kernel, play_detail
from runtime.kernel import TeamInput
from runtime.play_detail import DRIVE_SUMMARY_FIELDS, apply_drive_detail, check_ledger, coherence_counts
from runtime.player_evidence import empty_player_stats
from support_rosters import game_day_roster
from synthetic_games import sample

ROOT = Path(__file__).resolve().parents[1]
FOURTH = ("punt", "field_goal_attempt", "downs")
T = fp.T


def drives_of(result, number):
    return [r for r in result["play_ledger"] if r["drive"] == number and r["play_type"] in ("pass", "run")]


class FieldPositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.games = sample()

    def test_touchback_td_net_is_80(self):
        checked = 0
        for r in self.games:
            kicks = {k["drive"]: k for k in r["kickoffs"]}
            for p in r["possessions"]:
                k = kicks.get(p["number"])
                if k and k["touchback"] and not k["free_kick"] and k["enforcement"] == 0:
                    checked += 1
                    self.assertEqual(p["start_spot"], 80)
                    self.assertNotEqual(p["category"], "safety")
                    if p["category"] == "touchdown":
                        self.assertEqual(p["net_yards"], 80)
        self.assertGreater(checked, 1000)
        for pool_id in (("neutral", fp.start_bin(80)), ("h1_final", fp.h1_key(20)), ("ot", None)):
            for t in fp._static(pool_id, "touchdown", 80):
                self.assertEqual(fp.adapt("touchdown", t, 80), (80, 0))

    def test_no_safety_from_touchback(self):
        states = [(1, 1500, 0), (1, 25, 0), (2, 1200, 0), ("OT", 600, 0), ("OT", 300, -3)]
        states += [(2, window, diff) for window in (550, 250, 100, 20) for diff in (-12, -6, -2, 0, 4, 12)]
        rng = random.Random(20137)
        diagnostics = {}
        for i in range(2000):
            half, window, diff = states[i % len(states)]
            edge = (-0.06, 0.0, 0.06)[i % 3]
            drawn = fp.draw_drive(rng, 80, half, window, diff, edge, diagnostics)
            self.assertNotEqual(drawn.category, "safety")
        safeties = 0
        for r in self.games:
            for p in r["possessions"]:
                if p["category"] != "safety":
                    continue
                safeties += 1
                self.assertEqual(p["start_spot"] - p["net_yards"], 100)
                self.assertGreaterEqual(p["start_spot"], 74)
                self.assertNotEqual(p["start_spot"], 80)
                rows = drives_of(r, p["number"])
                self.assertEqual(p["start_spot"] - sum(x["result_yards"] for x in rows), 100)
                self.assertTrue(2 <= -rows[-1]["result_yards"] <= 18)
                self.assertEqual(rows[-1]["yardline"] - rows[-1]["result_yards"], 100)
        self.assertGreater(safeties, 0)

    def test_spot_chain_continuity(self):
        for r in self.games:
            ps = r["possessions"]
            by_number = {p["number"]: p for p in ps}
            for a, b in zip(ps, ps[1:]):
                if a["half"] == b["half"]:
                    self.assertEqual(b["start_spot"], a["next_start"])
            for p in ps:
                if p["category"] == "downs":
                    self.assertEqual(p["next_start"], 100 - p["end_spot"])
                if p["category"] == "field_goal_attempt" and not p["fg_made"]:
                    self.assertEqual(p["next_start"], min(80, 110 - p["fg_distance"]))
            for row in r["play_ledger"]:
                if row["play_type"] == "punt":
                    p = by_number[row["drive"]]
                    self.assertEqual(row["los"], p["end_spot"])
                    self.assertEqual(row["next_start"], p["next_start"])
                    if row["touchback"]:
                        self.assertEqual(row["next_start"], 80 + row["enforcement"])
                    else:
                        self.assertEqual(row["gross"] - row["return_yards"] + row["enforcement"],
                                         row["next_start"] - (100 - row["los"]))
                if row["play_type"] in ("kickoff", "free_kick"):
                    self.assertEqual(row["next_start"], by_number[row["drive"]]["start_spot"])
        # A 34-yard unreturned punt from any feasible line of scrimmage leaves
        # the receiving club at least 35 yards from the goal it attacks.
        records = [r for r in fp.load()["punt_pool"] if r[2] == 34 and r[3] == 0 and not r[6] and r[4] == 0]
        self.assertTrue(records)
        for los in range(33, 100):
            start = 100 - los + 34 - 0 + 0
            if 1 <= start <= 99:
                self.assertGreaterEqual(start, 35)

    def _mix(self, half, window, diff, spot, edge):
        cell = fp.cell_for(half, window, diff)
        pool_id = ("late", cell) if cell not in ("neutral", "OT") else ("ot", None)
        counts, options = fp.draw_options(pool_id, "late", spot, window)
        return fp.category_mix(counts, edge, options), options

    def test_ladder_steps_on_full_feasibility(self):
        """The same-bin rung is used only when one of its tuples fits both the
        spot and the clock; otherwise the same-zone rung supplies the drive,
        and a category is masked only when neither rung does."""
        stepped = 0
        for cell in sorted(fp.load()["late_counts"]):
            for category in fp.CATEGORIES:
                for spot in (80, 75, 65, 45, 25):
                    for window in (45, 100, 200, 290, 420, 580):
                        same, wider = fp._rungs(("late", cell), category, spot)
                        near = fp._dynamic(same, category, "late", window)
                        far = fp._dynamic(wider, category, "late", window)
                        got = fp.eligible(("late", cell), category, spot, "late", window)
                        self.assertEqual(got, near or far)
                        if same and not near and far:
                            stepped += 1
                            self.assertTrue(got)
        self.assertGreater(stepped, 0)

    def test_late_trailing_no_punt(self):
        for window in (1, 30, 61, 90, 120):
            for diff in range(-8, 0):
                for spot in range(5, 100, 7):
                    for edge in (-0.06, 0.0, 0.06):
                        probs, _ = self._mix(2, window, diff, spot, edge)
                        self.assertEqual(probs.get("punt", 0.0), 0.0, (window, diff, spot, edge))
        for spot in (70, 50, 30):
            _, options = self._mix(2, 288, -2, spot, 0.0)
            self.assertFalse([t for t in options.get("punt", ()) if t[T["term_bucket"]] == "le120"])
        for window in (30, 120, 200, 300):
            for diff in range(-8, -3):
                for spot in (60, 35, 20, 10):
                    for edge in (-0.06, 0.06):
                        probs, _ = self._mix(2, window, diff, spot, edge)
                        self.assertEqual(probs.get("field_goal_attempt", 0.0), 0.0)
        for r in self.games:
            for p in r["possessions"]:
                if p["half"] == 2 and p["start_clock"] <= 120 and -8 <= p["score_diff"] <= -1:
                    self.assertNotEqual(p["category"], "punt")
                if p["half"] == 2 and p["start_clock"] <= 300 and -8 <= p["score_diff"] <= -4:
                    self.assertNotEqual(p["category"], "field_goal_attempt")

    def test_late_terminal_state_and_decision_state(self):
        counts = coherence_counts([e for r in self.games for e in check_ledger(r)])
        self.assertEqual(counts["late_terminal_state_mismatch"], 0)
        self.assertEqual(counts["fourth_down_state_missing"], 0)
        kneeling_needs = set()
        for r in self.games:
            for p in r["possessions"]:
                if p["category"] in FOURTH:
                    fd = p["fourth_down"]
                    base = 1800 if p["half"] == 1 else 0
                    self.assertEqual(fd["los"], p["end_spot"])
                    self.assertEqual(fd["need"], fp.need(p["score_diff"]))
                    self.assertEqual(fd["decision_zone"], fp.decision_zone(p["end_spot"]))
                    self.assertEqual(fd["cell"], fp.cell_for(p["half"], p["start_clock"] - base, p["score_diff"]))
                    self.assertEqual(fd["clock_s"], p["end_clock"] - base)
                if p["half"] == 2 and p["cell"] != "neutral" and p["category"] == "end_of_game" and p["kneels"]:
                    kneeling_needs.add(fp.cell_need(p["cell"]))
        # Kneel-outs belong to clubs that are ahead or level (2012 trailing
        # one-score cells hold no kneeling clock drive).
        self.assertTrue(kneeling_needs)
        self.assertFalse(kneeling_needs & {"trail1_3", "trail4_8"})

    def test_chains_real(self):
        self.assertFalse(hasattr(kernel, "_chains"))
        for r in self.games:
            for team, s in r["team_stats"].items():
                mine = [p["chains"] for p in r["possessions"] if p["team"] == team]
                self.assertEqual(s["first_downs"], sum(c[0] + c[1] for c in mine))
                self.assertEqual(s["third_down_attempts"], sum(c[2] for c in mine))
                self.assertEqual(s["third_down_conversions"], sum(c[3] for c in mine))
            for p in r["possessions"]:
                if p["category"] == "punt":
                    self.assertGreaterEqual(p["chains"][2], 1)

    def _allocate(self, index, spot, category, runs, attempts, sacks, losses, net, kneels=(), **extra):
        roster, other = game_day_roster("X"), game_day_roster("Y")
        team = TeamInput("X", tuple(p.player_id for p in roster), roster=roster)
        defense = TeamInput("Y", tuple(p.player_id for p in other), roster=other)
        terminal = extra.get("safety_terminal")
        fixed = sum(kneels) - sum(losses) + (terminal[1] if terminal else 0)
        free_runs = runs - (1 if terminal and terminal[0] == "run" else 0)
        usable = attempts - (1 if category == "interception" else 0)
        free_total = net - fixed
        if usable and free_runs:
            pass_yards = free_total // 2
        else:
            pass_yards = free_total if usable else 0
        rush_free = free_total - pass_yards
        if extra.get("td_type") == "rush" and rush_free < 1:
            pass_yards, rush_free = pass_yards + rush_free - 1, 1
        if extra.get("td_type") == "pass" and pass_yards < 1:
            pass_yards, rush_free = 1, rush_free + pass_yards - 1
        end = spot - net
        punt = ({"los": end, "gross": 40, "return_yards": 0, "touchback": False, "enforcement": 0,
                 "outcome": "downed", "next_start": 100 - end + 40} if category == "punt" else None)
        diagnostics = {}
        ledger, _ = apply_drive_detail(
            seed=b"design-2013-7-extreme-starts-not-canonical-000", event_id="extreme-%d" % index, drive_no=1,
            team=team, defense=defense, available=roster, defenders=other,
            offense_stats={"players": empty_player_stats(roster)},
            defense_stats={"players": empty_player_stats(other)}, runs=runs, attempts=attempts, sacks=sacks,
            pass_yards=pass_yards, rush_free=rush_free, category=category, start_clock=600, end_clock=500,
            start_spot=spot, kneel_yards=list(kneels), sack_losses=losses, net_yards=net, punt_record=punt,
            fourth_down={"down": 4, "ydstogo": 5, "los": end} if category in FOURTH else None,
            diagnostics=diagnostics, **extra)
        rows = [r for r in ledger if r["play_type"] in ("pass", "run")]
        self.assertEqual(sum(r["result_yards"] for r in rows), net)
        running = 0
        for position, row in enumerate(rows):
            running += row["result_yards"]
            final = position == len(rows) - 1
            if final and category == "touchdown":
                self.assertEqual(spot - running, 0)
            elif final and category == "safety":
                self.assertEqual(spot - running, 100)
            else:
                self.assertTrue(1 <= spot - running <= 99, (category, spot, [r["result_yards"] for r in rows]))
        self.assertEqual(diagnostics.get("prefix_order_failed", 0), 0, (category, spot))

    def test_extreme_starts_allocate(self):
        index = 0
        for spot in (1, 2, 98, 99):
            keep = max(spot - 99, min(spot - 1, 12 if spot > 50 else -3))
            cases = [
                ("touchdown", 3, 2, 1, [9], spot, (), {"td_type": "rush"}),
                ("touchdown", 1, 3, 0, [], spot, (), {"td_type": "pass"}),
                ("interception", 2, 3, 1, [8], keep, (), {"turnover_type": "interception"}),
                ("fumble_lost", 2, 2, 1, [7], keep, (), {"turnover_type": "fumble_lost"}),
                ("punt", 2, 1, 1, [10], keep, (), {}),
                ("downs", 3, 2, 1, [6], keep, (), {}),
                ("field_goal_attempt", 4, 3, 2, [5, 9], keep, (), {}),
            ]
            if spot + 2 <= 99:
                cases.append(("end_of_game", 1, 0, 0, [], -2, (-1, -1), {}))
            for category, runs, attempts, sacks, losses, net, kneels, extra in cases:
                index += 1
                self._allocate(index, spot, category, runs, attempts, sacks, losses, net, kneels, **extra)
        for spot in (74, 91, 99):
            index += 1
            self._allocate(index, spot, "safety", 2, 1, 1, [], spot - 100, safety_terminal=("sack", -7))
            index += 1
            self._allocate(index, spot, "safety", 3, 0, 0, [], spot - 100, safety_terminal=("run", -10))

    def test_detectors_fire_on_canon_defects(self):
        def drive(number, team, category, start, net, **extra):
            row = {"number": number, "team": team, "half": 1, "category": category, "points": 0,
                   "scrimmage_plays": 3, "start_clock": 3600 - 100 * number, "end_clock": 3500 - 100 * number,
                   "net_yards": net, "fg_distance": None, "fg_made": None, "xp_made": None,
                   "kickoff_after": None, "half_final": False, "start_spot": start, "start_kind": "kickoff",
                   "end_spot": start - net if category not in ("touchdown", "safety") else (0 if category == "touchdown" else 100),
                   "next_start": None, "score_diff": 0, "cell": "neutral", "tuple_terminal_bucket": "gt600",
                   "chains": [0, 0, 0, 0, 0, 0], "fourth_down": None, "kneels": 0, "spikes": 0}
            row.update(extra)
            return row

        def result(*drives):
            points = {"A": 0, "B": 0}
            for d in drives:
                if d["category"] == "touchdown":
                    points[d["team"]] += 6
                if d["category"] == "safety":
                    points["B" if d["team"] == "A" else "A"] += 2
            return {"final_score": points, "game_type": "regular",
                    "drives": [[d.get(f) for f in DRIVE_SUMMARY_FIELDS] for d in drives]}

        def classes(res):
            return {e.split(":")[0] for e in check_ledger(res)}

        # Week 4 drive 1: a kickoff touchback, then a touchdown that netted 7.
        week4 = result(drive(1, "A", "touchdown", 80, 7, start_kind="kickoff_touchback", end_spot=0))
        self.assertIn("td_net_ne_start", classes(week4))
        # Week 5 drive 18: a touchback, then a safety netting -13.
        week5 = result(drive(1, "A", "safety", 80, -13, start_kind="kickoff_touchback", end_spot=100))
        found = classes(week5)
        self.assertTrue({"safety_not_at_goal_line", "safety_start_infeasible"} <= found)
        # Week 5 drives 21-22: a 34-yard unreturned punt, then a one-yard touchdown.
        punt = drive(1, "A", "punt", 70, 5, next_start=100 - 65 + 34,
                     fourth_down={"down": 4, "ydstogo": 3, "los": 65})
        td = drive(2, "B", "touchdown", 1, 1, end_spot=0)
        week5b = result(punt, td)
        self.assertIn("spot_chain_break", classes(week5b))
        # Week 5 drive 24: a punt at 1:56 by a club trailing by two, from a
        # 2012 tuple whose punt came with 121-300 seconds left.
        cell = fp.cell_for(2, 180, -2)
        late = drive(1, "A", "punt", 60, 20, half=2, start_clock=180, end_clock=116, score_diff=-2, cell=cell,
                     tuple_terminal_bucket="121-300", next_start=60,
                     fourth_down={"down": 4, "ydstogo": 4, "los": 40, "clock_s": 116, "clock_bucket": "le120",
                                  "half": 2, "score_diff": -2, "need": "trail1_3", "decision_zone": "opp_49_35",
                                  "cell": cell, "tuple_terminal_bucket": "121-300", "action": "punt"})
        self.assertIn("late_terminal_state_mismatch", classes(result(late)))

    def test_legacy_receipts_not_reclassified(self):
        from runtime.bands import coherence, cohorts
        receipts = [json.loads(p.read_text()) for p in sorted((ROOT / "career/2013/stats/game_receipts").glob("*.json"))]
        legacy, kernel_2013_6, current = cohorts(receipts)
        self.assertTrue(legacy and kernel_2013_6)
        self.assertFalse(current)
        errors = [e for r in receipts for e in check_ledger(r)]
        self.assertFalse([e for e in errors if e.split(":")[0] in play_detail.SPOT_CLASSES])
        # The committed Weeks 4-5 receipts closed with no coherence violation.
        self.assertEqual(errors, [])
        checked, counts = coherence(kernel_2013_6)
        self.assertEqual(checked, len(kernel_2013_6))
        for cls, count, measurable in counts:
            if cls in play_detail.SPOT_CLASSES:
                self.assertEqual((count, measurable), (0, 0), cls)


if __name__ == "__main__":
    unittest.main()
