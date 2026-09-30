# Season folders and continuity

The [2014 season](../career/2014/README.md) is the model from 2014 onward. Its numbered folders follow phase opening dates. Overlapping work follows the calendar; a folder’s position does not move an event. 2013 retains its historical structure.

| Home | Owns |
|---|---|
| `00_team` | Current roster, working depth, coaching staff, player cards, development and film |
| `01_early_offseason` | Review, scouting, staffing and pre-league-year preparation |
| `02_free_agency` | Targets, offers, negotiations and completed signings/tenders |
| `03_offseason_training` | Spring phases, staff plans, actual reports and player assessments |
| `04_draft` | Board, order, owned picks, selections and undrafted class |
| `05_training_camp_and_preseason` | Camp, preseason games, assessments, cuts and the preseason trade route |
| `06_regular_season` | Games, schedule, standings, statistics, league results and weekly/monthly awards |
| `07_postseason` | Playoff work, separate playoff statistics, honours and Pro Bowl |
| `08_season_review` | Exit reviews and the annual handoff |
| `09_finances` | Current-year cap/contracts and links to shared multi-year finances |
| `10_trades` | Targets/offers before completed trades, with dated exchanges and accounting |
| `calendar.md` / `ledger.md` | What is scheduled / what actually happened |

Each training phase uses `staff_plan.md` for intended work, `training_report.md` for actual events and `player_assessments.md` for conclusions supported by those events. Dates appear in the folder guides and navigation. A file guide explains the supporting records in each folder.

## One career across seasons

Complete the team review after its actual final game, reconcile contracts, roster, staff, medical status, future picks and open decisions, then stage the next year through `scripts/season_handoff.py`. The opening roster and working depth preserve their source checkpoint until reviewed. Player cards retain earlier yearly stat rows. New season game receipts, statistics, standings and awards start empty. Shared financial inputs preserve remaining obligations and history; actual cap rules, carryover and renewals require their own reconciliation.

A staged season is not the active season until the normal administrative event updates the current-record map and both state documents. Missing new-season inputs never fall back to another season. Review/closure requirements and game-release checks remain in force.

## Maintaining paths and reading pages

`runtime.seasons.SeasonPaths` resolves the season’s records. Use its properties or `record(logical_path)` rather than building old flat paths. `runtime.season_layout` maps logical record names to the readable layout from 2014 onward and preserves 2013 paths. Historical frozen JSON references resolve through that mapping; the original evidence is not rewritten.

- Cap and contract reading pages: `python scripts/render_jaguars_cap_tracker.py`.
- Trade exchange pages: `python scripts/render_trade_pages.py 2014`.
- Award cards: `python scripts/league_awards.py render --season 2014`. Rendering never draws or changes a winner.
- Repository checks: `python scripts/validate_repository.py` and `python -m unittest discover -s tests`.

Generated trade and financial pages are views of their linked source records. Change an actual transaction in its owner first, then regenerate the reading pages. Keep descriptions in plain football language; do not invent labels, outcomes or another editable balance.
