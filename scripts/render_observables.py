#!/usr/bin/env python3
"""Backfill or check a closed week's participation observables.

  python scripts/render_observables.py --season YEAR --week N [--check]

Kernel 2014.6 (batch B7, runtime/observables.py). A week closed by
scripts/close_week.py writes its observables from the frozen package at
closure; this command rebuilds a week closed before that record existed
(2014 Weeks 1-4) from committed data. The rebuild must reproduce every
background club's closed receipt or nothing is written; Jacksonville's rows
come from its closed full receipt where the current roster no longer rebuilds
that week's frozen input, and the file says so. --check compares the rebuild
with the committed file and writes nothing. No value or grade is written.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import observables  # noqa: E402
from runtime.strength import MODEL  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--week", type=int, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    target = observables.observables_path(args.week, args.season, ROOT)
    if args.check:
        if not target.is_file():
            print("OBSERVABLES: MISSING %s" % target.relative_to(ROOT))
            return 1
        rebuilt = observables.rebuild_record(args.week, args.season, ROOT, strength_model=MODEL)
        committed = json.loads(target.read_text(encoding="utf-8"))
        if rebuilt != committed:
            print("OBSERVABLES: DIFFERS %s" % target.relative_to(ROOT))
            return 1
        print("OBSERVABLES: OK %s" % target.relative_to(ROOT))
        return 0
    try:
        record, path = observables.backfill(args.week, args.season, ROOT, strength_model=MODEL)
    except ValueError as exc:
        print("OBSERVABLES: BLOCKED\n- %s" % exc)
        return 1
    print("OBSERVABLES: WRITTEN %s (%d clubs)" % (path.relative_to(ROOT), len(record["clubs"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
