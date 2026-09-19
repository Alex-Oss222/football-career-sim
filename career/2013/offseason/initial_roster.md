# Jacksonville Jaguars — Initial Roster Snapshot

> **Historical snapshot:** This file preserves the January 15 starting inventory. For the completed March 12 signings, re-signings and releases, use the [current roster](../roster.md) and [signing ledger](free_agency/signings.md). Historical active/IR labels below do not establish current status.

**As of:** January 15, 2013  
**Mode:** real pre-divergence facts; counterfactual personnel decisions begin after this snapshot  
**Status:** `POPULATED WITH NOTED SOURCE LIMITATIONS — TRANSACTION-LEDGER RECONCILIATION STILL REQUIRED`

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

**Inventory counts:** 53 final-week active names; 10 separately identified reserve/injured cases; 63 total listed persons. These are disjoint in this file. The latter two totals are not asserted to equal the club’s complete January 15 offseason control list because practice-squad expirations and reserve/future contracts require a dated transaction source.

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
