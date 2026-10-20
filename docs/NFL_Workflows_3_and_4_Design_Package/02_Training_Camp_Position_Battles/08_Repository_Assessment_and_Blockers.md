# Training camp position battles: rigorous repository assessment and blockers

**Inspected:** GitHub `Alex-Oss222/football-career-sim`, default branch `main`, tree/commit `75fd41fbfc5ed0363d9f6cb68b5bef37a6583f24`, October 20, 2026. Read-only source inspection. No pull request, commit, career clock movement or 2015 depth call has occurred in this package.

## What already works and should be preserved

1. **Documented authority:** `state/current_job.json` grants Stone depth-chart, package roles, lineups and practice work; Caldwell executes acquisitions, draft decisions, contracts, cuts and transactions; medical staff own return status. The four-year guaranteed head-coach contract and standing delegation remain canon. The coach does not get a power to cut a player simply by writing a depth chart.
2. **Actual battle evidence and dated sources:** Six full 2014 battle cards with substantive evidence, four real completed preseason game outputs in the simulated career and an unusually detailed camp training report. The individual 2014 cards are under the correct `Training_Camp_and_Preseason/Position_Battles/` tree, all closed August 30. The old report has no general claim that a no-target series identifies receiver quality. No 2014 battle is to be reopened for design aesthetics.
3. **Current depth owner:** `Team_Operations/Team/Depth_Chart/depth_chart.md` reads as the living current assignment, with the actual role chronology in Stone's `Roster_Decisions/roster_decisions.md`. The older 2014 roster reduction belongs to `final_roster_cuts.md`, not to a coach-comparison card.
4. **Specific coaching method:** `career/Stone/Coaching_Profile.md` defines his pace, split-group opportunities, sustained drives and corrections, and the current job record protects standing instructions. Those practices can be used as already-adopted intent, not automatic success.
5. **Existing presentation approach:** `foundation/templates/position_battle_card_template.md`, `foundation/templates/training_camp_and_preseason/training_camp_report.md` and `docs/camp_and_preseason_reports.md` already distinguish teaching, controlled contact, support, genuine field execution and preseason. Reuse them rather than introducing alternate grades.
6. **Three-page workflow is registered:** `runtime/decisions.py` already names `Position Battle Report`, `My Depth Calls`, `Depth Chart`, key `camp`, but `implemented=False`. The folder map maps it into the camp/preseason season folder; confirm the alias/parent route with a targeted test.
7. **Dated events and clean pages:** `runtime/events.py` and `scripts/render_annual_record.py` support each event at its rightful owner; `docs/event_inserts.md` fixes one separate output per resolution and immutable briefing editions. The current clean-page rules forbid technical IDs, system paths and administrative notes on the coach's pages.

## Actual design and integration blockers

| Blocker or ambiguity | Evidence, consequence and required action |
|---|---|
| No demonstrated **general-purpose 2015 camp practice resolver** | A completed 2014 narrative is not a reusable performance engine. No credible new result should be generated from “run inside run drill.” Before the career executes a camp, approve or verify an event-resolution procedure that honors actual source conditions, participants, medical law and protagonist-blind results. Until then, report unknowns rather than invented performance. |
| No fully implemented `camp` renderer/decision compiler | `runtime/decisions.py` lists the pages, but the `implemented` flag is false. Build issued brief -> Stone's natural instructions -> role-state/individual close -> derived Depth Chart, with pre-action validation and immutable issue history. |
| Generic queue cannot independently close multiple actual contests | `runtime/decision_queue.py` has `depth_and_roles`, but no per-battle statuses, issue cutoffs or first-group/role dependency. Implement *only real* stops when Stone's answer is needed. Silence cannot appoint an incumbent. |
| Unique result owner for independently resolved battles | The old 2014 August 30 `roster_decisions.md` combines a dated event marker for six decisions while each individual card carries its own readable conclusion. Preserve old history. New closures require one dated event output per separately concluded battle, at the card or dedicated owner, and an index link per outcome; reject a single omnibus report as a replacement. Ensure one identity per event to avoid annual-index duplicates. |
| One authoritative depth chart | `Depth_Chart.md` is the requested result page name, but an additional independently editable depth table would contradict the living depth chart. It must be rendered from the same stored role facts as `Team_Operations/Team/Depth_Chart/depth_chart.md`. Freeze old games and retain dated revisions. |
| Camp stop vs roster cut split | Stone can assign one long snapper despite neither candidate separating on practice performance. Caldwell can release the other; the release needs its own dated transaction and the chart must be revalidated against remaining rights. A Stone depth call never auto-writes an NFL roster limit, contract or waiver. |
| 2015 participants unknown | The season is still October 5, 2014. End-of-season roster, 2015 re-signings, draft choices, compensation, coaches and medical/eligibility changes are future. Do not copy real 2015 Jaguars' depth competition or pre-award a starter. |
| Historical 2015 calendar announcement timing | Date research exists, but the July 7, 2015 public practice schedule cannot appear in an October 2014 in-world document as if already announced. The 2015 initial posted camp sessions only run through August 12. |
| Legal and injury practice guards | Use the **2011** agreement, not current CBA transcription. Verify first-day conditioning/football prohibition, days two and three, padded/second-session limits, days off, personnel and medical eligibility; reject disallowed activity before making a report. |
| Attribution and unbalanced comparisons | Four 2014 preseason game outputs have meaningful snap and sack data but missing per-player route/rush film details. Keep “slot” and “responsibility” distinct. A fair competition may involve unequal work because the team needs different combinations; quantify only recorded exposure and explain the difference. |
| Historical-source conflict in 2014 camp | 2014 battle README notes an off-day discrepancy. Leave the historical record unchanged. A future provenance/reconciliation action, if explicitly approved, may resolve the discrepancy without quietly moving completed practices. |
| Cross-workflow sequencing | The camp phase can overlap the four preseason games and August personnel decisions. A named next game is an opportunity only; its Game Plan and Game Report are the separately designed preseason workflow. Roster reductions remain the separate Final 53 workflow. The camp report may only consume actual closed, attributed evidence. |

## No false resolutions

- Do not generate a WR1 battle for the real 2015 Jaguars' publicly known players. In Stone's October 5, 2014 career, those 2015 roster moves and draft choices have not happened.
- Do not “award” an offensive lineman after three clean non-contact OTA reps and claim he defeated an NFL defensive tackle.
- Do not make 40 fault-free snapper reps mean that the one chosen has a higher fabricated snap-accuracy rating.
- Do not force an open contest to close after a single preseason game when Stone has not answered.
- Do not convert a cut recommendation into Caldwell's executed waiver.

## Pre-execution acceptance bar

Before implementing a 2015 camp session: correct legally eligible roster and medical snapshot, active coach/assistant assignments, season-valid playbook, correctly released camp calendar, valid first-day and padded scheduling, Stone's actual plan, auditable procedure or actual independently recorded observations, individual battle cards, single source of truth for depth, specific pending user decisions, separately owned completed events, and passing clean-page/annual-record/season-handoff tests. This package supplies the document contract but does not assert those runtime capabilities exist.
