# Kernel 2014.6 batch B9F fourth-down specification, written before its rates were counted

**Written October 15, 2026, before the B9F builder (`scripts/research/build_2010_2014_fourth_down_decisions.py`) counted any fourth-down decision, conversion or kick offset from the 2010-2014 sources.** The author knows the published league-wide magnitudes (about one fourth-down attempt per team-game, about half of them converted) from general football knowledge, not from these files. The bins reuse the frozen rules of the [pre-build specification](2014_6_pre_build_specification.md) where they exist (its data window, structural filters, MIN_CELL, late time buckets and needs). This file is never edited: `scripts/research/fourth_down_specification.py` pins its sha256, and the B9F artifact header records that digest and the pre-build specification's.

Authority: Stone's standing instruction of October 2, 2026 (18:55), "Fourth downs remain my call. I want the decision prepared before third down whenever possible. Skalaski gives me distance, field position, score, timeouts, clock and the kicking information; Tice gives me the best prepared conversion call", and the one-resolution rule recorded with it ([Kernel 2014.6 decisions](../runtime/2014_engine_decisions.md#fourth-downs-stones-live-call-batch-b9f-added-to-the-plan)).

## 1. Data

- NFL regular seasons 2010-2013 and 2014 Weeks 1-4 (games through September 29, 2014), read only through the batch B2 gate (`scripts/research/sources_2010_2014.py`). The 2014 rows are an anonymous post-divergence league population, as for every 2014.6 artifact.
- Overtime decisions from 2012 only (the pre-build specification's structural filter: modified sudden death in the regular season from 2012).
- Equal weight per event. Integer counts per season are stored.
- Pass 1 reads nflverse play-by-play; pass 2 reads nflscrapR with separately written code. Only aggregate counts and anonymous play records are committed: no club, game, player or date field.

## 2. Decision rows and the decision

- A decision row is a regular-season snap with `down` 4 and `play_type` punt, field_goal, run or pass. Rows whose play was nullified (`play_type` no_play), kneels and spikes are not decisions (a fourth-down kneel or spike is a clock play of the replayed drive; defect register item 30).
- The decision is `punt` (play_type punt), `field_goal` (play_type field_goal) or `go` (run or pass, a fake from punt or field-goal formation included).
- The state of a row: its `ydstogo`, its `yardline_100` (the line of scrimmage as yards to the opponent's goal line, the kernel's spot), `goal_to_go`, the offense's score difference before the snap, and its clock.

## 3. The decision chart

- Distance bins: 1, 2, 3-4, 5-7, 8-10, 11 or more.
- Field zones (yardline_100): 1-4, 5-9, 10-19, 20-29, 30-34, 35-39, 40-49, 50-59, 60-69, 70-99.
- Game states:
  - `ot|trail`, `ot|tied`, `ot|lead`: overtime (2012 onward), by the offense's margin;
  - `q4|<bucket>|<need>`: the fourth quarter with 600 s or less left, by the pre-build specification's late time buckets (le120, 121-300, 301-600) and its eight needs;
  - `h1_le120`: the first half with 120 s or less left in it;
  - `neutral`: every other snap.
- A cell is (distance bin, zone, state). Its counts are the decision rows' go, field_goal and punt counts (pass 1).
- Collapse ladder, applied to every reachable key, most specific first; the first rung whose cell holds at least MIN_CELL (30) decision rows is the key's cell:
  1. `full`: (distance bin, zone, state);
  2. `time_merged`: a q4 state's time buckets merged, (distance bin, zone, `q4|<need>`); other states skip this rung;
  3. `zone_coarse`: (distance bin, coarse zone, the rung-2 state), coarse zones 1-9, 10-29, 30-39, 40-59, 60-99; the neutral state skips this rung;
  4. `neutral`: (distance bin, zone, neutral);
  5. `distance_coarse`: (coarse distance, zone, neutral), coarse distances 1-2, 3-7, 8 or more;
  6. `zone_only`: (zone, neutral), every distance.
  A key no rung serves is a build error.
- The chart decision: one uniform u per decision point; go when u < go/n, field goal when u < (go + field_goal)/n, punt otherwise.

## 4. Conversion

- Conversion rows: the go rows with no penalty flag on the play (a flag's yards are not modelled in the drive replay before batch B11; the count of penalty go rows left out is reported).
- Converted: a touchdown by the offense, or `yards_gained` at least `ydstogo`, with no interception and no lost fumble on the play. An interception or a lost fumble is a failed attempt.
- Conversion pairs (converted, attempts) by (distance bin, goal to go). A pair under MIN_CELL attempts takes its distance bin's pair pooled over goal to go.
- One named E1 socket at slope 0: `conversion_edge`, the drive's matchup edge. It returns the sourced rate exactly; no admissible evidence moves it in 2014.6.

## 5. The go snap's records

- Every conversion row is an anonymous record [distance, goal_to_go, kind, yards, converted], stored by distance bin. Kind: run, complete, incomplete, sack, interception, fumble_run, fumble_catch, fumble_sack (a lost fumble by the kind of snap that lost it). Yards: `yards_gained` (a sack's loss negative; an interception's 0).
- At the decision state (distance d, line L): a converted attempt draws, uniformly on the B9F substream, a converted record of d's bin with yards at least d; its yards reaching L are a touchdown (yards = L). A failed attempt draws a failed record of d's bin whose ball stays inside the field (L - yards from 1 to 99) and, unless it is an interception or a lost fumble, with yards under d. With no feasible record the attempt gains exactly d (converted) or 0 (failed), counted.
- A named call fixes the snap's family: a run call draws run records (run, fumble_run), a pass call pass records (complete, incomplete, sack, interception, fumble_catch, fumble_sack); a mixed or unspecified call, and every chart or policy go without a call, draws from all. The call never moves the conversion probability.
- The failed kinds end the possession as: interception (the kernel's interception transition from the line of scrimmage, R15 included), lost fumble (the kernel's fumble transition from the fumbled spot, R15 included), otherwise downs at L - yards.

## 6. Field goals and punts

- A field goal decided where the replayed drive did not kick it is kicked from L + the field-goal snap offset: the modal (kick_distance - yardline_100) of the fourth-down field-goal rows (pass 1; it must be 17, 18 or 19). Its make probability is the bound base's distance model with the kicker's term, as for every field goal; a miss gives the missed-kick start; R15 applies.
- A punt is the kernel's punt draw from L with the punter and returner terms; R15 applies.
- When the decision is the replayed drive's own kick at that point, the drive is the drawn drive unchanged (its own distance and draws).

## 7. Decision points, resolution and continuation (kernel)

- A decision point is the first state with down 4 in a laid-out drive or continuation segment: before a scrimmage snap walked at down 4 (not a kneel or spike), or, for a punt or field-goal drive, the state after its last scrimmage snap when that state is down 4. A field goal kicked before fourth down (batch B6, W3), a drive with no down-4 state and a drive whose layout failed have none.
- One resolution for every club: the decision (go, field goal or punt) from its source, then the sourced outcome (sections 4-6) with the same matchup terms for every club. A go is always resolved by the model, the replayed drive's own fourth-down snap included. A punt or field goal that is the replayed drive's own kick at that point keeps the drawn drive.
- A conversion short of the goal line continues the possession on the possession stream: a continuation segment is drawn exactly as a drive from the new spot (first and ten, or goal) with the window left, the same score, the timeouts left and the same matchup edge; it is laid out on its own keyed layout stream and has its own decision points. The possession publishes one drive (its drive totals, chains, clock and credits from the joined snaps) and its segments.
- Clock: the drawn drive's snap stamps (the bound base's W5a gap and kick-length constants, `runtime.play_detail.clock_stamps`) give the decision clock: the stamp of the fourth-down snap, or of the kick. A kick decided there takes the base's kick length for its category; a go that ends the possession takes the W5a mean gap after an incompletion in its clock context (a clock-stopping snap's game-clock duration); a conversion's continuation starts after the W5a mean gap of the converting snap's kind in its clock context. A resolved act that would run past the window ends it at 0:00.

## 8. Decision sources

- Bases: `policy:i` (rule i of the club's fourth-down block; its `otherwise` decision is rule len(rules)), `delegated:league`, `live` (the controlling coach's answer through the E2 pause) and `league` (the chart).
- In a user-controlled regular-season or postseason game, the controlled club with no fourth-down block decides live (Stone's standing instruction). A block may hold standing rules, `otherwise` (a decision, league or ask) and Tice's prepared conversion calls by menu. Every other club, every autonomous game, every preseason and Pro Bowl game: the chart. A block in a preseason or Pro Bowl game, a probability, share, rate, weight or odds key and an `ask` on any club but the controlling coach's are refused before the event is journaled.
- The decision uniform and the outcome uniforms are drawn on their keyed substream in every case (the event, the drive, the segment and the decision index; no team id), so a decision source never shifts a later draw and the same decision sequence given to either side gives the same result.

## 9. Timing and the pause

- `before_third_down` when the series' third-down snap is a scrimmage play (not a spike or kneel): the pause stands before that snap, which the drawn drive will not convert. Otherwise `at_fourth_down`, before the fourth-down snap or kick. The record names which. The pause is raised only when the series reaches fourth down, so its timing implies that third down will not convert; the answer cannot change the third-down snap.
- The pause shows only what the staff supply: Skalaski's distance, field position, score, timeouts, clock, the field-goal distance from the line shown, the venue and weather of the packet and the kicker and punter on the field; and Tice's prepared conversion call (the block's call for the matching menu, when the sheet names one) with the matching menu's calls. The matching menu is the frozen sheet's most specific applicable menu with a call (fourth down takes the third-down menu of its distance). Never a probability, a chart value, a cell or a hidden make probability.
- Answers: `fourth_down` go, field_goal or punt; with go, `call`, one of the matching menu's calls (required when the menu has one).

## 10. Band rows (2014.6 cohort)

Graded (3*sqrt(p(1-p)/n) for rates, 3*sqrt(c/n) for counts; a rate under 30 events reads INSUFFICIENT SAMPLE):
- fourth-down go share of decisions, chart-decided decisions only (centre: pooled go / decision rows);
- fourth-down attempts per team-game, the team-games whose fourth downs were all chart-decided (centre: pooled go rows per team-game);
- fourth-down conversion rate, every go (centre: pooled conversion pair).

Informational: field-goal and punt shares of chart decisions; decisions per team-game; the chart-conditional go count against the sum of each chart decision's go probability; fourth downs decided by a block or a live answer, counted apart and never graded.

## 11. Two passes

Pass 2 recounts the decision rows, the cell counts, the conversion pairs and the kick offset from nflscrapR with its own code. Agreement: every pooled count within 1% of pass 1; every adopted cell's go, field-goal and punt shares and every conversion pair within 2 standard errors. A disagreement is reported; pass 1's counts are adopted (the committed source of every 2014.6 drive pool).

## 12. Seeds

- `fourth-swap-2014.6-{0..119}`: the label-swap block (Jacksonville's Week 4 inputs at a neutral site; the same labels relabelled Denver; the same decision sequence supplied to the other side).

## 13. Frozen rules (machine-readable)

<!-- frozen-rules:begin -->
```json
{
  "specification": "kernel 2014.6 batch B9F fourth-down specification",
  "written": "2026-10-15",
  "blind": "written before the B9F builder counted any fourth-down row of the 2010-2014 sources",
  "pre_build_specification_sha256": "ca028ba38009d1b84e5c887ea86ce8d697edf1705bcd9b755f60aede9d6f8446",
  "data": {"seasons": [2010, 2011, 2012, 2013, 2014], "overtime_from_season": 2012,
           "decision_play_types": ["punt", "field_goal", "run", "pass"],
           "excluded_play_types": ["no_play", "qb_kneel", "qb_spike"],
           "conversion_rows": "go rows with no penalty flag"},
  "actions": ["go", "field_goal", "punt"],
  "distance_bins": [[1, 1], [2, 2], [3, 4], [5, 7], [8, 10], [11, 99]],
  "zones": [[1, 4], [5, 9], [10, 19], [20, 29], [30, 34], [35, 39], [40, 49], [50, 59], [60, 69], [70, 99]],
  "coarse_zones": [[1, 9], [10, 29], [30, 39], [40, 59], [60, 99]],
  "coarse_distances": [[1, 2], [3, 7], [8, 99]],
  "states": {"h1_seconds": 120, "q4_seconds": 600, "ot_margins": {"trail": [-999, -1], "tied": [0, 0], "lead": [1, 999]}},
  "late_time_buckets_from": "pre-build specification end_of_half.LATE_TIME_BUCKETS",
  "needs_from": "pre-build specification end_of_half.NEEDS",
  "collapse_ladder": ["full", "time_merged", "zone_coarse", "neutral", "distance_coarse", "zone_only"],
  "min_cell_from": "pre-build specification thresholds.MIN_CELL",
  "conversion": {"split": "goal_to_go", "collapse": "distance bin pooled over goal to go below MIN_CELL attempts",
                 "converted": "offense touchdown or yards_gained >= ydstogo, no interception, no lost fumble"},
  "record_kinds": ["run", "complete", "incomplete", "sack", "interception", "fumble_run", "fumble_catch", "fumble_sack"],
  "call_families": {"run": ["run", "fumble_run"],
                    "pass": ["complete", "incomplete", "sack", "interception", "fumble_catch", "fumble_sack"]},
  "field_goal_offset": {"rule": "modal kick_distance - yardline_100 of fourth-down field-goal rows", "allowed": [17, 18, 19]},
  "sockets": {"conversion_edge": 0.0},
  "bases": ["policy:i", "delegated:league", "live", "league"],
  "controlled_default": "live in a user-controlled regular-season or postseason game without a fourth-down block",
  "timing": ["before_third_down", "at_fourth_down"],
  "answers": {"fourth_down": ["go", "field_goal", "punt"], "call": "required with go when the matching menu has a call"},
  "substream": "fourth-down-v1",
  "clock": {"kick": "W5a kick length of the category", "go_terminal": "W5a incomplete gap in the clock context",
            "go_continue": "W5a gap of the converting snap's kind in the clock context"},
  "bands": {"graded": ["fourth-down go share of decisions", "fourth-down attempts per team-game",
                       "fourth-down conversion rate"],
            "informational": ["field-goal share of fourth-down decisions", "punt share of fourth-down decisions",
                              "fourth-down decisions per team-game", "chart-conditional go count",
                              "fourth downs decided by a block or a live answer"]},
  "agreement": {"pooled_relative": 0.01, "cell_share_se": 2},
  "seeds": {"swap": {"prefix": "fourth-swap-2014.6-", "count": 120}}
}
```
<!-- frozen-rules:end -->
