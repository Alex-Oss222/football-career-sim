# Engine defect register (assessed September 28, 2026, kernel 2014.3)

**Function:** the open list of engine defects and realism gaps, ranked for fixing before 2014 games. It was built from three read-only audits (game logic, player credit, calibration) over the 267 closed 2013 receipts and synthetic games on the current kernel, and every item here was checked in code, receipts or a synthetic sample unless marked inferred. Closed 2013 results stand; nothing here reruns a game.

**Columns.** *Changes results* says whether a fix moves scores, possessions or injuries (a new kernel version and your approval) or only credit and display. *Decision* names what a fix needs from you beyond approval.

## Fixed in kernel 2014.3

| Defect | Fix |
|---|---|
| Sacks allowed charged at random across every dressed lineman (32% to backups in Weeks 11-17) | Charged to the on-field lineman facing the rusher; line starts recorded |
| No coverage tackles; the punt cover player drawn from a set missing OLB/ILB/MLB/SS/FS and praised whatever happened | One coverage tackle per returned kick from the kicking club's unit; evidence only for the tackler |
| Long snappers credited with nothing | Long snaps on every punt, field goal and try |
| Returners drawn afresh on every kick (Jacksonville used 18) | One club returner per game (designated, else a depth rule) |
| No Pro Bowl game structure | `game_type="pro_bowl"` |

## Tier 1: results integrity (recommended before any 2014 game)

| # | Defect | Evidence | Proposed fix | Changes results | Decision |
|---|---|---|---|---|---|
| 1 | **Every club has the same strength.** All TeamInputs carry the Average anchor (2.0) on all three units, so a game is a coin flip plus a small home term. | 2013 win spread SD 2.01 (pure 16-game coin flips: 2.00; real NFL about 3, approximate). Point differentials SD 47 (real about 90-100, approximate). `scripts/build_week_inputs.py` AVERAGE_ANCHORS; `runtime/anchors.py` evidence anchors exist but are unused; Document 7 sections 2.2-2.4 not built. | Build Document 7's evidence anchors: unit tiers from sourced pre-season evidence, then updated from the branch's own results; widen the edge scale so tiers matter. | Yes | The evidence source for each club's opening tier (for example 2012 results and sourced pre-season rankings), how fast in-season results move it, and whether Jacksonville's staff evaluation feeds it |
| 2 | **Half-final drives take the whole remaining clock.** A drive that ends a half is given every second left, however many snaps it had. | 5 plays over 9:20, 10 plays over 9:49; the Colts' decisive Week 17 drive had two completions at 0:01 and 0:00. Over 50 s per snap in 13 of 147 end-of-game finals (2012: 0 of 256). | Replay the tuple's own seconds and add a clock-runs-out leg, or match tuples on time left within about 10%. Add a seconds-per-snap coherence class. | Yes | None |
| 3 | **Fourth-down distance and first downs contradict the drive's yardage.** The replayed drive keeps its real down and distance and chain counts when its start spot moves. | Distance = 10 minus net holds in 290 of 855 no-first-down receipt drives (2012 pool: 1,484 of 1,508). 4.4% of 10-plus-yard non-TD drives show no first down (2012: 0.5%). | Derive the published down, distance and first downs from the replayed yardage, or choose tuples that preserve start minus end. Add coherence classes. | Display and team counters | None |
| 4 | **Players never leave a game.** Injuries are drawn after the final whistle; an injured player keeps his full game, and a second passer is forbidden. | 437 injuries in 300 synthetic games, all post-game. QB1 attempt share 1.000 (2012: 0.978). | Draw injuries per drive on the possession stream, remove the player and promote by depth; allow a passer change. | Yes | Whether in-game injuries may end a Jacksonville player's game without a Stone decision (a user-controlled pause) |
| 5 | **Injury model bugs.** Position multipliers are keyed by group but read by raw position, so linemen, defensive backs and most linebackers get 1.0; every dressed player, backups and specialists included, gets the same exposure; head and neck is 27% of injuries. | `runtime/injuries.py` POSITION_MULTIPLIER; `kernel.py` injury loop. | Key by group; scale exposure by snaps played (now recorded for linemen, derivable for others); source the injury-class mix. | Yes (injuries) | None |

## Tier 2: visible play-by-play and decision bugs

| # | Defect | Evidence | Proposed fix | Changes results | Decision |
|---|---|---|---|---|---|
| 6 | Kicks and kneels stamped at 0:00 after a play that left the clock running; snaps evenly spaced; no timeout or two-minute-warning rows | 155 kicks and 187 kneels at 0:00 in 300 synthetic games; every Jacksonville punt and field goal shares the previous snap's clock | Stamp snaps by play type (running clock versus stoppage), leave kicks a play-clock interval after the last snap, show charged timeouts | Display only | None |
| 7 | First half runs out in field-goal range with no attempt | 14 of 110 clock-expired first halves end inside the 30 (2012: 5 of 163) | Keep clock tuples' own end spot, or mask them in field-goal range while the offence holds a timeout | Yes | None |
| 8 | No two-point tries; always kick when down 2 late | 10 fourth-quarter TDs in 300 games left the team down 2 | A sourced 2012 two-point decision chart and success rate | Yes | None |
| 9 | No onside kicks | 19 deep kickoffs in 300 games by a team trailing 1-8 with 2:00 or less | Onside branch from 2012 onside records, by score and time | Yes | None |
| 10 | Field goals while down 9-20 in the last two minutes | Down 20 with 0:18 left (Week 12); down 14 with 0:58 in the Super Bowl | Split the "trail 9+" need, or refuse a field goal that leaves a two-score deficit inside 2:00 | Yes | None |
| 11 | Penalties are counters only, all against the offence, one yardage per drive | 5.0-5.3 flags and 38-40 yards per team game (2012: 6.37 and 54.2); no band row | Sample real penalty records with each drive; add a band row | Yes (team counters, possibly yardage) | None |
| 12 | Every fumble is lost; the same defender forces and recovers | 0.49 fumbles per team game (2012: 1.46, 0.70 lost) | Add fumbles recovered by the offence; credit a separate recoverer; model muffs | Yes | None |
| 13 | Blocked punts shown as a 0-yard punt with a penalty-like enforcement | About 9 per 300 games | A blocked-kick row with a blocker and recovery | Display and credit | None |
| 14 | Overtime trailer replays two-minute-drill drives (a spike with 12:04 left in OT) | Synthetic sample; Week 18 | Condition overtime draws on overtime drives only | Yes | None |

## Tier 3: realism gaps and calibration

| # | Gap | Evidence | Proposed fix | Changes results |
|---|---|---|---|---|
| 15 | No defensive or return touchdowns | 2012 had 134; about 1 point per team game missing (21.7 against 22.8) | Sourced non-offensive scoring on turnovers and returns | Yes |
| 16 | Rushing runs high, and no band row grades it | 4.58 yards per carry (2012: 4.26); 127.8 rushing yards per team game (115.9); completion 63.3% (60.9%) | Add band rows for yards per carry, completion rate and the run/pass split; recalibrate the yard split | Yes |
| 17 | First half ends on a field goal too often (known detections) | First-half finals 56% field goal, 37% clock (2012: 27%, 64%) | Revisit the first-half half-final redirect | Yes |
| 18 | Field-goal make rate flat from 50 yards | 55+ yards made 34 of 48 | A distance fit | Yes |
| 19 | Individual production is league-average by depth: every club had a 1,000-yard rusher; season leaders are flat | 2013 leaders: 4,370 passing, 1,648 rushing, 14 sacks | Follows item 1 and per-player tiers (Document 7 section 2.2) | Yes |
| 20 | Weather, venue and game plans enter only the packet hash | `kernel.py` packet | Design question: which plan choices move which draws | Yes |
| 21 | Game-day actives: the Jets dressed 42-44 all season; background clubs never promote replacements | Receipts | Promote by depth for background clubs each week | Inputs |

## Display and records (no result change)

- **Box score total yards** adds gross passing yards; the NFL uses net (minus sack yards). Fixing it would re-render every 2013 box score.
- **The `tackler` field** holds the pass defender on incompletions.
- **Kick returns** are still counted on kickoffs that go out of bounds, are fair-caught or are muffed (coverage tackles are not).
- **Unrecorded 2013 defect:** the Week 9 San Diego-Washington tie came from the whole-period overtime defect that Entry 50 records for Week 10 (San Diego's nine-play overtime drive clocked from 13:25 to 0:00). Recorded in Entry 72; the result stands.
- **Library data:** the 2013 Week 1 depth library files the Jets' DT Sheldon Richardson as an offensive tackle (`scripts/research/build_2013_week1_depth_charts.py`), so the engine has counted him as a lineman. 2014 TeamInputs need a rebuilt library in any case.
- **2014 tooling:** receipt, box-score and statbook paths are hard-wired to `career/2013/` (`scripts/render_box_score.py` RECEIPTS and similar). They must take the season before any 2014 game closes.
- **Coherence coverage:** nothing checks down and distance per snap, fourth-down distance against net, first downs against yards, seconds per snap, kicks after 0:00, penalties, turnover transitions, late-game decision sanity or injury participation.
