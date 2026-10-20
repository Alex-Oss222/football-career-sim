# Spring and summer designs: the April program to final cuts

**Status:** Uploaded by the user on October 20, 2026 and adopted. The April offseason program, the draft and OTAs are built in step 7 of the [rebuild plan](rebuild_plan.md); position battles, preseason games and final cuts in step 8. This page indexes the six designs, then keeps the two package assessments and the package README as uploaded.

| Workflow | Design | Research and repository assessment | Templates | Worked example | Built in step |
|---|---|---|---|---|---|
| April Offseason Program | [offseason_program.md](offseason_program.md) | [offseason_program_research.md](offseason_program_research.md) | [foundation/templates/offseason_program/](../foundation/templates/offseason_program/) | [offseason_program_jacksonville.md](examples/offseason_program_jacksonville.md) | 7 |
| NFL Draft | [draft.md](draft.md) | [draft_research.md](draft_research.md) | [foundation/templates/draft/](../foundation/templates/draft/) | [draft_jacksonville.md](examples/draft_jacksonville.md) | 7 |
| May–June OTAs and Minicamp | [otas_and_minicamp.md](otas_and_minicamp.md) | [otas_and_minicamp_research.md](otas_and_minicamp_research.md) | [foundation/templates/otas/](../foundation/templates/otas/) | [otas_and_minicamp_jacksonville.md](examples/otas_and_minicamp_jacksonville.md) | 7 |
| Training Camp Position Battles | [position_battles.md](position_battles.md) | [position_battles_research.md](position_battles_research.md) | [foundation/templates/position_battles/](../foundation/templates/position_battles/) | [position_battles_jacksonville.md](examples/position_battles_jacksonville.md) | 8 |
| Every Preseason Game | [preseason_games.md](preseason_games.md) | [preseason_games_research.md](preseason_games_research.md) | [foundation/templates/preseason_game/](../foundation/templates/preseason_game/) | [preseason_games_jacksonville.md](examples/preseason_games_jacksonville.md) | 8 |
| Final Roster Cuts | [final_roster_cuts.md](final_roster_cuts.md) | [final_roster_cuts_research.md](final_roster_cuts_research.md) | [foundation/templates/final_cuts/](../foundation/templates/final_cuts/) | [final_roster_cuts_jacksonville.md](examples/final_roster_cuts_jacksonville.md) | 8 |

## NFL head-coach career simulator: May–June and training-camp design handoff

**Design packages, not execution.** GitHub `Alex-Oss222/football-career-sim` was inspected read-only at `75fd41fbfc5ed0363d9f6cb68b5bef37a6583f24` on October 20, 2026. The career still stands at October 5, 2014 after the Week 5 game. Weeks 6–17 and any 2014 postseason results remain future, and neither 2015 spring nor 2015 camp was simulated. No GitHub change is included or recommended as already applied.

### Findings to enforce first

1. **2011 CBA, not a modern rewrite.** In the 2014–15 era, Phase Three OTC/OTA and mandatory veteran minicamp activities are non-contact. Seven-on-seven, nine-on-seven and eleven-on-eleven against an opposing group are lawful without contact; opposed one-on-ones and shells are not. The voluntary OTA and mandatory veteran camp rules differ. The actual 2011 CBA has separate daily-duration rules for ordinary non-OTA activity, Appendix G OTAs and Article 22 minicamp. Training camp begins with restricted day one and no pads/contact on days two and three, followed by one legal padded session per day under Article 23 time/rest limits. See both source registers.
2. **Use actual historical Jacksonville dates, not their outcomes.** 2015 OTAs were announced for May 26–28; June 1–2 and 4; June 8–9 and 11–12, with June 16–18 mandatory minicamp. The real club ultimately held nine OTAs, but Stone's simulated completed count is unknown. The initial 2015 camp public announcement on July 7 provides July 31 first practice, August 5 first full pads and August 8 scrimmage; the remaining exact daily camp sessions are not supplied by that publication. On October 5, 2014 Stone has not received a July 2015 public announcement.
3. **One observed source, one authority owner.** `Offseason_Training/OTAs/training_report.md` and `.../Mandatory_Minicamp/training_report.md` own their separately conducted football work; new `OTA_Report.md` summarizes and links without duplicating assessments. `Training_Camp_and_Preseason/Training_Camp/training_report.md` and game outputs own camp/game evidence. Each genuine battle card owns its own comparisons and eventual dated result. The team's current depth data own the chart, which the phase `Depth_Chart.md` renders. A staff recommendation is never a transaction.
4. **Authority is not optional.** Stone chooses practice, group opportunities, depth and staff under his contract and standing instructions. Caldwell chooses contracts, cuts, trades, acquisitions and the draft. Medical staff determine diagnosis and clearance. The 2014 staff list and player assignments cannot simply be projected into 2015 without the intervening career results.
5. **Events never aggregate.** An active phase briefing can receive several inserts, which can be answered on one shared response journal, but every separately concluded trade inquiry, rejected offer, unsuccessful hiring pursuit, player transaction or independent battle closure must have its one correct dated readable result at its own department/position-card owner. The phase view only links these files.
6. **No practice-result magic.** The repo contains detailed already-completed 2014 sessions, not a validated general procedure for generating future 2015 on-field observations. An approved protagonist-blind method or actual recorded inputs are required before any new result. No arbitrary scores, role promotions, guaranteed improvement, coach dialogue or medical clearance are allowed.

### What the two new design packages contain

- [`otas_and_minicamp.md`](otas_and_minicamp.md): `OTA_Brief`, `My_Install_Plan`, `OTA_Report`, an event-result reference, a full integration contract with **58 proposed tests**, evidence-anchored 2014 three-page Jacksonville illustration, source register, repository assessment and README.
- [`position_battles.md`](position_battles.md): `Position_Battle_Report`, `My_Depth_Calls`, `Depth_Chart`, an individual battle-result reference, integration contract with **68 proposed tests**, 2014 six-battle illustration, source register, repository assessment and README.

All placeholders in the coach-page templates are *authoring instructions* only. A deployed page includes actual verified and relevant football facts, not template brackets, technology labels or unknown figures disguised as facts. The specs are technical and intentionally separate.

### Precise six-workflow checklist

| # | Workflow | Research/template status | GitHub deployment |
|---|---|---|---|
| 1 | April Offseason Program | Previously completed design package | Not established by this work |
| 2 | NFL Draft | Previously completed design package | Not established by this work |
| 3 | May–June OTAs and mandatory minicamp | **Design package complete here** | Not installed here |
| 4 | Training Camp Position Battles | **Design package complete here** | Not installed here |
| 5 | Each Preseason Game | **Still remaining** | Separately design briefing, Stone's game plan, per-game report |
| 6 | Final Roster Cuts | **Still remaining** | Separately design Caldwell's roster-cut report, Stone's recommendations and Final 53 |

**Quality gate:** Both packages need dedicated runtime implementations and their proposed tests run on a separate, explicitly approved future GitHub change. Their current contents do not authorize the next simulation event.

## Research assessment and six-workflow design checklist

**Scope:** Design packages for the remaining two decisions: every preseason game and final roster cuts, based on `Alex-Oss222/football-career-sim` at GitHub `main` tree `75fd41fbfc5ed0363d9f6cb68b5bef37a6583f24`, inspected October 20, 2026. The career is at October 5, 2014, after simulated Jacksonville Week 5. This package is **not** a recorded coaching action, not implemented in GitHub, and not authorization to play a 2015 game or make a transaction.

### Assessment: what is supported

The club already has four completed **simulated** 2014 exhibition games with distinct frozen inputs, game outputs, injury results and preseason-only statistics. Those historical career results are controlled by the branch and remain unedited. The existing `runtime.preseason` compiler, `runtime.rotation` controls, production closer and validation tests supply relevant foundations. The prior eight-section preseason output already includes a story, real coaching analysis, complete generated box score and a cumulative review. The new three-page structure must retain their substance, not replace them with generic narrative or run a second result for one game.

The completed 2014 reduction to 53 documents a lawful **no-cut first deadline** when Jacksonville counted 74 contracted players against 75, then a separate reduction to 53, a next-day waiver process and individually recorded practice-squad agreements. Stone's depth calls and Caldwell's transactions were distinct. The six documented 2014 position battles closed August 30, not automatically after an exhibition performance.

### Assessment: CBA and historical calendar

- The **2011 collective bargaining agreement** and then-applicable 2014 practice-squad expansion, not modern roster or waiver rules, govern this period. Waiver exemption under Article 29 depends on **credited service**. Practice-squad exceptions under Article 33 and the 2014 agreement rely on **accrued seasons** and their distinct tests. No substitute based solely on years since draft is valid.
- The 2015 Jacksonville preseason schedule was announced by the club April 20, 2015: Pittsburgh at Jacksonville August 14, Jacksonville at the NY Giants August 22, Detroit at Jacksonville August 28 and Jacksonville at Washington September 3, each with the established kickoff. Publication date controls what can appear in an earlier briefing.
- The NFL's May 19, 2015 extra-point rule changes the kicked try to the 15-yard-line snap, leaves two-point attempts at the 2, and allows defensive two-point returns. The released 2014 preseason rules may not be reused unmodified for 2015.
- **September 1, 2015 before 4 p.m. ET** is the 75-player limit, before preseason game four on September 3. **September 5 before 4 p.m. ET** is the 53-player filing, with the September 6 noon waiver checkpoint and later practice-squad window. A single end-of-August reduction would be incorrect.

### Specific implementation blockers

1. In `runtime.decisions.py`, the two unimplemented decisions `preseason_game` and `final_cuts` use a shared path that currently resolves to the *parent* `Training_Camp_and_Preseason` folder. The new plans need kind-specific routing: four `Preseason_Games/Game_0N/` triplets and the separate `Roster_Decisions/` cutdown triplet.
2. `scripts/close_preseason_game.py` currently owns the older `output.md` rendering. The new `Preseason_Game_Report.md` must become the only reader-facing owner for **future** games while frozen 2014 output bytes remain unchanged. Existing statistics and event records must not be double-written.
3. The 2014 game release does not prove a valid 2015 released game environment. The 2015 rules, medical status, opponent rosters, personnel, rotation, fixture and gameplay inputs require their own readiness gates and date limits. The remainder of 2014 has not been simulated.
4. A new decision-queue block is needed for a particular preseason game freeze and close, while a separate event-specific gate is needed at 75 and 53. Unrelated personnel business should not block independent events; a real roster dependency must.
5. The current 2014 practice and roster documents are histories, not machine-writable 2015 outcomes. Individual medical, contract, waiver and signed-player dispositions must be legally verified, idempotent and stored at the correct source of truth.
6. The current 2014 examples are **not** scripts for 2015 player development, camp grades, other clubs' transactions or waiver outcomes. The 2015 roster is not available at the October 2014 simulated date. Training-camp work and draft/cap outcomes must actually occur before they can appear.
7. For every separately resolved matter, including one player's cut, a rejected trade, a failed waiver claim or an unsuccessful practice-squad pursuit, generate **one separate dated result**. Main phase summaries link each result. A two-person injury case or twenty-person cutdown must not collapse into one invented universal result.
8. Final roster ownership belongs to Caldwell. Stone owns team depth, playing roles and game-day inactives and can advise on acquisition and retention. Medical personnel decide clearance. The 53 does not determine the dressed 46 or appoint the next available player automatically.

The package spells out **56 proposed preseason-game tests** and **68 proposed cutdown tests**, plus acceptance scenarios. These tests have **not** been run against GitHub and are not a claim that the workflows have been installed.

### Design checklist

| Order | Workflow | Research and downloadable design | GitHub implementation |
|---:|---|---|---|
| 1 | April Offseason Program | Complete in prior package | Not established by this work |
| 2 | NFL Draft | Complete in prior package | Not established by this work |
| 3 | May–June OTAs and Minicamp | Complete in prior package | Not established by this work |
| 4 | Training Camp Position Battles | Complete in prior package | Not established by this work |
| 5 | Every Preseason Game | **Complete in this package: ten documents** | **Not implemented** |
| 6 | Final Roster Cuts | **Complete in this package: ten documents** | **Not implemented** |

**Remaining design workflows:** none of the original six. **Remaining engineering work:** implementation and validation of all workflows not already demonstrably installed in GitHub, beginning with the specific routing, record-ownership, legality and date gates described above. Nothing in this research package creates a pull request, executes a roster move or advances the career clock.

### Primary sources

1. [August 4, 2011 NFL/NFLPA collective bargaining agreement, Articles 23, 29, 33](https://nflps.org/wp-content/uploads/2012/05/collective-bargaining-agreement-2011-2020.pdf).
2. [NFLPA, NFL–NFLPA agreement expanding practice squads](https://nflpa.com/press/nfl-nflpa-agree-to-expand-practice-squads), August 19, 2014.
3. [Jacksonville Jaguars 2015 preseason fixture announcement](https://www.jaguars.com/news/jaguars-announce-preseason-schedule-15157774), April 20, 2015.
4. [NFL, 2015 extra-point rule change](https://www.nfl.com/news/nfl-moves-extra-point-to-15-yard-line-for-2015-season-0ap3000000493347), May 19, 2015.
5. [2015 NFL season key dates, Seahawks](https://www.seahawks.com/news/nfl-announces-important-dates-for-2015-2016-126071), July 2015; verify league date against contemporaneous reports.
6. Existing repository's `career/2015/Calendar.md`, `library/2015_historical_calendar.md`, `docs/rebuild_plan.md`, `docs/event_inserts.md` and the closed 2014 game/roster owner pages. These are described with precise paths in each package's technical specification.

## NFL Coaching Career Simulator | Workflows 5 and 6

**Purpose:** Two independent, research-backed, implementation-ready **design specifications** for the final two items in the six-workflow redesign. Prepared October 20, 2026, after inspecting `Alex-Oss222/football-career-sim`. No simulated 2015 season event has occurred; the current playable career remains after October 5, 2014 Week 5. Nothing here modifies GitHub.

First read [the overall evidence assessment and complete six-workflow checklist](#research-assessment-and-six-workflow-design-checklist).

### Every Preseason Game

A full three-page cycle for **each** of four preseason games, keeping one game result and its real statistics, legal coaching authority, current roster and stand-alone event outcomes.

- [Preseason Game Briefing](../foundation/templates/preseason_game/preseason_game_briefing_template.md)
- [Preseason Game Plan](../foundation/templates/preseason_game/preseason_game_plan_template.md)
- [Preseason Game Report](../foundation/templates/preseason_game/preseason_game_report_template.md)
- [Individual Event Result](../foundation/templates/preseason_game/preseason_game_result_template.md)
- [Implementation Contract and 56 Proposed Tests](preseason_games.md)
- [Worked Jacksonville Example](examples/preseason_games_jacksonville.md)
- [Rules and Sources](preseason_games_research.md#preseason-game-research-and-source-register-20142015)
- [Repository Assessment and Blockers](preseason_games_research.md#preseason-games-repository-assessment-and-implementation-blockers)
- [Four-Game Operational Checklist](../foundation/templates/preseason_game/four_game_checklist.md)
- [Workflow README](preseason_games.md#every-preseason-game-research-and-design-package)

### Final Roster Cuts

The 75-player first deadline, final 53 decision, waivers and legal subsequent changes, keeping Stone's football recommendations and Caldwell's final transaction authority distinct.

- [Roster Cutdown Report](../foundation/templates/final_cuts/roster_cutdown_report_template.md)
- [My Cut Recommendations](../foundation/templates/final_cuts/my_cut_recommendations_template.md)
- [Final 53](../foundation/templates/final_cuts/final_53_template.md)
- [Individual Personnel Result](../foundation/templates/final_cuts/personnel_result_template.md)
- [Implementation Contract and 68 Proposed Tests](final_roster_cuts.md)
- [Worked Jacksonville Example](examples/final_roster_cuts_jacksonville.md)
- [Rules and Sources](final_roster_cuts_research.md#final-roster-cuts-2011-cba-and-201415-contemporary-research)
- [Repository Assessment and Blockers](final_roster_cuts_research.md#final-roster-cuts-repository-assessment-and-unresolved-implementation-requirements)
- [75/53 and Aftercare Checklist](../foundation/templates/final_cuts/cutdown_75_53_and_aftercare_checklist.md)
- [Workflow README](final_roster_cuts.md#final-roster-cuts-research-and-design-package)

### Scope of validation

The packages contain real, standalone Markdown documents. Their internal links, numbering and ZIP contents can be checked locally. The proposed 124 tests are **not** implemented or run in the GitHub project, and do not establish a valid 2015 private game release, waiver service, full roster or completed roster decisions.

Every independently resolved consequential event gets its own dated result under its department owner; a phase report, game report or Final 53 may link but never substitute for it. Existing 2013/2014 completed history is retained unchanged.
