# 2012 NFL field-position model for kernel 2013.7

**Research date:** September 27, 2026. **Football information window:** completed 2012 regular season only (256 games, 512 team-games). **Artifact:** `library/data/2012_nfl_field_position_model.json` (schema `2012-nfl-field-position-model-v1`), built by `scripts/research/build_2012_field_position_model.py`. **Status:** reconciled to the stored 2012 totals and to the kernel 2013.6 drive model; second pass passed with documented deviations; Pro Football Reference cross-check unresolved. No 2013 or later data is read, and the artifact holds no team or game identifiers.

The kernel 2013.6 artifact (`library/data/2012_nfl_drive_model.json`, [its calibration](2012_drive_model_calibration.md)) is unchanged and still byte-reproducible; kernel 2013.7 keeps using its category list, edge shift, clock scale, field-goal accuracy by distance and kick rates.

## Sources

| Pass | File | SHA-256 (pinned in the builder) |
|---|---|---|
| Primary | nflverse `play_by_play_2012.csv.gz` ([release](https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2012.csv.gz)), `season_type == REG` | `ff1cda2e26610ef8720324e442d1e5ebc24918e08fd1d2933590b7b91a7068cd` |
| Second | nflscrapR `reg_pbp_2012.csv` ([file](https://raw.githubusercontent.com/ryurko/nflscrapR-data/master/play_by_play_data/regular_season/reg_pbp_2012.csv)) | `9129396fc41597f9f44ab14d4d0fca890a3c56fea686b0b7dc92885aaedd0f98` |
| Position map (scramble denominator only) | nflverse `roster_2012.csv` ([release](https://github.com/nflverse/nflverse-data/releases/download/rosters/roster_2012.csv)) | `90628fcdadd9f2dde083bc77d41139cedc9fefd1fcc09f2ce8675823de23291b` |

**Verification labels.** nflverse and nflscrapR both derive from the NFL Game Statistics and Information System (GSIS) feed. The second pass therefore verifies the file parse, the drive grouping and the classifier; it is **not an independent observation of the 2012 season**. Every figure below is labelled either *two-file (same GSIS feed)* or *single-file*. The inputs are large and are not committed. `python scripts/research/build_2012_field_position_model.py --check` rebuilds the artifact (about 9 seconds) and exits non-zero unless it is reproduced byte-for-byte; `tests/test_field_position_model.py` runs that check when the sources are present and skips it otherwise.

## Method

**Drives.** The builder imports the kernel 2013.6 reader, offensive-snap test and result classifier (`rows`, `is_off`, `classify` from `build_2012_drive_model.py`) and repeats its drive grouping, so the 5,984 drives and their eight categories are exactly the 2013.6 drives; the build fails unless the category counts equal the committed 2013.6 artifact's.

**Per-drive record.** For each drive the builder keeps:

- `start`: the yard line (`yardline_100`) of the first non-kick snap. This corrects 11 drives whose 2013.6 start was a nullified kickoff row.
- `end`: touchdown 0; safety 100; punt or field goal: the terminal line of scrimmage; otherwise line of scrimmage minus yards gained on the last snap. `net0 = start - end`.
- `seconds`: nflverse drive time of possession, blank values imputed as plays x the category's pace (the 2013.6 rule, so the 2013.6 `clock_scale` applies unchanged; single-file).
- `t0` (seconds left in the half, or in the overtime period, at the first snap), `score_diff` at the first snap from the rebuilt score, `final` (last offensive drive of the half or period).
- `term_bucket` from the terminal snap's fourth-quarter clock (`le120`, `121-300`, `301-600`, `gt600` for earlier snaps, `OT`), and `term_down`/`term_ydstogo` for punt, field-goal and downs drives.
- `chains`: scrimmage first downs, penalty first downs, third-down attempts and conversions, fourth-down attempts and conversions, counted over all of the offense's rows in the drive (including `no_play` penalty rows).
- The drive's real snap counts: `runs` (non-kneel, scrambles included), `attempts` (non-spike pass attempts, interceptions included), `sacks`, `kneel_yards` (one entry per kneel) and `spikes`, plus `td_kind` (pass or rush, from the scoring snap).
- Field goals: real kick distance, made, blocked. Safeties: terminal kind (sack or run) and terminal line of scrimmage.

**Score rebuild.** The running score is rebuilt from each file's own scoring rows (touchdown 6 to the scoring club, good extra point 1, two-point success 2, made field goal 3, safety 2 to the defence), with an imputed made try after an offensive or return touchdown that has no try row. nflscrapR's `score_differential` is not used: it is corrupted by 115 missing extra-point rows.

**Transitions.** From the rows between two drives the builder classifies how each possession began (research start-type rules) and keeps the real transition records. Enforcement `e` is the residual that makes each record's published identity exact:

- Kickoffs: own-35, non-onside kicks followed by the receiving club's drive, `[touchback, next_start, kick_yards, return_yards, e, outcome]`; next = 35 + kick - return + e, or 80 + e on a touchback.
- Safety free kicks: the same fields from the 20 (13 records, all returned; single-file, small n).
- Punts: every punt followed by the receiving club's drive (return touchdowns and punts retained by the kicking club are excluded), `[los, outcome, gross, return_yards, e, next_start, touchback]`; next = 100 - LOS + gross - return + e, or 80 + e on a touchback.
- Interceptions and fumbles lost followed by the other club's drive (return touchdowns excluded), `[end, next_start, return_yards, touchback, delta]` with delta = next - (100 - end).
- Downs and missed field goals use the rules next = 100 - end and next = min(80, 110 - distance).

Punt and turnover pools are ordered by line of scrimmage (end spot) only; records at the same spot keep season (file) order.

## Pre-registration (frozen before the kernel 2013.7 acceptance run)

| Item | Value |
|---|---|
| Partition (must sum to 5,984) | neutral interior (first half, plus second-half drives starting with more than 600 s) 4,632; first-half finals 256; late (second half, 600 s or less) 1,035; overtime 61 |
| Neutral start bins (`yardline_100`) | 90-99, 81-89, 80 exactly, 70-79, 60-69, 50-59, 40-49, 30-39, 20-29, 1-19 (sizes 436, 757, 1,176, 921, 572, 316, 165, 102, 89, 98) |
| Zones for the tuple ladder | A 80-99, B 50-79, C 1-49 |
| Late time buckets x need | 301-600 / 121-300 / <=120 s x trail 9+, trail 4-8, trail 1-3, tied, lead 1-8, lead 9+ |
| MIN_CELL | 30 |
| Late collapse | a thin cell merges into the adjacent later time bucket; a thin <=120 bucket into the adjacent earlier one; repeated; need never merged. Result: trail 1-3 {301-600 + 121-300: 49, <=120: 30}; tied {all: 54}; every other cell already >= 30 |
| First-half finals | 2013.6 bucket edges (0-30, 31-60, 61-120, 121-240, 241-1800) and collapse rule restricted to the first half: 0-30 113, 31-60 77, 61-1800 66 |
| Tuple ladder | a neutral (bin, category) list under 30 adds the nearest bins (ties to the lower index); at draw time the bin's list, else the same zone, else the category is masked (no "any" step). A rung counts only when one of its tuples is feasible at both the spot and the clock (see the acceptance-run correction below) |
| Keep end | field goal, punt, downs, interception, fumble lost keep the real end spot; clock keeps the real net; touchdown net = start; safety net = start - 100 |
| Envelopes | [min, max] real net per (category, start bin) over all 5,984 drives |
| Safety render rule | only from a start bin with a 2012 safety and a net inside that bin's envelope (a start at exactly 80 never can); the terminal kind and line of scrimmage come from the real render tuple, so the terminal loss is exactly 100 - LOS |
| K_TRANSITION | 20 nearest feasible records by line of scrimmage (end spot) |
| Field-goal offsets | distance - LOS in {17, 18, 19} |
| Fallbacks (everything masked) | union of the need's late cells; nearest-bucket clock tuple of the same need; `[0, 0, 0]` (must never occur) |
| Overtime | tied: the OT cell; trailing: the <=120 trail 1-3 cell (labelled inference; 2012 overtime trailing n = 4); leading: the OT cell with a diagnostic |
| Fourth-down decision zones | own half 50-99, opp 49-35, opp 34-1 (descriptive labels on the published fourth-down state) |
| KNOWN_DETECTIONS | {`punts per team game (drive-ending)`}, graded within twice its tolerance because the first-half half-final redirect remains |

## Reconciliation (primary pass, nflverse)

| Check | Result |
|---|---|
| Drives / category counts | 5,984; identical to the 2013.6 artifact |
| Field-goal attempts / made, interceptions | 1,016 / 852, 468 |
| Chain sums | 9,241 scrimmage first downs / 919 penalty first downs / 6,814 third-down attempts / 2,600 conversions (all rows of the drive, `no_play` penalty rows included) |
| Fourth downs inside drives | 451 attempts, 225 conversions |
| Punt drives with no third-down attempt | 0 of 2,467 |
| Plays per team-game | 64.22 (64.2 +/- 0.1) |
| Net per team-game with the corrected start | 348.04 (reported; the 2013.6 builder start gives 347.2) |
| Snap counts | attempts incl. 78 spikes 17,788; sacks 1,169; rushes incl. 367 kneels 13,925 (the stored 2012 totals) |
| Kickoff pool | 2,444 records, 1,128 touchbacks (0.4615; nflscrapR 0.4613); non-touchback start mean 77.02 (sd 9.77, n 1,316) |
| Punt pool | 2,405 records (nflscrapR 2,394) |
| Interception / fumble pools | 386 / 251 |
| Turnover touchbacks | 32 interception pool records carry "touchback" in the description (31 start exactly at 80); 35 counts every interception-category drive, including those not followed by a turnover-started drive (a remapped return touchdown or the end of a half). Fumbles lost: 5 in every definition. Identical in both files. The research figure 32 is the pool count. |
| Scramble share | 681 scrambles / 1,223 quarterback rushes (nflverse); nflscrapR 643 / 1,228: UNRESOLVED description-revision conflict, informational only |

Corrections recorded in the artifact: the 11 corrected starts; one field-goal attempt whose kick distance minus line of scrimmage is +29 keeps its real distance with its end set to distance - 18; four safeties (penalty safeties and an aborted-snap fumble out of the end zone) and one touchdown scored on a muffed punt recovered in the end zone by the punting club count in the category mix but are never drawn as render tuples.

## Second pass (nflscrapR, same code, nflverse cell map)

94 compared metrics: 39 match, 28 within tolerance (counts 1%, shares 1 point, means 0.6 yd), 27 explained, 0 unexplained. The explanations (`EXPLAINED` in the artifact):

- **Score rebuild.** nflscrapR lacks 115 extra-point rows (122 tries imputed against 0 in nflverse) and repeats one touchdown description (game 2012112200, plays 2563 and 2658), so a few drives change score state: late score-state cells differ by one to three drives, allowed only while the need-free late time-bucket totals agree (they do). The trail 1-3 <=120 cell holds 30 drives in nflverse and 29 in nflscrapR.
- **Late punt shares** (nflscrapR 27/199 and 5/131 against nflverse 23/194 and 1/126): the score rebuild plus the missing punt rows.
- **Punt rows.** nflscrapR has 11 fewer punt rows, so its punt pool and punt category are smaller and 15 of its drives classify as `other`.
- **Scrambles.** The `qb_scramble` flag follows the play description; the two files carry different GSIS description revisions.
- **Spikes.** nflscrapR codes two spikes (2012092304 play 4391, 2012111810 play 2332) as ordinary incomplete passes; pass-attempt totals are unaffected.

Single-file items: drive seconds (nflverse drive time of possession, 2013.6 clock scale reused), the tuple sequences themselves, and the 13 safety free kicks.

## Band centres

`band_centres` in the artifact feeds `runtime/bands.audit_field_position` (kernel 2013.7 cohort only):

| Row | Centre | Status |
|---|---|---|
| Kickoff touchback share | 1,128 / 2,444 = 0.4615 | graded, binomial 3 SE |
| Mean start after a non-touchback kickoff | 77.02 (sd 9.77) | graded, 3 sd / sqrt(n) |
| Realized punt net by LOS bin (own 1-10 ... opp 39-30) | 43.71, 43.35, 43.74, 42.29, 38.84, 32.91, 28.00 (sd 12.36, 12.63, 11.73, 12.03, 8.51, 6.85, 6.51) | graded, 3 sd / sqrt(n), INSUFFICIENT below 30 punts |
| Punt share of possessions ending in Q4's last 5:00 or OT, offense trailing 1-8 | 23 / 194 = 0.119 | graded |
| ... ending at <=2:00 or in OT | 1 / 126 = 0.008 | graded |
| Third-down attempts per punt drive | 1.185 (sd 0.440) | graded |
| Sacks per dropback | 1,169 / 18,957 = 0.0617 | graded, binomial 3 SE |
| DL / LB / DB share of sack credits | 0.599 / 0.337 / 0.063 (position-usage baseline) | graded, binomial 3 SE |
| Start-bin shares; mean start 72.26 (all drives, sd 17.56) and 72.77 (modelled transitions only, n 5,873) | | informational |
| Touchdown and punt share by coarse start (own 1-20 / own 21-50 / opp 49-1) | TD 0.158 / 0.199 / 0.349; punt 0.486 / 0.402 / 0.108 | informational |
| Points per drive by start bin (90-99, 80-89 incl. 80, 70-79 ... 20-29, 1-19) | 1.14 / 1.47 / 1.71 / 1.83 / 2.21 / 2.58 / 3.09 / 4.08 / 4.52 | informational |
| QB scramble share of QB carries | 0.557 (nflscrapR 0.524) | informational |
| Fourth-down attempts / conversions per team-game (drive chains) | 0.881 / 0.439 | informational |
| Kneels per team-game; overtime punt share | 0.717; 19 / 61 | informational |

## Design-phase history (design seeds only; never the acceptance sample or the private service)

Design 3 prototypes A, C and D (judged before this build) established the chassis: one resampled real drive per possession with the category conditioned on the start. This rebuild then grafted the exact-80 start cell, the full late partition, the corrected field-goal offsets, real chains, published kick and punt enforcement, fourth-down states and carrier-true labels. Every change below was made on design seeds (`design-2013-7-*`) before the constants froze, and is disclosed:

1. **Punt and turnover pools were first sorted by outcome within a line of scrimmage.** Because the draw takes the 20 nearest records with ties by index, that order selected the shortest punts (realized net about 32 yards against 43). The pools are now ordered by spot only, in season order.
2. **Tied boundary included in the 20-nearest draw.** Even in season order, "20 nearest, ties by index" always used the same first 20 records at a crowded line of scrimmage (an early-season subset), which moved the kernel's expected punt net by about one yard at own 31-40. The draw now takes the 20 nearest feasible records plus every record tied at the 20th distance, which brings the expected nets back to the bin centres.
3. **Kneels are the drive's last snaps**, so a tuple with kneels is feasible only if the spot before them is in the field.
4. **A lost fumble's terminal kind** (which snap was fumbled) is descriptive; when the drawn kind cannot be ordered inside the field, the snap stream tries the others before any value repair.
5. **A touchdown's scoring snap joins its kind in the one-yard repair**, and when only sacks precede the scoring snap the kernel caps their losses so the ball stays out of the own end zone (counted in `sack_losses_fitted`).
6. **Real per-drive snap counts** replace the pass and sack Bernoullis and the touchdown-type draw (see the sack-rate note below).
7. **First-half finals** use the collapsed bucket pool as their time match (the 2013.6 fine-edge match inside the 61-1800 pool would leave only 18 tuples); late and overtime finals use the 2013.6 edges.
8. Tried and **not adopted**: a per-category union of the same need's late cells before masking (no measurable effect on the touchdown share), a sourced first-half final-possession rate by window, and first-half late cells mirroring the second half (both moved drives per team-game to 12.1-12.25 and yards per team-game to 387).

**Acceptance-run correction (a code defect, disclosed).** The first acceptance run (the 250-game test sample, `sample-2013-7-0` to `-249`) read two graded rows OUTSIDE: drive share touchdown 0.2107 (centre 0.1945, tolerance 0.0155) and drive share clock 0.0526 (0.0628, 0.0095). Its diagnosis found that `eligible()` applied the bin-to-zone ladder on spot feasibility alone and only then the clock filter, so a same-bin rung whose tuples all failed the clock filter masked the category even when the same zone had a feasible tuple. The specification defines feasibility as spot and clock together, with the ladder stepping on it. Over the sample's 1,075 late possessions the masking moved the expected late mix from field goals (raw 0.124, as built 0.094) and clock drives (0.215 against 0.199) to touchdowns (0.153 against 0.200). The ladder now steps on full feasibility (`runtime/field_position.py`, `_rungs` and `eligible`; `tests/test_field_position.py::test_ladder_steps_on_full_feasibility`). The same run also showed that the zero-tolerance fourth-down check did not recompute the published action (a field-goal or downs terminal relabelled as a punt passed); `check_ledger` now compares it. Both are code corrections toward the pre-registered definitions; neither changes a coefficient, pool, cell, centre, bucket edge or tolerance. After them the design gate was rerun on design seeds (1,000 games and the 20-block sweep) before the acceptance sample was resolved again; both acceptance runs are reported.

No coefficient, pool, cell, centre or tolerance was changed after the canonical acceptance run was seen.

## Acceptance (250 synthetic games, `sample-2013-7-0` to `-249`)

Seed `b"synthetic-calibration-seed-not-career-state"`; club A carries the Week 6 call sheet (families only, carriers and targets from the committed family map) plus five label probes; club B has no sheet. Games are resolved with `runtime.kernel.resolve_game` directly; the private service is never contacted.

| Criterion | Run 1 (as frozen) | Run 2 (after the two code corrections) |
|---|---|---|
| `validate_result` errors | 0 | 0 |
| `check_ledger` violations, all 32 classes | 0 | 0 |
| Defect counts (touchback touchdowns with net other than 80, safeties from 80 or with start - net other than 100, touchdown net other than start, start other than the previous next start, punt identity, field-goal offset, label violations, Jet Sweep / TE Delay / RB screen mislabels, undeclared designed-run labels on QB carries, kneel and spike labels, unspecified calls, punts on Q4 possessions starting at 2:00 or less trailing 1-8, field goals on Q4 possessions starting at 5:00 or less trailing 4-8, missing fourth-down records) | all 0 | all 0 |
| `[0, 0, 0]` fallbacks / prefix-order failures | 0 / 0 | 0 / 0 |
| Sacks per dropback (centre 0.0617, +/-0.0052) | 0.0604 WITHIN | 0.0599 WITHIN |
| Late trailing punt shares, last 5:00 / 2:00 (0.1186, 0.0079) | 0.1268 / 0.0078 WITHIN | 0.1200 / 0.0083 WITHIN |
| Punts per team game (KNOWN_DETECTION, within 2x) | 4.758 WITHIN | 4.774 WITHIN |
| Graded rows OUTSIDE | drive share touchdown 0.2107 (0.1945 +/- 0.0155); drive share clock 0.0526 (0.0628 +/- 0.0095) | drive share clock 0.0507 (0.0628 +/- 0.0095); clock-expired drives per team game 0.598 (0.734 +/- 0.115); field goals made per team game 1.840 (1.664 +/- 0.173) |
| Graded rows WITHIN (of 57) | 55 | 54 |

**Status: not passed.** The remaining OUTSIDE rows share one diagnosed cause, and it is the pre-registered first-half design, not a code defect: the first half ends through the half-final redirect. A neutral drive that would reach halftime is replaced by a first-half final drawn from the collapsed pool for the seconds left, so the final possession starts far earlier than 2012's (design runs: P(final | 121-240 s) about 0.40 against 0.083), and the pool used for more than 60 seconds (66 drives, 73% of them starting with 61-120 s) is a two-minute-drill mix. On the run-1 sample the first-half finals read clock 0.352 and field-goal attempts 0.564 against 2012's first-half finals 0.637 and 0.273; that alone moves the clock share by about -0.012 of all drives. The design gate had shown the same direction before the freeze (1,000 design games: clock 0.055; 20-block sweep: 8 of 20 blocks with every graded row WITHIN). The ladder correction restored late field goals (late field-goal share about 0.124 against 2012's 0.121), which is why field goals made now read high as well. No coefficient, pool, cell, bucket edge, centre or tolerance was changed; the decision on this first-half design is left to the project lead.

## Sack-rate root cause (kernel 2013.6) and the 2013.7 mechanism

Kernel 2013.6 drew pass plays at 0.565 per snap and sacks as Bernoulli(1,169 / 18,957) per pass play, then made three feasibility conversions: an interception drive with no pass play was given a sack-free attempt, a touchdown or interception drive whose every pass play was a sack turned one sack into an attempt, and a drive with no usable snap turned a sack into an attempt. Replaying the 2013.6 rule over 400,000 resampled 2012 interior drives (seeded, reproducible) gives 6.15% before the conversions and 6.02% after them; design runs of the 2013.6 kernel give about 5.97-6.08%, and re-resolving the exact Weeks 4-5 TeamInputs on design seeds gives about 5.8-5.97%, so no input dependence explains the gap. The committed 2013.6 cohort's 91 sacks on 2,144 dropbacks (4.24%) is therefore about 3.4 standard errors below the mechanism's own expectation: the conversions explain roughly 0.15-0.2 points of the 1.9-point gap and the rest is a low sampling draw, not an input or dropback-definition defect (sacks taken, sack rows and team sacks allowed agree; dropbacks equal pass rows).

Kernel 2013.7 removes the conversions at the mechanism level: every possession replays the real drive's own runs, attempts, sacks, kneels and spikes and its own scoring kind, so a sack is never converted and a scoring or intercepted pass is always a real attempt. Over all 5,984 drives these counts reproduce the stored totals exactly (1,169 sacks on 18,957 dropbacks). The realised rate still depends on which drives the game-state mix draws; the graded row "sacks per dropback" (binomial 3 SE) watches it.

## Known limitations

- No per-snap down, distance or explicit go-for-it model: converted fourth downs inside a drive are real chain counts; a failed attempt is the downs terminal (snap-level replay deferred to kernel 2013.8).
- Fourth downs before the fourth quarter and outside late cells keep the resampled drive's own decision; a neutral second-half drive that runs into the last 10:00 is counted (`h2_neutral_into_late`), not terminal-checked.
- Late-cell category mixes are not conditioned on start position; start enters only through masking, the envelope and the bin-to-zone ladder. A masked category's probability is renormalised onto the others. Because the fourth-quarter terminal-bucket match applies only to punt, field-goal and downs tuples, thin cells mask those categories more often than touchdowns, so late cells run touchdown-heavy (design runs after the ladder correction: late touchdown share about 0.205 against 0.159; all drives about 0.203 against 0.195, the home edge adding about 0.004).
- The first half still ends through the half-final redirect: its final possession starts earlier than 2012's (design runs: P(final | 121-240 s) about 0.40 against 0.083), so first-half finals are field-goal-heavy and clock-light.
- Snap order is not derived from real downs; per-drive chains are real, but a reader cannot reconstruct down and distance from the snap ledger.
- Not modelled: onside kicks, kicking-team recoveries and retained punts, return touchdowns of every kind, blocked field goals (the missed-field-goal rule applies), two-point tries, timeouts, penalty safeties as penalties.
- Remaining unsourced constants (none moves the ball spot): non-terminal sack loss randint(3, 10), penalty yards randint(5, 10) and the penalty Bernoulli, the gauss yardage-split spreads, the legacy edge coefficients (0.025 / 0.008 / +/-0.06; apply_edge 0.65 / 0.35), passes-defended 0.35 and pressure 0.20.
- Resampled real drives recur across a season with different players and labels.
- Weather, venue (e.g. altitude touchbacks) and per-staff tendencies are not conditioned; `user_controlled` pauses remain a stub.
