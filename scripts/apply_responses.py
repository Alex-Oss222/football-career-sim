#!/usr/bin/env python3
"""Record a week's answers on My Responses (rebuild step 5; runtime/responses.py).

  python scripts/apply_responses.py WEEK --season YEAR [--root PATH]

For each answered block that passes the check (scripts/check_responses.py): fills its empty "Date
answered" line with the master date (the runner's only edit to his page), records the block's
digest, compiles what the answer commits to (support, oppose, a recommendation of a named option, a
condition in his words, or his permission to let it lapse), settles the queue item by the user with
the page and heading as its record, and stores the response on the event with a dated response
entry, moving it to answered. A recommendation never executes anything: the person with the
authority decides, from the criteria and the substance. An applied block is frozen; a change is a
new block headed "Revised: <title>". A blank block leaves its question open, and running this twice
changes nothing. Nothing is recorded while a game is paused or while any block has a problem.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import responses  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("week", type=int)
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    period = responses.period_of(args.season, args.week, root)
    try:
        problems, applied = responses.apply(args.season, period, root)
    except (OSError, ValueError) as exc:
        print("MY RESPONSES NOT RECORDED: %s" % exc)
        return 1
    if problems:
        for line in problems:
            print("- %s" % line)
        print("MY RESPONSES NOT RECORDED")
        return 1
    for heading in applied:
        print("recorded %s" % heading)
    if not applied:
        print("my responses: nothing to record")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
