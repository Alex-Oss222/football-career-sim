# Preseason statistics

[Preseason games](../README.md)

Two preseason games are closed (game 1, August 8, 2014: Tampa Bay 30, Jacksonville 21; game 2, August 14, 2014: Chicago 23, Jacksonville 17, overtime). Completed preseason box scores and preseason totals belong here, drawn from the preseason records only. They never add to regular-season or playoff totals.

## How the records are kept

- `records/game_receipts/` holds one full public receipt per closed preseason game (`preseason_NN_<away>_at_<home>.json`), written by `python scripts/close_preseason_game.py N --season 2014 --close`. The receipt carries the fixture's own event id (`2014-preseason-NN-...`), `game_type` "preseason", the game date and the try rule the kernel applied. The directory is created by the first closure; `runtime/seasons.py` (`SeasonPaths.preseason_receipts`) keeps it apart from the regular-season and postseason receipt sets, so `render_standings.py`, `render_season_stats.py`, the awards and the draft order never read it.
- `preseason_stats.md` and `preseason_totals.json` are generated from those receipts by `python scripts/render_preseason_stats.py --season 2014` (also run by the closure): games, team totals, Jacksonville's players by position and the opponents' players from the games against Jacksonville only. Nothing is typed by hand, no league ranking is drawn, and `validate_repository.py` fails while a receipt exists and these views are stale.
- Each game's box score is the 2014 gamebook rendered into the marked block of `Game_0N/output.md` (`python scripts/render_box_score.py --season 2014 --preseason --write <output.md>`).
