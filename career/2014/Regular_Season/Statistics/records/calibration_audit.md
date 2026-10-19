# 2014 statistical band audit

**Version:** `2014-W05-BAND-AUDIT`
**Through:** Week 5.

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

## Kernel 2014.4 cohort (Weeks 1-2)

**Team-games audited:** 64. Carry shares exclude kneels, as in the 2012 baseline.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| QB1 share of team pass attempts | 1.000 | 0.978 | ±0.050 | WITHIN |
| top receiver share of team targets (team-game) | 0.296 | 0.294 | ±0.026 | WITHIN |
| top rusher share of non-QB carries (team-game) | 0.695 | 0.707 | ±0.059 | WITHIN |
| FB share of carries | 0.018 | 0.021 | ±0.050 | WITHIN |
| QB share of carries | 0.088 | 0.090 | ±0.050 | WITHIN |
| RB share of carries | 0.872 | 0.867 | ±0.050 | WITHIN |
| TE share of carries | 0.000 | 0.000 | ±0.050 | WITHIN |
| WR share of carries | 0.022 | 0.019 | ±0.050 | WITHIN |
| FB share of targets | 0.018 | 0.026 | ±0.050 | WITHIN |
| RB share of targets | 0.154 | 0.155 | ±0.050 | WITHIN |
| TE share of targets | 0.215 | 0.215 | ±0.050 | WITHIN |
| WR share of targets | 0.613 | 0.602 | ±0.050 | WITHIN |
| DB share of tackle credits | 0.389 | 0.401 | ±0.050 | WITHIN |
| DL share of tackle credits | 0.239 | 0.226 | ±0.050 | WITHIN |
| LB share of tackle credits | 0.372 | 0.353 | ±0.050 | WITHIN |
| Assisted share of tackle credits | 0.314 | 0.339 | ±0.050 | WITHIN |
| plays per team game | 65.8 | 64.2 | ±6.0 | WITHIN |
| yards per team game | 380.6 | 347.2 | ±40.0 | WITHIN |
| points per team game | 23.3 | 22.8 | ±5.0 | WITHIN |
| first downs per team game | 21.1 | 19.8 | ±3.0 | WITHIN |
| third down attempts per team game | 13.6 | 13.3 | ±2.5 | WITHIN |
| third down rate | 0.428 | 0.383 | ±0.060 | WITHIN |

Points: non-offensive touchdowns, their tries and two-point tries are not modelled by design (about 1.7-2.0 points per team game below the 2012 centre); the ±5.0 tolerance is deliberately not tightened. Yards per team game are net of sack yards, as the 2012 centre is (see the correction in the [December 1, 2013 Cleveland game report](../../../../2013/regular_season/week_13_jacksonville_at_cleveland/output.md); earlier audits compared gross passing yards and read about 14 yards high).

### Drive model rows

Centres from the 2012 drive model (nflverse drive definition) and period totals; tolerance is three standard errors at the observed sample.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| FG accuracy | 0.820 | 0.839 | ±0.096 | WITHIN |
| FG accuracy <30 yd | 0.963 | 0.967 | ±0.104 | INSUFFICIENT SAMPLE |
| FG accuracy 30-39 yd | 0.881 | 0.891 | ±0.144 | WITHIN |
| FG accuracy 40-49 yd | 0.881 | 0.802 | ±0.185 | WITHIN |
| FG accuracy 50+ yd | 0.409 | 0.609 | ±0.312 | INSUFFICIENT SAMPLE |
| XP accuracy (informational; partially verified) | 0.988 | 0.994 | ±0.019 | WITHIN |
| FGA per team game | 2.1 | 1.984 | ±0.528 | WITHIN (known detection) |
| FGM per team game | 1.703 | 1.664 | ±0.484 | WITHIN (known detection) |
| drives per team game (nflverse definition; PFR 10.47) | 12.1 | 11.7 | ±1.282 | WITHIN |
| punts per team game (drive-ending) | 4.7 | 4.8 | ±0.823 | WITHIN (known detection) |
| drive share: touchdown | 0.216 | 0.195 | ±0.043 | WITHIN |
| drive share: field goal attempt | 0.172 | 0.170 | ±0.041 | WITHIN |
| drive share: punt | 0.389 | 0.412 | ±0.053 | WITHIN |
| drive share: turnover (INT + fumble lost) | 0.141 | 0.125 | ±0.036 | WITHIN |
| drive share: downs | 0.021 | 0.033 | ±0.019 | WITHIN |
| drive share: safety | 0.000 | 0.002 | ±0.005 | WITHIN |
| drive share: clock | 0.061 | 0.063 | ±0.026 | WITHIN (known detection) |
| clock-expired drives per team game | 0.734 | 0.734 | ±0.321 | WITHIN (known detection) |
| offensive-drive turnovers per team game | 1.703 | 1.461 | ±0.453 | WITHIN |
| interception share of turnovers | 0.560 | 0.626 | ±0.139 | WITHIN |
| kickoffs per team game (informational; centre includes kicks not modelled: after non-offensive TDs, onside, re-kicks, after half-final scores) | 5.1 | 5.2 | ±0.856 | INFORMATIONAL |
| kick returns per team game | 2.7 | 2.6 | ±0.608 | WITHIN |

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
| kickoff touchback share | 0.479 | 0.462 | ±0.083 | WITHIN |
| mean start after a non-touchback kickoff (yardline_100) | 77.5 | 77.0 | ±2.2 | WITHIN |
| mean realized punt net, LOS opp 39-30 | 28.1 | 28.0 | ±7.4 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS opp 49-40 | 32.4 | 32.9 | ±3.1 | WITHIN |
| mean realized punt net, LOS own 1-10 | 43.2 | 43.7 | ±8.7 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS own 11-20 | 42.4 | 43.3 | ±6.1 | WITHIN |
| mean realized punt net, LOS own 21-30 | 45.4 | 43.7 | ±4.1 | WITHIN |
| mean realized punt net, LOS own 31-40 | 41.7 | 42.3 | ±4.6 | WITHIN |
| mean realized punt net, LOS own 41-50 | 39.0 | 38.8 | ±3.4 | WITHIN |
| mean kickoff return yards (non-touchback kickoffs) | 22.7 | 23.0 | ±2.4 | WITHIN |
| mean punt return yards (returned punts) | 10.0 | 9.2 | ±2.5 | WITHIN |
| punt share of possessions ending in Q4's last 5:00 or OT, offense trailing 1-8 | 0.037 | 0.119 | ±0.187 | INSUFFICIENT SAMPLE |
| punt share of possessions ending in Q4's last 2:00 or OT, offense trailing 1-8 | 0.000 | 0.008 | ±0.060 | INSUFFICIENT SAMPLE |
| third-down attempts per punt drive | 1.230 | 1.185 | ±0.076 | WITHIN |
| sacks per dropback | 0.070 | 0.062 | ±0.015 | WITHIN |
| DB share of sack credits | 0.029 | 0.063 | ±0.056 | WITHIN |
| DL share of sack credits | 0.647 | 0.599 | ±0.113 | WITHIN |
| LB share of sack credits | 0.324 | 0.337 | ±0.109 | WITHIN |
| mean drive start, all drives (2012 all-drive centre) | 72.1 | 72.3 | — | INFORMATIONAL |
| mean drive start (2012 centre over modelled transitions) | 72.1 | 72.8 | — | INFORMATIONAL |
| start-bin share 90-99 | 0.095 | 0.096 | — | INFORMATIONAL |
| start-bin share 81-89 | 0.159 | 0.160 | — | INFORMATIONAL |
| start-bin share 80-80 | 0.255 | 0.251 | — | INFORMATIONAL |
| start-bin share 70-79 | 0.197 | 0.191 | — | INFORMATIONAL |
| start-bin share 60-69 | 0.123 | 0.123 | — | INFORMATIONAL |
| start-bin share 50-59 | 0.058 | 0.071 | — | INFORMATIONAL |
| start-bin share 40-49 | 0.031 | 0.043 | — | INFORMATIONAL |
| start-bin share 30-39 | 0.023 | 0.023 | — | INFORMATIONAL |
| start-bin share 20-29 | 0.032 | 0.021 | — | INFORMATIONAL |
| start-bin share 1-19 | 0.026 | 0.022 | — | INFORMATIONAL |
| touchdown share, start opp 49-1 | 0.425 | 0.349 | — | INFORMATIONAL |
| punt share, start opp 49-1 | 0.080 | 0.108 | — | INFORMATIONAL |
| touchdown share, start own 1-20 | 0.186 | 0.158 | — | INFORMATIONAL |
| punt share, start own 1-20 | 0.466 | 0.486 | — | INFORMATIONAL |
| touchdown share, start own 21-50 | 0.195 | 0.199 | — | INFORMATIONAL |
| punt share, start own 21-50 | 0.377 | 0.402 | — | INFORMATIONAL |
| points per drive, start 1-19 | 4.2 | 4.5 | — | INFORMATIONAL |
| points per drive, start 20-29 | 4.6 | 4.1 | — | INFORMATIONAL |
| points per drive, start 30-39 | 3.5 | 3.1 | — | INFORMATIONAL |
| points per drive, start 40-49 | 2.8 | 2.6 | — | INFORMATIONAL |
| points per drive, start 50-59 | 1.844 | 2.2 | — | INFORMATIONAL |
| points per drive, start 60-69 | 1.884 | 1.829 | — | INFORMATIONAL |
| points per drive, start 70-79 | 1.822 | 1.707 | — | INFORMATIONAL |
| points per drive, start 80-89 | 1.656 | 1.473 | — | INFORMATIONAL |
| points per drive, start 90-99 | 1.288 | 1.140 | — | INFORMATIONAL |
| QB scramble share of QB carries (label stream; nflscrapR 643/1,228) | 0.500 | 0.557 | — | INFORMATIONAL |
| fourth-down attempts per team game (drive chains) | 0.766 | 0.881 | — | INFORMATIONAL |
| fourth-down conversions per team game (drive chains) | 0.453 | 0.439 | — | INFORMATIONAL |
| kneels per team game | 0.625 | 0.717 | — | INFORMATIONAL |
| overtime punt share | 0.714 | 0.311 | — | INFORMATIONAL |

### Ledger coherence

Zero-tolerance counts from `runtime.play_detail.check_ledger` (15 original and 17 kernel 2013.7 spot and label classes). Games checked: 32. The kick-row and label classes need the full snap ledger.

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

## Kernel 2014.5 cohort (Weeks 3-4)

**Team-games audited:** 58. Carry shares exclude kneels, as in the 2012 baseline.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| QB1 share of team pass attempts | 0.992 | 0.978 | ±0.050 | WITHIN |
| top receiver share of team targets (team-game) | 0.308 | 0.294 | ±0.027 | WITHIN |
| top rusher share of non-QB carries (team-game) | 0.707 | 0.707 | ±0.062 | WITHIN |
| FB share of carries | 0.017 | 0.021 | ±0.050 | WITHIN |
| QB share of carries | 0.098 | 0.090 | ±0.050 | WITHIN |
| RB share of carries | 0.862 | 0.867 | ±0.050 | WITHIN |
| TE share of carries | 0.000 | 0.000 | ±0.050 | WITHIN |
| WR share of carries | 0.023 | 0.019 | ±0.050 | WITHIN |
| FB share of targets | 0.020 | 0.026 | ±0.050 | WITHIN |
| RB share of targets | 0.144 | 0.155 | ±0.050 | WITHIN |
| TE share of targets | 0.217 | 0.215 | ±0.050 | WITHIN |
| WR share of targets | 0.619 | 0.602 | ±0.050 | WITHIN |
| DB share of tackle credits | 0.371 | 0.401 | ±0.050 | WITHIN |
| DL share of tackle credits | 0.264 | 0.226 | ±0.050 | WITHIN |
| LB share of tackle credits | 0.366 | 0.353 | ±0.050 | WITHIN |
| Assisted share of tackle credits | 0.329 | 0.339 | ±0.050 | WITHIN |
| plays per team game | 65.1 | 64.2 | ±6.0 | WITHIN |
| yards per team game | 374.7 | 347.2 | ±40.0 | WITHIN |
| points per team game | 23.8 | 22.8 | ±5.0 | WITHIN |
| first downs per team game | 21.1 | 19.8 | ±3.0 | WITHIN |
| third down attempts per team game | 13.6 | 13.3 | ±2.5 | WITHIN |
| third down rate | 0.420 | 0.383 | ±0.060 | WITHIN |

Points: non-offensive touchdowns, their tries and two-point tries are not modelled by design (about 1.7-2.0 points per team game below the 2012 centre); the ±5.0 tolerance is deliberately not tightened. Yards per team game are net of sack yards, as the 2012 centre is (see the correction in the [December 1, 2013 Cleveland game report](../../../../2013/regular_season/week_13_jacksonville_at_cleveland/output.md); earlier audits compared gross passing yards and read about 14 yards high).

### Drive model rows

Centres from the 2012 drive model (nflverse drive definition) and period totals; tolerance is three standard errors at the observed sample.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| FG accuracy | 0.853 | 0.839 | ±0.097 | WITHIN |
| FG accuracy <30 yd | 1.000 | 0.967 | ±0.102 | INSUFFICIENT SAMPLE |
| FG accuracy 30-39 yd | 1.000 | 0.891 | ±0.138 | WITHIN |
| FG accuracy 40-49 yd | 0.667 | 0.802 | ±0.191 | WITHIN |
| FG accuracy 50+ yd | 0.625 | 0.609 | ±0.366 | INSUFFICIENT SAMPLE |
| XP accuracy (informational; partially verified) | 0.987 | 0.994 | ±0.020 | WITHIN |
| FGA per team game | 2.2 | 1.984 | ±0.555 | WITHIN (known detection) |
| FGM per team game | 1.897 | 1.664 | ±0.508 | WITHIN (known detection) |
| drives per team game (nflverse definition; PFR 10.47) | 11.7 | 11.7 | ±1.347 | WITHIN |
| punts per team game (drive-ending) | 4.6 | 4.8 | ±0.865 | WITHIN (known detection) |
| drive share: touchdown | 0.220 | 0.195 | ±0.046 | WITHIN |
| drive share: field goal attempt | 0.189 | 0.170 | ±0.043 | WITHIN |
| drive share: punt | 0.388 | 0.412 | ±0.057 | WITHIN |
| drive share: turnover (INT + fumble lost) | 0.110 | 0.125 | ±0.038 | WITHIN |
| drive share: downs | 0.025 | 0.033 | ±0.021 | WITHIN |
| drive share: safety | 0.000 | 0.002 | ±0.005 | WITHIN |
| drive share: clock | 0.068 | 0.063 | ±0.028 | WITHIN (known detection) |
| clock-expired drives per team game | 0.793 | 0.734 | ±0.338 | WITHIN (known detection) |
| offensive-drive turnovers per team game | 1.293 | 1.461 | ±0.476 | WITHIN |
| interception share of turnovers | 0.573 | 0.626 | ±0.168 | WITHIN |
| kickoffs per team game (informational; centre includes kicks not modelled: after non-offensive TDs, onside, re-kicks, after half-final scores) | 5.3 | 5.2 | ±0.899 | INFORMATIONAL |
| kick returns per team game | 2.9 | 2.6 | ±0.638 | WITHIN |

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
| kickoff touchback share | 0.451 | 0.462 | ±0.085 | WITHIN |
| mean start after a non-touchback kickoff (yardline_100) | 77.1 | 77.0 | ±2.3 | WITHIN |
| mean realized punt net, LOS opp 39-30 | 25.9 | 28.0 | ±6.2 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS opp 49-40 | 33.4 | 32.9 | ±3.1 | WITHIN |
| mean realized punt net, LOS own 1-10 | 42.0 | 43.7 | ±8.5 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS own 11-20 | 41.8 | 43.3 | ±6.1 | WITHIN |
| mean realized punt net, LOS own 21-30 | 43.8 | 43.7 | ±4.5 | WITHIN |
| mean realized punt net, LOS own 31-40 | 42.6 | 42.3 | ±5.0 | WITHIN |
| mean realized punt net, LOS own 41-50 | 38.8 | 38.8 | ±4.0 | WITHIN |
| mean kickoff return yards (non-touchback kickoffs) | 23.2 | 23.0 | ±2.4 | WITHIN |
| mean punt return yards (returned punts) | 9.6 | 9.2 | ±2.6 | WITHIN |
| punt share of possessions ending in Q4's last 5:00 or OT, offense trailing 1-8 | 0.062 | 0.119 | ±0.171 | WITHIN |
| punt share of possessions ending in Q4's last 2:00 or OT, offense trailing 1-8 | 0.000 | 0.008 | ±0.058 | INSUFFICIENT SAMPLE |
| third-down attempts per punt drive | 1.186 | 1.185 | ±0.081 | WITHIN |
| sacks per dropback | 0.059 | 0.062 | ±0.015 | WITHIN |
| DB share of sack credits | 0.062 | 0.063 | ±0.064 | WITHIN |
| DL share of sack credits | 0.651 | 0.599 | ±0.129 | WITHIN |
| LB share of sack credits | 0.287 | 0.337 | ±0.125 | WITHIN |
| mean drive start, all drives (2012 all-drive centre) | 72.2 | 72.3 | — | INFORMATIONAL |
| mean drive start (2012 centre over modelled transitions) | 72.2 | 72.8 | — | INFORMATIONAL |
| start-bin share 90-99 | 0.093 | 0.096 | — | INFORMATIONAL |
| start-bin share 81-89 | 0.175 | 0.160 | — | INFORMATIONAL |
| start-bin share 80-80 | 0.260 | 0.251 | — | INFORMATIONAL |
| start-bin share 70-79 | 0.182 | 0.191 | — | INFORMATIONAL |
| start-bin share 60-69 | 0.119 | 0.123 | — | INFORMATIONAL |
| start-bin share 50-59 | 0.054 | 0.071 | — | INFORMATIONAL |
| start-bin share 40-49 | 0.041 | 0.043 | — | INFORMATIONAL |
| start-bin share 30-39 | 0.028 | 0.023 | — | INFORMATIONAL |
| start-bin share 20-29 | 0.023 | 0.021 | — | INFORMATIONAL |
| start-bin share 1-19 | 0.025 | 0.022 | — | INFORMATIONAL |
| touchdown share, start opp 49-1 | 0.362 | 0.349 | — | INFORMATIONAL |
| punt share, start opp 49-1 | 0.037 | 0.108 | — | INFORMATIONAL |
| touchdown share, start own 1-20 | 0.181 | 0.158 | — | INFORMATIONAL |
| punt share, start own 1-20 | 0.471 | 0.486 | — | INFORMATIONAL |
| touchdown share, start own 21-50 | 0.231 | 0.199 | — | INFORMATIONAL |
| punt share, start own 21-50 | 0.380 | 0.402 | — | INFORMATIONAL |
| points per drive, start 1-19 | 5.5 | 4.5 | — | INFORMATIONAL |
| points per drive, start 20-29 | 3.3 | 4.1 | — | INFORMATIONAL |
| points per drive, start 30-39 | 2.7 | 3.1 | — | INFORMATIONAL |
| points per drive, start 40-49 | 3.2 | 2.6 | — | INFORMATIONAL |
| points per drive, start 50-59 | 3.0 | 2.2 | — | INFORMATIONAL |
| points per drive, start 60-69 | 2.1 | 1.829 | — | INFORMATIONAL |
| points per drive, start 70-79 | 1.855 | 1.707 | — | INFORMATIONAL |
| points per drive, start 80-89 | 1.676 | 1.473 | — | INFORMATIONAL |
| points per drive, start 90-99 | 1.270 | 1.140 | — | INFORMATIONAL |
| QB scramble share of QB carries (label stream; nflscrapR 643/1,228) | 0.846 | 0.557 | — | INFORMATIONAL |
| fourth-down attempts per team game (drive chains) | 0.776 | 0.881 | — | INFORMATIONAL |
| fourth-down conversions per team game (drive chains) | 0.431 | 0.439 | — | INFORMATIONAL |
| kneels per team game | 0.500 | 0.717 | — | INFORMATIONAL |
| overtime punt share | 0.500 | 0.311 | — | INFORMATIONAL |

### Ledger coherence

Zero-tolerance counts from `runtime.play_detail.check_ledger` (15 original and 17 kernel 2013.7 spot and label classes). Games checked: 29. The kick-row and label classes need the full snap ledger.

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

## Kernel 2014.6 cohort (Week 5)

**Calibration base:** 2010_2014w4 (`library/data/2010_2014w4_nfl_aggregate_baseline.json`, `library/data/2010_2014w4_nfl_drive_model.json`, `library/data/2010_2014w4_nfl_field_position_model.json`, `library/data/2010_2014w4_nfl_position_usage_baseline.json`, `library/data/2010_2014w4_nfl_injury_calibration.json`, `library/data/2014_strength_calibration_v2.json`, `library/data/2010_2014w4_scoring_decisions.json`, `library/data/2010_2014w4_fourth_down_decisions.json`, `library/data/2010_2014w4_ball_security.json`, `library/data/2010_2014w4_penalties.json`, `library/data/2010_2014w4_yardage.json`). **Team-games audited:** 30. Carry shares exclude kneels.

| Metric | Observed | 2010_2014w4 base centre | Tolerance | Status |
|---|---:|---:|---:|---|
| QB1 share of team pass attempts | 1.000 | 0.974 | ±0.050 | WITHIN |
| top receiver share of team targets (team-game) | 0.304 | 0.290 | ±0.035 | WITHIN |
| top rusher share of non-QB carries (team-game) | 0.711 | 0.694 | ±0.086 | WITHIN |
| FB share of carries | 0.013 | 0.027 | ±0.050 | WITHIN |
| QB share of carries | 0.076 | 0.089 | ±0.050 | WITHIN |
| RB share of carries | 0.893 | 0.859 | ±0.050 | WITHIN |
| TE share of carries | 0.000 | 0.001 | ±0.050 | WITHIN |
| WR share of carries | 0.019 | 0.022 | ±0.050 | WITHIN |
| FB share of targets | 0.023 | 0.026 | ±0.050 | WITHIN |
| RB share of targets | 0.197 | 0.165 | ±0.050 | WITHIN |
| TE share of targets | 0.201 | 0.211 | ±0.050 | WITHIN |
| WR share of targets | 0.580 | 0.597 | ±0.050 | WITHIN |
| DB share of tackle credits | 0.395 | 0.402 | ±0.050 | WITHIN |
| DL share of tackle credits | 0.249 | 0.226 | ±0.050 | WITHIN |
| LB share of tackle credits | 0.356 | 0.351 | ±0.050 | WITHIN |
| Assisted share of tackle credits | 0.331 | 0.348 | ±0.050 | WITHIN |
| plays per team game | 64.1 | 64.0 | ±6.0 | WITHIN |
| yards per team game | 346.4 | 344.9 | ±40.0 | WITHIN |
| points per team game | 22.1 | 22.6 | ±5.0 | WITHIN |
| first downs per team game | 19.7 | 19.6 | ±3.0 | WITHIN |
| third down attempts per team game | 13.3 | 13.4 | ±2.5 | WITHIN |
| third down rate | 0.345 | 0.384 | ±0.060 | WITHIN |

Points: from kernel 2014.6 the two-point tries, onside kicks and the non-offensive (interception, fumble, punt, blocked-kick and kickoff return) touchdowns with their tries are modelled from the 2010-2014 scoring artifact (the scoring-decision rows below); points per team-game are measured, never forecast. Yards per team game are net of sack yards.

### Drive model rows

Centres from the base's band centres (equal weight per event); tolerance is three standard errors at the observed sample.

| Metric | Observed | 2010_2014w4 base centre | Tolerance | Status |
|---|---:|---:|---:|---|
| FG accuracy | 0.879 | 0.840 | ±0.145 | WITHIN |
| FG accuracy <30 yd | 0.929 | 0.965 | ±0.146 | INSUFFICIENT SAMPLE |
| FG accuracy 30-39 yd | 0.933 | 0.886 | ±0.246 | INSUFFICIENT SAMPLE |
| FG accuracy 40-49 yd | 0.824 | 0.777 | ±0.303 | INSUFFICIENT SAMPLE |
| FG accuracy 50+ yd | 0.833 | 0.627 | ±0.419 | INSUFFICIENT SAMPLE |
| XP accuracy (informational; partially verified) | 1.000 | 0.993 | ±0.030 | WITHIN |
| FGA per team game | 1.933 | 1.947 | ±0.764 | WITHIN (known detection) |
| FGM per team game | 1.700 | 1.635 | ±0.700 | WITHIN (known detection) |
| drives per team game (nflverse definition; PFR 10.47) | 12.0 | 11.8 | ±1.880 | WITHIN |
| punts per team game (drive-ending) | 5.3 | 4.8 | ±1.203 | WITHIN (known detection) |
| drive share: touchdown | 0.188 | 0.195 | ±0.063 | WITHIN (provisional detection, re-graded at B17) |
| drive share: field goal attempt | 0.161 | 0.165 | ±0.059 | WITHIN |
| drive share: punt | 0.443 | 0.409 | ±0.078 | WITHIN (provisional detection, re-graded at B17) |
| drive share: turnover (INT + fumble lost) | 0.102 | 0.127 | ±0.053 | WITHIN |
| drive share: downs | 0.036 | 0.036 | ±0.029 | WITHIN |
| drive share: safety | 0.000 | 0.003 | ±0.008 | WITHIN (provisional detection, re-graded at B17) |
| drive share: clock | 0.069 | 0.065 | ±0.039 | WITHIN (known detection) |
| clock-expired drives per team game | 0.833 | 0.761 | ±0.478 | WITHIN (known detection) |
| offensive-drive turnovers per team game | 1.233 | 1.500 | ±0.671 | WITHIN |
| interception share of turnovers | 0.649 | 0.641 | ±0.237 | WITHIN |

Known detections (`runtime/bands.py` `KNOWN_DETECTIONS`): graded rows with a documented design cause, accepted rather than tuned. Each stays graded; OUTSIDE within 2x its tolerance is the documented detection, and beyond that it is investigated. No centre, tolerance, coefficient or pool was changed. A row marked PROVISIONAL is a carried diagnosis from the kernel 2014.6 build, not an accepted detection: it is not bounded, and batch B17 re-grades it with the provisional status removed; a row still OUTSIDE then goes to the user (U8).

- punts per team game (drive-ending): the half-final redirect skews surviving interior drives short and punt-heavy (runtime/README.md, kernel 2013.6 limitations).
- FGM per team game: adopted as documented by the user's decision of September 27, 2026: the first-half half-final redirect starts first-half final possessions early, field-goal-heavy and clock-light (library/2012_field_position_model_calibration.md, acceptance).
- drive share: clock: adopted as documented by the user's decision of September 27, 2026: the first-half half-final redirect starts first-half final possessions early, field-goal-heavy and clock-light (library/2012_field_position_model_calibration.md, acceptance).
- clock-expired drives per team game: adopted as documented by the user's decision of September 27, 2026: the first-half half-final redirect starts first-half final possessions early, field-goal-heavy and clock-light (library/2012_field_position_model_calibration.md, acceptance).
- FGA per team game: field-goal attempts rise with FGM from the first-half half-final redirect; kernel 2014.2 also stops masking late field goals, whose expected share by need now tracks 2012 (runtime/README.md, kernel 2014.2 acceptance).
- punt share of possessions ending in Q4's last 5:00 or OT, offense trailing 1-8: about 70 events per 250 games; the 2014.2 expected late mix by need tracks 2012 (trailing 4-8 punts 0.173 against 0.179), a 750-game fresh sample reads 0.087 inside its tolerance, and the rest is the timing mix of possessions that end in the last 5:00 (runtime/README.md, kernel 2014.2 acceptance).
- first-half final possessions starting with 0-30 s left (share): PROVISIONAL (batch B5X, October 3, 2026; re-graded at B17 with the provisional status removed, never auto-registered permanently): 0.428 against 0.494 +/- 0.034, every block; attribution: design-measured residual: kickoff and return time are not modelled, so first-half final windows run slightly long (runtime/README.md, batch B5 acceptance); expected to resolve: residual note (kernel 2014.6 end-of-half design); no batch is expected to move it.
- first-half final possessions starting with 31-60 s left (share): PROVISIONAL (batch B5X, October 3, 2026; re-graded at B17 with the provisional status removed, never auto-registered permanently): 0.317 against 0.257 +/- 0.029, every block; attribution: the same design-measured residual as the 0-30 s window: the share the 0-30 s window loses moves here (runtime/README.md, batch B5 acceptance); expected to resolve: residual note (kernel 2014.6 end-of-half design); no batch is expected to move it.
- timeouts per team-game: PROVISIONAL (batch B5X, October 3, 2026; re-graded at B17 with the provisional status removed, never auto-registered permanently): 3.38 against 3.70 +/- 0.08, every block; kernel 2014.5 reads 3.29; attribution: design-measured residual: a drive replay cannot charge timeouts it does not carry (runtime/README.md, batch B5 acceptance and attribution); expected to resolve: residual note (kernel 2014.6 end-of-half design); no batch is expected to move it.
- drive share: touchdown: PROVISIONAL (batch B5X, October 3, 2026; re-graded at B17 with the provisional status removed, never auto-registered permanently): 0.204 against 0.195 on A2; with punt and safety on A1; attribution: the home term is not centred (at neutral sites the share reads 0.189); present under kernel 2014.5 on the same fixture; expected to resolve: B7 (the HOME_EDGE refit).
- drive share: punt: PROVISIONAL (batch B5X, October 3, 2026; re-graded at B17 with the provisional status removed, never auto-registered permanently): OUTSIDE on A1 with touchdown; attribution: the uncentred home term, as drive share: touchdown; expected to resolve: B7 (the HOME_EDGE refit).
- drive share: safety: PROVISIONAL (batch B5X, October 3, 2026; re-graded at B17 with the provisional status removed, never auto-registered permanently): 0.0017-0.0020 against 0.0028; also low under kernel 2014.5; attribution: the uncentred home term, with touchdown and punt (batch B5 acceptance); expected to resolve: B7 (the HOME_EDGE refit).
- top receiver share of team targets (team-game): PROVISIONAL (batch B5X, October 3, 2026; re-graded at B17 with the provisional status removed, never auto-registered permanently): 0.299 against 0.291 +/- 0.003; OUTSIDE under kernel 2014.5 too; attribution: the synthetic acceptance fixture and the usage tilt; expected to resolve: B13/B16 (yardage credit and credit concentration).
- punt share of possessions ending in Q4's last 2:00 or OT, offense trailing 1-8: PROVISIONAL (batch B5X, October 3, 2026; re-graded at B17 with the provisional status removed, never auto-registered permanently): 0.010-0.016 against 0.004 (2 of 536 real possessions); attribution: the pooled base, not the regimes: the B5 attribution run moves the row from 0.004 to 0.017 with the base alone; expected to resolve: unexplained; re-grade at B17.
- sacks per dropback: PROVISIONAL (batch B5X, October 3, 2026; re-graded at B17 with the provisional status removed, never auto-registered permanently): 0.069 against 0.063 on A1, strength records present; attribution: the synthetic strength records' sack term; expected to resolve: B7 (strength v4 at runtime).
- third-down attempts per punt drive: PROVISIONAL (batch B5X, October 3, 2026; re-graded at B17 with the provisional status removed, never auto-registered permanently): 1.200 against 1.189 +/- 0.010 on A2; attribution: no cause isolated at B5; expected to resolve: unexplained; re-grade at B17.

### Field-position and late-game rows

Centres from the base's band centres and its drawn transition pools. Rates use 3*sqrt(p(1-p)/n), counts 3*sqrt(c/n) and means 3*sd/sqrt(n); a row reads INSUFFICIENT SAMPLE below 30 events. INFORMATIONAL rows are shapes, not grades; the zero-tolerance rows read OUTSIDE on any event.

| Metric | Observed | 2010_2014w4 base centre | Tolerance | Status |
|---|---:|---:|---:|---|
| kickoff touchback share | 0.429 | 0.487 | ±0.124 | WITHIN |
| mean start after a non-touchback kickoff (yardline_100) | 76.9 | 76.9 | ±3.3 | WITHIN |
| mean realized punt net, LOS opp 39-30 | 17.0 | 26.0 | ±10.9 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS opp 49-40 | 32.0 | 32.1 | ±4.2 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS own 1-10 | 44.2 | 42.6 | ±11.4 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS own 11-20 | 45.0 | 43.5 | ±7.4 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS own 21-30 | 43.3 | 42.3 | ±5.6 | WITHIN |
| mean realized punt net, LOS own 31-40 | 43.1 | 41.6 | ±6.9 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS own 41-50 | 32.3 | 38.4 | ±5.9 | INSUFFICIENT SAMPLE |
| mean kickoff return yards (non-touchback kickoffs) | 24.1 | 23.1 | ±3.5 | WITHIN |
| mean punt return yards (returned punts) | 9.7 | 9.1 | ±3.8 | WITHIN |
| punt share of possessions ending in Q4's last 5:00 or OT, offense trailing 1-8 | 0.067 | 0.100 | ±0.233 | INSUFFICIENT SAMPLE |
| punt share of possessions ending in Q4's last 2:00 or OT, offense trailing 1-8 | 0.000 | 0.004 | ±0.058 | INSUFFICIENT SAMPLE |
| third-down attempts per punt drive | 1.210 | 1.189 | ±0.107 | WITHIN |
| sacks per dropback | 0.072 | 0.063 | ±0.022 | WITHIN |
| DB share of sack credits | 0.051 | 0.083 | ±0.093 | WITHIN |
| DL share of sack credits | 0.595 | 0.566 | ±0.167 | WITHIN |
| LB share of sack credits | 0.354 | 0.351 | ±0.161 | WITHIN |
| first-half final possessions: field-goal-attempt share | 0.200 | 0.265 | ±0.342 | INSUFFICIENT SAMPLE |
| first-half final possessions: clock share | 0.800 | 0.663 | ±0.366 | INSUFFICIENT SAMPLE |
| P(final | first-half possession starting with 61-120 s left) | 0.300 | 0.274 | ±0.423 | INSUFFICIENT SAMPLE |
| P(final | first-half possession starting with 121-240 s left) | 0.000 | 0.081 | ±0.199 | INSUFFICIENT SAMPLE |
| first-half final possessions starting with 0-30 s left (share) | 0.533 | 0.494 | ±0.387 | INSUFFICIENT SAMPLE |
| first-half final possessions starting with 31-60 s left (share) | 0.267 | 0.257 | ±0.339 | INSUFFICIENT SAMPLE |
| first-half final possessions starting with 61-120 s left (share) | 0.200 | 0.177 | ±0.296 | INSUFFICIENT SAMPLE |
| first-half final possessions starting with 121-240 s left (share) | 0.000 | 0.054 | ±0.176 | INSUFFICIENT SAMPLE |
| first-half final possessions starting with 241-600 s left (share) | 0.000 | 0.018 | ±0.102 | INSUFFICIENT SAMPLE |
| first-half final possessions starting with 601-1800 s left (share) | 0.000 | 0.000 | ±0.000 | INSUFFICIENT SAMPLE |
| clock-expired first halves ending inside the opponent 30 | 0.000 | 0.043 | ±0.176 | INSUFFICIENT SAMPLE |
| field-goal attempts inside 2:00 of Q4, offense trailing by 12 or more (per team-game) | 0.000 | 0.001 | ±0.017 | WITHIN |
| field-goal attempts inside 2:00 of Q4, offense trailing by 9-11 (per team-game) | 0.000 | 0.011 | — | INFORMATIONAL |
| defensive timeouts per second-half possession starting over 10:00 | 0.045 | 0.040 | ±0.057 | WITHIN |
| timeouts per team-game | 3.1 | 3.7 | ±0.907 | WITHIN |
| overtime spikes with more than 148 s left (zero tolerance) | — | 0.000 | ±0.000 | INSUFFICIENT SAMPLE |
| trailing overtime punts (zero tolerance) | 0.000 | 0.000 | ±0.000 | WITHIN |
| mean drive start, all drives (all-drive centre) | 72.8 | 71.6 | — | INFORMATIONAL |
| start-bin share 90-99 | 0.091 | 0.091 | — | INFORMATIONAL |
| start-bin share 81-89 | 0.147 | 0.150 | — | INFORMATIONAL |
| start-bin share 80-80 | 0.247 | 0.232 | — | INFORMATIONAL |
| start-bin share 70-79 | 0.230 | 0.203 | — | INFORMATIONAL |
| start-bin share 60-69 | 0.125 | 0.138 | — | INFORMATIONAL |
| start-bin share 50-59 | 0.058 | 0.074 | — | INFORMATIONAL |
| start-bin share 40-49 | 0.055 | 0.045 | — | INFORMATIONAL |
| start-bin share 30-39 | 0.017 | 0.027 | — | INFORMATIONAL |
| start-bin share 20-29 | 0.014 | 0.020 | — | INFORMATIONAL |
| start-bin share 1-19 | 0.017 | 0.021 | — | INFORMATIONAL |
| points per drive, start 1-19 | 2.2 | 4.5 | — | INFORMATIONAL |
| points per drive, start 20-29 | 3.4 | 3.9 | — | INFORMATIONAL |
| points per drive, start 30-39 | 3.3 | 3.4 | — | INFORMATIONAL |
| points per drive, start 40-49 | 3.9 | 2.7 | — | INFORMATIONAL |
| points per drive, start 50-59 | 2.1 | 2.3 | — | INFORMATIONAL |
| points per drive, start 60-69 | 1.756 | 1.855 | — | INFORMATIONAL |
| points per drive, start 70-79 | 1.422 | 1.615 | — | INFORMATIONAL |
| points per drive, start 80-89 | 1.620 | 1.421 | — | INFORMATIONAL |
| points per drive, start 90-99 | 0.879 | 1.127 | — | INFORMATIONAL |
| QB scramble share of QB carries (label stream) | 0.400 | 0.579 | — | INFORMATIONAL |
| spikes stamped with more than 148 s left in the half (share, informational) | — | 0.000 | — | INSUFFICIENT SAMPLE |
| fourth-down attempts per team game (drive chains) | 0.900 | 0.889 | — | INFORMATIONAL |
| fourth-down conversions per team game (drive chains) | 0.400 | 0.423 | — | INFORMATIONAL |
| kneels per team game | 0.933 | 0.720 | — | INFORMATIONAL |

### Injury rows

The injury calibration's acceptance bands (kernel 2014.4 method): WITHIN when the observed value lies inside the band; the centre column is the band midpoint and the tolerance its half-width.

| Metric | Observed | band midpoint | Tolerance | Status |
|---|---:|---:|---:|---|
| injury onsets per team-game | 2.2 | 2.7 | ±0.432 | OUTSIDE |
| rest-of-game removals per team-game | 0.733 | 0.861 | ±0.253 | WITHIN |
| head/neck share of onsets | 0.119 | 0.169 | ±0.034 | OUTSIDE |
| head/neck onsets per team-game | 0.267 | 0.454 | ±0.083 | OUTSIDE |
| lower-extremity share of onsets | 0.701 | 0.598 | ±0.057 | OUTSIDE |
| time-loss share of onsets (short or longer) | 0.299 | 0.285 | ±0.071 | WITHIN |
| long-term share of onsets | 0.030 | 0.045 | ±0.027 | WITHIN |

### Scoring-decision rows

Two-point tries, onside kicks and non-offensive touchdowns (kernel 2014.6 batch B9). Centres from the base's scoring artifact; rates use 3*sqrt(p(1-p)/n) and counts 3*sqrt(c/n), and a rate row reads INSUFFICIENT SAMPLE below 30 events. INFORMATIONAL rows are not graded and MEASURED rows have no centre.

| Metric | Observed | 2010_2014w4 base centre | Tolerance | Status |
|---|---:|---:|---:|---|
| two-point attempt share of tries | 0.069 | 0.043 | ±0.071 | WITHIN |
| two-point conversion rate | 0.400 | 0.496 | ±0.671 | INSUFFICIENT SAMPLE |
| extra-point rate | 1.000 | 0.993 | ±0.030 | WITHIN |
| fourth-quarter go share of tries down 2 after the touchdown | — | 0.941 | — | INSUFFICIENT SAMPLE |
| onside kicks per team-game | 0.103 | 0.107 | ±0.183 | WITHIN |
| onside share of kicks trailing by 1-8 inside 2:00 | 1.000 | 0.943 | ±0.696 | INSUFFICIENT SAMPLE |
| tries and kickoffs decided by a club's block or a live answer (informational; counted apart, never graded against the chart) | 4.0 | — | — | MEASURED |
| expected onside recovery rate | 0.000 | 0.110 | ±0.665 | INSUFFICIENT SAMPLE |
| surprise onside recovery rate (informational) | 1.000 | 0.241 | — | INSUFFICIENT SAMPLE |
| interception-return touchdown share of interceptions | 0.083 | 0.122 | ±0.200 | INSUFFICIENT SAMPLE |
| fumble-return touchdown share of lost fumbles | 0.154 | 0.080 | ±0.225 | INSUFFICIENT SAMPLE |
| punt return or blocked-punt touchdown share of punts | 0.006 | 0.009 | ±0.022 | WITHIN |
| kickoff-return touchdown share of deep kickoffs | 0.000 | 0.004 | ±0.015 | WITHIN |
| blocked field-goal touchdowns per missed field goal (informational) | 0.000 | 0.007 | — | INSUFFICIENT SAMPLE |
| non-offensive touchdowns per team-game (informational) | 0.167 | 0.230 | — | INFORMATIONAL |
| points per team-game (measured; no forecast) | 22.1 | — | — | MEASURED |

### Fourth-down rows

Fourth-down decisions and conversions (kernel 2014.6 batch B9F). Centres from the base's fourth-down artifact; the go share and attempts rows grade only the league chart's decisions, and the club decisions of a standing rule or a live call are counted apart. Rates use 3*sqrt(p(1-p)/n) and counts 3*sqrt(c/n); a rate row reads INSUFFICIENT SAMPLE below 30 events.

| Metric | Observed | 2010_2014w4 base centre | Tolerance | Status |
|---|---:|---:|---:|---|
| fourth-down go share of chart decisions | 0.115 | 0.118 | ±0.063 | WITHIN |
| fourth-down attempts per team-game (team-games decided by the chart) | 0.931 | 0.882 | ±0.523 | WITHIN |
| fourth-down conversion rate | 0.444 | 0.479 | ±0.288 | INSUFFICIENT SAMPLE |
| field-goal share of chart fourth-down decisions (informational) | 0.218 | 0.239 | — | INFORMATIONAL |
| punt share of chart fourth-down decisions (informational) | 0.667 | 0.643 | — | INFORMATIONAL |
| fourth-down decisions per team-game (informational) | 8.0 | 7.5 | — | INFORMATIONAL |
| chart-conditional go count against the sum of the chart decisions' go probabilities (informational) | 27.0 | 23.6 | — | INFORMATIONAL |
| fourth downs decided by a club's block or a live answer (informational; counted apart, never graded against the chart) | 6.0 | — | — | MEASURED |

### Ball-security rows

Fumbles, muffs and kicking-team recoveries (kernel 2014.6 batch B10). Centres from the base's ball-security artifact (the fumbles row in the nflverse definition, less the defense's own fumbles after a turnover); fumbles per team-game use 3*sqrt(phi*c/n) with the artifact's team-game dispersion, other counts 3*sqrt(c/n) and rates 3*sqrt(p(1-p)/n); a rate row reads INSUFFICIENT SAMPLE below 30 events. Who fumbled, forced, recovered or muffed is a group draw or a replayed record, never evidence of a player's ball security.

| Metric | Observed | 2010_2014w4 base centre | Tolerance | Status |
|---|---:|---:|---:|---|
| fumbles per team-game (nflverse definition, less defensive fumbles after a turnover) | 1.167 | 1.305 | ±0.658 | WITHIN |
| lost fumbles per team-game | 0.500 | 0.624 | ±0.433 | WITHIN |
| offense-kept share of scrimmage fumbles | 0.552 | 0.497 | ±0.279 | INSUFFICIENT SAMPLE |
| sack share of lost scrimmage fumbles | 0.462 | 0.316 | ±0.387 | INSUFFICIENT SAMPLE |
| kicking-team recoveries per team-game (punts; kickoffs from the 35 from 2011) | 0.067 | 0.073 | ±0.148 | WITHIN |
| muffer role share (the returner, muffs with a recorded muffer) | 1.000 | 1.000 | ±0.000 | INSUFFICIENT SAMPLE |
| forced share of lost non-aborted scrimmage fumbles (informational) | 1.000 | 0.946 | — | INSUFFICIENT SAMPLE |
| forcer also recovers, forced lost scrimmage fumbles (informational) | 0.308 | 0.141 | — | INSUFFICIENT SAMPLE |
| muffs per punt (informational) | 0.037 | 0.025 | — | INFORMATIONAL |
| receiving club's keep share of punt muffs (informational) | 0.667 | 0.701 | — | INSUFFICIENT SAMPLE |
| lost-fumble terminal snaps: run share (informational; the base pool's lost entries) | 0.385 | 0.421 | — | INSUFFICIENT SAMPLE |
| lost-fumble terminal snaps: catch share (informational; the base pool's lost entries) | 0.154 | 0.262 | — | INSUFFICIENT SAMPLE |
| lost-fumble terminal snaps: sack share (informational; the base pool's lost entries) | 0.462 | 0.317 | — | INSUFFICIENT SAMPLE |

### Penalty rows

Replayed penalty records (kernel 2014.6 batch B11). Centres from the base's penalty artifact, in the engine's scope (the replayed drives' records and the kick plays' records; records enforced after a possession or on a field-goal row are not replayed). Accepted penalties use 3*sqrt(phi*c/n) with the artifact's team-game dispersion, penalty yards 3*SD/sqrt(n) and first downs by penalty 3*sqrt(c/n). Each accepted foul is charged to the fouling club; who fouled is a group draw, never evidence, and an accept or decline is the real record's. The net-yards row is reported, never tuned.

| Metric | Observed | 2010_2014w4 base centre | Tolerance | Status |
|---|---:|---:|---:|---|
| accepted penalties per team-game (drive and kick plays; the fouling club) | 6.5 | 5.9 | ±1.480 | WITHIN |
| penalty yards per team-game (the fouling club) | 51.5 | 49.6 | ±14.1 | WITHIN |
| first downs by penalty per team-game | 1.967 | 1.712 | ±0.717 | WITHIN |
| defense share of accepted drive penalties (informational) | 0.429 | 0.435 | — | INFORMATIONAL |
| declined penalties per team-game (informational) | 0.767 | 0.655 | — | INFORMATIONAL |
| offsetting penalties per team-game (informational) | 0.067 | 0.221 | — | INFORMATIONAL |
| kick-play accepted penalties per team-game (informational) | 0.633 | 0.655 | — | INFORMATIONAL |
| net yards the records move the offense per team-game (reported, not tuned) | -0.967 | — | — | MEASURED |

### Yardage rows

The replayed yard split (kernel 2014.6 batch B13): each replayed drive keeps its own real rushing and passing yards, completions and sack losses, and its own run and completion values. Centres from the base's yardage artifact; yards per carry uses 3*SD/(carries*sqrt(n)) with the artifact's team-game residual SD, the completion rate and run share 3*sqrt(phi*p(1-p)/N) with its team-game dispersion, and rushing yards 3*SD/sqrt(n). The run-shape rows are graded only on the synthetic all-club acceptance samples; on a real cohort they are INFORMATIONAL.

| Metric | Observed | 2010_2014w4 base centre | Tolerance | Status |
|---|---:|---:|---:|---|
| yards per carry (kneels included) | 4.1 | 4.2 | ±0.698 | WITHIN |
| completion rate (spikes as attempts) | 0.614 | 0.610 | ±0.052 | WITHIN |
| run share of scrimmage plays | 0.427 | 0.425 | ±0.061 | WITHIN |
| rushing yards per team-game (kneels included) | 112.2 | 115.0 | ±28.4 | WITHIN |
| share of non-kneel runs losing yards (informational) | 0.103 | 0.096 | — | INFORMATIONAL |
| share of non-kneel runs gaining 0 (informational) | 0.107 | 0.094 | — | INFORMATIONAL |
| share of non-kneel runs of 1-3 yards (informational) | 0.360 | 0.370 | — | INFORMATIONAL |
| share of non-kneel runs of 4-9 yards (informational) | 0.317 | 0.326 | — | INFORMATIONAL |
| share of non-kneel runs of 10-19 yards (informational) | 0.078 | 0.088 | — | INFORMATIONAL |
| share of non-kneel runs of 20+ yards (informational) | 0.034 | 0.026 | — | INFORMATIONAL |
| completions of 20+ yards per attempt (informational) | 0.107 | 0.091 | — | INFORMATIONAL |
| completions the layout forced per team-game (measured) | 0.233 | — | — | MEASURED |

### Ledger coherence

Zero-tolerance counts from `runtime.play_detail.check_ledger`, checked with this base's rules. Games checked: 15.

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
| possession sequence break | 0 | WITHIN |
| kick chain incoherent | 0 | WITHIN |
| fourth down decision incoherent | 0 | WITHIN |
| fumble credit incoherent | 0 | WITHIN |
| muff without muffer | 0 | WITHIN |
| penalty record invalid | 0 | WITHIN |
| penalty enforcement illegal | 0 | WITHIN |
| penalty counter mismatch | 0 | WITHIN |
| def label menu mismatch | 0 | WITHIN |
| def label wrong club | 0 | WITHIN |
