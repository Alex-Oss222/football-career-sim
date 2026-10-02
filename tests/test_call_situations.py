"""Kernel 2014.5: call labels follow the sheet's situational menus and the
opening sequence, and never move a result.

Synthetic seeds only; the private service is never contacted. Club A carries
Jacksonville's frozen 2014 Week 2 sheet (with its menus and opener positions)
on the shared synthetic roster; the invariance test runs the same seeded
games under the same sheet stripped of every menu and opener field, which is
exactly the 2014.4 uniform rule, and compares everything but the label
fields.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import copy
import json
import unittest

from runtime import call_situations as cs
from runtime.game_runner import build_game_packet
from runtime.kernel import TeamInput, resolve_game, validate_result
from runtime.play_detail import check_ledger, coherence_counts
from synthetic_games import SEED, team

ROOT = Path(__file__).resolve().parents[1]
WEEK2 = ROOT / "career/2014/05_Regular_Season/Games/Week_02/call_sheet.json"
WEEK1 = ROOT / "career/2014/05_Regular_Season/Games/Week_01/call_sheet.json"
LABEL_FIELDS = {"concept", "family", "personnel", "formation", "motion", "protection", "tags",
                "scramble", "label_groups", "label_source", "label_type", "situation", "script_position"}
GAMES = 30


def load_sheet(path):
    return json.loads(path.read_text(encoding="utf-8"))["offensive_call_sheet"]


def uniform_sheet(sheet):
    """The same sheet without any menu or opener field: the 2014.4 label rule."""
    return [{k: v for k, v in call.items() if k not in ("menus", "opener", "opener_returns")} for call in sheet]


def scrimmage(result, offense):
    return [r for r in result["play_ledger"] if r["offense"] == offense and r["play_type"] in ("run", "pass")]


def strip_labels(rows):
    return [{k: v for k, v in r.items() if k not in LABEL_FIELDS} for r in rows]


class SituationClassificationTests(unittest.TestCase):
    def test_menu_keys_normalise_the_sheets_spellings(self):
        self.assertEqual(cs.menu_keys(["normal down", "2nd-and-long", "third-and-short", "PRESS sequence",
                                       "four minute", "low red zone", "goal line", "sudden change"]),
                         (cs.NORMAL, cs.SECOND_LONG, cs.THIRD_SHORT, cs.PRESS, cs.FOUR_MINUTE,
                          cs.LOW_RED, cs.GOAL_LINE, cs.SUDDEN_CHANGE))
        self.assertEqual(cs.menu_keys(None), ())

    def test_down_distance_and_zone_bins(self):
        base = dict(goal_to_go=False, half=1, half_remaining=900, score_diff=0)
        self.assertEqual(cs.classify(down=3, ydstogo=1, yardline=49, **base)[0], cs.THIRD_SHORT)
        self.assertEqual(cs.classify(down=3, ydstogo=2, yardline=49, **base)[0], cs.THIRD_SHORT)
        self.assertEqual(cs.classify(down=3, ydstogo=3, yardline=49, **base)[0], cs.THIRD_MEDIUM)
        self.assertEqual(cs.classify(down=3, ydstogo=5, yardline=49, **base)[0], cs.THIRD_MEDIUM)
        self.assertEqual(cs.classify(down=3, ydstogo=6, yardline=49, **base)[0], cs.THIRD_LONG)
        self.assertEqual(cs.classify(down=4, ydstogo=8, yardline=49, **base)[0], cs.THIRD_LONG)
        self.assertEqual(cs.classify(down=2, ydstogo=7, yardline=49, **base)[0], cs.SECOND_LONG)
        self.assertEqual(cs.classify(down=2, ydstogo=6, yardline=49, **base), [cs.NORMAL])
        self.assertEqual(cs.classify(down=1, ydstogo=10, yardline=90, **base)[0], cs.BACKED_UP)
        self.assertEqual(cs.classify(down=1, ydstogo=10, yardline=89, **base), [cs.NORMAL])
        self.assertEqual(cs.classify(down=1, ydstogo=10, yardline=20, **base)[0], cs.HIGH_RED)
        self.assertEqual(cs.classify(down=1, ydstogo=10, yardline=11, **base)[0], cs.HIGH_RED)
        self.assertEqual(cs.classify(down=1, ydstogo=10, yardline=10, **base)[0], cs.LOW_RED)
        self.assertEqual(cs.classify(down=1, ydstogo=5, yardline=5, **base)[0], cs.LOW_RED)
        self.assertEqual(cs.classify(down=1, ydstogo=4, yardline=4, goal_to_go=True, half=1,
                                     half_remaining=900, score_diff=0)[0], cs.GOAL_LINE)
        # Third down inside the zones: the distance menu first, then the zone.
        self.assertEqual(cs.classify(down=3, ydstogo=8, yardline=11, **base)[:2], [cs.THIRD_LONG, cs.HIGH_RED])

    def test_clock_and_sudden_change(self):
        self.assertEqual(cs.classify(down=1, ydstogo=10, yardline=60, goal_to_go=False, half=1,
                                     half_remaining=119, score_diff=14)[:2], [cs.TWO_MINUTE, cs.PRESS])
        self.assertEqual(cs.classify(down=1, ydstogo=10, yardline=60, goal_to_go=False, half=2,
                                     half_remaining=119, score_diff=14), [cs.FOUR_MINUTE, cs.NORMAL])
        self.assertEqual(cs.classify(down=1, ydstogo=10, yardline=60, goal_to_go=False, half=2,
                                     half_remaining=120, score_diff=0)[:2], [cs.TWO_MINUTE, cs.PRESS])
        self.assertEqual(cs.classify(down=1, ydstogo=10, yardline=60, goal_to_go=False, half=2,
                                     half_remaining=240, score_diff=3), [cs.FOUR_MINUTE, cs.NORMAL])
        self.assertEqual(cs.classify(down=1, ydstogo=10, yardline=60, goal_to_go=False, half=2,
                                     half_remaining=241, score_diff=3), [cs.NORMAL])
        for index, expect in ((0, [cs.SUDDEN_CHANGE, cs.NORMAL]), (1, [cs.SUDDEN_CHANGE, cs.NORMAL]), (2, [cs.NORMAL])):
            self.assertEqual(cs.classify(down=1, ydstogo=10, yardline=60, goal_to_go=False, half=1,
                                         half_remaining=900, score_diff=0, start_kind="interception",
                                         snap_index=index), expect)
        self.assertEqual(cs.classify(down=1, ydstogo=10, yardline=60, goal_to_go=False, half=1,
                                     half_remaining=900, score_diff=0, start_kind="punt"), [cs.NORMAL])
        self.assertEqual(cs.half_clock(3600, 2000, False), (1, 200))
        self.assertEqual(cs.half_clock(1800, 100, False), (2, 100))
        self.assertEqual(cs.half_clock(900, 50, "OT"), ("OT", 50))

    def test_frozen_2014_sheets_declare_menus_and_complete_openers(self):
        for path in (WEEK1, WEEK2):
            sheet = load_sheet(path)
            self.assertTrue(all(cs.menu_keys(call.get("menus")) for call in sheet), path)
            positions = cs.script_positions(sheet)
            self.assertEqual(sorted(positions), list(range(1, 31)), path)
            snag = next(call for call in sheet if call["family"] == "Snag")
            self.assertTrue(cs.restricted({"menus": cs.menu_keys(snag["menus"])}))
            self.assertEqual(cs.menu_keys(snag["menus"]), (cs.LOW_RED, "two-point"))
        self.assertFalse(cs.restricted({"menus": ()}))
        self.assertFalse(cs.restricted({"menus": (cs.NORMAL, cs.THIRD_LONG)}))


class SituationalLabelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sheet = load_sheet(WEEK2)
        gated = {"name": "Probe gated shot", "family": "Mills", "type": "pass", "personnel": "11",
                 "menus": ["third-and-long"]}
        cls.a = team("A", cls.sheet + [gated])
        cls.b = team("B")
        cls.games = tuple(resolve_game(cls.a, cls.b, seed=SEED + b"-sit%05d" % i, event_id="situation-%d" % i)
                          for i in range(GAMES))

    def test_coherence_and_label_sources(self):
        counts = coherence_counts([e for r in self.games for e in check_ledger(r)])
        self.assertEqual(sum(counts.values()), 0, counts)
        sources = set()
        for r in self.games:
            self.assertEqual(validate_result(r), [])
            for row in scrimmage(r, "A"):
                sources.add(row["label_source"])
                self.assertIn(row["situation"], (cs.NORMAL, cs.SECOND_LONG, cs.THIRD_SHORT, cs.THIRD_MEDIUM,
                                                 cs.THIRD_LONG, cs.BACKED_UP, cs.HIGH_RED, cs.LOW_RED,
                                                 cs.GOAL_LINE, cs.TWO_MINUTE, cs.FOUR_MINUTE, cs.SUDDEN_CHANGE))
                if row["label_source"].startswith("sheet:") and row["label_source"] not in (
                        "sheet:fallback", "sheet:" + cs.OPENING):
                    # A menu label names a menu the snap is in and the call declares.
                    menu = row["label_source"].split(":", 1)[1]
                    expected = cs.classify(
                        down=row["down"], ydstogo=row["ydstogo"], yardline=row["yardline"],
                        goal_to_go=row["goal_to_go"],
                        half=cs.half_clock(0, 0, False)[0], half_remaining=None, score_diff=0)
                    self.assertTrue(menu in expected or menu in (cs.TWO_MINUTE, cs.PRESS, cs.FOUR_MINUTE,
                                                                 cs.SUDDEN_CHANGE), (menu, row))
                    call = next(c for c in self.a.offensive_call_sheet if c["name"] == row["concept"])
                    self.assertIn(menu, cs.menu_keys(call["menus"]))
            for row in scrimmage(r, "B"):
                self.assertIn(row["label_source"], ("generic", "kneel", "spike"))
        self.assertIn("sheet:" + cs.OPENING, sources)
        self.assertIn("sheet:" + cs.THIRD_LONG, sources)
        self.assertIn("sheet:" + cs.LOW_RED, sources)
        self.assertNotIn("sheet", sources)

    def test_snag_labels_only_in_the_low_red_zone(self):
        seen = 0
        for r in self.games:
            for row in scrimmage(r, "A"):
                if row["family"] == "Snag":
                    seen += 1
                    # Inside the 10, goal line included: a goal-line pass takes
                    # the low-red-zone pass menu by the sheet's own rule.
                    self.assertEqual(row["label_source"], "sheet:" + cs.LOW_RED, row)
                    self.assertIn(row["situation"], (cs.LOW_RED, cs.GOAL_LINE), row)
                    self.assertLessEqual(row["yardline"], 10, row)
        self.assertGreater(seen, 0)

    def test_a_gated_call_never_lands_outside_its_menu(self):
        seen = 0
        for r in self.games:
            for row in scrimmage(r, "A"):
                if row["concept"] == "Probe gated shot":
                    seen += 1
                    self.assertEqual(row["label_source"], "sheet:" + cs.THIRD_LONG, row)
                    self.assertGreaterEqual(row["down"], 3)
                    self.assertGreaterEqual(row["ydstogo"], 6)
                if row["family"] == "Dagger":
                    self.assertIn(row["situation"], (cs.NORMAL, cs.THIRD_LONG), row)
                    self.assertFalse(row["down"] >= 3 and row["ydstogo"] <= 5, row)
        self.assertGreater(seen, 0)

    def test_opening_sequence_runs_in_script_order(self):
        positions = cs.script_positions(self.a.offensive_call_sheet)
        for r in self.games:
            rows = [row for row in scrimmage(r, "A") if not (row["kneel"] or row["spike"])]
            sent = set()
            for index, row in enumerate(rows):
                slot = row.get("script_position")
                if slot is None:
                    continue
                self.assertEqual(row["label_source"], "sheet:" + cs.OPENING)
                self.assertEqual(row["situation"], cs.NORMAL)
                self.assertLess(index, len(positions))
                self.assertNotIn(slot, sent)
                self.assertEqual(row["concept"], positions[slot]["name"])
                # Every lower unsent position is a call of the other snap type or
                # one whose declared groups exclude this snap's player; the strict
                # order itself is proven on the unconstrained script below.
                for lower in range(1, slot):
                    if lower in sent:
                        continue
                    call = positions[lower]
                    if row["play_type"] == "run" and not row["scramble"]:
                        self.assertTrue(call["type"] == "pass" or call.get("personnel")
                                        or row["carrier_group"] not in ("RB", "FB"), (lower, row))
                    else:
                        self.assertTrue(call["type"] == "run" or call.get("personnel"), (lower, row))
                sent.add(slot)
            self.assertLessEqual(len(sent), len(positions))

    def test_full_order_on_an_unconstrained_script(self):
        """With every opener call able to describe any snap, the script is
        sent 1, 2, 3, ... on the offense's first normal-down snaps."""
        calls = [{"name": "Opener %d" % n, "family": "Power", "type": "mixed",
                  "carrier": ["QB", "RB", "FB", "WR", "TE"], "target": "any",
                  "menus": ["normal down"], "opener": n} for n in range(1, 13)]
        a = team("A", calls)
        for i in range(6):
            r = resolve_game(a, self.b, seed=SEED + b"-ord%05d" % i, event_id="order-%d" % i)
            rows = [row for row in scrimmage(r, "A") if not (row["kneel"] or row["spike"])]
            sent = [row["script_position"] for row in rows if row.get("script_position") is not None]
            self.assertEqual(sent, list(range(1, len(sent) + 1)))
            normal = [row for row in rows[:12] if row["situation"] == cs.NORMAL]
            self.assertEqual(len(sent), len(normal))
            for row in rows[12:]:
                self.assertIsNone(row.get("script_position"))


class OutcomeInvarianceTests(unittest.TestCase):
    """The proof that 2014.5 is labelling only: the same seeded game under
    the 2014.4 uniform rule (the sheet without menus) and under the
    situational menus differs in nothing but the label fields."""

    def test_same_game_under_uniform_and_situational_labels(self):
        sheet = load_sheet(WEEK2)
        situational = team("A", sheet)
        uniform = team("A", uniform_sheet(sheet))
        b = team("B")

        def legal(t):
            return TeamInput(t.team_id, tuple(pid for pid in t.active_players if not pid.endswith("-CB5")),
                             roster=t.roster, offensive_call_sheet=t.offensive_call_sheet)
        self.assertEqual(build_game_packet("inv", "snapshot", legal(situational), legal(b)),
                         build_game_packet("inv", "snapshot", legal(uniform), legal(b)))
        differing_labels = 0
        for i in range(GAMES):
            seed = SEED + b"-inv%05d" % i
            first = resolve_game(uniform, b, seed=seed, event_id="invariance-%d" % i)
            second = resolve_game(situational, b, seed=seed, event_id="invariance-%d" % i)
            for key in ("final_score", "possessions", "kickoffs", "team_stats", "injuries",
                        "substitutions", "opening_receiver", "terminated"):
                self.assertEqual(first[key], second[key], key)
            self.assertEqual(strip_labels(first["play_ledger"]), strip_labels(second["play_ledger"]))
            for x, y in zip(first["play_ledger"], second["play_ledger"]):
                if x.get("play_type") in ("run", "pass") and x["offense"] == "A":
                    self.assertIn(x["label_source"], ("sheet", "generic", "kneel", "spike"))
                    differing_labels += x.get("concept") != y.get("concept")
            self.assertEqual(first["play_call_stats"]["B"], second["play_call_stats"]["B"])
        self.assertGreater(differing_labels, 0)


if __name__ == "__main__":
    unittest.main()
