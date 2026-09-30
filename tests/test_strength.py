"""Kernel 2014.4 candidate, defect register item 1: the E1 acceptance tests
for unit strength from dated honours and the actual lineup (runtime/strength.py).

Synthetic seeds and synthetic evidence records only, except where a test
reads the committed honours evidence to check the date gate and coverage.
Sample sizes and tolerances were fixed before any sample was inspected.
"""
import math
import sys
import unittest
from dataclasses import replace
from pathlib import Path
from statistics import mean, pstdev

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import drive_model, field_position as fp, strength
from runtime.drive_model import CATEGORIES
from runtime.kernel import TeamInput, _edge, resolve_game, validate_result
from support_rosters import game_day_roster
from synthetic_games import SEED

EVENT = "strength-fixture"


def honour(unit, group, tier="Elite", weight=1.0):
    tier_value = {"Elite": 4, "Plus": 3}[tier]
    return {"offdef": {"tier": tier, "tier_value": tier_value, "evidence_weight": weight,
                       "value": (tier_value - 2) * weight, "unit": unit, "honour_position": group,
                       "honour_group": group, "evidence_ids": ["synthetic-" + group]},
            "special": None}


def record(players=None):
    return {"model": strength.MODEL, "season": 2014, "as_of": "2014-09-07",
            "honour_seasons": [2011, 2012], "players": dict(players or {})}


def club(prefix, players=None, team_id=None):
    roster = game_day_roster(prefix)
    return TeamInput(team_id or prefix, tuple(p.player_id for p in roster), roster=roster,
                     strength=record(players))


def drives(result, team):
    return [p for p in result["possessions"] if p["team"] == team]


def td_share(results, team):
    rows = [p for r in results for p in drives(r, team)]
    return sum(p["category"] == "touchdown" for p in rows) / len(rows), len(rows)


def play(home, away, n, tag, venue="home", **kw):
    return [resolve_game(home, away, seed=SEED + b"-strength-%s-%04d" % (tag.encode(), i),
                         event_id="%s-%s-%d" % (EVENT, tag, i), venue=venue, **kw) for i in range(n)]


class ConstantsTests(unittest.TestCase):
    def test_constants_match_the_committed_calibration(self):
        # Second study: the combined (honours + production) composite is the
        # preregistered primary; the age shrink was fitted and not adopted.
        study = strength.calibration_file()["study_2012"]
        self.assertEqual(study["primary_variant"], "combined_max")
        self.assertFalse(study["variants"]["age_shrink_decision"]["adopted"])
        fits = study["variants"]["combined_max"]["fits"]
        self.assertEqual(strength.OFFENSE_SLOPE, fits["offense"]["shrunk_slope"])
        self.assertEqual(strength.DEFENSE_SLOPE, fits["defense"]["shrunk_slope"])
        self.assertEqual(strength.OFFENSE_CENTRE, fits["offense"]["composite_mean"])
        self.assertEqual(strength.DEFENSE_CENTRE, fits["defense"]["composite_mean"])
        pre = strength.first_pass_calibration_file()["preregistered"]
        self.assertEqual(strength.EVIDENCE_WEIGHT, pre["evidence_weight"])
        self.assertEqual(strength.QB_WEIGHT, pre["position_weights"]["QB"])
        self.assertEqual(strength.calibration_file()["preregistered"]["position_weights"]["QB"], 3)
        self.assertEqual((strength.HOME_EDGE, strength.EDGE_CLAMP), (0.023, 0.12))
        # The production tier values are the preregistered ones.
        self.assertEqual(strength.PRODUCTION_TIER_VALUE,
                         {"Elite": 2, "Plus": 1, "Average": 0, "Below-Average": -1, "Replacement-Level": -2})

    def test_window(self):
        self.assertEqual(strength.honour_seasons(2014), (2011, 2012))
        self.assertEqual(strength.honour_seasons(2013), (2011, 2012))
        self.assertEqual(strength.honour_seasons(2012), (2010, 2011))


class EvidenceRuleTests(unittest.TestCase):
    def row(self, i, **kw):
        base = {"evidence_id": "e%d" % i, "player_id": "00-0000001", "season": 2012, "honour_kind": "PB",
                "verification": "Confirmed two-pass", "position": "WR", "public_date": "2012-12-26",
                "admissible_pre_divergence": True}
        base.update(kw)
        return base

    def test_tier_rule(self):
        rows = [self.row(1), self.row(2, honour_kind="AP1", verification="Single-pass", public_date="2013-01-12"),
                self.row(3, honour_kind="PB_ALT", public_date=None, admissible_pre_divergence=False),
                self.row(4, season=2010, honour_kind="AP1")]
        rec, rejected = strength.player_evidence("00-0000001", 2014, "2014-09-07", rows)
        # Plus two-pass (value 1) ties a single-pass Elite (value 1); the higher tier wins the tie.
        self.assertEqual((rec["offdef"]["tier"], rec["offdef"]["value"]), ("Elite", 1.0))
        self.assertEqual(sorted(rec["offdef"]["evidence_ids"]), ["e1", "e2"])
        self.assertEqual([r["reason"] for r in rejected], ["alternate_or_replacement_no_effect"])
        # A specialist honour is special-teams evidence only.
        rec, _ = strength.player_evidence("00-0000001", 2014, "2014-09-07", [self.row(5, position="KR")])
        self.assertIsNone(rec["offdef"])
        self.assertEqual(rec["special"]["unit"], "special")

    def test_future_dated_evidence_is_rejected(self):
        rows = [self.row(1, honour_kind="AP1", public_date="2013-01-12")]
        rec, rejected = strength.player_evidence("00-0000001", 2014, "2013-01-10", rows)
        self.assertIsNone(rec)
        self.assertEqual(rejected[0]["reason"], "future_dated")
        # The committed file: every 2012 AP selection is dated 2013-01-12.
        entry = next(e for e in strength.evidence_file()["entries"]
                     if e["season"] == 2012 and e["honour_kind"] == "AP1")
        before, rejected = strength.player_evidence(entry["player_id"], 2014, "2013-01-11")
        after, _ = strength.player_evidence(entry["player_id"], 2014, "2014-09-07")
        self.assertIn(entry["evidence_id"], {r["evidence_id"] for r in rejected})
        self.assertIn(entry["evidence_id"], after["offdef" if strength.unit_of(entry["position"]) != "special"
                                                   else "special"]["evidence_ids"])
        self.assertTrue(before is None or entry["evidence_id"] not in
                        json_ids(before))

    def test_no_branch_2013_source(self):
        # The only evidence input is the pre-divergence honours file.
        source = Path(strength.__file__).read_text(encoding="utf-8")
        self.assertNotIn("career/2013", source)
        self.assertTrue(all(e["season"] <= 2012 for e in strength.evidence_file()["entries"]))


def json_ids(rec):
    return {i for part in rec.values() if part for i in part["evidence_ids"]}


class CoverageTests(unittest.TestCase):
    def test_all_32_clubs_with_fallbacks(self):
        report = strength.coverage_report(2014, "2014-09-07")
        self.assertEqual(len(report["clubs"]), 32)
        self.assertIn("Jacksonville Jaguars", report["clubs"])
        for team, c in report["clubs"].items():
            self.assertEqual(len(c["with_evidence"]) + len(c["fallbacks"]), c["roster_players"], team)
            self.assertTrue(all(f["reason"] for f in c["fallbacks"]))
        # Roster level (identity, not a depth chart), 2011-2012 honours and
        # 2011-2012 production with the discounted 2010 fallback.
        self.assertEqual(report["summary"]["with_honours"], 135)
        self.assertEqual(report["summary"]["with_evidence"], 948)
        self.assertEqual(report["summary"]["fallbacks"], 1056)
        self.assertEqual(report["summary"]["with_evidence"] + report["summary"]["fallbacks"], 2004)

    def test_jacksonville_by_the_same_rule(self):
        # Jacksonville's roster ids are names; they join by name and club.
        jax = [{"player_id": "Maurice Jones-Drew"}, {"player_id": "Jason Babin"},
               {"player_id": "Nobody In The Database"}]
        rec, cov = strength.team_strength("Jacksonville Jaguars", jax, 2014, "2014-09-07")
        self.assertEqual(rec["players"]["Maurice Jones-Drew"]["offdef"]["tier"], "Elite")
        self.assertEqual(rec["players"]["Jason Babin"]["offdef"]["tier"], "Plus")
        self.assertEqual(cov["fallbacks"], [{"player_id": "Nobody In The Database",
                                             "reason": "identity_unresolved"}])
        # Production rides beside the honour by the same file and rule:
        # Jones-Drew's 2011 (Average) and 2012 (Below-Average) seasons give
        # the window's best tier, Average, so the honour carries his value.
        prod = rec["players"]["Maurice Jones-Drew"]["production"]
        self.assertEqual((prod["tier"], prod["season"], prod["discounted"]), ("Average", 2011, False))
        self.assertEqual(strength.slot_value(rec["players"]["Maurice Jones-Drew"], "RB", "offense"), (2.0, 2.0, 0.0))


class BuilderHookTests(unittest.TestCase):
    """runtime.week_inputs.build_package attaches the record for 2014 clubs,
    Jacksonville included, and never for the closed 2013 season."""

    def build(self, season):
        from unittest import mock
        from runtime import week_inputs
        league = strength._league(2014)["players"]
        den = [{"player_id": p["name"], "gsis_id": p["player_id"], "position": p["position"]}
               for p in league if p.get("inventory_club") == "DEN"]
        jax = [{"player_id": p["name"], "position": p["position"]}
               for p in league if p.get("inventory_club") == "JAX"]
        game = {"week": 1, "date": "%d-09-07" % season, "away": "Denver Broncos",
                "home": "Jacksonville Jaguars", "site": "home"}
        with mock.patch.object(week_inputs, "schedule", return_value=[game]), \
                mock.patch.object(week_inputs, "jacksonville_input",
                                  return_value={"team_id": "Jacksonville Jaguars", "roster": jax}), \
                mock.patch.object(week_inputs, "background_input",
                                  return_value={"team_id": "Denver Broncos", "roster": den}), \
                mock.patch.object(week_inputs.player_bios, "biographies", return_value={}):
            return week_inputs.build_package(1, [], [], {}, season)

    def test_2014_inputs_carry_strength(self):
        package = self.build(2014)
        game = package["games"][0]
        for side in ("home_input", "away_input"):
            rec = game[side]["strength"]
            self.assertEqual((rec["model"], rec["honour_seasons"]), (strength.MODEL, [2011, 2012]))
        self.assertIn("Maurice Jones-Drew", game["home_input"]["strength"]["players"])
        self.assertIn("Peyton Manning", game["away_input"]["strength"]["players"])
        self.assertEqual(set(package["strength_coverage"]), {"Denver Broncos", "Jacksonville Jaguars"})
        # The record is a valid TeamInput field.
        TeamInput(**{**game["home_input"], "active_players": ()})

    def test_2013_inputs_are_untouched(self):
        package = self.build(2013)
        self.assertNotIn("strength", package["games"][0]["home_input"])
        self.assertNotIn("strength_coverage", package)


class ProductionRuleTests(unittest.TestCase):
    """The production stream's window, fallback, date gate and side rule."""
    META = {"2010": {"public_date": "2011-01-02", "admissible_pre_divergence": True},
            "2011": {"public_date": "2012-01-01", "admissible_pre_divergence": True},
            "2012": {"public_date": "2012-12-30", "admissible_pre_divergence": True}}

    def season(self, tier, group="WR", verification="Confirmed two-pass"):
        return {"tier": tier, "group": group, "verification": verification}

    def test_window_best_tier_and_fallback_discount(self):
        rows = {"2011": self.season("Below-Average"), "2012": self.season("Plus")}
        part, rejected = strength.production_evidence("x", 2014, "2014-09-07", rows, self.META)
        self.assertEqual((part["tier"], part["value"], part["season"], part["discounted"]), ("Plus", 1.0, 2012, False))
        self.assertEqual(rejected, [])
        # 2010 alone: one tier down.
        part, _ = strength.production_evidence("x", 2014, "2014-09-07", {"2010": self.season("Elite")}, self.META)
        self.assertEqual((part["tier"], part["undiscounted_tier"], part["discounted"], part["value"]),
                         ("Plus", "Elite", True, 1.0))
        part, _ = strength.production_evidence("x", 2014, "2014-09-07",
                                               {"2010": self.season("Replacement-Level")}, self.META)
        self.assertEqual(part["tier"], "Replacement-Level")
        # 2010 is ignored when a window season qualifies, even a worse one.
        part, _ = strength.production_evidence("x", 2014, "2014-09-07",
                                               {"2010": self.season("Elite"), "2011": self.season("Below-Average")}, self.META)
        self.assertEqual((part["tier"], part["value"]), ("Below-Average", -1.0))
        # An unverified season carries half weight; a job-evidence row no tier.
        part, _ = strength.production_evidence("x", 2014, "2014-09-07",
                                               {"2012": self.season("Elite", verification="Unverified")}, self.META)
        self.assertEqual(part["value"], 1.0)
        part, _ = strength.production_evidence("x", 2014, "2014-09-07", {"2012": {"tier": None, "group": "OL"}}, self.META)
        self.assertIsNone(part)

    def test_date_gate(self):
        rows = {"2012": self.season("Elite")}
        part, rejected = strength.production_evidence("x", 2014, "2012-12-30", rows, self.META)
        self.assertIsNone(part)
        self.assertEqual(rejected[0]["reason"], "future_dated")
        meta = {"2012": {"public_date": "2013-02-01", "admissible_pre_divergence": False}}
        part, rejected = strength.production_evidence("x", 2014, "2014-09-07", rows, meta)
        self.assertIsNone(part)
        self.assertEqual(rejected[0]["reason"], "post_divergence")
        # The committed file: every season's public date precedes the divergence.
        for year, meta in strength.production_file()["seasons"].items():
            self.assertLess(meta["public_date"], strength.DIVERGENCE, year)
            self.assertTrue(meta["admissible_pre_divergence"])

    def test_side_rule_and_max(self):
        qb = {"offdef": None, "production": {"tier": "Elite", "value": 2.0, "group": "QB", "unit": "offense"}}
        self.assertEqual(strength.slot_value(qb, "QB", "offense"), (2.0, 0.0, 2.0))
        self.assertEqual(strength.slot_value(qb, "WR", "offense"), (0.0, 0.0, 0.0))
        self.assertEqual(strength.slot_value(qb, "DL", "defense"), (0.0, 0.0, 0.0))
        wr = {"offdef": {"unit": "offense", "honour_group": "WR", "value": 1.0, "tier": "Plus", "evidence_weight": 1.0},
              "production": {"tier": "Replacement-Level", "value": -2.0, "group": "WR", "unit": "offense"}}
        # An honour never goes below 0 and the max keeps it above bad production.
        self.assertEqual(strength.slot_value(wr, "WR", "offense"), (1.0, 1.0, -2.0))
        self.assertEqual(strength.slot_value(wr, "QB", "offense"), (0.0, 0.0, 0.0))
        bad = {"offdef": None, "production": {"tier": "Below-Average", "value": -1.0, "group": "DL", "unit": "defense"}}
        self.assertEqual(strength.slot_value(bad, "DL", "defense"), (-1.0, 0.0, -1.0))
        for value, tier in ((2, "Elite"), (1.0, "Plus"), (0.5, "Average"), (0, "Average"), (-0.5, "Average"),
                            (-1, "Below-Average"), (-2, "Replacement-Level")):
            self.assertEqual(strength.tier_for_value(value), tier)

    def test_committed_file_tier_cut_points(self):
        # Fixed percentile cut-points: about 10/20/40/20/10 per group and season.
        data = strength.production_file()
        pre = data["preregistered"]["tiers"]
        self.assertEqual(pre["Elite"], "share_above < 0.10")
        for season, block in data["seasons"].items():
            for grp, counts in block["counts"].items():
                n = sum(counts.get(t, 0) for t in strength.TIER_STEP)
                self.assertGreater(n, 0, (season, grp))
                for tier, share in (("Elite", 0.10), ("Plus", 0.20), ("Average", 0.40),
                                    ("Below-Average", 0.20), ("Replacement-Level", 0.10)):
                    self.assertAlmostEqual(counts.get(tier, 0) / n, share, delta=0.05 + 1.0 / n, msg=(season, grp, tier))  # ties at the bottom pool upward

    def test_composite_with_negative_production(self):
        roster = game_day_roster("A")
        players = {"A-QB1": {"offdef": None, "production": {"tier": "Below-Average", "value": -1.0, "group": "QB",
                                                             "unit": "offense"}, "attribution_tier": "Below-Average"},
                   "A-WR1": honour("offense", "WR", "Plus"),
                   "A-DE1": {"offdef": None, "production": {"tier": "Replacement-Level", "value": -2.0, "group": "DL",
                                                             "unit": "defense"}, "attribution_tier": "Replacement-Level"}}
        team = club("A", players)
        passer = next(p for p in roster if p.player_id == "A-QB1")
        comp, rows = strength.composite(team.strength, strength.offense_starters(roster, passer), "offense")
        self.assertEqual(comp, -3.0 + 1.0)
        self.assertEqual({r["player_id"]: r["contribution"] for r in rows}, {"A-QB1": -3.0, "A-WR1": 1.0})
        comp, _ = strength.composite(team.strength, strength.defense_starters(roster), "defense")
        self.assertEqual(comp, -2.0)


class AgeShrinkTests(unittest.TestCase):
    """The age shrink on stale honours was preregistered, fitted and not
    adopted; the kernel therefore reads no birth date."""

    def test_not_adopted_and_not_read(self):
        decision = strength.calibration_file()["study_2012"]["variants"]["age_shrink_decision"]
        self.assertFalse(decision["adopted"])
        self.assertLess(decision["loo_skill_with"]["offense"], decision["loo_skill_without"]["offense"])
        self.assertTrue(decision["players_shrunk"])
        source = Path(strength.__file__).read_text(encoding="utf-8")
        self.assertNotIn("birth_date", source)
        self.assertNotIn("player_bios", source)


class AttributionTiltTests(unittest.TestCase):
    """Register item 19: the tilt moves credit only. With the same seeds and
    inputs, scores, possessions, kickoffs and injuries are identical with the
    tilt on and off; only who received a target, carry or sack credit moves."""
    N = 40

    def test_tilt_leaves_scores_possessions_and_injuries_unchanged(self):
        from unittest import mock
        from runtime import usage
        roster = game_day_roster("A")
        players = {"A-WR1": {**honour("offense", "WR"), "attribution_tier": "Elite"},
                   "A-WR3": {"offdef": None, "production": {"tier": "Replacement-Level", "value": -2.0, "group": "WR",
                                                             "unit": "offense"}, "attribution_tier": "Replacement-Level"},
                   "A-RB1": {**honour("offense", "RB"), "attribution_tier": "Elite"},
                   "B-DE1": {**honour("defense", "DE"), "attribution_tier": "Elite"}}
        a = club("A", {k: v for k, v in players.items() if k.startswith("A")})
        b = club("B", {k: v for k, v in players.items() if k.startswith("B")})
        self.assertTrue(usage.tilt_map(a.strength, roster, "target"))
        with_tilt = play(a, b, self.N, "tilt-on")
        with mock.patch.object(usage, "tilt_map", return_value={}):
            without = play(a, b, self.N, "tilt-on")
        keys = ("final_score", "possessions", "kickoffs", "injuries", "opening_receiver", "substitutions")
        for on, off in zip(with_tilt, without):
            for key in keys:
                self.assertEqual(on[key], off[key], key)
            for tid in ("A", "B"):
                team_on = {k: v for k, v in on["team_stats"][tid].items() if k != "players"}
                team_off = {k: v for k, v in off["team_stats"][tid].items() if k != "players"}
                self.assertEqual(team_on, team_off)
        # The tilt did move credit: WR1's target share rises, WR3's falls.
        def share(results, pid, field="targets"):
            lines = [r["team_stats"]["A"]["players"] for r in results]
            return sum(l[pid][field] for l in lines) / max(1, sum(x[field] for l in lines for x in l.values()))
        self.assertGreater(share(with_tilt, "A-WR1"), share(without, "A-WR1"))
        self.assertLess(share(with_tilt, "A-WR3"), share(without, "A-WR3"))
        self.assertNotEqual([r["team_stats"]["A"]["players"]["A-WR1"]["targets"] for r in with_tilt],
                            [r["team_stats"]["A"]["players"]["A-WR1"]["targets"] for r in without])

    def test_factors_come_from_the_calibration_file(self):
        from runtime import usage
        factors = usage.tilt_factors()
        source = strength.calibration_file()["attribution_tilt_2012"]
        self.assertEqual(factors["target"], source["top_receiver_target_share"]["factors"])
        self.assertEqual(factors["rush"], source["top_rusher_carry_share"]["factors"])
        self.assertEqual(factors["sack"], source["top_sacker_sack_share"]["factors"])
        self.assertEqual(usage.tilt_map(None, game_day_roster("A"), "target"), {})
        self.assertEqual(usage.tilt_map(record(), game_day_roster("A"), "rush"), {})


class EdgeTests(unittest.TestCase):
    def test_clamp_and_no_negative_probability(self):
        grid = [round(-0.12 + 0.005 * i, 3) for i in range(49)] + [-0.12, 0.12]
        data = fp.load()
        cells = [dict(zip(CATEGORIES, row)) for row in data["neutral_counts"]]
        for kind in ("h1_final", "late"):
            cells += list(data[kind + "_counts"].values())
        cells.append(data["ot_counts"])
        for counts in cells:
            total = sum(counts.values())
            base = {c: counts.get(c, 0) / total for c in CATEGORIES}
            eligible = {c: (1,) for c in CATEGORIES}
            for edge in grid:
                for probs in (drive_model.apply_edge(base, edge), fp.category_mix(counts, edge, eligible)):
                    self.assertTrue(all(math.isfinite(v) and v >= 0 for v in probs.values()), (counts, edge))
                    self.assertAlmostEqual(sum(probs.values()), 1.0)
        # The edge itself never leaves the clamp.
        roster = game_day_roster("A")
        stacked = club("A", {p.player_id: honour("offense", "QB" if p.position == "QB" else "WR")
                             for p in roster})
        weak = club("B")
        view = roster
        edge, _ = strength.drive_edge(stacked, weak, view, game_day_roster("B"), view[0], True)
        self.assertEqual(edge, strength.EDGE_CLAMP)
        edge, _ = strength.drive_edge(weak, club("A", {p.player_id: honour("defense", "DL") for p in roster}),
                                      game_day_roster("B"), roster, None, False)
        self.assertGreaterEqual(edge, -strength.EDGE_CLAMP)

    def test_home_term_only_at_home_venues(self):
        a, b = club("A"), club("B")
        va, vb = game_day_roster("A"), game_day_roster("B")
        home = _edge(a, b, a, "home", va, vb, va[0])
        away = _edge(b, a, a, "home", vb, va, vb[0])
        neutral = _edge(a, b, a, "neutral", va, vb, va[0])
        self.assertAlmostEqual(home - neutral, 0.023)
        self.assertAlmostEqual(away, neutral)
        for venue, expected in (("home", 0.023), ("neutral", 0.0)):
            result = play(a, b, 1, "home-" + venue, venue=venue)[0]
            for p in result["possessions"]:
                want = expected if p["team"] == "A" else 0.0
                self.assertEqual(p["strength"]["home"], want, (venue, p["team"]))

    def test_legacy_inputs_keep_the_anchor_path(self):
        roster = game_day_roster("A")
        legacy = TeamInput("A", tuple(p.player_id for p in roster), roster=roster, offense_anchor=3.0)
        other = TeamInput("B", tuple(p.player_id for p in game_day_roster("B")), roster=game_day_roster("B"))
        self.assertAlmostEqual(_edge(legacy, other, other, "neutral"), 0.025)
        result = resolve_game(legacy, other, seed=SEED + b"-legacy", event_id="legacy")
        self.assertTrue(all("strength" not in p for p in result["possessions"]))

    def test_legacy_packets_carry_no_strength_field(self):
        # A TeamInput without a record is frozen exactly as before 2014.4 in
        # the production game packet and the kernel's outcome packet, so a
        # legacy packet's identity is unchanged; a club with a record carries it.
        from runtime.game_runner import build_game_packet
        from runtime.kernel import _outcome_team
        # 46 actives: the synthetic rosters dress 47, one over the 2013 limit.
        roster = tuple(p for p in game_day_roster("A") if p.player_id != "A-WR5")
        b_roster = tuple(p for p in game_day_roster("B") if p.player_id != "B-WR5")
        legacy = TeamInput("A", tuple(p.player_id for p in roster), roster=roster)
        other = TeamInput("B", tuple(p.player_id for p in b_roster), roster=b_roster)
        packet = build_game_packet("legacy-packet", "0123456789abcdef", legacy, other)
        self.assertNotIn("strength", packet["home"])
        self.assertNotIn("strength", packet["away"])
        self.assertNotIn("strength", _outcome_team(legacy))
        scored = TeamInput("A", tuple(p.player_id for p in roster), roster=roster,
                           strength=record({"A-QB1": honour("offense", "QB")}))
        packet = build_game_packet("scored-packet", "0123456789abcdef", scored, other)
        self.assertIn("A-QB1", packet["home"]["strength"]["players"])
        self.assertIn("strength", _outcome_team(scored))


class CompositeTests(unittest.TestCase):
    def test_composite_counts_the_lineup_jobs(self):
        roster = game_day_roster("A")
        players = {"A-QB1": honour("offense", "QB"),                      # passer: 3 x 2
                   "A-WR1": honour("offense", "WR", "Plus", 0.5),         # 0.5
                   "A-WR5": honour("offense", "WR"),                      # not a starter
                   "A-OT1": honour("defense", "DL"),                      # wrong side
                   "A-DE1": honour("defense", "DE", "Plus"),              # 1
                   "A-CB5": honour("defense", "CB")}                      # not a starter
        team = club("A", players)
        passer = next(p for p in roster if p.player_id == "A-QB1")
        comp, rows = strength.composite(team.strength, strength.offense_starters(roster, passer), "offense")
        self.assertEqual(comp, 6.5)
        self.assertEqual({r["player_id"] for r in rows}, {"A-QB1", "A-WR1"})
        comp, _ = strength.composite(team.strength, strength.defense_starters(roster), "defense")
        self.assertEqual(comp, 1.0)
        # A QB honour counts only in the passer slot; another honour never does.
        backup = next(p for p in roster if p.player_id == "A-RB2")
        comp, _ = strength.composite(record({"A-RB2": honour("offense", "RB")}),
                                     strength.offense_starters(roster, backup), "offense")
        self.assertEqual(comp, 0)
        self.assertEqual(len(strength.offense_starters(roster, passer)), 11)
        self.assertEqual(len(strength.defense_starters(roster)), 11)

    def test_removed_starter_is_replaced_by_the_backup_next_drive(self):
        players = {"A-QB1": honour("offense", "QB"), "A-QB2": honour("offense", "QB", "Plus", 0.5)}
        a, b = club("A", players), club("B")
        seed = SEED + b"-strength-removal"
        base = resolve_game(a, b, seed=seed, event_id="strength-removal")
        d = [p["number"] for p in drives(base, "A")][1]
        forced = {(d, "A-QB1"): {"injury_class": "lower_extremity", "severity": "multi_week", "removed": True}}
        result = resolve_game(a, b, seed=seed, event_id="strength-removal", _test_onsets=forced)
        self.assertEqual(validate_result(result), [])
        mine = drives(result, "A")
        before = [p for p in mine if p["number"] <= d]
        after = [p for p in mine if p["number"] > d]
        self.assertTrue(before and after)
        self.assertTrue(all(p["strength"]["offense_composite"] == 6.0 for p in before))
        self.assertTrue(all(p["strength"]["offense_composite"] == 1.5 for p in after))
        self.assertTrue(all(p["passer"] == "A-QB2" for p in after))


class DistributionTests(unittest.TestCase):
    """Sampled distributions, never one game. N and tolerances fixed in advance."""
    N = 160
    N_EFFECT = 320

    @classmethod
    def setUpClass(cls):
        cls.a, cls.b = club("A"), club("B")
        cls.base = play(cls.a, cls.b, cls.N_EFFECT, "base", venue="neutral")

    def test_label_and_protagonist_swap_leave_the_distribution(self):
        # Same causal inputs; only the club labels change (one side becomes
        # "Jacksonville Jaguars"). Edges are identical drive for drive given
        # the lineups, and the sampled scoring agrees within tolerance.
        players = {"A-QB1": honour("offense", "QB")}
        a = club("A", players)
        swapped = club("A", players, team_id="Jacksonville Jaguars")
        va, vb = game_day_roster("A"), game_day_roster("B")
        self.assertEqual(strength.drive_edge(a, self.b, va, vb, va[0], True),
                         strength.drive_edge(swapped, self.b, va, vb, va[0], True))
        one = play(a, self.b, self.N, "swap-1", venue="neutral")
        two = play(swapped, self.b, self.N, "swap-2", venue="neutral")
        pts1 = [r["final_score"]["A"] for r in one]
        pts2 = [r["final_score"]["Jacksonville Jaguars"] for r in two]
        se = math.sqrt(pstdev(pts1) ** 2 / self.N + pstdev(pts2) ** 2 / self.N)
        self.assertLess(abs(mean(pts1) - mean(pts2)), 3 * se)
        # With the honoured passer on the field every drive's edge is the same
        # value under either label (his removal changes it the same way).
        e1 = {p["strength"]["edge"] for r in one for p in drives(r, "A") if p["passer"] == "A-QB1"}
        e2 = {p["strength"]["edge"] for r in two for p in drives(r, "Jacksonville Jaguars")
              if p["passer"] == "A-QB1"}
        self.assertEqual(len(e1), 1)
        self.assertEqual(e1, e2)

    def test_one_capability_moves_its_matchup_only(self):
        # An Elite two-pass quarterback honour on A: A's offense against B's
        # defense improves; B's offense against A's defense is unchanged.
        better = club("A", {"A-QB1": honour("offense", "QB")})
        results = play(better, self.b, self.N_EFFECT, "qb", venue="neutral")
        td0, n0 = td_share(self.base, "A")
        td1, n1 = td_share(results, "A")
        se = math.sqrt(td0 * (1 - td0) / n0 + td1 * (1 - td1) / n1)
        self.assertGreater(td1 - td0, 2 * se)
        expected = strength.OFFENSE_SLOPE * 6.0
        for p in (p for r in results for p in drives(r, "A") if p["passer"] == "A-QB1"):
            self.assertAlmostEqual(p["strength"]["offense_part"] - strength.OFFENSE_SLOPE * (0 - strength.OFFENSE_CENTRE),
                                   expected)
        # Unrelated matchup: every B drive has the same edge as before.
        edges = lambda rs: {round(p["strength"]["edge"], 12) for r in rs for p in drives(r, "B")}
        self.assertEqual(edges(results), edges(self.base))
        tb0, m0 = td_share(self.base, "B")
        tb1, m1 = td_share(results, "B")
        se_b = math.sqrt(tb0 * (1 - tb0) / m0 + tb1 * (1 - tb1) / m1)
        self.assertLess(abs(tb1 - tb0), 3 * se_b)


if __name__ == "__main__":
    unittest.main()
