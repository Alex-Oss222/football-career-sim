# Game stat receipts

One JSON receipt per closed regular-season or postseason game, written by `runtime.statbook.make_receipt` after the game closes. Receipts are the only source for the season statbook, the standings and every weekly box score.

Normal-week naming pattern: `week_NN_<away club>_at_<home club>.json`, for example `week_02_jacksonville_jaguars_at_oakland_raiders.json`, written by `scripts/close_week.py`. The Week 1 generation-3 receipts keep their event-id filenames from the audited replacement batch.

## Contents (statbook schema 3)

- `event_id`, `week`, `matchup` (`Away Club at Home Club`), and the designated `home` and `away` clubs.
- `final_score` and each club's team statistics.
- A player row for every player on each club's game-day active list. Each row carries the player's position, `games: 1`, and his generated statistics.
- `injuries`: the game's public injury report (club, player, injury class, severity, restriction, projected return and reassessment days). Later weeks read it for availability.
- Jacksonville and protagonist games use `detail="full"`: player rows keep every counter, including zeros, and the receipt adds the public snap `play_ledger` and named-call `play_call_stats`.
- Ordinary background games use `detail="compact_stats"`: player rows keep only nonzero counters plus `games`, and there is no snap ledger or named-call data. This keeps weekly diffs reviewable without losing any generated statistic or appearance.

No receipt may contain private Engine State data, seeds, probability distributions, hidden ratings or matchup deltas.

## Rebuilding

```
python scripts/render_season_stats.py 2013 --team "Jacksonville Jaguars"
python scripts/render_standings.py 2013
python scripts/render_box_score.py --write career/2013/regular_season/week_NN_<away>_at_<home>/output.md
```

## Attribution corrections

A receipt may list `player_attribution_incomplete_teams` when a later integrity correction proves that a preserved player identity could not legally belong to that simulated club and the exact eligible replacement is unknowable. The statistics then move to a pseudo-player id beginning `__`: team totals stay exact, box scores show the line as `Team / unattributed`, pseudo rows never enter leaderboards, and league player rankings stay withheld. A replacement player's line is never invented to restore completeness.

## Current contents

Week 1 generation 3: `2013-week01-reset-v3-01.json` through `-16.json`; Week 2: `week_02_*.json` (kernel 2013.4). Jacksonville's receipt each week is full; the rest are compact. The void generation-2 receipts were deleted by ledger Entry 34.
