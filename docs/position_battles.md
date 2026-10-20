# Training camp position battles: implementation and validation specification

**Status:** Uploaded by the user on October 20, 2026 and adopted; built in step 8 of the [rebuild plan](rebuild_plan.md). The templates are in [foundation/templates/position_battles/](../foundation/templates/position_battles/), the worked example is [docs/examples/position_battles_jacksonville.md](examples/position_battles_jacksonville.md) and the research register and repository assessment are in [docs/position_battles_research.md](position_battles_research.md).

As uploaded: **Status:** Design only, no GitHub mutation or simulation. Repository inspected at default-branch commit `75fd41fbfc5ed0363d9f6cb68b5bef37a6583f24` on October 20, 2026. The latest actual simulated event is October 5, 2014, Week 5. The remaining 2014 season is not played and 2015 camp has not occurred. All validation cases below are **proposed**, not executed.

## Training Camp Position Battles: research and Markdown design package

This is **workflow 4 of 6**, designed for the upcoming 2015 Jacksonville season from the existing career evidence, using the original 2011 CBA and credible 2014–15 club reporting. The simulator's active career is after Week 5, October 5, 2014. All 2014 preseason games and camp comparisons are previously completed, their contents are not replayed. **No GitHub files were modified or 2015 depth, camp or roster results created.**

### Main three pages

1. [Position Battle Report](../foundation/templates/position_battles/position_battle_report_template.md), a staff briefing that offers a genuine, detailed comparison of the jobs actually being contested, the work observed and an explicit decision status.
2. [My Depth Calls](../foundation/templates/position_battles/my_depth_calls_template.md), Stone's editable answer, allowing role appointments, meaningful tests, deferrals and a separate note to Caldwell without pretending that a coaching choice executes a cut.
3. [Depth Chart](../foundation/templates/position_battles/depth_chart_template.md), the phase's readable **derived** output from the single current depth owner, linked to each actual individual battle resolution.

### Supporting documents

4. [Individual Battle Closure](../foundation/templates/position_battles/battle_closure_template.md), the one-event result material that belongs in that battle's own original card.
5. [Implementation and Validation Specification](#1-design-contract-and-the-three-pages), authority, 2011 CBA contact rules, temporal controls, source ownership, state flow and **68 proposed tests**.
6. [Worked Jacksonville Example](examples/position_battles_jacksonville.md), full three-page retrospective from the established 2014 camp with six separate contest links, plus 2015 date-only setup.
7. [Research and Source Register](position_battles_research.md#training-camp-and-position-battles-2011-cba-and-contemporary-source-register), original CBA, period NFL/Jaguars reporting and canonical repository sources.
8. [Repository Assessment and Blockers](position_battles_research.md#training-camp-position-battles-rigorous-repository-assessment-and-blockers), what works and precisely what remains unimplemented or unsupported.

### Unchanged owners

The existing `foundation/templates/position_battle_card_template.md` and individual 2014 battle cards remain the canonical case-specific evidence/result model. The camp staff plan and training report own instruction and actual observed work. The team depth owner owns current assignments. Caldwell's roster cuts and waiver results stay at their own transaction owner. The shared consequential-event insert/response process and requirement for one separately dated result per event apply during camp exactly as during any other phase.

**Next separate workflows:** Every Preseason Game; Final Roster Cuts.

## 1. Design contract and the three pages

Reuse `runtime/decisions.py` key `camp` with exact titles:

- `Position_Battle_Report.md`: the staff's current, evidence-anchored briefing, materially revised as new legitimate findings appear. Published at `runtime.decisions.folder('camp', Y)`, resolving to the appropriate `career/Y/Training_Camp_and_Preseason/` folder. Each issued edition is immutable and the current entry points to its latest edition.
- `My_Depth_Calls.md`: a genuine editable answer from Stone (or the holder of depth authority in a different job). It may set initial groups, rehearsal rotations, packet roles, current depth, temporary injury replacement and final named contests. It must allow an explicit "not decided; next test" result. Do not auto-fill it from a staff recommendation.
- `Depth_Chart.md`: a **rendered result** of Stone's actual decisions, never a second mutable depth register. It follows the authority in `career/Y/Team_Operations/Team/Depth_Chart/depth_chart.md` and the underlying system depth state; it links each individually resolved contest to its dated individual card owner, preserving prior decisions. If no call is made, no changed roster or role appears.

`Position_Battle_Report` is not a transcription of each individual contest card. It presents only the important comparisons and choices for Stone at the current date. The detailed work and process belong under the camp `training_report.md` and the actual games, one complete comparison per dedicated position-battle card. Nothing invents a competing third annual player evaluation. The annual opening assessment carries dated updates; final annual assessment follows the season review.

## 2. Authority and real football boundaries

| Decision | Final authority in Stone's current Jacksonville appointment | Correct treatment |
|---|---|---|
| Start, rep groups, playing roles, X/Z/H, nickel/dime, snapper, return units, current depth chart | Alex Stone (job rows 9, 10, 11) | Stone decides personally or under a **previously adopted** standing instruction. Staff can teach and recommend. No silence-to-approval. |
| Practice workload within lawful CBA limits | Alex Stone, with performance/medical/facility consultation | Staff carries routine implementation; Stone is not prompted for every ordinary drill. |
| Players under contract, trade, veteran signing, waiver, release, 75/53 compliance, practice squad | David Caldwell (rows 3, 5, 7, 20) | Stone provides actual football evaluations. A depth call is not a release or automatic guarantee of a roster spot. |
| Diagnosis, independent hold, restrictions, return-to-participation | Qualified medical staff (rows 15, 16) | Medical availability limits work; neither coach nor GM can invent a clearance. |
| Assistant coach appointments | Stone within adopted budget (row 2) | Changes to staff only on recorded decisions, not automatically imported from real 2015 Jaguars. |

Stone's standing 2014 coaching commitments, when still operative, include: meaningful first- and reserve-group opportunities with varied combinations, a deliberate inside-run and protection test, connected front and coverage, concise corrections with later retests, situation/clock operation, real special-teams jobs and no punishment masquerading as a conditioning standard. None guarantees equal snaps, development, performance or a coaching grade. `career/Stone/Coaching_Profile.md` and the current job record govern any 2015 revision. In 2014 Stone calls offense and defense; Tice coordinates offense, Crennel prepares defense and transmits Stone's calls, Westhoff runs special teams. Do not carry staff assignments into 2015 without the career handoff.

## 3. Historical 2014 and 2015 calendar, CBA and practice law

### Original 2011 CBA Article 23, not later agreements

Use the August 4, 2011 NFL–NFLPA agreement, **Article 23 §6** (printed pp. 140–141; verify section numbering before implementing) and its predecessor Article 21 for spring. Its camp sequence:

1. First *club preseason training camp day*: medical exams, meetings, classroom instruction, permissible conditioning; no footballs, protective shirts or helmets, offensive/defensive walk-through, individual technique teaching or team drills; a conditioning test must be reasonable and cannot be imposed solely to punish an out-of-shape player.
2. Days two and three: no pads or contact. These days can have lawful football instruction and ordinary practices within limits.
3. Days four onward: at most **four total hours of on-field activities per player per day**, no more than **one padded practice** daily, padded session no longer than **three hours**; if there is a second on-field session, only a nonhelmet walkthrough within the remaining time, with a **three-hour break** after the first practice. Team scheduling must also meet required days off, treatment and club-specific safety rules. A completed preseason **game** is a distinct contest, not a camp-practice drill.
4. Players need the correct camp report eligibility and actual medical instructions. An eligible contracted player's reporting is different from a rookie with an unsigned deal, an authorized tryout, a reserve-list player or someone not under club control. A stated right to practice is not proof of participation.
5. Contact in padded practice is bounded by the coach's lawful controlled-contact instructions. Do not silently upgrade every padded period into full tackling to the ground or a competition against an outside NFL team.

**Important calendar difference:** 2014 Jaguars rookies reported July 21, veterans July 24, team first practiced July 25, had first full pads July 30, and recorded an August 2 scrimmage. These events already happened in this career; older 2014 camp cards keep their written chronology even where the historical open-day schedule later proved imperfect. The 2015 historical calendar names eligible special reporters July 27, other players July 30, practices July 31 onward, an August 4 day off, August 5 first **full** pads, an August 8 stadium scrimmage, August 9 off; initial posted schedule ends August 12. The 2015 preseason opener is August 14 vs Pittsburgh, then August 22 at NY Giants, August 28 vs Detroit, September 3 at Washington. Those are public calendar anchors, not played Stone events. Shoulder pads on August 2 (real club) and full pads August 5 are separate facts. The first *eligible* padded day does not compel a team to use pads on it.

The 2015 reduction deadlines are September 1 before 4 p.m. ET to 75, September 5 before 4 p.m. ET to 53. They belong to Caldwell's distinct cut workflow. The preliminary 90-player camp roster limit and any contemporaneous special exemptions or exempt statuses require a **dated legal roster check**, not a blanket assumption that every roster lists 90 or that every player can dress.

### Day and announcement gate

`career/2015/Calendar.md` and `library/2015_historical_calendar.md` hold club dates and publication sources. July 7, 2015 publication verifies initial practices and breaks. At the October 5, 2014 simulator point, these research entries can be used to design future output but cannot be introduced as already-announced camp details to Stone unless their real release date had arrived or an independently dated internal club scheduling decision is established. Avoid relying on retrospective articles about real 2015 starters, hires, preseason injuries, performance or roster cuts. Historical league rails only govern other clubs' specified player movements at their public dates, not the simulated Jaguars' draft class, depth, staff or health.

## 4. Competition eligibility and state machine

A *battle* is opened only from an actual dated authority/evidence record satisfying all three predicates:

1. Named, precise football job genuinely contested, such as **first-team left guard beside the named center** or **long snapper for Westhoff's punt and place-kick operation**; a roster spot, fallback role or formation alignment alone is not always a battle.
2. At least two legally available or conditionally eligible **actual candidate people** under club control or authorized participation, with each candidate's limitations recorded. A medically unavailable player may remain a candidate but cannot be scheduled unlawfully.
3. An actual comparative coaching intent and real available opportunity to examine the relevant assignment; not just an unassigned roster vacancy, player requested workout, camp speculation or an assumed competition to create drama.

Proposed technical statuses: `OPEN`, `PROVISIONAL`, `CLOSED`, `WITHDRAWN`. A provisional role choice does not necessarily close a live contest; a closed competition must point to an actual Stone answer and its effective date. Each record references a unique event identity, eligible candidate set, canonical spot, first-group starting point and sources.

For each actual contested position, keep ONE individually owned readable document in `career/Y/Training_Camp_and_Preseason/Position_Battles/{Offense|Defense|Special_Teams}/{position}/{spot}.md`; use `foundation/templates/position_battle_card_template.md`, not a parallel battle-card format. This new package's individual-closure reference covers the required result material within that same card. A contest is not closed by silently removing it from the open list. Retain dated original evidence and status history. Do not reopen the six 2014 cards after August 30.

At each legal observation: add the provenance-linked finding to the authoritative camp `Training_Camp/staff_plan.md` (intended work) versus `Training_Camp/training_report.md` (actual work), and refer to it on the battle card. For a preseason game, read its own `Preseason_Games/Game_XX/` completed `Preseason_Game_Report.md` or preserved 2014 `output.md`, plus participation data if available. The source must support assignment attribution. If the game record shows only a sack *slot*, do not invent a failed punch or busted protection by a named player.

## 5. Football evidence and fair comparison rules

The meaningful record for each candidate and question: exact date, work form (unopposed, nonpadded, padded controlled contact, scrimmage, external preseason game), first or reserve group, adjacent blockers and receiver/back group, defensive opponent and alignment, coverage help/pressure design, assignment actually asked, intervention from staff, observed result and whether the cause is established. Where a sample has no target, protection rep, rush or fault assigned, explicitly report that it failed to test the requested skill. Statistics (including sacks and catches) are evidence of a play, not an automatic personalized grade or a direct counterfactual about a player's NFL ability.

Use comparable contextual opportunities when lawful and sensible, but **do not force mathematically equal rep shares** that ignore practice teaching, availability and the game plan. A late entering reserve can supply important evidence of cold operation that the starter never faced. Cross-training at a second position does not start a new battle until the separate job actually becomes contested. A player competing at WR1 and WR3 gets one personal evidence history and two independent role comparisons.

No universal performance win points, repeating elite/plus/etc grades, simulated 10-point labels, arbitrary trust bars, automatic development gains, automatic rookie failure or guaranteed "earned" leap. Personnel-grade permissions in the canonical annual-card method do not license unsourced new camp numbers. Coach decisions under mixed evidence are allowed, but the report must label the decision as Stone's judgment rather than manufactured proof.

## 6. Issue, decision, resolution and rendering lifecycle

1. Read actual active simulated date, career job, roster rights, medical status, current depth and active playbook. Do not load real future 2015 Jaguars' transactions, final outcomes or performance as if they were career facts.
2. Obtain actual settled spring reports and latest camp/game evidence, including any pending comparison promised from a prior block; no unplayed session generates facts.
3. Validate each contest against its exact job and participants; when valid, create one card under the existing by-unit/by-position path. Preserve open/conditional status and first-group source.
4. Build the `Position_Battle_Report.md` from the *as-of* owner facts, organized by useful decisions, with the established shared action-insert section only for genuinely separate consequential events. Save an immutable issued edition. An informational event reissues only when it materially changes a pending choice, per `docs/event_inserts.md`.
5. Stone fills `My_Depth_Calls.md`; the compiler checks names, current eligibility, package, medical and season, and whether he is making a decision or explicitly deferring. It must not force closure or silently adopt a coach's view. Persist the exact answer and its issue date.
6. Commit Stone's actual depth or rotation instruction at the authoritative depth owner, with the respective dated decision in the domain's roster-decision owner as applicable. If multiple positions are decided simultaneously, the chart is written once while each contest gets its *own distinct dated close* in its individual card. Reject duplicate owners or conflicting role assignments.
7. Build `Depth_Chart.md` as a read-only phase view from the authoritative team depth chart, current roster, medical constraints and per-battle dated resolutions. Validate **byte-equivalent football assignments** against the same current depth facts. Show open contests as open, not winners.
8. If Stone recommends a cut, log his recommendation for Caldwell; the actual cut, reserve status, waiver and signing each close under the *Caldwell-owned* transaction files and the separate Final 53 workflow. A cut can change the candidate pool but cannot retroactively prove a training outcome or automatically choose a replacement starter for Stone.
9. Every other individual event (including rejected player contract negotiation, refused trade, unsuccessful coach pursuit or later waived player) resolves on its proper simulated date in its one owning file. One shared `My_Responses.md` does **not** mean one shared event-result file. The phase's index and result page may link them, never stand in for them.
10. Any newly communicated medical restriction constrains the lineup at the instant legally required; it does not backdate an earlier practice nor change the appointed role unless Stone decides. Return-to-activity stays with medical staff.
11. A legitimate later change to a closed depth role is a *new dated Stone adjustment*, not a rewrite of a past August comparison. Historic game inputs, old closed battle cards and Week 5-and-earlier content stay intact.

## 7. Proposed technical integration points

| Repo component | Existing capability | Required behind-the-scenes change |
|---|---|---|
| `runtime/decisions.py` | `camp` registry pages, `implemented=False`, destination under `training_camp_and_preseason` | Implement page issuer/response compiler/result renderer reusing registry, not another three-page system. Test `PLACES['training_camp_and_preseason']` through `runtime.seasons.SeasonPaths` after resolving the `preseason` legacy alias and parent. |
| `runtime/decision_queue.py` | `depth_and_roles` class; no specific open-battle revision/close lifecycle | Add properly scoped gates for a Stone-required *role decision*, with deadline only when genuinely needed. Open battles do not freeze unrelated league games. No "silence means keep incumbent" substitution. |
| `runtime/season_layout.py`, `runtime/seasons.py` | Central folder map and system/page split | Resolve all camp, battle, depth, event, game, issued-edition paths through map. Do not hardcode 2015 in runtime writer code. |
| `Training_Camp_and_Preseason/Training_Camp/` | Staff plan, authoritative report and dated findings | Add legal activity and provenance checks, not a replacement overall camp result. Camp report is not the same as the `Depth_Chart` phase result. |
| `Training_Camp_and_Preseason/Position_Battles/` | One card per actual spot with 2014 full evidence | Add per-spot dated closure markers, preserving original established card history. Never regenerate 2014 closed decisions from a new model. |
| `Team_Operations/Team/Depth_Chart/` | Single current role order and chronology | Apply only Stone's adopted legal instruction, then render both the primary chart and phase result from one stored fact. Later team changes remain dated, not rewritten past. |
| `Team_Operations/Team/Roster/`, `Roster_Decisions/` | Player control, cut owner, dated Stone instruction | Expose roster/legal status and separate Caldwell cut result; cross-check the final 53 process without making camp do it. |
| `Preseason_Games/Game_XX/` | Four closed 2014 game reports and session outputs | Read independently closed games only; 2015 preseason workflow needs its own engine release and plan, not an automatic camp draw. |
| `docs/event_inserts.md`, `runtime/decisions.EVENTS` | Shared insert, response journal, per-event final result | Route real events into active camp briefing, preserve revisions, and enforce one dated owner per resolution. |
| `scripts/validate_repository.py`, `runtime/clean_pages.py`, `scripts/render_annual_record.py` | Coach-page checks, annual index and event metadata | Enforce evidence cutoffs, unique battle owners, per-event output existence and current-chart equivalence without breaking old pages. |

The **critical missing resolution capability** is a generalized lawful practice/position-competition evidence process. The repo's 2014 reports are closed observations, not proof that an August 2015 practice resolver exists. Implement a deterministic, auditable, protagonist-blind approved procedure or import actual expressly observed facts; do not fabricate winning performance to fill a predesigned report. The decision and validation architecture can be implemented separately while this football evidence method is held as a blocker.

## 8. Regression tests proposed, not executed

### Era calendar, camp contact and safety

1. 2015 rookies/quarterbacks/first-year players have their July 27 conditional report route; ordinary veterans July 30; these dates are not automatic attendance.
2. The published July 7, 2015 club camp schedule is not presented as already public in the October 2014 head-coach briefing.
3. July 31 first practice, August 2 shoulder pads, August 5 full pads and August 8 stadium scrimmage are not conflated.
4. August 4/9 announced days off cannot become scheduled compulsory team practices without a separately lawful and recorded amendment.
5. 2015 camp does not import the real Jaguars' 2015 player evaluation, injury, personnel or starter.
6. Day-one camp session containing helmet, football, football play or team drill is refused under the 2011 CBA.
7. Day-two or day-three padded/contact session is refused.
8. Permitted non-padded group and team work on legal later days is accepted.
9. Only one padded practice per day per player can be committed.
10. A second daily session is a nonhelmet walkthrough within four combined on-field hours.
11. A padded practice longer than three hours is refused.
12. A second practice with less than the required three-hour break is refused.
13. An illegal full-contact tackle-to-ground is not authorized merely because practice is labelled "padded"; actual instruction and period govern.
14. A completed preseason game is accounted as its own actual game record, not an OTA or padded camp-practice entry.
15. Camp roster count and status are checked against the 2015 era's 90-player rules and exemptions, not an assumed actual attendance count.
16. Medical staff's uncommunicated or projected clearance never qualifies a player for contact.
17. A medically excused absence or a lawful contract hold is not classified as low effort or a lost battle.
18. Summer player-directed preparation is not represented as a coach-run June/July team practice.
19. The 2014 closed camp practices and reports remain byte-immutable through the Week 5 cutoff.
20. The 2014 camp historical off-day discrepancy is flagged for old-record research rather than silently shifting a completed practice date.

### True competition and football evidence

21. A roster vacancy with no two genuine contenders creates no battle card.
22. A cross-training look for a reserve player creates no fictional competition unless the target job itself is contested.
23. The program refuses to compare a name absent from the club's lawful participants.
24. A medically out player can stay an identified candidate without appearing in forbidden contact reps.
25. Same player's X/WR1 and Z/WR3 contests are distinct role cards, not two annual player assessments.
26. A simple QB1 carry-forward with no named challenge creates no mandatory fake quarterback competition.
27. One corner has 30 reserve reps and another 12 starter reps; no direct numerical "winner" is inferred without opponent/support context.
28. A receiver with no target in one preseason series is not assessed as a failure.
29. An interception thrown toward an X receiver does not become his route error without charted evidence.
30. A sack charged to a right-tackle *slot* does not automatically identify the individual technical failure.
31. A QB whistle at depth in a controlled padded rep is not entered as an actual game sack.
32. Correct box-call identification in no-pads work is not evaluated as full-contact anchor.
33. A successful padded combo block with a coach reset is distinguished from an independent series answer.
34. A pass-rush win with an open escape lane is not treated as identical to a rush preserving contain.
35. A linebacker covering a back in OTAs is not declared to have won a full-contact matchup.
36. Special-teams snap, kicker miss and protection faults are attributed to their correct operation sources.
37. Forty recorded specialist snaps with no fault for either candidate permit a Stone choice without a false "winner by accuracy" claim.
38. Two candidates with different partners have the differential exposure recorded, not erased from the brief.
39. In the absence of a permitted evidence resolver, an unplayed practice produces no invented technique win, injury, improvement or grade.
40. A player named in a 2014 closed battle is not automatically a 2015 contested candidate.

### Stone decisions, roster boundary and individual outputs

41. `Position_Battle_Report.md` shows the coach's dated position judgment and explicit evidence; never invents a coach quotation.
42. `My_Depth_Calls.md` is editable and accepts full natural football reasons, not a rigid numeric rating survey.
43. The user may explicitly defer a contested spot to a named next look; no automatic incumbent award from silence.
44. A role change consumes only the player, legal assignment and Stone authority; it does not sign or waive the candidate.
45. `Depth_Chart.md` cannot show a newly chosen starter before Stone's adopted answer.
46. A coach's first-group trial in practice never becomes an automatic final depth-chart award.
47. A 2015 coaching departure changes the attribution; 2014 assistants are not silently re-employed.
48. Caldwell's actual cut can remove a candidate from eligible assignments; it must have its own dated transaction record and not be converted into a Stone cut.
49. A roster cut alone cannot set a new named starter without a valid Stone depth decision or applicable prior standing role rule.
50. Stone's medically limited player cannot be placed in a game-active role contrary to communicated restrictions.
51. Six independent battle closures on the same date yield six separately readable results under six card owners plus one linked phase view.
52. A position battle result can explicitly say there was no evident separation but the coach chose based on continuity or the roster situation.
53. The 2014 August 30 Cain/Kreiter outcome is not misdescribed as superior snapping by Kreiter; Caldwell's release of Cain and Stone's depth designation remain distinct.
54. The 2014 WR1 closing with Nicks out after August 28 is not misdescribed as Adams winning every press matchup.
55. A battle that ends because the role vanishes is closed or withdrawn without a fake winner.
56. A reopened role after a later roster change is a new dated instruction; the old 2014 card keeps its evidence intact.
57. Two actual independently rejected trades during camp get two separate dated trade result files, not one combined paragraph in the Depth Chart.
58. A failed assistant hiring pursuit during camp retains its own dated staff result, even with no appointment.
59. Each open event blocks only a dependent transaction or actual roster/game lineup, not every unrelated practice.
60. Every individual completed event output appears in that period's chronological index as its own link and does not wait for camp closure.
61. Event `id`, source cutoff, owner and resolved date are consistent between its source and linked individual output; duplicate owners are refused.
62. Old completed game reports and previously frozen pregame plans are not regenerated or edited to incorporate a new camp page.
63. Changing the order of the six battle cards in the summary cannot change the role assignments, frozen resolution or game receipts.
64. The primary team depth chart and phase `Depth_Chart.md` render the same role owner and are checked for consistency.
65. An after-the-fact page rebuild never reruns a game, prospect acquisition, injury or practice-resolution process.
66. Coach-facing pages pass `runtime/clean_pages.py`: no technical codes, file paths, schema jargon, placeholders disguised as results or software maintenance notes.
67. A missing 2015 season opening/handoff prevents a real 2015 camp and prevents pre-filling it from 2014 roster or real 2015 Jaguars.
68. With no actual battles and no pending depth decision, the brief legitimately reports that no competition requires a call, without creating one.

## 9. End-to-end acceptance scenario

A legitimate 2015 position contest is *first* created only after Stone has reached 2015 camp on his own results, lawful club participants and two real contender roles with a dated coaching instruction. Session X supplies controlled-contact work; session Y may qualify or contradict it; the opening cards supply prior evidence. The current battle card is updated with date and situation, without authoring a universal player grade. The issued camp brief shows a football comparison, not a fictional "100 point" race.

If Stone chooses the starter, his adopted `My_Depth_Calls` updates the actual depth owner and creates **one named closure in the battle's original card**, which can be read alone and which the generated Depth Chart links. Caldwell may or may not later make a different cut/contract decision; if he does, it gets its own result. An active trade proposition can be inserted in the brief and answered in the shared response journal, but no trade happens until Caldwell and the counterpart actually close it. The final report's table links that trade's own file. Reopening the brief or re-rendering the current chart cannot change the event or produce a second owner.

## 10. Realism limits and blockers

1. **Missing generalized camp/practice evidence resolution**: 2014's historical record is detailed, but there is no proved game-quality process that can create new, lawful 2015 practices; approval required before events are resolved. Until then, the workflow can accept a valid user plan and record open questions, not assert outcomes.
2. **Current depth versus phase presentation**: design requires one machine source of truth for depth and distinct individual battle closures, with build-time equivalence tests. A second mutable `Depth_Chart.md` would create contradictions.
3. **Separate contested-role outcomes versus six-at-once dated roster note**: the old 2014 records have individual cards but a combined August 30 closure marker in `roster_decisions.md`. Retain that frozen history. From the new system onward, one output per resolved contest is mandatory; the old combined marker must not be used as precedent to aggregate future decisions.
4. **2015 roster and medical unknown**: no prospective true-contender list, future injury, cut, camp win or replacement is valid yet. The historical 2015 Jaguars' publicly reported competitions are examples of NFL practice, not Stone's roster.
5. **Public camp calendar vs club choice**: July 7 announcement does not prove every practice was held or a player participated; initial announced practice list ends August 12. Do not invent the remainder.
6. **Authority crossover**: conditional lineups after cuts require a Stone answer and a separate Caldwell transaction. Automatic "best 53" selection or medical clearance is prohibited.
