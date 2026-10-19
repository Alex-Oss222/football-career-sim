#!/usr/bin/env python3
"""Render the one-line annual record from metadata at each event's actual owner.

  python scripts/render_annual_record.py YEAR [--check] [--root PATH]

Each line is an event's date, its one-line summary and a link to its owner,
sorted by date (runtime/events.render_record). The page is checked by the
clean-page rule (runtime/clean_pages.py): its lines written before 2014 Week 6
are history, and every line after them is checked. So an event closed from
Week 6 on needs a clean summary (football words only: no internal code, no
system word, no version label) and an owner that is a page, never a file in
the data area. The write refuses a record that would break the rule, naming
each problem, and writes nothing; ``--check`` writes nothing and reports a
stale or unclean record.
"""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from runtime.clean_pages import text_errors
from runtime.events import annual_record_path, load_events, render_record


def problems(root, year, text):
    """The clean-page problems of the record ``text`` would be at its place."""
    rel = annual_record_path(root, year).relative_to(root).as_posix()
    return text_errors(rel, text, root)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('year', type=int)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    root = args.root.resolve()
    events = load_events(root)
    path = annual_record_path(root, args.year)
    expected = render_record(args.year, events, root)
    unclean = problems(root, args.year, expected)
    if args.check:
        stale = not path.is_file() or path.read_text() != expected
        if stale:
            print(f'Stale annual record: {path.relative_to(root)}')
        for problem in unclean:
            print(problem)
        if stale or unclean:
            return 1
        print(f'Annual record agrees with its event owners: {args.year}')
        return 0
    if unclean:
        print(f'Annual record not written: {path.relative_to(root)} would break the clean-page rule; '
              'reword the event summaries or owners named below')
        for problem in unclean:
            print(problem)
        return 1
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(expected)
    print(path.relative_to(root))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
