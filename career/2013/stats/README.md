# 2013 season statbook

This directory is the **current season-stat layer**, parallel to but separate from `../standings.md`.

- `../standings.md` owns team records, points for/against, conference/division position and tiebreak presentation.
- `team_player_stats.md` owns Jacksonville's current season-to-date player production.
- `league_player_stats.md` owns the all-club season-to-date player stat view.
- `league_leaders.md` is a derived top-of-league view and may only rank players when coverage is complete.
- `game_receipts/` is the rebuildable source: one public stat-only receipt per closed game.
- `season_totals.json` is generated from receipts by `python scripts/render_season_stats.py YEAR --team TEAM_ID` when a complete receipt set exists.

## Rules

1. **Closed games only.** No projected, expected or future statistics enter the statbook.
2. **One receipt per game.** The receipt is derived from the already-closed shared-kernel result. It does not rerun or influence the game.
3. **Public statistics only.** No seed, probability, hidden rating, matchup delta or private Engine State material belongs here.
4. **Additive arithmetic is automated.** Season totals are rebuilt from game receipts, not hand-carried from the previous week's Markdown.
5. **No historical backfill from the real NFL game.** If a simulated game did not preserve a player attribution, the missing split stays unknown or team/unattributed.
6. **Transactions follow the player.** The league view may show multiple teams for a player; a team view contains only production credited to that club.
7. **Standings and statistics remain separate authorities.** A statistical ranking never changes a tiebreak or team record.

## Week 1 bootstrap limitation

Week 1 was closed before this statbook existed. Jacksonville-Kansas City preserved enough of its player production to build a useful team view, but the fifteen background games saved only scores, highlights and selected standout lines. Their complete player-level result objects were not committed to the repository.

Accordingly:

- Jacksonville's Week 1 file below is exact for the preserved lines, with unattributed remainder called out.
- The league player-stat view contains only lines that were actually preserved in the Week 1 records.
- `league_leaders.md` withholds formal rankings until Week 1 can be idempotently backfilled from the exact closed game packets, or another complete canonical source becomes available.
- Starting with the next simulated game, the complete public stat receipt must be saved at closure so this gap does not recur.
