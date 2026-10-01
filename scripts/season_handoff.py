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
from runtime.season_layout import opening_guides
from runtime.events import EVENT_META, resolve_path

TEAM_GATES = ('team_season_closed', 'exit_interviews', 'roster_and_medical',
              'player_contracts_and_cap', 'staff_contracts', 'draft_assets',
              'development_and_open_decisions')
HISTORY_GATES = ('league_statistics', 'awards_and_history')
DIRECTORY_SOURCES = {'player_cards', 'final_assessments'}
REQUIRED_CARRY_SOURCES = {'roster', 'staff', 'depth_chart', 'cap', 'calendar',
                          'record', 'player_ages', 'player_contracts', 'contract_status',
                          'player_finances', 'organization_finances', 'draft_assets',
                          'medical_and_roles', 'checkpoint', 'development', 'decisions'}
REFERENCE_GROUPS = ('individual_development', 'film_delivery', 'medical',
                    'coach_development', 'draft_ownership')
OPENING_GATES = ('roster_and_roles', 'player_contracts_and_cap', 'medical',
                 'staff_and_authority', 'draft_assets', 'development_and_film',
                 'calendar_and_era')


def safe(root, relative):
    mapping = None if (root/'docs/repository_map.json').is_file() else {}
    return resolve_path(root, relative, mapping=mapping)


def digest(path):
    if path.is_dir():
        # A player's earlier career rows are evidence too. Freeze names as well
        # as content so an added, removed or renamed card invalidates the review.
        entries = [(p.relative_to(path).as_posix(), digest(p))
                   for p in sorted(path.rglob('*')) if p.is_file()]
        return hashlib.sha256(json.dumps(entries).encode()).hexdigest()
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_path(root, year):
    return SeasonPaths(year, root).record('closeouts/season_handoff.json')


def reference_sources(root, year):
    """Inventory existing owners only; never copy obligations into another record."""
    root = Path(root)
    paths = SeasonPaths(year, root)
    folders = {
        'individual_development': [paths.record('offseason/player_development')],
        'film_delivery': [paths.record('offseason/film')],
        'medical': [paths.record('medical')],
        'coach_development': [root/'career/coaching_profiles',
                              paths.record('closeouts/Exit_Interviews/Coaches')],
    }
    result = {}
    for name, owners in folders.items():
        result[name] = sorted(p.relative_to(root).as_posix() for folder in owners for p in folder.rglob('*')
                              if p.is_file() and p.suffix in ('.md', '.json')
                              and p.name.lower() not in ('readme.md', 'template.md')
                              and 'template' not in p.stem.lower())
    team_review = paths.record('closeouts/season_review.md')
    if team_review.is_file():
        result['coach_development'].append(team_review.relative_to(root).as_posix())
    result['draft_ownership'] = [p.relative_to(root).as_posix()
                                for p in (paths.record('draft/pick_ownership.json'),
                                          paths.record('draft/ownership_audit.md'))
                                if p.is_file()]
    opening = paths.career/'opening_handoff.json'
    if opening.is_file():
        inherited = json.loads(opening.read_text()).get('reference_inventory', {})
        # A still-owned incident or promised packet does not disappear at the
        # next rollover just because it was deliberately not copied this year.
        for name in folders:
            result[name] = sorted(set(result[name]) | set(inherited.get(name, {}).get('sources', [])))
    else:
        result['coach_development'].sort()
    return result


def refresh_reference_inventory(root, data):
    """Add newly discovered owners without silently retaining an obsolete review."""
    inventory = data.setdefault('reference_inventory', {})
    for name, sources in reference_sources(root, data['season']).items():
        item = inventory.setdefault(name, {'status': 'OPEN', 'sources': [], 'evidence': []})
        if item['sources'] != sources:
            item['sources'] = sources
            item['status'] = 'OPEN'
    data['schema_version'] = 2


def evidence_errors(root, item, label, required=()):
    errors = []
    evidence = item.get('evidence', [])
    if not evidence:
        errors.append('Completed review lacks evidence: '+label)
    reviewed = set()
    for source in evidence:
        path = safe(root, source['path'])
        reviewed.add(path)
        if not path.is_file() or digest(path) != source.get('sha256'):
            errors.append('Missing or changed review evidence: '+label+' / '+source['path'])
    for source in required:
        if safe(root, source) not in reviewed:
            errors.append('Source not reviewed: '+label+' / '+source)
    return errors


def reference_errors(root, data, *, complete=False):
    errors = []
    inventory = data.get('reference_inventory', {})
    expected = reference_sources(root, data['season'])
    if set(inventory) != set(REFERENCE_GROUPS):
        return ['Missing or extra carry-forward reference groups; run prepare again']
    for name, item in inventory.items():
        if item.get('sources') != expected[name]:
            errors.append('Carry-forward inventory changed; review again: '+name)
        for source in item.get('sources', []):
            if not safe(root, source).is_file():
                errors.append('Missing carry-forward reference: '+source)
        status = item.get('status')
        if status not in ('OPEN', 'COMPLETE'):
            errors.append('Invalid carry-forward review status: '+name)
        elif status == 'COMPLETE':
            errors.extend(evidence_errors(root, item, name, item['sources']))
        elif complete:
            errors.append('Carry-forward review remains open: '+name)
    return errors


def prepare(root, year):
    """An existing handoff is never reset by a repeated prepare call."""
    root = Path(root).resolve()
    path = manifest_path(root, year)
    final_dir = SeasonPaths(year, root).record('closeouts/player_assessments')
    has_finals = year >= 2014 and any(p.name not in ('README.md', 'TEMPLATE.md')
                                    for p in final_dir.glob('*.md'))
    if path.exists():
        data = json.loads(path.read_text())
        if has_finals and 'final_assessments' not in data['carry_forward']:
            data['carry_forward']['final_assessments'] = final_dir.relative_to(root).as_posix()
        refresh_reference_inventory(root, data)
        path.write_text(json.dumps(data, indent=2)+'\n')
        return data
    mapping = json.loads((root / 'docs/repository_map.json').read_text())
    if mapping['active_season'] != year:
        raise ValueError('Prepare the active season; do not copy another season as its baseline')
    sources = dict(mapping['current_records'])
    sources.pop('background_depth', None)  # Legacy roster research never becomes legal successor input.
    paths = SeasonPaths(year, root)
    relative = lambda name: paths.record(name).relative_to(root).as_posix()
    sources.update(player_contracts=relative('offseason/contract_table.md'),
                   contract_status=relative('offseason/contract_status_register.md'),
                   player_finances='career/finances/supporting_records/financial_inputs.json',
                   organization_finances='career/finances/coaching_and_organization/coaching_payroll.md',
                   draft_assets=relative('draft/pick_ownership.json'),
                   medical_and_roles='state/04_Roster_and_Staff_Register.md',
                   checkpoint='state/05_Current_Season_State.md',
                   development=relative('offseason/player_development/roster_profiles.md'),
                   decisions=relative('offseason/phase_plan_decisions.md'),
                   player_cards=relative('player_profiles'))
    if has_finals:
        sources['final_assessments'] = final_dir.relative_to(root).as_posix()
    for name, value in sources.items():
        source = safe(root, value)
        if not (source.is_dir() if name in DIRECTORY_SOURCES else source.is_file()):
            raise ValueError('Missing carry-forward source: ' + value)
    data = {'schema_version': 2, 'season': year, 'next_season': year+1,
            'status': 'NOT_STARTED', 'calendar_policy': 'historical',
            'gates': {k: {'status': 'OPEN', 'evidence': []} for k in TEAM_GATES+HISTORY_GATES},
            'carry_forward': sources,
            'history': {k: relative(k) for k in ('stats','awards','league_results','postseason')},
            'source_sha256': {}, 'pending_decisions': []}
    refresh_reference_inventory(root, data)
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
    required_sources = REQUIRED_CARRY_SOURCES | ({'player_cards'} if year >= 2014 else set())
    if staging and year >= 2014:
        required_sources |= {'final_assessments'}
    for name in sorted(required_sources-set(data.get('carry_forward', {}))):
        errors.append('Missing required carry-forward owner: '+name)
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
        if not (path.is_dir() if name in DIRECTORY_SOURCES else path.is_file()):
            errors.append('Missing carry-forward source: '+name)
        elif staging and digest(path) != data.get('source_sha256', {}).get(name):
            errors.append('Carry-forward source not frozen/reviewed: '+name)
    if staging and data.get('status') != 'TEAM_CLOSED':
        errors.append('Team closeout must be TEAM_CLOSED before staging')
    if staging and year >= 2014 and 'final_assessments' not in data['carry_forward']:
        errors.append('Season-end player assessments are required before preparing next-year openings')
    if staging and year >= 2014:
        from scripts.build_annual_player_sheets import final_assessment_errors
        errors.extend(final_assessment_errors(year, root, require_complete=True, require_reviewed=True))
    errors.extend(reference_errors(root, data, complete=staging))
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


def opening_gate_sources(root, year):
    paths = SeasonPaths(year, root)
    relatives = {
        'roster_and_roles': ('roster.md', 'offseason/depth_chart_working.json'),
        'player_contracts_and_cap': ('offseason/contract_table.md',
                                     'offseason/contract_status_register.md',
                                     'offseason/current_cap_worksheet.md'),
        'medical': ('medical/current_injury_report.md',),
        'staff_and_authority': ('coaching_staff.md',),
        'draft_assets': ('draft/pick_ownership.json',),
        'development_and_film': ('offseason/player_development/roster_profiles.md',
                                 'offseason/phase_plan_decisions.md'),
        'calendar_and_era': ('calendar.md',),
    }
    return {name: [paths.record(p).relative_to(root).as_posix() for p in files]
            for name, files in relatives.items()}


def opening_errors(root, data):
    """Strict pre-activation review, including mutable opening records and cards."""
    root = Path(root).resolve()
    year = data['next_season']
    errors = check(root, {**data, 'status': 'TEAM_CLOSED'}, staging=True)
    prior_path = manifest_path(root, data['season'])
    if not prior_path.is_file():
        return errors+['Current prior-season handoff is missing']
    prior = json.loads(prior_path.read_text())
    errors.extend(check(root, prior, staging=True))
    # Team review and its sources must still be the review we staged. League
    # awards/statistics may legitimately finish later and are not compared.
    for key in ('season', 'next_season', 'calendar_policy', 'carry_forward',
                'source_sha256', 'reference_inventory', 'final_assessment_review'):
        if prior.get(key) != data.get(key):
            errors.append('Prior-season handoff changed since staging: '+key)
    for name in TEAM_GATES:
        if prior.get('gates', {}).get(name) != data.get('gates', {}).get(name):
            errors.append('Prior-season team review changed since staging: '+name)
    for origin, decisions in (('prior handoff', prior.get('pending_decisions', [])),
                              ('opening handoff', data.get('pending_decisions', []))):
        for decision in decisions:
            if (isinstance(decision, dict) and decision.get('blocks_opening') is True
                    and decision.get('status') != 'RESOLVED'):
                errors.append('Unresolved decision blocks opening: '+origin+' / '+
                              str(decision.get('id', decision.get('decision', 'unnamed decision'))))
    if data.get('status') != 'STAGED' or data.get('source_season') != year-1:
        errors.append('Opening manifest is not a staged successor')
    review = data.get('opening_review', {})
    if review.get('status') != 'COMPLETE':
        errors.append('Opening review remains incomplete')
    gates = review.get('reconciliations', {})
    if set(gates) != set(OPENING_GATES):
        errors.append('Missing or extra opening reconciliation gates')
    required = opening_gate_sources(root, year)
    for name in OPENING_GATES:
        gate = gates.get(name, {})
        if gate.get('status') != 'COMPLETE':
            errors.append('Opening reconciliation remains open: '+name)
        else:
            errors.extend(evidence_errors(root, gate, 'opening '+name, required[name]))
    paths = SeasonPaths(year, root)
    errors.extend(unplayed_opening_errors(paths))
    if not paths.roster.is_file():
        return errors+['Opening roster is missing']
    from scripts.build_player_progression_roster import parse_current_roster
    from scripts.build_annual_player_sheets import slugify
    _, _, players = parse_current_roster(paths.roster)
    expected = {paths.record('player_profiles')/(slugify(p.player)+'.md'): p
                for p in players}
    assessments = data.get('opening_assessments', [])
    targets = [safe(root, row['target']) for row in assessments]
    if len(set(targets)) != len(targets):
        errors.append('Duplicate opening assessment review')
    reviews = dict(zip(targets, assessments))
    source_roster = safe(root, data['carry_forward']['roster'])
    _, _, previous_players = parse_current_roster(source_roster)
    previous_names = {slugify(p.player)+'.md' for p in previous_players}
    for target, player in expected.items():
        row = reviews.get(target, {})
        if row.get('status') != 'COMPLETE':
            errors.append('Opening assessment requires review: '+player.player)
        if not target.is_file():
            errors.append('Missing opening assessment: '+player.player)
            continue
        text = target.read_text()
        for marker in ('**Assessment stage:** Opening annual assessment',
                       '**Profile status:** Working player card',
                       '**Season:** '+str(year), '**Position:** '+player.pos):
            if marker not in text:
                errors.append('Incomplete opening assessment identity: '+player.player)
                break
        if digest(target) != row.get('reviewed_sha256'):
            errors.append('Missing or changed opening assessment review: '+player.player)
        if target.name in previous_names:
            final = safe(root, data['carry_forward']['final_assessments'])/target.name
            previous = safe(root, data['carry_forward']['player_cards'])/target.name
            for key, source in (('final_assessment', final), ('previous_opening', previous)):
                if row.get(key) != source.relative_to(root).as_posix():
                    errors.append('Wrong opening assessment source: '+player.player+' / '+key)
                if not source.is_file() or digest(source) != row.get('source_sha256', {}).get(key):
                    errors.append('Changed opening assessment source: '+player.player+' / '+key)
            # The primary inherited assessment must actually be linked, not just
            # listed in an administrative queue beside a copied old opening.
            linked = [safe(root, (target.parent/link.split('#')[0]).relative_to(root).as_posix())
                      for link in re.findall(r'\]\(([^\s)]+)\)', text)
                      if ':' not in link and not link.startswith('#')]
            if final not in linked:
                errors.append('Opening assessment does not link the prior final: '+player.player)
            if previous.is_file():
                for heading in ('Regular-season statistics by year', 'Playoff statistics by year'):
                    def rows(value):
                        body = value.split('## '+heading+'\n', 1)[-1].split('\n## ', 1)[0]
                        return [tuple(cell.strip() for cell in line.strip('|').split('|'))
                                for line in body.splitlines()
                                if re.match(r'^\|\s*\d{4}\s*\|', line)
                                and int(line.split('|')[1]) < year]
                    if rows(previous.read_text()) != rows(text):
                        errors.append('Opening assessment changed prior '+heading.lower()+': '+player.player)
        else:
            errors.extend(evidence_errors(root, row, 'new arrival '+player.player))
    for target, row in reviews.items():
        if target not in expected:
            if row.get('status') != 'NOT_CARRIED':
                errors.append('Reconcile departed opening candidate: '+str(target.relative_to(root)))
            else:
                errors.extend(evidence_errors(root, row, 'departure '+target.name))
    # The player-sheet validator owns the full football/statistics format.
    from scripts.update_player_cards import profile_errors
    errors.extend(profile_errors(year, root, require_complete=True))
    return errors


def opening_review_digest(data):
    """Freeze the reviewed metadata, not the future contents of living records."""
    payload = {key: value for key, value in data.items() if key != 'opening_acceptance'}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def review_opening(root, data):
    errors = opening_errors(root, data)
    if errors:
        raise ValueError('; '.join(errors))
    prior_path = manifest_path(root, data['season'])
    prior = json.loads(prior_path.read_text())
    data['opening_acceptance'] = {'season': data['next_season'],
                                 'review_sha256': opening_review_digest(data)}
    target = SeasonPaths(data['next_season'], root).career/'opening_handoff.json'
    target.write_text(json.dumps(data, indent=2)+'\n')
    prior['opening_accepted'] = data['opening_acceptance']
    prior_path.write_text(json.dumps(prior, indent=2)+'\n')


def repository_opening_errors(root, active_year):
    """An active successor needs a completed review; later football may evolve."""
    path = SeasonPaths(active_year, root).career/'opening_handoff.json'
    if not path.is_file():
        # The initial 2013/2014 setup predates this process. Every later year
        # must pass it, including when an unfinished manifest was deleted.
        if active_year >= 2015:
            return ['Active successor is missing its reviewed opening manifest']
        previous = manifest_path(root, active_year-1) if active_year > 2013 else None
        if previous and previous.is_file():
            old = json.loads(previous.read_text())
            if old.get('opening_accepted'):
                return ['Active successor is missing its reviewed opening manifest']
        return []
    data = json.loads(path.read_text())
    acceptance = data.get('opening_acceptance', {})
    if acceptance.get('season') != active_year or acceptance.get('review_sha256') != opening_review_digest(data):
        return ['Active season opening has not passed review-opening, or its reviewed manifest changed']
    if data.get('opening_review', {}).get('status') != 'COMPLETE':
        return ['Active season opening review is incomplete']
    previous = json.loads(manifest_path(root, active_year-1).read_text())
    if previous.get('opening_accepted') != acceptance:
        return ['Active season opening review does not match the prior handoff']
    return []


def unplayed_opening_errors(paths):
    folders = (paths.receipts, paths.postseason_receipts,
               paths.record('preseason/statistics'))
    return ['Successor already contains game receipts; reconcile before opening: '+str(folder)
            for folder in folders if any(folder.rglob('*.json'))]


def stage(root, data):
    """Preflight every write; existing different files cannot be overwritten."""
    root = Path(root).resolve()
    errors = check(root, data, staging=True)
    if errors:
        raise ValueError('; '.join(errors))
    year, nxt = data['season'], data['next_season']
    paths = SeasonPaths(nxt, root)
    folder = paths.career
    if not paths.calendar.is_file():
        raise ValueError('Source the historical successor calendar before staging')
    unplayed = unplayed_opening_errors(paths)
    if unplayed:
        raise ValueError('; '.join(unplayed))
    copies = {'roster':'roster.md', 'staff':'coaching_staff.md',
              'depth_chart':'offseason/depth_chart_working.json',
              'player_contracts':'offseason/contract_table.md',
              'contract_status':'offseason/contract_status_register.md',
              'cap':'offseason/current_cap_worksheet.md',
              'development':'offseason/player_development/roster_profiles.md',
              'decisions':'offseason/phase_plan_decisions.md'}
    writes = {}
    opening_assessments = []
    for key, relative in copies.items():
        source = safe(root, data['carry_forward'][key]); target = paths.record(relative)
        text = source.read_text()
        if target.suffix == '.md':
            text = EVENT_META.sub('', text)
            text = (f'> Opening carry-forward from {year}; dates and financial figures retain their source checkpoint until reconciled for {nxt}. No renewal, clearance or role award is implied.\n\n' + rebase_links(text, source, target))
        writes[target] = text
    if 'player_cards' in data['carry_forward']:
        cards = safe(root, data['carry_forward']['player_cards'])
        current_cards = None
        if year >= 2014:
            from scripts.build_player_progression_roster import parse_current_roster
            from scripts.build_annual_player_sheets import slugify
            _, _, controlled = parse_current_roster(safe(root, data['carry_forward']['roster']))
            current_cards = {slugify(player.player)+'.md' for player in controlled}
            missing = current_cards-{p.name for p in cards.glob('*.md')}
            if missing:
                raise ValueError('Missing current player opening cards: '+', '.join(sorted(missing)))
        for source in sorted(cards.glob('*.md')):
            target = paths.record('player_profiles') / source.name
            if year >= 2014:
                if source.name not in current_cards:
                    continue
                final = safe(root, data['carry_forward']['final_assessments']) / source.name
                if not final.is_file() or '**Assessment stage:** Final annual assessment' not in final.read_text():
                    raise ValueError('Missing completed final assessment for '+source.name)
                # Opening and final sheets are separate authored judgments.
                # Carry their reviewed sources, not last year's opening grades
                # disguised as a fresh assessment. The authoring step uses the
                # final evaluation, with career stat rows from the prior card.
                opening_assessments.append({
                    'target': target.relative_to(root).as_posix(),
                    'final_assessment': final.relative_to(root).as_posix(),
                    'previous_opening': source.relative_to(root).as_posix(),
                    'source_sha256': {'final_assessment': digest(final),
                                      'previous_opening': digest(source)},
                    'reviewed_sha256': None,
                    'status': 'REVIEW_REQUIRED',
                })
                continue
            text = rebase_links(EVENT_META.sub('', source.read_text()), source, target)
            if source.name not in ('README.md', 'TEMPLATE.md'):
                text = re.sub(r'(^# .+? — )'+str(year)+r'( Player Profile)',
                              lambda m: m[1]+str(nxt)+m[2], text, flags=re.M)
                text = re.sub(r'^\*\*Season:\*\* '+str(year)+r'\b', '**Season:** '+str(nxt), text, flags=re.M)
                note = f'> Opening {nxt} card: assessment and ages retain their {year} checkpoint pending review. Earlier annual statistics are preserved.'
                text = text.replace('\n', '\n\n'+note+'\n', 1)
                import os
                previous = os.path.relpath(source, target.parent)
                text = re.sub(r'^\*\*Previous annual profile:\*\*[^\n]*',
                              f'**Previous annual profile:** [{year} profile]({previous})', text, flags=re.M)
                if '<!-- yearly-statistics:start -->' in text:
                    from scripts.update_player_cards import refresh_text, period_data
                    name = re.search(r'^# (.+?) — ', text)[1]
                    pos = re.search(r'^\*\*Position:\*\* (\S+)', text, re.M)[1]
                    periods = {post: period_data(nxt, post, root) for post in (False, True)}
                    text = refresh_text(text, nxt, name, pos, periods, root)
            writes[target] = text
    for relative, text in opening_guides(nxt).items():
        path = folder/relative
        if not path.exists() or path.read_text() == text:
            writes[path] = text
    handoff = {**data, 'status':'STAGED', 'source_season':year,
               'activation':'Pending administrative event and current-state reconciliation; live map unchanged',
               'reset_for_new_season':['stats','awards','game receipts','standings','phase outputs'],
               'shared_finances':'career/finances/supporting_records/financial_inputs.json',
               'opening_review': {'status': 'OPEN', 'reconciliations': {
                   name: {'status': 'OPEN', 'evidence': []} for name in OPENING_GATES}}}
    if opening_assessments:
        handoff['opening_assessments'] = opening_assessments
        handoff['activation'] += '; complete the opening assessments from the linked finals before activation'
    writes[folder/'opening_handoff.json'] = json.dumps(handoff,indent=2)+'\n'
    for path, content in writes.items():
        if path.exists() and path.read_text() != content:
            raise ValueError('Existing successor file differs; reconcile instead of overwriting: '+str(path.relative_to(root)))
    for path, content in writes.items():
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(content)
    # Future phases, awards, game inputs and receipts are created only when
    # actual work requires them, never as empty successor scaffolding.
    return list(writes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare','check','stage','check-opening','review-opening'])
    parser.add_argument('season',type=int)
    args = parser.parse_args()
    try:
        if args.action in ('check-opening', 'review-opening'):
            path = SeasonPaths(args.season, ROOT).career/'opening_handoff.json'
            data = json.loads(path.read_text())
            if data.get('next_season') != args.season:
                raise ValueError('Opening manifest belongs to a different successor season')
            errors = opening_errors(ROOT, data)
            if errors: raise ValueError('; '.join(errors))
            if args.action == 'review-opening':
                review_opening(ROOT, data)
            print('Opening review complete; live owners and clock unchanged.')
            return 0
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
