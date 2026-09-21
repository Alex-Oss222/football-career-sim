# Keeping the career records current

The current checkpoint is owned by [Document 5](../state/05_Current_Season_State.md) and the latest closed [season-ledger entry](../career/2013/ledger.md). The [repository map](repository_map.json) records paths and dependencies, not a second set of football facts.

## Which files change together

| Event | First record | Dependent views to inspect and update when affected |
|---|---|---|
| Practice or camp work | Phase `output.md`, then ledger | Phase `standouts.md`; roster/register availability and role evidence; current state; calendar status; camp battles/decisions if a decision occurred |
| Signing, release, trade or drafted contract | Applicable signing/trade/draftee result, then ledger | Roster; cap/contract worksheet; pick ownership; Documents 4 and 5 |
| Staff appointment or delegation | Staff hiring record and ledger | Current coaching staff; Document 4; Document 3 if durable authority/delegation changed; Document 5 |
| Final regular-season game | Game output and ledger | Full public game receipt (player stats + snap ledger + named-call stats); rebuilt player/play season statbook; medical/availability; Documents 4 and 5; standings for all affected clubs; calendar |
| Preseason game | Preseason output and ledger | Same affected personnel/statistical views; regular-season standings stay unchanged |
| Bye or administrative correction | Applicable note and ledger | Only facts actually changed; no phantom game, practice, injury or roster move |
| Foundation correction | Ledger correction staged first | Named foundation document; source-version manifest; affected current views and readiness |

Plans own teaching intent. Outputs own what happened. Standouts are evidence summaries of outputs, never a second event source or a permanent depth chart. Initial roster/cap sheets preserve the starting baseline; the current roster and cap worksheet own later changes. An older financial effective date remains correct when no financial event occurred.

## Close an event

1. Read the current state, calendar, applicable plan and source records. Respect the active playbook lock. For a weekly football slate, build the full transient TeamInput package and pass `scripts/check_week_input_exclusivity.py <weekly-input-package.json> --expected-games <scheduled-game-count>` before any event closes; use the actual scheduled game count so a partial slate fails, and let branch player control override historical roster rails.
2. Write the event/result and stage its ledger entry. Preserve earlier dated entries verbatim; append a correction when needed.
3. Review each dependency above. Update affected owners and summaries in the same commit. For a closed Jacksonville/protagonist regular-season or postseason game, preserve the full public receipt including player dictionaries, snap ledger and named-call usage. For ordinary background games, preserve the compact_stats receipt with every nonzero generated player/team statistic but without background snap rows or zero-only counters. Rebuild current season stat views from the receipt set; do not hand-add totals or reconstruct missing plays from prior Markdown. Do not touch unrelated financial or historical records to manufacture freshness.
4. Update Documents 4 and 5 checkpoints/versions consistently. Document 4 may retain its older content version if none of its owned facts changed; Document 5 must name that exact version. Refresh foundation Git-blob hashes in Document 5 after a foundation change, using `git hash-object` on each changed foundation source.
5. Update phase metadata and review the actual summary text. Only then run the receipt command below. It acknowledges review of the current source; it does not generate observations or prove prose is correct.
6. Close the ledger entry, run validation and review the diff. Commit the entire dependency set together through a pull request.

```sh
python scripts/refresh_summary_receipt.py otas --reviewed
# After a game, once the complete receipt set for the current coverage window exists:
# python scripts/render_season_stats.py YEAR --team TEAM_ID
python scripts/validate_repository.py
python -m unittest discover -s tests -v
```

The receipt command supports the phase names in `repository_map.json`. Metadata uses `NOT_STARTED`, `IN_PROGRESS`, or `COMPLETE`, an ISO evidence-through date, and the source event's ledger entry number. Future phases use null date/entry. A summary holds the SHA-256 of its source output, so editing that output makes an unreviewed summary fail validation. Update metadata when appending actual work; never stamp a future phase complete just to pass a check.

## Validation scope

Checks cover required files, local Markdown targets/anchors, current-state source hashes, closed checkpoint continuity, controlled-player membership/counts, and phase evidence receipts. Archived material and future playbook contents are excluded from reads. Templates and code examples are not live records.

These checks cannot judge football truth, medical evidence, a cap calculation, or whether a summary faithfully captures every observation. Human/agent review against the source remains required. CI does not automatically simulate events or rewrite state.

## One-command regular-season weeks

For regular-season play, `Run Week N` is the top-level workflow defined in `AGENTS.md`. Internal readiness, authorized migration/reset preparation, background-team input construction, receipt/statbook rebuild, standings, snapshot advancement and PR bookkeeping belong to that task; do not hand those implementation steps back to the user. A genuinely new Stone decision may still require user input when no supplied or already-closed plan covers it.

See `docs/run_week.md` for the minimal Codex handoff prompt.

## Before a game

Read [game readiness](../state/game_readiness.md) and run `python scripts/check_game_readiness.py`. That command fails while any game prerequisite remains unverified. Repository validation, populated schedule folders and deterministic packet tests do not authorize a game. Keep private engine state outside Git, public logs and coach-facing files.
