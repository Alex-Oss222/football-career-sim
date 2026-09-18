# Jacksonville Jaguars — Initial 2013 Cap and Contract Sheet

**Accounting date:** January 15, 2013  
**League-year distinction:** the 2013 league year and its $123,000,000 cap do not begin until March 12, 2013 at 4:00 p.m. ET.  
**Status:** `PARTIALLY RECONCILED — 11 ARCHIVED OVERTHECAP 2013 PLAYER ROWS CONFIRMED; REMAINING PLAYER ROWS AND CLUB ADJUSTMENTS UNCONFIRMED`

## Sources and evidence boundary

- **Primary roster spine:** NFLverse's archived NFL weekly-roster export, `roster_weekly_2012.csv`, filtered to Jacksonville, regular-season Week 17, status `ACT`. The source preserves NFL identifiers, listed position, jersey and experience. [NFLverse weekly-rosters release](https://github.com/nflverse/nflverse-data/releases/tag/weekly_rosters)
- **Independent roster/role check:** Pro Football Reference's 2012 Jacksonville roster table as redistributed without alteration in NFLverse's `pfr_rosters.csv`; games and starts below are real 2012 facts, not evaluations. [NFLverse miscellaneous-data release](https://github.com/nflverse/nflverse-data/releases/tag/misc) and [PFR 2012 Jaguars roster](https://www.pro-football-reference.com/teams/jax/2012_roster.htm)
- **Archived annual cap rows:** OverTheCap’s 2013 `cap.php` player pages, preserved by the Internet Archive, supply the confirmed Base Salary, Prorated Bonus, other bonus, Cap Number and Dead Money fields below. The discovery query is preserved here so each accepted row remains auditable: [Internet Archive CDX query for archived Jaguars cap pages](http://web.archive.org/cdx/search/cdx?url=overthecap.com/cap.php*&filter=urlkey:.*jaguars.*&from=20130101&to=20130601&output=text&limit=200).
- **Contract-page index:** NFLverse’s OverTheCap-derived historical-contract export supplies each matched player’s current OverTheCap player-page URL and the already-recorded contract summary. [NFLverse contracts release](https://github.com/nflverse/nflverse-data/releases/tag/contracts)
- **Independent annual-cash check:** the public `haleykahn14/NFL-Salary-Cap` workbook, described by its maintainer as Spotrac-derived, was queried only for pre-existing Jacksonville contracts and only for its 2013 `salary` field. It is not treated as a cap ledger: its bonus columns are cash-payment fields, not annual cap proration. [Source workbook](https://github.com/haleykahn14/NFL-Salary-Cap/blob/main/merged_salaries_2013_2022_cleaned.xlsx)
- **Rules:** the $123,000,000 league cap and 2013 roster/accounting rules are already independently sourced in `foundation/02_League_Era_and_Sourcebook.md` §11 and `library/2013_league_calendar_and_financial_rules.md`.

**Cutoff:** January 15, 2013, the counterfactual Stone hire date. The final 2012 active roster is the last clean NFL roster snapshot available in the archived weekly feed. Reserve/injured designations are separately labeled because the export does not retain every reserve-list player in its Week 17 active slice. No actual transaction, release, re-signing, draft choice, staff hire, or player outcome after the divergence point was imported.

## Two-pass verification record

### Pass 1 — research

The OverTheCap historical-contract export was first matched against the roster inventory for player identity, signed year, nominal term, total value, total guarantee and player-page URL. The Spotrac-derived annual-cash workbook independently supplied the base-salary subset without treating cash bonuses as cap proration.

### Pass 2 — skeptical re-check

A separate archival pass located OverTheCap's contemporary `cap.php` pages through the Internet Archive CDX index and read the 2013 annual rows. Eleven rows are now accepted because the archived Base Salary agrees with the independent annual-cash source wherever that source contains the player, while the archived page supplies the distinct proration, other-bonus, Cap Number and Dead Money fields. The archived figures are transcribed rather than recomputed from contract totals. Rows not recovered from a Jacksonville-specific archived page remain expressly unconfirmed; a later-team page is not substituted for a Jacksonville obligation.

## Governing 2013 controls

| Control | Verified value | Treatment |
|---|---:|---|
| 2013 team salary cap | $123,000,000 | Confirmed in Document 2 §11 |
| 2013 league-year start | March 12, 2013, 4:00 p.m. ET | January 15 is still in the 2012 league year |
| Signing-bonus proration | Straight line, maximum four years | Apply only when actual bonus amount and contract years are known |
| Standard termination acceleration | Remaining unamortized signing bonus accelerates | Release calculation requires the actual ledger |
| Post-June 1 designations | Up to two per league year | Not assumed used |
| Team cash minimum | 89% of aggregate caps over 2013–2016 | Not a single-season cap floor |

## Verified contract summaries and archived 2013 cap rows

Contract totals remain useful context, but the annual accounting columns are populated only where the contemporary archived OverTheCap page was recovered. “Other bonus” identifies the archived row's roster/workout amounts; an em dash means the archived row showed none.

| Player | Pos. | Signed | Nominal term | Total value | Total guarantee | 2013 base | Prorated bonus | Other bonus | 2013 cap number | Dead money | Verification |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| [Andre Branch](https://overthecap.com/player/andre-branch/909/) | ED | 2012 | 4 years | $5,089,934 | $3,153,129 | $621,361 | Unknown | Unknown | Unknown | Unknown | Contract/base confirmed; Jacksonville archive row not yet recovered |
| [Blaine Gabbert](https://overthecap.com/player/blaine-gabbert/913/) | QB | 2011 | 4 years | $12,001,646 | $12,001,646 | $1,466,058 | $1,807,118 | — | $3,273,176 | $7,091,881 | Archived OverTheCap 2013 row confirmed |
| Brandon Marshall | LB | 2012 | 4 years | $2,300,500 | $200,500 | Unknown | Unknown | Unknown | Unknown | Unknown | Contract confirmed; Jacksonville archive row not yet recovered |
| [Bryan Anger](https://overthecap.com/player/bryan-anger/917/) | P | 2012 | 4 years | $2,877,166 | $662,500 | $509,913 | Unknown | Unknown | Unknown | Unknown | Contract/base confirmed; Jacksonville archive row not yet recovered |
| [C.J. Mosley](https://overthecap.com/player/c-j-mosley/819/) | IDL | 2012 | 3 years | $7,500,000 | $1,000,000 | Unknown | Unknown | Unknown | Unknown | Unknown | Contract confirmed; Jacksonville archive row not yet recovered |
| [Cecil Shorts](https://overthecap.com/player/cecil-shorts/919/) | WR | 2011 | 4 years | $2,672,146 | $443,380 | $617,922 | Unknown | Unknown | Unknown | Unknown | Contract/base confirmed; Jacksonville archive row not yet recovered |
| [Chad Henne](https://overthecap.com/player/chad-henne/920/) | QB | 2012 | 2 years | $6,750,000 | $4,075,000 | $2,625,000 | Unknown | Unknown | Unknown | Unknown | Contract/base confirmed; Jacksonville archive row not yet recovered |
| [Chris Prosinski](https://overthecap.com/player/chris-prosinski/921/) | S | 2011 | 4 years | $2,640,144 | $420,108 | $615,012 | Unknown | Unknown | Unknown | Unknown | Contract/base confirmed; Jacksonville archive row not yet recovered |
| Dwight Lowery | S | 2012 | 4 years | $13,600,000 | $4,000,000 | $3,100,000 | $750,000 | $25,000 workout | $3,875,000 | $2,250,000 | Archived OverTheCap 2013 row confirmed |
| [Eugene Monroe](https://overthecap.com/player/eugene-monroe/927/) | LT | 2009 | 5 years | $25,000,000 | $19,020,000 | $3,800,000 | $1,742,500 | $205,000 workout | $5,747,500 | $3,140,000 | Archived OverTheCap 2013 row confirmed |
| [Jason Babin](https://overthecap.com/player/jason-babin/931/) | ED | 2011 | 5 years | $28,325,000 | $5,500,000 | $4,225,000 | Unknown | Unknown | Unknown | Unknown | Contract/base confirmed; Jacksonville archive row not yet recovered |
| [Jeremy Mincey](https://overthecap.com/player/jeremy-mincey/934/) | ED | 2012 | 4 years | $20,000,000 | $9,000,000 | $1,525,000 | $2,000,000 | $25,000 workout | $3,550,000 | $6,000,000 | Archived OverTheCap 2013 row confirmed |
| [Jeris Pendleton](https://overthecap.com/player/jeris-pendleton/2662/) | IDL | 2012 | 4 years | $2,151,392 | $51,392 | Unknown | Unknown | Unknown | Unknown | Unknown | Contract confirmed; Jacksonville archive row not yet recovered |
| [Justin Blackmon](https://overthecap.com/player/justin-blackmon/943/) | WR | 2012 | 4 years | $18,512,010 | $18,512,010 | $1,231,455 | $2,975,818 | — | $4,207,273 | $15,146,184 | Archived OverTheCap 2013 row confirmed |
| [Marcedes Lewis](https://overthecap.com/player/marcedes-lewis/946/) | TE | 2011 | 5 years | $34,000,000 | $17,000,000 | $4,200,000 | $1,400,000 | $150,000 workout | $5,750,000 | $4,200,000 | Archived OverTheCap 2013 row confirmed |
| [Maurice Jones-Drew](https://overthecap.com/player/maurice-jones-drew/949/) | RB | 2009 | 4 years | $30,515,000 | $9,000,000 | $4,950,000 | $1,800,000 | $50,000 workout | $6,800,000 | $1,800,000 | Archived OverTheCap 2013 row confirmed |
| Mike Harris | CB | 2012 | 4 years | $2,215,788 | $115,788 | $480,000 | Unknown | Unknown | Unknown | Unknown | Contract/base confirmed; Jacksonville archive row not yet recovered |
| [Paul Posluszny](https://overthecap.com/player/paul-posluszny/954/) | LB | 2011 | 6 years | $45,000,000 | $15,000,000 | $6,450,000 | $2,000,000 | $50,000 workout | $8,500,000 | $6,000,000 | Archived OverTheCap 2013 row confirmed |
| Russell Allen | LB | 2012 | 3 years | $6,000,000 | $2,600,000 | $1,375,000 | Unknown | Unknown | Unknown | Unknown | Contract/base confirmed; Jacksonville archive row not yet recovered |
| [Tyson Alualu](https://overthecap.com/player/tyson-alualu/960/) | ED | 2010 | 5 years | $21,399,000 | $17,510,000 | $1,922,500 | $1,542,500 | $150,000 workout | $3,615,000 | $4,627,500 | Archived OverTheCap 2013 row confirmed |
| [Uche Nwaneri](https://overthecap.com/player/uche-nwaneri/961/) | RG | 2010 | 5 years | $24,000,000 | $8,600,000 | $3,775,000 | $1,094,500 | $1,000,000 roster + $25,000 workout | $5,894,500 | $3,283,500 | Archived OverTheCap 2013 row confirmed |
| [Will Rackley](https://overthecap.com/player/will-rackley/962/) | LG | 2011 | 4 years | $2,914,274 | $619,472 | $639,934 | $154,868 | — | $794,802 | $309,736 | Archived OverTheCap 2013 row confirmed |

**Confirmed-player subtotal:** the eleven recovered 2013 Cap Number fields total **$52,007,251**. This is a strict subtotal, not a club cap charge: it deliberately excludes every unrecovered player row, existing dead-money line, and club adjustment.

## Complete roster contract-control ledger

| Player | Contract-control finding at snapshot | 2013 financial fields |
|---|---|---|
| Blaine Gabbert | Verified 2011 contract summary above | Archived 2013 row confirmed; see table above |
| Chad Henne | Verified 2012 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jordan Palmer | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jalen Parmele | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jonathan Grimes | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Keith Toston | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Maurice Jones-Drew | Verified 2009 contract summary above | Archived 2013 row confirmed; see table above |
| Richard Murphy | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Greg Jones | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Montell Owens | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Cecil Shorts | Verified 2011 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jerrell Jackson | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jordan Shipley | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Justin Blackmon | Verified 2012 contract summary above | Archived 2013 row confirmed; see table above |
| Laurent Robinson | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Mike Brown | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Toney Clemons | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Allen Reisner | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Isaiah Stanback | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Marcedes Lewis | Verified 2011 contract summary above | Archived 2013 row confirmed; see table above |
| Zach Potter | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Cameron Bradfield | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Eugene Monroe | Verified 2009 contract summary above | Archived 2013 row confirmed; see table above |
| Guy Whimper | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Austin Pasztor | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Eben Britton | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Mark Asper | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Uche Nwaneri | Verified 2010 contract summary above | Archived 2013 row confirmed; see table above |
| Will Rackley | Verified 2011 contract summary above | Archived 2013 row confirmed; see table above |
| Brad Meester | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Mike Brewster | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Steve Vallos | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Andre Branch | Verified 2012 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Austen Lane | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| George Selvie | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jason Babin | Verified 2011 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jeremy Mincey | Verified 2012 contract summary above | Archived 2013 row confirmed; see table above |
| John Chick | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| C.J. Mosley | Verified 2012 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| D'Anthony Smith | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jeris Pendleton | Verified 2012 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jerome Long | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Terrance Knighton | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Tyson Alualu | Verified 2010 contract summary above | Archived 2013 row confirmed; see table above |
| Kyle Bosworth | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Paul Posluszny | Verified 2011 contract summary above | Archived 2013 row confirmed; see table above |
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
| Dwight Lowery | Verified 2012 contract summary above | Archived 2013 row confirmed; see table above |
| Josh Scobee | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Bryan Anger | Verified 2012 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jeremy Cain | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |

## Team reconciliation

| Item | Amount/status | Validation result |
|---|---|---|
| Confirmed-player gross 2013 cap commitments | **$52,007,251** | Exact sum of the eleven archived OverTheCap Cap Number fields above |
| Remaining player commitments | **Unconfirmed bounded residual** | The unrecovered rows are listed rather than silently omitted. Most remaining roster/bench contracts are at or near applicable minimum salaries; only the 51 highest cap numbers count during the offseason, so a raw all-player sum would not equal the offseason club charge. No unsupported dollar estimate is assigned. |
| Dead money as of January 15 | **Unknown** | Player-page Dead Money is a release consequence, not proof of already-booked club dead money; a dated club ledger remains necessary |
| Top-51 adjustment | **Not computable from recovered subset** | Requires all contracts competing for the 51 highest cap numbers |
| Rookie pool/set-aside | **Not yet fixed in this snapshot** | Draft contracts do not exist on January 15 |
| Carryover/other adjustments | **Unknown** | Requires the league notice or a dated club ledger |
| Adjusted team cap | **Unknown** | The $123,000,000 league ceiling is confirmed, but Jacksonville carryover and other adjustments are not |
| Remaining cap space | **Unknown** | Cannot be derived honestly from an eleven-player subtotal, and no independently confirmed dated top-down Jacksonville figure has been located |

### Departed-player / release-math audit

The archival team-tag problem is material for **Guy Whimper, Aaron Ross, Dawan Landry and Laurent Robinson**: later 2013 OverTheCap captures are attached to their Steelers, Giants or Jets pages (or otherwise reflect a later contract), not Jacksonville’s pre-release ledger. Those later-team rows are rejected as evidence of Jacksonville release cost. Earlier Jacksonville-specific pages or contemporaneous reporting sufficient to reconstruct all required unamortized bonus fields have not been confirmed, so this sheet records **release cap charge, dead money and savings as unknown** for all four rather than importing their new-team contracts. This is the only defensible release decision output from the present evidence.

### Financial decision gate

The sheet can now support a **$52,007,251 confirmed-player minimum commitment** and player-specific scenario work for the eleven recovered contracts. It still cannot certify a signing, release, restructuring or trade as cap-legal: the unrecovered player residual, Jacksonville’s already-booked dead money, top-51 ordering, carryover and other club adjustments remain unresolved. In particular, no Whimper/Ross/Landry/Robinson release savings may be credited until a Jacksonville-specific pre-release source establishes that player’s actual 2013 cap number and remaining proration. The gate clears only after those ledger inputs and a real adjusted-team-cap figure are sourced; it must not be cleared by subtracting the confirmed subtotal from $123,000,000.
