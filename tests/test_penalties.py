"""Kernel 2014.6 batch B11: per-play penalty records (R11).

Under the profile flag penalty_records every replayed real drive's own penalty
clauses are replayed in its chain layout (runtime.penalties): no-play and
pre-kick rows and the clauses on counted snaps, walked by ledger-walk-v2
(runtime.chains.walk_steps), legal from their spots (half the distance, a
half-distance record's floor or ceiling, a spot foul's new spot in the field),
first downs by rule or yardage, each fouler a labelled group draw on the
public-penalty-detail-v1 stream, the counters charged to the fouling club, the
kick plays' own records on their rows. Every number is read from the base's
artifacts (library/data/2010_2014w4_penalties.json and the field-position
model's `pen` annotations). Synthetic seeds only; the private service is never
contacted.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import copy
import inspect
import json
import random
import unittest

from runtime import bands, gamebook, penalties
from runtime import kernel as kernel_module
from runtime import chains as chain_walk
from runtime.calibration_base import BASE_2010_2014W4
from runtime.kernel import removal_names, resolve_game, validate_result
from runtime.play_detail import B11_CLASSES, check_ledger, has_penalty_records
from runtime.profiles import B11_FLAGS, FLAG_REQUIRES, PROFILE_2014_5, PROFILE_2014_6, Profile
from runtime.statbook import aggregate_receipts, make_receipt
from synthetic_games import SEED, sample_teams

ROOT = Path(__file__).resolve().parents[1]
A, B = sample_teams()
MODEL = BASE_2010_2014W4.penalties()
FPM = BASE_2010_2014W4.field_position()
ART = json.loads((ROOT / "library/data/2010_2014w4_penalties.json").read_text())


def level(flags):
    return Profile("2014.6", base=PROFILE_2014_6.base, cell_rules=PROFILE_2014_6.cell_rules,
                   strength=PROFILE_2014_6.strength, flags=frozenset(flags), record_base=True)


B11_OFF = level(PROFILE_2014_6.flags - B11_FLAGS)


def play(name, profile=PROFILE_2014_6):
    return resolve_game(A, B, seed=SEED + b"-" + name.encode(), event_id=name, _test_profile=profile)


def receipt(result, detail="compact_stats"):
    return make_receipt(result, week=5, matchup="B at A", detail=detail)


def clean(result):
    return (validate_result(result) + check_ledger(result) + check_ledger(receipt(result, "full"))
            + check_ledger(receipt(result)))


class Sample:
    """One cached 40-game sample of the shipped profile."""
    games = None

    @classmethod
    def get(cls):
        if cls.games is None:
            cls.games = [play("b11-sample-%d" % i) for i in range(40)]
        return cls.games


def entries(result):
    return [(row, e) for row in result["play_ledger"] for e in (row.get("penalties") or ())]


def rec(side="D", yards=5, status="A", auto=False, half=False, spot_foul=False, type_="Offside"):
    return penalties.Rec(0, 0, 0, type_, side, yards if status == "A" else 0, status, "N", False, "run",
                         None if spot_foul else 5, auto, half, spot_foul)


# ---- the model and its pure helpers ---------------------------------------------------------

class ModelTests(unittest.TestCase):
    def test_artifact_is_pinned_and_read(self):
        pin = dict(BASE_2010_2014W4.files)["penalties"]
        self.assertEqual(pin.path, "library/data/2010_2014w4_penalties.json")
        self.assertEqual(MODEL.reduced_below, ART["half_distance"]["reduced_below_nominal"])
        self.assertEqual(MODEL.centres, ART["band_centres"])
        for name, entry in ART["auto_first_down"]["types"].items():
            self.assertEqual(MODEL.auto_class[name], entry["class"])
        self.assertEqual(MODEL.types, FPM.load()["penalty_types"])
        self.assertTrue(ART["second_pass"]["agree"])

    def test_auto_rule_by_class(self):
        names = {cls: next(n for n, e in ART["auto_first_down"]["types"].items() if e["class"] == cls)
                 for cls in ("automatic", "yardage", "replay")}
        self.assertTrue(MODEL.auto(names["automatic"], False))
        self.assertFalse(MODEL.auto(names["yardage"], True))
        self.assertTrue(MODEL.auto(names["replay"], True))
        self.assertFalse(MODEL.auto(names["replay"], False))
        self.assertTrue(MODEL.auto("a type the table does not hold", True))

    def test_no_club_identity(self):
        source = inspect.getsource(penalties).split('"""', 2)[2]   # the code, not the docstring
        for word in ("protagonist", "Jacksonville", "controlled_team", "team_id"):
            self.assertNotIn(word, source)

    def test_stream_keys_are_literal(self):
        a = penalties.stream(b"s" * 32, "ev", "drive", 3).random()
        b = penalties.stream(b"s" * 32, "ev", "drive", 3).random()
        c = penalties.stream(b"s" * 32, "ev", "punt", 3).random()
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_slope_zero_terms(self):
        self.assertEqual(set(penalties.TERMS.values()), {0.0})

    def test_classification_by_place(self):
        # [order, type, side, yards, status, enforce, real fd, host, half, nominal]
        code = MODEL.types.index("False Start")
        pen = [[0, code, "O", -5, "A", "N", False, "no_play", 0, 5],     # before snap 1: movable
               [3, code, "O", -5, "A", "N", False, "no_play", 0, 5],     # after the 2 snaps: tail
               [2, code, "D", 5, "A", "S", False, "run", 0, 5],          # on snap 2 (run)
               [4, code, "O", 0, "D", "K", False, "punt", 0, 5]]         # the punt row's
        plan = penalties.classify(MODEL, pen, "punt", 2)
        self.assertEqual([(e.before, e.tail) for e in plan.events], [(0, False), (2, True)])
        self.assertEqual([a.before for a in plan.attached], [1])
        self.assertEqual(len(plan.kick_row), 1)
        self.assertEqual(plan.yards, -5 - 5 + 5)
        touchdown = penalties.classify(MODEL, pen[:3], "touchdown", 2)
        # After a touchdown's last snap and on that snap: enforced after the possession.
        self.assertEqual(len(touchdown.post), 2)
        self.assertEqual(len(touchdown.events), 1)

    def test_compiled_and_legal(self):
        auto = rec(yards=5, auto=True)
        self.assertEqual(penalties.compiled([rec(yards=5), auto]), (10, True, 1))
        self.assertTrue(penalties.legal([rec(yards=5)], 10))
        self.assertFalse(penalties.legal([rec(yards=15)], 20))          # more than half the distance
        self.assertTrue(penalties.legal([rec(yards=10, half=True)], 20))
        self.assertTrue(penalties.legal([rec(yards=10, half=True)], 21))  # ceiling of 10.5
        self.assertFalse(penalties.legal([rec(yards=10, half=True)], 30))
        self.assertTrue(penalties.legal([rec(yards=40, spot_foul=True)], 45))
        self.assertFalse(penalties.legal([rec(yards=45, spot_foul=True)], 45))  # into the end zone
        self.assertTrue(penalties.legal([rec(side="O", yards=-10)], 60))
        self.assertFalse(penalties.legal([rec(side="O", yards=-10)], 85))
        self.assertTrue(penalties.legal([rec(status="D")], 1))

    def test_relocation_gate(self):
        summary = {"records": ((10, True, False, "D"),)}
        self.assertTrue(penalties.relocation_ok(summary, spot=30, end=10, sacks=0, runs=0, run_loss=10))
        self.assertFalse(penalties.relocation_ok(summary, spot=15, end=5, sacks=0, runs=0, run_loss=10))
        self.assertTrue(penalties.relocation_ok(summary, spot=15, end=5, sacks=1, runs=0, run_loss=10))

    def test_entry_errors(self):
        entry = penalties.published(rec(yards=5), offense="A", defense="B", enforcement=penalties.NO_PLAY)
        self.assertEqual(penalties.entry_errors(entry, offense="A", defense="B"), [])
        self.assertTrue(penalties.entry_errors(dict(entry, team="A"), offense="A", defense="B"))
        self.assertTrue(penalties.entry_errors(dict(entry, penalty_yards=-5), offense="A", defense="B"))
        self.assertTrue(penalties.entry_errors(dict(entry, decision_source="coach"), offense="A", defense="B"))
        self.assertTrue(penalties.entry_errors(dict(entry, fouler="X"), offense="A", defense="B"))
        team = dict(entry, fouler_basis=penalties.TEAM_FOUL)
        self.assertEqual(penalties.entry_errors(team, offense="A", defense="B"), [])

    def test_unnamed_share_is_a_club_foul(self):
        key = next(k for k, v in ART["fouler_groups"]["shares"].items()
                   if set(v) == {penalties.UNNAMED_GROUP})
        side, name = key.split("|", 1)
        entry = {"penalty_side": "offense" if side == "O" else "defense", "penalty_type": name}
        self.assertIsNone(penalties.name_fouler(random.Random(1), MODEL, entry, []))
        self.assertEqual(entry["fouler_basis"], penalties.TEAM_FOUL)


# ---- ledger-walk-v2 -------------------------------------------------------------------------

class WalkTests(unittest.TestCase):
    def test_without_records_equals_the_v1_walk(self):
        rng = random.Random(7)
        for _ in range(200):
            values = [rng.randint(-8, 25) for _ in range(rng.randint(1, 12))]
            start = rng.randint(30, 99)
            v1 = chain_walk.walk(start, values)
            v2 = chain_walk.walk_steps(start, [("s", v, None) for v in values])
            for key in ("rows", "chains", "state", "failed", "breaks"):
                self.assertEqual(v1[key], v2[key])
            self.assertEqual(v2["penalty_first_downs"], 0)

    def test_defensive_no_play_first_down(self):
        # 3rd and 8 at the 50: an automatic defensive foul of 5 is a first down;
        # a 5-yard yardage foul is not, an 8-yard one is.
        steps = [("s", 2, None), ("s", 0, None), ("p", (5, True, 0))]
        w = chain_walk.walk_steps(60, steps)
        self.assertEqual(w["penalty_first_downs"], 1)
        self.assertEqual(w["state"]["down"], 1)
        self.assertEqual(w["state"]["los"], 53)
        w = chain_walk.walk_steps(60, [("s", 2, None), ("s", 0, None), ("p", (5, False, 0))])
        self.assertEqual((w["state"]["down"], w["penalty_first_downs"]), (3, 0))
        self.assertEqual(w["state"]["ydstogo"], 3)
        w = chain_walk.walk_steps(60, [("s", 2, None), ("s", 0, None), ("p", (8, False, 0))])
        self.assertEqual((w["state"]["down"], w["penalty_first_downs"]), (1, 1))

    def test_offensive_no_play_keeps_the_down(self):
        w = chain_walk.walk_steps(75, [("p", (-5, False, None)), ("s", 4, None)])
        self.assertEqual(w["rows"][0]["ydstogo"], 15)
        self.assertEqual(w["rows"][0]["los"], 80)
        self.assertEqual((w["state"]["down"], w["state"]["ydstogo"]), (2, 11))

    def test_clause_after_a_snap(self):
        # A 12-yard gain then a 15-yard automatic foul: the scrimmage first down
        # and a first down by penalty, as the source flags both.
        w = chain_walk.walk_steps(70, [("s", 12, (15, True, 0))])
        self.assertEqual((w["chains"][0], w["penalty_first_downs"]), (1, 1))
        self.assertEqual((w["state"]["down"], w["state"]["los"], w["state"]["ydstogo"]), (1, 43, 10))
        # A yardage-only foul that reaches the new line after a gaining snap is not one.
        w = chain_walk.walk_steps(70, [("s", 12, (12, False, 0))])
        self.assertEqual((w["chains"][0], w["penalty_first_downs"]), (1, 0))
        # An offensive foul after a gaining snap keeps the line to gain: first and 25.
        w = chain_walk.walk_steps(70, [("s", 12, (-15, False, None))])
        self.assertEqual((w["state"]["down"], w["state"]["ydstogo"]), (1, 25))
        # A fourth-down snap short of the line saved by its own clause's first down.
        w = chain_walk.walk_steps(60, [("s", 0, None), ("s", 0, None), ("s", 0, None), ("s", 2, (5, True, 0))])
        self.assertIsNone(w["failed"])
        self.assertEqual(w["penalty_first_downs"], 1)

    def test_pre_tail_state_and_kick_state(self):
        steps = [("s", 2, None), ("s", 0, None), ("s", 1, None), ("p", (-5, False, None))]
        w = chain_walk.walk_steps(70, steps)
        self.assertEqual((w["pre_tail_state"]["down"], w["pre_tail_state"]["los"]), (4, 67))
        state = chain_walk.fourth_down_state_steps("punt", 70, steps)
        self.assertEqual((state["down"], state["ydstogo"], state["los"]), (4, 12, 72))

    def test_ledger_steps_round_trip(self):
        r = next(g for g in Sample.get() if any(row.get("play_type") == penalties.PENALTY_ROW
                                                for row in g["play_ledger"]))
        for p in r["possessions"]:
            rows = [row for row in r["play_ledger"] if row.get("drive") == p["number"]
                    and row.get("play_type") in ("pass", "run", penalties.PENALTY_ROW)]
            w = chain_walk.walk_steps(p["start_spot"], chain_walk.ledger_steps(rows),
                                      p["category"] in chain_walk.TURNOVER_TERMINALS)
            self.assertEqual(w["penalty_first_downs"], p["chains"][1])
            self.assertEqual([w["chains"][0]] + w["chains"][1:], [p["chains"][0]] + p["chains"][2:])


# ---- replayed records in play ---------------------------------------------------------------

class ReplayTests(unittest.TestCase):
    def test_sample_is_clean_and_reconciles(self):
        for r in Sample.get():
            self.assertEqual(clean(r), [], r["event_id"])
            self.assertTrue(has_penalty_records(r))
            self.assertEqual(r["penalties"]["chain_model"], chain_walk.CHAIN_MODEL_V2)

    def test_every_kind_of_row_occurs(self):
        kinds = {(row.get("play_type"), e["enforcement"]) for r in Sample.get() for row, e in entries(r)}
        for expected in (("penalty", penalties.NO_PLAY), ("penalty", penalties.PRE_KICK),
                         ("pass", penalties.AFTER_SNAP), ("run", penalties.AFTER_SNAP),
                         ("kickoff", penalties.ON_KICK), ("punt", penalties.ON_KICK)):
            self.assertIn(expected, kinds)

    def test_records_are_replayed_never_decided(self):
        for r in Sample.get():
            for row, e in entries(r):
                self.assertEqual(e["decision_source"], penalties.DECISION_SOURCE)
                if row.get("play_type") == penalties.PENALTY_ROW:
                    self.assertEqual(row["decision_source"], penalties.DECISION_SOURCE)
                    self.assertTrue(row["untimed"])
                    self.assertEqual(row["result_yards"], 0)

    def test_foulers_come_from_the_fouling_club(self):
        bases = set()
        for r in Sample.get():
            for row, e in entries(r):
                bases.add(e["fouler_basis"])
                if e["fouler"]:
                    self.assertIn(e["fouler"], r["team_stats"][e["team"]]["players"])
                    self.assertIn((e["team"], e["fouler"]), set(removal_names(row)))
        self.assertTrue({penalties.GROUP_DRAW, penalties.UNIT_DRAW} <= bases)

    def test_counters_go_to_the_fouling_club(self):
        for r in Sample.get():
            for team, s in r["team_stats"].items():
                mine = [e for _, e in entries(r) if e["team"] == team]
                self.assertEqual(s["penalties"], sum(e["status"] == "accepted" for e in mine))
                self.assertEqual(s["penalty_yards"], sum(penalties.charged_yards(e) for e in mine))
                self.assertEqual(s["penalties_declined"], sum(e["status"] == "declined" for e in mine))
                self.assertEqual(s["penalties_offsetting"], sum(e["status"] == "offsetting" for e in mine))
                gained = sum(e["first_down"] for row, e in entries(r) if row.get("offense") == team
                             and row.get("play_type") in ("pass", "run", penalties.PENALTY_ROW))
                self.assertEqual(s["penalty_first_downs"], gained)
                self.assertEqual(sum(p["chains"][1] for p in r["possessions"] if p["team"] == team), gained)

    def test_each_record_is_legal_from_its_spot(self):
        for r in Sample.get():
            for row, e in entries(r):
                if row.get("play_type") == penalties.PENALTY_ROW:
                    self.assertTrue(penalties.legal_entries(row["penalties"], row["yardline"]))

    def test_fouls_are_never_player_evidence(self):
        # E1: no observation is written from a penalty row or record.
        source = inspect.getsource(kernel_module._append_evidence)
        self.assertNotIn("penalt", source)
        for r in Sample.get()[:10]:
            for obs in r["player_evidence"]:
                self.assertNotIn("penalt", json.dumps(obs).lower())

    def test_profile_without_the_flag_keeps_the_counter(self):
        r = play("b11-off", profile=B11_OFF)
        self.assertNotIn("penalties", r)
        self.assertFalse(entries(r))
        self.assertNotIn("penalties_declined", next(iter(r["team_stats"].values())))
        self.assertEqual(clean(r), [])

    def test_profile_2014_5_carries_none(self):
        r = play("b11-old", profile=PROFILE_2014_5)
        self.assertNotIn("penalties", r)
        self.assertFalse(entries(r))

    def test_flag_requires_sequencing(self):
        self.assertEqual(FLAG_REQUIRES["penalty_records"], frozenset({"possession_sequencing"}))
        self.assertIn("penalty_records", PROFILE_2014_6.flags)


# ---- detection ------------------------------------------------------------------------------

class DetectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = next(g for g in Sample.get() if any(row.get("play_type") == penalties.PENALTY_ROW
                                                         and any(e["status"] == "accepted" for e in row["penalties"])
                                                         for row in g["play_ledger"]))

    def doctored(self):
        r = copy.deepcopy(self.result)
        row = next(row for row in r["play_ledger"] if row.get("play_type") == penalties.PENALTY_ROW
                   and any(e["status"] == "accepted" for e in row["penalties"]))
        return r, row

    def classes(self, r):
        return {e.split(":")[0] for e in check_ledger(r)}

    def test_classes_are_registered(self):
        self.assertEqual(B11_CLASSES, ("penalty_record_invalid", "penalty_enforcement_illegal",
                                       "penalty_counter_mismatch"))

    def test_record_invalid(self):
        r, row = self.doctored()
        row["penalties"][0]["decision_source"] = "coach"
        self.assertIn("penalty_record_invalid", self.classes(r))

    def test_counter_mismatch(self):
        r, row = self.doctored()
        e = next(e for e in row["penalties"] if e["status"] == "accepted")
        r["team_stats"][e["team"]]["penalties"] += 1
        self.assertIn("penalty_counter_mismatch", self.classes(r))

    def test_snap_sum_is_event_aware(self):
        r, row = self.doctored()
        e = next(e for e in row["penalties"] if e["status"] == "accepted")
        e["penalty_yards"] += 1 if e["penalty_yards"] > 0 else -1
        found = self.classes(r)
        self.assertIn("snap_sum_ne_drive_net", found)

    def test_enforcement_illegal(self):
        r, row = self.doctored()
        row["yardline"] = (row["yardline"] or 50) + 1
        self.assertIn("penalty_enforcement_illegal", self.classes(r))

    def test_compact_receipt_reconciles(self):
        rc = receipt(self.result)
        self.assertEqual(check_ledger(rc), [])
        team = next(iter(rc["team_stats"]))
        rc["team_stats"][team]["penalties_declined"] = rc["team_stats"][team].get("penalties_declined", 0) + 1
        self.assertIn("penalty_counter_mismatch", {e.split(":")[0] for e in check_ledger(rc)})


# ---- the static gates -----------------------------------------------------------------------

class GateTests(unittest.TestCase):
    def test_layouts_of_admitted_drives(self):
        """Drives with records, laid out at their own starts, wherever the
        penalty-aware static gate admits them: a legal v2 layout (or the
        counted fallback of the kernel) every time."""
        rng = random.Random(11)
        T = FPM.T
        tuples = [(FPM.CATEGORIES[ci], t) for row in FPM.load()["pools"]["neutral"]
                  for ci, lst in enumerate(row) for t in lst if FPM.value(t, "pen", ())]
        rng.shuffle(tuples)
        failed = checked = 0
        for category, t in tuples[:150]:
            start = t[T["start"]]
            if not FPM.static_feasible(category, t, start, True):
                continue
            plan = FPM.penalty_plan(category, t)[0]
            net, _ = FPM.adapt(category, t, start)
            free, kneel_sum, terminal_value, sacks = FPM.fixed_yardage(category, t)
            losses = [rng.randint(3, 10) for _ in range(sacks)] if free > 0 else []
            if free <= 0 and sacks:
                required = kneel_sum + terminal_value - (net - plan.yards)
                base, extra = divmod(required, sacks)
                losses = [base + (1 if i < extra else 0) for i in range(sacks)]
            free_total = net - (kneel_sum - sum(losses) + terminal_value + plan.yards)
            attempts, runs = int(t[T["attempts"]]), int(t[T["runs"]])
            usable = attempts - (1 if category == "interception" else 0)
            if usable and runs:
                pass_yards = free_total // 2
            else:
                pass_yards = free_total if usable else 0
            layout = chain_walk.drive_layout(
                seed=SEED, event_id="b11-gate", drive_no=checked, offense="A", category=category,
                td_type=t[T["td_kind"]] if category == "touchdown" else None, runs=runs, attempts=attempts,
                sacks=int(t[T["sacks"]]), kneel_yards=list(t[T["kneel_yards"]]), spikes=int(t[T["spikes"]]),
                pass_yards=pass_yards, rush_free=free_total - pass_yards, losses=losses,
                safety_terminal=(t[T["safety_term_kind"]], terminal_value) if category == "safety" else None,
                net=net, spot=start, completion_rate=0.6, targets=list(t[T["chains"]]),
                term_down=t[T["term_down"]], diagnostics={}, penalty=plan)
            checked += 1
            failed += not layout["ok"]
            if layout["ok"]:
                self.assertEqual(sum(layout["values"]) + chain_walk.layout_penalty_yards(layout), net)
        self.assertGreater(checked, 50)
        self.assertLessEqual(failed, 2)


# ---- records, views and bands ---------------------------------------------------------------

class RecordsTests(unittest.TestCase):
    def test_receipts_and_statbook(self):
        games = Sample.get()[:8]
        receipts = [receipt(r) for r in games]
        for rc in receipts:
            self.assertEqual(rc["penalties"]["model"], penalties.MODEL)
        book = aggregate_receipts([dict(rc, event_id="%s-%d" % (rc["event_id"], i)) for i, rc in enumerate(receipts)])
        team = book["teams"]["A"]["team_stats"]
        self.assertEqual(team["penalties_declined"], sum(r["team_stats"]["A"]["penalties_declined"] for r in games))
        self.assertEqual(team["penalty_first_downs"], sum(r["team_stats"]["A"]["penalty_first_downs"] for r in games))

    def test_gamebook_penalty_summary_and_first_downs(self):
        r = Sample.get()[0]
        text = gamebook.render(receipt(r, "full"), "A")
        self.assertIn("#### Penalty summary", text)
        self.assertIn("Declined-offsetting", text)
        view = gamebook.GameView(receipt(r, "full"), "A")
        for club in ("A", "B"):
            self.assertEqual(view.first_down_split(club)[2],
                             sum(p["chains"][1] for p in r["possessions"] if p["team"] == club))

    def test_season_tables_are_split_by_definition(self):
        from scripts.render_season_stats import team_stats_markdown
        agg = aggregate_receipts
        old = receipt(play("b11-split-old", profile=PROFILE_2014_5))
        old["week"] = 1
        new = receipt(Sample.get()[1])
        book = agg([old, new])
        text = team_stats_markdown(2014, book, [old, new])
        self.assertIn("## Penalties — kernel 2014.6 games with penalty records", text)
        self.assertIn("No combined penalty figure or rank is published.", text)
        only_old = team_stats_markdown(2014, agg([old]), [old])
        self.assertNotIn("penalty records", only_old)

    def test_team_tracker_never_adds_the_two_definitions(self):
        # Review fix (October 16, 2026): the tracker's season Penalties cell
        # shows the counter games and the penalty-record games apart.
        import tempfile
        from runtime.seasons import SeasonPaths
        from scripts import render_team_tracker as tracker
        old = receipt(play("b11-split-old", profile=PROFILE_2014_5))
        old.update(week=1, event_id="b11-tracker-old")
        new = receipt(Sample.get()[1])
        new.update(week=5, event_id="b11-tracker-new")
        self.assertNotIsInstance(old.get("penalties"), dict)
        self.assertIsInstance(new.get("penalties"), dict)
        with tempfile.TemporaryDirectory() as tmp:
            folder = SeasonPaths(2014, Path(tmp)).receipts
            folder.mkdir(parents=True)

            def readme(receipts):
                for path in folder.glob("*.json"):
                    path.unlink()
                for rc in receipts:
                    (folder / ("%s.json" % rc["event_id"])).write_text(json.dumps(rc))
                games = tracker.load_games(Path(tmp), 2014, "A")
                return games, tracker.readme(Path(tmp), 2014, "A", games)

            games, text = readme([old, new])
            a_old, a_new = old["team_stats"]["A"], new["team_stats"]["A"]
            cell = "counter games %d-%d; penalty records %d-%d" % (
                a_old["penalties"], a_old["penalty_yards"], a_new["penalties"], a_new["penalty_yards"])
            self.assertIn(cell, text)
            self.assertIn(tracker.PENALTY_SPLIT_NOTE, text)
            summed = "| %d-%d |" % (a_old["penalties"] + a_new["penalties"],
                                    a_old["penalty_yards"] + a_new["penalty_yards"])
            self.assertNotIn(summed, text)
            # one definition: the earlier single cell, no note
            for only in ([old], [new]):
                _, text = readme(only)
                line = only[0]["team_stats"]["A"]
                self.assertIn("| %d-%d |" % (line["penalties"], line["penalty_yards"]), text)
                self.assertNotIn(tracker.PENALTY_SPLIT_NOTE, text)
                self.assertNotIn("counter games", text)


class BandTests(unittest.TestCase):
    def test_rows_and_centres(self):
        receipts = [receipt(r) for r in Sample.get()]
        team_games, rows = bands.audit_penalties(receipts, cohort="2014.6")
        self.assertEqual(team_games, 2 * len(receipts))
        by = {m: (o, c, t, s) for m, o, c, t, s in rows}
        accepted = ART["band_centres"]["accepted_penalties_per_team_game"]
        centre = accepted["pooled"][0] / accepted["pooled"][1]
        row = by["accepted penalties per team-game (drive and kick plays; the fouling club)"]
        self.assertAlmostEqual(row[1], centre)
        self.assertAlmostEqual(row[2], 3 * (accepted["dispersion"] * centre / team_games) ** 0.5)
        graded = [m for m, (o, c, t, s) in by.items() if s in ("WITHIN", "OUTSIDE")]
        self.assertEqual(len(graded), 3)
        self.assertEqual(bands.audit_penalties(receipts, cohort="2014.5"), (0, []))
        old = [receipt(play("b11-band-old", profile=B11_OFF))]
        self.assertEqual(bands.audit_penalties(old, cohort="2014.6"), (0, []))


if __name__ == "__main__":
    unittest.main()
