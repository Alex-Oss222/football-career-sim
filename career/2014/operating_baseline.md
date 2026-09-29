# 2014 operating baseline and handoffs

**Prepared at the February 2, 2014 checkpoint; current through March 18, 2014 (Entry 98).** This is the 2014 working structure for the offseason and eventual season. No offer, signing, trade, training phase, draft selection or game is completed by preparing it. Monroe was designated non-exclusive franchise player on February 18 (Entry 87); his tender became official at $11,654,000 when the league published the 2014 cap ($133,000,000) and tag values on February 28 (Entry 89), and it is not yet signed. The Combine closed February 25; its evidence is in `library/2014_combine_results.md` (Entry 88). The March 3 designation deadline passed with no further Jacksonville designation (Entry 92). The league year opened at 4 p.m. March 11 (Entry 94): tenders made, futures in force, and Entry 95's free-agency replay signed Monroe, Marks and Verner, Entry 96 signed Talib, Entry 97 signed Nicks and Hawkins (Tate and Edelman went elsewhere), and Entry 98 signed Te'o-Nesheim; Cain, Henne and the trade packages remain open. The next dated events are the held market draws from March 12 and Nwaneri's March 25 roster-bonus date.

## Start here

| Work | Current input | Where the actual event will be recorded |
|---|---|---|
| Contract/tag/tender and free agency | [Memo](offseason/stone_to_caldwell_2014_offseason_decisions.md), [contract status](offseason/contract_status_register.md), [verified target pool](offseason/league_rails/free_agent_pool.md) | [Signing/contract outcomes](offseason/free_agency/signings.md), plus affected state/accounting |
| Futures and practice squad | [Futures instructions](offseason/practice_squad_futures.md), [signings](offseason/free_agency/signings.md) | Six reserve/future contracts signed (Entry 85), effective March 11; credited seasons and 2014 practice-squad eligibility still to verify |
| Trade market | [Current packages and their gates](trades/trade_targets.md) | [Communications](trades/trade_offers.md), then [completed trades](trades/trades.md) |
| Draft | [Eight-pick current board](offseason/draft/player_draft_board.md), [all seven rounds](draft/draft_order.md) | [Draftees/contracts](offseason/draft/draftees.md), [rails pairing](offseason/league_rails/draft_pairing.md), [UDFA contracts](offseason/draft/udfa_signings.md) |
| Staff | [Staff changes and hires](offseason/staff_changes/README.md) | Westhoff hired February 11 (Entry 84); no February departure (Entry 83) |
| Training and film | [Phase route](offseason/README.md), existing player/coach methods | Five phase output/standout pairs, living profiles linked to actual evidence, [delivery receipts](offseason/film/delivery_log.md) |
| Phase decisions and schedule filing | [Detailed recommendations](offseason/phase_plan_decisions.md), [period rules](../../library/2014_offseason_phase_rules_verification.md) | Actual decisions and filing receipts when made; preparing the package adopts nothing |
| Schedule | [Full opponent matrix](schedule/README.md), [calendar](calendar.md) | Dated 256-game fixtures at April 23 after league-wide reconciliation |
| Camp/preseason | [Camp plan](offseason/training_camp/plan.md), [position questions](offseason/training_camp/position_battles.md) | Camp output, role decisions, game records, [75/53/squad closure](preseason/final_roster_cuts.md) |
| Regular season and postseason | [17-week index](regular_season/README.md), conditional dates in calendar | Actual weekly outputs/receipts, generated stats/standings and event ledger |

## Current ownership and season handoff

The [2013 roster](../2013/roster.md), [depth chart](../2013/depth_chart.json), [coaching staff](../2013/coaching_staff.md), [Document 4](../../state/04_Roster_and_Staff_Register.md), [Document 5](../../state/05_Current_Season_State.md) and [2013 ledger](../2013/ledger.md) remain the live owners named by the current checkpoint. February dates do not justify copying a stale 2013 roster into a competing live owner. The draft ownership/order files already live under 2014.

At the first event that establishes a 2014 ledger/roster owner, carry forward the verified current baseline, link its prior event, record only the actual new result and reconcile all state pointers in the same commit. The event operator owns this migration. Do not abandon open guarantees, medical restrictions, conditional assets, film obligations or staff authority during the year-folder change. Final 2013 stats/standings remain archived; initialize 2014 views from 2014 receipts only when the runtime is season-aware.

The generated 2,208-player league inventory is research data with unknown contracts/statuses. It is not a legal game-day roster. Build other clubs' dated 2014 rosters automatically at their prescribed gates, apply Jacksonville control and swaps, and resolve specific relevant exceptions. The user is not assigned to hand-fill 31 rosters.

## Decisions and facts still pending

- Package A asks for Seattle's original second, No. 36 (user amendment, September 29, 2026). Package H (No. 36 and Nwaneri to Minnesota for No. 31, for DeMarcus Lawrence) follows only if A closes.
- Package G retains actual Posluszny clearance and must finish by April 21. No buyer, compensation or cap saving is presumed. Nwaneri's bonus date/clauses still require verification before F1.
- The special-teams search is closed: Oakland re-signed Bobby April and refused the lateral request; Mike Westhoff was hired as special teams coordinator on February 11 (Entry 84).
- The [phase decision package](offseason/phase_plan_decisions.md) covers the pending dates, install and phase-plan choices. The program schedule must be filed by the agreed date, no later than March 31 for an April 21 start. Pre-program coach-led football study is prohibited; passive film distribution remains unresolved. Existing adopted individual-development methods remain adopted. Five prepared NOT_STARTED outputs do not resolve pending choices or create delivery receipts.
- Linsley and Gaines are current targets. Fallbacks (memo amendment, September 29, 2026): Paradis, then Stork, then Swanson for Linsley; Cockrell for Gaines, then Butler in round 7. Later overall numbers await compensatory awards. Eligibility, pre-selection reports and availability remain normal draft-date prerequisites.

## Before any 2014 game

This baseline supports offseason operations. It is **not game authorization**. [The defect register](../../runtime/defect_register.md), [approved E1/E2 policy](../../runtime/2014_engine_decisions.md) and [readiness checks](../../state/game_readiness.md) remain controlling.

E1 requires dated player/job evidence, available lineups and coaching/matchup tradeoffs through the common resolver. Branch 2013 records are not talent evidence and Jacksonville gets no bonus. E2 requires actual mid-game removal, important user-side substitution pauses and functioning backup quarterbacks. Clock, fourth-down and injury-rate Tier 1 defects also remain open. No fix is claimed by adding folders.

The game release also needs season-aware fixture/roster/closure/stat consumers, dated 2014 league inputs, control exclusivity, calibration and a validated kernel version. The existing 2013 runner must not silently execute a 2014 request with old data. Close these as engineering work before preseason, not as a hand-maintenance assignment for Stone. The ordinary repository check validates continuity and prepared records; a green result does not supersede the game gate.

## Setup acceptance and remaining work

[The readiness checklist](readiness.md) distinguishes prepared records from executable work. The [financial preparation worksheet](offseason/current_cap_worksheet.md) remains unreconciled. `runtime/seasons.py` supplies season paths; `runtime/season_readiness.json` records the independent 2014 release requirements. Neither path routing nor an accessible private runtime accepts the outstanding Tier 1 engine work. The current-record map preserves the established owners until one atomic season handoff.
