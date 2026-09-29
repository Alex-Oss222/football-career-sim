#!/usr/bin/env python3
"""Render the Jaguars' fixed 2014-2023 financial horizon from sourced and adopted simulation contract schedules."""
import argparse
from collections import Counter
from datetime import date
from decimal import Decimal
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
INPUT = Path('career/finances/jaguars_cap_inputs.json')
OUTPUT = Path('career/finances/jaguars_cap_2014_2023.md')
DETAILS = Path('career/finances/jaguars_contract_details.md')
POSITIONS = ['QB','RB','FB','WR','TE','OT','OG','C','EDGE','IDL','LB','CB','S','K','P','LS']
STATUSES = {'known','unknown_amount','approximate','term_unknown','not_committed','not_signed','tender','option_unexercised'}
CBA = 'https://nflps.org/wp-content/uploads/2012/05/collective-bargaining-agreement-2011-2020.pdf'

def dollars(v):
    return '' if v is None else (f'-${abs(v):,.0f}' if v<0 else f'${v:,.0f}')

def display_date(value):
    return date.fromisoformat(value).strftime('%B %d, %Y').replace(' 0', ' ')

def slug(name):
    return re.sub(r'[^\w -]', '', name.lower()).replace(' ', '-')

def draft_slot(value):
    rounds=re.findall(r'C([3-6])',value)
    if not rounds:return value
    label='round '+rounds[0] if len(rounds)==1 else 'rounds '+rounds[0]+' to '+rounds[-1]
    return value.split(' + ')[0]+' + compensatory picks from '+label

def table(headers, rows):
    def cell(v): return str(v).replace('|', '/').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(map(cell,headers))+' |', '|'+ '|'.join(['---']*len(headers))+'|'] + ['| '+' | '.join(map(cell,row))+' |' for row in rows])+'\n\n'

def md_rows(text):
    return [[c.strip() for c in l.strip('|').split('|')] for l in text.splitlines() if l.startswith('|')]

def exact_amount(text):
    m=re.fullmatch(r'\$(\d[\d,.]*)(M)?(?: from March 11)?', text)
    return int(Decimal(m[1].replace(',',''))*(1000000 if m[2] else 1)) if m else None

def validate(data, root=ROOT):
    years=list(map(str,range(data['start_year'],data['end_year']+1)))
    if len(years)!=10: raise ValueError('The tracker must cover exactly ten explicit league years')
    players=data['players'];names=[p['name'] for p in players]
    if set(data['team_years'])!=set(years): raise ValueError('Missing team accounting year')
    for y,book in data['team_years'].items():
        for key in ['carryover','net_adjustments','counted_team_salary','actual_cash_paid','operating_reserve','rookie_incremental_reserve','cash_budget']:
            value=book[key]
            if value is not None and (type(value) is not int or (key!='net_adjustments' and value<0)):
                raise ValueError('Invalid team accounting amount')
        if any(book[k] is not None for k in ['carryover','net_adjustments','counted_team_salary','actual_cash_paid','operating_reserve','rookie_incremental_reserve','cash_budget']) and not book['sources']:
            raise ValueError('Team accounting requires sources')
        if book['accounting_reconciled']:
            if any(book[k] is None for k in ['carryover','net_adjustments','counted_team_salary']) or y not in data['league_caps']:
                raise ValueError('Reconciled accounting requires complete inputs')
            if any(p['years'][y]['status'] in {'unknown_amount','term_unknown','approximate'} for p in players):
                raise ValueError('Cannot certify room with unresolved player obligations')
    if len(names)!=len(set(names)): raise ValueError('Duplicate player would double-count obligations')
    for p in players:
        if p.get('former_player'):
            if not p.get('departure_source') or not (root/p['departure_source']).is_file():
                raise ValueError('Former player requires a departure source')
            if date.fromisoformat(p['departure_date']) > date.fromisoformat(data['as_of']):
                raise ValueError('A future departure cannot archive a current player')
        if p['position'] not in POSITIONS: raise ValueError('Unknown position: '+p['name'])
        if set(p['years'])!=set(years): raise ValueError('Missing annual status: '+p['name'])
        if not p['sources'] or any(not (root/s).is_file() for s in p['sources']): raise ValueError('Missing source: '+p['name'])
        for year,row in p['years'].items():
            if row['status'] not in STATUSES: raise ValueError('Unknown annual status')
            for k in ['cap','base','proration','cash','other_cap','approximate_cap','planning_allowance','deferred_bonus_cash','guaranteed_base']:
                v=row.get(k)
                if v is not None and (type(v) is not int or v<0): raise ValueError('Invalid dollar value: '+p['name'])
            if row['status'] in {'known','tender'} and row['cap'] is None: raise ValueError('Known charge requires amount')
            if row['status'] not in {'known','tender'} and row['cap'] is not None: raise ValueError('Unknown or conditional charge must not be numeric')
            if row['status']=='approximate':
                if row.get('approximate_cap') is None or not row.get('estimate_note'):
                    raise ValueError('Estimate requires an amount and its basis: '+p['name'])
                if all(row.get(k) is not None for k in ['base','proration']):
                    if row['approximate_cap'] != row['base']+row['proration']+row.get('other_cap',0):
                        raise ValueError('Estimated cap components disagree: '+p['name'])
            if row.get('planning_allowance') is not None and (row['status']!='term_unknown' or not row.get('estimate_note')):
                raise ValueError('Conditional allowance requires unresolved term and basis')
            if row['status']=='known' and all(row.get(k) is not None for k in ['base','proration']):
                if row['cap'] != row['base']+row['proration']+row.get('other_cap',0): raise ValueError('Cap components disagree: '+p['name'])
            if row['status'] in {'known','approximate'} and p['contract_ends'] is not None and int(year)>p['contract_ends']: raise ValueError('Charge exceeds recorded term: '+p['name'])
    for p in players:
        if p['control'] in {'signed','future'}:
            if p['contract_ends'] is None: raise ValueError('Signed contract requires an end year')
            for year,row in p['years'].items():
                if int(year)<=p['contract_ends'] and working_charge(row) is None:
                    raise ValueError('Missing covered-year charge: '+p['name'])
                if working_charge(row) is not None and any(row.get(k) is None for k in ['base','proration','cash']):
                    raise ValueError('Missing annual contract component: '+p['name'])
            if p['remaining_guarantees'] != sum(r.get('guaranteed_base',0) for r in p['years'].values()):
                raise ValueError('Remaining guarantees disagree: '+p['name'])
    roster=md_rows((root/data['current_roster']).read_text())
    expected={x[0] for x in roster if len(x) in (6,7) and re.fullmatch(r'\d{4}-\d{2}-\d{2}',x[2])}
    current_names={p['name'] for p in players if not p.get('former_player')}
    if current_names!=expected: raise ValueError('Tracker coverage differs from current active, retired and future roster')
    source=(root/data['current_contract_table']).read_text()
    asof=display_date(data['as_of'])
    if f'**As of:** {asof}' not in source: raise ValueError('Contract table checkpoint changed; reconcile the tracker')
    contracts={x[0]:x for x in md_rows(source) if x[0] in expected and len(x) in (9,15)}
    if set(contracts)!=expected: raise ValueError('Contract table coverage differs from tracker')
    current=str(data['start_year'])
    for p in players:
        if p.get('former_player'): continue
        row=contracts[p['name']]; y=p['years'][current]
        if len(row)==15:
            amount=exact_amount(row[10])
            if amount is not None and (y['status'] not in {'known','approximate'} or working_charge(y)!=amount): raise ValueError('Current charge differs from contract table: '+p['name'])
            if amount is None and y['status'] in {'known','approximate'}: raise ValueError('Tracker invents an exact current charge: '+p['name'])
            if y['status']=='approximate' and exact_amount(row[10].removeprefix('About '))!=y['approximate_cap']:
                raise ValueError('Current estimate differs from contract table: '+p['name'])
        elif len(row)!=9: raise ValueError('Contract table layout changed; review parser')
        else:
            expected='tender' if 'Franchise player' in row[6] or row[6].startswith('Tendered') else ('unknown' if row[6].startswith('Unresolved:') else 'pending')
            if p['control']!=expected: raise ValueError('Contract status differs from current table: '+p['name'])
            if expected=='tender':
                match=re.search(r'2014 tender: \*\*\$(\d[\d,]*)',row[7])
                if not match or y['status']!='tender' or y['cap']!=int(match[1].replace(',','')): raise ValueError('Tender mismatch')
    return years

def cap_cell(row):
    return dollars(working_charge(row))

def totals(players, years, field='cap', status='known'):
    return [sum(p['years'][y].get(field) or 0 for p in players if p['years'][y]['status']==status) for y in years]


def source_link(path):return '['+Path(path).stem.replace('_',' ')+'](../../'+path+')'

def contract_total(p):
    values=[working_charge(r) for r in p['years'].values()]
    return dollars(sum(v for v in values if v is not None)) if any(v is not None for v in values) else ''

def team_accounting(d, year):
    book=d['team_years'][year]
    cap=d['league_caps'].get(year)
    adjusted=None
    if cap is not None and book['carryover'] is not None and book['net_adjustments'] is not None:
        adjusted=cap+book['carryover']+book['net_adjustments']
    room=adjusted-book['counted_team_salary'] if book['accounting_reconciled'] and adjusted is not None and book['counted_team_salary'] is not None else None
    after_rookies=room-book['rookie_incremental_reserve'] if room is not None and book['rookie_incremental_reserve'] is not None else None
    return {'adjusted':adjusted,'room':room,'after_rookies':after_rookies}

def working_charge(row):
    if row['status'] in {'known','tender'}: return row['cap']
    if row['status']=='approximate': return row['approximate_cap']
    return None

def working_total(players, year, field='cap', statuses=('known','approximate','tender')):
    rows=[p['years'][year] for p in players if p['years'][year]['status'] in statuses]
    if not rows:return None
    return sum((working_charge(r) if field=='cap' else r.get(field)) or 0 for r in rows)

def release_exposure(p, year):
    rows=[r for y,r in p['years'].items() if int(y)>=int(year) and r['status'] in {'known','approximate'}]
    return sum((r['proration'] or 0)+r.get('guaranteed_base',0) for r in rows)

def render_main(d,years):
    ps=d['players'];current=years[0]
    roster=Counter(p['control'] for p in ps if not p.get('former_player'))
    out=[f"# Jacksonville Jaguars cap tracker, {years[0]} to {years[-1]}\n\nAs of {display_date(d['as_of'])}, {d['checkpoint']}. Whole US dollars.\n\n",
    '[Player cap table](#4-cap-by-player-ten-years) | [Individual contract details](jaguars_contract_details.md) | [Expirations](#9-expiring-contracts-and-free-agent-classes) | [Updating this tracker](README.md)\n\n',
    f"The inventory covers {sum(roster.values())} current players: {roster['signed']} under signed contracts (the six reserve/future contracts included from March 11) and {roster['tender']} on unsigned tenders (franchise, RFA or ERFA). {len(ps)-sum(roster.values())} former players are retained for financial history only.\n\n",
    '## 0. Reading the table\n\n',
    '**Each amount is the working cap charge for that contract year. A blank means the recorded deal does not cover that year.** Existing sourced schedules and adopted simulation amounts are both included. The individual notes identify their basis; the [completion research](../../library/2014_jaguars_contract_completion.md) explains the assumptions. These terms persist until a recorded amendment or correction changes them.\n\n',
    'The ten-year horizon stays visible for future tracking. Pending free agents and unexercised options create no new salary commitment. Each unsigned tender is included once. Scheduled cash means money payable if the player remains under the stated terms, not evidence that it has already been paid.\n\n',
    '## 1. League inputs and accounting basis\n\n',
    table(['Input','2014 treatment'],[
        ['League salary cap',dollars(d['league_caps'][current])],
        ['Reserve/future effective date','March 11, 2014'],
        ['Counting rule','Top 51 from the league-year opening, including retained bonus and other required charges'],
        ['2014 minimum salaries','$420,000 / $495,000 / $570,000 / $645,000 / $730,000 / $855,000 / $955,000 for 0 / 1 / 2 / 3 / 4-6 / 7-9 / 10+ credited seasons'],
        ['Future league caps','Add each year’s published cap when that year is reached'],
        ['Club accounting','Carryover, adjustments and actual cash receipts remain in the current cap worksheet']]),
    f"The [2011 agreement]({CBA}) controls the era’s minimums, bonus allocation, Top-51 treatment, options and cash-floor windows. [The original-contract research](../../library/2014_jaguars_original_contract_reconstruction.md) supplies the historical salaries and bonus schedules. The [club worksheet](../2014/offseason/current_cap_worksheet.md) separates scheduled player commitments from adjusted club cap room.\n\n",
    '## 2. Team cap summary, ten years\n\n']
    signed=[working_total(ps,y,statuses=('known','approximate')) for y in years]
    tender=[working_total(ps,y,statuses=('tender',)) for y in years]
    player=[working_total(ps,y) for y in years]
    dead=[sum(x['amount'] for x in d['dead_money'] if str(x['year'])==y) for y in years]
    combined=[(a or 0)+b if a is not None or b else None for a,b in zip(player,dead)]
    rows=[['Signed contracts and futures']+list(map(dollars,signed)),
          ['Unsigned tenders']+list(map(dollars,tender)),
          ['Player contracts including tender']+list(map(dollars,player)),
          ['Separate carry-forward dead money']+[dollars(x) if player[i] is not None or x else '' for i,x in enumerate(dead)],
          ['Recorded cap obligations']+list(map(dollars,combined)),
          ['Scheduled player cash including tender']+[dollars(working_total(ps,y,'cash')) for y in years],
          ['Salary guaranteed in that year']+[dollars(working_total(ps,y,'guaranteed_base')) for y in years],
          ['Players with scheduled charges']+[sum(working_charge(p['years'][y]) is not None for p in ps) or '' for y in years]]
    out.append(table(['Item']+years,rows))
    out.append('These are the working obligations for the recorded deals, before club adjustments and additional roster construction. They are not a forecast of total team spending after these contracts expire.\n\n## 3. Cap by position, ten years\n\n')
    rows=[[pos]+[dollars(working_total([p for p in ps if p['position']==pos],y)) for y in years] for pos in POSITIONS]
    for label,positions in [('Offense',POSITIONS[:8]),('Defense',POSITIONS[8:13]),('Special teams',POSITIONS[13:])]:
        rows.append([label]+[dollars(working_total([p for p in ps if p['position'] in positions],y)) for y in years])
    rows.append(['All player contracts']+list(map(dollars,player)))
    out.append(table(['Position']+years,rows))
    out.append('Unsigned tenders are included in their positions. Each player is counted once. Futures are grouped by position for accounting; this does not assign a depth-chart role.\n\n## 4. Cap by player, ten years\n\n')
    labels={'signed':'Signed','future':'Futures','pending':'Pending free agent','tender':'Unsigned tender','retired':'Retired'}
    for i,pos in enumerate(POSITIONS,1):
        out.append(f'### 4.{i} {pos}\n\n')
        group=sorted([p for p in ps if p['position']==pos],key=lambda p:(-(working_charge(p['years'][current]) or 0),p['name']))
        rows=[]
        for p in group:
            rows.append([f"[{p['name']}](jaguars_contract_details.md#{slug(p['name'])})",p['contract_ends'] or '',labels.get(p['control'],p['control'])]+[cap_cell(p['years'][y]) for y in years]+[contract_total(p)])
        rows.append([pos+' total','','']+[dollars(working_total(group,y)) for y in years]+[dollars(sum(working_total(group,y) or 0 for y in years)) if any(working_total(group,y) is not None for y in years) else ''])
        out.append(table(['Player','Through','Status']+years+['Remaining cap total'],rows))
    out.append('### 4.17 Futures contracts\n\nAll six run through 2015 under the adopted two-year terms. They have no signing bonus or salary guarantee. Their dollars already appear in the position tables above.\n\n')
    out.append(table(['Player','2014 salary / cap','2015 salary / cap','Total'],[[p['name'],cap_cell(p['years']['2014']),cap_cell(p['years']['2015']),contract_total(p)] for p in ps if p['contract_type'].startswith('Reserve/future') and not p.get('former_player')]))
    out.append(f'## 5. Individual contract detail sheets\n\n[Open all {len(ps)} player sheets](jaguars_contract_details.md) for annual salary, bonus, cap, cash, guarantees, release exposure and sources.\n\n## 6. Dead money and void years\n\n')
    out.append(table(['Player','Year','Charge','Basis'],[[x['player'],x['year'],dollars(x['amount']),x['basis']] for x in d['dead_money']]))
    out.append('The $51,675 old Bray bonus is counted separately from his new $420,000 salary. No recorded deal has void years. The completion research explains the inherited bonus reconciliation.\n\n## 7. Draft class and rookie pool\n\n')
    out.append(table(['Draft','Round','Original club','Slot in round','Overall'],[[x['year'],x['round'],x['original_club'],x['slot_in_round'],draft_slot(x['overall'])] for x in d['draft_picks']]))
    out.append('These are selection rights. Add each rookie’s full contract schedule after the actual selection and signing. No future contract dollars are booked against an unselected player. [The draft ownership record](../2014/draft/draft_order.md) controls the picks. Overall numbers include the 32 compensatory picks announced March 24, 2014 (ledger Entry 100); Jacksonville received none.\n\n## 8. Decision calendar\n\n')
    out.append(table(['Date / review','Player or group','Financial treatment'],[
        ['March 11, 2014 (done, Entry 94)','Futures, tenders and Monroe','Futures effective; RFA/ERFA tenders and the $11,654,000 franchise tender count while unsigned'],
        ['March 16, 2014','Justin Blackmon','$1,700,000 deferred bonus cash; already allocated within the original cap schedule'],
        ['March 25, 2014 (traded March 20)','Uche Nwaneri','Roster bonus passes to Arizona; $2,189,000 of bonus proration is 2014 dead money'],
        ['Original opt-out window','Jason Babin','Keep the original 2014-2015 schedule until an actual exercise is recorded'],
        ['July 15, 2014','Eugene Monroe','Long-term agreement deadline; replace the tender, do not add a second charge'],
        ['2015 option window','Justin Blackmon','2016 fifth-year option remains unexercised; exercise decision follows the 2014 season'],
        ['2016 option window','Lane Johnson','2017 fifth-year option remains unexercised; exercise decision follows the 2015 season']]))
    out.append('## 9. Expiring contracts and free-agent classes\n\n')
    out.append(table(['Last contract year','Players'],[[year,', '.join(p['name'] for p in ps if p['contract_ends']==year and p.get('control')!='traded')] for year in sorted({p['contract_ends'] for p in ps if p['contract_ends'] is not None and p.get('control')!='traded'})]))
    out.append('“Through” describes the final league year of the recorded contract or tender. The 2013 contracts not retained expired at the March 11, 2014 league-year opening; those players are retained only as former-player history. Traded players leave these classes. A player’s class at a later expiry follows his actual accrued service; it does not extend the deal.\n\n## 10. Scheduled cash\n\n')
    out.append(table(['Item']+years,[['Signed contracts and futures']+[dollars(working_total(ps,y,'cash',('known','approximate'))) for y in years],['Unsigned tender, conditional on signing']+[dollars(working_total(ps,y,'cash',('tender',))) for y in years],['Total scheduled player cash']+[dollars(working_total(ps,y,'cash')) for y in years]]))
    out.append('Cash counts salary and the bonuses paid in that contract year; bonus proration is a cap allocation, not a second cash payment. Record actual payments separately. The 2013-2016 and 2017-2020 cash-floor tests require their complete four-year cash ledgers.\n\n## 11. Release comparisons\n\nThese are gross pre-June-1 comparisons under the adopted contract terms at this checkpoint. They exclude replacement costs and any later earned bonus, guarantee trigger or collected credit. No release is executed.\n\n')
    rows=[]
    for name in ['Roy Miller','Daryl Smith','Jason Babin','Russell Allen','Will Rackley','Jeremy Mincey','John Parker Wilson']:
        p=next(p for p in ps if p['name']==name);charge=working_charge(p['years'][current]);dead=release_exposure(p,current)
        rows.append([name,dollars(charge),dollars(dead),dollars(charge-dead)])
    out.append(table(['Player','Scheduled cap','Gross dead money','Gross cap reduction'],rows))
    out.append('## 12. Maintenance\n\nUpdate the event ledger, current contract owner and all remaining annual inputs together. A new contract replaces affected existing years; a release retains surviving bonus and guarantee charges. Preserve completed-year history. Run the generator and its check mode after every financial change. [Maintenance instructions](README.md) give the editable input path and commands.\n')
    return ''.join(out)

def render_details(d,years):
    out=[f"# Jacksonville Jaguars individual contract details\n\n[Return to the ten-year table](jaguars_cap_2014_2023.md). As of {display_date(d['as_of'])}, {d['checkpoint']}. Whole US dollars.\n\n",
    'Annual cells contain the working original or reconstructed contract schedule. Blank years lie outside that deal. The [completion research](../../library/2014_jaguars_contract_completion.md) identifies adopted simulation terms and guarantee assumptions. Cap, scheduled cash and remaining unpaid guarantees are separate amounts.\n\n']
    for p in d['players']:
        out.append(f"## {p['name']}\n\n")
        if p.get('former_player'):out.append(f"Former player; departure {display_date(p['departure_date'])}. {source_link(p['departure_source'])}.\n\n")
        rows=[['Position / status',p['position']+' / '+p['status']],['Original contract',p['contract_type']],['Signed',p['signed']],['Term',p['term']],['Contract value',p['value'] if p['value'] not in {'Unresolved','Unknown'} else '']]
        if p['control'] in {'signed','future','tender'}:
            rows += [['Bonus terms',p['bonus_terms']],['Remaining unpaid salary guarantee',dollars(p['remaining_guarantees'])],['Guarantee basis',p['guarantees']],['Schedule basis',p['schedule_basis']]]
        out.append(table(['Field','Detail'],rows))
        rows=[]
        for y in years:
            r=p['years'][y];charge=working_charge(r)
            if charge is None:rows.append([y]+['']*6);continue
            other=charge-r['base']-r['proration']
            rows.append([y,dollars(r['base']),dollars(r['proration']),dollars(other),dollars(charge),dollars(r['cash']),dollars(r.get('guaranteed_base',0))])
        out.append('### Annual schedule\n\n'+table(['Year','Base salary','Bonus proration','Other cap','Cap charge','Scheduled cash','Guaranteed base'],rows))
        if p['control'] in {'signed','future'}:
            rows=[]
            for y in years:
                r=p['years'][y];charge=working_charge(r)
                if charge is None:continue
                exposure=release_exposure(p,y)
                rows.append([y,dollars(exposure),dollars(charge-exposure)])
            out.append('### Release comparison\n\n'+table(['Year','Gross pre-June-1 dead money','Gross cap reduction'],rows))
            out.append('Assumes release before that year’s salary and bonuses are earned. Remaining guarantees plus unamortized bonus are included; replacement costs and later credits are excluded.\n\n')
        if p['control']=='tender':out.append('The tender is unsigned. Its annual cash is conditional; the full salary guarantee begins if signed.\n\n')
        elif p['control'] in {'pending','retired'}:out.append('No new playing contract is recorded for 2014 or later.\n\n')
        if p['name']=='Lane Johnson':out.append('The 2017 fifth-year option is unexercised and is excluded from committed years. Review the exercise decision in the 2016 option window.\n\n')
        elif p['name']=='Justin Blackmon':out.append('The 2016 fifth-year option is unexercised and is excluded from committed years. Review the exercise decision in the 2015 option window. The deferred bonus cash is already incorporated in the original bonus allocation and is not charged twice.\n\n')
        elif p.get('draft_pick'):out.append('Any future proven-performance escalator requires the branch’s actual qualifying participation; no later real-world escalator or extension is imported.\n\n')
        out.append('### Contract notes\n\n'+p['source_note'].rstrip('.')+'.\n\n')
        if p['plan']!='No new transaction decision in this tracker':out.append(p['plan'].rstrip('.')+'.\n\n')
        assumptions=list(dict.fromkeys(r['estimate_note'] for r in p['years'].values() if r.get('estimate_note')))
        for note in assumptions:
            if not note.startswith(p['source_note']):out.append(note.rstrip('.')+'.\n\n')
        out.append('Sources: '+', '.join(source_link(x) for x in dict.fromkeys(p['sources']))+'.\n\n')
    return ''.join(out).rstrip()+'\n'


def render(data,root=ROOT):
    years=validate(data,root)
    return {OUTPUT:render_main(data,years),DETAILS:render_details(data,years)}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    data=json.loads((ROOT/INPUT).read_text())
    try: outputs=render(data)
    except (ValueError,KeyError,TypeError) as e: print('INVALID CAP TRACKER: '+str(e));return 1
    stale=[]
    for path,content in outputs.items():
        if args.check:
            if not (ROOT/path).exists() or (ROOT/path).read_text()!=content:stale.append(str(path))
        else:(ROOT/path).write_text(content)
    if stale:print('STALE: '+', '.join(stale));return 1
    print(('PASS: ' if args.check else 'WROTE: ')+str(len(data['players']))+'-player source reconciliation and ten-year cap/detail views')
    return 0

if __name__=='__main__':sys.exit(main())
