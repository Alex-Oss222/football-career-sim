# Coaching vacancy and assistant hiring: implementation and realism specification

**Status:** Proposed design, not installed. Does not authorize a 2014 or 2015 personnel action. Applies whenever the *currently employed and authorized* head coach must fill a real NFL assistant/coordinator position; all dates and permissions follow the actual season being simulated. Preserve existing closed career history.

## 1. Architecture and boundaries

There are three coach-facing pages **per genuine search**:

1. `Candidate_Report.md`: the dated, staff-produced football and eligibility brief for this *specific vacancy*. Issued only once a real vacancy/search exists; updated by immutable reissues as relevant events occur. It is not a universal staff directory.
2. `My_Hire.md`: Stone's fixed-heading, fill-in directions. A decision at a particular stage can be submitted in chat or the page. The stage and its source brief are recorded and immutable after application. A later direction is an explicit amendment, not a retroactive overwrite.
3. `Staff_Hire.md`: the search result and event index. Lists the actual search sequence and whether the job is filled, still open, or lawfully closed without a hire; does not combine the individual candidate/permission/offer/hiring outputs.

**Separate completed event records:** Each concluded request/permission decision, substantive interview, distinct offer disposition and signed appointment receives its own dated readable result, using `Individual_Search_Event_Result_TEMPLATE.md`. One appointment does not erase the unsuccessful contacts. The active week's or phase's index links each independent result when it closes, even if the search itself continues.

The shared **event-inserts v2** format controls the announcement: when the vacancy opens, the current Game Week Briefing, Bye Week Review, Season Review, or offseason desk gets a prominent `ACTION REQUIRED` item if Stone must decide. It links to the Candidate Report; it does not start a redundant vacancy-specific one-page briefing. A search can occur outside January. After Stone leaves the club, his private staffing access and signing authority cease.

The **January Staff Status Report** remains a different workflow: it evaluates incumbents and contracts. It may *cause* a vacancy, but a proposed nonrenewal is not a vacancy until effective. Its completed individual retention/departure records link to this search when one becomes necessary. A simultaneous three-position staff overhaul means three distinguishable vacancies with three candidate searches, not one giant candidate tournament.

## 2. The authoritative football distinctions

| Concept | What it establishes | What it does **not** establish |
|---|---|---|
| A coach's contract reaches its final season | A renewal decision and an expiry issue to verify | Contract already expired, coach already gone, new vacancy |
| Stone chooses a candidate to approach | Stone's authorized priority and the search's next permitted action | Candidate is available, interested, interviewed or hired |
| Employer grants interview permission | This particular legal interview is authorized | Candidate will attend or agree to join |
| Candidate agrees to interview | Candidate is willing to meet under the approved conditions | Candidate will accept a job |
| Interview is held | Actual recorded conversation/notes may inform Stone | Applicant demonstrated mastery of an unrecorded drill, or Stone made a hiring promise |
| Stone authorizes a contract proposal | Club may propose *bounded terms* after actual budget confirmation | Money has been accepted, the salary is in payroll, or candidate joins staff |
| Candidate verbally accepts terms | Subject to the actual league/contract status and executed agreement | All old employer rights, guarantees or effective dates can be ignored |
| Coach's appointment becomes effective | Job and accepted terms change on the authorized date | Position group performance, player ratings or game outcomes automatically improve |

`Stone wants` and `candidate agrees` are always separate fields and independent events. The answer cannot be drawn by copying a name or ranking from the coach's own document. The simulator never gives Jacksonville an acceptance bonus because the user is the protagonist.

## 3. 2014/2015 NFL legal and market rails

- **Tier rules:** For the applicable 2014/2015 staff-hiring period, league anti-tampering rules distinguished head coaches and assistant coaches; titles like position coach and coordinator remained in the same assistant tier for outside hiring. The 2020 change guaranteeing access to interview for certain coordinator promotions cannot be applied backward. A club could refuse an under-contract assistant's interview for a coordinator job in January 2015. See contemporaneous [PFT January 21, 2015](https://www.nbcsports.com/nfl/profootballtalk/rumor-mill/news/fair-or-not-plenty-of-teams-prevent-assistants-from-leaving) and [NFL's May 19, 2020 policy change](https://www.nfl.com/_amp/nfl-announces-new-policies-designed-to-increase-diversity).
- **Head-coaching interview windows are not general assistant-hire windows.** Jacksonville's [2015 NFL dates](https://www.jaguars.com/news/2015-nfl-important-dates-14709246) establish special January windows for assistants being interviewed for **head coach** vacancies while their current clubs are in the playoffs. Do not use those windows to interview a live playoff club's position coach for Jacksonville's coordinator job.
- **Existing employer/rights:** Check the *branch's* dated employer contract, whether that party can legally grant or refuse the requested kind of move, and actual permission. A candidate with no known rights status is not 'unattached'. A real-world appointment made after the 2013 branch divergence is not a branch fact unless a specific authorized rail covers it; coaching changes do not have that exception.
- **Candidate origin:** Free agent, out-of-work coach, currently employed coach, retired coach, current Jacksonville assistant and college coach have distinct restrictions and willingness. Retired does not equal interested. College contracts may contain separate buyouts or permission restrictions. Incomplete evidence is a reason to investigate, not a reason to force availability.
- **Rooney Rule and 2014 era:** The NFL announced in March 2013 that the Rooney Rule would *not* be extended to coordinator vacancies, and it did not cover position coaches in January 2015. Do not install the 2020 coordinator or 2022 quarterbacks-coach requirements in this time frame. Applicable senior head-coach/GM hiring rules remain in their distinct workflows. [NFL 2013 announcement](https://www.nfl.com/news/rooney-rule-will-not-be-extended-to-coordinators-0ap1000000152292); [NFL May 2022 change](https://www.nfl.com/news/nfl-owners-approve-rooney-rule-applying-to-vacant-qb-coach-positions).
- **Dates:** Use the actual 2015 season calendar and date of a verified vacancy. A January search may continue into February or later when interviews, contracts, availability or playoff restrictions require it. No arbitrary 'Black Monday hire deadline'. The 2015 Jacksonville offseason program begins April 20 under the recorded calendar, but this is a preparation target, not an automatic guaranteed hiring date.
- **Pay:** Assistant compensation is an organization expense, not player salary cap. Current scheduled payroll is not remaining budget. Proposed salaries are negotiable and require actual authority and agent/candidate response. Pay-outs on an existing guaranteed coach can overlap new staff salary. Validate guarantees, offsets, contract effective periods and actual club approval; never invent unverified annual values.

## 4. Football sourcing and candidate evaluation

Use only the candidate's verified prior work as known at the current in-career date and the club's properly acquired observations. These establish *experience*, not guaranteed effectiveness or an engine skill score.

For position coaches, test the real unit task: protections, route depth and quarterback footwork, front/run-fit communication, defensive-back pattern-match rules, punt protection, ball security, or player-teaching correction and recheck as suited to the role. A coach who has never performed the job may still be considered; present the training/operational risk and what Stone would need to verify. A prior unit's total yards or sacks is not a causal measurement of one assistant.

For coordinators, ask who prepares the installation, who controls weekly packages, how position coaches communicate, and who makes live game-day calls. Current branch: Stone calls offense and defense (since September 28, 2014); Tice and Crennel prepare their respective units; Westhoff directs special teams. New assistants do **not** receive those calls automatically. A true change of delegation must be separately authored by Stone and entered in current-job authority records. A 'new scheme' needs actual installed plays and subsequent lawful work, not a title line.

Interview evidence is real only when the interview occurs. Create football questions beforehand, then record actual supplied answers or a properly labelled summary of completed discussion. Never fabricate transcripts, performance tests, personal relationships, secret conversations or promises. No fixed candidate count, score grade, perfect pros/cons symmetry or mandatory consensus.

## 5. State machine and safe execution order

A search has a vacancy state and multiple event histories. Each candidate has an independent status. Do not collapse a failed candidate into a filled vacancy or fill a vacancy solely because an earlier candidate accepted an invitation.

**Vacancy:** `UNCONFIRMED` → `CONFIRMED_OPEN` (or dated `OPENING_SCHEDULED`) → `SEARCH_ACTIVE` → `FILLED` / `CLOSED_WITHOUT_HIRE` / `STILL_OPEN`. A planned additional job requires explicit authorization first. `FILLED` requires an accepted and properly executed appointment whose effective date has arrived. No silent `FILLED` fallback.

**Candidate:** `IDENTIFIED` → `RIGHTS_CHECKED` → `PERMISSION_REQUESTED` (if applicable) → `CONTACTED` → `INTERVIEW_OFFERED` → `INTERVIEW_HELD` → `TERMS_AUTHORIZED` → `OFFER_SENT` → `COUNTER_PENDING` / `ACCEPTED` / `DECLINED` / `WITHDRAWN`; the accepted offer then needs a separately verified contract/appointment-effective event. These are illustrative possible stages, not a requirement every candidate pass through each. No employer permission is required of a genuinely free coach; a permission refusal ends that candidate's current request until a new lawful situation exists.

Before advancing any stage: read the controlling source, verify temporal/legal status, and check whether this stage requires Stone's authorized choice. If yes and not covered by an exact IN_FORCE standing instruction, stop only the dependent action; unrelated games, league news and safe administrative work may continue. User silence never means go, decline or approve a salary increase. A conditional fallback may execute only the actual stages authorized in writing. A new contract type, extra years, salary above the approved negotiating ceiling, expanded role, guarantee or different candidate must return to Stone.

Close each *concluded* external request, interview or offer in its own event record immediately. Keep an ongoing process record for still-open conversations. When any party changes state, issue a new dated Candidate Report if Stone needs new evidence, retain the prior issued report and notify the active briefing by event insert.

## 6. Owners, file placement and indexes

**Working example for the January 2015 hiring period**, once that in-world period exists and the season handoff/active folder map permits it:

```
career/2015/Early_Offseason/Staff_Searches/<actual-vacancy-key>/
  Candidate_Report.md
  My_Hire.md
  Staff_Hire.md
  outcomes/
    Permission_Result_<YYYY-MM-DD>_<candidate>.md
    Offer_Result_<YYYY-MM-DD>_<candidate>.md
    Staff_Hire_Result_<YYYY-MM-DD>_<candidate>.md
```

For an in-season vacancy, route the search to the then-active season's Team_Operations/Staff/Staff_Searches (or the established staff transaction owner), with *links* from the appropriate game/bye-week folder. The canonical folder resolver, not ad hoc literal paths, must choose the actual owner. Do not generate new 2015 early-offseason files during the October 2014 career checkpoint simply to satisfy this sample. The January 2015 transition may overlap 2014 Season_Review; a dated staff event must be recorded once and linked between the two, never stored as competing versions of the same hire.

The precise source of truth for an *appointment* is the dated completed appointment record and the actual coach's permanent history/contract data. The `outcomes/` path above is illustrative: if a pre-existing standalone appointment file is already the canonical output, reuse it and have Staff Hire link it, rather than generate a second competing file. For a concluded permission rejection or unsuccessful offer, create its own dated result under the same search owner.

`runtime/decisions.py` already declares `staff_vacancy` as Candidate Report → My Hire → Staff Hire in Early_Offseason but does not implement that workflow. `runtime/decision_queue.py` has a staff appointment class but currently lacks a stage-complete, event-scoped vacancy transition system. Update the decision registry, runner and validators accordingly. Also integrate the shared event-insert renderer from the event-inserts v2 proposal.

On accepted appointment, atomically update:

- **Individual coach's permanent record:** hire/effective date, job, contract reference, exact executed financial terms and contract status.
- **Team staff owner and current authority:** job filled, existing assignments transferred on the correct date; only authorized calling/delegation updates.
- **Coaching finances:** actual annual commitments, guarantee and offset obligations and verified funding; never alter player cap.
- **Current-job state / decision queue:** resolved staff appointment item by Stone's actual recorded direction and candidate assent, plus separate items for changes he did not authorize.
- **Event/annual index:** dated event recorded once, reader-facing search index and current season/phase desk link to all individual concluded stage outputs.
- **Dependent views/season handoff:** 2014 season review and 2015 carry-forward stay coherent, with opening-season readiness checked rather than assumed.

Never write a change to already-closed 2013 or early-2014 search results to make the new format look consistent. Historical episodes remain references.

## 7. Failure and exception rules

| Situation | Required behavior |
|---|---|
| No legal vacancy | No search files, no candidate offer and no fictional interim appointment |
| Expiring contract but no verified exact date | Mark deadline unresolved; verify employer rights before calling the job vacant |
| Incumbent might be renewed | Keep incumbent and possible opening as distinct states until resolution |
| Coach leaves for head-coach job | Record departure on actual date, then open vacancy and inform Stone if he still employs staff |
| Internal assistant promoted | Record role change only with Stone's authorization; open resulting backfill separately if necessary |
| Several vacancies | Each vacancy owns its search and staff result, and each completed stage gets one event result |
| All candidates decline or employers refuse | Keep role open or use authorized interim coverage; return for a new pool, do not invent an easy hire |
| Candidate offers changed duties | Recheck real authority and other coaches' jobs, not just budget |
| Candidate asks for more pay/guarantee | Accept only within Stone's explicit terms after actual funding approval; otherwise pause |
| Jacksonville still in playoffs | Use the applicable recruiting-contact/permission restrictions; no universal January 1 hire |
| Stone dismissed | His staff-selection power ends immediately; route him to his career/agent notice, and resolve club staff choices under its actual new authority |
| Salary budget not quantified | Do not infer a ceiling from total current payroll. Request finance confirmation or hold the offer |
| Assistant hired | No automatic unit wins, player development, skill improvement or new scheme installation |
| Search reviewed after outcome | Preserve all previous dated issue versions and refusals, not hindsight-updated candidate preferences |

## 8. Adversarial tests required before merge

1. No actual vacancy: all three search pages absent; no selection question.
2. Planned expiring deal: candidate search does not open until vacancy/departure confirmed.
3. Legitimate opening after a departure midweek: current brief gets urgent insert without writing a new game result.
4. Vacancy already known: repeated render does not create duplicates or advance time.
5. Existing interim lead from source: preserved; 'interim Stone' not invented for unrelated jobs.
6. No interim lead: vacancy remains correctly uncovered, no silent responsibility handoff.
7. Candidate listed but rights unknown: no legal contact yet; name and open check returned.
8. January 2015 position coach to coordinator: under-contract employer can refuse; protected-2020 rule not applied.
9. Head-coach interview window not misused to recruit another club's playoff assistant for Jacksonville's lateral coordinator job.
10. Unemployed candidate with established freedom: no fake employer permission; actual willingness still required.
11. Retired coach: check willingness and surviving rights; no automatic return.
12. Candidate approached on approved instruction: can decline even when first on Stone's list.
13. Opponent coach actual future employment after branch divergence does not become a predetermined branch result.
14. Interview not held: no fabricated meeting, quote, test result or evaluation improvement.
15. Interview held without detailed notes: report only fact held and next decision; no made-up dialogue.
16. User selects hire before budget and acceptance: pending offer, not executed contract.
17. Offer counters within explicit authorized bound and funded terms: lawful progression only after candidate chooses and terms are reconciled.
18. Counter exceeds bound or changes guarantees: user-required stop before further commitment.
19. Assistant's old guaranteed money survives release under the actual contract; financial totals reconcile.
20. Offer rejected: separate dated Offer Result, vacancy still open; no hire created.
21. Two refused contacts and one accepted coach: three distinct results with dates and one appointment, not one blended search result.
22. One completed interview and later declined offer: distinct stage outcomes if each had a concluded event, no duplicate permanent owner.
23. Two simultaneous vacancies: independent decisions and files, no cross-filling same coach in contradictory roles.
24. Internal promotion moves duty lawfully, opens any secondary vacancy separately and updates reporting lines only from authorized instruction.
25. New defensive coordinator hired while Stone calls defense: Stone remains caller unless separately changed.
26. Stone terminated before staff offer: authorization revoked; no Jacksonville confidential brief or binding offer signed by Stone afterward.
27. Search closes without hire on explicit authorized decision: records uncovered work, not fake staff hire; no 'filled' state.
28. Accepted hire updates permanent coach record, staff page, financial owners, season handoff and annual record consistently on the effective date.
29. No statistical 'coaching improvement bonus' is applied merely from new coach name or a persuasive My Hire paragraph.
30. Candidate reports frozen at issuance: a post-interview reissue does not rewrite the previous statement about availability and interests.
31. The full user-facing Staff Hire page links every separate closed event, and events concluded during a game week appear independently in that week's index before Sunday when feasible.
32. Rebuild and validation produce unchanged output after a second run with no new events and reject alterations to the closed 2014 Westhoff/Lowry history.

## 9. Research basis

**Repository-owned source of actual branch facts:**

- `career/2013/offseason/staff_building/staff_plan.md` and `hires.md`: user-selected candidate order, success/refusal/market obstacles, accepted contracts.
- `career/2014/Early_Offseason/staff_changes/staff_plan.md` and `hires.md`: real branch Lowry vacancy, April permission refusal, Westhoff's interview, offer, counter and appointment.
- `data/2014/Early_Offseason/staff_changes/st_search_method.json` and `st_search_results.json`: previously frozen private-resolution method and closed dated outcome. Preserve those events, not their method's context as an automatic future rule.
- `career/2014/Team_Operations/Staff/README.md` and `career/finances/coaching_and_organization/coaching_payroll.md`: current responsibilities and contractual commitments.
- `state/current_job.json`: Stone's actual staff-hiring, budget and play-calling authority.
- `library/2014_coaching_hiring_and_anti_tampering_rules.md` and `career/2015/Calendar.md`: applicable 2014/2015 rights, playoff interview windows and source limits.
- `docs/rebuild_plan.md`, `docs/season_cycle_milestones.md`, `foundation/decision_rules.md`, `docs/football_event_inserts_v2_separate_outputs/Implementation_Spec.md`: phase routing, standing instructions and independent outputs.

**Contemporaneous external research, used only for procedure and authenticity (not to import actual future branch hires):** [NFL 2015 dates](https://www.jaguars.com/news/2015-nfl-important-dates-14709246); [PFT on assistant interview rights, Jan. 21, 2015](https://www.nbcsports.com/nfl/profootballtalk/rumor-mill/news/fair-or-not-plenty-of-teams-prevent-assistants-from-leaving); [Sean Payton on staff structure, Feb. 19, 2015](https://www.neworleanssaints.com/news/saints-coach-sean-payton-talks-about-coaching-changes-combine-and-mark--14943593); [NFL on Jason Garrett's staff hiring, Feb. 8, 2013](https://www.nfl.com/news/jerry-jones-has-faith-in-dallas-cowboys-jason-garrett-0ap1000000137267); [NFL no coordinator Rooney Rule, Mar. 2013](https://www.nfl.com/news/rooney-rule-will-not-be-extended-to-coordinators-0ap1000000152292); [NFL 2020 rule-change contrast](https://www.nfl.com/_amp/nfl-announces-new-policies-designed-to-increase-diversity).
