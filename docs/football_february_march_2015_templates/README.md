# February Re-signings and March Free Agency | NFL head-coach career workflow

**Status:** Research-backed proposed Markdown templates and implementation specification. These files do not modify the GitHub repository, resolve any 2014 or 2015 career event, issue an official in-world briefing or make a player sign. Designed for the move from the simulated 2014 Jacksonville season to the **2015 NFL league year**, and repeatable for other seasons with their own historical rules.

## What to use

| Phase | The staff brief | Stone's page | Phase result | Individual result |
|---|---|---|---|---|
| February retention | [`February_Re_Signings/Re_Signing_Report_TEMPLATE.md`](February_Re_Signings/Re_Signing_Report_TEMPLATE.md) | [`February_Re_Signings/My_Re_Signing_Priorities_TEMPLATE.md`](February_Re_Signings/My_Re_Signing_Priorities_TEMPLATE.md) | [`February_Re_Signings/Front_Office_Moves_TEMPLATE.md`](February_Re_Signings/Front_Office_Moves_TEMPLATE.md) | [`February_Re_Signings/Individual_Retention_Result_TEMPLATE.md`](February_Re_Signings/Individual_Retention_Result_TEMPLATE.md) |
| March outside free agency | [`March_Free_Agency/Pro_Personnel_Report_TEMPLATE.md`](March_Free_Agency/Pro_Personnel_Report_TEMPLATE.md) | [`March_Free_Agency/My_Free_Agent_Priorities_TEMPLATE.md`](March_Free_Agency/My_Free_Agent_Priorities_TEMPLATE.md) | [`March_Free_Agency/Free_Agency_Results_TEMPLATE.md`](March_Free_Agency/Free_Agency_Results_TEMPLATE.md) | [`March_Free_Agency/Individual_Free_Agent_Result_TEMPLATE.md`](March_Free_Agency/Individual_Free_Agent_Result_TEMPLATE.md) |

**Additional:** [`Shared/Implementation_Spec.md`](Shared/Implementation_Spec.md) contains schema/routing, calendar/authority and 36 proposed validation tests. [`Shared/2014_Into_2015_Worked_Illustration.md`](Shared/2014_Into_2015_Worked_Illustration.md) demonstrates the 2014 checkpoint and real prior branch negotiations without making up any 2015 result.

## Central operating rules

1. One current phase briefing at a time, but later genuine events may update it by issuing a new immutable edition; never change what the coach already received.
2. Stone answers through the fixed My page. His recommendations are not Caldwell's contract decisions and never automatically execute a deal.
3. One distinct **concluded event**, one separate dated output, including real declined offers, withdrawn offers, tender filings, signed extensions and executed free-agent contracts. The phase report is the index to those files, not their replacement. A pending conversation is not a completed negotiation.
4. When the 2015 career year starts, the 2014 player roster, medical status, draft assets, payroll and expired contracts must carry forward from real completed branch outcomes, not from the real Jaguars' offseason. Do not treat early-October 2014 player contracts as a final February board.
5. The March 2 official NFL salary cap can be stated only once that date has arrived in the simulated calendar. The **real** Jaguars' 2015 cap space/adjusted cap was the product of the real Jaguars' finances; never import it here.
6. Keep current regular season and postseason results, game plans, league-player outcomes and all closed historical reports unchanged. Template work is not permission to advance the clock.

## Verified rule and research sources

- [Jacksonville Jaguars: 2015 NFL Important Dates](https://www.jaguars.com/news/2015-nfl-important-dates-14709246), pre-2015-season notice. February 16 through March 2 tags, March 7 to 10 negotiation window, March 10 league-year start, tenders and Top-51 deadlines.
- [Buffalo Bills: Important Dates on the 2015 NFL Calendar](https://www.buffalobills.com/news/important-dates-on-the-2015-nfl-calendar-14905495), February 12, 2015. Additional April 24/29 RFA deadlines and personnel windows.
- [NFL Communications: 2015 Free Agency FAQ](https://www.seahawks.com/news/2015-nfl-free-agency-faq-120736), published March 10, 2015. Legal categories, accrued seasons, franchise/transition and offer sheets, cap.
- [NFL: March 7, 2015 negotiating period](https://www.nfl.com/_amp/nfl-s-three-day-negotiating-period-underway-0ap3000000477176). Distinguishes permitted agent discussions from enforceable offers or new-club contracts.
- [NFL: March 9, 2015 memo on early agreements](https://www.nfl.com/news/nfl-sends-teams-memo-about-early-agreements-0ap3000000477438). Specifically prohibits official offers and agreements during the period.
- [NFLPA: 2015 NFL Salary Cap and Adjusted Team Positions](https://nflpa.com/press/2015-nfl-salary-cap-and-adjusted-team-positions), dated March 2, 2015. League-wide cap $143.28m. Real-team financial figures *not usable* for counterfactual Jacksonville.
- [2011 Collective Bargaining Agreement (original)](https://nflps.org/wp-content/uploads/2012/05/collective-bargaining-agreement-2011-2020.pdf), Article 7 on rookie contracts and when renegotiation is permitted. Primary era source.
- Existing project: `foundation/03_Head_Coach_Organization_and_Authority_Canon.md`, `state/current_job.json`, `runtime/decisions.py`, `docs/season_cycle_milestones.md`, `docs/rebuild_plan.md`, and era-specific contract/market records in `career/2014` and `career/finances`.

## Explicit gaps before implementation

- 2014 Weeks 6 through 17, any Jacksonville playoffs and the completed 2014 season review: **not yet played**. No final retention board can be populated today.
- The project's 2015 confirmed adjusted cap, carryover election, 2015 financial owner and cash budget must be derived and reconciled from the branch before contract execution. Historic league-wide cap is known only when its date arrives.
- The next-season market procedure, player statuses and independent acceptance mechanism need a 2015-specific precommitted implementation. A narrative template cannot repair or replace the market model.
- `runtime/decisions.py` registers both workflows but does not mark either implemented. The template page filenames and source-of-truth location must be wired to validators and the actual folder map, not manually copied into the active career.
