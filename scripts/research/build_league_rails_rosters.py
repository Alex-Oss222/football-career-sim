#!/usr/bin/env python3
"""Deprecated destructive exporter. Use the ID-linked league database builder."""
import sys


def main(*_args):
    raise SystemExit(
        'The legacy name-only contract exporter is retired because it overwrote '
        'verified research. Run python scripts/research/build_league_player_database.py '
        'to rebuild safely from the committed snapshot, or add --check to verify it.'
    )


if __name__ == '__main__':
    main(*sys.argv[1:])
