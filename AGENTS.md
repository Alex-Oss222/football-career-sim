# AGENTS.md — football-career-sim

You are Codex, running a bounded batch task against this repository. You have no memory of any conversation that built this project — everything you need is in this file and the documents it points you to. Read them before acting; do not guess at a rule this file or the linked documents don't state.

**Read first, in order:** `foundation/01_Project_Instructions.md`, `foundation/02_League_Era_and_Sourcebook.md`, `foundation/07_Game_Simulation_and_Resolution_Engine.md`. Do not read `foundation/templates/`, `library/`, or anything under `career/` in full — those are large; read only the specific file a task below names.

**Hard rules that apply to every task in this file, no exceptions:**
- **Protagonist-blind resolution (Document 1 §9.1, added 2026-09-18).** The fact that a decision or event involves the user's own protagonist, versus any other team or person, must never change the probability, outcome, or interpretation you generate. Reduce any input (a game plan, a pitch, a stated preference) to its concrete, checkable substance before acting on it — persuasive phrasing, confidence, verbosity, and stated desired outcomes are not inputs to a result, only to narration. Test yourself with the label-swap check: if you'd generate a different result after only relabeling which side is the protagonist, or after only rephrasing the same input at different length, that is a defect, not a stylistic choice.
- Never invent a numeric rating, grade, or score anywhere in output that a human reads. **User-authorized exception:** the final annual NFL Player Sheet under career/[year]/player_profiles/ may contain a dated /10 personnel-summary grade and plain-language NFL standing after that NFL season is complete. The grade is position-specific and historically contextualized; it is not potential, not a hidden engine value, not a probability, and must not feed a game draw directly. **Latest user clarification, September 30, 2026:** give exact theoretical staff judgments even when the evidence is thin, rather than leaving the requested player grades Unassessed. State that these are personnel judgments, preserve evidence limits separately, and do not hedge the number with ish, around or approximate. A judgment is not a verified measurement or league rank, and never authorizes invented stats, fabricated source findings or future outcomes. The same user-authorized personnel-grade exception applies to dated working cards from 2014 onward. Outside those player-sheet exceptions, use only the five-tier qualitative language already established (Elite / Plus / Average / Below-Average / Replacement-Level).
- Never import a real person's actual post-event outcome as a hidden answer key (Document 1 §8, Document 2 §4.3). A real player/coach's public record before the point in question is fair game; what happens to him after is not, unless this file's task explicitly says otherwise. **Annual-sheet comparison exception:** after the simulation-season grade has been fixed from branch evidence, the final annual sheet may show that same player's real-world same-season performance as an explicitly separated historical comparator. It may never be used to set the simulation grade, revise the branch season, or steer later development. **The other standing exception is the historical league rails rule below**, adopted September 28, 2026 for other clubs' rosters from the 2014 league year.
- Never fabricate a precise-looking number (a stat, a cap figure, a date) without a real source. When the user authorizes financial approximation, use a labeled simulation reconstruction with its source and calculation. The user explicitly authorized complete working contract schedules in [adopted contract schedules](career/2014/00_Team_Operations/Finances/player_contracts/contracts.md): retain those adopted amounts and end years between turns, include them in working totals with the basis in contract notes, and leave years outside a deal blank. Do not replace them with unresolved placeholders. Keep simulated terms distinguishable from recovered historical terms and from certified club cap room. Otherwise, if you can't verify something, say so explicitly rather than presenting an estimate as fact — this project's stated top priority is never repeating a past experience where numbers were "fudged."
- Write the task's named file as the primary record, but do **not** stop there when the task changes canon or advances simulation time. Never edit `foundation/` unless the task explicitly targets the rulebook. Research-only, planning-only, and ex-ante recommendation tasks must not mutate current state.
- Commit with a clear message describing what changed. Do not push directly to `main` without going through whatever PR flow this repo's owner has configured in Codex's environment settings.

### Season file layout (2014 onward)

The user-approved calendar layout is documented in [season folders and continuity](docs/season_structure.md). Historical logical names below such as `career/[year]/roster.md`, `stats/`, `player_profiles/` and `offseason/` resolve through `runtime.seasons.SeasonPaths.record()` from 2014 onward. Use the actual current owners in `docs/repository_map.json`; do not recreate the old flat 2014 folders. 2013 retains its existing layout. Spring phase files are `staff_plan.md` and `training_report.md`; dated individual findings stay in the report and link to the annual player card. Phase One and Phase Two are separate owners. Preserve all existing evidence, authority and release checks.

### Annual player assessments and position battles

The user clarified October 1, 2026: exactly two full personnel assessments per player per season. The opening assessment accompanies the player into the new year, spring work and the start of the playing season. Preserve that baseline and append dated, source-linked observations during training and the season. Statistics continue updating after each closed game. The separate final assessment is written after that season ends, compares the opening view with actual work, and remains frozen history. Do not create full player assessment cards at every phase or rewrite the opening grade as if it had always been the latest view. A later signing receives a dated entry assessment using information available when he joins.

Position battles exist only during offseason training, camp and preseason, and only for identifiable contested spots with actual candidates. Use `foundation/templates/position_battle_card_template.md`. Organize cards by unit, position and specific spot, with candidate names across the top and side-by-side scheme fit, observed work, remaining questions, head-coach, coordinator and position-coach assessments. Keep the three perspectives distinct; preserve Stone's actual decisions and label any staff-analysis reconstruction. Never invent a meeting, quote, preference, equal rep allocation or winner. No cards or empty position directories where there is no battle. A vacant spot alone is not a named competition. A resolved card is preserved as dated history and removed from the open list; the roster-decision owner controls the actual appointment.

Yearly `Record.md` is a generated dated one-line index of real events. `Calendar.md` is a schedule. Event facts and closure metadata belong at the relevant source. Legacy entry numbers survive only as compatibility aliases for frozen records, not as the user's navigation. The numbered, capitalized layout is defined in `docs/season_structure.md`; do not recreate duplicate forwarding directories or empty future outputs.

### Reader-facing writing

Annual sheet formats: 2013 uses `foundation/templates/player_sheet_template.md` (the completed-season position baseline). From 2014 onward use the restored `foundation/templates/player_sheet_2014_onward_template.md` with Overall and vs. Average / vs. Best / vs. Worst, inherited state and yearly changes. At the bottom retain separate full position-specific regular-season and playoff stat tables, beginning in 2014 and appending each later year. Preserve old rows and do not populate unplayed seasons or replace missing fields with zero. The source requirements above still apply. Latest user clarification (September 30, 2026): create working player cards from 2014 onward immediately for the current controlled roster. Retain the starting personnel assessment during the season; review it at season close. Update separate regular-season and playoff statistics after each closed game, preserve previous years and append each new year. Use exact theoretical staff judgments for grades, identifying judgment and evidence limits separately. Display year-based labels such as 2013 regular season and 2013 playoffs; omit the redundant simulation-context label from player-facing prose. Preserve proper names and technical identifiers.

Use the player, coach, decision or source name in prose. Add a descriptive link where the reader needs supporting evidence, and collect broader sourcing in a named source section. Do not attach citation-code clusters to every paragraph, invent IDs for ordinary recommendations, or repeat a label already supplied by the heading. Preserve identifiers that actually connect source events, machine-readable records, receipts or existing cross-references; explain them once and keep them out of the football narrative when the name suffices. Keep a single legacy-label mapping only where older references need it. This is a presentation rule, not permission to delete evidence or change a decision's status.

### Atomic progression and dependency rule

Any task that **completes an event, advances the career clock, changes roster/control, changes staff, changes draft capital, changes financial obligations, changes medical/availability state, changes a depth-chart or role decision, or otherwise changes canon** is an atomic progression task. For those tasks:

1. **Update the event/history owner first.** Write the completed result to the appropriate dated career file such as the individual trade, signing history, draftees file, medical history, practice/game report or roster-decision file. Add event metadata there and regenerate the annual one-line Record.md; never write another account in a season ledger.
2. **Update every dependent current-state view in the same commit.** At minimum inspect and update, when affected:
   - `career/[year]/Record.md`;
   - the applicable transaction/result file under `career/[year]/`;
   - `career/[year]/roster.md`;
   - `career/[year]/standings.md` whenever a final score changes any club's record, regenerated from receipts with `python scripts/render_standings.py YEAR`;
   - `career/[year]/stats/` whenever a regular-season or postseason game closes: preserve the public stat receipt and refresh the current team/league stat views from receipts rather than hand-adding prior Markdown;
   - the applicable cap/contract/draft-capital accounting file;
   - `career/[year]/depth_chart.md` and its working JSON (`career/[year]/offseason/depth_chart_working.json` until the season input `career/[year]/depth_chart.json` is released), with a row in its update log;
   - `career/[year]/offseason/contract_table.md`, with a row in its update log;
   - the long-term financial inputs and generated views under `career/finances/`, including all affected future-year obligations; run `python scripts/render_jaguars_cap_tracker.py` and its `--check` mode when these change;
   - `state/04_Roster_and_Staff_Register.md`;
   - `state/05_Current_Season_State.md`.
   Update another file only when that file actually owns a changed current fact. Do **not** append transaction history, roster snapshots, draft recaps, or checkpoint bookkeeping to durable strategy, development, playbook, or planning documents.
3. **The user does not need to name every dependent file.** A request like "make this trade," "sign this player," "run the draft," "advance to rookie minicamp," or "play the week" implicitly authorizes the dependent state updates required to keep canon internally consistent.
4. **Preserve ex-ante and durable planning records.** Do not rewrite a planning, recommendation, development, or playbook file merely because the roster or transaction state changed. A durable football plan changes only when the user changes the plan, teaching method, scheme, evaluation standard, or operational responsibility. Record acquisitions, departures, draft results, and current-room status in the proper result/history/current-state files instead.
5. **Unknown accounting is not a reason to leave state stale.** Update ownership, roster count, draft capital, and known contract/control effects immediately. If an exact cap, cash, guarantee, medical, or Top-51 figure is not verified, mark that field unresolved and identify the missing reconciliation instead of inventing a number.
6. **Advance checkpoints together.** When Document 4 or Document 5 changes, update their version/checkpoint/source pointers so both represent the same latest closed event.
7. **Run a contradiction pass before committing.** Search the affected year and state files for stale versions of the changed fact, including old player-team ownership, "no trade" or "not acquired" language, obsolete roster counts, stale draft-pick ownership, old season-phase text, and prior checkpoint/version labels. Resolve contradictions that are downstream of the event in the same commit.
8. **Do not create unrelated changes.** Dependency closure is required, but it is bounded to facts changed by the event. Library research, stable foundation rules, unrelated seasons, and unrelated player records stay untouched.

A progression commit is incomplete if its event file says one thing while a dependent current-state file still says another.

**Season-stat closure rule.** A closed regular-season or postseason game is not statistically complete until its public game receipt is preserved under career/[year]/stats/game_receipts/. Use runtime.statbook.make_receipt with detail="full" for Jacksonville/protagonist games so the receipt retains the complete public player dictionaries, snap play_ledger, and named-call stats. Use detail="compact_stats" for ordinary background games: it keeps every nonzero generated team/player statistic and a row for every game-day active player, and omits the background snap ledger, named-call data and zero-valued player fields. This is storage compression only; it never changes the game result or generated statistics. Every statistical view is generated from the receipt set, never typed: `python scripts/render_season_stats.py YEAR --team TEAM_ID` for the stats directory, `python scripts/render_standings.py YEAR` for standings, and `python scripts/render_box_score.py --season YEAR --write OUTPUT_MD` for the box score in the week's output.md. If statistical receipt coverage is incomplete, label the gap and withhold formal league rankings rather than filling it from real historical results or narrative inference.

Use [the dependency workflow](docs/update_workflow.md) and `docs/repository_map.json`. Run `python scripts/validate_repository.py` before closing a change; refresh a phase summary receipt only after reviewing the summary against its updated output. Both game paths must also pass `python scripts/check_game_readiness.py`. A green repository check is not game authorization.

### Playbook (offense and defense): active-iteration lock

`career/playbook/` holds Stone's authored, team-neutral offensive and defensive systems across the whole career, in two parallel series of dated iterations — see `career/playbook/README.md` for the full index and effective-season tables. The lock below applies to the offensive and defensive series independently.

- **Read only the offensive and defensive iterations whose effective-season ranges (their own frontmatter) cover the current in-sim year**, per `state/05_Current_Season_State.md`'s master clock. Never open, quote, or draw a concept, personnel grouping, protection name, front, coverage, pressure label, or term from an iteration whose range starts after the current in-sim year — that book is offense or defense Stone has not developed yet inside the story. This is the no-hindsight rule (Document 2 §12) applied to the user's own pre-written future material, not just real-world fact.
- **Stone is the head coach.** He may call, delegate or take back plays on offense, defense or special teams at any time. Follow his latest instruction and otherwise continue the existing staff arrangement. Do not repeatedly ask who calls plays, make a backup-caller appointment a prerequisite to practice, or add a play-calling decision to a routine phase review. Ask only if an actual unresolved instruction prevents the next football action. The defensive book identifies its author, not an exclusive caller. See `career/playbook/README.md`.
- A past, superseded iteration may be read for lineage (an iteration's `inheritance_rule`/`baseline` field legitimately points back to an earlier one), but only the currently active iteration is live for teaching, install work, scouting, or play-calling.
- **Human-player access rule.** Every player may receive, possess, and study the complete active iteration. The active book is a football playbook, not a software unlock tree. Players may read ahead and ask questions about any page. "Installed" means formally taught, walked through, practiced, and prepared for team use. Installation is still gated by the real CBA offseason-program calendar in `career/[year]/offseason/the_prowl_player_readiness_standard.md`, but that calendar limits club teaching/practice activity, not player access to the active book. Evaluate players on assigned/taught material, never on whether they mastered an uninstalled page.


### Historical league rails (2014 onward; user rule, September 28, 2026)

From the 2014 league year, the rosters of the 31 clubs other than Jacksonville follow real history, so the branch keeps the same league of players the real NFL had. Full method: `career/2014/league/personnel/method.md`. Document 2 §4.5 records the rule in the rulebook.

1. **What rides the rails:** other clubs' real player movements. That means free-agent signings, re-signings, trades, releases, retirements, draft selections, undrafted signings and each season's real Week 1 depth charts.
2. **What never does:** game results, statistics, injuries, suspensions, awards, standings, the draft order, coaching and front-office changes, and anything about Jacksonville. These stay branch-generated. The coaching carousel ([January coaching decisions](career/2014/01_Early_Offseason/staff_changes/timeline.md)) is canon, and players ride the rails regardless of which coaches the branch gave their clubs.
3. **Information gate:** a rail becomes usable only on its real public date. Rails data for a phase is built when the career clock reaches that phase. Before then, no rail may inform Stone's, Caldwell's or any club's evaluation.
4. **Jacksonville control overrides the rails.** Jacksonville's roster, contracts, cap and transactions come only from branch decisions (Caldwell's authority, Document 3). A real move involving a Jacksonville-controlled player does not apply, except retirement (rule 5). A real Jaguars move the branch never made does not happen; a player the real Jaguars signed stays a free agent Jacksonville may still sign.
5. **Retirements apply league-wide on their real dates, Jacksonville included.** A retirement is the player's own choice. Its actual contract and cap effects belong in the retirement/contract owners, with a one-line link in the annual record.
6. **Free agents Jacksonville pursues:** decided by one private market draw per player. The draw weighs Caldwell's offer against the contract the player really signed (method §4).
   - If Jacksonville wins, the player leaves his real club, and the next man up takes his depth slot.
   - If Jacksonville loses, he goes to his real club on his real terms and date.
   - A player who leaves Jacksonville follows his real next move only when that move was the same kind of move in the same window; otherwise he is an unplaced free agent.
7. **Draft:** Jacksonville's order is still computed from branch standings (Document 2 §12), and other clubs' selections are their real selections.
   - **Availability:** a prospect is available at Jacksonville's branch overall pick N only if his real selection was pick N or later, or he went undrafted.
   - **Swaps:** Jacksonville's k-th selection pairs with the real Jaguars' k-th selection. The real Jaguars' player goes to the club that really drafted Jacksonville's player, or to the club Jacksonville's player really joined as an undrafted free agent. With no partner, he is unplaced.
8. **Unchanged:** the protagonist-blind rule, the label-swap test and all other hard rules apply. The rails decide other clubs' personnel only; every football event is still resolved by the engine.

### Career calendar control rule

For any task that advances a season clock, opens/closes a camp or practice phase, executes a roster deadline, runs a transaction window, or plays/simulates a game, first read `career/[year]/calendar.md` when that file exists.

- The career calendar is the branch-facing schedule authority for team dates, opponents, reporting dates, camp windows, roster deadlines, trade deadlines, bye weeks and conditional postseason gates.
- Its historical sourcing belongs in the corresponding `library/[year]_*calendar*.md` file. For Jacksonville 2013, the full source is `library/2013_jacksonville_master_calendar.md`.
- Do not substitute an older phase-local date if the master calendar contains a later verified correction.
- Historical dates/opponents are rails only. Never import the real score, injury, transaction, attendance, depth chart or season result.
- If a previously missed phase is already behind the latest closed checkpoint, preserve the chronology gap unless the user expressly authorizes a retroactive simulation. Do not fabricate attendance or performance to make the calendar look complete.
- Before closing a date-sensitive event, check the next deadline/event in the career calendar and carry it into Document 5.

**Historical calendar, all seasons (including 2015):** the user explicitly requested the actual historical dates. Read `career/2015/calendar.md` and `library/2015_historical_calendar.md`; use the sourced Jacksonville practice, reporting, preseason, regular-season, bye and deadline dates, including dated amendments. Do not replace them with generic proposed week windows. The calendar can be researched ahead without advancing time or importing results. Use the actual historical opponents, dates, home/away, byes and dated amendments in every year. The user's September 29, 2026 clarification supersedes branch-standings-based schedule changes. Branch standings still control playoff qualification and draft order. An announced practice is not proof it was held. Information-release dates, actual eligibility, medical instructions and legal work restrictions still apply.

### Offseason onboarding and phase-plan execution rule

**Training report format, user instruction September 30, 2026.** For Phase One, Phase Two, rookie minicamp, OTAs and mandatory minicamp, read [the training-report index](foundation/templates/offseason_training/README.md) and its matching template before writing the report in chat or the phase output. Lead with actual football teaching and performance: formations, assignments, running the offense/defense, coaching corrections and what held later. These phase-specific versions of the offseason format replace the generic finance/draft/job-status layout for training reports. The four completed 2014 spring reports now have a readable football account followed by an expandable original session record; use that detail for evidence and follow-up questions, not as the default chat response. A request to review or rewrite a closed report does not authorize new practices, results, roles or time advance. Research and rationale: [offseason training reports](docs/offseason_training_reports.md).

**Training camp and preseason, same user instruction.** Read [the camp/preseason report index](foundation/templates/training_camp_and_preseason/README.md), the matching camp/game/consolidated-review template and its shared player-assessment method. Preserve the section order across seasons while using that season's actual staff, roster, active books, taught work and evidence. Explain scheme fit through assignments, technique, support and the actual opposition. Stone's [camp approach](career/coaching_profiles/alex_stone_coaching_profile.md#how-he-wants-training-camp-run) and the season plan govern intended work: everyone reports on the applicable date, players and coaches meet appropriate physical standards, participation is expected within individual medical/workload instructions, permitted contact is purposeful, and starters and reserves receive meaningful opportunities in varied combinations and situations. This direction does not fabricate a completed coach fitness test or retrofit contact into past non-contact sessions. The July 29 camp report retains its original detail beneath the readable account. Preseason follows the existing bulk workflow and game gates; the templates never create an unplayed result. [Research, examples and implementation](docs/camp_and_preseason_reports.md).

**Preseason game review, user follow-up October 1, 2026.** Render both a game story and a coaching review using the [expanded game template](foundation/templates/preseason_output_template.md). Explain team offense, defense, special teams and communication, then the consequential named-player strengths, failures, scheme execution and next coaching work. Assess actual starters, reserves and mixed groups with their support, opposition and opportunities. Keep recognition, technique, physical execution and decision errors distinct. Do not infer a missed assignment or clean communication from statistics alone, or invent film observations. The [consolidated review](foundation/templates/training_camp_and_preseason/preseason_review.md) must retain this substance in bulk chat output. [Research and a worked example](docs/preseason_game_reports.md).

**Full game-output layout, subsequent user correction.** Use [regular_season_output_template.md](foundation/templates/regular_season_output_template.md) for regular-season/postseason turns and [preseason_output_template.md](foundation/templates/preseason_output_template.md) for preseason. Preserve each complete layout: regular-season has unnumbered Coach info followed by seven sections, with Game in section 3; preseason has eight sections, with Game in section 4. Put the full **Report to render** directly beneath the game narrative in each version, retaining its unit, communication, player and coaching account and the generated full statistics. Retain surrounding preparation, media, personnel and closure sections. The consolidated preseason guide belongs within section 6 of the preseason template; it cannot replace the full output. The former generic season filename and separate short preseason-game template have been replaced by these two complete versions.

**Report ownership and carryover, October 1, 2026 implementation.** The [template catalog](foundation/templates/README.md) maps each recurring report and teaching aid to its single filled owner. Use the phase-specific work, actual opportunities and coaching response to explain performance. End substantive reports with continuing work, latest evidence, responsible coach and next opportunity. Keep session plans, individual teaching plans and film packets in their own owners using the shared coaching-method templates; they are not extra personnel assessments. At season close use the [exit-interview and team-review formats](foundation/templates/season_review/README.md). Preserve exactly two full annual assessments, earlier evidence and actual interview statements. The existing season handoff inventories unfinished work and reviewed sources; do not create another ledger or transition packet. Follow the [season continuity checks](docs/season_structure.md) before making a successor year active. Template work never advances the career or completes a promised task.

For any task that **starts, advances, runs, simulates, or closes** Jacksonville's rookie minicamp, offseason program/OTAs, a separately scheduled new-head-coach voluntary veteran minicamp, mandatory veteran minicamp, training camp, or the preseason work embedded in training camp, the durable development plans are mandatory inputs. Do not improvise a generic camp because the user said "advance to camp."

**Read these common files before resolving the phase:**

1. `state/05_Current_Season_State.md` — current clock, phase, roster-control caveats, and current checkpoint.
2. `career/[year]/offseason/player_onboarding_and_development_framework.md` — welcome-package process, Day-2 Stone/position-coach calls, learning cycle, Good/Better/Best standard, physical progression, and family-dinner policy.
3. `career/[year]/offseason/the_prowl_player_readiness_standard.md` — medical, physical, support, privacy, offseason-voluntariness, and CBA boundaries.
4. `career/[year]/offseason/the_prowl_program_identity.md` — program expectations and team-level football principles.
5. `career/playbook/README.md`, then **only** the active offensive iteration and the active defensive iteration permitted by the active-iteration lock above.
6. The phase plan listed below.
7. The current roster/staff files and only the additional player/medical/transaction records needed for that event.

**Phase-plan map:**

- Rookie minicamp -> `career/[year]/offseason/rookie_minicamp/plan.md`
- Offseason program / Phase One / Phase Two -> `career/[year]/offseason/offseason_program/plan.md` when that separate plan exists (2014 onward in the current layout); otherwise the combined `career/[year]/offseason/otas/plan.md` (2013).
- OTAs / Phase Three -> `career/[year]/offseason/otas/plan.md`
- Any separately scheduled new-head-coach voluntary veteran minicamp -> use `otas/plan.md` plus the exact voluntary-minicamp CBA/calendar rules; do not convert it into the mandatory event.
- Mandatory veteran minicamp -> `career/[year]/offseason/mandatory_minicamp/plan.md`
- Training camp and its integrated preseason-development process -> `career/[year]/offseason/training_camp/plan.md`

**Plan versus history is a hard boundary.** A `plan.md` says what Jacksonville intends to teach, train, evaluate, and provide. The corresponding `output.md`, annual event record, roster/register, and current-state files say what actually happened. Never write results, standouts, attendance lists, depth-chart outcomes, injuries, or performance history back into a durable plan merely because the event occurred.

**2014 carry-forward:** the framework, readiness standard and program identity remain at their `career/2013/offseason/` paths, explicitly incorporated by the 2014 phase plans. Read those durable methods when the corresponding year-local file does not exist; apply the 2014 plan/calendar's returning-head-coach restriction. Prepared recommendations marked pending are not adopted decisions. Resolve or explicitly defer any material pending choice needed for a phase before running it.

**2014 individual training and film:** read `career/2014/offseason_training/README.md`, `training/weekly_workflow.md`, `training/unit_plans.md`, `film/player_queue.md` and the relevant `player_development/` record before preparing or running a 2014 development phase (the shortened paths are relative to `career/2014/early_offseason`). Read `player_development/roster_profiles.md` for every player. For Cousins, use `player_development/kirk_cousins.md` and `film/kirk_cousins_2013_review.md`: synthesize his full starting season, preserve demonstrated strengths, invite his actual perspective when permitted, and let future evidence reveal who he is becoming. Apply this open-ended method to all players; no fixed archetype, whole-player unlock ladder or automatic phase upgrade. Distinguish observation, staff inference and proposed work; outcome totals are not mastery or talent evidence. Individual feedback, shared QB-center identification teaching and continuing individual development are adopted; other marked choices remain pending. Plans own intent, phase outputs own observed work, and `film/delivery_log.md` owns actual distribution receipts. A prepared index is not video, delivery or a completed review. Check actual control, medical instructions and the existing pre-program film/contact gate before participation or delivery.

**Calendar gate.** If the exact 2013 Jacksonville date/window needed to execute a phase is still unresolved in the repository, research and verify it under the project's two-pass sourcing discipline before advancing the career clock. Do not invent a convenient date, practice count, reporting day, or roster deadline.

**Living coaching assessments:** before preparing or resolving a development phase, weekly coaching review or staff evaluation, read `career/coaching_profiles/README.md`, `alex_stone_coaching_profile.md` and the relevant section of `staff_profiles.md`. Start from the coach after his actual branch experience, just as for a player; Stone now has a complete season building his staff and developing a starting QB. Preserve the frozen prehire dossier. Plans own intended teaching/decisions; primary outputs own actual contributions. At a material evidence handoff, append the dated change or retained assessment to `career/coaching_profiles/alex_stone_coaching_assessment_log.md` and refresh `alex_stone_coaching_profile.md` where the current interpretation changes, keeping strengths, counterevidence, actual perspectives and uncertainty. Keep dated history in the log; use `alex_stone_career_reference.md` for biography, appointments, records and authority. No fixed coach archetype, invented motive, calendar upgrade or ability inference from the equal-strength 2013 results. Coaching affects supported assignments and choices with costs under E1, not a reputation or protagonist multiplier. Profiles do not implement the engine, appoint staff or change authority.

**Onboarding gate.**

- Before a player's first Jacksonville football-development phase, verify club control and execute the welcome-package / playbook-distribution / follow-up-call process to the extent the calendar legally and practically allows.
- Contact only players whose Jacksonville control or invitation status is actually established. An unresolved inherited name is not a license to invent a call or letter.
- A late acquisition gets the same onboarding process on a compressed honest timeline; record the compression rather than backdating calls.
- Issue the complete active playbook. Players may study any part of it. The phase-appropriate practiced menu defines what the staff may fairly evaluate as installed team football; it is not a restriction on what players may read.
- During voluntary periods, an optional Stone/position-coach call, workout, meeting, or social event cannot become a hidden roster/role/commitment grade.

**Teaching and evaluation rule.** Execute the phase plan's Explain -> Show -> Walk -> Rep -> Correct -> Rep again -> Retain -> Add complexity cycle. Keep assignment, communication, technique, physical loss, processing delay, medical limit, and coaching/teaching failure analytically separate. Do not manufacture a flaw when a rep was correct. Do not add complexity simply because the calendar advanced. The phase plan's Good/Better/Best descriptions are teaching states, not numeric ratings and not permanent player labels.

**Second-year progression.** Apply the same development and install standard to offense and defense: review what the unit already demonstrated, onboard newcomers, protect unfinished individual work and teach the next material from the active books as ordinary program work. Each unit progresses from its own evidence; neither waits for the other or for every individual correction to close. Stone has approved Boot Flood's return to the 2014 teaching and practice program; do not ask for that approval again. Use the existing phase decision package for the progression and the existing E1 decision record for each unit's Communication and Plan execution badges, with individual playmaking assessed separately on both sides. Those assessments require evidence; planning does not award a badge or release the unfinished engine.

**No percentage-driven roster or playbook resolution.** Do not use a playbook personnel percentage, planning center, preset snap share, rep quota, touch quota, depth-chart probability, or target distribution as the mechanism that decides who plays, who wins a job, which package is used, or which concept succeeds. Those are football decisions that must emerge from the players' demonstrated work, health, matchup, opponent response, game situation, actual practice/preseason/game performance, and the coach's authorized judgment. If a playbook contains a numerical usage note, treat it as non-controlling background only. The football evidence overrides it.

The simulation engine may still use its hidden stochastic resolution machinery to resolve uncertain football events where Document 7 requires it. That hidden mechanism must not be exposed to the player-facing playbook and must not be substituted for the football evidence used to make roster, role, rep, touch, install, or game-plan decisions.

**Family-dinner rule.** The phase-specific family dinners are part of the established program. When the verified schedule permits, execute the dinner described by the phase plan. Invite the current team, appropriate staff, and invited family/meaningful guests under the framework's rules. Family/guest attendance is voluntary, the dinner is not a football meeting, and attendance, guest choice, family structure, finances, health, counseling use, or private conversation never becomes personnel evidence. Log an actual dinner in the phase output, not the durable plan.

**Resolution discipline.** The plans define opportunities and evaluation questions, not outcomes. Resolve actual player performance from the information legally available at that date, the work actually performed, the game/practice resolution rules, and the protagonist-blind standard. Never use future real-life player success/failure as proof that a rookie, veteran, signing, or draft pick must stand out or struggle.

**Closing the phase.** Once actual football work occurs, this becomes an atomic progression task. Write the phase report and its dated individual findings first, regenerate the annual event index, then update every genuinely affected roster, role, medical/availability, financial/control, Document 4, and Document 5 view in the same progression commit. If no current fact changed, do not manufacture a state edit merely to touch every file.

**Do not rewrite the plans after every practice.** Change a durable plan only when the user changes the teaching method, install philosophy, physical standard, evaluation standard, family-program policy, or operational responsibility.


---

## Task: "Run Week [N]" / "Run Week N"

This is the **top-level one-command regular-season workflow**. A user instruction such as `Run Week 1`, `Run Week 2`, or `Run Week 3. Plan: ...` authorizes the complete bounded week task. The user is not responsible for running helper scripts, filling migration JSON, building background-team packets, advancing private snapshots, or repairing internal readiness prerequisites.

### What the one command authorizes

For the named week, Codex must autonomously:

1. Read the current state, calendar, that week's existing `output.md`, the active playbook iterations, the season-output template, current roster/medical state, and any weekly plan supplied by the user.
2. Run ordinary repository/game readiness checks.
3. Resolve **internal repository prerequisites** that are already user-authorized, including an explicit migration/reset for that same week.
4. Build/freeze the protagonist and background TeamInput records required by the active kernel with `python scripts/build_week_inputs.py N --season YEAR` (Week 2 onward; it needs that week's frozen `call_sheet.json` from Stone's plan). Before any event closes, run the weekly TeamInput exclusivity gate: current Jacksonville-controlled active-roster and practice-squad players may appear only in Jacksonville's TeamInput, and no player may appear on more than one club in the same weekly slate. Historical roster rails always yield to branch transactions/control.
5. Run the protagonist game and every other league game in that week through the shared production runner, exactly once per canonical event: `python scripts/close_week.py N --season YEAR --close`.
6. Preserve the full public game receipts required by the active kernel/statbook contract.
7. Write the protagonist weekly `output.md` using the current season-output template and write the background roundup to `league_results/week_NN.md`.
8. Generate the box score, standings and season statistics from receipts (`render_box_score.py --write`, `render_standings.py`, `render_season_stats.py`); never hand-add totals from Markdown. Then read `career/[year]/stats/calibration_audit.md`: an OUTSIDE row is investigated as an input or engine defect, never grounds to rerun or select a closed result.
8a. Draw the week's league awards with `python scripts/league_awards.py week N --season YEAR --close`, and each month's awards when its league announcement date is reached (`month NAME --close`; October after Week 9's first game, and so on), then render `career/[year]/awards/`. `validate_repository.py` fails while a closed week or a finished month lacks awards.
9. Reconcile injuries, availability, roles, transactions and other actually changed state.
10. Close the event owners and current state atomically, regenerate Record.md, and validate the branch. Update the calendar only if a scheduled date or appointment changes. Open the normal PR. **Do not advance the private snapshot from an unmerged branch.** If Codex can merge the PR, merge it first, update/check out the merged `main`, then advance the private snapshot to the merged Document 5 digest and rerun readiness. If Codex cannot merge, leave the private snapshot unchanged and report snapshot advancement as pending merge.
11. Stop before Week N+1.

### Weekly TeamInput exclusivity

Before the first game event of any regular-season/postseason weekly slate closes:

- Build the full weekly TeamInput package in the transient workspace.
- Run `python scripts/check_week_input_exclusivity.py <weekly-input-package.json> --expected-games <scheduled-game-count>`. Use the actual week's scheduled game count so a partial package cannot pass.
- Derive Jacksonville control from the current branch `career/[year]/roster.md`, including both active roster and practice squad.
- A Jacksonville-controlled player may not appear in any non-Jacksonville TeamInput, even when a real historical Week-N roster source lists that player for another club.
- No player identifier may appear on two clubs in the same simulated weekly slate.
- Treat a failure as an internal data-preparation defect: fix the inputs and rerun the gate. Do not ask the user to reconcile historical rosters.

### User-plan handling

- If the user supplies a Week N plan in the same prompt, that plan controls within Stone's authority.
- If an already-closed ex-ante Week N plan/call sheet exists because the week is being rerun under an authorized technical migration, **reuse that pre-result plan**. Do not rewrite the plan because the old result is known.
- Do not manufacture a new consequential Stone commitment merely to avoid asking a real football question. A genuinely new user-controlled choice not covered by the supplied/closed plan may still require the user. Internal tooling, data preparation, migration work, background-team construction and repository bookkeeping never do.

### Internal migration / reset rule

A user-authorized migration for the requested week is an **internal prerequisite**, not a user task.

General rules for any such migration:

- Use only the current generation identifiers in the migration manifest. Never publish, show or compare the results of a voided or aborted generation.
- Freeze every replacement TeamInput before any replacement draw.
- Replace the whole affected slate as one batch. Never rerun only Jacksonville while leaving the rest of a voided slate active.
- Preserve a full Jacksonville receipt and compact_stats receipts for the other games, rebuild every dependent stat and standings view, append the supersession entry, and reconcile state before the next week.
- The decision to void and replay must never depend on which side a result favoured (the label-swap test in Document 1 §9.1).

The 2013 Week 1 restart is closed. Generations v1 and v2 were voided and Week 1 was replayed as generation 3 under kernel 2013.4. [Week 1 kernel restart](career/2013/migrations/week_01_kernel_2013_4_restart.md) and [2013 Kansas City game report](career/2013/regular_season/week_01_kansas_city_at_jacksonville/output.md) and `career/2013/migrations/` are its record. Its one-off readiness gate and void recorder were retired after closure (2026-09-27).

### Public/private transaction boundary

Private event closure may occur while a week is being generated, but the **private snapshot is a canonical-publication pointer**, not a branch-work pointer.

- Never call `advance_private_snapshot.py` or `/admin/snapshot/advance` for an unmerged branch.
- A week becomes publishable canon only after its complete public dependency set is committed and merged to `main`.
- If a Codex task, Git operation, diff extraction, validation, or PR creation fails before merge, the public week transaction is mechanically **aborted** regardless of its simulated outcome. Do not show/select among aborted results.
- A later retry must use a new migration/event generation identifier when the prior closed packets cannot be reproduced exactly. The reason is the recorded technical abort, never whether the prior result was desirable.
- Any stranded private snapshot created by an older workflow bug must be restored only through the audited checked-in-snapshot recovery mechanism; never edit the SQLite file or silently overwrite transition history.
- After merge, update to the merged `main`, then and only then advance the private snapshot and run final readiness.

### Diff-size / generated-data rule

The one-command week workflow must remain small enough for Codex to return a normal reviewable diff.

- Never commit .sim_cache/ or another transient reconstruction workspace.
- Never place all 32 reconstructed TeamInputs into a committed migration JSON.
- Never store full snap ledgers for ordinary background games; use compact_stats receipts.
- Do not duplicate raw receipt data inside Markdown outputs.
- If a generated human-readable stat view becomes very large, render only the canonical readable tables defined by the statbook tooling; the compact per-game receipts remain the rebuild source.
- A Codex diff-size limit is an internal implementation constraint, not a user blocker. Reduce generated storage according to these rules and continue the same Run Week N task.

### No-user-maintenance rule

For an ordinary `Run Week N` task, do **not** send the user back a checklist telling them to:

- edit or populate a migration manifest;
- run a readiness/reset helper command;
- research background rosters;
- advance the private snapshot;
- alter Railway;
- rebuild the statbook;
- update standings;
- create/merge intermediate setup PRs.

Those are implementation steps owned by Codex inside the one week task. Report a blocker only when it is genuinely external and cannot be resolved through the repository, available research/tools, or the user's already-authorized migration—not merely because an internal preflight currently exits nonzero.

### Completion report

Return only the useful week result and closure summary: protagonist score/result, major football evidence and Stone decisions, injuries/availability, updated record/standings, stat/receipt coverage, validation/readiness, PR/merge information, and confirmation that the next week was not simulated.


---

## Task: "Simulate background league, Week [N], [Year]."

**Availability gate:** this task is disabled until `foundation/07_Game_Simulation_and_Resolution_Engine.md` is marked runtime-ready, its §8 era calibration is complete for the season being played, and the private Engine State store has been instantiated. If any of those conditions is missing, stop without generating scores.

**Superseded in practice by `Run Week N` (2026-09-27).** Background games now close in the same `scripts/close_week.py` batch as Jacksonville's game, through the same production runner and per-possession kernel; there is no separate background path. The output-format, reactive-event, results-file and statistics rules below still govern `league_results/week_NN.md` and the background receipts.

**Scope:** every game that week between two teams, neither of which is the user's own team. Jacksonville's game is written up in its own weekly output, not in this roundup.

**Method — read `foundation/07_Game_Simulation_and_Resolution_Engine.md` §1's scope-discipline rule first, and §3.4's resolution-packet/seed rule.** Corrected 2026-09-18: there is only one outcome kernel in this project. Do not resolve these games by free-form judgment about who plausibly wins — that was an earlier version of this rule and it created two different outcome adjudicators in one league, which is a real integrity defect (background results decide the protagonist's standings, playoff seeding, and draft order, so they need the same physics as his own games, not a cheaper substitute physics). Resolve them through the same production runner and per-possession kernel as the protagonist's game, then narrate only the result. The savings versus the protagonist's game are in narration depth and compact receipt storage, never in the mechanism.

**Output format — highlights only, explicitly, per this project's owner's own instruction:** for each game, write final score, 2-4 sentences of highlight narration (not a drive-by-drive account), and 1-3 standout performers. Do not write play-by-play. Do not write a full box score unless a specific downstream task asks for one. A whole week's slate of ~13-15 games should read like a scores-and-highlights roundup, not 13 separate game stories.

**Reactive events — allowed, but bounded.** A team's players, coaches, or front office may generate a genuine reactive event (a trade demand, a coach on the hot seat, a locker-room story, a media dust-up) if it plausibly follows from something that actually happened in a game or a transaction already on the record. Do not manufacture one to fill a quiet week — per Document 7 §7's Locker Room/Media agent rule, these fire only from logged mechanical events, never invented for drama's own sake. Across a full week's slate, most games should have none; a handful having one is normal, all of them having one is a sign you're manufacturing rather than reacting.

**Write results to:** `career/[year]/league_results/week_[NN].md` (create the file/folder if it doesn't exist yet this season). One entry per game. Regenerate `career/[year]/standings.md` from the receipts with `python scripts/render_standings.py YEAR` in the same commit; it applies the Document 2 §5.3 tiebreakers. The week file carries no standings table of its own: the standings as of any past week come from `render_standings.py YEAR --through-week N`.

**Persist league statistics too.** For every closed background game, preserve a compact_stats public receipt under career/[year]/stats/game_receipts/. It keeps every nonzero generated player/team statistic and every game-day active player, and omits background snap rows and zero-valued counters to keep weekly Git diffs bounded. Once the full weekly slate is closed, rebuild the season statbook with runtime/statbook.py / scripts/render_season_stats.py. The weekly highlights file remains concise; Jacksonville retains full play detail in its own receipt.

**Do not** write anything into the protagonist's own weekly turn file — that's assembled separately by whoever is running the interactive side of this project, which reads your results file as one of its own inputs.

---

## Task: "Expand the real-data library: [specific target, e.g., 'the 2014 NFL draft class' or '2014-2016 salary cap and CBA figures']."

**Model this on the existing library files** (`library/2013_league_calendar_and_financial_rules.md`, `library/2013_coaching_market_pre_hire.md`, `library/2013_draft_class.md`) — same structure, same sourcing discipline, same honesty about what couldn't be confirmed.

**Two-pass discipline, not one:**
1. **Research pass.** Find the facts, cite a specific real source (a named outlet and a URL where possible) for every claim.
2. **Verification pass — do this as a genuinely separate step, skeptical of your own first pass.** Re-search each claim from scratch rather than trusting your own citation. If a second source confirms it, mark it confirmed. If you find a discrepancy, correct it and say what changed and why. If you can't independently confirm something, mark it unverifiable/approximate rather than silently keeping the original number. This two-pass process is what caught real errors (a wrong hire date, a wrong draft slot, a cap-floor rule that didn't actually exist as first described) when this library was first built by hand — do not skip it.

**Draft-class-specific rule, if the target is a draft class:** pre-selection data only — measurables, testing, college production, pre-draft consensus rankings. Never record what happened to a player after he was drafted (stats, awards, bust/star framing). See `foundation/02_League_Era_and_Sourcebook.md` §12's historical-class-sourcing rule for why.

For historical draft work, preserve **information timing**, not just a final cutoff. Model 2013 on `library/2013_draft_information_gates.md`: declarations, combine invitations/results, pro days, medical/workout updates, and final boards become runtime-eligible only on their dated release/event. Eligibility/pool coverage belongs in a separate registry such as `library/2013_draft_pool_registry.md`; do not infer eligibility from who was eventually drafted or signed.

**Write results to:** a new file under `library/`, named on the same pattern as the existing three (`library/[year]_[topic].md`). Do not edit the existing 2013 files unless you are specifically correcting an error found in them.

---

## Task: "Run the [year] hiring search."

This is the bounded pre-hire phase that may run before full career initialization. It produces organization-side developments and records the user's own already-authorized career choices, but it never invents a choice for Alex Stone.

**Prerequisite.** `career/[year]/offseason/hiring_search_brief/` must contain the user's own instructions covering the teams to pursue, priority/order, material terms or non-negotiables, concessions, and walk-away conditions. If a material choice is not covered, stop at that branch and report what decision is needed.

**Read, in this order:**
1. `foundation/03_Head_Coach_Organization_and_Authority_Canon.md` §10.
2. `foundation/templates/hiring_search_output_template.md`.
3. `library/alex_stone_character_dossier_pre_hire.md`, using its factual record and §11 evidence boundaries only. It does not supply Stone's interview answers, motives, philosophy, or negotiating preferences.
4. `library/2013_coaching_market_pre_hire.md`.
5. Only after the criteria freeze described below is written, read `career/[year]/offseason/hiring_search_brief/`.

**Do not load `archive/2013_coaching_market_historical_comparator.md` while resolving this search.** It contains the real later outcomes and is retained only for paused audit or historical fact-checking.

**Criteria freeze before the brief.** Before opening the user's brief, write a `Criteria freeze` entry into `career/[year]/offseason/hiring_search.md` for every organization already established in Document 3's search scope. Use only the pre-hire market file. Record documented needs and constraints, identify any labeled inference, and leave unsupported private weighting unknown. This entry is the pre-hire equivalent of Document 1 §9.4's ex-ante record and must close before Stone's pitch or terms are evaluated.

**Procedure:**
1. Reduce the user's brief to concrete terms. Persuasiveness, length, confidence, and desired outcome are not resolution inputs.
2. Resolve organization-side actions from the frozen criteria: interest, interview requests, rejection, second-stage requests, negotiation positions, counters, deadlines, and offers.
3. Routine scheduling and administrative implementation may proceed without another user turn when directly authorized by the brief.
4. A consequential Alex Stone choice remains user-controlled unless the brief contains an explicit standing instruction that covers the exact branch. Examples that require user control unless expressly pre-authorized: agreeing to a materially new interview condition, changing a non-negotiable, making a new promise, accepting a counter outside the stated range, accepting an offer, declining an offer, or choosing between simultaneous offers.
5. A walk-away rule in the brief may be executed automatically only when the triggering condition is objectively satisfied as written.
6. An acceptance rule may be executed automatically only when the exact offered terms satisfy an explicit pre-written acceptance condition. "Team is my first choice" is not by itself authorization to accept any contract.
7. Never use the eventual real hire, later coordinator staff, later roster move, or later career outcome as an answer key.
8. If every team resolves without a hire, close the search as `NO HIRE`. If a user-authorized acceptance occurs, close it as `HIRED — INITIALIZATION BUILD REQUIRED`. Do not begin roster, staff, game, press-conference, or season play.

**Persistence and ex-ante discipline.** Write every criteria freeze, user instruction relied on, material organization-side development, unresolved user decision, offer, and final search status to `career/[year]/offseason/hiring_search.md`. During this pre-hire phase that file is the authorized decision record. Do not write simulated hiring events into Document 6 before career initialization.

**Do not** edit Document 3, Document 6, or the state files as part of this batch task. After the search concludes, the interactive initialization build reconciles the accepted outcome into Documents 2–6 before active career play.

---

## Task: "Build the initial roster and cap sheet for [Team]." (fires once a hire closes)

**Prerequisite.** `career/[year]/offseason/hiring_search.md` must show status `HIRED — INITIALIZATION BUILD REQUIRED` (or later), with the accepted team and contract terms already recorded. If no hire has closed, stop and report rather than guessing a team.

**Two-pass research discipline, same standard as the real-data library task.**
1. **Research pass.** The real team's actual roster as of the hire date — every player under contract, position, and real contract terms (length, bonus structure, real cap hit where sourceable) — the team's real 2013 salary-cap position, and its real coaching/front-office staff below the head-coach level. Cite a specific real source for every claim.
2. **Verification pass, genuinely separate and skeptical of the first.** Re-check every figure from scratch. This exact discipline caught real errors (a wrong hire date, a wrong draft slot, a cap-floor rule that didn't exist as first described) when the original 2013 library was built — do not skip it here either. Mark anything unconfirmable as approximate rather than presenting an estimate as fact.

**Write the sourced research to two separate files**, kept inside the career folder rather than `library/` so the owner doesn't have to search elsewhere for the team's own starting snapshot:
- `career/[year]/offseason/initial_roster.md` — the roster itself: every player under contract, position, jersey number if known, and real prior-season role/experience. No contract or cap figures here.
- `career/[year]/offseason/initial_cap_sheet.md` — the full financial breakdown: every player's contract terms (length, base salary by year, bonus/proration, real 2013 cap hit where sourceable), dead-money entries, total cap usage, and remaining cap space against the real 2013 cap number. Cite sources the same way the library files do, in both files.

**Then, and only for this task, populate `state/04_Roster_and_Staff_Register.md`** from that sourced research, following the register's own already-written field definitions and evidence rules exactly as they stand in that file. This task authorizes the initial baseline write. Later canon-changing tasks also authorize affected state writes under the atomic progression rule above; baseline-only research still must not advance the career. Copy load-bearing cap figures into Document 2 §11's real financial tables the same way the original 2013 library build did.

**Do not** invent a depth chart, a scheme fit, or any coach's evaluation of a player — this task supplies real, sourced facts (contract, position, real prior-season role/statistics) only. Stone's own evaluation of these players is a separate, later, interactive step, not something to pre-decide here.

**Do not** touch Document 3, Document 5, or Document 6 — reconciling the new roster baseline into the rest of the package is a separate step for whoever runs the interactive side of this project to close out.

---

## Task: "Run Jacksonville's staff-building phase."

**Prerequisite.** `career/[year]/offseason/hiring_search.md` must show `HIRED`, and `career/[year]/offseason/staff_building/staff_plan.md` must exist with the user's own candidate targets. If either is missing, stop and report rather than inventing candidates or a philosophy — staff-hiring priorities and the roster/team-building plan are the user's to set (Document 1 §3), not yours.

**Read, in this order:**
1. `career/[year]/offseason/staff_building/staff_plan.md` — Stone's actual candidate targets, in priority order, with each candidate's real contemporaneous availability window.
2. `career/[year]/offseason/the_prowl_program_identity.md` and `the_prowl_player_readiness_standard.md` — Stone's actual established coaching identity (Document 3 §2.1). This governs how he'd frame the job to a candidate and what he'd actually want from a hire; it is not a script to recite verbatim.
3. `career/[year]/offseason/roster_evaluation.md` and `career/[year]/offseason/free_agency/player_board.md` — Stone's own roster evaluation and free-agency priorities, which this task also brings to Caldwell for an initial alignment conversation (see below).
4. Document 3 §5 (Authority Map): row 2 gives Stone final hiring authority over his own staff; rows 3, 5, 6, and 7 keep acquisition, contract, cap, and roster-cut authority with Caldwell.

**Staff hiring — resolve genuine acceptance, not automatic yes.**
1. For each open position, contact candidates in the stated priority order. A candidate's real, dated availability window in `staff_plan.md` is a hard constraint: if the in-world date this task runs on is past when a candidate's window closed (he already accepted a real job elsewhere, per the real dates already recorded there), that candidate is gone — move to the next call. Do not extend a window past what's already documented.
2. Whether an available candidate actually accepts is a genuine, resolvable question — weigh the real fit (role, authority, scheme, staff-funding trade Stone is offering) the same way any other autonomous person in this project is evaluated, never simply defaulting to yes because he's Stone's first choice.
3. A rejection or a candidate taking another job first is a normal, expected outcome for some fraction of these calls — do not manufacture uniform success across every position.
4. Record every actual hire — name, role, effective date — in `staff_building/hires.md`. Record a real decline or lost-to-competition outcome there too, briefly, so the hiring history includes actual outcomes.

**GM alignment conversation — Caldwell reacts, he doesn't rubber-stamp.**
1. Present Stone's roster evaluation (`roster_evaluation.md`) and free-agency priorities (`free_agency/player_board.md`) to Caldwell as one consolidated conversation, per Document 3 §10.2's compressed-turn discipline.
2. Caldwell's reaction is resolved from his own retained authority and the club's actual situation (library/2013_coaching_market_pre_hire.md §3), not assumed to agree with Stone on every point. A genuine, football-grounded pushback (a release Caldwell wants to revisit, a free-agent price he thinks is too rich, a roster call he weighs differently) is a normal and expected outcome, not something to avoid.
3. Record this exchange as a dated, appended entry in `roster_evaluation.md` — do not silently rewrite Stone's own original evaluation to match Caldwell's response.

**Do not** resolve any actual free-agency signing or draft selection in this task — free agency does not open until March 12 and the draft runs April 25-27 (`library/2013_league_calendar_and_financial_rules.md`); this phase is staff hiring and initial GM alignment on the broader plan only, not executing it early.

**Do not** invent Stone's coaching philosophy or personal positions beyond what's already established in The Prowl documents, the interview positions, and the accepted contract — if a candidate conversation would require a stance nothing on record covers, stop and report what's missing rather than inventing it.

---

## Task: "Run the [year] offseason cycle." (free agency, draft, and trades — gated each year by the real calendar)

Gated on the real calendar, not just a brief. Do not attempt free agency before March 12 or the draft before April 25 for the 2013 cycle (`library/2013_league_calendar_and_financial_rules.md`; check the equivalent library file for other years). When that window is actually reached, this task resolves `career/[year]/offseason/free_agency/player_board.md`, `career/[year]/offseason/draft/player_draft_board.md`, and `career/[year]/trades/trade_targets.md` the same way the staff-building task above resolves staff hiring: real market pressure, genuine possible rejection or lost competition, Caldwell's retained authority over the actual signing/pick/trade decision, and a written result (never a locked-in outcome assumed from what actually happened in real history). If any of those three files doesn't exist yet for the year in question, stop and report rather than improvising the user's priorities.

## 2014 E1/E2 policy adoption

Stone approved the policy in `runtime/2014_engine_decisions.md`. Use sourced pre-divergence evidence and reliable dated branch observations, actual personnel, shared assignments and coaching tradeoffs; no Jacksonville bonus or talent inference from the equal-strength engine's 2013 records. Injured/unavailable players must leave automatically, with a real live pause for consequential Jacksonville replacements and legal backup passing. Kernel 2014.4 carries the Tier 1 fixes and the close_week pause wiring; the merged live runtime was verified September 30, 2026 and `runtime/season_readiness.json` accepts that kernel. No 2014 game is authorized while the season-rules, end-to-end season-closure, legal-roster or financial-control gates remain BLOCKED. Read the current readiness gates and `runtime/defect_register.md` before any 2014 game.

**Season routing:** use the requested NFL season for YEAR, including January/February postseason games. Weekly input, closure, box-score and league-award commands require `--season YEAR`; readiness defaults to `docs/repository_map.json` active_season and can be checked explicitly with `--season YEAR`. Current record ownership follows that map separately. The 2014 release requirements remain blocking even when legacy readiness flags are VERIFIED.
