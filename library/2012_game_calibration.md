# 2012 NFL aggregate inputs for 2013 game calibration

**Research date:** September 19, 2026. **Football information window:** completed 2012 regular season only, available before the current May 2013 game clock. These are league facts, not player grades or probabilities of a particular simulated result.

**Status:** PARTIAL. Aggregate inputs collected; a drive model has not been fitted or validated. Independent publisher confirmation and the missing inputs below remain open.

## Research pass

Sum the 32 club rows in the NFL's [2012 team passing table](https://www.nfl.com/stats/team-stats/offense/passing/2012/reg/all) and [2012 team rushing table](https://www.nfl.com/stats/team-stats/offense/rushing/2012/reg/all). These current archive pages identify the 2012 regular-season filter; original page publication dates are not supplied. No player-specific later outcome or actual 2013 performance is used.

| Aggregate | Sum |
|---|---:|
| Pass attempts / completions | 17,788 / 10,833 |
| Gross passing yards | 125,951 |
| Sacks / sack yards | 1,169 / 7,533 |
| Interceptions thrown | 468 |
| Pass gains of 20+ yards | 1,580 |
| Rush attempts / yards | 13,925 / 59,349 |
| Rush gains of 20+ yards | 355 |
| Recorded rushing fumbles | 222 |

The [data file](data/2012_nfl_aggregate_baseline.json) retains totals, column labels, source URLs and exact numerator/denominator definitions. Completion and interception rates use pass attempts. Sack rate uses attempts plus sacks. Net passing efficiency subtracts sack yards and includes sacks in its denominator. Rushing fumbles are neither all fumbles nor fumbles lost. A combined explosive measure cannot silently change denominators.

## Verification pass and limits

A separate read of the NFL's [opponent passing table](https://www.nfl.com/stats/team-stats/defense/passing/2012/reg/all) and [opponent rushing table](https://www.nfl.com/stats/team-stats/defense/rushing/2012/reg/all) reproduced the corresponding league totals. Each table contains 32 teams. Passing yards use a differently named column; sack yards are not in the opponent passing table and therefore lack this cross-check.

This is a useful reconciliation across separately fetched tables from the same publisher. It does not meet an independent-source confirmation standard. A separate search did not establish that confirmation, so the baseline remains provisional for engine calibration. The data include raw totals rather than averaged rounded team percentages.

## Remaining calibration

- Independently corroborate the totals and resolve any differences before fitting a production model.
- Add all-fumble, possession-loss, penalty, field-position, clock and special-teams inputs with clear exposure denominators.
- Source position/exposure injury incidence and severity/return distributions. Team totals cannot supply per-position per-snap risk.
- Verify period-specific game rules and tiebreaks. A current NFL rules/tiebreaking page cannot establish its 2013 counterpart.
- Fit the shared drive/segment kernel and demonstrate held-out calibration, score/clock/stat invariants, label symmetry and mandatory user pauses.

Do not promote these rates into game outcome probabilities by guesswork. The engine remains blocked under [Document 7](../foundation/07_Game_Simulation_and_Resolution_Engine.md).
