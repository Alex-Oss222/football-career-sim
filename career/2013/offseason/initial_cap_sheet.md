# Jacksonville Jaguars — Initial 2013 Cap and Contract Sheet

**Accounting date:** January 15, 2013  
**League-year distinction:** the 2013 league year and its $123,000,000 cap do not begin until March 12, 2013 at 4:00 p.m. ET.  
**Status:** `PARTIALLY RECONCILED — EXACT CLUB LEDGER NOT SOURCEABLE; NO FALSE PRECISION USED`

## Sources and evidence boundary

- **Primary roster spine:** NFLverse's archived NFL weekly-roster export, `roster_weekly_2012.csv`, filtered to Jacksonville, regular-season Week 17, status `ACT`. The source preserves NFL identifiers, listed position, jersey and experience. [NFLverse weekly-rosters release](https://github.com/nflverse/nflverse-data/releases/tag/weekly_rosters)
- **Independent roster/role check:** Pro Football Reference's 2012 Jacksonville roster table as redistributed without alteration in NFLverse's `pfr_rosters.csv`; games and starts below are real 2012 facts, not evaluations. [NFLverse miscellaneous-data release](https://github.com/nflverse/nflverse-data/releases/tag/misc) and [PFR 2012 Jaguars roster](https://www.pro-football-reference.com/teams/jax/2012_roster.htm)
- **Contract cross-check:** OverTheCap historical-contract export, used only for contract totals that can be matched unambiguously. [NFLverse contracts release](https://github.com/nflverse/nflverse-data/releases/tag/contracts)
- **Rules:** the $123,000,000 league cap and 2013 roster/accounting rules are already independently sourced in `foundation/02_League_Era_and_Sourcebook.md` §11 and `library/2013_league_calendar_and_financial_rules.md`.

**Cutoff:** January 15, 2013, the counterfactual Stone hire date. The final 2012 active roster is the last clean NFL roster snapshot available in the archived weekly feed. Reserve/injured designations are separately labeled because the export does not retain every reserve-list player in its Week 17 active slice. No actual transaction, release, re-signing, draft choice, staff hire, or player outcome after the divergence point was imported.

## Two-pass verification record

### Pass 1 — research

The OverTheCap historical-contract export was matched against the roster inventory for signed year, stated term, total value and total guarantee. The league ceiling and accounting rules came from the already verified project sourcebook.

### Pass 2 — skeptical re-check

Contract matches were re-checked against player identity, signing year and nominal term. The export does not provide annual base salaries, bonus-proration schedules, individual 2013 cap charges, release offsets, or a January 15 club ledger. Therefore this sheet does not reverse-engineer them from total value, does not divide guarantees evenly, and does not present a made-up cap-space total. Every unavailable field is marked unknown. This is a deliberate validation stop, not an estimate.

## Governing 2013 controls

| Control | Verified value | Treatment |
|---|---:|---|
| 2013 team salary cap | $123,000,000 | Confirmed in Document 2 §11 |
| 2013 league-year start | March 12, 2013, 4:00 p.m. ET | January 15 is still in the 2012 league year |
| Signing-bonus proration | Straight line, maximum four years | Apply only when actual bonus amount and contract years are known |
| Standard termination acceleration | Remaining unamortized signing bonus accelerates | Release calculation requires the actual ledger |
| Post-June 1 designations | Up to two per league year | Not assumed used |
| Team cash minimum | 89% of aggregate caps over 2013–2016 | Not a single-season cap floor |

## Verified contract summaries

These totals are useful obligations, but **not substitutes for annual cap accounting**. Dollar amounts reproduce the historical-contract export.

| Player | Pos. | Signed | Nominal term | Total value | Total guarantee | 2013 base | 2013 bonus/proration | 2013 cap charge | Verification |
|---|---:|---:|---:|---:|---:|---|---|---|---|
| Andre Branch | ED | 2012 | 4 years | $5,089,934 | $3,153,129 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| Blaine Gabbert | QB | 2011 | 4 years | $12,001,646 | $12,001,646 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| Brandon Marshall | LB | 2012 | 4 years | $2,300,500 | $200,500 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| Bryan Anger | P | 2012 | 4 years | $2,877,166 | $662,500 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| C.J. Mosley | IDL | 2012 | 3 years | $7,500,000 | $1,000,000 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| Cecil Shorts | WR | 2011 | 4 years | $2,672,146 | $443,380 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| Chad Henne | QB | 2012 | 2 years | $6,750,000 | $4,075,000 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| Chris Prosinski | S | 2011 | 4 years | $2,640,144 | $420,108 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| Dwight Lowery | S | 2012 | 4 years | $13,600,000 | $4,000,000 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| Eugene Monroe | LT | 2009 | 5 years | $25,000,000 | $19,020,000 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| Jason Babin | ED | 2011 | 5 years | $28,325,000 | $5,500,000 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| Jeremy Mincey | ED | 2012 | 4 years | $20,000,000 | $9,000,000 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| Jeris Pendleton | IDL | 2012 | 4 years | $2,151,392 | $51,392 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| Justin Blackmon | WR | 2012 | 4 years | $18,512,010 | $18,512,010 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| Marcedes Lewis | TE | 2011 | 5 years | $34,000,000 | $17,000,000 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| Maurice Jones-Drew | RB | 2009 | 4 years | $30,515,000 | $9,000,000 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| Mike Harris | CB | 2012 | 4 years | $2,215,788 | $115,788 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| Paul Posluszny | LB | 2011 | 6 years | $45,000,000 | $15,000,000 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| Russell Allen | LB | 2012 | 3 years | $6,000,000 | $2,600,000 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| Tyson Alualu | ED | 2010 | 5 years | $21,399,000 | $17,510,000 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| Uche Nwaneri | RG | 2010 | 5 years | $24,000,000 | $8,600,000 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| Will Rackley | LG | 2011 | 4 years | $2,914,274 | $619,472 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |

## Complete roster contract-control ledger

| Player | Contract-control finding at snapshot | 2013 financial fields |
|---|---|---|
| Blaine Gabbert | Verified 2011 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Chad Henne | Verified 2012 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jordan Palmer | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jalen Parmele | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jonathan Grimes | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Keith Toston | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Maurice Jones-Drew | Verified 2009 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Richard Murphy | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Greg Jones | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Montell Owens | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Cecil Shorts | Verified 2011 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jerrell Jackson | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jordan Shipley | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Justin Blackmon | Verified 2012 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Laurent Robinson | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Mike Brown | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Toney Clemons | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Allen Reisner | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Isaiah Stanback | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Marcedes Lewis | Verified 2011 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Zach Potter | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Cameron Bradfield | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Eugene Monroe | Verified 2009 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Guy Whimper | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Austin Pasztor | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Eben Britton | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Mark Asper | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Uche Nwaneri | Verified 2010 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Will Rackley | Verified 2011 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Brad Meester | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Mike Brewster | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Steve Vallos | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Andre Branch | Verified 2012 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Austen Lane | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| George Selvie | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jason Babin | Verified 2011 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jeremy Mincey | Verified 2012 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| John Chick | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| C.J. Mosley | Verified 2012 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| D'Anthony Smith | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jeris Pendleton | Verified 2012 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jerome Long | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Terrance Knighton | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Tyson Alualu | Verified 2010 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Kyle Bosworth | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Paul Posluszny | Verified 2011 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Brandon Marshall | Verified 2012 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Daryl Smith | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Julian Stanford | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Russell Allen | Verified 2012 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Aaron Ross | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Antwaun Molden | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Derek Cox | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Kevin Rutland | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Mike Harris | Verified 2012 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Rashean Mathis | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Chris Prosinski | Verified 2011 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Antwon Blake | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Dawan Landry | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Dwight Lowery | Verified 2012 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Josh Scobee | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Bryan Anger | Verified 2012 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jeremy Cain | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |

## Team reconciliation

| Item | Amount/status | Validation result |
|---|---|---|
| Gross 2013 cap commitments | **Unknown** | Do not sum absent individual cap charges |
| Dead money as of January 15 | **Unknown** | No dated club ledger available |
| Top-51 adjustment | **Not yet applicable to a validated calculation** | Requires complete offseason contracts |
| Rookie pool/set-aside | **Not yet fixed in this snapshot** | Draft contracts do not exist on January 15 |
| Carryover/other adjustments | **Unknown** | Requires league notice/club ledger |
| Adjusted team cap | **Unknown** | $123,000,000 league ceiling alone is not the adjusted club cap |
| Remaining cap space | **Not calculated** | Any precise figure would be fabricated |

### Financial decision gate

No signing, release, restructuring or trade may be represented as cap-legal from this sheet alone. Before the first transaction, obtain a dated club ledger or a source containing every 2013 cap charge, dead-money item, carryover and adjustment; then reconcile the sum to the reported club total.
