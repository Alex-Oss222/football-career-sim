# Game stat receipts

Store one JSON stat receipt per closed regular-season or postseason game.

Naming pattern:

`week_NN_<away>_at_<home>.json`

A receipt is created **after** the game is closed and contains only public game output needed to rebuild season totals and play usage. Under kernel 2013.3 it includes complete public team/player stat dictionaries, the full public snap `play_ledger`, and game `play_call_stats`. It must not contain private Engine State data, seeds, probability distributions, hidden ratings, or matchup deltas.

The receipt schema is produced by `runtime.statbook.make_receipt`. Rebuilding the current stat views is handled by:

`python scripts/render_season_stats.py YEAR --team TEAM_ID`

Week 1 predates this storage rule, so a complete Week 1 receipt set is not present. The authorized full-fidelity reset remains blocked by `../../migrations/week_01_full_fidelity_reset.md` until all 32 canonical pre-Week-1 team inputs are available.
