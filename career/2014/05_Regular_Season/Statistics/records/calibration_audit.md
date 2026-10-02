# 2014 statistical band audit

**Version:** `2014-W01-BAND-AUDIT`
**Through:** Week 1.

League-wide receipts compared with the sourced 2012 shapes in `library/data/2012_nfl_aggregate_baseline.json`, `library/data/2012_nfl_position_usage_baseline.json`, `library/data/2012_nfl_drive_model.json` and `library/data/2012_nfl_field_position_model.json`. This is a defect detector for engine code and TeamInputs. An OUTSIDE row is investigated; it never reruns, selects or edits a closed game. Receipts are split into cohorts by kernel version; grading starts at 16 team-games per cohort.

## Legacy cohort: kernels 2013.4/2013.5

**Status:** legacy kernel, known snap-record defects (see the [September 8, 2013 Kansas City game report](../../../../2013/regular_season/week_01_kansas_city_at_jacksonville/output.md) and [September 22, 2013 Seattle game report](../../../../2013/regular_season/week_03_jacksonville_at_seattle/output.md)), detection only; never grounds to rerun.
**Team-games audited:** 0.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| QB1 share of team pass attempts | — | 0.978 | ±0.050 | INSUFFICIENT SAMPLE |
| top receiver share of team targets (team-game) | — | 0.294 | — | INSUFFICIENT SAMPLE |
| top rusher share of non-QB carries (team-game) | — | 0.707 | — | INSUFFICIENT SAMPLE |
| FB share of carries | — | 0.021 | ±0.050 | INSUFFICIENT SAMPLE |
| QB share of carries | — | 0.090 | ±0.050 | INSUFFICIENT SAMPLE |
| RB share of carries | — | 0.867 | ±0.050 | INSUFFICIENT SAMPLE |
| TE share of carries | — | 0.000 | ±0.050 | INSUFFICIENT SAMPLE |
| WR share of carries | — | 0.019 | ±0.050 | INSUFFICIENT SAMPLE |
| FB share of targets | — | 0.026 | ±0.050 | INSUFFICIENT SAMPLE |
| RB share of targets | — | 0.155 | ±0.050 | INSUFFICIENT SAMPLE |
| TE share of targets | — | 0.215 | ±0.050 | INSUFFICIENT SAMPLE |
| WR share of targets | — | 0.602 | ±0.050 | INSUFFICIENT SAMPLE |
| DB share of tackle credits | — | 0.401 | ±0.050 | INSUFFICIENT SAMPLE |
| DL share of tackle credits | — | 0.226 | ±0.050 | INSUFFICIENT SAMPLE |
| LB share of tackle credits | — | 0.353 | ±0.050 | INSUFFICIENT SAMPLE |
| Assisted share of tackle credits | — | 0.339 | ±0.050 | INSUFFICIENT SAMPLE |
| plays per team game | — | 64.2 | ±6.0 | INSUFFICIENT SAMPLE |
| yards per team game | — | 347.2 | ±40.0 | INSUFFICIENT SAMPLE |
| points per team game | — | 22.8 | ±5.0 | INSUFFICIENT SAMPLE |
| first downs per team game | — | 19.8 | ±3.0 | INSUFFICIENT SAMPLE |
| third down attempts per team game | — | 13.3 | ±2.5 | INSUFFICIENT SAMPLE |
| third down rate | — | 0.383 | ±0.060 | INSUFFICIENT SAMPLE |

Drive-model rows and ledger coherence: not measurable for this cohort (legacy receipts carry no drives summary or kicking-attempt counters).

## Kernel 2013.6 cohort (Week 4 onward, detection only)

**Status:** known field-position, label and late-game defects (see the [documented 2013.6 limitations and 2013.7 adoption](../../../../../runtime/README.md)); detection only; never grounds to rerun.
**Team-games audited:** 0.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| QB1 share of team pass attempts | — | 0.978 | ±0.050 | INSUFFICIENT SAMPLE |
| top receiver share of team targets (team-game) | — | 0.294 | — | INSUFFICIENT SAMPLE |
| top rusher share of non-QB carries (team-game) | — | 0.707 | — | INSUFFICIENT SAMPLE |
| FB share of carries | — | 0.021 | ±0.050 | INSUFFICIENT SAMPLE |
| QB share of carries | — | 0.090 | ±0.050 | INSUFFICIENT SAMPLE |
| RB share of carries | — | 0.867 | ±0.050 | INSUFFICIENT SAMPLE |
| TE share of carries | — | 0.000 | ±0.050 | INSUFFICIENT SAMPLE |
| WR share of carries | — | 0.019 | ±0.050 | INSUFFICIENT SAMPLE |
| FB share of targets | — | 0.026 | ±0.050 | INSUFFICIENT SAMPLE |
| RB share of targets | — | 0.155 | ±0.050 | INSUFFICIENT SAMPLE |
| TE share of targets | — | 0.215 | ±0.050 | INSUFFICIENT SAMPLE |
| WR share of targets | — | 0.602 | ±0.050 | INSUFFICIENT SAMPLE |
| DB share of tackle credits | — | 0.401 | ±0.050 | INSUFFICIENT SAMPLE |
| DL share of tackle credits | — | 0.226 | ±0.050 | INSUFFICIENT SAMPLE |
| LB share of tackle credits | — | 0.353 | ±0.050 | INSUFFICIENT SAMPLE |
| Assisted share of tackle credits | — | 0.339 | ±0.050 | INSUFFICIENT SAMPLE |
| plays per team game | — | 64.2 | ±6.0 | INSUFFICIENT SAMPLE |
| yards per team game | — | 347.2 | ±40.0 | INSUFFICIENT SAMPLE |
| points per team game | — | 22.8 | ±5.0 | INSUFFICIENT SAMPLE |
| first downs per team game | — | 19.8 | ±3.0 | INSUFFICIENT SAMPLE |
| third down attempts per team game | — | 13.3 | ±2.5 | INSUFFICIENT SAMPLE |
| third down rate | — | 0.383 | ±0.060 | INSUFFICIENT SAMPLE |

Points: non-offensive touchdowns, their tries and two-point tries are not modelled by design (about 1.7-2.0 points per team game below the 2012 centre); the ±5.0 tolerance is deliberately not tightened. Yards per team game are net of sack yards, as the 2012 centre is (see the correction in the [December 1, 2013 Cleveland game report](../../../../2013/regular_season/week_13_jacksonville_at_cleveland/output.md); earlier audits compared gross passing yards and read about 14 yards high).

### Drive model rows

Centres from the 2012 drive model (nflverse drive definition) and period totals; tolerance is three standard errors at the observed sample.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| FG accuracy | — | 0.839 | — | INSUFFICIENT SAMPLE |
| FG accuracy <30 yd | — | 0.967 | — | INSUFFICIENT SAMPLE |
| FG accuracy 30-39 yd | — | 0.891 | — | INSUFFICIENT SAMPLE |
| FG accuracy 40-49 yd | — | 0.802 | — | INSUFFICIENT SAMPLE |
| FG accuracy 50+ yd | — | 0.609 | — | INSUFFICIENT SAMPLE |
| XP accuracy (informational; partially verified) | — | 0.994 | — | INSUFFICIENT SAMPLE |
| FGA per team game | — | 1.984 | — | INSUFFICIENT SAMPLE |
| FGM per team game | — | 1.664 | — | INSUFFICIENT SAMPLE |
| drives per team game (nflverse definition; PFR 10.47) | — | 11.7 | — | INSUFFICIENT SAMPLE |
| punts per team game (drive-ending) | — | 4.8 | — | INSUFFICIENT SAMPLE |
| drive share: touchdown | — | 0.195 | — | INSUFFICIENT SAMPLE |
| drive share: field goal attempt | — | 0.170 | — | INSUFFICIENT SAMPLE |
| drive share: punt | — | 0.412 | — | INSUFFICIENT SAMPLE |
| drive share: turnover (INT + fumble lost) | — | 0.125 | — | INSUFFICIENT SAMPLE |
| drive share: downs | — | 0.033 | — | INSUFFICIENT SAMPLE |
| drive share: safety | — | 0.002 | — | INSUFFICIENT SAMPLE |
| drive share: clock | — | 0.063 | — | INSUFFICIENT SAMPLE |
| clock-expired drives per team game | — | 0.734 | — | INSUFFICIENT SAMPLE |
| offensive-drive turnovers per team game | — | 1.461 | — | INSUFFICIENT SAMPLE |
| interception share of turnovers | — | 0.626 | — | INSUFFICIENT SAMPLE |
| kickoffs per team game (informational; centre includes kicks not modelled: after non-offensive TDs, onside, re-kicks, after half-final scores) | — | 5.2 | — | INSUFFICIENT SAMPLE |
| kick returns per team game | — | 2.6 | — | INSUFFICIENT SAMPLE |

Known detections (`runtime/bands.py` `KNOWN_DETECTIONS`): graded rows with a documented design cause, accepted rather than tuned. Each stays graded; OUTSIDE within 2x its tolerance is the documented detection, and beyond that it is investigated. No centre, tolerance, coefficient or pool was changed.

- punts per team game (drive-ending): the half-final redirect skews surviving interior drives short and punt-heavy (runtime/README.md, kernel 2013.6 limitations).

### Ledger coherence

Zero-tolerance counts from `runtime.play_detail.check_ledger` over every receipt's drives summary plus the full snap ledgers. Games checked: 0. The kernel 2013.7 spot and label classes are not measurable for this cohort (its receipts carry no start spots).

| Class | Count | Status |
|---|---:|---|
| snaps after terminal | — | not measurable |
| drives missing terminal | — | not measurable |
| duplicate terminal | — | not measurable |
| drives spanning half | — | not measurable |
| wrong second half receiver | — | not measurable |
| missing half kickoff | — | not measurable |
| kickoff after expired clock | — | not measurable |
| xp after ot walkoff | — | not measurable |
| td snap sack or nonpositive | — | not measurable |
| drive net outside 2012 range | — | not measurable |
| snap sum ne drive net | — | not measurable |
| prefix out of bounds | — | not measurable |
| clock regression | — | not measurable |
| score identity violations | — | not measurable |
| ot end inconsistent | — | not measurable |
| start spot out of field | — | not measurable |
| td net ne start | — | not measurable |
| safety not at goal line | — | not measurable |
| safety start infeasible | — | not measurable |
| end spot identity | — | not measurable |
| spot chain break | — | not measurable |
| kick spot mismatch | — | not measurable |
| fg distance offset | — | not measurable |
| category impossible at start | — | not measurable |
| late terminal state mismatch | — | not measurable |
| fourth down state missing | — | not measurable |
| chain counter mismatch | — | not measurable |
| label type mismatch | — | not measurable |
| label carrier mismatch | — | not measurable |
| label target mismatch | — | not measurable |
| scramble with designed label | — | not measurable |
| kneel spike mislabelled | — | not measurable |
| timeout state invalid | — | not measurable |
| fourth down beyond goal | — | not measurable |
| seconds per snap outside | — | not measurable |
| snap after expiry | — | not measurable |
| expiry leg exceeds allowance | — | not measurable |
| down distance chain break | — | not measurable |
| fourth down distance mismatch | — | not measurable |
| first downs ne ledger | — | not measurable |
| goal to go mismatch | — | not measurable |
| layout resample incoherent | — | not measurable |

## Kernel 2013.7 cohort (after Week 8; no game closed yet)

**Team-games audited:** 0. Carry shares exclude kneels, as in the 2012 baseline.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| QB1 share of team pass attempts | — | 0.978 | ±0.050 | INSUFFICIENT SAMPLE |
| top receiver share of team targets (team-game) | — | 0.294 | — | INSUFFICIENT SAMPLE |
| top rusher share of non-QB carries (team-game) | — | 0.707 | — | INSUFFICIENT SAMPLE |
| FB share of carries | — | 0.021 | ±0.050 | INSUFFICIENT SAMPLE |
| QB share of carries | — | 0.090 | ±0.050 | INSUFFICIENT SAMPLE |
| RB share of carries | — | 0.867 | ±0.050 | INSUFFICIENT SAMPLE |
| TE share of carries | — | 0.000 | ±0.050 | INSUFFICIENT SAMPLE |
| WR share of carries | — | 0.019 | ±0.050 | INSUFFICIENT SAMPLE |
| FB share of targets | — | 0.026 | ±0.050 | INSUFFICIENT SAMPLE |
| RB share of targets | — | 0.155 | ±0.050 | INSUFFICIENT SAMPLE |
| TE share of targets | — | 0.215 | ±0.050 | INSUFFICIENT SAMPLE |
| WR share of targets | — | 0.602 | ±0.050 | INSUFFICIENT SAMPLE |
| DB share of tackle credits | — | 0.401 | ±0.050 | INSUFFICIENT SAMPLE |
| DL share of tackle credits | — | 0.226 | ±0.050 | INSUFFICIENT SAMPLE |
| LB share of tackle credits | — | 0.353 | ±0.050 | INSUFFICIENT SAMPLE |
| Assisted share of tackle credits | — | 0.339 | ±0.050 | INSUFFICIENT SAMPLE |
| plays per team game | — | 64.2 | ±6.0 | INSUFFICIENT SAMPLE |
| yards per team game | — | 347.2 | ±40.0 | INSUFFICIENT SAMPLE |
| points per team game | — | 22.8 | ±5.0 | INSUFFICIENT SAMPLE |
| first downs per team game | — | 19.8 | ±3.0 | INSUFFICIENT SAMPLE |
| third down attempts per team game | — | 13.3 | ±2.5 | INSUFFICIENT SAMPLE |
| third down rate | — | 0.383 | ±0.060 | INSUFFICIENT SAMPLE |

Points: non-offensive touchdowns, their tries and two-point tries are not modelled by design (about 1.7-2.0 points per team game below the 2012 centre); the ±5.0 tolerance is deliberately not tightened. Yards per team game are net of sack yards, as the 2012 centre is (see the correction in the [December 1, 2013 Cleveland game report](../../../../2013/regular_season/week_13_jacksonville_at_cleveland/output.md); earlier audits compared gross passing yards and read about 14 yards high).

### Drive model rows

Centres from the 2012 drive model (nflverse drive definition) and period totals; tolerance is three standard errors at the observed sample.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| FG accuracy | — | 0.839 | — | INSUFFICIENT SAMPLE |
| FG accuracy <30 yd | — | 0.967 | — | INSUFFICIENT SAMPLE |
| FG accuracy 30-39 yd | — | 0.891 | — | INSUFFICIENT SAMPLE |
| FG accuracy 40-49 yd | — | 0.802 | — | INSUFFICIENT SAMPLE |
| FG accuracy 50+ yd | — | 0.609 | — | INSUFFICIENT SAMPLE |
| XP accuracy (informational; partially verified) | — | 0.994 | — | INSUFFICIENT SAMPLE |
| FGA per team game | — | 1.984 | — | INSUFFICIENT SAMPLE |
| FGM per team game | — | 1.664 | — | INSUFFICIENT SAMPLE |
| drives per team game (nflverse definition; PFR 10.47) | — | 11.7 | — | INSUFFICIENT SAMPLE |
| punts per team game (drive-ending) | — | 4.8 | — | INSUFFICIENT SAMPLE |
| drive share: touchdown | — | 0.195 | — | INSUFFICIENT SAMPLE |
| drive share: field goal attempt | — | 0.170 | — | INSUFFICIENT SAMPLE |
| drive share: punt | — | 0.412 | — | INSUFFICIENT SAMPLE |
| drive share: turnover (INT + fumble lost) | — | 0.125 | — | INSUFFICIENT SAMPLE |
| drive share: downs | — | 0.033 | — | INSUFFICIENT SAMPLE |
| drive share: safety | — | 0.002 | — | INSUFFICIENT SAMPLE |
| drive share: clock | — | 0.063 | — | INSUFFICIENT SAMPLE |
| clock-expired drives per team game | — | 0.734 | — | INSUFFICIENT SAMPLE |
| offensive-drive turnovers per team game | — | 1.461 | — | INSUFFICIENT SAMPLE |
| interception share of turnovers | — | 0.626 | — | INSUFFICIENT SAMPLE |
| kickoffs per team game (informational; centre includes kicks not modelled: after non-offensive TDs, onside, re-kicks, after half-final scores) | — | 5.2 | — | INSUFFICIENT SAMPLE |
| kick returns per team game | — | 2.6 | — | INSUFFICIENT SAMPLE |

Known detections (`runtime/bands.py` `KNOWN_DETECTIONS`): graded rows with a documented design cause, accepted rather than tuned. Each stays graded; OUTSIDE within 2x its tolerance is the documented detection, and beyond that it is investigated. No centre, tolerance, coefficient or pool was changed.

- punts per team game (drive-ending): the half-final redirect skews surviving interior drives short and punt-heavy (runtime/README.md, kernel 2013.6 limitations).
- FGM per team game: adopted as documented by the user's decision of September 27, 2026: the first-half half-final redirect starts first-half final possessions early, field-goal-heavy and clock-light (library/2012_field_position_model_calibration.md, acceptance).
- drive share: clock: adopted as documented by the user's decision of September 27, 2026: the first-half half-final redirect starts first-half final possessions early, field-goal-heavy and clock-light (library/2012_field_position_model_calibration.md, acceptance).
- clock-expired drives per team game: adopted as documented by the user's decision of September 27, 2026: the first-half half-final redirect starts first-half final possessions early, field-goal-heavy and clock-light (library/2012_field_position_model_calibration.md, acceptance).

### Field-position rows

Centres from the 2012 field-position model's band_centres. Rates use 3*sqrt(p(1-p)/n) and means 3*sd/sqrt(n) with the 2012 sd; a row reads INSUFFICIENT SAMPLE below 30 events. INFORMATIONAL rows are shapes, not grades.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| kickoff touchback share | — | 0.462 | — | INSUFFICIENT SAMPLE |
| mean start after a non-touchback kickoff (yardline_100) | — | 77.0 | — | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS opp 39-30 | — | 28.0 | — | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS opp 49-40 | — | 32.9 | — | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS own 1-10 | — | 43.7 | — | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS own 11-20 | — | 43.3 | — | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS own 21-30 | — | 43.7 | — | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS own 31-40 | — | 42.3 | — | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS own 41-50 | — | 38.8 | — | INSUFFICIENT SAMPLE |
| mean kickoff return yards (non-touchback kickoffs) | — | 23.0 | — | INSUFFICIENT SAMPLE |
| mean punt return yards (returned punts) | — | 9.2 | — | INSUFFICIENT SAMPLE |
| punt share of possessions ending in Q4's last 5:00 or OT, offense trailing 1-8 | — | 0.119 | — | INSUFFICIENT SAMPLE |
| punt share of possessions ending in Q4's last 2:00 or OT, offense trailing 1-8 | — | 0.008 | — | INSUFFICIENT SAMPLE |
| third-down attempts per punt drive | — | 1.185 | — | INSUFFICIENT SAMPLE |
| sacks per dropback | — | 0.062 | — | INSUFFICIENT SAMPLE |
| DB share of sack credits | — | 0.063 | — | INSUFFICIENT SAMPLE |
| DL share of sack credits | — | 0.599 | — | INSUFFICIENT SAMPLE |
| LB share of sack credits | — | 0.337 | — | INSUFFICIENT SAMPLE |
| mean drive start, all drives (2012 all-drive centre) | — | 72.3 | — | INSUFFICIENT SAMPLE |
| mean drive start (2012 centre over modelled transitions) | — | 72.8 | — | INSUFFICIENT SAMPLE |
| start-bin share 90-99 | — | 0.096 | — | INSUFFICIENT SAMPLE |
| start-bin share 81-89 | — | 0.160 | — | INSUFFICIENT SAMPLE |
| start-bin share 80-80 | — | 0.251 | — | INSUFFICIENT SAMPLE |
| start-bin share 70-79 | — | 0.191 | — | INSUFFICIENT SAMPLE |
| start-bin share 60-69 | — | 0.123 | — | INSUFFICIENT SAMPLE |
| start-bin share 50-59 | — | 0.071 | — | INSUFFICIENT SAMPLE |
| start-bin share 40-49 | — | 0.043 | — | INSUFFICIENT SAMPLE |
| start-bin share 30-39 | — | 0.023 | — | INSUFFICIENT SAMPLE |
| start-bin share 20-29 | — | 0.021 | — | INSUFFICIENT SAMPLE |
| start-bin share 1-19 | — | 0.022 | — | INSUFFICIENT SAMPLE |
| touchdown share, start opp 49-1 | — | 0.349 | — | INSUFFICIENT SAMPLE |
| punt share, start opp 49-1 | — | 0.108 | — | INSUFFICIENT SAMPLE |
| touchdown share, start own 1-20 | — | 0.158 | — | INSUFFICIENT SAMPLE |
| punt share, start own 1-20 | — | 0.486 | — | INSUFFICIENT SAMPLE |
| touchdown share, start own 21-50 | — | 0.199 | — | INSUFFICIENT SAMPLE |
| punt share, start own 21-50 | — | 0.402 | — | INSUFFICIENT SAMPLE |
| points per drive, start 1-19 | — | 4.5 | — | INSUFFICIENT SAMPLE |
| points per drive, start 20-29 | — | 4.1 | — | INSUFFICIENT SAMPLE |
| points per drive, start 30-39 | — | 3.1 | — | INSUFFICIENT SAMPLE |
| points per drive, start 40-49 | — | 2.6 | — | INSUFFICIENT SAMPLE |
| points per drive, start 50-59 | — | 2.2 | — | INSUFFICIENT SAMPLE |
| points per drive, start 60-69 | — | 1.829 | — | INSUFFICIENT SAMPLE |
| points per drive, start 70-79 | — | 1.707 | — | INSUFFICIENT SAMPLE |
| points per drive, start 80-89 | — | 1.473 | — | INSUFFICIENT SAMPLE |
| points per drive, start 90-99 | — | 1.140 | — | INSUFFICIENT SAMPLE |
| QB scramble share of QB carries (label stream; nflscrapR 643/1,228) | — | 0.557 | — | INSUFFICIENT SAMPLE |
| fourth-down attempts per team game (drive chains) | — | 0.881 | — | INSUFFICIENT SAMPLE |
| fourth-down conversions per team game (drive chains) | — | 0.439 | — | INSUFFICIENT SAMPLE |
| kneels per team game | — | 0.717 | — | INSUFFICIENT SAMPLE |
| overtime punt share | — | 0.311 | — | INSUFFICIENT SAMPLE |

### Ledger coherence

Zero-tolerance counts from `runtime.play_detail.check_ledger` (15 original and 17 kernel 2013.7 spot and label classes). Games checked: 0. The kick-row and label classes need the full snap ledger.

| Class | Count | Status |
|---|---:|---|
| snaps after terminal | — | not measurable |
| drives missing terminal | — | not measurable |
| duplicate terminal | — | not measurable |
| drives spanning half | — | not measurable |
| wrong second half receiver | — | not measurable |
| missing half kickoff | — | not measurable |
| kickoff after expired clock | — | not measurable |
| xp after ot walkoff | — | not measurable |
| td snap sack or nonpositive | — | not measurable |
| drive net outside 2012 range | — | not measurable |
| snap sum ne drive net | — | not measurable |
| prefix out of bounds | — | not measurable |
| clock regression | — | not measurable |
| score identity violations | — | not measurable |
| ot end inconsistent | — | not measurable |
| start spot out of field | — | not measurable |
| td net ne start | — | not measurable |
| safety not at goal line | — | not measurable |
| safety start infeasible | — | not measurable |
| end spot identity | — | not measurable |
| spot chain break | — | not measurable |
| kick spot mismatch | — | not measurable |
| fg distance offset | — | not measurable |
| category impossible at start | — | not measurable |
| late terminal state mismatch | — | not measurable |
| fourth down state missing | — | not measurable |
| chain counter mismatch | — | not measurable |
| label type mismatch | — | not measurable |
| label carrier mismatch | — | not measurable |
| label target mismatch | — | not measurable |
| scramble with designed label | — | not measurable |
| kneel spike mislabelled | — | not measurable |
| timeout state invalid | — | not measurable |
| fourth down beyond goal | — | not measurable |
| seconds per snap outside | — | not measurable |
| snap after expiry | — | not measurable |
| expiry leg exceeds allowance | — | not measurable |
| down distance chain break | — | not measurable |
| fourth down distance mismatch | — | not measurable |
| first downs ne ledger | — | not measurable |
| goal to go mismatch | — | not measurable |
| layout resample incoherent | — | not measurable |

## Kernel 2014.4 cohort (Week 1)

**Team-games audited:** 32. Carry shares exclude kneels, as in the 2012 baseline.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| QB1 share of team pass attempts | 1.000 | 0.978 | ±0.050 | WITHIN |
| top receiver share of team targets (team-game) | 0.282 | 0.294 | ±0.037 | WITHIN |
| top rusher share of non-QB carries (team-game) | 0.685 | 0.707 | ±0.084 | WITHIN |
| FB share of carries | 0.024 | 0.021 | ±0.050 | WITHIN |
| QB share of carries | 0.081 | 0.090 | ±0.050 | WITHIN |
| RB share of carries | 0.875 | 0.867 | ±0.050 | WITHIN |
| TE share of carries | 0.000 | 0.000 | ±0.050 | WITHIN |
| WR share of carries | 0.019 | 0.019 | ±0.050 | WITHIN |
| FB share of targets | 0.018 | 0.026 | ±0.050 | WITHIN |
| RB share of targets | 0.171 | 0.155 | ±0.050 | WITHIN |
| TE share of targets | 0.213 | 0.215 | ±0.050 | WITHIN |
| WR share of targets | 0.599 | 0.602 | ±0.050 | WITHIN |
| DB share of tackle credits | 0.383 | 0.401 | ±0.050 | WITHIN |
| DL share of tackle credits | 0.238 | 0.226 | ±0.050 | WITHIN |
| LB share of tackle credits | 0.379 | 0.353 | ±0.050 | WITHIN |
| Assisted share of tackle credits | 0.317 | 0.339 | ±0.050 | WITHIN |
| plays per team game | 66.2 | 64.2 | ±6.0 | WITHIN |
| yards per team game | 394.6 | 347.2 | ±40.0 | OUTSIDE |
| points per team game | 24.7 | 22.8 | ±5.0 | WITHIN |
| first downs per team game | 21.9 | 19.8 | ±3.0 | WITHIN |
| third down attempts per team game | 13.4 | 13.3 | ±2.5 | WITHIN |
| third down rate | 0.424 | 0.383 | ±0.060 | WITHIN |

Points: non-offensive touchdowns, their tries and two-point tries are not modelled by design (about 1.7-2.0 points per team game below the 2012 centre); the ±5.0 tolerance is deliberately not tightened. Yards per team game are net of sack yards, as the 2012 centre is (see the correction in the [December 1, 2013 Cleveland game report](../../../../2013/regular_season/week_13_jacksonville_at_cleveland/output.md); earlier audits compared gross passing yards and read about 14 yards high).

### Drive model rows

Centres from the 2012 drive model (nflverse drive definition) and period totals; tolerance is three standard errors at the observed sample.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| FG accuracy | 0.803 | 0.839 | ±0.131 | WITHIN |
| FG accuracy <30 yd | 0.917 | 0.967 | ±0.156 | INSUFFICIENT SAMPLE |
| FG accuracy 30-39 yd | 0.870 | 0.891 | ±0.195 | INSUFFICIENT SAMPLE |
| FG accuracy 40-49 yd | 0.857 | 0.802 | ±0.261 | INSUFFICIENT SAMPLE |
| FG accuracy 50+ yd | 0.533 | 0.609 | ±0.378 | INSUFFICIENT SAMPLE |
| XP accuracy (informational; partially verified) | 0.977 | 0.994 | ±0.026 | WITHIN |
| FGA per team game | 2.2 | 1.984 | ±0.747 | WITHIN (known detection) |
| FGM per team game | 1.781 | 1.664 | ±0.684 | WITHIN (known detection) |
| drives per team game (nflverse definition; PFR 10.47) | 12.2 | 11.7 | ±1.813 | WITHIN |
| punts per team game (drive-ending) | 4.6 | 4.8 | ±1.164 | WITHIN (known detection) |
| drive share: touchdown | 0.228 | 0.195 | ±0.060 | WITHIN |
| drive share: field goal attempt | 0.182 | 0.170 | ±0.057 | WITHIN |
| drive share: punt | 0.379 | 0.412 | ±0.075 | WITHIN |
| drive share: turnover (INT + fumble lost) | 0.133 | 0.125 | ±0.050 | WITHIN |
| drive share: downs | 0.018 | 0.033 | ±0.027 | WITHIN |
| drive share: safety | 0.000 | 0.002 | ±0.007 | WITHIN |
| drive share: clock | 0.059 | 0.063 | ±0.037 | WITHIN (known detection) |
| clock-expired drives per team game | 0.719 | 0.734 | ±0.454 | WITHIN (known detection) |
| offensive-drive turnovers per team game | 1.625 | 1.461 | ±0.641 | WITHIN |
| interception share of turnovers | 0.577 | 0.626 | ±0.201 | WITHIN |
| kickoffs per team game (informational; centre includes kicks not modelled: after non-offensive TDs, onside, re-kicks, after half-final scores) | 5.3 | 5.2 | ±1.210 | INFORMATIONAL |
| kick returns per team game | 2.9 | 2.6 | ±0.860 | WITHIN |

Known detections (`runtime/bands.py` `KNOWN_DETECTIONS`): graded rows with a documented design cause, accepted rather than tuned. Each stays graded; OUTSIDE within 2x its tolerance is the documented detection, and beyond that it is investigated. No centre, tolerance, coefficient or pool was changed.

- punts per team game (drive-ending): the half-final redirect skews surviving interior drives short and punt-heavy (runtime/README.md, kernel 2013.6 limitations).
- FGM per team game: adopted as documented by the user's decision of September 27, 2026: the first-half half-final redirect starts first-half final possessions early, field-goal-heavy and clock-light (library/2012_field_position_model_calibration.md, acceptance).
- drive share: clock: adopted as documented by the user's decision of September 27, 2026: the first-half half-final redirect starts first-half final possessions early, field-goal-heavy and clock-light (library/2012_field_position_model_calibration.md, acceptance).
- clock-expired drives per team game: adopted as documented by the user's decision of September 27, 2026: the first-half half-final redirect starts first-half final possessions early, field-goal-heavy and clock-light (library/2012_field_position_model_calibration.md, acceptance).
- FGA per team game: field-goal attempts rise with FGM from the first-half half-final redirect; kernel 2014.2 also stops masking late field goals, whose expected share by need now tracks 2012 (runtime/README.md, kernel 2014.2 acceptance).
- punt share of possessions ending in Q4's last 5:00 or OT, offense trailing 1-8: about 70 events per 250 games; the 2014.2 expected late mix by need tracks 2012 (trailing 4-8 punts 0.173 against 0.179), a 750-game fresh sample reads 0.087 inside its tolerance, and the rest is the timing mix of possessions that end in the last 5:00 (runtime/README.md, kernel 2014.2 acceptance).

### Field-position rows

Centres from the 2012 field-position model's band_centres. Rates use 3*sqrt(p(1-p)/n) and means 3*sd/sqrt(n) with the 2012 sd; a row reads INSUFFICIENT SAMPLE below 30 events. INFORMATIONAL rows are shapes, not grades.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| kickoff touchback share | 0.456 | 0.462 | ±0.114 | WITHIN |
| mean start after a non-touchback kickoff (yardline_100) | 77.4 | 77.0 | ±3.0 | WITHIN |
| mean realized punt net, LOS opp 39-30 | 30.2 | 28.0 | ±9.8 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS opp 49-40 | 34.6 | 32.9 | ±4.6 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS own 1-10 | 43.7 | 43.7 | ±12.4 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS own 11-20 | 40.7 | 43.3 | ±8.7 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS own 21-30 | 44.7 | 43.7 | ±5.5 | WITHIN |
| mean realized punt net, LOS own 31-40 | 37.3 | 42.3 | ±7.1 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS own 41-50 | 38.2 | 38.8 | ±4.7 | INSUFFICIENT SAMPLE |
| mean kickoff return yards (non-touchback kickoffs) | 21.6 | 23.0 | ±3.2 | WITHIN |
| mean punt return yards (returned punts) | 12.5 | 9.2 | ±3.4 | WITHIN |
| punt share of possessions ending in Q4's last 5:00 or OT, offense trailing 1-8 | 0.059 | 0.119 | ±0.235 | INSUFFICIENT SAMPLE |
| punt share of possessions ending in Q4's last 2:00 or OT, offense trailing 1-8 | 0.000 | 0.008 | ±0.080 | INSUFFICIENT SAMPLE |
| third-down attempts per punt drive | 1.216 | 1.185 | ±0.109 | WITHIN |
| sacks per dropback | 0.066 | 0.062 | ±0.021 | WITHIN |
| DB share of sack credits | 0.025 | 0.063 | ±0.081 | WITHIN |
| DL share of sack credits | 0.617 | 0.599 | ±0.163 | WITHIN |
| LB share of sack credits | 0.358 | 0.337 | ±0.158 | WITHIN |
| mean drive start, all drives (2012 all-drive centre) | 72.1 | 72.3 | — | INFORMATIONAL |
| mean drive start (2012 centre over modelled transitions) | 72.1 | 72.8 | — | INFORMATIONAL |
| start-bin share 90-99 | 0.085 | 0.096 | — | INFORMATIONAL |
| start-bin share 81-89 | 0.154 | 0.160 | — | INFORMATIONAL |
| start-bin share 80-80 | 0.249 | 0.251 | — | INFORMATIONAL |
| start-bin share 70-79 | 0.226 | 0.191 | — | INFORMATIONAL |
| start-bin share 60-69 | 0.108 | 0.123 | — | INFORMATIONAL |
| start-bin share 50-59 | 0.074 | 0.071 | — | INFORMATIONAL |
| start-bin share 40-49 | 0.031 | 0.043 | — | INFORMATIONAL |
| start-bin share 30-39 | 0.018 | 0.023 | — | INFORMATIONAL |
| start-bin share 20-29 | 0.033 | 0.021 | — | INFORMATIONAL |
| start-bin share 1-19 | 0.023 | 0.022 | — | INFORMATIONAL |
| touchdown share, start opp 49-1 | 0.463 | 0.349 | — | INFORMATIONAL |
| punt share, start opp 49-1 | 0.049 | 0.108 | — | INFORMATIONAL |
| touchdown share, start own 1-20 | 0.200 | 0.158 | — | INFORMATIONAL |
| punt share, start own 1-20 | 0.458 | 0.486 | — | INFORMATIONAL |
| touchdown share, start own 21-50 | 0.201 | 0.199 | — | INFORMATIONAL |
| punt share, start own 21-50 | 0.371 | 0.402 | — | INFORMATIONAL |
| points per drive, start 1-19 | 5.0 | 4.5 | — | INFORMATIONAL |
| points per drive, start 20-29 | 4.4 | 4.1 | — | INFORMATIONAL |
| points per drive, start 30-39 | 4.1 | 3.1 | — | INFORMATIONAL |
| points per drive, start 40-49 | 3.6 | 2.6 | — | INFORMATIONAL |
| points per drive, start 50-59 | 1.931 | 2.2 | — | INFORMATIONAL |
| points per drive, start 60-69 | 1.667 | 1.829 | — | INFORMATIONAL |
| points per drive, start 70-79 | 1.989 | 1.707 | — | INFORMATIONAL |
| points per drive, start 80-89 | 1.739 | 1.473 | — | INFORMATIONAL |
| points per drive, start 90-99 | 1.303 | 1.140 | — | INFORMATIONAL |
| QB scramble share of QB carries (label stream; nflscrapR 643/1,228) | 0.375 | 0.557 | — | INFORMATIONAL |
| fourth-down attempts per team game (drive chains) | 0.812 | 0.881 | — | INFORMATIONAL |
| fourth-down conversions per team game (drive chains) | 0.531 | 0.439 | — | INFORMATIONAL |
| kneels per team game | 0.594 | 0.717 | — | INFORMATIONAL |
| overtime punt share | 0.714 | 0.311 | — | INFORMATIONAL |

### Ledger coherence

Zero-tolerance counts from `runtime.play_detail.check_ledger` (15 original and 17 kernel 2013.7 spot and label classes). Games checked: 16. The kick-row and label classes need the full snap ledger.

| Class | Count | Status |
|---|---:|---|
| snaps after terminal | 0 | WITHIN |
| drives missing terminal | 0 | WITHIN |
| duplicate terminal | 0 | WITHIN |
| drives spanning half | 0 | WITHIN |
| wrong second half receiver | 0 | WITHIN |
| missing half kickoff | 0 | WITHIN |
| kickoff after expired clock | 0 | WITHIN |
| xp after ot walkoff | 0 | WITHIN |
| td snap sack or nonpositive | 0 | WITHIN |
| drive net outside 2012 range | 0 | WITHIN |
| snap sum ne drive net | 0 | WITHIN |
| prefix out of bounds | 0 | WITHIN |
| clock regression | 0 | WITHIN |
| score identity violations | 0 | WITHIN |
| ot end inconsistent | 0 | WITHIN |
| start spot out of field | 0 | WITHIN |
| td net ne start | 0 | WITHIN |
| safety not at goal line | 0 | WITHIN |
| safety start infeasible | 0 | WITHIN |
| end spot identity | 0 | WITHIN |
| spot chain break | 0 | WITHIN |
| kick spot mismatch | 0 | WITHIN |
| fg distance offset | 0 | WITHIN |
| category impossible at start | 0 | WITHIN |
| late terminal state mismatch | 0 | WITHIN |
| fourth down state missing | 0 | WITHIN |
| chain counter mismatch | 0 | WITHIN |
| label type mismatch | 0 | WITHIN |
| label carrier mismatch | 0 | WITHIN |
| label target mismatch | 0 | WITHIN |
| scramble with designed label | 0 | WITHIN |
| kneel spike mislabelled | 0 | WITHIN |
| timeout state invalid | 0 | WITHIN |
| fourth down beyond goal | 0 | WITHIN |
| seconds per snap outside | 0 | WITHIN |
| snap after expiry | 0 | WITHIN |
| expiry leg exceeds allowance | 0 | WITHIN |
| down distance chain break | 0 | WITHIN |
| fourth down distance mismatch | 0 | WITHIN |
| first downs ne ledger | 0 | WITHIN |
| goal to go mismatch | 0 | WITHIN |
| layout resample incoherent | 0 | WITHIN |
