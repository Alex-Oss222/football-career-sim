#!/usr/bin/env python3
"""Build research-only 2013 peer references from downloaded nflverse CSVs.

No runtime inputs, branch grades or future-season results are produced.
Usage: python scripts/research/build_2013_player_sheet_benchmarks.py SOURCE_DIR
"""
import argparse
import collections
import csv
import hashlib
import json
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / 'library/data/2013_player_sheet_benchmarks.json'
SOURCES = {
    'stats_player_reg_2013.csv': 'https://github.com/nflverse/nflverse-data/releases/download/stats_player/stats_player_reg_2013.csv',
    'snap_counts_2013.csv': 'https://github.com/nflverse/nflverse-data/releases/download/snap_counts/snap_counts_2013.csv',
    'roster_2013.csv': 'https://github.com/nflverse/nflverse-data/releases/download/rosters/roster_2013.csv',
    'combine.csv': 'https://github.com/nflverse/nflverse-data/releases/download/combine/combine.csv',
}
GROUPS = {'T': 'OT', 'OT': 'OT', 'G': 'G', 'OG': 'G', 'C': 'C', 'NT': 'DT',
          'DT': 'DT', 'DE': 'DE', 'OLB': 'LB', 'ILB': 'LB', 'MLB': 'LB',
          'LB': 'LB', 'FS': 'S', 'SS': 'S', 'SAF': 'S', 'S': 'S', 'CB': 'CB'}
STAT_FIELDS = ('games completions attempts passing_yards passing_tds passing_interceptions '
               'sacks_suffered carries rushing_yards rushing_tds receptions targets receiving_yards '
               'receiving_tds fumbles_lost_total def_sacks def_interceptions def_pass_defended '
               'fg_made fg_att pat_made pat_att pt_att pt_yards pt_inside_20 pt_touchback').split()

def number(row, key):
    return float(row.get(key) or 0)

def name_key(name):
    return re.sub(r'[^a-z0-9]', '', re.sub(r'\s+(?:Jr\.?|Sr\.?|III|II)$', '', name).lower())

def rating(row):
    att = number(row, 'attempts')
    if not att:
        return None
    a = (number(row, 'completions') / att - .3) * 5
    b = (number(row, 'passing_yards') / att - 3) * .25
    c = number(row, 'passing_tds') / att * 20
    d = 2.375 - number(row, 'passing_interceptions') / att * 25
    return sum(min(2.375, max(0, x)) for x in (a, b, c, d)) / 6 * 100

def reference(rows, metric, opportunity, threshold, higher=True):
    qualified = [r for r in rows if r.get(metric) is not None and (r.get(opportunity) or 0) >= threshold]
    if not qualified:
        return None
    values = [r[metric] for r in qualified]
    top_value = (max if higher else min)(values)
    low_value = (min if higher else max)(values)
    return {
        'metric': metric, 'opportunity': opportunity, 'minimum': threshold,
        'n': len(qualified), 'average': round(statistics.mean(values), 4),
        'average_method': 'unweighted mean of qualified individual player values',
        'higher_is_better': higher,
        'top': [{'player': r['player'], 'value': round(r[metric], 4)} for r in qualified if r[metric] == top_value],
        'low': [{'player': r['player'], 'value': round(r[metric], 4)} for r in qualified if r[metric] == low_value],
    }

def build(source_dir):
    files = {}
    for filename in SOURCES:
        with (source_dir / filename).open(encoding='utf-8', newline='') as handle:
            files[filename] = list(csv.DictReader(handle))
    stats = [r for r in files['stats_player_reg_2013.csv'] if r['season'] == '2013' and r['season_type'] == 'REG']
    rosters = [r for r in files['roster_2013.csv'] if r['season'] == '2013']
    roster_by_id = {r['gsis_id']: r for r in rosters if r['gsis_id']}
    snaps = collections.defaultdict(lambda: {'offense_snaps': 0, 'defense_snaps': 0, 'positions': collections.Counter()})
    for row in files['snap_counts_2013.csv']:
        if row['season'] != '2013' or row['game_type'] != 'REG':
            continue
        key = (name_key(row['player']), GROUPS.get(row['position'], row['position']))
        for stat in ('offense_snaps', 'defense_snaps'):
            snaps[key][stat] += number(row, stat)
        snaps[key]['positions'][row['position']] += number(row, 'offense_snaps') + number(row, 'defense_snaps')
    records = []
    for row in stats:
        group = GROUPS.get(row['position'], row['position'])
        key = name_key(row['player_display_name'])
        if group == 'DB':
            candidates = [(p, s) for (name, p), s in snaps.items() if name == key and p in ('CB', 'S')]
            if len(candidates) == 1:
                group = candidates[0][0]
        exposure = snaps.get((key, group), {})
        record = {'player': row['player_display_name'], 'player_id': row['player_id'],
                  'position': group, 'source_position': row['position'], 'team': row['recent_team'],
                  'birth_date': roster_by_id.get(row['player_id'], {}).get('birth_date'),
                  **{field: number(row, field) for field in STAT_FIELDS},
                  'offense_snaps': exposure.get('offense_snaps'),
                  'defense_snaps': exposure.get('defense_snaps')}
        for metric, numerator, denominator, multiplier in (
                ('completion_pct', 'completions', 'attempts', 100),
                ('passing_ypa', 'passing_yards', 'attempts', 1),
                ('rushing_ypc', 'rushing_yards', 'carries', 1),
                ('catch_pct', 'receptions', 'targets', 100),
                ('receiving_ypr', 'receiving_yards', 'receptions', 1),
                ('fg_pct', 'fg_made', 'fg_att', 100),
                ('punt_gross_avg', 'pt_yards', 'pt_att', 1),
                ('punt_inside20_pct', 'pt_inside_20', 'pt_att', 100)):
            record[metric] = number(row, numerator) / number(row, denominator) * multiplier if number(row, denominator) else None
        record['passer_rating'] = rating(row)
        records.append(record)
    # The outcome dataset omits some linemen with no credited box-score event.
    # Recover participation only from a roster identity plus a unique snap join;
    # never manufacture zero outcome counts for these absent statistical rows.
    recorded_ids = {r['player_id'] for r in records}
    snap_aliases = {'Michael Brewster': 'Mike Brewster'}
    for player_id, row in roster_by_id.items():
        group = GROUPS.get(row['position'], row['position'])
        if player_id in recorded_ids or group not in ('OT', 'G', 'C', 'LS'):
            continue
        key = name_key(snap_aliases.get(row['full_name'], row['full_name']))
        exposure = snaps.get((key, group))
        if exposure is None:
            continue
        record = {'player': row['full_name'], 'player_id': player_id,
                  'position': group, 'source_position': row['position'],
                  'team': row.get('team'), 'birth_date': row.get('birth_date'),
                  'record_type': 'roster-and-snaps participation only; outcome row absent',
                  **{field: None for field in STAT_FIELDS},
                  'offense_snaps': exposure['offense_snaps'], 'defense_snaps': exposure['defense_snaps']}
        records.append(record)
    populations = collections.defaultdict(list)
    for row in records:
        populations[row['position']].append(row)
    references = {}
    for position, rows in populations.items():
        tests = []
        if position == 'QB':
            tests += [(m, 'attempts', 224) for m in ('completion_pct', 'passing_ypa', 'passer_rating')]
        if position == 'RB':
            tests += [('rushing_ypc', 'carries', 100)]
        if position in ('RB', 'FB', 'WR', 'TE'):
            threshold = {'RB': 20, 'FB': 10, 'WR': 40, 'TE': 30}[position]
            tests += [('catch_pct', 'targets', threshold), ('receiving_ypr', 'targets', threshold)]
        if position == 'K':
            tests += [('fg_pct', 'fg_att', 20)]
        if position == 'P':
            tests += [('punt_gross_avg', 'pt_att', 40), ('punt_inside20_pct', 'pt_att', 40)]
        if position in ('DE', 'DT', 'LB', 'CB', 'S'):
            tests += [(m, 'defense_snaps', 300) for m in ('def_sacks', 'def_interceptions', 'def_pass_defended')]
        if position in ('OT', 'G', 'C'):
            tests += [('offense_snaps', 'offense_snaps', 300)]
        references[position] = {metric: reference(rows, metric, exposure, minimum) for metric, exposure, minimum in tests}
    # Workout data is a tested subset of real 2013 rostered players, not a
    # complete league speed distribution and never a current branch measurement.
    roster_names = {name_key(r['full_name']) for r in rosters}
    workouts = []
    for row in files['combine.csv']:
        if not row['season'] or int(row['season']) > 2013 or name_key(row['player_name']) not in roster_names:
            continue
        if not row['forty']:
            continue
        workouts.append({'player': row['player_name'], 'position': GROUPS.get(row['pos'], row['pos']),
                         'test_year': int(row['season']), 'forty_seconds': float(row['forty'])})
    workout_refs = {}
    for position in sorted({r['position'] for r in workouts}):
        rows = [{**r, 'measured': 1} for r in workouts if r['position'] == position]
        workout_refs[position] = reference(rows, 'forty_seconds', 'measured', 1, higher=False)
    return {'schema_version': 1, 'season': 2013, 'season_type': 'REG',
            'purpose': 'Historical research only; production and archived workouts never determine branch talent or future development.',
            'sources': [{'file': f, 'url': url, 'sha256': hashlib.sha256((source_dir / f).read_bytes()).hexdigest()} for f, url in SOURCES.items()],
            'records': records, 'references': references, 'workouts': workouts, 'workout_references': workout_refs}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_dir', type=Path)
    args = parser.parse_args()
    result = build(args.source_dir)
    # Keep records individually reviewable rather than one megabyte-long line.
    parts = []
    for key, value in result.items():
        if key in ('records', 'workouts'):
            encoded = '[\n' + ',\n'.join('    ' + json.dumps(r, ensure_ascii=False, separators=(',', ':')) for r in value) + '\n  ]'
        else:
            encoded = json.dumps(value, ensure_ascii=False, indent=2)
        parts.append('  ' + json.dumps(key) + ': ' + encoded)
    OUTPUT.write_text('{\n' + ',\n'.join(parts) + '\n}\n', encoding='utf-8', newline='\n')
    print('Historical 2013 research written:', OUTPUT.relative_to(ROOT))

if __name__ == '__main__':
    main()
