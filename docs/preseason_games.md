# Every Preseason Game: implementation and validation contract

**Status:** Uploaded by the user on October 20, 2026 and adopted; built in step 8 of the [rebuild plan](rebuild_plan.md). Corrected after the process check of the spring and summer designs, with the lead's rulings and the settled answers this design states as its own rules (sections A, B, D and E). The templates are in [foundation/templates/preseason_game/](../foundation/templates/preseason_game/), the worked example is [docs/examples/preseason_games_jacksonville.md](examples/preseason_games_jacksonville.md) and the research register and repository assessment are in [docs/preseason_games_research.md](preseason_games_research.md). Two questions in this design are awaiting the user's decision (section H): rewording two rulebook lines for per-game preseason pages, and how 2015 practice observations are produced. The process documents and code the build changes are listed in section I; this design edits none of them.

As uploaded: **Status:** Proposed design, not implemented or executed. Repository inspected at `main` tree `75fd41fbfc5ed0363d9f6cb68b5bef37a6583f24` on 2026-10-20. No source file, game, player status, decision queue or state has been changed by this package.

## Every Preseason Game: research and design package

Three full coach-facing Markdown templates, a detailed implementation specification, a completed 2014 Jacksonville evidence example, 2011 CBA and contemporary research sources and a repository assessment. As uploaded the package also carried its own event-result reference and a four-game checklist. The process check folded both in: every resolved event uses the one shared result form (section D), and the per-game steps are in section E.

**Status:** Design-only. The active Jacksonville career remains at October 5, 2014 after regular-season Week 5. The 2015 fixtures are historically sourced future calendar appointments. Neither completed 2014 preseason nor any unplayed game, staffing, health, player status, transaction or performance was changed.

### Contents

1. [Preseason Game Briefing](../foundation/templates/preseason_game/preseason_game_briefing_template.md)
2. [Preseason Game Plan](../foundation/templates/preseason_game/preseason_game_plan_template.md)
3. [Preseason Game Report](../foundation/templates/preseason_game/preseason_game_report_template.md)
4. Event results: the [shared event result](../foundation/templates/event_inserts/event_result_template.md), one per resolved event at its owner (section D); the preseason pack has no result form of its own
5. [Implementation and Validation Spec](#a-operating-interpretation-and-governing-authority), **70 proposed tests** (56 as uploaded, 14 added by the process check)
6. [Worked Jacksonville Example](examples/preseason_games_jacksonville.md)
7. [Research and Sources](preseason_games_research.md#preseason-game-research-and-source-register-20142015)
8. [Repository Assessment and Blockers](preseason_games_research.md#preseason-games-repository-assessment-and-implementation-blockers)
9. [Per-game sequence](#per-game-sequence), which replaces the four-game checklist

Every preseason game repeats the three main pages in its own `Game_0N` folder, one set for each game in the season's fixtures, with that game's My Responses page for any event inserted in its briefing. Dated off-field events get standalone canonical owner results, even when rejected. The existing 2014 full `output.md` documents remain frozen history; no second competing 2014 report is created by this design.

## A. Operating interpretation and governing authority

Each actual preseason game has **one three-page decision workflow**, in its own folder, `Training_Camp_and_Preseason/Preseason_Games/Game_0N/`:

1. `Preseason_Game_Briefing.md`, brought by the coaching staff (the registry's "The coaching staff": the coordinators and the special teams coordinator, with the position coaches and the medical staff) using facts knowable at its issue time. It proposes; it decides nothing. The staff names and the calling arrangement on it are read at issue from the [coach records](../data/people/coaches/) and the parties and standing instructions of the [job record](../state/current_job.json), never from the template. No scout is named as an author.
2. `Preseason_Game_Plan.md`, Stone's owned and editable head-coach instruction for that game: its lineup, roles, holdouts, offensive and defensive direction, specialist groups and rotation. He answers it once; the check returns exact problems before anything runs, and the page stays as the record of his decision.
3. `Preseason_Game_Report.md`, the game's one result page. It is opened before kickoff with its preparation and pregame media, which are fixed at the game-day freeze (the Game Report's pregame freeze, `scripts/freeze_pregame.py`, with a `pregame.json` in the game's data folder), and completed after the verified game closes with the game narrative, postgame media, football review and the complete generated box score last. From 2015 it is the game's sole canonical *reader-facing result*, not an alternate recap beside an `output.md` owning identical facts.

Use the registered `runtime.decisions.REGISTRY['preseason_game']` page names; the plan is "Preseason Game Plan" everywhere. **Instantiate one independent set of pages for each game in the season's fixtures** (games 1 to N), not a single page for the entire preseason. Once the rulebook lines of section H are reworded, the bulk preseason turn does not survive from 2015 as a way to run games: each game needs its own checked Preseason Game Plan before its inputs freeze, though a chat may still report several closed games together. A season has at most five: 2011 CBA Article 23 §7 allows a fifth game only for the two clubs in the Hall of Fame Game or an American Bowl game scheduled around its date. 2015 has four.

**The cross-game review has one owner.** The staff's cross-game synthesis is a dated "Preseason review through [date]" section in the latest closed game's Preseason Game Report at the review's date (at the latest, once the last game closes), guided by the [consolidated preseason review guide](../foundation/templates/training_camp_and_preseason/preseason_review.md) and linking the earlier reports. There is no separate summary page. It summarizes and links prior games; it is not a substitute for any game's report or off-field event result, and an earlier dated review stays where it was written. The reused Game Report checks (`runtime/game_report.py`) cover it as part of that report.

**From the 2014 pages to the 2015 pages.** The 2014 files stay as written. From 2015 each 2014 page maps to one new owner:

| 2014 page | 2015 owner |
|---|---|
| `Game_0N/README.md`, the ex-ante camp questions | The briefing's staff questions |
| `Preseason Game N_ HC.md`, Stone's authored plan | The Preseason Game Plan |
| The frozen-inputs record in the README | `applied_plan.json` in the game's data folder, as for game weeks |
| `output.md` | The Preseason Game Report |
| `Game_0N/README.md` as the folder's page | A built index of the folder: the three pages, My Responses and the linked event results, as the game-week index is |

The game is an exhibition, but its participation, medical, signed-contract eligibility, transactions and CBA practice constraints are real.

**Authority.** Stone decides depth, roles, the game's lineup and holdouts, practice and his staff, and takes, delegates or takes back calls. David Caldwell decides acquisitions, the draft, contracts, waiver claims and cuts, on Stone's recommendation. Qualified medical staff decide diagnosis and clearance.

**Calling arrangement.** The arrangement in force at the October 5, 2014 clock is the job record's continue-calling-arrangement instruction, shown in the [staff page's phase-control table](../career/2014/Team_Operations/Staff/coaching_staff.md): Stone calls the offense (since the 2013 season) and the defense (from September 28, 2014); Romeo Crennel transmits the defensive call and Daryl Smith declares the front; Mike Westhoff calls special teams (from February 11, 2014); Mike Tice leads the offense day to day. The appointment behind it is Stone's head-coach appointment of January 15, 2013; no appointment is dated October 5, 2014. The arrangement persists until Stone changes it, and nobody asks him again. A 2015 briefing shows the arrangement in force at its issue, read from the job record; it is not assumed to survive the unplayed January 2015 staff phase.

**Calls.** Any call in the active playbook may be named on a Preseason Game Plan, for any situation, whether or not practice covered it, an earlier sheet carried it or the staff carded it. Only the no-hindsight lock refuses a call: one from a book whose range starts after the season. "Opening ideas" lists the calls Stone wants early, in his order of preference, and every call in the book stays available. A call is open to every rotation group unless Stone's page restricts it to one (the 2014 call sheets' optional `units` field). Players are evaluated only on taught material: work on a call that the book holds but practice never taught is reported as what happened, never judged as a mastery failure. No "practiced call required" gate is imposed.

**Game management in preseason.** Stone's standing fourth-down, two-point and kickoff rules are not applied in a preseason game until the plan-level engine decision (the user chose the plan-level version on October 20, 2026; it is switched on at a week boundary the user chooses, recommended for the 2015 opener, [rebuild plan](rebuild_plan.md) change log). A Preseason Game Plan's fourth-down, two-point, kickoff and defensive lines are recorded intent and staff direction: stored, shown and kept as his record, but not compiled into the game, and the page says so in football words. In a preseason game the engine's own preseason handling decides fourth downs, tries and kickoffs, and the only live stop is the consequential injury pause. Today the production path refuses these blocks in preseason (`runtime/game_runner.py:100-121`; `runtime/kernel.py:114-116`, `:141`, `:169`, `:191`), and the rebuild leaves the engine untouched (rule 2). Whether a preseason game should take them is part of that engine decision.

**Dressing.** The standing healthy-inactive rule was written for the 46-player game-day list and took effect August 31, 2014; it does not apply in preseason. The whole controlled roster may dress (for 2015 game 4, the 75). The only holdouts are players Stone names for football reasons and players the medical staff rules out.

Stone's head-coach agreement covers the 2013 to 2016 seasons: four years, fully guaranteed, accepted January 15, 2013; assistant budget and authorities remain as recorded. No preseason win changes the regular-season head-coach record. The 2015 playing-rule changes must be applied before freezing 2015 game inputs.

## B. Historical calendar and information gates

Historical 2015 Jacksonville fixtures, **not played in this career**:

| Game | Official opponent | Date, 2015 | Kickoff ET | Dated source |
|---|---|---|---|---|
| 1 | Pittsburgh at Jacksonville | Fri Aug 14 | 7:30 p.m. | Jaguars April 20 release |
| 2 | Jacksonville at New York Giants | Sat Aug 22 | 7:30 p.m. | Jaguars April 20 release |
| 3 | Detroit at Jacksonville | Fri Aug 28 | 8:00 p.m. | Jaguars April 9 and April 20 releases |
| 4 | Jacksonville at Washington Redskins | Thu Sep 3 | 7:30 p.m. | Jaguars April 20 release |

The dates and their sources are owned by the [2015 calendar](../career/2015/Calendar.md) and its [source register](../library/2015_historical_calendar.md); this design links them and never restates a rule or a date as its own. The club announced opponents, sites and weeks on April 9, 2015: Pittsburgh at home in the week of August 13 to 17, at the Giants in the week of August 20 to 24, Detroit at home on Friday, August 28 at 8 p.m. on CBS, and at Washington on September 3. The April 20 club release gave the exact four dates and kickoff times. A briefing issued before April 9 knows no 2015 preseason fixture; one issued from April 9 to April 19 knows only the April 9 framework. The calendar's register starts preseason knowledge at April 20, so the April 9 row is added there in the step 6 calendar check (section I).

The extra-point rule adopted May 19, 2015 for the 2015 season (by a 30 to 2 vote, to be reviewed after that season) moves the kicked try's snap to the 15-yard line, keeps two-point attempts at the 2 and lets the defense score two points on a returned try. It is unknown inside the story before May 19, 2015, any later status of the rule is gated to its own public date, and it **cannot** silently be applied to 2014 game records. A two-pass 2015 playing-rules record in the library owns it, built with the 2015 season release before August 14, 2015 (section I). This is a game-release requirement, not just a prose note.

**Mandatory cutdown interaction:** the 2015 reduction to 75 on Sept 1 before 4 p.m. ET occurs **before** preseason game 4 on Sept 3, and therefore gates the legal roster and the inputs for game 4. The reduction is Caldwell's, on Stone's recommendation ([final cuts design](final_roster_cuts.md)). Game 4's inputs freeze only after it is recorded, and game 4 dresses only players on the 75. It holds game 4 only, never games 1 to 3. Final 53 is Sept 5 before 4 p.m. ET, after game 4; it is built at the filing and frozen, and there is no separate page for the cut to 75. The deadlines are known inside the story from their public announcement (the 2015 calendar's source J, July 15, 2015), before any preseason briefing is issued. The 2014 cutdown dates differ; never hardcode one season's deadlines for the next. A 2015 calendar is a historical scheduling reference, not a roster, opponent lineup, player performance or result oracle, and no real 2015 outcome (a cut list, an article about the real cutdowns, a real score, the real Jaguars' practice count) is ever an input.

**Other clubs' players.** The opponents' players follow their real moves on their real dates under the historical league rails (`AGENTS.md`), each usable only from its real public date; rails data for the preseason is built when the clock reaches it, and the opponents' preseason rosters are researched at the August 2015 clock. Jacksonville's own roster comes only from this career's decisions. A claim on another club's waived player follows the waiver order then in force; Caldwell decides whether to claim, on Stone's recommendation ([final cuts design](final_roster_cuts.md)).

## C. Repository reality, reusable machinery and specific conflicts

| Existing file or subsystem | Verified function | Required adjustment |
|---|---|---|
| `runtime/decisions.py` | `preseason_game` registered with `implemented=False`; its shared `training_camp_and_preseason` place resolves to the **parent `Training_Camp_and_Preseason` folder, not a particular Game_0N folder**, and takes no game number (`:56`, `:86-87`, `:144-154`) | **Fix route:** a page set like `WeekPages` for game N (folder `SeasonPaths.preseason_folder(n)`, data `preseason_data(n)`, the briefing, the plan, `My_Responses.md`, `staff_briefing.json`, `briefings.json`, `applied_plan.json`, `pregame.json`). Camp and final cuts keep their own routes. Mark implemented **only after** tests prove the workflow. |
| `runtime/seasons.py`, `runtime/season_layout.py` | Year-specific `SeasonPaths.preseason_folder(n)`, `preseason_data(n)` (games 1 to 5) and logical folder map | Use these exclusively. Add `preseason_report(n)`, returning `output.md` for 2013 and 2014 and `Preseason_Game_Report.md` from 2015, on the pattern of `SeasonPaths.game_report`. No new hardcoded `career/2015/...` in runtime or builders. |
| `runtime/preseason.py` | Builds a preseason package from controlled roster, frozen game depth, call sheet, opponent and rotation; its game records are kept apart from the regular season's | Keep as compiler and adapt to each year's rules and current source records. No illegal move or defaulting an unknown roster to 2014. |
| `runtime/rotation.py` | Possession-boundary substitutions, optional unit blocks, default rotation and validation | Compile Stone's natural-language rotation into exact supported blocks; warn that a snap cap ends at a possession boundary. Do not silently invent missing player IDs or counts. |
| `runtime/game_plan.py`, `scripts/check_game_plan.py`, `scripts/apply_game_plan.py` | The Game Plan parser, compiler, check and apply, with the playbook lock, the exact-name rule, the roster and medical checks and the frozen and paused refusals | Model the Preseason Game Plan's on them: compile the page into `call_sheet.json`, `depth_chart.json` (holdouts in `game_day_inactives`) and `rotation.json`, whose `until` accepts possessions, snaps, quarter and possessions_after; keep the `units` restriction optional; keep the fourth-down, two-point, kickoff and defensive lines out of the compiled input; prove it by reproducing a 2014 game's frozen call sheet and rotation. |
| `scripts/render_game_week.py` | Builds the Game Week Briefing from stored facts; its staff line comes from the coach records (`:528-539`) | Model the briefing builder on it: staff text stored in `staff_briefing.json` with its author and date and shown "To come" when absent, the issue record and reissue, the shared insert renderer, medical shown only as communicated, and the whole-roster dressing rule in place of the 46. |
| `scripts/close_preseason_game.py` | Runs one game through the private service; supports the E2 pause, writes the game record, fills the box score into `Game_0N/output.md` (`fill_output`, `:156-168`) and renders the stats; rejects a repeat closure | **Blocker:** the box score goes into `Preseason_Game_Report.md` from 2015 through `preseason_report(n)`, while 2014's frozen `output.md` pages and records stay unchanged. Do not render two competing results. |
| `runtime/game_report.py` | The Game Report's layout, Final and line-score checks, story scores, pregame freeze and the rule against statistics tables outside the appendix | Reuse these validators, made aware of preseason games, rather than writing new ones. Only the preseason header, sections and tables differ. |
| `foundation/templates/preseason_output_template.md` | Prior eight-section complete report, narrative and coaching review in the game section, stats and consolidated review | Do not erase this design. From 2015 the Preseason Game Report is the one result page for each game; the eight-section template stays for 2013 and 2014 history only, and the 2014 outputs stay as written. The new report owns their football substance: preparation, the pregame and postgame media (each with its "No ... media session was recorded." line when none was held), the game story, the coaching review and the full final box score. Old section 1 (coach status) becomes the header, with the preseason record from the closed games; old section 7, the personnel snapshot, is dropped, because the roster and depth chart pages own it. This alignment must be accepted and regression-tested. |
| `tests/test_preseason_game.py`, `tests/test_preseason_rotation.py` | 2014 fixture, PAT trial, input, rotation, repeat-close, pause and cross-mode isolation tests | Add 2015-specific contract, rule, fixture and page checks, leave 2014 proofs unchanged. |
| `runtime/decision_queue.py` | Current blocking events cover weekly inputs and close and the season stage and opening; `practice_plan` has no game freeze block (`:24-27`, `:65`) | Add `preseason_inputs` and `preseason_close` keyed by `(season, game)`, with Stone's plan and the E2 pause. Game 4's input freeze also waits on the recorded reduction to 75. Only an answer due before the game it holds stops the clock; unrelated business never holds a game. |
| `docs/event_inserts.md`, `runtime/decisions.EVENTS` | Shared event insertion and separate dated outcomes | Reuse the shared insert system, immutable issued editions, the one reissue rule (section A, item 6), the response page, the event owner and one-event, one-result rules (section A, item 5). Do not code a second insert router or a `Preseason_Event_Results.md` omnibus. |
| `docs/season_structure.md`, `runtime/events.py`, `scripts/render_annual_record.py` | Owner-based annual event index; records from event-owning Markdown pages | Each game gets one game event, from the report's event-record line; each separately concluded trade, transaction and so on gets its own owner and event; indexes link without copying accounts. |
| `runtime/seasons.py` release checks | `game_release_errors` refuses a game without a registered season release (`:316-336`) and judges all seven gates, the player-state table and binding included; its input files include the Week 1 depth library (`:121-122`, `:343-349`) | A 2015 preseason game needs the 2015 release record, all seven gates, before game 1 on August 14, 2015. The preseason package never reads the Week 1 depth library (its opponent comes from `opponent_roster.json`), and the real Week 1 charts are public only in September, so the preseason input check drops it. |

**Current implementation blockers:** The known 2014 kernel, service and prepared 2014 game artifacts do not constitute a released 2015 game environment. No 2015 controlled lineup, 2015 opponent camp roster, medical status, completed camp or in-world game plan exists at the October 5, 2014 live checkpoint. 2015 must pass the existing season handoff and **separate game-readiness and release gates**, with the release record registered before preseason game 1, not before Week 1. No template is permission to run a game with 2014 strength, roster, PAT or schedule data.

## D. Minimum source and state contract

`preseason_game` (one event) requires, before freeze:

- fixture: year, preseason ordinal, teams, local kickoff, venue, public-information gate, unique event ID, from the season's `fixtures.json` (`YEAR-preseason-NN-away-at-home`, written at the April 20 clock);
- current employment and authority, current-year effective offensive and defensive books, the standing instructions that apply to a preseason game;
- legal controlled roster, contracted and eligible list, reserve-list state, medical communication through the accepted date, Stone's actual depth and role choices;
- opponent dated roster and legitimate availability knowledge, researched at the game's clock under the rails (section B); no future injury, game or depth hindsight;
- prior camp and played-game evidence as of report issuance, and *source-labeled* pregame scouting assumptions;
- current game-specific Stone decisions under the page's fixed headings, preserved with timestamp, and the parsed freeze artifact for eligible players, offensive direction, specialist operation, lineup, rotation and holdouts;
- season-appropriate game rules, private service and release status and idempotency key.

Game close yields exactly one immutable game-result record and one readable `Preseason_Game_Report.md` with generated statistics, plus recorded pause answers and any actual new injuries and events at their owners. A dated coach assessment may be appended to opening player assessments only if sourced, not calculated from invented advancement. The play-by-play and box score are not themselves film; film analysis needs stored observational evidence or must be labeled unavailable.

**One owner for each fact.**

| Fact | Its one owner | What the preseason pages do |
|---|---|---|
| Practice observations | The camp `Training_Camp/training_report.md` | The briefing cites them by date; the report links them. A changed personnel view goes on the player's record. |
| The season depth chart | The team depth data, changed during camp and the preseason only through My Depth Calls ([position battles design](position_battles.md)); the camp Depth Chart page stays as issued, and Final 53 and My Cut Recommendations link the team depth chart page | The Preseason Game Plan sets only that game's lineup, rotation and holdouts |
| A position battle's closure | The battle card, folded in as the battle closure and closed by Stone's depth call | The report links the card and never closes a battle |
| Intent | The briefing proposes; the Preseason Game Plan decides | The briefing's tables and staff text are built from the roster, the medical records, the player cards and the camp training report, with the staff text stored with its author and date |
| Rules and dates | The library and the 2015 calendar | Linked, never restated as this design's own |
| Media | The [head-coach media method](head_coach_media_method.md) | The report's two media sections |
| The report's prose | The [game-output workflow](game_output_workflow.md), once the build adds the Preseason Game Report to it | The template keeps short prompts and links it |
| An event's result | The [shared event result](../foundation/templates/event_inserts/event_result_template.md), at the event's owner | The report's after-action part links each one |
| The cross-game review | The latest closed game's Preseason Game Report | |
| 2014 records | As written | Never rewritten |

**Events inside the phase.** An event inside the preseason (a trade call, a staff permission request, a roster move, a contract matter, an injury replacement) is an insert at the top of the active brief, under the title block, in the [shared insert template](../foundation/templates/event_inserts/brief_action_inserts_template.md)'s form: ACTION REQUIRED, FOR YOUR INFORMATION and COMING UP, each omitted when empty. Camp, the preseason games and the cutdown overlap in August, so two briefs may carry inserts at the same time. Each event appears once, on the first brief that fits it, and an inserted event is answered on that brief's My Responses page, by the [August routing table](position_battles.md#which-brief-carries-an-event-in-august) of the position battles design: a depth question on the Position Battle Report, even when its answer is due before a kickoff, answered on My Depth Calls; a roster-limit, waiver, claim or practice-squad matter on the Roster Cutdown Report once it has been issued; any other matter of a game's preparation or availability, or any other answer due before its kickoff, on that game's Preseason Game Briefing, answered on that game folder's `My_Responses.md`; and any other event on the Position Battle Report until the first Preseason Game Briefing is issued, then on the briefing of the next unplayed game, and after the last game on the Roster Cutdown Report. Stone answers inserted events only on a My Responses page, never on his Preseason Game Plan, which he answers once. Each resolved event (accepted, rejected, withdrawn, lapsed, granted or refused) gets its own dated result built on the shared event result form, in its owner's folder: roster moves and waiver claims in `Team_Operations/Team/Roster`, signings and undrafted pursuits in `Team_Operations/Free_Agency`, trades in `Team_Operations/Trades`, staff in `Team_Operations/Staff`, and Stone's own career in `career/Stone`. A medical incident has its existing medical owner, not a duplicate transaction write. A trade rejection has its own dated result, even if no roster change. An existing standalone owner record, such as a completed trade, is that event's result; no second narrative is written. A brief is reissued only under the one reissue rule ([event inserts](event_inserts.md), section A, item 6), and only an answer due before the event it holds stops the clock.

**Event relationships:** briefing inserts -> My Responses (only for real events) -> individual result at its owner; Preseason Game Plan -> frozen game inputs -> game result -> single game report -> phase indexes. The game and each off-field event have distinct identities.

## E. Execution and atomicity

1. At the game's date, read the fixture, job authority, eligible controlled roster, medical holds and the latest actual coaching evidence, and issue the game's briefing. The page is an as-of view, not an independent fact source.
2. If Stone's answer is missing, preserve the unanswered plan and block that game's input freeze. His text remains verbatim on his page; the compiler creates structured input only after checking players, book names, legal dates, roles, no duplicate lineup or roster and use constraints, and it keeps the game-management lines as recorded intent.
3. Reissue the briefing only under the one reissue rule ([event inserts](event_inserts.md), section A, item 6): a new event needs Stone's answer, a dated finding materially changes a choice still pending, or an answer falls due before the next scheduled issue. Every issued edition is kept beside the current page with its date in its name, as the Game Week Briefing's are, and its issue record goes in the game's `briefings.json`; the current view points to the latest, and the plan's "Briefing used" line names it.
4. Freeze the accepted plan **once** and stamp all source revisions. At the same game-day commit, fix the report's preparation and pregame media. Post-freeze off-field event changes do not mutate that package; a legitimate subsequent roster or health change must follow the existing pregame re-approval and invalidating rules. Never reroll with a convenient new input.
5. Confirm the season release (all seven gates), the season's try rule and that the game is in the season's fixtures. Run the one-game private-service event exactly once. On an E2 consequential Jacksonville injury removal, stop for Stone's answer unless his valid prior instruction covers it; continue only from the existing frozen event.
6. On closure, render the game narrative from the verifiable play-by-play, actual unit rotations, special teams, substitution and injuries; write the postgame media, the review and the after-action part, then the complete generated box score last under "Full game statistics", with nothing after it. Link each off-field event's result at its owner. Do not infer film or dialogue from statistical totals.
7. Update the game-specific preseason records and season current views from actual owners; link the battle cards without closing a battle; do **not** change regular-season standings, awards or records, and do not create extra player grades. When the staff reviews the preseason so far, and at the latest after the last game, write the dated "Preseason review through [date]" section in the latest closed game's report, without rewriting earlier games' histories or reviews.
8. Run read-only validators and shadow checks before actual future integration commit. Keep the 2014 legacy path checks byte-stable and commit only under the authorized rebuild PR flow, not as part of this design package.

### Per-game sequence

This replaces the uploaded four-game checklist. It is an internal routing aid, not a coach-facing page and not permission to play a game. Each game in the fixtures has its own pages, event identity and result. The build merges these rows into the preseason row of the [season cycle milestones](season_cycle_milestones.md) and a preseason section of the [run sequence](run_week.md) (section I).

| Game | 2015 historic appointment | Prerequisites before its inputs freeze | Next transition |
|---|---|---|---|
| 1 | Aug 14: Pittsburgh at Jacksonville, 7:30 p.m. ET | Season opened and its release record registered (all seven gates); camp under way; current 2015 contract, health and roster owners; the opponent's roster researched at the game's clock; Stone's checked Preseason Game Plan | Close game one; link injuries and event results; battle cards stay open; no automatic role award |
| 2 | Aug 22: Jacksonville at NY Giants, 7:30 p.m. ET | Actual post-game-one observations and changes, no real-life scores, a new game-two plan and rotation | Close game two; link injuries; the coming reduction to 75 appears as COMING UP on the brief then active, until the Roster Cutdown Report is issued |
| 3 | Aug 28: Detroit at Jacksonville, 8 p.m. ET | Post-game-two eligibility, the staff's comparisons, the defensive communicator in force and the opponent's information gate | Close game three; the reduction to 75 is due Sep 1 before 4 p.m. ET, Caldwell's on Stone's recommendation |
| 4 | Sep 3: Jacksonville at Washington Redskins, 7:30 p.m. ET | The reduction to 75 recorded; the eligible list is the 75; Stone's fourth plan | Close game four; carry the findings to the 53 before Sep 5 at 4 p.m. ET |

**Freeze checklist (each game):**

- [ ] Fixture, venue and kickoff from the fixtures and the 2015 calendar, inside the information gate; team identity uses 2015 naming.
- [ ] Staff, calling arrangement and active playbook from the actual current year's records, not assumed 2014 carry-forward individuals after unplayed events.
- [ ] Controlled player list, medical clearance and restrictions and transaction dates checked for the game's day.
- [ ] One current issued briefing with earlier editions kept; genuine inserts only, each event on one brief.
- [ ] One Stone plan accepted, his words preserved; the game-management lines kept as recorded intent.
- [ ] Lineup, replacement roles and rotation compiled legally; no forced exact snaps or targets.
- [ ] Season release confirmed, including the season's try rule and all private service input gates; game 4 waits for the 75.
- [ ] Game package and the report's preparation and pregame media frozen once; an unrelated event cannot change them.

**Closure checklist (each game):**

- [ ] Exactly one completed exhibition event, with result, box score and rotation reconciled.
- [ ] E2 pauses answered only by Stone or an applicable valid standing direction.
- [ ] Preseason stats separate from regular-season and postseason counts and awards.
- [ ] Report contains the football narrative, both media sections, unit and role assessments supported by the game record, and the complete box score last.
- [ ] Medical incidents reside at medical owners; no unrecorded return-to-play assumption.
- [ ] Each separately completed trade, signing, rejected offer, injury-list transaction or hiring pursuit has its own dated result in its owner's folder; the report's after-action part links it.
- [ ] Position battles stay open until Stone's actual depth calls; Caldwell's cuts are his own decisions on Stone's recommendation.
- [ ] Score, outcomes, current-year roster and frozen game package remain unchanged when the next game opens.

## F. Proposed regression tests (not executed)

### Calendar, eligibility and 2014 preservation

1. On Oct 5, 2014 no 2015 preseason report, lineup or score may be closed.
2. Game 1 2015 is Pittsburgh at Jacksonville on Aug 14 at 7:30 ET; source gate April 20 for precise timing.
3. Game 2 2015 is at New York Giants on Aug 22 at 7:30 ET.
4. Game 3 2015 is Detroit at Jacksonville on Aug 28 at 8 ET; national timing announced April 9.
5. Game 4 2015 is at Washington on Sep 3 at 7:30 ET, and Washington is the contemporary Redskins.
6. An Aug 2015 game does not include players removed at the Sep 1 reduction when freezing game 4.
7. The Sep 5 final-53 action does not retroactively change the Sep 3 game roster.
8. All completed 2014 preseason pages and game records retain identical bytes and four distinct game IDs.
9. A 2014 game retains that year's PAT implementation, not the 2015 rule adopted May 19, 2015 for that season.
10. A 2015 kick try uses the 15-yard line, a two-point try the 2-yard line and can award defensive two points. (A 2015 season release test, outside step 8.)
11. A 2015 game is refused if the year-specific rule or release, private service or legal roster is missing.
12. A 2015 opponent camp roster cannot load a later Week 1 history as though known in August.

### Head-coach authority and plans

13. No checked Stone game plan means no game input freeze; opening a page never advances time.
14. The calling arrangement in force at issue (from the job record) continues without a repeated prompt.
15. Calling arrangement changes only on actual Stone instruction, not on program phase transition.
16. A referenced play from the active book is legal for any situation even if unpracticed.
17. A play from a later, not-yet-effective book is refused with the specific reason.
18. A player's name missing from the controlled roster is rejected and not replaced automatically.
19. A player unavailable medically cannot be inserted by the head coach as 'cleared'.
20. A legitimate voluntary football holdout by Stone is recorded without inventing medical status.
21. The plan's fourth-down, two-point, kickoff and defensive lines are stored and shown as recorded intent and never compiled into the preseason game; the page says so (a record-only check).
22. Game-day legal player availability honors completed earlier Caldwell transactions only.
23. A missing receiver or backup role with an available legal group produces a focused clarification, not an invented depth promotion.
24. A stated running-back touch or wideout target preference is not treated as guaranteed game distribution.

### Rotation, game result and causality

25. Whole-unit rotation blocks compile to valid offense, defense and special teams groups.
26. A snap ceiling ends at possession boundary, with actual snap overrun shown honestly.
27. A player may receive zero snaps if possessions never reach his block; do not write a failure evaluation.
28. Opposing team rotations are independent of which club is Stone's, under protagonist-swap test.
29. Rephrasing Stone's reason without changing actual inputs leaves the outcome packet identical.
30. A substituted quarterback is legally eligible and appears in actual team and drive snap records.
31. An E2 injury removal stops for Stone's uncovered consequential replacement.
32. A continuation reuses original event and private draw, not a new attempt or altered result.
33. A game cannot close twice or produce two conflicting final reports.
34. A scoring line without a matching scoring play or period fails output verification.
35. The full box score reconciles points, possession, attributed player stats and field position; unexplained residuals stay explicit.
36. Preseason game stats do not enter regular-season or playoff career totals.
37. An opponent's real 2015 score does not appear in the generated game outcome or as model evidence.
38. An output says 'tackle lost the rep' only with actual assignment or film evidence, not because a sack was charged at a slot.
39. A receiver with no targets is not classified as having run poor routes without observed route evidence.
40. A pressure producing a sack does not establish contain or correct peel responsibility without the relevant record.
41. Correct conversion and returner attribution uses actual 2015 rules, not the 2014 preseason PAT trial. (A 2015 season release test, outside step 8.)
42. Game review discusses actual first, second and reserve combinations, not a score-only recap.

### Individual events, rendering and navigation

43. Three separate concluded trade talks in one preseason game window, including rejections, create three dated owner-result documents ([event inserts](event_inserts.md), section A, item 5).
44. An unresolved trade inquiry creates no closed trade result and no player movement.
45. A single answered shared response does not merge distinct event conclusions.
46. A medical incident remains in the medical department and is linked, not copied under game output.
47. A material midweek event reissues the briefing under the one reissue rule; previous issued editions stay unchanged.
48. A rejected trade is visible on its final date even if a later game has not been played.
49. One canonical game report and one full statbook are produced, rather than the old `output.md` and a competing new duplicate.
50. All new reader-facing output passes `runtime.clean_pages` checks: no internal IDs, paths, system labels, fabricated grades or executable code.
51. The dated "Preseason review through [date]" section in the latest closed game's report links the earlier reports; no separate summary page exists.
52. Re-rendering a closed report changes neither game record nor incident outcome.
53. The annual event index points at the correct dated owner without duplicated event IDs.
54. Missing raw game evidence blocks factual claims but never prompts an invented number to fill a template.
55. All links are relative, path-mapped and do not point to a future season's created results; each game in the fixtures resolves its own `Game_0N` directory rather than the common parent.
56. Prior regression tests for 2014 preseason, postgame statistics, game packages and season isolation remain green.

### Added by the process check

57. The report has its Pregame media and Postgame media sections; with no session held, each carries its one "No ... media session was recorded." line.
58. The report's preparation and pregame media are fixed at the game-day freeze; a later edit to them is refused.
59. The report's header reads "[Away] at [Home]" and "Final: [Winner] [score], [Loser] [score]", and the reused Game Report validators check it.
60. "Full game statistics" holds only the box-score markers, and nothing but blank lines follows them.
61. The plan check refuses a page whose "Briefing used" does not name the current issued edition; "Baseline: Carry Game N" starts from that game's frozen instruction set.
62. Opening ideas are read in order of preference, and every call in the book stays available.
63. A call is open to every rotation group unless Stone's page restricts it to one.
64. The whole controlled roster may dress (the 75 for game 4); only Stone's football holdouts and the medical staff's rule-outs sit out, and the healthy-inactive rule is not applied.
65. Game 4's inputs do not freeze until the reduction to 75 is recorded; games 1 to 3 are never held by it.
66. With the Position Battle Report, a Preseason Game Briefing and the Roster Cutdown Report open together, an event appears on one brief only and is answered on that brief's My Responses page.
67. The briefing's staff names and calling arrangement come from the coach records and the job record at issue; the template carries no names.
68. A player's work on a call the book holds but practice never taught is not judged as a mastery failure.
69. A season with a fifth game for a Hall of Fame Game or American Bowl club gets a fifth set of pages; a season with four gets four.
70. A 2015 preseason game requires the 2015 release record (all seven gates) before game 1, and its release inputs do not include the Week 1 depth library.

## G. Acceptance sequence (future integration, not run here)

Use a **fixture-only 2015 dry run** first (no players or results), then a separately labeled synthetic season with fabricated test fixtures confined to `tests/`, then a no-write, all-four-game walkthrough on an isolated 2014 clone comparing closed output bytes to originals. The Preseason Game Plan compiler reproduces a 2014 game's frozen call sheet and rotation from a page written in its words. Verify the first three games' roster counts, the Sep 1 reduction before game four, and final 53 after game four. Finally exercise three independent off-field concluded events, one rejected, and verify three dated outputs and no duplicate account. Actual 2015 simulation remains blocked until career events and the 2015 season release allow it.

## H. Awaiting the user's decision

Neither question below is adopted. Each recommendation is shown as a proposal only.

1. **Q-R: rulebook lines for per-game preseason pages (awaiting the user's decision).** Document 7 §5.1 (`foundation/07_Game_Simulation_and_Resolution_Engine.md:188`, a single bulk preseason turn, restated in the template line of §5.2 at `:192`) and Document 1 (`foundation/01_Project_Instructions.md:229`) still describe the preseason as one bulk output in the eight-section template. Rulebook text changes only with the user's approval, so neither file is edited here. *Proposal, not adopted:* yes, reword both for the per-game preseason pages and the camp and cutdown pages issued during camp, the eight-section bulk output kept for 2013 and 2014. Until the user decides, the rulebook stands as written: the build lists both lines among the rulebook lines left for the user's approval and edits neither, and the camp, preseason-game and cutdown pages are built in step 8 but not issued for a 2015 preseason. The changes held on it are listed in [section I](#i-what-the-build-changes-outside-this-design).
2. **Q-P: how 2015 practice observations are produced (awaiting the user's decision).** The briefing's "Work already on record" column and the report's practice links cite camp observations from `training_report.md`, and no resolver for new practice observations is approved ([camp and preseason reports](camp_and_preseason_reports.md)). *Proposal, not adopted:* the 2014 authored, protagonist-blind method with its evidence rules; no resolver is approved yet. Until the user decides, no 2015 practice observation is produced, and a page cites only observations a training report already holds. The games themselves are resolved by the production runner and are not affected by this question.

## I. What the build changes outside this design

This design edits none of these files. Each is changed in the step named. The second table lists the changes held on Q-R (section H).

| File | Change | Step |
|---|---|---|
| `AGENTS.md:148`, `:166` | Flagged: these need 2015 wording from the user; until then the 2013 durable methods they name apply | 8 |
| `foundation/templates/README.md` (the preseason games row) | Drop the pack's own event result and four-game checklist links | 8 |
| `foundation/templates/preseason_game/preseason_game_result_template.md`, `four_game_checklist.md` | Remove once nothing links them; until then each says where its content went | 8 |
| `docs/rebuild_plan.md:178`, `:185`, and the preseason games row of "The decisions in a year" | List Document 7 §5.1 and Document 1:229 among the rulebook lines for the user's approval (Q-R); a change-log entry for this correction in the user's words; the change-log entry at `:185` no longer mentions the four-game checklist; the preseason row's folder is `Training_Camp_and_Preseason/Preseason_Games`, a folder per game | 8 |
| `docs/event_inserts.md` (section A, item 3) and the event router | Two briefs may carry inserts at once when phases overlap, each event once, on the brief of the phase it bears on (section A, item 3 assumes a single active brief) | 8 |
| `docs/game_output_workflow.md:5`; `docs/head_coach_media_method.md:3` | Add the Preseason Game Report as a page each owns (prose; media) | 8 |
| `docs/season_cycle_milestones.md:32`, `:105` | Name the three per-game pages and the per-game steps; date the release record (all seven gates) and the player-state table and binding before preseason game 1 (August 14, 2015), the Week 1-only items (awards method, Week 1 depth library, in-season rails) staying before Week 1 | 8 |
| `docs/run_week.md` | A preseason section with the per-game sequence | 8 |
| `runtime/decisions.py:49-57`, `:144-154`, `:174-221`; `runtime/seasons.py:179-219` | Per-game routing to `Preseason_Games/Game_0N`, with a test; the preseason page set and `preseason_report(n)`; the camp and final-cut routes unchanged by it | 8 |
| `runtime/seasons.py:121-122`, `:343-349` | Drop the Week 1 depth library from the preseason release inputs | 8 |
| `scripts/close_preseason_game.py:156-168`; `scripts/validate_repository.py:735-749` | The box score goes into `Preseason_Game_Report.md` from 2015; validation checks each season's result page | 8 |
| `runtime/game_report.py` | Preseason-aware layout, header, Final, media and statistics checks | 8 |
| `runtime/game_plan.py`, `scripts/check_game_plan.py`, `scripts/apply_game_plan.py`, `scripts/freeze_pregame.py` | The Preseason Game Plan compiler, check and apply, with a 2014 round-trip proof and the taught-calls rule kept to evaluation; the preseason `pregame.json` | 8 |
| `scripts/render_game_week.py` or a new builder | The Preseason Game Briefing builder from stored facts | 8 |
| `runtime/decision_queue.py:24-27`, `:65` | `preseason_inputs` and `preseason_close` keyed by `(season, game)`; game 4 waits on the 75 | 8 |
| `scripts/rebuild_pages.py` | A built 2015 preseason index (`Preseason_Games/README.md`) from the fixtures and the closed reports | 8 |
| `career/2015/Calendar.md:43`; `library/2015_historical_calendar.md:13` | The April 9, 2015 opponents-and-weeks announcement as an information-gate row | 6 |
| `data/2015/Training_Camp_and_Preseason/Preseason_Games/fixtures.json` | The four fixtures, written at the April 20, 2015 clock; the opponents' rosters researched at the August 2015 clock | 7 |
| A two-pass 2015 playing-rules library record; `runtime/rules.py:83-90` | The try rule adopted May 19, 2015 for that season, and its seam implemented for 2015; tests 10 and 41 | 2015 season release, before August 14, 2015 (outside the rebuild steps) |
| `library/` source register | Fold this design's remaining rule and date sources into the library (the Article 23 transcription, the 2015 cutdown rules) and the research register's Chiefs August 24, 2014 entry, marked unverified until retrieved | 8 |

**Held on Q-R.** These changes are made only after the user approves Q-R and are listed as held until then: the AGENTS.md lines 117, 119 and 121 and the AGENTS.md routing of 2015 camp, preseason-game and cutdown work to the new pages; `docs/update_workflow.md` line 125; and the rescoping of the eight-section references to 2013 and 2014 in the templates and process documents below. Until the user decides they stay as written, and the pages and their code are still built in step 8 but not issued for a 2015 preseason. The [position battles](position_battles.md#7-build-integration-points-and-the-files-to-change) and [final roster cuts](final_roster_cuts.md#3-repository-inspection-and-the-build) designs hold the same lines in the same words.

| File | Change once Q-R is approved | Step |
|---|---|---|
| `AGENTS.md:117`, `:119`, `:121` | Scope the eight-section template, its storage rule and the bulk turn to 2013 and 2014, the way `:121` scopes the regular-season template; route games from 2015 to the three pages. Held on Q-R | 8, after the user's approval |
| `foundation/templates/preseason_output_template.md:5`, `:9`, `:11`, `:13`, `:15` | Scope to 2013 and 2014 | 8, after the user's approval |
| `foundation/templates/training_camp_and_preseason/README.md:8-9`, `:32`; `preseason_review.md:3`, `:7`; `player_assessment.md:41` | Scope the eight-section references to 2013 and 2014; from 2015 the review is the dated section of the latest Preseason Game Report | 8, after the user's approval |
| `foundation/templates/offseason_output_template.md:7`; `foundation/templates/regular_season_output_template.md:4` | Name the Preseason Game Report from 2015 | 8, after the user's approval |
| `foundation/templates/README.md:24-25`, `:44`, `:45` | Scope the eight-section catalog rows to 2013 and 2014 | 8, after the user's approval |
| `docs/preseason_game_reports.md:5`, `:53`, `:77`; `docs/camp_and_preseason_reports.md:93-94`; `docs/update_workflow.md:125`; `career/README.md:17`; `runtime/README.md:47` | Scope the eight-section and bulk references to 2013 and 2014; the box score goes into the Preseason Game Report from 2015 | 8, after the user's approval |
