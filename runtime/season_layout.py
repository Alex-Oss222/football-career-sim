"""Readable season folders from 2014 onward; 2013 keeps its historical layout.

These are path translations only. They never advance a clock, copy a result,
renew a contract or substitute another season's records.
"""
from pathlib import PurePosixPath
import posixpath
import re
from urllib.parse import unquote, quote, urlsplit


SEASON_MOVES = {
    'roster.md': '00_team/roster/roster.md',
    'player_ages.md': '00_team/roster/player_ages.md',
    'depth_chart.md': '00_team/depth_chart/depth_chart.md',
    'depth_chart.json': '00_team/depth_chart/game_depth_chart.json',
    'coaching_staff.md': '00_team/coaching_staff/coaching_staff.md',
    'player_profiles': '00_team/player_cards',
    'offseason/depth_chart_working.json': '00_team/depth_chart/working_depth_chart.json',
    'offseason/player_development': '00_team/player_development',
    'offseason/film': '00_team/film',
    'offseason/current_cap_worksheet.md': '09_finances/01_salary_cap/cap_worksheet.md',
    'offseason/contract_table.md': '09_finances/02_player_contracts/contracts.md',
    'offseason/contract_status_register.md': '09_finances/02_player_contracts/contract_status.md',
    'offseason/league_rails': 'league/personnel',
    'offseason/free_agency': '02_free_agency',
    'offseason/draft': '04_draft',
    'draft': '04_draft',
    'offseason/README.md': '03_offseason_training/README.md',
    'offseason/phase_plan_decisions.md': '03_offseason_training/staff_decisions.md',
    'offseason/stone_april_18_2014_decisions.md': '03_offseason_training/stone_april_18_2014_decisions.md',
    'offseason/training': '03_offseason_training/coaching_methods',
    'offseason/offseason_program': '03_offseason_training/01_phases_one_and_two',
    'offseason/rookie_minicamp': '03_offseason_training/02_rookie_minicamp',
    'offseason/otas': '03_offseason_training/03_otas',
    'offseason/mandatory_minicamp': '03_offseason_training/04_mandatory_minicamp',
    'offseason/training_camp/position_battles.md': '05_training_camp_and_preseason/03_assessments/position_battles.md',
    'offseason/training_camp/roster_decisions.md': '05_training_camp_and_preseason/04_roster_cuts/roster_decisions.md',
    'offseason/training_camp': '05_training_camp_and_preseason/01_training_camp',
    'offseason': '01_early_offseason',
    'preseason/final_roster_cuts.md': '05_training_camp_and_preseason/04_roster_cuts/final_roster_cuts.md',
    'preseason': '05_training_camp_and_preseason/02_preseason_games',
    'regular_season': '06_regular_season/games',
    'schedule': '06_regular_season/schedule',
    'standings.md': '06_regular_season/standings.md',
    'statbook.md': '06_regular_season/statistics/README.md',
    'stats': '06_regular_season/statistics/records',
    'awards': '06_regular_season/awards',
    'league_results': '06_regular_season/league_results',
    'postseason/README.md': '07_postseason/README.md',
    'postseason': '07_postseason/games',
    'pro_bowl': '07_postseason/pro_bowl',
    'closeouts': '08_season_review',
    'trades/trade_targets.md': '10_trades/01_targets_and_offers/trade_targets.md',
    'trades/trade_offers.md': '10_trades/01_targets_and_offers/trade_offers.md',
    'trades/package_i_negotiation_2014-03-20.md': '10_trades/01_targets_and_offers/package_i_negotiation_2014-03-20.md',
    'trades/march_24_2014_trade_resolution.md': '10_trades/supporting_records/march_24_2014_trade_resolution.md',
    'trades/trade_sheets_2014-03-24.md': '10_trades/supporting_records/trade_sheets_2014-03-24.md',
    'trades/README.md': '10_trades/README.md',
    'trades': '10_trades/02_completed_trades',
    'scouting': '01_early_offseason/scouting',
    'readiness.md': 'supporting_records/readiness.md',
    'operating_baseline.md': 'supporting_records/operating_baseline.md',
}
FINANCE_MOVES = {
    'career/finances/jaguars_cap.md': 'career/finances/01_salary_cap/cap_tracker.md',
    'career/finances/jaguars_contract_details.md': 'career/finances/02_player_contracts/contract_details.md',
    'career/finances/organization_finances.md': 'career/finances/04_coaching_and_organization/coaching_payroll.md',
    'career/finances/jaguars_cap_inputs.json': 'career/finances/supporting_records/financial_inputs.json',
}


def season_relative(year, relative):
    """Resolve a logical record name without probing for another year's file."""
    value = PurePosixPath(relative).as_posix()
    if value.startswith('/') or '..' in PurePosixPath(value).parts:
        raise ValueError('Season record must stay within its season')
    if year < 2014:
        return value
    for old, new in sorted(SEASON_MOVES.items(), key=lambda item: -len(item[0])):
        if value == old or value.startswith(old + '/'):
            value = new + value[len(old):]
            break
    if value.startswith(('03_offseason_training/0', '05_training_camp_and_preseason/01_training_camp/')):
        parent, name = posixpath.split(value)
        name = {'plan.md': 'staff_plan.md', 'output.md': 'training_report.md',
                'standouts.md': 'player_assessments.md'}.get(name, name)
        value = posixpath.join(parent, name)
    return value


def repository_relative(relative):
    """Translate old public paths in links and historical source references."""
    value = PurePosixPath(relative).as_posix()
    if value in FINANCE_MOVES:
        return FINANCE_MOVES[value]
    match = re.match(r'^career/(\d{4})/(.+)$', value)
    return f'career/{match[1]}/{season_relative(int(match[1]), match[2])}' if match else value


def rebase_markdown(text, source, target):
    """Keep relative Markdown links valid when a readable page changes homes."""
    source, target = str(source), str(target)
    def link(match):
        destination = match[1]
        parts = urlsplit(destination)
        if parts.scheme or parts.netloc or destination.startswith('#'):
            return match[0]
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(source), unquote(parts.path)))
        translated = repository_relative(resolved)
        if source == target and translated == resolved:
            return match[0]
        resolved = translated
        path = posixpath.relpath(resolved, posixpath.dirname(target))
        suffix = ('?' + parts.query if parts.query else '') + ('#' + parts.fragment if parts.fragment else '')
        return '](' + quote(path, safe='/._-') + suffix + ')'
    return re.sub(r'\]\(([^\s)]+)\)', link, text)


def opening_guides(year):
    """Empty successor navigation. Dates come from its own sourced calendar."""
    areas = [
        ('00_team', 'Team', 'Roster, depth chart, player cards, staff, development and film.'),
        ('01_early_offseason', 'Early offseason', 'Reviews, staffing, scouting and league-year preparation.'),
        ('02_free_agency', 'Free agency', 'Targets, offers, negotiations and actual agreements.'),
        ('03_offseason_training', 'Offseason training', 'Dated phase plans, actual training reports and player assessments.'),
        ('04_draft', 'Draft', 'Pick ownership, board, selections and rookie agreements.'),
        ('05_training_camp_and_preseason', 'Training camp and preseason', 'Camp, preseason games, assessments and roster cuts.'),
        ('06_regular_season', 'Regular season', 'Games by week, statistics, standings and awards.'),
        ('07_postseason', 'Postseason and Pro Bowl', 'Qualification, playoff games, separate statistics and honours.'),
        ('08_season_review', 'Season review and next year', 'Exit interviews, contract decisions and the annual handoff.'),
        ('09_finances', 'Finances', 'Current-year reconciliation and continuing financial obligations.'),
        ('10_trades', 'Trades', 'Targets and offers, followed by completed exchanges.'),
    ]
    result = {}
    lines = [f'# Jacksonville — {year} season', '', '[Calendar](calendar.md) · [Career finances](../finances/README.md)', '',
             f'Opening baseline carried from {year-1}. Reconcile the handoff before activating this season. Dates and deadlines come from this year’s historical calendar. No game, contract renewal or training result is implied.', '',
             '| Open | What belongs here |', '|---|---|']
    for folder, title, description in areas:
        lines.append(f'| [{title}]({folder}/README.md) | {description} |')
        result[folder+'/README.md'] = f'# {title}\n\n[{year} season](../README.md) · [Calendar](../calendar.md)\n\n{description}\n\nNo new-season event is recorded by this opening guide. Review the carried baseline before use.\n'
    lines += ['', '[Opening handoff](opening_handoff.json)', '']
    result['README.md'] = '\n'.join(lines)
    links = [('Roster', 'roster/roster.md'), ('Working depth', 'depth_chart/working_depth_chart.json'),
             ('Staff', 'coaching_staff/coaching_staff.md'), ('Player cards', 'player_cards/README.md'),
             ('Development', 'player_development/roster_profiles.md')]
    result['00_team/README.md'] += '\n'+'\n'.join(f'- [{name}]({path})' for name,path in links)+'\n'
    result['09_finances/README.md'] += '\n[Current cap worksheet](01_salary_cap/cap_worksheet.md) · [Player contracts](02_player_contracts/contracts.md) · [Contract status](02_player_contracts/contract_status.md) · [Career finances](../../finances/README.md)\n'
    return result
