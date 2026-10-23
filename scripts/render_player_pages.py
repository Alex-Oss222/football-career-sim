#!/usr/bin/env python3
"""Build every player page from the permanent player records.

  python scripts/render_player_pages.py [--check] [--root PATH]

One builder for every player page (rebuild step 3a): each league player page
under career/league_players/ (with the league index and the club pages) and
each Jacksonville player page in the active season's player folder (with its
index), in the layout of the user's player card template
(foundation/templates/player_card_template.md): header, physical line, As of
and photo; the current assignment (runtime/assignments.py); the position
statistic from the closed games; the short staff assessment, its season
figures resolved from the closed games and no grades; contract; statistics
(the quarterback's column is Passer rating); awards; transactions. The pages
are built from data/people/players/ and the owners runtime/people.READ_THROUGH
names (the awards from the award results), never edited by hand.

Writing first adds an identity-only record for any player new to the game
records; no other fact is created. Files under the two folders that no
longer belong to a page are removed. --check writes nothing and fails on a
record that breaks the schema, a staff assessment whose figures cannot be read
from the closed games, a role label or Week 1 slot with no page words, an
award whose winner is not in the game records, a player without a record and
any page that differs from its rebuild; writing refuses, before it writes
anything, while a staff assessment, role label or Week 1 slot cannot be built. Run after every closed game and its
awards, after any change to a record and after any depth chart or role change
(docs/update_workflow.md).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import player_pages  # noqa: E402


def check(root=ROOT):
    return player_pages.check(root)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    if args.check:
        errors = check(args.root)
        print("\n".join(errors[:50]) if errors else "PLAYER PAGES CURRENT")
        if len(errors) > 50:
            print("... and %d more" % (len(errors) - 50))
        return 1 if errors else 0
    created, written, removed = player_pages.write(args.root)
    print("player pages: %d records created, %d pages written, %d files removed" % (created, written, removed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
