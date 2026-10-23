# OTAs and mandatory minicamp: implementation and validation specification

**Status:** Uploaded by the user on October 20, 2026 and adopted; built in step 7 of the [rebuild plan](rebuild_plan.md). Corrected after the process check of October 20, 2026, against the user's rulings of that day and the defaults the lead settled, each written below as this design's rule. One question in this design awaits the user: how 2015 OTA and minicamp observations are produced ([section 5](#how-2015-observations-are-produced-awaiting-the-users-decision)); its proposal is shown there and is not adopted. The templates are in [foundation/templates/otas/](../foundation/templates/otas/), the worked example is [docs/examples/otas_and_minicamp_jacksonville.md](examples/otas_and_minicamp_jacksonville.md) and the research register and repository assessment are in [docs/otas_and_minicamp_research.md](otas_and_minicamp_research.md). What the build must add, in other files and in code, is listed in [section 7](#7-minimal-proposed-technical-integration); this design edits none of them.

As uploaded: **Status:** Research and design only, inspected against GitHub `Alex-Oss222/football-career-sim` at commit `75fd41fbfc5ed0363d9f6cb68b5bef37a6583f24` (October 20, 2026). The current career remains October 5, 2014, with Week 5 closed and Week 6 unplayed. This package neither edits GitHub nor advances the career. It does not install a practice resolver or run repository tests.

## Workflow 3: May-June OTAs and mandatory minicamp

**Design complete; GitHub implementation not attempted.** The user controls Alex Stone's consequential head-coach decisions. As head coach Stone decides depth, roles, inactives, practice and his staff. David Caldwell decides acquisitions, the draft, contracts, claims and cuts, on Stone's recommendation. The medical staff decide diagnosis and clearance. The live career is October 5, 2014 after Week 5. The real 2015 calendar is reference, not simulated participation.

### Files

| File | Purpose |
|---|---|
| [ota_brief_template.md](../foundation/templates/otas/ota_brief_template.md) | The staff brief: the shared event-insert slot, then tables built from the stored facts, one staff read per unit stored with its author and date, the staff's proposal, the standing instructions in force, who decides what and the deadline |
| [my_install_plan_template.md](../foundation/templates/otas/my_install_plan_template.md) | Stone's page, answered once and kept: practice and teaching choices, with the standing instructions in force shown and not asked again |
| [ota_report_template.md](../foundation/templates/otas/ota_report_template.md) | Built once after minicamp: the schedule held against the announced dates, the two training reports' summaries and carry-forward questions shown or linked by section, the decisions and a link to each event result; no observation of its own |
| [otas_result_template.md](../foundation/templates/otas/otas_result_template.md) | Not a form. Every result in this phase uses the shared [event result](../foundation/templates/event_inserts/event_result_template.md); the page stays only until the template catalog links the shared form (section 7) |
| This document | Folder routes, ownership, settled rules, legal guards, state transitions, 73 proposed tests and what the build must add |
| [otas_and_minicamp_jacksonville.md](examples/otas_and_minicamp_jacksonville.md) | Completed 2014 career evidence in the three-page shape, with 2015 legitimately unknown |
| [otas_and_minicamp_research.md](otas_and_minicamp_research.md#may-june-otas-and-minicamp-period-source-register) | The 2011 CBA reading (the input to the library entry the build adds), contemporary club reports and the source-release boundary |
| [otas_and_minicamp_research.md](otas_and_minicamp_research.md#otas-and-minicamp-repository-assessment-and-blockers) | Proven integration gaps and genuine rule/ownership risks |

### Boundary

The rookie minicamp is its own phase and result owner, with its own `staff_plan.md` and `training_report.md`. It has no decision pages of its own: Stone's direction for it comes in a post-draft reissue of the Offseason Program Brief and is answered on the April My Responses page ([April design](offseason_program.md)). This design only reads its evidence. OTA and veteran minicamp teaching happen in different windows and reports, and the OTA Report is built from them. No action insert replaces an individually resolved event output. Do not edit completed 2014 records, import historical 2015 Jaguars player performance or automatically award a position based on non-contact work.

### Operating rules

1. **Pages and folder.** The three pages, the phase's My Responses page and every kept edition of the brief live in `career/Y/Offseason_Training/OTAs/`, beside that folder's `staff_plan.md` and `training_report.md`, through the folder map (section 1). The April program keeps the `Offseason_Training/` root, so the two phases' `My_Responses.md` pages and kept briefs never share a path, as the February and March phases each have their own folder ([re-signing and free agency design](re_signing_and_free_agency.md), section 1). `Mandatory_Minicamp/` keeps its two files.
2. **One owner for each fact** (the table in section 1). The training reports own practice observations, and the OTA Report indexes them. The roster and medical records own participation and permissions. The library and the 2015 calendar own rules and dates. The job record owns standing instructions and the emergency practice lead. The depth data own the depth chart. Each event result owns its event. The 2014 records stay as written.
3. **The brief proposes; My Install Plan decides.** Stone answers his page once, and it is kept as the record of his decision; it is never rewritten. A later change of direction, and every answer to an inserted event, goes on this phase's My Responses page as a dated entry that applies going forward. Each `staff_plan.md` is built after he answers and links his page without restating his choices.
4. **Events inside the phase** are inserts in the active OTA Brief (ACTION REQUIRED, FOR YOUR INFORMATION or COMING UP, in the form of the shared [insert template](../foundation/templates/event_inserts/brief_action_inserts_template.md)). Stone answers each on this phase's one My Responses page, from the shared [My Responses template](../foundation/templates/event_inserts/my_responses_template.md). Each resolved event gets its own dated result, built on the shared [event result](../foundation/templates/event_inserts/event_result_template.md), in its owner's folder: roster moves in `Team_Operations/Team/Roster`, signings and undrafted pursuits in `Team_Operations/Free_Agency`, trades in `Team_Operations/Trades`, staff in `Team_Operations/Staff` and Stone's own career in `career/Stone`; a medical decision stays in its medical record. A new edition of the brief is issued only under the one reissue rule ([event inserts](event_inserts.md), section A, item 6).
5. **Two briefs at once.** When phases overlap, two briefs may carry inserts at the same time. Each event appears once, on the brief of the phase it bears on, and is answered on that phase's My Responses page. The OTA Brief's first issue falls on the day the April program's Phase Two closes (May 22, 2015), when the Offseason Program Brief stops carrying the program's events ([April design](offseason_program.md#61-render-and-issue-the-brief)); from then a matter of the OTAs, the minicamp or the rookie development program goes on the OTA Brief, and a draft or undrafted matter on the Scouting Department Report while it is still active ([draft design](draft.md#a-fixed-scope-and-first-principles)).
6. **Only an answer due before the event it holds stops the clock.** An open install item holds only the sessions that depend on it. Other clubs' moves, league events and unrelated Jacksonville business go on.
7. **Calls and installation.** Any call in the active playbook may be named on a game plan, preseason included, for any situation; only the no-hindsight lock refuses a call from a later book. On a game plan the "Opening ideas" are listed in order of preference. Naming a call on My Install Plan schedules its teaching: installation decides what is formally taught, practiced and evaluated, never what may be called in a game. Every player may receive and study the complete active books. Players are evaluated only on taught material.
8. **Rails and hindsight.** Other clubs' players follow their real moves on their real dates. The draft follows AGENTS.md rails rule 7, with Jacksonville's order from the career's own standings. Information is usable from its real public date. No real 2015 outcome is used: not the real club's 2015 draft slot, not its held-OTA count, not the training-camp dates before their July 7, 2015 announcement, not any real player's spring.

## 1. What this workflow is, and is not

The three registry pages are fixed and live in the **upcoming active season** under `career/Y/Offseason_Training/OTAs/`, through `runtime.decisions.folder('otas', Y)` once the folder map gives the OTA decision its own place. The build adds it (section 7); today `folder('otas', Y)` returns the `Offseason_Training/` root that the April program also resolves to.

1. `OTA_Brief.md`: the issued staff briefing, with genuine event inserts at the top. Every edition is kept.
2. `My_Install_Plan.md`: Stone's page, answered once and kept as the record of his decision; it is never rewritten. His later changes of direction and his answers to inserted events go on the phase's `My_Responses.md`.
3. `OTA_Report.md`: built once, after the minicamp's staff handoff, from the two phase reports and the decision and event records, linking each completed consequential event separately. Until then the OTA training report is the interim record; there is no interim OTA Report.

The phase's `My_Responses.md` and the brief's kept editions sit in the same folder.

The report is a **built view, not a new practice evidence owner**. The already established primary practice files are `Offseason_Training/OTAs/staff_plan.md`, `Offseason_Training/OTAs/training_report.md`, `Offseason_Training/Mandatory_Minicamp/staff_plan.md` and `.../training_report.md`. The `Rookie_Minicamp/` plan/report files are a distinct owner, because rookie eligibility, date and participants differ. `Offseason_Training/Phase_One/` and `Phase_Two/` are predecessors, not new work to rewrite. The `Coaching_Methods/` and individual film-delivery sources retain their own authorship. No redundant practice transcript or extra per-drill report is created.

Stone may set a new practice priority, change the install while lawful and unfrozen, choose groups and reps, set depth and package roles, and decide whom to invite among unsigned tender players and expired-contract free agents. Caldwell decides acquisitions, the draft, contracts, claims and cuts, on Stone's recommendation, and his office executes participation agreements. The medical staff decide restrictions and clearance. Neither an OTA appearance nor an absence signs or releases a player or clears an injury.

### One owner for each fact

| Fact | Its one owner | What the OTA pages do with it |
|---|---|---|
| Announced dates, the filed schedule and any dated change | `career/Y/Calendar.md`, the season's library calendar entry and the club's filing record (the [April design](offseason_program.md) owns the filing event) | The brief and the report show them; no page sets a date |
| CBA rules | The library, entered in two passes | Linked; section 4 states only what this design relies on until the library entry exists |
| Control, participation basis and participation agreements | The roster record and the player contract records | The brief's participation table is built from them, never typed |
| Onboarding of a newly controlled player | The training report of the phase in which it happens (the [onboarding framework](../career/2013/offseason/player_onboarding_and_development_framework.md), section 1) | The brief's table shows its status |
| Medical work permissions and clearance | The medical records | The brief and report show the communicated permission only |
| Standing instructions and the emergency practice lead | [`state/current_job.json`](../state/current_job.json) | Shown as in force, not asked again |
| The staff's reads and proposal | The brief's authored parts, stored with author and date | Rendered "To come" when absent; the brief proposes |
| Stone's install decision | `My_Install_Plan.md` | The record of his decision, answered once |
| His answers to inserted events and his later changes of direction | The phase's `My_Responses.md` | Dated entries, each applying going forward |
| Intended sessions | `OTAs/staff_plan.md` and `Mandatory_Minicamp/staff_plan.md`, built after he answers, on the shared [session plan](../foundation/templates/coaching_methods/session_plan.md) | Each links his page and does not restate his choices |
| Practice observations, the sessions held, onboarding and family events as held | `OTAs/training_report.md` and `Mandatory_Minicamp/training_report.md` | The OTA Report shows or links them by section |
| Rookie minicamp work | `Rookie_Minicamp/staff_plan.md` and `training_report.md` | Linked; its counts never merge with the veteran counts |
| A changed personnel view of a player | A source-linked dated update on the player's permanent record (`data/people/players/`) | The report links it and writes no judgment of its own |
| Depth chart and roles | The depth data (the team depth chart) | A role or depth call Stone makes is applied there; no page edits it, and `Record.md` lists one line per applied set of depth calls |
| Each event's outcome | Its own dated result at its owner | Linked from its insert and from the OTA Report |
| The annual index | `career/Y/Record.md`, generated | One line per event; no second narrative |
| The 2014 decision package, the April 18, 2014 decisions and the 2014 OTA and minicamp reports | Their 2014 files | History, kept as written; read for precedent only |

## 2. Sources and version precedence

Apply in order:

1. The job record [`state/current_job.json`](../state/current_job.json) (authority, delegation and standing instructions, including the emergency practice lead in `delegation.emergency`), governing Document 3, and the active, season-valid Stone playbook iterations read through the [playbook index](../career/playbook/README.md). The offensive and defensive books covering 2015 remain Iteration I unless an actual canon event changes them.
2. Current in-career clock, season-opening/handoff state, signed personnel, roster/control, medical communication and latest dated practice evidence.
3. `career/Y/Calendar.md` and [`library/2015_historical_calendar.md`](../library/2015_historical_calendar.md), checking public announcement dates separately from dates on a historical reference calendar.
4. The library's entries for the 2011 CBA, Articles 21 and 22 and Appendix G, and contemporary club/NFL explanations; the period CBA controls over later summaries or a character's imprecise rule statement. Until the build's library entry exists, section 4 gives the reading this design relies on.
5. The durable methods AGENTS.md makes mandatory for a development phase: the [onboarding and development framework](../career/2013/offseason/player_onboarding_and_development_framework.md), the [readiness standard](../career/2013/offseason/the_prowl_player_readiness_standard.md) and the [program identity](../career/2013/offseason/the_prowl_program_identity.md) at their carried 2013 paths (no year-local copy exists); the coaching records ([Stone's coaching profile](../career/Stone/Coaching_Profile.md), the relevant section of the [assistants' profiles](../career/Assistant_Coaches/staff_profiles.md), the [coach records method](../foundation/templates/coach_records_method.md) and the [coach records](../data/people/coaches/)); and each phase `staff_plan.md` once built.
6. Stone's [April 18, 2014 decisions](../career/2014/Offseason_Training/stone_april_18_2014_decisions.md), which stay history as written. Their durable method items carry into 2015 as standing policy, without asking Stone again: practice if Stone is out (Tice runs practice, Crennel second, with no depth, install, role, disciplinary or personnel authority; read from the job record, which holds it), defensive intent (TAKE, GIVE, ANSWER on every package), injured-player learning, the targeted cross-training rule (primary job first, roughly 80 to 90% of the meaningful developmental work; newcomers learn their first Jacksonville job first), Westhoff's four punt families and separate grading of operation, kick and coverage while he holds the job, the consultation cadence and voluntary family events with no attendance kept. Their player-specific and dated items are proposed again by the staff in the brief against the 2015 roster: the cross-training list, the defensive relay succession (in 2014 Daryl Smith, then Paul Posluszny, then Julian Stanford) and the 2014 event dates. A proposed list takes effect only when Stone writes it on his page; until then each player works his primary job only. If Tice or Crennel has left the staff, the emergency succession goes back to Stone. The offensive install direction is not an April 18 item: it is the 2014 [staff decision package's](../career/2014/Offseason_Training/staff_decisions.md#install-scope-continue-into-year-two) "Install scope: continue into year two", history like the rest of that package, with AGENTS.md's second-year progression paragraph. Do not blindly reappoint an assistant or player in 2015.
7. Existing OTA and mandatory-minicamp report formats in `foundation/templates/offseason_training/`. Preserve established page ownership and no-duplicate assessment rules.

The job record holds only the emergency lead today; it has no practice subject among its standing instructions, and its `delegation.relay` is the game-day sideline relay (Tice, Bates and Skalaski, from the September 20, 2014 Indianapolis preparation), not the defensive communicator succession. Until the build records the durable April 18 items there (section 7), the brief shows them as carried from the April 18 page and asks nothing about them.

AGENTS.md's year-named instructions that this phase reads (the "2014 carry-forward", "2014 individual training and film" and "Second-year progression" paragraphs) need the user's own 2015 wording. The build flags them for the user and does not rewrite them; until the user words them, the 2013 durable methods apply as the 2014 carry-forward reads them.

A final 2015 roster, complete 2014 season results, 2015 staff hires, transactions, rookies, medical findings or completed practices cannot be read from present history. Research about what the **real** 2015 Jaguars did is rules/date context, not Stone-career evidence.

## 3. Correct historical calendar and release gate

| Year | OTC and rookie dates | Ten historically announced OTA dates | Mandatory minicamp | Evidence status |
|---|---|---|---|---|
| 2014 | April 21 program start; May 16-17 Jacksonville rookie *practice* days | May 27, 28, 29; June 2, 3, 5; June 9, 10, 12, 13 | Physicals June 16, practices June 17-19 | Ten OTA practices and three minicamp practices are complete in Stone career records. Preserve all existing documents and closed content. |
| 2015 | April 20 program start; May 8-10 Jacksonville rookie minicamp; rookie development program from May 11 ([2015 calendar](../career/2015/Calendar.md)), seven weeks, so through June 26 | May 26, 27, 28; June 1, 2, 4; June 8, 9, 11, 12 | June 16-18; June 15 physicals if the club's authorized program actually provides them | Announced dates only. How many the real club held is a later real outcome; the [2015 calendar](../career/2015/Calendar.md#program-phases-and-development-reviews) keeps it as a fenced caveat, and this design neither restates nor uses it. Stone's held days are this career's own events. |

*The Monday physical-examination day follows Article 22 §2; it is not another practice. The 2015 May 8-10 rookie minicamp is not the mandatory veteran minicamp and never counts as a veteran team practice. Historical club rookie weekend publications sometimes print an available three-day window even when fewer practices were actually held; the 2014 club announced two practice days.*

**The schedule filing.** Article 21 §2(c) requires the club's schedule by an agreed date no later than 21 days before the program starts, with advance written notice of any change: March 30, 2015 for an April 20 start. Caldwell's office files the historical dates before March 30 as a dated club event, and Stone receives it as FOR YOUR INFORMATION (the 2014 precedent: [filed March 28](../career/2014/Offseason_Training/staff_decisions.md#march-28-offseason-schedule-filed) for the March 31 limit). The April design owns that event, and the 2015 calendar gains its row (section 7). A filed club schedule and a published public notice are distinct evidence, each with a dated owner. Inside the club the dates are known from the filing; publicly they date from the NFL's May 15, 2015 listing and the Jaguars' May 18, 2015 schedule answer (sources F and G in the [2015 calendar sources](../library/2015_historical_calendar.md)), neither of which is evidence of an earlier publication.

**Every announced date is held** unless Stone cancels or moves one (on his page, or later as a dated entry on My Responses), with the advance written notice to the NFL and NFLPA that Article 21 §2(c) requires, which Caldwell's office gives; the staff records a dated outside cause; or an Article 21 §8 penalty cancels a week. The real club's cancellation is never imported. An announced date is not proof a practice was held: each held session is recorded in its training report.

**When the pages issue.** The OTA Brief has two scheduled issues: at the Phase Two close (Friday, May 22, 2015), and after the last OTA (Friday, June 12, 2015), before minicamp. These follow the 2014 handoffs of May 23 and June 13, with the minicamp agenda frozen before June 17. Any other edition is issued only under the one reissue rule. My Install Plan is due before the first OTA, Tuesday, May 26, 2015. The pre-minicamp edition reports the OTA findings that bear on minicamp and the staff's proposed minicamp agenda under his plan; it asks Stone nothing unless a choice his plan left open, or a finding that changes a choice still pending, needs his answer, which he gives on My Responses. The OTA Report names no training-camp date before the camp schedule's announcement (July 7, 2015, source H); before then it says camp opens on its announced schedule.

## 4. The actual 2011 CBA boundaries

**Ownership.** These rules belong to the library. Rows R4 to R7 of the [2014 league calendar and financial rules](../library/2014_league_calendar_and_financial_rules.md) and the [offseason phase rules verification](../library/2014_offseason_phase_rules_verification.md) hold part of them. The readings below of the rest were checked by the process check against the August 4, 2011 text and await a two-pass library entry (section 7); until that entry exists they are this design's reading, not a library record. Page references give the printed page and then the one-based PDF page, as the library counts.

### Four-week Phase Three and the OTA count

Article 21 §2(b)(iii) (printed p. 132, PDF p. 147): Phase Three is four weeks. At most ten OTA days; at most three in each of its first two weeks; at most four in the third **or** fourth week, with the mandatory veteran minicamp in the other week. A fourth **non-OTA** day during a three-OTA week must comply with Phase Two restrictions. OTAs permit helmets, non-contact seven-on-seven, nine-on-seven and eleven-on-eleven, team offense against team defense and non-contact special-team opposition. They do **not** permit shells/shoulder pads, tackling, live blocking, one-on-one offensive lineman vs. defensive lineman pass rush or one-on-one receiver vs. defender coverage. A whistle at quarterback depth is not proof of a game sack. Article 21 §2(c) (p. 133, PDF p. 148) requires advance written notice to the NFL and NFLPA of any change to the filed schedule, and Article 21 §8(d)(ii) (p. 136, PDF p. 151) cancels the club's next scheduled week of OTAs, minicamps excluded, when a violation is found.

### Facility hours, reporting and participation

Article 21 §5(b) (p. 134, PDF p. 149) applies a four-hour facility day, four days per week and 90-minute field maximum to ordinary non-OTA workouts. Under **Appendix G (printed p. 278, PDF p. 293)**, OTA days allow a maximum six hours per day and two hours on field for any player, with no pads except protective knee or elbow pads; the Article 21 ordinary four-hour facility rule must not be misapplied to OTA days. The library's R5 still marks the 90 minutes and the six and two hours Unverified; the 2011 text confirms them, and the build's library pass upgrades R5.

Article 22 §2 (p. 138, PDF p. 153) allows a Monday for physicals with no practice or workout that day, Tuesday-Thursday mandatory minicamp and a Friday off, in week three or four of Phase Three. Two-a-days are allowed on only two of the three practice days. A player is on the field at most 3.5 hours a day and at most 2.5 hours in one practice under Phase Three rules; any second practice is the rest of the 3.5 hours and walk-through only. No organized activity, taping and treatment included, starts before 7:00 a.m. or ends after 8:30 p.m. local time; players get at least an hour each for lunch and dinner; club activities last at most ten hours a day, taping and treatment included, meal time excluded. Article 22 §5 (p. 139, PDF p. 154) bars contact work and pads at minicamps. Only lawful individual participation is recorded.

Article 21 §1 and §5 make the official offseason program and classrooms voluntary, except the properly noticed Article 22 mandatory veteran minicamp. Article 21 §3 (p. 133, PDF p. 148) and §9 (p. 137, PDF p. 152), applied to minicamps by Article 22 §10 (p. 139, PDF p. 154): unsigned Required Tender players and expired-contract UFAs may participate **if invited and after signing an Offseason Workout and Minicamp Participation Agreement** before taking part. **Stone decides the invitation (practice, job record row 11); Caldwell's office executes the agreement (row 5), and the signing reaches Stone as FOR YOUR INFORMATION.** The 2014 exclusion of four named players (the [user's May 1, 2014 instruction](../career/2014/Early_Offseason/stone_to_caldwell_2014_offseason_decisions.md#september-30-2026-amendment-unsigned-tenders-and-the-cross-training-list), given as Stone, because they were not under contract) was player-specific and is not carried over: the brief asks about any such 2015 player. Until he signs a contract or that agreement, the player takes part in neither the program nor its social events. Whether a particular 2015 player may participate depends on his actual current legal rights and paperwork.

Article 21 §6 (p. 134, PDF p. 149) prohibits team-organized coach-led football work after the offseason program and before camp, with a narrow five-day pre-camp exception for quarterbacks and specifically eligible injured players and its own exclusions. It does not ban player-directed individual conditioning or lawful team contact on unrelated professional business. A summer take-home list is not evidence the player practiced it with staff.

### Separate rookie program

Article 22 §7 (p. 139, PDF p. 154) allows a separate seven-week Rookie Football Development Program, "commencing on or about May 16"; in 2015 it opens May 11 ([2015 calendar](../career/2015/Calendar.md)), so its seventh week ends Friday, June 26, after the veteran program ends with minicamp. No weekend activity is allowed in it except the club's one post-draft rookie minicamp, on the first or second weekend after the draft, and rookies take part in club activities at most ten hours a day. Article 22 §1 (p. 138) places no limit on the number of rookie minicamps inside those seven weeks. This design reads rookie development work inside that window, rookies only, as lawful after the veteran minicamp, under Article 22 and not Article 21 §6; the library entry checks that reading in its two passes. Do not count a veteran in the rookie work merely because both reports share a month. Rookies cannot be placed in veteran OTA drills until their actual club rights, paperwork and applicable college restrictions are verified. The record of a draft selection does not itself prove an executed rookie player contract.

## 5. Football-resolution and no-hindsight contract

**Input for an OTA session:** exact date and CBA phase, roster and valid participants, current medical limits, active playbook, Stone's filed direction, specific calls/situations, rep combinations and support, permissible opposing unit/look, evidence already established and any genuine timing/space/time constraints. The staff should identify a *football question* before practice, not a desired answer.

**Observed record:** dated session type, personnel and changes, actual named assignments, period/repetitions when verified, opponent presentation, whether coach prompted the answer, technique/communication/situation actually observed, correction and next independent opportunity. A negative result can have an unknown cause. An unobserved area stays unobserved.

### How 2015 observations are produced (awaiting the user's decision)

How the dated observations in the 2015 OTA and mandatory-minicamp reports are produced is **awaiting the user's decision**. No practice resolver exists in `runtime/` or `scripts/`, none is approved ([camp and preseason reports](camp_and_preseason_reports.md)), and nothing below is adopted.

**Proposal (not adopted):** use the 2014 method, under AGENTS.md's resolution discipline: observations authored from the work the phase actually scheduled, the players actually eligible and the communicated medical facts, with no draw, under the protagonist-blind rule and its label-swap check, and with the 2014 evidence rules (assignment, communication, technique, physical loss, processing delay, medical limit and coaching failure kept separate; no invented retests, scores, quotes or guaranteed gains; a later session may contradict an earlier one). The closed 2014 reports support only part of that description. The [OTA report](../career/2014/Offseason_Training/OTAs/training_report.md#legal-work-participation-and-medical-method) and the [mandatory minicamp report](../career/2014/Offseason_Training/Mandatory_Minicamp/training_report.md#legal-work-participation-and-medical-method) record that the spring had no engine injury draw for practices and recorded only communicated medical facts. The reports apply evidence separations in their observations without stating them as a method; the OTA receivers row for May 27 to 29, for example, records "a release-timing loss with the assignment intact". The authored, protagonist-blind method with the label-swap check is this proposal's own description, not something the 2014 reports state. A frozen, auditable practice resolver would be separate future work needing the user's approval. The upload's other option, collecting independently supplied session facts, is not proposed, because it would hand the practice facts to the user. Until the user decides, no 2015 practice observation is produced, and a page cites only observations a training report already holds; none is needed before the 2015 phase arrives.

Whatever method is chosen, do **not** turn natural-language ambition into success probabilities or provide an invented strong/average/weak verdict. No result exists if a session has not actually been resolved. The method must respect the global no-hindsight rule and cannot condition on later real Jaguars performances, familiar names or longer prose.

**Evaluation:** no synthetic per-session grades, generic trait upgrades, assumed fitness gains, fixed improvement arcs or guaranteed role gains. Write only football evidence observed. Players are evaluated only on material that was taught; a player who studied a page that was not installed is never marked down for it. Preserve the two annual assessments and their dated evidence updates; one OTA report is not a third annual player grade.

## 6. Decision and publication lifecycle

1. **Eligibility:** Confirm the career season handoff/opening and Stone's current job from the job record. As Jacksonville's head coach he receives these pages. In another club's job the same pages appear with that job's scope: a defensive coordinator's install plan covers the defense only, and where he holds no install authority he receives requests for his evaluations instead ([rebuild plan](rebuild_plan.md), "The decisions in a year"). Out of work, he receives no club brief.
2. **Issue:** The brief has its two scheduled issues (section 3); any other edition is issued only under the one reissue rule. The tables are built from the stored facts as of the issue time. The staff reads and the staff proposal are stored parts with author and date, rendered "To come" when absent, and each read cites only what the page shows. Staff are named only from the coach records and the job record's parties for that season; no scout is named as an author. Inserts appear in deadline order. Every edition is kept in the one phase-brief issue history keyed by phase (the one the February and March briefs use; [re-signing and free agency design](re_signing_and_free_agency.md)), and the latest-view pointer is separate from the kept copies.
3. **Decide:** Stone fills `My_Install_Plan.md` once, in place or by uploading a .md or .txt file with the same headings. A check extracts headings and substantive instructions and tests the active-book lock (Iteration I only in 2015), each named player's control and participation basis (including the onboarding gate for a player who came under control after the program began), medical permissions, the CBA calendar (tests 1 to 20), staffing powers, unresolved dependent items and that silence was not used as consent. Standing instructions in force are shown, not asked again.
4. **Approve and freeze:** Persist Stone's answer and source cutoff; build each `staff_plan.md` as *intended* work, an executable teaching plan that links his page and does not restate his choices, not a predicted report. Freeze before each affected session. My Install Plan is never rewritten after he answers; an upload that would replace it is refused. A later change of direction is a dated entry on My Responses that applies going forward, and the affected session plans follow it before their sessions freeze.
5. **Run separately:** Open and close each authorized OTA date with its session record, produced by the method the user approves (section 5). A cancelled or omitted date produces **no completed practice**. Close the ten-OTA maximum only through the legal schedule. Hold a distinct veteran-minicamp preparation and physicals gate.
6. **Handoff:** The actual phase owners carry practice and medical/participation records; `OTA_Report.md` is built from them once, after the minicamp's staff handoff, and says both the completed and the missing work. Camp dates appear in it only once announced (in 2015, July 7). Do not wait for the end of June to publish an independent completed transaction or hiring result.
7. **Events:** The phase's `My_Responses.md` binds Stone's answers to inserted events. Each separately *resolved* event is written once, on its effective career date, as its own result built on the shared event result, in its owner's folder (operating rule 4). A claim on another club's waived player follows the waiver order, with Caldwell deciding whether to claim on Stone's recommendation; its result is a roster move. Each result is linked from its insert and from the OTA Report. Negative outcomes are outputs. A pending approach remains pending.
8. **Carry forward:** The next camp opens only from verified applicable spring findings. The depth chart and position-battle cards do not change unless Stone actually decides the role; staff questions are not appointments. A role or depth call he does make is applied to the depth data, with one `Record.md` line for each applied set of depth calls. The camp's day limits under Article 23 §6(a) are counted from each player's own report day ([position battles design](position_battles.md)); the OTA Report names no padded date for any player. The no-coached-summer-work constraint remains in force, with the rookie development program inside its own window.

## 7. Minimal proposed technical integration

| Current source or component | What already exists | Change required; do not install in this research package |
|---|---|---|
| `runtime/decisions.py` | `otas` registry entry with the exact three titles and `offseason_training` place; `implemented=False` | Keep the registry entry (no second registry); give the OTA decision its own place, resolving to `Offseason_Training/OTAs/`; add the phase issue/render/validation service. |
| `runtime/season_layout.py`, `runtime/seasons.py` | Central folder map; 2014+ Markdown in `career/Y` and structured files in `data/Y` | Resolve all source and output paths through `SeasonPaths`, including edition history and work records. |
| `runtime/decision_queue.py` | `practice_plan` class but no spring-session block | Add a block kind for a spring session (season and date), so an open install item holds only the sessions that depend on it; a pending independent trade does not block unrelated practice. |
| `docs/event_inserts.md`, `runtime/decisions.EVENTS` | Shared insert and per-event result contract | Reuse issue/response/result routing, including reissue semantics, visibility and dated individual results. Do not create phase-specific transaction-output copies. |
| `Offseason_Training/OTAs/` and `/Mandatory_Minicamp/` | 2014 staff plans and rich completed reports | Continue these two distinct practice evidence owners in 2015, with unplayed and unavailable findings absent. |
| `/Rookie_Minicamp/` | Separate 2014/2015 calendar and expected dedicated phase records | Read completed rookie evidence *if it exists*, never absorb into veteran OTA session counts. |
| `career/Y/Team_Operations/*`, `data/people/players/` | Roster, medical, current depth and permanent player evidence owners | Derive current lists and write dated observations only to rightful owners. No duplicated annual assessments. |
| `scripts/validate_repository.py`, `runtime/clean_pages.py` | Path consistency and coach-page hygiene | Extend to all new three-page files and date/reissue/event output rules. PDFs, scripts, IDs and private state do not leak into coach pages. |
| `scripts/render_annual_record.py`, `runtime/events.py` | Annual index from dated event owners | Include each separately finalized event; never treat a planned OTA or routine rep as a transaction. |

The page destinations and their technical issue metadata are separate: `career/Y/Offseason_Training/OTAs/OTA_Brief.md` (current issue), its kept editions in the same folder and its metadata in the phase's data folder through the canonical folder map; similarly `My_Install_Plan.md`, `My_Responses.md` and `OTA_Report.md`. The April program's issued editions use their own phase key in the shared issue history. Do not repoint April's `Program_Report` to the OTA report.

### What the build must add

The process check of October 20, 2026 found these needs. Each belongs to the build step named; none is done by this design.

| Need | Where | Step |
|---|---|---|
| A folder-map place for the OTA decision that resolves to `Offseason_Training/OTAs/`, and a test that the April and OTA `My_Responses.md` pages and kept briefs have different paths | `runtime/decisions.py` (`PLACES`, `folder()`), `runtime/season_layout.py`, `tests/` | 7 |
| A library entry in two passes: Appendix G's six and two hours (printed p. 278) and Article 21 §5(b)'s 90 minutes (p. 134) out of Unverified; Article 21 §2(c)'s advance notice of changes, §§3 and 9 participation agreements, §6 (p. 134) and §8 penalties; Article 22 §2's two-a-day rules, §5, §7's rookie program (with this design's reading of it against §6) and §10 | `library/2014_league_calendar_and_financial_rules.md` R5, `library/2014_offseason_phase_rules_verification.md`, or a new entry | 7, before the My Install Plan check |
| 2015 calendar rows: "By March 30, latest filing date for an April 20 start" and "June 15, minicamp physicals (club appointment)", as the 2014 calendar has them | `career/2015/Calendar.md` | 6 |
| A decision-queue block kind for a spring session (season and date) | `runtime/decision_queue.py` (`BLOCK_KINDS`, the `practice_plan` class) | 7 |
| The brief's stored staff parts with author and date, rendered "To come" when absent, and its editions in the shared phase-brief issue history keyed by phase (the game week's `briefings.json` is game-only today) | The phase's data folder through the folder map; a builder like `scripts/render_game_week.py` | 7 |
| The My Install Plan check and apply: the active-book lock, control and participation basis including the onboarding gate, medical permissions and the CBA calendar (tests 1 to 20); applied into the two `staff_plan.md` files | A new runtime module and script | 7 |
| A check that My Install Plan is never rewritten after Stone answers (a replacing upload is refused) and that later changes land on My Responses; `runtime/clean_pages.py` stays as it is | The My Install Plan check | 7 |
| Validators for the minicamp two-a-day limits and the rookie-program window (tests 16 and 20) | The My Install Plan check | 7 |
| A standing-instruction subject for practice, the durable April 18 items recorded as standing instructions, and an entry for the defensive relay succession, which `delegation.relay` (the game-day sideline relay) does not hold | `runtime/current_job.py` (`SUBJECTS`), `state/current_job.json` | 7 |
| Event kinds and owners for in-phase player-contract results, including the signings owner `Team_Operations/Free_Agency` | `runtime/decisions.py` (`EVENTS`, `OWNERS`) | 5, extended in 7 |
| Routing for two briefs carrying inserts at once: each event once, on its own phase's brief | `docs/event_inserts.md` (section A, item 3, which assumes one active brief), the event router | 7 |
| The training report that records rookie-only development sessions after the veteran minicamp, inside the program's window | `runtime/season_layout.py` (folder map), `docs/season_structure.md` | 7 |
| The OTA Report builder, from the schedule records, the two training reports, Stone's page, My Responses and the event results | A builder and its check | 7 |
| The tests in section 8, run on a copy | `tests/` | 7 |

**Outside this design.** These process documents and code need the change named; the build makes it, not this design:

- `docs/season_structure.md` line 32: one sentence naming the phase decision pages and saying the OTA Report (like the Program Report) is a built index of the two training reports, not a third assessment. Line 44 and `scripts/season_handoff.py` lines 466 to 473: stop staging `staff_decisions.md` into 2015, since the briefs and the My pages replace it (step 6).
- `docs/update_workflow.md`: a row for the OTA pages (the brief's stored parts and issue record, My Install Plan and its apply into the staff plans, My Responses).
- `docs/season_cycle_milestones.md` lines 25 and 28 to 33: the rows name the new pages, and the OTA row's stop column names the OTA Brief and My Install Plan instead of "The phase plans".
- `foundation/templates/README.md`, the OTA row: the location becomes `Offseason_Training/OTAs/`, and the row links the shared event result instead of `otas/otas_result_template.md`, which is then removed.
- `docs/repository_map.json`: the 2015 phase entries.
- `docs/rebuild_plan.md`: the status and change-log entry for this correction, and in its phase table the "May and June" row's folder becomes `Offseason_Training/OTAs`, changed in the same commit as the `PLACES` change.
- AGENTS.md's year-named instructions (section 2): flagged for the user's 2015 wording.
- The April design, already consistent with this one: the March 30 filing as a dated club event, and the post-draft reissue of the Offseason Program Brief that carries Stone's rookie-minicamp direction.

## 8. Validation tests to implement (not executed)

### Calendar and CBA

1. The six announced 2015 dates in the first two OTA blocks plus four in the third sum to ten opportunities, not eleven.
2. 2014's May 16-17 rookie **practices** are not silently expanded into three because a league window is May 16-18.
3. The ten announced 2015 OTA dates can yield any smaller number of held sessions. The fixture holds eight, a count not taken from any real outcome, with two dates not held for recorded career reasons, and nothing about the real club's spring is read.
4. A ninth held OTA never produces a phantom tenth report.
5. A fifth OTA date in a week or eleventh in the year is rejected.
6. A proposed four-OTA first or second Phase Three week is rejected.
7. A legal fourth-day Phase Two-limited workout is never called an OTA.
8. A padded May/June spring period is refused.
9. A one-on-one pass-rush vs. pass-protection period is refused during an OTA.
10. A one-on-one press receiver vs. corner period is refused during minicamp.
11. Legal non-contact team eleven-on-eleven is accepted, even though Phase Two prohibited it.
12. No completed practice appears before its actual date.
13. The minicamp physicals day has no practice entry and occurs on the correct Monday.
14. A Friday minicamp practice is refused.
15. A fourth mandatory veteran practice day is refused.
16. A minicamp two-a-day is accepted on at most two of the three practice days, with the first practice at most 2.5 hours on the field, the second walk-through only within the 3.5-hour daily total, no activity before 7:00 a.m. or after 8:30 p.m. local time, an hour each for lunch and dinner and at most ten hours of club activity; a third two-a-day day or a break of any of these limits is refused.
17. OTA/non-OTA hours use the correct historical category: Appendix G permits no more than six hours of OTA activities and two hours on-field; Article 21 §5(b) limits ordinary non-OTA work to four facility hours and 90 on-field minutes.
18. A new-head-coach extra voluntary veteran minicamp is not automatically granted to returning Stone.
19. Offseason schedule filing is distinguished from a public article: the club's own dated filing record is the evidence of the filing, and nothing is backdated without it.
20. A coach-led football workout after minicamp and before camp is refused, except an explicitly verified Article 21 §6 five-day exception or rookie development program work, rookies only, inside its seven-week window (in 2015, May 11 to June 26).

### Participants, staff and football evidence

21. An unsigned tender player or expired-contract free agent whom Stone invites can take part once Caldwell's office has executed his participation agreement; blanket automatic exclusion is rejected.
22. An unsigned tender player without agreement cannot be marked present as if contracted.
23. A newly drafted but unsigned rookie's participation basis is verified rather than assumed.
24. A rookie who is not yet eligible because of college/other restrictions cannot appear in the field group.
25. A player medically limited to classroom work cannot appear in a field period.
26. Stone cannot override a medical hold or diagnose a condition through a plan.
27. OTA absence is not marked misconduct, lack of commitment or negative development.
28. Mandatory-minicamp nonattendance distinguishes an excused absence, lawful contract status and genuine unexplained failure; no automatic character judgment.
29. A 2014 staff role does not automatically appoint that person in 2015 if the career's staffing changes.
30. An offense that completes a short pass against a call's designated underneath concession is not marked a defensive assignment failure.
31. A non-contact whistle at the quarterback is not a game sack, tackle or established lineman defeat.
32. A successful seven-on-seven throw alone cannot resolve a contact-release WR battle.
33. The written practice plan can choose new active-book teaching without falsely claiming it has already been installed.
34. Later playbook iterations are rejected for 2015 work, even if their files are present.
35. A role decision is never inferred from a player's larger OTA opportunity alone.
36. A repeated correction is marked retained only with a later independent evidenced session, not by a new adjective.
37. Medical absence and practice workload can be recorded without unsupported causal claims about later improvement.
38. The rookie camp and veteran OTA practice counts never merge.
39. A prepared film packet cannot be labelled delivered without its delivery owner.
40. No generated 2015 player report mentions a full 2014 season performance until the 2014 season has actually closed.

### Decision, event, data and view consistency

41. The three pages, the phase's `My_Responses.md` and the brief's kept editions resolve to `Offseason_Training/OTAs/` through the folder map, and never to the April program's paths.
42. Updating a current briefing preserves all earlier issued copies and their information cutoffs.
43. A voluntary routine teaching correction requires no new Stone signoff, unless it changes a retained substantive choice.
44. An unanswered Stone install decision blocks only dependent practice, not a league-wide game or an unrelated medical appointment.
45. A pending midweek trade reissues the brief only when Stone owes an answer on it; otherwise it appears under FOR YOUR INFORMATION in the next issued edition.
46. An informational transaction result that changes no pending choice waits for scheduled briefing publication but its **own** dated result is immediately readable.
47. Two concluded contracts plus a failed hire during minicamp produce three distinct dated result files, not one paragraph in the OTA Report.
48. A rejected trade remains an individual dated result, not merely an FYI line.
49. A linked existing trade output is reused rather than duplicated under the OTA folder.
50. A delayed or unresolved negotiation has a process record but no invented outcome page.
51. Report summarization cannot mutate practice, contract, staff, roster or medical records.
52. Re-rendering or viewing the plan cannot create practices, event closures or updated player ability.
53. The 2014 OTA and minicamp source files remain byte-for-byte unchanged when designing the 2015 workflow.
54. The 2015 season remains unactivated while the current league clock is October 5, 2014.
55. Clean-page validation rejects internal IDs, file paths, private procedure names and source jargon from issued coach pages.
56. Repeated builds with the same frozen inputs yield identical outputs and do not duplicate annual-record event lines.
57. The result links only actual individual event owners and actual practice records.
58. The OTA Report cannot act as an individual event output or another annual assessment.

The next four come from the uploaded result reference, which is not placed as a form:

59. Two contract negotiations resolved on June 2 require two individual results, including any refusal.
60. A trade approach rejected June 4 receives its own trade result, whether or not it affects the next OTA block.
61. A minicamp report is not the output of a June 17 medical evaluation or roster transaction; it links that event's actual result.
62. One minor in-practice teaching correction is part of the practice report, not a fabricated contract, medical or personnel event.

### Ownership and settled rules

63. A player who comes under Jacksonville control after the program began cannot appear in a field group until his onboarding (welcome package, playbook, follow-up call) is recorded, on a compressed timeline that is never backdated.
64. The brief reads the emergency practice lead from the job record and asks nothing about a durable item already in force; it proposes the cross-training list and the defensive relay succession again against the current roster, and if Tice or Crennel has left, it asks Stone for the emergency succession.
65. Every statement in the OTA Report is a schedule fact, a decision, an event link or text shown from or linked to a training report section; a report with an observation of its own fails.
66. The OTA Report names no training-camp date before that date's announcement (July 7 in 2015).
67. Each `staff_plan.md` links My Install Plan and restates none of its choices.
68. My Install Plan is never rewritten after Stone answers it: a later change of direction, or an answer to an inserted event, lands on the OTA My Responses page as a dated entry, and an upload that would replace the answered page is refused.
69. While the April brief and the OTA Brief are both active, an event appears once, on its own phase's brief, and is answered on that phase's My Responses page; each resolved event has one result.
70. The brief's participation and medical table matches the roster and medical records at the issue time; a hand-typed row fails.
71. A call from the active books named on My Install Plan schedules teaching only: no call in the active books becomes callable or uncallable in a game because of the install plan, and no player is marked down for a page that was not taught.
72. The brief and the report name a coach only from the coach records and the job record's parties for that season, and no scout as an author; a 2014 position coach whose contract has ended is named only when a 2015 record shows him on the staff.
73. An announced OTA date not held carries its dated cause: Stone's change with Caldwell's office's notice to the NFL and NFLPA, a recorded outside cause or an Article 21 §8 cancellation; no other cancellation appears.

## 9. End-to-end acceptance story

On a valid future 2015 pre-OTA date, with the 2014 season/handoff and 2015 staff/roster already legitimately established, issue a brief from Phase One/Two and rookie-camp evidence then known. Stone files his install plan. The legal 2015 OTA calendar Caldwell's office filed is used, but two dates are independently not held, a fixture count taken from no real outcome. Eight legal non-contact practices and an authorized three-day veteran minicamp are resolved **only by the method the user approves** (section 5); no fact about what happened in the real Jaguars' spring is used. One genuine rejected trade and two unrelated completed contractual dispositions receive **three separate individual outputs** at their owner dates. The phase training reports own the observable practice evidence; the OTA Report is built from them and links them. Summer begins without a coaching practice being invented. Re-rendering leaves the entire state unchanged.

This is a regression scenario, not a claim that these events occurred in Stone's 2015 season.
