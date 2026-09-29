# 2014 setup and execution checklist

**Checkpoint: February 18, 2014, Entry 87.** Setup is prepared; games remain blocked. [Operating baseline](operating_baseline.md) owns the workflow, [calendar](calendar.md) the dates, and [Document 5](../../state/05_Current_Season_State.md) the current snapshot. The planning season and current record owner are deliberately separate in [repository_map.json](../../docs/repository_map.json).

| Area | Prepared now | Remaining work and gate |
|---|---|---|
| PR #135 integration | Living coaching profiles and their phase links coexist with the newer baseline, eight-pick board and phase outputs | Profiles are evidence records, not engine implementation |
| Current handoff | Entry 82 reconciled plan, staff, roster-count and next-checkpoint summaries; Entries 83-86 closed the February staff, futures and contract-status events and advanced the clock to February 17; Entry 87 recorded Monroe's February 18 franchise tag | First actual 2014 event establishes year-local current owners together |
| Contracts/cap | [2014 worksheet](offseason/current_cap_worksheet.md), corrected retired-player classification | Verify unresolved clauses, reserve/future players' credited seasons and actual 2014 obligations before affected execution |
| Staff | Mike Westhoff special teams coordinator from February 11 (Entry 84); February coaching exposure resolved with no departure (Entry 83) | Emergency succession for a caller remains unassigned |
| Training | Five linked NOT_STARTED outputs, player profiles, film queue, coach profiles | Pending role/Boot Flood/punt choices and lawful pre-program contact; no invented delivery receipts |
| Draft | 224 ordinary assets and eight Jacksonville targets | March 24 branch compensatory awards, final numbering, specific conditional holds; Linsley/Gaines and fallback dated reports; package A pick fixed at 36 and package H recorded (memo amendment, September 29, 2026) |
| Schedule | All-club 256-matchup opponent matrix and release plan | April 23 dated reconciliation, venue/bye/rest checks and frozen fixtures; no opponent matrix substituted for fixtures |
| League inputs | Offline 2,208-player research inventory | Dated movements, branch-control exclusions, draft swaps and legal 2014 Week 1 inputs |
| Tooling | Explicit season paths, separate caches/event IDs, foreign-receipt checks and season-specific preflight | Accept a complete synthetic 2014 closure after legal inputs and the new engine exist |
| Engine | E1/E2 policy and defect acceptance requirements recorded | All five Tier 1 fixes, relevant rules, calibration and accepted release remain open |
| Private service | Existing authenticated contract | Verify released kernel and merged public snapshot; no branch snapshot advancement |

## Current owners and activation

The live roster, depth chart, staff, financial history, age view and ledger still have their established 2013 paths. They are named under `current_records` in the repository map; `active_season: 2014` does not silently migrate them. At the first actual 2014 event, carry forward the verified baseline into `career/2014/ledger.md`, `roster.md`, `coaching_staff.md`, `depth_chart.json` and the applicable financial/age records, reconcile relative links, and switch the map and Documents 4/5 together. Retain prior events and final 2013 statistical views unchanged.

The [scouting index](scouting/README.md), [statbook](statbook.md), [league results](league_results/README.md), [awards](awards/README.md), [postseason](postseason/README.md) and [closeout index](closeouts/README.md) establish storage ownership only. Actual game folders follow frozen fixture assignments. Actual playoff rounds follow branch qualification. No empty result JSON, fake contract or fabricated zero-valued financial balance is created to satisfy a folder checklist.

## Command contract

Operator commands require `--season YEAR` for weekly input construction, closure, box scores and league awards. Readiness defaults to the map's active season and accepts an explicit `--season YEAR`. Standings and season-stat renderers retain their positional YEAR. Existing Python APIs default to 2013 for historical reproduction. New 2014 inputs never fall back to historical paths.

`python scripts/check_game_readiness.py --season 2014` must remain BLOCKED until the independent release checks pass. An accessible private service, green CI or a kernel name beginning with 2014 cannot override these checks. Source-based research still follows the project's two-pass verification discipline.
