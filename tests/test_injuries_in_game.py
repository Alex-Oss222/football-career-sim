"""Kernel 2014.4: in-game injury onset, removal, replacement and the E2 pause.

Tier 1 items 4 and 5 of runtime/defect_register.md and the E2 acceptance
gates of runtime/2014_engine_decisions.md. Onsets are forced through the
kernel's test-only ``_test_onsets`` hook, which the production runner cannot
pass. Synthetic seeds only; the private service used here is a local test
instance.
"""
import copy
import inspect
import json
import random
import sys
import tempfile
import threading
import unittest
from dataclasses import replace
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import injury_model, participation, usage
from runtime.game_runner import run_game
from runtime.kernel import TeamInput, resolve_game, validate_result
from runtime.private_client import Client
from runtime.private_service import Store, handler
from support_rosters import game_day_roster
from synthetic_games import SEED, sample, sample_teams

GAME_SEED = SEED + b"-injury-00011"
EVENT = "injury-11"
PARTICIPANT_FIELDS = ("passer", "runner", "target", "blocker", "tackler", "assist_tackler",
                      "kicker", "punter", "returner", "cover_player", "long_snapper")


def force(drive, player, **spec):
    base = {"injury_class": "lower_extremity", "severity": "multi_week", "removed": True}
    base.update(spec)
    return {(drive, player): base}


def named_after(result, player, drive):
    return [row for row in result["play_ledger"] if row.get("drive", 0) > drive
            and player in {row.get(f) for f in PARTICIPANT_FIELDS}]


def drives_of(result, team):
    return [p["number"] for p in result["possessions"] if p["team"] == team]


def scrimmage_rows(result, team, through):
    return [r for r in result["play_ledger"] if r.get("offense") == team
            and r.get("play_type") in ("pass", "run") and r["drive"] <= through]


def settled(possessions, pause_drive):
    """Possessions through a pause; the pause drive's kickoff_after and
    next_start are filled only by the next event (the kick after a score)."""
    return [{k: v for k, v in p.items() if p["number"] < pause_drive or k not in ("kickoff_after", "next_start")}
            for p in possessions if p["number"] <= pause_drive]


def team_with(team, **changes):
    roster = tuple(changes.pop("roster", team.roster))
    active = changes.pop("active", tuple(p.player_id for p in roster))
    return TeamInput(team.team_id, tuple(active), roster=roster,
                     offensive_call_sheet=team.offensive_call_sheet, **changes)


class InGameRemovalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a, cls.b = sample_teams()
        cls.base = resolve_game(cls.a, cls.b, seed=GAME_SEED, event_id=EVENT)
        cls.a_drive = drives_of(cls.base, "A")[0]

    def game(self, onsets, a=None, b=None, **kwargs):
        return resolve_game(a or self.a, b or self.b, seed=GAME_SEED, event_id=EVENT,
                            _test_onsets=onsets, **kwargs)

    def test_hook_is_unreachable_from_the_production_runner(self):
        self.assertNotIn("_test_onsets", inspect.signature(run_game).parameters)
        self.assertNotIn("_test_onsets", inspect.getsource(run_game))

    def test_forced_onset_removes_the_player_on_both_sides(self):
        d = self.a_drive
        onsets = {**force(d, "A-WR1"), **force(d, "B-CB1")}
        result = self.game(onsets)
        self.assertEqual(validate_result(result), [])
        hurt = {(i["team"], i["player"]): i for i in result["injuries"]}
        for key in (("A", "A-WR1"), ("B", "B-CB1")):
            self.assertTrue(hurt[key]["removed"])
            self.assertEqual((hurt[key]["drive"], hurt[key]["onset"]), (d, "end_of_drive"))
        self.assertEqual(named_after(result, "A-WR1", d), [])
        self.assertEqual(named_after(result, "B-CB1", d), [])
        # Both are every-snap players: their snaps stop exactly at the onset drive.
        a_snaps = len(scrimmage_rows(result, "A", d))
        self.assertEqual(result["team_stats"]["A"]["players"]["A-WR1"]["offensive_snaps"], a_snaps)
        self.assertEqual(result["team_stats"]["B"]["players"]["B-CB1"]["defensive_snaps"], a_snaps)
        self.assertGreater(result["team_stats"]["A"]["players"]["A-WR1"]["offensive_snaps"], 0)
        subs = {(s["team"], s["removed"]): s for s in result["substitutions"]}
        self.assertEqual(subs[("A", "A-WR1")]["basis"], "depth_order")
        # The prefix (everything through the onset drive) is the unforced game's.
        self.assertEqual([p for p in result["possessions"] if p["number"] <= d],
                         [p for p in self.base["possessions"] if p["number"] <= d])
        self.assertEqual(result["final_score"], self.base["final_score"])

    def test_qb1_removal_backup_passes_and_lines_reconcile(self):
        d = self.a_drive
        result = self.game(force(d, "A-QB1"))
        self.assertEqual(validate_result(result), [])
        passers = [p["passer"] for p in result["possessions"] if p["team"] == "A"]
        self.assertEqual(passers[0], "A-QB1")
        self.assertEqual(set(passers[1:]), {"A-QB2"})
        players = result["team_stats"]["A"]["players"]
        self.assertGreater(players["A-QB2"]["pass_attempts"], 0)
        rows = [r for r in result["play_ledger"] if r.get("offense") == "A" and r.get("play_type") == "pass"]
        for qb in ("A-QB1", "A-QB2"):
            attempts = sum(1 for r in rows if r["passer"] == qb and not r["sack"])
            yards = sum(r["passing_yards"] for r in rows if r["passer"] == qb)
            self.assertEqual((players[qb]["pass_attempts"], players[qb]["passing_yards"]), (attempts, yards))
        self.assertEqual(sum(p["passing_yards"] for p in players.values()), result["team_stats"]["A"]["passing_yards"])
        self.assertTrue(all(r["passer"] == "A-QB1" for r in rows if r["drive"] <= d))
        self.assertEqual(named_after(result, "A-QB1", d), [])

    def test_validator_rejects_participation_after_removal(self):
        d = self.a_drive
        result = self.game(force(d, "A-QB1"))
        tampered = copy.deepcopy(result)
        row = next(r for r in tampered["play_ledger"] if r.get("passer") == "A-QB2")
        row["passer"] = "A-QB1"
        self.assertIn("removed player participates after his removal", validate_result(tampered))
        tampered = copy.deepcopy(self.base)
        later = [p for p in tampered["possessions"] if p["team"] == "A"][1]
        later["passer"] = "A-QB2"
        self.assertIn("passer change without a removal", validate_result(tampered))

    def test_offensive_line_replacement(self):
        d = self.a_drive
        result = self.game(force(d, "A-OT1"))
        self.assertEqual(validate_result(result), [])
        self.assertEqual(named_after(result, "A-OT1", d), [])
        sub = next(s for s in result["substitutions"] if s["removed"] == "A-OT1")
        entering = result["team_stats"]["A"]["players"][sub["replacement"]]
        self.assertEqual(entering["line_starts"], 0)
        self.assertGreater(entering["offensive_snaps"], 0)
        self.assertEqual(sum(p["line_starts"] for p in result["team_stats"]["A"]["players"].values()), 5)

    def test_returner_replacement(self):
        receiver = self.base["opening_receiver"]
        returner = usage.club_returner(self.a.roster if receiver == "A" else self.b.roster, "kick_return")
        first = self.base["kickoffs"][0]
        self.assertEqual(first["drive"], 1)
        result = self.game(force(1, returner.player_id))
        self.assertEqual(validate_result(result), [])
        self.assertEqual(named_after(result, returner.player_id, 1), [])
        later = {r["returner"] for r in result["play_ledger"] if r.get("returner") and r["defense"] == receiver
                 and r["drive"] > 1}
        self.assertTrue(later)
        self.assertNotIn(returner.player_id, later)

    def test_specialist_replacements(self):
        kick = next(k for k in self.base["kickoffs"] if k["kicking"] == "A")
        result = self.game(force(kick["drive"], "A-K1"))
        self.assertEqual(validate_result(result), [])
        later = [r for r in result["play_ledger"] if r.get("kicker") and r["offense"] == "A"
                 and r["drive"] > kick["drive"]]
        self.assertTrue(later)
        self.assertEqual({r["kicker"] for r in later}, {"A-P1"})  # the punter kicks
        snap_drive = next(r["drive"] for r in self.base["play_ledger"]
                          if r.get("long_snapper") == "A-LS1")
        result = self.game(force(snap_drive, "A-LS1"))
        self.assertEqual(validate_result(result), [])
        later = [r for r in result["play_ledger"] if r.get("long_snapper") and r["offense"] == "A"
                 and r["drive"] > snap_drive]
        self.assertTrue(later)
        self.assertEqual({r["long_snapper"] for r in later}, {"A-C1"})  # the center snaps

    def test_minor_injury_stays_in_the_game(self):
        d = self.a_drive
        result = self.game(force(d, "A-WR1", severity="minor", removed=False))
        self.assertEqual(validate_result(result), [])
        entry = next(i for i in result["injuries"] if i["player"] == "A-WR1")
        self.assertFalse(entry["removed"])
        for field in ("team", "player", "injury_class", "severity", "restriction", "return_days",
                      "reassessment_days", "drive", "clock", "removed"):
            self.assertIn(field, entry)
        self.assertTrue(named_after(result, "A-WR1", d))

    def test_head_neck_is_always_an_independent_hold(self):
        result = self.game(force(self.a_drive, "A-WR1", injury_class="head_neck", severity="minor", removed=False))
        entry = next(i for i in result["injuries"] if i["player"] == "A-WR1")
        self.assertEqual((entry["restriction"], entry["removed"]), (injury_model.HOLD, True))

    def test_forced_onset_requires_participation(self):
        with self.assertRaisesRegex(ValueError, "no exposure"):
            self.game(force(self.a_drive, "A-QB2"))

    def test_exhausted_depth(self):
        # No second quarterback dressed: an emergency passer (next spare back)
        # takes over, recorded on every later drive.
        active = tuple(p.player_id for p in self.a.roster if p.player_id != "A-QB2")
        a = team_with(self.a, active=active)
        base = resolve_game(a, self.b, seed=GAME_SEED, event_id=EVENT)
        d = drives_of(base, "A")[0]
        result = resolve_game(a, self.b, seed=GAME_SEED, event_id=EVENT, _test_onsets=force(d, "A-QB1"))
        self.assertEqual(validate_result(result), [])
        later = [p for p in result["possessions"] if p["team"] == "A" and p["number"] > d]
        self.assertTrue(later)
        self.assertEqual({p["passer"] for p in later}, {"A-RB2"})
        self.assertTrue(all(any(n["group"] == "QB" and n["filled_by"] == "A-RB2" for n in p["emergency"])
                            for p in later))
        self.assertNotIn("A-QB2", result["team_stats"]["A"]["players"])
        # Fewer than eleven available: no legal personnel solution, stop.
        # WR:p4 covers or blocks on the opening kickoff whichever club kicks.
        thin = TeamInput("A", tuple("WR:p%d" % i for i in range(11)))
        with self.assertRaises(participation.NoLegalPersonnel):
            resolve_game(thin, self.b, seed=GAME_SEED, event_id=EVENT, _test_onsets=force(1, "WR:p4"))


class PauseAndContinuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        a, cls.b = sample_teams()
        # A featured receiver (TeamInput rotation plan) and an inactive spare.
        spare = replace(a.roster[0], player_id="A-WR9", position="WR", depth=9)
        roster = a.roster + (spare,)
        cls.a = team_with(a, roster=roster, active=tuple(p.player_id for p in a.roster),
                          rotation_plan=({"player_id": "A-WR1", "featured": True},))
        base = resolve_game(cls.a, cls.b, seed=GAME_SEED, event_id=EVENT)
        cls.d = drives_of(base, "A")[0]
        cls.onsets = {**force(cls.d, "A-QB1"), **force(cls.d, "A-WR1")}
        cls.partial = cls.play(cls.onsets)

    @classmethod
    def play(cls, onsets, decisions=None):
        return resolve_game(cls.a, cls.b, seed=GAME_SEED, event_id=EVENT, management_mode="user_controlled",
                            controlled_team="A", _test_onsets=onsets,
                            continuation=None if decisions is None else {"decisions": decisions})

    def decision(self, choices, token=None):
        return {"token": token or self.partial["pauses"][-1]["continuation_token"], "choices": choices}

    def prefix(self, result):
        return (settled(result["possessions"], self.d),
                [r for r in result["play_ledger"] if r["drive"] <= self.d],
                [i for i in result["injuries"] if i["drive"] <= self.d])

    def test_pause_is_partial_with_no_future_events(self):
        partial = self.partial
        self.assertFalse(partial["terminated"])
        for key in ("final_score", "team_stats", "player_evidence", "play_call_stats", "diagnostics"):
            self.assertNotIn(key, partial)
        self.assertTrue(all(p["number"] <= self.d for p in partial["possessions"]))
        self.assertEqual(partial["possessions"][-1]["number"], self.d)
        self.assertTrue(all(r["drive"] <= self.d for r in partial["play_ledger"]))
        self.assertTrue(all(k["drive"] <= self.d for k in partial["kickoffs"]))
        self.assertTrue(all(i["drive"] <= self.d for i in partial["injuries"]))
        pause = partial["pauses"][-1]
        slots = {d["slot"]: d for d in pause["decisions"]}
        self.assertEqual(slots["A-QB1"]["reason"], "quarterback")
        self.assertEqual(slots["A-QB1"]["eligible"], ["A-QB2"])
        self.assertEqual(slots["A-WR1"]["reason"], "featured_role")
        self.assertEqual(slots["A-WR1"]["eligible"], ["A-WR2", "A-WR3", "A-WR4", "A-WR5"])
        self.assertIn("A-QB1", pause["availability"]["A"]["removed"])
        self.assertNotIn("A-WR9", json.dumps(pause["decisions"]))

    def test_resume_reproduces_and_a_different_choice_keeps_the_prefix(self):
        one = self.play(self.onsets, [self.decision({"A-QB1": "A-QB2", "A-WR1": "A-WR2"})])
        again = self.play(self.onsets, [self.decision({"A-QB1": "A-QB2", "A-WR1": "A-WR2"})])
        other = self.play(self.onsets, [self.decision({"A-QB1": "A-QB2", "A-WR1": "A-WR5"})])
        for result in (one, other):
            self.assertTrue(result["terminated"])
            self.assertEqual(validate_result(result), [])
            self.assertEqual(self.prefix(result), self.prefix(self.partial))
        self.assertEqual(one, again)
        self.assertNotEqual(one["play_ledger"], other["play_ledger"])
        wr5 = lambda r: r["team_stats"]["A"]["players"]["A-WR5"]["offensive_snaps"]
        self.assertGreater(wr5(other), wr5(one))
        self.assertEqual(one["final_score"], other["final_score"])  # E1 not yet built: attribution only
        self.assertEqual(other["pauses"][0]["choices"]["A-WR1"], "A-WR5")
        sub = next(s for s in other["substitutions"] if s["removed"] == "A-WR1")
        self.assertEqual((sub["basis"], sub["replacement"]), ("coach_choice", "A-WR5"))

    def test_rejects_invalid_continuations(self):
        good = {"A-QB1": "A-QB2", "A-WR1": "A-WR2"}
        bad_choices = (
            {"A-QB1": "A-QB2", "A-WR1": "A-WR9"},   # inactive
            {"A-QB1": "A-QB2", "A-WR1": "Z-WR1"},   # absent
            {"A-QB1": "A-QB1", "A-WR1": "A-WR2"},   # held (the removed player)
            {"A-QB1": "A-QB2", "A-WR1": "A-QB2"},   # duplicate personnel
            {"A-QB1": "A-QB2"},                     # a pending choice missing
        )
        for choices in bad_choices:
            with self.assertRaises(ValueError, msg=choices):
                self.play(self.onsets, [self.decision(choices)])
        tampered = self.partial["pauses"][-1]["continuation_token"][:-1] + "0"
        with self.assertRaisesRegex(ValueError, "stale or tampered"):
            self.play(self.onsets, [self.decision(good, tampered)])
        # A decision that answers a different partial state is stale.
        other = self.play(force(self.d, "A-QB1"))
        with self.assertRaisesRegex(ValueError, "stale or tampered"):
            self.play(self.onsets, [self.decision(good, other["pauses"][-1]["continuation_token"])])
        with self.assertRaisesRegex(ValueError, "never reached"):
            self.play(self.onsets, [self.decision(good), self.decision(good)])

    def test_newly_injured_replacement_is_rejected(self):
        onsets = {**self.onsets, **force(self.d, "A-WR2")}
        partial = self.play(onsets)
        slots = {d["slot"]: d for d in partial["pauses"][-1]["decisions"]}
        self.assertNotIn("A-WR2", slots["A-WR1"]["eligible"])
        token = partial["pauses"][-1]["continuation_token"]
        with self.assertRaises(ValueError):
            self.play(onsets, [{"token": token, "choices": {"A-QB1": "A-QB2", "A-WR1": "A-WR2"}}])

    def test_autonomous_mode_uses_depth_order_without_pausing(self):
        result = resolve_game(self.a, self.b, seed=GAME_SEED, event_id=EVENT, _test_onsets=self.onsets)
        self.assertTrue(result["terminated"])
        self.assertEqual(result["pauses"], [])
        self.assertEqual(self.prefix(result), self.prefix(self.partial))

    def test_opponent_removal_never_pauses_the_controlled_club(self):
        onsets = force(self.d, "B-CB1")
        result = self.play(onsets)
        self.assertTrue(result["terminated"])


class ModelTests(unittest.TestCase):
    def test_calibration_file_validates(self):
        self.assertEqual(injury_model.validate(), [])
        broken = copy.deepcopy(injury_model.load())
        broken["recommended"]["class_mix_game_onsets"]["values"]["head_neck"] = 0.25
        self.assertTrue(injury_model.validate(broken))

    def test_position_aliases_and_risk_order(self):
        for alias, grp in (("OT", "OL"), ("OG", "OL"), ("C", "OL"), ("T", "OL"), ("DE", "DL"), ("DT", "DL"),
                           ("NT", "DL"), ("CB", "DB"), ("S", "DB"), ("FS", "DB"), ("SS", "DB"),
                           ("OLB", "LB"), ("ILB", "LB"), ("MLB", "LB"), ("FB", "RB"), ("HB", "RB"),
                           ("K", "K/P/LS"), ("P", "K/P/LS"), ("LS", "K/P/LS")):
            self.assertEqual(injury_model.risk_group(alias), grp, alias)
        risk = lambda pos: injury_model.onset_probability(pos, 1)
        self.assertEqual(risk("OT"), risk("OL"))
        self.assertEqual(risk("CB"), risk("DB"))
        for high in ("RB", "LB", "DB", "WR"):
            for low in ("OL", "QB", "DL"):
                self.assertGreater(risk(high), risk(low))
        self.assertTrue(all(risk("K") < risk(pos) for pos in ("QB", "OL", "DL", "TE")))

    def test_zero_participation_creates_no_injury(self):
        self.assertEqual(injury_model.onset_probability("RB", 0), 0.0)
        self.assertTrue(all(injury_model.draw(random.Random(i), "RB", 0) is None for i in range(2000)))
        for result in sample():
            removed = {i["player"]: i["drive"] for i in result["injuries"] if i["removed"]}
            for injury in result["injuries"]:
                self.assertGreater(injury["snaps_in_interval"], 0)
                line = result["team_stats"][injury["team"]]["players"][injury["player"]]
                self.assertGreater(line["offensive_snaps"] + line["defensive_snaps"] + line["special_teams_snaps"], 0)
            if "A-QB1" not in removed:
                self.assertNotIn("A-QB2", {i["player"] for i in result["injuries"]})

    def test_sample_within_calibration_bands(self):
        bands = injury_model.load()["recommended"]["acceptance_bands_for_kernel_2014_4"]
        games = sample()
        team_games = 2 * len(games)
        injuries = [i for r in games for i in r["injuries"]]
        n = len(injuries)
        share = lambda pred: sum(1 for i in injuries if pred(i)) / n
        observed = {
            "game_onsets_per_team_game": n / team_games,
            "rest_of_game_removals_per_team_game": sum(i["removed"] for i in injuries) / team_games,
            "head_neck_share_game_onsets": share(lambda i: i["injury_class"] == "head_neck"),
            "head_neck_game_onsets_per_team_game":
                sum(i["injury_class"] == "head_neck" for i in injuries) / team_games,
            "lower_extremity_share_game_onsets": share(lambda i: i["injury_class"] == "lower_extremity"),
            "time_loss_share_(short+)": share(lambda i: i["severity"] != "minor"),
            "long_term_share": share(lambda i: i["severity"] == "long_term"),
        }
        report = []
        for key, value in observed.items():
            low, high = bands[key]
            report.append("%s %.3f [%s, %s]" % (key, value, low, high))
            self.assertTrue(low <= value <= high, report[-1])
        print("\n[2014.4 sample, %d team-games] " % team_games + "; ".join(report))


class ProductionRunnerPauseTests(unittest.TestCase):
    """A natural pause and resume through run_game and the private closure."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        store = Store(Path(self.tmp.name) / "state.sqlite3"); store.initialize("snapshot")
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler(store, "test-only-token", "snapshot"))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close); self.addCleanup(server.shutdown)
        self.client = Client(f"http://127.0.0.1:{server.server_port}", token="test-only-token", snapshot="snapshot")

    def test_run_game_pauses_and_resumes(self):
        roster = tuple(p for p in game_day_roster("A") if p.player_id != "A-WR5")
        featured = ("A-QB1", "A-RB1", "A-WR1", "A-WR2", "A-TE1", "A-CB1", "A-S1", "A-OLB1", "A-DE1")
        home = TeamInput("A", tuple(p.player_id for p in roster), roster=roster,
                         rotation_plan=tuple({"player_id": pid, "featured": True} for pid in featured))
        b_roster = tuple(p for p in game_day_roster("B") if p.player_id != "B-WR5")
        away = TeamInput("B", tuple(p.player_id for p in b_roster), roster=b_roster)
        for i in range(60):
            event = "pause-search-%d" % i
            partial = run_game(home, away, event_id=event, snapshot="snapshot", client=self.client,
                               management_mode="user_controlled", controlled_team="A")
            if not partial["terminated"]:
                break
        else:
            self.fail("no consequential removal in 60 synthetic games")
        self.assertNotIn("final_score", partial)
        pause = partial["pauses"][-1]
        choices = {d["slot"]: d["eligible"][-1] for d in pause["decisions"]}
        decisions = [{"token": pause["continuation_token"], "choices": choices}]
        resumed = None
        while True:
            resumed = run_game(home, away, event_id=event, snapshot="snapshot", client=self.client,
                               management_mode="user_controlled", controlled_team="A",
                               continuation={"decisions": decisions})
            if resumed["terminated"]:
                break
            pause = resumed["pauses"][-1]
            decisions.append({"token": pause["continuation_token"],
                              "choices": {d["slot"]: d["default"] for d in pause["decisions"]}})
        self.assertEqual(validate_result(resumed), [])
        drive = partial["pauses"][-1]["drive"]
        self.assertEqual(settled(resumed["possessions"], drive), settled(partial["possessions"], drive))
        self.assertEqual([r for r in resumed["play_ledger"] if r["drive"] <= drive], partial["play_ledger"])
        self.assertEqual(len(resumed["pauses"]), len(decisions))


if __name__ == "__main__":
    unittest.main()
