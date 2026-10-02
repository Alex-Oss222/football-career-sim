"""Kernel 2014.6 batch B0: the frozen pre-build specification and the
read-only release preconditions (library/2014_6_pre_build_specification.md,
scripts/research/pre_build_specification.py,
scripts/research/release_preconditions_2014_6.py).

No network, no source data, no draw, no service call.
"""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


specification = load("pre_build_specification", "scripts/research/pre_build_specification.py")
VOID_FIRST_ISSUE = "2ce1018dee17052aa9e59bff8e80b2639f085376dd91310210417cb9aa53d70d"
preconditions = load("release_preconditions_2014_6", "scripts/research/release_preconditions_2014_6.py")


class FrozenSpecificationTests(unittest.TestCase):
    def test_file_is_frozen_and_consistent(self):
        self.assertEqual(specification.check(), [])

    def test_digest_is_the_pin(self):
        self.assertEqual(specification.digest(), specification.FROZEN_SHA256)
        self.assertRegex(specification.FROZEN_SHA256, r"^[0-9a-f]{64}$")
        # The first B0 issue (U5 recorded as a default) is void.
        self.assertNotEqual(specification.FROZEN_SHA256, VOID_FIRST_ISSUE)
        self.assertIn(VOID_FIRST_ISSUE, specification.SPEC.read_text(encoding="utf-8"))

    def test_an_edit_breaks_the_pin(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "spec.md"
            copy.write_bytes(specification.SPEC.read_bytes() + b"\n")
            self.assertTrue(any("never edited" in e for e in specification.check(copy)))

    def test_disclosed_as_not_blind(self):
        text = specification.SPEC.read_text(encoding="utf-8")
        self.assertTrue(text.startswith(specification.TITLE + "\n"))
        self.assertIn("**not a blind preregistration**", text)
        self.assertIs(specification.frozen_rules()["blind"], False)

    def test_information_gate(self):
        window = specification.frozen_rules()["data_window"]
        cut = window["cut_2014"]
        self.assertEqual((cut["max_week"], cut["max_game_date"], cut["games"]), (4, "2014-09-29", 61))
        self.assertEqual(cut["games_by_week"], [16, 16, 16, 13])
        self.assertEqual(window["public_from"], "2014-09-30")
        self.assertEqual(window["frozen_at"]["date"], "2014-10-02")
        self.assertEqual(max(window["seasons"]), 2014)
        self.assertIn("stats_player_reg_*", window["refused"])
        self.assertNotIn("position", window["players_columns"])

    def test_needs_partition_and_late_edges(self):
        eoh = specification.frozen_rules()["end_of_half"]
        for diff in range(-60, 61):
            hits = [n for n, (lo, hi) in eoh["NEEDS"].items() if lo <= diff <= hi]
            self.assertEqual(len(hits), 1, diff)
        self.assertEqual(eoh["NEEDS"]["trail9_11"], [-11, -9])
        self.assertEqual(eoh["NEEDS"]["trail12_16"], [-16, -12])
        self.assertEqual(eoh["NEEDS"]["trail17p"][1], -17)
        self.assertEqual((eoh["TIME_MATCH_SECONDS"], eoh["TIME_MATCH_FALLBACK_SECONDS"]), (40, 80))
        self.assertEqual((eoh["EARLY_FG_SECONDS"], eoh["SPIKE_WINDOW"]), (43, 148))

    def test_decisions_in_force(self):
        rules = specification.frozen_rules()
        self.assertIs(rules["emphasis_2014"]["completion_tilt"], False)
        self.assertEqual(rules["emphasis_2014"]["persist_through_week"], 17)
        self.assertEqual(rules["weighting"]["recency_half_life"], None)
        self.assertEqual(rules["context"]["altitude_slope"], 0)
        self.assertEqual(rules["player_state"]["feedback_in_2014"], 0)
        self.assertIn("every club", rules["player_state"]["draft_slot"])

    def test_u2_covers_the_regular_season_only(self):
        # Stone was told the emphasis level "holds through Week 17"; the
        # postseason was not put to him and fails closed until he answers.
        emphasis = specification.frozen_rules()["emphasis_2014"]
        self.assertEqual(emphasis["game_types_on"], ["regular"])
        self.assertEqual(emphasis["game_types_undecided"], ["postseason"])
        self.assertIn("fail closed", emphasis["undecided_game_type"])
        rules = specification.frozen_rules()
        rules["emphasis_2014"]["game_types_on"] = ["regular", "postseason"]
        self.assertTrue(any("postseason" in e for e in specification.rule_errors(rules)))

    def test_u5_is_unanswered_and_its_rules_conditional(self):
        state = specification.frozen_rules()["player_state"]
        self.assertEqual(state["u5"], "unanswered")
        self.assertIn("aging_two_pass_conjunction", state["u5_conditional"])
        self.assertIn("draft_slope_negative_sign", state["u5_conditional"])
        self.assertEqual(state["u5_fallback"]["draft_slope"], 0)
        self.assertEqual(state["u5_fallback"]["other_conditional_rules"], "held")
        text = specification.SPEC.read_text(encoding="utf-8")
        self.assertIn("the defaults U2 to U4 and U7", text)
        self.assertNotIn("U2 to U5", text)
        rules = specification.frozen_rules()
        del rules["player_state"]["u5_fallback"]
        self.assertTrue(specification.rule_errors(rules))

    def test_u6_basis_admits_a_live_answer(self):
        scoring = specification.frozen_rules()["scoring"]
        self.assertEqual(scoring["basis_values"], ["policy:i", "delegated:league", "live", "league"])
        self.assertNotIn("league", scoring["controlled_club_basis"])
        rules = specification.frozen_rules()
        rules["scoring"]["basis_values"].remove("live")
        self.assertTrue(specification.rule_errors(rules))

    def test_pins_name_what_they_cover(self):
        window = specification.frozen_rules()["data_window"]
        self.assertNotIn("nflscrapr_reg_pbp_sha256", window)
        self.assertEqual(sorted(window["nflscrapr_reg_pbp_fetch_sha256"]), ["2010", "2011", "2012", "2013", "2014"])
        self.assertIn("in memory before the cut", window["pins_cover"])

    def test_seed_blocks_are_fresh(self):
        seeds = specification.frozen_rules()["seeds"]
        self.assertEqual(seeds["acceptance"], {"prefix": "acc-2014.6-", "count": 1000})
        self.assertEqual(seeds["extended"], {"prefix": "acc-2014.6-x", "count": 2000})
        self.assertEqual(seeds["sweep"]["games"], 12000)
        self.assertEqual(seeds["latent_references"], {"prefix": "latref-", "count": 20})
        # The sweep's three fixtures are the October 1 sweep's, named now.
        self.assertEqual(sorted(seeds["sweep"]["fixture_tokens"]), ["pause", "sample", "single"])
        for source in seeds["sweep"]["fixture_tokens"].values():
            module, function = source.split()
            self.assertIn("def %s(" % function, (ROOT / module).read_text(encoding="utf-8"))
        # The standard sample and the October 1 sweep use other labels.
        for used in ("synthetic", "identity-", "sweep-0", "sw2-", "pz-", "samp-"):
            for key in ("acceptance", "extended", "latent_references"):
                self.assertFalse(seeds[key]["prefix"].startswith(used))

    def test_rule_errors_catch_a_broken_block(self):
        rules = specification.frozen_rules()
        rules["end_of_half"]["NEEDS"]["trail9_11"] = [-12, -9]
        self.assertTrue(specification.rule_errors(rules))


def season_root(tmp):
    root = Path(tmp)
    paths = preconditions.SeasonPaths(2014, root)
    paths.receipts.mkdir(parents=True)
    paths.week_folder(5).mkdir(parents=True)
    return root, paths


class ReleasePreconditionTests(unittest.TestCase):
    def test_repository_holds_before_the_flip(self):
        # A precondition of the 2014.6 release only: after the flip the Week 5
        # sheet and package are frozen by design.
        from runtime import KERNEL_VERSION
        if KERNEL_VERSION != "2014.5":
            self.skipTest("kernel 2014.6 released; the release preconditions no longer apply")
        result = preconditions.report(ROOT, 2014, 5)
        self.assertTrue(result["ok"], result)
        # The service journal is never visible here: the check is unverified,
        # never a pass on no evidence, and release mode refuses it.
        journal = result["checks"][1]
        self.assertEqual(journal["status"], "unverified", journal)
        self.assertFalse(preconditions.report(ROOT, 2014, 5, release=True)["ok"])
        slate = result["checks"][3]
        self.assertEqual(slate["status"], "pass", slate)

    def test_clean_root_holds(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _ = season_root(tmp)
            self.assertTrue(preconditions.report(root)["ok"])

    def test_release_mode_fails_on_unverified_journal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _ = season_root(tmp)
            result = preconditions.report(root, release=True)
            self.assertFalse(result["ok"])
            self.assertEqual(result["checks"][1]["status"], "unverified")
            self.assertEqual(result["checks"][1]["findings"], [])

    def test_journal_listing_is_compared_both_ways(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, paths = season_root(tmp)
            (paths.receipts / "r.json").write_text(json.dumps({"event_id": "2014-week05-a-at-b"}))
            listing = Path(tmp) / "journal.json"

            def check(events):
                listing.write_text(json.dumps(events))
                return preconditions.report(root, journal=listing, release=True)

            result = check(["2014-week05-a-at-b", {"event_id": "2014-week05-c-at-d"}, "2013-week01-x-at-y"])
            self.assertFalse(result["ok"])
            self.assertEqual(result["checks"][1]["findings"],
                             ["journal event 2014-week05-c-at-d has no public receipt"])
            self.assertTrue(check({"events": ["2014-week05-a-at-b"]})["ok"])
            truncated = check([])
            self.assertFalse(truncated["ok"])
            self.assertIn("incomplete listing", truncated["checks"][1]["findings"][0])
            listing.write_text("{not json")
            unreadable = preconditions.report(root, journal=listing)
            self.assertFalse(unreadable["ok"])
            self.assertIn("unreadable journal listing", unreadable["checks"][1]["findings"][0])

    def test_pending_pause_blocks_and_closed_record_does_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, paths = season_root(tmp)
            week4 = paths.week_folder(4)
            week4.mkdir(parents=True)
            record = week4 / "paused_game.json"
            record.write_text(json.dumps({"status": "paused", "event_id": "e"}))
            result = preconditions.report(root)
            self.assertFalse(result["ok"])
            self.assertEqual(result["checks"][0]["findings"], [record.relative_to(root.resolve()).as_posix()])
            record.write_text(json.dumps({"status": "closed", "event_id": "e"}))
            self.assertTrue(preconditions.report(root)["ok"])

    def test_cached_event_without_receipt_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, paths = season_root(tmp)
            paths.cache(4, "results").parent.mkdir(parents=True)
            paths.cache(4, "results").write_text(json.dumps({"e1": {}, "e2": {}}))
            (paths.receipts / "r1.json").write_text(json.dumps({"event_id": "e1"}))
            result = preconditions.report(root)
            self.assertFalse(result["ok"])
            self.assertEqual(len(result["checks"][1]["findings"]), 1)
            self.assertIn("e2", result["checks"][1]["findings"][0])
            # Matched by the event id the receipt carries, not by its file name.
            (paths.receipts / "any_name.json").write_text(json.dumps({"event_id": "e2"}))
            self.assertTrue(preconditions.report(root)["ok"])

    def test_preseason_cache_reads_preseason_receipts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, paths = season_root(tmp)
            cache = paths.preseason_cache(1, "results")
            cache.parent.mkdir(parents=True)
            cache.write_text(json.dumps({"p1": {}}))
            (paths.receipts / "r.json").write_text(json.dumps({"event_id": "p1"}))
            self.assertFalse(preconditions.report(root)["ok"])
            paths.preseason_receipts.mkdir(parents=True)
            (paths.preseason_receipts / "r.json").write_text(json.dumps({"event_id": "p1"}))
            self.assertTrue(preconditions.report(root)["ok"])

    def test_unreadable_cache_is_a_finding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, paths = season_root(tmp)
            paths.cache(3, "results").parent.mkdir(parents=True)
            paths.cache(3, "results").write_text("{not json")
            self.assertIn("unreadable", preconditions.report(root)["checks"][1]["findings"][0])

    def test_partly_published_slate_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, paths = season_root(tmp)
            games = [{"week": 1, "date": "2014-09-07", "away": "Away One", "home": "Home One"},
                     {"week": 1, "date": "2014-09-07", "away": "Away Two", "home": "Home Two"},
                     {"week": 2, "date": "2014-09-14", "away": "Away One", "home": "Home Two"}]
            paths.schedule.parent.mkdir(parents=True, exist_ok=True)
            paths.schedule.write_text(json.dumps({"season": 2014, "status": "RELEASED", "games": games}))

            def receipt(name, event_id, week=1):
                (paths.receipts / name).write_text(json.dumps({"event_id": event_id, "week": week}))

            receipt("a.json", "2014-week01-away-one-at-home-one")
            result = preconditions.report(root)
            self.assertFalse(result["ok"])
            self.assertEqual(result["checks"][3]["findings"],
                             ["Week 1: fixture 2014-week01-away-two-at-home-two has no receipt"])
            receipt("b.json", "2014-week01-away-two-at-home-two")
            self.assertTrue(preconditions.report(root)["ok"])
            receipt("c.json", "2014-week01-away-nine-at-home-one")
            self.assertIn("matches no fixture", preconditions.report(root)["checks"][3]["findings"][0])

    def test_frozen_week_inputs_block(self):
        for name in ("call_sheet.json", "conditions.json", None):
            with tempfile.TemporaryDirectory() as tmp:
                root, paths = season_root(tmp)
                if name:
                    (paths.week_folder(5) / name).write_text("{}")
                else:
                    paths.cache(5, "inputs").parent.mkdir(parents=True)
                    paths.cache(5, "inputs").write_text("{}")
                result = preconditions.report(root)
                self.assertFalse(result["ok"], name)
                self.assertEqual(len(result["checks"][2]["findings"]), 1)


if __name__ == "__main__":
    unittest.main()
