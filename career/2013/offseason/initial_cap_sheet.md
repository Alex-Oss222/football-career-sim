# Jacksonville Jaguars — Initial 2013 Cap and Contract Sheet

**Accounting date:** January 15, 2013  
**League-year distinction:** the 2013 league year and its $123,000,000 cap do not begin until March 12, 2013 at 4:00 p.m. ET.  
**Status:** `DECISION-USABLE INITIALIZATION BASELINE — 20 EXACT 2013 PLAYER CAP ROWS; JANUARY CLUB-ROOM ESTIMATE ESTABLISHED; FULL TOP-51 LEDGER STILL OPEN`

## Sources and evidence boundary

- **Primary roster spine:** NFLverse's archived NFL weekly-roster export, `roster_weekly_2012.csv`, filtered to Jacksonville, regular-season Week 17, status `ACT`. The source preserves NFL identifiers, listed position, jersey and experience. [NFLverse weekly-rosters release](https://github.com/nflverse/nflverse-data/releases/tag/weekly_rosters)
- **Independent roster/role check:** Pro Football Reference's 2012 Jacksonville roster table as redistributed without alteration in NFLverse's `pfr_rosters.csv`; games and starts below are real 2012 facts, not evaluations. [NFLverse miscellaneous-data release](https://github.com/nflverse/nflverse-data/releases/tag/misc) and [PFR 2012 Jaguars roster](https://www.pro-football-reference.com/teams/jax/2012_roster.htm)
- **Archived annual cap rows:** OverTheCap’s 2013 `cap.php` player pages, preserved by the Internet Archive, supply eleven contemporary Jacksonville Base Salary, Prorated Bonus, other bonus, Cap Number and Dead Money rows. The discovery query is preserved here so each accepted row remains auditable: [Internet Archive CDX query for archived Jaguars cap pages](http://web.archive.org/cdx/search/cdx?url=overthecap.com/cap.php*&filter=urlkey:.*jaguars.*&from=20130101&to=20130601&output=text&limit=200).
- **Current OverTheCap historical season rows:** where a player’s current OverTheCap history still preserves an unambiguous 2013 Jaguars row, that row may be used to fill annual base/proration/bonus/cap fields. This adds exact 2013 rows for Chad Henne, Jason Babin, Russell Allen, Josh Scobee, Andre Branch, Cecil Shorts, Bryan Anger, Chris Prosinski and Mike Harris. These are historical contract-accounting records, not later-career evaluation evidence.
- **Top-down January planning estimate:** a January 9, 2013 report citing ESPN’s John Clayton put Jacksonville’s carryover at about **$19.5M** and projected total 2013 room at about **$22.1M**. This is available to the January 15 front office as a planning estimate, not a league-certified adjusted cap figure. https://www.bigcatcountry.com/2013/1/9/3854934/jaguars-2013-salary-cap-space
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

The January 15 front office does **not** yet know the final 2013 league cap that will be announced later. This table separates the governing rule from when the number becomes available in-world.

| Control | 2013 rule / value | Runtime treatment |
|---|---|---|
| Final unadjusted league salary cap | **$123,000,000** | Later league fact announced Feb. 28; governs the 2013 league year but must not be treated as Jan. 15 Stone/Caldwell knowledge |
| 2013 league-year start | March 12, 2013, 4:00 p.m. ET | Cap compliance and Top-51 offseason accounting apply at league-year start |
| Offseason Top-51 | Only the 51 highest-valued contracts/tenders count in the ordinary offseason calculation, subject to Article 13 exceptions | Do not sum all offseason players as full cap charges |
| Veteran signing-bonus proration | Straight-line over contract term, **maximum five years** | General Article 13 rule |
| Rookie signing-bonus proration | **Maximum four years** | Separate Article 7 rookie rule |
| Release/trade on or before June 1 | Remaining unamortized signing bonus generally accelerates into the current League Year | Exact transaction timing/guarantees still matter |
| After-June-1 accounting | Future-year unamortized bonus generally shifts to the following League Year; up to two qualifying pre-June-1 terminations may be designated for June-2 treatment | Do not model every release as immediate full current-year acceleration |
| Club cash-spending minimum | **89%** of aggregate Salary Caps over 2013–2016 | Four-year test, not a 2013-only floor |
| League-wide cash-spending minimum | **95%** over 2013–2016 | Separate four-year league-wide requirement |
| Carryover | Up to 100% of unused prior-year cap room if timely elected | Jacksonville was publicly reported around $19.5M carryover; official league worksheet not recovered |

## Verified contract summaries and archived 2013 cap rows

Contract totals remain useful context, but the annual accounting columns are populated only where the contemporary archived OverTheCap page was recovered. “Other bonus” identifies the archived row's roster/workout amounts; an em dash means the archived row showed none.

| Player | Pos. | Signed | Nominal term | Total value | Total guarantee | 2013 base | Prorated bonus | Other bonus | 2013 cap number | Dead money | Verification |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| [Andre Branch](https://overthecap.com/player/andre-branch/909/) | ED | 2012 | 4 years | $5,089,934 | $3,153,129 | $621,361 | $535,442 | — | $1,156,803 | Not reconstructed for Jan. 15 | Current OTC 2013 Jaguars history row confirmed |
| [Blaine Gabbert](https://overthecap.com/player/blaine-gabbert/913/) | QB | 2011 | 4 years | $12,001,646 | $12,001,646 | $1,466,058 | $1,807,118 | — | $3,273,176 | $7,091,881 | Archived OverTheCap 2013 row confirmed |
| Brandon Marshall | LB | 2012 | 4 years | $2,300,500 | $200,500 | Unknown | Unknown | Unknown | Unknown | Unknown | Contract confirmed; Jacksonville archive row not yet recovered |
| [Bryan Anger](https://overthecap.com/player/bryan-anger/917/) | P | 2012 | 4 years | $2,877,166 | $662,500 | $509,913 | $165,625 | — | $675,538 | Not reconstructed for Jan. 15 | Current OTC 2013 Jaguars history row confirmed |
| [C.J. Mosley](https://overthecap.com/player/c-j-mosley/819/) | IDL | 2012 | 3 years | $7,500,000 | $1,000,000 | Unknown | Unknown | Unknown | Unknown | Unknown | Contract confirmed; Jacksonville archive row not yet recovered |
| [Cecil Shorts](https://overthecap.com/player/cecil-shorts/919/) | WR | 2011 | 4 years | $2,672,146 | $443,380 | $617,922 | $110,845 | — | $728,767 | Not reconstructed for Jan. 15 | Current OTC 2013 Jaguars history row confirmed |
| [Chad Henne](https://overthecap.com/player/chad-henne/920/) | QB | 2012 | 2 years | $6,750,000 | $4,075,000 | $2,625,000 | $1,500,000 | $25,000 workout + $500,000 other | $4,650,000 | Not reconstructed for Jan. 15 | Current OTC 2013 Jaguars history row confirmed |
| [Chris Prosinski](https://overthecap.com/player/chris-prosinski/921/) | S | 2011 | 4 years | $2,640,144 | $420,108 | $615,012 | $105,027 | — | $720,039 | Not reconstructed for Jan. 15 | Current OTC 2013 Jaguars history row confirmed |
| Dwight Lowery | S | 2012 | 4 years | $13,600,000 | $4,000,000 | $3,100,000 | $750,000 | $25,000 workout | $3,875,000 | $2,250,000 | Archived OverTheCap 2013 row confirmed |
| [Eugene Monroe](https://overthecap.com/player/eugene-monroe/927/) | LT | 2009 | 5 years | $25,000,000 | $19,020,000 | $3,800,000 | $1,742,500 | $205,000 workout | $5,747,500 | $3,140,000 | Archived OverTheCap 2013 row confirmed |
| [Jason Babin](https://overthecap.com/player/jason-babin/931/) | ED | 2011 | 5 years | $28,325,000 | $5,500,000 | $4,225,000 | — | $100,000 other | $4,325,000 | Not reconstructed for Jan. 15 | Current OTC 2013 Jaguars history row confirmed |
| [Jeremy Mincey](https://overthecap.com/player/jeremy-mincey/934/) | ED | 2012 | 4 years | $20,000,000 | $9,000,000 | $1,525,000 | $2,000,000 | $25,000 workout | $3,550,000 | $6,000,000 | Archived OverTheCap 2013 row confirmed |
| [Jeris Pendleton](https://overthecap.com/player/jeris-pendleton/2662/) | IDL | 2012 | 4 years | $2,151,392 | $51,392 | Unknown | Unknown | Unknown | Unknown | Unknown | Contract confirmed; Jacksonville archive row not yet recovered |
| [Justin Blackmon](https://overthecap.com/player/justin-blackmon/943/) | WR | 2012 | 4 years | $18,512,010 | $18,512,010 | $1,231,455 | $2,975,818 | — | $4,207,273 | $15,146,184 | Archived OverTheCap 2013 row confirmed |
| [Marcedes Lewis](https://overthecap.com/player/marcedes-lewis/946/) | TE | 2011 | 5 years | $34,000,000 | $17,000,000 | $4,200,000 | $1,400,000 | $150,000 workout | $5,750,000 | $4,200,000 | Archived OverTheCap 2013 row confirmed |
| [Maurice Jones-Drew](https://overthecap.com/player/maurice-jones-drew/949/) | RB | 2009 | 4 years | $30,515,000 | $9,000,000 | $4,950,000 | $1,800,000 | $50,000 workout | $6,800,000 | $1,800,000 | Archived OverTheCap 2013 row confirmed |
| [Mike Harris](https://overthecap.com/player/mike-harris/952/) | CB | 2012 | 4 years | $2,215,788 | $115,788 | $480,000 | $28,947 | — | $508,947 | Not reconstructed for Jan. 15 | Current OTC 2013 Jaguars history row confirmed |
| [Paul Posluszny](https://overthecap.com/player/paul-posluszny/954/) | LB | 2011 | 6 years | $45,000,000 | $15,000,000 | $6,450,000 | $2,000,000 | $50,000 workout | $8,500,000 | $6,000,000 | Archived OverTheCap 2013 row confirmed |
| [Russell Allen](https://overthecap.com/player/russell-allen/956/) | LB | 2012 | 3 years | $6,000,000 | $2,600,000 | $1,375,000 | $416,666 | $25,000 workout + $1,000,000 other | $2,816,666 | Not reconstructed for Jan. 15 | Current OTC 2013 Jaguars history row confirmed |
| [Tyson Alualu](https://overthecap.com/player/tyson-alualu/960/) | ED | 2010 | 5 years | $21,399,000 | $17,510,000 | $1,922,500 | $1,542,500 | $150,000 workout | $3,615,000 | $4,627,500 | Archived OverTheCap 2013 row confirmed |
| [Uche Nwaneri](https://overthecap.com/player/uche-nwaneri/961/) | RG | 2010 | 5 years | $24,000,000 | $8,600,000 | $3,775,000 | $1,094,500 | $1,000,000 roster + $25,000 workout | $5,894,500 | $3,283,500 | Archived OverTheCap 2013 row confirmed |
| [Will Rackley](https://overthecap.com/player/will-rackley/962/) | LG | 2011 | 4 years | $2,914,274 | $619,472 | $639,934 | $154,868 | — | $794,802 | $309,736 | Archived OverTheCap 2013 row confirmed |
| [Josh Scobee](https://overthecap.com/player/josh-scobee/941/) | K | 2012 | 4 years | $13.8M–$14.2M reported range | $4,750,000 reported guarantee | $2,325,000 | $937,500 | $25,000 workout | $3,287,500 | Not reconstructed for Jan. 15 | OTC 2013 Jaguars history row + contemporaneous 2012 contract report |

**Confirmed-player subtotal:** the **20 exact 2013 Jaguars Cap Number fields** now recovered total **$70,876,511**. Eleven come from contemporary archived OverTheCap pages and nine from unambiguous OverTheCap historical season rows. This remains a strict player subtotal, not the club Top-51 charge: it excludes every unrecovered player row, already-booked dead money, tenders, benefits/adjustments and Top-51 ordering effects.

## Complete roster contract-control ledger

| Player | Contract-control finding at snapshot | 2013 financial fields |
|---|---|---|
| Blaine Gabbert | Verified 2011 contract summary above | Archived 2013 row confirmed; see table above |
| Chad Henne | Verified 2012 contract summary above | Exact 2013 Jaguars history row confirmed; $4,650,000 cap number |
| Jordan Palmer | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jalen Parmele | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jonathan Grimes | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Keith Toston | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Maurice Jones-Drew | Verified 2009 contract summary above | Archived 2013 row confirmed; see table above |
| Richard Murphy | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Greg Jones | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Montell Owens | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Cecil Shorts | Verified 2011 contract summary above | Exact 2013 Jaguars history row confirmed; $728,767 cap number |
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
| Andre Branch | Verified 2012 contract summary above | Exact 2013 Jaguars history row confirmed; $1,156,803 cap number |
| Austen Lane | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| George Selvie | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jason Babin | Verified 2011 contract summary above | Exact 2013 Jaguars history row confirmed; $4,325,000 cap number |
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
| Russell Allen | Verified 2012 contract summary above | Exact 2013 Jaguars history row confirmed; $2,816,666 cap number |
| Aaron Ross | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Antwaun Molden | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Derek Cox | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Kevin Rutland | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Mike Harris | Verified 2012 contract summary above | Exact 2013 Jaguars history row confirmed; $508,947 cap number |
| Rashean Mathis | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Chris Prosinski | Verified 2011 contract summary above | Exact 2013 Jaguars history row confirmed; $720,039 cap number |
| Antwon Blake | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Dawan Landry | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Dwight Lowery | Verified 2012 contract summary above | Archived 2013 row confirmed; see table above |
| Josh Scobee | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Exact 2013 Jaguars history row confirmed; $3,287,500 cap number |
| Bryan Anger | Verified 2012 contract summary above | Exact 2013 Jaguars history row confirmed; $675,538 cap number |
| Jeremy Cain | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |

## January 15 decision-facing cap picture

This is the part Stone and Caldwell may actually use at initialization.

### What is known by January 15

A January 9 public report citing ESPN's John Clayton estimated:

- **about $19.5 million of 2012 cap room carried into 2013**; and
- **about $22.1 million of total projected 2013 cap room** for Jacksonville.

That is the best dated top-down planning number presently available **before Stone's January 15 hire**.

It is not a league-certified adjusted-cap worksheet. The final 2013 unadjusted cap had not yet been announced, exact benefit/credit/debit adjustments were not public, and the Rule-of-51 league-year calculation had not yet become the live compliance calculation.

**Runtime planning rule:** on January 15, use **~$22.1M projected room** as the club's planning estimate, with appropriate uncertainty. Do not replace it with a later March figure until the simulation date reaches that information.

Source: https://www.bigcatcountry.com/2013/1/9/3854934/jaguars-2013-salary-cap-space

## Research-only later validation — do not leak backward

Later period evidence can test whether the January estimate was reasonable without becoming January knowledge.

- The league ultimately set the unadjusted 2013 cap at **$123.0M**.
- An NFL.com leaguewide pre-free-agency snapshot later listed Jacksonville at **$23.8M under**.
- Jacksonville's own pre-free-agency coverage described the club as having **a little more than $20M** in room entering the league year.

Those later figures broadly validate a **low-/mid-$20M flexibility picture**, but they do not retroactively become Stone's January 15 information.

Sources:
- https://www.nfl.com/photos/nfl-salary-cap-situations-0ap1000000133245
- https://www.jaguars.com/news/no-1-objective-gather-talent-9607137
- https://www.jaguars.com/news/2013-nfl-free-agency-questions-answers-9665810

## Team reconciliation

| Item | Amount/status | Validation result |
|---|---|---|
| Exact recovered player-cap subtotal | **$70,876,511** | Sum of 20 exact 2013 Jaguars player cap rows; not the Top-51 club total |
| January 9 reported carryover | **about $19.5M** | Pre-hire public planning estimate |
| January 9 projected 2013 room | **about $22.1M** | Best current January-15 decision-facing top-down estimate |
| Final unadjusted 2013 cap | **$123.0M** | Later league fact; unavailable to Stone on Jan. 15 |
| Later pre-free-agency room cross-check | **$23.8M under** | Research-only validation from NFL.com; not January knowledge |
| Top-51 exact charge | **Not fully reconstructed** | Requires every contract/tender competing for the 51 highest values plus already-booked non-player charges |
| Already-booked dead money | **Not fully reconstructed** | Current player-page hypothetical dead money is not the same thing as club dead money already on the books |
| Rookie pool | **No signed-rookie cap charges yet** | Draft/signing reserve becomes relevant later; do not subtract a fictional rookie contract total on Jan. 15 |
| Head-coach / assistant payroll | **Excluded from player cap** | Tracked separately from NFL player salary accounting |

## Contract-pressure map

This table is designed for roster decisions. It does **not** tell Stone whom to cut.

### High existing 2013 cap exposure among exact rows

| Player | 2013 cap number | Financial note |
|---|---:|---|
| Paul Posluszny | $8,500,000 | Largest exact recovered cap number |
| Maurice Jones-Drew | $6,800,000 | Final year of existing veteran deal |
| Uche Nwaneri | $5,894,500 | Significant veteran OL commitment |
| Marcedes Lewis | $5,750,000 | Significant TE commitment |
| Eugene Monroe | $5,747,500 | Final contract year; no later real transaction imported |
| Chad Henne | $4,650,000 | Material QB2/QB-competition cost |
| Jason Babin | $4,325,000 | Veteran edge cost |
| Justin Blackmon | $4,207,273 | Fully guaranteed rookie-contract structure remains highly restrictive |
| Dwight Lowery | $3,875,000 | Veteran secondary commitment |
| Tyson Alualu | $3,615,000 | Rookie-contract veteran-year charge |
| Jeremy Mincey | $3,550,000 | Existing veteran DE commitment |
| Josh Scobee | $3,287,500 | Premium kicker contract |
| Blaine Gabbert | $3,273,176 | Guaranteed rookie-contract exposure |
| Russell Allen | $2,816,666 | Veteran LB commitment |

The point of this table is to show where meaningful dollars actually sit. A high cap number is neither a keep recommendation nor a cut recommendation.

## 2013 league-year release-planning flags

For the eleven archived rows that include a contemporary hypothetical Dead Money field, the file can identify whether a **standard 2013 league-year termination** appears to create gross cap room or gross cap loss.

This is a planning flag, not executable release math. Guarantees, transaction date, June-1 treatment, injury protection, grievances and the exact club ledger can alter the final accounting.

| Player | 2013 cap | Archived dead-money field | Gross cap delta if ordinary timing applied | Planning interpretation |
|---|---:|---:|---:|---|
| Maurice Jones-Drew | $6,800,000 | $1,800,000 | **+$5,000,000** | Financial flexibility exists; football value still controls |
| Uche Nwaneri | $5,894,500 | $3,283,500 | **+$2,611,000** | Positive gross room |
| Eugene Monroe | $5,747,500 | $3,140,000 | **+$2,607,500** | Positive gross room |
| Paul Posluszny | $8,500,000 | $6,000,000 | **+$2,500,000** | Positive gross room |
| Dwight Lowery | $3,875,000 | $2,250,000 | **+$1,625,000** | Positive gross room |
| Marcedes Lewis | $5,750,000 | $4,200,000 | **+$1,550,000** | Positive gross room |
| Will Rackley | $794,802 | $309,736 | **+$485,066** | Small gross room |
| Tyson Alualu | $3,615,000 | $4,627,500 | **-$1,012,500** | Standard release would worsen gross cap position |
| Jeremy Mincey | $3,550,000 | $6,000,000 | **-$2,450,000** | Standard release would worsen gross cap position |
| Blaine Gabbert | $3,273,176 | $7,091,881 | **-$3,818,705** | Strong cap lock under ordinary timing |
| Justin Blackmon | $4,207,273 | $15,146,184 | **-$10,938,911** | Very strong cap lock under ordinary timing |

Again: **gross cap delta is not total roster value**. Replacing the player costs money and talent, and later post-June-1 structures can change timing.

## Pre-release veteran exposures recoverable only by reconstruction

Some player pages were overwritten by later-team contracts, but contemporaneous reporting still recovers useful **pre-existing financial terms** from before the actual real-world release. Those terms may be used for branch decision analysis because the contracts already existed on January 15. The historical decision to release the player is quarantined.

| Player | Pre-existing 2013 exposure recoverable from period reporting | What remains uncertain |
|---|---|---|
| Dawan Landry | About **$6.7M opening cap exposure** reconstructed from $3.9M dead charge + roughly $2.8M reported savings; about $5.35–$5.4M cash due | Exact line-by-line Jan. 15 bonus composition |
| Aaron Ross | About **$3.705M opening cap exposure**; later actual release left $666,667 dead and created roughly $3.0M room | Exact Jan. 15 component split |
| Guy Whimper | About **$1.825M scheduled 2013 cap number**; later actual release shows $500K Jaguars dead money | Exact Jan. 15 component split |
| Laurent Robinson | Public Jaguars reporting referred to an approximately **$9M 2013 cap figure**; later release produced complex guarantee/grievance accounting | Exact clean pre-release cap composition and injury-guarantee treatment require caution |
| C.J. Mosley | Existing 3-year Jacksonville deal still controlled him on Jan. 15; later actual release created $666,667 Jaguars dead money | Exact scheduled Jaguars 2013 cap row not recovered |

These are **contract reconstruction facts**, not recommendations to repeat the real 2013 releases.

## What the sheet can support now

The file is sufficient for Stone/Caldwell to:

- understand that Jacksonville is entering the offseason with meaningful financial flexibility rather than a cap crisis;
- identify which existing contracts consume real resources;
- compare a proposed free-agent contract with the club's January planning room;
- identify when a veteran transaction is likely to create or consume cap room;
- discuss restructuring, release or trade scenarios without pretending salary cap is irrelevant;
- avoid confusing coaching payroll with player-cap accounting.

## What still requires reconciliation before claiming an exact post-transaction club balance

Before reporting a **penny-accurate** new cap-space total, reconcile:

1. every contract/tender that enters the Top-51;
2. reserve/future deals that actually count in the Top-51;
3. already-booked dead money from prior transactions;
4. benefit adjustments and league credits/debits;
5. the official rather than rounded carryover election;
6. any branch-specific transaction already executed;
7. any guarantee, grievance or June-1 treatment specific to the transaction being modeled.

### Operating rule for the simulation

**Do not block ordinary football decisions merely because the complete club worksheet is unavailable.**

- Before March 12: use the **~$22.1M January planning estimate** for strategy and negotiation ranges.
- Once the league year opens: update from the best contemporaneous club-room figure then available.
- For a transaction with a sourced individual cap effect, apply that effect to the current planning figure.
- Label the resulting club room as an **estimate** unless the full Top-51/adjusted-cap worksheet has been reconciled.
- If a proposed transaction approaches the uncertainty margin or depends on complicated guarantees/dead money, require a deeper cap reconciliation before execution.

This keeps the simulation financially disciplined without pretending an NFL club becomes incapable of acting until every historical accounting line has been reconstructed.

