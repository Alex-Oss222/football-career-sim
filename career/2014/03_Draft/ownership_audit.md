# 2014 pick ownership audit

**Checkpoint:** February 2, 2014, [draft ownership correction](ownership_audit.md). Research completed September 29, 2026 UTC. Covers all 32 original clubs in all seven rounds, 224 ordinary assets. Compensatory allocations are a separate March 24 event.

The user authorized a league-wide reconciliation. Historical trade indexes supplied the candidate list; team releases, reporting and the closed branch records decide which consideration applies. This restores costs for acquisitions already accepted in the 2013 baseline. It does not import real midseason trades that contradict the branch, future 2014 transactions, actual draft selections, or actual compensatory recipients.

<!-- event-record: {"closure": {"checkpoint": "Canonical correction - February 2, 2014 - Draft coin flip and league pick ownership reconciled", "sequence": 81, "through": "2014-02-02"}, "date": "2014-02-02", "id": "2014-02-02-draft-coin-flip-and-league-pick-ownership-reconciled", "kind": "technical", "status": "closed", "summary": "Draft coin flip and league pick ownership reconciled."} -->

## Coin result

RANDOM.ORG returned **tails**, so **Indianapolis 14, Green Bay 15**. Heads/Green Bay and tails/Indianapolis were assigned before the only draw. The recorded website time is **2026-09-29 01:42:47 UTC**. [Structured receipt](coin_flip.json), [screenshot](coin_flip_2026-09-29.jpg). The website result URL generates a fresh draw when reopened, so the saved receipt and screenshot are the evidence. The simulation clock remains February 2, 2014.

## Source and verification method

First pass enumerated pre-checkpoint transfers in the [2014 pick transaction index](https://prosportstransactions.com/football/DraftTrades/Years/2014.htm), its [2013 companion](https://www.prosportstransactions.com/football/DraftTrades/Years/2013.htm), and the [2014 draft trade index](https://en.wikipedia.org/wiki/2014_NFL_draft). These are discovery indexes, not authority for branch owners. Second pass separately searched each trade, checked source pairs below and compared accepted opening lineups with closed receipts. Team transaction feeds sometimes display a day earlier than announcements; announcement dates are used, with discrepancies noted. Later retrospectives supply only original transaction terms, never later football outcomes.

The accepted baseline is [2013 depth charts](../../../library/2013_week1_depth_charts.md) and its [data](../../../library/data/2013_week1_depth_charts.json). Branch game evidence is in [closed receipts](../../2013/stats/game_receipts). The 2013 season results are used only for contract conditions and draft ordering, never as talent ratings.

## Reconciled transferred assets

| Original asset | Owner | Consideration | Branch treatment |
|---|---|---|---|
| 2014 R1 Washington Redskins | Jacksonville Jaguars | User-corrected Cousins trade; [Cousins trade correction](../../2013/trades/trades.md) | [Authority](../../2013/trades/trades.md) |
| 2014 R2 Jacksonville Jaguars | Washington Redskins | User-corrected Cousins trade; [Cousins trade correction](../../2013/trades/trades.md) | [Authority](../../2013/trades/trades.md) |
| 2015 R2 Jacksonville Jaguars | Washington Redskins | User-corrected Cousins trade; [Cousins trade correction](../../2013/trades/trades.md); unconditional, slot unknown | [Authority](../../2013/trades/trades.md) |
| 2014 R7 Carolina Panthers | San Francisco 49ers | Pre-divergence Colin Jones trade, reported August 31, 2012 | [Authority](../../../library/2014_draft_order_verification.md) |
| 2014 R5 Detroit Lions | Jacksonville Jaguars | Mike Thomas: Inherited pre-divergence consideration; [draft ownership correction](ownership_audit.md) | [Authority](#thomas) |
| 2014 R7 Indianapolis Colts | St. Louis Rams | Josh Gordy: Inherited pre-divergence consideration; [draft ownership correction](ownership_audit.md) | [Authority](#gordy) |
| 2014 R2 Kansas City Chiefs | San Francisco 49ers | Alex Smith: KC finished 9-7 in the branch; meets .500 escalation, third retained; [draft ownership correction](ownership_audit.md) | [Authority](#smith) |
| 2014 R3 Tennessee Titans | San Francisco 49ers | Justin Hunter draft trade: Consideration for accepted 2013 draft acquisition; [draft ownership correction](ownership_audit.md) | [Authority](#hunter) |
| 2014 R3 Pittsburgh Steelers | Cleveland Browns | Shamarko Thomas draft trade: Consideration for accepted 2013 draft acquisition; [draft ownership correction](ownership_audit.md) | [Authority](#shamarko) |
| 2014 R3 Seattle Seahawks | Minnesota Vikings | Percy Harvin: Consideration for accepted 2013 background acquisition; [draft ownership correction](ownership_audit.md) | [Authority](#harvin) |
| 2014 R4 Indianapolis Colts | Cleveland Browns | Montori Hughes draft trade: Consideration for accepted 2013 draft acquisition; [draft ownership correction](ownership_audit.md) | [Authority](#hughes) |
| 2014 R5 Oakland Raiders | Seattle Seahawks | Matt Flynn: Unconditional 2014 portion; 2015 condition not settled here; [draft ownership correction](ownership_audit.md) | [Authority](#flynn) |
| 2014 R6 Tampa Bay Buccaneers | Chicago Bears | Gabe Carimi: Consideration for accepted 2013 background acquisition; [draft ownership correction](ownership_audit.md) | [Authority](#carimi) |
| 2014 R6 Dallas Cowboys | Kansas City Chiefs | Edgar Jones: 2014 sixth for Jones and KC seventh; [draft ownership correction](ownership_audit.md) | [Authority](#jones) |
| 2014 R7 Kansas City Chiefs | Dallas Cowboys | Edgar Jones: Counterpart of Dallas sixth in same Jones trade; [draft ownership correction](ownership_audit.md) | [Authority](#jones) |
| 2014 R7 Baltimore Ravens | Indianapolis Colts | A.Q. Shipley: Roster condition met in accepted branch Week 1 lineup; [draft ownership correction](ownership_audit.md) | [Authority](#shipley) |
| 2014 R7 Arizona Cardinals | Oakland Raiders | Carson Palmer: Thirteen-start condition met; branch QB1 and sole passer in all sixteen games; [draft ownership correction](ownership_audit.md) | [Authority](#palmer) |
| 2014 R7 New Orleans Saints | San Francisco 49ers | Parys Haralson: Roster condition met in accepted branch Week 1 lineup; [draft ownership correction](ownership_audit.md) | [Authority](#haralson) |

Jacksonville has **eight** ordinary 2014 picks. Detroit’s fifth is inherited from 2012 and was omitted before this audit. The Cousins exception remains exactly as authorized in [Cousins trade correction](../../2013/trades/trades.md). Nothing awards St. Louis another pick for losing its historical Washington claim.

## Conditional claims

| Claim | Current allocation | Potential beneficiary | Decision |
|---|---|---|---|
| [revis](#revis) | Tampa Bay Buccaneers: R3/R4 | New York Jets | One pick to NYJ: R3 if Revis remains on TB roster March 13, otherwise R4. Both alternatives reserved. |
| [benn](#benn) | Philadelphia Eagles: R1/R2/R3/R4/R5/R6/R7 | Tampa Bay Buccaneers | One conditional compensation claim to TB; round and trigger undisclosed. Scope hold until terms verified; not seven debts. |
| [rosario](#rosario) | Chicago Bears: R7 | Dallas Cowboys | Conditional seventh to DAL; playing-time threshold unverified. Branch appearances alone do not prove the clause. |

There are **three claims**, covering ten potentially affected original assets, not ten transferred picks. The register holds each asset with its original club and separately identifies the claim. `require_clear_ownership` rejects those assets. For Benn, all seven rounds are conservatively held because no round was disclosed. No claim is silently waived. Rosario is held because a generic report of a seventh-round trade conflicts with contemporaneous reporting that it was conditional. Sixteen game appearances are not proof of an undisclosed snap threshold.

At March 13, evaluate Revis against the dated branch roster, convey exactly one of Tampa Bay’s third/fourth, release the other and record the decision with its transaction history. For Benn and Rosario, recover the clause and adequate branch evidence before conveyance or release. Neither missing term can honestly be settled by importing real 2014 outcomes.

## Historical trades rejected by branch evidence

| Historical candidate | Branch evidence | Asset treatment |
|---|---|---|
| Trent Richardson, Cleveland to Indianapolis, September 18, 2013 | Cleveland RB1 and Cleveland participant in all sixteen closed regular-season games | IND R1 remains Indianapolis; no Cleveland claim |
| Isaac Sopoaga, Philadelphia to New England, October 29, 2013 | Philadelphia participant in all sixteen games, including Week 17 | NE R5 remains New England; PHI R6 stays Philadelphia, subject only to Benn hold |
| Jon Beason, Carolina to NY Giants, October 4, 2013 | Carolina participant in all sixteen games | NYG R7 remains New York Giants |
| Levi Brown, Arizona to Pittsburgh, October 2, 2013 | Arizona LT1 and participant in all sixteen games | No conditional Pittsburgh payment to Arizona |
| Eugene Monroe, Jacksonville to Baltimore, October 2013 | Jacksonville controlled roster and season receipts | BAL R4 and R5 remain Baltimore |
| D’Anthony Smith, Jacksonville to Seattle, August 31, 2013 | Jacksonville practice squad in controlling roster; no branch trade recorded | No Seattle conditional payment to Jacksonville |
| Washington 2014 first, historical RGIII consideration to St. Louis | User correction and [Cousins trade correction](../../2013/trades/trades.md) | JAX owns Washington first, No. 13; no duplicate Rams owner |

Historical candidates were cross-checked against team/transaction reporting and branch receipts, not reversed based on later real-life non-conveyance. The [Seattle trade history](https://www.seahawks.com/team/all-time-trades) also identifies the D’Anthony Smith conditional deal. The [Browns](https://www.clevelandbrowns.com/team/transactions/2013), [Cardinals](https://www.azcardinals.com/team/transactions/2013) and [Eagles](https://www.pro-football-reference.com/teams/phi/2013_trades.htm) transaction records supply additional historical cross-checks.

The proposed Eric Wright deal is not a conveyed pick: the historical agreement was voided before the accepted opening baseline. [Buccaneers transaction log](https://www.buccaneers.com/team/transactions/2013); [NFL report](https://www.nfl.com/news/eric-wright-fails-his-49ers-physical-cut-by-buccaneers-0ap1000000219568). No branch transaction or pick debt is recorded for that failed agreement.

Cam Johnson, Caesar Rayford, Greg Salas, Sean Lissemore and Bryant McKinnie consideration belongs to other draft years, not an extra 2014 pick. Flynn’s separate 2015 condition is not resolved here. The 2015 league-wide inventory requires its own audit. Any Schaub, Sproles, Mike Williams, Pryor or 2014 draft-day transaction is after this checkpoint and is not booked now.

## Conditions already satisfied in this branch

- **Alex Smith:** Kansas City finished 9-7 in the closed branch standings. The reported .500-or-better escalator therefore conveys KC R2, not both R2 and R3.
- **Carson Palmer:** Arizona lists Palmer at QB1. He is its sole recorded passer in all sixteen regular-season receipts. Inferring sixteen starts from that lineup and the closed engine’s QB1-only passing supports the thirteen-start clause. This is an explicit inference because compact receipts have no separate starts counter. No real 2013 start count is imported.
- **Shipley and Haralson:** the accepted opening roster and Week 1 active receipt place each with his receiving club. The reported roster conditions are satisfied. Subsequent branch injuries do not undo an opening-roster condition.

## Trade sources and skeptical recheck

### thomas

**Mike Thomas; original transaction 2012-10-30.** [Jaguars, Caldwell: Roster not in fire sale (2013-10-03)](https://www.jaguars.com/news/caldwell-roster-not-in-fire-sale-11406545). Independent re-search / clarification: [NFL, Mike Thomas cut by Detroit Lions after short tenure (2013-08-19)](https://www.nfl.com/news/mike-thomas-cut-by-detroit-lions-after-short-tenure-0ap1000000231765).

Detroit’s 2014 fifth is confirmed. The contemporary announcement was October 30; Detroit’s retrospective log says October 31 and the migrated Jaguars feed shows October 29. This date discrepancy does not affect ownership: all precede divergence. [Detroit historical trade log](https://static.www.nfl.com/league/apps/league-site/media-guides/2021/DET.pdf).

### gordy

**Josh Gordy; original transaction 2012-08-21.** [Colts, Colts receive CB Josh Gordy (2012-08-21)](https://www.colts.com/news/colts-receive-cb-josh-gordy-8008317). Independent re-search / clarification: [Colts, Mailbag (2014-01-29), seventh-round clarification](https://www.colts.com/news/colts-mailbag-january-29-2014-part-one-12531108).

The initial announcement leaves the round undisclosed; the January mailbag explicitly identifies Indianapolis’s seventh. Some indexes date the transfer August 22; the Colts announcement is August 21. Both predate divergence.

### smith

**Alex Smith; original transaction 2013-03-12.** [49ers, Acquire picks in Alex Smith trade (2013-03-12)](https://www.49ers.com/news/49ers-acquire-picks-in-alex-smith-trade-9684680). Independent re-search / clarification: [NFL, Alex Smith trade might produce better pick (2013-05-06)](https://www.nfl.com/news/alex-smith-trade-might-produce-better-pick-for-49ers-0ap1000000167057).

### hunter

**Justin Hunter draft trade; original transaction 2013-04-26.** [Titans, Aggressive pass lands Justin Hunter (2013-04-26)](https://www.tennesseetitans.com/news/titans-aggressive-pass-lands-justin-hunter-10021228). Independent re-search / clarification: [Titans 2014 media guide, 2013 transaction log](https://static.clubs.nfl.com/image/upload/titans/v0q1mnwdg9i2gidi3hzr.pdf).

### shamarko

**Shamarko Thomas draft trade; original transaction 2013-04-27.** [Steelers, Have 15th selection, historical 2013 draft notes (2014-05-06)](https://www.steelers.com/news/steelers-have-15th-selection-in-2014-nfl-draft-12963535). Independent re-search / clarification: [PFR, Cleveland 2013 trade register](https://www.pro-football-reference.com/teams/cle/2013_trades.htm).

### harvin

**Percy Harvin; original transaction 2013-03-12.** [Seahawks, all-time trades, 2013 section](https://www.seahawks.com/team/all-time-trades). Independent re-search / clarification: [Seahawks, On this date: Percy Harvin acquired (2015-03-12), historical terms only](https://www.seahawks.com/news/on-this-date-percy-harvin-acquired-in-trade-with-vikings-153546).

### hughes

**Montori Hughes draft trade; original transaction 2013-04-27.** [Colts, Select seven players in 2013 draft (2013-04-28)](https://www.colts.com/news/indianapolis-colts-select-seven-players-in-the-2013-nfl-draft-10042633). Independent re-search / clarification: [Colts, Mailbag (2013-12-18)](https://www.colts.com/news/colts-mailbag-december-18-2013-12184135).

### flynn

**Matt Flynn; original transaction 2013-04-01.** [Raiders, Obtain quarterback Matt Flynn (2013-04-01)](https://www.raiders.com/news/raiders-obtain-quarterback-matt-flynn-from-seattle-9811593). Independent re-search / clarification: [Seahawks, all-time trades, 2013 section](https://www.seahawks.com/team/all-time-trades).

### carimi

**Gabe Carimi; original transaction 2013-06-09.** [Buccaneers, Trade for Gabe Carimi bolsters O-line (2013-06-10)](https://www.buccaneers.com/news/trade-for-gabe-carimi-bolsters-bucs-o-line-10314128). Independent re-search / clarification: [Bears media guide, all-time trades, 2013 entries](https://static.www.nfl.com/league/apps/league-site/media-guides/2021/CHI.pdf).

### jones

**Edgar Jones; original transaction 2013-08-31.** [Cowboys, Trade Lissemore; claim Bosworth (2013-09-01), Jones transaction paragraph](https://www.dallascowboys.com/news/cowboys-trade-lissemore-claim-bosworth-off-waivers-340896). Independent re-search / clarification: [Chiefs, Trade LB Edgar Jones (2013-08-31)](https://www.chiefs.com/news/chiefs-trade-lb-edgar-jones-to-dallas-11026650).

The Chiefs announcement does not disclose the round. Dallas’s contemporaneous report gives both legs; its [December 14 report](https://www.dallascowboys.com/news/cowboys-release-lemon-add-jones-to-active-roster-345246) separately repeats the sixth/seventh exchange.

### shipley

**A.Q. Shipley; original transaction 2013-05-09.** [Ravens, Trade for center A.Q. Shipley (2013-05-09)](https://www.baltimoreravens.com/news/ravens-trade-for-center-a-q-shipley-10111061). Independent re-search / clarification: [Stampede Blue, roster-condition report quoting Russell Street Report (2013-05-10)](https://www.stampedeblue.com/2013/5/10/4319626/report-colts-will-only-get-a-7th-round-pick-if-a-q-shipley-makes).

### palmer

**Carson Palmer; original transaction 2013-04-02.** [Raiders, Trade Carson Palmer to Cardinals (2013-04-02)](https://www.raiders.com/news/raiders-trade-carson-palmer-to-cardinals-9818701). Independent re-search / clarification: [Cincy Jungle, trade report reproducing Adam Schefter terms (2013-04-02)](https://www.cincyjungle.com/2013/4/2/4174992/carson-palmer-officially-traded-to-arizona-cardinals-bengals-raiders-nfl).

### haralson

**Parys Haralson; original transaction 2013-08-26.** [49ers, Trade Parys Haralson (2013-08-27)](https://www.49ers.com/news/49ers-trade-parys-haralson-10975056). Independent re-search / clarification: [NFL, Parys Haralson dealt to Saints (2013-08-26)](https://www.nfl.com/news/parys-haralson-dealt-to-new-orleans-saints-from-49ers-0ap1000000234665).

### revis

**Darrelle Revis; original transaction 2013-04-21.** [NFL, New York Jets trade Darrelle Revis (2013-04-21)](https://www.nfl.com/news/new-york-jets-trade-darrelle-revis-to-tampa-bay-bucs-0ap1000000162196). Independent re-search / clarification: [Sports Illustrated, Peter King, Inside how the Revis trade went down (2013-04-22)](https://www.si.com/nfl/2013/04/22/darrelle-revis-peter-king-monday-morning-quarterback).

### benn

**Arrelious Benn; original transaction 2013-03-15.** [Eagles, Acquire WR Arrelious Benn (2013-03-15)](https://www.philadelphiaeagles.com/news/eagles-acquire-wr-arrelious-benn-9726231). Independent re-search / clarification: [Buccaneers, Arrelious Benn traded to Eagles (2013-03-15)](https://www.buccaneers.com/news/arrelious-benn-traded-to-eagles-9727953).

The two clubs confirm conditional 2014 compensation, but neither supplies its round or trigger. A separately searched report speculates about playing time; speculation is rejected. Real injury history and real non-conveyance do not close the branch claim.

### rosario

**Dante Rosario; original transaction 2013-09-02.** [Cowboys, Broaddus: Rosario move (2013-09-02), explicitly conditional](https://www.dallascowboys.com/news/broaddus-rosario-move-more-about-faith-in-andre-smith-340926). Independent re-search / clarification: [Dallas Morning News, Cowboys stockpile seventh-round picks (2013-09-02)](https://www.dallasnews.com/sports/cowboys/2013/09/02/cowboys-stockpile-7th-round-picks-with-trade-of-te-dante-rosario/).

The exact threshold remains unverified after the separate search. The transaction index describes a playing-time condition, while the club’s initial practice report simply says seventh. The contemporaneous conditional wording controls the conservative hold; no threshold is invented.

## All 32 clubs, all seven original assets

Each cell names the current owner. **Hold** refers to the single claim described above. No blank or blanket unverified owner remains. Future legal conveyance requires a new dated event record and register update.

| Original club | R1 | R2 | R3 | R4 | R5 | R6 | R7 |
|---|---|---|---|---|---|---|---|
| Arizona Cardinals | Retained | Retained | Retained | Retained | Retained | Retained | Oakland Raiders |
| Atlanta Falcons | Retained | Retained | Retained | Retained | Retained | Retained | Retained |
| Baltimore Ravens | Retained | Retained | Retained | Retained | Retained | Retained | Indianapolis Colts |
| Buffalo Bills | Retained | Retained | Retained | Retained | Retained | Retained | Retained |
| Carolina Panthers | Retained | Retained | Retained | Retained | Retained | Retained | San Francisco 49ers |
| Chicago Bears | Retained | Retained | Retained | Retained | Retained | Retained | Retained **Hold** |
| Cincinnati Bengals | Retained | Retained | Retained | Retained | Retained | Retained | Retained |
| Cleveland Browns | Retained | Retained | Retained | Retained | Retained | Retained | Retained |
| Dallas Cowboys | Retained | Retained | Retained | Retained | Retained | Kansas City Chiefs | Retained |
| Denver Broncos | Retained | Retained | Retained | Retained | Retained | Retained | Retained |
| Detroit Lions | Retained | Retained | Retained | Retained | Jacksonville Jaguars | Retained | Retained |
| Green Bay Packers | Retained | Retained | Retained | Retained | Retained | Retained | Retained |
| Houston Texans | Retained | Retained | Retained | Retained | Retained | Retained | Retained |
| Indianapolis Colts | Retained | Retained | Retained | Cleveland Browns | Retained | Retained | St. Louis Rams |
| Jacksonville Jaguars | Retained | Washington Redskins | Retained | Retained | Retained | Retained | Retained |
| Kansas City Chiefs | Retained | San Francisco 49ers | Retained | Retained | Retained | Retained | Dallas Cowboys |
| Miami Dolphins | Retained | Retained | Retained | Retained | Retained | Retained | Retained |
| Minnesota Vikings | Retained | Retained | Retained | Retained | Retained | Retained | Retained |
| New England Patriots | Retained | Retained | Retained | Retained | Retained | Retained | Retained |
| New Orleans Saints | Retained | Retained | Retained | Retained | Retained | Retained | San Francisco 49ers |
| New York Giants | Retained | Retained | Retained | Retained | Retained | Retained | Retained |
| New York Jets | Retained | Retained | Retained | Retained | Retained | Retained | Retained |
| Oakland Raiders | Retained | Retained | Retained | Retained | Seattle Seahawks | Retained | Retained |
| Philadelphia Eagles | Retained **Hold** | Retained **Hold** | Retained **Hold** | Retained **Hold** | Retained **Hold** | Retained **Hold** | Retained **Hold** |
| Pittsburgh Steelers | Retained | Retained | Cleveland Browns | Retained | Retained | Retained | Retained |
| San Diego Chargers | Retained | Retained | Retained | Retained | Retained | Retained | Retained |
| San Francisco 49ers | Retained | Retained | Retained | Retained | Retained | Retained | Retained |
| Seattle Seahawks | Retained | Retained | Minnesota Vikings | Retained | Retained | Retained | Retained |
| St. Louis Rams | Retained | Retained | Retained | Retained | Retained | Retained | Retained |
| Tampa Bay Buccaneers | Retained | Retained | Retained **Hold** | Retained **Hold** | Retained | Chicago Bears | Retained |
| Tennessee Titans | Retained | Retained | San Francisco 49ers | Retained | Retained | Retained | Retained |
| Washington Redskins | Jacksonville Jaguars | Retained | Retained | Retained | Retained | Retained | Retained |

**Verification:** stable asset IDs are `(year, round, original club)`. Loader checks full club coverage, duplicate transfers, claim overlaps and dates. Tests check all 224 assets, owner conservation, the branch exclusions, condition evidence, both coin alternatives and the saved screenshot checksum. Compensatory offsets remain unknown, not zero.
