#!/usr/bin/env python3
"""Render the league player cards from the committed game records.

  python scripts/render_player_cards.py [--check]

Writes career/league_players/: an index of the 32 clubs, one page per club
(its players by position group), and for every player in the game records a
page (his card, his regular-season and playoff statistics by season with a
career row, his awards) and the card itself as an SVG image. Pages of
players no longer on record are removed. Each Jacksonville player card page
(2014 onward) whose player has a league page also shows his card directly
under its title, in a generated <!-- player-card:begin --> ...
<!-- player-card:end --> block with a link to his career statistics; only
that block is written. --check writes nothing and fails when any file or
block differs. Run after every closed game (docs/update_workflow.md).
The cards are a reader view: no game, evaluation or decision reads them.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import player_cards  # noqa: E402


def check(root=ROOT):
    return player_cards.check(root)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    if args.check:
        errors = check(args.root)
        print("\n".join(errors[:50]) if errors else "LEAGUE PLAYER CARDS CURRENT")
        if len(errors) > 50:
            print("... and %d more" % (len(errors) - 50))
        return 1 if errors else 0
    written, removed, pages = player_cards.write(args.root)
    print("wrote %s: %d files changed, %d removed; %d Jacksonville player card pages updated"
          % (player_cards.FOLDER, written, removed, pages))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
