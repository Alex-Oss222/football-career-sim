# 2014 Week 1 depth charts for the 31 background clubs

**Research date:** September 30, 2026 (branch clock July 29, 2014). **Football information window:** the real Week 1 depth charts and the Week 1 injury reports, dated September 3 to 6, 2014, before any Week 1 game. **Status: PREPARED, GATED.** This library is prepared research under [rails method section 7](../career/2014/league/personnel/method.md#7-week-1-depth-charts). It is usable as background TeamInput only when the master clock reaches Week 1 (September 7, 2014); the real charts were public the week of September 2 to 5, 2014, and under the information gate (method section 2) no rail informs any evaluation, board or decision before its date. No Week 1 score, statistic, game participation or later roster move is an input.

**Machine artifact:** [data/2014_week1_depth_charts.json](data/2014_week1_depth_charts.json). **Builder:** `scripts/research/build_2014_week1_depth_charts.py` (reads downloaded sources from a transient workspace; the runtime never downloads anything). **Loader:** `runtime/depth_library.py` with `season=2014` turns one club into a kernel TeamInput; the caller supplies the unit anchors (Document 7 section 2.2). **Tests:** `tests/test_2014_week1_depth_library.py`.

Jacksonville is not in this library. Its TeamInput always comes from the branch roster (`career/2014/team/roster/roster.md`), its medical state and Stone's staff. The real Jaguars' Week 1 chart is recorded in the artifact (`real_jaguars_week1_chart`) only as the source of "the depth slot he really held" for the draft pairing and as the record of which real Jaguars have no branch club.

## Sources

| Use | Source | Scope read |
|---|---|---|
| Depth chart (primary) | nflverse [depth_charts_2014.csv](https://github.com/nflverse/nflverse-data/releases/download/depth_charts/depth_charts_2014.csv) | Week 1, regular season, 32 clubs (1,659 players, 1,957 slot rows) |
| Availability | nflverse [injuries_2014.csv](https://github.com/nflverse/nflverse-data/releases/download/injuries/injuries_2014.csv) | Week 1 report (219 rows dated September 3 to 6, 2014) |
| Membership cross-check | nflverse [roster_weekly_2014.csv](https://github.com/nflverse/nflverse-data/releases/download/weekly_rosters/roster_weekly_2014.csv) | Week 1 club membership and jersey only; status ignored |
| Player bio fields | the user's `user_nfl_2014_week1.json` (transient workspace) | Same 32 clubs and 1,659 gsis ids as the nflverse chart (verified); supplies `birth_date`, `headshot_url` and `page_url`, carried per player as data only; its jersey number equals the weekly-roster jersey for every player |
| Branch control | `career/2014/team/roster/roster.md`, July 29, 2014 | The 78 controlled players (74 signed, four unsigned tenders), matched by gsis id through `library/data/player_birth_dates.json` and `career/2014/league/personnel/league_players.json`; all 78 matched, none by name fallback |
| Draft pairing | [draft_pairing.md](../career/2014/league/personnel/draft_pairing.md) | The seven placements and the one unplaced selection |
| Branch trades | [trades.md](../career/2014/trades/completed_trades/trades.md) | Nwaneri, Babin, Alualu, Shorts, Blackmon, Rackley (Allen retired) |
| Free-agent draws and the replay | [fa_draws.md](../career/2014/league/personnel/fa_draws.md), [replay log](../career/2014/free_agency/march_2014_replay_log.md) | Players Jacksonville won leave their real clubs; players it lost stay on their real charts |
| Retirements | [retirements.md](../career/2014/league/personnel/retirements.md) | Russell Allen (April 22, 2014) |
| 2013 branch placements | `league_players.json` (`existing_branch_placement`), [2013 library](2013_week1_depth_charts.md) | The 2013 draft swaps carried into 2014 |

## Verification

- **Club membership:** all 1,584 retained depth-chart players are listed with the same club in the Week 1 weekly-roster feed (`cross_check.listed`); none is missing.
- **User file agreement:** slot strings agree for 1,577 of 1,584 players; the seven differences are duplicate slot rows in the nflverse feed (for example Javier Arenas, listed CB2 twice), which the user's file de-duplicated. The user's jersey number equals the weekly-roster Week 1 jersey for all 1,584 players, while the depth-chart feed's jersey differs from it for 833, so the user's number is stored. Bio fields are present for 1,583 of 1,584 retained chart players (Seattle's Phil Bates is absent from the user's file).
- **Branch control:** a gsis-id sweep of all 78 controlled players found 38 on other clubs' charts (removed below), 16 on the real Jaguars' chart and 24 on no chart. No controlled player remains on any club and no gsis id or player id appears on two clubs; the builder fails if either happens.
- **Exclusivity gate:** `scripts/check_week_input_exclusivity.py` returned READY on a synthetic 16-game package built from this library plus a scratch Jacksonville input from the branch roster (`--roster career/2014/team/roster/roster.md --expected-games 16`). That package was a gate check only, not game input.
- **Game-day units:** every club clears the kernel's game-day minimum (1 QB, 1 RB, 3 WR, 1 TE, 5 OL, 3 DL, 2 LB, 4 DB, K, P) after injuries and branch changes; `runtime.week_inputs.game_day_actives` trims each unit to 46 when a week is built. Every group's depth runs 1..n without gaps; QB, RB, WR and TE carry explicit order.
- **Starting quarterbacks:** every club's depth-1 passer is the passer its real chart listed first.

**Not independently verified:** the depth charts themselves are single-publisher. No second depth-chart source was compared.

## How each unit is built

1. **Players:** everyone on the club's Week 1 depth chart (offense, defense and special teams), once each.
2. **Position:** the position of the player's best depth-chart slot when that slot's label maps to a kernel group (`runtime.usage.group`), otherwise his roster position. Scheme labels such as LEO, MIKE, WILL, LDE or LCB map through the roster position. Every stored position maps to one of the twelve kernel groups (QB, RB, FB, WR, TE, OL, DL, LB, DB, K, P, LS); `listed_position` keeps the roster label when it differs.
3. **Depth:** within each kernel group, by depth-chart string (1st, 2nd, 3rd). Players the club listed at the same string are ordered by line slot (LT, LG, C, RG, RT, for linemen), then jersey number, then name. **Difference from 2013:** the 2013 builder broke ties by real prior-season usage. The real 2013 statistics are not the branch's 2013, so no usage file is read; the tie-break is the remaining part of the 2013 rule (slot, then jersey) and is documented here rather than inferred. A player seen only in a special-teams slot ranks behind every player with an offensive or defensive slot; a blank slot counts only for a player with no named slot.
4. **Roles:** the first-string kick and punt returners carry `kick_return` and `punt_return`; kickers and punters carry `placekicker` and `punt`.
5. **Availability:** a player listed Out or Doubtful on the Week 1 report is unavailable (55 players: 46 Out, 9 Doubtful). Questionable (38) and Probable (98) players are available. Same convention as 2013.
6. **Return of a pre-existing injury (`return_week`):** a player out before Week 1 did not play in the real Week 1, so his later pre-game reports still describe that same injury. He returns the first week he is reported Questionable or Probable, or is off the report while listed on his club's depth chart. Nothing about him is read after that week. 52 of the 55 have a projected return; three (Jonathan Meeks, Darrion Weems, Rashaan Melvin) never return under this rule.
7. **Ids:** a player id is the player's name. When two players share a name, or a player shares a name with a Jacksonville-controlled player, he gets his club code, for example `Brandon Marshall (DEN)` beside Chicago's Brandon Marshall and `Mike Harris (MIN)` and `C.J. Mosley (BAL)` beside Jacksonville's Mike Harris and C.J. Mosley (twelve ids carry a code). A namesake is never removed: control is matched by gsis id, and the name fallback applies only to a controlled player with no registry id (none in this build).
8. **Bio fields:** `birth_date`, `headshot_url` and `page_url` from the user's file, by gsis id. They are identity data only; nothing in the build reads them.

## Branch reconciliation

### Jacksonville-controlled players removed

Every player under Jacksonville control on July 29, 2014 is removed from his historical club with the reason from the roster, and the next player in his group moves up.

| Club | Removed (reason) |
|---|---|
| Atlanta Falcons | Dwight Lowery (2013 roster carried) |
| Baltimore Ravens | Daryl Smith, Brynden Trawick (2013 roster carried); Eugene Monroe (re-signed by Jacksonville March 11). Baltimore's own C.J. Mosley (LB, a 2014 rookie) is a namesake of Jacksonville's defensive tackle and stays, as `C.J. Mosley (BAL)` |
| Carolina Panthers | Trai Turner (drafted No. 90); Andrew Norwell (undrafted signing May 10) |
| Chicago Bears | Charles Leno Jr. (drafted No. 168); Christian Jones (undrafted signing May 10); Jeremy Cain (re-signed March 19) |
| Cleveland Browns | Joel Bitonio (drafted No. 26); Andrew Hawkins (signed March 18); Taylor Gabriel (undrafted signing May 10); Jordan Poyer (2013 roster carried) |
| Dallas Cowboys | Jeremy Mincey, Lavar Edwards (2013 roster carried) |
| Denver Broncos | Aqib Talib (signed March 11); C.J. Anderson (2013 roster carried) |
| Detroit Lions | Cornelius Lucas (undrafted signing May 10); Montell Owens, C.J. Mosley (2013 roster carried) |
| Green Bay Packers | Davante Adams (drafted No. 38); Corey Linsley (drafted No. 153) |
| Houston Texans | A.J. Bouye, Jonathan Grimes (2013 roster carried) |
| Indianapolis Colts | Hakeem Nicks (signed March 14) |
| Kansas City Chiefs | Travis Kelce (2013 roster carried) |
| Miami Dolphins | Gator Hoskins (undrafted signing May 10) |
| Minnesota Vikings | Adam Thielen (2013 roster carried) |
| New England Patriots | Malcolm Butler (drafted No. 241) |
| New Orleans Saints | Kasim Edebali (undrafted signing May 10) |
| Oakland Raiders | Maurice Jones-Drew, C.J. Wilson (re-signed March 28); Sio Moore (2013 roster carried) |
| Pittsburgh Steelers | Antwon Blake (reserve/future contract effective March 11) |
| St. Louis Rams | Aaron Donald (drafted No. 13) |
| Tampa Bay Buccaneers | Alterraun Verner (signed March 11) |
| Washington Redskins | Kirk Cousins, Bacarri Rambo (2013 roster carried) |

The other 40 controlled players were on the real Jaguars' chart (16) or on no Week 1 chart (24: John Parker Wilson, Tyler Bray, Connor Shaw, Richard Murphy, Toney Clemons, Jerrell Jackson, Cameron Brate, Marcel Jensen, Lane Johnson, Mark Asper, Matt Feiler, Mike Brewster, Tyler Larsen, Daniel Te'o-Nesheim, Jackson Jeffcoat, Jeris Pendleton, D'Anthony Smith, Jerome Long, Julian Stanford, Todd Davis, Mike Harris, Jemea Thomas, Adrian Phillips, Casey Kreiter). Removing them changes no other club.

### Draft pairing

Method section 6 and [draft_pairing.md](../career/2014/league/personnel/draft_pairing.md): the real Jaguars' k-th selection goes to the club that really drafted Jacksonville's k-th branch selection and takes the depth slot he held on the real Jaguars' Week 1 chart, keeping his real Week 1 injury status (the 2013 convention). **Convention for the slot:** the arriving player keeps his real depth string; when an incumbent holds the same string, the two are ordered by the ordinary tie-break (slot, jersey, name), exactly as the 2013 builder ordered Luke Joeckel beside Jason Peters. No listed player is displaced by fiat.

| k | Jacksonville's branch pick | Real Jaguars' selection | Goes to | Real slot | Resulting depth |
|---:|---|---|---|---|---|
| 1 | Aaron Donald (#13) | Blake Bortles, QB (#3) | St. Louis Rams | QB2 | QB2 (ahead of Austin Davis, also QB2, by jersey) |
| 2 | Joel Bitonio (#26) | Marqise Lee, WR (#39) | Cleveland Browns | WR1 | WR1 (tied at the first string; jersey 11 orders him first) |
| 3 | Davante Adams (#38) | Allen Robinson, WR (#61), Probable | Green Bay Packers | WR2 | WR4 |
| 4 | Trai Turner (#90) | Brandon Linder, G (#93) | Carolina Panthers | RG1 | OL4 (the first-string line in LT-LG-C-RG-RT order) |
| 5 | Telvin Smith (#129) | Aaron Colvin, CB (#114) | Unplaced | On no chart (real reserve list) | Listed in `draft_swaps_without_week1_chart` |
| 6 | Corey Linsley (#153) | Telvin Smith (#144) | No player moves | Jacksonville-controlled | |
| 7 | Charles Leno Jr. (#168) | Chris Smith, DE (#159) | Chicago Bears | LEO3 | LB9 (roster label OLB; the LEO slot maps through it) |
| 8 | Jemea Thomas (#205) | Luke Bowanko, C (#205), Probable | New England Patriots | C2 | OL8 |
| 9 | Malcolm Butler (#241) | Storm Johnson, RB (#222), Out | New England Patriots | RB3 | RB5, unavailable, projected return Week 3 |

### Branch trades

The 2013 Gabbert convention: a player the branch traded to another club is added below every listed player of his group, at the position the trade record names, because the branch has no depth evidence for him on his new club and the real Jaguars' slot describes a club he never joined. His real Week 1 report, where one exists, is kept.

| Player | Branch club | Real Week 1 status | Placement |
|---|---|---|---|
| Uche Nwaneri, G | Arizona Cardinals (March 20; 2013 ledger Entry 99) | On no chart | OL8, below every listed lineman |
| Jason Babin, DE | Miami Dolphins (March 24; Entry 102) | On the New York Jets' chart (OLB2), a real Jets signing that followed the real Jaguars' release, which the branch never made (rule 4) | Removed from the Jets; DL9 at Miami |
| Tyson Alualu, DT | Houston Texans (March 24; Entry 102) | Real Jaguars' chart, LDE2 | DL8 at Houston |
| Cecil Shorts, WR | Indianapolis Colts (March 31; Entry 104) | Real Jaguars' chart, WR1, Questionable | WR6 at Indianapolis, available |
| Justin Blackmon, WR | Indianapolis Colts (March 31; Entry 104) | On no chart (real suspension) | WR7 at Indianapolis, **available**: a suspension never rides the rails (rule 2), and the branch records no 2014 suspension of its own |
| Will Rackley, G | Seattle Seahawks (May 12; Entry 110) | On no chart | OL9 at Seattle |
| Russell Allen, LB | Arizona Cardinals (April 7; Entry 106), retired April 22 (Entry 107) | On no chart | Not placed |

### Free agents Jacksonville won and lost

Players Jacksonville signed from other clubs' markets (Talib, Verner, Nicks, Hawkins, Monroe, Te'o-Nesheim; the re-signed Marks, Jones-Drew, C.J. Wilson, Henne and Cain) are removed by the control sweep above; Te'o-Nesheim, Marks and Henne are on no other club's chart. Players Jacksonville lost stay on their real charts: Golden Tate (Detroit, WR1), Julian Edelman (New England, WR1). Undrafted players who declined Jacksonville stay on their real clubs: Albert Wilson (Kansas City, WR2), Trey Burton (Philadelphia, blank third-string slot), James Hurst (Baltimore, LT2, never called); Shaquil Barrett (Denver), Denico Autry (Oakland) and Willie Snead (Cleveland) are on no Week 1 chart, consistent with practice-squad or reserve status that the build does not read. Stephen Morris is an unplaced free agent (rule 4).

**Brent Grimes** stays on Miami's chart (CB1). His branch Jacksonville contract expired March 11, 2014, and Jacksonville did not pursue him; his real next move was a March 2014 free-agent contract with Miami, a free-agent signing in the same window, so under method section 3 he follows it. **Alan Ball** is unplaced: he left Jacksonville as a free agent, and his real next move was a re-signing with the real Jaguars, a real Jaguars move the branch never made (rule 4).

### 2013 branch placements carried forward

The 2013 draft swaps gave nine real 2013 Jaguars draftees to other clubs, and the league database carries them as those clubs' players (`existing_branch_placement`). A real Jaguars roster continuation is not a move, so each stays with his branch club and takes the depth string of his real 2014 Week 1 slot, the same rule that placed him in 2013.

| Player | Branch club since 2013 | Real 2014 slot | Resulting depth |
|---|---|---|---|
| Luke Joeckel, T | Philadelphia Eagles (#2, Lane Johnson) | Real Jaguars, LT1 | OL2 (beside Jason Peters at the first string; Lane Johnson is removed) |
| Dwayne Gratz, CB | Philadelphia Eagles (#64, Jordan Poyer) | Real Jaguars, LCB1 | DB3 |
| Demetrius McCray, CB | Philadelphia Eagles (#210 kept) | Real Jaguars, RCB2 | DB9 |
| Ace Sanders, WR | Philadelphia Eagles (#101 kept) | On no chart (real suspension, never a rail) | WR7, below every listed receiver |
| Matt Barkley, QB | Oakland Raiders (#98, Sio Moore) | Philadelphia's chart, QB3 (the real Eagles kept him; the branch's Oakland did not release him) | Removed from Philadelphia; QB3 at Oakland |
| Johnathan Cyprien, S | Kansas City Chiefs (#33, Travis Kelce) | Real Jaguars, SS1 | DB4 |
| Jeremy Harris, CB | Kansas City Chiefs (#208, Tyler Bray) | Real Jaguars, LCB3 | DB12. He was unplaced in 2013 for want of a Week 1 chart; the league database carries him as Kansas City's, and he now has a slot |
| Denard Robinson, RB | Tennessee Titans (#135, Lavar Edwards) | Real Jaguars, RB2 and KR2 | RB2 |
| Josh Evans, S | Washington Redskins (#169, Bacarri Rambo) | Real Jaguars, SS2 | DB5 |

**Blaine Gabbert** (Green Bay's since the 2013 trade) is on San Francisco's real chart (QB2) after the real March 2014 Jaguars-49ers trade. **Interpretation:** the acquisition is a real San Francisco move and rides the rails (rule 1), with Green Bay standing in the branch for the real Jaguars as the counterparty; he stays on San Francisco's chart. The alternative reading (a real Jaguars move the branch never made, so he stays in Green Bay) would remove a real 49ers player from a real chart and invent a Green Bay placement. This is the one interpretive call in the build not settled by the method's text, recorded here for the user.

**Brandon Marshall (LB)**, claimed on waivers from Jacksonville in August 2013 by a club the branch never named, is on Denver's real chart and stays there (a real Denver move). Austen Lane and Isaiah Stanback are on no chart and remain unplaced. Real 2013 Jaguars the branch never controlled who are on other clubs' real charts (Justin Forsett, Baltimore; Brandon Deaderick, New Orleans; Nathan Stupar, Atlanta; Marcus Burley, Seattle) stay there.

### Players with no branch club

The real Jaguars' chart lists 53 players: 16 Jacksonville-controlled, 16 moved by the pairing, the trades and the carried 2013 placements, and 21 with no branch club (rule 4: a real Jaguars move the branch never made does not happen, and a player the real Jaguars signed stays a free agent Jacksonville may still sign).

| Reason | Players |
|---|---|
| Real Jaguars 2014 acquisitions the branch never made | Toby Gerhart (RB, real 2013 club Minnesota), Zane Beadles (G, Denver), Red Bryant (DE, Seattle), Chris Clemons (DE, Seattle), Ziggy Hood (DE, Pittsburgh), Dekoda Watson (OLB, Tampa Bay) |
| 2014 rookies the real Jaguars signed, not branch players | Josh Wells (T), Mickey Shuler (TE) |
| Real 2013 Jaguars the branch never controlled (unplaced since 2013) | Jordan Todman, Clay Harbor, Jacques McClendon, Sam Young, Abry Jones, Geno Hayes, LaRoy Reynolds, J.T. Thomas, Winston Guy, Will Blackmon, Carson Tinker |
| Former branch players whose real next move was a real Jaguars re-signing | Alan Ball (CB), Will Ta'ufo'ou (FB) |
| Real Jaguars' draft selection with no partner | Aaron Colvin (CB, on no chart) |

Also unplaced, on no chart: Russell Allen (retired), Stephen Morris, Austen Lane, Isaiah Stanback, Kevin Rutland, Allen Reisner, Brandon King. The full list with reasons is `unplaced_branch_players` in the artifact.

## Limitations

- **Inactives:** the source has no Week 1 inactive list. `runtime.week_inputs.game_day_actives` trims each club mechanically by depth to 46 when the week is built; this library stores the full listed unit (45 to 56 per club).
- **Capture timing:** nflverse does not timestamp individual depth-chart rows. The rows are the Week 1 chart as distributed by the league.
- **Roster-feed status is not used:** the weekly-roster feed stamps later-season statuses onto Week 1. Only club membership and jersey are taken from it (through the user's file).
- **Real injury reports of placed players:** a pairing player or a traded player carries the Week 1 report his real club filed (Storm Johnson Out, Allen Robinson and Luke Bowanko Probable, Cecil Shorts Questionable). This is the dated public availability on September 5, 2014, the same rule the 2013 library applied; no later injury, suspension or transaction is read for anyone.
- **Duplicate feed rows:** seven players carry a duplicated slot in the feed's `slots` string; depth is unaffected.
- **Interpretations:** Gabbert (above) and Jeremy Harris (above) are the two placements that go beyond the method's literal text; both are labelled in the artifact's `branch_changes`.

## Gate and later use

- **Information gate:** this file is prepared research. It becomes usable background TeamInput only when the master clock in `state/05_Current_Season_State.md` reaches Week 1 (September 7, 2014). Until then no rail in it may inform Stone's, Caldwell's or any club's evaluation, and `docs/repository_map.json` keeps the 2013 library as the current `background_depth` record.
- **Jacksonville's own game depth chart** (`career/2014/team/depth_chart/game_depth_chart.json`) and 2014 control at the August 30 cutdown are still owed; `runtime/season_readiness.json` keeps `legal_rosters` BLOCKED.
- **Later weeks:** `runtime/week_inputs.py` carries these units forward; availability each week comes from the branch's own closed games plus `return_week` above. A branch transaction that moves a player onto or off one of these clubs after July 29, 2014 (a cutdown claim, a September signing) is applied by rebuilding this library before Week 1 inputs are frozen.

## Updating

```
python scripts/research/build_2014_week1_depth_charts.py SOURCE_DIR > library/data/2014_week1_depth_charts.json
python -m unittest tests.test_2014_week1_depth_library
```

`SOURCE_DIR` is a transient workspace holding the four downloaded inputs; it is never committed.
