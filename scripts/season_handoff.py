#!/usr/bin/env python3
"""Prepare/check/stage an annual handoff without simulating or changing live owners."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from runtime.seasons import SeasonPaths

TEAM_GATES = ('team_season_closed', 'exit_interviews', 'roster_and_medical',
              'player_contracts_and_cap', 'staff_contracts', 'draft_assets',
              'development_and_open_decisions')
HISTORY_GATES = ('league_statistics', 'awards_and_history')


def safe(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Handoff path leaves repository')
    return path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_path(root, year):
    return SeasonPaths(year, root).career / 'closeouts/season_handoff.json'


def prepare(root, year):
    """An existing handoff is never reset by a repeated prepare call."""
    root = Path(root).resolve()
    path = manifest_path(root, year)
    if path.exists():
        return json.loads(path.read_text())
    mapping = json.loads((root / 'docs/repository_map.json').read_text())
    if mapping['active_season'] != year:
        raise ValueError('Prepare the active season; do not copy another season as its baseline')
    sources = dict(mapping['current_records'])
    sources.pop('background_depth', None)  # Legacy roster research never becomes legal successor input.
    sources.update(player_contracts=f'career/{year}/offseason/contract_table.md',
                   contract_status=f'career/{year}/offseason/contract_status_register.md',
                   player_finances='career/finances/jaguars_cap_inputs.json',
                   organization_finances='career/finances/organization_finances.md',
                   draft_assets=f'career/{year}/draft/pick_ownership.json',
                   medical_and_roles='state/04_Roster_and_Staff_Register.md',
                   checkpoint='state/05_Current_Season_State.md',
                   development=f'career/{year}/offseason/player_development/roster_profiles.md',
                   decisions=f'career/{year}/offseason/phase_plan_decisions.md')
    for value in sources.values():
        if not safe(root, value).is_file():
            raise ValueError('Missing carry-forward source: ' + value)
    data = {'schema_version': 1, 'season': year, 'next_season': year+1,
            'status': 'NOT_STARTED', 'calendar_policy': 'historical',
            'gates': {k: {'status': 'OPEN', 'evidence': []} for k in TEAM_GATES+HISTORY_GATES},
            'carry_forward': sources,
            'history': {k: f'career/{year}/{k}' for k in ('stats','awards','league_results','postseason')},
            'source_sha256': {}, 'pending_decisions': []}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2)+'\n')
    return data


def check(root, data, *, staging=False):
    root = Path(root).resolve()
    errors = []
    year = data['season']
    SeasonPaths(year, root)
    if data.get('next_season') != year+1 or data.get('calendar_policy') != 'historical':
        errors.append('Successor identity/calendar policy is invalid')
    if set(data.get('gates', {})) != set(TEAM_GATES+HISTORY_GATES):
        errors.append('Missing or extra closeout gates')
    required = TEAM_GATES if staging else ()
    for name, gate in data.get('gates', {}).items():
        if gate.get('status') not in ('OPEN','COMPLETE'):
            errors.append('Invalid gate status: '+name)
        if name in required and gate.get('status') != 'COMPLETE':
            errors.append('Closeout remains open: '+name)
        if gate.get('status') == 'COMPLETE':
            if not gate.get('evidence'):
                errors.append('Completed gate lacks evidence: '+name)
            for evidence in gate.get('evidence', []):
                path = safe(root, evidence['path'])
                if not path.is_file() or digest(path) != evidence.get('sha256'):
                    errors.append('Missing or changed closeout evidence: '+name)
    for name, relative in data['carry_forward'].items():
        path = safe(root, relative)
        if not path.is_file():
            errors.append('Missing carry-forward source: '+name)
        elif staging and digest(path) != data.get('source_sha256', {}).get(name):
            errors.append('Carry-forward source not frozen/reviewed: '+name)
    if staging and data.get('status') != 'TEAM_CLOSED':
        errors.append('Team closeout must be TEAM_CLOSED before staging')
    return errors


def rebase_links(text, source, target):
    import os
    def replace(match):
        value = match[1]
        if ':' in value or value.startswith('#'):
            return match[0]
        path, sep, anchor = value.partition('#')
        return '](' + os.path.relpath((source.parent/path).resolve(), target.parent) + (sep+anchor if sep else '') + ')'
    return re.sub(r'\]\(([^\s)]+)\)', replace, text)


def stage(root, data):
    """Preflight every write; existing different files cannot be overwritten."""
    root = Path(root).resolve()
    errors = check(root, data, staging=True)
    if errors:
        raise ValueError('; '.join(errors))
    year, nxt = data['season'], data['next_season']
    folder = SeasonPaths(nxt, root).career
    if not (folder/'calendar.md').is_file():
        raise ValueError('Source the historical successor calendar before staging')
    copies = {'roster':'roster.md', 'staff':'coaching_staff.md',
              'depth_chart':'offseason/depth_chart_working.json',
              'player_contracts':'offseason/contract_table.md',
              'contract_status':'offseason/contract_status_register.md',
              'cap':'offseason/current_cap_worksheet.md',
              'development':'offseason/player_development/roster_profiles.md',
              'decisions':'offseason/phase_plan_decisions.md'}
    writes = {}
    for key, relative in copies.items():
        source = safe(root, data['carry_forward'][key]); target = folder/relative
        text = source.read_text()
        if target.suffix == '.md':
            text = (f'> Opening carry-forward from {year}; dates and financial figures retain their source checkpoint until reconciled for {nxt}. No renewal, clearance or role award is implied.\n\n' + rebase_links(text, source, target))
        writes[target] = text
    handoff = {**data, 'status':'STAGED', 'source_season':year,
               'activation':'Pending administrative event and current-state reconciliation; live map unchanged',
               'reset_for_new_season':['stats','awards','game receipts','standings','phase outputs'],
               'shared_finances':'career/finances/jaguars_cap_inputs.json'}
    writes[folder/'opening_handoff.json'] = json.dumps(handoff,indent=2)+'\n'
    for path, content in writes.items():
        if path.exists() and path.read_text() != content:
            raise ValueError('Existing successor file differs; reconcile instead of overwriting: '+str(path.relative_to(root)))
    for path, content in writes.items():
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(content)
    # No old totals, awards, game inputs or receipts are copied into new storage.
    for relative in ('stats/game_receipts','stats/postseason_receipts','awards','closeouts'):
        (folder/relative).mkdir(parents=True,exist_ok=True)
    return list(writes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare','check','stage'])
    parser.add_argument('season',type=int)
    args = parser.parse_args()
    try:
        data = prepare(ROOT,args.season) if args.action=='prepare' else json.loads(manifest_path(ROOT,args.season).read_text())
        if args.action=='stage':
            print('Staged %d successor files; live owners and clock unchanged.' % len(stage(ROOT,data)))
        else:
            errors = check(ROOT,data)
            if errors: raise ValueError('; '.join(errors))
            print('Handoff structure valid; closeout status: '+data['status'])
        return 0
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print('HANDOFF BLOCKED: '+str(exc));return 1


if __name__=='__main__':
    raise SystemExit(main())
