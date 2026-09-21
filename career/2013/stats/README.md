# 2013 season statbook

This directory is the **current season-stat layer**, parallel to but separate from `../standings.md`.

- `../standings.md` owns team records, points for/against, conference/division position and tiebreak presentation.
- `team_player_stats.md` owns Jacksonville's readable current season-to-date player production by category.
- `all_player_stats.md` is the comprehensive ledger: every player record preserved by the stat receipts and every currently supported generated stat field.
- `league_player_stats.md` owns the readable all-club season-to-date category view.
- `play_call_stats.md` owns Jacksonville's season-to-date named offensive call usage and results.
- `league_leaders.md` is a derived top-of-league view and may only rank players when coverage is complete.
- `game_receipts/` is the rebuildable source: one public stat-only receipt per closed game.
- `season_totals.json` is generated from receipts by `python scripts/render_season_stats.py YEAR --team TEAM_ID` when a complete receipt set exists.

## Rules

1. **Closed games only.** No projected, expected or future statistics enter the statbook.
2. **One receipt per game.** The receipt is derived from the already-closed shared-kernel result and never influences resolution. Jacksonville/protagonist games use `detail="full"` and preserve complete public player dictionaries, `play_ledger`, and game-level `play_call_stats`. Ordinary background games use `detail="compact_stats"` and preserve every nonzero generated player/team statistic while omitting the background snap ledger, named-call data, zero-only player rows and zero-valued player fields.
3. **Public statistics only.** No seed, probability, hidden rating, matchup delta or private Engine State material belongs here.
4. **Additive arithmetic is automated.** Season totals are rebuilt from game receipts, not hand-carried from the previous week's Markdown.
5. **No historical backfill from the real NFL game.** If a simulated game did not preserve a player attribution, the missing split stays unknown or team/unattributed.
6. **Transactions follow the player.** The league view may show multiple teams for a player; a team view contains only production credited to that club.
7. **All public numeric player counters are retained.** The statbook automatically discovers and accumulates every numeric field present in the public player dictionaries. The current engine includes passing attempts/yards/interceptions thrown, rushing attempts/yards, receptions/receiving yards, sacks allowed, sacks, pressures, fumbles, field goals made, punts, return yards and tackles. If the engine later adds targets, touchdowns, pass defenses, longest gains or another public numeric stat, the comprehensive ledger keeps it without requiring a new hard-coded whitelist. Cleaner category tables may hide irrelevant zero columns, but the underlying record is not discarded.
8. **Zero counters are preserved only where useful.** Full Jacksonville/protagonist receipts preserve zero counters. Compact background receipts intentionally omit zero-only players and zero-valued fields; this does not remove any generated nonzero statistical production and does not imply non-participation.
9. **Standings and statistics remain separate authorities.** A statistical ranking never changes a tiebreak or team record.

## Week 1 full-fidelity coverage

The authorized generation-2 reset replaced all sixteen legacy Week 1 games under kernel 2013.3. Jacksonville-Kansas City has a full receipt with public snap and named-call detail; the other fifteen games have compact statistical receipts preserving every nonzero generated team and player statistic.

Accordingly:

- `all_player_stats.md` renders every nonzero Week 1 player statistic from the complete receipt set.
- `league_player_stats.md` preserves known Week 1 player lines, but `league_leaders.md` withholds formal rankings because five corrected background receipts now have intentionally partial player attribution.
- `play_call_stats.md` renders Jacksonville's generated named-call use directly from the full receipt.
- Background compact receipts omit snap ledgers and zero-only counters only for storage efficiency. Team statistical totals remain complete. A later branch-control audit moved impossible historical-team player credits in five receipts to pseudo/unattributed rows; those receipts now distinguish complete team totals from partial exact player attribution.

## Branch-control attribution correction

Before Week 2, the Week 1 receipt set was checked against Jacksonville's branch-controlled roster. Players already acquired, drafted or signed by Jacksonville may not simultaneously appear on a real-history background roster. The affected impossible attributions were removed without changing any final score or team total. Exact replacement player attribution is intentionally left unknown rather than reassigned by guesswork. Future weekly input slates must pass `scripts/check_week_input_exclusivity.py` before any event closes.
