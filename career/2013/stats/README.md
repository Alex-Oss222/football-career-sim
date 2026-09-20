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

## Week 1 bootstrap limitation

Week 1 was closed before this statbook existed. Jacksonville-Kansas City preserved enough of its player production to build a useful team view, but the fifteen background games saved only scores, highlights and selected standout lines. Their complete player-level result objects were not committed to the repository.

Accordingly:

- Jacksonville's Week 1 file below is exact for the preserved lines, with unattributed remainder called out.
- `all_player_stats.md` keeps every Week 1 player/stat line that survived in the committed records and labels all missing legacy fields as unavailable rather than zero.
- The league player-stat view contains only lines that were actually preserved in the Week 1 records.
- `league_leaders.md` withholds formal rankings until Week 1 can be idempotently backfilled from the exact closed game packets, or another complete canonical source becomes available.
- Starting with the first game resolved under kernel 2013.3, Jacksonville keeps a full public stat/snap receipt and ordinary background games keep compact complete-stat receipts, so league statistical coverage remains complete without duplicating every background snap in Git.
- Week 1 also lacks canonical named-play usage because its old kernel did not generate a snap ledger. No concept usage count may be reconstructed from narrative prose.
