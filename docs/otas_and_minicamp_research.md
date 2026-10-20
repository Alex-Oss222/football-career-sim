# May–June OTAs and Minicamp: research and repository assessment

The research register and the repository assessment uploaded by the user on October 20, 2026 with the [May–June OTAs and Minicamp design](otas_and_minicamp.md), as uploaded.

## May-June OTAs and minicamp: period-source register

This document separates the historical labor and schedule rules from outcomes in the simulator. A date in a historical source is a calendar fact; an actual player attendance, coaching decision, injury, report or cancelled practice must arise from the career's own dated owners. Research was checked against the 2011 agreement itself and 2013-15 contemporary team/league reporting. The earlier completed 2014 career records are not retrospective real Jaguars history.

### Original governing labor document

**NFL and NFLPA, Collective Bargaining Agreement, August 4, 2011** (the 2011-20 agreement, not the 2020 CBA): https://nflps.org/wp-content/uploads/2012/05/collective-bargaining-agreement-2011-2020.pdf

| Provision | Printed pages / PDF pages (zero-based) | Controlling finding |
|---|---|---|
| Article 21 §1 and §2(a) | 131-132 / 145-146 | Work and classroom voluntary except Article 22; official nine-week program, no weekend workouts, four per week per individual; pre-program coach instruction restricted. |
| Article 21 §2(b)(ii)-(iii) | 132 / 146 | Phase Two separate work, Phase Three maximum ten OTAs, 3+3+4 weekly allocation, no one-on-one opposed work or contact in Phase Three. |
| Article 21 §2(c), §3 | 133 / 147 | Filing not later than 21 days before start; tendered/expired UFAs require valid participation agreement; 2015-16 daily workout minimum $195. |
| Article 21 §5(b)-(c) | 134 / 148 | Non-OTA activity: four hours facility, 90 minutes field; on-field sessions filmed; not OTA-specific hours. |
| Article 21 §6 | 134-135 / 148-149 | Organized pre-camp coach football work barred after program, with narrow five-day exceptions. |
| Article 22 §1-2 | 138 / 152 | One mandatory veteran minicamp, physicals Monday and legal practices Tuesday-Thursday with Friday off; 3.5-hour daily field and 2.5-hour primary-practice maxima, second practice walkthrough only. |
| Article 22 §7 | 139 / 153 | Rookie football development and special post-draft rookie minicamp weekend have separate rules. |
| Appendix G | 278 / 292 | OTAs: six hours total per player daily; two hours on field, helmets allowed, pads prohibited, no live contact. |

Original text and page images were checked directly. Later NFLPA summary pages do not replace the 2011 document for period-specific obligations.

### Verified historical NFL/club reporting

1. **NFL, April 3, 2014, All-club 2014 offseason dates:** https://www.nfl.com/news/nfl-offseason-workout-program-dates-announced-0ap2000000339264 . Corroborates three phases, non-contact team periods and ten-OTA/mandatory-minicamp structure. Its generic rookie-minicamp calendar **must not** be interpreted as evidence of three practices in Jacksonville.
2. **Jacksonville Jaguars, April 3, 2014, 'OTA, minicamp dates set':** https://www.jaguars.com/news/ota-minicamp-dates-set-12840120 . Club primary source: May 27-29, June 2-3 and 5, June 9-10 and 12-13; June 17-19 minicamp, April 21 start.
3. **Jacksonville Jaguars, April 30, 2014, 'Jaguars open three minicamp practices':** https://www.jaguars.com/news/jaguars-open-three-minicamp-practices-12936883 . Confirms **two** actual announced rookie on-field days, May 16-17, and one public veteran-minicamp day June 19. Title counts public practices, not a three-day rookie minicamp.
4. **Jacksonville Jaguars, May 27, 2014, first OTAs:** https://www.jaguars.com/news/jaguars-2014-otas-bradley-likes-first-day-13064450 . Contemporary confirmation of legal 11-on-11 without pads and integration of rookies, **in the real Jaguars club only**. Player names and evaluations on that page are not Stone career evidence.
5. **Jacksonville Jaguars, June 17, 2014, minicamp account:** https://www.jaguars.com/news/2014-minicamp-strong-start-to-2014-minicamp-13157547 . Longer minicamp day and on-field walkthrough/team work contemporaneously explained; real Gus Bradley quotes are not Stone dialogue.
6. **NFL, May 15, 2015, 2015 offseason program report:** https://www.nfl.com/news/nfl-announces-dates-for-offseason-workouts-0ap3000000492887 . Jacksonville dates and official three-phase explanation, including April 20 program start and May 8-10 rookie minicamp.
7. **Sporting News, May 2015, 2015 OTA club calendar:** https://www.sportingnews.com/au/nfl/news/2015-nfl-minicamp-otas-schedule-offseason-team-by-team-players-report-training-camp/lm4bth1ug434162e5d5ybo3xm . Independent published reproduction: Jacksonville's ten listed OTA dates and June 16-18 minicamp.
8. **Jacksonville Jaguars, June 15, 2015, '2015 minicamp: What to watch':** https://www.jaguars.com/news/2015-minicamp-what-to-watch-15407029 . Notes the real club had nine OTAs, and states accurately that minicamp remains non-contact team work, not opposed individual blocking/coverage.
9. **Jacksonville Jaguars, June 18, 2015, 'Jaguars wrap offseason':** https://www.jaguars.com/news/2015-minicamp-jaguars-wrap-offseason-15423487 . Confirms the real club's completed three-day minicamp, **not** a simulated 2015 Jacksonville outcome.

### Repository sources inspected

- `state/05_Current_Season_State.md`: Oct. 5, 2014 Week 5 closed, Week 6 not played; therefore no 2015 participants or results exist yet.
- `state/current_job.json`: Stone's head-coach powers, staff chain, medical authority, 2014 April instruction and standing choices.
- `career/2015/Calendar.md` plus `library/2015_historical_calendar.md`: publicly reported 2015 dates and release gates; announced ten, real held nine distinction.
- `career/2014/Offseason_Training/OTAs/staff_plan.md`, `training_report.md`; `Mandatory_Minicamp/staff_plan.md`, `training_report.md`.
- `career/2014/Offseason_Training/Phase_One/`, `Phase_Two/`, `Rookie_Minicamp/` completed distinct sources.
- `foundation/templates/offseason_training/otas_report.md`, `mandatory_minicamp_report.md`, `rookie_minicamp_report.md`.
- `career/2014/Offseason_Training/stone_april_18_2014_decisions.md` and `career/Stone/Coaching_Profile.md`.
- `runtime/decisions.py`, `runtime/decision_queue.py`, `runtime/season_layout.py`, `runtime/seasons.py`, `runtime/events.py`, `runtime/clean_pages.py`, `docs/event_inserts.md`, `docs/rebuild_plan.md`, `docs/season_structure.md`.

### Uncertainties deliberately retained

- The actual earlier date on which Jacksonville's 2015 full OTA schedule was first communicated publicly was not established from the available club release history. NFL's eventual May 15 announcement is not evidence of publication in March or April. An internal club scheduling authorization must be recorded separately.
- The specific 2015 in-career filed workout schedule, eligible roster, unsigned tender participation agreements, injuries and staff are not established.
- The real 2015 cancellation that left nine held OTAs is documented, but the corresponding Stone-career cancellation **must not be imported**.
- General-purpose future spring-practice evidence resolution has not been shown implemented. Narrative text alone is not an auditable substitute.
- An individual's medical instructions, film receipt, readiness or knowledge cannot be inferred from a team-wide practice label.

## OTAs and minicamp: repository assessment and blockers

### Assessment

**Well supported as a design:** Jacksonville's spring archive provides formation-specific, assignment-specific evidence, delayed retests and consequences for camp. The existing templates already distinguish Phase One classroom, Phase Two unopposed work, separate rookie minicamp, non-contact veteran OTAs and mandatory veteran minicamp. Stone's powers and spring teaching/medical boundaries are well established.

**Not implemented as the proposed workflow:** `runtime/decisions.py` registers `otas` with the exact fixed three names, but `implemented=False`. The existing file system contains the 2014 plans/reports, not the proposed combined three-page decision lifecycle for a future active season. Nothing inspected proves an engine for generating new practice outcomes or closed OTA issue/plan/report transactions.

**Risk if implemented naively:** The third new page could copy every observation and become a second owner of practice evidence. Instead `OTA_Report.md` must be a meaningful **derived view** of two real phase owners, with enough observed football to answer Stone's question but no independent editable findings.

### Specific blockers and decisions for implementation

1. **No verified 2015 practice-event resolver.** Either add a bounded, frozen, neutral resolver with inspectable evidentiary mechanics or require independently provided observed session evidence. Never roll generic improvement or fill session reports from plan language.
2. **CBA calendar/attendance legality.** Enforce ten announced OTA slots versus days actually held, three plus three plus four phase-week limit, six-hour/two-hour OTA limit, separate physicals/minicamp limits, voluntary status, valid tender agreements and medical exceptions.
3. **Roster and staff as of each session.** End-of-2014 season and 2015 handoff have not occurred. A 2014 player/assistant cannot be automatically inserted into a 2015 scene just because his past page is available.
4. **Brief reissue and freeze.** `docs/event_inserts.md` requires immutable issued copies for consequential changes, not silently edited current briefs. Its live active view needs phase-scoped edition tracking; date and source cutoffs must remain available.
5. **Decision queue.** The generic `practice_plan` class has no OTA-close dependency. Implement the smallest legal phase blockers and let independent league or contract work proceed.
6. **Department result routing.** The active OTA report must link individual rejected, accepted or abandoned trade, contract and staff result pages. Those events are never deferred to the minicamp summary and never duplicated in the training folder.
7. **Open medical reports.** Unresolved treatment/return dates do not let a coach clear a player or put him in a period. Medical staff decide.
8. **Handoff:** The June minicamp close cannot authorize coached football through the summer; only the narrow Article 21 §6 exceptions are possible. Camp must reopen on its own actual schedule.
9. **Page hygiene:** Both new root phase pages and their saved editions need the clean-page rule, with machine identifiers and technical hashes solely in data or invisible validated metadata.
10. **Legacy immutability:** The 2014 ten OTAs, three mandatory-minicamp practices, dated observations and existing medical decisions have already occurred. Leave their bytes and historical claims intact.

### Potential conflict in older instructions

The 2014 spring archive records Stone excluding four players on unsigned tenders because a valid participation basis was not established for those players. This was an **individual 2014 legal/evidentiary decision**, not a categorical labor rule. The 2011 CBA allows certain unsigned-tender players and expired-contract UFAs to participate after invitation and a proper offseason participation agreement. A 2015 validator must check the agreement instead of importing the 2014 roster's exclusion for all such players.

### Completion boundary

This package supplies three full intended coach-facing Markdown pages and the supporting research, demonstration, implementation and testing plan. It makes no in-career choices, creates no actual 2015 practice, writes no GitHub file and claims no tests have been run. Implementation is blocked pending the matters above, not blocked from research/design.
