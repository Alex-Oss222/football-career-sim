"""Kernel 2014.6 plumbing (batch B1): frozen kernel profiles.

PROFILE_2014_5 is the isolation proof for every 2014.6 mechanism: under it
the 40 identity games and the 250-game synthetic sample reproduce the
digests recorded from the tree before B1 (tests/data/
result_identity_2014_5_profile.json), both the ResultIdentityTests projection
and the whole result. strip_2014_6_fields is the projection later batches
use to compare a 2014.6 result with its 2014.5 counterpart when no 2014.6
mechanism fired."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import copy
import dataclasses
import hashlib
import json
import unittest

from runtime import KERNEL_VERSION
from runtime.calibration_base import BASE_2012, CalibrationBaseError, base_for_kernel
from runtime.kernel import resolve_game, validate_result
from runtime.profiles import B10_FLAGS, PROFILE_2014_5, PROFILE_2014_6, PROFILES, Profile, profile_for
from runtime.statbook import (KERNEL_2014_6_FIELD_GROUP, KERNEL_2014_6_PLAYER_FIELDS,
                              KERNEL_2014_6_TEAM_STAT_FIELDS)
from synthetic_games import EVENT_PREFIX, SAMPLE_SIZE, SEED, sample_teams

FIXTURE = Path(__file__).parent / "data/result_identity_2014_5_profile.json"
FIXTURE_2014_6 = Path(__file__).parent / "data/result_identity_2014_6.json"


def projection_digest(r):
    out = {k: r[k] for k in ("final_score", "possessions", "kickoffs", "injuries", "opening_receiver")}
    out["team"] = {t: {k: v for k, v in s.items() if k != "players"} for t, s in r["team_stats"].items()}
    return hashlib.sha256(json.dumps(out, sort_keys=True, default=str).encode()).hexdigest()


def full_digest(r):
    return hashlib.sha256(json.dumps(r, sort_keys=True, default=str).encode()).hexdigest()


def strip_2014_6_fields(result):
    """A copy of a result or receipt without the kernel 2014.6 field group
    (runtime.statbook.KERNEL_2014_6_FIELD_GROUP: result-level, possession,
    snap-ledger, team and player fields) and without its kernel_version, so a
    2014.6 result in which no 2014.6 mechanism fired compares equal to its
    2014.5 counterpart."""
    group = KERNEL_2014_6_FIELD_GROUP
    out = copy.deepcopy(result)
    out.pop("kernel_version", None)
    for key in group["result"]:
        out.pop(key, None)
    for p in out.get("possessions", ()):
        for key in group["possession"]:
            p.pop(key, None)
        for key in group.get("fourth_down", ()):
            if isinstance(p.get("fourth_down"), dict):
                p["fourth_down"].pop(key, None)
        for key in group.get("punt", ()):
            if isinstance(p.get("punt"), dict):
                p["punt"].pop(key, None)
    from runtime.statbook import KERNEL_2014_6_LEDGER_ROWS
    out["play_ledger"] = [row for row in out.get("play_ledger", ())
                          if row.get("play_type") not in KERNEL_2014_6_LEDGER_ROWS]
    for row in out["play_ledger"]:
        for key in group["ledger"]:
            row.pop(key, None)
    for kick in out.get("kickoffs", ()):
        for key in group.get("kickoff", ()):
            kick.pop(key, None)
    for team in (out.get("team_stats") or {}).values():
        for key in group["team"]:
            team.pop(key, None)
        for line in (team.get("players") or {}).values():
            for key in group["player"]:
                line.pop(key, None)
    return out


class ProfileTableTests(unittest.TestCase):
    def test_registered_profiles(self):
        self.assertEqual(set(PROFILES), {"2014.5", "2014.6"})
        # Kernel 2014.6 release (B18): the live kernel's profile is 2014.6.
        self.assertIs(profile_for(KERNEL_VERSION), PROFILE_2014_6)
        self.assertEqual(KERNEL_VERSION, "2014.6")
        for version, profile in PROFILES.items():
            self.assertEqual(profile.kernel_version, version)
            self.assertEqual(profile.base, base_for_kernel(version))
        with self.assertRaises(ValueError):
            profile_for("2014.7")
        with self.assertRaises(ValueError):
            profile_for(None)
        self.assertEqual((PROFILE_2014_5.base, PROFILE_2014_5.cell_rules, PROFILE_2014_5.flags,
                          PROFILE_2014_5.record_base), ("2012", "2013.7", frozenset(), False))
        self.assertEqual((PROFILE_2014_6.base, PROFILE_2014_6.record_base), ("2010_2014w4", True))
        self.assertIs(PROFILE_2014_5.calibration_base(), BASE_2012)

    def test_profiles_are_frozen(self):
        with self.assertRaises(dataclasses.FrozenInstanceError):
            PROFILE_2014_5.base = "2010_2014w4"
        with self.assertRaises(TypeError):
            Profile("x", base="2012", cell_rules="2013.7", strength="honours-production-v3", flags={"a"})
        self.assertFalse(PROFILE_2014_5.has("base_2014_6"))
        # A profile whose cell rules differ from its base's fails closed.
        wrong = Profile("2014.5", base="2012", cell_rules="2014.6", strength="honours-production-v3")
        with self.assertRaises(ValueError):
            wrong.calibration_base()

    def test_profile_2014_6_binds_the_2010_2014_base(self):
        # Batch B5 registered the base; its schema flags must be the profile's.
        from runtime.calibration_base import BASE_2010_2014W4
        self.assertIs(PROFILE_2014_6.calibration_base(), BASE_2010_2014W4)
        self.assertEqual(PROFILE_2014_6.flags, frozenset({"base_2014_6", "regimes_v3", "injury_2014_6",
                                                          "usage_2014_6",
                                                          # batch B6 (W3, W5a, W2a)
                                                          "early_fg_v2", "clock_detail_v1", "substitution_record",
                                                          # batch B8 (possession sequencing)
                                                          "possession_sequencing",
                                                          # batch B9 (R8, R15, R9 scoring decisions)
                                                          "two_point_tries", "return_touchdowns",
                                                          "onside_kicks",
                                                          # batch B9F (live fourth downs)
                                                          "fourth_down_decisions",
                                                          # batch B10 (W4, R12 layers A, B and C)
                                                          "ball_security_credit", "fumble_terminal_kind",
                                                          "retained_kicks",
                                                          # batch B11 (R11 penalty records)
                                                          "penalty_records",
                                                          # batch B13 (R16a yard split, R16b snap values)
                                                          "yard_split", "snap_values",
                                                          # batch B15 (W2b DB seats, W2c pause eligibility)
                                                          "db_slots", "pause_eligibility",
                                                          # W1a (the defensive call record; records only)
                                                          "defensive_call_record"}))
        a, b = sample_teams()
        r = resolve_game(a, b, seed=SEED + b"-b5-2014-6", event_id="b5-2014-6", _test_profile=PROFILE_2014_6)
        self.assertEqual(r["kernel_version"], "2014.6")
        self.assertEqual(r["calibration_base"]["name"], "2010_2014w4")
        self.assertEqual(validate_result(r), [])
        # A profile without the base's schema flags, or holding them on the
        # 2012 base, fails closed before any draw.
        bare = Profile("2014.6", base="2010_2014w4", cell_rules="2014.6", strength="honours-production-v3")
        with self.assertRaises(ValueError):
            bare.calibration_base()
        with self.assertRaises(ValueError):
            resolve_game(a, b, seed=SEED + b"-b5-bare", event_id="b5-bare", _test_profile=bare)
        wrong = Profile("2014.5", base="2012", cell_rules="2013.7", strength="honours-production-v3",
                        flags=frozenset({"regimes_v3"}))
        with self.assertRaises(ValueError):
            wrong.calibration_base()
        with self.assertRaises(ValueError):
            Profile("2014.6", base="2012", cell_rules="2013.7", strength="honours-production-v3",
                    flags=frozenset({"no_such_flag"}))
        # Batch B9F: live fourth downs need possession_sequencing and
        # clock_detail_v1 (their records and the W5a decision clock).
        for flag in ("possession_sequencing", "clock_detail_v1"):
            with self.assertRaises(ValueError):
                Profile("2014.6", base="2010_2014w4", cell_rules="2014.6", strength=PROFILE_2014_6.strength,
                        flags=PROFILE_2014_6.flags - B10_FLAGS
                        - {flag, "two_point_tries", "return_touchdowns", "onside_kicks"})
        # Batch B9: a scoring flag needs possession_sequencing (FLAG_REQUIRES),
        # refused when the profile is constructed.
        for flag in ("two_point_tries", "return_touchdowns", "onside_kicks"):
            with self.assertRaises(ValueError):
                Profile("2014.6", base="2010_2014w4", cell_rules="2014.6", strength=PROFILE_2014_6.strength,
                        flags=PROFILE_2014_6.flags - B10_FLAGS - {"possession_sequencing", "fourth_down_decisions"} - (
                            {"two_point_tries", "return_touchdowns", "onside_kicks"} - {flag}))
        # Batch B10: layers B and C need the credit layer, and layer C
        # (retained kicks) possession_sequencing; the credit layer alone
        # needs nothing.
        for removed in ({"ball_security_credit"}, {"ball_security_credit", "fumble_terminal_kind"},
                        {"ball_security_credit", "retained_kicks"}, {"possession_sequencing"}):
            with self.assertRaises(ValueError):
                Profile("2014.6", base="2010_2014w4", cell_rules="2014.6", strength=PROFILE_2014_6.strength,
                        flags=PROFILE_2014_6.flags - removed - {"two_point_tries", "return_touchdowns",
                                                                "onside_kicks", "fourth_down_decisions"})
        Profile("2014.6", base="2010_2014w4", cell_rules="2014.6", strength=PROFILE_2014_6.strength,
                flags=PROFILE_2014_6.flags - B10_FLAGS | {"ball_security_credit"})
        # Batch B15: the pause eligibility (W2c) needs the DB seats (W2b) and
        # the substitution record (W2a, its default entrant and moves); the
        # seats alone need nothing.
        for removed in ({"db_slots"}, {"substitution_record"}):
            with self.assertRaises(ValueError):
                Profile("2014.6", base="2010_2014w4", cell_rules="2014.6", strength=PROFILE_2014_6.strength,
                        flags=PROFILE_2014_6.flags - removed)
        Profile("2014.6", base="2010_2014w4", cell_rules="2014.6", strength=PROFILE_2014_6.strength,
                flags=PROFILE_2014_6.flags - {"pause_eligibility", "substitution_record"})

    def test_only_a_profile_is_accepted(self):
        a, b = sample_teams()
        with self.assertRaises(TypeError):
            resolve_game(a, b, seed=SEED + b"-b1-type", event_id="b1-type", _test_profile="2014.5")


class Profile2014_5IdentityTests(unittest.TestCase):
    """PROFILE_2014_5 reproduces the 40 identity digests and the 250-game
    sample, projection and whole result, as recorded before B1."""

    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(FIXTURE.read_text())

    def test_identity_games(self):
        a, b = sample_teams()
        recorded = {(row["game_type"], row["index"]): row["digest"]
                    for row in json.loads((FIXTURE.parent / "result_identity.json").read_text())["games"]}
        self.assertEqual(len(self.fixture["identity"]), 40)
        for row in self.fixture["identity"]:
            game_type, i = row["game_type"], row["index"]
            seed = hashlib.sha256(("identity-%s-%d" % (game_type, i)).encode()).digest()
            r = resolve_game(a, b, seed=seed, event_id="identity-%s-%d" % (game_type, i),
                             venue="neutral" if i % 5 == 0 else "home", game_type=game_type,
                             _test_profile=PROFILE_2014_5)
            self.assertEqual(projection_digest(r), recorded[(game_type, i)], "%s %d" % (game_type, i))
            self.assertEqual(projection_digest(r), row["digest"])
            self.assertEqual(full_digest(r), row["full_digest"], "%s %d" % (game_type, i))
            self.assertEqual(r["kernel_version"], "2014.5")
            self.assertNotIn("calibration_base", r)

    def test_sample_games(self):
        a, b = sample_teams()
        self.assertEqual(len(self.fixture["sample"]), SAMPLE_SIZE)
        for row in self.fixture["sample"]:
            i = row["index"]
            r = resolve_game(a, b, seed=SEED + b"-%05d" % i, event_id=f"{EVENT_PREFIX}-{i}",
                             _test_profile=PROFILE_2014_5)
            self.assertEqual(projection_digest(r), row["digest"], "sample game %d" % i)
            self.assertEqual(full_digest(r), row["full_digest"], "sample game %d" % i)


def identity_game(a, b, game_type, i, profile=None):
    """One of the 40 identity games by tests/data/result_identity.json's seed
    rule; ``profile`` None resolves on the profile of KERNEL_VERSION."""
    seed = hashlib.sha256(("identity-%s-%d" % (game_type, i)).encode()).digest()
    extra = {} if profile is None else {"_test_profile": profile}
    return resolve_game(a, b, seed=seed, event_id="identity-%s-%d" % (game_type, i),
                        venue="neutral" if i % 5 == 0 else "home", game_type=game_type, **extra)


IDENTITY_2014_6_NOTE = (
    "Result digests of the 40 synthetic identity games under kernel 2014.6 (PROFILE_2014_6), recorded on "
    "October 16, 2026 at the kernel 2014.6 release (plan batch B18) by `PYTHONPATH=. python tests/test_profiles.py "
    "--record-2014-6`, before the version flip, and re-recorded on October 17, 2026 after the release decisions "
    "(the pooled aging curve applied once), with every digest unchanged. The fixture clubs "
    "(tests/synthetic_games.py sample_teams()) carry no strength record, so no player state is read and no "
    "private draw is requested. 'digest' is the tests/test_attribution.py ResultIdentityTests projection "
    "(final score, possessions, kickoffs, injuries, opening receiver, team counters); 'full_digest' is the "
    "sha256 of the whole result (json.dumps with sort_keys, default=str). A credit-only or display-only "
    "change to kernel 2014.6 must reproduce this file; a later kernel that deliberately changes results "
    "records its own file and leaves this one asserted under PROFILE_2014_6, as "
    "result_identity_2014_5_profile.json stays asserted under PROFILE_2014_5.")


def record_2014_6_identity():
    """The tests/data/result_identity_2014_6.json record, computed from the tree."""
    a, b = sample_teams()
    rows = []
    for row in json.loads((FIXTURE.parent / "result_identity.json").read_text())["games"]:
        game_type, i = row["game_type"], row["index"]
        r = identity_game(a, b, game_type, i, PROFILE_2014_6)
        rows.append({"digest": projection_digest(r), "full_digest": full_digest(r), "game_type": game_type,
                     "index": i, "final_score": r["final_score"]})
    return {"kernel": "2014.6", "profile": "runtime.profiles.PROFILE_2014_6", "note": IDENTITY_2014_6_NOTE,
            "identity_rule": "tests/data/result_identity.json seed_rule (40 games)", "identity": rows}


def format_2014_6_identity(record):
    """The fixture's text: header keys, then one identity row per line."""
    head = {k: v for k, v in record.items() if k != "identity"}
    lines = ["{"] + ["  %s: %s," % (json.dumps(k), json.dumps(v)) for k, v in head.items()]
    lines.append('  "identity": [')
    lines += ["    %s%s" % (json.dumps(row, sort_keys=True), "," if n < len(record["identity"]) - 1 else "")
              for n, row in enumerate(record["identity"])]
    lines += ["  ]", "}"]
    return "\n".join(lines) + "\n"


class Profile2014_6IdentityTests(unittest.TestCase):
    """Kernel 2014.6 release (batch B18): PROFILE_2014_6 reproduces the 40
    identity digests recorded at the release, projection and whole result,
    and the profile of KERNEL_VERSION is that profile."""

    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(FIXTURE_2014_6.read_text())

    def test_identity_games(self):
        self.assertEqual((self.fixture["kernel"], self.fixture["profile"]),
                         ("2014.6", "runtime.profiles.PROFILE_2014_6"))
        self.assertEqual(len(self.fixture["identity"]), 40)
        seeds = {(row["game_type"], row["index"])
                 for row in json.loads((FIXTURE.parent / "result_identity.json").read_text())["games"]}
        self.assertEqual({(row["game_type"], row["index"]) for row in self.fixture["identity"]}, seeds)
        a, b = sample_teams()
        for row in self.fixture["identity"]:
            game_type, i = row["game_type"], row["index"]
            r = identity_game(a, b, game_type, i, PROFILE_2014_6)
            self.assertEqual(r["kernel_version"], "2014.6")
            self.assertEqual(r["calibration_base"]["name"], "2010_2014w4")
            self.assertEqual(validate_result(r), [], "%s %d" % (game_type, i))
            self.assertEqual(r["final_score"], row["final_score"], "%s %d" % (game_type, i))
            self.assertEqual(projection_digest(r), row["digest"], "%s %d" % (game_type, i))
            self.assertEqual(full_digest(r), row["full_digest"], "%s %d" % (game_type, i))

    def test_default_profile_is_the_live_kernel(self):
        # No _test_profile is the profile of KERNEL_VERSION: the same result.
        self.assertIs(profile_for(KERNEL_VERSION), PROFILE_2014_6)
        a, b = sample_teams()
        for row in (self.fixture["identity"][0], self.fixture["identity"][-1]):
            r = identity_game(a, b, row["game_type"], row["index"])
            self.assertEqual(full_digest(r), row["full_digest"])

    def test_the_fixture_is_the_recorder_output(self):
        # The committed file is the recorder's text for its own record
        # (format included); test_identity_games proves the record is this
        # tree's results, so no digest was typed by hand.
        self.assertEqual(format_2014_6_identity(self.fixture), FIXTURE_2014_6.read_text(encoding="utf-8"))
        self.assertEqual(self.fixture["note"], IDENTITY_2014_6_NOTE)


class ReleasePinTests(unittest.TestCase):
    """Kernel 2014.6 release (B18): runtime/season_readiness.json accepts the
    installed kernel and pins its calibration base, and the checkout holds
    every pin of that base."""

    def test_season_readiness_pins_the_live_base(self):
        from runtime.calibration_base import get_base, record
        data = json.loads((Path(__file__).resolve().parents[1] / "runtime/season_readiness.json").read_text())
        release = data["seasons"]["2014"]
        self.assertEqual(release["accepted_kernel"], KERNEL_VERSION)
        base = get_base(base_for_kernel(release["accepted_kernel"]))
        self.assertEqual(release["calibration_base"], record(base))
        self.assertEqual(base.verify(), [])


class StripFieldGroupTests(unittest.TestCase):
    def test_field_group_is_registered_with_each_batch(self):
        # Batch B6 appended the fourth-down marker group and the W2a and W5a
        # fields; batch B8 the kick-record group, the kicks summary, the
        # scoring events and the possession's non-offensive score; batch B9
        # (R8, R9, R15) the frozen decision blocks, the offensive try record,
        # the onside decision fields, the try-row and onside ledger fields,
        # and its team and player counters; batch B9F the possession's
        # fourth-down records and segments and the ledger's decision mark;
        # batch B10 (W4, R12) the ball-security marker, the possession's
        # credited fumbles, the kick's and the punt summary's fumble, the
        # ledger's fumble record, muffer and own recovery yards, and its team
        # and player counters.
        self.assertEqual(set(KERNEL_2014_6_FIELD_GROUP),
                         {"result", "possession", "ledger", "team", "player", "fourth_down", "kickoff", "punt"})
        self.assertEqual(KERNEL_2014_6_FIELD_GROUP["result"],
                         ("calibration_base", "substitutions", "kicks", "scoring_events", "decision_policies",
                          "ball_security", "penalties", "yardage"))
        self.assertEqual(KERNEL_2014_6_FIELD_GROUP["possession"],
                         ("last_spike_seconds_left", "non_offensive_score", "try", "fourth_downs", "segments",
                          "fumbles", "pen", "real_split"))
        self.assertEqual(KERNEL_2014_6_FIELD_GROUP["kickoff"],
                         ("remaining", "chain", "after_drive", "basis", "touchdown", "scoring_team", "xp_made", "points",
                          "onside", "cell", "p_onside", "recovery_class", "p_recover", "try", "fumble", "pen"))
        self.assertEqual(KERNEL_2014_6_FIELD_GROUP["ledger"],
                         ("decision_source", "anchor", "scoring_team", "decision", "basis", "cell", "p_go", "points",
                          "onside", "recovered_by", "blocked", "scorer", "attribution", "fourth_down_decision",
                          "fumble", "muffed_by", "own_recovery_yards", "penalties", "penalty_enforcement",
                          "penalty_yards", "untimed"))
        self.assertEqual(KERNEL_2014_6_FIELD_GROUP["punt"], ("fumble", "pen"))
        self.assertEqual(KERNEL_2014_6_TEAM_STAT_FIELDS,
                         ("two_point_attempts", "two_point_conversions", "defensive_touchdowns",
                          "special_teams_touchdowns", "onside_kicks", "onside_recoveries",
                          "fumbles", "fumbles_lost", "muffs", "kicking_team_recoveries",
                          "penalties_declined", "penalties_offsetting", "penalty_first_downs"))
        self.assertEqual(KERNEL_2014_6_PLAYER_FIELDS,
                         ("passing_two_point_conversions", "receiving_two_point_conversions",
                          "rushing_two_point_conversions", "interception_return_touchdowns",
                          "fumble_return_touchdowns", "punt_return_touchdowns", "kick_return_touchdowns",
                          "blocked_kick_touchdowns", "muffs", "fumbles_recovered_own", "penalties", "penalty_yards"))
        self.assertEqual(KERNEL_2014_6_FIELD_GROUP["fourth_down"], ("decision_source",))
        self.assertEqual(KERNEL_2014_6_FIELD_GROUP["team"], KERNEL_2014_6_TEAM_STAT_FIELDS)
        self.assertEqual(KERNEL_2014_6_FIELD_GROUP["player"], KERNEL_2014_6_PLAYER_FIELDS)

    def test_a_2014_6_marker_adds_only_the_field_group(self):
        # A 2014.6-marked profile on the 2012 base with no mechanism flag:
        # the result differs from 2014.5 only by its kernel version and the
        # recorded calibration base, which strip_2014_6_fields removes.
        marked = Profile("2014.6", base=BASE_2012, cell_rules="2013.7", strength="honours-production-v3",
                         record_base=True)
        a, b = sample_teams()
        for i in range(3):
            seed = SEED + b"-%05d" % i
            plain = resolve_game(a, b, seed=seed, event_id=f"{EVENT_PREFIX}-{i}", _test_profile=PROFILE_2014_5)
            r = resolve_game(a, b, seed=seed, event_id=f"{EVENT_PREFIX}-{i}", _test_profile=marked)
            self.assertEqual(r["kernel_version"], "2014.6")
            self.assertEqual(r["calibration_base"], {"name": "2012", "manifest_sha256": BASE_2012.manifest_sha256(),
                                                     "cell_rules": "2013.7"})
            self.assertNotEqual(r, plain)
            self.assertEqual(strip_2014_6_fields(r), strip_2014_6_fields(plain))
            self.assertEqual(validate_result(r, base=BASE_2012), [])


if __name__ == "__main__":
    if sys.argv[1:] == ["--record-2014-6"]:
        # Kernel 2014.6 release (B18): write tests/data/result_identity_2014_6.json.
        FIXTURE_2014_6.write_text(format_2014_6_identity(record_2014_6_identity()), encoding="utf-8")
    else:
        unittest.main()
