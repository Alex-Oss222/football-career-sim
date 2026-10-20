# February Re-signings + March Free Agency: implementation contract

**Status:** Uploaded by the user on October 20, 2026 and adopted; built in step 7 of the [rebuild plan](rebuild_plan.md). Corrected the same day after the process check, against the user's rulings of October 20, 2026 and the defaults the lead settled and told the user, each written below as this design's rule. No question in this design awaits the user. It relies on one that does, how the club decides Stone's 2014 employment ([season end design](season_end.md#how-the-club-decides-awaiting-the-users-decision)), since these briefs go to Stone only if the Club Decision retains him; the other open question, when the nine 2014 assistant contracts end, belongs to the [January staff design](january_staff_review.md) (section B, item 5). The templates are in [foundation/templates/re_signing/](../foundation/templates/re_signing/) (February) and [foundation/templates/free_agency/](../foundation/templates/free_agency/) (March) and the worked example is [docs/examples/re_signing_and_free_agency_2014_into_2015.md](examples/re_signing_and_free_agency_2014_into_2015.md).

As uploaded: **Status:** Proposed workflow and tests, not installed or executed. The active simulated career is at October 5, 2014 after Week 5; no 2014 final season record or 2015 player transaction is supplied by this proposal.

## February Re-signings and March Free Agency | NFL head-coach career workflow

**Status:** Research-backed proposed Markdown templates and implementation specification. These files do not modify the GitHub repository, resolve any 2014 or 2015 career event, issue an official in-world briefing or make a player sign. Designed for the move from the simulated 2014 Jacksonville season to the **2015 NFL league year**, and repeatable for other seasons with their own historical rules.

### What to use

| Phase | The staff brief | Stone's page | Phase result | Individual result |
|---|---|---|---|---|
| February retention | [`re_signing/re_signing_report_template.md`](../foundation/templates/re_signing/re_signing_report_template.md) | [`re_signing/my_re_signing_priorities_template.md`](../foundation/templates/re_signing/my_re_signing_priorities_template.md) | [`re_signing/front_office_moves_template.md`](../foundation/templates/re_signing/front_office_moves_template.md) | [`re_signing/retention_result_template.md`](../foundation/templates/re_signing/retention_result_template.md) |
| March outside free agency | [`free_agency/pro_personnel_report_template.md`](../foundation/templates/free_agency/pro_personnel_report_template.md) | [`free_agency/my_free_agent_priorities_template.md`](../foundation/templates/free_agency/my_free_agent_priorities_template.md) | [`free_agency/free_agency_results_template.md`](../foundation/templates/free_agency/free_agency_results_template.md) | [`free_agency/free_agent_result_template.md`](../foundation/templates/free_agency/free_agent_result_template.md) |

Each phase also has its own My Responses page for answers to event inserts, from the shared [My Responses template](../foundation/templates/event_inserts/my_responses_template.md). Both keep the registry's file name, `My_Responses.md`, so each lives in its own phase folder (section 1): `February/My_Responses.md` and `March/My_Responses.md` under `Team_Operations/Free_Agency`. The two individual result templates are the retention and free-agent forms of the shared [event result](../foundation/templates/event_inserts/event_result_template.md).

**Additional:** This document contains schema/routing, calendar/authority and 43 proposed validation tests. [`examples/re_signing_and_free_agency_2014_into_2015.md`](examples/re_signing_and_free_agency_2014_into_2015.md) demonstrates the 2014 checkpoint and real prior branch negotiations without making up any 2015 result.

### Central operating rules

1. One current phase briefing at a time. A new immutable edition is issued only under the one reissue rule that governs every brief ([event inserts](event_inserts.md), section A, item 6): (a) a new event needs an answer from Stone, (b) a dated finding materially changes a choice still pending, or (c) an answer falls due before the next scheduled issue. Each brief has one scheduled issue (section 3: the Re-signing Report by February 16, the Pro Personnel Report on March 3) and no later one, so an informational event that affects no pending answer appears under FOR YOUR INFORMATION only in an edition of that brief issued for another reason; it does not wait for the next phase's brief. A new phase brief's first issue may still list completed earlier results under FOR YOUR INFORMATION as of its issue date, and the Pro Personnel Report carries the open re-signing items as inserts (section 3). An event's own result page is readable as soon as it is written, and the phase result links it at once. Never change what the coach already received.
2. Stone answers each phase brief once, on its fixed My page (My Re-signing Priorities, My Free-Agent Priorities), which is never rewritten after he answers. His answers to event inserts added later go on that phase's separate My Responses page. His recommendations are not Caldwell's contract decisions and never automatically execute a deal: on player contracts, tags and tenders Stone recommends and Caldwell decides (section 2).
3. One distinct **concluded event**, one separate dated output, including real declined offers, withdrawn offers, tender filings, signed extensions and executed free-agent contracts. Each output is a form of the shared event result and carries its event-record line. The phase report is the index to those files, not their replacement. A pending conversation is not a completed negotiation. A contract that lapses at 4 p.m. ET March 10 with no offer, talks, tag or tender gets no result page, because nobody made a decision: its status is kept in the contract record and listed in Front Office Moves.
4. When the 2015 career year starts, the 2014 player roster, medical status, draft assets, payroll and expired contracts must carry forward from real completed branch outcomes, not from the real Jaguars' offseason. Do not treat early-October 2014 player contracts as a final February board.
5. The March 2 official NFL salary cap can be stated only once that date has arrived in the simulated calendar. The **real** Jaguars' 2015 cap space/adjusted cap was the product of the real Jaguars' finances; never import it here. No 2015 money figure (the cap, franchise and transition values, tender amounts, minimum salaries, the matching rules, the carryover rule or the accrual rules that set a player's class) is used in a brief until a two-pass 2015 financial-rules library entry gives its source and public date. No figure without a source.
6. Keep current regular season and postseason results, game plans, league-player outcomes and all closed historical reports unchanged. Template work is not permission to advance the clock.
7. Other clubs' moves and league events continue while Stone's answers are open. Only an answer due before the event it holds stops the clock (section 2).

### Verified rule and research sources

- [Jacksonville Jaguars: 2015 NFL Important Dates](https://www.jaguars.com/news/2015-nfl-important-dates-14709246), pre-2015-season notice. February 16 through March 2 tags, March 7 to 10 negotiation window, March 10 league-year start, tenders and Top-51 deadlines.
- [Buffalo Bills: Important Dates on the 2015 NFL Calendar](https://www.buffalobills.com/news/important-dates-on-the-2015-nfl-calendar-14905495), February 12, 2015. Additional April 24/29 RFA deadlines and personnel windows.
- [NFL Communications: 2015 Free Agency FAQ](https://www.seahawks.com/news/2015-nfl-free-agency-faq-120736), published March 10, 2015. Legal categories, accrued seasons, franchise/transition and offer sheets, cap.
- [NFL: March 7, 2015 negotiating period](https://www.nfl.com/_amp/nfl-s-three-day-negotiating-period-underway-0ap3000000477176). Distinguishes permitted agent discussions from enforceable offers or new-club contracts.
- [Pro Football Talk: League reminds teams of rules for three-day negotiating period](https://www.nbcsports.com/nfl/profootballtalk/rumor-mill/news/league-reminds-teams-of-rules-for-three-day-negotiating-period), March 7, 2015: the window opened "at 12:00 p.m. ET on Saturday", March 7. The Raiders' [important 2015 offseason dates](https://www.raiders.com/news/important-raiders-2015-offseason-dates-14725466) give the same noon New York start; that page was read through a search extract on October 20, 2026, because it could not be retrieved directly.
- [NFL: March 9, 2015 memo on early agreements](https://www.nfl.com/news/nfl-sends-teams-memo-about-early-agreements-0ap3000000477438). Specifically prohibits official offers and agreements during the period.
- [NFLPA: 2015 NFL Salary Cap and Adjusted Team Positions](https://nflpa.com/press/2015-nfl-salary-cap-and-adjusted-team-positions), dated March 2, 2015. League-wide cap $143.28m. Real-team financial figures *not usable* for counterfactual Jacksonville.
- [2011 Collective Bargaining Agreement (original)](https://nflps.org/wp-content/uploads/2012/05/collective-bargaining-agreement-2011-2020.pdf), Article 7 on rookie contracts and when renegotiation is permitted; Article 9, Section 3(a) and (b), on the restricted free agent's offer sheet and the prior club's five-day right of first refusal, "not later than one day before the Draft". Primary era source, read in the August 4, 2011 text.
- The repository's [2015 calendar](../career/2015/Calendar.md) and its [source register](../library/2015_historical_calendar.md) for the May through July deadlines in section 4.
- Existing project: `foundation/03_Head_Coach_Organization_and_Authority_Canon.md`, `state/current_job.json`, `runtime/decisions.py`, `docs/season_cycle_milestones.md`, `docs/rebuild_plan.md`, the [league rails method](../career/2014/League/personnel/method.md), and era-specific contract/market records in `career/2014` and `career/finances`.

### Explicit gaps before implementation

- 2014 Weeks 6 through 17, any Jacksonville playoffs and the completed 2014 season review: **not yet played**. No final retention board can be populated today.
- The project's 2015 confirmed adjusted cap, carryover election, 2015 financial owner and cash budget must be derived and reconciled from the branch before contract execution. Historic league-wide cap is known only when its date arrives. The carryover **notice deadline is unverified**. The readings disagree: the original 2011 CBA text, Article 13, Section 6(b)(v), "Carrying Over Room" (notice "no later than fourteen (14) days prior to the start of the next League Year"; the [August 4, 2011 CBA](https://nflps.org/wp-content/uploads/2012/05/collective-bargaining-agreement-2011-2020.pdf), the copy the 2014 rules cite); the Over the Cap transcription of Article 13 (the day following the club's final regular-season game), a 2014-era description (the day before it) and "the Tuesday after the regular season", the three readings in [2014 rules](../library/2014_league_calendar_and_financial_rules.md) F4, to which V8 points; and the 2015 league FAQ (the day before that game; [2015 calendar sources](../library/2015_historical_calendar.md), source P). The deadline may fall before the season ends. Until it is verified in two passes, no carryover deadline or amount appears in a brief.
- The next-season market procedure, player statuses and independent acceptance mechanism need a 2015-specific precommitted implementation. A narrative template cannot repair or replace the market model.
- `runtime/decisions.py` registers both workflows but does not mark either implemented. The template page filenames and source-of-truth location must be wired to validators and the actual folder map, not manually copied into the active career.

**What the build must add** (the process check of October 20, 2026; each item belongs to the build step named):

| Need | Step |
|---|---|
| A 2014 accrued-season and credited-season record for every Jacksonville player, from the weekly full-pay status; the contract inputs hold accrual only through 2013 | 6 |
| The upcoming-decisions view separating practice-squad contracts that end with the season from league-year expiries, and a reserve/future path from December 29, 2014 for those players | 6 |
| A player-extension path from December 29, 2014 (Adam Thielen; Kirk Cousins under row 3a), with a result page per event and a quarterback consultation item that can hold a contract execution | 6 |
| The carryover notice deadline, verified in two passes before December 27, 2014 and entered in the 2014 calendar as Caldwell's filing | 6 |
| Dated rights entries in the player contract records (designation, unsigned tender charge, offer sheet and matching period, UFA tender, withdrawal or renunciation), one file-name rule for per-event results, and the result machinery | 5 |
| A folder for each phase's pages under `Team_Operations/Free_Agency` (`February/` and `March/`), through the folder map, so the two `My_Responses.md` pages have different paths (section 1) | 7 |
| A two-pass 2015 financial-rules library entry (rule 5 above): the cap, gated March 2; franchise and transition values; RFA tender amounts with their publication date; minimum salaries; the Article 8 and 9 definitions; the five-day matching period; the one-designation rule; the May 12 UFA tender correction | 7 |
| A 2015 league-year method committed before the first 2015 draw (section 3), and 2015 rails data built as the clock reaches each date | 7 |
| Decision-queue event kinds for a designation filing, a tender filing, a contract execution, an offer-sheet match and a market draw; the recommendation and quarterback consultation classes able to hold exactly the filing they precede; a league-year command for any season that refuses while an item holds its event | 7 |
| An issue history for phase briefs (editions, issue dates, digests, earlier copies) and the scheduled issue dates in section 3 | 7 |
| The page builders and checks for the six pages and their results, and the tests in section 7, run on a copy | 7 |

Outside this design, the AGENTS.md offseason-cycle task, the February and league-year rows of the season milestones, the update workflow's owner of a signing or tender and the job record's row 5 must name these pages and rules; those changes belong to the build.

## 1. Fixed page architecture

The established registry names six primary pages. Each file name is the registry's page name through `runtime.decisions.file_name`, and every cross-link is written through it:

| Phase | Staff brief | Stone's fill-in page | Phase result |
|---|---|---|---|
| February retention | `Re-signing_Report.md` | `My_Re-signing_Priorities.md` | `Front_Office_Moves.md` |
| March free agency | `Pro_Personnel_Report.md` | `My_Free-Agent_Priorities.md` | `Free_Agency_Results.md` |

All six belong in the **appropriate upcoming league year's** `Team_Operations/Free_Agency` logical folder, not duplicated in the just-finished season, each phase in its own folder there:

```
career/2015/Team_Operations/Free_Agency/
  February/   Re-signing_Report.md, My_Re-signing_Priorities.md, Front_Office_Moves.md, My_Responses.md
  March/      Pro_Personnel_Report.md, My_Free-Agent_Priorities.md, Free_Agency_Results.md, My_Responses.md
  (each resolved event's own result page)
```

Both phases' answer pages keep the registry's file name, `My_Responses.md` (the shared answer-page name in `runtime/decisions.py`), so they need separate folders: today the registry's places for `re_signing` and `free_agency` both resolve to `Team_Operations/Free_Agency`, and the build gives each phase its own folder through the folder map. A season's date/year and the league year being entered remain explicit. Use `SeasonPaths.record('offseason/free_agency')` or equivalent folder map; do not guess a filepath based on 2014's old layout. Each resolved event's own result page lives in `Team_Operations/Free_Agency` itself, the contract event owner, and both phase results link it.

- Who brings each brief follows the registry: the Re-signing Report is the general manager's, David Caldwell's; the Pro Personnel Report is brought by Caldwell for the pro personnel department. As in the January staff and staff vacancy designs, an author is named only from the job record's parties, nobody assesses his own work, and Stone's view goes on his page.
- The staff/GM brief is built from dated, visible, current source records, not from Stone's answer or future outcomes.
- Stone's document has fixed readable headings and is never silently rewritten after he answers.
- The phase result is a concise **index and synthesis** of actual completed actions. It is not the sole record of multiple deals.
- **Every distinct resolved player negotiation, tag, tender, offer or signing event has one separate dated Markdown output at its true contract/personnel event owner**, in the form of the shared event result with its event-record line. A completed rejection or withdrawal has its own result. If one player generates separate legal actions at different dates (e.g. a franchise designation later replaced by a negotiated contract), they are distinct linked events, not overwritten. An open negotiation is process history, not falsely 'closed, no deal'. A contract that lapses with no offer, talks, tag or tender has no result page (central rule 3).
- A brief may contain any number of `ACTION REQUIRED`, `FOR YOUR INFORMATION`, and `COMING UP` inserts under the [event insert design](event_inserts.md) and its [insert template](../foundation/templates/event_inserts/brief_action_inserts_template.md), in one slot directly under the brief's header block, as in the Game Week Briefing and the Bye Week Review; an event's result always lives in its own output, not the brief or weekly/phase overview.
- A new edition of a brief follows the one reissue rule (central rule 1) and preserves what Stone previously received, with issue date and content digest in the active issue-history owner.

## 2. Authority and decision ownership

Refer to `state/current_job.json`, Document 3 rows 3, 3a, 4, 5, 6, 7 and 20. At the October 5, 2014 checkpoint:

- Caldwell owns player acquisition selection, trade execution, negotiation, contract execution, tenders and cap. On player contracts, tags and tenders (Document 3 row 5) Stone recommends and Caldwell decides, as the lead settled on October 20, 2026; the job record's row 5 still reads unset, and its change comes in the build. Stone recommends on football use, development, retention and replacement; he does not have a player-contract veto or a unilateral signature.
- A major intended-franchise-quarterback commitment requires Stone's **written football projection and consultation with Caldwell**, not Stone's approval (row 3a: a meeting to resolve disagreement before Caldwell acts). The user controls that actual projection when due. That consultation holds the contract execution it precedes.
- Stone owns game plans, team football roles and authorized personnel deployment, within legal roster/medical limits. A player signing does not name a starter or automatically change the offensive/defensive playbook.
- Owners, agents, players, rival clubs, medical staff and league offices make their own decisions. Their answers must not be generated to reward Stone's enthusiasm, his naming of a player, or the length of his prose. If Stone no longer holds this job after the season-end Club Decision, do not issue Jacksonville personnel briefs to him; Caldwell then acts on his own record, with offer terms from the frozen method below, and no My page is issued.

A Caldwell decision and Stone's recommendation are **not** one event. A Caldwell request holds a filing only when Caldwell asks for Stone's recommendation with a due time before that filing (for example a designation before 4 p.m. ET March 2 or a tender before 4 p.m. ET March 10). The item then holds that filing alone: if the answer is not in by its due time the clock stops there, nothing lapses silently, and league events and other clubs' moves continue. With no such request, Caldwell files on his own record. This applies the user's October 20, 2026 rule that only an answer due before the event it holds stops the clock. No arbitrary weekly or daily approval prompts.

**Caldwell's offer terms when Stone sets no figure.** They come from a method frozen before each window opens: dated comparable contracts signed before the brief's information cutoff, with the calculation shown and the result labelled as a reconstruction. A figure Stone does give is a recommendation Caldwell weighs. Neither is an offer until Caldwell makes it, and no figure is used without a source (central rule 5).

## 3. Concrete flow and temporal guards

### February retention

1. **Precondition:** Jacksonville's final 2014 game is actually closed, regular-season or postseason as the branch determines; reconcile 2014 contracts, player accrual, current roster, medical and the season review. February is not an automatic kickoff if the club is still playing. Some ordinary signings may occur before or after February. **Scheduled issue:** the Re-signing Report issues after the season review, by February 16, 2015, the day the designation window opens.
2. Build the board of *existing* Jacksonville players whose contract genuinely expires at the start of the 2015 league year, plus eligible extension candidates explicitly distinguished from expiring players. Read each contract's type: a practice-squad contract that ends with Jacksonville's season is a reserve/future decision from December 29, 2014, not a league-year re-signing, and it is not on this board. An extension that comes up after the final 2014 regular-season game and before the report issues arrives as an insert in the brief then active, with its own result page; the board lists it only while it is still open.
3. Retrieve all executed terms, remaining guarantees and rights, identify UFA/RFA/ERFA from earned 2014 accrual, then flag any uncertain eligibility as unresolved rather than filing a guess.
4. Generate Caldwell's review with a discrete football job at stake for every meaningful retention decision. Prior contracts that expire but require no Stone consultation may be handled within Caldwell's existing authority. Preserve all players' actual expiry status even if no new offer results.
5. Stone submits football priority and any explicit conditions. An optional recommended dollar figure remains advice, not a contract; with none, Caldwell's terms come from the frozen method in section 2. Caldwell makes the actual lawful contact/negotiation/offer/rights decision, independent of Stone's wording.
6. Each concluded individual event is recorded immediately in its **own** Markdown outcome and permanent contract/rights owner; update cap, roster, expiry flags and affected views. Keep unfinished offers pending through their actual deadlines.
7. The phase index lists all individual result links and the unresolved position/financial consequences feeding March scouting, without copying every negotiation. Front Office Moves continues to index own-player events after March 10.

### March acquisition

1. Build the pro scout board from the resulting *branch* roster and prior season self-scout, not from what the real Jaguars signed in 2015. Scouting dossiers must be available to the club by the briefing's date and may only cite earlier actual performance or branch-specific completed results. **Scheduled issue:** the Pro Personnel Report issues March 3, 2015, after the designation deadline, carrying the open re-signing items as inserts. Stone's answer on My Free-Agent Priorities is due before noon ET March 7, so his priorities are in before outside talks can begin.
2. Before noon ET March 7, no prospective outside UFA negotiations absent another valid authorization. From noon ET March 7 until before 4 p.m. ET on March 10, communications with certified agents may discuss permitted parameters, not make official offers, binding or oral deals, promises, or announce signings. From March 10 at 4 p.m. ET, validate status again before executing an eligible new-club contract.
3. Check contractual control: tendered RFAs have first-refusal/possibly pick-compensation procedures; ERFAs tendered at minimum lack open-market negotiating rights; franchise/transition designation creates rights. Do not treat them all as freely available UFAs.
4. Stone submits football priorities, specific positional assignments and conditional alternatives. Caldwell may decline those priorities for contractual/cap reasons, which are recorded if communicated; do not invent a disagreement.
5. Independent party decisions decide acceptance, counter and departure, by the market method fixed **before** negotiations. For 2015 that method is the rails private market draw ([league rails method](../career/2014/League/personnel/method.md), section 4), with the 2014 own-player rule (an own free agent whose real move was a re-signing with the real Jaguars is drawn against that real contract) and the 2014 uncontested rule (a target with no rival real contract when Jacksonville's offer can first be signed decides at the 0.90 ceiling) restated with 2015 dates in a 2015 league-year method committed before the first 2015 draw. That method also carries the 2015 window: agent talks from noon ET March 7 to before 4 p.m. ET March 10, signing from 4 p.m. ET March 10. The 2014 method's 2014 timing stays as written, as history. A real contract enters only as the draw comparator, read at that player's draw date under rails method sections 2 and 4, never in a brief or a board. Beyond that comparator, no real 2015 Jacksonville transaction, player future performance or future agent offer becomes an answer key. The March 2014 outcomes came from a one-off judgment replay and cannot be mechanically rerun.
6. Every concluded offer/signing/decline produces its own dated result in the canonical acquisition record, followed by cap/roster/depth-review changes where warranted. The phase report is an index, not a mega-narrative.
7. Free agency need not close artificially on March 31. The March phase can summarize activity through a dated cutoff while later negotiations continue into April, May or in-season, with each event staying under its correct date and owner.

## 4. Precise 2015 rule table

| Rule | 2015 action |
|---|---|
| Franchise/transition designations | Window opens February 16; deadline **March 2, 4 p.m. ET**. One franchise **or** one transition designation at most. Filing is its own legal result; a tag is not a completed multiyear extension. |
| League cap | **$143,280,000 announced March 2, 2015**, used from the two-pass 2015 rules entry. Before public announcement a club briefing uses only a dated verified projection or unresolved amount. Never import the real Jaguars' adjusted cap/carryover, as that is affected by the divergent career. |
| 2014 carryover into 2015 | **Notice deadline unverified** (section "Explicit gaps"). No carryover deadline or amount is shown until it is verified. |
| Other-club prospective UFA agent negotiations | **From noon ET March 7 to before 4 p.m. ET March 10.** Observe 2015 specific agent-contact and no-formal-offer rules; no signature until league-year opening. Do not use later versions of this window. |
| 2014 contracts expire, 2015 league year opens | **March 10, 4 p.m. ET**. Own UFA retention decisions may be pursued lawfully beforehand; outside UFA signings cannot be antedated. |
| RFA and ERFA tenders, contract option, cap compliance | Action before **March 10, 4 p.m. ET**, on genuinely eligible individuals at correct sourced figures. Tender submitted is not the same as player signing. |
| RFA offer sheets and matches | RFA signing deadline **April 24**. The prior club's right of first refusal runs **five days from the day it receives the offer sheet**, and never later than one day before the draft, **April 29** (2011 CBA Article 9, Section 3(a) and (b)), subject to the actual qualifying tender and compensation. |
| UFA tender | **May 12** for the prior club's tender to its unsigned UFA. The January 1, 2015 league bulletin said June 1; the move to May 12 was publicly reported March 31, 2015. A brief issued before March 31 shows June 1, the date then published, and the correction reaches Stone as a dated FOR YOUR INFORMATION. |
| RFA June dates | **June 1** RFA tender and bonus-accounting boundary; **June 15** RFA replacement-tender deadline, as the 2015 calendar records them. A replacement-tender mechanism is used only once the 2015 rules entry verifies it. |
| Franchise player multiyear agreement | **July 15, 4 p.m. ET** deadline. |
| Tendered UFA and transition offer sheets | **July 22**, or the first league camp if later: a tendered UFA's signing window closes, and the transition-player offer-sheet cutoff falls. |
| Rookie-contract renegotiations | Drafted rookie: not until after final regular-season game of third **contract** year. Undrafted rookie: after second contract year. Actual existing signed terms and eligibility control. |
| 2015 offseason roster | Verify actual era roster size (typically 90) and who already occupies a place. No phantom vacancy from an injury or from a player currently under contract. |
| Top 51 and adjusted cap | Use 2015 offseason Top-51 accounting as applicable, with *all* relevant bonus, guarantee, incentives and other charges; financing a signing is not just `new cap - annual average`. Separate cash available from salary-cap headroom and salary-guarantee obligations. |
| Medical | Diagnosis, clearance and fitness determinations belong to medical staff; a roster acquisition may be conditional on an actual physical. |

**Sources for chronology and law:** contemporaneous `jaguars.com` 2015 Important Dates; `buffalobills.com` February 12, 2015 NFL calendar; March 2015 NFL Communications free-agency FAQ published by `seahawks.com`; Pro Football Talk, March 7, 2015, for the noon start; NFL March 9, 2015 memo as published by `nfl.com`; NFLPA March 2, 2015 cap announcement; original 2011 CBA Article 7 for rookie renegotiation and Article 9, Section 3, for the matching period; the repository's 2015 calendar and its source register for the May through July dates. Do not import later NFL rules that differ.

## 5. Source ownership and file routing

- `runtime/decisions.py` already registers `re_signing` and `free_agency`; neither is marked implemented. Reuse their three named pages, with file names from `runtime.decisions.file_name`, changing only the smallest needed routing where the directory map resolves. Do **not** duplicate their page builders in the open-game or bye-week system.
- The direct page destination is `SeasonPaths(new_league_year).record('offseason/free_agency')`, which maps to `career/<year>/Team_Operations/Free_Agency/`, with each phase's pages in its own folder below it (section 1). `Early_Offseason` is where the GM may have preceding scouting meetings, not a second canonical copy of the result.
- `career/finances/upcoming_decisions/player_decisions.md` indexes the expiration windows. Its 2014 group today mixes the league-year expiries with seven practice-squad contracts that end with the 2014 season; the Re-signing Report's builder reads each contract's type and leaves the practice-squad players to the reserve/future decision. Individual executed player contracts and retained guarantees are rendered from permanent financial sources; use current `data/finances/financial_inputs.json`, `career/finances/player_contracts/contract_details.md` and the season-specific player contract/cap status owners as applicable. The actual 2015 owner is established through the season handoff, not by copying the 2014 page as-is.
- A separate retention outcome should live under the existing Free_Agency/contract event owner's structured records and surface with a dated individual Markdown page in the form of the shared event result. A March acquisition result likewise receives one dated authoritative Markdown page under the appropriate contract/acquisition owner; the two phase result pages merely index the files.
- `state/current_job.json` and `state/decision_queue.json` govern what Stone can see/answer, while Caldwell's independent transactions require their own commitments and dated authority. An event needing a response blocks **that transaction or filing only**, not all NFL games or unrelated scouting, and only on the terms of section 2. Correctly resolved decisions cannot be accepted by silence. The queue today cannot hold an offseason filing (its blocking kinds are game-week and season-stage events, and the recommendation and quarterback consultation classes may hold nothing); the build adds the kinds listed under "What the build must add".
- The same event ID and source date tie brief insert, My page or My Responses answer, final actor/agent decision, individual result and dependent player/cap changes. Validate idempotency; rebuilding a page never reruns a market draw or changes a contract.
- Keep season-close/2015 opening handoff and pending exit interviews as existing owners. Do not make a February re-signing declaration trigger the next season activation before acceptance gates. Preserve all earlier 2013/2014 closed records.

## 6. Evidence and prose controls

- Every player-specific claim is an actual completed game/practice observation, signed contract term, identified contemporaneous scouting finding or explicitly labelled inference. Do not force balanced 'pros and cons'; an observation can be narrow. No player grades, potential ratings or hidden scouting numbers are invented.
- Do not use actual future 2015 player statistics, later career outcomes, actual 2015 Jaguars signings or real-world Jaguars adjusted cap to determine branch choices. Public NFL calendar, salaries, tag rules and league-wide cap become available when they historically became known. A real contract is read only as a draw comparator at that player's draw (section 3).
- Do not generate agent conversations as narrative just because a negotiation status changed. A dated proposal, counter and response are sufficient; only quote words recorded in an actual authorized exchange.
- Never assume that a player signs because Stone names him, that the market price always rises when waiting, or that a large dollar contract guarantees improved football. Scouting projections can be wrong; assistant player growth does not reroll based on a good story.
- Descriptive output should read like a GM/pro scout explaining the football work, not a software audit. Keep internal event IDs, file digests, numerical randomness, and generated identifiers outside coach-facing prose. The validators and data keep them. The reader-facing pages use none of the words branch, simulation, receipt, kernel, engine, ledger, snapshot or checkpoint.
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
15. A first-refusal exercise more than five days after the prior club received the offer sheet, or later than April 29, 2015, is refused.
16. A cap figure labelled 'certified room' without verified branch adjusted cap and accounting blocks transaction approval.
17. A user recommendation with no actual offer does not create a signed player or accept an agent's demand.
18. A player may reject the best football offer. Protagonist label, prose verbosity and expressed desired outcome do not alter disposition.
19. Outside prospective UFA negotiations before noon ET March 7 with no separate legal exception are refused.
20. A parameters contact from noon ET March 7 to before 4 p.m. ET March 10 never generates an executable formal offer or agreement.
21. New-club player contract is not executed on March 10 before 4 p.m. ET.
22. A restricted or exclusive-rights player is not treated as open UFA under an active lawful tender.
23. A player already signed with a club cannot be signed as an unrestricted free agent absent an actual release or valid rights change.
24. Signing affects only supported roster/cap/control, not player improvement or automatic starting role.
25. Medical hold is neither a free roster slot nor a failed physical without a documented ruling.
26. Five concluded player negotiations on different dates, including two refusals, create five distinct dated Markdown result files; the monthly report only links them.
27. An offer completed March 11 is readable March 11 and not held until the end of March.
28. Multiple offers to one player are not accidentally treated as multiple completed acquisitions; preserve one canonical closed negotiation when applicable and distinct actual transactions when legally separate.
29. Each declined offer leaves no phantom cap charge, signing bonus, roster claim or automatic compensatory selection.
30. A new brief revision retains the content, source cutoff and issue date of every earlier issued edition, and an informational event alone issues no new edition.
31. Open player-contract items block only their dependent filing/signing, not unrelated NFL games or league events.
32. A change to future historical NFL team rails becomes usable only at its authorized date and never backfills an earlier scouting briefing.
33. A player re-signing with Jacksonville is counted only once when March free agency refreshes its board, not signed a second time as an outside FA.
34. A free agent signed via an authorized trade must be processed through the trade result, not labelled as a UFA acquisition.
35. Independent source records for cap, roster and contract all reconcile to a signed player's exact terms after rebuilding views.
36. No year-end or early-offseason action wipes 2013 and 2014 frozen historical results.
37. A contract that lapses at 4 p.m. ET March 10 with no offer, talks, tag or tender creates no result page; Front Office Moves lists it and the contract record holds its status.
38. A practice-squad contract that ended with Jacksonville's 2014 season does not appear on the Re-signing Report's board.
39. An answer to an insert is written on that phase's My Responses page (`February/My_Responses.md` or `March/My_Responses.md`), never on the other phase's; the phase's My page is unchanged after its first answer.
40. A Caldwell request without a due time before its filing holds nothing; one with such a due time holds only that filing, and league events and other clubs' moves continue.
41. With no figure from Stone, Caldwell's offer terms are the frozen method's labelled reconstruction from comparables dated before the brief's cutoff; no comparable signed after the cutoff is read.
42. No brief or board edition issued before a player's draw contains the terms of his real contract.
43. Every page file name and cross-link equals `runtime.decisions.file_name` of the registry's page name, and the two phases' `My_Responses.md` pages resolve to different paths.

## 8. End-to-end acceptance scenario

In a safe staging copy, use a fabricated **test-only** club/player set rather than changing active 2014 history: two Jacksonville expirings of different free-agent classes, one legally eligible early extension, one proposed franchise designation, two March outside UFA inquiries (one accepted, one declined) and an RFA from another club under a valid tender. Exercise the exact dates, one-per-event outputs, responses, lawful statuses, cap/roster controls, and a revised brief. Verify that the input page alone can never consummate a contract and that rebuilding pages changes no closed event. The staging scenario is never imported to the career as a played result.
