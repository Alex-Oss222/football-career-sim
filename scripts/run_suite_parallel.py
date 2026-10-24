#!/usr/bin/env python3
"""Run the full unittest suite one test module per process, several at a time,
and prove the run covered the same tests as `python -m unittest discover -s tests`.

Usage:
    python scripts/run_suite_parallel.py [REPO_DIR] [--jobs N] [--out LOG_DIR] [--shard I/N]

- Discovers the suite exactly as `discover -s tests` does and records its test
  count.
- Runs every tests/test_*.py module verbosely in its own process: working
  directory the repository root, with tests/ and the root on PYTHONPATH so the
  module imports what it imports under the serial discover, and a private
  TMPDIR removed afterwards. Modules
  start longest first, by the durations recorded on the previous run in this
  checkout (kept in the system temp directory, never in the repository).
- `--jobs` defaults to the machine's CPU count, at least 1 and at most 4; a
  value given on the command line is used as given.
- A module that fails is rerun alone, serially, after the parallel pass. One
  that fails in parallel and passes alone is reported as INTERFERENCE (a shared
  resource collision, not a code failure); the verdict uses the rerun.
- VERDICT OK only when every module passes (alone, if it was rerun) and the
  summed test count equals the discovered count. Exit code 0 on OK, 1
  otherwise. The verbose log of every failed module is printed; all logs stay in
  LOG_DIR.
- `--shard I/N` runs only shard I of N (CI runs the N shards on separate
  machines). The modules are split by longest first onto the least-loaded
  shard, by the durations committed in tests/suite_durations.json (a module
  not in it counts its file size in kilobytes as seconds), so every module
  falls in exactly one shard. A shard's count check is the discovered count of
  its own modules.
- When git and the checkout's .git are both present, any change to
  `git status` across the run is reported as a warning. Without them (inside
  the engine image build) the check is skipped with a note.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

RAN = re.compile(r"^Ran (\d+) tests? in", re.M)
MAX_DEFAULT_JOBS = 4


def default_jobs():
    return max(1, min(MAX_DEFAULT_JOBS, os.cpu_count() or 1))


def durations_path(repo):
    """Per-checkout durations file in the system temp directory."""
    key = hashlib.sha256(repo.encode("utf-8")).hexdigest()[:16]
    return os.path.join(tempfile.gettempdir(), "suite_module_durations_%s.json" % key)


def discovered_count(repo):
    code = ("import unittest; s=unittest.TestLoader().discover('tests'); "
            "print(s.countTestCases())")
    out = subprocess.run([sys.executable, "-c", code], cwd=repo, capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit("discovery failed:\n" + out.stderr[-4000:])
    return int(out.stdout.strip().splitlines()[-1])


def test_modules(repo):
    return sorted(f[:-3] for f in os.listdir(os.path.join(repo, "tests"))
                  if f.startswith("test_") and f.endswith(".py"))


COMMITTED_DURATIONS = os.path.join("tests", "suite_durations.json")


def parse_shard(text):
    """'I/N' -> (I, N), with 1 <= I <= N."""
    m = re.fullmatch(r"(\d+)/(\d+)", text or "")
    if not m or not 1 <= int(m.group(1)) <= int(m.group(2)):
        raise ValueError("--shard takes I/N with 1 <= I <= N, got %r" % text)
    return int(m.group(1)), int(m.group(2))


def shard_modules(mods, weights, index, count):
    """The modules of shard `index` (1-based) of `count`: longest first onto the least-loaded shard."""
    load = [0.0] * count
    owner = {}
    for m in sorted(mods, key=lambda m: (-weights[m], m)):
        i = min(range(count), key=lambda k: (load[k], k))
        load[i] += weights[m]
        owner[m] = i + 1
    return sorted(m for m in mods if owner[m] == index)


def modules_count(repo, mods):
    """Tests in these modules, loaded as `discover -s tests` loads them."""
    code = ("import sys, unittest; sys.path[:0] = ['tests', '.']; l = unittest.TestLoader(); "
            "print(sum(l.loadTestsFromName(m).countTestCases() for m in sys.argv[1:]))")
    out = subprocess.run([sys.executable, "-c", code] + list(mods), cwd=repo,
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit("loading the shard failed:\n" + out.stderr[-4000:])
    return int(out.stdout.strip().splitlines()[-1])


def run_module(repo, mod, log_dir, suffix=""):
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [os.path.join(repo, "tests"), repo, env.get("PYTHONPATH", "")]).rstrip(os.pathsep)
    tmp = tempfile.mkdtemp(prefix="suite_%s_" % mod)
    env["TMPDIR"] = tmp
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, "-m", "unittest", "-v", mod], cwd=repo,
                           env=env, capture_output=True, text=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    dt = time.time() - t0
    text = p.stdout + p.stderr
    log = os.path.join(log_dir, mod + suffix + ".log")
    with open(log, "w") as fh:
        fh.write(text)
    m = RAN.search(text)
    return {"module": mod, "rc": p.returncode, "ran": int(m.group(1)) if m else 0,
            "seconds": round(dt, 1), "ok": p.returncode == 0 and bool(m), "log": log}


def git_status(repo):
    """`git status --porcelain`, or None when git or the checkout's .git is absent."""
    if shutil.which("git") is None or not os.path.exists(os.path.join(repo, ".git")):
        return None
    p = subprocess.run(["git", "status", "--porcelain"], cwd=repo, capture_output=True, text=True)
    return p.stdout if p.returncode == 0 else None


def load_durations(path):
    try:
        with open(path) as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def save_durations(path, prev, results):
    durs = dict(prev)
    durs.update({r["module"]: r["seconds"] for r in results})
    try:
        with open(path, "w") as fh:
            json.dump(durs, fh, indent=1, sort_keys=True)
    except OSError:
        pass


def verdict(final, expected, only=False):
    """(ok, total, failed) from each module's final result."""
    total = sum(r["ran"] for r in final.values())
    failed = sorted(m for m, r in final.items() if not r["ok"])
    return (not failed and (total == expected or bool(only))), total, failed


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("--jobs", type=int, default=None,
                    help="parallel modules (default: CPU count, at least 1, at most 4)")
    ap.add_argument("--out", default=None, help="log directory (default: a new temp directory)")
    ap.add_argument("--durations", default=None,
                    help="durations file (default: per-checkout file in the system temp directory)")
    ap.add_argument("--shard", default=None, help="I/N: run shard I of N only")
    ap.add_argument("--only", nargs="*", default=None,
                    help="testing the runner: these modules only (no count check)")
    a = ap.parse_args(argv)
    jobs = a.jobs if a.jobs is not None else default_jobs()
    if jobs < 1:
        ap.error("--jobs must be at least 1")
    repo = os.path.abspath(a.repo)
    log_dir = a.out or tempfile.mkdtemp(prefix="suite_logs_")
    os.makedirs(log_dir, exist_ok=True)
    durations = a.durations or durations_path(repo)
    before = git_status(repo)
    expected = discovered_count(repo)
    mods = test_modules(repo)
    size = {m: os.path.getsize(os.path.join(repo, "tests", m + ".py")) for m in mods}
    if a.shard:
        try:
            index, count = parse_shard(a.shard)
        except ValueError as exc:
            ap.error(str(exc))
        committed = load_durations(os.path.join(repo, COMMITTED_DURATIONS))
        weights = {m: float(committed.get(m, size[m] / 1000.0)) for m in mods}
        mods = shard_modules(mods, weights, index, count)
        expected = modules_count(repo, mods)
    if a.only:
        mods = [m for m in mods if m in a.only]
    prev = load_durations(durations)
    mods.sort(key=lambda m: (-prev.get(m, size[m] / 1000.0), m))
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=jobs) as ex:
        results = list(ex.map(lambda m: run_module(repo, m, log_dir), mods))
    wall = time.time() - t0
    rerun = {}
    for r in results:
        if not r["ok"]:
            rerun[r["module"]] = run_module(repo, r["module"], log_dir, ".alone")
    final = {r["module"]: (rerun.get(r["module"]) or r) for r in results}
    ok, total, failed = verdict(final, expected, a.only)
    interference = sorted(m for m in rerun if rerun[m]["ok"])
    save_durations(durations, prev, results)
    after = git_status(repo) if before is not None else None
    if a.shard:
        print("shard %s: %d of %d modules" % (a.shard, len(mods), len(test_modules(repo))))
    print("modules: %d, jobs: %d, wall: %.0f s" % (len(mods), jobs, wall))
    print("tests run: %d, discovered: %d" % (total, expected))
    for r in sorted(results, key=lambda r: -r["seconds"])[:8]:
        print("  slowest: %-45s %7.1f s" % (r["module"], r["seconds"]))
    if interference:
        print("INTERFERENCE (failed in parallel, passed alone): " + ", ".join(interference))
    for m in failed:
        with open(final[m]["log"]) as fh:
            print("===== %s (failed alone) =====\n%s" % (m, fh.read()))
    if failed:
        print("FAILED modules: " + ", ".join(failed) + "  (logs in %s)" % log_dir)
    if a.only:
        print("count check skipped (--only)")
    if before is None:
        print("note: git status check skipped (git or the checkout's .git is absent)")
    elif after != before:
        print("WARNING: git status changed during the run:\n" + (after or ""))
    print("VERDICT: %s" % ("OK" if ok else "FAILED"))
    print("logs: %s" % log_dir)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
