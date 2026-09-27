# 2012 NFL position usage and drive volume for kernel 2013.4

**Research date:** September 27, 2026. **Football information window:** completed 2012 regular season only. **Status: VERIFIED for the 2013 runtime, with the single-source items labelled below.** No 2013 game, player line or team result is an input.

**Machine artifact:** [data/2012_nfl_position_usage_baseline.json](data/2012_nfl_position_usage_baseline.json). **Builder:** `scripts/research/build_2012_usage_baseline.py` (reads downloaded sources; the runtime never downloads anything).

## Why this exists

The Week 1 audit (2013 ledger Entry 34) found that team-level efficiency matched the 2012 baseline but player attribution and play volume did not. The engine had no concept of a depth chart and no sourced shape for who carries, who is targeted or who tackles. This file supplies those shapes. They distribute production the possession kernel has already resolved; they never decide an outcome, a depth chart, a roster spot or a Jacksonville quota.

## Sources

- **Primary pass:** nflverse 2012 play-by-play, [play_by_play_2012.csv.gz](https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2012.csv.gz), regular-season rows only (256 games, 512 team-games).
- **Position map:** nflverse [roster_2012.csv](https://github.com/nflverse/nflverse-data/releases/download/rosters/roster_2012.csv); each GSIS id takes its most frequent 2012 listed position.
- **Independent verification pass:** Ron Yurko's nflscrapR [reg_pbp_2012.csv](https://raw.githubusercontent.com/ryurko/nflscrapR-data/master/play_by_play_data/regular_season/reg_pbp_2012.csv), a separately scraped and published 2012 regular-season file, recomputed with the same code path.
- **Totals cross-check:** the existing NFL.com/PFR-derived [2012 aggregate baseline](2012_game_calibration.md).

## Verification result

Every share present in both files differs by at most **0.0039** between the two passes. Pass-level totals reconcile with the existing baseline: nflverse records 1,169 sacks (baseline 1,169) and 468 interception credits (baseline 468 interceptions); pass attempts are 17,753 against the baseline's 17,788 because spikes and aborted snaps are classified differently.

Items that could not be independently verified:

- **Sack credit by position group** is single-source: the nflscrapR 2012 file has no sack-credit columns.
- **Drive shapes** (plays and seconds per drive by result) use nflverse fixed-drive fields only. They are reconciled to the existing PFR-derived team-game totals rather than verified against a second drive file.
- **Position labels** come from one roster map in both passes, so labelling is not independently verified. In the rusher/target pass, 2 player IDs in the nflscrapR file had no roster match.

## Results (primary pass; verification in parentheses)

### Who gets the ball

| Share | RB | QB | FB | WR | TE |
|---|---:|---:|---:|---:|---:|
| Carries | 0.867 (0.867) | 0.090 (0.091) | 0.022 (0.022) | 0.019 (0.019) | 0.000 (0.000) |

| Share | WR | TE | RB | FB |
|---|---:|---:|---:|---:|
| Targets | 0.602 (0.602) | 0.215 (0.214) | 0.155 (0.156) | 0.026 (0.026) |

The leading passer threw **97.8%** of his team's attempts on average (97.8%); **82.8%** of team-games used a single passer (82.8%). Scrambles count as QB carries; kneels are excluded.

### Defensive credits

| Share | DB | LB | DL |
|---|---:|---:|---:|
| Tackle credits, solo plus assists | 0.401 (0.401) | 0.353 (0.352) | 0.226 (0.226) |
| Tackles for loss | 0.169 (0.169) | 0.374 (0.374) | 0.456 (0.453) |
| Sacks (single-source) | 0.063 | 0.337 | 0.599 |
| Interceptions | 0.786 (0.785) | 0.194 (0.194) | 0.019 (0.021) |
| Passes defended | 0.673 (0.673) | 0.192 (0.188) | 0.135 (0.139) |

About 2 percent of tackle credits went to offensive players after turnovers and are left out of the three groups. **20.4%** of tackled scrimmage plays carried an assist (20.5%). **10.1%** of carries lost yardage (10.1%); losses were 1 yard on 43.0%, 2 on 25.2%, 3 on 14.3%, 4 on 8.5%, 5 on 4.2% and 6 or more on 4.8% of losing carries.

### Usage rank inside a group

Within one team-game, ranked by that game's volume (index 1 is the most-used player). These are usage-rank shapes, not depth-chart facts; the runtime lays them over the coach-supplied depth order.

| Shape | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---:|---:|---:|---:|---:|---:|---:|
| RB carries | .741 | .213 | .044 | .002 | | | |
| WR targets | .469 | .298 | .166 | .057 | .010 | | |
| TE targets | .792 | .186 | .022 | | | | |
| RB targets | .754 | .211 | .033 | | | | |
| DL tackles | .375 | .239 | .165 | .113 | .065 | .031 | .011 |
| LB tackles | .440 | .291 | .170 | .068 | .023 | .006 | .002 |
| DB tackles | .324 | .238 | .179 | .131 | .085 | .035 | .008 |

Groups without their own shape borrow the closest sourced one (FB carries use RB carries, WR carries use WR targets, FB targets use RB targets); sacks, interceptions and passes defended use their group's tackle shape. That mapping is a modelling choice, stated here, not a measurement.

### Volume

| Per team-game | 2012 |
|---|---:|
| Third-down attempts | 13.31 (13.31) |
| Scrimmage first downs | 18.05 (18.05) |
| Penalty first downs | 1.80 (1.80) |

| Drive result | Drives | Plays mean | Plays SD | Seconds per play |
|---|---:|---:|---:|---:|
| Touchdown | 1,164 | 7.46 | 3.65 | 27.6 |
| Field goal | 851 | 7.71 | 3.19 | 28.6 |
| Punt | 2,440 | 4.29 | 1.81 | 30.2 |
| Turnover | 659 | 4.56 | 3.00 | 24.8 |
| Other (downs, missed FG, end of half, safety) | 748 | 5.05 | 3.58 | 23.8 |

The play-by-play drive definition counts end-of-half and split possessions that the PFR drive table in the aggregate baseline does not. The runtime therefore scales plays and clock by single factors, recomputed from these files at load time, so expected totals equal the verified 64.2 plays and 10.47 drives per team-game. The per-snap clock spread inside a drive is a modelling assumption; only its mean is sourced.

## Runtime use and limits

- `runtime/usage.py` applies these shapes; `runtime/bands.py` audits closed receipts against them and against the aggregate baseline.
- A synthetic 160-game league built from complete, depth-ordered rosters lands inside every audit band (`tests/test_usage_bands.py`). The kernel runs slightly above the 64.2-play target in that test (about 66.8) because the last possession of a game is cut short by the clock but still counts as a drive.
- The quarterback model plays one passer all game. It does not generate injury or blowout substitutions; a coach input is required for any change.
- Tackle shapes combine run and pass plays; the runtime does not yet separate them.
