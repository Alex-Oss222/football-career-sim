"""Readable weekly award cards. Presentation only: never select a winner."""
from html import escape
from pathlib import Path
import re
import textwrap

from scripts.player_photos import Photos, credit_short


def award_cards(award, shortlist, winner_index):
    if not 0 <= winner_index < len(shortlist) <= 3:
        raise ValueError('Award requires its recorded winner and at most three finalists')
    others = [row for i, row in enumerate(shortlist) if i != winner_index]
    slots = [others[0] if others else None, shortlist[winner_index], others[1] if len(others) > 1 else None]
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 255" role="img">',
             '<title>'+escape(award)+': recorded winner in the center</title>',
             '<rect width="960" height="255" fill="#f3f6f5"/>']
    for index, row in enumerate(slots):
        if row is None:
            continue
        x, winner = 16 + index * 315, index == 1
        parts.append(f'<rect x="{x}" y="16" width="298" height="220" rx="12" fill="white" stroke="{ "#b38b31" if winner else "#d4dddb" }" stroke-width="{4 if winner else 1}"/>')
        def line(y, value, size=17, color='#173f3c', weight='normal'):
            parts.append(f'<text x="{x+149}" y="{y}" text-anchor="middle" font-family="Arial, sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(str(value))}</text>')
        line(48, 'WINNER' if winner else 'FINALIST', 13, '#80601b' if winner else '#526c68', 'bold')
        for n, value in enumerate(textwrap.wrap(row['player'], 22)):
            line(94+n*25, value, 22, weight='bold')
        for n, value in enumerate(textwrap.wrap(row['team'], 29)):
            line(157+n*21, value, 16)
        line(213, f"Shortlist score: {row['score']:.1f}", 15, '#526c68')
    return '\n'.join(parts+['</svg>'])+'\n'


def _relative_link(repository_path):
    """A link from career/YEAR/05_Regular_Season/Awards/README.md to a repository path."""
    return '../../../../' + repository_path


def render_pages(season, results, method=None):
    if results and method is None:
        raise ValueError('Recorded awards require their season methodology')
    out = {}
    index = [f'# {season} regular-season awards', '',
             '[Regular season](../README.md) · [Season](../../README.md)', '',
             'Open a week to see each award’s three finalists. The recorded winner appears in the middle with a gold border. Shortlist scores are selection inputs; they are not vote totals or finishing positions.', '',
             f'Awards appear after games and the applicable award process close. No {season} award has been drawn.' if not results else 'These pages display recorded results without repeating the draw.', '',
             '## Weekly awards', '', '| Week | Awards |', '|---|---|']
    entries = {(v['kind'], str(v['key'])): v for v in results.values()}
    photos = Photos()
    for week in range(1, 19 if season >= 2021 else 18):
        rel = f'week_{week:02d}/README.md'
        entry = entries.get(('week', str(week)))
        label = f'[Week {week}]({rel})' if entry else f'Week {week}'
        index.append(f'| {label} | {"Recorded" if entry else "Awaiting closed games and awards"} |')
        if entry:
            out.update(period_page(f'Week {week}', rel, entry, method, photos=photos))
    index += ['', '## Monthly awards', '', '| Month | Awards |', '|---|---|']
    months = (list(method['months']) if method and method.get('months') else
              ['September', 'October', 'November', 'December'])
    for month in months:
        rel = f'monthly/{month.lower()}/README.md'
        entry = next((v for (kind, key), v in entries.items() if kind == 'month' and key.lower() == month.lower()), None)
        label = f'[{month}]({rel})' if entry else month
        index.append(f'| {label} | {"Recorded" if entry else "Awaiting the season’s dated coverage and closed awards"} |')
        if entry:
            out.update(period_page(month, rel, entry, method, back='../../README.md', photos=photos))
    if method and method.get('frozen'):
        frozen = method['frozen']
        index += ['', '## Methodology', '',
                  f"Frozen {frozen['clock']} ({frozen['date']}): [methodology.json](methodology.json). "
                  f"{frozen['basis']} It mirrors [{frozen['mirrors']}]({_relative_link(frozen['mirrors'])}). "
                  + (method.get('month_rule') or '')]
    index += ['', '## Season honours', '',
              'Season awards and the Pro Bowl use their own dates and selection processes. Follow [postseason and Pro Bowl]('+('../../06_Postseason/README.md' if season >= 2014 else '../../postseason/README.md')+').', '',
              ('This season’s methodology and monthly coverage were frozen from the actual schedule before the first draw (see Methodology above). Prior-year winners and monthly windows do not carry forward.'
               if method and method.get('frozen') else
               'Before the first draw, freeze this season’s methodology and monthly coverage from the actual schedule. Prior-year winners and monthly windows do not carry forward.'), '']
    out['README.md'] = '\n'.join(index)
    return out


def period_page(label, relative, entry, method, back='../README.md', photos=None):
    lines = [f'# {label} awards', '', f'[All regular-season awards]({back})', '']
    out = {}
    photos = photos or Photos()
    if not entry:
        lines += ['Not awarded yet. Finalists and the winner will appear here after the applicable games and award process close.', '']
    else:
        for key, award in entry['awards'].items():
            title = method['award_names'][key]
            asset = re.sub(r'[^a-z0-9]+', '_', key.lower())+'.svg'
            out[(Path(relative).parent / asset).as_posix()] = award_cards(title, award['shortlist'], award['winner_index'])
            winner = award['shortlist'][award['winner_index']]['player']
            found = {row['player']: photos.lookup(row['player'], team=row['team']) for row in award['shortlist']}
            lines += [f'## {title}', '']
            if found[winner]:
                lines += [f'<img src="{escape(found[winner]["url"], quote=True)}" alt="{escape(winner, quote=True)}" width="160">', '']
            lines += [f'![{title}: {winner} wins; winner centered with a gold border]({asset})', '',
                      '| Photo | Player | Team | Shortlist score | Result |', '|---|---|---|---:|---|']
            for i, row in enumerate(award['shortlist']):
                thumb = found[row['player']]
                cell = f'<img src="{escape(thumb["url"], quote=True)}" alt="{escape(row["player"], quote=True)}" width="60">' if thumb else ''
                lines.append(f"| {cell} | {row['player']} | {row['team']} | {row['score']:.1f} | {'Winner' if i == award['winner_index'] else 'Finalist'} |")
            lines += ['', 'Scores preserve the recorded shortlist. No vote totals or second/third places are inferred.', '']
            credits = [f"{name} ({credit_short(row)})" for name, row in found.items() if row]
            if credits:
                lines += ['Photos, identity imagery only: ' + '; '.join(credits) + '.', '']
        if entry.get('note'):
            lines += [entry['note'], '']
    out[relative] = '\n'.join(lines)
    return out
