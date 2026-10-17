"""Kernel 2014.6 batches B4 and U5: player states and strength v4 (data; runtime/player_state.py reads them from B7).

Structural, hygiene and model-math checks run always and need no source data. The builders'
--check runs (full rebuilds from the gated sources) run only when the fetched sources are present
($SOURCES_2010_2014_DIR) and B4_BUILDER_CHECKS=1, because raw data stays out of the repository.
"""
import csv
import json
import math
import os
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/research"))
sys.path.insert(0, str(ROOT))

import build_2010_2014_player_state_model as ps  # noqa: E402
import build_2014_branch_identity as ident  # noqa: E402
import build_2014_strength_calibration_v4 as v4  # noqa: E402
import pre_build_specification  # noqa: E402
import sources_2010_2014 as sources  # noqa: E402
import verify_2010_2014_player_state_model as verify  # noqa: E402

DATA = ROOT / "library/data"
_CACHE = {}


def load(path):
    if path not in _CACHE:
        _CACHE[path] = json.loads(Path(path).read_text())
    return _CACHE[path]


def model():
    return load(ps.MODEL_OUT)


def public():
    return load(ps.PUBLIC_OUT)


def identity():
    return load(ident.OUT)


def strength():
    return load(v4.OUT)


def keys(obj, out=None):
    out = set() if out is None else out
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.add(k)
            keys(v, out)
    elif isinstance(obj, list):
        for v in obj:
            keys(v, out)
    return out


CLUB_CODES = {"ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE", "DAL", "DEN", "DET", "GB", "HOU", "IND", "JAX",
              "KC", "MIA", "MIN", "NE", "NO", "NYG", "NYJ", "OAK", "PHI", "PIT", "SD", "SEA", "SF", "STL", "TB", "TEN",
              "WAS", "JAC"}


class HygieneTests(unittest.TestCase):
    def test_every_artifact_records_the_specification(self):
        digest = pre_build_specification.FROZEN_SHA256
        for path in (ps.MODEL_OUT, ps.PUBLIC_OUT, ps.MANIFEST_OUT, v4.OUT, ident.OUT):
            self.assertEqual(load(path).get("specification_sha256"), digest, path.name)

    def test_no_later_season_and_no_row_after_the_cut(self):
        for path in (ps.MODEL_OUT, ps.PUBLIC_OUT, v4.OUT):
            text = Path(path).read_text()
            for season in range(2015, 2030):
                self.assertNotIn('"%d"' % season, text, path.name)
        self.assertEqual(model()["data_cutoff"], "2014-09-29")

    def test_invariants_without_sources(self):
        self.assertEqual(verify.invariant_errors(), [])

    def test_manifest_names_no_kernel_and_is_unbound(self):
        manifest = load(ps.MANIFEST_OUT)
        self.assertNotIn("kernel", json.dumps(manifest).lower())
        self.assertFalse(manifest["bound"])
        self.assertEqual(manifest["derivation"], "player-state-v1")
        self.assertEqual(manifest["families"], list(ps.FAMILIES))

    def test_public_table_has_no_club_and_only_pre_divergence_rows(self):
        for gsis, row in public()["players"].items():
            self.assertFalse({"club", "team", "name", "tier"} & set(row), gsis)
            for src in row.get("source_rows", ()):
                self.assertIn(src["season"], (2010, 2011, 2012), gsis)
            for ret in row.get("returns", {}).values():
                for src in ret["source_rows"]:
                    self.assertIn(src["season"], (2010, 2011, 2012), gsis)

    def test_model_holds_no_club_game_or_player_field(self):
        found = keys({k: v for k, v in model().items() if k not in ("sources",)})
        for bad in ("club", "team", "game_id", "gsis_id", "player_id", "player"):
            self.assertNotIn(bad, found)

    def test_strength_v4_commits_aggregates_only(self):
        found = keys(strength())
        self.assertFalse(found & CLUB_CODES)
        self.assertNotIn("contributors", found)
        self.assertNotIn("composites", found)


class U5Tests(unittest.TestCase):
    """U5 accepted (Stone, October 16, 2026): the specification's conditional rules as written, and D1."""

    def test_u5_is_recorded_as_accepted_with_the_rules_it_applies(self):
        m = model()
        rules = pre_build_specification.frozen_rules()["player_state"]
        self.assertEqual(m["u5"]["status"], "accepted")
        self.assertEqual(m["u5"]["date"], "2026-10-16")
        self.assertEqual(m["u5"]["applied"], rules["u5_conditional"])
        self.assertIn("Pooled curve", m["u5"]["d1"])
        self.assertEqual(m["tiers"]["status"], "populated (U5)")

    def test_aging_follows_the_two_pass_rule_and_d1(self):
        m = model()
        ag = m["aging"]

        def check(rule, f1, f2, n):
            if min(n) < ps.MIN_CELL:
                self.assertEqual(rule["adopted"], "Z")
                return
            z1, z2 = f1["Z"]["loo_sse"], f2["Z"]["bic"]
            eligible = [c for c in ("C", "M1", "M2") if f1[c].get("estimable") and f2[c].get("estimable")
                        and f1[c]["loo_sse"] < z1 and f2[c]["bic"] < z2]
            self.assertEqual(sorted(rule["eligible"]), sorted(eligible))
            if eligible:
                self.assertEqual(rule["adopted"], min(eligible, key=lambda c: f1[c]["loo_sse"]))
            else:
                self.assertEqual(rule["adopted"], "Z")

        for fam, a in ag["families"].items():
            check(a["rule"], a["pass1"], a["pass2"], a["rows"])
        pooled = ag["pooled"]
        check(pooled["rule"], pooled["pass1"], pooled["pass2"], pooled["rows"])
        self.assertEqual(pooled["families"], ["QB", "RB", "WR", "TE", "DL", "LB", "DB"])
        for fam, block in m["families"].items():
            applied = block["aging"]
            if fam in ps.NON_SPECIALISTS and pooled["rule"]["adopted"] != "Z":
                self.assertEqual(applied["adopted"], pooled["rule"]["adopted"], fam)
                self.assertEqual(applied["beta"], pooled["pass1"][applied["adopted"]]["beta"], fam)
                scale = math.sqrt(block["adopted"]["sb2"] + block["adopted"]["su2"])
                self.assertAlmostEqual(applied["scale"], scale, places=12)
            else:
                self.assertEqual(applied["adopted"], ag["families"][fam]["rule"]["adopted"], fam)
        for row in public()["players"].values():
            fam = row["record_family"]
            if fam in m["families"]:
                self.assertEqual(row["aging"], m["families"][fam]["aging"]["label"])

    def test_the_punter_curve_takes_pass_1_within_2_se(self):
        m = model()
        block = m["families"]["P"]["aging"]
        if block["adopted"] == "Z" or block["source"] != "family":
            self.skipTest("no per-family punter curve adopted")
        f1 = m["aging"]["families"]["P"]["pass1"][block["adopted"]]
        f2 = m["aging"]["families"]["P"]["pass2"][block["adopted"]]
        for got, a, s, b in zip(block["beta"], f1["beta"], f1["se"], f2["beta"]):
            self.assertEqual(got, a if abs(b - a) <= 2 * s else (a if abs(a) <= abs(b) else b))

    def test_the_draft_slope_is_kept_only_in_both_passes_and_negative(self):
        m = model()
        for fam, block in m["families"].items():
            s1 = block["draft_priors"]["log_pick_slope"]
            s2 = m["second_pass"]["families"][fam]["draft_priors"]["log_pick_slope"]
            rule = block["draft_priors"]["rule"]
            expect = (s1["lines"] >= ps.MIN_CELL and s2["lines"] >= ps.MIN_CELL
                      and (s1["loo_class_skill"] or 0) > 0 and (s2["loo_class_skill"] or 0) > 0
                      and s1["slope"] < 0 and s2["slope"] < 0)
            self.assertEqual(rule["slope"], expect, fam)
            self.assertEqual(rule["drafted"] == "slope", expect and not rule["population"], fam)

    def test_the_minimum_cell(self):
        m = model()
        for fam, block in m["families"].items():
            rule = block["draft_priors"]["rule"]
            n = rule["lines"]
            self.assertEqual(rule["population"], n["all"] < ps.MIN_CELL, fam)
            if rule["population"]:
                self.assertEqual((rule["drafted"], rule["undrafted"]), ("population", "population"))
                continue
            if rule["drafted"] == "own":
                self.assertGreaterEqual(n["drafted"], ps.MIN_CELL, fam)
            if rule["undrafted"] == "own":
                self.assertGreaterEqual(n["undrafted"], ps.MIN_CELL, fam)
            else:
                self.assertEqual(rule["undrafted"], "slope_last_pick" if rule["slope"] else "pooled", fam)
            cell = block["honour_cell"]
            self.assertEqual(block["honour_cell_used"],
                             bool(cell and "mean" in cell and cell["seasons"] >= ps.MIN_CELL), fam)

    def test_no_family_is_held_and_dl_lb_take_pass_1s_set(self):
        m = model()
        for fam, block in m["families"].items():
            self.assertFalse(block["adopted"].get("held"), fam)
        for fam in ("DL", "LB"):
            p1 = m["families"][fam]["pass1"]
            a = m["families"][fam]["adopted"]
            want = ps.amendment3_reconcile(p1)
            for k in ("sb2", "su2", "rho"):
                self.assertEqual(a[k], want[k], (fam, k))
        self.assertFalse(any(r.get("basis") == "held" for r in public()["players"].values()))

    def test_reconcile_swing_dl_lb_unit(self):
        p1 = {"sb2": 0.0, "su2": 0.3, "rho": 0.9, "sb2_no_swing": 0.31, "bootstrap": {"su2_interval": [0.01, 0.4]}}
        p2 = {"sb2": 0.0, "su2": 0.28, "rho": 0.92, "bootstrap": {"su2_interval": [0.0, 0.35]}}
        lb = ps.reconcile_swing("LB", p1, p2)
        self.assertTrue(lb["swing_kept"])
        self.assertEqual((lb["sb2"], lb["su2"], lb["rho"]), (0.0, 0.3, 0.9))
        self.assertFalse(lb["plain_two_pass"]["swing_kept"])
        self.assertFalse(ps.reconcile_swing("QB", p1, p2)["swing_kept"])
        p1_none = dict(p1, bootstrap={"su2_interval": [0.0, 0.4]})
        dl = ps.reconcile_swing("DL", p1_none, p2)
        self.assertFalse(dl["swing_kept"])
        self.assertEqual(dl["sb2"], 0.31)
        both = dict(p2, bootstrap={"su2_interval": [0.02, 0.35]})
        self.assertEqual(ps.reconcile_swing("QB", p1, both)["status"], "Confirmed two-pass")

    def test_drawn_tiers_are_populated_on_the_qualifier_floors(self):
        m = model()
        floors = json.loads(ps.PRODUCTION.read_text())["preregistered"]["metrics"]
        for fam, block in m["tiers"]["families"].items():
            self.assertEqual(block["floor"], floors[fam]["minimum"])
            if block["population"] < ps.MIN_CELL:
                self.assertIsNone(block["cuts"], fam)
                continue
            self.assertEqual(len(block["cuts"]), 4, fam)
            self.assertEqual(block["cuts"], sorted(block["cuts"]), fam)
            self.assertEqual(block["shares_below"], [0.1, 0.3, 0.7, 0.9])
            self.assertAlmostEqual(sum(t["target"] for t in block["check"]["tiers"]), 1.0, places=12)
        for row in public()["players"].values():
            self.assertNotIn("tier", json.dumps(row))

    def test_prior_for_reads_the_slope_the_last_pick_and_the_pooled_cell(self):
        fit = {"c0": 0.5, "c1": -0.1, "s2": 0.04, "n": 100, "xbar": 4.0, "sxx": 50.0, "true_var": 0.02}
        stats = {"mean": -0.2, "se": 0.05, "true_var": 0.01, "lines": 40}
        priors = {"drafted": {"all": stats, "leave_class_out": {}}, "undrafted": {"all": None, "leave_class_out": {}},
                  "pooled": {"all": dict(stats, mean=-0.3), "leave_class_out": {}},
                  "log_pick_slope": {"all": fit, "leave_class_out": {}},
                  "rule": {"drafted": "slope", "undrafted": "slope_last_pick", "population": False,
                           "last_pick": {"2012": 253}}}
        params = {"sb2": 0.01, "su2": 0.01}
        m, _, P, basis = ps.prior_for(priors, {"cls": 2012, "drafted": True, "pick": 10}, params)
        self.assertAlmostEqual(m, 0.5 - 0.1 * math.log(10))
        self.assertEqual(basis, "draft")
        m, _, _, basis = ps.prior_for(priors, {"cls": 2012, "drafted": False, "censored": False}, params)
        self.assertAlmostEqual(m, 0.5 - 0.1 * math.log(253))
        self.assertEqual(basis, "undrafted")
        priors["rule"] = {"drafted": "own", "undrafted": "pooled", "population": False, "last_pick": {}}
        m, _, _, _ = ps.prior_for(priors, {"cls": 2012, "drafted": False, "censored": False}, params)
        self.assertAlmostEqual(m, -0.3)
        priors["rule"] = {"drafted": "population", "undrafted": "population", "population": True, "last_pick": {}}
        self.assertEqual(ps.prior_for(priors, {"cls": 2012, "drafted": True, "pick": 10}, params)[3], "population")

    def test_aging_candidates_recover_a_curve_and_keep_z_on_noise(self):
        rng = random.Random(11)

        def rows(curve):
            out = []
            for i in range(900):
                t = (2010, 2011, 2012)[i % 3]
                age = 22 + (i % 13)
                r = (curve(age) if curve else 0.0) + rng.gauss(0, 0.5)
                out.append((t, r, 0.25, float(age), None))
            return out

        curve = lambda a: -0.1 - 0.08 * (a - 27) + 0.006 * (a - 27) ** 2  # noqa: E731
        f1, f2 = ps.fit_candidates(rows(curve)), ps.fit_candidates(rows(curve))
        self.assertIn(ps.adopt_aging(f1, f2, 900, 900)["adopted"], ("M1", "M2"))
        self.assertAlmostEqual(f1["M1"]["beta"][1], -0.08, delta=0.02)
        g1, g2 = ps.fit_candidates(rows(None)), ps.fit_candidates(rows(None))
        self.assertEqual(ps.adopt_aging(g1, g2, 900, 900)["adopted"], "Z")
        self.assertEqual(ps.adopt_aging(f1, f2, 20, 900)["adopted"], "Z")

    def test_the_curve_moves_only_the_forecast_horizon(self):
        params = {"sb2": 1.0, "su2": 0.0, "rho": 0.0}
        drift = ps.Drift("C", [0.5])
        start = (2010, (0.0, 0.0, [1.0, 0.0, 0.0]))
        lines = {2010: (0.0, 1.0), 2011: (0.0, 1.0), 2012: (0.0, 1.0)}
        plain = ps.filter_player(start, lines, {}, params, None, 2014)
        aged = ps.filter_player(start, lines, {}, params, None, 2014, drift, {}, 2012)
        self.assertAlmostEqual(aged[0] - plain[0], 1.0)  # 2012 -> 2013 and 2013 -> 2014 only
        prior_only = ps.filter_player(start, {}, {}, params, None, 2014, drift, {}, None)
        self.assertEqual(prior_only[0], ps.filter_player(start, {}, {}, params, None, 2014)[0])
        # Release decision 2: applied once, the step at the last line's age only, whatever the horizon.
        once = ps.Drift("C", [0.5], application="once")
        self.assertAlmostEqual(ps.filter_player(start, lines, {}, params, None, 2014, once, {}, 2012)[0] - plain[0], 0.5)
        early = {2010: (0.0, 1.0)}
        plain_early = ps.filter_player(start, early, {}, params, None, 2014)
        self.assertAlmostEqual(ps.filter_player(start, early, {}, params, None, 2014, drift, {}, 2010)[0]
                               - plain_early[0], 2.0)
        self.assertAlmostEqual(ps.filter_player(start, early, {}, params, None, 2014, once, {}, 2010)[0]
                               - plain_early[0], 0.5)
        self.assertAlmostEqual(ps.filter_player(start, lines, {}, params, None, 2013, once, {}, 2012)[0],
                               ps.filter_player(start, lines, {}, params, None, 2013, drift, {}, 2012)[0])
        with self.assertRaises(ValueError):
            ps.Drift("C", [0.5], application="twice")
        with self.assertRaises(ValueError):
            ps.drift_from({"adopted": "C", "beta": [0.5], "scale": 1.0, "pass2_beta": [0.5], "pass2_scale": 1.0})

    def test_the_pooled_curve_applies_once_and_the_punter_curve_every_step(self):
        m = model()
        self.assertEqual(m["aging"]["application"]["answer"], "Once (Recommended)")
        for fam, block in m["families"].items():
            a = block["aging"]
            if a["adopted"] == "Z":
                self.assertNotIn("application", a, fam)
            elif a["source"] == "pooled (D1)":
                self.assertEqual(a["application"], "once", fam)
            else:
                self.assertEqual(a["application"], "every_step", fam)
        hc = m["aging"]["horizon_check"]
        if hc["candidate"] != "Z":
            self.assertEqual(hc["applied"], "once")
            for got in hc["checks"].values():
                self.assertEqual(sorted(got), ["every_step", "none", "once"])

    def test_age_and_experience(self):
        d = {"birth_date": "1990-09-01", "cls": 2012, "drafted": True}
        self.assertAlmostEqual(ps.age_at(d, 2014), 24.0, places=2)
        self.assertEqual(ps.experience_at(d, 2013), 1)
        self.assertIsNone(ps.experience_at({"cls": 2010, "drafted": False, "censored": True}, 2011))
        self.assertIsNone(ps.age_at({}, 2014))


class IdentityTests(unittest.TestCase):
    def test_every_required_row_resolves(self):
        cov = identity()["coverage"]
        self.assertEqual(cov["resolved_rows"], cov["required_rows"])
        self.assertGreater(cov["required_rows"], 1500)

    def test_no_gsis_on_two_required_player_ids(self):
        data = identity()
        required = {g for g, row in data["players"].items() if row["required"]}
        owners = {}
        for pid, g in data["by_player_id"].items():
            if g in required and pid in data["players"][g]["display_names"]:
                owners.setdefault(g, set()).add(pid)
        aliases = {g for g, pids in owners.items() if len(pids) > 1}
        self.assertEqual(aliases, set())

    def test_manual_rows_are_sourced(self):
        for gsis, row in identity()["players"].items():
            if row["basis"] == "manual":
                self.assertTrue(row["manual"]["sources"], gsis)
                self.assertIn(gsis, ident.MANUAL)

    def test_join_rule(self):
        by_name = {"will smith": {"00-0000001"}, "evan dietrich smith": {"00-0026784"}, "jay elliott": {"00-0000003"}}
        by_id = {"00-0000001": {"names": {"will smith"}, "seasons": {2012}},
                 "00-0000002": {"names": {"will smith"}, "seasons": {2014}},
                 "00-0000003": {"names": {"jay elliott"}, "seasons": {2014}}}
        self.assertEqual(ident.join("Will Smith", "00-0000001", by_name, by_id), ("unique_name", None))
        basis, error = ident.join("Will Smith", "00-0000002", by_name, by_id)
        self.assertIsNone(basis)
        self.assertIn("conflict", error)
        self.assertEqual(ident.join("Will Smith (DAL)", "00-0000002", by_name, by_id)[0], "dated_roster")
        self.assertEqual(ident.join("Jayrone Elliott", "00-0000003", by_name, by_id)[0], "dated_roster")
        self.assertEqual(ident.join("Evan Smith", "00-0026784", by_name, by_id)[0], "manual")
        self.assertIsNone(ident.join("Nobody Here", "00-0000009", by_name, by_id)[0])
        self.assertEqual(ident.join("Nobody Here", "00-0000009", by_name, by_id,
                                    {"00-0000009": {"year": 2014}})[0], "draft_record")

    def test_real_slot_for_every_club(self):
        for gsis, row in identity()["players"].items():
            slot = row["real_slot"]
            self.assertTrue(slot == "undrafted" or (isinstance(slot, dict) and slot["overall"] >= 1), gsis)


class ModelMathTests(unittest.TestCase):
    def test_fit_recovers_a_synthetic_covariance(self):
        sb2, su2, rho = 0.2, 0.5, 0.6
        tot = [[(sb2 + rho ** k * su2) * 1000, 1000] for k in ps.LAGS]
        fb, fu, fr, _ = ps.fit_covariance(tot)
        self.assertAlmostEqual(fb, sb2, places=6)
        self.assertAlmostEqual(fu, su2, places=6)
        self.assertAlmostEqual(fr, rho, places=6)

    def test_kalman_update_and_propagation(self):
        params = {"sb2": 1.0, "su2": 1.0, "rho": 0.5}
        state = (0.0, 0.0, [1.0, 0.0, 1.0])
        after = ps.update(state, 2.0, 2.0)
        self.assertAlmostEqual(after[0], 0.5)
        self.assertAlmostEqual(after[1], 0.5)
        moved = ps.propagate(after, params, 1)
        self.assertAlmostEqual(moved[1], 0.25)
        self.assertAlmostEqual(moved[2][2], after[2][2] * 0.25 + 0.75)
        self.assertEqual(moved[2][0], after[2][0])

    def test_no_swing_fit_pools_every_lag(self):
        moments = {"a": [[1.0, 1], [0.5, 1], [0.0, 0], [0.0, 0], [0.0, 0]]}
        self.assertAlmostEqual(ps.no_swing_sb2(moments), 0.75)

    def _lines(self, clubs):
        lines = {f: {} for f in ps.FAMILIES}
        rng = random.Random(7)
        for i in range(40):
            for s in (2010, 2011, 2012):
                lines["QB"][("p%d" % i, s)] = {"n": 300, "rate": 0.0, "y": rng.gauss(0, 0.2), "R": 0.01,
                                                "qualifies": True, "club": clubs[i % len(clubs)]}
        return lines

    def test_relabelling_a_club_leaves_every_public_value_identical(self):
        params = {"sb2": 0.01, "su2": 0.01, "rho": 0.5}
        priors = {"drafted": {"all": None, "leave_class_out": {}}, "undrafted": {"all": None, "leave_class_out": {}}}
        a = self._lines(["JAX", "PIT"])
        b = self._lines(["PIT", "JAX"])
        for i in range(40):
            sa = ps.player_state("p%d" % i, "QB", a, {}, priors, params, {}, None, ps.RECORD_SEASONS, 2014)
            sb = ps.player_state("p%d" % i, "QB", b, {}, priors, params, {}, None, ps.RECORD_SEASONS, 2014)
            self.assertEqual(sa[0], sb[0])

    def test_own_2013_2014_rows_never_set_the_public_value(self):
        params = {"sb2": 0.01, "su2": 0.01, "rho": 0.5}
        priors = {"drafted": {"all": None, "leave_class_out": {}}, "undrafted": {"all": None, "leave_class_out": {}}}
        lines = self._lines(["X"])
        before = ps.player_state("p1", "QB", lines, {}, priors, params, {}, None, ps.RECORD_SEASONS, 2014)
        lines["QB"][("p1", 2013)] = {"n": 500, "rate": 0, "y": 5.0, "R": 0.001, "qualifies": True, "club": "X"}
        after = ps.player_state("p1", "QB", lines, {}, priors, params, {}, None, ps.RECORD_SEASONS, 2014)
        self.assertEqual(before[0], after[0])

    def test_honour_is_a_pseudo_observation_split_by_the_gain(self):
        params = {"sb2": 1.0, "su2": 1.0, "rho": 0.5}
        cell = {"mean": 1.0, "true_var": 1.0}
        plain = ps.filter_player((2012, (0.0, 0.0, [1.0, 0.0, 1.0])), {}, {}, params, cell, 2013)
        lifted = ps.filter_player((2012, (0.0, 0.0, [1.0, 0.0, 1.0])), {}, {2012: 1.0}, params, cell, 2013)
        half = ps.filter_player((2012, (0.0, 0.0, [1.0, 0.0, 1.0])), {}, {2012: 0.5}, params, cell, 2013)
        self.assertGreater(lifted[0], plain[0])
        self.assertGreater(lifted[1], plain[1])
        self.assertGreater(lifted[0] + lifted[1], half[0] + half[1])

    def test_feedback_cap_without_variation_is_not_a_predictor(self):
        rows = [("QB", "c%d" % (i % 5), 0.1 * (i % 3), 0, 0.05 * i) for i in range(30)]
        out = ps.feedback_fit(rows)
        self.assertIsNone(out["availability"]["cap_quantile"])
        self.assertEqual(out["availability"]["slope"], 0.0)

    def test_append_only_after_bind(self):
        old = {"players": {"a": {"m_b": 1.0}}}
        self.assertEqual(ps.append_only_errors(old, {"players": {"a": {"m_b": 1.0}, "b": {"m_b": 0.0}}}), [])
        self.assertTrue(ps.append_only_errors(old, {"players": {"a": {"m_b": 2.0}}}))


class FutureDateTests(unittest.TestCase):
    def test_a_row_after_the_cut_is_refused_at_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stats_player_week_2014w4.csv"
            with open(path, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["player_id", "season", "week", "season_type", "game_id"])
                w.writerow(["00-0000001", "2014", "5", "REG", "2014_05_X_Y"])
            original = sources.source_path
            sources.source_path = lambda name, dest, manifest=None: path
            try:
                with self.assertRaises(sources.SourceRefused):
                    list(sources.rows("stats_player_week_2014w4.csv", tmp))
            finally:
                sources.source_path = original

    def test_the_builder_asserts_the_2014_cut_itself(self):
        with self.assertRaises(ValueError):
            ps.assert_cut(2014, 5)
        with self.assertRaises(ValueError):
            ps.assert_cut(2014, 4, "2014-10-02")
        ps.assert_cut(2014, 4, "2014-09-29")
        ps.assert_cut(2013, 17, "2013-12-29")

    def test_builders_read_league_data_only_through_the_gate(self):
        for name in ("build_2010_2014_player_state_model.py", "verify_2010_2014_player_state_model.py",
                     "build_2014_strength_calibration_v4.py", "build_2014_branch_identity.py"):
            text = (ROOT / "scripts/research" / name).read_text()
            self.assertNotIn("csv.DictReader(open", text, name)
            self.assertNotIn("gzip.open", text, name)
            self.assertNotIn("stats_player_reg", text, name)


class StrengthV4Tests(unittest.TestCase):
    def test_adopted_terms_pass_the_keep_rule_in_both_passes(self):
        a = strength()
        for name, term in a["adopted_terms"].items():
            self.assertTrue(a["kept"][name], name)
            self.assertTrue(a["fits"][name]["right_sign_and_skill"], name)
            self.assertTrue(a["pass2"]["fits"][name]["right_sign_and_skill"], name)
            self.assertFalse(name.startswith("ypc"), name)

    def test_specialist_slopes(self):
        a = strength()
        self.assertEqual(a["kicker_slope"], 0)
        self.assertEqual(a["returner_slope"], 0)
        self.assertIn(a["punter"]["adopted"]["status"].split(" ")[0], ("Confirmed", "single-pass", "not"))

    def test_targets_and_model_digest(self):
        a = strength()
        self.assertEqual([t["outcomes"] for t in a["targets"]], [2012, 2013])
        self.assertEqual(a["player_state_model_sha256"],
                         __import__("hashlib").sha256(ps.MODEL_OUT.read_bytes()).hexdigest())

    def test_report_section_matches_the_artifact(self):
        text = v4.REPORT.read_text()
        self.assertIn(v4.report_section(strength()), text)


@unittest.skipUnless(sources.default_dest() and os.environ.get("B4_BUILDER_CHECKS") == "1",
                     "fetched sources and B4_BUILDER_CHECKS=1 are needed for the builder --check runs")
class BuilderCheckTests(unittest.TestCase):
    def run_check(self, script):
        out = subprocess.run([sys.executable, str(ROOT / "scripts/research" / script), "--check"],
                             capture_output=True, text=True, timeout=3600)
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)

    def test_identity(self):
        self.run_check("build_2014_branch_identity.py")

    def test_player_state_model(self):
        self.run_check("build_2010_2014_player_state_model.py")

    def test_pass_2(self):
        self.run_check("verify_2010_2014_player_state_model.py")

    def test_strength_v4(self):
        self.run_check("build_2014_strength_calibration_v4.py")


if __name__ == "__main__":
    unittest.main()
