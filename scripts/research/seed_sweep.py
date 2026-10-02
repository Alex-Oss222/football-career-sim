#!/usr/bin/env python3
"""The autonomous seed sweep, committed (kernel 2014.6 batch B1).

Resolves synthetic games through runtime.kernel.resolve_game with kernel
entropy derived exactly as the production runner derives it from an opaque
event reference (runtime.game_runner._entropy_from_ref over sha256 of the
label; the label is the event id), over the three synthetic fixtures of the
October 1, 2026 sweep:

  single  tests/support_rosters.py single_quarterback_teams(): one
          quarterback, one unavailable receiver, a 46-man legal unit on
          both clubs
  pause   tests/test_chains.py pause_teams(): clubs A and B without their WR5
  sample  tests/synthetic_games.py sample_teams(): the 250-game sample's
          clubs (A with the Week 6 call sheet and its label probes)

Two label blocks:

  a6          the kernel 2014.6 acceptance sweep frozen in
              library/2014_6_pre_build_specification.md (section 6, A6):
              sweep-2014.6-<fixture>-<i>, i = 0..3999 per fixture, 12,000
              games, gate 0 refused games. Its labels are fresh: the block
              runs only under the kernel 2014.6 profile, so no result of a
              label is seen under another kernel first.
  october-1   the October 1, 2026 sweep (its regressions are the forced
              fixtures of tests/test_chains.py SeedSweepRegressionTests):
              sweep-<i> and sw2-<i> (single), pz-<i> (pause), samp-<i>
              (sample), i = 0..2999, 12,000 games.

A game is refused when resolve_game raises or validate_result returns an
error (the production runner refuses both). The summary counts refused
games and the layout diagnostics; nothing is written unless --out names a
file. Synthetic seeds only: no private service, no career state.

  python scripts/research/seed_sweep.py --block a6 --jobs 4        # once the 2014.6 base is built
  python scripts/research/seed_sweep.py --block october-1 --jobs 4
  python scripts/research/seed_sweep.py --block october-1 --count 25
"""
from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT, ROOT / "tests"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

FIXTURES = ("single", "pause", "sample")
# Block: (fixture of each label prefix, labels per prefix, kernel profile it is reserved for or None).
BLOCKS = {
    "a6": ({"sweep-2014.6-single": "single", "sweep-2014.6-pause": "pause", "sweep-2014.6-sample": "sample"},
           4000, "2014.6"),
    "october-1": ({"sweep": "single", "sw2": "single", "pz": "pause", "samp": "sample"}, 3000, None),
}
DIAGNOSTICS = ("chain_layout_failed", "chain_layout_resampled", "chain_layout_resample_exhausted",
               "chain_plan_concentrated", "fallback_zero_tuple")


def fixture(name):
    """(home, away) TeamInputs of one of the sweep's three fixtures."""
    if name == "single":
        from support_rosters import single_quarterback_teams
        return single_quarterback_teams()
    if name == "pause":
        from test_chains import pause_teams
        return pause_teams()
    if name == "sample":
        from synthetic_games import sample_teams
        return sample_teams()
    raise ValueError("unknown sweep fixture %r" % (name,))


def entropy(label):
    """Kernel entropy as runtime.game_runner.run_game derives it."""
    from runtime.game_runner import _entropy_from_ref
    return _entropy_from_ref(hashlib.sha256(label.encode()).hexdigest())


def labels(block, count=None, start=0):
    """[(label, fixture)] of a block, in prefix then index order."""
    prefixes, per_prefix, _ = BLOCKS[block]
    stop = per_prefix if count is None else min(per_prefix, start + count)
    return [("%s-%d" % (prefix, i), name) for prefix, name in prefixes.items() for i in range(start, stop)]


def play(job):
    label, name, version = job
    from runtime.kernel import resolve_game, validate_result
    from runtime.profiles import profile_for
    home, away = fixture(name)
    try:
        result = resolve_game(home, away, seed=entropy(label), event_id=label, _test_profile=profile_for(version))
    except Exception as exc:  # a refused game is the finding, not a crash of the sweep
        return {"label": label, "refused": ["%s: %s" % (type(exc).__name__, exc)], "diagnostics": {}}
    errors = validate_result(result)
    return {"label": label, "refused": errors[:5],
            "diagnostics": {k: result["diagnostics"].get(k, 0) for k in DIAGNOSTICS}}


def sweep(jobs_list, version, jobs=1):
    work = [(label, name, version) for label, name in jobs_list]
    if jobs > 1:
        with multiprocessing.Pool(jobs) as pool:
            rows = pool.map(play, work, chunksize=8)
    else:
        rows = [play(job) for job in work]
    refused = [row for row in rows if row["refused"]]
    totals = {k: sum(row["diagnostics"].get(k, 0) for row in rows) for k in DIAGNOSTICS}
    return {"kernel_profile": version, "games": len(rows), "refused_games": len(refused),
            "refused": refused, "diagnostics": totals}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--block", choices=sorted(BLOCKS), default="a6")
    parser.add_argument("--count", type=int, help="labels per prefix (default: the whole block)")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--profile", default=None,
                        help="kernel profile version (default: the block's reserved profile, else KERNEL_VERSION)")
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--out", type=Path, help="write the JSON summary here")
    args = parser.parse_args()
    from runtime import KERNEL_VERSION
    from runtime.calibration_base import CalibrationBaseError
    from runtime.profiles import profile_for
    reserved = BLOCKS[args.block][2]
    version = args.profile or reserved or KERNEL_VERSION
    if reserved is not None and version != reserved:
        parser.error("block %s is reserved for kernel profile %s (its labels are fresh)" % (args.block, reserved))
    try:
        profile_for(version).calibration_base().require()
    except (CalibrationBaseError, ValueError) as exc:
        print("seed sweep, block %s, kernel profile %s: BLOCKED (%s)" % (args.block, version, exc))
        return 2
    summary = sweep(labels(args.block, args.count, args.start), version, args.jobs)
    summary["block"] = args.block
    text = json.dumps(summary, indent=1, sort_keys=True)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
    print("seed sweep, block %s, kernel profile %s: %d games, %d refused; %s" % (
        args.block, version, summary["games"], summary["refused_games"],
        ", ".join("%s %d" % item for item in sorted(summary["diagnostics"].items()))))
    for row in summary["refused"][:20]:
        print("- %s: %s" % (row["label"], "; ".join(row["refused"])))
    return 1 if summary["refused_games"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
