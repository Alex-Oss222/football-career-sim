# 2012 NFL aggregate inputs for 2013 game calibration

**Research date:** September 19, 2026. **Football information window:** completed 2012 regular season only. **Status: VERIFIED for the 2013 runtime.** No actual 2013 Jacksonville result is an input.

## Research and independent verification

The first pass sums the 32 club rows in the NFL's [passing](https://www.nfl.com/stats/team-stats/offense/passing/2012/reg/all) and [rushing](https://www.nfl.com/stats/team-stats/offense/rushing/2012/reg/all) tables. The separately fetched opponent tables reconcile attempts, yards, touchdowns, interceptions, sacks and explosives. The independent pass uses Pro Football Reference's [2012 league summary](https://www.pro-football-reference.com/years/2012/index.htm), [drive table](https://www.pro-football-reference.com/years/2012/drives.htm), [kicking table](https://www.pro-football-reference.com/years/2012/kicking.htm), and [return table](https://www.pro-football-reference.com/years/2012/returns.htm). Penalty magnitude was separately checked against [NFL Penalties' 2012 season table](https://www.nflpenalties.com/year/2012). Publisher rounding can make a displayed percentage differ slightly from a rate recomputed from integer totals; the runtime always uses stored integer numerator and denominator.

The machine artifact records source URLs, access date, denominators, calculations and limitations. Its 512 team-games are the denominator for per-team-game rates; 5,360 offensive drives are the denominator for fitted terminal drive shares; pass attempts plus sacks are the denominator for sack rate; pass attempts are the denominator for interception and pass-explosive rates; rush attempts are the denominator for rushing rates; kickoffs and field-goal attempts are their respective special-teams denominators.

## Fitted distribution

The deterministic calibration artifact fits mutually exclusive drive terminals: touchdown, field goal, punt, turnover, and other (downs, missed field goal, safety/end-of-half administrative possessions). The shares sum exactly to one and are consumed by the only shared kernel. The kernel separately uses observed pass tendency, third-down conversion environment, sacks, penalties, kickoff touchbacks, punt returns and field-goal accuracy. It samples yardage around the observed net passing and rushing efficiencies rather than treating the league mean as a guaranteed outcome.

The special-teams layer is anchored to period totals for field-goal attempts/makes, punts, kickoffs/touchbacks, kickoff returns and punt returns. Range accuracy is represented by period bins in the kernel's bounded field-goal decision surface; the aggregate attempt-weighted value remains the reconciliation target. Touchdowns include offensive and return scores when reconciling scoring, while passing and rushing touchdown totals remain separately preserved.

## Injury calibration

The primary incidence source is the contemporaneous NFL injury-surveillance study, [Feeley et al., *American Journal of Sports Medicine* (2013)](https://pubmed.ncbi.nlm.nih.gov/24142991/); the second pass checks its game-versus-practice direction and exposure framing against CDC's [NFL concussion surveillance](https://www.cdc.gov/mmwr/preview/mmwrhtml/mm6036a2.htm). Public data do not expose every position-by-diagnosis-by-duration cell. The runtime therefore uses a sourced bounded model: snap exposure, higher game than practice hazard, conservative position bands, and four absence classes. It generates only broad football injury classes; medical disposition owns restriction, reassessment and return. A head/neck event becomes an independent medical hold and is never coach-overridable.

## Applicability and limitations

This is a prospective closest-season baseline for January 2013-forward simulation, not an attempt to recreate exact 2012 standings. PFR is independent of the NFL table presentation but ultimately describes the same games. Drive tables include administrative end-of-half possessions; those remain in `other`. Public injury surveillance supports aggregate bounds more strongly than every position cell, so long-run tests enforce aggregate burden, position ordering and bounded long-term outcomes rather than false precision. `runtime/calibration.py` deterministically validates this artifact, and runtime tests validate reconciliation and broad period bands.

## Error corrections (September 27, 2026; kernel 2013.6)

These notes correct statements above that were found to be inaccurate while building the kernel 2013.6 drive model. They do not change any stored value; `model.drive_outcomes` and `drives_per_team_game` stay in the artifact so kernel 2013.5 remains reproducible from history. The replacement drive inputs and their sourcing are in [the 2012 drive model calibration](2012_drive_model_calibration.md).

- **Lines 7 and 9 (drive shares and their denominator).** The fitted terminal shares (.221/.158/.466/.132/.023) have no stored integer numerators; `other` is a residual of the other four. The PFR drive table they cite could not be re-reached (proxy-blocked), so the shares cannot be re-derived. They are retired from kernel use for 2013.6, not explained.
- **Line 13 (`other` contents).** `other` cannot hold the 164 missed field goals: 164 / 5,360 = .031, larger than the .023 `other` bucket. The text's list of what `other` contains was therefore wrong.
- **Lines 13 and 15 (kicking detail).** Kernel 2013.5 did not use field-goal accuracy, range bins or return scores: every field-goal drive scored 3 and every touchdown 7. "Range accuracy is represented by period bins in the kernel's bounded field-goal decision surface" described no implemented mechanism. Kernel 2013.6 uses the sourced accuracy by kick distance.
- **Line 23 (end-of-half drives).** "Drive tables include administrative end-of-half possessions" contradicts `2012_position_usage_calibration.md` (line 86), which records that the play-by-play definition counts end-of-half and split possessions that the PFR drive table does not. The play-by-play statement is the one the 2013.6 drive model reconciles (5,984 drives, 376 of them clock-expired).
