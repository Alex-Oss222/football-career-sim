# Spring and summer designs: the April program to final cuts

**Status:** Uploaded by the user on October 20, 2026 and adopted. The April offseason program, the draft and OTAs are built in step 7 of the [rebuild plan](rebuild_plan.md); position battles, preseason games and final cuts in step 8. Each design was corrected after the process check of October 20, 2026, against the user's rulings of that day and the answers the lead settled, and the six were then made to agree where they describe the same thing. This page indexes the six designs, shows where they meet, and keeps the two package assessments and the package README as uploaded, corrected where they disagreed with the designs. Two questions await the user's decision ([below](#two-questions-awaiting-the-users-decision)).

| Workflow | Design | Research and repository assessment | Templates | Worked example | Built in step |
|---|---|---|---|---|---|
| April Offseason Program | [offseason_program.md](offseason_program.md) | [offseason_program_research.md](offseason_program_research.md) | [foundation/templates/offseason_program/](../foundation/templates/offseason_program/) | [offseason_program_jacksonville.md](examples/offseason_program_jacksonville.md) | 7 |
| NFL Draft | [draft.md](draft.md) | [draft_research.md](draft_research.md) | [foundation/templates/draft/](../foundation/templates/draft/) | [draft_jacksonville.md](examples/draft_jacksonville.md) | 7 |
| May–June OTAs and Minicamp | [otas_and_minicamp.md](otas_and_minicamp.md) | [otas_and_minicamp_research.md](otas_and_minicamp_research.md) | [foundation/templates/otas/](../foundation/templates/otas/) | [otas_and_minicamp_jacksonville.md](examples/otas_and_minicamp_jacksonville.md) | 7 |
| Training Camp Position Battles | [position_battles.md](position_battles.md) | [position_battles_research.md](position_battles_research.md) | [foundation/templates/position_battles/](../foundation/templates/position_battles/) | [position_battles_jacksonville.md](examples/position_battles_jacksonville.md) | 8 |
| Every Preseason Game | [preseason_games.md](preseason_games.md) | [preseason_games_research.md](preseason_games_research.md) | [foundation/templates/preseason_game/](../foundation/templates/preseason_game/) | [preseason_games_jacksonville.md](examples/preseason_games_jacksonville.md) | 8 |
| Final Roster Cuts | [final_roster_cuts.md](final_roster_cuts.md) | [final_roster_cuts_research.md](final_roster_cuts_research.md) | [foundation/templates/final_cuts/](../foundation/templates/final_cuts/) | [final_roster_cuts_jacksonville.md](examples/final_roster_cuts_jacksonville.md) | 8 |

## Where the six designs meet

Each design owns its own rules; this section points to them and adds none of its own. The page names are the registry's (`runtime/decisions.py`), and the folders are under `career/<year>/`.

| Workflow | Folder | Brief, and who brings it | Stone's page | Result page | Scheduled issues of the brief (2015) |
|---|---|---|---|---|---|
| April Offseason Program | `Offseason_Training/` | Offseason Program Brief: the coordinators, named from the coach records, and the strength and conditioning staff | My Program Plan, answered once | Program Report, an index built once after Phase Two closes | One, by April 10; a post-draft edition carries the rookie-minicamp direction |
| NFL Draft | `Draft/`, selections in `Draft/Selections/` | Scouting Department Report: the college scouting department, presented by the general manager | My Draft Recommendations, answered once and frozen when it is applied before Round 1 | Draft Room Results, built from the selection, contract and undrafted-pursuit results | One, April 29 |
| May–June OTAs and Minicamp | `Offseason_Training/OTAs/` | OTA Brief: the coaching staff | My Install Plan, answered once | OTA Report, an index built once after minicamp | Two, May 22 and June 12 |
| Training Camp Position Battles | `Training_Camp_and_Preseason/` | Position Battle Report: the coordinators and the position coaches (the build changes the registry's "The position coaches" to this) | My Depth Calls, each edition answered once | Depth Chart, each edition kept as issued, the last at the reduction to 53 | At the review points the camp plan sets |
| Every Preseason Game | `Training_Camp_and_Preseason/Preseason_Games/Game_0N/` | Preseason Game Briefing: the coaching staff | Preseason Game Plan, answered once for its game | Preseason Game Report, the game's one result page | One for each game in the fixtures, each game with its own pages |
| Final Roster Cuts | `Training_Camp_and_Preseason/Roster_Decisions/` | Roster Cutdown Report: the general manager and the coaching staff | My Cut Recommendations, each stage section answered once | Final 53, built at the September 5 filing and frozen | Two: for the reduction to 75 and, after game four, for the reduction to 53 |

Every brief names Stone on its "Prepared for" line and its authors on its "Presented by" line, read from the coach records and the job record's parties at issue; no scout is named as an author.

- **The brief proposes; Stone's page decides.** He answers his page once: the check tells him what to correct before anything is applied, and once applied the page is kept as the record of his decision and never rewritten. In camp a new round of depth calls is a new edition of My Depth Calls; at the cuts each stage section is answered once.
- **Answers to events.** Each folder holds its phase's one `My_Responses.md`. Events inside a phase are inserts in its active brief (ACTION REQUIRED, FOR YOUR INFORMATION and COMING UP, in the shared [insert template](../foundation/templates/event_inserts/brief_action_inserts_template.md)), answered on that phase's My Responses page, never on Stone's page. A later change of direction goes on My Responses as a dated entry. Only an answer due before the event it holds stops the clock.
- **Editions.** Every brief is reissued only under the one reissue rule ([event inserts](event_inserts.md), section A, item 6). Every issued edition is kept beside the current page with its date in its name, as the Game Week Briefing's are, with its issue record in the shared phase-brief issue history (a preseason game's in its own `briefings.json`).
- **Overlapping briefs.** When phases overlap, two briefs may carry inserts at once, and each event appears once, on its own phase's brief. In 2015 the Scouting Department Report carries draft matters from its April 29 issue until Draft Room Results is published, beside the Offseason Program Brief ([April design, section 6.1](offseason_program.md#61-render-and-issue-the-brief); [draft design, section A](draft.md#a-fixed-scope-and-first-principles)); the Offseason Program Brief carries the program's events until Phase Two closes on May 22, the day of the OTA Brief's first issue ([OTA design](otas_and_minicamp.md), operating rule 5); in August camp, the preseason games and the cuts follow one [routing table](position_battles.md#which-brief-carries-an-event-in-august). Rookie-minicamp direction is a post-draft reissue of the Offseason Program Brief.
- **Results.** Each resolved event gets one dated result, built on the shared [event result](../foundation/templates/event_inserts/event_result_template.md), in its owner's folder: roster moves and waiver claims in `Team_Operations/Team/Roster`, signings and undrafted pursuits in `Team_Operations/Free_Agency`, trades in `Team_Operations/Trades`, staff in `Team_Operations/Staff`, Stone's own career in `career/Stone`, draft selections in `Draft/Selections`; a medical finding stays in its medical record. The April, OTA and preseason packs have no result form of their own (each keeps a pointer page until the template catalog links the shared form); the draft's selection result and the cuts' personnel result are versions of the shared form. A battle closure is a dated section of its card, not an event result.
- **Practice observations.** Each phase's `training_report.md` owns them. The Program Report and the OTA Report index them by section, the camp, preseason and cutdown pages cite them, and a changed view of a player goes on his own record ([April](offseason_program.md#2-single-ownership-of-every-fact), [OTA](otas_and_minicamp.md#one-owner-for-each-fact) and [camp](position_battles.md#one-owner-for-each-fact) ownership tables). Players are evaluated only on taught material; any call in the active playbook may be named on a game plan, preseason included, and only the no-hindsight lock refuses a call from a later book.
- **Depth.** The depth data own the depth chart. From 2015 Stone's applied My Depth Calls is the record of a camp depth decision, `Record.md` lists one line per applied set of depth calls, and each battle card carries a dated closure, closing at the reduction to 53 at the latest. The camp Depth Chart page stays as issued, and its final edition, issued at the reduction to 53 once Final 53 is filed, links Final 53; Final 53 and My Cut Recommendations link the team depth chart page; a preseason game's lineup is on its Preseason Game Plan ([camp ownership table](position_battles.md#one-owner-for-each-fact); [final cuts, rules 12 to 14](final_roster_cuts.md#rules-this-design-follows)).
- **Rules and dates** are owned by the library and the [2015 calendar](../career/2015/Calendar.md); the designs link them. The 2014 records stay as written.

## Two questions awaiting the user's decision

Neither answer is adopted; each recommendation is a proposal only.

1. **Q-R: rewording Document 7 §5.1 and Document 1 line 229 for the per-game preseason pages: awaiting the user's decision.** Document 7 §5.1 resolves the preseason, camp-battle outcomes and roster cuts included, as a single bulk turn presented once at the transition into the regular season, and Document 1 line 229 names the eight-section preseason output. *Proposal, not adopted:* yes, reword both for the per-game preseason pages and the camp and cutdown pages issued during camp, the eight-section bulk output kept for 2013 and 2014. Rulebook text changes only with the user's approval. Until the user decides, the rulebook stands as written: the build lists both lines among the rulebook lines left for the user's approval and edits neither, and the camp, preseason-game and cutdown pages are built in step 8 but not issued for a 2015 preseason. The three August designs list the same held changes in the same words, made only after the user approves: AGENTS.md lines 117, 119 and 121 and the AGENTS.md routing to the new pages, `docs/update_workflow.md` line 125, and the rescoping of the eight-section template and process references to 2013 and 2014 ([position battles, section 11](position_battles.md#11-questions-awaiting-the-users-decision); [preseason games, section H](preseason_games.md#h-awaiting-the-users-decision); [final cuts](final_roster_cuts.md#awaiting-the-users-decision)).
2. **Q-P: how 2015 practice observations are produced: awaiting the user's decision.** No practice resolver is approved ([camp and preseason reports](camp_and_preseason_reports.md)). *Proposal, not adopted:* the 2014 authored, protagonist-blind method with its evidence rules. Until the user decides, no 2015 practice observation is produced, and a page cites only observations a training report already holds ([April, section 6.4](offseason_program.md#how-2015-practice-observations-are-produced-awaiting-the-users-decision); [OTA, section 5](otas_and_minicamp.md#how-2015-observations-are-produced-awaiting-the-users-decision); the camp, preseason and cuts sections linked above).

## NFL head-coach career simulator: May–June and training-camp design handoff

**Design packages, not execution.** GitHub `Alex-Oss222/football-career-sim` was inspected read-only at `75fd41fbfc5ed0363d9f6cb68b5bef37a6583f24` on October 20, 2026. The career still stands at October 5, 2014 after the Week 5 game. Weeks 6–17 and any 2014 postseason results remain future, and neither 2015 spring nor 2015 camp was simulated. No GitHub change is included or recommended as already applied.

### Findings to enforce first

1. **2011 CBA, not a modern rewrite.** In the 2014–15 era, Phase Three OTC/OTA and mandatory veteran minicamp activities are non-contact. Seven-on-seven, nine-on-seven and eleven-on-eleven against an opposing group are lawful without contact; opposed one-on-ones and shells are not. The voluntary OTA and mandatory veteran camp rules differ. The actual 2011 CBA has separate daily-duration rules for ordinary non-OTA activity, Appendix G OTAs and Article 22 minicamp. Training camp begins with restricted day one and no pads/contact on days two and three, counted from each player's own report day, followed by one legal padded session per day under Article 23 time/rest limits. See both source registers.
2. **Use actual historical Jacksonville dates, not their outcomes.** 2015 OTAs were announced for May 26–28; June 1–2 and 4; June 8–9 and 11–12, with June 16–18 mandatory minicamp. How many the real club held is a later real outcome, fenced in the [2015 calendar](../career/2015/Calendar.md#program-phases-and-development-reviews) and never used; Stone's held count is this career's own event. The initial 2015 camp public announcement on July 7 provides July 31 first practice, August 5 first full pads and August 8 scrimmage; the remaining exact daily camp sessions are not supplied by that publication. On October 5, 2014 Stone has not received a July 2015 public announcement.
3. **One observed source, one authority owner.** `Offseason_Training/OTAs/training_report.md` and `Offseason_Training/Mandatory_Minicamp/training_report.md` own their separately conducted football work; the OTA Report is built from them once, after minicamp, and links them without duplicating assessments. `Training_Camp_and_Preseason/Training_Camp/training_report.md` owns camp evidence, and each game's Preseason Game Report owns that game. Each genuine battle card owns its comparison and carries a dated closure that links Stone's My Depth Calls, the record of the decision. The team's depth data own the chart; the camp `Depth_Chart.md` shows Stone's applied calls as they stood on its issue date and stays as issued. A staff recommendation is never a transaction.
4. **Authority is not optional.** Stone chooses practice, group opportunities, depth and staff under his contract and standing instructions. Caldwell chooses contracts, cuts, claims, trades, acquisitions and the draft, on Stone's recommendation. Medical staff determine diagnosis and clearance. The 2014 staff list and player assignments cannot simply be projected into 2015 without the intervening career results.
5. **Events never aggregate.** An active phase briefing can receive several inserts, which are answered on one shared response page, but every separately concluded trade inquiry, rejected offer, unsuccessful hiring pursuit or player transaction has its one dated readable result, built on the shared event result, in its owner's folder. A battle closure is a dated section of its card, not an event result. The phase view only links these files.
6. **No practice-result magic.** The repo contains detailed already-completed 2014 sessions, not a validated general procedure for generating future 2015 on-field observations. How 2015 observations are produced is [awaiting the user's decision](#two-questions-awaiting-the-users-decision); until then no new observation is written. No arbitrary scores, role promotions, guaranteed improvement, coach dialogue or medical clearance are allowed.

### What the two new design packages contain

- [`otas_and_minicamp.md`](otas_and_minicamp.md): `OTA_Brief`, `My_Install_Plan`, `OTA_Report`, a pointer to the shared event result, a full integration contract with **73 proposed tests** (58 as uploaded), evidence-anchored 2014 three-page Jacksonville illustration, source register, repository assessment and README.
- [`position_battles.md`](position_battles.md): `Position_Battle_Report`, `My_Depth_Calls`, `Depth_Chart`, the battle closure folded into the card template, integration contract with **68 proposed tests**, 2014 six-battle illustration, source register, repository assessment and README.

All placeholders in the coach-page templates are *authoring instructions* only. A deployed page includes actual verified and relevant football facts, not template brackets, technology labels or unknown figures disguised as facts. The specs are technical and intentionally separate.

The uploaded six-workflow checklist is replaced by the table at the top of this page: all six designs are complete and adopted, and none is built yet.

**Quality gate:** Both packages need dedicated runtime implementations and their proposed tests run on a separate, explicitly approved future GitHub change. Their current contents do not authorize the next simulation event.

## Research assessment and six-workflow design checklist

**Scope:** Design packages for the remaining two decisions: every preseason game and final roster cuts, based on `Alex-Oss222/football-career-sim` at GitHub `main` tree `75fd41fbfc5ed0363d9f6cb68b5bef37a6583f24`, inspected October 20, 2026. The career is at October 5, 2014, after simulated Jacksonville Week 5. This package is **not** a recorded coaching action, not implemented in GitHub, and not authorization to play a 2015 game or make a transaction.

### Assessment: what is supported

The club already has four completed **simulated** 2014 exhibition games with distinct frozen inputs, game outputs, injury results and preseason-only statistics. Those historical career results are controlled by the branch and remain unedited. The existing `runtime.preseason` compiler, `runtime.rotation` controls, production closer and validation tests supply relevant foundations. The prior eight-section preseason output already includes a story, real coaching analysis, complete generated box score and a cumulative review. The new three-page structure must retain their substance, not replace them with generic narrative or run a second result for one game.

The completed 2014 reduction to 53 documents a lawful **no-cut first deadline** when Jacksonville counted 74 contracted players against 75, then a separate reduction to 53, a next-day waiver process and individually recorded practice-squad agreements. Stone's depth calls and Caldwell's transactions were distinct. The six documented 2014 position battles closed August 30, not automatically after an exhibition performance.

### Assessment: CBA and historical calendar

- The **2011 collective bargaining agreement** and then-applicable 2014 practice-squad expansion, not modern roster or waiver rules, govern this period. Waiver exemption under Article 29 depends on **Plan credited service**. Practice-squad exceptions under Article 33 and the 2014 agreement rely on **accrued seasons** and their distinct tests. No substitute based solely on years since draft is valid.
- The 2015 Jacksonville preseason schedule was announced by the club April 20, 2015: Pittsburgh at Jacksonville August 14, Jacksonville at the NY Giants August 22, Detroit at Jacksonville August 28 and Jacksonville at Washington September 3, each with the established kickoff. Publication date controls what can appear in an earlier briefing.
- The NFL's May 19, 2015 extra-point rule changes the kicked try to the 15-yard-line snap, leaves two-point attempts at the 2, and allows defensive two-point returns. The released 2014 preseason rules may not be reused unmodified for 2015.
- **September 1, 2015 before 4 p.m. ET** is the 75-player limit, before preseason game four on September 3. **September 5 before 4 p.m. ET** is the 53-player filing, with the September 6 noon waiver checkpoint and later practice-squad window. A single end-of-August reduction would be incorrect.

### Specific implementation blockers

1. In `runtime.decisions.py`, the two unimplemented decisions `preseason_game` and `final_cuts` use a shared path that currently resolves to the *parent* `Training_Camp_and_Preseason` folder. The new plans need kind-specific routing: one `Preseason_Games/Game_0N/` triplet for each game in the fixtures and the separate `Roster_Decisions/` cutdown triplet.
2. `scripts/close_preseason_game.py` currently owns the older `output.md` rendering. The new `Preseason_Game_Report.md` must become the only reader-facing owner for **future** games while frozen 2014 output bytes remain unchanged. Existing statistics and event records must not be double-written.
3. The 2014 game release does not prove a valid 2015 released game environment. The 2015 rules, medical status, opponent rosters, personnel, rotation, fixture and gameplay inputs require their own readiness gates and date limits. The remainder of 2014 has not been simulated.
4. A new decision-queue block is needed for a particular preseason game freeze and close, while a separate event-specific gate is needed at 75 and 53. Unrelated personnel business should not block independent events; a real roster dependency must.
5. The current 2014 practice and roster documents are histories, not machine-writable 2015 outcomes. Individual medical, contract, waiver and signed-player dispositions must be legally verified, idempotent and stored at the correct source of truth.
6. The current 2014 examples are **not** scripts for 2015 player development, camp grades, other clubs' transactions or waiver outcomes. The 2015 roster is not available at the October 2014 simulated date. Training-camp work and draft/cap outcomes must actually occur before they can appear.
7. For every separately resolved matter, including one player's cut, a rejected trade, a failed waiver claim or an unsuccessful practice-squad pursuit, generate **one separate dated result**. Main phase summaries link each result. A two-person injury case or twenty-person cutdown must not collapse into one invented universal result.
8. Final roster ownership belongs to Caldwell, on Stone's recommendation. Stone owns team depth, playing roles and game-day inactives and can advise on acquisition and retention. Medical personnel decide clearance. The 53 does not determine the dressed 46. When Caldwell removes a role holder, the next player in Stone's standing depth order takes the role, and a starting or specialist role with no ranked successor goes back to Stone ([final cuts design](final_roster_cuts.md#rules-this-design-follows), rule 9).

The package spells out **70 proposed preseason-game tests** (56 as uploaded) and **68 proposed cutdown tests**, plus acceptance scenarios. These tests have **not** been run against GitHub and are not a claim that the workflows have been installed.

### Design checklist

The uploaded design checklist is replaced by the table at the top of this page. All six workflows have complete, adopted designs; the remaining work is their implementation and validation, beginning with the specific routing, record-ownership, legality and date gates described above. Nothing in this research package creates a pull request, executes a roster move or advances the career clock.

### Primary sources

1. [August 4, 2011 NFL/NFLPA collective bargaining agreement, Articles 23, 29, 33](https://nflps.org/wp-content/uploads/2012/05/collective-bargaining-agreement-2011-2020.pdf).
2. [NFLPA, NFL–NFLPA agreement expanding practice squads](https://nflpa.com/press/nfl-nflpa-agree-to-expand-practice-squads), August 19, 2014.
3. [Jacksonville Jaguars 2015 preseason fixture announcement](https://www.jaguars.com/news/jaguars-announce-preseason-schedule-15157774), April 20, 2015.
4. [NFL, 2015 extra-point rule change](https://www.nfl.com/news/nfl-moves-extra-point-to-15-yard-line-for-2015-season-0ap3000000493347), May 19, 2015.
5. [2015 NFL season key dates, Seahawks](https://www.seahawks.com/news/nfl-announces-important-dates-for-2015-2016-126071), July 2015; verify league date against contemporaneous reports.
6. Existing repository's `career/2015/Calendar.md`, `library/2015_historical_calendar.md`, `docs/rebuild_plan.md`, `docs/event_inserts.md` and the closed 2014 game/roster owner pages. These are described with precise paths in each package's technical specification.

## NFL Coaching Career Simulator | Workflows 5 and 6

**Purpose:** Two independent, research-backed, implementation-ready **design specifications** for the final two items in the six-workflow redesign. Prepared October 20, 2026, after inspecting `Alex-Oss222/football-career-sim`. No simulated 2015 season event has occurred; the current playable career remains after October 5, 2014 Week 5. Nothing here modifies GitHub.

First read [the overall evidence assessment](#research-assessment-and-six-workflow-design-checklist).

### Every Preseason Game

A full three-page cycle for **each** game in the season's fixtures, keeping one game result and its real statistics, legal coaching authority, current roster and stand-alone event outcomes.

- [Preseason Game Briefing](../foundation/templates/preseason_game/preseason_game_briefing_template.md)
- [Preseason Game Plan](../foundation/templates/preseason_game/preseason_game_plan_template.md)
- [Preseason Game Report](../foundation/templates/preseason_game/preseason_game_report_template.md)
- Event results: the [shared event result](../foundation/templates/event_inserts/event_result_template.md), one per resolved event at its owner
- [Implementation Contract and 70 Proposed Tests](preseason_games.md)
- [Worked Jacksonville Example](examples/preseason_games_jacksonville.md)
- [Rules and Sources](preseason_games_research.md#preseason-game-research-and-source-register-20142015)
- [Repository Assessment and Blockers](preseason_games_research.md#preseason-games-repository-assessment-and-implementation-blockers)
- [Per-game sequence](preseason_games.md#per-game-sequence), which replaces the uploaded four-game checklist
- [Workflow README](preseason_games.md#every-preseason-game-research-and-design-package)

### Final Roster Cuts

The 75-player first deadline, final 53 decision, waivers and legal subsequent changes, keeping Stone's football recommendations and Caldwell's final transaction authority distinct.

- [Roster Cutdown Report](../foundation/templates/final_cuts/roster_cutdown_report_template.md)
- [My Cut Recommendations](../foundation/templates/final_cuts/my_cut_recommendations_template.md)
- [Final 53](../foundation/templates/final_cuts/final_53_template.md)
- [Personnel Result](../foundation/templates/final_cuts/personnel_result_template.md), the final-cuts form of the shared event result
- [Implementation Contract and 68 Proposed Tests](final_roster_cuts.md)
- [Worked Jacksonville Example](examples/final_roster_cuts_jacksonville.md)
- [Rules and Sources](final_roster_cuts_research.md#final-roster-cuts-2011-cba-and-201415-contemporary-research)
- [Repository Assessment and Blockers](final_roster_cuts_research.md#final-roster-cuts-repository-assessment-and-unresolved-implementation-requirements)
- [75/53 and Aftercare Checklist](../foundation/templates/final_cuts/cutdown_75_53_and_aftercare_checklist.md)
- [Workflow README](final_roster_cuts.md#final-roster-cuts-research-and-design-package)

### Scope of validation

The packages contain real, standalone Markdown documents. Their internal links, numbering and ZIP contents can be checked locally. The proposed 138 tests (70 and 68) are **not** implemented or run in the GitHub project, and do not establish a valid 2015 private game release, waiver service, full roster or completed roster decisions.

Every independently resolved consequential event gets its own dated result in its owner's folder; a phase report, game report or Final 53 may link but never substitute for it. Existing 2013/2014 completed history is retained unchanged.
