# Game stat receipts

Store one JSON stat receipt per closed regular-season or postseason game.

Normal-week naming pattern:

`week_NN_<away>_at_<home>.json`

Migration/reset receipts may retain immutable event-ID filenames when that identity is part of the audited replacement batch.

A receipt is created **after** the game is closed and contains only public game output needed for durable season accounting. Under kernel 2013.3, Jacksonville/protagonist games use `detail="full"` and retain complete player dictionaries, the public snap `play_ledger`, and `play_call_stats`. Ordinary background games use `detail="compact_stats"`: every nonzero generated team/player statistic is retained, while background snap rows, named-call data, zero-only player rows and zero-valued player fields are omitted to keep weekly Git diffs reviewable. Neither receipt type may contain private Engine State data, seeds, probability distributions, hidden ratings, or matchup deltas.

The receipt schema is produced by `runtime.statbook.make_receipt`. Rebuilding the current stat views is handled by:

`python scripts/render_season_stats.py YEAR --team TEAM_ID`

Week 1 now has a complete generation-2 receipt set produced by the authorized full-fidelity reset in `../../migrations/week_01_full_fidelity_reset.md`: one full Jacksonville-Kansas City receipt and fifteen compact statistical receipts. The later branch-control audit preserves exact team totals while marking player attribution partial where a historical-roster identity conflicted with Jacksonville branch control.

## Attribution corrections

A receipt may include `player_attribution_incomplete_teams` when a later integrity correction proves that a preserved player identity could not legally belong to that simulated club but the exact eligible replacement attribution is unknowable. In that case the generated statistics move to a pseudo-player id beginning `__`; team totals remain exact, pseudo rows are excluded from player leaderboards, and league player rankings remain withheld. Never invent a replacement player's line merely to restore leaderboard completeness.
