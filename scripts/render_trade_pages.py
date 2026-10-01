#!/usr/bin/env python3
"""Render concise trade navigation from the canonical completed-trade index."""
import argparse
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from runtime.seasons import SeasonPaths


def render(root, year):
    root = Path(root)
    if year < 2014:
        raise ValueError('The individual trade layout begins in 2014')
    completed = SeasonPaths(year, root).record('trades/trades.md')
    base = completed.parent.parent
    if not completed.exists():
        return {}
    rows = [line for line in completed.read_text().splitlines()
            if line.startswith('| ') and '](' in line]
    lines = [f'# {year} trades', '',
             '[Completed trades](completed_trades/trades.md) · '
             '[Target board](targets_and_offers/trade_targets.md) · '
             '[Offers and negotiations](targets_and_offers/trade_offers.md)', '',
             'Each completed exchange has one dated record. The target board '
             'owns intentions; the offer record owns negotiations and unresolved conditions. '
             'Neither changes control before a trade closes.', '',
             '## Completed exchanges', '',
             '| Date | Exchange |', '|---|---|']
    for row in rows:
        row = re.sub(r'\]\((?!https?://)([^)]+)\)',
                     lambda m: '](completed_trades/' + m[1] + ')', row)
        lines.append(row)
    return {base / 'README.md': '\n'.join(lines) + '\n'}


def check(root=ROOT, year=2014):
    return [f'Trade index stale: {path.relative_to(root)}'
            for path, content in render(root, year).items()
            if not path.exists() or path.read_text() != content]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('year', type=int)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        errors = check(ROOT, args.year)
        print('\n'.join(errors) if errors else 'Trade index is current')
        return bool(errors)
    for path, content in render(ROOT, args.year).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    print('Rendered trade navigation; no duplicate deal pages created')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
