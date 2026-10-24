#!/usr/bin/env python3
"""Render the trade pages: the folder's navigation from the canonical completed-trade index, and
the trade offer log's index of calls.

The navigation (``render``) is built from ``completed_trades/trades.md``, as before.

The offer log's index (``render_index``, ``targets_and_offers/trade_offers.md``): the page written
before 2014 Week 6 was split into one page per call under the split rule (runtime/clean_pages.py;
its title line and opening paragraph moved here as this page's opening, from the page history map's
record of them). The index lists each call by the date of its first call: the calls split from the
log (in the order the log gave them on a shared date; each with its completed trade record when one
carries the same players and club, as the names of both say; the San Francisco call's own page is
its record), then every trade call recorded as an
event from Week 6 (``runtime/open_events``) with its result page once resolved, then the open trade
calls with their due times, then the trade deadline while the briefs show it
(``runtime/deadlines.coming_up``, read at the master clock). Only events known to Stone are listed.
Nothing here creates a call, an offer or a result: a page with no open call says so.
"""
import argparse
import datetime as dt
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from runtime import clean_pages  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402

# The league date's key in its season's record (league_dates.json): "<season>-trading-deadline".
DEADLINE_KEY = 'trading-deadline'
DATED = re.compile(r'_(\d{4}-\d{2}-\d{2})\.md$')
COMPLETED_ROW = re.compile(r'^\| ([A-Z][a-z]+ \d{1,2}, \d{4}) \| \[[^\]]+\]\(([^()\s]+\.md)\) \|')
OUTCOME_WORDS = {'executed': 'Executed', 'no_move': 'No move', 'accepted': 'Accepted', 'rejected': 'Rejected',
                 'declined': 'Declined', 'withdrawn': 'Withdrawn', 'lapsed': 'Lapsed',
                 'ended_without_agreement': 'Ended without agreement'}
STATE_WORDS = {'open': 'Open', 'answered': 'Answered; the decision is pending', 'offered': 'Offered',
               'countered': 'Countered', 'agreed_in_principle': 'Agreed in principle',
               'awaiting_conditions': 'Awaiting conditions'}


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


def index_path(root, year):
    """The trade offer log's index of calls."""
    return SeasonPaths(year, root).record('trades/trade_offers.md')


def _long(day):
    day = dt.date.fromisoformat(day) if isinstance(day, str) else day
    return '%s %d, %d' % (day.strftime('%B'), day.day, day.year)


def _link(index, target, root):
    """A relative link from the index to a repository path."""
    return os.path.relpath(Path(root) / target, index.parent).replace(os.sep, '/')


def _stem(name):
    return DATED.sub('', name)


def completed_records(root, year):
    """{players and club: [(completion date in words, repository path)]} of the completed trade
    records the season's completed-trade index lists."""
    completed = SeasonPaths(year, root).record('trades/trades.md')
    out = {}
    if completed.exists():
        for line in completed.read_text(encoding='utf-8').splitlines():
            row = COMPLETED_ROW.match(line)
            if row:
                path = (completed.parent / row[2]).relative_to(root).as_posix()
                out.setdefault(_stem(Path(row[2]).name), []).append((row[1], path))
    return out


def history_calls(root, year):
    """The calls split from the offer log as written before Week 6: (sort key, first call, call
    cell, status cell)."""
    index = index_path(root, year)
    entry = clean_pages.splits(root).get(index.relative_to(root).as_posix())
    records = completed_records(root, year)
    out = []
    for order, part in enumerate((entry or {}).get('parts', ())):
        name = Path(part['path']).name
        first = DATED.search(name)
        if not first:
            raise ValueError('the call page %s is not named for the date of its first call' % name)
        found = records.get(_stem(name), [])
        if len(found) > 1:
            raise ValueError('two completed trade records carry the players and club of %s' % name)
        if found:
            status = '[Completed %s](%s)' % (found[0][0], _link(index, found[0][1], root))
        else:
            status = 'No trade; the call page is its record'
        title = re.sub(r'^Trade calls?: ', '', part['title'][2:])
        out.append(((first[1], 0, order, name), _long(first[1]), '[%s](%s)' % (title, name), status))
    return out


def trade_events(root, year):
    """The trade calls recorded as events in the season and known to Stone, by when raised."""
    from runtime import current_job, open_events
    job = current_job.load(root)
    return [r for r in open_events.load(year, root)
            if r.get('kind') == 'trade_talks' and open_events.known_to_stone(r, job)]


def _source_cell(record, title, index, root):
    """The call's title, linked to the page that first recorded it when that is a page."""
    source = (record.get('raised') or {}).get('source') or {}
    path = source.get('path') or ''
    if path.startswith('career/') and path.endswith('.md') and (Path(root) / path).is_file():
        anchor = '#' + source['anchor'] if source.get('anchor') else ''
        return '[%s](%s%s)' % (title, _link(index, path, root), anchor)
    return title


def render_index(root, year):
    """{the index's path: its text}; nothing for a season with no completed trade, no split log and
    no trade call recorded."""
    from runtime import deadlines, open_events
    root = Path(root).resolve()
    index = index_path(root, year)
    rel = index.relative_to(root).as_posix()
    entry = clean_pages.splits(root).get(rel)
    events = trade_events(root, year)
    if entry is None and not events and not SeasonPaths(year, root).record('trades/trades.md').exists():
        return {}
    opening = ''.join(m['text'] for m in (entry or {}).get('moved', ()) if m.get('to') == rel)
    if not opening:
        opening = ('# Jacksonville %d trade offer log\n\nEvery trade call of the season, by the date of its '
                   'first call, with its record.\n\n' % year)
    calls = history_calls(root, year)
    still = []
    for record in events:
        res = record.get('resolution')
        if res is None:
            still.append(record)
            continue
        first = record['raised']['at'][:10]
        status = '%s %s' % (OUTCOME_WORDS[res['outcome']], _long(res['at'][:10]))
        if res.get('result_page'):
            status = '[%s](%s)' % (status, _link(index, res['result_page'], root))
        calls.append(((first, 1, record['raised']['at'], record['id']), _long(first),
                      _source_cell(record, open_events.title(record), index, root), status))
    lines = ['## Trade calls', '', '| First call | Call | Result |', '|---|---|---|']
    lines += ['| %s | %s | %s |' % row[1:] for row in sorted(calls)]
    if not calls:
        lines = ['## Trade calls', '', 'No trade call is recorded.']
    lines += ['', '## Open trade calls', '']
    if still:
        lines += ['| Raised | Call | Where it stands | Due |', '|---|---|---|---|']
        for record in still:
            raised = open_events.at_text(open_events.parse_at(record['raised']['at']))
            due = record.get('deadline') or {}
            due = open_events.at_text(open_events.parse_at(due['at'])) if due.get('at') else 'Not set'
            lines.append('| %s | %s | %s | %s |' % (raised, _source_cell(record, open_events.title(record), index, root),
                                                     STATE_WORDS.get(record['state'], record['state']), due))
    else:
        lines.append('No trade call is open.')
    key = '%d-%s' % (year, DEADLINE_KEY)
    windows = [w for w in deadlines.coming_up(year, open_events.master_at(root), root) if w.get('key') == key]
    if windows:
        lines += ['', '## Trade deadline', '', '| Deadline | When | Where it stands |', '|---|---|---|']
        for w in windows:
            when = open_events.at_text(open_events.parse_at(w['at'])) if w.get('at') else 'Not set'
            lines.append('| %s | %s | %s |' % (w.get('title') or 'Trade deadline', when, w.get('state') or ''))
    return {index: opening + '\n'.join(lines) + '\n'}


def pages(root, year):
    """Every trade page this script builds: the navigation and the offer log's index."""
    out = dict(render(root, year))
    out.update(render_index(root, year))
    return out


def check(root=ROOT, year=2014):
    root = Path(root).resolve()
    return [f'Trade index stale: {path.relative_to(root)}'
            for path, content in pages(root, year).items()
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
    for path, content in pages(ROOT, args.year).items():
        unclean = clean_pages.text_errors(path.relative_to(ROOT).as_posix(), content)
        if unclean:
            print('Not written, unclean: ' + '; '.join(unclean))
            return 1
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    print('Rendered trade navigation and the trade offer index; no duplicate deal pages created')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
