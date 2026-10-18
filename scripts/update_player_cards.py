#!/usr/bin/env python3
"""Refresh statistics without rewriting opening assessments or coaching updates.

Each year's opening card remains intact through the season. Its dated coaching
updates are authored from event evidence, never generated from statistical totals.
The separate final assessment belongs to the season review after season close.
Each season row leads with Season | Team | Age | #: the Jacksonville Jaguars,
whose games the tables count; his age on the league's opening game of that
season; and the number his league card shows while he is a current Jaguar
(runtime.player_cards.jacksonville_rows): his real 2014 Jaguars listing, else
his real 2014 number with his real club when no other current Jaguar claims it.
Jacksonville has recorded no numbers of its own, so # is N/A for a player with
no game on record, one whose latest game was with another club, or one who had
already left when the row was first written. Only a current player's row in an
open season is worked out again; once he has left or the season has closed,
the row keeps the cells already written (written_row), so a closed season's
cards never follow later roster changes.
"""
import argparse
import json
import re
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.build_player_progression_roster import parse_current_roster
from scripts.build_annual_player_sheets import (slugify, season_is_complete,
    assessment_paths, assessment_card_errors, card_field)
from runtime.statbook import aggregate_receipts
from runtime.stat_tables import POSITION_GROUPS, GAMES, RETURNS, col, derived, avg, pct
from runtime.seasons import SeasonPaths, require_receipt_season
from scripts.player_photos import Photos, place_block
from runtime import player_cards
START = '<!-- yearly-statistics:start -->'
END = '<!-- yearly-statistics:end -->'
WORKING = '**Profile status:** Working player card'
OPENING = '**Assessment stage:** Opening annual assessment'

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
    paths = SeasonPaths(year, root)
    folder = paths.postseason_receipts if postseason else paths.receipts
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
    # The shared statbook predates this optional kicker field and sums it.
    # A season's longest field goal must instead be the maximum recorded kick.
    for name, line in team.get('players', {}).items():
        kicks = [r['team_stats']['Jacksonville Jaguars'].get('players', {}).get(name, {}).get('long_field_goal') for r in receipts]
        kicks = [v for v in kicks if isinstance(v, (int, float)) and not isinstance(v, bool)]
        if kicks:
            line['long_field_goal'] = max(kicks)
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

LEAD = ['Season', 'Team', 'Age', '#', 'Coverage']

def season_rows(year, names, root=ROOT):
    """{card name: (team, age, number)} for the year's season row, by the league player pages' own
    rules (runtime.player_cards.jacksonville_rows). A root without the league records (no
    repository map, as in a test fixture) has none on record: its rows read N/A."""
    root = Path(root)
    if not (root/'docs/repository_map.json').is_file():
        return {}
    return player_cards.jacksonville_rows(year, names, root)

def lead_cells(year, row=None):
    """Season | Team | Age | # for a season row; ``row`` is (team, age, number), None is N/A."""
    team, age, number = row or (player_cards.JAX, None, None)
    return [str(year), team, *(player_cards.N_A if v is None else str(v) for v in (age, number))]

def written_row(text, year):
    """(team, age, number) exactly as a card's statistics block already shows them in the year's row
    (lead_cells reads them back unchanged), or None when it has no such row under these columns."""
    if START not in text or END not in text:
        return None
    block = text.split(START,1)[1].split(END,1)[0]
    lead = '| '+' | '.join(LEAD)+' |'
    for heading in ('Regular-season statistics by year','Playoff statistics by year'):
        lines = section(block,heading).splitlines()
        header = next((l for l in lines if l.startswith('| Season |')),'')
        row = next((l for l in lines if l.startswith(f'| {year} |')),None)
        if header.startswith(lead) and row:
            team, age, number = [c.strip() for c in row.strip().strip('|').split('|')][1:4]
            return (team, *(None if v == player_cards.N_A else int(v) if v.isdigit() else v
                            for v in (age, number)))
    return None

def season_lead(year, cards, live, root=ROOT):
    """{card name: (team, age, number)} for the year's row of each card ({name: card text}). Only a
    player in ``live`` (Jacksonville controls him and the season is open) is worked out from the
    league records (season_rows); every other row keeps the cells already written, so a departure,
    a later roster change or the next season never rewrites it. A card with no such row yet is
    worked out."""
    kept = {name: written_row(text, year) for name, text in cards.items() if name not in live}
    kept = {name: row for name, row in kept.items() if row is not None}
    fresh = [name for name in cards if name not in kept]
    return {**(season_rows(year, fresh, root) if fresh else {}), **kept}

def live_players(year, root=ROOT):
    """The players whose season row is still worked out: those Jacksonville controls on the year's
    roster (practice squad included) while that season is open; none once it has closed."""
    from scripts.check_week_input_exclusivity import controlled_players_from_roster
    roster = SeasonPaths(year, root).roster
    if season_is_complete(year, root) or not roster.is_file():
        return set()
    return controlled_players_from_roster(roster)

def stats_block(year,player,pos,periods,old='',root=ROOT,row=None):
    lines = [START]
    for post,heading in [(False,'Regular-season statistics by year'),(True,'Playoff statistics by year')]:
        status,values = stat_values(player,pos,periods[post],season_is_complete(year,root),post)
        header = '| '+' | '.join([*LEAD,*[c[0] for c in columns(pos)]])+' |'
        prior = section(old,heading)
        old_header = next((l for l in prior.splitlines() if l.startswith('| Season |')),None)
        rows = [l for l in prior.splitlines() if re.match(r'^\| \d{4} \|',l) and not l.startswith(f'| {year} |')]
        if rows and old_header!=header:
            raise ValueError('Position/history columns changed; preserve older rows in a separate position block')
        rows += ['| '+' | '.join([*lead_cells(year,row),status,*values])+' |']
        lines += ['', '## '+heading,'',header,'| '+' | '.join(['---']*(len(LEAD)+len(values)))+' |',*rows]
    return '\n'.join([*lines,'',END])

def refresh_text(text,year,player,pos,periods,root=ROOT,row=None):
    """The card with its statistics block current; ``row`` is his season_rows entry (None: N/A)."""
    if START not in text or END not in text:
        raise ValueError('Missing statistics boundaries')
    old = text.split(START,1)[1].split(END,1)[0]
    return text.split(START,1)[0]+stats_block(year,player,pos,periods,old,root,row)+text.split(END,1)[1]

def card_name(text):
    """The player name in a card's title line, or None."""
    title = re.search(r'^# (.+?) — ',text,re.M)
    return title[1] if title else None

def refresh_cards(year,root=ROOT,check=False):
    periods = {p:period_data(year,p,root) for p in (False,True)}
    photos = Photos(root)
    errors = []
    cards = [path for path in sorted(SeasonPaths(year, root).record('player_profiles').glob('*.md'))
             if path.name not in ('README.md','TEMPLATE.md')]
    texts = {}
    for path in cards:
        text = path.read_text(encoding='utf-8')
        if card_name(text):
            texts.setdefault(card_name(text), text)
    identity = season_lead(year, texts, live_players(year, root), root)
    for path in cards:
        text = path.read_text(encoding='utf-8')
        if text.count(START) != 1 or text.count(END) != 1 or not text.rstrip().endswith(END):
            errors.append(f'{path.relative_to(root)}: yearly statistics must be a single block at the bottom')
            continue
        if START not in text:
            continue
        name = card_name(text)
        pos = card_field(text, 'Position')
        if not name or not any(pos in group[1] for group in POSITION_GROUPS):
            errors.append(f'{path.relative_to(root)}: missing player identity or unsupported position')
            continue
        try:
            updated = refresh_text(text,year,name,pos,periods,root,identity.get(name))
            updated = place_block(updated, photos.lookup(name), name)
        except (ValueError, KeyError) as error:
            errors.append(f'{path.relative_to(root)}: {error}')
            continue
        if updated!=text:
            if check:
                errors.append(f'{path.relative_to(root)}: stale yearly statistics')
            else:
                path.write_text(updated,encoding='utf-8',newline='\n')
    return errors

def profile_errors(year,root=ROOT,*,require_complete=True):
    """Strict for readiness; allow only wholly unstarted future sets when asked.

    Existing departed-player cards remain part of the annual evidence and are
    checked too. They are not silently dropped with a changed current roster.
    """
    if year < 2014:
        return []  # Frozen 2013 sheets use their own position-baseline validator.
    directory = SeasonPaths(year, root).record('player_profiles')
    cards = assessment_paths(directory)
    if not cards and not require_complete:
        return []
    try:
        _,_,roster = parse_current_roster(SeasonPaths(year, root).roster)
    except (OSError, ValueError) as error:
        return [f'{year}: cannot validate opening-card cohort: {error}']
    errors = []
    if not cards:
        errors.append(f'{year}: no opening annual assessments; roster coverage is incomplete')
    if not roster:
        errors.append(f'{year}: no controlled players to validate opening assessments')
    controlled = {slugify(player.player): player for player in roster}
    if len(controlled) != len(roster):
        errors.append(f'{year}: duplicate opening-card paths in controlled roster')
    for player in roster:
        path = directory/(slugify(player.player)+'.md')
        if not path.exists():
            errors.append(f'{year}: missing working player card for {player.player}')
    for path in cards:
        text = path.read_text(encoding='utf-8')
        player = controlled.get(path.stem)
        title = re.search(r'^# (.+?) — ',text,re.M)
        name = player.player if player else title[1] if title else path.stem
        pos = player.pos if player else card_field(text,'Position')
        errors.extend(assessment_card_errors(path,year,name,pos,root=root))
    if errors:
        return errors
    try:
        return refresh_cards(year,root,True)
    except (OSError, ValueError, KeyError) as error:
        return [f'{year}: cannot validate opening-card statistics: {error}']

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
