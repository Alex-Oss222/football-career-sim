# Final Roster Cuts: implementation and validation contract

**Status:** Uploaded by the user on October 20, 2026 and adopted; built in step 8 of the [rebuild plan](rebuild_plan.md). Corrected after the process check of October 20, 2026, against the user's rulings and the answers the lead settled, each written below as this design's rule ([rules this design follows](#rules-this-design-follows)). Two questions that bear on this design await the user's decision: rewording Document 7 §5.1 and Document 1 line 229 for the per-game preseason pages and these per-stage cut pages, and how 2015 practice observations are produced ([awaiting the user's decision](#awaiting-the-users-decision)). The templates and the 75, 53 and aftercare checklist are in [foundation/templates/final_cuts/](../foundation/templates/final_cuts/), the worked example is [docs/examples/final_roster_cuts_jacksonville.md](examples/final_roster_cuts_jacksonville.md) and the research register and repository assessment are in [docs/final_roster_cuts_research.md](final_roster_cuts_research.md).

As uploaded: **Status:** Design-only proposed workflow, never executed. Repository inspected at `main` tree `75fd41fbfc5ed0363d9f6cb68b5bef37a6583f24` (2026-10-20). Active career still October 5, 2014 after the Week 5 Pittsburgh game. This package did not make a transaction, medical designation, assistant appointment or Stone decision.

## Final Roster Cuts: research and design package

Three full coach-facing Markdown templates, the final-cuts form of the [shared event result](../foundation/templates/event_inserts/event_result_template.md), an implementation contract with **68 proposed tests**, the completed 2014 Jacksonville precedent and the 2015 schedule, the period CBA research and source register, the repository assessment and a 75, 53 and waiver checklist.

**Status:** Design only; all 2014 and 2015 results unchanged. The active career remains after the October 5, 2014 regular-season Week 5 game. The 2015 player list cannot be completed until the career actually reaches that period.

### Documents

1. [Roster Cutdown Report](../foundation/templates/final_cuts/roster_cutdown_report_template.md)
2. [My Cut Recommendations](../foundation/templates/final_cuts/my_cut_recommendations_template.md)
3. [Final 53](../foundation/templates/final_cuts/final_53_template.md)
4. [Personnel Result](../foundation/templates/final_cuts/personnel_result_template.md), the final-cuts form of the shared event result
5. [Implementation and Validation](#1-three-page-workflow-two-mandatory-roster-deadlines)
6. [Worked Jacksonville 2014/2015 Example](examples/final_roster_cuts_jacksonville.md)
7. [Research and Source Register](final_roster_cuts_research.md#final-roster-cuts-2011-cba-and-201415-contemporary-research)
8. [Repository Assessment and Blockers](final_roster_cuts_research.md#final-roster-cuts-repository-assessment-and-unresolved-implementation-requirements)
9. [75, 53 and Aftercare Checklist](../foundation/templates/final_cuts/cutdown_75_53_and_aftercare_checklist.md)

**Fixed ownership:** David Caldwell, the general manager in the current job record, decides the roster, contracts, waivers, claims and practice-squad signings on Stone's recommendation; Stone decides depth, roles, game-day inactives and practice; the medical staff decide diagnosis and clearance. Every concluded personnel transaction or pursuit, successful or not, is its own dated result in its owner's folder. The reduction to 75 is a distinct stage that gates preseason game four. The Final 53 is the roster as filed on September 5, not the roster after waivers and the practice squad.

### Rules this design follows

These are the user's rulings and the answers the lead settled after the process check of October 20, 2026, written as the rules that decide how the design works. Where an uploaded line below conflicts with one of them, the rule governs and the line has been corrected.

**Pages, answers and editions**

1. **Three pages, one answer page, one folder.** The Roster Cutdown Report, My Cut Recommendations and Final 53 live in `career/<year>/Training_Camp_and_Preseason/Roster_Decisions/`, with the phase's one `My_Responses.md` and its index, `README.md`. The registry's route lands in the parent folder today; the build adds the final-cuts route (section 3).
2. **Events are inserts.** An event during the phase (a trade call, a claim question, a medical change that needs a roster answer, a practice-squad matter) is an insert at the top of the Roster Cutdown Report, in the shared [insert form](../foundation/templates/event_inserts/brief_action_inserts_template.md): ACTION REQUIRED for an answer Stone owes, FOR YOUR INFORMATION for news and for what a standing rule or someone else has already answered, COMING UP for a window ahead. Stone answers every insert on the phase's one My Responses page. My Cut Recommendations holds only the phase answer. Each resolved event gets its own dated result page in its owner's folder (rule 10), built on the shared [event result](../foundation/templates/event_inserts/event_result_template.md) through its final-cuts form; the phase index links each one.
3. **Overlapping briefs.** The camp's Position Battle Report, a Preseason Game Briefing and the Roster Cutdown Report can be open at the same time. Two briefs may carry inserts at once; each event appears once, on the first brief that fits it, by the [August routing table](position_battles.md#which-brief-carries-an-event-in-august) of the position battles design: a depth question on the Position Battle Report, answered on My Depth Calls; roster-limit, waiver, claim and practice-squad matters on the Roster Cutdown Report once it has been issued; any other matter of a game's preparation or availability on that game's briefing ([preseason games design](preseason_games.md)); and, after the last preseason game, any other event on the Roster Cutdown Report.
4. **Editions under the one reissue rule.** The report has two scheduled issues: the first for the reduction to 75, the second after game four for the reduction to 53, which carries the 75 count. Any other edition follows the one reissue rule that governs every brief ([event inserts](event_inserts.md), section A, item 6): a new event needs Stone's answer, a dated finding materially changes a choice still pending, or an answer falls due before the next scheduled issue. Every issued edition is kept beside the current page with its date in its name, as the Game Week Briefing's are, with its issue record in the shared phase-brief issue history, and the page shows the latest. The build fixes the two issue dates in the 2015 calendar.
5. **Stone's page is answered once.** My Cut Recommendations is one page with two stage sections, and each is filled once and never rewritten. The 75 section is frozen when Caldwell acts on it; the 53 section is filled after game four and never rewrites the 75 answer. Answers to inserted events never go on this page. When the count is already at or under 75, the 75 section is not requested: a FOR YOUR INFORMATION line gives the count, and no cut is made.
6. **What stops the clock.** Only an answer due before the event it holds stops the clock. A requested 75 answer holds Caldwell's reduction to 75, and game four freezes only from a roster at or under 75, so game four waits for the 75. The 53 answer holds the September 5 filing. A claim or practice-squad recommendation holds only that claim or approach. Other clubs' moves and league events go on. Silence is never a yes or a no.

**Authority**

7. **Who decides.** Stone decides depth and package roles (row 9), game-day inactives (row 8), practice (row 11, a labelled inference) and his staff. Caldwell decides cuts and roster-limit compliance (row 7, a labelled inference from his personnel authority), player contracts (row 5), and waivers, claims, releases, reserve placements, practice-squad signings and trades (row 20), each on Stone's recommendation. The medical staff decide diagnosis and clearance (row 16). The rows are in the [job record](../state/current_job.json); its row 5 still reads unset for Stone's part, and writing "Stone recommends, Caldwell decides" there belongs to the build of the [February and March design](re_signing_and_free_agency.md). Staff names on every page come from the coach records (`data/people/coaches/`) and the job record's parties for the page's date; no scout is named as an author.
8. **The brief proposes, Stone's page decides, and Caldwell follows Stone's lawful list.** The Roster Cutdown Report may carry the staff's proposed keeps and cuts; a proposal is never an answer, and My Cut Recommendations is Stone's. Caldwell departs from Stone's list only on a criterion written into the Roster Cutdown Report before Stone answers (a legal, contract, cap or medical constraint), never because of how Stone worded his page, and no disagreement is invented. This is the rule the [February and March design](re_signing_and_free_agency.md) applies to Stone's priorities, and it passes the label-swap test.
9. **Who fills a role Caldwell removes.** If Stone's standing depth order already ranks the next player for that role, he takes it and Stone gets a FOR YOUR INFORMATION. A starting or specialist role with no ranked successor goes to Stone as ACTION REQUIRED on the brief then active, due before the Week 1 Game Plan freezes. This replaces the upload's blanket "return the role to me" and "no automatic promotion".

**Owners**

10. **Result owners.** Waivers, releases, reserve and list placements, and claims made or awarded: `Team_Operations/Team/Roster`. Practice-squad and other signed contracts, and approaches that end without a contract: `Team_Operations/Free_Agency`. Trades: `Team_Operations/Trades`. Staff: `Team_Operations/Staff`. Stone's own career: `career/Stone`. A medical finding stays in its medical record and is linked, not copied. A record that already owns an event (a completed trade, a medical incident) is linked as its result, never duplicated.
11. **Practice observations and taught material.** The camp training report (`training_report.md`) owns practice observations. The Roster Cutdown Report cites them and the battle cards and never restates them. A changed personnel view goes on the player's record. Players are evaluated only on material that was taught; any call in the active playbook may be named on a game plan, preseason included, and only the no-hindsight lock refuses a call from a later book, but a call never taught is not evidence for or against a player. How 2015 observations are produced awaits the user ([below](#awaiting-the-users-decision)).
12. **Depth.** The depth data own the depth chart: `game_depth_chart.json`, Stone's dated role decisions on `working_depth_chart.json`, and `update_log.json`, in `data/<year>/Team_Operations/Team/Depth_Chart/`; `depth_chart.md` is the built view ([update workflow](update_workflow.md)). Stone's depth calls reach the depth data through My Depth Calls or the Week 1 Game Plan, and his inactives through the Week 1 Game Plan. The camp Depth Chart page stays as issued. Final 53 and My Cut Recommendations link the team depth chart page (`depth_chart.md`), and the final camp Depth Chart edition, issued at the reduction to 53 once Final 53 is filed, links Final 53; My Cut Recommendations gives roles only as the football reason for a keep or a cut. Record.md carries one line per applied set of depth calls.
13. **Battle cards close at 53.** Every card still open closes with Stone's season depth chart at the reduction to 53, at the latest. A provisional call is allowed, and any later change is an ordinary in-season depth decision through the depth chart's update log. The closure is the battle card template's closure ([position battles design](position_battles.md)). The Roster Cutdown Report links the open cards and builds no second comparison table.
14. **Final 53 is built once and frozen.** It is built from the roster record at the September 5 filing, with a freeze record (a digest at filing), and never changes. A September 6 claim, waiver, release or signing appears only on its own result page and the roster page. There is no second edition of the 53 and no separate page for the cut to 75: the 75 count goes on the 53-stage edition of the Roster Cutdown Report, the 75-stage results are linked from the phase index, and Final 53 links the phase index.
15. **Rules and dates have their own owners.** The [2015 calendar](../career/2015/Calendar.md) and the library own the dates and rules. This design cites them: section 2 names each rule and its owner, and the design holds no rule of its own beyond that citation. The 2014 records stay as written.

**Waivers, claims and the practice squad**

16. **Vested veterans: Plan credited service.** A player who has finished the season in which he earned his fourth year of credited service under the Bert Bell/Pete Rozelle Plan and who is placed on waivers between February 1 and the trading deadline has his contract terminated and is free; any other player goes through waivers (2011 CBA Article 29 §1(a) and (b), printed p. 155). Plan credited service is verified per player. Where it cannot be established, it is recorded as unresolved and the move is a waiver request, and the result page says that a fourth credited year would make it a termination. The [2014 record](../career/2014/Training_Camp_and_Preseason/Roster_Decisions/final_roster_cuts.md) applied the user's vested-veteran instruction from accrued seasons and stays as written; that test is not copied. The finance inputs' `credited_seasons` field is an Article 26 count, which Article 26 §2 applies "under this Article only", and it is verified against the Plan before it is used for this.
17. **Other clubs' claims on Jacksonville's waived players follow the rails.** A waived Jacksonville player goes to another club only if his real next move was a claim in that window; otherwise he clears, as every 2014 waiver did ([2014 record](../career/2014/Training_Camp_and_Preseason/Roster_Decisions/final_roster_cuts.md), August 31). A released or cleared player follows his real next move only when it was the same kind of move in the same window; otherwise he is an unplaced free agent ([rails method](../career/2014/League/personnel/method.md), section 3).
18. **Jacksonville's claims on other clubs' waived players follow the waiver order.** Caldwell decides whether to claim, on Stone's recommendation. A player becomes claimable on his real waiver date. The claim is awarded by the waiver order then in force: Jacksonville wins only if it stands ahead of the club that really claimed the player, and a claim on a player no club really claimed is awarded. Jacksonville's place comes from the career's 2014 standings, never the real Jaguars'. The working reading is that the preseason order follows the 2015 draft order; the build enters the order rule in the two-pass 2015 rules entry before any claim (section 2). If Jacksonville wins, the club that really claimed him does not get him, and its next man up takes his depth place, as rails rule 6 treats a free agent Jacksonville wins.
19. **The practice squad.** No club signs a practice-squad player until the personnel notice confirms his waiver termination (September 6, about 1 p.m.). The squad has ten places, with at most two players with up to two accrued seasons (library G1, the 2014 and 2015 agreement); the base eligibility terms are Unverified (library R5) and are applied conservatively, as in 2014. An approach to a player who really signed somewhere in the same window, a player Jacksonville itself waived included, is decided by the rails market draw on its real date ([rails method](../career/2014/League/personnel/method.md), section 4). A player with no real signing in the window signs. No other decline is generated. The eight 2014 signings are not a precedent for this rule: the [2014 record](../career/2014/Training_Camp_and_Preseason/Roster_Decisions/final_roster_cuts.md) signed them from the target list without checking for real practice-squad signings elsewhere in the same window (its rails check covered cutdown-window waiver claims, and the [Week 1 depth-chart library](../library/2014_week1_depth_charts.md) it used holds no practice squads). At least three of the eight had such a signing: Matt Feiler with Houston, Jackson Jeffcoat with Washington on September 2 and Jemea Thomas with Dallas on September 2. The 2014 signings stay as written and are not a test fixture for the uncontested case. A draw Jacksonville loses is a dated result in `Team_Operations/Free_Agency`.
20. **Cap and contract effects.** Every effect comes from the finance inputs' recovered or adopted schedule, labelled a reconstruction where adopted, as the 2014 cuts were. A field is marked unresolved only where no recovered or adopted term exists. Termination pay cannot arise at the September 1 or September 5 reductions or on September 6: it applies only to a player with four Plan credited years who is released after his club's first regular-season game and was on the Active/Inactive List on or after that game, and only once in a career (2011 CBA Article 30 §1, printed p. 157). A vested veteran kept past the first regular-season game becomes eligible for it.

**Rails and hindsight**

21. **No real 2015 outcome.** No real 2015 Jacksonville roster move, cut list, practice-squad name or article about a real 2015 cutdown is a source, a model or a test value. Other clubs' players follow their real moves on their real dates, and a rail becomes usable only on its public date. Jacksonville's draft and waiver order come from the career's standings. The 2015 deadlines come from the league bulletins in the library (sources J, K, L and M), which the calendar holds; a brief cites a date only once its source was public.

**Writing**

22. Plain prose, tables where the content is a list, relative links, and "play-by-play" for the game record. The reader-facing pages carry no system words, file paths or identifiers.

### Awaiting the user's decision

**Q-R: rewording Document 7 §5.1 and Document 1 line 229 for the per-game preseason pages: awaiting the user's decision.** Document 7 §5.1 ([the game engine rulebook](../foundation/07_Game_Simulation_and_Resolution_Engine.md)) says the preseason resolves as one bulk turn with "one consolidated brief covering roster-cut decisions, the preseason-game slate's results and notable performances, and camp-battle outcomes, presented once at the transition into the regular season", and Document 1 line 229 ([project instructions](../foundation/01_Project_Instructions.md)) routes preseason output to the eight-section preseason template. This design's per-stage Roster Cutdown Report, My Cut Recommendations and Final 53, like the per-game preseason pages of the [preseason games design](preseason_games.md), depart from that wording. *Proposal, not adopted:* yes, reword both for the per-game preseason pages and the camp and cutdown pages issued during camp, the eight-section bulk output kept for 2013 and 2014. Rulebook text changes only with the user's approval. Until the user decides, the rulebook stands as written: the build lists both lines among the rulebook lines left for the user's approval and edits neither ([section 3](#3-repository-inspection-and-the-build)), and the camp, preseason-game and cutdown pages are built in step 8 but not issued for a 2015 preseason. The changes held on it are listed in [section 3](#3-repository-inspection-and-the-build).

**Q-P: how 2015 practice observations are produced: awaiting the user's decision.** The Roster Cutdown Report cites camp and battle work from the training report. *Proposal, not adopted:* the 2014 authored, protagonist-blind method with its evidence rules; no resolver is approved yet ([camp and preseason reports](camp_and_preseason_reports.md)). Until the user decides, no 2015 practice observation is produced, and a page cites only observations a training report already holds.

## 1. Three-page workflow, two mandatory roster deadlines

The `final_cuts` registry entry in `runtime/decisions.py` fixes three primary coach-facing pages. All live in `career/<year>/Training_Camp_and_Preseason/Roster_Decisions/`; the present route lands in the parent `Training_Camp_and_Preseason/`, and the build adds a route for this decision only (section 3).

| Role | Filename | Owner and status |
|---|---|---|
| The general manager's and coaching staff's brief | `Roster_Cutdown_Report.md` | Two scheduled issues (the reduction to 75, then the reduction to 53 after game four, carrying the 75 count) and any edition the one reissue rule requires; every edition kept |
| Stone's football recommendation | `My_Cut_Recommendations.md` | One page with a 75 section and a 53 section, each answered once; the 75 section is frozen when Caldwell acts on it and is not requested when the count is already compliant |
| The roster as filed | `Final_53.md` | Built once from the roster record at the September 5 filing and frozen with a digest; links the phase index and the depth chart; no later edition |
| Answers to inserted events | `My_Responses.md` | The phase's one answer page for every insert in the Roster Cutdown Report |
| Phase index | `README.md` | Links each resolved event's own result page, the 75-stage results included |

Do not compress the 2015 **September 1 before 4 p.m. ET reduction to 75** into the September 5 final 53. September 3 is the fourth preseason game and must use the compliant post-75 roster. The 75 stage gets its dated count, each completed transaction at its own owner, and its count on the 53-stage edition of the Roster Cutdown Report; there is no 'Final 75' page. After the final reduction, `Final_53.md` is built once from the roster record (rule 14).

## 2. Rules and dates, and where each is owned

The design reads these rules and dates; it does not own them. Dates are in the [2015 calendar](../career/2015/Calendar.md) and its [source register](../library/2015_historical_calendar.md); 2014 and 2015 list rules are in the [2014 playing and roster rules](../library/2014_playing_and_roster_rules.md). The rules marked for the new entry go into one two-pass 2015 cutdown-rules library entry in the build (section 3) before a 2015 page uses them.

| Rule or date | Owner today | Status | Design consequence |
|---|---|---|---|
| 90 to 75 by Tuesday, September 1, before 4 p.m. ET | 2015 calendar; library J and K | Confirmed | Count players legally classified against the limit; a list of unsigned rights is not a count of signed contracts |
| Game four: Jacksonville at Washington, Thursday, September 3, 7:30 p.m. ET | 2015 calendar; library C and E | Confirmed | Game four freezes only from a roster at or under 75 |
| 75 to 53 by Saturday, September 5, before 4 p.m. ET | 2015 calendar; library J, K and L | Confirmed. The library records: "An inaccessible Raiders PDF search extract showed a conflicting final-cutdown hour; it does not override the agreeing contemporaneous bulletin copies" | Final 53 is built at this filing |
| PUP and NFI at the 53: reserve list, waiver or termination, trade, or keep on the Active List | 2015 calendar (September 5 row); NBC/PFT, August 27, 2015 (library M), read October 20, 2026 | Supported; for the new entry | Each player's list status and medical opinion are verified individually, never inferred from an injury |
| Waiver claims close Sunday, September 6, at noon ET; personnel notice about 1 p.m. | 2015 calendar; library K and L, with M | Confirmed | Other clubs' claims come from the rails; Jacksonville's claims follow the waiver order (rules 17 and 18) |
| Practice squad: ten places; a squad season counts only with six games; at most two players with up to two accrued seasons | Library G1 (the two-year 2014 and 2015 agreement) | Confirmed | Signed only after the personnel notice; approaches decided as rule 19 says |
| Practice-squad base eligibility terms | Library R5 | Unverified | Applied conservatively, as in 2014; for the new entry |
| Designated for return: one player, designated at placement, placement only after September 6 at 4 p.m. ET | 2015 calendar; library R6 (the 2012 rule, unchanged for 2014), L and M | Confirmed for one player and the September 6 window; the at-placement and on-the-53 conditions Supported (R6); the 2015 row for the new entry | No same-day September 5 designation and no later multiple-return rules |
| Waived with the injured designation, then reserve/injured on clearing | The period procedure the [2014 record](../career/2014/Training_Camp_and_Preseason/Roster_Decisions/final_roster_cuts.md) applied | Applied in 2014; for the new entry | No reserve/injured placement until the waiver result permits it |
| Vested veteran: Plan credited service (Article 29 §1) | 2011 CBA, printed p. 155 | Confirmed in the CBA text; for the new entry | Rule 16 |
| No other club contacts a player on waivers until the waiving club releases him (Article 29 §2) | 2011 CBA, printed p. 155 | Confirmed in the CBA text; for the new entry | Waivers pending are not a free-agent negotiation |
| Termination pay only after the first regular-season game (Article 30 §1) | 2011 CBA, printed p. 157 | Confirmed in the CBA text; for the new entry | Rule 20 |
| Game-day list: 46 of the 53 dress for regular-season and postseason games | Library U3 and R4 (2014) | Confirmed for 2014; Unverified for 2015 | The 2015 figure goes into the new entry; no later 48-player or eight-lineman rule |
| Preseason waiver order | None yet | Unverified; working reading: the order of the 2015 draft, computed from the career's 2014 standings | For the new entry before any claim (rule 18) |
| Bonus acceleration on a release | None; the 2014 cuts used the post-June 1 treatment as a labelled reconstruction | Unverified | For the new entry; until then a labelled reconstruction, as in 2014 |
| Contract and cap effect of each cut | The finance inputs (`career/finances`, `data/finances/financial_inputs.json`) and the adopted schedules | As each schedule is labelled | Rule 20 |

The CBA rights distinction is nontrivial. Three different counts answer three different questions, and each answer carries its source: Plan credited service (the Article 29 waiver exemption and Article 30 termination pay); the Article 26 credited-season count that the finance inputs hold, which Article 26 applies "under this Article only" and which excludes reserve and practice-squad games; and accrued seasons (free agency and the enlarged practice-squad class). Do not equate one with another.

## 3. Repository inspection and the build

| Existing path or system | What works now | What the build must add |
|---|---|---|
| `runtime/decisions.py` `final_cuts` | The triplet is registered, not implemented. Its shared `training_camp_and_preseason` place resolves to `Training_Camp_and_Preseason/`, not `Roster_Decisions/` (re-run October 20, 2026) | A place for this decision only, such as `("training_camp_and_preseason/roster_cuts", 0)`, which `SeasonPaths.record` maps to `Roster_Decisions/`; the camp and preseason-game pages do not move |
| `state/current_job.json`, Document 3 | Stone decides depth (row 9), game-day inactives (row 8) and practice (row 11, a labelled inference); Caldwell decides final cuts (row 7, a labelled inference), contracts (row 5) and transactions (row 20); the medical staff decide clearance (row 16) | Owner-specific actions: Stone's recommendations never become transactions, and Caldwell never sets a depth call |
| `runtime/decision_queue.py` | `personnel_recommendation`, `personnel_transaction`, `depth_and_roles` and `medical_status` exist; the block kinds are `week_inputs`, `week_close`, `call_sheet_part`, `season_stage` and `season_opening`, with no cutdown block | Blocks for the reduction to 75, the reduction to 53 and the game-four freeze, scoped by season, and items for a claim or a practice-squad approach; an unanswered requested recommendation holds only the action it precedes |
| [2014 final roster cuts](../career/2014/Training_Camp_and_Preseason/Roster_Decisions/final_roster_cuts.md) | Completed 2014 reductions: 74 signed at the 75, 53 on August 30, waivers and eight squad signings August 31 | Kept as written, a precedent and not 2015 data; the 2015 dates differ |
| [2014 roster decisions](../career/2014/Training_Camp_and_Preseason/Roster_Decisions/roster_decisions.md) | Stone's dated depth and game-day decisions | Kept as written. From 2015 the depth data own the depth chart (rule 12) |
| `Position_Battles/` cards | Six 2014 competitions with dated evidence, closed August 30 | 2015 cards only for established contests; each closes at the 53 at the latest (rule 13) |
| `Team_Operations/Team/Roster/`, finances, medical | The roster record, the contract and cap inputs and the medical records | A 2015 transaction writer with roster, cap, list and waiver effects in one step; the views rebuilt from the owners, never edited |
| `runtime/rails.py`, the rails method | Other clubs' real moves on real dates, the Jacksonville exception and the same-kind, same-window rule | 2015 rails data for the cutdown window, built when the clock reaches it |
| `docs/event_inserts.md`, `runtime/events`, the annual index | One reissue rule, one result per resolved event, the event-record line and the generated Record.md | Inserts in the Roster Cutdown Report, answers on its My Responses page, results in the owner folders and the phase index |
| `scripts/validate_repository.py`, `runtime/clean_pages.py` | Football-only page rules and owner-path rules | The page checks for the three pages, a check that Final 53 matches its freeze record, and no duplicate event owner |
| `runtime/rules.py`, `scripts/close_preseason_game.py` | `active_limit` for a preseason game returns 90 | A date-aware limit: game four is checked against 75 |

**Not currently demonstrated:** a 2015 cutdown transaction writer, the waiver-order computation for Jacksonville's claims, the 53 cutdown dependencies, a result publisher for many events at once, and the 2015 roster and season release. The 2014 completion record does not establish these for 2015.

**What the build must add** (the process check of October 20, 2026; each item belongs to the build step named):

| Need | Where | Step |
|---|---|---|
| The final-cuts route to `Training_Camp_and_Preseason/Roster_Decisions`, without moving the camp or preseason-game routes, with a test | `runtime/decisions.py` (PLACES); the final-cuts row of `docs/rebuild_plan.md` (its Folder column) | 8 |
| Event kinds for each cutdown disposition (waiver, release, reserve or list placement, claim made or awarded, practice-squad signing, approach lost in the market draw), with their owners, and the signings owner `Team_Operations/Free_Agency` | `runtime/decisions.py` (EVENTS and OWNERS) | 8 (the signings owner with its first event in step 7) |
| Decision-queue blocks for the reductions to 75 and 53 and the game-four freeze, scoped by season | `runtime/decision_queue.py` | 8 |
| A date-aware preseason roster limit | `runtime/rules.py`; `scripts/close_preseason_game.py` | 8 |
| Active/PUP and Active/NFI on the roster record, counted against the 90 and the 75; a limit that changes by date (90, 75, 53); unsigned rights (tenders, unsigned draftees) | `runtime/roster.py` and the roster record | 8 (the 90-man offseason roster from step 7) |
| The 2015 cut, waiver, practice-squad and designated-return deadlines as stored dated facts the checks read, and the two issue dates of the Roster Cutdown Report | The 2015 data area and calendar (none exists yet) | 6 (2015 opened) or 8 |
| One two-pass 2015 cutdown-rules library entry: Article 29 §§1 and 2, Article 30 timing, the 2015 designated return, the 2015 game-day list, practice-squad formation after the notice, the base eligibility terms (R5), the preseason waiver order and bonus acceleration on a release | `library/` (new file) | 8 |
| Plan credited service verified for every player who may be cut; `credited_seasons` is an Article 26 count and reads "Unresolved" in 43 of its 90 rows | `data/finances/financial_inputs.json` | 7 or 8 |
| Each disposition appends a dated transaction to the player's permanent record and a departure row with its rails disposition to the roster record | `data/people/players/`; the roster record | 8 |
| A check of My Cut Recommendations before Caldwell acts: the fixed headings, every name a Jacksonville-controlled player, each player named once within a stage across keep, move and conditional | Validation | 8 |
| A freeze record (a digest at filing) for Final 53 | The roster record or the decision record | 8 |
| 2015 rails data for August 30 to September 6, 2015 (claims, releases, practice-squad signings), built when the clock reaches it | `runtime/rails.py` and its data | 8, at the phase |
| 2015 cap-tracker support for cutdown dead money and acceleration | `scripts/render_jaguars_cap_tracker.py` | 7 |
| The page builders and checks for the three pages and their results, using step 7's brief issue history, and the tests in section 6, run on a copy | Builders and validation | 8 |

Outside this design, these process documents and code must name the new pages and rules; those changes belong to the build, not to this design:

- `docs/season_cycle_milestones.md` (the roster-cuts row): the three pages in `Roster_Decisions` and the per-event results in their owner folders, in place of the 2014 combined `final_roster_cuts.md`.
- `scripts/render_career_views.py` (the desk's "Roster decisions" link): the new pages.
- `docs/rebuild_plan.md` (the final-cuts row): the folder `Training_Camp_and_Preseason/Roster_Decisions`.
- `docs/update_workflow.md`: the owner of each cutdown result (rule 10), and the 2015 vested test from Plan credited service, not the 2014 accrued-season test.
- `foundation/templates/README.md` (the final-cuts row): results in `Team_Operations/Team/Roster`, `Team_Operations/Free_Agency` and `Team_Operations/Trades`, linked from the phase index; medical findings linked, not results.
- `AGENTS.md` line 23, `docs/update_workflow.md` (line 137) and `foundation/templates/position_battle_card_template.md`: from the first applied My Depth Calls in 2015, that record owns the depth decision; this belongs to the [position battles design](position_battles.md)'s build.
- `docs/rebuild_plan.md` (its list of rulebook lines left for the user to approve): add Document 7 §5.1 and Document 1 line 229, the question awaiting the user's decision above. Neither rulebook file is edited.
- **Held on Q-R** (the [question awaiting the user's decision](#awaiting-the-users-decision) about Document 7 §5.1 and Document 1 line 229). These changes are made only after the user approves Q-R and are listed as held until then: the AGENTS.md lines 117, 119 and 121 and the AGENTS.md routing of 2015 camp, preseason-game and cutdown work to the new pages; `docs/update_workflow.md` line 125; and the rescoping of the eight-section references to 2013 and 2014 in `foundation/templates/preseason_output_template.md`, the `foundation/templates/training_camp_and_preseason/` README, `preseason_review.md` and `player_assessment.md`, the offseason and regular-season output templates, the `foundation/templates/README.md` catalog rows, `docs/preseason_game_reports.md` and `docs/camp_and_preseason_reports.md`. Until the user decides they stay as written, and the pages and their code are still built in step 8 but not issued for a 2015 preseason. Line 117 ("Preseason follows the existing bulk workflow and game gates") rests on Document 7 §5.1, so until then the 2013 and 2014 methods it describes apply. The [position battles](position_battles.md#7-build-integration-points-and-the-files-to-change) and [preseason games](preseason_games.md#i-what-the-build-changes-outside-this-design) designs hold the same lines in the same words.
- `state/current_job.json` row 5: Stone recommends and Caldwell decides on player contracts; listed in the [February and March design](re_signing_and_free_agency.md)'s build.
- `docs/event_inserts.md` (section A, item 3) and the event router: two briefs may carry inserts at once when phases overlap, each event once, on its own phase's brief (rule 3); item 3 assumes a single active brief.

## 4. Single-fact ownership and event lifecycle

**Data owner design:** each player has one permanent identity and contract history (`data/people/players` and the contract sources). Each season event has one owner (rule 10): a waiver, release or reserve placement at the roster owner with its contract effect in the finance inputs; a medical diagnosis or restriction at the medical owner; a trade offer and its disposition at Trades; a practice-squad contract at Free_Agency with its roster effect on the roster record. `Final_53.md` is built from the roster record at the filing, never a table retyped from Stone's recommendation.

**Event fields:** each event uses the fields of the [event inserts design](event_inserts.md), section A, item 1 (id, kind, raised_at, known_to, source, authority, state, deadline, options and evidence, effects, and links to the owning records), and its result page carries the event-record line from which Record.md is built. There is no second schema. The reader never sees these identifiers.

**Each independently resolved event, including every released or waived player, has its own dated outcome**, successful or not. A 20-player reduction therefore has 20 readable outcomes, linked from the phase index. If a player is later claimed, that is a new dated event, not a rewrite of his waiver. A trade or medical record that already owns an event is linked, not recorded twice. A role appointment is Stone's depth decision, not a Caldwell transaction, and goes to the depth data.

State transition for one player:

1. **Proposed:** a staff or Stone recommendation, visible to Caldwell, with no roster effect.
2. **Caldwell decides:** he verifies the signed contract, Plan credited service, medical and legal status and the deadline, and records the action submitted; a waiver period is not skipped.
3. **Submitted waiver or release:** a dated result for the action, with the owner updated. A vested veteran's contract is terminated and he is free (rule 16); a waiver stays open for claims.
4. **Waivers close at noon on September 6:** another club's claim only where the player's real next move was a claim in that window (rule 17); Jacksonville's own claims awarded by the waiver order (rule 18); otherwise the player clears. Each result is dated at its owner. Nothing signs him back automatically.
5. **Practice squad:** only after the personnel notice, eligibility and waiver clearance or other free-agent status. An approach is decided by the market draw where the player really signed in the same window, and otherwise signs (rule 19).
6. **Views:** rebuild the roster, finances, medical availability, any depth change Stone made, and Record.md from the event-record lines. Final 53 is not rebuilt after the filing. Rebuilding is idempotent and causes no transaction.

## 5. Stage-specific execution

### Before September 1: 75

Prepare a dated roster count from the actual contracts and list statuses. When the count is already at or under 75, Stone gets a FOR YOUR INFORMATION line with the count, no cut is made and the 75 section of his page is not requested. Otherwise the Roster Cutdown Report asks for his 75 section, and Caldwell decides which waivers, releases, injured designations or trades to execute, following Stone's lawful list (rule 8). Execute **only when the actor and the outcome are real**. Close the stage with its count and each filed decision; game four's freeze waits for it. A drafted or tendered player's unsigned rights do not count as a signed contract without a verified league status.

### After the September 3 preseason game four: 53

Reconcile only the completed game-four play-by-play, injuries and medical communications. Issue the 53-stage edition of the Roster Cutdown Report, carrying the 75 count. Stone's 75 section stays as answered; he fills the 53 section. Caldwell files the 53 by 4 p.m. ET on September 5, with a legality and cap review before and after. Final 53 is built at the filing and frozen. Stone's depth calls and inactives come from My Depth Calls and the Week 1 Game Plan, never from a roster table; every open battle card closes with his season depth chart (rule 13), and a role whose holder left goes to its ranked successor or to Stone (rule 9).

### September 6 and beyond

At noon ET the claims resolve (rules 17 and 18), then the personnel notice and the practice-squad approaches (rule 19). After 4 p.m., the designated-for-return rule applies to a qualifying case. Each concluded outcome gets its own dated result, and the roster page is rebuilt. Final 53 stays as filed on September 5.

## 6. Proposed regression tests (not run)

### Dates, lists, status accounting

1. At October 5, 2014 the 2015 53 cannot contain any player inferred from a future transaction.
2. Year selection uses the 2015 September 1, 4 p.m. 75 deadline, not 2014's August 26.
3. Year selection uses the 2015 September 5, 4 p.m. 53 deadline, not 2014's August 30.
4. Game four on September 3 cannot freeze while the 75 stage is unresolved or the count exceeds the limit.
5. A valid 74-player contracted count passes the 75 deadline without a fabricated release and asks Stone nothing beyond a FOR YOUR INFORMATION line with the count.
6. A true 76-player count cannot pass the 75 deadline without an authorized action or a valid exemption.
7. Four unsigned tenders are not automatically four active game participants, nor automatically all free agents.
8. A rights-only unsigned player does not alter the roster count unless the period classification requires it.
9. A 53 built from 52 distinct names cannot be described as exactly 53.
10. A 53 with a duplicated multiposition player is counted once and rejected as a duplicate row.
11. Reserve/Injured, Active/PUP and Active/NFI have distinct counted or not-counted status by lawful case.
12. Moving one player onto a properly eligible reserve list changes the count only at the recorded effective time.
13. A projected medical return never triggers automatic clearance or activation.
14. An unavailable but retained player may occupy a 53 place without being dressed for Week 1.
15. A plan or cut report for the 2015 season cannot read the real Jaguars' 2015 roster changes.

### Authority, football decisions and individual events

16. Stone's recommendation changes no contracts or control before Caldwell acts.
17. When Caldwell removes a player, the next player in Stone's standing depth order takes his role and Stone gets FOR YOUR INFORMATION; a starting or specialist role with no ranked successor goes to Stone as ACTION REQUIRED before the Week 1 Game Plan freezes.
18. A genuine unresolved head-coach depth decision is returned to Stone even during a roster deadline.
19. A 75-stage Stone recommendation is preserved when his later 53 preference changes.
20. The same football recommendation phrased differently cannot change a market draw or a waiver award.
21. Caldwell's decisions are protagonist-blind: he departs from Stone's lawful list only on a criterion written into the Roster Cutdown Report before Stone answered, never because of Stone's phrasing.
22. A requested Stone answer remains open when blank; silence is never an agreement to release a player.
23. Unrelated league events proceed while a particular recommendation waits for Stone, unless it holds the event (rule 6).
24. One 20-player Caldwell cut batch creates 20 distinct dated result pages and one phase index.
25. A rejected trade proposal during the cuts gets its own dated Trade result, never buried in `Final_53.md`.
26. A failed claim or a practice-squad approach lost in the market draw gets a dated unsuccessful outcome, not an invented signing.
27. Each corrected injury list or waiver result keeps the original issued state and the later outcome history.
28. The phase index contains links, not copies of the transaction narratives.
29. An unchanged roster after an unsuccessful trade keeps every player contract and right.
30. Pages written before 2014 Week 6 keep their exact bytes, the 2014 August cutdown results included.

### CBA waivers, injury and practice squad

31. A player who has finished the season of his fourth year of Plan credited service, placed on waivers between February 1 and the trading deadline, has his contract terminated and is free.
32. A player short of that is routed through waivers, not a same-day free-agent signing.
33. The code distinguishes Plan credited service (waivers, termination pay) from the Article 26 count in the finance inputs and from accrued seasons (practice-squad eligibility); where Plan credited service is unresolved, the move is a waiver request and its result page says a fourth credited year would make it a termination.
34. No outside club contacts a player while he is on waivers.
35. The September 6 noon waiver resolution cannot be assumed in the September 5 Final 53.
36. A player claimed by another club cannot also be on Jacksonville's new practice squad.
37. A waiver-cleared player is not automatically re-signed by Jacksonville, and goes to another club only by his real same-kind, same-window move.
38. A player waived with the injured designation does not enter reserve/injured until he clears and the reversion applies.
39. An injury settlement cannot be issued without its actual contractual process and assent.
40. A practice-squad approach is declined only by the market draw, for a player who really signed in the same window; a player with no real signing in the window signs.
41. At most ten practice-squad contracts under the 2015 agreement; an eleventh cannot be executed.
42. At most two players with up to two accrued seasons; a third is refused unless otherwise eligible.
43. The practice-squad season counter follows the 2014 and 2015 six-game rule, not the old three-game rule.
44. A 2015 practice squad is not filled before waiver clearance and the personnel notice.
45. A player on the 53 at filing and injured later may enter the designated-return process only after 4 p.m. on September 6.
46. An early pre-window reserve/injured placement does not gain a designated-return label.
47. The recovered or adopted contract schedule controls each cap effect, labelled a reconstruction where adopted; termination pay arises only for a vested veteran released after the first regular-season game.
48. A cut player's charge does not vanish from the cap while bonus proration or a guarantee remains.
49. Jacksonville's claims on other clubs' waived players are awarded by the waiver order then in force, Jacksonville's place from the career's 2014 standings: it wins only when ahead of the club that really claimed the player, and a claim on a player no club really claimed is awarded.
50. Other clubs claim a Jacksonville waived player only where his real next move was a claim in that window, and a departing player follows the rails only on his real public date and under the same-kind, same-window rule.

### View and record validation

51. The three pages are written in `Roster_Decisions`, never the parent folder, and Final 53 is not the roster owner.
52. The depth data (`game_depth_chart.json`, `working_depth_chart.json`, `update_log.json`) remain the depth owner, with legally retained players only; Final 53 and My Cut Recommendations link the built depth chart.
53. A released player cannot appear on the Final 53 at the same effective time.
54. A complete 53 includes every signed counted player exactly once, whatever his roles.
55. A retained medically unavailable player does not appear on the Week 1 game-day actives before clearance.
56. The 2015 Week 1 active list follows the 2015 rules entry's game-day limit, with no later 48-player or eight-lineman rule.
57. An actual 53 may lawfully differ from prefilled position counts; no invented quotas.
58. An open battle card stays open until Stone closes it, at the latest with the season depth chart at the reduction to 53; keeping a player declares no winner.
59. A roster deal with another club has its own signed acceptance and notice; no phantom trade.
60. A roster change rebuilds the team, contract and cap pages once from the data owners.
61. Every closed event has one stable identifier and one dated reader result.
62. An index link can point only to an already concluded event, never an unissued page.
63. Rebuilding pages does not execute waivers, redraw a claim, backdate the roster or change Final 53, which matches its freeze record.
64. An `Event_Results.md` omnibus cannot replace any dated individual outcome, failed pursuits included.
65. The clean-page check rejects internal paths, identifiers, disclaimers, invented rating tables, invented media dialogue and unsourced exact salaries on the coach-facing pages.
66. The 2014 salary-cap, season history, draft and free-agency personnel, camp and preseason records and game files remain unchanged.
67. My Cut Recommendations is checked before Caldwell acts: the fixed headings are present, every name is a Jacksonville-controlled player, and each player is named once within a stage across keep, move and conditional.
68. The annual index carries the correct owner links and per-event dates, without duplicate narratives.

## 7. Acceptance and no-commit rehearsal

A future implementation pull request should run a synthetic 75, preseason game four, 53, waiver claims and squad signing sequence in an isolated copy with no actual career progression. First stage: 74 signed players at the 75 deadline produce zero cuts and a FOR YOUR INFORMATION count. Second: 76 require one authorized action before game four freezes. Third: a 75-to-53 reduction outputs **22 player-level** results when 22 players leave, not one aggregate 'roster downsized' page, and Final 53 is built once and frozen. Fourth: three practice-squad approaches lost in the market draw remain three dated results, and Final 53 is unchanged. Confirm the single roster record and the individual owners, no double charges, no change to a 2014 file and unchanged game state. Then run the repository validation, the clean-page checks and the existing game readiness separately. These 68 tests are proposed, not executed here.
