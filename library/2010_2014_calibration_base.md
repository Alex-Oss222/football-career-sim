# 2010-2014 league calibration base

[Pre-build specification](2014_6_pre_build_specification.md) · [Scoring decisions](2010_2014_scoring_decisions_calibration.md) · [Context and conditions](2014_context_and_conditions_calibration.md) · [Engine decisions](../runtime/2014_engine_decisions.md#kernel-20146-decisions-dated) · [2012 field-position model](2012_field_position_model_calibration.md)

**What this is.** The league base of kernel 2014.6, built in plan batch B3 and data only: no runtime module reads these files until batch B5. The user chose U1 = (b) on October 2, 2026, so from 2014 Week 5 the 2010-2014 window replaces the 2012 base for drive pools, game rates, band centres and the league effect fits. Weeks 1-4 of 2014 stand as played on the 2012 base. Three artifacts, all built by `scripts/research/build_2010_2014_league_base.py`, which has a `--check` mode:

- `library/data/2010_2014w4_nfl_field_position_model.json` (schema v3): the drive tuples, cells, transition pools, band centres, constants and annotations;
- `library/data/2010_2014w4_nfl_drive_model.json` (schema v2): per-season integer rates, the field-goal distance logistic and the clock scale;
- `library/data/2010_2014w4_nfl_aggregate_baseline.json` (schema v3): team-game volume centres and play-level rates, reconciled with NFL.com.

The companion B3 artifacts:

- `library/data/2010_2014w4_nfl_position_usage_baseline.json`, from `build_2010_2014_usage_baseline.py`;
- `library/data/2010_2014w4_nfl_injury_calibration.json`, from `build_2010_2014_injury_calibration.py`;
- `library/data/2013_2014_participation_structure.json`, from `build_2013_2014_participation_structure.py`, informational only;
- the scoring and conditions records linked above.

**Data window and gate.** NFL regular seasons 2010-2013 and 2014 Weeks 1-4: 61 games, the last on September 29, 2014. The data is read only through `scripts/research/sources_2010_2014.py`, the batch B2 gate, which cuts 2014 at fetch and verifies every file's digest against `library/data/2010_2014_sources_manifest.json`. The base is usable in the branch from September 30, 2014. It is frozen at the first Week 5 event and stays frozen for the rest of 2014. 2013 and 2014 Weeks 1-4 are an anonymous post-divergence league population, so they enter pooled fits only. No artifact holds a club, game, player or date field, and no branch receipt or audit reading entered any value. Each header records the specification's sha256.

## Method

- **Extraction.** Each season goes through the committed 2012 builders' own functions: drive grouping by the nflverse `fixed_drive` key, the offensive-snap test, the result classifier, start kinds and transition records (`scripts/research/league_base_2010_2014.py`). The rebuilt transition records are asserted equal to the committed extractor's. A 2012 run of the committed build functions on the same extraction must reproduce the committed 2012 field-position and drive models on every key except `reconciliation` and `second_pass`, or the build fails.
- **Pooling.** Equal weight per event; per-season integer counts are stored. The structural filters are dated:
  - kickoff records from 2011 (the 2010 kicks from the 30 are excluded);
  - the 88 overtime drives of 2010-2011 (pure sudden death) are excluded from the overtime pools and from the overtime and late centres;
  - safety free kicks from every season.

  Every rate carries a per-season homogeneity test: chi-square for shares, Poisson chi-square for per-unit rates, and an ANOVA F test for means. The pooled rate is used whatever the test reads.
- **Source defects** (explained, never repaired by hand). 2010_12_CAR_CLE splits a drive in `fixed_drive`, and the game is regrouped by the source `drive` key. 2013_05_SD_OAK has two field-goal attempts on one drive. 2011_13_DET_NO has rows out of file order, found by the scoring builder's denominator check.
- **R17a seconds.** A drive's seconds are the time of possession on the first row of its group carrying one. The value is accepted when 0 ≤ TOP − e ≤ 45, where e is the game-clock time from the first snap to the terminal snap. Otherwise the seconds are e plus the median of TOP − e over that group's accepted drives (interior; first-half clock expiry; end-of-game clock). The pooled clock scale is recomputed from the corrected seconds, and each season's own scale is stored.
- **Partition (schema 3).** Neutral covers drives starting with more than 600 seconds left in the half. `h1_late` is the first half at or under 600 seconds, keyed 0-30, 31-60, 61-120, 121-240 and 241-600. Late is the second half at or under 600 seconds, in three time bins by eight needs. `ot_first` is the opening overtime possession and `ot_sudden` a later tied one, both from 2012. `ot_untied`, a later possession that is not tied, is counted but not pooled. The collapse rules run on raw counts, and every cell holds at least `MIN_CELL` (30).
- **Annotations (B3b).** Each tuple carries, in snap order:
  - its real rushing and passing yards, completions, sack losses, run and completion values, and the terminal snap;
  - its penalty clauses, parsed from the counted description (the 2014 emphasis counts and their exposures among them);
  - its fumbles, the single source of the lost-fumble terminal kind;
  - its legal placement range.

  Kick records gain their penalty clauses, a `spot_adjust` that leaves `enforcement` as the total, the fumble or muff, the next possession and the muffer's role. Kicking-club recoveries are kept as retained records in the kicking frame.
- **Drive model.** Field-goal make by distance band and in total, the extra point (the one source batch B9 reads), the two-point rate under both definitions, and the field-goal distance logistic. The logistic is fitted on events in both passes; its band intercepts are solved so that the mean fitted probability over the pool's own tuple distances equals the band's rate. The 2013.6 interior and half-final pools are dropped (the 2012 file keeps them).
- **Aggregate baseline.** Play-level integer pairs and team-game volume centres. Passing and rushing totals are reconciled to the NFL.com team tables for 2010-2013. 2014 Weeks 1-4 comes from a single publisher, because no table compiled before the gate is fetched. The B2 source set holds no NFL.com penalty table, so accepted penalties are checked against nflscrapR only.
- **Second pass.** The same code runs on nflscrapR, with the drive key `drive`. Counts must agree within 1% unless explained. Both files derive from the NFL GSIS feed, so this checks the parse and the classifier, not an independent observation.
- **Mode A.** `--seasons 2012` builds the same schemas on 2012 alone (files with a `_v3` suffix). It is not committed, because U1 = (b).

## Figures

<!-- generated:begin -->
Generated by `scripts/research/build_2010_2014_league_base.py` from the three artifacts; do not edit.

**Partition** (drives): neutral 16287, h1_late 4577, late 4493, ot_first 41, ot_sudden 64, ot_untied 6; 2010-2011 overtime excluded 88; total 25556.

| Season | Games | Drives | neutral | h1_late | late | ot_first | ot_sudden | ot_untied | Clock scale |
|---|---|---|---|---|---|---|---|---|---|
| 2010 | 256 | 6013 | 3827 | 1064 | 1063 | 0 | 0 | 0 | 921600 / 928340 |
| 2011 | 256 | 6050 | 3843 | 1094 | 1084 | 0 | 0 | 0 | 921600 / 924713 |
| 2012 | 256 | 5984 | 3823 | 1065 | 1035 | 22 | 35 | 4 | 921600 / 929963 |
| 2013 | 256 | 6144 | 3929 | 1101 | 1069 | 16 | 27 | 2 | 921600 / 928979 |
| 2014w4 | 61 | 1365 | 865 | 253 | 242 | 3 | 2 | 0 | 219600 / 219985 |

Pooled clock scale: 3906000 / 3931980.

**R17a drive seconds**: group medians of TOP - e end_of_game_clock 26 s, h1_clock_expiry 15 s, interior 9 s; drives by group and basis end_of_game_clock|corrected 37, end_of_game_clock|top 896, h1_clock_expiry|corrected 11, h1_clock_expiry|top 708, interior|corrected 140, interior|top 23764.
By grouping (not accepted; changed from the committed rule): 2010 fixed_drive 46 and 254 of 6014, drive 38 and 38 of 6013; 2011 fixed_drive 49 and 285 of 6050, drive 47 and 47 of 6052; 2012 fixed_drive 43 and 291 of 5984, drive 42 and 42 of 5986; 2013 fixed_drive 38 and 254 of 6144, drive 36 and 36 of 6141; 2014w4 fixed_drive 12 and 58 of 1365, drive 8 and 8 of 1365; totals fixed_drive 1142, drive 171 changed.

**Constants reproduced**: spike window 148.0 s (2010-2012 maximum, 2 spikes at it); early field goal 43.0 s (next 38.0, 36.0).

**Cells**: late 121-300|lead1_8 282, 121-300|lead9 332, 121-300|tied 62, 121-300|trail12_16 117, 121-300|trail17p 222, 121-300|trail1_3 125, 121-300|trail4_8 195, 121-300|trail9_11 99, 301-600|lead1_8 387, 301-600|lead9 438, 301-600|tied 88, 301-600|trail12_16 155, 301-600|trail17p 283, 301-600|trail1_3 142, 301-600|trail4_8 250, 301-600|trail9_11 126, le120|lead1_8 279, le120|lead9 255, le120|tied 125, le120|trail12_16 58, le120|trail17p 127, le120|trail1_3 124, le120|trail4_8 166, le120|trail9_11 56; h1_late 0-30 554, 121-240 726, 241-600 2183, 31-60 414, 61-120 700; ot_first 41, ot_sudden 64, ot_untied 6.

**Transition pools**: kickoff_pool 7944, free_kick_pool 65, punt_pool 10348, interception_pool 1790, fumble_pool 1044; retained kickoff 41, free_kick 0, punt 105.

| Drive-model rate | Pooled | Drift p |
|---|---|---|
| FG <30 | 1118/1158 = 0.9655 | 0.7566 |
| FG 30-39 | 1074/1212 = 0.8861 | 0.8485 |
| FG 40-49 | 995/1281 = 0.7767 | 0.0189 |
| FG 50+ | 360/574 = 0.6272 | 0.2214 |
| field_goal | 3547/4225 = 0.8395 | 0.1128 |
| extra_point | 5192/5228 = 0.9931 | 0.2279 |
| two_point | 117/240 = 0.4875 | 0.9017 |
| td_type_pass | 3257/4969 = 0.6555 | 0.8683 |
| turnover_type_interception | 2088/3255 = 0.6415 | 0.6334 |
| two_point, scrimmage definition | 115/232 = 0.4957 | |

| Season | FG | XP | Two-point | Completion | Gross YPA | YPC | Penalties per team-game | Points per team-game |
|---|---|---|---|---|---|---|---|---|
| 2010 | 0.8237 | 0.9885 | 26/50 | 0.6075 | 7.001 | 4.210 | 6.049 | 22.037 |
| 2011 | 0.8289 | 0.9942 | 23/50 | 0.6011 | 7.200 | 4.292 | 6.396 | 22.203 |
| 2012 | 0.8386 | 0.9935 | 29/56 | 0.6090 | 7.081 | 4.262 | 6.275 | 22.756 |
| 2013 | 0.8647 | 0.9961 | 33/69 | 0.6121 | 7.123 | 4.167 | 6.123 | 23.408 |
| 2014w4 | 0.8475 | 0.9933 | 6/15 | 0.6434 | 7.265 | 4.183 | 6.902 | 23.098 |

**FG distance logistic** (events): slope -0.09504 per yard (SE 0.0050); pass 2 -0.09486 (SE 0.0050); band intercepts <30 5.6685, 30-39 5.3610, 40-49 5.4948, 50+ 5.5579.

| Aggregate | Pooled (equal weight per event) |
|---|---|
| gross_yards_per_pass_attempt | 7.1110 per unit (532547 / 74891), drift p 0.0000 |
| yards_per_carry | 4.2299 per unit (249570 / 59001), drift p 0.0000 |
| completion_rate | 45650/74891 = 0.6096 (drift p 0.0000) |
| sack_rate | 5022/79913 = 0.0628 (drift p 0.0090) |
| interception_rate | 2088/74891 = 0.0279 (drift p 0.1476) |
| accepted_penalties_per_team_game | 6.2498 per unit (13562 / 2170), drift p 0.0053 |
| accepted_penalty_yards_per_team_game | 53.0733 per unit (115169 / 2170), drift p 0.0000 |
| penalty_first_downs_per_team_game | 1.7267 per unit (3747 / 2170), drift p 0.0000 |
| drive_penalty_per_play | 0.0865 per unit (12867 / 148786), drift p 0.0069 |
| points_per_team_game | 22.6290 per unit (49105 / 2170), drift p 0.0000 |
| plays_per_team_game | 64.0157 per unit (138914 / 2170), drift p 0.0027 |
| net_yards_per_team_game | 344.9106 per unit (748456 / 2170), drift p 0.0000 |
| first_downs_per_team_game | 19.6198 per unit (42575 / 2170), drift p 0.0000 |
| third_down_attempts_per_team_game | 13.3668 per unit (29006 / 2170), drift p 0.4574 |
| third_down_rate | 11143/29006 = 0.3842 (drift p 0.0023) |
| drives_per_team_game | 11.7770 per unit (25556 / 2170), drift p 0.1839 |

**Replacement officials** (2012 Weeks 1-3, 48 games, kept): accepted penalties per team-game 6.2498 with, 6.2242 without (difference +0.0256).

**NFL.com reconciliation** (2010-2013): match 17, within 1% 19 of 36 comparisons; result pass. Penalties: unreconciled: the B2 source set holds no NFL.com penalty table; the accepted-penalty parse is checked against nflscrapR only (annotation second pass).

**Second pass, field position**: explained 10, match 57, within 1% 52; result pass.
- 2010 category:other: nflverse 0, nflscrapR 14. nflscrapR drops terminal offensive rows (committed 2012 explanation).
- 2010 category:safety: nflverse 13, nflscrapR 14. One of the five spurious nflscrapR safety flags (a run to the 1) ends a drive, so nflscrapR shows 14 safety drives against nflverse's 13 (see safeties).
- 2011 category:other: nflverse 0, nflscrapR 19. nflscrapR drops terminal offensive rows (committed 2012 explanation).
- 2011 spikes: nflverse 79, nflscrapR 78. nflscrapR codes some spikes as ordinary incomplete passes (the committed 2012 explanation; the other seasons' one- or two-spike gaps were not matched row by row).
- 2012 category:other: nflverse 0, nflscrapR 15. nflscrapR drops terminal offensive rows (committed 2012 explanation).
- 2012 spikes: nflverse 78, nflscrapR 76. nflscrapR codes some spikes as ordinary incomplete passes (the committed 2012 explanation; the other seasons' one- or two-spike gaps were not matched row by row).
- 2013 category:other: nflverse 0, nflscrapR 16. nflscrapR drops terminal offensive rows (committed 2012 explanation).
- 2014w4 kneels: nflverse 94, nflscrapR 99. nflscrapR codes six 2014 Weeks 1-4 kickoff touchbacks whose description says the returner knelt as quarterback kneels and lacks one real kneel (94 against 99 in 61 games); nflverse is used.
- 2014w4 sacks: nflverse 240, nflscrapR 243. nflscrapR codes five 2014 Weeks 1-4 plays as sacks that nflverse codes as runs or no-plays (two of them aborted-snap fumbles), and nflverse two that nflscrapR codes as runs: 240 against 243 in 61 games; nflverse is used.
- 2014w4 spikes: nflverse 17, nflscrapR 16. nflscrapR codes some spikes as ordinary incomplete passes (the committed 2012 explanation; the other seasons' one- or two-spike gaps were not matched row by row).

**Second pass, drive model**: explained 16, match 34, within 1% 24; result pass.
- 2010 category:other: nflverse 0, nflscrapR 14. nflscrapR carries fewer terminal pass, punt and field-goal rows and more no_play rows, so some drives lose their terminal offensive play (the committed 2012 explanation).
- 2010 category:safety: nflverse 13, nflscrapR 14. One of the five spurious nflscrapR safety flags (a run to the 1) ends a drive, so nflscrapR shows 14 safety drives against nflverse's 13 (see safeties).
- 2010 safeties: nflverse 13, nflscrapR 18. nflscrapR sets its safety flag on five 2010 plays whose descriptions record no safety (three kickoffs, an interception and a run to the 1); the thirteen described safeties agree.
- 2010 xp_attempts: nflverse 1217, nflscrapR 1127. nflscrapR is missing extra-point rows (the committed 2012 explanation found 115 in 2012); the other seasons' shortfalls are of the same kind and were not matched row by row.
- 2010 xp_made: nflverse 1203, nflscrapR 1113. nflscrapR is missing extra-point rows (as xp_attempts).
- 2011 category:other: nflverse 0, nflscrapR 19. nflscrapR carries fewer terminal pass, punt and field-goal rows and more no_play rows, so some drives lose their terminal offensive play (the committed 2012 explanation).
- 2011 xp_attempts: nflverse 1207, nflscrapR 1114. nflscrapR is missing extra-point rows (the committed 2012 explanation found 115 in 2012); the other seasons' shortfalls are of the same kind and were not matched row by row.
- 2011 xp_made: nflverse 1200, nflscrapR 1108. nflscrapR is missing extra-point rows (as xp_attempts).
- 2012 category:other: nflverse 0, nflscrapR 15. nflscrapR carries fewer terminal pass, punt and field-goal rows and more no_play rows, so some drives lose their terminal offensive play (the committed 2012 explanation).
- 2012 xp_attempts: nflverse 1237, nflscrapR 1122. nflscrapR is missing extra-point rows (the committed 2012 explanation found 115 in 2012); the other seasons' shortfalls are of the same kind and were not matched row by row.
- 2012 xp_made: nflverse 1229, nflscrapR 1114. nflscrapR is missing extra-point rows (as xp_attempts).
- 2013 category:other: nflverse 0, nflscrapR 16. nflscrapR carries fewer terminal pass, punt and field-goal rows and more no_play rows, so some drives lose their terminal offensive play (the committed 2012 explanation).
- 2013 xp_attempts: nflverse 1267, nflscrapR 1153. nflscrapR is missing extra-point rows (the committed 2012 explanation found 115 in 2012); the other seasons' shortfalls are of the same kind and were not matched row by row.
- 2013 xp_made: nflverse 1262, nflscrapR 1149. nflscrapR is missing extra-point rows (as xp_attempts).
- 2014w4 xp_attempts: nflverse 300, nflscrapR 280. nflscrapR is missing extra-point rows (the committed 2012 explanation found 115 in 2012); the other seasons' shortfalls are of the same kind and were not matched row by row.
- 2014w4 xp_made: nflverse 298, nflscrapR 278. nflscrapR is missing extra-point rows (as xp_attempts).

**Second pass, annotations**: explained 2, listed 5, match 1, within 1% 17; result pass.
- 2011 scrimmage_fumbles: nflverse 614, nflscrapR 607. nflscrapR leaves its fumble flag unset on seven 2011 fumbles (614 against 607): six the offense kept or that went out of bounds and one lost (288 against 287).
- 2014w4 scrimmage_fumbles: nflverse 152, nflscrapR 144. nflscrapR leaves its fumble flag unset on eight 2014 Weeks 1-4 fumbles the offense kept (133 against 125); the lost fumbles agree (64).

**Relocation feasibility**: neutral 16268 tuples, 4 with defensive penalty yards over start - 1, 0 outside placement; h1_late 4571 tuples, 0 with defensive penalty yards over start - 1, 0 outside placement; late 4487 tuples, 2 with defensive penalty yards over start - 1, 0 outside placement; ot_first 41 tuples, 0 with defensive penalty yards over start - 1, 0 outside placement; ot_sudden 64 tuples, 0 with defensive penalty yards over start - 1, 0 outside placement.

**Emphasis counts** (accepted, per exposure): defense|Defensive Holding 2010 98/19699, 2011 124/20171, 2012 144/20586, 2013 168/21113, 2014w4 57/4976; defense|Illegal Contact 2010 66/19699, 2011 68/20171, 2012 62/20586, 2013 37/21113, 2014w4 32/4976; offense|Offensive Pass Interference 2010 70/19699, 2011 67/20171, 2012 76/20586, 2013 61/21113, 2014w4 23/4976; defense|Illegal Use of Hands 2010 26/34289, 2011 43/34827, 2012 50/35262, 2013 41/35519, 2014w4 31/8442; offense|Illegal Use of Hands 2010 13/19699, 2011 30/20171, 2012 28/20586, 2013 31/21113, 2014w4 13/4976.

**Lost-fumble terminal kind**: aborted 102, kick 1, reception 304, run 388, sack 368.
<!-- generated:end -->
