# 2013 Statbook

This is the front door for season statistics.

## Current views

| View | Purpose |
|---|---|
| [Jacksonville player stats](stats/team_player_stats.md) | Jaguars season-to-date player production by category |
| [All player stats](stats/all_player_stats.md) | Comprehensive supported-field ledger for every player preserved in the stat receipts |
| [League player stats](stats/league_player_stats.md) | League-wide category tables |
| [Stone play-call stats](stats/play_call_stats.md) | Season-to-date usage and results by named offensive concept |
| [League leaders](stats/league_leaders.md) | Formal leaders when league receipt coverage and exact player attribution are complete |
| [Team stats](stats/team_stats.md) | Per-game team totals for every club from the receipts |
| [Band audit](stats/calibration_audit.md) | League receipts compared with the sourced 2012 position and volume shapes |
| [Standings](standings.md) | Team W-L-T, division/conference/league position and tiebreak presentation |
| [Statbook rules](stats/README.md) | Receipt storage, coverage rules and rebuild procedure |

## Current coverage

No regular-season game is canon. Week 1 was voided by ledger Entry 34 and its receipts were deleted, so every view is empty until the replayed Week 1 closes under kernel 2013.4.

Every public player-stat dictionary returned by the shared game result is preserved in its game receipt and accumulated into the statbook. The comprehensive all-player ledger is not limited to leaders, starters or standouts. Rebuild every view with one command:

`python scripts/render_season_stats.py 2013 --team "Jacksonville Jaguars"`

## Snap ledger

Since kernel 2013.3 every closed game result carries a canonical public `play_ledger`. The corresponding game receipt stores the entire ledger, including every generated scrimmage snap and scoring/special-teams terminal play. Named Jacksonville calls come from the structured weekly offensive call sheet. The season play-call page is derived from those raw snap records.

## Player attribution (kernel 2013.4)

Carries, targets, tackles and defensive credits follow the club depth chart supplied in each TeamInput, shaped by sourced 2012 league-wide position usage (`../../library/2012_position_usage_calibration.md`). One passer plays the whole game unless a coach input changes it. Assisted tackles and tackles for loss are generated. The band audit flags a week whose league totals drift from those shapes; it never reruns a game.
