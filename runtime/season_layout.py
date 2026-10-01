"""Chronological season folders from 2014 onward; 2013 keeps its historical layout.

These are path translations only. They never advance a clock, copy a result,
renew a contract or substitute another season's records.
"""
from pathlib import PurePosixPath
import posixpath
import re
from urllib.parse import unquote, quote, urlsplit


LEGACY_MOVES = {
    'roster.md': 'team/roster/roster.md',
    'player_ages.md': 'team/roster/player_ages.md',
    'depth_chart.md': 'team/depth_chart/depth_chart.md',
    'depth_chart.json': 'team/depth_chart/game_depth_chart.json',
    'coaching_staff.md': 'team/coaching_staff/coaching_staff.md',
    'player_profiles': 'team/player_cards',
    'offseason/depth_chart_working.json': 'team/depth_chart/working_depth_chart.json',
    'offseason/player_development': 'team/player_development',
    'offseason/film': 'team/film',
    'offseason/current_cap_worksheet.md': 'finances/salary_cap/cap_worksheet.md',
    'offseason/contract_table.md': 'finances/player_contracts/contracts.md',
    'offseason/contract_status_register.md': 'finances/player_contracts/contract_status.md',
    'offseason/league_rails': 'league/personnel',
    'offseason/free_agency': 'free_agency',
    'offseason/draft': 'draft',
    'draft': 'draft',
    'offseason/README.md': 'offseason_training/README.md',
    'offseason/phase_plan_decisions.md': 'offseason_training/staff_decisions.md',
    'offseason/stone_april_18_2014_decisions.md': 'offseason_training/stone_april_18_2014_decisions.md',
    'offseason/training': 'offseason_training/coaching_methods',
    'offseason/offseason_program': 'offseason_training/phases_one_and_two',
    'offseason/rookie_minicamp': 'offseason_training/rookie_minicamp',
    'offseason/otas': 'offseason_training/otas',
    'offseason/mandatory_minicamp': 'offseason_training/mandatory_minicamp',
    'offseason/training_camp/position_battles.md': 'training_camp_and_preseason/assessments/position_battles.md',
    'offseason/training_camp/roster_decisions.md': 'training_camp_and_preseason/roster_cuts/roster_decisions.md',
    'offseason/training_camp': 'training_camp_and_preseason/training_camp',
    'offseason': 'early_offseason',
    'preseason/final_roster_cuts.md': 'training_camp_and_preseason/roster_cuts/final_roster_cuts.md',
    'preseason': 'training_camp_and_preseason/preseason_games',
    'regular_season': 'regular_season/games',
    'schedule': 'regular_season/schedule',
    'standings.md': 'regular_season/standings.md',
    'statbook.md': 'regular_season/statistics/README.md',
    'stats': 'regular_season/statistics/records',
    'awards': 'regular_season/awards',
    'league_results': 'regular_season/league_results',
    'postseason/README.md': 'postseason/README.md',
    'postseason': 'postseason/games',
    'pro_bowl': 'postseason/pro_bowl',
    'closeouts': 'season_review',
    'trades/trade_targets.md': 'trades/targets_and_offers/trade_targets.md',
    'trades/trade_offers.md': 'trades/targets_and_offers/trade_offers.md',
    'trades/package_i_negotiation_2014-03-20.md': 'trades/targets_and_offers/package_i_negotiation_2014-03-20.md',
    'trades/march_24_2014_trade_resolution.md': 'trades/supporting_records/march_24_2014_trade_resolution.md',
    'trades/trade_sheets_2014-03-24.md': 'trades/supporting_records/trade_sheets_2014-03-24.md',
    'trades/README.md': 'trades/README.md',
    'trades': 'trades/completed_trades',
    'scouting': 'early_offseason/scouting',
    'readiness.md': 'supporting_records/readiness.md',
    'operating_baseline.md': 'supporting_records/operating_baseline.md',
}
# The first readable layout remains an input alias for frozen source references.
LEGACY_TRAINING_FOLDERS = tuple(
    'offseason_training/%s/' % phase
    for phase in ('phases_one_and_two', 'rookie_minicamp', 'otas', 'mandatory_minicamp')
) + ('training_camp_and_preseason/training_camp/',)
SEASON_MOVES = {
    'team/roster/medical_history.md': '00_Team_Operations/Medical/medical_history.md',
    'team/roster': '00_Team_Operations/Team/Roster',
    'team/depth_chart': '00_Team_Operations/Team/Depth_Chart',
    'team/player_cards': '00_Team_Operations/Team/Player_Cards',
    'team/coaching_staff': '00_Team_Operations/Staff',
    'team/player_development': '00_Team_Operations/Player_Development',
    'team/film': '00_Team_Operations/Film',
    'team/medical': '00_Team_Operations/Medical',
    'medical': '00_Team_Operations/Medical',
    'team': '00_Team_Operations/Team',
    'trades': '00_Team_Operations/Trades',
    'free_agency': '00_Team_Operations/Free_Agency',
    'finances': '00_Team_Operations/Finances',
    'early_offseason': '01_Early_Offseason',
    'offseason_training/phase_one': '02_Offseason_Training/Phase_One',
    'offseason_training/phase_two': '02_Offseason_Training/Phase_Two',
    'offseason_training/phases_one_and_two': '02_Offseason_Training/Phase_Two',
    'offseason_training/rookie_minicamp': '02_Offseason_Training/Rookie_Minicamp',
    'offseason_training/otas': '02_Offseason_Training/OTAs',
    'offseason_training/mandatory_minicamp': '02_Offseason_Training/Mandatory_Minicamp',
    'offseason_training/coaching_methods': '02_Offseason_Training/Coaching_Methods',
    'offseason_training': '02_Offseason_Training',
    'draft': '03_Draft',
    'training_camp_and_preseason/training_camp': '04_Training_Camp_and_Preseason/Training_Camp',
    'training_camp_and_preseason/preseason_games': '04_Training_Camp_and_Preseason/Preseason_Games',
    'training_camp_and_preseason/position_battles': '04_Training_Camp_and_Preseason/Position_Battles',
    'training_camp_and_preseason/training_camp/player_assessments.md': '04_Training_Camp_and_Preseason/Training_Camp/training_report.md',
    'training_camp_and_preseason/assessments/position_battles.md': '04_Training_Camp_and_Preseason/Training_Camp/training_report.md',
    'training_camp_and_preseason/assessments': '04_Training_Camp_and_Preseason/Position_Battles',
    'training_camp_and_preseason/roster_cuts': '04_Training_Camp_and_Preseason/Roster_Decisions',
    'training_camp_and_preseason': '04_Training_Camp_and_Preseason',
    'regular_season/games': '05_Regular_Season/Games',
    'regular_season/schedule': '05_Regular_Season/Schedule',
    'regular_season/statistics': '05_Regular_Season/Statistics',
    'regular_season/awards': '05_Regular_Season/Awards',
    'regular_season/league_results': '05_Regular_Season/League_Results',
    'regular_season': '05_Regular_Season',
    'postseason/games': '06_Postseason/Games',
    'postseason/statistics': '06_Postseason/Statistics',
    'postseason/awards': '06_Postseason/Awards',
    'postseason/pro_bowl': '06_Postseason/Pro_Bowl',
    'postseason': '06_Postseason',
    'season_review/player_assessments': '07_Season_Review/Player_Assessments',
    'season_review': '07_Season_Review',
    'league': 'League',
    'supporting_records': 'Supporting_Records',
    'calendar.md': 'Calendar.md',
    'record.md': 'Record.md',
    'ledger.md': 'Record.md',
}
for _old_phase, _new_phase in (
    ('phase_one', 'Phase_One'), ('phase_two', 'Phase_Two'),
    ('phases_one_and_two', 'Phase_Two'), ('rookie_minicamp', 'Rookie_Minicamp'),
    ('otas', 'OTAs'), ('mandatory_minicamp', 'Mandatory_Minicamp'),
):
    SEASON_MOVES[f'offseason_training/{_old_phase}/player_assessments.md'] = (
        f'02_Offseason_Training/{_new_phase}/training_report.md')
TRAINING_PHASE_FOLDERS = tuple(
    '02_Offseason_Training/%s/' % phase
    for phase in ('Phase_One', 'Phase_Two', 'Rookie_Minicamp', 'OTAs', 'Mandatory_Minicamp')
) + ('04_Training_Camp_and_Preseason/Training_Camp/',)
FINANCE_MOVES = {
    'career/finances/jaguars_cap.md': 'career/finances/salary_cap/cap_tracker.md',
    'career/finances/jaguars_contract_details.md': 'career/finances/player_contracts/contract_details.md',
    'career/finances/organization_finances.md': 'career/finances/coaching_and_organization/coaching_payroll.md',
    'career/finances/jaguars_cap_inputs.json': 'career/finances/supporting_records/financial_inputs.json',
}
REPOSITORY_ALIASES = {
    'foundation/06_Chronology_Game_Ledger_and_Handoff.md': 'foundation/06_Event_Records_and_Handoff.md',
}


def _within_season(relative):
    value = PurePosixPath(relative).as_posix()
    if value.startswith('/') or '..' in PurePosixPath(value).parts:
        raise ValueError('Season record must stay within its season')
    return value


def _translate(value, mapping):
    for old, new in sorted(mapping.items(), key=lambda item: -len(item[0])):
        if value == old or value.startswith(old + '/'):
            return new + value[len(old):]
    return value


def _prior_readable_path(value):
    parts = value.split('/')
    children = {
        'regular_season': {'README.md', 'games', 'schedule', 'statistics', 'awards', 'league_results', 'standings.md'},
        'postseason': {'README.md', 'games', 'statistics', 'awards', 'pro_bowl'},
        'trades': {'README.md', 'targets_and_offers', 'completed_trades', 'supporting_records'},
    }
    return len(parts) > 1 and parts[0] in children and parts[1] in children[parts[0]]


def readable_relative(year, relative):
    """Map a physical path in the prior layout, without logical-name ambiguity."""
    value = _within_season(relative)
    if year < 2014:
        return value
    value = _translate(value, SEASON_MOVES)
    value = re.sub(r'^(04_Training_Camp_and_Preseason/Preseason_Games/)game_(\d{2})(?=/|$)',
                   r'\1Game_\2', value)
    value = re.sub(r'^(05_Regular_Season/Games/)week_(\d{2})', r'\1Week_\2', value)
    return value


def season_relative(year, relative):
    """Resolve logical and both readable layouts, preserving frozen old references."""
    value = _within_season(relative)
    if year < 2014:
        return value
    if value.split('/')[0] in {p.split('/')[0] for p in SEASON_MOVES.values()}:
        return value
    if not _prior_readable_path(value) and not any(value == new or value.startswith(new + '/') for new in LEGACY_MOVES.values()):
        value = _translate(value, LEGACY_MOVES)
    if value.startswith(LEGACY_TRAINING_FOLDERS):
        parent, name = posixpath.split(value)
        value = posixpath.join(parent, {'plan.md': 'staff_plan.md', 'output.md': 'training_report.md',
                                      'standouts.md': 'player_assessments.md'}.get(name, name))
    value = readable_relative(year, value)
    if value.startswith(TRAINING_PHASE_FOLDERS):
        parent, name = posixpath.split(value)
        name = {'plan.md': 'staff_plan.md', 'output.md': 'training_report.md',
                'standouts.md': 'player_assessments.md'}.get(name, name)
        value = posixpath.join(parent, name)
    return value


def repository_relative(relative):
    """Translate old public paths in links and historical source references."""
    value = PurePosixPath(relative).as_posix()
    if value in REPOSITORY_ALIASES:
        return REPOSITORY_ALIASES[value]
    if value in FINANCE_MOVES:
        return FINANCE_MOVES[value]
    match = re.match(r'^career/(\d{4})/(.+)$', value)
    if not match:
        return value
    year, local = int(match[1]), match[2]
    # Directory links in existing readable pages mean the phase, not the
    # historical logical "regular_season"/"postseason" game-directory alias.
    current_roots = ('team', 'early_offseason', 'free_agency', 'finances',
                     'offseason_training', 'training_camp_and_preseason',
                     'season_review', 'league', 'supporting_records')
    readable = local.split('/')[0] in current_roots or _prior_readable_path(local)
    if local in ('regular_season', 'regular_season/README.md', 'postseason', 'postseason/README.md', 'trades'):
        readable = True
    destination = readable_relative(year, local) if readable else season_relative(year, local)
    return f'career/{year}/{destination}'


def rebase_markdown(text, source, target, aliases=None):
    """Keep relative Markdown links valid when a readable page changes homes."""
    source, target = str(source), str(target)
    def link(match):
        destination = match[1]
        parts = urlsplit(destination)
        if parts.scheme or parts.netloc or destination.startswith('#'):
            return match[0]
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(source), unquote(parts.path)))
        original = resolved
        fragment = parts.fragment
        if re.match(r'^career/20\d\d/(?:training_camp_and_preseason/assessments/position_battles\.md|04_Training_Camp_and_Preseason/Training_Camp/position_review\.md)$', resolved):
            year = resolved.split('/')[1]
            resolved = f'career/{year}/04_Training_Camp_and_Preseason/Training_Camp/training_report.md'
            fragment = 'personnel-questions-after-august-1'
        combined = re.match(r'^career/(20\d\d)/(?:offseason_training/phases_one_and_two|offseason/offseason_program)/(training_report|staff_plan|output|plan|player_assessments|standouts)\.md$', resolved)
        if combined and int(combined[1]) >= 2014:
            one = {'before-the-program-april-18-staff-review', 'phase-one-april-21-to-may-1',
                   'may-1-instruction-the-four-unsigned-tenders', 'may-2-phase-one-handoff',
                   'phase-one-learning-the-calls-in-the-room'}
            if fragment in one:
                name = 'staff_plan.md' if combined[2] in ('staff_plan', 'plan') else 'training_report.md'
                resolved = f'career/{combined[1]}/02_Offseason_Training/Phase_One/{name}'
                if fragment == 'phase-one-learning-the-calls-in-the-room':
                    fragment = 'learning-the-calls-in-the-room'
            elif fragment == 'phase-two-technique-and-job-connection':
                resolved = f'career/{combined[1]}/02_Offseason_Training/Phase_Two/staff_plan.md'
                fragment = 'three-weeks-of-field-teaching'
        seen = set()
        while resolved in (aliases or {}):
            if resolved in seen:
                raise ValueError('Cyclic Markdown path alias: '+resolved)
            seen.add(resolved)
            resolved = aliases[resolved]
        translated = repository_relative(resolved)
        if source == target and translated == original and fragment == parts.fragment:
            return match[0]
        resolved = translated
        path = posixpath.relpath(resolved, posixpath.dirname(target))
        suffix = ('?' + parts.query if parts.query else '') + ('#' + fragment if fragment else '')
        return '](' + quote(path, safe='/._-') + suffix + ')'
    return re.sub(r'\]\(([^\s)]+)\)', link, text)


def opening_guides(year):
    """One successor guide, with links only to files the handoff actually carries."""
    links = [('Roster', 'roster.md'), ('Working depth', 'offseason/depth_chart_working.json'),
             ('Staff', 'coaching_staff.md'), ('Development', 'offseason/player_development/roster_profiles.md'),
             ('Player contracts', 'offseason/contract_table.md'),
             ('Contract status', 'offseason/contract_status_register.md'),
             ('Cap worksheet', 'offseason/current_cap_worksheet.md')]
    lines = [f'# Jacksonville {year}', '', '[Calendar](Calendar.md) · [Career finances](../finances/README.md)', '',
             f'Opening records carried from {year-1} await reconciliation. No new-season participation, agreement or game is recorded.', '',
             '| Current record | Open |', '|---|---|']
    lines += [f'| {title} | [{title}]({season_relative(year, path)}) |' for title, path in links]
    lines += ['', 'The season proceeds through early offseason, offseason training, the draft, camp and preseason, the regular season, any postseason, and season review. Create each phase record when work belongs there; do not create empty reports or battle cards.', '',
              '[Opening handoff](opening_handoff.json)', '']
    return {'README.md': '\n'.join(lines)}
