# Library

Sourced research for the career. Each record states its own research date, information window and status at the top. This page is an index only: it names each record, gives its status (from the record's own header, or from the code that pins or reads it where the header predates a release) and points to its machine artifact and builder. It copies no finding and adds no number.

**Reading rule (AGENTS.md).** Read only the record a task names, and only the section it needs. A record becomes usable only on the information date it states; a prepared or gated record informs no evaluation, board or decision before then. Records of real later outcomes are quarantined in the [archive](../archive/README.md) and are never a runtime input.

**Machine artifacts.** The JSON and CSV files the records describe are in [data/](data/README.md), which lists each file's record, builder, check command or pin, and status. Raw downloads stay out of the repository; [raw/DATA_REQUEST.md](raw/DATA_REQUEST.md) lists the only data the user supplies. Builders live in `scripts/research/` ([scripts index](../scripts/README.md)).

## 2006 to 2013: defensive data

| Record | Subject | Status | Artifacts and builder |
|---|---|---|---|
| [2006_2013_defense_data.md](2006_2013_defense_data.md) | Free defensive data, 2006 to 2013 | Prepared, not used by the engine | `data/defense_2006_2013/`; `build_defense_2006_2013.py`, `write_defense_2006_2013_dictionary.py` |

## 2010 to 2014: league calibration base and pre-divergence evidence (kernel 2014.6)

The 2010 to 2014 window covers the regular seasons 2010 to 2013 and 2014 Weeks 1 to 4, read through the information gate in `scripts/research/sources_2010_2014.py`. Kernel 2014.6 pins these artifacts through `runtime/calibration_base.py` (base `2010_2014w4`).

| Record | Subject | Status | Artifacts and builder |
|---|---|---|---|
| [2010_2014_calibration_base.md](2010_2014_calibration_base.md) | The league base: field-position model, drive model, aggregate baseline, injury and usage calibrations, sources manifest | Pinned by the 2014.6 base | `data/2010_2014w4_nfl_*.json`, `data/2010_2014_sources_manifest.json`, `data/2013_2014_participation_structure.json`; `build_2010_2014_league_base.py`, `build_2010_2014_injury_calibration.py`, `build_2010_2014_usage_baseline.py`, `build_2013_2014_participation_structure.py` |
| [2010_2014_scoring_decisions_calibration.md](2010_2014_scoring_decisions_calibration.md) | Tries, two-point success, onside kicks, return touchdowns | Pinned by the 2014.6 base | `data/2010_2014w4_scoring_decisions.json`; `build_2010_2014_scoring_decisions.py` |
| [2010_2014_fourth_down_calibration.md](2010_2014_fourth_down_calibration.md) | Fourth-down decision chart and conversion records | Pinned by the 2014.6 base | `data/2010_2014w4_fourth_down_decisions.json`; `build_2010_2014_fourth_down_decisions.py` |
| [2014_6_fourth_down_specification.md](2014_6_fourth_down_specification.md) | Fourth-down rules frozen before their rates were counted | Frozen; pinned by `fourth_down_specification.py` | None |
| [2010_2014_ball_security_calibration.md](2010_2014_ball_security_calibration.md) | Fumbles, muffs and kicking-team recoveries | Pinned by the 2014.6 base | `data/2010_2014w4_ball_security.json`; `build_2010_2014_ball_security.py` |
| [2010_2014_penalty_calibration.md](2010_2014_penalty_calibration.md) | Per-play penalty records | Pinned by the 2014.6 base | `data/2010_2014w4_penalties.json`; `build_2010_2014_penalties.py` |
| [2010_2014_yardage_calibration.md](2010_2014_yardage_calibration.md) | The yard split and its band rows | Pinned by the 2014.6 base | `data/2010_2014w4_yardage.json`; `build_2010_2014_yardage.py` |
| [2014_context_and_conditions_calibration.md](2014_context_and_conditions_calibration.md) | Weather and venue terms | Data only; its reader is planned for a later batch | `data/2014_conditions_calibration.json`, `data/2014_venues.json`, `data/2010_2013_venue_climatology.json`; `build_2014_conditions_calibration.py` |
| [2010_2014_player_state_study.md](2010_2014_player_state_study.md) | The player-state model: hidden priors for the engine only, never a staff grade | In production for 2014.6 | `data/2010_2014_player_state_model.json`, `data/2014_player_state_public.json`, `data/2014_player_state_manifest.json`; `build_2010_2014_player_state_model.py`, `verify_2010_2014_player_state_model.py` |
| [2014_6_pre_build_specification.md](2014_6_pre_build_specification.md) | Fixed rules for every 2014.6 builder, fit and acceptance run; by its own label not a blind preregistration | Frozen; pinned by `pre_build_specification.py` and the 2014.6 base | None |
| [2010_2012_honours_evidence.md](2010_2012_honours_evidence.md) | Public honours announced before the January 15, 2013 divergence | Research evidence for team strength | `data/2010_2012_honours_evidence.json`; `build_2010_2012_honours_evidence.py` |
| [2010_2012_production_evidence.md](2010_2012_production_evidence.md) | Pre-divergence production evidence | Research and data | `data/2010_2012_production_evidence.json`; `build_2010_2012_production_evidence.py` |
| [2014_strength_calibration.md](2014_strength_calibration.md) | Unit-strength calibrations, first pass to v4 | Research and data | `data/2014_strength_calibration.json`, `_v2`, `_v3`, `_v4`; `build_2014_strength_calibration.py`, `_v2.py`, `_v3.py`, `_v4.py` |
| [passer_interception_persistence_study.md](passer_interception_persistence_study.md) | Individual passer interception-rate persistence, 2010 to 2014 | Research only; nothing in `runtime/` reads it | `data/passer_interception_persistence.json`; `build_passer_interception_persistence.py`, `verify_passer_interception_persistence.py` |

## 2012: calibration for the 2013 season and kernels through 2014.5

These artifacts are pinned by the 2012 base in `runtime/calibration_base.py`, which serves every kernel through 2014.5: the 2013 season and 2014 Weeks 1 to 4.

| Record | Subject | Status | Artifacts and builder |
|---|---|---|---|
| [2012_game_calibration.md](2012_game_calibration.md) | Aggregate inputs for 2013 game calibration | Verified for the 2013 runtime | `data/2012_nfl_aggregate_baseline.json`; no builder in the repository |
| [2012_drive_model_calibration.md](2012_drive_model_calibration.md) | Offensive-drive model | Reconciled; second pass passed | `data/2012_nfl_drive_model.json`; `build_2012_drive_model.py` |
| [2012_field_position_model_calibration.md](2012_field_position_model_calibration.md) | Field-position drive model | Reconciled; second pass passed | `data/2012_nfl_field_position_model.json`; `build_2012_field_position_model.py` |
| [2012_position_usage_calibration.md](2012_position_usage_calibration.md) | Position usage and drive volume | Verified for the 2013 runtime | `data/2012_nfl_position_usage_baseline.json`; `build_2012_usage_baseline.py` |
| [2012_nfl_injury_calibration.md](2012_nfl_injury_calibration.md) | Injury calibration | In production for kernels 2014.4 and 2014.5 | `data/2012_nfl_injury_calibration.json`; `build_2012_injury_calibration.py` |

## 2013 season

| Record | Subject | Status | Artifacts and builder |
|---|---|---|---|
| [2013_coaching_market_pre_hire.md](2013_coaching_market_pre_hire.md) | Head-coaching market, January 14, 2013 snapshot | Researched and verified; the hiring-search input | None |
| [alex_stone_character_dossier_pre_hire.md](alex_stone_character_dossier_pre_hire.md) | Stone's pre-hire background and evidence boundaries | Supporting reference for the January 2013 search | None |
| [2013_jacksonville_master_calendar.md](2013_jacksonville_master_calendar.md) | Jacksonville's 2013 master calendar | Verified historical calendar | None |
| [2013_offseason_program_calendar.md](2013_offseason_program_calendar.md) | 2013 offseason-program calendar | Superseded by the master calendar; kept as a compatibility path | None |
| [2013_league_calendar_and_financial_rules.md](2013_league_calendar_and_financial_rules.md) | League calendar and financial rules | Researched and verified; backs Document 2 | None |
| [2013_league_schedule.md](2013_league_schedule.md) | Regular-season schedule (no scores) | Verified | `data/2013_schedule.json`; `build_2013_schedule.py` |
| [2013_playing_rules.md](2013_playing_rules.md) | Playing-rule verification | Supports Document 2; not a second rule authority | None |
| [2013_nfl_playing_rules_for_simulation.md](2013_nfl_playing_rules_for_simulation.md) | The playing rules the game kernel models | Researched and verified | None |
| [2013_suspension_reinstatement_rules.md](2013_suspension_reinstatement_rules.md) | Suspension completion and reinstatement | Researched and verified | None |
| [2013_week1_depth_charts.md](2013_week1_depth_charts.md) | Week 1 depth charts for the 31 background clubs | Verified for the 2013 TeamInputs | `data/2013_week1_depth_charts.json`; `build_2013_week1_depth_charts.py` |
| [2013_draft_class.md](2013_draft_class.md) | 2013 draft class, pre-selection snapshot | Researched and verified | None |
| [2013_draft_information_gates.md](2013_draft_information_gates.md) | 2013 draft information gates | Runtime date-gating companion | None |
| [2013_draft_pool_registry.md](2013_draft_pool_registry.md) | 2013 draft pool registry | Pre-selection eligibility registry | None |
| [2013_postseason_format_and_schedule.md](2013_postseason_format_and_schedule.md) | Postseason format, seeding and time slots | Researched and verified | `data/2013_postseason_slots.json`; no builder |
| [2013_nfl_awards_structure.md](2013_nfl_awards_structure.md) | Weekly, monthly and season award structure and calendar | Researched and verified | None |
| [2013_season_honours_selection_structure.md](2013_season_honours_selection_structure.md) | Pro Bowl, AP All-Pro and AP award selection structure | Researched and verified | None |
| [2013_super_bowl_mvp_and_pro_bowl_procedure.md](2013_super_bowl_mvp_and_pro_bowl_procedure.md) | Super Bowl MVP and Pro Bowl procedure | Researched and verified | None |
| [2013_player_sheet_research.md](2013_player_sheet_research.md) | Research behind the 2013 player sheets | Complete for the 2013 sheets | `data/2013_player_sheet_benchmarks.json`; `build_2013_player_sheet_benchmarks.py`, `complete_2013_player_sheets.py` |
| [2013_player_birth_dates.md](2013_player_birth_dates.md) | Player birth dates and simulation ages (2013 and 2014 rosters) | Birth date and identity only | `data/player_birth_dates.json`, `data/player_birth_date_corrections.json`; `build_player_birth_dates.py`, `import_2014_week1_birth_dates.py` |

## 2014 season

| Record | Subject | Status | Artifacts and builder |
|---|---|---|---|
| [2014_nfl_calendar.md](2014_nfl_calendar.md) | League calendar for 2014 and its postseason | Researched and checked | None |
| [2014_full_calendar_verification.md](2014_full_calendar_verification.md) | Compatibility link to the 2014 calendar | Stub | None |
| [2014_league_calendar_and_financial_rules.md](2014_league_calendar_and_financial_rules.md) | Salary cap, contract, tender and draft-order rules | Research with Confirmed and Unverified labels | None |
| [2014_playing_and_roster_rules.md](2014_playing_and_roster_rules.md) | Playing and roster rules | Researched and verified; backs Document 2 | None |
| [2014_offseason_phase_rules_verification.md](2014_offseason_phase_rules_verification.md) | Offseason phase activity rules | Research only | None |
| [2014_coaching_hiring_and_anti_tampering_rules.md](2014_coaching_hiring_and_anti_tampering_rules.md) | Coach hiring and anti-tampering rules, January 2014 cycle | Researched and verified | None |
| [2014_jaguars_original_contract_reconstruction.md](2014_jaguars_original_contract_reconstruction.md) | Jaguars original contracts carried into 2014 | Supplemented by the contract completion | None |
| [2014_jaguars_contract_completion.md](2014_jaguars_contract_completion.md) | Completing Jacksonville's existing contracts | User-authorized labelled simulation terms | None |
| [2014_draft_information_gates.md](2014_draft_information_gates.md) | 2014 draft information gates | Runtime date-gating companion | None |
| [2014_draft_pool_registry.md](2014_draft_pool_registry.md) | 2014 draft pool registry | Focus prospects only; full class not built | None |
| [2014_combine_results.md](2014_combine_results.md) | Combine results for Jacksonville's board | Pre-selection evidence | None |
| [2014_prospect_evidence/README.md](2014_prospect_evidence/README.md) | Individual prospect evidence files | Pre-selection evidence | None |
| [2014_draft_order_verification.md](2014_draft_order_verification.md) | Draft order rule and ownership verification | Superseded in part by the ownership audit it names | None |
| [2014_week1_rosters_branch_adjustment.md](2014_week1_rosters_branch_adjustment.md) | Real Week 1 rosters and the branch-adjusted copy | User-supplied source; branch-adjusted | `data/2014_week1_rosters_source.json`, `data/2014_week1_rosters_branch_adjusted.json`; no builder |
| [2014_week1_depth_charts.md](2014_week1_depth_charts.md) | Week 1 depth charts for the 31 background clubs | In use from September 7, 2014 | `data/2014_week1_depth_charts.json`; `build_2014_week1_depth_charts.py` |
| [2014_preseason_opponent_rosters.md](2014_preseason_opponent_rosters.md) | Each preseason opponent's camp roster | Prepared research; each game froze its own copy | `data/2014_preseason_opponent_rosters.json`; `build_2014_preseason_opponent_rosters.py` |
| [2014_inseason_rails.md](2014_inseason_rails.md) | Other clubs' in-season roster moves | In use from Week 5 (October 5, 2014); built through October 4 | `data/2014_inseason_rails/`; `build_2014_inseason_rails.py` |
| [2014_db_families.md](2014_db_families.md) | Defensive-back families for the background clubs | In use from Week 5 (October 5, 2014), read by kernel 2014.6 | `data/2014_db_families.json`; `build_2014_db_families.py` |
| [2014_listed_player_identity.md](2014_listed_player_identity.md) | Listed height, weight, college and number for the player cards | Reader data only | `data/2014_listed_player_identity.json`; `build_2014_listed_player_identity.py` |

## 2015 season

| Record | Subject | Status | Artifacts and builder |
|---|---|---|---|
| [2015_historical_calendar.md](2015_historical_calendar.md) | The real 2015 calendar: sources and verification | Researched ahead; advances no clock | None |

## Coaching careers (2013 to 2015 rules)

| Record | Subject | Status | Artifacts and builder |
|---|---|---|---|
| [nfl_coaching_career_path.md](nfl_coaching_career_path.md) | The NFL coaching ladder from position coach to head coach: rungs, timelines, the hiring cycle, contracts, failure points and the stops that need the user | Research only; two passes and a user-sourced verification pass, with Confirmed, Pattern, Unverified, Later and Real history labels | None |
| [nfl_head_coach_contracts_2005_2014.md](nfl_head_coach_contracts_2005_2014.md) | NFL head-coach contracts and extensions, real practice 2005 to January 2014: extension timing, lengths, reported salaries, guarantees, offsets, dismissal costs and assistants' contracts when the head coach goes | Research only; two passes (pass 2 a separate skeptical verification), with Confirmed, Corrected, Unverified and Derived labels; the basis cited by the reconstructed terms of Stone's contract | None |

## Methods

| Record | Subject | Status |
|---|---|---|
| [annual_player_sheet_benchmark_method.md](annual_player_sheet_benchmark_method.md) | Historical benchmark method for annual player sheets | Method |
| [player_development_research.md](player_development_research.md) | Research behind the player-progression model | Supporting note |
| [raw/DATA_REQUEST.md](raw/DATA_REQUEST.md) | The data the user supplies, and how | Request list |
