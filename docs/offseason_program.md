# April Offseason Program: implementation and validation specification

**Status:** Uploaded by the user on October 20, 2026 and adopted; built in step 7 of the [rebuild plan](rebuild_plan.md). The templates are in [foundation/templates/offseason_program/](../foundation/templates/offseason_program/), the worked example is [docs/examples/offseason_program_jacksonville.md](examples/offseason_program_jacksonville.md) and the research register and repository assessment are in [docs/offseason_program_research.md](offseason_program_research.md).

As uploaded: **Status:** Design and acceptance contract only. No implementation has been committed or tested against a working local checkout. No program is opened, run or closed by this package.  
**Inspected repository:** `Alex-Oss222/football-career-sim`, `main`, 20 October 2026.  
**Career data at inspection:** 2014 Week 5 closed on 5 October 2014; the Week 6 plan remains open.  
**Primary governing documents:** `docs/rebuild_plan.md`, `docs/season_structure.md`, `docs/event_inserts.md`, `foundation/01_Project_Instructions.md`, `foundation/02_League_Era_and_Sourcebook.md`, `foundation/03_Head_Coach_Organization_and_Authority_Canon.md`, `foundation/06_Event_Records_and_Handoff.md`, and `AGENTS.md`.

## April Offseason Program: research and three-page design package

**Scope:** The first of six remaining head-coach career workflows. Research and proposed templates only, prepared 20 October 2026. No GitHub commit, change to the career's state, 2015 season activation or result-generation is authorized by these materials.

**Repository inspected read-only:** [`Alex-Oss222/football-career-sim`](https://github.com/Alex-Oss222/football-career-sim), `main`, with active career state immediately after Jacksonville's 5 October 2014 Week 5 game. Week 6 remains the next live decision. The 2014 offseason training records are already completed historical career evidence; April 2015 remains conditional on what happens in the career.

### Start here

1. **[`offseason_program_research.md`](offseason_program_research.md#april-program-rigorous-assessment-and-implementation-blockers)**: what is genuinely proven, the rule ambiguities, current implementation gaps and what would be unacceptable to invent.
2. **[`offseason_program_research.md`](offseason_program_research.md#research-record-and-nfl-legality-findings-april-offseason-program)**: the original 2011 CBA, dated contemporary club/NFL reporting, exact 2014 and 2015 calendar, source-release limits and open rules questions.
3. **[`offseason_program_brief_template.md`](../foundation/templates/offseason_program/offseason_program_brief_template.md)**: complete staff briefing, with football evidence, roster and medical status, five-week teaching limits and real action items at the top when present.
4. **[`my_program_plan_template.md`](../foundation/templates/offseason_program/my_program_plan_template.md)**: coach-owned, naturally writable choices with the existing staff/football standing instructions preserved. It does not require a manufactured annual vote on settled matters.
5. **[`program_report_template.md`](../foundation/templates/offseason_program/program_report_template.md)**: readable account of what happened and was observed, actual limits, follow-on OTA questions and links to each individual completed event output.
6. **This document**: integration boundaries, canonical source ownership, method contracts, scheduling and evidence gates, separate result creation, and 46 specific proposed acceptance tests.
7. **[`offseason_program_jacksonville.md`](examples/offseason_program_jacksonville.md)**: historically honest presentation of the **already completed 2014** Stone offseason work through May 23, followed by a deliberately outcome-free 2015 illustrative boundary as known at the October 2014 checkpoint.
8. **[`offseason_program_result_template.md`](../foundation/templates/offseason_program/offseason_program_result_template.md)**: small supplemental example of the **standalone result that every closed consequential event must have**, including failure. It is not a fourth ordinary April workflow page and must be reused with the existing event-insert architecture, not implemented as a competing events system.

### Exact three-page contract

| Main page | Owner and purpose | Actual future repository view |
|---|---|---|
| Offseason Program Brief | Staff-issued evidence, calendar and request for Stone's lawful priorities | `career/{season}/Offseason_Training/Offseason_Program_Brief.md` |
| My Program Plan | Dated, editable Stone decision that adopts or changes his program priorities | `career/{season}/Offseason_Training/My_Program_Plan.md` |
| Program Report | Readable derived five-week review **after** actual Phase One and Two work | `career/{season}/Offseason_Training/Program_Report.md` |

The phase's actual `staff_plan.md` and `training_report.md` files still own detailed instructions and original teaching observations. The separate event owner retains one unique, dated Markdown result **per separately concluded consequential event**. No Program Report or annual record can replace those individually readable outputs.

### What this package does not do

- It does not rerun, rewrite or rename the completed 2014 Phase One or Phase Two records.
- It does not complete the 2014 season or guarantee Stone remains employed for the 2015 program.
- It does not select, sign, trade, release or medically clear any player; those powers remain where canon places them.
- It does not assume actual real-world 2015 Jaguars transactions, players, attendance, cancellations or performance occurred in the career.
- It does not claim the 2015 April briefing builder, training-evidence model or independent-event routing is implemented. All 46 tests are **proposed**, not executed.

### Six-workflow checklist, after this design deliverable

| # | Workflow | Design status | GitHub integration status |
|---|---|---|---|
| 1 | April Offseason Program | **Research, templates, example and validation contract completed in this package** | Not implemented by this package |
| 2 | NFL Draft | Next; research and three-page package still to design | Not assessed or modified here |
| 3 | May-June OTAs and Minicamp | Still to design | Not assessed or modified here |
| 4 | Training Camp Position Battles | Still to design | Not assessed or modified here |
| 5 | Every Preseason Game | Still to design | Not assessed or modified here |
| 6 | Final Roster Cuts | Still to design | Not assessed or modified here |

**Next design task:** The NFL Draft, after approving the April design. No career progression is implied by that next research step.

## 1. Workflow boundary and contract

**One decision, three public pages:**

| Registered decision | Coach-facing brief | User-owned decision page | Readable completed phase view |
|---|---|---|---|
| `offseason_program` | `Offseason_Program_Brief.md` | `My_Program_Plan.md` | `Program_Report.md` |

The registry in `runtime/decisions.py` already contains this row with the exact titles and the location `offseason_training`. It is not marked implemented. Preserve the page names; generate them through `runtime.decisions.file_name()`, `runtime.decisions.folder()` and `SeasonPaths`, not handmade dated folder strings.

In a normal 2015 Jacksonville employment scenario those three rendered pages live under `career/2015/Offseason_Training/`. The program covers **Phase One and Phase Two**: two weeks of classroom and physical preparation, followed by three weeks of legal individual and separates work. It is not the nine-week spring program's entire output. The remaining four weeks, OTAs and mandatory minicamp, belong to the later OTA workflow. The draft and rookie minicamp retain their own event owners. The word April names the decision's start, not a forced April 30 completion date.

This package does not redefine, overwrite or reconduct the actual completed `career/2014/Offseason_Training/Phase_One/` and `Phase_Two/` records. The new process begins prospectively under the Week 6 rebuild rule; 2014 records only demonstrate precedent. The next eligible Jacksonville example is the 2015 program **if Stone remains employed** when that real career date arrives. If he is not Jacksonville head coach, no private Jaguars decision packet is delivered to him. Rebind the workflow only to his actual authorized job and its calendar and authority.

## 2. Single ownership of every fact

| Fact or content | Canonical owner | Treatment by the three new pages |
|---|---|---|
| Job, contract, current authority, play calling, in-force standing instructions | `state/current_job.json` and its permanent supporting contracts | Read and summarize. Never add terms or reset a delegation. |
| Open Stone and club decisions | `state/decision_queue.json` with source owner | Brief links action; plan records the exact Stone answer; no new answer inferred. |
| Dates and first public announcement of dates | `career/{season}/Calendar.md` and dated `library/{season}_historical_calendar.md` evidence | Render only dates legitimately known by issue time. Calendar does not establish practice completion. |
| Participant roster, signings, unsigned rights and contract participation instruments | Permanent player/contract records and `Team_Operations` derived views; executed agreements where applicable | Brief uses legal status current as of issue date. Never copy prior-year participation. |
| Medical limits and clearance | Medical staff's incident and availability owner | Brief/report may quote communicated football-use status, but cannot issue or amend medical findings. |
| Actual program plan approved by Stone | `My_Program_Plan.md` as dated user choice; stored source for rendering | This is the single user-owned program decision. |
| Detailed Phase One coaching and conditioning plan | `Offseason_Training/Phase_One/staff_plan.md` | Produced from Stone's decision and coordinators' lawful scheduling; subordinate to user direction. |
| Actual Phase One teaching, observed questions, staff review | `Offseason_Training/Phase_One/training_report.md` | The actual phase report owns the evidence; Program Report links and faithfully condenses. |
| Detailed Phase Two coaching and practice plan | `Offseason_Training/Phase_Two/staff_plan.md` | Staff adapts lawfully to real Phase One findings and participant/medical changes. Material Stone changes go back to him. |
| Actual Phase Two on-air observations, staff review | `Offseason_Training/Phase_Two/training_report.md` | The actual phase report owns the evidence; Program Report links and faithfully condenses. |
| One concluded trade, contract discussion, hiring pursuit or medical/roster disposition | Existing canonical `Team_Operations/Trades`, `Team_Operations/Free_Agency`, staff, medical, career or player owner, as applicable | One separate, dated, reader-facing event result in the department of actual ownership. Program Report has a link-only entry. |
| Summary of the five-week program | `Program_Report.md` | **Built view**, not a new canonical phase assessment or substitute for a separate event result. |
| Annual dated event index | `career/{season}/Record.md`, generated by `scripts/render_annual_record.py` | One dated entry pointing to each authoritative event owner; no second narrative. |
| Teaching assignments carried into later noncontact team work | Dated phase reports, then the later `OTA_Brief.md` | Handoff question with evidence. No early OTA or future camp result. |

**Important reconciliation:** `docs/season_structure.md` says every training phase has exactly two substantive records (`staff_plan.md` and `training_report.md`). Keep that rule. `Program_Report.md` is a derived five-week executive presentation built from those two authoritative phase outputs, the program decision and individually resolved external events. It may present an accurately sourced, readable synthesis but may not introduce a fresh player judgment, unrecorded practice, unsourced medical finding or independently editable assessment. Never create a third Phase One or Phase Two assessment document.

The rebuilt system's broader one-fact-one-owner plan ultimately calls for permanent player and coach records with derived pages. Any permitted dated player-assessment update must be recorded in its permanent owner and rendered into public views, not hand-authored for the convenience of this report. Because the repository's 2014 phase reports are already completed, do not retroactively split or migrate their narration as part of this April design.

## 3. True 2014 and 2015 schedule boundaries

| Condition | 2014 historical | 2015 historical if Jacksonville retains a returning head coach |
|---|---|---|
| Start | Mon 21 Apr 2014 | Mon 20 Apr 2015 |
| Phase One | Apr 21 to May 2; record reports actual player sessions through May 1, staff review May 2 | Apr 20 to May 1; exact club sessions unproven until recorded |
| Phase Two | May 5 to May 23; record reports on-field work through May 22, staff handoff May 23 | May 4 to May 22; exact club sessions unproven until recorded |
| NFL draft | May 8 to 10 | Apr 30 to May 2 (overlaps Phase One) |
| Jaguars rookie minicamp | Actual practice days May 16 and 17, not a made-up third day | Historical announced May 8 to 10; eligibility and actual held work require their own record |
| Phase Three | Begins the week of May 26; OTAs on their historical announced dates | Begins the week of May 25; ten OTA days announced in later dated reports |
| Mandatory minicamp | Jun 17 to 19 | Jun 16 to 18 |

The **CBA eligibility** is not a team attendance report. A club that hires a new head coach after the prior regular season may start on the first Monday in April and may structure a distinct eligible program; a returning-head-coach club cannot begin before the third Monday in April. It is improper to change the 2015 Jacksonville start to Apr 6 without an actual branch coaching change and a compatible club schedule. Conversely, do not assume Stone stays in his 2013 job through the end of 2015 merely because his contract is fully guaranteed.

For a 2015 Apr 20 start, the 21-day filing limit falls **no later than Mar 30, 2015**. Article 21 section 2(c) says the schedule is furnished on the parties' agreed date, no later than 21 days before commencement. The actual mutually agreed earlier filing date, the executed Jacksonville submission, and its delivery confirmation have not been recovered. Public NFL/Jaguars reports that appeared after Apr 20 may verify history without establishing that Stone had received that published announcement on Apr 20. If a club-held schedule is supported by its genuinely recorded filing and operational communication, it can be coach-known on its stated internal date; do not manufacture that receipt from later web publication. This is a conditional program-approval gate, not a reason to silently substitute imaginary dates.

## 4. 2011 CBA legality model

Use the August 4, 2011 CBA, not a later NFL collective bargaining agreement. Relevant text: Article 21 sections 1, 2(a)-(c), 3, 5(a)-(c), 6, 8-9; Article 22 for minicamps; Appendix G. Always select actual year rules and club calendar in future seasons.

**Before the formal program:** under Article 21 section 2(a), club-supervised workouts, meetings with coaches, coach-supervised group or individual film/playbook study and directed strength sessions are prohibited. Independent personal workouts with facility access are a different matter; they are not a club program or staff evaluation. Earlier preparation by coaches is permissible; a coach's undated prepared film packet is not a delivered player packet. Do not silently assume passive playbook or film distribution was permitted before the formal start if the method was not verified.

**Phase One:** physical work limited to strength, conditioning and rehabilitation. Only full- or part-time strength/conditioning coaches with no other club coaching responsibilities may coach/participate in/observe field activity. No helmets or footballs except the agreement's narrow quarterback throwing exception (an uncovered receiver, no defending player), which is not a position-coached pass drill. Contemporaneous Chiefs/Packers accounts and the existing 2014 Jaguars source verification confirm that **football teaching in classrooms** may occur once the program begins. No punt snap/kick unit drill is assumed lawful in Phase One merely because an old Stone note proposed it. Reconcile any discrepancy to the actual CBA before execution.

**Phase Two:** coaches may conduct individual football instruction and separate offense-only, defense-only or special-teams-only perfect-play periods. No helmets, live contact, offense versus defense, offensive/defensive 1-on-1s or opposed special-teams drills. A front drawn on a card is not a live opponent. An ordinary on-air protection success cannot be graded as sound protection under rush.

**Time and voluntariness:** Article 21 section 1 and 5(a) protect choice to attend both workouts and classes. In non-OTA, non-minicamp weeks, a club may have each player at facilities at most 4 hours per day and 4 weekdays per week, with at most 90 minutes per day on the field. The club may specify no more than 2 hours per day; the player selects the remaining eligible workout time within open weight-room hours. Validate player-specific—not only team-wide—time, contact type and phase. No contact work during these phases. The minimum workout compensation and any specially signed participation agreement are paid/handled by the contract and club operations departments, not decided by Stone.

**Participation eligibility:** signed under-contract players are invited. A player with an unsigned Required Tender or certain expiring/UFA status may participate only after a valid Offseason Workout and Minicamp Participation Agreement under Article 21 sections 3 and 9; do not assume one exists. No draft choice becomes a contracted veteran merely by appearing on a draft list. Rookie entry additionally follows Article 22 and calendar/eligibility rules.

**Safety and legal records:** medical staff direct rehabilitation and clearance. Article 21 section 5(c) requires club filming of on-field sessions in all three phases and retention until 30 days after the start of the regular season; record necessary compliance material separately from a player grade. Under Article 21 section 8, the head coach and club can be held responsible for violations; a “better” football session does not justify a legal shortcut. Independent work after the program and before camp remains subject to Article 21 section 6, not a loophole for unsanctioned club practice.

## 5. Authority and retained Stone identity

Read `state/current_job.json` at the event's precise effective date and recheck his employment before each new action. The currently evidenced accepted terms are: head coach from Jan 15, 2013 on a four-year fully guaranteed agreement; retained Jan 15, 2014 without change. Actual salary and assistant-budget dollars were never filled in. Stone chooses assistants inside the approved budget, directs lawful practice and the coaching approach, sets depth and game-day roles, and retains control of game operation. The April plan does not create a new contract, an offseason retention promise or assistant expenditures beyond his delegated ceiling.

As of Oct 5, 2014, Stone calls offense and defense in games; Mike Tice prepares the offensive side; Romeo Crennel prepares and relays defensive calls; Mike Westhoff runs special teams. Stone's separate April 18, 2014 instructions put Tice in charge of a pre-approved practice when Stone is absent, Crennel next. That emergency assignment covers schedule and ordinary on-field adjustments only. It cannot change the depth chart, player role, staff employment, medical availability or Stone's installed concepts. Do not misstate the game-calling arrangement when building a 2015 brief, and do not repeat a default-caller appointment as a mandatory annual head-coach decision.

Stone's methods include specific film-supported correction and a later independent check; engaging players in questions about terminology; using known offensive families (Dagger, Mesh, play-action, screens, multiple tight ends, zone and gap runs); defensive fit and coordinated pressure; the TAKE/GIVE/ANSWER teaching format; targeted secondary roles without sacrificing primary work; and short, regular coordinator reviews. He keeps medical-limited players involved in lawful learning as clinicians allow. The exact 2014 player names and April social-event dates do not become 2015 canon. Voluntary family meals may be organized but cannot hide mandatory football work or serve as an attendance grade. The 2014 user-stated 80–90% primary-work guideline is an operating preference, not a fabricated numeric score for progress.

Caldwell alone finalizes trades, draft picks, acquisitions, player contracts, cap and personnel moves; Stone supplies football advice within his authority, with the specific written-projection consultation right for franchise-level QB actions. Medical staff make diagnosis/return decisions. The staff does not sign a player because the program needs an extra participant. Phase reopening triggered by a personnel move must update only dependent teaching assignments, not retroactively rewrite completed sessions.

## 6. Required new machinery, strictly separated from this design

### 6.1 Render and issue the brief

1. Verify career clock, active season, actual job, program eligibility, NFL calendar/public knowledge cutoff, event history and current staff. If 2014 is still in Week 5, output **research-only files** and never activate April 2015.
2. Resolve the correct league season and logical directory via `runtime.decisions.folder()`, not file names that contain an embedded year. The existing `offseason_program` row is reused.
3. Construct a source snapshot from job, current 2015 opening assessments and roster, current medical restrictions, resolved March personnel/financial moves, legal participation agreements, active-season playbook iterations and past dated football findings. No future performance or real Jaguars transactions enter.
4. Generate the coach-facing football brief using the template. Source every named assessment in its underlying owner; omit unsupported sections rather than adding filler. Legal dates may be displayed with appropriate issue-day knowledge guards.
5. Route actual event inserts through the existing active-phase shared event router. Place `ACTION REQUIRED` at the top only when a real Stone obligation exists, then information-only and upcoming notes as supported. Do not show a synthetic trade call to make the brief interesting.
6. Preserve each issued briefing and its issue time and input provenance in the existing immutable issue-history facility (`briefings.json` design). A later medical communication or actual contract change issues a new version and updates the current view; it never alters the text of the earlier briefing. The published coach page contains no internal identifiers, file paths, software instructions or model terms.

### 6.2 Accept Stone's plan once

`My_Program_Plan.md` is a natural letter-like decision page with headings, not a JSON questionnaire. Support an in-place filled Markdown or attached `.md`/`.txt` with the same headings, and preserve the user's original prose. Require only what actual unfinished football authority demands. Adopt already valid standing instructions unless the user changes them; do not demand a new play-caller, social calendar or unrelated role appointment. Silence does not equal approval if a new, material, required Stone decision remains open.

Parser/validator behind the page normalizes **substantive decisions** (which teaching assignment, unit, legal phase, dates, named players and responsible staff) into private decision metadata. The user can write naturally and explain in detail, but rhetorical intensity or extra prose cannot affect football outcomes. Reject an out-of-eligibility player, prohibited drill, illegal date, personnel transaction disguised as coaching plan, unsupported playbook iteration, medical clearance by Stone, or attempt to overwrite a previously executed plan. Report exactly what needs correction in football language, and otherwise accept the plan with no unnecessary prompt.

### 6.3 Phase-level dependencies and time gates

The present `runtime/decision_queue.py` has a `practice_plan` class but no event-specific blocker for starting or closing these two offseason phases; its generic block kinds cover game inputs, call sheets and season staging/opening. A new guarded *phase workflow* is required. Implement either a carefully extended queue block type (keyed to season and `phase_one`/`phase_two`) or a separate atomic phase gate wired to queue semantics; do not pretend that merely adding prose to a current queue item stops a script.

Proposed sequence:

- `RESEARCH_ONLY`: upcoming dates known, no new team season activated, no report/assessment fabricated.
- `ELIGIBLE_TO_ISSUE`: prior season really closed, employee has authority and participating program has legally valid scheduled start and filing evidence. No event committed.
- `AWAITING_STONE` if an actual uncovered practice decision is open. An effective standing instruction can satisfy what it actually covers and cannot be silently extended to a new choice.
- `PLAN_ADOPTED`: Stone's decision fixed, first dependent session may be prepared if attendance, medical, contract and CBA checks pass.
- `PHASE_ONE_ACTIVE` and `PHASE_ONE_REVIEWED`: each actual session advances only when authorized; Phase One report and updated teaching questions verified before Phase Two is materially built.
- `PHASE_TWO_ACTIVE` and `PHASE_TWO_REVIEWED`: separate-unit sessions and the Phase Two report are resolved without an illegal opponent.
- `PROGRAM_REPORTED`: overall derived report issued only after actual Phase Two closure, or a documented partial/terminated program is reported explicitly as such. No silent completion merely because May 22 passes.

Guards must be **dependency-specific**: an open decision over a revised Phase Two installation blocks only the affected Phase Two work, not Caldwell's parallel draft, unrelated free agency or other clubs' league events. Do not reuse a global game-week pause to block April unrelated actions. Resuming twice must not add two sessions or two decisions. The bridge must preserve date order, past issued pages and an unplayed 2014 Week 6 while this is only design work.

### 6.4 Actual football observations and evaluation limits

Before each authorized session, assemble a dated operational plan with actual permitted participants, medical/workload status, source teaching questions and legal unit grouping. A result must originate from specific authorized work, documented by the session source and any genuinely permitted resolution process. The present week-game private kernel is **not** an April practice model. There is no supported new production algorithm here that can turn a drill choice into improved player ability, roster status or a numerical football grade. Until one is explicitly designed and validated, report observed assignment/technique evidence and bounded judgment, not invented progress or simulated quantified gain.

Keep an observation record with: practice date, phase and legal mode; person(s) actually eligible and participating; responsible coach; existing installed call/assignment and evidence source; what happened in a defined opportunity; correction made; later independent check, if any; medical limitations; and what cannot be inferred. This record is behind the scenes or in the appropriate authoritative phase report, never raw identifiers on the coach-facing page. A later session may contradict an earlier finding. No improvement is guaranteed or rewarded because the user wrote an articulate plan. Different player types and limited sample sizes may create different *supported* observations, but no forced positive/negative balance, repeatable grade rubric or made-up video.

At most the Phase One record establishes classroom explanation and independently recorded physical measurements, if any. Phase Two adds separate-unit movement; no level of Phase Two repetition licenses a claim that a defender was beaten or a coverage was tested against an opponent. OTA opposed work is a later distinct legal opportunity. Handle the late draft and rookie minicamp separately: April 30-May 2 draft outcomes cannot be backdated into April 20's participant register; rookies must have a valid program/roster entry and their separate rookie-camp evidence before anything about them is carried forward to permitted subsequent work.

### 6.5 Individual events and phase-level summaries

Re-use `docs/event_inserts.md` and `foundation/templates/event_inserts/` for incoming consequential matters. The active Offseason Program Brief is the single main page for them. `My_Program_Plan` may contain an answer for a matter genuinely part of Stone's program-plan authority. An unrelated trade or contractual response normally belongs in one `Offseason_Training/My_Responses.md` journal, not in an unstructured overwrite of the approved plan. Keep each answer bound to the correct dated event, its authority and the evidence Stone saw.

**Mandatory invariant:** for every separately concluded consequential matter, create **one standalone, dated, reader-facing Markdown result owned by the department responsible for that event, as soon as it is resolved**, including rejection, failure and valid expiry. A source transaction record may double as that sole result if it is already suitable; never create a second competing event narrative. Examples: one rejected trade result in `Team_Operations/Trades`, one unsuccessful contract negotiation in its relevant Free_Agency or contract owner, one failed coach hire in `Early_Offseason/staff_changes` or its authorized coaching career owner, and one clinician decision in the correct medical incident owner. A still-open contact does **not** have a final result, but its process history remains distinct. The `Program_Report.md` row supplies only date, plain issue, disposition and a link to that event's own output. A phase summary and `Record.md` are indices, not substitute outputs.

The durable event owner should carry its unique `<!-- event-record: {...} -->` metadata as supported by `runtime/events.py`: unique descriptive ID, date, status `closed`, one-line summary, applicable date_end and season mapping. The generated annual record then links to that owner. Re-issuing a brief or rerendering a summary cannot re-resolve the event or create an extra result. Where a failed offer is not a roster mutation, its own dated result still exists, but no roster/cap/player record is falsely changed. Process events and the final disposition are reconciled; do not count one negotiation's proposal and counter as two independently concluded signings.

### 6.6 Derived Program Report and onward transfer

Close Phase One and Phase Two through their actual `training_report.md` owners, each containing location, dates, actual days, legal participation, football work, consequential corrections, and bounded uncertainties. Generate the `Program_Report.md` from both, preserving explicit unresolved items. If only Phase One is complete, display Phase One as a dated interim view at its authoritative phase owner and leave the five-week Program Report open, instead of creating imaginary Phase Two work. Distinguish dates scheduled, held, cancelled and staff-only reviews. A replacement participant enters prospectively, not retroactively.

Use named coaching problems as the transfer to the OTA brief: call/assignment, earlier supported opportunity, legal Phase One/Two evidence, what remains untested against defenders, relevant current eligible players, and responsible coach. The OTA workflow can change the upcoming teaching plan, but cannot rewrite prior practice facts. Preserve existing medically constrained learning arrangements, active-playbook access and current coaching authority. Opening May/June OTA pages is not authorized by closing the April report alone; its own decision and actual legal time gate apply.

## 7. Implementation surface and current status

| Component | Existing evidence | Exact requirement |
|---|---|---|
| `runtime/decisions.py` | Registered `offseason_program`, correct three titles, `implemented=False` | Add proper render/issue/decision/close workflow and only then flag implemented. Do not rename titles. |
| `runtime/seasons.py`, `runtime/season_layout.py` | SeasonPaths and legacy/offseason folder aliases, current 2014 and 2015 routes | Resolve new season path through map, protect frozen older paths, and avoid fallback from a missing 2015 file to 2014. |
| `runtime/decision_queue.py` | `practice_plan` class with no phase start or close block kind | Implement actual dependency enforcement, user answer source and narrow stops before triggering affected practices. |
| `runtime/events.py`, `scripts/render_annual_record.py` | Per-owner event metadata, unique IDs, generated chronological index | Add validated phase/event metadata to the right records; link each separately resolved event once. |
| `runtime/clean_pages.py` | Enforces no visible implementation jargon, internal identifiers or links to system files | Render prose only; keep diagnostics/method metadata in private source, preserve event metadata in permitted markers. |
| `career/2014/Offseason_Training/` | Completed Phase One/Two staff plans and reports, 2014 decisions | Use as evidence of method and historical precedent, never reauthor or reexecute. |
| `career/2015/Calendar.md`, `library/2015_historical_calendar.md` | 2015 dates with dated source caveats | Read as reference; confirm as-of publication or internally recorded filed schedule before treating as coach-known. |
| `docs/season_structure.md`, `foundation/templates/offseason_training/` | Each phase owns one plan and one full report | Keep these authoritative. Program Report is derived, with links to both, not an extra phase assessment. |
| `docs/event_inserts.md` | Shared response journal, top-of-brief inserts, individual result rule | Connect event router; protect issued versions and unique dated event outputs even on failed approaches. |
| `state/current_job.json`, `state/decision_queue.json` | Active authority, standing rules, currently open Week 6 choices | Respect exact effective date. Do not touch the 2014 active queue during this design. |
| `scripts/season_handoff.py` and opening review | Gated next-season source reconciliation | No April state from the unfinished 2014 year, no automatic successor open. |

**Not presently demonstrated:** a functional April briefing builder, legal schedule/filer, Phase One and Two execution model, immutable April briefing history, pre-2015 active handoff, independent event close integration, or corresponding acceptance tests. Existing game-week and historic 2014 phase records do not prove these functions already work. They are build requirements, not excuses to write hypothetical career output.

## 8. Acceptance and regression tests to add

These are proposed tests, not tests claimed as executed. An implementation is incomplete until it passes them plus the existing repository validation and tests in a safely staged copy.

### Eligibility, chronology and calendar

1. From the present Oct 5, 2014 state, April 2015 builder may generate research templates but creates no 2015 attendance, results, roster transactions, formal head-coach decision, season activation or changed Week 6 queue item.
2. Closing 2014 season, exits and opening checks are prerequisites for an official 2015 head-coach program. A prepared `career/2015/Calendar.md` does not itself open the career.
3. With Stone retained and returning, the schedule starts no earlier than Apr 20, 2015; Apr 6 is rejected unless actual new-head-coach criteria and the branch club schedule permit it.
4. For Apr 20 start, filing due is at least 21 days in advance (no later than Mar 30), subject to the earlier agreed date, if any. A missing actual filing is flagged, never auto-invented.
5. At a briefing issued before May 15/18 source publication, later 2015 OTA dates can be used only if a genuine earlier club schedule record confirms internal knowledge. No backdated public bulletin or falsified staff notice.
6. The program uses Apr 20-May 1 and May 4-May 22 as derived phase windows, with actual held dates recorded separately.
7. Apr 30-May 2 draft overlap does not add drafted players to Apr 20 signed-veteran work or set a Jacksonville selection.
8. May 8-10 rookie minicamp remains a separate eligible event and is never counted as veteran Phase Two field days or as OTA drills.
9. An unexpectedly changed or cancelled session records no phantom completion and leaves the next valid legal opportunity rather than rescheduling silently.
10. An official program cannot be issued to Stone for Jacksonville after an actual termination or change of job. His own four-year guarantee cannot be used as proof of ongoing employment.

### CBA and coaching authority

11. A club-coached film or playbook meeting before the formal start is blocked. Independent player workout availability does not generate a club practice or session evidence.
12. Phase One meeting-room football is permitted within the daily limits, while offensive/defensive position-coach field instruction, observation of physical workouts, team practice and snapper/punter football work are refused.
13. Phase One QB throwing exception is not converted to defended routes, a position-coached passing drill or an on-field staff observation.
14. Phase Two independent position drills and offense-only/defense-only/punt-unit-only legal work pass, while helmets, contact and opponent one-on-ones fail.
15. A simulated practice attempting offensive protection versus a live pass rush in Phase Two fails, even if labeled 'noncontact'.
16. Four weekdays/week, four hours/facility day, two specified hours and 90 field minutes are checked on a **player-level** legal calendar; fifth scheduled day, weekend team practice or excess assignment fails.
17. A veteran who voluntarily does not participate is not marked injured, disloyal, underdeveloped or subject to a punitive reduced role for that nonparticipation.
18. An unsigned tender holder with no executed valid participation agreement cannot participate; possession of a tender alone is insufficient. An appropriately recorded agreement changes only lawful eligibility.
19. A player's medical classroom/physical restrictions control each session. Stone and coordinators cannot clear the person or override a clinician.
20. The compliance process preserves legally required on-field filming and retention information without converting the video record into invented coach grades.
21. Tice's preexisting emergency practice lead, and Crennel's backup role, are honored without repeated user appointment. Neither assistant silently gains roster, depth, disciplinary or install authority.
22. Stone's plan may direct lawful practice but cannot sign players, set contracts, trade, draft or exercise medical authority. His written franchise-QB advice goes to Caldwell without becoming a veto.
23. Installed material comes from the correct active offensive and defensive playbook iterations, and player access to the full active book is not confused with formal coaching installation.

### Football evidence and output quality

24. A classroom explanation is not presented as an executed football play. A correct board check remains limited to the observed question.
25. An on-air run/protection finding never claims a real linebacker or defensive lineman was beaten or a player blocked a live rusher.
26. A changed diagram or unopposed formation can establish transfer only when the retest actually happened; planned retests remain planned.
27. A coach's session selection does not automatically increase player ability, manufacture fitness measurements, produce a new player grade or predetermine a role win.
28. Two actual contradictory practice findings remain distinguishable by date and context; the report does not force a steady improvement curve.
29. If no useful named individual evidence exists, the Program Report contains no fake standout list, balanced pros/cons or league rankings.
30. Signed veteran newcomer and drafted rookie receive distinct onboarding/eligibility; real Jacksonville 2015 roster, quarterback and player-performance history are not imported.
31. Defensive playcalling as of October 2014 remains Stone's; Crennel prepares/transmits; the new April page may not accidentally revert to Crennel as caller without an authorized later change.
32. The 2014 completed record, including Stone's April 18 decisions and Phase Two May 23 observations, is unchanged byte-for-byte by the new design.

### Page architecture, event ownership and idempotency

33. The correct three page titles render in the season's `Offseason_Training/` folder via the folder map and are linked in the season desk after valid issuance. Merely opening them does not advance a date.
34. A genuine mid-phase new injury or trade produces an immutable revised brief; the earlier issued brief and its content/date remain recoverable.
35. No actionable event means no Action Required section, empty manufactured offers or fake dialogue.
36. A material uncovered Stone plan decision blocks **only dependent April work**. A covered standing instruction prevents an unnecessary new question. Caldwell's independent draft or personnel work remains unblocked.
37. Every completed Phase One and Phase Two work item is recorded at its actual owner, with no same-day double application on rerun, repeated page view or interrupted output generation.
38. A Program Report cannot claim Phase Two completion from calendar passage alone. The phase's authoritative actual report is required; a cancelled or incomplete program is described accurately.
39. Three distinct concluded player-contract matters, including a failed negotiation and a decline, produce **three standalone dated readable results** under their correct department owner. The Program Report has three separate links and is not itself any of those results.
40. Two trade proposals from different clubs, one rejected and one pending, produce exactly one closed event result for the rejection; the pending proposal retains dated process history but not an invented final resolution.
41. One unsuccessful staff pursuit produces a separate dated staff result, not merely the sentence 'no hire' buried in the program summary. Stone's authority and budget constraints remain operative.
42. A medical disposition with a roster consequence retains an authoritative medical incident record and, if Caldwell independently executes a transaction, that distinct transaction result has its own owner. No merged pseudo-event or double cap change.
43. Re-rendering `Program_Report.md` cannot start a negotiation, rerun a private draw, create an event, move a contract, change a player or duplicate a resolution.
44. The `Record.md` generator includes one concise entry per authoritative completed event owner; reports link to that page rather than duplicate outcome narration. Event IDs remain unique with a correct in-world date.
45. The April brief, plan and result pass `runtime/clean_pages.py` content checks: no raw codes, internal paths, script names, engine terminology, hidden grades, template instructions, policy disclaimers or metadata exposed as football prose.
46. 2013 historical material, all 2014 reports and the Week 5 receipt remain frozen. The first unplayed career action is still the existing 2014 Week 6 work after research files are written.

### End-to-end acceptance scenario

Use a **separate staged test fixture**, not the active Oct 5 save: a lawful fictional 2015 opening based on permitted facts with explicit test-only inputs. Freeze its dates, retained Stone job, signed and tendered players, medical participation permissions, lawful plan and opponent-free session log before running the scenario. Open a real April briefing, record one Stone plan decision, complete two legally compliant Phase One teaching sessions, close that authoritative Phase One report, complete two legally compliant Phase Two separates sessions, then close Phase Two and generate the report. Insert three **test fixture only** independently concluded transactions (one accepted, two rejected), plus one still-open issue. Assert there are three individual dated event outputs, zero outcome for the still-open matter, one report with three links, no false game/medical/player upgrade, and no rewritten earlier brief. Run the same renderer twice and compare the authoritative state byte-for-byte. Then tear down the fixture without writing to the live repository.

**Stop conditions:** missing filing proof, unclear actual player participation agreement, unverified current roster or clinical instruction, stale phase/active-playbook information, unauthorized head-coach employment, missing canonical phase report, nonexistent individual final-event output, unverified future announcement timing or an unresolved Stone decision that really controls the next dependent session.
