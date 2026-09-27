# 2012 NFL drive model for kernel 2013.6

> **Kernel 2013.7 note.** This file documents the kernel 2013.6 reference artifact, which is unchanged and still byte-reproducible. Kernel 2013.7 keeps its category list, edge shift, clock scale, field-goal accuracy by distance and kick rates, and draws its drives from the field-position model documented in [2012_field_position_model_calibration.md](2012_field_position_model_calibration.md).

**Research date:** September 27, 2026. **Football information window:** completed 2012 regular season only (256 games, 512 team-games). **Artifact:** `library/data/2012_nfl_drive_model.json`, built by `scripts/research/build_2012_drive_model.py`. **Status:** reconciled to the stored 2012 totals; second pass passed with documented deviations; PFR cross-check unresolved (see Verification). No 2013 or later data is read, and the artifact holds no team or game identifiers.

## Sources

| Pass | File | SHA-256 (pinned in the builder) |
|---|---|---|
| Primary | nflverse `play_by_play_2012.csv.gz` ([release](https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2012.csv.gz)), `season_type == REG` | `ff1cda2e26610ef8720324e442d1e5ebc24918e08fd1d2933590b7b91a7068cd` |
| Second | nflscrapR `reg_pbp_2012.csv` ([file](https://raw.githubusercontent.com/ryurko/nflscrapR-data/master/play_by_play_data/regular_season/reg_pbp_2012.csv)) | `9129396fc41597f9f44ab14d4d0fca890a3c56fea686b0b7dc92885aaedd0f98` |

Both files derive from the NFL Game Statistics and Information System (GSIS) feed. The second pass therefore checks the classifier and the file parse; it is not an independent observation of the season. The inputs are large and are not committed. `python scripts/research/build_2012_drive_model.py --check` rebuilds the artifact and exits non-zero unless it is reproduced byte-for-byte.

## Method

**Drive.** Rows are grouped by the source drive key (`fixed_drive` in nflverse, `drive` in nflscrapR). An offensive snap is a pass, run, kneel, spike, punt or field goal by the team in possession. Two-point tries are excluded. A `no_play` row counts only when it carries an interception, fumble-lost, touchdown, safety or failed-fourth-down flag. A group with no offensive snap is not a drive.

**Result classifier.** The drive's last offensive snap decides, in this order: touchdown > safety > field goal (made or missed) > punt > interception > fumble lost > turnover on downs > clock. `clock` merges end of half and end of game: the final offensive possession of a half that ended without any other result.

**Categories.** `touchdown`, `field_goal_attempt`, `punt`, `interception`, `fumble_lost`, `downs`, `safety`, `clock`.

**Opponent-touchdown remap.** 119 drives ended in a defensive or return touchdown. The kernel does not model the defence's score, so each is remapped to the play that caused it: 71 interception returns to `interception`, 19 fumble returns to `fumble_lost`, 27 punt returns or blocked punts to `punt`, and 2 blocked-field-goal returns to `field_goal_attempt` (missed). No opponent-touchdown drive remained unclassified.

| Category | Drives | Mean plays | Mean net yards | Mean seconds |
|---|---:|---:|---:|---:|
| touchdown | 1,164 | 7.42 | 66.27 | 208.5 |
| field_goal_attempt | 1,016 | 7.59 | 45.51 | 228.7 |
| punt | 2,467 | 4.28 | 11.30 | 129.8 |
| interception | 468 | 4.47 | 21.50 | 110.9 |
| fumble_lost | 280 | 4.40 | 22.87 | 114.7 |
| downs | 200 | 7.66 | 33.75 | 174.7 |
| safety | 13 | 2.31 | -4.92 | 65.5 |
| clock | 376 | 2.90 | 9.12 | 66.9 |
| **Total** | **5,984** | | | |

**Tuples.** Each drive is stored as `[plays, net_yards, seconds]`; a field-goal drive adds `[kick_distance, made, blocked]`. Plays are scrimmage snaps (pass, run, kneel, spike); the punt or field-goal snap is not counted. Net yards are the yard line of the first snap minus the end spot: 0 for a touchdown, the line of scrimmage for a punt or field goal, otherwise the line of scrimmage minus yards gained on the last snap. Penalty yardage is therefore included. Seconds are the source drive time of possession. When blank (244 drives: 83 field-goal, 82 interception, 37 punt, 21 fumble, 14 touchdown, 7 downs), seconds are imputed as plays times that category's mean seconds per play; this is an imputation, not an observation.

**Pools.** `interior` holds every drive that is not the final offensive possession of a regulation half (5,472 drives; overtime drives are interior). `half_final` holds the final offensive possession of each regulation half (512 drives), keyed by `half_seconds_remaining` at its first snap.

**Pre-registered bucket edges** (fixed before any 2013.6 measurement, never changed after): `[0-30]`, `[31-60]`, `[61-120]`, `[121-240]`, `[241-1800]` seconds. **Collapse rule, fixed in code:** a bucket with fewer than 30 drives merges into the next larger bucket (the largest merges into the next smaller). Raw half-final counts were 179, 128, 130, 56 and 19; the `[241-1800]` bucket (19) therefore merged into `[121-240]`, which holds 75 drives.

**Rates (stored as integer pairs).**

| Figure | Value | Verification |
|---|---|---|
| Field goals made/attempted | 852/1,016 | two-source (same GSIS feed) plus stored period totals |
| FG by distance, <30 | 231/239 | two-source (same GSIS feed), PFR unverified |
| FG by distance, 30-39 | 270/303 | two-source (same GSIS feed), PFR unverified |
| FG by distance, 40-49 | 259/323 | two-source (same GSIS feed), PFR unverified |
| FG by distance, 50+ | 92/151 | two-source (same GSIS feed), PFR unverified |
| Missed field goals | 164 (nflverse: 143 missed + 21 blocked) | total verified in both files; the blocked/missed split is unresolved: nflscrapR shows 145/19 because two kicks (2012101407 play 4223, 2012110400 play 3608) are BLOCKED in the nflverse descriptions but No Good in the nflscrapR descriptions. The kernel does not use the split |
| Extra points good/attempted | 1,229/1,237 (4 blocked, 2 failed, 2 aborted) | partially verified: nflscrapR shows the same 8 non-good kicks but is missing 115 rows; PFR unverified |
| Two-point tries | 29/56 | single source (nflscrapR is missing 6 rows); documentation only, not used by the kernel |
| Safeties | 13 | two-source; the scoring decomposition 6 x 1,297 + 1,229 + 2 x 29 + 3 x 852 + 2 x 13 = 11,651 matches period totals exactly |
| Safety free kicks returned / not returned | 13 / 0 | single source |
| Touchdown type, pass share | 757/1,158 | stored baseline tables (NFL.com); nflverse counts 1,163 offensive touchdowns, a 5-touchdown definitional difference |
| Offensive-drive turnover type, interception share | 468/748 | derived from the remapped two-source counts (748 here is not the period-total fumble count, which is also 748 by coincidence) |
| Clock scale | 921,600 / 940,322 | single source; 3,600 x 256 seconds over the sum of tuple seconds |

## Reconciliation (builder exits non-zero on failure)

| Check | Result |
|---|---|
| interior + half_final = 5,984 | 5,472 + 512 = 5,984 |
| FGA = period total 1,016 | 1,016 |
| FGM = period total 852 | 852 |
| Interceptions = period total 468 | 397 + 71 remapped = 468 |
| Plays per team-game within 0.1 of 64.2 | 64.22 |
| Net yards per team-game within 1.0 of 347.2 | 347.33 |

Because plays and net yards come from the same resampled drives, kernel 2013.6 no longer needs the 2013.5 `plays_scale`.

## Second pass (nflscrapR)

The identical classifier runs on the nflscrapR file. Any count differing by more than 1%, or any category mean net-yards figure differing by more than 0.6 yards, fails the build unless listed with an explanation. Result: **pass**. Category counts match or sit within 1% (field-goal attempts 1,013 against 1,016, fumbles lost 279 against 280, punts 2,456 against 2,467); every category mean net differs by at most 0.29 yards. The documented, explained deviations are:

- nflscrapR has 414 fewer regular-season rows (45,415 against 45,829), including 115 fewer extra-point results, 6 fewer two-point results and 225 fewer rows with a blank play type;
- nflscrapR has 92 fewer pass, 11 fewer punt and 3 fewer field-goal rows and 64 more `no_play` rows, which leaves 15 drives without a terminal offensive play (`other`);
- nflscrapR repeats one touchdown description (2012112200, plays 2563 and 2658, the second with a penalty appended);
- the two kicks listed above, BLOCKED in nflverse and No Good in nflscrapR (split unresolved).

**Pro Football Reference cross-check: unresolved.** PFR's drive table (5,360 drives) and punt total (2,520) could not be reached through the session proxy, nor could a web archive copy. The earlier PFR-derived drive shares (.221/.158/.466/.132/.023) are retired from kernel use; they are not explained.

## Definitional change, not tuning

The drive denominator for kernel 2013.6 is nflverse's 5,984 drives, 11.6875 per team-game, not PFR's 5,360 (10.46875). The play-by-play definition counts end-of-half possessions and split possessions that PFR does not. This is a change of definition, recorded here and in the band audit labels.

## Unmodelled components

- Non-offensive touchdowns (134 in 2012, including 14 kickoff-return touchdowns), their tries, and 2-point tries. Remapped opponent-touchdown drives give the defence no score. Points therefore run below the 2012 centre by design (about 1.7 to 2.0 points per team-game).
- Onside kicks, fake kicks, and special-teams fumbles lost (358 - 280 = 78 in 2012).
- Field position, start spots and down-and-distance are not published by kernel 2013.6. Kernel 2013.7 publishes start and end spots from the 2012 field-position model ([2012_field_position_model_calibration.md](2012_field_position_model_calibration.md)); snap-level down and distance remain unpublished.

## How the kernel uses the model

`runtime/drive_model.py` validates the artifact and draws a category (the interior mix, shifted by the legacy anchor/home edge), then a uniform real drive of that category. If that drive's scaled seconds would reach the end of the half, the possession instead draws from the half-final pool for the pre-registered bucket of time remaining, filtered to drives that fit. A `clock` draw, or no drive that fits, expires the half. A half-final possession always runs out the half (or overtime period): nothing follows it in that window. This corrects the double-final defect found by the 2013.6 acceptance audit, in which leftover time started a further, almost always clock-expired, possession. The field-goal make/miss uses the stored accuracy for the tuple's kick distance. See `runtime/README.md` for the full 2013.6 contract.

## Known kernel 2013.6 limitations (from the acceptance audit)

- **Punt bias.** Kernel 2013.6 draws an interior drive first and redirects to the half-final pool only when that drive would overrun the window. Long touchdown and field-goal drives overrun more often, so the interior drives that survive are skewed short and punt-heavy. In the 250-game test sample: about 11.0 interior drives per team-game against 10.69 in 2012 (5,472 / 512), and an interior punt share of 0.464 against the pool's 0.450. That is roughly +0.2 to +0.3 drive-ending punts per team-game. The row stays graded in the band audit; it is a follow-up for a later kernel and was not tuned.
- **Kickoffs.** The 2012 kickoff centre (PFR 2,665; play-by-play 2,620) includes kicks this model does not generate: after non-offensive touchdowns, onside kicks, re-kicks, and after a half-final score. The band audit shows that row as informational only.
