# 2014 setup and execution checklist

Checkpoint: May 1, 2014. Setup is prepared; games remain blocked. The [operating baseline](operating_baseline.md) owns the workflow, the [calendar](calendar.md) the dates, and [Document 5](../../state/05_Current_Season_State.md) the current snapshot. Current record owners are mapped in [repository_map.json](../../docs/repository_map.json).

| Area | Prepared now | Remaining work and gate |
|---|---|---|
| Current records | Year-local 2014 owners for roster, working depth, staff, cap worksheet, ages and ledger; the map and Documents 4 and 5 agree. Events through May 1 are closed, including the April 18 decisions, the first two weeks of Phase One and the April 23 schedule release; 53 controlled players | Prior events stay in the [2013 ledger](../2013/ledger.md) |
| Contracts and cap | [2014 worksheet](offseason/current_cap_worksheet.md); complete dollar schedules for signed continuing and futures contracts in the [ten-year tracker](../finances/jaguars_cap.md) | Verify unresolved clauses, reserve/future players' credited seasons and actual 2014 obligations before affected execution |
| Staff | Mike Westhoff special teams coordinator from February 11; February coaching exposure resolved with no departure; living coaching profiles linked to phase evidence | Tice is the emergency practice lead, Crennel second ([April 18 decisions](offseason/stone_april_18_2014_decisions.md)); game-day caller succession remains unassigned. Profiles are evidence records, not engine implementation |
| Training | Five linked phase outputs (the offseason program [in progress](offseason/offseason_program/output.md), the others NOT_STARTED), player profiles, film queue, coach profiles and the [detailed decision package](offseason/phase_plan_decisions.md) | Dates, second-year install and the April 18 policy choices adopted; Phase One under way. The May 2 handoff, Phase Two and new role decisions still open |
| Program filing and contact | [Original-period rules verified](../../library/2014_offseason_phase_rules_verification.md); Phase One classroom teaching distinguished from field restrictions; selected schedule filed March 28 | Passive pre-program film permission unresolved; no fabricated receipts |
| Draft | Nine picks (13, 26, 38, 90, 129, 153, 168, 205, 241) in the audited 224-pick ordinary order plus 32 compensatory picks; [current board](offseason/draft/player_draft_board.md) | Dated eligibility and scouting reports for every target, Linsley, Gaines and their fallbacks included; the three conditional holds on other clubs' picks recorded in the [ownership audit](draft/ownership_audit.md) |
| Schedule | April 23 release frozen: [256 dated fixtures](schedule/fixtures.json), verified and tested; dated_fixtures gate VERIFIED | Apply dated amendments on their historical dates; two non-Jacksonville kickoff questions open in [sources](schedule/sources.md) |
| League inputs | Offline 2,208-player research inventory | Dated movements, branch-control exclusions, draft swaps and legal 2014 Week 1 inputs |
| Tooling | Explicit season paths, separate caches and event IDs, foreign-receipt checks and season-specific preflight | Accept a complete synthetic 2014 closure after legal inputs and the new engine exist |
| Engine | E1/E2 policy and defect acceptance requirements recorded | All five Tier 1 fixes, relevant rules, calibration and an accepted release remain open |
| Private service | Existing authenticated contract | Verify the released kernel and merged public snapshot; no branch snapshot advancement |

## Current owners and activation

Prior ledger events and final 2013 statistics remain archived. Game inputs still require the legal-rosters gate; the working depth file is not `depth_chart.json`. The [annual handoff](closeouts/README.md) prepares later years without simulating or copying prior statistics.

The [scouting index](scouting/README.md), [statbook](statbook.md), [league results](league_results/README.md), [awards](awards/README.md), [postseason](postseason/README.md) and [closeout index](closeouts/README.md) establish storage ownership only. Actual game folders follow frozen fixture assignments, and actual playoff rounds follow branch qualification. No empty result JSON, fake contract or fabricated zero-valued financial balance is created to satisfy a folder checklist.

## Command contract

Operator commands require `--season YEAR` for weekly input construction, closure, box scores and league awards. Readiness defaults to the map's active season and accepts an explicit `--season YEAR`. Standings and season-stat renderers keep their positional YEAR. Existing Python APIs default to 2013 for historical reproduction. New 2014 inputs never fall back to historical paths.

`python scripts/check_game_readiness.py --season 2014` must remain BLOCKED until the independent release checks pass. An accessible private service, green CI or a kernel name beginning with 2014 cannot override these checks. Source-based research still follows the project's two-pass verification discipline.
