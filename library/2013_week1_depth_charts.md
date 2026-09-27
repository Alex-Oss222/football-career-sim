# 2013 Week 1 depth charts for the 31 background clubs

**Research date:** September 27, 2026. **Football information window:** through the Friday, September 6, 2013 injury report, before any Week 1 game. **Status: VERIFIED for kernel 2013.4 TeamInputs, with the limitations labelled below.** No Week 1 score, statistic, game participation or later roster move is an input.

**Machine artifact:** [data/2013_week1_depth_charts.json](data/2013_week1_depth_charts.json). **Builder:** `scripts/research/build_2013_week1_depth_charts.py` (reads downloaded sources; the runtime never downloads anything). **Loader:** `runtime/depth_library.py` turns one club into a kernel TeamInput; the caller supplies the unit anchors (Document 7 section 2.2).

Jacksonville is not in this library. Its TeamInput always comes from the branch roster (`career/2013/roster.md`), its medical state and Stone's staff.

## Why this exists

Kernel 2013.4 distributes carries, targets and tackles by each club's depth order, so every club needs a complete game-day unit with explicit depth. Rebuilding 31 depth charts by hand each week is slow and error-prone. This library freezes the Week 1 units once, from dated public sources, already reconciled to the branch.

## Sources

| Use | Source | Scope read |
|---|---|---|
| Depth chart (primary) | nflverse [depth_charts_2013.csv](https://github.com/nflverse/nflverse-data/releases/download/depth_charts/depth_charts_2013.csv) | Week 1, regular season, 31 clubs |
| Availability | nflverse [injuries_2013.csv](https://github.com/nflverse/nflverse-data/releases/download/injuries/injuries_2013.csv) | Week 1 report, dated September 6, 2013 |
| Co-starter order | nflverse [stats_player_reg_2012.csv](https://github.com/nflverse/nflverse-data/releases/download/stats_player/stats_player_reg_2012.csv) | 2012 regular season |
| Membership cross-check | nflverse [roster_weekly_2013.csv](https://github.com/nflverse/nflverse-data/releases/download/weekly_rosters/roster_weekly_2013.csv) | Week 1 club membership only |
| Draft swaps | nflverse [draft_picks.csv](https://github.com/nflverse/nflverse-data/releases/download/draft_picks/draft_picks.csv); NFL.com, ["Matt Barkley taken by Philadelphia Eagles after trade"](https://www.nfl.com/news/matt-barkley-taken-by-philadelphia-eagles-after-trade-0ap1000000164751) | 2013 selections at Jacksonville's slots; the #98 trade |
| Branch control | `career/2013/roster.md`, September 4, 2013 | Jacksonville's active 53 and practice squad |

## Verification

- **Club membership:** all 1,599 depth-chart players are listed with the same club in the Week 1 weekly-roster feed, a separate NFL roster feed from the same publisher.
- **Starting quarterbacks:** every club's depth-1 passer is its Week 1 starter, including Terrelle Pryor (Oakland), E.J. Manuel (Buffalo) and Geno Smith (New York Jets).
- **Branch control:** a name-and-position sweep of all 61 Jacksonville-controlled players against every club's chart found no controlled player left on another club, and no different player wrongly removed.
- **Game-day units:** every club clears the kernel's game-day minimum (1 QB, 1 RB, 3 WR, 1 TE, 5 OL, 3 DL, 2 LB, 4 DB, K, P) after injuries and branch removals. `tests/test_depth_library.py` holds these checks.

**Not independently verified:** the depth charts themselves are single-publisher. Pro-Football-Reference, NFL.com, ESPN, Ourlads and the Wayback Machine are unreachable from this research environment, so no second depth-chart source could be compared.

## How each unit is built

1. **Players:** everyone on the club's Week 1 depth chart (offense, defense and special teams), once each.
2. **Position:** the position of the player's best depth-chart slot when that slot names one, otherwise his roster position. This files Terrelle Pryor (listed WR, QB1 slot) as a quarterback.
3. **Depth:** within each kernel position group, by depth-chart string (1st, 2nd, 3rd). Players the club listed at the same string are ordered by 2012 regular-season usage: attempts for quarterbacks, carries for backs, targets for receivers and tight ends, tackles for defenders. Offensive linemen at the same string follow LT, LG, C, RG, RT. A player seen only in a special-teams slot ranks behind every player with an offensive or defensive slot.
4. **Roles:** the first-string kick and punt returners carry `kick_return` and `punt_return`; kickers and punters carry `placekicker` and `punt`.
5. **Availability:** a player listed Out or Doubtful on the September 6 report is unavailable (55 players: 43 Out, 12 Doubtful). Under the 2013 definitions, Doubtful meant at least a 75 percent chance of not playing. Questionable and Probable players are available.
6. **Return of a pre-existing injury (`return_week`):** a player out before Week 1 did not play in the real Week 1, so his later pre-game reports still describe that same injury. He returns the first week he is reported Questionable or Probable, or is off the report while listed on his club's depth chart. Nothing about him is read after that week, because a later report could describe an injury from a real game. Two players never return during the regular season under this rule.
7. **Ids:** a player id is the player's name. When two players share a name, each gets his club code, for example `Alex Smith (KC)` and `Alex Smith (CIN)`, or `Mike Harris (SD)` beside Jacksonville's Mike Harris.

## Branch reconciliation

### Jacksonville-controlled players removed

Every player under Jacksonville control on September 4 is removed from his historical club, and the next player at his position moves up.

| Club | Removed |
|---|---|
| Baltimore Ravens | Brynden Trawick, Daryl Smith |
| Denver Broncos | C.J. Anderson |
| Detroit Lions | C.J. Mosley |
| Green Bay Packers | C.J. Wilson |
| Houston Texans | A.J. Bouye |
| Kansas City Chiefs | Tyler Bray, Travis Kelce |
| Miami Dolphins | Brent Grimes |
| Oakland Raiders | Sio Moore |
| Philadelphia Eagles | Lane Johnson, Jordan Poyer |
| Pittsburgh Steelers | Antwon Blake |
| Tennessee Titans | Lavar Edwards |
| Washington Redskins | Kirk Cousins, Bacarri Rambo |

### Branch trade

Blaine Gabbert, traded to Green Bay for C.J. Wilson (ledger Entry 5), is added to Green Bay below every quarterback Green Bay listed.

### Draft swaps

User rule, September 27, 2026: at each slot Jacksonville used in the branch, the player the real Jaguars took at that slot goes to the club that historically had Jacksonville's branch pick. He takes the depth slot he held on his real Week 1 depth chart and keeps his real Week 1 injury status.

| Slot | Jacksonville's branch pick | Real selection at the slot | Goes to |
|---:|---|---|---|
| #2 | Lane Johnson | Luke Joeckel (T) | Philadelphia Eagles |
| #33 | Travis Kelce | Johnathan Cyprien (S) | Kansas City Chiefs |
| #64 | Jordan Poyer | Dwayne Gratz (CB) | Philadelphia Eagles |
| #98 | Sio Moore | Matt Barkley (QB), moved from Philadelphia | Oakland Raiders |
| #135 | Lavar Edwards | Denard Robinson (RB/WR) | Tennessee Titans |
| #169 | Bacarri Rambo | Josh Evans (S) | Washington Redskins |
| #208 | Tyler Bray | Jeremy Harris (CB) | Not placed: absent from the real Jaguars' Week 1 depth chart |

On April 27, 2013 the real Jaguars traded #98 to Philadelphia for #101 and #210. The branch has no Jacksonville draft-day trade, so Jacksonville kept #98 and Philadelphia kept both picks. The players the real Jaguars took there, Ace Sanders (#101, WR) and Demetrius McCray (#210, CB), go to Philadelphia.

### Undrafted free agents

Jacksonville's branch undrafted signings (C.J. Anderson, A.J. Bouye, Brynden Trawick, Adam Thielen) are removed from their historical clubs, and the next man up takes the slot; unlike a draft slot, there is no pick to swap. The real Jaguars' 2013 undrafted signings that the branch never made are not placed on any club.

### Players with no branch club

- **Waiver claims:** Austen Lane, Brandon Marshall and Isaiah Stanback were claimed on August 31 by clubs the branch never named. Placing them would mean inventing the claimant.
- **Real Jaguars not in the branch:** sixteen players on the real Jaguars' Week 1 depth chart are neither under branch control nor moved by a draft swap: Abry Jones, Brandon Deaderick, Carson Tinker, Chris McCoy, Clay Harbor, Geno Hayes, J.T. Thomas, Jacques McClendon, Jordan Todman, Justin Forsett, Kyle Knox, LaRoy Reynolds, Ricky Stanzi, Stephen Burton, Will Blackmon, Winston Guy. No branch event places them with Jacksonville or another club.

## Limitations

- **Inactives:** the source has no Week 1 inactive list, so every available listed player is on the game-day unit (44 to 53 per club). Depth order, not the 46-man limit, decides usage, so low-depth extras rarely touch the ball.
- **Capture timing:** nflverse does not timestamp individual depth-chart rows. The rows are the Week 1 chart as distributed by the league.
- **Blank slots:** some rows carry no slot name. Such a slot counts only for a player with no named slot, ranked behind every named one. This lowers Seattle's Brandon Mebane and Cliff Avril, whose only Week 1 slots are blank.
- **Roster-feed status is not used:** the weekly-roster feed stamps later-season statuses onto Week 1, such as October injured-reserve placements. Reading it would leak future events, so only club membership is taken from it.
- **Practice-squad listings:** a few players the league may have listed from practice squads appear on club charts. The status that would confirm this is one of the leaking fields above, so they are kept at their listed depth.
- **Name-based control check:** branch control is matched by name and position side. A future Jacksonville acquisition must be checked against this library before the week it applies to.

## Later weeks

`runtime/week_inputs.py` carries these units forward to every later week. Real depth charts after Week 1 are not read, because they reflect injuries and results from real games the branch never had. Availability each week comes from the injuries generated in the branch's own closed games (every receipt carries its game's injury report) plus the `return_week` above. A branch transaction involving one of these clubs is applied by rebuilding this library.

## Updating

Rebuild after a branch transaction that moves a player onto or off one of these clubs:

```
python scripts/research/build_2013_week1_depth_charts.py SOURCE_DIR > library/data/2013_week1_depth_charts.json
python -m unittest tests.test_depth_library
```

## Runtime note (September 27, 2026)

This note scopes statements above; no data value changes and no rebuild is needed.

- **Game-day trimming from Week 3.** From Week 3 (ledger Entry 38), `runtime.week_inputs.game_day_actives` trims each background club's available unit mechanically by depth to at most 46 game-day actives; the weekly gate in `scripts/check_week_input_exclusivity.py` rejects more. The "Inactives" limitation above ("Depth order, not the 46-man limit, decides usage") describes Weeks 1 and 2 only. This library still stores each club's full listed unit; the trim happens when a week's TeamInputs are built.
- **Kernels served.** The status line names kernel 2013.4; the same units serve kernels 2013.4 through 2013.6.
