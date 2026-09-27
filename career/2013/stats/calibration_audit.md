# 2013 statistical band audit

**Version:** `2013-W05-BAND-AUDIT`
**Through:** Week 5.

League-wide receipts compared with the sourced 2012 shapes in `library/data/2012_nfl_aggregate_baseline.json`, `library/data/2012_nfl_position_usage_baseline.json` and `library/data/2012_nfl_drive_model.json`. This is a defect detector for engine code and TeamInputs. An OUTSIDE row is investigated; it never reruns, selects or edits a closed game. Receipts are split into cohorts by kernel version; grading starts at 16 team-games per cohort.

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

## Kernel 2013.6 cohort (Week 4 onward)

**Team-games audited:** 58.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| QB1 share of team pass attempts | 1.000 | 0.978 | ±0.050 | WITHIN |
| FB share of carries | 0.012 | 0.021 | ±0.050 | WITHIN |
| QB share of carries | 0.087 | 0.090 | ±0.050 | WITHIN |
| RB share of carries | 0.879 | 0.867 | ±0.050 | WITHIN |
| TE share of carries | 0.000 | 0.000 | ±0.050 | WITHIN |
| WR share of carries | 0.022 | 0.019 | ±0.050 | WITHIN |
| FB share of targets | 0.019 | 0.026 | ±0.050 | WITHIN |
| RB share of targets | 0.161 | 0.155 | ±0.050 | WITHIN |
| TE share of targets | 0.213 | 0.215 | ±0.050 | WITHIN |
| WR share of targets | 0.607 | 0.602 | ±0.050 | WITHIN |
| DB share of tackle credits | 0.377 | 0.401 | ±0.050 | WITHIN |
| DL share of tackle credits | 0.257 | 0.226 | ±0.050 | WITHIN |
| LB share of tackle credits | 0.367 | 0.353 | ±0.050 | WITHIN |
| Assisted share of tackle credits | 0.332 | 0.339 | ±0.050 | WITHIN |
| plays per team game | 64.1 | 64.2 | ±6.0 | WITHIN |
| yards per team game | 349.2 | 347.2 | ±40.0 | WITHIN |
| points per team game | 20.0 | 22.8 | ±5.0 | WITHIN |
| first downs per team game | 20.5 | 19.8 | ±3.0 | WITHIN |
| third down attempts per team game | 13.5 | 13.3 | ±2.5 | WITHIN |
| third down rate | 0.405 | 0.383 | ±0.060 | WITHIN |

Points: non-offensive touchdowns, their tries and two-point tries are not modelled by design (about 1.7-2.0 points per team game below the 2012 centre); the ±5.0 tolerance is deliberately not tightened.

### Drive model rows

Centres from the 2012 drive model (nflverse drive definition) and period totals; tolerance is three standard errors at the observed sample.

| Metric | Observed | 2012 band centre | Tolerance | Status |
|---|---:|---:|---:|---|
| FG accuracy | 0.853 | 0.839 | ±0.106 | WITHIN |
| FG accuracy <30 yd | 0.867 | 0.967 | ±0.099 | OUTSIDE |
| FG accuracy 30-39 yd | 0.938 | 0.891 | ±0.165 | WITHIN |
| FG accuracy 40-49 yd | 0.839 | 0.802 | ±0.215 | WITHIN |
| FG accuracy 50+ yd | 0.688 | 0.609 | ±0.366 | INSUFFICIENT SAMPLE |
| XP accuracy (informational; partially verified) | 0.992 | 0.994 | ±0.022 | WITHIN |
| FGA per team game | 1.879 | 1.984 | ±0.555 | WITHIN |
| FGM per team game | 1.603 | 1.664 | ±0.508 | WITHIN |
| drives per team game (nflverse definition; PFR 10.47) | 11.8 | 11.7 | ±1.347 | WITHIN |
| punts per team game (drive-ending) | 5.1 | 4.8 | ±0.865 | WITHIN |
| drive share: touchdown | 0.182 | 0.195 | ±0.045 | WITHIN |
| drive share: field goal attempt | 0.159 | 0.170 | ±0.043 | WITHIN |
| drive share: punt | 0.428 | 0.412 | ±0.056 | WITHIN |
| drive share: turnover (INT + fumble lost) | 0.127 | 0.125 | ±0.038 | WITHIN |
| drive share: downs | 0.028 | 0.033 | ±0.021 | WITHIN |
| drive share: safety | 0.004 | 0.002 | ±0.005 | WITHIN |
| drive share: clock | 0.072 | 0.063 | ±0.028 | WITHIN |
| clock-expired drives per team game | 0.845 | 0.734 | ±0.338 | WITHIN |
| offensive-drive turnovers per team game | 1.500 | 1.461 | ±0.476 | WITHIN |
| interception share of turnovers | 0.701 | 0.626 | ±0.156 | WITHIN |
| kickoffs per team game (informational; centre includes kicks not modelled: after non-offensive TDs, onside, re-kicks, after half-final scores) | 4.7 | 5.2 | ±0.899 | INFORMATIONAL |
| kick returns per team game | 2.4 | 2.6 | ±0.638 | WITHIN |

### Ledger coherence

Zero-tolerance counts from `runtime.play_detail.check_ledger` over every receipt's drives summary plus the full snap ledgers. Games checked: 29.

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
