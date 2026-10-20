# OTAs and minicamp: repository assessment and blockers

## Assessment

**Well supported as a design:** Jacksonville's spring archive provides formation-specific, assignment-specific evidence, delayed retests and consequences for camp. The existing templates already distinguish Phase One classroom, Phase Two unopposed work, separate rookie minicamp, non-contact veteran OTAs and mandatory veteran minicamp. Stone's powers and spring teaching/medical boundaries are well established.

**Not implemented as the proposed workflow:** `runtime/decisions.py` registers `otas` with the exact fixed three names, but `implemented=False`. The existing file system contains the 2014 plans/reports, not the proposed combined three-page decision lifecycle for a future active season. Nothing inspected proves an engine for generating new practice outcomes or closed OTA issue/plan/report transactions.

**Risk if implemented naively:** The third new page could copy every observation and become a second owner of practice evidence. Instead `OTA_Report.md` must be a meaningful **derived view** of two real phase owners, with enough observed football to answer Stone's question but no independent editable findings.

## Specific blockers and decisions for implementation

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

## Potential conflict in older instructions

The 2014 spring archive records Stone excluding four players on unsigned tenders because a valid participation basis was not established for those players. This was an **individual 2014 legal/evidentiary decision**, not a categorical labor rule. The 2011 CBA allows certain unsigned-tender players and expired-contract UFAs to participate after invitation and a proper offseason participation agreement. A 2015 validator must check the agreement instead of importing the 2014 roster's exclusion for all such players.

## Completion boundary

This package supplies three full intended coach-facing Markdown pages and the supporting research, demonstration, implementation and testing plan. It makes no in-career choices, creates no actual 2015 practice, writes no GitHub file and claims no tests have been run. Implementation is blocked pending the matters above, not blocked from research/design.
