# 2013 season statbook

This directory is the **current season-stat layer**, parallel to but separate from `../standings.md`.

- `../standings.md` owns team records, points for/against, conference/division position and tiebreak presentation.
- `team_player_stats.md` owns Jacksonville's readable current season-to-date player production by category.
- `all_player_stats.md` is the comprehensive ledger: every player record preserved by the stat receipts and every currently supported generated stat field.
- `league_player_stats.md` owns the readable all-club season-to-date category view.
- `play_call_stats.md` owns Jacksonville's season-to-date named offensive call usage and results.
- `league_leaders.md` is a derived top-of-league view and may only rank players when receipt coverage and exact player attribution are complete.
- `game_receipts/` is the rebuildable source: one public stat-only receipt per closed game.
- `season_totals.json` is generated from receipts by `python scripts/render_season_stats.py YEAR --team TEAM_ID` when a complete receipt set exists.

## Rules

1. **Closed games only.** No projected, expected or future statistics enter the statbook.
2. **One receipt per game.** The receipt is derived from the already-closed shared-kernel result and never influences resolution. Jacksonville/protagonist games use `detail="full"` and preserve complete public player dictionaries, `play_ledger`, and game-level `play_call_stats`. Ordinary background games use `detail="compact_stats"` and preserve every nonzero generated player/team statistic while omitting the background snap ledger, named-call data, zero-only player rows and zero-valued player fields.
3. **Public statistics only.** No seed, probability, hidden rating, matchup delta or private Engine State material belongs here.
4. **Additive arithmetic is automated.** Season totals are rebuilt from game receipts, not hand-carried from the previous week's Markdown.
5. **No historical backfill from the real NFL game.** If a simulated game did not preserve a player attribution, the missing split stays unknown or team/unattributed.
6. **Transactions follow the player.** The league view may show multiple teams for a player; a team view contains only production credited to that club.
7. **All public numeric player counters are retained.** The statbook automatically discovers and accumulates every numeric field present in the public player dictionaries. The current engine includes passing, rushing and receiving volume, yards and touchdowns, targets, longest gains, sacks allowed, sacks, pressures, fumbles, solo and assisted tackles, tackles for loss, passes defended, interceptions, forced fumbles and recoveries, kicking, punting and returns. A new public numeric stat is kept automatically without a hard-coded whitelist. Cleaner category tables may hide irrelevant zero columns, but the underlying record is not discarded.
8. **Zero counters are preserved only where useful.** Full Jacksonville/protagonist receipts preserve zero counters. Compact background receipts intentionally omit zero-only players and zero-valued fields; this does not remove any generated nonzero statistical production and does not imply non-participation.
9. **Standings and statistics remain separate authorities.** A statistical ranking never changes a tiebreak or team record.

## Current coverage

Empty. Week 1 was voided by ledger Entry 34; its generation-2 receipts and every derived view were deleted and regenerated from zero receipts. The views fill again when the replayed Week 1 closes under kernel 2013.4.

## Generated views

`python scripts/render_season_stats.py 2013 --team "Jacksonville Jaguars"` rebuilds every file below from `game_receipts/`, and `python scripts/validate_repository.py` fails if any of them drifts from that rebuild:

- `season_totals.json`: compact machine cache;
- `team_player_stats.md`, `play_call_stats.md`: Jacksonville;
- `league_player_stats.md`, `all_player_stats.md`, `league_leaders.md`: every club's players;
- `team_stats.md`: per-game team totals for every club;
- `calibration_audit.md`: league receipts against the sourced 2012 position and volume shapes. It detects engine or TeamInput defects and never reruns or selects a game.

## Branch-control rule

Players already acquired, drafted or signed by Jacksonville may not appear on a real-history background roster. Weekly input slates must pass `scripts/check_week_input_exclusivity.py` with the week's scheduled game count before any event closes. That gate also rejects a TeamInput that is not a legal game-day unit or lacks an explicit QB/RB/WR/TE depth order.
