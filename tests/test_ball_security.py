"""Kernel 2014.6 batch B10: ball security (W4 muffs; R12 layers A, B and C).

W4 and layer A (credit only, profile flag ball_security_credit): a muffed kick
names its muffer by the record's role, every kept or out-of-bounds fumble of
the replayed drive is seated on its laid-out snap, forcers and recoverers come
from the side-aware on-field sets, a forced fumble's tackle is the forcer's,
every name carries an attribution and no fumble is player evidence; outcomes
and the per-drive exposure are unchanged. Layer B (fumble_terminal_kind): a
lost fumble's terminal kind comes from the tuple's own lost entry. Layer C
(retained_kicks): the kicking club's recoveries at their real frequency, the
turnover the receiving club's, overtime kickoffs by rule R4 and overtime punts
excluding retained records (counted). Every number is read from the base's
artifacts (library/data/2010_2014w4_ball_security.json and the field-position
model's fumble annotations). Synthetic seeds only; the private service is
never contacted.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ast
import collections
import copy
import inspect
import json
import random
import unittest
from unittest import mock

from runtime import ball_security as bs
from runtime import bands, gamebook, participation, play_detail, usage
from runtime import chains as chain_walk
from runtime import field_position as fp
from runtime.calibration_base import BASE_2010_2014W4
from runtime.kernel import removal_names, resolve_game, validate_result
from runtime.play_detail import check_ledger, credit_kick_fumble
from runtime.profiles import B10_FLAGS, PROFILE_2014_5, PROFILE_2014_6, Profile
from runtime.rules import ot_history
from runtime.statbook import (KERNEL_2014_6_PLAYER_FIELDS, KERNEL_2014_6_TEAM_STAT_FIELDS, aggregate_receipts,
                              make_receipt)
from synthetic_games import SEED, sample_teams
from test_profiles import strip_2014_6_fields

ROOT = Path(__file__).resolve().parents[1]
A, B = sample_teams()
MODEL = BASE_2010_2014W4.ball_security()
FPM = BASE_2010_2014W4.field_position()
ART = json.loads((ROOT / "library/data/2010_2014w4_ball_security.json").read_text())


def level(flags):
    return Profile("2014.6", base=PROFILE_2014_6.base, cell_rules=PROFILE_2014_6.cell_rules,
                   strength=PROFILE_2014_6.strength, flags=frozenset(flags), record_base=True)


# Kernel 2014.6 without batch B10, and with its credit layer only.
B10_OFF = level(PROFILE_2014_6.flags - B10_FLAGS)
CREDIT_ONLY = level(B10_OFF.flags | {"ball_security_credit"})


def play(name, profile=PROFILE_2014_6, forced=None, **kw):
    return resolve_game(A, B, seed=SEED + b"-" + name.encode(), event_id=name, _test_profile=profile,
                        _test_scoring=forced, **kw)


def receipt(result, detail="compact_stats"):
    return make_receipt(result, week=5, matchup="B at A", detail=detail)


def clean(result):
    return (validate_result(result) + check_ledger(result) + check_ledger(receipt(result, "full"))
            + check_ledger(receipt(result)))


# Synthetic labels that reach each branch under PROFILE_2014_6 (found by a
# search over the same label pattern; each test fails loudly if its label no
# longer reaches the branch).
# Re-searched for batch B11 (the penalty records move every later result)
# and again for batch B13 (the replayed yard split moves every later layout
# and the decisions read from it): each is the first label of the same
# pattern that reaches the branch (the Pro Bowl label still does).
OT_REGULAR = "b10-ot-4"
OT_POSTSEASON = "b10-ot-22"
OT_PUNT = "b10-otp-11"
PRO_BOWL = "b10-pb-9"


def _club(result, pid):
    return next((t for t, s in result["team_stats"].items() if pid in s["players"]), None)


def fumble_rows(result):
    return [r for r in result["play_ledger"] if isinstance(r.get("fumble"), dict)]


class Sample:
    """One cached 60-game sample of the shipped profile."""
    games = None

    @classmethod
    def get(cls):
        if cls.games is None:
            cls.games = [play("b10-sample-%d" % i) for i in range(60)]
        return cls.games


# ---- the model and its pure helpers ---------------------------------------------------------

class ModelTests(unittest.TestCase):
    def test_artifact_is_pinned_and_read(self):
        self.assertIn("ball_security", BASE_2010_2014W4.roles())
        self.assertEqual(MODEL.data["schema"], bs.SCHEMA)
        c = MODEL.centres
        for name in ("fumbles_per_team_game", "lost_per_team_game", "offense_kept_share_of_scrimmage_fumbles",
                     "sack_share_of_lost_scrimmage_fumbles", "forced_share_of_lost_non_aborted_scrimmage_fumbles",
                     "forcer_also_recovers", "muffs_per_punt", "punt_muff_receiving_keep_share"):
            entry = c[name]
            self.assertEqual(entry["pooled"], [sum(v[0] for v in entry["by_season"].values()),
                                               sum(v[1] for v in entry["by_season"].values())])
        self.assertEqual(c["fumbles_per_team_game"]["pooled"][1], 2170)
        # The kicking-team recoveries are the field-position artifact's own
        # retained kick records, in the engine's scope.
        retained = FPM.data["retained_kick_pools"]
        k = c["kicking_team_recoveries_per_team_game"]
        self.assertEqual(k["punt"]["pooled"][0], len(retained["punt"]))
        self.assertEqual(k["kickoff"]["pooled"][0], len(retained["kickoff"]) + len(retained["free_kick"]))
        self.assertAlmostEqual(k["centre"], k["punt"]["pooled"][0] / k["punt"]["pooled"][1]
                               + k["kickoff"]["pooled"][0] / k["kickoff"]["pooled"][1], places=6)
        self.assertEqual(ART["field_position_sha256"], BASE_2010_2014W4.pin("field_position").sha256)
        self.assertTrue(ART["second_pass"]["agree"])

    def test_muffer_roles_match_the_pool(self):
        K, P = FPM.KICK, FPM.PUNT
        roles = collections.Counter()
        for name, index in (("kickoff_pool", K), ("free_kick_pool", K), ("punt_pool", P)):
            for r in FPM.data[name]:
                f = r[index["fumble"]]
                if f and f[0] == "muff":
                    roles[f[2] or "unrecorded"] += 1
        share = MODEL.centres["muffer_role_share"]
        self.assertEqual(share["returner"], [roles["returner"], roles["returner"] + roles["other"]])
        self.assertEqual(share["unrecorded"], roles["unrecorded"])

    def test_no_club_identity(self):
        tree = ast.parse(inspect.getsource(bs))
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {
            n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        self.assertFalse({"team_id", "controlled_team"} & names)

    def test_stream_keys_are_literal(self):
        one = bs.stream(SEED, "e", "scrim", 3).random()
        self.assertEqual(one, bs.stream(SEED, "e", "scrim", 3).random())
        self.assertNotEqual(one, bs.stream(SEED, "e", "punt", 3).random())
        self.assertNotEqual(one, bs.stream(SEED, "e", "kick", 3).random())
        self.assertEqual(bs.TAG, "public-ball-security-v1")

    def test_slope_zero_terms(self):
        self.assertEqual(set(bs.TERMS), {"carrier_ball_security", "returner_muffs", "defender_forcing"})
        self.assertTrue(all(v == 0.0 for v in bs.TERMS.values()))
        self.assertEqual(bs.TERM_STATUS, "not studied (admissible 2010-2012 evidence exists)")

    def test_terminal_kind_and_entries(self):
        def entry(kind, outcome="lost", host=None):
            return [0, kind, host, outcome, 1, "DL", "DL", 0, 0]
        self.assertEqual(bs.terminal_kind(bs.lost_entry([entry("run")])), "run")
        self.assertEqual(bs.terminal_kind(bs.lost_entry([entry("reception")])), "catch")
        self.assertEqual(bs.terminal_kind(bs.lost_entry([entry("sack")])), "sack")
        self.assertEqual(bs.terminal_kind(bs.lost_entry([entry("aborted", host="run")])), "run")
        self.assertEqual(bs.terminal_kind(bs.lost_entry([entry("aborted", host="sack")])), "sack")
        self.assertIsNone(bs.lost_entry([entry("kick")]))
        self.assertIsNone(bs.lost_entry([entry("run", "kept")]))
        self.assertIsNone(bs.terminal_kind(None))
        # A kick-play entry (the drive's own punt) belongs to its kick record.
        self.assertEqual(bs.entries([entry("kick", "kept"), entry("run", "kept")])[0]["kind"], "run")

    def test_scrimmage_index_skips_no_play_rows(self):
        e = dict(zip(bs.FUMBLE_FIELDS, [5, "run", "run", "kept", 0, None, "RB", 0, 1]))
        pen = [[1, 7, "D", 5, "A", "N", 0, "no_play", 0, 5], [3, 9, "O", -5, "A", "S", 0, "run", 0, 5],
               [6, 4, "D", 5, "A", "N", 0, "no_play", 0, 5]]
        self.assertEqual(bs.scrimmage_index(e, pen), 4)

    def test_seat_kept_rules(self):
        kinds = ["run", "att", "run", "sack", "kneel", "run"]
        completed = [False, True, False, False, False, False]
        fumbles = [[2, "run", "run", "kept", 0, None, "RB", 0, 1],      # nearest run to 2: snap 2
                   [5, "run", "run", "kept", 0, None, "RB", 0, 1],      # 5 is the terminal: nearest legal run 2 taken, so 0
                   [1, "reception", "complete", "oob", 1, "DB", None, 0, 0],
                   [3, "sack", "sack", "kept", 1, "DL", "OL", 0, 0],
                   [4, "aborted", "incomplete", "kept", 0, None, "QB", 0, 1],  # no other pass: falls back
                   [9, "run", "run", "kept", 0, None, "RB", 0, 1]]      # beyond the 6 kept of 12: cut
        diagnostics = {}
        seated = bs.seat_kept([(0, 6, fumbles, (), 12)], kinds, completed, 5, diagnostics)
        self.assertEqual([(e["snap_order"], i) for e, i in seated], [(2, 2), (5, 0), (1, 1), (3, 3)])
        self.assertEqual(diagnostics, {"kept_fumble_unseated": 1, "kept_fumble_cut": 1})
        for _, i in seated:
            self.assertNotIn(kinds[i], ("kneel", "spike"))
            self.assertNotEqual(i, 5)
        # A whole replayed drive cuts nothing: a stored order past its last
        # snap (a timeout or two-minute-warning row the tuple does not
        # record) is bounded there and seated nearest it.
        diagnostics = {}
        seated = bs.seat_kept([(0, 4, [[7, "run", "run", "kept", 0, None, "RB", 0, 1]], ())],
                              ["run", "run", "att", "run"], [False, False, True, False], 3, diagnostics)
        self.assertEqual([i for _, i in seated], [1])
        self.assertEqual(diagnostics, {})
        # Pool check: the bound applies to under 5% of the pool's kept entries
        # (the no-play rows a tuple does not record).
        T, beyond, total = FPM.T, 0, 0
        for category in fp.CATEGORIES:
            for t in fp._v3_tuples(FPM.load(), category):
                plays = t[T["runs"]] + t[T["attempts"]] + t[T["sacks"]] + len(t[T["kneel_yards"]]) + t[T["spikes"]]
                for e in bs.entries(FPM.value(t, "fumbles", ())):
                    total += 1
                    beyond += bs.scrimmage_index(e, FPM.value(t, "pen", ())) >= plays
        self.assertLess(beyond / total, 0.05)

    def test_synthetic_entry_draws_four_uniforms(self):
        rng = random.Random(7)
        entry = MODEL.synthetic_entry("run", rng)
        self.assertEqual(entry["outcome"], "lost")
        after = rng.random()
        rng2 = random.Random(7)
        for _ in range(4):
            rng2.random()
        self.assertEqual(after, rng2.random())
        self.assertIn(entry["recoverer_group"], ("DL", "LB", "DB"))

    def test_aborted_share_is_the_artifacts(self):
        a = ART["credit_shares"]["aborted_fumbler"]
        self.assertAlmostEqual(MODEL.p_centre_aborted, a["OL"] / (a["QB"] + a["OL"] + a["other"]))
        self.assertGreater(MODEL.p_kick("return", "forced"), MODEL.p_kick("muff", "forced"))


# ---- W4: muffs ------------------------------------------------------------------------------

def _week4_like_punt():
    """The punt record the closed Week 4 receipt's muffed punt replays: LOS
    38, gross 31 (LOS 39 and gross 32 there, the punter's term +1), no
    return, enforcement -5, muffed by the returner and out of bounds (next
    start 88: the receiving club's 12)."""
    P = FPM.PUNT
    for r in FPM.data["punt_pool"]:
        if (r[P["outcome"]], r[P["los"]], r[P["gross"]], r[P["return_yards"]], r[P["enforcement"]]) == (
                "muffed", 38, 31, 0, -5):
            return r
    raise AssertionError("the Week 4 punt record is not in the pool")


class MuffTests(unittest.TestCase):
    def units(self, row, kicking_players, receiving_players):
        return participation.kick(row, "K", "R", kicking_players, receiving_players)

    def test_week4_regression_names_the_muffer(self):
        record = _week4_like_punt()
        P = FPM.PUNT
        self.assertEqual(record[P["fumble"]], ["muff", "oob", "returner"])
        punt = {"los": 39, "outcome": "muffed", "gross": record[P["gross"]], "return_yards": 0,
                "enforcement": record[P["enforcement"]], "touchback": False,
                "next_start": FPM.punt_start(record, 39)}
        adjusted = fp.adjust_punt(punt, 1)
        self.assertEqual((adjusted["gross"], adjusted["next_start"]), (32, 88))
        kicking, receiving = B.roster, A.roster
        row = {"play_type": "punt", "offense": "K", "defense": "R", "punter": None, "long_snapper": None,
               "cover_player": None, "returner": None, "return_yards": 0, "outcome": "muffed"}
        units = self.units(row, kicking, receiving)
        stats = {"K": {"players": {p.player_id: collections.Counter() for p in kicking}, "muffs": 0, "fumbles": 0,
                       "fumbles_lost": 0, "kicking_team_recoveries": 0},
                 "R": {"players": {p.player_id: collections.Counter() for p in receiving}, "muffs": 0, "fumbles": 0,
                       "fumbles_lost": 0, "kicking_team_recoveries": 0}}
        compact = credit_kick_fumble(row, record[P["fumble"]], retained=False, kicking="K", receiving="R",
                                     units=units, stats=stats, rng=bs.stream(SEED, "w4", "punt", 15), model=MODEL)
        returner = usage.club_returner(receiving, "punt_return")
        self.assertEqual(row["muffed_by"], returner.player_id)
        self.assertEqual(row["fumble"]["attribution"]["fumbled_by"], bs.RETURNER)
        self.assertIsNone(row["fumble"]["recovered_by"])          # out of bounds at the 12
        self.assertEqual(compact, {"kind": "muff", "outcome": "oob", "role": "returner", "forced": row["fumble"]["forced"],
                                   "counted": True})
        line = stats["R"]["players"][returner.player_id]
        self.assertEqual((line["muffs"], line["fumbles"], line["fumbles_lost"], line["punt_returns"]), (1, 1, 0, 0))
        self.assertEqual(stats["R"]["muffs"], 1)
        self.assertNotIn("own_recovery_yards", row)

    def test_other_role_draws_from_the_return_unit(self):
        kicking, receiving = B.roster, A.roster
        row = {"play_type": "punt", "offense": "K", "defense": "R", "returner": None, "return_yards": 4,
               "outcome": "muffed"}
        units = self.units(row, kicking, receiving)
        stats = {t: {"players": {p.player_id: collections.Counter() for p in roster}, "muffs": 0, "fumbles": 0,
                     "fumbles_lost": 0, "kicking_team_recoveries": 0} for t, roster in (("K", kicking), ("R", receiving))}
        credit_kick_fumble(row, ["muff", "kept", "other"], retained=False, kicking="K", receiving="R", units=units,
                           stats=stats, rng=bs.stream(SEED, "w4", "punt", 2), model=MODEL)
        self.assertIn(row["muffed_by"], units["R"])
        self.assertNotEqual(row["muffed_by"], units["R"][0])
        self.assertEqual(row["fumble"]["attribution"]["fumbled_by"], bs.GROUP_DRAW)
        self.assertEqual(row["own_recovery_yards"], 4)
        # A kept kickoff muff with no recorded muffer is a muff only.
        row2 = {"play_type": "kickoff", "offense": "K", "defense": "R", "returner": units["R"][0]}
        compact = credit_kick_fumble(row2, ["muff", "kept", None], retained=False, kicking="K", receiving="R",
                                     units=units, stats=stats, rng=bs.stream(SEED, "w4", "kick", 2), model=MODEL)
        self.assertFalse(compact["counted"])
        self.assertEqual(row2["fumble"]["attribution"]["fumbled_by"], bs.CONVENTION)

    def test_every_muffed_kick_names_its_muffer_in_play(self):
        muffs = 0
        for r in Sample.get():
            for row in r["play_ledger"]:
                if row.get("play_type") in ("punt", "kickoff", "free_kick") and (
                        row.get("outcome") == "muffed" or (row.get("fumble") or {}).get("kind") == "muff"):
                    muffs += 1
                    self.assertTrue(row.get("muffed_by"))
                    self.assertIn(row["muffed_by"], r["team_stats"][row["defense"]]["players"])
                    if row["play_type"] == "punt":
                        self.assertIsNone(row.get("returner"))
                        self.assertIsNone(row.get("cover_player"))
        self.assertGreater(muffs, 0)

    def test_muff_without_muffer_is_detected(self):
        r = next(g for g in Sample.get() if any(row.get("muffed_by") for row in g["play_ledger"]))
        doctored = copy.deepcopy(r)
        row = next(row for row in doctored["play_ledger"] if row.get("muffed_by"))
        row["muffed_by"] = None
        self.assertTrue(any(e.startswith("muff_without_muffer") for e in check_ledger(doctored)))


# ---- layer A: credit -------------------------------------------------------------------------

class CreditTests(unittest.TestCase):
    def test_sample_is_clean_and_reconciles(self):
        for r in Sample.get():
            self.assertEqual(clean(r), [], r["event_id"])
            for team, s in r["team_stats"].items():
                players = s["players"].values()
                self.assertEqual(s["fumbles"], sum(p["fumbles"] for p in players))
                self.assertEqual(s["fumbles_lost"], sum(p["fumbles_lost"] for p in players))
                self.assertEqual(s["muffs"], sum(p.get("muffs", 0) for p in players))
        self.assertEqual(Sample.get()[0]["ball_security"], {"model": bs.MODEL, "credit": True, "terminal_kind": True,
                                                            "retained_kicks": True})

    def test_fumble_records(self):
        kept = lost = forced = 0
        for r in Sample.get():
            for row in fumble_rows(r):
                f = row["fumble"]
                self.assertEqual(bool(f["forced"]), bool(f["forced_by"]))
                self.assertIn("fumbled_by", f["attribution"])
                if f["forced"]:
                    forced += 1
                    self.assertIn("forced_by", f["attribution"])
                if f["recovered_by"] is not None:
                    self.assertIn("recovered_by", f["attribution"])
                if f["outcome"] == "oob":
                    self.assertIsNone(f["recovered_by"])
                if row["play_type"] in ("pass", "run"):
                    self.assertEqual(bool(row["turnover"]), f["outcome"] == "lost")
                    if f["outcome"] == "lost":
                        lost += 1
                        self.assertEqual(f["recovering_team"], row["defense"])
                    elif f["outcome"] == "kept":
                        kept += 1
                        self.assertEqual(f["recovering_team"], row["offense"])
                    if f["forced"] and f["attribution"]["forced_by"] == bs.RUSHER:
                        # A sack's forcer is its own rusher.
                        self.assertTrue(row.get("sack"))
                        self.assertEqual(f["forced_by"], row["tackler"])
                    elif f["forced"] and (row.get("completion") or row["play_type"] == "run"):
                        # A forced fumble's tackle is the forcer's.
                        self.assertEqual(row["tackler"], f["forced_by"])
                        self.assertIsNone(row.get("assist_tackler"))
                    elif f["outcome"] == "lost" and not f["forced"] and not row.get("sack"):
                        self.assertIsNone(row.get("tackler"))
        self.assertGreater(kept, 0)
        self.assertGreater(lost, 0)
        self.assertGreater(forced, 0)

    def test_names_come_from_the_on_field_sets(self):
        """Every scrimmage forcer and drawn recoverer is a player of the
        side-aware on-field set (runtime.participation.slot_lineup) of his
        own side; every kick-play name one of the play's units."""
        checked = 0
        real = participation.slot_lineup
        for i in range(10):
            seen = []

            def spy(*args, **kw):
                out = real(*args, **kw)
                seen.append(({s["player"].player_id for s in out["offense"]},
                             {s["player"].player_id for s in out["defense"]}))
                return out
            with mock.patch.object(participation, "slot_lineup", spy):
                r = play("b10-sample-%d" % i)
            for row in fumble_rows(r):
                f = row["fumble"]
                if row["play_type"] in ("pass", "run"):
                    offense = set().union(*(o for o, _ in seen if row["offense"] in {_club(r, x) for x in o}))
                    defense = set().union(*(d for _, d in seen if row["defense"] in {_club(r, x) for x in d}))
                    if f["forced"] and f["attribution"]["forced_by"] != bs.RUSHER:
                        self.assertIn(f["forced_by"], defense)
                    if f["recovered_by"] and f["attribution"]["recovered_by"] in (bs.GROUP_DRAW, bs.GROUP_FALLBACK):
                        self.assertIn(f["recovered_by"], defense if f["outcome"] == "lost" else offense)
                    checked += 1
                else:
                    kicking, receiving = row["offense"], row["defense"]
                    self.assertEqual(_club(r, f["fumbled_by"]), receiving)
                    if f["forced"]:
                        self.assertEqual(_club(r, f["forced_by"]), kicking)
                    if f["recovered_by"]:
                        self.assertEqual(_club(r, f["recovered_by"]), f["recovering_team"])
        self.assertGreater(checked, 0)

    def test_fumbles_are_never_player_evidence(self):
        for r in Sample.get():
            self.assertFalse([e for e in r["player_evidence"] if e.get("physical_execution") == "fumble lost"])
        # The kernel without the credit still records the lost-fumble
        # observation (unchanged), over enough games to see one.
        old = [play("b10-old-%d" % i, profile=B10_OFF) for i in range(8)]
        self.assertTrue(any(e.get("physical_execution") == "fumble lost" for r in old for e in r["player_evidence"]))

    def test_removal_names_are_side_aware(self):
        row = {"play_type": "punt", "offense": "K", "defense": "R", "punter": "p1", "muffed_by": "r1",
               "fumble": {"fumbled_by": "r1", "forced_by": "k2", "recovered_by": "k3", "recovering_team": "K"}}
        self.assertEqual(set(removal_names(row)), {("K", "p1"), ("R", "r1"), ("K", "k2"), ("K", "k3")})
        scrim = {"play_type": "run", "offense": "O", "defense": "D", "runner": "o1",
                 "fumble": {"fumbled_by": "o1", "forced_by": "d1", "recovered_by": "o2", "recovering_team": "O"}}
        self.assertEqual(set(removal_names(scrim)), {("O", "o1"), ("D", "d1"), ("O", "o2")})

    def test_fumble_credit_incoherent_is_detected(self):
        r = next(g for g in Sample.get() if fumble_rows(g))
        doctored = copy.deepcopy(r)
        row = fumble_rows(doctored)[0]
        row["fumble"]["forced"] = not row["fumble"]["forced"]
        self.assertTrue(any(e.startswith("fumble_credit_incoherent") for e in check_ledger(doctored)))
        compact = receipt(r)
        team = next(iter(compact["team_stats"]))
        compact["team_stats"][team]["fumbles"] += 1
        self.assertTrue(any(e.startswith("fumble_credit_incoherent") for e in check_ledger(compact)))


class ProjectionTests(unittest.TestCase):
    """The plan's B10 gate for W4 and layer A: outcomes and per-drive
    exposure identical once the declared fields are stripped."""

    GAMES = 40

    @staticmethod
    def captured(name, profile):
        hazards, kicks = [], []
        real_scrimmage, real_credit = participation.scrimmage, participation.credit

        def scrimmage(*args, **kw):
            out = real_scrimmage(*args, **kw)
            if kw.get("hazard_out") is not None:
                hazards.append(copy.deepcopy(kw["hazard_out"]))
            return out

        def credit(stats, team_id, snaps, side):
            if side == "special_teams":
                kicks.append((team_id, sorted(snaps)))
            return real_credit(stats, team_id, snaps, side)

        with mock.patch.object(participation, "scrimmage", scrimmage), \
                mock.patch.object(participation, "credit", credit):
            result = play(name, profile=profile)
        return result, hazards, kicks

    @staticmethod
    def outcome(result):
        out = strip_2014_6_fields(result)
        # Declared: the fumble observations leave the player evidence, and the
        # credit's own counters join the diagnostics.
        for key in ("player_evidence", "diagnostics"):
            out.pop(key, None)
        for team in out["team_stats"].values():
            team.pop("players")
        for p in out["possessions"]:
            if isinstance(p.get("punt"), dict):
                p["punt"].pop("fumble", None)
        for row in out["play_ledger"]:
            # The declared credit change on a row: a forced fumble's tackle
            # is the forcer's, a lost fumble's terminal snap draws no defender.
            for key in ("tackler", "assist_tackler"):
                row.pop(key, None)
        return out

    def test_credit_changes_no_outcome_or_exposure(self):
        changed = 0
        for i in range(self.GAMES):
            name = "b10-proj-%d" % i
            on, h_on, k_on = self.captured(name, CREDIT_ONLY)
            off, h_off, k_off = self.captured(name, B10_OFF)
            self.assertEqual(self.outcome(on), self.outcome(off), name)
            self.assertTrue(h_on and k_on, name)
            self.assertEqual(h_on, h_off, name)
            self.assertEqual(k_on, k_off, name)
            self.assertEqual([e for e in on["player_evidence"]],
                             [e for e in off["player_evidence"] if e.get("physical_execution") != "fumble lost"])
            self.assertEqual(on["injuries"], off["injuries"])
            self.assertEqual(validate_result(on), [])
            changed += bool(fumble_rows(on))
        self.assertGreater(changed, 0)


# ---- layer B: the terminal kind ----------------------------------------------------------------

class TerminalKindTests(unittest.TestCase):
    def layout(self, lost_kind, runs=2, attempts=2, sacks=1):
        return chain_walk.drive_layout(
            seed=SEED, event_id="b10-tk", drive_no=1, offense="A", category="fumble_lost", td_type=None,
            runs=runs, attempts=attempts, sacks=sacks, kneel_yards=[], spikes=0, pass_yards=8, rush_free=6,
            losses=[5] * sacks, safety_terminal=None, net=9, spot=60, completion_rate=0.6, lost_kind=lost_kind,
            diagnostics={})

    def test_kind_from_the_entry(self):
        for kind in ("run", "catch", "sack"):
            self.assertEqual(self.layout(kind)["terminal"], kind)

    def test_unavailable_kind_falls_back_and_is_counted(self):
        diagnostics = {}
        out = chain_walk.drive_layout(
            seed=SEED, event_id="b10-tk", drive_no=1, offense="A", category="fumble_lost", td_type=None, runs=3,
            attempts=2, sacks=0, kneel_yards=[], spikes=0, pass_yards=8, rush_free=6, losses=[], safety_terminal=None,
            net=14, spot=60, completion_rate=0.6, lost_kind="sack", diagnostics=diagnostics)
        self.assertNotEqual(out["terminal"], "sack")
        self.assertEqual(diagnostics.get("fumble_terminal_fallback"), 1)

    def test_kernel_terminal_is_the_entrys_kind(self):
        """Layer B in play: every lost scrimmage fumble's terminal snap is of
        its entry's kind (an aborted snap any kind), the fallbacks counted;
        with the credit layer alone the terminal kind is the snap-count draw."""
        mapping = {"run": "run", "reception": "pass", "sack": "sack"}

        def mismatches(games):
            lost = wrong = 0
            for r in games:
                for p in r["possessions"]:
                    for f in p.get("fumbles") or ():
                        if f["terminal"]:
                            lost += 1
                            wrong += f["kind"] in mapping and mapping[f["kind"]] != f["snap_kind"]
            return lost, wrong
        lost, wrong = mismatches(Sample.get())
        fallbacks = sum(r["diagnostics"].get("fumble_terminal_fallback", 0) for r in Sample.get())
        self.assertGreater(lost, 30)
        self.assertLessEqual(wrong, fallbacks)
        _, drawn = mismatches(play("b10-sample-%d" % i, profile=CREDIT_ONLY) for i in range(20))
        self.assertGreater(drawn, 0)

    def test_realised_kind_shares_match_the_pool(self):
        """The realised terminal kinds against the base pool's lost entries
        (bands.terminal_kind_centres), within three standard errors."""
        centres = bands.terminal_kind_centres(BASE_2010_2014W4)
        total = sum(centres.values())
        self.assertEqual(total, sum(1 for t in fp._v3_tuples(FPM.load(), "fumble_lost")
                                    if bs.terminal_kind(bs.lost_entry(FPM.value(t, "fumbles", ())))))
        realised = collections.Counter()
        for r in Sample.get():
            for p in r["possessions"]:
                for f in p.get("fumbles") or ():
                    if f["terminal"]:
                        realised[{"pass": "catch"}.get(f["snap_kind"], f["snap_kind"])] += 1
        n = sum(realised.values())
        for kind, count in centres.items():
            share = count / total
            self.assertLessEqual(abs(realised[kind] / n - share), 3 * (share * (1 - share) / n) ** 0.5, kind)

    def test_aborted_snap_is_carried_by_the_quarterback_or_the_centre(self):
        carriers = collections.Counter()
        for r in Sample.get():
            for row in fumble_rows(r):
                f = row["fumble"]
                if f["kind"] == "aborted" and f["outcome"] == "lost" and row["play_type"] == "run":
                    pos = r["team_stats"][row["offense"]]["players"][row["runner"]]["position"]
                    carriers[usage.group(pos)] += 1
                    self.assertEqual(row["runner"], f["fumbled_by"])
                    self.assertEqual(f["attribution"]["fumbled_by"], bs.SOURCED_SHARE)
        self.assertTrue(set(carriers) <= {"QB", "OL"})


# ---- layer C: retained kicks ---------------------------------------------------------------------

class RetainedKickTests(unittest.TestCase):
    def test_full_pools(self):
        P, K = FPM.PUNT, FPM.KICK
        self.assertEqual(sum(r[P["possession"]] == "kicking" for r in FPM._punt_pool_all), 105)
        self.assertEqual(sum(r[K["possession"]] == "kicking" for r in FPM._kick_pools_all["kickoff_pool"]), 41)
        self.assertFalse(any(r[P["possession"]] == "kicking" for r in FPM._punt_pool))
        rng = random.Random(3)
        draws = [FPM.punt(rng, 60, retained=False)["outcome"] for _ in range(400)]
        self.assertNotIn("retained", draws)

    def test_retained_possessions_in_play(self):
        punts = kicks = 0
        for r in Sample.get():
            by_number = {p["number"]: p for p in r["possessions"]}
            for p in r["possessions"]:
                if (p.get("punt") or {}).get("outcome") == "retained":
                    punts += 1
                    nxt = by_number[p["number"] + 1]
                    self.assertEqual((nxt["team"], nxt["start_kind"], nxt["start_spot"]),
                                     (p["team"], "punt_retained", p["next_start"]))
                    self.assertNotEqual(p["half"], "OT")
            for k in r["kickoffs"]:
                if k["outcome"] == "retained":
                    kicks += 1
                    self.assertEqual(k["fumble"]["outcome"], "lost")
            ktr = {t: s["kicking_team_recoveries"] for t, s in r["team_stats"].items()}
            retained_by = collections.Counter(k["kicking"] for k in r["kickoffs"] if k["outcome"] == "retained")
            for p in r["possessions"]:
                if (p.get("punt") or {}).get("outcome") == "retained":
                    retained_by[p["team"]] += 1
            self.assertEqual(ktr, {t: retained_by.get(t, 0) for t in ktr})
        self.assertGreater(punts + kicks, 0)

    def test_turnover_is_the_receiving_clubs(self):
        r = play("b10-forced-retained", forced={"kicks": {1: "retained"}})
        self.assertEqual(clean(r), [])
        k = r["kickoffs"][0]
        self.assertEqual(k["outcome"], "retained")
        receiving = r["team_stats"][k["receiving"]]
        self.assertGreaterEqual(receiving["turnovers"], 1)
        self.assertEqual(r["possessions"][0]["team"], k["kicking"])
        self.assertEqual(r["team_stats"][k["kicking"]]["kicking_team_recoveries"], 1)
        row = next(x for x in r["play_ledger"] if x["play_type"] == "kickoff")
        self.assertEqual(row["fumble"]["recovering_team"], k["kicking"])
        self.assertIn(row["fumble"]["recovered_by"], r["team_stats"][k["kicking"]]["players"])

    def test_overtime_retained_kickoff_follows_r4_in_both_overtimes(self):
        for game_type, name in (("regular", OT_REGULAR), ("postseason", OT_POSTSEASON)):
            base = play(name, game_type=game_type)
            openers = [k["kick_no"] for k in base["kickoffs"] if k["half"] == "OT"]
            if not openers:
                raise AssertionError("%s no longer reaches overtime; search another label" % name)
            r = play(name, forced={"kicks": {openers[0]: "retained"}}, game_type=game_type)
            self.assertEqual(clean(r), [], game_type)
            kick = r["kickoffs"][openers[0] - 1]
            self.assertEqual(kick["outcome"], "retained")
            ot = [p for p in r["possessions"] if p["half"] == "OT"]
            self.assertEqual((ot[0]["team"], ot[0]["start_kind"]), (kick["kicking"], "kickoff_retained"))
            history = ot_history(ot, [k for k in r["kickoffs"] if k["half"] == "OT"])
            self.assertEqual(history[0]["opportunity"], "kicking-club recovery (R4)")
            self.assertEqual(r["team_stats"][kick["kicking"]]["kicking_team_recoveries"],
                             sum(k["outcome"] == "retained" and k["kicking"] == kick["kicking"] for k in r["kickoffs"])
                             + sum((p.get("punt") or {}).get("outcome") == "retained" and p["team"] == kick["kicking"]
                                   for p in r["possessions"]))

    def test_overtime_punts_exclude_retained_records(self):
        r = play(OT_PUNT, game_type="postseason")
        self.assertEqual(clean(r), [])
        self.assertGreater(r["diagnostics"].get("ot_punt_retained_excluded", 0), 0,
                           "%s no longer excludes an overtime retained punt; search another label" % OT_PUNT)
        self.assertGreater(r["diagnostics"]["ot_punt_retained_records_excluded"], 0)
        for p in r["possessions"]:
            if p["half"] == "OT":
                self.assertNotEqual((p.get("punt") or {}).get("outcome"), "retained")

    def test_pro_bowl_retained_punt_validates(self):
        r = play(PRO_BOWL, game_type="pro_bowl")
        self.assertEqual(clean(r), [])
        retained = [p for p in r["possessions"] if (p.get("punt") or {}).get("outcome") == "retained"]
        self.assertTrue(retained, "%s no longer retains a punt; search another label" % PRO_BOWL)
        by_number = {p["number"]: p for p in r["possessions"]}
        for p in retained:
            nxt = by_number.get(p["number"] + 1)
            if nxt is not None and nxt.get("quarter") == p.get("quarter"):
                self.assertEqual((nxt["team"], nxt["start_kind"]), (p["team"], "punt_retained"))

    def test_retained_punt_identity_is_audited(self):
        r = next((g for g in Sample.get() if any((p.get("punt") or {}).get("outcome") == "retained"
                                                for p in g["possessions"])), None)
        self.assertIsNotNone(r)
        doctored = copy.deepcopy(r)
        row = next(x for x in doctored["play_ledger"] if x["play_type"] == "punt" and x["outcome"] == "retained")
        row["gross"] += 3
        self.assertTrue(any(e.startswith("kick_spot_mismatch") for e in check_ledger(doctored)))


# ---- records, views and bands --------------------------------------------------------------------

class RecordsTests(unittest.TestCase):
    def test_field_groups(self):
        # Batch B10's counters and summary slots, in place (batch B11 appends
        # after them).
        self.assertEqual(KERNEL_2014_6_TEAM_STAT_FIELDS[6:10], play_detail.BALL_SECURITY_TEAM_FIELDS)
        self.assertEqual(KERNEL_2014_6_PLAYER_FIELDS[8:10], play_detail.FUMBLE_COUNTERS)
        fields = play_detail.DRIVE_SUMMARY_FIELDS
        self.assertEqual(fields.index("fumbles"), fields.index("segments") + 1)
        kick_fields = play_detail.KICK_SUMMARY_FIELDS
        self.assertEqual(kick_fields.index("fumble"), kick_fields.index("return_yards") + 1)

    def test_profile_2014_5_carries_none(self):
        r = play("b10-old", profile=PROFILE_2014_5)
        self.assertNotIn("ball_security", r)
        self.assertFalse(fumble_rows(r))
        self.assertNotIn("muffs", next(iter(r["team_stats"].values())))

    def test_receipts_and_statbook(self):
        games = Sample.get()[:10]
        receipts = [make_receipt(r, week=5, matchup="B at A", detail="compact_stats") for r in games]
        for rc in receipts:
            self.assertEqual(rc["ball_security"]["model"], bs.MODEL)
            self.assertEqual(check_ledger(rc), [])
        book = aggregate_receipts([dict(rc, event_id="%s-%d" % (rc["event_id"], i)) for i, rc in enumerate(receipts)])
        team = book["teams"]["A"]["team_stats"]
        self.assertEqual(team["fumbles"], sum(r["team_stats"]["A"]["fumbles"] for r in games))
        self.assertEqual(team["muffs"], sum(r["team_stats"]["A"]["muffs"] for r in games))

    def test_gamebook_shows_own_recoveries(self):
        r = next(g for g in Sample.get() if any(l.get("fumbles_recovered_own") for s in g["team_stats"].values()
                                                for l in s["players"].values()))
        text = gamebook.render(receipt(r, "full"), "A")
        self.assertIn("OWN REC", text)
        self.assertIn("MUFFS", text)
        old = gamebook.render(make_receipt(play("b10-old-gb", profile=PROFILE_2014_5), week=5, matchup="B at A",
                                           detail="full"), "A")
        self.assertNotIn("OWN REC", old)


class BandTests(unittest.TestCase):
    def test_rows_and_centres(self):
        receipts = [dict(make_receipt(r, week=5, matchup="B at A", detail="compact_stats"),
                         possessions=r["possessions"]) for r in Sample.get()]
        team_games, rows = bands.audit_ball_security(receipts, cohort="2014.6")
        self.assertEqual(team_games, 120)
        by = {row[0]: row for row in rows}
        fumbles = MODEL.centres["fumbles_per_team_game"]
        self.assertAlmostEqual(by["fumbles per team-game (nflverse definition, less defensive fumbles after a "
                                  "turnover)"][2], fumbles["pooled"][0] / fumbles["pooled"][1])
        graded = [row for row in rows if "informational" not in row[0]]
        self.assertEqual(len(graded), 6)
        self.assertTrue(all(row[4] in ("WITHIN", "OUTSIDE", "INSUFFICIENT SAMPLE") for row in graded))
        self.assertTrue(all(row[4] in ("INFORMATIONAL", "INSUFFICIENT SAMPLE") for row in rows if row not in graded))
        self.assertEqual(by["lost fumbles per team-game"][4], "WITHIN")
        self.assertEqual(bands.audit_ball_security(receipts, cohort="2014.5"), (0, []))
        old = [make_receipt(play("b10-band-old", profile=B10_OFF), week=5, matchup="B at A")]
        self.assertEqual(bands.audit_ball_security(old, cohort="2014.6"), (0, []))

    def test_turnover_row_reads_the_categories(self):
        receipts = [dict(make_receipt(r, week=5, matchup="B at A", detail="compact_stats"),
                         possessions=r["possessions"]) for r in Sample.get()]
        _, rows = bands.audit_drive_model(receipts, cohort="2014.6")
        row = next(r for r in rows if r[0] == "offensive-drive turnovers per team game")
        categories = sum(p["category"] in ("interception", "fumble_lost") for r in Sample.get()
                         for p in r["possessions"])
        self.assertAlmostEqual(row[1], categories / 120)


if __name__ == "__main__":
    unittest.main()
