#!/usr/bin/env python3
"""Freeze the Game Report's pregame sections before kickoff (game week version 2).

  python scripts/freeze_pregame.py WEEK --season YEAR [--root PATH]

At the game-day commit (docs/run_week.md, step 5), once the Game Report is
opened with its sections 1 and 2 (the preparation and the pregame media),
this records the sha256 of each in the week's data folder
(runtime/decisions.WeekPages.pregame, ``pregame.json``) with the day. Once the
game has closed, validation holds the report's sections 1 and 2 to the record
(runtime/game_report.pregame_errors), and requires it: the pregame media is
written and frozen from pregame knowledge, never rewritten with the result
known (docs/game_week_v2.md, sections 3 and 6).

It refuses, writing nothing, a week whose Jacksonville game has been played or
is paused, a report that already gives a final score, and a report without
both pregame sections. Run again before kickoff, it replaces the record with
the sections as they stand. Nothing here moves the clock, plays a game or
writes a page.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import game_report, game_weeks  # noqa: E402
from runtime.decisions import week_pages  # noqa: E402
from runtime.player_bios import master_date  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402

JAX = "Jacksonville Jaguars"


def freeze(root, season, week):
    """Write the week's pregame freeze record; returns its path. ValueError, with nothing written,
    when the game is played or paused, or the report is not a pregame report."""
    root = Path(root).resolve()
    paths = SeasonPaths(season, root)
    postseason = game_weeks.is_postseason(paths, week)
    game = game_weeks.club_game(paths, week, JAX)
    name = game_weeks.round_name(week) if postseason else "Week %d" % week
    if game is None:
        raise ValueError("%s: Jacksonville has no game to freeze" % name)
    receipts = game_weeks.postseason_receipts(paths) if postseason else game_weeks.regular_receipts(paths)
    if game_weeks.closed_receipt(receipts, game) is not None:
        raise ValueError("%s has been played; its pregame sections were to be frozen before kickoff" % name)
    from scripts.render_career_views import paused_games
    if paused_games(root):
        raise ValueError("A game is paused; nothing is frozen until it is finished")
    pages = week_pages(season, week, root, postseason=postseason)
    if not pages.report.is_file():
        raise ValueError("%s: the Game Report is not opened yet (%s)" % (name, pages.report.relative_to(root)))
    text = pages.report.read_text(encoding="utf-8")
    problems = game_report.report_errors(text, None, game, root=root, label=name)
    if problems:
        raise ValueError("; ".join(problems))
    record = game_report.pregame_record(text, master_date(root))
    pages.pregame.parent.mkdir(parents=True, exist_ok=True)
    pages.pregame.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return pages.pregame


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("week", type=int)
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        path = freeze(args.root, args.season, args.week)
    except (OSError, ValueError, game_weeks.NotSet) as exc:
        print("PREGAME: NOT FROZEN\n- %s" % exc)
        return 1
    print("PREGAME: FROZEN  wrote %s" % path.relative_to(Path(args.root).resolve()).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
