# 2014 setup and execution checklist

**Checkpoint: March 20, 2014, Entry 99.** Setup is prepared; games remain blocked. [Operating baseline](operating_baseline.md) owns the workflow, [calendar](calendar.md) the dates, and [Document 5](../../state/05_Current_Season_State.md) the current snapshot. The planning season and current record owner are deliberately separate in [repository_map.json](../../docs/repository_map.json).

| Area | Prepared now | Remaining work and gate |
|---|---|---|
| PR #135 integration | Living coaching profiles and their phase links coexist with the newer baseline, eight-pick board and phase outputs | Profiles are evidence records, not engine implementation |
| Current handoff | Entry 82 reconciled plan, staff, roster-count and next-checkpoint summaries; Entries 83-86 closed the February staff, futures and contract-status events and advanced the clock to February 17; Entry 87 recorded Monroe's February 18 franchise tag; Entry 88 closed the Combine week; Entry 89 recorded the league's February 28 cap and tag figures; Entries 90-91 completed the contract schedules; Entry 92 passed the March 3 designation deadline; Entry 93 closed the March 1-3 rails gap; Entry 94 opened the league year; Entries 95 to 99 recorded the free-agency replay and package I (55 controlled players) | A later explicit season-owner handoff establishes year-local current owners together; closed February events remain in the current ledger |
| Contracts/cap | [2014 worksheet](offseason/current_cap_worksheet.md), corrected retired-player classification | Verify unresolved clauses, reserve/future players' credited seasons and actual 2014 obligations before affected execution |
| Staff | Mike Westhoff special teams coordinator from February 11 (Entry 84); February coaching exposure resolved with no departure (Entry 83) | Emergency succession remains unassigned; [specific recommendations](offseason/phase_plan_decisions.md#10-staff-responsibilities-and-emergency-succession) await Stone's call |
| Training | Five linked NOT_STARTED outputs, player profiles, film queue, coach profiles and [detailed decision package](offseason/phase_plan_decisions.md) | Dates/install and remaining policy choices; feedback, shared-identification teaching and continuing individual development already adopted; Boot Flood release and new roles remain separate decisions |
| Program filing and contact | [Original-period rules verified](../../library/2014_offseason_phase_rules_verification.md); Phase One classroom teaching distinguished from field restrictions | Schedule due at agreed league date, no later than March 31 for April 21; actual filing and passive pre-program film permission unresolved; no fabricated receipts |
| Draft | 224 ordinary assets and eight Jacksonville targets | March 24 branch compensatory awards, final numbering, specific conditional holds; Linsley/Gaines and fallback dated reports; package A pick fixed at 36 and package H recorded (memo amendment, September 29, 2026) |
| Schedule | All-club 256-matchup opponent matrix and release plan | April 23 dated reconciliation, venue/bye/rest checks and frozen fixtures; no opponent matrix substituted for fixtures |
| League inputs | Offline 2,208-player research inventory | Dated movements, branch-control exclusions, draft swaps and legal 2014 Week 1 inputs |
| Tooling | Explicit season paths, separate caches/event IDs, foreign-receipt checks and season-specific preflight | Accept a complete synthetic 2014 closure after legal inputs and the new engine exist |
| Engine | E1/E2 policy and defect acceptance requirements recorded | All five Tier 1 fixes, relevant rules, calibration and accepted release remain open |
| Private service | Existing authenticated contract | Verify released kernel and merged public snapshot; no branch snapshot advancement |

## Current owners and activation

The live roster, depth chart, staff, financial history, age view and ledger still have their established 2013 paths. They are named under `current_records` in the repository map; `active_season: 2014` does not silently migrate them. At the next authorized event that establishes the 2014 current-record owners, carry forward the verified baseline into `career/2014/ledger.md`, `roster.md`, `coaching_staff.md`, `depth_chart.json` and the applicable financial/age records, reconcile relative links, and switch the map and Documents 4/5 together. Retain prior events and final 2013 statistical views unchanged.

The [scouting index](scouting/README.md), [statbook](statbook.md), [league results](league_results/README.md), [awards](awards/README.md), [postseason](postseason/README.md) and [closeout index](closeouts/README.md) establish storage ownership only. Actual game folders follow frozen fixture assignments. Actual playoff rounds follow branch qualification. No empty result JSON, fake contract or fabricated zero-valued financial balance is created to satisfy a folder checklist.

## Command contract

Operator commands require `--season YEAR` for weekly input construction, closure, box scores and league awards. Readiness defaults to the map's active season and accepts an explicit `--season YEAR`. Standings and season-stat renderers retain their positional YEAR. Existing Python APIs default to 2013 for historical reproduction. New 2014 inputs never fall back to historical paths.

`python scripts/check_game_readiness.py --season 2014` must remain BLOCKED until the independent release checks pass. An accessible private service, green CI or a kernel name beginning with 2014 cannot override these checks. Source-based research still follows the project's two-pass verification discipline.

## Phase-plan folder sweep, September 29, 2026

Reviewed the 2014 folder inventory and local Markdown links, all five plan/output/evidence triplets, the phase decision register, current staff and futures references, medical/role boundaries and the proposed calendar. The existing folders cover the required work; no duplicate roster owner or empty result folder was added.

- Corrected stale Stone special-teams coverage, Bray's contract condition, the camp statement treating pending proposals as adopted, and the minicamp's inconsistent defensive-relay wording.
- Distinguished the research database's February 2 cutoff from the live clock, removed the obsolete film-queue claim that the roster still said 53 active, and clarified that closed February events precede the eventual season-owner handoff.
- Linked the detailed decision package throughout the phase/staff indexes and registered both new documents for repository validation. Existing signed futures now have participation conditions rather than hypothetical signing conditions in their development opportunities.
- Verified the schedule-filing lead, proposed nine-week structure, ten distinct weekday OTAs in three/three/four blocks and minicamp's final-week placement. New internal review and family-event dates remain explicitly proposed.
- Repository continuity validation passes. All five phase outputs and five evidence summaries remain NOT_STARTED. The 2014 game-readiness check remains BLOCKED by the separate release/input requirements; no game readiness, transaction, role, medical clearance, delivery or time advance is claimed.

## Contract, depth-chart and readability review

Reconciled the current views against the merged February 28 checkpoint, Entry 89. The contract table covers 52 active players, Meester on Reserve/Retired and six March 11 futures, for 59 unique rows. The working chart preserves the existing 52-player order, flags seven pending UFAs, three RFAs, three ERFAs, Monroe's unsigned franchise tender and two unresolved contracts, and keeps futures outside the ranked groups. No role, clearance or transaction was created.

Corrected Monroe's prior-year comparison wording, the C.J. Wilson arithmetic assertion, John Parker Wilson's unverified contract label and the suggestion that Bray already owns QB3. Updated source pointers and separated completed corrections from remaining accounting questions. The 13 exact scheduled charges sum to $17,618,182; adding Monroe's $11,654,000 tender gives $29,272,182. Both are partial figures, not Top-51 commitments or available cap space.

Removed the Coach Sheet's repeated citation codes while retaining all 114 capabilities and named supporting sources. Phase plans now use decision names, with the older policy labels retained once in the decision register. Repository writing guidance applies the same approach to later work. Validation includes a player-by-player comparison of the roster, contract rows and both working-chart formats, arithmetic checks and local links/anchors.

**Entry 91 financial follow-up:** Wilson and Jonathan Grimes are signed through 2014 under the completed terms; all six futures run through 2015. The 59-player inventory, carried depth order, medical holds and unsigned tender are unchanged. All 44 signed continuing/futures contracts have full dollar schedules in the [ten-year tracker](../finances/jaguars_cap_2014_2023.md). This closes their missing contract terms without releasing the separate game gates.
