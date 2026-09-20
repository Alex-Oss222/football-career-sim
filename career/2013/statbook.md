# 2013 Statbook

This is the front door for season statistics.

## Current views

| View | Purpose |
|---|---|
| [Jacksonville player stats](stats/team_player_stats.md) | Jaguars season-to-date player production by category |
| [All player stats](stats/all_player_stats.md) | Comprehensive supported-field ledger for every player preserved in the stat receipts |
| [League player stats](stats/league_player_stats.md) | League-wide category tables |
| [Stone play-call stats](stats/play_call_stats.md) | Season-to-date usage and results by named offensive concept |
| [League leaders](stats/league_leaders.md) | Formal leaders when league receipt coverage is complete |
| [Standings](standings.md) | Team W-L-T, division/conference/league position and tiebreak presentation |
| [Statbook rules](stats/README.md) | Receipt storage, coverage rules and rebuild procedure |

## Current coverage

The generation-2 Week 1 replacement has complete receipt coverage: full snap and named-call detail for Jacksonville-Kansas City and compact statistical receipts for the other fifteen games. Formal league rankings are rendered from those receipts.

From the next closed game forward, every public player-stat dictionary returned by the shared game result is preserved in its game receipt and accumulated into the statbook. The comprehensive all-player ledger is not limited to leaders, starters or standouts.

## Snap ledger

Kernel 2013.3 adds a canonical public `play_ledger` to each closed game result. The corresponding game receipt stores the entire ledger, including every generated scrimmage snap and scoring/special-teams terminal play. Named Jacksonville calls come from the structured weekly offensive call sheet. The season play-call page is derived from those raw snap records.
