#!/usr/bin/env python3
"""Read-only release preconditions for kernel 2014.6 (plan batch B0).

The kernel flip must not strand a game across two kernels. Before release the
repository must show:

1. no pending E2 pause: no ``paused_game.json`` in any 2014 week, postseason or
   preseason folder unless it is the closed record of a finished game
   (``status: closed``); a pending pause would be continued under a different
   kernel than the one that drew its prefix;
2. no journaled-but-unreceipted 2014 event: every event in a local 2014 results
   cache (``.sim_cache/2014/week_NN_results.json`` and the preseason caches) has
   a public receipt carrying its event id (an unreadable cache is a finding);
3. the first 2014.6 week's inputs not frozen: no package
   (``.sim_cache/2014/week_NN_inputs.json``), no ``call_sheet.json`` and no
   ``conditions.json`` in that week's folder, because the 2014.6 sheet format
   and conditions exist only after the release.

It reads files only: it never calls the private Engine State service, draws,
writes or advances a snapshot. The service's own journal and pending state are
checked at release through its readiness endpoint (plan B18), not here.

  python scripts/research/release_preconditions_2014_6.py [--season 2014] [--week 5] [--root PATH] [--json]

Exit status 0 when every precondition holds, 1 otherwise.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from runtime.seasons import SeasonPaths  # noqa: E402


def _paused_records(paths):
    folders = [paths.regular_season, paths.postseason, paths.preseason_games_dir]
    seen = set()
    for folder in folders:
        if not folder.is_dir():
            continue
        for record in sorted(folder.rglob("paused_game.json")):
            if record not in seen:
                seen.add(record)
                yield record


def pause_findings(paths):
    blocking, closed = [], []
    for record in _paused_records(paths):
        rel = record.relative_to(paths.root).as_posix()
        try:
            status = json.loads(record.read_text(encoding="utf-8")).get("status")
        except (OSError, ValueError, AttributeError):
            status = None
        (closed if status == "closed" else blocking).append(rel)
    return blocking, closed


def receipted_events(folders):
    """Event ids carried by the public receipts in these folders."""
    found = set()
    for folder in folders:
        if not folder.is_dir():
            continue
        for receipt in sorted(folder.glob("*.json")):
            try:
                event_id = json.loads(receipt.read_text(encoding="utf-8")).get("event_id")
            except (OSError, ValueError, AttributeError):
                event_id = None
            if event_id:
                found.add(event_id)
    return found


def _results_caches(paths):
    cache = paths.root / ".sim_cache" / str(paths.year)
    if not cache.is_dir():
        return
    regular = [paths.receipts, paths.postseason_receipts]
    for results in sorted(cache.glob("week_*_results.json")):
        yield results, regular
    for results in sorted(cache.glob("preseason_*_results.json")):
        yield results, [paths.preseason_receipts]


def unreceipted_events(paths):
    """Events closed into a local results cache whose public receipt is missing.

    A receipt is matched by the event id it carries, so the check needs no
    frozen package.
    """
    findings = []
    for results_path, folders in _results_caches(paths):
        rel = results_path.relative_to(paths.root).as_posix()
        try:
            results = json.loads(results_path.read_text(encoding="utf-8"))
            events = sorted(results)
        except (OSError, ValueError, TypeError):
            findings.append("%s: unreadable results cache" % rel)
            continue
        receipted = receipted_events(folders)
        for event_id in events:
            if event_id not in receipted:
                findings.append("%s: event %s has no public receipt" % (rel, event_id))
    return findings


def frozen_week_inputs(paths, week):
    found = []
    package = paths.cache(week, "inputs")
    if package.exists():
        found.append(package.relative_to(paths.root).as_posix())
    folder = paths.week_folder(week)
    for name in ("call_sheet.json", "conditions.json"):
        if (folder / name).exists():
            found.append((folder / name).relative_to(paths.root).as_posix())
    return found


def report(root=ROOT, season=2014, week=5):
    paths = SeasonPaths(season, root)
    pending, closed = pause_findings(paths)
    unreceipted = unreceipted_events(paths)
    frozen = frozen_week_inputs(paths, week)
    checks = [
        {"check": "no pending paused_game.json", "ok": not pending, "findings": pending,
         "note": "closed records of finished games: %d" % len(closed)},
        {"check": "no journaled-but-unreceipted %d event (local caches)" % season, "ok": not unreceipted,
         "findings": unreceipted, "note": "the private store's journal is checked at release, not here"},
        {"check": "Week %d inputs not frozen" % week, "ok": not frozen, "findings": frozen, "note": ""},
    ]
    return {"season": season, "week": week, "ok": all(c["ok"] for c in checks), "checks": checks}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--season", type=int, default=2014)
    parser.add_argument("--week", type=int, default=5, help="first week to run on kernel 2014.6")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = report(args.root, args.season, args.week)
    if args.json:
        print(json.dumps(result, indent=1, sort_keys=True))
    else:
        for c in result["checks"]:
            print("%s: %s%s" % ("PASS" if c["ok"] else "FAIL", c["check"], (" (%s)" % c["note"]) if c["note"] else ""))
            for finding in c["findings"]:
                print("  - " + finding)
        print("Release preconditions %s." % ("hold" if result["ok"] else "do NOT hold"))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
