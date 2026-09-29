#!/usr/bin/env python3
"""Idempotently mark a week's voided event generations in the private journal.

  python scripts/void_week_generation.py WEEK [SEASON]

Reads that season's career/SEASON/migrations/event_generations.json (SEASON
defaults to 2013; one season's voids never apply to another's). Every event of every
voided generation for WEEK is recorded as a correction with the manifest's
reason. Run it before closing the replacement generation. Voided results are
never read, shown, compared or selected among; this script reads none.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.private_client import Client, PrivateRuntimeUnavailable
from runtime.season import season_paths


def main(argv):
    if len(argv) not in (2, 3) or not all(a.isdigit() for a in argv[1:]):
        print(__doc__)
        return 2
    week = argv[1]
    season = int(argv[2]) if len(argv) == 3 else 2013
    generations = season_paths(season).generations
    if not generations.is_file():
        print("NO_VOIDED_GENERATION: %d has no event_generations.json" % season)
        return 1
    entry = json.loads(generations.read_text(encoding="utf-8"))["weeks"].get(str(int(week)))
    if not entry or not entry.get("voided"):
        print("NO_VOIDED_GENERATION: week %s" % week)
        return 1
    client = Client()
    marked = 0
    try:
        for void in entry["voided"]:
            for event_id in void["events"]:
                client.record_correction(event_id, void["reason"])
                marked += 1
    except PrivateRuntimeUnavailable as exc:
        print("WEEK_GENERATION_VOID_MARK_FAILED: %s" % exc, file=sys.stderr)
        return 1
    print("WEEK_%s_VOIDED_GENERATIONS_MARKED: %d events" % (week, marked))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
