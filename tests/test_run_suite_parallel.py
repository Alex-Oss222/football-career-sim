"""The parallel suite runner's counting and verdict logic.

Every run here is against a tiny synthetic checkout in a temporary directory;
nothing invokes the repository's own suite.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from unittest import mock

from scripts import run_suite_parallel as runner

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_suite_parallel.py"

PASSING = """
    import unittest
    import synth_helper
    import synthpkg

    class Passing(unittest.TestCase):
        def test_helper_on_path(self):
            self.assertEqual(synth_helper.VALUE, 3)

        def test_root_package_on_path(self):
            self.assertEqual(synthpkg.NAME, "root")
"""
SKIPPING = """
    import unittest

    class Skipping(unittest.TestCase):
        def test_runs(self):
            self.assertTrue(True)

        @unittest.skip("synthetic skip")
        def test_skipped(self):
            pass
"""
FAILING = """
    import unittest

    class Failing(unittest.TestCase):
        def test_fails(self):
            self.assertEqual(1, 2)
"""
# Fails on its first run and passes on the next: the shape of a collision with
# a module running beside it.
FLAKY = """
    import unittest
    from pathlib import Path

    MARK = Path(__file__).resolve().parents[1] / "flaky.mark"

    class Flaky(unittest.TestCase):
        def test_second_run_passes(self):
            if not MARK.exists():
                MARK.write_text("first run")
                self.fail("first run fails")
"""
NESTED = """
    import unittest

    class Nested(unittest.TestCase):
        def test_found_by_discover_only(self):
            pass
"""
TOUCHES_TRACKED = """
    import unittest
    from pathlib import Path

    class Touches(unittest.TestCase):
        def test_rewrites_a_tracked_file(self):
            (Path(__file__).resolve().parents[1] / "tracked.txt").write_text("changed")
"""


class SyntheticCheckout:
    def __init__(self, base, modules, extra=None):
        self.path = Path(base) / "checkout"
        tests = self.path / "tests"
        tests.mkdir(parents=True)
        (tests / "synth_helper.py").write_text("VALUE = 3\n")
        (self.path / "synthpkg").mkdir()
        (self.path / "synthpkg" / "__init__.py").write_text('NAME = "root"\n')
        for name, body in modules.items():
            (tests / (name + ".py")).write_text(textwrap.dedent(body))
        for rel, body in (extra or {}).items():
            target = self.path / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(textwrap.dedent(body))
        self.logs = Path(base) / "logs"
        self.durations = Path(base) / "durations.json"

    def run(self, jobs=2, shard=None):
        env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
        extra = ["--shard", shard] if shard else []
        p = subprocess.run([sys.executable, str(SCRIPT), str(self.path), "--jobs", str(jobs),
                            "--out", str(self.logs), "--durations", str(self.durations)] + extra,
                           cwd=self.path, env=env, capture_output=True, text=True, timeout=120)
        return p.returncode, p.stdout + p.stderr


class RunnerRuns(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = tmp.name

    def test_all_modules_pass_and_the_count_matches_discovery(self):
        checkout = SyntheticCheckout(self.base, {"test_synth_pass": PASSING, "test_synth_skip": SKIPPING})
        rc, out = checkout.run()
        self.assertEqual(rc, 0, out)
        self.assertIn("modules: 2, jobs: 2", out)
        self.assertIn("tests run: 4, discovered: 4", out)
        self.assertIn("VERDICT: OK", out)
        self.assertIn("note: git status check skipped", out)
        self.assertNotIn("FAILED", out)
        # Verbose per-module logs, and the durations kept outside the checkout.
        self.assertIn("test_helper_on_path (test_synth_pass.Passing", (checkout.logs / "test_synth_pass.log").read_text())
        self.assertIn("skipped 'synthetic skip'", (checkout.logs / "test_synth_skip.log").read_text())
        self.assertEqual(sorted(json.loads(checkout.durations.read_text())), ["test_synth_pass", "test_synth_skip"])
        self.assertEqual(sorted(p.name for p in checkout.path.rglob("*.json")), [])

    def test_a_failing_module_fails_the_verdict_after_its_rerun_alone(self):
        checkout = SyntheticCheckout(self.base, {"test_synth_pass": PASSING, "test_synth_fail": FAILING})
        rc, out = checkout.run()
        self.assertEqual(rc, 1, out)
        self.assertIn("tests run: 3, discovered: 3", out)
        self.assertIn("FAILED modules: test_synth_fail", out)
        self.assertIn("===== test_synth_fail (failed alone) =====", out)
        self.assertIn("AssertionError: 1 != 2", out)
        self.assertNotIn("INTERFERENCE", out)
        self.assertTrue((checkout.logs / "test_synth_fail.alone.log").is_file())
        self.assertIn("VERDICT: FAILED", out)

    def test_a_module_that_passes_alone_is_interference_and_the_verdict_holds(self):
        checkout = SyntheticCheckout(self.base, {"test_synth_pass": PASSING, "test_synth_flaky": FLAKY})
        rc, out = checkout.run()
        self.assertEqual(rc, 0, out)
        self.assertIn("INTERFERENCE (failed in parallel, passed alone): test_synth_flaky", out)
        self.assertIn("tests run: 3, discovered: 3", out)
        self.assertNotIn("FAILED modules", out)
        self.assertIn("VERDICT: OK", out)

    def test_tests_the_runner_does_not_reach_fail_the_count(self):
        checkout = SyntheticCheckout(self.base, {"test_synth_pass": PASSING},
                                     {"tests/nested/__init__.py": "", "tests/nested/test_nested.py": NESTED})
        rc, out = checkout.run(jobs=1)
        self.assertEqual(rc, 1, out)
        self.assertIn("tests run: 2, discovered: 3", out)
        self.assertNotIn("FAILED modules", out)
        self.assertIn("VERDICT: FAILED", out)

    @unittest.skipUnless(shutil.which("git"), "git is not installed")
    def test_a_changed_tracked_file_is_reported_without_changing_the_verdict(self):
        checkout = SyntheticCheckout(self.base, {"test_synth_touch": TOUCHES_TRACKED},
                                     {"tracked.txt": "original"})
        git = ["git", "-c", "user.name=Synthetic", "-c", "user.email=synthetic@example.invalid",
               "-c", "commit.gpgsign=false"]
        for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "synthetic"]):
            subprocess.run(git + args, cwd=checkout.path, check=True, capture_output=True)
        rc, out = checkout.run()
        self.assertEqual(rc, 0, out)
        self.assertIn("WARNING: git status changed during the run", out)
        self.assertIn("tracked.txt", out)
        self.assertNotIn("git status check skipped", out)
        self.assertIn("VERDICT: OK", out)


    def test_the_shards_together_run_every_module_once_with_their_own_counts(self):
        modules = {"test_synth_pass": PASSING, "test_synth_skip": SKIPPING}
        checkout = SyntheticCheckout(self.base, modules, extra={
            "tests/suite_durations.json": '{"test_synth_pass": 10, "test_synth_skip": 5}'})
        seen = []
        for shard in ("1/2", "2/2"):
            rc, out = checkout.run(shard=shard)
            self.assertEqual(rc, 0, out)
            self.assertIn("shard %s: 1 of 2 modules" % shard, out)
            self.assertIn("tests run: 2, discovered: 2", out)
            self.assertIn("VERDICT: OK", out)
            seen += [m for m in modules if (checkout.logs / (m + ".log")).exists() and m not in seen]
        self.assertEqual(sorted(seen), sorted(modules))


class RunnerLogic(unittest.TestCase):
    def test_shards_split_longest_first_and_cover_every_module_once(self):
        weights = {"a": 10.0, "b": 9.0, "c": 4.0, "d": 3.0, "e": 1.0}
        parts = [runner.shard_modules(list(weights), weights, i, 3) for i in (1, 2, 3)]
        self.assertEqual(parts, [["a"], ["b"], ["c", "d", "e"]])
        self.assertEqual(sorted(sum(parts, [])), sorted(weights))
        self.assertEqual(runner.parse_shard("2/4"), (2, 4))
        for bad in ("0/4", "5/4", "2", "a/b", ""):
            with self.assertRaises(ValueError):
                runner.parse_shard(bad)

    def test_the_committed_durations_name_only_real_test_modules(self):
        committed = json.loads((ROOT / "tests" / "suite_durations.json").read_text())
        modules = set(runner.test_modules(str(ROOT)))
        self.assertTrue(set(committed) <= modules, sorted(set(committed) - modules))

    def test_verdict_needs_every_module_and_the_discovered_count(self):
        good = {"a": {"ran": 2, "ok": True}, "b": {"ran": 1, "ok": True}}
        self.assertEqual(runner.verdict(good, 3), (True, 3, []))
        self.assertEqual(runner.verdict(good, 4), (False, 3, []))
        self.assertEqual(runner.verdict(good, 4, only=["a", "b"]), (True, 3, []))
        bad = dict(good, b={"ran": 1, "ok": False})
        self.assertEqual(runner.verdict(bad, 3), (False, 3, ["b"]))
        self.assertEqual(runner.verdict(bad, 3, only=["a", "b"]), (False, 3, ["b"]))
        self.assertEqual(runner.verdict({}, 0), (True, 0, []))

    def test_default_jobs_is_the_cpu_count_between_one_and_four(self):
        for cpus, jobs in ((None, 1), (1, 1), (2, 2), (4, 4), (64, 4)):
            with mock.patch.object(runner.os, "cpu_count", return_value=cpus):
                self.assertEqual(runner.default_jobs(), jobs)

    def test_durations_live_in_the_temp_directory_not_the_checkout(self):
        path = Path(runner.durations_path(str(ROOT)))
        self.assertEqual(path.parent, Path(tempfile.gettempdir()))
        self.assertNotEqual(path, Path(runner.durations_path(str(ROOT / "elsewhere"))))
        self.assertFalse(str(path).startswith(str(ROOT) + os.sep))


if __name__ == "__main__":
    unittest.main()
