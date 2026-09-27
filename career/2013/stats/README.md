# 2013 season statbook

Every file in this directory except `README.md` and `game_receipts/README.md` is generated from the closed-game receipts in `game_receipts/`. Nothing here is typed by hand, and `python scripts/validate_repository.py` fails if a view drifts from its rebuild.

## Views

| File | What it shows |
|---|---|
| `team_player_stats.md` | Jacksonville players by position, then player, with each position's standard statistics |
| `league_player_stats.md` | Every club's players in one league-wide table per position |
| `all_player_stats.md` | Club by club, then position, then player |
| `league_leaders.md` | Leaders within each position, qualified passer-rate leaders, then leaders across all positions |
| `team_stats.md` | Per-game team offense, defense (opponent production) and special teams |
| `play_call_stats.md` | Jacksonville's named offensive calls: use, completions, yards, explosive and negative plays |
| `calibration_audit.md` | League receipts against the sourced 2012 position and volume shapes |
| `season_totals.json` | Machine cache of the aggregated season |

Team records, division order, playoff seeding and tiebreakers live in `../standings.md`, generated from the same receipts.

## Rebuild

```
python scripts/render_season_stats.py 2013 --team "Jacksonville Jaguars"
python scripts/render_standings.py 2013
```

## Position tables

Players are filed by roster position: quarterbacks, running backs (RB, FB), wide receivers, tight ends, offensive line, defensive line, linebackers, defensive backs, kickers, punters and long snappers. Each table carries the statistics that position is measured by:

| Position | Columns |
|---|---|
| Quarterbacks | G, CMP, ATT, CMP%, YDS, Y/A, TD, INT, RTG, SCK, SCKY, then rushing and fumbles |
| Running backs | G, CAR, YDS, AVG, TD, LNG, then receiving and fumbles |
| Wide receivers, tight ends | G, TGT, REC, YDS, AVG, TD, LNG, then rushing and fumbles |
| Offensive line | G, SCK ALLOWED |
| Defensive line, linebackers | G, TOT, SOLO, AST, TFL, SCK, PRESS, PD, INT, FF, FR |
| Defensive backs | G, TOT, SOLO, AST, TFL, INT, INT YDS, PD, SCK, PRESS, FF, FR |
| Kickers | G, FGM, FGA, FG%, XPM, XPA, PTS |
| Punters | G, PUNTS, YDS, AVG, LNG, IN20, TB |

Kick and punt returners follow in their own table. A counter outside a player's position table, such as a receiver's coverage tackle, appears under **Other statistics**, so no generated statistic is dropped from the readable views.

**G** counts games on the game-day active list: every player in a closed game's result is stamped with one game active. RTG is the official NFL passer rating. CMP%, Y/A, AVG, FG% and every other derived column are arithmetic on stored counters. LNG is the longest single play, combined across games by maximum.

## Leader qualifiers

Passer-rate leaders (rating, completion percentage, yards per attempt) require 14 attempts per team game, the NFL passing qualifier. Rushing and receiving average leaders are not published: the NFL's minimums for those categories have not been verified from a dated source.

## Rules

1. **Closed games only.** No projected, expected or future statistic enters the statbook.
2. **One receipt per game,** derived from the already-closed shared-kernel result. It never influences resolution.
3. **Public statistics only.** No seed, probability, hidden rating, matchup delta or private Engine State material.
4. **No historical backfill.** A statistic the simulated game did not attribute stays unattributed; the real NFL game is never consulted.
5. **Transactions follow the player.** League views may list several clubs for one player; a club view holds only production credited to that club.
6. **Distinct player ids.** A player id names one player. Two players who share a name need distinct ids (for example `Mike Harris (SD)`); a receipt with the same id on both clubs is rejected.
7. **Standings and statistics stay separate.** A statistical ranking never changes a record or a tiebreaker.

## Current coverage

Through Week 1: sixteen of sixteen receipts, coverage complete.

## Branch-control rule

Players acquired, drafted or signed by Jacksonville may not appear on a real-history background roster. Weekly input slates must pass `scripts/check_week_input_exclusivity.py` with the week's scheduled game count before any event closes. That gate also rejects a TeamInput that is not a legal game-day unit or lacks an explicit QB/RB/WR/TE depth order.
