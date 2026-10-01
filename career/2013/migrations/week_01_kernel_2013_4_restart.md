# Week 1 restart under kernel 2013.4

**Status:** CLOSED. Week 1 was replayed as generation 3 and closed by [2013 Kansas City game report](../regular_season/week_01_kansas_city_at_jacksonville/output.md): Jacksonville 31, Kansas City 13, with all sixteen games replaced.
**User authorization:** On September 27, 2026 the user directed a full Week 1 restart after the statistical audit, asked that everything from Week 1 be deleted, and asked that the engine fixes and the stat-sheet rebuild be made.
**Restored checkpoint:** `Canonical correction - September 4, 2013 - Week 1 voided for kernel 2013.4 restart` (roster content equals the September 4 [2013 cap compliance](../record.md) state).
**Control manifest:** [week_01_full_fidelity_reset.json](week_01_full_fidelity_reset.json), now at event generation 3 (`2013-week01-reset-v3-01` through `-16`) and kernel 2013.4.

## What was deleted

- the sixteen generation-2 receipts under `../stats/game_receipts/`;
- `../league_results/week_01.md`;
- the Week 2 generation-readiness report, which only audited those receipts;
- the Week 1 result, statistics, injuries, standings and post-game role statements in the roster, register, calendar, standings, week files and current state.

The [superseded Week 1 generations and attribution corrections](week_01_full_fidelity_reset.md) remain preserved as technical history. The private journal keeps its append-only event rows; generations 1 and 2 are marked there, never deleted.

## Why the restart is allowed

The trigger was a measured engine defect, not a result. The audit compared every generation-2 receipt with sourced 2012 play-by-play: backups shared quarterback snaps in 29 of 32 team-games, receivers took about a third of carries, linebackers made 20 of about 2,050 tackles, tackles were never assisted and teams averaged about 84 plays against 64.2. Every game is replaced, not only Jacksonville's.

## Replay procedure (`Run Week 1`)

1. The private runtime must be redeployed at kernel 2013.4 and pass `python scripts/check_game_readiness.py`. A kernel mismatch fails closed.
2. Run `python scripts/mark_week1_generations_void.py` so generations 1 and 2 are marked in the private journal before any generation-3 event closes.
3. Rebuild all 32 pre-Week-1 TeamInputs in `.sim_cache/week_01_full_fidelity_inputs.json`. The 31 background clubs come from the sourced, branch-reconciled [Week 1 depth-chart library](../../../library/2013_week1_depth_charts.md) through `runtime.depth_library.team_input`; Jacksonville comes from the branch roster. Every input must be a legal game-day unit (at least 1 QB, 1 RB, 3 WR, 1 TE, 5 OL, 3 DL, 2 LB, 4 DB, K and P available) and carry explicit `depth` values at least for QB, RB, WR and TE. Linebackers must be present for every club. The generation-2 inputs were missing whole position groups for several clubs and must not be reused.
4. Jacksonville uses the September 4 roster, medical state and depth order and the recovered ex-ante call sheet in `../regular_season/week_01_kansas_city_at_jacksonville/call_sheet.json`, unless Stone amends it before the draw.
5. Run `python scripts/check_week1_reset_ready.py` (manifest, 32 inputs, branch exclusivity, game-day units and depth) until it passes.
6. Close all sixteen generation-3 events once each through `runtime.game_runner.run_game`. Preserve a full Jacksonville receipt and compact receipts for the other fifteen.
7. Rebuild every stat view with `python scripts/render_season_stats.py 2013 --team "Jacksonville Jaguars"`, including `team_stats.md` and `calibration_audit.md`. An OUTSIDE audit row is investigated as a possible input or engine defect; it is never a reason to rerun a closed game.
8. Rebuild standings, write the Week 1 output and league roundup, reconcile injuries and state, record the closure with the game output, regenerate the annual record and validate.
9. Merge before advancing the private snapshot. Stop before Week 2.

<!-- event-record: {"closure": {"checkpoint": "Canonical correction - September 4, 2013 - Week 1 voided for kernel 2013.4 restart", "original_close": "Commit closed - Canonical correction - September 4, 2013 - Week 1 voided for kernel 2013.4 restart - canonical through September 4, after regular-season cap compliance and before Week 1", "sequence": 34, "through": "2013-09-04"}, "date": "2013-09-04", "id": "2013-09-04-week-1-voided-for-kernel-2013-4-restart", "kind": "technical", "status": "closed", "summary": "Defective Week 1 generations were voided before a full replacement slate."} -->
