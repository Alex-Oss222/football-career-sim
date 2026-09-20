# Run-week prompt

Use this when handing a regular-season week to Codex.

```text
Run Week [N].

Use the repository's one-command Run Week workflow in AGENTS.md.
Resolve all internal readiness, migration/reset, background-team input, statbook, standings, snapshot and PR prerequisites yourself.
Do not ask me to edit manifests, run helper scripts, research rosters, touch Railway or perform intermediate setup.

Plan:
[PASTE STONE'S WEEKLY PLAN HERE, or write "use the already-closed ex-ante plan" for an authorized rerun]

Run Week [N] only and stop before Week [N+1].
```

For the currently authorized 2013 Week 1 full-fidelity reset, `Run Week 1` means: autonomously prepare the missing 32 pre-Week-1 TeamInputs, pass the internal reset gate, replace all 16 Week 1 games under the active kernel, rebuild receipts/stats/standings/state, validate, advance the private snapshot and close the normal PR flow. The user does not perform a separate reset-prep step.
