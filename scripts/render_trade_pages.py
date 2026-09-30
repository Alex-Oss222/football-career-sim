#!/usr/bin/env python3
"""Render individual trade reading pages from the existing dated records."""
import argparse
from html import escape
from pathlib import Path
import re
import sys
import textwrap

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from runtime.seasons import SeasonPaths
from runtime.season_layout import rebase_markdown


def slug(value):
    return re.sub(r'[^a-z0-9]+', '_', value.lower()).strip('_')


def exchange_card(sends, receives):
    columns = []
    for text in (sends, receives):
        columns.append([line for item in text.split(';')
                        for line in textwrap.wrap(item.strip(), 43)])
    height = max(220, 110 + max(map(len, columns)) * 26)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 {height}" role="img">',
           '<title>Completed trade: Jacksonville sends and receives</title>',
           f'<rect width="960" height="{height}" fill="#f3f6f5"/>']
    for index, lines in enumerate(columns):
        x = 16 + index * 472
        out += [f'<rect x="{x}" y="16" width="456" height="{height-32}" rx="12" fill="white" stroke="#b9cbc7"/>',
                f'<text x="{x+22}" y="53" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#17675d">JACKSONVILLE {"SENDS" if index == 0 else "RECEIVES"}</text>']
        for row, line in enumerate(lines):
            out.append(f'<text x="{x+22}" y="{94+row*26}" font-family="Arial, sans-serif" font-size="17" fill="#193d38">{escape(line)}</text>')
    return '\n'.join(out+['</svg>'])+'\n'


def render(root, year):
    root = Path(root)
    base = SeasonPaths(year, root).record('trades')
    # The logical trades directory maps to completed trades. Its parent is
    # the year-round trade index from 2014 onward.
    if year < 2014:
        raise ValueError('The individual trade layout begins in 2014')
    base = base.parent
    completed = base/'completed_trades/trades.md'
    offers = base/'targets_and_offers/trade_offers.md'
    targets = base/'targets_and_offers/trade_targets.md'
    out = {}
    completed_index = [f'# {year} completed trades', '', '[Trades](../README.md)', '',
                       'Each exchange below is already processed. Open a trade for both sides, the original terms, closing conditions and accounting. Figures and pick counts inside a dated trade describe that event; use the current roster and pick register for today’s holdings.', '',
                       '| Completed trade | Open |', '|---|---|']
    parts = re.findall(r'^## (Jacksonville / [^\n]+)\n(.*?)(?=^## |\Z)', completed.read_text(), re.M | re.S)
    for title, body in parts:
        rows = [re.match(r'^\| ([^|]+) \| ([^|]+) \|$', line) for line in body.splitlines()]
        exchange = {m[1].strip(): m[2].strip() for m in rows if m and m[1].strip() not in ('Club','---')}
        if 'Jacksonville' not in exchange or len(exchange) != 2:
            raise ValueError('Completed trade must retain both clubs: '+title)
        receives = exchange.pop('Jacksonville')
        sends = next(iter(exchange.values()))
        name = slug(title.removeprefix('Jacksonville / '))
        target = completed.parent/'deals'/name/'README.md'
        page = f'# {title}\n\n[Completed trades](../../README.md) · [Original dated record](../../trades.md)\n\n'
        page += f'![Jacksonville sends: {sends}. Jacksonville receives: {receives}.](exchange.svg)\n\n'
        page += rebase_markdown(body.strip(), completed.relative_to(root), target.relative_to(root))+'\n'
        out[target] = page
        out[target.parent/'exchange.svg'] = exchange_card(sends, receives)
        completed_index.append(f'| {title.removeprefix("Jacksonville / ")} | [Full exchange](deals/{name}/README.md) |')
    completed_index += ['', '[Full dated trade ledger](trades.md) · [Current draft assets](../../draft/pick_ownership.json) · [Finances](../../finances/README.md)', '',
                        'Maintain the dated source record first, then run `python scripts/render_trade_pages.py '+str(year)+'`. The individual pages are generated reading views.', '']
    out[completed.parent/'README.md'] = '\n'.join(completed_index)
    target_index = [f'# {year} trade targets and offers', '', '[Trades](../README.md)', '',
                    'The target board records intentions and the current disposition of each proposal. The offer history below records actual contacts. A proposal changes no player, pick or financial obligation.', '',
                    '## Targets', '', '| Proposal | Current recorded status |', '|---|---|']
    table = targets.read_text().split('## Trades and status',1)[1].split('## Open trades',1)[0]
    for line in table.splitlines():
        cells = [c.strip() for c in line.strip('|').split('|')]
        if not line.startswith('|') or len(cells) != 3 or cells[0] == 'Trade' or cells[0].startswith('---'):
            continue
        title, terms, status = cells
        name = slug(title)
        target = targets.parent/'targets'/f'{name}.md'
        page = f'# {title}\n\n[All targets and offers](../README.md) · [Source target board](../trade_targets.md)\n\n'
        page += rebase_markdown(f'## Proposed exchange\n\n{terms}\n\n## Recorded status\n\n{status}\n', targets.relative_to(root), target.relative_to(root))
        out[target] = page
        target_index.append(f'| [{title}](targets/{name}.md) | '+rebase_markdown(status, targets.relative_to(root), (targets.parent/'README.md').relative_to(root))+' |')
    target_index += ['', '## Offer history', '']
    for title, body in re.findall(r'^## ([^\n]+)\n(.*?)(?=^## |\Z)', offers.read_text(), re.M | re.S):
        if title == 'Adding an entry':
            continue
        name = slug(title)
        target = offers.parent/'offers'/f'{name}.md'
        out[target] = f'# {title}\n\n[All targets and offers](../README.md) · [Source offer log](../trade_offers.md)\n\n'+rebase_markdown(body.strip(), offers.relative_to(root), target.relative_to(root))+'\n'
        target_index.append(f'- [{title}](offers/{name}.md)')
    target_index += ['', '[Target board](trade_targets.md) · [Complete offer log](trade_offers.md) · [Completed trades](../completed_trades/README.md)', '']
    out[targets.parent/'README.md'] = '\n'.join(target_index)
    return out


def check(root=ROOT, year=2014):
    return [f'Trade page stale: {path.relative_to(root)}' for path, text in render(root, year).items()
            if not path.exists() or path.read_text() != text]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('year', type=int)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        errors = check(ROOT, args.year)
        print('\n'.join(errors) if errors else 'Trade reading pages are current')
        return bool(errors)
    for path, text in render(ROOT, args.year).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    print('Rendered trade targets, offers and completed exchanges')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
