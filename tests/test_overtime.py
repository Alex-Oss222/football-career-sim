"""Kernel 2013.8: 2013 NFL overtime (library/2013_nfl_playing_rules_for_simulation.md).

Regular season and preseason: one 15-minute period on a real clock,
possessions alternate, modified sudden death (an opening-possession
touchdown or a safety ends it; an opening-possession field goal gives the
other club a possession; then sudden death) and a tie when the period
expires. Postseason: the same possession rule over successive 15-minute
periods; a possession carries across a period break; never tied.

Scripted cases replace only the overtime drive draws (regulation is the
kernel's own, from synthetic seeds whose regulation ends tied), so every
scripted game is still a real kernel result checked by validate_result and
check_ledger. Synthetic seeds only; no career state.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import unittest
from unittest import mock

from runtime import KERNEL_VERSION
from runtime import field_position as fp
from runtime.kernel import resolve_game, validate_result
from runtime.play_detail import check_ledger
from runtime.rules import RULES, ot_status
from synthetic_games import SEED, sample, sample_teams

REAL_DRAW = fp.draw_drive


class Infeasible(Exception):
    """The scripted category has no real 2012 drive from the current spot."""
SEARCH = 400


def _tied_regulation_seeds(game_type, count):
    """Synthetic seeds whose regulation ends level (overtime is played)."""
    a, b = sample_teams()
    found = []
    for i in range(SEARCH):
        seed = SEED + b"-ot-%s-%05d" % (game_type.encode(), i)
        result = resolve_game(a, b, seed=seed, event_id="ot-%s-%d" % (game_type, i), game_type=game_type)
        if any(p["half"] == "OT" for p in result["possessions"]):
            found.append((seed, "ot-%s-%d" % (game_type, i), result))
            if len(found) == count:
                break
    return found


def _scripted(script):
    """A draw_drive that plays the scripted overtime categories in order.

    Each entry is a category; the tuple is a real 2012 drive of that category
    feasible from the spot (the OT pool, else the neutral pool for a safety).
    "clock" runs out the window. Regulation draws, and any overtime draw
    after the script is used up (a missed kick can extend the game), are the
    kernel's own."""
    queue = list(script)

    def draw(rng, spot, half, window, diff, edge, diagnostics):
        if half != "OT" or not queue:
            return REAL_DRAW(rng, spot, half, window, diff, edge, diagnostics)
        category = queue.pop(0)
        if category == "clock":
            t = fp._clock_fallback(rng, fp._late_clock_tuples("tied"), spot, window) or fp.ZERO_TUPLE
            return fp.Drive("clock", t, window, True, fp.cell_for(half, window, diff), "ot")
        if category == "safety":
            # 2012 safeties start inside the offense's own 26: any real one
            # feasible from this spot.
            pool = tuple(t for t in fp._all_tuples(fp.load(), "safety")
                         if fp.static_feasible("safety", t, spot) and fp.scaled_seconds(t) < window)
        else:
            pool = fp.eligible(("ot", None), category, spot, "ot", window) or fp.eligible(
                ("neutral", fp.start_bin(spot)), category, spot, "h2_neutral", window)
        if not pool:
            raise Infeasible("no feasible %s tuple from spot %s" % (category, spot))
        t = pool[0]
        return fp.Drive(category, t, fp.scaled_seconds(t), False, fp.cell_for(half, window, diff), "ot")
    return draw


def _ot(result):
    return [p for p in result["possessions"] if p["half"] == "OT"]


class OvertimeRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.regular = _tied_regulation_seeds("regular", 8)
        cls.postseason = _tied_regulation_seeds("postseason", 2)
        if not cls.regular or not cls.postseason:
            raise unittest.SkipTest("no tied regulation in the synthetic search")

    def replay(self, script, game_type="regular", which=0):
        seed, event_id, _ = (self.regular if game_type == "regular" else self.postseason)[which]
        a, b = sample_teams()
        with mock.patch.object(fp, "draw_drive", _scripted(script)):
            result = resolve_game(a, b, seed=seed, event_id=event_id, game_type=game_type)
        self.assertEqual(validate_result(result), [])
        self.assertEqual(check_ledger(result), [])
        return result

    def test_kernel_version(self):
        # 2013.8 introduced these rules; later kernels keep them.
        self.assertIn(KERNEL_VERSION, ("2013.8", "2013.9", "2013.10"))
        self.assertEqual((RULES.regular_ot_seconds, RULES.postseason_ot_seconds), (900, 900))

    def test_opening_field_goal_gives_the_other_club_a_possession(self):
        made = 0
        for which in range(len(self.regular)):
            for script in (["field_goal_attempt", "punt"], ["field_goal_attempt", "field_goal_attempt", "punt"]):
                result = self.replay(script, which=which)
                ot = _ot(result)
                if ot[0]["fg_made"] is not True:
                    continue  # a missed opening kick is no score: sudden death follows
                made += 1
                self.assertGreaterEqual(len(ot), 2, script)
                self.assertNotEqual(ot[0]["team"], ot[1]["team"])
                self.assertGreater(ot[0]["end_clock"], 0, "an opening field goal must not run out the period")
                self.assertFalse(ot[0]["half_final"])
                if script == ["field_goal_attempt", "punt"]:
                    # The reply failed: the field-goal club wins.
                    self.assertEqual(len(ot), 2)
                    scores = result["final_score"]
                    self.assertEqual(scores[ot[0]["team"]] - scores[ot[1]["team"]], 3)
                elif ot[1]["fg_made"]:
                    # Both kicked field goals: sudden death, the game goes on.
                    self.assertGreaterEqual(len(ot), 3)
        self.assertGreater(made, 0, "no made opening field goal in the scripted seeds")

    def test_opening_touchdown_ends_the_game(self):
        result = self.replay(["touchdown"])
        ot = _ot(result)
        self.assertEqual(len(ot), 1)
        self.assertIsNone(ot[0]["xp_made"])  # no try after a walk-off touchdown
        scores = result["final_score"]
        self.assertEqual(scores[ot[0]["team"]] - min(scores.values()), 6)

    def test_safety_ends_the_game(self):
        played = 0
        for which in range(len(self.regular)):
            for script in (["safety"], ["punt", "safety"]):
                try:
                    result = self.replay(script, which=which)
                except Infeasible:
                    continue
                played += 1
                ot = _ot(result)
                self.assertEqual(len(ot), len(script))
                self.assertEqual(ot[-1]["category"], "safety")
                scores = result["final_score"]
                winner = next(t for t in scores if t != ot[-1]["team"])
                self.assertEqual(scores[winner] - scores[ot[-1]["team"]], 2)
        self.assertGreater(played, 0, "no scripted overtime safety was feasible")

    def test_expired_regular_season_period_is_a_tie(self):
        result = self.replay(["punt", "punt", "clock"])
        ot = _ot(result)
        self.assertEqual(ot[-1]["category"], "end_of_overtime")
        self.assertEqual(ot[-1]["end_clock"], 0)
        self.assertEqual(sum(p["seconds"] for p in ot), RULES.regular_ot_seconds)
        self.assertEqual(len(set(result["final_score"].values())), 1)

    def test_postseason_continues_across_periods_and_never_ties(self):
        result = self.replay(["punt"] * 12 + ["field_goal_attempt"] * 6, game_type="postseason")
        ot = _ot(result)
        self.assertNotEqual(*result["final_score"].values())
        periods = {row["period"] for row in result["play_ledger"] if str(row["period"]).startswith("OT")}
        self.assertIn("OT2", periods)
        self.assertEqual(ot_status([{"team": p["team"], "score": {"touchdown": "touchdown", "safety": "safety"}.get(
            p["category"], "field_goal" if p.get("fg_made") else None)} for p in ot], "postseason"), "end")

    def test_walk_off_tuples_do_not_run_out_the_period(self):
        """Week 10 defect (kernel 2013.7): a 2012 overtime drive flagged final
        because its score ended the game was replayed as consuming the whole
        15-minute window. Under 2013.8 only a clock drive ends the period."""
        import random
        pools = fp.load()["pools"]["ot"]
        walk_offs = [t for c in ("touchdown", "field_goal_attempt") for t in pools[c] if t[fp.T["final"]]]
        self.assertTrue(walk_offs)
        self.assertFalse(any(fp.ends_window("ot", c, t) for c in ("touchdown", "field_goal_attempt")
                             for t in pools[c]))
        self.assertTrue(all(fp.ends_window("late", c, t) for c in ("touchdown", "field_goal_attempt")
                            for t in pools[c] if t[fp.T["final"]]))
        rng = random.Random(7)
        for _ in range(500):
            drawn = fp.draw_drive(rng, 75, "OT", 900, 0, 0.0, {})
            if drawn.category != "clock":
                self.assertFalse(drawn.consumes_window, drawn.category)
                self.assertLess(drawn.seconds, 900)

    def test_postseason_expiry_never_ends_level(self):
        self.assertEqual(ot_status([{"team": "A", "score": None}], "postseason", expired=True), "continue")
        self.assertEqual(ot_status([{"team": "A", "score": None}], "regular", expired=True), "end")
        self.assertEqual(ot_status([{"team": "A", "score": "field_goal"}], "regular"), "continue")
        self.assertEqual(ot_status([{"team": "A", "score": "field_goal"}, {"team": "B", "score": None}]), "end")
        self.assertEqual(ot_status([{"team": "A", "score": "field_goal"},
                                    {"team": "B", "score": "field_goal"}]), "continue")
        self.assertEqual(ot_status([{"team": "A", "score": None}, {"team": "B", "score": "field_goal"}]), "end")
        self.assertEqual(ot_status([{"team": "A", "score": "safety"}]), "end")

    def test_unscripted_overtime_follows_the_rule(self):
        """Every overtime the kernel draws (both game types) alternates
        possessions, lets no opening field goal end the game, and ties only
        in the regular season at the end of the period."""
        games = [(g, r) for g, rows in (("regular", self.regular), ("postseason", self.postseason))
                 for _, _, r in rows]
        games += [("regular", r) for r in sample() if _ot(r)]
        self.assertTrue(games)
        for game_type, result in games:
            ot = _ot(result)
            for a, b in zip(ot, ot[1:]):
                self.assertNotEqual(a["team"], b["team"])
            if ot[0]["category"] == "field_goal_attempt" and ot[0]["fg_made"]:
                self.assertGreaterEqual(len(ot), 2)
            tied = len(set(result["final_score"].values())) == 1
            if tied:
                self.assertEqual(game_type, "regular")
                self.assertEqual(ot[-1]["end_clock"], 0)


if __name__ == "__main__":
    unittest.main()
