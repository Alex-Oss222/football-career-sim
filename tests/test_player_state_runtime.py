"""Kernel 2014.6 batch B7: player states, identity and strength v4 at runtime.

runtime/player_state.py (the draw math and the public table), runtime/strength.py
model player-state-v1, the private service's latent tables, the production
runner's fetch after closure, the kernel's privacy, the weekly identity map and
exclusivity gate, the release gate, the privacy check and the observables.
Synthetic references and a local service only: no live call, nothing written
to the repository, no closed result touched. Sample sizes and tolerances were
fixed before any sample was inspected.
"""
import copy
import hashlib
import json
import math
import sys
import tempfile
import unittest
from dataclasses import replace
from datetime import date
from pathlib import Path
from statistics import mean, pstdev
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import game_runner, player_state as ps, seasons, strength, week_inputs
from runtime.kernel import TeamInput, resolve_game, validate_result
from runtime.profiles import PROFILE_2014_5, PROFILE_2014_6
from runtime.private_service import Store
from local_private_service import local_service
from support_rosters import game_day_roster
from synthetic_games import SEED

ROOT = Path(__file__).resolve().parents[1]
GOLDEN_SEED = b"golden-store-seed-0123456789abcdef"
# Pinned on October 3, 2026 from runtime.player_state (AS241, HMAC-SHA256 keyed draw).
GOLDEN = {"2014:00-0010346:b": "0x1.ecc73220b4e56p-6", "2014:00-0010346:u": "-0x1.188725d38d2d6p+0",
          "2015:00-0010346:e": "-0x1.63dbb1ba6658bp+0", "2014:00-0029604:b": "0x1.38e2eec9df0cep-3"}
GOLDEN_COMMITMENT = "72a63766094611829cc51fddf1cc98e500ed51ff16d6ade6764928e185859d2d"
SYNTHETIC_REF = ps.season_reference(b"test-player-state-reference", 2014)
STUB_BINDING = {"schema": ps.BINDING_SCHEMA, "league_year": 2014, "manifest_sha256": None,
                "commitment": "0" * 64}


def stub_binding(commitment="0" * 64):
    return dict(STUB_BINDING, manifest_sha256=ps.manifest_sha256(), commitment=commitment)


FAMILY_OF_POSITION = {"QB": "QB", "RB": "RB", "FB": "RB", "WR": "WR", "TE": "TE", "DE": "DL", "DT": "DL",
                      "LB": "LB", "CB": "DB", "S": "DB", "K": "K", "P": "P"}


def synthetic_record(roster, values=None, honours=None, model=strength.PLAYER_STATE_MODEL):
    """A player-state record for a synthetic roster: every player of a family
    with spread is drawn (value 0 unless `values` names him); `honours` maps
    player id to an offdef Plus/Elite honour part."""
    players, keys = {}, []
    for p in roster:
        fam = FAMILY_OF_POSITION.get(p.position)
        drawn = fam is not None and ps.family_scale(fam) > 0
        row = {"offdef": (honours or {}).get(p.player_id), "special": None, "production": None,
               "state": {"family": fam, "basis": "synthetic" if drawn else "no_state", "expected": 0.0,
                         "drawn": drawn}}
        if drawn:
            row["latent_value"] = float((values or {}).get(p.player_id, 0.0))
            keys.append(ps.key(2014, p.player_id, "b"))
        players[p.player_id] = row
    return {"model": model, "season": 2014, "as_of": "2014-09-07", "honour_seasons": [2011, 2012],
            "league_year": 2014, "manifest_sha256": ps.manifest_sha256(), "commitment": "0" * 64,
            "latent_keys": sorted(keys, key=ps.key_text), "players": players}


def honour(unit, group, tier="Elite"):
    tier_value = {"Elite": 4, "Plus": 3}[tier]
    return {"tier": tier, "tier_value": tier_value, "evidence_weight": 1.0, "value": float(tier_value - 2),
            "unit": unit, "honour_position": group, "honour_group": group, "evidence_ids": ["synthetic-" + group]}


def club(prefix, values=None, honours=None, team_id=None):
    roster = game_day_roster(prefix)
    return TeamInput(team_id or prefix, tuple(p.player_id for p in roster), roster=roster,
                     strength=synthetic_record(roster, values, honours))


def play(home, away, n, tag, venue="neutral", profile=PROFILE_2014_6):
    return [resolve_game(home, away, seed=SEED + b"-b7-%s-%04d" % (tag.encode(), i),
                         event_id="b7-%s-%d" % (tag, i), venue=venue, _test_profile=profile) for i in range(n)]


def td_share(results, team):
    rows = [p for r in results for p in r["possessions"] if p["team"] == team]
    return sum(p["category"] == "touchdown" for p in rows) / len(rows), len(rows)


def _has_key(obj, name):
    if isinstance(obj, dict):
        return any(k == name or _has_key(v, name) for k, v in obj.items())
    if isinstance(obj, list):
        return any(_has_key(v, name) for v in obj)
    return False


class DrawMathTests(unittest.TestCase):
    def test_inverse_normal_against_reference_quantiles(self):
        for p, ref in ((0.975, 1.959963984540054), (0.5, 0.0), (0.001, -3.090232306167813),
                       (1e-10, -6.361340902404056), (0.3, -0.5244005127080407), (0.95, 1.6448536269514722)):
            self.assertAlmostEqual(ps.inverse_normal(p), ref, places=11)
        for p in (0.01, 0.2, 0.4, 0.7):
            self.assertAlmostEqual(ps.inverse_normal(p), -ps.inverse_normal(1 - p), places=14)
        with self.assertRaises(ValueError):
            ps.inverse_normal(1.0)

    def test_uniform_is_inside_the_open_interval(self):
        self.assertGreater(ps.uniform_from_digest(bytes(8)), 0.0)
        self.assertLess(ps.uniform_from_digest(b"\xff" * 8), 1.0)
        self.assertEqual(ps.uniform_from_digest(bytes(8)), 0.5 / 2.0 ** 53)

    def test_golden_vectors_and_commitment(self):
        reference = ps.season_reference(GOLDEN_SEED, 2014)
        self.assertEqual(reference.hex(), "f6e75d5d323c5f75afa799c19377e30838a0ec1da198e37742dc4553c53b2e34")
        for text, z_hex in GOLDEN.items():
            k = ps.parse_key_text(text)
            self.assertEqual(ps.z_text(ps.draw_z(reference, k)), z_hex, text)
            self.assertEqual(ps.key_text(k), text)
        self.assertEqual(ps.commitment([("2014:00-0010346:b", GOLDEN["2014:00-0010346:b"])]), GOLDEN_COMMITMENT)

    def test_key_carries_no_club_and_no_family(self):
        self.assertEqual(ps.key(2014, "00-0010346", "b"), ["player-state-z-v1", 2014, "00-0010346", "b"])

    def test_draws_are_standard_normal(self):
        zs = [ps.draw_z(SYNTHETIC_REF, ps.key(2014, "00-%07d" % i, "b")) for i in range(4000)]
        self.assertLess(abs(mean(zs)), 3 / math.sqrt(4000))
        self.assertLess(abs(pstdev(zs) - 1), 0.05)

    def test_psd_safe_factorization(self):
        l11, l21, l22 = ps.factor([4.0, 2.0, 2.0])
        self.assertEqual(l11, 2.0)
        self.assertEqual(l21, 1.0)
        self.assertEqual(l22, 1.0)
        # Not positive semi-definite: the swing factor is clipped at 0, no error.
        self.assertEqual(ps.factor([1.0, 2.0, 1.0])[2], 0.0)
        # Zero variance draws nothing.
        self.assertEqual(ps.factor([0.0, 0.0, 0.0]), (0.0, 0.0, 0.0))

    def test_sigma_zero_slots_are_not_drawn_and_innovations_only_where_tau_is_positive(self):
        table = ps.public_table()
        gsis = next(g for g, r in table.items() if r.get("record_family") == "QB" and ps.has_state(r)
                    and r["P"][2] > 0)
        keys = ps.row_keys(gsis, table[gsis], 2014, 2014)
        self.assertEqual([k[3] for k in keys], ["b", "u"])
        keys_2016 = ps.row_keys(gsis, table[gsis], 2016, 2014)
        self.assertEqual([(k[1], k[3]) for k in keys_2016], [(2014, "b"), (2014, "u"), (2015, "e"), (2016, "e")])
        # A family whose swing is not kept (tau 0): base slots only, in every year.
        rb = next(g for g, r in table.items() if r.get("record_family") == "RB" and ps.has_state(r))
        self.assertTrue(all(k[3] == "b" for k in ps.row_keys(rb, table[rb], 2016, 2014)))
        # A held family and a no-state row draw nothing.
        lb = next(g for g, r in table.items() if r.get("basis") == "held")
        ol = next(g for g, r in table.items() if r.get("basis") == "no_state")
        self.assertEqual(ps.row_keys(lb, table[lb], 2014, 2014), [])
        self.assertEqual(ps.row_keys(ol, table[ol], 2014, 2014), [])
        self.assertEqual(ps.expected_value(table[lb]), 0.0)

    def test_latent_value_is_the_expectation_plus_the_factored_deviation(self):
        table = ps.public_table()
        gsis = "00-0010346"
        row = table[gsis]
        z = {ps.key_text(k): ps.draw_z(SYNTHETIC_REF, k) for k in ps.row_keys(gsis, row, 2014, 2014)}
        l11, l21, l22 = ps.factor(row["P"])
        zb, zu = z["2014:%s:b" % gsis], z["2014:%s:u" % gsis]
        expected = (row["m_b"] + row["m_u"] + l11 * zb + l21 * zb + l22 * zu) / ps.family_scale("QB")
        self.assertAlmostEqual(ps.latent_value(gsis, row, z, 2014, 2014), expected, places=12)
        with self.assertRaises(ps.PlayerStateError):
            ps.latent_value(gsis, row, {}, 2014, 2014)


class PublicTableTests(unittest.TestCase):
    def test_manifest_pins_both_files(self):
        self.assertEqual(ps.manifest()["league_year"], 2014)
        with mock.patch.object(ps, "sha256_file", return_value="0" * 64):
            ps.manifest.cache_clear()
            try:
                with self.assertRaises(ps.PlayerStateError):
                    ps.manifest()
            finally:
                ps.manifest.cache_clear()
        self.assertEqual(ps.manifest()["league_year"], 2014)

    def test_a_public_row_edit_after_bind_is_refused(self):
        # The service binds the manifest digest; a table whose digest no longer
        # matches the manifest cannot be read, so an edited row is refused.
        table = json.loads(ps.PUBLIC_PATH.read_text())
        gsis = next(iter(table["players"]))
        edited = copy.deepcopy(table)
        edited["players"][gsis]["m_b"] = 99.0
        digest = hashlib.sha256(json.dumps(edited, indent=1, sort_keys=True).encode()).hexdigest()
        self.assertNotEqual(digest, ps.manifest()["public_table_sha256"])

    def test_family_scale_and_held_families(self):
        self.assertEqual(ps.family_scale("LB"), 0.0)
        self.assertEqual(ps.family_scale("OL"), 0.0)
        qb = ps.family_params("QB")
        self.assertAlmostEqual(ps.family_scale("QB"), math.sqrt(qb["sb2"] + qb["su2"]))

    def test_binding_absent_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(ps.binding(2014, tmp))
            with self.assertRaises(ps.PlayerStateError):
                ps.require_binding(2014, tmp)
            (Path(tmp) / "library/data").mkdir(parents=True)
            ps.binding_path(2014, tmp).write_text(json.dumps(dict(stub_binding(), manifest_sha256="1" * 64)))
            with self.assertRaises(ps.PlayerStateError):
                ps.require_binding(2014, tmp)
            ps.binding_path(2014, tmp).write_text(json.dumps(stub_binding()))
            self.assertEqual(ps.require_binding(2014, tmp)["commitment"], "0" * 64)


class StrengthModelTests(unittest.TestCase):
    def test_profile_2014_6_resolves_with_the_player_state_model(self):
        self.assertEqual(PROFILE_2014_6.strength, strength.PLAYER_STATE_MODEL)
        self.assertEqual(PROFILE_2014_5.strength, strength.MODEL)

    def test_v4_terms_home_edge_and_punter_come_from_the_pinned_artifact(self):
        data = json.loads(strength.V4_CALIBRATION.read_text())
        self.assertEqual(hashlib.sha256(strength.V4_CALIBRATION.read_bytes()).hexdigest(), strength.V4_SHA256)
        params = strength.parameters(strength.PLAYER_STATE_MODEL)
        self.assertEqual(params.home_edge, data["home_edge"]["value"])
        self.assertEqual(params.punter_slope, data["punter"]["adopted"]["slope"])
        self.assertEqual((params.kicker_slope, params.kick_returner_slope, params.punt_returner_slope), (0, 0, 0))
        live = {t["name"] for t in params.terms if t["active"]}
        self.assertEqual(live, {name for name, kept in data["kept"].items() if kept} - {"ypc_defense_run_defense",
                                                                                          "ypc_offense_run"})
        self.assertEqual(live, {"td_share_offense_passing", "int_share_offense_passing"})
        for term in params.terms:
            self.assertEqual(term["centre"], data["fits"][term["name"]]["composite_mean"])
            self.assertEqual(term["slope"], data["adopted_terms"][term["name"]]["slope"] if term["active"] else 0.0)
        self.assertEqual(sum(1 for t in params.terms if t["name"] in data["terms_changed_by_refit"]["turned_off"]
                             and t["slope"] == 0.0), 2)

    def test_state_slot_value_side_rule_and_honour_floor(self):
        qb = {"state": {"family": "QB", "drawn": True}, "latent_value": 0.4, "offdef": None}
        self.assertEqual(strength.state_slot_value(qb, "QB", "offense"), (0.4, 0.0, 0.4))
        self.assertEqual(strength.state_slot_value(qb, "WR", "offense"), (0.0, 0.0, 0.0))  # QB only in the passer slot
        self.assertEqual(strength.state_slot_value(qb, "QB", "defense"), (0.0, 0.0, 0.0))
        wr = {"state": {"family": "WR", "drawn": True}, "latent_value": -1.5, "offdef": None}
        self.assertEqual(strength.state_slot_value(wr, "WR", "offense"), (-1.5, 0.0, -1.5))
        self.assertEqual(strength.state_slot_value(wr, "QB", "offense"), (0.0, 0.0, 0.0))
        floored = dict(wr, offdef=honour("offense", "WR", "Plus"))
        self.assertEqual(strength.state_slot_value(floored, "WR", "offense"), (1.0, 1.0, -1.5))
        above = dict(floored, latent_value=2.5)
        self.assertEqual(strength.state_slot_value(above, "WR", "offense")[0], 2.5)
        held = {"state": {"family": "LB", "drawn": False}, "offdef": None}
        self.assertEqual(strength.state_slot_value(held, "LB", "defense"), (0.0, 0.0, 0.0))
        with self.assertRaises(ps.PlayerStateError):
            strength.state_slot_value({"state": {"family": "QB", "drawn": True}}, "QB", "offense")

    def test_offensive_linemen_keep_rule_b_plus_honours(self):
        roster = game_day_roster("A")
        record = synthetic_record(roster, honours={"A-OT1": honour("offense", "OT", "Plus")})
        front = [("OL", p) for p in roster if p.position in ("OT", "OG", "C")][:5]
        total, rows = strength.composite(record, front, "offense", "protection")
        by_id = {r["player_id"]: r for r in rows}
        self.assertEqual(by_id["A-OT1"]["value"], 1.0)
        unproven = [r for r in rows if r.get("ol_unproven")]
        self.assertEqual(len(unproven), 4)
        self.assertEqual(total, 1.0 - 4.0)

    def test_team_strength_under_the_player_state_model(self):
        league = strength._league(2014)["players"]
        rows = [{"player_id": p["name"], "gsis_id": p["player_id"]} for p in league
                if p.get("inventory_club") == "DEN"][:30]
        with mock.patch.object(ps, "binding", return_value=stub_binding("7" * 64)):
            record, coverage = strength.team_strength("Denver Broncos", rows, 2014, date(2014, 9, 7),
                                                      model=strength.PLAYER_STATE_MODEL)
        self.assertEqual(record["model"], strength.PLAYER_STATE_MODEL)
        self.assertEqual((record["league_year"], record["commitment"]), (2014, "7" * 64))
        self.assertEqual(record["manifest_sha256"], ps.manifest_sha256())
        drawn = {pid for pid, p in record["players"].items() if (p.get("state") or {}).get("drawn")}
        self.assertEqual(set(coverage["with_state"]), drawn)
        key_ids = {k[2] for k in record["latent_keys"]}
        self.assertEqual(key_ids, {record["players"][pid]["gsis_id"] for pid in drawn})
        self.assertTrue(all("latent_value" not in p for p in record["players"].values()))
        # An unresolved identity fails closed under this model.
        with mock.patch.object(ps, "binding", return_value=stub_binding()):
            with self.assertRaises(ValueError):
                strength.team_strength("Denver Broncos", [{"player_id": "Nobody Known"}], 2014, "2014-09-07",
                                       model=strength.PLAYER_STATE_MODEL)
        # Without a binding, nothing is built.
        with mock.patch.object(ps, "binding", return_value=None):
            with self.assertRaises(ps.PlayerStateError):
                strength.team_strength("Denver Broncos", rows, 2014, "2014-09-07", model=strength.PLAYER_STATE_MODEL)
        # The honours-production record is unchanged by the model's existence.
        v3, _ = strength.team_strength("Denver Broncos", rows, 2014, date(2014, 9, 7), model=strength.MODEL)
        self.assertEqual(v3["model"], strength.MODEL)
        self.assertNotIn("latent_keys", v3)

    def test_relabelling_a_position_or_club_keeps_the_value(self):
        table = ps.public_table()
        gsis = "00-0010346"
        row = table[gsis]
        draws = {ps.key_text(k): ps.z_text(ps.draw_z(SYNTHETIC_REF, k)) for k in ps.row_keys(gsis, row, 2014, 2014)}
        base = TeamInput("X", ("p",), roster=(replace(game_day_roster("X")[0], player_id="p"),),
                         strength={"model": strength.PLAYER_STATE_MODEL, "league_year": 2014,
                                   "players": {"p": {"gsis_id": gsis, "state": ps.public_state(gsis)}}})
        a = ps.apply_latent(base, draws).strength["players"]["p"]["latent_value"]
        relabelled = replace(base, team_id="Jacksonville Jaguars",
                             roster=(replace(base.roster[0], position="WR"),))
        b = ps.apply_latent(relabelled, draws).strength["players"]["p"]["latent_value"]
        self.assertEqual(a, b)
        self.assertIs(ps.apply_latent(TeamInput("Y", ("q",)), draws).strength, None)


class KernelTests(unittest.TestCase):
    def test_profile_and_record_model_must_agree_and_values_must_be_present(self):
        a, b = club("A"), club("B")
        with self.assertRaisesRegex(ValueError, "strength record is model"):
            resolve_game(a, b, seed=SEED, event_id="b7-mismatch", _test_profile=PROFILE_2014_5)
        roster = game_day_roster("C")
        v3 = TeamInput("C", tuple(p.player_id for p in roster), roster=roster,
                       strength={"model": strength.MODEL, "season": 2014, "as_of": "2014-09-07",
                                 "honour_seasons": [2011, 2012], "players": {}})
        with self.assertRaisesRegex(ValueError, "strength record is model"):
            resolve_game(v3, b, seed=SEED, event_id="b7-mismatch-2", _test_profile=PROFILE_2014_6)
        record = copy.deepcopy(a.strength)
        record["players"]["A-QB1"].pop("latent_value")
        with self.assertRaisesRegex(ValueError, "cannot resolve"):
            resolve_game(replace(a, strength=record), b, seed=SEED, event_id="b7-missing", _test_profile=PROFILE_2014_6)

    def test_no_per_possession_strength_block_and_the_test_hook(self):
        a, b = club("A", {"A-QB1": 1.5}), club("B")
        rows = []
        r = resolve_game(a, b, seed=SEED, event_id="b7-hidden", _test_profile=PROFILE_2014_6,
                         _test_strength_receipt=rows)
        self.assertEqual(validate_result(r), [])
        self.assertFalse(_has_key(r, "strength"))
        self.assertFalse(_has_key(r, "latent_value"))
        self.assertFalse(_has_key(r, "attribution_tier"))
        self.assertEqual(len(rows), len(r["possessions"]))
        a_drives = [x for x in rows if x["team"] == "A"]
        self.assertTrue(a_drives)
        passing = next(t for t in strength.TERMS_V4 if t["name"] == "td_share_offense_passing")
        for row in a_drives:
            self.assertAlmostEqual(row["terms"]["td_share_offense_passing"], passing["slope"] * (4.5 - passing["centre"]))
            self.assertEqual(row["sack_shift"], 0.0)  # protection-to-sack turned off by the keep rule
        # The 2014.5 profile still publishes the block for its own records.
        with self.assertRaises(TypeError):
            resolve_game(a, b, seed=SEED, event_id="b7-hook", _test_profile=PROFILE_2014_6, _test_strength_receipt={})

    def test_home_edge_v4_applies_only_at_home_venues(self):
        a, b = club("A"), club("B")
        rows = []
        resolve_game(a, b, seed=SEED, event_id="b7-home", venue="home", _test_profile=PROFILE_2014_6,
                     _test_strength_receipt=rows)
        homes = {x["team"]: x["home"] for x in rows}
        self.assertEqual(homes, {"A": strength.HOME_EDGE_V4, "B": 0.0})
        rows = []
        resolve_game(a, b, seed=SEED, event_id="b7-neutral", venue="neutral", _test_profile=PROFILE_2014_6,
                     _test_strength_receipt=rows)
        self.assertEqual({x["home"] for x in rows}, {0.0})

    def test_production_runner_refuses_the_hook(self):
        self.assertEqual(game_runner.architecture_errors(), [])


class DistributionTests(unittest.TestCase):
    """Sampled distributions, never one game. N fixed in advance (the plan's
    2 x 120 neutral games for the label swap)."""
    N = 120
    N_EFFECT = 200

    def test_label_swap_leaves_values_edges_and_the_distribution(self):
        values = {"A-QB1": 1.2, "A-WR1": -0.4, "A-DE1": 0.8}
        a = club("A", values)
        swapped = club("A", values, team_id="Jacksonville Jaguars")
        b = club("B")
        va, vb = game_day_roster("A"), game_day_roster("B")
        params = strength.parameters(strength.PLAYER_STATE_MODEL)
        self.assertEqual(strength.drive_edge(a, b, va, vb, va[0], False, params=params),
                         strength.drive_edge(swapped, b, va, vb, va[0], False, params=params))
        one = play(a, b, self.N, "swap-1")
        two = play(swapped, b, self.N, "swap-2")
        pts1 = [r["final_score"]["A"] for r in one]
        pts2 = [r["final_score"]["Jacksonville Jaguars"] for r in two]
        se = math.sqrt(pstdev(pts1) ** 2 / self.N + pstdev(pts2) ** 2 / self.N)
        self.assertLess(abs(mean(pts1) - mean(pts2)), 3 * se)
        pts_b1 = [r["final_score"]["B"] for r in one]
        pts_b2 = [r["final_score"]["B"] for r in two]
        se_b = math.sqrt(pstdev(pts_b1) ** 2 / self.N + pstdev(pts_b2) ** 2 / self.N)
        self.assertLess(abs(mean(pts_b1) - mean(pts_b2)), 3 * se_b)

    def test_one_capability_moves_its_matchup_only(self):
        b = club("B")
        base = play(club("A"), b, self.N_EFFECT, "base")
        better = play(club("A", {"A-QB1": 3.0}), b, self.N_EFFECT, "qb")
        td0, n0 = td_share(base, "A")
        td1, n1 = td_share(better, "A")
        se = math.sqrt(td0 * (1 - td0) / n0 + td1 * (1 - td1) / n1)
        self.assertGreater(td1 - td0, 2 * se)
        tb0, m0 = td_share(base, "B")
        tb1, m1 = td_share(better, "B")
        se_b = math.sqrt(tb0 * (1 - tb0) / m0 + tb1 * (1 - tb1) / m1)
        self.assertLess(abs(tb1 - tb0), 3 * se_b)

    def test_two_draws_on_identical_public_inputs_publish_identical_fields(self):
        a1, b = club("A", {"A-QB1": 0.5}), club("B")
        a2 = club("A", {"A-QB1": -0.5})
        public = lambda t: {k: v for k, v in t.strength["players"]["A-QB1"].items() if k != "latent_value"}
        self.assertEqual(public(a1), public(a2))
        r1 = resolve_game(a1, b, seed=SEED, event_id="b7-priv", _test_profile=PROFILE_2014_6)
        r2 = resolve_game(a2, b, seed=SEED, event_id="b7-priv", _test_profile=PROFILE_2014_6)
        self.assertEqual(set(r1), set(r2))
        self.assertEqual(set(r1["possessions"][0]), set(r2["possessions"][0]))
        for r in (r1, r2):
            self.assertFalse(_has_key(r, "strength"))


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store, self.client = local_service(self, self.tmp.name, "b7", snapshot="snapshot-b7")

    def test_schema_migration_keeps_every_row(self):
        path = Path(self.tmp.name) / "old.sqlite3"
        store = Store(path)
        store.initialize("snapshot-b7")
        store.close("event-1", b'{"event_id":"event-1"}')
        with store.connect() as c:
            c.execute("UPDATE meta SET value=? WHERE key='schema'", (b"1",))
            before = c.execute("SELECT event_id,packet_hash,result FROM events").fetchall()
        with mock.patch("runtime.private_service.SCHEMA", "2"):
            Store(path).initialize("snapshot-b7")
        with Store(path).connect() as c:
            after = c.execute("SELECT event_id,packet_hash,result FROM events").fetchall()
            schema = c.execute("SELECT value FROM meta WHERE key='schema'").fetchone()[0]
        self.assertEqual(before, after)
        self.assertEqual(schema, b"2")
        self.assertEqual(Store(path).schema_history(), [("1", "2")])

    def test_bind_is_idempotent_and_a_second_manifest_is_refused(self):
        first = self.client.bind_latent(2014, ps.manifest_sha256())
        second = self.client.bind_latent(2014, ps.manifest_sha256())
        self.assertEqual(first["commitment"], second["commitment"])
        self.assertTrue(second["idempotent"])
        self.assertEqual(first["rows"], 1708)
        table = ps.public_table()
        expected = sum(len(ps.row_keys(g, r, 2014, 2014)) for g, r in table.items())
        self.assertEqual(first["rows"], expected)
        with self.assertRaises(Exception):
            self.client.bind_latent(2014, "1" * 64)
        ready = self.client._request("/ready")
        self.assertEqual(ready["latent_bound"]["2014"]["commitment"], first["commitment"])
        self.assertNotIn("reference", json.dumps(ready))
        # The commitment is the sha256 over the sorted drawn rows.
        with self.store.connect() as c:
            rows = [("%d:%s:%s" % (y, g, s), z) for y, g, s, z in
                    c.execute("SELECT league_year,gsis_id,slot,z FROM latent_draws")]
        self.assertEqual(ps.commitment(rows), first["commitment"])

    def test_draws_refused_before_journaling_on_mismatch_and_while_locked(self):
        bound = self.client.bind_latent(2014, ps.manifest_sha256())
        keys = ps.record_keys(["00-0010346", "00-0029604"], 2014)
        roster = ps.roster_sha256(keys)
        with self.assertRaises(Exception):
            self.client.latent_draws("event-x", 2014, keys, roster)
        self.client.close_event({"event_id": "event-x", "fact": "x"})
        with self.assertRaises(Exception):
            self.client.latent_draws("event-x", 2014, keys, "0" * 64)
        draws = self.client.latent_draws("event-x", 2014, keys, roster)
        self.assertEqual(draws["commitment"], bound["commitment"])
        self.assertEqual(set(draws["draws"]), {ps.key_text(k) for k in keys})
        with self.assertRaises(Exception):
            self.client.latent_draws("event-x", 2014, keys[:1], ps.roster_sha256(keys[:1]))
        with self.assertRaises(ValueError):
            self.store.latent_draws("event-x", 2015, [ps.key_text(k) for k in keys], roster)
        # Locked while a snapshot advance is pending.
        from runtime.private_service import handler
        import threading
        from http.server import ThreadingHTTPServer
        from runtime.private_client import Client, PrivateRuntimeUnavailable
        from local_private_service import TOKEN
        server = ThreadingHTTPServer(("127.0.0.1", 0),
                                     handler(self.store, TOKEN, "snapshot-b7", locked_until="another-snapshot"))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        locked = Client(f"http://127.0.0.1:{server.server_port}", token=TOKEN, snapshot="snapshot-b7")
        with self.assertRaises(PrivateRuntimeUnavailable):
            locked.latent_draws("event-x", 2014, keys, roster)
        with self.assertRaises(PrivateRuntimeUnavailable):
            locked.bind_latent(2014, ps.manifest_sha256())

    def test_a_resume_gives_identical_draws_and_a_later_entrant_is_appended(self):
        self.client.bind_latent(2014, ps.manifest_sha256())
        self.client.close_event({"event_id": "event-y"})
        keys = ps.record_keys(["00-0010346"], 2014) + [ps.key(2014, "00-9999999", "b")]
        first = self.client.latent_draws("event-y", 2014, keys, ps.roster_sha256(keys))
        restarted = Store(Path(self.tmp.name) / "state.sqlite3")
        again = restarted.latent_draws("event-y", 2014, sorted(ps.key_text(k) for k in keys), ps.roster_sha256(keys))
        self.assertEqual(first["draws"], again["draws"])
        with restarted.connect() as c:
            z = c.execute("SELECT z FROM latent_draws WHERE gsis_id='00-9999999'").fetchone()[0]
            seed = c.execute("SELECT value FROM meta WHERE key='seed'").fetchone()[0]
        self.assertEqual(z, ps.z_text(ps.draw_z(ps.season_reference(seed, 2014), ps.key(2014, "00-9999999", "b"))))


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store, self.client = local_service(self, self.tmp.name, "b7-runner", snapshot="snapshot-b7")
        self.bound = self.store.bind_latent(2014, ps.manifest_sha256())

    def real_clubs(self):
        """Two real 2014 Week 1 game-day units (runtime.depth_library) with
        their public states under a binding stub naming the local service's
        commitment."""
        from runtime import depth_library
        from runtime.seasons import SeasonPaths
        library = depth_library.load(SeasonPaths(2014).background_depth)
        anchors = dict(offense_anchor=2.0, defense_anchor=2.0, special_teams_anchor=2.0)
        identities = week_inputs.identity_map(2014)
        inputs = []
        with mock.patch.object(ps, "binding", return_value=stub_binding(self.bound["commitment"])):
            for team in ("Denver Broncos", "Seattle Seahawks"):
                data = depth_library.club_input(team, library["clubs"][team], week=1, **anchors)
                data["active_players"] = week_inputs.game_day_actives(data["roster"])
                rows = week_inputs.strength_identities(data["roster"], 2014, club=library["clubs"][team],
                                                       identities=identities, strict=True)
                record, _ = strength.team_strength(team, rows, 2014, date(2014, 9, 7),
                                                   model=strength.PLAYER_STATE_MODEL)
                fields = {k: v for k, v in data.items() if k in TeamInput.__dataclass_fields__}
                fields.update(active_players=tuple(fields["active_players"]), roster=tuple(fields["roster"]),
                              strength=record)
                inputs.append(TeamInput(**fields))
        return inputs

    def test_runner_fetches_after_closure_replays_identically_and_hides_the_draws(self):
        home, away = self.real_clubs()
        patches = [mock.patch.object(ps, "binding", return_value=stub_binding(self.bound["commitment"])),
                   mock.patch.object(seasons, "require_game_release"),
                   mock.patch("runtime.KERNEL_VERSION", "2014.6"), mock.patch.object(game_runner, "KERNEL_VERSION", "2014.6"),
                   mock.patch("runtime.kernel.KERNEL_VERSION", "2014.6")]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        packet = game_runner.build_game_packet("2014-b7-runner", "snapshot-b7", home, away)
        self.assertFalse(_has_key(packet, "latent_value"))
        self.assertEqual(packet["home"]["strength"]["commitment"], self.bound["commitment"])
        first = game_runner.run_game(home, away, event_id="2014-b7-runner", snapshot="snapshot-b7", client=self.client)
        second = game_runner.run_game(home, away, event_id="2014-b7-runner", snapshot="snapshot-b7", client=self.client)
        self.assertEqual(first, second)
        self.assertEqual(first["kernel_version"], "2014.6")
        self.assertFalse(_has_key(first, "strength"))
        with self.store.connect() as c:
            self.assertEqual(c.execute("SELECT count(*) FROM latent_requests").fetchone()[0], 1)
        # A record naming another commitment than the committed binding is refused before closure.
        other = replace(home, strength=dict(home.strength, commitment="f" * 64))
        with self.assertRaises(ValueError):
            game_runner.build_game_packet("2014-b7-other", "snapshot-b7", other, away)
        # Drawn values may not enter a packet.
        drawn = ps.apply_latent(home, {ps.key_text(k): ps.z_text(0.0) for k in home.strength["latent_keys"]})
        with self.assertRaises(ValueError):
            game_runner.build_game_packet("2014-b7-drawn", "snapshot-b7", drawn, away)

    def test_records_absent_path_makes_no_latent_call(self):
        from support_rosters import single_quarterback_teams
        a, b = single_quarterback_teams()
        client = mock.Mock(snapshot="snapshot-b7")
        client.close_event.return_value = "ab" * 32
        with mock.patch.object(seasons, "require_game_release"):
            game_runner.run_game(a, b, event_id="2014-b7-plain", snapshot="snapshot-b7", client=client)
        client.latent_draws.assert_not_called()
        self.assertEqual((game_runner.fetch_latent(client, "x", a, b)), (a, b))


class WeeklyInputTests(unittest.TestCase):
    def test_identity_map_fills_and_conflicts_block(self):
        identities = {"Alpha Beta": "00-0000001", "Gamma Delta": "00-0000002"}
        rows = [{"player_id": "Alpha Beta"}, {"player_id": "Gamma Delta", "gsis_id": "00-0000002"}]
        out = week_inputs.strength_identities(rows, 2014, identities=identities, strict=True)
        self.assertEqual([r["gsis_id"] for r in out], ["00-0000001", "00-0000002"])
        with self.assertRaisesRegex(ValueError, "identity table"):
            week_inputs.strength_identities([{"player_id": "Gamma Delta", "gsis_id": "00-0000009"}], 2014,
                                            identities=identities)
        with self.assertRaisesRegex(ValueError, "no gsis id"):
            week_inputs.strength_identities([{"player_id": "Nobody"}], 2014, identities=identities, strict=True)
        self.assertIsNone(week_inputs.strength_identities([{"player_id": "Nobody"}], 2014,
                                                          identities=identities)[0]["gsis_id"])
        self.assertEqual(week_inputs.identity_map(2014)["Kirk Cousins"], "00-0029604")
        self.assertEqual(week_inputs.identity_map(2013), {})

    def test_exclusivity_gate_rejects_gsis_duplicates(self):
        from scripts.check_week_input_exclusivity import gsis_errors
        record_a = {"players": {"A One": {"gsis_id": "00-0000001"}, "A Two": {"gsis_id": "00-0000001"}},
                    "latent_keys": [["player-state-z-v1", 2014, "00-0000007", "b"]]}
        record_b = {"players": {"B One": {"gsis_id": "00-0000001"}}}
        games = [{"away": "A", "home": "B", "away_input": {"strength": record_a}, "home_input": {"strength": record_b}}]
        errors = gsis_errors(games)
        self.assertTrue(any("two roster rows" in e for e in errors))
        self.assertTrue(any("multiple weekly TeamInputs" in e for e in errors))
        self.assertTrue(any("latent key names gsis" in e for e in errors))
        self.assertEqual(gsis_errors([{"away": "A", "home": "B", "away_input": {}, "home_input": {}}]), [])

    def test_release_gate_applies_from_kernel_2014_6(self):
        self.assertIn("player_state", seasons.RELEASE_GATES)
        data = json.loads((ROOT / "runtime/season_readiness.json").read_text())
        gate = next(g for g in data["seasons"]["2014"]["gates"] if g["id"] == "player_state")
        self.assertEqual((gate["status"], gate["applies_from_kernel"]), ("BLOCKED", "2014.6"))
        errors = seasons.game_release_errors(2014)
        self.assertFalse(any(e.startswith("player_state") for e in errors))
        with mock.patch("runtime.KERNEL_VERSION", "2014.6"):
            errors = seasons.game_release_errors(2014)
        self.assertTrue(any(e.startswith("player_state") for e in errors))


class PrivacyAndObservablesTests(unittest.TestCase):
    def test_privacy_check_finds_a_leaking_record_and_passes_the_repository(self):
        from runtime.privacy import privacy_errors
        self.assertEqual(privacy_errors(ROOT), [])
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "career/x"
            folder.mkdir(parents=True)
            (folder / "leak.json").write_text(json.dumps({"kernel_version": "2014.6", "possessions": [
                {"strength": {"units": {}, "edge": 0.1}}]}))
            (folder / "old.json").write_text(json.dumps({"kernel_version": "2014.5", "possessions": [
                {"strength": {"units": {}, "edge": 0.1}}]}))
            (folder / "tier.json").write_text(json.dumps({"players": {"x": {"attribution_tier": "Plus"}}}))
            errors = privacy_errors(tmp)
        self.assertEqual(len(errors), 2)
        self.assertTrue(any("leak.json" in e for e in errors))
        self.assertTrue(any("tier.json" in e for e in errors))

    def test_observables_from_a_package_and_the_committed_backfill(self):
        from runtime import observables
        roster = game_day_roster("A")
        team = {"team_id": "A", "active_players": [p.player_id for p in roster if p.player_id != "A-WR5"][:40],
                "roster": [{"player_id": p.player_id, "position": p.position, "available": p.player_id != "A-WR5",
                            "depth": p.depth, "medical_limitation": "hold" if p.player_id == "A-WR5" else None}
                           for p in roster],
                "strength": {"players": {"A-QB1": {"gsis_id": "00-0000001"}}}}
        package = {"season": 2014, "week": 9, "games": [{"event_id": "e", "away": "A", "home": "B",
                                                         "away_input": team, "home_input": dict(team, team_id="B")}]}
        record = observables.from_package(package, {"A-WR1": "00-0000002"})
        rows = {r["player_id"]: r for r in record["clubs"]["A"]}
        self.assertEqual(rows["A-QB1"]["gsis_id"], "00-0000001")
        self.assertEqual(rows["A-WR1"]["gsis_id"], "00-0000002")
        self.assertEqual((rows["A-WR5"]["available"], rows["A-WR5"]["hold"], rows["A-WR5"]["active"]),
                         (False, "hold", False))
        self.assertEqual(record["feedback"]["applied"]["in_2014"], 0)
        self.assertFalse(_has_key(record, "latent_value"))
        self.assertFalse(_has_key(record, "expected"))
        committed = json.loads(observables.observables_path(4, 2014, ROOT).read_text())
        self.assertEqual(committed["week"], 4)
        self.assertEqual(len(committed["clubs"]), 26)
        self.assertIn("Jacksonville Jaguars", committed["club_basis"])
        self.assertTrue(all(r["gsis_id"] for rows in committed["clubs"].values() for r in rows))
        for week in (1, 2, 3):
            self.assertTrue(observables.observables_path(week, 2014, ROOT).is_file())


if __name__ == "__main__":
    unittest.main()
