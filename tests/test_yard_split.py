"""Kernel 2014.6 batch B13: the replayed yard split (R16a, R16b) and its rows (R16c).

Under the profile flags yard_split and snap_values each replayed real drive keeps its own real
rushing and passing yards, completions and sack losses, and its own run and completion values
(runtime.yard_split): the relocation delta is split between the kinds and spread over the
non-terminal snaps by the gains-proportional rule; the placeholder gauss and randint draws are
still taken, so the possession stream is unchanged. Every centre is read from the base's
yardage artifact (library/data/2010_2014w4_yardage.json). Synthetic seeds only; the private
service is never contacted.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import itertools
import random
import unittest

from runtime import bands, yard_split
from runtime import chains as chain_walk
from runtime import kernel as kernel_module
from runtime.calibration_base import BASE_2010_2014W4
from runtime.kernel import resolve_game, validate_result
from runtime.play_detail import DRIVE_SUMMARY_FIELDS, check_ledger
from runtime.profiles import B13_FLAGS, FLAG_REQUIRES, PROFILE_2014_5, PROFILE_2014_6, Profile
from runtime.statbook import make_receipt
from synthetic_games import SEED, sample_teams

A, B = sample_teams()
FPM = BASE_2010_2014W4.field_position()
T = FPM.T
CATEGORIES = FPM.CATEGORIES


def level(flags):
    return Profile("2014.6", base=PROFILE_2014_6.base, cell_rules=PROFILE_2014_6.cell_rules,
                   strength=PROFILE_2014_6.strength, flags=frozenset(flags), record_base=True)


B13_OFF = level(PROFILE_2014_6.flags - B13_FLAGS)
SPLIT_ONLY = level(PROFILE_2014_6.flags - {"snap_values"})


def play(name, profile=PROFILE_2014_6):
    return resolve_game(A, B, seed=SEED + b"-" + name.encode(), event_id=name, _test_profile=profile)


def pool_tuples(category, limit=None, where=lambda t: True):
    """Tuples of a category in artifact order: the neutral pool's, then the
    late, first-half late and overtime pools'."""
    pools = FPM.data["pools"]
    c = CATEGORIES.index(category)
    lists = [bin_pools[c] for bin_pools in pools["neutral"]]
    for kind in ("late", "h1_late"):
        lists += [cells[category] for _, cells in sorted(pools[kind].items())]
    lists += [pools[kind][category] for kind in ("ot_first", "ot_sudden")]
    out = []
    for t in (t for lst in lists for t in lst):
        if where(t):
            out.append(t)
            if limit and len(out) >= limit:
                break
    return out


def lay(category, t, spot, *, real_on=True, values_on=True, seed=b"b13-lay", rng_seed=11):
    """One tuple laid out from `spot` as the kernel lays it out (steps 5-6b)."""
    net, _ = FPM.adapt(category, t, spot)
    free, kneel_sum, terminal_value, open_sacks = FPM.fixed_yardage(category, t)
    plan = FPM.penalty_plan(category, t)[0]
    real = yard_split.of_tuple(FPM, category, t) if real_on else None
    td_type = t[T["td_kind"]] if category == "touchdown" else None
    safety_terminal = (t[T["safety_term_kind"]], terminal_value) if category == "safety" else None
    terminal_kind = ("catch" if td_type == "pass" else "run") if category == "touchdown" else None
    scratch = {}
    rng = random.Random(rng_seed)
    losses, pass_yards, rush_free, _ = kernel_module._yard_split(
        rng, category=category, start=spot, net=net, free=free, kneel_sum=kneel_sum, terminal_value=terminal_value,
        open_sacks=open_sacks, pen_yards=plan.yards, attempts=t[T["attempts"]], runs=t[T["runs"]],
        safety_terminal=safety_terminal, td_type=td_type, yards_per_attempt=7.1, yards_per_carry=4.23,
        scratch=scratch, real=real, terminal_kind=terminal_kind)
    layout = chain_walk.drive_layout(
        seed=seed, event_id="b13", drive_no=1, offense="A", category=category, td_type=td_type,
        runs=t[T["runs"]], attempts=t[T["attempts"]], sacks=t[T["sacks"]], kneel_yards=list(t[T["kneel_yards"]]),
        spikes=t[T["spikes"]], pass_yards=pass_yards, rush_free=rush_free, losses=losses,
        safety_terminal=safety_terminal, net=net, spot=spot, completion_rate=0.61, targets=list(t[T["chains"]]),
        term_down=t[T["term_down"]], diagnostics=scratch, penalty=plan, real_split=real,
        replay_values=values_on and real is not None)
    return dict(net=net, plan=plan, real=real, layout=layout, scratch=scratch, losses=losses,
                split=(pass_yards, rush_free), safety_terminal=safety_terminal)


def completions_of(layout):
    return sum(1 for k, c in zip(layout["kinds"], layout["completed"]) if k in ("att", "catch") and c)


class RuleTests(unittest.TestCase):
    """The pure rules of the specification (section 4, Yardage)."""

    def test_gains_proportional_positive(self):
        # Each snap weighs max(gain - 3, 0) + 1: 1, 1, 8, 13 (total 23).
        values = [0, 3, 10, 15]
        out = yard_split.gains_proportional(values, 23)
        self.assertEqual(out, [1, 4, 18, 28])
        for delta in range(1, 40):
            out = yard_split.gains_proportional(values, delta)
            self.assertEqual(sum(out), sum(values) + delta)
            self.assertTrue(all(o >= v for o, v in zip(out, values)))

    def test_gains_proportional_negative_caps_then_longest(self):
        values = [2, 5, 9]                      # caps 0, 2, 6
        self.assertEqual(yard_split.gains_proportional(values, -8), [2, 3, 3])
        # Beyond the caps the rest moves one yard at a time off the longest.
        self.assertEqual(yard_split.gains_proportional(values, -10), [2, 2, 2])
        self.assertEqual(yard_split.gains_proportional(values, -11), [1, 2, 2])
        for delta in range(-30, 0):
            self.assertEqual(sum(yard_split.gains_proportional(values, delta)), sum(values) + delta)
        self.assertEqual(yard_split.gains_proportional(values, 0), values)

    def test_round_half_away_from_zero(self):
        self.assertEqual([yard_split.round_half_away(x) for x in (2.5, -2.5, 1.49, -1.5, 0.5)], [3, -3, 1, -2, 1])

    def real(self, rush=10, passing=20, completions=2, runs=(4, 6), comps=(8, 12), term=None, term_value=None):
        return yard_split.RealSplit(rush=rush, passing=passing, completions=completions, losses=(),
                                    run_values=tuple(runs), completion_values=tuple(comps), term_kind=term,
                                    term_value=term_value)

    def test_kind_split(self):
        real = self.real()
        # Pro rata: d = 6, runs take round(6 x 10 / 30) = 2.
        self.assertEqual(yard_split.kind_split(36, real, usable=3, free_runs=2), (24, 12, False))
        self.assertEqual(yard_split.kind_split(30, real, usable=3, free_runs=2), (20, 10, False))
        # No completion: all of d to the runs; no run: all to passing.
        none = self.real(completions=0, passing=0, comps=())
        self.assertEqual(yard_split.kind_split(17, none, usable=3, free_runs=2), (0, 17, False))
        self.assertEqual(yard_split.kind_split(17, real, usable=3, free_runs=0), (17, 0, False))
        self.assertEqual(yard_split.kind_split(17, real, usable=0, free_runs=2), (0, 17, False))
        self.assertEqual(yard_split.kind_split(5, real, usable=0, free_runs=0), (0, 0, False))
        # Both real totals 0: half each.
        zero = self.real(rush=0, passing=0, runs=(0, 0), comps=(0, 0))
        self.assertEqual(yard_split.kind_split(5, zero, usable=2, free_runs=2), (2, 3, False))
        # A kind whose only snap is the terminal hands its share to the other.
        td = self.real(rush=5, runs=(5,), passing=20, completions=2, term="run", term_value=5)
        self.assertEqual(yard_split.kind_split(31, td, usable=2, free_runs=1, terminal_kind="run"), (26, 5, True))

    def test_assign_keeps_the_terminal_and_the_multiset(self):
        rng = random.Random(3)
        out = yard_split.assign(rng, [0, 2, 4, 5], [7, 1, 12, 6], 26, terminal_slot=5, terminal_matches=True)
        self.assertEqual(out[5], 6)
        self.assertEqual(sorted(out[i] for i in (0, 2, 4)), [1, 7, 12])
        moved = yard_split.assign(random.Random(3), [0, 2, 4, 5], [7, 1, 12, 6], 31, terminal_slot=5,
                                  terminal_matches=True)
        self.assertEqual(moved[5], 6)
        self.assertEqual(sum(moved.values()), 31)
        # The slots must match the real values; only a kind with no other
        # slot moves its terminal.
        self.assertIsNone(yard_split.assign(rng, [0, 1], [3], 3))
        self.assertEqual(yard_split.assign(rng, [4], [9], 15, terminal_slot=4, terminal_matches=True), {4: 15})

    def test_published_bins(self):
        bins, long_completions = yard_split.published(
            ["run", "run", "run", "kneel", "att", "catch", "run"], [False, False, False, False, True, True, False],
            [-2, 0, 3, -1, 25, 19, 20])
        self.assertEqual(bins, [1, 1, 1, 0, 0, 1])
        self.assertEqual(long_completions, 1)


class PossessionStreamTests(unittest.TestCase):
    """The placeholder draws: the possession stream's state after steps 5-6
    is the same with the real split as without it, on fixtures with no
    attempt, no run, sacks only and a safety (plan B13, Tests)."""

    def state_after(self, real, **kw):
        rng = random.Random(2014)
        kernel_module._yard_split(rng, yards_per_attempt=7.1, yards_per_carry=4.23, scratch={}, real=real, **kw)
        return rng.getstate()

    def check(self, real, **kw):
        self.assertEqual(self.state_after(real, **kw), self.state_after(None, **kw))

    def test_fixtures(self):
        common = dict(kneel_sum=0, terminal_value=0, pen_yards=0, td_type=None, safety_terminal=None)
        runs_only = yard_split.RealSplit(7, 0, 0, (), (3, 4), (), None, None)
        self.check(runs_only, category="punt", start=75, net=7, free=2, open_sacks=0, attempts=0, runs=2, **common)
        passes = yard_split.RealSplit(0, 9, 1, (6,), (), (9,), None, None)
        self.check(passes, category="punt", start=75, net=3, free=3, open_sacks=1, attempts=3, runs=0, **common)
        sacks = yard_split.RealSplit(0, 0, 0, (7, 4), (), (), None, None)
        self.check(sacks, category="punt", start=75, net=-11, free=0, open_sacks=2, attempts=0, runs=0, **common)
        safety = yard_split.RealSplit(2, 0, 0, (), (2,), (), None, None)
        self.check(safety, category="safety", start=6, net=-94, free=2, open_sacks=0, attempts=1, runs=2,
                   kneel_sum=0, terminal_value=-3, pen_yards=0, td_type=None, safety_terminal=("run", -3))

    def test_sack_only_drive_keeps_its_real_losses_when_they_fit(self):
        sacks = yard_split.RealSplit(0, 0, 0, (7, 4), (), (), None, None)
        losses = kernel_module._yard_split(random.Random(1), category="punt", start=75, net=-11, free=0,
                                           kneel_sum=0, terminal_value=0, open_sacks=2, pen_yards=0, attempts=0,
                                           runs=0, safety_terminal=None, td_type=None, yards_per_attempt=7.1,
                                           yards_per_carry=4.23, scratch={}, real=sacks)[0]
        self.assertEqual(losses, [7, 4])
        scratch = {}
        moved = kernel_module._yard_split(random.Random(1), category="punt", start=75, net=-14, free=0,
                                          kneel_sum=0, terminal_value=0, open_sacks=2, pen_yards=0, attempts=0,
                                          runs=0, safety_terminal=None, td_type=None, yards_per_attempt=7.1,
                                          yards_per_carry=4.23, scratch=scratch, real=sacks)[0]
        self.assertEqual(moved, [9, 5])
        self.assertEqual(scratch["real_sack_losses_moved"], 1)


class ReplayTests(unittest.TestCase):
    """The real split on real tuples laid out directly."""

    def test_real_start_replays_the_real_split(self):
        checked = 0
        for category in ("touchdown", "punt", "field_goal_attempt", "interception", "downs"):
            for t in pool_tuples(category, limit=40):
                plan = FPM.penalty_plan(category, t)[0]
                if FPM.value(t, "other_yards") != plan.yards or plan.post or plan.kick_row:
                    continue
                out = lay(category, t, t[T["start"]])
                real = out["real"]
                self.assertEqual(out["split"], (real.passing, real.rush), category)
                self.assertEqual(out["losses"], list(real.losses))
                lay_ = out["layout"]
                if not lay_["ok"]:
                    continue
                self.assertEqual(completions_of(lay_), real.completions)
                if not {"chain_split_repaired", "chain_layout_repaired", "chain_plan_concentrated"} & set(out["scratch"]):
                    runs = sorted(v for k, v in zip(lay_["kinds"], lay_["values"]) if k == "run")
                    self.assertEqual(runs, sorted(real.run_values))
                checked += 1
        self.assertGreater(checked, 100)

    def test_reconciliation(self):
        """Interception, fumble, safety, kneel and spike drives: the snaps and
        records net the drive, each kind carries its plan's total, the
        completions are the real count plus any forced one."""
        groups = (("interception", lambda t: True), ("fumble_lost", lambda t: True), ("safety", lambda t: True),
                  ("clock", lambda t: bool(t[T["kneel_yards"]])), ("touchdown", lambda t: t[T["spikes"]] > 0),
                  ("field_goal_attempt", lambda t: t[T["spikes"]] > 0))
        seen = 0
        for category, where in groups:
            tuples = pool_tuples(category, limit=25, where=where)
            self.assertTrue(tuples, category)
            for t, shift in itertools.product(tuples, (0, -4, 3)):
                spot = t[T["start"]] + shift
                if not 1 <= spot <= 99 or not FPM.static_feasible(category, t, spot, penalty=True):
                    continue
                out = lay(category, t, spot)
                layout = out["layout"]
                if not layout["ok"]:
                    continue
                seen += 1
                kinds, completed, values = layout["kinds"], layout["completed"], layout["values"]
                self.assertEqual(sum(values) + chain_walk.layout_penalty_yards(layout), out["net"], (category, t))
                last = len(kinds) - 1
                safety_run = out["safety_terminal"] is not None and out["safety_terminal"][0] == "run"
                self.assertEqual(sum(v for k, c, v in zip(kinds, completed, values) if k in ("att", "catch") and c),
                                 layout["pass_yards"])
                self.assertEqual(sum(v for i, (k, v) in enumerate(zip(kinds, values))
                                     if k == "run" and not (safety_run and i == last)), layout["rush_free"])
                record = yard_split.segment_record(out["real"], layout)
                self.assertEqual(completions_of(layout), out["real"].completions + record["forced"])
                self.assertEqual(record["forced"] > 0, out["scratch"].get("real_values_fallback_completions", 0) > 0
                                 or record["forced"] > 0)
        self.assertGreater(seen, 60)


class GameTests(unittest.TestCase):
    games = None

    @classmethod
    def sample(cls):
        if cls.games is None:
            cls.games = [play("b13-sample-%d" % i) for i in range(12)]
        return cls.games

    def test_the_last_fallback_lays_out_an_unlayable_real_split_with_the_installed_split(self):
        # Review fix (October 16, 2026): the dated last fallback (decisions
        # record, B13 item 7, the review entry) is pinned. When a drive's real
        # split admits no legal layout and no drive of its rung does either,
        # the game still closes: the drive is laid out with the installed
        # split, counted real_split_dropped, its segment marked dropped. The
        # real case (slate-2014.6-4, drive 25 at commit 3aae25f) no longer
        # reaches the branch under the review's fixes, so the test forces it:
        # every layout of one drive that carries its real split fails.
        from unittest import mock
        base = play("b13-last-fallback")
        target = next(p["number"] for p in base["possessions"]
                      if p["number"] > 4 and p.get("real_split") and p["scrimmage_plays"] >= 3 and not p.get("segments"))
        real = chain_walk.drive_layout

        def unlayable(**kw):
            out = real(**kw)
            if kw["drive_no"] == target and kw.get("real_split") is not None:
                out = dict(out, ok=False)
            return out
        with mock.patch.object(chain_walk, "drive_layout", unlayable):
            r = play("b13-last-fallback")
        self.assertEqual(validate_result(r), [])
        self.assertEqual(check_ledger(make_receipt(r, week=5, matchup="B at A", detail="compact_stats")), [])
        self.assertEqual(r["diagnostics"].get("real_split_dropped"), 1)
        self.assertEqual(r["diagnostics"]["chain_layout_resample_exhausted"], 0)
        dropped = next(p for p in r["possessions"] if p["number"] == target)
        self.assertIs(dropped["real_split"]["segments"][0].get("dropped"), True)
        # Every earlier possession is the run without the forced failure.
        self.assertEqual([p for p in r["possessions"] if p["number"] < target],
                         [p for p in base["possessions"] if p["number"] < target])

    def test_flags_and_profiles(self):
        self.assertEqual(B13_FLAGS, frozenset({"yard_split", "snap_values"}))
        self.assertEqual(FLAG_REQUIRES["snap_values"], frozenset({"yard_split"}))
        self.assertTrue(B13_FLAGS <= PROFILE_2014_6.flags)
        self.assertFalse(B13_FLAGS & PROFILE_2014_5.flags)
        with self.assertRaises(ValueError):
            level(PROFILE_2014_6.flags - {"yard_split"})

    def test_games_are_clean_and_carry_the_records(self):
        for r in self.sample():
            self.assertEqual(validate_result(r), [])
            self.assertEqual(check_ledger(make_receipt(r, week=5, matchup="B at A", detail="compact_stats")), [])
            self.assertEqual(r["yardage"], {"model": yard_split.MODEL, "snap_values": True})
            for p in r["possessions"]:
                split = p["real_split"]
                self.assertEqual(len(split["runs"]), len(yard_split.RUN_BINS))
                self.assertEqual(len(split["segments"]), len(p.get("segments") or [None]))
                if p.get("segments"):
                    continue
                rows = [row for row in r["play_ledger"] if row.get("drive") == p["number"]
                        and row.get("play_type") in ("run", "pass")]
                seg = split["segments"][0]
                if seg is not None and not seg.get("dropped"):
                    self.assertEqual(sum(1 for row in rows if row.get("completion")), seg["completions"] + seg["forced"])
                runs = [row["result_yards"] for row in rows if row["play_type"] == "run" and not row.get("kneel")]
                self.assertEqual(sum(split["runs"]), len(runs))

    def test_receipt_summary_slot(self):
        self.assertEqual(DRIVE_SUMMARY_FIELDS[-1], "real_split")
        self.assertEqual(DRIVE_SUMMARY_FIELDS.index("real_split"), DRIVE_SUMMARY_FIELDS.index("pen") + 1)
        r = self.sample()[0]
        rc = make_receipt(r, week=5, matchup="B at A", detail="compact_stats")
        self.assertEqual(rc["yardage"]["model"], yard_split.MODEL)
        self.assertTrue(all(row[-1] is not None for row in rc["drives"]))

    def test_profile_2014_5_and_b13_off_carry_none(self):
        for profile in (PROFILE_2014_5, B13_OFF):
            r = play("b13-old", profile=profile)
            self.assertNotIn("yardage", r)
            self.assertTrue(all("real_split" not in p for p in r["possessions"]))

    def test_possession_stream_unchanged_without_layout_flips(self):
        """Without the mechanisms that read laid-out states (B9F decisions,
        R15 returns), the possessions with and without the replayed split are
        the same until the first drive whose layout was resampled in either
        run: the placeholders keep the possession stream (plan B13)."""
        base = PROFILE_2014_6.flags - {"fourth_down_decisions", "return_touchdowns"}
        on, off = level(base), level(base - B13_FLAGS)
        compared = 0
        for i in range(12):
            r_on, r_off = play("b13-inv-%d" % i, on), play("b13-inv-%d" % i, off)
            for p_on, p_off in zip(r_on["possessions"], r_off["possessions"]):
                if p_on.get("layout_resample") or p_off.get("layout_resample"):
                    break
                self.assertEqual((p_on["team"], p_on["category"], p_on["start_spot"], p_on["seconds"],
                                  p_on["net_yards"]),
                                 (p_off["team"], p_off["category"], p_off["start_spot"], p_off["seconds"],
                                  p_off["net_yards"]), "game %d drive %d" % (i, p_on["number"]))
                compared += 1
        self.assertGreater(compared, 200)

    def test_bands(self):
        receipts = [make_receipt(r, week=5, matchup="B at A", detail="compact_stats") for r in self.sample()]
        games, rows = bands.audit_yardage(receipts, cohort="2014.6")
        self.assertEqual(games, 24)
        by = {row[0]: row for row in rows}
        art = BASE_2010_2014W4.yardage().centres
        ypc = by["yards per carry (kneels included)"]
        self.assertAlmostEqual(ypc[2], art["yards_per_carry"]["pooled"][0] / art["yards_per_carry"]["pooled"][1])
        self.assertAlmostEqual(ypc[3], 3 * art["yards_per_carry"]["residual_sd_per_team_game"]
                               / (art["yards_per_carry"]["carries_per_team_game"] * 24 ** 0.5))
        self.assertIn(ypc[4], ("WITHIN", "OUTSIDE"))
        self.assertEqual(by["share of non-kneel runs losing yards (informational)"][4], "INFORMATIONAL")
        graded = dict((row[0], row) for row in bands.audit_yardage(receipts, cohort="2014.6", per_snap_graded=True)[1])
        self.assertIn(graded["share of non-kneel runs losing yards"][4], ("WITHIN", "OUTSIDE"))
        self.assertIn("share of non-kneel runs of 20+ yards", graded)
        self.assertIn("share of non-kneel runs of 1-3 yards", graded)
        self.assertEqual(graded["share of non-kneel runs of 4-9 yards (informational)"][4], "INFORMATIONAL")
        # Earlier cohorts and unmarked receipts have no row.
        self.assertEqual(bands.audit_yardage(receipts, cohort="2014.5"), (0, []))
        unmarked = [{k: v for k, v in rc.items() if k != "yardage"} for rc in receipts]
        self.assertEqual(bands.audit_yardage(unmarked, cohort="2014.6"), (0, []))

    def test_split_only_level_is_clean(self):
        # R16a without R16b: the real split and completions, the uniform
        # allocation of values.
        r = play("b13-split-only", SPLIT_ONLY)
        self.assertEqual(validate_result(r), [])
        self.assertEqual(r["yardage"]["snap_values"], False)


if __name__ == "__main__":
    unittest.main()
