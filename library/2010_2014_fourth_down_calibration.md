# 2010-2014 fourth-down calibration

[B9F specification](2014_6_fourth_down_specification.md) · [Pre-build specification](2014_6_pre_build_specification.md) · [League base](2010_2014_calibration_base.md) · [Engine decisions](../runtime/2014_engine_decisions.md#fourth-downs-stones-live-call-batch-b9f-added-to-the-plan)

**What this is.** The league record behind kernel 2014.6's fourth downs (batch B9F): the league decision chart (go, field goal or punt), the conversion rates, the real fourth-down attempt records the engine replays and the field-goal snap offset. The artifact is `library/data/2010_2014w4_fourth_down_decisions.json`, built by `scripts/research/build_2010_2014_fourth_down_decisions.py` with a `--check` mode, under rules frozen in the B9F specification before the builder counted any row.

**Data window.** NFL regular seasons 2010-2013 and 2014 Weeks 1-4 (games through September 29, 2014), read only through the batch B2 source gate. 2013 and 2014 Weeks 1-4 are an anonymous post-divergence league population: they enter pooled counts only. No club's, game's or player's own row is stored. Overtime decisions count from 2012, the first season of modified sudden death in the regular season.

## How each piece is counted

- **Decisions.** Every regular-season snap at fourth down whose play is a punt, a field goal, a run or a pass. Plays wiped out by a penalty (no play), kneels and spikes are not decisions. A run or a pass is a decision to go, a fake from kick formation included.
- **The chart.** Six distance bins (1, 2, 3-4, 5-7, 8-10, 11 or more), ten field zones by the line of scrimmage and four kinds of game state: neutral, the last two minutes of the first half, the fourth quarter's last ten minutes by time bucket and score need, and overtime by margin. A thin cell (under 30 decisions) gives way to the next rung of the adopted ladder (amendments F1 and F2, below): the same game state with coarse distance and coarse field zone, then every distance in that coarse zone, then (the last two minutes only) every distance on the same side of the opponent's 40, then the same rungs with the fourth quarter's time buckets (or overtime's margins) merged, then the neutral state by distance and zone, coarse distances, and finally the zone alone. A trailing overtime offense's punt share moves to going for it (the pre-build specification's R14). The frozen ladder's and F1's assignments are kept in the artifact for the record.
- **Conversion.** Every go with no penalty flag on the play. It converts when the offense scores a touchdown or gains the distance, with no interception and no lost fumble. The rate is kept by distance bin and goal to go; a thin goal-to-go or field split takes its bin's pooled rate.
- **Attempt records.** Each conversion row is kept as an anonymous record: its distance, goal to go, kind of play, yards and result. The engine replays a record of the right distance bin and result, feasible from the game's own line.
- **Field-goal offset.** A field goal decided where the replayed drive did not kick is kicked from the line plus the modal snap offset of real fourth-down kicks.

## Decision source

Every club and every autonomous run decides by this chart. Jacksonville's fourth downs belong to Stone in user-controlled games: a live answer, or a standing rule on the frozen sheet. One resolution applies to all 32 clubs: the conversion, field-goal and punt outcomes come from these rates with the same matchup terms. A decision drawn from the league chart is never narrated as Stone's or a coach's.

## Two passes

The primary pass reads nflverse through the committed loader. The second pass reads nflscrapR's raw rows with separately written parsing, its own goal-to-go column and its own flags. Both files derive from the NFL GSIS feed, so the second pass checks the parse, not an independent observation of the seasons.

Three adopted cells lie outside two standard errors (listed in the figures), all in the fourth quarter's late trailing states: the last two minutes trailing by 4-8 inside the opponent's 40, the last two minutes trailing by 1-3 at the opponent's 40 or beyond, and the last ten minutes trailing by 1-3 at the opponent's 10-29. nflscrapR's running score difference reads them differently: in spot checks of four of the rows (2010 and 2013 punts, 2011 and 2013 field goals) its offense score is one point short of nflverse's, so a tied club reads as trailing by 1 and a club trailing by 3 as trailing by 4, while nflverse's score agrees with the play (a tied club punting, a field goal that ties). Pass 1's counts stand (the specification's rule). The other 177 cells and all 18 conversion pairs agree.

## Amendment F1 (the collapse ladder)

The frozen ladder was run and printed first. It served almost every late, end-of-half and overtime key from the neutral state, which would have made a club trailing by 4-8 in the last two minutes punt from the opponent's 40s where the real clubs of that state went for it nearly every time. Amendment F1, made before any kernel use, keeps the game state with coarser distance and field position before it gives way to the neutral state, and never drops the field zone below its coarse zone, so a field-goal decision always follows the kick's distance. Its rungs, the disclosure and the frozen ladder's assignment for the record are in the artifact's `amendments` block and in the figures below. MIN_CELL, the bins, the states and the counts are unchanged, and no target rate was used.

## Amendment F2 (the last two minutes and trailing overtime)

The F1 chart's first acceptance runs (October 16, 2026; `runtime/README.md`, batch B9F) showed three trailing-overtime punts against the zero-tolerance row of the pre-build specification's R14, and more punts by clubs trailing by 1-8 late than the drawn drives had shown. Read back on its own rows, the F1 chart decided 357 gos in the last two minutes of the fourth quarter where the real clubs went 449 times: when a last-two-minutes cell was thin, F1 merged it with the 2:01-10:00 buckets, where a trailing club still has time to punt (fourth and 1 in its own territory, trailing by 4-8: 42/0/108 against the state's own 141/0/1). Amendment F2, made before any release, widens the field zone within the last two minutes' own state to one side of the opponent's 40 (inside it nearly every fourth-down field goal is kicked: the counts are in the figures) before the time bucket is merged, widens every merged state the same way before the neutral state, and applies R14 to the chart. One alternative was considered and is kept for the record: widening every late state before merging, which reads the earlier time buckets worse. The read-back table below shows each ladder against the real decisions. MIN_CELL, the bins, the states and the counts are unchanged.

## Figures

<!-- generated:begin -->
Generated by `scripts/research/build_2010_2014_fourth_down_decisions.py` from the artifact; do not edit.

| Centre | Count | Of | Value |
|---|---|---|---|
| go share | 1915 | 16226 | 0.1180 |
| field goal share | 3878 | 16226 | 0.2390 |
| punt share | 10433 | 16226 | 0.6430 |
| attempts per team game | 1915 | 2170 | 0.8825 |
| decisions per team game | 16226 | 2170 | 7.4774 |
| conversion rate | 906 | 1892 | 0.4789 |

| Season | Go | Field goal | Punt | Converted | Attempts (no flag) | Team-games |
|---|---|---|---|---|---|---|
| 2010 | 481 | 883 | 2437 | 237 | 477 | 512 |
| 2011 | 426 | 924 | 2477 | 184 | 419 | 512 |
| 2012 | 447 | 921 | 2469 | 222 | 442 | 512 |
| 2013 | 468 | 932 | 2526 | 221 | 463 | 512 |
| 2014w4 | 93 | 218 | 524 | 42 | 91 | 122 |

Season drift: go share chi-square 4.800 on 4 df, p 0.308; conversion rate p 0.361; attempts per team-game (Poisson) p 0.200.

**Conversion pairs** (converted / attempts; `field` is not goal to go; a split under 30 attempts reads its distance bin's pooled pair):

| Distance | Goal to go | Field | Pooled | Adopted for goal / field |
|---|---|---|---|---|
| 1 | 47/101 | 401/609 | 448/710 (0.631) | 1|goal / 1|field |
| 2 | 13/22 | 98/196 | 111/218 (0.509) | 2|any / 2|field |
| 3-4 | 7/21 | 116/244 | 123/265 (0.464) | 3-4|any / 3-4|field |
| 5-7 | 7/23 | 92/244 | 99/267 (0.371) | 5-7|any / 5-7|field |
| 8-10 | 3/7 | 82/231 | 85/238 (0.357) | 8-10|any / 8-10|field |
| 11-99 | 2/7 | 38/187 | 40/194 (0.206) | 11-99|any / 11-99|field |

Go rows with a penalty flag left out of the conversion rows: 23.

Field-goal snap offset (kick distance less the line, fourth-down kicks): modal 18; counts 17: 153, 18: 3491, 19: 233, 29: 1.

**Chart cells, neutral state** (go / field goal / punt; the adopted cell of each distance and zone):

| Distance \ zone | 1-4 | 5-9 | 10-19 | 20-29 | 30-34 | 35-39 | 40-49 | 50-59 | 60-69 | 70-99 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 91/53/0 | 22/21/0 | 46/46/0 | 64/42/0 | 45/11/0 | 54/2/6 | 74/0/57 | 39/0/144 | 19/0/155 | 18/0/295 |
| 2 | 10/89/0 | 4/44/0 | 12/62/0 | 6/56/0 | 15/28/0 | 27/8/9 | 18/0/86 | 7/0/104 | 1/0/112 | 3/0/234 |
| 3-4 | 5/124/0 | 5/77/0 | 7/136/0 | 9/127/0 | 21/54/1 | 20/12/44 | 18/1/172 | 4/0/231 | 4/0/230 | 6/0/442 |
| 5-7 | - | 6/211/0 | 7/193/0 | 6/178/1 | 13/105/9 | 19/27/55 | 9/1/275 | 8/0/358 | 3/0/410 | 1/0/756 |
| 8-10 | - | 1/69/0 | 2/186/0 | 4/193/0 | 10/68/8 | 4/29/41 | 8/1/235 | 7/0/267 | 0/0/372 | 2/0/743 |
| 11-99 | - | - | 3/164/0 | 3/215/0 | 12/112/9 | 6/45/81 | 1/2/272 | 4/0/342 | 0/0/393 | 2/0/1282 |

Reachable keys by the rung that served them (amendment F2, adopted): full 64, coarse 103, zone_state 401, wide_state 216, coarse_merged 66, zone_merged 406, wide_merged 272, neutral 96, distance_coarse 0, zone_only 0; 180 distinct cells. Under amendment F1, for the record: full 64, coarse 103, zone_state 401, coarse_merged 101, zone_merged 547, neutral 408, distance_coarse 0, zone_only 0 (488 keys moved by F2). Under the frozen ladder, for the record: full 64, time_merged 33, zone_coarse 129, neutral 1398, distance_coarse 0, zone_only 0 (1152 keys moved by F1).

**Amendment F1** (after the frozen ladder (specification section 3) was run and printed, before any kernel use): the collapse ladder: a late (fourth quarter, 600 s or less), first-half (120 s or less) or overtime state is kept, with coarse distance and zone, then any distance and coarse zone, then with its time buckets (overtime margins) merged, before it gives way to the neutral state; a field zone, at least its coarse zone, is kept on every rung. Disclosure: the frozen ladder served 1398 of 1624 reachable keys from the neutral state and kept a late, first-half or overtime state for only 226; for 5-7|40-49|q4|le120|trail4_8 (fourth and 5-7 at the opponent's 40-49, trailing by 4-8 in the last 2:00) it read the neutral cell 5-7/40-49/neutral (go/field goal/punt 9/1/275) where the real clubs of that state decided 141/0/1; amendment F1 reads */Z40-59/q4|le120|trail4_8 (34/0/0). The amendment changes the rung order on structural grounds (the game state before the field geometry for late decisions; the zone always kept so a field-goal decision follows the kick distance); MIN_CELL, the bins, the states and the counts are unchanged, and no target rate was used.

**Amendment F2** (after the acceptance runs of the F1 chart (October 16, 2026: three trailing-overtime punts against R14's zero-tolerance row, and the late trailing-punt rows; runtime/README.md, batch B9F), before any kernel release): the collapse ladder and one mask: a last-two-minutes state (q4|le120|<need>) widens its field zone to the field-goal-range boundary (wide zones 1-39 and 40-99) within that state before its time bucket is merged with the earlier ones, and every merged state widens its zone the same way before it gives way to the neutral state; the pre-build specification's R14 applies to the chart (a trailing overtime offense's punt share moves to go). Disclosure: the F1 chart read back on its own rows decided fewer gos than the real clubs: in the last two minutes of the fourth quarter F1 357.4 against 449 real, overall F1 1787.6 against 1915 real; for 1|70-99|q4|le120|trail4_8 (fourth and 1 in the club's own territory, trailing by 4-8 in the last 2:00) F1 read */Z60-99/q4|le600|trail4_8 (go/field goal/punt 42/0/108) where the real clubs of that state decided 141/0/1, because merging the last two minutes with the earlier time buckets brought in clubs that still had time to punt; amendment F2 reads */W40-99/q4|le120|trail4_8 (61/0/1). Wide zones split the field at the opponent's 40: 24 of the 10893 real fourth-down decisions at the opponent's 40 or beyond were field goals, against 3854 of 5333 inside it. The alternative of widening every late state before merging (for the record) reads wide_all 422.6 against 449 real and wide_all 1838.2 against 1915 real; F2 was chosen over it by this read-back on the 2010-2014 rows (its earlier time buckets read closer under F1's merge), not by an acceptance reading. R14's mask moves a trailing overtime offense's punt share to go. MIN_CELL, the bins, the states and the counts are unchanged.

**The chart read back on its own rows** (each state group's real decisions, then the sum over its rows of their adopted cells' probabilities, the masks applied; go / field goal / punt):

| State group | Real | Frozen ladder | F1 | Every state widened (alternative) | F2 (adopted) |
|---|---|---|---|---|---|
| all | 1915 / 3878 / 10433 | 1273.5 / 4138.2 / 10814.3 | 1787.6 / 3915.1 / 10523.3 | 1838.2 / 3899.8 / 10488.0 | 1883.1 / 3889.2 / 10453.8 |
| h1_le120 | 89 / 426 / 589 | 105.5 / 396.8 / 601.7 | 83.1 / 430.5 / 590.3 | 83.1 / 430.5 / 590.3 | 83.1 / 430.5 / 590.3 |
| neutral | 815 / 2792 / 8231 | 815.0 / 2792.0 / 8231.0 | 815.0 / 2792.0 / 8231.0 | 815.0 / 2792.0 / 8231.0 | 815.0 / 2792.0 / 8231.0 |
| ot | 9 / 24 / 40 | 8.6 / 21.1 / 43.3 | 8.6 / 21.1 / 43.3 | 10.7 / 22.1 / 40.2 | 13.2 / 22.1 / 37.7 |
| q4|121-300 | 309 / 188 / 499 | 105.6 / 267.4 / 623.0 | 283.9 / 189.0 / 523.1 | 289.8 / 185.9 / 520.3 | 290.5 / 187.9 / 517.6 |
| q4|301-600 | 244 / 274 / 793 | 128.1 / 348.3 / 834.7 | 239.6 / 278.3 / 793.0 | 217.0 / 280.3 / 813.7 | 258.6 / 267.8 / 784.6 |
| q4|le120 | 449 / 174 / 281 | 110.7 / 312.6 / 480.7 | 357.4 / 204.1 / 342.5 | 422.6 / 188.8 / 292.6 | 422.6 / 188.8 / 292.6 |

**Decisions by game state** (go / field goal / punt):

| State | Go | Field goal | Punt |
|---|---|---|---|
| neutral | 815 | 2792 | 8231 |
| h1_le120 | 89 | 426 | 589 |
| q4|le120|lead9 | 59 | 28 | 100 |
| q4|le120|lead1_8 | 14 | 53 | 123 |
| q4|le120|tied | 3 | 28 | 47 |
| q4|le120|trail1_3 | 52 | 46 | 1 |
| q4|le120|trail4_8 | 141 | 0 | 1 |
| q4|le120|trail9_11 | 35 | 17 | 0 |
| q4|le120|trail12_16 | 51 | 0 | 1 |
| q4|le120|trail17p | 94 | 2 | 8 |
| q4|121-300|lead9 | 31 | 55 | 164 |
| q4|121-300|lead1_8 | 7 | 70 | 171 |
| q4|121-300|tied | 2 | 12 | 25 |
| q4|121-300|trail1_3 | 22 | 18 | 32 |
| q4|121-300|trail4_8 | 62 | 10 | 49 |
| q4|121-300|trail9_11 | 30 | 20 | 5 |
| q4|121-300|trail12_16 | 79 | 1 | 10 |
| q4|121-300|trail17p | 76 | 2 | 43 |
| q4|301-600|lead9 | 15 | 81 | 239 |
| q4|301-600|lead1_8 | 5 | 75 | 182 |
| q4|301-600|tied | 3 | 18 | 54 |
| q4|301-600|trail1_3 | 7 | 33 | 63 |
| q4|301-600|trail4_8 | 28 | 33 | 103 |
| q4|301-600|trail9_11 | 21 | 22 | 39 |
| q4|301-600|trail12_16 | 62 | 2 | 34 |
| q4|301-600|trail17p | 103 | 10 | 79 |
| ot|trail | 4 | 2 | 0 |
| ot|tied | 5 | 22 | 40 |
| ot|lead | 0 | 0 | 0 |

**Second pass (nflscrapR)**

| Metric | nflverse | nflscrapR | Within 1% |
|---|---|---|---|
| go decisions | 1915 | 1904 | yes |
| field_goal decisions | 3878 | 3861 | yes |
| punt decisions | 10433 | 10383 | yes |
| decision rows | 16226 | 16148 | yes |
| conversion attempts | 1892 | 1888 | yes |
| conversions | 906 | 902 | yes |

Adopted cells within 2 SE: 177 of 180. Conversion pairs within 2 SE: 18 of 18. Modal field-goal offset: nflverse 18, nflscrapR 18. The source's goal_to_go column equals distance at the line: True. Disagreements: cell */W1-39/q4|le120|trail4_8, cell */W40-99/q4|le120|trail1_3, cell */Z10-29/q4|le600|trail1_3.
<!-- generated:end -->
