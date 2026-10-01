# Week 1 full-fidelity reset

**Status:** SUPERSEDED. Generation 1 technically aborted; generation 2 was published in merge `6658e3c0e8797f0524a9fda25a4624992118815f` and later **voided** by [Week 1 kernel restart](week_01_kernel_2013_4_restart.md) for the kernel 2013.4 restart. It was replaced by the generation-3 restart ([week_01_kernel_2013_4_restart.md](week_01_kernel_2013_4_restart.md)), closed by [2013 Kansas City game report](../regular_season/week_01_kansas_city_at_jacksonville/output.md). This file is retained as the audit history of generations 1 and 2.
**User authorization:** The user explicitly authorized the full-stat/full-play Week 1 replacement and later instructed that `Run Week 1` must perform all reset preparation automatically without sending setup work back to the user.
**Source checkpoint:** `Canonical update - September 4, 2013 - preseason, roster and cap block closed`.

**Technical-abort record (September 20, 2026):** the first full-fidelity reset attempt privately closed all 16 `reset-v1` events, then an older workflow erroneously advanced the private snapshot before public publication. Codex subsequently failed because the generated Git diff exceeded its extraction limit; no reset commit or PR reached `main`, and no v1 result was published to the user as replacement canon. HTTP deployment logs independently show the 16 event closures followed by the premature snapshot-advance call. Under the project's transaction rule this entire v1 batch is an outcome-independent technical abort. Generation 2 uses new event IDs and may run only after the private binding is auditably restored to the checked-in canonical state.

Before any replacement event closes, `python scripts/mark_week1_generations_void.py` (which replaced the earlier generation-1-only helper) idempotently records the private correction for each known `2013-week01-reset-v1-01` through `...-16` event ID. This preserves the private append-only audit trail without exposing the abandoned results.

## Why the reset needs reconstruction

The original Week 1 closure did not commit the 16 frozen production game packets or their event IDs. The private Engine State journal intentionally does not expose old packet rows through the public API. The fifteen background games also did not commit complete player-level TeamInput/roster packets.

A replacement slate therefore cannot be reconstructed honestly from the existing Markdown. The repo must not:

- infer missing players from highlight prose;
- substitute the real 2013 NFL box scores;
- silently use future roster knowledge;
- invent named play calls for the old Jacksonville game;
- rerun only Jacksonville while leaving the other 15 games on the legacy data contract.

## Internal execution gate

`week_01_full_fidelity_reset.json` is small committed control metadata listing all 16 Week 1 games and replacement event IDs. The complete reconstructed pre-Week-1 `away_input` and `home_input` objects belong in the gitignored `.sim_cache/week_01_full_fidelity_inputs.json`, where `scripts/check_week1_reset_ready.py` overlays them for the execution gate.

**This is not a user-maintenance gate.** When the user says `Run Week 1`, Codex owns researching, constructing, source-recording and freezing those 32 TeamInputs as part of the same task. Codex must write the large reconstructed objects to `.sim_cache/`, never to the committed migration manifest. A failed first pass of `check_week1_reset_ready.py` means internal preparation remains; it is not grounds to ask the user to edit JSON or run another command.

Every replacement input must be dated to the September 4 checkpoint and include, where applicable:

- team identifier;
- active participants and full public roster packet;
- offense/defense/special-teams evidence anchors;
- availability;
- roles/rotation;
- personnel packages;
- Jacksonville's structured weekly offensive call sheet for the protagonist game;
- any other football input required by the active runtime schema.

Codex must run:

`python scripts/check_week1_reset_ready.py`

If it does not pass, Codex must complete the missing canonical TeamInput reconstruction and rerun it. The command must exit successfully before any Week 1 replacement simulation is attempted.

## Replacement procedure once ready

1. Freeze all 32 team inputs before drawing any replacement game.
2. Confirm the v1 correction records are written, then close all 16 generation-2 replacement events under the same kernel version and same reset batch.
3. Preserve one full public stat/snap receipt for Jacksonville-Kansas City and `compact_stats` receipts for the other 15 games. The background compact receipts retain every nonzero generated statistic required for league totals and leaders without committing 15 redundant snap ledgers.
4. Rebuild standings, Jacksonville player stats, all-player stats, league stats, named-play stats and league leaders from the replacement receipts.
5. Reconcile all replacement injuries/availability across affected current records.
6. Rewrite Jacksonville Week 1 using the current season template.
7. Replace the Week 1 background roundup from the new closed results.
8. Append a Document 6 supersession entry identifying the legacy Week 1 slate as superseded by the full-fidelity reset.
9. Validate and open the public PR after every dependency reconciles atomically. **Do not advance the private snapshot from the branch.** Merge first; only the merged `main` checkout may advance the private snapshot to the new Document 5 digest.
10. Do not start Week 2 until the replacement Week 1 package validates.

Generation 2 passed the internal gate, closed all 16 replacements and was published to `main` in merge `6658e3c0e8797f0524a9fda25a4624992118815f`.

## Post-publication branch-roster attribution correction

A Week 2 handoff audit, followed by the Week 2 generation-readiness audit, found that the historical Week-1 roster reconstruction had retained players on their real-history clubs even though branch canon already placed them under Jacksonville control. The completed defect scope affected ten player identities across seven receipts:

- Baltimore-Denver: Brynden Trawick and C.J. Anderson;
- Tennessee-Pittsburgh: Antwon Blake on Pittsburgh;
- Miami-Cleveland: Brent Grimes;
- Minnesota-Detroit: C.J. Mosley on Detroit;
- Green Bay-San Francisco: C.J. Wilson;
- Philadelphia-Washington: Jordan Poyer, Kirk Cousins and Bacarri Rambo;
- Kansas City-Jacksonville: Tyler Bray on Kansas City's historical roster rail.

The correction is outcome-preserving. The published Week 1 team scores, standings, team totals and Jacksonville's own player statistics remain unchanged. Each impossible non-Jacksonville player line was moved to an explicit pseudo/unattributed row in the affected receipt so the generated team total is preserved without inventing which eligible teammate would have received the production. Those clubs are therefore marked player-attribution partial and formal league player rankings are withheld until that exact attribution can be established by a canonical source.

This correction does **not** authorize another Week 1 draw. The kernel's team-level matchup anchors and published outcome remain canon; rerolling after the result is known would create outcome-selection risk. Future weekly TeamInput packages must pass `scripts/check_week_input_exclusivity.py` with the week's scheduled game count before any event closes, so a partial slate cannot pass and branch-controlled Jacksonville players cannot reappear on another club.

The separate private-snapshot transition conflict found after publication was a bookkeeping defect caused by the audited generation-1 rollback retaining a legacy unique transition row. Runtime transition history now supports legitimate progression after an audited recovery while retaining the old history append-only.

<!-- event-record: {"closure": {"checkpoint": "Canonical update - September 9, 2013 - Week 1 closed", "original_close": "Commit closed \u2014 Canonical update - September 9, 2013 - Week 1 closed \u2014 canonical through the full Week 1 slate and Jacksonville postgame work", "sequence": 30, "through": "2013-09-09"}, "date": "2013-09-09", "id": "2013-09-09-regular-season-week-1-closed", "kind": "technical", "status": "closed", "summary": "Superseded Week 1 generation or attribution correction."} -->

<!-- event-record: {"closure": {"checkpoint": "Canonical update - September 9, 2013 - Week 1 full-fidelity reset closed", "original_close": "Commit closed \u2014 Canonical update - September 9, 2013 - Week 1 full-fidelity reset closed \u2014 canonical through the full Week 1 slate and Jacksonville postgame work", "sequence": 31, "through": "2013-09-09"}, "date": "2013-09-09", "id": "2013-09-09-regular-season-week-1-full-fidelity-reset-closed", "kind": "technical", "status": "closed", "summary": "Superseded Week 1 generation or attribution correction."} -->

<!-- event-record: {"closure": {"checkpoint": "Canonical correction - September 9, 2013 - Week 1 attribution and Week 2 handoff reconciled", "original_close": "Commit closed \u2014 Canonical correction - September 9, 2013 - Week 1 attribution and Week 2 handoff reconciled \u2014 canonical through September 9, after Week 1 and before Week 2 preparation", "sequence": 32, "through": "2013-09-09"}, "date": "2013-09-09", "id": "2013-09-09-week-1-attribution-and-week-2-handoff-correction-closed", "kind": "technical", "status": "closed", "summary": "Superseded Week 1 generation or attribution correction."} -->

<!-- event-record: {"closure": {"checkpoint": "Canonical correction - September 9, 2013 - Week 1 attribution audit completed for Week 2 readiness", "original_close": "Commit closed \u2014 Canonical correction - September 9, 2013 - Week 1 attribution audit completed for Week 2 readiness \u2014 canonical through September 9, after Week 1 and before Week 2 preparation", "sequence": 33, "through": "2013-09-09"}, "date": "2013-09-09", "id": "2013-09-09-week-1-attribution-audit-completion-and-week-2-readiness-correction-closed", "kind": "technical", "status": "closed", "summary": "Superseded Week 1 generation or attribution correction."} -->
