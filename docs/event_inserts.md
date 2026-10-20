# Event inserts: implementation and validation specification

**Status:** Uploaded by the user on October 20, 2026 and adopted; built in step 5 of the [rebuild plan](rebuild_plan.md). The templates are in [foundation/templates/event_inserts/](../foundation/templates/event_inserts/) and the worked scenarios in [docs/examples/2014_event_scenarios.md](examples/2014_event_scenarios.md).

**Fixed requirement (the user's rule):** one active period briefing and one possible shared response page, but one standalone dated result file per resolved event, individual trades included. Never aggregate separate outcomes into one output or postpone them until the weekly game report.

**Scope:** Applies to 2014-era decisions at their actual in-career dates, not real-world results after divergence. Keep legacy Weeks 1 to 5 closed and immutable.

## A. Architecture: event source -> active briefing -> response -> result

1. **Event source**: a dated, canonical record contains `id`, `kind`, `raised_at`, `known_to`, `source`, `authority`, `state`, `deadline`, `options/evidence`, `effects`, and links to offers/contracts/medical/roster/coach records as applicable. No invented salary, interest or market price.
2. **Decision queue**: an event requiring Stone opens an item with exact authority, dependency and due time. An informational event never gets a user-owned blocking item. Do not make every potential transaction into an offer.
3. **Brief routing**: render a single `ACTION REQUIRED` section at the *top* of the active `Game_Week_Briefing.md`, `Bye_Week_Review.md`, `Season_Review.md`, another active phase's brief, or `career/Stone` agent/career view once Stone is no longer employed. Use `FOR YOUR INFORMATION` and `COMING UP` for nonblocking material. If none exists, omit the sections.
4. **Response**: a concise block with matching event ID in one `My_Responses.md` journal for the current week/phase, or the equivalent authorized answer channel. Keep `Game_Plan.md` immutable after its freeze; never overwrite it in response to a later trade call.
5. **Resolution, one separate output per event**: the actor with final authority decides or the event is otherwise properly resolved. On that simulated date, commit a **distinct Markdown result document for this event alone** to its canonical department/career owner, whether an offer is accepted, rejected, withdrawn or closes without a deal. A live unresolved negotiation retains dated process records, not an invented final result. Record the response to that event; add its own link to the current week's/phase's index and a short link in the ordinary week/phase report. **No combined Event Results page may substitute for these files.**
6. **Immutable briefings**: an important dated event creates a *new issued version* of the active briefing while preserving every previously issued copy and its issue record. The current view points to the latest issued version. Don't silently overwrite what Stone previously saw.

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
| Another club seeks assistant interview | Apply **that season's** head-coach versus assistant permission rules. In-force standing rule can answer without user prompt |
| Head-coach vacancy confirmed | NEWS unless the inquiring club genuinely requests contact with Stone or Stone is free to seek it |
| Actual owner/GM extension offer to Stone | ACTION REQUIRED with concrete written terms |
| Owner fires Stone | Notify as finalized club decision; immediately reroute future action notices to agent/career view. Never offer Stone a choice to veto firing |
| Stone's contract expires | Verify end terms/date; switch to free-agent/agent desk and job-search instructions, no phantom Jaguars briefing |

## C. Urgency and time

The briefing insertion order is: (1) pending decision that blocks a dated action, earliest due first; (2) other pending consequential answers; (3) FYI; (4) upcoming windows. Show exact ET deadlines where known, otherwise say “not set.” If an offer expires before the next weekly briefing, issue an immediate revision and stop before the expiring action is committed. Independent work may proceed. No reply is never yes or no; if Stone explicitly authorizes passing the deadline, the elapsed-time consequence can then close as “lapsed.” Do not duplicate the same notice on every open page; reference its current event and last communication.

A “trade deadline approaching” window is not a reason to manufacture a trade. A vacancy alone is not an invitation, and a player's extension eligibility is not proof of agent interest.

## D. Year-specific rules and authority

- **2014 trade deadline:** October 28, 2014, 4 p.m. ET. Recompute season-specific deadline for later years, do not apply today's deadline. The current calendar already knows this date.
- **2014 coaching carousel:** Black Monday was December 29, 2014; firings can happen on other dates. NFL interview rules in this era do not permit arbitrary contact with an employed head coach during his club's active season. For an assistant of a playoff club, use the then-applicable postseason interview windows, not later virtual-interview rules.
- **2014 assistant permissions:** the 2014-era protected move was an assistant pursuing an actual head-coaching job. A lateral move, including position coach -> coordinator under then-applicable rules, could generally be withheld while under contract. The repo has a *standing permission preference* that may grant more than legally required; preserve it unless Stone changes it. Do not import the 2020 coordinator-promotion protection into 2014.
- **Player contracts:** drafted rookies are ineligible for renegotiation until after their third contracted regular season; undrafted rookies until after their second. Verify original player contract, rights, league year, guarantees, cap effect and applicable franchise/tender restrictions. A veteran deal may be extendable during the season subject to the 2011 CBA and original deal. Never use a fabricated market quote or deterministic “delay tax.”
- **Stone's authority:** Caldwell executes player acquisitions, contracts and trades; Stone supplies requested football recommendation and retains his specified QB consultation right. Stone selects his assistant staff inside the approved budget. Khan/Caldwell determine Stone's own employment. Stone accepts, rejects or counters personal offers himself.
- **Coach standing contract:** as recorded at the Oct 5, 2014 checkpoint, Stone's four-year deal runs through the later of January 31, 2017 or the day after Jacksonville's last 2016 game, unless changed by a real employment event. No weekly fictitious expiration warning.
- **Who approves another club contacting Stone:** settled by the user's employment answers of October 18, 2026 (recorded in the [rebuild plan](rebuild_plan.md)): Stone keeps a standing yes-or-no answer to whether he is open to job offers, and Shad Khan and David Caldwell handle the club's formal permission. Verify the standing answer on file before routing a request; do not invent one.

## E. Files and integration points in existing repository

- Keep `runtime/decisions.py` registry for main phases; add *insertable* event kinds, not ten new independent briefing builders.
- Expand `runtime/decision_queue.py` with event-scoped blocks for transactions, offers, staff consents and employment responses, and valid requesters/roles. Do not block a whole `week_inputs` package for unrelated business unless a material dependent roster/game role actually changes.
- Build an event-router and a shared insert renderer called by `scripts/render_game_week.py`, the future bye renderer and future season/career briefing builders. Preserve the existing `briefings.json` issue history.
- Use `docs/update_workflow.md` and `docs/rebuild_plan.md` as single governing workflow owners. Replace, don't simply add contradictory old “separate brief for every decision” instructions.
- Reuse active `career/2014/Team_Operations/Trades/` and their data owners, `data/people/coaches/`, roster, contract, cap and injury owners; add only the minimal new response surface.
- Extend the career desk to show all pending time-sensitive answers regardless of current phase. After loss of employment, enforce visibility change.

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

## G. Sources and verification

Repository: `docs/season_cycle_milestones.md`, `foundation/decision_rules.md`, `foundation/03_Head_Coach_Organization_and_Authority_Canon.md`, `library/2014_coaching_hiring_and_anti_tampering_rules.md`, `docs/rebuild_plan.md`.

External era sources: [2014 trade deadline reporting](https://www.bleedinggreennation.com/2014/10/28/7085525/nfl-trade-deadline-philadelphia-eagles-transaction-2014), [2014 NFL calendar](https://www.buffalobills.com/news/important-dates-on-the-2014-nfl-calendar-12566429), [2014 rookie renegotiation explainer](https://www.ninersnation.com/2014/5/16/5723510/breaking-down-the-cba-rookie-contracts), [December 29, 2014 coaching carousel](https://www.si.com/nfl/2014/12/29/nfl-black-monday-coaches-fired-tracker). Later rule summaries must never be silently imported into 2014.
