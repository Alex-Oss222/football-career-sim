# Season-end workflow: implementation, evidence and tests

**Status:** Uploaded by the user on October 20, 2026 and adopted; built in step 6 of the [rebuild plan](rebuild_plan.md). Corrected the same day after the process check, against the user's rulings of October 20, 2026 and the defaults the lead settled and told the user, each written below as this design's rule. One question awaits the user's decision: how the club decides ([section C](#how-the-club-decides-awaiting-the-users-decision)). The templates are in [foundation/templates/season_end/](../foundation/templates/season_end/) and the worked example is [docs/examples/season_end_2013_precedent_and_2014_setup.md](examples/season_end_2013_precedent_and_2014_setup.md). The user ruled on October 20, 2026 that Stone's season-end page is separate from the weekly My Responses page and has a different name: it is My Season Response (`My_Season_Response.md`, from the [My Season Response template](../foundation/templates/season_end/my_season_response_template.md)).

This design advances no career event. Apply it to the next actual final game of Stone's club and later years. Never rewrite closed 2013 history or pre-decide the unplayed 2014 season.

## Season ends: ownership review and club decision

Applies after Jacksonville's **actual final game of an NFL season**, whether that is Week 17 (Sunday, December 28, 2014 for the 2014 season) or a postseason game. No 2014 ending has been played or presumed by these documents. A dismissal can happen on any date ([event inserts](event_inserts.md), section D); where the Club Decision of a dismissal before the final game is filed, and how it is routed, is part of the step 6 build ([section G](#g-suggested-module-boundaries-not-required-filenames)).

### Reader-facing files

| Page (file) | Owner | What it does |
|---|---|---|
| Season Review Briefing (`Season_Review_Briefing.md`) | Khan and Caldwell, with evidence supplied by the football department | Gives Stone their communicated concerns and the questions they want answered. It does **not** announce a decision they have not made. |
| My Season Response (`My_Season_Response.md`) | Stone | Holds Stone's actual account of the football year and any request he deliberately makes. It is a one-time answer to the briefing. An ACTION REQUIRED notice in the briefing is answered on the season-end phase's own My Responses page (`My_Responses.md`), not here. |
| Club Decision (`Club_Decision.md`) | Khan and Caldwell | Records the club's completed employment decision and its actual consequences. It is the season end's form of the [shared event result](../foundation/templates/event_inserts/event_result_template.md) and keeps the decision's event-record line. |

The file names come from the page names through `runtime/decisions.file_name`. The existing `career/YEAR/Season_Review/season_review.md` **is a different document**, the football department's team season report. It remains in place and owns the detailed offensive, defensive, special-teams, player-development and coaching review. `Season_Review_Briefing.md` deliberately has a different filename to avoid a case-insensitive clash with that established owner. The registry still names the brief "Season Review" and Stone's page "My Response"; the build renames both together with their links ([Filenames](#filenames-avoid-a-real-collision)).

### Supporting files

- This document gives the decision gates, authority boundaries, chronology, independent ownership decision method, validation and regression tests.
- [`season_end_2013_precedent_and_2014_setup.md`](examples/season_end_2013_precedent_and_2014_setup.md) shows what can be stated from the closed 2013 review and 2014 evidence **without fabricating a 2014 outcome or owner conversation**.

### Governing distinctions

1. The **club** decides whether Stone stays, with which existing terms, and whether it wishes to make a new offer. Stone does not decide his own retention.
2. **A formal hearing is not required.** No league rule in the library requires one, and the era's recorded dismissals ([head-coach contracts](../library/nfl_head_coach_contracts_2005_2014.md), rows C53 and C78) describe none. That is pattern evidence, not a rule, and the [job record](../state/current_job.json) leaves row 1's consultation unset. Whether and when the club asks for Stone's input and holds a meeting is fixed in the employment method before the final game ([section C](#how-the-club-decides-awaiting-the-users-decision)). If the club decides without asking, record the real decision; do not generate fake prior discussion or an answered `My_Season_Response.md`.
3. Being **retained** does not mean getting a raise, extension, new authority or guaranteed employment for another year. Such changes need real offers, approval and signatures.
4. A separate extension negotiation, hiring request, staff appointment, assistant exit, trade or player contract is a **separate event** with its **own dated output**, even if introduced in this briefing and answered through the phase's `My_Responses.md`. An extension offer to Stone follows section C, item 8.
5. If employment ends, stop showing confidential Jacksonville briefings to Stone and route the next genuine career decisions to his agent/career view.
6. The existing 2013 closed decision must not be revised and the 2014 outcome must not be preselected.

No page builder reads these templates yet; step 6 builds them ([section G](#g-suggested-module-boundaries-not-required-filenames)). This design does not advance game time or alter any canonical record.

## A. Research-supported design decision

A head coach's employment status and the club's football evaluation are related but distinct. The era's recorded cases show what a club weighed when it decided and what the decision cost. They come from the [head-coach contracts library](../library/nfl_head_coach_contracts_2005_2014.md), whose named examples all predate this career's January 2013 divergence:

| Row | What the library records | Its label there | Use in this design |
|---|---|---|---|
| C53 | Clubs that dismissed a head coach without cause kept paying what was left of his contract, less any offset: dismissals with years left at San Diego, Baltimore, Seattle, Denver, Jacksonville and Philadelphia, 2007 to 2012 | Corrected; the dismissal dates Confirmed, the amounts Unverified | A dismissal without cause pays out the remainder less the offset; no hearing is described |
| C54, C55 | The offset: the former club's obligation fell by the coach's pay in his next job (Denver and Shanahan, 2010; Jacksonville and Del Rio, 2012) | C54 mechanism Confirmed, amount Unverified; C55 Unverified | How an offset term works |
| C56 | Oakland dismissed Lane Kiffin for cause on September 30, 2008; an arbitrator denied his grievance on November 15, 2010 | Confirmed; offset amounts Unverified | A for-cause dismissal needs grounds and can be contested |
| C78 | San Diego dismissed Marty Schottenheimer on February 12, 2007 after a 14-2 season, citing changes to his coaching staff and friction with the general manager, and said it would pay his final year | Confirmed; the buyout term Unverified | A winning record does not settle the decision; staff and general-manager alignment can weigh in it |
| C61 | Dismissing a coach with years left meant paying the remainder, less any offset, plus the assistants who were not kept | Derived from C53 to C59 and C78 | The cost the club weighs |

Each row is real history, an example only, never an answer key for any club's decision in this career. Who is dismissed, and when, is this career's own event: no real-world coaching change after the divergence is read, and no tracker of real dismissals is a source.

## B. Existing owners to preserve

| Existing record | Its role and required boundary |
|---|---|
| `career/YEAR/Season_Review/season_review.md` | **Team football synthesis**. Already prescribed by [`foundation/templates/season_review/season_review.md`](../foundation/templates/season_review/season_review.md). Do not replace or duplicate it with the new ownership briefing. |
| `career/YEAR/Season_Review/Exit_Interviews/` | Actual player/staff interviews, individually dated; no fabricated blanket meeting. |
| `career/YEAR/Season_Review/Player_Assessments/` | Individual final assessments. Do not issue an extra set of grades in the owner review. |
| `data/YEAR/Season_Review/season_handoff.json` | The season's closeout manifest: team gates, carry-forward sources and pending decisions ([2014 season review](../career/2014/Season_Review/README.md)). The next season's opening review is the separate `data/NEXT/opening_handoff.json`, written by `python scripts/season_handoff.py stage YEAR`. Do not create a competing handoff manifest. |
| [`career/2013/season_review/owner_and_gm_review.md`](../career/2013/season_review/owner_and_gm_review.md) | Closed January 15, 2014 **precedent**. Its retained/unchanged outcome is canon and must remain. |
| [`career/Stone/Performance_Reviews.md`](../career/Stone/Performance_Reviews.md) | Existing ownership perspective. It is not an employment decision. Its October 5, 2014 review does not count as concerns delivered to Stone: no record shows it delivered. |
| [`data/people/coaches/alex_stone.json`](../data/people/coaches/alex_stone.json) and [`state/current_job.json`](../state/current_job.json) | Employment contract and live authority owners; the job record's `evaluation` and `employer_requests` hold the standards and requests on record. Update only on the actual employment event; do not invent an extension. |
| [`state/decision_queue.json`](../state/decision_queue.json) | User decisions that are genuinely pending, owned and consequential; employer's decision is not owned by Stone. |
| [`docs/event_inserts.md`](event_inserts.md) and [`foundation/templates/event_inserts/`](../foundation/templates/event_inserts/) | Existing design for one active briefing / answer surface, the one reissue rule that governs every brief (section A, item 6) and **one standalone dated output per resolved independent event**, each a form of the shared event result. Reuse it for extension, staff, trade and job-search events. |

### Filenames: avoid a real collision

The `runtime/decisions.py` registry still declares `Season Review` -> `My Response` -> `Club Decision` under `career/YEAR/Season_Review/`. Through `runtime/decisions.file_name`, the brief would be `Season_Review.md`, which collides **case-insensitively** with the existing team `season_review.md`. Implement these page names:

- Season Review Briefing, `Season_Review_Briefing.md` (reader title: “Season Review: Ownership and General Manager”),
- My Season Response, `My_Season_Response.md`,
- Club Decision, `Club_Decision.md`,
- while retaining `season_review.md` unchanged as the team football report.

Change the registry, the rebuild plan's page table, the brief named in [event inserts](event_inserts.md) section A, item 3, link generation and the page-name test together, and record the rename in the rebuild plan's change log. Add a validation check that no two pages in one folder differ only by letter case. Do not silently rename legacy `season_review.md` or maintain two synthesized team reports.

## C. Trigger, calendar and sequence

1. **Actual team completion.** Start only after Jacksonville's final played game of that NFL season. If the club qualifies for the playoffs, Week 17 alone is insufficient; the real elimination or Super Bowl completion is the trigger. The 2014 regular season ends on December 28, 2014 ([2014 calendar](../career/2014/Calendar.md)); the 2014 postseason slots the trigger needs are an input the build adds. From 2014 on, the ownership review and the Club Decision belong to the closing NFL season's record: each event-record line carries `"season"` set to the season reviewed, so a decision made in January lists in that season's annual record. Do not import the actual 2014 Jaguars finish.
2. **Freeze the employer's decision basis before its resolution.** The club's recorded hire criteria and the contract's first-season standard, later properly communicated performance priorities, record, and legally relevant contract terms must be available with valid as-of timestamps. The employment method (below) is frozen before Jacksonville's final game and before any My Season Response is read, and it is tested by swapping the clubs' labels. Do not invent arbitrary “owner satisfaction” scores, secret fixed wins or guaranteed retention. An adjudication unable to distinguish possible outcomes must say its decision method is unresolved rather than make up an answer.
3. **Team review and individual records remain distinct.** Gather completed game books, final stats, the detailed team review when actually ready, medical/contract records, completed exit interviews and staff issues. No forced parallel completion: if ownership decides before all exit interviews or league awards finish, use the evidence available at that actual moment.
4. **Does ownership actually request Stone's input?** The employment method fixes, before the final game, whether and when the club asks; the answer is never chosen after the result. If yes, issue the briefing with the specific communicated concerns and genuine meeting date/deadline; the `My_Season_Response.md` user turn opens only for those requests. If the club has already decided and communicated termination, write the decision first; do not invent a meeting, and do not ask Stone to “approve” the firing. If the owner has conveyed retention before a later discussion, preserve that decision and treat subsequent requests as separate issues.
5. **Stone's response.** Accept the same fixed headings, or the same named sections in an uploaded `.md` / `.txt` or chat. Permit brief football prose, concrete proposals, “None”/“No change” where applicable. Reject contradictions to the real roster/playbook/contract/authority; do not accept ghost offers. Only an answer due before the event it holds stops that event: the other clubs' games close while Stone's answers are open, and unrelated offseason work continues. Silence never equals approval, acceptance or request.
6. **Independent decision.** Khan/Caldwell determine Stone's employment by the method fixed below. The decision accounts for the earlier frozen criteria, actual results, roster and staff circumstances, contract and material new information, under protagonist-blind logic. Stone may rebut an error or provide a *substantive* new plan; rhetorical polish, word count and actor name cannot change the conclusion. An owner's private mental state is not magically conveyed to the coach.
7. **Write result immediately.** When the club actually decides, issue `Club_Decision.md` then and there, with real date, actual basis, input where applicable, status, financial/authority consequences, access change and its event-record line. Record one canonical event in the coach job/contract owner, then rebuild dependent live state, desk, calendar and annual event index. A pending matter has no fabricated final output.
8. **Separate event outputs.** If Stone is **retained** and the club later makes him an extension offer, Khan and Caldwell decide whether to make it, under Document 3 row 1. It arrives as an ACTION REQUIRED insert in the active brief; Stone answers it on that phase's My Responses page; its one result page is New Contract or Unchanged (`New_Contract_or_Unchanged.md`) in `career/Stone/`. There is no separate Extension Offer brief. If fired, the employment decision is the `Club_Decision.md` in that season's `Season_Review/` (do not duplicate it as a second dismissal result), while the agent's job search, each interview, each separate offer and each new contract receive their own outputs in `career/Stone/`. The same holds for assistant contracts, trades, player extensions, permission decisions and January staff actions. If Stone is dismissed while staff items are open, Caldwell answers them for Jacksonville; an assistant's renewal stays open for the successor head coach.
9. **Season handoff.** Staging may use only actually closed team gates and valid carry-forward data. Staging the next season waits until the club's employment decision is recorded. Retaining the head coach does not authorize roster renewal, staff changes, new practice, medical clearance or a future year's first game. If dismissed, transfer current football authority appropriately and cease Stone's access to Jacksonville's restricted operations.

### How the club decides (awaiting the user's decision)

How Jacksonville's 2014 employment decision is resolved is **awaiting the user's decision**. Neither option below is adopted; the first is the proposal.

| | Proposal (not adopted) | Alternative |
|---|---|---|
| Method | One base-rate draw for all 32 clubs, keyed on wins, tenure and recent playoffs, as the [January 2014 method](../data/2014/Early_Offseason/staff_changes/carousel_method.json) (stage 1) drew every club but Jacksonville | A review with frozen criteria for every club, as Jacksonville's January 15, 2014 review was ([Entry 1](../career/2013/season_review/owner_and_gm_review.md#entry-1-criteria-freeze)) |
| The club's questions and reasons | Still on the Season Review Briefing and the Club Decision | On the same pages, from each club's frozen criteria |
| My Season Response | Can correct a factual input before the draw | Read against the frozen criteria |
| Stone's input and a meeting | Whether and when the club asks for them is fixed in the method before the final game | The same |

Why it matters: in January 2014 the other 31 clubs received a probability draw while Jacksonville, already decided by its January 15 review, received none. Two methods in one league fail the label-swap test ([Document 1 §9.1](../foundation/01_Project_Instructions.md#91-protagonist-blind-resolution-and-anti-favoritism)). Whichever the user chooses is written into the 2014 employment method before Jacksonville's final 2014 game. The closed 2013 decision stays as it is.

### No fixed meeting ritual

The model supports at least four timelines without inventing conversations:

- Club requests review -> Stone responds -> club decides -> result.
- Club determines retention immediately -> result -> optional later football meeting or extension discussion.
- Club dismisses Stone immediately -> result -> agent/career view (no fictitious prior `My_Season_Response.md`).
- Club requests information -> a specified clarification remains unanswered -> only dependent decision waits; other legitimate work continues.

Do **not** use December 29, 2014 as a compulsory dismissal, review or decision date. It is the day after the last regular-season games, when the league's futures-contract signing period opens ([2014 calendar](../career/2014/Calendar.md); [2014 NFL calendar](../library/2014_nfl_calendar.md)). It is not a mandatory NFL deadline and not Jacksonville's review date if the club has a playoff game to play.

## D. Who owns what

- **Khan and Caldwell:** final retain/dismiss decision under the current authority map (Document 3 row 1); must be a real action before results or job status change. They also decide, under the same row, whether to offer Stone an extension (section C, item 8).
- **Khan:** alone decides another club's request to contact or interview Stone (Document 3 row 1a): he may grant it, refuse it, or ask for compensation under the head-coach exception. Stone's standing answer is that he is not open to job offers, so such a request and Khan's answer reach him only as news, FOR YOUR INFORMATION, never ACTION REQUIRED.
- **Stone:** his presentation, his own contract asks/acceptance/counter/decline, resignations, staff choices and football direction within existing authority. On player contracts he recommends and Caldwell decides.
- **Caldwell:** final acquisition, trade, player contract and cap decisions, plus required QB consultation with Stone as already negotiated. Do not make Stone's speech execute any of these. If Stone is dismissed while staff items are open, Caldwell answers for Jacksonville.
- **Medical staff:** diagnosis, restrictions and clearance. Not determined by success/failure of the head-coach season.
- **Agent:** career choices after Stone is legally free to seek work, or permitted outside employment contacts. Dismissal changes the audience for future private football briefings.
- **Players/assistants/other clubs:** independent agents, no guaranteed assent to a coaching recommendation, contract request or interview.
- **Another club's request to interview a Jacksonville assistant:** answered by Jacksonville's standing instruction, given by the user on October 20, 2026 and matching the [January 2014 policy](../career/2014/Early_Offseason/staff_changes/README.md#interview-permission-january-2014-policy): grant an assistant's head-coach interview and a position coach's coordinator interview; refuse a move to the same title. For a request the instruction does not name, a real step up the staff ladder is granted, a nominal title at the same level counts as lateral and is refused, and a different position at the same level goes to Stone as a staff-permission item. Requests the instruction answers appear on the briefing as FOR YOUR INFORMATION. Other clubs answer Jacksonville's requests for their assistants by the same symmetric rule, as the 2014 method did; that is this design's method rule, not a league rule.

For the existing 2014 career, Stone's [coach record](../data/people/coaches/alex_stone.json) holds the contract signed January 15, 2013 for the 2013 to 2016 seasons. Signed on that date: the length, the guarantee (every season) and the authority terms. Reconstructions, completed on October 19, 2026 under the user's delegation and labelled so in the coach record and on [Contract and jobs](../career/Stone/Contract_and_Jobs.md): the end date, the later of January 31, 2017 or the day after Jacksonville's last 2016 game (from the wording of Jacksonville's own 2010 assistant contracts, library row C73), and the salary, offset, dismissal terms, signing bonus and options (from comparable head-coach contracts of the time). 2014 is **not** an expiry year. Show each term with its label. Verify whether a payment is unpaid and the termination classification before claiming a sum. The coach record states no grounds for cause, only that nothing further is owed after a dismissal for cause; the build either completes the grounds as a labelled reconstruction or refuses that classification until they exist. Neither retention nor a positive review automatically adds a year, raise or new authority.

## E. Evidence contract and editorial guardrails

**Facts with provenance**

1. A season stat must come from closed game books/receipts through the stated cutoff, with playoff data separate. It is not safe to add provisional awards or another club's unplayed results.
2. A prior employment standard must originate in the actual hire or dated earlier review, never be reverse-engineered from the current finish. For the 2014 review the standards on record are the club's recorded hire criteria, the contract's first-season standard (a signed term for 2013) and Caldwell's first 2014 measures from the January 15, 2014 review: the scoring margin, and the quarterback's ball security and protection. Khan's request to prepare the London week is an organizational request, not a performance concern; the briefing shows its status (open, met or withdrawn) from the job record, settled when the Week 10 London game closes. The October 5, 2014 ownership review does not count as concerns delivered to Stone: no record shows it delivered. A later 2014 result cannot be fabricated to satisfy any of them.
3. Personnel and coaching evaluations must distinguish the coach's decisions from Caldwell's acquisitions and player execution. A sack/turnover is not independently proof of a missed technique or poor call.
4. Contract figures only from the terms in Stone's coach record, signed or adopted reconstruction, each shown with its label, or from a sourced library entry. Do not write invented cap totals or contract extension terms. If no offer, say so.
5. A spoken owner quote or a dialogue exchange is never manufactured just to make the briefing vivid. If the club issued written concerns, quote/paraphrase that written message and identify the author; if not, issue a factual meeting notice instead.
6. No template requirement for a player grade, emotional confession, blame allocation, praise paragraph, minimum interview count, compulsory philosophical change or fixed numbers of “wins and weaknesses.”
7. Avoid technical system words in reader-facing football text; internal provenance, hashes and tests stay in the data owner or implementation docs.
8. The club may disagree with Stone or retain him despite serious criticism, or dismiss him after meaningful football progress, if the independent evidence and previously established employer method warrant it. Never force a happy ending.

**The three prose jobs must not duplicate each other:** Brief = what the employer has communicated and is asking; Response = Stone's own position; Decision = completed employer action and reasons. The separate football `season_review.md` owns the full season narrative.

## F. Validation / regression tests

1. **Regular season vs playoffs:** 2014 Week 17 ends without Jacksonville elimination -> no season-end documents yet; later final playoff game triggers the process once, with correct NFL season ownership.
2. **No invented last game:** last closed game Week 5 -> 2014 season review remains unissued; no final 2014 record, score, grade, awards or outcome manufactured.
3. **Prior criteria immutable:** review includes the club's recorded 2013 hire criteria, the contract's first-season standard and Caldwell's January 2014 measures; the October 5, 2014 ownership review is not presented as a delivered concern; a new unstated requirement is rejected as an earlier criterion.
4. **No date invented:** owner has not scheduled a meeting -> briefing shows “Not scheduled,” not fake January appointment.
5. **Dismissal without a formal hearing:** where the frozen method has the club decide without asking for Stone's input, the employer may record a dismissal before a user response, producing an immediate standalone `Club_Decision.md`, without generating fictitious `My_Season_Response.md` or a meeting transcript.
6. **User decision vs owner authority:** a response saying “I retain myself” fails; a request to discuss an extension does not create a signed extension.
7. **No appearance bias:** equivalent football/contract evidence with Stone's identity swapped or his response paraphrased at different length yields the same employer evaluation, and the same method decides every club.
8. **Concrete correction permitted:** a sourced factual correction can change the evaluated fact before the club decides; a rhetorical restatement cannot.
9. **Different legal outcomes:** retained unchanged, dismissed without cause, dismissed for cause, term expires, and genuine separation correctly apply only the terms in the coach record, each with its label, the effective dates and actor authority; a classification for which the record holds no term is reported unresolved.
10. **No automatic future contract:** retained under existing 2013-2016 terms; no fabricated 2017 season on the contract.
11. **Financial specificity:** unpaid guarantee, offset and cause distinctions are read from the adopted coach record and shown as reconstructions completed October 19, 2026; unresolved accounting is explicitly unresolved, never estimated by model storytelling.
12. **Separate output rule:** club employment decision has one dated canonical `Club_Decision.md`; a later extension offer arrives as an ACTION REQUIRED insert, is answered on that phase's My Responses page and has its one result page, New Contract or Unchanged, in `career/Stone/`; each staff appointment and player contract has its own result under its own owner. Links from the same phase index do not merge the outputs.
13. **No private Jacksonville brief after termination:** routing immediately switches to agent/career desk, without leaked scouting, contract proposals or current player information.
14. **No empty fake team records:** player/staff exit interviews exist only if they actually happened; team football review stays separate and cannot be overwritten by owner briefing.
15. **Cross-platform paths:** `Season_Review_Briefing.md` and existing `season_review.md` both resolve on case-insensitive filesystems. Registry/links and generated views agree.
16. **Idempotent rendering:** under the one reissue rule ([event inserts](event_inserts.md), section A, item 6), rebuilding an issued brief does not change its historical bytes; a dated new issue keeps the prior edition.
17. **State consistency:** once a decision is committed, coach record, current job, delegation, authority, career desk, event record, and permitted year handoff agree. No half-completed dismissal.
18. **No no-answer auto-approval:** missed reply leaves the required answer unresolved unless there is an explicitly lawful and recorded independent employer decision, which is its own action rather than silence treated as consent.
19. **Offseason ownership:** employer can continue independent evaluation and league dates, while Stone-owned offers/asks remain pending only where genuinely dependent; an answer due after the event it would hold stops nothing.
20. **Editorial gate:** review a standalone draft with its headings removed. If the owner sounds like a fill-in form, the club rewrites the section. This gate is **not** a keyword linter and cannot be passed solely by score/hash checks.
21. **Another club calls about Stone:** Khan decides under row 1a; the request and his answer reach Stone as FOR YOUR INFORMATION, and no answer from Stone is opened.
22. **Closing season's record:** the 2014 Club Decision, written in January 2015, lists in the 2014 annual record.

## G. Suggested module boundaries, not required filenames

- Extend `runtime/decisions.py` with a distinct season-end page route (brief, response, club decision) while preserving the team football review owner. Rename the brief and response in the registry and the rebuild plan's table together, with `docs/event_inserts.md` and `tests/test_game_week_pages.py`; drop the registry's separate Extension Offer brief and its answer page (section C, item 8).
- Add a season-end decision event class and a **separate** employer-owned decision state, not a Stone-owned employment-retention checkbox in `runtime/decision_queue.py`. Wire legitimate, dated dependent stops.
- Add a coach-record entry for retention and dismissal (disposition, effective date, classification) in `runtime/coaches.py`, and an owner row for the head-coach employment decision in `docs/update_workflow.md`.
- Add the 2014 postseason slots input, and the 2014 employment method once the user decides ([section C](#how-the-club-decides-awaiting-the-users-decision)), frozen before the final game.
- Build a reader-visible issue-preserving briefing renderer that accepts event inserts from the existing shared insert component. Support owner review on a non-game day, and the agent view after loss of employment.
- Add a response validator that checks actual user-authored headings, source-linked claims, requests and authority, while allowing “No change” and limited answers.
- Build a club decision writer that closes its distinct event, applies contract and role changes, emits the report immediately, then refreshes dependent views. The team season synthesis and exit interview owners remain independent.
- Add a handoff gate so staging cannot open the next season before the employment decision is recorded, the route for a dismissal before the final game, and the between-jobs desk.
- Update the relevant `docs/rebuild_plan.md`, `docs/season_cycle_milestones.md` (Stone stops at the ownership review only when the club asks for his input), `docs/update_workflow.md`, `foundation/templates/season_review/README.md`, `career/2014/Season_Review/README.md` (the team review holds no ownership decision) and `foundation/decision_rules.md` **by replacing conflicting instructions**, not stacking another loose list. Ensure current repository validation and its test suite still pass.

A design specification alone does not implement these modules. No canonical 2014 event has been advanced or altered.
