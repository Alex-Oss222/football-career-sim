#!/usr/bin/env python3
"""Render the Jaguars' rolling twelve-year financial horizon from sourced and adopted simulation contract schedules."""
import argparse
from collections import Counter
from datetime import date
from decimal import Decimal
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from runtime.player_bios import biographies
from runtime.season_layout import logical_path, repository_relative
from runtime.seasons import SeasonPaths, page_link
from runtime.season_layout import PLAYER_FINANCES
INPUT = Path(PLAYER_FINANCES)
OUTPUT = Path('career/finances/salary_cap/cap_tracker.md')
DETAILS = Path('career/finances/player_contracts/contract_details.md')
ORGANIZATION = Path('career/finances/coaching_and_organization/coaching_payroll.md')
POSITIONS = ['QB','RB','FB','WR','TE','OT','OG','C','EDGE','IDL','LB','CB','S','K','P','LS']
STATUSES = {'known','unknown_amount','approximate','term_unknown','not_committed','not_signed','tender','option_unexercised'}
CBA = 'https://nflps.org/wp-content/uploads/2012/05/collective-bargaining-agreement-2011-2020.pdf'

def dollars(v):
    return '' if v is None else (f'-${abs(v):,.0f}' if v<0 else f'${v:,.0f}')

def display_date(value):
    return date.fromisoformat(value).strftime('%B %d, %Y').replace(' 0', ' ')

def source_path(path, root=ROOT):
    """Read frozen financial references through the current folder layout."""
    return root / repository_relative(path.split('#')[0])

def departure_source(player, data):
    source = player.get('departure_source', '')
    if Path(source).name != 'ledger.md':
        return source
    if player['control'] == 'traded':
        return logical_path(int(player['departure_date'][:4]), 'trades/trades.md')
    return next((path for path in player['sources'] if path.endswith('/contract_status.md')),
                data['current_contract_table'])

# Reader wording for the stored accounting notes (rebuild step 3b): the facts and figures stay as
# the inputs hold them; only system words, raw file paths, research codes and the "M" unit change.
# A player's name that contains a checked word (Andre Branch) is never touched.
READER_WORDS = (
    (re.compile(r'\ba labelled simulation reconstruction\b'), 'a labelled reconstruction'),
    (re.compile(r'\bsimulation reconstruction\b'), 'reconstruction'),
    (re.compile(r'\b[Ss]imulation\b'), lambda m: 'Reconstructed' if m[0][0] == 'S' else 'reconstructed'),
    (re.compile(r"\bthe branch(?:'s|’s)"), 'Jacksonville’s'),
    (re.compile(r'(?<!Andre )(?<!Alan )(?<!Tyvon )\b[Bb]ranch\b'), 'Jacksonville'),
    (re.compile(r'\bdead-money ledger\b'), 'dead-money table'),
    (re.compile(r'\bcash ledgers\b'), 'cash records'),
    (re.compile(r'\bledger\b'), 'record'),
    (re.compile(r'\bcash receipts\b'), 'cash received'),
    (re.compile(r' \(library [A-Z]\d+(?:, (?:Confirmed|Unverified))?\)'), ''),
    (re.compile(r',? library [A-Z]\d+\b(?:, (?:Confirmed|Unverified))?'), ''),
    (re.compile(r'\$(\d[\d,]*(?:\.\d+)?)M\b'), r'$\1 million'),
)
# Notes written for the record-keepers rather than the reader: clauses that only say a later
# real-world move is not applied, research-file references, and wording joined without its full
# stop when a later transaction was appended. Each rewrite keeps every figure the note holds.
CONTRACT_NAMES = (
    (re.compile(r'^Rookie scale, pick #(\d+)$'), r'rookie-scale contract (pick #\1)'),
    (re.compile(r'^Rookie, (\d{4}) (\w+) round$'), r'\1 \2-round rookie contract'),
    (re.compile(r'^Veteran minimum (.+)$'), r'veteran-minimum contract \1'),
    (re.compile(r'^(?:UDFA|udfa) minimum$'), 'undrafted minimum contract'),
    (re.compile(r'^Reserve/future, (.+)$'), r'reserve/future contract of \1'),
)


def contract_name(match):
    name = match[2]
    for pattern, new in CONTRACT_NAMES:
        if pattern.match(name):
            return match[1] + ' ' + pattern.sub(new, name) + ' ended'
    return match[0]


RECORD_NOTES = (
    (re.compile(r' No later Washington contract is imported\.'), ''),
    (re.compile(r'; no later real-world escalator or extension is imported'), ''),
    (re.compile(r' Later actual suspension/tolling does not apply\.'), ''),
    (re.compile(r'; do not add them to cap twice'), ' and are counted once'),
    (re.compile(r'\. The \d{4} salary reduction in real history is excluded;'), ';'),
    (re.compile(r'; no real \d{4} replacement deal is imported'), ''),
    (re.compile(r' No later retirement or real release is executed here\.'), ''),
    (re.compile(r' No real release is imported\.'), ''),
    (re.compile(r' Later real contracts do not extend it\.'), ''),
    (re.compile(r'; the later real extension is excluded'), ''),
    (re.compile(r' The later real Houston contract is a different deal and is excluded\.'), ''),
    (re.compile(r"\.? Not the player's real contract(?=[.\s]|$)"), '.'),
    (re.compile(r'\binferred from his real ([A-Z][a-z]+ \d{4})'), r'inferred from his \1'),
    (re.compile(r'\bhis real retirement\b'), 'his retirement'),
    (re.compile(r'\bin this branch\b'), 'at Jacksonville'),
    (re.compile(r', before divergence\.'), '.'),
    (re.compile(r'\b(is |was )?modeled as\b'), lambda m: (m[1] or '') + 'treated as'),
    (re.compile(r'\bmodeled without\b'), 'recorded without'),
    (re.compile(r'\bthe library does not record the rule\b'), 'the league rule is not on file'),
    (re.compile(r'\bthe library records no proration rule\b'), 'no league proration rule is on file'),
    (re.compile(r"\bthe library's Confirmed (\d{4}) figure\b"), r'the confirmed \1 league figure'),
    (re.compile(r'\(library section \w+, Confirmed\)'), '(confirmed league figure)'),
    (re.compile(r'\bthe nflverse/OTC historical contracts file\b'), 'the historical contract records'),
    (re.compile(r'(?<=[a-z]) (Waived|Released) (?=(?:January|February|March|April|May|June|July|August|'
                r'September|October|November|December) \d)'), r'. \1 '),
    (re.compile(r'\b([Tt]he(?: earlier)?) ((?:Rookie|Veteran|UDFA|udfa|Reserve/future)[^;.]*?) ended\b'), contract_name),
)
RAW_PATH = re.compile(r'(?<![\[/\w])(career/[^\s)\]]+\.md)(#[\w-]+)?')


def reader_words(text):
    """``text`` in reader wording, outside link destinations and web addresses."""
    parts = re.split(r'(\]\([^)]*\)|https?://\S+)', text)
    for i in range(0, len(parts), 2):
        piece = parts[i]
        for pattern, new in RECORD_NOTES + READER_WORDS:
            piece = pattern.sub(new, piece)
        parts[i] = RAW_PATH.sub(lambda m: source_link(m[1], Path(m[1]).stem.replace('_', ' ')
                                                      .rstrip(' 0123456789-').strip() or 'record'), piece)
    return ''.join(parts)


def presentation_note(text, contract_table):
    """Keep the frozen accounting basis, but present named records to readers."""
    contract = source_link(contract_table, 'adopted contract reconstruction')
    text = text.replace('Branch record (Entry 85); minimum Confirmed Entry 91',
                        'The minimum salary is confirmed in the signing record. The ' + contract)
    text = text.replace('adopted in Entry 91', 'adopted in the ' + contract)
    text = text.replace('Entry 91', 'The ' + contract)
    reference = r'Entr(?:y|ies) \d+(?:(?:, | and | to |[-–])\d+)*'
    text = re.sub(r' \(' + reference + r'\)', '', text)
    text = re.sub(r'\(' + reference + r'; ', '(', text)
    text = re.sub(r', ' + reference, '', text)
    text = re.sub(r'negotiation record (career/[^\s)]+\.md)',
                  lambda match: source_link(match[1], 'negotiation record'), text)
    text = text.replace('March 2014 replay log', source_link(
        SeasonPaths(2014, ROOT).record('free_agency/march_2014_replay_log.md').relative_to(ROOT).as_posix(),
        'March 2014 signing record'))
    return reader_words(text)

def slug(name):
    return re.sub(r'[^\w -]', '', name.lower()).replace(' ', '-')

def draft_slot(value):
    rounds=re.findall(r'C([3-6])',value)
    if not rounds:return value
    label='round '+rounds[0] if len(rounds)==1 else 'rounds '+rounds[0]+' to '+rounds[-1]
    return value.split(' + ')[0]+' + compensatory picks from '+label

def table(headers, rows):
    annual = [i for i, h in enumerate(headers) if re.fullmatch(r'20\d{2}', str(h))]
    if len(annual) == 12:
        fixed = [i for i in range(len(headers)) if i not in annual]
        result = []
        for label, selected in [('Nine-year view', annual[:9]), ('Additional three years', annual[9:])]:
            indices = sorted(fixed + selected)
            result.append('**' + label + '**\n\n' + table(
                [headers[i] for i in indices], [[row[i] for i in indices] for row in rows]))
        return ''.join(result)
    def cell(v): return str(v).replace('|', '/').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(map(cell,headers))+' |', '|'+ '|'.join(['---']*len(headers))+'|'] + ['| '+' | '.join(map(cell,row))+' |' for row in rows])+'\n\n'

def md_rows(text):
    return [[c.strip() for c in l.strip('|').split('|')] for l in text.splitlines() if l.startswith('|')]

def exact_amount(text):
    m=re.fullmatch(r'\$(\d[\d,.]*)(M)?(?: from March 11)?', text)
    return int(Decimal(m[1].replace(',',''))*(1000000 if m[2] else 1)) if m else None

def validate(data, root=ROOT):
    years=list(map(str,range(data['start_year'],data['end_year']+1)))
    if len(years)!=12: raise ValueError('The tracker must cover exactly twelve explicit league years')
    players=data['players'];names=[p['name'] for p in players]
    if set(data['team_years'])!=set(years): raise ValueError('Missing team accounting year')
    for y,book in data['team_years'].items():
        if 'opening_workout_charge' in book:
            value = book['opening_workout_charge']
            if type(value) is not int or value < 0 or not source_path(book.get('opening_workout_source',''),root).is_file():
                raise ValueError('Opening workout charge requires a nonnegative amount and source')
        for key in ['carryover','net_adjustments','counted_team_salary','actual_cash_paid','operating_reserve','rookie_incremental_reserve','cash_budget']:
            value=book[key]
            if value is not None and (type(value) is not int or (key!='net_adjustments' and value<0)):
                raise ValueError('Invalid team accounting amount')
        if any(book[k] is not None for k in ['carryover','net_adjustments','counted_team_salary','actual_cash_paid','operating_reserve','rookie_incremental_reserve','cash_budget']) and not book['sources']:
            raise ValueError('Team accounting requires sources')
        if 'carryover_working_estimate' in book:
            est = book['carryover_working_estimate']
            if (type(est.get('low')) is not int or type(est.get('high')) is not int
                    or not 0 <= est['low'] <= est['high']
                    or not source_path(est.get('source', ''),root).is_file()):
                raise ValueError('Carryover working estimate requires a low-high range and a source')
        if book['accounting_reconciled']:
            if any(book[k] is None for k in ['carryover','net_adjustments','counted_team_salary']) or y not in data['league_caps']:
                raise ValueError('Reconciled accounting requires complete inputs')
            if any(p['years'][y]['status'] in {'unknown_amount','term_unknown','approximate'} for p in players):
                raise ValueError('Cannot certify room with unresolved player obligations')
    if len(names)!=len(set(names)): raise ValueError('Duplicate player would double-count obligations')
    for p in players:
        if p.get('former_player'):
            if not p.get('departure_source') or not source_path(departure_source(p,data),root).is_file():
                raise ValueError('Former player requires a departure source')
            if date.fromisoformat(p['departure_date']) > date.fromisoformat(data['as_of']):
                raise ValueError('A future departure cannot archive a current player')
        if p['position'] not in POSITIONS: raise ValueError('Unknown position: '+p['name'])
        if set(p['years'])!=set(years): raise ValueError('Missing annual status: '+p['name'])
        if not p['sources'] or any(not source_path(s,root).is_file() for s in p['sources']): raise ValueError('Missing source: '+p['name'])
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
    # Every player the roster record lists (the active roster, the reserve lists and the practice
    # squad) carries a contract here, and only they are current players.
    from runtime import roster as roster_record
    expected={row['name'] for row in roster_record.load(source_path(data['current_roster'],root))['players']}
    current_names={p['name'] for p in players if not p.get('former_player')}
    if current_names!=expected: raise ValueError('Tracker coverage differs from current active, retired and future roster')
    source=source_path(data['current_contract_table'],root).read_text()
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


def source_link(path, label=None):
    return '['+(label or Path(path).stem.replace('_',' '))+'](../../'+repository_relative(path)+')'

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
    out=[f"# Jacksonville Jaguars cap tracker, {years[0]} to {years[-1]}\n\nAs of {display_date(d['as_of'])}. Whole US dollars.\n\n",
    '[Player cap table](#cap-by-player) | [Individual contract details](jaguars_contract_details.md) | [Expirations](#expiring-contracts-and-free-agent-classes)\n\n',
    f"The inventory covers {sum(roster.values())} current players: {roster['signed']} under signed contracts (reserve/future contracts from March 11 and practice-squad contracts from August 31, 2014 included while in force) and {roster['tender']} on unsigned tenders (RFA or ERFA). {len(ps)-sum(roster.values())} former players stay listed for their contract history and remaining charges.\n\n",
    '## Reading the table\n\n',
    '**Each amount is the working cap charge for that contract year. A blank means the recorded deal does not cover that year.** Existing sourced schedules and adopted simulation amounts are both included. The individual notes identify their basis; the [completion research](../../library/2014_jaguars_contract_completion.md) explains the assumptions. These terms persist until a recorded amendment or correction changes them.\n\n',
    'The table runs twelve years so later commitments stay in view. Pending free agents and unexercised options create no new salary commitment. Each unsigned tender is included once. Scheduled cash means money payable if the player remains under the stated terms, not evidence that it has already been paid.\n\n',
    '## League cap rules\n\n',
    table(['Rule',current],[
        ['League salary cap',dollars(d['league_caps'][current])],
        ['Reserve/future effective date','March 11, 2014'],
        ['Counting rule','Top 51 from the league-year opening, including retained bonus and other required charges'],
        ['2014 minimum salaries','$420,000 / $495,000 / $570,000 / $645,000 / $730,000 / $855,000 / $955,000 for 0 / 1 / 2 / 3 / 4-6 / 7-9 / 10+ credited seasons'],
        ['Future league caps','Published as each league year opens'],
        ['Club accounting','Carryover, adjustments and actual cash received are kept in the club’s cap worksheet']]),
    f"The [2011 agreement]({CBA}) controls the era’s minimums, bonus allocation, Top-51 treatment, options and cash-floor windows. [The original-contract research](../../library/2014_jaguars_original_contract_reconstruction.md) supplies the historical salaries and bonus schedules. The [club worksheet]({page_link(d['start_year'], 'offseason/current_cap_worksheet.md', 1)}) separates scheduled player commitments from adjusted club cap room.\n\n",
    '## Team cap summary, twelve years\n\n']
    active = [p for p in ps if not p.get('former_player')]
    accounting = team_accounting(d, current)
    money = lambda value: dollars(value) if value is not None else 'Unresolved'
    dashboard = '## Current cap at a glance\n\n' + table(
        ['Measure', current, 'Meaning'], [
            ['League cap', dollars(d['league_caps'][current]), 'Published league limit'],
            ['Adjusted team cap', money(accounting['adjusted']), 'League cap plus verified carryover and adjustments'],
            ['Recorded player obligations', dollars(working_total(ps,current)), 'All scheduled contracts, including unsigned tenders once'],
            ['Dead money', dollars(sum(x['amount'] for x in d['dead_money'] if str(x['year'])==current)), 'Separate departed-contract charges'],
            ['Certified cap space', money(accounting['room']), 'Withheld until club accounting is reconciled'],
            ['Space after rookie reserve', money(accounting['after_rookies']), 'Requires verified net rookie cost and certified space'],
        ])
    dashboard += f'The [current worksheet]({page_link(d["start_year"], "offseason/current_cap_worksheet.md", 1)}) records the Top-51 calculation and workout charge. A league-cap difference is not certified available room. [Organization finances](organization_finances.md) contains coaching commitments.\n\n'
    if current == '2014':
        # Preserve required bonus charges below Top 51; displace only their base (P5) salary.
        ranked = sorted(active, key=lambda p: -(working_charge(p['years'][current]) or 0))
        excluded_base = sum(p['years'][current]['base'] for p in ranked[51:])
        dead = sum(x['amount'] for x in d['dead_money'] if str(x['year']) == current)
        top51 = working_total(ps,current) - excluded_base + dead
        workout = d['team_years'][current]['opening_workout_charge']
        dashboard += table(['Working offseason reconciliation', current], [
            ['Recorded player obligations', dollars(working_total(ps,current))],
            ['Base salary displaced below Top 51', dollars(-excluded_base)],
            ['Separate dead money', dollars(dead)],
            ['Top-51 obligations before workout charge', dollars(top51)],
            ['Opening workout charge (recorded worksheet)', dollars(workout)],
            ['Working counted total', dollars(top51+workout)],
            ['Difference below league cap, before club adjustments and reserves', dollars(d['league_caps'][current]-top51-workout)],
        ])
        est = d['team_years'][current].get('carryover_working_estimate')
        if est:
            difference = d['league_caps'][current]-top51-workout
            dashboard += table(['Rollover from the prior year (working estimate, not certified)', current], [
                ['Unused prior-year room carried in', f"{dollars(est['low'])} to {dollars(est['high'])}"],
                ['Difference including the rollover estimate', f"{dollars(difference+est['low'])} to {dollars(difference+est['high'])}"],
            ])
            dashboard += f"The rollover is calculated step by step in the [cap worksheet]({page_link(d['start_year'], 'offseason/current_cap_worksheet.md', 1)}#2013-rollover). It becomes certified room only when club accounting is reconciled.\n\n"
    # Ages come from the birth-date registry with the canon overrides
    # (runtime/player_bios.py), as of the inputs' date; the inputs store none.
    ages = biographies([p['name'] for p in active], d['as_of'])
    dashboard += '## Current player cap breakdown\n\n' + table(
        ['Player','Pos','Age','Status','Cap hit','% of league cap','Base','Bonus proration','Other cap','Unpaid guaranteed salary'],
        [[f"[{p['name']}](jaguars_contract_details.md#{slug(p['name'])})", p['position'],ages[p['name']]['age'],
          'Unsigned tender' if p['control']=='tender' else 'Signed',
          dollars(working_charge(p['years'][current])),
          f"{100 * working_charge(p['years'][current]) / d['league_caps'][current]:.2f}%",
          dollars(p['years'][current]['base']), dollars(p['years'][current]['proration']),
          dollars(working_charge(p['years'][current])-p['years'][current]['base']-p['years'][current]['proration']),
          dollars(p['remaining_guarantees']) if p['remaining_guarantees'] is not None else 'Conditional on signing']
         for p in sorted(active,key=lambda p:-(working_charge(p['years'][current]) or 0))])
    dashboard += 'Percentages use the published league cap because adjusted club cap is unresolved. Other cap is the recorded total of the remaining charges; roster, option, workout and incentive amounts not yet verified are not broken out. Unpaid guarantees exclude bonuses already paid.\n\n'
    out.insert(2, dashboard)
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
    out.append('These are the working obligations for the recorded deals, before club adjustments and additional roster construction. They are not a forecast of total team spending after these contracts expire.\n\n## Cap by position, twelve years\n\n')
    rows=[[pos]+[dollars(working_total([p for p in ps if p['position']==pos],y)) for y in years] for pos in POSITIONS]
    for label,positions in [('Offense',POSITIONS[:8]),('Defense',POSITIONS[8:13]),('Special teams',POSITIONS[13:])]:
        rows.append([label]+[dollars(working_total([p for p in ps if p['position'] in positions],y)) for y in years])
    rows.append(['All player contracts']+list(map(dollars,player)))
    out.append(table(['Position']+years,rows))
    out.append('Unsigned tenders are included in their positions. Each player is counted once. Futures are grouped by position for accounting; this does not assign a depth-chart role.\n\n## Cap by player\n\n')
    labels={'signed':'Signed','future':'Futures','pending':'Pending free agent','tender':'Unsigned tender','retired':'Retired','released':'Released','waived':'Waived','traded':'Traded'}
    for i,pos in enumerate(POSITIONS,1):
        out.append(f'### {pos}\n\n')
        group=sorted([p for p in ps if p['position']==pos],key=lambda p:(-(working_charge(p['years'][current]) or 0),p['name']))
        rows=[]
        for p in group:
            rows.append([f"[{p['name']}](jaguars_contract_details.md#{slug(p['name'])})",p['contract_ends'] or '',labels.get(p['control'],p['control'])]+[cap_cell(p['years'][y]) for y in years]+[contract_total(p)])
        rows.append([pos+' total','','']+[dollars(working_total(group,y)) for y in years]+[dollars(sum(working_total(group,y) or 0 for y in years)) if any(working_total(group,y) is not None for y in years) else ''])
        out.append(table(['Player','Through','Status']+years+['Remaining cap total'],rows))
    futures=[p for p in ps if p['contract_type'].startswith('Reserve/future') and not p.get('former_player')]
    out.append(f"### Futures contracts\n\n{len(futures)} of the six reserve/future contracts signed in February 2014 remain in force under the adopted two-year terms through 2015 (the others ended with the August 30, 2014 waivers; see the dead-money ledger and the former-player sheets). They have no signing bonus or salary guarantee. Their dollars already appear in the position tables above.\n\n")
    out.append(table(['Player','2014 salary / cap','2015 salary / cap','Total'],[[p['name'],cap_cell(p['years']['2014']),cap_cell(p['years']['2015']),contract_total(p)] for p in futures]))
    out.append(f'## Individual contract detail sheets\n\n[Open all {len(ps)} player sheets](jaguars_contract_details.md) for annual salary, bonus, cap, cash, guarantees and sources.\n\n## Dead money and void years\n\n')
    out.append(table(['Player','Year','Charge','Basis'],[[x['player'],x['year'],dollars(x['amount']),presentation_note(x['basis'],d['current_contract_table'])] for x in d['dead_money']]))
    out.append('The $51,675 old Bray bonus is counted separately from his new $420,000 salary. No recorded deal has void years. The completion research explains the inherited bonus reconciliation.\n\n## Draft class and rookie pool\n\n')
    picks=d['draft_picks']
    if all(x.get('selection') for x in picks):
        out.append(table(['Draft','Round','Original club','Overall','Selection','Selected','Contract'],[[x['year'],x['round'],x['original_club'],draft_slot(x['overall']),x['selection'],display_date(x['selected']),x['contract']] for x in picks]))
        out.append('All nine selections were exercised May 8 to 10 and signed May 11, 2014; no 2014 selection right remains. Each rookie contract is in the position tables above and in its individual sheet, and the gross and net Top-51 effect of the class is in the [cap worksheet]('+page_link(d['start_year'], 'offseason/current_cap_worksheet.md', 1)+'). [The draft record]('+page_link(d['start_year'], 'offseason/draft/draftees.md', 1)+') owns the selections and [the draft ownership record]('+page_link(d['start_year'], 'draft/draft_order.md', 1)+') the picks. Overall numbers include the 32 compensatory picks announced March 24, 2014; Jacksonville received none.\n\n## Decision calendar\n\n')
    else:
        out.append(table(['Draft','Round','Original club','Slot in round','Overall'],[[x['year'],x['round'],x['original_club'],x['slot_in_round'],draft_slot(x['overall'])] for x in picks]))
        out.append('These are selection rights. Add each rookie’s full contract schedule after the actual selection and signing. No future contract dollars are booked against an unselected player. [The draft ownership record]('+page_link(d['start_year'], 'draft/draft_order.md', 1)+') controls the picks.\n\n## Decision calendar\n\n')
    out.append(table(['Date / review','Player or group','Financial treatment'],[
        ['Closed August 30, 2014','Cameron Bradfield (RFA); Toney Clemons, Austin Pasztor and Mike Brown (ERFA)','The four qualifying offers were withdrawn at the reduction to 53 and the players\' rights renounced; the $3,066,000 tender charge leaves. No offer sheet had been received by the May 2 deadline'],
        ['Closed August 30 and 31, 2014','Reduction to 53, waivers and the practice squad','Seventeen players waived and two vested veterans (Cain, C.J. Wilson) released; their surviving bonus allocations are in the dead-money ledger (2014 and 2015). Brate and Jackson on reserve/injured, contracts continuing. Eight practice-squad contracts at the $6,300 weekly minimum, carried as a $107,100 working estimate each for 17 weeks and charged only for weeks on the squad; two places open'],
        ['Closed May 12, 2014','Will Rackley','Traded to Seattle for its unconditional 2015 seventh; his $154,868 final bonus allocation stays as 2014 dead money and his $1,431,000 base leaves. Brewster is kept'],
        ['After the offseason program','Offseason workout charge','The $504,000 opening charge is reconciled to actual workout payments, not charged again'],
        ['2014 season','Hakeem Nicks and Daniel Te’o-Nesheim','Active-game bonuses of $31,250 a game, up to $500,000 each, are counted in the 2014 charges'],
        ['2016 option window','Lane Johnson','2017 fifth-year option remains unexercised; exercise decision follows the 2015 season'],
        ['2017 option window','Aaron Donald and Joel Bitonio','2018 fifth-year options remain unexercised and unbooked; exercise decisions follow the 2016 season']]))
    out.append('## Expiring contracts and free-agent classes\n\n')
    out.append(table(['Last contract year','Players'],[[year,', '.join(p['name'] for p in ps if p['contract_ends']==year and p.get('control')!='traded')] for year in sorted({p['contract_ends'] for p in ps if p['contract_ends'] is not None and p.get('control')!='traded'})]))
    out.append('The last contract year is the final league year of the recorded contract or tender. The 2013 contracts not retained expired when the league year opened on March 11, 2014; those players are no longer with the club. Traded players leave these classes. A player’s class at a later expiry follows his actual accrued service; it does not extend the deal.\n\n## Scheduled cash\n\n')
    out.append(table(['Item']+years,[['Signed contracts and futures']+[dollars(working_total(ps,y,'cash',('known','approximate'))) for y in years],['Unsigned tender, conditional on signing']+[dollars(working_total(ps,y,'cash',('tender',))) for y in years],['Total scheduled player cash']+[dollars(working_total(ps,y,'cash')) for y in years]]))
    out.append('Cash counts salary and bonuses scheduled in that contract year. Bonus proration is not another cash payment. Actual paid cash remains unverified; the 2013–2016 and 2017–2020 cash-floor windows require complete cash ledgers.\n\n## Cap scenarios\n\nNo cap scenario is active. Trade packages, player recommendations and possible replacement contracts are not counted in these totals.\n')
    return ''.join(out)

def render_details(d,years):
    out=[f"# Jacksonville Jaguars individual contract details\n\n[Return to the twelve-year table](jaguars_cap.md). As of {display_date(d['as_of'])}. Whole US dollars.\n\n",
    'Annual cells contain the working original or reconstructed contract schedule. Blank years lie outside that deal. The [completion research](../../library/2014_jaguars_contract_completion.md) identifies adopted simulation terms and guarantee assumptions. Cap, scheduled cash and remaining unpaid guarantees are separate amounts.\n\n']
    for p in d['players']:
        out.append(f"## {p['name']}\n\n")
        if p.get('former_player'):out.append(f"Former player; departure {display_date(p['departure_date'])}. {source_link(departure_source(p,d), 'Departure record')}.\n\n")
        rows=[['Position / status',p['position']+' / '+p['status']],['Original contract',p['contract_type']],['Signed',p['signed']],['Term',p['term']],['Contract value',p['value'] if p['value'] not in {'Unresolved','Unknown'} else '']]
        if p['control'] in {'signed','future','tender'}:
            rows += [['Bonus terms',p['bonus_terms']],['Remaining unpaid salary guarantee',dollars(p['remaining_guarantees']) if p['remaining_guarantees'] is not None else 'Conditional on signing'],['Guarantee basis',p['guarantees']],['Schedule basis',p['schedule_basis']]]
        out.append(table(['Field','Detail'],[[label,presentation_note(value,d['current_contract_table'])] for label,value in rows]))
        rows=[]
        for y in years:
            r=p['years'][y];charge=working_charge(r)
            if charge is None:continue
            other=charge-r['base']-r['proration']
            rows.append([y,dollars(r['base']),dollars(r['proration']),dollars(other),dollars(charge),dollars(r['cash']),dollars(r.get('guaranteed_base',0))])
        if rows:
            out.append('### Annual schedule\n\n'+table(['Year','Base salary','Bonus proration','Other cap','Cap charge','Scheduled cash','Guaranteed base'],rows))
        else:
            out.append('No scheduled player-contract charge in this horizon. Any surviving liability appears separately in the dead-money ledger.\n\n')
        if p['control']=='tender':out.append('The tender is unsigned. Its annual cash is conditional; the full salary guarantee begins if signed.\n\n')
        elif p['control'] in {'pending','retired'}:out.append('No new playing contract is recorded for 2014 or later.\n\n')
        if p['name']=='Lane Johnson':out.append('The 2017 fifth-year option is unexercised and is excluded from committed years. Review the exercise decision in the 2016 option window.\n\n')
        elif p['name']=='Justin Blackmon':out.append('The contract, its deferred bonus cash and the 2016 fifth-year option left with the March 31, 2014 trade to Indianapolis. Only the accelerated bonus allocation stays with Jacksonville, once, in the dead-money ledger.\n\n')
        elif p.get('draft_pick'):out.append('Any future proven-performance escalator requires his actual qualifying participation for Jacksonville.\n\n')
        out.append('### Contract notes\n\n'+presentation_note(p['source_note'],d['current_contract_table']).rstrip('.')+'.\n\n')

        assumptions=list(dict.fromkeys(r['estimate_note'] for r in p['years'].values() if r.get('estimate_note')))
        for note in assumptions:
            if not note.startswith(p['source_note']):out.append(presentation_note(note,d['current_contract_table']).rstrip('.')+'.\n\n')
        out.append('Sources: '+', '.join(source_link(x) for x in dict.fromkeys(p['sources']))+'.\n\n')
    return ''.join(out).rstrip()+'\n'


def organization_staff(root, years, on=None):
    """[(record, contract as it stands on day ``on``, {year: salary})] of every coach whose
    contract schedules salary in the horizon: the head coach first, then by first-year salary and
    name. ``on`` keeps an amendment dated after it off the page (None: every amendment). A coach
    still on a staff by his record whose latest contract there schedules no salary fails, so a
    broken record cannot drop him from the payroll."""
    from runtime import coaches
    rows, missing = [], []
    for record in coaches.load_all(root).values():
        for signed in coaches.entries(record, 'contract_signed'):
            terms = coaches.contract(record, signed['contract'], on)
            salary = {str(y): v for y, v in coaches.scheduled(terms).items() if str(y) in years}
            if salary:
                rows.append((record, terms, salary))
        for hire in coaches.entries(record, 'hired'):
            club = hire.get('club')
            if hire is coaches.hired(record, club) and coaches.employed(record, club):
                terms = coaches.current_contract(record, club, on)
                if terms is None or not coaches.scheduled(terms):
                    missing.append('%s (%s)' % (record.get('name'), club))
    if missing:
        raise ValueError('Coaches on staff without a contract that schedules salary: %s; reconcile the coach '
                         'records' % ', '.join(missing))
    def order(row):
        record, terms, salary = row
        return (terms.get('job') != 'Head coach', -max(salary.values()), record['name'])
    return sorted(rows, key=order)


def organization_guarantee(terms):
    from runtime import coaches
    text = coaches.guarantee_text(terms)
    if not terms.get('offset') or text == 'Not guaranteed':
        return text
    first, _, rest = text.partition(';')
    return first + ', with offset' + (';' + rest if rest else '')


def render_organization(data, years, root):
    """The coaching payroll, read from the coach records (data/people/coaches): every contract
    scheduling salary in the horizon, the payroll by season, the guarantee, the basis of each
    completed term and the contracts ending. The page is dated by its latest contract change,
    never the master date; it shows each contract as it stands on the master date, so an
    amendment dated later never applies (repository validation refuses one, so the page does not
    move with the date alone). Links are written against the page's first home,
    career/finances/, and rebased by render()."""
    import os
    from runtime import coaches
    from runtime.season_layout import STONE_PAGES
    from runtime.events import repository_map
    root = Path(root)
    finances = root / 'career' / 'finances'
    def here(path):
        return os.path.relpath(path, finances).replace(os.sep, '/')
    from runtime.player_bios import master_date
    on = master_date(root)
    staff = organization_staff(root, years, on)
    if not staff:
        raise ValueError('No coach contract schedules salary in the horizon; reconcile the coach records')
    season = int(repository_map(root)['active_season'])
    staff_page = SeasonPaths(season, root).staff_page
    rows, head, assistants, ending, ends = [], {y: 0 for y in years}, {y: 0 for y in years}, {}, {}
    for record, terms, salary in staff:
        rows.append([record['name'], terms.get('job')] + [dollars(salary.get(y)) for y in years]
                    + [organization_guarantee(terms)])
        bucket = head if terms.get('job') == 'Head coach' else assistants
        for y, v in salary.items():
            bucket[y] += v
        ending.setdefault(coaches.through_season(terms), []).append(record['name'])
        ends.setdefault(coaches.through_season(terms), {}).setdefault(
            (terms.get('end') or {}).get('text') or 'Not recorded', []).append(record['name'])
    def money(values):
        return [dollars(v) if v else '' for v in values]
    payroll = [['Head coach'] + money(head.values()), ['Assistant coaches'] + money(assistants.values()),
               ['Total'] + money(head[y] + assistants[y] for y in years)]
    departed = []
    for record in coaches.load_all(root).values():
        for leave in coaches.entries(record, 'departed'):
            terms = coaches.current_contract(record, leave.get('club'), on)
            unpaid = {s: v for s, v in (terms.get('salary') or {}).items() if int(s) > leave['last_season']}
            if any(s in years for s in unpaid):
                departed.append('%s left on %s; his %s salary of %s ended with the move and is not counted.' % (
                    record['name'], coaches.date_text(leave), ' and '.join(sorted(unpaid)),
                    ' and '.join(dollars(v) for _, v in sorted(unpaid.items()))))
    names = {'seasons': 'length', 'end': 'end date', 'salary': 'salary', 'guaranteed': 'guarantee',
             'offset': 'offset', 'dismissal': 'dismissal terms', 'signing_bonus': 'signing bonus', 'options': 'options'}
    def listed(items):
        items = list(items)
        return ', '.join(items[:-1]) + ' and ' + items[-1] if len(items) > 1 else items[0]
    # The completed terms: the head coach's line links his Contract and jobs page; assistants whose
    # contracts were completed the same way, from the same research, share one line that links it.
    completed = {}
    for record, terms, _ in staff:
        groups = coaches.completed(terms)
        if groups:
            head_coach = terms.get('job') == 'Head coach'
            shape = (head_coach, record['name'] if head_coach else None,
                     tuple((source, tuple(keys)) for source, keys in groups), tuple(coaches.completed_sources(terms)))
            completed.setdefault(shape, []).append(record['name'])
    def completed_line(coach_names, groups):
        (source, keys), rest = groups[0], groups[1:]
        if len(coach_names) == 1:
            line = "%s's %s %s completed from %s" % (coach_names[0], listed(names[k] for k in keys),
                                                     'were' if len(keys) > 1 else 'was', source)
            for source, keys in rest:
                line += ', and his %s from %s' % (listed(names[k] for k in keys), source)
        else:
            line = "%s: each contract's %s %s completed from %s" % (
                listed(coach_names), listed(names[k] for k in keys), 'were' if len(keys) > 1 else 'was', source)
            for source, keys in rest:
                line += ', and its %s from %s' % (listed(names[k] for k in keys), source)
        return line + '; the rest is as signed'
    def research_label(path):
        first = next((l for l in (root / path).read_text(encoding='utf-8').split('\n') if l.startswith('# ')),
                     '# ' + Path(path).stem)
        return re.sub(r'^Library:\s*', '', first[2:].strip())
    # The page is dated by the latest contract fact it shows (a signing, an amendment by its
    # in-world date, in force on the master date, or a departure), so it changes only when a
    # coach contract does.
    shown = [e for record, _, _ in staff for e in coaches.entries(record)
             if e['kind'] == 'contract_signed' or (e['kind'] == 'contract_amended'
                                                   and coaches.day(e['in_world']) <= on)]
    shown += [e for record in coaches.load_all(root).values() for e in coaches.entries(record, 'departed')
              if any(str(s) in years for s in (coaches.current_contract(record, e.get('club'), on) or {}).get('salary') or {}
                     if int(s) > e['last_season'])]
    latest = max(shown, key=lambda e: coaches.day(coaches.when(e)))
    out = ('# Coaching payroll\n\n'
           '[Player cap](salary_cap/cap_tracker.md) · [Finances](README.md) · [Coaching staff](' + here(staff_page) + ')\n\n'
           'Current through the latest contract change, ' + coaches.date_text(latest) + '. Whole US dollars.\n\n'
           '## Coaching contracts\n\n' + table(['Coach', 'Job'] + years + ['Guarantee'], rows) +
           '## Payroll by season\n\n' + table(['Measure'] + years, payroll) +
           'Coaching pay is a club expense and never counts against the player salary cap. The assistant total is '
           'scheduled salary, not a hiring budget.\n\n'
           '## Contract terms\n\n')
    assistants_terms = [(record, terms) for record, terms, _ in staff if terms.get('job') != 'Head coach']
    if assistants_terms:
        open_years = [(record['name'], coaches.open_seasons(terms)) for record, terms in assistants_terms
                      if coaches.open_seasons(terms)]
        line = ('Assistant contracts: if the club dismisses a coach without cause, the guaranteed salary for the rest '
                'of his term is still owed. ')
        if not open_years:
            line += 'Every assistant\'s whole term is guaranteed.'
        else:
            line += 'Every assistant\'s salary is guaranteed for his whole term except %s, which %s not.' % (
                listed('%s\'s %s salary' % (name, coaches.years_text(seasons)) for name, seasons in open_years),
                'is' if len(open_years) == 1 and len(open_years[0][1]) == 1 else 'are')
        out += line + '\n\n'
    offsets = sorted({terms['offset'] for _, terms in assistants_terms if terms.get('offset')})
    for text in offsets:
        out += 'Offset: ' + text[:1].lower() + text[1:].rstrip('.') + '.\n\n'
    for line in departed:
        out += line + '\n\n'
    for (head_coach, _, groups, sources), coach_names in completed.items():
        if head_coach:
            links = ['[Contract and jobs](%s)' % here(root / STONE_PAGES / 'Contract_and_Jobs.md')]
        else:
            links = ['[%s](%s)' % (research_label(s), here(root / s)) for s in sources]
        out += '%s%s.\n\n' % (completed_line(coach_names, list(groups)),
                               ' (%s)' % ', '.join(links) if links else '')
    def ends_text(by_text):
        # One end term for the whole row reads alone; different ones name their coaches.
        if len(by_text) == 1:
            return next(iter(by_text))
        return '; '.join('%s (%s)' % (text, ', '.join(who)) for text, who in by_text.items())
    out += '## Contracts ending\n\n' + table(['After the season', 'Coaches', 'Ends'],
                                              [[s, ', '.join(names), ends_text(ends[s])]
                                               for s, names in sorted(ending.items())])
    return out.rstrip() + '\n'

def render(data,root=ROOT):
    from runtime.season_layout import rebase_markdown
    years=validate(data,root)
    outputs = {
        OUTPUT: rebase_markdown(reader_words(render_main(data,years)), 'career/finances/jaguars_cap.md', OUTPUT),
        DETAILS: rebase_markdown(reader_words(render_details(data,years)), 'career/finances/jaguars_contract_details.md',
                                 DETAILS),
        ORGANIZATION: rebase_markdown(render_organization(data,years,root), 'career/finances/organization_finances.md', ORGANIZATION),
    }
    # Focused reading pages come from the same calculated view, never from a
    # second set of editable balances or contract schedules.
    sections = dict(re.findall(r'^## ([^\n]+)\n(.*?)(?=^## |\Z)', outputs[OUTPUT], re.M | re.S))
    pages = {
        'upcoming_decisions/player_decisions.md': ('Player contract decisions',
            ['Decision calendar', 'Expiring contracts and free-agent classes']),
        'future_commitments/commitments.md': ('Future commitments and scheduled cash',
            ['Team cap summary, twelve years', 'Cap by position, twelve years', 'Scheduled cash']),
        'history/dead_money.md': ('Departed contracts and dead money', ['Dead money and void years']),
    }
    for relative, (title, headings) in pages.items():
        target = Path('career/finances') / relative
        content = f'# {title}\n\n[Finances](../README.md) · [Full cap table](../salary_cap/cap_tracker.md)\n\n'
        content += f"As of {display_date(data['as_of'])}.\n\n"
        for heading in headings:
            content += rebase_markdown('## '+heading+'\n'+sections[heading], OUTPUT, target)
        outputs[target] = content.rstrip()+'\n'
    return outputs

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    data=json.loads((ROOT/INPUT).read_text())
    try: outputs=render(data)
    except (ValueError,KeyError,TypeError) as e: print('INVALID CAP TRACKER: '+str(e));return 1
    stale=[]
    for path,content in outputs.items():
        if args.check:
            if not (ROOT/path).exists() or (ROOT/path).read_text()!=content:stale.append(str(path))
        else:
            (ROOT/path).parent.mkdir(parents=True, exist_ok=True)
            (ROOT/path).write_text(content)
    if stale:print('STALE: '+', '.join(stale));return 1
    print(('PASS: ' if args.check else 'WROTE: ')+str(len(data['players']))+'-player source reconciliation and twelve-year cap/detail views')
    return 0

if __name__=='__main__':sys.exit(main())
