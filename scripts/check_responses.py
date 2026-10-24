#!/usr/bin/env python3
"""Check a week's My Responses page (rebuild step 5; runtime/responses.py).

  python scripts/check_responses.py WEEK --season YEAR [--file PATH] [--root PATH]

His answers to the notices inserted in the week's briefing (or the bye's review), one block each,
checked by the template's validation rules in football words: the notice a block answers exists, was
brought to him, is still open and needs his part; every player and coach he names is on the roster
or the coach records; every date he writes is checked against the notice's due time; a notice his
standing instruction or someone else answers needs nothing from him ("None needed", and how to
change the rule); "Leave this open until <date>" is accepted only before the due time and keeps it
open; an empty answer means still open, never an error; the page is clean; an answer for a settled
question is refused. Builder C's reserved blocks (Depth and inactives change, Practice week) have
their own checks and are not read here.

``--file`` uploads a .md or .txt file with the same headings as the week's page (refused, with
nothing written, for an unbound heading, a change to a recorded answer, or an answer for a settled
question); it never touches the Game Plan. Exits 1 while anything is missing or invalid. Nothing is
recorded here: scripts/apply_responses.py records the answers.
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
    parser.add_argument("--file", type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    period = responses.period_of(args.season, args.week, root)
    if args.file is not None:
        try:
            page = responses.place_upload(root, args.season, period, args.file)
        except (OSError, ValueError) as exc:
            print("MY RESPONSES NOT PLACED: %s" % exc)
            return 1
        print("placed %s" % page.relative_to(root).as_posix())
    checked = responses.check(args.season, period, root)
    for line in checked.problems:
        print("- %s" % line)
    for line in checked.notes:
        print("note: %s" % line)
    if checked.problems:
        print("MY RESPONSES: NOT READY")
        return 1
    print("MY RESPONSES: %d answer%s ready to record" % (len(checked.ready), "" if len(checked.ready) == 1 else "s"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
