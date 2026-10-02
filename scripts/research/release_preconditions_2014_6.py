#!/usr/bin/env python3
"""Read-only release preconditions for kernel 2014.6 (plan batch B0).

The kernel flip must not strand a game across two kernels. Before release the
repository must show:

1. no pending E2 pause: no ``paused_game.json`` in any 2014 week, postseason or
   preseason folder unless it is the closed record of a finished game
   (``status: closed``); a pending pause would be continued under a different
   kernel than the one that drew its prefix;
2. no journaled-but-unreceipted 2014 event: every event in a local 2014 results
   cache (``.sim_cache/2014/week_NN_results.json`` and the preseason caches)
   and every event in the private service's journal listing (``--journal``)
   has a public receipt carrying its event id (an unreadable cache or listing
   is a finding); every committed receipt must also appear in the listing, so
   a truncated listing cannot clear the check;
3. the first 2014.6 week's inputs not frozen: no package
   (``.sim_cache/2014/week_NN_inputs.json``), no ``call_sheet.json`` and no
   ``conditions.json`` in that week's folder, because the 2014.6 sheet format
   and conditions exist only after the release;
4. no partly published slate, from committed data alone: every regular-season
   week with at least one receipt has a receipt for each of its fixtures in
   ``SeasonPaths(2014).schedule`` and no receipt outside them.

Check 2 is UNVERIFIED unless the service journal listing was compared. The
service's journal is not visible from the repository: no endpoint lists
journaled events (``/ready`` reports readiness and the snapshot-advance lock,
not events), and a cloud session normally has no ``.sim_cache``. The release
batch (plan B18) supplies a read-only listing of the service's closed event
ids as a JSON file (a list of event ids, or of objects with ``event_id``, or
``{"events": [...]}``) through ``--journal``. In the default mode UNVERIFIED is
reported and does not fail; ``--release`` turns it into a failure, so the
release cannot pass on an empty check.

It reads files only: it never calls the private Engine State service, draws,
writes or advances a snapshot.

  python scripts/research/release_preconditions_2014_6.py [--season 2014] [--week 5] [--root PATH]
      [--journal LISTING.json] [--release] [--json]

Exit status 0 when every precondition holds (in --release mode, only when
every check passes), 1 otherwise.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from runtime.seasons import SeasonPaths  # noqa: E402

PASS, FAIL, UNVERIFIED = "pass", "fail", "unverified"


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


def _receipts(folders):
    for folder in folders:
        if not folder.is_dir():
            continue
        for receipt in sorted(folder.glob("*.json")):
            try:
                row = json.loads(receipt.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                row = None
            yield receipt, row if isinstance(row, dict) else None


def receipted_events(folders):
    """Event ids carried by the public receipts in these folders."""
    return {row.get("event_id") for _, row in _receipts(folders) if row and row.get("event_id")}


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
    return _cache_check(paths)[0]


def _cache_check(paths):
    findings, caches = [], 0
    for results_path, folders in _results_caches(paths):
        caches += 1
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
    return findings, caches


def _journal_events(listing):
    data = json.loads(Path(listing).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data["events"]
    if not isinstance(data, list):
        raise ValueError("the journal listing must be a list of events")
    events = []
    for item in data:
        event_id = item.get("event_id") if isinstance(item, dict) else item
        if not isinstance(event_id, str) or not event_id:
            raise ValueError("journal listing entry without an event id")
        events.append(event_id)
    return events


def journal_findings(paths, listing):
    """Events of this season in the service's journal listing without a receipt."""
    try:
        events = _journal_events(listing)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return ["%s: unreadable journal listing (%s)" % (listing, exc)], 0
    season = set(e for e in events if e.startswith("%d-" % paths.year))
    receipted = receipted_events([paths.receipts, paths.postseason_receipts, paths.preseason_receipts])
    findings = ["journal event %s has no public receipt" % e for e in sorted(season - receipted)]
    # Every committed receipt was closed through the service, so a listing
    # missing one is truncated or of the wrong store: it cannot clear the check.
    findings += ["receipt %s is absent from the journal listing (incomplete listing)" % e
                 for e in sorted(receipted - season)]
    return findings, len(season)


def journal_check(paths, listing=None):
    """Check 2: local caches always; the service journal listing when supplied."""
    findings, caches = _cache_check(paths)
    notes = ["local results caches: %d" % caches]
    if listing is not None:
        journal, events = journal_findings(paths, listing)
        findings += journal
        notes.append("service journal listing compared: %d %d events" % (events, paths.year))
    else:
        notes.append("service journal not compared (no --journal listing)")
    status = FAIL if findings else (PASS if listing is not None else UNVERIFIED)
    return status, findings, "; ".join(notes)


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


def _slug(team):
    return re.sub(r"[^a-z0-9]+", "-", team.lower()).strip("-")


def _generation(paths, week):
    if not paths.generations.exists():
        return 1
    weeks = json.loads(paths.generations.read_text(encoding="utf-8")).get("weeks", {})
    return int(weeks.get(str(int(week)), {}).get("current_generation", 1))


def fixture_event_id(paths, game):
    """The event id a fixture's receipt carries (runtime.week_inputs.event_id)."""
    base = "%d-week%02d-%s-at-%s" % (paths.year, game["week"], _slug(game["away"]), _slug(game["home"]))
    generation = _generation(paths, game["week"])
    return base if generation == 1 else "%s-g%d" % (base, generation)


def slate_findings(paths):
    """Committed data only: each regular-season week with a receipt is complete."""
    by_week = {}
    for receipt, row in _receipts([paths.receipts]):
        week = row.get("week") if row else None
        if isinstance(week, int) and not isinstance(week, bool):
            by_week.setdefault(week, set()).add(row.get("event_id"))
    if not by_week:
        return [], 0
    try:
        games = paths.regular_games()
    except (OSError, ValueError, KeyError) as exc:
        return ["%d schedule unreadable (%s)" % (paths.year, exc)], len(by_week)
    findings = []
    for week in sorted(by_week):
        expected = {fixture_event_id(paths, g) for g in games if g["week"] == week}
        if not expected:
            continue  # not a regular-season fixture week
        for event_id in sorted(expected - by_week[week]):
            findings.append("Week %d: fixture %s has no receipt" % (week, event_id))
        for event_id in sorted(e for e in by_week[week] - expected if e):
            findings.append("Week %d: receipt %s matches no fixture" % (week, event_id))
    return findings, len(by_week)


def report(root=ROOT, season=2014, week=5, journal=None, release=False):
    paths = SeasonPaths(season, root)
    pending, closed = pause_findings(paths)
    journal_status, unreceipted, journal_note = journal_check(paths, journal)
    frozen = frozen_week_inputs(paths, week)
    slate, weeks = slate_findings(paths)

    def status(findings):
        return FAIL if findings else PASS

    checks = [
        {"check": "no pending paused_game.json", "status": status(pending), "findings": pending,
         "note": "closed records of finished games: %d" % len(closed)},
        {"check": "no journaled-but-unreceipted %d event" % season, "status": journal_status,
         "findings": unreceipted, "note": journal_note},
        {"check": "Week %d inputs not frozen" % week, "status": status(frozen), "findings": frozen, "note": ""},
        {"check": "no partly published %d slate (committed receipts against the schedule)" % season,
         "status": status(slate), "findings": slate, "note": "weeks with receipts: %d" % weeks},
    ]
    for c in checks:
        c["ok"] = c["status"] == PASS or (c["status"] == UNVERIFIED and not release)
    return {"season": season, "week": week, "release": release,
            "ok": all(c["ok"] for c in checks), "checks": checks}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--season", type=int, default=2014)
    parser.add_argument("--week", type=int, default=5, help="first week to run on kernel 2014.6")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--journal", type=Path, help="read-only listing of the service's closed event ids (B18)")
    parser.add_argument("--release", action="store_true", help="fail on any unverified check")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = report(args.root, args.season, args.week, args.journal, args.release)
    if args.json:
        print(json.dumps(result, indent=1, sort_keys=True))
    else:
        for c in result["checks"]:
            print("%s: %s%s" % (c["status"].upper(), c["check"], (" (%s)" % c["note"]) if c["note"] else ""))
            for finding in c["findings"]:
                print("  - " + finding)
        print("Release preconditions %s%s." % ("hold" if result["ok"] else "do NOT hold",
                                               " (release mode)" if result["release"] else ""))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
