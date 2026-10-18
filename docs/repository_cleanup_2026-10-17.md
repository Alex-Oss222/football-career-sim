# Repository cleanup, October 17, 2026

The user asked for the repository to be cleaned up, its data and stale information verified, and the research organized so that the career can be replicated and moved from one year to the next. This page records what the cleanup changed, what it left alone on purpose and what still needs the user. It changed no football fact, rule, plan, game result or closed event record, and it did not touch `state/05_Current_Season_State.md`, whose bytes the private snapshot digest binds.

The audit labels (S, STALE, DATA, F, Y, LINK) are the finding identifiers of the cleanup audit; several findings named the same problem and were applied as one change.

## What was cleaned

### Uploads and retired tools moved to the archive

| Change | Evidence it was safe | Findings |
|---|---|---|
| `docs/football_snap_estimates (1)/` moved to `archive/uploads/2026-10-02_football_snap_estimates/` | Browser upload (commit 6fa033a). The only mention outside the folder is plain text in [the 2014 engine decisions](../runtime/2014_engine_decisions.md#the-uploaded-snap-estimates-and-evidence-builder-not-used-in-20146), which records that the estimates use full-season 2014 data beyond the information gate and are not used; no script, test or repository-map entry names the path. That sentence is unchanged and the archive index maps the old path | S01, F01 |
| `docs/free_nfl_evidence_build/free_nfl_evidence_build/` moved to `archive/uploads/2026-10-02_free_nfl_evidence_build/`, removing the duplicated folder level | Same upload commit; the decision record says the package is not adopted; nothing outside the folder names it; its tests sit outside `tests/`, so the suite never ran them | S02, DATA-05, F02 |
| `scripts/migrate_season_layout.py` and its test moved to `archive/scripts/` | The test was the script's only reference; the migration was applied in a953aa5; the layout helpers keep their own tests in `tests/test_season_layout.py`; new seasons are staged in the readable layout | F03 |
| `scripts/research/build_league_rails_rosters.py` deleted, with the one README sentence that described it | The whole file only exited with a migration message; git history keeps it | F04 |
| [Archive index](../archive/README.md) lists the uploads, the retired migration and the quarantined retirement audit | Index lines only | S11 |

### Stale status text corrected, with its source

| Change | Evidence | Findings |
|---|---|---|
| `AGENTS.md`, 2014 E1/E2 section: kernel 2014.6 is installed (`runtime/__init__.py`) and accepted by `runtime/season_readiness.json` | Both files read 2014.6. The rule sentence "No 2014 game is authorized while ... remain BLOCKED", the readiness instruction and season routing are byte-unchanged | STALE-01, DATA-03, F12 |
| `AGENTS.md`, 2014 film and training paragraph: the short paths are logical names under `career/2014/offseason`, with the physical folders named; two lowercase logical paths case-corrected to their files | The old base `career/2014/early_offseason` resolved to missing files; the new one resolves all seven through `runtime.season_layout`. No rule word changed | S08, STALE-14 |
| [Game readiness](../state/game_readiness.md): every public 2014 gate VERIFIED on kernel 2014.6; the October 1 status kept as a dated earlier record | `runtime/season_readiness.json` gates; an offline `check_game_readiness.py --season 2014` reports only the private-runtime probe | STALE-03 |
| [2014 checklist](../career/2014/Supporting_Records/readiness.md): the Engine, Tooling and League-inputs cells | `season_closure` and `legal_rosters` VERIFIED; kernel 2014.6 released October 17, 2026. The checkpoint line and per-week requirements were left for the Week 5 closure | STALE-04, Y15 |
| [2012 injury calibration](../library/2012_nfl_injury_calibration.md) status line | `runtime/injury_model.py` reads it and the 2012 base pins it. Its JSON, sha256-pinned, was not edited | STALE-06 |
| [2014 Week 1 library](../library/2014_week1_depth_charts.md) status token: in use from September 7, 2014 | Weeks 1 to 4 were built on it; the gate sentence its test reads is kept verbatim | STALE-09 |
| Training camp, preseason and schedule READMEs | Camp report complete through August 29; the cut to 53 executed August 30; all gates VERIFIED and four weeks closed | STALE-10, STALE-11, STALE-12 |
| [Runtime README](../runtime/README.md) names the installed kernel at the top; [defect register](../runtime/defect_register.md) heading reads "verified live September 30, 2026" | Release record of October 17, 2026; `tier1_engine` evidence. No anchor pointed at the old heading | STALE-15, STALE-16 |
| [Update workflow](update_workflow.md) weekly-inputs heading; [season structure](season_structure.md) notes the six 2014 battles resolved August 30 | Week 1 closed September 7; the battles index says no competition is open | STALE-17, STALE-18 |
| [Season handoff](../career/2014/07_Season_Review/README.md): seven game-release gates | `RELEASE_GATES` in `runtime/seasons.py`. The suggested link to a separate rollover page was not added, because the checklist went into the season-cycle guide instead | Y14 |
| [2015 calendar](../career/2015/Calendar.md) clock and E1/E2 lines | Document 5's clock; the 2014 kernels implement E1/E2. The sourced research file was not touched | Y16 |
| [Statistics storage README](../career/2014/05_Regular_Season/Statistics/records/README.md): status and an index of the generated views | 61 receipts and eight generated views existed beside a "no game has closed" line | S07 |
| Root README runtime row names the current kernel | `KERNEL_VERSION` in `runtime/__init__.py` | S05, F09 |
| Doubled period after the kickoff time in eleven future week pages (Weeks 6 to 10 and 12 to 17) | Hand-written pages; no generator | S13, Y19 |

### Tooling and path fixes

| Change | Evidence | Findings |
|---|---|---|
| [Run Week guide](run_week.md) and the `build_week_inputs.py` docstring name the season-routed call-sheet and inactives owners, with the 2014 and 2013 forms, and the call-sheet parts the 2014.6 builder reads | `SeasonPaths.week_folder`, `SeasonPaths.depth_chart` and the builder's own reading. The prompt block and season routing are unchanged | S09, STALE-13, F10, Y17 |
| `validate_repository.py` no longer regenerates `season_honours.md` as a side effect; `season_honours.py` gains a pure `render_text(root)`; a new test shows a stale copy is reported while neither tree changes | Before the fix a hand edit was reported once and silently repaired | F13 |
| The validator's draft-order message names the resolved file | Message text only | F20 |
| `close_preseason_game.py` imports `controlled_team_id` and `default_detail` from `close_week.py` | The local copies were byte-identical | F14 |
| Removed `test_repository_holds_before_the_flip` | It skips unless the kernel is 2014.5 and can never run again | F05 |
| The links on seven lines of the [March 2014 replay log](../career/2014/00_Team_Operations/Free_Agency/march_2014_replay_log.md) pinned to commit ddae28ca (six distinct paths) now name the paths that existed at that commit | `git cat-file -e` fails for the old paths and passes for the new ones at that commit; link text and record unchanged | LINK-01 |

### Indexes added

| Change | Findings |
|---|---|
| [library/README.md](../library/README.md): every record by information window, with its status, artifacts and builder | S06 |
| [library/data/README.md](../library/data/README.md): every data file's record, builder, check or pin, and status; how to reproduce the frozen strength v1 and v2; the rails `--check` source-folder pitfall | DATA-06, DATA-08, DATA-12 |
| [docs/README.md](README.md) and [scripts/README.md](../scripts/README.md), linked from the root README with a tests row | S09, S20, F09 |
| [2013 migrations index](../career/2013/migrations/README.md), noting the Week 1 helpers retired in e04dd82 and how to recover them | F16 |
| Draw script and pinned commit for each closed draw in the [early offseason](../career/2014/01_Early_Offseason/README.md) and [staff changes](../career/2014/01_Early_Offseason/staff_changes/README.md) READMEs (each commit's bytes match the results' `code_sha256`) | F06 |
| "Built by" lines for the 2013 honours evidence and the head-coach change base rates | F08 |
| The three unindexed 2013 files in the [2013 index](../career/2013/README.md); a file list, without summaries, in the hiring brief README | S20 |
| `.gitignore`: `.pytest_cache/`, `*.egg-info/`, `.DS_Store`, `readiness-report.txt` | S12 |

### Research and guides added

- [The NFL coaching career path](../library/nfl_coaching_career_path.md): the ladder from position coach to head coach under the 2013 to 2015 rules, with two research passes and their corrections.
- [Season cycle and career milestones](season_cycle_milestones.md): Stone's yearly cycle, his contract and review milestones, where each stops for the user, and the year-to-year checklist of existing commands and owners.

## Deliberately left

- `career/2014/05_Regular_Season/Games/Week_05/README.md` (its doubled period and its index of `Week_05_Pittsburgh.md`): the Run Week 5 branch owns the page.
- `state/05_Current_Season_State.md`: any byte change moves the snapshot digest (see STALE-05 below).
- `foundation/`: the rulebook is reported, never edited, in a cleanup (STALE-22).
- Closed records keep their wording: the 2013 migration records still name the retired helpers (indexed instead), and the sha256-pinned JSON files keep their out-of-date internal status strings (`2012_nfl_injury_calibration.json`, `2010_2014w4_nfl_injury_calibration.json`).
- `runtime/2014_engine_decisions.md` keeps the sentence naming the upload's original path, which truthfully records where the files were evaluated.
- The user-uploaded head-coach packets with spaces in their names inside the 2014 preseason and Week 1 to 4 game folders are part of those closed folders and were not renamed.
- Pre-existing em dashes in the future week-page headings and the root README's start line were not rewritten.
- Generated folders and views (`career/league_players/`, statistics, standings, award pages) were not hand-edited.

## Needs the user

| Finding | Problem | Recommendation |
|---|---|---|
| S10 | `docs/pr_132_followup_review.md` is a finished September 29 review, but `docs/repository_map.json` still requires it | Approve moving it to `archive/` and updating or dropping its required-files entry |
| S15, STALE-21 | `Supporting_Records/operating_baseline.md` reads "Current through July 29, 2014" with 78 controlled players and open defects, and it is cited as `legal_rosters` gate evidence | Relabel it as the July 29, 2014 baseline (no fact changes) and describe it that way in the Supporting Records README, rather than refreshing it |
| STALE-05 | Document 5 still names kernel 2014.5, lists closed defect items 7 and 8 as open and calls the Week 1 library gated | Fold the corrections into the Run Week 5 closure, which replaces Document 5 anyway |
| STALE-19 | Two VERIFIED gate records in `runtime/season_readiness.json` keep "remaining" clauses that have since been met | Approve appending a dated status sentence to each, changing no status, kernel or base field |
| STALE-20 | The release boundary and the runtime release record stop before recording step 7, the live `check_game_readiness.py --season 2014` from merged `main` | Once the live result is confirmed, append one dated line to each record |
| STALE-22 | Document 7 section 8 still gives the August 8, 2013 clock and only the 2012 calibration | Decide whether to authorize a rulebook update for the 2014 season and the 2014.6 base |
| DATA-01 | `build_2014_branch_identity.py --check` can no longer run on `main` because today's Week 5 dry build trips a later defensive-back guard | Keep `branch_identity.json` frozen; make the check reproduce its recorded dry-build basis, or mark it historical with the reason in the defect register |
| DATA-02, Y09 | `current_records.background_depth` still points at the 2013 Week 1 library, so the 2014 ages view lists other clubs' 2013 rosters | Choose the 2014 source (the 2014 Week 1 library or the rails as of the master date), repoint the key and regenerate with `render_player_ages.py`; the status-text correction can be made now |
| DATA-07 | Sixteen research builders have no `--check`, and two read live branch records, so their dated artifacts cannot be regenerated from a later `main` | Approve adding `--check` modes, starting with the artifacts the runtime reads; until then the data index lists their pins |
| F17 | The annual milestone tools are hardcoded to one season, and the market-draw curve lives only in two 2014 scripts | Schedule a later task to add `--season` and per-year method folders and a shared runtime module |
| Y02 | Nothing reports which per-season inputs exist before a rollover | Approve a read-only `scripts/season_rollover.py status YEAR` with its test |
| Y03 | 2014 cannot schedule its postseason: `library/data/2014_postseason_slots.json` and its research record do not exist | Research them in two passes (schedule facts only) before the Week 18 build, then make `runtime/postseason.py` season-neutral |
| Y04 | The honours, Pro Bowl and Super Bowl MVP tools are hardcoded to 2013, and no 2014 method is frozen | Add `--season` (default 2013, closed output byte-identical) and freeze the 2014 methods before any draw |
| Y06 | The draft order and pick ownership cover only the 2014 draft | Before the 2015 order is needed, add a season parameter and run a 2015 ownership audit |
| Y07 | No committed builder produces a season's `fixtures.json` in the schema the runtime requires | Add a schedule builder and run it at the April 21, 2015 release, not before |
| Y08 | The validator's season-record checks are hardcoded to 2014 | Refactor them into a per-season check that runs for every record year from 2014 |
| Y10 | January season-review events of 2013 carry no `season` field and appear in the 2014 record, unlike the Pro Bowl events | Decide whether season-closing January and February events belong to their NFL season; if so add only `"season": 2013` to those two comments and regenerate both records |
| Y18 | Future-week and award placeholder pages exist in 2014 with no generator | Choose between a week-page generator with the award placeholders dropped, and retiring the placeholders; record the choice in the year-to-year checklist |
| Y20 | The cap tracker embeds 2014 events in renderer code and branches on the 2014 year | Move the year-specific rows into the financial inputs, with `--check` proving no dollar figure changes |
| Y22 | Several `AGENTS.md` instructions are pinned to 2014 | At activation, approve year-neutral wording or a 2015 paragraph (the 2014 path note is already corrected) |
| Y23 | Staging skips an existing `career/Y+1/README.md`, and `career/2015/README.md` exists | Reconcile the 2015 README at activation; optionally have staging print the skipped path |

## Checks

Repository validation, `render_player_cards.py --check`, the focused test modules for every file touched and the stale-audit link checker were run on the result; the parent task runs the full suite.
