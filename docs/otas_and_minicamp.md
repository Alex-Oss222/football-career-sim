# OTAs and mandatory minicamp: implementation and validation specification

**Status:** Uploaded by the user on October 20, 2026 and adopted; built in step 7 of the [rebuild plan](rebuild_plan.md). The templates are in [foundation/templates/otas/](../foundation/templates/otas/), the worked example is [docs/examples/otas_and_minicamp_jacksonville.md](examples/otas_and_minicamp_jacksonville.md) and the research register and repository assessment are in [docs/otas_and_minicamp_research.md](otas_and_minicamp_research.md).

As uploaded: **Status:** Research and design only, inspected against GitHub `Alex-Oss222/football-career-sim` at commit `75fd41fbfc5ed0363d9f6cb68b5bef37a6583f24` (October 20, 2026). The current career remains October 5, 2014, with Week 5 closed and Week 6 unplayed. This package neither edits GitHub nor advances the career. It does not install a practice resolver or run repository tests.

## Workflow 3: May-June OTAs and mandatory minicamp

**Design complete; GitHub implementation not attempted.** The user controls Alex Stone's consequential head-coach decisions. David Caldwell controls player contracts, acquisitions, trades, draft choices and roster cuts; medical professionals control diagnoses and clearance. The live career is October 5, 2014 after Week 5. The real 2015 calendar is reference, not simulated participation.

### Files

| File | Purpose |
|---|---|
| [ota_brief_template.md](../foundation/templates/otas/ota_brief_template.md) | Full staff brief with real unit questions and active event-insert placement |
| [my_install_plan_template.md](../foundation/templates/otas/my_install_plan_template.md) | Editable coach page with practice/teaching choices and existing standing directions |
| [ota_report_template.md](../foundation/templates/otas/ota_report_template.md) | Narrative and evidence-based combined result, built from distinct official OTA and minicamp reports |
| [otas_result_template.md](../foundation/templates/otas/otas_result_template.md) | Per-event negative and positive result format, reusing existing event owners |
| This document | Folder routes, legal guards, state transitions and 58 proposed tests |
| [otas_and_minicamp_jacksonville.md](examples/otas_and_minicamp_jacksonville.md) | Completed 2014 actual-career evidence, with 2015 legitimately unknown |
| [otas_and_minicamp_research.md](otas_and_minicamp_research.md#may-june-otas-and-minicamp-period-source-register) | Original 2011 CBA, contemporary club reports and source-release boundary |
| [otas_and_minicamp_research.md](otas_and_minicamp_research.md#otas-and-minicamp-repository-assessment-and-blockers) | Proven integration gaps and genuine rule/ownership risks |

### Boundary

The rookie minicamp is its own phase and result owner. OTA and veteran minicamp teaching happen in different windows and reports, then one third-page OTA Report can synthesize their consequential football. No action insert replaces an individually resolved event output. Do not edit completed 2014 records, import historical 2015 Jaguars player performance or automatically award a position based on non-contact work.

## 1. What this workflow is, and is not

The three registry pages are fixed and live in the **upcoming active season** under `career/Y/Offseason_Training/`, through `runtime.decisions.folder('otas', Y)`:

1. `OTA_Brief.md`: issued staff briefing, including genuine event inserts at the top.
2. `My_Install_Plan.md`: Stone's actual editable instructions, immutable as a committed decision after adoption; append a dated authorized amendment rather than silently altering history.
3. `OTA_Report.md`: readable spring synthesis after work genuinely occurs, based on the two phase-report owners and separately linking completed consequential events.

The report is a **view, not a new practice evidence owner**. The already established primary practice files are `Offseason_Training/OTAs/staff_plan.md`, `Offseason_Training/OTAs/training_report.md`, `Offseason_Training/Mandatory_Minicamp/staff_plan.md` and `.../training_report.md`. The `Rookie_Minicamp/` plan/report files are a distinct owner, because rookie eligibility, date and participants differ. `Offseason_Training/Phase_One/` and `Phase_Two/` are predecessors, not new work to rewrite. The `Coaching_Methods/` and individual film-delivery sources retain their own authorship. No redundant practice transcript or extra per-drill report is created.

The user may make a new practice priority, change the install while lawful and unfrozen, choose groups/reps and set depth/package roles within the authority record. Caldwell chooses acquisitions, contracts and draft selections. Medical staff choose restrictions and clearance. Neither an OTA appearance nor absence signs/releases a player or clears an injury.

## 2. Sources and version precedence

Apply in order:

1. Latest current-job and authority `state/current_job.json`, governing Document 3, and the active, season-valid Stone playbook iteration. The version of the offensive/defensive book covering 2015 remains Iteration I unless an actual canon event changes it.
2. Current in-career clock, season-opening/handoff state, signed personnel, roster/control, medical communication and latest dated practice evidence.
3. `career/Y/Calendar.md` and `library/2015_historical_calendar.md`, checking public announcement dates separately from dates on a historical reference calendar.
4. 2011 CBA Article 21, Article 22, Appendix G and contemporary club/NFL explanations; the period CBA controls over later summaries or a character's imprecise rule statement.
5. Stone's actual April 18, 2014 operating instructions, but only while unchanged and logically applicable: Tice/Crennel emergency practice coverage, targeted cross-training, injured-player learning, offensive/defensive teaching, consultation, Westhoff's punt evaluation and genuinely optional family events. Do not blindly reappoint an assistant or player in 2015.
6. Existing OTA and mandatory-minicamp report formats in `foundation/templates/offseason_training/`. Preserve established page ownership and no-duplicate assessment rules.

A final 2015 roster, complete 2014 season results, 2015 staff hires, transactions, rookies, medical findings or completed practices cannot be read from present history. Research about what the **real** 2015 Jaguars did is rules/date context, not Stone-career evidence.

## 3. Correct historical calendar and release gate

| Year | OTC and rookie dates | Ten historically announced OTA dates | Mandatory minicamp | Evidence status |
|---|---|---|---|---|
| 2014 | April 21 program start; May 16-17 Jacksonville rookie *practice* days | May 27, 28, 29; June 2, 3, 5; June 9, 10, 12, 13 | Physicals June 16, practices June 17-19 | Ten OTA practices and three minicamp practices are complete in Stone career records. Preserve all existing documents and closed content. |
| 2015 | April 20 program start; May 8-10 Jacksonville rookie minicamp | May 26, 27, 28; June 1, 2, 4; June 8, 9, 11, 12 | June 16-18; June 15 physicals if the club's authorized program actually provides them | The real Jacksonville club held nine OTAs in 2015; Stone's actual future attendance/held days are unknown. Do not import cancellation. |

*The Monday physical-examination day follows Article 22 §2; it is not another practice. The 2015 May 8-10 rookie minicamp is not the mandatory veteran minicamp and never counts as a veteran team practice. Historical club rookie weekend publications sometimes print an available three-day window even when fewer practices were actually held; the 2014 club announced two practice days.*

The 2015 public program schedule cited later in the year cannot be described as officially announced to Stone on an unsupported earlier date. A filed internal club schedule and a published public notice are distinct evidence, and both need a dated owner. The April 20 start implies a CBA filing no later than March 30 unless an earlier agreed date was established, but neither this arithmetic nor the real team's schedule proves a career filing occurred.

## 4. The actual 2011 CBA boundaries

### Four-week Phase Three and the OTA count

Article 21 §2(b)(iii): Phase Three is four weeks. At most ten OTA days; at most three in each of its first two weeks; at most four in the third **or** fourth week, with the mandatory veteran minicamp in the other week. A fourth **non-OTA** day during a three-OTA week must comply with Phase Two restrictions. OTAs permit helmets, non-contact seven-on-seven, nine-on-seven and eleven-on-eleven, team offense against team defense and non-contact special-team opposition. They do **not** permit shells/shoulder pads, tackling, live blocking, one-on-one offensive lineman vs. defensive lineman pass rush or one-on-one receiver vs. defender coverage. A whistle at quarterback depth is not proof of a game sack.

### Facility hours, reporting and participation

Article 21 §5(b) applies a four-hour facility day, four days per week and 90-minute field maximum to ordinary non-OTA workouts. Under **Appendix G (printed p. 278, PDF p. 292)**, OTA days allow a maximum six hours of club activity per day and two hours on field for any player; the Article 21 ordinary four-hour facility rule must not be misapplied to OTA days. Article 22 §2 allows a Monday for physicals, Tuesday-Thursday mandatory minicamp with a Friday off, ten hours of activities daily (excluding meal time), 3.5 hours on field, at most 2.5 hours in one Phase-Three-type practice; any second practice is walkthrough only. The club must provide meal breaks and comply with time limits. Only lawful individual participation is recorded.

Article 21 §1/§5 makes the official offseason program and classrooms voluntary, except the properly noticed Article 22 mandatory veteran minicamp. Article 21 §3: unsigned required-tender players and expired-contract UFAs may participate **if properly invited and after signing the specified participation agreement**; absence of a 2014 signature was a *2014 record fact*, not a rule that all unsigned tender players are forbidden. This corrects overbroad reuse of Stone's 2014 exclusion policy. Whether a particular 2015 player may participate depends on the person's actual current legal rights and paperwork.

Article 21 §6 prohibits team-organized coach-led football work after the offseason program and before camp, with a narrow five-day pre-camp exception for quarterbacks and specifically eligible injured players and its own exclusions. It does not ban player-directed individual conditioning or lawful team contact on unrelated professional business. A summer take-home list is not evidence the player practiced it with staff.

### Separate rookie program

Article 21/22 allow the distinct post-draft rookie-minicamp and rookie development calendar under conditions specific to rookies, tryouts and graduation/college restrictions. Do not count a veteran in the rookie work merely because both reports share a month. Rookies cannot be placed in veteran OTA drills until their actual club rights, paperwork and applicable college restrictions are verified. The record of a draft selection does not itself prove an executed rookie player contract.

## 5. Football-resolution and no-hindsight contract

**Input for an OTA session:** exact date and CBA phase, roster and valid participants, current medical limits, active playbook, Stone's filed direction, specific calls/situations, rep combinations and support, permissible opposing unit/look, evidence already established and any genuine timing/space/time constraints. The staff should identify a *football question* before practice, not a desired answer.

**Observed record:** dated session type, personnel and changes, actual named assignments, period/repetitions when verified, opponent presentation, whether coach prompted the answer, technique/communication/situation actually observed, correction and next independent opportunity. A negative result can have an unknown cause. An unobserved area stays unobserved.

**Outcome engine:** none has been shown to resolve future OTA and minicamp sessions generally. Implementation must either (a) integrate an approved, auditable, protagonist-blind practice-event procedure frozen before use, or (b) collect explicitly observed session facts as actual new authorized inputs. Do **not** turn natural-language ambition into success probabilities or provide an invented strong/average/weak verdict. No result exists if a session has not actually been resolved. The method must respect the game's global no-hindsight rule and cannot condition on later real Jaguars performances, familiar names or longer prose.

**Evaluation:** no synthetic per-session grades, generic trait upgrades, assumed fitness gains, fixed improvement arcs or guaranteed role gains. Write only football evidence observed. Preserve the two annual assessments and their dated evidence updates; one OTA report is not a third annual player grade.

## 6. Decision and publication lifecycle

1. **Eligibility:** Confirm career season handoff/opening and that Stone still holds Jacksonville's head-coach appointment. If not, never issue him a Jacksonville briefing.
2. **Issue:** Staff assembles evidence cut at the simulated issue time, flags only real questions, includes event inserts in deadline order and issues an immutable version of `OTA_Brief.md`; a latest-view pointer is separate from the saved issued copies.
3. **Decide:** Stone fills `My_Install_Plan.md` naturally or submits a Markdown/text equivalent. A validator extracts headings and substantive instructions, checks active book, legal time, people/control/medical, staffing powers, unresolved dependent items and that silence was not used as consent. Prior adopted standing instructions do not need to be re-asked.
4. **Approve and freeze:** Persist Stone's answer and source cutoff; build actual session plans as *intended* work. `staff_plan.md` in each owner is an executable teaching plan, not a predicted report. Freeze before each affected session; a material change gets a dated amendment after Stone chooses.
5. **Run separately:** Open and close each authorized OTA date with session evidence; a cancelled or omitted date produces **no completed practice**. Close the ten-OTA maximum only through the legal schedule. Hold a distinct veteran-minicamp preparation and physicals gate.
6. **Handoff:** The actual phase owners carry practice and medical/participation records; `OTA_Report.md` is rendered from them and says both the completed and the missing work. Do not wait for end of June to publish an independent completed transaction or hiring result.
7. **Events:** The active phase's shared `My_Responses.md` binds individual decisions. Each separately *resolved* event is written once, on its effective career date, at its rightful owner and linked in the active index and OTA report. Negative outcomes are outputs. A pending approach remains pending.
8. **Carry forward:** Next camp opens only from verified applicable spring findings. The chart and position-battle cards do not change unless Stone actually decides the role; staff questions are not appointments. The no-coached-summer-work constraint remains in force.

## 7. Minimal proposed technical integration

| Current source or component | What already exists | Change required; do not install in this research package |
|---|---|---|
| `runtime/decisions.py` | `otas` registry entry with the exact three titles and `offseason_training` place; `implemented=False` | Reuse existing entry and destination; add phase issue/render/validation service. No second registry. |
| `runtime/season_layout.py`, `runtime/seasons.py` | Central folder map; 2014+ Markdown in `career/Y` and structured files in `data/Y` | Resolve all source and output paths through `SeasonPaths`, including edition history and work records. |
| `runtime/decision_queue.py` | `practice_plan` class but no OTA-specific close block | Add an OTA-plan/phase-close block bound only to dependent work; a pending independent trade does not block unrelated practice. |
| `docs/event_inserts.md`, `runtime/decisions.EVENTS` | Shared insert and per-event result contract | Reuse issue/response/result routing, including reissue semantics, visibility and dated individual results. Do not create phase-specific transaction-output copies. |
| `Offseason_Training/OTAs/` and `/Mandatory_Minicamp/` | 2014 staff plans and rich completed reports | Continue these two distinct practice evidence owners in 2015, with unplayed and unavailable findings absent. |
| `/Rookie_Minicamp/` | Separate 2014/2015 calendar and expected dedicated phase records | Read completed rookie evidence *if it exists*, never absorb into veteran OTA session counts. |
| `career/Y/Team_Operations/*`, `data/people/players/` | Roster, medical, current depth and permanent player evidence owners | Derive current lists and write dated observations only to rightful owners. No duplicated annual assessments. |
| `scripts/validate_repository.py`, `runtime/clean_pages.py` | Path consistency and coach-page hygiene | Extend to all new three-page files and date/reissue/event output rules. PDFs, scripts, IDs and private state do not leak into coach pages. |
| `scripts/render_annual_record.py`, `runtime/events.py` | Annual index from dated event owners | Include each separately finalized event; never treat a planned OTA or routine rep as a transaction. |

A specific editable page destination and its technical issue metadata are separate: `career/Y/Offseason_Training/OTA_Brief.md` (current issue), dated issued editions under its routed view directory and metadata under `data/Y/Offseason_Training/` (by the canonical folder map); similarly `My_Install_Plan.md` and `OTA_Report.md`. Ensure the April program's issued-version records use distinct phase keys. Do not repoint April's `Program_Report` to the OTA report.

## 8. Validation tests to implement (not executed)

### Calendar and CBA

1. The six announced 2015 dates in the first two OTA blocks plus four in the third sum to ten opportunities, not eleven.
2. 2014's May 16-17 rookie **practices** are not silently expanded into three because a league window is May 16-18.
3. The ten announced 2015 OTA dates can yield nine actual held sessions, one cancelled, without copying the real Jaguars' cancellation.
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
16. A minicamp two-a-day has a second session restricted to walkthrough with legal duration/rest.
17. OTA/non-OTA hours use the correct historical category: Appendix G permits no more than six hours of OTA activities and two hours on-field; Article 21 §5(b) limits ordinary non-OTA work to four facility hours and 90 on-field minutes.
18. A new-head-coach extra voluntary veteran minicamp is not automatically granted to returning Stone.
19. Offseason schedule filing is distinguished from a public article and is not backdated without an actual receipt.
20. A pre-camp coach-led football workout after minicamp is refused except an explicitly verified Article 21 exception.

### Participants, staff and football evidence

21. An unsigned tender player with the required valid participation agreement can be invited under Article 21; blanket automatic exclusion is rejected.
22. An unsigned tender player without agreement cannot be marked present as if contracted.
23. A newly drafted but unsigned rookie's participation basis is verified rather than assumed.
24. A rookie who is not yet eligible because of college/other restrictions cannot appear in the field group.
25. A player medically limited to classroom work cannot appear in a field period.
26. Stone cannot override a medical hold or diagnose a condition through a plan.
27. OTA absence is not marked misconduct, lack of commitment or negative development.
28. Mandatory-minicamp nonattendance distinguishes an excused absence, lawful contract status and genuine unexplained failure; no automatic character judgment.
29. A 2014 staff role does not automatically appoint that person in 2015 if branch staffing changes.
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

41. Three primary pages resolve to the single mapped `Offseason_Training` destination.
42. Updating a current briefing preserves all earlier issued copies and their information cutoffs.
43. A voluntary routine teaching correction requires no new Stone signoff, unless it changes a retained substantive choice.
44. An unanswered Stone install decision blocks only dependent practice, not a league-wide game or an unrelated medical appointment.
45. A pending midweek trade inserts in the active phase brief only when Stone actually has an answer to give.
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
58. The OTA report cannot act as an individual event output or another annual assessment.

## 9. End-to-end acceptance story

On a valid future 2015 pre-OTA date, with the 2014 season/handoff and 2015 staff/roster already legitimately established, issue a brief from Phase One/Two and rookie-camp evidence then known. Stone files his install plan. The approved legal 2015 OTA calendar is used, but one date is independently not held. Nine legal non-contact practices and an authorized three-day veteran minicamp might be resolved **only by the approved practice method**; no fact about what happened in the real Jaguars' spring is used. One genuine rejected trade and two unrelated completed contractual dispositions receive **three separate individual outputs** at their owner dates. The phase training reports own the observable practice evidence; the combined OTA Report reads and links them. Summer begins without a coaching practice being invented. Re-rendering leaves the entire state unchanged.

This is a regression scenario, not a claim that these events occurred in Stone's 2015 season.
