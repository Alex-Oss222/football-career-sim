# Keeping the career records current

The current checkpoint is owned by [Document 5](../state/05_Current_Season_State.md) and the latest closed [season-ledger entry](../career/2013/ledger.md). The [repository map](repository_map.json) records paths and dependencies, not a second set of football facts.

## Which files change together

| Event | First record | Dependent views to inspect and update when affected |
|---|---|---|
| Practice or camp work | Phase `output.md`, then ledger | Phase `standouts.md`; roster/register availability and role evidence; current state; calendar status; camp battles/decisions if a decision occurred |
| Signing, release, trade or drafted contract | Applicable signing/trade/draftee result, then ledger | Roster; cap/contract worksheet; pick ownership; Documents 4 and 5 |
| Outside staff interview request, permission, interview, offer or refusal | Applicable dated request/outcome record and ledger; preserve frozen carousel artifacts | Current season's staff timeline and overview; calendar and Document 5 when their pending decisions change; staff employment and payroll change only if an actual event changes them |
| Staff appointment, departure or delegation | Staff hiring/departure record and ledger | Current coaching staff and contract totals; Document 4; Document 3 if authority/delegation or current-incumbent pointers change; Document 5; current season's staff timeline, overview, hiring record and calendar |
| Final regular-season game | Game output and ledger | Full public game receipt for Jacksonville (player stats + snap ledger + named-call stats) and a `compact_stats` receipt for each background game; background roundup `career/YEAR/league_results/week_NN.md`; the week's league awards (`scripts/league_awards.py week N --close`, plus the month's when due) in `career/YEAR/awards/`; generated box score in the week's output; regenerated statbook and standings; read `stats/calibration_audit.md` (investigate OUTSIDE rows, never rerun); the week's frozen `call_sheet.json`, committed as frozen; `career/YEAR/depth_chart.json` (order and inactives) when Stone changes either; medical/availability; Documents 4 and 5; calendar |
| Preseason game | Preseason output and ledger | Same affected personnel/statistical views; regular-season standings stay unchanged |
| Bye or administrative correction | Applicable note and ledger | Only facts actually changed; no phantom game, practice, injury or roster move |
| Foundation correction | Ledger correction staged first | Named foundation document; source-version manifest; affected current views and readiness |

Plans own teaching intent. Outputs own what happened. Standouts are evidence summaries of outputs, never a second event source or a permanent depth chart. Initial roster/cap sheets preserve the starting baseline; the current roster and cap worksheet own later changes. An older financial effective date remains correct when no financial event occurred.

For 2014, the staff front door is [the staff-change folder](../career/2014/offseason/staff_changes/README.md). Its [timeline](../career/2014/offseason/staff_changes/timeline.md) summarizes dated outside requests and Jacksonville's [hiring outcomes](../career/2014/offseason/staff_changes/hires.md). Update these views in the same commit as a relevant closed event. The [plan](../career/2014/offseason/staff_changes/staff_plan.md) retains Stone's targets and proposed terms; do not rewrite it into a result log.

## Close an event

1. Read the current state, calendar, applicable plan and source records. Respect the active playbook lock. For a weekly football slate, `python scripts/build_week_inputs.py N` freezes the full transient TeamInput package and runs the exclusivity and game-day gate with the week's scheduled game count, so a partial slate fails, before any event closes; branch player control overrides historical roster rails. Run `scripts/check_week_input_exclusivity.py <weekly-input-package.json> --expected-games <scheduled-game-count>` directly only for an ad-hoc package.
2. Write the event/result and stage its ledger entry. Preserve earlier dated entries verbatim; append a correction when needed.
3. Review each dependency above. Update affected owners and summaries in the same commit. For a closed Jacksonville/protagonist regular-season or postseason game, preserve the full public receipt including player dictionaries, snap ledger and named-call usage. For ordinary background games, preserve the compact_stats receipt with every nonzero generated player/team statistic and every game-day active player, without background snap rows or zero-valued counters. Generate the box score, standings and season stat views from the receipt set; do not hand-add totals or reconstruct missing plays from prior Markdown. Do not touch unrelated financial or historical records to manufacture freshness.
4. Update Documents 4 and 5 checkpoints/versions consistently. Document 4 may retain its older content version if none of its owned facts changed; Document 5 must name that exact version. Refresh foundation Git-blob hashes in Document 5 after a foundation change, using `git hash-object` on each changed foundation source.
5. Update phase metadata and review the actual summary text. Only then run the receipt command below. It acknowledges review of the current source; it does not generate observations or prove prose is correct.
6. Refresh DOB/age columns and the league age view with `python scripts/render_player_ages.py` after any master-date or roster change, including birthdays within a season and January postseason dates. Verify a new player's identity and birth date before preparing his first game; never substitute an experience count or current real-world age. Then close the ledger entry, run validation and review the diff. Commit the entire dependency set together through a pull request.

```sh
python scripts/refresh_summary_receipt.py otas --reviewed
# A regular-season week: freeze inputs, close the games, then generate every view
# python scripts/build_week_inputs.py WEEK
# python scripts/close_week.py WEEK --close
# After a game, once the complete receipt set for the current coverage window exists:
# python scripts/render_box_score.py --write career/YEAR/regular_season/week_NN_<away>_at_<home>/output.md
# python scripts/render_standings.py YEAR
# python scripts/render_season_stats.py YEAR --team TEAM_ID
python scripts/render_player_ages.py
python scripts/validate_repository.py
python -m unittest discover -s tests -v
```

The receipt command supports the phase names in `repository_map.json`. Metadata uses `NOT_STARTED`, `IN_PROGRESS`, or `COMPLETE`, an ISO evidence-through date, and the source event's ledger entry number. Future phases use null date/entry. A summary holds the SHA-256 of its source output, so editing that output makes an unreviewed summary fail validation. Update metadata when appending actual work; never stamp a future phase complete just to pass a check.

## Validation scope

Checks cover required files, local Markdown targets/anchors, current-state source hashes, closed checkpoint continuity, controlled-player membership/counts, phase evidence receipts, that every regular-season week with any game receipt has exactly one receipt per scheduled game (`library/data/2013_schedule.json`), and that the statbook, standings and every filled box score match a fresh rebuild from the game receipts. Archived material and future playbook contents are excluded from reads. Templates and code examples are not live records.

These checks cannot judge football truth, medical evidence, a cap calculation, or whether a summary faithfully captures every observation. Human/agent review against the source remains required. CI does not automatically simulate events or rewrite state.

## One-command regular-season weeks

For regular-season play, `Run Week N` is the top-level workflow defined in `AGENTS.md`. Internal readiness, authorized migration/reset preparation, background-team input construction, receipt/statbook rebuild, standings, snapshot advancement and PR bookkeeping belong to that task; do not hand those implementation steps back to the user. A genuinely new Stone decision may still require user input when no supplied or already-closed plan covers it.

See `docs/run_week.md` for the minimal runner handoff prompt.

## Postseason rounds

The postseason uses the same one-command workflow, with weeks numbered 18 (Wild Card), 19 (Divisional), 20 (Conference) and 21 (Super Bowl); a request such as "Run the Wild Card" means `Run Week 18`. The round's games come from `runtime/postseason.py` (seeds from the final standings, the real 2013-14 slot by seed matchup, a round built only after the previous one closed). The differences from a regular-season week:

- Jacksonville's folder is `career/2013/postseason/week_NN_<away>_at_<home>/` (`output.md` and the frozen `call_sheet.json`); `career/2013/postseason/README.md` is the bracket page and round index.
- Receipts go to `career/2013/stats/postseason_receipts/`. Standings, the regular-season statbook, the calibration audit and awards stay regular-season views; no postseason weekly awards are drawn (the league gave none).
- The league roundup is `career/2013/league_results/week_NN.md` for the round's other games.
- A club eliminated from the postseason, Jacksonville included, plays no further game; if Jacksonville is eliminated, later rounds still close as background slates.

## Before a game

Read [game readiness](../state/game_readiness.md) and run `python scripts/check_game_readiness.py`. That command fails while any game prerequisite remains unverified. Repository validation, populated schedule folders and deterministic packet tests do not authorize a game. Keep private engine state outside Git, public logs and coach-facing files.
