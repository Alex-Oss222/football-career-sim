# Jacksonville Jaguars — Initial 2013 Cap and Contract Sheet

**Accounting date:** January 15, 2013  
**League-year distinction:** the 2013 league year and its $123,000,000 cap do not begin until March 12, 2013 at 4:00 p.m. ET.  
**Status:** `DECISION-USABLE PLANNING BASELINE; 20 TRANSCRIBED 2013 PLAYER CAP ROWS; JANUARY ROOM APPROXIMATE; FULL TOP-51 LEDGER STILL OPEN`

**Audit date:** September 18, 2026. Source transcription, January applicability, and independent corroboration are separate checks; see the verification record.

## Sources and evidence boundary

- **Primary roster spine:** NFLverse's archived NFL weekly-roster export, `roster_weekly_2012.csv`, filtered to Jacksonville, regular-season Week 17, status `ACT`. The source preserves NFL identifiers, listed position, jersey and experience. [NFLverse weekly-rosters release](https://github.com/nflverse/nflverse-data/releases/tag/weekly_rosters)
- **Independent roster/role check:** Pro Football Reference's 2012 Jacksonville roster table as redistributed without alteration in NFLverse's `pfr_rosters.csv`; the games and starts in `initial_roster.md` are real 2012 facts, not evaluations. [NFLverse miscellaneous-data release](https://github.com/nflverse/nflverse-data/releases/tag/misc) and [PFR 2012 Jaguars roster](https://www.pro-football-reference.com/teams/jax/2012_roster.htm)
- **Archived annual cap rows:** the prior research pass transcribed eleven Jacksonville Base Salary, Prorated Bonus, other bonus, Cap Number and Dead Money rows from archived OverTheCap 2013 `cap.php` pages. Exact capture URLs and timestamps were not retained in this file; the discovery query alone does not identify the evidence for each row: [Internet Archive CDX query for archived Jaguars cap pages](http://web.archive.org/cdx/search/cdx?url=overthecap.com/cap.php*&filter=urlkey:.*jaguars.*&from=20130101&to=20130601&output=text&limit=200).
- **Current OverTheCap historical season rows:** the linked player pages preserve 2013 Jaguars rows for Chad Henne, Jason Babin, Russell Allen, Josh Scobee, Andre Branch, Cecil Shorts, Bryan Anger, Chris Prosinski and Mike Harris. Their displayed annual components were rechecked in this audit. A historical season row can include later changes or adjustments; matching its transcription does not by itself establish the January 15 scheduled obligation.
- **Top-down January planning estimate:** a January 9, 2013 report citing ESPN’s John Clayton put Jacksonville’s carryover at about **$19.5M** and projected total 2013 room at about **$22.1M**. This is available to the January 15 front office as a planning estimate, not a league-certified adjusted cap figure. https://www.bigcatcountry.com/2013/1/9/3854934/jaguars-2013-salary-cap-space
- **Contract-page index:** NFLverse’s OverTheCap-derived historical-contract export supplies each matched player’s current OverTheCap player-page URL and the already-recorded contract summary. [NFLverse contracts release](https://github.com/nflverse/nflverse-data/releases/tag/contracts)
- **Independent annual-cash check:** the public `haleykahn14/NFL-Salary-Cap` workbook, described by its maintainer as Spotrac-derived, was queried only for pre-existing Jacksonville contracts and only for its 2013 `salary` field. It is not treated as a cap ledger: its bonus columns are cash-payment fields, not annual cap proration. [Source workbook](https://github.com/haleykahn14/NFL-Salary-Cap/blob/main/merged_salaries_2013_2022_cleaned.xlsx)
- **Rules:** apply `foundation/02_League_Era_and_Sourcebook.md` §11 and `library/2013_league_calendar_and_financial_rules.md`. The Jaguars' [March 8, 2013 league Q&A](https://www.jaguars.com/news/2013-nfl-free-agency-questions-answers-9665810) also confirms the final league cap, compliance deadline and carryover mechanism; it is a later rules reference, not January club-room evidence.

**Cutoff:** January 15, 2013, the counterfactual Stone hire date. The final 2012 active roster is the last clean NFL roster snapshot available in the archived weekly feed. Reserve/injured designations are separately labeled because the export does not retain every reserve-list player in its Week 17 active slice. No actual transaction, release, re-signing, draft choice, staff hire, or player outcome after the divergence point is adopted as simulation canon. Later accounting records may reconstruct an earlier contract only when its January applicability is supported. Later actual dead-money entries do not become January liabilities.

## Verification record

### Prior research record

#### Pass 1: research

The OverTheCap historical-contract export was first matched against the roster inventory for player identity, signed year, nominal term, total value, total guarantee and player-page URL. The Spotrac-derived annual-cash workbook independently supplied the base-salary subset without treating cash bonuses as cap proration.

#### Pass 2: skeptical re-check

A separate archival pass located OverTheCap's contemporary `cap.php` pages through the Internet Archive CDX index and read the 2013 annual rows. The prior pass accepted eleven rows, reporting that archived Base Salary agreed with the independent annual-cash source where available; the archive supplied the separate proration, other-bonus, Cap Number and Dead Money fields. That salary comparison does not independently corroborate the other fields. The archived figures are transcribed rather than recomputed from contract totals. Rows without a Jacksonville-specific archive remain separate from the nine current historical rows; a later-team contract is not substituted for a Jacksonville obligation.

### September 18, 2026 audit: findings and limits

- **Arithmetic confirmed:** all 20 populated cap numbers equal their listed base, proration and other-bonus components. The eleven archived transcriptions sum to **$52,007,251** and the nine current-history transcriptions sum to **$18,869,260**, for **$70,876,511**. All eleven displayed gross release deltas also reconcile.
- **Source-match confirmed for nine rows:** the linked OTC pages reproduce the displayed 2013 Jaguars components. This is a re-read of one publisher, not independent verification of the full January obligation. Henne's $500,000, Allen's $1,000,000 and Babin's $100,000 entries remain labeled **other**; their precise type, earning conditions and January cap treatment are unresolved.
- **January report confirmed:** Alfie Crow's January 9 article reports both the ~$19.5M carryover and ~$22.1M total projected room. The linked ESPN original could not be read in this audit, so the exact January estimate remains an attributed report, not an independently reconciled club balance.
- **Archive provenance remains open:** the CDX query could not be retrieved during this audit. The eleven older rows are retained as prior transcriptions, not newly source-verified numbers. Restore each exact capture URL, capture date, 2013 Jaguars row and evidence that no post-cutoff amendment changed the applicable terms before treating it as a verified January transaction input.
- **Reconstruction leads remain open:** the five veteran exposure estimates below lack row-specific period citations in the supplied sheet. They are retained as research leads and cannot supply booked savings until corroborated. No unsupported replacement figures were invented.

The planning estimate remains usable while these row-level questions are resolved for the transactions that depend on them.

## Governing 2013 controls

The January 15 front office does **not** yet know the final 2013 league cap that will be announced later. This table separates the governing rule from when the number becomes available in-world.

| Control | 2013 rule / value | Runtime treatment |
|---|---|---|
| Final unadjusted league salary cap | **$123,000,000** | Later league fact announced Feb. 28; governs the 2013 league year but must not be treated as Jan. 15 Stone/Caldwell knowledge |
| 2013 league-year start | March 12, 2013, 4:00 p.m. ET | Cap compliance and Top-51 offseason accounting apply at league-year start |
| Offseason Top-51 | The 51 highest-valued contracts/tenders principally determine ordinary salary counting; applicable bonus proration and other Article 13 items outside that group still count | Recompute the counted obligations when a contract enters or leaves the Top-51; excluded base salary does not imply a zero total charge |
| Veteran signing-bonus proration | Straight-line over contract term, **maximum five years** | General Article 13 rule |
| Rookie signing-bonus proration | **Maximum four years** | Separate Article 7 rookie rule |
| Release/trade on or before June 1 | Remaining unamortized signing bonus generally accelerates into the current League Year | Exact transaction timing/guarantees still matter |
| After-June-1 accounting | Future-year unamortized bonus generally shifts to the following League Year; up to two qualifying pre-June-1 terminations may be designated for June-2 treatment | Do not model every release as immediate full current-year acceleration |
| Club cash-spending minimum | **89%** of aggregate Salary Caps over 2013–2016 | Four-year test, not a 2013-only floor |
| League-wide cash-spending minimum | **95%** over 2013–2016 | Separate four-year league-wide requirement |
| Carryover | Up to 100% of unused prior-year cap room if timely elected | Jacksonville was publicly reported around $19.5M carryover; official league worksheet not recovered |

## Reported contract summaries and transcribed 2013 cap rows

Contract totals and original guarantees describe the reported deal at signing, not remaining guarantees or release cost. A nominal extension term is not necessarily the full remaining contract term. Annual columns combine eleven prior archived transcriptions and nine current OTC season-history rows. The verification column identifies the source class, not blanket January certification. A dash means the source recorded no amount for that component; **Unknown** means missing evidence and must never be counted as zero. An unspecified **other** bonus must not be silently reclassified as a roster bonus or guaranteed cash.

| Player | Pos. | Signed | Nominal term | Total value | Guarantee at signing | 2013 base | Prorated bonus | Other bonus | 2013 cap number | Hypothetical dead money | Verification |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| [Andre Branch](https://overthecap.com/player/andre-branch/909/) | ED | 2012 | 4 years | $5,089,934 | $3,153,129 | $621,361 | $535,442 | — | $1,156,803 | Not reconstructed for Jan. 15 | OTC history source-matched; see audit |
| [Blaine Gabbert](https://overthecap.com/player/blaine-gabbert/913/) | QB | 2011 | 4 years | $12,001,646 | $12,001,646 | $1,466,058 | $1,807,118 | — | $3,273,176 | $7,091,881 | Prior archive transcription; see audit |
| Brandon Marshall | LB | 2012 | 4 years | $2,300,500 | $200,500 | Unknown | Unknown | Unknown | Unknown | Unknown | Contract confirmed; Jacksonville archive row not yet recovered |
| [Bryan Anger](https://overthecap.com/player/bryan-anger/917/) | P | 2012 | 4 years | $2,877,166 | $662,500 | $509,913 | $165,625 | — | $675,538 | Not reconstructed for Jan. 15 | OTC history source-matched; see audit |
| [C.J. Mosley](https://overthecap.com/player/c-j-mosley/819/) | IDL | 2012 | 3 years | $7,500,000 | $1,000,000 | Unknown | Unknown | Unknown | Unknown | Unknown | Contract confirmed; Jacksonville archive row not yet recovered |
| [Cecil Shorts](https://overthecap.com/player/cecil-shorts/919/) | WR | 2011 | 4 years | $2,672,146 | $443,380 | $617,922 | $110,845 | — | $728,767 | Not reconstructed for Jan. 15 | OTC history source-matched; see audit |
| [Chad Henne](https://overthecap.com/player/chad-henne/920/) | QB | 2012 | 2 years | $6,750,000 | $4,075,000 | $2,625,000 | $1,500,000 | $25,000 workout + $500,000 other | $4,650,000 | Not reconstructed for Jan. 15 | OTC history source-matched; see audit |
| [Chris Prosinski](https://overthecap.com/player/chris-prosinski/921/) | S | 2011 | 4 years | $2,640,144 | $420,108 | $615,012 | $105,027 | — | $720,039 | Not reconstructed for Jan. 15 | OTC history source-matched; see audit |
| Dwight Lowery | S | 2012 | 4 years | $13,600,000 | $4,000,000 | $3,100,000 | $750,000 | $25,000 workout | $3,875,000 | $2,250,000 | Prior archive transcription; see audit |
| [Eugene Monroe](https://overthecap.com/player/eugene-monroe/927/) | LT | 2009 | 5 years | $25,000,000 | $19,020,000 | $3,800,000 | $1,742,500 | $205,000 workout | $5,747,500 | $3,140,000 | Prior archive transcription; see audit |
| [Jason Babin](https://overthecap.com/player/jason-babin/931/) | ED | 2011 | 5 years | $28,325,000 | $5,500,000 | $4,225,000 | — | $100,000 other | $4,325,000 | Not reconstructed for Jan. 15 | OTC history source-matched; see audit |
| [Jeremy Mincey](https://overthecap.com/player/jeremy-mincey/934/) | ED | 2012 | 4 years | $20,000,000 | $9,000,000 | $1,525,000 | $2,000,000 | $25,000 workout | $3,550,000 | $6,000,000 | Prior archive transcription; see audit |
| [Jeris Pendleton](https://overthecap.com/player/jeris-pendleton/2662/) | IDL | 2012 | 4 years | $2,151,392 | $51,392 | Unknown | Unknown | Unknown | Unknown | Unknown | Contract confirmed; Jacksonville archive row not yet recovered |
| [Justin Blackmon](https://overthecap.com/player/justin-blackmon/943/) | WR | 2012 | 4 years | $18,512,010 | $18,512,010 | $1,231,455 | $2,975,818 | — | $4,207,273 | $15,146,184 | Prior archive transcription; see audit |
| [Marcedes Lewis](https://overthecap.com/player/marcedes-lewis/946/) | TE | 2011 | 5 years | $34,000,000 | $17,000,000 | $4,200,000 | $1,400,000 | $150,000 workout | $5,750,000 | $4,200,000 | Prior archive transcription; see audit |
| [Maurice Jones-Drew](https://overthecap.com/player/maurice-jones-drew/949/) | RB | 2009 | 4 years | $30,515,000 | $9,000,000 | $4,950,000 | $1,800,000 | $50,000 workout | $6,800,000 | $1,800,000 | Prior archive transcription; see audit |
| [Mike Harris](https://overthecap.com/player/mike-harris/952/) | CB | 2012 | 4 years | $2,215,788 | $115,788 | $480,000 | $28,947 | — | $508,947 | Not reconstructed for Jan. 15 | OTC history source-matched; see audit |
| [Paul Posluszny](https://overthecap.com/player/paul-posluszny/954/) | LB | 2011 | 6 years | $45,000,000 | $15,000,000 | $6,450,000 | $2,000,000 | $50,000 workout | $8,500,000 | $6,000,000 | Prior archive transcription; see audit |
| [Russell Allen](https://overthecap.com/player/russell-allen/956/) | LB | 2012 | 3 years | $6,000,000 | $2,600,000 | $1,375,000 | $416,666 | $25,000 workout + $1,000,000 other | $2,816,666 | Not reconstructed for Jan. 15 | OTC history source-matched; see audit |
| [Tyson Alualu](https://overthecap.com/player/tyson-alualu/960/) | ED | 2010 | 5 years | $21,399,000 | $17,510,000 | $1,922,500 | $1,542,500 | $150,000 workout | $3,615,000 | $4,627,500 | Prior archive transcription; see audit |
| [Uche Nwaneri](https://overthecap.com/player/uche-nwaneri/961/) | RG | 2010 | 5 years | $24,000,000 | $8,600,000 | $3,775,000 | $1,094,500 | $1,000,000 roster + $25,000 workout | $5,894,500 | $3,283,500 | Prior archive transcription; see audit |
| [Will Rackley](https://overthecap.com/player/will-rackley/962/) | LG | 2011 | 4 years | $2,914,274 | $619,472 | $639,934 | $154,868 | — | $794,802 | $309,736 | Prior archive transcription; see audit |
| [Josh Scobee](https://overthecap.com/player/josh-scobee/941/) | K | 2012 | 4 years | $13.8M–$14.2M reported range | $4,750,000 reported guarantee | $2,325,000 | $937,500 | $25,000 workout | $3,287,500 | Not reconstructed for Jan. 15 | OTC season row source-matched; 2012 contract-report citation still needed |

**Transcribed-player subtotal:** the **20 populated 2013 Jaguars Cap Number fields** total **$70,876,511**. The sum is arithmetically exact; its completeness and January applicability are not. It excludes unrecovered player rows, already-booked dead money, tenders, other countable charges and Top-51 ordering effects. **Do not subtract this partial subtotal from the league cap to claim club room.** League benefits are not an additional blanket deduction from the published player salary cap; apply only the relevant club credits/debits under the governing rules.

## Roster contract-control inventory

The 63 listed players are a roster-derived inventory, not 63 established 2013 contracts or a complete Top-51 worksheet. Week 17 membership does not prove continued contract control, a reserve/future signing or a 2013 tender. Check intervening pre-hire transactions and expiring contracts before adding annual obligations.

| Player | Contract-control finding at snapshot | 2013 financial fields |
|---|---|---|
| Blaine Gabbert | Verified 2011 contract summary above | Prior archive transcription; see evidence limits above |
| Chad Henne | Verified 2012 contract summary above | OTC historical 2013 row source-matched; $4,650,000 cap number |
| Jordan Palmer | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jalen Parmele | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jonathan Grimes | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Keith Toston | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Maurice Jones-Drew | Verified 2009 contract summary above | Prior archive transcription; see evidence limits above |
| Richard Murphy | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Greg Jones | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Montell Owens | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Cecil Shorts | Verified 2011 contract summary above | OTC historical 2013 row source-matched; $728,767 cap number |
| Jerrell Jackson | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jordan Shipley | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Justin Blackmon | Verified 2012 contract summary above | Prior archive transcription; see evidence limits above |
| Laurent Robinson | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Mike Brown | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Toney Clemons | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Allen Reisner | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Isaiah Stanback | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Marcedes Lewis | Verified 2011 contract summary above | Prior archive transcription; see evidence limits above |
| Zach Potter | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Cameron Bradfield | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Eugene Monroe | Verified 2009 contract summary above | Prior archive transcription; see evidence limits above |
| Guy Whimper | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Austin Pasztor | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Eben Britton | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Mark Asper | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Uche Nwaneri | Verified 2010 contract summary above | Prior archive transcription; see evidence limits above |
| Will Rackley | Verified 2011 contract summary above | Prior archive transcription; see evidence limits above |
| Brad Meester | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Mike Brewster | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Steve Vallos | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Andre Branch | Verified 2012 contract summary above | OTC historical 2013 row source-matched; $1,156,803 cap number |
| Austen Lane | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| George Selvie | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jason Babin | Verified 2011 contract summary above | OTC historical 2013 row source-matched; $4,325,000 cap number |
| Jeremy Mincey | Verified 2012 contract summary above | Prior archive transcription; see evidence limits above |
| John Chick | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| C.J. Mosley | Verified 2012 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| D'Anthony Smith | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jeris Pendleton | Verified 2012 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Jerome Long | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Terrance Knighton | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Tyson Alualu | Verified 2010 contract summary above | Prior archive transcription; see evidence limits above |
| Kyle Bosworth | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Paul Posluszny | Verified 2011 contract summary above | Prior archive transcription; see evidence limits above |
| Brandon Marshall | Verified 2012 contract summary above | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Daryl Smith | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Julian Stanford | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Russell Allen | Verified 2012 contract summary above | OTC historical 2013 row source-matched; $2,816,666 cap number |
| Aaron Ross | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Antwaun Molden | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Derek Cox | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Kevin Rutland | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Mike Harris | Verified 2012 contract summary above | OTC historical 2013 row source-matched; $508,947 cap number |
| Rashean Mathis | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Chris Prosinski | Verified 2011 contract summary above | OTC historical 2013 row source-matched; $720,039 cap number |
| Antwon Blake | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Dawan Landry | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |
| Dwight Lowery | Verified 2012 contract summary above | Prior archive transcription; see evidence limits above |
| Josh Scobee | Reported 2012 four-year terms above; period-report citation remains open | OTC historical 2013 row source-matched; $3,287,500 cap number |
| Bryan Anger | Verified 2012 contract summary above | OTC historical 2013 row source-matched; $675,538 cap number |
| Jeremy Cain | Player appears on sourced roster; exact contract term not independently confirmed in available contract export | Base, bonus/proration, cash and cap charge unknown pending club-level ledger |

## January 15 decision-facing cap picture

This is the part Stone and Caldwell may actually use at initialization.

### What is known by January 15

A January 9 public report citing ESPN's John Clayton estimated:

- **about $19.5 million of 2012 cap room carried into 2013**; and
- **about $22.1 million of total projected 2013 cap room** for Jacksonville.

That is the best dated top-down planning number presently available **before Stone's January 15 hire**.

It is not a league-certified adjusted-cap worksheet. The final 2013 unadjusted cap had not yet been announced, exact club credits/debits were not established in the recovered evidence, and the Rule-of-51 league-year calculation had not yet become the live compliance calculation.

**Runtime planning rule:** on January 15, use **~$22.1M projected room** as the club's planning estimate, with appropriate uncertainty. The reported carryover is already included; **do not add the ~$19.5M again**. The report does not expose a full cap-assumption worksheet, so it also does not support a mechanical adjustment to the final cap. Later real-world club room requires both a date check and a transaction reconciliation to this branch before adoption.

Source: https://www.bigcatcountry.com/2013/1/9/3854934/jaguars-2013-salary-cap-space

## Research-only comparisons: do not leak backward

- [Jaguars league Q&A, March 8, 2013](https://www.jaguars.com/news/2013-nfl-free-agency-questions-answers-9665810): confirms the **$123.0M league cap**, not Jacksonville's cap room.
- [NFL.com gallery](https://www.nfl.com/photos/nfl-salary-cap-situations-0ap1000000133245): **$23.8M room assuming a $121M cap; date unverified. Not a final-cap reconciliation.**
- [Jaguars reporting, February 22, 2013](https://www.jaguars.com/news/no-1-objective-gather-talent-9607137): estimates room slightly above **$20M** entering the league year.

These reports support a broad flexibility assessment. They do not establish an exact balance on a common accounting date. A later actual-club snapshot may reflect moves that never occurred in this branch; reaching its publication date alone does not authorize importing its balance.

## Team reconciliation

| Item | Amount/status | Validation result |
|---|---|---|
| Transcribed player-cap subtotal | **$70,876,511** | Arithmetic verified across 20 populated rows; January applicability and the complete club charge remain open |
| January 9 reported carryover | **about $19.5M** | Pre-hire public planning estimate |
| January 9 projected 2013 room | **about $22.1M** | Best current January-15 decision-facing top-down estimate |
| Final unadjusted 2013 cap | **$123.0M** | Later league fact; unavailable to Stone on Jan. 15 |
| Total offseason team charge | **Not fully reconstructed** | Requires Top-51 ordering, applicable charges outside that group, already-booked dead money and other countable items |
| Already-booked dead money | **Not fully reconstructed** | Current player-page hypothetical dead money is not the same thing as club dead money already on the books |
| Draft-class planning reserve | **No 2013 draft class selected at this snapshot** | Keep a labeled future reserve when setting offers; use sourced expected net cap cost and Top-51 effects as available, not the gross multi-year rookie contract total |
| Head-coach / assistant payroll | **Excluded from player cap** | Tracked separately from NFL player salary accounting |

## Contract-pressure map

This table is designed for roster decisions. It does **not** tell Stone whom to cut.

### Highest transcribed 2013 cap exposures

| Player | 2013 cap number | Financial note |
|---|---:|---|
| Paul Posluszny | $8,500,000 | Largest transcribed cap number; archive provenance still open |
| Maurice Jones-Drew | $6,800,000 | Final year of existing veteran deal |
| Uche Nwaneri | $5,894,500 | Significant veteran OL commitment |
| Marcedes Lewis | $5,750,000 | Significant TE commitment |
| Eugene Monroe | $5,747,500 | Final contract year; no later real transaction imported |
| Chad Henne | $4,650,000 | Material QB2/QB-competition cost |
| Jason Babin | $4,325,000 | Veteran edge cost |
| Justin Blackmon | $4,207,273 | Reported rookie guarantees require clause-level review before a release or trade |
| Dwight Lowery | $3,875,000 | Veteran secondary commitment |
| Tyson Alualu | $3,615,000 | Rookie-contract veteran-year charge |
| Jeremy Mincey | $3,550,000 | Existing veteran DE commitment |
| Josh Scobee | $3,287,500 | Premium kicker contract |
| Blaine Gabbert | $3,273,176 | Reported rookie guarantees require clause-level review |
| Russell Allen | $2,816,666 | Veteran LB commitment |

This ranks the recovered figures only; missing large veteran rows can change the ordering. Use it to prioritize contract review, with the source and January-applicability limits above. A high cap number is neither a keep recommendation nor a cut recommendation.

## 2013 league-year release-planning flags

For the eleven prior archived transcriptions with a hypothetical Dead Money field, subtraction supplies a **conditional 2013 league-year, on-or-before-June-1 release comparison**. The archive capture and dead-money assumptions remain to be re-established; this table does not certify any release cost.

These figures are screening arithmetic, not executable release math. Guarantees, vesting dates, injury protection, grievances and transaction timing can change the result. Do not use this release column for trades, which can transfer obligations differently. A January transaction occurs in the 2012 league year and needs a separate analysis of 2012 closing charges, carryover and 2013 effects.

| Player | 2013 cap | Archived dead-money field | Gross cap delta if the transcribed assumptions apply | Planning interpretation |
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

**Gross release delta is not net spendable room.** Account for the incremental counted cost of the player moving into the Top-51, any replacement contract and any already-counted bonus amounts. Post-June-1 treatment changes when charges and relief occur; do not spend deferred relief in March. The before/after club calculation below controls.

## Veteran reconstruction leads: verification incomplete

The earlier sheet attributed the following numbers to period reporting without attaching a specific source to each row. This audit could not independently corroborate them. Preserve them as **unverified research leads**, excluded from the transcribed subtotal and from booked transaction savings. A later actual dead-money charge alone cannot reconstruct a January release cost: timing, guarantees, amendments and settlements may differ.

| Player | Previously reported lead, not a verified January charge | Evidence required before applying a cap effect |
|---|---|---|
| Dawan Landry | Prior sheet estimated ~$6.7M cap from ~$3.9M dead money plus ~$2.8M savings, and ~$5.35M-$5.4M cash | Dated source for both sides of the reconstruction; January contract components and guarantee treatment |
| Aaron Ross | Prior sheet listed ~$3.705M cap, $666,667 later dead money and roughly $3.0M savings | Dated source, consistent release timing and January component split |
| Guy Whimper | Prior sheet listed ~$1.825M scheduled cap and $500K later dead money | Dated source and January component split; later dead money alone is insufficient |
| Laurent Robinson | Prior sheet attributed an approximately $9M cap figure to Jaguars reporting | Recover the exact article and distinguish scheduled cap, guaranteed cash and termination exposure; resolve applicable injury-guarantee terms without importing a later grievance outcome |
| C.J. Mosley | Prior sheet cited $666,667 later Jaguars dead money alongside the reported 2012 three-year deal | Recover the scheduled 2013 Jaguars row and termination assumptions; a later charge does not establish January savings |

These leads neither execute nor recommend a release. A missing or disputed savings figure limits that transaction's budget calculation, not unrelated scouting, negotiations or ordinary football planning.

## What the sheet can support now

The file is sufficient for Stone/Caldwell to:

- understand that Jacksonville is entering the offseason with meaningful financial flexibility rather than a cap crisis;
- identify which existing contracts consume real resources;
- compare a proposed free-agent contract with the club's January planning room;
- screen veteran transaction scenarios, then verify the specific contract terms before booking a cap effect;
- discuss restructuring, release or trade scenarios without pretending salary cap is irrelevant;
- avoid confusing coaching payroll with player-cap accounting.

## What still requires reconciliation before claiming an exact post-transaction club balance

Before reporting a **penny-accurate** new cap-space total, reconcile:

1. every contract/tender that enters the Top-51;
2. reserve/future deals that actually count in the Top-51;
3. already-booked dead money from prior transactions;
4. applicable club credits/debits and other countable charges, without deducting league benefits a second time;
5. the official rather than rounded carryover election and the cap basis of the starting room estimate;
6. any branch-specific transaction already executed;
7. any guarantee, grievance or June-1 treatment specific to the transaction being modeled;
8. the effective date and pre-divergence applicability of every annual component used.

### Updating planning room after a branch transaction

Use the identity **change in room = change in adjusted cap minus change in total counted team charges**. Calculate those charges before and after the move under the same accounting rules and effective date. This captures Top-51 displacement, bonus amounts that remain countable outside the Top-51, dead money and other adjustments without counting a component twice.

- A signing's incremental charge is its effect on counted team salary, not its total contract value or average annual value. Show any displaced amount separately.
- A release's table delta is only a gross starting point. Identify the replacement counted amount and any guarantee or timing difference before estimating net relief.
- Track future-year cap charges and current cash commitments separately; a restructure can improve present room while increasing future charges.
- Record the date, source, transaction terms, before/after treatment and unresolved inputs in the transaction's existing ledger. Recompute after each move; do not stack multiple moves against the same displaced contract.
- Retain full precision in supported individual rows. Display club room as approximate, normally to the nearest $0.1M, while the starting balance remains a rounded estimate. Keep any draft, roster-completion or operating reserve visibly separate from booked liabilities.

### Operating rule for the simulation

**Do not block ordinary football decisions merely because the complete club worksheet is unavailable.**

- Before March 12: use the **~$22.1M January planning estimate** for internal strategy and price ranges. Contact with prospective UFAs under another club's contract must follow the March 9-12 agent-only window; their new-club contracts cannot be executed before March 12 at 4:00 p.m. ET.
- Once the league year opens: update the cap basis and branch obligations using then-available evidence. Adopt a later real-club room figure only after reconciling the transactions and assumptions included in it.
- For a transaction with a sourced individual cap effect, apply its **net counted change**, including displacement and timing, to the current planning figure. Unknown savings remain unbooked rather than assumed to be zero or automatically favorable.
- Label the resulting club room as an **estimate** unless the full Top-51/adjusted-cap worksheet has been reconciled.
- If affordability depends on unresolved charges, unverified savings or complicated guarantees/dead money, reconcile those specific inputs before execution. No numerical uncertainty band has been established; do not invent one.

This keeps the simulation financially disciplined without pretending an NFL club becomes incapable of acting until every historical accounting line has been reconstructed.
