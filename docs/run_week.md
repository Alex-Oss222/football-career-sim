# Run-week prompt

Use this when handing a regular-season week to the runner (Claude Code; see `CLAUDE.md`).

```text
Run Week [N].

Use the repository's one-command Run Week workflow in AGENTS.md.
Resolve all internal readiness, migration/reset, background-team input, statbook, standings, snapshot and PR prerequisites yourself.
Do not ask me to edit manifests, run helper scripts, research rosters, touch Railway or perform intermediate setup.

Plan:
[PASTE STONE'S WEEKLY PLAN HERE, or write "use the already-closed ex-ante plan" for an authorized rerun]

Run Week [N] only and stop before Week [N+1].
```

The 2013 Week 1 restart (generation 3 under kernel 2013.4) is closed history: see [career/2013/migrations/week_01_kernel_2013_4_restart.md](../career/2013/migrations/week_01_kernel_2013_4_restart.md) (ledger Entry 35).

A current week needs these inputs from Stone before `python scripts/build_week_inputs.py N --season YEAR` can freeze the slate: the week's plan frozen as `call_sheet.json` at `SeasonPaths(YEAR).call_sheet(N)` (2014: `data/2014/Regular_Season/Games/Week_NN/call_sheet.json`; 2013: `career/2013/regular_season/week_NN_<away>_at_<home>/call_sheet.json`), without which the builder blocks; any open role decision the plan must settle, such as the weekly center evaluation; and the game-day inactives, written to `game_day_inactives` in `SeasonPaths(YEAR).depth_chart` (2014: `data/2014/Team_Operations/Team/Depth_Chart/game_depth_chart.json`; 2013: `career/2013/depth_chart.json`), where a week without a new list reuses the last one. Under kernel 2014.6 the builder reads three parts of the call sheet: `offensive_call_sheet` (required), `decisions` (Stone's standing two-point, kickoff and optional fourth-down blocks; required under 2014.6, which decides two-point tries and onside kicks) and `defensive_call_sheet` (optional, records only). The [games and statistical evidence](update_workflow.md#games-and-their-statistical-evidence) section of the update workflow gives the commands that follow. The private snapshot stays on the last merged canonical state until the public PR is merged; only a merged `main` checkout may advance it.

The [decision queue](../state/decision_queue.json) holds a week until Stone's decisions for it are recorded ([career layer](career_layer.md)). `build_week_inputs.py` and `close_week.py --close` (with or without `--continue`) refuse with exit 1 while an open item names the week or a part of its committed call sheet; the dry run of `close_week.py` lists the same items as notes. Only an item owned by Stone becomes a question for the user. When a week closes, the closing commit opens the `weekly_game_plan` item and, unless a standing instruction covers them, the `game_day_inactives` item for the next week in which Jacksonville plays; a bye week gets none. The week's packet resolves them `by: "user"`. An open item that still holds a closed week fails validation. Stone's standing fourth-down rule is in force and is frozen into each week's call sheet as its `decisions.fourth_down` block, which the game applies at the actual fourth-down distance and spot; no fourth-down item is opened for a week or carried to the next. Neither the queue nor Document 5 changes while a game is paused.

From 2014 Week 6 the week's result page is the Game Report (`SeasonPaths(YEAR).game_report(N)`, `Game_Report.md` in the week's folder; Weeks 1 to 5 keep `output.md`), written from the [Game Report template](../foundation/templates/regular_season_output_template.md). After the close: fill its box score with `render_box_score.py --season YEAR --write <Game_Report.md>`, bring the roster record up to the game, run `render_week_pages.py --season YEAR` (the Games and league-results indexes, the league-results week page, the injury report, the medical history's game entry and the new incident records), write the highlights under the league-results page's game headings, then `render_annual_record.py YEAR`. The [update workflow](update_workflow.md#games-and-their-statistical-evidence) gives the details.

## Generated-data rule

Every club dresses at most 46 players. Jacksonville's inactives are Stone's list in `game_day_inactives` of `SeasonPaths(YEAR).depth_chart`; a background club's are chosen mechanically from the bottom of its depth order (`runtime.week_inputs.game_day_actives`), never from a real historical inactive list, and the weekly gate rejects a TeamInput with more than 46 actives.

The one-command workflow keeps large reconstructed TeamInputs in the gitignored `.sim_cache/` workspace. Jacksonville/protagonist games preserve full snap/stat receipts; ordinary background games preserve `compact_stats` receipts with complete nonzero generated statistics but no background snap ledger. The runner must use these bounded-storage paths automatically rather than failing the task because the generated Git diff is too large.

**Season routing:** use the requested NFL season for YEAR, including January/February postseason games. Weekly input, closure, box-score and league-award commands require `--season YEAR`; readiness defaults to `docs/repository_map.json` active_season and can be checked explicitly with `--season YEAR`. Current record ownership follows that map separately. The 2014 release requirements remain blocking even when legacy readiness flags are VERIFIED.
