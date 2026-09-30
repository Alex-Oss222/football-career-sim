#!/usr/bin/env python3
"""Refresh working player cards from closed regular-season/playoff receipts."""
import argparse
import json
import re
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.build_player_progression_roster import parse_current_roster
from scripts.build_annual_player_sheets import slugify, season_is_complete
from runtime.statbook import aggregate_receipts
from runtime.stat_tables import POSITION_GROUPS, GAMES, RETURNS, col, derived, avg, pct
from runtime.seasons import require_receipt_season
START = '<!-- yearly-statistics:start -->'
END = '<!-- yearly-statistics:end -->'
WORKING = '**Profile status:** Working player card'

def section(text, heading):
    m = re.search(r'^## ' + re.escape(heading) + r'\n(.*?)(?=\n## |\Z)', text, re.M | re.S)
    return m[1].strip() if m else ''

def clean_labels(text):
    text = text.replace('Andre Branch', 'Andre \x00')
    text = re.sub(r'\b[Tt]he [Bb]ranch version\b', 'The player', text)
    text = re.sub(r'\b[Bb]ranch version\b', 'Cousins', text)
    text = re.sub(r'\bin this branch\b', 'in 2013', text)
    text = re.sub(r'\bin the 2013 branch\b', 'in the 2013 season', text)
    replacements = [(r'\b[Bb]ranch regular season\b', '2013 regular season'),
                    (r'\b[Bb]ranch playoffs(?: \(two games\))?', '2013 playoffs'),
                    (r'\b[Bb]ranch evidence\b', 'recorded evidence'),
                    (r'\b[Bb]ranch findings\b', 'recorded findings'),
                    (r'\b[Bb]ranch ?\b', '')]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)
    text = text.replace('| Trait | Sim player |', '| Trait | Player |')
    text = text.replace('Simulation 2013 Cousins', '2013 Cousins').replace('Branch 2013', '2013')
    text = text.replace('the branch version', 'the player').replace('The branch version', 'The player')
    text = text.replace('in this .', 'in 2013.').replace('in the 2013 ,', 'in the 2013 season,')
    text = text.replace('The version had', 'Cousins had').replace('| version ', '| Cousins ')
    return text.replace('Andre \x00', 'Andre Branch')

def columns(pos):
    base = next(group[2] for group in POSITION_GROUPS if pos in group[1])
    result = [GAMES, *base]
    if pos in ('RB', 'FB'):
        result += [derived('REC AVG', lambda l: avg(l['receiving_yards'], l['receptions']), 'receiving_yards', 'receptions'), col('REC LNG', 'long_reception')]
    if pos in ('RB', 'FB', 'WR', 'TE'):
        result += [derived('CATCH%', lambda l: pct(l['receptions'], l['targets']), 'receptions', 'targets')]
    if pos in ('OT', 'G', 'C'):
        result += [col('STARTS', 'line_starts'), col('OFF SNAPS', 'offensive_snaps'), col('PEN', 'penalties'), col('PEN YDS', 'penalty_yards')]
    elif pos in ('DE', 'DT', 'LB', 'CB', 'S', 'DB'):
        result += [col('DEF SNAPS', 'defensive_snaps'), col('QB HITS', 'quarterback_hits')]
        if pos in ('DE', 'DT', 'LB'):
            result += [col('INT YDS', 'interception_return_yards')]
    elif pos == 'K':
        result += [col('LONG', 'long_field_goal')]
        for label, key in [('0-19','0_19'), ('20-29','20_29'), ('30-39','30_39'), ('40-49','40_49'), ('50+','50_plus')]:
            result += [col('FGM '+label, 'field_goals_made_'+key), col('FGA '+label, 'field_goals_attempted_'+key)]
        result += [col('KO', 'kickoffs'), col('KO YDS', 'kickoff_yards'), col('KO TB', 'kickoff_touchbacks')]
    elif pos == 'P':
        result += [col('NET YDS', 'punt_net_yards'), derived('NET AVG', lambda l: avg(l['punt_net_yards'],l['punts']), 'punt_net_yards','punts'), col('RET ALLOWED','punt_returns_allowed'), col('RET YDS ALLOWED','punt_return_yards_allowed'), col('BLOCKED','punts_blocked')]
    elif pos == 'LS':
        result += [col(label,key) for label,key in [('LONG SNAPS','long_snaps'),('FG SNAPS','field_goal_snaps'),('TRY SNAPS','extra_point_snaps'),('PUNT SNAPS','punt_snaps'),('BAD SNAPS','bad_snaps'),('PEN','penalties')]]
    if pos not in ('K','P','LS'):
        result += list(RETURNS)
    return result + [col('ST TKL','special_teams_tackles')]

def period_data(year, postseason=False, root=ROOT):
    folder = root/f'career/{year}/stats'/('postseason_receipts' if postseason else 'game_receipts')
    receipts = [json.loads(p.read_text(encoding='utf-8')) for p in sorted(folder.glob('*.json'))]
    require_receipt_season(receipts, year)
    if any(r.get('game_type', 'regular') != ('postseason' if postseason else 'regular') for r in receipts):
        raise ValueError('Wrong game type in season receipt folder')
    receipts = [r for r in receipts if 'Jacksonville Jaguars' in r.get('team_stats', {})]
    book = aggregate_receipts(receipts)
    team = book['teams'].get('Jacksonville Jaguars', {})
    fields = {}
    for receipt in receipts:
        for name,line in receipt['team_stats']['Jacksonville Jaguars'].get('players', {}).items():
            recorded = {'games'} | {k for k,v in line.items() if isinstance(v,(int,float)) and not isinstance(v,bool)}
            fields[name] = fields.get(name,recorded) & recorded
    return {'players':team.get('players',{}), 'fields':fields, 'games':team.get('games',0),
            'through':max((r['week'] for r in receipts),default=0),
            'complete':book['coverage_complete'] and book.get('team_player_attribution_complete',{}).get('Jacksonville Jaguars',True)}

def stat_values(player,pos,period,closed=False,postseason=False):
    cols = columns(pos)
    if not period['games']:
        label = 'Unrecorded' if closed else 'Not played'
        return label,[label]*len(cols)
    label = ('Full regular season' if not postseason and period['games']==16 and period['complete']
             else 'Final playoffs' if postseason and closed and period['complete']
             else f"Through Week {period['through']}")
    if not period['complete']:
        label += '; partial record'
    line = period['players'].get(player,{})
    fields = period['fields'].get(player,set())
    values = []
    for label_col,fn,required in cols:
        if not required:
            required = {'CMP%':('completions','pass_attempts'),'Y/A':('passing_yards','pass_attempts'),
                        'AVG':('rushing_yards','rushing_attempts') if pos in ('RB','FB') else ('punt_yards','punts') if pos=='P' else ('receiving_yards','receptions'),
                        'FG%':('field_goals_made','field_goals_attempted'),
                        'KR AVG':('kick_return_yards','kick_returns'),'PR AVG':('punt_return_yards','punt_returns'),
                        'RTG':('completions','pass_attempts','passing_yards','passing_touchdowns','interceptions_thrown'),
                        'PTS':('field_goals_made','extra_points_made')}[label_col]
        available = bool(set(required)&fields) if label_col=='INT' and pos=='QB' else set(required)<=fields
        if not available:
            values.append('Unrecorded')
        else:
            value = fn(line)
            values.append(f'{value:g}' if isinstance(value,(int,float)) else str(value))
    return label,values

def stats_block(year,player,pos,periods,old='',root=ROOT):
    lines = [START]
    for post,heading in [(False,'Regular-season statistics by year'),(True,'Playoff statistics by year')]:
        status,values = stat_values(player,pos,periods[post],season_is_complete(year,root),post)
        header = '| '+' | '.join(['Season','Team(s)','Coverage',*[c[0] for c in columns(pos)]])+' |'
        prior = section(old,heading)
        old_header = next((l for l in prior.splitlines() if l.startswith('| Season |')),None)
        rows = [l for l in prior.splitlines() if re.match(r'^\| \d{4} \|',l) and not l.startswith(f'| {year} |')]
        if rows and old_header!=header:
            raise ValueError('Position/history columns changed; preserve older rows in a separate position block')
        rows += ['| '+' | '.join([str(year),'Jacksonville',status,*values])+' |']
        lines += ['', '## '+heading,'',header,'| '+' | '.join(['---']*(3+len(values)))+' |',*rows]
    return '\n'.join([*lines,'',END])

def refresh_text(text,year,player,pos,periods,root=ROOT):
    if START not in text or END not in text:
        raise ValueError('Missing statistics boundaries')
    old = text.split(START,1)[1].split(END,1)[0]
    return text.split(START,1)[0]+stats_block(year,player,pos,periods,old,root)+text.split(END,1)[1]

def refresh_cards(year,root=ROOT,check=False):
    periods = {p:period_data(year,p,root) for p in (False,True)}
    errors = []
    for path in sorted((root/f'career/{year}/player_profiles').glob('*.md')):
        if path.name in ('README.md','TEMPLATE.md'):
            continue
        text = path.read_text(encoding='utf-8')
        if text.count(START) != 1 or text.count(END) != 1 or not text.rstrip().endswith(END):
            errors.append(f'{path.relative_to(root)}: yearly statistics must be a single block at the bottom')
            continue
        if START not in text:
            continue
        name = re.search(r'^# (.+?) — ',text)[1]
        pos = re.search(r'^\*\*Position:\*\* (\S+)',text,re.M)[1]
        updated = refresh_text(text,year,name,pos,periods,root)
        if updated!=text:
            if check:
                errors.append(f'{path.relative_to(root)}: stale yearly statistics')
            else:
                path.write_text(updated,encoding='utf-8',newline='\n')
    return errors

def profile_errors(year,root=ROOT):
    directory = root/f'career/{year}/player_profiles'
    if not any(START in p.read_text(encoding='utf-8') for p in directory.glob('*.md')):
        return []
    _,_,roster = parse_current_roster(root/f'career/{year}/roster.md')
    errors = []
    for player in roster:
        path = directory/(slugify(player.player)+'.md')
        if not path.exists():
            errors.append(f'{year}: missing working player card for {player.player}')
            continue
        text = path.read_text(encoding='utf-8')
        if f'**Position:** {player.pos}' not in text:
            errors.append(f'{path.relative_to(root)}: wrong current position')
        if WORKING not in text and not season_is_complete(year,root):
            errors.append(f'{path.relative_to(root)}: premature final evaluation')
        if '| Trait | vs. Average | vs. Best | vs. Worst |' not in text:
            errors.append(f'{path.relative_to(root)}: missing overall comparison format')
    return errors if errors else refresh_cards(year,root,True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('year',type=int)
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    errors = profile_errors(args.year) if args.check else refresh_cards(args.year)
    for error in errors:
        print('ERROR:',error)
    if not errors:
        print(f'{args.year} player-card statistics: '+('checked' if args.check else 'updated'))
    return int(bool(errors))

if __name__=='__main__':
    raise SystemExit(main())
