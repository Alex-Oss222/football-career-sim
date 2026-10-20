# Coaching vacancy and assistant hiring: implementation and realism specification

**Status:** Uploaded by the user on October 20, 2026 and adopted; built in step 6 of the [rebuild plan](rebuild_plan.md). Corrected the same day after a process check, with the user's rulings of October 20, 2026 and the defaults this design states as its own rules (sections 3 to 7). The templates are in [foundation/templates/staff_vacancy/](../foundation/templates/staff_vacancy/) and the worked example is [docs/examples/staff_vacancy_2014_westhoff_precedent.md](examples/staff_vacancy_2014_westhoff_precedent.md). No question in this design awaits the user. It relies on the two that do: how the club decides Stone's 2014 employment ([season end design](season_end.md#how-the-club-decides-awaiting-the-users-decision)), which settles who holds staff authority, and when the nine 2014 assistant contracts end ([January staff design](january_staff_review.md), section B, item 5), which settles when a lapse can open a vacancy.

As uploaded: **Status:** Proposed design, not installed. Does not authorize a 2014 or 2015 personnel action. Applies whenever the *currently employed and authorized* head coach must fill a real NFL assistant/coordinator position; all dates and permissions follow the actual season being simulated. Preserve existing closed career history.

## Coaching vacancy / assistant hiring, three-page templates

**Design:** Candidate Report → My Hire → Staff Hire. An actual vacancy appears first as a conspicuous insert in whichever briefing is active. If your hiring input is required, this vacancy gets its own full Candidate Report, a fill-in My Hire page, and a search outcome/index. Each concluded event of one of the fixed kinds in section 5 (employment check, permission, contact, interview, offer, appointment, search closed) keeps its own independent dated result page. The weekly/phase report merely links these records.

**Status:** Research/design only. No changes to the football-career-sim repository or current staff. No future Jacksonville 2015 hiring result is assumed or created. Historic 2014 Lowry/Westhoff sequence is used as a **closed example only**.

### Files

| File | Who uses it | What it contains |
|---|---|---|
| [`candidate_report_template.md`](../foundation/templates/staff_vacancy/candidate_report_template.md) | David Caldwell brings it, with the affected unit's coordinator as adviser | Vacancy, real duties, candidates with employer/permission/interest status, evidence, sourced reference figures only, advice, and precise question for Stone |
| [`my_hire_template.md`](../foundation/templates/staff_vacancy/my_hire_template.md) | Stone fills it | Interim coverage, outreach order, interview direction, post-interview choice, explicit negotiating limits (his own opening and ceiling), fallbacks |
| [`staff_hire_template.md`](../foundation/templates/staff_vacancy/staff_hire_template.md) | Club creates it after actual events | Search status and index of individual dated results, with executed appointment terms only if a hire closes |
| [`search_event_result_template.md`](../foundation/templates/staff_vacancy/search_event_result_template.md) | Club creates one per concluded event of a fixed kind (section 5) | A form of the shared [event result](../foundation/templates/event_inserts/event_result_template.md), with its event-record line, on its in-career date |
| [`staff_vacancy_2014_westhoff_precedent.md`](examples/staff_vacancy_2014_westhoff_precedent.md) | Example and testing | Real 2014 special-teams search without retroactive changes; no invented next-cycle candidate |
| This document | Developer/runner | Applicable 2014 and 2015 NFL rights, contracts, state transitions, data-owner routing and 39 regression tests |

### When to use

Use for a confirmed departure, actual open assistant job, authorized new coaching position or a conditional vacancy after its condition becomes true. January is common, but a real vacancy may also occur during the playing season. If the assistant's deal is merely approaching expiry, handle the retention question in the Staff Status Report first ([January staff review](january_staff_review.md)). Do not open a hiring search from a rumor, from an unverified coach contract lapse, or because the system thinks the staff could use a stronger name.

### Rules that survive every change

- A shortlist is not a permission grant, an interview, an offer or a hire.
- Stone hires his assistants and sets their terms within the promised staff budget (Document 3 rows 2 and 6); Caldwell confirms the funding; the candidate controls acceptance.
- Being a familiar former head coach does not prove he will accept, teach well, improve a unit or want a lesser title.
- A new title does not shift the calls Stone holds. Calls Stone held only as interim cover for the vacated job pass to the new coach on his effective date unless My Hire says otherwise; calls he held before the vacancy stay with him (section 4).
- A declined candidate does not disappear from history. The record has a dated outcome, while the vacancy may remain open.
- One event, one independent output at the time it is resolved. `Staff_Hire.md` summarizes and links, never replaces them.
- No real coaching change after the divergence is imported as an outcome in this divergent 2013-onward Jacksonville career. A real appointment from the 2014 league year on never closes a candidate's window or sets his employment (section 3).

## 1. Architecture and boundaries

There are three coach-facing pages **per genuine search**, named by the decision registry (`runtime/decisions.py`, `file_name`):

1. `Candidate_Report.md`: the dated, staff-produced football and eligibility brief for this *specific vacancy*. Issued only once a real vacancy/search exists; that first issue is its one scheduled issue. A new dated edition is issued only under the one reissue rule that governs every brief ([event inserts](event_inserts.md), section A, item 6): when (a) a new event needs an answer from Stone, (b) a dated finding materially changes a choice still pending, or (c) an answer falls due before the next scheduled issue. Every issued copy and its issue record are kept. It is not a universal staff directory.
2. `My_Hire.md`: Stone's fixed-heading, fill-in directions. He fills it in place, or uploads a .md or .txt file with the same headings. An answer given in chat is first written onto `My_Hire.md` (or saved as the uploaded page with the same headings), dated on Submitted, and checked before any stage runs; the page stays the record. The bracketed choices are examples, not a closed menu: any other lawful instruction is accepted ([Document 1](../foundation/01_Project_Instructions.md), the coach's alternatives; [decision rules](../foundation/decision_rules.md), section 2). The stage and its source brief are recorded and immutable after application. A later direction is an explicit, dated amendment, not a retroactive overwrite.
3. `Staff_Hire.md`: the search result and event index. Lists the actual search sequence and whether the job is filled, still open, or lawfully closed without a hire; does not combine the individual candidate/permission/offer/hiring outputs.

**Separate completed event records:** Each concluded event of a kind fixed in section 5 receives its own dated readable result, using [`search_event_result_template.md`](../foundation/templates/staff_vacancy/search_event_result_template.md), a form of the shared event result. The page carries its event-record line on a line of its own, with `"season"` set to the league year of the folder the search is filed in, so that year's Record.md lists it, an event dated December 29 to 31 included. One appointment does not erase the unsuccessful contacts. The active week's or phase's index links each independent result when it closes, even if the search itself continues.

The shared event-insert design ([docs/event_inserts.md](event_inserts.md)) controls the announcement: when the vacancy opens, the current Game Week Briefing, Bye Week Review, Season Review Briefing or other active phase brief (the desk when none is active) gets a prominent `ACTION REQUIRED` item if Stone must decide, and a `FOR YOUR INFORMATION` item otherwise. It links to the Candidate Report; it does not start a redundant vacancy-specific one-page briefing. A search can occur outside January. After Stone leaves the club, his private staffing access and signing authority cease (section 7).

The **January Staff Status Report** remains a different workflow: it evaluates incumbents and contracts. It may *cause* a vacancy, but a proposed nonrenewal is not a vacancy until effective. Its completed individual retention/departure records link to this search when one becomes necessary. A simultaneous three-position staff overhaul means three distinguishable vacancies with three candidate searches, not one giant candidate tournament.

## 2. The authoritative football distinctions

| Concept | What it establishes | What it does **not** establish |
|---|---|---|
| A coach's contract reaches its final season | A renewal decision and an expiry issue to verify | Contract already expired, coach already gone, new vacancy |
| Stone chooses a candidate to approach | Stone's authorized priority and the search's next permitted action | Candidate is available, interested, interviewed or hired |
| Employer grants interview permission | This particular legal interview is authorized | Candidate will attend or agree to join |
| Candidate agrees to interview | Candidate is willing to meet under the approved conditions | Candidate will accept a job |
| Interview is held | Actual recorded conversation/notes may inform Stone | Applicant demonstrated mastery of an unrecorded drill, or Stone made a hiring promise |
| Stone authorizes a contract proposal | Club may propose *bounded terms* after Caldwell confirms the funding (section 3) | Money has been accepted, the salary is in payroll, or candidate joins staff |
| Candidate verbally accepts terms | Subject to the actual league/contract status and executed agreement | All old employer rights, guarantees or effective dates can be ignored |
| Coach's appointment becomes effective | Job and accepted terms change on the authorized date | Position group performance, player ratings or game outcomes automatically improve |

`Stone wants` and `candidate agrees` are always separate fields and independent events. The answer cannot be drawn by copying a name or ranking from the coach's own document. The simulator never gives Jacksonville an acceptance bonus because the user is the protagonist: every draw in a search reads only the coach's employment status, the job and the calendar, so the same method gives any club the same probabilities (the label-swap test).

## 3. 2014/2015 NFL legal and market rails

- **Tier rules:** For the 2014 and 2015 staff-hiring periods, league anti-tampering rules recognized only two tiers, head coach and assistant coach; coordinator and position coach were both assistant titles. The only protected move was to head coach. Any other request, including position coach to coordinator, could be refused while the coach was under contract, including in January 2015. The May 19, 2020 protection for coordinator interviews cannot be applied backward. Sources: the [hiring-rules library](../library/2014_coaching_hiring_and_anti_tampering_rules.md), rules T1 to T4, which cite ProFootballTalk of January 21, 2015 (its source E10) for the procedural rule only, and [NFL's May 19, 2020 policy change](https://www.nfl.com/_amp/nfl-announces-new-policies-designed-to-increase-diversity).
- **How other clubs answer Jacksonville, a method rule.** This is the design's stated method, not a league rule, and it is what the 2014 search did (its method's steps 2 and 4). Every other club answers Jacksonville's request for one of its assistants by the same symmetric rule: a real step up the staff ladder (assistant to position coach, position coach to coordinator, any assistant to head coach) is granted; a move to the same title, or a nominal title at the same level, is lateral and refused. Jacksonville answers other clubs' requests for its own assistants by the same rule, except that a request for a different position at the same level goes to Stone as a staff-permission item ([January staff design](january_staff_review.md), section C). A request for a different position at the same level is not settled by the rule; the search's frozen method states its answer before any such request is made. No refusal rate is invented, and every club answers alike.
- **Head-coaching interview windows are not general assistant-hire windows.** The [2015 calendar](../career/2015/Calendar.md) (source A, the Jaguars' 2015 NFL important dates of January 1, 2015) gives the special January windows for assistants being interviewed for **head coach** vacancies while their current clubs are in the playoffs; the library's rule W10 limits them to head-coach jobs. Do not use those windows to interview a live playoff club's position coach for Jacksonville's coordinator job.
- **Existing employer/rights:** Availability and employment come from Jacksonville's own records and from the search's own method, frozen before its draws. A candidate's employment starts from his last verified job before the divergence, which for other clubs' staffs runs through the January-February 2013 hiring cycle, as the 2014 search and the [2013 coordinator turnover record](../career/2014/Early_Offseason/staff_changes/2013_retained_club_coordinator_turnover.md) treat it. Whether he was kept since then is drawn from a labelled rate from a cycle before the divergence (library section 7, the January 2013 cycle) or from a labelled modelling choice. No real 2014-cycle or 2015-cycle staff news is read: a real coaching appointment from the 2014 league year on never closes a window and never sets a candidate's status (AGENTS.md, historical league rails rule 2; Document 2 §4.5). The 2014 April draw took its rate from a January 2014 report of Oakland's real retention decisions; a later search does not copy that kind of source. Check whether the employer can legally grant or refuse the requested kind of move. A candidate with no known rights status is not 'unattached'; unattached and retired coaches follow library rules E1, E2 and E5.
- **Candidate origin:** Free agent, out-of-work coach, currently employed coach, retired coach, current Jacksonville assistant and college coach have distinct restrictions and willingness. Retired does not equal interested. Whether a college contract carries a buyout or a permission restriction is **unverified**: no library entry covers college coaches' contracts, so the Candidate Report shows it as an open check, never as a rule, until a two-pass library note covers it. Incomplete evidence is a reason to investigate, not a reason to force availability.
- **Rooney Rule and 2014 era:** The NFL announced in March 2013 that the Rooney Rule would *not* be extended to coordinator vacancies, and it did not cover position coaches in January 2015 (library R3 and R4). Do not install the 2020 coordinator or 2022 quarterbacks-coach requirements in this time frame. Applicable senior head-coach/GM hiring rules remain in their distinct workflows. [NFL 2013 announcement](https://www.nfl.com/news/rooney-rule-will-not-be-extended-to-coordinators-0ap1000000152292); [NFL May 2022 change](https://www.nfl.com/news/nfl-owners-approve-rooney-rule-applying-to-vacant-qb-coach-positions), cited only as a later rule not to apply.
- **Rules still unverified for a later search:** the in-season contact bar (library W1) is confirmed for the 2013-14 text only; the lateral bar from the opening of the employer's training camp (W1a) and the employer's exclusive rights through the second Tuesday after its last game (E4) are Unverified. A check that relies on one of them says so on the Candidate Report. The rebuild plan allows no new research in a build step except a season's historical dates, so the build adds no entry for them, and the Unverified label stays on every check that relies on either.
- **Dates:** Use the actual 2015 season calendar and date of a verified vacancy. A January search may continue into February or later when interviews, contracts, availability or playoff restrictions require it. No hiring deadline is invented. The 2014 regular season ends December 28, 2014 and the league's futures-contract signing period opens December 29 ([2014 calendar](../career/2014/Calendar.md)); who leaves a staff, and when, is this career's own event, never the real-world list. The 2015 Jacksonville offseason program begins April 20 under the [2015 calendar](../career/2015/Calendar.md), but this is a preparation target, not an automatic guaranteed hiring date.
- **Pay:** Assistant compensation is an organization expense, not player salary cap. Current scheduled payroll is not remaining budget. Proposed salaries are negotiable and require actual authority and agent/candidate response. Pay-outs on an existing guaranteed coach can overlap new staff salary. Validate guarantees, offsets, contract effective periods and actual club approval; never invent unverified annual values. The Candidate Report shows only sourced reference figures, the vacated coach's salary and the scheduled assistant payroll, neither of which is a ceiling; Stone writes any opening and ceiling on My Hire. If he asks Caldwell for costed terms instead, they come from a method frozen before the window: dated comparable contracts signed before the brief's cutoff, labelled as a reconstruction with its calculation. With no sourced comparable, no figure is offered and the stage returns to Stone.
- **Funding without a budget figure:** the promised staff budget has no number (Document 3 §3.1 and row 6). This design's rule: an offer for the vacated job at no more than the departed coach's salary, on the common terms, is within the promise; Caldwell confirms it before the offer. Anything above returns to Caldwell as his decision, resolved by the search's frozen method and never assumed. No ceiling is invented. The rule is narrower than the reading Jacksonville stated in 2014, which it does not restate: the 2014 special teams search's own method read a like-for-like replacement anywhere up to the plan's ceilings as within the promise, and under it Caldwell confirmed Westhoff's $750,000 against Lowry's $625,000. Under this design's rule that $750,000 would have been Caldwell's separate decision.

## 4. Football sourcing and candidate evaluation

Use only the candidate's verified prior work as known at the current in-career date and the club's properly acquired observations. These establish *experience*, not guaranteed effectiveness or an engine skill score.

For position coaches, test the real unit task: protections, route depth and quarterback footwork, front/run-fit communication, defensive-back pattern-match rules, punt protection, ball security, or player-teaching correction and recheck as suited to the role. A coach who has never performed the job may still be considered; present the training/operational risk and what Stone would need to verify. A prior unit's total yards or sacks is not a causal measurement of one assistant.

For coordinators, ask who prepares the installation, who controls weekly packages, how position coaches communicate, and who makes live game-day calls. Current staff, from the coach records and the job record's delegation (shown on the [Staff page](../career/2014/Team_Operations/Staff/README.md)): Stone calls the offense (since the 2013 season) and the defense (since September 28, 2014); Tice and Crennel prepare their sides, and Crennel sends in the defensive call; Westhoff prepares and calls special teams. New assistants do **not** receive Stone's calls.

- **When a play-caller leaves,** Stone takes interim direction of that phase automatically from the departure, as on January 12, 2014. Nothing stops the clock. An `ACTION REQUIRED` insert asks only who covers the departed coach's teaching duties, which hold no game.
- **On a hire,** calls Stone held only as interim cover for the vacated job pass to the new coach on his effective date unless My Hire says otherwise, as the special teams calls passed to Westhoff on February 11, 2014. Calls Stone held before the vacancy stay with him until he changes them.
- Any other change of delegation is separately authored by Stone and entered in the job record's delegation. A 'new scheme' needs actual installed plays and subsequent lawful work, not a title line.

Interview evidence is real only when the interview occurs. Create football questions beforehand, then record actual supplied answers or a properly labelled summary of completed discussion. Never fabricate transcripts, performance tests, personal relationships, secret conversations or promises. No fixed candidate count, score grade, perfect pros/cons symmetry or mandatory consensus.

## 5. State machine and safe execution order

A search has a vacancy state and multiple event histories. Each candidate has an independent status. Do not collapse a failed candidate into a filled vacancy or fill a vacancy solely because an earlier candidate accepted an invitation.

**Vacancy:** `UNCONFIRMED` → `CONFIRMED_OPEN` (or dated `OPENING_SCHEDULED`) → `SEARCH_ACTIVE` → `FILLED` / `CLOSED_WITHOUT_HIRE` / `STILL_OPEN`. A planned additional job requires explicit authorization first. `FILLED` requires an accepted and properly executed appointment whose effective date has arrived. No silent `FILLED` fallback.

**Candidate:** `IDENTIFIED` → `RIGHTS_CHECKED` → `PERMISSION_REQUESTED` (if applicable) → `CONTACTED` → `INTERVIEW_OFFERED` → `INTERVIEW_HELD` → `TERMS_AUTHORIZED` → `OFFER_SENT` → `COUNTER_PENDING` / `ACCEPTED` / `DECLINED` / `WITHDRAWN`; the accepted offer then needs a separately verified contract/appointment-effective event. These are illustrative possible stages, not a requirement every candidate pass through each. No employer permission is required of a genuinely free coach; a permission refusal ends that candidate's current request until a new lawful situation exists.

**Concluded events and their result pages.** The list is closed: each kind below gets one result page, in the search's `outcomes/` folder (section 6), named `<Kind>_Result_<YYYY-MM-DD>_<First_Last>.md`.

| Kind | Concluded when | File name |
|---|---|---|
| Employment check | The search's method settles an unknown employment fact about a candidate (kept, released, retired, free) | `Employment_Check_Result_<date>_<candidate>.md` |
| Permission | The employer club grants or refuses Jacksonville's request | `Permission_Result_<date>_<candidate>.md` |
| Contact | The candidate agrees or declines to talk or to interview | `Contact_Result_<date>_<candidate>.md` |
| Interview | The interview is held (recorded notes only) or is cancelled | `Interview_Result_<date>_<candidate>.md` |
| Offer | An offer closes without a hire: declined, withdrawn, lapsed, or a counter beyond Stone's limits that he does not meet | `Offer_Result_<date>_<candidate>.md` |
| Appointment | The accepted terms are signed and the appointment has its effective date | `Staff_Hire_Result_<date>_<candidate>.md` |
| Search closed | The search ends without a hire on Stone's authorized decision | `Search_Closed_Result_<date>.md` |

**Process entries** get no result page; they are recorded in the search's data record and listed on Staff Hire: a request sent and not yet answered, a contact awaiting a reply, an interview scheduled, a counter pending, Caldwell's funding confirmation (shown on the offer or appointment result it governs) and Stone's stage answers, which are his My Hire page. An offer that is accepted closes as the appointment, not as a separate offer result. The departure or new post that opened the vacancy is owned by its own record (a departure's own staff result is in `Team_Operations/Staff/`, [January staff design](january_staff_review.md)) and linked.

**The search method.** Each search runs on a season-aware method frozen before its first draw and run through the private packet, as the 2014 search was. It covers unknown employment, willingness, the other club's permission answer (the method rule in section 3), the counter and acceptance, and Caldwell's answer to any amount above the departed coach's salary. Every probability is a labelled modelling choice or a base rate from before the divergence (library section 7), and each reads only the coach's status, the job and the calendar. **Candidate acceptance keeps the 2014 structure:** willingness and a counter are drawn at labelled rates; an offer at or within his counter is accepted; an offer below it returns to Stone. No separate acceptance rate is drawn, because none is sourced (library §7.5); the willingness draw already makes declining a real outcome.

Before advancing any stage: read the controlling source, verify temporal/legal status, and check whether this stage needs Stone's choice. If it does, stop only the dependent action until his answer is on My Hire. A staff appointment is never closed by a standing instruction (the decision queue's `staff_appointment` class); Stone's stage answers on My Hire resolve his items, as answers by the user. The candidate's response and the employer club's answer are separate events owned by those parties. Only an answer due before the event it holds stops the clock: unrelated games, league news and safe administrative work continue. Search business that does not hold Jacksonville's game never holds the week's slate, and in a bye week the other clubs' games close. An in-season search holds a week's game package or close only when a search answer is due before a Jacksonville game input that depends on it; then the whole slate is held until the user rules whether the other clubs' games may close while Jacksonville's own pre-kickoff answer is open ([event inserts](event_inserts.md), section C). User silence never means go, decline or approve a salary increase. A reply authorizes only the stages it names, with their limits: interview is not offer and offer is not hired unless his page says so. A new contract type, extra years, salary above the approved negotiating ceiling, expanded role, guarantee or different candidate must return to Stone.

Close each *concluded* event in its own result page immediately. Keep an ongoing process record for still-open conversations. A new dated Candidate Report follows the one reissue rule (section 1): an informational change that affects no pending answer waits for the next scheduled issue; since the Candidate Report has no later one, it appears only in an edition issued for another reason. Its result page is readable as soon as it is written, and Staff Hire links it at once. Keep every prior issued report.

## 6. Owners, file placement and indexes

Every search lives under the season's Early_Offseason staff owner, whatever its date, as the folder map already places staff records: the logical record `offseason/staff_changes` (`runtime/seasons.SeasonPaths`), which is `career/YEAR/Early_Offseason/staff_changes/`, with one folder per vacancy. **Working example for the January 2015 hiring period**, once that in-world period exists and the season handoff/active folder map permits it:

```
career/2015/Early_Offseason/staff_changes/<vacancy-key>/
  Candidate_Report.md
  My_Hire.md
  Staff_Hire.md
  outcomes/
    Employment_Check_Result_<YYYY-MM-DD>_<candidate>.md
    Permission_Result_<YYYY-MM-DD>_<candidate>.md
    Contact_Result_<YYYY-MM-DD>_<candidate>.md
    Interview_Result_<YYYY-MM-DD>_<candidate>.md
    Offer_Result_<YYYY-MM-DD>_<candidate>.md
    Staff_Hire_Result_<YYYY-MM-DD>_<candidate>.md
    Search_Closed_Result_<YYYY-MM-DD>.md
```

The search's stored record sits beside it in the data area, at `data/YEAR/Early_Offseason/staff_changes/<vacancy-key>/`: the vacancy state, interim coverage, each candidate's dated stage history, the staff's authored texts with author and date, each Candidate Report's issue record (date, file, sha256, as `briefings.json` does for game weeks), the frozen method and its results, and My Hire's applied stage answers kept unchanged, with amendments appended.

A vacancy that opens during the season uses the same owner; the game-week or bye-week folder carries only *links*. The canonical folder resolver, not ad hoc literal paths, chooses the actual owner. Do not generate new 2015 early-offseason files during the October 2014 career date simply to satisfy this sample; the January 2015 searches open only once 2015 is staged (rebuild step 6). The January 2015 transition may overlap the 2014 Season Review; a dated staff event must be recorded once and linked between the two, never stored as competing versions of the same hire. A search never appends to the 2014 `hires.md` or `timeline.md`, closed pages that the page-history prefix rule would otherwise let grow; from Week 6 every Jacksonville search writes its own pages under its search folder.

The precise source of truth for an *appointment* is the dated completed appointment result and the coach's permanent record. If a pre-existing standalone appointment file is already the canonical output, reuse it and have Staff Hire link it, rather than generate a second competing file. For a concluded permission rejection or unsuccessful offer, create its own dated result under the same search owner.

`runtime/decisions.py` already declares `staff_vacancy` as Candidate Report → My Hire → Staff Hire in Early_Offseason but does not implement that workflow. `runtime/decision_queue.py` has a staff appointment class but currently lacks a stage-complete, event-scoped vacancy transition system. The build adds what the table below lists, and integrates the shared event-insert renderer of [docs/event_inserts.md](event_inserts.md).

On accepted appointment, atomically update:

- **Coach record** (`data/people/coaches/<slug>.json`): `hired`, `contract_signed` with the executed terms and, where calls move, `calling_changed`, as in Mike Westhoff's record. A new coach's record carries only sourced history from before the divergence, and his profile is added to the [staff profiles](../career/Assistant_Coaches/staff_profiles.md).
- **Job record** (`state/current_job.json`): the delegation for any call or preparation that moves, and the decision-queue item resolved by Stone's My Hire answer, plus separate items for changes he did not authorize.
- **Built views, rebuilt from those records and never written by hand:** the Staff page and Coach page (`scripts/render_coach_pages.py`) and the coaching payroll (`scripts/render_jaguars_cap_tracker.py`); never the player cap.
- **Rulebook and state views:** Document 3 §6.1 incumbent rows and, when a coordinator or a call changes, its §11.3 index entry and §11.4 audit trigger (the Westhoff precedent is Entries 77 and 84); Documents 4 and 5.
- **Event/annual index:** the result page's event-record line, so Record.md lists the dated event once; the Staff Hire index and current season/phase desk link to all individual concluded results.
- **Dependent views/season handoff:** 2014 season review and 2015 carry-forward stay coherent, with opening-season readiness checked rather than assumed.

Never write a change to already-closed 2013 or early-2014 search results to make the new format look consistent. Historical episodes remain references.

**What the build adds (step 6; this design builds none of it):**

| Item | Where |
|---|---|
| A vacancy key for the registry's folder (two vacancies in one season would otherwise write the same three file names), a logical season record for staff searches and the repository-map entries the folder-map test needs | `runtime/decisions.py`, `runtime/seasons.py`, `runtime/season_layout.py`, `docs/repository_map.json` |
| A decision-queue event kind for search stages (for example `staff_search_stage`, keyed by season, vacancy and stage), so a `staff_appointment` item holds the next stage; one item per Stone stage, with its deadline and `can_continue` | `runtime/decision_queue.py`, [career layer](career_layer.md) sections 3 and 4 |
| Page builders: Candidate Report issue and reissue keeping earlier copies; a blank My Hire, its check (accepts free-text alternatives; verifies the candidate, his rights, the role and the terms) and its apply, including a chat answer once written onto the page; the Staff Hire index; one result page per concluded event | `scripts/` |
| A season-aware search method, frozen before any draw, replacing the one-off 2014 script | `scripts/` (replacing `scripts/st_coordinator_search.py`) and the search's data folder |
| Coach-record schema: a departure without a destination (expiry, dismissal, resignation, retirement); the Staff page's open jobs read the vacancy record | `runtime/coaches.py`, `scripts/render_coach_pages.py` |
| An insert trigger row for Jacksonville's own vacancy, routed to the active brief or the desk | [docs/event_inserts.md](event_inserts.md) sections B and E |
| Workflow and runner text: one result page per event and the search owner; the decisions table and the rulebook lines awaiting approval (Document 3 §10.2); the staff task; the template catalog row; the milestones | `docs/update_workflow.md`, `docs/rebuild_plan.md`, `AGENTS.md`, `foundation/templates/README.md`, `docs/season_cycle_milestones.md` |

## 7. Failure and exception rules

| Situation | Required behavior |
|---|---|
| No legal vacancy | No search files, no candidate offer and no fictional interim appointment |
| Expiring contract but no verified exact date | Mark deadline unresolved; verify employer rights before calling the job vacant. For the nine 2014 assistant contracts the end date awaits the user's decision (January staff design, section B, item 5) |
| Incumbent might be renewed | Keep incumbent and possible opening as distinct states until resolution |
| Coach leaves for head-coach job | Record departure on actual date, then open vacancy and inform Stone if he still employs staff |
| Departed coach called a phase | Stone takes interim direction automatically from the departure; no clock stop; the insert asks only who covers the teaching duties |
| Internal assistant promoted | Record role change only with Stone's authorization; open resulting backfill separately if necessary |
| Several vacancies | Each vacancy owns its folder, search and Staff Hire, and each concluded event gets one result |
| All candidates decline or employers refuse | Keep role open or use authorized interim coverage; return for a new pool, do not invent an easy hire |
| Candidate offers changed duties | Recheck real authority and other coaches' jobs, not just budget |
| Candidate asks for more pay/guarantee | Accept only within Stone's explicit terms after Caldwell confirms the funding; otherwise return to Stone |
| Jacksonville still in playoffs | Use the applicable recruiting-contact/permission restrictions; no universal January 1 hire |
| Stone dismissed | His staff-selection power ends immediately; route him to his career/agent notice. Caldwell answers for Jacksonville on items still open; no offer goes out on Stone's authority; the vacancy, like a pending renewal, stays open for the successor |
| Salary budget not quantified | Do not infer a ceiling from total current payroll. An offer at no more than the departed coach's salary on the common terms is within the promise once Caldwell confirms it; anything above is Caldwell's decision (section 3) |
| Assistant hired | No automatic unit wins, player development, skill improvement or new scheme installation |
| Search reviewed after outcome | Preserve all previous dated issue versions and refusals, not hindsight-updated candidate preferences |

## 8. Adversarial tests required before merge

1. No actual vacancy: all three search pages absent; no selection question.
2. Planned expiring deal: candidate search does not open until vacancy/departure confirmed.
3. Legitimate opening after a departure midweek: the current brief gets an insert under the one reissue rule without writing a new game result.
4. Vacancy already known: repeated render does not create duplicates or advance time.
5. Departed coach called a phase: Stone takes interim direction from the departure date with no clock stop, recorded in the job record's delegation; 'interim Stone' is not invented for teaching duties or unrelated jobs.
6. No interim lead for teaching duties: those duties remain uncovered and the insert asks Stone who covers them; no silent responsibility handoff, and no game is held for it.
7. Candidate listed but rights unknown: no legal contact yet; name and open check returned.
8. January 2015 position coach to coordinator: the league rule lets an under-contract employer refuse and the protected-2020 rule is not applied; under the design's method rule another club grants the step up and refuses a same-title move, alike for every club.
9. Head-coach interview window not misused to recruit another club's playoff assistant for Jacksonville's lateral coordinator job.
10. Unemployed candidate with established freedom: no fake employer permission; actual willingness still required.
11. Retired coach: check willingness and surviving rights; no automatic return.
12. Candidate approached on approved instruction: can decline to talk or interview even when first on Stone's list (willingness drawn at a labelled rate); an offer below his counter returns to Stone; an offer at or within it is accepted.
13. Opponent coach actual future employment after branch divergence does not become a predetermined branch result.
14. Interview not held: no fabricated meeting, quote, test result or evaluation improvement.
15. Interview held without detailed notes: report only fact held and next decision; no made-up dialogue.
16. User selects hire before budget and acceptance: pending offer, not executed contract.
17. Offer at or within the candidate's counter and within Stone's ceiling, with funding confirmed: accepted; the appointment closes only when the terms are signed and effective.
18. Counter exceeds bound or changes guarantees: user-required stop before further commitment.
19. Assistant's old guaranteed money survives release under the actual contract; financial totals reconcile.
20. Offer rejected: separate dated Offer Result, vacancy still open; no hire created.
21. Two refused contacts and one accepted coach: three distinct results with dates and one appointment, not one blended search result.
22. One completed interview and later declined offer: distinct stage outcomes if each had a concluded event, no duplicate permanent owner.
23. Two simultaneous vacancies: independent decisions and files, no cross-filling same coach in contradictory roles.
24. Internal promotion moves duty lawfully, opens any secondary vacancy separately and updates reporting lines only from authorized instruction.
25. New defensive coordinator hired while Stone calls defense: Stone remains caller unless separately changed.
26. Stone terminated before staff offer: authorization revoked; no Jacksonville confidential brief or binding offer on Stone's authority afterward; Caldwell answers for Jacksonville on open items, and the vacancy stays open for the successor.
27. Search closes without hire on explicit authorized decision: records uncovered work, not fake staff hire; no 'filled' state.
28. Accepted hire writes the coach record and, where calls move, the job record's delegation; the Staff page, Coach page and coaching payroll are rebuilt from them, and the season handoff and annual record agree on the effective date.
29. No statistical 'coaching improvement bonus' is applied merely from new coach name or a persuasive My Hire paragraph.
30. Candidate reports frozen at issuance: a post-interview reissue does not rewrite the previous statement about availability and interests.
31. The full user-facing Staff Hire page links every separate closed event, and events concluded during a game week appear independently in that week's index before Sunday when feasible.
32. Rebuild and validation produce unchanged output after a second run with no new events and reject alterations to the closed 2014 Westhoff/Lowry history.
33. Another club's assistant is not contacted during his club's season, postseason included (library W1, labelled as confirmed for the 2013-14 text).
34. Label swap on every search draw: relabelling which club is hiring changes no probability and no outcome.
35. My Hire accepts a lawful instruction that is not listed in its brackets.
36. An answer given in chat is checked only after it is written onto My Hire; no stage runs on the chat text alone.
37. A search never appends to the 2014 `hires.md` or `timeline.md`, even though the page-history prefix rule would allow it.
38. A standing instruction never closes a staff appointment item; Stone's My Hire answer does.
39. Each result page carries its event-record line on a line of its own, with the `season` of the folder its search is filed in, passes the clean-page check and appears in that year's Record.md.

## 9. Research basis

**Repository-owned source of actual career facts:**

- The 2013 [staff plan](../career/2013/offseason/staff_building/staff_plan.md) and [hires](../career/2013/offseason/staff_building/hires.md): user-selected candidate order, success/refusal/market obstacles, accepted contracts.
- The 2014 [staff plan](../career/2014/Early_Offseason/staff_changes/staff_plan.md) and [hires](../career/2014/Early_Offseason/staff_changes/hires.md): the Lowry vacancy, the April employment draw and permission refusal, Westhoff's interview, offer, counter and appointment.
- [`st_search_method.json`](../data/2014/Early_Offseason/staff_changes/st_search_method.json) and [`st_search_results.json`](../data/2014/Early_Offseason/staff_changes/st_search_results.json): previously frozen private-resolution method and closed dated outcome. Preserve those events, not their method's context as an automatic future rule.
- The coach records in `data/people/coaches/` and the authority, delegation and standing instructions in `state/current_job.json`: current jobs, contracts, calls and Stone's staff-hiring and budget authority. The [Staff page](../career/2014/Team_Operations/Staff/README.md) and the [coaching payroll](../career/finances/coaching_and_organization/coaching_payroll.md) are their built views, never the source.
- The [hiring-rules library](../library/2014_coaching_hiring_and_anti_tampering_rules.md) and the [2015 calendar](../career/2015/Calendar.md): applicable 2014/2015 rights, playoff interview windows and source limits.
- [Rebuild plan](rebuild_plan.md), [season cycle milestones](season_cycle_milestones.md), [decision rules](../foundation/decision_rules.md), [event inserts](event_inserts.md): phase routing, standing instructions and independent outputs.

**Contemporaneous external research, used only for procedure and authenticity (not to import actual future hires):** [NFL.com, Kareem Copeland, on Jason Garrett's staff changes, February 2013 (day not shown)](https://www.nfl.com/news/jerry-jones-has-faith-in-dallas-cowboys-jason-garrett-0ap1000000137267); [NFL, no coordinator Rooney Rule, March 2013](https://www.nfl.com/news/rooney-rule-will-not-be-extended-to-coordinators-0ap1000000152292); [NFL 2020 rule-change contrast](https://www.nfl.com/_amp/nfl-announces-new-policies-designed-to-increase-diversity). The 2015 dates are cited through the 2015 calendar (source A) and the January 2015 tier rule through the library (source E10, procedure only). The upload's citation of Sean Payton's staff-structure transcript of February 19, 2015 is removed: it reports real 2015 staff changes and a real 2014 season result, and it carries no procedural rule the library lacks.
