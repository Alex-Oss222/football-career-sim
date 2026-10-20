# Event inserts: implementation and validation specification

**Status:** Uploaded by the user on October 20, 2026 and adopted; built in step 5 of the [rebuild plan](rebuild_plan.md), except the employment and assistant events, which are built with the employment events in step 6. Corrected the same day after the process check and the user's answers on permissions, the bye and the season page (recorded in the rebuild plan's change log). The templates are in [foundation/templates/event_inserts/](../foundation/templates/event_inserts/) and the worked scenarios in [docs/examples/2014_event_scenarios.md](examples/2014_event_scenarios.md).

**Fixed requirement (the user's rule):** one active period briefing and one possible shared response page, but one standalone dated result file per resolved event, individual trades included. Never aggregate separate outcomes into one output or postpone them until the weekly game report.

**Scope:** Applies to 2014-era decisions at their actual in-career dates, not real-world results after divergence. Keep legacy Weeks 1 to 5 closed and immutable.

## A. Architecture: event source -> active briefing -> response -> result

1. **Event source**: a dated, canonical record contains `id`, `kind`, `raised_at`, `known_to`, `source`, `authority`, `state`, `deadline`, `options/evidence`, `effects`, and links to offers/contracts/medical/roster/coach records as applicable. No invented salary, interest or market price.
2. **Decision queue**: an event requiring Stone opens an item with exact authority, dependency and due time. An informational event never gets a user-owned blocking item. Do not make every potential transaction into an offer.
3. **Brief routing**: render a single `ACTION REQUIRED` section at the *top* of the active `Game_Week_Briefing.md`, `Bye_Week_Review.md`, `Season_Review.md`, another active phase's brief, or `career/Stone` agent/career view once Stone is no longer employed. Use `FOR YOUR INFORMATION` and `COMING UP` for nonblocking material. If none exists, omit the sections.
4. **Response**: a concise block with matching event ID in one `My_Responses.md` journal for the current week/phase, or the equivalent authorized answer channel. Keep `Game_Plan.md` immutable after its freeze; never overwrite it in response to a later trade call.
5. **Resolution, one separate output per event**: the actor with final authority decides or the event is otherwise properly resolved. On that simulated date, commit a **distinct Markdown result document for this event alone** to its canonical department/career owner, whether an offer is accepted, rejected, withdrawn or closes without a deal. A live unresolved negotiation retains dated process records, not an invented final result. Record the response to that event; add its own link to the current week's/phase's index and a short link in the ordinary week/phase report. **No combined Event Results page may substitute for these files.**
6. **Immutable briefings, one reissue rule.** This rule governs the Game Week Briefing, the Bye Week Review and every other phase brief. Issue a new dated version of the active brief when (a) a new event needs an answer from Stone, (b) a dated finding materially changes a choice still pending, or (c) an answer falls due before the next scheduled issue. Keep every issued copy and its issue record; the current view points to the latest issued version. An informational event that affects no pending answer waits for the next scheduled issue; its own result page is readable as soon as it is written. Re-issuing a brief changes no career event. Don't silently overwrite what Stone previously saw.

### Per-event result contract (mandatory)

- Briefing: one active briefing for a week or phase, containing any number of event notices.
- Response: one `My_Responses.md` journal for that week or phase may contain any number of answers, each bound to its source event. Event-specific answer files are optional, not required.
- Output: **N resolved events = N independent dated event outputs**, not a single weekly or generic result. Each stays in the correct in-world time period and is linked from the week/phase index. Rejected trades and declined extension proposals qualify; open negotiations have process entries but no falsely final outcome.
- Source-of-truth: choose **one** canonical reader-facing result per event. An existing standalone completed-trade record should be used as the trade's result when it is already the correct authoritative owner; do not create a duplicate narrative under the week's folder. Index links are sufficient for in-week navigation.
- Timing: write each resolved event output at its own resolution time. Do not wait until Sunday, after the bye or the next game to make it available.
- The ordinary Game Report/Bye Week Report is not a replacement and should link, never paste, each standalone event output.

## B. Trigger model

Check on each simulated date/time advance; after every game, exam, roster transaction, contract negotiation or coaching vacancy event; before a deadline; and when the current authority/employment role changes. Also run a nonblocking weekly eligibility/deadline scan. No real-world polling or guaranteed weekly popups.

| Condition | Correct behavior |
|---|---|
| Injury *and* proposed/actual roster-list action | Notify only if a football role or roster recommendation is actually required; medical decisions remain medical |
| Outside club initiates a genuine trade contact | Date and terms sourced; Caldwell controls talks. Response if Stone's football input is needed |
| Deadline nears, no actual offer | COMING UP only; no fabricated incoming call |
| Player's contract is eligible and strategically relevant | Optional nonblocking extension opportunity; actual formal offer only after genuine negotiation by authorized parties |
| Assistant contract approaches expiration | Show terms and valid date/window; ask Stone only about his staff decision within budget |
| Another club seeks assistant interview | Apply **that season's** league permission rules, then Jacksonville's standing assistant-permission instruction (section D). The instruction answers without asking Stone; the request and Jacksonville's answer are FOR YOUR INFORMATION |
| Another club asks permission to contact or interview Stone | Shad Khan alone decides: grant, refuse, or ask for compensation under the head-coach exception (Document 3 row 1a). Stone's standing answer is that he is not open to job offers, so the request and Khan's answer reach him as FOR YOUR INFORMATION, never ACTION REQUIRED |
| Head-coach vacancy confirmed | FOR YOUR INFORMATION. A vacancy alone is not an approach to Stone |
| Actual owner/GM extension offer to Stone | ACTION REQUIRED with concrete written terms |
| Owner fires Stone | Notify as finalized club decision; immediately reroute future action notices to agent/career view. Never offer Stone a choice to veto firing |
| Stone's contract expires | Verify end terms/date; switch to free-agent/agent desk and job-search instructions, no phantom Jaguars briefing |

## C. Urgency and time

**What stops the clock.** Only an answer due before kickoff (or, in a bye, before the bye's scheduled work) holds Jacksonville's game or the bye's close. Unrelated business never holds a game, and the other clubs' games in the slate close whatever is open for Jacksonville (the user's answers of October 20, 2026).

The briefing insertion order is: (1) pending decision that blocks a dated action, earliest due first; (2) other pending consequential answers; (3) FYI; (4) upcoming windows. Show exact ET deadlines where known, otherwise say “not set.” If an offer expires before the next weekly briefing, issue an immediate revision and stop before the expiring action is committed. Independent work may proceed. No reply is never yes or no; if Stone explicitly authorizes passing the deadline, the elapsed-time consequence can then close as “lapsed.” Do not duplicate the same notice on every open page; reference its current event and last communication.

A “trade deadline approaching” window is not a reason to manufacture a trade. A vacancy alone is not an invitation, and a player's extension eligibility is not proof of agent interest.

## D. Year-specific rules and authority

- **2014 trade deadline:** October 28, 2014, 4 p.m. ET. Recompute season-specific deadline for later years, do not apply today's deadline. The current calendar already knows this date.
- **End of the 2014 regular season:** Jacksonville's last scheduled game is Sunday, December 28, 2014, and the league's futures-contract signing period opens December 29 ([2014 calendar](../career/2014/Calendar.md)). Who is dismissed, and when, is this career's own event, never the real-world list; a dismissal can happen on any date. NFL interview rules in this era do not permit contact with an employed head coach during his club's active season. For an assistant of a playoff club, use the then-applicable postseason interview windows, not later virtual-interview rules.
- **2014 assistant permissions:** under the 2014 rules the only protected move was an assistant pursuing a head-coaching job. Any other move, including a position coach going for a coordinator job, could be refused while the coach was under contract. The rule protecting coordinator interviews dates from May 2020 and does not apply to this career.
- **Jacksonville's assistant-permission instruction:** grant a head-coach interview and a position-coach-to-coordinator interview; refuse a move to the same title elsewhere. It applies alike whatever the asking club, and stays in force until the user changes it. The user gave it on October 20, 2026, matching the January 2014 default in the [staff-changes record](../career/2014/Early_Offseason/staff_changes/README.md#interview-permission-january-2014-policy). It is Jacksonville's choice, not a league rule: another club may still refuse its own assistants a coordinator interview with Jacksonville.
- **Player contracts:** drafted rookies are ineligible for renegotiation until after their third contracted regular season; undrafted rookies until after their second. This rule is not yet in the library: step 5 adds a two-pass library entry before any check enforces it. Verify original player contract, rights, league year, guarantees, cap effect and applicable franchise/tender restrictions. A veteran deal may be extendable during the season subject to the 2011 CBA and original deal. Never use a fabricated market quote or deterministic “delay tax.”
- **Stone's authority:** Caldwell executes player acquisitions, contracts and trades; Stone supplies requested football recommendation and retains his specified QB consultation right. Stone selects his assistant staff inside the approved budget. Khan and Caldwell determine Stone's own employment (row 1). Khan alone decides another club's request to contact or interview Stone (row 1a). Stone accepts, rejects or counters personal offers himself.
- **Stone's contract end:** the signed contract covers the 2013 to 2016 seasons. Its end date, the later of January 31, 2017 or the day after Jacksonville's last 2016 game, is a reconstruction completed on October 19, 2026 under the user's delegation, not a signed term on file; it is labelled so in his [coach record](../data/people/coaches/alex_stone.json), and so are the salary, offset and dismissal terms. It changes only by a real employment event. No weekly fictitious expiration warning.
- **Who approves another club contacting Stone:** settled by the user on October 20, 2026 (recorded in the rebuild plan's change log): Shad Khan alone decides, and may grant, refuse, or ask for compensation under the head-coach exception. Stone's standing answer is that he is not open to job offers, so another club's call reaches him only as news. A compensation proposal for Stone is an employment event, built in step 6.

## E. Files and integration points in existing repository

- Keep `runtime/decisions.py` registry for main phases; add *insertable* event kinds, not ten new independent briefing builders.
- Expand `runtime/decision_queue.py` with event-scoped blocks for transactions, offers, staff consents and employment responses, and valid requesters/roles. Do not block a whole `week_inputs` package for unrelated business unless a material dependent roster/game role actually changes.
- Build an event-router and a shared insert renderer called by `scripts/render_game_week.py`, the future bye renderer and future season/career briefing builders. Preserve the existing `briefings.json` issue history.
- Use `docs/update_workflow.md` and `docs/rebuild_plan.md` as single governing workflow owners. Replace, don't simply add contradictory old “separate brief for every decision” instructions.
- Reuse active `career/2014/Team_Operations/Trades/` and their data owners, `data/people/coaches/`, roster, contract, cap and injury owners; add only the minimal new response surface.
- Extend the career desk to show all pending time-sensitive answers regardless of current phase. After loss of employment, enforce visibility change.
- Store each open event in the data area beside its owner, at a path the folder map names (step 5). Each result page passes the clean-page check and carries its event-record line, so the year's Record.md lists it.

## F. Required tests

1. Week opens without transaction events: the brief has no Action Required section and the game path is unchanged.
2. Genuine trade call arrives after brief issue: immutable new brief is issued; offer is not silently accepted or invented.
3. Trade deadline passes with no offers: no user stop, no fake trade.
4. Player eligibility: drafted 2014 rookie cannot extend in October 2014; appropriate veterans can be considered only after individual cap/contract verification.
5. Medical injury with no list move: no fictitious open roster spot.
6. Medical reserve transaction occurs: legal replacement options surface, Caldwell's final action separately recorded.
7. In-force assistant interview standing rule: response is applied under era-specific permission checks, no duplicate user question.
8. Assistant with playoff club: correct protected interview windows and hiring delay.
9. Stone's termination: no Jacksonville private brief after dismissal; agent/career desk replaces it.
10. Unanswered response with deadline: must not silently resolve or advance a dependent event; user may explicitly decline or permit lapse.
11. Frozen game plan never changes due to midweek or postgame business inserts; genuine depth/roster changes must separately satisfy current game-readiness gates.
12. Every standalone result has one event ID, original triggering fact, legitimate decision/actor, result timestamp, and correct changes to owner + linked reader views.
13. Five independent resolved events in one week (including two different trades, one rejected) create **five distinct output files** and five links in that week's index, even if one briefing and one `My_Responses.md` contain all notices and answers.
14. The first trade closes Tuesday and is readable Tuesday, without waiting for the Sunday game to finish. A second trade still under negotiation has dated process entries but no falsely finalized output.
15. A week's Game Report lists or links the separately completed outputs without copying their content or silently consolidating them into a single transaction summary.
16. Another club asks to contact Stone: Khan's answer is recorded as its own result, Stone's brief shows it as FOR YOUR INFORMATION only, and no ACTION REQUIRED item or queue question reaches Stone.
17. An open question due after kickoff (for example a trade call due Tuesday) does not hold Sunday's game; one due before kickoff does. The other clubs' games in the week close either way.

## G. Sources and verification

Repository: `docs/season_cycle_milestones.md`, `foundation/decision_rules.md`, `foundation/03_Head_Coach_Organization_and_Authority_Canon.md`, `library/2014_coaching_hiring_and_anti_tampering_rules.md`, `docs/rebuild_plan.md`.

External era sources: [2014 trade deadline reporting](https://www.bleedinggreennation.com/2014/10/28/7085525/nfl-trade-deadline-philadelphia-eagles-transaction-2014), [2014 NFL calendar](https://www.buffalobills.com/news/important-dates-on-the-2014-nfl-calendar-12566429), [2014 rookie renegotiation explainer](https://www.ninersnation.com/2014/5/16/5723510/breaking-down-the-cba-rookie-contracts). The end of the regular season and the futures date come from the career's [2014 calendar](../career/2014/Calendar.md); a tracker of real 2014 dismissals is not a source, because real coaching changes are not part of this career ([hiring-rules library](../library/2014_coaching_hiring_and_anti_tampering_rules.md)). Later rule summaries must never be silently imported into 2014.
