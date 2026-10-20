# Season-end workflow: implementation, evidence and tests

**Status:** Uploaded by the user on October 20, 2026 and adopted; built in step 6 of the [rebuild plan](rebuild_plan.md). The templates are in [foundation/templates/season_end/](../foundation/templates/season_end/) and the worked example is [docs/examples/season_end_2013_precedent_and_2014_setup.md](examples/season_end_2013_precedent_and_2014_setup.md). The user ruled on October 20, 2026 that Stone's season-end page is separate from the weekly My Responses page and has a different name: it is My Season Response (`My_Season_Response.md`, from the [My Season Response template](../foundation/templates/season_end/my_season_response_template.md)).

As uploaded: **Proposal only. No GitHub implementation or career event is authorized by this design.** Apply to the next actual final game of Stone's club and later years. Never rewrite closed 2013 history or pre-decide the unplayed 2014 season.

## Season ends: ownership review and club decision

**Design proposal, not installed in the repository.** Applies after Jacksonville's **actual final game of an NFL season**, whether that is Week 17 or a postseason game. No 2014 ending has been played or presumed by these documents.

### Reader-facing files

| Proposed file | Owner | What it does |
|---|---|---|
| `Season_Review_Briefing.md` | Khan and Caldwell, with evidence supplied by the football department | Gives Stone their communicated concerns and the questions they want answered. It does **not** announce a decision they have not made. |
| `My_Season_Response.md` | Stone | Holds Stone's actual account of the football year and any request he deliberately makes. |
| `Club_Decision.md` | Khan and Caldwell | Records the club's completed employment decision and its actual consequences. |

The existing `career/YEAR/Season_Review/season_review.md` **is a different document**, the football-department's team season report. It remains in place and owns the detailed offensive, defensive, special-teams, player-development and coaching review. The proposed `Season_Review_Briefing.md` deliberately has a different filename to avoid a case-insensitive clash with that established owner. Alter the registry and links together when implemented.

### Supporting files

- This document gives the decision gates, authority boundaries, chronology, independent ownership decision method, validation and regression tests.
- [`season_end_2013_precedent_and_2014_setup.md`](examples/season_end_2013_precedent_and_2014_setup.md) shows what can be stated from the closed 2013 review and 2014 evidence **without fabricating a 2014 outcome or owner conversation**.

### Governing distinctions

1. The **club** decides whether Stone stays, with which existing terms, and whether it wishes to make a new offer. Stone does not decide his own retention.
2. A **meeting** is not mandatory. The owner may issue a lawful employment decision before meeting the coach. In that case record the real decision, do not generate fake prior discussion or an answered `My_Season_Response.md`.
3. Being **retained** does not mean getting a raise, extension, new authority or guaranteed employment for another year. Such changes need real offers, approval and signatures.
4. A separate extension negotiation, hiring request, staff appointment, assistant exit, trade or player contract is a **separate event** with its **own dated output**, even if introduced in this briefing and answered through `My_Responses.md`.
5. If employment ends, stop showing confidential Jacksonville briefings to Stone and route the next genuine career decisions to his agent/career view.
6. The existing 2013 closed decision must not be revised and the 2014 outcome must not be preselected.

Read the implementation specification before attempting to use these Markdown files with the current parsers. This is a template design only; it does not advance game time or alter any canonical record.

## A. Research-supported design decision

A head coach's employment status and the club's football evaluation are related but distinct. In late 2013, the real Jacksonville GM and coach reviewed the season publicly in terms of organizational standards, football progress and personnel, not a rigid numerical coaching scorecard. Contemporaneous coverage of NFL head-coach decisions recognizes signed contracts, owner/GM alignment, quarterback continuity, the cost of changing a system and the season's record as possible considerations. An owner may dismiss a coach in a brief post-season meeting; a formal hearing is not a universally mandatory step.

**Sources for process only; never import these clubs' real post-divergence decisions into the simulation:**

- Jaguars, December 31, 2013, “Inside the Jaguars: Setting a standard”: https://www.jaguars.com/news/inside-the-jaguars-setting-a-standard-12332888
- NFL.com, Judy Battista, December 2013, “Why some teams acted and others didn't”: https://www.nfl.com/news/nfl-coaching-carousel-why-some-teams-acted-and-others-didn-t-0ap2000000307301
- NFL.com, December 30, 2013, Mike Shanahan dismissal, illustrating that a club need not conduct a prior defense-of-performance hearing: https://www.nfl.com/news/mike-shanahan-fired-as-washington-redskins-coach-0ap2000000306955
- SI, Andrew Brandt, January 16, 2014, coach-contract offset clauses: https://www.si.com/nfl/2014/01/16/nfl-finances-concussion-settlement-playoff-pay
- Jaguars, December 31, 2014, “What We Learned: The Aftermath”, contextual example of separate GM and HC season-end communication and staff authority: https://www.jaguars.com/news/what-we-learned-the-aftermath-14699947 (format only, not branch events).

## B. Existing owners to preserve

| Existing record | Its role and required boundary |
|---|---|
| `career/YEAR/Season_Review/season_review.md` | **Team football synthesis**. Already prescribed by `foundation/templates/season_review/season_review.md`. Do not replace or duplicate it with the new ownership briefing. |
| `career/YEAR/Season_Review/Exit_Interviews/` | Actual player/staff interviews, individually dated; no fabricated blanket meeting. |
| `career/YEAR/Season_Review/Player_Assessments/` | Individual final assessments. Do not issue an extra set of grades in the owner review. |
| `data/YEAR/Season_Review/season_handoff.json` | The existing 2014 team-close and 2015 opening source/checklist. Do not create a competing handoff manifest. |
| `career/2013/season_review/owner_and_gm_review.md` | Closed January 15, 2014 **precedent**. Its retained/unchanged outcome is canon and must remain. |
| `career/Stone/Performance_Reviews.md` | Existing ownership perspective and standing concerns. This assessment is not itself a new legal employment decision. |
| `data/people/coaches/alex_stone.json` and `state/current_job.json` | Employment contract and live authority owners. Update only on the actual employment event; do not invent an extension. |
| `state/decision_queue.json` | User decisions that are genuinely pending, owned and consequential; employer's decision is not owned by Stone. |
| [`docs/event_inserts.md`](event_inserts.md) and [`foundation/templates/event_inserts/`](../foundation/templates/event_inserts/) | Existing design for one active briefing / answer surface and **one standalone dated output per resolved independent event**. Reuse it for extension, staff, trade and job-search events. |

### Filenames: avoid a real collision

The original `runtime/decisions.py` registry declares `Season Review` -> `My Response` -> `Club Decision` under `career/YEAR/Season_Review/`. That collides conceptually and, if named `Season_Review.md`, **case-insensitively** with the existing team `season_review.md`. Implement:

- `Season_Review_Briefing.md` (reader title: “Season Review: Ownership and General Manager”),
- `My_Season_Response.md`,
- `Club_Decision.md`,
- while retaining `season_review.md` unchanged as the team football report.

Update `runtime/decisions.py` registry/page resolver, link generation and validations together. Do not silently rename legacy `season_review.md` or maintain two synthesized team reports.

## C. Trigger, calendar and sequence

1. **Actual team completion.** Start only after Jacksonville's final played game of that NFL season. If the club qualifies for the playoffs, Week 17 alone is insufficient; the real elimination or Super Bowl completion is the trigger. Calendar and NFL-season ownership for January/February remain with the preceding NFL season. Do not import the actual 2014 Jaguars finish.
2. **Freeze the employer's decision basis before its resolution.** The signed hire criteria, later properly communicated performance priorities, record, and legally relevant contract terms must be available with valid as-of timestamps. Where the implementation needs an independent discretionary club decision, bind a method to substantive facts *before* reading Stone's answer. Do not invent arbitrary “owner satisfaction” scores, secret fixed wins or guaranteed retention. An adjudication unable to distinguish possible outcomes must say its decision method is unresolved rather than make up an answer.
3. **Team review and individual records remain distinct.** Gather completed game books, final stats, the detailed team review when actually ready, medical/contract records, completed exit interviews and staff issues. No forced parallel completion: if ownership decides before all exit interviews or league awards finish, use the evidence available at that actual moment.
4. **Does ownership actually request Stone's input?** If yes, issue the briefing with the specific communicated concerns and genuine meeting date/deadline; the `My_Season_Response.md` user turn opens only for those requests. If the club has already decided and communicated termination, write the decision first; do not invent a meeting, and do not ask Stone to “approve” the firing. If the owner has conveyed retention before a later discussion, preserve that decision and treat subsequent requests as separate issues.
5. **Stone's response.** Accept same fixed headings, or the same named sections in an uploaded `.md` / `.txt` or chat. Permit brief football prose, concrete proposals, “None”/“No change” where applicable. Reject contradictions to the real roster/playbook/contract/authority; do not accept ghost offers. An unanswered required choice holds only genuinely dependent actions, not the league's games or unrelated offseason work. Silence never equals approval, acceptance or request.
6. **Independent decision.** Khan/Caldwell determine Stone's employment. The decision accounts for the earlier frozen criteria, actual results, roster and staff circumstances, contract and material new information, under protagonist-blind logic. Stone may rebut an error or provide a *substantive* new plan; rhetorical polish, word count and actor name cannot change the conclusion. An owner's private mental state is not magically conveyed to the coach.
7. **Write result immediately.** When the club actually decides, issue `Club_Decision.md` then and there, with real date, actual basis, input where applicable, status, financial/authority consequences and access change. Record one canonical event in the coach job/contract owner, then rebuild dependent live state, desk, calendar and annual event index. A pending matter has no fabricated final output.
8. **Separate event outputs.** If Stone is **retained** and later receives an extension offer, the offer and any final negotiation have their **own dated event result**. If fired, the employment decision is the `Club_Decision.md` (do not duplicate it as a second dismissal result), while the agent's job search, each interview, each separate offer and each new contract receive their own outputs. The same holds for assistant contracts, trades, player extensions, permission decisions and January staff actions.
9. **Season handoff.** Staging may use only actually closed team gates and valid carry-forward data. Retaining the head coach does not authorize roster renewal, staff changes, new practice, medical clearance or a future year's first game. If dismissed, transfer current football authority appropriately and cease Stone's access to Jacksonville's restricted operations.

### No fixed meeting ritual

The model supports at least four timelines without inventing conversations:

- Club requests review -> Stone responds -> club decides -> result.
- Club determines retention immediately -> result -> optional later football meeting or extension discussion.
- Club dismisses Stone immediately -> result -> agent/career view (no fictitious prior `My_Season_Response.md`).
- Club requests information -> a specified clarification remains unanswered -> only dependent decision waits; other legitimate work continues.

Do **not** use December 29 (“Black Monday”) as a compulsory dismissal, review or decision date. It was the Monday after the real 2014 regular season, not a mandatory NFL deadline and not Jacksonville's review date if the simulated team has a playoff game to play.

## D. Who owns what

- **Khan and Caldwell:** final retain/dismiss decision under the current authority map; must be a real action before results or job status change.
- **Stone:** his presentation, his own contract asks/acceptance/counter/decline, resignations, staff choices and football direction within existing authority.
- **Caldwell:** final acquisition, trade, player contract and cap decisions, plus required QB consultation with Stone as already negotiated. Do not make Stone's speech execute any of these.
- **Medical staff:** diagnosis, restrictions and clearance. Not determined by success/failure of the head-coach season.
- **Agent:** career choices after Stone is legally free to seek work, or permitted outside employment contacts. Dismissal changes the audience for future private football briefings.
- **Players/assistants/other clubs:** independent agents, no guaranteed assent to a coaching recommendation, contract request or interview.

For the existing 2014 career, Stone's signed head-coach agreement is recorded as 2013-2016, with a completed end date of the later of January 31, 2017 or the day after the club's last game in the 2016 season; 2014 is **not** an expiry year. Fully guaranteed and offset terms are documented in `career/Stone/Contract_and_Jobs.md`. Verify whether a payment is unpaid and the termination classification before claiming a sum. Neither retention nor a positive review automatically adds a year, raise or new authority.

## E. Evidence contract and editorial guardrails

**Facts with provenance**

1. A season stat must come from closed game books/receipts through the stated cutoff, with playoff data separate. It is not safe to add provisional awards or another club's unplayed results.
2. A prior employment standard must originate in the actual hire or dated earlier review, never be reverse-engineered from the current finish. The January 15, 2014 club assessment singled out scoring margin, quarterback ball security and protection as 2014 concerns. A later 2014 result cannot be fabricated to satisfy them.
3. Personnel and coaching evaluations must distinguish the coach's decisions from Caldwell's acquisitions and player execution. A sack/turnover is not independently proof of a missed technique or poor call.
4. Contract figures only from signed or explicitly adopted branch reconstructions. Do not write invented cap totals or contract extension terms. If no offer, say so.
5. A spoken owner quote or a dialogue exchange is never manufactured just to make the briefing vivid. If the club issued written concerns, quote/paraphrase that written message and identify the author; if not, issue a factual meeting notice instead.
6. No template requirement for a player grade, emotional confession, blame allocation, praise paragraph, minimum interview count, compulsory philosophical change or fixed numbers of “wins and weaknesses.”
7. Avoid technical system words in reader-facing football text; internal provenance, hashes and tests stay in the data owner or implementation docs.
8. The club may disagree with Stone or retain him despite serious criticism, or dismiss him after meaningful football progress, if the independent evidence and previously established employer method warrant it. Never force a happy ending.

**The three prose jobs must not duplicate each other:** Brief = what the employer has communicated and is asking; Response = Stone's own position; Decision = completed employer action and reasons. The separate football `season_review.md` owns the full season narrative.

## F. Validation / regression tests

1. **Regular season vs playoffs:** 2014 Week 17 ends without Jacksonville elimination -> no season-end documents yet; later final playoff game triggers the process once, with correct NFL season ownership.
2. **No invented last game:** Week 5 current checkpoint -> 2014 season review remains unissued; no final 2014 record, score, grade, awards or outcome manufactured.
3. **Prior criteria immutable:** review includes established 2013 hire and January 2014 concerns; a new unstated requirement is rejected as an earlier criterion.
4. **No date invented:** owner has not scheduled a meeting -> briefing shows “Not scheduled,” not fake January appointment.
5. **Owner dismissal without hearing:** employer may record a dismissal before a user response, producing an immediate standalone `Club_Decision.md`, without generating fictitious `My_Season_Response.md` or a meeting transcript.
6. **User decision vs owner authority:** a response saying “I retain myself” fails; a request to discuss an extension does not create a signed extension.
7. **No appearance bias:** equivalent football/contract evidence with Stone's identity swapped or his response paraphrased at different length yields the same employer evaluation.
8. **Concrete correction permitted:** a sourced factual correction can change the evaluated fact before the club decides; a rhetorical restatement cannot.
9. **Different legal outcomes:** retained unchanged, dismissed without cause, dismissed for cause, term expires, and genuine separation correctly apply only the verified contract terms, effective dates and actor authority.
10. **No automatic future contract:** retained under existing 2013-2016 terms; no fabricated 2017 season on the contract.
11. **Financial specificity:** unpaid guarantee, offset and cause distinctions are read from the adopted coach record; unresolved accounting is explicitly unresolved, never estimated by model storytelling.
12. **Separate output rule:** club employment decision has one dated canonical `Club_Decision.md`; subsequent extension negotiation has its separate result, as does each staff appointment and player contract. Links from the same phase index do not merge the outputs.
13. **No private Jacksonville brief after termination:** routing immediately switches to agent/career desk, without leaked scouting, contract proposals or current player information.
14. **No empty fake team records:** player/staff exit interviews exist only if they actually happened; team football review stays separate and cannot be overwritten by owner briefing.
15. **Cross-platform paths:** `Season_Review_Briefing.md` and existing `season_review.md` both resolve on case-insensitive filesystems. Registry/links and generated views agree.
16. **Idempotent rendering:** rebuilding an issued brief does not change its historical bytes; a newly communicated fact creates a dated new issue and keeps the prior edition.
17. **State consistency:** once a decision is committed, coach record, current job, delegation, authority, career desk, event record, and permitted year handoff agree. No half-completed dismissal.
18. **No no-answer auto-approval:** missed reply leaves the required answer unresolved unless there is an explicitly lawful and recorded independent employer decision, which is its own action rather than silence treated as consent.
19. **Offseason ownership:** employer can continue independent evaluation and league dates, while Stone-owned offers/asks remain pending only where genuinely dependent.
20. **Editorial gate:** review a standalone draft with its headings removed. If the owner sounds like a fill-in form, the club rewrites the section. This gate is **not** a keyword linter and cannot be passed solely by score/hash checks.

## G. Suggested module boundaries, not required filenames

- Extend `runtime/decisions.py` with a distinct season-end page route (brief, response, club decision) while preserving the team football review owner.
- Add a season-end decision event class and a **separate** employer-owned decision state, not a Stone-owned employment-retention checkbox in `runtime/decision_queue.py`. Wire legitimate, dated dependent stops.
- Build a reader-visible issue-preserving briefing renderer that accepts event inserts from the existing shared insert component. Support owner review on a non-game day, and the agent view after loss of employment.
- Add a response validator that checks actual user-authored headings, source-linked claims, requests and authority, while allowing “No change” and limited answers.
- Build a club decision writer that closes its distinct event, applies contract and role changes, emits the report immediately, then refreshes dependent views. The team season synthesis and exit interview owners remain independent.
- Update the relevant `docs/rebuild_plan.md`, `docs/season_cycle_milestones.md`, `docs/update_workflow.md`, `foundation/templates/season_review/README.md`, and `foundation/decision_rules.md` **by replacing conflicting instructions**, not stacking another loose list. Ensure current repository validation and its test suite still pass.

A design specification alone does not implement these modules. No canonical 2014 event has been advanced or altered.
