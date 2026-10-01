#!/usr/bin/env python3
"""Render the one-line annual record from metadata at each event's actual owner."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from runtime.events import annual_record_path, load_events, render_record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('year', type=int)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    root = args.root.resolve()
    events = load_events(root)
    path = annual_record_path(root, args.year)
    expected = render_record(args.year, events, root)
    if args.check:
        if not path.is_file() or path.read_text() != expected:
            print(f'Stale annual record: {path.relative_to(root)}')
            return 1
        print(f'Annual record agrees with its event owners: {args.year}')
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(expected)
    print(path.relative_to(root))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
