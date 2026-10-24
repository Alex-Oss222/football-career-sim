#!/usr/bin/env python3
"""Build the league's head-coach changes pages from their records (rebuild step 5, D2).

  python scripts/render_coaching_changes.py --season YEAR [--check]

The folder's index and each change page the master clock has reached are built from the method
and the weekly check records (runtime/league_coaches.py): never typed. This rewrites a stale page
and never creates a new change page (scripts/coaching_check.py --effective writes one, with its
news event). Before the first check there is no folder and nothing to build. ``--check`` writes
nothing and exits 1 on a missing or stale page, a page for a change the clock has not reached, or
an effective change without its news event.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import league_coaches as lc  # noqa: E402
from runtime.clean_pages import text_errors  # noqa: E402


def check(root=ROOT, season=None):
    """The problems of the season's head-coach pages (empty when they are current)."""
    root = Path(root).resolve()
    season = lc._season(root) if season is None else season
    if lc.load_method(season, root) is None:
        return []
    return lc.page_errors(season, root)


def write(root=ROOT, season=None):
    """Rewrite each stale built page; returns the pages written. A change page that does not exist
    yet is refused (its news event comes with it)."""
    root = Path(root).resolve()
    season = lc._season(root) if season is None else season
    written = []
    for path, text in lc.pages(season, root).items():
        rel = path.relative_to(root).as_posix()
        problems = text_errors(rel, text, root)
        if problems:
            raise ValueError("not clean: %s" % "; ".join(problems))
        if path.name != lc.INDEX and not path.is_file():
            raise ValueError("%s is a new change; scripts/coaching_check.py --season %d --effective writes it "
                             "with its news" % (rel, season))
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            written.append(path)
    return written


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.check:
        problems = check(ROOT, args.season)
        for problem in problems:
            print(problem)
        if problems:
            return 1
        print("HEAD-COACH PAGES CURRENT")
        return 0
    try:
        written = write(ROOT, args.season)
    except ValueError as exc:
        print("HEAD-COACH PAGES NOT WRITTEN: %s" % exc)
        return 1
    print("HEAD-COACH PAGES: %d written" % len(written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
