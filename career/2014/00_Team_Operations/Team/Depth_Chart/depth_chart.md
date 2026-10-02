# Jacksonville Jaguars 2014 depth chart (season game depth chart)

**As of:** September 13, 2014, after the Washington preparation. Stone re-set the defensive-back order for Week 2 after the September 8 transactions ([record](../Roster/transactions_2014-09-08.md)): Harris and Lowery off the chart on reserve/injured, Verner and Trawick into the first group, Ball and Phillips added; the Week 2 inactives set the same day ([Week 2 record](../../../05_Regular_Season/Games/Week_02/output.md)). Jones-Drew cleared September 12
**Status:** Stone's season game depth chart, issued August 30, 2014 at the reduction to 53 (Document 3 row 9) over the 53 only, from the baseline in the [August 28 personnel packet](../../../05_Regular_Season/Games/Week_01/Regular-season%20Week%201.md) and the frozen [Atlanta chart's](../../../04_Training_Camp_and_Preseason/Preseason_Games/Game_04/depth_chart.json) order for everyone else. The five May 12 competitions and the long-snapper competition closed with it ([roster decisions](../../../04_Training_Camp_and_Preseason/Roster_Decisions/roster_decisions.md)). Stone changes the order only by decision; each change is logged below and copied to the two JSON files in the same commit.
**Machine-readable copies:** [game_depth_chart.json](game_depth_chart.json), the released 2014 game input that `runtime/week_inputs.py` reads as Stone's order (depth by kernel group, positions, roles, the Week 1 inactives), and [working_depth_chart.json](working_depth_chart.json), the same chart with contract flags, availability notes, the removed-player history and the update log.
**Sources:** the [personnel packet](../../../05_Regular_Season/Games/Week_01/Regular-season%20Week%201.md) (the season depth chart baseline), the [final roster cuts](../../../04_Training_Camp_and_Preseason/Roster_Decisions/final_roster_cuts.md) (the 53), the [current roster](../Roster/roster.md) and the [contract status register](../../Finances/player_contracts/contract_status.md) for control and availability, the [medical history](../../Medical/medical_history.md) for instructions.

## How to read this chart

- Order is the kernel's depth order within each position group, first listed first: the packet's baseline for the starting offense, the snapper and the returners; the frozen Atlanta order for everyone else, minus the players who left on August 30. A chart place is Stone's decision, not a promise of snaps; the kernel turns the order into game usage.
- A player out under a medical instruction is listed last in his group while out and is on the inactive list; his return to the order is Stone's decision on clearance. Nicks returns to X, with Adams to Z, only after medical clearance and a full practice week (the packet's condition, carried as Stone's instruction).
- Contract flag comes from the [contract status register](../../Finances/player_contracts/contract_status.md) and the [contract table](../../Finances/player_contracts/contracts.md).
- The four reserve/injured players and the seven practice-squad players are not on the chart.

## Offense

### Quarterbacks (QB)

| Order | Player | Pos | Contract flag | Role on the season chart | Availability |
|---:|---|---|---|---|---|
| 1 | Kirk Cousins | QB | Under contract | QB1; offensive captain (quarterback), named August 31, 2014 | No communicated restriction |
| 2 | Chad Henne | QB | Under contract through 2015 (re-signed April 4) | QB2 (re-signed April 4, 2014; no starting promise) | No communicated restriction |

### Running backs (RB)

| Order | Player | Pos | Contract flag | Role on the season chart | Availability |
|---:|---|---|---|---|---|
| 1 | Maurice Jones-Drew | RB | Under contract through 2015 (re-signed March 28) | Lead back; offensive captain (skill group), named August 31, 2014 | No communicated restriction (cleared September 12, 2014, his projected date, from the September 7 injury; reassessed September 8 with no change; did not practice September 10 to 12, full in the September 13 walkthrough; [medical history](../../Medical/medical_history.md#september-8-to-12-jones-drew-reassessed-and-cleared-harris-and-lowery-to-reserveinjured)) |
| 2 | C.J. Anderson | RB | Under contract | Second back on the season chart (the Atlanta order carried, August 30, 2014); coverage units | No communicated restriction (cleared August 11, 2014, his projected date, from the August 8 lower-extremity injury; reassessed August 9 with no change; [medical history](../../Medical/medical_history.md#august-9-to-11-reassessments-and-andersons-clearance)) |
| 3 | Jonathan Grimes | RB | Under contract through 2014 | Third back on the season chart (the Atlanta order carried, August 30, 2014) | No communicated restriction |

### Fullback (FB)

| Order | Player | Pos | Contract flag | Role on the season chart | Availability |
|---:|---|---|---|---|---|
| 1 | Montell Owens | FB | Under contract (through 2015, Supported) | FB | No communicated restriction |

### Wide receivers (WR)

Adams is the X, Thielen the H (the movable receiver) and Hawkins the Z. Hurns and Gabriel carry rehearsed relief jobs; Hurns is the second punt returner. Nicks is listed last while out.

| Order | Player | Pos | Contract flag | Role on the season chart | Availability |
|---:|---|---|---|---|---|
| 1 | Davante Adams | WR | Rookie contract through 2017 (No. 38, signed May 11) | X (season depth chart, August 30, 2014; the WR1 and WR3 competitions closed); moves to Z when Nicks returns under Stone's condition | No communicated restriction |
| 2 | Adam Thielen | WR | Under contract | H, the movable receiver (season depth chart, August 30, 2014); coverage units | No communicated restriction |
| 3 | Andrew Hawkins | WR | Signed March 18, 2014 (four years) | Z (season depth chart, August 30, 2014; the WR3 competition closed); first kick returner and first punt returner (Westhoff's recommendation, Stone's decision, August 30, 2014) | No communicated restriction |
| 4 | Allen Hurns | WR | Undrafted rookie contract through 2016 (signed May 10) | Fourth receiver on the season chart; second punt returner; rehearsed relief job (August 30, 2014) | No communicated restriction |
| 5 | Taylor Gabriel | WR | Undrafted rookie contract through 2016 (signed May 10) | Fifth receiver on the season chart; rehearsed relief job (August 30, 2014); Week 1 and Week 2 inactive by Stone's standing rule | No communicated restriction |
| 6 | Hakeem Nicks | WR | Signed March 14, 2014 (one year) | Out; listed last among the receivers while out. Returns to X, with Adams to Z, only after medical clearance and a full practice week (Stone's condition, August 30, 2014). Week 1 and Week 2 inactive | Out, multi-week: lower extremity, removed from the August 28 preseason game; projected return September 20, 2014; reassessed September 4 with no change; carried on the 53 by Caldwell's August 30 decision ([medical history](../../Medical/medical_history.md#august-28-preseason-game-4-injuries)) |

### Tight ends (TE)

| Order | Player | Pos | Contract flag | Role on the season chart | Availability |
|---:|---|---|---|---|---|
| 1 | Marcedes Lewis | TE | Under contract | Lead TE | No communicated restriction |
| 2 | Travis Kelce | TE | Under contract | TE2 | No communicated restriction |
| 3 | Marcel Jensen | TE | Undrafted rookie contract through 2016 (signed May 10) | TE3 (season depth chart, August 30, 2014) | No communicated restriction (released August 28, 2014, his projected date, from the August 22 head/neck hold; reassessed August 24 with no change; inactive August 28 under the frozen plan; [medical history](../../Medical/medical_history.md#august-28-preseason-game-4-injuries)) |
| 4 | Gator Hoskins | TE | Undrafted rookie contract through 2016 (signed May 10) | Out; fourth tight end on the season chart while out; Week 1 and Week 2 inactive | Out, short: lower extremity, August 28 preseason game (not removed; finished the game); projected return September 16, 2014; reassessed September 3 with no change; carried on the 53 by Caldwell's August 30 decision ([medical history](../../Medical/medical_history.md#august-28-preseason-game-4-injuries)) |

### Offensive line (OL)

The kernel group is one OL list: the starting five Monroe, Bitonio, Brewster, Turner, Johnson (left to right), then Lucas, Leno, Norwell and Linsley.

| Order | Player | Pos | Contract flag | Role on the season chart | Availability |
|---:|---|---|---|---|---|
| 1 | Eugene Monroe | OT | Under contract through 2018 (re-signed March 11) | Starting LT; offensive captain (offensive line), named August 31, 2014 | No communicated restriction |
| 2 | Joel Bitonio | OT | Rookie contract through 2017 (No. 26, signed May 11) | Starting left guard (season depth chart, August 30, 2014; the left-guard competition closed) | No communicated restriction |
| 3 | Mike Brewster | C | Under contract | Starting center | No communicated restriction |
| 4 | Trai Turner | G | Rookie contract through 2017 (No. 90, signed May 11) | Starting right guard (season depth chart, August 30, 2014; the conditional right-guard alternative closed) | No communicated restriction |
| 5 | Lane Johnson | OT | Under contract | Starting right tackle (season depth chart, August 30, 2014) | No communicated restriction (cleared August 14, 2014, his projected date, from the August 8 trunk injury; reassessed August 10 with no change; inactive at Chicago by Stone's decision; worked August 15 to 21 in full; [medical history](../../Medical/medical_history.md#august-14-johnsons-projected-date)) |
| 6 | Cornelius Lucas | OT | Undrafted rookie contract through 2016 (signed May 10) | Sixth lineman on the season chart, the first reserve tackle (August 30, 2014) | No communicated restriction (club physical May 13, 2014, the specific check after his pre-combine foot stress fracture; the foot is a performance-staff review item) |
| 7 | Charles Leno Jr. | OT | Rookie contract through 2017 (No. 168, signed May 11) | Seventh lineman on the season chart, reserve tackle (August 30, 2014) | No communicated restriction |
| 8 | Andrew Norwell | G | Undrafted rookie contract through 2016 (signed May 10) | Eighth lineman on the season chart, reserve guard (August 30, 2014) | No communicated restriction |
| 9 | Corey Linsley | C | Rookie contract through 2017 (No. 153, signed May 11) | Ninth lineman on the season chart, reserve center (August 30, 2014); Week 1 and Week 2 inactive by Stone's standing rule | No communicated restriction |

## Defense

### Defensive line (DL)

| Order | Player | Pos | Contract flag | Role on the season chart | Availability |
|---:|---|---|---|---|---|
| 1 | Jeremy Mincey | DE | Under contract | Edge 1 (season depth chart, August 30, 2014; the Edge 1 competition closed) | No communicated restriction |
| 2 | Sen'Derrick Marks | DT | Under contract through 2017 (re-signed March 11) | Starting DT; defensive captain (defensive line), named August 31, 2014 | No communicated restriction |
| 3 | Roy Miller | DT | Under contract | Starting DT | No communicated restriction |
| 4 | Andre Branch | DE | Under contract | Edge 2, the next edge in the chart order (August 30, 2014) | No communicated restriction |
| 5 | C.J. Mosley | DT | Under contract | Interior rotation, next inside (season depth chart, August 30, 2014) | No communicated restriction |
| 6 | Daniel Te'o-Nesheim | DE | Signed March 18, 2014 (three years) | Sixth on the defensive line chart (August 30, 2014) | No communicated restriction |
| 7 | Aaron Donald | DT | Rookie contract through 2017 (No. 13, signed May 11) | Seventh on the defensive line chart (August 30, 2014) | No communicated restriction |
| 8 | Kasim Edebali | DE | Undrafted rookie contract through 2016 (signed May 10) | Eighth on the defensive line chart (August 30, 2014); Week 1 and Week 2 inactive by Stone's standing rule | No communicated restriction |

### Linebackers (LB)

| Order | Player | Pos | Contract flag | Role on the season chart | Availability |
|---:|---|---|---|---|---|
| 1 | Daryl Smith | LB | Under contract | Base LB; defensive communication lead; defensive captain (linebackers), named August 31, 2014 | No communicated restriction |
| 2 | Paul Posluszny | LB | Under contract | Base LB | No communicated restriction (head/neck hold from Week 13 cleared April 5, 2014) |
| 3 | Julian Stanford | LB | Under contract | LB depth | No communicated restriction |
| 4 | Sio Moore | LB | Under contract | Package LB (Crennel's packages) | No communicated restriction |
| 5 | Telvin Smith | LB | Rookie contract through 2017 (No. 129, signed May 11) | Fifth linebacker on the season chart (August 30, 2014) | No communicated restriction |
| 6 | Christian Jones | LB | Undrafted rookie contract through 2016 (signed May 10) | Sixth linebacker on the season chart (August 30, 2014) | No communicated restriction |
| 7 | Todd Davis | LB | Undrafted rookie contract through 2016 (signed May 10) | Seventh linebacker on the season chart (August 30, 2014); Week 1 and Week 2 inactive by Stone's standing rule | No communicated restriction |

### Defensive backs (DB)

Stone's Week 2 order, set September 13, 2014 after the September 8 transactions: Talib and Verner outside, Rambo and Trawick at safety, Poyer the nickel, Bouye the first outside reserve, Butler the next cornerback, Prosinski the safety reserve, Phillips added depth, Ball the reserve outside cornerback listed last in his first week. Harris (ordinary reserve/injured) and Lowery (reserve/injured, designated for return) are off the chart from September 8.

| Order | Player | Pos | Contract flag | Role on the season chart | Availability |
|---:|---|---|---|---|---|
| 1 | Aqib Talib | CB | Signed March 11, 2014 (five years) | Starting CB (season depth chart, August 30, 2014) | No communicated restriction |
| 2 | Alterraun Verner | CB | Signed March 11, 2014 (four years) | Starting CB opposite Talib for Week 2 (Stone, September 13; sixth defensive back on the August 30 chart) | No communicated restriction |
| 3 | Bacarri Rambo | S | Under contract | Starting S; coverage units | No communicated restriction |
| 4 | Brynden Trawick | S | Under contract | Starting S next to Rambo for Week 2 (Stone, September 13); coverage units | No communicated restriction |
| 5 | Jordan Poyer | CB | Under contract | Nickel (unchanged; Stone did not move him to solve the outside place); coverage units | No communicated restriction (cleared August 26, 2014, his projected date, from the August 22 upper-extremity injury; reassessed August 23 with no change; [medical history](../../Medical/medical_history.md#august-23-to-27-reassessments-and-poyers-clearance)) |
| 6 | A.J. Bouye | CB | Under contract | First outside reserve CB; coverage units | No communicated restriction (cleared August 31, 2014, his projected date, from the August 28 lower-extremity injury; reassessed August 29 with no change; [medical history](../../Medical/medical_history.md#august-29-to-31-reassessments-bouyes-clearance-and-the-reserve-placements)) |
| 7 | Malcolm Butler | CB | Rookie contract through 2017 (No. 241, signed May 11) | Next cornerback after Bouye (Week 2 order); Week 1 inactive by Stone's standing rule, active Week 2 | No communicated restriction |
| 8 | Chris Prosinski | S | Under contract | Safety reserve; coverage units | No communicated restriction |
| 9 | Adrian Phillips | S | Under contract through 2016 (promoted from the practice squad September 8 on a three-year minimum contract) | Safety and coverage-unit depth (the packet's proposed promotion) | No communicated restriction |
| 10 | Alan Ball | CB | Under contract through 2014 (signed September 8, one year at the minimum rate) | Reserve outside CB, listed last in the group in his first week after signing; expansion earned through the week's work, not promised; Week 2 inactive by Stone's standing rule | No communicated restriction (club physical September 8, 2014, no finding) |

## Special teams

| Slot | Player | Contract flag | Role | Availability |
|---|---|---|---|---|
| K (placekicker) | Josh Scobee | Under contract | K | No communicated restriction |
| P (punt) | Bryan Anger | Under contract | P | No communicated restriction |
| LS | Casey Kreiter | Undrafted rookie contract through 2016 (signed May 10) | LS; the competition closed August 30 with Cain released | No communicated restriction |
| Kick returner | Andrew Hawkins | Under contract through 2017 (signed March 18) | First kick returner (Westhoff's recommendation, Stone's decision, August 30) | No communicated restriction |
| Punt returner | Andrew Hawkins; Allen Hurns second | Under contract through 2017 (signed March 18) | First punt returner; Hurns the second punt returner | No communicated restriction |

Mike Westhoff coordinates special teams. The coverage units carry the defined primary and backup jobs recorded in Document 5 section 7 until Westhoff or Stone changes them; the hands and onside personnel are prepared from the 53 in the Week 1 preparation.

## Captains (August 31, 2014)

Stone named six season captains on August 31, three on offense and three on defense by position group, with no player vote: Kirk Cousins (quarterback), Eugene Monroe (offensive line) and Maurice Jones-Drew (skill group); Sen'Derrick Marks (defensive line), Daryl Smith (linebackers) and Dwight Lowery (secondary). The appointment is in [roster decisions](../../../04_Training_Camp_and_Preseason/Roster_Decisions/roster_decisions.md).

## Week 2 inactives (set September 13, 2014)

Seven of the 53 are inactive for Week 2 at Washington, so 46 dress (rules library R4): Hakeem Nicks and Gator Hoskins by medical instruction, and five by Stone's standing rule for the healthy inactives, the deepest healthy reserve on the chart in each of the five largest healthy position groups, never below a legal game-day unit, re-set each week: Alan Ball (tenth defensive back, listed last in his first week after signing September 8), Corey Linsley (ninth lineman), Kasim Edebali (eighth defensive lineman), Todd Davis (seventh linebacker) and Taylor Gabriel (fifth healthy receiver). Malcolm Butler, the Week 1 healthy inactive in the group, is active. Maurice Jones-Drew, cleared September 12, is active by Stone's decision. Stone set the seven on September 13 after the Washington preparation ([Week 2 record](../../../05_Regular_Season/Games/Week_02/output.md)). The 46 satisfy the game-day unit check (`runtime.usage.lineup_errors`). The Week 1 list (Nicks, Hoskins; Butler, Linsley, Edebali, Todd Davis, Gabriel) was applied September 7 with no change.

## Counts at September 13, 2014

| Group | Count |
|---|---:|
| Active 53 on the chart | 53 |
| Reserve/injured (not on the chart) | 4 |
| Practice squad (not on the chart) | 7 of 10 |
| Controlled players (the 53 and the four on reserve/injured) | 57 |
| Removed August 30 (19 waived or released; four tenders withdrawn) | 23 |

Open on the chart: nothing is added but not placed. Ball and Phillips, added September 8, were placed by Stone's Week 2 order on September 13.

## Update log

Add a row for every signing, tag, tender, trade, release, retirement, draft pick, medical change and Stone depth decision that changes this chart, and change the two JSON copies in the same commit.

| Date | Event | Source record | Change |
|---|---|---|---|

| February 17, 2014 | Working chart created from the closed 2013 chart | None (derived view; inputs are [Meester retirement record](../../../League/personnel/retirements.md), [2014 reserve/future signings](../../Free_Agency/signings.md), and [February 17 pre-tag review](../../../01_Early_Offseason/caldwell_pre_tag_verifications.md)) | Meester removed; 14 pending free agents and 2 unresolved contracts flagged; six reserve/future players listed as joining March 11 with no role |
| February 18, 2014 | Eugene Monroe designated non-exclusive franchise player | [Monroe franchise designation](../../Free_Agency/signings.md) | Monroe's flag changes from pending UFA to franchise-tagged; order unchanged |
| February 28, 2014 checkpoint review | Administrative reconciliation against the merged roster and contracts | None (review through [February 28 cap publication](../../Finances/salary_cap/cap_worksheet.md)) | Refreshed source pointers; verified 52 active players, Meester retired and six March 11 futures; order, roles and availability unchanged |
| February 28, 2014 | Complete contract terms | [adopted contract schedules](../../Finances/player_contracts/contracts.md) | Wilson and Jonathan Grimes signed through 2014; futures through 2015; no depth-order or role change |
| March 11, 2014 | League year opened | [March 11 league-year transactions](../../Free_Agency/signings.md) | Removed Henne, Jones-Drew, Reisner, Marks, C.J. Wilson, Brent Grimes, Rutland and Ball (control ended); players below them moved up only by removal. Added, not placed: the six futures (now in force) and Te'o-Nesheim. Tender flags for Bradfield, Clemons, Brown and Pasztor; Monroe on the tag; Cain re-signed |
| March 11, 2014 correction | March 2014 free-agency replay | [Monroe, Marks and Verner agreements](../../Free_Agency/march_2014_replay_log.md) | Marks re-signed and restored to his carried place (DL 1, players below move down one); Verner added, not placed; Te'o-Nesheim's and Cain's first-pass signings withdrawn (LS open); Monroe signed through 2018 |
| March 12, 2014 | Replay: Talib signed | [Talib and Tate decisions](../../Free_Agency/march_2014_replay_log.md) | Talib added, not placed; no order change |
| March 18, 2014 | Replay: Nicks and Hawkins signed | [Nicks, Hawkins and Edelman decisions](../../Free_Agency/march_2014_replay_log.md) | Both added, not placed; no order change |
| March 18, 2014 | Replay: Te'o-Nesheim signed | [Te’o-Nesheim agreement](../../Free_Agency/teo_nesheim_negotiation_2014-03-18.md) | Added, not placed; no order change |
| March 20, 2014 | Cain re-signed; Nwaneri traded | [March 19–20 Cain and Nwaneri transactions](../../../Record.md) | Cain back in the LS slot; Nwaneri (OL 2, starting LG) removed and the linemen below him move up one without a reorder; the left guard job is open |
| March 24, 2014 | Babin and Alualu traded | [Babin trade](../../Trades/completed_trades/babin_to_miami_2014-03-24.md) and [Alualu trade](../../Trades/completed_trades/alualu_to_houston_2014-03-24.md) | Babin (DL 2) and Alualu (DL 4) removed; the linemen below each move up without a reorder; the carried Edge 1 role is open |
| March 28, 2014 | Jones-Drew and C.J. Wilson re-signed | [March 25–31 signings and schedule filing](../../../Record.md) | Jones-Drew restored at RB 1 (lead back) and Wilson after Pendleton, their carried 2013 places; the players below each move down one |
| March 31, 2014 | Shorts and Blackmon traded to Indianapolis | [Shorts and Blackmon trade](../../Trades/completed_trades/shorts_blackmon_to_indianapolis_2014-03-31.md) | Shorts (WR 1) and Blackmon (WR 3) removed; Thielen, Clemons and Brown move up without a reorder; the carried WR1 and WR3 roles are open |
| April 4 to 7, 2014 | Henne re-signed; Posluszny cleared; Allen traded to Arizona | [April 1–17 personnel and staff decisions](../../../Record.md) | Henne restored at QB 2, his carried place; John Parker Wilson moves down one. Posluszny's hold cleared April 5. Allen (LB 2) removed; Stanford, Moore and Posluszny move up without a reorder. Smith and Posluszny keep their carried base roles and Smith the communication lead; no Stone role decision |
| May 2, 2014 | Unsigned tenders: user instruction on program participation | [May 2–11 record](../../../Record.md) | No chart change. Bradfield, Clemons, Brown and Pasztor keep their carried places and tender flags; they take no part in the program until they sign |
| May 8 to 11, 2014 | 2014 draft, undrafted signings and rookie contracts | [May 8–11 draft and signings](../../../Record.md) | Added, not placed: the nine draft selections and 17 undrafted rookies in their groups (Kreiter under special teams). No order change; no Stone role decision |
| May 12, 2014 | Rackley traded to Seattle | [May 11–12 Rackley and Ball decisions](../../../Record.md) | Rackley (OL 3, starting right guard) removed; Johnson, Bradfield, Pasztor and Asper move up without a reorder. The starting right guard role is open for Stone; no Stone role decision |
| May 12, 2014 (recorded May 23) | Stone's starting roles entering OTAs; rookie minicamp and Phase Two closed | [May 12–23 spring record](../../../Record.md) | Rep starting points, not awards: Nicks placed WR 1 (Adams the competition) and Adams WR 3 (Hawkins the competition), so Thielen is WR 2 and Clemons and Brown move to WR 4 and 5 without a reorder; Bitonio placed OL 2 at left guard (Norwell the competition) and Turner OL 4 at right guard (Bitonio or Norwell if Turner struggles), the line reading Monroe, Bitonio, Brewster, Turner, Johnson, then Bradfield, Pasztor, Asper; Mincey holds Edge 1 (Branch the competition) with no DL reorder. Hawkins, Norwell and every other added player stay unplaced. The May 16 and 17 rookie minicamp and Phase Two through May 23 changed no order and no availability |
| August 8 to 14, 2014 (recorded August 14) | Preseason games 1 and 2: availability notes | [Preseason game 1](../../../04_Training_Camp_and_Preseason/Preseason_Games/Game_01/output.md) and [game 2](../../../04_Training_Camp_and_Preseason/Preseason_Games/Game_02/output.md) outputs; [medical history](../../Medical/medical_history.md) | No order change and no Stone depth decision. Availability notes only: Brate out long term (August 8); Johnson out August 8 to 14 and cleared on his projected date, inactive at Chicago by Stone's one-game decision with Lucas the one-game right tackle (not a chart change); Jackson out multi-week and Murphy on an independent medical hold (August 14). Anderson's August 8 injury cleared August 11. Jackson's and Brate's roster dispositions are pending with Caldwell |
| August 15 to 21, 2014 (recorded August 21) | Detroit preparation: availability notes | [Camp record](../../../04_Training_Camp_and_Preseason/Training_Camp/training_report.md#august-15-to-21-the-chicago-review-and-the-detroit-preparation); [medical history](../../Medical/medical_history.md#august-15-to-21-reassessments-and-murphys-release) | No order change and no Stone depth decision. Availability notes only: Murphy released August 18 on his projected date and available; Jackson's August 21 and Brate's August 15 reassessments unchanged; Johnson's return to the first-group right tackle for August 22 is a game-plan freeze in the [Game_03 inputs](../../../04_Training_Camp_and_Preseason/Preseason_Games/Game_03/README.md), not a chart change |
| August 22, 2014 | Preseason game 3: availability notes | [Preseason game 3](../../../04_Training_Camp_and_Preseason/Preseason_Games/Game_03/output.md) output; [medical history](../../Medical/medical_history.md#august-22-preseason-game-3-injuries) | No order change and no Stone depth decision. Availability notes only: Jensen on an independent medical hold (August 22; projected return August 28, reassessment August 24); Poyer out (August 22; not removed; projected return August 26, reassessment August 23). Johnson's one-game right-tackle workload plan for Detroit ran as frozen and has ended; the August 28 arrangement is Stone's open decision, not a chart change |
| August 23 to 27, 2014 (recorded August 27) | Atlanta preparation: availability notes | [Camp record](../../../04_Training_Camp_and_Preseason/Training_Camp/training_report.md#august-23-to-27-the-detroit-review-and-the-atlanta-preparation); [medical history](../../Medical/medical_history.md#august-23-to-27-reassessments-and-poyers-clearance) | No order change and no Stone depth decision. Availability notes only: Poyer cleared August 26 on his projected date and available; Jensen's August 24 reassessment unchanged, the hold running to its August 28 projected date (game day) and keeping him out of the frozen Atlanta plan; Jackson and Brate unchanged. The August 26 reduction to 75 required no transaction (74 under contract). Johnson's first-quarter right tackle for August 28 is the current chart's starting point in a game lineup frozen in the [Game_04 inputs](../../../04_Training_Camp_and_Preseason/Preseason_Games/Game_04/README.md), not a chart change |
| August 28, 2014 | Preseason game 4: availability notes | [Preseason game 4](../../../04_Training_Camp_and_Preseason/Preseason_Games/Game_04/output.md) output; [medical history](../../Medical/medical_history.md#august-28-preseason-game-4-injuries) | No order change and no Stone depth decision. Availability notes only: Nicks out multi-week (August 28; removed; projected return September 20, reassessment September 4); Hoskins out, short (August 28; not removed; projected return September 16, reassessment September 3); Pendleton out (August 28; not removed; projected return September 1, reassessment August 29); Bouye out (August 28; not removed; projected return August 31, reassessment August 29); Jensen's hold cleared August 28 on its projected date with him inactive under the frozen plan; Jackson and Brate unchanged. The preseason is complete at 1-3; the season game depth chart is owed at the August 30 reduction to 53 (Stone), and the Week 1 receiver arrangement without Nicks is Stone's open decision, not a chart change |

| August 29, 2014 | Atlanta review and cutdown meeting; Bouye and Pendleton reassessed | [Camp record](../../../04_Training_Camp_and_Preseason/Training_Camp/training_report.md#august-29-the-atlanta-review-and-the-cutdown-meeting); [medical history](../../Medical/medical_history.md#august-29-to-31-reassessments-bouyes-clearance-and-the-reserve-placements) | No order change. Availability notes only: Bouye and Pendleton reassessed August 29 with no change. The meeting carried the packet's 53 recommendation and depth baseline to Caldwell unchanged |
| August 30, 2014 | Reduction to 53 and Stone's season game depth chart | [Final roster cuts](../../../04_Training_Camp_and_Preseason/Roster_Decisions/final_roster_cuts.md); [roster decisions](../../../04_Training_Camp_and_Preseason/Roster_Decisions/roster_decisions.md) | Removed by Caldwell's reduction: Wilson, Bray and Shaw (QB); Murphy (RB); Asper, Feiler, Shatley and Larsen (OL); Ryan Davis, C.J. Wilson, Edwards, Jeffcoat, Pendleton, Long and D'Anthony Smith (DL); Blake, Thomas and Phillips (DB); Cain (LS); Bradfield, Clemons, Brown and Pasztor (tenders withdrawn); Brate and Jackson waived with the injured designation and off the chart. Stone's season chart over the 53: Adams X, Thielen H, Hawkins Z, then Hurns, Gabriel and Nicks last while out; Lewis, Kelce, Jensen, Hoskins last while out; Monroe, Bitonio, Brewster, Turner, Johnson, then Lucas, Leno, Norwell, Linsley; Kreiter snapping; Hawkins returning kicks and punts with Hurns the second punt returner; every other group in the frozen Atlanta order minus the departures. The WR1, WR3, left-guard, right-guard, Edge 1 and long-snapper competitions closed; nothing is added but not placed. Promoted to `game_depth_chart.json`, the released game input |
| August 31, 2014 | Waivers cleared, reserve/injured placements, practice squad, Week 1 inactives and captains | [Final roster cuts](../../../04_Training_Camp_and_Preseason/Roster_Decisions/final_roster_cuts.md); [roster decisions](../../../04_Training_Camp_and_Preseason/Roster_Decisions/roster_decisions.md); [medical history](../../Medical/medical_history.md#august-29-to-31-reassessments-bouyes-clearance-and-the-reserve-placements) | No order change. Brate and Jackson to reserve/injured; eight practice-squad players signed; Bouye cleared August 31, his projected date, and active. Week 1 inactives set (Nicks, Hoskins; Butler, Linsley, Edebali, Todd Davis, Gabriel by the standing rule). Captains named: Cousins, Monroe, Jones-Drew; Marks, Daryl Smith, Lowery |
| September 7, 2014 | Week 1 at Philadelphia: availability notes | [Week 1 game record](../../../05_Regular_Season/Games/Week_01/output.md); [medical history](../../Medical/medical_history.md#september-7-week-1-injuries-at-philadelphia) | No order change and no Stone depth decision. Availability notes only: Jones-Drew out, minor (September 7; not removed; projected return September 12, reassessment September 8); Mike Harris out, long term (September 7; removed in overtime; projected return December 8, reassessment September 14); Dwight Lowery out, long term (September 7; removed in overtime; projected return December 11, reassessment September 14). The Week 2 starting cornerback and safety, the listing of Harris and Lowery last in their group while out and the Week 2 inactives are Stone's decisions after the September 8 review; the roster dispositions on Harris and Lowery are Caldwell's with the user. Both JSON copies: availability notes and this row in the working copy; the released game input unchanged until Stone's Week 2 decision |

| September 8 to 13, 2014 | Harris and Lowery to reserve/injured, Ball signed, Phillips promoted (September 8); Stone's Week 2 secondary and inactives (September 13) | [September 8 transactions](../Roster/transactions_2014-09-08.md); [Alan Ball signing](../../Free_Agency/alan_ball_signing_2014-09-08.md); [medical history](../../Medical/medical_history.md#september-8-to-12-jones-drew-reassessed-and-cleared-harris-and-lowery-to-reserveinjured); [Week 2 record](../../../05_Regular_Season/Games/Week_02/output.md) | Harris (DB 2) and Lowery (DB 3) removed to reserve/injured and off the chart; Ball and Phillips added. Stone's Week 2 defensive-back order: Talib, Verner, Rambo, Trawick, Poyer, Bouye, Butler, Prosinski, Phillips, Ball (Verner and Trawick into the first group; Poyer stays at nickel; Bouye the first outside reserve; Ball last in his first week). No other group changed. Week 2 inactives: Nicks and Hoskins by instruction; Ball, Linsley, Edebali, Todd Davis and Gabriel by the standing rule (Butler active). Availability: Jones-Drew cleared September 12, active; Nicks and Hoskins unchanged. Both JSON copies changed with this row |

## Maintaining the game-input copy

`runtime/seasons.py` names `career/2014/00_Team_Operations/Team/Depth_Chart/game_depth_chart.json` as the required 2014 game input, and `runtime/week_inputs.py` reads it as Stone's order when it builds Jacksonville's weekly TeamInput: `depth` by kernel group (starters first), `positions`, `roles` and `game_day_inactives` (`week`, exactly seven players from the 53, every unavailable player among them). It was promoted on August 30, 2014 from Stone's season chart; the working copy mirrors it. Change both files and this log in the same commit; a changed inactive list is a weekly Stone decision recorded in the week's output and here.
