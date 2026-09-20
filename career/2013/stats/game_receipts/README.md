# Game stat receipts

Store one JSON stat receipt per closed regular-season or postseason game.

Naming pattern:

`week_NN_<away>_at_<home>.json`

A receipt is created **after** the game is closed and contains only public game output needed for durable season accounting. Under kernel 2013.3, Jacksonville/protagonist games use `detail="full"` and retain complete player dictionaries, the public snap `play_ledger`, and `play_call_stats`. Ordinary background games use `detail="compact_stats"`: every nonzero generated team/player statistic is retained, while background snap rows, named-call data, zero-only player rows and zero-valued player fields are omitted to keep weekly Git diffs reviewable. Neither receipt type may contain private Engine State data, seeds, probability distributions, hidden ratings, or matchup deltas.

The receipt schema is produced by `runtime.statbook.make_receipt`. Rebuilding the current stat views is handled by:

`python scripts/render_season_stats.py YEAR --team TEAM_ID`

Week 1 predates this storage rule, so a complete Week 1 receipt set is not present. The authorized full-fidelity reset in `../../migrations/week_01_full_fidelity_reset.md` requires 32 canonical pre-Week-1 team inputs before replacement draws, but constructing those inputs is an internal prerequisite of the one-command `Run Week 1` workflow. The user is not responsible for populating the reset manifest.
