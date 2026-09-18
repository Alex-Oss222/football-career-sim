# Jacksonville Jaguars — Initial 2013 Cap and Contract Sheet

**Accounting date:** January 15, 2013  
**League-year distinction:** the 2013 league year and its $123,000,000 cap do not begin until March 12, 2013 at 4:00 p.m. ET.  
**Status:** `PARTIALLY RECONCILED — 2013 BASE-SALARY PASS ADDED; BONUS PRORATION AND GROSS CLUB LEDGER STILL UNSOURCEABLE`

## Sources and evidence boundary

- **Primary roster spine:** NFLverse's archived NFL weekly-roster export, `roster_weekly_2012.csv`, filtered to Jacksonville, regular-season Week 17, status `ACT`. The source preserves NFL identifiers, listed position, jersey and experience. [NFLverse weekly-rosters release](https://github.com/nflverse/nflverse-data/releases/tag/weekly_rosters)
- **Independent roster/role check:** Pro Football Reference's 2012 Jacksonville roster table as redistributed without alteration in NFLverse's `pfr_rosters.csv`; games and starts below are real 2012 facts, not evaluations. [NFLverse miscellaneous-data release](https://github.com/nflverse/nflverse-data/releases/tag/misc) and [PFR 2012 Jaguars roster](https://www.pro-football-reference.com/teams/jax/2012_roster.htm)
- **Contract-page index:** NFLverse’s OverTheCap-derived historical-contract export supplies each matched player’s exact OverTheCap player-page URL as well as the already-recorded contract summary. [NFLverse contracts release](https://github.com/nflverse/nflverse-data/releases/tag/contracts)
- **Independent annual-cash check:** the public `haleykahn14/NFL-Salary-Cap` workbook, described by its maintainer as Spotrac-derived, was queried only for pre-existing Jacksonville contracts and only for its 2013 `salary` field. It is not treated as a cap ledger: its bonus columns are cash-payment fields, not annual cap proration. [Source workbook](https://github.com/haleykahn14/NFL-Salary-Cap/blob/main/merged_salaries_2013_2022_cleaned.xlsx)
- **Rules:** the $123,000,000 league cap and 2013 roster/accounting rules are already independently sourced in `foundation/02_League_Era_and_Sourcebook.md` §11 and `library/2013_league_calendar_and_financial_rules.md`.

**Cutoff:** January 15, 2013, the counterfactual Stone hire date. The final 2012 active roster is the last clean NFL roster snapshot available in the archived weekly feed. Reserve/injured designations are separately labeled because the export does not retain every reserve-list player in its Week 17 active slice. No actual transaction, release, re-signing, draft choice, staff hire, or player outcome after the divergence point was imported.

## Two-pass verification record

### Pass 1 — research

The OverTheCap historical-contract export was matched against the roster inventory for signed year, stated term, total value, total guarantee and exact player-page URL. A separate Spotrac-derived annual-cash workbook was then filtered to 2013 Jacksonville rows. Where that independent source carries a plausible base salary under a contract already in force at the January 15 cutoff, that base is now recorded below. No bonus cash field was relabeled as cap proration.

### Pass 2 — skeptical re-check

Contract matches and URLs were re-checked against player identity, signing year and nominal term. The independently collected annual file confirms 2013 base salary for 14 of the contracts below, but does not contain cap-proration schedules or January 15 club adjustments. Direct retrieval of the historical OverTheCap page tables and a genuinely independent second cap source did not succeed in this environment. Accordingly, the sheet records the verified base subset, leaves every unconfirmed proration/cap charge unknown, and still refuses to compute a false gross commitment or cap-space figure. This is a deliberate validation stop, not an estimate.

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
| [Andre Branch](https://overthecap.com/player/andre-branch/909/) | ED | 2012 | 4 years | $5,089,934 | $3,153,129 | $621,361 | Unknown in available export | Unknown in available export | Base independently confirmed; proration/cap charge unavailable |
| [Blaine Gabbert](https://overthecap.com/player/blaine-gabbert/913/) | QB | 2011 | 4 years | $12,001,646 | $12,001,646 | $1,466,058 | Unknown in available export | Unknown in available export | Base independently confirmed; proration/cap charge unavailable |
| Brandon Marshall | LB | 2012 | 4 years | $2,300,500 | $200,500 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| [Bryan Anger](https://overthecap.com/player/bryan-anger/917/) | P | 2012 | 4 years | $2,877,166 | $662,500 | $509,913 | Unknown in available export | Unknown in available export | Base independently confirmed; proration/cap charge unavailable |
| [C.J. Mosley](https://overthecap.com/player/c-j-mosley/819/) | IDL | 2012 | 3 years | $7,500,000 | $1,000,000 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| [Cecil Shorts](https://overthecap.com/player/cecil-shorts/919/) | WR | 2011 | 4 years | $2,672,146 | $443,380 | $617,922 | Unknown in available export | Unknown in available export | Base independently confirmed; proration/cap charge unavailable |
| [Chad Henne](https://overthecap.com/player/chad-henne/920/) | QB | 2012 | 2 years | $6,750,000 | $4,075,000 | $2,625,000 | Unknown in available export | Unknown in available export | Base independently confirmed; proration/cap charge unavailable |
| [Chris Prosinski](https://overthecap.com/player/chris-prosinski/921/) | S | 2011 | 4 years | $2,640,144 | $420,108 | $615,012 | Unknown in available export | Unknown in available export | Base independently confirmed; proration/cap charge unavailable |
| Dwight Lowery | S | 2012 | 4 years | $13,600,000 | $4,000,000 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| [Eugene Monroe](https://overthecap.com/player/eugene-monroe/927/) | LT | 2009 | 5 years | $25,000,000 | $19,020,000 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| [Jason Babin](https://overthecap.com/player/jason-babin/931/) | ED | 2011 | 5 years | $28,325,000 | $5,500,000 | $4,225,000 | Unknown in available export | Unknown in available export | Base independently confirmed; proration/cap charge unavailable |
| [Jeremy Mincey](https://overthecap.com/player/jeremy-mincey/934/) | ED | 2012 | 4 years | $20,000,000 | $9,000,000 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| [Jeris Pendleton](https://overthecap.com/player/jeris-pendleton/2662/) | IDL | 2012 | 4 years | $2,151,392 | $51,392 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| [Justin Blackmon](https://overthecap.com/player/justin-blackmon/943/) | WR | 2012 | 4 years | $18,512,010 | $18,512,010 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| [Marcedes Lewis](https://overthecap.com/player/marcedes-lewis/946/) | TE | 2011 | 5 years | $34,000,000 | $17,000,000 | $4,200,000 | Unknown in available export | Unknown in available export | Base independently confirmed; proration/cap charge unavailable |
| [Maurice Jones-Drew](https://overthecap.com/player/maurice-jones-drew/949/) | RB | 2009 | 4 years | $30,515,000 | $9,000,000 | $4,950,000 | Unknown in available export | Unknown in available export | Base independently confirmed; proration/cap charge unavailable |
| Mike Harris | CB | 2012 | 4 years | $2,215,788 | $115,788 | $480,000 | Unknown in available export | Unknown in available export | Base independently confirmed; proration/cap charge unavailable |
| [Paul Posluszny](https://overthecap.com/player/paul-posluszny/954/) | LB | 2011 | 6 years | $45,000,000 | $15,000,000 | $6,450,000 | Unknown in available export | Unknown in available export | Base independently confirmed; proration/cap charge unavailable |
| Russell Allen | LB | 2012 | 3 years | $6,000,000 | $2,600,000 | $1,375,000 | Unknown in available export | Unknown in available export | Base independently confirmed; proration/cap charge unavailable |
| [Tyson Alualu](https://overthecap.com/player/tyson-alualu/960/) | ED | 2010 | 5 years | $21,399,000 | $17,510,000 | $1,922,500 | Unknown in available export | Unknown in available export | Base independently confirmed; proration/cap charge unavailable |
| [Uche Nwaneri](https://overthecap.com/player/uche-nwaneri/961/) | RG | 2010 | 5 years | $24,000,000 | $8,600,000 | Unknown in available export | Unknown in available export | Unknown in available export | Confirmed summary; annual ledger unavailable |
| [Will Rackley](https://overthecap.com/player/will-rackley/962/) | LG | 2011 | 4 years | $2,914,274 | $619,472 | $639,934 | Unknown in available export | Unknown in available export | Base independently confirmed; proration/cap charge unavailable |

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
