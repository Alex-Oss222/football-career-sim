# 2013 Statbook

The front door for season statistics and standings. Every page below is generated from the closed-game receipts; none is maintained by hand.

## Pages

| Page | What it shows |
|---|---|
| [Standings](standings.md) | Division standings, conference seeding if the season ended today, the league table and every tiebreaker applied |
| [Jacksonville player stats](stats/team_player_stats.md) | Jaguars players by position, then player |
| [League player stats](stats/league_player_stats.md) | Every club's players, one league-wide table per position |
| [All players by club](stats/all_player_stats.md) | Club, then position, then player |
| [League leaders](stats/league_leaders.md) | Leaders within each position, qualified passer-rate leaders and leaders across positions |
| [Team stats](stats/team_stats.md) | Per-game offense, defense and special teams for every club |
| [Stone play-call stats](stats/play_call_stats.md) | Named-call labels on Jacksonville snaps (Weeks 1-8 labels are drawn per run/pass type, not carrier-true; Entry 41) |
| [Band audit](stats/calibration_audit.md) | League receipts against the sourced 2012 position and volume shapes |
| [Statbook rules](stats/README.md) | Columns, qualifiers, receipt rules and rebuild commands |

Each weekly `output.md` carries its game's box score, generated from the same receipt by `scripts/render_box_score.py`.

## Current coverage

Through Week 8: one hundred twenty of one hundred twenty game receipts (Weeks 1-2 kernel 2013.4, Week 3 kernel 2013.5, Weeks 4-8 kernel 2013.6); coverage complete. Every graded band-audit row is WITHIN the 2012 bands, and every ledger-coherence count is zero.

## Rebuild

```
python scripts/render_season_stats.py 2013 --team "Jacksonville Jaguars"
python scripts/render_standings.py 2013
```

## Snap ledger

Every Jacksonville receipt stores the complete public `play_ledger`: each scrimmage snap with its named call, and each scoring or special-teams terminal play. The play-call page, including its explosive (20+ yard) and negative-play counts, is derived from those snap records. The ledger records play type, gain, participants and clock; it does not record down, distance or field position, so red-zone and down-and-distance splits are not generated. Through Week 8 (kernels 2013.4-2013.6) each snap's call label is drawn from the sheet's calls of that run/pass type, independent of the ball carrier (Entry 41), so the play-call page shows label assignment, not Stone's call frequencies.

## Player attribution (kernel 2013.4 onward)

Carries, targets, tackles and defensive credits follow the club depth chart supplied in each TeamInput, shaped by sourced 2012 league-wide position usage (`../../library/2012_position_usage_calibration.md`). One passer plays the whole game unless a coach input changes it. The band audit flags a week whose league totals drift from those shapes; it never reruns a game.
