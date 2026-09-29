"""Undated 2014 opponents from historical rotation and closed branch standings.

This is not a fixture scheduler or a game runner. No real result, bye, television
slot or real standings-dependent opponent is an input. See schedule/sources.md.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path

from .league import DIVISIONS, DIVISION_OF, TEAMS
from .standings import Season, games_from_receipts

ROOT = Path(__file__).resolve().parents[1]
FOLDER = Path('career/2014/schedule')
COMPONENT_COUNTS = {'division': 6, 'conference_rotation': 4,
                    'interconference_rotation': 4, 'same_place': 2}


def branch_ranks(receipts):
    games = games_from_receipts(receipts)
    if (len(games) != 256 or len({(g.week, g.home, g.away) for g in games}) != 256
            or any(not 1 <= g.week <= 17 for g in games)):
        raise ValueError('2014 opponents require the complete 2013 regular season')
    counts = Counter(t for g in games for t in (g.home, g.away))
    slots = Counter((g.week, t) for g in games for t in (g.home, g.away))
    if set(counts) != set(TEAMS) or any(n != 16 for n in counts.values()) or max(slots.values()) != 1:
        raise ValueError('invalid 2013 club/week coverage')
    season = Season(games)
    ranks = season.division_ranks()
    if any(note['step'] is None for note in season.notes):
        raise ValueError('division tie unresolved; no alphabetical scheduling fallback')
    return ranks


def build_games(config, ranks):
    if set(ranks) != set(DIVISIONS) or any(
            len(ranks[d]) != 4 or set(ranks[d]) != set(teams)
            for d, teams in DIVISIONS.items()):
        raise ValueError('division ranks must be permutations of the actual clubs')
    codes = config['club_codes']
    if len(codes) != 32 or set(codes.values()) != set(TEAMS):
        raise ValueError('invalid 2014 club code map')
    games = []

    def add(home, away, component):
        games.append({'home': home, 'away': away, 'component': component})

    for teams in DIVISIONS.values():
        for home in teams:
            for away in teams:
                if home != away:
                    add(home, away, 'division')
    for grid in config['rotation_grids']:
        a, b = grid['first_division'], grid['second_division']
        hosts = {codes[t]: {codes[o] for o in opponents}
                 for t, opponents in grid['first_division_home_opponents'].items()}
        if set(hosts) != set(DIVISIONS[a]) or any(
                len(oo) != 2 or not oo <= set(DIVISIONS[b]) for oo in hosts.values()):
            raise ValueError('rotation grid must specify two visitors for each first-division club')
        for team in DIVISIONS[a]:
            for opponent in DIVISIONS[b]:
                home, away = (team, opponent) if opponent in hosts[team] else (opponent, team)
                add(home, away, grid['kind'])
    for home_division, away_division in config['same_place_home_to_away_divisions']:
        for home, away in zip(ranks[home_division], ranks[away_division]):
            add(home, away, 'same_place')
    games.sort(key=lambda g: (g['home'], g['away']))
    validate_games(games, ranks)
    return games


def validate_games(games, ranks):
    pairs = {(g['home'], g['away']) for g in games}
    if len(games) != 256 or len(pairs) != 256:
        raise ValueError('expected 256 unique home/away matchups')
    if any(h not in TEAMS or a not in TEAMS or h == a for h, a in pairs):
        raise ValueError('invalid club or self-matchup')
    for team in TEAMS:
        home = [g for g in games if g['home'] == team]
        away = [g for g in games if g['away'] == team]
        if len(home) != 8 or len(away) != 8:
            raise ValueError('each club must have eight designated home and eight away games')
        if Counter(g['component'] for g in home + away) != COMPONENT_COUNTS:
            raise ValueError('invalid 6/4/4/2 opponent composition')
    for g in games:
        h, a, kind = g['home'], g['away'], g['component']
        hd, ad = DIVISION_OF[h], DIVISION_OF[a]
        if kind == 'division':
            if hd != ad or (a, h) not in pairs:
                raise ValueError('division opponents must meet at both designated homes')
        elif hd == ad or (a, h) in pairs:
            raise ValueError('nondivision opponents must meet only once')
        if kind in ('conference_rotation', 'same_place') and hd[:3] != ad[:3]:
            raise ValueError('intraconference opponent outside conference')
        if kind == 'interconference_rotation' and hd[:3] == ad[:3]:
            raise ValueError('interconference opponent in same conference')
        if kind == 'same_place' and ranks[hd].index(h) != ranks[ad].index(a):
            raise ValueError('same-place pairing differs from branch standings')


def build(root=ROOT):
    root = Path(root)
    config_bytes = (root / FOLDER / 'rotation_2014.json').read_bytes()
    config = json.loads(config_bytes)
    paths = sorted((root / 'career/2013/stats/game_receipts').glob('*.json'))
    blobs = [(p.name, p.read_bytes()) for p in paths]
    ranks = branch_ranks([json.loads(data) for _, data in blobs])
    games = build_games(config, ranks)
    fixed = []
    for anchor in config['fixed_games']:
        home, away = config['club_codes'][anchor['home']], config['club_codes'][anchor['away']]
        if not any(g['home'] == home and g['away'] == away for g in games):
            raise ValueError('fixed international game is absent from the opponent matrix')
        fixed.append({**anchor, 'home': home, 'away': away})
    receipt_digest = hashlib.sha256()
    for name, data in blobs:
        receipt_digest.update(name.encode() + b'\0' + hashlib.sha256(data).digest())
    return {
        'schema_version': 1, 'season': 2014, 'as_of': '2014-02-02',
        'status': 'OPPONENTS_ONLY', 'fixture_release': '2014-04-23T20:00:00-04:00',
        'rotation_sha256': hashlib.sha256(config_bytes).hexdigest(),
        'regular_season_receipts_sha256': receipt_digest.hexdigest(),
        'division_order_2013': ranks, 'fixed_games': fixed, 'games': games,
    }


def render(data, config):
    codes = {name: code for code, name in config['club_codes'].items()}
    lines = ['# 2014 league opponents (branch)', '',
             '**As of February 2, 2014.** Generated by `python scripts/render_2014_opponents.py`.',
             '256 matchups; 32 clubs; 16 games, eight designated home and eight away per club. '
             'The two same-place opponents use closed branch division standings. '
             'This is not a dated schedule; fixtures and byes wait for April 23.', '',
             '[Source checks](sources.md) · [Schedule release](release_plan.md) · '
             '[Jacksonville view](opponents.md) · [Machine-readable matrix](league_opponents.json)', '']
    for division, teams in data['division_order_2013'].items():
        lines += [f'## {division}', '',
                  '| 2013 branch place | Club | Home opponents | Away opponents | Same-place: home / away |',
                  '|---:|---|---|---|---|']
        for place, team in enumerate(teams, 1):
            home = [g for g in data['games'] if g['home'] == team]
            away = [g for g in data['games'] if g['away'] == team]
            h = ', '.join(codes[g['away']] for g in home)
            a = ', '.join(codes[g['home']] for g in away)
            sh = next(codes[g['away']] for g in home if g['component'] == 'same_place')
            sa = next(codes[g['home']] for g in away if g['component'] == 'same_place')
            lines.append(f'| {place} | {codes[team]}: {team} | {h} | {a} | **{sh} / {sa}** |')
        lines.append('')
    lines += ['## Fixed London dates known before the branch checkpoint', '',
              '| Week | Date | Away | Designated home | Venue |', '|---:|---|---|---|---|']
    for g in data['fixed_games']:
        lines.append(f"| {g['week']} | {g['date']} | {g['away']} | {g['home']} | {g['venue']} |")
    lines += ['', 'These count as designated home games for OAK, ATL and JAX; the venue is neutral. '
              'No ordinary home-field advantage follows from the home label. No bye is assigned here. '
              'Other game dates, kickoff slots and broadcast assignments are not generated.', '']
    return '\n'.join(lines)


def products(root=ROOT):
    data = build(root)
    config = json.loads((Path(root) / FOLDER / 'rotation_2014.json').read_text())
    return {'league_opponents.json': json.dumps(data, indent=2) + '\n',
            'league_opponents.md': render(data, config)}


def check(root=ROOT):
    errors = []
    for name, expected in products(root).items():
        path = Path(root) / FOLDER / name
        if not path.exists() or path.read_text() != expected:
            errors.append(f'{FOLDER / name} is stale; run scripts/render_2014_opponents.py')
    return errors
