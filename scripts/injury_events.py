#!/usr/bin/env python3
"""Open the injury replacement questions after a closed game (rebuild step 5, D1).

  python scripts/injury_events.py WEEK --season YEAR [--check]
  python scripts/injury_events.py --return PLAYER --season YEAR [--check]
  python scripts/injury_events.py --recommend PLAYER --source PAGE --season YEAR [--check]

Run after the close of Week WEEK has recorded each new injury's medical communication on the roster
record (docs/run_week.md, the step after the close). One ``injury_replacement`` event opens for each
Jacksonville active-roster player whose instruction from the game is long term, and one for each
game-day group the players out for the next game leave short of its minimum (usage.lineup_errors)
that no such event covers. A shorter injury opens nothing. ``--return`` raises the question for a
designated-for-return player whose windows have passed and whose medical clearance is recorded,
when he needs a place on the 53. ``--recommend`` raises it for an active player on Stone's own
recommendation, from the page of his that names it. One event per player whose list question is
open: a second run opens nothing new.

Each event is raised through the event store (runtime/open_events.raise_event): the general
manager's criteria first (the need, the legal moves before the next game, the contract facts), then
Stone's football recommendation item, due at the next game's kickoff; when the facts record that the
active roster cannot dress a legal team, the general manager's transaction item too, holding the
next game's build until the move is applied. Every fact and option comes from stored records, never
a grade, and no option names a later real move. ``--check`` prints what would open and writes
nothing. Nothing is played, moved or decided here.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import open_events, transactions  # noqa: E402


def describe(event):
    lines = ["%s: %s" % (open_events.title(event), event["summary"]["text"])]
    for fact in event["facts"]:
        lines.append("  %s: %s" % (fact["label"], fact["value"]))
    for option in event["options"]:
        lines.append("  Option: %s, %s (%s)" % (option["name"], option["position"], option["basis"]))
    return lines


def main(argv=None, root=ROOT, out=print):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("week", type=int, nargs="?")
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--return", dest="returning", default=None)
    parser.add_argument("--recommend", default=None)
    parser.add_argument("--source", default=None)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    root = Path(root).resolve()
    try:
        if args.returning or args.recommend:
            if args.week is not None:
                raise transactions.Refused("--return and --recommend take no week")
            if args.recommend:
                events = [transactions.recommendation_event(args.season, args.recommend, {"path": args.source or ""},
                                                            root)]
            else:
                events = [transactions.return_event(args.season, args.returning, root)]
            notes = []
        elif args.week is None:
            raise transactions.Refused("name the closed week: injury_events.py WEEK --season YEAR")
        else:
            events, notes = transactions.injury_events(args.season, args.week, root)
        for note in notes:
            out(note)
        for event in events:                  # every event checked before any is raised
            open_events.prepare(event, root)
        for event in events:
            if not args.check:
                open_events.raise_event(event, root)
            for line in describe(event):
                out(line)
        out("ROSTER QUESTIONS %s: %d" % ("TO OPEN" if args.check else "OPENED", len(events)))
        return 0
    except (transactions.Refused, open_events.Refused) as exc:
        out("ROSTER QUESTION REFUSED: %s" % exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
