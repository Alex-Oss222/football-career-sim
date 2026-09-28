# 2013 statistical band audit

**Version:** `2013-W17-BAND-AUDIT`
**Through:** Week 17.

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
| yards per team game | 338.3 | 347.2 | ±40.0 | WITHIN |
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
| yards per team game | 346.4 | 347.2 | ±40.0 | WITHIN |
| points per team game | 21.2 | 22.8 | ±5.0 | WITHIN |
| first downs per team game | 20.8 | 19.8 | ±3.0 | WITHIN |
| third down attempts per team game | 13.4 | 13.3 | ±2.5 | WITHIN |
| third down rate | 0.384 | 0.383 | ±0.060 | WITHIN |

Points: non-offensive touchdowns, their tries and two-point tries are not modelled by design (about 1.7-2.0 points per team game below the 2012 centre); the ±5.0 tolerance is deliberately not tightened. Yards per team game are net of sack yards, as the 2012 centre is (corrected in Entry 55; earlier audits compared gross passing yards and read about 14 yards high).

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

## Kernel 2013.7 cohort (Weeks 9-10)

**Team-games audited:** 54. Carry shares exclude kneels, as in the 2012 baseline.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| QB1 share of team pass attempts | 1.000 | 0.978 | ±0.050 | WITHIN |
| FB share of carries | 0.011 | 0.021 | ±0.050 | WITHIN |
| QB share of carries | 0.087 | 0.090 | ±0.050 | WITHIN |
| RB share of carries | 0.885 | 0.867 | ±0.050 | WITHIN |
| TE share of carries | 0.001 | 0.000 | ±0.050 | WITHIN |
| WR share of carries | 0.017 | 0.019 | ±0.050 | WITHIN |
| FB share of targets | 0.015 | 0.026 | ±0.050 | WITHIN |
| RB share of targets | 0.161 | 0.155 | ±0.050 | WITHIN |
| TE share of targets | 0.214 | 0.215 | ±0.050 | WITHIN |
| WR share of targets | 0.611 | 0.602 | ±0.050 | WITHIN |
| DB share of tackle credits | 0.391 | 0.401 | ±0.050 | WITHIN |
| DL share of tackle credits | 0.265 | 0.226 | ±0.050 | WITHIN |
| LB share of tackle credits | 0.344 | 0.353 | ±0.050 | WITHIN |
| Assisted share of tackle credits | 0.324 | 0.339 | ±0.050 | WITHIN |
| plays per team game | 65.0 | 64.2 | ±6.0 | WITHIN |
| yards per team game | 343.9 | 347.2 | ±40.0 | WITHIN |
| points per team game | 19.9 | 22.8 | ±5.0 | WITHIN |
| first downs per team game | 20.0 | 19.8 | ±3.0 | WITHIN |
| third down attempts per team game | 13.4 | 13.3 | ±2.5 | WITHIN |
| third down rate | 0.362 | 0.383 | ±0.060 | WITHIN |

Points: non-offensive touchdowns, their tries and two-point tries are not modelled by design (about 1.7-2.0 points per team game below the 2012 centre); the ±5.0 tolerance is deliberately not tightened. Yards per team game are net of sack yards, as the 2012 centre is (corrected in Entry 55; earlier audits compared gross passing yards and read about 14 yards high).

### Drive model rows

Centres from the 2012 drive model (nflverse drive definition) and period totals; tolerance is three standard errors at the observed sample.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| FG accuracy | 0.841 | 0.839 | ±0.104 | WITHIN |
| FG accuracy <30 yd | 0.917 | 0.967 | ±0.110 | INSUFFICIENT SAMPLE |
| FG accuracy 30-39 yd | 0.838 | 0.891 | ±0.154 | WITHIN |
| FG accuracy 40-49 yd | 0.884 | 0.802 | ±0.182 | WITHIN |
| FG accuracy 50+ yd | 0.444 | 0.609 | ±0.488 | INSUFFICIENT SAMPLE |
| XP accuracy (informational; partially verified) | 1.000 | 0.994 | ±0.023 | WITHIN |
| FGA per team game | 2.1 | 1.984 | ±0.575 | WITHIN |
| FGM per team game | 1.759 | 1.664 | ±0.527 | WITHIN (known detection) |
| drives per team game (nflverse definition; PFR 10.47) | 11.4 | 11.7 | ±1.396 | WITHIN |
| punts per team game (drive-ending) | 4.8 | 4.8 | ±0.896 | WITHIN (known detection) |
| drive share: touchdown | 0.182 | 0.195 | ±0.048 | WITHIN |
| drive share: field goal attempt | 0.183 | 0.170 | ±0.045 | WITHIN |
| drive share: punt | 0.421 | 0.412 | ±0.059 | WITHIN |
| drive share: turnover (INT + fumble lost) | 0.120 | 0.125 | ±0.040 | WITHIN |
| drive share: downs | 0.032 | 0.033 | ±0.022 | WITHIN |
| drive share: safety | 0.003 | 0.002 | ±0.006 | WITHIN |
| drive share: clock | 0.058 | 0.063 | ±0.029 | WITHIN (known detection) |
| clock-expired drives per team game | 0.667 | 0.734 | ±0.350 | WITHIN (known detection) |
| offensive-drive turnovers per team game | 1.370 | 1.461 | ±0.493 | WITHIN |
| interception share of turnovers | 0.662 | 0.626 | ±0.169 | WITHIN |
| kickoffs per team game (informational; centre includes kicks not modelled: after non-offensive TDs, onside, re-kicks, after half-final scores) | 4.7 | 5.2 | ±0.931 | INFORMATIONAL |
| kick returns per team game | 2.8 | 2.6 | ±0.662 | WITHIN |

Known detections (`runtime/bands.py` `KNOWN_DETECTIONS`): graded rows with a documented design cause, accepted rather than tuned. Each stays graded; OUTSIDE within 2x its tolerance is the documented detection, and beyond that it is investigated. No centre, tolerance, coefficient or pool was changed.

- punts per team game (drive-ending): the half-final redirect skews surviving interior drives short and punt-heavy (runtime/README.md, kernel 2013.6 limitations).
- FGM per team game: adopted as documented by the user's decision of September 27, 2026: the first-half half-final redirect starts first-half final possessions early, field-goal-heavy and clock-light (library/2012_field_position_model_calibration.md, acceptance).
- drive share: clock: adopted as documented by the user's decision of September 27, 2026: the first-half half-final redirect starts first-half final possessions early, field-goal-heavy and clock-light (library/2012_field_position_model_calibration.md, acceptance).
- clock-expired drives per team game: adopted as documented by the user's decision of September 27, 2026: the first-half half-final redirect starts first-half final possessions early, field-goal-heavy and clock-light (library/2012_field_position_model_calibration.md, acceptance).

### Field-position rows

Centres from the 2012 field-position model's band_centres. Rates use 3*sqrt(p(1-p)/n) and means 3*sd/sqrt(n) with the 2012 sd; a row reads INSUFFICIENT SAMPLE below 30 events. INFORMATIONAL rows are shapes, not grades.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| kickoff touchback share | 0.404 | 0.462 | ±0.095 | WITHIN |
| mean start after a non-touchback kickoff (yardline_100) | 77.5 | 77.0 | ±2.4 | WITHIN |
| mean realized punt net, LOS opp 39-30 | 26.0 | 28.0 | ±5.6 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS opp 49-40 | 33.8 | 32.9 | ±3.2 | WITHIN |
| mean realized punt net, LOS own 1-10 | 42.1 | 43.7 | ±9.6 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS own 11-20 | 44.3 | 43.3 | ±5.5 | WITHIN |
| mean realized punt net, LOS own 21-30 | 45.0 | 43.7 | ±4.5 | WITHIN |
| mean realized punt net, LOS own 31-40 | 42.9 | 42.3 | ±5.5 | WITHIN |
| mean realized punt net, LOS own 41-50 | 38.7 | 38.8 | ±3.9 | WITHIN |
| punt share of possessions ending in Q4's last 5:00 or OT, offense trailing 1-8 | 0.091 | 0.119 | ±0.292 | INSUFFICIENT SAMPLE |
| punt share of possessions ending in Q4's last 2:00 or OT, offense trailing 1-8 | 0.000 | 0.008 | ±0.089 | INSUFFICIENT SAMPLE |
| third-down attempts per punt drive | 1.181 | 1.185 | ±0.082 | WITHIN |
| sacks per dropback | 0.056 | 0.062 | ±0.016 | WITHIN |
| DB share of sack credits | 0.090 | 0.063 | ±0.069 | WITHIN |
| DL share of sack credits | 0.595 | 0.599 | ±0.140 | WITHIN |
| LB share of sack credits | 0.315 | 0.337 | ±0.135 | WITHIN |
| mean drive start, all drives (2012 all-drive centre) | 72.4 | 72.3 | — | INFORMATIONAL |
| mean drive start (2012 centre over modelled transitions) | 72.4 | 72.8 | — | INFORMATIONAL |
| start-bin share 90-99 | 0.099 | 0.096 | — | INFORMATIONAL |
| start-bin share 81-89 | 0.172 | 0.160 | — | INFORMATIONAL |
| start-bin share 80-80 | 0.227 | 0.251 | — | INFORMATIONAL |
| start-bin share 70-79 | 0.180 | 0.191 | — | INFORMATIONAL |
| start-bin share 60-69 | 0.151 | 0.123 | — | INFORMATIONAL |
| start-bin share 50-59 | 0.076 | 0.071 | — | INFORMATIONAL |
| start-bin share 40-49 | 0.037 | 0.043 | — | INFORMATIONAL |
| start-bin share 30-39 | 0.021 | 0.023 | — | INFORMATIONAL |
| start-bin share 20-29 | 0.023 | 0.021 | — | INFORMATIONAL |
| start-bin share 1-19 | 0.015 | 0.022 | — | INFORMATIONAL |
| touchdown share, start opp 49-1 | 0.271 | 0.349 | — | INFORMATIONAL |
| punt share, start opp 49-1 | 0.068 | 0.108 | — | INFORMATIONAL |
| touchdown share, start own 1-20 | 0.153 | 0.158 | — | INFORMATIONAL |
| punt share, start own 1-20 | 0.515 | 0.486 | — | INFORMATIONAL |
| touchdown share, start own 21-50 | 0.195 | 0.199 | — | INFORMATIONAL |
| punt share, start own 21-50 | 0.390 | 0.402 | — | INFORMATIONAL |
| points per drive, start 1-19 | 4.9 | 4.5 | — | INFORMATIONAL |
| points per drive, start 20-29 | 2.1 | 4.1 | — | INFORMATIONAL |
| points per drive, start 30-39 | 3.1 | 3.1 | — | INFORMATIONAL |
| points per drive, start 40-49 | 2.6 | 2.6 | — | INFORMATIONAL |
| points per drive, start 50-59 | 1.723 | 2.2 | — | INFORMATIONAL |
| points per drive, start 60-69 | 1.828 | 1.829 | — | INFORMATIONAL |
| points per drive, start 70-79 | 1.910 | 1.707 | — | INFORMATIONAL |
| points per drive, start 80-89 | 1.496 | 1.473 | — | INFORMATIONAL |
| points per drive, start 90-99 | 1.082 | 1.140 | — | INFORMATIONAL |
| QB scramble share of QB carries (label stream; nflscrapR 643/1,228) | 0.750 | 0.557 | — | INFORMATIONAL |
| fourth-down attempts per team game (drive chains) | 0.907 | 0.881 | — | INFORMATIONAL |
| fourth-down conversions per team game (drive chains) | 0.481 | 0.439 | — | INFORMATIONAL |
| kneels per team game | 0.722 | 0.717 | — | INFORMATIONAL |
| overtime punt share | 0.333 | 0.311 | — | INFORMATIONAL |

### Ledger coherence

Zero-tolerance counts from `runtime.play_detail.check_ledger` (15 original and 17 kernel 2013.7 spot and label classes). Games checked: 27. The kick-row and label classes need the full snap ledger.

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

## Kernel 2013.8 cohort (Weeks 11-12)

**Team-games audited:** 58. Carry shares exclude kneels, as in the 2012 baseline.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| QB1 share of team pass attempts | 1.000 | 0.978 | ±0.050 | WITHIN |
| FB share of carries | 0.009 | 0.021 | ±0.050 | WITHIN |
| QB share of carries | 0.094 | 0.090 | ±0.050 | WITHIN |
| RB share of carries | 0.882 | 0.867 | ±0.050 | WITHIN |
| TE share of carries | 0.001 | 0.000 | ±0.050 | WITHIN |
| WR share of carries | 0.014 | 0.019 | ±0.050 | WITHIN |
| FB share of targets | 0.016 | 0.026 | ±0.050 | WITHIN |
| RB share of targets | 0.143 | 0.155 | ±0.050 | WITHIN |
| TE share of targets | 0.222 | 0.215 | ±0.050 | WITHIN |
| WR share of targets | 0.619 | 0.602 | ±0.050 | WITHIN |
| DB share of tackle credits | 0.373 | 0.401 | ±0.050 | WITHIN |
| DL share of tackle credits | 0.256 | 0.226 | ±0.050 | WITHIN |
| LB share of tackle credits | 0.371 | 0.353 | ±0.050 | WITHIN |
| Assisted share of tackle credits | 0.314 | 0.339 | ±0.050 | WITHIN |
| plays per team game | 64.1 | 64.2 | ±6.0 | WITHIN |
| yards per team game | 370.7 | 347.2 | ±40.0 | WITHIN |
| points per team game | 23.3 | 22.8 | ±5.0 | WITHIN |
| first downs per team game | 20.7 | 19.8 | ±3.0 | WITHIN |
| third down attempts per team game | 13.5 | 13.3 | ±2.5 | WITHIN |
| third down rate | 0.421 | 0.383 | ±0.060 | WITHIN |

Points: non-offensive touchdowns, their tries and two-point tries are not modelled by design (about 1.7-2.0 points per team game below the 2012 centre); the ±5.0 tolerance is deliberately not tightened. Yards per team game are net of sack yards, as the 2012 centre is (corrected in Entry 55; earlier audits compared gross passing yards and read about 14 yards high).

### Drive model rows

Centres from the 2012 drive model (nflverse drive definition) and period totals; tolerance is three standard errors at the observed sample.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| FG accuracy | 0.815 | 0.839 | ±0.101 | WITHIN |
| FG accuracy <30 yd | 0.968 | 0.967 | ±0.097 | WITHIN |
| FG accuracy 30-39 yd | 0.838 | 0.891 | ±0.154 | WITHIN |
| FG accuracy 40-49 yd | 0.763 | 0.802 | ±0.194 | WITHIN |
| FG accuracy 50+ yd | 0.538 | 0.609 | ±0.406 | INSUFFICIENT SAMPLE |
| XP accuracy (informational; partially verified) | 1.000 | 0.994 | ±0.020 | WITHIN |
| FGA per team game | 2.1 | 1.984 | ±0.555 | WITHIN |
| FGM per team game | 1.672 | 1.664 | ±0.508 | WITHIN (known detection) |
| drives per team game (nflverse definition; PFR 10.47) | 11.4 | 11.7 | ±1.347 | WITHIN |
| punts per team game (drive-ending) | 4.5 | 4.8 | ±0.865 | WITHIN (known detection) |
| drive share: touchdown | 0.227 | 0.195 | ±0.046 | WITHIN |
| drive share: field goal attempt | 0.179 | 0.170 | ±0.044 | WITHIN |
| drive share: punt | 0.395 | 0.412 | ±0.057 | WITHIN |
| drive share: turnover (INT + fumble lost) | 0.116 | 0.125 | ±0.039 | WITHIN |
| drive share: downs | 0.026 | 0.033 | ±0.021 | WITHIN |
| drive share: safety | 0.002 | 0.002 | ±0.005 | WITHIN |
| drive share: clock | 0.056 | 0.063 | ±0.028 | WITHIN (known detection) |
| clock-expired drives per team game | 0.638 | 0.734 | ±0.338 | WITHIN (known detection) |
| offensive-drive turnovers per team game | 1.328 | 1.461 | ±0.476 | WITHIN |
| interception share of turnovers | 0.714 | 0.626 | ±0.165 | WITHIN |
| kickoffs per team game (informational; centre includes kicks not modelled: after non-offensive TDs, onside, re-kicks, after half-final scores) | 5.1 | 5.2 | ±0.899 | INFORMATIONAL |
| kick returns per team game | 2.6 | 2.6 | ±0.638 | WITHIN |

Known detections (`runtime/bands.py` `KNOWN_DETECTIONS`): graded rows with a documented design cause, accepted rather than tuned. Each stays graded; OUTSIDE within 2x its tolerance is the documented detection, and beyond that it is investigated. No centre, tolerance, coefficient or pool was changed.

- punts per team game (drive-ending): the half-final redirect skews surviving interior drives short and punt-heavy (runtime/README.md, kernel 2013.6 limitations).
- FGM per team game: adopted as documented by the user's decision of September 27, 2026: the first-half half-final redirect starts first-half final possessions early, field-goal-heavy and clock-light (library/2012_field_position_model_calibration.md, acceptance).
- drive share: clock: adopted as documented by the user's decision of September 27, 2026: the first-half half-final redirect starts first-half final possessions early, field-goal-heavy and clock-light (library/2012_field_position_model_calibration.md, acceptance).
- clock-expired drives per team game: adopted as documented by the user's decision of September 27, 2026: the first-half half-final redirect starts first-half final possessions early, field-goal-heavy and clock-light (library/2012_field_position_model_calibration.md, acceptance).

### Field-position rows

Centres from the 2012 field-position model's band_centres. Rates use 3*sqrt(p(1-p)/n) and means 3*sd/sqrt(n) with the 2012 sd; a row reads INSUFFICIENT SAMPLE below 30 events. INFORMATIONAL rows are shapes, not grades.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| kickoff touchback share | 0.481 | 0.462 | ±0.087 | WITHIN |
| mean start after a non-touchback kickoff (yardline_100) | 76.7 | 77.0 | ±2.4 | WITHIN |
| mean realized punt net, LOS opp 39-30 | 32.8 | 28.0 | ±8.7 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS opp 49-40 | 32.8 | 32.9 | ±3.4 | WITHIN |
| mean realized punt net, LOS own 1-10 | 49.0 | 43.7 | ±14.0 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS own 11-20 | 44.1 | 43.3 | ±5.9 | WITHIN |
| mean realized punt net, LOS own 21-30 | 44.3 | 43.7 | ±4.2 | WITHIN |
| mean realized punt net, LOS own 31-40 | 41.5 | 42.3 | ±5.1 | WITHIN |
| mean realized punt net, LOS own 41-50 | 39.5 | 38.8 | ±3.5 | WITHIN |
| punt share of possessions ending in Q4's last 5:00 or OT, offense trailing 1-8 | 0.125 | 0.119 | ±0.242 | INSUFFICIENT SAMPLE |
| punt share of possessions ending in Q4's last 2:00 or OT, offense trailing 1-8 | 0.000 | 0.008 | ±0.077 | INSUFFICIENT SAMPLE |
| third-down attempts per punt drive | 1.206 | 1.185 | ±0.082 | WITHIN |
| sacks per dropback | 0.063 | 0.062 | ±0.016 | WITHIN |
| DB share of sack credits | 0.074 | 0.063 | ±0.063 | WITHIN |
| DL share of sack credits | 0.578 | 0.599 | ±0.127 | WITHIN |
| LB share of sack credits | 0.348 | 0.337 | ±0.122 | WITHIN |
| mean drive start, all drives (2012 all-drive centre) | 72.8 | 72.3 | — | INFORMATIONAL |
| mean drive start (2012 centre over modelled transitions) | 72.8 | 72.8 | — | INFORMATIONAL |
| start-bin share 90-99 | 0.092 | 0.096 | — | INFORMATIONAL |
| start-bin share 81-89 | 0.158 | 0.160 | — | INFORMATIONAL |
| start-bin share 80-80 | 0.286 | 0.251 | — | INFORMATIONAL |
| start-bin share 70-79 | 0.193 | 0.191 | — | INFORMATIONAL |
| start-bin share 60-69 | 0.108 | 0.123 | — | INFORMATIONAL |
| start-bin share 50-59 | 0.054 | 0.071 | — | INFORMATIONAL |
| start-bin share 40-49 | 0.039 | 0.043 | — | INFORMATIONAL |
| start-bin share 30-39 | 0.027 | 0.023 | — | INFORMATIONAL |
| start-bin share 20-29 | 0.021 | 0.021 | — | INFORMATIONAL |
| start-bin share 1-19 | 0.021 | 0.022 | — | INFORMATIONAL |
| touchdown share, start opp 49-1 | 0.472 | 0.349 | — | INFORMATIONAL |
| punt share, start opp 49-1 | 0.056 | 0.108 | — | INFORMATIONAL |
| touchdown share, start own 1-20 | 0.157 | 0.158 | — | INFORMATIONAL |
| punt share, start own 1-20 | 0.444 | 0.486 | — | INFORMATIONAL |
| touchdown share, start own 21-50 | 0.258 | 0.199 | — | INFORMATIONAL |
| punt share, start own 21-50 | 0.424 | 0.402 | — | INFORMATIONAL |
| points per drive, start 1-19 | 4.4 | 4.5 | — | INFORMATIONAL |
| points per drive, start 20-29 | 5.6 | 4.1 | — | INFORMATIONAL |
| points per drive, start 30-39 | 4.3 | 3.1 | — | INFORMATIONAL |
| points per drive, start 40-49 | 2.8 | 2.6 | — | INFORMATIONAL |
| points per drive, start 50-59 | 3.4 | 2.2 | — | INFORMATIONAL |
| points per drive, start 60-69 | 1.833 | 1.829 | — | INFORMATIONAL |
| points per drive, start 70-79 | 2.0 | 1.707 | — | INFORMATIONAL |
| points per drive, start 80-89 | 1.553 | 1.473 | — | INFORMATIONAL |
| points per drive, start 90-99 | 1.361 | 1.140 | — | INFORMATIONAL |
| QB scramble share of QB carries (label stream; nflscrapR 643/1,228) | 0.286 | 0.557 | — | INFORMATIONAL |
| fourth-down attempts per team game (drive chains) | 0.621 | 0.881 | — | INFORMATIONAL |
| fourth-down conversions per team game (drive chains) | 0.310 | 0.439 | — | INFORMATIONAL |
| kneels per team game | 0.672 | 0.717 | — | INFORMATIONAL |
| overtime punt share | 0.125 | 0.311 | — | INFORMATIONAL |

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

## Kernel 2013.9 cohort (Week 13)

**Team-games audited:** 32. Carry shares exclude kneels, as in the 2012 baseline.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| QB1 share of team pass attempts | 1.000 | 0.978 | ±0.050 | WITHIN |
| FB share of carries | 0.016 | 0.021 | ±0.050 | WITHIN |
| QB share of carries | 0.086 | 0.090 | ±0.050 | WITHIN |
| RB share of carries | 0.878 | 0.867 | ±0.050 | WITHIN |
| TE share of carries | 0.000 | 0.000 | ±0.050 | WITHIN |
| WR share of carries | 0.020 | 0.019 | ±0.050 | WITHIN |
| FB share of targets | 0.018 | 0.026 | ±0.050 | WITHIN |
| RB share of targets | 0.163 | 0.155 | ±0.050 | WITHIN |
| TE share of targets | 0.218 | 0.215 | ±0.050 | WITHIN |
| WR share of targets | 0.601 | 0.602 | ±0.050 | WITHIN |
| DB share of tackle credits | 0.385 | 0.401 | ±0.050 | WITHIN |
| DL share of tackle credits | 0.239 | 0.226 | ±0.050 | WITHIN |
| LB share of tackle credits | 0.376 | 0.353 | ±0.050 | WITHIN |
| Assisted share of tackle credits | 0.336 | 0.339 | ±0.050 | WITHIN |
| plays per team game | 68.8 | 64.2 | ±6.0 | WITHIN |
| yards per team game | 376.9 | 347.2 | ±40.0 | WITHIN |
| points per team game | 21.3 | 22.8 | ±5.0 | WITHIN |
| first downs per team game | 20.6 | 19.8 | ±3.0 | WITHIN |
| third down attempts per team game | 15.1 | 13.3 | ±2.5 | WITHIN |
| third down rate | 0.362 | 0.383 | ±0.060 | WITHIN |

Points: non-offensive touchdowns, their tries and two-point tries are not modelled by design (about 1.7-2.0 points per team game below the 2012 centre); the ±5.0 tolerance is deliberately not tightened. Yards per team game are net of sack yards, as the 2012 centre is (corrected in Entry 55; earlier audits compared gross passing yards and read about 14 yards high).

### Drive model rows

Centres from the 2012 drive model (nflverse drive definition) and period totals; tolerance is three standard errors at the observed sample.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| FG accuracy | 0.852 | 0.839 | ±0.123 | WITHIN |
| FG accuracy <30 yd | 0.947 | 0.967 | ±0.124 | INSUFFICIENT SAMPLE |
| FG accuracy 30-39 yd | 0.966 | 0.891 | ±0.174 | INSUFFICIENT SAMPLE |
| FG accuracy 40-49 yd | 0.750 | 0.802 | ±0.267 | INSUFFICIENT SAMPLE |
| FG accuracy 50+ yd | 0.615 | 0.609 | ±0.406 | INSUFFICIENT SAMPLE |
| XP accuracy (informational; partially verified) | 0.985 | 0.994 | ±0.029 | WITHIN |
| FGA per team game | 2.5 | 1.984 | ±0.747 | WITHIN |
| FGM per team game | 2.2 | 1.664 | ±0.684 | WITHIN (known detection) |
| drives per team game (nflverse definition; PFR 10.47) | 12.7 | 11.7 | ±1.813 | WITHIN |
| punts per team game (drive-ending) | 5.8 | 4.8 | ±1.164 | WITHIN (known detection) |
| drive share: touchdown | 0.168 | 0.195 | ±0.059 | WITHIN |
| drive share: field goal attempt | 0.200 | 0.170 | ±0.056 | WITHIN |
| drive share: punt | 0.459 | 0.412 | ±0.073 | WITHIN |
| drive share: turnover (INT + fumble lost) | 0.111 | 0.125 | ±0.049 | WITHIN |
| drive share: downs | 0.015 | 0.033 | ±0.027 | WITHIN |
| drive share: safety | 0.000 | 0.002 | ±0.007 | WITHIN |
| drive share: clock | 0.047 | 0.063 | ±0.036 | WITHIN (known detection) |
| clock-expired drives per team game | 0.594 | 0.734 | ±0.454 | WITHIN (known detection) |
| offensive-drive turnovers per team game | 1.406 | 1.461 | ±0.641 | WITHIN |
| interception share of turnovers | 0.667 | 0.626 | ±0.216 | WITHIN |
| kickoffs per team game (informational; centre includes kicks not modelled: after non-offensive TDs, onside, re-kicks, after half-final scores) | 5.0 | 5.2 | ±1.210 | INFORMATIONAL |
| kick returns per team game | 2.8 | 2.6 | ±0.860 | WITHIN |

Known detections (`runtime/bands.py` `KNOWN_DETECTIONS`): graded rows with a documented design cause, accepted rather than tuned. Each stays graded; OUTSIDE within 2x its tolerance is the documented detection, and beyond that it is investigated. No centre, tolerance, coefficient or pool was changed.

- punts per team game (drive-ending): the half-final redirect skews surviving interior drives short and punt-heavy (runtime/README.md, kernel 2013.6 limitations).
- FGM per team game: adopted as documented by the user's decision of September 27, 2026: the first-half half-final redirect starts first-half final possessions early, field-goal-heavy and clock-light (library/2012_field_position_model_calibration.md, acceptance).
- drive share: clock: adopted as documented by the user's decision of September 27, 2026: the first-half half-final redirect starts first-half final possessions early, field-goal-heavy and clock-light (library/2012_field_position_model_calibration.md, acceptance).
- clock-expired drives per team game: adopted as documented by the user's decision of September 27, 2026: the first-half half-final redirect starts first-half final possessions early, field-goal-heavy and clock-light (library/2012_field_position_model_calibration.md, acceptance).

### Field-position rows

Centres from the 2012 field-position model's band_centres. Rates use 3*sqrt(p(1-p)/n) and means 3*sd/sqrt(n) with the 2012 sd; a row reads INSUFFICIENT SAMPLE below 30 events. INFORMATIONAL rows are shapes, not grades.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| kickoff touchback share | 0.447 | 0.462 | ±0.118 | WITHIN |
| mean start after a non-touchback kickoff (yardline_100) | 79.2 | 77.0 | ±3.1 | WITHIN |
| mean realized punt net, LOS opp 39-30 | 27.5 | 28.0 | ±13.8 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS opp 49-40 | 33.1 | 32.9 | ±3.8 | WITHIN |
| mean realized punt net, LOS own 1-10 | 48.9 | 43.7 | ±14.0 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS own 11-20 | 44.1 | 43.3 | ±6.9 | WITHIN |
| mean realized punt net, LOS own 21-30 | 40.9 | 43.7 | ±5.1 | WITHIN |
| mean realized punt net, LOS own 31-40 | 41.3 | 42.3 | ±5.7 | WITHIN |
| mean realized punt net, LOS own 41-50 | 37.3 | 38.8 | ±4.7 | INSUFFICIENT SAMPLE |
| punt share of possessions ending in Q4's last 5:00 or OT, offense trailing 1-8 | 0.167 | 0.119 | ±0.198 | INSUFFICIENT SAMPLE |
| punt share of possessions ending in Q4's last 2:00 or OT, offense trailing 1-8 | 0.000 | 0.008 | ±0.071 | INSUFFICIENT SAMPLE |
| third-down attempts per punt drive | 1.188 | 1.185 | ±0.097 | WITHIN |
| sacks per dropback | 0.057 | 0.062 | ±0.020 | WITHIN |
| DB share of sack credits | 0.078 | 0.063 | ±0.083 | WITHIN |
| DL share of sack credits | 0.545 | 0.599 | ±0.168 | WITHIN |
| LB share of sack credits | 0.377 | 0.337 | ±0.162 | WITHIN |
| mean drive start, all drives (2012 all-drive centre) | 73.2 | 72.3 | — | INFORMATIONAL |
| mean drive start (2012 centre over modelled transitions) | 73.2 | 72.8 | — | INFORMATIONAL |
| start-bin share 90-99 | 0.096 | 0.096 | — | INFORMATIONAL |
| start-bin share 81-89 | 0.193 | 0.160 | — | INFORMATIONAL |
| start-bin share 80-80 | 0.222 | 0.251 | — | INFORMATIONAL |
| start-bin share 70-79 | 0.175 | 0.191 | — | INFORMATIONAL |
| start-bin share 60-69 | 0.148 | 0.123 | — | INFORMATIONAL |
| start-bin share 50-59 | 0.089 | 0.071 | — | INFORMATIONAL |
| start-bin share 40-49 | 0.020 | 0.043 | — | INFORMATIONAL |
| start-bin share 30-39 | 0.015 | 0.023 | — | INFORMATIONAL |
| start-bin share 20-29 | 0.025 | 0.021 | — | INFORMATIONAL |
| start-bin share 1-19 | 0.017 | 0.022 | — | INFORMATIONAL |
| touchdown share, start opp 49-1 | 0.355 | 0.349 | — | INFORMATIONAL |
| punt share, start opp 49-1 | 0.097 | 0.108 | — | INFORMATIONAL |
| touchdown share, start own 1-20 | 0.150 | 0.158 | — | INFORMATIONAL |
| punt share, start own 1-20 | 0.556 | 0.486 | — | INFORMATIONAL |
| touchdown share, start own 21-50 | 0.156 | 0.199 | — | INFORMATIONAL |
| punt share, start own 21-50 | 0.407 | 0.402 | — | INFORMATIONAL |
| points per drive, start 1-19 | 4.9 | 4.5 | — | INFORMATIONAL |
| points per drive, start 20-29 | 4.0 | 4.1 | — | INFORMATIONAL |
| points per drive, start 30-39 | 2.7 | 3.1 | — | INFORMATIONAL |
| points per drive, start 40-49 | 2.5 | 2.6 | — | INFORMATIONAL |
| points per drive, start 50-59 | 2.3 | 2.2 | — | INFORMATIONAL |
| points per drive, start 60-69 | 1.233 | 1.829 | — | INFORMATIONAL |
| points per drive, start 70-79 | 1.901 | 1.707 | — | INFORMATIONAL |
| points per drive, start 80-89 | 1.333 | 1.473 | — | INFORMATIONAL |
| points per drive, start 90-99 | 1.410 | 1.140 | — | INFORMATIONAL |
| QB scramble share of QB carries (label stream; nflscrapR 643/1,228) | — | 0.557 | — | INSUFFICIENT SAMPLE |
| fourth-down attempts per team game (drive chains) | 0.750 | 0.881 | — | INFORMATIONAL |
| fourth-down conversions per team game (drive chains) | 0.500 | 0.439 | — | INFORMATIONAL |
| kneels per team game | 0.406 | 0.717 | — | INFORMATIONAL |
| overtime punt share | 0.471 | 0.311 | — | INFORMATIONAL |

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

## Kernel 2013.10 cohort (Weeks 14-17)

**Team-games audited:** 128. Carry shares exclude kneels, as in the 2012 baseline.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| QB1 share of team pass attempts | 1.000 | 0.978 | ±0.050 | WITHIN |
| FB share of carries | 0.012 | 0.021 | ±0.050 | WITHIN |
| QB share of carries | 0.093 | 0.090 | ±0.050 | WITHIN |
| RB share of carries | 0.875 | 0.867 | ±0.050 | WITHIN |
| TE share of carries | 0.000 | 0.000 | ±0.050 | WITHIN |
| WR share of carries | 0.019 | 0.019 | ±0.050 | WITHIN |
| FB share of targets | 0.016 | 0.026 | ±0.050 | WITHIN |
| RB share of targets | 0.159 | 0.155 | ±0.050 | WITHIN |
| TE share of targets | 0.217 | 0.215 | ±0.050 | WITHIN |
| WR share of targets | 0.607 | 0.602 | ±0.050 | WITHIN |
| DB share of tackle credits | 0.388 | 0.401 | ±0.050 | WITHIN |
| DL share of tackle credits | 0.250 | 0.226 | ±0.050 | WITHIN |
| LB share of tackle credits | 0.362 | 0.353 | ±0.050 | WITHIN |
| Assisted share of tackle credits | 0.336 | 0.339 | ±0.050 | WITHIN |
| plays per team game | 66.0 | 64.2 | ±6.0 | WITHIN |
| yards per team game | 375.8 | 347.2 | ±40.0 | WITHIN |
| points per team game | 22.8 | 22.8 | ±5.0 | WITHIN |
| first downs per team game | 21.3 | 19.8 | ±3.0 | WITHIN |
| third down attempts per team game | 13.4 | 13.3 | ±2.5 | WITHIN |
| third down rate | 0.396 | 0.383 | ±0.060 | WITHIN |

Points: non-offensive touchdowns, their tries and two-point tries are not modelled by design (about 1.7-2.0 points per team game below the 2012 centre); the ±5.0 tolerance is deliberately not tightened. Yards per team game are net of sack yards, as the 2012 centre is (corrected in Entry 55; earlier audits compared gross passing yards and read about 14 yards high).

### Drive model rows

Centres from the 2012 drive model (nflverse drive definition) and period totals; tolerance is three standard errors at the observed sample.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| FG accuracy | 0.831 | 0.839 | ±0.065 | WITHIN |
| FG accuracy <30 yd | 0.986 | 0.967 | ±0.064 | WITHIN |
| FG accuracy 30-39 yd | 0.906 | 0.891 | ±0.095 | WITHIN |
| FG accuracy 40-49 yd | 0.671 | 0.802 | ±0.140 | WITHIN |
| FG accuracy 50+ yd | 0.689 | 0.609 | ±0.218 | WITHIN |
| XP accuracy (informational; partially verified) | 0.997 | 0.994 | ±0.014 | WITHIN |
| FGA per team game | 2.2 | 1.984 | ±0.374 | WITHIN |
| FGM per team game | 1.844 | 1.664 | ±0.342 | WITHIN (known detection) |
| drives per team game (nflverse definition; PFR 10.47) | 11.7 | 11.7 | ±0.907 | WITHIN |
| punts per team game (drive-ending) | 4.6 | 4.8 | ±0.582 | WITHIN (known detection) |
| drive share: touchdown | 0.211 | 0.195 | ±0.031 | WITHIN |
| drive share: field goal attempt | 0.190 | 0.170 | ±0.029 | WITHIN |
| drive share: punt | 0.391 | 0.412 | ±0.038 | WITHIN |
| drive share: turnover (INT + fumble lost) | 0.126 | 0.125 | ±0.026 | WITHIN |
| drive share: downs | 0.032 | 0.033 | ±0.014 | WITHIN |
| drive share: safety | 0.002 | 0.002 | ±0.004 | WITHIN |
| drive share: clock | 0.048 | 0.063 | ±0.019 | WITHIN (known detection) |
| clock-expired drives per team game | 0.562 | 0.734 | ±0.227 | WITHIN (known detection) |
| offensive-drive turnovers per team game | 1.477 | 1.461 | ±0.321 | WITHIN |
| interception share of turnovers | 0.614 | 0.626 | ±0.106 | WITHIN |
| kickoffs per team game (informational; centre includes kicks not modelled: after non-offensive TDs, onside, re-kicks, after half-final scores) | 5.0 | 5.2 | ±0.605 | INFORMATIONAL |
| kick returns per team game | 2.8 | 2.6 | ±0.430 | WITHIN |

Known detections (`runtime/bands.py` `KNOWN_DETECTIONS`): graded rows with a documented design cause, accepted rather than tuned. Each stays graded; OUTSIDE within 2x its tolerance is the documented detection, and beyond that it is investigated. No centre, tolerance, coefficient or pool was changed.

- punts per team game (drive-ending): the half-final redirect skews surviving interior drives short and punt-heavy (runtime/README.md, kernel 2013.6 limitations).
- FGM per team game: adopted as documented by the user's decision of September 27, 2026: the first-half half-final redirect starts first-half final possessions early, field-goal-heavy and clock-light (library/2012_field_position_model_calibration.md, acceptance).
- drive share: clock: adopted as documented by the user's decision of September 27, 2026: the first-half half-final redirect starts first-half final possessions early, field-goal-heavy and clock-light (library/2012_field_position_model_calibration.md, acceptance).
- clock-expired drives per team game: adopted as documented by the user's decision of September 27, 2026: the first-half half-final redirect starts first-half final possessions early, field-goal-heavy and clock-light (library/2012_field_position_model_calibration.md, acceptance).

### Field-position rows

Centres from the 2012 field-position model's band_centres. Rates use 3*sqrt(p(1-p)/n) and means 3*sd/sqrt(n) with the 2012 sd; a row reads INSUFFICIENT SAMPLE below 30 events. INFORMATIONAL rows are shapes, not grades.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| kickoff touchback share | 0.445 | 0.462 | ±0.059 | WITHIN |
| mean start after a non-touchback kickoff (yardline_100) | 77.1 | 77.0 | ±1.553 | WITHIN |
| mean realized punt net, LOS opp 39-30 | 32.9 | 28.0 | ±5.2 | INSUFFICIENT SAMPLE |
| mean realized punt net, LOS opp 49-40 | 33.4 | 32.9 | ±2.0 | WITHIN |
| mean realized punt net, LOS own 1-10 | 40.0 | 43.7 | ±6.6 | WITHIN |
| mean realized punt net, LOS own 11-20 | 41.5 | 43.3 | ±4.3 | WITHIN |
| mean realized punt net, LOS own 21-30 | 42.9 | 43.7 | ±2.9 | WITHIN |
| mean realized punt net, LOS own 31-40 | 41.9 | 42.3 | ±3.5 | WITHIN |
| mean realized punt net, LOS own 41-50 | 37.4 | 38.8 | ±2.5 | WITHIN |
| punt share of possessions ending in Q4's last 5:00 or OT, offense trailing 1-8 | 0.065 | 0.119 | ±0.143 | WITHIN |
| punt share of possessions ending in Q4's last 2:00 or OT, offense trailing 1-8 | 0.000 | 0.008 | ±0.046 | WITHIN |
| third-down attempts per punt drive | 1.185 | 1.185 | ±0.055 | WITHIN |
| sacks per dropback | 0.054 | 0.062 | ±0.010 | WITHIN |
| DB share of sack credits | 0.061 | 0.063 | ±0.045 | WITHIN |
| DL share of sack credits | 0.591 | 0.599 | ±0.090 | WITHIN |
| LB share of sack credits | 0.348 | 0.337 | ±0.087 | WITHIN |
| mean drive start, all drives (2012 all-drive centre) | 72.5 | 72.3 | — | INFORMATIONAL |
| mean drive start (2012 centre over modelled transitions) | 72.5 | 72.8 | — | INFORMATIONAL |
| start-bin share 90-99 | 0.112 | 0.096 | — | INFORMATIONAL |
| start-bin share 81-89 | 0.148 | 0.160 | — | INFORMATIONAL |
| start-bin share 80-80 | 0.244 | 0.251 | — | INFORMATIONAL |
| start-bin share 70-79 | 0.202 | 0.191 | — | INFORMATIONAL |
| start-bin share 60-69 | 0.120 | 0.123 | — | INFORMATIONAL |
| start-bin share 50-59 | 0.067 | 0.071 | — | INFORMATIONAL |
| start-bin share 40-49 | 0.035 | 0.043 | — | INFORMATIONAL |
| start-bin share 30-39 | 0.029 | 0.023 | — | INFORMATIONAL |
| start-bin share 20-29 | 0.015 | 0.021 | — | INFORMATIONAL |
| start-bin share 1-19 | 0.026 | 0.022 | — | INFORMATIONAL |
| touchdown share, start opp 49-1 | 0.367 | 0.349 | — | INFORMATIONAL |
| punt share, start opp 49-1 | 0.089 | 0.108 | — | INFORMATIONAL |
| touchdown share, start own 1-20 | 0.187 | 0.158 | — | INFORMATIONAL |
| punt share, start own 1-20 | 0.440 | 0.486 | — | INFORMATIONAL |
| touchdown share, start own 21-50 | 0.200 | 0.199 | — | INFORMATIONAL |
| punt share, start own 21-50 | 0.409 | 0.402 | — | INFORMATIONAL |
| points per drive, start 1-19 | 5.0 | 4.5 | — | INFORMATIONAL |
| points per drive, start 20-29 | 4.0 | 4.1 | — | INFORMATIONAL |
| points per drive, start 30-39 | 3.1 | 3.1 | — | INFORMATIONAL |
| points per drive, start 40-49 | 2.7 | 2.6 | — | INFORMATIONAL |
| points per drive, start 50-59 | 2.1 | 2.2 | — | INFORMATIONAL |
| points per drive, start 60-69 | 1.944 | 1.829 | — | INFORMATIONAL |
| points per drive, start 70-79 | 1.914 | 1.707 | — | INFORMATIONAL |
| points per drive, start 80-89 | 1.563 | 1.473 | — | INFORMATIONAL |
| points per drive, start 90-99 | 1.749 | 1.140 | — | INFORMATIONAL |
| QB scramble share of QB carries (label stream; nflscrapR 643/1,228) | 0.556 | 0.557 | — | INFORMATIONAL |
| fourth-down attempts per team game (drive chains) | 0.875 | 0.881 | — | INFORMATIONAL |
| fourth-down conversions per team game (drive chains) | 0.477 | 0.439 | — | INFORMATIONAL |
| kneels per team game | 0.523 | 0.717 | — | INFORMATIONAL |
| overtime punt share | 0.154 | 0.311 | — | INFORMATIONAL |

### Ledger coherence

Zero-tolerance counts from `runtime.play_detail.check_ledger` (15 original and 17 kernel 2013.7 spot and label classes). Games checked: 64. The kick-row and label classes need the full snap ledger.

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
