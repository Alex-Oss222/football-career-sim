#!/usr/bin/env python3
"""Record an event inside a week or phase (rebuild step 5; runtime/open_events.py).

  python scripts/raise_event.py --season YEAR --file EVENT.json [--check]

The one way to record an event: an injury replacement, a trade call, another club's head-coach
change. The file is the event's record (``open-event-v1``) as whoever brings it supplies it, from a
sourced record only: its id (beginning with the date it was raised), kind, subject, who raised it and
the page that records it (``raised.source``), who knows of it, the authority (the Document 3 rows and
who decides), Stone's part, the one-line summary in football words, the staff's position and the
football consequence when supplied, the facts and options (names, positions, dates and sourced
terms, never a grade; a figure needs its source), the due time when one is sourced, its state and
any process entries already on record. The store stamps the open period and its latest issue, writes
the record to its owner's event store and, when Stone's part needs his answer, opens its item in the
decision queue (an injury replacement that leaves the active roster unable to dress a legal team for
the next game also opens the general manager's transaction item, and both hold that game). The open
period's index, which lists the events still open, is rebuilt at once; the brief that must show a
new answer is issued again by scripts/render_game_week.py under the one reissue rule.

Refused, with nothing written: a record without a source page, a time after the master date/time,
an id already used, a record that breaks a rule of the store, and anything while a game is paused.
``--check`` validates without writing. Nothing here creates an event of its own: no call, offer,
salary, interest or market price is generated, and recording one moves no time.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import open_events  # noqa: E402


def check(record, root=ROOT):
    """The problems recording ``record`` would meet, with nothing written."""
    try:
        open_events.prepare(record, root)
    except (open_events.Refused, ValueError, KeyError, TypeError) as exc:
        return [str(exc)]
    return []


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        record = json.loads(args.file.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print("EVENT NOT RECORDED: %s" % exc)
        return 1
    if not isinstance(record, dict) or record.get("season") != args.season:
        print("EVENT NOT RECORDED: the record names season %r, not %d" % (
            record.get("season") if isinstance(record, dict) else None, args.season))
        return 1
    if args.check:
        problems = check(record, args.root)
        print("\n".join(problems) if problems else "EVENT READY TO RECORD")
        return 1 if problems else 0
    try:
        written = open_events.raise_event(record, args.root)
    except (open_events.Refused, ValueError, KeyError, TypeError) as exc:
        print("EVENT NOT RECORDED: %s" % exc)
        return 1
    root = Path(args.root).resolve()
    try:
        written += rebuild_index(root)
    except (OSError, ValueError, KeyError) as exc:
        print("note: the open period's index was not rebuilt (%s); run python scripts/render_game_week.py" % exc)
    for path in written:
        print("wrote %s" % Path(path).resolve().relative_to(root).as_posix())
    return 0


def rebuild_index(root):
    """The open period's index, which lists the events still open (its "Other business this week"):
    a game week's by scripts/render_game_week.write_index, the bye's by its own builder."""
    from scripts import render_game_week, resolve_event
    wk = render_game_week.Week(root)
    if wk.game is not None:
        return render_game_week.write_index(root)
    if (wk.period or {}).get("bye"):
        return resolve_event.bye_index(root)
    return []


if __name__ == "__main__":
    raise SystemExit(main())
