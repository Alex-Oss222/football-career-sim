# 2013 statistical band audit

**Version:** `2013-W03-BAND-AUDIT`
**Through:** Week 3.

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

**Team-games audited:** 0.

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

### Ledger coherence

Zero-tolerance counts from `runtime.play_detail.check_ledger` over every receipt's drives summary plus the full snap ledgers. Games checked: 0.

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
