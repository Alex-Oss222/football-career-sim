# 2013 statistical band audit

**Version:** `2013-W09-BAND-AUDIT`
**Through:** Week 9.

League-wide receipts compared with the sourced 2012 shapes in `library/data/2012_nfl_aggregate_baseline.json`, `library/data/2012_nfl_position_usage_baseline.json`, `library/data/2012_nfl_drive_model.json` and `library/data/2012_nfl_field_position_model.json`. This is a defect detector for engine code and TeamInputs. An OUTSIDE row is investigated; it never reruns, selects or edits a closed game. Receipts are split into cohorts by kernel version; grading starts at 16 team-games per cohort.

## Legacy cohort: kernels 2013.4/2013.5

**Status:** legacy kernel, known ledger defects (Entries 35/38), detection only; never grounds to rerun.
**Team-games audited:** 96.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| QB1 share of team pass attempts | 1.000 | 0.978 | ±0.050 | WITHIN |
| FB share of carries | 0.021 | 0.021 | ±0.050 | WITHIN |
| QB share of carries | 0.077 | 0.090 | ±0.050 | WITHIN |
| RB share of carries | 0.879 | 0.867 | ±0.050 | WITHIN |
| TE share of carries | 0.001 | 0.000 | ±0.050 | WITHIN |
| WR share of carries | 0.022 | 0.019 | ±0.050 | WITHIN |
| FB share of targets | 0.017 | 0.026 | ±0.050 | WITHIN |
| RB share of targets | 0.155 | 0.155 | ±0.050 | WITHIN |
| TE share of targets | 0.214 | 0.215 | ±0.050 | WITHIN |
| WR share of targets | 0.614 | 0.602 | ±0.050 | WITHIN |
| DB share of tackle credits | 0.380 | 0.401 | ±0.050 | WITHIN |
| DL share of tackle credits | 0.252 | 0.226 | ±0.050 | WITHIN |
| LB share of tackle credits | 0.367 | 0.353 | ±0.050 | WITHIN |
| Assisted share of tackle credits | 0.324 | 0.339 | ±0.050 | WITHIN |
| plays per team game | 65.9 | 64.2 | ±6.0 | WITHIN |
| yards per team game | 352.6 | 347.2 | ±40.0 | WITHIN |
| points per team game | 21.2 | 22.8 | ±5.0 | WITHIN |
| first downs per team game | 20.4 | 19.8 | ±3.0 | WITHIN |
| third down attempts per team game | 13.7 | 13.3 | ±2.5 | WITHIN |
| third down rate | 0.377 | 0.383 | ±0.060 | WITHIN |

Drive-model rows and ledger coherence: not measurable for this cohort (legacy receipts carry no drives summary or kicking-attempt counters).

## Kernel 2013.6 cohort (Weeks 4-8, detection only)

**Status:** known field-position, label and late-game defects (Entries 40-45 and the 2013.7 adoption entry); detection only; never grounds to rerun.
**Team-games audited:** 144.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| QB1 share of team pass attempts | 1.000 | 0.978 | ±0.050 | WITHIN |
| FB share of carries | 0.016 | 0.021 | ±0.050 | WITHIN |
| QB share of carries | 0.086 | 0.090 | ±0.050 | WITHIN |
| RB share of carries | 0.878 | 0.867 | ±0.050 | WITHIN |
| TE share of carries | 0.000 | 0.000 | ±0.050 | WITHIN |
| WR share of carries | 0.020 | 0.019 | ±0.050 | WITHIN |
| FB share of targets | 0.016 | 0.026 | ±0.050 | WITHIN |
| RB share of targets | 0.163 | 0.155 | ±0.050 | WITHIN |
| TE share of targets | 0.217 | 0.215 | ±0.050 | WITHIN |
| WR share of targets | 0.604 | 0.602 | ±0.050 | WITHIN |
| DB share of tackle credits | 0.377 | 0.401 | ±0.050 | WITHIN |
| DL share of tackle credits | 0.260 | 0.226 | ±0.050 | WITHIN |
| LB share of tackle credits | 0.363 | 0.353 | ±0.050 | WITHIN |
| Assisted share of tackle credits | 0.331 | 0.339 | ±0.050 | WITHIN |
| plays per team game | 65.1 | 64.2 | ±6.0 | WITHIN |
| yards per team game | 358.9 | 347.2 | ±40.0 | WITHIN |
| points per team game | 21.2 | 22.8 | ±5.0 | WITHIN |
| first downs per team game | 20.8 | 19.8 | ±3.0 | WITHIN |
| third down attempts per team game | 13.4 | 13.3 | ±2.5 | WITHIN |
| third down rate | 0.384 | 0.383 | ±0.060 | WITHIN |

Points: non-offensive touchdowns, their tries and two-point tries are not modelled by design (about 1.7-2.0 points per team game below the 2012 centre); the ±5.0 tolerance is deliberately not tightened.

### Drive model rows

Centres from the 2012 drive model (nflverse drive definition) and period totals; tolerance is three standard errors at the observed sample.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| FG accuracy | 0.841 | 0.839 | ±0.066 | WITHIN |
| FG accuracy <30 yd | 0.917 | 0.967 | ±0.064 | WITHIN |
| FG accuracy 30-39 yd | 0.927 | 0.891 | ±0.103 | WITHIN |
| FG accuracy 40-49 yd | 0.800 | 0.802 | ±0.123 | WITHIN |
| FG accuracy 50+ yd | 0.588 | 0.609 | ±0.251 | WITHIN |
| XP accuracy (informational; partially verified) | 0.997 | 0.994 | ±0.013 | WITHIN |
| FGA per team game | 1.965 | 1.984 | ±0.352 | WITHIN |
| FGM per team game | 1.653 | 1.664 | ±0.322 | WITHIN |
| drives per team game (nflverse definition; PFR 10.47) | 12.1 | 11.7 | ±0.855 | WITHIN |
| punts per team game (drive-ending) | 5.1 | 4.8 | ±0.549 | WITHIN (known detection) |
| drive share: touchdown | 0.191 | 0.195 | ±0.028 | WITHIN |
| drive share: field goal attempt | 0.162 | 0.170 | ±0.027 | WITHIN |
| drive share: punt | 0.424 | 0.412 | ±0.035 | WITHIN |
| drive share: turnover (INT + fumble lost) | 0.126 | 0.125 | ±0.024 | WITHIN |
| drive share: downs | 0.027 | 0.033 | ±0.013 | WITHIN |
| drive share: safety | 0.003 | 0.002 | ±0.003 | WITHIN |
| drive share: clock | 0.067 | 0.063 | ±0.017 | WITHIN |
| clock-expired drives per team game | 0.812 | 0.734 | ±0.214 | WITHIN |
| offensive-drive turnovers per team game | 1.528 | 1.461 | ±0.302 | WITHIN |
| interception share of turnovers | 0.691 | 0.626 | ±0.098 | WITHIN |
| kickoffs per team game (informational; centre includes kicks not modelled: after non-offensive TDs, onside, re-kicks, after half-final scores) | 4.9 | 5.2 | ±0.570 | INFORMATIONAL |
| kick returns per team game | 2.6 | 2.6 | ±0.405 | WITHIN |

Known detections (`runtime/bands.py` `KNOWN_DETECTIONS`): graded rows with a documented design cause, accepted rather than tuned. Each stays graded; OUTSIDE within 2x its tolerance is the documented detection, and beyond that it is investigated. No centre, tolerance, coefficient or pool was changed.

- punts per team game (drive-ending): the half-final redirect skews surviving interior drives short and punt-heavy (runtime/README.md, kernel 2013.6 limitations).

### Ledger coherence

Zero-tolerance counts from `runtime.play_detail.check_ledger` over every receipt's drives summary plus the full snap ledgers. Games checked: 72. The kernel 2013.7 spot and label classes are not measurable for this cohort (its receipts carry no start spots).

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

## Kernel 2013.7 cohort (Week 9)

**Team-games audited:** 26. Carry shares exclude kneels, as in the 2012 baseline.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| QB1 share of team pass attempts | 1.000 | 0.978 | ±0.050 | WITHIN |
| FB share of carries | 0.006 | 0.021 | ±0.050 | WITHIN |
| QB share of carries | 0.093 | 0.090 | ±0.050 | WITHIN |
| RB share of carries | 0.878 | 0.867 | ±0.050 | WITHIN |
| TE share of carries | 0.000 | 0.000 | ±0.050 | WITHIN |
| WR share of carries | 0.024 | 0.019 | ±0.050 | WITHIN |
| FB share of targets | 0.014 | 0.026 | ±0.050 | WITHIN |
| RB share of targets | 0.161 | 0.155 | ±0.050 | WITHIN |
| TE share of targets | 0.226 | 0.215 | ±0.050 | WITHIN |
| WR share of targets | 0.598 | 0.602 | ±0.050 | WITHIN |
| DB share of tackle credits | 0.407 | 0.401 | ±0.050 | WITHIN |
| DL share of tackle credits | 0.259 | 0.226 | ±0.050 | WITHIN |
| LB share of tackle credits | 0.334 | 0.353 | ±0.050 | WITHIN |
| Assisted share of tackle credits | 0.300 | 0.339 | ±0.050 | WITHIN |
| plays per team game | 65.2 | 64.2 | ±6.0 | WITHIN |
| yards per team game | 377.1 | 347.2 | ±40.0 | WITHIN |
| points per team game | 20.5 | 22.8 | ±5.0 | WITHIN |
| first downs per team game | 20.7 | 19.8 | ±3.0 | WITHIN |
| third down attempts per team game | 13.3 | 13.3 | ±2.5 | WITHIN |
| third down rate | 0.350 | 0.383 | ±0.060 | WITHIN |

Points: non-offensive touchdowns, their tries and two-point tries are not modelled by design (about 1.7-2.0 points per team game below the 2012 centre); the ±5.0 tolerance is deliberately not tightened.

### Drive model rows

Centres from the 2012 drive model (nflverse drive definition) and period totals; tolerance is three standard errors at the observed sample.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| FG accuracy | 0.810 | 0.839 | ±0.145 | WITHIN |
| FG accuracy <30 yd | 1.000 | 0.967 | ±0.156 | INSUFFICIENT SAMPLE |
| FG accuracy 30-39 yd | 0.722 | 0.891 | ±0.220 | INSUFFICIENT SAMPLE |
| FG accuracy 40-49 yd | 0.875 | 0.802 | ±0.244 | INSUFFICIENT SAMPLE |
| FG accuracy 50+ yd | 0.250 | 0.609 | ±0.732 | INSUFFICIENT SAMPLE |
| XP accuracy (informational; partially verified) | 1.000 | 0.994 | ±0.032 | WITHIN |
| FGA per team game | 2.2 | 1.984 | ±0.829 | WITHIN |
| FGM per team game | 1.808 | 1.664 | ±0.759 | WITHIN (known detection) |
| drives per team game (nflverse definition; PFR 10.47) | 11.2 | 11.7 | ±2.0 | WITHIN |
| punts per team game (drive-ending) | 4.7 | 4.8 | ±1.291 | WITHIN (known detection) |
| drive share: touchdown | 0.192 | 0.195 | ±0.069 | WITHIN |
| drive share: field goal attempt | 0.199 | 0.170 | ±0.066 | WITHIN |
| drive share: punt | 0.414 | 0.412 | ±0.086 | WITHIN |
| drive share: turnover (INT + fumble lost) | 0.116 | 0.125 | ±0.058 | WITHIN |
| drive share: downs | 0.021 | 0.033 | ±0.032 | WITHIN |
| drive share: safety | 0.000 | 0.002 | ±0.008 | WITHIN |
| drive share: clock | 0.058 | 0.063 | ±0.043 | WITHIN (known detection) |
| clock-expired drives per team game | 0.654 | 0.734 | ±0.504 | WITHIN (known detection) |
| offensive-drive turnovers per team game | 1.308 | 1.461 | ±0.711 | WITHIN |
| interception share of turnovers | 0.794 | 0.626 | ±0.249 | WITHIN |
| kickoffs per team game (informational; centre includes kicks not modelled: after non-offensive TDs, onside, re-kicks, after half-final scores) | 4.8 | 5.2 | ±1.342 | INFORMATIONAL |
| kick returns per team game | 2.8 | 2.6 | ±0.954 | WITHIN |

Known detections (`runtime/bands.py` `KNOWN_DETECTIONS`): graded rows with a documented design cause, accepted rather than tuned. Each stays graded; OUTSIDE within 2x its tolerance is the documented detection, and beyond that it is investigated. No centre, tolerance, coefficient or pool was changed.

- punts per team game (drive-ending): the half-final redirect skews surviving interior drives short and punt-heavy (runtime/README.md, kernel 2013.6 limitations).
- FGM per team game: adopted as documented by the user's decision of September 27, 2026: the first-half half-final redirect starts first-half final possessions early, field-goal-heavy and clock-light (library/2012_field_position_model_calibration.md, acceptance).
- drive share: clock: adopted as documented by the user's decision of September 27, 2026: the first-half half-final redirect starts first-half final possessions early, field-goal-heavy and clock-light (library/2012_field_position_model_calibration.md, acceptance).
- clock-expired drives per team game: adopted as documented by the user's decision of September 27, 2026: the first-half half-final redirect starts first-half final possessions early, field-goal-heavy and clock-light (library/2012_field_position_model_calibration.md, acceptance).

### Field-position rows

Centres from the 2012 field-position model's band_centres. Rates use 3*sqrt(p(1-p)/n) and means 3*sd/sqrt(n) with the 2012 sd; a row reads INSUFFICIENT SAMPLE below 30 events. INFORMATIONAL rows are shapes, not grades.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| kickoff touchback share | 0.424 | 0.462 | ±0.134 | WITHIN |
| mean start after a non-touchback kickoff (yardline_100) | 77.8 | 77.0 | ±3.5 | WITHIN |
| mean realized punt net, LOS opp 39-30 | 26.2 | 28.0 | ±9.8 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS opp 49-40 | 34.4 | 32.9 | ±4.7 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS own 1-10 | 39.9 | 43.7 | ±13.1 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS own 11-20 | 45.7 | 43.3 | ±7.4 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS own 21-30 | 46.2 | 43.7 | ±7.0 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS own 31-40 | 42.7 | 42.3 | ±9.0 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS own 41-50 | 39.2 | 38.8 | ±5.3 | INSUFFICIENT SAMPLE |
| punt share of possessions ending in Q4's last 5:00 or OT, offense trailing 1-8 | 0.000 | 0.119 | ±0.367 | INSUFFICIENT SAMPLE |
| punt share of possessions ending in Q4's last 2:00 or OT, offense trailing 1-8 | 0.000 | 0.008 | ±0.109 | INSUFFICIENT SAMPLE |
| third-down attempts per punt drive | 1.140 | 1.185 | ±0.120 | WITHIN |
| sacks per dropback | 0.052 | 0.062 | ±0.023 | WITHIN |
| DB share of sack credits | 0.060 | 0.063 | ±0.103 | WITHIN |
| DL share of sack credits | 0.640 | 0.599 | ±0.208 | WITHIN |
| LB share of sack credits | 0.300 | 0.337 | ±0.201 | WITHIN |
| mean drive start, all drives (2012 all-drive centre) | 73.6 | 72.3 | — | INFORMATIONAL |
| mean drive start (2012 centre over modelled transitions) | 73.6 | 72.8 | — | INFORMATIONAL |
| start-bin share 90-99 | 0.116 | 0.096 | — | INFORMATIONAL |
| start-bin share 81-89 | 0.168 | 0.160 | — | INFORMATIONAL |
| start-bin share 80-80 | 0.236 | 0.251 | — | INFORMATIONAL |
| start-bin share 70-79 | 0.171 | 0.191 | — | INFORMATIONAL |
| start-bin share 60-69 | 0.168 | 0.123 | — | INFORMATIONAL |
| start-bin share 50-59 | 0.055 | 0.071 | — | INFORMATIONAL |
| start-bin share 40-49 | 0.041 | 0.043 | — | INFORMATIONAL |
| start-bin share 30-39 | 0.014 | 0.023 | — | INFORMATIONAL |
| start-bin share 20-29 | 0.021 | 0.021 | — | INFORMATIONAL |
| start-bin share 1-19 | 0.010 | 0.022 | — | INFORMATIONAL |
| touchdown share, start opp 49-1 | 0.200 | 0.349 | — | INFORMATIONAL |
| punt share, start opp 49-1 | 0.040 | 0.108 | — | INFORMATIONAL |
| touchdown share, start own 1-20 | 0.151 | 0.158 | — | INFORMATIONAL |
| punt share, start own 1-20 | 0.507 | 0.486 | — | INFORMATIONAL |
| touchdown share, start own 21-50 | 0.243 | 0.199 | — | INFORMATIONAL |
| punt share, start own 21-50 | 0.374 | 0.402 | — | INFORMATIONAL |
| points per drive, start 1-19 | 3.3 | 4.5 | — | INFORMATIONAL |
| points per drive, start 20-29 | 1.000 | 4.1 | — | INFORMATIONAL |
| points per drive, start 30-39 | 5.0 | 3.1 | — | INFORMATIONAL |
| points per drive, start 40-49 | 2.7 | 2.6 | — | INFORMATIONAL |
| points per drive, start 50-59 | 1.938 | 2.2 | — | INFORMATIONAL |
| points per drive, start 60-69 | 1.816 | 1.829 | — | INFORMATIONAL |
| points per drive, start 70-79 | 2.4 | 1.707 | — | INFORMATIONAL |
| points per drive, start 80-89 | 1.534 | 1.473 | — | INFORMATIONAL |
| points per drive, start 90-99 | 1.265 | 1.140 | — | INFORMATIONAL |
| QB scramble share of QB carries (label stream; nflscrapR 643/1,228) | — | 0.557 | — | INSUFFICIENT SAMPLE |
| fourth-down attempts per team game (drive chains) | 0.846 | 0.881 | — | INFORMATIONAL |
| fourth-down conversions per team game (drive chains) | 0.538 | 0.439 | — | INFORMATIONAL |
| kneels per team game | 0.654 | 0.717 | — | INFORMATIONAL |
| overtime punt share | 0.500 | 0.311 | — | INFORMATIONAL |

### Ledger coherence

Zero-tolerance counts from `runtime.play_detail.check_ledger` (15 original and 17 kernel 2013.7 spot and label classes). Games checked: 13. The kick-row and label classes need the full snap ledger.

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
| kick spot mismatch | — | not measurable |
| fg distance offset | 0 | WITHIN |
| category impossible at start | 0 | WITHIN |
| late terminal state mismatch | 0 | WITHIN |
| fourth down state missing | 0 | WITHIN |
| chain counter mismatch | 0 | WITHIN |
| label type mismatch | — | not measurable |
| label carrier mismatch | — | not measurable |
| label target mismatch | — | not measurable |
| scramble with designed label | — | not measurable |
| kneel spike mislabelled | — | not measurable |
