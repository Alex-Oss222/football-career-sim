# Week 1 full-fidelity reset

**Status:** AUTO-RESOLVABLE INTERNAL PREREQUISITE — authorized, not executed.  
**User authorization:** The user explicitly authorized the full-stat/full-play Week 1 replacement and later instructed that `Run Week 1` must perform all reset preparation automatically without sending setup work back to the user.  
**Source checkpoint:** `Canonical update - September 4, 2013 - preseason, roster and cap block closed`.

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
2. Close all 16 replacement events under the same kernel version and same reset batch.
3. Preserve one full public stat/snap receipt for Jacksonville-Kansas City and `compact_stats` receipts for the other 15 games. The background compact receipts retain every nonzero generated statistic required for league totals and leaders without committing 15 redundant snap ledgers.
4. Rebuild standings, Jacksonville player stats, all-player stats, league stats, named-play stats and league leaders from the replacement receipts.
5. Reconcile all replacement injuries/availability across affected current records.
6. Rewrite Jacksonville Week 1 using the current season template.
7. Replace the Week 1 background roundup from the new closed results.
8. Append a Document 6 supersession entry identifying the legacy Week 1 slate as superseded by the full-fidelity reset.
9. Advance current state only after every dependency reconciles atomically.
10. Do not start Week 2 until the replacement Week 1 package validates.

Until the internal gate passes, the existing Week 1 result remains the active canon and its statbook coverage remains explicitly partial. The user should not be asked to perform any reset-preparation step.
