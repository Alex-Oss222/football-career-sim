"""Kernel 2013.7 call labels follow the ball carrier and never move outcomes.

Club A in the shared sample carries Jacksonville's Week 6 call sheet (families
only; carriers and targets come from the committed 2013 call-family map) plus
label probes (see tests/synthetic_games.py). Synthetic seeds only.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import json
import unittest

from runtime import call_families
from runtime.game_runner import build_game_packet
from runtime.kernel import TeamInput, resolve_game, validate_result
from runtime.play_detail import canonical_call_sheet, check_ledger, coherence_counts
from synthetic_games import EVENT_PREFIX, SEED, TEAM_A_SHEET, WEEK6_SHEET, sample, sample_teams

LABEL_CLASSES = ("label_type_mismatch", "label_carrier_mismatch", "label_target_mismatch",
                 "scramble_with_designed_label", "kneel_spike_mislabelled")
ISOLATION_GAMES = 50


def rows(result, team):
    return [r for r in result["play_ledger"] if r["offense"] == team and r["play_type"] in ("pass", "run")]


class CallLabelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.games = sample()

    def test_week_sheets_resolve_through_the_family_map(self):
        root = Path(__file__).resolve().parents[1]
        for path in sorted((root / "career/2013/regular_season").glob("*/call_sheet.json")):
            self.assertEqual(call_families.sheet_errors(json.loads(path.read_text())["offensive_call_sheet"]), [], path)
        self.assertEqual(call_families.sheet_errors(WEEK6_SHEET), [])
        self.assertEqual(call_families.resolve({"family": "Jet Sweep", "type": "run"})[0], ("WR",))
        self.assertEqual(call_families.resolve({"family": "TE Delay", "type": "pass"})[1], ("TE",))
        self.assertEqual(call_families.resolve({"family": "Draw", "type": "run", "carrier": ["QB"]})[0], ("QB",))
        errors = call_families.sheet_errors([{"name": "Mystery", "family": "Mystery", "type": "run"},
                                             {"name": "Bad", "family": "Power", "type": "run", "carrier": ["OL"]}])
        self.assertEqual(len(errors), 2)
        self.assertIn("Mystery", errors[0])

    def test_labels_follow_carrier(self):
        counts = coherence_counts([e for r in self.games for e in check_ledger(r)])
        self.assertEqual({c: counts[c] for c in LABEL_CLASSES}, {c: 0 for c in LABEL_CLASSES})
        seen = {"Jet": 0, "TE Delay": 0, "RB Slow Screen": 0, "QB Draw": 0, "kneel": 0, "spike": 0}
        qb_carries = scrambles = 0
        for r in self.games:
            passer = {}
            for row in r["play_ledger"]:
                if row.get("play_type") == "pass" and row.get("passer"):
                    passer.setdefault(row["offense"], row["passer"])
            for row in rows(r, "A"):
                family, concept = row["family"], row["concept"]
                self.assertNotEqual(concept, "Unspecified probe")
                if family == "Jet Sweep":
                    seen["Jet"] += 1
                    self.assertEqual((row["play_type"], row["carrier_group"]), ("run", "WR"))
                if family == "TE Delay" and row["target"]:
                    seen["TE Delay"] += 1
                    self.assertEqual(row["target_group"], "TE")
                if family == "RB Slow Screen" and row["target"]:
                    seen["RB Slow Screen"] += 1
                    self.assertIn(row["target_group"], ("RB", "FB"))
                if concept == "QB Draw":
                    seen["QB Draw"] += 1
                    self.assertEqual(row["carrier_group"], "QB")
                    self.assertFalse(row["scramble"])
                if row["play_type"] == "run" and row["carrier_group"] == "QB" and not row["kneel"]:
                    qb_carries += 1
                    scrambles += row["scramble"]
                    if not row["scramble"]:
                        self.assertIn(concept, ("QB Draw", "Generic Run"))
                if row["kneel"]:
                    seen["kneel"] += 1
                    self.assertEqual((row["concept"], row["runner"]), ("Victory (kneel)", passer.get("A", row["runner"])))
                if row["spike"]:
                    seen["spike"] += 1
                    self.assertIsNone(row["target"])
                    self.assertEqual(row["concept"], "Clock (spike)")
            for row in rows(r, "B"):
                self.assertIn(row["label_source"], ("generic", "kneel", "spike"))
        self.assertTrue(all(seen.values()), seen)
        # Reported, not graded: 2012 nflverse 681/1,223 = 0.557 (nflscrapR 0.524).
        print("\n[2013.7 sample] QB scramble share of club A QB carries: %d/%d = %.3f"
              % (scrambles, qb_carries, scrambles / qb_carries))

    def test_declarations_and_names_do_not_move_outcomes(self):
        changed = []
        for call in reversed(TEAM_A_SHEET):
            call = dict(call)
            call["name"] = "Renamed " + call["name"]
            if call["family"] == "Stick":
                call["target"] = ["WR", "TE"]
            if call["family"] == "Power":
                call["carrier"] = ["RB"]
            changed.append(call)
        changed.append(dict(changed[0], name="Duplicate listing"))
        a, b = sample_teams()
        x = TeamInput("A", a.active_players, roster=a.roster, offensive_call_sheet=tuple(changed))
        self.assertEqual(canonical_call_sheet(x), canonical_call_sheet(a))
        self.assertFalse([row for row in canonical_call_sheet(x) if {"carrier", "target", "name"} & set(row)])
        self.assertEqual(build_game_packet("iso", "snapshot", x, b), build_game_packet("iso", "snapshot", a, b))
        for i in range(ISOLATION_GAMES):
            first = self.games[i]
            second = resolve_game(x, b, seed=SEED + b"-%05d" % i, event_id=f"{EVENT_PREFIX}-{i}")
            self.assertEqual(first["possessions"], second["possessions"])
            self.assertEqual(first["kickoffs"], second["kickoffs"])
            self.assertEqual(first["team_stats"], second["team_stats"])
            self.assertEqual(validate_result(second), [])
        self.assertNotEqual(first["play_call_stats"], second["play_call_stats"])


if __name__ == "__main__":
    unittest.main()
