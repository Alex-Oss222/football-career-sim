#!/usr/bin/env python3
"""Render the Jaguars' fixed 2014-2023 financial horizon without inventing unknown charges."""
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
LABELS = {'unknown_amount':'Unknown','term_unknown':'Term unknown','not_committed':'Not committed','not_signed':'Not signed','option_unexercised':'Option open'}
CBA = 'https://nflps.org/wp-content/uploads/2012/05/collective-bargaining-agreement-2011-2020.pdf'

def dollars(v):
    return 'Unknown' if v is None else f'{v:,.0f}'

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
            for k in ['cap','base','proration','cash']:
                v=row.get(k)
                if v is not None and (type(v) is not int or v<0): raise ValueError('Invalid dollar value: '+p['name'])
            if row['status'] in {'known','tender'} and row['cap'] is None: raise ValueError('Known charge requires amount')
            if row['status'] not in {'known','tender'} and row['cap'] is not None: raise ValueError('Unknown or conditional charge must not be numeric')
            if row['status']=='known' and all(row.get(k) is not None for k in ['base','proration']):
                if row['cap'] != row['base']+row['proration']+row.get('other_cap',0): raise ValueError('Cap components disagree: '+p['name'])
            if row['status']=='known' and p['contract_ends'] is not None and int(year)>p['contract_ends']: raise ValueError('Charge exceeds recorded term: '+p['name'])
    roster=md_rows((root/data['current_roster']).read_text())
    expected={x[0] for x in roster if len(x) in (6,7) and re.fullmatch(r'\d{4}-\d{2}-\d{2}',x[2])}
    current_names={p['name'] for p in players if not p.get('former_player')}
    if current_names!=expected: raise ValueError('Tracker coverage differs from current active, retired and future roster')
    source=(root/data['current_contract_table']).read_text()
    asof=display_date(data['as_of'])
    if f'**As of:** {asof}' not in source: raise ValueError('Contract table checkpoint changed; reconcile the tracker')
    contracts={x[0]:x for x in md_rows(source) if x[0] in expected}
    if set(contracts)!=expected: raise ValueError('Contract table coverage differs from tracker')
    current=str(data['start_year'])
    for p in players:
        if p.get('former_player'): continue
        row=contracts[p['name']]; y=p['years'][current]
        if len(row)==15:
            amount=exact_amount(row[10])
            if amount is not None and (y['status']!='known' or y['cap']!=amount): raise ValueError('Current charge differs from contract table: '+p['name'])
            if amount is None and y['status']=='known': raise ValueError('Tracker invents an exact current charge: '+p['name'])
        elif len(row)!=9: raise ValueError('Contract table layout changed; review parser')
        else:
            expected='tender' if 'Franchise player' in row[6] else ('unknown' if row[6].startswith('Unresolved:') else 'pending')
            if p['control']!=expected: raise ValueError('Contract status differs from current table: '+p['name'])
            if expected=='tender':
                match=re.search(r'2014 tender: \*\*\$(\d[\d,]*)',row[7])
                if not match or y['status']!='tender' or y['cap']!=int(match[1].replace(',','')): raise ValueError('Tender mismatch')
    return years

def cap_cell(row):
    if row['status']=='known':return dollars(row['cap'])
    if row['status']=='tender':return dollars(row['cap'])+' tender'
    if row['status']=='approximate':return 'About '+dollars(row['approximate_cap'])
    return LABELS[row['status']]

def totals(players, years, field='cap', status='known'):
    return [sum(p['years'][y].get(field) or 0 for p in players if p['years'][y]['status']==status) for y in years]

def partial(values): return [dollars(v)+' partial' for v in values]

def source_link(path):return '['+Path(path).stem.replace('_',' ')+'](../../'+path+')'

def contract_total(p):
    rows=list(p['years'].values());known=sum(x['cap'] or 0 for x in rows if x['status'] in {'known','tender'})
    incomplete=any(x['status'] in {'unknown_amount','term_unknown','approximate'} for x in rows)
    if incomplete:return dollars(known)+' known; incomplete' if known else 'Unknown'
    return dollars(known)+(' plus option if exercised' if any(x['status']=='option_unexercised' for x in rows) else '')

def team_accounting(d, year):
    book=d['team_years'][year]
    cap=d['league_caps'].get(year)
    adjusted=None
    if cap is not None and book['carryover'] is not None and book['net_adjustments'] is not None:
        adjusted=cap+book['carryover']+book['net_adjustments']
    room=adjusted-book['counted_team_salary'] if book['accounting_reconciled'] and adjusted is not None and book['counted_team_salary'] is not None else None
    after_rookies=room-book['rookie_incremental_reserve'] if room is not None and book['rookie_incremental_reserve'] is not None else None
    return {'adjusted':adjusted,'room':room,'after_rookies':after_rookies}

def render_main(d,years):
    ps=d['players'];known=totals(ps,years);tender=totals(ps,years,status='tender');cash=totals(ps,years,field='cash')
    counts=[Counter(p['years'][y]['status'] for p in ps) for y in years]
    accounts={y:team_accounting(d,y) for y in years}
    roster=Counter(p['control'] for p in ps if not p.get('former_player'))
    former=sum(bool(p.get('former_player')) for p in ps)
    active=sum(roster.values())-roster['retired']-roster['future']
    out=[f"# Jacksonville Jaguars cap tracker, {years[0]} to {years[-1]}\n\nAs of {display_date(d['as_of'])}, {d['checkpoint']}. Prepared {display_date(d['prepared'])} from the supplied ten-year template. All dollar amounts are whole US dollars. Caldwell owns contract decisions; this tracker records obligations and open questions.\n\n",
    "[Player cap table](#4-cap-by-player-ten-years) | [Individual contract details](jaguars_contract_details.md) | [Expirations](#9-expiring-contracts-and-free-agent-classes) | [Decision calendar](#8-decision-calendar) | [Updating this tracker](README.md)\n\n",
    f"The current inventory is {active} active players, {roster['retired']} Reserve/Retired and {roster['future']} signed futures. The individual sheets state effective dates. All {len(ps)} tracked players appear below, including {former} former players retained for financial history. The horizon stays open through {years[-1]} even after a recorded deal ends. Future contracts, draft classes and extensions will be added when executed.\n\n",
    "## 0. Conventions and formulas\n\n",
    "A number is a sourced scheduled charge, not proof of payment. **Unknown** means the term exists but the amount is incomplete. **Term unknown** means even the final contract year is unresolved. **Not signed** identifies a pending free agent without a new 2014 obligation. **Not committed** means the recorded deal supplies no charge in that year; it is not a forecast of a free roster or zero team spending. **Option open** is excluded until exercised. Approximate amounts and tenders remain visibly separate from exact signed-contract subtotals. No blank cell means zero.\n\n",
    "Cap charge adds salary, scheduled bonus proration and other applicable charges. Cash commitments track salary and bonuses attributable to a year without spreading a paid bonus over cap years. Gross scheduled charges are not counted team salary. Cap space requires adjusted club cap, the applicable counting adjustments, dead money and other obligations. A planning reserve is a budget holdback, not an NFL charge. Never subtract practice-squad or reserve-list charges twice.\n\n",
    "## 1. Global inputs, assumptions, key dates and rules\n\n### 1.1 League cap and adjustments\n\n"]
    rows=[['League cap']+[dollars(d['league_caps'].get(y)) for y in years],['Cap basis']+['Announced February 28' if y=='2014' else 'Not published at checkpoint' for y in years]]
    rows.append(['Carryover into year']+[dollars(d['team_years'][y]['carryover']) for y in years])
    rows.append(['Net league adjustments, signed amount']+[dollars(d['team_years'][y]['net_adjustments']) for y in years])
    rows.append(['Adjusted Jacksonville cap']+[dollars(accounts[y]['adjusted']) for y in years])
    rows.append(['Counting basis']+['2014 preparation; apply Top 51 at league-year activation']+['Future commitments only']*9)
    out.append(table(['Item']+years,rows))
    out.append('### 1.2 Assumptions and inputs\n\n'+table(['Input','Current treatment','Next evidence needed'],[
      ['Future cap growth','No rate assumed','Dated league announcement or explicitly approved projection'],
      ['Minimum salary, 2014','0 seasons 420,000; 1: 495,000; 2: 570,000; 3: 645,000; 4 to 6: 730,000; 7 to 9: 855,000; 10+: 955,000','Credited service for Murphy, Jackson, Long, Smith and Blake remains unresolved'],
      ['Practice squad','6,300 per week in 2014; no current PS contracts','Actual signings and paid weeks; future expansion is date-gated'],
      ['Tag/tender values','Monroe: 11,654,000 non-exclusive tender; unsigned','A replacement agreement or actual signing; do not count twice'],
      ['RFA/ERFA offers','Not executed','Actual tender, eligibility and dated amount'],
      ['Rookie pool, UDFAs and replacement reserve','Unknown','Actual picks, contracts, displaced salary and club budget decision'],
      ['Ownership player-cash budget and operating reserve','Not established','Ownership/Caldwell decision'],
      ['League position benchmarks and team allocation targets','Not established','Comparable same-date full ledgers; no target percentages invented']]))
    out.append('### 1.3 Key dates\n\n'+table(['Event','2014 date/status','Later years','Financial effect to review'],[
      ['Tag window','February 17 to March 3, 4 p.m. ET; Monroe designated February 18','Date not established here','Tender separately tracked'],
      ['Negotiating window','March 8, noon ET','Not established','Negotiation creates no signed contract'],
      ['League year and free agency','March 11, 4 p.m. ET','Not established','Futures effective, prior contracts expire, tender/counting reconciliation'],
      ['Draft','May 8 to 10','Not established','Selection rights and rookie salary accounting'],
      ['June 1 accounting boundary','June 1; designated-release relief no earlier than June 2','Recheck applicable rules','Contract-specific acceleration, guarantees and replacement costs'],
      ['Franchise long-term agreement deadline','July 15, 4 p.m. ET','Recheck applicable date','Unsigned tender does not become signed automatically'],
      ['Training camp and cutdown','See branch calendar; future dates gated','Not established','Roster and payroll review; full-count transition follows governing rule'],
      ['Trade deadline and final regular-season game','See branch calendar when released','Not established','Transaction accounting and final cash reconciliation'],
      ['Cash-spending window close','2013 to 2016 window includes the preceding 2013 year','2017 to 2020; later agreement not yet known','2014 to 2023 columns do not define new cash-floor periods']]))
    out.append(f'''### 1.4 Period-correct verification

The supplied template was a modern starting form. This tracker uses the [August 4, 2011 agreement]({CBA}), not later option tiers or practice-squad elevation rules.

- First-round options use the top-ten/remaining-first-round distinction, not Pro Bowl tiers. Injury protection starts at exercise; full protection begins in the option year if the roster condition is met. Article 7, section 7.
- Top 51 is not simply discarding every charge outside the first 51. Retained bonus charges and specified salary exceptions must be reconciled. Article 13, section 6(a).
- Release guarantees and trade assignments need separate clause review. A signing guarantee is not automatically remaining unpaid exposure. Article 13, section 6.
- Minimum salary comes from Article 26. Do not equate credited service with accrued service.

[Over the Cap's minimum table](https://overthecap.com/minimum-salaries) independently matches all seven 2014 tiers. The [NFLPA's February 2013 explanation](https://nflpa.com/press/nflpa-media-conference-call-highlights) confirms the 89% club and 95% league cash tests for 2013 to 2016 and 2017 to 2020. The [Steelers' February 28 announcement](https://www.steelers.com/news/salary-cap-set-for-2014-season-12688741) corroborates the 133,000,000 league cap. These checks establish rules and league inputs, not Jacksonville's carryover, cash ledger or future contracts. The 2021 to 2023 columns await the agreement and announcements applicable when those years arrive.

Other template rule fields, repeated-tag formulas, salary benefits, forfeitures, reserve-list treatment, vesting, split salary and incentives, remain subject to the actual instrument and the [existing financial research](../../library/2014_league_calendar_and_financial_rules.md). No generic template shortcut authorizes a transaction.

## 2. Team cap summary, ten years

''')
    rows=[['Exact signed-contract scheduled cap']+partial(known),['Separate franchise tender']+[dollars(x) for x in tender],['Known charges plus tender, still partial']+partial([a+b for a,b in zip(known,tender)]),['Exact charge rows']+[c['known'] for c in counts],['Known term, amount unknown/approximate']+[c['unknown_amount']+c['approximate'] for c in counts],['Unresolved term rows']+[c['term_unknown'] for c in counts],['Unexercised option rows']+[c['option_unexercised'] for c in counts],['Known scheduled player cash, partial']+partial(cash)]
    for label in ['Adjusted club cap','Top-51 exclusion and retained charges','Counted player contracts','Booked dead-money reconciliation','Practice squad and reserve-list reconciliation','Rookie costs after actual displacement','Incentive and workout adjustments','Total NFL commitments','Cap space','Cap space after rookies','Cap space after hypothetical voids','Actual cash paid','Cash as percent of cap','Fully guaranteed money still outstanding','All guarantee types still outstanding','Top five / top ten cap-hit share','QB / offense / defense / special-teams cap share']:
        values=None
        if label=='Adjusted club cap': values=[dollars(accounts[y]['adjusted']) for y in years]
        elif label=='Total NFL commitments': values=[dollars(d['team_years'][y]['counted_team_salary']) if d['team_years'][y]['accounting_reconciled'] else 'Unresolved' for y in years]
        elif label=='Cap space': values=[dollars(accounts[y]['room']) for y in years]
        elif label=='Cap space after rookies': values=[dollars(accounts[y]['after_rookies']) for y in years]
        elif label=='Actual cash paid': values=[dollars(d['team_years'][y]['actual_cash_paid']) for y in years]
        rows.append([label]+(values or ['Unresolved']*10))
    rows.extend([['Operating reserve']+[dollars(d['team_years'][y]['operating_reserve']) for y in years],['Ownership player-cash budget']+[dollars(d['team_years'][y]['cash_budget']) for y in years],['Signed terms known to cover year, excluding tag']+[sum(p['control'] in {'signed','future'} and (p['years'][y]['status'] in {'known','unknown_amount','approximate'}) for p in ps) for y in years],['Players in counted Top 51']+['Unresolved']*10,['Void-year charges']+['None documented']*10])
    out.append(table(['Line']+years,rows))
    out.append('Zero in a partial subtotal means no exact scheduled amount is currently recorded for that subtotal. It does not clear the unknown-term rows, options, future roster costs or unresolved liabilities. Monroe appears once, in the separate tender line. The 2014 exact-contract subtotal agrees with the existing contract table.\n\n## 3. Cap by position, ten years\n\n### 3.1 Positional cap allocation\n\nThe following is exact scheduled cap only, including the tender in its own row. Unknown and approximate amounts are excluded, so these are not percentages or rankings of full team spending.\n\n')
    rows=[]
    for pos in POSITIONS:
        group=[p for p in ps if p['position']==pos]
        rows.append([pos]+[dollars(x) for x in totals(group,years)]+[len(group),sum(p['years'][years[0]]['status'] in {'unknown_amount','approximate','term_unknown'} for p in group)])
    rows += [['Offense subtotal']+[dollars(x) for x in totals([p for p in ps if p['position'] in POSITIONS[:8]],years)]+['Not applicable','Not applicable'],['Defense subtotal']+[dollars(x) for x in totals([p for p in ps if p['position'] in POSITIONS[8:13]],years)]+['Not applicable','Not applicable'],['Special teams subtotal']+[dollars(x) for x in totals([p for p in ps if p['position'] in POSITIONS[13:]],years)]+['Not applicable','Not applicable'],['Monroe tender, OT']+[dollars(x) for x in tender]+[1,0],['Known total plus tender']+[dollars(a+b) for a,b in zip(known,tender)]+[len(ps),'Partial']]
    out.append(table(['Position']+years+['Tracked players','2014 incomplete amount rows'],rows))
    out.append('### 3.2 Guarantees and bonus exposure\n\nAnnual proration carried from an inherited 2013 transcription is an inference, not newly verified contract language. The player details retain those source limits. Remaining unpaid guarantees and bonus exposure are different columns and must not be added indiscriminately.\n\n')
    rows=[]
    for pos in POSITIONS:
        group=[p for p in ps if p['position']==pos]
        recorded=sum(x['proration'] or 0 for p in group for x in p['years'].values() if x['status'] in {'known','unknown_amount','approximate'})
        rows.append([pos,'Unresolved','Unresolved',dollars(recorded)+' recorded portion','None documented','See individual limits'])
    out.append(table(['Position','Fully guaranteed remaining','Injury-only remaining','Remaining scheduled bonus proration','Void exposure','Release exposure'],rows))
    out.append('### 3.3 Positional benchmarks\n\nNo complete same-date league salary sample or Stone/Caldwell allocation target is recorded. League average, median, top-quartile share, team target, actual full share and variance are therefore unestablished for every position. The table above tracks obligations without inventing a spending target.\n\n## 4. Cap by player, ten years\n\nPlayers with exact amounts are listed first within each room, descending by 2014 charge; unknown values cannot be ranked. Position groups include futures for financial visibility, not a depth-chart assignment. Amounts are gross scheduled charges.\n\n')
    for i,pos in enumerate(POSITIONS,1):
        out.append(f'### 4.{i} {pos}\n\n')
        group=sorted([p for p in ps if p['position']==pos],key=lambda p:(p['years']['2014']['cap'] is None,-(p['years']['2014']['cap'] or 0),p['name']))
        rows=[]
        for p in group:
            rows.append([f"[{p['name']}](jaguars_contract_details.md#{slug(p['name'])})",p['age_at_checkpoint'],p['contract_ends'] or 'Unknown','former player' if p.get('former_player') else p['control']]+[cap_cell(p['years'][y]) for y in years]+[contract_total(p)])
        rows.append([pos+' exact subtotal','Not applicable','Not applicable','Excludes tender']+[dollars(x) for x in totals(group,years)]+['Partial'])
        out.append(table(['Player','Age now','Through','Status']+years+['Recorded remaining cap'],rows))
    out.append('### 4.17 Practice squad and futures\n\n'+table(['Player','Position','Effective date','2014 cap','Later term','Current treatment'],[[p['name'],p['position'],'March 11, 2014',cap_cell(p['years']['2014']),'Unresolved','Already included above; do not add again'] for p in ps if p['control']=='future']))
    out.append('There are no current practice-squad contracts. The six future deals are camp contracts, not six paid practice-squad places. No modern elevation mechanism is assumed. Meester is included for control reconciliation with no scheduled 2014 playing salary; retirement accounting remains a separate review.\n\n### 4.18 Roster ledger totals\n\n'+table(['Line']+years,[['Exact position totals']+[dollars(x) for x in known],['Tender']+[dollars(x) for x in tender],['Applicable Top-51 adjustment']+['Unresolved']*10,['Counted contract total']+['Unresolved']*10]))
    out.append(f'## 5. Individual contract detail sheets\n\n[Open all {len(ps)} named player sheets](jaguars_contract_details.md). Each contains the known contract and service record, all ten annual cells, release/guarantee limits, incentive/option watch, amendments and the original sources. Names replace artificial sheet IDs. Common unknown clause fields are explained once rather than repeated as dozens of empty rows.\n\n## 6. Dead money and void years\n\n### 6.1 Dead-money ledger\n\n')
    out.append(table(['Player','Year','Amount','Status','Basis'],[[x['player'],x['year'],dollars(x['amount']),x['status'].replace('_',' '),x['basis']] for x in d['dead_money']]))
    out.append('No 2014 release or trade has been executed at this checkpoint. The entries above concern possible carry-forward costs of 2013 moves and remain outside booked totals until reconciled. Bray\'s possible 51,675 dead charge is distinct from his new 420,000 futures salary. The March 2013 releases and Gabbert trade remain in the 2013 accounting history; no unsupported 2014 carry is added.\n\n### 6.2 Void-year watchlist\n\nNo void-year arrangement is documented. This is not confirmation that every inherited clause has been recovered. No void date or acceleration amount is invented.\n\n### 6.3 Guarantees at risk\n\nMiller and Smith have no recorded 2014 base guarantee beyond their original signing bonuses. The four branch UDFAs and six futures have no additional guarantee in their recorded terms. Base guarantees for the six remaining drafted rookies are unresolved. Inherited guarantees, vesting dates, offsets, injury protection, forfeitures and payment status need individual evidence; original signing guarantees are not remaining cash exposure.\n\n## 7. Draft class and rookie pool\n\n### 7.1 Current picks\n\n')
    out.append(table(['Draft','Round','Original club','Slot in round','Overall number','Player / salary / net cap'],[[x['year'],x['round'],x['original_club'],x['slot_in_round'],draft_slot(x['overall']),'Not selected; amounts unresolved'] for x in d['draft_picks']]))
    out.append('Final overall numbers after round three await compensatory awards. The [draft ownership record](../2014/draft/draft_order.md) controls all assets. Jacksonville\'s 2015 second belongs to Washington. Later classes are open future work, not ten assumed annual rookie pools. No signed rookie charge, pool total or Top-51 displacement has been invented.\n\n### 7.2 Compensatory tracking\n\n2014 awards from branch 2013 free agency remain pending until the March 24 event. The 2014 free-agent window has not run, so no 2015 compensatory award is inferred. All later rows remain open.\n\n### 7.3 Undrafted free agents\n\nThe four 2013 UDFAs are already included above: Trawick, Bouye, Thielen and Anderson each have 495,000 scheduled for 2014 and 585,000 for 2015, with zero signing bonus and additional guarantee. No 2014 UDFA has been signed.\n\n## 8. Decision calendar\n\n')
    out.append(table(['Deadline / review','Player or group','Decision and present status','Amount / consequence','Owner'],[
      ['March 3, 2014, 4 p.m. ET','Monroe','Designation already completed','11,654,000 tender; do not apply a second tag','Caldwell'],
      ['Before actual bonus due date, not yet verified','Nwaneri','Review memo trade/release preference against contract','1,000,000 roster bonus; do not assume a deadline','Caldwell'],
      ['March 11, 2014, 4 p.m. ET','Bradfield; Clemons, Brown, Pasztor','Tender choices remain unexecuted','Verify amount, class and replacement cost','Caldwell'],
      ['Before affected league-year decision','John Parker Wilson; Jonathan Grimes','Resolve original contract term','Do not turn uncertainty into release or zero','Caldwell'],
      ['March 11, 2014','Six futures; Meester','Futures become effective; prior Meester contract expires','No automatic role for a futures player','Caldwell'],
      ['April 22, 2014 date-gated rail','Russell Allen','Retirement applies only when reached','Accounting unresolved; no present saving','Caldwell / medical authority'],
      ['July 15, 2014, 4 p.m. ET','Monroe','Long-term contract deadline','Unsigned status still separately tracked','Caldwell'],
      ['After 2014 season, before May 3, 2015; confirm league notice','Justin Blackmon','First-round 2016 option review','Unexercised; amount and eligibility review open','Caldwell'],
      ['After 2015 season, before May 3, 2016; confirm league notice','Lane Johnson','First-round 2017 option review','Unexercised; not a current obligation','Caldwell'],
      ['Before each relevant year-four accounting','Eligible drafted rookies','Verify branch participation and proven-performance escalator','Scheduled base is not an assumed earned escalator','Caldwell'],
      ['Every new agreement or accounting correction','All players','Refresh tracker, current table and affected source owners','Keep closed years and prior agreements in history','Caldwell record / repository maintenance']]))
    out.append('## 9. Expiring contracts and free-agent classes\n\n### 9.1 Current March 11 handoff\n\n')
    out.append(table(['Player','Position','Current class / status','Recorded plan'],[[p['name'],p['position'],p['status'],p['plan']] for p in ps if p['control'] in {'pending','unknown','tender','retired'}]))
    out.append('### 9.2 Through 9.4 Annual expiration watch\n\nFuture free-agent classes depend on actual accrued service. A scheduled expiration is not proof a player will reach it with Jacksonville. Option years are listed separately from firm terms. Monroe\'s 2014 entry is the tender year, not a signed extension.\n\n')
    rows=[]
    for y in years:
        group=[p for p in ps if p['contract_ends']==int(y)]
        rows.append([y,', '.join(p['name'] for p in group) or 'No confirmed term ends recorded', 'Verify actual accrued service and contract outcome', 'No future market APY assumed'])
    out.append(table(['Last recorded contract/tender year','Players','Free-agent class at that future expiry','Market / re-signing assumption'],rows))
    unknown=[p['name'] for p in ps if p['contract_ends'] is None]
    out.append('Unresolved final year: '+', '.join(unknown)+'. These names remain visibly unresolved across the horizon, rather than being dropped after 2014.\n\n### 9.5 Re-signings and replacements\n\nNo projected replacement salary, market APY, automatic extension or future roster has been adopted. The 2014 memo\'s desired outcomes remain in the decision records; they do not populate future contract columns.\n\n## 10. Cash spending and floor tracking\n\n### 10.1 Annual cash\n\n')
    rows=[['Known scheduled cash if retained, partial']+[dollars(x) for x in cash],['Monroe salary if tender signed, separate']+[dollars(x) for x in tender]]
    for n in ['Actual base payments','Actual signing/option/restructure payments','Actual roster/workout/reporting bonuses','Incentives and escalators paid','Practice-squad and reserve payments','Settlements and grievances paid','Total qualifying cash paid','Cash as percent of league cap','Ownership budget / variance']:
        if n=='Total qualifying cash paid': values=[dollars(d['team_years'][y]['actual_cash_paid']) for y in years]
        elif n=='Ownership budget / variance': values=[dollars(d['team_years'][y]['cash_budget'])+' budget; '+(dollars(d['team_years'][y]['cash_budget']-d['team_years'][y]['actual_cash_paid']) if d['team_years'][y]['cash_budget'] is not None and d['team_years'][y]['actual_cash_paid'] is not None else 'unknown')+' unspent' for y in years]
        else: values=['Unresolved']*10
        rows.append([n]+values)
    out.append(table(['Line']+years,rows))
    out.append('The scheduled cash subtotal includes only annual cash amounts supported by recorded contracts. It excludes inherited amounts not fully recovered, payment-timing uncertainty and an unsigned tender. It is not evidence of an actual payment or satisfaction of the spending floor.\n\n### 10.2 Cash-floor windows\n\n'+table(['Window','Included years','Cap denominator known so far','Club minimum','Actual cash / compliance'],[
      ['First period','2013, 2014, 2015, 2016','256,000,000 for 2013 and 2014 only; later caps not yet known','89% of the complete four-year total','Unresolved; recover 2013 cash as well'],
      ['Second period','2017, 2018, 2019, 2020','Unresolved','89% of the complete four-year total','Unresolved'],
      ['Later horizon','2021, 2022, 2023','Unresolved','Applicable future agreement not yet available','No floor test invented']]))
    out.append('## 11. Scenario worksheet\n\nThese are conditional comparisons from existing terms, not approved moves. Savings are gross and exclude replacement-player costs, Top-51 changes, termination pay and unverified clauses.\n\n')
    out.append(table(['Possible action','Year','Scheduled cap','Recorded bonus dead money','Gross cap reduction','Limit'],[
      ['Release Roy Miller before June 1','2014','3,250,000','750,000','2,500,000','Recorded base is not guaranteed; verify instrument and replacement'],
      ['Release Daryl Smith before June 1','2014','3,500,000','500,000','3,000,000','Recorded base is not guaranteed; verify instrument and replacement'],
      ['Do both, purely arithmetic','2014','6,750,000','1,250,000','5,500,000','Not a football recommendation or certified net space'],
      ['Nwaneri, Allen, Rackley or Mincey memo move','2014','Partial/unresolved','Partial/unresolved','Not certified','Recover bonus timing, remaining guarantees and actual transaction terms'],
      ['Replace Monroe tender with an extension','2014 onward','Tender 11,654,000','New structure not agreed','Unresolved','Remove tender only when the replacement takes effect'],
      ['Restructure or add void years','Any horizon year','No agreement','No agreement','Not booked','Check eligibility, minimums, consent, proration and future CBA constraints']]))
    out.append('### 11.1 Scenario stacking\n\nOnly the explicitly labeled Miller-plus-Smith arithmetic above is combined. Other scenarios are not stacked, and none feed committed totals. This prevents counting the same player\'s release, trade and restructure savings together. New proposals require a named action, sourced inputs and replacement costs before comparison.\n\n## 12. Glossary and maintenance\n\n'+table(['Term','Meaning in this tracker'],[
      ['Scheduled cap','Contract charge assigned to a year, before team counting adjustments'],['Cash commitment / paid cash','Contractual annual amount / separately evidenced payment'],['Partial total','Sum of established numeric entries; missing entries are not zero'],['Unamortized bonus','Bonus proration still allocated to later years; separate from unpaid guarantees'],['Dead money','Obligations surviving departure, subject to transaction and guarantee terms'],['Option open','A conditional future year not exercised and not in commitments'],['Accrued / credited service','Different service tests for free agency and minimum salary; use sourced counts'],['LTBE / NLTBE','Incentive accounting categories, not player-quality judgments'],['APY','Contract average, not the charge for any particular year'],['Cap space','Unavailable until all counted obligations and club adjustments reconcile']]))
    out.append('The [maintenance instructions](README.md) identify the editable financial inputs and regeneration command. Original event ledgers, signed terms, current roster and contract register remain authoritative. The tracker adds a ten-year view without advancing the clock or replacing those owners.\n')
    return ''.join(out)

def render_details(d,years):
    out=[f"# Jacksonville Jaguars individual contract details\n\n[Return to the ten-year table](jaguars_cap_2014_2023.md). Snapshot: {display_date(d['as_of'])}, {d['checkpoint']}. Whole US dollars. All {len(d['players'])} tracked players have a named sheet below.\n\nThe supplied template's clause fields remain relevant. Unless a player entry establishes them, agent, jersey number, option/restructure/reporting bonuses, incentive schedules, split salary, guarantee vesting, offset, no-trade/no-tag language, deferrals, advances and physical clauses are **unresolved**, not zero or absent. No speculative market value or performance rating is added. Cash means scheduled annual commitment if retained, not paid-to-date. An inherited annual bonus carry-forward is only the inference disclosed in the current contract table.\n\n"]
    for p in d['players']:
        out.append(f"## {p['name']}\n\n### Contract and service\n\n")
        if p.get('former_player'):
            out.append(f"Former player, departed {display_date(p['departure_date'])}; financial history and surviving obligations retained. Departure: {source_link(p['departure_source'])}.\n\n")
        rows=[['Position / current status',p['position']+' / '+p['status']],['Birth date / age at checkpoint',p['date_of_birth']+' / '+str(p['age_at_checkpoint'])],['Acquisition / contract',p['contract_type']],['Signed',p['signed']],['Recorded term',p['term']],['Last recorded contract/tender year',p['contract_ends'] or 'Unresolved'],['Reported original deal value',p['value']],['Signing bonus and proration',p['bonus_terms']],['2014 guarantee evidence',p['guarantees']],['Remaining guarantees',dollars(p['remaining_guarantees'])],['Credited seasons',p['credited_seasons']],['Accrued service evidence',p['accrued_seasons']],['Availability',p['availability']],['New-money APY / payment dates / other clauses','Unresolved unless established in the sources below'],['Void years','None documented; inherited clauses not exhaustively verified']]
        if p['control']=='tender':rows.append(['Current tender versus original deal','The original 25,000,000 rookie deal above ends in 2013. The separate 2014 tender is 11,654,000, unsigned.'])
        out.append(table(['Field','Recorded detail'],rows))
        out.append('### Annual cap and cash\n\n')
        rows=[]
        for y in years:
            x=p['years'][y];inforce=x['status'] in {'known','unknown_amount','approximate','tender'}
            pror_after=sum(v['proration'] or 0 for yy,v in p['years'].items() if int(yy)>int(y) and v['status'] in {'known','unknown_amount','approximate'})
            if not inforce:base=pror=other=cash=exposure='Not applicable' if x['status']=='not_committed' else 'Unresolved'
            else:
                base=x.get('base_note',dollars(x['base']));pror=dollars(x['proration']);cash=dollars(x['cash'])
                other=dollars(x['cap']-x['base']-x['proration']) if all(x.get(k) is not None for k in ['cap','base','proration']) else ('1,000,000 roster; other components unresolved' if p['name']=='Uche Nwaneri' and y=='2014' else 'Unresolved')
                exposure=dollars(pror_after)+' recorded portion' if x['proration'] is not None else 'Unresolved'
            rows.append([y,base,pror,other,cap_cell(x),cash,exposure])
        out.append(table(['Year','Base salary','Bonus proration','Other cap components','Scheduled cap','Scheduled cash','Bonus allocated after year'],rows))
        out.append('### Release, trade and restructure review\n\n')
        out.append('Recorded 2014 pre-June-1 exposure: '+p['dead_money_2014']+'. Guarantees can make release different from trade. No automatic restructure or void years are added.\n\n')
        rows=[]
        for y in years:
            x=p['years'][y]
            if x['status'] not in {'known','unknown_amount','approximate','tender'}: continue
            remaining=sum(v['proration'] or 0 for yy,v in p['years'].items() if int(yy)>=int(y) and v['status'] in {'known','unknown_amount','approximate'})
            future=remaining-(x['proration'] or 0)
            known_bonus=x['proration'] is not None
            certain=p['remaining_guarantees']==0 and known_bonus
            pre=dollars(remaining) if certain else (dollars(remaining)+' bonus floor; guarantees unresolved' if known_bonus else 'Unresolved')
            saving=dollars(x['cap']-remaining) if certain and x['cap'] is not None else 'Unresolved'
            rows.append([y,cap_cell(x),pre,saving,dollars(x['proration'])+' bonus portion' if known_bonus else 'Unresolved',dollars(future)+' bonus portion' if known_bonus else 'Unresolved','Unresolved; verify terms'])
        if rows:out.append(table(['Year','Scheduled cap','Pre-June-1 exposure','Gross saving before replacement','Post-June-1 current-year bonus','Post-June-1 next-year bonus','Trade / max restructure'],rows))
        else:out.append('No new signed charge supplies a release-savings calculation. Outstanding old-contract liabilities, if any, require separate reconciliation.\n\n')
        out.append('### Guarantees and incentives\n\n'+p['guarantees']+'. Remaining unpaid exposure is '+dollars(p['remaining_guarantees']).lower()+'. Paid bonus and cap proration are not a second unpaid guarantee. No earned incentive, vesting event or forfeiture is inferred from a season summary.\n\n')
        rookie_note='No new rookie option or escalator amount has been established.'
        if p['name']=='Lane Johnson':rookie_note='Branch pick 2 in 2013. The 2017 first-round option is unexercised. Review after the 2015 season under the period rule; no real Eagles extension is imported.'
        elif p['name']=='Justin Blackmon':rookie_note='Inherited 2012 first-round deal. The potential 2016 option remains unexercised; review eligibility and terms after the 2014 season. Suspension/forfeiture questions are not resolved by this table.'
        elif p['name']=='Tyler Bray':rookie_note='The 2013 pick-208 deal ended at the August 31 waiver. Its old 2014 to 2016 salaries do not return with the futures signing. Possible old bonus dead money remains separate.'
        elif p.get('draft_pick'):rookie_note=f"Branch 2013 pick {p['draft_pick']}. The executed schedule is carried through 2016. Any applicable proven-performance escalator requires branch participation evidence; no future threshold is assumed met. No first-round option applies."
        elif p['name'] in ['A.J. Bouye','Adam Thielen','Brynden Trawick','C.J. Anderson']:rookie_note='Three-year 2013 UDFA contract through 2015; no first-round option. No new extension is assumed.'
        out.append('### Rookie terms and conditional years\n\n'+rookie_note+'\n\n')
        out.append('### Tags, tenders and expiration\n\n')
        if p['control']=='tender':out.append('Non-exclusive designation February 18, 2014; 11,654,000 official February 28; tender unsigned. The July 15 long-term deadline is a decision date, not an automatic signing. No offer sheet or matching outcome is created here.\n\n')
        elif p['control']=='pending':out.append(p['status']+'. '+p['plan']+'. Any tender or new deal must be recorded before a future charge is added.\n\n')
        else:out.append('The firm term and annual status above control. Future free-agent class depends on actual accrued service; a new tender, tag or extension is not presumed.\n\n')
        out.append('### Amendments and decision notes\n\n')
        changes=[x for x in d['amendments'] if x.get('player')==p['name']]
        out.append(('\n'.join('- '+x['description'] for x in changes) if changes else 'No new restructure, conversion or extension is executed by this tracker.')+'\n\n')
        out.append((p['plan']+'. ' if p['plan']!='No new transaction decision in this tracker' else '')+p['source_note']+'.\n\n')
        out.append('Sources: '+', '.join(source_link(x) for x in p['sources'])+'.\n\n')
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
