#!/usr/bin/env python3
"""Render the researched 2013 review without turning production into talent.

The dated exit-review syntheses are frozen first. Historical records are used
only for disclosed peer context and a separate same-player comparison.
"""
import argparse
import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.build_annual_player_sheets import POSITION_SHEET_TRAITS, load_season_players, target_path
from scripts.research.build_2013_player_sheet_benchmarks import name_key, rating
from runtime.statbook import aggregate_receipts
from runtime.stat_tables import position_sections
from scripts.update_player_cards import clean_labels

DATA = ROOT / 'library/data/2013_player_sheet_benchmarks.json'
REVIEW_SOURCE = ROOT / 'career/2013/player_profiles/review_findings.json'
RESEARCH_LINK = '../../../library/2013_player_sheet_research.md'
METRICS = {
    'QB': [('Passing completion rate', 'completion_pct', 'CMP%', 'attempts', 'ATT'),
           ('Passing yards per attempt', 'passing_ypa', 'Y/A', 'attempts', 'ATT'),
           ('Passer rating', 'passer_rating', 'RTG', 'attempts', 'ATT')],
    'RB': [('Rushing yards per carry', 'rushing_ypc', 'AVG', 'carries', 'CAR'),
           ('Receiving catch rate', 'catch_pct', None, 'targets', 'TGT'),
           ('Receiving yards per catch', 'receiving_ypr', None, 'targets', 'TGT')],
    'FB': [('Receiving catch rate', 'catch_pct', None, 'targets', 'TGT'),
           ('Receiving yards per catch', 'receiving_ypr', None, 'targets', 'TGT')],
    'WR': [('Receiving catch rate', 'catch_pct', None, 'targets', 'TGT'),
           ('Receiving yards per catch', 'receiving_ypr', 'AVG', 'targets', 'TGT')],
    'TE': [('Receiving catch rate', 'catch_pct', None, 'targets', 'TGT'),
           ('Receiving yards per catch', 'receiving_ypr', 'AVG', 'targets', 'TGT')],
    'K': [('Field-goal make rate (all distances)', 'fg_pct', 'FG%', 'fg_att', 'FGA')],
    'P': [('Gross punt average', 'punt_gross_avg', 'AVG', 'pt_att', 'PUNTS'),
          ('Inside-20 punt percentage', 'punt_inside20_pct', None, 'pt_att', 'PUNTS')],
}
for pos in ('DE', 'DT', 'LB', 'CB', 'S'):
    METRICS[pos] = [('Sacks (count, not pass-rush skill)', 'def_sacks', 'SCK', 'defense_snaps', None),
                    ('Interceptions (count, not coverage skill)', 'def_interceptions', 'INT', 'defense_snaps', None),
                    ('Passes defended (count, not coverage skill)', 'def_pass_defended', 'PD', 'defense_snaps', None)]

def cells(line):
    return [c.strip() for c in line.strip().strip('|').split('|')]

def branch_tables():
    text = (ROOT / 'career/2013/stats/team_player_stats.md').read_text(encoding='utf-8')
    return parse_tables(text)

def parse_tables(text):
    tables = {}
    for section in re.split(r'^## ', text, flags=re.M)[1:]:
        title = section.split('\n', 1)[0]
        lines = [cells(l) for l in section.splitlines() if l.startswith('|')]
        if len(lines) < 3:
            continue
        tables[title] = {r[0]: dict(zip(lines[0][1:], r[1:])) for r in lines[2:]}
    return tables

def postseason_tables():
    receipts = [json.loads(p.read_text(encoding='utf-8')) for p in
                sorted((ROOT / 'career/2013/stats/postseason_receipts').glob('*jacksonville*.json'))]
    book = aggregate_receipts(receipts)
    return parse_tables('\n'.join(position_sections(book['teams']['Jacksonville Jaguars']['players'], with_team=False)))

POSITION_TABLE = {'QB': 'Quarterbacks', 'RB': 'Running backs', 'FB': 'Running backs',
                  'WR': 'Wide receivers', 'TE': 'Tight ends', 'OT': 'Offensive line',
                  'G': 'Offensive line', 'C': 'Offensive line', 'DE': 'Defensive line',
                  'DT': 'Defensive line', 'LB': 'Linebackers', 'CB': 'Defensive backs',
                  'S': 'Defensive backs', 'DB': 'Defensive backs', 'K': 'Kickers',
                  'P': 'Punters', 'LS': 'Long snappers'}

def format_number(value):
    return f'{value:.1f}'

def reference_names(rows, precision=1):
    # Preserve ties without implying the first alphabetical player is the only low end.
    names = ', '.join(r['player'] for r in rows[:3])
    if len(rows) > 3:
        names += f' and {len(rows)-3} other tied players'
    return f"{names}: {rows[0]['value']:.{precision}f}"

def branch_metric(row, metric, column):
    if column:
        value = row.get(column)
        return float(value) if value not in (None, '—') else None
    if metric == 'catch_pct':
        return float(row['REC']) / float(row['TGT']) * 100 if float(row.get('TGT', 0)) else None
    if metric == 'receiving_ypr':
        return float(row['REC YDS']) / float(row['REC']) if float(row.get('REC', 0)) else None
    if metric == 'punt_inside20_pct':
        return float(row['IN20']) / float(row['PUNTS']) * 100 if float(row.get('PUNTS', 0)) else None
    return None

def pool_rows(player, row, historical):
    results = []
    for label, metric, column, opportunity, branch_column in METRICS.get(player.pos, []):
        ref = historical['references'].get(player.pos, {}).get(metric)
        if not ref:
            continue
        value = branch_metric(row, metric, column)
        sim = format_number(value) if value is not None else 'No recorded comparable production'
        if branch_column:
            exposure = float(row.get(branch_column, 0))
            if exposure < ref['minimum']:
                sim += f"; below {ref['minimum']}-opportunity threshold"
        else:
            sim += '; branch defensive snaps unrecorded; qualification unknown'
        avg = format_number(ref['average'])
        if value is not None and branch_column and exposure >= ref['minimum']:
            avg += f"; branch {'above' if value > ref['average'] else 'below' if value < ref['average'] else 'equal to'} this production mean"
        basis = f"2013 {player.pos}; {ref['opportunity']} ≥ {ref['minimum']}; n={ref['n']}; production only"
        results.append(f"| {label} | {sim} | {avg} | {reference_names(ref['top'])} | {reference_names(ref['low'])} | {basis} |")
    ref = historical['workout_references'].get(player.pos)
    if ref and ref['n'] >= 8:
        results.append(f"| Archived 40-yard dash (physical proxy only) | No timed 2013 branch measurement recovered | Tested 2013 roster subset: {ref['average']:.2f} seconds | Fastest in tested subset: {reference_names(ref['top'], 2)} seconds | Slowest in tested subset: {reference_names(ref['low'], 2)} seconds | n={ref['n']}; testing positions/years vary; incomplete roster coverage; no game-speed grade |")
    return results

def production(player, row, tables, postseason):
    if not row:
        return ('No regular-season statistical row is recorded for this player. That is a limit '
                'on the branch record, not a zero grade or evidence of no ability. ')
    post = postseason.get(POSITION_TABLE[player.pos], {}).get(player.player, {})
    headers = ['Statistic', 'Branch regular season', 'Branch playoffs (two games)']
    lines = ['| ' + ' | '.join(headers) + ' |', '| --- | ---: | ---: |']
    lines += [f"| {k} | {v} | {post.get(k, 'Unrecorded')} |" for k, v in row.items()]
    other = tables.get('Other statistics', {}).get(player.player, {}).get('Statistics')
    post_other = postseason.get('Other statistics', {}).get(player.player, {}).get('Statistics')
    if other or post_other:
        lines.append(f"| Other recorded counts | {other or 'Unrecorded'} | {post_other or 'Unrecorded'} |")
    returns = tables.get('Kick and punt returners', {}).get(player.player, {})
    post_returns = postseason.get('Kick and punt returners', {}).get(player.player, {})
    for key in dict.fromkeys([*returns, *post_returns]):
        if key not in ('Pos', 'G'):
            lines.append(f"| Returns: {key} | {returns.get(key, 'Unrecorded')} | {post_returns.get(key, 'Unrecorded')} |")
    lines += ['', '**Source:** [generated branch statbook](../stats/team_player_stats.md). '
              'G means game-day active, not starts or measured snaps. Regular season and postseason are separate.',
              'Playoffs are aggregated independently from the [two Jacksonville postseason receipts](../stats/postseason_receipts/). '
              'The [exit review](../../../' + player.evidence + ') supplies the individual interpretation and limitations.']
    if player.pos in ('OT', 'G', 'C'):
        lines.append('Sacks allowed were assigned randomly among dressed linemen in the 2013 engine. '
                     'They are preserved as recorded charges and excluded from individual blocking grades.')
    elif player.pos in ('DE', 'DT', 'LB', 'CB', 'S', 'DB'):
        lines.append('Defensive credits followed role/depth shares without individual strength or '
                     'coverage responsibility. Counts do not establish technique, fit, rush or coverage ability.')
    elif player.pos == 'P':
        lines.append('The engine sampled punt distance and outcome from a historical field-position pool. '
                     'Gross average and inside-20 totals do not establish Anger’s leg or location skill.')
    elif player.pos == 'K':
        lines.append('Make results do not identify the kick, snap, hold or protection cause. '
                     'The old long-distance make model also limits range inference.')
    return '\n'.join(lines)

def counterpart(player, historical):
    aliases = {'Mike Brewster': 'Michael Brewster'}
    key = name_key(aliases.get(player.player, player.player))
    matches = [r for r in historical['records'] if name_key(r['player']) == key]
    # Prevent the DE C.J. Wilson from being confused with the same-name corner.
    if len(matches) > 1:
        matches = [r for r in matches if r['position'] == player.pos]
    if len(matches) != 1:
        return None
    births = json.loads((ROOT/'library/data/player_birth_dates.json').read_text(encoding='utf-8'))['players']
    born = births.get(player.player, {}).get('birth_date')
    if matches[0]['birth_date'] and born and born != matches[0]['birth_date']:
        raise ValueError(f'Historical counterpart identity mismatch: {player.player}')
    return matches[0]

def real_comparison(player, row, historical):
    real = counterpart(player, historical)
    if real is None:
        return ('The real-world 2013 statistical dataset has no uniquely identified entry '
                'for this player. No real-world total or participation claim is invented. '
                'The branch assessment above stands independently.')
    entries = [('Source position', player.pos, real['source_position'])]
    pairs = {'QB': [('G', 'games'), ('ATT', 'attempts'), ('CMP', 'completions'), ('YDS', 'passing_yards'), ('TD', 'passing_tds'), ('INT', 'passing_interceptions')],
             'RB': [('G', 'games'), ('CAR', 'carries'), ('YDS', 'rushing_yards'), ('TD', 'rushing_tds'), ('REC', 'receptions'), ('REC YDS', 'receiving_yards')],
             'FB': [('G', 'games'), ('CAR', 'carries'), ('YDS', 'rushing_yards'), ('REC', 'receptions'), ('REC YDS', 'receiving_yards')],
             'WR': [('G', 'games'), ('TGT', 'targets'), ('REC', 'receptions'), ('YDS', 'receiving_yards'), ('TD', 'receiving_tds')],
             'TE': [('G', 'games'), ('TGT', 'targets'), ('REC', 'receptions'), ('YDS', 'receiving_yards'), ('TD', 'receiving_tds')],
             'K': [('G', 'games'), ('FGM', 'fg_made'), ('FGA', 'fg_att'), ('XPM', 'pat_made'), ('XPA', 'pat_att')],
             'P': [('G', 'games'), ('PUNTS', 'pt_att'), ('YDS', 'pt_yards'), ('IN20', 'pt_inside_20'), ('TB', 'pt_touchback')]}
    for key, field in pairs.get(player.pos, []):
        entries.append((key, row.get(key, 'Unrecorded'), f"{real[field]:g}"))
    if player.pos in ('DE', 'DT', 'LB', 'CB', 'S', 'DB'):
        for key, field in [('SCK', 'def_sacks'), ('INT', 'def_interceptions'), ('PD', 'def_pass_defended')]:
            entries.append((key, row.get(key, 'Unrecorded'), f"{real[field]:g}"))
    if player.pos in ('OT', 'G', 'C'):
        entries.append(('Offensive snaps', 'Unrecorded', f"{real['offense_snaps']:g}" if real['offense_snaps'] is not None else 'Unrecorded'))
    lines = ['The branch findings and theoretical staff grades above were fixed first. '
             'This is a separate real-world 2013 regular-season comparison; it cannot set or revise a branch grade.', '',
             '| Category | Branch 2013 | Real-world 2013 |', '| --- | --- | --- |']
    lines += [f'| {k} | {branch} | {actual} |' for k, branch, actual in entries]
    lines += ['', f"**Historical identity:** {real['player']} ({real['player_id']}); [2013 dataset and method]({RESEARCH_LINK}).",
              'Game-count definitions can differ: branch G counts game-day active listings; '
              'the historical statistics dataset records its own participation. Roles, support and '
              'exposure differ, so these are descriptive totals rather than matched talent tests.']
    return '\n'.join(lines)

def section_replace(text, name, body):
    pattern = rf'(## {re.escape(name)}\n).*?(?=\n## |\Z)'
    return re.sub(pattern, lambda m: m[1] + '\n' + body.strip() + '\n', text, count=1, flags=re.S)

def render(player, finding, historical, tables, postseason):
    path = target_path(2013, player.player)
    text = path.read_text(encoding='utf-8')
    row = tables.get(POSITION_TABLE[player.pos], {}).get(player.player, {})
    text = re.sub(r'^\*\*Review status:\*\*.*$',
                  '**Review status:** Completed, including exact user-authorized theoretical staff grades.  ', text, flags=re.M)
    if '**Grade basis:**' not in text:
        text = text.replace('> Final 2013 season evaluation.',
                            '**Grade basis:** My personnel judgment of the 2013 player. These exact grades include inference where the record is thin; they are not measured talent values.  \n\n> Final 2013 season evaluation.', 1)
    traits = POSITION_SHEET_TRAITS[player.pos]
    grade_section = text.split('## Position grades\n', 1)[1].split('\n## ', 1)[0]
    grades = {cells(line)[0]: cells(line) for line in grade_section.splitlines()
              if line.startswith('|') and re.fullmatch(r'[\d.]+ /10', cells(line)[1])}
    if set(grades) != {'Overall at position', *traits}:
        raise ValueError(f'{player.player}: every theoretical staff grade must be explicitly entered in the final sheet')
    table = ['| Trait | Sim player | vs. 2013 NFL average | vs. 2013 top reference | vs. 2013 low-end reference | Basis |',
             '| --- | --- | --- | --- | --- | --- |']
    notes = finding['trait_findings']
    for trait in traits:
        score = float(grades[trait][1].split()[0])
        sim = f"{score:.1f} /10. " + notes.get(trait, 'My view: ' + grades[trait][2].lower() + '.')
        average = 'Above my NFL starter standard' if score > 6 else 'At my NFL starter standard' if score == 6 else 'Below my NFL starter standard'
        top = 'At the elite trait standard' if score >= 9 else 'Below the elite trait standard'
        low = 'Above my low-end NFL trait standard' if score > 3 else 'At the low-end trait standard' if score == 3 else 'Below the low-end trait standard'
        table.append(f'| {trait} | {sim} | {average} | {top} | {low} | Theoretical staff judgment; recorded branch findings where available |')
    table += pool_rows(player, row, historical)
    table += ['', f'**Historical method and sources:** [2013 position research]({RESEARCH_LINK}). '
              'Production comparisons use qualified individual-player means; they are not ability grades. '
              'A below-threshold branch sample has no peer standing. Defensive branch qualification is '
              'unknown because snaps were not recorded. Archived workout times are an incomplete tested '
              'subset from different years, not measured 2013 game speed.', '',
              'The technical grades and comparisons are my user-authorized theoretical judgments. '
              'My comparison standards are 6.0 for a viable NFL starter trait, 9.0 for an elite trait '
              'and 3.0 for a low-end trait. These are personnel yardsticks, not measured league means '
              'or verified grades for historical peers. Production references below the trait rows '
              'remain independently sourced statistics.']
    text = section_replace(text, 'Historical NFL benchmark', '\n'.join(table))
    text = section_replace(text, 'Season production in context', production(player, row, tables, postseason))
    text = section_replace(text, 'Same-player real-world comparison', real_comparison(player, row, historical))
    text = section_replace(text, 'Play style', finding['staff_view'])
    ranked = sorted(traits, key=lambda trait: float(grades[trait][1].split()[0]), reverse=True)
    best = [f"- **My judgment: {trait} — {grades[trait][1]}.** {grades[trait][2]}." for trait in ranked[:3]]
    best += ['', '**Recorded support:**', *('- ' + item for item in finding['strengths'])]
    text = section_replace(text, 'Best traits', '\n'.join(best))
    weakest = sorted(traits, key=lambda trait: float(grades[trait][1].split()[0]))[:3]
    limits = [f"- **My judgment: {trait} — {grades[trait][1]}.** {grades[trait][2]}." for trait in weakest]
    limits += ['', '**Recorded limitations and open questions:**', *('- ' + item for item in finding['limitations'])]
    text = section_replace(text, 'Main weaknesses', '\n'.join(limits))
    uncertainty = [f"- **Branch evidence used:** [2013 exit review](../../../{player.evidence}) and its linked practice/game records.",
                   f'- **Historical benchmark sources:** [2013 position pools and archived workouts]({RESEARCH_LINK}); source URLs, raw file hashes and qualified peer rows are preserved.',
                   '- **What is established:** ' + finding['established'],
                   '- **My evaluation:** ' + finding['staff_view'],
                   '- **Judgment basis:** The user explicitly requested exact theoretical grades even when the source cannot support a measured rating. These are staff hypotheses about the frozen 2013 player. Thin evidence lowers confidence rather than leaving the number blank.',
                   '- **What would change my judgment:** Individually classified branch reps, current physical measurements and comparable same-season film. Neither later real-world success nor failure can revise this baseline.',
                   '', '**One-line description:**  ', player.identity]
    return clean_labels(section_replace(text, 'Evidence and uncertainty', '\n'.join(uncertainty)))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    _, players = load_season_players(2013)
    findings = json.loads(REVIEW_SOURCE.read_text(encoding='utf-8'))['players']
    historical = json.loads(DATA.read_text(encoding='utf-8'))
    tables = branch_tables()
    postseason = postseason_tables()
    stale = []
    for player in players:
        if player.player == 'Kirk Cousins':
            continue  # Preserve the user's previously researched worked example.
        result = render(player, findings[player.player], historical, tables, postseason)
        path = target_path(2013, player.player)
        if args.check:
            if path.read_text(encoding='utf-8') != result:
                stale.append(player.player)
        else:
            path.write_text(result, encoding='utf-8', newline='\n')
    if stale:
        print('STALE:', ', '.join(stale))
        return 1
    print('2013 remaining-player reviews:', 'checked' if args.check else 'written', '60')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
