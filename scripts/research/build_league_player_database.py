#!/usr/bin/env python3
"""Reproducible 2013 league research inventory, never a live TeamInput.

Capture once: --source-dir DIR --capture --checked-on YYYY-MM-DD
Rebuild offline: no arguments. Verify outputs: --check.
Only whitelisted historical fields enter the committed source snapshot.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
from datetime import date
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.research.build_2013_week1_depth_charts import CLUBS, ROSTER_CODE, UNPLACED_CLAIMS, draft_moves

REL = Path('career/2014/League/personnel')
AS_OF = '2014-02-02'
BEGIN = '<!-- BEGIN GENERATED LEAGUE DATABASE -->'
END = '<!-- END GENERATED LEAGUE DATABASE -->'
URLS = {
    'roster_weekly_2013.csv': 'https://github.com/nflverse/nflverse-data/releases/download/weekly_rosters/roster_weekly_2013.csv',
    'roster_2013.csv': 'https://github.com/nflverse/nflverse-data/releases/download/rosters/roster_2013.csv',
    'players.csv': 'https://github.com/nflverse/nflverse-data/releases/download/players/players.csv',
    'historical_contracts.csv.gz': 'https://github.com/nflverse/nflverse-data/releases/download/contracts/historical_contracts.csv.gz',
    'draft_picks.csv': 'https://github.com/nflverse/nflverse-data/releases/download/draft_picks/draft_picks.csv',
    'depth_charts_2013.csv': 'https://github.com/nflverse/nflverse-data/releases/download/depth_charts/depth_charts_2013.csv',
}
CODE = {v:k for k,v in ROSTER_CODE.items()}
TEAMS = {**CLUBS, 'JAX':'Jacksonville Jaguars'}
# Reviewed against the branch initial roster and nflverse identity register.
# Marshall is the 2012 linebacker, not the 2006 wide receiver.
UNPLACED_IDS = {'Austen Lane':'00-0027752', 'Brandon Marshall':'00-0029620', 'Isaiah Stanback':'00-0025490'}
STATUSES = {'ACT':'Active', 'DEV':'Practice squad', 'RES':'Reserve', 'INA':'Inactive',
            'SUS':'Suspended', 'RSN':'Reserve, non-football', 'PUP':'PUP', 'CUT':'Released',
            'TRD':'Practice-squad release', 'TRC':'Practice-squad release', 'TRT':'Practice-squad release',
            'RSR':'Released from reserve', 'NWT':'Waived indicator', 'RET':'Retired indicator', 'EXE':'Exempt'}


def clean(value):
    return None if value is None or str(value).strip() in {'', 'NA', 'N/A', 'NaN'} else str(value).strip()


def number(value):
    try:
        f=float(value)
        return int(f) if f.is_integer() else None
    except (TypeError, ValueError):
        return None


def norm(value):
    return re.sub(r'[^a-z0-9]', '', (value or '').lower())


def code(value):
    return CODE.get(value, value)


def contract_clubs(value):
    aliases={norm(k):k for k in TEAMS}
    aliases.update({norm(v):k for k,v in TEAMS.items()})
    aliases.update({norm(v.split()[-1]):k for k,v in TEAMS.items()})
    aliases.update({'redskins':'WAS','commanders':'WAS','footballteam':'WAS'})
    return {aliases[norm(x)] for x in (value or '').split('/') if norm(x) in aliases}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_text(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2)+'\n'


def database_text(obj):
    """Keep one player per line for reviewable generated diffs."""
    metadata={k:v for k,v in obj.items() if k!='players'}
    head=json_text(metadata).rstrip()[:-1].rstrip()
    return head+',\n  "players": [\n'+',\n'.join('    '+json.dumps(p,ensure_ascii=False,sort_keys=True) for p in obj['players'])+'\n  ]\n}\n'


def read_csv(path):
    op = gzip.open if path.suffix=='.gz' else open
    with op(path, 'rt', encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def project(row, keys):
    return {k:clean(row.get(k)) for k in keys.split()}


def controlled(root):
    """Include reserve/retired and PS, not just the active 53."""
    result={}; header=None
    for line in (root/'career/2013/roster.md').read_text().splitlines():
        if not line.startswith('|'):
            header=None; continue
        cells=[x.strip() for x in line.strip('|').split('|')]
        if 'Player' in cells and 'Pos' in cells:
            header=cells; continue
        if not header or set(cells[0]) <= {'-', ':'}:
            continue
        status_col=next((i for i,x in enumerate(header) if x.lower()=='status'),None)
        if status_col is not None:
            status=cells[status_col]
            if status=='Active 53' or status.startswith('Offseason roster') or status=='Practice squad' or status.startswith('Reserve/'):
                result[cells[header.index('Player')]]={'position':cells[header.index('Pos')], 'status':status}
    if not result:
        raise ValueError('No Jacksonville controlled players found')
    return result


def manual_pool(text):
    if BEGIN in text:
        return text.split(BEGIN,1)[0].rstrip()+'\n\n'
    if '## Unverified contract candidates (406)' in text:
        return text.split('## Unverified contract candidates (406)',1)[0].rstrip()+'\n\n'
    raise ValueError('Free-agent manual section boundary missing; refusing overwrite')


def verified_targets(text):
    targets=[]; category=None
    for line in manual_pool(text).splitlines():
        if line.startswith('### '):
            category=None
        if line.startswith('### Pending '):
            category=next((x for x in ('UFA','RFA','ERFA') if f'({x})' in line),None)
        if category and line.startswith('| ') and not line.startswith('| Player |'):
            cells=[x.strip() for x in line.strip('|').split('|')]
            if len(cells)==4:
                targets.append(dict(name=cells[0], club=next(k for k,v in TEAMS.items() if v==cells[1]),position=cells[2],category=category,source=cells[3]))
    return targets


def capture(source, root, checked_on):
    """Preserve compact, date-filtered evidence so regeneration needs no network."""
    date.fromisoformat(checked_on)
    state=(root/'state/05_Current_Season_State.md').read_text()
    if not re.search(r'\| Master date/time \| February 2, 2014,', state):
        raise ValueError('Recapture requires the February 2, 2014 branch checkpoint')
    rows={name:read_csv(source/name) for name in URLS}
    roster_keys='gsis_id full_name position birth_date team status years_exp week game_type'
    rosters=[]; quarantine=[]
    for name in ('roster_weekly_2013.csv','roster_2013.csv'):
        groups=defaultdict(list)
        for r in rows[name]:
            if number(r['season'])!=2013 or not (1 <= (number(r['week']) or 0) <= 21):
                continue
            if not clean(r['gsis_id']):
                quarantine.append({'source':name,'name':r['full_name'],'reason':'missing_gsis_id','week':number(r['week'])})
                continue
            groups[(r['gsis_id'],code(r['team']))].append(r)
        for (pid,team),observations in sorted(groups.items()):
            last=max(number(x['week']) for x in observations)
            # Keep conflicts at the latest observation rather than selecting file order.
            distinct={json.dumps(project(x,roster_keys),sort_keys=True) for x in observations if number(x['week'])==last}
            for value in sorted(distinct):
                r=json.loads(value);r['team']=team;r['week']=last;r['source']=name
                r['first_week']=min(number(x['week']) for x in observations)
                rosters.append(r)
    depths={}
    for r in rows['depth_charts_2013.csv']:
        if number(r['season'])==2013 and 1 <= (number(r['week']) or 0) <= 21 and clean(r['gsis_id']):
            key=(r['gsis_id'],code(r['club_code']),number(r['week']))
            depths[key]=dict(gsis_id=r['gsis_id'],team=code(r['club_code']),week=number(r['week']))
    drafts=[project(r,'season round pick team gsis_id pfr_player_id pfr_player_name position college') for r in rows['draft_picks.csv'] if (number(r['season']) or 9999)<=2013]
    quarantine += [{'source':'draft_picks.csv','name':r['pfr_player_name'],'reason':'missing_gsis_id','pick':r['pick']}
                   for r in drafts if r['season']=='2013' and not r['gsis_id']]
    if {r['team'] for r in rosters}!={'JAX',*CLUBS}:
        raise ValueError('2013 roster inputs do not cover all 32 clubs')
    contracts=[]
    rejected=Counter()
    for r in rows['historical_contracts.csv.gz']:
        ys=number(r['year_signed']);yrs=number(r['years'])
        if ys is None or not 1900<=ys<=2013:
            rejected['missing_invalid_or_post_2013_year']+=1;continue
        if yrs is None or not 1<=yrs<=20:
            rejected['invalid_length']+=1;continue
        # Exclude current active flags, money, statuses and nested future histories.
        contracts.append(project(r,'player position team otc_id year_signed years player_page'))
    bios=json.loads((root/'library/data/player_birth_dates.json').read_text())['players']
    wanted={r['gsis_id'] for r in rosters}|{r['gsis_id'] for r in drafts if r['season']=='2013' and r['gsis_id']}|{r['gsis_id'] for r in bios.values()}|set(UNPLACED_IDS.values())
    # Include contract-only prospects for a 2013 roster; membership still unknown.
    otc_ids={r['otc_id'] for r in contracts if int(r['year_signed'])+int(r['years'])-1>=2013}
    profiles=[project(r,'gsis_id display_name birth_date position college_name otc_id pfr_id draft_year draft_round draft_pick draft_team') for r in rows['players.csv'] if r['gsis_id'] in wanted or clean(r['otc_id']) in otc_ids]
    profile_ids={r['gsis_id'] for r in profiles}
    contract_ids={r['otc_id'] for r in profiles if r['otc_id']}
    contracts=[r for r in contracts if r['otc_id'] in contract_ids]
    # OTC team strings can contain later clubs on an older contract row.
    # Retain only clubs independently observed for that identity in 2013.
    observed_clubs=defaultdict(set)
    for r in rosters:observed_clubs[r['gsis_id']].add(r['team'])
    observed_by_otc=defaultdict(set)
    for p in profiles:observed_by_otc[p['otc_id']].update(observed_clubs[p['gsis_id']])
    for r in contracts:r['team']='/'.join(sorted(contract_clubs(r['team']) & observed_by_otc[r['otc_id']]))
    # Immutable identity fields only; no later draft information.
    for r in profiles:
        if (number(r['draft_year']) or 0)>2013:
            for k in ('draft_year','draft_round','draft_pick','draft_team'):r[k]=None
    branch_moves=draft_moves(source,[r for r in rows['depth_charts_2013.csv'] if r['season']=='2013' and r['week']=='1'],controlled(root))
    placements={pid:{'club':dest,'basis':basis} for pid,_,dest,basis in branch_moves if pid}
    lib=json.loads((root/'library/data/2013_week1_depth_charts.json').read_text())
    for club in lib['clubs'].values():
        for change in club['branch_changes']:
            if change.startswith('Added '):
                name=change[6:].split(' (',1)[0]
                matches=[p for p in club['players'] if p['player_id']==name]
                if len(matches)!=1:raise ValueError('Unresolved branch addition: '+name)
                identity=matches[0].get('gsis_id') or bios[name]['gsis_id']
                placements[identity]={'club':club['code'],'basis':change}
    source_meta={name:{'url':url,'sha256':sha((source/name).read_bytes()),'raw_rows':len(rows[name])} for name,url in URLS.items()}
    control={bios[name]['gsis_id']:{**r,'name':name} for name,r in controlled(root).items()}
    library_players={p.get('gsis_id') or bios[p['player_id']]['gsis_id']:
                     {'player_id':p['player_id'],'position':p['position'],'club':c['code'],'slots':p.get('slots')}
                     for c in lib['clubs'].values() for p in c['players']}
    branch_paths=['career/2013/roster.md','career/2013/offseason/draft/draftees.md','career/2013/offseason/initial_roster.md',
                  'library/data/2013_week1_depth_charts.json','library/data/player_birth_dates.json']
    branch={'control':control,'library_players':library_players,
            'reviewed_bios':{r['gsis_id']:{'birth_date':r['birth_date'],'evidence':r['evidence']} for r in bios.values()},
            'unplaced_ids':UNPLACED_IDS,'source_hashes':{p:sha((root/p).read_bytes()) for p in branch_paths}}
    return dict(schema_version=1,as_of=AS_OF,season=2013,checked_on=checked_on,sources=source_meta,
                rosters=rosters,depth_membership=[depths[k] for k in sorted(depths)],players=profiles,
                contracts=contracts,draft_picks=[r for r in drafts if r['gsis_id'] in profile_ids or r['season']=='2013'],
                branch=branch,branch_placements=placements,quarantine=quarantine,excluded_contract_rows=dict(rejected))


def contract_for(player, club, contracts):
    if not player.get('otc_id'):
        return {'evidence':'missing_otc_id','start':None,'end':None}
    candidates=[r for r in contracts if r['otc_id']==player['otc_id']]
    if not candidates:
        return {'evidence':'no_pre_2014_contract','start':None,'end':None}
    if club not in TEAMS:
        return {'evidence':'club_unresolved','start':None,'end':None}
    same=[r for r in candidates if club in contract_clubs(r['team'])]
    if not same:
        return {'evidence':'no_matching_club_contract','start':None,'end':None}
    latest=max(int(r['year_signed']) for r in same)
    picks=[r for r in same if int(r['year_signed'])==latest]
    terms={(int(r['year_signed']),int(r['years'])) for r in picks}
    if len(terms)!=1:
        return {'evidence':'ambiguous_same_year_terms','start':None,'end':None,'candidates':picks}
    start,years=next(iter(terms));end=start+years-1
    return {'evidence':'stale_contract' if end<2013 else 'estimated_not_verified','start':start,'end':end,
            'years':years,'join':'otc_id_and_club','source':picks[0]['player_page']}


def estimated_category(experience):
    if experience is None or experience<0:return None
    seasons=experience+1
    return 'UFA' if seasons>=4 else ('RFA' if seasons==3 else 'ERFA')


def corrections(root):
    """Small reviewed factual patches, never canonical branch transactions."""
    data=json.loads((root/REL/'league_corrections.json').read_text())
    if data.get('schema_version')!=1 or data.get('as_of')!=AS_OF:
        raise ValueError('Correction schema or date mismatch')
    for pid,patch in data['players'].items():
        if set(patch)-{'source_club','birth_date','position','contract_start','contract_end','sources','note'}:
            raise ValueError('Unsupported correction field: '+pid)
        if not patch.get('note') or not patch.get('sources'):
            raise ValueError('Correction needs explanation and dated sources: '+pid)
        for source in patch['sources']:
            if not all(source.get(k) for k in ('publisher','title','url','published')):
                raise ValueError('Incomplete correction source: '+pid)
            if not source['url'].startswith('https://') or date.fromisoformat(source['published'])>date.fromisoformat(AS_OF):
                raise ValueError('Correction source is outside the historical gate: '+pid)
        if 'source_club' in patch and patch['source_club'] not in TEAMS:
            raise ValueError('Unknown correction club: '+pid)
        if 'birth_date' in patch:
            if not date(1900,1,1)<=date.fromisoformat(patch['birth_date'])<date.fromisoformat(AS_OF):
                raise ValueError('Invalid corrected birth date: '+pid)
        if 'position' in patch and (not isinstance(patch['position'],str) or not patch['position'].isalpha() or len(patch['position'])>4):
            raise ValueError('Invalid corrected position: '+pid)
        if 'contract_start' in patch or 'contract_end' in patch:
            start=number(patch.get('contract_start'));end=number(patch.get('contract_end'))
            if start is None or end is None or not 1900<=start<=2013 or not start<=end<=2030:
                raise ValueError('Correction needs valid start and end years: '+pid)
    return data['players']


def build(snapshot, root):
    if snapshot['as_of']!=AS_OF or snapshot['season']!=2013:
        raise ValueError('This builder is only for the February 2, 2014 research baseline')
    if any(int(r['year_signed'])>2013 or int(r['year_signed'])<1900 or not 1<=int(r['years'])<=20 for r in snapshot['contracts']):
        raise ValueError('Invalid or future contract in snapshot')
    if any(int(r['season'])>2013 for r in snapshot['draft_picks']):
        raise ValueError('Future draft information in snapshot')
    if any(not 1<=r['week']<=21 for r in snapshot['rosters']):
        raise ValueError('Roster observation outside 2013 season')
    by_id={}; obs=defaultdict(list); depth=defaultdict(list); drafts=defaultdict(list)
    for p in snapshot['players']:
        if p['gsis_id'] in by_id:raise ValueError('Duplicate player ID: '+p['gsis_id'])
        by_id[p['gsis_id']]=p
    for r in snapshot['rosters']:obs[r['gsis_id']].append(r)
    for r in snapshot['depth_membership']:depth[r['gsis_id']].append(r)
    for r in snapshot['draft_picks']:
        if r['gsis_id']:drafts[r['gsis_id']].append(r)
    bios_by_id=snapshot['branch']['reviewed_bios']
    control=snapshot['branch']['control']
    library_players=snapshot['branch']['library_players']
    patches=corrections(root)
    if set(patches)&set(control):
        raise ValueError('Jacksonville-controlled corrections belong in the branch registers')
    names=defaultdict(set)
    for p in snapshot['players']:names[norm(p['display_name'])].add(p['gsis_id'])
    for r in snapshot['rosters']:names[norm(r['full_name'])].add(r['gsis_id'])
    targets={}
    for target in verified_targets((root/REL/'free_agent_pool.md').read_text()):
        matches=names[norm(target['name'])]
        if len(matches)!=1:raise ValueError('Target identity not unique: '+target['name'])
        targets[next(iter(matches))]=target
    unplaced=set(snapshot['branch']['unplaced_ids'].values())
    ids=set(obs)|set(control)|set(library_players)|set(targets)|set(by_id)
    if set(patches)-ids:
        raise ValueError('Correction ID absent from snapshot; research and recapture identity first')
    results=[]
    for pid in sorted(ids):
        profile=by_id.get(pid,{})
        history=obs[pid];issues=[]
        latest=max((r['week'] for r in history),default=None)
        last=[r for r in history if r['week']==latest]
        clubs=sorted({r['team'] for r in last})
        historical_club=clubs[0] if len(clubs)==1 else None
        statuses=sorted({r['status'] for r in last if r['status']})
        name=(control.get(pid) or {}).get('name') or next((r['full_name'] for r in last if r['full_name']),None) or profile.get('display_name') or library_players.get(pid,{}).get('player_id')
        if not name:raise ValueError('No name for '+pid)
        position=control.get(pid,{}).get('position') or next((r['position'] for r in last if r['position']),None) or library_players.get(pid,{}).get('position') or profile.get('position')
        patch=patches.get(pid,{})
        if 'source_club' in patch:
            historical_club=patch['source_club'];clubs=[historical_club]
        position=patch.get('position',position)
        if not profile:issues.append('missing_player_register')
        if len(clubs)>1:issues.append('ambiguous_latest_club')
        if not history:issues.append('no_2013_roster_observation')
        elif latest<17:issues.append('last_observed_before_week17')
        if len(statuses)!=1:issues.append('missing_or_conflicting_source_status')
        if set(statuses)&{'CUT','TRD','TRC','TRT','RSR','NWT'}:issues.append('release_status_needs_dated_source')
        dobs={r['birth_date'] for r in history if r['birth_date']}
        if profile.get('birth_date'):dobs.add(profile['birth_date'])
        bio=bios_by_id.get(pid)
        dob=bio['birth_date'] if bio else (next(iter(dobs)) if len(dobs)==1 else None)
        dob_evidence=bio['evidence'] if bio else ('single_provider' if len(dobs)==1 else 'unresolved')
        if 'birth_date' in patch:
            dob=patch['birth_date'];dob_evidence='sourced_correction'
        if len(dobs)>1 and not bio and 'birth_date' not in patch:issues.append('birth_date_conflict')
        if not dob:issues.append('birth_date_missing')
        inventory_club=historical_club;assignment='historical_observation_only';branch_status=None
        if pid in control:
            inventory_club='JAX';assignment='jacksonville_control';branch_status=control[pid]['status']
        elif pid in unplaced:
            inventory_club=None;assignment='unplaced_branch_claim';issues.append('branch_claimant_unknown')
        elif pid in snapshot['branch_placements']:
            inventory_club=snapshot['branch_placements'][pid]['club'];assignment='existing_branch_placement'
        elif historical_club=='JAX':
            inventory_club=None;assignment='real_jaguars_only';issues.append('real_jaguars_move_not_applied')
        elif not inventory_club:
            issues.append('placement_unknown')
        if pid in control:
            contract={'evidence':'branch_register_controls','start':None,'end':None}
        else:
            contract=contract_for(profile,historical_club,snapshot['contracts'])
        if 'contract_end' in patch:
            contract={'evidence':'sourced_correction','start':patch['contract_start'],'end':patch['contract_end'],
                      'source':'league_corrections.json','raw_estimate':contract}
        if assignment=='existing_branch_placement':issues.append('branch_contract_review')
        experiences={number(r['years_exp']) for r in last if number(r['years_exp']) is not None}
        exp=next(iter(experiences)) if len(experiences)==1 else None
        category=None;evidence='unknown';candidate=False;fa_source=None
        if pid in control:evidence='branch_register_controls'
        elif pid in targets:
            t=targets[pid];category=t['category'];evidence='verified_two_pass';candidate=True;fa_source=t['source']
        elif contract['evidence'] in {'estimated_not_verified','sourced_correction'} and contract['end']==2013 and assignment=='historical_observation_only':
            category=estimated_category(exp);candidate=True;evidence='experience_estimate' if category else 'experience_unknown'
        if contract['evidence'] not in {'estimated_not_verified','sourced_correction','branch_register_controls'}:issues.append(contract['evidence'])
        # A roster status describes source evidence, not a branch injury or a transaction date.
        historic_drafts=sorted(drafts[pid],key=lambda r:int(r['season']))
        draft=historic_drafts[-1] if historic_drafts else None
        if draft is None and profile.get('draft_year') and int(profile['draft_year'])<=2013:
            draft={k:profile.get(v) for k,v in {'season':'draft_year','round':'draft_round','pick':'draft_pick','team':'draft_team'}.items()}
        results.append(dict(player_id=pid,name=name,position=position,birth_date=dob,birth_date_evidence=dob_evidence,
            college=profile.get('college_name'),otc_id=profile.get('otc_id'),draft=draft,
            source_club=historical_club,source_club_candidates=clubs,source_status=statuses,
            first_observed_week=min((r['first_week'] for r in history),default=None),last_observed_week=latest,
            depth_cross_check=bool(historical_club and any(r['team']==historical_club and r['week']==latest for r in depth[pid])),
            inventory_club=inventory_club,assignment=assignment,branch_status=branch_status,
            branch_week1_slot=library_players.get(pid,{}).get('slots'),
            years_exp_source=exp,accrued_seasons_verified=None,contract=contract,
            free_agency={'category':category,'evidence':evidence,'candidate':candidate,'source':fa_source},
            issues=sorted(set(issues)),correction=patch or None,provenance=sorted({r['source'] for r in history}|({'players.csv'} if profile else set()))))
    summary={'players':len(results),'jacksonville_controlled':len(control),'verified_targets':len(targets),
             'contract_evidence':dict(sorted(Counter(p['contract']['evidence'] for p in results).items())),
             'free_agent_evidence':dict(sorted(Counter(p['free_agency']['evidence'] for p in results).items())),
             'candidate_categories':dict(sorted(Counter(p['free_agency']['category'] or 'UNKNOWN' for p in results if p['free_agency']['candidate']).items())),
             'estimated_categories':dict(sorted(Counter(p['free_agency']['category'] or 'UNKNOWN' for p in results if p['free_agency']['evidence']=='experience_estimate').items())),
             'last_observed_week17_or_later':sum((p['last_observed_week'] or 0)>=17 for p in results),
             'no_weekly_roster_evidence':sum(p['last_observed_week'] is None for p in results),
             'unplaced':sum(p['inventory_club'] is None for p in results),
             'issues':dict(sorted(Counter(issue for p in results for issue in p['issues']).items()))}
    return dict(schema_version=1,as_of=AS_OF,scope='Research inventory, not canonical roster or legal eligibility',summary=summary,players=results)


def csv_text(rows,fields):
    f=io.StringIO(newline='');w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows);return f.getvalue()


def flat(p):
    return dict(player_id=p['player_id'],name=p['name'],position=p['position'],birth_date=p['birth_date'],
        birth_date_evidence=p['birth_date_evidence'],college=p['college'],source_club=p['source_club'],
        source_status=';'.join(p['source_status']),last_observed_week=p['last_observed_week'],inventory_club=p['inventory_club'],
        assignment=p['assignment'],branch_status=p['branch_status'],contract_start_estimate=p['contract']['start'],contract_end_estimate=p['contract']['end'],
        contract_evidence=p['contract']['evidence'],years_exp_source=p['years_exp_source'],pending_fa_category=p['free_agency']['category'],
        fa_evidence=p['free_agency']['evidence'],issues=';'.join(p['issues']))


def cell(value):
    return str(value if value is not None else 'Unknown').replace('|','/').replace('\n',' ')


def contract_label(p):
    c=p['contract']
    if c['evidence']=='sourced_correction':return f"{c['start']}-{c['end']} (sourced correction)"
    return f"{c['start']}-{c['end']} (estimate)" if c['start'] else c['evidence'].replace('_',' ')


def category_label(p):
    fa=p['free_agency']
    if fa['category']:return fa['category']+(' (verified)' if fa['evidence']=='verified_two_pass' else ' (estimate)')
    if p['contract']['evidence']=='sourced_correction' and p['contract']['end']>2013:
        return 'Under contract (sourced)'
    if p['contract']['evidence']=='estimated_not_verified' and p['contract']['end']>2013:
        return 'Under contract (estimate)'
    return 'Unknown'


def render(db,snapshot,root):
    players=db['players'];outputs={REL/'league_players.json':database_text(db)}
    rows=[flat(p) for p in players]
    outputs[REL/'league_players.csv']=csv_text(rows,list(rows[0]))
    exceptions=[dict(player_id=p['player_id'],name=p['name'],issues=';'.join(p['issues'])) for p in players if p['issues']]
    outputs[REL/'league_exceptions.csv']=csv_text(exceptions,['player_id','name','issues'])
    for club in sorted(CLUBS):
        path=REL/'clubs'/f'{club}.md';previous=(root/path).read_text()
        prefix=''
        if BEGIN in previous:
            if END not in previous:raise ValueError('Incomplete generated block: '+str(path))
            prefix=previous.split(BEGIN,1)[0]
            tail=previous.split(END,1)[1]
        else:
            marker='## Changes on the rails (fill by real date)'
            if marker not in previous:raise ValueError('Missing manual rails table: '+str(path))
            # Refuse to discard existing hand-entered notes during one-time migration.
            for line in previous.split(marker)[0].splitlines():
                if line.startswith('| ') and not line.startswith('| 2013 slot |'):
                    cols=[x.strip() for x in line.strip('|').split('|')]
                    if len(cols)==6 and cols[-1]:raise ValueError('Migrate hand-entered note before regenerating '+str(path))
            tail='\n\n'+marker+previous.split(marker,1)[1]
        group=sorted((p for p in players if p['inventory_club']==club),key=lambda p:(p['name'],p['player_id']))
        lines=[BEGIN,f'# {CLUBS[club]}: generated end-of-2013 research inventory','',
               '**As of:** February 2, 2014. These are historical observations with existing branch placements applied, not a certified final roster or a live TeamInput. Source status does not impose an injury or suspension on the branch. Week 1 slots are reference labels only; row order is alphabetical, not depth order.',
               '',f'{len(group)} players. See [database coverage and rebuild instructions](../league_database_report.md). Contract years and experience-derived categories require verification before pursuit. Manual dated moves below are preserved by rebuilds.','',
               '| Player | GSIS ID | Pos | 2013 branch Week 1 slot | Last observed week | Source status | Contract | Pending FA | Review flags |',
               '|---|---|---|---|---|---|---|---|---|']
        for p in group:
            lines.append('| '+' | '.join(cell(x) for x in [p['name'],p['player_id'],p['position'],p['branch_week1_slot'],p['last_observed_week'],','.join(p['source_status']) or None,contract_label(p),category_label(p),'; '.join(p['issues']) or 'Source data only'])+' |')
        outputs[path]=prefix+'\n'.join(lines)+'\n'+END+tail
    pool_path=REL/'free_agent_pool.md';old_pool=(root/pool_path).read_text();prefix=manual_pool(old_pool)
    pool_tail=old_pool.split(END,1)[1] if END in old_pool else '\n'
    lines=[BEGIN,'## Generated pending-free-agent candidates','',
           'Rebuilt from the league database. Verified targets above remain authoritative. Every other category is an experience-based estimate, not verified accrued service or signing permission. Only an estimated contract ending in 2013 produces an expiry candidate. Old contracts ending before 2013 do not. Jacksonville-controlled players use their own register. Unknown contracts and uncertain placement remain in `league_exceptions.csv`; omission here does not mean a player is unavailable.','']
    for cat in ('UFA','RFA','ERFA',None):
        group=sorted((p for p in players if p['free_agency']['candidate'] and p['free_agency']['evidence']!='verified_two_pass' and p['free_agency']['category']==cat),key=lambda p:(p['name'],p['player_id']))
        lines += [f"### Estimated {cat or 'unknown category'} ({len(group)})",'', '| Player | GSIS ID | Observed 2013 club | Pos | Contract estimate | Review flags |','|---|---|---|---|---|---|']
        for p in group:lines.append('| '+' | '.join(cell(x) for x in [p['name'],p['player_id'],p['source_club'],p['position'],contract_label(p),'; '.join(p['issues']) or 'Verify expiry and accrued service'])+' |')
        lines.append('')
    lines += ['The superseded 406-row raw list is replaced by these ID-linked candidates and the complete research inventory. Released-status observations are not exact dated releases; they remain research leads, not confirmed unsigned players.',END]
    outputs[pool_path]=prefix+'\n'.join(lines)+pool_tail
    summary=db['summary']
    report=['# League database: coverage, provenance and operation','',f'**Research baseline:** {AS_OF}. **Source capture checked:** {snapshot["checked_on"]}. Generated deterministically from the committed, field-limited `source_snapshot.json.gz`. No runtime or calendar mutation.','',
        '## Coverage','',f'- {summary["players"]} distinct GSIS identities; {summary["jacksonville_controlled"]} Jacksonville-controlled players, including reserve/retired and practice squad.',
        f'- {summary["last_observed_week17_or_later"]} identities observed in Week 17 or the playoffs; {summary["no_weekly_roster_evidence"]} additional identities have no 2013 roster observation.',
        f'- {summary["unplaced"]} identities have no resolved inventory club. All remain in the database.',
        f'- {len(snapshot["quarantine"])} missing-ID source rows quarantined: '+', '.join(sorted({r['name'] for r in snapshot['quarantine']}))+'.',
        '- Sources do not establish a complete final 53 plus eight practice-squad players and every reserve list for each club. Seasonal rosters add no new IDs to the weekly feed in this capture. Annual/weekly/depth agreement is a same-provider consistency check, not independent verification.',
        '- Players seen earlier in 2013, draft-only identities, existing branch identities and players with contract estimates spanning 2013 are retained. Absence after an earlier week does not prove release, retirement or unsigned status. Players absent from all these sources may still be missing.',
        '- The register is used only for identity, birth date, college, OTC/PFR IDs and pre-2014 draft fields. Current status, current team, career totals and later outcomes are excluded. The draft file is projected to selection/identity fields before storage, with all 2014+ selections excluded.',
        '- Existing reviewed DOB evidence takes precedence. New birthdays are single-provider data unless independently verified. A conflict becomes an exception rather than a guessed date.','',
        '## Free agency and contract limits','',
        'Nine targeted statuses retain the two-pass evidence in `free_agent_pool.md`. Elsewhere `years_exp + 1` is only an experience proxy for the completed 2013 season. It is not a verified accrued-season count. Four or more maps to estimated UFA, three to estimated RFA, fewer to estimated ERFA, and missing experience stays unknown.',
        '', 'An accrued season depends on qualifying regular-season service. Practice-squad time, credited experience, holdouts and reserve designations prevent treating the proxy as legal eligibility. Check the actual accrued service, expiration and any tag or tender for each pursued player. Rule cross-check: Tennessee Titans, [2014 NFL Free Agency Questions & Answers](https://www.tennesseetitans.com/news/2014-nfl-free-agency-questions-answers-salary-cap-set-at-133-million-12709412), March 8, 2014. Only the established free-agency definitions are used, not later player actions.',
        '', 'Contracts join by OTC ID from the GSIS-linked player register and matching historical club. Full-name and slash-separated club codes are normalized. Retrospective OTC club strings are limited to clubs observed for the player in 2013; later destinations are stripped. There is no name-only or wrong-club fallback. Invalid zero years, post-2013 signings and nonpositive lengths are excluded. Conflicting latest-year terms remain unresolved. Start + length - 1 is explicitly an estimate: extensions may list only added years, and release/option/restructure history is incomplete. Contract-only entries do not prove club membership. No contract dollars or future terms are imported.',
        '', '| Contract evidence | Players |','|---|---|']
    report += [f'| {k} | {v} |' for k,v in summary['contract_evidence'].items()]
    report += ['', 'Two spot checks exposed false expiry candidates: Ben Roethlisberger and Rob Gronkowski. Dated club reports and independent corroboration are recorded in `league_corrections.json`; they remain under contract rather than being classified as 2014 free agents. These corrections do not certify the remaining contract estimates.', '', '## Branch protection and date gates','',
        'Jacksonville control comes from the current branch roster, including Reserve/Retired and practice squad, using reviewed GSIS identities. Existing 2013 trades and draft swaps are preserved. A real Jaguars player with no branch placement stays unplaced; he is never silently added to Jacksonville or another club. Existing unnamed waiver claimants remain unresolved. Real source statuses never set branch injuries, suspensions or availability.',
        '', 'The builder accepts only this February 2 baseline. It cannot advance the clock, resolve an offer or draw, apply a retirement, or construct 2014 Week 1 TeamInputs. Future dated moves still belong in the club rails tables; draft pairing remains at the draft. The later Week 1 build must reconcile branch control and swaps afresh. The four VERIFY retirement rows are untouched.',
        '', '## Rebuild and review','',
        '- Run `python scripts/research/build_league_player_database.py` for a fully offline rebuild from the committed snapshot.',
        '- Run `python scripts/research/build_league_player_database.py --check` to verify generated JSON, CSV, exceptions, club blocks, report and pool sections without writing.',
        '- To recapture sources, download the six files below into a scratch directory and run `python scripts/research/build_league_player_database.py --source-dir SOURCE_DIR --capture --checked-on YYYY-MM-DD`. Review source hashes, coverage and the diff before committing. Never use later-season files under these names.',
        '- Resolve a dated club, position, birth-date or contract-year correction in `league_corrections.json`, keyed by GSIS ID, with `note` and a `sources` list. Each source requires publisher, title, HTTPS URL and an ISO published date no later than February 2. These corrections cannot change Jacksonville control or existing branch placements. Use paired contract_start and contract_end fields for sourced term corrections. Free-agent-category confirmations belong in the sourced target section.',
        '- Edit the verified section and source receipt in `free_agent_pool.md`, not generated candidate rows. Rebuilds preserve that section. Club text outside the generated markers, including dated moves, is also preserved. Reviewed club/position/DOB/contract-year corrections belong in `league_corrections.json` before rebuilding; do not hand-edit generated outputs.',
        '- `league_exceptions.csv` is the full row-level review queue. Missing or ambiguous contracts need attention when a player is pursued, not a manual cleanup of the whole league. The existing retired-player research remains in `retirements.md`.',
        '', '## Input hashes','', '| Input | Raw rows | SHA-256 |','|---|---|---|']
    report += [f'| [{name}]({r["url"]}) | {r["raw_rows"]} | `{r["sha256"]}` |' for name,r in sorted(snapshot['sources'].items())]
    report += ['', 'Status-code reference: [nflreadr roster status dictionary](https://nflreadr.nflverse.com/articles/dictionary_roster_status.html). The source status codes are retained verbatim, not interpreted as dated transactions.','']
    outputs[REL/'league_database_report.md']='\n'.join(report)
    return outputs


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-dir',type=Path);p.add_argument('--capture',action='store_true');p.add_argument('--checked-on')
    p.add_argument('--check',action='store_true');p.add_argument('--root',type=Path,default=ROOT)
    args=p.parse_args();root=args.root.resolve();snapshot_path=root/REL/'source_snapshot.json.gz'
    if args.capture:
        if args.check or not args.source_dir or not args.checked_on:p.error('capture needs --source-dir and --checked-on; cannot combine with --check')
        snapshot=capture(args.source_dir,root,args.checked_on)
    else:
        if args.source_dir or args.checked_on:p.error('source-dir and checked-on require --capture')
        snapshot=json.loads(gzip.decompress(snapshot_path.read_bytes()))
    db=build(snapshot,root);outputs=render(db,snapshot,root)
    if args.capture:outputs[REL/'source_snapshot.json.gz']=gzip.compress(json.dumps(snapshot,sort_keys=True,separators=(',',':')).encode(),mtime=0)
    differences=[]
    for path,content in outputs.items():
        target=root/path
        data=content.encode() if isinstance(content,str) else content
        if args.check:
            if not target.exists() or target.read_bytes()!=data:differences.append(str(path))
        else:target.write_bytes(data)
    if differences:
        print('Generated files differ: '+'; '.join(differences),file=sys.stderr);return 1
    print(('CHECK PASS: ' if args.check else 'BUILT: ')+json.dumps(db['summary'],sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
