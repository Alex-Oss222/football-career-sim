# 2013 statistical band audit

**Version:** `2013-W08-BAND-AUDIT`
**Through:** Week 8.

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

## Kernel 2013.7 cohort (after Week 8; no game closed yet)

**Team-games audited:** 0. Carry shares exclude kneels, as in the 2012 baseline.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| QB1 share of team pass attempts | — | 0.978 | ±0.050 | INSUFFICIENT SAMPLE |
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

Points: non-offensive touchdowns, their tries and two-point tries are not modelled by design (about 1.7-2.0 points per team game below the 2012 centre); the ±5.0 tolerance is deliberately not tightened.

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
