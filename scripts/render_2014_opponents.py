#!/usr/bin/env python3
"""Render or check the undated, branch-derived 2014 league opponent matrix."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from runtime.schedule_2014 import FOLDER, check, products


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        errors = check(ROOT)
        print('\n'.join(errors) if errors else '2014 OPPONENT MATRIX CURRENT: 256 games, 32 clubs')
        return bool(errors)
    for name, text in products(ROOT).items():
        (ROOT / FOLDER / name).write_text(text, encoding='utf-8')
    print('2014 opponent matrix rendered; no dated fixtures or game authorization added.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
