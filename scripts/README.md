# Scripts

Command-line tools, grouped by when they are used. Each line is taken from the script's own docstring and argument parser; the script's docstring is the full reference. The workflow that strings them together is in [docs/update_workflow.md](../docs/update_workflow.md), and `Run Week N` in [AGENTS.md](../AGENTS.md) owns the order for a regular-season week. Run repository scripts from the repository root.

A script that talks to the private Engine State service needs `ENGINE_RUNTIME_URL` and `ENGINE_API_TOKEN`. Never advance the private snapshot or bind player states from an unmerged branch.

## Checks

| Command | What it does |
|---|---|
| `python scripts/validate_repository.py [--root PATH]` | Read-only continuity checks across the repository |
| `python scripts/check_game_readiness.py [--season YEAR] [--preseason N] [--json]` | Fail-closed game preflight: public release gates, then the live private-runtime probe |
| `python scripts/check_week_input_exclusivity.py PACKAGE --expected-games COUNT [--season YEAR] [--roster PATH] [--protagonist NAME]` | Fails a weekly TeamInput slate that is incomplete or puts a player on two clubs |
| `python scripts/run_suite_parallel.py [REPO_DIR] [--jobs N] [--out LOG_DIR] [--durations PATH] [--only MODULE ...]` | The full unit-test suite, one module per process, proven to cover the same tests as `python -m unittest discover -s tests` (CI runs this) |

## A regular-season or postseason week

| Command | What it does |
|---|---|
| `python scripts/build_week_inputs.py WEEK --season YEAR` | Builds, freezes and gates the week's TeamInput package from Stone's frozen call sheet |
| `python scripts/close_week.py WEEK --season YEAR --close [--continue ANSWER.json]` | Closes every game of the week once through the production runner, writes the receipts and regenerates the statbook and standings |
| `python scripts/render_box_score.py [EVENT_ID] --season YEAR [--team TEAM] [--write OUTPUT_MD] [--line-score] [--preseason]` | Box score from a closed-game receipt, written into the marked block of a game output |
| `python scripts/render_standings.py YEAR [--through-week N]` | Standings from the receipts |
| `python scripts/render_season_stats.py YEAR --team TEAM` | The season statistics views from the receipts |
| `python scripts/render_team_tracker.py YEAR [--team TEAM] [--check]` | Jacksonville's team stat tracker from the receipts |
| `python scripts/league_awards.py week N --season YEAR [--close] [--note TEXT]` | Weekly awards: dry run, or the audited draw with `--close` |
| `python scripts/league_awards.py month NAME --season YEAR [--close]` | Monthly awards on the league's announcement date |
| `python scripts/league_awards.py render --season YEAR` | Rewrites the award pages |
| `python scripts/render_player_cards.py [--check] [--root PATH]` | League player cards under `career/league_players/` |
| `python scripts/update_player_cards.py YEAR [--check]` | Refreshes statistics on the working player cards without rewriting assessments |
| `python scripts/render_observables.py --season YEAR --week N [--check]` | Backfills or checks a closed week's participation observables |
| `python scripts/render_inseason_rails.py --season YEAR [--week N] [--write] [--check] [--event ID]` | One week's in-season rails page from the committed rails data |
| `python scripts/render_coach_record.py YEAR [--opponent NAME] [--date YYYY-MM-DD]` | Stone's head-coaching record table for the weekly Coach info block |
| `python scripts/render_player_ages.py [--check]` | Birth-date and age columns as of Document 5's master date |
| `python scripts/advance_private_snapshot.py CHECKPOINT` | From merged `main` only: advances the private snapshot to the current Document 5 digest |

## Preseason

| Command | What it does |
|---|---|
| `python scripts/close_preseason_game.py N --season YEAR [--close] [--continue ANSWER.json]` | Closes one Jacksonville preseason game through the production runner |
| `python scripts/render_preseason_stats.py --season YEAR` | Preseason statistics from the preseason receipts only |

## Records and current views

| Command | What it does |
|---|---|
| `python scripts/render_annual_record.py YEAR [--root PATH] [--check]` | The one-line annual `Record.md` from each event owner's metadata |
| `python scripts/render_career_views.py [--check]` | The career views (Document 5, the staff register's phase control, the head coach's desk) from the current-job record and the decision queue; writing is refused while a Jacksonville game is paused |
| `python scripts/render_trade_pages.py YEAR [--check]` | Trade navigation from the completed-trade index |
| `python scripts/render_jaguars_cap_tracker.py [--check]` | The twelve-year financial horizon from the contract inputs |
| `python scripts/render_draft_order.py [--check]` | The 2014 draft order from the closed receipts |
| `python scripts/render_2014_opponents.py [--check]` | The undated 2014 opponent matrix |
| `python scripts/resolve_compensatory_picks.py [--check]` | The branch 2014 compensatory picks (deterministic) |
| `python scripts/build_player_progression_roster.py [--roster PATH] [--exit-index PATH] [--output PATH] [--check]` | The offseason player-progression cohort from the live roster |
| `python scripts/refresh_summary_receipt.py PHASE [--reviewed]` | Acknowledges a reviewed phase summary; never writes football observations |
| `python scripts/bind_latent_season.py YEAR [--check]` | From merged `main` only: binds a league year's player states in the private service and writes `library/data/YEAR_player_state_binding.json` |

## Season close and the next season

| Command | What it does |
|---|---|
| `python scripts/season_handoff.py prepare\|check\|stage\|check-opening\|review-opening SEASON` | Prepares, checks and stages the annual handoff; never simulates or changes live owners |
| `python scripts/build_annual_player_sheets.py --season YEAR [--check] [--review] [--force]` | Creates or checks the frozen end-of-season player sheets |
| `python scripts/season_honours.py [render] [--close] [--entry TEXT]` | 2013 season honours (built for the 2013 season) |
| `python scripts/pro_bowl.py draft\|game\|render [--close] [--entry TEXT]` | The 2014 Pro Bowl of the 2013 season |
| `python scripts/super_bowl_mvp.py [--close] [--entry TEXT]` | Super Bowl XLVIII MVP of the 2013 season |

## Closed one-off draws

Each script below drew once. Its results file pins the drawing script's bytes as `code_sha256`, and each refuses a second `--close`. To verify a draw, compare `git show COMMIT:scripts/NAME.py | sha256sum` with the results file.

| Script | Results | Commit whose bytes match `code_sha256` | Later edits |
|---|---|---|---|
| `futures_2014.py [--close] [--entry TEXT]` | `career/2014/01_Early_Offseason/futures_results.json` | 8f85462 | Paths only |
| `league_year_2014.py [--close] [--entry TEXT]` | `career/2014/01_Early_Offseason/league_year_results.json` | 34c5986 | Paths only |
| `coaching_carousel.py [render] [--close] [--entry TEXT]` | `career/2014/01_Early_Offseason/staff_changes/carousel_results.json` | 35f1276 | Paths and the page renderer; the draw code is unchanged |
| `coaching_carousel_deferred.py [render] [--close] [--entry TEXT]` | `career/2014/01_Early_Offseason/staff_changes/carousel_deferred_results.json` | b8812d2 (its `entry75_code_sha256` matches `coaching_carousel.py` at 42f785d) | Paths only |
| `st_coordinator_search.py [--close] [--entry TEXT]` | `career/2014/01_Early_Offseason/staff_changes/st_search_results.json` | 10ba5f7 | Paths only |
| `recover_injury_projection.py [--close]` | `career/2013/migrations/injury_projection_recovery.json` | Not pinned | |
| `void_week_generation.py WEEK` | Marks voided generations listed in `career/2013/migrations/event_generations.json` | Not pinned | |

## Private service and shared modules

- `serve_private_runtime.py`: the Engine State container entry point; secrets and storage stay outside the repository.
- `render_award_pages.py` and `player_photos.py`: modules imported by other scripts (award cards; open-licensed photo registry), not commands.

## Research builders (`scripts/research/`)

Research tools only; the runtime never downloads anything. Each builder's artifact and library record are indexed in [library/data/README.md](../library/data/README.md). A builder with `--check` rebuilds in memory and compares with the committed file without writing.

| Builder | Writes | Record |
|---|---|---|
| `sources_2010_2014.py --fetch --dest DIR [--only NAME ...] [--write-manifest] [--repin]`; `--check [--dest DIR]` | The 2014.6 sources manifest and gate (not a builder of football data) | [calibration base](../library/2010_2014_calibration_base.md) |
| `build_2010_2014_league_base.py [--seasons 2010-2014w4\|2012] [--sources DIR] [--stage core\|annotations\|all] [--check]` | 2010-2014 field-position, drive and aggregate models | [calibration base](../library/2010_2014_calibration_base.md) |
| `build_2010_2014_injury_calibration.py [--sources DIR] [--check]` | 2010-2014 injury calibration | [calibration base](../library/2010_2014_calibration_base.md) |
| `build_2010_2014_usage_baseline.py [--sources DIR] [--check]` | 2010-2014 position usage | [calibration base](../library/2010_2014_calibration_base.md) |
| `build_2013_2014_participation_structure.py [--sources DIR] [--check]` | Participation structure (informational) | [calibration base](../library/2010_2014_calibration_base.md) |
| `build_2010_2014_scoring_decisions.py [--seasons 2010-2014w4\|2012] [--sources DIR] [--check]` | Scoring decisions | [scoring decisions](../library/2010_2014_scoring_decisions_calibration.md) |
| `build_2010_2014_fourth_down_decisions.py [--sources DIR] [--check]` | Fourth-down decisions | [fourth downs](../library/2010_2014_fourth_down_calibration.md) |
| `build_2010_2014_ball_security.py [--sources DIR] [--check]` | Ball security | [ball security](../library/2010_2014_ball_security_calibration.md) |
| `build_2010_2014_penalties.py [--sources DIR] [--check]` | Penalties | [penalties](../library/2010_2014_penalty_calibration.md) |
| `build_2010_2014_yardage.py [--sources DIR] [--check]` | Yardage | [yardage](../library/2010_2014_yardage_calibration.md) |
| `build_2014_conditions_calibration.py [--sources DIR] [--check] [--jobs N]` | Conditions, venues and climatology | [context and conditions](../library/2014_context_and_conditions_calibration.md) |
| `build_2010_2014_player_state_model.py [--sources DIR] [--check]`; pass 2 `verify_2010_2014_player_state_model.py [--sources DIR] [--check]` | Player-state model, public table and manifest | [player-state study](../library/2010_2014_player_state_study.md) |
| `build_2014_branch_identity.py [--sources DIR] [--week N] [--check]` | `career/2014/League/personnel/branch_identity.json` | [personnel](../career/2014/League/personnel/README.md) |
| `build_2014_strength_calibration.py SOURCE_DIR PBP_2012 [PBP_2011]`, `build_2014_strength_calibration_v2.py SOURCE_DIR PBP_2012`, `build_2014_strength_calibration_v3.py SOURCE_DIR`, `build_2014_strength_calibration_v4.py [--sources DIR] [--check]` | Strength calibrations v1 to v4 | [strength calibration](../library/2014_strength_calibration.md) |
| `build_2010_2012_honours_evidence.py HONOURS_JSON SOURCE_DIR` | 2010-2012 honours evidence | [honours evidence](../library/2010_2012_honours_evidence.md) |
| `build_2010_2012_production_evidence.py SOURCE_DIR` | 2010-2012 production evidence | [production evidence](../library/2010_2012_production_evidence.md) |
| `build_passer_interception_persistence.py SOURCE_DIR`; second pass `verify_passer_interception_persistence.py SOURCE_DIR` | Interception persistence study data | [study](../library/passer_interception_persistence_study.md) |
| `build_2012_drive_model.py [--sources DIR] [--out PATH] [--check]` | 2012 drive model | [drive model](../library/2012_drive_model_calibration.md) |
| `build_2012_field_position_model.py [--sources DIR] [--out PATH] [--check]` | 2012 field-position model | [field-position model](../library/2012_field_position_model_calibration.md) |
| `build_2012_usage_baseline.py SOURCE_DIR` | 2012 position usage | [position usage](../library/2012_position_usage_calibration.md) |
| `build_2012_injury_calibration.py SOURCE_DIR` | 2012 injury calibration | [injury calibration](../library/2012_nfl_injury_calibration.md) |
| `build_2013_schedule.py games.csv` | 2013 schedule (stdout) | [2013 schedule](../library/2013_league_schedule.md) |
| `build_2013_week1_depth_charts.py SOURCE_DIR` | 2013 Week 1 library (stdout) | [2013 Week 1 library](../library/2013_week1_depth_charts.md) |
| `build_2014_week1_depth_charts.py SOURCE_DIR` | 2014 Week 1 library (stdout) | [2014 Week 1 library](../library/2014_week1_depth_charts.md) |
| `build_2014_preseason_opponent_rosters.py [WORKSPACE]` | Preseason opponent rosters (stdout) | [preseason opponents](../library/2014_preseason_opponent_rosters.md) |
| `build_2014_inseason_rails.py SOURCE_DIR --through DATE [--extend] [--check]` | In-season rails | [in-season rails](../library/2014_inseason_rails.md) |
| `build_2014_db_families.py [--sources DIR] [--check]` | Defensive-back families | [defensive-back families](../library/2014_db_families.md) |
| `build_2014_listed_player_identity.py [SOURCE_DIR] [--check]` | Listed player identity | [listed identity](../library/2014_listed_player_identity.md) |
| `build_league_player_database.py [--source-dir DIR --capture --checked-on DATE] [--check] [--root PATH]` | 2013 league research inventory | [personnel](../career/2014/League/personnel/README.md) |
| `build_player_birth_dates.py SOURCE_DIR --checked-on DATE`; `import_2014_week1_birth_dates.py [--write]` | Birth-date registry | [birth dates](../library/2013_player_birth_dates.md) |
| `build_2013_player_sheet_benchmarks.py SOURCE_DIR`; `complete_2013_player_sheets.py [--check]` | 2013 player-sheet references and sheets | [player-sheet research](../library/2013_player_sheet_research.md) |
| `build_2013_honours_evidence.py SOURCE_DIR PACKAGE...` | `career/2013/awards/season_honours_evidence.json`; needs the frozen 2013 weekly packages from `.sim_cache`, so a fresh session cannot rerun it | [2013 awards](../career/2013/awards/README.md) |
| `build_2014_compensatory_inputs.py` | `career/2014/03_Draft/compensatory/inputs.json` | [compensatory picks](../career/2014/03_Draft/compensatory/README.md) |
| `build_hc_change_base_rates.py GAMES_CSV` | `library/data/2012_hc_change_base_rates.json` | [staff changes](../career/2014/01_Early_Offseason/staff_changes/README.md) |
| `build_defense_2006_2013.py RAW_DIR OUT_DIR`; `write_defense_2006_2013_dictionary.py OUT_DIR` | 2006-2013 defensive datasets | [defensive data](../library/2006_2013_defense_data.md) |

Specification and acceptance tools: `pre_build_specification.py [--check]` and `fourth_down_specification.py [--check]` print or verify the pinned digests of the frozen 2014.6 specifications; `acceptance_2014_6.py --block BLOCK ...` and `seed_sweep.py [--block BLOCK] ...` run the committed acceptance and seed sweeps; `release_preconditions_2014_6.py [--season YEAR] [--week N] [--journal LISTING.json] [--release] [--json]` checks the 2014.6 release preconditions read-only. `league_base_2010_2014.py` and `player_state_study.py` are modules used by the builders, not commands.
