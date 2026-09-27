# Run-week prompt

Use this when handing a regular-season week to the runner (Claude Code; see `CLAUDE.md`).

```text
Run Week [N].

Use the repository's one-command Run Week workflow in AGENTS.md.
Resolve all internal readiness, migration/reset, background-team input, statbook, standings, snapshot and PR prerequisites yourself.
Do not ask me to edit manifests, run helper scripts, research rosters, touch Railway or perform intermediate setup.

Plan:
[PASTE STONE'S WEEKLY PLAN HERE, or write "use the already-closed ex-ante plan" for an authorized rerun]

Run Week [N] only and stop before Week [N+1].
```

The 2013 Week 1 restart (generation 3 under kernel 2013.4) is closed history: see [career/2013/migrations/week_01_kernel_2013_4_restart.md](../career/2013/migrations/week_01_kernel_2013_4_restart.md) (ledger Entry 35).

A current week needs these inputs from Stone before `python scripts/build_week_inputs.py N` can freeze the slate: the week's plan frozen as `career/YEAR/regular_season/week_NN_<away>_at_<home>/call_sheet.json` (the builder blocks without it); any open role decision the plan must settle, such as the weekly center evaluation; and the game-day inactives, written to `career/YEAR/depth_chart.json` (a week without a new list reuses the last one). The private snapshot stays on the last merged canonical state until the public PR is merged; only a merged `main` checkout may advance it.

## Generated-data rule

Every club dresses at most 46 players. Jacksonville's inactives are Stone's list in `career/2013/depth_chart.json`; a background club's are chosen mechanically from the bottom of its depth order (`runtime.week_inputs.game_day_actives`), never from a real historical inactive list, and the weekly gate rejects a TeamInput with more than 46 actives.

The one-command workflow keeps large reconstructed TeamInputs in the gitignored `.sim_cache/` workspace. Jacksonville/protagonist games preserve full snap/stat receipts; ordinary background games preserve `compact_stats` receipts with complete nonzero generated statistics but no background snap ledger. The runner must use these bounded-storage paths automatically rather than failing the task because the generated Git diff is too large.
