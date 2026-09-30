# 2014 operating baseline and handoffs

Current through May 23, 2014. Jacksonville controls 78 players: 74 under signed contracts, including the eight free-agency replay signings, the six reserve/future contracts, the March 28 re-signings of Maurice Jones-Drew and C.J. Wilson, Chad Henne's April 4 re-signing, the nine 2014 draft selections (rookie contracts signed May 11) and the 17 undrafted rookies signed May 10, plus four unsigned tenders. Will Rackley was traded to Seattle May 12 for Seattle's unconditional 2015 seventh, after the May 11 calls; Brewster is kept. Russell Allen was traded to Arizona April 7 for Arizona's 2015 fourth, after Paul Posluszny's April 5 clearance. Shorts and Blackmon were traded to Indianapolis March 31, Babin and Alualu March 24, and Nwaneri March 20. The two Colts picks from that trade, Nos. 82 and 194, went to Washington the same day for Jacksonville's own 2015 second. All nine 2014 picks (13, 26, 38, 90, 129, 153, 168, 205 and 241) were exercised May 8 to 10: Donald, Bitonio, Adams, Turner, Telvin Smith, Linsley, Leno, Thomas and Butler. The offseason-program schedule was filed March 28; Stone adopted his April 18 decisions, Phase One ran April 21 to May 1 with its handoff May 2, Phase Two ran May 5 to 22 with its handoff May 23, the rookie minicamp ran May 16 and 17, and the regular-season schedule was released April 23. On May 12 Stone set rep starting points for WR1 (Nicks), WR3 (Adams), left guard (Bitonio), right guard (Turner) and Edge 1 (Mincey), each with named competition. No game has been played. Completed events are in the [2014 ledger](ledger.md); earlier ones stay in the [2013 ledger](../2013/ledger.md).

## Start here

| Work | Current input | Where the actual event is recorded |
|---|---|---|
| Contracts, tags, tenders and free agency | [Memo](offseason/stone_to_caldwell_2014_offseason_decisions.md), [contract status](offseason/contract_status_register.md), [verified target pool](offseason/league_rails/free_agent_pool.md) | [Signing and contract outcomes](offseason/free_agency/signings.md), plus affected state and accounting |
| Futures and practice squad | [Futures instructions](offseason/practice_squad_futures.md), [signings](offseason/free_agency/signings.md) | Six reserve/future contracts signed, effective March 11; credited seasons and 2014 practice-squad eligibility still to verify |
| Trade market | [Trade plan and status](trades/trade_targets.md) | [Offer log](trades/trade_offers.md), then [completed trades](trades/trades.md) |
| Draft | [Nine-pick board](offseason/draft/player_draft_board.md) (executed), [all seven rounds](draft/draft_order.md) | [Draftees and contracts](offseason/draft/draftees.md), [rails pairing](offseason/league_rails/draft_pairing.md) and [undrafted contracts](offseason/draft/udfa_signings.md), all closed in Entry 108 |
| Staff | [Staff changes and hires](offseason/staff_changes/README.md) | Mike Westhoff hired special teams coordinator February 11 after Oakland kept Bobby April; no February departure |
| Training and film | [Phase route](offseason/README.md), existing player and coach methods | Five phase output and standout pairs, living profiles linked to actual evidence, [delivery receipts](offseason/film/delivery_log.md) |
| Phase decisions | [Detailed recommendations](offseason/phase_plan_decisions.md), [period rules](../../library/2014_offseason_phase_rules_verification.md) | Schedule filed March 28; [April 18 decisions](offseason/stone_april_18_2014_decisions.md) adopted |
| Schedule | [Schedule records](schedule/README.md), [calendar](calendar.md) | [Frozen 256-game fixtures](schedule/fixtures.json) from the April 23 release |
| Camp and preseason | [Camp plan](offseason/training_camp/plan.md), [position questions](offseason/training_camp/position_battles.md) | Camp output, role decisions, game records, [75/53/squad closure](preseason/final_roster_cuts.md) |
| Regular season and postseason | [17-week index](regular_season/README.md), conditional dates in the calendar | Actual weekly outputs and receipts, generated stats and standings, and the event ledger |

## Current ownership and season handoff

The [2014 roster](roster.md), [working depth](offseason/depth_chart_working.json), [staff](coaching_staff.md), [cap worksheet](offseason/current_cap_worksheet.md), [ages](player_ages.md) and [ledger](ledger.md) are the current owners in the repository map. The 2013 final statistics and awards remain their own season's history. The working depth file is not a game-input release.

[Annual closeout](closeouts/README.md) uses a single manifest for contracts, finances, roles, medical, staff, draft assets, development and history. It stages a reviewed successor after exit interviews and team closeout; unfinished league history remains explicitly open. 2015 and 2016 have isolated runtime paths and remain game-blocked until their own acceptance.

The generated 2,208-player league inventory is research data with unknown contracts and statuses, not a legal game-day roster. Other clubs' dated 2014 rosters are built automatically at their prescribed gates, with Jacksonville control and draft swaps applied and specific relevant exceptions resolved. The user is not assigned to hand-fill 31 rosters.

## Decisions and facts still pending

- The [phase decision package](offseason/phase_plan_decisions.md) records the adopted choices, including the April 18 decisions and the May 1 revision of the cross-training list. No film packet has been issued; the January 31 receipts remain unverified. The four players on unsigned tenders are outside the program and the social calendar until they sign.
- Draft: closed. Every first choice was taken except at No. 205, where Gaines and Cockrell were gone and Stone named Jemea Thomas. James Hurst stays on a medical hold on the undrafted board; Alan Ball was not re-signed May 12 and is first on the veteran-corner call list; the five starting roles are open competitions from their May 12 starting points, and every other rookie's place is Stone's decision from the work.

## Before any 2014 game

This baseline supports offseason operations. It is not game authorization. [The defect register](../../runtime/defect_register.md), [approved E1/E2 policy](../../runtime/2014_engine_decisions.md) and [readiness checks](../../state/game_readiness.md) remain controlling.

E1 requires dated player and job evidence, available lineups and coaching and matchup tradeoffs through the common resolver. Branch 2013 records are not talent evidence and Jacksonville gets no bonus. E2 requires actual mid-game removal, important user-side substitution pauses and functioning backup quarterbacks. Clock, fourth-down and injury-rate Tier 1 defects also remain open. Adding folders fixes nothing.

The game release also needs season-aware roster, closure and stat consumers (the dated fixtures are frozen), dated 2014 league inputs, control exclusivity, calibration and a validated kernel version. The existing 2013 runner must not silently execute a 2014 request with old data. These are engineering work to close before the preseason, not a hand-maintenance assignment for Stone. The ordinary repository check validates continuity and prepared records; a green result does not supersede the game gate.

## Setup acceptance and remaining work

[The readiness checklist](readiness.md) separates prepared records from executable work. The [financial preparation worksheet](offseason/current_cap_worksheet.md) remains unreconciled. `runtime/seasons.py` supplies season paths and `runtime/season_readiness.json` records the independent 2014 release requirements. Neither path routing nor an accessible private runtime accepts the outstanding Tier 1 engine work.
