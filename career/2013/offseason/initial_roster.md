# Jacksonville Jaguars — Initial Roster Snapshot

**As of:** January 15, 2013  
**Mode:** real pre-divergence facts; counterfactual personnel decisions begin after this snapshot  
**Status:** `OPERATING INITIALIZATION SNAPSHOT — ACTIVE/RESERVE SPINE VERIFIED; MARCH 12 CONTRACT-RIGHTS LAYER ADDED; FUTURES/PRACTICE-SQUAD EDGE CASES STILL OPEN`

## Sources and evidence boundary

- **Primary roster spine:** NFLverse's archived NFL weekly-roster export, `roster_weekly_2012.csv`, filtered to Jacksonville, regular-season Week 17, status `ACT`. The source preserves NFL identifiers, listed position, jersey and experience. [NFLverse weekly-rosters release](https://github.com/nflverse/nflverse-data/releases/tag/weekly_rosters)
- **Independent roster/role check:** Pro Football Reference's 2012 Jacksonville roster table as redistributed without alteration in NFLverse's `pfr_rosters.csv`; games and starts below are real 2012 facts, not evaluations. [NFLverse miscellaneous-data release](https://github.com/nflverse/nflverse-data/releases/tag/misc) and [PFR 2012 Jaguars roster](https://www.pro-football-reference.com/teams/jax/2012_roster.htm)
- **Contract cross-check:** OverTheCap historical-contract export, used only for contract totals that can be matched unambiguously. [NFLverse contracts release](https://github.com/nflverse/nflverse-data/releases/tag/contracts)
- **Rules:** the $123,000,000 league cap and 2013 roster/accounting rules are already independently sourced in `foundation/02_League_Era_and_Sourcebook.md` §11 and `library/2013_league_calendar_and_financial_rules.md`.

**Cutoff:** January 15, 2013, the counterfactual Stone hire date. The final 2012 active roster is the last clean NFL roster snapshot available in the archived weekly feed. Reserve/injured designations are separately labeled because the export does not retain every reserve-list player in its Week 17 active slice. No actual transaction, release, re-signing, draft choice, staff hire, or player outcome after the divergence point was imported.

## Two-pass verification record

### Pass 1 — research

The NFL weekly export supplied the 53 unique names carrying an `ACT` row at Week 17 after transaction-duplicate rows were removed. The PFR roster supplied the prior-season participation record and exposed reserve-list players who were absent from the active-only slice.

### Pass 2 — skeptical re-check

Every active-roster name was re-matched by name against the independent PFR roster; every games/starts entry comes from that second dataset. Ten season-ending reserve/injured cases visible in the season roster were added as a separate, expressly provisional bucket rather than silently counted as active. This pass does **not** claim an exact January 15 reserve/futures inventory: a dated official transaction ledger was not available in the environment. That omission is stated, not estimated.

## How to read the January roster

Three different concepts must not be collapsed into one list:

1. **Week 17 active roster:** the 53-player game-roster spine at the end of the 2012 regular season.
2. **Reserve/injured and other reserve control:** players still tied to Jacksonville but absent from that Week 17 active slice.
3. **2013 contractual rights:** whether a player's existing contract continues into the 2013 league year or expires March 12 as UFA/RFA/ERFA.

A player can be on Jacksonville's January football-control list and still be scheduled for free agency in March. Conversely, a final-week active player is not automatically under contract for 2013.

No actual post-January-15 release, signing, waiver claim, re-signing or draft result is imported.

## March 12, 2013 expiring-rights board

Jacksonville's own February 5 offseason preview published the players scheduled to become free agents March 12. That article postdates Stone's hire, but it verifies **contract expiration terms that were already fixed on January 15**. It is used only for the pre-existing rights status, never for what the real Jaguars later chose to do.

Source: https://www.jaguars.com/news/the-offseason-begins-9537328

| Player | Position | March 12 status | January 15 treatment |
|---|---|---|---|
| Kyle Bosworth | LB | Scheduled free agent | Club may negotiate before expiration; no 2013 contract assumed |
| Eben Britton | OL | Scheduled free agent | Same |
| John Chick | DE | **ERFA** | Jacksonville can retain rights with qualifying tender; no tender assumed yet |
| Derek Cox | CB | Scheduled free agent | No re-signing or departure assumed |
| John Estes | C | **RFA** | Not in the Week 17 active spine below; still part of the contract-rights board |
| Rashad Jennings | RB | Scheduled free agent | Not in the Week 17 active spine below; still part of the contract-rights board |
| Greg Jones | FB | Scheduled free agent | No re-signing or departure assumed |
| Terrance Knighton | DT | Scheduled free agent | No re-signing or departure assumed |
| Rashean Mathis | CB | Scheduled free agent | No re-signing or departure assumed |
| Brad Meester | C | Scheduled free agent | No re-signing or departure assumed |
| William Middleton | CB | Scheduled free agent | Not in the Week 17 active spine below; still part of the contract-rights board |
| Antwaun Molden | CB | Scheduled free agent | No re-signing or departure assumed |
| Jordan Palmer | QB | Scheduled free agent | No re-signing or departure assumed |
| Jalen Parmele | RB | Scheduled free agent | Reserve/injured season-end evidence does not create a 2013 contract |
| Zach Potter | TE | **RFA** | Jacksonville can tender or allow market process; no tender assumed |
| George Selvie | DE | **RFA** | Same |
| Jordan Shipley | WR | **RFA** | Same |
| Daryl Smith | LB | Scheduled free agent | No re-signing or departure assumed |
| Keith Toston | RB | **ERFA** | Jacksonville can retain rights with qualifying tender; no tender assumed |
| Steve Vallos | C | Scheduled free agent | No re-signing or departure assumed |

**Important:** "scheduled free agent" above follows the Jaguars' own article. Where the article explicitly identifies RFA or ERFA status, that classification controls. No tender, franchise tag, re-signing or market result has happened in this branch yet.

## Continuing-contract core entering 2013 planning

The following prominent players have source-backed contracts that continue into the 2013 league year unless Jacksonville later makes a branch transaction:

| Player | Pos. | 2013 contractual position at initialization |
|---|---|---|
| Blaine Gabbert | QB | Under rookie contract; 2013 scheduled cap $3.273M; starting job **not guaranteed** |
| Chad Henne | QB | Under 2012 two-year veteran contract; 2013 scheduled cap $4.650M |
| Maurice Jones-Drew | RB | Under veteran extension through 2013; scheduled cap $6.800M |
| Cecil Shorts | WR | Under rookie contract; scheduled cap $0.729M |
| Justin Blackmon | WR | Under rookie contract; scheduled cap $3.266M |
| Laurent Robinson | WR | Under 2012 five-year agreement at the cutoff; no later real release imported |
| Marcedes Lewis | TE | Under veteran contract; scheduled cap $5.750M |
| Eugene Monroe | OT | Final year of rookie contract; scheduled opening cap about $5.748M |
| Uche Nwaneri | G | Under veteran extension; scheduled cap $5.895M |
| Will Rackley | G | Under rookie contract; scheduled cap $0.795M |
| Andre Branch | DE | Under rookie contract; scheduled cap $1.157M |
| Jason Babin | DE | Existing waiver/contract obligation continues into 2013 at the cutoff |
| Tyson Alualu | DL | Under rookie contract; scheduled cap $3.615M |
| Paul Posluszny | LB | Under veteran contract; scheduled cap $8.500M |
| Russell Allen | LB | Under veteran contract; scheduled cap $2.817M |
| Mike Harris | CB | Under rookie contract; scheduled cap $0.509M |
| Chris Prosinski | S | Under rookie contract; scheduled cap $0.720M |
| Dawan Landry | S | Under veteran contract at cutoff; later real release is not imported |
| Dwight Lowery | S | Under veteran contract; scheduled obligation about $3.875M |
| Josh Scobee | K | Under veteran contract; scheduled cap $3.288M |
| Bryan Anger | P | Under rookie contract; scheduled cap $0.676M |

This is not a keep/cut recommendation. It is the contractual starting condition. Player evaluation occurs after initialization under the ordinary roster process.

## Position-group inventory at the snapshot

The table below is an administrative count of the names in this file, not a depth-chart quality judgment.

| Group | Active-spine / reserve names visible here | Immediate contract-planning issue |
|---|---:|---|
| Quarterback | 3 | Gabbert and Henne under contract; Palmer scheduled free agent |
| Running back / fullback | 7 | Jones, Parmele and Toston among March expirations; Jones-Drew under contract |
| Wide receiver | 7 | Shipley scheduled RFA; Robinson/Blackmon/Shorts under continuing deals |
| Tight end | 4 | Potter scheduled RFA; Lewis under major veteran contract |
| Offensive line | 11 | Monroe/Nwaneri/Rackley continuing; Britton/Meester/Vallos plus Estes rights require March decisions |
| Defensive line / edge | 11 | Knighton, Chick, Selvie among expirations; several continuing rookie/veteran deals |
| Linebacker | 6 | Daryl Smith/Bosworth expirations; Posluszny/Allen continuing |
| Defensive back | 11 | Cox/Mathis/Molden/Middleton expirations; multiple continuing veteran contracts |
| Specialists | 3 | Scobee, Anger and Cain in snapshot |

Counts reflect the listed active/reserve register and the separately noted expiring-rights players. They are not asserted as the exact 90-man offseason roster.

## Player register

This is an administrative roster inventory, **not a depth chart or talent evaluation**. Jersey numbers are the numbers shown in the final 2012 source and are not guaranteed for 2013. “Experience” reproduces the NFL feed field (zero means rookie in that feed).

| Player | Pos. | No. | Jan. 15 control/status basis | NFL experience entering snapshot | Verified 2012 role | Stable source key |
|---|---:|---:|---|---:|---|---|
| Blaine Gabbert | QB | 11 | Reserve/injured at season close — exact Jan. 15 list designation requires transaction-ledger confirmation | 1 | 2012: 10 games, 10 starts | GabbBl00 |
| Chad Henne | QB | 7 | 2012 final active roster | 4 | 2012: 10 games, 6 starts | 00-0026197 |
| Jordan Palmer | QB | 5 | 2012 final active roster | 5 | 2012 role not independently tabulated | 00-0025592 |
| Jalen Parmele | RB | 34 | Reserve/injured at season close — exact Jan. 15 list designation requires transaction-ledger confirmation | 4 | 2012: 11 games, 2 starts | ParmJa00 |
| Jonathan Grimes | RB | 43 | 2012 final active roster | 0 | 2012: 2 games, 2 starts | 00-0029510 |
| Keith Toston | RB | 35 | 2012 final active roster | 2 | 2012: 5 games, 1 start | 00-0027257 |
| Maurice Jones-Drew | RB | 32 | Reserve/injured at season close — exact Jan. 15 list designation requires transaction-ledger confirmation | 6 | 2012: 6 games, 5 starts | DrewMa00 |
| Richard Murphy | RB | 39 | 2012 final active roster | 1 | 2012: 5 games, 0 starts | 00-0028416 |
| Greg Jones | FB | 33 | 2012 final active roster | 8 | 2012: 12 games, 4 starts | 00-0022897 |
| Montell Owens | FB | 24 | 2012 final active roster | 6 | 2012: 13 games, 4 starts | 00-0024103 |
| Cecil Shorts | WR | 84 | Reserve/injured at season close — exact Jan. 15 list designation requires transaction-ledger confirmation | 1 | 2012: 14 games, 9 starts | ShorCe00 |
| Jerrell Jackson | WR | 18 | 2012 final active roster | 0 | 2012: 1 games, 0 starts | 00-0029511 |
| Jordan Shipley | WR | 16 | 2012 final active roster | 2 | 2012: 6 games, 2 starts | 00-0027687 |
| Justin Blackmon | WR | 14 | 2012 final active roster | 0 | 2012: 16 games, 14 starts | 00-0029707 |
| Laurent Robinson | WR | 81 | Reserve/injured at season close — exact Jan. 15 list designation requires transaction-ledger confirmation | 5 | 2012: 7 games, 4 starts | RobiLa01 |
| Mike Brown | WR | 12 | 2012 final active roster | 0 | 2012: 2 games, 1 start | 00-0029155 |
| Toney Clemons | WR | 17 | 2012 final active roster | 0 | 2012: 4 games, 0 starts | 00-0029204 |
| Allen Reisner | TE | 87 | 2012 final active roster | 1 | 2012: 2 games, 2 starts | 00-0028267 |
| Isaiah Stanback | TE | 86 | 2012 final active roster | 5 | 2012: 6 games, 0 starts | 00-0025490 |
| Marcedes Lewis | TE | 89 | 2012 final active roster | 6 | 2012: 16 games, 15 starts | 00-0024243 |
| Zach Potter | TE | 88 | 2012 final active roster | 3 | 2012: 16 games, 5 starts | 00-0026658 |
| Cameron Bradfield | T | 78 | 2012 final active roster | 1 | 2012: 14 games, 12 starts | 00-0028401 |
| Eugene Monroe | T | 75 | 2012 final active roster | 3 | 2012: 16 games, 16 starts | 00-0026984 |
| Guy Whimper | T | 68 | 2012 final active roster | 6 | 2012: 16 games, 6 starts | 00-0024344 |
| Austin Pasztor | G | 67 | 2012 final active roster | 0 | 2012: 3 games, 3 starts | 00-0029076 |
| Eben Britton | G | 73 | 2012 final active roster | 3 | 2012: 11 games, 5 starts | 00-0027015 |
| Mark Asper | G | 72 | 2012 final active roster | 0 | 2012: 1 games, 0 starts | 00-0029296 |
| Uche Nwaneri | G | 77 | 2012 final active roster | 5 | 2012: 15 games, 15 starts | 00-0025536 |
| Will Rackley | G | 65 | Reserve/injured at season close — exact Jan. 15 list designation requires transaction-ledger confirmation | Unknown | 2012 role not independently tabulated |  |
| Brad Meester | C | 63 | 2012 final active roster | 12 | 2012: 16 games, 16 starts | 00-0018956 |
| Mike Brewster | C | 60 | Reserve/injured at season close — exact Jan. 15 list designation requires transaction-ledger confirmation | Rook | 2012: 12 games, 7 starts | BrewMi00 |
| Steve Vallos | C | 66 | 2012 final active roster | 5 | 2012: 2 games, 1 start | 00-0025619 |
| Andre Branch | DE | 90 | Reserve/injured at season close — exact Jan. 15 list designation requires transaction-ledger confirmation | Rook | 2012: 13 games, 3 starts | BranAn00 |
| Austen Lane | DE | 92 | 2012 final active roster | 2 | 2012: 11 games, 7 starts | 00-0027752 |
| George Selvie | DE | 91 | 2012 final active roster | 2 | 2012: 9 games, 0 starts | 00-0027818 |
| Jason Babin | DE | 58 | 2012 final active roster | 8 | 2012: 5 games, 5 starts | 00-0022695 |
| Jeremy Mincey | DE | 94 | 2012 final active roster | 6 | 2012: 16 games, 16 starts | 00-0024405 |
| John Chick | DE | 97 | 2012 final active roster | 6 | 2012: 8 games, 0 starts | 00-0024058 |
| C.J. Mosley | DT | 99 | 2012 final active roster | 7 | 2012: 16 games, 13 starts | 00-0023624 |
| D'Anthony Smith | DT | 95 | Reserve/injured at season close — exact Jan. 15 list designation requires transaction-ledger confirmation | 1 | 2012: 8 games, 0 starts | SmitDA99 |
| Jeris Pendleton | DT | 98 | 2012 final active roster | 0 | 2012: 4 games, 0 starts | 00-0029622 |
| Jerome Long | DT | 70 | 2012 final active roster | 0 | 2012 role not independently tabulated | 00-0029306 |
| Terrance Knighton | DT | 96 | 2012 final active roster | 3 | 2012: 16 games, 4 starts | 00-0027046 |
| Tyson Alualu | DT | 93 | 2012 final active roster | 2 | 2012: 16 games, 16 starts | 00-0027862 |
| Kyle Bosworth | MLB | 56 | 2012 final active roster | 2 | 2012: 16 games, 5 starts | 00-0027499 |
| Paul Posluszny | MLB | 51 | 2012 final active roster | 5 | 2012: 16 games, 16 starts | 00-0025421 |
| Brandon Marshall | OLB | 53 | 2012 final active roster | 0 | 2012: 5 games, 0 starts | 00-0029620 |
| Daryl Smith | OLB | 52 | 2012 final active roster | 8 | 2012: 2 games, 2 starts | 00-0022839 |
| Julian Stanford | OLB | 57 | 2012 final active roster | 0 | 2012: 16 games, 6 starts | 00-0029061 |
| Russell Allen | OLB | 50 | 2012 final active roster | 3 | 2012: 16 games, 16 starts | 00-0026605 |
| Aaron Ross | CB | 31 | 2012 final active roster | 5 | 2012: 14 games, 9 starts | 00-0025407 |
| Antwaun Molden | CB | 36 | 2012 final active roster | 4 | 2012: 3 games, 0 starts | 00-0026219 |
| Derek Cox | CB | 21 | 2012 final active roster | 3 | 2012: 12 games, 12 starts | 00-0027047 |
| Kevin Rutland | CB | 22 | 2012 final active roster | 1 | 2012: 13 games, 1 start | 00-0028420 |
| Mike Harris | CB | 20 | 2012 final active roster | 0 | 2012: 15 games, 6 starts | 00-0029610 |
| Rashean Mathis | CB | 27 | 2012 final active roster | 9 | 2012: 12 games, 4 starts | 00-0022080 |
| Chris Prosinski | FS | 42 | 2012 final active roster | 1 | 2012: 16 games, 7 starts | 00-0028059 |
| Antwon Blake | SS | 38 | 2012 final active roster | 0 | 2012: 16 games, 0 starts | 00-0029050 |
| Dawan Landry | SS | 26 | 2012 final active roster | 6 | 2012: 16 games, 16 starts | 00-0024360 |
| Dwight Lowery | S | 25 | Reserve/injured at season close — exact Jan. 15 list designation requires transaction-ledger confirmation | 4 | 2012: 9 games, 9 starts | LoweDw99 |
| Josh Scobee | K | 10 | 2012 final active roster | 8 | 2012: 16 games, 0 starts | 00-0022874 |
| Bryan Anger | P | 19 | 2012 final active roster | 0 | 2012: 16 games, 0 starts | 00-0029692 |
| Jeremy Cain | LS | 48 | 2012 final active roster | 8 | 2012: 16 games, 0 starts | 00-0022502 |

**Inventory counts:** 53 final-week active names; 10 separately identified reserve/injured cases; 63 total listed persons in the active/reserve evidence spine. The March 12 rights board additionally identifies John Estes, Rashad Jennings and William Middleton, who are not present in that 63-name spine but whose expiring Jacksonville contract rights are independently documented. None of these totals is asserted to equal the exact January 15 90-man offseason control list because reserve/future and practice-squad contract activity still requires a dated transaction ledger.

## Roster decisions reserved for the branch

At initialization, the following are **questions**, not answers:

- whether to tender or re-sign any March 12 free agent;
- whether to retain, release, trade or restructure any player already under contract;
- whether Gabbert or Henne begins the offseason as the leading quarterback;
- whether Jones-Drew's final contract year is retained, extended or otherwise addressed;
- whether expensive veteran contracts fit the new program;
- which reserve/injured players are medically available when offseason work begins;
- which reserve/future players occupy offseason roster spots;
- how the No. 2 draft position or free agency changes any position room.

The actual 2013 Jaguars subsequently made many of these decisions. Those outcomes are quarantined. Stone and Caldwell make them fresh in this branch under their agreed authority split.

## Staff and football-operations baseline

| Person | Snapshot role | Evidence status | Initialization treatment |
|---|---|---|---|
| Shad Khan | Owner | Verified public fact | Ownership authority; not a subordinate coach |
| David Caldwell | General manager | Verified public fact | Active football executive and Stone’s primary football counterpart |
| Mel Tucker | 2012 defensive coordinator / assistant head coach | Verified public fact from the permitted pre-hire market source | Incumbent status only; no post-hire appointment inferred |
| Bob Bratkowski | 2012 offensive coordinator | Supported by 2012 staff directories | Prior staff only; continuation unknown |
| John Bonamego | 2012 special-teams coordinator | Supported by 2012 staff directories | Prior staff only; continuation unknown |
| Sylvester Croom | 2012 running-backs coach | Supported by 2012 staff directories | Prior staff only; continuation unknown |
| Jerry Sullivan | 2012 wide-receivers coach | Supported by 2012 staff directories | Prior staff only; continuation unknown |
| Bobby Johnson | 2012 tight-ends coach | Supported by 2012 staff directories | Prior staff only; continuation unknown |
| Andy Heck | 2012 offensive-line coach | Supported by 2012 staff directories | Prior staff only; continuation unknown |
| Joe Cullen | 2012 defensive-line coach | Supported by 2012 staff directories | Prior staff only; continuation unknown |
| Mark Duffner | 2012 linebackers coach | Supported by 2012 staff directories | Prior staff only; continuation unknown |
| Tony Oden | 2012 secondary coach | Supported by 2012 staff directories | Prior staff only; continuation unknown |
| Tom Myslinski | 2012 strength and conditioning coach | Supported by 2012 staff directories | Prior staff only; continuation unknown |

**Important:** listing a 2012 coach does not appoint or retain him in the counterfactual Stone staff. The accepted contract gives Stone staff-selection authority; each appointment must be a later user-controlled or authorized event. No actual Gus Bradley-era staff outcome was consulted. [Pro Football Reference 2012 Jaguars staff/roster page](https://www.pro-football-reference.com/teams/jax/2012_roster.htm)
