# Library data

Machine artifacts behind the [library records](../README.md). This page is an index only: it changes no data and copies no value. Each row names the file's record, the builder that writes it and the check that verifies it (or, where there is no check, what pins it), and a status taken from code and repository references, not from judgment. Builders live in `scripts/research/` unless another folder is named ([scripts index](../../scripts/README.md)).

**Never hand-edit a pinned file.** `runtime/calibration_base.py` pins the two calibration bases by sha256: `BASE_2012` serves every kernel through 2014.5 (the 2013 season and 2014 Weeks 1 to 4), and `BASE_2010_2014W4` serves kernel 2014.6. Changing a pinned file's bytes breaks that pin, even where the file's own status string has gone out of date.

**Sources.** The 2014.6 builders read their downloads only through `scripts/research/sources_2010_2014.py` (the information gate and sources manifest); `--sources DIR` defaults to `$SOURCES_2010_2014_DIR`. The other builders name their downloaded inputs and pinned digests in their own docstrings. Raw downloads are never committed.

## Calibration base 2010_2014w4 (kernel 2014.6)

| File | Record | Builder and check | Pin or reader | Status |
|---|---|---|---|---|
| `2010_2014w4_nfl_field_position_model.json` | [calibration base](../2010_2014_calibration_base.md) | `build_2010_2014_league_base.py --check` | `BASE_2010_2014W4` field_position | Pinned |
| `2010_2014w4_nfl_drive_model.json` | [calibration base](../2010_2014_calibration_base.md) | `build_2010_2014_league_base.py --check` | `BASE_2010_2014W4` drive_model | Pinned |
| `2010_2014w4_nfl_aggregate_baseline.json` | [calibration base](../2010_2014_calibration_base.md) | `build_2010_2014_league_base.py --check` | `BASE_2010_2014W4` aggregate | Pinned |
| `2010_2014w4_nfl_injury_calibration.json` | [calibration base](../2010_2014_calibration_base.md) | `build_2010_2014_injury_calibration.py --check` | `BASE_2010_2014W4` injury | Pinned; its internal status string predates batch B5 and is left as built |
| `2010_2014w4_nfl_position_usage_baseline.json` | [calibration base](../2010_2014_calibration_base.md) | `build_2010_2014_usage_baseline.py --check` | `BASE_2010_2014W4` usage | Pinned |
| `2010_2014w4_scoring_decisions.json` | [scoring decisions](../2010_2014_scoring_decisions_calibration.md) | `build_2010_2014_scoring_decisions.py --check` | `BASE_2010_2014W4` scoring | Pinned |
| `2010_2014w4_fourth_down_decisions.json` | [fourth downs](../2010_2014_fourth_down_calibration.md) | `build_2010_2014_fourth_down_decisions.py --check` | `BASE_2010_2014W4` fourth_down | Pinned |
| `2010_2014w4_ball_security.json` | [ball security](../2010_2014_ball_security_calibration.md) | `build_2010_2014_ball_security.py --check` | `BASE_2010_2014W4` ball_security | Pinned |
| `2010_2014w4_penalties.json` | [penalties](../2010_2014_penalty_calibration.md) | `build_2010_2014_penalties.py --check` | `BASE_2010_2014W4` penalties | Pinned |
| `2010_2014w4_yardage.json` | [yardage](../2010_2014_yardage_calibration.md) | `build_2010_2014_yardage.py --check` | `BASE_2010_2014W4` yardage | Pinned |
| `2010_2014_sources_manifest.json` | [calibration base](../2010_2014_calibration_base.md) | `sources_2010_2014.py --fetch --dest DIR --write-manifest`; `sources_2010_2014.py --check` | Read by the 2014.6 builders, never by `runtime/` (its own status field) | Builder input |
| `2013_2014_participation_structure.json` | [calibration base](../2010_2014_calibration_base.md) | `build_2013_2014_participation_structure.py --check` | No kernel coefficient reads it (its own status field) | Informational |

The 2014.6 base also pins `2014_strength_calibration_v2.json` (usage_tilt) and the pre-build specification record (`../2014_6_pre_build_specification.md`, pinned by `pre_build_specification.py`).

## Calibration base 2012 (kernels through 2014.5)

| File | Record | Builder and check | Pin or reader | Status |
|---|---|---|---|---|
| `2012_nfl_aggregate_baseline.json` | [2012 game calibration](../2012_game_calibration.md) (its "machine artifact") | No builder in the repository | `BASE_2012` aggregate; `runtime/calibration.py` | Pinned |
| `2012_nfl_drive_model.json` | [drive model](../2012_drive_model_calibration.md) | `build_2012_drive_model.py --check` | `BASE_2012` drive_model; `runtime/drive_model.py` | Pinned |
| `2012_nfl_field_position_model.json` | [field-position model](../2012_field_position_model_calibration.md) | `build_2012_field_position_model.py --check` | `BASE_2012` field_position; `runtime/field_position.py` | Pinned |
| `2012_nfl_position_usage_baseline.json` | [position usage](../2012_position_usage_calibration.md) | `build_2012_usage_baseline.py SOURCE_DIR` (no `--check`) | `BASE_2012` usage; `runtime/usage.py` | Pinned |
| `2012_nfl_injury_calibration.json` | [injury calibration](../2012_nfl_injury_calibration.md) | `build_2012_injury_calibration.py SOURCE_DIR` (no `--check`) | `BASE_2012` injury; `runtime/injury_model.py` | Pinned; its internal status string predates kernel 2014.4 and is left as built |

`BASE_2012` also pins `2014_strength_calibration_v2.json` (usage_tilt) and `2014_strength_calibration_v3.json` (fg_distance).

## Strength and pre-divergence evidence

| File | Record | Builder and check | Pin or reader | Status |
|---|---|---|---|---|
| `2010_2012_honours_evidence.json` | [honours evidence](../2010_2012_honours_evidence.md) | `build_2010_2012_honours_evidence.py HONOURS_JSON SOURCE_DIR` (no `--check`) | `runtime/strength.py` | Current input; matches the digest recorded in v2 and v3 |
| `2010_2012_production_evidence.json` | [production evidence](../2010_2012_production_evidence.md) | `build_2010_2012_production_evidence.py SOURCE_DIR` (no `--check`) | `runtime/strength.py`; `tests/test_production_evidence.py` | Current input; matches the digest recorded in v3 |
| `2014_strength_calibration.json` (first pass, v1) | [strength calibration](../2014_strength_calibration.md) | `build_2014_strength_calibration.py SOURCE_DIR PBP_2012 [PBP_2011]` (no `--check`) | `runtime/strength.py` (`first_pass_calibration_file`); `tests/test_strength.py` | Frozen |
| `2014_strength_calibration_v2.json` | [strength calibration](../2014_strength_calibration.md), section 9 | `build_2014_strength_calibration_v2.py SOURCE_DIR PBP_2012` (no `--check`) | Both bases (usage_tilt); `runtime/strength.py` | Frozen; still pinned |
| `2014_strength_calibration_v3.json` | [strength calibration](../2014_strength_calibration.md), section 10 | `build_2014_strength_calibration_v3.py SOURCE_DIR` (no `--check`) | `BASE_2012` (fg_distance); `runtime/strength.py` | Pinned; its recorded inputs match the current files |
| `2014_strength_calibration_v4.json` | [strength calibration](../2014_strength_calibration.md), section 11 | `build_2014_strength_calibration_v4.py --check` | `runtime/strength.py`, `runtime/profiles.py` (player-state-v1) | In production for 2014.6 |
| `passer_interception_persistence.json` | [interception persistence study](../passer_interception_persistence_study.md) | `build_passer_interception_persistence.py SOURCE_DIR`; second pass `verify_passer_interception_persistence.py SOURCE_DIR` | Nothing in `runtime/` (its own status field) | Research only |

**Reproducing v1 and v2 (frozen).** Their recorded input digests no longer match the committed inputs, which were rebuilt later; the files and their pins are unchanged. To reproduce them, check out the inputs as they stood when each was built: the honours evidence at commit 81ebe46 for v1; the production evidence at commit 772a4f2 and the birth-date registry at commit 1112469 for v2. The league player inventory both name, `career/2014/League/personnel/league_players.json`, matches the recorded digest today; v1 names it under its pre-reorganization path.

## Player state (kernel 2014.6)

| File | Record | Builder and check | Pin or reader | Status |
|---|---|---|---|---|
| `2010_2014_player_state_model.json` | [player-state study](../2010_2014_player_state_study.md) | `build_2010_2014_player_state_model.py --check`; second pass `verify_2010_2014_player_state_model.py --check` | `runtime/player_state.py`, `runtime/observables.py`; copied into the engine image (`Dockerfile.engine`) | In production |
| `2014_player_state_public.json` | [player-state study](../2010_2014_player_state_study.md) | Same builder | `runtime/player_state.py`; engine image | In production |
| `2014_player_state_manifest.json` | [player-state study](../2010_2014_player_state_study.md) | Same builder | `runtime/player_state.py`; engine image | In production |
| `2014_player_state_binding.json` | No library record; [runtime README, kernel 2014.6 release](../../runtime/README.md#kernel-20146-release-october-17-2026) | `scripts/bind_latent_season.py 2014`, from merged `main` only; `--check` compares with the service and writes nothing | `runtime/player_state.py`; evidence of the `player_state` gate in `runtime/season_readiness.json` | Bound October 17, 2026 |

## League rosters and schedules

| File | Record | Builder and check | Pin or reader | Status |
|---|---|---|---|---|
| `2013_schedule.json` | [2013 schedule](../2013_league_schedule.md) | `build_2013_schedule.py games.csv > 2013_schedule.json` (no `--check`) | `runtime/week_inputs.py`, `runtime/seasons.py`; `scripts/validate_repository.py` | Frozen 2013 schedule |
| `2013_week1_depth_charts.json` | [2013 Week 1 library](../2013_week1_depth_charts.md) | `build_2013_week1_depth_charts.py` (no `--check`) | `runtime/depth_library.py`; `docs/repository_map.json` | Frozen dated snapshot |
| `2013_postseason_slots.json` | [2013 postseason format](../2013_postseason_format_and_schedule.md) | No builder (researched by hand) | `runtime/postseason.py` | Frozen |
| `2014_week1_depth_charts.json` | [2014 Week 1 library](../2014_week1_depth_charts.md) | `build_2014_week1_depth_charts.py` (no `--check`) | `SeasonPaths(2014).background_depth` (`runtime/seasons.py`); tests | In use from September 7, 2014 |
| `2014_week1_rosters_source.json` | [Week 1 rosters](../2014_week1_rosters_branch_adjustment.md) | No builder (user supplied) | No reader | Source copy |
| `2014_week1_rosters_branch_adjusted.json` | [Week 1 rosters](../2014_week1_rosters_branch_adjustment.md) | No builder (branch-adjusted copy of the source) | `runtime/player_cards.py`; `build_2014_listed_player_identity.py` | Frozen |
| `2014_preseason_opponent_rosters.json` | [preseason opponent rosters](../2014_preseason_opponent_rosters.md) | `build_2014_preseason_opponent_rosters.py` (no `--check`) | Each game's frozen `Game_0N/opponent_roster.json`; tests | Frozen per game |
| `2014_inseason_rails/manifest.json`, `base.json`, `week_05.json`, `week_06.json`, `sources.json` | [in-season rails](../2014_inseason_rails.md) | `build_2014_inseason_rails.py SOURCE_DIR --through DATE` (first build), `--extend` (append), `--check` | `runtime/rails.py` and the weekly build | In use from Week 5 (October 5, 2014); built through October 11 |
| `2014_db_families.json` | [defensive-back families](../2014_db_families.md) | `build_2014_db_families.py --check` | `runtime/depth_library.py` (`db_families`) | In use from Week 5 (October 5, 2014), read by kernel 2014.6 |

**Rails check pitfall.** `build_2014_inseason_rails.py --check` hashes every file in `SOURCE_DIR`. It needs a source folder holding exactly the files pinned in the build it checks (the manifest's `builds[0].inputs` while the record has one build; the last build's inputs after an `--extend`). Keep later wire pages in a separate folder for `--extend`; otherwise the check reports the manifest stale even when every pinned input matches.

## Venues and conditions

| File | Record | Builder and check | Pin or reader | Status |
|---|---|---|---|---|
| `2014_conditions_calibration.json` | [context and conditions](../2014_context_and_conditions_calibration.md) | `build_2014_conditions_calibration.py --check` | No `runtime/` module names it; `tests/test_league_artifacts_2014_6.py` | Data only |
| `2014_venues.json` | [context and conditions](../2014_context_and_conditions_calibration.md) | Same builder | No `runtime/` module names it; tests | Data only |
| `2010_2013_venue_climatology.json` | [context and conditions](../2014_context_and_conditions_calibration.md) | Same builder | No `runtime/` module names it; tests | Data only |

## Players and identity

| File | Record | Builder and check | Pin or reader | Status |
|---|---|---|---|---|
| `player_birth_dates.json` | [birth dates](../2013_player_birth_dates.md) | `build_player_birth_dates.py SOURCE_DIR --checked-on DATE` (writes to stdout); `import_2014_week1_birth_dates.py [--write]` | `runtime/player_bios.py`, `runtime/player_cards.py`, `runtime/rails.py`; `scripts/render_player_ages.py` | Current registry |
| `player_birth_date_corrections.json` | [birth dates](../2013_player_birth_dates.md) | No builder (the third-source conflict review) | `build_player_birth_dates.py`; `runtime/player_cards.py` | Current |
| `player_photos.json` | [2014 Week 1 library](../2014_week1_depth_charts.md) | No builder in the repository (its `source` field names the user's Week 1 file) | `scripts/player_photos.py` | Identity imagery only |
| `2014_listed_player_identity.json` | [listed player identity](../2014_listed_player_identity.md) | `build_2014_listed_player_identity.py [SOURCE_DIR] --check` | `runtime/player_cards.py` | Reader data only |
| `2013_player_sheet_benchmarks.json` | [2013 player-sheet research](../2013_player_sheet_research.md) | `build_2013_player_sheet_benchmarks.py SOURCE_DIR` (no `--check`) | Named by player cards; nothing in `runtime/` | Research only |

## Coaching

| File | Record | Builder and check | Pin or reader | Status |
|---|---|---|---|---|
| `2012_hc_change_base_rates.json` | No library record; method [carousel_method.json](../../data/2014/Early_Offseason/staff_changes/carousel_method.json); cited by [the coaching career path](../nfl_coaching_career_path.md) | `build_hc_change_base_rates.py GAMES_CSV` (nfldata `games.csv`; the source digest is inside the JSON; no `--check`) | `scripts/coaching_carousel.py`; its digest is the closed carousel's `rates_sha256` | Frozen input of the closed January 2014 carousel |

## Defensive data, 2006 to 2013

| File | Record | Builder and check | Pin or reader | Status |
|---|---|---|---|---|
| `defense_2006_2013/defense_player_season_2006_2013.csv`, `defense_team_season_2006_2013.csv`, `defense_unclassified_players_2006_2013.csv` | [defensive data](../2006_2013_defense_data.md) | `build_defense_2006_2013.py RAW_DIR OUT_DIR` (no `--check`; the record lists each file's sha256) | Nothing in `runtime/` | Prepared, not used by the engine |
| `defense_2006_2013/data_dictionary.csv` | [defensive data](../2006_2013_defense_data.md) | `write_defense_2006_2013_dictionary.py OUT_DIR` | Nothing in `runtime/` | Prepared, not used by the engine |
