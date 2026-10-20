# February Re-signings + March Free Agency: implementation contract

**Status:** Uploaded by the user on October 20, 2026 and adopted; built in step 7 of the [rebuild plan](rebuild_plan.md). The templates are in [foundation/templates/re_signing/](../foundation/templates/re_signing/) (February) and [foundation/templates/free_agency/](../foundation/templates/free_agency/) (March) and the worked example is [docs/examples/re_signing_and_free_agency_2014_into_2015.md](examples/re_signing_and_free_agency_2014_into_2015.md).

As uploaded: **Status:** Proposed workflow and tests, not installed or executed. The active simulated career is at October 5, 2014 after Week 5; no 2014 final season record or 2015 player transaction is supplied by this proposal.

## February Re-signings and March Free Agency | NFL head-coach career workflow

**Status:** Research-backed proposed Markdown templates and implementation specification. These files do not modify the GitHub repository, resolve any 2014 or 2015 career event, issue an official in-world briefing or make a player sign. Designed for the move from the simulated 2014 Jacksonville season to the **2015 NFL league year**, and repeatable for other seasons with their own historical rules.

### What to use

| Phase | The staff brief | Stone's page | Phase result | Individual result |
|---|---|---|---|---|
| February retention | [`re_signing/re_signing_report_template.md`](../foundation/templates/re_signing/re_signing_report_template.md) | [`re_signing/my_re_signing_priorities_template.md`](../foundation/templates/re_signing/my_re_signing_priorities_template.md) | [`re_signing/front_office_moves_template.md`](../foundation/templates/re_signing/front_office_moves_template.md) | [`re_signing/retention_result_template.md`](../foundation/templates/re_signing/retention_result_template.md) |
| March outside free agency | [`free_agency/pro_personnel_report_template.md`](../foundation/templates/free_agency/pro_personnel_report_template.md) | [`free_agency/my_free_agent_priorities_template.md`](../foundation/templates/free_agency/my_free_agent_priorities_template.md) | [`free_agency/free_agency_results_template.md`](../foundation/templates/free_agency/free_agency_results_template.md) | [`free_agency/free_agent_result_template.md`](../foundation/templates/free_agency/free_agent_result_template.md) |

**Additional:** This document contains schema/routing, calendar/authority and 36 proposed validation tests. [`examples/re_signing_and_free_agency_2014_into_2015.md`](examples/re_signing_and_free_agency_2014_into_2015.md) demonstrates the 2014 checkpoint and real prior branch negotiations without making up any 2015 result.

### Central operating rules

1. One current phase briefing at a time, but later genuine events may update it by issuing a new immutable edition; never change what the coach already received.
2. Stone answers through the fixed My page. His recommendations are not Caldwell's contract decisions and never automatically execute a deal.
3. One distinct **concluded event**, one separate dated output, including real declined offers, withdrawn offers, tender filings, signed extensions and executed free-agent contracts. The phase report is the index to those files, not their replacement. A pending conversation is not a completed negotiation.
4. When the 2015 career year starts, the 2014 player roster, medical status, draft assets, payroll and expired contracts must carry forward from real completed branch outcomes, not from the real Jaguars' offseason. Do not treat early-October 2014 player contracts as a final February board.
5. The March 2 official NFL salary cap can be stated only once that date has arrived in the simulated calendar. The **real** Jaguars' 2015 cap space/adjusted cap was the product of the real Jaguars' finances; never import it here.
6. Keep current regular season and postseason results, game plans, league-player outcomes and all closed historical reports unchanged. Template work is not permission to advance the clock.

### Verified rule and research sources

- [Jacksonville Jaguars: 2015 NFL Important Dates](https://www.jaguars.com/news/2015-nfl-important-dates-14709246), pre-2015-season notice. February 16 through March 2 tags, March 7 to 10 negotiation window, March 10 league-year start, tenders and Top-51 deadlines.
- [Buffalo Bills: Important Dates on the 2015 NFL Calendar](https://www.buffalobills.com/news/important-dates-on-the-2015-nfl-calendar-14905495), February 12, 2015. Additional April 24/29 RFA deadlines and personnel windows.
- [NFL Communications: 2015 Free Agency FAQ](https://www.seahawks.com/news/2015-nfl-free-agency-faq-120736), published March 10, 2015. Legal categories, accrued seasons, franchise/transition and offer sheets, cap.
- [NFL: March 7, 2015 negotiating period](https://www.nfl.com/_amp/nfl-s-three-day-negotiating-period-underway-0ap3000000477176). Distinguishes permitted agent discussions from enforceable offers or new-club contracts.
- [NFL: March 9, 2015 memo on early agreements](https://www.nfl.com/news/nfl-sends-teams-memo-about-early-agreements-0ap3000000477438). Specifically prohibits official offers and agreements during the period.
- [NFLPA: 2015 NFL Salary Cap and Adjusted Team Positions](https://nflpa.com/press/2015-nfl-salary-cap-and-adjusted-team-positions), dated March 2, 2015. League-wide cap $143.28m. Real-team financial figures *not usable* for counterfactual Jacksonville.
- [2011 Collective Bargaining Agreement (original)](https://nflps.org/wp-content/uploads/2012/05/collective-bargaining-agreement-2011-2020.pdf), Article 7 on rookie contracts and when renegotiation is permitted. Primary era source.
- Existing project: `foundation/03_Head_Coach_Organization_and_Authority_Canon.md`, `state/current_job.json`, `runtime/decisions.py`, `docs/season_cycle_milestones.md`, `docs/rebuild_plan.md`, and era-specific contract/market records in `career/2014` and `career/finances`.

### Explicit gaps before implementation

- 2014 Weeks 6 through 17, any Jacksonville playoffs and the completed 2014 season review: **not yet played**. No final retention board can be populated today.
- The project's 2015 confirmed adjusted cap, carryover election, 2015 financial owner and cash budget must be derived and reconciled from the branch before contract execution. Historic league-wide cap is known only when its date arrives.
- The next-season market procedure, player statuses and independent acceptance mechanism need a 2015-specific precommitted implementation. A narrative template cannot repair or replace the market model.
- `runtime/decisions.py` registers both workflows but does not mark either implemented. The template page filenames and source-of-truth location must be wired to validators and the actual folder map, not manually copied into the active career.

## 1. Fixed page architecture

The established registry names six primary pages:

| Phase | Staff brief | Stone's fill-in page | Phase result |
|---|---|---|---|
| February retention | `Re_Signing_Report.md` | `My_Re_Signing_Priorities.md` | `Front_Office_Moves.md` |
| March free agency | `Pro_Personnel_Report.md` | `My_Free_Agent_Priorities.md` | `Free_Agency_Results.md` |

All six belong in the **appropriate upcoming league year's** `Team_Operations/Free_Agency` logical folder as the current `runtime.decisions.REGISTRY` resolves it, not duplicated in the just-finished season. A season's date/year and the league year being entered remain explicit. Use `SeasonPaths.record('offseason/free_agency')` or equivalent folder map; do not guess a filepath based on 2014's old layout.

- The staff/GM brief is built from dated, visible, current source records, not from Stone's answer or future outcomes.
- Stone's document has fixed readable headings and is never silently rewritten after he answers.
- The phase result is a concise **index and synthesis** of actual completed actions. It is not the sole record of multiple deals.
- **Every distinct resolved player negotiation, tag, tender, offer or signing event has one separate dated Markdown output at its true contract/personnel event owner.** A completed rejection or withdrawal has its own result. If one player generates separate legal actions at different dates (e.g. a franchise designation later replaced by a negotiated contract), they are distinct linked events, not overwritten. An open negotiation is process history, not falsely 'closed, no deal'.
- A brief may contain any number of `ACTION REQUIRED`, `FOR YOUR INFORMATION`, and `COMING UP` inserts under the existing shared event-insert contract; an event's result always lives in its own output, not the brief or weekly/phase overview.
- When a substantive event changes what Stone needs to know, issue a fresh **immutable** brief and preserve what he previously received, with issue date and content digest in the active issue-history owner.

## 2. Authority and decision ownership

Refer to `state/current_job.json`, Document 3 rows 3, 3a, 4, 5, 6, 7 and 20. At the October 5, 2014 checkpoint:

- Caldwell owns player acquisition selection, trade execution, negotiation, contract execution, tenders and cap. Stone can advise on football use, development, retention and replacement; he does not have a player-contract veto or a unilateral signature.
- A major intended-franchise-quarterback commitment requires Stone's **written football projection and consultation with Caldwell**, not Stone's approval. The user controls that actual projection when due.
- Stone owns game plans, team football roles and authorized personnel deployment, within legal roster/medical limits. A player signing does not name a starter or automatically change the offensive/defensive playbook.
- Owners, agents, players, rival clubs, medical staff and league offices make their own decisions. Their answers must not be generated to reward Stone's enthusiasm, his naming of a player, or the length of his prose. If Stone no longer holds this job after the season-end Club Decision, do not issue Jacksonville personnel briefs to him.

A Caldwell decision and Stone's recommendation are **not** one event. A genuine owner/GM request for Stone's view opens an item on the decision queue only when the next authorized action requires it. No arbitrary weekly or daily approval prompts.

## 3. Concrete flow and temporal guards

### February retention

1. **Precondition:** Jacksonville's final 2014 game is actually closed, regular-season or postseason as the branch determines; reconcile 2014 contracts, player accrual, current roster, medical and the season review. February is not an automatic kickoff if the club is still playing. Some ordinary signings may occur before or after February.
2. Build the board of *existing* Jacksonville players whose contract genuinely expires at the start of the 2015 league year, plus eligible extension candidates explicitly distinguished from expiring players.
3. Retrieve all executed terms, remaining guarantees and rights, identify UFA/RFA/ERFA from earned 2014 accrual, then flag any uncertain eligibility as unresolved rather than filing a guess.
4. Generate Caldwell's review with a discrete football job at stake for every meaningful retention decision. Prior contracts that expire but require no Stone consultation may be handled within Caldwell's existing authority. Preserve all players' actual expiry status even if no new offer results.
5. Stone submits football priority and any explicit conditions. An optional recommended dollar figure remains advice, not a contract. Caldwell makes the actual lawful contact/negotiation/offer/rights decision, independent of Stone's wording.
6. Each concluded individual event is recorded immediately in its **own** Markdown outcome and permanent contract/rights owner; update cap, roster, expiry flags and affected views. Keep unfinished offers pending through their actual deadlines.
7. The phase index lists all individual result links and the unresolved position/financial consequences feeding March scouting, without copying every negotiation.

### March acquisition

1. Build the pro scout board from the resulting *branch* roster and prior season self-scout, not from what the real Jaguars signed in 2015. Scouting dossiers must be available to the club by the briefing's date and may only cite earlier actual performance or branch-specific completed results.
2. Before the March 7 window, no prospective outside UFA negotiations absent another valid authorization. From March 7 until 3:59:59 p.m. ET on March 10, communications with certified agents may discuss permitted parameters, not make official offers, binding or oral deals, promises, or announce signings. From March 10 at 4 p.m. ET, validate status again before executing an eligible new-club contract.
3. Check contractual control: tendered RFAs have first-refusal/possibly pick-compensation procedures; ERFAs tendered at minimum lack open-market negotiating rights; franchise/transition designation creates rights. Do not treat them all as freely available UFAs.
4. Stone submits football priorities, specific positional assignments and conditional alternatives. Caldwell may decline those priorities for contractual/cap reasons, which are recorded if communicated; do not invent a disagreement.
5. Independent party decisions and the market method fixed **before** negotiations decide acceptance/counter/departure. The established 2014 outside-club historical-player rails apply only at their allowed publication/effective dates as authorized; no real 2015 Jacksonville outcome, player future performance or future agent offer becomes an answer key. Future-year methods need their own adopted release and cannot mechanically rerun the old March 2014 results.
6. Every concluded offer/signing/decline produces its own dated result in the canonical acquisition record, followed by cap/roster/depth-review changes where warranted. The phase report is an index, not a mega-narrative.
7. Free agency need not close artificially on March 31. The March phase can summarize activity through a dated cutoff while later negotiations continue into April, May or in-season, with each event staying under its correct date and owner.

## 4. Precise 2015 rule table

| Rule | 2015 action |
|---|---|
| Franchise/transition designations | Window opens February 16; deadline **March 2, 4 p.m. ET**. One franchise **or** one transition designation at most. Filing is its own legal result; a tag is not a completed multiyear extension. |
| League cap | **$143,280,000 announced March 2, 2015**. Before public announcement a club briefing uses only a dated verified projection or unresolved amount. Never import the real Jaguars' adjusted cap/carryover, as that is affected by the divergent career. |
| Other-club prospective UFA agent negotiations | **March 7 to March 10**, before 4 p.m. ET. Observe 2015 specific agent-contact and no-formal-offer rules; no signature until league-year opening. Do not use later versions of this window. |
| 2014 contracts expire, 2015 league year opens | **March 10, 4 p.m. ET**. Own UFA retention decisions may be pursued lawfully beforehand; outside UFA signings cannot be antedated. |
| RFA and ERFA tenders, contract option, cap compliance | Action before **March 10, 4 p.m. ET**, on genuinely eligible individuals at correct sourced figures. Tender submitted is not the same as player signing. |
| RFA offer sheets and matches | RFA signing deadline **April 24**; prior club first-refusal deadline **April 29**, subject to the actual qualifying tender and compensation. |
| Rookie-contract renegotiations | Drafted rookie: not until after final regular-season game of third **contract** year. Undrafted rookie: after second contract year. Actual existing signed terms and eligibility control. |
| 2015 offseason roster | Verify actual era roster size (typically 90) and who already occupies a place. No phantom vacancy from an injury or from a player currently under contract. |
| Top 51 and adjusted cap | Use 2015 offseason Top-51 accounting as applicable, with *all* relevant bonus, guarantee, incentives and other charges; financing a signing is not just `new cap - annual average`. Separate cash available from salary-cap headroom and salary-guarantee obligations. |
| Medical | Diagnosis, clearance and fitness determinations belong to medical staff; a roster acquisition may be conditional on an actual physical. |

**Sources for chronology and law:** contemporaneous `jaguars.com` 2015 Important Dates; `buffalobills.com` February 12, 2015 NFL calendar; March 2015 NFL Communications free-agency FAQ published by `seahawks.com`; NFL March 9, 2015 memo as published by `nfl.com`; NFLPA March 2, 2015 cap announcement; original 2011 CBA Article 7 for rookie renegotiation. Do not import later NFL rules that differ.

## 5. Source ownership and file routing

- `runtime/decisions.py` already registers `re_signing` and `free_agency`; neither is marked implemented. Reuse their three named pages, changing only the smallest needed routing and exact filenames where the directory map resolves. Do **not** duplicate their page builders in the open-game or bye-week system.
- The direct page destination is `SeasonPaths(new_league_year).record('offseason/free_agency')`, which maps to `career/<year>/Team_Operations/Free_Agency/`. `Early_Offseason` is where the GM may have preceding scouting meetings, not a second canonical copy of the result.
- `career/finances/upcoming_decisions/player_decisions.md` indexes the expiration windows. Individual executed player contracts and retained guarantees are rendered from permanent financial sources; use current `data/finances/financial_inputs.json`, `career/finances/player_contracts/contract_details.md` and the season-specific player contract/cap status owners as applicable. The actual 2015 owner is established through the season handoff, not by copying the 2014 page as-is.
- A separate retention outcome should live under the existing Free_Agency/contract event owner's structured records and surface with a dated individual Markdown page. A March acquisition result likewise receives one dated authoritative Markdown page under the appropriate contract/acquisition owner; the two phase result pages merely index the files.
- `state/current_job.json` and `state/decision_queue.json` govern what Stone can see/answer, while Caldwell's independent transactions require their own commitments and dated authority. An event needing a response blocks **that transaction or filing only**, not all NFL games or unrelated scouting. Correctly resolved decisions cannot be accepted by silence.
- The same event ID and source date tie brief insert, My page response, final actor/agent decision, individual result and dependent player/cap changes. Validate idempotency; rebuilding a page never reruns a market draw or changes a contract.
- Keep season-close/2015 opening handoff and pending exit interviews as existing owners. Do not make a February re-signing declaration trigger the next season activation before acceptance gates. Preserve all earlier 2013/2014 closed records.

## 6. Evidence and prose controls

- Every player-specific claim is an actual completed game/practice observation, signed contract term, identified contemporaneous scouting finding or explicitly labelled inference. Do not force balanced 'pros and cons'; an observation can be narrow. No player grades, potential ratings or hidden scouting numbers are invented.
- Do not use actual future 2015 player statistics, later career outcomes, actual 2015 Jaguars signings or real-world Jaguars adjusted cap to determine branch choices. Public NFL calendar, salaries, tag rules and league-wide cap become available when they historically became known.
- Do not generate agent conversations as narrative just because a negotiation status changed. A dated proposal, counter and response are sufficient; only quote words recorded in an actual authorized exchange.
- Never assume that a player signs because Stone names him, that the market price always rises when waiting, or that a large dollar contract guarantees improved football. Scouting projections can be wrong; assistant player growth does not reroll based on a good story.
- Descriptive output should read like a GM/pro scout explaining the football work, not a software audit. Keep internal event IDs, file digests, numerical randomness, and generated identifiers outside coach-facing prose. The validators and data keep them.
- Summaries must not count projected cap savings or signing-bonus commitments twice; all signed terms are held in their actual owner and derived displays rebuilt from them.
- Quiet months are allowed. If only two relevant contracts are due, show two; a significant free-agent phase may produce zero signings or many distinct events.

## 7. Regression tests to implement (not presently run)

1. Pre-2014-season-close report does not invent 2014 final record or January 2015 contract decision.
2. A coach not employed by Jacksonville sees no private Caldwell brief.
3. A February issued report does not show the March 2 official 2015 cap as already announced.
4. After March 2, the report shows $143,280,000 as the **league** cap, never the real Jaguars' adjusted cap.
5. February status is sourced from the career roster and signed terms after the last real game, not real 2015 Jaguars transactions.
6. 2014 expiring Roy Miller and Daryl Smith receive individual class verification after season accrual; neither automatically signs.
7. Hakeem Nicks's 2014 one-year deal is considered without assuming his 2015 whereabouts.
8. Thielen's 2013-undrafted 2015 ending contract is **not** misclassified as a 2014 expiring UFA; eligible extension after the 2014 regular finale is a different inquiry.
9. A 2014 drafted rookie cannot be renegotiated in February 2015; a 2013 undrafted rookie may become eligible at its correct contract-year threshold.
10. Every RFA/ERFA class is computed from accrued seasons, not age or draft year alone.
11. Only one 2015 franchise OR transition designation is committed, before the March 2 deadline.
12. Unsigned franchise tender is not presented as a newly signed long-term contract.
13. Tag replacement by a signed extension updates cap/rights once, retaining both dated legal events.
14. Tender never becomes executed contract solely because Caldwell filed it; RFA compensation/right-to-match follows actual tender.
15. First-refusal exercise outside the 2015 April 29 deadline is refused.
16. A cap figure labelled 'certified room' without verified branch adjusted cap and accounting blocks transaction approval.
17. A user recommendation with no actual offer does not create a signed player or accept an agent's demand.
18. A player may reject the best football offer. Protagonist label, prose verbosity and expressed desired outcome do not alter disposition.
19. Outside prospective UFA negotiations before March 7 with no separate legal exception are refused.
20. March 7-10 parameters contact never generates an executable formal offer or agreement.
21. New-club player contract is not executed on March 10 before 4 p.m. ET.
22. A restricted or exclusive-rights player is not treated as open UFA under an active lawful tender.
23. A player already signed with a club cannot be signed as an unrestricted free agent absent an actual release or valid rights change.
24. Signing affects only supported roster/cap/control, not player improvement or automatic starting role.
25. Medical hold is neither a free roster slot nor a failed physical without a documented ruling.
26. Five concluded player negotiations on different dates, including two refusals, create five distinct dated Markdown result files; the monthly report only links them.
27. An offer completed March 11 is readable March 11 and not held until the end of March.
28. Multiple offers to one player are not accidentally treated as multiple completed acquisitions; preserve one canonical closed negotiation when applicable and distinct actual transactions when legally separate.
29. Each declined offer leaves no phantom cap charge, signing bonus, roster claim or automatic compensatory selection.
30. A new brief revision retains the content, source cutoff and issue date of every earlier issued edition.
31. Open player-contract items block only their dependent filing/signing, not unrelated NFL games or league events.
32. A change to future historical NFL team rails becomes usable only at its authorized date and never backfills an earlier scouting briefing.
33. A player re-signing with Jacksonville is counted only once when March free agency refreshes its board, not signed a second time as an outside FA.
34. A free agent signed via an authorized trade must be processed through the trade result, not labelled as a UFA acquisition.
35. Independent source records for cap, roster and contract all reconcile to a signed player's exact terms after rebuilding views.
36. No year-end or early-offseason action wipes 2013 and 2014 frozen historical results.

## 8. End-to-end acceptance scenario

In a safe staging copy, use a fabricated **test-only** club/player set rather than changing active 2014 history: two Jacksonville expirings of different free-agent classes, one legally eligible early extension, one proposed franchise designation, two March outside UFA inquiries (one accepted, one declined) and an RFA from another club under a valid tender. Exercise the exact dates, one-per-event outputs, responses, lawful statuses, cap/roster controls, and a revised brief. Verify that the input page alone can never consummate a contract and that rebuilding pages changes no closed event. The staging scenario is never imported to the career as a played result.
